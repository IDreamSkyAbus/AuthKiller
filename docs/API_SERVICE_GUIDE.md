# AuthKiller API 服务使用指南

## ⚠️ 重要声明

**本工具仅用于授权安全审计和强度测试！未经授权使用可能违反法律！**

在使用本工具前，请确保：
1. ✅ 已获得目标系统的明确书面授权
2. ✅ 测试行为符合所在国家/地区的法律法规
3. ✅ 测试结果仅用于安全加固，不用于任何恶意目的
4. ✅ 了解并承担使用本工具可能产生的法律责任

---

## 功能概述

API服务模式提供RESTful接口，便于集成到自动化平台和其他系统。

### 核心特性

- 🔗 **RESTful API**：标准化接口设计，易于使用
- 🔌 **易于集成**：可集成到自动化平台、CI/CD系统
- 📡 **远程调用**：支持远程任务管理和监控
- 🔄 **异步处理**：后台任务执行，不阻塞调用方
- 📊 **状态查询**：实时查询任务状态和进度
- 🔐 **认证授权**：API密钥认证，确保安全性

---

## 开发状态

**当前状态**：🚧 **规划阶段 - 待实现**

本功能正在积极规划中，预计将包含以下模块：

### 规划功能列表

#### 第一阶段（核心API）

- [ ] **任务管理API**
  - 启动测试任务
  - 停止/暂停/恢复任务
  - 查询任务状态

- [ ] **配置管理API**
  - 创建/更新/删除配置
  - 配置验证
  - 配置模板

- [ ] **结果查询API**
  - 实时结果查询
  - 结果导出
  - 结果统计

#### 第二阶段（高级API）

- [ ] **认证授权**
  - API密钥管理
  - 权限控制
  - 访问日志

- [ ] **批量操作**
  - 批量任务提交
  - 任务队列管理
  - 任务优先级

- [ ] **通知回调**
  - Webhook通知
  - 任务完成通知
  - 错误告警

#### 第三阶段（集成增强）

- [ ] **SDK开发**
  - Python SDK
  - JavaScript SDK
  - Go SDK

- [ ] **API文档**
  - Swagger文档
  - Postman集合
  - 示例代码

- [ ] **监控统计**
  - API调用统计
  - 性能监控
  - 错误率统计

---

## API架构设计

### RESTful API设计原则

- **资源导向**：每个URL代表一种资源
- **统一接口**：使用标准HTTP方法（GET、POST、PUT、DELETE）
- **无状态**：每个请求包含所有必要信息
- **可缓存**：支持响应缓存
- **分层系统**：支持中间层（代理、负载均衡）

### API版本管理

- **版本前缀**：`/api/v1/`
- **向后兼容**：新版本不影响旧版本
- **版本废弃**：提前通知旧版本废弃时间

---

## 预期API接口

### 1. 任务管理接口

#### 启动测试任务

```http
POST /api/v1/task/start
```

**请求体**：
```json
{
  "config": {
    "target_url": "http://example.com/login",
    "protocol": "http_form",
    "users_file": "users.txt",
    "passwords_file": "passwords.txt",
    "concurrency": 20,
    "timeout": 30,
    "success_pattern": "Welcome|成功",
    "failure_pattern": "Invalid|错误"
  },
  "options": {
    "auto_save_checkpoint": true,
    "checkpoint_interval": 100,
    "callback_url": "http://your-server/callback"
  }
}
```

**响应**：
```json
{
  "success": true,
  "task_id": "task_20260701_120000",
  "message": "任务已启动",
  "estimated_duration": "约15分钟"
}
```

---

#### 查询任务状态

```http
GET /api/v1/task/status?task_id={task_id}
```

**响应**：
```json
{
  "success": true,
  "task_id": "task_20260701_120000",
  "status": {
    "state": "running",  // running | paused | stopped | completed | failed
    "progress": {
      "total": 1000,
      "tested": 450,
      "success": 5,
      "failed": 445,
      "percentage": 45.0
    },
    "start_time": "2026-07-01T12:00:00",
    "estimated_end_time": "2026-07-01T12:15:00",
    "elapsed_time": "7分30秒"
  }
}
```

