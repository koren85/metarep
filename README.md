# MetaRep - Система Анализа Метаданных Миграции SITEX-ЭСРН

## Описание проекта

MetaRep - это веб-приложение на Flask для анализа и управления процессом миграции метаданных из Microsoft SQL Server в PostgreSQL в рамках системы SITEX-ЭСРН. Приложение предоставляет детальную аналитику различий между источником и назначением, управление исключениями и отчетность.

## Архитектура системы

### Основные компоненты

```
metarep/
├── app.py                    # Главный Flask модуль с маршрутами
├── data_service.py          # Основной сервис бизнес-логики
├── database_manager.py      # JDBC менеджер подключений к БД
├── config.py               # Конфигурация из переменных окружения
├── diagnostic.py           # Диагностические утилиты
├── templates/              # HTML шаблоны Jinja2
├── static/                 # Статические файлы (CSS, JS, images)
├── lib/                    # JDBC драйверы
│   ├── mssql-jdbc.jar     # Драйвер Microsoft SQL Server
│   └── postgresql.jar     # Драйвер PostgreSQL
├── *.sql                  # SQL отчеты и запросы
├── *.md                   # Файлы исключений и документация
└── docker-compose.yml     # Docker конфигурация
```

### Технологический стек

- **Backend**: Python 3.12, Flask
- **Database**: PostgreSQL (назначение), MSSQL (источник)
- **JDBC**: JPype1 для работы с Java драйверами
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Deployment**: Docker, Docker Compose

## Конфигурация системы

### Переменные окружения (.env)

```bash
# PostgreSQL (назначение)
POSTGRES_HOST=10.3.0.254
POSTGRES_PORT=22618
POSTGRES_DB=sdu_postgres_migration_20250404
POSTGRES_USER=tomcat
POSTGRES_PASSWORD=password

# MSSQL (источник)
MSSQL_HOST=
MSSQL_PORT=1433
MSSQL_DB=
MSSQL_USER=
MSSQL_PASSWORD=

# Java и JDBC
JAVA_HOME=/opt/homebrew/opt/openjdk
MSSQL_DRIVER_PATH=./lib/mssql-jdbc.jar
POSTGRES_DRIVER_PATH=./lib/postgresql.jar

# SITEX-ЭСРН
SITEX_CONTEXT_URL=http://10.3.0.254:22617/test_voron_124724_migration_0001/

# Flask
PORT=5001
FLASK_DEBUG=false
```

### Структура конфигурации (config.py)

```python
@dataclass
class MigrationConfig:
    mssql: DatabaseConfig           # Конфигурация MSSQL
    postgres: DatabaseConfig       # Конфигурация PostgreSQL
    java_home: str                 # Путь к Java
    sitex_context_url: str         # URL админки SITEX
    directories: DirectoryConfig    # Пути директорий
    logging: LoggingConfig         # Настройки логирования
    task_generation: TaskGenerationConfig
    class_analysis: ClassAnalysisConfig
    performance: PerformanceConfig
```

## Структура базы данных

### Основные таблицы источника

- **SXCLASS_SOURCE** - Классы объектов
- **SXATTR_GRP_SOURCE** - Группы атрибутов  
- **SXATTR_SOURCE** - Атрибуты
- **SXDATATYPE** - Типы данных

### Таблица исключений

```sql
CREATE TABLE __meta_statistic (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20) NOT NULL,     -- 'class', 'group', 'attribute'
    entity_name VARCHAR(100) NOT NULL,    -- Имя сущности
    property_name VARCHAR(100) NOT NULL,  -- Имя свойства
    action INTEGER DEFAULT 0,             -- 0=игнорировать, 2=обновить
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_name, property_name)
);
```

### Ключевые поля статуса

- **a_status_variance**: 2 = есть различия
- **a_event**: действие (0=без действия, 2=обновить, 4=анализ)
- **a_priznak**: признак миграции (1=переносим, 2=не переносим, 3=вручную)

## Основные модули

### 1. DataService (data_service.py)

Основной сервис бизнес-логики приложения.

#### Методы получения данных:

```python
def get_classes(page, per_page, search, status_variance, event, a_priznak, base_url, source_base_url)
def get_groups(page, per_page, search, status_variance, event, a_priznak, base_url, source_base_url)  
def get_attributes(page, per_page, search, status_variance, event, a_priznak, base_url, source_base_url, exception_action_filter, analyze_exceptions)
def get_class_details(class_ouid, base_url, source_base_url, search, status_variance, event, a_priznak)
```

#### Методы анализа различий:

```python
def get_class_differences(class_ouid, base_url, source_base_url, skip_disconnect)
def get_group_differences(class_ouid, search, status_variance, event, a_priznak, base_url, source_base_url, skip_disconnect)
def get_attribute_differences(class_ouid, search, status_variance, event, a_priznak, base_url, source_base_url, skip_disconnect)
```

#### CRUD операции для исключений:

