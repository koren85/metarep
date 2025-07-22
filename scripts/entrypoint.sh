#!/bin/sh
set -e

echo "Запуск SSL контейнера..."

# Генерируем сертификаты при первом запуске
/usr/local/bin/generate-ssl.sh

# Запускаем cron в фоне
crond -f &
CRON_PID=$!

echo "SSL контейнер запущен. Cron PID: $CRON_PID"

# Функция для graceful shutdown
cleanup() {
    echo "Остановка SSL контейнера..."
    kill $CRON_PID 2>/dev/null || true
    wait $CRON_PID 2>/dev/null || true
    exit 0
}

# Обработчики сигналов
trap cleanup SIGTERM SIGINT

# Бесконечный цикл с проверкой каждые 24 часа
while true; do
    sleep 86400  # 24 часа
    if ! kill -0 $CRON_PID 2>/dev/null; then
        echo "Cron процесс упал, перезапускаем..."
        crond -f &
        CRON_PID=$!
    fi
done 