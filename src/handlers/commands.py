#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command handlers for bot control
"""

from typing import Optional, Dict, Callable, Any
from telethon import events


class CommandHandler:
    """Handle bot commands"""

    def __init__(self, config, ai_client, stats, logger):
        self.config = config
        self.ai_client = ai_client
        self.stats = stats
        self.logger = logger

        # Command registry
        self.commands: Dict[str, Callable] = {
            'help': self.cmd_help,
            'stats': self.cmd_stats,
            'clear': self.cmd_clear,
            'ignore': self.cmd_ignore,
            'unignore': self.cmd_unignore,
            'personality': self.cmd_personality,
            'personalities': self.cmd_list_personalities,
            'version': self.cmd_version,
        }

    async def handle_command(self, event, user_id: int, command: str, args: str) -> Optional[str]:
        """Process command and return response"""
        # Record command usage
        self.stats.record_command_used(command)

        # Get command handler
        handler = self.commands.get(command)

        if handler:
            return await handler(event, user_id, args)
        else:
            return f"хз что за команда '{command}'. напиши !help чтоб посмотреть список"

    async def cmd_help(self, event, user_id: int, args: str) -> str:
        """Show help message"""
        help_text = """📝 Доступные команды:

!help - показать это сообщение
!stats - показать статистику бота
!clear - очистить историю диалога
!personality [имя] - сменить стиль общения
!personalities - показать доступные стили
!ignore - игнорировать сообщения от меня
!unignore - снять игнор
!version - показать версию бота

Примеры:
!personality romantic - переключиться на романтичный стиль
!personality playful - переключиться на игривый стиль
"""
        return help_text

    async def cmd_stats(self, event, user_id: int, args: str) -> str:
        """Show statistics"""
        return self.stats.get_formatted_stats()

    async def cmd_clear(self, event, user_id: int, args: str) -> str:
        """Clear conversation history"""
        self.ai_client.clear_user_history(user_id)
        self.logger.info(f"Cleared history for user {user_id}")
        return "ок, стерла всю нашу переписку из памяти"

    async def cmd_ignore(self, event, user_id: int, args: str) -> str:
        """Add user to ignore list"""
        self.config.add_ignored_user(user_id)
        self.logger.info(f"User {user_id} added to ignore list")
        return "ок, больше не буду тебе отвечать. напиши !unignore когда передумаешь"

    async def cmd_unignore(self, event, user_id: int, args: str) -> str:
        """Remove user from ignore list"""
        self.config.remove_ignored_user(user_id)
        self.logger.info(f"User {user_id} removed from ignore list")
        return "ок, снова буду отвечать"

    async def cmd_personality(self, event, user_id: int, args: str) -> str:
        """Change personality"""
        if not args:
            current = self.ai_client.get_user_personality(user_id)
            personality_info = self.config.get_personality(current)
            return f"Сейчас у меня личность '{personality_info['name']}'. Чтобы сменить, напиши !personality [имя]"

        personality_name = args.strip().lower()

        if personality_name in self.config.personalities:
            self.ai_client.set_user_personality(user_id, personality_name)
            personality_info = self.config.get_personality(personality_name)
            self.logger.info(f"User {user_id} changed personality to {personality_name}")
            return f"ок, переключилась на '{personality_info['name']}' - {personality_info['description']}"
        else:
            available = ', '.join(self.config.personalities.keys())
            return f"не знаю такую личность. доступные: {available}"

    async def cmd_list_personalities(self, event, user_id: int, args: str) -> str:
        """List available personalities"""
        text = "🎭 Доступные стили общения:\n\n"

        for key, personality in self.config.personalities.items():
            text += f"• {key} - {personality['name']}\n"
            text += f"  {personality['description']}\n\n"

        text += "Используй: !personality [имя]"
        return text

    async def cmd_version(self, event, user_id: int, args: str) -> str:
        """Show bot version"""
        from src.core.version import get_version_info

        info = get_version_info()
        text = f"🤖 {info['title']} v{info['version']}\n\n"
        text += f"📝 {info['description']}\n\n"
        text += "✨ Возможности:\n"
        for feature in info['features'][:5]:  # Show first 5 features
            text += f"• {feature}\n"

        return text

    def is_command(self, text: str) -> bool:
        """Check if message is a command"""
        return text.startswith('!')

    def parse_command(self, text: str) -> tuple[Optional[str], str]:
        """Parse command from message"""
        if not self.is_command(text):
            return None, ""

        # Remove ! and split
        parts = text[1:].split(maxsplit=1)
        command = parts[0].lower() if parts else None
        args = parts[1] if len(parts) > 1 else ""

        return command, args
