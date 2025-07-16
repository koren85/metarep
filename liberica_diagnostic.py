#!/usr/bin/env python3
"""
Утилита для диагностики Liberica JDK 17 и JPype
Использование: python liberica_diagnostic.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_separator(title):
    """Печатает разделитель с заголовком"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def check_system_info():
    """Проверка системной информации"""
    print_separator("СИСТЕМНАЯ ИНФОРМАЦИЯ")
    
    print(f"ОС: {platform.system()} {platform.release()}")
    print(f"Архитектура: {platform.machine()}")
    print(f"Python версия: {sys.version}")
    
    # Проверка переменных окружения
    java_home = os.environ.get('JAVA_HOME')
    path = os.environ.get('PATH', '')
    
    print(f"JAVA_HOME: {java_home}")
    print(f"Java в PATH: {'java' in path}")

def check_java_installation():
    """Проверка установки Java"""
    print_separator("ПРОВЕРКА JAVA")
    
    try:
        # Проверка java команды
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Java команда работает")
            print("Вывод java -version:")
            print(result.stderr)
        else:
            print("❌ Java команда не работает")
            print(f"Ошибка: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ Java команда зависла")
    except FileNotFoundError:
        print("❌ Java команда не найдена")
    except Exception as e:
        print(f"❌ Ошибка проверки Java: {e}")

def find_liberica_installations():
    """Поиск установок Liberica JDK"""
    print_separator("ПОИСК LIBERICA JDK")
    
    # Пути поиска для разных ОС
    if platform.system() == "Darwin":  # macOS
        search_paths = [
            "/Library/Java/JavaVirtualMachines",
            "/opt/homebrew/lib",
            "/usr/local/lib"
        ]
    elif platform.system() == "Linux":
        search_paths = [
            "/usr/lib/jvm",
            "/opt/java",
            "/usr/java"
        ]
    else:  # Windows
        search_paths = [
            "C:\\Program Files\\BellSoft",
            "C:\\Program Files (x86)\\BellSoft"
        ]
    
    liberica_found = []
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            try:
                for item in os.listdir(search_path):
                    if "liberica" in item.lower():
                        full_path = os.path.join(search_path, item)
                        liberica_found.append(full_path)
                        print(f"✅ Найдена Liberica JDK: {full_path}")
            except Exception as e:
                print(f"❌ Ошибка поиска в {search_path}: {e}")
    
    if not liberica_found:
        print("❌ Liberica JDK не найдена")
    
    return liberica_found

def check_jpype():
    """Проверка JPype"""
    print_separator("ПРОВЕРКА JPYPE")
    
    try:
        import jpype
        print(f"✅ JPype установлен, версия: {jpype.__version__}")
        
        # Проверка поиска JVM
        try:
            jvm_path = jpype.getDefaultJVMPath()
            print(f"✅ Автоматически найден JVM путь: {jvm_path}")
            
            # Проверка существования файла
            if os.path.exists(jvm_path):
                print("✅ JVM библиотека существует")
            else:
                print("❌ JVM библиотека НЕ существует")
        except Exception as e:
            print(f"❌ Ошибка поиска JVM: {e}")
            
    except ImportError:
        print("❌ JPype НЕ установлен")
        print("Для установки выполните: pip install JPype1")

def test_jvm_startup():
    """Тест запуска JVM"""
    print_separator("ТЕСТ ЗАПУСКА JVM")
    
    try:
        import jpype
        
        if jpype.isJVMStarted():
            print("⚠️  JVM уже запущена")
            return
        
        print("Попытка запуска JVM...")
        
        # Получаем путь к JVM
        jvm_path = jpype.getDefaultJVMPath()
        print(f"Используемый путь JVM: {jvm_path}")
        
        # Запускаем JVM
        jpype.startJVM(jvm_path)
        print("✅ JVM запущена успешно")
        
        # Проверяем версию Java
        java_version = jpype.java.lang.System.getProperty("java.version")
        java_vendor = jpype.java.lang.System.getProperty("java.vendor")
        java_vm_name = jpype.java.lang.System.getProperty("java.vm.name")
        
        print(f"Java версия: {java_version}")
        print(f"Поставщик: {java_vendor}")
        print(f"JVM: {java_vm_name}")
        
        # Проверяем, что это Liberica
        if "bellsoft" in java_vendor.lower() or "liberica" in java_vm_name.lower():
            print("✅ Используется Liberica JDK")
        else:
            print("⚠️  Используется НЕ Liberica JDK")
        
        # Останавливаем JVM
        jpype.shutdownJVM()
        print("✅ JVM остановлена")
        
    except ImportError:
        print("❌ JPype не установлен")
    except Exception as e:
        print(f"❌ Ошибка запуска JVM: {e}")

