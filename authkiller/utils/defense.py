"""
AuthKiller 防御机制检测
检测速率限制、账户锁定、验证码等防御措施
"""

import re
from typing import Dict, Any, List
import aiohttp


class DefenseDetector:
    """
    防御机制检测器
    检测并应对目标系统的防御措施
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化防御检测器

        Args:
            config: 配置字典（可选）
        """
        self.config = config or {}
        self.rate_limit_detected = False
        self.account_lockout_detected = False
        self.captcha_detected = False
        self.defense_events: List[Dict[str, Any]] = []

    def detect_rate_limit(self, response: aiohttp.ClientResponse) -> bool:
        """
        检测速率限制

        Args:
            response: HTTP 响应对象

        Returns:
            bool: True 表示检测到速率限制
        """
        # 检测 429 状态码
        if response.status == 429:
            self.rate_limit_detected = True
            self._record_defense_event('rate_limit', response.status, 'Too Many Requests')
            return True

        # 检测响应头中的速率限制信息
        headers = dict(response.headers)
        if 'X-RateLimit-Remaining' in headers:
            remaining = headers.get('X-RateLimit-Remaining', '0')
            if remaining == '0':
                self.rate_limit_detected = True
                self._record_defense_event('rate_limit', response.status, 'Rate limit exceeded')
                return True

        return False

    async def detect_account_lockout(self, response: aiohttp.ClientResponse,
                                     response_text: str = None) -> bool:
        """
        检测账户锁定

        Args:
            response: HTTP 响应对象
            response_text: 响应文本（可选）

        Returns:
            bool: True 表示检测到账户锁定
        """
        # 检测常见账户锁定提示
        lockout_patterns = [
            r'账户已被锁定',
            r'account has been locked',
            r'account locked',
            r'too many failed attempts',
            r'暂时禁止登录',
            r'login temporarily disabled',
            r'locked out',
        ]

        if response_text:
            for pattern in lockout_patterns:
                if re.search(pattern, response_text, re.IGNORECASE):
                    self.account_lockout_detected = True
                    self._record_defense_event('account_lockout', response.status,
                                              f'Matched pattern: {pattern}')
                    return True

        # 检测特定状态码
        if response.status == 403:
            # 403 可能表示账户锁定
            self.account_lockout_detected = True
            self._record_defense_event('account_lockout', response.status, 'Forbidden (possible lockout)')
            return True

        return False

    async def detect_captcha(self, response: aiohttp.ClientResponse,
                             response_text: str = None) -> bool:
        """
        检测验证码

        Args:
            response: HTTP 响应对象
            response_text: 响应文本（可选）

        Returns:
            bool: True 表示检测到验证码
        """
        captcha_patterns = [
            r'captcha',
            r'验证码',
            r'recaptcha',
            r'<img[^>]*captcha',
            r'data-captcha',
            r'requires verification',
        ]

        if response_text:
            for pattern in captcha_patterns:
                if re.search(pattern, response_text, re.IGNORECASE):
                    self.captcha_detected = True
                    self._record_defense_event('captcha', response.status,
                                              f'Matched pattern: {pattern}')
                    return True

        return False

    async def detect_all_defenses(self, response: aiohttp.ClientResponse,
                                  response_text: str = None) -> Dict[str, bool]:
        """
        检测所有防御机制

        Args:
            response: HTTP 响应对象
            response_text: 响应文本（可选）

        Returns:
            Dict: 检测结果字典
        """
        return {
            'rate_limit': self.detect_rate_limit(response),
            'account_lockout': await self.detect_account_lockout(response, response_text),
            'captcha': await self.detect_captcha(response, response_text)
        }

    def get_throttle_recommendation(self) -> int:
        """
        获取降速建议（等待秒数）

        Returns:
            int: 建议等待的秒数
        """
        if self.rate_limit_detected:
            return 60  # 速率限制：等待 60 秒
        elif self.account_lockout_detected:
            return 300  # 账户锁定：等待 5 分钟
        elif self.captcha_detected:
            return 0  # 验证码：无法自动处理，返回 0
        else:
            return 0

    def _record_defense_event(self, defense_type: str, status_code: int, message: str):
        """
        记录防御事件

        Args:
            defense_type: 防御类型
            status_code: HTTP 状态码
            message: 事件消息
        """
        from datetime import datetime

        event = {
            'type': defense_type,
            'status_code': status_code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.defense_events.append(event)

    def get_defense_events(self) -> List[Dict[str, Any]]:
        """
        获取所有防御事件

        Returns:
            List: 防御事件列表
        """
        return self.defense_events.copy()

    def clear_defense_events(self):
        """
        清空防御事件列表
        """
        self.defense_events.clear()
        self.rate_limit_detected = False
        self.account_lockout_detected = False
        self.captcha_detected = False

    def should_pause(self) -> bool:
        """
        是否应该暂停测试

        Returns:
            bool: True 表示应该暂停
        """
        # 验证码检测时必须暂停（无法自动处理）
        if self.captcha_detected:
            return True

        return False

    def should_throttle(self) -> bool:
        """
        是否应该降速

        Returns:
            bool: True 表示应该降速
        """
        # 速率限制或账户锁定时应该降速
        return self.rate_limit_detected or self.account_lockout_detected

    def get_defense_summary(self) -> str:
        """
        获取防御检测摘要

        Returns:
            str: 摘要文本
        """
        summary = []

        if self.rate_limit_detected:
            summary.append("✗ 速率限制检测到")

        if self.account_lockout_detected:
            summary.append("✗ 账户锁定检测到")

        if self.captcha_detected:
            summary.append("✗ 验证码检测到")

        if not summary:
            summary.append("✓ 未检测到防御机制")

        return "\n".join(summary)