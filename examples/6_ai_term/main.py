from command_executor import execute_command

prefix = "(AI_TERM.py)>"


def main():
    while True:
        try:
            command = input(prefix)

            if command.lower() in ["exit", "quit", "exit()"]:
                print("Exiting shell.")
                break

            execute_command(command)

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: Type 'exit' to quit.")
        except Exception as e:
            print("Exception occurred:", str(e))


if __name__ == "__main__":
    main()
