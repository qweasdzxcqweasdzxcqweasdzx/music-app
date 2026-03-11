"""
Модели для базы цензурированных треков
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class CensorshipType(str, Enum):
    """Типы цензуры"""
    BLURRED = "blurred"  # Заблюренный звук (beep)
    MUTED = "muted"  # Вырезанный звук (тишина)
    REPLACED = "replaced"  # Заменённое слово
    DELETED = "deleted"  # Трек удалён из платформы
    CLEAN_VERSION = "clean_version"  # Clean/radio версия


class CensorshipSource(str, Enum):
    """Источники информации о цензуре"""
    USER_REPORT = "user_report"  # Сообщение пользователя
    AUTO_DETECT = "auto_detect"  # Автоматическое распознавание
    MANUAL_CHECK = "manual_check"  # Ручная проверка
    API_RESPONSE = "api_response"  # Ответ от API платформы


class CensoredTrack(BaseModel):
    """Модель цензурированного трека"""
    id: Optional[str] = Field(default=None, alias="_id")
    
    # Основная информация
    title: str
    artist: str
    original_title: Optional[str] = None  # Оригинальное название (если отличалось)
    
    # Идентификаторы
    platform_id: str  # ID трека на платформе
    platform: str  # soundcloud, youtube, vk, navidrome
    
    # Информация о цензуре
    censorship_type: CensorshipType
    censorship_source: CensorshipSource = CensorshipSource.AUTO_DETECT
    confidence: float = Field(default=1.0, ge=0, le=1)  # Уверенность (0-1)
    
    # Описание проблемы
    description: Optional[str] = None  # Что именно цензурировано
    timestamp_start: Optional[int] = None  # Секунда начала цензуры
    timestamp_end: Optional[int] = None  # Секунда конца цензуры
    censored_words: List[str] = []  # Список цензурных слов
    
    # Поиск замены
    replacement_found: bool = False
    replacement_track_id: Optional[str] = None  # ID найденной замены
    replacement_url: Optional[str] = None  # URL замены
    replacement_platform: Optional[str] = None
    
    # Статус
    status: str = "pending"  # pending, verified, replaced, false_positive
    verified_by: Optional[str] = None  # Кто проверил
    verified_at: Optional[datetime] = None
    
    # Метаданные
    duration: Optional[int] = None  # Длительность в секундах
    cover: Optional[str] = None  # Обложка
    genres: List[str] = []
    
    # Временные метки
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Дополнительно
    notes: Optional[str] = None  # Заметки
    report_count: int = 0  # Количество жалоб
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CensoredTrackCreate(BaseModel):
    """Модель для создания цензурированного трека"""
    title: str
    artist: str
    original_title: Optional[str] = None
    platform_id: str
    platform: str
    censorship_type: CensorshipType
    description: Optional[str] = None
    timestamp_start: Optional[int] = None
    timestamp_end: Optional[int] = None
    censored_words: List[str] = []
    duration: Optional[int] = None
    cover: Optional[str] = None
    genres: List[str] = []
    notes: Optional[str] = None


class CensoredTrackUpdate(BaseModel):
    """Модель для обновления цензурированного трека"""
    title: Optional[str] = None
    original_title: Optional[str] = None
    censorship_type: Optional[CensorshipType] = None
    description: Optional[str] = None
    replacement_found: Optional[bool] = None
    replacement_track_id: Optional[str] = None
    replacement_url: Optional[str] = None
    replacement_platform: Optional[str] = None
    status: Optional[str] = None
    verified_by: Optional[str] = None
    notes: Optional[str] = None
    report_count: Optional[int] = None


class CensoredTrackSearch(BaseModel):
    """Поиск по базе цензурированных треков"""
    query: Optional[str] = None
    artist: Optional[str] = None
    platform: Optional[str] = None
    censorship_type: Optional[CensorshipType] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0


class CensorshipStatistics(BaseModel):
    """Статистика по цензуре"""
    total_censored: int
    by_type: Dict[str, int]
    by_platform: Dict[str, int]
    by_status: Dict[str, int]
    replacements_found: int
    verified_count: int
    last_updated: datetime
