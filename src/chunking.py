from pathlib import Path
import re
from typing import Dict, List


def parse_faq_markdown(path: str) -> List[Dict[str, str]]:
    """
    Parse the EU Taxonomy FAQ markdown file into FAQ-level chunks.

    Expected structure:
    ## Section title
    ### FAQ question
    Answer text
    """

    text = Path(path).read_text(encoding="utf-8")

    current_section = None
    current_question = None
    current_answer = []
    faqs = []

    def flush_question():
        nonlocal current_question, current_answer

        if current_section and current_question and current_answer:
            faqs.append(
                {
                    "section": current_section,
                    "question": current_question,
                    "answer": "\n".join(current_answer).strip(),
                }
            )

        current_question = None
        current_answer = []

    parts = re.split(r"(^#{2,3} .*$)", text, flags=re.MULTILINE)

    for part in parts:
        part = part.strip()

        if not part:
            continue

        if part.startswith("## "):
            flush_question()
            current_section = part.replace("## ", "", 1).strip()

        elif part.startswith("### "):
            flush_question()
            current_question = part.replace("### ", "", 1).strip()

        else:
            if current_question:
                current_answer.append(part)

    flush_question()

    return faqs


def build_document_text(faq: Dict[str, str]) -> str:
    """
    Build the text that will be embedded.

    The FAQ question is repeated to give it more weight during semantic
    retrieval, since user queries are often closer to the FAQ question than
    to the full answer text.
    """

    return (
        f"Section: {faq['section']}\n"
        f"Question: {faq['question']}\n"
        f"Question repeated for retrieval: {faq['question']}\n"
        f"Answer: {faq['answer']}"
    )