# PR #2 · GitHub Actions CI 流水线

| 项 | 内容 |
| --- | --- |
| 仓库 | `task-servlet-demo` |
| 源分支 | `feature/ci-pipeline` |
| 目标分支 | `master` |
| 作者 | AI 结对（生成初稿） |
| 评审人 | 人类工程师（课程验收角色） |
| 结论 | **Request Changes** → 修复后 **Approve** → 合并 |

> 本记录对应报告「环节一：配置 GitHub Actions 自动化持续集成流水线」与
> 「环节三：团队代码评审」。重点不是把 YAML 写长，而是保证**质量门禁不可绕过、产物可复现**。

---

## 1. 变更目标

1. Push / PR 到主分支自动触发；
2. JDK 17 + Maven 缓存；
3. 先跑 `mvn clean test`，失败即红灯；
4. 通过后 `mvn package`，把可执行 JAR 上传为 Artifact；
5. 测试报告即使失败也归档，便于定位。

---

## 2. 审查意见 1（P0）：流水线没有测试门禁

### 2.1 初稿代码

```yaml
# ❌ AI 初稿：只打包，不跑测试
name: build
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - run: mvn -B package -DskipTests
      - uses: actions/upload-artifact@v4
        with:
          name: jar
          path: target/
```

### 2.2 问题

- 报告明确要求「流水线必须包含 `mvn clean test` 质量门禁」，初稿用 `-DskipTests` 直接跳过；
- 测试失败不会让流水线红灯，等于「CI 只验证能编译」，无法杜绝「在我电脑上能跑」；
- 没有 `pull_request` 触发，PR 阶段无法提前发现问题。

### 2.3 审查意见

> 门禁必须是独立、先执行、不可跳过的步骤：
> `mvn clean test` 失败 → 后续 `package` 与上传都不执行。
> 同时补 `pull_request` 触发，让 PR 阶段就能看到红灯；保留 `workflow_dispatch` 方便手动重跑。

### 2.4 修复后代码

```yaml
# ✅ 修复后
on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]
  workflow_dispatch:

steps:
  - name: Quality gate - mvn clean test
    run: mvn -B -ntp clean test

  - name: Build artifact - mvn package
    run: mvn -B -ntp package -DskipTests
```

### 2.5 复核

- 任意一个测试失败时，`Quality gate` 步骤非 0 退出，GitHub Actions 终止后续步骤；
- 本地用同一命令验证：`mvn -B clean test` → `Tests run: 181, Failures: 0, Errors: 0`。

**结论：通过。**

---

## 3. 审查意见 2（P1）：直接上传整个 `target/`，产物里混入不可执行文件

### 3.1 问题

Spring Boot Maven Plugin 打包后会生成两个 JAR：

```text
target/task-springboot.jar            # fat jar，可 java -jar 运行
target/task-springboot.jar.original   # 原始 thin jar，没有 Main-Class，不能直接运行
```

初稿为了省事，直接上传整个构建目录：

```yaml
# ❌ AI 初稿
- uses: actions/upload-artifact@v4
  with:
    name: jar
    path: target/
```

这会把 `.original`、`classes/`、`maven-status/`、`surefire-reports/` 一起打进去：
Artifact 体积大、下载方无法从文件名判断哪个才是可执行 JAR，
一旦拿到 `task-springboot.jar.original`，`java -jar` 会报 `no main manifest attribute`。
同时 `name: jar` 过于笼统，和后续测试报告无法区分。

### 3.2 审查意见

> 产物路径必须精确到 `target/task-springboot.jar`，并在上传前用 `test -f` + `ls -lh` 校验；
> Artifact 名称用 `task-springboot-jar`，避免和测试报告混淆。
> 测试报告作为独立 Artifact 上传，不要混在构建产物里。

### 3.3 修复后代码

```yaml
# ✅ 修复后
- name: Verify executable jar
  run: |
    test -f target/task-springboot.jar
    ls -lh target/task-springboot.jar

- name: Upload executable jar
  uses: actions/upload-artifact@v4
  with:
    name: task-springboot-jar
    path: target/task-springboot.jar
    if-no-files-found: error
    retention-days: 7
```

### 3.4 复核

- 本地 `target/` 中同时存在 `.jar` 与 `.jar.original`，与 CI 一致；
- 只上传精确路径，`if-no-files-found: error` 防止「静默成功但无产物」；
- 下载后 `java -jar task-springboot.jar --spring.profiles.active=test` 可启动。

**结论：通过。**

---

## 4. 审查意见 3（P2）：缺少最小权限、并发控制与失败报告归档

### 4.1 问题

- 未声明 `permissions`，`GITHUB_TOKEN` 默认权限偏大，CI 只需要读代码；
- 同一分支连续 push 会并行跑多条流水线，浪费 runner 且结果可能互相覆盖；
- 测试失败时 `target/surefire-reports` 没有上传，定位红灯只能翻日志。

### 4.2 修复

```yaml
# ✅ 修复后
permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

```yaml
- name: Upload surefire reports
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: surefire-reports
    path: target/surefire-reports/
    if-no-files-found: ignore
```

**结论：通过。**

---

## 5. 合并检查清单

- [x] `push` / `pull_request` / 手动触发齐全
- [x] JDK 17（Temurin）+ Maven 缓存
- [x] `mvn clean test` 先执行，失败不打包
- [x] `mvn package` 生成可执行 JAR
- [x] Artifact 精确上传 `target/task-springboot.jar`
- [x] 测试报告 `if: always()` 归档
- [x] `contents: read` 最小权限
- [x] 同分支并发取消

## 6. 证据索引

| 内容 | 位置 |
| --- | --- |
| 工作流 | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) |
| 本地等价验证 | [`docs/ci/LOCAL-VERIFICATION.md`](../ci/LOCAL-VERIFICATION.md) |
| 构建配置 | [`pom.xml`](../../pom.xml) |
| 一键启动 | [`scripts/run-demo.ps1`](../../scripts/run-demo.ps1) |
