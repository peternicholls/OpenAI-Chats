"""ChatGPT Archive Search & Export - CLI tool for managing ChatGPT conversation exports.

This package provides a complete pipeline for importing, searching, viewing,
and exporting ChatGPT conversation archives.

Modules:
    cli: Click-based command-line interface
    db: SQLite database connection and schema management
    models: Data classes for Conversation, Message, and Attachment
    importer: JSON archive parsing and database insertion
    search: FTS5 full-text and optional semantic/hybrid search
    embeddings: OpenAI vector embedding generation
    exporters: Output formatters (Markdown, JSON, YAML, HTML, XML)
"""

__version__ = "0.1.0"
__author__ = "Peter Nicholls"

from chatgpt_archive.models import Conversation, Message, Attachment

__all__ = ["__version__", "Conversation", "Message", "Attachment"]
