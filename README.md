# IAQP

Casino con crupieres de IA. Servicio separado de QuartzPlay.

## Estructura

    iaqp/rng.py       Núcleo de aleatoriedad. Provably fair. ← lo certifica el laboratorio
    iaqp/ruleta.py    Reglas y pagos. Funciones puras, sin base ni red.
    iaqp/mesa.py      Ciclo de la ronda y rotación de semillas.
    iaqp/crupier.py   Locuciones pregrabadas y chat.
    iaqp/billetera.py Cliente contra la billetera de QuartzPlay.
    iaqp/ciclo.py     Reloj de la mesa.
    main.py           API HTTP.
    pruebas/          Evidencia estadística para la certificación.

## Variables de entorno

    DATABASE_URL       Postgres propio de IAQP (NO el de QuartzPlay)
    QP_URL             URL de la API de QuartzPlay
    IAQP_SERVICE_KEY   Clave compartida con QuartzPlay
    ANTHROPIC_API_KEY  Solo para el chat del crupier (opcional)
    ALLOWED_ORIGINS    Dominios del frontend, separados por coma

## Principios que no se tocan

1. IAQP no guarda saldos. El saldo vive en QuartzPlay.
2. El resultado se sortea después de cerrar las apuestas. Nunca antes.
3. El crupier con IA narra; no decide. Nunca recibe la semilla.
4. No existe ningún parámetro que ajuste cuánto gana la casa.

## Pruebas

    python -m pruebas.pruebas
