-- Schéma minimal reconstruit à partir des requêtes du workflow et de Grafana.
-- Ce fichier n'est pas un dump de la base d'origine.
CREATE TABLE IF NOT EXISTS public.incidents (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_ip TEXT NOT NULL,
    attack_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    action_taken TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS incidents_event_time_idx ON public.incidents (event_time);
