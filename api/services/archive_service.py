"""Archive service adapter — thin wrapper around the chatgpt_archive library.

This adapter provides the API layer with access to all chatgpt_archive
functionality without duplicating business logic (per FR-012).
"""

import logging
import os
import sqlite3
import tempfile
import threading
import zipfile
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from chatgpt_archive import db, importer
from chatgpt_archive import search as search_module

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

        for col_name, _expected_type in expected_columns.items():
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

# In-memory embedding progress state
_embedding_progress: dict[str, Any] = {
    "status": "idle",
    "current": 0,
    "total": 0,
    "percent": 0.0,
    "message": None,
}

# Cancellation flag for embedding generation (threading.Event for thread safety)
_embedding_cancelled: threading.Event = threading.Event()


def get_db_path() -> Path:
    """Get the database path from environment or default."""
    return db.get_db_path()


def _progress_state_path() -> Path:
    """Return path to the progress state persistence file."""
    return db.get_db_path().parent / "progress_state.json"


def _persist_progress_state() -> None:
    """Write current progress dicts to disk so restarts can recover last state."""
    try:
        path = _progress_state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        import json as _json
        with open(path, "w", encoding="utf-8") as f:
            _json.dump(
                {"import": _import_progress, "embedding": _embedding_progress},
                f,
            )
    except Exception as e:
        logger.warning("Failed to persist progress state: %s", e)


