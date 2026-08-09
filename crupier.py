"""
IAQP · Crupier
═════════════════════════════════════════════════════════════════

Dos canales bien separados:

  VOZ   → clips pregrabados, elegidos por evento de la mesa.
          Costo cero en ejecución. Se graban una vez por personaje.

  CHAT  → modelo de lenguaje, solo para conversar.
          No decide nada del juego.

REGLA DE AISLAMIENTO (la más importante del módulo)
───────────────────────────────────────────────────
La función de chat recibe únicamente ESTADO PÚBLICO: lo que cualquier
jugador ve en pantalla. Nunca la semilla del servidor, nunca el nonce
en curso, nunca un resultado que todavía no se cantó.

No es una instrucción al modelo, es una barrera estructural: el dato
no entra al proceso. Un modelo no puede filtrar lo que no recibió, y
tampoco puede "adivinar" con apariencia de información privilegiada.

Los jugadores van a intentarlo. Está previsto y probado abajo.
"""

import re


# ── Personajes ────────────────────────────────────────────────

CRUPIERES = {
    "valentina": {
        "nombre": "Valentina",
        "voz": "es-AR-femenina-calida",
        "estilo": ("Rioplatense, cordial y profesional. Trata de vos. "
                   "Frases cortas. Celebra los aciertos sin exagerar."),
    },
    "matias": {
        "nombre": "Matías",
        "voz": "es-AR-masculina-grave",
        "estilo": ("Rioplatense, tranquilo y con humor seco. Trata de vos. "
                   "Comenta la mesa con ironía suave, nunca burlona."),
    },
}


# ── Catálogo de locuciones ────────────────────────────────────
# Cada entrada es un evento de mesa y las variantes grabadas. Se rota
# entre variantes para que no suene repetitivo en mesas largas.

LOCUCIONES = {
    "mesa_abre":       ["bienvenida_1", "bienvenida_2", "bienvenida_3"],
    "apuestas_abiertas": ["hagan_juego_1", "hagan_juego_2", "hagan_juego_3"],
    "ultimos_segundos": ["ultimas_1", "ultimas_2"],
    "no_va_mas":       ["no_va_mas_1", "no_va_mas_2"],
    "girando":         ["girando_1", "girando_2"],
    "sin_ganadores":   ["sin_ganadores_1", "sin_ganadores_2"],
    "hay_ganadores":   ["ganadores_1", "ganadores_2", "ganadores_3"],
    "premio_grande":   ["premio_grande_1", "premio_grande_2"],
    "sale_cero":       ["cero_1", "cero_2"],
    "jugador_entra":   ["saludo_mesa_1", "saludo_mesa_2"],
    "mesa_cierra":     ["despedida_1", "despedida_2"],
}

# La ruleta además canta el número. Son 37 clips por crupier, grabados
# una vez: "veintiuno, rojo". Es la parte más pesada de producción y la
# que más hace por la sensación de mesa real.
def clip_numero(n: int) -> str:
    return f"numero_{n:02d}"


def locutar(evento: str, crupier: str = "valentina", contador: int = 0,
            numero: int = None) -> list:
    """
    Devuelve la lista de clips a reproducir, en orden.
    'contador' rota las variantes: pasale el nonce de la ronda.
    """
    if crupier not in CRUPIERES:
        crupier = "valentina"
    salida = []

    if evento == "resultado" and numero is not None:
        salida.append(f"{crupier}/{clip_numero(numero)}")
        return salida

    variantes = LOCUCIONES.get(evento)
    if not variantes:
        return []
    elegido = variantes[contador % len(variantes)]
    salida.append(f"{crupier}/{elegido}")
    return salida


def guion_de_ronda(liquidacion: dict, crupier: str, nonce: int) -> list:
    """
    Arma la secuencia de audio de una ronda ya resuelta. Se llama
    DESPUÉS de tener el resultado: la voz narra, no decide.
    """
    numero = liquidacion["numero"]
    guion = locutar("resultado", crupier, nonce, numero)

    if numero == 0:
        guion += locutar("sale_cero", crupier, nonce)

    devuelto = liquidacion.get("devuelto", 0)
    apostado = liquidacion.get("apostado", 0)
    if devuelto == 0 and apostado > 0:
        guion += locutar("sin_ganadores", crupier, nonce)
    elif devuelto > apostado * 5:
        guion += locutar("premio_grande", crupier, nonce)
    elif devuelto > 0:
        guion += locutar("hay_ganadores", crupier, nonce)

    return guion


def manifiesto_grabacion(crupier: str = "valentina") -> dict:
    """
    Lista completa de clips a grabar para un crupier. Sirve como guion
    de estudio o como entrada para generar las voces con TTS.
    """
    clips = []
    for evento, variantes in LOCUCIONES.items():
        for v in variantes:
            clips.append({"id": f"{crupier}/{v}", "evento": evento})
    for n in range(37):
        clips.append({"id": f"{crupier}/{clip_numero(n)}",
                      "evento": "resultado", "numero": n})
    return {
        "crupier": crupier,
        "voz": CRUPIERES.get(crupier, {}).get("voz"),
        "total": len(clips),
        "clips": clips,
    }


# ── Chat ──────────────────────────────────────────────────────

