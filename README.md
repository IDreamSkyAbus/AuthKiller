# AuthKiller - 密码测试工具

**\[!] 重要声明：本工具仅用于授权安全审计和强度测试，严禁用于任何非法用途！**

**GitHub:** <https://github.com/IDreamSkyAbus/AuthKiller>

## 项目简介

AuthKiller 是一个基于 Python 的高性能密码测试工具，专为授权安全审计和强度测试设计。使用异步架构（asyncio + aiohttp），支持多种身份验证协议，提供断点续传、规则引擎、防御机制检测等高级功能。

## 核心特性

- ✅ **高性能异步架构**：基于 asyncio + aiohttp，充分利用网络带宽
- ✅ **多协议支持**：HTTP/HTTPS（表单登录、Basic Auth）
- ✅ **智能字典管理**：生成器逐行读取，避免内存溢出
- ✅ **规则引擎**：密码变异、动态生成、规则链式组合
- ✅ **断点续传**：定期保存进度，意外中断可恢复
- ✅ **防御机制检测**：速率限制、账户锁定、验证码检测
- ✅ **多格式报告**：JSON、CSV、TXT 格式输出
- ✅ **进度可视化**：实时进度条和彩色日志

## 法律声明

**使用本工具前，必须确保：**

1. ✅ 已获得目标系统的明确书面授权
2. ✅ 测试行为符合所在国家/地区的法律法规
3. ✅ 测试结果仅用于安全加固，不用于任何恶意目的
4. ✅ 了解并承担使用本工具可能产生的法律责任

**作者和开发者不对任何非法使用行为承担责任。**

## 安装

### 从源码安装

```bash
git clone https://github.com/example/authkiller.git
cd authkiller
pip install -r requirements.txt
pip install -e .
```

### 依赖要求

- Python 3.7+
- aiohttp >= 3.9.0
- aiofiles >= 23.2.0
- tqdm >= 4.66.0
- colorama >= 0.4.6
- pyyaml >= 6.0

## 快速开始

### HTTP 表单登录测试

```bash
authkiller attack \
  --url "http://testsite.com/login.php" \
  --method POST \
  --data "username={user}&password={pass}" \
  --users examples/dictionaries/usernames.txt \
  --passwords examples/dictionaries/passwords.txt \
  --concurrency 20 \
  --success-regex "Login successful"
```

### HTTP Basic Auth 测试

```bash
authkiller attack \
  --url "http://api.example.com/admin" \
  --protocol basic \
  --users examples/dictionaries/usernames.txt \
  --passwords examples/dictionaries/passwords.txt \
  --success-status 200
```

### 从配置文件启动

```bash
authkiller attack --config examples/configs/example.json
```

### 从断点恢复

```bash
authkiller resume --checkpoint checkpoint_20260701_120000.json
```

## 配置示例

```json
{
  "target": {
    "url": "http://example.com/login",
    "method": "POST",
    "headers": {
      "User-Agent": "Mozilla/5.0",
      "Content-Type": "application/x-www-form-urlencoded"
    },
    "body_template": "username={user}&password={pass}"
  },
  "payload": {
    "users_file": "examples/dictionaries/usernames.txt",
    "passwords_file": "examples/dictionaries/passwords.txt",
    "rules": ["uppercase", "append_numbers"]
  },
  "performance": {
    "concurrency": 50,
    "timeout": 10,
    "retry_times": 3,
    "checkpoint_interval": 100
  },
  "detection": {
    "success_pattern": "Welcome|成功",
    "failure_pattern": "Invalid|错误",
    "success_status_codes": [200, 302]
  },
  "defense": {
    "detect_rate_limit": true,
    "auto_throttle": true,
    "throttle_delay": 5
  }
}
```

## 主要功能模块

### 1. 协议层 (`protocols/`)

- `BaseProtocol`: 协议基类，定义统一接口
- `HTTPFormProtocol`: HTTP 表单登录实现
- `HTTPBasicProtocol`: HTTP Basic Auth 实现

### 2. 载荷管理层 (`payload/`)

- `DictionaryManager`: 字典管理，生成器逐行读取
- `RuleEngine`: 规则引擎，密码变异和动态生成

### 3. 核心引擎层 (`core/`)

- `Engine`: 主引擎，协调各模块
- `Attacker`: 攻击执行器，处理单次请求
- `Config`: 配置管理，参数验证

### 4. 状态管理层 (`state/`)

- `CheckpointManager`: 断点续传，定期保存进度
- `SessionManager`: 会话管理，Cookie 和 Token 处理

### 5. 工具层 (`utils/`)

- `Logger`: 日志系统，多级别多目标输出
- `Reporter`: 报告生成，多格式输出
- `DefenseDetector`: 防御机制检测

## 测试与验证

### 运行单元测试

```bash
pytest tests/ -v
```

### 功能验证

- ✅ 字典管理测试：大文件逐行读取是否内存友好
- ✅ 并发测试：并发数控制是否生效
- ✅ 断点续传测试：中断后恢复是否正确
- ✅ 防御检测测试：速率限制检测是否准确

## 防御机制应对

工具内置以下防御检测机制：

- **速率限制检测**：检测 429 状态码，自动降速
- **账户锁定检测**：识别账户锁定提示，跳过锁定账户
- **验证码检测**：检测验证码要求，提示人工介入
- **自动降速**：根据响应时间和错误率自动调整并发数

## 限制说明

当前版本限制：

1. 仅支持 HTTP/HTTPS 协议
2. 不支持需要 JavaScript 渲染的页面
3. 不处理验证码（需要人工介入）
4. 不支持 SOCKS 代理（仅支持 HTTP 代理）

## 后续优化方向

- 扩展协议支持：SSH、FTP、MySQL 等
- GUI 图形界面版本
- Web 界面版本
- 分布式攻击支持
- GPU 加速密码哈希计算

## 许可证

MIT License

**重要：许可证仅授权合法使用，任何非法使用行为将追究法律责任。**

## 联系方式

- 项目主页：<https://github.com/IDrameSkyAbus/authkiller>
- 问题反馈：<https://github.com/IDrameSkyAbus/authkiller/issues>
- 安全建议：<admin@pubnexus.cn>

***

**再次提醒：请确保合法使用本工具，遵守法律法规，尊重他人隐私和系统安全。**
