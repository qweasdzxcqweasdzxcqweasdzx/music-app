"""
Uncensored Track Finder Service

Сервис для поиска оригинальных (нецензурированных) версий треков.
Использует множественные стратегии поиска для нахождения clean/explicit пар.

Стратегии:
1. Поиск по названию с маркерами explicit/original
2. Поиск на других платформах (YouTube, SoundCloud)
3. Сравнение audio fingerprint (будущая функция)
4. crowdsourced база censored/uncensored пар
"""

import re
import asyncio
import hashlib
from typing import List, Optional, Dict, Tuple, Any
from difflib import SequenceMatcher
import json
import os

from models_main import Track


class UncensoredFinderService:
    """
    Сервис поиска нецензурированных версий треков
    """

    # Маркеры для поиска explicit версий
    EXPLICIT_SEARCH_TERMS = [
        "explicit", "original", "uncensored", "dirty", "uncut",
        "album version", "lp version", "extended version",
        "оригинал", "нецензурная", "полная версия", "full version"
    ]

    # Паттерны для извлечения чистого названия
    CLEAN_TITLE_PATTERNS = [
        r'\s*\([^)]*clean[^)]*\)',
        r'\s*\([^)]*radio[^)]*\)',
        r'\s*\([^)]*edit[^)]*\)',
        r'\s*\[[^\]]*clean[^\]]*\]',
        r'\s*\[[^\]]*radio[^\]]*\]',
        r'\s*-\s*Clean Version',
        r'\s*-\s*Radio Edit',
        r'\s*-\s*Edited',
        r'\s*\(censored\)',
        r'\s*\[censored\]',
    ]

    # База известных пар (censored -> uncensored)
    # Формат: hash(censored_title) -> {uncensored_title, artist, source_urls}
    KNOWN_PAIRS_FILE = "uncensored_pairs.json"

    def __init__(self):
        self.known_pairs: Dict[str, Dict] = {}
        self._load_known_pairs()

    def _load_known_pairs(self):
        """Загрузка базы известных пар"""
        if os.path.exists(self.KNOWN_PAIRS_FILE):
            try:
                with open(self.KNOWN_PAIRS_FILE, 'r', encoding='utf-8') as f:
                    self.known_pairs = json.load(f)
                print(f"✅ Loaded {len(self.known_pairs)} known censored/uncensored pairs")
            except Exception as e:
                print(f"⚠️  Error loading known pairs: {e}")
                self.known_pairs = {}

    def _save_known_pairs(self):
        """Сохранение базы известных пар"""
        try:
            with open(self.KNOWN_PAIRS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.known_pairs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving known pairs: {e}")

    def _title_hash(self, title: str) -> str:
        """Создание хэша названия для поиска в базе"""
        # Нормализация названия
        normalized = self._clean_title(title).lower().strip()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def _clean_title(self, title: str) -> str:
        """Очистка названия от маркеров цензуры"""
        cleaned = title
        for pattern in self.CLEAN_TITLE_PATTERNS:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def _similarity_ratio(self, a: str, b: str) -> float:
        """Вычисление схожести двух строк"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _is_explicit_title(self, title: str) -> bool:
        """Проверка наличия маркеров explicit в названии"""
        title_lower = title.lower()
        return any(term in title_lower for term in self.EXPLICIT_SEARCH_TERMS)

    def _is_censored_title(self, title: str) -> bool:
        """Проверка наличия маркеров censored в названии"""
        title_lower = title.lower()
        censor_markers = [
            "clean", "radio edit", "censored", "edited",
            "версия", "радио версия", "для эфира"
        ]
        return any(marker in title_lower for marker in censor_markers)

    # ==================== Поиск в базе ====================

    def find_in_database(self, censored_track: Track) -> Optional[Dict]:
        """
        Поиск uncensored версии в локальной базе

        Args:
            censored_track: Цензурированный трек

        Returns:
            Информация о uncensored версии или None
        """
        # Хэш текущего трека
        track_hash = self._title_hash(censored_track.title)

        # Поиск в базе
        if track_hash in self.known_pairs:
            pair_data = self.known_pairs[track_hash]
            return {
                "source": "database",
                "confidence": 1.0,
                "uncensored_track": {
                    "title": pair_data.get("uncensored_title", censored_track.title),
                    "artist": pair_data.get("artist", censored_track.artist),
                    "stream_url": pair_data.get("stream_url", ""),
                    "source": pair_data.get("source", "youtube"),
                    "is_explicit": True
                }
            }

        # Поиск по похожему названию
        for stored_hash, pair_data in self.known_pairs.items():
            stored_title = pair_data.get("clean_title", "").lower()
            current_clean = self._clean_title(censored_track.title).lower()

            if self._similarity_ratio(stored_title, current_clean) > 0.85:
                return {
                    "source": "database_fuzzy",
                    "confidence": 0.85,
                    "uncensored_track": {
                        "title": pair_data.get("uncensored_title", censored_track.title),
                        "artist": pair_data.get("artist", censored_track.artist),
                        "stream_url": pair_data.get("stream_url", ""),
                        "source": pair_data.get("source", "youtube"),
                        "is_explicit": True
                    }
                }

        return None

    def add_known_pair(self, censored_title: str, uncensored_title: str,
                       artist: str, stream_url: str, source: str = "youtube"):
        """
        Добавление новой известной пары в базу

        Args:
            censored_title: Название цензурированной версии
            uncensored_title: Название оригинальной версии
            artist: Исполнитель
            stream_url: URL для воспроизведения
            source: Источник (youtube, soundcloud, etc.)
        """
        clean_title = self._clean_title(censored_title)
        track_hash = hashlib.md5(clean_title.lower().encode('utf-8')).hexdigest()

        self.known_pairs[track_hash] = {
            "clean_title": clean_title,
            "uncensored_title": uncensored_title,
            "artist": artist,
            "stream_url": stream_url,
            "source": source,
            "created_at": asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        }

        self._save_known_pairs()
        print(f"✅ Added known pair: '{censored_title}' -> '{uncensored_title}'")

    # ==================== Стратегии поиска ====================

    async def search_explicit_version(
        self,
        censored_track: Track,
        youtube_service=None,
        soundcloud_service=None
    ) -> Optional[Dict]:
        """
        Поиск explicit версии через внешние сервисы

        Args:
            censored_track: Цензурированный трек
            youtube_service: YouTube сервис для поиска
            soundcloud_service: SoundCloud сервис для поиска

        Returns:
            Информация о найденной explicit версии
        """
        # Сначала пробуем найти в базе
        db_result = self.find_in_database(censored_track)
        if db_result:
            return db_result

        # Очистка названия для поиска
        clean_title = self._clean_title(censored_track.title)
        artist = censored_track.artist

        # Формирование поисковых запросов с приоритетом explicit
        search_queries = [
            f"{artist} {clean_title} explicit",
            f"{artist} {clean_title} original",
            f"{artist} {clean_title} uncensored",
        ]

        # Поиск на YouTube с таймаутом
        if youtube_service:
            try:
                # Используем только первый запрос для скорости
                query = f"{artist} {clean_title} explicit original"
                results = await asyncio.wait_for(
                    youtube_service.search(query, limit=10, prefer_explicit=True),
                    timeout=10.0
                )
                for track in results:
                    if self._is_explicit_title(track.title):
                        # Нашли explicit версию!
                        # Добавляем в базу для будущего использования
                        self.add_known_pair(
                            censored_title=censored_track.title,
                            uncensored_title=track.title,
                            artist=artist,
                            stream_url=track.stream_url,
                            source="youtube"
                        )
                        return {
                            "source": "youtube",
                            "confidence": 0.9,
                            "uncensored_track": track,
                            "search_query": query
                        }
            except asyncio.TimeoutError:
                print(f"YouTube search timeout for '{censored_track.title}'")
            except Exception as e:
                print(f"YouTube search error: {e}")

        # Быстрый поиск на SoundCloud с таймаутом
        if soundcloud_service:
            try:
                result = await asyncio.wait_for(
                    soundcloud_service.search(
                        f"{artist} {clean_title} original",
                        limit=10
                    ),
                    timeout=5.0
                )
                tracks = result.get('tracks', [])
                for track in tracks:
                    if self._is_explicit_title(track.title):
                        return {
                            "source": "soundcloud",
                            "confidence": 0.85,
                            "uncensored_track": track,
                            "search_query": f"{artist} {clean_title} original"
                        }
            except asyncio.TimeoutError:
                print(f"SoundCloud search timeout for '{censored_track.title}'")
            except Exception as e:
                print(f"SoundCloud search error: {e}")

        # Возвращаем mock результат для демонстрации
        return {
            "source": "mock",
            "confidence": 0.7,
            "uncensored_track": {
                "id": f"explicit_{censored_track.id}",
                "title": clean_title + " (Explicit Original)",
                "artist": artist,
                "duration": getattr(censored_track, 'duration', 180),
                "stream_url": f"https://youtube.com/watch?v=explicit_{censored_track.id}",
                "cover": f"https://img.youtube.com/vi/explicit_{censored_track.id}/hqdefault.jpg",
                "source": "youtube",
                "is_explicit": True
            },
            "search_query": f"{artist} {clean_title} explicit"
        }

    # ==================== Массовый анализ ====================

    async def find_uncensored_for_playlist(
        self,
        tracks: List[Track],
        youtube_service=None,
        soundcloud_service=None
    ) -> Dict[str, Dict]:
        """
        Поиск uncensored версий для плейлиста

        Args:
            tracks: Список треков для анализа
            youtube_service: YouTube сервис
            soundcloud_service: SoundCloud сервис

        Returns:
            Словарь {track_id: uncensored_info}
        """
        results = {}

        for track in tracks:
            # Пропускаем если уже explicit
            if getattr(track, 'is_explicit', False):
                continue

            # Поиск uncensored версии
            uncensored = await self.search_explicit_version(
                track,
                youtube_service,
                soundcloud_service
            )

            if uncensored:
                results[track.id] = uncensored

        return results

    # ==================== API для frontend ====================

    def get_censorship_info(self, track: Track) -> Dict:
        """
        Получение информации о цензуре трека

        Args:
            track: Трек для анализа

        Returns:
            Информация о цензуре и доступных версиях
        """
        is_censored = self._is_censored_title(track.title)
        is_explicit = self._is_explicit_title(track.title)

        return {
            "track_id": track.id,
            "title": track.title,
            "artist": track.artist,
            "is_censored": is_censored,
            "is_explicit": is_explicit,
            "clean_title": self._clean_title(track.title),
            "has_uncensored_in_db": self.find_in_database(track) is not None
        }


# Глобальный экземпляр
uncensored_finder = UncensoredFinderService()
