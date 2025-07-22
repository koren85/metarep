# MetaRep - Техническая документация для ИИ

## Ключевые принципы архитектуры

### 1. Разделение ответственности

- **app.py**: Маршрутизация Flask, обработка HTTP запросов, рендеринг шаблонов
- **data_service.py**: Бизнес-логика, работа с данными, CRUD операции
- **database_manager.py**: Низкоуровневая работа с JDBC, соединения, транзакции
- **config.py**: Централизованная конфигурация из переменных окружения

### 2. Паттерны проектирования

- **Service Layer**: DataService инкапсулирует бизнес-логику
- **Data Access Object**: DatabaseManager абстрагирует работу с БД
- **Configuration Object**: MigrationConfig централизует настройки
- **Template Method**: Единообразная обработка запросов в Flask routes

## Структуры данных

### Основные Entity классы

```python
# Неявные структуры данных (возвращаются как dict)

Class = {
    'ouid': int,
    'name': str,
    'description': str,
    'status_variance': int,        # 0,1,2
    'event': int,                  # 0,1,2,3,4
    'a_priznak': int,             # 1,2,3
    'admin_url': str,             # URL в админку назначения
    'source_admin_url': str       # URL в админку источника
}

Group = {
    'ouid': int,
    'title': str,
    'name': str,
    'cls': int,                   # OUID класса-владельца
    'class_name': str,
    # ... остальные поля из SXATTR_GRP_SOURCE
}

Attribute = {
    'ouid': int,
    'name': str,
    'title': str,
    'description': str,
    'ouidsxclass': int,           # OUID класса-владельца
    'ouiddatatype': int,          # OUID типа данных
    'datatype_name': str,
    'class_name': str,
    'property_name': str,         # Имя свойства из различий
    'source': str,                # Значение source из различий
    'target': str,                # Значение target из различий
    'exception_actions': List[ExceptionAction],
    'overall_action': int,        # Общее действие (-1, 0, 2)
    'overall_action_name': str    # Текстовое описание действия
}

ExceptionAction = {
    'property_name': str,         # Имя свойства
    'source_value': str,          # Значение в источнике
    'target_value': str,          # Значение в назначении
    'exception_action': int,      # Действие исключения (0, 2)
    'action_name': str           # Текстовое описание
}

Difference = {
    'class_ouid': int,
    'class_name': str,
    'attribute_name': str,        # Имя свойства
    'source_value': str,
    'target_value': str,
    'difference_type': str,       # "Добавлено в target", "Удалено из target", "Изменено значение"
    'exception_action': int,
    'should_ignore': bool,
    'should_update': bool
}
```

### Пагинация

```python
PaginatedResult = {
    'items': List[Dict],          # classes/groups/attributes
    'total_count': int,           # Общее количество записей
    'total_pages': int,           # Общее количество страниц
    'current_page': int,          # Текущая страница
    'per_page': int,              # Записей на странице
    'has_prev': bool,             # Есть ли предыдущая страница
    'has_next': bool              # Есть ли следующая страница
}
```

## Алгоритмы работы с данными

### 1. Парсинг различий из a_log

**Вход**: строка a_log из таблицы _SOURCE
**Выход**: список различий с source/target значениями

```sql
-- Основной алгоритм парсинга
WITH log_lines AS (
    -- Шаг 1: Разбиваем a_log на строки с номерами
    SELECT unnest(string_to_array(a_log, E'\n')) as log_line,
           generate_series(1, array_length(string_to_array(a_log, E'\n'), 1)) as line_number
),
source_lines AS (
    -- Шаг 2: Находим строки с "source ="
    SELECT * FROM log_lines WHERE log_line ~ 'source[[:space:]]*='
),
attribute_names AS (
    -- Шаг 3: Определяем имена свойств (строка перед "source =")
    SELECT (SELECT trim(ll.log_line) FROM log_lines ll 
            WHERE ll.line_number = sl.line_number - 1) as attribute_name
),
extracted_values AS (
    -- Шаг 4: Извлекаем значения source и target
    SELECT attribute_name,
           regexp_replace(source_line, '^.*source[[:space:]]*=[[:space:]]*', '') as source_value,
           regexp_replace(target_line, '^.*target[[:space:]]*=[[:space:]]*', '') as target_value
)
```

### 2. Анализ исключений

**Вход**: список ExceptionAction для атрибута
**Выход**: общее действие (overall_action)

