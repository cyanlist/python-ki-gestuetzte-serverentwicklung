-- Testdaten: 12 Pokémon der 5. Generation (Auswahl). Werte aus dem Gedächtnis erfasst,
-- vor der Abgabe bitte stichprobenartig gegen PokeAPI oder Bulbapedia prüfen.
SET search_path TO pokemon;

INSERT INTO pokemon (id, name, typ1, typ2, groesse_m, gewicht_kg, legendaer) VALUES
    (494, 'Victini',   'Psycho',  'Feuer',  0.4,   4.0, TRUE),
    (495, 'Serpifeu',  'Pflanze', NULL,     0.6,   8.1, FALSE),
    (498, 'Floink',    'Feuer',   NULL,     0.5,   9.9, FALSE),
    (501, 'Ottaro',    'Wasser',  NULL,     0.5,   5.9, FALSE),
    (570, 'Zorua',     'Unlicht', NULL,     0.7,  12.5, FALSE),
    (571, 'Zoroark',   'Unlicht', NULL,     1.6,  81.1, FALSE),
    (609, 'Skelabra',  'Geist',   'Feuer',  1.0,  34.3, FALSE),
    (612, 'Maxax',     'Drache',  NULL,     1.8, 105.5, FALSE),
    (635, 'Trikephalo','Unlicht', 'Drache', 1.8, 160.0, FALSE),
    (643, 'Reshiram',  'Drache',  'Feuer',  3.2, 330.0, TRUE),
    (644, 'Zekrom',    'Drache',  'Elektro',2.9, 345.0, TRUE),
    (646, 'Kyurem',    'Drache',  'Eis',    3.0, 325.0, TRUE);

INSERT INTO pokemon_detail (pokemon_id, fangrate, basis_erfahrung) VALUES
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

INSERT INTO attacke (pokemon_id, name, typ, staerke, genauigkeit) VALUES
    (494, 'V-Generator',    'Feuer',   180,  95),
    (494, 'Psychokinese',   'Psycho',   90, 100),
    (495, 'Rankenhieb',     'Pflanze',  45, 100),
    (498, 'Glut',           'Feuer',    40, 100),
    (501, 'Aquaknarre',     'Wasser',   40, 100),
    (570, 'Kratzer',        'Normal',   40, 100),
    (571, 'Nachthieb',      'Unlicht',  70, 100),
    (609, 'Flammenwurf',    'Feuer',    90, 100),
    (609, 'Spukball',       'Geist',    80, 100),
    (612, 'Drachenklaue',   'Drache',   80, 100),
    (635, 'Drachenpuls',    'Drache',   85, 100),
    (635, 'Flammenwurf',    'Feuer',    90, 100),
    (643, 'Blauflammen',    'Feuer',   130,  85),
    (643, 'Drachenklaue',   'Drache',   80, 100),
    (644, 'Donnerblitz',    'Elektro',  90, 100),
    (644, 'Drachenklaue',   'Drache',   80, 100),
    (646, 'Eisstrahl',      'Eis',      90, 100),
    (646, 'Drachenpuls',    'Drache',   85, 100);
