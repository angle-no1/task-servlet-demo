# -*- coding: utf-8 -*-
"""按 06 报告模板生成已填写的《Java 高级编程实验报告（DevOps 实践与项目验收交付）》。

模板来源：桌面上的 06_完整学号_姓名_题目_设计报告(DevOps 实践与项目验收交付).docx
输出：task-servlet-demo/report/06_..._已填写.docx
"""
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

SRC = r"C:\Users\augenstern\Desktop\06_完整学号_姓名_题目_设计报告(DevOps 实践与项目验收交付).docx"
OUT_DIR = r"C:\Users\augenstern\Desktop\task-servlet-demo 7\task-servlet-demo\report"
OUT = os.path.join(
    OUT_DIR,
    "06_完整学号_姓名_题目_设计报告(DevOps 实践与项目验收交付)_已填写.docx",
)

doc = Document(SRC)

BODY_FONT = "Times New Roman"
EA_FONT = "宋体"
CODE_FONT = "Consolas"


# ---------------------------------------------------------------------------
# 排版辅助（沿用 04/05 报告约定：正文 10.5pt、1.25 倍行距、首行缩进 2 字符）
# ---------------------------------------------------------------------------
def set_run(run, size=10.5, bold=False, ascii_font=BODY_FONT, east=EA_FONT):
    run.font.name = ascii_font
    run.font.size = Pt(size)
    run.font.bold = bold
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    rf.set(qn("w:ascii"), ascii_font)
    rf.set(qn("w:hAnsi"), ascii_font)
    rf.set(qn("w:eastAsia"), east)
    rf.set(qn("w:cs"), ascii_font)
    old = rpr.find(qn("w:szCs"))
    if old is not None:
        rpr.remove(old)
    szcs = OxmlElement("w:szCs")
    szcs.set(qn("w:val"), str(int(size * 2)))
    rpr.append(szcs)


def set_indent(par, first_pt=None, left_pt=None):
    ind = par._p.get_or_add_pPr().get_or_add_ind()
    if first_pt is not None:
        ind.set(qn("w:firstLine"), str(int(first_pt * 20)))
        ind.set(qn("w:firstLineChars"), "0")
    if left_pt is not None:
        ind.set(qn("w:left"), str(int(left_pt * 20)))
        ind.set(qn("w:leftChars"), "0")


def set_shading(par, fill="F2F2F2"):
    ppr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.insert_element_before(
        shd,
        "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct",
        "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd",
        "w:snapToGrid", "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents",
        "w:suppressOverlap", "w:jc", "w:textDirection", "w:textAlignment",
        "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr",
        "w:sectPr", "w:pPrChange",
    )


def set_snap_off(par):
    ppr = par._p.get_or_add_pPr()
    snap = OxmlElement("w:snapToGrid")
    snap.set(qn("w:val"), "0")
    ppr.insert_element_before(
        snap,
        "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap",
        "w:jc", "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
        "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange",
    )


def new_para(after, text="", first_pt=21.0, left_pt=None, size=10.5, bold=False,
             ascii_font=BODY_FONT, east=EA_FONT, align=None, before=0, after_sp=0,
             shading=None, line=1.25, snap_off=False, keep_together=False,
             keep_with_next=False):
    par = doc.add_paragraph()
    par.style = doc.styles["Normal"]
    if text:
        run = par.add_run(text)
        set_run(run, size=size, bold=bold, ascii_font=ascii_font, east=east)
    pf = par.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after_sp)
    pf.line_spacing = line
    pf.keep_together = keep_together
    pf.keep_with_next = keep_with_next
    if align is not None:
        pf.alignment = align
    set_indent(par, first_pt=first_pt, left_pt=left_pt)
    if shading:
        set_shading(par, shading)
    if snap_off:
        set_snap_off(par)
    after.addnext(par._p)
    return par._p


def para(after, text, **kw):
    return new_para(after, text, **kw)


def lead(after, label, text, **kw):
    par = doc.add_paragraph()
    par.style = doc.styles["Normal"]
    r1 = par.add_run(label)
    set_run(r1, size=kw.get("size", 10.5), bold=True)
    r2 = par.add_run(text)
    set_run(r2, size=kw.get("size", 10.5), bold=False)
    pf = par.paragraph_format
    pf.space_before = Pt(kw.get("before", 0))
    pf.space_after = Pt(kw.get("after_sp", 0))
    pf.line_spacing = kw.get("line", 1.25)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_indent(par, first_pt=kw.get("first_pt", 21.0), left_pt=kw.get("left_pt"))
    after.addnext(par._p)
    return par._p


def sub_heading(after, text):
    return new_para(after, text, first_pt=0, size=10.5, bold=True, before=8,
                    after_sp=2, align=WD_ALIGN_PARAGRAPH.LEFT)


def code_block(after, text):
    cur = after
    lines = text.strip("\n").split("\n")
    for idx, line in enumerate(lines):
        cur = new_para(
            cur, line, first_pt=0, left_pt=14, size=8,
            ascii_font=CODE_FONT, east=EA_FONT,
            before=4 if idx == 0 else 0,
            after_sp=4 if idx == len(lines) - 1 else 0,
            shading="F2F2F2", line=1.0, snap_off=True,
            align=WD_ALIGN_PARAGRAPH.LEFT,
            keep_together=True,
            keep_with_next=(idx < len(lines) - 1),
        )
    return cur


def caption(after, text):
    par = doc.add_paragraph()
    par.style = doc.styles["Normal"]
    run = par.add_run(text)
    set_run(run, size=9, bold=True)
    pf = par.paragraph_format
    pf.space_before = Pt(6)
    pf.space_after = Pt(2)
    pf.keep_with_next = True
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_indent(par, first_pt=0)
    set_snap_off(par)
    after.addnext(par._p)
    return par._p


def table(after, cap, rows, widths, keep=True):
    cur = caption(after, cap)
    tbl = doc.add_table(rows=len(rows), cols=len(rows[0]))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    tbl_pr = tbl._tbl.tblPr
    for existing in tbl_pr.findall(qn("w:tblW")):
        tbl_pr.remove(existing)
    tbl_w = OxmlElement("w:tblW")
    tbl_w.set(qn("w:w"), str(int(sum(widths) * 567)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_pr.insert_element_before(
        tbl_w,
        "w:jc", "w:tblCellSpacing", "w:tblInd", "w:tblBorders", "w:shd", "w:tblLayout",
        "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription", "w:tblPrChange",
    )

    # 固定列宽：否则 Word/LibreOffice 会按内容重新分配，窄列被挤成竖排
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.insert_element_before(
        layout,
        "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription", "w:tblPrChange",
    )

    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "808080")
        borders.append(el)
    tbl_pr.insert_element_before(
        borders,
        "w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook", "w:tblCaption",
        "w:tblDescription", "w:tblPrChange",
    )

    cell_mar = OxmlElement("w:tblCellMar")
    for edge in ("left", "right"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:w"), "80")
        el.set(qn("w:type"), "dxa")
        cell_mar.append(el)
    tbl_pr.insert_element_before(
        cell_mar, "w:tblLook", "w:tblCaption", "w:tblDescription", "w:tblPrChange",
    )

    for idx, w in enumerate(widths):
        tbl.columns[idx].width = Cm(w)
    for r_idx, row in enumerate(rows):
        tbl.rows[r_idx].height = Cm(0.6)
        tbl.rows[r_idx].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        tr_pr = tbl.rows[r_idx]._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        cant_split.set(qn("w:val"), "true")
        tr_pr.append(cant_split)
        for c_idx, value in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.width = Cm(widths[c_idx])
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER if r_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            )
            p.paragraph_format.keep_together = True
            if keep and r_idx < len(rows) - 1:
                p.paragraph_format.keep_with_next = True
            set_snap_off(p)
            run = p.add_run(str(value))
            set_run(run, size=9, bold=(r_idx == 0))
            if r_idx == 0:
                tc_pr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "E7E6E6")
                tc_pr.append(shd)
                th = OxmlElement("w:tblHeader")
                th.set(qn("w:val"), "true")
                tr_pr.append(th)
    cur.addnext(tbl._tbl)
    return tbl._tbl


