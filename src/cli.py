from src.rag import answer_question, get_collection


def main():
    print("EU Taxonomy FAQ Assistant")
    print("Ask one question at a time.")
    print("Type 'exit' or 'quit' to stop.\n")

    print("Loading FAQ retriever...")
    get_collection()
    print("Retriever ready.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Session ended.")
            break

        if not question:
            continue

        try:
            result = answer_question(question, k=3)

            print("\nAnswer:")
            print(result["answer"])

            if result["sources"]:
                print("\nSources:")
                for source in result["sources"][:2]:
                    print(f"- [{source['section']}] {source['question']}")
            else:
                print("\nSources: No relevant FAQ sources found.")

            print("\n" + "-" * 80 + "\n")

        except Exception as error:
            print("\nSomething went wrong while generating the answer.")
            print(f"Error: {error}")
            print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()