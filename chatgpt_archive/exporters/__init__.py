"""Exporter registry and factory for conversation export.

This module provides a registry of available export formats and a factory
function to get the appropriate exporter for a given format.

Available formats:
    - md: Markdown format
    - json: JSON format  
    - yaml: YAML format
    - html: HTML with CSS styling
    - xml: XML format
    - csv: CSV format
    - xlsx: Excel format (requires openpyxl)
"""

from typing import Dict, Type

from .base import BaseExporter
from .markdown import MarkdownExporter
from .json_export import JSONExporter
from .yaml_export import YAMLExporter
from .html import HTMLExporter
from .xml_export import XMLExporter
from .csv_export import CSVExporter

# Excel exporter is optional (requires openpyxl)
try:
    from .excel_export import ExcelExporter
    _HAS_EXCEL = True
except ImportError:
    _HAS_EXCEL = False


# Registry mapping format names to exporter classes
EXPORTERS: Dict[str, Type[BaseExporter]] = {
    "md": MarkdownExporter,
    "markdown": MarkdownExporter,
    "json": JSONExporter,
    "yaml": YAMLExporter,
    "yml": YAMLExporter,
    "html": HTMLExporter,
    "xml": XMLExporter,
    "csv": CSVExporter,
}

# Add Excel exporter if openpyxl is available
if _HAS_EXCEL:
    EXPORTERS["xlsx"] = ExcelExporter  # type: ignore[assignment]
    EXPORTERS["excel"] = ExcelExporter  # type: ignore[assignment]

# Supported format options for CLI
SUPPORTED_FORMATS = ["md", "json", "yaml", "html", "xml", "csv", "xlsx"]


def get_exporter(format_name: str) -> BaseExporter | None:
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
    "CSVExporter",
    "EXPORTERS",
    "SUPPORTED_FORMATS",
    "get_exporter",
    "get_supported_formats",
    "get_file_extension",
]
