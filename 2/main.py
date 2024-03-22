import os

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

stop_words = set(stopwords.words('russian'))
morph = MorphAnalyzer()


def process_text(text):
    # Токенизация
    tokens = word_tokenize(text, language="russian")
    # Лемматизация и удаление стоп-слов
    lemmatized_tokens = [morph.parse(word)[0].normal_form for word in tokens if
                         word not in stop_words and word.isalpha()]
    return ' '.join(lemmatized_tokens)


def process_files(input_folder: str, output_folder: str):

    for root, dirs, files in os.walk(input_folder):
        rel_path = os.path.relpath(root, input_folder)
        output_dir = os.path.join(output_folder, rel_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in files:
            if filename == "index.txt":
                continue

            file_path = os.path.join(root, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    text = file.read()
                except UnicodeDecodeError:
                    continue
                processed_text = process_text(text)

            # Сохранение обработанного файла
            output_file_path = os.path.join(output_dir, filename)
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(f"{processed_text}\n")


if __name__ == '__main__':
    # Определение путей к папкам
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)

    src_data_folder = os.path.join(parent_dir, '1/downloaded_pages/')
    output_folder = os.path.join(current_dir, 'processed_text/')
    process_files(src_data_folder, output_folder)
