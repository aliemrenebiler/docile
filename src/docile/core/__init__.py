"""Shared logic used by both the command line and the MCP server."""

from .create import DocileError, OutputExists, create_docx, template_variables

__all__ = ["DocileError", "OutputExists", "create_docx", "template_variables"]
