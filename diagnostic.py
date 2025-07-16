import sys
import platform
import subprocess
import os

print("=== ДИАГНОСТИКА СИСТЕМЫ ===")
print(f"Python версия: {sys.version}")
print(f"Python путь: {sys.executable}")
print(f"Архитектура: {platform.machine()}")
print(f"Платформа: {platform.platform()}")

# Проверяем JPype
try:
    import jpype
    print(f"JPype версия: {jpype.__version__}")
    print(f"JPype путь: {jpype.__file__}")
except Exception as e:
    print(f"Ошибка импорта JPype: {e}")

# Проверяем Java
print(f"JAVA_HOME: {os.environ.get('JAVA_HOME', 'НЕ УСТАНОВЛЕН')}")

try:
    result = subprocess.run(['java', '-version'], capture_output=True, text=True)
    print(f"Java версия (stderr): {result.stderr}")
except Exception as e:
    print(f"Ошибка проверки Java: {e}")

# Проверяем какой Java видит jpype
try:
    import jpype
    if not jpype.isJVMStarted():
        jvm_path = jpype.getDefaultJVMPath()
        print(f"JPype видит JVM путь: {jvm_path}")
        print(f"JVM файл существует: {os.path.exists(jvm_path)}")
except Exception as e:
    print(f"Ошибка проверки JVM пути: {e}")
