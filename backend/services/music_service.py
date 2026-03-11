"""
Music Service - Фасад для работы с музыкальными источниками

Источники:
1. SoundCloud - основной источник
2. VK Music - резервный источник
3. YouTube - поиск оригинальных версий
4. Navidrome - личная коллекция

Система анти-цензуры v2.0:
- ML-классификатор на основе текста
- Анализ акустических признаков
- Интеграция с внешними API
- Кэширование результатов
- Сообщество-маркеры
"""

import re
import asyncio
from typing import List, Optional, Dict
from models_main import Track
from services.soundcloud_service import soundcloud_service
from services.vk_service import VKMusicService
from services.youtube_service import YouTubeMusicService
from services.censorship_service import (
    censorship_service,
    CensorshipResult,
    CensorshipType
)
from config import settings


class CensorshipDetector:
    """Детектор цензурированных версий треков"""

    # Маркеры чистой/цензурированной версии
    CLEAN_MARKERS = [
        'clean', 'radio', 'censored', 'edited', 'censor',
        'радио', 'цензура', 'версия', 'edit version',
        'album version', 'single version'
    ]

    # Маркеры оригинальной/explicit версии
    EXPLICIT_MARKERS = [
        'explicit', 'original', 'uncensored', "director's cut",
        'extended', 'album', 'deluxe', 'нецензурно', 'оригинал'
    ]

    # Минимальная длительность для нормального трека (секунды)
    MIN_DURATION = 120  # 2 минуты

    # Максимальная разница в длительности для сравнения версий
    MAX_DURATION_DIFF = 30  # 30 секунд

    @classmethod
    def is_censored(cls, track: Track) -> bool:
        """
        Проверка трека на цензуру

        Args:
            track: Трек для проверки

        Returns:
            True если трек цензурирован
        """
        title_lower = track.title.lower()

        # Проверка по маркерам чистой версии
        for marker in cls.CLEAN_MARKERS:
            if marker in title_lower:
                return True

        # Проверка по длительности (слишком короткие треки подозрительны)
        if track.duration < cls.MIN_DURATION:
            # Но не считаем цензурой если это не явный маркер
            if track.duration < 60:  # Меньше 1 минуты - точно подозрительно
                return True

        # Проверка флагов
        if hasattr(track, 'is_censored') and track.is_censored:
            return True

        return False

    @classmethod
    def is_explicit(cls, track: Track) -> bool:
        """
        Проверка на explicit контент

        Args:
            track: Трек для проверки

        Returns:
            True если трек содержит explicit контент
        """
        title_lower = track.title.lower()

        # Проверка по маркерам
        for marker in cls.EXPLICIT_MARKERS:
            if marker in title_lower:
                return True

        # Проверка флага
        if hasattr(track, 'is_explicit') and track.is_explicit:
            return True

        return False

    @classmethod
    def compare_versions(cls, original: Track, clean: Track) -> float:
        """
        Сравнение двух версий трека

        Args:
            original: Оригинальная версия
            clean: Чистая версия

        Returns:
            Коэффициент схожести (0.0 - 1.0)
        """
        score = 0.0

        # Сравнение названий (нечеткое)
        title_similarity = cls._string_similarity(
            original.title.lower(),
            clean.title.lower()
        )
        score += title_similarity * 0.5

        # Сравнение артистов
        if original.artist.lower() == clean.artist.lower():
            score += 0.3

        # Сравнение длительности
        duration_diff = abs(original.duration - clean.duration)
        if duration_diff < cls.MAX_DURATION_DIFF:
            score += 0.2 * (1 - duration_diff / cls.MAX_DURATION_DIFF)

        return score

    @classmethod
    def _string_similarity(cls, s1: str, s2: str) -> float:
        """Вычисление схожести строк (упрощённый Levenshtein)"""
        # Удаление лишних символов
        s1 = re.sub(r'[^\w\s]', '', s1)
        s2 = re.sub(r'[^\w\s]', '', s2)

        # Разбиение на слова
        words1 = set(s1.split())
        words2 = set(s2.split())

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0


