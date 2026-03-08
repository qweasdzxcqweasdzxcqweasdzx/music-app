"""
Smart Music Mixer Service

Умный миксер для комбинирования музыки из разных источников:
- Локальная коллекция (Navidrome)
- SoundCloud - основной источник
- VK Music (резерв)
- AI генерация

Алгоритм миксера:
1. Анализ предпочтений пользователя
2. Определение лучшего источника для каждого трека
3. Создание бесконечного радио
4. Бесшовное переключение между источниками
"""

import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import Counter
from models import Track
from config import settings


class SmartMixer:
    """
    Умный миксер для создания персонализированных плейлистов
    из разных источников музыки
    """

    def __init__(self):
        self._source_weights: Dict[str, float] = {
            "navidrome": 1.0,    # Приоритет локальной коллекции
            "soundcloud": 0.9,   # SoundCloud основной источник
            "ai": 0.3            # AI для уникального контента
        }

    async def create_smart_mix(
        self,
        user_id: str,
        history: List[Dict],
        likes: List[str],
        top_artists: List[str],
        limit: int = 50,
        sources: Optional[List[str]] = None
    ) -> List[Track]:
        """
        Создание умного микса на основе предпочтений

        Args:
            user_id: ID пользователя
            history: История прослушиваний
            likes: Список лайкнутых треков
            top_artists: Топ артистов пользователя
            limit: Количество треков в миксе
            sources: Предпочтительные источники

        Returns:
            Список треков для микса
        """
        from services.music_source_base import source_manager
        from services.soundcloud_service import soundcloud_service
        from services.navidrome_service import navidrome_service
        from services.ai_music_service import ai_music_service

        if sources is None:
            sources = source_manager.get_available_sources()

        # Анализ предпочтений
        preferences = await self._analyze_preferences(history, likes, top_artists)

        # Генерация seed для рекомендаций
        seeds = self._generate_seeds(preferences)

        # Получение треков из разных источников
        tracks_pool = []

        # 1. Треки из SoundCloud (основной источник)
        if "soundcloud" in sources and soundcloud_service.is_authenticated:
            # Поиск по топ жанрам
            if seeds.get("genres"):
                sc_query = " ".join(seeds["genres"][:2])
                sc_results = await soundcloud_service.search(sc_query, limit=limit // 2)
                for track in sc_results.get("tracks", []):
                    tracks_pool.append((track, "soundcloud", 0.9))

        # 2. Треки из Navidrome (локальная коллекция)
        if "navidrome" in sources and navidrome_service.is_connected:
            # Поиск по топ артистам
            for artist_name in top_artists[:5]:
                search_results = await navidrome_service.search3(artist_name, limit=5)
                for track in search_results.get("tracks", []):
                    tracks_pool.append((track, "navidrome", 1.0))

        # 3. AI генерация (для уникальности)
        if "ai" in sources and settings.MIXER_ENABLE_AI:
            # Генерация на основе предпочтений
            ai_prompt = self._generate_ai_prompt(preferences)
            # AI генерация асинхронная, не блокируем микс
            # tracks можно добавить позже через task queue

        # Сортировка и выбор треков
        # Приоритет: Navidrome > SoundCloud > AI
        tracks_pool.sort(key=lambda x: x[2], reverse=True)

        # Удаление дубликатов
        seen_titles = set()
        unique_tracks = []

        for track, source, weight in tracks_pool:
            key = f"{track.title.lower()}_{track.artist.lower()}"
            if key not in seen_titles:
                seen_titles.add(key)
                unique_tracks.append(track)

        # Перемешивание с учетом весов
        mixed_tracks = self._weighted_shuffle(unique_tracks, limit)

        return mixed_tracks[:limit]

    async def _analyze_preferences(
        self,
        history: List[Dict],
        likes: List[str],
        top_artists: List[str]
    ) -> Dict:
        """Анализ музыкальных предпочтений пользователя"""
        # Извлечение жанров из истории
        genres = []
        artists = []

        for item in history[-100:]:  # Последние 100 треков
            if isinstance(item.get("track"), dict):
                track = item["track"]
                genres.extend(track.get("genres", []))
                if track.get("artist"):
                    artists.append(track["artist"])
            elif isinstance(item, dict):
                # Прямые данные трека
                genres.extend(item.get("genres", []))
                if item.get("artist"):
                    artists.append(item["artist"])

        # Топ жанров
        genre_counts = Counter(genres)
        top_genres = [g for g, _ in genre_counts.most_common(5)]

        # Топ артистов из истории
        artist_counts = Counter(artists)
        history_top_artists = [a for a, _ in artist_counts.most_common(10)]

        # Объединение с явным списком
        all_top_artists = list(set(top_artists + history_top_artists[:5]))

        return {
            "top_genres": top_genres,
            "top_artists": all_top_artists[:10],
            "liked_count": len(likes),
            "history_count": len(history)
        }

    def _generate_seeds(self, preferences: Dict) -> Dict:
        """Генерация seed для рекомендаций"""
        return {
            "artists": preferences.get("top_artists", [])[:5],
            "genres": preferences.get("top_genres", [])[:5],
            "tracks": []  # Можно добавить из likes
        }

    def _generate_ai_prompt(self, preferences: Dict) -> str:
        """Генерация промпта для AI музыки"""
        genres = preferences.get("top_genres", [])
        artists = preferences.get("top_artists", [])

        prompt_parts = []

        if genres:
            prompt_parts.append(f"Genre: {', '.join(genres[:3])}")

        if artists:
            prompt_parts.append(f"Similar to: {', '.join(artists[:3])}")

        prompt_parts.append("Instrumental background music")
        prompt_parts.append("High quality production")

        return ". ".join(prompt_parts)

    def _weighted_shuffle(self, tracks: List[Track], limit: int) -> List[Track]:
        """
        Перемешивание треков с весами

        Треки из приоритетных источников чаще попадают в начало
        """
        if not tracks:
            return []

        # Назначение весов источникам
        source_weights = {
            "navidrome": 3,
            "soundcloud": 2,
            "ai": 1
        }

        weighted_tracks = []
        for track in tracks:
            weight = source_weights.get(track.source, 1)
            # Добавляем трек несколько раз в пул для взвешенного выбора
            weighted_tracks.extend([track] * weight)

        # Перемешивание
        random.shuffle(weighted_tracks)

        # Выбор уникальных треков
        seen_ids = set()
        result = []

        for track in weighted_tracks:
            track_key = f"{track.source}:{track.id}"
            if track_key not in seen_ids:
                seen_ids.add(track_key)
                result.append(track)

            if len(result) >= limit:
                break

        return result

    async def create_infinite_radio(
        self,
        seed_track: Track,
        limit: int = 50,
        sources: Optional[List[str]] = None
    ) -> List[Track]:
        """
        Создание бесконечного радио на основе трека

        Args:
            seed_track: Трек для начала радио
            limit: Количество треков
            sources: Источники

        Returns:
            Список треков для радио
        """
        from services.music_source_base import source_manager
        from services.soundcloud_service import soundcloud_service

        if sources is None:
            sources = source_manager.get_available_sources()

        tracks_pool = []

        # 1. Похожие треки из SoundCloud
        if "soundcloud" in sources and soundcloud_service.is_authenticated:
            # Поиск по жанру трека
            if seed_track.genre:
                similar = await soundcloud_service.search(seed_track.genre, limit=limit // 2)
                tracks_pool.extend(similar.get("tracks", []))

        # 2. Поиск по названию и артисту в других источниках
        search_query = f"{seed_track.artist} {seed_track.title}"

        for source_name in sources:
            if source_name == "soundcloud":
                continue

            source = source_manager.get_source(source_name)
            if source and source.is_available:
                results = await source.search(search_query, limit=limit // 4)
                tracks_pool.extend(results.get("tracks", []))

        # Удаление дубликатов и перемешивание
        seen_titles = {f"{seed_track.title.lower()}_{seed_track.artist.lower()}"}
        unique_tracks = [seed_track]  # Начинаем с seed трека

        for track in tracks_pool:
            key = f"{track.title.lower()}_{track.artist.lower()}"
            if key not in seen_titles:
                seen_titles.add(key)
                unique_tracks.append(track)

        # Перемешивание (кроме первого трека)
        if len(unique_tracks) > 1:
            rest = unique_tracks[1:]
            random.shuffle(rest)
            unique_tracks = [unique_tracks[0]] + rest

        return unique_tracks[:limit]

    async def create_mood_mix(
        self,
        mood: str,
        limit: int = 30,
        sources: Optional[List[str]] = None
    ) -> List[Track]:
        """
        Создание микса по настроению

        Args:
            mood: Настроение (happy, sad, energetic, chill, focus)
            limit: Количество треков
            sources: Источники

        Returns:
            Список треков
        """
        from services.soundcloud_service import soundcloud_service

        # Жанры для разных настроений
        mood_genres = {
            "happy": "pop dance happy",
            "sad": "acoustic indie folk",
            "energetic": "edm dance electro",
            "chill": "chillout downtempo ambient",
            "focus": "classical study beats",
        }

        genre_query = mood_genres.get(mood, "chill")
        result = await soundcloud_service.search(genre_query, limit=limit)
        return result.get("tracks", [])[:limit]

    async def create_genre_mix(
        self,
        genre: str,
        limit: int = 40,
        sources: Optional[List[str]] = None
    ) -> List[Track]:
        """Создание микса по жанру"""
        from services.music_source_base import source_manager

        if sources is None:
            sources = source_manager.get_available_sources()

        tracks_pool = []

        # Поиск по всем источникам
        for source_name in sources:
            source = source_manager.get_source(source_name)
            if source and source.is_available:
                try:
                    results = await source.get_tracks_by_genre(genre, limit // len(sources))
                    tracks_pool.extend(results)
                except Exception:
                    pass

        # Удаление дубликатов
        seen_titles = set()
        unique_tracks = []

        for track in tracks_pool:
            key = f"{track.source}:{track.title.lower()}_{track.artist.lower()}"
            if key not in seen_titles:
                seen_titles.add(key)
                unique_tracks.append(track)

        random.shuffle(unique_tracks)
        return unique_tracks[:limit]


# Глобальный экземпляр
smart_mixer = SmartMixer()
