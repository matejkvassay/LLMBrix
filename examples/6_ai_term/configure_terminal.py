import atexit
import glob
import os
import readline

# config
HIST_MAX = 1000
HIST_FILE = "~/.llmbrix_shell_history"

# terminal setup
readline.set_history_length(HIST_MAX)
if "libedit" in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
hist_file = os.path.expanduser(HIST_FILE)
try:
    readline.read_history_file(hist_file)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, hist_file)


def file_path_completer(text, state):
    line = readline.get_line_buffer().split()
    if not line or (len(line) == 1 and not text.startswith(".")):
        matches = [cmd for cmd in os.listdir("/bin") if cmd.startswith(text)]
    else:
        matches = glob.glob(text + "*")
    try:
        return matches[state]
    except IndexError:
        return None


readline.set_completer(file_path_completer)