class MusicService:
    """Основной музыкальный сервис (фасад)"""

    def __init__(self):
        self.soundcloud = soundcloud_service
        self.vk = VKMusicService()
        self.youtube = YouTubeMusicService(proxy=settings.PROXY_URL)
        self.censorship_service = censorship_service

        # Настройки
        self.prefer_original = settings.PREFER_ORIGINAL
        self.auto_replace_censored = settings.AUTO_REPLACE_CENSORED

    async def search(self, query: str, limit: int = 20, source: str = "all") -> List[Track]:
        """
        Поиск треков

        Args:
            query: Поисковый запрос
            limit: Количество результатов
            source: Источник (soundcloud, vk, youtube, all)

        Returns:
            Список треков
        """
        if source == "soundcloud":
            tracks = await self.soundcloud.search(query, limit)
            tracks = tracks.get("tracks", [])
        elif source == "vk":
            tracks = await self.vk.search(query, limit)
        elif source == "youtube":
            tracks = await self.youtube.search(query, limit)
        else:
            # Поиск во всех источниках с объединением
            results = await asyncio.gather(
                self.soundcloud.search(query, limit // 2),
                self.vk.search(query, limit // 2),
                return_exceptions=True
            )

            # Обработка ошибок
            tracks = []
            for result in results:
                if isinstance(result, Exception):
                    continue
                if isinstance(result, dict):
                    tracks.extend(result.get("tracks", []))
                elif isinstance(result, list):
                    tracks.extend(result)

        # Применение анти-цензуры
        if self.auto_replace_censored:
            tracks = await self._apply_anti_censorship(tracks)

        return tracks[:limit]

    async def _apply_anti_censorship(self, tracks: List[Track]) -> List[Track]:
        """
        Применение системы анти-цензуры к списку треков

        Args:
            tracks: Список треков

        Returns:
            Список с заменёнными цензурированными версиями
        """
        result = []

        for track in tracks:
            # Проверка на цензуру через новый сервис
            censorship_result = await self.censorship_service.check(track)

            if censorship_result.is_censored and self.prefer_original:
                # Поиск оригинальной версии
                original = await self.get_original_version(track, censorship_result)

                if original:
                    # Замена на оригинал
                    result.append(original)
                else:
                    # Оригинал не найден, добавляем как есть с флагом
                    track.is_censored = True
                    track.censorship_type = censorship_result.censorship_type.value
                    result.append(track)
            else:
                # Добавляем информацию о цензуре в трек
                if censorship_result.markers_found:
                    track.is_explicit = censorship_result.censorship_type == CensorshipType.NONE
                    track.censorship_type = censorship_result.censorship_type.value
                result.append(track)

        return result

    async def get_original_version(
        self,
        censored_track: Track,
        censorship_result: Optional[CensorshipResult] = None
    ) -> Optional[Track]:
        """
        Поиск оригинальной версии для цензурированного трека

        Алгоритм:
        1. Поиск кандидатов на YouTube и SoundCloud
        2. Фильтрация по длительности (оригинал длиннее)
        3. Сравнение акустических отпечатков
        4. Возврат наиболее подходящего

        Args:
            censored_track: Цензурированный трек
            censorship_result: Результат проверки на цензуру

        Returns:
            Оригинальный трек или None
        """
        query = f"{censored_track.artist} {censored_track.title}"

        # Поиск кандидатов на YouTube и SoundCloud
        candidates = []

        # YouTube поиск
        yt_tracks = await self.youtube.search(f"{query} original explicit", limit=5)
        candidates.extend(yt_tracks)

        # SoundCloud поиск
        sc_result = await self.soundcloud.search(f"{query} original version", limit=5)
        candidates.extend(sc_result.get("tracks", []))

        if not candidates:
            return None

        # Поиск лучшей версии через censorship_service
        original = await self.censorship_service.find_original(
            censored_track,
            candidates
        )

        return original

    async def get_track(self, track_id: str, source: str = "vk") -> Optional[Track]:
        """
        Получение трека по ID

        Args:
            track_id: ID трека
            source: Источник

        Returns:
            Трек или None
        """
        # Заглушка - в реальности нужно хранить треки в БД
        return Track(
            id=track_id,
            title="Track Title",
            artist="Artist Name",
            duration=180,
            stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            cover="https://picsum.photos/seed/track/300/300",
            source=source
        )

    async def get_track_stream_url(self, track: Track) -> Optional[str]:
        """
        Получение прямого URL потока для трека

        Args:
            track: Трек

        Returns:
            URL потока или None
        """
        if track.source == "vk":
            return track.stream_url  # VK уже даёт прямой URL
        elif track.source == "youtube":
            return await self.youtube.get_track_stream(track.id or track.stream_url)
        else:
            return track.stream_url

    async def check_censorship(self, track: Track) -> CensorshipResult:
        """
        Проверка трека на цензуру (расширенная)

        Args:
            track: Трек для проверки

        Returns:
            Результат проверки с деталями
        """
        return await self.censorship_service.check(track)

    async def report_censorship(
        self,
        track_id: str,
        user_id: str,
        is_censored: bool,
        original_track_id: Optional[str] = None
    ):
        """
        Добавление пользовательского отчёта о цензуре

        Args:
            track_id: ID трека
            user_id: ID пользователя
            is_censored: Является ли цензурой
            original_track_id: ID оригинальной версии (если есть)
        """
        await self.censorship_service.report(
            track_id,
            user_id,
            is_censored,
            original_track_id
        )

    async def get_artist(self, artist_id: str) -> Optional[Dict]:
        """Получение информации об артисте"""
        return await self.vk.get_artist(artist_id)

    async def get_artist_tracks(self, artist_id: str, limit: int = 20) -> List[Track]:
        """Получение треков артиста"""
        return await self.vk.get_artist_tracks(artist_id, limit)

    async def get_top_tracks(self, limit: int = 20, genre: Optional[str] = None) -> List[Track]:
        """
        Получение популярных треков

        Args:
            limit: Количество результатов
            genre: Жанр (опционально)

        Returns:
            Список популярных треков
        """
        # TODO: Реализовать через БД (сортировка по play_count)
        # Временно заглушка
        return await self.search("top hits", limit)

    async def get_new_releases(self, limit: int = 20) -> List[Track]:
        """
        Получение новых релизов

        Args:
            limit: Количество результатов

        Returns:
            Список новых треков
        """
        # TODO: Реализовать через БД (сортировка по created_at)
        # Временно заглушка
        return await self.search("new music 2024", limit)

    async def get_tracks_by_genre(self, genre: str, limit: int = 20) -> List[Track]:
        """
        Поиск треков по жанру

        Args:
            genre: Жанр
            limit: Количество результатов

        Returns:
            Список треков
        """
        # TODO: Реализовать через БД с фильтрацией по жанру
        # Временно заглушка
        return await self.search(genre, limit)


# Глобальный экземпляр
music_service = MusicService()