```python
def get_exceptions(page, per_page, entity_type, search)
def get_exception(exception_id)
def create_exception(entity_type, entity_name, property_name, action)
def update_exception(exception_id, entity_type, entity_name, property_name, action)
def delete_exception(exception_id)
```

#### Управление действиями миграции:

```python
def load_actions_from_exceptions(class_ouid, search, status_variance, event)
def save_actions_to_db(class_ouid, search, status_variance, event)
def migrate_actions_from_minus_one_to_two()
```

### 2. DatabaseManager (database_manager.py)

Менеджер подключений к базам данных через JDBC.

#### Возможности:

- Автоматическая инициализация JVM
- Поддержка транзакций
- Подключение к MSSQL и PostgreSQL
- Управление таймаутами соединений
- Создание и инициализация таблицы исключений

```python
class DatabaseManager:
    def connect() -> bool
    def disconnect()
    def execute_query(query: str) -> List[Tuple[Any, ...]]
    def execute_update(query: str) -> int
    
    @contextmanager
    def transaction()
```

### 3. Flask приложение (app.py)

Веб-интерфейс с маршрутами для всех операций.

#### Основные маршруты:

**Страницы просмотра:**
- `GET /` - Список классов
- `GET /groups` - Список групп атрибутов
- `GET /attributes` - Список атрибутов  
- `GET /class/<int:class_ouid>` - Детали класса
- `GET /exceptions` - Управление исключениями

**API endpoints:**
- `GET /api/classes` - JSON список классов
- `GET /api/groups` - JSON список групп
- `GET /api/attributes` - JSON список атрибутов
- `GET /api/class/<int:class_ouid>` - JSON детали класса
- `GET /api/statistics` - JSON статистика

**API исключений:**
- `GET /api/exceptions` - Список исключений
- `POST /api/exceptions` - Создание исключения
- `PUT /api/exceptions/<id>` - Обновление исключения
- `DELETE /api/exceptions/<id>` - Удаление исключения

**API действий:**
- `POST /api/class/<id>/load-actions` - Загрузка действий
- `POST /api/class/<id>/save-actions` - Сохранение действий
- `POST /api/migrate-actions` - Миграция действий
- `POST /api/reload-exceptions` - Перезагрузка исключений

## Алгоритмы и логика

### 1. Парсинг различий (a_log поля)

Система анализирует поле `a_log` содержащее различия в формате:
```
property_name
source = value1
target = value2
```

#### Алгоритм парсинга:

1. Разбиение `a_log` на строки
2. Поиск строк с `source =` и `target =`
3. Определение названия свойства (строка перед `source =`)
4. Извлечение значений source и target
5. Создание структуры различий

```sql
WITH log_lines AS (
    SELECT unnest(string_to_array(a_log, E'\n')) as log_line,
           generate_series(1, array_length(string_to_array(a_log, E'\n'), 1)) as line_number
    FROM table_source 
),
source_lines AS (
    SELECT * FROM log_lines WHERE log_line ~ 'source[[:space:]]*='
),
-- ... дальнейший парсинг
```

### 2. Система исключений

Исключения определяют как обрабатывать конкретные различия:

- **entity_type**: тип сущности (class/group/attribute)  
- **entity_name**: имя свойства для поиска
- **property_name**: описательное имя свойства
- **action**: действие (0=игнорировать, 2=обновить)

#### Алгоритм применения исключений:

1. Для каждого различия ищется исключение по ключу `entity_type:entity_name`
2. Если не найдено, ищется по `entity_type:property_name`
3. Применяется найденное действие или по умолчанию (0)

### 3. Анализ исключений для атрибутов

Для атрибутов система анализирует все различия в `a_log` и определяет общее действие:

```python
def _get_overall_exception_action(exception_actions):
    # Если есть хотя бы одно действие "Обновить" (2), то общее - "Обновить"
    for action_data in exception_actions:
        if action_data.get('exception_action', 0) == 2:
            return 2
    # Иначе - игнорировать
    return 0
```

### 4. Групповая обработка атрибутов

В режиме анализа исключений (`analyze_exceptions=true`) атрибуты группируются по классам и действиям:

- **ignore_list**: атрибуты с общим действием = 0
- **update_list**: атрибуты с общим действием = 2  
- **no_action_list**: атрибуты без различий

## API Reference

### Фильтры запросов

Все основные методы поддерживают фильтрацию:

- `page`: номер страницы (по умолчанию 1)
- `per_page`: записей на странице (по умолчанию 20)
- `search`: текстовый поиск по названию/описанию
- `status_variance`: фильтр по статусу различий (2=есть различия)
- `event`: фильтр по событию/действию  
- `a_priznak`: фильтр по признаку миграции
- `base_url`: URL админки назначения
- `source_base_url`: URL админки источника

### Дополнительные фильтры для атрибутов

- `exception_action_filter`: фильтр по действию исключения (0/-1/2)
- `analyze_exceptions`: включить анализ исключений (true/false)

