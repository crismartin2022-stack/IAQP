"""
IAQP · Ruleta europea
═════════════════════════════════════════════════════════════════

Un solo cero: 37 casilleros (0 a 36). El retorno teórico al jugador es
36/37 = 97,297 %, y sale de las reglas, no de ningún ajuste.

Este módulo es a propósito PURO: sin base de datos, sin red, sin reloj.
Entra una apuesta y una semilla, sale un resultado. Así el laboratorio
lo puede correr millones de veces aislado, que es justo lo que hace
para certificar.
"""

from . import rng


# ── Disposición de la rueda ───────────────────────────────────
# Orden físico real de una rueda europea (single zero). Importa para la
# animación y para las apuestas por vecinos.
RUEDA = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8,
         23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12,
         35, 3, 26]

ROJOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
NEGROS = set(range(1, 37)) - ROJOS


def color(n: int) -> str:
    if n == 0:
        return "verde"
    return "rojo" if n in ROJOS else "negro"


# ── Tabla de pagos ────────────────────────────────────────────
# El pago es "a 1": pleno paga 35 a 1, o sea devuelve 36 veces la apuesta
# contando la ficha original. De ahí sale el 36/37.
PAGOS = {
    "pleno":       35,   # un número
    "caballo":     17,   # dos números contiguos
    "transversal": 11,   # una fila de tres
    "cuadro":       8,   # cuatro en cuadrado
    "linea":        5,   # dos filas, seis números
    "columna":      2,
    "docena":       2,
    "rojo":         1, "negro": 1,
    "par":          1, "impar": 1,
    "falta":        1,   # 1 a 18
    "pasa":         1,   # 19 a 36
}


def _cubre(tipo: str, valor, n: int) -> bool:
    """¿La apuesta cubre el número que salió?"""
    if tipo == "pleno":
        return n == int(valor)
    if tipo in ("caballo", "transversal", "cuadro", "linea"):
        return n in {int(x) for x in valor}
    if n == 0:
        return False              # el cero se lleva todas las sencillas
    if tipo == "rojo":
        return n in ROJOS
    if tipo == "negro":
        return n in NEGROS
    if tipo == "par":
        return n % 2 == 0
    if tipo == "impar":
        return n % 2 == 1
    if tipo == "falta":
        return 1 <= n <= 18
    if tipo == "pasa":
        return 19 <= n <= 36
    if tipo == "columna":
        return n % 3 == (int(valor) % 3) and int(valor) in (1, 2, 3) \
            if int(valor) != 3 else n % 3 == 0
    if tipo == "docena":
        d = int(valor)
        return (d - 1) * 12 + 1 <= n <= d * 12
    return False


# ── Validación de apuestas ────────────────────────────────────

def validar(apuesta: dict) -> tuple:
    """(ok, motivo). Se corre antes de aceptar la ficha."""
    tipo = apuesta.get("tipo")
    if tipo not in PAGOS:
        return False, f"Tipo de apuesta desconocido: {tipo}"

    monto = apuesta.get("monto", 0)
    if not isinstance(monto, int) or monto <= 0:
        return False, "El monto tiene que ser un entero positivo"

    valor = apuesta.get("valor")
    if tipo == "pleno":
        if not isinstance(valor, int) or not 0 <= valor <= 36:
            return False, "El pleno va de 0 a 36"
    elif tipo in ("caballo", "transversal", "cuadro", "linea"):
        largo = {"caballo": 2, "transversal": 3, "cuadro": 4, "linea": 6}[tipo]
        if not isinstance(valor, (list, tuple)) or len(valor) != largo:
            return False, f"{tipo} necesita {largo} números"
        if len({int(x) for x in valor}) != largo:
            return False, f"{tipo} tiene números repetidos"
        if any(not 0 <= int(x) <= 36 for x in valor):
            return False, "Hay números fuera de la rueda"
    elif tipo in ("columna", "docena"):
        if valor not in (1, 2, 3):
            return False, f"{tipo} va de 1 a 3"

    return True, ""


# ── Resolución ────────────────────────────────────────────────

def girar(semilla_servidor: str, semilla_cliente: str, nonce: int) -> int:
    """El número que sale. Único punto donde interviene el azar."""
    return rng.entero(semilla_servidor, semilla_cliente, nonce, 37)


def resolver(apuestas: list, numero: int) -> dict:
    """
    Liquida la mesa contra el número que salió.

    'devuelto' incluye la ficha original de las apuestas ganadoras:
    un pleno de 100 que gana devuelve 3.600 (35 de premio + la ficha).
    """
    detalle = []
    apostado = 0
    devuelto = 0

    for ap in apuestas:
        tipo = ap["tipo"]
        monto = int(ap["monto"])
        apostado += monto
        gana = _cubre(tipo, ap.get("valor"), numero)
        pago = monto * (PAGOS[tipo] + 1) if gana else 0
        devuelto += pago
        detalle.append({
            "tipo": tipo, "valor": ap.get("valor"), "monto": monto,
            "gana": gana, "devuelto": pago,
        })

    return {
        "numero": numero,
        "color": color(numero),
        "apostado": apostado,
        "devuelto": devuelto,
        "resultado_jugador": devuelto - apostado,
        "detalle": detalle,
    }


def ronda_completa(semilla_servidor: str, semilla_cliente: str, nonce: int,
                   apuestas: list) -> dict:
    """Gira y liquida, dejando el rastro que necesita la auditoría."""
    for ap in apuestas:
        ok, motivo = validar(ap)
        if not ok:
            raise ValueError(motivo)

    numero = girar(semilla_servidor, semilla_cliente, nonce)
    salida = resolver(apuestas, numero)
    salida["auditoria"] = {
        "hash_semilla_servidor": rng.compromiso(semilla_servidor),
        "semilla_cliente": semilla_cliente,
        "nonce": nonce,
        "juego": "ruleta_europea",
        "version_reglas": 1,
    }
    return salida


def rtp_teorico() -> float:
    """36/37. Es el mismo para toda apuesta simple de esta ruleta."""
    return 36 / 37