---

#### 停止任务

```http
POST /api/v1/task/stop
```

**请求体**：
```json
{
  "task_id": "task_20260701_120000"
}
```

**响应**：
```json
{
  "success": true,
  "task_id": "task_20260701_120000",
  "message": "任务已停止",
  "checkpoint_saved": true,
  "checkpoint_file": "checkpoints/checkpoint_20260701_120730.json"
}
```

---

#### 暂停任务

```http
POST /api/v1/task/pause
```

**请求体**：
```json
{
  "task_id": "task_20260701_120000"
}
```

**响应**：
```json
{
  "success": true,
  "task_id": "task_20260701_120000",
  "message": "任务已暂停",
  "current_progress": "45%"
}
```

---

#### 恢复任务

```http
POST /api/v1/task/resume
```

**请求体**：
```json
{
  "task_id": "task_20260701_120000"
}
```

**响应**：
```json
{
  "success": true,
  "task_id": "task_20260701_120000",
  "message": "任务已恢复"
}
```

---

### 2. 配置管理接口

#### 创建配置

```http
POST /api/v1/config/create
```

**请求体**：
```json
{
  "name": "my_config",
  "config": {
    "target_url": "http://example.com/login",
    "protocol": "http_form",
    "users_file": "users.txt",
    "passwords_file": "passwords.txt",
    "concurrency": 20
  }
}
```

**响应**：
```json
{
  "success": true,
  "config_id": "config_001",
  "name": "my_config",
  "message": "配置已创建"
}
```

---

#### 获取配置

```http
GET /api/v1/config/{config_id}
```

**响应**：
```json
{
  "success": true,
  "config_id": "config_001",
  "name": "my_config",
  "config": {
    "target_url": "http://example.com/login",
    "protocol": "http_form",
    "users_file": "users.txt",
    "passwords_file": "passwords.txt",
    "concurrency": 20
  },
  "created_at": "2026-07-01T10:00:00",
  "updated_at": "2026-07-01T11:00:00"
}
```

---

#### 更新配置

```http
PUT /api/v1/config/{config_id}
```

**请求体**：
```json
{
  "config": {
    "target_url": "http://example.com/login",
    "protocol": "http_form",
    "users_file": "users.txt",
    "passwords_file": "passwords.txt",
    "concurrency": 30  // 修改并发数
  }
}
```

**响应**：
```json
{
  "success": true,
  "config_id": "config_001",
  "message": "配置已更新"
}
```

---

#### 删除配置

```http
DELETE /api/v1/config/{config_id}
```

**响应**：
```json
{
  "success": true,
  "config_id": "config_001",
  "message": "配置已删除"
}
```

---

#### 配置列表

```http
GET /api/v1/config/list
```

**响应**：
```json
{
  "success": true,
  "configs": [
    {
      "config_id": "config_001",
      "name": "my_config",
      "created_at": "2026-07-01T10:00:00"
    },
    {
      "config_id": "config_002",
      "name": "test_config",
      "created_at": "2026-07-01T11:00:00"
    }
  ],
  "total": 2
}
```

---

### 3. 结果查询接口

#### 获取测试结果

```http
GET /api/v1/results/{task_id}
```

**响应**：
```json
{
  "success": true,
  "task_id": "task_20260701_120000",
  "results": [
    {
      "username": "admin",
      "password": "password123",
      "success": true,
      "response_time": 150,
      "timestamp": "2026-07-01T12:05:00",
      "details": {
        "status_code": 200,
        "response_length": 1024
      }
    }
  ],
  "total": 5,
  "success_count": 1,
  "failed_count": 4
}
```

---

#### 分页查询结果

```http
GET /api/v1/results/{task_id}?page=1&per_page=50
```

**响应**：
```json
{
  "success": true,
  "task_id": "task_20260701_120000",
  "results": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_pages": 10,
    "total_results": 500
  }
}
```