def load_persisted_progress() -> None:
    """Load persisted progress state on startup.

    If any job was in 'processing' state when the server last stopped, mark it
    as 'error' (interrupted) rather than showing a misleading 'idle' status.
    Called once from the FastAPI lifespan startup handler.
    """
    global _import_progress, _embedding_progress
    import json as _json

    path = _progress_state_path()
    if not path.exists():
        return

    try:
        stored = _json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Could not load persisted progress state: %s", e)
        return

    for key, target in (("import", "_import_progress"), ("embedding", "_embedding_progress")):
        state = stored.get(key)
        if not isinstance(state, dict):
            continue
        if state.get("status") in ("processing", "pending"):
            state = {**state, "status": "error", "message": "Server restarted — job interrupted"}
        if key == "import":
            _import_progress = state
        else:
            _embedding_progress = state

    logger.info("Loaded persisted progress state from %s", path)


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

        if not rows:
            return [], total

        # Batch-fetch all tags for returned conversations in one query (fixes N+1)
        conv_db_ids = [row["id"] for row in rows]
        placeholders = ",".join("?" * len(conv_db_ids))
        tag_map: dict[int, list[str]] = {row["id"]: [] for row in rows}
        tag_rows = conn.execute(
            f"""
            SELECT ct.conversation_id, t.name
            FROM conversation_tags ct
            JOIN tags t ON ct.tag_id = t.id
            WHERE ct.conversation_id IN ({placeholders})
            ORDER BY t.name
            """,
            conv_db_ids,
        ).fetchall()
        for r in tag_rows:
            tag_map[r[0]].append(r[1])

        conversations = []
        for row in rows:
            conversations.append(
                {
                    "id": row["openai_id"],
                    "title": row["title"],
                    "create_time": row["create_time"],
                    "update_time": row["update_time"],
                    "message_count": row["message_count"],
                    "model": row["model_slug"],
                    "tags": tag_map.get(row["id"], []),
                    "is_favorite": bool(row["is_favorite"]),
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
        is_fav = bool(
            conn.execute(
                "SELECT is_favorite FROM conversations WHERE id = ?", (row["id"],)
            ).fetchone()["is_favorite"]
        )

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
    _persist_progress_state()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Extract ZIP — validate paths to prevent ZIP Slip (path traversal)
            _import_progress["message"] = "Extracting archive..."
            with zipfile.ZipFile(zip_path, "r") as zf:
                resolved_tmpdir = tmpdir_path.resolve()
                for member in zf.namelist():
                    member_path = (tmpdir_path / member).resolve()
                    if not member_path.is_relative_to(resolved_tmpdir):
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid archive: path traversal detected",
                        )
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
            _persist_progress_state()

    except Exception as e:
        _import_progress = {
            "status": "error",
            "current": 0,
            "total": 0,
            "percent": 0.0,
            "message": str(e),
        }
        _persist_progress_state()
    finally:
        try:
            os.unlink(zip_path)
        except OSError as e:
            logger.warning("Failed to clean up temp file %s: %s", zip_path, e)


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


def rename_tag(old_name: str, new_name: str) -> bool:
    """Rename a tag across all conversations.

    Returns:
        True if the tag was found and renamed, False if not found.
    """
    conn = get_connection()
    try:
        return db.rename_tag(conn, old_name, new_name)
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

        current = conn.execute(
            "SELECT is_favorite FROM conversations WHERE id = ?", (row["id"],)
        ).fetchone()
        new_val = 0 if (current and current[0]) else 1

        conn.execute("UPDATE conversations SET is_favorite = ? WHERE id = ?", (new_val, row["id"]))
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
        sort_map = {"date": "c.create_time", "title": "c.title", "messages": "message_count"}
        sort_column = sort_map.get(sort_by, "c.create_time")
        order_clause = "DESC" if order.lower() == "desc" else "ASC"
        null_handling = "NULLS LAST" if order_clause == "DESC" else "NULLS FIRST"

        total = conn.execute("SELECT COUNT(*) FROM conversations WHERE is_favorite = 1").fetchone()[
            0
        ]

        # Safe: sort_column, order_clause, null_handling are from hardcoded maps
        query = f"""
            SELECT c.id, c.openai_id, c.title, c.create_time, c.update_time,
                   c.model_slug, c.is_archived,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
            FROM conversations c
            WHERE c.is_favorite = 1
            ORDER BY {sort_column} {order_clause} {null_handling}
            LIMIT ? OFFSET ?
        """  # noqa: S608
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
    from chatgpt_archive.exporters import (
        csv_export,
        excel_export,
        json_export,
        markdown,
        yaml_export,
    )
    from chatgpt_archive.exporters import html as html_export
    from chatgpt_archive.exporters import xml_export as xml_exp

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
        content = exporter.export_bytes(conv_dict, messages)
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


def export_multiple_conversations(
    conversation_ids: list[str], format: str
) -> tuple[str | bytes, str, str]:
    """Export multiple conversations in the specified format as a combined file.

    Returns:
        Tuple of (content, content_type, filename).
    """
    from chatgpt_archive.exporters import (
        csv_export,
        excel_export,
        json_export,
        markdown,
        yaml_export,
    )
    from chatgpt_archive.exporters import html as html_export
    from chatgpt_archive.exporters import xml_export as xml_exp

    if not conversation_ids:
        raise ValueError("No conversation IDs provided")

    # Collect all conversations — use a single DB connection for the entire batch
    conversations_data = []
    missing_ids = []
    conn = get_connection()
    try:
        for conv_id in conversation_ids:
            row = db.get_conversation_by_id(conn, conv_id)
            if row is None:
                missing_ids.append(conv_id)
                continue

            messages_rows = db.get_conversation_messages(conn, row["id"])
            tags = db.get_conversation_tags(conn, conv_id)
            is_fav = bool(
                conn.execute(
                    "SELECT is_favorite FROM conversations WHERE id = ?", (row["id"],)
                ).fetchone()["is_favorite"]
            )

            messages = [
                {
                    "id": msg["openai_id"],
                    "role": msg["author_role"],
                    "content": msg["content"],
                    "create_time": msg["create_time"],
                }
                for msg in messages_rows
            ]

            conversations_data.append({
                "id": row["openai_id"],
                "title": row["title"],
                "create_time": row["create_time"],
                "update_time": row["update_time"],
                "message_count": row["message_count"],
                "model": row["model_slug"],
                "messages": messages,
                "tags": tags,
                "is_favorite": is_fav,
            })
    finally:
        conn.close()

    if missing_ids:
        raise ValueError(f"Conversations not found: {', '.join(missing_ids)}")

    if not conversations_data:
        raise ValueError("No valid conversations to export")

    # Build combined content based on format
    timestamp = int(conversations_data[0]["create_time"] or 0)
    filename_base = f"export_{len(conversations_data)}_conversations"

    format_info = {
        "md": ("text/markdown", f"{filename_base}.md"),
        "json": ("application/json", f"{filename_base}.json"),
        "yaml": ("application/x-yaml", f"{filename_base}.yaml"),
        "html": ("text/html", f"{filename_base}.html"),
        "xml": ("application/xml", f"{filename_base}.xml"),
        "csv": ("text/csv", f"{filename_base}.csv"),
        "xlsx": (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            f"{filename_base}.xlsx",
        ),
    }

    if format not in format_info:
        raise ValueError(f"Unsupported export format: {format}")

    content_type, filename = format_info[format]

    # Export each conversation and combine
    if format == "json":
        import json

        combined = []
        for conv_data in conversations_data:
            conv_dict = {
                "id": conv_data["id"],
                "title": conv_data["title"],
                "create_time": conv_data["create_time"],
                "update_time": conv_data["update_time"],
                "model": conv_data["model"],
                "messages": conv_data["messages"],
            }
            combined.append(conv_dict)
        content = json.dumps(combined, indent=2, ensure_ascii=False)

    elif format == "md":
        parts = []
        exporter = markdown.MarkdownExporter()
        for conv_data in conversations_data:
            conv_dict = _build_conv_dict(conv_data)
            parts.append(exporter.export(conv_dict, conv_data["messages"]))
        content = "\n\n---\n\n".join(parts)

    elif format == "yaml":
        import yaml

        combined = []
        for conv_data in conversations_data:
            conv_dict = {
                "id": conv_data["id"],
                "title": conv_data["title"],
                "create_time": conv_data["create_time"],
                "update_time": conv_data["update_time"],
                "model": conv_data["model"],
                "messages": conv_data["messages"],
            }
            combined.append(conv_dict)
        content = yaml.dump(combined, allow_unicode=True, default_flow_style=False)

    elif format == "html":
        parts = []
        for conv_data in conversations_data:
            exporter = html_export.HTMLExporter()
            conv_dict = _build_conv_dict(conv_data)
            parts.append(exporter.export(conv_dict, conv_data["messages"]))
        content = "\n<hr/>\n".join(parts)

    elif format == "xml":
        parts = ["<?xml version='1.0' encoding='UTF-8'?>\n<conversations>"]
        for conv_data in conversations_data:
            exporter = xml_exp.XMLExporter()
            conv_dict = _build_conv_dict(conv_data)
            xml_content = exporter.export(conv_dict, conv_data["messages"])
            # Remove XML declaration from individual exports
            if xml_content.startswith("<?xml"):
                xml_content = xml_content.split("?>", 1)[-1].strip()
            parts.append(xml_content)
        parts.append("</conversations>")
        content = "\n".join(parts)

    elif format == "csv":
        import csv
        import io
        from chatgpt_archive.exporters.base import BaseExporter

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["conversation_id", "title", "role", "content", "create_time"]
        )
        for conv_data in conversations_data:
            for msg in conv_data["messages"]:
                writer.writerow(
                    [
                        BaseExporter.sanitize_spreadsheet_cell(conv_data["id"]),
                        BaseExporter.sanitize_spreadsheet_cell(conv_data["title"]),
                        BaseExporter.sanitize_spreadsheet_cell(msg["role"]),
                        BaseExporter.sanitize_spreadsheet_cell(msg["content"]),
                        BaseExporter.sanitize_spreadsheet_cell(msg.get("create_time", "")),
                    ]
                )
        content = output.getvalue()

    elif format == "xlsx":
        # For Excel, combine all messages with conversation context
        exporter = excel_export.ExcelExporter()
        # Create combined data structure
        all_messages = []
        for conv_data in conversations_data:
            for msg in conv_data["messages"]:
                msg_with_context = dict(msg)
                msg_with_context["conversation_id"] = conv_data["id"]
                msg_with_context["conversation_title"] = conv_data["title"]
                all_messages.append(msg_with_context)
        combined_conv = {
            "id": "combined",
            "title": f"{len(conversations_data)} Conversations",
            "create_time": timestamp,
            "update_time": timestamp,
            "model": "various",
            "message_count": len(all_messages),
        }
        content = exporter.export_bytes(combined_conv, all_messages)

    return content, content_type, filename


