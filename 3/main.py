from collections import defaultdict
import re


def build_inverted_index(docs: list[str]):
    inverted_index = defaultdict(set)
    for doc_id, document in enumerate(docs):
        tokens = set(re.split(r"\s*&\s*|\s*\|\s*", document))
        for token in tokens:
            inverted_index[token].add(doc_id)
    return inverted_index


# Пример использования
documents = [
    "word1 & word2 | word3",
    "word1 | word2 | word3",
    "word1 & word2 & word3",
]

inverted_index = build_inverted_index(documents)
for word, doc_ids in inverted_index.items():
    print(f"Word '{word}' is in documents: {doc_ids}")
