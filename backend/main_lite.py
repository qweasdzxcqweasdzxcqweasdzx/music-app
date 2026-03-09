"""
Main FastAPI Application - Lite Version (без MongoDB)

Эта версия может работать без MongoDB для тестирования API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import Optional

from config import settings
from routes_lite import router  # Упрощенные роуты без MongoDB
from routes_subsonic import router as subsonic_router  # Subsonic API совместимость
from routes_api_keys import router as api_keys_router  # API-ключи
from services.cache_service import cache_service

from fastapi.staticfiles import StaticFiles
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения (Lite версия)"""
    print("✅ Starting Ultimate Music App (Lite Mode - без MongoDB)")
    
    # Подключение к Redis (опционально)
    try:
        await cache_service.connect()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
    
    # Инициализация YouTube сервиса
    try:
        from services.youtube_service import YouTubeMusicService
        yt = YouTubeMusicService()
        if yt.is_available:
            print("✅ YouTube service available (yt-dlp)")
        else:
            print("⚠️  YouTube service: yt-dlp not installed")
    except Exception as e:
        print(f"⚠️  YouTube service error: {e}")
    
    yield
    
    # Закрытие
    try:
        await cache_service.close()
    except:
        pass
    
    print("👋 Application stopped")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION + " [Lite Version]",
    version="3.1.0-lite",
    lifespan=lifespan
)

# CORS - РАЗРЕШАЕМ ВСЕ ДОМЕНЫ (для GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтирование статических файлов
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Роуты
app.include_router(router)
app.include_router(subsonic_router)  # Subsonic API совместимость
app.include_router(api_keys_router)  # API-ключи


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "name": "Ultimate Music App",
        "version": "3.1.0-lite",
        "mode": "No-MongoDB",
        "status": "running",
        "features": [
            "Anti-Censorship System ✓",
            "YouTube via yt-dlp",
            "SoundCloud API",
            "Fuzzy Matching",
            "Multi-platform Search",
            "Subsonic API Compatible ✓",
            "API Keys Authentication ✓"
        ],
        "api_docs": "/docs",
        "api_endpoints": {
            "main": "/api/*",
            "subsonic": "/rest/*",
            "api_keys": "/api/keys"
        },
        "new_endpoints": [
            "/api/censorship/check",
            "/api/censorship/find-original",
            "/api/censorship/search-uncensored",
            "/api/censorship/analyze-batch",
            "/api/censorship/statistics",
            "/api/censorship/replace-censored",
            "/api/keys",
            "/api/keys/test",
            "/rest/ping.view",
            "/rest/getArtists.view",
            "/rest/getAlbumList.view"
        ],
        "subsonic_clients": [
            "DSub (Android)",
            "Substreamer (iOS)",
            "Sonos",
            "Kodi"
        ]
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья"""
    from services.youtube_service import YouTubeMusicService
    from services.soundcloud_service import soundcloud_service
    
    yt_available = False
    try:
        yt = YouTubeMusicService()
        yt_available = yt.is_available
    except:
        pass
    
    return {
        "status": "healthy",
        "mongodb": "disabled (lite mode)",
        "redis": "optional",
        "youtube": "available" if yt_available else "unavailable",
        "soundcloud": "configured" if settings.SOUNDCLOUD_CLIENT_ID else "not configured",
        "anti_censorship": "enabled"
    }


@app.get("/api/test/blues")
async def test_blues_detection():
    """Тест системы Anti-Censorship"""
    from services.blues_detection_service import blues_detection_service
    from models import Track
    
    # Тестовые треки
    test_tracks = [
        Track(title="Bad Guy (Clean Version)", artist="Billie Eilish", duration=194, stream_url=""),
        Track(title="Lose Yourself (Explicit)", artist="Eminem", duration=326, stream_url="", is_explicit=True),
        Track(title="Shape of You", artist="Ed Sheeran", duration=233, stream_url=""),
    ]
    
    results = []
    for track in test_tracks:
        results.append({
            "title": track.title,
            "is_censored": blues_detection_service.is_censored(track),
            "is_explicit": blues_detection_service.is_explicit_version(track),
            "version_type": blues_detection_service.get_version_type(track)
        })
    
    return {
        "test": "blues_detection",
        "status": "passed",
        "results": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )
