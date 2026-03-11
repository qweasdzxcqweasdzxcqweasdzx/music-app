#!/usr/bin/env python3
"""
Скачивание треков с VK Music используя cookies
"""

import json
import os
import subprocess
import sys

# Проверка cookies
COOKIES_FILE = "cookies.txt"
if not os.path.exists(COOKIES_FILE):
    print(f"❌ Файл {COOKIES_FILE} не найден!")
    print("   Положи cookies.txt в папку backend/")
    sys.exit(1)

# Папка для скачивания
DOWNLOAD_DIR = "downloaded_tracks"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Треки для скачивания (приоритетные)
priority_tracks = [
    # OG Buda
    {"artist": "OG Buda", "title": "ОПГ сити"},
    {"artist": "OG Buda", "title": "Даёт 2"},
    {"artist": "OG Buda", "title": "Групи"},
    {"artist": "OG Buda", "title": "Выстрелы"},
    {"artist": "OG Buda", "title": "Грусть"},
    {"artist": "OG Buda", "title": "Добро Пожаловать"},
    {"artist": "OG Buda", "title": "Грязный"},
    
    # Big Baby Tape
    {"artist": "Big Baby Tape", "title": "Bandana"},
    {"artist": "Big Baby Tape", "title": "KOOP"},
    {"artist": "Big Baby Tape", "title": "So Icy Nihao"},
    
    # Pharaoh
    {"artist": "Pharaoh", "title": "Phuneral"},
    {"artist": "Pharaoh", "title": "Правило"},
    
    # Агата Кристи
    {"artist": "Агата Кристи", "title": "Опиум для никого"},
    {"artist": "Агата Кристи", "title": "Декаданс"},
    {"artist": "Агата Кристи", "title": "Ураган"},
    
    # Платина
    {"artist": "Платина", "title": "Завидуют"},
    {"artist": "Платина", "title": "Актриса"},
    
    # Soda Luv
    {"artist": "Soda Luv", "title": "Голодный пес"},
    {"artist": "Soda Luv", "title": "G-SHOKK"},
    
    # Lil Krystalll
    {"artist": "Lil Krystalll", "title": "2 бара"},
    {"artist": "Lil Krystalll", "title": "Тик-так"},
]


def search_vk_track(artist, title):
    """Поиск трека в VK через yt-dlp"""
    query = f"{artist} {title}"
    
    cmd = [
        'yt-dlp',
        '--cookies', COOKIES_FILE,
        '--flat-playlist',
        '--dump-json',
        f'vk:search:{query}',
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        if data.get('_type') == 'url':
                            return {
                                'url': data.get('url', ''),
                                'title': data.get('title', ''),
                                'artist': data.get('uploader', '')
                            }
                    except:
                        continue
    except Exception as e:
        print(f"  Ошибка поиска: {e}")
    
    return None


def download_track(url, artist, title):
    """Скачивание трека"""
    # Очистка названия
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:50]
    safe_artist = "".join(c for c in artist if c.isalnum() or c in " -_").strip()[:50]
    
    artist_dir = os.path.join(DOWNLOAD_DIR, safe_artist)
    os.makedirs(artist_dir, exist_ok=True)
    
    output_template = os.path.join(artist_dir, f"{safe_artist} - {safe_title}.%(ext)s")
    
    cmd = [
        'yt-dlp',
        '--cookies', COOKIES_FILE,
        '-x',  # Extract audio
        '--audio-format', 'mp3',
        '--audio-quality', '320K',
        '-o', output_template,
        '--no-playlist',
        '--quiet',
        '--no-warnings',
        url
    ]
    
    try:
        print(f"  ⬇️  Скачивание: {artist} - {title}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # Проверяем что файл скачался
            for f in os.listdir(artist_dir):
                if f.startswith(f"{safe_artist} - {safe_title}") and f.endswith('.mp3'):
                    print(f"  ✅ Скачано: {f}")
                    return True
        
        print(f"  ❌ Ошибка при скачивании")
        return False
        
    except subprocess.TimeoutExpired:
        print(f"  ❌ Таймаут")
        return False
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False


def main():
    print("="*70)
    print("🎵 СКАЧИВАНИЕ ТРЕКОВ С VK MUSIC")
    print("="*70)
    print(f"📁 Папка загрузки: {os.path.abspath(DOWNLOAD_DIR)}")
    print(f"🍪 Cookies: {os.path.abspath(COOKIES_FILE)}")
    print("="*70)
    
    downloaded = 0
    failed = 0
    
    for i, track in enumerate(priority_tracks, 1):
        print(f"\n[{i}/{len(priority_tracks)}] {track['artist']} - {track['title']}")
        
        # Поиск трека в VK
        search_result = search_vk_track(track['artist'], track['title'])
        
        if not search_result:
            print(f"  ❌ Не найдено в VK")
            failed += 1
            continue
        
        print(f"  🔍 Найдено: {search_result['title']}")
        
        # Скачивание
        if download_track(
            search_result['url'],
            track['artist'],
            track['title']
        ):
            downloaded += 1
        else:
            failed += 1
        
        # Задержка между скачиваниями
        import time
        time.sleep(2)
    
    print("\n" + "="*70)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Скачано: {downloaded}/{len(priority_tracks)}")
    print(f"  ❌ Не удалось: {failed}")
    print("="*70)
    
    if downloaded > 0:
        print(f"\n📁 Файлы в: {os.path.abspath(DOWNLOAD_DIR)}")
        print("\n💡 Для интеграции с приложением:")
        print("   1. Перемести файлы в backend/static/tracks/")
        print("   2. Обнови базу с новыми путями")
        print("   3. Перезапусти backend")


if __name__ == "__main__":
    # Проверка yt-dlp
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
    except:
        print("❌ yt-dlp не найден!")
        print("   Установите: pip install yt-dlp")
        sys.exit(1)
    
    main()