def find_heading(text):
    for p in doc.paragraphs:
        if p.style.name == "Heading 1" and p.text.strip() == text:
            return p._p
    raise KeyError(text)


# ---------------------------------------------------------------------------
# 封面
# ---------------------------------------------------------------------------
cover = doc.tables[0]
cover_values = {
    "班级": "（请填写班级）",
    "姓名": "肖建飞",
    "学号": "（请填写学号）",
    "指导教师": "（请填写指导教师）",
    "完成日期": "2026 年 10 月 30 日",
}
for row in cover.rows:
    key = row.cells[0].text.strip()
    if key in cover_values:
        cell = row.cells[1]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(cover_values[key])
        set_run(run, size=10.5)

doc.core_properties.title = "DevOps 实践与项目验收交付 实验报告"
doc.core_properties.subject = "Java 高级编程实验报告（课程代号 33252070）"
doc.core_properties.author = "肖建飞"


# ---------------------------------------------------------------------------
# 3 分析问题和确定解决方案
# ---------------------------------------------------------------------------
def section3():
    cur = find_heading("分析问题和确定解决方案；")
    cur = para(cur, "05 阶段交付的工程已经满足“能跑”：java -jar 可以启动，113 个测试全部通过，"
                    "登录、分页、校验、部署都有实现。但把评价标准从“代码能跑”换成“能否稳定交付、"
                    "能否复现演示、能否让 AI 产出可审查”，工程仍然存在五类缺口。")

    cur = lead(cur, "（1）交付验证靠手工，质量结论无法回溯到某次提交。",
               "05 阶段的构建、测试、打包都在本机执行，测试结果只存在于当时的终端输出；"
               "把 target/task-springboot.jar 拷到另一台机器时，无法证明它对应的代码是否通过了测试。"
               "一旦有人提交了破坏性修改，只要没人在本地重新跑一遍 mvn clean test，问题就会漏到验收现场，"
               "这正是报告所说的“在我电脑上能跑”的交付漏洞。")

    cur = lead(cur, "（2）文档与代码不同频，接口没有可执行的契约。",
               "README 仍然是 05 阶段的演进叙述，没有架构简图、技术栈徽标、环境依赖和一键启动；"
               "页面控制器只返回 HTML，外部脚本无法调用，也没有一份写清入参、出参、错误码的 API 手册。"
               "当代码调整字段或状态码时，文档只能靠人记忆同步，时间一长必然漂移。")

    cur = lead(cur, "（3）AI 生成代码缺少评审闭环。",
               "如果直接把 AI 生成的 REST 接口贴进工程，初稿会出现三类典型问题："
               "排序参数被拼进 ORDER BY 造成 SQL 注入；批量改状态写成循环 updateById 造成 N+1；"
               "findById 返回 null 时直接解引用造成 NPE，最终被兜底成 500。"
               "这些问题都能编译、也能在“数据正常”的手测中通过，只有评审和针对性测试才能提前拦住。")

    cur = lead(cur, "（4）Demo 依赖临场发挥，异步处理没有可观察载体。",
               "验收现场如果只靠临时点页面，很容易出现“数据被改乱、端口被占用、错误路径没准备”的尴尬；"
               "同时 05 阶段的写操作是同步的，没有任何异步链路，无法展示报告要求的“异步处理表现”，"
               "也无法说明异步带来的响应时间与故障隔离收益。")

    cur = lead(cur, "（5）质量数据无法量化，复盘缺少证据。",
               "没有 CI 运行记录、没有 PR 审查意见、没有测试数量与拦截缺陷的统计，"
               "就无法回答“AI 在哪些环节提效、提效多少”以及“人类评审拦住了哪些 AI 隐患”。"
               "答辩时只能讲感受，不能讲数据。")

    cur = para(cur, "针对上述缺口，本次改造确定的总体方案是：用 GitHub Actions 把“编译—测试—打包—归档”"
                    "固化成流水线；在不重写前端的前提下增加一套 REST 接口，用 OpenAPI 与 Markdown 形成双份契约；"
                    "以两个 PR 的形式模拟团队评审，先让 AI 生成初稿，再由人类审查并补测试；"
                    "增加异步审计作为“异步处理”的可观察载体；最后用可重复的 Demo 脚本和预置数据把验收流程固定下来。"
                    "问题、方案与验证方式的对应关系如表 1 所示。")
    cur = table(cur, "表 1  交付缺口、解决方案与验证方式", [
        ["缺口", "解决方案", "落地位置", "验证方式"],
        ["交付验证手工", "GitHub Actions：clean test 门禁 + package + Artifact", ".github/workflows/ci.yml", "本地同命令 + Actions 运行"],
        ["文档滞后", "README + OpenAPI 3.0.3 + API 手册", "README.md、openapi.yaml、docs/api/API.md", "相对链接检查 + 契约测试"],
        ["接口缺失", "REST API + 统一响应体/错误码", "src/main/java/.../api", "18 个切片用例 + 15 步冒烟"],
        ["AI 代码隐患", "PR 评审 + 白名单/单条 SQL/显式 404", "docs/code-review、TaskSort、TaskBuss", "7 条审查意见 + 回归测试"],
        ["Demo 不可复现", "Demo 脚本 + 预置数据 + 异步审计", "docs/demo/DEMO.md、scripts", "重启重置 + 冒烟脚本"],
        ["质量不可量化", "181 用例、7 条意见、提效比表", "surefire、docs/ci、本报告", "构建日志 + 统计"],
    ], [2.8, 5.6, 3.6, 2.6])

    cur = para(cur, "几个关键决策需要说明：")
    cur = lead(cur, "① 在现有 MVC 工程上增加 REST 接口，而不是重写前后端分离。",
               "页面与接口复用同一个 ITaskBuss，业务规则只有一份；如果另起一套前端工程，"
               "就要额外处理跨域、鉴权、构建和部署，偏离了本阶段“交付流程”的重点。"
               "REST 控制器只做参数解析、视图转换和错误映射，业务校验仍留在业务层。")
    cur = lead(cur, "② CI 选择 GitHub Actions 托管 runner + Temurin 17 + Maven 缓存。",
               "托管 runner 不需要自建 Jenkins，PR 事件原生支持；JDK 17 与 pom.xml 的 java.version 对齐，"
               "Temurin 是免费且广泛使用的发行版；Maven 缓存可以把一次构建从数分钟降到一分钟左右，"
               "适合课堂项目反复触发。")
    cur = lead(cur, "③ 文档采用 OpenAPI 规范 + Markdown 手册双份，不引入额外的运行时文档组件。",
               "OpenAPI 3.0.3 的 YAML 可以被 Apifox、Postman、Swagger Editor 直接导入，"
               "也可以作为 CI 校验对象；Markdown 手册适合在仓库和报告里阅读。"
               "不引入 springdoc/Knife4j 可以避免与 Spring Boot 3.2 的版本矩阵耦合，"
               "也保证离线演示时文档仍然可用；契约是否漂移由 TaskRestControllerTest 的 JSON 断言兜底。")
    cur = lead(cur, "④ 排序字段使用枚举白名单，而不是字符串拼接或临时正则。",
               "白名单是“默认拒绝”：只有枚举里声明的 createTime、title、status 才可能进入 ORDER BY，"
               "列引用由 MyBatis-Plus 的 SFunction 生成，外部字符串永远不会拼进 SQL；"
               "非法字段在参数解析阶段就返回 400，不触达数据库。")
    cur = lead(cur, "⑤ 批量改状态使用一条 UPDATE ... WHERE id IN (...)，而不是循环 updateById。",
               "100 条任务从 100 次 UPDATE 降为 1 次，事务持有时间、网络往返和锁竞争都显著下降；"
               "编号先去重、过滤 null、限制最多 100 条，避免超长 IN 和长事务；返回实际影响行数，语义清晰。")
    cur = lead(cur, "⑥ 异步审计使用独立线程池 + 有界内存队列。",
               "审计是典型的“允许最终一致”的旁路逻辑，不应该阻塞主请求；独立线程池避免与 Tomcat 请求线程互相拖垮，"
               "CallerRunsPolicy 在队列满时退化为调用方执行，宁可慢一点也不丢事件；"
               "队列最多保留 200 条，重启即清空，生产环境应替换为消息队列 + 持久化审计表。")
    cur = lead(cur, "⑦ 未登录时页面 302、API 401 JSON，两条链路分开处理。",
               "页面需要把用户带到登录页并支持登录后回跳；API 调用方需要稳定的状态码和 JSON 错误体，"
               "不能拿到 302 或登录页 HTML。拦截器按路径前缀分流，既保持页面体验，也保证接口契约。")
    cur = lead(cur, "⑧ 测试以 H2 + 切片测试为主，集成测试兜底。",
               "CI 与验收机不需要安装 MySQL；@WebMvcTest 切片只装配 MVC，单测速度快；"
               "TaskApplicationTests 在 H2 上跑完整 Spring 容器，验证真实 SQL、事务、分页与异步审计，"
               "两者结合既快又可信。")