---

#### 导出结果

```http
GET /api/v1/results/{task_id}/export?format=json
```

**支持的格式**：
- `json` - JSON格式
- `csv` - CSV格式
- `txt` - TXT格式

**响应**：
```json
{
  "success": true,
  "download_url": "/api/v1/download/results_task_20260701_120000.json",
  "format": "json",
  "expires_at": "2026-07-02T12:00:00"
}
```

---

#### 结果统计

```http
GET /api/v1/results/{task_id}/statistics
```

**响应**：
```json
{
  "success": true,
  "task_id": "task_20260701_120000",
  "statistics": {
    "total_attempts": 1000,
    "success_count": 5,
    "failed_count": 995,
    "success_rate": 0.5,
    "average_response_time": 180,
    "total_time": "15分30秒",
    "success_patterns": [
      {
        "pattern": "admin:*",
        "count": 3,
        "percentage": 60
      }
    ],
    "failure_reasons": [
      {
        "reason": "密码错误",
        "count": 850,
        "percentage": 85
      }
    ]
  }
}
```

---

### 4. 系统管理接口

#### 系统状态

```http
GET /api/v1/system/status
```

**响应**：
```json
{
  "success": true,
  "status": {
    "version": "1.0.0",
    "uptime": "5天12小时",
    "active_tasks": 2,
    "completed_tasks": 15,
    "cpu_usage": 45.2,
    "memory_usage": 62.5,
    "disk_usage": 30.8
  }
}
```

---

#### API密钥管理

```http
POST /api/v1/auth/key/create
```

**请求体**：
```json
{
  "name": "my_api_key",
  "permissions": ["task:start", "task:status", "results:get"],
  "expires_at": "2026-12-31T23:59:59"
}
```

**响应**：
```json
{
  "success": true,
  "key_id": "key_001",
  "api_key": "ak_live_xxxxxxxxxxxxxxxxxxxx",
  "name": "my_api_key",
  "message": "API密钥已创建，请妥善保管"
}
```

---

#### API密钥列表

```http
GET /api/v1/auth/key/list
```

**响应**：
```json
{
  "success": true,
  "keys": [
    {
      "key_id": "key_001",
      "name": "my_api_key",
      "created_at": "2026-07-01T10:00:00",
      "expires_at": "2026-12-31T23:59:59",
      "last_used": "2026-07-01T12:00:00"
    }
  ],
  "total": 1
}
```

---

#### 删除API密钥

```http
DELETE /api/v1/auth/key/{key_id}
```

**响应**：
```json
{
  "success": true,
  "key_id": "key_001",
  "message": "API密钥已删除"
}
```

---

### 5. Webhook通知接口

#### 注册Webhook

```http
POST /api/v1/webhook/register
```

**请求体**：
```json
{
  "url": "http://your-server.com/webhook",
  "events": [
    "task.started",
    "task.completed",
    "task.failed",
    "result.found"
  ],
  "secret": "your_webhook_secret"
}
```

**响应**：
```json
{
  "success": true,
  "webhook_id": "webhook_001",
  "message": "Webhook已注册"
}
```

---

#### Webhook事件类型

| 事件 | 说明 | 触发时机 |
|------|------|----------|
| `task.started` | 任务启动 | 任务开始执行时 |
| `task.completed` | 任务完成 | 任务成功完成时 |
| `task.failed` | 任务失败 | 任务执行失败时 |
| `task.paused` | 任务暂停 | 任务暂停时 |
| `task.resumed` | 任务恢复 | 任务恢复时 |
| `result.found` | 发现成功凭证 | 发现有效凭证时 |
| `progress.update` | 进度更新 | 进度达到特定百分比时 |

---

#### Webhook回调示例

**发送到您的服务器**：
```json
{
  "event": "task.completed",
  "task_id": "task_20260701_120000",
  "timestamp": "2026-07-01T12:15:00",
  "data": {
    "total_attempts": 1000,
    "success_count": 5,
    "failed_count": 995,
    "elapsed_time": "15分30秒"
  },
  "signature": "sha256=xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

---

## 使用示例

### Python调用示例（预期）

#### 使用requests库

```python
import requests
import json

