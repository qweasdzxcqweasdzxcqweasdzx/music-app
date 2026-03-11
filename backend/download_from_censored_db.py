#!/usr/bin/env python3
"""
Скачивание оригинальных (uncensored) версий для треков из базы цензурированных треков

Использование:
    python download_from_censored_db.py
    
Или с параметрами:
    python download_from_censored_db.py --status pending --limit 10
    python download_from_censored_db.py --method telegram
    python download_from_censored_db.py --method ytdlp
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path

# Добавляем backend в path
sys.path.insert(0, str(Path(__file__).parent))

from services.censored_tracks_service import censored_tracks_db
from models.censored_tracks import CensorshipType


class CensoredTracksDownloader:
    """
    Загрузчик оригинальных версий для цензурированных треков
    """
    
    def __init__(self, download_dir: str = "downloaded_uncensored", method: str = "ytdlp"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.method = method  # 'ytdlp' или 'telegram'
        self.downloaded = 0
        self.failed = 0
        self.skipped = 0
        
    def search_uncensored_version(self, title: str, artist: str) -> dict:
        """
        Поиск uncensored версии через API
        
        Returns:
            dict с информацией о найденном треке или None
        """
        import urllib.request
        import json as json_lib
        
        query = f"{title} {artist} explicit original uncensored"
        encoded_query = urllib.request.quote(query)
        
        try:
            # Поиск через локальное API
            url = f"http://localhost:8000/api/censorship/search-uncensored?q={encoded_query}&limit=5"
            
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json_lib.loads(response.read().decode())
                
                if data.get('tracks'):
                    # Возвращаем первый результат
                    return data['tracks'][0]
                    
        except Exception as e:
            print(f"  ⚠️  Ошибка поиска: {e}")
            
        return None
    
    def download_with_ytdlp(self, track: dict) -> bool:
        """
        Скачивание через yt-dlp
        """
        try:
            import yt_dlp
            
            title = track.get('title', 'Unknown')
            artist = track.get('artist', 'Unknown')
            url = track.get('stream_url', '')
            
            if not url:
                print(f"  ❌ Нет URL для скачивания")
                return False
            
            # Очистка названия для файла
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            safe_artist = "".join(c for c in artist if c.isalnum() or c in " -_").strip()
            
            output_template = str(self.download_dir / f"{safe_artist}" / f"{safe_artist} - {safe_title}.%(ext)s")
            
            # Настройки yt-dlp
            ydl_opts = {
                'format': 'bestaudio[ext=mp3]/bestaudio/best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'postprocessors': [],
            }
            
            # Проверка на наличие ffmpeg
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
            
            print(f"  ⬇️  Скачивание: {artist} - {title}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            print(f"  ✅ Скачано: {safe_artist} - {safe_title}")
            return True
            
        except ImportError:
            print(f"  ❌ yt-dlp не установлен: pip install yt-dlp")
            return False
        except Exception as e:
            print(f"  ❌ Ошибка скачивания: {e}")
            return False
    
    async def download_with_telegram(self, track: dict) -> bool:
        """
        Скачивание через Telegram ботов
        """
        try:
            from telethon import TelegramClient
            from telethon.tl.types import DocumentAttributeAudio
            
            # Конфигурация
            API_ID = 29125653
            API_HASH = "45f6766d50913319e0a7e5752a28ceb7"
            
            title = track.get('title', 'Unknown')
            artist = track.get('artist', 'Unknown')
            query = f"{artist} {title} explicit"
            
            # Боты для скачивания
            BOTS = ["vk_music_bot", "SaveMusicBot", "GoMusicBot"]
            
            print(f"  🔍 Поиск в Telegram: {artist} - {title}")
            
            # Запрос номера телефона если не настроен
            phone = input("  📱 Введи номер Telegram (+7...): ").strip()
            
            async with TelegramClient('music_downloader', API_ID, API_HASH) as client:
                await client.start(phone=phone)
                print(f"  ✅ Авторизован в Telegram")
                
                for bot in BOTS:
                    try:
                        # Отправка запроса
                        await client.send_message(bot, query)
                        await asyncio.sleep(2)
                        
                        # Получение сообщений
                        messages = await client.get_messages(bot, limit=5)
                        
                        for msg in messages:
                            if msg.file and msg.file.mime_type.startswith('audio/'):
                                # Скачивание
                                safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
                                safe_artist = "".join(c for c in artist if c.isalnum() or c in " -_").strip()
                                
                                filename = f"{safe_artist} - {safe_title}.mp3"
                                filepath = self.download_dir / safe_artist / filename
                                filepath.parent.mkdir(exist_ok=True)
                                
                                await msg.download_media(str(filepath))
                                print(f"  ✅ Скачано: {filename}")
                                return True
                        
                    except Exception as e:
                        print(f"  ⚠️  {bot}: {e}")
                        continue
                        
            print(f"  ❌ Не найдено в Telegram")
            return False
            
        except ImportError:
            print(f"  ❌ Telethon не установлен: pip install telethon")
            return False
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False
    
    def process_track(self, track: dict) -> bool:
        """
        Обработка одного трека
        """
        track_id = track['id']
        title = track['title']
        artist = track['artist']
        censorship_type = track.get('censorship_type', 'unknown')
        
        print(f"\n{'='*60}")
        print(f"🎵 Трек: {artist} - {title}")
        print(f"   Тип цензуры: {censorship_type}")
        print(f"   Статус: {track.get('status', 'pending')}")
        print(f"{'='*60}")
        
        # Проверка есть ли уже замена
        if track.get('replacement_found'):
            print(f"  ⏭️  Замена уже найдена")
            replacement_url = track.get('replacement_url', '')
            if replacement_url:
                print(f"  URL: {replacement_url}")
                
                # Спросить скачать ли
                answer = input("  ⬇️  Скачать замену? (y/n): ").strip().lower()
                if answer == 'y':
                    # Скачивание замены
                    if self.method == 'ytdlp':
                        success = self.download_with_ytdlp({
                            'title': title + ' (uncensored)',
                            'artist': artist,
                            'stream_url': replacement_url,
                        })
                    else:
                        success = asyncio.run(self.download_with_telegram({
                            'title': title + ' (uncensored)',
                            'artist': artist,
                        }))
                    
                    if success:
                        self.downloaded += 1
                        # Обновить статус
                        censored_tracks_db.update_track(track_id, type('obj', (object,), {'status': 'replaced'})())
                    else:
                        self.failed += 1
                else:
                    self.skipped += 1
            return True
        
        # Поиск uncensored версии
        print(f"  🔍 Поиск uncensored версии...")
        found_track = self.search_uncensored_version(title, artist)
        
        if not found_track:
            print(f"  ❌ Не найдено uncensored версии")
            self.failed += 1
            return False
        
        print(f"  ✅ Найдено: {found_track.get('artist')} - {found_track.get('title')}")
        print(f"  Платформа: {found_track.get('source', 'unknown')}")
        
        # Добавление замены в базу
        answer = input("  ➕ Добавить замену в базу? (y/n): ").strip().lower()
        if answer == 'y':
            try:
                import urllib.request
                import json as json_lib
                
                data = json.dumps({
                    'replacement_track_id': found_track.get('id', ''),
                    'replacement_url': found_track.get('stream_url', ''),
                    'replacement_platform': found_track.get('source', ''),
                }).encode('utf-8')
                
                req = urllib.request.Request(
                    f"http://localhost:8000/api/censored-tracks/{track_id}/replacement",
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    print(f"  ✅ Замена добавлена в базу")
                    
            except Exception as e:
                print(f"  ⚠️  Ошибка добавления в базу: {e}")
        
        # Скачивание
        answer = input("  ⬇️  Скачать uncensored версию? (y/n): ").strip().lower()
        if answer != 'y':
            self.skipped += 1
            return True
        
        if self.method == 'ytdlp':
            success = self.download_with_ytdlp(found_track)
        else:
            success = asyncio.run(self.download_with_telegram(found_track))
        
        if success:
            self.downloaded += 1
        else:
            self.failed += 1
        
        return True
    
    def run(self, status: str = 'pending', limit: int = 50):
        """
        Запуск скачивания
        
        Args:
            status: Статус треков для обработки (pending, verified, all)
            limit: Максимальное количество треков
        """
        print("="*70)
        print("🎵 СКАЧИВАНИЕ UNCENSORED ВЕРСИЙ")
        print("="*70)
        print(f"📁 Папка загрузки: {self.download_dir.absolute()}")
        print(f"🔧 Метод: {self.method}")
        print(f"📊 Статус: {status}")
        print(f"📊 Лимит: {limit}")
        print("="*70)
        
        # Получение треков из базы
        if status == 'all':
            tracks = censored_tracks_db.export_to_json()
        else:
            from models.censored_tracks import CensoredTrackSearch
            search = CensoredTrackSearch(status=status if status != 'all' else None, limit=limit)
            tracks = censored_tracks_db.search(search)
        
        if not tracks:
            print("\n⚠️  Треки не найдены")
            return
        
        print(f"\n📊 Найдено треков: {len(tracks)}")
        
        # Обработка каждого трека
        for i, track in enumerate(tracks[:limit], 1):
            print(f"\n[{i}/{len(tracks[:limit])}]")
            self.process_track(track)
        
        # Итоги
        print("\n" + "="*70)
        print("📊 РЕЗУЛЬТАТЫ:")
        print(f"  ✅ Скачано: {self.downloaded}")
        print(f"  ❌ Не удалось: {self.failed}")
        print(f"  ⏭️  Пропущено: {self.skipped}")
        print("="*70)
        
        # Создание плейлиста
        self.create_playlist()


def create_playlist(self):
    """Создание M3U плейлиста"""
    playlist_file = self.download_dir / "uncensored_playlist.m3u"
    
    with open(playlist_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        
        for root, dirs, files in os.walk(self.download_dir):
            for file in sorted(files):
                if file.endswith('.mp3'):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, self.download_dir)
                    title = file[:-4]  # Без .mp3
                    f.write(f"#EXTINF:-1,{title}\n")
                    f.write(f"{rel_path}\n")
    
    print(f"\n📝 Плейлист создан: {playlist_file}")


# Добавляем метод в класс
CensoredTracksDownloader.create_playlist = create_playlist


def main():
    parser = argparse.ArgumentParser(
        description='Скачивание uncensored версий для треков из базы'
    )
    parser.add_argument(
        '--status',
        default='pending',
        choices=['pending', 'verified', 'all'],
        help='Статус треков для обработки'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Максимальное количество треков'
    )
    parser.add_argument(
        '--method',
        default='ytdlp',
        choices=['ytdlp', 'telegram'],
        help='Метод скачивания'
    )
    parser.add_argument(
        '--output',
        default='downloaded_uncensored',
        help='Папка для скачанных треков'
    )
    
    args = parser.parse_args()
    
    downloader = CensoredTracksDownloader(
        download_dir=args.output,
        method=args.method
    )
    
    downloader.run(status=args.status, limit=args.limit)


if __name__ == "__main__":
    main()