# ---------------------------------------------------------------------------
# 4 详细设计
# ---------------------------------------------------------------------------
def section4():
    cur = find_heading("详细设计")
    cur = para(cur, "本阶段在 05 阶段工程上增加“交付层”：CI 流水线、REST 接口与契约文档、PR 评审记录、"
                    "异步审计与 Demo 脚本。原有页面、登录、分页、校验逻辑保持不变，新增能力通过组合而非重写实现。"
                    "工程目录中与本次交付直接相关的部分如下（省略 target 与 IDE 文件）。")
    cur = code_block(cur, r"""
task-servlet-demo
├── .github/workflows/ci.yml          CI：clean test → package → artifact
├── docs
│   ├── api/API.md                    API 手册（入参/出参/错误码）
│   ├── code-review/PR-001-*.md       代码评审：注入 / N+1 / NPE / 测试
│   ├── code-review/PR-002-*.md       代码评审：CI 门禁 / 产物 / 权限
│   ├── demo/DEMO.md                  Demo 脚本与预置数据
│   └── ci/LOCAL-VERIFICATION.md      本地等价验证记录
├── scripts
│   ├── run-demo.ps1 / run-demo.sh    一键构建 + test 环境启动
│   └── api-smoke.ps1                 API 冒烟（15 项）
└── src/main
    ├── java/cn/edu/mju/band
    │   ├── api/                      REST 控制器、DTO、统一响应/异常
    │   ├── audit/                    异步审计服务、有界队列
    │   ├── buss/TaskSort.java        排序白名单
    │   └── config/AsyncConfig.java   审计线程池
    └── resources/static/openapi.yaml OpenAPI 3.0.3 规范
""")

    cur = sub_heading(cur, "4.1  总体架构与请求链路")
    cur = para(cur, "系统在原有 MVC 分层上增加 API 与异步两条支路：页面请求仍由 TaskController 渲染 Thymeleaf，"
                    "/api/** 请求由 TaskRestController 返回 JSON；两条支路复用同一套业务接口；"
                    "写操作完成后把审计事件投递到独立线程池，由 /api/audits 查询结果。各层职责如表 2 所示。")
    cur = table(cur, "表 2  分层结构与职责", [
        ["层次", "主要组件", "职责"],
        ["接入层", "LoginInterceptor、WebMvcConfig", "Session 鉴权；页面 302、API 401 JSON；放行登录页/静态资源/OpenAPI"],
        ["页面层", "TaskController、templates/*.html", "任务列表、新增/修改表单、登录页、错误页；@Valid 回显"],
        ["API 层", "TaskRestController、dto/*、TaskApiExceptionHandler", "分页/CRUD/批量状态/审计查询；统一响应体与错误码"],
        ["业务层", "ITaskBuss/TaskBuss、IUserBuss/UserBuss", "参数边界校验、默认状态、分页、批量更新、异常翻译"],
        ["持久层", "TaskMapper/UserMapper、MyBatis-Plus", "BaseMapper CRUD、LambdaQueryWrapper、分页插件、UPDATE ... IN"],
        ["异步层", "AsyncConfig、TaskAuditService、TaskAuditStore", "task-audit-* 线程池、有界队列、审计事件查询"],
        ["交付层", "ci.yml、README、OpenAPI、docs、scripts", "自动验证与打包、文档契约、评审记录、Demo 复现"],
    ], [2.0, 5.4, 7.2])

    cur = para(cur, "以带排序的分页查询和一次新增为例，请求链路如下：")
    cur = code_block(cur, r"""
GET /api/tasks?title=报告&status=1&sort=title,asc
→ LoginInterceptor：Session 有 loginUser 放行；否则 401 JSON
→ TaskRestController.list：SortSpec.parse("title,asc") → TaskSort.TITLE
→ TaskBuss.findPage：校验页码/状态；LambdaQueryWrapper + orderBy(column)
→ TaskMapper.selectPage：COUNT + SELECT ... ORDER BY title ASC LIMIT ?,?
→ PageResult<TaskView> → ApiResponse{code=0,...}

POST /api/tasks
→ @Valid TaskSaveRequest → TaskBuss.add → 主键回填
→ TaskAuditService.record(...)  @Async 立即返回
→ task-audit-1 线程写 TaskAuditStore → /api/audits 可查
""")

    cur = sub_heading(cur, "4.2  CI 流水线设计")
    cur = para(cur, "流水线以“提交即验证”为目标，把质量门禁放在打包之前。触发规则覆盖主分支 push、PR、手动运行；"
                    "同一分支的新提交会取消旧流水线，避免重复占用 runner。各阶段设计如表 3。")
    cur = table(cur, "表 3  CI 流水线阶段设计", [
        ["阶段", "命令/动作", "失败行为", "产物"],
        ["检出", "actions/checkout@v4", "流水线终止", "工作区源码"],
        ["环境", "setup-java@v4：Temurin 17 + Maven 缓存", "流水线终止", "JDK 17、依赖缓存"],
        ["质量门禁", "mvn -B -ntp clean test", "红灯，后续步骤不执行", "surefire 报告"],
        ["打包", "mvn -B -ntp package -DskipTests", "红灯，不产出 Artifact", "target/task-springboot.jar"],
        ["产物校验", "test -f + ls -lh 精确检查 JAR", "红灯，避免空产物", "文件信息"],
        ["归档", "upload-artifact：JAR + surefire", "步骤失败", "task-springboot-jar、surefire-reports"],
    ], [2.0, 6.2, 3.4, 3.0])

    cur = sub_heading(cur, "4.3  REST 接口与错误码设计")
    cur = para(cur, "接口只暴露任务资源与审计查询，共 7 个端点；全部返回统一响应体，成功 code=0，"
                    "失败时 HTTP 状态与业务码同时表达语义。端点设计如表 4，错误码如表 5。")
    cur = table(cur, "表 4  REST 端点设计", [
        ["方法", "路径", "说明", "成功状态"],
        ["GET", "/api/tasks", "分页查询：标题模糊、状态精确、白名单排序", "200"],
        ["GET", "/api/tasks/{id}", "按编号查询；不存在返回 404", "200"],
        ["POST", "/api/tasks", "新增；返回 Location 指向新资源", "201"],
        ["PUT", "/api/tasks/{id}", "修改；不存在返回 404", "200"],
        ["DELETE", "/api/tasks/{id}", "删除；不存在返回 404", "200"],
        ["PATCH", "/api/tasks/batch-status", "批量改状态；返回实际更新行数", "200"],
        ["GET", "/api/audits", "最近异步审计事件，limit 1~200", "200"],
    ], [1.6, 5.4, 6.2, 1.4])

    cur = table(cur, "表 5  统一错误码", [
        ["HTTP", "code", "含义", "典型场景"],
        ["400", "40001", "请求参数不合法", "空标题、状态 9、pageSize 101、非法排序、JSON 语法错误"],
        ["401", "40100", "未登录或会话过期", "未登录访问 /api/**"],
        ["404", "40401", "任务不存在", "查询/修改/删除不存在的 id"],
        ["500", "50001", "数据库暂时不可用", "连接失败、SQL 执行异常"],
        ["500", "50000", "未预期的服务器错误", "兜底异常，细节只写日志"],
    ], [1.4, 1.6, 3.4, 8.2])

    cur = para(cur, "响应体统一为 {code, message, data, timestamp}。参数校验失败时 data 是“字段 → 错误信息”的对象，"
                    "例如 {\"title\":\"任务标题不能为空\",\"status\":\"任务状态只能是 0/1/2\"}；"
                    "未登录时拦截器直接写 401 JSON，不进入控制器，也不重定向登录页。")

    cur = sub_heading(cur, "4.4  排序白名单与批量更新设计")
    cur = para(cur, "排序是外部可控、又必须进入 SQL 的典型参数，不能直接拼接。设计上把“外部字段名”收敛到 TaskSort 枚举，"
                    "枚举持有实体列引用；SortSpec 负责解析“字段,方向”，只允许 asc/desc，非法输入抛 IllegalArgumentException，"
                    "由 API 异常处理器转成 400。白名单如表 6。")
    cur = table(cur, "表 6  排序字段白名单", [
        ["对外字段", "实体列", "说明"],
        ["createTime", "create_time", "默认排序，降序展示最新任务"],
        ["title", "title", "按标题升/降序，便于按名称浏览"],
        ["status", "status", "按状态分组浏览"],
    ], [2.6, 3.0, 9.0])

    cur = para(cur, "业务层不再接收 String 排序片段，而是接收 TaskSort 与方向，调用 MyBatis-Plus 的 orderBy：")
    cur = code_block(cur, r"""
TaskSort order = sort == null ? TaskSort.CREATE_TIME : sort;
wrapper.orderBy(true, ascending, order.getColumn());
""")

    cur = para(cur, "批量改状态的设计分四步：① 校验状态非空且在 0/1/2；② 编号去重、过滤 null；"
                    "③ 限制单次最多 100 条；④ 用 UpdateWrapper 生成一条 UPDATE ... WHERE id IN (...)。"
                    "核心代码如下：")
    cur = code_block(cur, r"""
UpdateWrapper<Task> wrapper = Wrappers.update();
wrapper.set("status", status).in("id", distinctIds);
return taskMapper.update(null, wrapper);
""")

    cur = sub_heading(cur, "4.5  异步审计设计")
    cur = para(cur, "审计用于记录“谁在什么时候对哪个任务做了什么”，但不应该让用户等待。"
                    "设计上使用 Spring @Async + 独立线程池：控制器调用 TaskAuditService.record 后立即返回，"
                    "审计事件在线程池中写入有界队列，/api/audits 按时间倒序读取。线程池参数如表 7。")
    cur = table(cur, "表 7  审计线程池参数", [
        ["参数", "取值", "原因"],
        ["核心/最大线程", "2 / 4", "课堂演示足够，资源可控"],
        ["队列容量", "100", "短时突发可排队，避免无限堆积"],
        ["线程前缀", "task-audit-", "日志与 Demo 中一眼识别异步线程"],
        ["拒绝策略", "CallerRunsPolicy", "队列满时退化为调用方执行，不丢事件"],
        ["停机策略", "等待 5 秒", "应用退出前尽量写完审计"],
        ["存储上限", "200 条", "进程内有界队列，重启清空，生产换 MQ/审计表"],
    ], [2.4, 3.2, 9.0])

    cur = para(cur, "异步链路的时序是：写库成功 → 控制器提交审计任务 → 线程池分配 task-audit-N → 写队列 → 日志与查询可见。"
                    "审计失败不会回滚主流程；由于审计只写内存，不访问数据库，也不会出现“异步线程读不到未提交事务”的问题。")

    cur = sub_heading(cur, "4.6  文档体系设计")
    cur = para(cur, "文档不是一份 README 包打天下，而是按读者拆分：评审人看架构与验收，前端看接口契约，"
                    "答辩看 Demo 脚本，运维看 CI 与启动。文档清单如表 8。")
    cur = table(cur, "表 8  文档体系", [
        ["文档", "主要读者", "内容", "更新触发"],
        ["README.md", "教师/评审/新成员", "架构图、徽标、环境依赖、一键启动、核心特性、验收清单", "接口/依赖/启动方式变化"],
        ["openapi.yaml", "前端/测试/工具", "7 个端点、Schema、错误响应、示例", "DTO/状态码变化"],
        ["docs/api/API.md", "前端/答辩", "认证、错误码、逐接口入参出参示例、curl", "接口行为变化"],
        ["docs/code-review/*.md", "评审人", "PR 范围、问题、复现、修复、回归", "每次评审"],
        ["docs/demo/DEMO.md", "答辩人", "预置数据、正常/边界/异步场景、应急", "演示流程变化"],
        ["docs/ci/LOCAL-VERIFICATION.md", "教师/评审", "本地等价验证命令与输出", "CI 或测试变化"],
    ], [3.2, 3.4, 5.6, 2.4])

    cur = sub_heading(cur, "4.7  测试设计")
    cur = para(cur, "测试按“单元 → 切片 → 集成”分层：单元测试只 Mock Mapper，验证业务规则；"
                    "切片测试只装配 MVC，验证参数绑定、状态码、JSON 契约；集成测试启动完整 Spring 容器，"
                    "在 H2 上验证真实 SQL、事务与异步。用例分布如表 9。")
    cur = table(cur, "表 9  测试分层与用例分布", [
        ["层次", "测试类", "用例数", "关注点"],
        ["单元", "TaskBussTest", "72", "校验、边界、排序白名单、批量单条 SQL、异常翻译"],
        ["单元", "UserBussTest", "15", "登录成功/失败、空口令、Mapper 异常"],
        ["单元", "TaskSortTest、SortSpecTest", "28", "白名单、方向、注入载荷、格式错误"],
        ["单元", "TaskAuditStoreTest", "4", "倒序、200 条上限、边界"],
        ["切片", "TaskRestControllerTest", "18", "401/400/404/201、字段校验、注入、审计调用"],
        ["切片", "TaskControllerTest", "15", "页面参数绑定、@Valid 回显、登录拦截、错误页"],
        ["切片", "LoginControllerTest", "10", "登录成功/失败、回跳、防 open redirect、退出"],
        ["切片", "LoginInterceptorTest", "6", "页面 302、API 401 JSON、context-path"],
        ["切片", "HomeControllerTest", "1", "GET / 重定向 /task"],
        ["集成", "TaskApplicationTests", "12", "H2 分页、事务、登录、REST 全链路、异步审计"],
        ["合计", "11 个测试类", "181", "全部通过（mvn clean test）"],
    ], [2.2, 5.0, 2.0, 5.4])

    cur = sub_heading(cur, "4.8  Demo 演示设计")
    cur = para(cur, "Demo 按“先证明能用、再证明稳、最后证明快”的顺序组织，预置数据由 H2 脚本在每次启动时重建，"
                    "避免现场数据被改乱。场景与时长如表 10。")
    cur = table(cur, "表 10  Demo 场景设计", [
        ["场景", "操作", "预期", "时长"],
        ["正常链路", "登录 → 列表/搜索 → 新增 → 编辑 → 删除", "302 回列表、提示成功、数据同步", "5 min"],
        ["边界报错", "空标题、状态 9、pageSize 101、404、未登录、注入载荷", "400/401/404 + 业务码，不写库", "4 min"],
        ["异步处理", "连续新增 3 条任务，观察日志与 /api/audits", "task-audit-* 线程写入，响应不等待", "3 min"],
        ["CI 流水线", "Actions 运行页 + Artifact 下载", "test 绿灯、JAR 可下载", "2 min"],
        ["评审证据", "PR-001/PR-002 记录", "问题—复现—修复—测试闭环", "1 min"],
    ], [2.2, 6.4, 4.6, 1.4])

    cur = sub_heading(cur, "4.9  代码评审流程设计")
    cur = para(cur, "评审按 PR 模板组织：变更目标、影响范围、复现步骤、风险等级、修复方式、回归用例、合并检查清单。"
                    "评审人重点检查六类问题：")
    cur = para(cur, "① 安全：SQL/命令/模板注入、越权、敏感信息进入日志；"
                    "② 性能：N+1、循环内远程调用、无界集合；"
                    "③ 健壮性：空结果、空集合、类型转换、并发；"
                    "④ 契约：状态码、字段名、错误码、文档同步；"
                    "⑤ 测试：正常流、异常流、边界值是否有对应用例；"
                    "⑥ 过度设计：为演示引入不必要的中间件/框架。")
    cur = para(cur, "只有“门禁绿灯 + 评审意见关闭 + 回归用例通过”三个条件同时满足，PR 才允许合并；"
                    "评审记录归档到 docs/code-review，作为报告环节三的证据。")


