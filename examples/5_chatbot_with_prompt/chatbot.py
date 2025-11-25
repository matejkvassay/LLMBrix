from datetime import datetime
from time import time

from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg
from llmbrix.prompt import Prompt
from llmbrix.prompt_reader import PromptReader
from llmbrix.tools import GetDatetime, ListDir

RUN_START = time()
HIST_LIMIT = 5
MODEL = "gpt-5-mini"
PROMPT_DIR = "./prompts"
CHATBOT_NAME = "Rupert"


def get_context_vars():
    dur = time() - RUN_START
    weekday_name = datetime.now().strftime("%A")
    return {"uptime": round(dur, 2), "weekday": weekday_name}


prompt_reader = PromptReader(PROMPT_DIR)

# example of full rendering
system_prompt: Prompt = prompt_reader.read("system")
system_prompt_str: str = system_prompt.render({"chatbot_name": CHATBOT_NAME})

gpt = GptOpenAI(model=MODEL)
chat_history = ChatHistory(max_turns=HIST_LIMIT)
system_msg = SystemMsg(content=system_prompt_str)
tools = [GetDatetime(), ListDir()]
agent = Agent(gpt=gpt, chat_history=chat_history, system_msg=system_msg, tools=tools)

while True:
    user_input = input("User input (enter 'q' to exit): ")
    if user_input.lower() in {"q"}:
        break
    user_msg = UserMsg(content=user_input)
    assistant_msg = agent.chat(user_msg)

    print(user_msg)
    print(assistant_msg)

print("Final chat history dump:")

for m in chat_history.get():
    print("\n\n")
    print(m)
