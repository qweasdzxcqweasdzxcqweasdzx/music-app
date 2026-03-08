from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_telegram_data(init_data: str, bot_token: str) -> Optional[dict]:
    """
    Проверка данных Telegram WebApp
    
    Args:
        init_data: Строка инициализации от Telegram
        bot_token: Токен бота
    
    Returns:
        Данные пользователя или None
    """
    try:
        # Парсинг строки инициализации
        data = {}
        for pair in init_data.split('&'):
            key, value = pair.split('=', 1)
            data[key] = value
        
        # Проверка хэша
        received_hash = data.get('hash')
        if not received_hash:
            return None
        
        # Удаление хэша из данных для проверки
        data_check_string = '\n'.join(
            f"{k}={v}" for k, v in sorted(data.items()) if k != 'hash'
        )
        
        # Создание секретного ключа для проверки
        import hashlib
        import hmac
        
        secret_key = hmac.new(
            b'WebAppData',
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисление хэша
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Сравнение хэшей
        if calculated_hash != received_hash:
            return None
        
        # Проверка времени (данные действительны 24 часа)
        auth_date = datetime.fromtimestamp(int(data.get('auth_date', 0)))
        if (datetime.utcnow() - auth_date).total_seconds() > 86400:
            return None
        
        # Возврат данных пользователя
        user_data = data.get('user')
        if user_data:
            import json
            return json.loads(user_data)
        
        return None
        
    except Exception as e:
        print(f"Error verifying telegram data: {e}")
        return None


def hash_password(password: str) -> str:
    """Хэширование пароля"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)
