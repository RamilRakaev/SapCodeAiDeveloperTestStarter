"""Небольшой учебный обработчик заявок. Некоторые сценарии реализованы с ошибками.

Тестовое задание САП КОД. Используются только синтетические данные.
"""

import sqlite3


def _prepare_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            external_id TEXT NOT NULL,
            customer TEXT NOT NULL,
            message TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL
        );
        """
    )


_REQUIRED_FIELDS = ("source", "external_id", "customer", "message")


def _validate_and_normalize(event: dict) -> tuple[dict | None, dict | None]:
    """Проверяет событие и возвращает (нормализованные поля, ответ invalid)."""
    if not isinstance(event, dict):
        return None, {
            "status": "invalid",
            "reason": "Событие должно быть словарём",
        }

    normalized: dict[str, str] = {}
    for field in _REQUIRED_FIELDS:
        if field not in event:
            return None, {
                "status": "invalid",
                "reason": f"Отсутствует обязательное поле: {field}",
            }
        value = event[field]
        if not isinstance(value, str):
            return None, {
                "status": "invalid",
                "reason": f"Поле {field} должно быть строкой",
            }
        value = value.strip()
        if value == "":
            return None, {
                "status": "invalid",
                "reason": f"Поле {field} не должно быть пустым",
            }
        normalized[field] = value
    return normalized, None


def process_event(event: dict, db_path: str) -> dict:
    """Принимает событие и возвращает dict со статусом и, при успехе, id заявки.

    Контракт статусов и бизнес-правила описаны в README.md.
    """
    normalized, error = _validate_and_normalize(event)
    if error is not None:
        return error

    connection = sqlite3.connect(db_path)
    try:
        _prepare_db(connection)

        cursor = connection.execute(
            """
            INSERT INTO leads (source, external_id, customer, message)
            VALUES (?, ?, ?, ?)
            """,
            (
                normalized["source"],
                normalized["external_id"],
                normalized["customer"],
                normalized["message"],
            ),
        )
        lead_id = cursor.lastrowid
        connection.execute(
            "INSERT INTO notifications (lead_id) VALUES (?)", (lead_id,)
        )
        connection.commit()
    finally:
        connection.close()
    return {"status": "created", "id": lead_id}
