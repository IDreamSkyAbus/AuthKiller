"""
AuthKiller 命令行接口
提供 attack、resume、report、web、gui、api、launcher 子命令
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# 添加父目录到路径，确保能导入核心模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from authkiller.core.config import ConfigManager
from authkiller.core.engine import AttackEngine
from authkiller.utils.logger import Logger
from authkiller.utils.reporter import Reporter
# 语言管理模块（预留接口）
from authkiller.utils.language import (
    initialize_language,
    get_cli_string,
    get_language_manager,
    set_language
)

# 尝试导入 tqdm（可选）
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# 语言支持（使用语言管理器）
# 旧的语言配置已迁移到 authkiller.utils.language 模块
# 这里保留向后兼容的接口
def get_text(key: str, **kwargs) -> str:
    """
    获取国际化文本（向后兼容接口）
    
    Args:
        key: 文本键名
        **kwargs: 格式化参数
        
    Returns:
        文本值
    """
    return get_cli_string(key, **kwargs)


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器

    Returns:
        ArgumentParser 对象
    """
    parser = argparse.ArgumentParser(
        prog='authkiller',
        description='AuthKiller - 密码测试工具（仅用于授权安全审计）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  【attack 命令 - 启动密码测试】
  # HTTP 表单登录测试（基础用法）
  authkiller attack --url http://example.com/login --method POST --data "user={user}&pass={pass}" --users users.txt --passwords passwords.txt
  
  # 使用配置文件（推荐）
  authkiller attack --config examples/configs/example.json
  
  # HTTP Basic Auth 测试
  authkiller attack --url http://api.example.com/admin --protocol http_basic --users users.txt --passwords passwords.txt
  
  # 自定义并发和超时
  authkiller attack --url http://example.com/login --users users.txt --passwords passwords.txt --concurrency 50 --timeout 15
  
  # 使用正则表达式识别成功/失败
  authkiller attack --url http://example.com/login --users users.txt --passwords passwords.txt --success-regex "Welcome|成功" --failure-regex "Invalid|错误"

  【resume 命令 - 断点恢复】
  # 从断点文件恢复任务
  authkiller resume --checkpoint checkpoint_20260701_120000.json
  
  # 指定新的输出文件
  authkiller resume --checkpoint checkpoint_20260701_120000.json --output new_results.json

  【report 命令 - 生成报告】
  # 生成 CSV 格式报告
  authkiller report --input results.json --format csv --output report.csv
  
  # 生成 TXT 格式报告（默认）
  authkiller report --input results.json --output report.txt
  
  # 生成 JSON 格式报告
  authkiller report --input results.json --format json --output report.json

  【web 命令 - Web界面】
  # 启动Web界面（默认端口37496）
  authkiller web
  
  # 指定端口和主机
  authkiller web --port 8080 --host 0.0.0.0
  
  # 启用调试模式
  authkiller web --debug

  【gui 命令 - GUI界面】
  # 启动GUI界面（需要安装 tkinter）
  authkiller gui

  【api 命令 - API服务】
  # 启动API服务（默认端口5000）
  authkiller api
  
  # 指定端口
  authkiller api --port 8000

  【launcher 命令 - 统一启动器】
  # 启动统一启动器（交互式选择界面类型）
  authkiller launcher

警告: 本工具仅用于授权安全测试，未经授权使用可能违反法律！
        '''
    )

    # 全局参数
    parser.add_argument('--lang', choices=['zh', 'en'], default='zh', help='语言选择 (zh=中文, en=English)')

    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # attack 子命令
    attack_parser = subparsers.add_parser('attack', help='启动新的密码测试任务', 
                                         description='启动密码测试任务，支持HTTP表单登录、Basic Auth等多种协议')
    attack_parser.add_argument('--config', '-c', help='配置文件路径（JSON/YAML）')
    attack_parser.add_argument('--url', '-u', help='目标 URL（例如: http://example.com/login）')
    attack_parser.add_argument('--method', '-m', default='POST', choices=['POST', 'GET'], help='请求方法（POST/GET，默认: POST）')
    attack_parser.add_argument('--data', '-d', help='请求体模板，使用 {user} 和 {pass} 占位符（例如: "username={user}&password={pass}")')
    attack_parser.add_argument('--users', help='用户名字典文件路径')
    attack_parser.add_argument('--passwords', '-p', help='密码字典文件路径')
    attack_parser.add_argument('--concurrency', '-n', type=int, default=10, help='并发数（默认: 10）')
    attack_parser.add_argument('--timeout', '-t', type=int, default=10, help='超时时间（秒，默认: 10）')
    attack_parser.add_argument('--success-regex', '-s', help='成功响应正则表达式（例如: "Welcome|成功")')
    attack_parser.add_argument('--failure-regex', '-f', help='失败响应正则表达式（例如: "Invalid|错误")')
    attack_parser.add_argument('--protocol', choices=['http_form', 'http_basic'], default='http_form', help='认证协议类型（默认: http_form）')
    attack_parser.add_argument('--content-type', choices=['json', 'urlencoded', 'xml'], default='urlencoded', help='请求体格式（默认: urlencoded）')
    attack_parser.add_argument('--output', '-o', default='results.json', help='结果输出文件（默认: results.json）')
    attack_parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='日志级别（默认: INFO）')
    attack_parser.add_argument('--no-progress', action='store_true', help='禁用进度条')
    attack_parser.add_argument('--max-retries', type=int, default=3, help='最大重试次数（默认: 3）')
    attack_parser.add_argument('--checkpoint-interval', type=int, default=100, help='断点保存间隔（默认: 每100次尝试）')

    # resume 子命令
    resume_parser = subparsers.add_parser('resume', help='从断点恢复任务', 
                                         description='从之前保存的断点文件恢复未完成的测试任务')
    resume_parser.add_argument('--checkpoint', '-c', required=True, help='断点文件路径（例如: checkpoint_20260701_120000.json）')
    resume_parser.add_argument('--output', '-o', default='results.json', help='结果输出文件（默认: results.json）')

    # report 子命令
    report_parser = subparsers.add_parser('report', help='生成测试报告', 
                                         description='将测试结果转换为不同格式的报告文件')
    report_parser.add_argument('--input', '-i', required=True, help='输入结果文件（JSON格式）')
    report_parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='txt', help='报告格式（默认: txt）')
    report_parser.add_argument('--output', '-o', required=True, help='输出报告文件路径')

    # web 子命令
    web_parser = subparsers.add_parser('web', help='启动Web界面', 
                                      description='启动基于Flask的Web图形界面，提供更友好的操作体验')
    web_parser.add_argument('--port', '-p', type=int, default=37496, help='Web服务端口（默认: 37496）')
    web_parser.add_argument('--host', default='127.0.0.1', help='Web服务主机地址（默认: 127.0.0.1）')
    web_parser.add_argument('--debug', action='store_true', help='启用调试模式')
    web_parser.add_argument('--no-auto-port', action='store_true', help='禁用端口自动检测')

    # gui 子命令（THINKER GUI）
    gui_parser = subparsers.add_parser('gui', help='启动GUI界面（THINKER）', 
                                      description='启动基于Tkinter的桌面GUI界面（需要安装tkinter）')
    gui_parser.add_argument('--theme', choices=['light', 'dark'], default='light', help='界面主题（默认: light）')
    gui_parser.add_argument('--no-splash', action='store_true', help='禁用启动画面')

    # api 子命令
    api_parser = subparsers.add_parser('api', help='启动API服务', 
                                      description='启动独立的API服务，供其他工具或脚本调用')
    api_parser.add_argument('--port', '-p', type=int, default=5000, help='API服务端口（默认: 5000）')
    api_parser.add_argument('--host', default='127.0.0.1', help='API服务主机地址（默认: 127.0.0.1）')
    api_parser.add_argument('--debug', action='store_true', help='启用调试模式')

    # launcher 子命令
    launcher_parser = subparsers.add_parser('launcher', help='启动统一启动器', 
                                           description='启动交互式启动器，选择要使用的界面类型（CLI/Web/GUI/API）')
    launcher_parser.add_argument('--default', choices=['cli', 'web', 'gui', 'api'], default='web', help='默认启动模式（默认: web）')

    return parser


def build_config_from_args(args) -> dict:
    """
    从命令行参数构建配置字典

    Args:
        args: argparse 解析的参数对象

    Returns:
        配置字典
    """
    config = {
        'target': {
            'url': args.url,
            'method': args.method,
            'body_template': args.data or 'username={user}&password={pass}',
            'content_type': args.content_type
        },
        'payload': {
            'users_file': args.users,
            'passwords_file': args.passwords
        },
        'performance': {
            'concurrency': args.concurrency,
            'timeout': args.timeout,
            'retry_times': getattr(args, 'max_retries', 3),
            'checkpoint_interval': getattr(args, 'checkpoint_interval', 100)
        },
        'detection': {
            'protocol': args.protocol,
            'success_pattern': args.success_regex,
            'failure_pattern': args.failure_regex,
            'success_status_codes': [200, 302]
        },
        'output': {
            'result_file': args.output,
            'log_level': args.log_level
        }
    }

    return config


def validate_attack_args(args) -> tuple[bool, str]:
    """
    验证 attack 命令参数

    Args:
        args: 命令行参数

    Returns:
        (是否有效, 错误消息)
    """
    if args.config:
        # 使用配置文件时，验证配置文件是否存在
        if not os.path.exists(args.config):
            return False, f"配置文件不存在: {args.config}"
        return True, ""
    
    # 不使用配置文件时，必须提供基本参数
    if not args.url:
        return False, "缺少必要参数: --url"
    
    if not args.users:
        return False, "缺少必要参数: --users"
    
    if not args.passwords:
        return False, "缺少必要参数: --passwords"
    
    # 验证字典文件是否存在
    if not os.path.exists(args.users):
        return False, f"用户名字典文件不存在: {args.users}"
    
    if not os.path.exists(args.passwords):
        return False, f"密码字典文件不存在: {args.passwords}"
    
    # 验证并发数范围
    if args.concurrency < 1 or args.concurrency > 1000:
        return False, "并发数必须在 1-1000 之间"
    
    # 验证超时时间
    if args.timeout < 1 or args.timeout > 300:
        return False, "超时时间必须在 1-300 秒之间"
    
    return True, ""


def validate_resume_args(args) -> tuple[bool, str]:
    """
    验证 resume 命令参数

    Args:
        args: 命令行参数

    Returns:
        (是否有效, 错误消息)
    """
    if not os.path.exists(args.checkpoint):
        return False, f"{get_text('error_checkpoint_not_found')}: {args.checkpoint}"
    
    return True, ""


def validate_report_args(args) -> tuple[bool, str]:
    """
    验证 report 命令参数

    Args:
        args: 命令行参数

    Returns:
        (是否有效, 错误消息)
    """
    if not os.path.exists(args.input):
        return False, f"{get_text('error_result_file_not_found')}: {args.input}"
    
    # 验证输出目录是否存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            return False, f"无法创建输出目录: {output_dir} - {e}"
    
    return True, ""


async def run_attack(args):
    """
    执行 attack 子命令

    Args:
        args: 命令行参数
    """
    logger = Logger.get_logger('cli')

    try:
        # 验证参数
        is_valid, error_message = validate_attack_args(args)
        if not is_valid:
            logger.error(error_message)
            sys.exit(1)

        # 加载配置
        if args.config:
            # 从配置文件加载
            config_manager = ConfigManager(args.config)
            logger.info(f"{get_text('info_config_loaded')}: {args.config}")
        else:
            # 从命令行参数构建配置
            config = build_config_from_args(args)
            config_manager = ConfigManager()
            config_manager.update_from_dict(config)

        # 验证配置
        is_valid, error_message = config_manager.validate()
        if not is_valid:
            logger.error(f"{get_text('error_config_invalid')}: {error_message}")
            sys.exit(1)

        logger.info(get_text('info_config_valid'))

        # 显示任务信息
        logger.info("=" * 60)
        logger.info(f"目标 URL: {config_manager.get('target.url')}")
        logger.info(f"用户名字典: {config_manager.get('payload.users_file')}")
        logger.info(f"密码字典: {config_manager.get('payload.passwords_file')}")
        logger.info(f"并发数: {config_manager.get('performance.concurrency')}")
        logger.info(f"协议类型: {config_manager.get('detection.protocol')}")
        logger.info("=" * 60)

        # 创建引擎
        engine = AttackEngine(config_manager)

        # 运行任务
        logger.info(get_text('info_task_start'))
        stats = await engine.run()

        # 显示结果
        logger.info("=" * 60)
        logger.info(get_text('info_task_complete'))
        logger.info(f"总尝试次数: {stats['total_attempts']}")
        logger.info(f"成功次数: {stats['success_count']}")
        logger.info(f"成功率: {stats['success_rate']}")
        logger.info(f"耗时: {stats['elapsed_time']}")
        logger.info(f"平均尝试时间: {stats['average_time_per_attempt']}")
        logger.info("=" * 60)

        # 显示成功凭证
        if engine.success_results:
            logger.info(get_text('info_valid_credentials'))
            for result in engine.success_results:
                logger.success(f"  {result['username']} : {result['password']}")

        logger.info(f"{get_text('info_results_saved')}: {args.output}")

    except KeyboardInterrupt:
        logger.warning("用户中断任务")
        sys.exit(0)

    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        sys.exit(1)


async def run_resume(args):
    """
    执行 resume 子命令

    Args:
        args: 命令行参数
    """
    logger = Logger.get_logger('cli')

    try:
        # 验证参数
        is_valid, error_message = validate_resume_args(args)
        if not is_valid:
            logger.error(error_message)
            sys.exit(1)

        checkpoint_file = args.checkpoint
        logger.info(f"{get_text('info_checkpoint_loaded')}: {checkpoint_file}")

        # 加载配置（断点文件包含配置）
        from authkiller.state.checkpoint import CheckpointManager
        checkpoint_manager = CheckpointManager()
        checkpoint_data = await checkpoint_manager.load_checkpoint(checkpoint_file)

        # 获取配置
        config = checkpoint_data.get('config')
        if not config:
            logger.error(get_text('error_checkpoint_invalid'))
            sys.exit(1)

        # 创建配置管理器
        config_manager = ConfigManager()
        config_manager.update_from_dict(config)

        # 创建引擎
        engine = AttackEngine(config_manager)

        # 运行任务（从断点恢复）
        stats = await engine.run(checkpoint_file)

        # 显示结果
        logger.info("=" * 60)
        logger.info(get_text('info_task_resumed'))
        logger.info(f"总尝试次数: {stats['total_attempts']}")
        logger.info(f"成功次数: {stats['success_count']}")
        logger.info(f"成功率: {stats['success_rate']}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"恢复任务失败: {e}")
        sys.exit(1)


def run_report(args):
    """
    执行 report 子命令

    Args:
        args: 命令行参数
    """
    logger = Logger.get_logger('cli')

    try:
        # 验证参数
        is_valid, error_message = validate_report_args(args)
        if not is_valid:
            logger.error(error_message)
            sys.exit(1)

        # 加载结果文件
        import json
        input_file = args.input

        with open(input_file, 'r', encoding='utf-8') as f:
            results_data = json.load(f)

        # 创建报告生成器
        reporter = Reporter()

        # 根据格式生成报告
        output_file = args.output
        format_type = args.format

        logger.info(f"生成报告: {output_file} (格式: {format_type})")

        if format_type == 'json':
            reporter.save_json(results_data, output_file)
        elif format_type == 'csv':
            reporter.save_csv(results_data, output_file)
        elif format_type == 'txt':
            reporter.save_txt(results_data, output_file)

        logger.info(f"报告已生成: {output_file}")

    except json.JSONDecodeError as e:
        logger.error(f"JSON文件解析失败: {e}")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        sys.exit(1)


def run_web(args):
    """
    执行 web 子命令

    Args:
        args: 命令行参数
    """
    try:
        # 导入Web模块
        from authkiller.web.app import run_web

        # 启动Web服务
        run_web(
            host=args.host,
            port=args.port,
            debug=args.debug,
            auto_port=not args.no_auto_port
        )

    except ImportError:
        print(f"❌ {get_text('error_web_module_not_installed')}")
        sys.exit(1)

    except Exception as e:
        print(f"❌ 启动Web界面失败: {e}")
        sys.exit(1)


def run_gui(args):
    """
    执行 gui 子命令（THINKER GUI）

    Args:
        args: 命令行参数
    """
    try:
        # 尝试导入tkinter
        import tkinter as tk
        from tkinter import messagebox
        
        # 尝试导入GUI模块
        try:
            from authkiller.gui.app import launch_gui
            launch_gui(theme=args.theme, show_splash=not args.no_splash)
        except ImportError:
            # GUI模块未实现，显示提示信息
            print("\n" + "=" * 60)
            print("AuthKiller GUI（THINKER）")
            print("=" * 60)
            print("\n⚠️  GUI模块尚未实现")
            print("\n当前可用界面：")
            print("  - CLI命令行: authkiller attack --config config.json")
            print("  - Web界面:   authkiller web")
            print("\n后续版本将提供完整的GUI界面支持。")
            print("=" * 60)
            sys.exit(0)
    
    except ImportError:
        print(f"❌ {get_text('error_gui_module_not_installed')}")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ 启动GUI界面失败: {e}")
        sys.exit(1)


def run_api(args):
    """
    执行 api 子命令

    Args:
        args: 命令行参数
    """
    try:
        # 导入Web模块（API和Web共用Flask应用）
        from authkiller.web.app import create_app
        
        # 创建应用
        app = create_app()
        
        # 显示启动信息
        print("=" * 60)
        print("AuthKiller API 服务已启动")
        print("=" * 60)
        print(f"API 地址: http://{args.host}:{args.port}/api")
        print("=" * 60)
        print("API 端点:")
        print("  - POST /api/task/start     - 启动测试任务")
        print("  - POST /api/task/stop      - 停止测试任务")
        print("  - GET  /api/task/progress  - 获取任务进度")
        print("  - GET  /api/task/results   - 获取测试结果")
        print("=" * 60)
        print("提示: 按 Ctrl+C 可停止服务")
        print("=" * 60)
        
        # 启动API服务
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    
    except ImportError:
        print(f"❌ {get_text('error_web_module_not_installed')}")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ 启动API服务失败: {e}")
        sys.exit(1)


def run_launcher(args):
    """
    执行 launcher 子命令（统一启动器）

    Args:
        args: 命令行参数
    """
    try:
        # 尝试导入tkinter用于交互式选择
        try:
            import tkinter as tk
            from tkinter import messagebox, simpledialog
            
            # 创建选择窗口
            root = tk.Tk()
            root.title("AuthKiller Launcher")
            root.geometry("400x300")
            
            # 添加标题
            title_label = tk.Label(root, text="AuthKiller - 密码测试工具", font=("Arial", 16))
            title_label.pack(pady=20)
            
            # 添加警告
            warning_label = tk.Label(root, text="⚠️ 仅用于授权安全测试！", fg="red", font=("Arial", 12))
            warning_label.pack(pady=10)
            
            # 添加选择按钮
            def launch_web():
                root.destroy()
                run_web(argparse.Namespace(host='127.0.0.1', port=37496, debug=False, no_auto_port=False))
            
            def launch_cli():
                root.destroy()
                print("\n请使用以下命令启动CLI任务:")
                print("  authkiller attack --config config.json")
                print("  authkiller attack --url http://example.com/login --users users.txt --passwords passwords.txt")
            
            def launch_gui():
                root.destroy()
                run_gui(argparse.Namespace(theme='light', no_splash=False))
            
            def launch_api():
                root.destroy()
                run_api(argparse.Namespace(host='127.0.0.1', port=5000, debug=False))
            
            # Web按钮（默认推荐）
            web_btn = tk.Button(root, text="启动 Web 界面（推荐）", command=launch_web, width=20, height=2)
            web_btn.pack(pady=10)
            
            # CLI按钮
            cli_btn = tk.Button(root, text="CLI 命令行提示", command=launch_cli, width=20, height=2)
            cli_btn.pack(pady=5)
            
            # GUI按钮
            gui_btn = tk.Button(root, text="启动 GUI 界面", command=launch_gui, width=20, height=2)
            gui_btn.pack(pady=5)
            
            # API按钮
            api_btn = tk.Button(root, text="启动 API 服务", command=launch_api, width=20, height=2)
            api_btn.pack(pady=5)
            
            # 退出按钮
            quit_btn = tk.Button(root, text="退出", command=root.destroy, width=20, height=1)
            quit_btn.pack(pady=10)
            
            root.mainloop()
        
        except ImportError:
            # tkinter未安装，使用命令行交互式选择
            print("\n" + "=" * 60)
            print("AuthKiller Launcher - 统一启动器")
            print("=" * 60)
            print("\n⚠️  tkinter 未安装，使用命令行模式")
            print("\n可用界面类型:")
            print("  1. Web 界面（推荐）")
            print("  2. CLI 命令行")
            print("  3. GUI 界面（需要安装tkinter）")
            print("  4. API 服务")
            print("  0. 退出")
            print("=" * 60)
            
            # 根据默认选项自动选择
            if args.default == 'web':
                print(f"\n默认启动: Web 界面")
                run_web(argparse.Namespace(host='127.0.0.1', port=37496, debug=False, no_auto_port=False))
            elif args.default == 'api':
                print(f"\n默认启动: API 服务")
                run_api(argparse.Namespace(host='127.0.0.1', port=5000, debug=False))
            elif args.default == 'gui':
                print(f"\n默认启动: GUI 界面")
                run_gui(argparse.Namespace(theme='light', no_splash=False))
            else:
                print(f"\n默认启动: CLI 命令行")
                print("请使用以下命令启动CLI任务:")
                print("  authkiller attack --config config.json")
    
    except Exception as e:
        print(f"❌ 启动Launcher失败: {e}")
        sys.exit(1)


def interactive_select_language() -> str:
    """
    交互式选择语言

    Returns:
        选中的语言代码
    """
    print("\n" + "=" * 60)
    print("  Select Language / 选择语言 / 言語選択")
    print("=" * 60)
    print("  1. 中文 (zh-CN) - 默认")
    print("  2. English (en-US)")
    print("  3. 日本語 (ja-JP)")
    print("=" * 60)

    try:
        choice = input("请选择 [1]: ").strip() or "1"

        lang_map = {
            "1": "zh-CN",
            "2": "en-US",
            "3": "ja-JP"
        }

        selected = lang_map.get(choice, "zh-CN")
        return selected
    except (EOFError, KeyboardInterrupt):
        return "zh-CN"


def interactive_select_mode() -> str:
    """
    交互式选择界面模式

    Returns:
        选中的模式
    """
    print("\n" + "=" * 60)
    print("  选择界面模式 / Select Interface Mode")
    print("=" * 60)
    print("  1. Web GUI  - 浏览器界面（推荐）")
    print("  2. THINKER  - 桌面图形界面")
    print("  3. CLI      - 命令行界面")
    print("  4. API      - API服务模式")
    print("=" * 60)

    try:
        choice = input("请选择 [1]: ").strip() or "1"

        mode_map = {
            "1": "web",
            "2": "gui",
            "3": "cli",
            "4": "api"
        }

        return mode_map.get(choice, "web")
    except (EOFError, KeyboardInterrupt):
        return "web"


def show_welcome_banner(lang: str):
    """显示欢迎横幅"""
    banners = {
        "zh-CN": """
============================================================
                                                           
            AuthKiller - 密码测试工具                       
         Password Testing Tool v1.0.0                      
                                                           
  [!] 警告：仅用于授权安全审计和强度测试！                   
  Warning: For authorized security testing only!           
                                                           
============================================================
""",
        "en-US": """
============================================================
                                                           
            AuthKiller - Password Testing Tool              
         Password Testing Tool v1.0.0                      
                                                           
  [!] Warning: For authorized security testing only!        
                                                           
============================================================
""",
        "ja-JP": """
============================================================
                                                           
            AuthKiller - パスワードテストツール              
         Password Testing Tool v1.0.0                      
                                                           
  [!] 警告：認可されたセキュリティテスト専用！             
                                                           
============================================================
"""
    }
    print(banners.get(lang, banners["zh-CN"]))


def run_mode(mode: str, lang: str):
    """
    根据选择的模式启动对应界面

    Args:
        mode: 模式（web/gui/cli/api）
        lang: 语言
    """
    if mode == "web":
        # 启动Web GUI
        from authkiller.web.app import run_web
        try:
            run_web(host="127.0.0.1", port=37496, debug=False, auto_port=True)
        except KeyboardInterrupt:
            print("\n\n[INFO] Web服务已停止")
            return

    elif mode == "gui":
        # 启动THINKER GUI
        try:
            import tkinter as tk
        except ImportError:
            print("\n[ERROR] tkinter 未安装，无法启动GUI界面")
            print("请使用: pip install tk 或使用其他界面模式")
            return

        try:
            from authkiller.gui.run_gui import launch_gui
            launch_gui(lang=lang)
        except ImportError:
            print("\n[ERROR] GUI模块未找到")
        except Exception as e:
            print(f"\n[ERROR] 启动GUI失败: {e}")

    elif mode == "cli":
        # CLI模式 - 显示使用说明
        print("\n" + "=" * 60)
        print("  CLI 命令行模式")
        print("=" * 60)
        print("\n使用示例:")
        print("  1. 使用配置文件:")
        print("     authkiller attack --config config.json")
        print()
        print("  2. 直接命令行参数:")
        print("     authkiller attack \\")
        print("       --url http://example.com/login \\")
        print("       --users users.txt \\")
        print("       --passwords passwords.txt \\")
        print("       --concurrency 10")
        print()
        print("  3. 断点恢复:")
        print("     authkiller resume --checkpoint checkpoint.json")
        print()
        print("  4. 生成报告:")
        print("     authkiller report --input results.json --format csv")
        print("=" * 60)
        print("\n更多参数请使用: authkiller --help")

    elif mode == "api":
        # 启动API服务
        from authkiller.web.app import create_app
        try:
            app = create_app()
            print("\n" + "=" * 60)
            print("  AuthKiller API 服务")
            print(f"  地址: http://127.0.0.1:5000")
            print("=" * 60)
            app.run(host="127.0.0.1", port=5000, debug=False, threaded=True, use_reloader=False)
        except KeyboardInterrupt:
            print("\n\n[INFO] API服务已停止")


def main():
    """
    主入口函数
    引导用户选择语言和界面模式
    """
    # 创建参数解析器（用于解析命令行参数）
    parser = create_parser()
    args = parser.parse_args()

    # 初始化语言管理器
    initialize_language('zh-CN')

    # 检查是否有 --lang 参数
    selected_lang = None
    if hasattr(args, 'lang') and args.lang:
        lang_map = {
            'zh': 'zh-CN',
            'en': 'en-US',
            'ja': 'ja-JP',
        }
        selected_lang = lang_map.get(args.lang, args.lang)

    # 如果有子命令（非交互模式）
    if args.command:
        # 设置语言
        if selected_lang:
            set_language(selected_lang)

        # 显示横幅
        show_welcome_banner(selected_lang or 'zh-CN')

        # 警告信息
        print("=" * 60)
        print("  ⚠️  警告：仅用于授权安全审计和强度测试！")
        print("=" * 60 + "\n")

        # 执行子命令
        try:
            if args.command == 'attack':
                asyncio.run(run_attack(args))
            elif args.command == 'resume':
                asyncio.run(run_resume(args))
            elif args.command == 'report':
                run_report(args)
            elif args.command == 'web':
                run_web(args)
            elif args.command == 'gui':
                run_gui(args)
            elif args.command == 'api':
                run_api(args)
            elif args.command == 'launcher':
                run_launcher(args)
            else:
                parser.print_help()
                sys.exit(1)

        except KeyboardInterrupt:
            print("\n\n[INFO] 操作已取消")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 发生未知错误: {e}")
            sys.exit(1)

        return

    # ========== 交互模式（无子命令） ==========

    # 第一步：选择语言
    if not selected_lang:
        selected_lang = interactive_select_language()

    # 设置语言
    set_language(selected_lang)

    # 第二步：显示欢迎横幅
    show_welcome_banner(selected_lang)

    # 第三步：选择界面模式
    selected_mode = interactive_select_mode()

    # 第四步：启动对应模式
    print(f"\n[INFO] 正在启动 {selected_mode.upper()} 模式...")
    print("=" * 60)

    try:
        run_mode(selected_mode, selected_lang)
    except KeyboardInterrupt:
        print("\n\n[INFO] 用户中断操作")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()