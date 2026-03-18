# 🧠 Graph RAG — Knowledge Graph + Vector Hybrid Retrieval

A hybrid Retrieval-Augmented Generation (RAG) system that combines a **Neo4j knowledge graph** with a **ChromaDB vector store** to answer questions using structured relationships AND raw text passages.

Built on top of Game of Thrones text as a demo, but works with any PDF document.

---

## 📐 Architecture Overview

```
PDF Document
     │
     ▼
┌─────────────┐
│  Text       │  loading_txt.py
│  Extraction │
└─────────────┘
     │
     ▼
┌─────────────┐
│   Chunker   │  chunker.py
└─────────────┘
     │
     ├──────────────────────────────────────┐
     ▼                                      ▼
┌──────────────────────┐        ┌──────────────────────┐
│  Entity & Relation   │        │   Vector Store        │
│  Extraction (LLM)    │        │   (ChromaDB)          │
│  entity_relation_    │        │   query_processing_   │
│  extracter.py        │        │   for_vectorDB.py     │
└──────────────────────┘        └──────────────────────┘
     │                                      │
     ▼                                      │
┌──────────────────────┐                   │
│  Neo4j Graph DB      │                   │
│  graph_builder.py    │                   │
└──────────────────────┘                   │
     │                                      │
     ▼                                      ▼
┌──────────────────────┐        ┌──────────────────────┐
│  Graph Retrieval     │        │  Vector Retrieval     │
│  query_processing_   │        │  (MMR Search)         │
│  for_graphDB.py      │        │                       │
└──────────────────────┘        └──────────────────────┘
     │                                      │
     └──────────────┬───────────────────────┘
                    ▼
          ┌──────────────────┐
          │  Context Merger  │  context_formater.py
          └──────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │  LLM Answer Gen  │  hybrid_retriever.py
          └──────────────────┘
                    │
                    ▼
               Final Answer
```

---

## 🗂️ File Reference

### `config.py`
Loads all environment variables and sets the LLM model configuration.

- Reads `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `GROQ_API_KEY` from `.env`
- Defines three model tiers you can switch between:
  - `best_model` — most capable, slower
  - `fastest_model` — optimized for speed
  - `thinking_model` — reasoning-focused (default)
- Set `GROQ_MODEL` to whichever tier you want to use

---

### `schemas.py`
Defines all Pydantic data models used across the project.

| Schema | Purpose |
|---|---|
| `NodeProperty` | A key-value pair attached to a node or relationship |
| `Node` | A graph node with name, type (e.g. `PERSON`), and optional properties |
| `Relationship` | A directed edge between two nodes with a type (e.g. `WORKS_AT`) |
| `KnowledgeGraph` | A container holding a list of nodes and relationships |
| `ExtractEntities` | LLM output schema for named entity extraction from a query |
| `KHopDecision` | LLM output schema for deciding how many graph hops (k=1,2,3) a query needs |

---

### `prompts.py`
Holds all system and user prompt templates used by the LLMs.

| Prompt | Used By | Purpose |
|---|---|---|
| `graph_builder_system_prompt` | `entity_relation_extracter.py` | Instructs LLM to always respond using the KnowledgeGraph function call |
| `extraction_prompt` | `entity_relation_extracter.py` | Extracts nodes and relationships from a text chunk |
| `entity_extracter_system_prompt` | `query_processing_for_graphDB.py` | Extracts named entities from a user query |
| `KHop_system_prompt` | `query_processing_for_graphDB.py` | Decides how many hops (k) are needed to answer a query |
| `hybrid_retriever_system_prompt` | `hybrid_retriever.py` | Instructs the answer LLM to use only provided context, no outside knowledge |
| `hybrid_retriver_search_prompt` | `hybrid_retriever.py` | Injects combined context + query into the final answer prompt |

---

### `llm.py`
Factory function for creating LLM instances backed by Groq.

- Uses `langchain_openai.ChatOpenAI` pointed at Groq's OpenAI-compatible API
- Call `get_llm()` for a plain chat LLM
- Call `get_llm(output_schema=MyPydanticModel)` to get a structured output LLM via function calling

---

### `loading_txt.py`
Extracts plain text from a PDF file.

- Uses `pypdf.PdfReader` to read each page
- Skips the first page (typically a cover) and concatenates the rest
- Returns a single string of the full document text

---

### `chunker.py`
Splits extracted text into overlapping chunks for processing.

- Uses LangChain's `RecursiveCharacterTextSplitter`
- Default chunk size: **500 characters** with **100 character overlap**
- Overlap ensures context is not lost at chunk boundaries

---

### `entity_relation_extracter.py`
Uses an LLM to extract entities and relationships from each text chunk.

- Sends each chunk to the LLM with structured output bound to `KnowledgeGraph`
- Enforces consistent node types: `PERSON`, `HOUSE`, `LOCATION`, `EVENT`, etc.
- Skips chunks where nothing is extracted
- Adds a **2.1 second sleep** between calls to respect Groq rate limits
- Returns a list of `KnowledgeGraph` objects (one per chunk)

---

### `graph_builder.py`
Writes extracted knowledge graphs into Neo4j.

- Uses `MERGE` so duplicate nodes/relationships are never created
- Dynamically assigns Neo4j labels from the node's `type` field (e.g. `PERSON` → `:PERSON` label)
- Sanitizes labels: uppercased, spaces/hyphens replaced with underscores
- Stores node and relationship properties alongside the graph structure

---

### `cypher.py`
Contains the parameterized Cypher query used for k-hop graph retrieval.

- Accepts `$name` (starting node) and `{k}` (number of hops)
- Returns: entity name, types, properties, up to 30 neighbors, and up to 30 relationships
- Neighbors include hop distance so you can tell how directly something is connected

---

### `query_processing_for_graphDB.py`
Handles all query-side graph retrieval logic.

**Key functions:**

| Function | What it does |
|---|---|
| `extract_entity_from_query(query)` | Uses LLM to pull named entities (people, places, orgs) from the user's question |
| `select_k(query)` | Uses LLM to decide k=1, 2, or 3 hops based on query complexity |
| `fuzzy_find_node(session, entity)` | Tries exact → case-insensitive → substring match to find a node in Neo4j |
| `graph_retrieve_entity(entity, k)` | Fuzzy-finds a node then runs the k-hop Cypher query |
| `graph_retrieve_entities(entities, k)` | Loops over all extracted entities and retrieves each one |

---

### `query_processing_for_vectorDB.py`
Handles all query-side vector retrieval logic.

**Key functions:**

| Function | What it does |
|---|---|
| `build_vector_store(chunks)` | Embeds chunks using HuggingFace `all-mpnet-base-v2` and saves to ChromaDB |
| `load_vector_store()` | Loads the persisted ChromaDB from disk |
| `vector_retrieve(query, k=3)` | Runs **MMR (Maximal Marginal Relevance)** search — fetches 20 candidates and picks the 3 most relevant AND diverse results |

---

### `context_formater.py`
Formats and merges graph and vector results into a single context string for the LLM.

- `format_graph_context()` — renders entity types, properties, and relationships in a readable block
- `format_vector_context()` — labels each retrieved passage with a number
- `combine_context()` — places graph context first, then vector passages

---

### `hybrid_retriever.py`
The main end-to-end RAG pipeline. Orchestrates all retrieval steps and generates the final answer.

**Pipeline steps:**
1. Call `select_k()` to decide traversal depth
2. Call `extract_entity_from_query()` to find entities
3. Retrieve k-hop subgraph from Neo4j for each entity
4. Retrieve top-3 relevant chunks from ChromaDB using MMR
5. Merge both contexts into one string
6. Send merged context + original query to LLM for final answer generation

---

## 🚀 Running the Project

### Step 1 — Set up environment

Create a `.env` file in the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
GROQ_API_KEY=your_groq_api_key
```

