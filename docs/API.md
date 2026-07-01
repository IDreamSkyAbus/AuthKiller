# AuthKiller API参考文档

## 目录

1. [核心模块](#核心模块)
2. [协议模块](#协议模块)
3. [载荷管理模块](#载荷管理模块)
4. [状态管理模块](#状态管理模块)
5. [工具模块](#工具模块)
6. [完整使用示例](#完整使用示例)

---

## 核心模块

### ConfigManager (authkiller.core.config)

配置管理器，负责加载、验证和管理配置。

#### 类方法

##### `__init__(config_path: Optional[str] = None)`

初始化配置管理器。

**参数**：
- `config_path` (Optional[str]): 配置文件路径，支持 .json 或 .yaml/.yml 格式

**示例**：
```python
from authkiller.core.config import ConfigManager

# 从配置文件加载
config = ConfigManager('examples/configs/example.json')

# 使用默认配置
config = ConfigManager()
```

---

##### `load_config(config_path: str)`

加载配置文件。

**参数**：
- `config_path` (str): 配置文件路径

**异常**：
- `FileNotFoundError`: 配置文件不存在
- `ValueError`: 配置文件格式错误

**示例**：
```python
config = ConfigManager()
config.load_config('my_config.json')
```

---

##### `validate() -> tuple`

验证配置是否有效。

**返回**：
- `tuple`: (is_valid, error_message)

**示例**：
```python
is_valid, error = config.validate()
if not is_valid:
    print(f"配置错误: {error}")
```

---

##### `get(key: str, default: Any = None) -> Any`

获取配置项（支持多级访问）。

**参数**：
- `key` (str): 配置键，支持点号分隔，如 'target.url'
- `default` (Any): 默认值

**返回**：
- `Any`: 配置值

**示例**：
```python
url = config.get('target.url')
concurrency = config.get('performance.concurrency', 10)
```

---

##### `set(key: str, value: Any)`

设置配置项。

**参数**：
- `key` (str): 配置键，支持点号分隔
- `value` (Any): 配置值

**示例**：
```python
config.set('target.url', 'http://example.com')
config.set('performance.concurrency', 50)
```

---

##### `update_from_dict(updates: Dict[str, Any])`

从字典批量更新配置。

**参数**：
- `updates` (Dict): 更新字典

**示例**：
```python
config.update_from_dict({
    'target': {'url': 'http://new.com'},
    'performance': {'concurrency': 30}
})
```

---

##### `get_protocol_config() -> Dict[str, Any]`

获取协议配置。

**返回**：
- `Dict`: 协议配置字典

**示例**：
```python
protocol_config = config.get_protocol_config()
# {'url': ..., 'method': ..., 'timeout': ...}
```

---

### AttackEngine (authkiller.core.engine)

主引擎，协调各模块并管理并发任务。

#### 类方法

##### `__init__(config_manager: ConfigManager)`

初始化引擎。

**参数**：
- `config_manager` (ConfigManager): 配置管理器实例

**示例**：
```python
from authkiller.core.engine import AttackEngine

engine = AttackEngine(config_manager)
```

---

##### `async initialize()`

初始化引擎（异步）。

**示例**：
```python
await engine.initialize()
```

---

##### `async cleanup()`

清理资源（异步）。

**示例**：
```python
await engine.cleanup()
```

---

##### `async run(checkpoint_file: Optional[str] = None) -> Dict[str, Any]`

运行攻击任务。

**参数**：
- `checkpoint_file` (Optional[str]): 断点文件路径（用于恢复）

**返回**：
- `Dict`: 执行结果统计字典

**示例**：
```python
# 运行新任务
stats = await engine.run()

# 从断点恢复
stats = await engine.run('checkpoint_20260701_120000.json')
```

---

##### `stop()`

停止任务。

**示例**：
```python
engine.stop()
```

---

##### `pause()`

暂停任务。

**示例**：
```python
engine.pause()
```

---

##### `resume()`

恢复任务。

**示例**：
```python
engine.resume()
```

---

##### `get_progress() -> Dict[str, Any]`

获取当前进度。

**返回**：
- `Dict`: 进度信息字典

**示例**：
```python
progress = engine.get_progress()
print(f"进度: {progress['progress_percentage']}")
```

---

### Attacker (authkiller.core.attacker)

攻击执行器，执行单次认证测试。

#### 类方法

##### `__init__(config: Dict[str, Any])`

初始化攻击执行器。

**参数**：
- `config` (Dict): 配置字典

**示例**：
```python
from authkiller.core.attacker import Attacker

attacker = Attacker(protocol_config)
```

---

##### `async test_credential(username: str, password: str) -> Tuple[bool, Dict[str, Any]]`

测试单个凭证组合。

**参数**：
- `username` (str): 用户名
- `password` (str): 密码

**返回**：
- `Tuple`: (是否成功, 结果详情字典)

**示例**：
```python
success, result = await attacker.test_credential('admin', 'password123')
if success:
    print(f"成功: {result['username']}:{result['password']}")
```

---

##### `async test_with_defense_handling(username: str, password: str) -> Tuple[bool, Dict[str, Any]]`

测试凭证并处理防御机制。

**参数**：
- `username` (str): 用户名
- `password` (str): 密码

**返回**：
- `Tuple`: (是否成功, 结果详情字典)

**示例**：
```python
success, result = await attacker.test_with_defense_handling('admin', 'password123')
```

---

##### `async init_session()`

初始化协议会话。

**示例**：
```python
await attacker.init_session()
```

---

##### `async close_session()`

关闭协议会话。

**示例**：
```python
await attacker.close_session()
```

---

## 协议模块

### BaseProtocol (authkiller.protocols.base)

协议基类，定义统一接口。

#### 类方法

##### `__init__(config: Dict[str, Any])`

初始化协议。

**参数**：
- `config` (Dict): 协议配置字典

---

##### `async test_credential(username: str, password: str) -> bool`

测试凭证是否有效（抽象方法）。

**参数**：
- `username` (str): 用户名
- `password` (str): 密码

**返回**：
- `bool`: True 表示认证成功

---

##### `parse_response(response: Any) -> Dict[str, Any]`

解析响应内容（抽象方法）。

**参数**：
- `response`: HTTP 响应对象

**返回**：
- `Dict`: 响应数据字典

---

##### `is_success(response_data: Dict[str, Any]) -> bool`

判断认证是否成功（抽象方法）。

**参数**：
- `response_data` (Dict): 解析后的响应数据

**返回**：
- `bool`: True 表示认证成功

---

### HTTPFormProtocol (authkiller.protocols.http_form)

HTTP表单登录协议实现。

#### 类方法

继承 `BaseProtocol` 所有方法，额外提供：

##### `_construct_body(username: str, password: str) -> Any`

构造请求体。

**参数**：
- `username` (str): 用户名
- `password` (str): 密码

**返回**：
- `Any`: 请求体数据（字典或字符串）

**示例**：
```python
body = protocol._construct_body('admin', 'password123')
```

---

##### `_get_content_headers() -> Dict[str, str]`

获取 Content-Type Headers。

**返回**：
- `Dict`: Headers 字典

**示例**：
```python
headers = protocol._get_content_headers()
```

---

##### `async is_success_with_content(response_data: Dict[str, Any]) -> bool`

判断认证是否成功（包含响应内容判断）。

**参数**：
- `response_data` (Dict): 解析后的响应数据

**返回**：
- `bool`: True 表示认证成功

**示例**：
```python
result = await protocol.is_success_with_content(response_data)
```

---

### HTTPBasicProtocol (authkiller.protocols.http_basic)

HTTP Basic Auth 协议实现。

#### 类方法

继承 `BaseProtocol` 所有方法。

---

## 载荷管理模块

### DictionaryManager (authkiller.payload.dictionary)

字典管理器，使用生成器逐行读取大文件。

#### 类方法

##### `__init__(users_file: str, passwords_file: str)`

初始化字典管理器。

**参数**：
- `users_file` (str): 用户名字典文件路径
- `passwords_file` (str): 密码字典文件路径

**异常**：
- `FileNotFoundError`: 文件不存在

**示例**：
```python
from authkiller.payload.dictionary import DictionaryManager

dict_mgr = DictionaryManager('users.txt', 'passwords.txt')
```

---

##### `load_users() -> Generator[str, None, None]`

逐行加载用户名字典。

**返回**：
- `Generator`: 用户名生成器

**示例**：
```python
for username in dict_mgr.load_users():
    print(username)
```

---

##### `load_passwords() -> Generator[str, None, None]`

逐行加载密码字典。

**返回**：
- `Generator`: 密码生成器

**示例**：
```python
for password in dict_mgr.load_passwords():
    print(password)
```

---

##### `generate_combinations(mode: str = 'normal') -> Generator[tuple, None, None]`

生成用户名/密码组合。

**参数**：
- `mode` (str): 组合模式
  - 'normal': 所有组合
  - 'single_user': 单用户多密码
  - 'single_password': 单密码多用户

**返回**：
- `Generator`: (username, password) 组合生成器

**示例**：
```python
for username, password in dict_mgr.generate_combinations():
    print(f"{username}:{password}")
```

---

##### `mark_combination_tested(username: str, password: str)`

标记组合已测试。

**参数**：
- `username` (str): 用户名
- `password` (str): 密码

**示例**：
```python
dict_mgr.mark_combination_tested('admin', 'password')
```

---

##### `is_combination_tested(username: str, password: str) -> bool`

检查组合是否已测试。

**参数**：
- `username` (str): 用户名
- `password` (str): 密码

**返回**：
- `bool`: True 表示已测试

**示例**：
```python
if dict_mgr.is_combination_tested('admin', 'password'):
    print("已测试")
```

---

##### `get_total_combinations(mode: str = 'normal') -> int`

获取总组合数。

**参数**：
- `mode` (str): 组合模式

**返回**：
- `int`: 总组合数

**示例**：
```python
total = dict_mgr.get_total_combinations()
print(f"总共 {total} 个组合")
```

---

##### `get_remaining_combinations() -> int`

获取剩余未测试的组合数。

**返回**：
- `int`: 剩余组合数

**示例**：
```python
remaining = dict_mgr.get_remaining_combinations()
```

---

### RuleEngine (authkiller.payload.rules)

规则引擎，支持密码变异和动态生成。

#### 类方法

##### `__init__()`

初始化规则引擎。

**示例**：
```python
from authkiller.payload.rules import RuleEngine

rule_engine = RuleEngine()
```

---

##### `register_rule(name: str, rule_func: Callable)`

注册自定义规则。

**参数**：
- `name` (str): 规则名称
- `rule_func` (Callable): 规则函数

**示例**：
```python
def custom_rule(password):
    return [password + '_custom']

rule_engine.register_rule('custom', custom_rule)
```

---

##### `apply_rule(password: str, rule_name: str) -> List[str]`

应用单个规则。

**参数**：
- `password` (str): 原始密码
- `rule_name` (str): 规则名称

**返回**：
- `List`: 变异后的密码列表

**示例**：
```python
mutated = rule_engine.apply_rule('admin', 'uppercase')
# ['ADMIN']
```

---

##### `apply_rules_chain(password: str, rules: List[str]) -> Generator[str, None, None]`

应用规则链（链式组合）。

**参数**：
- `password` (str): 原始密码
- `rules` (List): 规则列表

**返回**：
- `Generator`: 变异密码生成器

**示例**：
```python
for pwd in rule_engine.apply_rules_chain('admin', ['uppercase', 'append_numbers']):
    print(pwd)  # ADMIN1, ADMIN123, ...
```

---

##### `apply_multiple_rules(password: str, rules: List[str]) -> List[str]`

应用多个规则（非链式）。

**参数**：
- `password` (str): 原始密码
- `rules` (List): 规则列表

**返回**：
- `List`: 变异密码列表

**示例**：
```python
mutated = rule_engine.apply_multiple_rules('admin', ['uppercase', 'append_numbers'])
# ['admin', 'ADMIN', 'admin1', 'admin123', ...]
```

---

##### `get_available_rules() -> List[str]`

获取所有可用规则。

**返回**：
- `List`: 规则名称列表

**示例**：
```python
rules = rule_engine.get_available_rules()
print(rules)  # ['uppercase', 'lowercase', 'append_numbers', ...]
```

---

### PasswordMutator (authkiller.payload.rules)

密码变异器，支持批量变异密码字典。

#### 类方法

##### `__init__(rule_engine: RuleEngine = None)`

初始化密码变异器。

**参数**：
- `rule_engine` (RuleEngine): 规则引擎实例（可选）

**示例**：
```python
from authkiller.payload.rules import PasswordMutator

mutator = PasswordMutator()
```

---

##### `mutate_password(password: str, rules: List[str], chain: bool = False) -> List[str]`

变异密码。

**参数**：
- `password` (str): 原始密码
- `rules` (List): 规则列表
- `chain` (bool): 是否链式组合

**返回**：
- `List`: 变异密码列表

**示例**：
```python
mutated = mutator.mutate_password('admin', ['uppercase', 'append_numbers'])
```

---

##### `mutate_dictionary(passwords: Generator, rules: List[str], chain: bool = False) -> Generator[str, None, None]`

变异整个字典。

**参数**：
- `passwords` (Generator): 原始密码生成器
- `rules` (List): 规则列表
- `chain` (bool): 是否链式组合

**返回**：
- `Generator`: 变异密码生成器

**示例**：
```python
def password_gen():
    yield 'admin'
    yield 'password'

for pwd in mutator.mutate_dictionary(password_gen(), ['uppercase']):
    print(pwd)
```

---

## 状态管理模块

### CheckpointManager (authkiller.state.checkpoint)

断点续传管理器。

#### 类方法

##### `__init__(checkpoint_dir: str = "checkpoints")`

初始化断点管理器。

**参数**：
- `checkpoint_dir` (str): 断点文件存储目录

**示例**：
```python
from authkiller.state.checkpoint import CheckpointManager

checkpoint_mgr = CheckpointManager('checkpoints')
```

---

##### `async save_checkpoint(data: Dict[str, Any]) -> str`

保存断点数据。

**参数**：
- `data` (Dict): 断点数据字典

**返回**：
- `str`: 断点文件路径

**示例**：
```python
checkpoint_data = CheckpointManager.create_checkpoint_data(
    tested_combinations={'admin:password'},
    current_position=100
)
filepath = await checkpoint_mgr.save_checkpoint(checkpoint_data)
```

---

##### `async load_checkpoint(checkpoint_file: str) -> Dict[str, Any]`

加载断点数据。

**参数**：
- `checkpoint_file` (str): 断点文件路径

**返回**：
- `Dict`: 断点数据

**示例**：
```python
data = await checkpoint_mgr.load_checkpoint('checkpoint_20260701_120000.json')
tested = data['tested_combinations']
```

---

##### `get_latest_checkpoint() -> str`

获取最新的断点文件。

**返回**：
- `str`: 最新断点文件路径，如果没有返回 None

**示例**：
```python
latest = checkpoint_mgr.get_latest_checkpoint()
```

---

##### `list_checkpoints() -> list`

列出所有断点文件。

**返回**：
- `list`: 断点文件列表

**示例**：
```python
checkpoints = checkpoint_mgr.list_checkpoints()
for checkpoint in checkpoints:
    print(f"{checkpoint['filename']} - {checkpoint['time_str']}")
```

---

##### `static create_checkpoint_data(...) -> Dict[str, Any]`

创建断点数据结构（静态方法）。

**参数**：
- `tested_combinations` (Set): 已测试组合集合
- `current_position` (int): 当前位置
- `config` (Dict): 配置字典（可选）
- `results` (list): 结果列表（可选）

**返回**：
- `Dict`: 断点数据

**示例**：
```python
data = CheckpointManager.create_checkpoint_data(
    tested_combinations={'admin:password'},
    current_position=100,
    config={'target': {'url': 'http://example.com'}},
    results=[]
)
```

---

### SessionManager (authkiller.state.session)

会话管理器，管理Cookie、Token和会话状态。

#### 类方法

##### `__init__()`

初始化会话管理器。

**示例**：
```python
from authkiller.state.session import SessionManager

session_mgr = SessionManager()
```

---

##### `extract_cookies(response: aiohttp.ClientResponse) -> Dict[str, str]`

从响应中提取Cookie。

**参数**：
- `response` (aiohttp.ClientResponse): aiohttp 响应对象

**返回**：
- `Dict`: Cookie 字典

**示例**：
```python
cookies = session_mgr.extract_cookies(response)
```

---

##### `async extract_csrf_token(response_text: str, patterns: list = None) -> Optional[str]`

从响应内容中提取CSRF Token。

**参数**：
- `response_text` (str): 响应文本
- `patterns` (list): Token 提取模式列表（可选）

**返回**：
- `Optional[str]: Token 值，如果未找到返回 None

**示例**：
```python
token = await session_mgr.extract_csrf_token(response_text)
```

---

##### `inject_cookies_to_request(headers: Dict[str, str] = None) -> Dict[str, str]`

将存储的Cookie注入到请求Headers。

**参数**：
- `headers` (Dict): 现有 Headers（可选）

**返回**：
- `Dict`: 包含 Cookie 的 Headers

**示例**：
```python
headers = session_mgr.inject_cookies_to_request()
```

---

##### `inject_token_to_request(body_template: str, token_name: str = 'csrf_token') -> str`

将Token注入到请求体模板。

**参数**：
- `body_template` (str): 请求体模板
- `token_name` (str): Token 参数名

**返回**：
- `str`: 包含 Token 的请求体模板

**示例**：
```python
body = session_mgr.inject_token_to_request('username={user}&password={pass}')
```

---

## 工具模块

### Logger (authkiller.utils.logger)

日志系统。

#### 类方法

##### `__init__(name: str = "AuthKiller", level: int = logging.INFO, log_file: Optional[str] = None)`

初始化日志器。

**参数**：
- `name` (str): 日志器名称
- `level` (int): 日志级别
- `log_file` (Optional[str]): 日志文件路径（可选）

**示例**：
```python
from authkiller.utils.logger import Logger

logger = Logger('MyApp', logging.DEBUG, 'app.log')
```

---

##### `static get_logger(name: str = 'AuthKiller', level: int = None, log_file: str = None) -> Logger`

获取日志器实例（静态方法）。

**返回**：
- `Logger`: Logger 实例

**示例**：
```python
logger = Logger.get_logger('engine', logging.INFO)
logger.info("开始执行任务")
logger.success("admin", "password123")
```

---

### Reporter (authkiller.utils.reporter)

报告生成器。

#### 类方法

##### `__init__(output_dir: str = "reports")`

初始化报告生成器。

**参数**：
- `output_dir` (str): 报告输出目录

**示例**：
```python
from authkiller.utils.reporter import Reporter

reporter = Reporter('reports')
```

---

##### `add_result(username: str, password: str, success: bool, timestamp: str = None, details: Dict[str, Any] = None)`

添加测试结果。

**参数**：
- `username` (str): 用户名
- `password` (str): 密码
- `success` (bool): 是否成功
- `timestamp` (str): 时间戳（可选）
- `details` (Dict): 详细信息（可选）

**示例**：
```python
reporter.add_result('admin', 'password123', True, details={'status_code': 200})
```

---

##### `export_json(filename: str = None) -> str`

导出为JSON格式。

**参数**：
- `filename` (str): 文件名（可选）

**返回**：
- `str`: 文件路径

**示例**：
```python
filepath = reporter.export_json('report.json')
```

---

##### `export_csv(filename: str = None) -> str`

导出为CSV格式。

**参数**：
- `filename` (str): 文件名（可选）

**返回**：
- `str`: 文件路径

**示例**：
```python
filepath = reporter.export_csv('report.csv')
```

---

##### `export_txt(filename: str = None) -> str`

导出为TXT格式。

**参数**：
- `filename` (str): 文件名（可选）

**返回**：
- `str`: 文件路径

**示例**：
```python
filepath = reporter.export_txt('report.txt')
```

---

##### `async save_json(data: Dict[str, Any], filename: str) -> str`

异步保存JSON格式报告。

**参数**：
- `data` (Dict): 数据字典
- `filename` (str): 文件名

**返回**：
- `str`: 文件路径

**示例**：
```python
filepath = await reporter.save_json(data, 'results.json')
```

---

### DefenseDetector (authkiller.utils.defense)

防御机制检测器。

#### 类方法

##### `__init__(config: Dict[str, Any] = None)`

初始化防御检测器。

**参数**：
- `config` (Dict): 配置字典（可选）

**示例**：
```python
from authkiller.utils.defense import DefenseDetector

detector = DefenseDetector()
```

---

##### `detect_rate_limit(response: aiohttp.ClientResponse) -> bool`

检测速率限制。

**参数**：
- `response` (aiohttp.ClientResponse): HTTP 响应对象

**返回**：
- `bool`: True 表示检测到速率限制

**示例**：
```python
if detector.detect_rate_limit(response):
    print("检测到速率限制")
```

---

##### `async detect_account_lockout(response: aiohttp.ClientResponse, response_text: str = None) -> bool`

检测账户锁定。

**参数**：
- `response` (aiohttp.ClientResponse): HTTP 响应对象
- `response_text` (str): 响应文本（可选）

**返回**：
- `bool`: True 表示检测到账户锁定

**示例**：
```python
if await detector.detect_account_lockout(response, text):
    print("检测到账户锁定")
```

---

##### `async detect_captcha(response: aiohttp.ClientResponse, response_text: str = None) -> bool`

检测验证码。

**参数**：
- `response` (aiohttp.ClientResponse): HTTP 响应对象
- `response_text` (str): 响应文本（可选）

**返回**：
- `bool`: True 表示检测到验证码

**示例**：
```python
if await detector.detect_captcha(response, text):
    print("检测到验证码")
```

---

##### `async detect_all_defenses(response: aiohttp.ClientResponse, response_text: str = None) -> Dict[str, bool]`

检测所有防御机制。

**参数**：
- `response` (aiohttp.ClientResponse): HTTP 响应对象
- `response_text` (str): 响应文本（可选）

**返回**：
- `Dict`: 检测结果字典

**示例**：
```python
results = await detector.detect_all_defenses(response, text)
if results['rate_limit']:
    print("速率限制")
```

---

##### `get_throttle_recommendation() -> int`

获取降速建议（等待秒数）。

**返回**：
- `int`: 建议等待的秒数

**示例**：
```python
wait_time = detector.get_throttle_recommendation()
await asyncio.sleep(wait_time)
```

---

## 完整使用示例

### 示例1: 使用API直接控制引擎

```python
import asyncio
from authkiller.core.config import ConfigManager
from authkiller.core.engine import AttackEngine

async def main():
    # 创建配置
    config = ConfigManager()
    config.set('target.url', 'http://example.com/login')
    config.set('target.method', 'POST')
    config.set('payload.users_file', 'users.txt')
    config.set('payload.passwords_file', 'passwords.txt')
    config.set('performance.concurrency', 30)
    config.set('detection.success_pattern', 'Welcome|成功')

    # 创建引擎
    engine = AttackEngine(config)

    # 运行任务
    stats = await engine.run()

    # 显示结果
    print(f"总尝试次数: {stats['total_attempts']}")
    print(f"成功次数: {stats['success_count']}")
    print(f"成功率: {stats['success_rate']}")

    # 显示成功凭证
    for result in engine.success_results:
        print(f"成功: {result['username']}:{result['password']}")

asyncio.run(main())
```

---

### 示例2: 使用字典管理器和规则引擎

```python
from authkiller.payload.dictionary import DictionaryManager
from authkiller.payload.rules import PasswordMutator

# 创建字典管理器
dict_mgr = DictionaryManager('users.txt', 'passwords.txt')

# 创建密码变异器
mutator = PasswordMutator()

# 应用规则
for username, password in dict_mgr.generate_combinations():
    # 变异密码
    mutated_passwords = mutator.mutate_password(
        password,
        ['uppercase', 'append_numbers']
    )

    for pwd in mutated_passwords:
        print(f"{username}:{pwd}")
```

---

### 示例3: 自定义协议实现

```python
from authkiller.protocols.base import BaseProtocol
import aiohttp

class CustomAuthProtocol(BaseProtocol):
    async def test_credential(self, username: str, password: str) -> bool:
        # 自定义认证逻辑
        await self.init_session()

        # 构造自定义请求
        data = {
            'user': username,
            'pass': password,
            'custom_field': 'value'
        }

        response = await self.session.post(
            self.url,
            json=data,
            headers={'X-Custom-Header': 'CustomValue'}
        )

        return self.is_success({'status_code': response.status})

    def is_success(self, response_data: dict) -> bool:
        # 自定义成功判定
        return response_data['status_code'] == 200

# 使用自定义协议
config = {
    'url': 'http://custom.api.com/auth',
    'timeout': 10
}

protocol = CustomAuthProtocol(config)
result = await protocol.test_credential('admin', 'password')
```

---

### 示例4: 断点续传和恢复

```python
from authkiller.state.checkpoint import CheckpointManager

async def save_progress():
    # 创建断点管理器
    checkpoint_mgr = CheckpointManager('checkpoints')

    # 创建断点数据
    checkpoint_data = CheckpointManager.create_checkpoint_data(
        tested_combinations={'admin:password', 'root:123456'},
        current_position=100,
        config={'target': {'url': 'http://example.com'}},
        results=[{'username': 'admin', 'password': 'password'}]
    )

    # 保存断点
    filepath = await checkpoint_mgr.save_checkpoint(checkpoint_data)
    print(f"断点已保存: {filepath}")

async def restore_progress():
    # 加载断点
    checkpoint_mgr = CheckpointManager('checkpoints')
    data = await checkpoint_mgr.load_checkpoint('checkpoint_20260701_120000.json')

    # 恢复已测试组合
    tested = data['tested_combinations']
    print(f"已测试 {len(tested)} 个组合")

    # 继续测试...

asyncio.run(save_progress())
```

---

**完整API文档已更新，请参考各模块的具体实现和使用示例。**