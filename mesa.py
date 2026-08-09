"""
IAQP · Mesa: ciclo de vida de la ronda
═════════════════════════════════════════════════════════════════

Estados y la única transición válida entre ellos:

    ABIERTA ──────► CERRADA ──────► RESUELTA
     acepta          no acepta       número
     apuestas        más apuestas    cantado y
                     (se gira)       liquidado

    ABIERTA ──────► ANULADA
     (caída, fallo de billetera: se devuelve todo)

POR QUÉ IMPORTA EL ORDEN
────────────────────────
El giro ocurre DESPUÉS de cerrar. Mientras la mesa está abierta el
resultado no existe en ningún lado, ni siquiera calculado y guardado
para después. Eso es lo que impide que alguien mire el número y decida
si acepta o rechaza una apuesta de último segundo.

ROTACIÓN DE SEMILLAS
────────────────────
Una semilla de servidor cubre muchas rondas; el nonce las separa. La
semilla se revela cuando se rota, no antes: revelarla mientras sigue
en uso permitiría calcular los resultados que faltan.

Al rotar se publica el hash de la nueva ANTES de usarla, así nunca hay
un momento en que la casa conozca un resultado futuro que el jugador no
pueda verificar después.
"""

from datetime import datetime, timezone, timedelta
import rng


ABIERTA = "abierta"
CERRADA = "cerrada"
RESUELTA = "resuelta"
ANULADA = "anulada"


class ErrorMesa(Exception):
    """Se intentó algo que el estado actual no permite."""


class Sesion:
    """
    Una semilla de servidor y su vida útil. Cuando se rota, la vieja se
    revela y todas sus rondas quedan verificables para siempre.
    """

    def __init__(self, rondas_max=1000):
        self.semilla = rng.nueva_semilla_servidor()
        self.hash_publicado = rng.compromiso(self.semilla)
        self.nonce = 0
        self.rondas_max = rondas_max
        self.revelada = False
        self.abierta_en = datetime.now(timezone.utc)

    def siguiente_nonce(self):
        if self.revelada:
            raise ErrorMesa("La semilla ya se reveló: no se puede seguir usando")
        if self.nonce >= self.rondas_max:
            raise ErrorMesa("La sesión agotó sus rondas: hay que rotar")
        self.nonce += 1
        return self.nonce

    def hay_que_rotar(self):
        return self.nonce >= self.rondas_max

    def revelar(self):
        """Se llama al rotar. A partir de acá la semilla es pública."""
        self.revelada = True
        return {
            "semilla": self.semilla,
            "hash_publicado": self.hash_publicado,
            "rondas": self.nonce,
            "verifica": rng.verificar_compromiso(self.semilla, self.hash_publicado),
        }


