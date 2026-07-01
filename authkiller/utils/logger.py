"""
AuthKiller 日志系统
多级别、多目标、彩色输出
"""

import logging
import sys
from typing import Optional
from colorama import Fore, Back, Style, init

# 初始化 colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """
    彩色日志格式化器
    """

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE,
    }

    def format(self, record):
        # 获取颜色
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        # 应用颜色
        record.levelname = color + record.levelname + Style.RESET_ALL
        record.msg = color + str(record.msg) + Style.RESET_ALL
        return super().format(record)


class Logger:
    """
    日志管理器
    支持控制台和文件输出
    """

    def __init__(self, name: str = "AuthKiller",
                 level: int = logging.INFO,
                 log_file: Optional[str] = None):
        """
        初始化日志器

        Args:
            name: 日志器名称
            level: 日志级别
            log_file: 日志文件路径（可选）
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 清除现有 Handler
        self.logger.handlers.clear()

        # 控制台 Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(
            '[%(levelname)s] %(asctime)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # 文件 Handler（如果指定）
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                '[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)

    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)

    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)

    def critical(self, message: str):
        """严重错误日志"""
        self.logger.critical(message)

    def success(self, username: str, password: str):
        """成功日志（特殊格式）"""
        message = f"✅ 成功找到凭证！用户名: {username}, 密码: {password}"
        self.logger.info(Fore.GREEN + Back.BLACK + message + Style.RESET_ALL)

    def attempt(self, username: str, password: str, success: bool):
        """尝试日志"""
        if success:
            self.success(username, password)
        else:
            self.debug(f"尝试失败: {username}:{password}")

    def set_level(self, level: int):
        """设置日志级别"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

    @staticmethod
    def get_logger(name: str = 'AuthKiller', level: int = None, log_file: str = None) -> 'Logger':
        """
        获取日志器实例（静态方法）

        Args:
            name: 日志器名称
            level: 日志级别（可选）
            log_file: 日志文件路径（可选）

        Returns:
            Logger 实例
        """
        if level is None:
            level = logging.INFO
        return Logger(name, level, log_file)