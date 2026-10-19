# Задача 03: Расширение набора unit-тестов и проверка всех сценариев

## Статус
`DONE`

## Цель
Добиться прохождения всех существующих тестов в `tests/test_app.py` и добавить минимум два новых содержательных теста на сценарии, которые недостаточно покрыты исходным тестовым набором.

## Критерии приёмки
- [x] Все 8 исходных тестов в `tests/test_app.py` проходят без изменения их проверок.
- [x] Добавлено минимум 2 новых теста в `tests/test_app.py`, покрывающих важные граничные сценарии, например:
  1. Чувствительность `source` к регистру: `"Telegram"` и `"telegram"` с одинаковым `external_id` создают две разные заявки.
  2. Сохранение очищенных от краевых пробелов значений `customer` и `message` в БД.
  3. Обработка событий с отсутствующими обязательными ключами, `None` или некорректным типом самого `event` без необработанных исключений.
- [x] Все тесты успешно проходят при запуске штатной командой `python -m unittest discover -s tests -v`.

## Ограничения
- Не удалять и не ослаблять проверки в существующих тестах `tests/test_app.py`.
- Использовать стандартный фреймворк `unittest`.
- Тесты должны использовать временную БД (`tempfile`) и не оставлять `.sqlite3` файлов в рабочей директории.

## Результаты проверок

Проверено 2026-10-19. Команда `python` в этой среде не найдена, запуск эквивалентом `py -3 -m unittest discover -s tests -v`.

Добавлены тесты `test_source_case_creates_separate_leads`, `test_customer_and_message_are_stored_trimmed`, `test_missing_key_none_and_non_dict_are_invalid`. Утверждения восьми исходных тестов не менялись. В `count()` и в чтении строки исходного теста соединение закрывается явно, в `tearDown` перед удалением временного каталога вызывается `gc.collect()`: иначе на Windows контекстный менеджер `sqlite3` оставляет файл занятым.

```text
test_customer_and_message_are_stored_trimmed ... ok
test_duplicate_after_reopening_database ... ok
test_first_event_data_is_preserved_on_retry ... ok
test_missing_customer_is_invalid_and_not_saved ... ok
test_missing_key_none_and_non_dict_are_invalid ... ok
test_new_lead_creates_one_notification ... ok
test_non_string_field_is_invalid ... ok
test_retry_is_duplicate_without_new_notification ... ok
test_same_external_id_from_different_source_is_new ... ok
test_source_case_creates_separate_leads ... ok
test_whitespace_is_trimmed_before_comparison ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.274s

OK
```

Файлов `*.sqlite3` в рабочей директории после прогона нет.