class Ronda:
    """
    Una tirada. Guarda todo lo necesario para reconstruirla: qué se
    apostó, con qué semillas, en qué momento y qué salió.
    """

    def __init__(self, mesa_id, sesion: Sesion, segundos_apuestas=20):
        self.mesa_id = mesa_id
        self.sesion = sesion
        self.nonce = sesion.siguiente_nonce()
        self.hash_semilla = sesion.hash_publicado
        self.estado = ABIERTA
        self.apuestas = []          # [{jugador, tipo, valor, monto, ref}]
        self.numero = None
        self.liquidacion = None
        self.abierta_en = datetime.now(timezone.utc)
        self.cierra_en = self.abierta_en + timedelta(seconds=segundos_apuestas)
        self.cerrada_en = None
        self.resuelta_en = None

    # ── Apuestas ──────────────────────────────────────────────

    def segundos_restantes(self):
        if self.estado != ABIERTA:
            return 0
        falta = (self.cierra_en - datetime.now(timezone.utc)).total_seconds()
        return max(0, round(falta, 1))

    def apostar(self, jugador, apuesta, validador, ref=None):
        """
        'validador' es la función validar() del juego. La mesa no conoce
        las reglas de ningún juego: se las pide al módulo correspondiente.
        'ref' es el identificador que manda el cliente para que un
        reintento por red no cobre dos veces.
        """
        if self.estado != ABIERTA:
            raise ErrorMesa("La ronda ya no acepta apuestas")
        if self.segundos_restantes() <= 0:
            raise ErrorMesa("Se acabó el tiempo de apuestas")

        ok, motivo = validador(apuesta)
        if not ok:
            raise ErrorMesa(motivo)

        if ref and any(a.get("ref") == ref for a in self.apuestas):
            # Reintento del mismo pedido: se ignora en silencio, no se
            # cobra de nuevo. Devolver el estado actual es lo correcto.
            return False

        self.apuestas.append({
            "jugador": jugador,
            "tipo": apuesta["tipo"],
            "valor": apuesta.get("valor"),
            "monto": int(apuesta["monto"]),
            "ref": ref,
            "en": datetime.now(timezone.utc).isoformat(),
        })
        return True

    def apostado_por(self, jugador):
        return sum(a["monto"] for a in self.apuestas if a["jugador"] == jugador)

    # ── Transiciones ──────────────────────────────────────────

    def cerrar(self):
        if self.estado != ABIERTA:
            raise ErrorMesa(f"No se puede cerrar una ronda {self.estado}")
        self.estado = CERRADA
        self.cerrada_en = datetime.now(timezone.utc)

    def resolver(self, motor):
        """
        'motor' es el módulo del juego (ruleta, blackjack…). Recién acá
        se consulta el azar: antes de este punto el resultado no existe.
        """
        if self.estado != CERRADA:
            raise ErrorMesa("Hay que cerrar la ronda antes de girar")

        self.numero = motor.girar(self.sesion.semilla,
                                  self._semilla_cliente(), self.nonce)
        self.liquidacion = motor.resolver(self.apuestas, self.numero)
        self.estado = RESUELTA
        self.resuelta_en = datetime.now(timezone.utc)
        return self.liquidacion

    def anular(self, motivo):
        """Devuelve todo. Se usa si falla la billetera o se cae la mesa."""
        if self.estado == RESUELTA:
            raise ErrorMesa("Una ronda resuelta no se anula: se corrige aparte")
        self.estado = ANULADA
        self.motivo_anulacion = motivo
        return [{"jugador": a["jugador"], "devolver": a["monto"]}
                for a in self.apuestas]

    # ── Auditoría ─────────────────────────────────────────────

    def _semilla_cliente(self):
        """
        En mesa compartida la semilla del cliente no puede ser de un solo
        jugador: se arma con datos públicos de la ronda, para que ninguno
        pueda influir en el resultado de los demás.
        """
        return f"{self.mesa_id}:{self.abierta_en.isoformat()}"

    def acta(self):
        """El registro que se guarda y que permite reconstruir la ronda."""
        return {
            "mesa_id": self.mesa_id,
            "nonce": self.nonce,
            "hash_semilla_servidor": self.hash_semilla,
            "semilla_cliente": self._semilla_cliente(),
            "estado": self.estado,
            "numero": self.numero,
            "apuestas": self.apuestas,
            "liquidacion": self.liquidacion,
            "abierta_en": self.abierta_en.isoformat(),
            "cerrada_en": self.cerrada_en.isoformat() if self.cerrada_en else None,
            "resuelta_en": self.resuelta_en.isoformat() if self.resuelta_en else None,
        }


class Mesa:
    """Una mesa que encadena rondas con la misma sesión de semilla."""

    def __init__(self, mesa_id, motor, segundos_apuestas=20, rondas_por_semilla=1000):
        self.mesa_id = mesa_id
        self.motor = motor
        self.segundos_apuestas = segundos_apuestas
        self.sesion = Sesion(rondas_por_semilla)
        self.ronda = None
        self.historial = []
        self.semillas_reveladas = []

    def nueva_ronda(self):
        if self.ronda and self.ronda.estado in (ABIERTA, CERRADA):
            raise ErrorMesa("La ronda anterior sigue en juego")

        if self.sesion.hay_que_rotar():
            self.rotar_semilla()

        self.ronda = Ronda(self.mesa_id, self.sesion, self.segundos_apuestas)
        return self.ronda

    def rotar_semilla(self):
        """Revela la vieja y publica el hash de la nueva."""
        if self.sesion.nonce > 0:
            self.semillas_reveladas.append(self.sesion.revelar())
        self.sesion = Sesion(self.sesion.rondas_max)
        return self.sesion.hash_publicado

    def cerrar_y_resolver(self):
        self.ronda.cerrar()
        liq = self.ronda.resolver(self.motor)
        self.historial.append(self.ronda.acta())
        return liq

    def estado_publico(self):
        """Lo que ve el jugador. Nunca incluye la semilla en uso."""
        return {
            "mesa_id": self.mesa_id,
            "hash_semilla_servidor": self.sesion.hash_publicado,
            "ronda_nonce": self.ronda.nonce if self.ronda else None,
            "estado": self.ronda.estado if self.ronda else None,
            "segundos_restantes": self.ronda.segundos_restantes() if self.ronda else 0,
            "apuestas_en_mesa": len(self.ronda.apuestas) if self.ronda else 0,
            "ultimos_numeros": [h["numero"] for h in self.historial[-12:]],
        }
