![logo](./img/logo.png)

# About LLMBrix

- in early development, not a working version yet
- low abstraction LLM framework

# Development notes

### Install package

```bash
pip install -e '.[dev]'
```

### Configure pre-commit hook

```bash
pip install pre-commit
```

```bash
pre-commit install
```

### Run tests

```bash
pytest
```

### Env setup

#### OpenAI API key

This framework currently supports only OpenAI completion API
as an LLM backend. To enable it you have to configure env variable
with your API access token (see https://platform.openai.com/docs/quickstart for more details).

```bash
export OPENAI_API_KEY="<YOUR API TOKEN>"
```
