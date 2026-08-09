"""
IAQP · Núcleo de aleatoriedad
═════════════════════════════════════════════════════════════════

Este módulo es el corazón certificable del casino. Todo lo que decida
un resultado de juego pasa por acá y por ningún otro lado.

REGLAS QUE NO SE NEGOCIAN
─────────────────────────
1. El resultado se determina ANTES de cualquier presentación. El
   crupier con IA narra lo que ya ocurrió; no participa en decidirlo.
2. No hay parámetro que ajuste cuánto gana la casa. La ventaja sale
   de las reglas del juego y de las tablas de pago, que son públicas.
   Cualquier perilla de "porcentaje de premio" es fraude y además
   invalida la certificación.
3. Toda ronda es reproducible: con (semilla_servidor, semilla_cliente,
   nonce) cualquiera recalcula el resultado y verifica que coincide.

ESQUEMA PROVABLY FAIR
─────────────────────
  Antes de aceptar apuestas, se publica  hash = SHA256(semilla_servidor).
  El jugador aporta su semilla_cliente (o se usa una por defecto).
  Cada ronda usa un nonce que se incrementa.

    flujo = HMAC-SHA256(semilla_servidor, "semilla_cliente:nonce")

  Al cerrar la ronda se revela la semilla_servidor. El jugador comprueba
  que su SHA256 da el hash publicado antes de apostar: prueba de que la
  casa no eligió el resultado después de ver las apuestas.

SESGO DE MÓDULO
───────────────
  Convertir bytes a un rango con  %  reparte mal cuando el rango no es
  potencia de dos: los primeros valores salen un poco más seguido. En
  una ruleta de 37 casilleros eso es exactamente lo que un laboratorio
  detecta y rechaza. Por eso acá se usa muestreo por rechazo, que
  reparte parejo aunque consuma algún byte de más.
"""

import hashlib
import hmac
import secrets


# ── Semillas ──────────────────────────────────────────────────

def nueva_semilla_servidor() -> str:
    """32 bytes de entropía del sistema operativo, en hexadecimal."""
    return secrets.token_hex(32)


def compromiso(semilla_servidor: str) -> str:
    """El hash que se publica ANTES de aceptar apuestas."""
    return hashlib.sha256(semilla_servidor.encode()).hexdigest()


def verificar_compromiso(semilla_servidor: str, hash_publicado: str) -> bool:
    """Lo corre el jugador (o el auditor) al revelarse la semilla."""
    return hmac.compare_digest(compromiso(semilla_servidor), hash_publicado)


# ── Flujo de bytes determinista ───────────────────────────────

def _flujo(semilla_servidor: str, semilla_cliente: str, nonce: int,
           ronda: int = 0) -> bytes:
    """
    32 bytes deterministas. 'ronda' permite estirar el flujo cuando una
    tirada necesita más bytes de los que entran en un bloque: mezclar
    barajas, repartir cartas, etc.
    """
    mensaje = f"{semilla_cliente}:{nonce}:{ronda}".encode()
    return hmac.new(semilla_servidor.encode(), mensaje,
                    hashlib.sha256).digest()


def entero(semilla_servidor: str, semilla_cliente: str, nonce: int,
           tope: int) -> int:
    """
    Entero uniforme en [0, tope). Muestreo por rechazo: se descarta el
    tramo final de cada bloque de 4 bytes que no entra en un múltiplo
    exacto de 'tope', para que ningún valor tenga ventaja.
    """
    if tope < 1:
        raise ValueError("El tope tiene que ser al menos 1")
    if tope == 1:
        return 0

    limite = (2 ** 32 // tope) * tope   # mayor múltiplo de tope que entra
    ronda = 0
    while True:
        bloque = _flujo(semilla_servidor, semilla_cliente, nonce, ronda)
        for i in range(0, 32, 4):
            valor = int.from_bytes(bloque[i:i + 4], "big")
            if valor < limite:          # dentro del tramo parejo
                return valor % tope
        ronda += 1                      # bloque agotado, se estira
        if ronda > 1000:                # no puede pasar; red de seguridad
            raise RuntimeError("RNG sin converger")


def enteros(semilla_servidor: str, semilla_cliente: str, nonce: int,
            tope: int, cantidad: int) -> list:
    """Varios enteros independientes de la misma ronda (cartas, dados)."""
    return [entero(semilla_servidor, f"{semilla_cliente}#{k}", nonce, tope)
            for k in range(cantidad)]


def mezclar(semilla_servidor: str, semilla_cliente: str, nonce: int,
            mazo: list) -> list:
    """
    Fisher-Yates con la aleatoriedad del módulo. Es la mezcla que un
    laboratorio espera ver: cada permutación con la misma probabilidad.
    """
    cartas = list(mazo)
    for i in range(len(cartas) - 1, 0, -1):
        j = entero(semilla_servidor, f"{semilla_cliente}~{i}", nonce, i + 1)
        cartas[i], cartas[j] = cartas[j], cartas[i]
    return cartas


# ── Reproducción para auditoría ───────────────────────────────

def reproducir(semilla_servidor: str, semilla_cliente: str, nonce: int,
               tope: int) -> dict:
    """
    Devuelve el resultado y el rastro de cómo se llegó a él. Es lo que
    se le muestra a un jugador que reclama, y al auditor.
    """
    return {
        "semilla_servidor": semilla_servidor,
        "hash_semilla_servidor": compromiso(semilla_servidor),
        "semilla_cliente": semilla_cliente,
        "nonce": nonce,
        "tope": tope,
        "resultado": entero(semilla_servidor, semilla_cliente, nonce, tope),
        "algoritmo": "HMAC-SHA256 + muestreo por rechazo",
    }
