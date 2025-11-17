#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Statistics and analytics system
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from collections import defaultdict


class Statistics:
    """Bot statistics tracker"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.stats_file = data_dir / 'statistics.json'

        # Statistics data
        self.total_messages_received = 0
        self.total_messages_sent = 0
        self.user_stats: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
            'messages_received': 0,
            'messages_sent': 0,
            'first_contact': None,
            'last_contact': None,
            'name': 'Unknown'
        })
        self.daily_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'messages_received': 0,
            'messages_sent': 0
        })
        self.personality_usage: Dict[str, int] = defaultdict(int)
        self.command_usage: Dict[str, int] = defaultdict(int)

        # Load existing stats
        self._load_stats()

    def record_message_received(self, user_id: int, user_name: str = "Unknown"):
        """Record incoming message"""
        self.total_messages_received += 1
        today = datetime.now().strftime('%Y-%m-%d')

        # Update user stats
        if self.user_stats[user_id]['first_contact'] is None:
            self.user_stats[user_id]['first_contact'] = datetime.now().isoformat()

        self.user_stats[user_id]['messages_received'] += 1
        self.user_stats[user_id]['last_contact'] = datetime.now().isoformat()
        self.user_stats[user_id]['name'] = user_name

        # Update daily stats
        self.daily_stats[today]['messages_received'] += 1

        self._save_stats()

    def record_message_sent(self, user_id: int):
        """Record outgoing message"""
        self.total_messages_sent += 1
        today = datetime.now().strftime('%Y-%m-%d')

        # Update user stats
        self.user_stats[user_id]['messages_sent'] += 1

        # Update daily stats
        self.daily_stats[today]['messages_sent'] += 1

        self._save_stats()

    def record_personality_used(self, personality: str):
        """Record personality usage"""
        self.personality_usage[personality] += 1
        self._save_stats()

    def record_command_used(self, command: str):
        """Record command usage"""
        self.command_usage[command] += 1
        self._save_stats()

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for specific user"""
        return self.user_stats.get(user_id)

    def get_top_users(self, limit: int = 10) -> list:
        """Get top users by message count"""
        sorted_users = sorted(
            self.user_stats.items(),
            key=lambda x: x[1]['messages_received'],
            reverse=True
        )
        return sorted_users[:limit]

    def get_summary(self) -> Dict[str, Any]:
        """Get statistics summary"""
        return {
            'total_messages_received': self.total_messages_received,
            'total_messages_sent': self.total_messages_sent,
            'total_users': len(self.user_stats),
            'top_personality': max(self.personality_usage.items(), key=lambda x: x[1])[0] if self.personality_usage else 'default',
            'top_users': self.get_top_users(5),
        }

    def get_formatted_stats(self) -> str:
        """Get formatted statistics string"""
        summary = self.get_summary()

        stats_text = "📊 Статистика бота:\n\n"
        stats_text += f"📨 Всего сообщений получено: {summary['total_messages_received']}\n"
        stats_text += f"📤 Всего сообщений отправлено: {summary['total_messages_sent']}\n"
        stats_text += f"👥 Всего пользователей: {summary['total_users']}\n"
        stats_text += f"🎭 Популярная личность: {summary['top_personality']}\n\n"

        if summary['top_users']:
            stats_text += "🏆 Топ пользователей:\n"
            for i, (user_id, data) in enumerate(summary['top_users'], 1):
                name = data.get('name', 'Unknown')
                msg_count = data.get('messages_received', 0)
                stats_text += f"{i}. {name}: {msg_count} сообщений\n"

        return stats_text

    def _save_stats(self):
        """Save statistics to file"""
        try:
            stats_data = {
                'total_messages_received': self.total_messages_received,
                'total_messages_sent': self.total_messages_sent,
                'user_stats': dict(self.user_stats),
                'daily_stats': dict(self.daily_stats),
                'personality_usage': dict(self.personality_usage),
                'command_usage': dict(self.command_usage),
                'last_updated': datetime.now().isoformat()
            }

            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving statistics: {e}")

    def _load_stats(self):
        """Load statistics from file"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.total_messages_received = data.get('total_messages_received', 0)
                self.total_messages_sent = data.get('total_messages_sent', 0)

                # Load user stats
                user_stats_data = data.get('user_stats', {})
                for user_id_str, stats in user_stats_data.items():
                    user_id = int(user_id_str)
                    self.user_stats[user_id] = stats

                # Load daily stats
                daily_stats_data = data.get('daily_stats', {})
                for date, stats in daily_stats_data.items():
                    self.daily_stats[date] = stats

                # Load personality usage
                self.personality_usage = defaultdict(int, data.get('personality_usage', {}))

                # Load command usage
                self.command_usage = defaultdict(int, data.get('command_usage', {}))

        except Exception as e:
            print(f"Error loading statistics: {e}")

    def reset_stats(self):
        """Reset all statistics"""
        self.total_messages_received = 0
        self.total_messages_sent = 0
        self.user_stats.clear()
        self.daily_stats.clear()
        self.personality_usage.clear()
        self.command_usage.clear()
        self._save_stats()