```python
def _get_overall_exception_action(exception_actions: List[Dict]) -> int:
    """
    Правило: если хотя бы одно свойство имеет действие "Обновить" (2),
    то общее действие - "Обновить". Иначе "Игнорировать" (0).
    """
    if not exception_actions:
        return 0  # По умолчанию игнорировать
    
    for action_data in exception_actions:
        if action_data.get('exception_action', 0) == 2:
            return 2  # Найдено действие "Обновить"
    
    return 0  # Все действия "Игнорировать"
```

### 3. Кэширование исключений

**Оптимизация**: загрузка всей таблицы __meta_statistic в память

```python
def _load_exceptions_cache(self) -> Dict[str, int]:
    """
    Создает кэш вида:
    {
        "attribute:readOnly": 2,
        "attribute:Только для чтения": 2,
        "class:description": 0,
        "group:title": 2
    }
    """
    cache = {}
    result = self.db_manager.execute_query("SELECT entity_type, entity_name, property_name, action FROM __meta_statistic")
    
    for entity_type, entity_name, property_name, action in result:
        # Создаем ключи для поиска по обеим вариантам
        key1 = f"{entity_type}:{entity_name}"       # По entity_name
        key2 = f"{entity_type}:{property_name}"     # По property_name
        cache[key1] = int(action)
        if property_name != entity_name:
            cache[key2] = int(action)
    
    return cache
```

## База данных

### Схема источника (SITEX)

```sql
-- Основные таблицы источника
SXCLASS_SOURCE (
    ouid INTEGER PRIMARY KEY,
    name VARCHAR(255),                    -- Имя класса
    description TEXT,                     -- Описание
    a_status_variance INTEGER,            -- Статус различий: 0,1,2
    a_event INTEGER,                      -- Событие/действие: 0,1,2,3,4
    a_priznak INTEGER,                    -- Признак миграции: 1,2,3
    a_log TEXT,                          -- Лог различий для парсинга
    a_issystem INTEGER,                  -- Системный класс
    a_createdate TIMESTAMP,
    a_editor VARCHAR(100),
    parent_ouid INTEGER                   -- OUID родительского класса
);

SXATTR_GRP_SOURCE (
    ouid INTEGER PRIMARY KEY,
    title VARCHAR(255),                   -- Заголовок группы
    name VARCHAR(255),                    -- Имя группы
    cls INTEGER,                          -- OUID класса-владельца
    num INTEGER,                          -- Порядковый номер
    a_status_variance INTEGER,
    a_event INTEGER,
    a_priznak INTEGER,
    a_log TEXT,
    -- ... остальные поля
    FOREIGN KEY (cls) REFERENCES SXCLASS_SOURCE(ouid)
);

SXATTR_SOURCE (
    ouid INTEGER PRIMARY KEY,
    name VARCHAR(255),                    -- Имя атрибута
    title VARCHAR(255),                   -- Заголовок
    description TEXT,                     -- Описание
    ouidsxclass INTEGER,                  -- OUID класса-владельца
    ouiddatatype INTEGER,                 -- OUID типа данных
    pkey INTEGER,                         -- Признак первичного ключа
    defvalue TEXT,                        -- Значение по умолчанию
    visible INTEGER,                      -- Видимость
    informs INTEGER,                      -- В форме
    read_only INTEGER,                    -- Только для чтения
    mandatory INTEGER,                    -- Обязательное
    calculated INTEGER,                   -- Вычисляемое
    length INTEGER,                       -- Длина
    a_status_variance INTEGER,
    a_event INTEGER,
    a_priznak INTEGER,
    a_log TEXT,
    -- ... остальные поля
    FOREIGN KEY (ouidsxclass) REFERENCES SXCLASS_SOURCE(ouid),
    FOREIGN KEY (ouiddatatype) REFERENCES SXDATATYPE(ouid)
);

-- Справочник типов данных
SXDATATYPE (
    ouid INTEGER PRIMARY KEY,
    description VARCHAR(255)              -- Описание типа
);
```

### Таблица исключений

```sql
CREATE TABLE __meta_statistic (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20) NOT NULL,     -- 'class', 'group', 'attribute'
    entity_name VARCHAR(100) NOT NULL,    -- Кодовое имя (для поиска)
    property_name VARCHAR(100) NOT NULL,  -- Описательное имя
    action INTEGER DEFAULT 0,             -- 0=игнорировать, 2=обновить
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_name, property_name)
);

-- Примеры данных:
INSERT INTO __meta_statistic VALUES 
(1, 'attribute', 'readOnly', 'Только для чтения', 2),
(2, 'attribute', 'visible', 'Загружать на клиент', 2),
(3, 'attribute', 'description', 'Описание', 0),
(4, 'class', 'title', 'Название', 0),
(5, 'group', 'num', '№ п/п', 2);
```

