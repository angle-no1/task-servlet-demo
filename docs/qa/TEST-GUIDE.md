# TaskMaster · 测试执行与截图取证指南

> 配套文档：`06_完整学号_姓名_题目_设计报告(DevOps 实践与项目验收交付).docx`
> 适用项目：本仓库 `task-springboot`（JDK 17 + Spring Boot 3.2.12 + H2 内存库）
> 本文目标：把「我做了」变成「有证据」——按 7 轮测试跑完，产出 19 张可直接插入报告的截图（其中 2 张可选）。

---

## 0. 先用 3 分钟看懂全局

| 项目 | 现状（已在本地核对） |
| --- | --- |
| 自动化测试 | 11 个测试类、**181 个用例**，`mvn clean test` 全绿（约 15 秒） |
| 可执行 JAR | `target/task-springboot.jar`，约 31 MB |
| 接口冒烟 | `scripts/api-smoke.ps1` 共 15 步，全 PASS |
| 运行时环境 | test profile + H2 内存库，7 条预置任务，每页 3 条共 3 页，账号 `admin / 123456` |
| 尚未具备 | 远程 GitHub 仓库（当前 `git remote` 为空）、真实 PR 记录、截图 |

推荐节奏（总计约 2～2.5 小时）：

| 轮次 | 内容 | 时长 | 产出 |
| --- | --- | --- | --- |
| 第 1 轮 | 本地自动化测试 | 15 min | 图 1～图 3 |
| 第 2 轮 | 启动 + 页面验收 | 30 min | 图 4～图 8 |
| 第 3 轮 | 接口与异步审计 | 20 min | 图 9～图 10 |
| 第 4 轮 | 推 GitHub 跑 CI | 25 min | 图 11～图 13 |
| 第 5 轮 | 失败演练（红灯） | 15 min | 图 14 |
| 第 6 轮 | PR 评审全流程 | 30 min | 图 15～图 17 |
| 第 7 轮 | 文档渲染截图 | 10 min | 图 18～图 19 |
| 收尾 | 插图 + 写图注 | 20 min | 报告 6.1～6.5 完整 |

---

## 1. 要求 → 证据对照表

先明确「报告里每一节凭什么打勾」，再动手截图。

| 报告要求（来自任务书） | 当前实现 | 需要的截图 |
| --- | --- | --- |
| 环节一：`.github/workflows/ci.yml`，JDK 17，Push/PR 触发，`mvn clean test` 门禁 + `mvn package` 产物归档 | 已就绪（6 个步骤） | 图 11、12、13 |
| 环节二：README（架构简图、徽标、环境依赖、一键启动、核心特性） | 已就绪（Mermaid 架构图 + 7 个徽标） | 图 18 |
| 环节二：API 手册（入参、出参、错误码） | 已就绪（`docs/api/API.md` + `openapi.yaml`） | 图 19 |
| 环节三：PR + 至少 2 条针对 AI 代码的审查意见 | 评审记录已有，**缺真实的 GitHub PR** | 图 15、16、17 |
| 环节四：Demo 脚本（正常链路、边界报错、异步表现） | 已就绪（`docs/demo/DEMO.md`） | 图 4～图 10 |
| 环节五：答辩 PPT + 复盘 | **尚未制作**（本指南不覆盖） | — |

> 结论：代码与文档基本满足要求，真正缺的是**「跑起来 + 截图」**这一环。本指南就是补这一环。

---

## 2. 第 0 步：环境检查（5 分钟）

在仓库根目录打开 **Windows PowerShell**（不要用 Git Bash，后面脚本是 .ps1）。

```powershell
java -version        # 必须是 17.x（pom.xml 与 ci.yml 都锁 17）
mvn -v               # 建议 3.9+
git --version
```

三条都要有输出。JDK 不是 17 时，截图里的 `mvn` 日志会和 CI 不一致，答辩容易被追问。

确认没有旧进程占用端口（本项目演示固定用 18080，避免和别的课设 8080 冲突）：

```powershell
netstat -ano | findstr :18080
```

有输出就先结束对应 PID：`taskkill /PID <PID> /F`。

---

## 3. 第 1 轮：本地自动化测试（图 1～图 3）

