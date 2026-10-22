-- Test data: 12 Pokémon from Generation 5 (selection). Values entered from memory,
-- please spot-check against PokeAPI or Bulbapedia before submission.
SET search_path TO pokemon;

INSERT INTO pokemon (id, name, type_1, type_2, height_m, weight_kg, legendary) VALUES
    (494, 'Victini',   'Psychic', 'Fire',   0.4,   4.0, TRUE),
    (495, 'Snivy',     'Grass',   NULL,     0.6,   8.1, FALSE),
    (498, 'Tepig',     'Fire',    NULL,     0.5,   9.9, FALSE),
    (501, 'Oshawott',  'Water',   NULL,     0.5,   5.9, FALSE),
    (570, 'Zorua',     'Dark',    NULL,     0.7,  12.5, FALSE),
    (571, 'Zoroark',   'Dark',    NULL,     1.6,  81.1, FALSE),
    (609, 'Chandelure','Ghost',   'Fire',   1.0,  34.3, FALSE),
    (612, 'Haxorus',   'Dragon',  NULL,     1.8, 105.5, FALSE),
    (635, 'Hydreigon', 'Dark',    'Dragon', 1.8, 160.0, FALSE),
    (643, 'Reshiram',  'Dragon',  'Fire',   3.2, 330.0, TRUE),
    (644, 'Zekrom',    'Dragon',  'Electric', 2.9, 345.0, TRUE),
    (646, 'Kyurem',    'Dragon',  'Ice',    3.0, 325.0, TRUE);

INSERT INTO pokemon_detail (pokemon_id, catch_rate, base_experience) VALUES
    (494,   3, 270),
    (495,  45,  62),
    (498,  45,  62),
    (501,  45,  62),
    (570,  75,  66),
    (571,  45, 179),
    (609,  45, 260),
    (612,  45, 270),
    (635,  45, 300),
    (643,   3, 306),
    (644,   3, 306),
    (646,   3, 297);

INSERT INTO move (pokemon_id, name, type, power, accuracy) VALUES
    (494, 'V-create',       'Fire',     180,  95),
    (494, 'Psychic',        'Psychic',   90, 100),
    (495, 'Vine Whip',      'Grass',     45, 100),
    (498, 'Ember',          'Fire',      40, 100),
    (501, 'Water Gun',      'Water',     40, 100),
    (570, 'Scratch',        'Normal',    40, 100),
    (571, 'Night Slash',    'Dark',      70, 100),
    (609, 'Flamethrower',   'Fire',      90, 100),
    (609, 'Shadow Ball',    'Ghost',     80, 100),
    (612, 'Dragon Claw',    'Dragon',    80, 100),
    (635, 'Dragon Pulse',   'Dragon',    85, 100),
    (635, 'Flamethrower',   'Fire',      90, 100),
    (643, 'Blue Flare',     'Fire',     130,  85),
    (643, 'Dragon Claw',    'Dragon',    80, 100),
    (644, 'Thunderbolt',    'Electric',  90, 100),
    (644, 'Dragon Claw',    'Dragon',    80, 100),
    (646, 'Ice Beam',       'Ice',       90, 100),
    (646, 'Dragon Pulse',   'Dragon',    85, 100);
