"""
AuthKiller 语言管理系统
提供多语言支持和语言切换功能
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class LanguageManager:
    """
    语言管理器
    负责加载、管理和切换语言资源
    """

    # 支持的语言列表
    SUPPORTED_LANGUAGES = {
        'zh-CN': '简体中文',
        'en-US': 'English (US)',
        'ja-JP': '日本語',
        # 预留更多语言
        'zh-TW': '繁體中文',
        'ko-KR': '한국어',
        'de-DE': 'Deutsch',
        'fr-FR': 'Français',
        'es-ES': 'Español',
        'ru-RU': 'Русский',
    }

    # 默认语言
    DEFAULT_LANGUAGE = 'zh-CN'

    # 字符串资源目录
    STRINGS_DIR = None

    def __init__(self, language: str = None, strings_dir: str = None):
        """
        初始化语言管理器

        Args:
            language: 语言代码（如 'zh-CN', 'en-US'）
            strings_dir: 字符串资源目录路径
        """
        # 设置字符串资源目录
        if strings_dir:
            self.STRINGS_DIR = strings_dir
        else:
            # 默认资源目录
            project_root = Path(__file__).parent.parent.parent
            self.STRINGS_DIR = project_root / 'resources' / 'strings'

        # 当前语言
        self.current_language = language or self.DEFAULT_LANGUAGE

        # 字符串资源缓存
        self._strings_cache: Dict[str, Dict[str, Any]] = {}

        # 加载当前语言资源
        self.load_language(self.current_language)

    def load_language(self, language: str) -> bool:
        """
        加载指定语言的字符串资源

        Args:
            language: 语言代码

        Returns:
            是否成功加载
        """
        if language not in self.SUPPORTED_LANGUAGES:
            print(f"警告: 不支持的语言 '{language}'，使用默认语言 '{self.DEFAULT_LANGUAGE}'")
            language = self.DEFAULT_LANGUAGE

        # 检查缓存
        if language in self._strings_cache:
            self.current_language = language
            return True

        # 加载资源文件
        resource_file = Path(self.STRINGS_DIR) / f'{language}.json'

        if not resource_file.exists():
            print(f"警告: 语言资源文件不存在 '{resource_file}'")
            # 如果默认语言资源也不存在，使用空字典
            if language == self.DEFAULT_LANGUAGE:
                self._strings_cache[language] = {}
                self.current_language = language
                return False
            # 尝试加载默认语言
            return self.load_language(self.DEFAULT_LANGUAGE)

        try:
            with open(resource_file, 'r', encoding='utf-8') as f:
                self._strings_cache[language] = json.load(f)
            self.current_language = language
            return True
        except Exception as e:
            print(f"错误: 加载语言资源失败 '{resource_file}': {e}")
            self._strings_cache[language] = {}
            return False

    def get_string(self, key: str, module: str = 'common', **kwargs) -> str:
        """
        获取字符串资源

        Args:
            key: 字符串键名
            module: 模块名称（cli, web, api, gui等）
            **kwargs: 格式化参数

        Returns:
            字符串值
        """
        # 获取当前语言的资源
        resources = self._strings_cache.get(self.current_language, {})

        # 尝试从指定模块获取
        module_strings = resources.get(module, {})
        value = module_strings.get(key)

        # 如果模块中没有，尝试从common获取
        if value is None:
            common_strings = resources.get('common', {})
            value = common_strings.get(key)

        # 如果还是没有，返回键名本身
        if value is None:
            return f'[{key}]'

        # 格式化字符串（如果有参数）
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value

        return value

    def get_strings(self, module: str = None) -> Dict[str, Any]:
        """
        获取模块的所有字符串资源

        Args:
            module: 模块名称（可选，默认返回所有）

        Returns:
            字符串资源字典
        """
        resources = self._strings_cache.get(self.current_language, {})

        if module:
            return resources.get(module, {})
        return resources

    def set_language(self, language: str) -> bool:
        """
        切换语言

        Args:
            language: 语言代码

        Returns:
            是否成功切换
        """
        return self.load_language(language)

    def get_current_language(self) -> str:
        """
        获取当前语言

        Returns:
            当前语言代码
        """
        return self.current_language

    def get_supported_languages(self) -> Dict[str, str]:
        """
        获取支持的语言列表

        Returns:
            语言字典 {code: name}
        """
        return self.SUPPORTED_LANGUAGES

    def get_language_name(self, code: str = None) -> str:
        """
        获取语言名称

        Args:
            code: 语言代码（可选，默认当前语言）

        Returns:
            语言名称
        """
        code = code or self.current_language
        return self.SUPPORTED_LANGUAGES.get(code, code)

    def is_language_supported(self, language: str) -> bool:
        """
        检查语言是否支持

        Args:
            language: 语言代码

        Returns:
            是否支持
        """
        return language in self.SUPPORTED_LANGUAGES

    def reload(self) -> bool:
        """
        重新加载当前语言资源

        Returns:
            是否成功
        """
        # 清除缓存
        if self.current_language in self._strings_cache:
            del self._strings_cache[self.current_language]
        # 重新加载
        return self.load_language(self.current_language)


# 全局语言管理器实例（延迟初始化）
_global_manager: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """
    获取全局语言管理器实例

    Returns:
        LanguageManager 实例
    """
    global _global_manager

    if _global_manager is None:
        _global_manager = LanguageManager()

    return _global_manager


def initialize_language(language: str = None, strings_dir: str = None) -> LanguageManager:
    """
    初始化全局语言管理器

    Args:
        language: 语言代码
        strings_dir: 字符串资源目录

    Returns:
        LanguageManager 实例
    """
    global _global_manager

    _global_manager = LanguageManager(language, strings_dir)
    return _global_manager


def set_language(language: str) -> bool:
    """
    设置全局语言

    Args:
        language: 语言代码

    Returns:
        是否成功
    """
    return get_language_manager().set_language(language)


def get_string(key: str, module: str = 'common', **kwargs) -> str:
    """
    获取全局字符串资源

    Args:
        key: 字符串键名
        module: 模块名称
        **kwargs: 格式化参数

    Returns:
        字符串值
    """
    return get_language_manager().get_string(key, module, **kwargs)


def get_strings(module: str = None) -> Dict[str, Any]:
    """
    获取全局模块字符串资源

    Args:
        module: 模块名称（可选）

    Returns:
        字符串资源字典
    """
    return get_language_manager().get_strings(module)


# 模块专用接口函数
def get_cli_string(key: str, **kwargs) -> str:
    """
    获取CLI模块字符串

    Args:
        key: 字符串键名
        **kwargs: 格式化参数

    Returns:
        字符串值
    """
    return get_string(key, 'cli', **kwargs)


def get_web_string(key: str, **kwargs) -> str:
    """
    获取Web GUI模块字符串

    Args:
        key: 字符串键名
        **kwargs: 格式化参数

    Returns:
        字符串值
    """
    return get_string(key, 'web', **kwargs)


def get_api_string(key: str, **kwargs) -> str:
    """
    获取API模块字符串

    Args:
        key: 字符串键名
        **kwargs: 格式化参数

    Returns:
        字符串值
    """
    return get_string(key, 'api', **kwargs)


def get_gui_string(key: str, **kwargs) -> str:
    """
    获取GUI模块字符串（THINKER GUI）

    Args:
        key: 字符串键名
        **kwargs: 格式化参数

    Returns:
        字符串值
    """
    return get_string(key, 'gui', **kwargs)


def get_log_string(key: str, **kwargs) -> str:
    """
    获取日志模块字符串

    Args:
        key: 字符串键名
        **kwargs: 格式化参数

    Returns:
        字符串值
    """
    return get_string(key, 'log', **kwargs)