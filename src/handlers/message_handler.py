#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Message handler for processing incoming messages
"""

import asyncio
import random
from telethon import events
from typing import List


class MessageHandler:
    """Handle incoming messages"""

    def __init__(self, config, ai_client, stats, command_handler, logger):
        self.config = config
        self.ai_client = ai_client
        self.stats = stats
        self.command_handler = command_handler
        self.logger = logger

        # Auto reactions
        self.reactions = ['👍', '❤️', '🔥', '😊', '😂', '🤔', '👌', '✨']

    async def handle_message(self, event, client):
        """Process incoming message"""
        try:
            # Ignore messages from self
            if event.out:
                return

            # Get sender info
            user = await event.get_sender()
            user_name = user.first_name if user.first_name else "Пользователь"
            user_id = user.id
            message_text = event.message.text

            # Mark message as read (automatically)
            try:
                await client.send_read_acknowledge(event.chat_id, event.message)
                self.logger.debug(f"Marked message as read from {user_name}")
            except Exception as e:
                self.logger.debug(f"Could not mark as read: {str(e)}")

            # Check if user is ignored
            if self.config.is_user_ignored(user_id):
                self.logger.info(f"Ignored message from {user_name} (ID: {user_id})")
                return

            # Check if bot is in offline mode
            if self.config.is_offline_mode():
                self.logger.info(f"Offline mode: read message from {user_name} but not responding")
                return

            # Record incoming message
            self.stats.record_message_received(user_id, user_name)
            self.logger.message(f"Сообщение от {user_name} (ID: {user_id}): {message_text}")

            # Check for commands
            if self.command_handler.is_command(message_text):
                command, args = self.command_handler.parse_command(message_text)
                response = await self.command_handler.handle_command(event, user_id, command, args)

                if response:
                    await event.reply(response)
                    self.stats.record_message_sent(user_id)
                    self.logger.success(f"Команда обработана: !{command}")
                return

            # Add auto reaction (if enabled)
            if self.config.ENABLE_AUTO_REACTIONS and random.random() < 0.3:  # 30% chance
                try:
                    reaction = random.choice(self.reactions)
                    # Note: Reactions API might need different implementation depending on Telethon version
                    # await event.message.react(reaction)
                    self.logger.debug(f"Auto reaction: {reaction}")
                except:
                    pass  # Ignore if reactions not supported

            # Show typing status
            async with client.action(event.chat_id, 'typing'):
                # Get personality for user
                personality_name = self.ai_client.get_user_personality(user_id)
                personality_config = self.config.get_personality(personality_name)

                # Record personality usage
                self.stats.record_personality_used(personality_name)

                # Get AI response
                response = await self.ai_client.get_response(
                    user_id,
                    message_text,
                    personality_config
                )

                # Natural typing delay
                await asyncio.sleep(self.config.TYPING_DELAY)

                # Send response
                await event.reply(response)
                self.stats.record_message_sent(user_id)
                self.logger.success(f"Ответ отправлен: {response[:50]}...")

        except Exception as e:
            self.logger.error(f"Ошибка обработки сообщения: {str(e)}")
            try:
                await event.reply("ой бл что то сломалось... напиши еще раз пжлст")
            except:
                pass
