"""
AuthKiller 配置管理
支持 JSON/YAML/INI 配置文件加载、参数验证、配置合并和模板生成
"""

import json
import os
import configparser
import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from enum import Enum
import copy

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigFormat(Enum):
    """配置文件格式枚举"""
    JSON = 'json'
    YAML = 'yaml'
    INI = 'ini'


class RunMode(Enum):
    """运行模式枚举"""
    CLI = 'cli'
    WEB_GUI = 'web_gui'
    THINKER_GUI = 'thinker_gui'
    API_SERVICE = 'api_service'


class ConfigManager:
    """
    配置管理器
    负责加载、验证和管理配置
    """

    # 默认配置
    DEFAULT_CONFIG = {
        'general': {
            'language': 'zh-CN',  # 语言选择：zh-CN, en-US 等
            'mode': 'cli',  # 运行模式：cli, web_gui, thinker_gui, api_service
            'debug': False,
            'quiet': False
        },
        'target': {
            'url': '',
            'method': 'POST',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            'body_template': 'username={user}&password={pass}',
            'content_type': 'urlencoded',
            'cookies': {}
        },
        'payload': {
            'users_file': '',
            'passwords_file': '',
            'rules': [],
            'mode': 'normal'  # normal, single_user, single_password
        },
        'performance': {
            'concurrency': 10,
            'timeout': 10,
            'retry_times': 3,
            'checkpoint_interval': 100
        },
        'detection': {
            'success_status_codes': [200, 302],
            'success_pattern': None,
            'failure_pattern': None,
            'protocol': 'http_form'  # http_form, http_basic
        },
        'defense': {
            'detect_rate_limit': True,
            'auto_throttle': True,
            'throttle_delay': 5,
            'max_rate_limit_retries': 3
        },
        'output': {
            'log_level': 'INFO',
            'log_file': None,
            'result_file': 'results.json',
            'checkpoint_dir': 'checkpoints'
        },
        'api': {  # API 服务模式专用配置
            'host': '0.0.0.0',
            'port': 8080,
            'enable_auth': False,
            'auth_token': '',
            'cors_origins': ['*']
        },
        'web_gui': {  # Web GUI 模式专用配置
            'host': '0.0.0.0',
            'port': 5000,
            'secret_key': '',
            'session_timeout': 3600
        },
        'thinker_gui': {  # THINKER GUI 模式专用配置
            'theme': 'dark',
            'window_size': [1200, 800],
            'auto_save_interval': 300
        }
    }

    # 配置模板
    CONFIG_TEMPLATES = {
        'basic': '基础配置模板 - 适用于快速测试',
        'advanced': '高级配置模板 - 适用于生产环境',
        'stealth': '隐蔽模式模板 - 适用于绕过检测',
        'aggressive': '激进模式模板 - 适用于高强度测试',
        'api': 'API服务模板 - 适用于API服务模式',
        'web_gui': 'Web GUI模板 - 适用于Web界面模式'
    }

    def __init__(self, config_path: Optional[str] = None, config_paths: Optional[List[str]] = None):
        """
        初始化配置管理器

        Args:
            config_path: 单个配置文件路径（可选）
            config_paths: 多个配置文件路径列表，用于合并配置（可选）
        """
        self.config: Dict[str, Any] = {}
        self.config_path = config_path
        self.config_format: Optional[ConfigFormat] = None

        if config_path:
            self.load_config(config_path)

        if config_paths:
            self.load_and_merge_configs(config_paths)

        if not self.config:
            # 使用默认配置
            self.config = self._deep_copy_dict(self.DEFAULT_CONFIG)

    def load_config(self, config_path: str):
        """
        加载配置文件

        Args:
            config_path: 配置文件路径（支持 .json、.yaml/.yml、.ini）

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        # 根据文件扩展名选择加载方式
        ext = Path(config_path).suffix.lower()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if ext in ['.yaml', '.yml']:
                    if not YAML_AVAILABLE:
                        raise ImportError("需要安装 PyYAML 库才能加载 YAML 配置: pip install pyyaml")
                    loaded_config = yaml.safe_load(f)
                    self.config_format = ConfigFormat.YAML
                elif ext == '.ini':
                    loaded_config = self._load_ini_config(f)
                    self.config_format = ConfigFormat.INI
                else:  # 默认为 JSON
                    loaded_config = json.load(f)
                    self.config_format = ConfigFormat.JSON
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            if YAML_AVAILABLE and 'YAMLError' in str(type(e).__name__):
                raise ValueError(f"YAML 配置文件格式错误: {e}")
            else:
                raise ValueError(f"加载配置文件失败: {e}")

        # 合并配置（用户配置覆盖默认配置）
        self.config = self._merge_config(self._deep_copy_dict(self.DEFAULT_CONFIG), loaded_config)
        self.config_path = config_path

    def _load_ini_config(self, file_obj) -> Dict[str, Any]:
        """
        从 INI 文件加载配置

        Args:
            file_obj: 文件对象

        Returns:
            配置字典
        """
        config_parser = configparser.ConfigParser()
        config_parser.read_file(file_obj)

        config_dict = {}

        for section in config_parser.sections():
            config_dict[section] = {}

            for key, value in config_parser.items(section):
                # 尝试解析值类型
                parsed_value = self._parse_ini_value(value)
                config_dict[section][key] = parsed_value

        return config_dict

    def _parse_ini_value(self, value: str) -> Any:
        """
        解析 INI 配置值，尝试转换为适当的类型

        Args:
            value: 字符串值

        Returns:
            解析后的值
        """
        # 尝试解析为布尔值
        if value.lower() in ['true', 'yes', 'on']:
            return True
        if value.lower() in ['false', 'no', 'off']:
            return False

        # 尝试解析为整数
        try:
            return int(value)
        except ValueError:
            pass

        # 尝试解析为浮点数
        try:
            return float(value)
        except ValueError:
            pass

        # 尝试解析为列表（逗号分隔）
        if ',' in value:
            items = [item.strip() for item in value.split(',')]
            # 尝试将列表项转换为整数
            try:
                return [int(item) for item in items]
            except ValueError:
                return items

        # 返回字符串
        return value

    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """
        深度合并配置（用户配置覆盖默认配置）

        Args:
            default: 默认配置
            user: 用户配置

        Returns:
            合并后的配置
        """
        result = default.copy()

        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 递归合并字典
                result[key] = self._merge_config(result[key], value)
            else:
                # 直接覆盖
                result[key] = value

        return result

    def _deep_copy_dict(self, d: Dict) -> Dict:
        """
        深拷贝字典

        Args:
            d: 原始字典

        Returns:
            拷贝后的字典
        """
        import copy
        return copy.deepcopy(d)

    def load_and_merge_configs(self, config_paths: List[str], merge_strategy: str = 'override'):
        """
        加载并合并多个配置文件

        Args:
            config_paths: 配置文件路径列表
            merge_strategy: 合并策略 ('override'-覆盖, 'merge'-合并)

        Returns:
            合并后的配置

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if not config_paths:
            raise ValueError("配置文件路径列表不能为空")

        merged_config = self._deep_copy_dict(self.DEFAULT_CONFIG)

        for config_path in config_paths:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"配置文件不存在: {config_path}")

            # 加载单个配置文件
            ext = Path(config_path).suffix.lower()
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if ext in ['.yaml', '.yml']:
                        if not YAML_AVAILABLE:
                            raise ImportError("需要安装 PyYAML 库才能加载 YAML 配置: pip install pyyaml")
                        loaded_config = yaml.safe_load(f)
                    elif ext == '.ini':
                        loaded_config = self._load_ini_config(f)
                    else:  # 默认为 JSON
                        loaded_config = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"配置文件格式错误 ({config_path}): {e}")
            except Exception as e:
                if YAML_AVAILABLE and 'YAMLError' in str(type(e).__name__):
                    raise ValueError(f"YAML 配置文件格式错误 ({config_path}): {e}")
                else:
                    raise ValueError(f"加载配置文件失败 ({config_path}): {e}")

            # 合并配置
            if merge_strategy == 'override':
                merged_config = self._merge_config(merged_config, loaded_config)
            elif merge_strategy == 'merge':
                merged_config = self._deep_merge_dicts(merged_config, loaded_config)
            else:
                raise ValueError(f"不支持的合并策略: {merge_strategy}")

        self.config = merged_config
        return self.config

    def _deep_merge_dicts(self, dict1: Dict, dict2: Dict) -> Dict:
        """
        深度合并两个字典（dict2 合并到 dict1）
        递归合并所有嵌套字典

        Args:
            dict1: 第一个字典
            dict2: 第二个字典

        Returns:
            合并后的字典
        """
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge_dicts(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    # 列表合并：去重合并
                    result[key] = list(set(result[key] + value))
                else:
                    result[key] = value
            else:
                result[key] = value

        return result

    def validate(self) -> Tuple[bool, List[str]]:
        """
        验证配置是否有效

        Returns:
            tuple: (is_valid, errors_list) - 验证结果和错误消息列表
        """
        errors = []
        warnings = []

        # 验证通用配置
        general = self.config.get('general', {})
        language = general.get('language', 'zh-CN')
        supported_languages = ['zh-CN', 'en-US', 'ja-JP', 'ko-KR']
        if language not in supported_languages:
            warnings.append(f"不支持的语言: {language}，将使用默认语言 zh-CN")

        mode = general.get('mode', 'cli')
        supported_modes = ['cli', 'web_gui', 'thinker_gui', 'api_service']
        if mode not in supported_modes:
            errors.append(f"不支持的运行模式: {mode}，支持的模式: {', '.join(supported_modes)}")

        # 验证目标配置
        target = self.config.get('target', {})
        url = target.get('url', '')
        if not url:
            errors.append("缺少目标 URL (target.url)")
        else:
            # 验证 URL 格式
            url_pattern = re.compile(
                r'^https?://'  # http:// 或 https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP 地址
                r'(?::\d+)?'  # 可选端口
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not url_pattern.match(url):
                warnings.append(f"URL 格式可能无效: {url}")

        # 验证 HTTP 方法
        method = target.get('method', 'POST')
        supported_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if method.upper() not in supported_methods:
            errors.append(f"不支持的 HTTP 方法: {method}")

        # 验证字典文件
        payload = self.config.get('payload', {})
        users_file = payload.get('users_file')
        passwords_file = payload.get('passwords_file')

        if not users_file:
            errors.append("缺少用户名字典文件 (payload.users_file)")
        elif not os.path.exists(users_file):
            warnings.append(f"用户名字典文件不存在: {users_file}")

        if not passwords_file:
            errors.append("缺少密码字典文件 (payload.passwords_file)")
        elif not os.path.exists(passwords_file):
            warnings.append(f"密码字典文件不存在: {passwords_file}")

        # 验证 payload 模式
        payload_mode = payload.get('mode', 'normal')
        supported_modes = ['normal', 'single_user', 'single_password']
        if payload_mode not in supported_modes:
            errors.append(f"不支持的 payload 模式: {payload_mode}")

        # 验证性能参数
        performance = self.config.get('performance', {})
        concurrency = performance.get('concurrency', 10)
        if not isinstance(concurrency, int) or concurrency < 1:
            errors.append("并发数必须为正整数 (performance.concurrency)")
        elif concurrency > 1000:
            warnings.append(f"并发数过大 ({concurrency})，可能导致性能问题或被检测")

        timeout = performance.get('timeout', 10)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("超时时间必须为正数 (performance.timeout)")
        elif timeout > 300:
            warnings.append(f"超时时间过长 ({timeout}秒)，可能导致任务执行缓慢")

        retry_times = performance.get('retry_times', 3)
        if not isinstance(retry_times, int) or retry_times < 0:
            errors.append("重试次数必须为非负整数 (performance.retry_times)")
        elif retry_times > 10:
            warnings.append(f"重试次数过多 ({retry_times})，可能导致任务执行缓慢")

        checkpoint_interval = performance.get('checkpoint_interval', 100)
        if not isinstance(checkpoint_interval, int) or checkpoint_interval < 1:
            errors.append("检查点间隔必须为正整数 (performance.checkpoint_interval)")

        # 验证检测配置
        detection = self.config.get('detection', {})
        protocol = detection.get('protocol', 'http_form')
        if protocol not in ['http_form', 'http_basic']:
            errors.append(f"不支持的协议类型: {protocol}")

        # 验证状态码列表
        success_status_codes = detection.get('success_status_codes', [200, 302])
        if not isinstance(success_status_codes, list):
            errors.append("成功状态码必须是列表 (detection.success_status_codes)")
        else:
            for code in success_status_codes:
                if not isinstance(code, int) or code < 100 or code > 599:
                    errors.append(f"无效的 HTTP 状态码: {code}")

        # 验证正则表达式（如果提供）
        success_pattern = detection.get('success_pattern')
        if success_pattern:
            try:
                re.compile(success_pattern)
            except re.error as e:
                errors.append(f"成功模式正则表达式错误: {e}")

        failure_pattern = detection.get('failure_pattern')
        if failure_pattern:
            try:
                re.compile(failure_pattern)
            except re.error as e:
                errors.append(f"失败模式正则表达式错误: {e}")

        # 验证防御配置
        defense = self.config.get('defense', {})
        throttle_delay = defense.get('throttle_delay', 5)
        if not isinstance(throttle_delay, (int, float)) or throttle_delay < 0:
            errors.append("节流延迟必须为非负数 (defense.throttle_delay)")

        max_rate_limit_retries = defense.get('max_rate_limit_retries', 3)
        if not isinstance(max_rate_limit_retries, int) or max_rate_limit_retries < 0:
            errors.append("最大速率限制重试次数必须为非负整数 (defense.max_rate_limit_retries)")

        # 验证输出配置
        output = self.config.get('output', {})
        log_level = output.get('log_level', 'INFO')
        supported_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level.upper() not in supported_log_levels:
            errors.append(f"不支持的日志级别: {log_level}")

        # 验证 API 配置（如果模式为 api_service）
        if mode == 'api_service':
            api_config = self.config.get('api', {})
            port = api_config.get('port', 8080)
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append(f"API 服务端口无效: {port}")

            if api_config.get('enable_auth') and not api_config.get('auth_token'):
                warnings.append("API 服务已启用认证但未设置认证令牌 (api.auth_token)")

        # 验证 Web GUI 配置（如果模式为 web_gui）
        if mode == 'web_gui':
            web_gui_config = self.config.get('web_gui', {})
            port = web_gui_config.get('port', 5000)
            if not isinstance(port, int) or port < 1 or port > 65535:
                errors.append(f"Web GUI 服务端口无效: {port}")

            if not web_gui_config.get('secret_key'):
                warnings.append("Web GUI 未设置密钥，会话可能不安全 (web_gui.secret_key)")

        # 合并错误和警告
        all_messages = errors + [f"[警告] {w}" for w in warnings]
        is_valid = len(errors) == 0

        return is_valid, all_messages

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项（支持多级访问）

        Args:
            key: 配置键，支持点号分隔的多级访问，如 'target.url'
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """
        设置配置项（支持多级设置）

        Args:
            key: 配置键，支持点号分隔的多级设置，如 'target.url'
            value: 配置值
        """
        keys = key.split('.')
        config = self.config

        # 定位到最后一个键的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value

    def update_from_dict(self, updates: Dict[str, Any]):
        """
        从字典批量更新配置

        Args:
            updates: 更新字典
        """
        self.config = self._merge_config(self.config, updates)

    def save_config(self, output_path: Optional[str] = None, format: Optional[ConfigFormat] = None):
        """
        保存配置到文件

        Args:
            output_path: 输出路径（可选，默认使用原路径）
            format: 配置格式（可选，默认根据文件扩展名自动判断）
        """
        save_path = output_path or self.config_path
        if not save_path:
            raise ValueError("未指定配置保存路径")

        # 确定保存格式
        if format:
            save_format = format
        else:
            ext = Path(save_path).suffix.lower()
            if ext in ['.yaml', '.yml']:
                save_format = ConfigFormat.YAML
            elif ext == '.ini':
                save_format = ConfigFormat.INI
            else:
                save_format = ConfigFormat.JSON

        # 确保输出目录存在
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)

        with open(save_path, 'w', encoding='utf-8') as f:
            if save_format == ConfigFormat.YAML:
                if not YAML_AVAILABLE:
                    raise ImportError("需要安装 PyYAML 库才能保存 YAML 配置: pip install pyyaml")
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            elif save_format == ConfigFormat.INI:
                self._save_ini_config(f)
            else:  # JSON
                json.dump(self.config, f, indent=2, ensure_ascii=False)

        self.config_path = save_path
        self.config_format = save_format

    def _save_ini_config(self, file_obj):
        """
        保存配置为 INI 格式

        Args:
            file_obj: 文件对象
        """
        config_parser = configparser.ConfigParser()

        for section, options in self.config.items():
            if isinstance(options, dict):
                config_parser.add_section(section)
                for key, value in options.items():
                    # 将值转换为字符串
                    str_value = self._convert_value_to_ini_string(value)
                    config_parser.set(section, key, str_value)

        config_parser.write(file_obj)

    def _convert_value_to_ini_string(self, value: Any) -> str:
        """
        将配置值转换为 INI 字符串格式

        Args:
            value: 配置值

        Returns:
            字符串表示
        """
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (list, tuple)):
            return ','.join(str(item) for item in value)
        elif isinstance(value, dict):
            # 字典无法直接表示在 INI 中，转换为 JSON 字符串
            return json.dumps(value, ensure_ascii=False)
        elif value is None:
            return ''
        else:
            return str(value)

    def get_protocol_config(self) -> Dict[str, Any]:
        """
        获取协议配置（用于初始化协议对象）

        Returns:
            协议配置字典
        """
        detection = self.config.get('detection', {})
        target = self.config.get('target', {})
        performance = self.config.get('performance', {})

        return {
            'url': target.get('url', ''),
            'method': target.get('method', 'POST'),
            'headers': target.get('headers', {}),
            'cookies': target.get('cookies', {}),
            'body_template': target.get('body_template', ''),
            'content_type': target.get('content_type', 'urlencoded'),
            'success_status_codes': detection.get('success_status_codes', [200, 302]),
            'success_pattern': detection.get('success_pattern'),
            'failure_pattern': detection.get('failure_pattern'),
            'timeout': performance.get('timeout', 10),
            'retry_times': performance.get('retry_times', 3)
        }

    def get_performance_config(self) -> Dict[str, Any]:
        """
        获取性能配置

        Returns:
            性能配置字典
        """
        return self.config.get('performance', {})

    def get_defense_config(self) -> Dict[str, Any]:
        """
        获取防御检测配置

        Returns:
            防御配置字典
        """
        return self.config.get('defense', {})

    def get_output_config(self) -> Dict[str, Any]:
        """
        获取输出配置

        Returns:
            输出配置字典
        """
        return self.config.get('output', {})

    def __repr__(self) -> str:
        """
        字符串表示

        Returns:
            配置的字符串表示
        """
        return f"ConfigManager(config_path='{self.config_path}')"

    def to_dict(self) -> Dict[str, Any]:
        """
        导出为字典

        Returns:
            配置字典
        """
        return self._deep_copy_dict(self.config)

    @classmethod
    def generate_template(cls, template_name: str = 'basic', output_format: ConfigFormat = ConfigFormat.JSON) -> Dict[str, Any]:
        """
        生成配置模板

        Args:
            template_name: 模板名称 ('basic', 'advanced', 'stealth', 'aggressive', 'api', 'web_gui')
            output_format: 输出格式

        Returns:
            配置模板字典
        """
        templates = {
            'basic': cls._get_basic_template(),
            'advanced': cls._get_advanced_template(),
            'stealth': cls._get_stealth_template(),
            'aggressive': cls._get_aggressive_template(),
            'api': cls._get_api_template(),
            'web_gui': cls._get_web_gui_template()
        }

        if template_name not in templates:
            raise ValueError(f"不支持的模板名称: {template_name}，支持的模板: {', '.join(templates.keys())}")

        return templates[template_name]

    @classmethod
    def _get_basic_template(cls) -> Dict[str, Any]:
        """基础配置模板"""
        return {
            'general': {
                'language': 'zh-CN',
                'mode': 'cli',
                'debug': False,
                'quiet': False
            },
            'target': {
                'url': 'http://example.com/login',
                'method': 'POST',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                'body_template': 'username={user}&password={pass}',
                'content_type': 'urlencoded',
                'cookies': {}
            },
            'payload': {
                'users_file': 'usernames.txt',
                'passwords_file': 'passwords.txt',
                'rules': [],
                'mode': 'normal'
            },
            'performance': {
                'concurrency': 10,
                'timeout': 10,
                'retry_times': 3,
                'checkpoint_interval': 100
            },
            'detection': {
                'success_status_codes': [200, 302],
                'success_pattern': 'Welcome|成功',
                'failure_pattern': 'Invalid|失败',
                'protocol': 'http_form'
            },
            'defense': {
                'detect_rate_limit': True,
                'auto_throttle': True,
                'throttle_delay': 5,
                'max_rate_limit_retries': 3
            },
            'output': {
                'log_level': 'INFO',
                'log_file': 'authkiller.log',
                'result_file': 'results.json',
                'checkpoint_dir': 'checkpoints'
            }
        }

    @classmethod
    def _get_advanced_template(cls) -> Dict[str, Any]:
        """高级配置模板"""
        template = cls._get_basic_template()
        template.update({
            'performance': {
                'concurrency': 50,
                'timeout': 15,
                'retry_times': 5,
                'checkpoint_interval': 50
            },
            'detection': {
                'success_status_codes': [200, 201, 302, 301],
                'success_pattern': 'Welcome|成功|Dashboard|欢迎|Success|Logged in|登录成功|认证成功',
                'failure_pattern': 'Invalid|错误|Failed|Incorrect|Wrong|Error|Invalid username or password|认证失败|用户名或密码错误',
                'protocol': 'http_form'
            },
            'defense': {
                'detect_rate_limit': True,
                'auto_throttle': True,
                'throttle_delay': 10,
                'max_rate_limit_retries': 5
            },
            'output': {
                'log_level': 'DEBUG',
                'log_file': 'advanced_authkiller.log',
                'result_file': 'advanced_results.json',
                'checkpoint_dir': 'advanced_checkpoints'
            }
        })
        return template

    @classmethod
    def _get_stealth_template(cls) -> Dict[str, Any]:
        """隐蔽模式配置模板"""
        template = cls._get_basic_template()
        template.update({
            'performance': {
                'concurrency': 3,
                'timeout': 30,
                'retry_times': 2,
                'checkpoint_interval': 10
            },
            'defense': {
                'detect_rate_limit': True,
                'auto_throttle': True,
                'throttle_delay': 15,
                'max_rate_limit_retries': 10
            },
            'output': {
                'log_level': 'WARNING',
                'log_file': 'stealth_authkiller.log',
                'result_file': 'stealth_results.json',
                'checkpoint_dir': 'stealth_checkpoints'
            }
        })
        return template

    @classmethod
    def _get_aggressive_template(cls) -> Dict[str, Any]:
        """激进模式配置模板"""
        template = cls._get_basic_template()
        template.update({
            'performance': {
                'concurrency': 100,
                'timeout': 5,
                'retry_times': 10,
                'checkpoint_interval': 200
            },
            'defense': {
                'detect_rate_limit': False,
                'auto_throttle': False,
                'throttle_delay': 1,
                'max_rate_limit_retries': 3
            },
            'output': {
                'log_level': 'INFO',
                'log_file': 'aggressive_authkiller.log',
                'result_file': 'aggressive_results.json',
                'checkpoint_dir': 'aggressive_checkpoints'
            }
        })
        return template

    @classmethod
    def _get_api_template(cls) -> Dict[str, Any]:
        """API 服务模式配置模板"""
        template = cls._get_basic_template()
        template['general']['mode'] = 'api_service'
        template.update({
            'api': {
                'host': '0.0.0.0',
                'port': 8080,
                'enable_auth': True,
                'auth_token': 'your-secret-token-here',
                'cors_origins': ['*']
            }
        })
        return template

    @classmethod
    def _get_web_gui_template(cls) -> Dict[str, Any]:
        """Web GUI 模式配置模板"""
        template = cls._get_basic_template()
        template['general']['mode'] = 'web_gui'
        template.update({
            'web_gui': {
                'host': '0.0.0.0',
                'port': 5000,
                'secret_key': 'your-secret-key-here-change-in-production',
                'session_timeout': 3600
            }
        })
        return template

    @classmethod
    def save_template(cls, template_name: str, output_path: str, format: ConfigFormat = ConfigFormat.JSON):
        """
        保存配置模板到文件

        Args:
            template_name: 模板名称
            output_path: 输出路径
            format: 输出格式
        """
        template = cls.generate_template(template_name, format)

        # 创建临时配置管理器来保存模板
        temp_manager = cls()
        temp_manager.config = template
        temp_manager.save_config(output_path, format)

    def get_general_config(self) -> Dict[str, Any]:
        """
        获取通用配置

        Returns:
            通用配置字典
        """
        return self.config.get('general', {})

    def get_language(self) -> str:
        """
        获取语言设置

        Returns:
            语言代码
        """
        return self.config.get('general', {}).get('language', 'zh-CN')

    def get_run_mode(self) -> str:
        """
        获取运行模式

        Returns:
            运行模式
        """
        return self.config.get('general', {}).get('mode', 'cli')

    def get_api_config(self) -> Dict[str, Any]:
        """
        获取 API 服务配置

        Returns:
            API 配置字典
        """
        return self.config.get('api', {})

    def get_web_gui_config(self) -> Dict[str, Any]:
        """
        获取 Web GUI 配置

        Returns:
            Web GUI 配置字典
        """
        return self.config.get('web_gui', {})

    def get_thinker_gui_config(self) -> Dict[str, Any]:
        """
        获取 THINKER GUI 配置

        Returns:
            THINKER GUI 配置字典
        """
        return self.config.get('thinker_gui', {})