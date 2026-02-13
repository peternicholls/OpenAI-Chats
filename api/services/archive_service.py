"""Archive service adapter — thin wrapper around the chatgpt_archive library.

This adapter provides the API layer with access to all chatgpt_archive
functionality without duplicating business logic (per FR-012).
"""

import logging
import os
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from chatgpt_archive import db
from chatgpt_archive import search as search_module
from chatgpt_archive import importer


logger = logging.getLogger(__name__)


# Expected schema definitions for validation
EXPECTED_SCHEMA = {
    "conversations": {
        "id": "INTEGER",
        "openai_id": "TEXT",
        "title": "TEXT",
        "create_time": "REAL",
        "update_time": "REAL",
        "model_slug": "TEXT",
    },
    "messages": {
        "id": "INTEGER",
        "conversation_id": "INTEGER",
        "openai_id": "TEXT",
        "author_role": "TEXT",
        "content": "TEXT",
        "create_time": "REAL",
    },
    "embeddings": {
        "id": "INTEGER",
        "message_id": "INTEGER",
        "embedding": "BLOB",
    },
}


def validate_schema_compatibility(conn: sqlite3.Connection) -> tuple[bool, list[str]]:
    """Validate SQLite schema has required tables and columns.

    Args:
        conn: Database connection to validate

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    for table_name, expected_columns in EXPECTED_SCHEMA.items():
        # Check table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        if cursor.fetchone() is None:
            if table_name == "embeddings":
                # embeddings table is optional (created when first embedding is generated)
                continue
            errors.append(f"Missing required table: {table_name}")
            continue

        # Check columns exist
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {row[1]: row[2].upper() for row in cursor.fetchall()}

        for col_name, expected_type in expected_columns.items():
            if col_name not in existing_columns:
                errors.append(f"Missing column: {table_name}.{col_name}")
            # Type checking is lenient - SQLite uses type affinity
            # Just verify column exists, not strict type matching

    return len(errors) == 0, errors


# In-memory import progress state
_import_progress: dict[str, Any] = {
    "status": "idle",
    "current": 0,
    "total": 0,
    "percent": 0.0,
    "message": None,
}


def get_db_path() -> Path:
    """Get the database path from environment or default."""
    return db.get_db_path()


def get_connection(validate: bool = True) -> sqlite3.Connection:
    """Get a database connection with schema initialized.

    Args:
        validate: Whether to validate schema compatibility (default: True).
                  Set to False for initial import operations.

    Returns:
        SQLite connection with row factory set.

    Raises:
        RuntimeError: If schema validation fails.
    """
    conn = db.init_db(get_db_path())

    if validate:
        is_valid, errors = validate_schema_compatibility(conn)
        if not is_valid:
            conn.close()
            error_msg = "Database schema incompatible: " + "; ".join(errors)
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    return conn


def list_conversations(
    sort_by: str = "date",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
    tag_filter: str | None = None,
) -> tuple[list[dict], int]:
    """List conversations with pagination and optional tag filtering.

    Returns:
        Tuple of (list of conversation dicts, total count).
    """
    conn = get_connection()
    try:
        if tag_filter:
            rows, total = db.list_conversations_by_tag(
                conn, tag_filter, sort_by=sort_by, order=order, limit=limit, offset=offset
            )
        else:
            rows, total = db.list_conversations(
                conn, sort_by=sort_by, order=order, limit=limit, offset=offset
            )

        conversations = []
        for row in rows:
            openai_id = row["openai_id"]
            tags = db.get_conversation_tags(conn, openai_id)
            is_fav = _get_is_favorite(conn, row["id"])
            conversations.append(
                {
                    "id": openai_id,
                    "title": row["title"],
                    "create_time": row["create_time"],
                    "update_time": row["update_time"],
                    "message_count": row["message_count"],
                    "model": row["model_slug"],
                    "tags": tags,
                    "is_favorite": is_fav,
                }
            )
        return conversations, total
    finally:
        conn.close()


def get_conversation(conversation_id: str) -> dict | None:
    """Get a single conversation with all messages by OpenAI ID."""
    conn = get_connection()
    try:
        row = db.get_conversation_by_id(conn, conversation_id)
        if row is None:
            return None

        messages_rows = db.get_conversation_messages(conn, row["id"])
        tags = db.get_conversation_tags(conn, conversation_id)
        is_fav = _get_is_favorite(conn, row["id"])

        messages = [
            {
                "id": msg["openai_id"],
                "role": msg["author_role"],
                "content": msg["content"],
                "create_time": msg["create_time"],
            }
            for msg in messages_rows
        ]

        return {
            "id": row["openai_id"],
            "title": row["title"],
            "create_time": row["create_time"],
            "update_time": row["update_time"],
            "message_count": row["message_count"],
            "model": row["model_slug"],
            "messages": messages,
            "tags": tags,
            "is_favorite": is_fav,
        }
    finally:
        conn.close()


def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation by its OpenAI ID."""
    conn = get_connection()
    try:
        return db.delete_conversation(conn, conversation_id)
    finally:
        conn.close()


