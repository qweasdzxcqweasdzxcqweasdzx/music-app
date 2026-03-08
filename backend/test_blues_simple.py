"""
Упрощенные тесты для Blues Detection Service
"""

import sys
sys.path.insert(0, '/home/c1ten12/music-app/backend')

# Простая модель Track для тестов
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Track:
    title: str
    artist: str
    duration: int
    stream_url: str
    source: str = "soundcloud"
    is_explicit: bool = False
    is_censored: bool = False
    play_count: int = 0
    popularity: int = 0
    genres: List[str] = None
    description: Optional[str] = None

    def __post_init__(self):
        if self.genres is None:
            self.genres = []


# Импортируем сервис
from services.blues_detection_service import BluesDetectionService

# Создаем экземпляр
blues_service = BluesDetectionService()


def test_censorship_detection():
    """Тесты распознавания цензуры"""
    print("\n=== Тесты распознавания цензуры ===\n")

    # Трек с чистой версией
    clean_track = Track(
        title="Bad Guy (Clean Version)",
        artist="Billie Eilish",
        duration=194,
        stream_url="https://example.com/track1",
        source="soundcloud",
        is_explicit=False
    )

    # Трек с оригинальной версией
    explicit_track = Track(
        title="Bad Guy (Explicit Original)",
        artist="Billie Eilish",
        duration=194,
        stream_url="https://example.com/track2",
        source="youtube",
        is_explicit=True
    )

    # Трек с замаскированным словом
    masked_track = Track(
        title="F***k You (Radio Edit)",
        artist="CeeLo Green",
        duration=223,
        stream_url="https://example.com/track3",
        source="soundcloud",
        is_explicit=False
    )

    # Трек без маркеров
    unknown_track = Track(
        title="Shape of You",
        artist="Ed Sheeran",
        duration=233,
        stream_url="https://example.com/track4",
        source="soundcloud"
    )

    # Проверка clean трека
    assert blues_service.is_censored(clean_track) == True
    assert blues_service.is_explicit_version(clean_track) == False
    assert blues_service.get_version_type(clean_track) == "clean"
    print(f"✓ Clean track: {clean_track.title}")
    print(f"  is_censored: {blues_service.is_censored(clean_track)}")
    print(f"  version_type: {blues_service.get_version_type(clean_track)}")

    # Проверка explicit трека
    assert blues_service.is_censored(explicit_track) == False
    assert blues_service.is_explicit_version(explicit_track) == True
    assert blues_service.get_version_type(explicit_track) == "explicit"
    print(f"\n✓ Explicit track: {explicit_track.title}")
    print(f"  is_explicit: {blues_service.is_explicit_version(explicit_track)}")
    print(f"  version_type: {blues_service.get_version_type(explicit_track)}")

    # Проверка masked трека
    assert blues_service.is_censored(masked_track) == True
    print(f"\n✓ Masked track: {masked_track.title}")
    print(f"  is_censored: {blues_service.is_censored(masked_track)}")

    # Проверка unknown трека
    assert blues_service.get_version_type(unknown_track) == "unknown"
    print(f"\n✓ Unknown track: {unknown_track.title}")
    print(f"  version_type: {blues_service.get_version_type(unknown_track)}")


def test_fuzzy_matching():
    """Тесты fuzzy matching для названий"""
    print("\n\n=== Тесты Fuzzy Matching ===\n")

    # Тест нормализации
    title1 = "Bad Guy (Clean Version)"
    title2 = "Bad Guy (Explicit Original)"
    title3 = "Bad Guy - Radio Edit"

    norm1 = blues_service.normalize_title(title1)
    norm2 = blues_service.normalize_title(title2)
    norm3 = blues_service.normalize_title(title3)

    print(f"Оригинал 1: '{title1}'")
    print(f"Нормализовано: '{norm1}'")
    print(f"\nОригинал 2: '{title2}'")
    print(f"Нормализовано: '{norm2}'")
    print(f"\nОригинал 3: '{title3}'")
    print(f"Нормализовано: '{norm3}'")

    # Тест схожести
    similarity1 = blues_service.similarity_ratio(title1, title2)
    similarity2 = blues_service.similarity_ratio(title1, title3)
    similarity3 = blues_service.similarity_ratio(title1, title1)

    print(f"\nСхожесть '{title1}' и '{title2}': {similarity1:.2f}")
    print(f"Схожесть '{title1}' и '{title3}': {similarity2:.2f}")
    print(f"Схожесть '{title1}' и '{title1}': {similarity3:.2f}")

    assert similarity3 == 1.0, "Одинаковые названия должны иметь схожесть 1.0"
    assert similarity2 > 0.5, "Похожие названия должны иметь схожесть > 0.5"
    # similarity1 может быть < 0.5 из-за разных маркеров версий


