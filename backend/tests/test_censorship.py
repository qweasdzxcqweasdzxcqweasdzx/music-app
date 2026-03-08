"""
Tests for Advanced Censorship Detection Service

Запуск:
    python -m pytest tests/test_censorship.py -v

Coverage:
    python -m pytest tests/test_censorship.py --cov=services/censorship_service
"""

import pytest
from datetime import datetime
from models import Track
from services.censorship_service import (
    AdvancedCensorshipService,
    TextClassifier,
    AudioFingerprint,
    CensorshipCache,
    CensorshipDatabase,
    CensorshipResult,
    CensorshipType,
)


class TestTextClassifier:
    """Тесты для текстового классификатора"""

    def test_radio_edit_detection(self):
        """Обнаружение radio edit версии"""
        track = Track(
            id="test1",
            title="Song Title (Radio Edit)",
            artist="Artist Name",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )
        result = TextClassifier.classify(track)
        assert result.is_censored is True
        assert result.censorship_type == CensorshipType.RADIO_EDIT
        assert result.confidence >= 0.7

    def test_clean_version_detection(self):
        """Обнаружение clean версии"""
        track = Track(
            id="test2",
            title="Song Title (Clean Version)",
            artist="Artist Name",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )
        result = TextClassifier.classify(track)
        assert result.is_censored is True
        assert result.censorship_type == CensorshipType.CLEAN_VERSION

    def test_explicit_version_detection(self):
        """Обнаружение explicit версии (не цензура)"""
        track = Track(
            id="test3",
            title="Song Title (Explicit Version)",
            artist="Artist Name",
            duration=180,
            stream_url="http://test.com/track.mp3",
            is_explicit=True,
        )
        result = TextClassifier.classify(track)
        # Explicit версия - это оригинал, не цензура
        assert result.is_censored is False

    def test_instrumental_detection(self):
        """Обнаружение инструментальной версии"""
        track = Track(
            id="test4",
            title="Song Title (Instrumental)",
            artist="Artist Name",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )
        result = TextClassifier.classify(track)
        assert result.is_censored is True
        assert result.censorship_type == CensorshipType.INSTRUMENTAL

    def test_russian_censorship_detection(self):
        """Обнаружение русской цензуры"""
        track = Track(
            id="test5",
            title="Песня (Радио Версия)",
            artist="Исполнитель",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )
        result = TextClassifier.classify(track)
        assert result.is_censored is True
        assert result.censorship_type in [
            CensorshipType.RADIO_EDIT,
            CensorshipType.CLEAN_VERSION,
        ]

    def test_no_censorship(self):
        """Отсутствие цензуры"""
        track = Track(
            id="test6",
            title="Normal Song Title",
            artist="Artist Name",
            duration=200,
            stream_url="http://test.com/track.mp3",
        )
        result = TextClassifier.classify(track)
        assert result.is_censored is False
        assert result.censorship_type == CensorshipType.NONE

    def test_short_duration_suspicion(self):
        """Подозрение на цензуру из-за короткой длительности"""
        track = Track(
            id="test7",
            title="Song (Edit)",
            artist="Artist",
            duration=90,  # Очень короткий трек
            stream_url="http://test.com/track.mp3",
        )
        result = TextClassifier.classify(track)
        # Должно быть подозрение из-за комбинации факторов
        assert len(result.markers_found) > 0


class TestAudioFingerprint:
    """Тесты для акустических отпечатков"""

    def test_fingerprint_computation(self):
        """Вычисление отпечатка трека"""
        track = Track(
            id="test1",
            title="Song Title",
            artist="Artist Name",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )
        fp = AudioFingerprint.compute(track)
        assert "duration" in fp
        assert "hash" in fp
        assert fp["duration"] == 180

    def test_fingerprint_comparison_same_track(self):
        """Сравнение одинаковых треков"""
        fp1 = {"duration": 180, "hash": "abc123", "bpm_estimate": 120}
        fp2 = {"duration": 180, "hash": "abc123", "bpm_estimate": 120}
        score = AudioFingerprint.compare(fp1, fp2)
        assert score >= 0.8

    def test_fingerprint_comparison_different_tracks(self):
        """Сравнение разных треков"""
        fp1 = {"duration": 180, "hash": "abc123", "bpm_estimate": 120}
        fp2 = {"duration": 240, "hash": "xyz789", "bpm_estimate": 140}
        score = AudioFingerprint.compare(fp1, fp2)
        assert score < 0.5

    def test_fingerprint_comparison_similar_duration(self):
        """Сравнение треков с похожей длительностью"""
        fp1 = {"duration": 180, "hash": "abc123", "bpm_estimate": 120}
        fp2 = {"duration": 185, "hash": "abc123", "bpm_estimate": 120}
        score = AudioFingerprint.compare(fp1, fp2)
        assert score >= 0.7


