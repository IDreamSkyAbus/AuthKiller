"""
Web 工具函数
端口检测、自动选择等
"""

import socket
from typing import Optional


def is_port_available(port: int, host: str = '127.0.0.1') -> bool:
    """
    检查端口是否可用

    Args:
        port: 端口号
        host: 主机地址

    Returns:
        bool: 端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # 连接失败表示端口可用
    except Exception:
        return True


def find_available_port(start_port: int = 37496, max_attempts: int = 100,
                        host: str = '127.0.0.1') -> Optional[int]:
    """
    查找可用端口

    Args:
        start_port: 起始端口号
        max_attempts: 最大尝试次数
        host: 主机地址

    Returns:
        Optional[int]: 可用端口号，如果找不到返回 None
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port, host):
            return port

    # 如果起始端口之后的端口都被占用，尝试之前的端口
    for port in range(start_port - 1, max(1024, start_port - max_attempts), -1):
        if is_port_available(port, host):
            return port

    return None


def get_local_ip() -> str:
    """
    获取本机 IP 地址

    Returns:
        str: 本机 IP 地址
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # 连接外部地址（不会真正发送数据）
            sock.connect(('8.8.8.8', 80))
            return sock.getsockname()[0]
    except Exception:
        return '127.0.0.1'