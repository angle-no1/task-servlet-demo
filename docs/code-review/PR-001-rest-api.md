# PR #1 · 任务 REST API 与异步审计

| 项 | 内容 |
| --- | --- |
| 仓库 | `task-servlet-demo` |
| 源分支 | `feature/task-rest-api` |
| 目标分支 | `master` |
| 作者 | AI 结对（生成初稿与测试） |
| 评审人 | 人类工程师（课程验收角色） |
| 变更规模 | 新增 1 个 REST 控制器、5 个 DTO、1 个异常处理器、3 个审计类、1 个异步配置；修改业务接口与拦截器 |
| 结论 | **Request Changes** → 修复后 **Approve** → 合并 |

> 说明：本记录按 PR 讨论整理，保留「AI 初稿代码片段 → 审查意见 → 修复后代码 → 复核测试」的完整链路。
> 当前仓库中的实现为修复后版本，初稿片段不再保留在运行代码里，避免把已知漏洞带进交付物。

---

## 1. 变更目标

1. 为页面之外提供一套 JSON 接口（分页、CRUD、批量改状态），支撑接口手册与自动化验证；
2. 统一响应体与错误码，页面请求继续返回 HTML，API 请求返回 JSON；
3. 写操作触发异步审计，用于 Demo 展示「异步处理表现」；
4. 排序字段由调用方指定，支持 `createTime / title / status`。

---

## 2. 审查意见 1（P0）：`ORDER BY` 字符串拼接导致 SQL 注入

### 2.1 初稿代码

`TaskBuss#findPage` 直接把请求参数拼进 SQL 片段：

```java
// ❌ AI 初稿
@Override
public Page<Task> findPage(String title, Byte status, int pageNum, int pageSize, String sort) {
    Page<Task> page = new Page<>(pageNum, pageSize);
    LambdaQueryWrapper<Task> wrapper = Wrappers.lambdaQuery(Task.class);
    if (StringUtils.hasText(title)) {
        wrapper.like(Task::getTitle, title.trim());
    }
    if (status != null) {
        wrapper.eq(Task::getStatus, status);
    }
    // sort 来自 ?sort=...，被原样拼到 ORDER BY 后面
    wrapper.last("ORDER BY " + sort);
    return taskMapper.selectPage(page, wrapper);
}
```

控制器直接把参数透传：

```java
// ❌ AI 初稿
@GetMapping
public ApiResponse<PageResult<TaskView>> list(..., @RequestParam(defaultValue = "createTime,desc") String sort) {
    Page<Task> page = taskBuss.findPage(title, status, pageNum, pageSize, sort);
    ...
}
```

### 2.2 复现步骤

```bash
curl -s -b cookie.txt \
  'http://localhost:18080/api/tasks?sort=createTime%3BDROP%20TABLE%20t_task%3B--'
```

实际拼出的 SQL 片段：

```sql
ORDER BY createTime;DROP TABLE t_task;--
```

### 2.3 风险

- **SQL 注入**：`last()` 的内容不经过参数绑定，属于 MyBatis-Plus 明确标注的「拼接 SQL」入口；
- 取决于 JDBC 是否允许一次执行多条语句，可能直接破坏表结构；即使不允许，也会造成 SQL 语法错误（500）并把原始 SQL 暴露到日志；
- 该参数是公开查询参数，攻击成本极低。

### 2.4 审查意见

> 排序字段不能作为 SQL 片段接收。要么改成枚举白名单，要么在进入 `last()` 之前做严格的正则校验；
> 推荐前者：把「外部字符串 → 列引用」收敛到一个枚举，非法字段在参数解析阶段直接 400。
> 同时补一个注入载荷的测试，防止以后有人为了「支持更多排序」又把它改回字符串拼接。

### 2.5 修复后代码

新增白名单枚举（`TaskSort`）：

```java
public enum TaskSort {
    CREATE_TIME("createTime", Task::getCreateTime),
    TITLE("title", Task::getTitle),
    STATUS("status", Task::getStatus);

    private final String field;
    private final SFunction<Task, ?> column;

    public static TaskSort of(String field) {
        if (field == null || field.isBlank()) {
            return CREATE_TIME;
        }
        for (TaskSort sort : values()) {
            if (sort.field.equalsIgnoreCase(field.trim())) {
                return sort;
            }
        }
        throw new IllegalArgumentException(
                "不支持的排序字段：" + field + "（可选：createTime、title、status）");
    }
}
```

