"""
Daily Mixes Service

Генерация персональных ежедневных миксов на основе:
1. Истории прослушиваний за последние 30 дней
2. Любимых треков и артистов
3. Жанровых предпочтений
4. Времени суток и дня недели

Алгоритм как у Spotify:
- 6 миксов по 50 треков каждый
- Каждый микс фокусируется на определённом жанре/настроении
- Миксы обновляются ежедневно в полночь
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter
import hashlib


class DailyMixesService:
    """Сервис генерации Daily Mixes"""

    def __init__(self):
        self.mix_count = 6  # Количество миксов
        self.tracks_per_mix = 50  # Треков в каждом миксе

    async def generate_daily_mixes(
        self,
        user_id: str,
        history: List[Dict],
        likes: List[str],
        top_artists: List[str]
    ) -> List[Dict]:
        """
        Генерация 6 ежедневных миксов

        Args:
            user_id: ID пользователя
            history: История прослушиваний
            likes: Любимые треки
            top_artists: Топ артисты

        Returns:
            Список миксов с треками
        """
        # Анализируем предпочтения
        preferences = await self._analyze_user_preferences(
            user_id, history, likes, top_artists
        )

        # Генерируем миксы
        mixes = []

        # Микс 1: Топ артисты #1-3
        mixes.append(await self._create_mix(
            user_id, preferences, "top_artists_1",
            "Daily Mix 1",
            "Ваши любимые артисты"
        ))

        # Микс 2: Топ артисты #4-6
        mixes.append(await self._create_mix(
            user_id, preferences, "top_artists_2",
            "Daily Mix 2",
            "Ещё больше любимой музыки"
        ))

        # Микс 3: Топ жанры
        mixes.append(await self._create_mix(
            user_id, preferences, "top_genres",
            "Daily Mix 3",
            "Жанры которые вы любите"
        ))

        # Микс 4: Новые открытия
        mixes.append(await self._create_mix(
            user_id, preferences, "discoveries",
            "Daily Mix 4",
            "Новая музыка для вас"
        ))

        # Микс 5: Ностальгия
        mixes.append(await self._create_mix(
            user_id, preferences, "nostalgia",
            "Daily Mix 5",
            "Треки из прошлого"
        ))

        # Микс 6: Свежее
        mixes.append(await self._create_mix(
            user_id, preferences, "fresh",
            "Daily Mix 6",
            "Самые новые релизы"
        ))

        return mixes

    async def _analyze_user_preferences(
        self,
        user_id: str,
        history: List[Dict],
        likes: List[str],
        top_artists: List[str]
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

        # Временные предпочтения
        hour = datetime.now().hour
        time_preference = self._get_time_preference(hour)

        return {
            "top_artists": [a for a, _ in artist_counts.most_common(20)],
            "top_genres": [g for g, _ in genre_counts.most_common(10)],
            "liked_tracks": likes,
            "history": history,
            "time_preference": time_preference,
            "top_artist_ids": top_artists
        }

    def _get_time_preference(self, hour: int) -> str:
        """Определение настроения по времени суток"""
        if 5 <= hour < 10:
            return "morning"  # Энергичное
        elif 10 <= hour < 15:
            return "day"  # Активное
        elif 15 <= hour < 19:
            return "evening"  # Спокойное
        else:
            return "night"  # Расслабленное

    async def _create_mix(
        self,
        user_id: str,
        preferences: Dict,
        mix_type: str,
        name: str,
        description: str
    ) -> Dict:
        """Создание одного микса"""

        # Генерируем seed для воспроизводимости
        date_str = datetime.now().strftime("%Y-%m-%d")
        seed_string = f"{user_id}:{mix_type}:{date_str}"
        seed_hash = hashlib.md5(seed_string.encode()).hexdigest()

        # Выбираем треки на основе типа микса
        tracks = await self._select_tracks_for_mix(
            preferences, mix_type, self.tracks_per_mix, seed_hash
        )

        # Генерируем обложку
        cover_color = self._get_mix_color(mix_type)
        cover = f"https://picsum.photos/seed/{seed_hash}/300/300"

        return {
            "id": f"daily_mix_{mix_type}",
            "name": name,
            "description": description,
            "cover": cover,
            "cover_color": cover_color,
            "tracks": tracks,
            "tracks_count": len(tracks),
            "generated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=1)).isoformat()
        }

    async def _select_tracks_for_mix(
        self,
        preferences: Dict,
        mix_type: str,
        limit: int,
        seed: str
    ) -> List[Dict]:
        """Выбор треков для микса"""

        # В реальности здесь будет логика выбора из Spotify API
        # Для демонстрации - заглушка

        if mix_type == "top_artists_1":
            # Треки от топ-3 артистов
            return await self._get_tracks_from_artists(
                preferences["top_artists"][:3], limit
            )

        elif mix_type == "top_artists_2":
            # Треки от артистов 4-6
            return await self._get_tracks_from_artists(
                preferences["top_artists"][3:6], limit
            )

        elif mix_type == "top_genres":
            # Треки из топ жанров
            return await self._get_tracks_from_genres(
                preferences["top_genres"][:3], limit
            )

        elif mix_type == "discoveries":
            # Новые треки от любимых артистов
            return await self._get_new_tracks_from_artists(
                preferences["top_artists"][:5], limit
            )

        elif mix_type == "nostalgia":
            # Старые треки которые давно не слушал
            return await self._get_old_tracks(
                preferences["history"], limit
            )

        elif mix_type == "fresh":
            # Новые релизы
            return await self._get_fresh_releases(limit)

        return []

    async def _get_tracks_from_artists(
        self,
        artists: List[str],
        limit: int
    ) -> List[Dict]:
        """Получение треков от артистов"""
        # Заглушка - в реальности Spotify API
        return self._generate_mock_tracks(artists, limit)

    async def _get_tracks_from_genres(
        self,
        genres: List[str],
        limit: int
    ) -> List[Dict]:
        """Получение треков по жанрам"""
        # Заглушка - в реальности Spotify API
        return self._generate_mock_tracks(genres, limit)

    async def _get_new_tracks_from_artists(
        self,
        artists: List[str],
        limit: int
    ) -> List[Dict]:
        """Новые треки от артистов"""
        return self._generate_mock_tracks(artists, limit, new=True)

    async def _get_old_tracks(
        self,
        history: List[Dict],
        limit: int
    ) -> List[Dict]:
        """Старые треки"""
        return self._generate_mock_tracks(["nostalgia"], limit)

    async def _get_fresh_releases(
        self,
        limit: int
    ) -> List[Dict]:
        """Новые релизы"""
        return self._generate_mock_tracks(["fresh"], limit, new=True)

    def _generate_mock_tracks(
        self,
        seeds: List[str],
        limit: int,
        new: bool = False
    ) -> List[Dict]:
        """Генерация mock треков"""
        tracks = []
        for i in range(limit):
            seed = seeds[i % len(seeds)] if seeds else "unknown"
            tracks.append({
                "id": f"track_{seed}_{i}",
                "title": f"{seed.title()} Track {i+1}",
                "artist": f"{seed.title()} Artist",
                "duration": 180 + (i * 10) % 120,
                "cover": f"https://picsum.photos/seed/{seed}{i}/300/300",
                "is_new": new
            })
        return tracks

    def _get_mix_color(self, mix_type: str) -> str:
        """Цвет обложки микса"""
        colors = {
            "top_artists_1": "#1DB954",  # Spotify green
            "top_artists_2": "#E91429",  # Red
            "top_genres": "#DC148C",     # Pink
            "discoveries": "#0D73EC",    # Blue
            "nostalgia": "#8C67AC",      # Purple
            "fresh": "#BC5900",          # Orange
        }
        return colors.get(mix_type, "#1DB954")


# Глобальный экземпляр
daily_mixes_service = DailyMixesService()
