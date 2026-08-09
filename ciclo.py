"""
IAQP · Reloj de la mesa
═════════════════════════════════════════════════════════════════

El bucle que hace girar una mesa sin parar:

    abrir ──► esperar apuestas ──► avisar últimos segundos ──►
    cerrar ──► girar ──► liquidar ──► pagar ──► pausa ──► abrir…

ORDEN QUE NO SE ALTERA
──────────────────────
El giro va después del cierre. La locución va después del giro. El
pago va después de la liquidación. Cada paso solo puede ocurrir cuando
el anterior terminó, y el estado de la ronda lo hace cumplir: si algo
intenta saltarse el orden, mesa.py lanza ErrorMesa.

QUÉ PASA SI ALGO FALLA
──────────────────────
  Falla el cobro de una apuesta  → esa apuesta no entra. La ronda sigue.
  Falla el pago de un premio     → la ronda NO se revierte. El resultado
                                   ya se cantó y está auditado. El pago
                                   queda pendiente y se reintenta.
  Falla el guardado de la ronda  → se registra y se sigue. Perder el
                                   registro es grave, así que se alerta.
"""

import asyncio
import json
import logging

from . import mesa as M
from . import crupier as C
from . import billetera as B

log = logging.getLogger("iaqp.ciclo")


class MesaEnVivo:
    """Una mesa girando, con su estado en memoria y su registro en base."""

    def __init__(self, mesa_id, motor, pool, juego="ruleta_europea",
                 crupier="valentina", segundos_apuestas=20,
                 segundos_pausa=8):
        self.mesa = M.Mesa(mesa_id, motor, segundos_apuestas)
        self.motor = motor
        self.pool = pool
        self.juego = juego
        self.crupier = crupier
        self.segundos_pausa = segundos_pausa
        self.corriendo = False
        self.semilla_id = None
        self.ronda_id = None
        self.guion = []          # clips que el frente debe reproducir
        self.chat = []           # últimos mensajes de la mesa

    # ── Persistencia ──────────────────────────────────────────

    async def _guardar_semilla(self, conn):
        self.semilla_id = await conn.fetchval("""
            INSERT INTO iaqp_semillas (mesa_id, hash_publicado, abierta_en)
            VALUES ($1,$2,NOW())
            ON CONFLICT (hash_publicado) DO UPDATE SET mesa_id=EXCLUDED.mesa_id
            RETURNING id
        """, self.mesa.mesa_id, self.mesa.sesion.hash_publicado)

    async def _revelar_semilla(self, conn, revelada):
        await conn.execute("""
            UPDATE iaqp_semillas SET semilla=$2, rondas=$3, revelada_en=NOW()
            WHERE hash_publicado=$1
        """, revelada["hash_publicado"], revelada["semilla"],
             revelada["rondas"])

    async def _abrir_ronda_en_base(self, conn, ronda):
        self.ronda_id = await conn.fetchval("""
            INSERT INTO iaqp_rondas
                (mesa_id, juego, semilla_id, nonce, semilla_cliente,
                 estado, abierta_en)
            VALUES ($1,$2,$3,$4,$5,'abierta',NOW())
            RETURNING id
        """, self.mesa.mesa_id, self.juego, self.semilla_id, ronda.nonce,
             ronda._semilla_cliente())

    async def _cerrar_ronda_en_base(self, conn, ronda, liq):
        await conn.execute("""
            UPDATE iaqp_rondas
            SET estado='resuelta', resultado=$2, apostado=$3, devuelto=$4,
                cerrada_en=$5, resuelta_en=NOW()
            WHERE id=$1
        """, self.ronda_id, json.dumps(liq), liq["apostado"], liq["devuelto"],
             ronda.cerrada_en)

        for d in liq["detalle"]:
            await conn.execute("""
                UPDATE iaqp_apuestas SET gana=$2, devuelto=$3
                WHERE ronda_id=$1 AND tipo=$4 AND monto=$5 AND gana IS NULL
            """, self.ronda_id, d["gana"], d["devuelto"], d["tipo"], d["monto"])

    # ── Apuestas ──────────────────────────────────────────────

    async def apostar(self, jugador_id, apuesta, ref=None):
        """
        Cobra primero, anota después. Si el cobro falla, la ficha no
        entra a la mesa: nunca queda una apuesta sin respaldo de plata.
        """
        ronda = self.mesa.ronda
        if not ronda or ronda.estado != M.ABIERTA:
            raise M.ErrorMesa("La mesa no está tomando apuestas")

        ok, motivo = self.motor.validar(apuesta)
        if not ok:
            raise M.ErrorMesa(motivo)

        indice = len(ronda.apuestas)
        referencia = ref or B.ref_apuesta(self.ronda_id, jugador_id, indice)
        centavos = int(apuesta["monto"])

        # PRIMERO se descarta el reintento, DESPUÉS se cobra.
        # Al revés se cobraba de nuevo y recién ahí se descubría que la
        # ficha ya estaba puesta: la plata salía dos veces. QuartzPlay
        # igual lo frena por idempotencia, pero no hay que depender de
        # que el otro lado nos salve.
        if any(a.get("ref") == referencia for a in ronda.apuestas):
            return {"ok": True, "repetido": True,
                    "apuestas_en_mesa": len(ronda.apuestas)}

        saldo_post = await B.cobrar(jugador_id, centavos, referencia,
                                    self.mesa.mesa_id, self.juego)

        entro = ronda.apostar(jugador_id, apuesta, self.motor.validar,
                              ref=referencia)
        if entro:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO iaqp_apuestas
                        (ronda_id, jugador_id, tipo, valor, monto, ref)
                    VALUES ($1,$2,$3,$4,$5,$6)
                    ON CONFLICT DO NOTHING
                """, self.ronda_id, str(jugador_id), apuesta["tipo"],
                     json.dumps(apuesta.get("valor")), centavos, referencia)

        return {"ok": True, "saldo_centavos": saldo_post,
                "apuestas_en_mesa": len(ronda.apuestas)}

    # ── Pagos ─────────────────────────────────────────────────

    async def _pagar_ronda(self, conn, liq):
        """Agrupa por jugador: un solo movimiento por persona, no por ficha."""
        por_jugador = {}
        for ap, det in zip(self.mesa.ronda.apuestas, liq["detalle"]):
            if det["devuelto"] > 0:
                j = ap["jugador"]
                por_jugador[j] = por_jugador.get(j, 0) + det["devuelto"]

        fallos = 0
        for jugador, monto in por_jugador.items():
            ok = await B.pagar_con_registro(conn, self.ronda_id, jugador,
                                            monto, self.mesa.mesa_id)
            if not ok:
                fallos += 1
        return len(por_jugador), fallos

    # ── Bucle ─────────────────────────────────────────────────

    async def girar_una_ronda(self):
        async with self.pool.acquire() as conn:
            if self.semilla_id is None:
                await self._guardar_semilla(conn)

            hash_previo = self.mesa.sesion.hash_publicado
            ronda = self.mesa.nueva_ronda()

            # Si rotó la semilla, se revela la vieja y se registra la nueva
            if self.mesa.sesion.hash_publicado != hash_previo:
                if self.mesa.semillas_reveladas:
                    await self._revelar_semilla(
                        conn, self.mesa.semillas_reveladas[-1])
                await self._guardar_semilla(conn)

            await self._abrir_ronda_en_base(conn, ronda)

        self.guion = C.locutar("apuestas_abiertas", self.crupier, ronda.nonce)

        # Ventana de apuestas
        espera = self.mesa.segundos_apuestas
        if espera > 5:
            await asyncio.sleep(espera - 5)
            self.guion = C.locutar("ultimos_segundos", self.crupier, ronda.nonce)
            await asyncio.sleep(5)
        else:
            await asyncio.sleep(espera)

        # Cierre y giro, en ese orden y no en otro
        ronda.cerrar()
        self.guion = C.locutar("no_va_mas", self.crupier, ronda.nonce)

        liq = ronda.resolver(self.motor)
        self.mesa.historial.append(ronda.acta())

        # Recién ahora habla el crupier: narra lo que ya pasó
        self.guion = C.guion_de_ronda(liq, self.crupier, ronda.nonce)

        async with self.pool.acquire() as conn:
            try:
                await self._cerrar_ronda_en_base(conn, ronda, liq)
            except Exception as e:
                log.error(f"[CICLO] no se pudo guardar la ronda "
                          f"{self.ronda_id}: {e}")
            pagados, fallos = await self._pagar_ronda(conn, liq)

        if fallos:
            log.error(f"[CICLO] {fallos} de {pagados} pagos quedaron pendientes "
                      f"en la ronda {self.ronda_id}")

        return liq

    async def correr(self):
        self.corriendo = True
        log.info(f"[CICLO] arranca {self.mesa.mesa_id}")
        while self.corriendo:
            try:
                await self.girar_una_ronda()
                await asyncio.sleep(self.segundos_pausa)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.exception(f"[CICLO] error en {self.mesa.mesa_id}: {e}")
                await asyncio.sleep(5)   # no arder en un bucle de fallos

    def detener(self):
        self.corriendo = False
        self.guion = C.locutar("mesa_cierra", self.crupier, 0)

    # ── Vista pública ─────────────────────────────────────────

    def estado(self):
        e = self.mesa.estado_publico()
        e["juego"] = self.juego
        e["crupier"] = C.CRUPIERES[self.crupier]["nombre"]
        e["guion"] = self.guion
        e["chat"] = self.chat[-25:]
        return e
