"""CLI interface for ChatGPT Archive Search & Export.

Commands:
    import   Import conversations from ChatGPT export archive
    search   Search conversations by keyword or phrase
    list     List all imported conversations
    view     View a specific conversation
    export   Export a conversation to file
"""

import json
import sys
from pathlib import Path

import click  # type: ignore[import-untyped]

from chatgpt_archive import __version__
from chatgpt_archive.db import (
    get_db_path,
    get_connection,
    get_db_size,
    get_conversation_by_id,
    get_conversation_messages,
    list_conversations as db_list_conversations,
    delete_conversation as db_delete_conversation,
    add_tag as db_add_tag,
    remove_tag as db_remove_tag,
    get_conversation_tags as db_get_tags,
    list_all_tags as db_list_all_tags,
    list_conversations_by_tag as db_list_by_tag,
)
from chatgpt_archive import importer
from chatgpt_archive.media import get_archive_media_dir, persist_archive_media
from chatgpt_archive.search import (
    execute_search,
    format_results_human,
    format_results_json,
    InvalidQueryError,
)


def get_db_option_path(db: str | None) -> Path:
    """Resolve database path from CLI option or environment/default.

    Args:
        db: CLI --db option value, or None

    Returns:
        Resolved database path
    """
    if db:
        return Path(db).expanduser()
    return get_db_path()


class AliasedGroup(click.Group):
    """Click group that supports command aliases."""

    def get_command(self, ctx, cmd_name):
        """Resolve command name, supporting aliases.

        Checks for an exact match first, then falls back to
        predefined aliases: ls→list, find→search, show→view.

        Args:
            ctx: Click context
            cmd_name: Command name entered by user

        Returns:
            Resolved Click command, or None if not found
        """
        # Check for exact match first
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        # Support common aliases
        aliases = {
            "ls": "list",
            "find": "search",
            "show": "view",
        }
        if cmd_name in aliases:
            return click.Group.get_command(self, ctx, aliases[cmd_name])
        return None


@click.group(cls=AliasedGroup)
@click.option(
    "--db",
    "-d",
    "--database",
    type=click.Path(),
    envvar="CHATGPT_ARCHIVE_DB",
    help="Database file path (default: ~/.chatgpt-archive/chats.db)",
)
@click.option("--json", "-j", "json_output", is_flag=True, help="Output in JSON format")
@click.version_option(version=__version__, prog_name="chatgpt-archive")
@click.pass_context
def main(ctx: click.Context, db: str | None, json_output: bool) -> None:
    """ChatGPT Archive Search & Export - manage your ChatGPT conversation history.

    Import your ChatGPT export, search through conversations, view them,
    and export to various formats (Markdown, JSON, YAML, HTML, XML).

    \b
    Examples:
        chatgpt-archive import ./chatgpt-export/
        chatgpt-archive search "machine learning"
        chatgpt-archive view <conversation-id>
        chatgpt-archive export <id> -f md -o chat.md
    """
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = get_db_option_path(db)
    ctx.obj["json_output"] = json_output


