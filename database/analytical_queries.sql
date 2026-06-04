-- Аналитические запросы к БД


-- Примеры SQL-запросов, которые могут быть применимы не только в моей базе,
-- но и в другой аналитической работе


-- 1. Воронка “художник => создание картины => выставление в музее” 
--    Аналог в продуктовой аналитике: воронка “регистрация => создание контента => публикация” 

WITH steps AS (
    SELECT 
        COUNT(DISTINCT a.artist_id) AS total_artists,
        COUNT(DISTINCT aw.artist_id) AS artists_with_artworks,
        COUNT(DISTINCT CASE WHEN aw.is_on_display = true THEN aw.artist_id END) AS artists_with_displayed
    FROM artists a
    LEFT JOIN artworks aw ON a.artist_id = aw.artist_id
)
SELECT 
    total_artists,
    artists_with_artworks,
    artists_with_displayed,
    ROUND(100.0 * artists_with_artworks / NULLIF(total_artists,0), 1) AS conv_to_artwork,
    ROUND(100.0 * artists_with_displayed / NULLIF(artists_with_artworks,0), 1) AS conv_to_displayed
FROM steps;


-- 2. RFM-сегментация художников (здесь использую частоту и стоимость, без давности)
--    Аналог: сегментация пользователей по выручке и активности
--    Делю художников на сегменты: VIP, High value, Regular, Newbie

WITH artist_value AS (
    SELECT 
        artist_id,
        COUNT(artwork_id) AS freq,
        COALESCE(SUM(estimated_value_eur), 0) AS monetary,
        MAX(creation_year) AS last_creation
    FROM artworks
    GROUP BY artist_id
),
segments AS (
    SELECT 
        artist_id,
        NTILE(4) OVER (ORDER BY monetary) AS monetary_segment,
        NTILE(4) OVER (ORDER BY freq) AS freq_segment
    FROM artist_value
)
SELECT 
    CASE 
        WHEN monetary_segment >= 3 AND freq_segment >= 3 THEN 'VIP'
        WHEN monetary_segment >= 3 THEN 'High value'
        WHEN freq_segment = 1 THEN 'Newbie'
        ELSE 'Regular'
    END AS segment,
    COUNT(*) AS artist_count
FROM segments
GROUP BY segment;


-- 3. Когорты художников по векам рождения: сравниваю, кто сколько создал
--    Аналог: удержание когорт пользователей по времени регистрации

WITH cohorts AS (
    SELECT 
        FLOOR(birth_year / 50) * 50 AS cohort,
        artist_id
    FROM artists
),
cohort_size AS (
    SELECT cohort, COUNT(DISTINCT artist_id) AS size
    FROM cohorts
    GROUP BY cohort
)
SELECT 
    c.cohort,
    cs.size,
    COUNT(DISTINCT aw.artwork_id) AS total_artworks,
    ROUND(COUNT(DISTINCT aw.artwork_id) * 1.0 / cs.size, 2) AS artworks_per_artist
FROM cohorts c
LEFT JOIN artworks aw ON c.artist_id = aw.artist_id
JOIN cohort_size cs ON c.cohort = cs.cohort
GROUP BY c.cohort, cs.size
ORDER BY c.cohort;


-- 4. Топ музеев по "конверсии" картин в выставочный статус
--    Аналог: эффективность каналов привлечения или торговых площадок

SELECT 
    m.museum_name,
    COUNT(aw.artwork_id) AS total_artworks,
    SUM(CASE WHEN aw.is_on_display THEN 1 ELSE 0 END) AS displayed,
    ROUND(100.0 * SUM(CASE WHEN aw.is_on_display THEN 1 ELSE 0 END) / COUNT(aw.artwork_id), 1) AS display_rate
FROM museums m
JOIN artworks aw ON m.museum_id = aw.museum_id
GROUP BY m.museum_id
ORDER BY display_rate DESC;


-- 5. Поиск аномально дорогих картин (z-score > 2)
--    Аналог: выявление выбросов в метриках (например, крупных заказов)

WITH stats AS (
    SELECT 
        AVG(estimated_value_eur) AS mean_val,
        STDDEV(estimated_value_eur) AS std_val
    FROM artworks
    WHERE estimated_value_eur IS NOT NULL
)
SELECT 
    title,
    estimated_value_eur,
    (estimated_value_eur - mean_val) / NULLIF(std_val, 0) AS z_score
FROM artworks, stats
WHERE estimated_value_eur IS NOT NULL
    AND ABS((estimated_value_eur - mean_val) / NULLIF(std_val, 0)) > 2
ORDER BY z_score DESC;


