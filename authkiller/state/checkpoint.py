"""
AuthKiller 断点续传管理
定期保存进度，支持意外中断后恢复
"""

import json
import os
from typing import Dict, Any, Set
from datetime import datetime
import aiofiles


class CheckpointManager:
    """
    断点续传管理器
    定期保存测试进度到JSON文件
    """

    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """
        初始化断点管理器

        Args:
            checkpoint_dir: 断点文件存储目录
        """
        self.checkpoint_dir = checkpoint_dir
        self.current_checkpoint_file = None

        # 创建目录
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

    def generate_checkpoint_filename(self) -> str:
        """
        生成断点文件名

        Returns:
            str: 断点文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"checkpoint_{timestamp}.json"
        filepath = os.path.join(self.checkpoint_dir, filename)
        return filepath

    async def save_checkpoint(self, data: Dict[str, Any]) -> str:
        """
        保存断点数据

        Args:
            data: 断点数据字典，包含：
                - tested_combinations: 已测试的用户名/密码组合集合
                - current_position: 当前位置（可选）
                - timestamp: 时间戳
                - config: 当前配置（可选）
                - results: 已发现的成功结果（可选）

        Returns:
            str: 断点文件路径
        """
        if self.current_checkpoint_file is None:
            self.current_checkpoint_file = self.generate_checkpoint_filename()

        # 添加元数据
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'checkpoint_file': self.current_checkpoint_file,
            **data
        }

        # 转换 set 为 list（JSON 不支持 set）
        if 'tested_combinations' in checkpoint_data:
            checkpoint_data['tested_combinations'] = list(checkpoint_data['tested_combinations'])

        # 异步写入文件（原子写入）
        async with aiofiles.open(self.current_checkpoint_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(checkpoint_data, indent=2, ensure_ascii=False))

        return self.current_checkpoint_file

    async def load_checkpoint(self, checkpoint_file: str) -> Dict[str, Any]:
        """
        加载断点数据

        Args:
            checkpoint_file: 断点文件路径

        Returns:
            Dict: 断点数据
        """
        if not os.path.exists(checkpoint_file):
            raise FileNotFoundError(f"断点文件不存在: {checkpoint_file}")

        async with aiofiles.open(checkpoint_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)

        # 转换 list 回 set
        if 'tested_combinations' in data:
            data['tested_combinations'] = set(data['tested_combinations'])

        return data

    def get_latest_checkpoint(self) -> str:
        """
        获取最新的断点文件

        Returns:
            str: 最新断点文件路径，如果没有返回 None
        """
        checkpoints = []

        for filename in os.listdir(self.checkpoint_dir):
            if filename.startswith('checkpoint_') and filename.endswith('.json'):
                filepath = os.path.join(self.checkpoint_dir, filename)
                checkpoints.append((filepath, os.path.getmtime(filepath)))

        if not checkpoints:
            return None

        # 按修改时间排序，返回最新的
        checkpoints.sort(key=lambda x: x[1], reverse=True)
        return checkpoints[0][0]

    def list_checkpoints(self) -> list:
        """
        列出所有断点文件

        Returns:
            list: 断点文件列表
        """
        checkpoints = []

        for filename in os.listdir(self.checkpoint_dir):
            if filename.startswith('checkpoint_') and filename.endswith('.json'):
                filepath = os.path.join(self.checkpoint_dir, filename)
                timestamp = os.path.getmtime(filepath)
                checkpoints.append({
                    'file': filepath,
                    'filename': filename,
                    'timestamp': timestamp,
                    'time_str': datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                })

        # 按时间排序
        checkpoints.sort(key=lambda x: x['timestamp'], reverse=True)

        return checkpoints

    def delete_checkpoint(self, checkpoint_file: str):
        """
        删除断点文件

        Args:
            checkpoint_file: 断点文件路径
        """
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)

    def clear_current_checkpoint(self):
        """
        清空当前断点文件
        """
        self.current_checkpoint_file = None

    @staticmethod
    def create_checkpoint_data(tested_combinations: Set[str],
                               current_position: int = 0,
                               config: Dict = None,
                               results: list = None) -> Dict[str, Any]:
        """
        创建断点数据结构

        Args:
            tested_combinations: 已测试组合集合
            current_position: 当前位置
            config: 配置字典
            results: 结果列表

        Returns:
            Dict: 断点数据
        """
        data = {
            'tested_combinations': tested_combinations,
            'current_position': current_position
        }

        if config:
            data['config'] = config

        if results:
            data['results'] = results

        return data