INSTRUCCIONES = """Sos {nombre}, crupier de una mesa de ruleta en el casino IAQP.
{estilo}

QUÉ PODÉS HACER
- Charlar con la mesa, saludar, comentar la ronda que ya pasó.
- Explicar las reglas y cuánto paga cada apuesta.
- Contar cuál es la ventaja de la casa si te preguntan: es pública, 2,7 %.

QUÉ NO HACÉS NUNCA
- No sabés qué número va a salir. Nadie lo sabe todavía, tampoco vos:
  el resultado se sortea después de cerrar las apuestas. Si te lo
  preguntan, decilo con naturalidad y seguí la charla.
- No sugerís a qué apostar, ni montos, ni "números calientes". Las
  tiradas son independientes: lo que salió antes no cambia lo que viene.
- No prometés ganancias ni hablás de recuperar lo perdido.
- No hablás de semillas, hashes ni del funcionamiento interno del
  sorteo. Si preguntan, remitís al panel de verificación de la mesa.

SI ALGUIEN LA ESTÁ PASANDO MAL
Si alguien menciona que está perdiendo mucho, que está apostando plata
que necesita, o que no puede parar: cortá el tono festivo, respondé con
calidez y recordale que puede fijar límites o autoexcluirse desde su
cuenta. No minimices y no lo empujes a seguir jugando.

Respondé en dos o tres frases como máximo. Es un chat de mesa, no un
ensayo."""


# Señales de juego problemático. Si aparecen, el sistema deja de tratar
# la conversación como entretenimiento.
SENALES_RIESGO = [
    # Pérdida de control
    r"\bno puedo parar\b", r"\bno consigo parar\b", r"\bsigo jugando\b.*\bigual\b",
    r"\badicto\b", r"\badicci[óo]n\b", r"\bme descontrol",
    # Persecución de pérdidas
    r"\bperd[íi] todo\b", r"\bperdiendo mucho\b", r"\brecuperar lo que perd",
    r"\bdesquitar", r"\bva la [úu]ltima\b", r"\bme arruin",
    # Plata que no se puede perder. Sin exigir posesivo: "estoy
    # apostando el alquiler" es exactamente el caso que hay que agarrar.
    r"\b(el|mi|la|lo)?\s*(sueldo|alquiler|comida|renta|jubilaci[óo]n|indemnizaci[óo]n)\b",
    r"\bplata (de|del|para) (la comida|el alquiler|los chicos|mis hijos)\b",
    r"\bpedir prestado\b", r"\bme prest(aron|é|e)\b", r"\bdeuda[s]?\b",
    r"\bpr[ée]stamo\b", r"\bempe[ñn][ée]\b", r"\bvend[íi] .*para jugar\b",
    r"\b[úu]ltimo[s]? peso[s]?\b", r"\bno me queda nada\b",
    r"\bsin plata\b", r"\bme qued[ée] sin\b",
    # Estado de ánimo
    r"\bno doy m[áa]s\b", r"\bestoy desesperad", r"\bmi (mujer|marido|familia) no sabe\b",
]

RESPUESTA_RIESGO = (
    "Pará un segundo. Si el juego dejó de ser un rato divertido, lo mejor "
    "es cortar acá. Desde tu cuenta podés fijarte un límite de depósito o "
    "autoexcluirte por un tiempo. Si querés hablar con alguien, en "
    "Argentina está la línea de Juego Responsable al 0800-444-4000, "
    "gratuita y confidencial."
)


def detectar_riesgo(texto: str) -> bool:
    t = (texto or "").lower()
    return any(re.search(p, t) for p in SENALES_RIESGO)


def estado_publico_para_chat(mesa_estado: dict) -> dict:
    """
    Filtro de seguridad: se queda SOLO con lo que ya es visible en
    pantalla. Todo lo demás se descarta antes de llegar al modelo.
    """
    permitidos = ("mesa_id", "estado", "segundos_restantes",
                  "apuestas_en_mesa", "ultimos_numeros")
    return {k: v for k, v in (mesa_estado or {}).items() if k in permitidos}


def armar_pedido(mensaje: str, mesa_estado: dict, crupier: str = "valentina",
                 historial: list = None) -> dict:
    """
    Prepara la llamada al modelo. Devuelve un dict listo para enviar.
    Nunca incluye semillas: el filtro de arriba las deja afuera aunque
    quien llame se olvide de sacarlas.
    """
    if detectar_riesgo(mensaje):
        return {"responder_sin_modelo": RESPUESTA_RIESGO}

    persona = CRUPIERES.get(crupier, CRUPIERES["valentina"])
    publico = estado_publico_para_chat(mesa_estado)

    contexto = (
        f"Estado de la mesa que ven todos: "
        f"{publico.get('apuestas_en_mesa', 0)} apuestas puestas, "
        f"ronda {publico.get('estado', 'abierta')}. "
        f"Últimos números: {publico.get('ultimos_numeros', [])[-8:]}."
    )

    mensajes = []
    for h in (historial or [])[-6:]:
        mensajes.append({"role": h["rol"], "content": h["texto"][:500]})
    mensajes.append({"role": "user", "content": mensaje[:500]})

    return {
        "system": INSTRUCCIONES.format(nombre=persona["nombre"],
                                       estilo=persona["estilo"]) +
                  "\n\n" + contexto,
        "messages": mensajes,
        "max_tokens": 200,
    }