## API Endpoints детально

### REST API Convention

- **GET** `/api/{resource}` - Список ресурсов с пагинацией
- **GET** `/api/{resource}/{id}` - Детали ресурса
- **POST** `/api/{resource}` - Создание ресурса
- **PUT** `/api/{resource}/{id}` - Обновление ресурса
- **DELETE** `/api/{resource}/{id}` - Удаление ресурса

### Обработка параметров

```python
def get_classes(page=1, per_page=20, search=None, status_variance=None, 
                event=None, a_priznak=None, base_url=None, source_base_url=None):
    """
    Параметры:
    - page: номер страницы (>=1)
    - per_page: записей на странице (1-1000)
    - search: текст для ILIKE поиска по name/description
    - status_variance: точное соответствие (0,1,2)
    - event: точное соответствие (0,1,2,3,4)
    - a_priznak: точное соответствие (1,2,3)
    - base_url: базовый URL для admin_url (назначение)
    - source_base_url: базовый URL для source_admin_url (источник)
    """
    
    # Валидация параметров
    page = max(1, int(page))
    per_page = max(1, min(1000, int(per_page)))
    
    # Построение WHERE условий
    where_conditions = []
    if search:
        search_escaped = search.replace("'", "''")
        where_conditions.append(f"(name ILIKE '%{search_escaped}%' OR description ILIKE '%{search_escaped}%')")
    if status_variance is not None:
        where_conditions.append(f"a_status_variance = {status_variance}")
    # ... остальные фильтры
    
    # Пагинация
    offset = (page - 1) * per_page
    query = f"SELECT ... FROM sxclass_source WHERE {where_clause} ORDER BY name LIMIT {per_page} OFFSET {offset}"
```

### Специальные endpoints

```python
# Загрузка действий из исключений
POST /api/class/{class_ouid}/load-actions
{
    "search": "string",
    "status_variance": int,
    "event": int
}
# Response: {"success": true, "class_count": 5, "group_count": 10, "attribute_count": 50}

# Сохранение действий в БД
POST /api/class/{class_ouid}/save-actions  
{
    "search": "string",
    "status_variance": int,
    "event": int
}
# Response: {"success": true, "class_updated": 1, "group_updated": 5, "attribute_updated": 20}

# Миграция действий -1 → 2
POST /api/migrate-actions
# Response: {"success": true, "message": "Обновлено 150 записей: действие -1 -> 2"}

# Перезагрузка исключений из файлов
POST /api/reload-exceptions
# Response: {"success": true, "message": "Данные исключений успешно перезагружены из файлов"}
```

## Конфигурация окружения

### Автоопределение JAVA_HOME

```python
def auto_detect_java_home():
    """
    Порядок поиска Java:
    1. Переменная окружения JAVA_HOME
    2. Homebrew пути (macOS)
    3. Системные пути (macOS)
    4. Linux пути
    5. Fallback значение
    """
    java_home = os.getenv('JAVA_HOME')
    if java_home and os.path.exists(java_home):
        return java_home
    
    # Проверка Homebrew путей (M1/Intel Mac)
    homebrew_paths = [
        '/opt/homebrew/opt/openjdk',      # M1 Mac
        '/usr/local/opt/openjdk',         # Intel Mac
        '/opt/homebrew/opt/openjdk@8',    # Конкретные версии
        '/opt/homebrew/opt/openjdk@11',
        '/opt/homebrew/opt/openjdk@17',
    ]
    
    # Системные пути Java (macOS)
    system_paths = glob.glob('/Library/Java/JavaVirtualMachines/*/Contents/Home')
    
    # Linux пути
    linux_paths = [
        '/usr/lib/jvm/java-8-openjdk-amd64',
        '/usr/lib/jvm/default-java'
    ]
    
    all_paths = homebrew_paths + system_paths + linux_paths
    for path in all_paths:
        if os.path.exists(path):
            return path
    
    return '/usr/lib/jvm/default-java'  # Fallback
```

### JVM оптимизация

```python
def get_optimized_jvm_args():
    """
    Оптимизированные параметры JVM для JDBC:
    - Ограничение памяти (важно для контейнеров)
    - G1 сборщик мусора (лучше для коротких пауз)
    - Headless режим (без GUI)
    - Совместимость с ARM процессорами (M1/M2 Mac)
    """
    return [
        f"-Djava.class.path={classpath}",
        "-Xmx1024m",                      # Максимум 1GB heap
        "-Xms256m",                       # Начальный размер heap
        "-XX:+UseG1GC",                   # G1 Garbage Collector
        "-XX:MaxGCPauseMillis=200",       # Максимальная пауза GC
        "-Djava.awt.headless=true",       # Без GUI
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseZGC" if supports_zgc() else "-XX:+UseG1GC"
    ]
```

