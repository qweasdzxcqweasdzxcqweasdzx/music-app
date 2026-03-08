from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import Optional

from config import settings
from database import connect_to_mongodb, close_mongodb_connection
from routes import router
from services.cache_service import cache_service
from services.audio_streaming_service import audio_streaming_service
from services.navidrome_service import navidrome_service
from services.vk_service import VKMusicService
from services.youtube_service import YouTubeMusicService
from services.websocket_manager import ws_router
from services.music_source_base import source_manager
from services.soundcloud_source_adapter import soundcloud_source
from services.navidrome_source_adapter import navidrome_source
# from bot import music_bot  # Отключено для тестов

from fastapi.staticfiles import StaticFiles
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Подключение к базе данных
    await connect_to_mongodb()

    # Подключение к Redis для кэширования
    await cache_service.connect()

    # Инициализация аудио сервиса
    vk_service = VKMusicService()
    youtube_service = YouTubeMusicService(proxy=settings.PROXY_URL)

    audio_streaming_service.initialize(
        vk_service=vk_service,
        youtube_service=youtube_service,
        soundcloud_service=soundcloud_service
    )

    # Подключение к Navidrome (если настроен)
    if settings.NAVIDROME_URL and settings.NAVIDROME_USERNAME:
        connected = await navidrome_service.connect(
            settings.NAVIDROME_URL,
            settings.NAVIDROME_USERNAME,
            settings.NAVIDROME_PASSWORD,
            settings.NAVIDROME_JWT_TOKEN
        )
        if connected:
            print(f"✅ Navidrome connected: {settings.NAVIDROME_URL}")

    # Регистрация источников музыки
    source_manager.register_source(soundcloud_source)
    source_manager.register_source(navidrome_source)

    # Проверка доступных источников
    available = source_manager.get_available_sources()
    print(f"✅ Available music sources: {available}")

    # Запуск Telegram бота в фоновом режиме (отключено для тестов)
    # if settings.TELEGRAM_BOT_TOKEN:
    #     asyncio.create_task(music_bot.run())

    yield

    # Отключение от базы данных
    await close_mongodb_connection()

    # Отключение от Redis
    await cache_service.close()

    # Отключение от Navidrome
    # navidrome_service.disconnect()

    # Остановка бота
    # if bot_task:
    #     bot_task.cancel()
    #     try:
    #         await bot_task
    #     except asyncio.CancelledError:
    #         pass


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version="3.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Монтирование статических файлов (для фронтенда)
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Роуты
app.include_router(router)
app.include_router(ws_router)  # WebSocket


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    available_sources = source_manager.get_available_sources()
    return {
        "name": settings.APP_NAME,
        "version": "3.0.0",
        "status": "running",
        "sources": {
            "available": available_sources,
            "total": len(available_sources)
        },
        "features": [
            "Multi-source music integration",
            "SoundCloud API",
            "Navidrome/Subsonic (local library)",
            "VK Music (backup)",
            "YouTube (backup)",
            "AI music generation (Suno, Mubert, MusicGen)",
            "Stem separation (LALAL.AI)",
            "Voice synthesis (ElevenLabs)",
            "Smart Mixer",
            "WebSocket real-time updates",
            "Anti-censorship system"
        ]
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья"""
    sources_health = await source_manager.health_check_all()
    return {
        "status": "healthy",
        "mongodb": "connected",
        "redis": "connected",
        "sources": sources_health,
        "telegram_bot": "running" if settings.TELEGRAM_BOT_TOKEN else "disabled"
    }


@app.get("/api/sources")
async def get_sources():
    """Получение доступных источников музыки"""
    sources = {}
    for name, source in source_manager.get_all_sources().items():
        sources[name] = {
            "available": source.is_available,
            "name": source.source_name
        }
    return {"sources": sources}


@app.get("/api/search/unified")
async def unified_search(
    q: str,
    limit: int = 20,
    sources: Optional[str] = None
):
    """Единый поиск по всем источникам"""
    from fastapi import Query
    source_list = sources.split(",") if sources else None
    results = await source_manager.search_all(q, limit, source_list)
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
