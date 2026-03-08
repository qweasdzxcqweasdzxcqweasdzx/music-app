from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# ==================== Треки ====================

class Track(BaseModel):
    """Модель трека"""
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    artist: str
    artist_id: Optional[str] = None
    duration: int  # в секундах
    stream_url: str
    preview_url: Optional[str] = None
    cover: Optional[str] = None
    source: str = "soundcloud"  # soundcloud, vk, youtube, navidrome
    is_explicit: bool = False
    is_censored: bool = False
    original_track_id: Optional[str] = None
    play_count: int = 0
    popularity: int = 0  # 0-100
    album: Optional[str] = None
    album_id: Optional[str] = None
    genres: List[str] = []
    release_date: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class TrackSearch(BaseModel):
    """Поиск треков"""
    query: str
    limit: int = 20
    offset: int = 0


# ==================== Артисты ====================

class Artist(BaseModel):
    """Модель артиста"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    cover: Optional[str] = None
    banner: Optional[str] = None
    description: Optional[str] = None
    genres: List[str] = []
    subscribers_count: int = 0
    followers: int = 0
    popularity: int = 0  # 0-100
    tracks: List[str] = []  # ID треков
    albums: List[Dict] = []
    singles: List[Dict] = []
    appears_on: List[Dict] = []
    similar_artists: List[str] = []  # ID артистов
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ArtistSearch(BaseModel):
    """Поиск артистов"""
    query: str
    limit: int = 20


# ==================== Альбомы ====================

class Album(BaseModel):
    """Модель альбома"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    cover: Optional[str] = None
    banner: Optional[str] = None
    release_date: Optional[str] = None
    total_tracks: int = 0
    album_type: str = "album"  # album, single, compilation, appears_on
    artists: List[Dict] = []  # [{id, name}]
    tracks: List[Track] = []
    label: Optional[str] = None
    copyrights: List[Dict] = []
    genres: List[str] = []
    popularity: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class AlbumSearch(BaseModel):
    """Поиск альбомов"""
    query: str
    limit: int = 20


# ==================== Синглы ====================

class Single(BaseModel):
    """Модель сингла"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    cover: Optional[str] = None
    release_date: Optional[str] = None
    total_tracks: int = 1
    artists: List[Dict] = []
    tracks: List[Track] = []
    label: Optional[str] = None
    popularity: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


# ==================== Плейлисты ====================

class Playlist(BaseModel):
    """Модель плейлиста"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    name: str
    description: Optional[str] = None
    cover: Optional[str] = None
    tracks: List[str] = []  # ID треков
    is_public: bool = False
    is_collaborative: bool = False
    followers: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class PlaylistCreate(BaseModel):
    """Создание плейлиста"""
    name: str
    description: Optional[str] = None
    is_public: bool = False


class PlaylistUpdate(BaseModel):
    """Обновление плейлиста"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover: Optional[str] = None


# ==================== Пользователи ====================

class User(BaseModel):
    """Модель пользователя"""
    id: Optional[str] = Field(default=None, alias="_id")
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_premium: bool = False
    favorite_genres: List[str] = []
    top_artists: List[str] = []  # ID артистов

    class Config:
        populate_by_name = True


class UserCreate(BaseModel):
    """Создание пользователя"""
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# ==================== История и лайки ====================

class PlayHistory(BaseModel):
    """История прослушиваний"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    track_id: str
    played_at: datetime = Field(default_factory=datetime.utcnow)
    play_duration: int = 0  # сколько секунд прослушано
    completed: bool = False  # прослушан ли трек полностью


class Like(BaseModel):
    """Лайки"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    track_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== Поиск ====================

class SearchResponse(BaseModel):
    """Результаты поиска"""
    tracks: List[Track] = []
    artists: List[Artist] = []
    albums: List[Album] = []
    singles: List[Single] = []
    playlists: List[Playlist] = []
    total: int = 0


class SearchAllResponse(BaseModel):
    """Результаты поиска по всем категориям"""
    tracks: List[Track] = []
    artists: List[Dict] = []
    albums: List[Dict] = []
    total_tracks: int = 0
    total_artists: int = 0
    total_albums: int = 0


# ==================== Рекомендации ====================

class RecommendationRequest(BaseModel):
    """Запрос рекомендаций"""
    seed_artists: Optional[List[str]] = None
    seed_tracks: Optional[List[str]] = None
    seed_genres: Optional[List[str]] = None
    limit: int = 20
    target_energy: Optional[float] = None
    target_danceability: Optional[float] = None
    target_valence: Optional[float] = None


class RecommendationResponse(BaseModel):
    """Ответ с рекомендациями"""
    tracks: List[Track]
    seeds: Dict[str, Any]
    total: int


# ==================== Жанры ====================

class Genre(BaseModel):
    """Модель жанра"""
    id: str
    name: str
    cover: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class GenreResponse(BaseModel):
    """Список жанров"""
    genres: List[Genre]
    total: int


# ==================== Charts ====================

class ChartTrack(BaseModel):
    """Трек в чарте"""
    track: Track
    position: int
    previous_position: Optional[int] = None
    weeks_on_chart: int = 1
    peak_position: int = 1


class ChartResponse(BaseModel):
    """Чарт"""
    name: str
    description: str
    tracks: List[ChartTrack]
    updated_at: datetime
    total: int
