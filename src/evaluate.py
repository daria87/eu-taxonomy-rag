import json
from pathlib import Path
from typing import Dict, List

from src.rag import retrieve


EVAL_PATH = "data/eval_questions.json"
K_VALUES = [1, 3, 5]


def load_eval_questions(path: str) -> List[Dict[str, str]]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def expected_source_found(retrieved_chunks: List[Dict], expected_source_id: str) -> bool:
    """
    Check whether the expected FAQ chunk ID appears in the retrieved results.
    """

    for chunk in retrieved_chunks:
        retrieved_source_id = chunk["metadata"]["source_id"]

        if retrieved_source_id == expected_source_id:
            return True

    return False


def evaluate_retrieval() -> None:
    eval_questions = load_eval_questions(EVAL_PATH)

    results_by_k = {k: 0 for k in K_VALUES}
    detailed_results = []

    for item in eval_questions:
        question = item["question"]
        expected_source_id = item["expected_source_id"]

        max_k = max(K_VALUES)
        retrieved = retrieve(question, k=max_k)

        row = {
            "question": question,
            "expected_source_id": expected_source_id,
            "retrieved_source_ids": [
                chunk["metadata"]["source_id"] for chunk in retrieved
            ],
            "retrieved_questions": [
                chunk["metadata"]["question"] for chunk in retrieved
            ],
        }

        for k in K_VALUES:
            found = expected_source_found(retrieved[:k], expected_source_id)
            row[f"recall@{k}"] = found

            if found:
                results_by_k[k] += 1

        detailed_results.append(row)

    total = len(eval_questions)

    print("Retrieval evaluation")
    print("-" * 80)
    print(f"Number of questions: {total}\n")

    for k in K_VALUES:
        score = results_by_k[k] / total
        print(f"Recall@{k}: {results_by_k[k]}/{total} = {score:.3f}")

    print("\nDetailed results")
    print("-" * 80)

    for row in detailed_results:
        print(f"\nQuestion: {row['question']}")
        print(f"Expected source ID: {row['expected_source_id']}")

        matched_at = None

        for k in K_VALUES:
            if row[f"recall@{k}"]:
                matched_at = k
                break

        if matched_at is None:
            print("Expected source found: no")
        else:
            print(f"Expected source found: top {matched_at}")

        print("Retrieved:")
        for i, (source_id, retrieved_question) in enumerate(
            zip(row["retrieved_source_ids"], row["retrieved_questions"]),
            start=1,
        ):
            print(f"  {i}. {source_id} | {retrieved_question}")

if __name__ == "__main__":
    evaluate_retrieval()