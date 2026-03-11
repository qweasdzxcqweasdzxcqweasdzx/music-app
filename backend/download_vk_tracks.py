#!/usr/bin/env python3
"""
Скачивание треков с VK Music
Использует прямые ссылки на аудио из VK
"""

import json
import os
import urllib.request
import urllib.error

# Папка для скачивания
DOWNLOAD_DIR = "downloaded_tracks"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_artist_dir(artist):
    artist_dir = os.path.join(DOWNLOAD_DIR, artist)
    os.makedirs(artist_dir, exist_ok=True)
    return artist_dir

def download_from_vk(title, artist, url):
    """Скачивание с VK (если есть прямой URL)"""
    # Очистка названия
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:50]
    safe_artist = "".join(c for c in artist if c.isalnum() or c in " -_").strip()[:50]
    
    filename = f"{safe_artist} - {safe_title}.mp3"
    output_path = os.path.join(get_artist_dir(safe_artist), filename)
    
    if os.path.exists(output_path):
        print(f"  ⏭️  Уже скачан: {filename}")
        return False
    
    # VK Audio URL обычно выглядит так: https://psv4.vk.me/audio/...
    if 'vk.com' not in url and 'vk.me' not in url:
        print(f"  ⚠️  Не VK ссылка: {url}")
        return False
    
    try:
        print(f"  ⬇️  Скачивание: {artist} - {title}")
        
        # Запрос с User-Agent
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://vk.com/'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(output_path, 'wb') as out_file:
                out_file.write(response.read())
        
        print(f"  ✅ Скачано: {filename}")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False


def main():
    print("="*70)
    print("🎵 СКАЧИВАНИЕ ТРЕКОВ С VK MUSIC")
    print("="*70)
    
    # Загрузка базы
    pairs_file = "uncensored_pairs.json"
    if not os.path.exists(pairs_file):
        print(f"❌ Файл {pairs_file} не найден!")
        return
    
    with open(pairs_file, 'r', encoding='utf-8') as f:
        pairs = json.load(f)
    
    print(f"📊 Найдено треков: {len(pairs)}")
    print(f"📁 Папка: {os.path.abspath(DOWNLOAD_DIR)}")
    print("="*70)
    
    downloaded = 0
    failed = 0
    skipped = 0
    not_vk = 0
    
    for hash_key, track in pairs.items():
        title = track.get('uncensored_title', '')
        artist = track.get('artist', '')
        url = track.get('stream_url', '')
        source = track.get('source', '')
        
        # Пропускаем тестовые и не-VK
        if 'test' in artist.lower():
            skipped += 1
            continue
        
        if source != 'vk' and 'vk' not in url.lower():
            not_vk += 1
            print(f"  ⚠️  Пропущено (не VK): {artist} - {title} [{source}]")
            continue
        
        # Скачивание
        if download_from_vk(title, artist, url):
            downloaded += 1
        else:
            failed += 1
    
    print("\n" + "="*70)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Скачано: {downloaded}")
    print(f"  ❌ Не удалось: {failed}")
    print(f"  ⏭️  Пропущено: {skipped}")
    print(f"  ⚠️  Не VK ссылки: {not_vk}")
    print("="*70)
    print("\n⚠️  ПРИМЕЧАНИЕ:")
    print("   Для скачивания нужны ПРЯМЫЕ ссылки на аудио VK")
    print("   Ссылки вида 'https://vk.com/audio...' не работают без API")
    print("   Нужно использовать yt-dlp с авторизацией VK")
    print("="*70)


if __name__ == "__main__":
    main()
