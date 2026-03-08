"""
Secure Token Storage Service

Безопасное хранение токенов и чувствительных данных:
- Шифрование токенов OAuth
- Хранение учетных данных
- Управление сессиями
"""

import base64
import hashlib
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import settings


class SecureTokenStorage:
    """Сервис для безопасного хранения токенов"""

    def __init__(self):
        self._master_key = self._derive_key(settings.SECRET_KEY)
        self._cipher = Fernet(self._master_key)

        # In-memory хранилище (в продакшене использовать Redis/DB)
        self._storage: Dict[str, Dict] = {}

    def _derive_key(self, password: str) -> bytes:
        """Генерация ключа шифрования из пароля"""
        # Использование фиксированной соли для простоты
        # В продакшене использовать уникальную соль на пользователя
        salt = b"ultimate_music_app_salt_v1"

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: str) -> str:
        """Шифрование строки"""
        encrypted = self._cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Расшифровка строки"""
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self._cipher.decrypt(decoded)
        return decrypted.decode()

    async def store_token(
        self,
        user_id: str,
        service: str,
        token: str,
        token_type: str = "access",
        expires_at: Optional[int] = None,
        refresh_token: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Сохранение токена

        Args:
            user_id: ID пользователя
            service: Название сервиса (spotify, soundcloud, etc.)
            token: Access token
            token_type: Тип токена
            expires_at: Время истечения (timestamp)
            refresh_token: Refresh token (шифруется)
            metadata: Дополнительные данные
        """
        key = f"{user_id}:{service}"

        # Шифрование токенов
        encrypted_token = self.encrypt(token)
        encrypted_refresh = self.encrypt(refresh_token) if refresh_token else None

        self._storage[key] = {
            "user_id": user_id,
            "service": service,
            "token": encrypted_token,
            "token_type": token_type,
            "expires_at": expires_at,
            "refresh_token": encrypted_refresh,
            "metadata": metadata or {},
            "created_at": __import__("time").time()
        }

    async def get_token(
        self,
        user_id: str,
        service: str
    ) -> Optional[Dict]:
        """
        Получение токена

        Args:
            user_id: ID пользователя
            service: Название сервиса

        Returns:
            Расшифрованные данные токена или None
        """
        key = f"{user_id}:{service}"

        if key not in self._storage:
            return None

        stored = self._storage[key]

        # Проверка истечения
        if stored.get("expires_at"):
            import time
            if time.time() > stored["expires_at"]:
                # Токен истёк, пробуем обновить
                return None

        # Расшифровка
        try:
            token = self.decrypt(stored["token"])
            refresh_token = self.decrypt(stored["refresh_token"]) if stored.get("refresh_token") else None

            return {
                "user_id": stored["user_id"],
                "service": stored["service"],
                "token": token,
                "token_type": stored["token_type"],
                "expires_at": stored["expires_at"],
                "refresh_token": refresh_token,
                "metadata": stored["metadata"]
            }
        except Exception as e:
            print(f"Error decrypting token: {e}")
            return None

    async def delete_token(self, user_id: str, service: str) -> bool:
        """Удаление токена"""
        key = f"{user_id}:{service}"
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    async def list_services(self, user_id: str) -> list:
        """Получение списка сервисов с токенами"""
        services = []
        for key, stored in self._storage.items():
            if key.startswith(f"{user_id}:"):
                services.append({
                    "service": stored["service"],
                    "has_token": bool(stored.get("token")),
                    "expires_at": stored.get("expires_at"),
                    "metadata": stored.get("metadata", {})
                })
        return services

    async def update_metadata(
        self,
        user_id: str,
        service: str,
        metadata: Dict
    ) -> bool:
        """Обновление метаданных токена"""
        key = f"{user_id}:{service}"

        if key not in self._storage:
            return False

        self._storage[key]["metadata"].update(metadata)
        return True

    async def get_all_tokens(self, user_id: str) -> Dict[str, Dict]:
        """Получение всех токенов пользователя"""
        tokens = {}
        for key, stored in self._storage.items():
            if key.startswith(f"{user_id}:"):
                service = stored["service"]
                try:
                    token = self.decrypt(stored["token"])
                    tokens[service] = {
                        "token": token,
                        "token_type": stored["token_type"],
                        "expires_at": stored["expires_at"],
                        "metadata": stored["metadata"]
                    }
                except Exception:
                    tokens[service] = {
                        "token": None,
                        "error": "Decryption failed"
                    }
        return tokens


# Глобальный экземпляр
secure_storage = SecureTokenStorage()


# ==================== Rate Limiter ====================

from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter для API
limiter = Limiter(key_func=get_remote_address)


def get_rate_limit_config():
    """Получение конфигурации rate limiting"""
    return {
        "per_minute": settings.RATE_LIMIT_PER_MINUTE,
        "per_hour": settings.RATE_LIMIT_PER_HOUR
    }