# ---------------------------------------------------------------------------
# 5 实现
# ---------------------------------------------------------------------------
def section5():
    cur = find_heading("实现")
    cur = para(cur, "本节按“流水线 → 接口 → 安全修复 → 异步 → 文档 → 运行结果”的顺序说明关键实现。"
                    "代码均来自当前仓库，命令均在 JDK 17.0.1 + Maven 3.9.16 下实际执行。")

    cur = sub_heading(cur, "5.1  CI 流水线实现")
    cur = para(cur, "工作流文件 .github/workflows/ci.yml 的核心是：PR/push 触发、最小权限、同分支取消旧任务、"
                    "先测试后打包、精确路径归档。关键片段如下：")
    cur = code_block(cur, r"""
on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]
  workflow_dispatch:

permissions:
  contents: read
concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-java@v4
    with: { distribution: temurin, java-version: '17', cache: maven }
  - name: Quality gate - mvn clean test
    run: mvn -B -ntp clean test
  - name: Build artifact - mvn package
    run: mvn -B -ntp package -DskipTests
  - name: Upload executable jar
    uses: actions/upload-artifact@v4
    with: { name: task-springboot-jar, path: target/task-springboot.jar }
""")
    cur = para(cur, "门禁步骤失败时 GitHub Actions 会以非 0 退出终止后续步骤，因此测试不通过就不会产出 Artifact；"
                    "打包前先执行 test -f target/task-springboot.jar 并 ls -lh，防止“构建成功但产物名变了”悄悄通过；"
                    "surefire 报告用 if: always() 上传，失败时也能下载定位。")

    cur = sub_heading(cur, "5.2  REST 接口实现")
    cur = para(cur, "TaskRestController 负责参数绑定、调用业务层和组装响应。以列表与新增为例：")
    cur = code_block(cur, r"""
@RestController
@RequestMapping("/api/tasks")
public class TaskRestController {
    private final ITaskBuss taskBuss;
    private final TaskAuditService auditService;

    @GetMapping
    public ApiResponse<PageResult<TaskView>> list(
            @RequestParam(required = false) String title,
            @RequestParam(required = false) Byte status,
            @RequestParam(defaultValue = "1") int pageNum,
            @RequestParam(defaultValue = "10") int pageSize,
            @RequestParam(defaultValue = "createTime,desc") String sort) {
        SortSpec spec = SortSpec.parse(sort);
        Page<Task> page = taskBuss.findPage(title, status, pageNum, pageSize,
                spec.field(), spec.ascending());
        return ApiResponse.ok(PageResult.of(page, TaskView::from));
    }

    @PostMapping
    public ResponseEntity<ApiResponse<TaskView>> create(
            @Valid @RequestBody TaskSaveRequest request) {
        Task task = request.toEntity(null);
        if (!taskBuss.add(task)) {
            throw new TaskServiceException("任务创建失败，请稍后重试");
        }
        Task saved = taskBuss.findById(task.getId());
        auditService.record(TaskAuditService.ACTION_CREATE, task.getId(), task.getTitle());
        return ResponseEntity.status(HttpStatus.CREATED)
                .header(HttpHeaders.LOCATION, "/api/tasks/" + task.getId())
                .body(ApiResponse.ok("任务已创建", TaskView.from(saved != null ? saved : task)));
    }
}
""")
    cur = para(cur, "统一响应体是一个 record，提供 ok/error 工厂方法，时间戳截断到秒，避免响应里出现 7 位纳秒：")
    cur = code_block(cur, r"""
public record ApiResponse<T>(int code, String message, T data, String timestamp) {
    public static <T> ApiResponse<T> ok(T data) { ... }
    public static <T> ApiResponse<T> error(ApiErrorCode code, String message, T data) { ... }
}
""")
    cur = para(cur, "异常处理使用 @RestControllerAdvice(basePackages = \"cn.edu.mju.band.api\") + "
                    "@Order(HIGHEST_PRECEDENCE)，只接管 API 包下的控制器，并优先于页面侧的 GlobalExceptionHandler。"
                    "MethodArgumentNotValidException 返回 400 + 字段错误集合，IllegalArgumentException 返回 400，"
                    "TaskNotFoundException 返回 404，ServiceException 返回 50001，其余异常兜底 50000。")

    cur = sub_heading(cur, "5.3  排序白名单实现")
    cur = para(cur, "AI 初稿把 sort 参数直接拼进 SQL（wrapper.last(\"ORDER BY \" + sort)），"
                    "请求 sort=createTime;DROP TABLE t_task;-- 会生成危险片段。修复后改为枚举白名单：")
    cur = code_block(cur, r"""
public enum TaskSort {
    CREATE_TIME("createTime", Task::getCreateTime),
    TITLE("title", Task::getTitle),
    STATUS("status", Task::getStatus);

    public static TaskSort of(String field) {
        if (field == null || field.isBlank()) return CREATE_TIME;
        for (TaskSort sort : values()) {
            if (sort.field.equalsIgnoreCase(field.trim())) return sort;
        }
        throw new IllegalArgumentException(
                "不支持的排序字段：" + field + "（可选：createTime、title、status）");
    }
}
""")
    cur = para(cur, "SortSpec 再把“字段,方向”解析成 (TaskSort, boolean)，方向只接受 asc/desc；"
                    "业务层只接收枚举，不使用任何字符串拼接。对应测试覆盖 6 种注入载荷，"
                    "并在集成测试中验证注入请求后 t_task 仍有 7 条种子数据。")

    cur = sub_heading(cur, "5.4  批量改状态实现")
    cur = para(cur, "AI 初稿的写法是循环 updateById，N 条任务产生 N 条 UPDATE。修复后用一条 SQL 完成：")
    cur = code_block(cur, r"""
// 修复前：N 次 UPDATE（N+1）
for (Integer id : ids) {
    Task task = new Task();
    task.setId(id);
    task.setStatus(status);
    updated += taskMapper.updateById(task);
}

// 修复后：1 次 UPDATE ... IN (...)
List<Integer> distinctIds = ids.stream().filter(Objects::nonNull).distinct().toList();
UpdateWrapper<Task> wrapper = Wrappers.update();
wrapper.set("status", status).in("id", distinctIds);
return taskMapper.update(null, wrapper);
""")
    cur = para(cur, "业务层同时校验状态非空/合法、编号非空、去重后不超过 100 条；"
                    "测试通过捕获 UpdateWrapper 断言 sqlSet 含 status、sqlSegment 含 IN，并 verify(never()).updateById(...)，"
                    "从断言层面防止 N+1 回潮。")

    cur = sub_heading(cur, "5.5  异步审计实现")
    cur = para(cur, "线程池配置与审计服务如下：")
    cur = code_block(cur, r"""
@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean(name = "taskAuditExecutor")
    public ThreadPoolTaskExecutor taskAuditExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(4);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("task-audit-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(5);
        executor.initialize();
        return executor;
    }
}

@Async("taskAuditExecutor")
public void record(String action, Integer taskId, String detail) {
    TaskAuditEntry entry = new TaskAuditEntry(
            OffsetDateTime.now().withNano(0).format(TIME_FORMAT),
            Thread.currentThread().getName(), action, taskId, detail);
    store.add(entry);
    log.info("异步审计 action={} taskId={} detail={} thread={}", action, taskId, detail, entry.thread());
}
""")
    cur = para(cur, "AuditController 提供 GET /api/audits?limit=20，按时间倒序返回最近事件；"
                    "TaskAuditStore 用 ConcurrentLinkedDeque 保存最近 200 条，超出后淘汰最旧事件。"
                    "日志中可以直接看到 http-nio-18080-exec-* 与 task-audit-* 两种线程，Demo 时用于证明异步。")

    cur = sub_heading(cur, "5.6  页面 302 / API 401 的分流")
    cur = para(cur, "LoginInterceptor 在 Session 没有 loginUser 时先判断路径前缀：")
    cur = code_block(cur, r"""
if (isApiRequest(request)) {
    response.setStatus(HttpStatus.UNAUTHORIZED.value());
    response.setContentType(MediaType.APPLICATION_JSON_VALUE);
    response.setCharacterEncoding(StandardCharsets.UTF_8.name());
    objectMapper.writeValue(response.getWriter(),
            ApiResponse.error(ApiErrorCode.UNAUTHORIZED));
    return false;
}
// 页面请求：记录 GET 回跳地址，302 /login
""")
    cur = para(cur, "isApiRequest 会去掉 context-path 后判断 /api 或 /api/ 前缀；"
                    "对象映射器由 WebMvcConfig 构造注入，保证 401 响应与其他接口使用同一套 Jackson 配置。")

    cur = sub_heading(cur, "5.7  OpenAPI 文档与一键脚本")
    cur = para(cur, "OpenAPI 规范以 YAML 维护，描述 7 个端点、统一响应、任务/分页/审计 Schema、"
                    "公共参数与 400/401/404/500 响应。片段如下：")
    cur = code_block(cur, r"""
openapi: 3.0.3
info: { title: TaskMaster 任务管理 API, version: 1.0.0 }
servers:
  - { url: 'http://localhost:8080', description: dev }
  - { url: 'http://localhost:18080', description: test }
paths:
  /api/tasks:
    get:
      parameters:
        - { name: sort, in: query, schema: { type: string, default: 'createTime,desc' } }
      responses:
        '200': { description: 查询成功 }
        '400': { $ref: '#/components/responses/BadRequest' }
        '401': { $ref: '#/components/responses/Unauthorized' }
""")
    cur = para(cur, "规范文件放在 src/main/resources/static/openapi.yaml，应用启动后可通过 /openapi.yaml 访问，"
                    "可导入 Apifox/Postman/Swagger Editor；docs/api/API.md 则给出每个接口的中文说明与 curl 示例。"
                    "scripts/run-demo.ps1 把构建与启动合并为一条命令，scripts/api-smoke.ps1 用 15 个步骤验证主链路。")

    cur = sub_heading(cur, "5.8  运行结果")
    cur = para(cur, "使用 test 环境（H2 内存库）启动，日志确认 Profile 与端口：")
    cur = code_block(cur, r"""
$ java -jar target/task-springboot.jar --spring.profiles.active=test --server.port=18080
The following 1 profile is active: "test"
Tomcat started on port 18080 (http) with context path '/'
Started TaskApplication in 2.456 seconds
""")
    cur = para(cur, "登录后查询任务列表，返回统一响应体与分页结构：")
    cur = code_block(cur, r"""
$ curl -s -b cookie.txt 'http://localhost:18080/api/tasks?pageSize=1'
{
  "code": 0, "message": "成功",
  "data": {
    "records": [{
      "id": 7, "title": "代码评审", "content": "消除坏味道",
      "status": 0, "statusLabel": "待办", "createTime": "2026-10-07 09:00:00"
    }],
    "total": 7, "current": 1, "size": 1, "pages": 7
  },
  "timestamp": "2026-10-30T09:26:41+08:00"
}
""")
    cur = para(cur, "不存在的任务返回 404 + 40401；未登录返回 401 + 40100；"
                    "非法排序返回 400 + 40001，且表数据不受影响：")
    cur = code_block(cur, r"""
$ curl -s -b cookie.txt http://localhost:18080/api/tasks/9999
{"code":40401,"message":"任务不存在：9999","data":null,"timestamp":"..."}

$ curl -s http://localhost:18080/api/tasks
{"code":40100,"message":"未登录或会话已过期","data":null,"timestamp":"..."}

$ curl -s -b cookie.txt \
  'http://localhost:18080/api/tasks?sort=createTime%3BDROP%20TABLE%20t_task%3B--'
{"code":40001,"message":"不支持的排序字段：...（可选：createTime、title、status）",...}
""")
    cur = para(cur, "异步审计在日志中表现为独立线程，且 /api/audits 可查：")
    cur = code_block(cur, r"""
09:26:41 INFO [http-nio-18080-exec-3] ... TaskRestController - 创建任务
09:26:41 INFO [task-audit-1] ... TaskAuditService - 异步审计 action=CREATE taskId=8 ...
""")


