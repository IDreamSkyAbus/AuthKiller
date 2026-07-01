# AuthKiller 启动器使用指南

## ⚠️ 重要声明

**本工具仅用于授权安全审计和强度测试！未经授权使用可能违反法律！**

在使用本工具前，请确保：
1. ✅ 已获得目标系统的明确书面授权
2. ✅ 测试行为符合所在国家/地区的法律法规
3. ✅ 测试结果仅用于安全加固，不用于任何恶意目的
4. ✅ 了解并承担使用本工具可能产生的法律责任

---

## 目录

1. [启动器概述](#启动器概述)
2. [CLI命令行模式](#cli命令行模式)
3. [Web GUI模式](#web-gui模式)
4. [THINKER GUI模式（待实现）](#thinker-gui模式待实现)
5. [API服务模式（待实现）](#api服务模式待实现)
6. [启动方式对比](#启动方式对比)
7. [常见问题](#常见问题)

---

## 启动器概述

AuthKiller 提供四种使用方式，满足不同场景需求：

| 模式 | 适用场景 | 特点 |
|------|----------|------|
| **CLI命令行** | 自动化脚本、批量测试 | 高效、可编程、适合CI/CD |
| **Web GUI** | 交互式测试、实时监控 | 可视化、易操作、实时反馈 |
| **THINKER GUI** | 深度分析、智能测试 | 智能推荐、深度分析（待实现） |
| **API服务** | 集成到其他系统 | RESTful接口、易于集成（待实现） |

---

## CLI命令行模式

### 基本语法

```bash
authkiller <子命令> [选项]
```

### 可用子命令

- `attack` - 启动新的密码测试任务
- `resume` - 从断点恢复任务
- `report` - 生成测试报告
- `web` - 启动Web界面
- `help` - 显示帮助信息

---

### 1. attack 子命令

启动新的密码测试任务。

#### 基本用法

```bash
authkiller attack [选项]
```

#### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--url, -u` | 目标URL | `http://example.com/login` |
| `--users` | 用户名字典文件 | `users.txt` |
| `--passwords, -p` | 密码字典文件 | `passwords.txt` |

#### 可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--method, -m` | HTTP方法 | POST |
| `--data, -d` | 请求体模板 | `username={user}&password={pass}` |
| `--concurrency, -n` | 并发数 | 10 |
| `--timeout, -t` | 超时时间（秒） | 10 |
| `--success-regex, -s` | 成功响应正则 | 无 |
| `--failure-regex, -f` | 失败响应正则 | 无 |
| `--protocol` | 协议类型 | http_form |
| `--content-type` | 请求体格式 | urlencoded |
| `--output, -o` | 结果输出文件 | results.json |
| `--log-level` | 日志级别 | INFO |
| `--config, -c` | 配置文件路径 | 无 |
| `--no-progress` | 禁用进度条 | false |

#### 使用示例

##### 快速测试（HTTP表单）

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

##### HTTP Basic Auth测试

```bash
authkiller attack \
  --url "http://api.example.com/admin" \
  --protocol http_basic \
  --users examples/dictionaries/usernames.txt \
  --passwords examples/dictionaries/passwords.txt \
  --concurrency 10 \
  --timeout 15
```

##### 使用配置文件

```bash
authkiller attack --config examples/configs/example.json
```

##### JSON格式请求体

```bash
authkiller attack \
  --url "http://api.example.com/auth" \
  --method POST \
  --content-type json \
  --data '{"username":"{user}","password":"{pass}"}' \
  --users users.txt \
  --passwords passwords.txt \
  --success-regex '"success":true'
```

##### 高并发测试

```bash
authkiller attack \
  --url "http://example.com/login" \
  --users large_users.txt \
  --passwords large_passwords.txt \
  --concurrency 50 \
  --timeout 20 \
  --output results_20260701.json \
  --log-level DEBUG
```

---

### 2. resume 子命令

从断点恢复中断的任务。

#### 基本用法

```bash
authkiller resume --checkpoint <断点文件路径>
```

#### 参数说明

| 参数 | 说明 | 必需 |
|------|------|------|
| `--checkpoint, -c` | 断点文件路径 | ✓ |
| `--output, -o` | 结果输出文件 | 否（默认：results.json） |

#### 使用示例

##### 从最新断点恢复

```bash
# 找到最新的断点文件
ls checkpoints/

# 恢复任务
authkiller resume --checkpoint checkpoints/checkpoint_20260701_120000.json
```

##### 指定输出文件

```bash
authkiller resume \
  --checkpoint checkpoints/checkpoint_20260701_120000.json \
  --output recovered_results.json
```

#### 断点文件说明

断点文件存储在 `checkpoints/` 目录，文件名格式：
```
checkpoint_YYYYMMDD_HHMMSS.json
```

断点文件包含：
- 已测试的组合集合
- 当前测试位置
- 原始配置
- 已发现的成功凭证

---

### 3. report 子命令

生成测试报告。

#### 基本用法

```bash
authkiller report --input <结果文件> --format <格式> --output <输出文件>
```

#### 参数说明

| 参数 | 说明 | 必需 |
|------|------|------|
| `--input, -i` | 输入结果文件（JSON） | ✓ |
| `--format` | 报告格式（json/csv/txt） | ✓ |
| `--output, -o` | 输出报告文件 | ✓ |

#### 使用示例

##### JSON格式报告

```bash
authkiller report \
  --input results.json \
  --format json \
  --output report.json
```

##### CSV格式报告（便于Excel分析）

```bash
authkiller report \
  --input results.json \
  --format csv \
  --output report.csv
```

##### TXT格式报告（便于阅读）

```bash
authkiller report \
  --input results.json \
  --format txt \
  --output report.txt
```

---

### 4. web 子命令

启动Web GUI界面。

#### 基本用法

```bash
authkiller web [选项]
```

#### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host` | Web服务主机地址 | 127.0.0.1 |
| `--port, -p` | Web服务端口 | 37496 |
| `--debug` | 启用调试模式 | false |
| `--no-auto-port` | 禁用端口自动检测 | false |

#### 使用示例

##### 默认启动

```bash
authkiller web
```

访问地址：
- 本地：http://127.0.0.1:37496
- 局域网：http://<本机IP>:37496

##### 自定义端口

```bash
authkiller web --port 8080
```

##### 允许外部访问

```bash
authkiller web --host 0.0.0.0 --port 8080
```

##### 调试模式

```bash
authkiller web --debug
```

---

### 5. 查看帮助

#### 主命令帮助

```bash
authkiller --help
authkiller -h
```

#### 子命令帮助

```bash
authkiller attack --help
authkiller resume --help
authkiller report --help
authkiller web --help
```

---

## Web GUI模式

### 启动Web界面

#### 方式1：使用CLI命令

```bash
authkiller web
```

#### 方式2：直接运行Web模块

```bash
python -m authkiller.web.app
```

#### 方式3：使用Python脚本

```python
from authkiller.web.app import run_web

run_web(host='127.0.0.1', port=37496, debug=False)
```

---

### Web界面功能

#### 1. 配置管理

- **加载配置**：从JSON文件加载配置
- **保存配置**：将当前配置保存为JSON文件
- **手动配置**：填写表单配置测试参数

#### 2. 任务控制

- **启动测试**：配置完成后启动测试任务
- **暂停测试**：暂停正在运行的任务
- **恢复测试**：恢复暂停的任务
- **停止测试**：终止正在运行的任务

#### 3. 实时监控

- **进度条**：实时显示测试进度百分比
- **统计数据**：
  - 总组合数
  - 已测试数
  - 成功数
  - 失败数
- **时间信息**：
  - 开始时间
  - 预计完成时间

#### 4. 结果展示

- **实时日志**：滚动显示测试日志
- **结果表格**：分页显示测试结果
- **导出功能**：导出JSON格式结果

---

### Web界面使用流程

#### 步骤1：启动Web服务

```bash
authkiller web
```

浏览器访问：http://127.0.0.1:37496

#### 步骤2：配置测试参数

填写左侧配置表单：
- 目标URL
- 协议类型（HTTP表单 / HTTP Basic Auth）
- 用户字典路径
- 密码字典路径
- 并发数
- 超时时间
- 成功/失败标识

#### 步骤3：启动测试

点击 **"启动测试"** 按钮

#### 步骤4：监控进度

观察右侧面板：
- 进度条更新
- 统计数据变化
- 实时日志滚动

#### 步骤5：查看结果

底部结果表格实时更新：
- 成功凭证高亮显示
- 分页浏览所有结果

#### 步骤6：导出结果

点击 **"导出结果"** 按钮，下载JSON文件

---

### Web界面截图说明

#### 界面布局

```
┌─────────────────────────────────────────────────┐
│  AuthKiller Web GUI                              │
├──────────────────┬──────────────────────────────┤
│  测试配置         │  任务控制                     │
│  - 目标URL       │  [启动] [暂停] [停止] [恢复] │
│  - 协议类型      │                              │
│  - 字典文件      │  进度: 45%                   │
│  - 并发/超时     │  总数: 1000  已测: 450      │
│  - 成功/失败标识 │  成功: 5    失败: 445       │
│                  │                              │
│  [加载配置]      │  实时日志                    │
│  [保存配置]      │  [12:00:01] 任务已启动      │
│                  │  [12:00:02] 测试 admin:123  │
├──────────────────┴──────────────────────────────┤
│  测试结果 (总数: 5)                    [导出]    │
│  ┌──────┬──────┬──────┬──────────┬──────────┐  │
│  │用户名│密码  │状态  │响应时间  │测试时间  │  │
│  ├──────┼──────┼──────┼──────────┼──────────┤  │
│  │admin │123456│成功  │150ms     │12:00:05  │  │
│  └──────┴──────┴──────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────┘
```

---

## THINKER GUI模式（待实现）

### 功能概述

THINKER GUI 是计划中的智能测试界面，将提供以下功能：

- 🧠 **智能字典推荐**：根据目标系统特征推荐字典
- 📊 **深度分析**：分析测试结果，提供优化建议
- 🔍 **模式识别**：识别防御机制，自动调整策略
- 📈 **可视化报告**：生成图表化测试报告
- 🎯 **精准定位**：缩小测试范围，提高效率

### 启动方式（待实现）

```bash
authkiller thinker
```

或

```bash
authkiller thinker --port 5000
```

### 访问地址（待实现）

- 本地：http://127.0.0.1:5000

### 预期功能（待实现）

#### 1. 智能配置向导

- 目标系统识别
- 自动配置推荐
- 协议自动检测

#### 2. 智能测试策略

- 动态字典优化
- 自适应并发调整
- 防御机制智能应对

#### 3. 结果深度分析

- 成功模式分析
- 失败原因统计
- 优化建议生成

#### 4. 可视化图表

- 测试进度曲线图
- 成功/失败分布图
- 时间消耗分析图

### 开发进度

当前状态：**规划阶段**

预计功能：
- [ ] 智能字典推荐
- [ ] 自动配置检测
- [ ] 可视化图表
- [ ] 深度分析报告
- [ ] 机器学习优化

---

## API服务模式（待实现）

### 功能概述

API服务模式提供RESTful接口，便于集成到其他系统：

- 🔗 **RESTful API**：标准化接口设计
- 🔌 **易于集成**：可集成到自动化平台
- 📡 **远程调用**：支持远程任务管理
- 🔄 **异步处理**：后台任务执行

### 启动方式（待实现）

```bash
authkiller api
```

或

```bash
authkiller api --port 8000 --host 0.0.0.0
```

### 预期API接口（待实现）

#### 任务管理接口

```http
POST /api/v1/task/start
GET  /api/v1/task/status
POST /api/v1/task/stop
POST /api/v1/task/pause
POST /api/v1/task/resume
```

#### 配置管理接口

```http
POST /api/v1/config/create
GET  /api/v1/config/{id}
PUT  /api/v1/config/{id}
DELETE /api/v1/config/{id}
```

#### 结果查询接口

```http
GET /api/v1/results/{task_id}
GET /api/v1/results/{task_id}/export?format=json
```

### 使用示例（待实现）

#### 启动测试任务

```bash
curl -X POST http://localhost:8000/api/v1/task/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "http://example.com/login",
    "users_file": "users.txt",
    "passwords_file": "passwords.txt",
    "concurrency": 20
  }'
```

#### 查询任务状态

```bash
curl http://localhost:8000/api/v1/task/status
```

#### 获取测试结果

```bash
curl http://localhost:8000/api/v1/results/task_123
```

### 开发进度

当前状态：**规划阶段**

预计功能：
- [ ] RESTful API接口
- [ ] 任务管理API
- [ ] 配置管理API
- [ ] 结果查询API
- [ ] API文档（Swagger）

---

## 启动方式对比

### 功能对比表

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

### 适用场景推荐

#### CLI命令行

**推荐场景**：
- 自动化脚本和批处理
- CI/CD流水线集成
- 定时任务和计划任务
- 无图形界面环境（服务器）
- 高级用户快速操作

**优势**：
- 执行效率高
- 可编程控制
- 输出易于解析
- 资源占用低

**劣势**：
- 需要记忆命令
- 无可视化界面
- 操作门槛较高

---

#### Web GUI

**推荐场景**：
- 交互式测试操作
- 实时监控和调试
- 初次使用和学习
- 需要实时反馈的场景
- 远程访问测试

**优势**：
- 操作直观易用
- 实时可视化反馈
- 支持远程访问
- 学习成本低

**劣势**：
- 不适合批量自动化
- 需要浏览器环境
- 资源占用略高

---

#### THINKER GUI（待实现）

**推荐场景**：
- 深度分析和优化
- 智能测试策略
- 可视化报告生成
- 复杂目标的测试

**优势**：
- 智能推荐配置
- 深度结果分析
- 可视化图表
- 优化建议生成

**劣势**：
- 功能待实现
- 开发进度未知

---

#### API服务（待实现）

**推荐场景**：
- 集成到其他系统
- 自动化平台集成
- 远程任务管理
- 分布式测试

**优势**：
- 标准化接口
- 易于集成
- 支持远程调用
- 异步处理

**劣势**：
- 功能待实现
- 需要API开发知识

---

## 常见问题

### Q1: 如何选择启动方式？

**答**：根据使用场景选择：

- **自动化脚本** → CLI命令行
- **交互式测试** → Web GUI
- **深度分析** → THINKER GUI（待实现）
- **系统集成** → API服务（待实现）

---

### Q2: CLI和Web GUI可以同时使用吗？

**答**：可以，但需注意：

- CLI和Web GUI独立运行
- 同时测试同一目标会相互干扰
- 建议分时使用或测试不同目标

---

### Q3: Web GUI端口被占用怎么办？

**答**：有两种解决方式：

#### 方式1：使用自动端口检测（默认启用）

```bash
authkiller web
# 系统会自动寻找可用端口
```

#### 方式2：手动指定端口

```bash
authkiller web --port 8080
```

---

### Q4: 如何在服务器上使用Web GUI？

**答**：允许外部访问：

```bash
authkiller web --host 0.0.0.0 --port 8080
```

访问地址：http://服务器IP:8080

**安全提示**：
- 仅在可信网络中使用
- 建议配置防火墙规则
- 避免在公网直接暴露

---

### Q5: CLI命令如何查看详细日志？

**答**：使用DEBUG级别：

```bash
authkiller attack --config config.json --log-level DEBUG
```

日志输出示例：
```
[DEBUG] 配置验证通过
[DEBUG] 字典加载完成：用户数=20, 密码数=30
[DEBUG] 开始测试：admin:password
[DEBUG] 响应状态码：200
[DEBUG] 响应匹配成功模式：Welcome
```

---

### Q6: 如何停止正在运行的CLI任务？

**答**：按 `Ctrl+C` 中断：

```
^C
[WARNING] 用户中断任务
[INFO] 断点已保存: checkpoints/checkpoint_20260701_120000.json
```

中断后可使用 `resume` 恢复。

---

### Q7: Web GUI的任务如何持久化？

**答**：当前版本限制：

- Web GUI任务状态在内存中
- 页面刷新会丢失状态
- 建议定期导出结果

**改进计划**：
- 后续版本将支持数据库持久化
- 支持会话恢复

---

### Q8: THINKER GUI何时可用？

**答**：THINKER GUI正在规划中：

- 预计功能：智能分析、可视化图表
- 开发优先级：中等
- 发布时间：待定

关注项目更新获取进度。

---

### Q9: API服务何时可用？

**答**：API服务正在规划中：

- 预计功能：RESTful接口、远程管理
- 开发优先级：高
- 发布时间：待定

关注项目更新获取进度。

---

### Q10: 如何在脚本中调用AuthKiller？

**答**：使用Python API：

```python
import asyncio
from authkiller.core.config import ConfigManager
from authkiller.core.engine import AttackEngine

async def run_test():
    # 创建配置
    config = ConfigManager('config.json')

    # 创建引擎
    engine = AttackEngine(config)

    # 运行测试
    stats = await engine.run()

    # 输出结果
    print(f"成功率: {stats['success_rate']}")

asyncio.run(run_test())
```

详见 `docs/API.md`。

---

## 技术支持

- **项目主页**：https://github.com/example/authkiller
- **问题反馈**：https://github.com/example/authkiller/issues
- **文档更新**：查看项目Wiki

---

**再次提醒：请确保合法使用本工具，遵守法律法规，尊重他人隐私和系统安全！**