#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced logging system with colored console output and file rotation
"""

import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from colorama import Fore, Back, Style, init
from typing import Optional

# Initialize colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.BLUE,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE,
    }

    ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '✗ ',
        'CRITICAL': '💀',
        'SUCCESS': '✓ ',
        'MESSAGE': '💬',
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        icon = self.ICONS.get(record.levelname, '  ')

        record.levelname = f"{log_color}{icon} {record.levelname}{Style.RESET_ALL}"
        record.msg = f"{log_color}{record.msg}{Style.RESET_ALL}"

        return super().format(record)


class CustomLogger:
    """Custom logger with console and file output"""

    def __init__(self, name: str = "GirlfriendBot", log_dir: str = "logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

        # File handler with rotation
        log_file = os.path.join(log_dir, f'bot_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

    def success(self, message: str):
        """Log success message (custom level)"""
        icon = '✓ '
        color = Fore.GREEN
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{color}{timestamp} {icon} SUCCESS {message}{Style.RESET_ALL}")
        self.logger.info(f"[SUCCESS] {message}")

    def message(self, message: str):
        """Log user message (custom level)"""
        icon = '💬'
        color = Fore.MAGENTA
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{color}{timestamp} {icon} {message}{Style.RESET_ALL}")
        self.logger.info(f"[MESSAGE] {message}")


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
║    {Fore.YELLOW}👤 Virtual Girlfriend Userbot v1.1 by Gemini AI{Fore.MAGENTA}      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(logo)


# Global logger instance
logger: Optional[CustomLogger] = None


def get_logger() -> CustomLogger:
    """Get or create global logger instance"""
    global logger
    if logger is None:
        logger = CustomLogger()
    return logger