# ---------------------------------------------------------------------------
# 6 测试
# ---------------------------------------------------------------------------
def section6():
    cur = find_heading("测试")
    cur = para(cur, "测试分为自动化测试与运行时验收两部分：自动化测试由 Maven/Surefire 执行，"
                    "运行时验收用 curl 与 PowerShell 脚本对真实启动的应用发请求。全部命令在 "
                    "JDK 17.0.1 + Maven 3.9.16 + Windows 10 下实际执行。")

    cur = sub_heading(cur, "6.1  自动化测试结果")
    cur = para(cur, "执行 mvn -B clean test，11 个测试类共 181 个用例（含参数化展开）全部通过：")
    cur = code_block(cur, r"""
[INFO] Tests run: 181, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
[INFO] Total time: 11.642 s
""")
    cur = table(cur, "表 11  测试类执行结果", [
        ["测试类", "用例数", "结果", "关键场景"],
        ["TaskBussTest", "72", "通过", "边界校验、排序白名单、批量单条 SQL、异常翻译"],
        ["TaskRestControllerTest", "18", "通过", "401/400/404/201、字段校验、注入、审计调用"],
        ["TaskControllerTest", "15", "通过", "页面参数绑定、@Valid 回显、登录拦截、错误页"],
        ["LoginControllerTest", "10", "通过", "登录成功/失败、回跳、防 open redirect、退出"],
        ["LoginInterceptorTest", "6", "通过", "页面 302、API 401 JSON、context-path"],
        ["TaskSortTest", "15", "通过", "白名单、大小写、6 种注入载荷"],
        ["SortSpecTest", "13", "通过", "字段/方向解析、格式错误、默认值"],
        ["TaskAuditStoreTest", "4", "通过", "倒序、200 条上限、边界"],
        ["UserBussTest", "15", "通过", "登录成功/失败、空口令、Mapper 异常"],
        ["TaskApplicationTests", "12", "通过", "H2 分页、事务、REST 全链路、异步审计"],
        ["HomeControllerTest", "1", "通过", "GET / 302 到 /task"],
        ["合计", "181", "全部通过", "单元 + 切片 + 集成"],
    ], [4.6, 2.0, 2.0, 6.0])

    cur = sub_heading(cur, "6.2  API 冒烟结果")
    cur = para(cur, "应用以 test 环境启动后，执行 scripts/api-smoke.ps1，15 个步骤全部 PASS：")
    cur = table(cur, "表 12  API 冒烟测试结果", [
        ["#", "步骤", "预期", "结果"],
        ["1", "登录并保存 Cookie", "响应包含 JSESSIONID", "PASS"],
        ["2", "GET /api/tasks", "200，code=0", "PASS"],
        ["3", "分页字段", "total/current/size/pages 完整", "PASS"],
        ["4", "POST /api/tasks", "201，data.id > 0", "PASS"],
        ["5", "GET /api/tasks/{id}", "200，标题一致", "PASS"],
        ["6", "PATCH 批量状态", "200，data=1", "PASS"],
        ["7", "批量后查询", "status=2（已完成）", "PASS"],
        ["8", "DELETE 任务", "200，code=0", "PASS"],
        ["9", "查询已删除任务", "404，code=40401", "PASS"],
        ["10", "空标题 + 状态 9", "400，data 含字段错误", "PASS"],
        ["11", "ORDER BY 注入载荷", "400，code=40001", "PASS"],
        ["12", "注入后查询", "200，表未被删除", "PASS"],
        ["13", "未登录访问", "401，code=40100", "PASS"],
        ["14", "GET /api/audits", "200，事件数 > 0", "PASS"],
        ["15", "审计线程名", "以 task-audit- 开头", "PASS"],
    ], [1.0, 5.6, 5.6, 2.4])

    cur = sub_heading(cur, "6.3  页面与 HTTP 验收结果")
    cur = para(cur, "除 API 外，对页面链路也做了验收，确保新增 API 没有破坏原有功能：")
    cur = table(cur, "表 13  页面与 HTTP 验收", [
        ["场景", "操作", "结果"],
        ["未登录访问", "GET /task", "302 → /login"],
        ["正确登录", "POST /login（admin/123456）", "302 → /task，Session 写入 loginUser"],
        ["错误密码", "POST /login（admin/bad）", "200，提示“用户名或密码错误”"],
        ["任务列表", "GET /task", "200，7 条任务、每页 3 条、3 页"],
        ["条件筛选", "GET /task?title=JaCoCo&status=1", "200，命中 1 条，翻页保留条件"],
        ["空标题", "POST /task?opt=add（title 空白）", "200，表单回显“任务标题不能为空”"],
        ["非法状态", "POST /task?opt=add（status=9）", "200，表单回显“任务状态只能是 0/1/2”"],
        ["退出登录", "POST /logout", "302 → /login?logout；再访问 /task 被拦截"],
        ["OpenAPI", "GET /openapi.yaml", "200，返回 OpenAPI 3.0.3 规范"],
        ["一键启动", "scripts/run-demo.ps1 -SkipBuild", "test 环境启动到 18080"],
    ], [3.0, 7.0, 4.6])

    cur = sub_heading(cur, "6.4  调试过程中遇到的问题与解决")
    cur = para(cur, "开发与验收过程中遇到的问题按“现象—原因—解决”记录如表 14。")
    cur = table(cur, "表 14  调试问题与解决", [
        ["问题", "现象", "原因", "解决办法"],
        ["PowerShell 脚本中文乱码", "Windows PowerShell 5.1 读取 .ps1 时中文变乱码，字符串引号解析报错", "文件为 UTF-8 无 BOM，5.1 按 ANSI 读取", "另存为 UTF-8 with BOM；脚本内路径/提示统一中文"],
        ["curl 传 JSON 丢引号", "POST 返回 400“请求参数格式错误”，JSON 字段名被吞", "PowerShell 向原生 curl 传参时会去掉双引号", "把 JSON 写入临时文件，用 --data-binary @file"],
        ["API 与页面异常处理冲突", "API 参数错误返回 HTML 错误页，前端无法解析", "页面异常处理器对所有控制器生效", "新增 API 专用异常处理器，并设为最高优先级"],
        ["切片测试缺少 JSON 序列化器", "切片测试启动失败，配置类构造注入失败", "拦截器需要 JSON 序列化器输出 401", "由配置类构造注入；切片测试自带 Jackson"],
        ["异步审计断言不稳定", "请求返回后立即查 /api/audits 偶发为空", "审计线程与测试线程并发，存在毫秒级延迟", "测试轮询最多 2 秒；断言线程名以 task-audit- 开头"],
        ["时间戳格式不一致", "响应 timestamp 出现 7 位纳秒，与文档示例不符", "时间对象默认带纳秒", "截断到秒（withNano(0)）"],
        ["空 records 序列化风险", "Mapper 返回空页时 PageResult 可能 NPE", "分页结果 records 可能为 null", "of() 中判空回退空列表，并加测试"],
    ], [3.2, 4.2, 3.4, 3.8], keep=False)

    cur = sub_heading(cur, "6.5  GitHub Actions 线上验证说明")
    cur = para(cur, "本仓库完成时未连接远程 GitHub 仓库，因此流水线以“本地同命令 + YAML 语法校验”验证："
                    "mvn -B clean test 与 mvn -B package -DskipTests 均成功，ci.yml 可被 YAML 解析器正常读取。"
                    "推送到 GitHub 后，Actions 会按同一份工作流执行：Quality gate → Build artifact → "
                    "Verify executable jar → Upload executable jar → Upload surefire reports，"
                    "运行页可直接下载 task-springboot-jar 与 surefire-reports。"
                    "本地等价验证的完整输出见 docs/ci/LOCAL-VERIFICATION.md。")


