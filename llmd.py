import mimetypes, os, sys, warnings
from tree_sitter_languages import get_language, get_parser

LANGUAGES = {"py": "python", "css": "css", "js": "javascript", "jsx": "javascript", "md": "markdown"}
