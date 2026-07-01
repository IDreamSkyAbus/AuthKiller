"""
THINKER GUI 主窗口
整合配置面板、进度面板和结果面板
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

from authkiller.gui.config_panel import ConfigPanel
from authkiller.gui.progress_panel import ProgressPanel
from authkiller.gui.result_panel import ResultPanel


class MainWindow:
    """
    主窗口类
    整合所有GUI组件，提供统一的用户界面
    """

    def __init__(self, root: tk.Tk, app):
        """
        初始化主窗口

        Args:
            root: Tkinter根窗口
            app: ThinkerApp应用实例
        """
        self.root = root
        self.app = app

        # 窗口设置
        self._setup_window()

        # 创建菜单栏
        self._create_menu()

        # 创建主布局
        self._create_layout()

        # 创建状态栏
        self._create_status_bar()

        # 进度更新定时器
        self.progress_timer: Optional[str] = None

    def _setup_window(self):
        """
        设置窗口属性
        """
        self.root.title("THINKER GUI - AuthKiller")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # 设置窗口图标（如果存在）
        try:
            # self.root.iconbitmap("icon.ico")
            pass
        except Exception:
            pass

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.app.quit_app)

        # 设置样式
        self._setup_styles()

    def _setup_styles(self):
        """
        设置TTK样式
        """
        style = ttk.Style()

        # 主题设置
        style.theme_use('clam')  # 使用clam主题，更适合自定义

        # 自定义样式
        style.configure('Title.TLabel', font=('微软雅黑', 14, 'bold'))
        style.configure('Status.TLabel', font=('微软雅黑', 9))
        style.configure('TButton', font=('微软雅黑', 10))
        style.configure('Start.TButton', font=('微软雅黑', 11, 'bold'))
        style.configure('TNotebook.Tab', font=('微软雅黑', 10, 'bold'), padding=[10, 5])

        # 进度条样式
        style.configure('Horizontal.TProgressbar', thickness=25)

    def _create_menu(self):
        """
        创建菜单栏
        """
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="加载配置", command=self._load_config_dialog)
        file_menu.add_command(label="保存配置", command=self._save_config_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="导出结果 (JSON)", command=lambda: self.app.export_results('json'))
        file_menu.add_command(label="导出结果 (CSV)", command=lambda: self.app.export_results('csv'))
        file_menu.add_command(label="导出结果 (TXT)", command=lambda: self.app.export_results('txt'))
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.app.quit_app)

        # 任务菜单
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="任务", menu=task_menu)
        task_menu.add_command(label="启动", command=self.app.start_attack)
        task_menu.add_command(label="暂停/恢复", command=self.app.pause_attack)
        task_menu.add_command(label="停止", command=self.app.stop_attack)

        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)

        # 语言子菜单（预留）
        lang_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="语言", menu=lang_menu)
        lang_menu.add_command(label="简体中文", command=lambda: self.app.set_language('zh_CN'))
        lang_menu.add_command(label="英语", command=lambda: self.app.set_language('en_US'))
        lang_menu.add_separator()
        lang_menu.add_command(label="(更多语言)", state='disabled')

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)

    def _create_layout(self):
        """
        创建主布局
        """
        # 主容器
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上半部分：配置面板
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # 配置面板
        self.config_panel = ConfigPanel(top_frame, self.app)
        self.config_panel.pack(fill=tk.BOTH, expand=True)

        # 下半部分：进度和结果
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # 创建分割布局
        paned_window = ttk.PanedWindow(bottom_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 进度面板
        progress_frame = ttk.Frame(paned_window)
        self.progress_panel = ProgressPanel(progress_frame, self.app)
        self.progress_panel.pack(fill=tk.BOTH, expand=True)
        paned_window.add(progress_frame, weight=1)

        # 结果面板
        result_frame = ttk.Frame(paned_window)
        self.result_panel = ResultPanel(result_frame, self.app)
        self.result_panel.pack(fill=tk.BOTH, expand=True)
        paned_window.add(result_frame, weight=2)

    def _create_status_bar(self):
        """
        创建状态栏
        """
        status_bar = ttk.Frame(self.root)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 状态标签
        self.status_label = ttk.Label(
            status_bar,
            text="就绪",
            style='Status.TLabel',
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 版本标签
        version_label = ttk.Label(
            status_bar,
            text="v1.0.0",
            style='Status.TLabel',
            relief=tk.SUNKEN,
            anchor=tk.E,
            width=10
        )
        version_label.pack(side=tk.RIGHT)

    def _load_config_dialog(self):
        """
        加载配置对话框
        """
        from tkinter import filedialog
        config_path = filedialog.askopenfilename(
            title="加载配置文件",
            filetypes=[
                ("JSON文件", "*.json"),
                ("YAML文件", "*.yaml *.yml"),
                ("所有文件", "*.*")
            ]
        )

        if config_path:
            if self.app.load_config(config_path):
                # 更新配置面板
                self.config_panel.load_config_to_gui()
                self.update_status(f"配置加载成功: {config_path}")

    def _save_config_dialog(self):
        """
        保存配置对话框
        """
        from tkinter import filedialog
        config_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[
                ("JSON文件", "*.json"),
                ("YAML文件", "*.yaml *.yml"),
                ("所有文件", "*.*")
            ]
        )

        if config_path:
            # 从GUI获取配置
            config_data = self.config_panel.get_config_data()
            self.app.update_config_from_gui(config_data)

            if self.app.save_config(config_path):
                self.update_status(f"配置保存成功: {config_path}")

    def _show_help(self):
        """
        显示帮助信息
        """
        help_text = """