def search_conversations(
    query: str,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 20,
    offset: int = 0,
    search_type: str = "keyword",
) -> dict:
    """Search conversations using keyword, semantic, or hybrid search.

    Returns:
        Dict with total, items list of search results.
    """
    conn = get_connection()
    try:
        fetch_limit = limit + offset

        if search_type == "semantic":
            results = search_module.execute_semantic_search(
                conn, query, from_date=from_date, to_date=to_date, limit=fetch_limit
            )
        elif search_type == "hybrid":
            results = search_module.execute_hybrid_search(
                conn, query, from_date=from_date, to_date=to_date, limit=fetch_limit
            )
        else:
            results = search_module.execute_search(
                conn, query, from_date=from_date, to_date=to_date, limit=fetch_limit
            )

        items = [
            {
                "conversation_id": r.openai_id,
                "title": r.title,
                "create_time": r.create_time,
                "match_count": r.match_count,
                "preview": r.preview,
                "relevance_score": r.relevance_score,
            }
            for r in results.results
        ]
        paged_items = items[offset : offset + limit]

        return {
            "total": results.total_results,
            "offset": offset,
            "limit": limit,
            "items": paged_items,
        }
    finally:
        conn.close()


def import_archive_from_zip(zip_path: str) -> None:
    """Import a ChatGPT archive from a ZIP file.

    Extracts the ZIP to a temp directory and runs the importer.
    Updates global _import_progress during import.
    """
    global _import_progress
    _import_progress = {
        "status": "processing",
        "current": 0,
        "total": 0,
        "percent": 0.0,
        "message": "Starting import...",
    }

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Extract ZIP
            _import_progress["message"] = "Extracting archive..."
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmpdir_path)

            # Find the conversations.json - might be in a subdirectory
            archive_dir = tmpdir_path
            if not (archive_dir / "conversations.json").exists():
                # Check one level deep
                for child in archive_dir.iterdir():
                    if child.is_dir() and (child / "conversations.json").exists():
                        archive_dir = child
                        break

            def progress_callback(current: int, total: int) -> None:
                global _import_progress
                pct = (current / total * 100) if total > 0 else 0
                _import_progress = {
                    "status": "processing",
                    "current": current,
                    "total": total,
                    "percent": round(pct, 1),
                    "message": f"Importing conversation {current}/{total}...",
                }

            convs, msgs = importer.import_archive(
                archive_dir,
                db_path=get_db_path(),
                progress_callback=progress_callback,
            )

            _import_progress = {
                "status": "complete",
                "current": convs,
                "total": convs,
                "percent": 100.0,
                "message": f"Imported {convs} conversations with {msgs} messages.",
            }

    except Exception as e:
        _import_progress = {
            "status": "error",
            "current": 0,
            "total": 0,
            "percent": 0.0,
            "message": str(e),
        }
    finally:
        try:
            os.unlink(zip_path)
        except OSError:
            pass


def get_import_progress() -> dict[str, Any]:
    """Get current import progress state."""
    return dict(_import_progress)


def get_all_tags() -> list[dict]:
    """Get all tags with usage counts."""
    conn = get_connection()
    try:
        return db.list_all_tags(conn)
    finally:
        conn.close()


def get_tags_for_conversation(conversation_id: str) -> list[str]:
    """Get tags for a specific conversation."""
    conn = get_connection()
    try:
        return db.get_conversation_tags(conn, conversation_id)
    finally:
        conn.close()


def add_tag_to_conversation(conversation_id: str, tag_name: str) -> bool:
    """Add a tag to a conversation."""
    conn = get_connection()
    try:
        return db.add_tag(conn, conversation_id, tag_name)
    finally:
        conn.close()


def remove_tag_from_conversation(conversation_id: str, tag_name: str) -> bool:
    """Remove a tag from a conversation."""
    conn = get_connection()
    try:
        return db.remove_tag(conn, conversation_id, tag_name)
    finally:
        conn.close()


