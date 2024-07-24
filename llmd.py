import re, json
from typing import List, Tuple, Optional

import typer

app = typer.Typer()

@app.command()
def run(filepath: str) -> None:
    document = parse_markdown(filepath)
    project_key = list(document.keys())[0]
    conversation_text = document[project_key]["Conversation Thread"]["Entry 2"]["text"]
    functions = parse_functions(conversation_text)
    document = apply_functions(document, project_key, functions)

    print(json.dumps(functions, indent=4))

def parse_markdown(filepath: str) -> dict:
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

def unparse_markdown(data: dict) -> str:
    def traverse(d, level=0):
        result = ""
        for key, value in d.items():
            if key != "text":
                result += f"{'#' * (level + 1)} {key}\n"
                result += value.get("text", "")
                result += traverse(value, level + 1)
        return result

    return traverse(data)

def parse_functions(content: str) -> List[Tuple[str, str, str, str, Optional[str]]]:
    pattern = r'([^\n]*)\n<<<<<< (.*?)\n(.*?)\n=======\n(.*?)\n>>>>>> (.*?)(?:\n|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    return [(m[0].strip() or None, m[1], m[2], m[4], m[3]) for m in matches]

def apply_functions(document: dict, project_title: str, functions: List[Tuple[str, str, str, str,
                                                                              Optional[str]]]) -> dict:
    for filepath, function_name_start, input_a, function_name_end, input_b in functions:
        function_names = (function_name_start, function_name_end)
        print(function_names)
        if function_names == ("SEARCH", "REPLACE"):
            # assert input_a in document[project_title]["Code Context"][filepath]["text"], "SEARCH string not found."
            document[project_title]["Code Context"][filepath]["text"].replace(input_a, input_b)
        elif function_names == ("SEARCH_MISSION", "REPLACE_MISSION"):
            assert input_a in document[project_title]["Mission"]["text"], "SEARCH_MISSION string not found."
            document[project_title]["Mission"]["text"].replace(input_a, input_b)
        elif function_names == ("CHANGELOG", None):
            kofkwokef

    return document

def test_unparse_markdown():
    with open("EXAMPLE.ll.md") as f:
        assert f.read() == unparse_markdown(parse_markdown("EXAMPLE.ll.md"))

if __name__ == "__main__":
    test_unparse_markdown()
    app()

# Changelog:
# - Updated parse_functions to capture filenames and fix replace string handling
# - Modified run function to display detailed parsed function information
# - Fixed parse_functions to only match a single line above search blocks
