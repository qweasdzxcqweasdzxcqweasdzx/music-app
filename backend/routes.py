from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta

from models import (
    User, UserCreate, Track, Playlist, PlaylistCreate,
    SearchResponse, SearchAllResponse, Artist, Album, Single,
    RecommendationRequest, RecommendationResponse, GenreResponse, Genre
)
from database import get_collection
from auth import create_access_token, verify_telegram_data, decode_access_token
from config import settings
from services.music_service import music_service
from services.soundcloud_service import soundcloud_service
from services.soundcloud_source_adapter import soundcloud_source
from services.recommendation_service import recommendation_service

router = APIRouter(prefix="/api", tags=["main"])
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Получение текущего пользователя из токена"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload


# ==================== Аутентификация ====================

@router.post("/auth/telegram")
async def telegram_auth(init_data: str):
    """Аутентификация через Telegram WebApp"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Telegram bot token not configured")

    user_data = verify_telegram_data(init_data, settings.TELEGRAM_BOT_TOKEN)

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid Telegram data")

    users_collection = await get_collection("users")
    telegram_id = str(user_data.get("id"))

    existing_user = await users_collection.find_one({"telegram_id": telegram_id})

    if existing_user:
        await users_collection.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {
                "username": user_data.get("username"),
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
            }}
        )
        user_id = str(existing_user["_id"])
    else:
        user = UserCreate(
            telegram_id=telegram_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name")
        )
        result = await users_collection.insert_one(user.dict())
        user_id = str(result.inserted_id)

    access_token = create_access_token(
        data={"sub": user_id, "telegram_id": telegram_id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "telegram_id": telegram_id,
            "username": user_data.get("username"),
        }
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Данные текущего пользователя"""
    users_collection = await get_collection("users")
    user = await users_collection.find_one({"telegram_id": current_user["telegram_id"]})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user["_id"]),
        "telegram_id": user["telegram_id"],
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "is_premium": user.get("is_premium", False),
    }


# ==================== Поиск ====================