def _build_conv_dict(conv_data: dict) -> dict:
    """Build a conversation dict for exporters."""
    return {
        "id": conv_data["id"],
        "title": conv_data["title"],
        "create_time": conv_data["create_time"],
        "update_time": conv_data["update_time"],
        "model": conv_data["model"],
        "message_count": conv_data["message_count"],
    }


def get_embedding_progress() -> dict[str, Any]:
    """Get current embedding generation progress state."""
    return dict(_embedding_progress)


def update_embedding_progress(
    status: str,
    current: int = 0,
    total: int = 0,
    message: str | None = None,
) -> None:
    """Update embedding generation progress state."""
    global _embedding_progress
    pct = (current / total * 100) if total > 0 else 0.0
    _embedding_progress = {
        "status": status,
        "current": current,
        "total": total,
        "percent": round(pct, 1),
        "message": message,
    }
    _persist_progress_state()


def reset_embedding_progress() -> None:
    """Reset embedding progress to idle state."""
    global _embedding_progress
    _embedding_progress = {
        "status": "idle",
        "current": 0,
        "total": 0,
        "percent": 0.0,
        "message": None,
    }
    _embedding_cancelled.clear()
    _persist_progress_state()


def cancel_embedding_generation() -> bool:
    """Request cancellation of embedding generation.

    Returns:
        True if cancellation was requested, False if no embedding is in progress.
    """
    if _embedding_progress.get("status") in ("processing", "pending"):
        _embedding_cancelled.set()
        return True
    return False


def is_embedding_cancelled() -> bool:
    """Check if embedding generation has been cancelled."""
    return _embedding_cancelled.is_set()


def clear_embedding_cancellation() -> None:
    """Clear the cancellation flag."""
    _embedding_cancelled.clear()
