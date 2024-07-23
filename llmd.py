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
    print(tree.root_node.sexp())

    query = language.query("""
    (atx_heading
      (atx_h1_marker)
      (heading_content) @project (#match? @project "^Project:"))
    (atx_heading
      (atx_h2_marker)
      (heading_content) @section_name)
    (paragraph) @mission (#eq? @section_name "Mission")
    (atx_heading
      (atx_h3_marker)
      (heading_content) @filename)
    (fenced_code_block) @code_block (#eq? @section_name "Code Context")
    (list_item) @changelog_item
    (paragraph
      (strong_emphasis) @speaker
      (text) @message) (#eq? @section_name "Conversation Thread")
    """)

    captures = query.captures(tree.root_node)

    result = {"project": "", "mission": "", "code_context": {}, "changelog": [], "conversation": []}

    current_section = ""
    current_filename = ""
    current_entry = {}
    for capture in captures:
        node, capture_name = capture
        text = content[node.start_byte:node.end_byte].strip()

        if capture_name == "project":
            result["project"] = text.replace("Project:", "").strip()
        elif capture_name == "section_name":
            current_section = text
        elif capture_name == "mission" and current_section == "Mission":
            result["mission"] = text
        elif capture_name == "filename":
            current_filename = text
        elif capture_name == "code_block" and current_section == "Code Context":
            result["code_context"][current_filename] = text
        elif capture_name == "changelog_item" and current_section == "Changelog":
            result["changelog"].append(text.lstrip("- "))
        elif capture_name == "speaker" and current_section == "Conversation Thread":
            speaker = text.strip("*")
            if speaker == "Human":
                current_entry = {"human": ""}
            elif speaker == "Assistant":
                current_entry["assistant"] = ""
        elif capture_name == "message" and current_section == "Conversation Thread":
            if "human" in current_entry and not current_entry["human"]:
                current_entry["human"] = text.strip()
            elif "assistant" in current_entry:
                current_entry["assistant"] = text.strip()
                result["conversation"].append(current_entry)
                current_entry = {}

    return result

if __name__ == "__main__":
    app()
