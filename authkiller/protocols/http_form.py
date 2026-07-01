"""
AuthKiller HTTP 表单登录协议实现
支持自定义请求体格式、Headers、响应判断规则
"""

import re
import json
from typing import Dict, Any, Optional
import aiohttp
from authkiller.protocols.base import BaseProtocol


class HTTPFormProtocol(BaseProtocol):
    """
    HTTP 表单登录协议
    支持 POST/GET 方法，自定义请求体格式（JSON、URL编码、XML）
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 HTTP 表单协议

        Args:
            config: 配置字典，必须包含：
                - url: 目标 URL
                - method: 请求方法（POST/GET）
                - body_template: 请求体模板（使用 {user} 和 {pass} 占位符）
                - headers: 自定义 Headers
                - cookies: 自定义 Cookies
                - content_type: 请求体格式（json、urlencoded、xml）
                - success_status_codes: 成功状态码列表
                - success_pattern: 成功响应正则表达式
                - failure_pattern: 失败响应正则表达式
        """
        super().__init__(config)
        self.url = config['url']
        self.method = config.get('method', 'POST')
        self.body_template = config.get('body_template', 'username={user}&password={pass}')
        self.headers = config.get('headers', {})
        self.cookies = config.get('cookies', {})
        self.content_type = config.get('content_type', 'urlencoded')

        # 成功判定规则
        self.success_status_codes = config.get('success_status_codes', [200, 302])
        self.success_pattern = config.get('success_pattern', None)
        self.failure_pattern = config.get('failure_pattern', None)

        # 会话管理
        self.session: Optional[aiohttp.ClientSession] = None

    async def init_session(self):
        """
        初始化 aiohttp 会话
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                cookies=self.cookies,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close_session(self):
        """
        关闭 aiohttp 会话
        """
        if self.session and not self.session.closed:
            await self.session.close()

    async def test_credential(self, username: str, password: str) -> bool:
        """
        测试凭证

        Args:
            username: 用户名
            password: 密码

        Returns:
            bool: 认证结果
        """
        await self.init_session()

        # 构造请求体
        body = self._construct_body(username, password)

        try:
            # 发送请求
            if self.method.upper() == 'POST':
                response = await self.session.post(
                    self.url,
                    data=body if self.content_type == 'urlencoded' else None,
                    json=body if self.content_type == 'json' else None,
                    headers=self._get_content_headers()
                )
            else:  # GET
                response = await self.session.get(
                    self.url,
                    params=body if self.content_type == 'urlencoded' else None,
                    headers=self._get_content_headers()
                )

            # 解析响应
            response_data = self.parse_response(response)
            return self.is_success(response_data)

        except aiohttp.ClientError as e:
            raise e

    def _construct_body(self, username: str, password: str) -> Any:
        """
        构造请求体

        Args:
            username: 用户名
            password: 密码

        Returns:
            请求体数据（字典或字符串）
        """
        # 替换模板中的占位符
        body_str = self.body_template.replace('{user}', username).replace('{pass}', password)

        if self.content_type == 'json':
            # JSON 格式：解析为字典
            try:
                return json.loads(body_str)
            except json.JSONDecodeError:
                # 如果不是标准 JSON，尝试构造简单字典
                parts = body_str.split('&')
                data = {}
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        data[key] = value
                return data

        elif self.content_type == 'urlencoded':
            # URL 编码格式：解析为字典
            parts = body_str.split('&')
            data = {}
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    data[key] = value
            return data

        elif self.content_type == 'xml':
            # XML 格式：直接返回字符串
            return body_str

        else:
            # 默认 URL 编码
            parts = body_str.split('&')
            data = {}
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    data[key] = value
            return data

    def _get_content_headers(self) -> Dict[str, str]:
        """
        获取 Content-Type 相关的 Headers

        Returns:
            Headers 字典
        """
        headers = {}

        if self.content_type == 'json':
            headers['Content-Type'] = 'application/json'
        elif self.content_type == 'urlencoded':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif self.content_type == 'xml':
            headers['Content-Type'] = 'application/xml'

        return headers

    def parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """
        解析响应

        Args:
            response: aiohttp 响应对象

        Returns:
            响应数据字典
        """
        # 读取响应体（异步需要等待）
        # 注意：这里需要在调用方处理异步读取
        return {
            'status_code': response.status,
            'headers': dict(response.headers),
            'cookies': dict(response.cookies),
            'url': str(response.url),
            'response': response  # 保留原始响应对象供后续使用
        }

    async def get_response_text(self, response: aiohttp.ClientResponse) -> str:
        """
        获取响应文本（异步）

        Args:
            response: aiohttp 响应对象

        Returns:
            响应文本
        """
        try:
            return await response.text()
        except Exception:
            return ''

    def is_success(self, response_data: Dict[str, Any]) -> bool:
        """
        判断认证是否成功

        Args:
            response_data: 解析后的响应数据

        Returns:
            bool: True 表示认证成功
        """
        status_code = response_data['status_code']

        # 1. 状态码判断
        if status_code in self.success_status_codes:
            # 状态码符合，进一步检查响应内容
            if not self.success_pattern and not self.failure_pattern:
                # 如果没有定义响应内容规则，仅依赖状态码
                return True

        # 2. 响应内容判断（需要异步读取响应体，这里先返回状态码结果）
        # 实际使用时需要在调用方处理响应体读取
        # 这里先返回状态码判断结果
        if status_code in self.success_status_codes:
            return True
        elif status_code == 401 or status_code == 403:
            return False

        # 其他状态码需要进一步判断
        return False

    async def is_success_with_content(self, response_data: Dict[str, Any]) -> bool:
        """
        判断认证是否成功（包含响应内容判断）

        Args:
            response_data: 解析后的响应数据

        Returns:
            bool: True 表示认证成功
        """
        response = response_data['response']
        status_code = response_data['status_code']

        # 状态码判断
        if status_code in [401, 403]:
            return False

        # 读取响应体
        try:
            text = await self.get_response_text(response)
        except Exception:
            text = ''

        # 成功模式匹配
        if self.success_pattern:
            if re.search(self.success_pattern, text, re.IGNORECASE):
                return True

        # 失败模式匹配
        if self.failure_pattern:
            if re.search(self.failure_pattern, text, re.IGNORECASE):
                return False

        # 状态码判断
        if status_code in self.success_status_codes:
            return True

        return False

    def validate_config(self) -> bool:
        """
        验证配置

        Returns:
            bool: True 表示配置有效
        """
        if not super().validate_config():
            return False

        if 'method' not in self.config:
            return False

        if self.config['method'].upper() not in ['POST', 'GET']:
            return False

        return True