# ---------------------------------------------------------------------------
# 7 结果分析
# ---------------------------------------------------------------------------
def section7():
    cur = find_heading("结果分析；")
    cur = para(cur, "（1）调整后的优势。")
    cur = lead(cur, "① 交付从“手工验证”变成“提交即验证”。",
               "CI 把 clean test 设为质量门禁，测试失败不会产出 JAR；产物通过 Artifact 归档，"
               "评审人下载到的 JAR 与某次提交、某次测试结果一一对应，不再依赖“我本地跑过”。")
    cur = lead(cur, "② 文档与代码同频，接口有了可执行契约。",
               "README 提供架构图、徽标、环境依赖和一键启动；OpenAPI 规范与 API 手册写清了每个端点的入参、出参、"
               "错误码与示例；REST 切片测试对状态码和字段做断言，字段改名会先在测试里暴露，减少文档漂移。")
    cur = lead(cur, "③ 缺陷左移，AI 代码从“能跑”变成“可审查”。",
               "两个 PR 共记录 7 条审查意见，其中 3 条是 AI 初稿中的真实隐患：ORDER BY 注入、循环 updateById 的 N+1、"
               "findById 空结果 NPE。修复后分别由 TaskSortTest、TaskBussTest、TaskRestControllerTest 与集成测试锁定，"
               "同类问题再次出现会直接红灯。")
    cur = lead(cur, "④ Demo 可复现，异步处理有可观察载体。",
               "test 环境每次启动重建 7 条预置任务；run-demo 一条命令完成构建与启动；api-smoke 15 步覆盖正常、边界、"
               "未登录与审计；日志中 http-nio-* 与 task-audit-* 两种线程形成直观对比，现场不需要“碰运气”。")
    cur = lead(cur, "⑤ 质量数据可量化。",
               "自动化用例从 113 增加到 181，REST 端点从 0 增加到 7，审查意见 7 条，文档 6 份，"
               "CI 阶段 6 个；这些数字都可以在仓库、surefire 报告和 Actions 运行页复核，复盘不再只靠主观感受。")

    cur = para(cur, "交付指标的前后对比如表 15。")
    cur = table(cur, "表 15  05 阶段与 06 阶段交付指标对比", [
        ["指标", "05 阶段", "06 阶段", "变化"],
        ["自动化测试用例", "113", "181", "+68"],
        ["测试类", "7", "11", "+4"],
        ["REST 端点", "0", "7", "+7"],
        ["CI 流水线阶段", "0", "6", "从手工到自动"],
        ["OpenAPI/API 手册", "0", "2 份", "契约可导入"],
        ["PR 评审记录", "0", "2 份 / 7 条意见", "可追溯"],
        ["Demo 脚本/冒烟", "0", "1 份 + 15 步", "可复现"],
        ["构建产物", "手工拷贝 JAR", "Artifact 归档", "可追溯"],
    ], [4.0, 4.0, 4.2, 2.4])

    cur = para(cur, "（2）AI 提效比与人工投入对比。")
    cur = para(cur, "说明：下表的“人工基线”是按同类任务拆分后的经验估算（含编码、调试、写文档、补测试），"
                    "“AI 辅助实际”是本次任务的实际投入估算（含提示词设计、初稿审查、返工与验证）；"
                    "不同人、不同环境差异较大，数字用于说明量级，不作为精确工时。")
    cur = table(cur, "表 16  AI 提效比（估算）", [
        ["环节", "人工基线", "AI 辅助实际", "提效比", "说明"],
        ["CI 工作流", "1.5 h", "0.5 h", "3.0×", "初稿 + 权限/并发/产物路径修正"],
        ["REST 接口与 DTO", "4.0 h", "1.5 h", "2.7×", "初稿 7 个端点，评审后修 3 处"],
        ["测试用例（+68）", "5.0 h", "1.5 h", "3.3×", "参数化 + 切片 + 集成"],
        ["README/API/Demo 文档", "5.0 h", "1.5 h", "3.3×", "OpenAPI 与手册同步生成"],
        ["评审与修复", "2.0 h", "1.0 h", "2.0×", "7 条意见，逐条复现/回归"],
        ["合计", "17.5 h", "6.0 h", "约 2.9×", "按任务拆解估算"],
    ], [3.2, 2.6, 3.0, 2.0, 3.8])

    cur = para(cur, "从产出规模看：新增/改动的 Java 主代码约 513 行（API、DTO、审计、配置、排序白名单），"
                    "测试代码约 1 791 行，仓库共 84 个受版本控制的文件，文档约 5.7k 词。"
                    "AI 负责“快速铺开初稿与样板”，人类负责“定契约、挑风险、补边界”，两者分工比单纯追求生成速度更重要。")

    cur = para(cur, "（3）测试与评审对 AI 隐患的拦截。")
    cur = table(cur, "表 17  评审拦截的 AI 隐患与回归用例", [
        ["隐患", "初稿表现", "拦截方式", "回归用例"],
        ["SQL 注入", "ORDER BY 拼字符串，sort 可注入", "PR 评审 + 白名单改造", "TaskSortTest、TaskRestControllerTest、集成测试"],
        ["N+1", "批量改状态循环 updateById", "PR 评审 + 单条 UPDATE IN", "TaskBussTest#updateStatusBatch_*"],
        ["NPE", "findById 空结果直接解引用", "PR 评审 + 显式 404", "TaskRestControllerTest#shouldReturn404WhenTaskMissing"],
        ["CI 门禁缺失", "只打包不跑测试", "PR 评审 + clean test 前置", "工作流步骤 + 本地同命令"],
        ["产物混淆", "上传整个 target，混入 .original", "PR 评审 + 精确路径", "Verify executable jar 步骤"],
    ], [2.4, 5.0, 4.0, 3.2], keep=False)

    cur = para(cur, "（4）经验和体会。")
    cur = lead(cur, "① 先定契约，再让 AI 写实现。",
               "本次先写 OpenAPI 的路径、Schema、错误码，再生成 DTO 与控制器，返工明显减少；"
               "如果先写代码再补文档，字段名和状态码很容易对不上。")
    cur = lead(cur, "② 把“AI 可能犯错”写进流程，而不是写进信任。",
               "排序、批量、空结果这三类问题都不是编译错误，必须靠评审清单和针对性测试拦截；"
               "评审意见要写到“可复现、可回归”，否则改完仍可能回潮。")
    cur = lead(cur, "③ 质量门禁要放在产物之前。",
               "如果 CI 先打包再测试，红灯时 Artifact 已经产生，容易被误下载；"
               "把 clean test 放在 package 之前，失败即终止，产物才有意义。")
    cur = lead(cur, "④ 文档要能被工具消费。",
               "README 给人看，OpenAPI 给工具看，API 手册给答辩看；三者分工明确，"
               "再由测试锁定契约，文档才不是“写完就过期”的附件。")
    cur = lead(cur, "⑤ Demo 的稳定性也是工程质量。",
               "预置数据、固定端口、一键脚本、应急方案都要提前准备；现场少一次“重来”，"
               "就多一分钟讲清楚设计取舍。")

    cur = para(cur, "（5）局限与改进方向。")
    cur = para(cur, "① 当前未引入 Spring Security，写操作没有 CSRF token，生产环境需要补齐；"
                    "② 审计存储是进程内队列，重启即丢失，生产应改为 MQ + 持久化审计表；"
                    "③ OpenAPI 为手工维护的静态规范，后续可引入 springdoc 在运行时生成并做契约测试；"
                    "④ CI 尚未在远程 GitHub 仓库实际运行，推送后应补充 Actions 截图与失败演练；"
                    "⑤ 测试覆盖了主要分支，但未接入 JaCoCo 覆盖率门禁，可进一步把覆盖率纳入 CI。")


