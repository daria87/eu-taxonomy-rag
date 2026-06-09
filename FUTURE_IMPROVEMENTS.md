# Future Improvements

This prototype focuses on a simple, runnable RAG pipeline. The following improvements would be useful as next steps.

## Hybrid retrieval

The current system uses dense vector search only. Some FAQ questions depend on exact regulatory terms, such as `technical screening criteria`, `DNSH`, or `Taxonomy-alignment`.

A hybrid approach combining vector search with BM25 or keyword retrieval could improve recall for these cases.

## Reranking

A reranking step could improve the order of retrieved FAQ chunks. The current system uses Chroma vector search directly, so the top retrieved result is not always the most relevant FAQ.

A future version could retrieve a larger candidate set first, then rerank the candidates with a cross-encoder or sequence-to-sequence reranker such as MonoT5:

```text
retrieve top 10 chunks,
rerank query–chunk pairs,
send top 3 chunks to the LLM.
```

This would be especially useful when the correct FAQ is retrieved in the top 5 but not ranked first.

## Larger evaluation set

The current evaluation set contains 12 manually labelled questions. A larger set would give a more reliable picture of retrieval quality.

Useful additions would include:

- more paraphrased questions,
- more out-of-scope questions,
- similar questions with different expected FAQ entries,
- manually reviewed answer quality labels.

## Answer quality evaluation

The current metric evaluates retrieval, not generated answers.

Future evaluation could check whether answers are:

- grounded in the retrieved FAQ,
- complete enough,
- concise,
- free from outside knowledge,
- correct for out-of-scope questions.

## Stable source IDs

The current FAQ IDs are generated from the order of the FAQ entries in the markdown file, for example `faq_0000`.

This is acceptable for the current static dataset. If the FAQ file changes often, a more stable ID based on a hash of the FAQ question would be better.

## API or web interface

The current interface is a CLI. A future version could expose the same logic through:

- a FastAPI endpoint,
- a small Streamlit or Gradio interface,
- or another lightweight UI.