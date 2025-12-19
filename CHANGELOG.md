# [2025/11/26]

- New `Graph` initialization options include specification of mixed sequence of nodes and edges
- `Graph.visualize()` is done in-memory and returns img bytes sequence to be displayed
- `Graph.run_iter()` yielding optimized to yield just before step execution / termination
- `graph` module docs improved
- `graph` module unit tests added

# [2025/11/25]

- New module `llmbrix.graph` for definition of agentic workflow graphs
- pre-commit config extended with removal of unused imports
- `tracing.py` module and Arize integration removed
- `AboutMe` tool removed

# [2025/08/17]

- Structured output format `BaseModel` configurable in `Agent`

# [2025/08/12]

- GPT 5 set as default model for examples
- Tracing silenced when Arize server not available
- OpenAI SDK upgrade

# [2025/08/02]

- Easier configuration of `OpenAI` / `AzureOpenAI` clients in `GptOpenAI` class
- New class methods `from_openai()` & `from_azure_openai` in `GptOpenAI`

# [2025/07/26]

- fixed bug when `AssistantMsg` with None content was added to history when tool calling in structured output `Agent`
- added support for `Arize Phoenix` tracing

# [2025/06/12]

- option to specify custom `OpenAI` or `AzureOpenAI` client in `GptOpenAI` wrapper

# [2025/06/09]

- refactor of `GptOpenai` class
- structured outputs supported in `generate()` function
- `generate_structured()` function removed
- new field `content_parsed` in `AssistantMsg` containing parsed structured ouput
- parsed output automatically converted to `str` and passed as `content` into `AssistantMsg` visible to LLM on predict
- responses API `**kwargs` can be now passed to `generate()` function
- `OpenAIResponseError` custom exception added

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
