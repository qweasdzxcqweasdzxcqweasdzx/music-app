"""
Recommendation Service

Система рекомендаций треков на основе:
1. Истории прослушиваний
2. Любимых треков (лайки)
3. Предпочтений пользователя
4. Similarity-based рекомендации (SoundCloud)
5. Жанровые предпочтения
"""

from typing import List, Optional, Dict, Set
from datetime import datetime, timedelta
from collections import Counter
import random

from models import Track, PlayHistory, Like
from database import get_collection
from services.soundcloud_service import soundcloud_service
from config import settings


class RecommendationService:
    """Сервис рекомендаций"""

    def __init__(self):
        self.min_tracks = settings.RECOMMENDATIONS_MIN_TRACKS
        self.max_tracks = settings.RECOMMENDATIONS_MAX_TRACKS

    async def get_recommendations_for_user(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Track]:
        """
        Получение персональных рекомендаций для пользователя

        Алгоритм:
        1. Анализируем историю прослушиваний
        2. Находим любимые жанры и артистов
        3. Получаем рекомендации от Spotify
        4. Добавляем треки от похожих артистов
        5. Перемешиваем результаты
        """
        # Получаем данные пользователя
        history = await self._get_user_history(user_id)
        likes = await self._get_user_likes(user_id)

        if not history and not likes:
            # Холодный старт - популярные треки
            return await self._get_popular_tracks(limit)

        # Анализируем предпочтения
        preferences = await self._analyze_preferences(history, likes)

        # Получаем рекомендации
        recommendations = []

        # 1. Рекомендации от SoundCloud на основе жанров
        if preferences["top_genres"]:
            soundcloud_recs = await soundcloud_service.search(
                " ".join(preferences["top_genres"][:3]),
                limit=limit
            )
            recommendations.extend(soundcloud_recs.get("tracks", []))

        # 2. Треки от топ артистов пользователя
        if preferences["top_artists"]:
            artist_tracks = await self._get_tracks_from_artists(
                preferences["top_artists"][:3],
                exclude=preferences["listened_track_ids"],
                limit=limit // 2
            )
            recommendations.extend(artist_tracks)

        # 3. Треки из любимых жанров
        if preferences["top_genres"]:
            genre_tracks = await self._get_tracks_by_genres(
                preferences["top_genres"][:3],
                exclude=preferences["listened_track_ids"],
                limit=limit // 2
            )
            recommendations.extend(genre_tracks)

        # 4. Похожие артисты
        if preferences["top_artist_ids"]:
            similar_tracks = await self._get_similar_artists_tracks(
                preferences["top_artist_ids"][:3],
                exclude=preferences["listened_track_ids"],
                limit=limit // 3
            )
            recommendations.extend(similar_tracks)

        # Удаляем дубликаты и уже прослушанные
        unique_tracks = self._deduplicate_tracks(
            recommendations,
            exclude=preferences["listened_track_ids"]
        )

        # Перемешиваем и ограничиваем
        random.shuffle(unique_tracks)
        return unique_tracks[:limit]

    async def _get_user_history(self, user_id: str) -> List[PlayHistory]:
        """Получение истории прослушиваний"""
        history_collection = await get_collection("play_history")
        history = await history_collection.find(
            {"user_id": user_id}
        ).sort("played_at", -1).limit(100).to_list(length=100)

        return [PlayHistory(**h) for h in history]

    async def _get_user_likes(self, user_id: str) -> List[Like]:
        """Получение лайков пользователя"""
        likes_collection = await get_collection("likes")
        likes = await likes_collection.find(
            {"user_id": user_id}
        ).to_list(length=500)

        return [Like(**like) for like in likes]

    async def _analyze_preferences(
        self,
        history: List[PlayHistory],
        likes: List[Like]
    ) -> Dict:
        """
        Анализ предпочтений пользователя

        Returns:
            Dict с топ артистами, жанрами, треками
        """
        # Считаем прослушивания по трекам и артистам
        track_counts = Counter(h.track_id for h in history)
        
        # Топ треков
        top_track_ids = [track_id for track_id, _ in track_counts.most_common(10)]

        # Топ артистов (по названиям, потом получим ID)
        artist_counts = Counter()
        for h in history:
            # Здесь нужен трек для получения артиста
            # Для упрощения - заглушка
            pass

        # Жанры - из Spotify на основе прослушанных треков
        top_genres = []  # Заглушка

        # ID прослушанных треков
        listened_track_ids = set(h.track_id for h in history)

        return {
            "top_artists": [],
            "top_artist_ids": [],
            "top_genres": top_genres,
            "top_track_ids": top_track_ids,
            "listened_track_ids": listened_track_ids
        }

    async def _get_popular_tracks(self, limit: int) -> List[Track]:
        """Получение популярных треков (холодный старт)"""
        # Используем SoundCloud trending
        tracks = await soundcloud_service.get_trending(limit=limit)
        return tracks[:limit]

    async def _get_tracks_from_artists(
        self,
        artists: List[str],
        exclude: Set[str],
        limit: int
    ) -> List[Track]:
        """Получение треков от артистов"""
        tracks = []
        for artist in artists:
            # Получаем треки артиста из SoundCloud
            artist_tracks = await soundcloud_service.get_user_tracks(artist, limit=limit)
            tracks.extend([t for t in artist_tracks if t.id not in exclude])

        return tracks[:limit]

    async def _get_tracks_by_genres(
        self,
        genres: List[str],
        exclude: Set[str],
        limit: int
    ) -> List[Track]:
        """Получение треков по жанрам"""
        tracks = []
        for genre in genres:
            result = await soundcloud_service.search(genre, limit=limit // len(genres))
            for track in result.get("tracks", []):
                if track.id not in exclude:
                    tracks.append(track)

        return tracks[:limit]

    async def _get_similar_artists_tracks(
        self,
        artist_ids: List[str],
        exclude: Set[str],
        limit: int
    ) -> List[Track]:
        """Получение треков от похожих артистов"""
        tracks = []

        for artist_id in artist_ids:
            # Получаем информацию об артисте
            artist = await soundcloud_service.get_user(artist_id)
            if not artist:
                continue

            # Используем поиск по похожим жанрам
            if artist.get("genres"):
                genre = artist["genres"][0] if isinstance(artist["genres"], list) else str(artist["genres"])
                result = await soundcloud_service.search(genre, limit=limit)
                for track in result.get("tracks", []):
                    if track.id not in exclude:
                        tracks.append(track)

        return tracks[:limit]

    def _deduplicate_tracks(
        self,
        tracks: List[Track],
        exclude: Set[str]
    ) -> List[Track]:
        """Удаление дубликатов"""
        seen_ids = set()
        unique = []
        
        for track in tracks:
            if track.id and track.id not in exclude and track.id not in seen_ids:
                seen_ids.add(track.id)
                unique.append(track)
        
        return unique

    async def get_track_recommendations(
        self,
        track_id: str,
        limit: int = 20
    ) -> List[Track]:
        """
        Рекомендации на основе конкретного трека
        (похожие треки)
        """
        # Получаем трек для определения жанра
        track = await soundcloud_service.get_track(track_id)
        if track and track.genre:
            result = await soundcloud_service.search(track.genre, limit=limit)
            return result.get("tracks", [])[:limit]
        return []

    async def get_artist_recommendations(
        self,
        artist_id: str,
        limit: int = 20
    ) -> List[Track]:
        """
        Рекомендации на основе артиста
        (похожие артисты и их треки)
        """
        # Получаем информацию об артисте
        artist = await soundcloud_service.get_user(artist_id)
        if not artist:
            return []

        # Поиск по жанрам артиста
        tracks = []
        if artist.get("genres"):
            genre = artist["genres"][0] if isinstance(artist["genres"], list) else str(artist["genres"])
            result = await soundcloud_service.search(genre, limit=limit)
            tracks = result.get("tracks", [])

        # Получаем треки артиста
        artist_tracks = await soundcloud_service.get_user_tracks(artist_id, limit=limit // 2)
        tracks.extend(artist_tracks)

        return tracks[:limit]

    async def get_mood_recommendations(
        self,
        mood: str,
        limit: int = 20
    ) -> List[Track]:
        """
        Рекомендации по настроению

        Mood mapping:
        - happy: high energy, positive vibes
        - sad: low energy, melancholic
        - energetic: high energy, upbeat
        - chill: low energy, relaxing
        - focus: medium energy, instrumental
        """
        # Жанры для разных настроений
        mood_genres = {
            "happy": "pop dance happy",
            "sad": "acoustic indie folk",
            "energetic": "edm dance electro",
            "chill": "chillout downtempo ambient",
            "focus": "classical study beats",
        }

        genre_query = mood_genres.get(mood, "pop")
        result = await soundcloud_service.search(genre_query, limit=limit)
        return result.get("tracks", [])[:limit]


# Глобальный экземпляр
recommendation_service = RecommendationService()
