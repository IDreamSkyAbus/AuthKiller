"""
THINKER GUI 进度面板
包含进度显示、任务控制按钮和日志显示
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any
from datetime import datetime


class ProgressPanel:
    """
    进度面板类
    显示任务进度、统计信息和实时日志
    """

    def __init__(self, parent: ttk.Frame, app):
        """
        初始化进度面板

        Args:
            parent: 父容器
            app: ThinkerApp应用实例
        """
        self.parent = parent
        self.app = app

        # 创建布局
        self._create_layout()

    def _create_layout(self):
        """
        创建进度面板布局
        """
        # 主框架
        main_frame = ttk.Frame(self.parent, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上半部分：控制按钮和进度条
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # 控制按钮
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(side=tk.LEFT, padx=(0, 20))

        self.start_button = ttk.Button(
            buttons_frame,
            text="▶ 启动",
            command=self.app.start_attack,
            width=12,
            style='Start.TButton'
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(
            buttons_frame,
            text="⏸ 暂停",
            command=self.app.pause_attack,
            width=12,
            state='disabled'
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            buttons_frame,
            text="⏹ 停止",
            command=self.app.stop_attack,
            width=12,
            state='disabled'
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # 进度条
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(progress_frame, text="进度:").pack(side=tk.LEFT, padx=(0, 5))

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            mode='determinate',
            length=300,
            style='Horizontal.TProgressbar'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.progress_label = ttk.Label(progress_frame, text="0.00%", width=10)
        self.progress_label.pack(side=tk.LEFT, padx=5)

        # 统计信息框架
        stats_frame = ttk.LabelFrame(main_frame, text="统计信息", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # 统计信息网格
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        # 第一行
        ttk.Label(stats_grid, text="总尝试次数:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.total_attempts_label = ttk.Label(stats_grid, text="0", width=15)
        self.total_attempts_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(stats_grid, text="成功次数:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.success_count_label = ttk.Label(stats_grid, text="0", foreground='green', width=15)
        self.success_count_label.grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(stats_grid, text="失败次数:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.failed_count_label = ttk.Label(stats_grid, text="0", foreground='red', width=15)
        self.failed_count_label.grid(row=0, column=5, sticky=tk.W, padx=5)

        # 第二行
        ttk.Label(stats_grid, text="剩余组合:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.remaining_label = ttk.Label(stats_grid, text="0", width=15)
        self.remaining_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(stats_grid, text="成功率:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.success_rate_label = ttk.Label(stats_grid, text="0.00%", width=15)
        self.success_rate_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(stats_grid, text="耗时:").grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        self.elapsed_time_label = ttk.Label(stats_grid, text="0.00s", width=15)
        self.elapsed_time_label.grid(row=1, column=5, sticky=tk.W, padx=5, pady=5)

        # 第三行
        ttk.Label(stats_grid, text="平均速度:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.avg_speed_label = ttk.Label(stats_grid, text="0.00/s", width=15)
        self.avg_speed_label.grid(row=2, column=1, sticky=tk.W, padx=5)

        ttk.Label(stats_grid, text="任务状态:").grid(row=2, column=2, sticky=tk.W, padx=5)
        self.task_status_label = ttk.Label(stats_grid, text="就绪", foreground='gray', width=15)
        self.task_status_label.grid(row=2, column=3, sticky=tk.W, padx=5)

        ttk.Label(stats_grid, text="当前时间:").grid(row=2, column=4, sticky=tk.W, padx=5)
        self.current_time_label = ttk.Label(stats_grid, text="--:--:--", width=15)
        self.current_time_label.grid(row=2, column=5, sticky=tk.W, padx=5)

        # 更新时间显示
        self._update_time_display()

        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="实时日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            width=80,
            wrap=tk.WORD,
            state='normal'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 日志级别过滤器
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(log_control_frame, text="日志级别:").pack(side=tk.LEFT, padx=5)

        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(
            log_control_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=10,
            state="readonly"
        )
        log_level_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            log_control_frame,
            text="清空日志",
            command=self._clear_log
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            log_control_frame,
            text="导出日志",
            command=self._export_log
        ).pack(side=tk.LEFT, padx=5)

    def _update_time_display(self):
        """
        更新时间显示
        """
        current_time = datetime.now().strftime("%H:%M:%S")
        self.current_time_label.config(text=current_time)
        # 每1秒更新一次
        self.parent.after(1000, self._update_time_display)

    def update_buttons(self, status: str):
        """
        更新控制按钮状态

        Args:
            status: 任务状态 (running, paused, stopped)
        """
        if status == 'running':
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal', text="⏸ 暂停")
            self.stop_button.config(state='normal')
            self.task_status_label.config(text="运行中", foreground='green')

        elif status == 'paused':
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal', text="▶ 恢复")
            self.stop_button.config(state='normal')
            self.task_status_label.config(text="已暂停", foreground='orange')

        elif status == 'stopped':
            self.start_button.config(state='normal')
            self.pause_button.config(state='disabled', text="⏸ 暂停")
            self.stop_button.config(state='disabled')
            self.task_status_label.config(text="已停止", foreground='red')

        else:
            self.start_button.config(state='normal')
            self.pause_button.config(state='disabled')
            self.stop_button.config(state='disabled')
            self.task_status_label.config(text="就绪", foreground='gray')

    def update_progress(self, progress: Dict[str, Any]):
        """
        更新进度显示

        Args:
            progress: 进度信息字典
        """
        total = progress.get('total', 0)
        tested = progress.get('tested', 0)
        remaining = progress.get('remaining', 0)
        success_count = progress.get('success_count', 0)
        progress_percentage = progress.get('progress_percentage', '0.00%')

        # 更新进度条
        if total > 0:
            percentage = (tested / total) * 100
            self.progress_bar['value'] = percentage
            self.progress_label.config(text=f"{percentage:.2f}%")

        # 更新统计信息
        self.total_attempts_label.config(text=str(tested))
        self.success_count_label.config(text=str(success_count))
        self.failed_count_label.config(text=str(tested - success_count))
        self.remaining_label.config(text=str(remaining))

        # 计算成功率
        if tested > 0:
            success_rate = (success_count / tested) * 100
            self.success_rate_label.config(text=f"{success_rate:.2f}%")
        else:
            self.success_rate_label.config(text="0.00%")

    def update_stats(self, stats: Dict[str, Any]):
        """
        更新统计信息

        Args:
            stats: 统计信息字典
        """
        self.total_attempts_label.config(text=str(stats.get('total_attempts', 0)))
        self.success_count_label.config(text=str(stats.get('success_count', 0)))
        self.failed_count_label.config(text=str(stats.get('failed_count', 0)))
        self.remaining_label.config(text=str(stats.get('remaining_combinations', 0)))
        self.success_rate_label.config(text=stats.get('success_rate', '0.00%'))
        self.elapsed_time_label.config(text=stats.get('elapsed_time', '0.00s'))

        # 计算平均速度
        total_attempts = stats.get('total_attempts', 0)
        elapsed_time = float(stats.get('elapsed_time', '0s').replace('s', ''))

        if elapsed_time > 0:
            avg_speed = total_attempts / elapsed_time
            self.avg_speed_label.config(text=f"{avg_speed:.2f}/s")
        else:
            self.avg_speed_label.config(text="0.00/s")

    def log_message(self, message: str, level: str = 'INFO'):
        """
        显示日志消息

        Args:
            message: 日志消息
            level: 日志级别
        """
        # 获取当前时间
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 根据日志级别设置颜色
        colors = {
            'DEBUG': 'gray',
            'INFO': 'black',
            'WARNING': 'orange',
            'ERROR': 'red',
            'SUCCESS': 'green'
        }

        color = colors.get(level.upper(), 'black')

        # 添加日志标签
        log_line = f"[{level}] {timestamp} - {message}\n"

        # 检查日志级别是否满足过滤条件
        current_level = self.log_level_var.get()
        levels_order = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

        if levels_order.index(level.upper()) >= levels_order.index(current_level):
            # 插入日志并设置颜色
            self.log_text.insert(tk.END, log_line)

            # 为新插入的行设置颜色
            start_index = self.log_text.index(f"end-{len(log_line)+1}c")
            end_index = self.log_text.index("end-1c")
            self.log_text.tag_add(level, start_index, end_index)
            self.log_text.tag_config(level, foreground=color)

            # 自动滚动到底部
            self.log_text.see(tk.END)

    def _clear_log(self):
        """
        清空日志
        """
        self.log_text.delete(1.0, tk.END)

    def _export_log(self):
        """
        导出日志到文件
        """
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="导出日志",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")]
        )

        if file_path:
            log_content = self.log_text.get(1.0, tk.END)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                from tkinter import messagebox
                messagebox.showinfo("成功", f"日志已导出:\n{file_path}")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("错误", f"导出日志失败:\n{str(e)}")