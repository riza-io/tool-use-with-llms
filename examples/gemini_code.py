import os
import rizaio
import google.generativeai as genai

# requires a valid Google Gemini API key in the GOOGLE_API_KEY env var
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
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.0-pro-latest', tools=[execute_python])
    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message('Please base64 encode the last message I sent you')
    print(response.text)

    for content in chat.history:
        print(content.role, "->", [type(part).to_dict(part) for part in content.parts])
        print('-'*80)

if __name__ == "__main__":
    main()