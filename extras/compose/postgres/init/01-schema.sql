-- Schema für das Pokémon-Beispiel (Generation 5, Einall/Unova, Pokédex-Nr. 494-649)
--   pokemon         Haupttabelle
--   pokemon_detail  1:1 zu pokemon (UNIQUE auf dem Fremdschlüssel)
--   attacke         1:N zu pokemon (ein Pokémon hat mehrere Attacken)
-- Wird vom Postgres-Image beim ersten Start (leeres Datenvolume) automatisch ausgeführt.

CREATE SCHEMA IF NOT EXISTS pokemon;
SET search_path TO pokemon;
ALTER ROLE CURRENT_USER SET search_path = 'pokemon';   -- gilt für künftige Verbindungen

CREATE TABLE pokemon (
    id          INTEGER PRIMARY KEY,                -- Pokédex-Nummer, bewusst keine IDENTITY
    name        TEXT NOT NULL UNIQUE,
    typ1        TEXT NOT NULL,
    typ2        TEXT,
    groesse_m   NUMERIC(4, 1) NOT NULL CHECK (groesse_m > 0),
    gewicht_kg  NUMERIC(5, 1) NOT NULL CHECK (gewicht_kg > 0),
    legendaer   BOOLEAN NOT NULL DEFAULT FALSE,
    version     INTEGER NOT NULL DEFAULT 0,         -- für optimistische Synchronisation (If-Match/ETag)
    erzeugt     TIMESTAMP NOT NULL DEFAULT now(),
    aktualisiert TIMESTAMP NOT NULL DEFAULT now()
);

-- 1:1: pro Pokémon höchstens eine Detail-Zeile
CREATE TABLE pokemon_detail (
    id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pokemon_id       INTEGER NOT NULL UNIQUE REFERENCES pokemon (id) ON DELETE CASCADE,
    fangrate         INTEGER NOT NULL CHECK (fangrate BETWEEN 1 AND 255),
    basis_erfahrung  INTEGER NOT NULL CHECK (basis_erfahrung > 0)
);

-- 1:N: mehrere Attacken pro Pokémon
CREATE TABLE attacke (
    id           INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pokemon_id   INTEGER NOT NULL REFERENCES pokemon (id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    typ          TEXT NOT NULL,
    staerke      INTEGER CHECK (staerke > 0),       -- NULL bei Statusattacken
    genauigkeit  INTEGER CHECK (genauigkeit BETWEEN 1 AND 100)
);
CREATE INDEX attacke_pokemon_id_idx ON attacke (pokemon_id);
