# TaskMaster API 接口手册

> 适用版本：`task-springboot 1.0.0`（Java 高级编程实验 · 第六阶段 DevOps 交付）
> 规范文件：[`src/main/resources/static/openapi.yaml`](../src/main/resources/static/openapi.yaml)
> 实现代码：[`TaskRestController`](../src/main/java/cn/edu/mju/band/api/TaskRestController.java)、[`TaskApiExceptionHandler`](../src/main/java/cn/edu/mju/band/api/TaskApiExceptionHandler.java)

---

## 1. 概览

| 项 | 说明 |
| --- | --- |
| Base URL（dev） | `http://localhost:8080` |
| Base URL（test / Demo） | `http://localhost:18080` |
| 数据格式 | `application/json;charset=UTF-8` |
| 鉴权方式 | 登录后的 Session Cookie `JSESSIONID`（与页面登录共用） |
| 时间格式 | `yyyy-MM-dd HH:mm:ss`（GMT+8）；响应体 `timestamp` 为 ISO-8601 带时区 |
| 统一响应体 | `{ code, message, data, timestamp }`，`code=0` 表示成功 |
| 分页参数 | `pageNum` 从 1 开始；`pageSize` 默认 10，最大 100 |
| 排序白名单 | `createTime`、`title`、`status`，格式 `字段,asc\|desc` |

### 1.1 认证

API 与页面共用同一套 Session：

```bash
# 1) 登录并保存 Cookie（-c 写 cookie.txt）
curl -s -c cookie.txt -X POST http://localhost:18080/login \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'loginName=admin&loginPwd=123456'

# 2) 后续请求携带 Cookie（-b 读 cookie.txt）
curl -s -b cookie.txt 'http://localhost:18080/api/tasks?pageNum=1&pageSize=3'
```

未登录（或 Session 过期）访问 `/api/**` 时，拦截器直接返回 **401 + JSON**，
不会 302 到 HTML 登录页，便于前端/脚本稳定处理：

```json
{
  "code": 40100,
  "message": "未登录或会话已过期",
  "data": null,
  "timestamp": "2026-10-30T09:30:00+08:00"
}
```

### 1.2 统一响应体

