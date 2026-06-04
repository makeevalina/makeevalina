-- Проект: База данных "Европейское художественное наследие XIX–XX веков"
-- Автор: Макеева Али, СПбГУ, ПМ-ПУ
-- Описание: Данные о художниках, картинах, музеях и художественных направлениях
--           Таблицы адаптированы под задачи продуктовой аналитики:
--           artists => пользователи,
-- 			 artworks => товары/контент,
--           museums => площадки/каналы,
-- 			 art_movements => категории/теги


DROP TABLE IF EXISTS artist_movements CASCADE;
DROP TABLE IF EXISTS artworks CASCADE;
DROP TABLE IF EXISTS artists CASCADE;
DROP TABLE IF EXISTS art_movements CASCADE;
DROP TABLE IF EXISTS museums CASCADE;

-- СОЗДАНИЕ ТАБЛИЦ

-- Таблица "artists" — художники.
-- Аналог таблицы "пользователи" в продуктовой аналитике.
-- Поля: artist_id (уникальный ID), full_name (имя), birth_year, death_year,
--       country_of_birth, education_institution

CREATE TABLE artists(
	artist_id SERIAL PRIMARY KEY,
	full_name VARCHAR(100) NOT NULL,
	birth_year INTEGER NOT NULL CHECK(
        birth_year >= 1740 AND 
        birth_year <= 1950
    ),
	death_year INTEGER CHECK(
        death_year IS NULL OR 
        (death_year >= birth_year + 16 AND 
         death_year <= EXTRACT(YEAR FROM CURRENT_DATE))
		 ),
	country_of_birth VARCHAR(100) NOT NULL,
	education_institution VARCHAR(100),

	UNIQUE(full_name, birth_year)
);


-- Таблица "museums" — музеи и галереи
-- Аналог таблицы "площадки / каналы дистрибуции"
-- Поля: museum_id, museum_name, country, foundation_year, annual_visitors

CREATE TABLE museums(
	museum_id SERIAL PRIMARY KEY,
	museum_name VARCHAR(100) NOT NULL,
	country VARCHAR(50) NOT NULL,
	foundation_year INTEGER NOT NULL CHECK(
        foundation_year <= EXTRACT(YEAR FROM CURRENT_DATE)
    ),
	annual_visitors INTEGER CHECK(annual_visitors >= 0),

	UNIQUE(museum_name, country)
);


-- Таблица "artworks" — произведения искусства
-- Аналог таблицы "товары / контент" в продуктовой аналитике
-- Поля: artwork_id, title, creation_year, medium, estimated_value_eur,
--       is_on_display (аналог "опубликовано"), artist_id, museum_id

CREATE TABLE artworks(
	artwork_id SERIAL PRIMARY KEY,
	title VARCHAR(100) NOT NULL,
	creation_year INTEGER NOT NULL CHECK(
        creation_year >= 1800 AND 
        creation_year <= EXTRACT(YEAR FROM CURRENT_DATE)
    ),
	medium VARCHAR(100) NOT NULL,
	estimated_value_eur DECIMAL(12,2) CHECK (estimated_value_eur >= 0),
	is_on_display BOOLEAN DEFAULT TRUE,
	-- поля для связей
	artist_id INTEGER NOT NULL,
	museum_id INTEGER,
	-- внешние ключи
	FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
	FOREIGN KEY (museum_id) REFERENCES museums(museum_id),

	UNIQUE(title, artist_id, creation_year),

	EXCLUDE USING btree (
        artist_id WITH =,
        title WITH =,
        creation_year WITH = 1900
    )
	
);

-- Таблица "art_movements" — справочник художественных направлений
-- Аналог таблицы "категории / теги продукта"
-- Поля: movement_id, movement_name, century_start, country_of_origin

CREATE TABLE art_movements(
	movement_id SERIAL PRIMARY KEY,
	movement_name VARCHAR(100) UNIQUE NOT NULL CHECK (
        movement_name IN (
            'Romanticism', 'Realism', 'Impressionism', 'Post-Impressionism',
            'Symbolism', 'Art Nouveau', 'Fauvism', 'Expressionism', 'Cubism',
            'Futurism', 'Dada', 'Surrealism', 'Abstract Expressionism',
            'Pop Art', 'Minimalism', 'Conceptual Art'
        )
    ),
	century_start INTEGER NOT NULL CHECK (
        century_start IN (18, 19, 20)
    ),
	country_of_origin VARCHAR(100)


	
);

-- Таблица "artist_movements" — связь художников с художественными направлениями (многие-ко-многим)
-- Аналог связки "пользователь → категории / теги" в продуктовой аналитике
-- Поля: artist_id (ссылка на художника), movement_id (ссылка на направление)

