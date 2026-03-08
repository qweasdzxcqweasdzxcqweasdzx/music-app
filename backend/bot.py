"""
Telegram Bot для Music Mini App

Бот обеспечивает:
- Inline режим для поиска музыки прямо в чатах
- Команды управления (/start, /search, /top, /help)
- Быстрый доступ к Mini App
"""

import logging
from typing import Optional
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    Application,
    CommandHandler,
    InlineQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from services.music_service import music_service
from config import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class MusicBot:
    """Telegram бот для музыкального приложения"""

    def __init__(self):
        self.app: Optional[Application] = None
        self.api_url = f"https://{settings.HOST}:{settings.PORT}" if settings.HOST != "0.0.0.0" else "http://localhost:8000"
        self.webapp_url = f"{self.api_url}/static/index.html"  # URL Mini App

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎵 Открыть плеер",
                    web_app=WebAppInfo(url=self.webapp_url)
                )
            ],
            [
                InlineKeyboardButton("🔍 Поиск inline", switch_inline_query_current_chat=""),
                InlineKeyboardButton("🔥 Топ треков", callback_data="top")
            ],
            [
                InlineKeyboardButton("📚 Жанры", callback_data="genres"),
                InlineKeyboardButton("🆕 Новинки", callback_data="new")
            ]
        ]

        await update.message.reply_text(
            "🎵 **Telegram Music Bot**\n\n"
            "Добро пожаловать в музыкальный стриминг без цензуры!\n\n"
            "**Возможности:**\n"
            "• 🎧 Полноценный плеер в Telegram\n"
            "• 🔍 Поиск по миллионам треков\n"
            "• 🎵 Плейлисты и лайки\n"
            "• 📀 Страницы артистов\n"
            "• ⚡ Автозамена цензурированных версий\n\n"
            "**Команды:**\n"
            "/search [запрос] - Поиск трека\n"
            "/top - Популярные треки\n"
            "/new - Новинки недели\n"
            "/genre [жанр] - Музыка по жанрам\n"
            "/help - Помощь\n\n"
            "Нажми кнопку ниже чтобы открыть плеер:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        await update.message.reply_text(
            "📖 **Помощь**\n\n"
            "**Поиск музыки:**\n"
            "• Введите название трека или артиста в inline режиме\n"
            "• Используйте команду /search [запрос]\n"
            "• Или откройте плеер через кнопку\n\n"
            "**Анти-цензура:**\n"
            "Бот автоматически находит оригинальные версии треков,\n"
            "если стандартная версия содержит цензуру.\n\n"
            "**Команды:**\n"
            "/search [запрос] - Поиск по названию\n"
            "/top [limit] - Топ треков (по умолчанию 10)\n"
            "/new [limit] - Новые релизы\n"
            "/genre [жанр] - Жанры: pop, rock, hiphop, rap, electronic, metal, jazz\n"
            "/me - Информация о вашем аккаунте\n\n"
            "**Inline режим:**\n"
            "Напишите @byicmbot [запрос] в любом чате для быстрого поиска",
            parse_mode='Markdown'
        )

    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /search"""
        if not context.args:
            await update.message.reply_text(
                "❌ Использование: /search [название трека или артиста]\n\n"
                "Пример: /search Queen Bohemian Rhapsody"
            )
            return

        query = ' '.join(context.args)
        await update.message.reply_text(f"🔍 Поиск: {query}...")

        # Поиск треков
        tracks = await music_service.search(query, limit=10)

        if not tracks:
            await update.message.reply_text("😔 Ничего не найдено")
            return

        # Формирование результатов
        for i, track in enumerate(tracks[:5], 1):
            # Проверка на цензуру
            is_censored = await music_service.check_censorship(track)
            original = None
            if is_censored:
                original = await music_service.get_original_version(track)
                track = original if original else track

            keyboard = [
                [InlineKeyboardButton("▶️ Слушать", web_app=WebAppInfo(url=self.webapp_url))]
            ]

            await update.message.reply_text(
                f"{i}. 🎵 **{track.artist}** - {track.title}\n"
                f"⏱ Длительность: {track.duration // 60}:{track.duration % 60:02d}\n"
                f"📀 Источник: {track.source}\n"
                + ("⚠️ Найдена оригинальная версия!" if original else ""),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )

    async def top_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /top"""
        limit = int(context.args[0]) if context.args and context.args[0].isdigit() else 10

        # TODO: Реализовать endpoint /api/top
        await update.message.reply_text(
            f"🔥 Топ {limit} треков\n\n"
            "Функция в разработке...\n"
            "Откройте плеер для просмотра популярных треков:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎵 Открыть плеер", web_app=WebAppInfo(url=self.webapp_url))]
            ])
        )

    async def new_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /new"""
        limit = int(context.args[0]) if context.args and context.args[0].isdigit() else 10

        # TODO: Реализовать endpoint /api/new
        await update.message.reply_text(
            f"🆕 Новинки ({limit})\n\n"
            "Функция в разработке...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎵 Открыть плеер", web_app=WebAppInfo(url=self.webapp_url))]
            ])
        )

    async def genre_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /genre"""
        if not context.args:
            await update.message.reply_text(
                "📚 **Доступные жанры:**\n\n"
                "• pop - Поп музыка\n"
                "• rock - Рок\n"
                "• hiphop - Хип-хоп\n"
                "• rap - Рэп\n"
                "• electronic - Электронная\n"
                "• metal - Метал\n"
                "• jazz - Джаз\n"
                "• classical - Классическая\n"
                "• rnb - R&B\n"
                "• indie - Инди\n\n"
                "Использование: /genre [жанр]\n"
                "Пример: /genre rock",
                parse_mode='Markdown'
            )
            return

        genre = context.args[0].lower()
        
        # TODO: Реализовать endpoint /api/genres/{genre}
        await update.message.reply_text(
            f"🎵 Жанр: **{genre}**\n\n"
            "Функция в разработке...",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎵 Открыть плеер", web_app=WebAppInfo(url=self.webapp_url))]
            ])
        )

    async def inline_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inline поиск для Telegram"""
        query = update.inline_query.query

        if not query:
            # Пустой запрос - показать подсказку
            results = [
                InlineQueryResultArticle(
                    id="help",
                    title="🎵 Telegram Music",
                    description="Введите название трека или артиста для поиска",
                    input_message_content=InputTextMessageContent(
                        message_text="🎵 Поиск музыки через Telegram Music Bot"
                    ),
                    thumbnail_url="https://picsum.photos/seed/music/100/100"
                )
            ]
            await update.inline_query.answer(results, cache_time=300)
            return

        # Поиск треков
        tracks = await music_service.search(query, limit=20)

        if not tracks:
            results = [
                InlineQueryResultArticle(
                    id="no_results",
                    title="😔 Ничего не найдено",
                    description=f"По запросу: {query}",
                    input_message_content=InputTextMessageContent(
                        message_text=f"😔 Ничего не найдено по запросу: {query}"
                    )
                )
            ]
            await update.inline_query.answer(results, cache_time=60)
            return

        # Формирование результатов inline
        results = []
        for track in tracks[:10]:
            # Проверка на цензуру и замена на оригинал
            is_censored = await music_service.check_censorship(track)
            display_title = track.title
            if is_censored:
                display_title = f"{track.title} ⚠️"

            results.append(
                InlineQueryResultArticle(
                    id=f"track_{track.id or hash(track.title)}",
                    title=f"{track.artist} - {display_title}",
                    description=f"⏱ {track.duration // 60}:{track.duration % 60:02d}",
                    input_message_content=InputTextMessageContent(
                        message_text=f"🎵 {track.artist} - {track.title}\n\n"
                                    f"⏱ Длительность: {track.duration // 60}:{track.duration % 60:02d}\n"
                                    f"📀 Источник: {track.source}\n"
                                    f"🔗 Слушать: {self.webapp_url}"
                    ),
                    thumbnail_url=track.cover or "https://picsum.photos/seed/track/100/100"
                )
            )

        await update.inline_query.answer(results, cache_time=60, is_personal=True)

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback queries от кнопок"""
        query = update.callback_query
        await query.answer()

        if query.data == "top":
            await self.top_command(update, context)
        elif query.data == "new":
            await self.new_command(update, context)
        elif query.data == "genres":
            await self.genre_command(update, context)

    def create_application(self) -> Application:
        """Создание и настройка приложения"""
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN не настроен!")
            return None

        app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        # Обработчики команд
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("search", self.search_command))
        app.add_handler(CommandHandler("top", self.top_command))
        app.add_handler(CommandHandler("new", self.new_command))
        app.add_handler(CommandHandler("genre", self.genre_command))

        # Inline режим
        app.add_handler(InlineQueryHandler(self.inline_search))

        # Callback queries
        app.add_handler(MessageHandler(filters.StatusUpdate.ALL, self.callback_handler))

        return app

    async def run(self):
        """Запуск бота"""
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("Невозможно запустить бота: не настроен TELEGRAM_BOT_TOKEN")
            return

        self.app = self.create_application()
        
        logger.info("Бот запущен...")
        await self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# Глобальный экземпляр
music_bot = MusicBot()


async def start_bot():
    """Функция для запуска бота из main.py"""
    if settings.TELEGRAM_BOT_TOKEN:
        await music_bot.run()
