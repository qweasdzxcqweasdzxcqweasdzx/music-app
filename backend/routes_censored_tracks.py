"""
API Endpoints для управления базой цензурированных треков
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from datetime import datetime

from models.censored_tracks import (
    CensoredTrack,
    CensoredTrackCreate,
    CensoredTrackUpdate,
    CensoredTrackSearch,
    CensorshipType,
    CensorshipStatistics,
)
from services.censored_tracks_service import censored_tracks_db


router = APIRouter(prefix="/api/censored-tracks", tags=["Censored Tracks"])


@router.get("/stats", response_model=CensorshipStatistics)
async def get_statistics():
    """
    Получить статистику по базе цензурированных треков
    
    Возвращает:
    - Общее количество треков
    - Распределение по типам цензуры
    - Распределение по платформам
    - Распределение по статусам
    - Количество найденных замен
    - Количество проверенных треков
    """
    return censored_tracks_db.get_statistics()


@router.get("/search", response_model=List[dict])
async def search_tracks(
    q: Optional[str] = Query(None, description="Поисковый запрос (название или артист)"),
    artist: Optional[str] = Query(None, description="Фильтр по артисту"),
    platform: Optional[str] = Query(None, description="Фильтр по платформе"),
    censorship_type: Optional[CensorshipType] = Query(None, description="Фильтр по типу цензуры"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(50, ge=1, le=500, description="Лимит результатов"),
    offset: int = Query(0, ge=0, description="Смещение"),
):
    """
    Поиск треков в базе цензурированных треков
    
    Параметры:
    - **q**: Поисковый запрос по названию или артисту
    - **artist**: Фильтр по артисту
    - **platform**: Платформа (soundcloud, youtube, vk, navidrome)
    - **censorship_type**: Тип цензуры (blurred, muted, replaced, deleted, clean_version)
    - **status**: Статус (pending, verified, replaced, false_positive)
    - **limit**: Максимальное количество результатов (1-500)
    - **offset**: Смещение для пагинации
    """
    search = CensoredTrackSearch(
        query=q,
        artist=artist,
        platform=platform,
        censorship_type=censorship_type,
        status=status,
        limit=limit,
        offset=offset,
    )
    return censored_tracks_db.search(search)


@router.get("/{track_id}", response_model=dict)
async def get_track(track_id: int):
    """
    Получить информацию о конкретном цензурированном треке
    
    Параметры:
    - **track_id**: ID трека в базе
    """
    track = censored_tracks_db.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
    return track


@router.post("/", response_model=dict)
async def add_track(track: CensoredTrackCreate):
    """
    Добавить новый цензурированный трек в базу
    
    Параметры:
    - **title**: Название трека
    - **artist**: Имя артиста
    - **platform_id**: ID трека на платформе
    - **platform**: Платформа (soundcloud, youtube, vk, navidrome)
    - **censorship_type**: Тип цензуры
    - **original_title**: Оригинальное название (если отличается)
    - **description**: Описание проблемы
    - **timestamp_start**: Секунда начала цензуры
    - **timestamp_end**: Секунда конца цензуры
    - **censored_words**: Список цензурных слов
    - **duration**: Длительность трека
    - **cover**: URL обложки
    - **genres**: Жанры
    - **notes**: Заметки
    """
    # Проверяем существование трека
    existing = censored_tracks_db.get_track_by_platform(track.platform_id, track.platform)
    if existing:
        # Увеличиваем счётчик жалоб
        censored_tracks_db.increment_report_count(existing['id'])
        return {
            "id": existing['id'],
            "message": "Трек уже существует в базе",
            "report_count": existing.get('report_count', 0) + 1,
        }
    
    track_id = censored_tracks_db.add_track(track)
    if not track_id:
        raise HTTPException(status_code=400, detail="Не удалось добавить трек")
    
    return {
        "id": track_id,
        "message": "Трек добавлен в базу",
    }


@router.put("/{track_id}", response_model=dict)
async def update_track(track_id: int, update: CensoredTrackUpdate):
    """
    Обновить информацию о цензурированном треке
    
    Параметры:
    - **track_id**: ID трека в базе
    - **update**: Данные для обновления
    """
    # Проверяем существование
    existing = censored_tracks_db.get_track(track_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Трек не найден")
    
    # Автоматически устанавливаем verified_at при смене статуса на verified
    if update.status == "verified" and not update.verified_at:
        update.verified_at = datetime.utcnow()
    
    success = censored_tracks_db.update_track(track_id, update)
    if not success:
        raise HTTPException(status_code=400, detail="Не удалось обновить трек")
    
    return {
        "id": track_id,
        "message": "Трек обновлён",
    }


@router.delete("/{track_id}", response_model=dict)
async def delete_track(track_id: int):
    """
    Удалить трек из базы
    
    Параметры:
    - **track_id**: ID трека в базе
    """
    success = censored_tracks_db.delete_track(track_id)
    if not success:
        raise HTTPException(status_code=404, detail="Трек не найден")
    
    return {
        "id": track_id,
        "message": "Трек удалён",
    }


@router.post("/{track_id}/report", response_model=dict)
async def report_track(track_id: int):
    """
    Сообщить о проблеме с треком (увеличить счётчик жалоб)
    
    Параметры:
    - **track_id**: ID трека в базе
    """
    existing = censored_tracks_db.get_track(track_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Трек не найден")
    
    censored_tracks_db.increment_report_count(track_id)
    return {
        "id": track_id,
        "report_count": existing.get('report_count', 0) + 1,
    }


@router.post("/{track_id}/replacement", response_model=dict)
async def add_replacement(
    track_id: int,
    replacement_track_id: str = Body(..., description="ID трека замены"),
    replacement_url: str = Body(..., description="URL трека замены"),
    replacement_platform: str = Body(..., description="Платформа замены"),
):
    """
    Добавить информацию о найденной замене для цензурированного трека
    
    Параметры:
    - **track_id**: ID цензурированного трека
    - **replacement_track_id**: ID трека замены
    - **replacement_url**: URL трека замены
    - **replacement_platform**: Платформа замены
    """
    existing = censored_tracks_db.get_track(track_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Трек не найден")
    
    update = CensoredTrackUpdate(
        replacement_found=True,
        replacement_track_id=replacement_track_id,
        replacement_url=replacement_url,
        replacement_platform=replacement_platform,
        status="replaced",
    )
    
    success = censored_tracks_db.update_track(track_id, update)
    if not success:
        raise HTTPException(status_code=400, detail="Не удалось обновить трек")
    
    return {
        "id": track_id,
        "message": "Замена добавлена",
        "replacement": {
            "track_id": replacement_track_id,
            "url": replacement_url,
            "platform": replacement_platform,
        }
    }


@router.get("/export/json", response_model=List[dict])
async def export_to_json():
    """
    Экспорт всей базы в JSON формат
    
    Возвращает все треки из базы в формате JSON
    """
    return censored_tracks_db.export_to_json()


@router.post("/import/json", response_model=dict)
async def import_from_json(data: List[dict] = Body(..., description="Список треков для импорта")):
    """
    Импорт треков из JSON формата
    
    Параметры:
    - **data**: Список словарей с данными треков
    """
    count = censored_tracks_db.import_from_json(data)
    return {
        "imported": count,
        "message": f"Импортировано {count} треков",
    }


@router.get("/pending", response_model=List[dict])
async def get_pending_tracks(limit: int = Query(100, ge=1, le=1000)):
    """
    Получить все непроверенные треки
    
    Параметры:
    - **limit**: Максимальное количество результатов
    """
    search = CensoredTrackSearch(status="pending", limit=limit)
    return censored_tracks_db.search(search)


@router.get("/verified", response_model=List[dict])
async def get_verified_tracks(limit: int = Query(100, ge=1, le=1000)):
    """
    Получить все проверенные треки
    
    Параметры:
    - **limit**: Максимальное количество результатов
    """
    search = CensoredTrackSearch(status="verified", limit=limit)
    return censored_tracks_db.search(search)
