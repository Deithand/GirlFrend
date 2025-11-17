#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main bot class
"""

import sys
from telethon import TelegramClient, events
from pathlib import Path

from src.utils.config import get_config
from src.utils.logger import get_logger, print_logo
from src.ai.gemini_client import GeminiClient
from src.core.stats import Statistics
from src.handlers.commands import CommandHandler
from src.handlers.message_handler import MessageHandler
from src.core.version import get_version, get_version_info


class GirlfriendBot:
    """Main bot class"""

    def __init__(self):
        # Initialize components
        self.config = get_config()
        self.logger = get_logger()

        # Check configuration
        self._check_config()

        # Initialize Telegram client
        self.client = None

        # Initialize AI client
        self.ai_client = GeminiClient(
            api_key=self.config.GEMINI_API_KEY,
            data_dir=self.config.DATA_DIR,
            max_history_length=self.config.MAX_HISTORY_LENGTH
        )

        # Initialize statistics
        self.stats = Statistics(self.config.DATA_DIR)

        # Initialize command handler
        self.command_handler = CommandHandler(
            config=self.config,
            ai_client=self.ai_client,
            stats=self.stats,
            logger=self.logger
        )

        # Initialize message handler
        self.message_handler = MessageHandler(
            config=self.config,
            ai_client=self.ai_client,
            stats=self.stats,
            command_handler=self.command_handler,
            logger=self.logger
        )

    def _check_config(self):
        """Check configuration"""
        self.logger.info("Проверка конфигурации...")

        is_valid, missing = self.config.validate()

        if not is_valid:
            self.logger.error(f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}")
            self.logger.warning("Создайте файл .env и добавьте необходимые переменные")
            sys.exit(1)

        if not self.config.PHONE_NUMBER:
            self.logger.warning("PHONE_NUMBER не указан - будет запрошен при запуске")

        self.logger.success("Конфигурация загружена успешно")

    async def start(self):
        """Start the bot"""
        # Print logo
        print_logo()

        # Show version
        version_info = get_version_info()
        self.logger.info(f"Запуск {version_info['title']} v{get_version()}")

        # Initialize Telegram client
        self.logger.info("Инициализация Telegram клиента (userbot)...")
        self.client = TelegramClient(
            str(self.config.SESSIONS_DIR / self.config.SESSION_NAME),
            self.config.TELEGRAM_API_ID,
            self.config.TELEGRAM_API_HASH
        )

        # Start client
        self.logger.info("Авторизация в Telegram...")
        if self.config.PHONE_NUMBER:
            await self.client.start(phone=self.config.PHONE_NUMBER)
        else:
            await self.client.start()

        self.logger.success("Userbot успешно запущен!")

        # Get bot info
        me = await self.client.get_me()
        username = f"@{me.username}" if me.username else me.phone
        self.logger.success(f"Работаю как: {username} ({me.first_name})")

        # Register event handlers
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_new_message(event):
            """Handle new incoming messages"""
            if event.is_private:
                await self.message_handler.handle_message(event, self.client)

        # Show ready message
        print("\n" + "="*60)
        print("  ✨ Бот готов к работе! Жду сообщений...")
        print("="*60 + "\n")

        self.logger.info("Начинаю прослушивание сообщений...")

        # Run until disconnected
        await self.client.run_until_disconnected()

    async def stop(self):
        """Stop the bot"""
        if self.client:
            self.logger.info("Остановка бота...")
            await self.client.disconnect()
            self.logger.success("Бот остановлен")
