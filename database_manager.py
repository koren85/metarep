"""
Менеджеры для работы с базами данных через JDBC
Расширяет функциональность из export_db_scripts.py
"""
import os
import jpype
import jpype.imports
import logging
import atexit
from typing import List, Tuple, Any, Optional
from contextlib import contextmanager
from config import config

# Глобальная переменная для отслеживания состояния JVM
_jvm_started = False

def initialize_jvm():
    """
    Единая инициализация JVM для всех JDBC подключений
    Аналогично export_db_scripts.py
    """
    global _jvm_started
    
    if _jvm_started and jpype.isJVMStarted():
        return True
    
    logger = logging.getLogger(__name__)
    
    try:
        # Проверка драйверов
        mssql_driver = config.mssql.driver_path
        postgres_driver = config.postgres.driver_path
        
        if not os.path.exists(mssql_driver):
            logger.error(f"❌ MSSQL JDBC драйвер не найден: {mssql_driver}")
            return False
            
        if not os.path.exists(postgres_driver):
            logger.error(f"❌ PostgreSQL JDBC драйвер не найден: {postgres_driver}")
            return False
        
        # Настройка JAVA_HOME
        java_home = config.java_home
        logger.info(f"🔍 Trying JAVA_HOME: {java_home}")
        
        if not os.path.exists(java_home):
            logger.error(f"❌ JAVA_HOME не найден: {java_home}")
            
            # Попробуем найти Java автоматически
            import glob
            possible_paths = glob.glob('/Library/Java/JavaVirtualMachines/*/Contents/Home')
            if possible_paths:
                java_home = possible_paths[0]
                logger.info(f"🔄 Нашли Java: {java_home}")
            else:
                return False
        
        os.environ['JAVA_HOME'] = java_home
        logger.info(f"✅ Using JAVA_HOME: {java_home}")
        
        # Создаем classpath для обоих драйверов (аналогично export_db_scripts.py)
        classpath = f"{mssql_driver}{os.pathsep}{postgres_driver}"
        
        if not jpype.isJVMStarted():
            # Используем автоматический поиск JVM
            try:
                jvm_path = jpype.getDefaultJVMPath()
                logger.info(f"🔍 JVM path: {jvm_path}")
                
                # Проверим существование файла
                if not os.path.exists(jvm_path):
                    logger.error(f"❌ JVM файл не найден: {jvm_path}")
                    return False
                
                # Оптимизированные параметры JVM для M2 Mac
                jvm_args = [
                    f"-Djava.class.path={classpath}",
                    "-Xmx1024m",  # Ограничиваем память
                    "-Xms256m",   # Начальная память
                    "-XX:+UseG1GC",  # Используем G1 сборщик мусора
                    "-XX:MaxGCPauseMillis=200",
                    "-Djava.awt.headless=true",  # Без GUI
                    "-XX:+UnlockExperimentalVMOptions",  # Для M2 совместимости
                    "-XX:+UseZGC" if hasattr(jpype, '_hasFeature') else "-XX:+UseG1GC"  # ZGC для новых версий
                ]
                
                # Запускаем JVM с оптимизированными параметрами
                jpype.startJVM(jvm_path, *jvm_args, convertStrings=False)
                logger.info("✅ JVM запущена успешно")
                
                # Регистрируем shutdown при выходе из приложения
                atexit.register(shutdown_jvm)
                
            except Exception as jvm_error:
                logger.error(f"❌ Ошибка JVM: {jvm_error}")
                return False
        
        _jvm_started = True
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации JVM: {e}")
        return False

def shutdown_jvm():
    """Безопасное завершение JVM"""
    global _jvm_started
    
    logger = logging.getLogger(__name__)
    
    try:
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            logger.info("JVM завершена")
        _jvm_started = False
    except Exception as e:
        logger.warning(f"Предупреждение при завершении JVM: {e}")

