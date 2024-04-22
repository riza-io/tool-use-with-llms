import anthropic
import rizaio


def main():
    client = anthropic.Anthropic()
    riza = rizaio.Riza()
        
    messages = [
        {"role": "user", "content": "Can you base64 encode this message?"},
    ]
    tools = [
        {
            "name": "execute_python",
            "description": "Execute a Python script. The Python runtime does not have network or filesystem access, but does include the entire standard library. Read input from stdin and write output to stdout.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to execute",
                    }
                },
                "required": ["code"],
            },
        },
        {
            "name": "execute_javascript",
            "description": "Execute a JavaScript script. The JavaScript runtime does not have network or filesystem access. Read input from the process.stdout global variable and write output using console.log.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The JavaScript code to execute",
                    }
                },
                "required": ["code"],
            },
        }
    ]

    response = client.beta.tools.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

    changed = False
    for block in response.content:
        if block.type == 'tool_use':
            language = "UNKNOWN"
            if block.name == 'execute_python':
                language = "PYTHON"
            if block.name == 'execute_javascript':
                language = "JAVASCRIPT"

            print(f"Running {language}...")
            print(block.input['code'])

            output = riza.sandbox.execute(language=language, code=block.input['code'])
            print(output)

            if int(output.exit_code) > 1:
                raise ValueError(f"non-zero exit code {output.exit_code}")

            changed = True

            messages.append({
                "role": "assistant",
                "content": response.content,
            })
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output.stdout,
                    }
                ],
            })

    if not changed:
        print("NO TOOL USE")
        return

    response = client.beta.tools.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

    print(response)

if __name__ == "__main__":
    main()
