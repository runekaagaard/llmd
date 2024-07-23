import mimetypes, os, sys, warnings
from tree_sitter_languages import get_language, get_parser
import typer

app = typer.Typer()

LANGUAGES = {"py": "python", "css": "css", "js": "javascript", "jsx": "javascript", "md": "markdown"}

@app.command()
def run(filepath: str) -> None:
    parsed = parse(filepath)
    print(f"Project Title: {parsed['project_title']}")
    print("\nSections:")
    for section, content in parsed['sections'].items():
        print(f"\n{section}:")
        print(content[:100] + "..." if len(content) > 100 else content)

def parse(filepath: str) -> dict:
    with open(filepath, 'r') as file:
        content = file.read()

    language = get_language('markdown')
    parser = get_parser('markdown')
    tree = parser.parse(bytes(content, 'utf8'))
    print(tree.root_node.sexp())

    with open('parse.query', 'r') as query_file:
        query_string = query_file.read()

    query = language.query(query_string)

    captures = query.captures(tree.root_node)

    result = {"project_title": "", "sections": {}}

    current_section = ""
    section_content = ""

    for capture in captures:
        node, capture_name = capture
        text = content[node.start_byte:node.end_byte].strip()

        if capture_name == "project":
            result["project_title"] = text.split("Project:", 1)[1].strip()
        elif capture_name == "section_name":
            if current_section:
                result["sections"][current_section] = section_content.strip()
            current_section = text
            section_content = ""
        else:
            section_content += text + "\n"

    if current_section:
        result["sections"][current_section] = section_content.strip()

    return result

if __name__ == "__main__":
    app()

# Suppress the FutureWarning
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