class TestCensorshipCache:
    """Тесты для кэширования"""

    @pytest.mark.asyncio
    async def test_cache_set_get(self):
        """Сохранение и получение из кэша"""
        cache = CensorshipCache(ttl_seconds=60)
        track = Track(
            id="test1",
            title="Song Title",
            artist="Artist Name",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )
        result = CensorshipResult(
            is_censored=True,
            confidence=0.9,
            censorship_type=CensorshipType.RADIO_EDIT,
        )

        await cache.set(track, result)
        cached = await cache.get(track)

        assert cached is not None
        assert cached.is_censored is True
        assert cached.confidence == 0.9

    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """Истечение срока кэша"""
        cache = CensorshipCache(ttl_seconds=0)  # Мгновенное истечение
        track = Track(
            id="test1",
            title="Song Title",
            artist="Artist Name",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )
        result = CensorshipResult(
            is_censored=True,
            confidence=0.9,
            censorship_type=CensorshipType.RADIO_EDIT,
        )

        await cache.set(track, result)
        import asyncio
        await asyncio.sleep(0.1)  # Небольшая задержка
        cached = await cache.get(track)

        assert cached is None


class TestCensorshipDatabase:
    """Тесты для базы данных цензурированных треков"""

    @pytest.mark.asyncio
    async def test_add_and_check_censored(self):
        """Добавление и проверка цензурированного трека"""
        db = CensorshipDatabase()
        track = Track(
            id="test1",
            title="Censored Song",
            artist="Artist Name",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )

        await db.add_censored_track(track, original_id="original_123")
        is_censored, original_id = await db.is_known_censored(track)

        assert is_censored is True
        assert original_id == "original_123"

    @pytest.mark.asyncio
    async def test_user_reports(self):
        """Пользовательские отчёты"""
        db = CensorshipDatabase()
        track_id = "test_track"

        await db.report_track(track_id, "user1", True)
        await db.report_track(track_id, "user2", True)
        await db.report_track(track_id, "user3", False)

        confidence = await db.get_confidence_from_reports(track_id)
        assert 0.6 <= confidence <= 0.7  # 2 из 3 сказали что цензура


class TestAdvancedCensorshipService:
    """Тесты для основного сервиса"""

    @pytest.mark.asyncio
    async def test_check_censorship_radio_edit(self):
        """Проверка radio edit версии"""
        service = AdvancedCensorshipService()
        track = Track(
            id="test1",
            title="Song (Radio Edit)",
            artist="Artist",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )

        result = await service.check(track)
        assert result.is_censored is True
        assert result.censorship_type == CensorshipType.RADIO_EDIT
        assert result.method == "text_analysis"

    @pytest.mark.asyncio
    async def test_check_censorship_clean(self):
        """Проверка clean версии"""
        service = AdvancedCensorshipService()
        track = Track(
            id="test2",
            title="Song (Clean)",
            artist="Artist",
            duration=180,
            stream_url="http://test.com/track.mp3",
        )

        result = await service.check(track)
        assert result.is_censored is True

    @pytest.mark.asyncio
    async def test_check_no_censorship(self):
        """Проверка отсутствия цензуры"""
        service = AdvancedCensorshipService()
        track = Track(
            id="test3",
            title="Normal Song",
            artist="Artist",
            duration=200,
            stream_url="http://test.com/track.mp3",
        )

        result = await service.check(track)
        assert result.is_censored is False
        assert result.censorship_type == CensorshipType.NONE

    @pytest.mark.asyncio
    async def test_find_original_version(self):
        """Поиск оригинальной версии"""
        service = AdvancedCensorshipService()
        censored_track = Track(
            id="censored1",
            title="Song (Radio Edit)",
            artist="Artist",
            duration=180,
            stream_url="http://test.com/censored.mp3",
        )
        original_track = Track(
            id="original1",
            title="Song (Original Version)",
            artist="Artist",
            duration=210,  # Длиннее
            stream_url="http://test.com/original.mp3",
            is_explicit=True,
        )

        found_original = await service.find_original(
            censored_track,
            [original_track]
        )

        assert found_original is not None
        assert found_original.id == "original1"


class TestIntegration:
    """Интеграционные тесты"""

    @pytest.mark.asyncio
    async def test_full_censorship_workflow(self):
        """Полный рабочий процесс проверки на цензуру"""
        service = AdvancedCensorshipService()

        # 1. Создаём цензурированный трек
        censored_track = Track(
            id="censored",
            title="Bad Song (Clean Version)",
            artist="Bad Artist",
            duration=180,
            stream_url="http://test.com/censored.mp3",
        )

        # 2. Проверяем на цензуру
        result = await service.check(censored_track)
        assert result.is_censored is True

        # 3. Добавляем пользовательский отчёт
        if censored_track.id:
            await service.report(
                censored_track.id,
                "test_user",
                is_censored=True
            )

        # 4. Проверяем что отчёт учтён
        cached_result = await service.cache.get(censored_track)
        assert cached_result is not None


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
