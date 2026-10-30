# CI 本地等价验证记录

> 目的：在没有远程 GitHub 仓库的离线环境里，用与 `.github/workflows/ci.yml` **完全相同的命令**
> 验证流水线各阶段可复现；GitHub Actions 的实际运行截图由任课教师/学生在推送后补充。
>
> 验证时间：2026-10-30 09:17 ~ 09:25（Asia/Shanghai）
> 环境：Windows 10 · JDK 17.0.1 · Maven 3.9.16 · 项目路径 `task-servlet-demo`

---

## 1. 质量门禁：`mvn -B clean test`

```bash
mvn -B clean test
```

```text
[INFO] Tests run: 181, Failures: 0, Errors: 0, Skipped: 0
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  11.629 s
```

| 测试类 | 用例数（含参数化展开） | 覆盖点 |
| --- | --- | --- |
| `TaskApplicationTests` | 12 | H2 上分页、事务、登录、REST 全链路、异步审计、注入后表完好 |
| `TaskBussTest` | 72 | 业务校验、边界、排序白名单、批量更新单条 SQL、异常翻译 |
| `TaskRestControllerTest` | 18 | 401/400/404/201、字段校验、注入拦截、批量审计调用 |
| `TaskControllerTest` | 15 | 页面参数绑定、`@Valid` 回显、登录拦截、错误页 |
| `LoginControllerTest` | 10 | 登录成功/失败、回跳、防 open redirect、退出 |
| `LoginInterceptorTest` | 6 | 页面 302、API 401 JSON、context-path |
| `TaskSortTest` / `SortSpecTest` | 15 + 13 | 白名单、方向、注入载荷 |
| `TaskAuditStoreTest` | 4 | 倒序、上限淘汰、边界 |
| `UserBussTest` / `HomeControllerTest` | 15 + 1 | 登录业务、首页重定向 |

> 具体数量以 `target/surefire-reports/` 为准；总计 181。

---

## 2. 打包：`mvn -B package -DskipTests`

```bash
mvn -B package -DskipTests
```

```text
[INFO] Building jar: ...\target\task-springboot.jar
[INFO] Replacing main artifact ... with repackaged archive, adding nested dependencies in BOOT-INF/.
[INFO] BUILD SUCCESS
```

| 产物 | 大小 | 说明 |
| --- | --- | --- |
| `target/task-springboot.jar` | 32,665,820 字节（约 31.2 MB） | fat jar，内嵌 Tomcat |
| `target/task-springboot.jar.original` | — | Spring Boot 插件保留的原始 thin jar，**不是**交付物 |

CI 中通过 `test -f target/task-springboot.jar` + 精确路径上传，避免把 `.original` 混入 Artifact。

---

## 3. 启动与 API 冒烟

```bash
java -jar target/task-springboot.jar --spring.profiles.active=test --server.port=18080
```

```text
The following 1 profile is active: "test"
Tomcat started on port 18080 (http) with context path '/'
Started TaskApplication in 2.606 seconds
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/api-smoke.ps1
```

```text
== TaskMaster API 冒烟测试：http://localhost:18080 ==
[PASS] 登录并保存 Session Cookie
[PASS] GET /api/tasks 返回 code=0
[PASS] 分页字段完整（total/current/size/pages）
[PASS] POST /api/tasks 返回 201 + 回填 id
[PASS] GET /api/tasks/{id} 返回刚创建的任务
[PASS] PATCH /api/tasks/batch-status 更新 1 条
[PASS] 批量更新后状态变为已完成
[PASS] DELETE /api/tasks/{id} 删除成功
[PASS] 查询已删除任务返回 404 + 40401
[PASS] 空标题 / 非法状态返回 400 + 字段错误
[PASS] ORDER BY 注入载荷被拦截（400）
[PASS] 注入尝试后 t_task 仍可查询（表未被删除）
[PASS] 未登录访问 /api/tasks 返回 401 + 40100
[PASS] GET /api/audits 能看到异步审计事件
[PASS] 审计事件由 task-audit-* 线程写入
全部通过
```

补充手工验证：

| 请求 | 结果 |
| --- | --- |
| `GET /task`（已登录） | 200，返回任务列表页面 |
| `GET /openapi.yaml` | 200，返回 OpenAPI 3.0.3 规范 |
| `GET /api/tasks?pageSize=3&sort=title,asc` | 200，`ORDER BY title ASC` 生效 |
| `GET /api/tasks/9999` | 404，`code=40401` |
| 日志中审计线程 | `task-audit-1` / `task-audit-2` |

---

## 4. 与 CI 的差异说明

| 项 | 本地 | GitHub Actions |
| --- | --- | --- |
| OS | Windows 10 | `ubuntu-latest` |
| JDK | Oracle JDK 17.0.1 | Temurin 17 |
| 依赖来源 | 本机 `~/.m2`（离线） | Maven Central（`setup-java` 缓存） |
| 命令 | `mvn -B clean test` / `mvn -B package -DskipTests` | 同左（加 `-ntp`） |
| 产物 | 本地 `target/task-springboot.jar` | Artifact `task-springboot-jar` |

跨平台差异点已规避：

- 不使用仅 Windows 可用的脚本步骤；CI 只跑 Maven；
- 测试使用 H2 内存库，不依赖 MySQL；
- 文件编码统一 UTF-8（`project.build.sourceEncoding`）；
- 日志中的中文不影响构建结果。

---

## 5. 待补充的线上证据

推送仓库后，在 GitHub Actions 页面截取：

1. `CI` 工作流绿灯全貌（`Quality gate` → `Build artifact` → 两个 Artifact）；
2. Artifacts 展开，显示 `task-springboot-jar` 与 `surefire-reports`；
3. 一次测试失败的红色运行（可临时改坏一个断言后回滚），证明门禁会阻断打包。

将截图放入实验报告「测试」与「实现」章节。
