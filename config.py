"""
Конфигурация системы автоматизации миграции MSSQL → PostgreSQL
Все параметры загружаются из переменных окружения (.env файл)
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

def get_bool_env(key: str, default: bool = False) -> bool:
    """Получение boolean значения из переменной окружения"""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_int_env(key: str, default: int = 0) -> int:
    """Получение integer значения из переменной окружения"""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

@dataclass
class DatabaseConfig:
    """Конфигурация подключения к базе данных"""
    host: str
    port: int
    database: str
    username: str
    password: str
    driver_path: str
    jdbc_url_template: str
    connection_timeout: int = 30
    query_timeout: int = 300
    enable_ssl: bool = False
    verify_ssl: bool = False

@dataclass
class LoggingConfig:
    """Конфигурация логирования"""
    level: str = "INFO"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    encrypt_passwords: bool = True
    datetime_format: str = "%Y-%m-%d %H:%M:%S"

@dataclass  
class TaskGenerationConfig:
    """Конфигурация генерации задач"""
    task_name_prefix: str = "Миграция класса"
    folder_name_prefix: str = "04_Миграция" 
    project_name_template: str = "Migration_{context}_{date}"
    date_format: str = "%Y%m%d"

@dataclass
class ClassAnalysisConfig:
    """Конфигурация анализа классов"""
    table_prefix: str = "migration_classes"
    analyze_dependencies: bool = True
    check_rollback_support: bool = True
    task_id: str = "120682"

@dataclass
class PerformanceConfig:
    """Конфигурация производительности"""
    batch_size: int = 1000
    max_retries: int = 3
    max_db_connections: int = 5
    connection_pool_timeout: int = 60
    connection_pool_size: int = 3

@dataclass
class DirectoryConfig:
    """Конфигурация директорий"""
    output_dir: str = "migration_output"
    logs_dir: str = "logs"
    templates_dir: str = "templates"
    auto_create_dirs: bool = True

@dataclass
class MigrationConfig:
    """Основная конфигурация системы миграции"""
    # Подключения к БД
    mssql: DatabaseConfig
    postgres: DatabaseConfig
    
    # Пути и директории
    java_home: str
    export_script_path: str
    directories: DirectoryConfig
    
    # Настройки системы SITEX-ЭСРН
    sitex_context_url: str
    
    # Конфигурации подсистем
    logging: LoggingConfig
    task_generation: TaskGenerationConfig
    class_analysis: ClassAnalysisConfig
    performance: PerformanceConfig
    
    # Дополнительные настройки
    debug_mode: bool = False
    create_backups: bool = True
    default_encoding: str = "utf-8"
    
    @classmethod
    def from_env(cls) -> 'MigrationConfig':
        """Создание конфигурации из переменных окружения"""
        
        # Автоопределение JAVA_HOME для Mac если не задано
        java_home = os.getenv('JAVA_HOME')
        if not java_home:
            # Проверяем возможные пути к Java на macOS
            possible_paths = [
                '/opt/homebrew/opt/openjdk',  # M1/M2 Mac через Homebrew
                '/usr/local/opt/openjdk',     # Intel Mac через Homebrew
                '/opt/homebrew/opt/openjdk@8',  # Конкретная версия
                '/usr/local/opt/openjdk@8',
                '/opt/homebrew/opt/openjdk@11',
                '/usr/local/opt/openjdk@11',
                '/opt/homebrew/opt/openjdk@17',
                '/usr/local/opt/openjdk@17'
            ]
            
            # Проверяем системные пути к Java
            import glob
            system_java_paths = glob.glob('/Library/Java/JavaVirtualMachines/*/Contents/Home')
            possible_paths.extend(system_java_paths)
            
            # Также проверяем Linux пути
            possible_paths.extend([
                '/usr/lib/jvm/java-8-openjdk-amd64',  # Linux
                '/usr/lib/jvm/default-java'  # Default Linux
            ])
            
            # Найдем первый существующий путь
            java_home = None
            for path in possible_paths:
                if os.path.exists(path):
                    java_home = path
                    break
            
            if not java_home:
                java_home = '/usr/lib/jvm/default-java'  # Fallback
        
        # Конфигурация MSSQL
        mssql_config = DatabaseConfig(
            host=os.getenv('MSSQL_HOST', ''),
            port=get_int_env('MSSQL_PORT', 1433),
            database=os.getenv('MSSQL_DB', ''),
            username=os.getenv('MSSQL_USER', ''),
            password=os.getenv('MSSQL_PASSWORD', ''),
            driver_path=os.getenv('MSSQL_DRIVER_PATH', './lib/mssql-jdbc.jar'),
            jdbc_url_template='jdbc:sqlserver://{host}:{port};databaseName={database};trustServerCertificate=true;encrypt=false;characterEncoding=UTF-8;sendStringParametersAsUnicode=true;loginTimeout=60;socketTimeout=600',
            connection_timeout=get_int_env('DB_CONNECTION_TIMEOUT', 60),
            query_timeout=get_int_env('DB_QUERY_TIMEOUT', 600),
            enable_ssl=get_bool_env('ENABLE_SSL', False),
            verify_ssl=get_bool_env('VERIFY_SSL_CERTIFICATES', False)
        )
        
        # Конфигурация PostgreSQL
        postgres_config = DatabaseConfig(
            host=os.getenv('POSTGRES_HOST', '10.3.0.254'),
            port=get_int_env('POSTGRES_PORT', 22618),
            database=os.getenv('POSTGRES_DB', 'sdu_postgres_migration_20250404'),
            username=os.getenv('POSTGRES_USER', 'tomcat'),
            password=os.getenv('POSTGRES_PASSWORD', 'password'),
            driver_path=os.getenv('POSTGRES_DRIVER_PATH', './lib/postgresql.jar'),
            jdbc_url_template='jdbc:postgresql://{host}:{port}/{database}?connectTimeout=60&socketTimeout=600',
            connection_timeout=get_int_env('DB_CONNECTION_TIMEOUT', 60),
            query_timeout=get_int_env('DB_QUERY_TIMEOUT', 600),
            enable_ssl=get_bool_env('ENABLE_SSL', False),
            verify_ssl=get_bool_env('VERIFY_SSL_CERTIFICATES', False)
        )
        
        # Конфигурация логирования
        logging_config = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            max_size=get_int_env('LOG_MAX_SIZE', 10485760),
            backup_count=get_int_env('LOG_BACKUP_COUNT', 5),
            encrypt_passwords=get_bool_env('ENCRYPT_PASSWORDS_IN_LOGS', True),
            datetime_format=os.getenv('DATETIME_FORMAT', '%Y-%m-%d %H:%M:%S')
        )
        
        # Конфигурация генерации задач
        task_generation_config = TaskGenerationConfig(
            task_name_prefix=os.getenv('TASK_NAME_PREFIX', 'Миграция класса'),
            folder_name_prefix=os.getenv('FOLDER_NAME_PREFIX', '04_Миграция'),
            project_name_template=os.getenv('PROJECT_NAME_TEMPLATE', 'Migration_{context}_{date}'),
            date_format=os.getenv('DATE_FORMAT', '%Y%m%d')
        )
        
        # Конфигурация анализа классов
        class_analysis_config = ClassAnalysisConfig(
            table_prefix=os.getenv('CLASS_TABLE_PREFIX', 'migration_classes'),
            analyze_dependencies=get_bool_env('ANALYZE_DEPENDENCIES', True),
            check_rollback_support=get_bool_env('CHECK_ROLLBACK_SUPPORT', True),
            task_id=os.getenv('CLASS_ANALYSIS_TASK_ID', '120682')
        )
        
        # Конфигурация производительности
        performance_config = PerformanceConfig(
            batch_size=get_int_env('BATCH_SIZE', 1000),
            max_retries=get_int_env('MAX_RETRIES', 3),
            max_db_connections=get_int_env('MAX_DB_CONNECTIONS', 5),
            connection_pool_timeout=get_int_env('CONNECTION_POOL_TIMEOUT', 60),
            connection_pool_size=get_int_env('CONNECTION_POOL_SIZE', 3)
        )
        
        # Конфигурация директорий
        directories_config = DirectoryConfig(
            output_dir=os.getenv('OUTPUT_DIR', 'migration_output'),
            logs_dir=os.getenv('LOGS_DIR', 'logs'),
            templates_dir=os.getenv('TEMPLATES_DIR', 'templates'),
            auto_create_dirs=get_bool_env('AUTO_CREATE_DIRS', True)
        )
        
        return cls(
            mssql=mssql_config,
            postgres=postgres_config,
            java_home=java_home,
            export_script_path=os.getenv('EXPORT_SCRIPT_PATH', './export_db_scripts.py'),
            sitex_context_url=os.getenv('SITEX_CONTEXT_URL', 
                'http://10.3.0.254:22617/test_voron_124724_migration_0001/'),
            directories=directories_config,
            logging=logging_config,
            task_generation=task_generation_config,
            class_analysis=class_analysis_config,
            performance=performance_config,
            debug_mode=get_bool_env('DEBUG_MODE', False),
            create_backups=get_bool_env('CREATE_BACKUPS', True),
            default_encoding=os.getenv('DEFAULT_ENCODING', 'utf-8')
        )

# Глобальная конфигурация
config = MigrationConfig.from_env() 