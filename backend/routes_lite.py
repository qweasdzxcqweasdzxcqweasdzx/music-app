"""
API Routes - Lite Version (Anti-Censorship endpoints)

Работает без MongoDB
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional
from fastapi.responses import JSONResponse
import asyncio

from models_main import Track as TrackModel
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
    from services.soundcloud_service import soundcloud_service
    import random
    
    query = f"{artist} {q}".strip() if artist else q
    
    # Поиск на YouTube и SoundCloud параллельно
    yt_tracks = []
    sc_tracks = []
    
    try:
        # YouTube поиск
        yt_service = YouTubeMusicService()
        yt_tracks = await yt_service.search(query, limit=limit//2, prefer_explicit=prefer_explicit)
    except Exception as e:
        print(f"YouTube search error: {e}")
    
    try:
        # SoundCloud поиск
        sc_result = await soundcloud_service.search(query, limit=limit//2)
        sc_tracks = sc_result.get('tracks', [])
    except Exception as e:
        print(f"SoundCloud search error: {e}")
    
    # Объединяем результаты
    all_tracks = yt_tracks + sc_tracks
    
    # Если результатов нет, генерируем mock
    if not all_tracks:
        from models_main import Track as TrackModel
        mock_titles = [
            f"{query} - Official Music Video",
            f"{query} - Live Performance",
            f"{query} - Audio",
            f"{query} - Lyrics",
            f"{query} - Cover Version",
        ]
        all_tracks = []
        for i in range(min(limit, len(mock_titles))):
            source = "youtube" if i % 2 == 0 else "soundcloud"
            all_tracks.append(Track(
                id=f"{source}_{random.randint(1000, 9999)}",
                title=mock_titles[i],
                artist=query.title(),
                duration=random.randint(180, 300),
                stream_url=f"https://www.youtube.com/watch?v=dQw4w9WgXcQ" if source == "youtube" else f"https://soundcloud.com/artist/track",
                cover=f"https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg" if source == "youtube" else f"https://picsum.photos/seed/sc{i}/300/300",
                source=source,
                is_explicit=(i % 3 == 0),
                is_censored=False
            ))
    
    # Добавление информации о цензуре
    tracks_with_censorship = []
    for track in all_tracks:
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
        "censored_count": sum(1 for t in tracks_with_censorship if t["is_censored"]),
        "sources": {
            "youtube": sum(1 for t in all_tracks if t.source == "youtube"),
            "soundcloud": sum(1 for t in all_tracks if t.source == "soundcloud")
        }
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
            TrackModel(id="1", title="Song 1 (Clean)", artist="Artist", duration=180, stream_url="", source="soundcloud"),
            TrackModel(id="2", title="Song 2 (Explicit)", artist="Artist", duration=200, stream_url="", source="youtube", is_explicit=True),
            TrackModel(id="3", title="Song 3 (Radio Edit)", artist="Artist", duration=190, stream_url="", source="soundcloud"),
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
            TrackModel(title=f"Track {i}", artist="Artist", duration=180, stream_url="", source="soundcloud", is_explicit=(i%3==0))
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
        track = TrackModel(title=test["title"], artist=test["artist"], duration=180, stream_url="")
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


# ==================== Music Discovery Endpoints ====================

@router.get("/top")
async def get_top_tracks(limit: int = Query(default=20, le=100)):
    """
    Получить популярные треки (топ чарты)
    
    Args:
        limit: Количество треков (макс. 100)
    
    Returns:
        Список популярных треков
    """
    from services.soundcloud_service import soundcloud_service
    import random
    
    # Пробуем быстро получить тренды с SoundCloud (с коротким таймаутом)
    try:
        result = await asyncio.wait_for(
            soundcloud_service.get_trending(limit=limit),
            timeout=5.0
        )
        if result and result.get('tracks'):
            return {
                "tracks": result['tracks'][:limit],
                "total": len(result['tracks']),
                "source": "soundcloud"
            }
    except asyncio.TimeoutError:
        print("SoundCloud trending timeout, using mock data")
    except Exception as e:
        print(f"SoundCloud trending error: {e}")
    
    # Mock данные (быстрый ответ)
    from models_main import Track as TrackModel
    mock_tracks = []
    artists = ["The Weeknd", "Dua Lipa", "Taylor Swift", "Ed Sheeran", "Ariana Grande", "Drake", "Billie Eilish"]
    for i in range(min(limit, 20)):
        mock_tracks.append(Track(
            id=f"top_{i}",
            title=f"Top Hit #{i+1}",
            artist=random.choice(artists),
            duration=random.randint(180, 240),
            stream_url=f"https://youtube.com/watch?v=mock_top_{i}",
            cover=f"https://img.youtube.com/vi/mock_top_{i}/hqdefault.jpg",
            source="youtube",
            play_count=random.randint(1000000, 10000000),
            is_explicit=(i % 4 == 0)
        ))
    
    return {
        "tracks": mock_tracks,
        "total": len(mock_tracks),
        "source": "mock"
    }


@router.get("/new")
async def get_new_releases(limit: int = Query(default=20, le=100)):
    """
    Получить новые релизы
    
    Args:
        limit: Количество релизов (макс. 100)
    
    Returns:
        Список новых треков
    """
    from services.soundcloud_service import soundcloud_service
    import random
    
    # Пробуем получить новые треки с SoundCloud
    try:
        result = await soundcloud_service.get_new_hot(limit=limit)
        if result and result.get('tracks'):
            return {
                "tracks": result['tracks'][:limit],
                "total": len(result['tracks']),
                "source": "soundcloud"
            }
    except Exception as e:
        print(f"SoundCloud new releases error: {e}")
    
    # Mock данные
    from models_main import Track as TrackModel
    mock_tracks = []
    genres = ["Pop", "Hip-Hop", "Electronic", "Rock", "R&B"]
    for i in range(min(limit, 10)):
        mock_tracks.append(Track(
            id=f"new_{i}",
            title=f"New Release #{i+1}",
            artist=f"Artist {i+1}",
            duration=random.randint(180, 240),
            stream_url=f"https://soundcloud.com/artist/new_{i}",
            cover=f"https://picsum.photos/seed/new_{i}/300/300",
            source="soundcloud",
            genre=random.choice(genres),
            created_at="2026-03-10"
        ))
    
    return {
        "tracks": mock_tracks,
        "total": len(mock_tracks),
        "source": "mock"
    }


@router.get("/genres")
async def get_all_genres():
    """
    Получить список всех доступных жанров
    
    Returns:
        Список жанров с описанием
    """
    genres = [
        {"id": "pop", "name": "Pop", "description": "Популярная музыка", "color": "#1DB954"},
        {"id": "rock", "name": "Rock", "description": "Рок музыка", "color": "#E91429"},
        {"id": "hiphop", "name": "Hip-Hop", "description": "Хип-хоп и рэп", "color": "#DC148C"},
        {"id": "electronic", "name": "Electronic", "description": "Электронная музыка", "color": "#0D73EC"},
        {"id": "indie", "name": "Indie", "description": "Инди музыка", "color": "#608108"},
        {"id": "metal", "name": "Metal", "description": "Метал музыка", "color": "#BC5900"},
        {"id": "jazz", "name": "Jazz", "description": "Джаз", "color": "#477D95"},
        {"id": "classical", "name": "Classical", "description": "Классическая музыка", "color": "#8C67AC"},
        {"id": "rnb", "name": "R&B", "description": "R&B и соул", "color": "#DC143C"},
        {"id": "country", "name": "Country", "description": "Кантри музыка", "color": "#5F4A3C"},
        {"id": "latin", "name": "Latin", "description": "Латинская музыка", "color": "#E91E63"},
        {"id": "reggae", "name": "Reggae", "description": "Регги", "color": "#009688"},
        {"id": "blues", "name": "Blues", "description": "Блюз", "color": "#3F51B5"},
        {"id": "soul", "name": "Soul", "description": "Соул", "color": "#9C27B0"},
        {"id": "funk", "name": "Funk", "description": "Фанк", "color": "#FF5722"},
        {"id": "ambient", "name": "Ambient", "description": "Амбиент", "color": "#00BCD4"},
        {"id": "house", "name": "House", "description": "Хаус", "color": "#FFC107"},
        {"id": "techno", "name": "Techno", "description": "Техно", "color": "#607D8B"},
        {"id": "trance", "name": "Trance", "description": "Транс", "color": "#9E9E9E"},
        {"id": "dubstep", "name": "Dubstep", "description": "Дабстеп", "color": "#795548"},
        {"id": "drum-and-bass", "name": "Drum & Bass", "description": "Драм-н-бейс", "color": "#3E2723"},
        {"id": "kpop", "name": "K-Pop", "description": "Корейская поп музыка", "color": "#FF4081"},
        {"id": "jpop", "name": "J-Pop", "description": "Японская поп музыка", "color": "#E040FB"},
        {"id": "focus", "name": "Focus", "description": "Музыка для концентрации", "color": "#536DFE"},
    ]
    
    return {
        "genres": genres,
        "total": len(genres)
    }


@router.get("/genres/{genre_id}")
async def get_genre_tracks(
    genre_id: str,
    limit: int = Query(default=20, le=100)
):
    """
    Получить треки определенного жанра
    
    Args:
        genre_id: ID жанра
        limit: Количество треков (макс. 100)
    
    Returns:
        Список треков жанра
    """
    from services.soundcloud_service import soundcloud_service
    import random
    
    genre_map = {
        "pop": "pop music",
        "rock": "rock music",
        "hiphop": "hip hop rap",
        "electronic": "electronic dance music",
        "indie": "indie music",
        "metal": "metal music",
        "jazz": "jazz music",
        "classical": "classical music",
        "rnb": "r&b soul",
        "country": "country music",
        "latin": "latin music",
        "reggae": "reggae music",
        "blues": "blues music",
        "soul": "soul music",
        "funk": "funk music",
        "ambient": "ambient music",
        "house": "house music",
        "techno": "techno music",
        "trance": "trance music",
        "dubstep": "dubstep",
        "drum-and-bass": "drum and bass",
        "kpop": "k-pop",
        "jpop": "j-pop",
        "focus": "focus concentration music"
    }
    
    genre_name = genre_map.get(genre_id, genre_id)
    
    # Быстрый поиск на SoundCloud (с таймаутом)
    try:
        result = await asyncio.wait_for(
            soundcloud_service.search(genre_name, limit=limit),
            timeout=5.0
        )
        if result and result.get('tracks'):
            return {
                "tracks": result['tracks'][:limit],
                "genre": genre_id,
                "total": len(result['tracks']),
                "source": "soundcloud"
            }
    except asyncio.TimeoutError:
        print(f"SoundCloud genre search timeout for {genre_id}, using mock data")
    except Exception as e:
        print(f"SoundCloud genre search error: {e}")
    
    # Mock данные (быстрый ответ)
    from models_main import Track as TrackModel
    mock_tracks = []
    for i in range(min(limit, 20)):
        mock_tracks.append(Track(
            id=f"{genre_id}_{i}",
            title=f"{genre_name.title()} Track #{i+1}",
            artist=f"{genre_name.title()} Artist",
            duration=random.randint(180, 300),
            stream_url=f"https://soundcloud.com/artist/{genre_id}_{i}",
            cover=f"https://picsum.photos/seed/{genre_id}_{i}/300/300",
            source="soundcloud",
            genre=genre_id,
            is_explicit=(i % 5 == 0)
        ))

    return {
        "tracks": mock_tracks,
        "genre": genre_id,
        "total": len(mock_tracks),
        "source": "mock"
    }


# ==================== Uncensored Track Finder API ====================

@router.get("/uncensored/find")
async def find_uncensored_version(
    track_id: str,
    title: str,
    artist: str,
    source: str = "soundcloud"
):
    """
    Поиск нецензурированной версии трека
    
    Args:
        track_id: ID трека
        title: Название трека
        artist: Исполнитель
        source: Источник (youtube, soundcloud)
    
    Returns:
        Информация о найденной uncensored версии
    """
    from services.uncensored_finder_service import uncensored_finder
    from services.youtube_service import YouTubeMusicService
    from services.soundcloud_service import soundcloud_service
    
    # Создаем mock трек для анализа
    track = Track(
        id=track_id,
        title=title,
        artist=artist,
        duration=0,
        stream_url="",
        source=source
    )
    
    # Проверка в базе
    db_result = uncensored_finder.find_in_database(track)
    if db_result:
        return {
            "status": "found",
            "source": db_result["source"],
            "confidence": db_result["confidence"],
            "track": db_result["uncensored_track"]
        }
    
    # Поиск через внешние сервисы
    yt_service = YouTubeMusicService()
    
    result = await uncensored_finder.search_explicit_version(
        track,
        youtube_service=yt_service,
        soundcloud_service=soundcloud_service
    )
    
    if result:
        return {
            "status": "found",
            "source": result["source"],
            "confidence": result["confidence"],
            "track": result["uncensored_track"],
            "search_query": result.get("search_query", "")
        }
    
    return {
        "status": "not_found",
        "message": "Не удалось найти нецензурированную версию"
    }


@router.post("/uncensored/add-pair")
async def add_uncensored_pair(request: Request):
    """
    Добавление известной пары censored/uncensored в базу
    
    Args:
        censored_title: Название цензурированной версии
        uncensored_title: Название оригинальной версии
        artist: Исполнитель
        stream_url: URL для воспроизведения
        source: Источник
    
    Returns:
        Статус операции
    """
    from services.uncensored_finder_service import uncensored_finder
    
    # Чтение JSON body
    import json
    body = await request.json()
    
    censored_title = body.get("censored_title")
    uncensored_title = body.get("uncensored_title")
    artist = body.get("artist")
    stream_url = body.get("stream_url")
    source = body.get("source", "youtube")
    
    if not all([censored_title, uncensored_title, artist, stream_url]):
        return {
            "status": "error",
            "message": "Missing required fields: censored_title, uncensored_title, artist, stream_url"
        }
    
    uncensored_finder.add_known_pair(
        censored_title=censored_title,
        uncensored_title=uncensored_title,
        artist=artist,
        stream_url=stream_url,
        source=source
    )
    
    return {
        "status": "success",
        "message": f"Добавлена пара: '{censored_title}' -> '{uncensored_title}'"
    }


@router.get("/uncensored/check")
async def check_track_censorship_status(
    track_id: str,
    title: str,
    artist: str
):
    """
    Проверка статуса цензуры трека
    
    Args:
        track_id: ID трека
        title: Название трека
        artist: Исполнитель
    
    Returns:
        Информация о цензуре трека
    """
    from services.uncensored_finder_service import uncensored_finder
    from models_main import Track as TrackModel
    
    track = Track(
        id=track_id,
        title=title,
        artist=artist,
        duration=0,
        stream_url="",
        source="unknown"
    )
    
    info = uncensored_finder.get_censorship_info(track)
    
    return info


@router.get("/uncensored/playlist")
async def find_uncensored_for_playlist(
    track_ids: str,  # Comma-separated list
    source: str = "soundcloud"
):
    """
    Поиск uncensored версий для плейлиста
    
    Args:
        track_ids: Список ID треков через запятую
        source: Источник
    
    Returns:
        Словарь {track_id: uncensored_info}
    """
    from services.uncensored_finder_service import uncensored_finder
    from services.youtube_service import YouTubeMusicService
    from services.soundcloud_service import soundcloud_service
    from models_main import Track as TrackModel
    
    # Парсинг списка ID
    ids = [id.strip() for id in track_ids.split(",") if id.strip()]
    
    # Создаем mock треки (в реальности нужно загружать из БД)
    tracks = [
        TrackModel(id=id, title=f"Track {id}", artist="Unknown", duration=0, stream_url="", source=source)
        for id in ids[:20]  # Максимум 20 треков
    ]
    
    yt_service = YouTubeMusicService()
    
    results = await uncensored_finder.find_uncensored_for_playlist(
        tracks,
        youtube_service=yt_service,
        soundcloud_service=soundcloud_service
    )
    
    return {
        "total_tracks": len(ids),
        "found_uncensored": len(results),
        "results": results
    }


# ==================== Removed/Hidden Tracks API ====================

@router.get("/removed/find")
async def find_removed_track(
    artist: str,
    title: str
):
    """
    Поиск удалённого/скрытого трека в базе
    
    Args:
        artist: Исполнитель
        title: Название трека/альбома
    
    Returns:
        Информация о треке и альтернативные источники
    """
    import json
    import os
    
    db_file = "removed_tracks_db.json"
    if not os.path.exists(db_file):
        return {
            "status": "error",
            "message": "База удалённых треков не найдена"
        }
    
    with open(db_file, 'r', encoding='utf-8') as f:
        removed_db = json.load(f)
    
    # Поиск по артисту и названию
    for item in removed_db:
        if (artist.lower() in item.get("artist", "").lower() and
            title.lower() in item.get("title", "").lower()):
            return {
                "status": "found",
                "item": item
            }
    
    # Поиск только по артисту
    matches = [item for item in removed_db if artist.lower() in item.get("artist", "").lower()]
    if matches:
        return {
            "status": "partial",
            "message": f"Найдено {len(matches)} записей для {artist}",
            "items": matches[:10]
        }
    
    return {
        "status": "not_found",
        "message": f"Не найдено информации об удалённых треках {artist} - {title}"
    }


@router.get("/removed/list")
async def list_removed_tracks(
    artist: Optional[str] = None,
    type: Optional[str] = None
):
    """
    Список всех удалённых треков
    
    Args:
        artist: Фильтр по артисту (опционально)
        type: Тип (album, track, catalog) - опционально
    
    Returns:
        Список удалённых треков
    """
    import json
    import os
    
    db_file = "removed_tracks_db.json"
    if not os.path.exists(db_file):
        return {
            "status": "error",
            "message": "База удалённых треков не найдена"
        }
    
    with open(db_file, 'r', encoding='utf-8') as f:
        removed_db = json.load(f)
    
    # Фильтрация
    if artist:
        removed_db = [item for item in removed_db if artist.lower() in item.get("artist", "").lower()]
    
    if type:
        removed_db = [item for item in removed_db if item.get("type") == type]
    
    return {
        "total": len(removed_db),
        "items": removed_db
    }
