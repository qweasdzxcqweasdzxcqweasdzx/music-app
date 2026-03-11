"""
SoundCloud API Service - Обновлённая версия

Использует неофициальный API для работы без OAuth
"""

import aiohttp
from typing import List, Optional, Dict
from models_main import Track


class SoundCloudService:
    """Сервис для работы с SoundCloud через неофициальный API"""

    def __init__(self):
        self.client_id = "gZX8jnL55gAHKRgcpIMt9nTUKo94Un61"
        self.base_url = "https://api-v2.soundcloud.com"
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> Dict[str, List]:
        """Поиск по SoundCloud"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/search/tracks",
                    params={
                        'q': query,
                        'limit': limit,
                        'offset': offset,
                        'client_id': self.client_id
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "tracks": self._parse_tracks(data.get('collection', [])),
                            "users": [],
                            "playlists": []
                        }
                    else:
                        print(f"SoundCloud API error: {resp.status}")
                        return {"tracks": [], "users": [], "playlists": []}
            except Exception as e:
                print(f"SoundCloud search error: {e}")
                return {"tracks": [], "users": [], "playlists": []}

    def _parse_tracks(self, items: List[Dict]) -> List[Track]:
        """Парсинг треков"""
        tracks = []
        for item in items:
            try:
                cover = item.get('artwork_url') or item.get('user', {}).get('avatar_url')
                if cover and 'large.jpg' in cover:
                    cover = cover.replace('large.jpg', 't500x500.jpg')

                track = Track(
                    id=str(item.get('id')),
                    title=item.get('title', 'Unknown'),
                    artist=item.get('user', {}).get('username', 'Unknown'),
                    artist_id=str(item.get('user', {}).get('id')),
                    duration=item.get('duration', 0) // 1000,
                    stream_url="",  # Потребуется дополнительный запрос
                    cover=cover,
                    source="soundcloud",
                    is_explicit=item.get('explicit', False),
                    play_count=item.get('playback_count', 0),
                    genre=item.get('genre'),
                    permalink_url=item.get('permalink_url')
                )
                tracks.append(track)
            except Exception as e:
                print(f"Error parsing track: {e}")
        return tracks

    async def get_track(self, track_id: str) -> Optional[Track]:
        """Получение информации о треке"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/tracks/{track_id}",
                    params={'client_id': self.client_id},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tracks = self._parse_tracks([data])
                        return tracks[0] if tracks else None
            except Exception as e:
                print(f"Error getting track: {e}")
        return None

    @property
    def is_authenticated(self) -> bool:
        return True  # Работает без OAuth


# Глобальный экземпляр
soundcloud_service = SoundCloudService()
