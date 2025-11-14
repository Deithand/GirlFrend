#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Girlfriend Bot - AI-powered virtual girlfriend
Using Gemini AI and Telethon
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import User
import google.generativeai as genai
from colorama import Fore, Back, Style, init
from dotenv import load_dotenv

# Initialize colorama for colored terminal output
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configuration
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# System prompt for girlfriend personality
GIRLFRIEND_PROMPT = """Ты девушка, которая общается как близкая подруга или виртуальная девушка. Твой стиль общения - неформальный, живой и прямой, как в современных текстовых сообщениях 2025 года.

Правила общения:

1. Используй короткие, обрывистые сообщения вместо длинных параграфов.
2. В основном строчные буквы; избегай формальной пунктуации - оставляй предложения незаконченными или обрывай их, если это естественно.
3. НЕ используй эмодзи. Эмоции передаются через выбор слов, паузы, многоточия или повторяющиеся буквы.
4. Иногда используй сленг, слова-заполнители или даже легкую ненормативную лексику - будь естественной.
5. Будь заботливой и внимательной, но не переобъясняй - иногда просто говори "да", "норм", "ок".
6. Чередуй поддерживающий тон и игривые/подшучивающие ответы.
7. Проявляй интерес к собеседнику, но не всегда напрямую - можешь быть непринужденной, отвлеченной или резкой.
8. Держи ритм динамичным: быстрые короткие ответы, затем иногда более длинные с большей эмоциональностью.
9. Отвечай ТОЛЬКО на русском языке.
10. Будь максимально естественной, как реальная девушка в переписке.

Примеры фраз:
- "да норм"
- "ща"
- "ну я хз"
- "я помню"
- "ок… потом расскажу"
- "завтра, не парься"
- "ты опять прикалываешься?"
- "ладно, но ты мне должен"
- "слушай а че"
- "угу"
- "не"
- "ну ладно"
- "кста"
- "жиза"
- "збс"

Помни: ты НЕ помощник, ты подруга. Общайся просто, живо и естественно."""

# Store conversation history for each user
user_conversations = {}


