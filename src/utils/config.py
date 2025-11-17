#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management system
"""

import os
import sys
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    def __init__(self):
        # Telegram configuration
        self.TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
        self.TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
        self.PHONE_NUMBER = os.getenv('PHONE_NUMBER')

        # Gemini AI configuration
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

        # Bot configuration
        self.SESSION_NAME = os.getenv('SESSION_NAME', 'girlfriend_userbot')
        self.DEFAULT_PERSONALITY = os.getenv('DEFAULT_PERSONALITY', 'default')

        # Directories
        self.DATA_DIR = Path('data')
        self.HISTORY_DIR = self.DATA_DIR / 'history'
        self.SESSIONS_DIR = self.DATA_DIR / 'sessions'
        self.LOGS_DIR = Path('logs')
        self.CONFIG_DIR = Path('config')

        # Create directories if they don't exist
        for directory in [self.HISTORY_DIR, self.SESSIONS_DIR, self.LOGS_DIR, self.CONFIG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

        # Features configuration
        self.ENABLE_AUTO_REACTIONS = os.getenv('ENABLE_AUTO_REACTIONS', 'true').lower() == 'true'
        self.ENABLE_HISTORY_SAVE = os.getenv('ENABLE_HISTORY_SAVE', 'true').lower() == 'true'
        self.ENABLE_STATISTICS = os.getenv('ENABLE_STATISTICS', 'true').lower() == 'true'

        # AI configuration
        self.MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', '20'))
        self.TYPING_DELAY = float(os.getenv('TYPING_DELAY', '0.5'))

        # Personalities
        self.personalities: Dict[str, Any] = self._load_personalities()

        # Ignored users
        self.ignored_users: set = set()

        # Offline mode (v1.1.1 feature)
        self.offline_mode: bool = False

    def _load_personalities(self) -> Dict[str, Any]:
        """Load personality configurations from JSON file"""
        personalities_file = self.CONFIG_DIR / 'personalities.json'
        try:
            if personalities_file.exists():
                with open(personalities_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading personalities: {e}")

        # Default personality if file not found
        return {
            "default": {
                "name": "Подруга",
                "description": "Дефолтная личность",
                "prompt": "Ты виртуальная девушка-подруга. Общайся неформально и естественно.",
                "temperature": 0.9,
                "max_tokens": 200
            }
        }

    def get_personality(self, personality_name: Optional[str] = None) -> Dict[str, Any]:
        """Get personality configuration"""
        name = personality_name or self.DEFAULT_PERSONALITY
        return self.personalities.get(name, self.personalities['default'])

    def validate(self) -> tuple[bool, list[str]]:
        """Validate required configuration"""
        missing = []

        if not self.TELEGRAM_API_ID:
            missing.append('TELEGRAM_API_ID')
        if not self.TELEGRAM_API_HASH:
            missing.append('TELEGRAM_API_HASH')
        if not self.GEMINI_API_KEY:
            missing.append('GEMINI_API_KEY')

        return len(missing) == 0, missing

    def add_ignored_user(self, user_id: int):
        """Add user to ignore list"""
        self.ignored_users.add(user_id)
        self._save_ignored_users()

    def remove_ignored_user(self, user_id: int):
        """Remove user from ignore list"""
        self.ignored_users.discard(user_id)
        self._save_ignored_users()

    def is_user_ignored(self, user_id: int) -> bool:
        """Check if user is ignored"""
        return user_id in self.ignored_users

    def _save_ignored_users(self):
        """Save ignored users to file"""
        ignored_file = self.DATA_DIR / 'ignored_users.json'
        try:
            with open(ignored_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.ignored_users), f)
        except Exception as e:
            print(f"Error saving ignored users: {e}")

    def _load_ignored_users(self):
        """Load ignored users from file"""
        ignored_file = self.DATA_DIR / 'ignored_users.json'
        try:
            if ignored_file.exists():
                with open(ignored_file, 'r', encoding='utf-8') as f:
                    self.ignored_users = set(json.load(f))
        except Exception as e:
            print(f"Error loading ignored users: {e}")

    def set_offline_mode(self, enabled: bool):
        """Enable or disable offline mode (v1.1.1 feature)"""
        self.offline_mode = enabled

    def is_offline_mode(self) -> bool:
        """Check if bot is in offline mode (v1.1.1 feature)"""
        return self.offline_mode


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = Config()
        _config._load_ignored_users()
    return _config
