"""
AuthKiller HTTP Basic Auth 协议实现
标准的 HTTP Basic 认证
"""

import base64
from typing import Dict, Any
import aiohttp
from authkiller.protocols.base import BaseProtocol


class HTTPBasicProtocol(BaseProtocol):
    """
    HTTP Basic Auth 协议
    使用标准的 Authorization Header
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 HTTP Basic 协议

        Args:
            config: 配置字典，必须包含：
                - url: 目标 URL
                - method: 请求方法（GET/POST）
                - success_status_codes: 成功状态码列表
        """
        super().__init__(config)
        self.url = config['url']
        self.method = config.get('method', 'GET')
        self.success_status_codes = config.get('success_status_codes', [200])

        # 会话管理
        self.session: aiohttp.ClientSession = None

    async def init_session(self):
        """
        初始化 aiohttp 会话
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
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

        # 构造 Authorization Header
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        auth_header = f"Basic {encoded_credentials}"

        headers = {
            'Authorization': auth_header
        }

        try:
            # 发送请求
            if self.method.upper() == 'GET':
                response = await self.session.get(self.url, headers=headers)
            else:  # POST
                response = await self.session.post(self.url, headers=headers)

            # 解析响应
            response_data = self.parse_response(response)
            return self.is_success(response_data)

        except aiohttp.ClientError as e:
            raise e

    def parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """
        解析响应

        Args:
            response: aiohttp 响应对象

        Returns:
            响应数据字典
        """
        return {
            'status_code': response.status,
            'headers': dict(response.headers),
            'url': str(response.url),
            'response': response
        }

    def is_success(self, response_data: Dict[str, Any]) -> bool:
        """
        判断认证是否成功

        Args:
            response_data: 解析后的响应数据

        Returns:
            bool: True 表示认证成功
        """
        status_code = response_data['status_code']

        # 401 = 认证失败
        if status_code == 401:
            return False

        # 403 = 禁止访问（可能认证成功但权限不足）
        if status_code == 403:
            # 根据需求决定，这里暂时认为认证成功
            return True

        # 成功状态码
        if status_code in self.success_status_codes:
            return True

        return False

    def validate_config(self) -> bool:
        """
        验证配置

        Returns:
            bool: True 表示配置有效
        """
        return super().validate_config()

    def get_name(self) -> str:
        """
        获取协议名称

        Returns:
            str: 协议名称
        """
        return "HTTPBasicAuth"