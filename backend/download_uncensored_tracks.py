#!/usr/bin/env python3
"""
Массовое скачивание uncensored версий треков
Скачивает всё что найдено в базе uncensored_pairs.json
"""

import json
import os
import subprocess
import sys

# Пытаемся импортировать yt_dlp
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    print("❌ yt-dlp не установлен!")
    print("   Установите: pip install yt-dlp")
    sys.exit(1)

# Папка для скачивания
DOWNLOAD_DIR = "downloaded_tracks"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Создаём подпапки по артистам
def get_artist_dir(artist):
    artist_dir = os.path.join(DOWNLOAD_DIR, artist)
    os.makedirs(artist_dir, exist_ok=True)
    return artist_dir


def download_track(title, artist, url, source):
    """Скачивание трека"""
    # Очистка названия для файла
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
    safe_artist = "".join(c for c in artist if c.isalnum() or c in " -_").strip()
    
    filename = f"{safe_artist} - {safe_title}.mp3"
    output_path = os.path.join(get_artist_dir(safe_artist), filename)
    
    # Проверяем есть ли уже файл
    if os.path.exists(output_path):
        print(f"  ⏭️  Уже скачан: {filename}")
        return False
    
    # Настройки yt-dlp
    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'postprocessors': [],  # Без конвертации если нет ffmpeg
    }
    
    try:
        print(f"  ⬇️  Скачивание: {artist} - {title}")
        
        # Для VK нужны дополнительные параметры
        if 'vk.com' in url:
            ydl_opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print(f"  ✅ Скачано: {filename}")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False


def main():
    print("="*70)
    print("🎵 МАССОВОЕ СКАЧИВАНИЕ UNCENSORED ТРЕКОВ")
    print("="*70)
    
    # Загрузка базы
    pairs_file = "uncensored_pairs.json"
    if not os.path.exists(pairs_file):
        print(f"❌ Файл {pairs_file} не найден!")
        return
    
    with open(pairs_file, 'r', encoding='utf-8') as f:
        pairs = json.load(f)
    
    print(f"📊 Найдено треков для скачивания: {len(pairs)}")
    print(f"📁 Папка загрузки: {os.path.abspath(DOWNLOAD_DIR)}")
    print("="*70)
    
    # Скачивание
    downloaded = 0
    failed = 0
    skipped = 0
    
    for hash_key, track in pairs.items():
        title = track.get('uncensored_title', '')
        artist = track.get('artist', '')
        url = track.get('stream_url', '')
        source = track.get('source', '')
        
        # Пропускаем тестовые записи
        if 'test' in artist.lower() or 'test' in title.lower():
            skipped += 1
            continue
        
        # Скачивание
        if download_track(title, artist, url, source):
            downloaded += 1
        else:
            # Проверяем не был ли файл уже скачан
            if os.path.exists(url):
                skipped += 1
            else:
                failed += 1
        
        # Небольшая задержка
        import time
        time.sleep(0.5)
    
    print("\n" + "="*70)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Скачано: {downloaded}")
    print(f"  ❌ Не удалось: {failed}")
    print(f"  ⏭️  Пропущено: {skipped}")
    print("="*70)
    
    # Создаём плейлист для скачанных треков
    create_playlist()


def create_playlist():
    """Создание m3u плейлиста"""
    playlist_file = os.path.join(DOWNLOAD_DIR, "uncensored_playlist.m3u")
    
    with open(playlist_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        
        for root, dirs, files in os.walk(DOWNLOAD_DIR):
            for file in sorted(files):
                if file.endswith('.mp3'):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, DOWNLOAD_DIR)
                    f.write(f"#EXTINF:-1,{file[:-4]}\n")
                    f.write(f"{rel_path}\n")
    
    print(f"\n📝 Плейлист создан: {playlist_file}")


if __name__ == "__main__":
    # Проверка ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except:
        print("⚠️  FFmpeg не найден! Установите для конвертации в MP3:")
        print("   sudo apt install ffmpeg")
        print()
    
    main()