### Структура ответов API

#### Список классов/групп/атрибутов:

```json
{
  "classes": [...],
  "total_count": 1500,
  "total_pages": 75,
  "current_page": 1,
  "per_page": 20,
  "has_prev": false,
  "has_next": true
}
```

#### Атрибуты с анализом исключений:

```json
{
  "classes": {
    "ClassName": {
      "class_name": "ClassName",
      "attributes": {
        "ignore_list": [...],
        "update_list": [...],
        "no_action_list": [...]
      },
      "statistics": {
        "ignore_count": 10,
        "update_count": 5,
        "no_action_count": 20
      }
    }
  },
  "statistics": {
    "ignore_count": 100,
    "update_count": 50, 
    "no_action_count": 200
  }
}
```

#### Детали класса:

```json
{
  "class": {...},
  "groups": [...],
  "attributes": [...],
  "differences": [...],
  "group_differences": [...],
  "attribute_differences": [...],
  "statistics": {
    "groups_count": 10,
    "attributes_count": 50,
    "differences_count": 5
  }
}
```

## Использование Docker

### Запуск через Docker Compose:

```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production  
docker-compose -f docker-compose.prod.yml up
```

### Конфигурация Nginx (nginx.conf):

```nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://app:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Файлы исключений

Система загружает исключения из Markdown файлов:

- `исключения классо.md` - исключения для классов
- `исключения групп.md` - исключения для групп атрибутов
- `исключение атрибутов.md` - исключения для атрибутов

### Формат файла исключений:

```
attr_title	attr_name	attr_map
Описание	description	DESCRIPTION
Название	title	TITLE
Только для чтения	readOnly	READ_ONLY
```

- **attr_title**: описательное название (используется как property_name)
- **attr_name**: кодовое имя (используется как entity_name)
- **attr_map**: поле таблицы (используется для справки)

## SQL отчеты

Готовые SQL запросы для анализа:

- `отчёт по классам.sql` - детальный анализ различий классов
- `отчёт по группам.sql` - анализ различий групп атрибутов  
- `отчёт по атрибутам.sql` - анализ различий атрибутов
- `структура классов.sql` - структурный анализ классов

## Обработка ошибок

### Типы ошибок:

1. **Подключение к БД**: автоматическая инициализация JVM и повторные попытки
2. **Таймауты запросов**: настраиваются через конфигурацию
3. **Ошибки парсинга**: логирование и возврат пустых результатов
4. **Отсутствие данных**: корректная обработка пустых результатов

### Логирование:

```python
# Уровни логирования настраиваются в config.py
logging_config = LoggingConfig(
    level="INFO",
    max_size=10485760,  # 10MB
    backup_count=5
)
```

## Производительность

### Оптимизация запросов:

- Пагинация результатов
- Индексы на часто используемые поля
- Кэширование исключений в памяти
- Пакетная обработка обновлений

### Настройки JVM:

```python
jvm_args = [
    "-Xmx1024m",  # Максимальная память
    "-Xms256m",   # Начальная память
    "-XX:+UseG1GC",  # G1 сборщик мусора
    "-XX:MaxGCPauseMillis=200"
]
```

## Безопасность

### Меры безопасности:

- Экранирование SQL параметров
- Prepared statements для пользовательского ввода
- Валидация входных данных
- Таймауты соединений
- Логирование операций

## Мониторинг и диагностика

### Доступные утилиты:

- `diagnostic.py` - диагностика подключений
- `java_diagnostic.py` - проверка Java окружения
- `liberica_diagnostic.py` - диагностика Liberica JDK

### Проверка состояния:

```bash
python diagnostic.py  # Общая диагностика
python java_diagnostic.py  # Проверка Java
```

## Разработка и развертывание

### Локальная разработка:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактировать .env

# Запуск приложения
python app.py
```

### Структура development workflow:

1. Изменение кода
2. Тестирование локально
3. Обновление документации
4. Commit в git
5. Deploy через Docker Compose

## Troubleshooting

### Частые проблемы:

**JVM не запускается:**
- Проверить JAVA_HOME
- Убедиться что JDBC драйверы существуют
- Проверить права доступа к файлам

**Ошибки подключения к БД:**
- Проверить сетевую доступность
- Валидировать credentials
- Проверить таймауты

**Медленные запросы:**
- Увеличить таймауты в конфигурации
- Проверить индексы в БД
- Оптимизировать размер страниц

**Ошибки памяти:**
- Увеличить heap size JVM
- Уменьшить размер страниц
- Включить оптимизацию GC

## Roadmap

### Планы развития:

1. **v2.0**: Добавление REST API для внешних интеграций
2. **v2.1**: Система уведомлений о статусе миграции  
3. **v2.2**: Расширенная аналитика и дашборды
4. **v2.3**: Автоматизация применения исключений
5. **v3.0**: Микросервисная архитектура 