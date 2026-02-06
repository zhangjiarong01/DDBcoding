---
name: ddb-coding-skills
description: A comprehensive skill set for DolphinDB development. Includes a RAG system for searching documentation/tutorials, and a command-line executor for running DolphinDB scripts. Use this to find coding patterns (tutorials) or API details (manuals) and execute code.
license: MIT
metadata:
  author: ddb-user
  version: "2.0.0"
---

# DolphinDB Coding Skills

This skill empowers you to master DolphinDB development through a combination of **Actionable Tools** and **Structured Knowledge**.

## 🏗️ Structure Overview

The repository is organized to separate *tools* from *knowledge*, and *methodology* from *definitions*.

```text
DDBcoding/
├── references/             # 🧠 KNOWLEDGE BASE (Input for RAG)
│   ├── tutorials/          # [Methodology] Procedural guides, patterns, & tips.
│   └── api_manuals/        # [Facts] Declarative API definitions, function specs.
├── scripts/                # 🛠️ TOOLS & EXAMPLES
│   ├── rag/                # [Tool] GPU-Accelerated Search Service
│   ├── ddb_runner/         # [Tool] DDB Script Executor
│   └── dos_samples/        # [Examples] Raw .dos scripts referenced by tutorials
└── SKILL.md                # 🧭 You are here
```

---

## 🛠️ Part 1: Tools (Action)

These tools allow you to interface with the documentation and the database.

### 1. RAG Service (Search)
**Use Case**: "I don't know how to do X" or "What are the arguments for function Y?"
*   **Engine**: Uses `BAAI/bge-m3` (Requires **GPU**).
*   **Scope**: Searches everything in `references/`.

**Commands**:
*   **Update Index** (Run after editing references):
    ```bash
    uv run scripts/rag/ingest.py
    ```
*   **Start Server** (For persistent Agent use):
    ```bash
    uv run scripts/rag/mcp_server.py
    ```
*   **Quick Search** (CLI):
    ```bash
    uv run scripts/rag/cli_search.py "context of query"
    ```

### 2. DDB Executor (Run)
**Use Case**: "Execute this script" or "Test this code snippet."
*   **Config**: `scripts/ddb_runner/.env`
*   **Commands**:
    *   Run file: `uv run scripts/ddb_runner/execute.py scripts/dos_samples/moving_average.dos`
    *   Run code: `uv run scripts/ddb_runner/execute.py -c "print(1+1)"`

> **Note on `uv`**: If you encounter network errors downloading Python, ensure you have a local Python environment installed and use `python script.py` directly, or configure `uv` to use the system python.

---

## 🧠 Part 2: Knowledge (Learning)

The documentation is split to help you learn efficiently. **Use the RAG tool to search across both.**

### 📘 Tutorials (`references/tutorials/`)
*   **Type**: Procedural, Strategic, Skill-based.
*   **Content**: "How-to" guides, best practices, design patterns.
*   **Usage**: Read these to understand *how* to approach a problem.
*   **Example Topics**:
    *   `01_moving_averages.md`: How to calculate rolling windows (References `scripts/dos_samples/moving_average.dos`).

### 📕 API Manuals (`references/api_manuals/`)
*   **Type**: Declarative, Factual, Memory-based.
*   **Content**: Function signatures, parameter definitions, return types.
*   **Usage**: Search these when you know *what* you want to do but need the exact syntax.

---

## 🚀 Recommended Workflow

1.  **Search**: Use `scripts/rag/cli_search.py` to find a relevant tutorial or API doc.
2.  **Learn**: Read the Markdown file to understand the logic.
3.  **Examine**: Check the corresponding `.dos` script in `scripts/dos_samples/` if available.
4.  **Action**: Modify the script and run it using `scripts/ddb_runner/execute.py`.