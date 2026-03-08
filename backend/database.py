"""
База данных MongoDB

Для тестов без MongoDB используется in-memory хранилище
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from config import settings

# In-memory хранилище для тестов
_in_memory_db: Dict[str, List[Dict]] = {
    "users": [],
    "playlists": [],
    "play_history": [],
    "likes": [],
    "tracks": []
}

_mongo_client = None
_db = None

# Флаг использования MongoDB
USE_MONGODB = False


class MockCollection:
    """Mock коллекция для тестов без MongoDB"""

    def __init__(self, name: str):
        self.name = name

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict]:
        """Найти один документ"""
        collection = _in_memory_db.get(self.name, [])
        
        for item in collection:
            match = True
            for key, value in query.items():
                if key == "_id":
                    from bson import ObjectId
                    if str(item.get("id")) != str(value) and str(item.get("_id")) != str(value):
                        match = False
                        break
                elif item.get(key) != value:
                    match = False
                    break
            if match:
                return item
        return None

    async def find(self, query: Optional[Dict[str, Any]] = None):
        """Найти документы"""
        collection = _in_memory_db.get(self.name, [])
        
        if not query:
            return MockCursor(collection)
        
        results = []
        for item in collection:
            match = True
            for key, value in query.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                results.append(item)
        
        return MockCursor(results)

    async def insert_one(self, document: Dict) -> Any:
        """Вставить документ"""
        from bson import ObjectId
        document["_id"] = ObjectId()
        if "id" not in document:
            document["id"] = str(document["_id"])
        _in_memory_db[self.name].append(document)
        return MockInsertResult(document["_id"])

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]):
        """Обновить документ"""
        collection = _in_memory_db.get(self.name, [])
        
        for item in collection:
            match = True
            for key, value in query.items():
                if key == "_id":
                    from bson import ObjectId
                    if str(item.get("id")) != str(value) and str(item.get("_id")) != str(value):
                        match = False
                        break
                elif item.get(key) != value:
                    match = False
                    break
            if match:
                if "$set" in update:
                    for key, value in update["$set"].items():
                        item[key] = value
                if "$addToSet" in update:
                    for key, value in update["$addToSet"].items():
                        if key in item and isinstance(item[key], list):
                            if value not in item[key]:
                                item[key].append(value)
                if "$pull" in update:
                    for key, value in update["$pull"].items():
                        if key in item and isinstance(item[key], list):
                            item[key] = [x for x in item[key] if x != value]
                return MockUpdateResult(1)
        
        return MockUpdateResult(0)

    async def delete_one(self, query: Dict[str, Any]) -> int:
        """Удалить документ"""
        collection = _in_memory_db.get(self.name, [])
        
        for i, item in enumerate(collection):
            match = True
            for key, value in query.items():
                if key == "_id":
                    from bson import ObjectId
                    if str(item.get("id")) != str(value) and str(item.get("_id")) != str(value):
                        match = False
                        break
                elif item.get(key) != value:
                    match = False
                    break
            if match:
                collection.pop(i)
                return 1
        
        return 0

    async def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """Агрегация"""
        collection = _in_memory_db.get(self.name, [])
        return collection


class MockCursor:
    """Mock курсор для тестов"""

    def __init__(self, items: List[Dict]):
        self.items = items
        self.sort_field = None
        self.sort_order = 1
        self.limit_count = None

    def sort(self, field: str, order: int = 1):
        self.sort_field = field
        self.sort_order = order
        return self

    def limit(self, count: int):
        self.limit_count = count
        return self

    async def to_list(self, length: Optional[int] = None) -> List[Dict]:
        """Конвертировать в список"""
        if self.sort_field:
            self.items.sort(
                key=lambda x: x.get(self.sort_field, 0),
                reverse=(self.sort_order == -1)
            )
        
        result = self.items
        if self.limit_count:
            result = result[:self.limit_count]
        elif length:
            result = result[:length]
        
        return result


class MockInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class MockUpdateResult:
    def __init__(self, modified_count):
        self.modified_count = modified_count


async def connect_to_mongodb():
    """Подключение к MongoDB"""
    global USE_MONGODB, _mongo_client, _db
    
    if not settings.MONGODB_URL:
        print("⚠️  MongoDB не настроена, используем in-memory хранилище")
        print("   Для полноценной работы установите MongoDB или Docker")
        USE_MONGODB = False
        return
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        _mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        _db = _mongo_client[settings.DB_NAME]
        
        # Проверка подключения
        await _mongo_client.admin.command('ping')
        USE_MONGODB = True
        print("✅ MongoDB подключена:", settings.MONGODB_URL)
    except Exception as e:
        print(f"⚠️  Ошибка подключения к MongoDB: {e}")
        print("   Используем in-memory хранилище")
        USE_MONGODB = False


async def close_mongodb_connection():
    """Отключение от MongoDB"""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None


async def get_collection(name: str):
    """Получение коллекции"""
    if USE_MONGODB and _db:
        return _db[name]
    return MockCollection(name)
