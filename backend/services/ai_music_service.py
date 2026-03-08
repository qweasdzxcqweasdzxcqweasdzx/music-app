"""
AI Music Studio Service

Интеграция с ИИ-сервисами для генерации и обработки музыки:

1. Генерация музыки по тексту/промпту:
   - Suno AI API (https://suno.com)
   - Wondera API
   - Hugging Face MusicGen

2. Генерация фоновой музыки:
   - Mubert API (https://mubert.com)

3. Разделение треков на стемы (stems):
   - LALAL.AI API (https://www.lalal.ai)
   - Moises API

4. Синтез речи/вокала:
   - ElevenLabs API (https://elevenlabs.io)

5. Открытые модели:
   - Hugging Face Inference API
   - Replicate API
"""

import aiohttp
import time
import base64
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from config import settings


class GenerationStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StemType(Enum):
    VOCALS = "vocals"
    INSTRUMENTAL = "instrumental"
    DRUMS = "drums"
    BASS = "bass"
    GUITAR = "guitar"
    PIANO = "piano"
    OTHER = "other"


class AIMusicService:
    """Сервис для ИИ-генерации и обработки музыки"""

    def __init__(self):
        # Suno API
        self.suno_api_key = settings.SUNO_API_KEY
        self.suno_base_url = "https://studio-api.suno.ai"

        # Mubert API
        self.mubert_client_id = settings.MUBERT_CLIENT_ID
        self.mubert_token = settings.MUBERT_TOKEN
        self.mubert_base_url = "https://api.mubert.com"

        # LALAL.AI API
        self.lalal_api_key = settings.LALAL_API_KEY
        self.lalal_base_url = "https://api.lalal.ai"

        # ElevenLabs API
        self.elevenlabs_api_key = settings.ELEVENLABS_API_KEY
        self.elevenlabs_base_url = "https://api.elevenlabs.io"

        # Hugging Face API
        self.huggingface_token = settings.HUGGINGFACE_TOKEN
        self.huggingface_base_url = "https://api-inference.huggingface.co/models"

        # Replicate API
        self.replicate_api_token = settings.REPLICATE_API_TOKEN
        self.replicate_base_url = "https://api.replicate.com"

        # Кэш для задач генерации
        self._generation_tasks: Dict[str, Dict] = {}

    # ==================== Suno AI ====================

    async def suno_generate(
        self,
        prompt: str,
        tags: Optional[str] = None,
        title: Optional[str] = None,
        make_instrumental: bool = False,
        wait_for_audio: bool = False
    ) -> Dict:
        """
        Генерация музыки через Suno AI

        Args:
            prompt: Описание песни (текст, стиль, настроение)
            tags: Жанры/теги (например: "pop rock energetic")
            title: Название трека
            make_instrumental: Сделать инструментальным
            wait_for_audio: Ждать завершения генерации

        Returns:
            Информация о задаче генерации
        """
        if not self.suno_api_key:
            return {"error": "Suno API key not configured"}

        payload = {
            "prompt": prompt,
            "tags": tags or "",
            "title": title or "",
            "make_instrumental": make_instrumental,
            "mv": "chirp-v3-0",  # Модель
            "continue_at": None,
            "continue_clip_id": None
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.suno_base_url}/api/generate/v2/",
                    headers={
                        "Authorization": f"Bearer {self.suno_api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        task_id = data.get("clips", [{}])[0].get("id")

                        task_info = {
                            "task_id": task_id,
                            "status": GenerationStatus.PENDING,
                            "provider": "suno",
                            "prompt": prompt,
                            "created_at": time.time()
                        }
                        self._generation_tasks[task_id] = task_info

                        if wait_for_audio:
                            return await self.suno_wait_for_generation(task_id)

                        return task_info
                    else:
                        return {"error": f"Suno API error: {resp.status}"}
            except Exception as e:
                return {"error": str(e)}

    async def suno_get_generation(self, task_id: str) -> Dict:
        """Получение статуса генерации Suno"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.suno_base_url}/api/feed/{task_id}",
                    headers={"Authorization": f"Bearer {self.suno_api_key}"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if isinstance(data, list) and data:
                            clip = data[0]
                            status = clip.get("status")

                            if status == "complete":
                                return {
                                    "task_id": task_id,
                                    "status": GenerationStatus.COMPLETED,
                                    "audio_url": clip.get("audio_url"),
                                    "video_url": clip.get("video_url"),
                                    "title": clip.get("title"),
                                    "artist": clip.get("artist"),
                                    "duration": clip.get("duration"),
                                    "prompt": clip.get("prompt"),
                                    "tags": clip.get("tags"),
                                    "created_at": clip.get("created_at")
                                }
                            elif status == "error":
                                return {
                                    "task_id": task_id,
                                    "status": GenerationStatus.FAILED,
                                    "error": clip.get("error_message", "Unknown error")
                                }
                            else:
                                return {
                                    "task_id": task_id,
                                    "status": GenerationStatus.PROCESSING,
                                    "progress": clip.get("progress", 0)
                                }
            except Exception as e:
                return {"error": str(e)}

        return {"task_id": task_id, "status": GenerationStatus.FAILED}

    async def suno_wait_for_generation(
        self,
        task_id: str,
        timeout: int = 120,
        poll_interval: int = 5
    ) -> Dict:
        """Ожидание завершения генерации"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = await self.suno_get_generation(task_id)
            status = result.get("status")

            if status == GenerationStatus.COMPLETED:
                return result
            elif status == GenerationStatus.FAILED:
                return result

            await asyncio.sleep(poll_interval)

        return {
            "task_id": task_id,
            "status": GenerationStatus.FAILED,
            "error": "Generation timeout"
        }

    # ==================== Mubert ====================

    async def mubert_generate(
        self,
        prompt: str,
        duration: int = 60,
        mood: Optional[str] = None,
        genre: Optional[str] = None,
        tempo: Optional[int] = None
    ) -> Dict:
        """
        Генерация фоновой музыки через Mubert

        Args:
            prompt: Описание настроения/атмосферы
            duration: Длительность в секундах
            mood: Настроение (calm, energetic, dark, etc.)
            genre: Жанр (ambient, electronic, etc.)
            tempo: Темп (BPM)

        Returns:
            Информация о задаче генерации
        """
        if not self.mubert_token:
            return {"error": "Mubert API token not configured"}

        # Mubert использует JWT для аутентификации
        headers = {
            "x-mubert-token": self.mubert_token,
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "duration": duration,
            "mood": mood,
            "genre": genre,
            "tempo": tempo,
            "output_format": "mp3"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.mubert_base_url}/render/tasks",
                    headers=headers,
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        task_id = data.get("id")

                        task_info = {
                            "task_id": task_id,
                            "status": GenerationStatus.PENDING,
                            "provider": "mubert",
                            "prompt": prompt,
                            "duration": duration,
                            "created_at": time.time()
                        }
                        self._generation_tasks[task_id] = task_info

                        return task_info
                    else:
                        return {"error": f"Mubert API error: {resp.status}"}
            except Exception as e:
                return {"error": str(e)}

    async def mubert_get_task_status(self, task_id: str) -> Dict:
        """Получение статуса задачи Mubert"""
        headers = {"x-mubert-token": self.mubert_token}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.mubert_base_url}/render/tasks/{task_id}",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        status = data.get("status")

                        if status == "success":
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.COMPLETED,
                                "download_url": data.get("download_url"),
                                "duration": data.get("duration"),
                                "created_at": data.get("created_at")
                            }
                        elif status == "failed":
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.FAILED,
                                "error": data.get("error_message", "Unknown error")
                            }
                        else:
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.PROCESSING,
                                "progress": data.get("progress", 0)
                            }
            except Exception as e:
                return {"error": str(e)}

        return {"task_id": task_id, "status": GenerationStatus.FAILED}

    # ==================== LALAL.AI (Stem Separation) ====================

    async def lalal_separate_stems(
        self,
        audio_url: str,
        stem_type: StemType = StemType.VOCALS,
        enable_de_noise: bool = False
    ) -> Dict:
        """
        Разделение трека на стемы через LALAL.AI

        Args:
            audio_url: URL аудиофайла или base64 данные
            stem_type: Тип стема для выделения
            enable_de_noise: Шумоподавление

        Returns:
            Информация о задаче разделения
        """
        if not self.lalal_api_key:
            return {"error": "LALAL.AI API key not configured"}

        headers = {
            "Authorization": f"Bearer {self.lalal_api_key}",
            "Content-Type": "application/json"
        }

        # Определение типа входных данных
        if audio_url.startswith('http'):
            payload = {
                "input_url": audio_url,
                "stem_type": stem_type.value,
                "enable_de_noise": enable_de_noise
            }
        else:
            # Предполагаем base64
            payload = {
                "input_blob": audio_url,
                "stem_type": stem_type.value,
                "enable_de_noise": enable_de_noise
            }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.lalal_base_url}/api/v2.0/extract",
                    headers=headers,
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        task_id = data.get("task_id")

                        task_info = {
                            "task_id": task_id,
                            "status": GenerationStatus.PENDING,
                            "provider": "lalal",
                            "stem_type": stem_type.value,
                            "created_at": time.time()
                        }
                        self._generation_tasks[task_id] = task_info

                        return task_info
                    else:
                        return {"error": f"LALAL.AI error: {resp.status}"}
            except Exception as e:
                return {"error": str(e)}

    async def lalal_get_task_status(self, task_id: str) -> Dict:
        """Получение статуса задачи разделения"""
        headers = {"Authorization": f"Bearer {self.lalal_api_key}"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.lalal_base_url}/api/v2.0/progress/{task_id}",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        status = data.get("status")

                        if status == "done":
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.COMPLETED,
                                "tracks": data.get("track"),
                                "download_urls": {
                                    "instrumental": data.get("track", {}).get("instrumental"),
                                    "vocals": data.get("track", {}).get("vocals")
                                }
                            }
                        elif status == "error":
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.FAILED,
                                "error": data.get("message", "Unknown error")
                            }
                        else:
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.PROCESSING,
                                "progress": data.get("progress", 0),
                                "eta": data.get("eta", 0)
                            }
            except Exception as e:
                return {"error": str(e)}

        return {"task_id": task_id, "status": GenerationStatus.FAILED}

    # ==================== ElevenLabs (TTS/Voice Synthesis) ====================

    async def elevenlabs_generate(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel (default)
        model_id: str = "eleven_monolingual_v1",
        style: float = 0.0,
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> Dict:
        """
        Генерация речи/вокала через ElevenLabs

        Args:
            text: Текст для озвучки
            voice_id: ID голоса
            model_id: ID модели
            style: Стиль (0.0-1.0)
            stability: Стабильность (0.0-1.0)
            similarity_boost: Усиление схожести (0.0-1.0)

        Returns:
            Аудио данные или URL
        """
        if not self.elevenlabs_api_key:
            return {"error": "ElevenLabs API key not configured"}

        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style
            }
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.elevenlabs_base_url}/v1/text-to-speech/{voice_id}",
                    headers=headers,
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        # Получение аудио данных
                        audio_data = await resp.read()
                        audio_base64 = base64.b64encode(audio_data).decode()

                        return {
                            "status": GenerationStatus.COMPLETED,
                            "audio_base64": audio_base64,
                            "content_type": "audio/mpeg",
                            "voice_id": voice_id,
                            "model_id": model_id,
                            "text_length": len(text)
                        }
                    else:
                        error_data = await resp.json() if resp.status < 500 else {}
                        return {"error": f"ElevenLabs error: {resp.status}", "details": error_data}
            except Exception as e:
                return {"error": str(e)}

    async def elevenlabs_get_voices(self) -> List[Dict]:
        """Получение списка доступных голосов"""
        if not self.elevenlabs_api_key:
            return []

        headers = {"xi-api-key": self.elevenlabs_api_key}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.elevenlabs_base_url}/v1/voices",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [
                            {
                                "voice_id": v.get("voice_id"),
                                "name": v.get("name"),
                                "category": v.get("category"),
                                "description": v.get("description"),
                                "preview_url": v.get("preview_url"),
                                "available_for_tiers": v.get("available_for_tiers")
                            }
                            for v in data.get("voices", [])
                        ]
            except Exception as e:
                print(f"Error getting ElevenLabs voices: {e}")

        return []

    # ==================== Hugging Face MusicGen ====================

    async def musicgen_generate(
        self,
        prompt: str,
        duration: int = 10,
        model_id: str = "facebook/musicgen-large"
    ) -> Dict:
        """
        Генерация музыки через Hugging Face MusicGen

        Args:
            prompt: Описание музыки
            duration: Длительность в секундах (макс 30 для бесплатного API)
            model_id: ID модели

        Returns:
            Информация о задаче генерации
        """
        if not self.huggingface_token:
            return {"error": "Hugging Face token not configured"}

        headers = {
            "Authorization": f"Bearer {self.huggingface_token}",
            "Content-Type": "application/json"
        }

        # MusicGen принимает текст и возвращает аудио
        payload = {
            "inputs": prompt,
            "parameters": {
                "duration": duration
            }
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.huggingface_base_url}/{model_id}",
                    headers=headers,
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        # Получение аудио данных
                        audio_data = await resp.read()
                        audio_base64 = base64.b64encode(audio_data).decode()

                        return {
                            "status": GenerationStatus.COMPLETED,
                            "audio_base64": audio_base64,
                            "content_type": "audio/flac",
                            "prompt": prompt,
                            "duration": duration,
                            "model": model_id
                        }
                    elif resp.status == 503:
                        # Модель загружается
                        return {
                            "status": GenerationStatus.PENDING,
                            "error": "Model loading, please try again",
                            "estimated_time": 30
                        }
                    else:
                        error_data = await resp.json() if resp.status < 500 else {}
                        return {"error": f"Hugging Face error: {resp.status}", "details": error_data}
            except Exception as e:
                return {"error": str(e)}

    # ==================== Replicate (разные модели) ====================

    async def replicate_generate(
        self,
        model: str,
        version: str,
        input_data: Dict
    ) -> Dict:
        """
        Генерация через Replicate API

        Args:
            model: Название модели (например, meta/musicgen)
            version: Версия модели
            input_data: Параметры для модели

        Returns:
            Информация о задаче генерации
        """
        if not self.replicate_api_token:
            return {"error": "Replicate API token not configured"}

        headers = {
            "Authorization": f"Bearer {self.replicate_api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "version": version,
            "input": input_data
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.replicate_base_url}/predictions",
                    headers=headers,
                    json=payload
                ) as resp:
                    if resp.status in (200, 201):
                        data = await resp.json()
                        task_id = data.get("id")

                        task_info = {
                            "task_id": task_id,
                            "status": GenerationStatus.PENDING,
                            "provider": "replicate",
                            "model": model,
                            "created_at": time.time()
                        }
                        self._generation_tasks[task_id] = task_info

                        return task_info
                    else:
                        return {"error": f"Replicate error: {resp.status}"}
            except Exception as e:
                return {"error": str(e)}

    async def replicate_get_prediction(self, task_id: str) -> Dict:
        """Получение статуса задачи Replicate"""
        headers = {"Authorization": f"Bearer {self.replicate_api_token}"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.replicate_base_url}/predictions/{task_id}",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        status = data.get("status")

                        if status == "succeeded":
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.COMPLETED,
                                "output": data.get("output"),
                                "created_at": data.get("created_at"),
                                "completed_at": data.get("completed_at")
                            }
                        elif status == "failed":
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.FAILED,
                                "error": data.get("error", "Unknown error")
                            }
                        else:
                            return {
                                "task_id": task_id,
                                "status": GenerationStatus.PROCESSING,
                                "logs": data.get("logs")
                            }
            except Exception as e:
                return {"error": str(e)}

        return {"task_id": task_id, "status": GenerationStatus.FAILED}

    # ==================== Unified API ====================

    async def generate_music(
        self,
        provider: str,
        prompt: str,
        **kwargs
    ) -> Dict:
        """
        Универсальный метод генерации музыки

        Args:
            provider: Провайдер (suno, mubert, musicgen, replicate)
            prompt: Описание/промпт
            **kwargs: Дополнительные параметры

        Returns:
            Информация о задаче генерации
        """
        if provider == "suno":
            return await self.suno_generate(prompt, **kwargs)
        elif provider == "mubert":
            return await self.mubert_generate(prompt, **kwargs)
        elif provider == "musicgen":
            return await self.musicgen_generate(prompt, **kwargs)
        elif provider == "replicate":
            return await self.replicate_generate(**kwargs)
        else:
            return {"error": f"Unknown provider: {provider}"}

    async def get_generation_status(self, provider: str, task_id: str) -> Dict:
        """Получение статуса задачи генерации"""
        if provider == "suno":
            return await self.suno_get_generation(task_id)
        elif provider == "mubert":
            return await self.mubert_get_task_status(task_id)
        elif provider == "lalal":
            return await self.lalal_get_task_status(task_id)
        elif provider == "replicate":
            return await self.replicate_get_prediction(task_id)
        else:
            return {"error": f"Unknown provider: {provider}"}

    async def separate_stems(
        self,
        audio_url: str,
        stem_type: str = "vocals",
        provider: str = "lalal"
    ) -> Dict:
        """Разделение трека на стемы"""
        if provider == "lalal":
            return await self.lalal_separate_stems(
                audio_url,
                StemType(stem_type)
            )
        else:
            return {"error": f"Unknown stem separation provider: {provider}"}

    async def generate_voice(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        provider: str = "elevenlabs"
    ) -> Dict:
        """Генерация голоса/речи"""
        if provider == "elevenlabs":
            return await self.elevenlabs_generate(text, voice_id)
        else:
            return {"error": f"Unknown voice provider: {provider}"}

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Получение информации о задаче из кэша"""
        return self._generation_tasks.get(task_id)


# Глобальный экземпляр
ai_music_service = AIMusicService()

# Import asyncio for wait methods
import asyncio