def toggle_favorite(conversation_id: str) -> bool:
    """Toggle the favorite status of a conversation.

    Returns:
        New favorite status (True if now favorited).
    """
    conn = get_connection()
    try:
        row = db.get_conversation_by_id(conn, conversation_id)
        if row is None:
            return False

        # Check if is_favorite column exists; add it if not
        _ensure_favorite_column(conn)

        current = conn.execute(
            "SELECT is_favorite FROM conversations WHERE id = ?", (row["id"],)
        ).fetchone()
        new_val = 0 if (current and current[0]) else 1

        conn.execute(
            "UPDATE conversations SET is_favorite = ? WHERE id = ?", (new_val, row["id"])
        )
        conn.commit()
        return bool(new_val)
    finally:
        conn.close()


def list_favorites(
    sort_by: str = "date", order: str = "desc", limit: int = 50, offset: int = 0
) -> tuple[list[dict], int]:
    """List favorited conversations."""
    conn = get_connection()
    try:
        _ensure_favorite_column(conn)

        sort_map = {"date": "c.create_time", "title": "c.title", "messages": "message_count"}
        sort_column = sort_map.get(sort_by, "c.create_time")
        order_clause = "DESC" if order.lower() == "desc" else "ASC"
        null_handling = "NULLS LAST" if order_clause == "DESC" else "NULLS FIRST"

        total = conn.execute(
            "SELECT COUNT(*) FROM conversations WHERE is_favorite = 1"
        ).fetchone()[0]

        query = f"""
            SELECT c.id, c.openai_id, c.title, c.create_time, c.update_time,
                   c.model_slug, c.is_archived,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
            FROM conversations c
            WHERE c.is_favorite = 1
            ORDER BY {sort_column} {order_clause} {null_handling}
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query, (limit, offset)).fetchall()

        conversations = []
        for row in rows:
            openai_id = row["openai_id"]
            tags = db.get_conversation_tags(conn, openai_id)
            conversations.append(
                {
                    "id": openai_id,
                    "title": row["title"],
                    "create_time": row["create_time"],
                    "update_time": row["update_time"],
                    "message_count": row["message_count"],
                    "model": row["model_slug"],
                    "tags": tags,
                    "is_favorite": True,
                }
            )
        return conversations, total
    finally:
        conn.close()


def export_conversation(conversation_id: str, format: str) -> tuple[str | bytes, str, str]:
    """Export a conversation in the specified format.

    Returns:
        Tuple of (content, content_type, filename).
    """
    from chatgpt_archive.exporters import markdown, json_export, yaml_export
    from chatgpt_archive.exporters import html as html_export
    from chatgpt_archive.exporters import xml_export as xml_exp
    from chatgpt_archive.exporters import csv_export
    from chatgpt_archive.exporters import excel_export

    conv_data = get_conversation(conversation_id)
    if conv_data is None:
        raise ValueError(f"Conversation {conversation_id} not found")

    # Build conversation dict and messages list for exporters
    conv_dict = {
        "id": conv_data["id"],
        "title": conv_data["title"],
        "create_time": conv_data["create_time"],
        "update_time": conv_data["update_time"],
        "model": conv_data["model"],
        "message_count": conv_data["message_count"],
    }
    messages = conv_data["messages"]
    safe_title = (conv_data["title"] or "untitled").replace("/", "_").replace(" ", "_")[:50]

    format_map = {
        "md": (markdown.MarkdownExporter, "text/markdown", f"{safe_title}.md"),
        "json": (json_export.JSONExporter, "application/json", f"{safe_title}.json"),
        "yaml": (yaml_export.YAMLExporter, "application/x-yaml", f"{safe_title}.yaml"),
        "html": (html_export.HTMLExporter, "text/html", f"{safe_title}.html"),
        "xml": (xml_exp.XMLExporter, "application/xml", f"{safe_title}.xml"),
        "csv": (csv_export.CSVExporter, "text/csv", f"{safe_title}.csv"),
    }

    if format == "xlsx":
        exporter = excel_export.ExcelExporter()
        content = exporter.export(conv_dict, messages)
        return (
            content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            f"{safe_title}.xlsx",
        )

    if format not in format_map:
        raise ValueError(f"Unsupported export format: {format}")

    exporter_cls, content_type, filename = format_map[format]
    exporter = exporter_cls()
    content = exporter.export(conv_dict, messages)
    return content, content_type, filename


def _ensure_favorite_column(conn: sqlite3.Connection) -> None:
    """Ensure the is_favorite column exists on conversations table."""
    try:
        conn.execute("SELECT is_favorite FROM conversations LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE conversations ADD COLUMN is_favorite INTEGER DEFAULT 0")
        conn.commit()


def _get_is_favorite(conn: sqlite3.Connection, db_id: int) -> bool:
    """Check if a conversation is favorited."""
    try:
        row = conn.execute(
            "SELECT is_favorite FROM conversations WHERE id = ?", (db_id,)
        ).fetchone()
        return bool(row and row["is_favorite"])
    except sqlite3.OperationalError:
        return False
