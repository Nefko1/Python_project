import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

class FileManager:
    @staticmethod
    def create_directory(directory):
        """Создаёт директорию, если её нет."""
        if not os.path.exists(directory):
            os.makedirs(directory)

class BaseDownloader:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        FileManager.create_directory(self.output_dir)

    def download(self, url):
        """Базовый метод для скачивания, должен быть реализован в наследниках."""
        raise NotImplementedError("Этот метод должен быть реализован в подклассе.")

class ImageDownloader(BaseDownloader):
    def download(self, image_url):
        """Скачивает изображение и сохраняет его в указанную папку."""
        try:
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            filename = os.path.join(self.output_dir, os.path.basename(image_url.split('?')[0]))
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Скачано: {image_url}")
        except Exception as e:
            print(f"Ошибка при скачивании {image_url}: {e}")

class BaseScraper:
    def __init__(self, url):
        self.url = url
        self.data = []

    def parse(self):
        """Базовый метод для парсинга, должен быть реализован в наследниках."""
        raise NotImplementedError("Этот метод должен быть реализован в подклассе.")

class ImageScraper(BaseScraper):
    OUTPUT_DIR = "images"

    def __init__(self, url):
        super().__init__(url)
        self.downloader = ImageDownloader(self.OUTPUT_DIR)

    def parse(self):
        """Парсит изображения с веб-страницы."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for img in soup.find_all("img"):
                img_url = img.get("src")
                if img_url:
                    full_url = urljoin(self.url, img_url)
                    self.data.append(full_url)
        except Exception as e:
            print(f"Ошибка при парсинге {self.url}: {e}")

    def download_images(self):
        """Скачивает все найденные изображения."""
        if not self.data:
            print("Не найдено изображений для скачивания.")
            return

        print(f"Найдено {len(self.data)} изображений. Начинаем скачивание...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            for image_url in self.data:
                executor.submit(self.downloader.download, image_url)

class ImageScraperApp:
    @staticmethod
    def run():
        """Запускает приложение для парсинга и скачивания изображений."""
        url = input("Введите URL для парсинга изображений: ")
        if not url.startswith("http"):
            print("Ошибка: введите корректный URL.")
            return

        scraper = ImageScraper(url)
        print(f"Парсинг изображений с {url}...")
        scraper.parse()
        scraper.download_images()

if __name__ == "__main__":
    ImageScraperApp.run()
