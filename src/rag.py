
import os
from typing import Dict, List

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "taxonomy_faqs"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")


def get_collection():
    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )


def retrieve(question: str, k: int = 3) -> List[Dict]:
    collection = get_collection()

    results = collection.query(
        query_texts=[question],
        n_results=k,
    )

    retrieved = []

    for doc, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append(
            {
                "document": doc,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return retrieved


def build_context(retrieved_chunks: List[Dict]) -> str:
    context_parts = []

    for i, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk["metadata"]

        context_parts.append(
            f"[FAQ {i}]\n"
            f"Section: {metadata['section']}\n"
            f"Question: {metadata['question']}\n"
            f"Content:\n{chunk['document']}"
        )

    return "\n\n".join(context_parts)


def answer_question(question: str, k: int = 3) -> Dict:
    retrieved_chunks = retrieve(question, k=k)
    context = build_context(retrieved_chunks)

    user_prompt = f"""
You are answering questions about the EU Taxonomy Navigator FAQ.

Use only the retrieved FAQ context.
Do not use outside knowledge.

The retrieved FAQ may contain its own original question and answer.
Treat the retrieved FAQ question as a source title only.
Answer the user's question, not the retrieved FAQ question.

Do not start the answer with "Yes" or "No".
Start with a full declarative sentence that directly answers the user's question.
Then add one or two short supporting sentences from the FAQ context.

If the answer is not present in the FAQ context, say:
"I could not find this information in the provided FAQ."

Answer clearly and concisely.
Do not refer to sources as "FAQ 1", "FAQ 2", etc.

FAQ context:
{context}

User question:
{question}

Answer:
""".strip()

    client = OpenAI()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful assistant. You answer only from the "
                    "provided EU Taxonomy FAQ context."
                ),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
    )

    answer = response.choices[0].message.content

    normalised_answer = answer.lower().strip()

    is_out_of_scope = (
        "could not find this information" in normalised_answer
        or "not present in the provided faq" in normalised_answer
        or "not found in the provided faq" in normalised_answer
    )

    sources = [] if is_out_of_scope else [
        {
            "section": chunk["metadata"]["section"],
            "question": chunk["metadata"]["question"],
            "distance": chunk["distance"],
        }
        for chunk in retrieved_chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":
    test_question = "What is the capital of Belgium?"

    result = answer_question(test_question, k=3)

    print("\nQuestion:")
    print(result["question"])

    print("\nAnswer:")
    print(result["answer"])

    if result["sources"]:
        print("\nSources:")
        for source in result["sources"][:2]:
            print(f"- [{source['section']}] {source['question']}")
    else:
        print("\nSources: No relevant FAQ sources found.")