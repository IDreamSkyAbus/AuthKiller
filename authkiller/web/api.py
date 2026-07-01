"""
Web API 路由
提供测试任务管理、进度查询、结果获取等接口
"""

import os
import json
import asyncio
import threading
from datetime import datetime
from typing import Dict, Any
from flask import Blueprint, request, jsonify, current_app

from authkiller.core.engine import AttackEngine
from authkiller.core.config import ConfigManager
from authkiller.utils.logger import Logger

api_bp = Blueprint('api', __name__)


def convert_web_config_to_backend(web_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    将前端Web配置转换为后端引擎配置格式

    Args:
        web_config: 前端配置（扁平格式）

    Returns:
        后端配置（嵌套格式）
    """
    backend_config = {
        'target': {
            'url': web_config.get('target_url', ''),
            'method': 'POST',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            'body_template': f"{web_config.get('username_field', 'username')}={{user}}&{web_config.get('password_field', 'password')}={{pass}}",
            'content_type': 'urlencoded',
            'cookies': {}
        },
        'payload': {
            'users_file': web_config.get('users_file', ''),
            'passwords_file': web_config.get('passwords_file', ''),
            'rules': [],
            'mode': 'normal'
        },
        'performance': {
            'concurrency': web_config.get('concurrency', 10),
            'timeout': web_config.get('timeout', 30),
            'retry_times': 3,
            'checkpoint_interval': 100
        },
        'detection': {
            'success_status_codes': [200, 302],
            'success_pattern': web_config.get('success_pattern', None),
            'failure_pattern': web_config.get('failure_pattern', None),
            'protocol': web_config.get('protocol_type', 'http_form')
        },
        'defense': {
            'detect_rate_limit': True,
            'auto_throttle': True,
            'throttle_delay': 5,
            'max_rate_limit_retries': 3
        },
        'output': {
            'log_level': 'INFO',
            'log_file': None,
            'result_file': 'results.json',
            'checkpoint_dir': 'checkpoints'
        }
    }

    return backend_config

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
engine_instance: AttackEngine = None
engine_lock = threading.Lock()


@api_bp.route('/config/load', methods=['POST'])
def load_config():
    """加载配置文件"""
    try:
        data = request.get_json()
        config_path = data.get('config_path')

        if not config_path:
            return jsonify({'success': False, 'error': '配置文件路径不能为空'}), 400

        if not os.path.exists(config_path):
            return jsonify({'success': False, 'error': '配置文件不存在'}), 404

        config_mgr = ConfigManager(config_path)
        config = config_mgr.get_config()

        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/config/save', methods=['POST'])
def save_config():
    """保存配置文件"""
    try:
        data = request.get_json()
        config_path = data.get('config_path')
        config = data.get('config')

        if not config_path or not config:
            return jsonify({'success': False, 'error': '配置路径和配置内容不能为空'}), 400

        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/task/start', methods=['POST'])
def start_task():
    """启动测试任务"""
    global engine_instance, task_status

    try:
        with engine_lock:
            if task_status['running']:
                return jsonify({'success': False, 'error': '任务已在运行中'}), 400

        data = request.get_json()
        web_config = data.get('config')

        if not web_config:
            return jsonify({'success': False, 'error': '配置不能为空'}), 400

        # 转换配置格式
        config = convert_web_config_to_backend(web_config)

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

        # 在后台线程中启动测试
        def run_attack():
            global engine_instance, task_status
            try:
                # 创建临时配置文件
                temp_config_path = 'temp_web_config.json'
                with open(temp_config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                # 创建配置管理器
                config_manager = ConfigManager(temp_config_path)

                # 创建引擎实例
                engine_instance = AttackEngine(config_manager)

                # 运行测试（这里需要适配异步引擎）
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # 运行引擎（不使用回调，使用进度轮询机制）
                loop.run_until_complete(engine_instance.run())

                # 更新最终状态
                progress = engine_instance.get_progress()
                task_status['progress'] = {
                    'total': progress.get('total', 0),
                    'tested': progress.get('tested', 0),
                    'success': progress.get('success_count', 0),
                    'failed': progress.get('tested', 0) - progress.get('success_count', 0),
                    'percentage': float(progress.get('progress_percentage', '0%').replace('%', ''))
                }

                # 收集结果
                task_status['results'] = engine_instance.success_results.copy()

                task_status['end_time'] = datetime.now().isoformat()

                # 清理临时配置文件
                try:
                    os.remove(temp_config_path)
                except:
                    pass

            except Exception as e:
                task_status['error'] = str(e)
                task_status['end_time'] = datetime.now().isoformat()
            finally:
                task_status['running'] = False
                engine_instance = None
                loop.close()

        # 启动后台线程
        thread = threading.Thread(target=run_attack, daemon=True)
        thread.start()

        return jsonify({'success': True, 'message': '任务已启动'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/task/stop', methods=['POST'])
def stop_task():
    """停止测试任务"""
    global engine_instance, task_status

    try:
        with engine_lock:
            if not task_status['running']:
                return jsonify({'success': False, 'error': '没有运行中的任务'}), 400

            # 停止引擎
            if engine_instance:
                engine_instance.stop()

            task_status['running'] = False
            task_status['end_time'] = datetime.now().isoformat()

        return jsonify({'success': True, 'message': '任务已停止'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/task/pause', methods=['POST'])
def pause_task():
    """暂停测试任务"""
    global task_status

    try:
        if not task_status['running']:
            return jsonify({'success': False, 'error': '没有运行中的任务'}), 400

        task_status['paused'] = True
        if engine_instance:
            engine_instance.pause()

        return jsonify({'success': True, 'message': '任务已暂停'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/task/resume', methods=['POST'])
def resume_task():
    """恢复测试任务"""
    global task_status

    try:
        if not task_status['paused']:
            return jsonify({'success': False, 'error': '任务未暂停'}), 400

        task_status['paused'] = False
        if engine_instance:
            engine_instance.resume()

        return jsonify({'success': True, 'message': '任务已恢复'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/task/progress', methods=['GET'])
def get_progress():
    """获取任务进度"""
    global engine_instance

    # 如果引擎正在运行，实时更新进度
    if engine_instance and task_status['running']:
        try:
            progress = engine_instance.get_progress()
            task_status['progress'] = {
                'total': progress.get('total', 0),
                'tested': progress.get('tested', 0),
                'success': progress.get('success_count', 0),
                'failed': progress.get('tested', 0) - progress.get('success_count', 0),
                'percentage': float(progress.get('progress_percentage', '0%').replace('%', ''))
            }

            # 如果有新结果，添加到结果列表
            if hasattr(engine_instance, 'success_results'):
                # 只添加最新的结果（避免重复）
                current_count = len(task_status['results'])
                new_results = engine_instance.success_results[current_count:]
                for result in new_results:
                    task_status['results'].append({
                        'username': result.get('username', '-'),
                        'password': result.get('password', '-'),
                        'success': True,
                        'response_time': result.get('response_time', 0),
                        'timestamp': result.get('timestamp', datetime.now().isoformat())
                    })
        except Exception as e:
            current_app.logger.error(f"更新进度失败: {e}")

    return jsonify({
        'success': True,
        'status': task_status
    })


@api_bp.route('/task/results', methods=['GET'])
def get_results():
    """获取测试结果"""
    # 支持分页
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    start = (page - 1) * per_page
    end = start + per_page

    results = task_status['results'][start:end]

    return jsonify({
        'success': True,
        'results': results,
        'total': len(task_status['results']),
        'page': page,
        'per_page': per_page
    })


@api_bp.route('/task/results/export', methods=['GET'])
def export_results():
    """导出测试结果"""
    try:
        export_format = request.args.get('format', 'json')

        if export_format == 'json':
            return jsonify({
                'success': True,
                'data': task_status['results']
            })
        elif export_format == 'csv':
            # TODO: 实现 CSV 导出
            return jsonify({'success': False, 'error': 'CSV导出功能待实现'}), 501
        else:
            return jsonify({'success': False, 'error': '不支持的导出格式'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/system/status', methods=['GET'])
def system_status():
    """获取系统状态"""
    return jsonify({
        'success': True,
        'status': {
            'running': task_status['running'],
            'paused': task_status['paused'],
            'has_results': len(task_status['results']) > 0
        }
    })


@api_bp.route('/dictionary/preview', methods=['POST'])
def dictionary_preview():
    """预览字典文件内容"""
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        max_lines = data.get('max_lines', 50)

        if not file_path:
            return jsonify({'success': False, 'error': '文件路径不能为空'}), 400

        # 安全检查：禁止访问系统关键目录
        forbidden_paths = ['/etc/', '/proc/', '/sys/', 'C:\\Windows\\', 'C:\\System32\\']
        for forbidden in forbidden_paths:
            if file_path.lower().startswith(forbidden.lower()):
                return jsonify({'success': False, 'error': '禁止访问该路径'}), 403

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': f'文件不存在: {file_path}'}), 404

        # 读取文件前N行
        lines = []
        line_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lines.append(line)
                        line_count += 1
                        if line_count >= max_lines:
                            break
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lines.append(line)
                        line_count += 1
                        if line_count >= max_lines:
                            break

        content = '\n'.join(lines)
        return jsonify({
            'success': True,
            'content': content,
            'line_count': line_count,
            'file_path': file_path
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/dictionary/upload', methods=['POST'])
def dictionary_upload():
    """上传字典文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400

        # 保存到字典目录
        dict_dir = os.path.join('examples', 'dictionaries', 'uploaded')
        os.makedirs(dict_dir, exist_ok=True)

        file_path = os.path.join(dict_dir, file.filename)
        file.save(file_path)

        # 统计行数
        line_count = 0
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip():
                    line_count += 1

        return jsonify({
            'success': True,
            'file_path': file_path,
            'line_count': line_count,
            'message': f'上传成功，共 {line_count} 行'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/dictionary/list', methods=['GET'])
def dictionary_list():
    """列出可用字典文件"""
    try:
        dict_dir = os.path.join('examples', 'dictionaries')
        files = []

        if os.path.exists(dict_dir):
            for filename in os.listdir(dict_dir):
                file_path = os.path.join(dict_dir, filename)
                if os.path.isfile(file_path):
                    # 统计行数
                    line_count = 0
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                if line.strip():
                                    line_count += 1
                    except Exception:
                        line_count = 0

                    size = os.path.getsize(file_path)
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'line_count': line_count,
                        'size': size
                    })

        return jsonify({
            'success': True,
            'files': files
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/rules/apply', methods=['POST'])
def apply_rules():
    """应用密码变异规则"""
    try:
        data = request.get_json()
        passwords = data.get('passwords', [])
        rules = data.get('rules', [])

        if not isinstance(passwords, list):
            return jsonify({'success': False, 'error': '密码必须是列表'}), 400

        # 导入规则引擎
        from authkiller.payload.rules import PasswordMutator

        mutator = PasswordMutator()
        result = []

        for pwd in passwords[:10]:  # 限制最多处理10个
            if not isinstance(pwd, str):
                continue

            # 使用正确的方法名 mutate_password
            try:
                variations = mutator.mutate_password(pwd, rules, chain=False)
            except Exception as e:
                variations = [pwd]
            result.append({
                'original': pwd,
                'variations': variations[:20] if isinstance(variations, list) else [pwd]  # 每个密码最多20个变体
            })

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/history/list', methods=['GET'])
def history_list():
    """获取历史任务列表"""
    try:
        # 从results目录读取历史结果文件
        results_dir = 'results'
        history = []

        if os.path.exists(results_dir):
            for filename in sorted(os.listdir(results_dir), reverse=True):
                if filename.endswith('.json'):
                    file_path = os.path.join(results_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                history.append({
                                    'file': filename,
                                    'path': file_path,
                                    'count': len(data),
                                    'created_at': datetime.fromtimestamp(
                                        os.path.getmtime(file_path)
                                    ).isoformat()
                                })
                    except Exception:
                        pass

        return jsonify({
            'success': True,
            'history': history[:20]  # 最多20条
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/checkpoint/save', methods=['POST'])
def save_checkpoint():
    """保存检查点"""
    try:
        data = request.get_json()
        checkpoint_dir = 'checkpoints'
        os.makedirs(checkpoint_dir, exist_ok=True)

        checkpoint_file = os.path.join(
            checkpoint_dir,
            f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'checkpoint_file': checkpoint_file
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/checkpoint/list', methods=['GET'])
def list_checkpoints():
    """列出所有检查点"""
    try:
        checkpoint_dir = 'checkpoints'
        checkpoints = []

        if os.path.exists(checkpoint_dir):
            for filename in sorted(os.listdir(checkpoint_dir), reverse=True):
                if filename.endswith('.json'):
                    file_path = os.path.join(checkpoint_dir, filename)
                    size = os.path.getsize(file_path)
                    checkpoints.append({
                        'name': filename,
                        'path': file_path,
                        'size': size,
                        'created_at': datetime.fromtimestamp(
                            os.path.getmtime(file_path)
                        ).isoformat()
                    })

        return jsonify({
            'success': True,
            'checkpoints': checkpoints
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500