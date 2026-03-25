"""Test fixtures and configuration for API tests."""

import json
from collections.abc import Generator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from chatgpt_archive import db


MEDIA_CONVERSATION_ID = "68e06336-bce4-8330-b350-f7a33ffac85e"
MEDIA_IMAGE_FILE_ID = "file_000000004f48620a9bfb06ccaa684b65"
MEDIA_AUDIO_FILE_ID = "file_00000000aaaaaaaaaaaaaaaaaaaaaaaa"
MEDIA_ROOT_FILE_ID = "file-4Vdhhbs7F48DZfbPKwk1PN"


@pytest.fixture(scope="session")
def sample_conversations_data() -> list[dict]:
    """Sample conversation data for testing."""
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
                        "content": {
                            "parts": ["Hello, how are you?"],
                            "content_type": "text",
                        },
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
                        "content": {
                            "parts": ["What is Python?"],
                            "content_type": "text",
                        },
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
                                "Machine learning is a subset of AI that enables"
                                " computers to learn from data."
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
    """Create a temporary database path for testing."""
    db_path = tmp_path / "test_chats.db"
    yield db_path


@pytest.fixture
def initialized_db(temp_db_path: Path) -> Generator[Path, None, None]:
    """Initialize an empty database for testing."""
    conn = db.init_db(temp_db_path)
    conn.close()
    yield temp_db_path


@pytest.fixture
def populated_db(
    temp_db_path: Path, sample_conversations_data: list[dict]
) -> Generator[Path, None, None]:
    """Create a database populated with sample conversations."""
    conn = db.init_db(temp_db_path)

    for conv in sample_conversations_data:
        # Insert conversation
        cursor = conn.execute(
            """
            INSERT INTO conversations (openai_id, title, create_time, update_time)
            VALUES (?, ?, ?, ?)
            """,
            (conv["id"], conv["title"], conv["create_time"], conv["update_time"]),
        )
        conv_db_id = cursor.lastrowid

        # Insert messages from mapping
        for msg_id, msg_data in conv["mapping"].items():
            if msg_data.get("message"):
                msg = msg_data["message"]
                content_parts = msg.get("content", {}).get("parts", [])
                content = content_parts[0] if content_parts else ""
                role = msg.get("author", {}).get("role", "user")

                conn.execute(
                    """
                    INSERT INTO messages
                        (conversation_id, openai_id, parent_id, author_role, content, create_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conv_db_id,
                        msg_id,
                        msg_data.get("parent"),
                        role,
                        content,
                        msg.get("create_time"),
                    ),
                )

    conn.commit()
    conn.close()
    yield temp_db_path


@pytest.fixture
def sample_archive_dir(tmp_path: Path, sample_conversations_data: list[dict]) -> Path:
    """Create a sample archive directory with conversations.json."""
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()

    conversations_file = archive_dir / "conversations.json"
    conversations_file.write_text(json.dumps(sample_conversations_data))

    # Create minimal user.json
    user_file = archive_dir / "user.json"
    user_file.write_text(json.dumps({"id": "test-user", "email": "test@example.com"}))

    image_dir = archive_dir / MEDIA_CONVERSATION_ID / "image"
    image_dir.mkdir(parents=True)
    (image_dir / f"{MEDIA_IMAGE_FILE_ID}-sample-image.jpg").write_bytes(b"fake-jpeg")

    audio_dir = archive_dir / MEDIA_CONVERSATION_ID / "audio"
    audio_dir.mkdir(parents=True)
    (audio_dir / f"{MEDIA_AUDIO_FILE_ID}-sample-audio.wav").write_bytes(b"RIFFfake")

    (archive_dir / f"{MEDIA_ROOT_FILE_ID}-Sample Document.pdf").write_bytes(b"%PDF-1.4")

    return archive_dir


@pytest.fixture
def sample_archive_zip(sample_archive_dir: Path, tmp_path: Path) -> Path:
    """Create a ZIP file from the sample archive directory."""
    import zipfile

    zip_path = tmp_path / "test_archive.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sample_archive_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(sample_archive_dir)
                zf.write(file, arcname)

    return zip_path


@pytest.fixture
def env_with_test_db(populated_db: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Set environment to use test database."""
    monkeypatch.setenv("CHATGPT_ARCHIVE_DB", str(populated_db))
    monkeypatch.setenv("DB_PATH", str(populated_db))
    monkeypatch.setenv("DISABLE_RATE_LIMIT", "1")
    return populated_db


@pytest.fixture
def media_db_path(tmp_path: Path) -> Path:
    """Create a database with one conversation containing media asset pointers."""
    db_path = tmp_path / "media_test.db"
    conn = db.init_db(db_path)

    cursor = conn.execute(
        """
        INSERT INTO conversations (openai_id, title, create_time, update_time)
        VALUES (?, ?, ?, ?)
        """,
        (MEDIA_CONVERSATION_ID, "Media Conversation", 1701000000.0, 1701000100.0),
    )
    conv_db_id = cursor.lastrowid

    conn.execute(
        """
        INSERT INTO messages (conversation_id, openai_id, parent_id, author_role, content, create_time)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            conv_db_id,
            "msg-media-001",
            None,
            "assistant",
            "Lead text\n"
            + str(
                {
                    "content_type": "image_asset_pointer",
                    "asset_pointer": f"sediment://{MEDIA_IMAGE_FILE_ID}",
                    "size_bytes": 1234,
                    "width": 640,
                    "height": 480,
                }
            )
            + "\nMiddle text\n"
            + str(
                {
                    "content_type": "image_asset_pointer",
                    "asset_pointer": f"file-service://{MEDIA_ROOT_FILE_ID}",
                    "size_bytes": 2048,
                }
            )
            + "\n"
            + str(
                {
                    "content_type": "audio_asset_pointer",
                    "asset_pointer": f"sediment://{MEDIA_AUDIO_FILE_ID}",
                    "size_bytes": 4096,
                }
            ),
            1701000000.0,
        ),
    )

    conn.execute(
        """
        INSERT INTO messages (conversation_id, openai_id, parent_id, author_role, content, create_time)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            conv_db_id,
            "msg-media-002",
            "msg-media-001",
            "assistant",
            str(
                {
                    "content_type": "image_asset_pointer",
                    "asset_pointer": "sediment://file_00000000missingmissingmissing",
                    "size_bytes": 5,
                }
            ),
            1701000200.0,
        ),
    )

    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def env_with_media_db(
    media_db_path: Path,
    sample_archive_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    """Set environment to use the media-capable test database and archive."""
    monkeypatch.setenv("CHATGPT_ARCHIVE_DB", str(media_db_path))
    monkeypatch.setenv("DB_PATH", str(media_db_path))
    monkeypatch.setenv("CHATGPT_ARCHIVE_DIR", str(sample_archive_dir))
    monkeypatch.setenv("DISABLE_RATE_LIMIT", "1")
    return media_db_path


@pytest_asyncio.fixture
async def media_client(env_with_media_db: Path):
    """Async test client configured for media fixtures."""
    from api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def client(env_with_test_db: Path):
    """Create an async test client for the API.

    Note: Import app inside fixture to ensure env is set first.
    """
    # Import here to ensure environment variables are set
    from api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sync_client(env_with_test_db: Path):
    """Create a synchronous test client for the API."""
    from fastapi.testclient import TestClient

    from api.main import app

    return TestClient(app)
