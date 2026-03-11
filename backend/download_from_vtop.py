#!/usr/bin/env python3
"""
Скачивание треков с vtop.mp3wr.com
"""

import requests
import os
import re
from bs4 import BeautifulSoup

# Папка для скачивания
DOWNLOAD_DIR = "static/tracks"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Список треков для скачивания
tracks_to_download = [
    {"artist": "OG Buda", "title": "ОПГ сити"},
    {"artist": "OG Buda", "title": "Даёт 2"},
    {"artist": "OG Buda", "title": "Групи"},
    {"artist": "OG Buda", "title": "Выстрелы"},
    {"artist": "OG Buda", "title": "Грусть"},
    {"artist": "OG Buda", "title": "Добро Пожаловать"},
    {"artist": "OG Buda", "title": "Грязный"},
    {"artist": "Big Baby Tape", "title": "Bandana I"},
    {"artist": "Big Baby Tape", "title": "KOOP"},
    {"artist": "Big Baby Tape", "title": "So Icy Nihao"},
    {"artist": "Pharaoh", "title": "Phuneral"},
    {"artist": "Pharaoh", "title": "Правило"},
    {"artist": "Агата Кристи", "title": "Опиум для никого"},
    {"artist": "Агата Кристи", "title": "Декаданс"},
    {"artist": "Агата Кристи", "title": "Ураган"},
    {"artist": "Платина", "title": "Завидуют"},
    {"artist": "Платина", "title": "Актриса"},
    {"artist": "Soda Luv", "title": "Голодный пес"},
    {"artist": "Soda Luv", "title": "G-SHOKK"},
    {"artist": "Lil Krystalll", "title": "2 бара"},
    {"artist": "Lil Krystalll", "title": "Тик-так"},
]


def search_track(artist, title):
    """Поиск трека на сайте"""
    query = f"{artist} {title}"
    url = "https://vtop.mp3wr.com/search"
    
    params = {"q": query}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Поиск ссылок на треки
        tracks = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if '/track/' in href or 'track' in href:
                track_url = f"https://vtop.mp3wr.com{href}"
                track_title = link.get_text(strip=True)
                tracks.append({"title": track_title, "url": track_url})
        
        if tracks:
            return tracks[0]  # Возвращаем первый результат
        
    except Exception as e:
        print(f"  ❌ Ошибка поиска: {e}")
    
    return None


def get_download_url(track_url):
    """Получение прямой ссылки на скачивание"""
    try:
        response = requests.get(track_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Поиск кнопки/ссылки скачивания
        download_link = soup.find('a', href=True, string=re.compile(r'скачать|download|Download', re.IGNORECASE))
        
        if download_link:
            download_url = download_link.get('href')
            if download_url and download_url.startswith('http'):
                return download_url
        
        # Альтернативный поиск
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if '.mp3' in href or 'download' in href.lower():
                return href
        
    except Exception as e:
        print(f"  ❌ Ошибка получения ссылки: {e}")
    
    return None


def download_file(url, filename):
    """Скачивание файла"""
    try:
        print(f"  ⬇️  Скачивание: {filename}")
        
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  ✅ Скачано: {filename}")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка скачивания: {e}")
        return False


def main():
    print("="*70)
    print("🎵 СКАЧИВАНИЕ ТРЕКОВ С vtop.mp3wr.com")
    print("="*70)
    print(f"📁 Папка: {os.path.abspath(DOWNLOAD_DIR)}")
    print("="*70)
    
    downloaded = 0
    failed = 0
    not_found = 0
    
    for i, track in enumerate(tracks_to_download, 1):
        print(f"\n[{i}/{len(tracks_to_download)}] {track['artist']} - {track['title']}")
        
        # Поиск трека
        search_result = search_track(track['artist'], track['title'])
        
        if not search_result:
            print(f"  ❌ Не найдено")
            not_found += 1
            continue
        
        print(f"  🔍 Найдено: {search_result['title']}")
        
        # Получение ссылки на скачивание
        download_url = get_download_url(search_result['url'])
        
        if not download_url:
            print(f"  ❌ Не удалось получить ссылку")
            failed += 1
            continue
        
        print(f"  🔗 Ссылка: {download_url[:60]}...")
        
        # Скачивание
        safe_filename = f"{track['artist']} - {track['title']}.mp3".replace('/', '_')
        if download_file(download_url, safe_filename):
            downloaded += 1
        else:
            failed += 1
        
        # Задержка
        import time
        time.sleep(1)
    
    print("\n" + "="*70)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Скачано: {downloaded}")
    print(f"  ❌ Не удалось: {failed}")
    print(f"  🔍 Не найдено: {not_found}")
    print("="*70)

if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
        import requests
    except ImportError:
        print("❌ Не установлены зависимости!")
        print("   Установите: pip install requests beautifulsoup4")
        exit(1)
    
    main()
