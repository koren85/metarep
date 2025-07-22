#!/usr/bin/env python3
"""
Диагностический скрипт для тестирования стабильности подключения к БД
"""

import time
import sys
from database_manager import PostgreSQLManager
from config import config

def test_connection_stability():
    """Тестирует стабильность соединения с БД"""
    
    db_manager = PostgreSQLManager()
    
    print("🔍 Диагностика стабильности соединения с БД")
    print("=" * 50)
    
    # Тест 1: Базовое подключение
    print("1️⃣ Тест базового подключения...")
    if db_manager.connect():
        print("✅ Подключение установлено")
    else:
        print("❌ Ошибка подключения")
        return False
    
    # Тест 2: Простой запрос
    print("\n2️⃣ Тест простого запроса...")
    try:
        result = db_manager.execute_query("SELECT COUNT(*) FROM sxattr_source")
        total_attrs = int(result[0][0])
        print(f"✅ Простой запрос успешен: {total_attrs} атрибутов")
    except Exception as e:
        print(f"❌ Ошибка простого запроса: {e}")
        return False
    
    # Тест 3: Множественные запросы
    print("\n3️⃣ Тест множественных запросов...")
    success_count = 0
    for i in range(10):
        try:
            result = db_manager.execute_query(f"SELECT COUNT(*) FROM sxattr_source WHERE ouid > {i * 100}")
            success_count += 1
            print(f"  Запрос {i+1}/10: ✅")
        except Exception as e:
            print(f"  Запрос {i+1}/10: ❌ {e}")
        time.sleep(0.1)
    
    print(f"Успешных запросов: {success_count}/10")
    
    # Тест 4: Сложные запросы с a_log
    print("\n4️⃣ Тест парсинга a_log (имитация реальной нагрузки)...")
    complex_query = """
        SELECT a.ouid, a.name, a.a_log 
        FROM sxattr_source a 
        WHERE a.a_log IS NOT NULL 
          AND LENGTH(a.a_log) > 100 
        LIMIT 5
    """
    
    try:
        result = db_manager.execute_query(complex_query)
        print(f"✅ Получено {len(result)} атрибутов с a_log")
        
        # Тестируем парсинг a_log для каждого атрибута
        for i, (ouid, name, a_log) in enumerate(result):
            print(f"  Парсинг атрибута {i+1}: {name}")
            try:
                # Имитируем тот же сложный запрос что используется в _analyze_attribute_exceptions_cached
                parse_query = f"""
                    WITH source_data AS (
                        SELECT
                            {ouid} as ouid,
                            '{name}' as name,
                            $${a_log}$$ as a_log
                    ),
                    attr_blocks AS (
                        SELECT
                            s.ouid,
                            s.name,
                            trim(split_part(attr_block, E'\\n', 1)) as attribute_name
                        FROM source_data s
                        CROSS JOIN LATERAL (
                            SELECT unnest(
                                regexp_split_to_array(
                                    s.a_log,
                                    E'(?=\\n[^[:space:]\\n])'
                                )
                            ) AS attr_block
                        ) attr_blocks
                        WHERE attr_block ~ 'source[[:space:]]*='
                            AND trim(split_part(attr_block, E'\\n', 1)) != ''
                            AND length(trim(attr_block)) > 0
                    )
                    SELECT COUNT(*) FROM attr_blocks
                """
                
                parse_result = db_manager.execute_query(parse_query)
                properties_count = int(parse_result[0][0])
                print(f"    ✅ Найдено {properties_count} свойств")
                
            except Exception as e:
                print(f"    ❌ Ошибка парсинга: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка теста парсинга: {e}")
    
    # Тест 5: Длительная нагрузка
    print("\n5️⃣ Тест длительной нагрузки (30 сек)...")
    start_time = time.time()
    request_count = 0
    error_count = 0
    
    while time.time() - start_time < 30:
        try:
            result = db_manager.execute_query("SELECT COUNT(*) FROM sxattr_source")
            request_count += 1
            if request_count % 10 == 0:
                print(f"  Запросов выполнено: {request_count}")
        except Exception as e:
            error_count += 1
            print(f"  ❌ Ошибка #{error_count}: {e}")
        
        time.sleep(0.5)
    
    print(f"Результат нагрузочного теста:")
    print(f"  Успешных запросов: {request_count}")
    print(f"  Ошибок: {error_count}")
    print(f"  Процент успеха: {(request_count/(request_count+error_count)*100):.1f}%")
    
    # Тест 6: Тест исключений
    print("\n6️⃣ Тест загрузки исключений...")
    try:
        exceptions_query = "SELECT COUNT(*) FROM __meta_statistic"
        result = db_manager.execute_query(exceptions_query)
        exceptions_count = int(result[0][0])
        print(f"✅ Найдено {exceptions_count} исключений в таблице")
        
        # Проверяем несколько ключевых исключений
        key_exceptions = ['readOnly', 'informs', 'description', 'title']
        for key in key_exceptions:
            check_query = f"SELECT COUNT(*) FROM __meta_statistic WHERE entity_name = '{key}'"
            result = db_manager.execute_query(check_query)
            count = int(result[0][0])
            print(f"  Исключение '{key}': {count} записей")
            
    except Exception as e:
        print(f"❌ Ошибка теста исключений: {e}")
    
    # Закрываем соединение
    db_manager.disconnect()
    
    print("\n🏁 Диагностика завершена")
    return True

def test_attributes_analysis():
    """Тестирует анализ атрибутов как в реальном приложении"""
    
    print("\n🔬 Тест анализа атрибутов (имитация get_attributes)")
    print("=" * 50)
    
    from data_service import DataService
    
    data_service = DataService()
    
    # Тестируем получение атрибутов с анализом исключений
    print("Запуск анализа атрибутов с фильтрами как на проде...")
    
    result = data_service.get_attributes(
        page=1,
        per_page=20,
        search='',
        status_variance=2,
        event=0,
        a_priznak=3,
        base_url='',
        source_base_url='',
        exception_action_filter=None,
        analyze_exceptions=True
    )
    
    if 'error' in result:
        print(f"❌ Ошибка анализа: {result['error']}")
        return False
    
    stats = result.get('statistics', {})
    print(f"📊 Результаты анализа:")
    print(f"  Всего атрибутов: {result.get('total_count', 0)}")
    print(f"  Обновить: {stats.get('update_count', 0)}")
    print(f"  Игнорировать: {stats.get('ignore_count', 0)}")
    print(f"  Без действия: {stats.get('no_action_count', 0)}")
    
    total = stats.get('update_count', 0) + stats.get('ignore_count', 0) + stats.get('no_action_count', 0)
    print(f"  Проверка суммы: {total} (должно совпадать с общим количеством)")
    
    return True

if __name__ == "__main__":
    print("🚀 Запуск диагностики подключения к БД MetaRep")
    print(f"📍 Подключение к: {config.postgres.host}:{config.postgres.port}/{config.postgres.database}")
    print(f"👤 Пользователь: {config.postgres.username}")
    
    try:
        # Тест стабильности соединения
        if test_connection_stability():
            print("\n✅ Базовые тесты соединения пройдены")
            
            # Тест анализа атрибутов
            if test_attributes_analysis():
                print("\n✅ Тест анализа атрибутов успешен")
            else:
                print("\n❌ Тест анализа атрибутов провален")
                sys.exit(1)
        else:
            print("\n❌ Базовые тесты соединения провалены")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)
        
    print("\n🎉 Все тесты завершены успешно!") 