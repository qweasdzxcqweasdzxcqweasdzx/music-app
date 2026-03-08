"""
YouTube Music Service

Полноценный сервис для поиска музыки на YouTube/YouTube Music
с использованием yt-dlp. Поддерживает поиск explicit версий.
"""

import re
import asyncio
from typing import List, Optional, Dict, Any
from models import Track

# Попытка импорта yt-dlp
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False


class YouTubeMusicService:
    """Сервис для работы с YouTube Music"""

    def __init__(self, proxy: Optional[str] = None):
        # Используем прокси из параметра или из .env
        if not proxy:
            from config import settings
            proxy = settings.PROXY_URL
        
        self.proxy = proxy
        self._available = YTDLP_AVAILABLE
        self._yt_dlp = yt_dlp if YTDLP_AVAILABLE else None

        # Опции для yt-dlp
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch',
        }
        if proxy:
            self.ydl_opts['proxy'] = proxy

    # ==================== Поиск ====================

    async def search(
        self,
        query: str,
        limit: int = 20,
        prefer_explicit: bool = False
    ) -> List[Track]:
        """
        Поиск треков на YouTube

        Args:
            query: Поисковый запрос
            limit: Количество результатов
            prefer_explicit: Приоритет explicit версий

        Returns:
            Список треков
        """
        if not self._available:
            return self._get_mock_tracks(query, limit)

        try:
            # Формируем поисковый запрос
            search_query = f"ytsearch{limit}:{query}"
            if prefer_explicit:
                search_query = f"ytsearch{limit}:{query} explicit original"

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._extract_search,
                search_query
            )

            return self._parse_results(results, query)

        except Exception as e:
            print(f"YouTube search error: {e}")
            return self._get_mock_tracks(query, limit)

    def _extract_search(self, search_query: str) -> Dict:
        """Извлечение результатов поиска (синхронно)"""
        with self._yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            return ydl.extract_info(search_query, download=False)

    def _parse_results(self, results: Dict, original_query: str) -> List[Track]:
        """Парсинг результатов YouTube"""
        tracks = []
        entries = results.get('entries', [])

        for entry in entries:
            if entry.get('_type') != 'video':
                continue

            try:
                # Извлечение информации
                title = entry.get('title', 'Unknown')
                artist = self._extract_artist(title, entry.get('channel', ''))
                duration = entry.get('duration', 180)

                # Определение explicit версии
                is_explicit = self._is_explicit_version(title, entry.get('description', ''))

                # Формирование URL
                video_id = entry.get('id', '')
                stream_url = f"https://www.youtube.com/watch?v={video_id}"
                cover = entry.get('thumbnail', f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg")

                track = Track(
                    id=video_id,
                    title=title,
                    artist=artist,
                    duration=duration or 180,
                    stream_url=stream_url,
                    preview_url=None,
                    cover=cover,
                    source="youtube",
                    is_explicit=is_explicit,
                    is_censored=self._is_censored_version(title),
                    play_count=0,
                    popularity=int(entry.get('view_count', 0) or 0),
                    genres=[],
                    description=entry.get('description', '')
                )
                tracks.append(track)

            except Exception as e:
                print(f"Error parsing YouTube entry: {e}")
                continue

        return tracks

    def _extract_artist(self, title: str, channel: str) -> str:
        """Извлечение имени артиста из названия/канала"""
        # Паттерны для извлечения артиста
        patterns = [
            r'^(.+?)\s*[-–]\s*.+',  # Artist - Title
            r'^(.+?)\s*:\s*.+',      # Artist: Title
            r'^(.+?)\s*feat\..+',    # Artist feat. ...
            r'^(.+?)\s*ft\..+',      # Artist ft. ...
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Если не нашли, используем канал
        if channel and channel != title:
            return channel

        return "Unknown Artist"

    def _is_explicit_version(self, title: str, description: str = "") -> bool:
        """Проверка на explicit версию"""
        text = (title + " " + description).lower()

        explicit_markers = [
            'explicit', 'uncensored', 'dirty', 'original',
            'album version', 'lp version', 'uncut',
            'оригинал', 'нецензурная', 'полная версия'
        ]

        return any(marker in text for marker in explicit_markers)

    def _is_censored_version(self, title: str) -> bool:
        """Проверка на цензурную версию"""
        title_lower = title.lower()

        censor_markers = [
            'clean', 'radio edit', 'censored', 'edited',
            'радио версия', 'цензурная', 'для эфира',
            'family friendly', 'pg version'
        ]

        return any(marker in title_lower for marker in censor_markers)

    def _get_mock_tracks(self, query: str, limit: int) -> List[Track]:
        """Mock данные для тестов"""
        tracks = []
        for i in range(limit):
            tracks.append(Track(
                title=f"{query} (YouTube Track {i+1})",
                artist="YouTube Artist",
                duration=180 + (i * 10) % 120,
                stream_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                cover=f"https://picsum.photos/seed/yt{i}/300/300",
                source="youtube",
                is_explicit=(i % 3 == 0),
                is_censored=(i % 5 == 0)
            ))
        return tracks

    # ==================== Стриминг ====================

    async def get_track_stream(self, track_id: str) -> Optional[str]:
        """
        Получение URL аудио потока

        Args:
            track_id: ID видео на YouTube

        Returns:
            URL потока или None
        """
        if not self._available:
            return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

        try:
            loop = asyncio.get_event_loop()
            audio_url = await loop.run_in_executor(
                None,
                self._extract_audio_url,
                track_id
            )
            return audio_url

        except Exception as e:
            print(f"YouTube stream error: {e}")
            return None

    def _extract_audio_url(self, video_id: str) -> Optional[str]:
        """Извлечение URL аудио (синхронно)"""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best',
            'extract-audio': True,
        }
        if self.proxy:
            opts['proxy'] = self.proxy

        with self._yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            if info and 'formats' in info:
                # Ищем аудио формат
                for fmt in info['formats']:
                    if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                        return fmt.get('url')
                # Fallback на лучший формат
                return info['formats'][-1].get('url')

        return None

    # ==================== Поиск оригинальных версий ====================

    async def get_original_track(self, query: str) -> Optional[Track]:
        """
        Поиск оригинальной (explicit) версии

        Args:
            query: Поисковый запрос

        Returns:
            Трек или None
        """
        # Приоритет explicit версий
        tracks = await self.search(f"{query} explicit original", limit=10, prefer_explicit=True)

        # Фильтрация explicit
        explicit_tracks = [t for t in tracks if t.is_explicit and not t.is_censored]

        if explicit_tracks:
            return explicit_tracks[0]

        # Fallback на обычный поиск
        tracks = await self.search(query, limit=5)
        return tracks[0] if tracks else None

    async def get_track_by_query(self, query: str, artist: str = "") -> Optional[Track]:
        """
        Точный поиск трека

        Args:
            query: Название трека
            artist: Имя артиста

        Returns:
            Трек или None
        """
        full_query = f"{artist} {query}".strip()
        tracks = await self.search(full_query, limit=10)

        if not tracks:
            return None

        # Поиск лучшего совпадения
        from services.blues_detection_service import blues_detection_service

        best = blues_detection_service.find_best_match(
            Track(title=query, artist=artist, duration=0, stream_url="", source="youtube"),
            tracks,
            min_similarity=0.5
        )

        return best or tracks[0]

    async def find_uncensored_version(
        self,
        censored_track: Track
    ) -> Optional[Track]:
        """
        Поиск нецензурированной версии трека

        Args:
            censored_track: Цензурированный трек

        Returns:
            Нецензурированная версия или None
        """
        from services.blues_detection_service import blues_detection_service

        # Генерация поисковых запросов
        queries = blues_detection_service.generate_search_queries(
            censored_track,
            prefer_explicit=True
        )

        # Поиск по каждому запросу
        for query in queries[:5]:  # Ограничиваем количество запросов
            tracks = await self.search(query, limit=5, prefer_explicit=True)

            for track in tracks:
                if track.is_explicit and not track.is_censored:
                    # Проверка схожести
                    similarity = blues_detection_service.similarity_ratio(
                        censored_track.title,
                        track.title
                    )
                    if similarity > 0.6:
                        return track

        return None

    @property
    def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        return self._available
