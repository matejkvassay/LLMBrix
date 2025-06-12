import glob
import os
import readline
import subprocess
import time

import pyperclip
from blessed import Terminal
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
term = Terminal()
current_dir = os.getcwd()
prev_dir = None

if os.path.exists(HIST_FILE):
    readline.read_history_file(HIST_FILE)
else:
    open(HIST_FILE, "a").close()
readline.set_history_length(1000)


# Helpers
def save_to_history(cmd):
    readline.add_history(cmd)
    readline.write_history_file(HIST_FILE)


def complete_path(token):
    if os.path.sep in token:
        dir_part, base = os.path.split(token)
        search_dir = os.path.join(current_dir, dir_part)
        pattern = os.path.join(search_dir, base + "*")
        matches = glob.glob(pattern)
        return [os.path.join(dir_part, os.path.basename(m)) for m in matches]
    else:
        pattern = os.path.join(current_dir, token + "*")
        matches = glob.glob(pattern)
        return [os.path.basename(m) for m in matches]


def execute_cd_command(cmd: str, allow_ai=True):
    global prev_dir, current_dir
    path = cmd[3:].strip()
    if path == "-":
        if prev_dir:
            current_dir, prev_dir = prev_dir, current_dir
        else:
            console.print("[bold red]❌ No previous directory[/bold red]")
            if allow_ai:
                execute_ai_term_command(cmd)
    else:
        expanded = os.path.expanduser(path)
        new_path = os.path.abspath(os.path.join(current_dir, expanded) if not os.path.isabs(expanded) else expanded)
        if os.path.isdir(new_path):
            prev_dir = current_dir
            current_dir = new_path
        else:
            console.print(f"[bold red]❌ No such directory:[/bold red] [italic]{path}[/italic]")
            if allow_ai:
                execute_ai_term_command(cmd)


def run_and_capture_output(cmd: str, cwd: str):
    try:
        base = cmd.split()[0]
        if base in {"htop", "top", "less", "nano", "vim"}:
            code = subprocess.call(cmd, shell=True, cwd=cwd)
            return code, "", ""
        proc = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()

        if out.strip():
            console.print(out.strip(), style="green")
        if err.strip():
            style = "yellow" if proc.returncode == 0 else "bold red"
            console.print(err.strip(), style=style)

        return proc.returncode, out, err

    except FileNotFoundError:
        console.print(f"[bold red]❌ Command not found:[/bold red] {cmd}")
        return 127, "", ""


def execute_ai_term_command(cmd: str):
    resp: AssistantMsg = terminal_bot.chat(UserMsg(content=cmd))
    suggestion = getattr(resp.content_parsed, "valid_terminal_command", None)
    if suggestion:
        console.print(f"\n💡 [bold yellow]AI Suggestion:[/bold yellow] [bold cyan]{suggestion}[/bold cyan]\n")
        confirm = input("⚠️ Run this command? [y/N]: ").strip().lower()
        if confirm == "y":
            save_to_history(suggestion)
            if suggestion.startswith("cd "):
                execute_cd_command(suggestion, allow_ai=False)
            else:
                code, out, err = run_and_capture_output(suggestion, current_dir)
                if code == 0:
                    terminal_bot.chat_history.add(AssistantMsg(content=f"Command returned: {out or err}"))
                    console.print("[bold green]✅ Command executed successfully[/bold green]")
        else:
            console.print("[bold red]❌ Cancelled[/bold red]")
    else:
        console.print("[bold red]❌ No suggestion[/bold red]")


def execute_ai_question(question: str):
    res = ai_bot.chat(UserMsg(content=question)).content
    console.print(Markdown(res))


def execute_code_gen_request(request: str):
    res: AssistantMsg = code_bot.chat(UserMsg(content=request))
    code = getattr(res.content_parsed, "python_code", None)
    if code:
        pyperclip.copy(code)
        console.print(Markdown(code))
        console.print("[bold green]✅ Copied to clipboard[/bold green]")
    else:
        console.print("[bold red]❌ Failed to generate code[/bold red]")


