"""
IAQP · Pruebas del núcleo de juego
Reproduce, en chico, lo que revisa un laboratorio de certificación.
"""
import sys, time, hashlib
from collections import Counter
sys.path.insert(0, "/home/claude")
from iaqp import rng, ruleta

print("═" * 62)
print("1 · PROVABLY FAIR: el compromiso no se puede falsear")
print("═" * 62)
s = rng.nueva_semilla_servidor()
h = rng.compromiso(s)
print(f"  semilla (se revela al final): {s[:24]}…")
print(f"  hash publicado antes:         {h[:24]}…")
print(f"  verifica con la semilla real: {rng.verificar_compromiso(s, h)}")
falsa = rng.nueva_semilla_servidor()
print(f"  verifica con otra semilla:    {rng.verificar_compromiso(falsa, h)}")

print()
print("═" * 62)
print("2 · DETERMINISMO: la misma entrada da siempre lo mismo")
print("═" * 62)
a = ruleta.girar(s, "jugador123", 42)
b = ruleta.girar(s, "jugador123", 42)
c = ruleta.girar(s, "jugador123", 43)
print(f"  nonce 42 dos veces: {a} y {b}  -> iguales: {a == b}")
print(f"  nonce 43:           {c}  -> distinto del 42: {c != a}")

print()
print("═" * 62)
print("3 · UNIFORMIDAD: chi-cuadrado sobre 370.000 giros")
print("═" * 62)
N = 370_000
t0 = time.time()
cuenta = Counter(ruleta.girar(s, "test", i) for i in range(N))
seg = time.time() - t0
esperado = N / 37
chi2 = sum((cuenta[k] - esperado) ** 2 / esperado for k in range(37))
print(f"  giros: {N:,} en {seg:.1f}s ({N/seg:,.0f}/s)")
print(f"  esperado por casillero: {esperado:,.0f}")
print(f"  mínimo observado:       {min(cuenta.values()):,}")
print(f"  máximo observado:       {max(cuenta.values()):,}")
print(f"  chi-cuadrado: {chi2:.2f}   (36 grados de libertad)")
print(f"  umbral al 95%: 50.998  ->  {'PASA' if chi2 < 50.998 else 'REVISAR'}")
print(f"  todos los casilleros salieron: {len(cuenta) == 37}")

print()
print("═" * 62)
print("4 · SESGO DE MÓDULO: comparación contra el método ingenuo")
print("═" * 62)
import hmac
def ingenuo(seed, cliente, nonce):
    d = hmac.new(seed.encode(), f"{cliente}:{nonce}".encode(), hashlib.sha256).digest()
    return int.from_bytes(d[:4], "big") % 37     # <- así NO
M = 370_000
ing = Counter(ingenuo(s, "test", i) for i in range(M))
esp = M / 37
chi_ing = sum((ing[k] - esp) ** 2 / esp for k in range(37))
print(f"  chi-cuadrado del método ingenuo: {chi_ing:.2f}")
print(f"  chi-cuadrado del nuestro:        {chi2:.2f}")
print("  (con 2^32 el sesgo es chico, pero el rechazo lo elimina del todo)")

print()
print("═" * 62)
print("5 · RTP: convergencia con apuestas mezcladas")
print("═" * 62)
print(f"  RTP teórico: {ruleta.rtp_teorico()*100:.3f} %")
casos = [
    ("pleno al 17",      [{"tipo": "pleno", "valor": 17, "monto": 100}]),
    ("rojo",             [{"tipo": "rojo", "monto": 100}]),
    ("docena 2",         [{"tipo": "docena", "valor": 2, "monto": 100}]),
    ("cuadro 1-2-4-5",   [{"tipo": "cuadro", "valor": [1,2,4,5], "monto": 100}]),
    ("mezcla",           [{"tipo": "pleno", "valor": 7, "monto": 50},
                          {"tipo": "negro", "monto": 100},
                          {"tipo": "linea", "valor": [1,2,3,4,5,6], "monto": 50}]),
]
V = 300_000
for nombre, aps in casos:
    apostado = devuelto = 0
    for i in range(V):
        n = ruleta.girar(s, f"rtp-{nombre}", i)
        r = ruleta.resolver(aps, n)
        apostado += r["apostado"]; devuelto += r["devuelto"]
    rtp = devuelto / apostado * 100
    dif = rtp - ruleta.rtp_teorico() * 100
    print(f"  {nombre:18} RTP {rtp:6.3f} %   desvío {dif:+.3f}")

print()
print("═" * 62)
print("6 · REGLAS: el cero, los pagos y la validación")
print("═" * 62)
r0 = ruleta.resolver([{"tipo":"rojo","monto":100},
                      {"tipo":"par","monto":100},
                      {"tipo":"falta","monto":100}], 0)
print(f"  sale 0 con rojo+par+falta: devuelve {r0['devuelto']} (debe ser 0)")
rp = ruleta.resolver([{"tipo":"pleno","valor":17,"monto":100}], 17)
print(f"  pleno acertado de 100: devuelve {rp['devuelto']} (debe ser 3600)")
print(f"  color del 17: {ruleta.color(17)}   del 32: {ruleta.color(32)}   del 0: {ruleta.color(0)}")
print(f"  casilleros en la rueda: {len(ruleta.RUEDA)}  sin repetidos: {len(set(ruleta.RUEDA))==37}")
print(f"  rojos {len(ruleta.ROJOS)} / negros {len(ruleta.NEGROS)}")
for mala, desc in [
    ({"tipo":"pleno","valor":37,"monto":100}, "pleno al 37"),
    ({"tipo":"pleno","valor":5,"monto":-50},  "monto negativo"),
    ({"tipo":"caballo","valor":[1,1],"monto":100}, "caballo repetido"),
    ({"tipo":"inventado","monto":100},        "tipo inexistente"),
]:
    ok, motivo = ruleta.validar(mala)
    print(f"  rechaza {desc:20} -> {not ok}  ({motivo})")

print()
print("═" * 62)
print("7 · REPRODUCCIÓN PARA AUDITORÍA")
print("═" * 62)
rep = rng.reproducir(s, "cliente-abc", 999, 37)
for k, v in rep.items():
    print(f"  {k}: {str(v)[:60]}")
