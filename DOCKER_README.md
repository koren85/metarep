# Docker развертывание MetaRep

## Быстрый старт

### Настройка переменных окружения

1. Скопируй пример файла переменных окружения:
```bash
cp .env.example .env
```

2. Отредактируй `.env` файл с твоими настройками БД:
```bash
# Основные настройки
MSSQL_HOST=your_mssql_server
MSSQL_DB=your_database
MSSQL_USER=your_username
MSSQL_PASSWORD=your_password

POSTGRES_HOST=your_postgres_server
POSTGRES_DB=your_postgres_database
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
```

### Разработка

Для разработки с горячей перезагрузкой:

```bash
# Запуск в режиме разработки
docker-compose -f docker-compose.dev.yml up --build

# Или в фоне
docker-compose -f docker-compose.dev.yml up -d --build
```

Приложение будет доступно по адресу: http://localhost:5000

В режиме разработки:
- Включена горячая перезагрузка
- Включен debug режим Flask
- Файлы проекта монтируются как volume для live-редактирования

### Продакшен

Для развертывания в продакшене есть два варианта:

#### Простой продакшен
```bash
# Запуск в продакшене
docker-compose up --build -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

#### Продакшен с Nginx (рекомендуется)
```bash
# Запуск с Nginx reverse proxy
docker-compose -f docker-compose.prod.yml up --build -d

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f
```

Версия с Nginx включает:
- Reverse proxy для лучшей производительности
- Сжатие gzip
- Настройки для статических файлов
- Готовность к SSL (раскомментируй в nginx.conf)
- Load balancing возможности

## Управление контейнерами

### Основные команды

```bash
# Пересборка образа
docker-compose build

# Запуск с пересборкой
docker-compose up --build

# Остановка
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Просмотр логов
docker-compose logs -f metarep
```

### Отладка

```bash
# Подключение к контейнеру
docker-compose exec metarep bash

# Проверка Java
docker-compose exec metarep java -version

# Проверка Python пакетов
docker-compose exec metarep pip list
```

## Структура файлов

- `Dockerfile` - основной образ с Java + Python
- `docker-compose.yml` - конфигурация для продакшена
- `docker-compose.dev.yml` - конфигурация для разработки
- `.env` - переменные окружения (не в git)
- `.env.example` - пример переменных окружения
- `.dockerignore` - исключения для Docker build

## Переменные окружения

### Flask настройки
- `FLASK_ENV` - режим Flask (development/production)
- `FLASK_DEBUG` - включение debug режима
- `PORT` - порт приложения (по умолчанию 5000)

### Java настройки
- `JAVA_HOME` - путь к Java (автоматически в контейнере)

### База данных
- `MSSQL_HOST`, `MSSQL_PORT`, `MSSQL_DB`, `MSSQL_USER`, `MSSQL_PASSWORD` - настройки MSSQL
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - настройки PostgreSQL

Полный список переменных смотри в `.env.example`

## Health Check

В продакшене включен health check:
- Проверка каждые 30 секунд
- Timeout 10 секунд
- 3 попытки
- Старт проверок через 40 секунд после запуска

## Логи и данные

Следующие директории монтируются как volumes:
- `./logs` - логи приложения
- `./migration_output` - выходные файлы миграции

## Troubleshooting

### Проблемы с Java
```bash
# Проверь JAVA_HOME в контейнере
docker-compose exec metarep echo $JAVA_HOME
docker-compose exec metarep java -version
```

### Проблемы с JDBC
```bash
# Проверь наличие драйверов
docker-compose exec metarep ls -la /app/lib/
```

### Проблемы с подключением к БД
```bash
# Проверь сетевое подключение
docker-compose exec metarep ping your_database_host
``` 