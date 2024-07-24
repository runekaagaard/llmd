import re, json
from typing import List, Tuple, Optional

import typer

app = typer.Typer()

@app.command()
def run(filepath: str) -> None:
    parsed = parse(filepath)
    conversation_text = parsed["Project: Simple Todo App"]["Conversation Thread"]["Entry 2"]["text"]
    functions = parse_functions(conversation_text)
    
    print("Parsed functions:")
    for func in functions:
        print(f"File: {func[0]}")
        print(f"Search type: {func[1]}")
        print(f"Search content:\n{func[2]}")
        print(f"Replace type: {func[3]}")
        print(f"Replace content:\n{func[4] if func[4] is not None else 'None'}")
        print("-" * 50)

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

def unparse(data: dict) -> str:
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
    pattern = r'(.*?)\n<<<<<< (.*?)\n(.*?)\n=======\n(.*?)\n>>>>>> (.*?)(?:\n|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    return [(m[0].strip(), m[1], m[2], m[4], m[3]) for m in matches]

def test_unparse():
    with open("EXAMPLE.ll.md") as f:
        assert f.read() == unparse(parse("EXAMPLE.ll.md"))

if __name__ == "__main__":
    test_unparse()
    app()

# Changelog:
# - Updated parse_functions to capture filenames and fix replace string handling
# - Modified run function to display detailed parsed function information
