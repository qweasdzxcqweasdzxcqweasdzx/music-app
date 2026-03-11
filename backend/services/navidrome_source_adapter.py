"""
Navidrome Service Adapter

Адаптер для Navidrome/Subsonic API, реализующий интерфейс MusicSource.
"""

from typing import List, Optional, Dict
from services.music_source_base import MusicSource
from services.navidrome_service import navidrome_service as nd_service
from models_main import Track


class NavidromeSource(MusicSource):
    """Navidrome источник музыки (локальная коллекция)"""

    @property
    def source_name(self) -> str:
        return "navidrome"

    @property
    def is_available(self) -> bool:
        return nd_service.is_connected

    async def connect(
        self,
        base_url: str,
        username: str,
        password: Optional[str] = None,
        jwt_token: Optional[str] = None
    ) -> bool:
        """Подключение к Navidrome серверу"""
        return await nd_service.connect(base_url, username, password, jwt_token)

    async def search(self, query: str, limit: int = 20) -> Dict[str, List]:
        """Поиск по Navidrome"""
        return await nd_service.search3(query, limit)

    async def get_track(self, song_id: str) -> Optional[Track]:
        return await nd_service.get_song(song_id)

    async def get_track_stream_url(self, song_id: str) -> Optional[str]:
        return await nd_service.get_stream_url(song_id)

    async def get_artist(self, artist_id: str) -> Optional[Dict]:
        return await nd_service.get_artist(artist_id)

    async def get_artist_tracks(self, artist_id: str, limit: int = 20) -> List[Track]:
        return await nd_service.get_artist_songs(artist_id)

    async def get_album(self, album_id: str) -> Optional[Dict]:
        return await nd_service.get_album(album_id)

    async def get_album_tracks(self, album_id: str, limit: int = 50) -> List[Track]:
        album = await self.get_album(album_id)
        if album:
            tracks = []
            for song in album.get('song', []):
                track = nd_service._parse_song(song)
                if track:
                    tracks.append(track)
            return tracks[:limit]
        return []

    async def get_top_tracks(self, limit: int = 20) -> List[Track]:
        # Navidrome не имеет "топ треков", используем случайные
        # или недавно добавленные
        result = await nd_service.search3("", limit)
        return result.get("tracks", [])[:limit]

    async def get_new_releases(self, limit: int = 20) -> List[Dict]:
        # Получение недавно добавленных альбомов
        # Через search3 с пустым запросом
        result = await nd_service.search3("", limit)
        return result.get("albums", [])[:limit]

    async def get_recommendations(
        self,
        seed_artists: Optional[List[str]] = None,
        seed_tracks: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Track]:
        # Navidrome не имеет API рекомендаций
        # Используем поиск по жанрам или похожим артистам
        if seed_genres:
            tracks = []
            for genre in seed_genres[:3]:
                genre_tracks = await nd_service.get_songs_by_genre(genre, limit // 3)
                tracks.extend(genre_tracks)
            return tracks[:limit]

        if seed_artists:
            # Получение похожих артистов
            for artist_id in seed_artists[:3]:
                artist = await nd_service.get_artist(artist_id)
                if artist:
                    for similar in artist.get('similar_artists', []):
                        similar_tracks = await self.get_artist_tracks(
                            similar['id'],
                            limit // 6
                        )
                        tracks.extend(similar_tracks)
            return tracks[:limit]

        return []

    async def get_genres(self) -> List[Dict]:
        genres = await nd_service.get_genres()
        return [
            {"id": g["name"], "name": g["name"], "source": "navidrome"}
            for g in genres
        ]

    async def get_tracks_by_genre(self, genre: str, limit: int = 20) -> List[Track]:
        return await nd_service.get_songs_by_genre(genre, limit)

    async def get_starred(self) -> Dict[str, List]:
        """Получение избранных треков"""
        return await nd_service.get_starred()

    async def get_playlists(self) -> List[Dict]:
        """Получение плейлистов"""
        return await nd_service.get_playlists()

    async def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Получение плейлиста"""
        return await nd_service.get_playlist(playlist_id)


# Глобальный экземпляр
navidrome_source = NavidromeSource()
