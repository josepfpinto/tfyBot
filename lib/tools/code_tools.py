from langchain_core.tools import tool
from typing import Annotated
from langchain_experimental.utilities import PythonREPL
from pprint import pprint

# Warning: This executes code locally, which can be unsafe when not sandboxed
repl = PythonREPL()


@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."]
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        print(50 * "=")
        print("We are inside PYTHONREPL: ")
        pprint(code)
        result = repl.run(code)
        print(50 * "=")
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Succesfully executed:\n```python\n{code}\n```\nStdout: {result}"
