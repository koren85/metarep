# MetaRep Docker Makefile

.PHONY: help build dev prod stop clean logs shell test

# Цвета для вывода
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Показать это сообщение помощи
	@echo "${GREEN}MetaRep Docker Commands${NC}"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "${YELLOW}%-15s${NC} %s\n", $$1, $$2}'

build: ## Собрать Docker образ
	@echo "${GREEN}Сборка Docker образа...${NC}"
	docker-compose build

dev: ## Запустить в режиме разработки
	@echo "${GREEN}Запуск в режиме разработки...${NC}"
	docker-compose -f docker-compose.dev.yml up --build

dev-d: ## Запустить в режиме разработки в фоне
	@echo "${GREEN}Запуск в режиме разработки (фон)...${NC}"
	docker-compose -f docker-compose.dev.yml up --build -d

prod: ## Запустить в продакшене
	@echo "${GREEN}Запуск в продакшене...${NC}"
	docker-compose up --build -d

prod-nginx: ## Запустить в продакшене с Nginx
	@echo "${GREEN}Запуск в продакшене с Nginx...${NC}"
	docker-compose -f docker-compose.prod.yml up --build -d

stop: ## Остановить все контейнеры
	@echo "${YELLOW}Остановка контейнеров...${NC}"
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

stop-dev: ## Остановить dev контейнеры
	@echo "${YELLOW}Остановка dev контейнеров...${NC}"
	docker-compose -f docker-compose.dev.yml down

stop-prod: ## Остановить prod контейнеры
	@echo "${YELLOW}Остановка prod контейнеров...${NC}"
	docker-compose down

stop-nginx: ## Остановить nginx prod контейнеры
	@echo "${YELLOW}Остановка nginx prod контейнеров...${NC}"
	docker-compose -f docker-compose.prod.yml down

clean: ## Очистить контейнеры и volumes
	@echo "${RED}Очистка контейнеров и volumes...${NC}"
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f

logs: ## Показать логи
	docker-compose logs -f

logs-dev: ## Показать логи dev
	docker-compose -f docker-compose.dev.yml logs -f

logs-nginx: ## Показать логи nginx prod
	docker-compose -f docker-compose.prod.yml logs -f

shell: ## Подключиться к контейнеру
	docker-compose exec metarep bash

shell-dev: ## Подключиться к dev контейнеру
	docker-compose -f docker-compose.dev.yml exec metarep-dev bash

ps: ## Показать статус контейнеров
	@echo "${GREEN}Статус контейнеров:${NC}"
	docker-compose ps
	@echo ""
	@echo "${GREEN}Dev контейнеры:${NC}"
	docker-compose -f docker-compose.dev.yml ps

restart: ## Перезапустить контейнеры
	@echo "${YELLOW}Перезапуск...${NC}"
	docker-compose restart

restart-dev: ## Перезапустить dev контейнеры
	@echo "${YELLOW}Перезапуск dev...${NC}"
	docker-compose -f docker-compose.dev.yml restart

setup: ## Начальная настройка проекта
	@echo "${GREEN}Настройка проекта...${NC}"
	@if [ ! -f .env ]; then \
		echo "${YELLOW}Копирование .env.example в .env...${NC}"; \
		cp .env.example .env; \
		echo "${RED}ВАЖНО: Отредактируй .env файл с твоими настройками БД!${NC}"; \
	else \
		echo "${GREEN}.env файл уже существует${NC}"; \
	fi
	@echo "${GREEN}Создание директорий...${NC}"
	@mkdir -p logs migration_output

test-java: ## Проверить Java в контейнере
	@echo "${GREEN}Проверка Java...${NC}"
	docker-compose exec metarep java -version

test-python: ## Проверить Python в контейнере
	@echo "${GREEN}Проверка Python и пакетов...${NC}"
	docker-compose exec metarep python --version
	docker-compose exec metarep pip list

test-jdbc: ## Проверить JDBC драйверы
	@echo "${GREEN}Проверка JDBC драйверов...${NC}"
	docker-compose exec metarep ls -la /app/lib/

# Развертывание без кэша
rebuild: ## Пересобрать образы без кэша
	@echo "${GREEN}Пересборка без кэша...${NC}"
	docker-compose build --no-cache

rebuild-dev: ## Пересобрать dev без кэша
	@echo "${GREEN}Пересборка dev без кэша...${NC}"
	docker-compose -f docker-compose.dev.yml build --no-cache 