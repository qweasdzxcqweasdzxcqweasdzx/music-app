"""
Genius Lyrics Service

Получение текстов песен через Genius API.
Документация: https://docs.genius.com/

Для использования нужен API токен от https://genius.com/api_clients
"""

import aiohttp
from typing import Optional, Dict, List
from config import settings


class GeniusLyricsService:
    """Сервис для получения текстов песен из Genius"""

    def __init__(self):
        self.api_token = settings.GENIUS_API_TOKEN
        self.base_url = "https://api.genius.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}" if self.api_token else None
        }

    async def search(self, query: str, artist: str = "") -> Optional[Dict]:
        """
        Поиск текста песни

        Args:
            query: Название трека
            artist: Имя артиста (опционально)

        Returns:
            Информация о треке с Genius или None
        """
        if not self.api_token:
            return None

        search_query = f"{artist} {query}" if artist else query

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    params={"q": search_query}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        hits = data.get("response", {}).get("hits", [])
                        
                        if hits:
                            # Возвращаем первый результат
                            return hits[0]["result"]
                    return None
            except Exception as e:
                print(f"Genius search error: {e}")
                return None

    async def get_lyrics(self, song_id: int) -> Optional[str]:
        """
        Получение текста песни по ID

        Args:
            song_id: ID песни на Genius

        Returns:
            Текст песни или None
        """
        if not self.api_token:
            return None

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/songs/{song_id}",
                    headers=self.headers,
                    params={"text_format": "plain"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        song = data.get("response", {}).get("song", {})
                        
                        # Получаем текст из path (нужен парсинг HTML)
                        # Genius не отдаёт полный текст через API
                        # Нужно парсить страницу
                        return await self._parse_lyrics(song.get("url"))
                    return None
            except Exception as e:
                print(f"Genius lyrics error: {e}")
                return None

    async def _parse_lyrics(self, url: str) -> Optional[str]:
        """
        Парсинг текста со страницы Genius

        Args:
            url: URL страницы песни на Genius

        Returns:
            Текст песни или None
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        
                        # Простой парсинг (в реальности нужен BeautifulSoup)
                        # Ищем <div class="lyrics"> или [data-lyrics-container="true"]
                        import re
                        
                        # Поиск контейнера с текстом
                        match = re.search(
                            r'data-lyrics-container="true"[^>]*>(.*?)</div>',
                            html,
                            re.DOTALL
                        )
                        
                        if match:
                            # Удаляем HTML теги
                            text = re.sub(r'<[^>]+>', '', match.group(1))
                            # Удаляем лишние пробелы
                            text = re.sub(r'\n\s*\n', '\n', text)
                            return text.strip()
                        
                        return None
            except Exception as e:
                print(f"Lyrics parsing error: {e}")
                return None

    async def get_track_lyrics(self, track_title: str, artist_name: str) -> Optional[Dict]:
        """
        Получение текста для трека

        Args:
            track_title: Название трека
            artist_name: Имя артиста

        Returns:
            Dict с текстом и метаданными
        """
        # Поиск трека
        song_info = await self.search(track_title, artist_name)
        
        if not song_info:
            return None

        # Получение текста
        lyrics = await self.get_lyrics(song_info["id"])

        return {
            "track_id": song_info.get("id"),
            "title": song_info.get("title"),
            "artist": song_info.get("artist_names"),
            "lyrics": lyrics or "Текст недоступен",
            "url": song_info.get("url"),
            "cover": song_info.get("song_art_image_url"),
            "synced": False
        }


# Альтернативный сервис - Lyrics OVH (бесплатный, без токена)
class LyricsOVHService:
    """Бесплатный сервис текстов песен"""

    def __init__(self):
        self.base_url = "https://api.lyrics.ovh"

    async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """
        Получение текста песни

        Args:
            artist: Имя артиста
            title: Название песни

        Returns:
            Текст песни или None
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/{artist}/{title}"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("lyrics")
                    return None
            except Exception as e:
                print(f"LyricsOVH error: {e}")
                return None


# Глобальные экземпляры
genius_service = GeniusLyricsService()
lyrics_ovh_service = LyricsOVHService()
