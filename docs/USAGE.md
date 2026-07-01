# AuthKiller 使用指南

## ⚠️ 重要声明

**本工具仅用于授权安全审计和强度测试！未经授权使用可能违反法律！**

在使用本工具前，请确保：
1. ✅ 已获得目标系统的明确书面授权
2. ✅ 测试行为符合所在国家/地区的法律法规
3. ✅ 测试结果仅用于安全加固，不用于任何恶意目的
4. ✅ 了解并承担使用本工具可能产生的法律责任

---

## 目录

1. [快速开始](#快速开始)
2. [启动方式](#启动方式)
3. [基本使用](#基本使用)
4. [配置详解](#配置详解)
5. [高级功能](#高级功能)
6. [最佳实践](#最佳实践)
7. [常见问题](#常见问题)

---

## 快速开始

### 安装

#### 从源码安装

```bash
# 克隆项目
git clone https://github.com/example/authkiller.git
cd authkiller

# 安装依赖
pip install -r requirements.txt

# 安装工具
pip install -e .
```

#### 验证安装

```bash
authkiller --help
```

---

### 第一次测试

#### HTTP表单登录测试

```bash
authkiller attack \
  --url "http://testsite.com/login.php" \
  --method POST \
  --data "username={user}&password={pass}" \
  --users examples/dictionaries/usernames.txt \
  --passwords examples/dictionaries/passwords.txt \
  --concurrency 20 \
  --success-regex "Login successful|成功"
```

#### HTTP Basic Auth测试

```bash
authkiller attack \
  --url "http://api.example.com/admin" \
  --protocol basic \
  --users examples/dictionaries/usernames.txt \
  --passwords examples/dictionaries/passwords.txt \
  --success-status 200
```

---

## 启动方式

AuthKiller 提供四种使用方式，满足不同场景需求：

### 1. CLI命令行模式

**适用场景**：自动化脚本、批量测试、服务器环境

**特点**：
- ✅ 高效、可编程、适合CI/CD
- ✅ 执行效率高，资源占用低
- ⚠️ 需要记忆命令，操作门槛较高

**启动方式**：
```bash
authkiller <子命令> [选项]
```

**可用子命令**：
- `attack` - 启动新的密码测试任务
- `resume` - 从断点恢复任务
- `report` - 生成测试报告
- `web` - 启动Web界面

**详细说明**：参见 [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md) - CLI命令行模式

---

### 2. Web GUI模式

**适用场景**：交互式测试、实时监控、初学者使用

**特点**：
- ✅ 操作直观易用，实时可视化反馈
- ✅ 支持远程访问，学习成本低
- ⚠️ 不适合批量自动化，需要浏览器环境

**启动方式**：
```bash
authkiller web
```

访问地址：http://127.0.0.1:37496

**详细说明**：参见 [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md) - Web GUI模式

---

### 3. THINKER GUI模式（待实现）

**适用场景**：深度分析、智能测试、可视化报告

**特点**：
- ✅ 智能推荐配置、深度结果分析
- ✅ 可视化图表、优化建议生成
- ❌ 功能待实现，开发进度未知

**预期启动方式**：
```bash
authkiller thinker
```

**详细说明**：参见 [THINKER_GUI_GUIDE.md](THINKER_GUI_GUIDE.md)

---

### 4. API服务模式（待实现）

**适用场景**：系统集成、自动化平台、远程任务管理

**特点**：
- ✅ RESTful接口、易于集成
- ✅ 支持远程调用、异步处理
- ❌ 功能待实现，需要API开发知识

**预期启动方式**：
```bash
authkiller api
```

**详细说明**：参见 [API_SERVICE_GUIDE.md](API_SERVICE_GUIDE.md)

---

### 启动方式对比

| 功能特性 | CLI | Web GUI | THINKER GUI | API服务 |
|---------|-----|---------|-------------|---------|
| **可用状态** | ✅ 已实现 | ✅ 已实现 | ❌ 待实现 | ❌ 待实现 |
| **批量测试** | ✅ | ❌ | ✅ | ✅ |
| **可视化界面** | ❌ | ✅ | ✅ | ❌ |
| **实时监控** | ⚠️ | ✅ | ✅ | ✅ |
| **智能分析** | ❌ | ❌ | ✅ | ❌ |
| **远程访问** | ❌ | ✅ | ✅ | ✅ |
| **自动化集成** | ✅ | ❌ | ❌ | ✅ |
| **易用性** | ⚠️ | ✅ | ✅ | ⚠️ |

### 如何选择启动方式？

根据使用场景选择：

- **自动化脚本** → CLI命令行
- **交互式测试** → Web GUI
- **深度分析** → THINKER GUI（待实现）
- **系统集成** → API服务（待实现）

---

## 基本使用

### 使用配置文件

#### 1. 创建配置文件

创建JSON配置文件 `my_config.json`：

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
    "users_file": "users.txt",
    "passwords_file": "passwords.txt"
  },
  "performance": {
    "concurrency": 30,
    "timeout": 10
  },
  "detection": {
    "success_pattern": "Welcome|成功",
    "failure_pattern": "Invalid|错误",
    "protocol": "http_form"
  }
}
```

#### 2. 运行测试

```bash
authkiller attack --config my_config.json
```

---

### 命令行参数详解

#### attack 子命令

| 参数 | 说明 | 默认值 | 必需 |
|------|------|--------|------|
| `--url, -u` | 目标URL | 无 | ✓ |
| `--method, -m` | HTTP方法（POST/GET） | POST | |
| `--data, -d` | 请求体模板 | 无 | ✓ (POST) |
| `--users` | 用户名字典文件 | 无 | ✓ |
| `--passwords, -p` | 密码字典文件 | 无 | ✓ |
| `--concurrency, -n` | 并发数 | 10 | |
| `--timeout, -t` | 超时时间（秒） | 10 | |
| `--success-regex, -s` | 成功响应正则 | 无 | |
| `--failure-regex, -f` | 失败响应正则 | 无 | |
| `--protocol` | 协议类型（http_form/http_basic） | http_form | |
| `--content-type` | 请求体格式（json/urlencoded/xml） | urlencoded | |
| `--output, -o` | 结果输出文件 | results.json | |
| `--log-level` | 日志级别 | INFO | |

#### 请求体模板占位符

使用 `{user}` 和 `{pass}` 占位符：

```bash
# URL编码格式
--data "username={user}&password={pass}&submit=Login"

# JSON格式（需要--content-type json）
--data '{"user":"{user}","pass":"{pass"}"}'

# XML格式（需要--content-type xml）
--data '<credentials><user>{user}</user><pass>{pass}</pass></credentials>'
```

---

### resume 子命令

从断点恢复任务：

```bash
authkiller resume --checkpoint checkpoints/checkpoint_20260701_120000.json
```

---

### report 子命令

生成报告：

```bash
# JSON格式
authkiller report --input results.json --format json --output report.json

# CSV格式
authkiller report --input results.json --format csv --output report.csv

# TXT格式
authkiller report --input results.json --format txt --output report.txt
```

---

## 配置详解

### target 配置

目标系统配置：

```json
{
  "target": {
    "url": "http://example.com/login",          // 目标URL（必需）
    "method": "POST",                            // HTTP方法
    "headers": {                                 // 自定义Headers
      "User-Agent": "Mozilla/5.0",
      "Referer": "http://example.com",
      "Content-Type": "application/x-www-form-urlencoded"
    },
    "cookies": {                                 // 自定义Cookies
      "session_id": "abc123"
    },
    "body_template": "username={user}&password={pass}",  // 请求体模板
    "content_type": "urlencoded"                 // 请求体格式
  }
}
```

---

### payload 配置

载荷和字典配置：

```json
{
  "payload": {
    "users_file": "users.txt",           // 用户名字典文件（必需）
    "passwords_file": "passwords.txt",   // 密码字典文件（必需）
    "rules": ["uppercase", "append_numbers"],  // 密码变异规则
    "mode": "normal"                     // 测试模式
  }
}
```

**测试模式**：
- `normal` - 标准模式：每个用户名尝试所有密码
- `single_user` - 单用户模式：指定用户尝试所有密码
- `single_password` - 密码喷洒模式：单一密码尝试多个用户名

---

### performance 配置

性能和并发配置：

```json
{
  "performance": {
    "concurrency": 50,           // 并发数（推荐20-100）
    "timeout": 10,               // 单次请求超时时间（秒）
    "retry_times": 3,            // 重试次数
    "checkpoint_interval": 100   // 断点保存间隔（尝试次数）
  }
}
```

**性能建议**：
- **低并发** (10-20)：适合小型目标或网络不稳定
- **中并发** (50)：适合大多数场景
- **高并发** (100+)：适合高性能目标，需监控防御机制

---

### detection 配置

成功判定和协议配置：

```json
{
  "detection": {
    "success_status_codes": [200, 302],    // 成功状态码列表
    "success_pattern": "Welcome|成功",     // 成功响应正则表达式
    "failure_pattern": "Invalid|错误",     // 失败响应正则表达式
    "protocol": "http_form"                // 协议类型
  }
}
```

**成功判定逻辑**：
1. 优先检查失败模式（如果匹配，直接判定失败）
2. 检查成功模式（如果匹配，判定成功）
3. 检查状态码（如果符合，判定成功）

---

### defense 配置

防御机制检测配置：

```json
{
  "defense": {
    "detect_rate_limit": true,      // 启用速率限制检测
    "auto_throttle": true,          // 自动降速
    "throttle_delay": 5,            // 降速等待时间（秒）
    "max_rate_limit_retries": 3     // 最大速率限制重试次数
  }
}
```

**防御检测**：
- **速率限制**：检测429状态码，自动降速
- **账户锁定**：检测锁定提示，跳过锁定账户
- **验证码**：检测验证码要求，暂停任务

---

### output 配置

输出和日志配置：

```json
{
  "output": {
    "log_level": "INFO",           // 日志级别（DEBUG/INFO/WARNING/ERROR）
    "log_file": "authkiller.log",  // 日志文件路径
    "result_file": "results.json", // 结果文件路径
    "checkpoint_dir": "checkpoints" // 断点文件目录
  }
}
```

---

## 高级功能

### 密码规则引擎

#### 可用规则

| 规则名称 | 说明 | 示例 |
|----------|------|------|
| `uppercase` | 大写转换 | admin → ADMIN |
| `lowercase` | 小写转换 | ADMIN → admin |
| `capitalize` | 首字母大写 | admin → Admin |
| `append_numbers` | 添加数字后缀 | admin → admin123, admin1 |
| `prepend_numbers` | 添加数字前缀 | admin → 1admin, 123admin |
| `append_special` | 添加特殊字符 | admin → admin!, admin@ |
| `leet` | Leet字符替换 | password → p4ssw0rd |
| `reverse` | 反转密码 | admin → nimda |
| `user_based` | 用户名组合 | admin + pass → adminpass |
| `date_based` | 日期组合 | admin → admin2025, admin01 |

#### 使用规则

在配置文件中指定规则：

```json
{
  "payload": {
    "rules": ["uppercase", "append_numbers"]
  }
}
```

或使用 `PasswordMutator` 类：

```python
from authkiller.payload.rules import PasswordMutator

mutator = PasswordMutator()
passwords = mutator.mutate_password('admin', ['uppercase', 'append_numbers'])
# 结果: ['admin', 'ADMIN', 'admin1', 'admin123', ...]
```

---

### 断点续传

#### 自动断点保存

工具会定期保存进度到 `checkpoints/` 目录：

```bash
checkpoints/
  ├── checkpoint_20260701_120000.json
  ├── checkpoint_20260701_121000.json
  └── checkpoint_20260701_122000.json
```

#### 手动恢复

```bash
authkiller resume --checkpoint checkpoints/checkpoint_20260701_120000.json
```

#### 断点文件结构

```json
{
  "timestamp": "2026-07-01T12:00:00",
  "tested_combinations": ["admin:password", "root:123456"],
  "current_position": 100,
  "config": {...},
  "results": [...]
}
```

---

### 会话管理

#### Cookie自动提取

工具会自动提取和传递Cookie：

```python
from authkiller.state.session import SessionManager

session_mgr = SessionManager()
cookies = session_mgr.extract_cookies(response)
headers = session_mgr.inject_cookies_to_request(headers)
```

#### CSRF Token处理

自动提取和注入CSRF Token：

```python
token = await session_mgr.extract_csrf_token(response_text)
body_template = session_mgr.inject_token_to_request(body_template)
```

---

### 自定义协议

#### 实现自定义协议

继承 `BaseProtocol` 类：

```python
from authkiller.protocols.base import BaseProtocol

class CustomProtocol(BaseProtocol):
    async def test_credential(self, username: str, password: str) -> bool:
        # 实现自定义认证逻辑
        pass

    def parse_response(self, response) -> dict:
        # 解析响应
        pass

    def is_success(self, response_data: dict) -> bool:
        # 判断成功
        pass
```

---

## 最佳实践

### 1. 合理设置并发数

- **起始并发**：建议从20开始
- **观察响应**：监控响应时间和错误率
- **逐步调整**：如果稳定，可增加到50-100
- **遇到防御**：立即降速到10-20

---

### 2. 准备高质量字典

#### 用户名字典

```
admin
administrator
root
user
test
guest
manager
support
sysadmin
webmaster
```

#### 密码字典

```
admin
password
123456
qwerty
letmein
welcome
P@ssw0rd
Admin123!
```

#### 使用规则扩展字典

```json
{
  "rules": ["uppercase", "append_numbers", "leet"]
}
```

---

### 3. 精确的成功判定

#### 多层判定

```json
{
  "detection": {
    "success_status_codes": [200, 302],
    "success_pattern": "Dashboard|欢迎|Welcome",
    "failure_pattern": "Invalid|错误|Failed|Incorrect"
  }
}
```

#### 测试判定逻辑

先手动测试一个已知凭证，观察响应：

```bash
curl -X POST http://example.com/login \
  -d "username=admin&password=admin123" \
  -v
```

根据响应调整判定规则。

---

### 4. 监控防御机制

#### 常见防御触发

| 状态码 | 含义 | 应对 |
|--------|------|------|
| 429 | 速率限制 | 立即降速，等待60秒 |
| 403 | 禁止访问 | 检查账户锁定提示 |
| 401 | 认证失败 | 继续尝试 |

#### 启用防御检测

```json
{
  "defense": {
    "detect_rate_limit": true,
    "auto_throttle": true
  }
}
```

---

### 5. 定期保存断点

```json
{
  "performance": {
    "checkpoint_interval": 50  // 每50次尝试保存一次
  }
}
```

**建议**：
- 小字典（<1000组合）：interval=100
- 中字典（1000-10000）：interval=50
- 大字典（>10000）：interval=10

---

## 常见问题

### Q1: 如何测试HTTPS站点？

**答**: 直接使用HTTPS URL，工具会自动处理SSL：

```bash
authkiller attack --url "https://example.com/login"
```

---

### Q2: 如何处理需要CSRF Token的登录？

**答**: 使用会话管理功能：

```json
{
  "target": {
    "url": "http://example.com/login",
    "method": "POST",
    "body_template": "username={user}&password={pass}&csrf_token={token}"
  }
}
```

工具会自动提取和注入Token。

---

### Q3: 遇到验证码怎么办？

**答**: 验证码无法自动处理，工具会检测并暂停：

```
[WARNING] 检测到验证码，暂停任务
建议：人工处理验证码后继续
```

建议：
- 降低测试频率
- 使用代理IP轮换
- 联系系统管理员获取测试白名单

---

### Q4: 如何测试不同的用户角色？

**答**: 为不同角色创建不同字典：

```bash
# 测试管理员账户
authkiller attack --users admins.txt --passwords passwords.txt

# 测试普通用户
authkiller attack --users users.txt --passwords passwords.txt
```

---

### Q5: 内存占用过大怎么办？

**答**: 工具使用生成器逐行读取字典，内存占用恒定：

```python
# 即使百万级字典，内存也不会增长
def load_users():
    with open('huge_users.txt') as f:
        for line in f:
            yield line.strip()
```

如果仍有问题，检查：
- 并发数是否过高
- 是否有其他进程占用内存

---

### Q6: 如何生成测试报告？

**答**: 使用report子命令：

```bash
# 完整JSON报告
authkiller report --input results.json --format json --output report.json

# CSV报告（便于分析）
authkiller report --input results.json --format csv --output report.csv

# 文本报告（便于阅读）
authkiller report --input results.json --format txt --output report.txt
```

---

### Q7: 如何避免账户锁定？

**答**:

1. **使用密码喷洒模式**：

```json
{
  "payload": {
    "mode": "single_password"
  }
}
```

2. **降低并发数**：

```json
{
  "performance": {
    "concurrency": 5
  }
}
```

3. **增加延迟**：

```python
# 在engine.py中添加延迟
await asyncio.sleep(2)  # 每次尝试间隔2秒
```

---

### Q8: 如何调试配置？

**答**: 使用DEBUG日志级别：

```bash
authkiller attack --config config.json --log-level DEBUG
```

检查日志输出：
```
[DEBUG] 配置验证通过
[DEBUG] 字典加载完成：用户数=20, 密码数=30
[DEBUG] 开始测试：admin:password
[DEBUG] 响应状态码：200
[DEBUG] 响应匹配成功模式：Welcome
```

---

## 技术支持

- **问题反馈**：https://github.com/example/authkiller/issues
- **安全建议**：security@example.com
- **文档更新**：查看项目Wiki

---

**再次提醒：请确保合法使用本工具，遵守法律法规，尊重他人隐私和系统安全！**