# ---------------------------------------------------------------------------
# 8 参考文献
# ---------------------------------------------------------------------------
def section8():
    cur = find_heading("参考文献")
    refs = [
        "[1] GitHub Docs. GitHub Actions：Workflow syntax、events、artifacts、permissions[EB/OL]. "
        "https://docs.github.com/en/actions",
        "[2] OpenAPI Initiative. OpenAPI Specification 3.0.3[EB/OL]. "
        "https://spec.openapis.org/oas/v3.0.3",
        "[3] Spring Boot Reference Documentation 3.2.x：Testing、Profiles、Packaging、Async[EB/OL]. "
        "https://docs.spring.io/spring-boot/docs/3.2.x/reference/html/",
        "[4] Spring Framework Reference Documentation 6.1：Web MVC、@RestControllerAdvice、HandlerInterceptor[EB/OL]. "
        "https://docs.spring.io/spring-framework/reference/",
        "[5] MyBatis-Plus Documentation：BaseMapper、UpdateWrapper、PaginationInnerInterceptor[EB/OL]. "
        "https://baomidou.com/",
        "[6] JUnit 5 User Guide：ParameterizedTest、Assertions、Extensions[EB/OL]. "
        "https://junit.org/junit5/docs/current/user-guide/",
        "[7] Mockito Documentation：Mocking、Verifying、ArgumentCaptor[EB/OL]. "
        "https://site.mockito.org/",
        "[8] OWASP. SQL Injection Prevention Cheat Sheet[EB/OL]. "
        "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
        "[9] Microsoft Learn. PowerShell 7 与 Windows PowerShell 5.1 编码、原生命令参数传递[EB/OL]. "
        "https://learn.microsoft.com/powershell/",
        "[10] 阿里巴巴集团. 阿里巴巴 Java 开发手册（黄山版）[S]. 2022.",
    ]
    for item in refs:
        cur = new_para(cur, item, first_pt=0, size=9.5, after_sp=3,
                       align=WD_ALIGN_PARAGRAPH.LEFT)


