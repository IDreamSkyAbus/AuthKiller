"""
AuthKiller 工具模块
日志、报告、防御检测、语言管理等
"""

from authkiller.utils.logger import Logger
from authkiller.utils.reporter import Reporter
from authkiller.utils.defense import DefenseDetector
from authkiller.utils.language import (
    LanguageManager,
    get_language_manager,
    initialize_language,
    set_language,
    get_string,
    get_strings,
    get_cli_string,
    get_web_string,
    get_api_string,
    get_gui_string,
    get_log_string
)

__all__ = [
    "Logger",
    "Reporter",
    "DefenseDetector",
    "LanguageManager",
    "get_language_manager",
    "initialize_language",
    "set_language",
    "get_string",
    "get_strings",
    "get_cli_string",
    "get_web_string",
    "get_api_string",
    "get_gui_string",
    "get_log_string"
]