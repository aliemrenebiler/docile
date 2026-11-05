"""Shared logic used by both the command line and the MCP server."""

from .create import DocxerError, create_docx, template_variables

__all__ = ["DocxerError", "create_docx", "template_variables"]