# API配置
API_BASE = "http://localhost:8000/api/v1"
API_KEY = "ak_live_xxxxxxxxxxxxxxxxxxxx"

# 请求头
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 启动任务
def start_task(config):
    url = f"{API_BASE}/task/start"
    payload = {"config": config}

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    if result['success']:
        return result['task_id']
    else:
        raise Exception(result['message'])

# 查询任务状态
def get_task_status(task_id):
    url = f"{API_BASE}/task/status?task_id={task_id}"

    response = requests.get(url, headers=headers)
    result = response.json()

    return result['status']

# 获取结果
def get_results(task_id):
    url = f"{API_BASE}/results/{task_id}"

    response = requests.get(url, headers=headers)
    result = response.json()

    return result['results']

# 使用示例
config = {
    "target_url": "http://example.com/login",
    "protocol": "http_form",
    "users_file": "users.txt",
    "passwords_file": "passwords.txt",
    "concurrency": 20
}

# 启动任务
task_id = start_task(config)
print(f"任务已启动: {task_id}")

# 监控进度
import time
while True:
    status = get_task_status(task_id)
    print(f"进度: {status['progress']['percentage']}%")

    if status['state'] == 'completed':
        break

    time.sleep(5)

# 获取结果
results = get_results(task_id)
print(f"成功凭证: {len(results)}")

for result in results:
    if result['success']:
        print(f"{result['username']} : {result['password']}")
```

---

#### 使用SDK（预期）

```python
from authkiller_sdk import AuthKillerClient

# 创建客户端
client = AuthKillerClient(
    api_key="ak_live_xxxxxxxxxxxxxxxxxxxx",
    base_url="http://localhost:8000/api/v1"
)

# 启动任务
task = client.task.start(
    target_url="http://example.com/login",
    protocol="http_form",
    users_file="users.txt",
    passwords_file="passwords.txt",
    concurrency=20
)

print(f"任务ID: {task.id}")

# 等待完成
task.wait_for_completion()

# 获取结果
results = task.get_results()

for result in results:
    if result.success:
        print(f"{result.username} : {result.password}")
```

---

### JavaScript调用示例（预期）

#### 使用fetch API

```javascript
// API配置
const API_BASE = 'http://localhost:8000/api/v1';
const API_KEY = 'ak_live_xxxxxxxxxxxxxxxxxxxx';

// 请求头
const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// 启动任务
async function startTask(config) {
  const response = await fetch(`${API_BASE}/task/start`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({ config: config })
  });

  const result = await response.json();

  if (result.success) {
    return result.task_id;
  } else {
    throw new Error(result.message);
  }
}

// 查询任务状态
async function getTaskStatus(taskId) {
  const response = await fetch(`${API_BASE}/task/status?task_id=${taskId}`, {
    method: 'GET',
    headers: headers
  });

  const result = await response.json();

  return result.status;
}

// 获取结果
async function getResults(taskId) {
  const response = await fetch(`${API_BASE}/results/${taskId}`, {
    method: 'GET',
    headers: headers
  });

  const result = await response.json();

  return result.results;
}

// 使用示例
const config = {
  target_url: 'http://example.com/login',
  protocol: 'http_form',
  users_file: 'users.txt',
  passwords_file: 'passwords.txt',
  concurrency: 20
};

// 启动任务
startTask(config)
  .then(taskId => {
    console.log(`任务已启动: ${taskId}`);

    // 监控进度
    const intervalId = setInterval(async () => {
      const status = await getTaskStatus(taskId);
      console.log(`进度: ${status.progress.percentage}%`);

      if (status.state === 'completed') {
        clearInterval(intervalId);

        // 获取结果
        getResults(taskId).then(results => {
          console.log(`成功凭证: ${results.length}`);
          results.forEach(result => {
            if (result.success) {
              console.log(`${result.username} : ${result.password}`);
            }
          });
        });
      }
    }, 5000);
  })
  .catch(error => {
    console.error(error);
  });
