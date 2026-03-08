"""
Release Radar Service

Еженедельные новые релизы от любимых артистов.
Обновляется каждую пятницу.

Алгоритм:
1. 60% - Новые релизы от артистов которые слушал за последние 3 месяца
2. 25% - Новые релизы от артистов которые лайкал
3. 15% - Новые релизы от похожих артистов

Обновляется: Каждую пятницу в 00:00
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter


class ReleaseRadarService:
    """Сервис генерации Release Radar"""

    def __init__(self):
        self.tracks_count = 30  # Треков в плейлисте
        self.update_day = "Friday"  # День обновления
        self.lookback_months = 3  # Период анализа

    async def generate_release_radar(
        self,
        user_id: str,
        history: List[Dict],
        likes: List[str],
        top_artists: List[str]
    ) -> Dict:
        """
        Генерация Release Radar плейлиста

        Args:
            user_id: ID пользователя
            history: История прослушиваний
            likes: Любимые треки
            top_artists: Топ артисты

        Returns:
            Плейлист с новыми релизами
        """
        # Определяем дату следующего обновления
        next_update = self._get_next_friday()
        
        # Генерируем уникальный ID
        week_str = datetime.now().strftime("%Y-W%W")
        playlist_id = f"release_radar_{user_id}_{week_str}"

        # Фильтруем историю за последние 3 месяца
        cutoff_date = datetime.now() - timedelta(days=self.lookback_months * 30)
        recent_history = [
            h for h in history
            if datetime.fromisoformat(h.get('played_at', '2000-01-01')) > cutoff_date
        ]

        # Анализируем предпочтения
        preferences = await self._analyze_preferences(
            recent_history, likes, top_artists
        )

        # Генерируем треки по категориям
        tracks = []
        
        # 60% - Новые релизы от артистов которые слушал (18 треков)
        from_recent = await self._get_new_releases_from_artists(
            preferences["recent_artists"], 18
        )
        tracks.extend(from_recent)

        # 25% - Новые релизы от лайкнутых артистов (7 треков)
        from_likes = await self._get_new_releases_from_liked_artists(
            preferences["liked_artists"], 7
        )
        tracks.extend(from_likes)

        # 15% - Новые релизы от похожих артистов (5 треков)
        from_similar = await self._get_new_releases_from_similar(
            preferences["recent_artists"][:5], 5
        )
        tracks.extend(from_similar)

        # Перемешиваем
        import random
        random.shuffle(tracks)

        # Генерируем обложку
        cover_color = self._get_radar_color()
        cover = f"https://picsum.photos/seed/{playlist_id}/300/300"

        return {
            "id": playlist_id,
            "name": "Release Radar",
            "description": f"Новые релизы для вас • {self.tracks_count} треков",
            "cover": cover,
            "cover_color": cover_color,
            "tracks": tracks,
            "tracks_count": len(tracks),
            "generated_at": datetime.now().isoformat(),
            "next_update": next_update.isoformat(),
            "is_weekly": True,
            "update_day": "Friday"
        }

    def _get_next_friday(self) -> datetime:
        """Получение даты следующей пятницы"""
        today = datetime.now()
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:  # Если сегодня пятница
            days_until_friday = 7
        next_friday = today + timedelta(days=days_until_friday)
        return next_friday.replace(hour=0, minute=0, second=0, microsecond=0)

    async def _analyze_preferences(
        self,
        history: List[Dict],
        likes: List[str],
        top_artists: List[str]
    ) -> Dict:
        """Анализ предпочтений пользователя"""
        
        # Артисты из недавней истории
        recent_artist_counts = Counter(
            h.get('artist_id') or h.get('artist')
            for h in history
            if h.get('artist_id') or h.get('artist')
        )

        # Артисты из лайков (нужно получить из треков)
        liked_artists = top_artists[:10]  # Упрощённо

        return {
            "recent_artists": [a for a, _ in recent_artist_counts.most_common(20)],
            "liked_artists": liked_artists,
            "history": history
        }

    async def _get_new_releases_from_artists(
        self,
        artists: List[str],
        limit: int
    ) -> List[Dict]:
        """Новые релизы от артистов которые слушал"""
        # В реальности: Spotify API - get new releases by artist IDs
        return self._generate_mock_tracks(artists, limit, new=True)

    async def _get_new_releases_from_liked_artists(
        self,
        artists: List[str],
        limit: int
    ) -> List[Dict]:
        """Новые релизы от лайкнутых артистов"""
        return self._generate_mock_tracks(artists, limit, new=True)

    async def _get_new_releases_from_similar(
        self,
        artists: List[str],
        limit: int
    ) -> List[Dict]:
        """Новые релизы от похожих артистов"""
        # В реальности: Spotify API - get similar artists then their new releases
        return self._generate_mock_tracks(["similar"] + artists, limit, new=True)

    def _generate_mock_tracks(
        self,
        artists: List[str],
        limit: int,
        new: bool = False
    ) -> List[Dict]:
        """Генерация mock треков"""
        tracks = []
        for i in range(limit):
            artist = artists[i % len(artists)] if artists else "unknown"
            tracks.append({
                "id": f"release_{artist}_{i}",
                "title": f"{artist} New Release {i+1}",
                "artist": f"{artist}",
                "duration": 180 + (i * 10) % 120,
                "cover": f"https://picsum.photos/seed/release{artist}{i}/300/300",
                "is_new": new,
                "release_date": datetime.now().strftime("%Y-%m-%d")
            })
        return tracks

    def _get_radar_color(self) -> str:
        """Цвет обложки Release Radar"""
        # Фирменный цвет Release Radar
        return "#8C67AC"  # Purple

    def should_update(self, last_generated: datetime) -> bool:
        """Проверка нужно ли обновлять плейлист"""
        today = datetime.now()
        is_friday = today.weekday() == 4  # 4 = Friday
        
        if not is_friday:
            return False
            
        # Если последний раз генерировали не на этой неделе
        last_week = last_generated.isocalendar()[1]
        current_week = today.isocalendar()[1]
        
        return current_week > last_week


# Глобальный экземпляр
release_radar_service = ReleaseRadarService()
