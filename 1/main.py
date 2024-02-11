import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger


class PageDownloader:
    @staticmethod
    def download(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
        except requests.exceptions.RequestException:
            logger.info(f"Failed to fetch {url}")
            return None
        return None


class TextExtractor:
    @staticmethod
    def extract(html):
        soup = BeautifulSoup(html, 'html.parser')
        text = ' '.join(soup.stripped_strings)
        return text


class TextSaver:
    @staticmethod
    def save(text, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)


class WebCrawler:
    def __init__(self, *,  urls, target_dir, max_pages=100, min_words=1000):
        self.urls = urls
        self.target_dir = target_dir
        self.max_pages = max_pages
        self.min_words = min_words
        self.__crawled_pages = set()

    def crawl(self):
        index_file = open('index.txt', 'w', encoding='utf-8')
        pages_to_crawl = self.urls.copy()

        while len(self.__crawled_pages) < self.max_pages and pages_to_crawl:
            url = pages_to_crawl.pop(0)
            html = PageDownloader.download(url)
            if any(
                    [
                        url in self.__crawled_pages,
                        not html
                     ]
            ):
                continue

            text = TextExtractor.extract(html)
            if not self.is_sufficient_text(text):
                continue

            self.save_page(url, text, index_file)
            self.add_links_to_crawl(url, html, pages_to_crawl)

        index_file.close()

    def is_sufficient_text(self, text):
        return len(text.split()) >= self.min_words

    def save_page(self, url, text, index_file):
        filename = f"page_{len(self.__crawled_pages) + 1}.txt"
        TextSaver.save(text, os.path.join(self.target_dir, filename))
        index_file.write(f"{len(self.__crawled_pages) + 1}: {url}\n")
        self.__crawled_pages.add(url)

    def add_links_to_crawl(self, url, html, pages_to_crawl):
        soup = BeautifulSoup(html, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a') if link.get('href')]
        for link in links:
            absolute_link = urljoin(url, link)
            if absolute_link not in self.__crawled_pages:
                pages_to_crawl.append(absolute_link)


if __name__ == "__main__":
    target_directory = "./downloaded_pages"
    os.makedirs(target_directory, exist_ok=True)
    crawler = WebCrawler(
        urls=["https://dev-ed.ru/blog/101-python3-qa/#32", "https://habr.com/ru/feed"],
        target_dir=target_directory
    )
    crawler.crawl()
