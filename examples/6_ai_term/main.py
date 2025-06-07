import atexit
import glob
import os
import readline
import subprocess

# Enable TAB completion (macOS/libedit compatible)
if "libedit" in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

# Add persistent history
histfile = os.path.expanduser("~/.llmbrix_shell_history")
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, histfile)


# Custom completer: complete file paths
def file_path_completer(text, state):
    line = readline.get_line_buffer().split()
    if not line or (len(line) == 1 and not text.startswith(".")):
        # Complete executables from PATH
        matches = [cmd for cmd in os.listdir("/bin") if cmd.startswith(text)]
    else:
        # Complete files/directories
        matches = glob.glob(text + "*")
    try:
        return matches[state]
    except IndexError:
        return None


readline.set_completer(file_path_completer)


def main():
    print("Welcome to your Python shell! Type 'exit' to quit.")

    while True:
        try:
            command = input("(llmbrix)>>> ")

            if command.lower() in ["exit", "quit", "exit()"]:
                print("Exiting shell.")
                break

            # Run shell command
            result = subprocess.run(command, shell=True)

            if result.returncode != 0:
                print(f"Command failed with exit code {result.returncode}")

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: Type 'exit' to quit.")
        except Exception as e:
            print("Exception occurred:", str(e))


if __name__ == "__main__":
    main()
