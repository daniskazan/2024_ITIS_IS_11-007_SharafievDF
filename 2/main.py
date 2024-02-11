import nltk
from pprint import pprint
from nltk.tokenize import word_tokenize
from pymorphy2 import MorphAnalyzer
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

# Загрузка списка стоп-слов
stop_words = set(stopwords.words('russian'))

# Создание экземпляра MorphAnalyzer для лемматизации
morph = MorphAnalyzer()


def preprocess_text(text):
    # Токенизация текста
    tokens = word_tokenize(text.lower(), language='russian')

    # Лемматизация токенов
    lemmatized_tokens = [morph.parse(token)[0].normal_form for token in tokens]

    # Отбрасывание стоп-слов
    filtered_tokens = [token for token in lemmatized_tokens if token not in stop_words]

    return filtered_tokens


if __name__ == "__main__":

    with open("../first/downloaded_pages/page_4.txt", mode="r") as f:
        content = f.read()
        processed_tokens = preprocess_text(content)
        pprint(processed_tokens)