CREATE TABLE artist_movements(
	 artist_id INTEGER,
	 movement_id INTEGER,
	 FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
	 FOREIGN KEY (movement_id) REFERENCES art_movements(movement_id),
	 PRIMARY KEY(artist_id, movement_id)
	 
);



--ЗАПОЛНЕНИЕ--
--художники--
INSERT INTO artists (full_name, birth_year, death_year, country_of_birth, education_institution) VALUES
('Claude Monet', 1840, 1926, 'France', 'Académie Suisse'),
('Pierre-Auguste Renoir', 1841, 1919, 'France', 'École des Beaux-Arts'),
('Edgar Degas', 1834, 1917, 'France', 'École des Beaux-Arts'),
('Édouard Manet', 1832, 1883, 'France', 'Collège Rollin'),
('Paul Cézanne', 1839, 1906, 'France', 'Académie Suisse'),
('Henri Matisse', 1869, 1954, 'France', 'Académie Julian'),
('Georges Braque', 1882, 1963, 'France', 'École des Beaux-Arts'),
('Camille Pissarro', 1830, 1903, 'France', 'Académie Suisse'),
('Pablo Picasso', 1881, 1973, 'Spain', 'Royal Academy of San Fernando'),
('Salvador Dalí', 1904, 1989, 'Spain', 'Royal Academy of Fine Arts of San Fernando'),
('Francisco Goya', 1746, 1828, 'Spain', 'Royal Academy of Fine Arts of San Fernando'),
('Joan Miró', 1893, 1983, 'Spain', 'Cercle Artístic de Sant Lluc'),
('Vincent van Gogh', 1853, 1890, 'Netherlands', 'Royal Academy of Fine Arts'),
('Piet Mondrian', 1872, 1944, 'Netherlands', 'Rijksakademie van beeldende kunsten'),
('Caspar David Friedrich', 1774, 1840, 'Germany', 'University of Greifswald'),
('Max Ernst', 1891, 1976, 'Germany', 'University of Bonn'),
('Gustav Klimt', 1862, 1918, 'Austria', 'Vienna School of Arts and Crafts'),
('Egon Schiele', 1890, 1918, 'Austria', 'Academy of Fine Arts Vienna'),
('Edvard Munch', 1863, 1944, 'Norway', 'Royal School of Art and Design'),
('Amedeo Modigliani', 1884, 1920, 'Italy', 'Accademia di Belle Arti'),
('Giorgio de Chirico', 1888, 1978, 'Italy', 'Academy of Fine Arts, Munich'),
('Wassily Kandinsky', 1866, 1944, 'Russia', 'Academy of Fine Arts, Munich'),
('Kazimir Malevich', 1879, 1935, 'Russia', 'Moscow School of Painting'),
('Marc Chagall', 1887, 1985, 'Russia', 'Imperial Society for the Encouragement of the Arts');

--музеи--
INSERT INTO museums (museum_name, country, foundation_year, annual_visitors) VALUES
('Musée du Louvre', 'France', 1793, 9700000),
('Musée d''Orsay', 'France', 1986, 3600000),
('Centre Pompidou', 'France', 1977, 3300000),
('Museo del Prado', 'Spain', 1819, 3400000),
('Museo Nacional Centro de Arte Reina Sofía', 'Spain', 1992, 3800000),
('Guggenheim Museum Bilbao', 'Spain', 1997, 1100000),
('Rijksmuseum', 'Netherlands', 1800, 2700000),
('Van Gogh Museum', 'Netherlands', 1973, 2100000),
('Stedelijk Museum', 'Netherlands', 1874, 700000),
('Metropolitan Museum of Art', 'USA', 1870, 7000000),
('Museum of Modern Art (MoMA)', 'USA', 1929, 3100000),
('Tate Modern', 'UK', 2000, 5900000),
('National Gallery', 'UK', 1824, 6000000),
('Alte Nationalgalerie', 'Germany', 1876, 500000),
('Museum Berggruen', 'Germany', 1996, 300000),
('State Russian Museum', 'Russia', 1895, 2200000);

--художественные направления--
INSERT INTO art_movements (movement_name, century_start, country_of_origin) VALUES
('Romanticism', 18, 'Germany'),
('Realism', 19, 'France'),
('Impressionism', 19, 'France'),
('Post-Impressionism', 19, 'France'),
('Symbolism', 19, 'France'),
('Art Nouveau', 19, 'Belgium'),
('Fauvism', 20, 'France'),
('Expressionism', 20, 'Germany'),
('Cubism', 20, 'France'),
('Futurism', 20, 'Italy'),
('Dada', 20, 'Switzerland'),
('Surrealism', 20, 'France'),
('Abstract Expressionism', 20, 'USA'),
('Pop Art', 20, 'UK'),
('Minimalism', 20, 'USA'),
('Conceptual Art', 20, 'USA');

