#!/usr/bin/env python3
"""
Утилита для диагностики проблем с Java для Flask приложения
"""
import os
import sys
import glob
import subprocess
from pathlib import Path

def check_java_installation():
    """Проверка установки Java"""
    print("🔍 Проверка Java installation...")
    
    # Проверяем JAVA_HOME
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        print(f"✅ JAVA_HOME установлена: {java_home}")
        if os.path.exists(java_home):
            print(f"✅ JAVA_HOME директория существует")
        else:
            print(f"❌ JAVA_HOME директория НЕ существует!")
    else:
        print("⚠️  JAVA_HOME не установлена")
    
    # Проверяем java команду
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, stderr=subprocess.STDOUT)
        print(f"✅ Java команда работает:")
        print(f"   {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Java команда не найдена")
    
    # Проверяем javac команду
    try:
        result = subprocess.run(['javac', '-version'], 
                              capture_output=True, text=True, stderr=subprocess.STDOUT)
        print(f"✅ Javac команда работает:")
        print(f"   {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Javac команда не найдена")

def find_java_installations():
    """Поиск всех установок Java"""
    print("\n🔍 Поиск установок Java...")
    
    java_paths = []
    
    # macOS пути
    if sys.platform == 'darwin':
        # Homebrew установки
        homebrew_paths = [
            '/opt/homebrew/opt/openjdk',
            '/usr/local/opt/openjdk',
            '/opt/homebrew/opt/openjdk@8',
            '/usr/local/opt/openjdk@8',
            '/opt/homebrew/opt/openjdk@11',
            '/usr/local/opt/openjdk@11',
            '/opt/homebrew/opt/openjdk@17',
            '/usr/local/opt/openjdk@17',
        ]
        
        for path in homebrew_paths:
            if os.path.exists(path):
                java_paths.append(path)
        
        # Системные установки
        system_paths = glob.glob('/Library/Java/JavaVirtualMachines/*/Contents/Home')
        java_paths.extend(system_paths)
    
    # Linux пути
    elif sys.platform.startswith('linux'):
        linux_paths = glob.glob('/usr/lib/jvm/java-*')
        java_paths.extend(linux_paths)
    
    if java_paths:
        print("✅ Найденные установки Java:")
        for i, path in enumerate(java_paths, 1):
            print(f"   {i}. {path}")
            
            # Проверяем версию
            java_exe = os.path.join(path, 'bin', 'java')
            if os.path.exists(java_exe):
                try:
                    result = subprocess.run([java_exe, '-version'], 
                                          capture_output=True, text=True, stderr=subprocess.STDOUT)
                    version_line = result.stdout.split('\n')[0]
                    print(f"      Версия: {version_line}")
                except:
                    print("      Версия: не удалось определить")
            else:
                print("      ❌ java executable не найден")
    else:
        print("❌ Java установки не найдены")
    
    return java_paths

def check_jpype():
    """Проверка jpype"""
    print("\n🔍 Проверка jpype...")
    
    try:
        import jpype
        print(f"✅ jpype импортирован, версия: {jpype.__version__}")
        
        # Проверяем getDefaultJVMPath
        try:
            jvm_path = jpype.getDefaultJVMPath()
            print(f"✅ getDefaultJVMPath(): {jvm_path}")
            
            if os.path.exists(jvm_path):
                print(f"✅ JVM файл существует")
            else:
                print(f"❌ JVM файл НЕ существует!")
                
        except Exception as e:
            print(f"❌ Ошибка getDefaultJVMPath(): {e}")
            
    except ImportError as e:
        print(f"❌ jpype не установлен: {e}")
        print("   Установите: pip install jpype1")

def check_jdbc_drivers():
    """Проверка JDBC драйверов"""
    print("\n🔍 Проверка JDBC драйверов...")
    
    drivers = [
        './lib/postgresql.jar',
        './lib/mssql-jdbc.jar'
    ]
    
    for driver in drivers:
        if os.path.exists(driver):
            size = os.path.getsize(driver)
            print(f"✅ {driver} - {size} байт")
        else:
            print(f"❌ {driver} - НЕ НАЙДЕН")

def recommendations():
    """Рекомендации по исправлению"""
    print("\n💡 Рекомендации:")
    print("1. Если Java не найдена:")
    print("   macOS: brew install openjdk")
    print("   Linux: sudo apt-get install openjdk-8-jdk")
    print("   или скачайте с https://adoptopenjdk.net/")
    
    print("\n2. Если jpype не работает:")
    print("   pip install jpype1")
    
    print("\n3. Если JDBC драйверы не найдены:")
    print("   Скачайте и поместите в папку lib/:")
    print("   - postgresql.jar")
    print("   - mssql-jdbc.jar")
    
    print("\n4. Если проблема с JAVA_HOME:")
    print("   Установите переменную окружения:")
    java_paths = find_java_installations()
    if java_paths:
        print(f"   export JAVA_HOME='{java_paths[0]}'")

if __name__ == "__main__":
    print("🚀 Диагностика Java для Flask приложения")
    print("=" * 50)
    
    check_java_installation()
    find_java_installations()
    check_jpype()
    check_jdbc_drivers()
    recommendations()
    
    print("\n" + "=" * 50)
    print("🏁 Диагностика завершена") 