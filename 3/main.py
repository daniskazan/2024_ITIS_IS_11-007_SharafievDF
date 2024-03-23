import csv
from collections import defaultdict
from typing import TypeAlias, Dict
import os
import json

# task 2
import re


DocID: TypeAlias = str
DocumentBigStr: TypeAlias = str
DocumentItem: TypeAlias = str


class TaskOneSolution:

    def __init__(self,
                 src_folder: str
                 ):
        self.src_folder = src_folder
    @staticmethod
    def inverted_index(data: Dict[DocID, DocumentBigStr]) -> Dict[DocumentItem, list[DocID]]:
        """
        https://xn----7sbbgprkmspltp4jgh.xn--p1ai/articles/vvedenie-v-poisk/invertirovannyy-indeks/
        Возвращает словарь где ключ - термин из документа,
        а значение - список документов где этот термин встречается
        """
        res = defaultdict(set)
        for doc_id, doc in data.items():
            doc_items: list[str] = doc.split()
            for doc_item in doc_items:
                res[doc_item].add(doc_id)
        res = {k: list(v) for k, v in res.items()}
        return res

    def read_documents(self):
        """Читает документы из указанной папки и возвращает их содержимое в виде словаря."""
        documents = {}
        for doc_file in os.listdir(self.src_folder):
            file_path = os.path.join(self.src_folder, doc_file)
            with open(file_path, 'r', encoding='utf-8') as file:
                documents[doc_file] = file.read()
        return documents

    @staticmethod
    def save_inverted_index(index: Dict[DocumentItem, list[DocID]]):
        with open("inverted_index.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(index, indent=4))

    @staticmethod
    def read_json_file() -> dict:
        with open("inverted_index.json", "r", encoding="utf-8") as f:
            content = json.load(f)
        return content

    def execute(self):
        docs = self.read_documents()
        inverted_index_res = self.inverted_index(docs)
        self.save_inverted_index(inverted_index_res)
        return inverted_index_res


class BooleanSearch:
    def __init__(self, index):
        self.index = index

    def search(self, query):
        tokens = re.findall(r'\b(?:!?\w+)\b|\&|\|', query)
        print(tokens)
        current_operation = None
        current_result = None

        for token in tokens:
            if token == '&':
                current_operation = 'AND'
            elif token == '|':
                current_operation = 'OR'
            else:
                if token.startswith('!'):
                    token = token[1:]
                    result = set(self.index.keys()) - set(self.index.get(token, []))
                else:
                    result = set(self.index.get(token, []))

                if current_result is None:
                    current_result = result
                elif current_operation == 'AND':
                    current_result = current_result.intersection(result)
                elif current_operation == 'OR':
                    current_result = current_result.union(result)

        return current_result if current_result else set()


def main():
    solution = TaskOneSolution(src_folder='../2/processed_text')
    index = solution.execute()

    query = [
        "софт & программный | обеспечение",
        "софт & !программный | !обеспечение",
        "софт | программный | обеспечение",
        "софт | !программный | !обеспечение",
        "софт & программный & обеспечение"
    ]

    search_engine = BooleanSearch(index)
    res = []
    for q in query:
        result = search_engine.search(q)
        res.append(result)
    with open("results.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerows(res)


if __name__ == "__main__":
    main()
