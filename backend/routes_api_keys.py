"""
API Keys Management Routes

Управление API-ключами для безопасного доступа
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from models_api_keys import (
    APIKey, APIKeyCreate, APIKeyResponse, APIKeyList,
    create_api_key, get_api_keys_by_user, revoke_api_key,
    get_api_key_by_key, update_last_used, api_keys_db
)

router = APIRouter(prefix="/api/keys", tags=["api-keys"])


# ==================== Dependency ====================

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Проверка API-ключа из заголовка"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    api_key = get_api_key_by_key(x_api_key)
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    update_last_used(x_api_key)
    return api_key


# ==================== Routes ====================

@router.post("", response_model=APIKeyResponse)
async def create_key(key_data: APIKeyCreate):
    """
    Создать новый API-ключ
    
    - **name**: Имя ключа (например, "Telegram Bot")
    - **user_id**: ID пользователя (опционально)
    """
    user_id = key_data.user_id or "default_user"
    api_key = create_api_key(user_id=user_id, name=key_data.name)
    
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key=api_key.key,  # Показываем только при создании!
        created_at=api_key.created_at,
        last_used=api_key.last_used,
        is_active=api_key.is_active
    )


@router.get("", response_model=APIKeyList)
async def list_keys(api_key: APIKey = Depends(verify_api_key)):
    """
    Получить список всех API-ключей
    
    Требуется валидный API-ключ в заголовке X-API-Key
    """
    keys = get_api_keys_by_user(api_key.user_id)
    
    return APIKeyList(
        keys=[
            APIKeyResponse(
                id=k.id,
                name=k.name,
                key=k.key[:8] + "..." + k.key[-4:],  # Скрываем большую часть ключа
                created_at=k.created_at,
                last_used=k.last_used,
                is_active=k.is_active
            )
            for k in keys
        ],
        total=len(keys)
    )


@router.delete("/{key_id}")
async def revoke_key(key_id: str, api_key: APIKey = Depends(verify_api_key)):
    """
    Отозвать API-ключ по ID
    
    Ключ перестанет работать немедленно
    """
    if revoke_api_key(key_id, api_key.user_id):
        return {"status": "ok", "message": "Key revoked"}
    raise HTTPException(status_code=404, detail="Key not found")


@router.get("/test")
async def test_key(api_key: APIKey = Depends(verify_api_key)):
    """
    Проверить валидность API-ключа
    
    Возвращает информацию о ключе
    """
    return {
        "status": "ok",
        "key": {
            "id": api_key.id,
            "name": api_key.name,
            "created_at": api_key.created_at,
            "last_used": api_key.last_used
        }
    }


# ==================== Public endpoint ====================

@router.get("/public/info")
async def public_info():
    """
    Публичная информация о сервере
    
    Не требует аутентификации
    """
    return {
        "name": "Music App API",
        "version": "3.1.0",
        "features": [
            "Music Search",
            "Audio Streaming",
            "Subsonic API Compatible",
            "API Keys Authentication"
        ],
        "auth_methods": [
            "X-API-Key header",
            "Bearer token (Telegram)"
        ]
    }
