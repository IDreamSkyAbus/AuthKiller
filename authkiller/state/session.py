"""
AuthKiller 会话管理
管理 Cookie、Token 和会话状态
"""

import re
from typing import Dict, Any, Optional
import aiohttp


class SessionManager:
    """
    会话管理器
    自动处理 Cookie、CSRF Token 等会话元素
    """

    def __init__(self):
        """
        初始化会话管理器
        """
        self.cookies: Dict[str, str] = {}
        self.tokens: Dict[str, str] = {}
        self.session_data: Dict[str, Any] = {}

    def extract_cookies(self, response: aiohttp.ClientResponse) -> Dict[str, str]:
        """
        从响应中提取 Cookie

        Args:
            response: aiohttp 响应对象

        Returns:
            Dict: Cookie 字典
        """
        cookies = {}

        for name, cookie in response.cookies.items():
            cookies[name] = cookie.value

        # 更新本地 Cookie 存储
        self.cookies.update(cookies)

        return cookies

    async def extract_csrf_token(self, response_text: str, patterns: list = None) -> Optional[str]:
        """
        从响应内容中提取 CSRF Token

        Args:
            response_text: 响应文本
            patterns: Token 提取模式列表（正则表达式）

        Returns:
            Optional[str]: Token 值，如果未找到返回 None
        """
        if patterns is None:
            # 默认 CSRF Token 提取模式
            patterns = [
                r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']',
                r'<input[^>]*name=["\']csrf["\'][^>]*value=["\']([^"\']+)["\']',
                r'name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']',
                r'csrf_token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            ]

        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                token = match.group(1)
                # 存储 Token
                self.tokens['csrf'] = token
                return token

        return None

    def get_csrf_token(self) -> Optional[str]:
        """
        获取已提取的 CSRF Token

        Returns:
            Optional[str]: CSRF Token
        """
        return self.tokens.get('csrf')

    def clear_csrf_token(self):
        """
        清空 CSRF Token
        """
        if 'csrf' in self.tokens:
            del self.tokens['csrf']

    def update_cookies(self, cookies: Dict[str, str]):
        """
        更新 Cookie 存储

        Args:
            cookies: Cookie 字典
        """
        self.cookies.update(cookies)

    def get_cookies(self) -> Dict[str, str]:
        """
        获取当前存储的所有 Cookie

        Returns:
            Dict: Cookie 字典
        """
        return self.cookies.copy()

    def clear_cookies(self):
        """
        清空 Cookie 存储
        """
        self.cookies.clear()

    def update_session_data(self, key: str, value: Any):
        """
        更新会话数据

        Args:
            key: 数据键
            value: 数据值
        """
        self.session_data[key] = value

    def get_session_data(self, key: str) -> Optional[Any]:
        """
        获取会话数据

        Args:
            key: 数据键

        Returns:
            Optional[Any]: 数据值
        """
        return self.session_data.get(key)

    def clear_session_data(self):
        """
        清空所有会话数据
        """
        self.cookies.clear()
        self.tokens.clear()
        self.session_data.clear()

    def inject_cookies_to_request(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """
        将存储的 Cookie 注入到请求 Headers

        Args:
            headers: 现有 Headers

        Returns:
            Dict: 包含 Cookie 的 Headers
        """
        if headers is None:
            headers = {}

        if self.cookies:
            cookie_str = '; '.join([f"{name}={value}" for name, value in self.cookies.items()])
            headers['Cookie'] = cookie_str

        return headers

    def inject_token_to_request(self, body_template: str, token_name: str = 'csrf_token') -> str:
        """
        将 Token 注入到请求体模板

        Args:
            body_template: 请求体模板
            token_name: Token 参数名

        Returns:
            str: 包含 Token 的请求体模板
        """
        token = self.get_csrf_token()
        if token:
            # 在模板中添加 Token 参数
            if '{token}' in body_template:
                body_template = body_template.replace('{token}', token)
            else:
                # 在模板末尾添加 Token 参数
                if body_template:
                    body_template += f'&{token_name}={token}'
                else:
                    body_template = f'{token_name}={token}'

        return body_template

    def to_dict(self) -> Dict[str, Any]:
        """
        将会话状态转换为字典（用于保存）

        Returns:
            Dict: 会话状态字典
        """
        return {
            'cookies': self.cookies,
            'tokens': self.tokens,
            'session_data': self.session_data
        }

    def from_dict(self, data: Dict[str, Any]):
        """
        从字典恢复会话状态

        Args:
            data: 会话状态字典
        """
        self.cookies = data.get('cookies', {})
        self.tokens = data.get('tokens', {})
        self.session_data = data.get('session_data', {})


class SessionAwareProtocol:
    """
    会话感知协议基类
    提供会话管理功能给协议层
    """

    def __init__(self, session_manager: SessionManager = None):
        """
        初始化会话感知协议

        Args:
            session_manager: 会话管理器实例
        """
        self.session_manager = session_manager or SessionManager()

    async def maintain_session(self, response: aiohttp.ClientResponse, response_text: str = None):
        """
        维护会话状态

        Args:
            response: HTTP 响应对象
            response_text: 响应文本（可选）
        """
        # 提取 Cookie
        self.session_manager.extract_cookies(response)

        # 提取 CSRF Token
        if response_text:
            await self.session_manager.extract_csrf_token(response_text)

    def get_session_headers(self) -> Dict[str, str]:
        """
        获取包含会话信息的 Headers

        Returns:
            Dict: Headers 字典
        """
        headers = {}
        self.session_manager.inject_cookies_to_request(headers)
        return headers