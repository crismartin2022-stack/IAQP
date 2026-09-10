-- Synthetic IAQP-only fixture. Every statement is safe to rerun.
INSERT INTO public.iaqp_semillas
    (mesa_id, hash_publicado, semilla, rondas, abierta_en, revelada_en)
VALUES
    ('synthetic-ruleta-01',
     '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
     'synthetic-server-seed-not-for-production', 1, NOW(), NOW())
ON CONFLICT (hash_publicado) DO NOTHING;

INSERT INTO public.iaqp_rondas
    (mesa_id, juego, semilla_id, nonce, semilla_cliente, estado, resultado,
     apostado, devuelto, abierta_en, cerrada_en, resuelta_en)
SELECT
    'synthetic-ruleta-01', 'ruleta_europea', id, 1, 'synthetic-client-seed',
    'resuelta', '{"numero":17}'::jsonb, 100, 200, NOW(), NOW(), NOW()
FROM public.iaqp_semillas
WHERE hash_publicado = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
ON CONFLICT (semilla_id, nonce) DO NOTHING;

INSERT INTO public.iaqp_apuestas
    (ronda_id, jugador_id, tipo, valor, monto, ref, gana, devuelto)
SELECT
    r.id, 'synthetic-player', 'pleno', '17'::jsonb, 100,
    'synthetic:bet:ruleta-01:1', TRUE, 200
FROM public.iaqp_rondas r
JOIN public.iaqp_semillas s ON s.id = r.semilla_id
WHERE s.hash_publicado = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
  AND r.nonce = 1
ON CONFLICT (ronda_id, ref) DO NOTHING;

INSERT INTO public.iaqp_movimientos
    (jugador_id, ronda_id, tipo, monto, ref_externa, estado, creado_en, confirmado_en)
SELECT
    'synthetic-player', r.id, 'premio', 200,
    'synthetic:payout:ruleta-01:1', 'confirmado', NOW(), NOW()
FROM public.iaqp_rondas r
JOIN public.iaqp_semillas s ON s.id = r.semilla_id
WHERE s.hash_publicado = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
  AND r.nonce = 1
ON CONFLICT (ref_externa) DO NOTHING;
