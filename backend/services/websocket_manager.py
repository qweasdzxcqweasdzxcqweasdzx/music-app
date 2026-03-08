"""
WebSocket Manager for Real-time Updates

Менеджер WebSocket соединений для:
- Обновлений плеера в реальном времени
- Уведомлений о завершении AI генерации
- Синхронизации между устройствами
- Jam сессий (совместное прослушивание)
"""

import asyncio
import json
from typing import Dict, Set, Optional, Any
from datetime import datetime


class WebSocketManager:
    """Менеджер WebSocket соединений"""

    def __init__(self):
        # Активные соединения: {connection_id: websocket}
        self._connections: Dict[str, Any] = {}

        # Соединения по пользователям: {user_id: set of connection_ids}
        self._user_connections: Dict[str, Set[str]] = {}

        # Соединения по комнатам (для Jam сессий): {room_id: set of connection_ids}
        self._rooms: Dict[str, Set[str]] = {}

        # Подписки по типам событий: {event_type: set of connection_ids}
        self._subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, connection_id: str, websocket: Any) -> None:
        """Подключение нового клиента"""
        self._connections[connection_id] = websocket
        print(f"WebSocket connected: {connection_id}")

    def disconnect(self, connection_id: str) -> None:
        """Отключение клиента"""
        if connection_id in self._connections:
            del self._connections[connection_id]
            print(f"WebSocket disconnected: {connection_id}")

        # Удаление из всех комнат и подписок
        for room in self._rooms.values():
            room.discard(connection_id)

        for subs in self._subscriptions.values():
            subs.discard(connection_id)

    async def register_user(self, user_id: str, connection_id: str) -> None:
        """Регистрация соединения за пользователем"""
        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()
        self._user_connections[user_id].add(connection_id)

    def unregister_user(self, user_id: str, connection_id: str) -> None:
        """Отписка соединения от пользователя"""
        if user_id in self._user_connections:
            self._user_connections[user_id].discard(connection_id)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

    async def join_room(self, room_id: str, connection_id: str) -> None:
        """Присоединение к комнате"""
        if room_id not in self._rooms:
            self._rooms[room_id] = set()
        self._rooms[room_id].add(connection_id)

    def leave_room(self, room_id: str, connection_id: str) -> None:
        """Покидание комнаты"""
        if room_id in self._rooms:
            self._rooms[room_id].discard(connection_id)
            if not self._rooms[room_id]:
                del self._rooms[room_id]

    async def subscribe(self, event_type: str, connection_id: str) -> None:
        """Подписка на тип событий"""
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = set()
        self._subscriptions[event_type].add(connection_id)

    def unsubscribe(self, event_type: str, connection_id: str) -> None:
        """Отписка от типа событий"""
        if event_type in self._subscriptions:
            self._subscriptions[event_type].discard(connection_id)

    async def send_to_connection(self, connection_id: str, data: Dict) -> bool:
        """Отправка данных конкретному соединению"""
        if connection_id not in self._connections:
            return False

        websocket = self._connections[connection_id]
        try:
            await websocket.send_json(data)
            return True
        except Exception as e:
            print(f"Error sending to {connection_id}: {e}")
            return False

    async def send_to_user(self, user_id: str, data: Dict) -> int:
        """Отправка данных всем соединениям пользователя"""
        if user_id not in self._user_connections:
            return 0

        sent_count = 0
        for connection_id in self._user_connections[user_id]:
            if await self.send_to_connection(connection_id, data):
                sent_count += 1

        return sent_count

    async def send_to_room(self, room_id: str, data: Dict) -> int:
        """Отправка данных всем в комнате"""
        if room_id not in self._rooms:
            return 0

        sent_count = 0
        for connection_id in self._rooms[room_id]:
            if await self.send_to_connection(connection_id, data):
                sent_count += 1

        return sent_count

    async def broadcast(self, data: Dict, event_type: Optional[str] = None) -> int:
        """
        Рассылка данных всем подписчикам

        Args:
            data: Данные для отправки
            event_type: Тип события (для фильтрации подписчиков)

        Returns:
            Количество полученных соединений
        """
        if event_type and event_type in self._subscriptions:
            targets = self._subscriptions[event_type]
        else:
            targets = set(self._connections.keys())

        sent_count = 0
        for connection_id in targets:
            if await self.send_to_connection(connection_id, data):
                sent_count += 1

        return sent_count

    async def broadcast_player_update(
        self,
        user_id: str,
        track_id: str,
        action: str,
        position: int = 0
    ) -> None:
        """
        Обновление состояния плеера для всех устройств пользователя

        Args:
            user_id: ID пользователя
            track_id: ID трека
            action: Действие (play, pause, seek, next, previous)
            position: Позиция в секундах
        """
        data = {
            "type": "player_update",
            "user_id": user_id,
            "track_id": track_id,
            "action": action,
            "position": position,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.send_to_user(user_id, data)

    async def broadcast_ai_generation_update(
        self,
        user_id: str,
        task_id: str,
        status: str,
        progress: float = 0,
        result: Optional[Dict] = None
    ) -> None:
        """
        Уведомление о статусе AI генерации

        Args:
            user_id: ID пользователя
            task_id: ID задачи генерации
            status: Статус (pending, processing, completed, failed)
            progress: Прогресс (0-1)
            result: Результат (если завершен)
        """
        data = {
            "type": "ai_generation_update",
            "user_id": user_id,
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.send_to_user(user_id, data)

    async def broadcast_jam_update(
        self,
        room_id: str,
        event: str,
        data: Dict
    ) -> None:
        """
        Обновление для Jam сессии

        Args:
            room_id: ID комнаты
            event: Событие (user_joined, user_left, track_changed, vote)
            data: Данные события
        """
        message = {
            "type": "jam_update",
            "room_id": room_id,
            "event": event,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.send_to_room(room_id, message)

    def get_stats(self) -> Dict:
        """Получение статистики подключений"""
        return {
            "total_connections": len(self._connections),
            "total_users": len(self._user_connections),
            "total_rooms": len(self._rooms),
            "subscriptions": {
                event_type: len(subs)
                for event_type, subs in self._subscriptions.items()
            }
        }

    async def cleanup_inactive(self, timeout: int = 300) -> None:
        """Очистка неактивных соединений (каждые 5 минут)"""
        # TODO: Реализовать tracking last activity
        pass


# Глобальный экземпляр
ws_manager = WebSocketManager()


# ==================== WebSocket Router ====================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional

ws_router = APIRouter()


@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Основной WebSocket endpoint"""
    await websocket.accept()

    # Генерация ID соединения
    import uuid
    connection_id = str(uuid.uuid4())

    # Подключение
    await ws_manager.connect(connection_id, websocket)

    try:
        while True:
            # Получение сообщений от клиента
            data = await websocket.receive_json()

            event_type = data.get("type")
            payload = data.get("payload", {})

            # Обработка команд
            if event_type == "auth":
                # Аутентификация
                user_id = payload.get("user_id")
                token = payload.get("token")

                if user_id:
                    await ws_manager.register_user(user_id, connection_id)
                    await websocket.send_json({
                        "type": "auth_success",
                        "connection_id": connection_id
                    })

            elif event_type == "join_room":
                # Присоединение к комнате
                room_id = payload.get("room_id")
                if room_id:
                    await ws_manager.join_room(room_id, connection_id)
                    await websocket.send_json({
                        "type": "room_joined",
                        "room_id": room_id
                    })

            elif event_type == "leave_room":
                # Покидание комнаты
                room_id = payload.get("room_id")
                if room_id:
                    ws_manager.leave_room(room_id, connection_id)
                    await websocket.send_json({
                        "type": "room_left",
                        "room_id": room_id
                    })

            elif event_type == "subscribe":
                # Подписка на события
                event_types = payload.get("events", [])
                for et in event_types:
                    await ws_manager.subscribe(et, connection_id)

            elif event_type == "player_action":
                # Действие плеера (для синхронизации)
                user_id = payload.get("user_id")
                if user_id:
                    await ws_manager.broadcast_player_update(
                        user_id=user_id,
                        track_id=payload.get("track_id"),
                        action=payload.get("action"),
                        position=payload.get("position", 0)
                    )

            elif event_type == "jam_action":
                # Действие в Jam сессии
                room_id = payload.get("room_id")
                if room_id:
                    await ws_manager.broadcast_jam_update(
                        room_id=room_id,
                        event=payload.get("event"),
                        data=payload.get("data", {})
                    )

    except WebSocketDisconnect:
        ws_manager.disconnect(connection_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(connection_id)
