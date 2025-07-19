"""
Flask приложение для анализа классов SiTex
"""
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from data_service import DataService
from config import config

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Добавляем фильтр для форматирования даты
@app.template_filter('strftime')
def strftime_filter(date_str, format='%d.%m.%Y %H:%M'):
    if date_str:
        # Убираем время зоны и миллисекунды если есть
        date_str = date_str.split('+')[0].split('.')[0]
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date_obj.strftime(format)
        except:
            return date_str.replace('T', ' ')[:16]
    return '-'

print(os.environ.get('JAVA_HOME'))
# Инициализация сервиса данных
data_service = DataService()

@app.route('/')
def index():
    """Главная страница со списком классов"""
    
    # Получаем параметры из запроса
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 1000:
        per_page = 20
    
    # Получаем данные
    result = data_service.get_classes(
        page=page,
        per_page=per_page,
        search=search if search else None,
        status_variance=status_variance,
        event=event,
        a_priznak=a_priznak,
        base_url=base_url if base_url else None,
        source_base_url=source_base_url if source_base_url else None
    )
    
    # Получаем статистику
    statistics = data_service.get_statistics()
    
    return render_template('index.html', 
                         result=result, 
                         statistics=statistics,
                         current_filters={
                             'search': search,
                             'status_variance': status_variance,
                             'event': event,
                             'a_priznak': a_priznak,
                             'base_url': base_url,
                             'source_base_url': source_base_url
                         })

@app.route('/groups')
def groups():
    """Страница со списком групп атрибутов"""
    
    # Получаем параметры из запроса
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 1000:
        per_page = 20
    
    # Получаем данные
    result = data_service.get_groups(
        page=page,
        per_page=per_page,
        search=search if search else None,
        status_variance=status_variance,
        event=event,
        a_priznak=a_priznak,
        base_url=base_url if base_url else None,
        source_base_url=source_base_url if source_base_url else None
    )
    
    # Получаем статистику
    statistics = data_service.get_statistics()
    
    return render_template('groups.html', 
                         result=result, 
                         statistics=statistics,
                         current_filters={
                             'search': search,
                             'status_variance': status_variance,
                             'event': event,
                             'a_priznak': a_priznak,
                             'base_url': base_url,
                             'source_base_url': source_base_url
                         })

@app.route('/attributes')
def attributes():
    """Страница со списком атрибутов"""
    
    # Получаем параметры из запроса
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 1000:
        per_page = 20
    
    # Получаем данные
    result = data_service.get_attributes(
        page=page,
        per_page=per_page,
        search=search if search else None,
        status_variance=status_variance,
        event=event,
        a_priznak=a_priznak,
        base_url=base_url if base_url else None,
        source_base_url=source_base_url if source_base_url else None
    )
    
    # Получаем статистику
    statistics = data_service.get_statistics()
    
    return render_template('attributes.html', 
                         result=result, 
                         statistics=statistics,
                         current_filters={
                             'search': search,
                             'status_variance': status_variance,
                             'event': event,
                             'a_priznak': a_priznak,
                             'base_url': base_url,
                             'source_base_url': source_base_url
                         })

@app.route('/class/<int:class_ouid>')
def class_detail(class_ouid):
    """Детальная страница класса"""
    
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    
    result = data_service.get_class_details(
        class_ouid, 
        base_url if base_url else None,
        source_base_url if source_base_url else None,
        search if search else None,
        status_variance,
        event,
        a_priznak
    )
    
    if 'error' in result:
        return render_template('error.html', error=result['error'])
    
    # Добавляем текущие фильтры для отображения на странице
    result['current_filters'] = {
        'search': search,
        'status_variance': status_variance,
        'event': event,
        'a_priznak': a_priznak,
        'base_url': base_url,
        'source_base_url': source_base_url
    }
    
    return render_template('class_detail.html', data=result)

@app.route('/api/classes')
def api_classes():
    """API для получения списка классов (для AJAX)"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 1000:
        per_page = 20
    
    result = data_service.get_classes(
        page=page,
        per_page=per_page,
        search=search if search else None,
        status_variance=status_variance,
        event=event,
        a_priznak=a_priznak,
        base_url=base_url if base_url else None
    )
    
    return jsonify(result)

@app.route('/api/groups')
def api_groups():
    """API для получения списка групп (для AJAX)"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 1000:
        per_page = 20
    
    result = data_service.get_groups(
        page=page,
        per_page=per_page,
        search=search if search else None,
        status_variance=status_variance,
        event=event,
        a_priznak=a_priznak,
        base_url=base_url if base_url else None
    )
    
    return jsonify(result)

@app.route('/api/attributes')
def api_attributes():
    """API для получения списка атрибутов (для AJAX)"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 1000:
        per_page = 20
    
    result = data_service.get_attributes(
        page=page,
        per_page=per_page,
        search=search if search else None,
        status_variance=status_variance,
        event=event,
        a_priznak=a_priznak,
        base_url=base_url if base_url else None
    )
    
    return jsonify(result)

@app.route('/api/class/<int:class_ouid>')
def api_class_detail(class_ouid):
    """API для получения деталей класса (для AJAX)"""
    
    base_url = request.args.get('base_url', '')
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    
    result = data_service.get_class_details(
        class_ouid, 
        base_url if base_url else None,
        search if search else None,
        status_variance,
        event,
        a_priznak
    )
    return jsonify(result)

@app.route('/api/statistics')
def api_statistics():
    """API для получения статистики"""
    
    result = data_service.get_statistics()
    return jsonify(result)

# ===== API для работы с исключениями =====

@app.route('/exceptions')
def exceptions():
    """Страница управления исключениями"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    entity_type = request.args.get('entity_type', '')
    search = request.args.get('search', '')
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 200:
        per_page = 50
    
    # Получаем данные исключений
    result = data_service.get_exceptions(
        page=page,
        per_page=per_page,
        entity_type=entity_type if entity_type else None,
        search=search if search else None
    )
    
    return render_template('exceptions.html', 
                         result=result,
                         current_filters={
                             'entity_type': entity_type,
                             'search': search
                         })

