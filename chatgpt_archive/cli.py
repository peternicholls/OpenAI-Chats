"""CLI interface for ChatGPT Archive Search & Export.

Commands:
    import   Import conversations from ChatGPT export archive
    search   Search conversations by keyword or phrase
    list     List all imported conversations
    view     View a specific conversation
    export   Export a conversation to file
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click

from chatgpt_archive import __version__
from chatgpt_archive.db import get_db_path, init_db


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
def main(ctx, db: Optional[str], json_output: bool):
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


@main.command("import")
@click.argument("archive_dir", type=click.Path(exists=True, file_okay=False))
@click.pass_context
def import_archive(ctx, archive_dir: str):
    """Import conversations from ChatGPT export archive.
    
    ARCHIVE_DIR is the path to the extracted ChatGPT export directory
    containing conversations.json.
    
    \b
    Example:
        chatgpt-archive import ~/Downloads/chatgpt-export/
    """
    # TODO: Implement in Phase 3 (T011-T018)
    click.echo("Import command placeholder - implementation in Phase 3", err=True)
    sys.exit(1)


@main.command()
@click.argument("query")
@click.option("--from", "from_date", help="Filter: conversations after date (YYYY-MM-DD)")
@click.option("--to", "to_date", help="Filter: conversations before date (YYYY-MM-DD)")
@click.option("--limit", "-l", default=20, help="Maximum results to return")
@click.pass_context
def search(ctx, query: str, from_date: Optional[str], to_date: Optional[str], limit: int):
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


@main.command("list")
@click.option("--sort", "-s", type=click.Choice(["date", "title", "messages"]), default="date",
              help="Sort by field")
@click.option("--order", "-o", type=click.Choice(["asc", "desc"]), default="desc",
              help="Sort order")
@click.option("--limit", "-l", default=50, help="Maximum results")
@click.option("--offset", default=0, help="Skip first N results (pagination)")
@click.pass_context
def list_conversations(ctx, sort: str, order: str, limit: int, offset: int):
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


@main.command()
@click.argument("conversation_id")
@click.pass_context
def view(ctx, conversation_id: str):
    """View a specific conversation.
    
    CONVERSATION_ID is the OpenAI conversation ID (shown in search/list output).
    
    \b
    Example:
        chatgpt-archive view 6974cc29-45d8-8327-a6dc-ef1ef0a82f46
    """
    # TODO: Implement in Phase 5 (T025-T030)
    click.echo("View command placeholder - implementation in Phase 5", err=True)
    sys.exit(1)


@main.command()
@click.argument("conversation_id")
@click.option("--format", "-f", "fmt", required=True,
              type=click.Choice(["md", "json", "yaml", "html", "xml"]),
              help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file (stdout if not specified)")
@click.pass_context
def export(ctx, conversation_id: str, fmt: str, output: Optional[str]):
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
    main()
