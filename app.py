"""
Flask приложение для анализа классов SiTex
"""
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, make_response
from data_service import DataService
from config import config
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO

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
    exception_action_filter = request.args.get('exception_action_filter', type=int)
    analyze_exceptions_param = request.args.get('analyze_exceptions', 'false').lower()
    analyze_exceptions = analyze_exceptions_param == 'true'
    
    # Фильтры исключений применяются только в режиме анализа исключений
    if analyze_exceptions:
        source_target_filter = request.args.get('source_target_filter', '')
        property_filter = request.args.getlist('property_filter')  # Множественный выбор свойств
        
        # Обработка чекбокса: если есть "true" в списке значений, то True, иначе False
        show_update_actions_values = request.args.getlist('show_update_actions')
        show_update_actions = 'true' in show_update_actions_values
    else:
        # В быстром режиме игнорируем фильтры исключений
        source_target_filter = None
        property_filter = None  
        show_update_actions = True
    
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
        source_base_url=source_base_url if source_base_url else None,
        exception_action_filter=exception_action_filter,
        analyze_exceptions=analyze_exceptions,
        source_target_filter=source_target_filter,
        property_filter=property_filter,
        show_update_actions=show_update_actions
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
                             'source_base_url': source_base_url,
                             'exception_action_filter': exception_action_filter,
                             'analyze_exceptions': analyze_exceptions,
                             'source_target_filter': source_target_filter,
                             'property_filter': property_filter,
                             'show_update_actions': show_update_actions
                         })

