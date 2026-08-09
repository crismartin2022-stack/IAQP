"""
IAQP · Cliente de billetera
═════════════════════════════════════════════════════════════════

IAQP no guarda saldos. El saldo vive en QuartzPlay y acá se le piden
débitos y créditos. Una sola fuente de verdad para la plata.

CUÁNDO SE COBRA
───────────────
Al apostar, no al resolver. Si se cobrara al final, un jugador podría
poner fichas que no puede pagar y retirarse antes del giro.

QUÉ PASA SI FALLA EL PAGO
─────────────────────────
La ronda NO se revierte. El resultado ya se sorteó, se cantó y quedó
auditado: deshacerlo sería peor que deberle plata a alguien. El
movimiento queda 'pendiente' en iaqp_movimientos y se reintenta. Por eso
la tabla tiene índice sobre los no confirmados: es una cola de trabajo.

IDEMPOTENCIA
────────────
Cada movimiento lleva una referencia derivada de la ronda y el jugador,
no un azar. Así el reintento genera exactamente la misma referencia y
QuartzPlay lo reconoce como repetido en vez de pagar dos veces.
"""

import os
import asyncio
import logging

import httpx

log = logging.getLogger("iaqp.billetera")

QP_URL = os.environ.get("QP_URL", "").rstrip("/")
QP_SERVICE_KEY = os.environ.get("IAQP_SERVICE_KEY", "")

TIEMPO_ESPERA = 8.0
REINTENTOS = 3


class ErrorBilletera(Exception):
    """Falló la comunicación o QuartzPlay rechazó el movimiento."""

    def __init__(self, mensaje, definitivo=False):
        super().__init__(mensaje)
        # 'definitivo' = no tiene sentido reintentar (saldo insuficiente,
        # jugador bloqueado). Los errores de red sí se reintentan.
        self.definitivo = definitivo


def ref_apuesta(ronda_id, jugador_id, indice):
    """Determinista: el mismo reintento produce la misma referencia."""
    return f"iaqp:apu:{ronda_id}:{jugador_id}:{indice}"


def ref_premio(ronda_id, jugador_id):
    return f"iaqp:pre:{ronda_id}:{jugador_id}"


def ref_devolucion(ronda_id, jugador_id):
    return f"iaqp:dev:{ronda_id}:{jugador_id}"


async def _llamar(camino: str, cuerpo: dict) -> dict:
    if not QP_URL or not QP_SERVICE_KEY:
        raise ErrorBilletera("Billetera sin configurar (QP_URL / IAQP_SERVICE_KEY)",
                             definitivo=True)

    ultimo = None
    for intento in range(REINTENTOS):
        try:
            async with httpx.AsyncClient(timeout=TIEMPO_ESPERA) as cli:
                r = await cli.post(
                    f"{QP_URL}{camino}",
                    json=cuerpo,
                    headers={"X-Service-Key": QP_SERVICE_KEY,
                             "Content-Type": "application/json"},
                )
            if r.status_code == 200:
                return r.json()

            # 4xx: el pedido está mal o no se puede cumplir. Reintentar
            # no lo va a arreglar y además ensucia los registros.
            if 400 <= r.status_code < 500:
                detalle = ""
                try:
                    detalle = r.json().get("detail", "")
                except Exception:
                    detalle = r.text[:120]
                raise ErrorBilletera(detalle or f"Rechazado ({r.status_code})",
                                     definitivo=True)

            ultimo = f"HTTP {r.status_code}"

        except ErrorBilletera:
            raise
        except Exception as e:
            ultimo = str(e)

        if intento < REINTENTOS - 1:
            await asyncio.sleep(0.4 * (2 ** intento))   # 0,4s · 0,8s

    raise ErrorBilletera(f"Billetera inalcanzable: {ultimo}")


async def saldo(jugador_id: str) -> int:
    """Saldo en centavos."""
    d = await _llamar("/api/wallet/saldo", {"jugador_id": str(jugador_id)})
    return int(d.get("saldo_centavos", 0))


