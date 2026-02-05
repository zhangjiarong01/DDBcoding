---
name: ddb-rag-agent
description: A RAG (Retrieval-Augmented Generation) skill for DolphinDB. It provides document ingestion, vector search, and a DolphinDB execution interface via an MCP server. Use this skill to index markdown docs, search for coding examples, or execute DolphinDB scripts.
license: MIT
metadata:
  author: ddb-user
  version: "1.0.0"
---

# DolphinDB RAG Skill

This skill allows you to run a local RAG system tailored for DolphinDB. It enables you to index markdown files, perform semantic searches, and execute DolphinDB code against a live server.

## 📂 Structure Overview

To understand how this skill works, explore the following directories:

-   **`scripts/`**: The core executable logic.
    -   [`ingest.py`](scripts/ingest.py): Run this to scan docs and update embeddings.
    -   [`server.py`](scripts/server.py): Run this to start the MCP server (Exposes Search & Execute tools).
    -   [`search.py`](scripts/search.py): Run this to test search results locally without starting the full server.
-   **`my_markdown_files/`**: **(Input)** Place your knowledge base (Markdown files) here.
-   **`references/`**: Additional documentation and project READMEs.
-   **`storage_data/`** & **`lancedb_data/`**: **(Output)** Generated indices and vector databases.

## ⚙️ Configuration

Before running any scripts, ensure your environment is configured in the `.env` file located at the root of this skill folder ([`.env`](.env)).

**Important:** You must create or edit this file to match your environment.

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| **DolphinDB Connection** | | |
| `DDB_HOST` | IP address of the DolphinDB server | `183.134.101.137` |
| `DDB_PORT` | Port of the DolphinDB server | `8652` |
| `DDB_USER` | Username | `admin` |
| `DDB_PASS` | Password | `123456` |
| **MCP Server** | | |
| `MCP_HOST` | Local binding IP for the Agent | `192.168.100.43` |
| `MCP_PORT` | Port for the Agent service | `7731` |
| **Paths** | | |
| `DOCS_DIR` | Path to source markdown files | `./my_markdown_files` |
| `PERSIST_DIR` | Path for metadata storage | `./storage_data` |
| `DB_URI` | Path for vector storage | `./lancedb_data` |

## 🚀 Usage Guide

Follow these steps to set up and use the skill.

### 1. Configure the Environment
Check the [`.env`](.env) file and ensure the DolphinDB connection details and paths are correct for your setup.

### 2. Ingest Documents (Update Knowledge Base)
Whenever you add or modify files in [`my_markdown_files/`](my_markdown_files/), you must rebuild the index.

```bash
uv run scripts/ingest.py
```
*   **What it does:** Reads files from `DOCS_DIR`, generates embeddings (using `BAAI/bge-m3`), and saves them to `DB_URI`.
*   **Output:** Updates `storage_data/` and `lancedb_data/`.

### 3. Start the MCP Server
This starts the agent interface that allows LLMs to interact with your data and database.

```bash
uv run scripts/server.py
```
*   **Tools Provided:**
    *   `search_knowledge_base(query)`: Searches the ingested documents.
    *   `execute_ddb_code(code)`: Runs code on the configured DolphinDB server.

### 4. (Optional) Test Search
To quickly verify that your documents are indexed correctly without starting the full server:

```bash
uv run scripts/search.py
```