def execute_command(cmd: str):
    if cmd.startswith("cd "):
        execute_cd_command(cmd)
    elif cmd.startswith("a "):
        execute_ai_question(cmd[2:])
    elif cmd.startswith("c "):
        execute_code_gen_request(cmd[2:])
    else:
        code, out, err = run_and_capture_output(cmd, current_dir)
        if code != 0 and not err.strip():
            execute_ai_term_command(cmd)


def read_multiline_input() -> str:
    console.print("[grey42](Paste your input. Press Ctrl-D on empty line to finish.)[/grey42]")
    lines = []
    try:
        while True:
            lines.append(input())
    except EOFError:
        pass
    return "\n".join(lines)


def blessed_input_prompt(prompt_str: str) -> str:
    buffer = []
    cursor = 0
    history = readline.get_current_history_length()
    hidx = history
    blink = True
    last = time.time()

    with term.cbreak(), term.hidden_cursor():
        print(term.move_x(0) + term.clear_eol + term.bold_blue(prompt_str), end="", flush=True)
        while True:
            now = time.time()
            k = term.inkey(timeout=0.1)
            if k.code in (term.KEY_ENTER, term.KEY_RETURN):
                print(term.move_x(0) + term.clear_eol, end="", flush=True)
                return "".join(buffer)
            if k.code == term.KEY_BACKSPACE and cursor > 0:
                del buffer[cursor - 1]
                cursor -= 1
            elif k.code == term.KEY_DELETE and cursor < len(buffer):  # ✅ add this
                del buffer[cursor]
            elif k.code == term.KEY_LEFT and cursor > 0:
                cursor -= 1
                blink = True
                last = now
            elif k.code == term.KEY_RIGHT and cursor < len(buffer):
                cursor += 1
                blink = True
                last = now
            elif k.code == term.KEY_UP and hidx > 0:
                hidx -= 1
                buf = readline.get_history_item(hidx + 1) or ""
                buffer = list(buf)
                cursor = len(buffer)
            elif k.code == term.KEY_DOWN:
                if hidx < readline.get_current_history_length() - 1:
                    hidx += 1
                    buf = readline.get_history_item(hidx + 1) or ""
                    buffer = list(buf)
                    cursor = len(buffer)
                else:
                    hidx = readline.get_current_history_length()
                    buffer = []
                    cursor = 0
            elif k.code == term.KEY_TAB:
                pre = "".join(buffer[:cursor])
                parts = pre.split()
                last_tok = parts[-1] if parts else ""
                matches = complete_path(last_tok)
                if matches:
                    if len(matches) == 1:
                        sug = matches[0]
                        start = pre.rfind(last_tok)
                        new = pre[:start] + sug
                        buffer = list(new) + buffer[cursor:]
                        cursor = len(new)
                    else:
                        print("\n" + "  ".join(matches))
                        print(
                            term.move_x(0) + term.clear_eol + term.bold_blue(prompt_str) + "".join(buffer),
                            end="",
                            flush=True,
                        )
            elif not k.is_sequence and k:
                buffer.insert(cursor, k)
                cursor += 1

            if now - last > 0.5:
                blink = not blink
                last = now
            vis = "".join(buffer)
            print(f"\r{term.move_x(0)}{term.clear_eol}{term.bold_blue(prompt_str)}{vis}", end="", flush=True)
            print(term.move_x(len(prompt_str) + cursor), end="", flush=True)
            char = buffer[cursor] if cursor < len(buffer) else " "
            if blink:
                print(term.reverse(char), end="", flush=True)
            else:
                print(char, end="", flush=True)


def run():
    console.print(
        "\n[bold green]🚀 Welcome to [underline]AI Terminal[/underline][bold green] (Blessed-based)[/bold green]\n"
    )
    while True:
        try:
            prompt = f"{os.path.basename(current_dir)} > "
            cmd = blessed_input_prompt(prompt).strip()
            if cmd in {"exit", "quit", "q", "e"}:
                break
            if cmd.startswith("a ") or cmd == "a":
                full = read_multiline_input() if cmd == "a" else cmd[2:]
                if full:
                    execute_ai_question(full)
            elif cmd:
                save_to_history(cmd)
                execute_command(cmd)
        except KeyboardInterrupt:
            print()
        except EOFError:
            print()
            break
