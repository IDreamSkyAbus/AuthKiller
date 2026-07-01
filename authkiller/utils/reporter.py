"""
AuthKiller 报告生成器
支持 JSON、CSV、TXT 格式输出
"""

import json
import csv
import os
from typing import List, Dict, Any
from datetime import datetime


class Reporter:
    """
    报告生成器
    生成多格式的测试报告
    """

    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告生成器

        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = output_dir
        self.results: List[Dict[str, Any]] = []

        # 创建目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def add_result(self, username: str, password: str,
                   success: bool, timestamp: str = None,
                   details: Dict[str, Any] = None):
        """
        添加测试结果

        Args:
            username: 用户名
            password: 密码
            success: 是否成功
            timestamp: 时间戳
            details: 详细信息
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        result = {
            'username': username,
            'password': password,
            'success': success,
            'timestamp': timestamp,
        }

        if details:
            result['details'] = details

        self.results.append(result)

    def get_successful_results(self) -> List[Dict[str, Any]]:
        """
        获取成功的结果

        Returns:
            List: 成功结果列表
        """
        return [r for r in self.results if r['success']]

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            Dict: 统计信息
        """
        total = len(self.results)
        successful = len(self.get_successful_results())
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0

        return {
            'total_attempts': total,
            'successful_attempts': successful,
            'failed_attempts': failed,
            'success_rate': f"{success_rate:.2f}%",
            'start_time': self.results[0]['timestamp'] if self.results else None,
            'end_time': self.results[-1]['timestamp'] if self.results else None,
        }

    def export_json(self, filename: str = None) -> str:
        """
        导出为 JSON 格式

        Args:
            filename: 文件名（可选）

        Returns:
            str: 文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)

        report_data = {
            'statistics': self.get_statistics(),
            'results': self.results,
            'successful_credentials': self.get_successful_results()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return filepath

    def export_csv(self, filename: str = None) -> str:
        """
        导出为 CSV 格式

        Args:
            filename: 文件名（可选）

        Returns:
            str: 文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # 写入表头
            writer.writerow(['用户名', '密码', '状态', '时间', '详细信息'])

            # 写入数据
            for result in self.results:
                status = '成功' if result['success'] else '失败'
                details = json.dumps(result.get('details', {}))
                writer.writerow([
                    result['username'],
                    result['password'],
                    status,
                    result['timestamp'],
                    details
                ])

        return filepath

    def export_txt(self, filename: str = None) -> str:
        """
        导出为 TXT 格式

        Args:
            filename: 文件名（可选）

        Returns:
            str: 文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.txt"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # 写入统计信息
            stats = self.get_statistics()
            f.write("=" * 50 + "\n")
            f.write("AuthKiller 测试报告\n")
            f.write("=" * 50 + "\n\n")

            f.write("统计信息:\n")
            f.write(f"  总尝试次数: {stats['total_attempts']}\n")
            f.write(f"  成功次数: {stats['successful_attempts']}\n")
            f.write(f"  失败次数: {stats['failed_attempts']}\n")
            f.write(f"  成功率: {stats['success_rate']}\n")
            f.write(f"  开始时间: {stats['start_time']}\n")
            f.write(f"  结束时间: {stats['end_time']}\n\n")

            # 写入成功结果
            f.write("=" * 50 + "\n")
            f.write("成功凭证:\n")
            f.write("=" * 50 + "\n\n")

            for result in self.get_successful_results():
                f.write(f"用户名: {result['username']}\n")
                f.write(f"密码: {result['password']}\n")
                f.write(f"时间: {result['timestamp']}\n")
                if 'details' in result:
                    f.write(f"详细信息: {json.dumps(result['details'])}\n")
                f.write("\n")

        return filepath

    def export_all(self) -> Dict[str, str]:
        """
        导出所有格式

        Returns:
            Dict: 文件路径字典
        """
        return {
            'json': self.export_json(),
            'csv': self.export_csv(),
            'txt': self.export_txt()
        }

    def clear_results(self):
        """
        清空结果列表
        """
        self.results.clear()

    async def save_json(self, data: Dict[str, Any], filename: str) -> str:
        """
        异步保存 JSON 格式报告（用于 engine）

        Args:
            data: 数据字典
            filename: 文件名（可以是完整路径）

        Returns:
            str: 文件路径
        """
        filepath = filename if os.path.isabs(filename) else os.path.join(self.output_dir, filename)

        # 确保目录存在
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def save_csv(self, data: Dict[str, Any], filename: str) -> str:
        """
        保存 CSV 格式报告（用于 CLI）

        Args:
            data: 数据字典
            filename: 文件名（可以是完整路径）

        Returns:
            str: 文件路径
        """
        filepath = filename if os.path.isabs(filename) else os.path.join(self.output_dir, filename)

        # 确保目录存在
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

        # 提取结果列表
        results = data.get('success_results', [])

        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['用户名', '密码', '状态', '时间'])

            for result in results:
                writer.writerow([
                    result.get('username', ''),
                    result.get('password', ''),
                    '成功',
                    result.get('timestamp', '')
                ])

        return filepath

    def save_txt(self, data: Dict[str, Any], filename: str) -> str:
        """
        保存 TXT 格式报告（用于 CLI）

        Args:
            data: 数据字典
            filename: 文件名（可以是完整路径）

        Returns:
            str: 文件路径
        """
        filepath = filename if os.path.isabs(filename) else os.path.join(self.output_dir, filename)

        # 确保目录存在
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

        stats = data.get('stats', {})
        results = data.get('success_results', [])

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("AuthKiller 测试报告\n")
            f.write("=" * 60 + "\n\n")

            f.write("统计信息:\n")
            f.write(f"  总尝试次数: {stats.get('total_attempts', 0)}\n")
            f.write(f"  成功次数: {stats.get('success_count', 0)}\n")
            f.write(f"  失败次数: {stats.get('failed_count', 0)}\n")
            f.write(f"  成功率: {stats.get('success_rate', '0.00%')}\n")
            f.write(f"  耗时: {stats.get('elapsed_time', '0.00s')}\n\n")

            f.write("=" * 60 + "\n")
            f.write("成功凭证:\n")
            f.write("=" * 60 + "\n\n")

            for result in results:
                f.write(f"用户名: {result.get('username', '')}\n")
                f.write(f"密码: {result.get('password', '')}\n\n")

        return filepath