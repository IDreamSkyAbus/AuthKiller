"""
AuthKiller API 服务模块
提供REST API接口，支持任务管理、配置管理、结果查询等功能
"""

from authkiller.api_service.server import APIServer, create_app, run_api_server
from authkiller.api_service.routes import api_bp

__all__ = ['APIServer', 'create_app', 'run_api_server', 'api_bp']