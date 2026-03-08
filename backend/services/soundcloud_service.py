"""
SoundCloud API Service - Версия с обходом блокировок

Использует неофициальный API через scraper
"""

import aiohttp
import re
import json
from typing import List, Optional, Dict
from models import Track


class SoundCloudService:
    """Сервис для работы с SoundCloud через веб-скрапинг"""

    def __init__(self, proxy: Optional[str] = None):
        # Используем прокси из параметра или из .env
        if not proxy:
            try:
                from config import settings
                proxy = settings.PROXY_URL
            except:
                pass
        
        self.client_id = "gZX8jnL55gAHKRgcpIMt9nTUKo94Un61"
        self.base_url = "https://api-v2.soundcloud.com"
        self.web_url = "https://soundcloud.com"
        self.proxy = proxy
        self._session: Optional[aiohttp.ClientSession] = None
        
        # User-Agent для обхода блокировок
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://soundcloud.com/',
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            proxy = self.proxy if self.proxy else None
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> Dict[str, List]:
        """Поиск по SoundCloud через веб-API"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Используем публичный API
                params = {
                    'q': query,
                    'limit': limit,
                    'offset': offset,
                    'client_id': self.client_id
                }
                
                proxy = self.proxy if self.proxy else None
                
                async with session.get(
                    f"{self.base_url}/search/tracks",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
                    proxy=proxy
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
                        # Пробуем альтернативный метод
                        return await self._search_alternative(query, limit)
        except Exception as e:
            print(f"SoundCloud search error: {e}")
            return await self._search_alternative(query, limit)

    async def _search_alternative(self, query: str, limit: int = 20) -> Dict[str, List]:
        """Альтернативный поиск через HTML страницу"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Поиск через веб-страницу
                async with session.get(
                    f"{self.web_url}/search?q={query}",
                    timeout=aiohttp.ClientTimeout(total=30),
                    proxy=self.proxy
                ) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        # Извлекаем JSON данные из страницы
                        tracks = self._parse_html_search(html, limit)
                        return {
                            "tracks": tracks,
                            "users": [],
                            "playlists": []
                        }
        except Exception as e:
            print(f"Alternative search error: {e}")
        
        return {"tracks": [], "users": [], "playlists": []}

    def _parse_html_search(self, html: str, limit: int = 20) -> List[Track]:
        """Парсинг треков из HTML страницы поиска"""
        tracks = []
        try:
            # Поиск JSON данных в странице
            match = re.search(r'<script[^>]*>window\.__sc_versioned_preloaded_data\s*=\s*(\{.*?\});</script>', html, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                # Извлечение треков из данных
                for key, value in data.items():
                    if isinstance(value, dict) and value.get('kind') == 'track':
                        track = self._parse_track_data(value)
                        if track:
                            tracks.append(track)
                            if len(tracks) >= limit:
                                break
        except Exception as e:
            print(f"HTML parsing error: {e}")
        
        return tracks

    def _parse_tracks(self, items: List[Dict]) -> List[Track]:
        """Парсинг треков из JSON API"""
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

    def _parse_track_data(self, data: Dict) -> Optional[Track]:
        """Парсинг данных трека"""
        try:
            cover = data.get('artwork_url') or data.get('user', {}).get('avatar_url')
            if cover and 'large.jpg' in cover:
                cover = cover.replace('large.jpg', 't500x500.jpg')

            return Track(
                id=str(data.get('id')),
                title=data.get('title', 'Unknown'),
                artist=data.get('user', {}).get('username', 'Unknown'),
                artist_id=str(data.get('user', {}).get('id')),
                duration=data.get('duration', 0) // 1000,
                stream_url="",
                cover=cover,
                source="soundcloud",
                is_explicit=data.get('explicit', False),
                play_count=data.get('playback_count', 0),
                genre=data.get('genre'),
                permalink_url=data.get('permalink_url')
            )
        except Exception as e:
            print(f"Error parsing track data: {e}")
            return None

    async def get_track(self, track_id: str) -> Optional[Track]:
        """Получение информации о треке"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(
                    f"{self.base_url}/tracks/{track_id}",
                    params={'client_id': self.client_id},
                    timeout=aiohttp.ClientTimeout(total=10),
                    proxy=self.proxy
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
        return False  # Работает без OAuth


# Глобальный экземпляр
soundcloud_service = SoundCloudService()
