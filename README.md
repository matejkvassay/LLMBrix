![logo](https://github.com/matejkvassay/LLMBrix/blob/main/img/logo.png?raw=true)

# About LLMBrix

- in early alpha development do not use productively
- low abstraction LLM framework
- simple toolkit to create AI apps

# Install

```bash
pip install llmbrix --pre
```
# Use

See examples in `examples/` dir.

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

### Other

#### Release test install

```bash
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple \
            llmbrix --pre
```