### 3.1 一条命令跑完「测试 → 打包 → 起服务 → 接口冒烟」

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify-local.ps1
```

脚本会依次输出 5 段，全部通过时结尾是：

```
测试类：11 个；用例：181 个；失败：0；错误：0；跳过：0
产物：target/task-springboot.jar（31.15 MB）
[PASS] ...（15 行接口冒烟）
全部通过：15/15

================ 验收汇总 ================
测试类     : 11
用例总数    : 181
JAR     : 31.15 MB
接口冒烟    : 15/15 PASS
结论：本地全绿，可进入 GitHub Actions 与 PR 环节
```

> **这一张图（图 3）的性价比最高**：一份截图同时证明「181 个用例全绿 + JAR 打得出来 + 15 步接口冒烟通过」。
> 答辩时被问「你怎么证明测试真的跑过」，直接翻这张。

> 脚本结束时会自动关闭自己启动的 Java 进程；若端口已有实例在跑，它会复用并在结尾提示「不负责关闭」。

### 3.2 只看测试（CI 里那条质量门禁）

```powershell
mvn -B clean test
```

预期结尾（约 15 秒）：

```
[INFO] Tests run: 181, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

### 3.3 截图清单（第 1 轮）

| 图号 | 截什么 | 画面里必须出现 | 存为 |
| --- | --- | --- | --- |
| 图 1 | `mvn -B clean test` 的结尾 | `Tests run: 181, Failures: 0`、`BUILD SUCCESS`、命令本身 | `report/screenshots/06-01-mvn-test.png` |
| 图 2 | `target/surefire-reports/` 目录 | 11 个 `.txt`/`.xml` 报告文件名（说明真的是逐类跑过） | `06-02-surefire.png` |
| 图 3 | `verify-local.ps1` 的汇总段 | 181 用例 + 15/15 PASS + JAR 大小 + 结论行 | `06-03-verify-local.png` |

**截法**：PowerShell 窗口拉宽到约 120 列（避免日志折行），窗口标题栏留着（能看出是 PowerShell 而非编辑器内部终端），用 `Win + Shift + S` 框选命令 + 结果区域。

---

## 4. 第 2 轮：启动应用与页面验收（图 4～图 8）

### 4.1 启动

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-demo.ps1 -SkipBuild
```

（第 1 轮已经打过包，这里加 `-SkipBuild` 省 5 秒；不加也可以。）

看到这两行就是启动成功：

```
The following 1 profile is active: "test"
Tomcat started on port 18080 (http) with context path '/'
```

浏览器打开 <http://localhost:18080>，应 302 跳到 `/login`。

### 4.2 逐项验收（对照报告「表 13 页面与 HTTP 验收」）

| # | 操作 | 预期 | 对应图 |
| --- | --- | --- | --- |
| 1 | 直接访问 `/task` | 302 跳 `/login` | 图 7（可并入图 4） |
| 2 | 用 `admin / 123456` 登录 | 回到 `/task`，显示 7 条任务、3 页 | 图 4、图 5 |
| 3 | 搜索框输 `JaCoCo` + 状态选「进行中」 | 命中 1 条，翻页后条件不丢 | 图 5 |
| 4 | 新增任务，标题留空 / 状态填 9 | 回到表单，出现中文错误提示，不写库 | 图 6 |
| 5 | 新增一条合法任务 | 列表多一条，出现成功提示 | 图 8 |
| 6 | 点「退出登录」后再访问 `/task` | 302 回 `/login` | 并入图 4 |

> 数据库是 H2 内存库，**每次重启都会重置回 7 条预置任务**。截图前建议先重启一次，保证画面干净。

### 4.3 截图清单（第 2 轮）

| 图号 | 截什么 | 画面里必须出现 | 存为 |
| --- | --- | --- | --- |
| 图 4 | 登录页 | 用户名/密码输入框、登录按钮、`admin/123456` 已填入 | `06-04-login.png` |
| 图 5 | 任务列表（含筛选） | 7 条数据、分页「1/3」、筛选条件 `JaCoCo` + 进行中 | `06-05-task-list.png` |
| 图 6 | 表单校验回显 | 标题输入框标红/提示「任务标题不能为空」 | `06-06-validation.png` |
| 图 7 | 未登录被拦截 | 地址栏 `/task` → 实际停在 `/login`（或开发者工具 Network 里 302） | `06-07-redirect.png` |
| 图 8 | 新增成功后的列表 | 成功提示条 + 新任务出现在第一行 | `06-08-created.png` |

**截法**：浏览器按 `F11` 全屏、`Ctrl + 0` 保证 100% 缩放，隐藏书签栏（`Ctrl+Shift+B`）；只截浏览器窗口，别把桌面壁纸带进去。

---

## 5. 第 3 轮：接口验收与异步审计（图 9～图 10）

浏览器里已经登录，**同一个浏览器窗口**直接访问下列地址，会带着 Session Cookie，省掉 curl 处理 Cookie 的麻烦（Chrome/Edge 会自动格式化 JSON）。

| 场景 | 地址 | 预期 |
| --- | --- | --- |
| 列表 | `http://localhost:18080/api/tasks?pageNum=1&pageSize=3` | `code:0`，`data.records` 3 条，`total:7`，`pages:3` |
| 详情 | `/api/tasks/1` | 200，`code:0`，返回该任务 |
| 不存在 | `/api/tasks/99999` | **404**，`code:40401`，`message:"任务不存在：99999"` |
| 参数校验 | 用 `scripts/api-smoke.ps1` 覆盖（见 5.2） | 400，`code:40001`，`data` 里有字段级错误 |
| 注入拦截 | `/api/tasks?sort=createTime%3BDROP%20TABLE%20t_task%3B--` | **400**，`code:40001` |
| 异步审计 | `/api/audits?limit=20` | `data` 数组里每条的 `thread` 是 `task-audit-*` |

