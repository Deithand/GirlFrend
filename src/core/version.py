#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version information for Telegram Girlfriend Userbot
"""

__version__ = "1.1.1"
__title__ = "Telegram Girlfriend Userbot"
__description__ = "AI-powered virtual girlfriend using Gemini AI and Telethon"
__author__ = "GirlFrend Team"
__license__ = "MIT"

VERSION_INFO = {
    'version': __version__,
    'title': __title__,
    'description': __description__,
    'author': __author__,
    'license': __license__,
    'features': [
        'Userbot mode - messages from your account',
        'Gemini AI powered conversations',
        'Natural girlfriend-style communication',
        'Conversation history persistence',
        'Multiple personality modes',
        'Command system (!help, !stats, !clear, etc.)',
        'Statistics and analytics',
        'Auto reactions',
        'Ignore list',
        'File logging with rotation',
        'Auto read messages (mark as read)',
        'Offline mode - read but don\'t respond',
    ]
}

def get_version() -> str:
    """Get version string"""
    return __version__

def get_version_info() -> dict:
    """Get full version information"""
    return VERSION_INFO
