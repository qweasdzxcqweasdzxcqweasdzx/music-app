"""
Discover Weekly Service

Еженедельные рекомендации в стиле Spotify.
Генерируется каждый понедельник новый плейлист из 30 треков.

Алгоритм:
1. 40% - Новые треки от любимых артистов
2. 30% - Похожее на прослушанное (collaborative filtering)
3. 20% - Треки из любимых жанров которые ещё не слушал
4. 10% - Полностью новые открытия (random exploration)

Обновляется: Каждый понедельник в 00:00
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter
import hashlib
import random


class DiscoverWeeklyService:
    """Сервис генерации Discover Weekly"""

    def __init__(self):
        self.tracks_count = 30  # Треков в плейлисте
        self.update_day = "Monday"  # День обновления

    async def generate_discover_weekly(
        self,
        user_id: str,
        history: List[Dict],
        likes: List[str],
        top_artists: List[str],
        top_genres: List[str]
    ) -> Dict:
        """
        Генерация Discover Weekly плейлиста

        Args:
            user_id: ID пользователя
            history: История прослушиваний
            likes: Любимые треки
            top_artists: Топ артисты
            top_genres: Топ жанры

        Returns:
            Плейлист с треками
        """
        # Определяем дату следующего обновления
        next_update = self._get_next_monday()
        
        # Генерируем уникальный ID для этой недели
        week_str = datetime.now().strftime("%Y-W%W")
        playlist_id = f"discover_weekly_{user_id}_{week_str}"

        # Анализируем предпочтения
        preferences = await self._analyze_preferences(
            history, likes, top_artists, top_genres
        )

        # Генерируем треки по категориям
        tracks = []
        
        # 40% - Новые треки от любимых артистов (12 треков)
        new_from_artists = await self._get_new_from_artists(
            preferences["top_artists"], 12
        )
        tracks.extend(new_from_artists)

        # 30% - Похожее на прослушанное (9 треков)
        similar_tracks = await self._get_similar_tracks(
            preferences["listened_tracks"], 9
        )
        tracks.extend(similar_tracks)

        # 20% - Треки из любимых жанров (6 треков)
        genre_tracks = await self._get_genre_tracks(
            preferences["top_genres"], 6
        )
        tracks.extend(genre_tracks)

        # 10% - Случайные открытия (3 трека)
        random_tracks = await self._get_random_explorations(3)
        tracks.extend(random_tracks)

        # Перемешиваем
        random.shuffle(tracks)

        # Генерируем обложку
        cover_color = self._get_weekly_color()
        cover = f"https://picsum.photos/seed/{playlist_id}/300/300"

        return {
            "id": playlist_id,
            "name": "Discover Weekly",
            "description": f"Новая подборка для вас • {self.tracks_count} треков",
            "cover": cover,
            "cover_color": cover_color,
            "tracks": tracks,
            "tracks_count": len(tracks),
            "generated_at": datetime.now().isoformat(),
            "next_update": next_update.isoformat(),
            "is_weekly": True
        }

    def _get_next_monday(self) -> datetime:
        """Получение даты следующего понедельника"""
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:  # Если сегодня понедельник
            days_until_monday = 7
        next_monday = today + timedelta(days=days_until_monday)
        return next_monday.replace(hour=0, minute=0, second=0, microsecond=0)

    async def _analyze_preferences(
        self,
        history: List[Dict],
        likes: List[str],
        top_artists: List[str],
        top_genres: List[str]
    ) -> Dict:
        """Анализ предпочтений пользователя"""
        
        # Топ артисты по истории
        artist_counts = Counter(
            h.get('artist_id') or h.get('artist')
            for h in history
            if h.get('artist_id') or h.get('artist')
        )

        # Топ жанры
        genre_counts = Counter()
        for h in history:
            genres = h.get('genres', [])
            genre_counts.update(genres)

        # ID прослушанных треков
        listened_track_ids = set(h.get('track_id') for h in history if h.get('track_id'))

        return {
            "top_artists": [a for a, _ in artist_counts.most_common(20)],
            "top_genres": [g for g, _ in genre_counts.most_common(10)],
            "liked_tracks": likes,
            "listened_tracks": list(listened_track_ids),
            "history": history
        }

    async def _get_new_from_artists(
        self,
        artists: List[str],
        limit: int
    ) -> List[Dict]:
        """Новые треки от любимых артистов"""
        # В реальности: Spotify API - get artist's new releases
        return self._generate_mock_tracks(artists, limit, new=True)

    async def _get_similar_tracks(
        self,
        listened_tracks: List[str],
        limit: int
    ) -> List[Dict]:
        """Похожие треки на прослушанные"""
        # В реальности: Spotify API - get recommendations based on seed tracks
        return self._generate_mock_tracks(["similar"], limit)

    async def _get_genre_tracks(
        self,
        genres: List[str],
        limit: int
    ) -> List[Dict]:
        """Треки из любимых жанров"""
        # В реальности: Spotify API - search by genre
        return self._generate_mock_tracks(genres[:3], limit)

    async def _get_random_explorations(
        self,
        limit: int
    ) -> List[Dict]:
        """Случайные открытия"""
        # В реальности: Spotify API - completely random recommendations
        return self._generate_mock_tracks(["explore"], limit, random=True)

    def _generate_mock_tracks(
        self,
        seeds: List[str],
        limit: int,
        new: bool = False,
        random: bool = False
    ) -> List[Dict]:
        """Генерация mock треков"""
        tracks = []
        for i in range(limit):
            seed = seeds[i % len(seeds)] if seeds else "unknown"
            tracks.append({
                "id": f"track_{seed}_{i}_{random.randint(1000, 9999)}",
                "title": f"{seed.title()} Discovery {i+1}",
                "artist": f"{seed.title()} Artist",
                "duration": 180 + (i * 10) % 120,
                "cover": f"https://picsum.photos/seed/{seed}{i}/300/300",
                "is_new": new,
                "is_exploration": random
            })
        return tracks

    def _get_weekly_color(self) -> str:
        """Цвет обложки для этой недели"""
        # Меняется каждую неделю
        week_num = datetime.now().isocalendar()[1]
        colors = [
            "#1DB954",  # Green
            "#E91429",  # Red
            "#DC148C",  # Pink
            "#0D73EC",  # Blue
            "#8C67AC",  # Purple
            "#BC5900",  # Orange
        ]
        return colors[week_num % len(colors)]

    def should_update(self, last_generated: datetime) -> bool:
        """Проверка нужно ли обновлять плейлист"""
        # Если сегодня понедельник и ещё не генерировали сегодня
        today = datetime.now()
        is_monday = today.weekday() == 0  # 0 = Monday
        
        if not is_monday:
            return False
            
        # Если последний раз генерировали не на этой неделе
        last_week = last_generated.isocalendar()[1]
        current_week = today.isocalendar()[1]
        
        return current_week > last_week


# Глобальный экземпляр
discover_weekly_service = DiscoverWeeklyService()
