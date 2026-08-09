"""
IAQP · API
═════════════════════════════════════════════════════════════════

Punto de entrada del servicio. Levanta las mesas, las hace girar y
expone lo que consume el frontend.

Arranque:
    uvicorn main:app --host 0.0.0.0 --port $PORT
"""

import os
import json
import logging
import asyncio
from contextlib import asynccontextmanager

import asyncpg
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import ruleta
import mesa as M
import crupier as C
import billetera as B
import ciclo

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("iaqp")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
ORIGENES = [o.strip() for o in
            os.environ.get("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

_pool = None
MESAS = {}


async def get_pool():
    global _pool
    if _pool is None:
        if not DATABASE_URL:
            raise RuntimeError("Falta DATABASE_URL")
        _pool = await asyncpg.create_pool(
            DATABASE_URL, min_size=2, max_size=20,
            timeout=10, command_timeout=15,
            max_inactive_connection_lifetime=300)
    return _pool


# ── Configuración de mesas ────────────────────────────────────
# Por ahora fija. Cuando haya panel, sale de la base.
MESAS_CONFIG = [
    {"id": "ruleta-01", "juego": "ruleta_europea", "motor": ruleta,
     "crupier": "valentina", "apuestas": 25, "pausa": 8},
    {"id": "ruleta-02", "juego": "ruleta_europea", "motor": ruleta,
     "crupier": "matias", "apuestas": 40, "pausa": 10},
]


async def _reintentador():
    """Levanta cada minuto los pagos que quedaron colgados."""
    while True:
        try:
            await asyncio.sleep(60)
            pool = await get_pool()
            async with pool.acquire() as conn:
                await B.reintentar_pendientes(conn)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.error(f"[REINTENTOS] {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await get_pool()
    tareas = []
    for cfg in MESAS_CONFIG:
        mv = ciclo.MesaEnVivo(cfg["id"], cfg["motor"], pool,
                              juego=cfg["juego"], crupier=cfg["crupier"],
                              segundos_apuestas=cfg["apuestas"],
                              segundos_pausa=cfg["pausa"])
        MESAS[cfg["id"]] = mv
        tareas.append(asyncio.create_task(mv.correr()))
    tareas.append(asyncio.create_task(_reintentador()))
    log.info(f"[IAQP] {len(MESAS)} mesas girando")

    yield

    for mv in MESAS.values():
        mv.detener()
    for t in tareas:
        t.cancel()
    if _pool:
        await _pool.close()


app = FastAPI(title="IAQP", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=ORIGENES,
                   allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type"], allow_credentials=False)


# ── Estado ────────────────────────────────────────────────────

@app.get("/salud")
async def salud():
    return {"ok": True, "mesas": list(MESAS.keys())}


@app.get("/api/mesas")
async def listar_mesas():
    return {"mesas": [m.estado() for m in MESAS.values()]}


@app.get("/api/mesa/{mesa_id}/estado")
async def estado_mesa(mesa_id: str):
    mv = MESAS.get(mesa_id)
    if not mv:
        raise HTTPException(404, "Mesa inexistente")
    return mv.estado()


# ── Juego ─────────────────────────────────────────────────────

@app.post("/api/mesa/{mesa_id}/apostar")
async def apostar(mesa_id: str, request: Request):
    mv = MESAS.get(mesa_id)
    if not mv:
        raise HTTPException(404, "Mesa inexistente")

    body = await request.json()
    jugador = str(body.get("jugador_id") or "")
    if not jugador:
        raise HTTPException(400, "Falta el jugador")

    apuesta = {
        "tipo": body.get("tipo"),
        "valor": body.get("valor"),
        "monto": body.get("monto_centavos"),
    }
    try:
        return await mv.apostar(jugador, apuesta, ref=body.get("ref"))
    except M.ErrorMesa as e:
        raise HTTPException(400, str(e))
    except B.ErrorBilletera as e:
        raise HTTPException(400 if e.definitivo else 503, str(e))


@app.get("/api/mesa/{mesa_id}/mis-apuestas")
async def mis_apuestas(mesa_id: str, jugador_id: str):
    mv = MESAS.get(mesa_id)
    if not mv or not mv.mesa.ronda:
        raise HTTPException(404, "Mesa inexistente")
    fichas = [a for a in mv.mesa.ronda.apuestas if a["jugador"] == jugador_id]
    return {"apuestas": fichas,
            "total_centavos": sum(a["monto"] for a in fichas)}


# ── Chat ──────────────────────────────────────────────────────

@app.post("/api/mesa/{mesa_id}/chat")
async def chat(mesa_id: str, request: Request):
    mv = MESAS.get(mesa_id)
    if not mv:
        raise HTTPException(404, "Mesa inexistente")

    body = await request.json()
    texto = str(body.get("texto") or "")[:400].strip()
    quien = str(body.get("nombre") or "Jugador")[:24]
    if not texto:
        raise HTTPException(400, "Mensaje vacío")

    mv.chat.append({"rol": "user", "nombre": quien, "texto": texto})

    pedido = C.armar_pedido(texto, mv.estado(), mv.crupier,
                            historial=mv.chat[-8:])

    # Señales de juego problemático: responde el sistema, no el modelo
    if "responder_sin_modelo" in pedido:
        r = pedido["responder_sin_modelo"]
        mv.chat.append({"rol": "assistant", "nombre": "Crupier", "texto": r})
        return {"respuesta": r, "asistencia": True}

    if not ANTHROPIC_KEY:
        return {"respuesta": None, "sin_configurar": True}

    try:
        async with httpx.AsyncClient(timeout=20) as cli:
            r = await cli.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC_KEY,
                         "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": "claude-sonnet-4-6",
                      "max_tokens": pedido["max_tokens"],
                      "system": pedido["system"],
                      "messages": pedido["messages"]})
        if r.status_code != 200:
            log.warning(f"[CHAT] modelo respondió {r.status_code}")
            raise HTTPException(503, "El crupier no puede responder ahora")
        datos = r.json()
        salida = "".join(b.get("text", "") for b in datos.get("content", [])
                         if b.get("type") == "text").strip()
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"[CHAT] {e}")
        raise HTTPException(503, "El crupier no puede responder ahora")

    mv.chat.append({"rol": "assistant", "nombre": "Crupier", "texto": salida})
    return {"respuesta": salida}


# ── Verificación pública ──────────────────────────────────────

@app.get("/api/verificar/{ronda_id}")
async def verificar(ronda_id: int):
    """
    Lo que le mostramos a un jugador que quiere comprobar una ronda.
    La semilla solo aparece si ya se reveló: mientras esté en uso,
    revelarla permitiría calcular las rondas que faltan.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        f = await conn.fetchrow("""
            SELECT r.id, r.mesa_id, r.juego, r.nonce, r.semilla_cliente,
                   r.resultado, r.abierta_en, r.resuelta_en,
                   s.hash_publicado, s.semilla, s.revelada_en
            FROM iaqp_rondas r
            JOIN iaqp_semillas s ON s.id = r.semilla_id
            WHERE r.id = $1
        """, ronda_id)
    if not f:
        raise HTTPException(404, "Ronda inexistente")

    res = f["resultado"]
    if isinstance(res, str):
        res = json.loads(res)

    salida = {
        "ronda_id": f["id"], "mesa": f["mesa_id"], "juego": f["juego"],
        "nonce": f["nonce"], "semilla_cliente": f["semilla_cliente"],
        "hash_semilla_servidor": f["hash_publicado"],
        "numero": (res or {}).get("numero"),
        "resuelta_en": f["resuelta_en"].isoformat() if f["resuelta_en"] else None,
        "algoritmo": "HMAC-SHA256 + muestreo por rechazo",
    }

    if f["semilla"]:
        salida["semilla_servidor"] = f["semilla"]
        salida["revelada_en"] = f["revelada_en"].isoformat()
        salida["como_verificar"] = (
            "1) SHA256 de la semilla del servidor tiene que dar el hash "
            "publicado. 2) HMAC-SHA256 con esa semilla sobre "
            "'semilla_cliente:nonce:0', tomando bloques de 4 bytes y "
            "descartando los que caen fuera del múltiplo de 37, da el número."
        )
    else:
        salida["semilla_servidor"] = None
        salida["nota"] = ("La semilla sigue en uso. Se revela al rotarla, "
                          "y ahí esta ronda queda verificable para siempre.")
    return salida
