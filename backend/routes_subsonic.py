"""
Subsonic API Compatibility Layer

Совместимость с клиентами Subsonic:
- DSub (Android)
- Substreamer (iOS)
- Sonos
- Kodi
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List
from datetime import datetime
import hashlib
import random

router = APIRouter(prefix="/rest", tags=["subsonic"])

# ==================== Authentication ====================

def verify_subsonic_auth(username: str, password: str, salt: str, token: str):
    """Проверка аутентификации Subsonic"""
    # Subsonic использует: md5(password + salt)
    expected_token = hashlib.md5((password + salt).encode()).hexdigest()
    return token == expected_token


# ==================== Core API ====================

@router.get("/ping.view")
async def ping():
    """Проверка доступности сервера"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "type": "music-app",
            "serverVersion": "3.1.0"
        }
    }


@router.get("/getArtists.view")
async def get_artists(
    u: str = Query(...),  # username
    t: str = Query(...),  # token
    s: str = Query(...),  # salt
    v: str = Query(...),  # version
    c: str = Query(...)   # client
):
    """Получить список всех артистов"""
    # TODO: Получить из базы данных
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "artists": {
                "index": [
                    {
                        "name": "A",
                        "artist": [
                            {
                                "id": "1",
                                "name": "Artist A",
                                "albumCount": 5,
                                "coverArt": "artist-1"
                            }
                        ]
                    }
                ]
            }
        }
    }


@router.get("/getAlbumList.view")
async def get_album_list(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...),
    type: str = Query("random"),  # random, newest, highest, frequent, recent
    size: int = Query(10),
    offset: int = Query(0)
):
    """Получить список альбомов"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "albumList": {
                "album": [
                    {
                        "id": "1",
                        "name": "Album Name",
                        "artist": "Artist Name",
                        "artistId": "1",
                        "coverArt": "album-1",
                        "year": 2024,
                        "created": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }
    }


@router.get("/getAlbum.view")
async def get_album(
    id: str,
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить информацию об альбоме с треками"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "album": {
                "id": id,
                "name": "Album Name",
                "artist": "Artist Name",
                "year": 2024,
                "song": [
                    {
                        "id": "1",
                        "title": "Track 1",
                        "artist": "Artist Name",
                        "album": "Album Name",
                        "duration": 180,
                        "track": 1,
                        "size": 4500000,
                        "contentType": "audio/mpeg",
                        "path": "Artist/Album/01 - Track 1.mp3"
                    }
                ]
            }
        }
    }


@router.get("/getSong.view")
async def get_song(
    id: str,
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить информацию о треке"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "song": {
                "id": id,
                "title": "Song Title",
                "artist": "Artist Name",
                "album": "Album Name",
                "duration": 180,
                "track": 1,
                "year": 2024,
                "genre": "Rock",
                "size": 4500000,
                "contentType": "audio/mpeg"
            }
        }
    }


@router.get("/stream.view")
async def stream(
    id: str,
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить аудио поток"""
    # TODO: Вернуть аудио файл
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/download.view")
async def download(
    id: str,
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Скачать трек"""
    raise HTTPException(status_code=501, detail="Not implemented yet")


# ==================== Search ====================

@router.get("/search2.view")
async def search2(
    query: str,
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...),
    artistCount: int = Query(20),
    albumCount: int = Query(20),
    songCount: int = Query(20)
):
    """Поиск по библиотеке"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "searchResult2": {
                "artist": [
                    {"id": "1", "name": "Artist"}
                ],
                "album": [
                    {"id": "1", "name": "Album", "artist": "Artist"}
                ],
                "song": [
                    {
                        "id": "1",
                        "title": "Song",
                        "artist": "Artist",
                        "album": "Album",
                        "duration": 180
                    }
                ]
            }
        }
    }


# ==================== Playlists ====================

@router.get("/getPlaylists.view")
async def get_playlists(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить список плейлистов"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "playlists": {
                "playlist": [
                    {
                        "id": "1",
                        "name": "My Playlist",
                        "songCount": 10,
                        "duration": 1800,
                        "created": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }
    }


@router.get("/getPlaylist.view")
async def get_playlist(
    id: str,
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить плейлист с треками"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "playlist": {
                "id": id,
                "name": "My Playlist",
                "songCount": 10,
                "duration": 1800,
                "entry": [
                    {
                        "id": "1",
                        "title": "Track 1",
                        "artist": "Artist",
                        "duration": 180
                    }
                ]
            }
        }
    }


# ==================== Scrobbling ====================

@router.get("/scrobble.view")
async def scrobble(
    id: str,
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...),
    submission: Optional[bool] = Query(None),
    time: Optional[int] = Query(None)
):
    """Scrobble прослушивания (Last.fm совместимость)"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1"
        }
    }


# ==================== Bookmarks ====================

@router.get("/getBookmarks.view")
async def get_bookmarks(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить закладки (позиции воспроизведения)"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "bookmarks": {
                "bookmark": []
            }
        }
    }


# ==================== Genres ====================

@router.get("/getGenres.view")
async def get_genres(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить список жанров"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "genres": {
                "genre": [
                    {"value": "Rock", "albumCount": 100, "songCount": 1000},
                    {"value": "Pop", "albumCount": 80, "songCount": 800},
                    {"value": "Jazz", "albumCount": 50, "songCount": 500}
                ]
            }
        }
    }


# ==================== Now Playing ====================

@router.get("/getNowPlaying.view")
async def get_now_playing(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить текущие воспроизведения"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "nowPlaying": {
                "entry": []
            }
        }
    }


# ==================== Star Rating ====================

@router.get("/star.view")
async def star(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...),
    id: Optional[List[str]] = None,
    albumId: Optional[List[str]] = None,
    artistId: Optional[List[str]] = None
):
    """Добавить звезду (лайк)"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1"
        }
    }


@router.get("/unstar.view")
async def unstar(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...),
    id: Optional[List[str]] = None,
    albumId: Optional[List[str]] = None,
    artistId: Optional[List[str]] = None
):
    """Убрать звезду"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1"
        }
    }


# ==================== Index ====================

@router.get("/getIndex.view")
async def get_index(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...),
    musicFolderId: Optional[int] = Query(None)
):
    """Получить индекс артистов (A-Z)"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "artists": {
                "index": [
                    {
                        "name": "A",
                        "artist": [
                            {"id": "1", "name": "Artist A"}
                        ]
                    },
                    {
                        "name": "B",
                        "artist": [
                            {"id": "2", "name": "Artist B"}
                        ]
                    }
                ]
            }
        }
    }


# ==================== Music Folders ====================

@router.get("/getMusicFolders.view")
async def get_music_folders(
    u: str = Query(...),
    t: str = Query(...),
    s: str = Query(...),
    v: str = Query(...),
    c: str = Query(...)
):
    """Получить музыкальные папки"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "musicFolders": {
                "musicFolder": [
                    {"id": 1, "name": "Music"}
                ]
            }
        }
    }
