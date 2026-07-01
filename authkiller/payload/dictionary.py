"""
AuthKiller 字典管理
使用生成器逐行读取大文件，避免内存溢出
"""

from typing import Generator, List, Set, Optional
import os


class DictionaryManager:
    """
    字典管理类
    支持逐行读取大字典文件，内存友好
    """

    def __init__(self, users_file: str, passwords_file: str):
        """
        初始化字典管理器

        Args:
            users_file: 用户名字典文件路径
            passwords_file: 密码字典文件路径
        """
        self.users_file = users_file
        self.passwords_file = passwords_file

        # 验证文件是否存在
        if not os.path.exists(users_file):
            raise FileNotFoundError(f"用户名字典文件不存在: {users_file}")
        if not os.path.exists(passwords_file):
            raise FileNotFoundError(f"密码字典文件不存在: {passwords_file}")

        # 预处理：统计字典大小和去重
        self.users_count = self._count_lines(users_file)
        self.passwords_count = self._count_lines(passwords_file)

        # 去重后的集合（用于跳过已测试的组合）
        self.tested_combinations: Set[str] = set()

    def load_users(self) -> Generator[str, None, None]:
        """
        逐行加载用户名字典
        使用生成器避免内存溢出

        Returns:
            Generator: 用户名生成器
        """
        with open(self.users_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                username = line.strip()
                if username:  # 跳过空行
                    yield username

    def load_passwords(self) -> Generator[str, None, None]:
        """
        逐行加载密码字典
        使用生成器避免内存溢出

        Returns:
            Generator: 密码生成器
        """
        with open(self.passwords_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                password = line.strip()
                if password:  # 跳过空行
                    yield password

    def generate_combinations(self, mode: str = 'normal') -> Generator[tuple, None, None]:
        """
        生成用户名/密码组合

        Args:
            mode: 组合模式
                - 'normal': 单用户名 × 单密码（所有组合）
                - 'single_user': 单用户名 × 多密码（一个用户尝试所有密码）
                - 'single_password': 单密码 × 多用户名（密码喷洒）

        Returns:
            Generator: (username, password) 组合生成器
        """
        if mode == 'normal':
            # 所有组合：每个用户名尝试所有密码
            for username in self.load_users():
                for password in self.load_passwords():
                    combination_key = f"{username}:{password}"
                    # 跳过已测试的组合
                    if combination_key not in self.tested_combinations:
                        yield (username, password)

        elif mode == 'single_user':
            # 单用户多密码模式：指定用户尝试所有密码
            # 这种模式需要在调用时指定用户名
            pass

        elif mode == 'single_password':
            # 密码喷洒模式：单一密码尝试多个用户名
            # 这种模式需要在调用时指定密码
            pass

    def generate_single_user(self, username: str) -> Generator[str, None, None]:
        """
        为指定用户名生成所有密码

        Args:
            username: 指定的用户名

        Returns:
            Generator: 密码生成器
        """
        for password in self.load_passwords():
            combination_key = f"{username}:{password}"
            if combination_key not in self.tested_combinations:
                yield password

    def generate_single_password(self, password: str) -> Generator[str, None, None]:
        """
        为指定密码生成所有用户名（密码喷洒）

        Args:
            password: 指定的密码

        Returns:
            Generator: 用户名生成器
        """
        for username in self.load_users():
            combination_key = f"{username}:{password}"
            if combination_key not in self.tested_combinations:
                yield username

    def mark_combination_tested(self, username: str, password: str):
        """
        标记组合已测试

        Args:
            username: 用户名
            password: 密码
        """
        combination_key = f"{username}:{password}"
        self.tested_combinations.add(combination_key)

    def is_combination_tested(self, username: str, password: str) -> bool:
        """
        检查组合是否已测试

        Args:
            username: 用户名
            password: 密码

        Returns:
            bool: True 表示已测试
        """
        combination_key = f"{username}:{password}"
        return combination_key in self.tested_combinations

    def get_total_combinations(self, mode: str = 'normal') -> int:
        """
        获取总组合数

        Args:
            mode: 组合模式

        Returns:
            int: 总组合数
        """
        if mode == 'normal':
            return self.users_count * self.passwords_count
        elif mode == 'single_user':
            return self.passwords_count
        elif mode == 'single_password':
            return self.users_count
        return 0

    def get_remaining_combinations(self) -> int:
        """
        获取剩余未测试的组合数

        Returns:
            int: 剩余组合数
        """
        total = self.get_total_combinations()
        tested = len(self.tested_combinations)
        return total - tested

    def _count_lines(self, filepath: str) -> int:
        """
        统计文件行数（跳过空行）

        Args:
            filepath: 文件路径

        Returns:
            int: 有效行数
        """
        count = 0
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip():  # 跳过空行
                    count += 1
        return count

    def load_users_list(self) -> List[str]:
        """
        加载用户名列表（一次性加载到内存）
        仅适用于小字典文件

        Returns:
            List: 用户名列表
        """
        users = []
        with open(self.users_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                username = line.strip()
                if username:
                    users.append(username)
        return users

    def load_passwords_list(self) -> List[str]:
        """
        加载密码列表（一次性加载到内存）
        仅适用于小字典文件

        Returns:
            List: 密码列表
        """
        passwords = []
        with open(self.passwords_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                password = line.strip()
                if password:
                    passwords.append(password)
        return passwords

    def clear_tested_combinations(self):
        """
        清空已测试组合集合
        """
        self.tested_combinations.clear()

    def restore_tested_combinations(self, combinations: Set[str]):
        """
        恢复已测试组合集合（用于断点续传）

        Args:
            combinations: 已测试组合集合
        """
        self.tested_combinations = combinations.copy()


class MultiDictionaryManager:
    """
    多字典管理器
    支持多个用户名/密码字典文件组合
    """

    def __init__(self, users_files: List[str], passwords_files: List[str]):
        """
        初始化多字典管理器

        Args:
            users_files: 用户名字典文件列表
            passwords_files: 密码字典文件列表
        """
        self.users_files = users_files
        self.passwords_files = passwords_files

        # 验证所有文件
        for file in users_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"用户名字典文件不存在: {file}")
        for file in passwords_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"密码字典文件不存在: {file}")

        self.tested_combinations: Set[str] = set()

    def load_all_users(self) -> Generator[str, None, None]:
        """
        逐行加载所有用户名字典

        Returns:
            Generator: 用户名生成器
        """
        for file in self.users_files:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    username = line.strip()
                    if username:
                        yield username

    def load_all_passwords(self) -> Generator[str, None, None]:
        """
        逐行加载所有密码字典

        Returns:
            Generator: 密码生成器
        """
        for file in self.passwords_files:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    password = line.strip()
                    if password:
                        yield password

    def generate_combinations(self) -> Generator[tuple, None, None]:
        """
        生成所有字典的组合

        Returns:
            Generator: (username, password) 组合生成器
        """
        for username in self.load_all_users():
            for password in self.load_all_passwords():
                combination_key = f"{username}:{password}"
                if combination_key not in self.tested_combinations:
                    yield (username, password)

    def mark_combination_tested(self, username: str, password: str):
        """
        标记组合已测试

        Args:
            username: 用户名
            password: 密码
        """
        combination_key = f"{username}:{password}"
        self.tested_combinations.add(combination_key)