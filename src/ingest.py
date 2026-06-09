import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from src.chunking import build_document_text, parse_faq_markdown


FAQ_PATH = "data/taxonomy_faqs_cleaned.md"
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "taxonomy_faqs"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"


def main():
    faqs = parse_faq_markdown(FAQ_PATH)

    print(f"Parsed {len(faqs)} FAQ chunks")

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name= EMBEDDING_MODEL_NAME
    )

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Recreate collection so ingestion is deterministic during development
    existing_collections = [collection.name for collection in client.list_collections()]

    if COLLECTION_NAME in existing_collections:
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    documents = []
    metadatas = []
    ids = []

    for i, faq in enumerate(faqs):
        doc_id = f"faq_{i:04d}"

        documents.append(build_document_text(faq))
        metadatas.append(
            {
                "source_id": doc_id,
                "section": faq["section"],
                "question": faq["question"],
            }
        )
        ids.append(doc_id)

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )

    print(f"Stored {collection.count()} FAQ chunks in Chroma")
    print(f"Vector database path: {CHROMA_PATH}")
    



if __name__ == "__main__":
    main()