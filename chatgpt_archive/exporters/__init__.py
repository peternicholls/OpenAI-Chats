"""Exporter registry and factory for conversation export.

This module provides a registry of available export formats and a factory
function to get the appropriate exporter for a given format.

Available formats:
    - md: Markdown format
    - json: JSON format  
    - yaml: YAML format
    - html: HTML with CSS styling
    - xml: XML format
"""

from typing import Dict, Type, Optional

from .base import BaseExporter
from .markdown import MarkdownExporter
from .json_export import JSONExporter
from .yaml_export import YAMLExporter
from .html import HTMLExporter
from .xml_export import XMLExporter


# Registry mapping format names to exporter classes
EXPORTERS: Dict[str, Type[BaseExporter]] = {
    "md": MarkdownExporter,
    "markdown": MarkdownExporter,
    "json": JSONExporter,
    "yaml": YAMLExporter,
    "yml": YAMLExporter,
    "html": HTMLExporter,
    "xml": XMLExporter,
}

# Supported format options for CLI
SUPPORTED_FORMATS = ["md", "json", "yaml", "html", "xml"]


def get_exporter(format_name: str) -> Optional[BaseExporter]:
    """Get an exporter instance for the specified format.
    
    Args:
        format_name: Export format (md, json, yaml, html, xml)
        
    Returns:
        Exporter instance, or None if format not supported
    """
    exporter_class = EXPORTERS.get(format_name.lower())
    if exporter_class:
        return exporter_class()
    return None


def get_supported_formats() -> list:
    """Get list of supported export format names.
    
    Returns:
        List of format name strings
    """
    return SUPPORTED_FORMATS.copy()


def get_file_extension(format_name: str) -> str:
    """Get the default file extension for a format.
    
    Args:
        format_name: Export format name
        
    Returns:
        File extension (with dot), or ".txt" if unknown
    """
    exporter = get_exporter(format_name)
    if exporter:
        return exporter.file_extension
    return ".txt"


__all__ = [
    "BaseExporter",
    "MarkdownExporter", 
    "JSONExporter",
    "YAMLExporter",
    "HTMLExporter",
    "XMLExporter",
    "EXPORTERS",
    "SUPPORTED_FORMATS",
    "get_exporter",
    "get_supported_formats",
    "get_file_extension",
]
