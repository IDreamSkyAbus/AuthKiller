"""
AuthKiller 规则引擎
支持密码变异、动态生成和规则链式组合
"""

from typing import Generator, List, Callable, Dict, Any
import re
from datetime import datetime


class RuleEngine:
    """
    规则引擎
    支持密码变异和动态生成
    """

    def __init__(self):
        """
        初始化规则引擎
        """
        self.rules: Dict[str, Callable] = {}
        self._register_default_rules()

    def _register_default_rules(self):
        """
        注册默认规则
        """
        # 大小写规则
        self.register_rule('uppercase', self.rule_uppercase)
        self.register_rule('lowercase', self.rule_lowercase)
        self.register_rule('capitalize', self.rule_capitalize)

        # 数字规则
        self.register_rule('append_numbers', self.rule_append_numbers)
        self.register_rule('prepend_numbers', self.rule_prepend_numbers)

        # 特殊字符规则
        self.register_rule('append_special', self.rule_append_special)

        # 变异规则
        self.register_rule('leet', self.rule_leet)
        self.register_rule('reverse', self.rule_reverse)

        # 动态生成规则
        self.register_rule('user_based', self.rule_user_based)
        self.register_rule('date_based', self.rule_date_based)

    def register_rule(self, name: str, rule_func: Callable):
        """
        注册自定义规则

        Args:
            name: 规则名称
            rule_func: 规则函数（接收密码字符串，返回变异后的密码列表）
        """
        self.rules[name] = rule_func

    def apply_rule(self, password: str, rule_name: str) -> List[str]:
        """
        应用单个规则

        Args:
            password: 原始密码
            rule_name: 规则名称

        Returns:
            List: 变异后的密码列表
        """
        if rule_name not in self.rules:
            return [password]

        rule_func = self.rules[rule_name]
        return rule_func(password)

    def apply_rules_chain(self, password: str, rules: List[str]) -> Generator[str, None, None]:
        """
        应用规则链（链式组合）

        Args:
            password: 原始密码
            rules: 规则列表

        Returns:
            Generator: 变异密码生成器
        """
        if not rules:
            yield password
            return

        # 第一个规则的结果
        first_rule = rules[0]
        first_results = self.apply_rule(password, first_rule)

        # 如果只有一个规则，直接返回结果
        if len(rules) == 1:
            for result in first_results:
                yield result
            return

        # 递归应用后续规则
        for first_result in first_results:
            for final_result in self.apply_rules_chain(first_result, rules[1:]):
                yield final_result

    def apply_multiple_rules(self, password: str, rules: List[str]) -> List[str]:
        """
        应用多个规则（非链式，分别应用每个规则）

        Args:
            password: 原始密码
            rules: 规则列表

        Returns:
            List: 变异密码列表
        """
        results = [password]  # 包含原始密码

        for rule in rules:
            rule_results = self.apply_rule(password, rule)
            results.extend(rule_results)

        # 去重
        return list(set(results))

    # 默认规则实现

    def rule_uppercase(self, password: str) -> List[str]:
        """
        大写转换

        Args:
            password: 密码

        Returns:
            List: [PASSWORD]
        """
        return [password.upper()]

    def rule_lowercase(self, password: str) -> List[str]:
        """
        小写转换

        Args:
            password: 密码

        Returns:
            List: [password]
        """
        return [password.lower()]

    def rule_capitalize(self, password: str) -> List[str]:
        """
        首字母大写

        Args:
            password: 密码

        Returns:
            List: [Password]
        """
        return [password.capitalize()]

    def rule_append_numbers(self, password: str) -> List[str]:
        """
        添加数字后缀

        Args:
            password: 密码

        Returns:
            List: [password1, password12, password123, ...]
        """
        results = []
        # 添加常见数字后缀
        common_numbers = ['1', '12', '123', '1234', '12345', '123456',
                          '!', '!1', '@', '#', '$', '%',
                          '01', '02', '03', '04', '05', '06', '07', '08', '09', '00',
                          '11', '22', '33', '44', '55', '66', '77', '88', '99',
                          '2024', '2025', '2026']

        for num in common_numbers:
            results.append(password + num)

        return results

    def rule_prepend_numbers(self, password: str) -> List[str]:
        """
        添加数字前缀

        Args:
            password: 密码

        Returns:
            List: [1password, 12password, ...]
        """
        results = []
        common_numbers = ['1', '12', '123', '1234', '12345', '!1', '@', '#']

        for num in common_numbers:
            results.append(num + password)

        return results

    def rule_append_special(self, password: str) -> List[str]:
        """
        添加特殊字符后缀

        Args:
            password: 密码

        Returns:
            List: [password!, password@, ...]
        """
        results = []
        special_chars = ['!', '@', '#', '$', '%', '*', '?', '_', '-']

        for char in special_chars:
            results.append(password + char)

        return results

    def rule_leet(self, password: str) -> List[str]:
        """
        Leet 字符替换
        a -> 4, e -> 3, i -> 1, o -> 0, s -> 5

        Args:
            password: 密码

        Returns:
            List: 变异密码列表
        """
        results = []
        leet_map = {
            'a': '4',
            'e': '3',
            'i': '1',
            'o': '0',
            's': '5',
            'A': '4',
            'E': '3',
            'I': '1',
            'O': '0',
            'S': '5'
        }

        # 完全替换
        leet_password = password
        for char, replacement in leet_map.items():
            leet_password = leet_password.replace(char, replacement)

        if leet_password != password:
            results.append(leet_password)

        return results

    def rule_reverse(self, password: str) -> List[str]:
        """
        反转密码

        Args:
            password: 密码

        Returns:
            List: [drowssap]
        """
        return [password[::-1]]

    def rule_user_based(self, password: str, username: str = None) -> List[str]:
        """
        用户名组合规则

        Args:
            password: 密码
            username: 用户名（可选）

        Returns:
            List: 用户名组合密码列表
        """
        results = []

        if username:
            # 用户名 + 密码
            results.append(username + password)
            results.append(password + username)

            # 用户名大写
            results.append(username.upper() + password)
            results.append(password + username.upper())

            # 用户名小写
            results.append(username.lower() + password)
            results.append(password + username.lower())

        return results

    def rule_date_based(self, password: str, username: str = None) -> List[str]:
        """
        日期组合规则

        Args:
            password: 密码
            username: 用户名（可选）

        Returns:
            List: 日期组合密码列表
        """
        results = []

        # 当前年份
        current_year = datetime.now().year
        current_year_str = str(current_year)

        # 密码 + 年份
        results.append(password + current_year_str)
        results.append(current_year_str + password)

        # 常见年份
        common_years = ['2024', '2025', '2026', '2020', '2019', '2018', '2017']
        for year in common_years:
            results.append(password + year)
            results.append(year + password)

        # 月份和日期
        common_dates = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        for date in common_dates:
            results.append(password + date)
            results.append(date + password)

        if username:
            # 用户名 + 年份
            results.append(username + current_year_str)
            results.append(current_year_str + username)

        return results

    def get_available_rules(self) -> List[str]:
        """
        获取所有可用规则

        Returns:
            List: 规则名称列表
        """
        return list(self.rules.keys())


