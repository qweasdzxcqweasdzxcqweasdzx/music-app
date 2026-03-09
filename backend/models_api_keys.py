"""
API Keys для безопасного доступа

Используется вместо пароля для:
- Telegram бота
- Мобильных приложений
- Сторонних клиентов
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import secrets


class APIKey(BaseModel):
    """Модель API-ключа"""
    id: str = Field(default_factory=lambda: secrets.token_urlsafe(16))
    user_id: str
    name: str  # "Telegram Bot", "Mobile App"
    key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        populate_by_name = True


class APIKeyCreate(BaseModel):
    """Создание API-ключа"""
    name: str
    user_id: Optional[str] = None


class APIKeyResponse(BaseModel):
    """Ответ с API-ключом (без sensitive данных)"""
    id: str
    name: str
    key: str  # Показываем только при создании
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool


class APIKeyList(BaseModel):
    """Список API-ключей"""
    keys: List[APIKeyResponse]
    total: int


# In-memory хранилище (для демонстрации)
api_keys_db: List[APIKey] = []


def create_api_key(user_id: str, name: str) -> APIKey:
    """Создать новый API-ключ"""
    api_key = APIKey(
        user_id=user_id,
        name=name
    )
    api_keys_db.append(api_key)
    return api_key


def get_api_key_by_key(key: str) -> Optional[APIKey]:
    """Получить ключ по значению"""
    for api_key in api_keys_db:
        if api_key.key == key and api_key.is_active:
            return api_key
    return None


def get_api_keys_by_user(user_id: str) -> List[APIKey]:
    """Получить все ключи пользователя"""
    return [k for k in api_keys_db if k.user_id == user_id]


def revoke_api_key(key_id: str, user_id: str) -> bool:
    """Отозвать ключ"""
    for api_key in api_keys_db:
        if api_key.id == key_id and api_key.user_id == user_id:
            api_key.is_active = False
            return True
    return False


def update_last_used(key: str) -> None:
    """Обновить время последнего использования"""
    for api_key in api_keys_db:
        if api_key.key == key:
            api_key.last_used = datetime.utcnow()
            break


# Создать тестовый ключ
create_api_key(user_id="telegram_bot", name="Telegram Bot")
