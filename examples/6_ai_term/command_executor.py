import subprocess

from pydantic import BaseModel

from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import SystemMsg, UserMsg


class TerminalCommand(BaseModel):
    valid_terminal_command: str
    # your_reasoning: str
    # brief_command_description: str


CHAT_HISTORY_MAX_TURNS = 5
MODEL = "gpt-4o-mini"
SYSTEM_MSG_AI_MODE = (
    "You are Python programming chatbot assistant. "
    "Your answers are shown inside a terminal window, quite narrow. "
    "Make short sentences. Be super brief. "
)
SYSTEM_MSG_CODE_MODE = (
    "You never speak words you only answer to user in Python code. "
    "No explanations needed. Just listen very carefully to what user says and "
    "return pure valid Python code."
)
SYSTEM_MSG_TERMINAL_MODE = (
    "You will get a text user entered into a unix terminal but ended up with an error code. \n"
    "Based on this unix terminal input from the user do following: \n"
    "   - if the input seems like an attempt to write a valid terminal command then fix it"
    " (e.g. some typo or small mistake)\n"
    "   - if the input is natural language speech translate it into a valid terminal command\n"
    "   - if the input has nothing to do with unix terminal commands "
    'just return empty command ""'
)
gpt = GptOpenAI(model=MODEL)
ai_bot = Agent(gpt=gpt, chat_history=ChatHistory(max_turns=CHAT_HISTORY_MAX_TURNS), system_msg=SYSTEM_MSG_AI_MODE)

code_bot = Agent(gpt=gpt, chat_history=ChatHistory(max_turns=CHAT_HISTORY_MAX_TURNS), system_msg=SYSTEM_MSG_CODE_MODE)


def execute_command(cmd: str):
    print(f"INPUT: {cmd}")
    if cmd.startswith("a "):
        llm_input = cmd[2:]
        assistant_msg = ai_bot.chat(UserMsg(content=llm_input))
        result = assistant_msg.content
        print(f"✅> {result}")
    elif cmd.startswith("c "):
        llm_input = cmd[2:]
        assistant_msg = code_bot.chat(UserMsg(content=llm_input))
        result = assistant_msg.content
        print(f"✅> {result}")
    else:
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            messages = [SystemMsg(content=SYSTEM_MSG_TERMINAL_MODE), UserMsg(content=cmd)]
            response = gpt.generate_structured(messages=messages, output_format=TerminalCommand)
            if response.valid_terminal_command:
                print("\nAI suggestion:")
                print(f"→ {response.valid_terminal_command}")
                confirm = input("⚠️  Run this command? [y/N]: ").strip().lower()
                if confirm == "y":
                    print("✅ Executing:  ")
                    result = subprocess.run(response.valid_terminal_command, shell=True)
                    if result.returncode != 0:
                        print(f"⚠️ Command failed with exit code {result.returncode}")
                else:
                    print("❌️ Command cancelled.")
            else:
                execute_command(f"a {cmd}")
