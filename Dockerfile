# Используем базовый образ с OpenJDK 17 и Python 3.11
FROM openjdk:17-jdk-slim

# Устанавливаем Python и необходимые пакеты
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем символическую ссылку для python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем JDBC драйверы
COPY lib/ ./lib/

# Копируем остальные файлы приложения
COPY . .

# Устанавливаем переменную JAVA_HOME
ENV JAVA_HOME=/usr/local/openjdk-17

# Экспонируем порт
EXPOSE 5000

# Команда для запуска приложения
CMD ["python", "app.py"] 