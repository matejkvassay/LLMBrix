import glob
import os
import subprocess
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from pydantic import BaseModel

from llmbrix.agent import Agent
from llmbrix.chat_history import ChatHistory
from llmbrix.gpt_openai import GptOpenAI
from llmbrix.msg import AssistantMsg, SystemMsg, UserMsg

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
HIST_FILE = os.path.expanduser("~/.llmbrix_shell_history")
MODEL = "gpt-4o-mini"
TERMINAL_SYS_PROMPT = (
    "You will get a text user entered into a Unix terminal that failed.\n"
    "Fix it if it's a broken terminal command (e.g. typo).\n"
    "If it's natural language, convert it to a valid command.\n"
    "If unrelated, return empty string."
)


# ─────────────────────────────────────────────────────────────────────────────
# AI SETUP


class TerminalCommand(BaseModel):
    valid_terminal_command: str


chat_history_terminal = ChatHistory(max_turns=3)
chat_history_terminal.add(SystemMsg(content=TERMINAL_SYS_PROMPT))

gpt = GptOpenAI(model=MODEL)

ai_bot = Agent(
    gpt=gpt,
    chat_history=ChatHistory(max_turns=5),
    system_msg="You are a concise assistant for use inside a narrow terminal window.",
)

code_bot = Agent(
    gpt=gpt,
    chat_history=ChatHistory(max_turns=5),
    system_msg="You only respond with valid Python code. No explanations.",
)


# ─────────────────────────────────────────────────────────────────────────────
# SHELL COMPLETER
class ShellCompleter(Completer):
    def get_completions(self, document, complete_event):
        global current_dir

        text = document.text_before_cursor.lstrip()
        words = text.split()

        if not words:
            return

        first = words[0]
        is_first = document.cursor_position <= len(first)

        if is_first:
            # Complete command names from PATH
            paths = os.environ.get("PATH", "").split(os.pathsep)
            seen = set()
            for path in paths:
                try:
                    for entry in os.listdir(path):
                        if entry not in seen and entry.startswith(first):
                            seen.add(entry)
                            yield Completion(entry, start_position=-len(first))
                except Exception:
                    continue
        else:
            # File/dir completion from current_dir
            current = document.get_word_before_cursor()

            # Handle things like ~, ., .. correctly
            prefix = os.path.expanduser(current)
            if not os.path.isabs(prefix):
                prefix = os.path.join(current_dir, prefix)

            matches = glob.glob(prefix + "*")

            for match in matches:
                # Show relative path instead of full one
                display = os.path.relpath(match, current_dir)
                yield Completion(display, start_position=-len(current))


# ─────────────────────────────────────────────────────────────────────────────
# SHELL STATE + EXECUTION

current_dir = os.getcwd()
prev_dir = None


def execute_cd_command(cmd: str, allow_ai=True):
    global prev_dir, current_dir
    path = cmd[3:].strip()

    if path == "-":
        if prev_dir:
            current_dir, prev_dir = prev_dir, current_dir
        else:
            print("❌  No previous directory")
            if allow_ai:
                execute_ai_term_command(cmd)
            return
    else:
        expanded_path = os.path.expanduser(path)
        new_path = os.path.abspath(
            os.path.join(current_dir, expanded_path) if not os.path.isabs(expanded_path) else expanded_path
        )
        if os.path.isdir(new_path):
            prev_dir = current_dir
            current_dir = new_path
        else:
            print(f"❌  No such directory: {path}")
            if allow_ai:
                execute_ai_term_command(cmd)
            return


def run_and_capture_output(cmd: str, cwd: str):
    process = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout = []
    stderr = []

    while True:
        out_line = process.stdout.readline()
        err_line = process.stderr.readline()
        if out_line:
            stdout.append(out_line)
            print(out_line, end="")
        if err_line:
            stderr.append(err_line)
            print(err_line, end="", file=sys.stderr)
        if out_line == "" and err_line == "" and process.poll() is not None:
            break
    return process.returncode, "".join(stdout), "".join(stderr)


def execute_ai_term_command(cmd: str):
    chat_history_terminal.add(UserMsg(content=cmd))
    response = gpt.generate_structured(messages=chat_history_terminal.get(), output_format=TerminalCommand)
    suggestion = response.valid_terminal_command
    chat_history_terminal.add(AssistantMsg(content=str(response.model_dump(mode="json"))))
    if suggestion:
        print(f"💡 AI Suggestion: {suggestion}")
        confirm = input("⚠️ Run this command? [y/N]: ").strip().lower()
        if confirm == "y":
            return_code, stdout, stderr = run_and_capture_output(suggestion, current_dir)
            if return_code == 0:
                if stdout:
                    stdout = stdout[:200]
                else:
                    stdout = stderr[:200]
                chat_history_terminal.add(AssistantMsg(content=f"Command returned: {stdout}"))
                print("✅ ")
        else:
            print("❌  Cancelled.")
    else:
        print("❌  No suggestion.")


def execute_ai_question(question: str):
    result = ai_bot.chat(UserMsg(content=question)).content
    print(result)
    return


def execute_code_gen_request(request: str):
    result = code_bot.chat(UserMsg(content=request)).content
    print(result)
    return


def execute_command(cmd: str):
    global current_dir, prev_dir

    if cmd.startswith("cd "):
        execute_cd_command(cmd)
        return

    elif cmd.startswith("a "):
        execute_ai_question(cmd[2:])

    elif cmd.startswith("c "):
        execute_code_gen_request(cmd[2:])

    else:
        result = subprocess.run(cmd, shell=True, cwd=current_dir)
        if result.returncode != 0:
            execute_ai_term_command(cmd)
        return


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP


def main():
    global current_dir

    style = Style.from_dict(
        {
            "": "",  # default style
            "prompt": "ansicyan bold",
        }
    )

    session = PromptSession(completer=ShellCompleter(), history=FileHistory(HIST_FILE), style=style)

    while True:
        try:
            prompt = f"[{os.path.basename(current_dir)}] > "
            cmd = session.prompt(prompt).strip()  # ← FIXED: no style override
            if cmd in {"exit", "exit()", "quit", "e", "q"}:
                break
            if cmd:
                execute_command(cmd)
        except KeyboardInterrupt:
            print()
        except EOFError:
            print()
            break


if __name__ == "__main__":
    main()