`TaskBuss#findPage` 改为接收枚举，并用 `orderBy` + 列引用：

```java
// ✅ 修复后
public Page<Task> findPage(String title, Byte status, int pageNum, int pageSize,
                           TaskSort sort, boolean ascending) {
    ...
    TaskSort order = sort == null ? TaskSort.CREATE_TIME : sort;
    // SFunction 引用由 MyBatis-Plus 转成受信任的列名，外部字符串不进入 SQL
    wrapper.orderBy(true, ascending, order.getColumn());
    ...
}
```

接口参数解析（`SortSpec`）：

```java
// ✅ 修复后
SortSpec sortSpec = SortSpec.parse(sort);   // 非法字段/方向直接抛 IllegalArgumentException → 400
Page<Task> page = taskBuss.findPage(
        title, status, pageNum, pageSize, sortSpec.field(), sortSpec.ascending());
```

### 2.6 复核与回归

| 用例 | 断言 |
| --- | --- |
| `TaskSortTest#shouldRejectUnknownFields` | `createTime;DROP TABLE t_task;--` 等 6 种载荷全部抛异常 |
| `SortSpecTest#shouldRejectMalformedSort` | 非法方向、超过两段、注入载荷全部 400 |
| `TaskRestControllerTest#shouldRejectSqlInjectionInSort` | 接口返回 400 + `40001`，业务层零调用 |
| `TaskApplicationTests#apiShouldRejectSqlInjectionAndKeepTableIntact` | 注入请求后 `t_task` 仍有 7 条种子数据 |

**复核结论：通过。** 原始字符串不再进入任何 SQL 片段。

---

## 3. 审查意见 2（P1）：批量改状态写成循环 `updateById`（N+1）

### 3.1 初稿代码

```java
// ❌ AI 初稿：N 条任务 → N 次 UPDATE
@Override
@Transactional
public int updateStatusBatch(List<Integer> ids, Byte status) {
    int updated = 0;
    for (Integer id : ids) {
        Task task = new Task();
        task.setId(id);
        task.setStatus(status);
        updated += taskMapper.updateById(task);
    }
    return updated;
}
```

### 3.2 问题

- 100 条任务会产生 **100 条 UPDATE**，每条一次网络往返，事务被拉长；
- 与报告「N+1 问题排查」直接对应：循环里逐条访问数据库；
- 部分失败时难以给出准确的「成功条数」，且容易长时间持锁。

### 3.3 审查意见

> 批量接口只应该产生一条 SQL。用 `UpdateWrapper.set(...).in("id", ids)`，
> 同时在业务层做去重、过滤 null、限制最大 100 条，避免超长 IN 与长事务。
> 测试要断言「只调用一次 `update`，不再调用 `updateById`」。

### 3.4 修复后代码

```java
// ✅ 修复后：一条 UPDATE ... WHERE id IN (...)
UpdateWrapper<Task> wrapper = Wrappers.update();
wrapper.set("status", status).in("id", distinctIds);
return taskMapper.update(null, wrapper);
```

### 3.5 复核与回归

| 用例 | 断言 |
| --- | --- |
| `TaskBussTest#updateStatusBatch_shouldIssueSingleUpdate` | 捕获 `UpdateWrapper`，`sqlSet` 含 `status`、`sqlSegment` 含 `IN`；`verify(never()).updateById(...)` |
| `TaskBussTest#updateStatusBatch_shouldRejectTooManyIds` | 101 条被拒绝，不触达 Mapper |
| `TaskApplicationTests#apiShouldCompleteCrudFlow` | 批量改状态后单条查询状态为 2 |

**复核结论：通过。** 100 条任务从 100 条 UPDATE 降为 1 条。

---

## 4. 审查意见 3（P1）：`findById` 结果直接解引用，空结果 NPE → 500

### 4.1 初稿代码

```java
// ❌ AI 初稿：taskBuss.findById 可能返回 null
@GetMapping("/{id}")
public ApiResponse<TaskView> get(@PathVariable Integer id) {
    return ApiResponse.ok(TaskView.from(taskBuss.findById(id)));
}
```

`TaskView.from` 同样没有判空：