@router.get("/search", response_model=SearchAllResponse)
async def search(
    q: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    type: str = Query("all", description="Тип: all, tracks, artists, albums")
):
    """
    Поиск по всем источникам (SoundCloud + VK + YouTube)
    """
    # Поиск через SoundCloud (основной источник)
    soundcloud_results = await soundcloud_service.search(q, limit=limit, offset=offset)

    # Поиск через VK (резерв)
    vk_tracks = await music_service.vk.search(q, limit=limit // 2)

    # Объединение результатов
    all_tracks = soundcloud_results.get("tracks", []) + vk_tracks

    return {
        "tracks": all_tracks[:limit],
        "artists": soundcloud_results.get("users", [])[:limit // 2],
        "playlists": soundcloud_results.get("playlists", [])[:limit // 2],
        "total_tracks": len(all_tracks),
        "total_artists": len(soundcloud_results.get("users", [])),
        "total_playlists": len(soundcloud_results.get("playlists", []))
    }


# ==================== Треки ====================

@router.get("/tracks/{track_id}")
async def get_track(track_id: str):
    """Получение трека по ID"""
    track = await soundcloud_service.get_track(track_id)

    if not track:
        # Пробуем VK
        track = await music_service.get_track(track_id)

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    return track


@router.get("/tracks/{track_id}/stream")
async def get_track_stream(track_id: str):
    """Получение URL потока для трека (полноценное аудио)"""
    from services.audio_streaming_service import audio_streaming_service

    # Получаем трек из SoundCloud
    track = await soundcloud_service.get_track(track_id)

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Пробуем получить полноценное аудио
    audio_data = await audio_streaming_service.get_audio_url(track)

    if audio_data:
        return {
            "stream_url": audio_data["url"],
            "track": track,
            "is_preview": audio_data.get("is_preview", False),
            "source": audio_data.get("source", "unknown"),
            "duration": audio_data.get("duration", track.duration)
        }
    else:
        # Fallback на превью
        return {
            "stream_url": track.preview_url or track.stream_url,
            "track": track,
            "is_preview": True,
            "source": "soundcloud",
            "duration": 30
        }


# ==================== Артисты ====================

@router.get("/artists/{artist_id}", response_model=Artist)
async def get_artist(artist_id: str):
    """Получение информации об артисте"""
    artist = await soundcloud_service.get_user(artist_id)

    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    return artist


@router.get("/artists/{artist_id}/tracks")
async def get_artist_top_tracks(
    artist_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Популярные треки артиста"""
    tracks = await soundcloud_service.get_user_tracks(artist_id)
    return {"tracks": tracks[:limit]}


@router.get("/artists/{artist_id}/albums")
async def get_artist_albums(
    artist_id: str,
    include_groups: str = Query("album,single", description="album,single,appears_on"),
    limit: int = Query(20, ge=1, le=50)
):
    """Альбомы и синглы артиста"""
    albums = await soundcloud_service.get_user_playlists(artist_id)
    return {"albums": albums, "total": len(albums)}


@router.get("/artists/{artist_id}/recommendations")
async def get_artist_recommendations(
    artist_id: str,
    limit: int = Query(20, ge=1, le=50)
):
    """Похожие артисты и рекомендации"""
    tracks = await recommendation_service.get_artist_recommendations(
        artist_id,
        limit=limit
    )
    return {"tracks": tracks, "total": len(tracks)}


# ==================== Альбомы ====================

@router.get("/albums/{album_id}")
async def get_album(album_id: str):
    """Получение альбома"""
    album = await soundcloud_service.get_playlist(album_id)

    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    return album


@router.get("/albums/{album_id}/tracks")
async def get_album_tracks(
    album_id: str,
    limit: int = Query(50, ge=1, le=50)
):
    """Треки альбома"""
    album = await soundcloud_service.get_playlist(album_id)
    if album:
        return {"tracks": album.get("tracks", [])[:limit], "total": len(album.get("tracks", []))}
    return {"tracks": [], "total": 0}


# ==================== Синглы ====================

@router.get("/singles/{single_id}")
async def get_single(single_id: str):
    """Получение сингла"""
    # Сингл - это плейлист с 1 треком
    album = await soundcloud_service.get_playlist(single_id)

    if not album:
        raise HTTPException(status_code=404, detail="Single not found")

    if album.get("track_count", 0) > 1:
        raise HTTPException(status_code=400, detail="Not a single")

    return album


# ==================== Рекомендации ====================

@router.get("/recommendations")
async def get_recommendations(
    seed_artists: Optional[str] = Query(None, description="CSV artist IDs"),
    seed_tracks: Optional[str] = Query(None, description="CSV track IDs"),
    seed_genres: Optional[str] = Query(None, description="CSV genres"),
    limit: int = Query(20, ge=1, le=50)
):
    """Рекомендации на основе seed"""
    tracks = await recommendation_service.get_recommendations(
        seed_artists=seed_artists.split(",") if seed_artists else None,
        seed_tracks=seed_tracks.split(",") if seed_tracks else None,
        seed_genres=seed_genres.split(",") if seed_genres else None,
        limit=limit
    )
    return {"tracks": tracks, "total": len(tracks)}


@router.get("/recommendations/for-you")
async def get_personalized_recommendations(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=50)
):
    """Персональные рекомендации для пользователя"""
    user_id = current_user["telegram_id"]
    tracks = await recommendation_service.get_recommendations_for_user(
        user_id,
        limit=limit
    )
    return {"tracks": tracks, "total": len(tracks)}


@router.get("/recommendations/mood/{mood}")
async def get_mood_recommendations(
    mood: str,
    limit: int = Query(20, ge=1, le=50)
):
    """
    Рекомендации по настроению
    
    mood: happy, sad, energetic, chill, focus
    """
    valid_moods = ["happy", "sad", "energetic", "chill", "focus"]
    if mood not in valid_moods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mood. Valid: {', '.join(valid_moods)}"
        )
    
    tracks = await recommendation_service.get_mood_recommendations(
        mood,
        limit=limit
    )
    return {"tracks": tracks, "total": len(tracks)}


# ==================== Жанры ====================

@router.get("/genres")
async def get_genres():
    """Список доступных жанров"""
    # Получаем жанры из SoundCloud
    soundcloud_genres = await soundcloud_source.get_genres()

    # Красивые названия для жанров
    genre_names = {
        "electronic": "Electronic",
        "hip-hop-rap": "Hip-Hop & Rap",
        "indie": "Indie",
        "pop": "Pop",
        "rock": "Rock",
        "ambient": "Ambient",
        "jazz": "Jazz",
        "classical": "Classical",
        "metal": "Metal",
        "r-n-b": "R&B",
        "soul": "Soul",
        "funk": "Funk",
        "blues": "Blues",
        "country": "Country",
        "reggae": "Reggae",
        "latin": "Latin",
        "house": "House",
        "techno": "Techno",
        "trance": "Trance",
        "dubstep": "Dubstep",
    }

    # Цвета для жанров (SoundCloud orange вместо Spotify green)
    genre_colors = {
        "electronic": "#ff5500",
        "hip-hop-rap": "#DC148C",
        "indie": "#608108",
        "pop": "#ff5500",
        "rock": "#E91429",
        "ambient": "#0D73EC",
        "jazz": "#477D95",
        "classical": "#8C67AC",
        "metal": "#BC5900",
    }

    genres = []
    for genre in soundcloud_genres:
        genre_id = genre["id"]
        genres.append({
            "id": genre_id,
            "name": genre_names.get(genre_id, genre["name"]),
            "cover": f"https://picsum.photos/seed/{genre_id}/300/300",
            "color": genre_colors.get(genre_id, "#ff5500"),
            "source": "soundcloud"
        })

    return {"genres": genres, "total": len(genres)}


@router.get("/genres/{genre_id}")
async def get_genre_tracks(
    genre_id: str,
    limit: int = Query(20, ge=1, le=50)
):
    """Треки по жанру"""
    tracks = await soundcloud_source.get_tracks_by_genre(genre_id, limit)
    return {"tracks": tracks, "total": len(tracks)}


# ==================== Чарты и популярное ====================

@router.get("/top")
async def get_top_tracks(
    limit: int = Query(20, ge=1, le=50),
):
    """Популярные треки (чарт)"""
    # Получаем трендовые треки из SoundCloud
    tracks = await soundcloud_service.get_trending(limit=limit)
    return {"tracks": tracks[:limit], "total": len(tracks)}


@router.get("/new")
async def get_new_releases(
    limit: int = Query(20, ge=1, le=50)
):
    """Новые релизы"""
    # Получаем новые и горячие треки из SoundCloud
    tracks = await soundcloud_service.get_new_hot(limit=limit)
    return {"tracks": tracks, "total": len(tracks)}


@router.get("/featured")
async def get_featured_playlists(
    limit: int = Query(10, ge=1, le=50)
):
    """Популярные плейлисты"""
    # SoundCloud не имеет прямого API для featured playlists
    # Используем поиск по популярным плейлистам
    result = await soundcloud_service.search("top hits 2026", limit=limit)
    playlists = result.get("playlists", [])
    return {"playlists": playlists, "total": len(playlists)}


# ==================== Плейлисты ====================

@router.post("/playlists")
async def create_playlist(
    playlist: PlaylistCreate,
    current_user: dict = Depends(get_current_user)
):
    """Создание плейлиста"""
    playlists_collection = await get_collection("playlists")

    new_playlist = Playlist(
        user_id=current_user["telegram_id"],
        name=playlist.name,
        description=playlist.description,
        is_public=playlist.is_public
    )

    result = await playlists_collection.insert_one(new_playlist.dict())

    return {
        "id": str(result.inserted_id),
        **new_playlist.dict()
    }


@router.get("/playlists")
async def get_playlists(current_user: dict = Depends(get_current_user)):
    """Плейлисты пользователя"""
    playlists_collection = await get_collection("playlists")

    playlists = await playlists_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=100)

    return [{"id": str(p["_id"]), **p} for p in playlists]


@router.get("/playlists/{playlist_id}")
async def get_playlist(playlist_id: str, current_user: dict = Depends(get_current_user)):
    """Плейлист по ID"""
    playlists_collection = await get_collection("playlists")

    playlist = await playlists_collection.find_one({"_id": ObjectId(playlist_id)})

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    return {"id": str(playlist["_id"]), **playlist}


@router.put("/playlists/{playlist_id}")
async def update_playlist(
    playlist_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user)
):
    """Обновление плейлиста"""
    playlists_collection = await get_collection("playlists")

    await playlists_collection.update_one(
        {"_id": ObjectId(playlist_id), "user_id": current_user["telegram_id"]},
        {"$set": updates}
    )

    return {"status": "ok"}


@router.delete("/playlists/{playlist_id}")
async def delete_playlist(playlist_id: str, current_user: dict = Depends(get_current_user)):
    """Удаление плейлиста"""
    playlists_collection = await get_collection("playlists")

    await playlists_collection.delete_one({
        "_id": ObjectId(playlist_id),
        "user_id": current_user["telegram_id"]
    })

    return {"status": "ok"}


@router.post("/playlists/{playlist_id}/tracks")
async def add_track_to_playlist(
    playlist_id: str,
    track_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Добавление трека в плейлист"""
    playlists_collection = await get_collection("playlists")

    await playlists_collection.update_one(
        {"_id": ObjectId(playlist_id), "user_id": current_user["telegram_id"]},
        {"$addToSet": {"tracks": track_id}}
    )

    return {"status": "ok"}


@router.delete("/playlists/{playlist_id}/tracks/{track_id}")
async def remove_track_from_playlist(
    playlist_id: str,
    track_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Удаление трека из плейлиста"""
    playlists_collection = await get_collection("playlists")

    await playlists_collection.update_one(
        {"_id": ObjectId(playlist_id), "user_id": current_user["telegram_id"]},
        {"$pull": {"tracks": track_id}}
    )

    return {"status": "ok"}


# ==================== История и лайки ====================

@router.get("/history")
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """История прослушиваний"""
    history_collection = await get_collection("play_history")

    history = await history_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).sort("played_at", -1).limit(limit).to_list(length=limit)

    return [{"id": str(h["_id"]), **h} for h in history]


@router.post("/history")
async def add_to_history(
    track_id: str,
    play_duration: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Добавление в историю"""
    from models import PlayHistory
    from datetime import datetime

    history_collection = await get_collection("play_history")

    history = PlayHistory(
        user_id=current_user["telegram_id"],
        track_id=track_id,
        play_duration=play_duration
    )

    await history_collection.insert_one(history.dict())

    return {"status": "ok"}


@router.get("/likes")
async def get_likes(current_user: dict = Depends(get_current_user)):
    """Любимые треки"""
    likes_collection = await get_collection("likes")

    likes = await likes_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=1000)

    return [str(like["track_id"]) for like in likes]


@router.post("/likes/{track_id}")
async def add_like(
    track_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Добавление лайка"""
    from models import Like

    likes_collection = await get_collection("likes")

    like = Like(
        user_id=current_user["telegram_id"],
        track_id=track_id
    )

    await likes_collection.insert_one(like.dict())

    return {"status": "ok"}


@router.delete("/likes/{track_id}")
async def remove_like(
    track_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Удаление лайка"""
    likes_collection = await get_collection("likes")

    await likes_collection.delete_one({
        "user_id": current_user["telegram_id"],
        "track_id": track_id
    })

    return {"status": "ok"}


# ==================== Очередь (Queue) ====================

@router.get("/queue")
async def get_queue(current_user: dict = Depends(get_current_user)):
    """Текущая очередь воспроизведения"""
    # В реальности нужно хранить в Redis
    # Для тестов - заглушка
    return {
        "currently_playing": None,
        "queue": [],
        "total": 0
    }


@router.post("/queue")
async def add_to_queue(
    track_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Добавить трек в очередь"""
    # В реальности нужно добавлять в Redis
    return {"status": "ok", "message": "Track added to queue"}


@router.delete("/queue/{track_id}")
async def remove_from_queue(
    track_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Удалить трек из очереди"""
    return {"status": "ok"}


@router.post("/queue/clear")
async def clear_queue(current_user: dict = Depends(get_current_user)):
    """Очистить очередь"""
    return {"status": "ok"}


# ==================== Устройства (Devices) ====================

@router.get("/devices")
async def get_devices(current_user: dict = Depends(get_current_user)):
    """Список доступных устройств для воспроизведения"""
    # Заглушка - в реальности нужно интеграция с устройствами
    return {
        "devices": [
            {
                "id": "web_player",
                "name": "Web Player",
                "type": "computer",
                "is_active": True
            }
        ],
        "total": 1
    }


@router.post("/playback/transfer")
async def transfer_playback(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Переключить воспроизведение на другое устройство"""
    # В реальности нужна интеграция с устройствами
    return {"status": "ok", "device_id": device_id}


# ==================== Тексты песен (Lyrics) ====================

@router.get("/tracks/{track_id}/lyrics")
async def get_lyrics(
    track_id: str,
    track_title: Optional[str] = Query(None),
    artist_name: Optional[str] = Query(None)
):
    """Получить текст песни"""
    from services.lyrics_service import genius_service, lyrics_ovh_service
    
    # Пробуем получить текст через Genius
    if track_title and artist_name:
        lyrics_data = await genius_service.get_track_lyrics(track_title, artist_name)
        if lyrics_data:
            return lyrics_data
    
    # Если не получилось, пробуем Lyrics OVH (без токена)
    if track_title and artist_name:
        lyrics = await lyrics_ovh_service.get_lyrics(artist_name, track_title)
        if lyrics:
            return {
                "track_id": track_id,
                "title": track_title,
                "artist": artist_name,
                "lyrics": lyrics,
                "synced": False,
                "provider": "Lyrics OVH"
            }
    
    # Заглушка если ничего не найдено
    return {
        "track_id": track_id,
        "lyrics": "Текст песни недоступен\n\nЭто заглушка для демонстрации.\nВ продакшене здесь будет текст из Musixmatch или Genius API.",
        "synced": False,
        "provider": "Musixmatch"
    }


# ==================== Daily Mixes ====================

@router.get("/daily-mixes")
async def get_daily_mixes(current_user: dict = Depends(get_current_user)):
    """Персональные ежедневные миксы"""
    from services.daily_mixes_service import daily_mixes_service
    from database import get_collection
    
    # Получаем данные пользователя
    history_collection = await get_collection("play_history")
    likes_collection = await get_collection("likes")
    
    history = await history_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=300)
    
    likes = await likes_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=500)
    
    like_track_ids = [like["track_id"] for like in likes]
    
    # Генерируем миксы
    mixes = await daily_mixes_service.generate_daily_mixes(
        user_id=current_user["telegram_id"],
        history=history,
        likes=like_track_ids,
        top_artists=[]  # Можно получить из профиля
    )
    
    return {
        "mixes": mixes,
        "total": len(mixes),
        "generated_at": datetime.now().isoformat(),
        "expires_at": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).isoformat()
    }


# ==================== Release Radar ====================

@router.get("/release-radar")
async def get_release_radar(current_user: dict = Depends(get_current_user)):
    """Новые релизы любимых артистов"""
    from services.release_radar_service import release_radar_service
    from database import get_collection
    
    # Получаем данные пользователя
    history_collection = await get_collection("play_history")
    likes_collection = await get_collection("likes")
    
    history = await history_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=300)
    
    likes = await likes_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=500)
    
    like_track_ids = [like["track_id"] for like in likes]
    
    # Генерируем Release Radar
    radar = await release_radar_service.generate_release_radar(
        user_id=current_user["telegram_id"],
        history=history,
        likes=like_track_ids,
        top_artists=[]
    )
    
    return radar


# ==================== Discover Weekly ====================

@router.get("/discover-weekly")
async def get_discover_weekly(current_user: dict = Depends(get_current_user)):
    """Еженедельные рекомендации"""
    from services.discover_weekly_service import discover_weekly_service
    from database import get_collection
    
    # Получаем данные пользователя
    history_collection = await get_collection("play_history")
    likes_collection = await get_collection("likes")
    
    history = await history_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=300)
    
    likes = await likes_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=500)
    
    like_track_ids = [like["track_id"] for like in likes]
    
    # Генерируем Discover Weekly
    weekly = await discover_weekly_service.generate_discover_weekly(
        user_id=current_user["telegram_id"],
        history=history,
        likes=like_track_ids,
        top_artists=[],
        top_genres=[]
    )
    
    return weekly


# ==================== Статистика ====================

@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Статистика прослушиваний"""
    history_collection = await get_collection("play_history")
    
    # Подсчёт статистики
    total_plays = await history_collection.count_documents({"user_id": current_user["telegram_id"]})
    
    return {
        "total_plays": total_plays,
        "total_minutes": total_plays * 3,  # Приблизительно
        "top_artists": [],
        "top_genres": [],
        "recent_activity": "active"
    }


# ==================== Jam Session (совместное прослушивание) ====================

@router.post("/jam")
async def create_jam(current_user: dict = Depends(get_current_user)):
    """Создать сессию совместного прослушивания"""
    import uuid
    session_id = str(uuid.uuid4())
    
    return {
        "session_id": session_id,
        "join_url": f"https://t.me/music_bot?startapp=jam_{session_id}",
        "code": session_id[:8].upper()
    }


@router.get("/jam/{session_id}")
async def get_jam_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Информация о сессии"""
    return {
        "session_id": session_id,
        "host": "user_123",
        "participants": 1,
        "currently_playing": None
    }


@router.post("/jam/{session_id}/join")
async def join_jam_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Присоединиться к сессии"""
    return {"status": "ok", "session_id": session_id}


@router.post("/jam/{session_id}/leave")
async def leave_jam_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Покинуть сессию"""
    return {"status": "ok"}


# ==================== Smart Mixer (Умный миксер) ====================

@router.get("/mixer/smart")
async def get_smart_mix(
    limit: int = Query(50, ge=10, le=100),
    sources: Optional[str] = Query(None, description="CSV источников"),
    current_user: dict = Depends(get_current_user)
):
    """
    Создание умного микса на основе предпочтений пользователя
    """
    from services.smart_mixer_service import smart_mixer
    from database import get_collection

    # Получение данных пользователя
    history_collection = await get_collection("play_history")
    likes_collection = await get_collection("likes")

    history = await history_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=300)

    likes = await likes_collection.find(
        {"user_id": current_user["telegram_id"]}
    ).to_list(length=500)

    like_track_ids = [like["track_id"] for like in likes]

    # Генерация микса
    source_list = sources.split(",") if sources else None
    tracks = await smart_mixer.create_smart_mix(
        user_id=current_user["telegram_id"],
        history=history,
        likes=like_track_ids,
        top_artists=[],
        limit=limit,
        sources=source_list
    )

    return {
        "mix_type": "smart",
        "tracks": [
            {
                "id": t.id,
                "title": t.title,
                "artist": t.artist,
                "source": t.source,
                "cover": t.cover,
                "duration": t.duration
            }
            for t in tracks
        ],
        "total": len(tracks),
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/mixer/radio/{track_id}")
async def get_infinite_radio(
    track_id: str,
    limit: int = Query(50, ge=10, le=100),
    source: str = Query("soundcloud", description="Источник трека")
):
    """
    Бесконечное радио на основе трека
    """
    from services.smart_mixer_service import smart_mixer
    from services.soundcloud_service import soundcloud_service

    # Получение seed трека
    track = await soundcloud_service.get_track(track_id)

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    tracks = await smart_mixer.create_infinite_radio(
        seed_track=track,
        limit=limit
    )

    return {
        "mix_type": "radio",
        "seed_track": {
            "id": track.id,
            "title": track.title,
            "artist": track.artist,
            "cover": track.cover
        },
        "tracks": [
            {
                "id": t.id,
                "title": t.title,
                "artist": t.artist,
                "source": t.source,
                "cover": t.cover,
                "duration": t.duration
            }
            for t in tracks
        ],
        "total": len(tracks)
    }


@router.get("/mixer/mood/{mood}")
async def get_mood_mix(
    mood: str,
    limit: int = Query(30, ge=10, le=100)
):
    """
    Микс по настроению

    mood: happy, sad, energetic, chill, focus
    """
    from services.smart_mixer_service import smart_mixer

    tracks = await smart_mixer.create_mood_mix(mood, limit)

    return {
        "mix_type": "mood",
        "mood": mood,
        "tracks": [
            {
                "id": t.id,
                "title": t.title,
                "artist": t.artist,
                "source": t.source,
                "cover": t.cover,
                "duration": t.duration
            }
            for t in tracks
        ],
        "total": len(tracks)
    }


@router.get("/mixer/genre/{genre}")
async def get_genre_mix(
    genre: str,
    limit: int = Query(40, ge=10, le=100),
    sources: Optional[str] = Query(None, description="CSV источников")
):
    """
    Микс по жанру
    """
    from services.smart_mixer_service import smart_mixer

    source_list = sources.split(",") if sources else None
    tracks = await smart_mixer.create_genre_mix(genre, limit, source_list)

    return {
        "mix_type": "genre",
        "genre": genre,
        "tracks": [
            {
                "id": t.id,
                "title": t.title,
                "artist": t.artist,
                "source": t.source,
                "cover": t.cover,
                "duration": t.duration
            }
            for t in tracks
        ],
        "total": len(tracks)
    }


# ==================== AI Generation ====================

@router.post("/ai/generate")
async def generate_music(
    provider: str,
    prompt: str,
    tags: Optional[str] = None,
    title: Optional[str] = None,
    duration: Optional[int] = None,
    mood: Optional[str] = None,
    genre: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Генерация музыки через AI сервисы

    provider: suno, mubert, musicgen
    prompt: Описание музыки
    """
    from services.ai_music_service import ai_music_service

    if provider == "suno":
        result = await ai_music_service.suno_generate(
            prompt=prompt,
            tags=tags,
            title=title,
            make_instrumental=False
        )
    elif provider == "mubert":
        result = await ai_music_service.mubert_generate(
            prompt=prompt,
            duration=duration or 60,
            mood=mood,
            genre=genre
        )
    elif provider == "musicgen":
        result = await ai_music_service.musicgen_generate(
            prompt=prompt,
            duration=duration or 10
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "task_id": result.get("task_id"),
        "status": result.get("status"),
        "provider": provider,
        "prompt": prompt
    }


@router.get("/ai/status/{task_id}")
async def get_generation_status(
    task_id: str,
    provider: str = Query(..., description="Провайдер: suno, mubert, lalal")
):
    """
    Получение статуса задачи генерации
    """
    from services.ai_music_service import ai_music_service

    result = await ai_music_service.get_generation_status(provider, task_id)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/ai/separate")
async def separate_stems(
    audio_url: str,
    stem_type: str = Query("vocals", description="Тип стема: vocals, instrumental, drums, bass"),
    provider: str = Query("lalal", description="Провайдер"),
    current_user: dict = Depends(get_current_user)
):
    """
    Разделение трека на стемы
    """
    from services.ai_music_service import ai_music_service

    result = await ai_music_service.separate_stems(audio_url, stem_type, provider)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "task_id": result.get("task_id"),
        "status": result.get("status"),
        "stem_type": stem_type
    }


@router.post("/ai/voice")
async def generate_voice(
    text: str,
    voice_id: Optional[str] = "21m00Tcm4TlvDq8ikWAM",
    provider: str = Query("elevenlabs", description="Провайдер"),
    current_user: dict = Depends(get_current_user)
):
    """
    Синтез голоса через AI
    """
    from services.ai_music_service import ai_music_service

    result = await ai_music_service.generate_voice(text, voice_id, provider)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "status": result.get("status"),
        "audio_base64": result.get("audio_base64"),
        "voice_id": voice_id,
        "provider": provider
    }


@router.get("/ai/voices")
async def get_available_voices(provider: str = "elevenlabs"):
    """
    Получение списка доступных голосов
    """
    from services.ai_music_service import ai_music_service

    if provider == "elevenlabs":
        voices = await ai_music_service.elevenlabs_get_voices()
        return {"voices": voices}

    raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")


# ==================== Celery Tasks (фоновые задачи) ====================

@router.post("/tasks/generate-mix")
async def generate_mix_task(
    user_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Фоновая генерация умного микса через Celery
    """
    from celery_worker import generate_smart_mix

    task = generate_smart_mix.delay(
        user_id=current_user["telegram_id"],
        limit=limit
    )

    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Mix generation started"
    }


@router.get("/tasks/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Статус фоновой задачи
    """
    from celery.result import AsyncResult
    from celery_worker import celery_app

    task = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
