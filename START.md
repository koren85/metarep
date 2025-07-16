# Быстрый запуск SiTex Анализ Классов

## 0. Установка Python и pip (macOS)

Если у вас ошибка `bash: pip: command not found`, сначала установите Python:

### Вариант 1: Через Homebrew (рекомендуется)
```bash
# Установите Homebrew если его нет
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установите Python
brew install python

# Проверьте установку
python3 --version
pip3 --version
```

### Вариант 2: Через официальный сайт
1. Скачайте Python с https://www.python.org/downloads/
2. Установите .pkg файл
3. Перезапустите терминал

### Вариант 3: Если есть Python, но нет pip
```bash
# Установите pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py

# Или через ensurepip
python3 -m ensurepip --upgrade
```

### Создание виртуального окружения (рекомендуется)
```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# Теперь можно использовать pip (без pip3)
pip --version
```

## 1. Создайте файл .env

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

## 2. Установите зависимости

```bash
# Если использовали виртуальное окружение:
pip install -r requirements.txt

# Если НЕ использовали виртуальное окружение:
pip3 install -r requirements.txt
```

## 3. Убедитесь, что JDBC драйверы на месте

```bash
ls lib/
# Должны быть файлы:
# - postgresql.jar
# - mssql-jdbc.jar
```

## 4. Запустите приложение

```bash
# Если использовали виртуальное окружение:
python app.py

# Если НЕ использовали виртуальное окружение:
python3 app.py
```

## 5. Откройте в браузере

```
http://localhost:5000
```

## Возможные проблемы

### ❌ Первая помощь - запустите диагностику
```bash
python java_diagnostic.py
```
Эта утилита покажет все проблемы с Java и предложит решения.

### Python/pip не найден
```bash
# macOS - установите Homebrew и Python
brew install python

# Проверьте версию
python3 --version
pip3 --version
```

### Java не найдена
```bash
# macOS
brew install openjdk

# Linux
sudo apt-get install openjdk-8-jdk
```

### Ошибка JVM (как в вашем случае)
```bash
# 1. Проверьте установленную Java
java -version

# 2. Найдите все установки Java (macOS)
ls /Library/Java/JavaVirtualMachines/

# 3. Установите JAVA_HOME вручную
export JAVA_HOME=/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home

# 4. Проверьте, что путь существует
ls $JAVA_HOME

# 5. Попробуйте запустить приложение снова
python app.py
```

### Не удается подключиться к БД
- Проверьте настройки в .env
- Убедитесь, что PostgreSQL доступен
- Проверьте правильность пути к JDBC драйверу

### Если ничего не помогает
```bash
# 1. Переустановите Java через Homebrew
brew uninstall --ignore-dependencies openjdk
brew install openjdk

# 2. Установите JAVA_HOME в профиле
echo 'export JAVA_HOME="$(brew --prefix openjdk)"' >> ~/.zshrc
source ~/.zshrc

# 3. Переустановите jpype
pip uninstall jpype1
pip install jpype1

# 4. Попробуйте снова
python app.py
```

## Функционал

- ✅ **Список классов** с фильтрацией и поиском
- ✅ **Детальная информация** о каждом классе
- ✅ **Группы атрибутов** и **атрибуты**
- ✅ **Парсинг различий** между source и target
- ✅ **Ссылки в админку** для каждого объекта
- ✅ **Показ/скрытие технических полей**
- ✅ **Пагинация** и **статистика**

---

**Готово! Приложение должно работать.** 

Если возникают проблемы, смотрите подробную документацию в README.md 