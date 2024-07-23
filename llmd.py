import mimetypes, os, sys, warnings
from tree_sitter_languages import get_language, get_parser
import typer

app = typer.Typer()

LANGUAGES = {"py": "python", "css": "css", "js": "javascript", "jsx": "javascript", "md": "markdown"}

@app.command()
def run(filepath: str) -> None:
    parsed = parse(filepath)
    import json
    print(json.dumps(parsed, indent=4))

def parse(filepath: str) -> dict:
    result, level = {}, 0
    inner_result = result
    stack = []

    with open(filepath, 'r') as f:
        for line in f.readlines():
            if line.startswith("#"):
                hashtags, title = line.strip().split(" ", 1)
                assert title != "text"
                new_level = len(hashtags)

                if stack and new_level <= level:
                    for _ in range(level - new_level + 1):
                        stack.pop()

                if stack:
                    inner_result = stack[-1]

                inner_result[title] = {"text": ""}
                stack.append(inner_result[title])
                level = new_level
            else:

                stack[-1]["text"] += line

    return result

if __name__ == "__main__":
    app()
