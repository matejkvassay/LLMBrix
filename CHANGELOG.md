# [2025/06/03]
- all missing docstrings added
- chat history method count_conv_turns() added
- new chatbot example demonstrating prompt reading and rendering
- fixed bug with ToolExecutor transforming outputs to str

# [2025/06/02]

- tool parameters made modular
- tools return ToolOutput and include debug metadata if viable
- tool executor includes stack trace and exception as metadata of tool message
- new "About Me" tool for chatbots
- missing docstrings added

# [2025/05/31]

- packaging fix, scripts and tests no longer included
- release of alpha v5
- PromptReader for YAML prompts implemented
- Prompt class with complete and partial rendering implemented
- custom exception added for incorrect prompt format

# [2025/05/28]

- release scripts added
- pyproject.toml finalized for release
- pre-alpha v0.1.0a3 released on test pypi and prod pypi

# [2025/05/26]

- transformation to responses API format
- new message classes
- improved history trimming performance with dequeue
- agent class reimplemented
- gpt class implemented
- package structure changed
- basic usage examples added
