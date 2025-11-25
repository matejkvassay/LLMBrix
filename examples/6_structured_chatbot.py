from pydantic import BaseModel, Field

from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg
from llmbrix.tools import GetDatetime, ListDir

"""
Uses chat history, listens to user but also returns response in structured format.
"""

PROMPT = (
    "You will get unix command which failed and your job is to fix it. "
    "User might have just entered a typo or entered an incorrect path. "
    "You can use tool to verify what files are on any given path. "
    "User can also just give feedback on your correction, if the input doesnt look like a command listen to user "
    "and try to refine your suggestion."
)

HIST_LIMIT = 10
MODEL = "gpt-5-nano"

INPUT_MSGS = ["lz -la", "cd //tmp", "cat /tmp/myfile" "try in local tmp"]


class CommandCorrection(BaseModel):
    original_command: str = Field(..., description="The original Unix command entered by the user.")
    explanation: str = Field(..., description="An explanation of what was corrected and why.")
    corrected_command: str = Field(
        ...,
        description="The corrected and likely intended Unix command. "
        "Must be valid pure unix command we can directly run in terminal.",
    )


gpt = GptOpenAI(model=MODEL, output_format=CommandCorrection)
chat_history = ChatHistory(max_turns=HIST_LIMIT)
system_msg = SystemMsg(content=PROMPT)
tools = [GetDatetime(), ListDir()]
agent = Agent(gpt=gpt, chat_history=chat_history, system_msg=system_msg, tools=tools)

for c in INPUT_MSGS:
    print("\n\n_____________________________________________________")
    print("USER: \n")
    print(f"INCORRECT CMD: '{c}'")
    response = agent.chat(UserMsg(content=c))
    print("\n\nASSISTANT: \n")
    print(f"CORRECTED CMD: '{response.content_parsed.corrected_command}'\n")
    print(f"EXPLANATION: '{response.content_parsed.explanation}'\n")
