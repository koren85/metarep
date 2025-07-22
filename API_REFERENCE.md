# MetaRep API Reference

## Base URL
```
http://localhost:5001/api
```

## Authentication
Нет аутентификации (открытый доступ)

## Common Parameters

### Pagination
- `page`: int = 1 (номер страницы)
- `per_page`: int = 20 (записей на странице, макс. 1000)

### Filters  
- `search`: string (поиск по имени/описанию)
- `status_variance`: int (0,1,2)
- `event`: int (0,1,2,3,4)
- `a_priznak`: int (1,2,3)
- `base_url`: string (URL админки назначения)
- `source_base_url`: string (URL админки источника)

### Attributes specific
- `exception_action_filter`: int (-1,0,2)
- `analyze_exceptions`: bool (включить анализ исключений)

## Endpoints

### Classes
```
GET /api/classes
GET /api/class/{id}
```

### Groups
```
GET /api/groups
```

### Attributes  
```
GET /api/attributes
```

### Exceptions
```
GET /api/exceptions
POST /api/exceptions
PUT /api/exceptions/{id}
DELETE /api/exceptions/{id}
```

### Actions
```
POST /api/class/{id}/load-actions
POST /api/class/{id}/save-actions
POST /api/migrate-actions
POST /api/reload-exceptions
```

### Statistics
```
GET /api/statistics
```

## Response Formats

### Success Response
```json
{
  "items": [...],
  "total_count": 1500,
  "total_pages": 75,
  "current_page": 1,
  "per_page": 20,
  "has_prev": false,
  "has_next": true
}
```

### Error Response
```json
{
  "error": "Error message"
}
```

### Action Response
```json
{
  "success": true,
  "message": "Action completed",
  "class_count": 5,
  "group_count": 10,
  "attribute_count": 50
}
```

## Examples

### Get Classes with Filters
```bash
curl "http://localhost:5001/api/classes?status_variance=2&search=User&page=1&per_page=20"
```

### Get Class Details
```bash
curl "http://localhost:5001/api/class/12345?base_url=http://target-admin.com"
```

### Create Exception
```bash
curl -X POST "http://localhost:5001/api/exceptions" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "attribute",
    "entity_name": "readOnly", 
    "property_name": "Только для чтения",
    "action": 2
  }'
```

### Load Actions for Class
```bash
curl -X POST "http://localhost:5001/api/class/12345/load-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "search": "",
    "status_variance": 2,
    "event": 4
  }'
```

### Save Actions to Database
```bash
curl -X POST "http://localhost:5001/api/class/12345/save-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "search": "",
    "status_variance": 2, 
    "event": 4
  }'
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (валидация)
- `404` - Not Found
- `500` - Internal Server Error

## Entity Types

### Exception entity_type values
- `class` - Классы
- `group` - Группы атрибутов  
- `attribute` - Атрибуты

### Action values
- `0` - Игнорировать
- `2` - Обновить
- `-1` - Без действия (устаревшее, мигрируется в 2)

### Status variance values
- `0` - Без различий
- `1` - Частичные различия
- `2` - Есть различия

### Event values
- `0` - Без действия
- `1` - Создать
- `2` - Обновить
- `3` - Удалить
- `4` - Анализ

### Priznak values
- `1` - Переносим миграцией
- `2` - Не переносим
- `3` - Переносим не миграцией 