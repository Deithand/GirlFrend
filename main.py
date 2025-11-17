#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Girlfriend Userbot v1.1
AI-powered virtual girlfriend using Gemini AI and Telethon

Main entry point for the application
"""

import asyncio
import sys
from src.core.bot import GirlfriendBot
from src.utils.logger import get_logger


async def main():
    """Main function"""
    logger = get_logger()

    try:
        # Create and start bot
        bot = GirlfriendBot()
        await bot.start()

    except KeyboardInterrupt:
        logger.warning("\n\nБот остановлен пользователем")
        sys.exit(0)

    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
