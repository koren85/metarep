# SiTex Анализ Классов

Веб-приложение для анализа классов, групп атрибутов и атрибутов системы SiTex с интерактивными отчетами.

## Возможности

- **Список классов** с фильтрацией и поиском
- **Детальная информация** о каждом классе
- **Группы атрибутов** и **атрибуты** для каждого класса
- **Парсинг различий** между source и target значениями
- **Ссылки в админку** для каждого объекта
- **Показ/скрытие технических полей**
- **Пагинация** и **статистика**

## Установка

### 1. Зависимости

```bash
# Установка Python зависимостей
pip install -r requirements.txt

# Убедитесь, что JDBC драйверы находятся в папке lib/
ls lib/
# Должны быть файлы:
# - postgresql.jar
# - mssql-jdbc.jar
```

### 2. Настройка окружения

Создайте файл `.env` в корне проекта:

```bash
# PostgreSQL подключение
POSTGRES_HOST=10.3.0.254
POSTGRES_PORT=22618
POSTGRES_DB=sdu_postgres_migration_20250404
POSTGRES_USER=tomcat
POSTGRES_PASSWORD=password

# Базовый URL для админки SiTex
SITEX_CONTEXT_URL=http://10.3.0.254:22617/test_voron_124724_migration_0001/#HlBsGLFzd2v9vJsX

# Пути к JDBC драйверам
POSTGRES_DRIVER_PATH=./lib/postgresql.jar
MSSQL_DRIVER_PATH=./lib/mssql-jdbc.jar

# Настройки логирования
LOG_LEVEL=INFO
DEBUG_MODE=false

# Настройки приложения
CREATE_BACKUPS=true
DEFAULT_ENCODING=utf-8
```

### 3. Установка Java

Приложение требует Java 8+ для работы с JDBC драйверами.

**macOS:**
```bash
# Через Homebrew
brew install openjdk

# Или Java 8
brew install openjdk@8
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install openjdk-8-jdk

# CentOS/RHEL
sudo yum install java-1.8.0-openjdk-devel
```

## Запуск

```bash
python app.py
```

Приложение будет доступно по адресу: http://localhost:5000

## Структура проекта

```
metarep/
├── app.py                 # Основное Flask приложение
├── data_service.py        # Сервис для работы с данными
├── config.py             # Конфигурация приложения
├── database_manager.py   # Менеджеры БД через JDBC
├── requirements.txt      # Python зависимости
├── .env                  # Настройки окружения
├── templates/            # HTML шаблоны
│   ├── base.html
│   ├── index.html
│   ├── class_detail.html
│   └── error.html
└── lib/                  # JDBC драйверы
    ├── postgresql.jar
    └── mssql-jdbc.jar
```

## Использование

### Главная страница

- **Список классов** с возможностью фильтрации по `A_STATUS_VARIANCE` и `A_EVENT`
- **Поиск** по имени и описанию класса
- **Пагинация** для больших объемов данных
- **Статистика** - общее количество классов, с различиями и т.д.

### Детальная страница класса

- **Информация о классе** со всеми полями из `SXCLASS_SOURCE`
- **Группы атрибутов** из `SXATTR_GRP_SOURCE`
- **Атрибуты** из `SXATTR_SOURCE`
- **Различия** (парсинг из поля `A_LOG`)
- **Ссылки в админку** для каждого объекта

### Особенности

- **Технические поля** скрыты по умолчанию (кнопка "Показать технические поля")
- **Клик по значениям** копирует их в буфер обмена
- **Цветовая индикация** различий (добавлено/удалено/изменено)
- **Адаптивный дизайн** с Bootstrap

## Ссылки в админку

Приложение автоматически генерирует ссылки для перехода в админку:

- **Класс**: `{базовый_url}/admin/edit.htm?id={ouid}@SXClass`
- **Группа атрибутов**: `{базовый_url}/admin/edit.htm?id={ouid}@SXAttrGrp`
- **Атрибут**: `{базовый_url}/admin/edit.htm?id={ouid}@SXAttr`

## API Endpoints

- `GET /` - Главная страница
- `GET /class/<int:class_ouid>` - Детали класса
- `GET /api/classes` - JSON API списка классов
- `GET /api/class/<int:class_ouid>` - JSON API деталей класса
- `GET /api/statistics` - JSON API статистики

## Фильтры

- **A_STATUS_VARIANCE**: 0, 1, 2 (по умолчанию показывать все)
- **A_EVENT**: 0, 1, 2, 3, 4 (по умолчанию показывать все)
- **Поиск**: по имени и описанию класса
- **Записей на странице**: 10, 20, 50, 100

## Парсинг различий

Используется SQL запрос из `отчёт по классам.sql` для парсинга различий из поля `A_LOG` классов с `A_STATUS_VARIANCE = 2` и `A_EVENT = 4`.

## Технические требования

- Python 3.7+
- Java 8+
- PostgreSQL JDBC драйвер
- Flask 2.3+
- jpype1 для работы с Java из Python

## Безопасность

- Открытый доступ (без аутентификации)
- Предназначено для использования в локальной сети
- Экранирование SQL-запросов для предотвращения инъекций

## Поддержка

Для вопросов и проблем обращайтесь к разработчику системы миграции MSSQL → PostgreSQL. 