> 想看**未登录 401**：按 `Ctrl+Shift+N` 开一个无痕窗口（不共享 Cookie）再访问 `/api/tasks`，返回 `{"code":40100,"message":"未登录或会话已过期",...}`。

### 5.1 接口冒烟脚本（报告表 12 的原始证据）

先确保应用在跑（第 4.1 步那个窗口不要关），**另开一个 PowerShell**：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/api-smoke.ps1
```

15 步全 PASS 时结尾是 `全部通过：15/15`。单步失败会打印 `[FAIL] 步骤名 详情`，按详情定位即可。

> 本次已修复一个 Windows 环境问题：旧版脚本把接口响应读进 PowerShell 变量，而 PowerShell 5.1 默认按系统代码页（GBK）解码子进程输出，UTF-8 中文会变乱码并让 `ConvertFrom-Json` 直接抛异常。现在改为 `curl -o 临时文件` 落盘后按 UTF-8 读取，中文与解析都正常。

### 5.2 异步审计怎么看「异步」

1. 在页面上新增或删除一条任务（触发写操作）；
2. 立刻打开 `/api/audits?limit=5`，最上面一条就是刚才的动作；
3. 回看 `run-demo` 那个窗口的日志，能看到两类线程交替出现：

```
http-nio-18080-exec-1  ... 处理 /api/tasks 请求
task-audit-1           ... 审计事件 action=CREATE taskId=8
```

**「http-nio-*」负责响应请求、「task-audit-*」负责写审计**，这就是报告里「异步处理表现」的可视化证据。

### 5.3 截图清单（第 3 轮）

| 图号 | 截什么 | 画面里必须出现 | 存为 |
| --- | --- | --- | --- |
| 图 9 | 冒烟脚本 15 行 PASS | 首行 `== TaskMaster API 冒烟测试：http://localhost:18080 ==`、末行 `全部通过：15/15` | `06-09-api-smoke.png` |
| 图 10 | 异步审计（二选一或拼接） | 左：`/api/audits` 的 JSON（`thread` 字段可见）；右：控制台里 `task-audit-*` 日志 | `06-10-async-audit.png` |

**截法**：图 10 建议截「控制台日志 + 浏览器 JSON」两个窗口并排，一张图讲清「异步」这件事；单独截 JSON 时，把 `thread` 字段滚动到可见位置。

---

## 6. 第 4 轮：推送到 GitHub，让 CI 真正跑一次（图 11～图 13）

### 6.1 建仓库并推送（只需一次）

