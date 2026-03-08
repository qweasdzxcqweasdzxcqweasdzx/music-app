from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Приложение
    APP_NAME: str = "Ultimate Music App"
    DEBUG: bool = True
    DESCRIPTION: str = "Music streaming with AI generation and multi-source integration"

    # Сервер
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # База данных
    MONGODB_URL: Optional[str] = None
    DB_NAME: str = "ultimate_music_app"

    # Redis
    REDIS_URL: Optional[str] = None

    # JWT
    SECRET_KEY: str = "dev-secret-key-not-for-production-min-32-chars-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_BOT_USERNAME: Optional[str] = None

    # Genius API (для текстов песен)
    GENIUS_API_TOKEN: Optional[str] = None

    # SoundCloud API
    SOUNDCLOUD_CLIENT_ID: Optional[str] = None
    SOUNDCLOUD_CLIENT_SECRET: Optional[str] = None
    SOUNDCLOUD_REDIRECT_URI: str = "http://localhost:8000/callback/soundcloud"

    # VK API
    VK_CLIENT_ID: Optional[str] = None
    VK_CLIENT_SECRET: Optional[str] = None

    # YouTube
    YOUTUBE_API_KEY: Optional[str] = None

    # Navidrome / Subsonic
    NAVIDROME_URL: Optional[str] = None
    NAVIDROME_USERNAME: Optional[str] = None
    NAVIDROME_PASSWORD: Optional[str] = None
    NAVIDROME_JWT_TOKEN: Optional[str] = None

    # AI Services
    # Suno AI
    SUNO_API_KEY: Optional[str] = None

    # Mubert
    MUBERT_CLIENT_ID: Optional[str] = None
    MUBERT_TOKEN: Optional[str] = None

    # LALAL.AI
    LALAL_API_KEY: Optional[str] = None

    # ElevenLabs
    ELEVENLABS_API_KEY: Optional[str] = None

    # Hugging Face
    HUGGINGFACE_TOKEN: Optional[str] = None

    # Replicate
    REPLICATE_API_TOKEN: Optional[str] = None

    # Прокси
    PROXY_URL: Optional[str] = None

    # Анти-цензура
    PREFER_ORIGINAL: bool = True
    AUTO_REPLACE_CENSORED: bool = True

    # Лимиты
    MAX_SEARCH_RESULTS: int = 50
    MAX_PLAYLIST_TRACKS: int = 1000

    # Рекомендации
    RECOMMENDATIONS_MIN_TRACKS: int = 10
    RECOMMENDATIONS_MAX_TRACKS: int = 50

    # Умный миксер
    MIXER_PREFERRED_SOURCE: str = "auto"  # auto, soundcloud, navidrome
    MIXER_ENABLE_AI: bool = True  # Разрешить AI генерацию в миксе

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Кэширование
    CACHE_TTL_DEFAULT: int = 3600  # 1 час
    CACHE_TTL_TRACK: int = 86400  # 24 часа
    CACHE_TTL_ARTIST: int = 43200  # 12 часов

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
