#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI client for generating responses
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


class ConversationHistory:
    """Manage conversation history for users"""

    def __init__(self, data_dir: Path, max_length: int = 20):
        self.data_dir = data_dir
        self.history_dir = data_dir / 'history'
        self.history_dir.mkdir(parents=True, exist_ok=True)

        self.max_length = max_length
        self.conversations: Dict[int, List[Dict[str, Any]]] = {}

    def add_message(self, user_id: int, role: str, content: str):
        """Add message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        self.conversations[user_id].append({
            'role': role,
            'parts': [content]
        })

        # Keep only last N messages
        if len(self.conversations[user_id]) > self.max_length:
            self.conversations[user_id] = self.conversations[user_id][-self.max_length:]

        # Save to file
        self._save_history(user_id)

    def get_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get conversation history for user"""
        if user_id not in self.conversations:
            self._load_history(user_id)
        return self.conversations.get(user_id, [])

    def clear_history(self, user_id: int):
        """Clear conversation history for user"""
        if user_id in self.conversations:
            self.conversations[user_id] = []
            self._save_history(user_id)

    def _save_history(self, user_id: int):
        """Save conversation history to file"""
        try:
            history_file = self.history_dir / f'user_{user_id}.json'
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations.get(user_id, []), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history for user {user_id}: {e}")

    def _load_history(self, user_id: int):
        """Load conversation history from file"""
        try:
            history_file = self.history_dir / f'user_{user_id}.json'
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.conversations[user_id] = json.load(f)
        except Exception as e:
            print(f"Error loading history for user {user_id}: {e}")
            self.conversations[user_id] = []


class GeminiClient:
    """Gemini AI client for generating girlfriend-style responses"""

    def __init__(self, api_key: str, data_dir: Path, max_history_length: int = 20):
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

        # Conversation history
        self.history = ConversationHistory(data_dir, max_history_length)

        # User personalities
        self.user_personalities: Dict[int, str] = {}

    def set_user_personality(self, user_id: int, personality: str):
        """Set personality for specific user"""
        self.user_personalities[user_id] = personality

    def get_user_personality(self, user_id: int) -> str:
        """Get personality for specific user"""
        return self.user_personalities.get(user_id, 'default')

    async def get_response(
        self,
        user_id: int,
        message: str,
        personality_config: Dict[str, Any]
    ) -> str:
        """Get AI response with personality"""
        try:
            # Get conversation history
            history = self.history.get_history(user_id)

            # Add user message to history
            self.history.add_message(user_id, 'user', message)

            # Create full prompt with personality
            system_prompt = personality_config.get('prompt', '')
            full_prompt = f"{system_prompt}\n\nСообщение: {message}\n\nОтветь естественно, как подруга:"

            # Create chat with history
            chat = self.model.start_chat(history=history[:-1] if history else [])

            # Get response
            response = await asyncio.to_thread(
                chat.send_message,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=personality_config.get('temperature', 0.9),
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=personality_config.get('max_tokens', 200),
                ),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )

            ai_response = response.text

            # Add AI response to history
            self.history.add_message(user_id, 'model', ai_response)

            return ai_response

        except Exception as e:
            print(f"Gemini AI error: {e}")
            return "блин чет у меня глюк... попробуй еще раз"

    def clear_user_history(self, user_id: int):
        """Clear conversation history for user"""
        self.history.clear_history(user_id)
