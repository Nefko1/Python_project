import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

"""Папка для изображений"""
OUTPUT_DIR = "images"

"""Делаем папку, если ее нет"""
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def download_image(image_url, output_dir):
    """Скачиваем изображения и сохраняем его в созданную папку"""
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
    """Парсим изображения с указанной страницы и возвращаем в консоль список ссылок"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if img_url:
                """Преобразуем относительную ссылку в абсолютную"""
                full_url = urljoin(url, img_url)
                images.append(full_url)
        return images
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return []

def main():
    """Ввод ссылки для парсинга"""
    start_url = input("Введите URL для парсинга изображений: ")

    """Парсинг с исходной страницы"""
    print(f"Парсинг изображений с {start_url}...")
    image_urls = parse_images_from_page(start_url)

    if not image_urls:
        print("Не удалось найти изображения.")
        return

    """Постарался сделать многопоток, вроде работает))"""
    print(f"Найдено {len(image_urls)} изображений. Начинаем скачивание...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for image_url in image_urls:
            executor.submit(download_image, image_url, OUTPUT_DIR)

if __name__ == "__main__":
    main()
