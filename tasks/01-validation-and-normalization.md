# Задача 01: Валидация и нормализация входных данных

## Статус
`DONE`

## Цель
Реализовать строгую проверку и нормализацию входного словаря `event` в `app.py` до сохранения данных в базу, чтобы некорректные события отклонялись со статусом `"invalid"`, а корректные очищались от краевых пробелов с сохранением регистра символов.

## Критерии приёмки
- [x] Проверяется, что `event` является словарём (`dict`). При передаче не-словаря возвращается `{"status": "invalid", "reason": "..."}` без необработанных исключений.
- [x] Проверяется наличие обязательных полей: `source`, `external_id`, `customer`, `message`.
- [x] Проверяется, что значение каждого из четырёх полей имеет тип `str` (числа, `None`, списки, булевы значения отклоняются).
- [x] У каждого из четырёх полей удаляются пробелы по краям (`strip()`), при этом регистр символов сохраняется (`"Telegram"` и `"telegram"` остаются в исходном регистре).
- [x] Если хотя бы одно поле после удаления краевых пробелов оказывается пустым (`""`), возвращается `{"status": "invalid", "reason": "<непустое понятное объяснение>"}`.
- [x] При невалидном событии запись в таблицы `leads` и `notifications` не создаётся.

## Ограничения
- Использовать только стандартную библиотеку Python (Python 3.10+).
- Сохранить сигнатуру публичной функции `process_event(event: dict, db_path: str) -> dict`.
- Не изменять существующие проверки в `tests/test_app.py`.

## Результаты проверок

Проверено 2026-10-19. Python 3.14 (`py -3`). Существующие тесты в `tests/test_app.py` не изменялись.

### Критерии валидации и нормализации

Команда: отдельный прогон сценариев через `process_event` (не-словарь, `None`, отсутствие каждого обязательного поля, типы `int` / `None` / `list` / `bool`, пробелы по краям, сохранение регистра). Соединения в прогоне закрывались явно.

```text
OK non-dict
  {'status': 'invalid', 'reason': 'Событие должно быть словарём'}
OK none-event no exception
  {'status': 'invalid', 'reason': 'Событие должно быть словарём'}
OK missing-source
  {'status': 'invalid', 'reason': 'Отсутствует обязательное поле: source'}
OK missing-external_id
  {'status': 'invalid', 'reason': 'Отсутствует обязательное поле: external_id'}
OK missing-customer
  {'status': 'invalid', 'reason': 'Отсутствует обязательное поле: customer'}
OK missing-message
  {'status': 'invalid', 'reason': 'Отсутствует обязательное поле: message'}
OK type-source-int
  {'status': 'invalid', 'reason': 'Поле source должно быть строкой'}
OK type-external_id-NoneType
  {'status': 'invalid', 'reason': 'Поле external_id должно быть строкой'}
OK type-customer-list
  {'status': 'invalid', 'reason': 'Поле customer должно быть строкой'}
OK type-message-bool
  {'status': 'invalid', 'reason': 'Поле message должно быть строкой'}
OK type-customer-bool
  {'status': 'invalid', 'reason': 'Поле customer должно быть строкой'}
OK blank-source
  {'status': 'invalid', 'reason': 'Поле source не должно быть пустым'}
OK blank-external_id
  {'status': 'invalid', 'reason': 'Поле external_id не должно быть пустым'}
OK blank-customer
  {'status': 'invalid', 'reason': 'Поле customer не должно быть пустым'}
OK blank-message
  {'status': 'invalid', 'reason': 'Поле message не должно быть пустым'}
OK trim keeps case
  {'response': {'status': 'created', 'id': 1}, 'row': ('Telegram', 'event-100', 'Client', 'Text')}
OK Telegram vs telegram stored apart
  {'response': {'status': 'created', 'id': 2}, 'rows': [('Telegram',), ('telegram',)]}
RESULT 17 / 17
```

Для каждого невалидного сценария счётчики `leads` и `notifications` оставались `(0, 0)` до первой успешной записи. После `strip()` в базу попали `Telegram`, `event-100`, `Client`, `Text`. Источники `Telegram` и `telegram` сохранены как разные строки.

### Существующие unit-тесты

Команда:

```text
py -3 -m unittest discover -s tests -v
```

Итог: `Ran 8 tests in 0.177s`, `FAILED (failures=4, errors=4)`.

Утверждения, относящиеся к этой задаче, прошли. Падения — сценарии дедупликации из задачи 02 (повтор всё ещё создаёт новую заявку):

```text
FAIL: test_duplicate_after_reopening_database
AssertionError: {'status': 'created', 'id': 2} != {'status': 'duplicate', 'id': 1}

FAIL: test_first_event_data_is_preserved_on_retry
AssertionError: {'status': 'created', 'id': 2} != {'status': 'duplicate', 'id': 1}

FAIL: test_retry_is_duplicate_without_new_notification
AssertionError: {'status': 'created', 'id': 2} != {'status': 'duplicate', 'id': 1}

FAIL: test_whitespace_is_trimmed_before_comparison
AssertionError: {'status': 'created', 'id': 2} != {'status': 'duplicate', 'id': 1}
```

`ERROR` у `test_missing_customer_is_invalid_and_not_saved`, `test_non_string_field_is_invalid`, `test_new_lead_creates_one_notification` и `test_same_external_id_from_different_source_is_new` возникают в `tearDown`: `PermissionError: [WinError 32]` при удалении временного `leads.sqlite3`. Проверки самих тестов к этому моменту уже выполнены. Файл остаётся занят, потому что `count()` в `tests/test_app.py` открывает SQLite через контекстный менеджер, который транзакцию завершает, но соединение не закрывает. Этот файл по ограничению задачи не менялся. В `process_event` соединение закрывается в `finally`.
