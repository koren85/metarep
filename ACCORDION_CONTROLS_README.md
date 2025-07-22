# Кнопки управления аккордеонами классов

## 🎯 Назначение

Добавлены кнопки для удобного управления отображением всех аккордеонов классов одновременно.

## 🎛 Функциональность

### Кнопки управления:
- **"Скрыть все"** - сворачивает все аккордеоны классов
- **"Раскрыть все"** - разворачивает все аккордеоны классов

### Расположение:
- Находятся в **правом верхнем углу** над аккордеонами
- Показываются только в **полном режиме** анализа исключений
- Компактный дизайн (`btn-sm`) не загромождает интерфейс

## 🎨 UI/UX

### Дизайн кнопок:
```html
<button type="button" class="btn btn-outline-secondary btn-sm" onclick="collapseAllAccordions()">
    <i class="bi bi-chevron-up"></i> Скрыть все
</button>
<button type="button" class="btn btn-outline-secondary btn-sm" onclick="expandAllAccordions()">
    <i class="bi bi-chevron-down"></i> Раскрыть все
</button>
```

### Иконки:
- **Скрыть все:** `bi-chevron-up` (стрелка вверх)
- **Раскрыть все:** `bi-chevron-down` (стрелка вниз)

## 🛠 Техническая реализация

### JavaScript функции:

**Скрытие всех аккордеонов:**
```javascript
function collapseAllAccordions() {
    const allCollapses = document.querySelectorAll('#classesAccordion .accordion-collapse');
    allCollapses.forEach(function(collapse) {
        const bsCollapse = bootstrap.Collapse.getInstance(collapse);
        if (bsCollapse) {
            bsCollapse.hide();
        } else {
            new bootstrap.Collapse(collapse, {show: false});
        }
    });
}
```

**Раскрытие всех аккордеонов:**
```javascript
function expandAllAccordions() {
    const allCollapses = document.querySelectorAll('#classesAccordion .accordion-collapse');
    allCollapses.forEach(function(collapse) {
        const bsCollapse = bootstrap.Collapse.getInstance(collapse);
        if (bsCollapse) {
            bsCollapse.show();
        } else {
            new bootstrap.Collapse(collapse, {show: true});
        }
    });
}
```

## 🔄 Логика работы

### Использование Bootstrap API:
1. **Поиск существующих экземпляров:** `bootstrap.Collapse.getInstance()`
2. **Управление состоянием:** `.show()` / `.hide()`
3. **Создание новых экземпляров:** при необходимости

### Совместимость:
- Работает с существующим кодом автораскрытия при фильтрах
- Не конфликтует с ручным управлением отдельными аккордеонами
- Корректно обрабатывает частично открытые аккордеоны

## 📱 Пользовательский сценарий

### Обычное использование:
1. **Заходишь в анализ исключений** → все аккордеоны закрыты по умолчанию
2. **Нажимаешь "Раскрыть все"** → все классы раскрываются
3. **Просматриваешь нужную информацию**
4. **Нажимаешь "Скрыть все"** → интерфейс становится компактным

### При фильтрации:
1. **Выбираешь фильтр по действиям** (например, "Игнорировать")
2. **Аккордеоны автоматически раскрываются** (существующая функция)
3. **Можешь управлять отображением** кнопками при необходимости

## 🎯 Преимущества

✅ **Удобство навигации:** быстрое управление всеми классами  
✅ **Экономия времени:** не нужно кликать каждый аккордеон отдельно  
✅ **Лучший обзор:** можно быстро получить общую картину или сфокусироваться  
✅ **Интуитивность:** знакомые иконки и понятные названия  
✅ **Не навязчивость:** кнопки маленькие и расположены в углу  

## 📊 Файлы изменены

- `templates/attributes.html`:
  - Добавлены HTML кнопки управления
  - Добавлены JavaScript функции `collapseAllAccordions()` и `expandAllAccordions()`

**Результат: удобное управление большим количеством классов!** 📂✨ 