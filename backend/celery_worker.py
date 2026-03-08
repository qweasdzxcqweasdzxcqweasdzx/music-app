"""
Celery Worker для фоновых задач

Задачи:
- AI генерация музыки (Suno, Mubert, MusicGen)
- Разделение треков на стемы (LALAL.AI)
- Синтез голоса (ElevenLabs)
- Долгие операции обработки
- Периодические задачи (очистка кэша, обновление рекомендаций)
"""

from celery import Celery
from celery.schedules import crontab
import asyncio
import os

# Настройка Celery
celery_app = Celery(
    'music_app',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

# Конфигурация
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 минут максимум
    worker_prefetch_multiplier=1,
)

# Расписание периодических задач
celery_app.conf.beat_schedule = {
    # Очистка кэша каждый час
    'cleanup-cache-hourly': {
        'task': 'tasks.cleanup_cache',
        'schedule': crontab(minute=0),  # Каждый час
    },
    # Обновление рекомендаций каждый день
    'update-recommendations-daily': {
        'task': 'tasks.update_daily_recommendations',
        'schedule': crontab(hour=3, minute=0),  # В 3:00 UTC
    },
    # Очистка старых задач генерации
    'cleanup-old-tasks': {
        'task': 'tasks.cleanup_old_generation_tasks',
        'schedule': crontab(hour=2, minute=0),  # В 2:00 UTC
    },
}


# ==================== AI Генерация ====================

@celery_app.task(bind=True, max_retries=3)
def generate_music_suno(self, prompt: str, tags: str = "", title: str = "", instrumental: bool = False):
    """Генерация музыки через Suno AI"""
    from services.ai_music_service import ai_music_service

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            ai_music_service.suno_generate(
                prompt=prompt,
                tags=tags,
                title=title,
                make_instrumental=instrumental,
                wait_for_audio=False
            )
        )

        if 'error' in result:
            raise Exception(result['error'])

        # Запуск ожидания завершения генерации
        task_id = result.get('task_id')
        wait_for_suno_generation.delay(task_id)

        return {
            'status': 'pending',
            'task_id': task_id,
            'provider': 'suno'
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def wait_for_suno_generation(self, task_id: str):
    """Ожидание завершения генерации Suno"""
    from services.ai_music_service import ai_music_service
    from services.websocket_manager import ws_manager

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            ai_music_service.suno_wait_for_generation(task_id, timeout=180)
        )

        # Уведомление пользователя через WebSocket
        if result.get('status') == 'completed':
            # TODO: Получить user_id из задачи и отправить уведомление
            pass

        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(bind=True, max_retries=3)
def generate_music_mubert(self, prompt: str, duration: int = 60, mood: str = None, genre: str = None):
    """Генерация фоновой музыки через Mubert"""
    from services.ai_music_service import ai_music_service

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            ai_music_service.mubert_generate(
                prompt=prompt,
                duration=duration,
                mood=mood,
                genre=genre
            )
        )

        if 'error' in result:
            raise Exception(result['error'])

        task_id = result.get('task_id')
        wait_for_mubert_generation.delay(task_id)

        return {
            'status': 'pending',
            'task_id': task_id,
            'provider': 'mubert'
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def wait_for_mubert_generation(self, task_id: str):
    """Ожидание завершения генерации Mubert"""
    from services.ai_music_service import ai_music_service

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            ai_music_service.mubert_get_task_status(task_id)
        )
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(bind=True, max_retries=3)
def generate_music_musicgen(self, prompt: str, duration: int = 10):
    """Генерация музыки через Hugging Face MusicGen"""
    from services.ai_music_service import ai_music_service

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            ai_music_service.musicgen_generate(prompt=prompt, duration=duration)
        )

        # MusicGen генерирует быстро, результат сразу готов
        return {
            'status': result.get('status', 'completed'),
            'audio_base64': result.get('audio_base64'),
            'provider': 'musicgen'
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# ==================== Разделение треков (Stem Separation) ====================

@celery_app.task(bind=True, max_retries=3)
def separate_stems_lalal(self, audio_url: str, stem_type: str = "vocals"):
    """Разделение трека на стемы через LALAL.AI"""
    from services.ai_music_service import ai_music_service

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            ai_music_service.lalal_separate_stems(
                audio_url=audio_url,
                stem_type=stem_type
            )
        )

        if 'error' in result:
            raise Exception(result['error'])

        task_id = result.get('task_id')
        wait_for_lalal_separation.delay(task_id)

        return {
            'status': 'pending',
            'task_id': task_id,
            'provider': 'lalal'
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def wait_for_lalal_separation(self, task_id: str):
    """Ожидание завершения разделения LALAL.AI"""
    from services.ai_music_service import ai_music_service

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            ai_music_service.lalal_get_task_status(task_id)
        )
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