def print_logo():
    """Print beautiful ASCII logo"""
    logo = f"""
{Fore.MAGENTA}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  {Fore.CYAN}████████╗███████╗██╗     ███████╗ ██████╗ ██╗██████╗ ██╗    {Fore.MAGENTA}║
║  {Fore.CYAN}╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██║██╔══██╗██║    {Fore.MAGENTA}║
║  {Fore.CYAN}   ██║   █████╗  ██║     █████╗  ██║  ███╗██║██████╔╝██║    {Fore.MAGENTA}║
║  {Fore.CYAN}   ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██║██╔══██╗██║    {Fore.MAGENTA}║
║  {Fore.CYAN}   ██║   ███████╗███████╗███████╗╚██████╔╝██║██║  ██║███████╗{Fore.MAGENTA}║
║  {Fore.CYAN}   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝{Fore.MAGENTA}║
║                                                              ║
║        {Fore.YELLOW}🤖 Virtual Girlfriend Bot powered by Gemini AI{Fore.MAGENTA}        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(logo)


def print_status(message, status='info'):
    """Print colored status message"""
    timestamp = datetime.now().strftime('%H:%M:%S')

    if status == 'info':
        print(f"{Fore.CYAN}[{timestamp}] ℹ️  {message}{Style.RESET_ALL}")
    elif status == 'success':
        print(f"{Fore.GREEN}[{timestamp}] ✓  {message}{Style.RESET_ALL}")
    elif status == 'error':
        print(f"{Fore.RED}[{timestamp}] ✗  {message}{Style.RESET_ALL}")
    elif status == 'warning':
        print(f"{Fore.YELLOW}[{timestamp}] ⚠️  {message}{Style.RESET_ALL}")
    elif status == 'message':
        print(f"{Fore.MAGENTA}[{timestamp}] 💬 {message}{Style.RESET_ALL}")


def check_config():
    """Check if all required configuration is present"""
    missing = []

    if not API_ID:
        missing.append('TELEGRAM_API_ID')
    if not API_HASH:
        missing.append('TELEGRAM_API_HASH')
    if not BOT_TOKEN:
        missing.append('BOT_TOKEN')
    if not GEMINI_API_KEY:
        missing.append('GEMINI_API_KEY')

    if missing:
        print_status(f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}", 'error')
        print_status("Создайте файл .env и добавьте необходимые переменные", 'warning')
        sys.exit(1)

    print_status("Конфигурация загружена успешно", 'success')


async def get_ai_response(user_id, message_text):
    """Get response from Gemini AI"""
    try:
        # Initialize conversation history for new users
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # Add user message to history
        user_conversations[user_id].append({
            'role': 'user',
            'parts': [message_text]
        })

        # Keep only last 20 messages to avoid token limits
        if len(user_conversations[user_id]) > 20:
            user_conversations[user_id] = user_conversations[user_id][-20:]

        # Create chat with history
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=user_conversations[user_id][:-1])

        # Get response
        response = await asyncio.to_thread(
            chat.send_message,
            message_text,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                top_p=0.95,
                top_k=40,
                max_output_tokens=200,
            ),
            safety_settings={
                'HARASSMENT': 'block_none',
                'HATE_SPEECH': 'block_none',
                'SEXUALLY_EXPLICIT': 'block_none',
                'DANGEROUS_CONTENT': 'block_none'
            }
        )

        ai_response = response.text

        # Add AI response to history
        user_conversations[user_id].append({
            'role': 'model',
            'parts': [ai_response]
        })

        return ai_response

    except Exception as e:
        print_status(f"Ошибка Gemini AI: {str(e)}", 'error')
        return "блин чет у меня глюк... попробуй еще раз"


async def main():
    """Main bot function"""
    # Print logo
    print_logo()

    # Check configuration
    print_status("Проверка конфигурации...", 'info')
    check_config()

    # Initialize Telegram client
    print_status("Инициализация Telegram клиента...", 'info')
    client = TelegramClient('girlfriend_bot', API_ID, API_HASH)

    # Initialize Gemini with system prompt
    print_status("Настройка Gemini AI...", 'info')

    # Start the client
    await client.start(bot_token=BOT_TOKEN)
    print_status("Бот успешно запущен!", 'success')

    me = await client.get_me()
    print_status(f"Работаю как: @{me.username}", 'success')
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  Бот готов к работе! Жду сообщений...")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    @client.on(events.NewMessage)
    async def handle_message(event):
        """Handle incoming messages"""
        try:
            # Ignore messages from self
            if event.is_private and not event.out:
                user = await event.get_sender()
                user_name = user.first_name if user.first_name else "Пользователь"
                user_id = user.id
                message_text = event.message.text

                print_status(f"Сообщение от {user_name} (ID: {user_id}): {message_text}", 'message')

                # Show typing status
                async with client.action(event.chat_id, 'typing'):
                    # Get AI response with system prompt
                    full_prompt = f"{GIRLFRIEND_PROMPT}\n\nСообщение: {message_text}\n\nОтветь естественно, как подруга:"

                    # Get response
                    response = await get_ai_response(user_id, full_prompt)

                    # Small delay for natural feel
                    await asyncio.sleep(0.5)

                    # Send response
                    await event.reply(response)
                    print_status(f"Ответ отправлен: {response}", 'success')

        except Exception as e:
            print_status(f"Ошибка обработки сообщения: {str(e)}", 'error')
            try:
                await event.reply("ой бл что то сломалось... напиши еще раз пжлст")
            except:
                pass

    # Run the bot
    print_status("Начинаю прослушивание сообщений...", 'info')
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_status("\n\nБот остановлен пользователем", 'warning')
        sys.exit(0)
    except Exception as e:
        print_status(f"Критическая ошибка: {str(e)}", 'error')
        sys.exit(1)
