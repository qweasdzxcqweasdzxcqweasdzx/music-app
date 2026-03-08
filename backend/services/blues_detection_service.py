"""
Blues/Censorship Detection Service

Сервис для распознавания цензурированных (заблюренных) версий песен
и поиска оригинальных (explicit) версий на разных площадках.

Проблема:
- В России ввели цензуру на музыкальных платформах
- Слова в песнях "блюрят" (заменяют, вырезают, заглушают)
- Названия треков могут отличаться на разных площадках

Решение:
- Распознавание признаков цензуры (audio analysis + metadata)
- Поиск оригинальных версий через fuzzy matching названий
- Мульти-платформенный поиск (YouTube, SoundCloud, VK, etc.)
"""

import re
import aiohttp
from typing import List, Optional, Dict, Tuple
from difflib import SequenceMatcher
from collections import Counter

from models import Track


class BluesDetectionService:
    """
    Сервис распознавания цензурированных треков и поиска оригиналов
    """

    # Маркеры цензурной версии в названии
    CENSOR_MARKERS = [
        "clean", "radio edit", "censored", "edited", "sanitized",
        "версия", "радио версия", "цензурная", "для эфира",
        "no explicit", "family friendly", "pg version"
    ]

    # Маркеры оригинальной (explicit) версии
    EXPLICIT_MARKERS = [
        "explicit", "original", "uncensored", "dirty", "uncut",
        "оригинал", "нецензурная", "полная версия", "full version",
        "extended", "album version", "lp version"
    ]

    # Слова, которые часто цензурят (признак explicit контента)
    # Используем паттерны для распознавания
    PROFANITY_PATTERNS = [
        r'\b(f|ф)(u|у)(c|к)\s*(k|к)?\b',
        r'\b(s|ш)(i|и)(t|т)\b',
        r'\b(h|х)(e|е)(l|л)(l|л)\b',
        r'\b(d|д)(a|а)(m|м)(n|н)\b',
        r'\b(b|б)(i|и)(t|т)(c|ц)(h|ч)\b',
        r'\b(a|а)(s|с)(s|с)\b',
        # Русские паттерны (обобщенные)
        r'\b[а-я]{3,7}\*[а-я]*\b',  # Звездочки в словах
        r'\b[а-я]*\[[а-я]+\]\b',    # Квадратные скобки
    ]

    # Паттерны для "чистки" названий
    CLEANUP_PATTERNS = [
        r'\s*\([^)]*clean[^)]*\)',
        r'\s*\([^)]*radio[^)]*\)',
        r'\s*\([^)]*edit[^)]*\)',
        r'\s*\[[^\]]*clean[^\]]*\]',
        r'\s*\[[^\]]*radio[^\]]*\]',
        r'\s*\[[^\]]*edit[^\]]*\]',
        r'\s*-\s*Clean Version',
        r'\s*-\s*Radio Edit',
        r'\s*-\s*Edited',
    ]

    # Сервисы для поиска
    SEARCH_SERVICES = ['youtube', 'soundcloud', 'vk', 'navidrome']

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение HTTP сессии"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Закрытие сессии"""
        if self.session and not self.session.closed:
            await self.session.close()

    # ==================== Распознавание цензуры ====================

    def is_censored(self, track: Track) -> bool:
        """
        Проверка трека на признаки цензуры

        Args:
            track: Трек для проверки

        Returns:
            True если трек цензурирован
        """
        title_lower = track.title.lower()

        # Проверка по маркерам чистой версии
        for marker in self.CENSOR_MARKERS:
            if marker in title_lower:
                return True

        # Проверка флага explicit (если False - возможно цензура)
        if hasattr(track, 'is_explicit') and not track.is_explicit:
            # Дополнительная проверка на "подозрительные" названия
            if self._has_censorship_indicators(title_lower):
                return True

        # Проверка на замененные символы (звездочки, скобки)
        if self._has_masked_words(track.title):
            return True

        return False

    def _has_censorship_indicators(self, title: str) -> bool:
        """Проверка на индикаторы цензуры в названии"""
        indicators = [
            '(clean)', '[clean]',
            '(radio)', '[radio]',
            '(edit)', '[edit]',
            '(edited)',
            'for radio', 'for tv',
            'версия для', 'для эфира'
        ]
        return any(ind in title for ind in indicators)

    def _has_masked_words(self, title: str) -> bool:
        """Проверка на замаскированные слова (звездочки, скобки)"""
        # Звездочки вместо букв
        if '*' in title:
            return True
        # Квадратные скобки с текстом внутри
        if re.search(r'\[[а-яa-z]+\]', title, re.IGNORECASE):
            return True
        # Многоточие вместо слова
        if re.search(r'\b\w+\.{3,}\b', title):
            return True
        return False

    def is_explicit_version(self, track: Track) -> bool:
        """
        Проверка на оригинальную (explicit) версию

        Args:
            track: Трек для проверки

        Returns:
            True если это оригинальная версия
        """
        title_lower = track.title.lower()

        # Проверка по маркерам explicit версии
        for marker in self.EXPLICIT_MARKERS:
            if marker in title_lower:
                return True

        # Проверка флага explicit
        if hasattr(track, 'is_explicit') and track.is_explicit:
            return True

        return False

    def get_version_type(self, track: Track) -> str:
        """
        Определение типа версии трека

        Args:
            track: Трек для проверки

        Returns:
            "explicit", "clean", "unknown"
        """
        if self.is_explicit_version(track):
            return "explicit"
        elif self.is_censored(track):
            return "clean"
        else:
            return "unknown"

    # ==================== Fuzzy Matching ====================

    def normalize_title(self, title: str) -> str:
        """
        Нормализация названия для сравнения

        Удаляет маркеры версий, спецсимволы, приводит к нижнему регистру
        """
        normalized = title.lower()

        # Удаление маркеров версий
        for pattern in self.CLEANUP_PATTERNS:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)

        # Удаление спецсимволов
        normalized = re.sub(r'[^\w\sа-яё]', ' ', normalized)

        # Удаление лишних пробелов
        normalized = ' '.join(normalized.split())

        return normalized.strip()

    def similarity_ratio(self, title1: str, title2: str) -> float:
        """
        Вычисление коэффициента схожести названий

        Args:
            title1: Первое название
            title2: Второе название

        Returns:
            Коэффициент от 0 до 1
        """
        norm1 = self.normalize_title(title1)
        norm2 = self.normalize_title(title2)

        # SequenceMatcher для fuzzy matching
        ratio = SequenceMatcher(None, norm1, norm2).ratio()

        # Дополнительная проверка по словам
        words1 = set(norm1.split())
        words2 = set(norm2.split())

        if words1 and words2:
            # Процент общих слов
            common_words = len(words1 & words2)
            total_words = len(words1 | words2)
            word_ratio = common_words / total_words if total_words > 0 else 0

            # Комбинируем оба коэффициента
            ratio = (ratio + word_ratio) / 2

        return ratio

    def find_best_match(
        self,
        query_track: Track,
        candidates: List[Track],
        min_similarity: float = 0.6
    ) -> Optional[Track]:
        """
        Поиск лучшего совпадения среди кандидатов

        Args:
            query_track: Исходный трек
            candidates: Кандидаты для сравнения
            min_similarity: Минимальный порог схожести

        Returns:
            Лучшее совпадение или None
        """
        best_match = None
        best_score = min_similarity

        for candidate in candidates:
            # Схожесть названий
            title_score = self.similarity_ratio(
                query_track.title,
                candidate.title
            )

            # Схожесть артистов
            artist_score = self.similarity_ratio(
                query_track.artist,
                candidate.artist
            )

            # Комбинированный скор
            combined_score = (title_score * 0.6) + (artist_score * 0.4)

            if combined_score > best_score:
                best_score = combined_score
                best_match = candidate

        return best_match

    # ==================== Генерация поисковых запросов ====================

    def generate_search_queries(
        self,
        track: Track,
        prefer_explicit: bool = True
    ) -> List[str]:
        """
        Генерация вариантов поисковых запросов для поиска оригинала

        Args:
            track: Исходный трек
            prefer_explicit: Приоритет explicit версий

        Returns:
            Список поисковых запросов
        """
        queries = []
        title = track.title
        artist = track.artist

        # Базовый запрос
        queries.append(f"{artist} {title}")

        # С очисткой от маркеров цензуры
        clean_title = self.normalize_title(title)
        queries.append(f"{artist} {clean_title}")

        if prefer_explicit:
            # С добавлением explicit маркеров
            queries.append(f"{artist} {title} explicit")
            queries.append(f"{artist} {title} original")
            queries.append(f"{artist} {title} uncensored")
            queries.append(f"{artist} {title} uncut")
            queries.append(f"{artist} {clean_title} explicit")

        # С不同类型 версий
        queries.append(f"{artist} {title} album version")
        queries.append(f"{artist} {title} full version")

        # Русские варианты
        queries.append(f"{artist} {title} оригинал")
        queries.append(f"{artist} {title} нецензурная")
        queries.append(f"{artist} {title} полная версия")

        # Удаление дубликатов
        return list(dict.fromkeys(queries))

    # ==================== Мульти-платформенный поиск ====================

    async def search_original_across_platforms(
        self,
        censored_track: Track,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, List[Track]]:
        """
        Поиск оригинальной версии на разных платформах

        Args:
            censored_track: Цензурированный трек
            platforms: Список платформ для поиска

        Returns:
            Dict с платформами и найденными треками
        """
        if platforms is None:
            platforms = self.SEARCH_SERVICES

        results = {}
        search_queries = self.generate_search_queries(censored_track)

        # Импортируем сервисы
        from services.youtube_service import YouTubeMusicService
        from services.soundcloud_service import soundcloud_service
        from services.vk_service import VKMusicService
        from services.navidrome_service import navidrome_service

        for platform in platforms:
            platform_results = []

            try:
                if platform == 'youtube':
                    yt_service = YouTubeMusicService(proxy=settings.PROXY_URL)
                    for query in search_queries[:3]:  # Ограничиваем количество запросов
                        tracks = await yt_service.search(query, limit=5)
                        platform_results.extend(tracks)

                elif platform == 'soundcloud':
                    for query in search_queries[:3]:
                        result = await soundcloud_service.search(query, limit=5)
                        platform_results.extend(result.get('tracks', []))

                elif platform == 'vk':
                    vk_service = VKMusicService()
                    for query in search_queries[:2]:
                        tracks = await vk_service.search(query, limit=5)
                        platform_results.extend(tracks)

                elif platform == 'navidrome':
                    if navidrome_service.is_connected:
                        for query in search_queries[:2]:
                            tracks = await navidrome_service.search(query, limit=5)
                            platform_results.extend(tracks)

            except Exception as e:
                print(f"Error searching {platform}: {e}")
                continue

            # Фильтрация и выбор лучших совпадений
            if platform_results:
                # Ищем лучшие совпадения
                best_matches = []
                for track in platform_results:
                    if self.is_explicit_version(track):
                        best_matches.append(track)
                    elif self.similarity_ratio(censored_track.title, track.title) > 0.7:
                        best_matches.append(track)

                results[platform] = best_matches[:10]  # Ограничиваем результат

        return results

    async def find_original_version(
        self,
        censored_track: Track,
        min_similarity: float = 0.7
    ) -> Optional[Track]:
        """
        Поиск оригинальной (нецензурированной) версии трека

        Args:
            censored_track: Цензурированный трек
            min_similarity: Минимальная схожесть

        Returns:
            Оригинальная версия или None
        """
        # Поиск по всем платформам
        all_results = await self.search_original_across_platforms(censored_track)

        # Собираем все кандидаты
        all_candidates = []
        for platform, tracks in all_results.items():
            all_candidates.extend(tracks)

        if not all_candidates:
            return None

        # Приоритизация explicit версий
        explicit_candidates = [
            t for t in all_candidates
            if self.is_explicit_version(t)
        ]

        # Сначала ищем среди explicit
        if explicit_candidates:
            best = self.find_best_match(censored_track, explicit_candidates, min_similarity)
            if best:
                return best

        # Если не нашли explicit, ищем среди остальных
        best = self.find_best_match(censored_track, all_candidates, min_similarity)
        return best

    # ==================== Анализ аудио (заглушка) ====================

    async def analyze_audio_for_censorship(
        self,
        audio_url: str
    ) -> Dict:
        """
        Анализ аудиофайла на признаки цензуры

        Примечание: Полноценная реализация требует ML модели
        для детектирования:
        - Резких обрывов аудио (вырезание слов)
        - Заглушения (beep)
        - Замены слов (тишина/шум)

        Args:
            audio_url: URL аудиофайла

        Returns:
            Результат анализа
        """
        # Заглушка для будущей реализации
        # В продакшене здесь будет ML модель

        return {
            "is_censored": False,
            "confidence": 0.0,
            "censorship_segments": [],  # Таймкоды цензурных вставок
            "analysis_method": "placeholder"
        }

    # ==================== Статистика и отчеты ====================

    def get_censorship_report(self, tracks: List[Track]) -> Dict:
        """
        Отчет по цензуре в списке треков

        Args:
            tracks: Список треков для анализа

        Returns:
            Статистика
        """
        total = len(tracks)
        censored = sum(1 for t in tracks if self.is_censored(t))
        explicit = sum(1 for t in tracks if self.is_explicit_version(t))
        unknown = total - censored - explicit

        # Статистика по платформам
        platform_stats = Counter()
        for track in tracks:
            platform_stats[track.source] += 1

        return {
            "total_tracks": total,
            "censored_count": censored,
            "explicit_count": explicit,
            "unknown_count": unknown,
            "censorship_percentage": (censored / total * 100) if total > 0 else 0,
            "by_platform": dict(platform_stats)
        }


# Глобальный экземпляр
blues_detection_service = BluesDetectionService()
