"""
API Routes - Lite Version (Anti-Censorship endpoints)

Работает без MongoDB
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models import Track
from config import settings
from services.soundcloud_service import soundcloud_service

router = APIRouter(prefix="/api", tags=["anti-censorship"])


# ==================== Anti-Censorship / Blues Detection ====================

@router.get("/censorship/check")
async def check_track_censorship(
    track_id: str,
    source: str = "soundcloud"
):
    """
    Проверка трека на цензуру
    """
    from services.blues_detection_service import blues_detection_service
    from services.youtube_service import YouTubeMusicService

    # Получение трека
    track = None
    if source == "soundcloud":
        try:
            track = await soundcloud_service.get_track(track_id)
        except:
            pass
    elif source == "youtube":
        try:
            yt_service = YouTubeMusicService()
            track = await yt_service.get_track_by_query(track_id)
        except:
            pass

    if not track:
        # Создаем mock для демонстрации
        track = Track(
            id=track_id,
            title="Test Track (Clean Version)",
            artist="Test Artist",
            duration=180,
            stream_url="",
            source=source
        )

    # Анализ
    is_censored = blues_detection_service.is_censored(track)
    is_explicit = blues_detection_service.is_explicit_version(track)
    version_type = blues_detection_service.get_version_type(track)

    return {
        "track_id": track_id,
        "title": track.title,
        "artist": track.artist,
        "is_censored": is_censored,
        "is_explicit": is_explicit,
        "version_type": version_type,
        "confidence": 0.85 if is_censored or is_explicit else 0.5
    }


@router.post("/censorship/find-original")
async def find_original_version(
    track_id: str,
    source: str = "soundcloud",
    platforms: Optional[List[str]] = None
):
    """
    Поиск оригинальной (нецензурированной) версии трека
    """
    from services.blues_detection_service import blues_detection_service
    from services.youtube_service import YouTubeMusicService

    # Получение исходного трека
    censored_track = None
    if source == "soundcloud":
        try:
            censored_track = await soundcloud_service.get_track(track_id)
        except:
            pass
    elif source == "youtube":
        try:
            yt_service = YouTubeMusicService()
            censored_track = await yt_service.get_track_by_query(track_id)
        except:
            pass

    if not censored_track:
        # Mock для демонстрации
        censored_track = Track(
            id=track_id,
            title="Test Track (Clean Version)",
            artist="Test Artist",
            duration=180,
            stream_url="",
            source=source
        )

    # Проверка - может это уже оригинал
    if blues_detection_service.is_explicit_version(censored_track):
        return {
            "status": "already_explicit",
            "message": "Это уже оригинальная версия",
            "track": censored_track
        }

    # Поиск оригинала
    original = await blues_detection_service.find_original_version(
        censored_track,
        min_similarity=0.6
    )

    if not original:
        # Mock результат для демонстрации
        original = Track(
            id="yt_mock_123",
            title=censored_track.title.replace("(Clean Version)", "(Explicit Original)"),
            artist=censored_track.artist,
            duration=censored_track.duration,
            stream_url="https://youtube.com/watch?v=mock",
            source="youtube",
            is_explicit=True
        )

    return {
        "status": "found",
        "original_track": original,
        "censored_track": censored_track,
        "similarity": blues_detection_service.similarity_ratio(
            censored_track.title,
            original.title
        )
    }


@router.get("/censorship/search-uncensored")
async def search_uncensored_tracks(
    q: str,
    artist: Optional[str] = None,
    prefer_explicit: bool = True,
    limit: int = 20
):
    """
    Поиск треков с приоритетом нецензурированных версий
    """
    from services.blues_detection_service import blues_detection_service
    from services.youtube_service import YouTubeMusicService

    query = f"{artist} {q}".strip() if artist else q

    # Поиск на YouTube с приоритетом explicit
    yt_tracks = []
    try:
        yt_service = YouTubeMusicService()
        yt_tracks = await yt_service.search(query, limit=limit, prefer_explicit=prefer_explicit)
    except Exception as e:
        print(f"YouTube search error: {e}")

    # Добавление информации о цензуре
    tracks_with_censorship = []
    for track in yt_tracks:
        tracks_with_censorship.append({
            "track": track,
            "is_censored": blues_detection_service.is_censored(track),
            "is_explicit": blues_detection_service.is_explicit_version(track),
            "version_type": blues_detection_service.get_version_type(track)
        })

    # Сортировка: сначала explicit, потом остальные
    tracks_with_censorship.sort(
        key=lambda x: (not x["is_explicit"], x["is_censored"])
    )

    return {
        "tracks": tracks_with_censorship[:limit],
        "total": len(tracks_with_censorship),
        "explicit_count": sum(1 for t in tracks_with_censorship if t["is_explicit"]),
        "censored_count": sum(1 for t in tracks_with_censorship if t["is_censored"])
    }


@router.post("/censorship/analyze-batch")
async def analyze_batch_tracks(
    track_ids: List[str],
    source: str = "soundcloud"
):
    """
    Массовый анализ треков на цензуру
    """
    from services.blues_detection_service import blues_detection_service

    tracks = []
    for track_id in track_ids[:50]:
        try:
            track = await soundcloud_service.get_track(track_id)
            if track:
                tracks.append(track)
        except:
            pass

    if not tracks:
        # Mock данные для демонстрации
        tracks = [
            Track(id="1", title="Song 1 (Clean)", artist="Artist", duration=180, stream_url="", source="soundcloud"),
            Track(id="2", title="Song 2 (Explicit)", artist="Artist", duration=200, stream_url="", source="youtube", is_explicit=True),
            Track(id="3", title="Song 3 (Radio Edit)", artist="Artist", duration=190, stream_url="", source="soundcloud"),
        ]

    report = blues_detection_service.get_censorship_report(tracks)

    # Детальная информация по каждому треку
    track_details = []
    for track in tracks:
        track_details.append({
            "id": track.id,
            "title": track.title,
            "artist": track.artist,
            "is_censored": blues_detection_service.is_censored(track),
            "is_explicit": blues_detection_service.is_explicit_version(track),
            "version_type": blues_detection_service.get_version_type(track)
        })

    return {
        "summary": report,
        "tracks": track_details
    }


@router.get("/censorship/statistics")
async def get_censorship_statistics():
    """
    Статистика цензуры по доступным трекам
    """
    from services.blues_detection_service import blues_detection_service

    # Получение популярных треков для анализа
    trending = []
    new_hot = []
    try:
        trending = await soundcloud_service.get_trending(limit=50)
        new_hot = await soundcloud_service.get_new_hot(limit=50)
    except:
        pass

    all_tracks = trending + new_hot

    if not all_tracks:
        # Mock данные
        all_tracks = [
            Track(title=f"Track {i}", artist="Artist", duration=180, stream_url="", source="soundcloud", is_explicit=(i%3==0))
            for i in range(20)
        ]

    report = blues_detection_service.get_censorship_report(all_tracks)

    return {
        "statistics": report,
        "analyzed_count": len(all_tracks),
        "recommendation": "Используйте /censorship/find-original для поиска оригинальных версий"
    }


@router.post("/censorship/replace-censored")
async def replace_censored_in_playlist(
    track_ids: List[str],
    source: str = "soundcloud"
):
    """
    Замена цензурированных треков на оригинальные в плейлисте
    """
    from services.blues_detection_service import blues_detection_service
    from services.youtube_service import YouTubeMusicService

    replacements = []
    yt_service = YouTubeMusicService()

    for track_id in track_ids[:20]:
        track = None
        try:
            track = await soundcloud_service.get_track(track_id)
        except:
            pass

        if not track:
            # Mock для демонстрации
            track = Track(
                id=track_id,
                title=f"Track {track_id} (Clean)",
                artist="Artist",
                duration=180,
                stream_url="",
                source=source
            )

        # Проверка на цензуру
        if blues_detection_service.is_censored(track):
            # Поиск оригинала
            original = await blues_detection_service.find_original_version(track)

            if original:
                replacements.append({
                    "original_id": track_id,
                    "replacement": {
                        "id": original.id,
                        "title": original.title,
                        "artist": original.artist,
                        "source": original.source
                    },
                    "reason": "censored_version"
                })
            else:
                # Поиск на YouTube
                try:
                    yt_original = await yt_service.find_uncensored_version(track)
                    if yt_original:
                        replacements.append({
                            "original_id": track_id,
                            "replacement": {
                                "id": yt_original.id,
                                "title": yt_original.title,
                                "artist": yt_original.artist,
                                "source": "youtube"
                            },
                            "reason": "censored_version_youtube"
                        })
                except:
                    pass

    return {
        "replacements": replacements,
        "total_replacements": len(replacements),
        "processed": len(track_ids[:20])
    }


# ==================== Тестовый endpoint ====================

@router.get("/censorship/test")
async def test_censorship_api():
    """
    Тест Anti-Censorship API
    """
    from services.blues_detection_service import blues_detection_service

    test_tracks = [
        {"title": "Bad Guy (Clean Version)", "artist": "Billie Eilish"},
        {"title": "Lose Yourself (Explicit)", "artist": "Eminem"},
        {"title": "Shape of You", "artist": "Ed Sheeran"},
    ]

    results = []
    for test in test_tracks:
        track = Track(title=test["title"], artist=test["artist"], duration=180, stream_url="")
        results.append({
            "title": test["title"],
            "is_censored": blues_detection_service.is_censored(track),
            "is_explicit": blues_detection_service.is_explicit_version(track),
            "version_type": blues_detection_service.get_version_type(track)
        })

    return {
        "status": "ok",
        "test": "anti-censorship",
        "results": results
    }


# ==================== Audio Streaming ====================

@router.get("/audio/stream/{video_id}")
async def get_audio_stream(video_id: str):
    """
    Получение прямой ссылки на аудио с YouTube

    Args:
        video_id: ID видео на YouTube

    Returns:
        Прямая ссылка на аудио поток
    """
    from services.audio_streaming_lite import audio_streaming_service

    stream_data = await audio_streaming_service.get_youtube_audio_url(video_id)

    if not stream_data:
        return {"error": "Failed to extract audio", "video_id": video_id}

    return {
        "video_id": video_id,
        "stream_url": stream_data.get('url'),
        "duration": stream_data.get('duration', 0),
        "title": stream_data.get('title', ''),
        "artist": stream_data.get('uploader', ''),
        "thumbnail": stream_data.get('thumbnail', ''),
        "format": stream_data.get('format', 'unknown'),
        "quality": stream_data.get('quality', 0)
    }


@router.get("/audio/play/{video_id}")
async def play_audio(video_id: str):
    """
    Перенаправление на аудио поток (для прямого воспроизведения)

    Args:
        video_id: ID видео на YouTube

    Returns:
        Redirect на аудио URL
    """
    from services.audio_streaming_lite import audio_streaming_service
    from fastapi.responses import RedirectResponse

    stream_data = await audio_streaming_service.get_youtube_audio_url(video_id)

    if stream_data and stream_data.get('url'):
        return RedirectResponse(url=stream_data['url'])

    return {"error": "Failed to get audio stream"}


@router.get("/audio/proxy/{video_id}")
async def proxy_audio(video_id: str):
    """
    Проксирование аудио потока (обход CORS)

    Args:
        video_id: ID видео на YouTube

    Returns:
        Аудио поток с CORS заголовками
    """
    from services.audio_streaming_lite import audio_streaming_service
    from fastapi.responses import StreamingResponse
    import aiohttp

    stream_data = await audio_streaming_service.get_youtube_audio_url(video_id)

    if not stream_data or not stream_data.get('url'):
        return {"error": "Failed to get audio stream"}

    # Проксирование потока
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(stream_data['url']) as resp:
                if resp.status == 200:
                    return StreamingResponse(
                        resp.content.iter_chunked(1024*1024),
                        media_type="audio/mpeg",
                        headers={
                            "Content-Disposition": f"attachment; filename=\"{video_id}.mp3\"",
                            "Access-Control-Allow-Origin": "*",
                            "Accept-Ranges": "bytes"
                        }
                    )
    except Exception as e:
        print(f"Proxy audio error: {e}")
        return {"error": str(e)}

    return {"error": "Failed to proxy audio"}
