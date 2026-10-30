# TaskMaster Demo 演示脚本

> 适用：第六阶段验收 / 答辩现场（15 分钟版本，可按 8 分钟压缩）
> 环境：JDK 17 + 任意浏览器；**不需要 MySQL**（test 环境用 H2 内存库）

---

## 0. 演示前 10 分钟检查清单

| # | 检查项 | 命令 / 操作 | 应看到 |
| --- | --- | --- | --- |
| 1 | JDK 17 | `java -version` | `17.x` |
| 2 | 端口未被占用 | `netstat -ano \| findstr 18080` | 无输出 |
| 3 | 构建通过 | `mvn -B clean test` | `Tests run: 181, Failures: 0` |
| 4 | 启动应用 | `scripts/run-demo.ps1` | `The following 1 profile is active: "test"`、`Tomcat started on port 18080` |
| 5 | 登录页可开 | 浏览器打开 <http://localhost:18080/login> | 登录表单 |
| 6 | 预置数据 | `admin / 123456` 登录 | 列表 7 条、每页 3 条、3 页 |
| 7 | Cookie 工具 | 浏览器开发者工具 → Application → Cookies | `JSESSIONID` |
| 8 | 备用终端 | 打开第二个终端，`cd` 到仓库根目录 | 用于 curl 演示 |
| 9 | 重置数据 | 重启应用（H2 内存库每次启动重建） | 回到 7 条预置任务 |

> H2 数据在进程内存中，**重启即恢复初始 7 条**，演示前重启一次最稳。

---

## 1. 预置数据

test 环境由 `db/schema-h2.sql` + `db/data-h2.sql` 初始化：

| 编号 | 标题 | 状态 | 创建时间 |
| --- | --- | --- | --- |
| 1 | 完成实验报告 | 待办 | 2026-10-01 09:00 |
| 2 | 迁移 SpringBoot | 已完成 | 2026-10-02 09:00 |
| 3 | 编写 JUnit 5 用例 | 进行中 | 2026-10-03 09:00 |
| 4 | Mockito 打桩 | 待办 | 2026-10-04 09:00 |
| 5 | 生成 JaCoCo 报告 | 进行中 | 2026-10-05 09:00 |
| 6 | 配置多环境 | 已完成 | 2026-10-06 09:00 |
| 7 | 代码评审 | 待办 | 2026-10-07 09:00 |

账号：`admin / 123456`（明文仅用于教学演示）。

**演示前建议**（可选）：先新增 1 条「答辩演示任务」，让列表变成 8 条，后来删除时能体现「少一条」。

---

## 2. 场景一：正常交易链路（约 5 分钟）

### 2.1 登录与鉴权边界

1. 先访问 <http://localhost:18080/task>（未登录）→ 观察地址栏变成 `/login`，说明拦截器生效；
2. 用 `admin / 123456` 登录 → 自动回到 `/task`；
3. 讲一句：登录成功后 `changeSessionId()` 防会话固定，Session 里只存身份不存口令。

### 2.2 列表 / 搜索 / 分页

1. 列表显示 7 条、每页 3 条、共 3 页；
2. 搜索「JaCoCo」→ 1 条；状态选「进行中」→ 结果与页码保留条件；
3. 翻到第 2 页 → 搜索条件仍在 URL 里（`?title=...&status=...&pageNum=2`）；
4. 点「重置」→ 回到全部 7 条。

### 2.3 新增 / 编辑 / 删除

1. 新增任务：标题「答辩演示任务」、内容「Demo 脚本第 2.3 节」、状态「进行中」→ 提交；
2. 列表出现新任务与绿色成功提示；
3. 编辑该任务：改标题为「答辩演示任务（已更新）」、状态「已完成」→ 保存；
4. 删除该任务 → 列表少一条，提示「任务已删除」。

### 2.4 同一链路的 API 版本（终端）

