# Production-Grade RAG for Finance

Live bootcamp resources. A fully local RAG pipeline over real SEC filings:
Ollama runs the model (`qwen3.8:27B`) and the embeddings (`nomic-embed-text`),
Qdrant holds the vectors, RAGWire wires it together, and Chainlit puts a chat
UI on top. The only API key in the project is for LangSmith tracing.

## Setup, in order

1. Install [Ollama](https://ollama.com) and pull the two models:

```bash
ollama pull qwen3.8:27B
```

```bash
ollama pull nomic-embed-text
```

2. Install [uv](https://docs.astral.sh/uv/), then from this directory:

```bash
uv sync
```

```bash
uv run python -m ipykernel install --user --name finance-rag --display-name "Python (finance-rag-bootcamp)"
```

3. Start Qdrant (needs Docker):

```bash
docker compose up -d
```

4. Copy `.env.example` to `.env` and add your LangSmith key. Tracing is
   optional: without a key the pipeline still runs, you just get no traces.

5. Open `Finance_RAG_Bootcamp.ipynb` and pick the kernel
   "Python (finance-rag-bootcamp)".

6. After the notebook has ingested the filings, launch the chat UI:

```bash
uv run chainlit run app.py -w
```

## What is here

```
finance-rag-bootcamp/
├── Finance_RAG_Bootcamp.ipynb   the session: extraction, chunking, embeddings,
│                                ingestion with metadata, hybrid retrieval,
│                                grounded answers, refusal, an agent that
│                                decides its own filters
├── app.py                       Chainlit chat UI over the same pipeline
├── scripts/                     the notebook's finalized code as importable modules
│   ├── extraction.py            PDF to markdown (MarkItDown)
│   ├── chunking.py              one chunk per page (ragwire 1.6 page strategy)
│   ├── embeddings.py            nomic-embed-text via Ollama
│   ├── pipeline.py              get_rag(), used by the notebook and app.py
│   └── tools.py                 the agent's tools: get_filter_context,
│                                search_documents
├── db/                          the agent's SQLite memory, created on first run
├── config/finance_rag.yaml      the whole pipeline in one file
├── data/                        2024 10-K filings: Amazon, Alphabet, Meta
├── docker-compose.yml           one service: Qdrant on 6333
├── src/                         notebook source, built by tools/build_notebook.py
└── tools/
```

## Troubleshooting

- `Connection refused` on 6333: the Qdrant container is not running.
  `docker compose up -d` from this directory.
- First ingestion is the slow step: three filings are converted, chunked,
  embedded, and each one gets an LLM metadata pass. Re-running is fast,
  because unchanged files are hash-skipped.
- The model needs roughly 25 GB of memory. On a smaller machine, change
  `llm.model` in `config/finance_rag.yaml` to a smaller tag you have pulled.
  The pipeline is identical.
- If Ollama runs on another machine, set `base_url` under both `embeddings`
  and `llm` in the config to that machine's address.
- Every path in `config/finance_rag.yaml` is relative and stays valid if you
  move the project. `metadata.config_file` resolves against the config file's
  own directory (ragwire 1.6.1), so the MCP server works no matter which
  directory Claude launches it from.
- MCP: the server entry must carry `"env": {"LANGSMITH_TRACING": "false"}`.
  RAGWire's config loader finds this project's `.env` and turns LangSmith
  tracing on inside the MCP server, and the first traced chain then shells
  out to `git` for run metadata. Inside a stdio MCP server that subprocess
  never returns: the tool call hangs, the client times out at 60 seconds,
  and the GPU sits idle the whole time. With tracing off, `answer_question`
  answers in about ten seconds warm.
- MCP: a cold `answer_question` call also pays the model load, which can
  exceed a 60 second client timeout. In Claude Code, launch with
  `MCP_TOOL_TIMEOUT=180000` for margin. `search_documents` and
  `collection_stats` are fast. The server handles one call at a time, so
  parallel calls queue behind each other. Keep the model warm before a demo:
  Ollama unloads it after a few minutes idle, and the reload is the slowest
  part of a cold call.
- A one-off Qdrant `408 Request Timeout` at MCP startup has been seen once;
  the client's automatic reconnect handled it.