1. GitHub 右上角 **New repository** → 名称建议 `task-springboot-devops`；
2. **不要**勾选 README / .gitignore / license（空仓库，否则 push 会冲突）；
3. 复制仓库地址，在仓库根目录执行：

```bash
git remote add origin https://github.com/<你的账号>/task-springboot-devops.git
git push -u origin master
```

> 当前分支是 `master`，`ci.yml` 同时监听 `master` 与 `main`，两条路都能触发。
> 推到空仓库时，GitHub 会自动把 `master` 设为默认分支，无需手动设置。

第一次 push 后 10 秒内，仓库顶部 **Actions** 就会出现一条 `CI` 运行记录。

### 6.2 看流水线（对照报告 4.2 节）

点进运行记录，应该看到 6 个业务步骤，顺序与 `ci.yml` 一致：

| 步骤 | 作用 | 截图要点 |
| --- | --- | --- |
| Set up JDK 17 (temurin) | 与本地一致的运行时 | 展开可见 `java-version 17` |
| **Quality gate - mvn clean test** | 测试不过就红灯，后面全跳过 | 出现 `Tests run: 181` |
| Build artifact - mvn package | 产出可执行 JAR | `BUILD SUCCESS` |
| Verify executable jar | 防「产物为空/改名」 | `task-springboot.jar` 大小 |
| Upload executable jar | 归档下载 | Artifacts 区出现 `task-springboot-jar` |
| Upload surefire reports | 失败也能查报告 | Artifacts 区出现 `surefire-reports` |

首跑含依赖下载，约 1.5～2 分钟；之后有 Maven 缓存，约 40 秒。

### 6.3 截图清单（第 4 轮）

| 图号 | 截什么 | 画面里必须出现 | 存为 |
| --- | --- | --- | --- |
| 图 11 | Actions 运行列表 | 绿色对勾、`CI`、触发方式 `push`、提交信息、耗时 | `06-11-actions-list.png` |
| 图 12 | 单次运行详情 | 6 个步骤全绿 + 展开 `Quality gate` 里的 `Tests run: 181` | `06-12-actions-detail.png` |
| 图 13 | 页面底部 Artifacts | `task-springboot-jar`、`surefire-reports` 两个可下载项 + 保留天数 | `06-13-artifacts.png` |

---

## 7. 第 5 轮：故意让流水线红灯（图 14）

这一轮是「失败演练」，也是报告 6.4 节「调试过程中遇到的问题」最好的素材：**证明质量门禁不是摆设**。

### 7.1 制造一个真实缺陷

在仓库根目录执行（Git Bash 或 PowerShell 均可）：

```bash
git checkout -b chore/ci-red-drill
```

打开 `src/main/java/cn/edu/mju/band/api/TaskRestController.java`，找到 `get` 方法，**删除这 3 行**：

```java
if (task == null) {
    throw new TaskNotFoundException("任务不存在：" + id);
}
```

本地先自测（约 15 秒，确认真的会红）：

```powershell
mvn -B clean test
```

预期：

```
[ERROR]   TaskApplicationTests.apiShouldCompleteCrudFlow:224 Status expected:<404> but was:<200>
[ERROR]   TaskRestControllerTest.shouldReturn404WhenTaskMissing:185 Status expected:<404> but was:<200>
[ERROR] Tests run: 181, Failures: 2, Errors: 0, Skipped: 0
```

然后提交并推送：

```bash
git commit -am "chore: 演练质量门禁（人为去掉 404 判断）"
git push -u origin chore/ci-red-drill
```

### 7.2 截图要点

运行详情页里应该看到：

- `Quality gate - mvn clean test` 标红失败；
- 后面 `Build artifact` / `Verify` / `Upload` 全部是灰色 **skipped**；
- 页面底部 **没有** `task-springboot-jar` 这个 Artifact（这正是「测试失败不产出交付物」的证据）；
- 展开失败步骤能看到那两行 `Status expected:<404> but was:<200>`。

### 7.3 恢复

```bash
git checkout master          # 回到干净分支
git branch -D chore/ci-red-drill
git push origin --delete chore/ci-red-drill
```

> 这一轮**不要**合并到 master。它的唯一价值是那张红灯截图。

