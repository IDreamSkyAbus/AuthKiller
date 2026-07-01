"""
Flask 应用主文件
Web GUI 核心逻辑
"""

import os
from flask import Flask, render_template, jsonify, request
from authkiller.web.api import api_bp
from authkiller.web.utils import find_available_port, get_local_ip
# 语言管理模块（预留接口）
from authkiller.utils.language import (
    initialize_language,
    get_web_string,
    get_language_manager,
    set_language,
    get_strings
)


def create_app(template_folder: str = None, static_folder: str = None) -> Flask:
    """
    创建 Flask 应用

    Args:
        template_folder: 模板文件夹路径
        static_folder: 静态文件夹路径

    Returns:
        Flask: Flask 应用实例
    """
    # 获取默认路径
    if template_folder is None:
        template_folder = os.path.join(os.path.dirname(__file__), 'templates')

    if static_folder is None:
        static_folder = os.path.join(os.path.dirname(__file__), 'static')

    # 创建应用
    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)

    # 配置
    app.config['SECRET_KEY'] = 'authkiller-web-gui-2026'
    app.config['JSON_AS_ASCII'] = False  # 支持中文JSON

    # 注册API蓝图
    app.register_blueprint(api_bp, url_prefix='/api')

    # 主页路由
    @app.route('/')
    def index():
        # 获取语言参数
        try:
            manager = get_language_manager()
            current_lang = manager.current_language if manager else 'zh-CN'
        except Exception:
            current_lang = 'zh-CN'
        
        # 检查URL参数
        url_lang = request.args.get('lang')
        if url_lang in ['zh-CN', 'en-US', 'ja-JP']:
            current_lang = url_lang
            try:
                set_language(current_lang)
            except Exception:
                pass
        
        # 根据语言返回对应的字符串
        lang_strings = {
            'zh-CN': {
                'title': 'AuthKiller - 密码测试工具 Web界面',
                'test_config': '测试配置',
                'system_ready': '系统就绪',
                'target_url': '目标URL',
                'protocol_type': '协议类型',
                'protocol_http_form': 'HTTP表单登录',
                'protocol_http_basic': 'HTTP Basic Auth',
                'users_dict': '用户字典',
                'passwords_dict': '密码字典',
                'concurrency': '并发数',
                'timeout': '超时时间',
                'user_field': '用户字段',
                'pass_field': '密码字段',
                'success_pattern': '成功标识',
                'failure_pattern': '失败标识',
                'load_config': '加载配置',
                'save_config': '保存配置',
                'task_control': '任务控制',
                'start_test': '启动测试',
                'pause': '暂停',
                'stop': '停止',
                'resume': '恢复',
                'total_combinations': '总组合数',
                'tested': '已测试',
                'success': '成功',
                'failed': '失败',
                'start_time': '开始时间',
                'estimated_time': '预计完成',
                'realtime_log': '实时日志',
                'test_results': '测试结果',
                'export_results': '导出结果',
                'username': '用户名',
                'password': '密码',
                'status': '状态',
                'status_success': '成功',
                'status_failed': '失败',
                'response_time': '响应时间',
                'test_time': '测试时间',
                'language': '语言',
                'language_changed': '语言已切换',
                'language_change_failed': '语言切换失败',
                'placeholder_target_url': '请输入目标URL，如: http://example.com/login',
                'placeholder_users_file': '请输入用户字典文件路径',
                'placeholder_passwords_file': '请输入密码字典文件路径',
                'placeholder_success_pattern': '登录成功的标识，如: Welcome',
                'placeholder_failure_pattern': '登录失败的标识，如: Invalid',
                'waiting_start': '等待启动...',
                'system_initialized': '系统初始化完成',
                'waiting_config': '等待用户配置',
                'current_page_home': '当前在首页',
                'page_new_task': '新建任务页面',
                'page_history': '历史记录页面',
                'page_templates': '任务模板页面',
                'page_user_dict': '用户字典管理',
                'page_pass_dict': '密码字典管理',
                'page_rules': '密码变异规则',
                'page_results': '测试结果查看',
                'page_reports': '统计报告',
                'page_export': '数据导出',
                'page_config': '配置管理',
                'page_logs': '系统日志',
                'page_about': '关于工具',
                'page_new_task_desc': '在此创建新的密码测试任务，配置目标、字典和测试参数。',
                'page_history_desc': '查看历史测试任务记录、结果和分析。',
                'page_templates_desc': '管理和使用预设的任务模板，快速开始常见场景的测试。',
                'page_user_dict_desc': '管理用户名字典，支持上传、编辑和分类管理。',
                'page_pass_dict_desc': '管理密码字典，支持上传、编辑和分类管理。',
                'page_rules_desc': '配置密码变异规则，如添加数字、特殊字符、大小写变换等。',
                'page_results_desc': '查看详细测试结果，支持搜索、筛选和导出。',
                'page_reports_desc': '生成统计报告，包括成功率、平均耗时等指标。',
                'page_export_desc': '导出测试结果和报告为多种格式。',
                'page_config_desc': '管理系统配置，包括默认参数、字典路径等。',
                'page_logs_desc': '查看系统运行日志，便于排查问题。',
                'version': '版本',
                'author': '作者',
                'description': '专业的密码测试工具，仅用于授权安全审计'
            },
            'en-US': {
                'title': 'AuthKiller - Password Testing Tool Web UI',
                'test_config': 'Test Configuration',
                'system_ready': 'System Ready',
                'target_url': 'Target URL',
                'protocol_type': 'Protocol Type',
                'protocol_http_form': 'HTTP Form Login',
                'protocol_http_basic': 'HTTP Basic Auth',
                'users_dict': 'Users Dictionary',
                'passwords_dict': 'Passwords Dictionary',
                'concurrency': 'Concurrency',
                'timeout': 'Timeout',
                'user_field': 'Username Field',
                'pass_field': 'Password Field',
                'success_pattern': 'Success Pattern',
                'failure_pattern': 'Failure Pattern',
                'load_config': 'Load Config',
                'save_config': 'Save Config',
                'task_control': 'Task Control',
                'start_test': 'Start Test',
                'pause': 'Pause',
                'stop': 'Stop',
                'resume': 'Resume',
                'total_combinations': 'Total Combinations',
                'tested': 'Tested',
                'success': 'Success',
                'failed': 'Failed',
                'start_time': 'Start Time',
                'estimated_time': 'Estimated Time',
                'realtime_log': 'Real-time Log',
                'test_results': 'Test Results',
                'export_results': 'Export Results',
                'username': 'Username',
                'password': 'Password',
                'status': 'Status',
                'status_success': 'Success',
                'status_failed': 'Failed',
                'response_time': 'Response Time',
                'test_time': 'Test Time',
                'language': 'Language',
                'language_changed': 'Language Changed',
                'language_change_failed': 'Language Change Failed',
                'placeholder_target_url': 'Enter target URL, e.g.: http://example.com/login',
                'placeholder_users_file': 'Enter users dictionary file path',
                'placeholder_passwords_file': 'Enter passwords dictionary file path',
                'placeholder_success_pattern': 'Success pattern, e.g.: Welcome',
                'placeholder_failure_pattern': 'Failure pattern, e.g.: Invalid',
                'waiting_start': 'Waiting to start...',
                'system_initialized': 'System initialized',
                'waiting_config': 'Waiting for user configuration',
                'current_page_home': 'Currently on home page',
                'page_new_task': 'New Task',
                'page_history': 'History',
                'page_templates': 'Task Templates',
                'page_user_dict': 'Users Dictionary',
                'page_pass_dict': 'Passwords Dictionary',
                'page_rules': 'Mutation Rules',
                'page_results': 'Test Results',
                'page_reports': 'Statistical Reports',
                'page_export': 'Data Export',
                'page_config': 'Configuration',
                'page_logs': 'System Logs',
                'page_about': 'About',
                'page_new_task_desc': 'Create new password testing tasks, configure target, dictionaries, and test parameters.',
                'page_history_desc': 'View historical testing task records, results, and analysis.',
                'page_templates_desc': 'Manage and use preset task templates for quick start in common scenarios.',
                'page_user_dict_desc': 'Manage username dictionaries with upload, edit, and category management.',
                'page_pass_dict_desc': 'Manage password dictionaries with upload, edit, and category management.',
                'page_rules_desc': 'Configure password mutation rules, such as adding numbers, special characters, case transformations.',
                'page_results_desc': 'View detailed test results with search, filter, and export support.',
                'page_reports_desc': 'Generate statistical reports including success rate, average time, and other metrics.',
                'page_export_desc': 'Export test results and reports in multiple formats.',
                'page_config_desc': 'Manage system configurations including default parameters, dictionary paths, etc.',
                'page_logs_desc': 'View system running logs for troubleshooting.',
                'version': 'Version',
                'author': 'Author',
                'description': 'Professional password testing tool for authorized security audits only'
            },
            'ja-JP': {
                'title': 'AuthKiller - パスワードテストツール Web UI',
                'test_config': 'テスト設定',
                'system_ready': 'システム準備完了',
                'target_url': 'ターゲットURL',
                'protocol_type': 'プロトコル種別',
                'protocol_http_form': 'HTTPフォームログイン',
                'protocol_http_basic': 'HTTP Basic認証',
                'users_dict': 'ユーザー辞書',
                'passwords_dict': 'パスワード辞書',
                'concurrency': '並行数',
                'timeout': 'タイムアウト',
                'user_field': 'ユーザーフィールド',
                'pass_field': 'パスワードフィールド',
                'success_pattern': '成功パターン',
                'failure_pattern': '失敗パターン',
                'load_config': '設定読込',
                'save_config': '設定保存',
                'task_control': 'タスク制御',
                'start_test': 'テスト開始',
                'pause': '一時停止',
                'stop': '停止',
                'resume': '再開',
                'total_combinations': '総組み合わせ',
                'tested': 'テスト済み',
                'success': '成功',
                'failed': '失敗',
                'start_time': '開始時間',
                'estimated_time': '予想完了',
                'realtime_log': 'リアルタイムログ',
                'test_results': 'テスト結果',
                'export_results': '結果エクスポート',
                'username': 'ユーザー名',
                'password': 'パスワード',
                'status': '状態',
                'status_success': '成功',
                'status_failed': '失敗',
                'response_time': '応答時間',
                'test_time': 'テスト時間',
                'language': '言語',
                'language_changed': '言語変更済み',
                'language_change_failed': '言語変更失敗',
                'placeholder_target_url': 'ターゲットURLを入力、例: http://example.com/login',
                'placeholder_users_file': 'ユーザー辞書ファイルのパスを入力',
                'placeholder_passwords_file': 'パスワード辞書ファイルのパスを入力',
                'placeholder_success_pattern': '成功パターン、例: Welcome',
                'placeholder_failure_pattern': '失敗パターン、例: Invalid',
                'waiting_start': '開始待ち...',
                'system_initialized': 'システム初期化完了',
                'waiting_config': 'ユーザー設定待ち',
                'current_page_home': 'ホームページにいます',
                'page_new_task': '新規タスク',
                'page_history': '履歴',
                'page_templates': 'タスクテンプレート',
                'page_user_dict': 'ユーザー辞書',
                'page_pass_dict': 'パスワード辞書',
                'page_rules': '変異ルール',
                'page_results': 'テスト結果',
                'page_reports': '統計レポート',
                'page_export': 'データエクスポート',
                'page_config': '設定管理',
                'page_logs': 'システムログ',
                'page_about': 'について',
                'page_new_task_desc': '新しいパスワードテストタスクを作成し、ターゲット、辞書、テストパラメータを設定します。',
                'page_history_desc': '過去のテストタスクリコード、結果、分析を表示します。',
                'page_templates_desc': 'プリセットタスクテンプレートを管理し、迅速に開始します。',
                'page_user_dict_desc': 'ユーザー名辞書を管理します。アップロード、編集、カテゴリ管理をサポート。',
                'page_pass_dict_desc': 'パスワード辞書を管理します。アップロード、編集、カテゴリ管理をサポート。',
                'page_rules_desc': 'パスワード変異ルールを設定します。数字、特殊文字、大文字小文字変換など。',
                'page_results_desc': '詳細なテスト結果を表示します。検索、フィルタ、エクスポートをサポート。',
                'page_reports_desc': '成功率、平均時間などの統計レポートを生成します。',
                'page_export_desc': 'テスト結果とレポートを複数の形式でエクスポートします。',
                'page_config_desc': 'デフォルトパラメータ、辞書パスなどのシステム設定を管理します。',
                'page_logs_desc': 'トラブルシューティング用のシステム実行ログを表示します。',
                'version': 'バージョン',
                'author': '作者',
                'description': '認可されたセキュリティ監査専用のプロ用パスワードテストツール'
            }
        }
        
        # 获取对应语言的字符串，如果不存在则回退到中文
        strings = lang_strings.get(current_lang, lang_strings['zh-CN'])
        
        return render_template('index.html', strings=strings, current_lang=current_lang)

    # 语言管理路由（预留接口）
    @app.route('/api/language/set', methods=['POST'])
    def set_language_route():
        """设置语言"""
        try:
            data = request.get_json()
            language = data.get('language', 'zh-CN')
            
            # 使用语言管理器设置语言
            success = set_language(language)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Language changed successfully',
                    'language': language
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Language not supported'
                }), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/language/get', methods=['GET'])
    def get_language_route():
        """获取当前语言"""
        try:
            manager = get_language_manager()
            return jsonify({
                'success': True,
                'language': manager.get_current_language(),
                'language_name': manager.get_language_name(),
                'supported_languages': manager.get_supported_languages()
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/language/strings', methods=['GET'])
    def get_strings_route():
        """获取字符串资源"""
        try:
            module = request.args.get('module', 'web')
            strings = get_strings(module)
            return jsonify({
                'success': True,
                'strings': strings,
                'module': module
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error='页面不存在'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error='服务器内部错误'), 500

    return app


def run_web(host: str = '127.0.0.1', port: int = 37496,
            debug: bool = False, auto_port: bool = True):
    """
    运行 Web 界面

    Args:
        host: 主机地址
        port: 端口号（默认 37496）
        debug: 是否启用调试模式
        auto_port: 是否自动检测可用端口
    """
    # 初始化语言管理器（预留接口）
    initialize_language('zh-CN')
    
    # 创建应用
    app = create_app()

    # 端口检测和自动选择
    actual_port = port
    if auto_port:
        actual_port = find_available_port(port)
        if actual_port is None:
            print(f"[ERROR] 无法找到可用端口（尝试范围: {port} - {port + 100}）")
            return

        if actual_port != port:
            print(f"[INFO]  默认端口 {port} 已被占用，自动切换到端口 {actual_port}")

    # 获取访问地址
    local_ip = get_local_ip()
    urls = [
        f"http://{host}:{actual_port}",
        f"http://{local_ip}:{actual_port}"
    ]

    # 显示启动信息
    print("=" * 60)
    print("AuthKiller Web GUI 已启动")
    print("=" * 60)
    print(f"本地访问: {urls[0]}")
    print(f"局域网访问: {urls[1]}")
    print("=" * 60)
    print("提示:")
    print("  - 在浏览器中打开上述地址即可使用")
    print("  - 按 Ctrl+C 可停止服务")
    print("=" * 60)

    # 启动Flask
    try:
        # 使用 werkzeug 服务器，禁用 reloader 确保干净退出
        app.run(host=host, port=actual_port, debug=debug, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n[INFO] 服务已停止")
    except SystemExit:
        pass
    except Exception as e:
        print(f"\n[ERROR] 启动失败: {e}")
    finally:
        # 清理资源
        import os
        try:
            os._exit(0)  # 强制退出进程，确保端口释放
        except Exception:
            pass


if __name__ == '__main__':
    # 直接运行此文件时的默认配置
    run_web(port=37496, debug=True)