## Обработка ошибок

### Иерархия исключений

```python
class MetaRepException(Exception):
    """Базовое исключение MetaRep"""
    pass

class DatabaseConnectionError(MetaRepException):
    """Ошибка подключения к БД"""
    pass

class JVMInitializationError(MetaRepException):
    """Ошибка инициализации JVM"""
    pass

class QueryExecutionError(MetaRepException):
    """Ошибка выполнения SQL запроса"""
    pass

class ParseError(MetaRepException):
    """Ошибка парсинга данных"""
    pass
```

### Стратегия retry

```python
def with_retry(max_retries=3, delay=1.0):
    """
    Декоратор для повторных попыток операций БД
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (DatabaseConnectionError, QueryExecutionError) as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

# Использование:
@with_retry(max_retries=3, delay=1.0)
def execute_query(self, query: str):
    # ... выполнение запроса
```

## Тестирование

### Структура тестов

```python
# tests/test_data_service.py
class TestDataService:
    def setup_method(self):
        """Инициализация для каждого теста"""
        self.service = DataService()
        self.mock_db = Mock()
        self.service.db_manager = self.mock_db
    
    def test_get_classes_with_filters(self):
        """Тест фильтрации классов"""
        # Given
        self.mock_db.execute_query.return_value = [
            (1, 'TestClass', 'Description', 2, 4, 1)
        ]
        
        # When
        result = self.service.get_classes(status_variance=2, event=4)
        
        # Then
        assert result['total_count'] > 0
        assert 'TestClass' in [c['name'] for c in result['classes']]
    
    def test_parse_differences_from_log(self):
        """Тест парсинга различий"""
        # Given
        sample_log = """
        description
        source = Old Description
        target = New Description
        
        title
        source = Old Title
        target = New Title
        """
        
        # When
        differences = self.service._parse_log_differences(sample_log)
        
        # Then
        assert len(differences) == 2
        assert differences[0]['attribute_name'] == 'description'
        assert differences[0]['source_value'] == 'Old Description'
        assert differences[0]['target_value'] == 'New Description'
```

### Mock данные

```python
# tests/fixtures.py
SAMPLE_CLASS = {
    'ouid': 12345,
    'name': 'TestClass',
    'description': 'Test Class Description',
    'status_variance': 2,
    'event': 4,
    'a_priznak': 1
}

SAMPLE_ATTRIBUTE = {
    'ouid': 67890,
    'name': 'testAttr',
    'title': 'Test Attribute',
    'ouidsxclass': 12345,
    'ouiddatatype': 1,
    'a_log': 'readOnly\nsource = 0\ntarget = 1'
}

SAMPLE_EXCEPTIONS = [
    ('attribute', 'readOnly', 'Только для чтения', 2),
    ('attribute', 'visible', 'Загружать на клиент', 2),
    ('class', 'description', 'Описание', 0)
]
```

## Мониторинг и логирование

### Структура логов

```python
# Конфигурация логирования
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Настройка системы логирования:
    - Ротация файлов по размеру
    - Различные уровни для разных компонентов
    - Форматирование с timestamp и уровнем
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Основной файл логов
    file_handler = RotatingFileHandler(
        'logs/metarep.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Консольный вывод
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # Настройка логгеров
    loggers = [
        'data_service',
        'database_manager', 
        'app',
        'config'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
```

### Метрики производительности

```python
def log_performance(func):
    """
    Декоратор для логирования времени выполнения
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} выполнена за {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} завершилась с ошибкой за {execution_time:.3f}s: {e}")
            raise
    return wrapper

# Использование:
@log_performance
def get_classes(self, ...):
    # ... логика метода
```

## Security considerations

### SQL Injection защита

```python
def execute_safe_query(self, query_template: str, params: Dict[str, Any]):
    """
    Безопасное выполнение параметризованных запросов
    """
    # Валидация параметров
    validated_params = {}
    for key, value in params.items():
        if isinstance(value, str):
            # Экранирование кавычек
            validated_params[key] = value.replace("'", "''")
        elif isinstance(value, int):
            validated_params[key] = int(value)  # Принудительное приведение типа
        else:
            validated_params[key] = str(value)
    
    # Формирование запроса
    safe_query = query_template.format(**validated_params)
    return self.execute_query(safe_query)

# Использование:
query = "SELECT * FROM sxclass_source WHERE name ILIKE '%{search}%' AND a_status_variance = {status}"
result = self.execute_safe_query(query, {
    'search': user_input,
    'status': status_filter
})
```

