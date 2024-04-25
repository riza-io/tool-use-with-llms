import openai
import rizaio
import json

# requires a valid OpenAI API key in the OPENAI_API_KEY env var
# requires a valid Riza API key in the RIZA_API_KEY env var

def execute_python(code:str):
    """ Executes a Python script and returns whatever was printed to stdout.
    
    The Python runtime does not have network or filesystem access, but does include the entire standard library. Read input from stdin and write output to stdout.
    """
    riza = rizaio.Riza()
    resp = riza.command.exec(
        language="PYTHON",
        code=code
    )
    return resp.stdout

def main():
    client = openai.OpenAI()

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo-0125',
        messages=[{ 'role': 'user', 'content': 'Please base64 encode the last message I sent you' }],
        tools=[{
            "type": "function",
            "function": {
                "name": "run_python",
                "description": "Run Python to solve problems. The Python runtime does not have network or filesystem access, but does include the entire standard library. Read input from stdin and write output to stdout.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code. Must log the desired output to stdout."
                        }
                    },
                    "required": ["code"],
                }
            }
        }]
    )

    if completion.choices[0].message.tool_calls:
        for tool_call in completion.choices[0].message.tool_calls:
            args = json.loads(tool_call.function.arguments)

            output = execute_python(code=args.get('code'))

            print("used tool", output)
    else:
        print("finished", completion.choices[0].message)

if __name__ == "__main__":
    main()