```bash
# 登录，保存 Cookie
curl -s -c cookie.txt -X POST http://localhost:18080/login \
     -d 'loginName=admin&loginPwd=123456'

# 查询（默认第 1 页、每页 10 条、创建时间倒序）
curl -s -b cookie.txt 'http://localhost:18080/api/tasks?pageNum=1&pageSize=3'

# 新增
curl -s -b cookie.txt -X POST http://localhost:18080/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"API 演示任务","content":"正常链路","status":1}'

# 批量改状态（把 id 换成上一步返回的 data.id）
curl -s -b cookie.txt -X PATCH http://localhost:18080/api/tasks/batch-status \
  -H 'Content-Type: application/json' \
  -d '{"ids":[8],"status":2}'
```

讲解点：页面与 API 复用同一个 `ITaskBuss`，业务规则只有一份；
响应统一为 `{code, message, data, timestamp}`。

---

## 3. 场景二：极端边界报错（约 4 分钟）

### 3.1 页面侧

| 操作 | 期望 |
| --- | --- |
| 新增时标题留空、状态 9（用 curl 绕过 HTML `required`） | 回到表单，中文错误提示，不写库 |
| 访问 `/task?opt=update&id=9999` | 400 错误页「任务不存在或已被删除」 |
| 访问 `/task?status=abc` | 400 错误页「任务状态参数非法」 |
| 退出登录后再访问 `/task` | 302 到 `/login` |
| 登录页输错密码 | 提示「用户名或密码错误」（不区分账号不存在/密码错误） |

curl 绕过前端校验：

```bash
curl -s -b cookie.txt -X POST http://localhost:18080/task \
  -d 'opt=add&title=&status=9' | Select-String '任务标题不能为空'
```

### 3.2 API 侧（终端逐条执行，观察 HTTP 状态与 `code`）

```bash
# ① 字段校验失败：400 + 字段级错误
curl -s -b cookie.txt -X POST http://localhost:18080/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"   ","status":9}'

# ② 任务不存在：404 + 40401
curl -s -b cookie.txt http://localhost:18080/api/tasks/9999

# ③ 页码越界：400
curl -s -b cookie.txt 'http://localhost:18080/api/tasks?pageNum=0'

# ④ 每页条数超限：400
curl -s -b cookie.txt 'http://localhost:18080/api/tasks?pageSize=101'

# ⑤ 未登录：401 JSON（不是 302 登录页）
curl -s http://localhost:18080/api/tasks

# ⑥ ORDER BY 注入：400，且任务表仍然存在
curl -s -b cookie.txt \
  'http://localhost:18080/api/tasks?sort=createTime%3BDROP%20TABLE%20t_task%3B--'
curl -s -b cookie.txt 'http://localhost:18080/api/tasks?pageSize=1'
```

讲解点：

- 排序字段在 `TaskSort` 白名单里解析，非法值在参数解析阶段被拒绝，JSON 错误码 `40001`；
- 修复前 AI 初稿用 `wrapper.last("ORDER BY " + sort)`，同一请求会拼出
  `ORDER BY createTime;DROP TABLE t_task;--`，这是 PR-001 拦截的第 1 个问题；
- 校验失败不写库：日志里只有 `WARN`，没有 `INSERT`。

---

## 4. 场景三：异步处理表现（约 3 分钟）

### 4.1 观察日志

1. 保持应用控制台可见；
2. 连续新增 3 条任务（页面或 API 均可）；
3. 观察控制台：

   ```text
   DEBUG ... TaskMapper.insert  - <==    Updates: 1
   DEBUG ... TaskMapper.selectById - <==    Total: 1
   INFO  [task-audit-1] ... TaskAuditService - 异步审计 action=CREATE taskId=8 detail=...
   INFO  [task-audit-2] ... TaskAuditService - 异步审计 action=CREATE taskId=9 detail=...
   ```

