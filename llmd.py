import typer

app = typer.Typer()

@app.command()
def run(filepath: str) -> None:
    parsed = parse(filepath)

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

def test_unparse():
    with open("EXAMPLE.ll.md") as f:
        assert f.read() == unparse(parse("EXAMPLE.ll.md"))

if __name__ == "__main__":
    test_unparse()
    app()
