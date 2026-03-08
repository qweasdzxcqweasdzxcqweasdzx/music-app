"""
Audio Streaming Service

Сервис для получения прямых ссылок на аудио из YouTube
"""

import asyncio
from typing import Optional, Dict
import yt_dlp


class AudioStreamingService:
    """Сервис для получения аудио потоков"""

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best',
            'extract-audio': False,  # Получаем оригинальный формат
        }
        if proxy:
            self.ydl_opts['proxy'] = proxy

    async def get_youtube_audio_url(self, video_id: str) -> Optional[Dict]:
        """
        Получение прямой ссылки на аудио с YouTube

        Args:
            video_id: ID видео на YouTube

        Returns:
            Dict с URL и информацией о треке
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._extract_audio,
                f"https://www.youtube.com/watch?v={video_id}"
            )
            return result
        except Exception as e:
            print(f"Audio streaming error: {e}")
            return None

    def _extract_audio(self, url: str) -> Optional[Dict]:
        """Извлечение аудио URL (синхронно)"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info and 'formats' in info:
                    # Ищем лучший аудио формат
                    audio_format = None
                    for fmt in info['formats']:
                        if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                            audio_format = fmt
                            break

                    # Если не нашли чистое аудио, берём лучшее с аудио
                    if not audio_format:
                        for fmt in info['formats']:
                            if fmt.get('acodec') != 'none':
                                audio_format = fmt
                                break

                    # Fallback на последний формат
                    if not audio_format and info.get('formats'):
                        audio_format = info['formats'][-1]

                    if audio_format:
                        return {
                            'url': audio_format.get('url'),
                            'duration': info.get('duration', 0),
                            'title': info.get('title', ''),
                            'uploader': info.get('uploader', ''),
                            'thumbnail': info.get('thumbnail', ''),
                            'format': audio_format.get('format_note', 'unknown'),
                            'quality': audio_format.get('quality', 0)
                        }

                return None
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None

    async def get_direct_stream(self, video_id: str) -> Optional[str]:
        """
        Получение прямой ссылки для стриминга

        Args:
            video_id: ID видео на YouTube

        Returns:
            Прямая ссылка на аудио или None
        """
        result = await self.get_youtube_audio_url(video_id)
        if result:
            return result.get('url')
        return None


# Глобальный экземпляр
audio_streaming_service = AudioStreamingService()