class PasswordMutator:
    """
    密码变异器
    支持批量变异密码字典
    """

    def __init__(self, rule_engine: RuleEngine = None):
        """
        初始化密码变异器

        Args:
            rule_engine: 规则引擎实例
        """
        self.rule_engine = rule_engine or RuleEngine()

    def mutate_password(self, password: str, rules: List[str], chain: bool = False) -> List[str]:
        """
        变异密码

        Args:
            password: 原始密码
            rules: 规则列表
            chain: 是否链式组合

        Returns:
            List: 变异密码列表
        """
        if chain:
            # 链式组合
            return list(self.rule_engine.apply_rules_chain(password, rules))
        else:
            # 分别应用
            return self.rule_engine.apply_multiple_rules(password, rules)

    def mutate_dictionary(self, passwords: Generator[str, None, None],
                         rules: List[str], chain: bool = False) -> Generator[str, None, None]:
        """
        变异整个字典

        Args:
            passwords: 原始密码生成器
            rules: 规则列表
            chain: 是否链式组合

        Returns:
            Generator: 变异密码生成器
        """
        seen = set()  # 去重

        for password in passwords:
            # 包含原始密码
            if password not in seen:
                seen.add(password)
                yield password

            # 变异密码
            mutated = self.mutate_password(password, rules, chain)
            for mut_password in mutated:
                if mut_password not in seen:
                    seen.add(mut_password)
                    yield mut_password

    def generate_user_specific_passwords(self, username: str,
                                        passwords: Generator[str, None, None],
                                        rules: List[str] = None) -> Generator[str, None, None]:
        """
        生成用户特定密码

        Args:
            username: 用户名
            passwords: 原始密码生成器
            rules: 规则列表

        Returns:
            Generator: 用户特定密码生成器
        """
        seen = set()

        # 用户名基础密码
        user_passwords = [
            username,
            username.lower(),
            username.upper(),
            username.capitalize(),
            username + '123',
            username + '1234',
            username + '12345',
            username + '!',
            username + '@',
            username + '#',
        ]

        for pwd in user_passwords:
            if pwd not in seen:
                seen.add(pwd)
                yield pwd

        # 原始密码和变异密码
        for password in passwords:
            if password not in seen:
                seen.add(password)
                yield password

            if rules:
                mutated = self.mutate_password(password, rules, False)
                for mut_password in mutated:
                    if mut_password not in seen:
                        seen.add(mut_password)
                        yield mut_password