"""
AuthKiller - 密码测试工具
仅用于授权安全审计和强度测试

警告：此工具仅用于合法的安全测试，未经授权使用本工具进行密码测试是违法行为。
使用者必须确保：
1. 已获得目标系统的明确授权
2. 测试行为符合相关法律法规
3. 测试结果用于安全加固而非恶意目的

作者和开发者不对任何非法使用行为承担责任。
"""

__version__ = "1.0.0"
__author__ = "IDrameSkyAbus"
__license__ = "MIT"

# 导入核心模块
from authkiller.core.engine import AttackEngine
from authkiller.core.config import ConfigManager
from authkiller.core.attacker import Attacker

# 导出主要类
__all__ = [
    "AttackEngine",
    "ConfigManager",
    "Attacker",
    "__version__",
]