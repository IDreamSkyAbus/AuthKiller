"""
THINKER GUI 主应用入口
协调各个GUI组件，集成核心模块
"""

import tkinter as tk
from tkinter import messagebox
import asyncio
import threading
from typing import Optional, Dict, Any
from pathlib import Path

from authkiller.gui.main_window import MainWindow
from authkiller.core.config import ConfigManager
from authkiller.core.engine import AttackEngine
from authkiller.utils.logger import Logger
# 语言管理模块（预留接口）
from authkiller.utils.language import (
    initialize_language,
    get_gui_string,
    get_language_manager,
    set_language,
    get_strings
)


class ThinkerApp:
    """
    THINKER GUI 主应用类
    负责协调GUI组件和核心业务逻辑
    """

    def __init__(self):
        """
        初始化主应用
        """
        # 创建主窗口
        self.root = tk.Tk()
        self.main_window = MainWindow(self.root, self)

        # 核心模块
        self.config_manager: Optional[ConfigManager] = None
        self.engine: Optional[AttackEngine] = None

        # 日志器
        self.logger = Logger.get_logger('thinker_gui')

        # 任务控制
        self.is_running = False
        self.is_paused = False
        self.task_thread: Optional[threading.Thread] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None

        # 语言设置（使用新的语言管理器）
        initialize_language('zh-CN')  # 默认中文
        self.language_manager = get_language_manager()

        # 初始化配置
        self._init_default_config()

    def _init_default_config(self):
        """
        初始化默认配置
        """
        self.config_manager = ConfigManager()

    def run(self):
        """
        运行应用
        """
        self.logger.info("THINKER GUI 启动")
        self.root.mainloop()

    def load_config(self, config_path: str) -> bool:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            bool: 是否加载成功
        """
        try:
            self.config_manager.load_config(config_path)
            self.logger.info(f"配置文件加载成功: {config_path}")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件失败:\n{str(e)}")
            self.logger.error(f"加载配置文件失败: {e}")
            return False

    def save_config(self, config_path: str) -> bool:
        """
        保存配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            bool: 是否保存成功
        """
        try:
            self.config_manager.save_config(config_path)
            self.logger.info(f"配置文件保存成功: {config_path}")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存配置文件失败:\n{str(e)}")
            self.logger.error(f"保存配置文件失败: {e}")
            return False

    def update_config_from_gui(self, config_data: Dict[str, Any]):
        """
        从GUI更新配置

        Args:
            config_data: 配置数据字典
        """
        if self.config_manager:
            self.config_manager.update_from_dict(config_data)

    def start_attack(self):
        """
        启动攻击任务
        """
        if self.is_running:
            messagebox.showwarning("警告", "任务已在运行中")
            return

        # 验证配置
        is_valid, error_message = self.config_manager.validate()
        if not is_valid:
            messagebox.showerror("配置错误", f"配置验证失败:\n{error_message}")
            return

        # 初始化引擎
        try:
            self.engine = AttackEngine(self.config_manager)
            self.logger.info("引擎初始化成功")
        except Exception as e:
            messagebox.showerror("错误", f"引擎初始化失败:\n{str(e)}")
            self.logger.error(f"引擎初始化失败: {e}")
            return

        # 启动任务线程
        self.is_running = True
        self.is_paused = False
        self.task_thread = threading.Thread(target=self._run_attack_task, daemon=True)
        self.task_thread.start()

        # 更新GUI状态
        self.main_window.update_task_status('running')
        self.logger.info("攻击任务已启动")

    def _run_attack_task(self):
        """
        在线程中运行攻击任务
        """
        # 创建事件循环
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        try:
            # 运行引擎
            self.event_loop.run_until_complete(self._execute_attack())
        except Exception as e:
            self.logger.error(f"任务执行异常: {e}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"任务执行异常:\n{str(e)}"))
        finally:
            # 清理
            self.event_loop.close()
            self.is_running = False
            self.root.after(0, lambda: self.main_window.update_task_status('stopped'))

    async def _execute_attack(self):
        """
        执行攻击任务
        """
        try:
            # 初始化引擎
            await self.engine.initialize()

            # 运行攻击
            stats = await self.engine.run()

            # 更新结果
            self.root.after(0, lambda: self.main_window.update_results(stats))

        except Exception as e:
            raise e

    def pause_attack(self):
        """
        暂停攻击任务
        """
        if not self.is_running:
            return

        if self.is_paused:
            # 恢复任务
            self.engine.resume()
            self.is_paused = False
            self.main_window.update_task_status('running')
            self.logger.info("任务已恢复")
        else:
            # 暂停任务
            self.engine.pause()
            self.is_paused = True
            self.main_window.update_task_status('paused')
            self.logger.info("任务已暂停")

    def stop_attack(self):
        """
        停止攻击任务
        """
        if not self.is_running:
            return

        # 发送停止信号
        if self.engine:
            self.engine.stop()

        self.is_running = False
        self.is_paused = False

        # 更新GUI状态
        self.main_window.update_task_status('stopped')
        self.logger.info("任务已停止")

    def get_progress(self) -> Dict[str, Any]:
        """
        获取当前进度

        Returns:
            Dict: 进度信息
        """
        if self.engine:
            return self.engine.get_progress()
        return {
            'total': 0,
            'tested': 0,
            'remaining': 0,
            'success_count': 0,
            'progress_percentage': '0.00%',
            'is_running': False
        }

    def export_results(self, format: str = 'json') -> str:
        """
        导出结果

        Args:
            format: 导出格式 (json, csv, txt)

        Returns:
            str: 导出文件路径
        """
        if not self.engine or not self.engine.success_results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return ""

        try:
            # 获取结果数据
            stats = self.engine._generate_stats()
            result_data = {
                'stats': stats,
                'success_results': self.engine.success_results,
                'timestamp': self.engine.start_time
            }

            # 导出
            from authkiller.utils.reporter import Reporter
            reporter = Reporter()

            if format == 'json':
                filepath = reporter.save_json(result_data, f'results_{stats.get("total_attempts", 0)}.json')
            elif format == 'csv':
                filepath = reporter.save_csv(result_data, f'results_{stats.get("total_attempts", 0)}.csv')
            elif format == 'txt':
                filepath = reporter.save_txt(result_data, f'results_{stats.get("total_attempts", 0)}.txt')
            else:
                filepath = ""

            if filepath:
                messagebox.showinfo("成功", f"结果已导出:\n{filepath}")
                self.logger.info(f"结果导出成功: {filepath}")

            return filepath

        except Exception as e:
            messagebox.showerror("错误", f"导出结果失败:\n{str(e)}")
            self.logger.error(f"导出结果失败: {e}")
            return ""

    def set_language(self, language: str):
        """
        设置语言（使用新的语言管理器）

        Args:
            language: 语言代码 (zh-CN, en-US, ja-JP, etc.)
        """
        # 将下划线格式转换为连字符格式（向后兼容）
        if '_' in language:
            language = language.replace('_', '-')
        
        # 使用语言管理器设置语言
        success = self.language_manager.set_language(language)
        
        if success:
            self.logger.info(f"语言设置: {language}")
            # 更新GUI界面（需要重新加载字符串资源）
            # TODO: 实现GUI界面更新逻辑
        else:
            self.logger.warning(f"不支持的语言: {language}")

    def get_translation(self, key: str, **kwargs) -> str:
        """
        获取翻译文本（使用新的语言管理器）

        Args:
            key: 翻译键
            **kwargs: 格式化参数

        Returns:
            str: 翻译后的文本
        """
        return get_gui_string(key, **kwargs)

    def quit_app(self):
        """
        退出应用
        """
        if self.is_running:
            if messagebox.askyesno("确认退出", "任务正在运行，确定要退出吗？"):
                self.stop_attack()
            else:
                return

        self.logger.info("THINKER GUI 关闭")
        self.root.quit()
        self.root.destroy()


def main():
    """
    GUI 应用入口函数
    """
    app = ThinkerApp()
    app.run()


if __name__ == '__main__':
    main()