THINKER GUI 使用说明

1. 配置设置
   - 选择协议类型（HTTP表单或HTTP Basic）
   - 设置目标URL和请求参数
   - 配置用户名和密码字典文件
   - 设置并发数和超时时间

2. 任务控制
   - 启动：开始执行攻击任务
   - 暂停/恢复：暂停或恢复正在运行的任务
   - 停止：停止当前任务

3. 结果查看
   - 实时显示进度和统计信息
   - 查看成功的凭证列表
   - 支持导出为JSON、CSV、TXT格式

4. 注意事项
   - 请确保字典文件存在且可读
   - 合理设置并发数，避免对目标造成过大压力
   - 遵守法律法规，仅用于合法的测试场景
        """
        messagebox.showinfo("使用说明", help_text)

    def _show_about(self):
        """
        显示关于信息
        """
        about_text = """
THINKER GUI - AuthKiller
版本: 1.0.0

基于Tkinter的桌面GUI应用
用于密码测试工具的图形化操作

核心功能：
- 多协议支持（HTTP表单、HTTP Basic）
- 高并发处理
- 断点续传
- 实时进度监控
- 多格式结果导出

开发者：AuthKiller Team
        """
        messagebox.showinfo("关于", about_text)

    def update_task_status(self, status: str):
        """
        更新任务状态

        Args:
            status: 状态 (running, paused, stopped)
        """
        status_text = {
            'running': "运行中",
            'paused': "已暂停",
            'stopped': "已停止"
        }

        self.update_status(f"状态: {status_text.get(status, '未知')}")

        # 更新控制按钮
        self.progress_panel.update_buttons(status)

        # 启动或停止进度更新
        if status == 'running':
            self._start_progress_update()
        else:
            self._stop_progress_update()

    def update_results(self, stats: Dict[str, Any]):
        """
        更新结果显示

        Args:
            stats: 统计信息字典
        """
        # 更新进度面板统计
        self.progress_panel.update_stats(stats)

        # 更新结果面板
        if self.app.engine and self.app.engine.success_results:
            self.result_panel.update_results(self.app.engine.success_results)

        messagebox.showinfo("任务完成", f"任务已完成！\n成功找到 {stats.get('success_count', 0)} 个凭证")

    def update_status(self, message: str):
        """
        更新状态栏信息

        Args:
            message: 状态信息
        """
        self.status_label.config(text=message)

    def _start_progress_update(self):
        """
        启动进度更新定时器
        """
        self._update_progress()

    def _stop_progress_update(self):
        """
        停止进度更新定时器
        """
        if self.progress_timer:
            self.root.after_cancel(self.progress_timer)
            self.progress_timer = None

    def _update_progress(self):
        """
        更新进度显示
        """
        if not self.app.is_running:
            return

        # 获取进度
        progress = self.app.get_progress()

        # 更新进度面板
        self.progress_panel.update_progress(progress)

        # 继续定时更新（每500ms）
        self.progress_timer = self.root.after(500, self._update_progress)

    def log_message(self, message: str, level: str = 'INFO'):
        """
        在日志面板显示消息

        Args:
            message: 日志消息
            level: 日志级别
        """
        self.progress_panel.log_message(message, level)