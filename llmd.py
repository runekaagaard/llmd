import re, json, os
from typing import List, Tuple, Optional

import typer
from litellm import completion

app = typer.Typer(pretty_exceptions_enable=False)  # pretty_exceptions_show_locals = False

@app.command()
def run(filepath: str) -> None:
    document = parse_markdown(filepath)
    project_key = list(document.keys())[0]
    response = query_ai(document)
    document[project_key]["Conversation Thread"].append({"role": "assistant", "content": response})
    functions = parse_functions(response)
    document = apply_functions(document, functions)
    with open("new.ll.md", "w") as f:
        f.write(unparse_markdown(document))

def parse_markdown(filepath: str) -> dict:
    # Markdown to dict
    result, level = {}, 0
    inner_result = result
    stack = []

    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader([os.path.dirname(filepath), 'templates']))
    # Load and render a template
    template = env.get_template(os.path.basename(filepath))
    rendered = template.render()

    for line in rendered.splitlines():
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

    # Parse conversation thread
    project_key = list(result.keys())[0]
    messages = []

    for key, content in result[project_key]["Conversation Thread"].items():
        if key == "text":
            continue
        i, human, assistant = -1, "", ""
        for line in content["text"].splitlines():
            if line.startswith("**Human:**"):
                human += line.replace("**Human:**", "") + "\n"
                i = 0
            elif line.startswith("**Assistant:**"):
                assistant += line.replace("**Assistant:**", "") + "\n"
                i = 1
            else:
                if i == 0:
                    human += line + "\n"
                elif i == 1:
                    assistant += line + "\n"

        if human:
            messages.append({"role": "user", "content": human})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})

    result[project_key]["Conversation Thread"] = messages

    return result

def unparse_markdown(data: dict) -> str:
    def traverse(d, level=0):
        result = ""
        for key, value in d.items():
            if key == "Conversation Thread":
                result += f"{'#' * (level + 1)} {key}"
                for i, message in enumerate(value):
                    if i % 2 == 0:
                        result += f"\n\n### Entry {i // 2 + 1}"
                    role = "Human" if message["role"] == "user" else "Assistant"
                    result += f"\n\n**{role}:** {message['content'].strip()}"
            elif key != "text":
                result += f"{'#' * (level + 1)} {key}\n"
                result += value.get("text", "")
                result += traverse(value, level + 1)
        return result

    return traverse(data) + "\n"

def parse_functions(content: str) -> List[Tuple[str, str, str, str, Optional[str]]]:
    pattern = r'(?:([^\n]+)\n)?<<<<<< (.*?)\n(.*?)\n(?:=======\n(.*?)\n)?>>>>>> (.*?)(?:\n|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    return [(m[0].strip() or None, m[1], m[2], m[4], m[3] if m[3] else None) for m in matches]

def apply_functions(document: dict, functions: List[Tuple[str, str, str, str, Optional[str]]]) -> dict:
    project_title = list(document.keys())[0]
    for filepath, function_name_start, input_a, function_name_end, input_b in functions:
        function_names = (function_name_start, function_name_end)
        if function_names == ("SEARCH", "REPLACE"):
            if input_a not in document[project_title]["Code Context"][filepath]["text"]:
                print("SEARCH NOT FOUND:")
                print(input_a)
                print()
                print("IN:")
                print(document[project_title]["Code Context"][filepath]["text"])
                print()
                print("OUT:")
                print(input_b)
            assert input_a in document[project_title]["Code Context"][filepath]["text"], "SEARCH string not found."
            document[project_title]["Code Context"][filepath]["text"] = document[project_title]["Code Context"][
                filepath]["text"].replace(input_a, input_b)
            document[project_title]["Conversation Thread"][-1]["content"] = document[project_title][
                "Conversation Thread"][-1]["content"].replace(
                    input_a, "[Omitted for brevity. See latest version in Code Context.]")
            document[project_title]["Conversation Thread"][-1]["content"] = document[project_title][
                "Conversation Thread"][-1]["content"].replace(
                    input_b, "[Omitted for brevity. See latest version in Code Context.]")

            print("SEARCH/REPLACE OK", filepath)
        elif function_names == ("SEARCH_MISSION", "REPLACE_MISSION"):
            assert input_a in document[project_title]["Mission"]["text"], "SEARCH_MISSION string not found."
            document[project_title]["Mission"]["text"] = document[project_title]["Mission"]["text"].replace(
                input_a, input_b)
        elif function_names == ("CHANGELOG", None):
            document[project_title]["Changelog"]["text"] += f"- {input_a}\n"

    return document

def query_ai(document: dict) -> str:
    project_key = list(document.keys())[0]

    system_message = unparse_markdown({k: v for k, v in document.items() if k != "Conversation Thread"})
    messages = [{"role": "system", "content": system_message}] + document[project_key]["Conversation Thread"]

    response = completion(model="claude-3-5-sonnet-20240620", messages=messages)

    return response.choices[0].message.content

def test_unparse_markdown():
    with open("EXAMPLE.ll.md") as f:
        unparsed = unparse_markdown(parse_markdown("EXAMPLE.ll.md"))
        assert f.read() == unparsed

if __name__ == "__main__":
    # test_unparse_markdown()
    app()