```json
{
  "code": 0,
  "message": "成功",
  "data": { },
  "timestamp": "2026-10-30T09:30:00+08:00"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `code` | integer | 业务码，见第 2 节；`0` 成功 |
| `message` | string | 可读提示，成功时可能是「任务已创建」等操作结果 |
| `data` | object / array / null | 业务数据；校验失败时为「字段 → 错误信息」对象 |
| `timestamp` | string | 服务端生成响应的时间，ISO-8601 |

---

## 2. 错误码

HTTP 状态码表达错误类别，`code` 表达具体业务原因。

| HTTP | `code` | 含义 | 典型场景 | 响应形态 |
| --- | --- | --- | --- | --- |
| 200 / 201 | `0` | 成功 | 查询、新增、修改、删除、批量更新 | `data` 为业务数据 |
| 400 | `40001` | 请求参数不合法 | 标题为空、状态 9、`pageSize=101`、非法排序字段、JSON 语法错误、id 非数字 | `message` 为具体原因；字段校验时 `data` 为字段错误集合 |
| 401 | `40100` | 未登录 / 会话过期 | 未登录直接请求 `/api/**` | `data=null` |
| 404 | `40401` | 任务不存在 | 查询、修改、删除不存在的 id | `data=null` |
| 500 | `50001` | 数据库暂时不可用 | 数据库宕机、连接超时 | `data=null`，不泄漏 SQL 与堆栈 |
| 500 | `50000` | 未预期的服务器错误 | 兜底异常 | `data=null`，细节只写服务端日志 |

字段校验失败示例：

```json
{
  "code": 40001,
  "message": "任务标题不能为空",
  "data": {
    "title": "任务标题不能为空",
    "status": "任务状态只能是 0/1/2"
  },
  "timestamp": "2026-10-30T09:30:00+08:00"
}
```

---

## 3. 接口详情

### 3.1 分页查询任务

`GET /api/tasks`

| 参数 | 位置 | 必填 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `title` | query | 否 | string | — | 标题关键字，模糊匹配 |
| `status` | query | 否 | integer | — | `0` 待办 / `1` 进行中 / `2` 已完成 |
| `pageNum` | query | 否 | integer | `1` | 页码，最小 1 |
| `pageSize` | query | 否 | integer | `10` | 每页条数，1 ~ 100 |
| `sort` | query | 否 | string | `createTime,desc` | `字段[,asc\|desc]`；字段只允许 `createTime` / `title` / `status` |

**请求**

```bash
curl -s -b cookie.txt \
  'http://localhost:18080/api/tasks?title=报告&status=1&pageNum=1&pageSize=3&sort=title,asc'
```

**成功响应 `200`**

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "records": [
      {
        "id": 1,
        "title": "完成实验报告",
        "content": "整理单元测试与覆盖率截图",
        "status": 0,
        "statusLabel": "待办",
        "createTime": "2026-10-01 09:00:00"
      }
    ],
    "total": 1,
    "current": 1,
    "size": 3,
    "pages": 1
  },
  "timestamp": "2026-10-30T09:30:00+08:00"
}
```

**错误示例：排序字段注入**

```bash
curl -s -b cookie.txt \
  'http://localhost:18080/api/tasks?sort=createTime;DROP%20TABLE%20t_task;--'
```

```json
{
  "code": 40001,
  "message": "不支持的排序字段：createTime;DROP TABLE t_task;--（可选：createTime、title、status）",
  "data": null,
  "timestamp": "2026-10-30T09:30:00+08:00"
}
```

> 排序字段在 `SortSpec` / `TaskSort` 白名单中解析，只有枚举里的列引用会进入 SQL，
> 原始字符串永远不会被拼进 `ORDER BY`。对应测试：
> `TaskRestControllerTest#shouldRejectSqlInjectionInSort`、
> `TaskApplicationTests#apiShouldRejectSqlInjectionAndKeepTableIntact`。

### 3.2 查询单个任务

`GET /api/tasks/{id}`

| 参数 | 位置 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | path | 是 | integer | 任务编号 |

**成功响应 `200`**

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": 7,
    "title": "代码评审",
    "content": "消除坏味道",
    "status": 0,
    "statusLabel": "待办",
    "createTime": "2026-10-07 09:00:00"
  },
  "timestamp": "2026-10-30T09:30:00+08:00"
}
```

**不存在 `404`**

```json
{
  "code": 40401,
  "message": "任务不存在：404",
  "data": null,
  "timestamp": "2026-10-30T09:30:00+08:00"
}
```

> 早期 AI 初稿直接调用 `TaskView.from(null)`，会触发 NPE 并返回 500。
> 经 Code Review 后改为显式判空 + `TaskNotFoundException` → 404，见
> [`docs/code-review/PR-001-rest-api.md`](code-review/PR-001-rest-api.md)。

### 3.3 新增任务

`POST /api/tasks`

| 字段 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `title` | string | 是 | 非空白，≤ 100 字符 | 任务标题，服务端会 `trim` |
| `content` | string | 否 | ≤ 2000 字符 | 任务内容 |
| `status` | integer | 是 | `0` / `1` / `2` | 任务状态 |

**请求**

```bash
curl -s -b cookie.txt -X POST http://localhost:18080/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"准备答辩 PPT","content":"整理 AI 提效比数据","status":1}'
```

**成功响应 `201`**（响应头 `Location: /api/tasks/42`）

```json
{
  "code": 0,
  "message": "任务已创建",
  "data": {
    "id": 42,
    "title": "准备答辩 PPT",
    "content": "整理 AI 提效比数据",
    "status": 1,
    "statusLabel": "进行中",
    "createTime": "2026-10-30 09:31:00"
  },
  "timestamp": "2026-10-30T09:31:00+08:00"
}
```

### 3.4 修改任务

`PUT /api/tasks/{id}`

请求体同新增。`content` 不传表示保持原值，传空串表示清空。
任务不存在返回 404；校验失败返回 400。

```bash
curl -s -b cookie.txt -X PUT http://localhost:18080/api/tasks/7 \
  -H 'Content-Type: application/json' \
  -d '{"title":"准备答辩 PPT（终稿）","status":2}'
```

**成功响应 `200`**

```json
{
  "code": 0,
  "message": "任务已更新",
  "data": {
    "id": 7,
    "title": "准备答辩 PPT（终稿）",
    "content": "消除坏味道",
    "status": 2,
    "statusLabel": "已完成",
    "createTime": "2026-10-07 09:00:00"
  },
  "timestamp": "2026-10-30T09:32:00+08:00"
}
```

### 3.5 删除任务

`DELETE /api/tasks/{id}`

```bash
curl -s -b cookie.txt -X DELETE http://localhost:18080/api/tasks/42
```

**成功响应 `200`**

```json
{
  "code": 0,
  "message": "任务已删除",
  "data": null,
  "timestamp": "2026-10-30T09:33:00+08:00"
}
```

### 3.6 批量修改状态

`PATCH /api/tasks/batch-status`

| 字段 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `ids` | integer[] | 是 | 1 ~ 100 个，元素非空 | 任务编号，服务端会去重、过滤 null |
| `status` | integer | 是 | `0` / `1` / `2` | 目标状态 |

```bash
curl -s -b cookie.txt -X PATCH http://localhost:18080/api/tasks/batch-status \
  -H 'Content-Type: application/json' \
  -d '{"ids":[1,2,3],"status":2}'
```

**成功响应 `200`**（`data` 为实际更新行数）

```json
{
  "code": 0,
  "message": "已更新 3 条任务",
  "data": 3,
  "timestamp": "2026-10-30T09:34:00+08:00"
}
```

> 实现使用一条 `UPDATE t_task SET status=? WHERE id IN (?, ?, ?)`，
> 而不是循环 `updateById`。AI 初稿的 N+1 写法已在 Code Review 中拦截，
> 见 [`docs/code-review/PR-001-rest-api.md`](code-review/PR-001-rest-api.md)。

### 3.7 查询异步审计事件

`GET /api/audits`

| 参数 | 位置 | 必填 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `limit` | query | 否 | integer | `20` | 返回条数，1 ~ 200 |

```bash
curl -s -b cookie.txt 'http://localhost:18080/api/audits?limit=5'
```

```json
{
  "code": 0,
  "message": "成功",
  "data": [
    {
      "at": "2026-10-30T09:35:00+08:00",
      "thread": "task-audit-1",
      "action": "CREATE",
      "taskId": 42,
      "detail": "准备答辩 PPT"
    },
    {
      "at": "2026-10-30T09:35:01+08:00",
      "thread": "task-audit-2",
      "action": "BATCH_STATUS",
      "taskId": null,
      "detail": "ids=[1, 2, 3], status=2"
    }
  ],
  "timestamp": "2026-10-30T09:35:01+08:00"
}
```

> `thread` 以 `task-audit-` 开头，证明事件由异步线程池写入；
> 写接口的响应不会等待审计完成。详见 `TaskAuditService`、`AsyncConfig`。

---

## 4. 数据字典

### 4.1 TaskView

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 任务编号 |
| `title` | string | 标题 |
| `content` | string / null | 内容 |
| `status` | integer | `0` 待办 / `1` 进行中 / `2` 已完成 |
| `statusLabel` | string | 状态中文文案：待办 / 进行中 / 已完成 / 未知 |
| `createTime` | string / null | 创建时间 `yyyy-MM-dd HH:mm:ss` |

### 4.2 TaskAuditEntry

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `at` | string | 事件时间（ISO-8601） |
| `thread` | string | 实际执行线程名，异步为 `task-audit-*` |
| `action` | string | `CREATE` / `UPDATE` / `DELETE` / `BATCH_STATUS` |
| `taskId` | integer / null | 单条操作的任务编号；批量操作时为 null |
| `detail` | string / null | 可读描述（不含敏感信息） |

---

## 5. OpenAPI 规范与工具导入

- 规范文件：`src/main/resources/static/openapi.yaml`（OpenAPI 3.0.3）
- 应用启动后可直接访问：<http://localhost:18080/openapi.yaml>（免登录）
- 导入方式：
  1. **Apifox / Postman**：导入 → 选择 OpenAPI/Swagger → 粘贴 YAML 或选择文件；
  2. **Swagger Editor**：<https://editor.swagger.io/> → File → Import file；
  3. **VS Code**：安装 `OpenAPI (Swagger) Editor` 插件，打开 YAML 即可预览与校验。

> 规范里的 `servers`、参数、示例与实现一一对应；字段改名时先改 YAML 再改 DTO，
> 由 `TaskRestControllerTest` 的 JSON 断言兜底，防止文档与代码漂移。

---

## 6. 本地验证

启动 test 环境（H2 内存库，7 条预置任务）：

```bash
java -jar target/task-springboot.jar --spring.profiles.active=test --server.port=18080
```

快速验证脚本（PowerShell，需应用已启动）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/api-smoke.ps1 -BaseUrl http://localhost:18080
```

脚本依次验证：登录 → 列表 → 新增 → 详情 → 批量改状态 → 删除 → 404 → 401 → 注入拦截。

---

## 7. 变更记录

| 版本 | 日期 | 变更 |
| --- | --- | --- |
| 1.0.0 | 2026-10-30 | 首次发布：任务分页/CRUD/批量状态 + 异步审计 + 统一错误码 |