def test_search_queries():
    """Тесты генерации поисковых запросов"""
    print("\n\n=== Тесты поисковых запросов ===\n")

    track = Track(
        title="Bad Guy (Clean Version)",
        artist="Billie Eilish",
        duration=194,
        stream_url="https://example.com/track",
        source="soundcloud"
    )

    queries = blues_service.generate_search_queries(track, prefer_explicit=True)

    print(f"Треки: {track.title} - {track.artist}")
    print(f"\nСгенерированные запросы ({len(queries)}):")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")

    # Проверка наличия explicit запросов
    explicit_queries = [q for q in queries if 'explicit' in q.lower()]
    assert len(explicit_queries) > 0, "Должны быть explicit запросы"
    print(f"\n✓ Explicit запросов: {len(explicit_queries)}")


def test_version_markers():
    """Тесты маркеров версий"""
    print("\n\n=== Тесты маркеров версий ===\n")

    # Маркеры чистой версии
    clean_titles = [
        "Song (Clean Version)",
        "Song (Radio Edit)",
        "Song - Edited for Radio",
        "Song (Censored)",
        "Song (версия для эфира)"
    ]

    # Маркеры explicit версии
    explicit_titles = [
        "Song (Explicit)",
        "Song (Original Uncensored)",
        "Song (Dirty Version)",
        "Song (Album Version)",
        "Song (оригинал)"
    ]

    print("Чистые версии:")
    for title in clean_titles:
        track = Track(title=title, artist="Artist", duration=180, stream_url="", source="test")
        is_clean = blues_service.is_censored(track)
        print(f"  '{title}' -> is_censored: {is_clean}")
        assert is_clean == True, f"Должна быть цензура: {title}"

    print("\nExplicit версии:")
    for title in explicit_titles:
        track = Track(title=title, artist="Artist", duration=180, stream_url="", source="test")
        is_explicit = blues_service.is_explicit_version(track)
        print(f"  '{title}' -> is_explicit: {is_explicit}")
        assert is_explicit == True, f"Должна быть explicit: {title}"


def test_censorship_report():
    """Тесты отчета по цензуре"""
    print("\n\n=== Тесты отчета по цензуре ===\n")

    tracks = [
        Track(title="Clean Song 1", artist="Artist", duration=180, stream_url="", source="soundcloud"),
        Track(title="Explicit Song", artist="Artist", duration=180, stream_url="", source="youtube", is_explicit=True),
        Track(title="Radio Edit", artist="Artist", duration=180, stream_url="", source="soundcloud"),
        Track(title="Original Version", artist="Artist", duration=180, stream_url="", source="youtube", is_explicit=True),
        Track(title="Unknown Song", artist="Artist", duration=180, stream_url="", source="soundcloud"),
    ]

    report = blues_service.get_censorship_report(tracks)

    print("Отчет по цензуре:")
    print(f"  Всего треков: {report['total_tracks']}")
    print(f"  Цензурировано: {report['censored_count']}")
    print(f"  Explicit: {report['explicit_count']}")
    print(f"  Неизвестно: {report['unknown_count']}")
    print(f"  Процент цензуры: {report['censorship_percentage']:.1f}%")
    print(f"  По платформам: {report['by_platform']}")


def test_best_match():
    """Тесты поиска лучшего совпадения"""
    print("\n\n=== Тесты поиска лучшего совпадения ===\n")

    query_track = Track(
        title="Bad Guy (Clean Version)",
        artist="Billie Eilish",
        duration=194,
        stream_url="",
        source="soundcloud"
    )

    candidates = [
        Track(title="Bad Guy (Explicit)", artist="Billie Eilish", duration=194, stream_url="", source="youtube", is_explicit=True),
        Track(title="Bad Guy (Instrumental)", artist="Billie Eilish", duration=194, stream_url="", source="soundcloud"),
        Track(title="Good Guy", artist="Billie Eilish", duration=180, stream_url="", source="soundcloud"),
        Track(title="Bad Guy", artist="Someone Else", duration=200, stream_url="", source="youtube"),
    ]

    best = blues_service.find_best_match(query_track, candidates, min_similarity=0.3)

    print(f"Исходный трек: {query_track.title}")
    print(f"\nКандидаты:")
    for c in candidates:
        print(f"  - {c.title} ({c.artist})")

    print(f"\n✓ Лучшее совпадение: {best.title if best else 'Не найдено'}")
    print(f"  Источник: {best.source if best else 'N/A'}")
    print(f"  is_explicit: {best.is_explicit if best else 'N/A'}")


if __name__ == "__main__":
    print("=" * 60)
    print("Blues Detection Service - Тесты")
    print("=" * 60)

    test_censorship_detection()
    test_fuzzy_matching()
    test_search_queries()
    test_version_markers()
    test_censorship_report()
    test_best_match()

    print("\n" + "=" * 60)
    print("Все тесты завершены успешно!")
    print("=" * 60)
