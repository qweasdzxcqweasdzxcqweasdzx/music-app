#!/usr/bin/env python3
"""
Скачивание списка треков из telegram_auto_download.py
Использует yt-dlp для скачивания
"""

import yt_dlp
import os

# Список треков из telegram_auto_download.py
TRACKS = [
    "OG Buda ОПГ сити",
    "OG Buda Даёт 2",
    "OG Buda Групи",
    "OG Buda Выстрелы",
    "OG Buda Грусть",
    "OG Buda Добро Пожаловать",
    "OG Buda Грязный",
    "Big Baby Tape Bandana I",
    "Big Baby Tape KOOP",
    "Big Baby Tape So Icy Nihao",
    "Pharaoh Phuneral",
    "Pharaoh Правило",
    "Агата Кристи Опиум для никого",
    "Агата Кристи Декаданс",
    "Агата Кристи Ураган",
    "Платина Завидуют",
    "Платина Актриса",
    "Soda Luv Голодный пес",
    "Soda Luv G-SHOKK",
    "Lil Krystalll 2 бара",
    "Lil Krystalll Тик-так",
]

DOWNLOAD_DIR = "music_library"

def safe_filename(name):
    """Безопасное имя файла"""
    return "".join(c for c in name if c.isalnum() or c in " -_().").strip()[:100]

def download_track(query, artist_name=""):
    """Скачивание одного трека"""
    ydl_opts = {
        'format': 'bestaudio[ext=webm]/bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'default_search': 'ytsearch1',
        'postprocessors': [],
    }
    
    # Пробуем добавить ffmpeg
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]
    except:
        pass
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Поиск
            print(f"  🔍 Поиск: {query}")
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            
            if info and 'entries' in info:
                entry = info['entries'][0]
                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                
                # Создаём папку артиста
                artist_dir = os.path.join(DOWNLOAD_DIR, safe_filename(artist_name) if artist_name else "Various")
                os.makedirs(artist_dir, exist_ok=True)
                
                # Скачивание
                ydl_opts['outtmpl'] = os.path.join(artist_dir, f"{safe_filename(query)}.%(ext)s")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                    ydl_download.download([video_url])
                
                print(f"  ✅ Скачано: {query}")
                return True
            else:
                print(f"  ❌ Не найдено")
                return False
                
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

def main():
    print("="*70)
    print("🎵 СКАЧИВАНИЕ ТРЕКОВ ИЗ СПИСКА")
    print("="*70)
    print(f"📊 Треков: {len(TRACKS)}")
    print(f"📁 Папка: {os.path.abspath(DOWNLOAD_DIR)}")
    print("="*70)
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    downloaded = 0
    failed = 0
    
    for i, track in enumerate(TRACKS, 1):
        print(f"\n[{i}/{len(TRACKS)}] {track}")
        
        # Пытаемся извлечь имя артиста
        parts = track.split(' ', 1)
        artist = parts[0] if len(parts) > 1 else ""
        
        if download_track(track, artist):
            downloaded += 1
        else:
            failed += 1
        
        # Задержка
        import time
        time.sleep(2)
    
    print("\n" + "="*70)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"  ✅ Скачано: {downloaded}/{len(TRACKS)}")
    print(f"  ❌ Не удалось: {failed}")
    print("="*70)

if __name__ == "__main__":
    main()