| 图号 | 截什么 | 存为 |
| --- | --- | --- |
| 图 14 | 红灯运行详情（失败步骤 + 后续 skipped + 无 Artifact） | `06-14-ci-red.png` |

---

## 8. 第 6 轮：PR 与代码评审（图 15～图 17）

任务书要求「在 Git 仓库中模拟团队协作提交 PR，记录至少 2 次针对 AI 生成代码的审查意见」。
`docs/code-review/PR-001、PR-002` 是整理好的评审记录，但**答辩时要的是真实的 GitHub PR 页面**。这里用一次「AI 过度简化」的真实改动把这套流程跑通。

### 8.1 建分支、提交「AI 初稿」

```bash
git checkout master
git checkout -b refactor/api-get-simplify
```

同样把 `TaskRestController#get` 里那 3 行 `if (task == null) { throw ... }` 删掉（和 7.1 完全一样），然后：

```bash
git commit -am "refactor(api): 简化任务详情查询，去掉冗余判空"
git push -u origin refactor/api-get-simplify
```

> 这条提交信息的措辞很重要：它模拟了 AI「看起来合理、其实破坏了契约」的典型输出，评审才有话可说。

### 8.2 开 PR，写描述（直接抄）

推送后 GitHub 页面会出现绿色的 **Compare & pull request** 按钮，点它。

- 标题：`refactor(api): 简化任务详情查询`
- 描述：

```markdown
**变更动机**
`GET /api/tasks/{id}` 里对 `findById` 结果做了判空，`TaskView.from` 内部已经判空，
因此这段判断属于冗余代码，删除后可以少一层分支。

**变更内容**
- 移除 `TaskRestController#get` 中的 `if (task == null)` 判断。

**影响面**
- 仅 REST 详情接口；页面控制器未改动。

**自测**
- 本地 `mvn test`（待补充）
```

这段描述是故意写得「像 AI 交的作业」：动机听起来成立、自测一栏空着——评审意见正好从这里切入。

### 8.3 留 2 条审查意见（直接抄）

在 **Files changed** 里，鼠标移到被删除的那几行，点蓝色 `+` 写行内评论。

**意见 1（P1，必须改）**

```markdown
这里不能删。`TaskBuss#findById` 在任务不存在时返回 `null`，`TaskView.from(null)` 也返回 `null`，
接口会变成 `200 + {"code":0,"data":null}`。

但 `docs/api/API.md` 与 `openapi.yaml` 都约定「不存在 → 404 + 40401」，
前端拿到 `data:null` 无法区分「任务不存在」和「查询成功但没有数据」，属于**契约破坏**。

