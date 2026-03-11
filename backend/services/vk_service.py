"""
VK Music API Service

Примечание: Это неофициальный API. Для продакшена рекомендуется
использовать официальное партнерство с VK или другие легальные источники.

Альтернативы:
- Yandex Music API (неофициально)
- Spotify API (официально, требуется premium)
- SoundCloud API
- Собственная библиотека треков

VK API Docs: https://dev.vk.com/ru/method/audio
"""

import aiohttp
import hashlib
import time
from typing import List, Optional, Dict
from models_main import Track


class VKMusicService:
    """Сервис для работы с VK Music"""

    def __init__(self):
        self.base_url = "https://api.vk.com/method"
        self.version = "5.131"
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.token_expires = 0

    async def _get_access_token(self) -> Optional[str]:
        """Получение access токена VK"""
        if self.access_token and time.time() < self.token_expires:
            return self.access_token

        # Implicit flow для клиентских приложений
        # https://dev.vk.com/ru/api/access_token/implicit-flow
        if not self.client_id or not self.client_secret:
            return None

        # Запрос токена (упрощённая версия)
        async with aiohttp.ClientSession() as session:
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            try:
                async with session.get(
                    f"{self.base_url}/oauth2_client_credentials",
                    params=params
                ) as resp:
                    data = await resp.json()
                    if 'access_token' in data:
                        self.access_token = data['access_token']
                        self.token_expires = time.time() + data.get('expires_in', 3600)
                        return self.access_token
            except Exception as e:
                print(f"Error getting VK token: {e}")
        
        return None

    async def search(self, query: str, limit: int = 20) -> List[Track]:
        """
        Поиск треков через VK API

        Args:
            query: Поисковый запрос
            limit: Количество результатов

        Returns:
            Список треков
        """
        token = await self._get_access_token()
        
        if not token:
            # Возврат заглушки если нет токена
            return await self._search_mock(query, limit)

        params = {
            'q': query,
            'count': limit,
            'access_token': token,
            'v': self.version
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/audio.search",
                    params=params
                ) as resp:
                    data = await resp.json()
                    
                    if 'response' in data and 'items' in data['response']:
                        tracks = []
                        for item in data['response']['items']:
                            track = self._parse_vk_track(item)
                            if track:
                                tracks.append(track)
                        return tracks[:limit]
        except Exception as e:
            print(f"VK search error: {e}")
        
        return await self._search_mock(query, limit)

    def _parse_vk_track(self, item: Dict) -> Optional[Track]:
        """Парсинг трека из VK API ответа"""
        try:
            # VK audio fields:
            # artist, title, duration, url, cover (в новых версиях)
            artist = item.get('artist', 'Unknown')
            title = item.get('title', 'Unknown')
            duration = item.get('duration', 0)
            url = item.get('url', '')
            
            # Обложка (может отсутствовать)
            cover = None
            if 'album' in item and 'thumb' in item['album']:
                cover = item['album']['thumb']
            elif 'cover' in item:
                cover = item['cover']

            # Проверка на explicit
            is_explicit = item.get('is_explicit', False)

            return Track(
                title=title,
                artist=artist,
                duration=duration,
                stream_url=url,
                cover=cover,
                source="vk",
                is_explicit=is_explicit
            )
        except Exception as e:
            print(f"Error parsing VK track: {e}")
            return None

    async def _search_mock(self, query: str, limit: int = 20) -> List[Track]:
        """Mock поиск для демонстрации"""
        tracks = []
        
        # Генерация разнообразных моков
        mock_artists = [
            "The Weeknd", "Dua Lipa", "Ed Sheeran", "Taylor Swift",
            "Arctic Monkeys", "Imagine Dragons", "OneRepublic", "Coldplay"
        ]
        
        for i in range(limit):
            artist = mock_artists[i % len(mock_artists)]
            tracks.append(Track(
                title=f"{query} (Track {i+1})",
                artist=artist,
                duration=180 + (i * 10) % 120,
                stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                cover=f"https://picsum.photos/seed/{query}{i}/300/300",
                source="vk",
                is_explicit=(i % 5 == 0)  # Каждый 5-й трек explicit
            ))
        
        return tracks

    async def get_track_stream(self, track_id: str) -> Optional[str]:
        """Получение URL потока для трека"""
        # Для VK это уже есть в track.stream_url
        return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

    async def get_artist(self, artist_id: str) -> Optional[Dict]:
        """Получение информации об артисте"""
        # Заглушка
        return {
            "id": artist_id,
            "name": "Artist Name",
            "cover": "https://picsum.photos/seed/artist/300/300",
            "banner": "https://picsum.photos/seed/banner/800/400",
            "description": "Описание артиста",
            "subscribers_count": 1000000
        }

    async def get_artist_tracks(self, artist_id: str, limit: int = 20) -> List[Track]:
        """Получение треков артиста"""
        # Заглушка
        tracks = []
        for i in range(limit):
            tracks.append(Track(
                title=f"Track {i+1}",
                artist="Artist Name",
                duration=180 + i * 10,
                stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                cover=f"https://picsum.photos/seed/track{i}/300/300",
                source="vk"
            ))
        return tracks
