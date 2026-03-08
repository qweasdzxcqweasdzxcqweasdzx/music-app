"""
Redis Cache Service

Кэширование ответов API для улучшения производительности.
Используется для:
- Кэширования ответов Spotify API
- Кэширования поисковых запросов
- Кэширования рекомендаций

TTL (Time To Live):
- Поиск: 1 час
- Треки/Артисты: 6 часов
- Рекомендации: 30 минут
- Плейлисты: 5 минут
"""

import json
import hashlib
from typing import Optional, Any, Dict
from datetime import timedelta


class RedisCache:
    """Сервис кэширования в Redis"""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self._redis = None
        self._enabled = False

    async def connect(self):
        """Подключение к Redis"""
        if not self.redis_url:
            print("Redis URL not configured, caching disabled")
            return

        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Проверка подключения
            await self._redis.ping()
            self._enabled = True
            print("Redis connected, caching enabled")
        except Exception as e:
            print(f"Redis connection error: {e}, caching disabled")
            self._enabled = False

    async def close(self):
        """Отключение от Redis"""
        if self._redis:
            await self._redis.close()

    def _make_key(self, prefix: str, data: Any) -> str:
        """Создание ключа кэша"""
        # Хэшируем данные для создания уникального ключа
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{data_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Получение из кэша"""
        if not self._enabled or not self._redis:
            return None

        try:
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Сохранение в кэш

        Args:
            key: Ключ
            value: Значение
            ttl: Время жизни в секундах (по умолчанию 1 час)
        """
        if not self._enabled or not self._redis:
            return False

        try:
            await self._redis.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Удаление из кэша"""
        if not self._enabled or not self._redis:
            return False

        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """Очистка ключей по паттерну"""
        if not self._enabled or not self._redis:
            return False

        try:
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Redis clear pattern error: {e}")
            return False

    # ==================== Helper методы ====================

    async def cache_search(
        self,
        query: str,
        source: str,
        limit: int
    ) -> Optional[Dict]:
        """Кэширование поискового запроса"""
        key = self._make_key(f"search:{source}", {
            "query": query,
            "limit": limit
        })
        return await self.get(key)

    async def cache_set_search(
        self,
        query: str,
        source: str,
        limit: int,
        result: Dict
    ) -> bool:
        """Сохранение результата поиска"""
        key = self._make_key(f"search:{source}", {
            "query": query,
            "limit": limit
        })
        # TTL 1 час для поиска
        return await self.set(key, result, ttl=3600)

    async def cache_track(self, track_id: str) -> Optional[Dict]:
        """Кэш трека"""
        return await self.get(f"track:{track_id}")

    async def cache_set_track(self, track_id: str, track: Dict) -> bool:
        """Сохранение трека в кэш"""
        # TTL 6 часов для треков
        return await self.set(f"track:{track_id}", track, ttl=21600)

    async def cache_artist(self, artist_id: str) -> Optional[Dict]:
        """Кэш артиста"""
        return await self.get(f"artist:{artist_id}")

    async def cache_set_artist(self, artist_id: str, artist: Dict) -> bool:
        """Сохранение артиста в кэш"""
        # TTL 6 часов для артистов
        return await self.set(f"artist:{artist_id}", artist, ttl=21600)

    async def cache_recommendations(
        self,
        seeds: Dict
    ) -> Optional[Dict]:
        """Кэш рекомендаций"""
        key = self._make_key("recommendations", seeds)
        return await self.get(key)

    async def cache_set_recommendations(
        self,
        seeds: Dict,
        result: Dict
    ) -> bool:
        """Сохранение рекомендаций в кэш"""
        key = self._make_key("recommendations", seeds)
        # TTL 30 минут для рекомендаций
        return await self.set(key, result, ttl=1800)


# Глобальный экземпляр
cache_service = RedisCache()
