"""
AuthKiller API 服务器
提供REST API服务，支持任务管理、配置管理、结果查询等功能
"""

import os
from typing import Optional
from flask import Flask, jsonify
from flask_cors import CORS

from authkiller.api_service.routes import api_bp
from authkiller.utils.logger import Logger
# 语言管理模块（预留接口）
from authkiller.utils.language import (
    initialize_language,
    get_api_string,
    get_language_manager,
    set_language
)


class APIServer:
    """
    API服务器类
    负责创建和运行Flask应用
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 5000,
                 debug: bool = False, cors_enabled: bool = True):
        """
        初始化API服务器

        Args:
            host: 监听地址
            port: 监听端口
            debug: 是否启用调试模式
            cors_enabled: 是否启用CORS
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.cors_enabled = cors_enabled
        self.app: Optional[Flask] = None
        self.logger = Logger.get_logger('api_server')
        
        # 初始化语言管理器（预留接口）
        initialize_language('zh-CN')

    def create_app(self) -> Flask:
        """
        创建Flask应用

        Returns:
            Flask应用实例
        """
        # 创建Flask应用
        self.app = Flask(__name__)

        # 配置
        self.app.config['SECRET_KEY'] = 'authkiller-api-server-2026'
        self.app.config['JSON_AS_ASCII'] = False  # 支持中文JSON
        self.app.config['JSON_SORT_KEYS'] = False  # 保持字典顺序

        # 启用CORS
        if self.cors_enabled:
            CORS(self.app)

        # 注册API蓝图
        self.app.register_blueprint(api_bp, url_prefix='/api')

        # 全局错误处理
        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'success': False,
                'error': '请求参数错误',
                'message': str(error)
            }), 400

        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'success': False,
                'error': '接口不存在',
                'message': str(error)
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'success': False,
                'error': '服务器内部错误',
                'message': str(error)
            }), 500

        # 根路径 - API文档
        @self.app.route('/')
        def index():
            return jsonify({
                'name': 'AuthKiller API',
                'version': '1.0.0',
                'description': '密码测试工具 REST API 服务',
                'endpoints': {
                    'task': {
                        'start': 'POST /api/task/start - 启动测试任务',
                        'stop': 'POST /api/task/stop - 停止任务',
                        'progress': 'GET /api/task/progress - 获取进度',
                        'results': 'GET /api/task/results - 获取结果'
                    },
                    'config': {
                        'save': 'POST /api/config/save - 保存配置',
                        'load': 'GET /api/config/load - 加载配置',
                        'mutate': 'POST /api/config/mutate - 密码变异'
                    },
                    'system': {
                        'status': 'GET /api/system/status - 系统状态',
                        'language': 'GET /api/system/language - 获取语言设置',
                        'set_language': 'POST /api/system/language - 设置语言'
                    },
                    'docs': 'GET /api/docs - API文档'
                }
            })

        self.logger.info("Flask应用创建成功")
        return self.app

    def run(self):
        """
        启动API服务器
        """
        if not self.app:
            self.create_app()

        self.logger.info(f"API服务器启动: http://{self.host}:{self.port}")
        print("=" * 60)
        print("AuthKiller API 服务已启动")
        print("=" * 60)
        print(f"服务地址: http://{self.host}:{self.port}")
        print(f"API文档: http://{self.host}:{self.port}/api/docs")
        print("=" * 60)
        print("提示:")
        print("  - 所有API接口均在 /api 路径下")
        print("  - 支持 JSON 格式的请求和响应")
        print("  - 按 Ctrl+C 可停止服务")
        print("=" * 60)

        try:
            self.app.run(host=self.host, port=self.port, debug=self.debug, threaded=True)
        except KeyboardInterrupt:
            self.logger.info("API服务器停止")
            print("\n服务已停止")
        except Exception as e:
            self.logger.error(f"API服务器启动失败: {e}")
            print(f"\n启动失败: {e}")


def create_app(host: str = '127.0.0.1', port: int = 5000,
               debug: bool = False, cors_enabled: bool = True) -> Flask:
    """
    创建Flask应用（工厂函数）

    Args:
        host: 监听地址
        port: 监听端口
        debug: 是否启用调试模式
        cors_enabled: 是否启用CORS

    Returns:
        Flask应用实例
    """
    server = APIServer(host=host, port=port, debug=debug, cors_enabled=cors_enabled)
    return server.create_app()


def run_api_server(host: str = '127.0.0.1', port: int = 5000,
                   debug: bool = False, cors_enabled: bool = True):
    """
    运行API服务器

    Args:
        host: 监听地址
        port: 监听端口
        debug: 是否启用调试模式
        cors_enabled: 是否启用CORS
    """
    server = APIServer(host=host, port=port, debug=debug, cors_enabled=cors_enabled)
    server.create_app()
    server.run()


if __name__ == '__main__':
    # 直接运行此文件时的默认配置
    run_api_server(port=5000, debug=True)