```

---

### cURL调用示例（预期）

#### 启动任务

```bash
curl -X POST http://localhost:8000/api/v1/task/start \
  -H "Authorization: Bearer ak_live_xxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "target_url": "http://example.com/login",
      "protocol": "http_form",
      "users_file": "users.txt",
      "passwords_file": "passwords.txt",
      "concurrency": 20
    }
  }'
```

#### 查询任务状态

```bash
curl -X GET "http://localhost:8000/api/v1/task/status?task_id=task_20260701_120000" \
  -H "Authorization: Bearer ak_live_xxxxxxxxxxxxxxxxxxxx"
```

#### 获取结果

```bash
curl -X GET "http://localhost:8000/api/v1/results/task_20260701_120000" \
  -H "Authorization: Bearer ak_live_xxxxxxxxxxxxxxxxxxxx"
```

---

## 认证与安全

### API密钥认证（预期）

#### 认证方式

**方式1：Authorization Header**

```http
Authorization: Bearer ak_live_xxxxxxxxxxxxxxxxxxxx
```

**方式2：Query Parameter**

```http
GET /api/v1/task/status?api_key=ak_live_xxxxxxxxxxxxxxxxxxxx
```

---

#### 权限控制

不同API密钥可设置不同权限：

| 权限 | 说明 |
|------|------|
| `task:start` | 启动任务 |
| `task:stop` | 停止任务 |
| `task:status` | 查询状态 |
| `config:create` | 创建配置 |
| `config:read` | 读取配置 |
| `config:update` | 更新配置 |
| `config:delete` | 删除配置 |
| `results:get` | 获取结果 |
| `results:export` | 导出结果 |
| `admin:all` | 所有权限 |

---

#### 安全建议

1. **密钥保密**：不要在代码中硬编码API密钥
2. **环境变量**：使用环境变量存储密钥
3. **定期更换**：定期更换API密钥
4. **权限最小化**：仅授予必要权限
5. **HTTPS**：使用HTTPS传输
6. **IP白名单**：限制API访问IP

---

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "任务不存在",
    "details": {
      "task_id": "task_invalid"
    }
  }
}
```

---

### 错误代码列表

| 错误代码 | HTTP状态码 | 说明 |
|---------|-----------|------|
| `INVALID_API_KEY` | 401 | API密钥无效 |
| `PERMISSION_DENIED` | 403 | 权限不足 |
| `TASK_NOT_FOUND` | 404 | 任务不存在 |
| `CONFIG_NOT_FOUND` | 404 | 配置不存在 |
| `INVALID_CONFIG` | 400 | 配置格式错误 |
| `TASK_ALREADY_RUNNING` | 409 | 任务已在运行 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 内部服务器错误 |

---

## 开发计划

### 版本规划

#### v1.0 - 核心API版本（预计）

**功能范围**：
- 任务管理API（启动、停止、暂停、恢复、状态）
- 配置管理API（创建、读取、更新、删除）
- 结果查询API（查询、导出、统计）
- 基础认证（API密钥）

**开发周期**：预计 2-3个月

---

#### v2.0 - 高级API版本（预计）

**功能范围**：
- Webhook通知
- 批量操作
- SDK开发（Python、JavaScript）
- Swagger文档
- Postman集合

**开发周期**：预计 3-4个月

---

#### v3.0 - 企业版API（预计）

**功能范围**：
- 高级认证（OAuth2）
- 权限细分控制
- API调用统计
- 性能监控
- 高可用部署

**开发周期**：预计 4-6个月

---

## 技术架构（预期）

### 技术栈

#### Web框架

- **FastAPI**：高性能异步框架
- **Flask**：轻量级框架（可选）

#### 数据存储

- **PostgreSQL**：任务和配置数据
- **Redis**：任务状态缓存
- **MongoDB**：结果数据（可选）