def test_jdbc_drivers():
    """Тест JDBC драйверов"""
    print_separator("ТЕСТ JDBC ДРАЙВЕРОВ")
    
    # Проверяем наличие драйверов
    driver_paths = [
        "./lib/postgresql.jar",
        "./lib/mssql-jdbc.jar",
        "lib/postgresql.jar",
        "lib/mssql-jdbc.jar"
    ]
    
    found_drivers = []
    for driver_path in driver_paths:
        if os.path.exists(driver_path):
            print(f"✅ Найден драйвер: {driver_path}")
            found_drivers.append(driver_path)
        else:
            print(f"❌ Драйвер не найден: {driver_path}")
    
    if not found_drivers:
        print("❌ JDBC драйверы не найдены")
        return
    
    # Тестируем загрузку драйверов
    try:
        import jpype
        
        if not jpype.isJVMStarted():
            jvm_path = jpype.getDefaultJVMPath()
            classpath = os.pathsep.join(found_drivers)
            
            print(f"Запуск JVM с classpath: {classpath}")
            jpype.startJVM(jvm_path, f"-Djava.class.path={classpath}")
        
        # Проверяем драйвер PostgreSQL
        try:
            from java.sql import DriverManager
            driver_class = jpype.JClass("org.postgresql.Driver")
            print("✅ PostgreSQL драйвер загружен")
        except Exception as e:
            print(f"❌ PostgreSQL драйвер не загружен: {e}")
        
        # Проверяем драйвер MS SQL
        try:
            driver_class = jpype.JClass("com.microsoft.sqlserver.jdbc.SQLServerDriver")
            print("✅ MS SQL Server драйвер загружен")
        except Exception as e:
            print(f"❌ MS SQL Server драйвер не загружен: {e}")
        
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            
    except ImportError:
        print("❌ JPype не установлен")
    except Exception as e:
        print(f"❌ Ошибка тестирования драйверов: {e}")

def generate_recommendations():
    """Генерация рекомендаций"""
    print_separator("РЕКОМЕНДАЦИИ")
    
    # Проверим основные проблемы
    problems = []
    solutions = []
    
    # Проверка Java
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if "liberica" not in result.stderr.lower() and "bellsoft" not in result.stderr.lower():
            problems.append("Используется не Liberica JDK")
            solutions.append("Установите Liberica JDK 17 и настройте JAVA_HOME")
    except:
        problems.append("Java не найдена")
        solutions.append("Установите Liberica JDK 17")
    
    # Проверка JPype
    try:
        import jpype
        if jpype.__version__ < "1.4.0":
            problems.append("Устаревшая версия JPype")
            solutions.append("Обновите JPype: pip install --upgrade JPype1")
    except ImportError:
        problems.append("JPype не установлен")
        solutions.append("Установите JPype: pip install JPype1")
    
    # Проверка JDBC драйверов
    if not any(os.path.exists(p) for p in ["./lib/postgresql.jar", "lib/postgresql.jar"]):
        problems.append("PostgreSQL JDBC драйвер не найден")
        solutions.append("Скачайте postgresql.jar и поместите в папку lib/")
    
    if problems:
        print("Обнаружены следующие проблемы:")
        for i, problem in enumerate(problems, 1):
            print(f"{i}. {problem}")
        
        print("\nРекомендованные решения:")
        for i, solution in enumerate(solutions, 1):
            print(f"{i}. {solution}")
    else:
        print("✅ Никаких проблем не обнаружено!")
        print("Система готова к работе с Liberica JDK 17 и JDBC")

def main():
    """Основная функция диагностики"""
    print("🔍 Диагностика Liberica JDK 17 для JDBC")
    print("=" * 50)
    
    # Выполняем все проверки
    check_system_info()
    check_java_installation()
    find_liberica_installations()
    check_jpype()
    test_jvm_startup()
    test_jdbc_drivers()
    generate_recommendations()
    
    print("\n" + "=" * 50)
    print("🏁 Диагностика завершена")

if __name__ == "__main__":
    main() 