#!/usr/bin/env python3
"""
Локальный музыкальный сервер с базой данных uncensored треков

Предоставляет:
- REST API для поиска и воспроизведения
- Базу данных скачанных треков
- Интеграцию с базой цензурированных треков
- Subsonic API совместимость

Использование:
    python local_music_server.py --port 8080
"""

import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn


# ==================== Модели ====================

class Track(BaseModel):
    id: Optional[int] = None
    title: str
    artist: str
    artist_id: Optional[int] = None
    album: Optional[str] = None
    duration: int = 0
    path: str
    size: int = 0
    bitrate: int = 320
    source: str = "local"
    is_explicit: bool = True
    added_at: str = ""


class Artist(BaseModel):
    id: Optional[int] = None
    name: str
    cover: Optional[str] = None
    track_count: int = 0
    album_count: int = 0


class Album(BaseModel):
    id: Optional[int] = None
    title: str
    artist: str
    year: Optional[int] = None
    cover: Optional[str] = None
    track_count: int = 0


# ==================== База данных ====================

class LocalMusicDatabase:
    """Локальная база данных музыки"""
    
    def __init__(self, db_path: str = "local_music.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    artist_id INTEGER,
                    album TEXT,
                    duration INTEGER DEFAULT 0,
                    path TEXT NOT NULL UNIQUE,
                    size INTEGER DEFAULT 0,
                    bitrate INTEGER DEFAULT 320,
                    source TEXT DEFAULT 'local',
                    is_explicit INTEGER DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    play_count INTEGER DEFAULT 0,
                    last_played TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    cover TEXT,
                    track_count INTEGER DEFAULT 0,
                    album_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS albums (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    year INTEGER,
                    cover TEXT,
                    track_count INTEGER DEFAULT 0
                )
            """)
            
            # Индексы
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_album ON tracks(album)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks(title)")
            
            conn.commit()
    
    def add_track(self, track: dict) -> int:
        """Добавление трека"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Проверяем существование
            cursor.execute("SELECT id FROM tracks WHERE path = ?", (track['path'],))
            if cursor.fetchone():
                return -1  # Уже существует
            
            # Добавляем артиста если нет
            cursor.execute("SELECT id FROM artists WHERE name = ?", (track['artist'],))
            artist_row = cursor.fetchone()
            if artist_row:
                track['artist_id'] = artist_row[0]
            else:
                cursor.execute("INSERT INTO artists (name) VALUES (?)", (track['artist'],))
                track['artist_id'] = cursor.lastrowid
            
            # Добавляем трек
            cursor.execute("""
                INSERT INTO tracks (title, artist, artist_id, album, duration, path, size, bitrate, is_explicit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track['title'],
                track['artist'],
                track.get('artist_id'),
                track.get('album'),
                track.get('duration', 0),
                track['path'],
                track.get('size', 0),
                track.get('bitrate', 320),
                1 if track.get('is_explicit', True) else 0,
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def search(self, query: str, limit: int = 50) -> List[dict]:
        """Поиск треков"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tracks 
                WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?
                ORDER BY title
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_tracks(self, limit: int = 1000, offset: int = 0) -> List[dict]:
        """Получение всех треков"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tracks 
                ORDER BY artist, title
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_artists(self) -> List[dict]:
        """Получение всех артистов"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.*, COUNT(t.id) as track_count
                FROM artists a
                LEFT JOIN tracks t ON a.id = t.artist_id
                GROUP BY a.id
                ORDER BY a.name
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_albums(self) -> List[dict]:
        """Получение всех альбомов"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT album as title, artist, COUNT(*) as track_count
                FROM tracks
                WHERE album IS NOT NULL AND album != ''
                GROUP BY album, artist
                ORDER BY album
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_artist_tracks(self, artist_id: int) -> List[dict]:
        """Треки артиста"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tracks WHERE artist_id = ?
                ORDER BY album, title
            """, (artist_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_random_tracks(self, limit: int = 20) -> List[dict]:
        """Случайные треки"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tracks 
                ORDER BY RANDOM()
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def increment_play_count(self, track_id: int):
        """Увеличение счётчика воспроизведений"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE tracks 
                SET play_count = play_count + 1,
                    last_played = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (track_id,))
            conn.commit()
    
    def get_statistics(self) -> dict:
        """Статистика библиотеки"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM tracks")
            tracks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT artist) FROM tracks")
            artists = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT album) FROM tracks WHERE album != ''")
            albums = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(size) FROM tracks")
            total_size = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(play_count) FROM tracks")
            total_plays = cursor.fetchone()[0] or 0
            
            return {
                'tracks': tracks,
                'artists': artists,
                'albums': albums,
                'total_size': total_size,
                'total_plays': total_plays,
            }
    
    def scan_directory(self, music_dir: str) -> int:
        """Сканирование директории и добавление треков"""
        music_path = Path(music_dir)
        if not music_path.exists():
            return 0
        
        added = 0
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.ogg', '.webm'}
        
        for audio_file in music_path.rglob('*'):
            if audio_file.suffix.lower() not in audio_extensions:
                continue
            
            try:
                # Получаем метаданные
                import mutagen
                audio = mutagen.File(str(audio_file))
                
                if audio is None:
                    continue
                
                # Извлекаем информацию
                track_data = {
                    'title': audio.get('title', audio_file.stem),
                    'artist': audio.get('artist', 'Unknown'),
                    'album': audio.get('album'),
                    'duration': int(audio.info.length) if audio.info else 0,
                    'path': str(audio_file.absolute()),
                    'size': audio_file.stat().st_size,
                    'bitrate': int(audio.info.bitrate / 1000) if audio.info else 320,
                }
                
                # Добавляем в базу
                result = self.add_track(track_data)
                if result > 0:
                    added += 1
                    
            except Exception as e:
                print(f"⚠️  Ошибка обработки {audio_file}: {e}")
        
        return added


