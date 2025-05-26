from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg

SYSTEM_MSG = "Be super brief."
HIST_LIMIT = 5
MODEL = "gpt-4o-mini"

gpt = GptOpenAI(model=MODEL)
chat_history = ChatHistory(max_turns=HIST_LIMIT)
system_msg = SystemMsg(content=SYSTEM_MSG)
agent = Agent(gpt=gpt, chat_history=chat_history, system_msg=system_msg)

while True:
    user_input = input("User input (enter 'q' to exit): ")
    if user_input.lower() in {"q"}:
        break
    user_msg = UserMsg(content=user_input)
    assistant_msg = agent.chat(user_msg)

    print(user_msg)
    print(assistant_msg)
