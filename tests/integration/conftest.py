"""Fixtures for integration tests.

Self-contained fixtures that mirror api/tests/conftest.py to avoid
cross-directory fixture pollution when running the combined test suite.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from chatgpt_archive import db


@pytest.fixture(scope="session")
def sample_conversations_data() -> list[dict]:
    return [
        {
            "id": "conv-001-test",
            "title": "Test Conversation 1",
            "create_time": 1700000000.0,
            "update_time": 1700001000.0,
            "mapping": {
                "msg-001": {
                    "id": "msg-001",
                    "message": {
                        "id": "msg-001",
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello, how are you?"], "content_type": "text"},
                        "create_time": 1700000000.0,
                    },
                    "parent": None,
                    "children": ["msg-002"],
                },
                "msg-002": {
                    "id": "msg-002",
                    "message": {
                        "id": "msg-002",
                        "author": {"role": "assistant"},
                        "content": {
                            "parts": ["I'm doing well, thank you for asking!"],
                            "content_type": "text",
                        },
                        "create_time": 1700000100.0,
                    },
                    "parent": "msg-001",
                    "children": [],
                },
            },
        },
        {
            "id": "conv-002-test",
            "title": "Test Conversation 2",
            "create_time": 1700100000.0,
            "update_time": 1700101000.0,
            "mapping": {
                "msg-003": {
                    "id": "msg-003",
                    "message": {
                        "id": "msg-003",
                        "author": {"role": "user"},
                        "content": {"parts": ["What is Python?"], "content_type": "text"},
                        "create_time": 1700100000.0,
                    },
                    "parent": None,
                    "children": ["msg-004"],
                },
                "msg-004": {
                    "id": "msg-004",
                    "message": {
                        "id": "msg-004",
                        "author": {"role": "assistant"},
                        "content": {
                            "parts": ["Python is a programming language."],
                            "content_type": "text",
                        },
                        "create_time": 1700100100.0,
                    },
                    "parent": "msg-003",
                    "children": [],
                },
            },
        },
        {
            "id": "conv-003-test",
            "title": "Search Test Conversation",
            "create_time": 1700200000.0,
            "update_time": 1700201000.0,
            "mapping": {
                "msg-005": {
                    "id": "msg-005",
                    "message": {
                        "id": "msg-005",
                        "author": {"role": "user"},
                        "content": {
                            "parts": ["Tell me about machine learning"],
                            "content_type": "text",
                        },
                        "create_time": 1700200000.0,
                    },
                    "parent": None,
                    "children": ["msg-006"],
                },
                "msg-006": {
                    "id": "msg-006",
                    "message": {
                        "id": "msg-006",
                        "author": {"role": "assistant"},
                        "content": {
                            "parts": [
                                "Machine learning is a subset of AI that enables computers to learn from data."
                            ],
                            "content_type": "text",
                        },
                        "create_time": 1700200100.0,
                    },
                    "parent": "msg-005",
                    "children": [],
                },
            },
        },
    ]


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Generator[Path, None, None]:
    db_path = tmp_path / "integ_test_chats.db"
    yield db_path


@pytest.fixture
def initialized_db(temp_db_path: Path) -> Generator[Path, None, None]:
    conn = db.init_db(temp_db_path)
    conn.close()
    yield temp_db_path


@pytest.fixture
def populated_db(
    temp_db_path: Path, sample_conversations_data: list[dict]
) -> Generator[Path, None, None]:
    conn = db.init_db(temp_db_path)
    for conv in sample_conversations_data:
        cursor = conn.execute(
            "INSERT INTO conversations (openai_id, title, create_time, update_time) VALUES (?, ?, ?, ?)",
            (conv["id"], conv["title"], conv["create_time"], conv["update_time"]),
        )
        conv_db_id = cursor.lastrowid
        for msg_data in conv["mapping"].values():
            if msg_data.get("message"):
                msg = msg_data["message"]
                content_parts = msg.get("content", {}).get("parts", [])
                content = content_parts[0] if content_parts else ""
                conn.execute(
                    "INSERT INTO messages (conversation_id, openai_id, parent_id, author_role, content, create_time) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        conv_db_id,
                        msg["id"],
                        msg_data.get("parent"),
                        msg.get("author", {}).get("role", "user"),
                        content,
                        msg.get("create_time"),
                    ),
                )
    conn.commit()
    conn.close()
    yield temp_db_path


@pytest.fixture
def sample_archive_dir(tmp_path: Path, sample_conversations_data: list[dict]) -> Path:
    archive_dir = tmp_path / "integ_archive"
    archive_dir.mkdir()
    (archive_dir / "conversations.json").write_text(json.dumps(sample_conversations_data))
    (archive_dir / "user.json").write_text(json.dumps({"id": "test-user", "email": "test@example.com"}))
    return archive_dir


@pytest.fixture
def sample_archive_zip(sample_archive_dir: Path, tmp_path: Path) -> Path:
    zip_path = tmp_path / "integ_test_archive.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sample_archive_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(sample_archive_dir))
    return zip_path


@pytest.fixture
def env_with_test_db(populated_db: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("CHATGPT_ARCHIVE_DB", str(populated_db))
    monkeypatch.setenv("DB_PATH", str(populated_db))
    monkeypatch.setenv("TESTING", "1")
    return populated_db


@pytest_asyncio.fixture
async def client(env_with_test_db: Path):
    from api.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