而且 CI 已经拦住了：`TaskRestControllerTest.shouldReturn404WhenTaskMissing` 报
`Status expected:<404> but was:<200>`（共 2 个用例红）。请恢复 `TaskNotFoundException`。
```

**意见 2（P2，建议改）**

```markdown
即使要简化，也不该在 Controller 里各自判空：`update`、`delete` 都还在依赖自己的判断，
改一处漏三处。建议把「找不到就抛 `TaskNotFoundException`」下沉到 `TaskBuss#findById`，
Controller 只负责组装响应；同时补一条 `findById` 查不到的单元测试，把语义钉在业务层。
```

第二条意见的核心是「**同一规则不要在多处重复实现**」，这是评审里最常被接受的改进建议。

### 8.4 修复、复核、合并

```bash
git revert --no-edit HEAD     # 恢复那 3 行；也可按意见 2 下沉到 TaskBuss，答辩演示用恢复更直观
git commit --amend -m "fix(api): 恢复任务不存在时的 404 语义，回应评审意见"
git push
```

回到 PR 页面：

1. 新提交推上来后，CI 重新运行并变绿（**这就是「修复后复核」的证据**）；
2. 在两条评论下分别回复「已恢复判空，CI 已转绿」；
3. 点 **Resolve conversation**；
4. 右上角 **Review changes → Approve → Submit review**；
5. **Merge pull request → Confirm merge**。

合并后 master 会自动再跑一次 CI，又一个绿勾。

### 8.5 截图清单（第 6 轮）

| 图号 | 截什么 | 画面里必须出现 | 存为 |
| --- | --- | --- | --- |
| 图 15 | PR 列表 / PR 详情页顶部 | 标题、`Open`（或 `Merged`）、`refactor/api-get-simplify → master`、CI 绿勾 | `06-15-pr-overview.png` |
| 图 16 | Conversation 里的两条行内评论 | 评论正文前两行 + 所在文件与行号（`TaskRestController.java`）+ `Resolved` 标记 | `06-16-pr-comments.png` |
| 图 17 | Files changed | 红色删除 / 绿色恢复的 diff（一眼看出「删了 3 行又加回来」） | `06-17-pr-diff.png` |

> 图 16 是这一环节的**得分点**：它同时证明「有真实 PR」「有 2 条审查意见」「意见被采纳并复核」。

---

## 9. 第 7 轮：文档类截图（图 18～图 19）

这两张图对应环节二的「AI 辅助输出工业级技术资产文档」，必须在 GitHub 上截（本地 Markdown 预览看不到徽标和 Mermaid 渲染效果）。

| 图号 | 地址 | 画面里必须出现 |
| --- | --- | --- |
| 图 18 | 仓库首页 README | 顶部 7 个徽标（JDK/Spring Boot/MyBatis-Plus/…/CI）+ 「核心特性」+ 渲染出来的 Mermaid 架构图 |
| 图 19 | `docs/api/API.md` | 至少一个端点小节：请求参数表、响应示例、错误码表 |

**截法**：
- 图 18 只截首屏（徽标 + 标题 + 架构图），别把 Issue/Star 区带进来；
- Mermaid 图如果显示为代码块，说明渲染没开，等 2 秒刷新即可；
- 图 19 打开后按 `Ctrl + F` 搜「错误码」，把带表格的那段滚到屏幕中间再截。

> 可选：`http://localhost:18080/openapi.yaml` 能直接下载规范文件（`docs/ci/LOCAL-VERIFICATION.md` 有记录），
> 想强调「机器可读契约」可以补一张，但不必放进正文。

---

## 10. 截图总清单（照着勾）

命名统一放 `report/screenshots/`，前缀 `06-` 与报告编号对应，避免和前几个实验的截图混在一起。

| 图号 | 文件名 | 内容 | 插入报告位置 |
| --- | --- | --- | --- |
| 图 1 | `06-01-mvn-test.png` | `mvn clean test` 全绿 | 6.1 自动化测试结果 |
| 图 2 | `06-02-surefire.png` | surefire 报告目录 | 6.1（可选） |
| 图 3 | `06-03-verify-local.png` | 一键验收汇总 | 6.1 / 6.2 之间 |
| 图 4 | `06-04-login.png` | 登录页 | 6.3 页面验收 |
| 图 5 | `06-05-task-list.png` | 列表 + 筛选 + 分页 | 6.3 |
| 图 6 | `06-06-validation.png` | 表单校验回显 | 6.3 |
| 图 7 | `06-07-redirect.png` | 未登录 302 | 6.3 |
| 图 8 | `06-08-created.png` | 新增成功 | 6.3（可选） |
| 图 9 | `06-09-api-smoke.png` | 15 步 PASS | 6.2 API 冒烟结果 |
| 图 10 | `06-10-async-audit.png` | 异步审计 + 线程名 | 5.5 异步审计实现 / 6.2 |
| 图 11 | `06-11-actions-list.png` | Actions 列表绿勾 | 6.5 |
| 图 12 | `06-12-actions-detail.png` | 步骤全绿 + `Tests run: 181` | 6.5 |
| 图 13 | `06-13-artifacts.png` | Artifact 可下载 | 6.5 |
| 图 14 | `06-14-ci-red.png` | 红灯 + 后续 skipped | 6.4 调试问题 / 6.5 |
| 图 15 | `06-15-pr-overview.png` | PR 概览 | 4.9 评审流程 / 环节三 |
| 图 16 | `06-16-pr-comments.png` | 2 条行内审查意见 | 同上（**必放**） |
| 图 17 | `06-17-pr-diff.png` | Files changed | 同上 |
| 图 18 | `06-18-readme.png` | README 徽标 + 架构图 | 5.7 / 环节二 |
| 图 19 | `06-19-api-doc.png` | API 手册渲染 | 5.7 / 环节二 |