--картины--
INSERT INTO artworks (title, creation_year, medium, estimated_value_eur, is_on_display, artist_id, museum_id) VALUES
('The Starry Night', 1889, 'Oil on canvas', 100000000.00, true, 1, 8),
('Sunflowers', 1888, 'Oil on canvas', 85000000.00, true, 1, 8),
('The Potato Eaters', 1885, 'Oil on canvas', 40000000.00, false, 1, 7),
('Water Lilies', 1916, 'Oil on canvas', 55000000.00, true, 2, 1),
('Impression, Sunrise', 1872, 'Oil on canvas', 75000000.00, true, 2, 2),
('Haystacks', 1890, 'Oil on canvas', 45000000.00, true, 2, 1),
('Bal du moulin de la Galette', 1876, 'Oil on canvas', 180000000.00, true, 3, 1),
('Luncheon of the Boating Party', 1881, 'Oil on canvas', 90000000.00, true, 3, 10),
('The Ballet Class', 1874, 'Oil on canvas', 45000000.00, true, 4, 1),
('Little Dancer of Fourteen Years', 1881, 'Bronze sculpture', 35000000.00, true, 4, 2),
('Olympia', 1863, 'Oil on canvas', 120000000.00, true, 5, 2),
('A Bar at the Folies-Bergère', 1882, 'Oil on canvas', 110000000.00, true, 5, 13),
('The Card Players', 1895, 'Oil on canvas', 260000000.00, true, 6, 1),
('Mont Sainte-Victoire', 1904, 'Oil on canvas', 50000000.00, true, 6, 10),
('The Dance', 1910, 'Oil on canvas', 300000000.00, true, 7, 1),
('Woman with a Hat', 1905, 'Oil on canvas', 20000000.00, true, 7, 10),
('Les Demoiselles d''Avignon', 1907, 'Oil on canvas', 120000000.00, true, 9, 11),
('Guernica', 1937, 'Oil on canvas', 200000000.00, true, 9, 5),
('The Old Guitarist', 1903, 'Oil on canvas', 40000000.00, true, 9, 10),
('The Persistence of Memory', 1931, 'Oil on canvas', 150000000.00, true, 10, 11),
('The Elephants', 1948, 'Oil on canvas', 70000000.00, true, 10, 4),
('The Kiss', 1908, 'Oil and gold leaf on canvas', 240000000.00, true, 18, 9),
('Portrait of Adele Bloch-Bauer I', 1907, 'Oil and gold on canvas', 135000000.00, true, 18, 15),
('Portrait of Wally', 1912, 'Oil on canvas', 35000000.00, true, 19, 15),
('Self-Portrait with Physalis', 1912, 'Oil on canvas', 25000000.00, true, 19, 9),
('The Scream', 1893, 'Oil, tempera, pastel on cardboard', 120000000.00, true, 20, NULL),
('Composition VIII', 1923, 'Oil on canvas', 40000000.00, true, 17, 11),
('Yellow-Red-Blue', 1925, 'Oil on canvas', 35000000.00, true, 17, 16),
('Suprematist Composition', 1916, 'Oil on canvas', 30000000.00, true, 23, 16),
('I and the Village', 1911, 'Oil on canvas', 55000000.00, true, 24, 11),
('The Fiddler', 1912, 'Oil on canvas', 30000000.00, true, 24, 16),
('Portrait of Jeanne Hébuterne', 1918, 'Oil on canvas', 45000000.00, true, 21, 11),
('Reclining Nude', 1917, 'Oil on canvas', 170000000.00, true, 21, 13),
('Violin and Candlestick', 1910, 'Oil on canvas', 50000000.00, true, 8, 10),
('Houses at L''Estaque', 1908, 'Oil on canvas', 45000000.00, true, 8, 1),
('Composition with Red, Blue and Yellow', 1930, 'Oil on canvas', 50000000.00, true, 14, 11),
('Broadway Boogie Woogie', 1943, 'Oil on canvas', 40000000.00, true, 14, 8),
('Boulevard Montmartre at Night', 1897, 'Oil on canvas', 40000000.00, true, 15, 2),
('The Harvest', 1882, 'Oil on canvas', 25000000.00, true, 15, 7);


-- Подсчёт количества полей в таблицах (для самопроверки)
SELECT 
    table_name,
    COUNT(*) as columns_count
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name IN ('artists', 'art_movements', 'museums', 'artworks', 'artist_movements')
GROUP BY table_name
ORDER BY table_name;









