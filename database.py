"""SQLite persistence for accounts, nicknames, and battle records."""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "data" / "pokemon_quiz.db"
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{4,20}$")
NICKNAME_PATTERN = re.compile(r"^[0-9A-Za-z가-힣_]{2,12}$")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def initialize_database() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                nickname TEXT,
                partner_pokemon TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                wins INTEGER NOT NULL DEFAULT 0,
                best_score INTEGER NOT NULL DEFAULT 0,
                has_badge INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Migrate databases created by earlier app versions without losing accounts.
        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "partner_pokemon" not in columns:
            connection.execute("ALTER TABLE users ADD COLUMN partner_pokemon TEXT")


def validate_signup(username: str, password: str) -> str | None:
    if not USERNAME_PATTERN.fullmatch(username):
        return "아이디는 영문, 숫자, 밑줄만 사용해 4~20자로 입력해 주세요."
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "비밀번호는 영문과 숫자를 포함해 8자 이상이어야 합니다."
    return None


def validate_nickname(nickname: str) -> str | None:
    if not NICKNAME_PATTERN.fullmatch(nickname):
        return "닉네임은 한글·영문·숫자·밑줄로 2~12자까지 입력해 주세요."
    return None


def _derive_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 240_000).hex()


def create_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    error = validate_signup(username, password)
    if error:
        return False, error

    salt = os.urandom(16)
    password_hash = _derive_password(password, salt)
    try:
        with _connect() as connection:
            connection.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt.hex()),
            )
    except sqlite3.IntegrityError:
        return False, "이미 사용 중인 아이디입니다."
    return True, "회원가입 완료! 이제 로그인해 주세요."


def authenticate(username: str, password: str) -> dict | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
    if row is None:
        return None
    candidate = _derive_password(password, bytes.fromhex(row["salt"]))
    if not hmac.compare_digest(candidate, row["password_hash"]):
        return None
    return dict(row)


def set_nickname(user_id: int, nickname: str) -> tuple[bool, str]:
    nickname = nickname.strip()
    error = validate_nickname(nickname)
    if error:
        return False, error
    with _connect() as connection:
        connection.execute("UPDATE users SET nickname = ? WHERE id = ?", (nickname, user_id))
    return True, nickname


def grant_partner_pokemon(user_id: int, pokemon_name: str = "루미볼트") -> str:
    """Grant the account its permanent first partner exactly once."""
    with _connect() as connection:
        connection.execute(
            """
            UPDATE users
               SET partner_pokemon = COALESCE(partner_pokemon, ?)
             WHERE id = ?
            """,
            (pokemon_name, user_id),
        )
        row = connection.execute(
            "SELECT partner_pokemon FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return row["partner_pokemon"]


def get_user(user_id: int) -> dict | None:
    with _connect() as connection:
        row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def record_battle(user_id: int, score: int, won: bool) -> None:
    with _connect() as connection:
        connection.execute(
            """
            UPDATE users
               SET attempts = attempts + 1,
                   wins = wins + ?,
                   best_score = MAX(best_score, ?),
                   has_badge = MAX(has_badge, ?)
             WHERE id = ?
            """,
            (int(won), score, int(won), user_id),
        )
