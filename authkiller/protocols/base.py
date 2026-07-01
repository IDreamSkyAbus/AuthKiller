"""
AuthKiller 协议基类
定义统一的身份验证协议接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio


class BaseProtocol(ABC):
    """
    协议基类
    所有身份验证协议必须继承此类并实现相关方法
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化协议

        Args:
            config: 协议配置字典，包含目标 URL、请求参数等
        """
        self.config = config
        self.timeout = config.get('timeout', 10)
        self.retry_times = config.get('retry_times', 3)

    @abstractmethod
    async def test_credential(self, username: str, password: str) -> bool:
        """
        测试凭证是否有效

        Args:
            username: 用户名
            password: 密码

        Returns:
            bool: True 表示认证成功，False 表示失败
        """
        pass

    @abstractmethod
    def parse_response(self, response: Any) -> Dict[str, Any]:
        """
        解析响应内容

        Args:
            response: HTTP 响应对象

        Returns:
            Dict: 包含状态码、响应体、Headers 等信息的字典
        """
        pass

    @abstractmethod
    def is_success(self, response_data: Dict[str, Any]) -> bool:
        """
        判断认证是否成功

        Args:
            response_data: 解析后的响应数据

        Returns:
            bool: True 表示认证成功
        """
        pass

    async def execute_with_retry(self, username: str, password: str) -> bool:
        """
        执行测试并支持重试机制

        Args:
            username: 用户名
            password: 密码

        Returns:
            bool: 认证结果
        """
        for attempt in range(self.retry_times):
            try:
                result = await asyncio.wait_for(
                    self.test_credential(username, password),
                    timeout=self.timeout
                )
                return result
            except asyncio.TimeoutError:
                if attempt < self.retry_times - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < self.retry_times - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise e

        return False

    def get_name(self) -> str:
        """
        获取协议名称

        Returns:
            str: 协议名称
        """
        return self.__class__.__name__

    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            bool: True 表示配置有效
        """
        required_keys = ['url']
        for key in required_keys:
            if key not in self.config:
                return False
        return True