@app.route('/classes')
def classes():
    """Страница с анализом классов по исключениям"""
    
    # Получаем параметры из запроса
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    exception_action_filter = request.args.get('exception_action_filter', type=int)
    analyze_exceptions_param = request.args.get('analyze_exceptions', 'false').lower()
    analyze_exceptions = analyze_exceptions_param == 'true'
    
    # Фильтры исключений применяются только в режиме анализа исключений
    if analyze_exceptions:
        source_target_filter = request.args.get('source_target_filter', '')
        property_filter = request.args.getlist('property_filter')  # Множественный выбор свойств
        
        # Обработка чекбокса: если есть "true" в списке значений, то True, иначе False
        show_update_actions_values = request.args.getlist('show_update_actions')
        show_update_actions = 'true' in show_update_actions_values
    else:
        # В быстром режиме игнорируем фильтры исключений
        source_target_filter = None
        property_filter = None  
        show_update_actions = True
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 1000:
        per_page = 20
    
    # Получаем данные с анализом исключений
    result = data_service.get_classes_with_exceptions(
        page=page,
        per_page=per_page,
        search=search if search else None,
        status_variance=status_variance,
        event=event,
        a_priznak=a_priznak,
        base_url=base_url if base_url else None,
        source_base_url=source_base_url if source_base_url else None,
        exception_action_filter=exception_action_filter,
        analyze_exceptions=analyze_exceptions,
        source_target_filter=source_target_filter,
        property_filter=property_filter,
        show_update_actions=show_update_actions
    )
    
    # Получаем статистику
    statistics = data_service.get_statistics()
    
    return render_template('classes.html', 
                         result=result, 
                         statistics=statistics,
                         current_filters={
                             'search': search,
                             'status_variance': status_variance,
                             'event': event,
                             'a_priznak': a_priznak,
                             'base_url': base_url,
                             'source_base_url': source_base_url,
                             'exception_action_filter': exception_action_filter,
                             'analyze_exceptions': analyze_exceptions,
                             'source_target_filter': source_target_filter,
                             'property_filter': property_filter,
                             'show_update_actions': show_update_actions
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

@app.route('/api/classes_with_exceptions')
def api_classes_with_exceptions():
    """API для получения списка классов с анализом исключений (для AJAX)"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    exception_action_filter = request.args.get('exception_action_filter', type=int)
    analyze_exceptions_param = request.args.get('analyze_exceptions', 'false').lower()
    analyze_exceptions = analyze_exceptions_param == 'true'
    
    # Фильтры исключений
    source_target_filter = request.args.get('source_target_filter', '')
    property_filter = request.args.getlist('property_filter')
    show_update_actions_values = request.args.getlist('show_update_actions')
    show_update_actions = 'true' in show_update_actions_values
    
    # Проверяем корректность значений
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 1000:
        per_page = 20
    
    result = data_service.get_classes_with_exceptions(
        page=page,
        per_page=per_page,
        search=search if search else None,
        status_variance=status_variance,
        event=event,
        a_priznak=a_priznak,
        base_url=base_url if base_url else None,
        source_base_url=source_base_url if source_base_url else None,
        exception_action_filter=exception_action_filter,
        analyze_exceptions=analyze_exceptions,
        source_target_filter=source_target_filter if source_target_filter else None,
        property_filter=property_filter if property_filter else None,
        show_update_actions=show_update_actions
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



@app.route('/api/reload-exceptions', methods=['POST'])
def api_reload_exceptions():
    """API для принудительной перезагрузки данных исключений из файлов"""
    
    try:
        # Принудительно перезагружаем данные исключений
        result = data_service.db_manager.init_exceptions_data(force_reload=True)
        
        if result:
            return jsonify({
                "success": True,
                "message": "Данные исключений успешно перезагружены из файлов"
            })
        else:
            return jsonify({"error": "Ошибка перезагрузки данных исключений"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Ошибка перезагрузки исключений: {e}"}), 500

# ===== Эндпоинты для экспорта в Excel =====

@app.route('/export/classes.xlsx')
def export_classes_xlsx():
    """Экспорт классов в Excel с учетом фильтров"""
    
    # Получаем все те же параметры что и для обычного просмотра
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    exception_action_filter = request.args.get('exception_action_filter', type=int)
    analyze_exceptions_param = request.args.get('analyze_exceptions', 'false').lower()
    analyze_exceptions = analyze_exceptions_param == 'true'
    
    # Фильтры исключений применяются только в режиме анализа исключений
    if analyze_exceptions:
        source_target_filter = request.args.get('source_target_filter', '')
        property_filter = request.args.getlist('property_filter')
        show_update_actions_values = request.args.getlist('show_update_actions')
        show_update_actions = 'true' in show_update_actions_values
    else:
        source_target_filter = None
        property_filter = None  
        show_update_actions = True
    
    try:
        # Получаем данные без пагинации (устанавливаем per_page = 100000)
        result = data_service.get_classes_with_exceptions(
            page=1,
            per_page=100000,  # Получаем все записи
            search=search if search else None,
            status_variance=status_variance,
            event=event,
            a_priznak=a_priznak,
            base_url=base_url if base_url else None,
            source_base_url=source_base_url if source_base_url else None,
            exception_action_filter=exception_action_filter,
            analyze_exceptions=analyze_exceptions,
            source_target_filter=source_target_filter,
            property_filter=property_filter,
            show_update_actions=show_update_actions
        )
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        # Создаем Excel файл
        wb = Workbook()
        ws = wb.active
        ws.title = "Классы"
        
        # Определяем заголовки в зависимости от режима
        if analyze_exceptions and result.get('classes_by_action'):
            # Полный режим с анализом исключений
            headers = ['ID', 'Имя', 'Описание', 'Свойство', 'Source', 'Target', 'Признак', 'Действие']
            ws.append(headers)
            
            # Стилизуем заголовки
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # Добавляем данные для обновления
            if result['classes_by_action'].get('update_list'):
                for class_item in result['classes_by_action']['update_list']:
                    priznak_text = {1: 'Переносим миграцией', 2: 'Не переносим', 3: 'Переносим не миграцией'}.get(class_item.get('a_priznak'), 'Не определен')
                    ws.append([
                        class_item.get('ouid', ''),
                        class_item.get('name', ''),
                        class_item.get('description', ''),
                        class_item.get('property_name', ''),
                        class_item.get('source', ''),
                        class_item.get('target', ''),
                        priznak_text,
                        'Обновить'
                    ])
            
            # Добавляем данные для игнорирования
            if result['classes_by_action'].get('ignore_list'):
                for class_item in result['classes_by_action']['ignore_list']:
                    priznak_text = {1: 'Переносим миграцией', 2: 'Не переносим', 3: 'Переносим не миграцией'}.get(class_item.get('a_priznak'), 'Не определен')
                    ws.append([
                        class_item.get('ouid', ''),
                        class_item.get('name', ''),
                        class_item.get('description', ''),
                        class_item.get('property_name', ''),
                        class_item.get('source', ''),
                        class_item.get('target', ''),
                        priznak_text,
                        'Игнорировать'
                    ])
            
            # Добавляем данные без действий
            if result['classes_by_action'].get('no_action_list'):
                for class_item in result['classes_by_action']['no_action_list']:
                    priznak_text = {1: 'Переносим миграцией', 2: 'Не переносим', 3: 'Переносим не миграцией'}.get(class_item.get('a_priznak'), 'Не определен')
                    ws.append([
                        class_item.get('ouid', ''),
                        class_item.get('name', ''),
                        class_item.get('description', ''),
                        class_item.get('property_name', ''),
                        class_item.get('source', ''),
                        class_item.get('target', ''),
                        priznak_text,
                        'Без действия'
                    ])
        
        elif result.get('classes', {}).get('fast_mode'):
            # Быстрый режим
            headers = ['ID', 'Имя', 'Описание', 'Статус', 'Действие', 'Признак']
            ws.append(headers)
            
            # Стилизуем заголовки
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # Добавляем данные
            for class_item in result['classes']['fast_mode']:
                status_text = {0: 'Идентичны', 1: 'Отсутствует', 2: 'Отличаются'}.get(class_item.get('a_status_variance'), str(class_item.get('a_status_variance', '')))
                action_text = {0: 'Игнорировать', 1: 'Добавить', 2: 'Обновить'}.get(class_item.get('a_event'), str(class_item.get('a_event', '')))
                priznak_text = {1: 'Переносим миграцией', 2: 'Не переносим', 3: 'Переносим не миграцией'}.get(class_item.get('a_priznak'), 'Не определен')
                
                ws.append([
                    class_item.get('ouid', ''),
                    class_item.get('name', ''),
                    class_item.get('description', ''),
                    status_text,
                    action_text,
                    priznak_text
                ])
        else:
            # Нет данных
            ws.append(['Нет данных для экспорта'])
        
        # Автоширина колонок
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Сохраняем в BytesIO
        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        # Генерируем имя файла с датой
        filename = f"classes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        response = make_response(excel_buffer.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return jsonify({"error": f"Ошибка экспорта: {str(e)}"}), 500

@app.route('/export/attributes.xlsx')
def export_attributes_xlsx():
    """Экспорт атрибутов в Excel с учетом фильтров"""
    
    # Получаем все те же параметры что и для обычного просмотра
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    exception_action_filter = request.args.get('exception_action_filter', type=int)
    analyze_exceptions_param = request.args.get('analyze_exceptions', 'false').lower()
    analyze_exceptions = analyze_exceptions_param == 'true'
    
    # Фильтры исключений применяются только в режиме анализа исключений
    if analyze_exceptions:
        source_target_filter = request.args.get('source_target_filter', '')
        property_filter = request.args.getlist('property_filter')
        show_update_actions_values = request.args.getlist('show_update_actions')
        show_update_actions = 'true' in show_update_actions_values
    else:
        source_target_filter = None
        property_filter = None  
        show_update_actions = True
    
    try:
        # Получаем данные без пагинации (устанавливаем per_page = 100000)
        result = data_service.get_attributes(
            page=1,
            per_page=100000,  # Получаем все записи
            search=search if search else None,
            status_variance=status_variance,
            event=event,
            a_priznak=a_priznak,
            base_url=base_url if base_url else None,
            source_base_url=source_base_url if source_base_url else None,
            exception_action_filter=exception_action_filter,
            analyze_exceptions=analyze_exceptions,
            source_target_filter=source_target_filter,
            property_filter=property_filter,
            show_update_actions=show_update_actions
        )
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        # Создаем Excel файл
        wb = Workbook()
        ws = wb.active
        ws.title = "Атрибуты"
        
        # Определяем заголовки в зависимости от режима
        if analyze_exceptions and result.get('classes'):
            # Полный режим с анализом исключений - группировка по классам
            headers = ['Класс', 'ID', 'Имя', 'Заголовок', 'Тип', 'Свойство', 'Source', 'Target', 'Признак', 'Действие']
            ws.append(headers)
            
            # Стилизуем заголовки
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # Добавляем данные по классам
            for class_name, class_data in result['classes'].items():
                # Атрибуты для обновления
                if class_data.get('attributes', {}).get('update_list'):
                    for attr in class_data['attributes']['update_list']:
                        priznak_text = {1: 'Переносим миграцией', 2: 'Не переносим', 3: 'Переносим не миграцией'}.get(attr.get('a_priznak'), 'Не определен')
                        ws.append([
                            class_data.get('class_name', ''),
                            attr.get('ouid', ''),
                            attr.get('name', ''),
                            attr.get('title', ''),
                            attr.get('datatype_name', ''),
                            attr.get('property_name', ''),
                            attr.get('source', ''),
                            attr.get('target', ''),
                            priznak_text,
                            'Обновить'
                        ])
                
                # Атрибуты для игнорирования
                if class_data.get('attributes', {}).get('ignore_list'):
                    for attr in class_data['attributes']['ignore_list']:
                        priznak_text = {1: 'Переносим миграцией', 2: 'Не переносим', 3: 'Переносим не миграцией'}.get(attr.get('a_priznak'), 'Не определен')
                        ws.append([
                            class_data.get('class_name', ''),
                            attr.get('ouid', ''),
                            attr.get('name', ''),
                            attr.get('title', ''),
                            attr.get('datatype_name', ''),
                            attr.get('property_name', ''),
                            attr.get('source', ''),
                            attr.get('target', ''),
                            priznak_text,
                            'Игнорировать'
                        ])
                
                # Атрибуты без действий
                if class_data.get('attributes', {}).get('no_action_list'):
                    for attr in class_data['attributes']['no_action_list']:
                        priznak_text = {1: 'Переносим миграцией', 2: 'Не переносим', 3: 'Переносим не миграцией'}.get(attr.get('a_priznak'), 'Не определен')
                        ws.append([
                            class_data.get('class_name', ''),
                            attr.get('ouid', ''),
                            attr.get('name', ''),
                            attr.get('title', ''),
                            attr.get('datatype_name', ''),
                            attr.get('property_name', ''),
                            attr.get('source', ''),
                            attr.get('target', ''),
                            priznak_text,
                            'Без действия'
                        ])
        
        elif result.get('attributes', {}).get('fast_mode'):
            # Быстрый режим
            headers = ['ID', 'Имя', 'Заголовок', 'Класс', 'Тип', 'Признак']
            ws.append(headers)
            
            # Стилизуем заголовки
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # Добавляем данные
            for attr in result['attributes']['fast_mode']:
                priznak_text = {1: 'Переносим миграцией', 2: 'Не переносим', 3: 'Переносим не миграцией'}.get(attr.get('a_priznak'), 'Не определен')
                
                ws.append([
                    attr.get('ouid', ''),
                    attr.get('name', ''),
                    attr.get('title', ''),
                    attr.get('class_name', ''),
                    attr.get('datatype_name', ''),
                    priznak_text
                ])
        else:
            # Нет данных
            ws.append(['Нет данных для экспорта'])
        
        # Автоширина колонок
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Сохраняем в BytesIO
        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        # Генерируем имя файла с датой
        filename = f"attributes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        response = make_response(excel_buffer.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return jsonify({"error": f"Ошибка экспорта: {str(e)}"}), 500

@app.route('/api/generate_sql_scripts')
def generate_sql_scripts():
    """API для генерации SQL скриптов для отфильтрованных атрибутов (все записи)"""
    
    # Получаем все те же параметры что и для обычного просмотра
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    exception_action_filter = request.args.get('exception_action_filter', type=int)
    analyze_exceptions_param = request.args.get('analyze_exceptions', 'false').lower()
    analyze_exceptions = analyze_exceptions_param == 'true'
    
    # Фильтры исключений применяются только в режиме анализа исключений
    if analyze_exceptions:
        source_target_filter = request.args.get('source_target_filter', '')
        property_filter = request.args.getlist('property_filter')
        show_update_actions_values = request.args.getlist('show_update_actions')
        show_update_actions = 'true' in show_update_actions_values
    else:
        source_target_filter = None
        property_filter = None  
        show_update_actions = True
    
    try:
        # Получаем данные без пагинации (все записи)
        result = data_service.get_attributes(
            page=1,
            per_page=100000,  # Получаем все записи
            search=search if search else None,
            status_variance=status_variance,
            event=event,
            a_priznak=a_priznak,
            base_url=base_url if base_url else None,
            source_base_url=source_base_url if source_base_url else None,
            exception_action_filter=exception_action_filter,
            analyze_exceptions=analyze_exceptions,
            source_target_filter=source_target_filter,
            property_filter=property_filter,
            show_update_actions=show_update_actions
        )
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        # Генерируем SQL скрипты
        sql_scripts = []
        
        # Определяем значение A_EVENT (согласно требованиям пользователя - всегда 2)
        a_event_value = 2
        
        if analyze_exceptions and result.get('classes'):
            # Полный режим с анализом исключений - группировка по классам
            for class_name, class_data in result['classes'].items():
                # Атрибуты для обновления
                if class_data.get('attributes', {}).get('update_list'):
                    for attr in class_data['attributes']['update_list']:
                        where_conditions = _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance)
                        if where_conditions:
                            script = f"UPDATE SXATTR_SOURCE SET A_EVENT={a_event_value} WHERE {where_conditions};"
                            sql_scripts.append(script)
                
                # Атрибуты для игнорирования
                if class_data.get('attributes', {}).get('ignore_list'):
                    for attr in class_data['attributes']['ignore_list']:
                        where_conditions = _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance)
                        if where_conditions:
                            script = f"UPDATE SXATTR_SOURCE SET A_EVENT={a_event_value} WHERE {where_conditions};"
                            sql_scripts.append(script)
                
                # Атрибуты без действий
                if class_data.get('attributes', {}).get('no_action_list'):
                    for attr in class_data['attributes']['no_action_list']:
                        where_conditions = _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance)
                        if where_conditions:
                            script = f"UPDATE SXATTR_SOURCE SET A_EVENT={a_event_value} WHERE {where_conditions};"
                            sql_scripts.append(script)
        
        elif result.get('attributes', {}).get('fast_mode'):
            # Быстрый режим - простая таблица атрибутов
            for attr in result['attributes']['fast_mode']:
                where_conditions = _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance)
                if where_conditions:
                    script = f"UPDATE SXATTR_SOURCE SET A_EVENT={a_event_value} WHERE {where_conditions};"
                    sql_scripts.append(script)
        
        # Формируем итоговый результат
        all_scripts = '\n'.join(sql_scripts)
        
        return jsonify({
            "success": True,
            "scripts": all_scripts,
            "count": len(sql_scripts),
            "message": f"Сгенерировано {len(sql_scripts)} SQL скриптов"
        })
        
    except Exception as e:
        return jsonify({"error": f"Ошибка генерации скриптов: {str(e)}"}), 500

@app.route('/api/generate_sql_scripts_page')
def generate_sql_scripts_page():
    """API для генерации SQL скриптов только для текущей страницы"""
    
    # Получаем параметры включая пагинацию
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    a_priznak = request.args.get('a_priznak', type=int)
    base_url = request.args.get('base_url', '')
    source_base_url = request.args.get('source_base_url', '')
    exception_action_filter = request.args.get('exception_action_filter', type=int)
    analyze_exceptions_param = request.args.get('analyze_exceptions', 'false').lower()
    analyze_exceptions = analyze_exceptions_param == 'true'
    
    # Фильтры исключений применяются только в режиме анализа исключений
    if analyze_exceptions:
        source_target_filter = request.args.get('source_target_filter', '')
        property_filter = request.args.getlist('property_filter')
        show_update_actions_values = request.args.getlist('show_update_actions')
        show_update_actions = 'true' in show_update_actions_values
    else:
        source_target_filter = None
        property_filter = None  
        show_update_actions = True
    
    try:
        # Получаем данные с учетом пагинации (только текущая страница)
        result = data_service.get_attributes(
            page=page,
            per_page=per_page,  # Используем реальную пагинацию
            search=search if search else None,
            status_variance=status_variance,
            event=event,
            a_priznak=a_priznak,
            base_url=base_url if base_url else None,
            source_base_url=source_base_url if source_base_url else None,
            exception_action_filter=exception_action_filter,
            analyze_exceptions=analyze_exceptions,
            source_target_filter=source_target_filter,
            property_filter=property_filter,
            show_update_actions=show_update_actions
        )
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        # Генерируем SQL скрипты (та же логика что и в generate_sql_scripts)
        sql_scripts = []
        
        # Определяем значение A_EVENT (согласно требованиям пользователя - всегда 2)
        a_event_value = 2
        
        if analyze_exceptions and result.get('classes'):
            # Полный режим с анализом исключений - группировка по классам
            for class_name, class_data in result['classes'].items():
                # Атрибуты для обновления
                if class_data.get('attributes', {}).get('update_list'):
                    for attr in class_data['attributes']['update_list']:
                        where_conditions = _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance)
                        if where_conditions:
                            script = f"UPDATE SXATTR_SOURCE SET A_EVENT={a_event_value} WHERE {where_conditions};"
                            sql_scripts.append(script)
                
                # Атрибуты для игнорирования
                if class_data.get('attributes', {}).get('ignore_list'):
                    for attr in class_data['attributes']['ignore_list']:
                        where_conditions = _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance)
                        if where_conditions:
                            script = f"UPDATE SXATTR_SOURCE SET A_EVENT={a_event_value} WHERE {where_conditions};"
                            sql_scripts.append(script)
                
                # Атрибуты без действий
                if class_data.get('attributes', {}).get('no_action_list'):
                    for attr in class_data['attributes']['no_action_list']:
                        where_conditions = _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance)
                        if where_conditions:
                            script = f"UPDATE SXATTR_SOURCE SET A_EVENT={a_event_value} WHERE {where_conditions};"
                            sql_scripts.append(script)
        
        elif result.get('attributes', {}).get('fast_mode'):
            # Быстрый режим - простая таблица атрибутов
            for attr in result['attributes']['fast_mode']:
                where_conditions = _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance)
                if where_conditions:
                    script = f"UPDATE SXATTR_SOURCE SET A_EVENT={a_event_value} WHERE {where_conditions};"
                    sql_scripts.append(script)
        
        # Формируем итоговый результат
        all_scripts = '\n'.join(sql_scripts)
        
        return jsonify({
            "success": True,
            "scripts": all_scripts,
            "count": len(sql_scripts),
            "message": f"Сгенерировано {len(sql_scripts)} SQL скриптов для текущей страницы"
        })
        
    except Exception as e:
        return jsonify({"error": f"Ошибка генерации скриптов: {str(e)}"}), 500

def _build_where_conditions_for_update(attr, search, a_priznak, event, status_variance):
    """Построение WHERE условий для UPDATE скриптов с учетом всех фильтров"""
    conditions = []
    
    # Обязательное условие по имени атрибута
    attr_name = attr.get('name', '')
    if attr_name:
        conditions.append(f"NAME='{attr_name}'")
    
    # Добавляем фильтры если они были применены
    if a_priznak is not None:
        conditions.append(f"A_PRIZNAK={a_priznak}")
    
    if event is not None:
        conditions.append(f"A_EVENT={event}")
        
    if status_variance is not None:
        conditions.append(f"A_STATUS_VARIANCE={status_variance}")
    
    # Если есть связь с классом, добавляем условие по классу
    ouidsxclass = attr.get('ouidsxclass')
    if ouidsxclass:
        conditions.append(f"OUIDSXCLASS={ouidsxclass}")
    
    return " AND ".join(conditions)

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