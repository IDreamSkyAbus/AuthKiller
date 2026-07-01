"""
AuthKiller 攻击执行器
负责执行单次认证测试，管理超时和重试机制
"""

import asyncio
from typing import Dict, Any, Tuple, Optional
from authkiller.protocols.base import BaseProtocol
from authkiller.protocols.http_form import HTTPFormProtocol
from authkiller.protocols.http_basic import HTTPBasicProtocol
from authkiller.utils.defense import DefenseDetector
from authkiller.utils.logger import Logger


class Attacker:
    """
    攻击执行器
    根据配置选择合适的协议并执行认证测试
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化攻击执行器

        Args:
            config: 配置字典（从 ConfigManager 获取）
        """
        self.config = config
        self.protocol: Optional[BaseProtocol] = None
        self.defense_detector: Optional[DefenseDetector] = None
        self.logger = Logger.get_logger('attacker')

        # 初始化协议
        self._init_protocol()

        # 初始化防御检测器
        self._init_defense_detector()

    def _init_protocol(self):
        """
        根据配置初始化协议对象
        """
        protocol_type = self.config.get('protocol', 'http_form')
        protocol_config = self._build_protocol_config()

        if protocol_type == 'http_form':
            self.protocol = HTTPFormProtocol(protocol_config)
        elif protocol_type == 'http_basic':
            self.protocol = HTTPBasicProtocol(protocol_config)
        else:
            raise ValueError(f"不支持的协议类型: {protocol_type}")

        # 验证协议配置
        if not self.protocol.validate_config():
            raise ValueError("协议配置无效")

    def _build_protocol_config(self) -> Dict[str, Any]:
        """
        构建协议配置字典

        Returns:
            协议配置字典
        """
        return {
            'url': self.config.get('url', ''),
            'method': self.config.get('method', 'POST'),
            'headers': self.config.get('headers', {}),
            'cookies': self.config.get('cookies', {}),
            'body_template': self.config.get('body_template', ''),
            'content_type': self.config.get('content_type', 'urlencoded'),
            'success_status_codes': self.config.get('success_status_codes', [200, 302]),
            'success_pattern': self.config.get('success_pattern'),
            'failure_pattern': self.config.get('failure_pattern'),
            'timeout': self.config.get('timeout', 10),
            'retry_times': self.config.get('retry_times', 3)
        }

    def _init_defense_detector(self):
        """
        初始化防御检测器
        """
        defense_config = self.config.get('defense', {})
        if defense_config.get('detect_rate_limit', True):
            self.defense_detector = DefenseDetector(defense_config)

    async def test_credential(self, username: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        测试单个凭证组合

        Args:
            username: 用户名
            password: 密码

        Returns:
            Tuple: (是否成功, 结果详情字典)
        """
        result = {
            'username': username,
            'password': password,
            'success': False,
            'status_code': None,
            'response_time': None,
            'error': None,
            'attempt_count': 0
        }

        max_retries = self.config.get('retry_times', 3)
        timeout = self.config.get('timeout', 10)

        for attempt in range(max_retries):
            result['attempt_count'] = attempt + 1

            try:
                # 执行认证测试（带超时）
                start_time = asyncio.get_event_loop().time()

                success = await asyncio.wait_for(
                    self.protocol.test_credential(username, password),
                    timeout=timeout
                )

                end_time = asyncio.get_event_loop().time()
                result['response_time'] = end_time - start_time
                result['success'] = success

                # 如果是 HTTPFormProtocol，需要额外处理响应内容判断
                if isinstance(self.protocol, HTTPFormProtocol):
                    # 这里简化处理，实际应该读取响应内容判断
                    # HTTPFormProtocol 的 is_success 已经包含了状态码判断
                    pass

                # 检测防御机制（如速率限制）
                if self.defense_detector:
                    # 获取最后响应的状态码（需要协议支持）
                    # 这里简化处理，实际应该从协议获取响应数据
                    pass

                # 成功或失败，直接返回
                return result['success'], result

            except asyncio.TimeoutError:
                result['error'] = 'timeout'
                self.logger.warning(f"尝试 {attempt + 1}/{max_retries} 超时: {username}:{password}")

                if attempt < max_retries - 1:
                    # 等待后重试
                    await asyncio.sleep(1)
                    continue
                else:
                    # 最后一次尝试失败
                    return False, result

            except Exception as e:
                result['error'] = str(e)
                self.logger.error(f"尝试 {attempt + 1}/{max_retries} 异常: {username}:{password} - {e}")

                if attempt < max_retries - 1:
                    # 等待后重试
                    await asyncio.sleep(1)
                    continue
                else:
                    # 最后一次尝试失败
                    return False, result

        # 所有尝试都失败
        return False, result

    async def test_with_defense_handling(self, username: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        测试凭证并处理防御机制

        Args:
            username: 用户名
            password: 密码

        Returns:
            Tuple: (是否成功, 结果详情字典)
        """
        max_rate_limit_retries = self.config.get('max_rate_limit_retries', 3)
        throttle_delay = self.config.get('throttle_delay', 5)

        for rate_limit_attempt in range(max_rate_limit_retries):
            success, result = await self.test_credential(username, password)

            # 检测到速率限制
            if result.get('error') == 'rate_limit' or result.get('status_code') == 429:
                if self.defense_detector and self.config.get('auto_throttle', True):
                    self.logger.warning(f"检测到速率限制，等待 {throttle_delay} 秒后重试")
                    await asyncio.sleep(throttle_delay)
                    continue
                else:
                    # 不自动降速，直接返回失败
                    return False, result

            # 其他情况直接返回
            return success, result

        # 达到最大速率限制重试次数
        return False, result

    async def init_session(self):
        """
        初始化协议会话（如果需要）
        """
        if hasattr(self.protocol, 'init_session'):
            await self.protocol.init_session()

    async def close_session(self):
        """
        关闭协议会话（如果需要）
        """
        if hasattr(self.protocol, 'close_session'):
            await self.protocol.close_session()

    def get_protocol_name(self) -> str:
        """
        获取当前使用的协议名称

        Returns:
            协议名称
        """
        return self.protocol.get_name() if self.protocol else 'None'

    def update_config(self, new_config: Dict[str, Any]):
        """
        更新配置并重新初始化协议

        Args:
            new_config: 新配置字典
        """
        self.config = new_config
        self._init_protocol()
        self._init_defense_detector()

    async def test_batch(self, credentials: list) -> list:
        """
        批量测试凭证（用于测试）

        Args:
            credentials: 凭证列表 [(username, password), ...]

        Returns:
            结果列表
        """
        results = []
        for username, password in credentials:
            success, result = await self.test_credential(username, password)
            results.append(result)
        return results

    def __repr__(self) -> str:
        """
        字符串表示

        Returns:
            字符串表示
        """
        return f"Attacker(protocol={self.get_protocol_name()})"