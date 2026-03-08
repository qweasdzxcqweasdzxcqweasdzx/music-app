"""
SoundCloud Service Adapter

Адаптер для SoundCloud API, реализующий интерфейс MusicSource.
"""

from typing import List, Optional, Dict
from services.music_source_base import MusicSource
from services.soundcloud_service import soundcloud_service as sc_service
from models import Track


class SoundCloudSource(MusicSource):
    """SoundCloud источник музыки"""

    @property
    def source_name(self) -> str:
        return "soundcloud"

    @property
    def is_available(self) -> bool:
        return sc_service.client_id is not None

    async def search(self, query: str, limit: int = 20) -> Dict[str, List]:
        """Поиск по SoundCloud"""
        return await sc_service.search(query, limit)

    async def get_track(self, track_id: str) -> Optional[Track]:
        return await sc_service.get_track(track_id)

    async def get_track_stream_url(self, track_id: str) -> Optional[str]:
        return await sc_service.get_track_stream_url(track_id)

    async def get_artist(self, user_id: str) -> Optional[Dict]:
        return await sc_service.get_user(user_id)

    async def get_artist_tracks(self, user_id: str, limit: int = 20) -> List[Track]:
        return await sc_service.get_user_tracks(user_id, limit)

    async def get_album(self, playlist_id: str) -> Optional[Dict]:
        return await sc_service.get_playlist(playlist_id)

    async def get_album_tracks(self, playlist_id: str, limit: int = 50) -> List[Track]:
        playlist = await self.get_album(playlist_id)
        if playlist:
            return playlist.get("tracks", [])[:limit]
        return []

    async def get_top_tracks(self, limit: int = 20) -> List[Track]:
        return await sc_service.get_trending(limit)

    async def get_new_releases(self, limit: int = 20) -> List[Dict]:
        # SoundCloud не имеет прямого аналога "новых релизов"
        # Используем поиск по популярным плейлистам
        return []

    async def get_recommendations(
        self,
        seed_artists: Optional[List[str]] = None,
        seed_tracks: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Track]:
        # SoundCloud не имеет API рекомендаций
        # Используем поиск по жанрам
        if seed_genres:
            query = " ".join(seed_genres[:3])
            result = await self.search(query, limit)
            return result.get("tracks", [])
        return []

    async def get_genres(self) -> List[Dict]:
        # SoundCloud использует свободные теги
        return [
            {"id": "electronic", "name": "Electronic", "source": "soundcloud"},
            {"id": "hip-hop-rap", "name": "Hip-hop & Rap", "source": "soundcloud"},
            {"id": "indie", "name": "Indie", "source": "soundcloud"},
            {"id": "pop", "name": "Pop", "source": "soundcloud"},
            {"id": "rock", "name": "Rock", "source": "soundcloud"},
            {"id": "ambient", "name": "Ambient", "source": "soundcloud"},
            {"id": "jazz", "name": "Jazz", "source": "soundcloud"},
            {"id": "classical", "name": "Classical", "source": "soundcloud"},
        ]

    async def get_tracks_by_genre(self, genre: str, limit: int = 20) -> List[Track]:
        result = await self.search(genre, limit)
        return result.get("tracks", [])[:limit]


# Глобальный экземпляр
soundcloud_source = SoundCloudSource()
