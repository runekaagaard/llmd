import mimetypes, os, sys, warnings
from tree_sitter_languages import get_language, get_parser
import typer

app = typer.Typer()

LANGUAGES = {"py": "python", "css": "css", "js": "javascript", "jsx": "javascript", "md": "markdown"}

@app.command()
def run(filepath: str) -> None:
    parsed = parse(filepath)
    # We will fill this out later.

def parse(filepath: str) -> dict:
    return {
        "project": "TODO PROJECT HEADING",
        "code_context": {
            "app.py": ["CODE CONTEXT app.py"],
            "foo.py": ["CODE CONTEXT foo.py"],
        },
        "changelog": "TODO CHANGELOG",
        "conversation": [
            {
                "human": "foo 1",
                "assistant": "bar 1"
            },
            {
                "human": "foo 2",
                "assistant": "bar 3"
            },
        ]
    }