### 图注（可直接粘到报告里，五号字、居中）

```
图 1  mvn clean test：11 个测试类、181 个用例全部通过
图 2  Surefire 逐类测试报告
图 3  一键验收汇总：181 用例全绿、JAR 31.15 MB、接口冒烟 15/15
图 4  登录页（admin / 123456）
图 5  任务列表：7 条预置数据、每页 3 条共 3 页、条件筛选
图 6  服务端校验：标题为空时回显中文错误提示且不写库
图 7  未登录访问 /task 被拦截并重定向到 /login
图 8  新增任务成功后返回列表
图 9  api-smoke.ps1：15 个接口场景全部 PASS
图 10 异步审计：http-nio-* 处理请求，task-audit-* 线程写审计
图 11 GitHub Actions 运行列表（push 触发，绿灯）
图 12 单次运行详情：质量门禁 → 打包 → 校验 → 归档
图 13 Artifacts：可下载可执行 JAR 与测试报告
图 14 失败演练：测试红灯时流水线中断且不产出 Artifact
图 15 PR 概览：refactor/api-get-simplify → master
图 16 两条行内审查意见（契约破坏 + 规则下沉建议）
图 17 Files changed：修复提交恢复了 404 判定
图 18 README：技术栈徽标、核心特性与架构简图
图 19 API 手册：入参、出参与错误码定义
```

---

## 11. 截图规范（老师一眼看得出「认真」的细节）

1. **尺寸**：窗口宽度 ≥ 1200px；终端窗口拉到 120 列以上，避免长命令行折行。
2. **干净**：关掉微信/QQ 弹窗、浏览器书签栏、多余标签页；只截应用窗口。
3. **可读**：终端字号 ≥ 12pt；浏览器缩放 100%（`Ctrl + 0`）。
4. **完整**：一定要带上「命令本身」和「结果」，只截结果没有说服力。
5. **标注**：关键行用系统截图工具的画笔圈一下（如 `Tests run: 181`、`task-springboot-jar`），最多标 2～3 处，别画花。
6. **格式**：统一 PNG；不要用手机拍屏幕（摩尔纹 + 反光会直接扣印象分）。
7. **对齐**：插进 Word 时统一宽度（约 15 cm），图注在图下方居中，正文里写「如图 5 所示」。

---

## 12. 常见问题排查

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| `mvn` 不是内部或外部命令 | Maven 未配 PATH | 用 IDEA 自带 Maven 或配置 `MAVEN_HOME` 后重开终端 |
| `java -version` 不是 17 | 多版本 JDK 冲突 | 调整 `JAVA_HOME`，与 `ci.yml` 的 `java-version: '17'` 对齐 |
| 端口 18080 被占用 | 上次的 java 进程没关 | `netstat -ano \| findstr :18080` → `taskkill /PID xxx /F` |
| 页面能开但样式错乱 | 静态资源缓存 | `Ctrl + F5` 强刷 |
| 接口一直 401 | 没带 Session Cookie | 在**已登录的同一浏览器窗口**访问，或先跑登录请求拿 `JSESSIONID` |
| 冒烟脚本报 `ConvertFrom-Json` 异常 | 旧版脚本按 GBK 解码 UTF-8 响应 | 已修复（响应落盘后按 UTF-8 读），`git pull` 最新脚本即可 |
| `.ps1` 无法运行 | 执行策略限制 | 用 `powershell -ExecutionPolicy Bypass -File xxx.ps1` |
| 脚本中文乱码 | `.ps1` 存成 UTF-8 无 BOM，PS 5.1 按 ANSI 读 | 用 VSCode「UTF-8 with BOM」另存 |
| Actions 报 `task-springboot.jar` 不存在 | `finalName` 被改 / 打包失败 | 看 `Build artifact` 步骤日志，本地先 `mvn package` 复现 |
| Actions 找不到 `target/surefire-reports` | 测试阶段就没跑起来 | 属正常兜底（`if-no-files-found: ignore`），先修 `Quality gate` |
| push 被拒（non-fast-forward） | 建仓时勾了 README | `git pull --rebase origin master` 后再 push |
| PR 里 CI 一直是红灯 | 就是你删的那 3 行导致的 | 这正是演练目的；按 8.4 恢复即可转绿 |

