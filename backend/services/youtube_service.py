"""
YouTube Music Service (заглушка для тестов)

Полная версия использует yt-dlp для поиска и загрузки аудио.
Для тестов возвращает mock данные.
"""

from typing import List, Optional, Dict
from models import Track


class YouTubeMusicService:
    """Сервис для работы с YouTube Music (заглушка для тестов)"""

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self._available = False  # yt-dlp не установлен

    async def search(self, query: str, limit: int = 20) -> List[Track]:
        """Поиск треков на YouTube (заглушка)"""
        # Возврат mock данных для тестов
        tracks = []
        for i in range(limit):
            tracks.append(Track(
                title=f"{query} (YouTube Track {i+1})",
                artist="YouTube Artist",
                duration=180 + (i * 10) % 120,
                stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                cover=f"https://picsum.photos/seed/yt{i}/300/300",
                source="youtube",
                is_explicit=(i % 5 == 0)
            ))
        return tracks

    async def get_track_stream(self, track_id: str) -> Optional[str]:
        """Получение URL потока (заглушка)"""
        return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

    async def get_original_track(self, query: str) -> Optional[Track]:
        """Поиск оригинальной версии (заглушка)"""
        tracks = await self.search(f"{query} original", limit=3)
        return tracks[0] if tracks else None

    async def get_track_by_query(self, query: str, artist: str = "") -> Optional[Track]:
        """Точный поиск трека (заглушка)"""
        tracks = await self.search(f"{artist} {query}", limit=5)
        return tracks[0] if tracks else None
