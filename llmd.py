import re
import json
import os
from typing import List, Tuple, Optional

import typer
import openai

app = typer.Typer()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.command()
def run(filepath: str) -> None:
    document = parse_markdown(filepath)
    project_key = list(document.keys())[0]
    conversation_text = document[project_key]["Conversation Thread"]["Entry 2"]["text"]
    functions = parse_functions(conversation_text)
    document = apply_functions(document, project_key, functions)

    # Query AI and print the response
    # ai_response = query_ai(document)
    # print("AI Response:")
    # print(ai_response)

    print("\nParsed functions:")
    print(json.dumps(functions, indent=4))

def parse_markdown(filepath: str) -> dict:
    # Markdown to dict
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

    # Parse conversation thread
    project_key = list(result.keys())[0]
    messages = []

    for key, content in result[project_key]["Conversation Thread"].items():
        if key == "text":
            continue
        i, human, assistant = -1, "", ""
        for line in content["text"].splitlines():
            if line.startswith("**Human:**"):
                human += line.replace("**Human:**", "")
                i = 0
            elif line.startswith("**Assistant:**"):
                assistant += line.replace("**Assistant:**", "")
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
                result += f"{'#' * (level + 1)} {key}\n"
                for message in value:
                    role = "Human" if message["role"] == "user" else "Assistant"
                    result += f"**{role}:** {message['content']}\n\n"
            elif key != "text":
                result += f"{'#' * (level + 1)} {key}\n"
                result += value.get("text", "")
                result += traverse(value, level + 1)
        return result

    return traverse(data)

def parse_functions(content: str) -> List[Tuple[str, str, str, str, Optional[str]]]:
    pattern = r'(?:([^\n]+)\n)?<<<<<< (.*?)\n(.*?)\n(?:=======\n(.*?)\n)?>>>>>> (.*?)(?:\n|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    return [(m[0].strip() or None, m[1], m[2], m[4], m[3] if m[3] else None) for m in matches]

def apply_functions(document: dict, project_title: str, functions: List[Tuple[str, str, str, str,
                                                                              Optional[str]]]) -> dict:
    for filepath, function_name_start, input_a, function_name_end, input_b in functions:
        function_names = (function_name_start, function_name_end)
        if function_names == ("SEARCH", "REPLACE"):
            # assert input_a in document[project_title]["Code Context"][filepath]["text"], "SEARCH string not found."
            document[project_title]["Code Context"][filepath]["text"] = document[project_title]["Code Context"][
                filepath]["text"].replace(input_a, input_b)
        elif function_names == ("SEARCH_MISSION", "REPLACE_MISSION"):
            assert input_a in document[project_title]["Mission"]["text"], "SEARCH_MISSION string not found."
            document[project_title]["Mission"]["text"] = document[project_title]["Mission"]["text"].replace(
                input_a, input_b)
        elif function_names == ("CHANGELOG", None):
            document[project_title]["Changelog"]["text"] += f"- {input_a}\n"

    return document

def query_ai(document: dict) -> str:
    project_key = list(document.keys())[0]

    # Prepare system message
    system_message = ""
    for key, value in document[project_key].items():
        if key != "Conversation Thread":
            system_message += f"# {key}\n\n{value['text']}\n\n"

    # Prepare conversation messages
    messages = [{"role": "system", "content": system_message}]
    conversation_thread = document[project_key]["Conversation Thread"]
    for entry_key, entry_value in conversation_thread.items():
        if entry_key != "text":
            human_message = entry_value.get("Human", {}).get("text", "")
            assistant_message = entry_value.get("Assistant", {}).get("text", "")

            if human_message:
                messages.append({"role": "user", "content": human_message})
            if assistant_message:
                messages.append({"role": "assistant", "content": assistant_message})

    # Send request to OpenAI API
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    return response.choices[0].message['content']

def test_unparse_markdown():
    with open("EXAMPLE.ll.md") as f:
        assert f.read() == unparse_markdown(parse_markdown("EXAMPLE.ll.md"))

if __name__ == "__main__":
    test_unparse_markdown()
    app()