async def cobrar(jugador_id: str, centavos: int, ref: str,
                 mesa_id: str = "", juego: str = "ruleta") -> int:
    """Cobra una apuesta. Devuelve el saldo posterior."""
    d = await _llamar("/api/wallet/debito", {
        "jugador_id": str(jugador_id), "monto_centavos": int(centavos),
        "ref": ref, "mesa_id": mesa_id, "juego": juego,
    })
    return int(d.get("saldo_centavos", 0))


async def pagar(jugador_id: str, centavos: int, ref: str,
                mesa_id: str = "", juego: str = "ruleta",
                devolucion: bool = False) -> int:
    """Paga un premio, o devuelve una ronda anulada."""
    d = await _llamar("/api/wallet/credito", {
        "jugador_id": str(jugador_id), "monto_centavos": int(centavos),
        "ref": ref, "mesa_id": mesa_id, "juego": juego,
        "devolucion": devolucion,
    })
    return int(d.get("saldo_centavos", 0))


async def pagar_con_registro(conn, ronda_id, jugador_id, centavos,
                             mesa_id="", devolucion=False):
    """
    Paga y deja rastro en iaqp_movimientos pase lo que pase. Si falla,
    el movimiento queda pendiente para que lo levante el reintentador.
    """
    ref = (ref_devolucion(ronda_id, jugador_id) if devolucion
           else ref_premio(ronda_id, jugador_id))
    tipo = "devolucion" if devolucion else "premio"

    await conn.execute("""
        INSERT INTO iaqp_movimientos
            (jugador_id, ronda_id, tipo, monto, ref_externa, estado, creado_en)
        VALUES ($1,$2,$3,$4,$5,'pendiente',NOW())
        ON CONFLICT (ref_externa) DO NOTHING
    """, str(jugador_id), ronda_id, tipo, int(centavos), ref)

    try:
        await pagar(jugador_id, centavos, ref, mesa_id, devolucion=devolucion)
        await conn.execute("""
            UPDATE iaqp_movimientos SET estado='confirmado', confirmado_en=NOW()
            WHERE ref_externa=$1
        """, ref)
        return True
    except ErrorBilletera as e:
        await conn.execute("""
            UPDATE iaqp_movimientos SET estado='fallido', error=$2
            WHERE ref_externa=$1
        """, ref, str(e)[:300])
        log.error(f"[BILLETERA] no se pudo pagar {ref}: {e}")
        return False


async def reintentar_pendientes(conn, limite=50):
    """
    Levanta los pagos que quedaron colgados. Se corre cada tanto.
    Como las referencias son deterministas, reintentar es seguro: si el
    pago sí había entrado, QuartzPlay responde 'repetido' y no duplica.
    """
    filas = await conn.fetch("""
        SELECT id, jugador_id, ronda_id, tipo, monto, ref_externa
        FROM iaqp_movimientos
        WHERE estado <> 'confirmado'
        ORDER BY creado_en
        LIMIT $1
    """, limite)

    recuperados = 0
    for f in filas:
        try:
            await pagar(f["jugador_id"], f["monto"], f["ref_externa"],
                        devolucion=(f["tipo"] == "devolucion"))
            await conn.execute("""
                UPDATE iaqp_movimientos SET estado='confirmado',
                       confirmado_en=NOW(), error=NULL WHERE id=$1
            """, f["id"])
            recuperados += 1
        except ErrorBilletera as e:
            if e.definitivo:
                await conn.execute("""
                    UPDATE iaqp_movimientos SET estado='trabado', error=$2
                    WHERE id=$1
                """, f["id"], str(e)[:300])
                log.error(f"[BILLETERA] trabado {f['ref_externa']}: {e}")

    if recuperados:
        log.info(f"[BILLETERA] recuperados {recuperados} pagos pendientes")
    return recuperados