@app.route('/api/exceptions')
def api_exceptions():
    """API для получения списка исключений (для AJAX)"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    entity_type = request.args.get('entity_type', '')
    search = request.args.get('search', '')
    
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 200:
        per_page = 50
    
    result = data_service.get_exceptions(
        page=page,
        per_page=per_page,
        entity_type=entity_type if entity_type else None,
        search=search if search else None
    )
    
    return jsonify(result)

@app.route('/api/exceptions/<int:exception_id>')
def api_get_exception(exception_id):
    """API для получения исключения по ID"""
    
    result = data_service.get_exception(exception_id)
    return jsonify(result)

@app.route('/api/exceptions', methods=['POST'])
def api_create_exception():
    """API для создания нового исключения"""
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Отсутствуют данные"}), 400
    
    entity_type = data.get('entity_type')
    entity_name = data.get('entity_name')
    property_name = data.get('property_name')
    action = data.get('action', 0)
    
    if not entity_type or not entity_name or not property_name:
        return jsonify({"error": "Обязательные поля: entity_type, entity_name, property_name"}), 400
    
    if entity_type not in ['class', 'group', 'attribute']:
        return jsonify({"error": "entity_type должен быть: class, group или attribute"}), 400
    
    if action not in [0, 2]:
        return jsonify({"error": "action должен быть: 0 (игнорировать) или 2 (обновить)"}), 400
    
    result = data_service.create_exception(entity_type, entity_name, property_name, action)
    
    if "error" in result:
        return jsonify(result), 400
    else:
        return jsonify(result), 201

@app.route('/api/exceptions/<int:exception_id>', methods=['PUT'])
def api_update_exception(exception_id):
    """API для обновления исключения"""
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Отсутствуют данные"}), 400
    
    entity_type = data.get('entity_type')
    entity_name = data.get('entity_name') 
    property_name = data.get('property_name')
    action = data.get('action')
    
    # Валидация если поля переданы
    if entity_type and entity_type not in ['class', 'group', 'attribute']:
        return jsonify({"error": "entity_type должен быть: class, group или attribute"}), 400
    
    if action is not None and action not in [0, 2]:
        return jsonify({"error": "action должен быть: 0 (игнорировать) или 2 (обновить)"}), 400
    
    result = data_service.update_exception(
        exception_id, entity_type, entity_name, property_name, action
    )
    
    if "error" in result:
        return jsonify(result), 400
    else:
        return jsonify(result)

@app.route('/api/exceptions/<int:exception_id>', methods=['DELETE'])
def api_delete_exception(exception_id):
    """API для удаления исключения"""
    
    result = data_service.delete_exception(exception_id)
    
    if "error" in result:
        return jsonify(result), 400
    else:
        return jsonify(result)

@app.route('/api/class/<int:class_ouid>/load-actions', methods=['POST'])
def api_load_actions(class_ouid):
    """API для загрузки действий из списка исключений"""
    
    # Получаем параметры фильтрации из тела запроса
    filters = request.get_json() or {}
    search = filters.get('search', '')
    status_variance = filters.get('status_variance', '')
    event = filters.get('event', '')
    
    # Конвертируем пустые строки в None, числовые значения в int
    search = search if search else None
    status_variance = int(status_variance) if status_variance else None
    event = int(event) if event else None
    
    result = data_service.load_actions_from_exceptions(class_ouid, search, status_variance, event)
    
    if "error" in result:
        return jsonify(result), 400
    else:
        return jsonify(result)

@app.route('/api/class/<int:class_ouid>/save-actions', methods=['POST'])
def api_save_actions(class_ouid):
    """API для записи действий в БД"""
    
    # Получаем параметры фильтрации из тела запроса
    filters = request.get_json() or {}
    search = filters.get('search', '')
    status_variance = filters.get('status_variance', '')
    event = filters.get('event', '')
    
    # Конвертируем пустые строки в None, числовые значения в int
    search = search if search else None
    status_variance = int(status_variance) if status_variance else None
    event = int(event) if event else None
    
    result = data_service.save_actions_to_db(class_ouid, search, status_variance, event)
    
    if "error" in result:
        return jsonify(result), 400
    else:
        return jsonify(result)

@app.route('/api/migrate-actions', methods=['POST'])
def api_migrate_actions():
    """API для миграции действий с -1 на 2"""
    result = data_service.migrate_actions_from_minus_one_to_two()
    
    if "error" in result:
        return jsonify(result), 400
    else:
        return jsonify(result), 200

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Страница не найдена"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Внутренняя ошибка сервера"), 500

if __name__ == '__main__':
    # Создаем директории для статики и шаблонов если их нет
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Запуск Flask приложения...")
    print(f"📊 Подключение к PostgreSQL: {config.postgres.host}:{config.postgres.port}")
    print(f"🔗 Базовый URL админки: {config.sitex_context_url}")
    
    # Конфигурация из переменных окружения
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 'yes')
    
    app.run(debug=debug, host='0.0.0.0', port=port) 