# ---------------------------------------------------------------------------
# 9 注意事项
# ---------------------------------------------------------------------------
def section9():
    cur = find_heading("注意事项")
    cur = para(cur, "（1）本报告中的 admin/123456 仅用于课堂演示，口令以明文保存在 t_user 中；"
                    "生产环境必须改为 BCrypt/Argon2 哈希存储，并修改默认密码。")
    cur = para(cur, "（2）当前未引入 Spring Security，写操作没有 CSRF token；正式上线应加 Spring Security "
                    "或至少校验 Origin/Referer，并为 Session Cookie 设置 secure。")
    cur = para(cur, "（3）prod 环境数据库账号应遵循最小权限原则，只授予 SELECT/INSERT/UPDATE/DELETE；"
                    "建表脚本由 DBA 执行，应用启动不自动改表。")
    cur = para(cur, "（4）审计事件保存在进程内队列，重启会清空；生产应改为消息队列 + 持久化审计表，"
                    "并设置合理的保留策略与脱敏规则。")
    cur = para(cur, "（5）修改 REST 接口时，先改 openapi.yaml 与 docs/api/API.md，再改 DTO/控制器，"
                    "最后跑 TaskRestControllerTest 与 api-smoke，避免文档与代码漂移。")
    cur = para(cur, "（6）GitHub Actions 的线上运行需在推送后查看；本地验证使用与 CI 完全相同的命令，"
                    "但 runner 的操作系统为 Ubuntu，首次运行需要下载依赖，耗时可能比本地更长。")
    cur = para(cur, "（7）本报告运行数据来自 2026 年 10 月 30 日的实际构建与启动（JDK 17.0.1、Maven 3.9.16、"
                    "Windows 10）；换 JDK、MySQL 或操作系统版本后，启动耗时和日志细节可能略有差异，"
                    "但构建、测试、启动与验收步骤不变。")


# ---------------------------------------------------------------------------
# 生成
# ---------------------------------------------------------------------------
section3()
section4()
section5()
section6()
section7()
section8()
section9()

# 去掉标题末尾多余的分号（“分析问题和确定解决方案；”“结果分析；”）
for par in doc.paragraphs:
    if par.style.name == "Heading 1" and par.text.rstrip().endswith("；"):
        for run in reversed(par.runs):
            if run.text.rstrip().endswith("；"):
                run.text = run.text.rstrip()[:-1]
                break

# 删除模板中的提示语，只保留正文
PROMPTS = {
    "根据自己的理解对关键细节说明原因。",
    "描述具体如何调整",
    "关键代码的解释说明及运行结果",
    "（1）列出你的测试结果。",
    "（2）调试过程中遇到的问题是如何解决的",
    "（1）调整后的优势（理解说明）；",
    "（2）经验和体会等。",
    "列出参考的相关资料和书籍。",
}
for par in list(doc.paragraphs):
    if par.text.strip() in PROMPTS:
        par._p.getparent().remove(par._p)

os.makedirs(OUT_DIR, exist_ok=True)
doc.save(OUT)
print("saved:", OUT)
print("paragraphs:", len(doc.paragraphs), "tables:", len(doc.tables))