@main.command("import")  # type: ignore[attr-defined]
@click.argument("archive_dir", type=click.Path(exists=True, file_okay=False))
@click.pass_context
def import_archive(ctx: click.Context, archive_dir: str) -> None:
    """Import conversations from ChatGPT export archive.

    ARCHIVE_DIR is the path to the extracted ChatGPT export directory
    containing conversations.json.

    \b
    Example:
        chatgpt-archive import ~/Downloads/chatgpt-export/
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]
    archive_path = Path(archive_dir)

    try:
        if not json_output:
            click.echo(f"Importing from {archive_path}...")

        # Progress tracking
        total = 0

        def progress_callback(current: int, total_count: int) -> None:
            nonlocal total
            total = total_count
            if not json_output and current % 100 == 0:
                click.echo(
                    f"  Processed {current}/{total_count} conversations...", err=True
                )

        # Run import
        conversations_imported, messages_imported = importer.import_archive(
            archive_path, db_path, progress_callback
        )
        media_dir = persist_archive_media(archive_path)

        # Get database size
        db_size = get_db_size(db_path)

        # Output results
        if json_output:
            result = {
                "status": "success",
                "conversations_imported": conversations_imported,
                "messages_imported": messages_imported,
                "database_path": str(db_path),
                "database_size_bytes": db_size,
                "archive_media_dir": str(media_dir),
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("\n✓ Import complete!")
            click.echo(f"  Conversations: {conversations_imported}")
            click.echo(f"  Messages: {messages_imported}")
            click.echo(f"  Database: {db_path} ({db_size / 1024 / 1024:.1f} MB)")
            click.echo(f"  Archive media: {media_dir}")

        sys.exit(0)

    except importer.InvalidArchiveError as e:
        if json_output:
            error = {"status": "error", "error": "invalid_archive", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    except importer.InvalidJSONError as e:
        if json_output:
            error = {"status": "error", "error": "invalid_json", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(2)

    except Exception as e:
        if json_output:
            error = {"status": "error", "error": "import_failed", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: Import failed: {e}", err=True)
        sys.exit(3)


@main.command("verify-media")  # type: ignore[attr-defined]
@click.argument(
    "archive_dir", type=click.Path(exists=True, file_okay=False), required=False
)
@click.pass_context
def verify_media(ctx: click.Context, archive_dir: str | None) -> None:
    """Verify the configured archive media directory exists and is readable."""
    json_output = ctx.obj["json_output"]
    resolved_dir = (
        Path(archive_dir).expanduser()
        if archive_dir
        else get_archive_media_dir(db_path=ctx.obj["db_path"])
    )

    exists = resolved_dir.exists()
    conversations_json = (resolved_dir / "conversations.json").exists()
    root_files = (
        sum(1 for path in resolved_dir.glob("file-*") if path.is_file())
        if exists
        else 0
    )
    conversation_dirs = (
        sum(1 for path in resolved_dir.iterdir() if path.is_dir()) if exists else 0
    )

    payload = {
        "archive_media_dir": str(resolved_dir),
        "exists": exists,
        "has_conversations_json": conversations_json,
        "root_file_count": root_files,
        "conversation_dir_count": conversation_dirs,
    }

    if json_output:
        click.echo(json.dumps(payload, indent=2))
    else:
        click.echo(f"Archive media directory: {resolved_dir}")
        click.echo(f"  Exists: {'yes' if exists else 'no'}")
        click.echo(f"  conversations.json: {'yes' if conversations_json else 'no'}")
        click.echo(f"  Root files: {root_files}")
        click.echo(f"  Conversation directories: {conversation_dirs}")

    sys.exit(0 if exists else 1)


@main.command()  # type: ignore[attr-defined]
@click.argument("query")
@click.option(
    "--from", "from_date", help="Filter: conversations after date (YYYY-MM-DD)"
)
@click.option("--to", "to_date", help="Filter: conversations before date (YYYY-MM-DD)")
@click.option("--limit", "-l", default=20, help="Maximum results to return")
@click.option(
    "--semantic",
    is_flag=True,
    help="Use semantic (vector) search instead of keyword search",
)
@click.option(
    "--hybrid",
    is_flag=True,
    help="Combine keyword and semantic search for best results",
)
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    from_date: str | None,
    to_date: str | None,
    limit: int,
    semantic: bool,
    hybrid: bool,
) -> None:
    """Search conversations by keyword or phrase.

    QUERY is the search term. Supports FTS5 syntax for advanced queries.
    Use --semantic for meaning-based search or --hybrid to combine both.

    \b
    Examples:
        chatgpt-archive search "machine learning"
        chatgpt-archive search "python AND tutorial"
        chatgpt-archive search "error" --from 2024-01-01
        chatgpt-archive search "neural networks" --semantic
        chatgpt-archive search "AI concepts" --hybrid
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    # Check database exists
    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        try:
            if semantic or hybrid:
                # Use semantic/hybrid search
                try:
                    from chatgpt_archive.search import (
                        execute_semantic_search,
                        execute_hybrid_search,
                    )

                    if hybrid:
                        results = execute_hybrid_search(
                            conn, query, from_date, to_date, limit
                        )
                    else:
                        results = execute_semantic_search(
                            conn, query, from_date, to_date, limit
                        )
                except ImportError:
                    click.echo(
                        "Error: Semantic search requires 'chatgpt-archive[semantic]'. "
                        "Install with: pip install 'chatgpt-archive[semantic]'",
                        err=True,
                    )
                    sys.exit(1)
            else:
                results = execute_search(conn, query, from_date, to_date, limit)

            if json_output:
                click.echo(json.dumps(format_results_json(results), indent=2))
            else:
                click.echo(format_results_human(results))

            sys.exit(0)
        finally:
            conn.close()

    except InvalidQueryError as e:
        if json_output:
            error = {"status": "error", "error": "invalid_query", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(2)


@main.command()  # type: ignore[attr-defined]
@click.option(
    "--model",
    "-m",
    default="text-embedding-3-small",
    help="Embedding model to use (default: text-embedding-3-small)",
)
@click.option(
    "--batch-size", "-b", default=100, help="Messages per API batch (default: 100)"
)
@click.option(
    "--estimate", is_flag=True, help="Show cost estimate without generating embeddings"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def embed(
    ctx: click.Context, model: str, batch_size: int, estimate: bool, yes: bool
) -> None:
    """Generate vector embeddings for semantic search.

    Creates embeddings for all messages using OpenAI's embedding API.
    Requires OPENAI_API_KEY environment variable to be set.
    Supports resume - only embeds messages without existing embeddings.

    \b
    Examples:
        chatgpt-archive embed --estimate          # Show cost estimate
        chatgpt-archive embed                     # Generate embeddings (with confirmation)
        chatgpt-archive embed --yes               # Skip confirmation
        chatgpt-archive embed --model text-embedding-3-large
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    # Check database exists
    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        from chatgpt_archive.embeddings import (
            embed_messages,
            estimate_cost,
            EmbeddingProgress,
            APIKeyMissingError,
            EmbeddingError,
        )
        from chatgpt_archive.db import init_embeddings_schema
    except ImportError:
        click.echo(
            "Error: Semantic search requires additional packages. "
            "Install with: pip install 'chatgpt-archive[semantic]'",
            err=True,
        )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        init_embeddings_schema(conn)

        try:
            # Cost estimation
            cost_info = estimate_cost(conn, model)

            if cost_info["messages_to_embed"] == 0:
                if json_output:
                    click.echo(
                        json.dumps(
                            {
                                "status": "complete",
                                "message": "All messages already embedded",
                            }
                        )
                    )
                else:
                    click.echo("✓ All messages already have embeddings. Nothing to do.")
                sys.exit(0)

            if estimate or not yes:
                if json_output:
                    click.echo(json.dumps(cost_info, indent=2))
                    if estimate:
                        sys.exit(0)
                else:
                    click.echo("Embedding cost estimate:")
                    click.echo(
                        f"  Messages to embed: {cost_info['messages_to_embed']:,}"
                    )
                    click.echo(
                        f"  Estimated tokens:  {cost_info['estimated_tokens']:,}"
                    )
                    click.echo(f"  Model:             {cost_info['model']}")
                    click.echo(
                        f"  Estimated cost:    {cost_info['estimated_cost_display']}"
                    )
                    click.echo()

                    if estimate:
                        sys.exit(0)

                    if not yes:
                        if not click.confirm("Proceed with embedding generation?"):
                            click.echo("Aborted.")
                            sys.exit(0)

            # Progress callback
            last_percent = [0]

            def progress_callback(progress: EmbeddingProgress) -> None:
                if not json_output:
                    pct = int(progress.percent_complete)
                    if pct > last_percent[0] or pct == 0:
                        last_percent[0] = pct
                        click.echo(
                            f"\r  Embedding: {progress.completed:,}/{progress.total:,} "
                            f"({progress.percent_complete}%) "
                            f"- est. cost: ${progress.estimated_cost:.4f}",
                            nl=False,
                            err=True,
                        )

            # Generate embeddings
            if not json_output:
                click.echo("Generating embeddings...")

            result = embed_messages(
                conn,
                model=model,
                batch_size=batch_size,
                progress_callback=progress_callback,
            )

            if not json_output:
                click.echo()  # Newline after progress
                click.echo("\n✓ Embedding complete!")
                click.echo(
                    f"  Embedded:  {result.completed:,}/{result.total:,} messages"
                )
                click.echo(f"  Remaining: {result.remaining:,}")
                click.echo(f"  Tokens:    ~{result.tokens_used:,}")
                click.echo(f"  Cost:      ~${result.estimated_cost:.4f}")
            else:
                output = {
                    "status": "success",
                    "total": result.total,
                    "completed": result.completed,
                    "remaining": result.remaining,
                    "tokens_used": result.tokens_used,
                    "estimated_cost": result.estimated_cost,
                    "model": result.model,
                }
                click.echo(json.dumps(output, indent=2))

            sys.exit(0)

        finally:
            conn.close()

    except APIKeyMissingError as e:
        if json_output:
            error = {"status": "error", "error": "api_key_missing", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    except EmbeddingError as e:
        if json_output:
            error = {"status": "error", "error": "embedding_failed", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command("list")  # type: ignore[attr-defined]  # noqa: F811
@click.option(
    "--sort",
    "-s",
    type=click.Choice(["date", "title", "messages"]),
    default="date",
    help="Sort by field",
)
@click.option(
    "--order",
    "-o",
    type=click.Choice(["asc", "desc"]),
    default="desc",
    help="Sort order",
)
@click.option("--limit", "-l", default=50, help="Maximum results")
@click.option("--offset", default=0, help="Skip first N results (pagination)")
@click.option("--tag", "-t", help="Filter by tag name")
@click.pass_context
def list_conversations(
    ctx: click.Context, sort: str, order: str, limit: int, offset: int, tag: str | None
) -> None:
    """List all imported conversations.

    \b
    Examples:
        chatgpt-archive list
        chatgpt-archive list --sort title --order asc
        chatgpt-archive list --limit 10 --offset 20
        chatgpt-archive list --tag important
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    # Check database exists
    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        try:
            if tag:
                conversations, total = db_list_by_tag(
                    conn,
                    tag_name=tag,
                    sort_by=sort,
                    order=order,
                    limit=limit,
                    offset=offset,
                )
            else:
                conversations, total = db_list_conversations(
                    conn, sort_by=sort, order=order, limit=limit, offset=offset
                )

            if json_output:
                _list_json(conversations, total, offset, limit)
            else:
                if tag:
                    click.echo(f"Tag: {tag}")
                _list_human(conversations, total, offset, limit)

            sys.exit(0)

        finally:
            conn.close()

    except Exception as e:
        if json_output:
            error = {"status": "error", "error": "list_failed", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _list_human(conversations, total: int, offset: int, limit: int) -> None:
    """Display conversation list in human-readable format.

    Args:
        conversations: List of conversation Row objects
        total: Total number of conversations
        offset: Current pagination offset
        limit: Current pagination limit
    """
    if total == 0:
        click.echo("No conversations found. Run 'chatgpt-archive import' first.")
        return

    click.echo(f"{total:,} conversations")
    click.echo()

    for conv in conversations:
        title = conv["title"] or "[Untitled]"
        date_str = _format_date(conv["create_time"])
        msg_count = conv["message_count"]
        conv_id = conv["openai_id"]

        click.echo(f"[{date_str}] {title} ({msg_count} messages)")
        click.echo(f"  ID: {conv_id}")
        click.echo()

    # Pagination info
    showing_end = min(offset + len(conversations), total)
    showing_start = offset + 1 if conversations else 0
    click.echo(f"(showing {showing_start}-{showing_end} of {total:,})")


def _list_json(conversations, total: int, offset: int, limit: int) -> None:
    """Display conversation list in JSON format.

    Args:
        conversations: List of conversation Row objects
        total: Total number of conversations
        offset: Current pagination offset
        limit: Current pagination limit
    """
    result = {
        "total": total,
        "offset": offset,
        "limit": limit,
        "conversations": [
            {
                "id": conv["openai_id"],
                "title": conv["title"],
                "create_time": conv["create_time"],
                "update_time": conv["update_time"],
                "message_count": conv["message_count"],
                "model": conv["model_slug"],
            }
            for conv in conversations
        ],
    }
    click.echo(json.dumps(result, indent=2))


@main.command()  # type: ignore[attr-defined]
@click.argument("conversation_id")
@click.pass_context
def view(ctx: click.Context, conversation_id: str) -> None:
    """View a specific conversation.

    CONVERSATION_ID is the OpenAI conversation ID (shown in search/list output).

    \b
    Example:
        chatgpt-archive view 6974cc29-45d8-8327-a6dc-ef1ef0a82f46
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    # Check database exists
    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        try:
            # Retrieve conversation
            conv = get_conversation_by_id(conn, conversation_id)

            if conv is None:
                if json_output:
                    error = {
                        "status": "error",
                        "error": "conversation_not_found",
                        "message": f"Conversation not found: {conversation_id}",
                    }
                    click.echo(json.dumps(error), err=True)
                else:
                    click.echo(
                        f"Error: Conversation not found: {conversation_id}", err=True
                    )
                sys.exit(2)

            # Retrieve messages
            messages = get_conversation_messages(conn, conv["id"])

            if json_output:
                _view_json(conv, messages)
            else:
                _view_human(conv, messages)

            sys.exit(0)
        finally:
            conn.close()

    except Exception as e:
        if json_output:
            error = {"status": "error", "error": "view_failed", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(3)


def _format_timestamp(ts: float | None) -> str:
    """Format a unix timestamp for display.

    Args:
        ts: Unix timestamp or None

    Returns:
        Formatted datetime string or empty string
    """
    if ts is None:
        return ""
    from datetime import datetime, timezone

    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _format_date(ts: float | None) -> str:
    """Format a unix timestamp as date only.

    Args:
        ts: Unix timestamp or None

    Returns:
        Formatted date string or ""
    """
    if ts is None:
        return ""
    from datetime import datetime, timezone

    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def _format_time(ts: float | None) -> str:
    """Format a unix timestamp as time only.

    Args:
        ts: Unix timestamp or None

    Returns:
        Formatted time string or ""
    """
    if ts is None:
        return ""
    from datetime import datetime, timezone

    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%H:%M:%S")


def _view_human(conv, messages) -> None:
    """Display a conversation in human-readable format.

    For long conversations (1000+ messages), output is paginated
    using click's built-in pager.

    Args:
        conv: Conversation Row from database
        messages: List of message Rows
    """
    title = conv["title"] or "[Untitled]"
    created = _format_timestamp(conv["create_time"])
    model = conv["model_slug"] or "unknown"
    msg_count = conv["message_count"]

    lines = []
    lines.append(f"# {title}")
    lines.append(f"Created: {created} | Model: {model} | {msg_count} messages")
    lines.append("")

    for msg in messages:
        role = msg["author_role"]
        content = msg["content"] or ""
        time_str = _format_time(msg["create_time"])

        # Skip messages with no content (system placeholders)
        if not content.strip() and role == "system":
            continue

        lines.append("---")
        lines.append("")

        role_label = role.capitalize()
        if time_str:
            lines.append(f"**{role_label}** ({time_str}):")
        else:
            lines.append(f"**{role_label}**:")

        lines.append(content)
        lines.append("")

    output = "\n".join(lines)

    # Paginate for long conversations (1000+ messages)
    if len(messages) >= 1000:
        click.echo_via_pager(output)
    else:
        click.echo(output)


def _view_json(conv, messages) -> None:
    """Display a conversation in JSON format.

    Args:
        conv: Conversation Row from database
        messages: List of message Rows
    """
    result = {
        "id": conv["openai_id"],
        "title": conv["title"],
        "create_time": conv["create_time"],
        "update_time": conv["update_time"],
        "model": conv["model_slug"],
        "message_count": conv["message_count"],
        "messages": [
            {
                "id": msg["openai_id"],
                "role": msg["author_role"],
                "content": msg["content"],
                "create_time": msg["create_time"],
            }
            for msg in messages
        ],
    }
    click.echo(json.dumps(result, indent=2))


@main.command()  # type: ignore[attr-defined]
@click.argument("conversation_id")
@click.option(
    "--format",
    "-f",
    "fmt",
    required=True,
    type=click.Choice(["md", "json", "yaml", "html", "xml", "csv", "xlsx"]),
    help="Output format",
)
@click.option(
    "--output", "-o", type=click.Path(), help="Output file (stdout if not specified)"
)
@click.pass_context
def export(
    ctx: click.Context, conversation_id: str, fmt: str, output: str | None
) -> None:
    """Export a conversation to file.

    CONVERSATION_ID is the OpenAI conversation ID.

    \b
    Examples:
        chatgpt-archive export <id> -f md -o conversation.md
        chatgpt-archive export <id> -f json
        chatgpt-archive export <id> -f html -o chat.html
        chatgpt-archive export <id> -f csv -o chat.csv
        chatgpt-archive export <id> -f xlsx -o chat.xlsx
    """
    from chatgpt_archive.exporters import get_exporter

    db_path = ctx.obj["db_path"]

    # Check database exists
    if not db_path.exists():
        click.echo(
            "Error: Database not found. Run 'chatgpt-archive import' first.", err=True
        )
        sys.exit(1)

    # Get exporter
    exporter = get_exporter(fmt)
    if exporter is None:
        click.echo(f"Error: Invalid format: {fmt}", err=True)
        sys.exit(3)

    try:
        conn = get_connection(db_path)
        try:
            # Retrieve conversation
            conv = get_conversation_by_id(conn, conversation_id)

            if conv is None:
                click.echo(
                    f"Error: Conversation not found: {conversation_id}", err=True
                )
                sys.exit(2)

            # Retrieve messages
            messages = get_conversation_messages(conn, conv["id"])

            # Build conversation dict for exporter
            conv_dict = {
                "id": conv["openai_id"],
                "title": conv["title"],
                "create_time": conv["create_time"],
                "update_time": conv["update_time"],
                "model": conv["model_slug"],
                "message_count": conv["message_count"],
            }

            # Build messages list for exporter
            messages_list = [
                {
                    "id": msg["openai_id"],
                    "role": msg["author_role"],
                    "content": msg["content"],
                    "create_time": msg["create_time"],
                }
                for msg in messages
            ]

            # Export
            content = exporter.export(conv_dict, messages_list)

            # Write output
            if output:
                output_path = Path(output).expanduser()
                try:
                    # Excel format needs binary write
                    if fmt == "xlsx":
                        try:
                            raw_bytes = exporter.export_bytes(conv_dict, messages_list)
                            output_path.write_bytes(raw_bytes)
                        except AttributeError:
                            output_path.write_text(content, encoding="utf-8")
                    else:
                        output_path.write_text(content, encoding="utf-8")
                    click.echo(f"Exported to {output_path}", err=True)
                except IOError as e:
                    click.echo(f"Error: Failed to write file: {e}", err=True)
                    sys.exit(4)
            else:
                if fmt == "xlsx":
                    click.echo(
                        "Error: Excel format requires --output/-o option "
                        "(binary format cannot be written to stdout).",
                        err=True,
                    )
                    sys.exit(4)
                # Write to stdout
                click.echo(content)

            sys.exit(0)

        finally:
            conn.close()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)


@main.group()  # type: ignore[attr-defined]
@click.pass_context
def tag(ctx: click.Context) -> None:
    """Manage conversation tags.

    \b
    Examples:
        chatgpt-archive tag add <id> "important"
        chatgpt-archive tag remove <id> "important"
        chatgpt-archive tag show <id>
        chatgpt-archive tag list
    """
    pass


@tag.command("add")
@click.argument("conversation_id")
@click.argument("tag_name")
@click.pass_context
def tag_add(ctx: click.Context, conversation_id: str, tag_name: str) -> None:
    """Add a tag to a conversation.

    \b
    Example:
        chatgpt-archive tag add 6974cc29-... "important"
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        try:
            result = db_add_tag(conn, conversation_id, tag_name)
            if result:
                if json_output:
                    click.echo(
                        json.dumps(
                            {
                                "status": "success",
                                "conversation_id": conversation_id,
                                "tag": tag_name.strip(),
                            },
                            indent=2,
                        )
                    )
                else:
                    click.echo(f'✓ Tagged "{tag_name.strip()}" on {conversation_id}')
                sys.exit(0)
            else:
                if json_output:
                    error = {
                        "status": "error",
                        "error": "conversation_not_found",
                        "message": f"Conversation not found: {conversation_id}",
                    }
                    click.echo(json.dumps(error), err=True)
                else:
                    click.echo(
                        f"Error: Conversation not found: {conversation_id}", err=True
                    )
                sys.exit(2)
        finally:
            conn.close()
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)


@tag.command("remove")
@click.argument("conversation_id")
@click.argument("tag_name")
@click.pass_context
def tag_remove(ctx: click.Context, conversation_id: str, tag_name: str) -> None:
    """Remove a tag from a conversation.

    \b
    Example:
        chatgpt-archive tag remove 6974cc29-... "important"
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        try:
            result = db_remove_tag(conn, conversation_id, tag_name)
            if result:
                if json_output:
                    click.echo(
                        json.dumps(
                            {
                                "status": "success",
                                "conversation_id": conversation_id,
                                "tag_removed": tag_name.strip(),
                            },
                            indent=2,
                        )
                    )
                else:
                    click.echo(
                        f'✓ Removed tag "{tag_name.strip()}" from {conversation_id}'
                    )
                sys.exit(0)
            else:
                if json_output:
                    error = {
                        "status": "error",
                        "error": "not_found",
                        "message": f'Tag "{tag_name}" not found on conversation {conversation_id}',
                    }
                    click.echo(json.dumps(error), err=True)
                else:
                    click.echo(
                        f'Error: Tag "{tag_name}" not found on conversation {conversation_id}',
                        err=True,
                    )
                sys.exit(2)
        finally:
            conn.close()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)


@tag.command("show")
@click.argument("conversation_id")
@click.pass_context
def tag_show(ctx: click.Context, conversation_id: str) -> None:
    """Show all tags for a conversation.

    \b
    Example:
        chatgpt-archive tag show 6974cc29-...
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        try:
            # Verify conversation exists
            conv = get_conversation_by_id(conn, conversation_id)
            if conv is None:
                if json_output:
                    error = {
                        "status": "error",
                        "error": "conversation_not_found",
                        "message": f"Conversation not found: {conversation_id}",
                    }
                    click.echo(json.dumps(error), err=True)
                else:
                    click.echo(
                        f"Error: Conversation not found: {conversation_id}", err=True
                    )
                sys.exit(2)

            tags = db_get_tags(conn, conversation_id)

            if json_output:
                click.echo(
                    json.dumps(
                        {
                            "conversation_id": conversation_id,
                            "title": conv["title"],
                            "tags": tags,
                        },
                        indent=2,
                    )
                )
            else:
                title = conv["title"] or "[Untitled]"
                click.echo(f"{title}")
                if tags:
                    click.echo(f"Tags: {', '.join(tags)}")
                else:
                    click.echo("No tags")
            sys.exit(0)
        finally:
            conn.close()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)


@tag.command("list")
@click.pass_context
def tag_list(ctx: click.Context) -> None:
    """List all tags with usage counts.

    \b
    Example:
        chatgpt-archive tag list
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        try:
            tags = db_list_all_tags(conn)

            if json_output:
                click.echo(json.dumps({"tags": tags}, indent=2))
            else:
                if not tags:
                    click.echo(
                        "No tags. Use 'chatgpt-archive tag add <id> <tag>' to create one."
                    )
                else:
                    click.echo(f"{len(tags)} tag(s)")
                    click.echo()
                    for t in tags:
                        click.echo(f"  {t['name']} ({t['count']} conversations)")
            sys.exit(0)
        finally:
            conn.close()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(3)


@main.command()  # type: ignore[attr-defined]
@click.argument("conversation_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete(ctx: click.Context, conversation_id: str, yes: bool) -> None:
    """Delete a conversation from the database.

    CONVERSATION_ID is the OpenAI conversation ID. This permanently removes
    the conversation and all its messages from the database.

    \b
    Examples:
        chatgpt-archive delete 6974cc29-45d8-8327-a6dc-ef1ef0a82f46
        chatgpt-archive delete <id> --yes   # Skip confirmation
    """
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]

    # Check database exists
    if not db_path.exists():
        if json_output:
            error = {
                "status": "error",
                "error": "database_not_found",
                "message": "Database not found. Run 'chatgpt-archive import' first.",
            }
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(
                "Error: Database not found. Run 'chatgpt-archive import' first.",
                err=True,
            )
        sys.exit(1)

    try:
        conn = get_connection(db_path)
        try:
            # Check conversation exists before confirming
            conv = get_conversation_by_id(conn, conversation_id)
            if conv is None:
                if json_output:
                    error = {
                        "status": "error",
                        "error": "conversation_not_found",
                        "message": f"Conversation not found: {conversation_id}",
                    }
                    click.echo(json.dumps(error), err=True)
                else:
                    click.echo(
                        f"Error: Conversation not found: {conversation_id}", err=True
                    )
                sys.exit(2)

            title = conv["title"] or "[Untitled]"
            msg_count = conv["message_count"]

            # Confirm deletion
            if not yes and not json_output:
                click.echo(f'Delete "{title}" ({msg_count} messages)?')
                if not click.confirm("This action cannot be undone. Continue?"):
                    click.echo("Aborted.")
                    sys.exit(0)

            # Perform deletion
            deleted = db_delete_conversation(conn, conversation_id)

            if deleted:
                if json_output:
                    result = {
                        "status": "success",
                        "deleted_id": conversation_id,
                        "title": title,
                        "messages_removed": msg_count,
                    }
                    click.echo(json.dumps(result, indent=2))
                else:
                    click.echo(f'✓ Deleted "{title}" ({msg_count} messages)')
                sys.exit(0)
            else:
                # Should not happen since we checked above, but handle defensively
                if json_output:
                    error = {
                        "status": "error",
                        "error": "delete_failed",
                        "message": "Failed to delete conversation",
                    }
                    click.echo(json.dumps(error), err=True)
                else:
                    click.echo("Error: Failed to delete conversation", err=True)
                sys.exit(3)

        finally:
            conn.close()

    except Exception as e:
        if json_output:
            error = {"status": "error", "error": "delete_failed", "message": str(e)}
            click.echo(json.dumps(error), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(3)


if __name__ == "__main__":
    main()  # type: ignore[call-arg]  # Click handles the arguments
