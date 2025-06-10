import os
import readline
import subprocess
import sys

import pyperclip
from pydantic import BaseModel
from rich.console import Console
from rich.markdown import Markdown

from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import AssistantMsg, UserMsg

HIST_FILE = os.path.expanduser("~/.llmbrix_shell_history")
MODEL = "gpt-4o-mini"
TERMINAL_SYS_PROMPT = (
    "You will get a text user entered into a Unix terminal that failed.\n"
    "Fix it if it's a broken terminal command (e.g. typo).\n"
    "If it's natural language, convert it to a valid command.\n"
    "If unrelated, return empty string."
)


class TerminalCommand(BaseModel):
    valid_terminal_command: str


class GeneratedCode(BaseModel):
    python_code: str


ai_bot = Agent(
    gpt=GptOpenAI(model=MODEL),
    chat_history=ChatHistory(max_turns=5),
    system_msg="You are a concise assistant for use inside a narrow terminal window.",
)

code_bot = Agent(
    gpt=GptOpenAI(model=MODEL, output_format=GeneratedCode),
    chat_history=ChatHistory(max_turns=5),
    system_msg="You only respond with valid Python code. No explanations.",
)

terminal_bot = Agent(
    gpt=GptOpenAI(model=MODEL, output_format=TerminalCommand),
    chat_history=ChatHistory(max_turns=5),
    system_msg=TERMINAL_SYS_PROMPT,
)

console = Console()
current_dir = os.getcwd()
prev_dir = None

if os.path.exists(HIST_FILE):
    readline.read_history_file(HIST_FILE)
else:
    open(HIST_FILE, "a").close()

readline.set_history_length(1000)


def save_to_history(cmd):
    readline.add_history(cmd)
    readline.write_history_file(HIST_FILE)


def execute_cd_command(cmd: str, allow_ai=True):
    global prev_dir, current_dir
    path = cmd[3:].strip()
    if path == "-":
        if prev_dir:
            current_dir, prev_dir = prev_dir, current_dir
        else:
            console.print("❌  No previous directory")
            if allow_ai:
                execute_ai_term_command(cmd)
    else:
        expanded_path = os.path.expanduser(path)
        new_path = os.path.abspath(
            os.path.join(current_dir, expanded_path) if not os.path.isabs(expanded_path) else expanded_path
        )
        if os.path.isdir(new_path):
            prev_dir = current_dir
            current_dir = new_path
        else:
            console.print(f"❌  No such directory: {path}")
            if allow_ai:
                execute_ai_term_command(cmd)


def run_and_capture_output(cmd: str, cwd: str):
    process = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)
    return process.returncode, stdout, stderr


def execute_ai_term_command(cmd: str):
    response: AssistantMsg = terminal_bot.chat(UserMsg(content=cmd))
    generated_cmd = None
    if response.content_parsed and hasattr(response.content_parsed, "valid_terminal_command"):
        generated_cmd = response.content_parsed.valid_terminal_command
    if generated_cmd:
        console.print(f"💡 [bold yellow]AI Suggestion:[/bold yellow] `{generated_cmd}`")
        confirm = input("⚠️ Run this command? [y/N]: ").strip().lower()
        if confirm == "y":
            save_to_history(generated_cmd)
            if generated_cmd.startswith("cd "):
                execute_cd_command(generated_cmd, allow_ai=False)
            else:
                return_code, stdout, stderr = run_and_capture_output(generated_cmd, current_dir)
                if return_code == 0:
                    summary = (stdout or stderr)[:200]
                    terminal_bot.chat_history.add(AssistantMsg(content=f"Command returned: {summary}"))
                    console.print("✅ ")
        else:
            console.print("❌  Cancelled.")
    else:
        console.print("❌  No suggestion.")


def execute_ai_question(question: str):
    result = ai_bot.chat(UserMsg(content=question)).content
    console.print(Markdown(result))


def execute_code_gen_request(request: str):
    response: AssistantMsg = code_bot.chat(UserMsg(content=request))
    code = None
    if response.content_parsed and hasattr(response.content_parsed, "python_code"):
        code = response.content_parsed.python_code
    if code:
        pyperclip.copy(code)
        console.print(Markdown(code))
        console.print("✅ Copied to clipboard.")
    else:
        console.print("❌ Failed to generate code.")


def execute_command(cmd: str):
    global current_dir, prev_dir

    if cmd.startswith("cd "):
        execute_cd_command(cmd)
    elif cmd.startswith("a "):
        execute_ai_question(cmd[2:])
    elif cmd.startswith("c "):
        execute_code_gen_request(cmd[2:])
    else:
        process = subprocess.Popen(
            cmd, shell=True, cwd=current_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate()

        if stdout:
            print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)

        if process.returncode != 0 and stderr.strip():
            execute_ai_term_command(cmd)


def read_multiline_input(prompt: str) -> str:
    console.print("[grey42](Paste your input. Press Ctrl-D (EOF) on an empty line to finish.)[/grey42]")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


def main():
    console.print("[bold green]Welcome to AI Terminal (Blessed-based)[/bold green]")

    while True:
        try:
            prompt = f"[{os.path.basename(current_dir)}] > "
            cmd = input(prompt).strip()
            if cmd in {"exit", "quit", "q", "e"}:
                break
            if cmd == "a" or cmd.startswith("a \n"):
                full_input = read_multiline_input(prompt)
                if full_input:
                    execute_ai_question(full_input)
                continue
            if cmd:
                save_to_history(cmd)
                execute_command(cmd)
        except KeyboardInterrupt:
            print()
        except EOFError:
            print()
            break


if __name__ == "__main__":
    main()
