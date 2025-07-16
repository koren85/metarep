# Установка и настройка Liberica JDK 17 для JDBC в Python проектах

## 1. Установка Liberica JDK 17

### macOS

#### Вариант 1: Через Homebrew
```bash
# Добавляем tap для Liberica
brew tap bell-sw/liberica

# Устанавливаем Liberica JDK 17
brew install --cask liberica-jdk17
```

#### Вариант 2: Ручная установка
1. Скачать с [официального сайта](https://bell-sw.com/pages/downloads/)
2. Выбрать `Java 17 LTS` → `macOS` → `ARM64` или `x86_64`
3. Скачать `.pkg` файл и установить

### Linux (Ubuntu/Debian)
```bash
# Добавляем репозиторий
wget -q -O - https://download.bell-sw.com/pki/GPG-KEY-bellsoft | sudo apt-key add -
echo "deb [arch=amd64] https://apt.bell-sw.com/ stable main" | sudo tee /etc/apt/sources.list.d/bellsoft.list

# Обновляем пакеты и устанавливаем
sudo apt update
sudo apt install liberica-jdk17
```

### Windows
1. Скачать с [официального сайта](https://bell-sw.com/pages/downloads/)
2. Выбрать `Java 17 LTS` → `Windows` → `x86_64`
3. Скачать `.msi` файл и установить

## 2. Проверка установки

```bash
# Проверяем установку
java -version
javac -version

# Находим JAVA_HOME
java -XshowSettings:properties -version 2>&1 | grep java.home
```

Ожидаемый вывод:
```
openjdk version "17.0.15" 2025-04-15 LTS
OpenJDK Runtime Environment (build 17.0.15+10-LTS)
OpenJDK 64-Bit Server VM (build 17.0.15+10-LTS, mixed mode, sharing)
```

## 3. Настройка окружения

### Определение путей для разных ОС

#### macOS
```bash
# Автоматически установленная через Homebrew
JAVA_HOME="/opt/homebrew/lib/liberica-jdk17"

# Вручную установленная
JAVA_HOME="/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home"
```

#### Linux
```bash
JAVA_HOME="/usr/lib/jvm/liberica-jdk17"
```

#### Windows
```cmd
set JAVA_HOME=C:\Program Files\BellSoft\LibericaJDK-17
```

### Переменные окружения

#### Для проекта (.env файл)
```env
# Java настройки
JAVA_HOME=/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home

# Пути к JDBC драйверам
POSTGRES_DRIVER_PATH=./lib/postgresql.jar
MSSQL_DRIVER_PATH=./lib/mssql-jdbc.jar
```

#### Системные переменные (опционально)
```bash
# В ~/.bashrc или ~/.zshrc
export JAVA_HOME="/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
```

## 4. Установка и настройка JPype

### Требования
```bash
# Устанавливаем последнюю версию JPype
pip install JPype1>=1.4.0

# Проверяем совместимость
python -c "import jpype; print(jpype.__version__)"
```

### Настройка JPype для Liberica JDK

#### Базовая настройка
```python
import jpype
import os
from pathlib import Path

def setup_liberica_jvm():
    """Настройка JVM для Liberica JDK 17"""
    
    # Проверяем, запущена ли JVM
    if jpype.isJVMStarted():
        return True
    
    try:
        # Автоматический поиск JVM
        jvm_path = jpype.getDefaultJVMPath()
        print(f"Найденный путь JVM: {jvm_path}")
        
        # Запуск JVM
        jpype.startJVM(jvm_path)
        print("JVM запущена успешно")
        
        # Проверка версии Java
        java_version = jpype.java.lang.System.getProperty("java.version")
        print(f"Версия Java: {java_version}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка запуска JVM: {e}")
        return False

# Использование
if setup_liberica_jvm():
    print("JVM готова к работе")
```

#### Расширенная настройка с JDBC
```python
import jpype
import jpype.imports
import os
from pathlib import Path

class LibericaJDBCManager:
    """Менеджер для работы с JDBC через Liberica JDK 17"""
    
    def __init__(self, driver_paths: list):
        """
        driver_paths: список путей к JDBC драйверам
        """
        self.driver_paths = driver_paths
        self.connection = None
        
    def initialize_jvm(self):
        """Инициализация JVM с драйверами"""
        if jpype.isJVMStarted():
            return True
            
        try:
            # Проверяем существование драйверов
            for driver_path in self.driver_paths:
                if not Path(driver_path).exists():
                    raise FileNotFoundError(f"Драйвер не найден: {driver_path}")
            
            # Создаем classpath
            classpath = os.pathsep.join(self.driver_paths)
            
            # Автоматический поиск JVM
            jvm_path = jpype.getDefaultJVMPath()
            print(f"JVM path: {jvm_path}")
            
            # Запуск JVM с classpath
            jpype.startJVM(
                jvm_path,
                f"-Djava.class.path={classpath}",
                "-Xmx1024m",  # Максимум памяти
                "-Xms256m"    # Начальная память
            )
            
            print("JVM инициализирована успешно")
            return True
            
        except Exception as e:
            print(f"Ошибка инициализации JVM: {e}")
            return False
    
    def connect_postgresql(self, host, port, database, username, password):
        """Подключение к PostgreSQL"""
        if not self.initialize_jvm():
            return False
            
        try:
            from java.sql import DriverManager
            
            jdbc_url = f"jdbc:postgresql://{host}:{port}/{database}"
            self.connection = DriverManager.getConnection(
                jdbc_url, username, password
            )
            print("Подключение к PostgreSQL установлено")
            return True
            
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            return False
    
    def connect_mssql(self, host, port, database, username, password):
        """Подключение к MS SQL Server"""
        if not self.initialize_jvm():
            return False
            
        try:
            from java.sql import DriverManager
            
            jdbc_url = f"jdbc:sqlserver://{host}:{port};databaseName={database};trustServerCertificate=true"
            self.connection = DriverManager.getConnection(
                jdbc_url, username, password
            )
            print("Подключение к MS SQL Server установлено")
            return True
            
        except Exception as e:
            print(f"Ошибка подключения к MS SQL Server: {e}")
            return False
    
    def execute_query(self, query):
        """Выполнение SELECT запроса"""
        if not self.connection:
            raise Exception("Нет подключения к БД")
            
        try:
            statement = self.connection.createStatement()
            result_set = statement.executeQuery(query)
            
            # Получаем метаданные
            metadata = result_set.getMetaData()
            column_count = metadata.getColumnCount()
            
            # Собираем результаты
            results = []
            while result_set.next():
                row = []
                for i in range(1, column_count + 1):
                    value = result_set.getObject(i)
                    row.append(str(value) if value is not None else None)
                results.append(tuple(row))
            
            statement.close()
            return results
            
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            raise
    
    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
            print("Соединение закрыто")
```

## 5. Примеры использования

### Пример 1: Простое подключение
```python
from liberica_jdbc import LibericaJDBCManager

# Создаем менеджер
jdbc_manager = LibericaJDBCManager([
    "./lib/postgresql.jar",
    "./lib/mssql-jdbc.jar"
])

# Подключаемся к PostgreSQL
if jdbc_manager.connect_postgresql(
    host="localhost",
    port=5432,
    database="mydb",
    username="user",
    password="password"
):
    # Выполняем запрос
    results = jdbc_manager.execute_query("SELECT * FROM users LIMIT 10")
    for row in results:
        print(row)
    
    # Закрываем соединение
    jdbc_manager.close()
```

### Пример 2: Конфигурация через .env
```python
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Создаем менеджер с конфигурацией
jdbc_manager = LibericaJDBCManager([
    os.getenv('POSTGRES_DRIVER_PATH', './lib/postgresql.jar'),
    os.getenv('MSSQL_DRIVER_PATH', './lib/mssql-jdbc.jar')
])

# Подключение с параметрами из .env
if jdbc_manager.connect_postgresql(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=int(os.getenv('POSTGRES_PORT', '5432')),
    database=os.getenv('POSTGRES_DB', 'mydb'),
    username=os.getenv('POSTGRES_USER', 'user'),
    password=os.getenv('POSTGRES_PASSWORD', 'password')
):
    print("Подключение успешно")
```

## 6. Диагностика проблем

### Проверка установки Liberica JDK
```python
import jpype
import subprocess

def diagnose_liberica_jdk():
    """Диагностика установки Liberica JDK"""
    
    print("=== Диагностика Liberica JDK ===")
    
    # 1. Проверка java команды
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True)
        print(f"Java version output:\n{result.stderr}")
    except Exception as e:
        print(f"Ошибка выполнения java -version: {e}")
    
    # 2. Проверка JAVA_HOME
    java_home = os.environ.get('JAVA_HOME')
    print(f"JAVA_HOME: {java_home}")
    
    # 3. Проверка автоматического поиска JVM
    try:
        jvm_path = jpype.getDefaultJVMPath()
        print(f"Автоматически найденный JVM путь: {jvm_path}")
        
        # Проверка существования файла
        if os.path.exists(jvm_path):
            print("✅ JVM библиотека найдена")
        else:
            print("❌ JVM библиотека НЕ найдена")
            
    except Exception as e:
        print(f"Ошибка поиска JVM: {e}")
    
    # 4. Попытка запуска JVM
    try:
        if not jpype.isJVMStarted():
            jpype.startJVM(jpype.getDefaultJVMPath())
            print("✅ JVM запущена успешно")
            
            # Проверка версии Java
            java_version = jpype.java.lang.System.getProperty("java.version")
            vendor = jpype.java.lang.System.getProperty("java.vendor")
            print(f"Java версия: {java_version}")
            print(f"Поставщик: {vendor}")
            
            jpype.shutdownJVM()
        else:
            print("JVM уже запущена")
            
    except Exception as e:
        print(f"❌ Ошибка запуска JVM: {e}")

# Запуск диагностики
diagnose_liberica_jdk()
```

### Частые проблемы и решения

#### 1. JVM DLL not found
```bash
# Проверить правильность пути
find /Library/Java/JavaVirtualMachines -name "libjli.dylib"

# Установить правильный JAVA_HOME
export JAVA_HOME=/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home
```

#### 2. Ошибка SIGBUS на ARM64 Mac
```python
# Использовать автоматический поиск JVM вместо ручного указания пути
jvm_path = jpype.getDefaultJVMPath()
jpype.startJVM(jvm_path)
```

#### 3. Проблемы с кодировкой
```python
# Добавить параметры JVM для UTF-8
jpype.startJVM(
    jvm_path,
    f"-Djava.class.path={classpath}",
    "-Dfile.encoding=UTF-8",
    "-Dconsole.encoding=UTF-8"
)
```

## 7. Рекомендации по производительности

### Настройки памяти JVM
```python
jpype.startJVM(
    jvm_path,
    f"-Djava.class.path={classpath}",
    "-Xmx2048m",      # Максимум 2GB
    "-Xms512m",       # Начальная 512MB
    "-XX:+UseG1GC"    # Использовать G1 сборщик мусора
)
```

### Пул соединений
```python
class ConnectionPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.connections = []
        self.available = []
    
    def get_connection(self):
        if self.available:
            return self.available.pop()
        elif len(self.connections) < self.max_connections:
            conn = self.create_connection()
            self.connections.append(conn)
            return conn
        else:
            raise Exception("Нет доступных соединений")
    
    def return_connection(self, conn):
        self.available.append(conn)
```

## 8. Примеры для разных фреймворков

### Flask
```python
from flask import Flask
from liberica_jdbc import LibericaJDBCManager

app = Flask(__name__)

# Глобальный менеджер JDBC
jdbc_manager = LibericaJDBCManager([
    "./lib/postgresql.jar"
])

@app.before_first_request
def setup_database():
    jdbc_manager.connect_postgresql(
        host="localhost",
        port=5432,
        database="mydb",
        username="user",
        password="password"
    )

@app.route('/users')
def get_users():
    results = jdbc_manager.execute_query("SELECT * FROM users")
    return {'users': [dict(zip(['id', 'name'], row)) for row in results]}

if __name__ == '__main__':
    app.run(debug=True)
```

### Django
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Дополнительно для JDBC
LIBERICA_JDBC_SETTINGS = {
    'drivers': ['./lib/postgresql.jar'],
    'java_home': '/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home'
}
```

## 9. Тестирование

### Модульные тесты
```python
import unittest
from liberica_jdbc import LibericaJDBCManager

class TestLibericaJDBC(unittest.TestCase):
    
    def setUp(self):
        self.jdbc_manager = LibericaJDBCManager([
            "./lib/postgresql.jar"
        ])
    
    def test_jvm_initialization(self):
        self.assertTrue(self.jdbc_manager.initialize_jvm())
    
    def test_postgresql_connection(self):
        self.assertTrue(self.jdbc_manager.connect_postgresql(
            host="localhost",
            port=5432,
            database="testdb",
            username="test",
            password="test"
        ))
    
    def tearDown(self):
        self.jdbc_manager.close()

if __name__ == '__main__':
    unittest.main()
```

## 10. Деплой и продакшн

### Docker
```dockerfile
FROM bellsoft/liberica-openjdk-alpine:17

# Устанавливаем Python
RUN apk add --no-cache python3 py3-pip

# Копируем приложение
COPY . /app
WORKDIR /app

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Устанавливаем переменные окружения
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=$JAVA_HOME/bin:$PATH

CMD ["python", "app.py"]
```

### Systemd сервис
```ini
[Unit]
Description=Python JDBC App with Liberica JDK
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
Environment=JAVA_HOME=/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home
ExecStart=/opt/myapp/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Заключение

Liberica JDK 17 обеспечивает стабильную работу с JDBC в Python проектах. Основные преимущества:

- ✅ Полная совместимость с OpenJDK
- ✅ Оптимизации для ARM64 архитектуры
- ✅ LTS поддержка до 2029 года
- ✅ Бесплатная коммерческая лицензия
- ✅ Лучшая производительность на macOS

Следуя этому руководству, вы сможете успешно интегрировать Liberica JDK 17 в любой Python проект, требующий JDBC подключения. 