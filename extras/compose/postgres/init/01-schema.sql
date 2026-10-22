-- Schema for the Pokémon example (Generation 5, Unova, Pokédex no. 494-649)
--   pokemon         main table
--   pokemon_detail  1:1 with pokemon (UNIQUE on the foreign key)
--   move            1:N with pokemon (a Pokémon has several moves)
-- Automatically executed by the Postgres image on first start (empty data volume).

CREATE SCHEMA IF NOT EXISTS pokemon;
SET search_path TO pokemon;
ALTER ROLE CURRENT_USER SET search_path = 'pokemon';   -- applies to future connections

CREATE TABLE pokemon (
    id           INTEGER PRIMARY KEY,                -- Pokédex number, deliberately not an IDENTITY
    name         TEXT NOT NULL UNIQUE,
    type_1       TEXT NOT NULL,
    type_2       TEXT,
    height_m     NUMERIC(4, 1) NOT NULL CHECK (height_m > 0),
    weight_kg    NUMERIC(5, 1) NOT NULL CHECK (weight_kg > 0),
    legendary    BOOLEAN NOT NULL DEFAULT FALSE,
    version      INTEGER NOT NULL DEFAULT 0,         -- for optimistic concurrency (If-Match/ETag)
    created_at   TIMESTAMP NOT NULL DEFAULT now(),
    updated_at   TIMESTAMP NOT NULL DEFAULT now()
);

-- 1:1: at most one detail row per Pokémon
CREATE TABLE pokemon_detail (
    id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pokemon_id       INTEGER NOT NULL UNIQUE REFERENCES pokemon (id) ON DELETE CASCADE,
    catch_rate       INTEGER NOT NULL CHECK (catch_rate BETWEEN 1 AND 255),
    base_experience  INTEGER NOT NULL CHECK (base_experience > 0)
);

-- 1:N: several moves per Pokémon
CREATE TABLE move (
    id           INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pokemon_id   INTEGER NOT NULL REFERENCES pokemon (id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    type         TEXT NOT NULL,
    power        INTEGER CHECK (power > 0),          -- NULL for status moves
    accuracy     INTEGER CHECK (accuracy BETWEEN 1 AND 100)
);
CREATE INDEX move_pokemon_id_idx ON move (pokemon_id);