# ==================== Сервер ====================

def create_app(music_db: LocalMusicDatabase, music_dir: str):
    """Создание FastAPI приложения"""
    
    app = FastAPI(
        title="Local Uncensored Music Server",
        description="Локальный сервер музыки без цензуры",
        version="1.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Статические файлы
    if os.path.exists(music_dir):
        app.mount("/music", StaticFiles(directory=music_dir), name="music")
    
    # ==================== API Endpoints ====================
    
    @app.get("/")
    async def root():
        return {
            "name": "Local Uncensored Music Server",
            "version": "1.0.0",
            "status": "running",
            "features": [
                "REST API",
                "Uncensored Tracks",
                "Local Library",
                "Subsonic Compatible (soon)"
            ]
        }
    
    @app.get("/api/stats")
    async def get_stats():
        """Статистика библиотеки"""
        stats = music_db.get_statistics()
        size_gb = stats['total_size'] / (1024 ** 3)
        return {
            **stats,
            'total_size_gb': round(size_gb, 2)
        }
    
    @app.get("/api/tracks", response_model=List[Track])
    async def get_tracks(
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
    ):
        """Все треки"""
        return music_db.get_all_tracks(limit=limit, offset=offset)
    
    @app.get("/api/search")
    async def search(
        q: str = Query(..., min_length=1),
        limit: int = Query(50, ge=1, le=500)
    ):
        """Поиск треков"""
        return {
            'tracks': music_db.search(q, limit=limit),
            'query': q
        }
    
    @app.get("/api/artists", response_model=List[Artist])
    async def get_artists():
        """Все артисты"""
        return music_db.get_artists()
    
    @app.get("/api/albums", response_model=List[Album])
    async def get_albums():
        """Все альбомы"""
        return music_db.get_albums()
    
    @app.get("/api/artist/{artist_id}/tracks")
    async def get_artist_tracks(artist_id: int):
        """Треки артиста"""
        return music_db.get_artist_tracks(artist_id)
    
    @app.get("/api/random")
    async def get_random(limit: int = Query(20, ge=1, le=100)):
        """Случайные треки"""
        return music_db.get_random_tracks(limit=limit)
    
    @app.get("/api/track/{track_id}/play")
    async def play_track(track_id: int):
        """Воспроизведение трека (счётчик)"""
        music_db.increment_play_count(track_id)
        return {"status": "ok"}
    
    @app.get("/api/scan")
    async def scan_library(directory: str = Query(...)):
        """Сканирование директории"""
        added = music_db.scan_directory(directory)
        return {
            "added": added,
            "message": f"Добавлено {added} треков"
        }
    
    return app


def main():
    parser = argparse.ArgumentParser(
        description='Локальный музыкальный сервер'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Порт сервера'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Хост сервера'
    )
    parser.add_argument(
        '--music-dir',
        default='music_library',
        help='Директория с музыкой'
    )
    parser.add_argument(
        '--db',
        default='local_music.db',
        help='Файл базы данных'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Сканировать директорию при запуске'
    )
    
    args = parser.parse_args()
    
    # Создание базы данных
    music_db = LocalMusicDatabase(db_path=args.db)
    
    # Сканирование при запуске
    if args.scan or not os.path.exists(args.db):
        print(f"\n🔍 Сканирование {args.music_dir}...")
        added = music_db.scan_directory(args.music_dir)
        print(f"✅ Добавлено {added} треков\n")
    
    # Создание приложения
    app = create_app(music_db, args.music_dir)
    
    # Запуск
    print(f"\n{'='*60}")
    print("🎵 LOCAL UNCENSORED MUSIC SERVER")
    print(f"{'='*60}")
    print(f"📁 Музыка: {os.path.abspath(args.music_dir)}")
    print(f"💾 База: {args.db}")
    print(f"🌐 URL: http://{args.host}:{args.port}")
    print(f"📡 API: http://{args.host}:{args.port}/api/tracks")
    print(f"📊 Stats: http://{args.host}:{args.port}/api/stats")
    print(f"{'='*60}\n")
    
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    # Проверка mutagen
    try:
        import mutagen
    except ImportError:
        print("⚠️  mutagen не установлен!")
        print("   Установите: pip install mutagen")
        print("   (без него метаданные не будут читаться)\n")
    
    main()
