import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

# Папка (Мамка) для изображений
OUTPUT_DIR = "images"

# Делаем папку (мамку), если ее нет
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def download_image(image_url, output_dir):
    """Скачивает изображение по URL и сохраняет его в указанную папку."""
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
        filename = os.path.join(output_dir, os.path.basename(image_url))
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Скачано: {image_url}")
    except Exception as e:
        print(f"Ошибка при скачивании {image_url}: {e}")

def parse_images_from_page(url):
    """Парсит изображения с указанной страницы и возвращает список URL-адресов."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if img_url:
                # Преобразуем относительный URL в абсолютный
                full_url = urljoin(url, img_url)
                images.append(full_url)
        return images
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return []

def main():
    # URL для парсинга
    start_url = input("Введите URL для парсинга изображений: ")

    # Парсим изображения с начальной страницы
    print(f"Парсинг изображений с {start_url}...")
    image_urls = parse_images_from_page(start_url)

    if not image_urls:
        print("Не удалось найти изображения.")
        return

    # Скачиваем изображения с использованием многопоточности
    print(f"Найдено {len(image_urls)} изображений. Начинаем скачивание...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for image_url in image_urls:
            executor.submit(download_image, image_url, OUTPUT_DIR)

if __name__ == "__main__":
    main()
