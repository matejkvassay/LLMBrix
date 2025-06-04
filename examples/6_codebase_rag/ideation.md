# Anatomy of Python code base

## Reduced minimal rag data model
- only python files
-

## Initial ideation:

#### General:
1. file structure - what are full paths to all scripts, modules submodules etc
2. misc stuff -
    1. dockerfile
    2. readme
    3. data files
    4. pyproject.toml
    5. env examples
    6. setup.py
    7.  ipynb
    8.  sh scripts, ..
    9. configs (yaml, .cfg)
    10. python scripts.
3. not forget to filter out bullshit
    1.  __pychache__
    2. venv
    3. ...
    4.  everything gitignored) => use git ignore to filter out what shouldn't be read

#### Python files
- imports
- constants
- docstrings on top level
- functions on top - level
    - name, args, arg hints, code
    - docstring restructuredtext
        - desc
        - args desc
        - return
        - raises
    - code
    - inline comments
    - is private (starts with _)
    - decorators
- classes
    - parent class list
    - constructor
        - inherit function
    - class methods
        -  inherit function
        - is static
        - is classmethod
    - dunder methods
        - inherit function


## AI extended

# 🧬 Anatomy of a Python Repository

## 1. File Structure & Project Metadata

Includes full paths to:
- Python source files: `*.py` (scripts, modules, submodules)
- Jupyter Notebooks: `*.ipynb`
- Shell scripts: `*.sh`, `*.bat`
- Configuration files: `*.yaml`, `*.yml`, `.cfg`, `.ini`
- Docs: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- Containerization: `Dockerfile`, `docker-compose.yml`
- Project setup: `requirements.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`
- Environment variables: `.env`, `.env.example`, `.envrc`
- Assets: `data/`, `assets/`, `static/`, `docs/`
- Licensing: `LICENSE`
- Git submodules: `.gitmodules`

---

## 2. Noise Filtering

Exclude:
- `__pycache__/`, `*.pyc`
- `.venv/`, `venv/`, `env/`
- `dist/`, `build/`, `.egg-info/`
- `.git/`, `.mypy_cache/`, `.pytest_cache/`, `.tox/`, `.coverage`
- Everything in `.gitignore`
- Optional: custom `.ragignore` for RAG-specific filtering

Use libraries like `pathspec` to parse `.gitignore` programmatically.

---

## 3. Python Code Analysis

### File-Level
- Top-level docstring (module description)
- Top-level constants (e.g. `MY_CONSTANT = ...`)

### Imports
- All `import` / `from ... import ...`
  - Source
  - Aliases
  - Tag as: standard lib / 3rd-party / local module

### Functions (top-level or class methods)
- Name
- Args (with names, types, defaults)
- Return type
- Decorators (e.g. `@staticmethod`, `@classmethod`, `@mydecorator`)
- Is private? (starts with `_`)
- Is dunder? (starts and ends with `__`)
- Docstring (preferably parsed into components)
  - Summary
  - Args: name, type, description
  - Returns: type, description
  - Raises: exception, description
- Full source code
- Inline comments (including TODO, HACK)
- Optional: complexity, line count

### Classes
- Class name
- Inheritance (parent classes)
- Class-level docstring
- Constructor (`__init__`)
- Class methods:
  - All method properties as above
  - `@staticmethod`, `@classmethod`, `@property`
- Dunder methods (`__str__`, `__repr__`, etc.)
- Class-level variables

---

## 4. Advanced Enhancements (Optional)

- Call graph / dependency tree
- Type inference for missing hints (`pyright`, `mypy`)
- Docstring format normalization (Google/NumPy/ReST parsing)
- Embedding-ready JSON or chunks with metadata
- Linter diagnostics (`ruff`, `pylint`, `mypy`)
- Test analysis (`tests/` directory, `unittest`/`pytest` presence)
- Notebook parsing (`*.ipynb`: cells, markdown, code, imports)

---
