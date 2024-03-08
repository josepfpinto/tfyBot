"""Langchain tool for python shell"""
from io import StringIO
import sys
import traceback
from langchain.agents.tools import Tool


class PythonREPL:
    def __init__(self):
        pass

    def run(self, command):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        try:
            exec(command, globals())
            sys.stdout = old_stdout
            output = mystdout.getvalue()
        except Exception:
            sys.stdout = old_stdout
            output = traceback.format_exc()

        return output


# Setup for LangChain
python_repl = Tool(
    "Python REPL",
    PythonREPL().run,
    "A Python shell. Use this to execute python commands. Input should be a valid python command. If you expect output it should be printed out."
)
