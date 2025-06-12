def main():
    try:
        import blessed  # noqa: F401
        import pyperclip  # noqa: F401
        import rich  # noqa: F401
    except ImportError:
        print("The terminal app requires optional dependencies.")
        print('Install with: pip install "llmbrix[term]"')
        return
    from llmbrix.apps.terminal.term import run

    run()
