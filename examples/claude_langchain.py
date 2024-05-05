from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool

from rizaio import Riza

# Get an API key from https://dashboard.riza.io and set it as the value of
# an environment variable named RIZA_API_KEY
riza = Riza()

@tool
def execute_javascript(javascript_code: str) -> str:
    """Execute JavaScript code to solve problems.

    The JavaScript runtime does not have network or filesystem access, but does
    include the global JSON object. Read input from stdin and write output
    to stdout."""
    output = riza.command.exec(language="JAVASCRIPT", code=javascript_code)

    # TODO: handle errors using https://python.langchain.com/docs/modules/tools/custom_tools/#handling-tool-errors

    return output.stdout


def main():
    llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.2, max_tokens=1024)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Make sure to use the execute_javascript tool if you need to solve a problem."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    tools = [execute_javascript]

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print(agent_executor.invoke({"input": "please base32 encode the message \"purple monkey dishwasher\""}))

if __name__ == "__main__":
    main()
