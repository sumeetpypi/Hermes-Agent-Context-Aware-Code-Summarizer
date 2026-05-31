# Context-Aware Code Summarizer

A static analysis and documentation tool that scans Python project directories, tracks file-level changes using MD5 hashing, extracts structural metadata via AST parsing, and maintains a persistent skeleton cache of your codebase.

---

## Overview

This tool monitors a target project directory for modifications across watched file extensions. When changes are detected, it re-parses affected Python files to extract class definitions, method signatures, and docstrings, then writes the updated structural index back to a persistent JSON cache. A secondary file crawler leverages the Hermes Agent shell environment for direct file read operations within active terminal sessions.

---

## Features

- Directory scanning with configurable exclusion lists and file extension filters
- MD5-based change detection to avoid redundant re-parsing
- AST-based extraction of classes, methods, functions, and module docstrings
- Persistent skeleton cache stored as a JSON index file
- Automatic purging of deleted file entries from the cache
- Shell-integrated file reading via the Hermes Agent terminal and file operations tools
- Configurable local LLM backend via `llama-server` (supports GGUF models)

---

## Project Structure

```
project-root/
|-- components/
|   |-- crawler.py            # Core directory scanner and change tracker
|   |-- fileReadCrawler.py    # Shell-integrated file reader using Hermes Agent
|   |-- parser.py             # AST-based Python code parser
|-- main.py                   # Entry point and user input handler
|-- server.bat                # llama-server startup script (Windows)
```

---

## Requirements

- Python 3.9 or higher
- Hermes Agent package (`hermes_agent`) with `terminal_tool` and `file_operations` modules
- `llama.cpp` server binary (for local LLM backend, optional)
- A GGUF-format model file if using the local inference server

---

## Configuration

The tool expects a `config.json` file in your designated config directory. Supported keys:

| Key                | Type            | Default                          | Description                                      |
|--------------------|-----------------|----------------------------------|--------------------------------------------------|
| `exclude_dirs`     | list of strings | `[".git", "__pycache__", "venv"]` | Directories to skip during scanning              |
| `watch_extensions` | list of strings | `[".py", ".json", ".md"]`        | File extensions to monitor                       |
| `output_dir`       | string          | `"docs"`                         | Directory where generated documentation is saved |
| `project_name`     | string          | `"System"`                       | Project name used in generated output headers    |
| `target_file`      | string          | `"ARCHITECTURE.md"`              | Output documentation file name                  |

Example `config.json`:

```json
{
  "exclude_dirs": [".git", "__pycache__", "venv", "node_modules"],
  "watch_extensions": [".py", ".json", ".md"],
  "output_dir": "docs",
  "project_name": "MyProject",
  "target_file": "ARCHITECTURE.md"
}
```

---

## Usage

Run the tool from the project root:

```bash
python main.py
```

You will be prompted for three paths:

1. **Target project path** - the root directory of the project you want to scan
2. **Config directory path** - the directory containing your `config.json`
3. **Skeleton cache path** - the directory where `project_skeleton.json` will be stored

Paths can be pasted directly (including drag-and-drop paths with surrounding quotes; these are stripped automatically).

---

## Hermes Agent Integration

The `ProjectFileCrawler` class reads files via `ShellFileOperations`, which requires an active Hermes Agent terminal session. A terminal session must be initialized before constructing a `ProjectFileCrawler` instance, as the crawler extracts the active environment from the `_active_environments` global registry.

If no active environment is found, a `RuntimeError` is raised with the message:

```
No active environment sessions found. Run a terminal_tool command first.
```

---

## Local LLM Server (Windows)

The included `server.bat` launches a `llama-server` instance for local inference. Edit the `MODEL_PATH` variable to point to your GGUF model file before running.

Default settings:

| Parameter    | Value  |
|--------------|--------|
| Context size | 8192   |
| Port         | 8080   |
| Threads      | 12     |

To start the server:

```bat
server.bat
```

---

## Hermes Agent: Editing `MINIMUM_CONTEXT_LENGTH`

To modify the `MINIMUM_CONTEXT_LENGTH` variable used by the Hermes Agent for metadata file processing, locate the configuration or constants file within the `hermes_agent` package (typically `hermes_agent/config.py` or `hermes_agent/constants.py`) and update the variable directly:

```python
# hermes_agent/config.py (or constants.py)
MINIMUM_CONTEXT_LENGTH = 512  # Set to your required minimum token count
```

To allow the agent to locate and edit this value dynamically at runtime, pass an updated `max_tokens` value when constructing the agent or calling the relevant tool. The agent reads `MINIMUM_CONTEXT_LENGTH` to decide whether the current context window is large enough to process a metadata file. If the context is below this threshold, the agent will skip or defer the operation.

If you are extending the Hermes Agent to support editing this variable programmatically, add a configuration setter in the agent initialization path and expose it as a parameter in the tool interface.

---

## Known Limitations

- Non-Python files (`.json`, `.md`) are logged as changed but do not undergo structural parsing. Full parsing support for these types is noted as not yet implemented.
- The `DocumentationGenerator.generate_architecture_markdown` method is currently commented out in `main.py` and is not active.
- The file crawler requires an active Hermes Agent terminal session and will fail if invoked without one.

---

## License

This project does not currently include a license file. All rights reserved until a license is specified.