```java
// ❌ AI 初稿
public static TaskView from(Task task) {
    return new TaskView(task.getId(), task.getTitle(), ...);   // NPE
}
```

### 4.2 复现

```bash
curl -s -b cookie.txt http://localhost:18080/api/tasks/9999
```

初稿返回 500（`NullPointerException`），而不是 404。

### 4.3 审查意见

> 查询单条资源的语义是「不存在 → 404」。NPE 被兜底成 500 会让调用方误判为服务端故障，
> 也会把堆栈写进日志。请在控制器显式判空并抛 `TaskNotFoundException`，
> `TaskView.from` 保留防御性判空；同时补 404 的接口测试。

### 4.4 修复后代码

```java
// ✅ 修复后
Task task = taskBuss.findById(id);
if (task == null) {
    throw new TaskNotFoundException("任务不存在：" + id);
}
return ApiResponse.ok(TaskView.from(task));
```

`TaskApiExceptionHandler` 将 `TaskNotFoundException` 映射为 404 + `40401`。

### 4.5 复核与回归

| 用例 | 断言 |
| --- | --- |
| `TaskRestControllerTest#shouldReturn404WhenTaskMissing` | 404 + `40401` + 文案 |
| `TaskRestControllerTest#shouldReturn404WhenUpdatingMissingTask` | 修改不存在任务同样 404 |
| `TaskRestControllerTest#shouldReturn404WhenDeletingMissingTask` | 删除不存在任务同样 404 |
| `TaskApplicationTests#apiShouldCompleteCrudFlow` | 删除后再查返回 404 |

**复核结论：通过。** 不存在资源统一为 404，不再出现 NPE。

---

## 5. 审查意见 4（P2）：新增接口没有测试

### 5.1 意见

> AI 初稿只提交了实现，没有测试；接口契约、错误码、排序白名单都只能靠手测。
> 按项目约定（每个 Controller 至少一个切片测试、每条业务分支至少一个单元测试）补齐：
> 401、400、404、201、批量更新、注入载荷、异步审计线程名。

### 5.2 修复

新增/扩充 4 个测试类、20+ 用例：

- `TaskRestControllerTest`：REST 切片（18 个用例）；
- `TaskSortTest` / `SortSpecTest`：白名单与参数解析（参数化覆盖）；
- `TaskAuditStoreTest`：有界队列；
- `TaskApplicationTests`：H2 上的 API 全链路 + 异步审计 + 注入后表完好。

**复核结论：通过。** `mvn clean test` 共 181 个用例全部通过。

---

## 6. 合并检查清单

- [x] `mvn -B clean test` 全绿（181 个用例）
- [x] `mvn -B package -DskipTests` 生成 `target/task-springboot.jar`
- [x] 未登录 `/api/tasks` 返回 401 JSON，页面请求仍 302 到 `/login`
- [x] 注入载荷返回 400，`t_task` 表完好
- [x] 批量改状态为单条 `UPDATE ... IN`
- [x] 404 语义覆盖查询/修改/删除
- [x] 异步审计线程名为 `task-audit-*`
- [x] OpenAPI 规范与实现字段一致（`openapi.yaml` / `API.md`）

## 7. 证据索引

| 内容 | 位置 |
| --- | --- |
| REST 控制器 | [`TaskRestController`](../../src/main/java/cn/edu/mju/band/api/TaskRestController.java) |
| 统一错误码 | [`ApiErrorCode`](../../src/main/java/cn/edu/mju/band/api/ApiErrorCode.java) |
| 排序白名单 | [`TaskSort`](../../src/main/java/cn/edu/mju/band/buss/TaskSort.java)、[`SortSpec`](../../src/main/java/cn/edu/mju/band/api/dto/SortSpec.java) |
| 批量更新 | [`TaskBuss#updateStatusBatch`](../../src/main/java/cn/edu/mju/band/buss/impl/TaskBuss.java) |
| 异步审计 | [`TaskAuditService`](../../src/main/java/cn/edu/mju/band/audit/TaskAuditService.java)、[`AsyncConfig`](../../src/main/java/cn/edu/mju/band/config/AsyncConfig.java) |
| 接口手册 | [`docs/api/API.md`](../api/API.md) |
| 接口测试 | [`TaskRestControllerTest`](../../src/test/java/cn/edu/mju/band/api/TaskRestControllerTest.java) |
