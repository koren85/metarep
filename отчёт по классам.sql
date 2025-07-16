-- Анализ различий между классами источника и назначения в системе SiTex
-- PostgreSQL синтаксис (исправленная версия парсинга)

-- Создаем временную таблицу для парсинга различий
DROP TABLE IF EXISTS temp_parsed_differences;
CREATE TEMP TABLE temp_parsed_differences (
    class_ouid INTEGER,
    class_name VARCHAR(255),
    class_description TEXT,
    attribute_name VARCHAR(255),
    source_value TEXT,
    target_value TEXT
);

-- Парсим поле A_LOG для извлечения различий
WITH log_lines AS (
    -- Разбиваем A_LOG на строки
    SELECT
        ouid as class_ouid,
        name as class_name,
        description as class_description,
        a_log,
        unnest(string_to_array(a_log, E'\n')) as log_line,
        generate_series(1, array_length(string_to_array(a_log, E'\n'), 1)) as line_number
    FROM SXCLASS_SOURCE
    WHERE A_STATUS_VARIANCE = 2 AND A_EVENT = 4

),
source_lines AS (
    -- Находим все строки с "source ="
    SELECT
        class_ouid,
        class_name,
        class_description,
        line_number,
        log_line,
        ROW_NUMBER() OVER (PARTITION BY class_name ORDER BY line_number) as source_seq
    FROM log_lines
    WHERE log_line ~ 'source[[:space:]]*='
),
attribute_names AS (
    -- Получаем названия атрибутов (строка перед "source =")
    SELECT
        sl.class_ouid,
        sl.class_name,
        sl.class_description,
        sl.line_number as source_line_number,
        sl.source_seq,
        COALESCE(
            (SELECT trim(ll.log_line)
             FROM log_lines ll
             WHERE ll.class_name = sl.class_name
               AND ll.line_number = sl.line_number - 1
               AND trim(ll.log_line) != ''
             LIMIT 1),
            'unknown_attribute_' || sl.source_seq
        ) as attribute_name
    FROM source_lines sl
),
source_target_blocks AS (
    -- Определяем блоки source/target для каждого атрибута
    SELECT
        an.class_ouid,
        an.class_name,
        an.class_description,
        an.attribute_name,
        an.source_seq,
        an.source_line_number,
        LEAD(an.source_line_number, 1, 999999) OVER (
            PARTITION BY an.class_name
            ORDER BY an.source_line_number
        ) as next_source_line_number
    FROM attribute_names an
),
extracted_values AS (
    -- Извлекаем значения source и target
    SELECT
        stb.class_ouid,
        stb.class_name,
        stb.class_description,
        stb.attribute_name,
        -- Извлекаем source значение
        string_agg(
            CASE
                WHEN ll.log_line ~ 'source[[:space:]]*=' THEN
                    trim(regexp_replace(ll.log_line, '^.*source[[:space:]]*=[[:space:]]*', ''))
                WHEN ll.log_line ~ 'target[[:space:]]*=' THEN NULL
                ELSE trim(ll.log_line)
            END,
            ' ' ORDER BY ll.line_number
        ) FILTER (WHERE ll.line_number >= stb.source_line_number
                    AND ll.line_number < COALESCE(
                        (SELECT MIN(ll2.line_number)
                         FROM log_lines ll2
                         WHERE ll2.class_name = stb.class_name
                           AND ll2.line_number > stb.source_line_number
                           AND ll2.log_line ~ 'target[[:space:]]*='),
                        stb.next_source_line_number
                    )) as source_value,
        -- Извлекаем target значение
        string_agg(
            CASE
                WHEN ll.log_line ~ 'target[[:space:]]*=' THEN
                    trim(regexp_replace(ll.log_line, '^.*target[[:space:]]*=[[:space:]]*', ''))
                WHEN ll.log_line ~ 'source[[:space:]]*=' THEN NULL
                WHEN ll.log_line !~ '^[[:space:]]' AND trim(ll.log_line) != '' THEN NULL  -- Исключаем названия атрибутов
                ELSE trim(ll.log_line)
            END,
            ' ' ORDER BY ll.line_number
        ) FILTER (WHERE ll.line_number > stb.source_line_number
                    AND ll.line_number < stb.next_source_line_number
                    AND ll.line_number >= COALESCE(
                        (SELECT MIN(ll2.line_number)
                         FROM log_lines ll2
                         WHERE ll2.class_name = stb.class_name
                           AND ll2.line_number > stb.source_line_number
                           AND ll2.log_line ~ 'target[[:space:]]*='),
                        stb.next_source_line_number
                    )
                    AND ll.line_number < COALESCE(
                        (SELECT MIN(ll3.line_number)
                         FROM log_lines ll3
                         WHERE ll3.class_name = stb.class_name
                           AND ll3.line_number > COALESCE(
                               (SELECT MIN(ll2.line_number)
                                FROM log_lines ll2
                                WHERE ll2.class_name = stb.class_name
                                  AND ll2.line_number > stb.source_line_number
                                  AND ll2.log_line ~ 'target[[:space:]]*='),
                               stb.next_source_line_number
                           )
                           AND ll3.log_line !~ '^[[:space:]]'
                           AND trim(ll3.log_line) != ''),
                        stb.next_source_line_number
                    )) as target_value
    FROM source_target_blocks stb
    JOIN log_lines ll ON ll.class_name = stb.class_name
    GROUP BY stb.class_ouid, stb.class_name, stb.class_description, stb.attribute_name, stb.source_seq,
             stb.source_line_number, stb.next_source_line_number
)
INSERT INTO temp_parsed_differences (class_ouid, class_name, class_description, attribute_name, source_value, target_value)
SELECT
    class_ouid,
    class_name,
    class_description,
    attribute_name,
    COALESCE(trim(source_value), '') as source_value,
    COALESCE(trim(target_value), '') as target_value
FROM extracted_values
WHERE attribute_name IS NOT NULL
    AND attribute_name != ''
    AND NOT attribute_name LIKE 'unknown_attribute_%';

SELECT
    '=== ОТЧЕТ 4: ДЕТАЛЬНЫЕ РАЗЛИЧИЯ ПО КЛАССАМ ===' as info,
    0 as class_ouid,
    '' as class_name,
    '' as attribute_name,
    '' as source_value,
    '' as target_value,
    '' as difference_type
WHERE 1=0

UNION ALL

SELECT
    'Детали' as info,
    class_ouid,
    class_name,
    attribute_name,
    CASE
        WHEN LENGTH(source_value) > 100 THEN LEFT(source_value, 97) || '...'
        ELSE source_value
    END as source_value,
    CASE
        WHEN LENGTH(target_value) > 100 THEN LEFT(target_value, 97) || '...'
        ELSE target_value
    END as target_value,
    CASE
        WHEN source_value = '' AND target_value != '' THEN 'Добавлено в target'
        WHEN source_value != '' AND target_value = '' THEN 'Удалено из target'
        WHEN source_value != target_value THEN 'Изменено значение'
        ELSE 'Неизвестный тип'
    END as difference_type
FROM temp_parsed_differences
ORDER BY class_name, attribute_name;



-- Очистка временной таблицы
DROP TABLE IF EXISTS temp_parsed_differences;