# EU Taxonomy FAQ RAG Assistant

A Retrieval-Augmented Generation (RAG) application for answering questions from the EU Taxonomy Navigator FAQ dataset.

The app parses the FAQ markdown file, stores FAQ chunks in a local vector database, retrieves relevant FAQ entries for a user question, and generates an answer grounded in the retrieved context.

## Features

- FAQ-level chunking from markdown
- Local embeddings with `BAAI/bge-small-en-v1.5`
- Local vector storage and search with ChromaDB
- LLM-based answer generation
- CLI interface
- Source attribution
- Basic out-of-scope handling
- Retrieval evaluation with Recall@k

## Project structure

```text
.
├── data/
│   ├── taxonomy_faqs_cleaned.md
│   ├── eval_questions.json
│   └── faq_questions_with_ids.json
├── src/
│   ├── chunking.py
│   ├── ingest.py
│   ├── rag.py
│   ├── cli.py
│   ├── evaluate.py
│   └── export_faq_id_mapping.py
├── README.md
├── FUTURE_IMPROVEMENTS.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Approach

The FAQ markdown is parsed into FAQ-level chunks. Each chunk contains:

- the FAQ section,
- the FAQ question,
- the FAQ answer.

I chose FAQ-level chunking because the source data is already structured as question-answer pairs. This keeps each retrieval unit coherent.

Each FAQ chunk is embedded with `BAAI/bge-small-en-v1.5` and stored in ChromaDB. At query time, the user question is embedded with the same model, and the top retrieved FAQ chunks are passed to the LLM as context.

The generation prompt instructs the model to answer only from the retrieved FAQ context, avoid outside knowledge, and return a fallback message when the answer is not present in the FAQ.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
```


## Build the vector database

Run:

```bash
python -m src.ingest
```

This parses the FAQ markdown, creates embeddings, and stores the chunks in ChromaDB under `data/chroma_db/`.

Expected output:

```text
Parsed 328 FAQ chunks
Stored 328 FAQ chunks in Chroma
Vector database path: data/chroma_db
```

## Run the chatbot

Start the CLI:

```bash
python -m src.cli
```

Example question:

```text
Can companies without taxonomy-aligned activities still access finance?
```

Example answer:

```text
Companies without Taxonomy-aligned activities can still access finance. The absence of Taxonomy-aligned activities does not automatically indicate a company’s environmental performance or its ability to access finance.

Sources:
- [Climate Delegated Act] How about companies without any Taxonomy-aligned activities? Will they lose access to finance?
```

To stop the CLI, type:

```text
exit
```

## Evaluation

The evaluation focuses on retrieval quality.

The file `data/eval_questions.json` contains manually paraphrased user questions. Each question is mapped to the expected FAQ `source_id`.

The evaluation script checks whether the expected FAQ appears in the top-k retrieved chunks.

Run:

```bash
python -m src.evaluate
```

Current results:

| Metric   |         Score |
| -------- | ------------: |
| Recall@1 |  7/12 = 0.583 |
| Recall@3 |  9/12 = 0.750 |
| Recall@5 | 10/12 = 0.833 |

The application uses top-3 retrieval for answer generation as a balance between enough context and limited noise.

## Design choices

- **RAG instead of fine-tuning:** the knowledge is already available in the FAQ corpus, so the main task is retrieval and grounded answer generation.
- **FAQ-level chunking:** each FAQ question-answer pair is used as one chunk because the markdown is already structured that way.
- **ChromaDB:** used as a local vector database because the dataset is small and does not require external infrastructure.
- **Top-3 retrieval:** used for answer generation as a balance between enough context and limited noise.

## Notes

The embedding model is downloaded automatically from Hugging Face on first run. No Hugging Face token is required for the default public model.

The Chroma database is generated locally and is not committed to Git. It can be recreated with:

```bash
python -m src.ingest
```

Possible next steps are listed in `FUTURE_IMPROVEMENTS.md`.
