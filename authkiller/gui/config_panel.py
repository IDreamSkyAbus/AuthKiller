"""
THINKER GUI 配置面板
包含协议选择、字典配置、并发和超时设置
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Dict, Any


class ConfigPanel:
    """
    配置面板类
    提供任务配置的GUI界面
    """

    def __init__(self, parent: ttk.Frame, app):
        """
        初始化配置面板

        Args:
            parent: 父容器
            app: ThinkerApp应用实例
        """
        self.parent = parent
        self.app = app

        # 创建Notebook（标签页容器）
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建各个配置标签页
        self._create_target_tab()
        self._create_dictionary_tab()
        self._create_performance_tab()
        self._create_detection_tab()

    def _create_target_tab(self):
        """
        创建目标配置标签页
        """
        target_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(target_frame, text="目标配置")

        # 协议选择
        protocol_frame = ttk.LabelFrame(target_frame, text="协议选择", padding="10")
        protocol_frame.pack(fill=tk.X, pady=(0, 10))

        self.protocol_var = tk.StringVar(value="http_form")
        ttk.Radiobutton(
            protocol_frame,
            text="HTTP 表单登录 (POST/GET)",
            variable=self.protocol_var,
            value="http_form"
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            protocol_frame,
            text="HTTP Basic 认证",
            variable=self.protocol_var,
            value="http_basic"
        ).pack(anchor=tk.W)

        # URL配置
        url_frame = ttk.LabelFrame(target_frame, text="URL配置", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(url_frame, text="目标URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.url_entry.insert(0, "http://example.com/login")

        ttk.Label(url_frame, text="请求方法:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.method_var = tk.StringVar(value="POST")
        method_combo = ttk.Combobox(url_frame, textvariable=self.method_var, values=["POST", "GET"], width=10, state="readonly")
        method_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        url_frame.columnconfigure(1, weight=1)

        # 请求体配置（仅HTTP表单）
        body_frame = ttk.LabelFrame(target_frame, text="请求体配置 (HTTP表单)", padding="10")
        body_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(body_frame, text="请求体模板:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.body_entry = ttk.Entry(body_frame, width=50)
        self.body_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.body_entry.insert(0, "username={user}&password={pass}")

        ttk.Label(body_frame, text="(使用 {user} 和 {pass} 作为占位符)").grid(row=1, column=1, sticky=tk.W)

        ttk.Label(body_frame, text="Content-Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.content_type_var = tk.StringVar(value="urlencoded")
        content_type_combo = ttk.Combobox(
            body_frame,
            textvariable=self.content_type_var,
            values=["urlencoded", "json", "xml"],
            width=15,
            state="readonly"
        )
        content_type_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        body_frame.columnconfigure(1, weight=1)

        # Headers配置
        headers_frame = ttk.LabelFrame(target_frame, text="自定义Headers", padding="10")
        headers_frame.pack(fill=tk.BOTH, expand=True)

        # Headers文本框
        self.headers_text = tk.Text(headers_frame, height=5, width=50)
        self.headers_text.pack(fill=tk.BOTH, expand=True)

        # 默认Headers
        default_headers = """User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Content-Type: application/x-www-form-urlencoded"""
        self.headers_text.insert(tk.END, default_headers)

    def _create_dictionary_tab(self):
        """
        创建字典配置标签页
        """
        dict_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(dict_frame, text="字典配置")

        # 攻击模式
        mode_frame = ttk.LabelFrame(dict_frame, text="攻击模式", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.mode_var = tk.StringVar(value="normal")
        ttk.Radiobutton(
            mode_frame,
            text="普通模式 (所有用户名×所有密码)",
            variable=self.mode_var,
            value="normal"
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            mode_frame,
            text="单用户模式 (一个用户名×所有密码)",
            variable=self.mode_var,
            value="single_user"
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            mode_frame,
            text="密码喷洒模式 (一个密码×所有用户名)",
            variable=self.mode_var,
            value="single_password"
        ).pack(anchor=tk.W)

        # 单用户/单密码配置
        self.single_config_frame = ttk.Frame(mode_frame)
        self.single_config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.single_config_frame, text="指定用户名:").grid(row=0, column=0, sticky=tk.W)
        self.single_user_entry = ttk.Entry(self.single_config_frame, width=20)
        self.single_user_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.single_user_entry.insert(0, "admin")

        ttk.Label(self.single_config_frame, text="指定密码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.single_password_entry = ttk.Entry(self.single_config_frame, width=20)
        self.single_password_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.single_password_entry.insert(0, "admin")

        # 用户名字典
        users_frame = ttk.LabelFrame(dict_frame, text="用户名字典", padding="10")
        users_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(users_frame, text="字典文件:").grid(row=0, column=0, sticky=tk.W)
        self.users_file_entry = ttk.Entry(users_frame, width=40)
        self.users_file_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)

        ttk.Button(
            users_frame,
            text="选择文件",
            command=self._select_users_file
        ).grid(row=0, column=2, padx=5)

        users_frame.columnconfigure(1, weight=1)

        # 密码字典
        passwords_frame = ttk.LabelFrame(dict_frame, text="密码字典", padding="10")
        passwords_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(passwords_frame, text="字典文件:").grid(row=0, column=0, sticky=tk.W)
        self.passwords_file_entry = ttk.Entry(passwords_frame, width=40)
        self.passwords_file_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)

        ttk.Button(
            passwords_frame,
            text="选择文件",
            command=self._select_passwords_file
        ).grid(row=0, column=2, padx=5)

        passwords_frame.columnconfigure(1, weight=1)

        # 字典预览
        preview_frame = ttk.LabelFrame(dict_frame, text="字典预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        preview_paned = ttk.PanedWindow(preview_frame, orient=tk.HORIZONTAL)
        preview_paned.pack(fill=tk.BOTH, expand=True)

        # 用户名预览
        users_preview_frame = ttk.Frame(preview_paned)
        ttk.Label(users_preview_frame, text="用户名列表 (前10个):").pack(anchor=tk.W)
        self.users_preview_text = tk.Text(users_preview_frame, height=10, width=30)
        self.users_preview_text.pack(fill=tk.BOTH, expand=True)
        preview_paned.add(users_preview_frame, weight=1)

        # 密码预览
        passwords_preview_frame = ttk.Frame(preview_paned)
        ttk.Label(passwords_preview_frame, text="密码列表 (前10个):").pack(anchor=tk.W)
        self.passwords_preview_text = tk.Text(passwords_preview_frame, height=10, width=30)
        self.passwords_preview_text.pack(fill=tk.BOTH, expand=True)
        preview_paned.add(passwords_preview_frame, weight=1)

        # 预览按钮
        ttk.Button(
            dict_frame,
            text="预览字典",
            command=self._preview_dictionaries
        ).pack(pady=10)

    def _create_performance_tab(self):
        """
        创建性能配置标签页
        """
        perf_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(perf_frame, text="性能配置")

        # 并发设置
        concurrency_frame = ttk.LabelFrame(perf_frame, text="并发设置", padding="10")
        concurrency_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(concurrency_frame, text="并发数:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.concurrency_var = tk.IntVar(value=10)
        concurrency_spinbox = ttk.Spinbox(
            concurrency_frame,
            from_=1,
            to=100,
            textvariable=self.concurrency_var,
            width=10
        )
        concurrency_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(concurrency_frame, text="(建议: 10-30)").grid(row=0, column=2, sticky=tk.W)

        # 超时设置
        timeout_frame = ttk.LabelFrame(perf_frame, text="超时设置", padding="10")
        timeout_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(timeout_frame, text="请求超时 (秒):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.IntVar(value=10)
        timeout_spinbox = ttk.Spinbox(
            timeout_frame,
            from_=1,
            to=60,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(timeout_frame, text="重试次数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.retry_var = tk.IntVar(value=3)
        retry_spinbox = ttk.Spinbox(
            timeout_frame,
            from_=1,
            to=10,
            textvariable=self.retry_var,
            width=10
        )
        retry_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # 断点续传
        checkpoint_frame = ttk.LabelFrame(perf_frame, text="断点续传", padding="10")
        checkpoint_frame.pack(fill=tk.X, pady=(0, 10))

        self.enable_checkpoint_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            checkpoint_frame,
            text="启用断点续传",
            variable=self.enable_checkpoint_var
        ).pack(anchor=tk.W)

        ttk.Label(checkpoint_frame, text="断点保存间隔:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.checkpoint_interval_var = tk.IntVar(value=100)
        checkpoint_spinbox = ttk.Spinbox(
            checkpoint_frame,
            from_=10,
            to=1000,
            textvariable=self.checkpoint_interval_var,
            width=10
        )
        checkpoint_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(checkpoint_frame, text="(尝试次数)").grid(row=1, column=2, sticky=tk.W)

    def _create_detection_tab(self):
        """
        创建检测配置标签页
        """
        detection_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(detection_frame, text="检测配置")

        # 成功判定
        success_frame = ttk.LabelFrame(detection_frame, text="成功判定", padding="10")
        success_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(success_frame, text="成功状态码:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.success_codes_entry = ttk.Entry(success_frame, width=30)
        self.success_codes_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.success_codes_entry.insert(0, "200, 302")

        ttk.Label(success_frame, text="(多个状态码用逗号分隔)").grid(row=0, column=2, sticky=tk.W)

        ttk.Label(success_frame, text="成功响应模式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.success_pattern_entry = ttk.Entry(success_frame, width=30)
        self.success_pattern_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(success_frame, text="(正则表达式，可选)").grid(row=1, column=2, sticky=tk.W)

        ttk.Label(success_frame, text="失败响应模式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.failure_pattern_entry = ttk.Entry(success_frame, width=30)
        self.failure_pattern_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(success_frame, text="(正则表达式，可选)").grid(row=2, column=2, sticky=tk.W)

        # 防御检测
        defense_frame = ttk.LabelFrame(detection_frame, text="防御检测", padding="10")
        defense_frame.pack(fill=tk.X, pady=(0, 10))

        self.detect_rate_limit_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            defense_frame,
            text="检测速率限制 (429状态码)",
            variable=self.detect_rate_limit_var
        ).pack(anchor=tk.W)

        self.auto_throttle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            defense_frame,
            text="自动降速",
            variable=self.auto_throttle_var
        ).pack(anchor=tk.W)

        throttle_frame = ttk.Frame(defense_frame)
        throttle_frame.pack(fill=tk.X, pady=5)

        ttk.Label(throttle_frame, text="降速延迟 (秒):").grid(row=0, column=0, sticky=tk.W)
        self.throttle_delay_var = tk.IntVar(value=5)
        throttle_spinbox = ttk.Spinbox(
            throttle_frame,
            from_=1,
            to=30,
            textvariable=self.throttle_delay_var,
            width=10
        )
        throttle_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(throttle_frame, text="最大速率限制重试:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_rate_limit_var = tk.IntVar(value=3)
        max_rate_spinbox = ttk.Spinbox(
            throttle_frame,
            from_=1,
            to=10,
            textvariable=self.max_rate_limit_var,
            width=10
        )
        max_rate_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

    def _select_users_file(self):
        """
        选择用户名字典文件
        """
        file_path = filedialog.askopenfilename(
            title="选择用户名字典文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.users_file_entry.delete(0, tk.END)
            self.users_file_entry.insert(0, file_path)

    def _select_passwords_file(self):
        """
        选择密码字典文件
        """
        file_path = filedialog.askopenfilename(
            title="选择密码字典文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.passwords_file_entry.delete(0, tk.END)
            self.passwords_file_entry.insert(0, file_path)

    def _preview_dictionaries(self):
        """
        预览字典内容
        """
        users_file = self.users_file_entry.get()
        passwords_file = self.passwords_file_entry.get()

        # 清空预览
        self.users_preview_text.delete(1.0, tk.END)
        self.passwords_preview_text.delete(1.0, tk.END)

        # 预览用户名
        if users_file:
            try:
                with open(users_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [line.strip() for line in f.readlines()[:10] if line.strip()]
                    self.users_preview_text.insert(tk.END, '\n'.join(lines))
            except Exception as e:
                self.users_preview_text.insert(tk.END, f"读取失败: {str(e)}")

        # 预览密码
        if passwords_file:
            try:
                with open(passwords_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [line.strip() for line in f.readlines()[:10] if line.strip()]
                    self.passwords_preview_text.insert(tk.END, '\n'.join(lines))
            except Exception as e:
                self.passwords_preview_text.insert(tk.END, f"读取失败: {str(e)}")

    def get_config_data(self) -> Dict[str, Any]:
        """
        从GUI获取配置数据

        Returns:
            Dict: 配置数据字典
        """
        # 解析Headers
        headers_text = self.headers_text.get(1.0, tk.END).strip()
        headers = {}
        for line in headers_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()

        # 解析成功状态码
        success_codes_text = self.success_codes_entry.get().strip()
        success_codes = [int(code.strip()) for code in success_codes_text.split(',') if code.strip()]

        # 构建配置字典
        config = {
            'target': {
                'url': self.url_entry.get().strip(),
                'method': self.method_var.get(),
                'headers': headers,
                'body_template': self.body_entry.get().strip(),
                'content_type': self.content_type_var.get(),
                'cookies': {}
            },
            'payload': {
                'users_file': self.users_file_entry.get().strip(),
                'passwords_file': self.passwords_file_entry.get().strip(),
                'mode': self.mode_var.get(),
                'single_user_username': self.single_user_entry.get().strip(),
                'single_password_value': self.single_password_entry.get().strip(),
                'rules': []
            },
            'performance': {
                'concurrency': self.concurrency_var.get(),
                'timeout': self.timeout_var.get(),
                'retry_times': self.retry_var.get(),
                'checkpoint_interval': self.checkpoint_interval_var.get()
            },
            'detection': {
                'success_status_codes': success_codes,
                'success_pattern': self.success_pattern_entry.get().strip() or None,
                'failure_pattern': self.failure_pattern_entry.get().strip() or None,
                'protocol': self.protocol_var.get()
            },
            'defense': {
                'detect_rate_limit': self.detect_rate_limit_var.get(),
                'auto_throttle': self.auto_throttle_var.get(),
                'throttle_delay': self.throttle_delay_var.get(),
                'max_rate_limit_retries': self.max_rate_limit_var.get()
            },
            'output': {
                'log_level': 'INFO',
                'log_file': None,
                'result_file': 'results.json',
                'checkpoint_dir': 'checkpoints'
            }
        }

        return config

    def load_config_to_gui(self):
        """
        从ConfigManager加载配置到GUI
        """
        if not self.app.config_manager:
            return

        config = self.app.config_manager.config

        # 目标配置
        target = config.get('target', {})
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, target.get('url', ''))

        self.method_var.set(target.get('method', 'POST'))

        self.body_entry.delete(0, tk.END)
        self.body_entry.insert(0, target.get('body_template', ''))

        self.content_type_var.set(target.get('content_type', 'urlencoded'))

        # Headers
        headers = target.get('headers', {})
        headers_text = '\n'.join([f"{k}: {v}" for k, v in headers.items()])
        self.headers_text.delete(1.0, tk.END)
        self.headers_text.insert(tk.END, headers_text)

        # 字典配置
        payload = config.get('payload', {})
        self.users_file_entry.delete(0, tk.END)
        self.users_file_entry.insert(0, payload.get('users_file', ''))

        self.passwords_file_entry.delete(0, tk.END)
        self.passwords_file_entry.insert(0, payload.get('passwords_file', ''))

        self.mode_var.set(payload.get('mode', 'normal'))

        self.single_user_entry.delete(0, tk.END)
        self.single_user_entry.insert(0, payload.get('single_user_username', 'admin'))

        self.single_password_entry.delete(0, tk.END)
        self.single_password_entry.insert(0, payload.get('single_password_value', 'admin'))

        # 性能配置
        performance = config.get('performance', {})
        self.concurrency_var.set(performance.get('concurrency', 10))
        self.timeout_var.set(performance.get('timeout', 10))
        self.retry_var.set(performance.get('retry_times', 3))
        self.checkpoint_interval_var.set(performance.get('checkpoint_interval', 100))

        # 检测配置
        detection = config.get('detection', {})
        self.protocol_var.set(detection.get('protocol', 'http_form'))

        success_codes = detection.get('success_status_codes', [200, 302])
        self.success_codes_entry.delete(0, tk.END)
        self.success_codes_entry.insert(0, ', '.join([str(code) for code in success_codes]))

        success_pattern = detection.get('success_pattern', '')
        self.success_pattern_entry.delete(0, tk.END)
        self.success_pattern_entry.insert(0, success_pattern or '')

        failure_pattern = detection.get('failure_pattern', '')
        self.failure_pattern_entry.delete(0, tk.END)
        self.failure_pattern_entry.insert(0, failure_pattern or '')

        # 防御配置
        defense = config.get('defense', {})
        self.detect_rate_limit_var.set(defense.get('detect_rate_limit', True))
        self.auto_throttle_var.set(defense.get('auto_throttle', True))
        self.throttle_delay_var.set(defense.get('throttle_delay', 5))
        self.max_rate_limit_var.set(defense.get('max_rate_limit_retries', 3))