import sqlite3
from pathlib import Path


DB_PATH = Path("data/bot.db")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS auto_replies (
                chat_id INTEGER PRIMARY KEY,
                replied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


def has_auto_replied(chat_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
            """
            SELECT 1
            FROM auto_replies
            WHERE chat_id = ?
            """,
            (chat_id,),
        ).fetchone()

    return result is not None


def mark_auto_replied(chat_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO auto_replies (chat_id)
            VALUES (?)
            """,
            (chat_id,),
        )

        conn.commit()