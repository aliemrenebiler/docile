"""Shared logic used by both the command line and the MCP server."""

from .create import DocxerError, OutputExists, create_docx, template_variables

__all__ = ["DocxerError", "OutputExists", "create_docx", "template_variables"]
