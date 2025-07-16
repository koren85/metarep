"""
Flask приложение для анализа классов SiTex
"""
import os
from flask import Flask, render_template, request, jsonify
from data_service import DataService
from config import config

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
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
    base_url = request.args.get('base_url', '')
    
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
        base_url=base_url if base_url else None
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
                             'base_url': base_url
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
    base_url = request.args.get('base_url', '')
    
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
        base_url=base_url if base_url else None
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
                             'base_url': base_url
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
    base_url = request.args.get('base_url', '')
    
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
        base_url=base_url if base_url else None
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
                             'base_url': base_url
                         })

@app.route('/class/<int:class_ouid>')
def class_detail(class_ouid):
    """Детальная страница класса"""
    
    base_url = request.args.get('base_url', '')
    search = request.args.get('search', '')
    status_variance = request.args.get('status_variance', type=int)
    event = request.args.get('event', type=int)
    
    result = data_service.get_class_details(
        class_ouid, 
        base_url if base_url else None,
        search if search else None,
        status_variance,
        event
    )
    
    if 'error' in result:
        return render_template('error.html', error=result['error'])
    
    # Добавляем текущие фильтры для отображения на странице
    result['current_filters'] = {
        'search': search,
        'status_variance': status_variance,
        'event': event,
        'base_url': base_url
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
    
    result = data_service.get_class_details(
        class_ouid, 
        base_url if base_url else None,
        search if search else None,
        status_variance,
        event
    )
    return jsonify(result)

@app.route('/api/statistics')
def api_statistics():
    """API для получения статистики"""
    
    result = data_service.get_statistics()
    return jsonify(result)

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
    
    app.run(debug=True, host='0.0.0.0', port=5001) 