Install dependencies:

```bash
pip install langchain langchain-openai langchain-huggingface langchain-chroma
pip install neo4j pypdf python-dotenv
```

---

### Step 2 — Build the Knowledge Graph (run once)

This step reads your PDF, extracts entities and relationships using the LLM, and stores everything in Neo4j.

```bash
python graph_creation_orchestrater.py
```

What it does internally:
1. Extracts text from `Game+of+Thrones.pdf`
2. Splits text into 500-character chunks
3. Sends each chunk to the LLM to extract nodes and relationships
4. Writes all extracted graphs into Neo4j using MERGE (idempotent)

> ⚠️ This step makes many LLM calls and may take several minutes depending on document size. A 2.1s rate-limit delay is built in between chunks.

---

### Step 3 — Build the Vector Store (run once)

Open `query_processing_for_vectorDB.py`, uncomment the build section at the bottom, and run:

```bash
python query_processing_for_vectorDB.py
```

This embeds all chunks using `sentence-transformers/all-mpnet-base-v2` and saves them to the `chroma_db/` folder. Once built, the vector store persists on disk and does not need to be rebuilt.

---

### Step 4 — Query the System

Run the hybrid retriever:

```bash
python hybrid_retriever.py
```

Or import and use it in your own script:

```python
from hybrid_retriever import hybrid_retrieve

answer = hybrid_retrieve("Who is Eddard Stark?")
print(answer)
```

---

## 🗺️ Neo4j Graph Visualization

Below is a screenshot of the knowledge graph built from the Game of Thrones document, visualized in the Neo4j Browser.

<!-- 📸 INSERT NEO4J SCREENSHOT HERE -->
> _Replace this section with your Neo4j Browser screenshot._
> _To capture it: open Neo4j Browser → run `MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100` → take a screenshot of the graph view._

---

## 📦 Project Structure

```
├── config.py                          # Env vars and model config
├── schemas.py                         # Pydantic data models
├── prompts.py                         # All LLM prompts
├── llm.py                             # LLM factory (Groq)
│
├── loading_txt.py                     # PDF → plain text
├── chunker.py                         # Text → overlapping chunks
│
├── entity_relation_extracter.py       # Chunks → KnowledgeGraph (LLM)
├── graph_builder.py                   # KnowledgeGraph → Neo4j
├── graph_creation_orchestrater.py     # ⭐ Run this to build the graph DB
│
├── cypher.py                          # k-hop Cypher query template
├── query_processing_for_graphDB.py    # Query → Neo4j retrieval
├── query_processing_for_vectorDB.py   # Query → ChromaDB retrieval (also builds store)
│
├── context_formater.py                # Merge graph + vector context
├── hybrid_retriever.py                # ⭐ Run this to query the system
│
├── chroma_db/                         # Persisted vector store (auto-created)
└── .env                               # API keys and DB credentials (not committed)
```

---

## 🔧 Configuration

To switch LLM models, edit `config.py`:

```python
GROQ_MODEL = best_model      # Most capable
GROQ_MODEL = fastest_model   # Fastest responses
GROQ_MODEL = thinking_model  # Reasoning (default)
```

To change chunk size, edit `chunker.py`:

```python
chunks = chunk_txt(text, chunk_size=800, overlap=150)
```

To retrieve more/fewer results, edit `hybrid_retriever.py`:

```python
chunks = vector_retrieve(query, k=5)   # More vector results
```

---
