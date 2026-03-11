#!/usr/bin/env python3
"""
Массовое скачивание UNCENSORED версий треков

Использование:
    python download_uncensored_massive.py --input censored_tracks.json --output music_library
    
Или из базы:
    python download_uncensored_massive.py --from-db --status pending --limit 20
"""

import os
import sys
import json
import argparse
import asyncio
import yt_dlp
from pathlib import Path
from datetime import datetime


class UncensoredDownloader:
    """Загрузчик uncensored версий треков"""
    
    def __init__(self, output_dir: str = "music_library", max_retries: int = 3):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_retries = max_retries
        self.stats = {
            'downloaded': 0,
            'failed': 0,
            'skipped': 0,
            'total_size': 0
        }
        
    def get_artist_dir(self, artist: str) -> Path:
        """Создание папки для артиста"""
        safe_artist = self._safe_filename(artist)
        artist_dir = self.output_dir / safe_artist
        artist_dir.mkdir(exist_ok=True)
        return artist_dir
    
    def _safe_filename(self, filename: str) -> str:
        """Безопасное имя файла"""
        safe = "".join(c for c in filename if c.isalnum() or c in " -_().").strip()
        return safe[:100]  # Ограничение длины
    
    def search_youtube(self, query: str) -> str:
        """Поиск YouTube URL по запросу"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch1',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)
                
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry:
                            return f"https://www.youtube.com/watch?v={entry['id']}"
                            
        except Exception as e:
            print(f"  ⚠️  Ошибка поиска: {e}")
            
        return None
    
    def download_track(self, url: str, artist: str, title: str, force_explicit: bool = False) -> bool:
        """
        Скачивание трека
        
        Args:
            url: YouTube URL
            artist: Имя артиста
            title: Название трека
            force_explicit: Искать explicit версию
        """
        for attempt in range(self.max_retries):
            try:
                artist_dir = self.get_artist_dir(artist)
                safe_title = self._safe_filename(title)
                output_template = str(artist_dir / f"{safe_title}.%(ext)s")
                
                # Настройки yt-dlp
                ydl_opts = {
                    'format': 'bestaudio[ext=webm]/bestaudio/best',
                    'outtmpl': output_template,
                    'quiet': True,
                    'no_warnings': True,
                    'noplaylist': True,
                    'postprocessors': [],
                    'retry_sleep': 1,
                    'extractor_retries': 3,
                }
                
                # Проверка ffmpeg
                try:
                    import subprocess
                    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }]
                except:
                    print(f"  ⚠️  FFmpeg не найден, скачиваем как есть")
                
                # Добавляем explicit к запросу если нужно
                if force_explicit:
                    # Поиск explicit версии
                    explicit_query = f"{artist} {title} explicit original uncensored"
                    explicit_url = self.search_youtube(explicit_query)
                    if explicit_url:
                        print(f"  🔍 Найдена explicit версия")
                        url = explicit_url
                
                print(f"  ⬇️  Скачивание: {artist} - {title}")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    # Получаем размер файла
                    if os.path.exists(output_template.replace('.%(ext)s', '.mp3')):
                        file_path = output_template.replace('.%(ext)s', '.mp3')
                        self.stats['total_size'] += os.path.getsize(file_path)
                        self.stats['downloaded'] += 1
                        print(f"  ✅ Скачано: {os.path.basename(file_path)}")
                        return True
                    elif os.path.exists(output_template):
                        file_path = output_template
                        self.stats['total_size'] += os.path.getsize(file_path)
                        self.stats['downloaded'] += 1
                        print(f"  ✅ Скачано: {os.path.basename(file_path)}")
                        return True
                        
                return False
                
            except Exception as e:
                print(f"  ❌ Ошибка (попытка {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    self.stats['failed'] += 1
                    return False
                    
        return False
    
    def download_from_list(self, tracks: list, force_explicit: bool = False) -> dict:
        """
        Скачивание из списка треков
        
        Args:
            tracks: Список треков [{'artist': ..., 'title': ..., 'url': ...}]
            force_explicit: Искать explicit версии
        """
        total = len(tracks)
        print(f"\n{'='*70}")
        print(f"🎵 МАССОВОЕ СКАЧИВАНИЕ UNCENSORED ВЕРСИЙ")
        print(f"{'='*70}")
        print(f"📊 Треков: {total}")
        print(f"📁 Папка: {self.output_dir.absolute()}")
        print(f"🔍 Explicit поиск: {'включен' if force_explicit else 'выключен'}")
        print(f"{'='*70}\n")
        
        for i, track in enumerate(tracks, 1):
            print(f"\n[{i}/{total}]")
            
            artist = track.get('artist', 'Unknown')
            title = track.get('title', 'Unknown')
            url = track.get('url', None)
            
            # Проверка есть ли уже трек
            artist_dir = self.get_artist_dir(artist)
            existing = list(artist_dir.glob(f"{self._safe_filename(title)}.*"))
            if existing:
                print(f"  ⏭️  Уже скачан: {existing[0].name}")
                self.stats['skipped'] += 1
                continue
            
            # Если нет URL - ищем на YouTube
            if not url:
                query = f"{artist} {title} explicit original"
                url = self.search_youtube(query)
                if not url:
                    print(f"  ❌ Не найдено в YouTube")
                    self.stats['failed'] += 1
                    continue
            
            # Скачивание
            self.download_track(url, artist, title, force_explicit=force_explicit)
            
            # Небольшая задержка
            import time
            time.sleep(1)
        
        # Итоги
        self.print_stats()
        self.create_playlist()
        
        return self.stats
    
    def download_from_db(self, status: str = 'pending', limit: int = 50, force_explicit: bool = True) -> dict:
        """
        Скачивание из базы цензурированных треков
        
        Args:
            status: Статус треков
            limit: Лимит треков
            force_explicit: Искать explicit версии
        """
        sys.path.insert(0, str(Path(__file__).parent))
        from services.censored_tracks_service import censored_tracks_db
        from models.censored_tracks import CensoredTrackSearch
        
        # Получение треков из базы
        search = CensoredTrackSearch(status=status if status != 'all' else None, limit=limit)
        tracks = censored_tracks_db.search(search)
        
        if not tracks:
            print("⚠️  Треки не найдены")
            return self.stats
        
        print(f"\n📊 Найдено треков в базе: {len(tracks)}")
        
        # Преобразование в формат для скачивания
        download_list = []
        for track in tracks[:limit]:
            # Если есть замена - используем её
            if track.get('replacement_found') and track.get('replacement_url'):
                download_list.append({
                    'artist': track['artist'],
                    'title': track['title'] + ' (uncensored)',
                    'url': track['replacement_url'],
                    'db_id': track['id'],
                })
            else:
                # Ищем uncensored версию
                download_list.append({
                    'artist': track['artist'],
                    'title': track['title'],
                    'url': None,  # Будет найдено автоматически
                    'db_id': track['id'],
                    'censorship_type': track.get('censorship_type'),
                })
        
        return self.download_from_list(download_list, force_explicit=force_explicit)
    
    def print_stats(self):
        """Вывод статистики"""
        size_gb = self.stats['total_size'] / (1024 ** 3)
        size_mb = self.stats['total_size'] / (1024 ** 2)
        
        print(f"\n{'='*70}")
        print("📊 РЕЗУЛЬТАТЫ:")
        print(f"  ✅ Скачано: {self.stats['downloaded']}")
        print(f"  ❌ Не удалось: {self.stats['failed']}")
        print(f"  ⏭️  Пропущено: {self.stats['skipped']}")
        print(f"  💾 Размер: {size_mb:.1f} MB ({size_gb:.2f} GB)")
        print(f"{'='*70}")
    
    def create_playlist(self):
        """Создание M3U плейлиста"""
        playlist_file = self.output_dir / "uncensored_playlist.m3u"
        
        with open(playlist_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n\n")
            
            for artist_dir in sorted(self.output_dir.iterdir()):
                if artist_dir.is_dir():
                    artist_name = artist_dir.name
                    for track_file in sorted(artist_dir.glob("*.mp3")):
                        title = track_file.stem
                        rel_path = track_file.relative_to(self.output_dir)
                        f.write(f"#EXTINF:-1,{artist_name} - {title}\n")
                        f.write(f"{rel_path}\n\n")
        
        print(f"\n📝 Плейлист создан: {playlist_file}")
    
    def export_library_json(self):
        """Экспорт библиотеки в JSON"""
        library_file = self.output_dir / "library.json"
        library = []
        
        for artist_dir in sorted(self.output_dir.iterdir()):
            if artist_dir.is_dir():
                artist_name = artist_dir.name
                for track_file in sorted(artist_dir.glob("*.mp3")):
                    library.append({
                        'artist': artist_name,
                        'title': track_file.stem,
                        'path': str(track_file.relative_to(self.output_dir)),
                        'size': track_file.stat().st_size,
                    })
        
        with open(library_file, 'w', encoding='utf-8') as f:
            json.dump(library, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Библиотека экспортирована: {library_file}")
        return library


def main():
    parser = argparse.ArgumentParser(
        description='Массовое скачивание uncensored версий треков'
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--input',
        type=str,
        help='JSON файл со списком треков'
    )
    group.add_argument(
        '--from-db',
        action='store_true',
        help='Скачать из базы цензурированных треков'
    )
    
    parser.add_argument(
        '--output',
        default='music_library',
        help='Папка для скачанных треков'
    )
    parser.add_argument(
        '--status',
        default='pending',
        choices=['pending', 'verified', 'replaced', 'all'],
        help='Статус треков (для --from-db)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Лимит треков'
    )
    parser.add_argument(
        '--explicit',
        action='store_true',
        help='Искать explicit версии'
    )
    parser.add_argument(
        '--retry',
        type=int,
        default=3,
        help='Количество попыток'
    )
    
    args = parser.parse_args()
    
    downloader = UncensoredDownloader(
        output_dir=args.output,
        max_retries=args.retry
    )
    
    if args.from_db:
        downloader.download_from_db(
            status=args.status,
            limit=args.limit,
            force_explicit=args.explicit
        )
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            tracks = json.load(f)
        downloader.download_from_list(tracks, force_explicit=args.explicit)
    else:
        print("❌ Укажите --input или --from-db")
        parser.print_help()
        sys.exit(1)
    
    # Экспорт библиотеки
    downloader.export_library_json()


if __name__ == "__main__":
    # Проверка зависимостей
    try:
        import yt_dlp
    except ImportError:
        print("❌ yt-dlp не установлен!")
        print("   Установите: pip install yt-dlp")
        sys.exit(1)
    
    main()