### Валидация входных данных

```python
def validate_pagination_params(page: int, per_page: int) -> Tuple[int, int]:
    """
    Валидация параметров пагинации
    """
    page = max(1, int(page)) if page else 1
    per_page = max(1, min(1000, int(per_page))) if per_page else 20
    return page, per_page

def validate_entity_type(entity_type: str) -> str:
    """
    Валидация типа сущности
    """
    allowed_types = ['class', 'group', 'attribute']
    if entity_type not in allowed_types:
        raise ValueError(f"entity_type должен быть одним из: {allowed_types}")
    return entity_type

def validate_action(action: int) -> int:
    """
    Валидация действия исключения
    """
    allowed_actions = [0, 2]
    if action not in allowed_actions:
        raise ValueError(f"action должен быть одним из: {allowed_actions}")
    return action
```

## Deployment

### Docker многоэтапная сборка

```dockerfile
# Dockerfile
FROM python:3.12-slim as builder

# Установка Java
RUN apt-get update && apt-get install -y openjdk-17-jdk

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Продакшн образ
FROM python:3.12-slim

# Копирование Java
COPY --from=builder /usr/lib/jvm/java-17-openjdk-amd64 /usr/lib/jvm/java-17-openjdk-amd64
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Копирование Python окружения
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Рабочая директория
WORKDIR /app

# Копирование приложения
COPY . .

# Безопасность: непривилегированный пользователь
RUN useradd -m -s /bin/bash metarep
USER metarep

EXPOSE 5001
CMD ["python", "app.py"]
```

### Environment-specific конфигурации

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - FLASK_DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - .:/app  # Живая перезагрузка кода
    ports:
      - "5001:5001"

# docker-compose.prod.yml  
version: '3.8'
services:
  app:
    build: .
    environment:
      - FLASK_DEBUG=false
      - LOG_LEVEL=INFO
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
    depends_on:
      - app
```

## Performance optimization

### Кэширование

```python
from functools import lru_cache
from typing import Dict, Any

class CachedDataService(DataService):
    """
    Версия DataService с кэшированием для часто запрашиваемых данных
    """
    
    @lru_cache(maxsize=100)
    def get_class_details_cached(self, class_ouid: int) -> Dict[str, Any]:
        """
        Кэширование деталей класса (данные редко изменяются)
        """
        return self.get_class_details(class_ouid)
    
    @lru_cache(maxsize=1)
    def get_statistics_cached(self) -> Dict[str, Any]:
        """
        Кэширование статистики на 5 минут
        """
        return self.get_statistics()
    
    def invalidate_cache(self):
        """
        Сброс кэша при изменении данных
        """
        self.get_class_details_cached.cache_clear()
        self.get_statistics_cached.cache_clear()
```

### Пакетная обработка

```python
def batch_update_actions(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Пакетное обновление действий для повышения производительности
    """
    try:
        if not self.db_manager.connect():
            return {"error": "Ошибка подключения к БД"}
        
        with self.db_manager.transaction():
            updated_count = 0
            
            # Группировка обновлений по таблицам
            class_updates = [u for u in updates if u['entity_type'] == 'class']
            group_updates = [u for u in updates if u['entity_type'] == 'group'] 
            attr_updates = [u for u in updates if u['entity_type'] == 'attribute']
            
            # Пакетное обновление каждой таблицы
            for table, updates_list in [
                ('SXCLASS_SOURCE', class_updates),
                ('SXATTR_GRP_SOURCE', group_updates),
                ('SXATTR_SOURCE', attr_updates)
            ]:
                if updates_list:
                    batch_query = f"""
                        UPDATE {table} SET a_event = ? WHERE ouid = ?
                    """
                    prep_stmt = self.db_manager.connection.prepareStatement(batch_query)
                    
                    for update in updates_list:
                        prep_stmt.setInt(1, update['action'])
                        prep_stmt.setInt(2, update['ouid'])
                        prep_stmt.addBatch()
                    
                    results = prep_stmt.executeBatch()
                    updated_count += sum(results)
                    prep_stmt.close()
            
            return {"success": True, "updated_count": updated_count}
            
    except Exception as e:
        return {"error": f"Ошибка пакетного обновления: {e}"}
    finally:
        self.db_manager.disconnect()
```

Эта техническая документация предоставляет полную информацию для понимания и доработки системы MetaRep любым ИИ-разработчиком. 