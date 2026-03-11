"""
Music Source Base Module

Абстрактный базовый класс для всех источников музыки.
Обеспечивает единый интерфейс для работы с разными провайдерами.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from models_main import Track


class MusicSource(ABC):
    """
    Абстрактный базовый класс для источника музыки

    Все источники музыки (SoundCloud, Navidrome, AI)
    должны реализовывать этот интерфейс.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Название источника (soundcloud, navidrome, ai)"""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Доступен ли источник (настроен и подключен)"""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> Dict[str, List]:
        """
        Поиск по источнику

        Args:
            query: Поисковый запрос
            limit: Количество результатов

        Returns:
            Dict с ключами: tracks, artists, albums
        """
        pass

    @abstractmethod
    async def get_track(self, track_id: str) -> Optional[Track]:
        """Получение трека по ID"""
        pass

    @abstractmethod
    async def get_track_stream_url(self, track_id: str) -> Optional[str]:
        """Получение URL для стриминга трека"""
        pass

    @abstractmethod
    async def get_artist(self, artist_id: str) -> Optional[Dict]:
        """Получение информации об артисте"""
        pass

    @abstractmethod
    async def get_artist_tracks(self, artist_id: str, limit: int = 20) -> List[Track]:
        """Получение треков артиста"""
        pass

    @abstractmethod
    async def get_album(self, album_id: str) -> Optional[Dict]:
        """Получение альбома"""
        pass

    @abstractmethod
    async def get_album_tracks(self, album_id: str, limit: int = 50) -> List[Track]:
        """Получение треков альбома"""
        pass

    @abstractmethod
    async def get_top_tracks(self, limit: int = 20) -> List[Track]:
        """Получение популярных треков"""
        pass

    @abstractmethod
    async def get_new_releases(self, limit: int = 20) -> List[Dict]:
        """Получение новых релизов"""
        pass

    @abstractmethod
    async def get_recommendations(
        self,
        seed_artists: Optional[List[str]] = None,
        seed_tracks: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Track]:
        """Получение рекомендаций"""
        pass

    @abstractmethod
    async def get_genres(self) -> List[Dict]:
        """Получение списка жанров"""
        pass

    @abstractmethod
    async def get_tracks_by_genre(self, genre: str, limit: int = 20) -> List[Track]:
        """Получение треков по жанру"""
        pass

    async def health_check(self) -> Dict:
        """Проверка здоровья источника"""
        return {
            "name": self.source_name,
            "available": self.is_available,
            "status": "healthy" if self.is_available else "unavailable"
        }


class MusicSourceManager:
    """
    Менеджер источников музыки

    Управляет множественными источниками и предоставляет
    единый интерфейс для работы с ними.
    """

    def __init__(self):
        self._sources: Dict[str, MusicSource] = {}

    def register_source(self, source: MusicSource) -> None:
        """Регистрация источника"""
        self._sources[source.source_name] = source

    def unregister_source(self, source_name: str) -> None:
        """Удаление источника"""
        if source_name in self._sources:
            del self._sources[source_name]

    def get_source(self, source_name: str) -> Optional[MusicSource]:
        """Получение источника по названию"""
        return self._sources.get(source_name)

    def get_available_sources(self) -> List[str]:
        """Получение списка доступных источников"""
        return [
            name for name, source in self._sources.items()
            if source.is_available
        ]

    def get_all_sources(self) -> Dict[str, MusicSource]:
        """Получение всех зарегистрированных источников"""
        return self._sources.copy()

    async def search_all(
        self,
        query: str,
        limit: int = 20,
        sources: Optional[List[str]] = None
    ) -> Dict[str, List]:
        """
        Поиск по всем или указанным источникам

        Args:
            query: Поисковый запрос
            limit: Количество результатов
            sources: Список источников (None = все доступные)

        Returns:
            Объединённые результаты поиска
        """
        import asyncio

        if sources is None:
            sources = self.get_available_sources()

        # Запуск поиска по всем источникам параллельно
        tasks = []
        for source_name in sources:
            source = self.get_source(source_name)
            if source and source.is_available:
                tasks.append(source.search(query, limit // len(sources)))

        if not tasks:
            return {"tracks": [], "artists": [], "albums": []}

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Объединение результатов
        all_tracks = []
        all_artists = []
        all_albums = []

        for result in results:
            if isinstance(result, Exception):
                continue
            all_tracks.extend(result.get("tracks", []))
            all_artists.extend(result.get("artists", []))
            all_albums.extend(result.get("albums", []))

        # Сортировка по популярности и удаление дубликатов
        seen_ids = set()
        unique_tracks = []
        unique_artists = []
        unique_albums = []

        for track in all_tracks:
            track_id = f"{track.source}:{track.id}"
            if track_id not in seen_ids:
                seen_ids.add(track_id)
                unique_tracks.append(track)

        for artist in all_artists:
            artist_id = f"{artist.get('source', 'unknown')}:{artist.get('id')}"
            if artist_id not in seen_ids:
                seen_ids.add(artist_id)
                unique_artists.append(artist)

        for album in all_albums:
            album_id = f"{album.get('source', 'unknown')}:{album.get('id')}"
            if album_id not in seen_ids:
                seen_ids.add(album_id)
                unique_albums.append(album)

        return {
            "tracks": unique_tracks[:limit],
            "artists": unique_artists[:limit // 2],
            "albums": unique_albums[:limit // 2]
        }

    async def health_check_all(self) -> Dict[str, Dict]:
        """Проверка здоровья всех источников"""
        results = {}
        for name, source in self._sources.items():
            results[name] = await source.health_check()
        return results


# Глобальный экземпляр менеджера
source_manager = MusicSourceManager()
