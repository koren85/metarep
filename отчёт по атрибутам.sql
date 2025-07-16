-- Анализ различий между атрибутами источника и назначения в системе SiTex
-- PostgreSQL синтаксис (оптимизированная версия для больших объемов)

-- Создаем временную таблицу для парсинга различий с индексами
DROP TABLE IF EXISTS temp_parsed_attr_differences;
CREATE TEMP TABLE temp_parsed_attr_differences (
    attr_ouid INTEGER,
    attr_name VARCHAR(255),
    attr_description TEXT,
    attribute_name VARCHAR(255),
    source_value TEXT,
    target_value TEXT
);

-- Создаем индексы для оптимизации
CREATE INDEX idx_temp_attr_ouid ON temp_parsed_attr_differences(attr_ouid);
CREATE INDEX idx_temp_attr_name ON temp_parsed_attr_differences(attr_name);
CREATE INDEX idx_temp_attribute_name ON temp_parsed_attr_differences(attribute_name);

-- Упрощенный парсинг с использованием регулярных выражений
INSERT INTO temp_parsed_attr_differences (attr_ouid, attr_name, attr_description, attribute_name, source_value, target_value)
SELECT
    s.ouid,
    s.name,
    s.description,
    attr_blocks.attribute_name,
    attr_blocks.source_value,
    attr_blocks.target_value
FROM SXATTR_SOURCE s
CROSS JOIN LATERAL (
    -- Разбиваем A_LOG на блоки атрибутов с использованием regexp_split_to_table
    SELECT
        trim(split_part(attr_block, E'\n', 1)) as attribute_name,
        COALESCE(
            trim(regexp_replace(
                substring(attr_block from 'source[[:space:]]*=[[:space:]]*([^\n]*(?:\n[[:space:]]+[^\n]*)*?)(?=\n[[:space:]]*target[[:space:]]*=|\n[^[:space:]]|$)'),
                '^[[:space:]]*', '', 'g'
            )),
            ''
        ) as source_value,
        COALESCE(
            trim(regexp_replace(
                substring(attr_block from 'target[[:space:]]*=[[:space:]]*([^\n]*(?:\n[[:space:]]+[^\n]*)*?)(?=\n[^[:space:]]|$)'),
                '^[[:space:]]*', '', 'g'
            )),
            ''
        ) as target_value
    FROM unnest(
        -- Разбиваем по блокам (строки без отступов + следующие строки с отступами)
        regexp_split_to_array(
            s.a_log,
            E'(?=\n[^[:space:]\n])'
        )
    ) AS attr_block
    WHERE attr_block ~ 'source[[:space:]]*='
        AND trim(split_part(attr_block, E'\n', 1)) != ''
        AND length(trim(attr_block)) > 0
) attr_blocks
WHERE s.A_STATUS_VARIANCE = 2
    AND s.A_EVENT = 0
    AND attr_blocks.attribute_name IS NOT NULL
    AND attr_blocks.attribute_name != '';

-- Создаем индексы после вставки данных
ANALYZE temp_parsed_attr_differences;


WITH detailed_differences AS (
    SELECT
        attr_ouid,
        attr_name,
        attribute_name,
        source_value,
        target_value,
        CASE
            WHEN source_value = '' AND target_value != '' THEN 'Добавлено в target'
            WHEN source_value != '' AND target_value = '' THEN 'Удалено из target'
            WHEN source_value != target_value THEN 'Изменено значение'
            ELSE 'Неизвестный тип'
        END as difference_type,
        ROW_NUMBER() OVER (ORDER BY attr_name, attribute_name) as rn
    FROM temp_parsed_attr_differences
)
SELECT
    '=== ОТЧЕТ 5: ДЕТАЛЬНЫЕ РАЗЛИЧИЯ ПО АТРИБУТАМ (ПЕРВЫЕ 500 ЗАПИСЕЙ) ===' as info,
    0 as attr_ouid,
    '' as attr_name,
    '' as attribute_name,
    '' as source_value,
    '' as target_value,
    '' as difference_type
WHERE 1=0

UNION ALL

SELECT
    'Детали' as info,
    attr_ouid,
    attr_name,
    attribute_name,
    CASE
        WHEN LENGTH(source_value) > 200 THEN LEFT(source_value, 197) || '...'
        ELSE source_value
    END as source_value,
    CASE
        WHEN LENGTH(target_value) > 200 THEN LEFT(target_value, 197) || '...'
        ELSE target_value
    END as target_value,
    difference_type
FROM detailed_differences
-- WHERE rn <= 500  -- Ограничиваем для производительности
ORDER BY attr_name, attribute_name;
-- Очистка временной таблицы
DROP TABLE IF EXISTS temp_parsed_attr_differences;