from collections import defaultdict
import re


def build_inverted_index(docs: list[str]):
    inverted_index = defaultdict(set)
    for doc_id, document in enumerate(docs):
        tokens = set(re.split(r"\s*&\s*|\s*\|\s*", document))
        for token in tokens:
            inverted_index[token].add(doc_id)
    return inverted_index


def boolean_search(index, query):
    result = None
    tokens = re.findall(r"[a-zA-Z0-9]+|\&|\||\!", query)
    print(tokens)
    print("========")

    # Проходимся по каждому токену в запросе
    for i, token in enumerate(tokens):
        if token == '&':
            # Логическое И
            result = result & index[tokens[i + 1]]
        elif token == '|':
            # Логическое ИЛИ
            result = result | index[tokens[i + 1]]
        elif token == '!':
            # Логическое НЕ
            result = result - index[tokens[i + 1]]
        elif result is None:
            # Если это первый операнд, присваиваем ему текущий результат
            result = index[token]

    return result


# Пример использования
documents = [
    "word1 & word2 | word3",
    "word1 | word2 | word3",
    "word1 & word2 & word3",
]

inverted_index = build_inverted_index(documents)
for word, doc_ids in inverted_index.items():
    print(f"Word '{word}' is in documents: {doc_ids}")

docs_for_bool_search = [
    "word1 & word2 | !word3",
    "word1 | !word2 | !word3"
]
