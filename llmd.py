import mimetypes, os, sys, warnings
from tree_sitter_languages import get_language, get_parser
import typer

app = typer.Typer()

LANGUAGES = {"py": "python", "css": "css", "js": "javascript", "jsx": "javascript", "md": "markdown"}

@app.command()
def run(filepath: str) -> None:
    parsed = parse(filepath)
    print(parsed)

def parse(filepath: str) -> dict:
    with open(filepath, 'r') as file:
        content = file.read()

    language = get_language('markdown')
    parser = get_parser('markdown')
    tree = parser.parse(bytes(content, 'utf8'))

    query = language.query("""
    (atx_heading
      (atx_h1_marker)
      (heading_content) @project (#match? @project "^Project:"))
    (section
      (atx_heading
        (atx_h2_marker)
        (heading_content) @section_name)
      (paragraph) @mission (#eq? @section_name "Mission"))
    (section
      (atx_heading
        (atx_h2_marker)
        (heading_content) @section_name)
      (section
        (atx_heading
          (atx_h3_marker)
          (heading_content) @filename)
        (fenced_code_block) @code_block) (#eq? @section_name "Code Context"))
    (section
      (atx_heading
        (atx_h2_marker)
        (heading_content) @section_name)
      (list
        (list_item) @changelog_item) (#eq? @section_name "Changelog"))
    (section
      (atx_heading
        (atx_h2_marker)
        (heading_content) @section_name)
      (section
        (atx_heading
          (atx_h3_marker)
          (heading_content) @entry_number)
        (paragraph) @human
        (paragraph) @assistant) (#eq? @section_name "Conversation Thread"))
    """)

    captures = query.captures(tree.root_node)

    result = {
        "project": "",
        "mission": "",
        "code_context": {},
        "changelog": [],
        "conversation": []
    }

    current_entry = {}
    for capture in captures:
        node, capture_name = capture
        text = content[node.start_byte:node.end_byte].strip()

        if capture_name == "project":
            result["project"] = text.replace("Project:", "").strip()
        elif capture_name == "mission":
            result["mission"] = text
        elif capture_name == "filename":
            current_filename = text
        elif capture_name == "code_block":
            result["code_context"][current_filename] = text
        elif capture_name == "changelog_item":
            result["changelog"].append(text.lstrip("- "))
        elif capture_name == "human":
            current_entry["human"] = text.replace("**Human:**", "").strip()
        elif capture_name == "assistant":
            current_entry["assistant"] = text.replace("**Assistant:**", "").strip()
            result["conversation"].append(current_entry)
            current_entry = {}

    return result