class DatabaseManager:
    """Базовый класс для работы с БД через JDBC"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def connect(self) -> bool:
        """Установка соединения с БД"""
        try:
            # Инициализируем JVM если еще не запущена
            if not initialize_jvm():
                return False
            
            # Импортируем Java классы
            from java.sql import DriverManager, SQLException
            
            # Формируем JDBC URL
            jdbc_url = self.db_config.jdbc_url_template.format(
                host=self.db_config.host,
                port=self.db_config.port,
                database=self.db_config.database
            )
            
            self.logger.info(f"JDBC URL: {jdbc_url}")
            self.logger.info(f"User: {self.db_config.username}")
            self.logger.info(f"Database: {self.db_config.database}")
            
            # Создаем соединение с таймаутами
            connection_properties = {
                'user': self.db_config.username,
                'password': self.db_config.password,
                'connectTimeout': str(self.db_config.connection_timeout * 1000),  # В миллисекундах
                'socketTimeout': str(self.db_config.query_timeout * 1000)
            }
            
            # Создаем соединение
            self.connection = DriverManager.getConnection(jdbc_url, self.db_config.username, self.db_config.password)
            
            self.logger.info("✅ JDBC соединение установлено успешно!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения к БД: {e}")
            return False
    
    def disconnect(self):
        """Закрытие соединения с БД"""
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Соединение с БД закрыто")
            except Exception as e:
                self.logger.error(f"Ошибка закрытия соединения: {e}")
            finally:
                self.connection = None
    
    def execute_query(self, query: str) -> List[Tuple[Any, ...]]:
        """Выполнение SELECT запроса"""
        if not self.connection:
            raise Exception("Нет соединения с БД")
        
        try:
            statement = self.connection.createStatement()
            
            # Устанавливаем таймауты
            statement.setQueryTimeout(self.db_config.query_timeout)
            
            resultSet = statement.executeQuery(query)
            
            # Получаем метаданные для определения количества колонок
            metadata = resultSet.getMetaData()
            column_count = metadata.getColumnCount()
            
            results = []
            while resultSet.next():
                row = []
                for i in range(1, column_count + 1):
                    value = resultSet.getObject(i)
                    # Преобразуем Java объекты в Python с правильной кодировкой
                    if value is not None:
                        if hasattr(value, 'toString'):
                            value_str = str(value)
                            # Дополнительная проверка для русских символов
                            # Если строка содержит вопросительные знаки, возможно проблема кодировки
                            if isinstance(value_str, str) and '?' in value_str:
                                self.logger.debug(f"Возможная проблема кодировки в значении: {value_str}")
                            value = value_str
                        else:
                            value = value
                    row.append(value)
                results.append(tuple(row))
            
            self.logger.info(f"Выполнен запрос, получено {len(results)} строк")
            
            resultSet.close()
            statement.close()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения запроса: {e}")
            raise
    
    def execute_update(self, query: str) -> int:
        """Выполнение INSERT/UPDATE/DELETE запроса"""
        if not self.connection:
            raise Exception("Нет соединения с БД")
        
        try:
            statement = self.connection.createStatement()
            
            # Устанавливаем таймауты
            statement.setQueryTimeout(self.db_config.query_timeout)
            
            affected_rows = statement.executeUpdate(query)
            
            self.logger.info(f"Выполнен запрос, затронуто {affected_rows} строк")
            
            statement.close()
            return affected_rows
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения запроса: {e}")
            raise
    
    @contextmanager
    def transaction(self):
        """Контекстный менеджер для транзакций"""
        if not self.connection:
            raise Exception("Нет соединения с БД")
        
        try:
            self.connection.setAutoCommit(False)
            yield
            self.connection.commit()
            self.logger.info("Транзакция зафиксирована")
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Транзакция отменена: {e}")
            raise
        finally:
            self.connection.setAutoCommit(True)

class MSSQLManager(DatabaseManager):
    """Менеджер для работы с Microsoft SQL Server"""
    
    def __init__(self):
        super().__init__(config.mssql)

class PostgreSQLManager(DatabaseManager):
    """Менеджер для работы с PostgreSQL"""
    
    def __init__(self):
        super().__init__(config.postgres)
