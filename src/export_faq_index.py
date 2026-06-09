import json
from pathlib import Path

from src.chunking import parse_faq_markdown


FAQ_PATH = "data/taxonomy_faqs_cleaned.md"
OUTPUT_PATH = "data/faq_questions_with_ids.json"


def main():
    faqs = parse_faq_markdown(FAQ_PATH)

    faq_index = []

    for i, faq in enumerate(faqs):
        source_id = f"faq_{i:04d}"

        faq_index.append(
            {
                "source_id": source_id,
                "section": faq["section"],
                "question": faq["question"],
            }
        )

    output_path = Path(OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(faq_index, file, indent=2, ensure_ascii=False)

    print(f"Exported {len(faq_index)} FAQ records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()