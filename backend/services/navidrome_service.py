"""
Navidrome / Subsonic API Service

Поддержка протокола Subsonic для интеграции с личными музыкальными серверами:
- Navidrome (рекомендуется)
- Subsonic
- Airsonic
- Libresonic

API Documentation:
- Subsonic API: http://www.subsonic.org/pages/api.jsp
- Navidrome: https://www.navidrome.org/docs/developers/subsonic-api/

Аутентификация:
- Username + Password (plain или md5)
- JWT токены (Navidrome 0.47+)
"""

import aiohttp
import hashlib
import base64
from typing import List, Optional, Dict, Any
from models_main import Track, Artist as ArtistModel, Album as AlbumModel
from config import settings


class NavidromeService:
    """Сервис для работы с Navidrome/Subsonic серверами"""

    def __init__(self):
        self.base_url: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.jwt_token: Optional[str] = None
        self.salt: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._server_version: Optional[str] = None
        self._connected: bool = False

    async def connect(
        self,
        base_url: str,
        username: str,
        password: Optional[str] = None,
        jwt_token: Optional[str] = None
    ) -> bool:
        """
        Подключение к Navidrome серверу

        Args:
            base_url: URL сервера (например, https://music.example.com)
            username: Имя пользователя
            password: Пароль (для MD5 аутентификации)
            jwt_token: JWT токен (альтернатива паролю)

        Returns:
            True если подключение успешно
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.jwt_token = jwt_token

        try:
            # Проверка подключения через ping
            response = await self._request('ping')
            if response and response.get('status') == 'ok':
                self._connected = True
                # Получение версии сервера
                versions = response.get('version', '1.0.0')
                self._server_version = versions
                return True
        except Exception as e:
            print(f"Navidrome connection error: {e}")

        self._connected = False
        return False

    def _get_auth_params(self) -> Dict[str, str]:
        """Генерация параметров аутентификации Subsonic"""
        import random
        import string

        # Генерация случайного salt
        if not self.salt:
            self.salt = ''.join(random.choices(string.hexdigits.lower(), k=8))

        # Вычисление MD5 хеша: md5(password + salt)
        if self.password:
            token = hashlib.md5(f"{self.password}{self.salt}".encode()).hexdigest()
        else:
            token = ""

        return {
            'u': self.username,
            't': token,
            's': self.salt,
            'v': '1.16.1',  # Версия Subsonic API
            'c': 'UltimateMusicApp',
            'f': 'json'  # Формат ответа
        }

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        use_auth: bool = True
    ) -> Optional[Dict]:
        """HTTP запрос к Subsonic API"""
        if not self.base_url:
            return None

        url = f"{self.base_url}/rest/{endpoint}"

        # Параметры аутентификации
        auth_params = self._get_auth_params() if use_auth else {}

        # JWT аутентификация
        headers = {}
        if self.jwt_token:
            headers['Authorization'] = f'Bearer {self.jwt_token}'
            # Для JWT не нужны параметры u, t, s
            if self.jwt_token:
                auth_params = {'v': '1.16.1', 'c': 'UltimateMusicApp', 'f': 'json'}

        # Объединение параметров
        all_params = {**auth_params, **(params or {})}

        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(url, params=all_params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Subsonic оборачивает ответ в <subsonic-response>
                        if 'subsonic-response' in data:
                            return data['subsonic-response']
                        return data
                    else:
                        print(f"Navidrome API error: {resp.status}")
                        return None
            except Exception as e:
                print(f"Navidrome request error: {e}")
                return None

    async def get_indexes(self) -> List[Dict]:
        """Получение списка всех артистов (алфавитный указатель)"""
        response = await self._request('getIndexes')
        if not response:
            return []

        indexes = response.get('indexes', {})
        artists = indexes.get('index', [])

        result = []
        for index in artists:
            for artist in index.get('artist', []):
                result.append({
                    'id': artist.get('id'),
                    'name': artist.get('artist', artist.get('name')),
                    'cover': artist.get('coverArt'),
                    'album_count': artist.get('albumCount', 0),
                    'starred': artist.get('starred') is not None
                })

        return result

    async def get_artist(self, artist_id: str) -> Optional[Dict]:
        """Получение информации об артисте"""
        response = await self._request('getArtist', {'id': artist_id})
        if not response:
            return None

        artist = response.get('artist', {})
        return {
            'id': artist.get('id'),
            'name': artist.get('name'),
            'cover': artist.get('coverArt'),
            'album_count': artist.get('albumCount', 0),
            'song_count': artist.get('songCount', 0),
            'size': artist.get('size', 0),  # в байтах
            'starred': artist.get('starred') is not None,
            'similar_artists': [
                {'id': a.get('id'), 'name': a.get('name')}
                for a in artist.get('similarArtist', [])
            ],
            'albums': [
                {
                    'id': a.get('id'),
                    'name': a.get('name'),
                    'cover': a.get('coverArt'),
                    'year': a.get('year'),
                    'created': a.get('created')
                }
                for a in artist.get('album', [])
            ]
        }

    async def get_artist_songs(self, artist_id: str) -> List[Track]:
        """Получение всех треков артиста"""
        response = await self._request('getArtist', {'id': artist_id})
        if not response:
            return []

        artist = response.get('artist', {})
        tracks = []

        for album in artist.get('album', []):
            album_tracks = await self.get_album(album.get('id'))
            if album_tracks and 'song' in album_tracks:
                for song in album_tracks['song']:
                    track = self._parse_song(song)
                    if track:
                        tracks.append(track)

        return tracks

    async def get_album(self, album_id: str) -> Optional[Dict]:
        """Получение альбома с треками"""
        response = await self._request('getAlbum', {'id': album_id})
        if not response:
            return None

        album = response.get('album', {})
        return album

    async def get_song(self, song_id: str) -> Optional[Track]:
        """Получение информации о треке"""
        response = await self._request('getSong', {'id': song_id})
        if not response:
            return None

        song = response.get('song', {})
        return self._parse_song(song)

    def _parse_song(self, song: Dict) -> Optional[Track]:
        """Парсинг трека из Subsonic API"""
        try:
            # Получение URL для стриминга
            stream_url = f"{self.base_url}/rest/stream?id={song.get('id')}"
            stream_params = self._get_auth_params()
            stream_url += '&' + '&'.join(f"{k}={v}" for k, v in stream_params.items())

            # Получение URL для обложки
            cover_id = song.get('coverArt', song.get('albumId'))
            cover_url = None
            if cover_id:
                cover_url = f"{self.base_url}/rest/getCoverArt?id={cover_id}"
                cover_params = self._get_auth_params()
                cover_url += '&' + '&'.join(f"{k}={v}" for k, v in cover_params.items())

            return Track(
                id=song.get('id'),
                title=song.get('title', 'Unknown'),
                artist=song.get('artist', 'Unknown'),
                artist_id=song.get('artistId'),
                duration=song.get('duration', 0),
                stream_url=stream_url,
                cover=cover_url,
                source="navidrome",
                album=song.get('album'),
                album_id=song.get('albumId'),
                track=song.get('track'),
                year=song.get('year'),
                genres=[song.get('genre')] if song.get('genre') else [],
                is_starred=song.get('starred') is not None,
                play_count=song.get('playCount', 0),
                content_type=song.get('contentType', 'audio/mpeg'),
                bit_rate=song.get('bitRate', 320),
                path=song.get('path'),  # Путь к файлу на сервере
                suffix=song.get('suffix'),  # Расширение файла
                size=song.get('size', 0),  # Размер в байтах
                created=song.get('created')
            )
        except Exception as e:
            print(f"Error parsing Navidrome song: {e}")
            return None

    async def search3(self, query: str, limit: int = 20) -> Dict[str, List]:
        """
        Поиск по всем типам контента

        Args:
            query: Поисковый запрос
            limit: Количество результатов

        Returns:
            Dict с ключами: tracks, artists, albums
        """
        response = await self._request('search3', {
            'query': query,
            'songCount': limit,
            'artistCount': limit // 2,
            'albumCount': limit // 2
        })

        if not response:
            return {"tracks": [], "artists": [], "albums": []}

        search_result = response.get('searchResult3', {})

        # Парсинг треков
        tracks = []
        for song in search_result.get('song', []):
            track = self._parse_song(song)
            if track:
                tracks.append(track)

        # Парсинг артистов
        artists = []
        for artist in search_result.get('artist', []):
            artists.append({
                'id': artist.get('id'),
                'name': artist.get('artist', artist.get('name')),
                'cover': artist.get('coverArt'),
                'source': 'navidrome'
            })

        # Парсинг альбомов
        albums = []
        for album in search_result.get('album', []):
            albums.append({
                'id': album.get('id'),
                'name': album.get('name'),
                'cover': album.get('coverArt'),
                'artist': album.get('artist'),
                'artist_id': album.get('artistId'),
                'year': album.get('year'),
                'created': album.get('created'),
                'source': 'navidrome'
            })

        return {
            "tracks": tracks,
            "artists": artists,
            "albums": albums
        }

    async def get_starred(self) -> Dict[str, List]:
        """Получение избранных треков, альбомов и артистов"""
        response = await self._request('getStarred2')
        if not response:
            return {"tracks": [], "albums": [], "artists": []}

        starred = response.get('starred2', {})

        tracks = [self._parse_song(s) for s in starred.get('song', []) if self._parse_song(s)]
        albums = [
            {
                'id': a.get('id'),
                'name': a.get('name'),
                'cover': a.get('coverArt'),
                'artist': a.get('artist'),
                'source': 'navidrome'
            }
            for a in starred.get('album', [])
        ]
        artists = [
            {
                'id': a.get('id'),
                'name': a.get('artist', a.get('name')),
                'cover': a.get('coverArt'),
                'source': 'navidrome'
            }
            for a in starred.get('artist', [])
        ]

        return {"tracks": tracks, "albums": albums, "artists": artists}

    async def star(self, ids: List[str], unstar: bool = False) -> bool:
        """Добавление/удаление из избранного"""
        endpoint = 'unstar' if unstar else 'star'
        params = {'id': ids}
        response = await self._request(endpoint, params)
        return response is not None

    async def get_playlists(self) -> List[Dict]:
        """Получение списка плейлистов"""
        response = await self._request('getPlaylists')
        if not response:
            return []

        playlists = response.get('playlists', {}).get('playlist', [])
        return [
            {
                'id': p.get('id'),
                'name': p.get('name'),
                'comment': p.get('comment'),
                'song_count': p.get('songCount', 0),
                'duration': p.get('duration', 0),
                'public': p.get('public', False),
                'owner': p.get('owner'),
                'created': p.get('created'),
                'changed': p.get('changed'),
                'cover': p.get('coverArt')
            }
            for p in playlists
        ]

    async def get_playlist(self, playlist_id: str) -> Optional[Dict]:
        """Получение плейлиста с треками"""
        response = await self._request('getPlaylist', {'id': playlist_id})
        if not response:
            return None

        playlist = response.get('playlist', {})
        tracks = [self._parse_song(s) for s in playlist.get('entry', []) if self._parse_song(s)]

        return {
            'id': playlist.get('id'),
            'name': playlist.get('name'),
            'comment': playlist.get('comment'),
            'song_count': playlist.get('songCount', 0),
            'duration': playlist.get('duration', 0),
            'public': playlist.get('public', False),
            'owner': playlist.get('owner'),
            'created': playlist.get('created'),
            'changed': playlist.get('changed'),
            'cover': playlist.get('coverArt'),
            'tracks': tracks
        }

    async def create_playlist(self, name: str, comment: str = "") -> Optional[str]:
        """Создание плейлиста"""
        response = await self._request('createPlaylist', {'name': name, 'comment': comment})
        if response:
            return response.get('id')
        return None

    async def update_playlist(
        self,
        playlist_id: str,
        name: Optional[str] = None,
        comment: Optional[str] = None
    ) -> bool:
        """Обновление плейлиста"""
        params = {'playlistId': playlist_id}
        if name:
            params['name'] = name
        if comment:
            params['comment'] = comment

        response = await self._request('updatePlaylist', params)
        return response is not None

    async def delete_playlist(self, playlist_id: str) -> bool:
        """Удаление плейлиста"""
        response = await self._request('deletePlaylist', {'id': playlist_id})
        return response is not None

    async def add_to_playlist(self, playlist_id: str, song_ids: List[str]) -> bool:
        """Добавление треков в плейлист"""
        params = {'playlistId': playlist_id, 'songIdToAdd': song_ids}
        response = await self._request('updatePlaylist', params)
        return response is not None

    async def remove_from_playlist(self, playlist_id: str, indices: List[int]) -> bool:
        """Удаление треков из плейлиста по индексу"""
        params = {'playlistId': playlist_id, 'songIndexToRemove': indices}
        response = await self._request('updatePlaylist', params)
        return response is not None

    async def get_genres(self) -> List[Dict]:
        """Получение списка жанров"""
        response = await self._request('getGenres')
        if not response:
            return []

        genres = response.get('genres', {}).get('genre', [])
        return [
            {
                'name': g.get('value'),
                'count': g.get('albumCount', 0) + g.get('songCount', 0),
                'album_count': g.get('albumCount', 0),
                'song_count': g.get('songCount', 0)
            }
            for g in genres
        ]

    async def get_songs_by_genre(self, genre: str, limit: int = 20) -> List[Track]:
        """Получение треков по жанру"""
        response = await self._request('getSongsByGenre', {'genre': genre, 'count': limit})
        if not response:
            return []

        songs = response.get('songsByGenre', {}).get('song', [])
        return [self._parse_song(s) for s in songs if self._parse_song(s)]

    async def get_now_playing(self) -> List[Dict]:
        """Получение информации о том, что сейчас слушают другие пользователи"""
        response = await self._request('getNowPlaying')
        if not response:
            return []

        playing = response.get('nowPlaying', {}).get('entry', [])
        return [
            {
                'user': p.get('userName'),
                'track': self._parse_song(p),
                'played': p.get('played'),
                'minutes_ago': p.get('minutesAgo', 0)
            }
            for p in playing
        ]

    async def get_scan_status(self) -> Dict:
        """Получение статуса сканирования библиотеки"""
        response = await self._request('getScanStatus')
        if not response:
            return {'scanning': False, 'count': 0}

        status = response.get('scanStatus', {})
        return {
            'scanning': status.get('scanning', False),
            'count': status.get('count', 0)
        }

    async def start_scan(self) -> bool:
        """Запуск сканирования библиотеки"""
        response = await self._request('startScan')
        return response is not None

    async def get_stream_url(self, song_id: str, max_bit_rate: Optional[int] = None) -> str:
        """Получение URL для стриминга трека"""
        url = f"{self.base_url}/rest/stream?id={song_id}"
        params = self._get_auth_params()

        if max_bit_rate:
            params['maxBitRate'] = max_bit_rate

        url += '&' + '&'.join(f"{k}={v}" for k, v in params.items())
        return url

    async def get_download_url(self, song_id: str) -> str:
        """Получение URL для скачивания трека"""
        url = f"{self.base_url}/rest/download?id={song_id}"
        params = self._get_auth_params()
        url += '&' + '&'.join(f"{k}={v}" for k, v in params.items())
        return url

    @property
    def is_connected(self) -> bool:
        """Проверка подключения к серверу"""
        return self._connected

    @property
    def server_version(self) -> Optional[str]:
        """Версия сервера"""
        return self._server_version


# Глобальный экземпляр
navidrome_service = NavidromeService()