#### 异步处理

- **Celery**：任务队列
- **RabbitMQ**：消息队列

#### API文档

- **Swagger/OpenAPI**：自动文档生成
- **Postman**：API测试集合

---

### 核心模块

```
API服务模块架构:

api_service/
├── app.py              # FastAPI应用入口
├── routers/            # API路由
│   ├── task_router.py      # 任务管理路由
│   ├── config_router.py    # 配置管理路由
│   ├── results_router.py   # 结果查询路由
│   ├── auth_router.py      # 认证路由
│   └── webhook_router.py   # Webhook路由
│
├── models/             # 数据模型
│   ├── task.py             # 任务模型
│   ├── config.py           # 配置模型
│   ├── results.py          # 结果模型
│   └── auth.py             # 认证模型
│
├── services/           # 业务逻辑
│   ├── task_service.py     # 任务服务
│   ├── config_service.py   # 配置服务
│   ├── results_service.py  # 结果服务
│   └── auth_service.py     # 认证服务
│
├── workers/            # 后台任务
│   ├── task_worker.py      # 任务执行Worker
│   ├── callback_worker.py  # Webhook回调Worker
│
├── middleware/         # 中间件
│   ├── auth_middleware.py  # 认证中间件
│   ├── error_middleware.py # 错误处理中间件
│   ├── rate_limit.py       # 速率限制中间件
│
└── docs/               # API文档
    ├── swagger.json        # Swagger文档
    ├── postman.json        # Postman集合
    └── examples/           # 示例代码
```

---

## 常见问题（预期）

### Q1: API服务如何启动？

**答**（预期）：

```bash
authkiller api
```

或

```bash
authkiller api --port 8000 --host 0.0.0.0
```

---

### Q2: 如何获取API密钥？

**答**（预期）：

1. **Web界面**：在管理界面创建API密钥
2. **API调用**：使用管理员权限调用创建接口
3. **配置文件**：在配置文件中预设密钥

---

### Q3: API调用频率限制？

**答**（预期）：

默认限制：
- **普通用户**：100次/分钟
- **高级用户**：500次/分钟
- **企业用户**：无限制

超出限制会返回 `429 Rate Limit Exceeded`

---

### Q4: 如何处理长时间任务？

**答**（预期）：

推荐方式：
- 使用 **Webhook** 等待完成通知
- 定期 **查询状态**（每5-10秒）
- 设置 **超时时间**（避免无限等待）

---

### Q5: API支持哪些数据格式？

**答**（预期）：

- **请求格式**：JSON
- **响应格式**：JSON
- **导出格式**：JSON、CSV、TXT

---

### Q6: 如何集成到CI/CD？

**答**（预期）：

示例（GitHub Actions）：

```yaml
name: Security Test

on:
  schedule:
    - cron: '0 2 * * *'  # 每天2点执行

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Start AuthKiller Task
        run: |
          curl -X POST http://your-server/api/v1/task/start \
            -H "Authorization: Bearer ${{ secrets.AUTHKILLER_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{"config": {...}}'

      - name: Wait for Completion
        run: |
          # 轮询等待任务完成
          python scripts/wait_for_task.py
```

---

## 反馈与建议

API服务正在规划中，欢迎提供反馈：

### 功能建议

如果您有以下需求，欢迎反馈：
- 需要的API接口
- SDK语言需求
- 集成场景建议
- 文档改进建议

### 提交方式

- **GitHub Issues**：https://github.com/example/authkiller/issues
- **功能建议标签**：`feature-request` + `api-service`

---

## 技术支持

- **项目主页**：https://github.com/example/authkiller
- **问题反馈**：https://github.com/example/authkiller/issues
- **API文档**：待发布（Swagger）
- **SDK文档**：待发布

---

**再次提醒：请确保合法使用本工具，遵守法律法规，尊重他人隐私和系统安全！**

---

**注意：本文档描述的功能均为规划功能，实际实现可能有所调整。请关注项目更新获取最新进度。**