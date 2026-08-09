"""
Genera el guion de grabación de los crupieres de IAQP.
Salida: un CSV listo para llevar a estudio o a un TTS.
"""
import csv, sys

ROJOS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

UNIDADES = ["cero","uno","dos","tres","cuatro","cinco","seis","siete","ocho",
            "nueve","diez","once","doce","trece","catorce","quince","dieciséis",
            "diecisiete","dieciocho","diecinueve","veinte","veintiuno",
            "veintidós","veintitrés","veinticuatro","veinticinco","veintiséis",
            "veintisiete","veintiocho","veintinueve","treinta","treinta y uno",
            "treinta y dos","treinta y tres","treinta y cuatro",
            "treinta y cinco","treinta y seis"]

def texto_numero(n):
    if n == 0:
        return "Cero."
    color = "rojo" if n in ROJOS else "negro"
    return f"{UNIDADES[n].capitalize()}, {color}."

FRASES = {
 "valentina": {
  "bienvenida_1": "Bienvenidos a la mesa. Soy Valentina, los acompaño esta noche.",
  "bienvenida_2": "Buenas, llegaron justo. Arrancamos.",
  "bienvenida_3": "Bienvenidos. Acomódense que ya empezamos.",
  "hagan_juego_1": "Hagan juego, señores.",
  "hagan_juego_2": "Mesa abierta. Pongan sus fichas.",
  "hagan_juego_3": "Adelante, la mesa está abierta.",
  "ultimas_1": "Últimas apuestas.",
  "ultimas_2": "Van cerrando, por favor.",
  "no_va_mas_1": "No va más.",
  "no_va_mas_2": "No va más, señores.",
  "girando_1": "Allá va.",
  "girando_2": "Gira la bola.",
  "sin_ganadores_1": "Esta vez no hubo suerte. Vamos con la próxima.",
  "sin_ganadores_2": "La casa se lleva esta. Sigue la mesa.",
  "ganadores_1": "¡Tenemos ganadores! Felicitaciones.",
  "ganadores_2": "Muy bien, ahí hay premio.",
  "ganadores_3": "Buena esa. Pagamos.",
  "premio_grande_1": "¡Qué manera de acertar! Tremendo premio.",
  "premio_grande_2": "¡Eso es un golazo! Felicitaciones.",
  "cero_1": "Cero. La casa saluda.",
  "cero_2": "Salió el cero, señores.",
  "saludo_mesa_1": "Bienvenido a la mesa.",
  "saludo_mesa_2": "Sumate, hay lugar.",
  "despedida_1": "Cerramos por hoy. Gracias por acompañarnos.",
  "despedida_2": "Hasta la próxima, que anden bien.",
 },
 "matias": {
  "bienvenida_1": "Buenas. Matías por acá, vamos a jugar un rato.",
  "bienvenida_2": "Bienvenidos. Siéntense que esto arranca.",
  "bienvenida_3": "Acá estamos. Mesa lista.",
  "hagan_juego_1": "Hagan juego.",
  "hagan_juego_2": "Mesa abierta, adelante.",
  "hagan_juego_3": "A poner fichas, señores.",
  "ultimas_1": "Últimas, que cierro.",
  "ultimas_2": "Van cerrando.",
  "no_va_mas_1": "No va más.",
  "no_va_mas_2": "Listo, no va más.",
  "girando_1": "Ahí va.",
  "girando_2": "Rueda la bola.",
  "sin_ganadores_1": "Nada esta vez. Seguimos.",
  "sin_ganadores_2": "Se la llevó la casa. Otra vuelta.",
  "ganadores_1": "Ahí hay ganadores.",
  "ganadores_2": "Bien ahí. Pagamos.",
  "ganadores_3": "Esa salió redonda. Felicitaciones.",
  "premio_grande_1": "Uh, tremendo premio. Bien jugado.",
  "premio_grande_2": "Eso sí que estuvo bueno. Felicitaciones.",
  "cero_1": "Cero. Casa.",
  "cero_2": "Y salió el cero.",
  "saludo_mesa_1": "Bienvenido, hay lugar.",
  "saludo_mesa_2": "Sumate tranquilo.",
  "despedida_1": "Cerramos acá. Gracias por venir.",
  "despedida_2": "Nos vemos la próxima.",
 },
}

# Notas de interpretación: importan más que el texto para que no suene a robot
TONO = {
 "bienvenida": "Cálido, sin apuro. Es lo primero que escucha el jugador.",
 "hagan_juego": "Neutro, profesional. Se repite mucho: que no canse.",
 "ultimas": "Un punto más de urgencia, sin apurar.",
 "no_va_mas": "Firme y corto. Es una orden, no una sugerencia.",
 "girando": "Baja el volumen, expectativa.",
 "sin_ganadores": "Neutro, nunca burlón. El jugador acaba de perder.",
 "ganadores": "Alegre y genuino, sin gritar.",
 "premio_grande": "Sorpresa auténtica. Es el momento del video que comparten.",
 "cero": "Neutro. El cero fastidia: no festejarlo.",
 "saludo_mesa": "Breve y amable.",
 "despedida": "Cálido, cierra la sesión.",
 "numero": "Claro y parejo. Se van a escuchar miles de veces: sin adornos.",
}

def familia(clip_id):
    base = clip_id.rsplit("_", 1)[0]
    return "numero" if clip_id.startswith("numero") else base

filas = []
for crupier, frases in FRASES.items():
    for cid, texto in frases.items():
        filas.append({
            "archivo": f"audio/{crupier}/{cid}.mp3",
            "crupier": crupier,
            "clip": cid,
            "texto": texto,
            "tono": TONO.get(familia(cid), ""),
        })
    for n in range(37):
        cid = f"numero_{n:02d}"
        filas.append({
            "archivo": f"audio/{crupier}/{cid}.mp3",
            "crupier": crupier,
            "clip": cid,
            "texto": texto_numero(n),
            "tono": TONO["numero"],
        })

salida = sys.argv[1] if len(sys.argv) > 1 else "guion_grabacion.csv"
with open(salida, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["archivo","crupier","clip","texto","tono"])
    w.writeheader()
    w.writerows(filas)

print(f"{len(filas)} clips · {len(FRASES)} crupieres")
for c in FRASES:
    print(f"  {c}: {len(FRASES[c])} frases + 37 números = {len(FRASES[c])+37}")
print(f"\nGuardado en {salida}")
