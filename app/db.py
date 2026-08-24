import logging
import psycopg2
import psycopg2.extras
from app.config import config
from app.models import SearchProfile

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(config.database_url)


def init_schema() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id              BIGINT PRIMARY KEY,
                    origin_airports      TEXT[]      NOT NULL DEFAULT '{}',
                    destination_airports TEXT[]      NOT NULL DEFAULT '{}',
                    depart_from          DATE,
                    depart_to            DATE,
                    trip_length_min      INT         NOT NULL DEFAULT 7,
                    trip_length_max      INT         NOT NULL DEFAULT 14,
                    adults               INT         NOT NULL DEFAULT 2,
                    children_ages        INT[]       NOT NULL DEFAULT '{}',
                    max_connections      INT         NOT NULL DEFAULT 3,
                    watch_enabled        BOOL        NOT NULL DEFAULT FALSE,
                    last_watch_run       TIMESTAMPTZ,
                    created_at           TIMESTAMPTZ DEFAULT NOW(),
                    updated_at           TIMESTAMPTZ DEFAULT NOW()
                )
            """)
        conn.commit()
    logger.info("Database schema initialised")


def get_or_create_user(chat_id: int) -> dict:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO users (chat_id) VALUES (%s)
                ON CONFLICT (chat_id) DO NOTHING
            """, (chat_id,))
            cur.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def update_user_profile(chat_id: int, **fields) -> None:
    if not fields:
        return
    set_clauses = ", ".join(f"{k} = %s" for k in fields)
    set_clauses += ", updated_at = NOW()"
    values = list(fields.values()) + [chat_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE users SET {set_clauses} WHERE chat_id = %s",
                values,
            )
        conn.commit()


def set_watch(chat_id: int, enabled: bool) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET watch_enabled = %s, updated_at = NOW() WHERE chat_id = %s",
                (enabled, chat_id),
            )
        conn.commit()


def mark_watch_run(chat_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET last_watch_run = NOW(), updated_at = NOW() WHERE chat_id = %s",
                (chat_id,),
            )
        conn.commit()


def get_all_watch_users() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE watch_enabled = TRUE")
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def row_to_profile(row: dict) -> SearchProfile:
    return SearchProfile(
        origin_airports=row["origin_airports"] or [],
        destination_airports=row["destination_airports"] or [],
        depart_from=str(row["depart_from"]) if row["depart_from"] else None,
        depart_to=str(row["depart_to"]) if row["depart_to"] else None,
        trip_length_min=row["trip_length_min"],
        trip_length_max=row["trip_length_max"],
        adults=row["adults"],
        children_ages=row["children_ages"] or [],
        max_connections=row["max_connections"],
    )
