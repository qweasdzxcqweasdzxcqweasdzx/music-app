"""
Audio Streaming Service

Унифицированный сервис для получения полноценного аудио из различных источников:
1. VK Music - основной источник (полноценные треки)
2. YouTube - через yt-dlp (полноценные треки)
3. SoundCloud - основной источник музыки

Приоритет источников:
1. SoundCloud (основной)
2. VK (если есть OAuth токены)
3. YouTube (если установлен yt-dlp)
"""

import asyncio
from typing import Optional, Dict, List
from models_main import Track


class AudioStreamingService:
    """Сервис для получения полноценного аудио"""

    def __init__(self):
        self.vk_service = None
        self.youtube_service = None
        self.soundcloud_service = None
        self._vk_available = False
        self._youtube_available = False
        self._soundcloud_available = False

    def initialize(
        self,
        vk_service=None,
        youtube_service=None,
        soundcloud_service=None
    ):
        """Инициализация сервисов"""
        self.vk_service = vk_service
        self.youtube_service = youtube_service
        self.soundcloud_service = soundcloud_service

        # Проверяем доступность
        self._vk_available = vk_service is not None
        self._youtube_available = youtube_service is not None
        self._soundcloud_available = soundcloud_service is not None

    async def get_audio_url(self, track: Track) -> Optional[Dict]:
        """
        Получение URL аудио для трека

        Args:
            track: Трек для которого нужен URL

        Returns:
            Dict с URL и метаданными или None
        """
        # Пробуем SoundCloud (приоритет)
        if self._soundcloud_available and track.stream_url:
            return {
                "url": track.stream_url,
                "source": "soundcloud",
                "is_preview": False,
                "duration": track.duration
            }

        # Пробуем VK (резерв)
        if self._vk_available:
            vk_url = await self._get_vk_audio(track)
            if vk_url:
                return vk_url

        # Пробуем YouTube (резерв)
        if self._youtube_available:
            yt_url = await self._get_youtube_audio(track)
            if yt_url:
                return yt_url

        return None

    async def _get_vk_audio(self, track: Track) -> Optional[Dict]:
        """Получение аудио из VK"""
        try:
            # Поиск трека в VK
            query = f"{track.artist} {track.title}"
            vk_tracks = await self.vk_service.search(query, limit=5)

            if vk_tracks:
                # Находим наиболее подходящий трек
                best_match = self._find_best_match(track, vk_tracks)
                if best_match:
                    return {
                        "url": best_match.stream_url,
                        "source": "vk",
                        "is_preview": False,
                        "duration": best_match.duration,
                        "track": best_match
                    }
        except Exception as e:
            print(f"VK audio error: {e}")
        
        return None

    async def _get_youtube_audio(self, track: Track) -> Optional[Dict]:
        """Получение аудио из YouTube"""
        try:
            # Поиск трека на YouTube
            query = f"{track.artist} {track.title} official audio"
            yt_tracks = await self.youtube_service.search(query, limit=5)

            if yt_tracks:
                # Находим наиболее подходящий трек
                best_match = self._find_best_match(track, yt_tracks)
                if best_match:
                    # Получаем прямой URL потока
                    stream_url = await self.youtube_service.get_track_stream(
                        best_match.id or best_match.stream_url
                    )
                    
                    if stream_url:
                        return {
                            "url": stream_url,
                            "source": "youtube",
                            "is_preview": False,
                            "duration": best_match.duration,
                            "track": best_match
                        }
        except Exception as e:
            print(f"YouTube audio error: {e}")
        
        return None

    def _find_best_match(
        self,
        original: Track,
        candidates: List[Track]
    ) -> Optional[Track]:
        """Поиск наиболее подходящего трека"""
        best_score = 0
        best_match = None

        original_title = original.title.lower()
        original_artist = original.artist.lower()

        for candidate in candidates:
            score = 0

            # Сравниваем названия
            candidate_title = candidate.title.lower()
            if original_title in candidate_title or candidate_title in original_title:
                score += 50

            # Сравниваем артистов
            candidate_artist = candidate.artist.lower()
            if original_artist in candidate_artist or candidate_artist in original_artist:
                score += 30

            # Сравниваем длительность (разница не более 20%)
            if original.duration > 0 and candidate.duration > 0:
                duration_diff = abs(original.duration - candidate.duration)
                duration_ratio = duration_diff / max(original.duration, candidate.duration)
                if duration_ratio < 0.2:
                    score += 20

            if score > best_score:
                best_score = score
                best_match = candidate

        # Возвращаем если найдено совпадение с score > 50
        return best_match if best_score > 50 else None

    async def search_audio(
        self,
        query: str,
        artist: str = "",
        limit: int = 10
    ) -> List[Dict]:
        """
        Поиск аудио по запросу

        Args:
            query: Поисковый запрос (название трека)
            artist: Имя артиста
            limit: Количество результатов

        Returns:
            Список найденных аудио
        """
        results = []

        # Ищем во всех доступных источниках
        if self._vk_available:
            vk_results = await self.vk_service.search(f"{artist} {query}", limit=limit)
            for track in vk_results:
                results.append({
                    "track": track,
                    "source": "vk",
                    "url": track.stream_url
                })

        if self._youtube_available:
            yt_results = await self.youtube_service.search(f"{artist} {query}", limit=limit)
            for track in yt_results:
                results.append({
                    "track": track,
                    "source": "youtube",
                    "url": track.stream_url
                })

        return results[:limit]

    async def download_track(
        self,
        track: Track,
        output_path: str
    ) -> Optional[str]:
        """
        Загрузка трека в файл

        Args:
            track: Трек для загрузки
            output_path: Путь для сохранения

        Returns:
            Путь к файлу или None
        """
        # Получаем URL аудио
        audio_data = await self.get_audio_url(track)
        if not audio_data:
            return None

        # Если это YouTube, используем yt-dlp для загрузки
        if audio_data["source"] == "youtube":
            return await self._download_youtube_track(
                audio_data["url"],
                output_path
            )

        # Для VK просто возвращаем URL (прямая загрузка)
        return audio_data["url"]

    async def _download_youtube_track(
        self,
        url: str,
        output_path: str
    ) -> Optional[str]:
        """Загрузка трека с YouTube"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            return f"{output_path}.mp3"
        except Exception as e:
            print(f"YouTube download error: {e}")
            return None


# Глобальный экземпляр
audio_streaming_service = AudioStreamingService()
