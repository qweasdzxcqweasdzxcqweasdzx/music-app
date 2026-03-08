"""
SoundCloud API Service

Официальный SoundCloud API для интеграции с платформой.
Документация: https://developers.soundcloud.com/docs/api/guide

Аутентификация: OAuth 2.0
- Implicit Grant (для клиентских приложений)
- Authorization Code Flow (для серверных приложений)

Для использования нужно:
1. Зарегистрировать приложение на https://soundcloud.com/you/apps
2. Получить Client ID и Client Secret
3. Настроить Redirect URI
"""

import aiohttp
import base64
import time
from typing import List, Optional, Dict, Any
from models import Track, Artist as ArtistModel
from config import settings


class SoundCloudService:
    """Сервис для работы с официальным SoundCloud API"""

    def __init__(self):
        self.client_id = settings.SOUNDCLOUD_CLIENT_ID
        self.client_secret = settings.SOUNDCLOUD_CLIENT_SECRET
        self.redirect_uri = settings.SOUNDCLOUD_REDIRECT_URI
        self.access_token = None
        self.refresh_token = None
        self.token_expires = 0
        self.base_url = "https://api.soundcloud.com"
        self.auth_url = "https://soundcloud.com/oauth2/authorize"
        self.token_url = "https://api.soundcloud.com/oauth2/token"
        self._session: Optional[aiohttp.ClientSession] = None

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Генерация URL для авторизации пользователя

        Args:
            state: Уникальный токен для защиты от CSRF

        Returns:
            URL для перенаправления пользователя
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'non-expiring',
        }
        if state:
            params['state'] = state

        query = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query}"

    async def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """
        Обмен authorization code на access token

        Args:
            code: Authorization code из callback

        Returns:
            Токены или None
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.token_url,
                    data={
                        'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'code': code,
                        'redirect_uri': self.redirect_uri,
                        'grant_type': 'authorization_code'
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.access_token = data['access_token']
                        self.refresh_token = data.get('refresh_token')
                        self.token_expires = time.time() + data.get('expires_in', 3600)
                        return data
                    else:
                        print(f"SoundCloud token error: {resp.status}")
                        return None
            except Exception as e:
                print(f"Error exchanging code: {e}")
                return None

    async def _get_access_token(self) -> Optional[str]:
        """Получение/обновление access токена"""
        if self.access_token and time.time() < self.token_expires - 60:
            return self.access_token

        # Если есть refresh token, обновляем
        if self.refresh_token:
            return await self._refresh_token()

        # Client credentials flow (для публичных данных)
        if self.client_id and self.client_secret:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        self.token_url,
                        data={
                            'client_id': self.client_id,
                            'client_secret': self.client_secret,
                            'grant_type': 'client_credentials'
                        }
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.access_token = data['access_token']
                            self.token_expires = time.time() + data.get('expires_in', 3600)
                            return self.access_token
                except Exception as e:
                    print(f"SoundCloud client credentials error: {e}")

        return None

    async def _refresh_token(self) -> Optional[str]:
        """Обновление access токена через refresh token"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.token_url,
                    data={
                        'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'refresh_token': self.refresh_token,
                        'grant_type': 'refresh_token'
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.access_token = data['access_token']
                        self.refresh_token = data.get('refresh_token', self.refresh_token)
                        self.token_expires = time.time() + data.get('expires_in', 3600)
                        return self.access_token
            except Exception as e:
                print(f"Token refresh error: {e}")

        return None

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        use_auth: bool = True
    ) -> Optional[Dict]:
        """HTTP запрос к SoundCloud API"""
        token = await self._get_access_token() if use_auth else None
        headers = {}
        if token:
            headers['Authorization'] = f'OAuth {token}'

        # Для публичных запросов используем client_id
        query_params = params or {}
        if not token and self.client_id:
            query_params['client_id'] = self.client_id

        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(
                    f"{self.base_url}{endpoint}",
                    params=query_params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 401 and use_auth:
                        # Токен истёк, пробуем обновить
                        await self._refresh_token()
                        return await self._request(endpoint, params, use_auth)
                    else:
                        print(f"SoundCloud API error {resp.status}")
                        return None
            except Exception as e:
                print(f"SoundCloud request error: {e}")
                return None

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> Dict[str, List]:
        """
        Поиск по SoundCloud

        Args:
            query: Поисковый запрос
            limit: Количество результатов
            offset: Смещение

        Returns:
            Dict с ключами: tracks, users, playlists
        """
        # SoundCloud v2 API
        results = await self._request('/search', {
            'q': query,
            'limit': limit,
            'offset': offset,
            'facet': 'genre',
            'search.kind': 'all'
        })

        if not results:
            return {"tracks": [], "users": [], "playlists": []}

        return {
            "tracks": self._parse_tracks(results.get('collection', [])[:limit]),
            "users": self._parse_users(results.get('collection', [])[:limit // 2]),
            "playlists": self._parse_playlists(results.get('collection', [])[:limit // 2])
        }

    def _parse_tracks(self, items: List[Dict]) -> List[Track]:
        """Парсинг треков из SoundCloud API"""
        tracks = []
        for item in items:
            if item.get('kind') != 'track':
                continue
            try:
                # Получение URL для стриминга
                stream_url = None
                if item.get('media', {}).get('transcodings'):
                    transcoding = item['media']['transcodings'][0]
                    stream_url = transcoding.get('url')

                # Обложка
                cover = item.get('artwork_url') or (
                    item.get('user', {}).get('avatar_url')
                )

                # Замена размера обложки на больший
                if cover and 'large.jpg' in cover:
                    cover = cover.replace('large.jpg', 't500x500.jpg')

                track = Track(
                    id=str(item.get('id')),
                    title=item.get('title', 'Unknown'),
                    artist=item.get('user', {}).get('username', 'Unknown'),
                    artist_id=str(item.get('user', {}).get('id')),
                    duration=item.get('duration', 0) // 1000,
                    stream_url=stream_url or '',
                    cover=cover,
                    source="soundcloud",
                    is_explicit=item.get('explicit', False),
                    play_count=item.get('playback_count', 0),
                    likes_count=item.get('likes_count', 0),
                    genre=item.get('genre'),
                    description=item.get('description'),
                    created_at=item.get('created_at'),
                    permalink_url=item.get('permalink_url'),
                    waveform_url=item.get('waveform_url')
                )
                tracks.append(track)
            except Exception as e:
                print(f"Error parsing SoundCloud track: {e}")

        return tracks

    def _parse_users(self, items: List[Dict]) -> List[Dict]:
        """Парсинг пользователей/артистов"""
        users = []
        for item in items:
            if item.get('kind') != 'user':
                continue
            try:
                users.append({
                    'id': str(item.get('id')),
                    'username': item.get('username'),
                    'full_name': item.get('full_name'),
                    'avatar_url': item.get('avatar_url'),
                    'city': item.get('city'),
                    'country': item.get('country'),
                    'description': item.get('description'),
                    'followers_count': item.get('followers_count', 0),
                    'followings_count': item.get('followings_count', 0),
                    'track_count': item.get('track_count', 0),
                    'playlist_count': item.get('playlist_count', 0),
                    'verified': item.get('verified', False),
                    'permalink_url': item.get('permalink_url'),
                    'source': 'soundcloud'
                })
            except Exception as e:
                print(f"Error parsing SoundCloud user: {e}")
        return users

    def _parse_playlists(self, items: List[Dict]) -> List[Dict]:
        """Парсинг плейлистов"""
        playlists = []
        for item in items:
            if item.get('kind') not in ('playlist', 'album'):
                continue
            try:
                playlists.append({
                    'id': str(item.get('id')),
                    'title': item.get('title'),
                    'user': {
                        'id': str(item.get('user', {}).get('id')),
                        'username': item.get('user', {}).get('username')
                    },
                    'artwork_url': item.get('artwork_url'),
                    'track_count': item.get('track_count', 0),
                    'duration': item.get('duration', 0) // 1000,
                    'genre': item.get('genre'),
                    'description': item.get('description'),
                    'created_at': item.get('created_at'),
                    'likes_count': item.get('likes_count', 0),
                    'permalink_url': item.get('permalink_url'),
                    'is_album': item.get('kind') == 'album',
                    'source': 'soundcloud'
                })
            except Exception as e:
                print(f"Error parsing SoundCloud playlist: {e}")
        return playlists

    async def get_track(self, track_id: str) -> Optional[Track]:
        """Получение информации о треке"""
        data = await self._request(f'/tracks/{track_id}')
        if not data:
            return None

        tracks = self._parse_tracks([data])
        return tracks[0] if tracks else None

    async def get_track_stream_url(self, track_id: str) -> Optional[str]:
        """
        Получение URL для стриминга трека

        SoundCloud использует двухэтапный процесс:
        1. Получение playlist URL из track metadata
        2. Получение actual stream URL из playlist
        """
        track = await self.get_track(track_id)
        if not track or not track.stream_url:
            return None

        # Запрос к playlist URL для получения реального stream URL
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    track.stream_url,
                    params={'client_id': self.client_id}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('url')
            except Exception as e:
                print(f"Error getting stream URL: {e}")

        return None

    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Получение информации о пользователе"""
        data = await self._request(f'/users/{user_id}')
        if not data:
            return None

        users = self._parse_users([data])
        return users[0] if users else None

    async def get_user_tracks(self, user_id: str, limit: int = 20) -> List[Track]:
        """Получение треков пользователя"""
        data = await self._request(f'/users/{user_id}/tracks', {'limit': limit})
        if not data:
            return []

        return self._parse_tracks(data)

    async def get_user_playlists(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Получение плейлистов пользователя"""
        data = await self._request(f'/users/{user_id}/playlists', {'limit': limit})
        if not data:
            return []

        return self._parse_playlists(data)

    async def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Получение плейлиста"""
        data = await self._request(f'/playlists/{playlist_id}')
        if not data:
            return None

        playlists = self._parse_playlists([data])
        playlist = playlists[0] if playlists else None

        if playlist:
            # Получение треков плейлиста
            tracks = []
            for track_data in data.get('tracks', []):
                track = self._parse_tracks([track_data])
                if track:
                    tracks.append(track[0])
            playlist['tracks'] = tracks

        return playlist

    async def get_trending(self, limit: int = 20, genre: Optional[str] = None) -> List[Track]:
        """Получение трендовых треков"""
        params = {'limit': limit, 'kind': 'trending'}
        if genre:
            params['filter.genre'] = genre

        data = await self._request('/search', params)
        if not data:
            return []

        return self._parse_tracks(data.get('collection', [])[:limit])

    async def get_new_hot(self, limit: int = 20) -> List[Track]:
        """Получение новых и горячих треков"""
        data = await self._request('/search', {
            'limit': limit,
            'filter.created_at': 'last_week',
            'order': 'hotness'
        })
        if not data:
            return []

        return self._parse_tracks(data.get('collection', [])[:limit])

    async def get_user_likes(self, user_id: str, limit: int = 20) -> List[Track]:
        """Получение лайков пользователя"""
        data = await self._request(f'/users/{user_id}/likes', {'limit': limit})
        if not data:
            return []

        tracks = []
        for item in data.get('collection', []):
            if item.get('type') == 'track':
                track_data = item.get('track') or item.get('origin')
                if track_data:
                    track = self._parse_tracks([track_data])
                    if track:
                        tracks.append(track[0])

        return tracks

    async def like_track(self, track_id: str) -> bool:
        """Добавление трека в лайки (требует OAuth)"""
        if not self.access_token:
            return False

        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(
                    f"{self.base_url}/users/me/favorites/{track_id}",
                    headers={'Authorization': f'OAuth {self.access_token}'}
                ) as resp:
                    return resp.status == 201
            except Exception as e:
                print(f"Error liking track: {e}")
                return False

    async def unlike_track(self, track_id: str) -> bool:
        """Удаление трека из лайков"""
        if not self.access_token:
            return False

        async with aiohttp.ClientSession() as session:
            try:
                async with session.delete(
                    f"{self.base_url}/users/me/favorites/{track_id}",
                    headers={'Authorization': f'OAuth {self.access_token}'}
                ) as resp:
                    return resp.status == 204
            except Exception as e:
                print(f"Error unliking track: {e}")
                return False

    async def follow_user(self, user_id: str) -> bool:
        """Подписка на пользователя"""
        if not self.access_token:
            return False

        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(
                    f"{self.base_url}/users/me/followings/{user_id}",
                    headers={'Authorization': f'OAuth {self.access_token}'}
                ) as resp:
                    return resp.status == 201
            except Exception as e:
                print(f"Error following user: {e}")
                return False

    async def get_stream_url_from_playlist(self, playlist_url: str) -> Optional[str]:
        """
        Получение реального stream URL из playlist URL

        SoundCloud возвращает playlist URL, который нужно запросить
        дополнительно для получения фактического URL аудио
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    playlist_url,
                    params={'client_id': self.client_id}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('url')
            except Exception as e:
                print(f"Error getting stream from playlist: {e}")

        return None

    @property
    def is_authenticated(self) -> bool:
        """Проверка аутентификации"""
        return self.access_token is not None and time.time() < self.token_expires


# Глобальный экземпляр
soundcloud_service = SoundCloudService()
