"""
AuthKiller 主引擎
协调所有模块，管理并发任务调度和结果收集
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime

from authkiller.core.config import ConfigManager
from authkiller.core.attacker import Attacker
from authkiller.payload.dictionary import DictionaryManager
from authkiller.state.checkpoint import CheckpointManager
from authkiller.utils.logger import Logger
from authkiller.utils.reporter import Reporter


class AttackEngine:
    """
    主引擎
    负责协调各模块，管理并发任务和结果收集
    """

    def __init__(self, config_manager: ConfigManager):
        """
        初始化引擎

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.config = config_manager.config

        # 初始化各个模块
        self.logger = Logger.get_logger('engine')
        self.attacker: Optional[Attacker] = None
        self.dictionary_manager: Optional[DictionaryManager] = None
        self.checkpoint_manager: Optional[CheckpointManager] = None
        self.reporter: Optional[Reporter] = None

        # 任务控制
        self.semaphore: Optional[asyncio.Semaphore] = None
        self.is_running = False
        self.is_paused = False
        self.stop_flag = False

        # 结果收集
        self.success_results: List[Dict[str, Any]] = []
        self.failed_results: List[Dict[str, Any]] = []
        self.total_attempts = 0
        self.success_count = 0

        # 断点续传
        self.tested_combinations: Set[str] = set()
        self.checkpoint_interval = 100

        # 统计信息
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # 初始化各组件
        self._init_components()

    def _init_components(self):
        """
        初始化所有组件
        """
        # 初始化字典管理器
        payload_config = self.config.get('payload', {})
        users_file = payload_config.get('users_file')
        passwords_file = payload_config.get('passwords_file')

        if users_file and passwords_file:
            self.dictionary_manager = DictionaryManager(users_file, passwords_file)

        # 初始化攻击执行器
        protocol_config = self.config_manager.get_protocol_config()
        defense_config = self.config.get('defense', {})
        protocol_config.update(defense_config)
        protocol_config['protocol'] = self.config.get('detection', {}).get('protocol', 'http_form')
        self.attacker = Attacker(protocol_config)

        # 初始化断点管理器
        output_config = self.config.get('output', {})
        checkpoint_dir = output_config.get('checkpoint_dir', 'checkpoints')
        self.checkpoint_manager = CheckpointManager(checkpoint_dir)

        # 初始化报告生成器
        self.reporter = Reporter()

        # 设置并发控制
        performance_config = self.config.get('performance', {})
        concurrency = performance_config.get('concurrency', 10)
        self.semaphore = asyncio.Semaphore(concurrency)

        # 设置断点保存间隔
        self.checkpoint_interval = performance_config.get('checkpoint_interval', 100)

    async def initialize(self):
        """
        初始化引擎（异步）
        """
        # 初始化协议会话
        if self.attacker:
            await self.attacker.init_session()

        self.logger.info("引擎初始化完成")

    async def cleanup(self):
        """
        清理资源（异步）
        """
        # 关闭协议会话
        if self.attacker:
            await self.attacker.close_session()

        self.logger.info("引擎资源清理完成")

    async def run(self, checkpoint_file: Optional[str] = None) -> Dict[str, Any]:
        """
        运行攻击任务

        Args:
            checkpoint_file: 断点文件路径（可选，用于恢复）

        Returns:
            执行结果统计字典
        """
        # 检查是否恢复断点
        if checkpoint_file:
            await self._load_checkpoint(checkpoint_file)

        # 验证配置
        is_valid, error_message = self.config_manager.validate()
        if not is_valid:
            raise ValueError(f"配置验证失败: {error_message}")

        self.logger.info(f"开始攻击任务 - 目标: {self.config.get('target', {}).get('url')}")

        # 开始计时
        self.start_time = time.time()
        self.is_running = True
        self.stop_flag = False

        try:
            # 执行任务
            await self._execute_attack()

        except KeyboardInterrupt:
            self.logger.warning("用户中断任务")
            await self._save_checkpoint()

        except Exception as e:
            self.logger.error(f"任务执行异常: {e}")
            await self._save_checkpoint()
            raise e

        finally:
            # 结束计时
            self.end_time = time.time()
            self.is_running = False

            # 清理资源
            await self.cleanup()

            # 生成报告
            stats = self._generate_stats()
            await self._save_results(stats)

            self.logger.info("攻击任务完成")

        return self._generate_stats()

    async def _execute_attack(self):
        """
        执行攻击任务（核心逻辑）
        """
        # 生成用户名/密码组合
        payload_config = self.config.get('payload', {})
        mode = payload_config.get('mode', 'normal')

        # 创建任务队列
        tasks = []

        # 根据模式生成组合
        if mode == 'normal':
            # 普通模式：每个用户名尝试所有密码
            for username, password in self.dictionary_manager.generate_combinations(mode):
                # 检查是否已测试
                if self.dictionary_manager.is_combination_tested(username, password):
                    continue

                # 创建任务
                task = self._create_attack_task(username, password)
                tasks.append(task)

                # 控制并发：当任务数达到并发限制时，等待部分任务完成
                if len(tasks) >= self.semaphore._value * 2:
                    await self._process_tasks_batch(tasks)

        elif mode == 'single_user':
            # 单用户模式：指定用户名尝试所有密码
            username = payload_config.get('single_user_username', 'admin')
            for password in self.dictionary_manager.generate_single_user(username):
                task = self._create_attack_task(username, password)
                tasks.append(task)

                if len(tasks) >= self.semaphore._value * 2:
                    await self._process_tasks_batch(tasks)

        elif mode == 'single_password':
            # 密码喷洒模式：单一密码尝试多个用户名
            password = payload_config.get('single_password_value', 'admin')
            for username in self.dictionary_manager.generate_single_password(password):
                task = self._create_attack_task(username, password)
                tasks.append(task)

                if len(tasks) >= self.semaphore._value * 2:
                    await self._process_tasks_batch(tasks)

        # 处理剩余任务
        if tasks:
            await self._process_tasks_batch(tasks)

    async def _create_attack_task(self, username: str, password: str) -> asyncio.Task:
        """
        创建单个攻击任务

        Args:
            username: 用户名
            password: 密码

        Returns:
            asyncio.Task 对象
        """
        return asyncio.create_task(self._attack_with_semaphore(username, password))

    async def _attack_with_semaphore(self, username: str, password: str):
        """
        带并发控制的攻击任务

        Args:
            username: 用户名
            password: 密码
        """
        async with self.semaphore:
            if self.stop_flag:
                return

            try:
                # 执行认证测试
                success, result = await self.attacker.test_credential(username, password)

                # 收集结果
                self._collect_result(success, result)

                # 标记已测试
                self.dictionary_manager.mark_combination_tested(username, password)

                # 定期保存断点
                if self.total_attempts % self.checkpoint_interval == 0:
                    await self._save_checkpoint()

            except Exception as e:
                self.logger.error(f"任务执行异常: {username}:{password} - {e}")

    async def _process_tasks_batch(self, tasks: List[asyncio.Task]):
        """
        处理一批任务

        Args:
            tasks: 任务列表
        """
        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)

        # 清空任务列表
        tasks.clear()

    def _collect_result(self, success: bool, result: Dict[str, Any]):
        """
        收集结果

        Args:
            success: 是否成功
            result: 结果详情
        """
        self.total_attempts += 1

        if success:
            self.success_count += 1
            self.success_results.append(result)
            self.logger.success(f"发现有效凭证: {result['username']}:{result['password']}")
        else:
            # 只记录失败的前100个（避免内存占用过大）
            if len(self.failed_results) < 100:
                self.failed_results.append(result)

        # 输出进度信息
        if self.total_attempts % 50 == 0:
            remaining = self.dictionary_manager.get_remaining_combinations()
            self.logger.info(f"进度: {self.total_attempts} | 成功: {self.success_count} | 剩余: {remaining}")

    async def _save_checkpoint(self):
        """
        保存断点
        """
        checkpoint_data = CheckpointManager.create_checkpoint_data(
            tested_combinations=self.dictionary_manager.tested_combinations,
            current_position=self.total_attempts,
            config=self.config,
            results=self.success_results
        )

        checkpoint_file = await self.checkpoint_manager.save_checkpoint(checkpoint_data)
        self.logger.info(f"断点已保存: {checkpoint_file}")

    async def _load_checkpoint(self, checkpoint_file: str):
        """
        加载断点

        Args:
            checkpoint_file: 断点文件路径
        """
        try:
            checkpoint_data = await self.checkpoint_manager.load_checkpoint(checkpoint_file)

            # 恢复已测试组合
            tested_combinations = checkpoint_data.get('tested_combinations', set())
            self.dictionary_manager.restore_tested_combinations(tested_combinations)

            # 恢复成功结果
            self.success_results = checkpoint_data.get('results', [])

            self.logger.info(f"断点已恢复: 已测试 {len(tested_combinations)} 个组合")

        except Exception as e:
            self.logger.error(f"加载断点失败: {e}")
            raise e

    async def _save_results(self, stats: Dict[str, Any]):
        """
        保存结果到文件

        Args:
            stats: 统计信息字典
        """
        output_config = self.config.get('output', {})
        result_file = output_config.get('result_file', 'results.json')

        # 保存完整结果
        result_data = {
            'stats': stats,
            'success_results': self.success_results,
            'timestamp': datetime.now().isoformat()
        }

        await self.reporter.save_json(result_data, result_file)
        self.logger.info(f"结果已保存: {result_file}")

    def _generate_stats(self) -> Dict[str, Any]:
        """
        生成统计信息

        Returns:
            统计信息字典
        """
        elapsed_time = 0
        if self.start_time and self.end_time:
            elapsed_time = self.end_time - self.start_time

        total_combinations = self.dictionary_manager.get_total_combinations()
        remaining_combinations = self.dictionary_manager.get_remaining_combinations()

        stats = {
            'total_attempts': self.total_attempts,
            'success_count': self.success_count,
            'failed_count': self.total_attempts - self.success_count,
            'total_combinations': total_combinations,
            'tested_combinations': len(self.dictionary_manager.tested_combinations),
            'remaining_combinations': remaining_combinations,
            'success_rate': f"{(self.success_count / self.total_attempts * 100) if self.total_attempts > 0 else 0:.2f}%",
            'elapsed_time': f"{elapsed_time:.2f}s",
            'average_time_per_attempt': f"{(elapsed_time / self.total_attempts) if self.total_attempts > 0 else 0:.2f}s",
            'start_time': datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            'end_time': datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None
        }

        return stats

    def stop(self):
        """
        停止任务
        """
        self.stop_flag = True
        self.logger.info("任务停止信号已发送")

    def pause(self):
        """
        暂停任务
        """
        self.is_paused = True
        self.logger.info("任务已暂停")

    def resume(self):
        """
        恢复任务
        """
        self.is_paused = False
        self.logger.info("任务已恢复")

    def get_progress(self) -> Dict[str, Any]:
        """
        获取当前进度

        Returns:
            进度信息字典
        """
        total = self.dictionary_manager.get_total_combinations()
        tested = len(self.dictionary_manager.tested_combinations)

        return {
            'total': total,
            'tested': tested,
            'remaining': total - tested,
            'success_count': self.success_count,
            'progress_percentage': f"{(tested / total * 100) if total > 0 else 0:.2f}%",
            'is_running': self.is_running
        }

    async def run_single_test(self, username: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        运行单次测试（用于调试或快速验证）

        Args:
            username: 用户名
            password: 密码

        Returns:
            测试结果
        """
        await self.initialize()
        result = await self.attacker.test_credential(username, password)
        await self.cleanup()
        return result

    def __repr__(self) -> str:
        """
        字符串表示

        Returns:
            字符串表示
        """
        status = "运行中" if self.is_running else "停止"
        return f"AttackEngine(status={status}, attempts={self.total_attempts}, success={self.success_count})"