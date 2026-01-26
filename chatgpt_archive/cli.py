"""CLI interface for ChatGPT Archive Search & Export.

Commands:
    import   Import conversations from ChatGPT export archive
    search   Search conversations by keyword or phrase
    list     List all imported conversations
    view     View a specific conversation
    export   Export a conversation to file
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import click  # type: ignore[import-untyped]

from chatgpt_archive import __version__
from chatgpt_archive.db import get_db_path, init_db, get_db_size
from chatgpt_archive import importer


def get_db_option_path(db: Optional[str]) -> Path:
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
    "--db", "-d",
    type=click.Path(),
    envvar="CHATGPT_ARCHIVE_DB",
    help="Database file path (default: ~/.chatgpt-archive/chats.db)"
)
@click.option(
    "--json", "-j",
    "json_output",
    is_flag=True,
    help="Output in JSON format"
)
@click.version_option(version=__version__, prog_name="chatgpt-archive")
@click.pass_context
def main(ctx: click.Context, db: Optional[str], json_output: bool) -> None:
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
                click.echo(f"  Processed {current}/{total_count} conversations...", err=True)
        
        # Run import
        conversations_imported, messages_imported = importer.import_archive(
            archive_path,
            db_path,
            progress_callback
        )
        
        # Get database size
        db_size = get_db_size(db_path)
        
        # Output results
        if json_output:
            result = {
                "status": "success",
                "conversations_imported": conversations_imported,
                "messages_imported": messages_imported,
                "database_path": str(db_path),
                "database_size_bytes": db_size
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"\n✓ Import complete!")
            click.echo(f"  Conversations: {conversations_imported}")
            click.echo(f"  Messages: {messages_imported}")
            click.echo(f"  Database: {db_path} ({db_size / 1024 / 1024:.1f} MB)")
        
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


@main.command()  # type: ignore[attr-defined]
@click.argument("query")
@click.option("--from", "from_date", help="Filter: conversations after date (YYYY-MM-DD)")
@click.option("--to", "to_date", help="Filter: conversations before date (YYYY-MM-DD)")
@click.option("--limit", "-l", default=20, help="Maximum results to return")
@click.pass_context
def search(ctx: click.Context, query: str, from_date: Optional[str], to_date: Optional[str], limit: int) -> None:
    """Search conversations by keyword or phrase.
    
    QUERY is the search term. Supports FTS5 syntax for advanced queries.
    
    \b
    Examples:
        chatgpt-archive search "machine learning"
        chatgpt-archive search "python AND tutorial"
        chatgpt-archive search "error" --from 2024-01-01
    """
    # TODO: Implement in Phase 4 (T019-T024)
    click.echo("Search command placeholder - implementation in Phase 4", err=True)
    sys.exit(1)


@main.command("list")  # type: ignore[attr-defined]
@click.option("--sort", "-s", type=click.Choice(["date", "title", "messages"]), default="date",
              help="Sort by field")
@click.option("--order", "-o", type=click.Choice(["asc", "desc"]), default="desc",
              help="Sort order")
@click.option("--limit", "-l", default=50, help="Maximum results")
@click.option("--offset", default=0, help="Skip first N results (pagination)")
@click.pass_context
def list_conversations(ctx: click.Context, sort: str, order: str, limit: int, offset: int) -> None:
    """List all imported conversations.
    
    \b
    Examples:
        chatgpt-archive list
        chatgpt-archive list --sort title --order asc
        chatgpt-archive list --limit 10 --offset 20
    """
    # TODO: Implement in Phase 7 (T041-T046)
    click.echo("List command placeholder - implementation in Phase 7", err=True)
    sys.exit(1)


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
    # TODO: Implement in Phase 5 (T025-T030)
    click.echo("View command placeholder - implementation in Phase 5", err=True)
    sys.exit(1)


@main.command()  # type: ignore[attr-defined]
@click.argument("conversation_id")
@click.option("--format", "-f", "fmt", required=True,
              type=click.Choice(["md", "json", "yaml", "html", "xml"]),
              help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file (stdout if not specified)")
@click.pass_context
def export(ctx: click.Context, conversation_id: str, fmt: str, output: Optional[str]) -> None:
    """Export a conversation to file.
    
    CONVERSATION_ID is the OpenAI conversation ID.
    
    \b
    Examples:
        chatgpt-archive export <id> -f md -o conversation.md
        chatgpt-archive export <id> -f json
        chatgpt-archive export <id> -f html -o chat.html
    """
    # TODO: Implement in Phase 6 (T031-T040)
    click.echo("Export command placeholder - implementation in Phase 6", err=True)
    sys.exit(1)


if __name__ == "__main__":
    main()  # type: ignore[call-arg]  # Click handles the arguments