关键点：HTTP 请求线程是 `http-nio-18080-exec-*`，审计线程是 `task-audit-*`，
说明写操作没有等待审计完成。

### 4.2 查询审计事件

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
      "taskId": 8,
      "detail": "API 演示任务"
    }
  ],
  "timestamp": "2026-10-30T09:35:01+08:00"
}
```

### 4.3 讲清「为什么异步」

| 维度 | 同步审计 | 异步审计（当前实现） |
| --- | --- | --- |
| 响应时间 | 写库 + 审计都完成后才返回 | 写库完成即返回，审计在线程池排队 |
| 故障影响 | 审计慢/失败会拖慢或回滚主流程 | 审计异常不阻塞主流程（`CallerRunsPolicy` 兜底排队） |
| 可观测性 | 日志与请求线程混在一起 | `task-audit-*` 线程名 + `/api/audits` 可查 |

> 局限也要讲：当前审计存在进程内队列，重启即丢失；生产应换 MQ + 持久化审计表。

---

## 5. 场景四：CI 流水线（约 2 分钟，可提前录屏）

1. 打开 GitHub 仓库 → Actions → `CI`；
2. 展示最近一次 `push` 触发的运行：
   - `Quality gate - mvn clean test` 绿灯；
   - `Build artifact - mvn package` 绿灯；
   - Artifacts 区域可下载 `task-springboot-jar` 与 `surefire-reports`；
3. 展示一次「测试失败 → 红灯 → 打包步骤被跳过」的历史运行（提前制造一个失败提交再回滚）；
4. 讲清报告要点：`mvn clean test` 是质量门禁，`mvn package` 产物归档，杜绝「在我电脑上能跑」。

本地等价命令：

```bash
mvn -B clean test
mvn -B package -DskipTests
ls -lh target/task-springboot.jar
```

---

## 6. 场景五：Code Review 证据（约 1 分钟）

打开 [`docs/code-review/PR-001-rest-api.md`](code-review/PR-001-rest-api.md) 与
[`PR-002-ci-pipeline.md`](code-review/PR-002-ci-pipeline.md)，按「问题 → 复现 → 修复 → 测试」讲：

1. **SQL 注入**：`sort=createTime;DROP TABLE t_task;--`，修复为 `TaskSort` 白名单；
2. **N+1**：批量改状态循环 `updateById`，修复为一条 `UPDATE ... IN`；
3. **NPE**：`findById` 返回 null 直接 `TaskView.from`，修复为 404；
4. **CI**：`mvn test` 未 clean、`target/*.jar` 误传 `.original`，修复为 `clean test` + 精确路径。

强调：这些不是「AI 不会写」，而是「AI 初稿必须在人类评审 + 测试门禁下才能上线」。

---

## 7. 时间分配建议

| 版本 | 时长 | 内容 |
| --- | --- | --- |
| 完整版 | 15 min | 场景一 5 + 场景二 4 + 场景三 3 + 场景四 2 + 评审 1 |
| 压缩版 | 8 min | 登录 → 新增/删除 → 注入 400 → 401 → 审计日志 → CI Artifact |
| 极端情况 | 3 min | 只演示 401、注入拦截、异步日志三张「证据」 |

---

## 8. 应急方案

| 故障 | 处理 |
| --- | --- |
| 端口 18080 被占用 | `scripts/run-demo.ps1 -Port 18081`，后续命令同步改端口 |
| 页面 500 / 数据库报错 | 确认用的是 `test` profile；重启应用恢复 H2 |
| curl 中文乱码 | Windows 终端执行 `chcp 65001`，或只看状态码与 JSON 字段 |
| 忘记 Cookie | 重新执行登录 curl，或浏览器登录后用开发者工具复制 `JSESSIONID` |
| GitHub Actions 打不开 | 播放提前录屏，并展示本地 `mvn clean test` 输出 |
| 演示数据被改乱 | 重启应用，H2 自动回到 7 条预置任务 |