---

## 13. 交付前检查清单

- [ ] `git status` 干净（除 `target/`、`report/screenshots/`），`body.json` 这类临时文件已删除或加进 `.gitignore`
- [ ] `mvn clean test` → 181 / 0 / 0 / 0，`BUILD SUCCESS`
- [ ] `scripts/verify-local.ps1` → 结论行「本地全绿」
- [ ] 浏览器 6 项页面验收全部符合预期（第 4.2 节表格）
- [ ] `/api/tasks` 未登录 401、登录后 200、注入载荷 400、不存在 404
- [ ] `/api/audits` 能看到 `task-audit-*` 线程事件
- [ ] GitHub Actions 至少 3 次成功运行（首次 push、PR、合并后）
- [ ] Artifacts 里两个产物都能下载
- [ ] 红灯演练截图已保存，且分支已删除（master 上没有缺陷代码）
- [ ] PR 已合并，2 条评论均为 Resolved
- [ ] 19 张截图按 `06-xx` 命名放入 `report/screenshots/`
- [ ] 报告 6.5 节按附录 A 改写（删掉「未连接远程仓库」的表述）
- [ ] 报告封面填好班级、学号、姓名、日期

---

## 附录 A：CI 跑通后，报告 6.5 节这样改写

原稿写的是「本仓库完成时未连接远程 GitHub 仓库，因此流水线以本地同命令 + YAML 语法校验验证」。
推上 GitHub 并跑绿之后，这段必须改写，否则和截图自相矛盾。建议替换为：

> 流水线已在 GitHub 上实际运行。仓库推送到 `master` 后，Actions 依据 `ci.yml` 依次执行
> Checkout → Set up JDK 17 → Quality gate（`mvn clean test`）→ Build artifact（`mvn package`）→
> Verify executable jar → Upload executable jar / surefire reports，单次运行约 1～2 分钟。
> 三个 Artifact（`task-springboot-jar`、`surefire-reports`）均可直接下载，与生成它们的提交一一对应。
> 为验证门禁有效性，另在 `chore/ci-red-drill` 分支上人为移除 404 判断，流水线在 Quality gate 步骤即失败，
> 后续打包与归档步骤全部跳过、不产出 Artifact（见图 14），说明「测试不过不交付」不是口号。

同时把报告 6.4 节的表格补一行（本次实测得到的问题）：

| 问题 | 现象 | 原因 | 解决办法 |
| --- | --- | --- | --- |
| 冒烟脚本解析响应失败 | `ConvertFrom-Json` 抛「传入的对象无效」，中文全乱码 | Windows PowerShell 5.1 按系统代码页（GBK）解码子进程输出 | `curl -o` 把响应落盘，再用 UTF-8 读取后解析 |

---

## 附录 B：本次对代码与脚本的改动

| 文件 | 改动 | 原因 |
| --- | --- | --- |
| `scripts/api-smoke.ps1` | 响应体改为 `curl -o 临时文件` + UTF-8 读取；输出增加步骤计数（`全部通过：15/15`） | 原实现把响应读进变量，Windows 下按 GBK 解码导致乱码、JSON 解析失败，脚本跑不完 |
| `scripts/verify-local.ps1` | **新增**：一键完成「环境自检 → clean test → 统计用例 → package → 起服务 → 冒烟 → 汇总」 | 报告需要一张「全链路通过」的截图；手工串 5 条命令容易漏步，也不便于复现 |
| `README.md` | 第 9 节补「一条命令本地验收」，交付物索引补两个脚本与本指南 | 让验收人不必翻聊天记录就能复现 |
| `docs/qa/TEST-GUIDE.md` | **新增**：本文件 | 测试步骤与截图清单的单一事实来源 |

> 运行验证记录：`verify-local.ps1` 实测输出 11 个测试类 / 181 用例 / 0 失败，JAR 31.15 MB，
> 接口冒烟 15/15 PASS；红灯演练实测 2 个用例失败（`TaskApplicationTests.apiShouldCompleteCrudFlow`、
> `TaskRestControllerTest.shouldReturn404WhenTaskMissing`），与本文描述一致。
