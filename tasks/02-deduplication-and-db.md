# Задача 02: Дедупликация заявок по `(source, external_id)` и работа с БД

## Статус
`DONE`

## Цель
Обеспечить уникальность заявок по паре `(source, external_id)` в SQLite и корректную обработку повторных событий без создания дубликатов заявок, лишних уведомлений и без перезаписи исходных данных.

## Критерии приёмки
- [x] Уникальность заявки определяется парой `(source, external_id)` с учётом регистра и после удаления пробелов по краям.
- [x] В схеме БД (функция `_prepare_db`) добавлен уникальный индекс или ограничение по `(source, external_id)` в таблице `leads`.
- [x] Если пара `(source, external_id)` встречается впервые:
  - В таблицу `leads` сохраняются очищенные от краевых пробелов значения `source`, `external_id`, `customer`, `message`.
  - В таблицу `notifications` добавляется ровно одна запись с `lead_id` созданной заявки.
  - Функция возвращает `{"status": "created", "id": <int>}`, где `id` — целое положительное число.
- [x] Если пара `(source, external_id)` уже существует в БД:
  - Новая запись в `leads` не создаётся.
  - Новое уведомление в `notifications` не создаётся.
  - Первоначальные значения `customer` и `message` в таблице `leads` остаются без изменений (даже если в повторном событии пришёл другой текст).
  - Функция возвращает `{"status": "duplicate", "id": <existing_id>}` с тем же `id`, что и при создании.
- [x] Повторное подключение к тому же файлу БД (`db_path`) сохраняет ранее записанные данные.

## Ограничения
- Использовать только встроенный модуль `sqlite3` из стандартной библиотеки Python.
- Сохранить имена таблиц (`leads`, `notifications`) и существующих столбцов (`id`, `source`, `external_id`, `customer`, `message`, `lead_id`).
- Не создавать внешние сервисы, веб-интерфейсы или сторонние зависимости.

## Результаты проверок

Проверено 2026-10-19. Python 3.14 (`py -3`).

### Сценарии дедупликации

Отдельный прогон через `process_event` с явным закрытием соединений:

```text
OK created trimmed
  {'first': {'status': 'created', 'id': 1}, 'row': [(1, 'telegram', 'event-100', 'Client', 'Need delivery')], 'notes': [(1,)], 'idx': [('idx_leads_source_external_id', 'CREATE UNIQUE INDEX idx_leads_source_external_id\n            ON leads (source, external_id)')]}
OK unique index
  [('idx_leads_source_external_id', 'CREATE UNIQUE INDEX idx_leads_source_external_id\n            ON leads (source, external_id)')]
OK duplicate keeps original
  {'second': {'status': 'duplicate', 'id': 1}, 'row': [('Client', 'Need delivery')], 'counts': (1, 1)}
OK case sensitive source
  {'other': {'status': 'created', 'id': 2}, 'sources': [('telegram', 1), ('Telegram', 2)], 'counts': (2, 2)}
OK reopen same file
  {'third': {'status': 'duplicate', 'id': 1}, 'counts': (2, 2)}
RESULT 5 / 5
```

Повтор с другим `customer` и `message` вернул тот же `id` и не изменил исходную строку. `Telegram` и `telegram` сохранились как две заявки. Повторное открытие того же файла нашло уже записанную пару.

### Существующие unit-тесты

Команда:

```text
py -3 -m unittest discover -s tests -v
```

Итог: `Ran 8 tests in 0.163s`, `FAILED (errors=7)`.

Утверждений, которые бы упали, нет. `test_duplicate_after_reopening_database` завершился `ok`. Остальные семь тестов выполнили свои проверки и получили `ERROR` только в `tearDown`: `PermissionError: [WinError 32]` при удалении временного `leads.sqlite3`. Соединение остаётся открытым в `count()` и в прямом `sqlite3.connect` внутри `test_first_event_data_is_preserved_on_retry`, потому что контекстный менеджер `sqlite3` соединение не закрывает. Файл тестов в этой задаче не менялся.
