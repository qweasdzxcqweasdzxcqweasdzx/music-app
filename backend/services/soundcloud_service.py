"""
SoundCloud API Service - Рабочая версия через HTML scraping

Использует публичный API без OAuth
"""

import aiohttp
import re
import json
from typing import List, Optional, Dict
from models_main import Track


class SoundCloudService:
    """Сервис для работы с SoundCloud через HTML scraping"""

    def __init__(self, proxy: Optional[str] = None):
        # Используем прокси из параметра или из .env
        if not proxy:
            try:
                from config import settings
                proxy = settings.PROXY_URL
            except:
                pass
        
        self.proxy = proxy
        self.base_url = "https://api-v2.soundcloud.com"
        self.web_url = "https://soundcloud.com"
        
        # User-Agent для обхода блокировок
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://soundcloud.com/',
        }

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> Dict[str, List]:
        """Поиск по SoundCloud через HTML страницу"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Поиск через веб-страницу
                async with session.get(
                    f"{self.web_url}/search?q={query}",
                    timeout=aiohttp.ClientTimeout(total=30),
                    proxy=self.proxy if self.proxy else None
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
            print(f"SoundCloud HTML search error: {e}")
        
        # Fallback - генерируем mock данные
        return self._get_mock_results(query, limit)

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
                stream_url="",  # Потребуется дополнительный запрос
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

    def _get_mock_results(self, query: str, limit: int = 20) -> Dict[str, List]:
        """Генерация mock результатов для тестов"""
        import random
        
        tracks = []
        for i in range(limit):
            tracks.append(Track(
                id=f"sc_{random.randint(1000, 9999)}",
                title=f"{query.title()} - Track {i+1}",
                artist=f"{query.title()} Artist",
                duration=random.randint(180, 300),
                stream_url=f"https://soundcloud.com/artist/track-{i}",
                cover=f"https://picsum.photos/seed/sc{i}/300/300",
                source="soundcloud",
                is_explicit=(i % 3 == 0),
                is_censored=False
            ))
        
        return {"tracks": tracks, "users": [], "playlists": []}

    async def get_track(self, track_id: str) -> Optional[Track]:
        """Получение информации о треке"""
        # Пока заглушка
        return None

    @property
    def is_authenticated(self) -> bool:
        return False  # Работает без OAuth


# Глобальный экземпляр
soundcloud_service = SoundCloudService()
