"""
AuthKiller API 路由
定义所有REST API接口，支持任务管理、配置管理、密码变异等功能
"""

import os
import json
import asyncio
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify

from authkiller.core.engine import AttackEngine
from authkiller.core.config import ConfigManager
from authkiller.payload.rules import PasswordMutator, RuleEngine
from authkiller.utils.logger import Logger
# 语言管理模块（预留接口）
from authkiller.utils.language import (
    get_api_string,
    get_language_manager,
    set_language,
    get_strings
)

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 全局状态管理
task_status: Dict[str, Any] = {
    'running': False,
    'paused': False,
    'progress': {
        'total': 0,
        'tested': 0,
        'success': 0,
        'failed': 0,
        'percentage': 0.0
    },
    'results': [],
    'start_time': None,
    'end_time': None,
    'error': None
}

# 全局引擎实例
engine_instance: Optional[AttackEngine] = None
engine_lock = threading.Lock()

# 语言设置（使用新的语言管理器）
# 旧的language_settings已迁移到 authkiller.utils.language 模块
language_manager = get_language_manager()

# 日志器
logger = Logger.get_logger('api_routes')


# ==================== 任务管理接口 ====================

@api_bp.route('/task/start', methods=['POST'])
def start_task():
    """
    启动测试任务

    Request JSON:
        {
            "config": {
                "target": {"url": "...", "method": "POST", ...},
                "payload": {"users_file": "...", "passwords_file": "...", ...},
                ...
            },
            "checkpoint_file": "可选，用于恢复断点"
        }

    Response JSON:
        {
            "success": true,
            "message": "任务已启动",
            "task_id": "任务ID"
        }
    """
    global engine_instance, task_status

    try:
        with engine_lock:
            if task_status['running']:
                return jsonify({
                    'success': False,
                    'error': '任务已在运行中'
                }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据不能为空'
            }), 400

        config = data.get('config')
        checkpoint_file = data.get('checkpoint_file')

        if not config:
            return jsonify({
                'success': False,
                'error': '配置不能为空'
            }), 400

        # 验证配置
        try:
            config_manager = ConfigManager()
            config_manager.update_from_dict(config)
            is_valid, error_message = config_manager.validate()
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': f'配置验证失败: {error_message}'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'配置处理失败: {str(e)}'
            }), 400

        # 重置状态
        task_status = {
            'running': True,
            'paused': False,
            'progress': {
                'total': 0,
                'tested': 0,
                'success': 0,
                'failed': 0,
                'percentage': 0.0
            },
            'results': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'error': None
        }

        logger.info(f"启动测试任务: {config.get('target', {}).get('url')}")

        # 在后台线程中启动测试
        def run_attack():
            global engine_instance, task_status
            try:
                # 创建引擎实例
                engine_instance = AttackEngine(config_manager)

                # 运行测试
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # 注册进度回调
                def progress_callback(progress_info):
                    task_status['progress'] = progress_info

                # 注册结果回调
                def result_callback(result):
                    task_status['results'].append(result)
                    if result.get('success'):
                        task_status['progress']['success'] += 1
                    else:
                        task_status['progress']['failed'] += 1

                # 运行引擎
                loop.run_until_complete(engine_instance.run(
                    checkpoint_file=checkpoint_file
                ))

                task_status['end_time'] = datetime.now().isoformat()
                logger.info("测试任务完成")

            except Exception as e:
                task_status['error'] = str(e)
                task_status['end_time'] = datetime.now().isoformat()
                logger.error(f"任务执行异常: {e}")
            finally:
                task_status['running'] = False
                engine_instance = None
                loop.close()

        # 启动后台线程
        thread = threading.Thread(target=run_attack, daemon=True)
        thread.start()

        return jsonify({
            'success': True,
            'message': '任务已启动',
            'task_id': datetime.now().strftime('%Y%m%d%H%M%S')
        })

    except Exception as e:
        logger.error(f"启动任务失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/task/stop', methods=['POST'])
def stop_task():
    """
    停止测试任务

    Response JSON:
        {
            "success": true,
            "message": "任务已停止",
            "status": {...}
        }
    """
    global engine_instance, task_status

    try:
        with engine_lock:
            if not task_status['running']:
                return jsonify({
                    'success': False,
                    'error': '没有运行中的任务'
                }), 400

            # 停止引擎
            if engine_instance:
                engine_instance.stop()

            task_status['running'] = False
            task_status['paused'] = False
            task_status['end_time'] = datetime.now().isoformat()

        logger.info("测试任务已停止")

        return jsonify({
            'success': True,
            'message': '任务已停止',
            'status': task_status
        })

    except Exception as e:
        logger.error(f"停止任务失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/task/progress', methods=['GET'])
def get_progress():
    """
    获取任务进度

    Response JSON:
        {
            "success": true,
            "status": {
                "running": false,
                "paused": false,
                "progress": {
                    "total": 100,
                    "tested": 50,
                    "success": 5,
                    "failed": 45,
                    "percentage": 50.0
                },
                "start_time": "...",
                "end_time": "...",
                "error": null
            }
        }
    """
    return jsonify({
        'success': True,
        'status': task_status
    })


@api_bp.route('/task/results', methods=['GET'])
def get_results():
    """
    获取测试结果

    Query Parameters:
        page: 页码（默认1）
        per_page: 每页数量（默认50）
        success_only: 仅显示成功结果（默认false）

    Response JSON:
        {
            "success": true,
            "results": [...],
            "total": 100,
            "page": 1,
            "per_page": 50
        }
    """
    # 支持分页和筛选
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    success_only = request.args.get('success_only', 'false').lower() == 'true'

    # 筛选结果
    if success_only:
        filtered_results = [r for r in task_status['results'] if r.get('success')]
    else:
        filtered_results = task_status['results']

    # 分页
    start = (page - 1) * per_page
    end = start + per_page

    results_page = filtered_results[start:end]

    return jsonify({
        'success': True,
        'results': results_page,
        'total': len(filtered_results),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(filtered_results) // per_page) + 1
    })


# ==================== 配置管理接口 ====================

@api_bp.route('/config/save', methods=['POST'])
def save_config():
    """
    保存配置文件

    Request JSON:
        {
            "config_path": "配置文件路径",
            "config": {
                "target": {...},
                "payload": {...},
                ...
            }
        }

    Response JSON:
        {
            "success": true,
            "message": "配置已保存",
            "path": "配置文件路径"
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据不能为空'
            }), 400

        config_path = data.get('config_path')
        config = data.get('config')

        if not config_path or not config:
            return jsonify({
                'success': False,
                'error': '配置路径和配置内容不能为空'
            }), 400

        # 确保目录存在
        dir_path = os.path.dirname(config_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"配置已保存: {config_path}")

        return jsonify({
            'success': True,
            'message': '配置已保存',
            'path': config_path
        })

    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/config/load', methods=['GET'])
def load_config():
    """
    加载配置文件

    Query Parameters:
        config_path: 配置文件路径（必需）

    Response JSON:
        {
            "success": true,
            "config": {...}
        }
    """
    try:
        config_path = request.args.get('config_path')

        if not config_path:
            return jsonify({
                'success': False,
                'error': '配置文件路径不能为空'
            }), 400

        if not os.path.exists(config_path):
            return jsonify({
                'success': False,
                'error': '配置文件不存在'
            }), 404

        # 加载配置
        config_manager = ConfigManager(config_path)
        config = config_manager.to_dict()

        logger.info(f"配置已加载: {config_path}")

        return jsonify({
            'success': True,
            'config': config,
            'path': config_path
        })

    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/config/mutate', methods=['POST'])
def mutate_password():
    """
    密码变异

    Request JSON:
        {
            "password": "原始密码",
            "rules": ["uppercase", "append_numbers", ...],
            "chain": false  // 是否链式组合
        }

    或批量变异:
        {
            "passwords": ["password1", "password2", ...],
            "rules": ["uppercase", "append_numbers", ...],
            "chain": false
        }

    Response JSON:
        {
            "success": true,
            "mutated_passwords": ["PASSWORD", "password1", ...],
            "total": 10
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据不能为空'
            }), 400

        rules = data.get('rules', [])
        chain = data.get('chain', False)

        # 创建密码变异器
        rule_engine = RuleEngine()
        mutator = PasswordMutator(rule_engine)

        # 单个密码变异
        if 'password' in data:
            password = data['password']
            mutated_passwords = mutator.mutate_password(password, rules, chain)

            logger.info(f"密码变异: {password} -> {len(mutated_passwords)} 个变体")

            return jsonify({
                'success': True,
                'original_password': password,
                'mutated_passwords': mutated_passwords,
                'total': len(mutated_passwords),
                'rules_applied': rules
            })

        # 批量密码变异
        elif 'passwords' in data:
            passwords = data['passwords']
            all_mutated = []

            for password in passwords:
                mutated = mutator.mutate_password(password, rules, chain)
                all_mutated.extend(mutated)

            # 去重
            unique_mutated = list(set(all_mutated))

            logger.info(f"批量密码变异: {len(passwords)} 个密码 -> {len(unique_mutated)} 个变体")

            return jsonify({
                'success': True,
                'original_count': len(passwords),
                'mutated_passwords': unique_mutated,
                'total': len(unique_mutated),
                'rules_applied': rules
            })

        else:
            return jsonify({
                'success': False,
                'error': '请提供 password 或 passwords 参数'
            }), 400

    except Exception as e:
        logger.error(f"密码变异失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/config/rules', methods=['GET'])
def get_available_rules():
    """
    获取可用的密码变异规则

    Response JSON:
        {
            "success": true,
            "rules": ["uppercase", "lowercase", ...],
            "descriptions": {
                "uppercase": "大写转换",
                ...
            }
        }
    """
    try:
        rule_engine = RuleEngine()
        rules = rule_engine.get_available_rules()

        # 规则描述
        descriptions = {
            'uppercase': '大写转换 (password -> PASSWORD)',
            'lowercase': '小写转换 (Password -> password)',
            'capitalize': '首字母大写 (password -> Password)',
            'append_numbers': '添加数字后缀 (password -> password123)',
            'prepend_numbers': '添加数字前缀 (password -> 123password)',
            'append_special': '添加特殊字符后缀 (password -> password!)',
            'leet': 'Leet字符替换 (password -> p4ssw0rd)',
            'reverse': '反转密码 (password -> drowssap)',
            'user_based': '用户名组合',
            'date_based': '日期组合'
        }

        return jsonify({
            'success': True,
            'rules': rules,
            'descriptions': descriptions
        })

    except Exception as e:
        logger.error(f"获取规则失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 系统管理接口 ====================

@api_bp.route('/system/status', methods=['GET'])
def system_status():
    """
    获取系统状态

    Response JSON:
        {
            "success": true,
            "status": {
                "running": false,
                "paused": false,
                "has_results": false,
                "engine_status": "idle"
            }
        }
    """
    engine_status = 'idle'
    if task_status['running']:
        if task_status['paused']:
            engine_status = 'paused'
        else:
            engine_status = 'running'

    return jsonify({
        'success': True,
        'status': {
            'running': task_status['running'],
            'paused': task_status['paused'],
            'has_results': len(task_status['results']) > 0,
            'engine_status': engine_status,
            'success_count': task_status['progress']['success'],
            'failed_count': task_status['progress']['failed'],
            'uptime': _calculate_uptime()
        }
    })


@api_bp.route('/system/language', methods=['GET'])
def get_language():
    """
    获取语言设置（预留接口）

    Response JSON:
        {
            "success": true,
            "language": "zh-CN",
            "available_languages": ["zh-CN", "en-US"]
        }
    """
    return jsonify({
        'success': True,
        'language': language_settings['current_language'],
        'available_languages': language_settings['available_languages']
    })


@api_bp.route('/system/language', methods=['POST'])
def set_language():
    """
    设置语言（预留接口）

    Request JSON:
        {
            "language": "en-US"
        }

    Response JSON:
        {
            "success": true,
            "message": "语言已设置为 en-US"
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据不能为空'
            }), 400

        language = data.get('language')
        if not language:
            return jsonify({
                'success': False,
                'error': '语言参数不能为空'
            }), 400

        if language not in language_settings['available_languages']:
            return jsonify({
                'success': False,
                'error': f'不支持的语言: {language}'
            }), 400

        language_settings['current_language'] = language
        logger.info(f"语言已设置为: {language}")

        return jsonify({
            'success': True,
            'message': f'语言已设置为 {language}',
            'language': language
        })

    except Exception as e:
        logger.error(f"设置语言失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== API文档接口 ====================

@api_bp.route('/docs', methods=['GET'])
def api_docs():
    """
    API文档

    Response JSON:
        {
            "success": true,
            "documentation": {
                "endpoints": [...],
                "examples": {...}
            }
        }
    """
    documentation = {
        'title': 'AuthKiller REST API 文档',
        'version': '1.0.0',
        'description': '密码测试工具 REST API 服务',
        'base_url': '/api',
        'endpoints': [
            {
                'path': '/task/start',
                'method': 'POST',
                'description': '启动测试任务',
                'request_body': {
                    'config': '配置对象（必需）',
                    'checkpoint_file': '断点文件路径（可选）'
                },
                'response': {
                    'success': '布尔值',
                    'message': '消息',
                    'task_id': '任务ID'
                }
            },
            {
                'path': '/task/stop',
                'method': 'POST',
                'description': '停止测试任务',
                'response': {
                    'success': '布尔值',
                    'message': '消息',
                    'status': '任务状态'
                }
            },
            {
                'path': '/task/progress',
                'method': 'GET',
                'description': '获取任务进度',
                'response': {
                    'success': '布尔值',
                    'status': '任务状态对象'
                }
            },
            {
                'path': '/task/results',
                'method': 'GET',
                'description': '获取测试结果',
                'query_params': {
                    'page': '页码（默认1）',
                    'per_page': '每页数量（默认50）',
                    'success_only': '仅显示成功结果（默认false）'
                },
                'response': {
                    'success': '布尔值',
                    'results': '结果列表',
                    'total': '总数',
                    'page': '当前页',
                    'per_page': '每页数量'
                }
            },
            {
                'path': '/config/save',
                'method': 'POST',
                'description': '保存配置文件',
                'request_body': {
                    'config_path': '配置文件路径（必需）',
                    'config': '配置对象（必需）'
                },
                'response': {
                    'success': '布尔值',
                    'message': '消息',
                    'path': '配置文件路径'
                }
            },
            {
                'path': '/config/load',
                'method': 'GET',
                'description': '加载配置文件',
                'query_params': {
                    'config_path': '配置文件路径（必需）'
                },
                'response': {
                    'success': '布尔值',
                    'config': '配置对象',
                    'path': '配置文件路径'
                }
            },
            {
                'path': '/config/mutate',
                'method': 'POST',
                'description': '密码变异',
                'request_body': {
                    'password': '原始密码（单个）',
                    'passwords': '密码列表（批量）',
                    'rules': '规则列表',
                    'chain': '是否链式组合（默认false）'
                },
                'response': {
                    'success': '布尔值',
                    'mutated_passwords': '变异密码列表',
                    'total': '总数'
                }
            },
            {
                'path': '/config/rules',
                'method': 'GET',
                'description': '获取可用的密码变异规则',
                'response': {
                    'success': '布尔值',
                    'rules': '规则列表',
                    'descriptions': '规则描述'
                }
            },
            {
                'path': '/system/status',
                'method': 'GET',
                'description': '获取系统状态',
                'response': {
                    'success': '布尔值',
                    'status': '系统状态对象'
                }
            },
            {
                'path': '/system/language',
                'method': 'GET',
                'description': '获取语言设置（预留接口）',
                'response': {
                    'success': '布尔值',
                    'language': '当前语言',
                    'available_languages': '可用语言列表'
                }
            },
            {
                'path': '/system/language',
                'method': 'POST',
                'description': '设置语言（预留接口）',
                'request_body': {
                    'language': '语言代码（必需）'
                },
                'response': {
                    'success': '布尔值',
                    'message': '消息',
                    'language': '设置的语言'
                }
            }
        ],
        'examples': {
            'start_task': {
                'url': '/api/task/start',
                'method': 'POST',
                'body': {
                    'config': {
                        'target': {
                            'url': 'http://example.com/login',
                            'method': 'POST'
                        },
                        'payload': {
                            'users_file': 'users.txt',
                            'passwords_file': 'passwords.txt'
                        }
                    }
                }
            },
            'mutate_password': {
                'url': '/api/config/mutate',
                'method': 'POST',
                'body': {
                    'password': 'admin',
                    'rules': ['uppercase', 'append_numbers'],
                    'chain': False
                }
            }
        }
    }

    return jsonify({
        'success': True,
        'documentation': documentation
    })


# ==================== 辅助函数 ====================

def _calculate_uptime() -> str:
    """
    计算任务运行时长

    Returns:
        运行时长字符串
    """
    if not task_status['start_time']:
        return '0s'

    try:
        start = datetime.fromisoformat(task_status['start_time'])
        if task_status['end_time']:
            end = datetime.fromisoformat(task_status['end_time'])
        else:
            end = datetime.now()

        duration = (end - start).total_seconds()
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)

        if hours > 0:
            return f'{hours}h {minutes}m {seconds}s'
        elif minutes > 0:
            return f'{minutes}m {seconds}s'
        else:
            return f'{seconds}s'
    except Exception:
        return '0s'