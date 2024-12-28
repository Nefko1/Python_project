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

class ImageDownloader:
    @staticmethod
    def download_image(image_url, output_dir):
        """Скачивает изображение и сохраняет его в указанную папку."""
        try:
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            filename = os.path.join(output_dir, os.path.basename(image_url.split('?')[0]))
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Скачано: {image_url}")
        except Exception as e:
            print(f"Ошибка при скачивании {image_url}: {e}")

class ImageScraper:
    OUTPUT_DIR = "images"

    def __init__(self, url):
        """Инициализация парсера с URL."""
        self.url = url
        self.image_urls = []
        FileManager.create_directory(self.OUTPUT_DIR)

    def parse_images(self):
        """Парсит изображения с веб-страницы."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for img in soup.find_all("img"):
                img_url = img.get("src")
                if img_url:
                    full_url = urljoin(self.url, img_url)
                    self.image_urls.append(full_url)
        except Exception as e:
            print(f"Ошибка при парсинге {self.url}: {e}")

    def download_images(self):
        """Скачивает все найденные изображения."""
        if not self.image_urls:
            print("Не найдено изображений для скачивания.")
            return

        print(f"Найдено {len(self.image_urls)} изображений. Начинаем скачивание...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            for image_url in self.image_urls:
                executor.submit(ImageDownloader.download_image, image_url, self.OUTPUT_DIR)

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
        scraper.parse_images()
        scraper.download_images()

if __name__ == "__main__":
    ImageScraperApp.run()
