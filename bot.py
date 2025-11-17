#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Girlfriend Userbot - Compatibility wrapper
This file provides backward compatibility with v1.0

For new installations, use: python main.py
For legacy mode (v1.0), use: python bot_legacy.py
"""

import sys
import os

print("=" * 60)
print("  Telegram Girlfriend Userbot")
print("=" * 60)
print("\nℹ️  Вы запускаете бота через bot.py")
print("✨ Запускаю новую версию v1.1 (main.py)...\n")
print("Совет: используйте 'python main.py' для запуска v1.1")
print("       или 'python bot_legacy.py' для старой версии v1.0\n")
print("=" * 60 + "\n")

# Import and run the new version
from main import main
import asyncio

if __name__ == '__main__':
    asyncio.run(main())