-- Для полноты демонстрации навыков также приведу 10 запросов разной степени сложности,
-- которые были созданы в расках курсовой работы (в скобочках применение в аналитике)


-- ПРОСТЫЕ ЗАПРОСЫ

-- 1. Список художников из Франции (фильтрация по региону)
SELECT full_name, birth_year, death_year, education_institution
FROM artists
WHERE country_of_birth = 'France'
ORDER BY birth_year;

-- 2. Картины, выставленные в музеях (отбор активных товаров)
SELECT title, creation_year, medium, estimated_value_eur
FROM artworks
WHERE is_on_display = true
ORDER BY creation_year DESC;

-- 3. Музеи с посещаемостью > 5 млн (крупные партнёрские площадки)
SELECT museum_name, country, foundation_year, annual_visitors
FROM museums
WHERE annual_visitors > 5000000
ORDER BY annual_visitors DESC;

-- 4. Художники, обучавшиеся в академиях (поиск по свойству)
SELECT full_name, country_of_birth, education_institution
FROM artists
WHERE education_institution ILIKE '%academy%'
ORDER BY full_name;

--СРЕДНИЕ ЗАПРОСЫ

-- 5. Список художников и их направлений (связь пользователей с категориями)
SELECT a.full_name AS artist_name, a.country_of_birth, m.movement_name AS art_movement
FROM artists a
INNER JOIN artist_movements am ON a.artist_id = am.artist_id
INNER JOIN art_movements m ON am.movement_id = m.movement_id
ORDER BY a.full_name, m.movement_name;

-- 6. Количество художников по направлениям (популярность категорий)
SELECT 
    m.movement_name AS art_movement,
    COUNT(DISTINCT am.artist_id) AS artists_count,
    m.country_of_origin
FROM art_movements m
LEFT JOIN artist_movements am ON m.movement_id = am.movement_id
GROUP BY m.movement_id, m.movement_name, m.country_of_origin
ORDER BY artists_count DESC, m.movement_name;

-- 7. Выставленные картины с данными о художниках и музеях (обогащённая выборка для дашборда)
SELECT 
    aw.title AS artwork_title,
    aw.creation_year,
    a.full_name AS artist_name,
    m.museum_name,
    m.country AS museum_country
FROM artworks aw
INNER JOIN artists a ON aw.artist_id = a.artist_id
LEFT JOIN museums m ON aw.museum_id = m.museum_id
WHERE aw.is_on_display = true
ORDER BY aw.creation_year DESC;

-- СЛОЖНЫЕ ЗАПРОСЫ
-- 8. Самое популярное направление по числу художников
SELECT 
    m.movement_name,
    COUNT(DISTINCT am.artist_id) AS artists_count
FROM art_movements m
INNER JOIN artist_movements am ON m.movement_id = am.movement_id
GROUP BY m.movement_id, m.movement_name
HAVING COUNT(DISTINCT am.artist_id) = (
    SELECT MAX(artist_count)
    FROM (
        SELECT COUNT(DISTINCT am2.artist_id) AS artist_count
        FROM art_movements m2
        INNER JOIN artist_movements am2 ON m2.movement_id = am2.movement_id
        GROUP BY m2.movement_id
    ) AS max_counts
)
ORDER BY m.movement_name;

-- 9. Импрессионистские картины после 1880 года (сегментация по времени и стилю)
SELECT 
    aw.title AS artwork_title,
    a.full_name AS artist_name,
    aw.creation_year,
    m.movement_name AS art_movement,
    aw.estimated_value_eur
FROM artworks aw
JOIN artists a ON aw.artist_id = a.artist_id
JOIN artist_movements am ON a.artist_id = am.artist_id
JOIN art_movements m ON am.movement_id = m.movement_id
WHERE m.movement_name = 'Impressionism'
    AND aw.creation_year > 1880
    AND aw.estimated_value_eur IS NOT NULL
ORDER BY aw.creation_year;

-- 10. Художники, у которых картины хранятся в музеях родной страны (локальный контент)
SELECT 
    a.full_name AS художник,
    a.country_of_birth AS страна_рождения,
    COUNT(aw.artwork_id) AS картин_в_родной_стране,
    ROUND(AVG(aw.estimated_value_eur), 2) AS средняя_стоимость
FROM artists a
JOIN artworks aw ON a.artist_id = aw.artist_id
JOIN museums m ON aw.museum_id = m.museum_id AND m.country = a.country_of_birth
WHERE aw.estimated_value_eur IS NOT NULL
GROUP BY a.artist_id, a.full_name, a.country_of_birth
HAVING COUNT(aw.artwork_id) >= 1
ORDER BY картин_в_родной_стране DESC, средняя_стоимость DESC;