# ==================== Синтез голоса ====================

@celery_app.task(bind=True, max_retries=3)
def generate_voice_elevenlabs(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
    """Синтез голоса через ElevenLabs"""
    from services.ai_music_service import ai_music_service

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            ai_music_service.elevenlabs_generate(text=text, voice_id=voice_id)
        )

        return {
            'status': result.get('status', 'completed'),
            'audio_base64': result.get('audio_base64'),
            'voice_id': voice_id,
            'provider': 'elevenlabs'
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


# ==================== Периодические задачи ====================

@celery_app.task
def cleanup_cache():
    """Очистка кэша"""
    from services.cache_service import cache_service

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cache_service.clear_expired())
        return {'status': 'ok', 'message': 'Cache cleaned'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@celery_app.task
def update_daily_recommendations():
    """Обновление ежедневных рекомендаций для пользователей"""
    from services.discover_weekly_service import discover_weekly_service
    from database import get_collection
    import asyncio

    async def _update():
        users_collection = await get_collection("users")
        users = await users_collection.find({}).to_list(length=1000)

        updated_count = 0
        for user in users:
            user_id = user.get("telegram_id")
            if user_id:
                # Генерация новых рекомендаций
                # (в реальности нужно проверять дату последней генерации)
                updated_count += 1

        return {'status': 'ok', 'updated_users': updated_count}

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_update())
        return result
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@celery_app.task
def cleanup_old_generation_tasks():
    """Очистка старых задач генерации"""
    # TODO: Реализовать очистку старых задач из БД
    return {'status': 'ok', 'message': 'Old tasks cleaned'}


# ==================== Умный миксер ====================

@celery_app.task(bind=True, max_retries=3)
def generate_smart_mix(self, user_id: str, limit: int = 50):
    """Генерация умного микса для пользователя"""
    from services.smart_mixer_service import smart_mixer
    from database import get_collection
    import asyncio

    async def _generate():
        # Получение данных пользователя
        history_collection = await get_collection("play_history")
        likes_collection = await get_collection("likes")

        history = await history_collection.find(
            {"user_id": user_id}
        ).to_list(length=300)

        likes = await likes_collection.find(
            {"user_id": user_id}
        ).to_list(length=500)

        like_track_ids = [like["track_id"] for like in likes]

        # Генерация микса
        tracks = await smart_mixer.create_smart_mix(
            user_id=user_id,
            history=history,
            likes=like_track_ids,
            top_artists=[],
            limit=limit
        )

        return {
            'status': 'ok',
            'tracks': [
                {
                    'id': t.id,
                    'title': t.title,
                    'artist': t.artist,
                    'source': t.source
                }
                for t in tracks
            ]
        }

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_generate())
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def generate_infinite_radio(self, track_id: str, source: str = "soundcloud", limit: int = 50):
    """Генерация бесконечного радио на основе трека"""
    from services.smart_mixer_service import smart_mixer
    from services.soundcloud_service import soundcloud_service
    import asyncio

    async def _generate():
        # Получение seed трека
        track = await soundcloud_service.get_track(track_id)

        if not track:
            return {'status': 'error', 'message': 'Track not found'}

        tracks = await smart_mixer.create_infinite_radio(
            seed_track=track,
            limit=limit
        )

        return {
            'status': 'ok',
            'seed_track': {
                'id': track.id,
                'title': track.title,
                'artist': track.artist
            },
            'tracks': [
                {
                    'id': t.id,
                    'title': t.title,
                    'artist': t.artist,
                    'source': t.source
                }
                for t in tracks
            ]
        }

    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_generate())
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


if __name__ == '__main__':
    celery_app.start()
