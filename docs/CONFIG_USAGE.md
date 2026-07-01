# AuthKiller 配置管理使用指南

## 概述

AuthKiller 的配置管理模块支持多种配置格式和高级功能，包括：

- **多种配置格式**：JSON、YAML、INI
- **配置模板生成**：6 种预定义模板（基础、高级、隐蔽、激进、API、Web GUI）
- **配置验证**：详细的类型和范围验证
- **配置合并**：多个配置文件合并功能
- **语言支持**：预留国际化配置
- **模式支持**：CLI、Web GUI、THINKER GUI、API 服务

## 配置格式

### 1. JSON 格式

最常用的配置格式，易于阅读和编辑：

```json
{
  "general": {
    "language": "zh-CN",
    "mode": "cli"
  },
  "target": {
    "url": "http://example.com/login",
    "method": "POST"
  }
}
```

### 2. YAML 格式

更易读的配置格式（需要安装 PyYAML）：

```yaml
general:
  language: zh-CN
  mode: cli

target:
  url: http://example.com/login
  method: POST
```

### 3. INI 格式

传统配置格式，适合简单配置：

```ini
[general]
language = zh-CN
mode = cli

[target]
url = http://example.com/login
method = POST
```

## 配置模板

### 使用预定义模板

```python
from authkiller.core.config import ConfigManager, ConfigFormat

# 生成基础模板
basic_config = ConfigManager.generate_template('basic')

# 生成高级模板
advanced_config = ConfigManager.generate_template('advanced')

# 生成隐蔽模式模板
stealth_config = ConfigManager.generate_template('stealth')

# 生成激进模式模板
aggressive_config = ConfigManager.generate_template('aggressive')

# 生成 API 服务模板
api_config = ConfigManager.generate_template('api')

# 生成 Web GUI 模板
web_gui_config = ConfigManager.generate_template('web_gui')

# 保存模板到文件
ConfigManager.save_template('basic', 'config.json', ConfigFormat.JSON)
ConfigManager.save_template('advanced', 'config.yaml', ConfigFormat.YAML)
```

### 可用模板说明

| 模板名称 | 说明 | 适用场景 |
|---------|------|---------|
| basic | 基础配置模板 | 快速测试、学习使用 |
| advanced | 高级配置模板 | 生产环境、复杂场景 |
| stealth | 隐蔽模式模板 | 绕过检测、低调测试 |
| aggressive | 激进模式模板 | 高强度测试、快速扫描 |
| api | API 服务模板 | API 服务模式运行 |
| web_gui | Web GUI 模板 | Web 界面模式运行 |

## 配置加载与保存

### 加载配置

```python
# 加载单个配置文件
manager = ConfigManager('config.json')

# 加载多个配置文件并合并
manager = ConfigManager(config_paths=['base.json', 'override.json'])

# 使用合并策略
manager = ConfigManager()
manager.load_and_merge_configs(['base.json', 'override.json'], merge_strategy='merge')
```

### 保存配置

```python
# 保存为 JSON 格式
manager.save_config('output.json', ConfigFormat.JSON)

# 保存为 YAML 格式
manager.save_config('output.yaml', ConfigFormat.YAML)

# 保存为 INI 格式
manager.save_config('output.ini', ConfigFormat.INI)
```

## 配置验证

### 验证配置

```python
manager = ConfigManager('config.json')
is_valid, messages = manager.validate()

if is_valid:
    print("配置验证通过")
else:
    print("配置验证失败")
    for msg in messages:
        print(f"  - {msg}")
```

### 验证规则

配置验证包括以下检查：

1. **类型验证**：确保配置项类型正确
2. **范围验证**：确保数值在合理范围内
3. **存在性验证**：检查必要配置项是否存在
4. **格式验证**：验证 URL、正则表达式等格式
5. **路径验证**：检查文件路径是否存在

## 配置合并

### 合并策略

有两种合并策略：

1. **override（覆盖）**：后加载的配置覆盖前加载的配置
2. **merge（合并）**：递归合并所有配置，列表去重合并

```python
# 覆盖合并
manager.load_and_merge_configs(['base.json', 'override.json'], merge_strategy='override')

# 递归合并
manager.load_and_merge_configs(['base.json', 'extra.json'], merge_strategy='merge')
```

## 配置访问

### 获取配置项

```python
# 获取单个配置项
url = manager.get('target.url')
concurrency = manager.get('performance.concurrency')

# 获取配置项（带默认值）
timeout = manager.get('performance.timeout', default=10)

# 获取特定配置
general_config = manager.get_general_config()
language = manager.get_language()
run_mode = manager.get_run_mode()
```

### 设置配置项

```python
# 设置单个配置项
manager.set('target.url', 'http://new.example.com/login')
manager.set('performance.concurrency', 20)

# 批量更新
manager.update_from_dict({
    'target': {'url': 'http://new.example.com/login'},
    'performance': {'concurrency': 20}
})
```

## 语言和模式配置

### 语言支持

配置文件中预留了语言选择配置：

```json
{
  "general": {
    "language": "zh-CN"  // 支持 zh-CN, en-US, ja-JP, ko-KR
  }
}
```

### 运行模式

支持四种运行模式：

```json
{
  "general": {
    "mode": "cli"  // 支持 cli, web_gui, thinker_gui, api_service
  }
}
```

每种模式都有特定的配置项：

- **CLI 模式**：基础配置
- **Web GUI 模式**：`web_gui` 配置项（端口、密钥等）
- **THINKER GUI 模式**：`thinker_gui` 配置项（主题、窗口大小等）
- **API 服务模式**：`api` 配置项（端口、认证等）

## 完整配置示例

### JSON 配置示例

```json
{
  "general": {
    "language": "zh-CN",
    "mode": "cli",
    "debug": false,
    "quiet": false
  },
  "target": {
    "url": "http://example.com/login",
    "method": "POST",
    "headers": {
      "User-Agent": "Mozilla/5.0",
      "Content-Type": "application/x-www-form-urlencoded"
    },
    "body_template": "username={user}&password={pass}",
    "content_type": "urlencoded"
  },
  "payload": {
    "users_file": "usernames.txt",
    "passwords_file": "passwords.txt",
    "mode": "normal"
  },
  "performance": {
    "concurrency": 10,
    "timeout": 10,
    "retry_times": 3
  },
  "detection": {
    "success_status_codes": [200, 302],
    "success_pattern": "Welcome|成功",
    "failure_pattern": "Invalid|失败",
    "protocol": "http_form"
  },
  "defense": {
    "detect_rate_limit": true,
    "auto_throttle": true,
    "throttle_delay": 5
  },
  "output": {
    "log_level": "INFO",
    "log_file": "authkiller.log",
    "result_file": "results.json"
  }
}
```

## 最佳实践

1. **使用配置模板**：从预定义模板开始，然后根据需要调整
2. **配置验证**：始终在运行前验证配置
3. **分层配置**：使用多个配置文件分层管理（基础配置 + 环境配置）
4. **版本控制**：将配置文件纳入版本控制
5. **敏感信息**：不要在配置文件中存储敏感信息（密码、令牌等）

## 依赖说明

- **JSON**：内置支持，无需额外依赖
- **YAML**：需要 PyYAML 库（可选依赖）
  ```bash
  pip install pyyaml
  ```
- **INI**：内置支持，无需额外依赖