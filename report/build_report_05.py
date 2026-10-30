# -*- coding: utf-8 -*-
"""按 05 报告模板生成已填写的《Java 高级编程实验报告》。

模板来源：桌面上的 05_完整学号_姓名_题目_设计报告(TaskMaster 的 SpringBoot 现代化与部署上线).docx
输出：task-servlet-demo/report/05_..._已填写.docx
"""
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ROW_HEIGHT_RULE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

SRC = r"C:\Users\augenstern\Desktop\05_完整学号_姓名_题目_设计报告(TaskMaster 的 SpringBoot 现代化与部署上线).docx"
OUT_DIR = r"C:\Users\augenstern\Desktop\task-servlet-demo 5备份\task-servlet-demo\report"
OUT = os.path.join(OUT_DIR, "05_完整学号_姓名_题目_设计报告(TaskMaster 的 SpringBoot 现代化与部署上线)_已填写.docx")

doc = Document(SRC)

BODY_FONT = "Times New Roman"
EA_FONT = "宋体"
CODE_FONT = "Consolas"


# ---------------------------------------------------------------------------
# helpers（沿用 04 报告脚本的排版约定：正文 10.5pt、1.25 倍行距、首行缩进 2 字符）
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
             shading=None, line=1.25, snap_off=False, keep_together=False, keep_with_next=False):
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
    """加粗小标题 + 正文，同一段。"""
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
    return new_para(after, text, first_pt=0, size=10.5, bold=True, before=8, after_sp=2,
                    align=WD_ALIGN_PARAGRAPH.LEFT)


def code_block(after, text):
    cur = after
    lines = text.strip("\n").split("\n")
    for idx, line in enumerate(lines):
        cur = new_para(
            cur, line,
            first_pt=0,
            left_pt=14,
            size=8,
            ascii_font=CODE_FONT,
            east=EA_FONT,
            before=4 if idx == 0 else 0,
            after_sp=4 if idx == len(lines) - 1 else 0,
            shading="F2F2F2",
            line=1.0,
            snap_off=True,
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
        cell_mar,
        "w:tblLook", "w:tblCaption", "w:tblDescription", "w:tblPrChange",
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
    "完成日期": "2026 年 10 月 28 日",
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

doc.core_properties.title = "TaskMaster 的 SpringBoot 现代化与部署上线 实验报告"
doc.core_properties.subject = "Java 高级编程实验报告（课程代号 33252070）"
doc.core_properties.author = "肖建飞"


# ---------------------------------------------------------------------------
# 3 分析问题和确定解决方案
# ---------------------------------------------------------------------------
def section3():
    cur = find_heading("分析问题和确定解决方案；")
    cur = para(cur, "本次实验的起点是上一阶段的 Spring Boot 迁移版本：容器配置已经去掉，但视图层仍是 JSP，持久层仍是 MyBatis XML，"
                    "打包方式仍是 war，系统也没有登录边界。对照报告 05 的六个环节，当前工程主要存在五类问题。")

    cur = lead(cur, "（1）视图层无法静态预览，且锁死了 war 部署。",
               "JSP 需要 Servlet 容器编译，页面中的 Java 片段、JSTL 标签和 HTML 混在一起，不能像普通网页一样直接用浏览器打开；"
               "更关键的是 JSP 与 Spring Boot 可执行 JAR 不兼容，只要保留 JSP，就只能继续打 war、装外部 Tomcat，"
               "这与“java -jar 跨机部署”的目标直接冲突。")

    cur = lead(cur, "（2）持久层 SQL 手工维护，分页代码重复。",
               "原 TaskMapper.xml 为 CRUD、分页查询、count 统计分别写了 SQL，Service 里还要手算 "
               "(pageNum - 1) * pageSize 偏移量；条件查询依靠 XML 的 <if> 标签，表名、列名、字段长度发生变化时"
               "要同时改实体、Mapper、XML 和测试，维护成本高，也容易出现 SQL 与实体不一致。")

    cur = lead(cur, "（3）校验和异常处理分散，表单错误无法回显。",
               "控制层直接接收 @RequestParam，空标题、非法状态、页码越界等校验散落在业务层 if 语句中；"
               "校验失败后只能抛异常，页面不能保留用户已经填写的内容，也不能在对应输入框下提示具体错误；"
               "异常处理只覆盖了 IllegalArgumentException 和业务异常，缺少表单绑定失败等 MVC 层异常。")

    cur = lead(cur, "（4）没有登录边界。",
               "任何访问者只要知道 /task 地址就能直接查看、新增、修改、删除任务；没有用户表、没有 Session 会话、"
               "没有登录页和拦截器，无法区分“谁在操作”，也不满足报告环节五的要求。")

    cur = lead(cur, "（5）部署依赖重，环境切换仍不够彻底。",
               "war 部署要求目标机器安装 Tomcat 并手工拷贝应用；dev/test/prod 虽然已经拆成 YAML，但数据库初始化、"
               "每页条数、模板缓存等还没有形成完整的启动闭环，换一台机器仍要手工建库、建表、补账号。")

    cur = para(cur, "因此，本次改造的总体路线是：先把视图层从 JSP 换成纯 HTML 模板，解除 war 依赖；再把持久层从手写 MyBatis XML "
                    "换成 MyBatis-Plus 的 BaseMapper + 条件构造器 + 分页插件；然后用 @Valid + BindingResult + 全局异常处理补齐"
                    "服务端校验和错误回显；接着加入 t_user、登录页、Session 与 LoginInterceptor；最后把工程打成可执行 JAR，"
                    "用 dev/test/prod 三套 Profile 完成本地开发、自动化测试和跨机部署的闭环。各层的具体调整如表 1 所示。")
    cur = table(cur, "表 1  改造前后对照表", [
        ["层次", "改造前（04 阶段）", "改造后（05 阶段）", "调整原因"],
        ["构建与部署", "war 打包，依赖外部 Tomcat；JSP 由容器编译",
         "jar 打包，spring-boot-maven-plugin 生成可执行 JAR，内嵌 Tomcat",
         "一条 java -jar 命令即可跨机运行，不再安装容器"],
        ["视图层", "JSP + JSTL",
         "Thymeleaf 模板 + fragments 公共片段，classpath:/templates/",
         "模板是纯 HTML，可静态预览，且与可执行 JAR 兼容"],
        ["持久层", "MyBatis XML：7 个 CRUD/分页 SQL + 手写 LIMIT/COUNT",
         "BaseMapper + LambdaQueryWrapper + PaginationInnerInterceptor",
         "CRUD 与分页由框架生成，条件查询类型安全"],
        ["校验", "@RequestParam 手工接收，业务层 if 校验",
         "@Valid + BindingResult + 字段错误回显 + 全局错误提示",
         "声明式规则，错误可定位到字段，客户端绕过仍会被拦截"],
        ["异常", "只处理 IllegalArgumentException / TaskServiceException",
         "ServiceException 体系 + BindException + 统一 error.html（400/500）",
         "参数错误与服务故障分开，页面不暴露堆栈"],
        ["登录", "无用户、无 Session、无拦截器",
         "t_user + UserBuss + Session + LoginInterceptor + 登录/退出页",
         "建立会话边界，未登录访问自动跳转并在登录后回跳"],
        ["配置与初始化", "4 个 YAML，数据库表手工维护",
         "4 个 YAML + dev 自动初始化 + test H2 + prod 环境变量",
         "同一份代码适配开发、测试、生产三套环境"],
    ], [2.4, 4.2, 4.6, 3.4])

    cur = para(cur, "几个关键决策需要说明：")
    cur = lead(cur, "① 选择 Thymeleaf 而不是继续使用 JSP。",
               "Thymeleaf 模板本质上是 HTML，th:text、th:each、th:if 只是额外属性，浏览器会忽略它们，"
               "因此可以直接双击 templates/task.html 查看静态结构；这正好满足报告“验证静态可预览”的要求。"
               "代价是模板错误通常在运行时才暴露，所以本次把表单字段、分页链接、登录用户等关键表达式都放进了 HTTP 验收用例。")
    cur = lead(cur, "② 选择 MyBatis-Plus 而不是继续手写 XML。",
               "BaseMapper 直接提供 insert、updateById、deleteById、selectById、selectList、selectPage，"
               "原来 7 个 Mapper 方法和 63 行 XML 可以删掉；LambdaQueryWrapper 用方法引用指定列，"
               "拼错字段名会在编译期或启动期暴露。与此同时保留业务层校验和 DataAccessException 翻译，避免“用了框架就丢掉业务语义”。")
    cur = lead(cur, "③ 保留“接口 + 实现”的业务分层。",
               "ITaskBuss/IUserBuss 让控制层依赖抽象，单元测试可以用 Mockito 注入 Mapper、不启动容器；"
               "如果把 Mapper 直接写进 Controller，测试就会退化成集成测试，分页、校验、异常翻译也无法单独验证。")
    cur = lead(cur, "④ 用 jar 替代 war。",
               "JSP 是 war 依赖的根源；视图层换成 Thymeleaf 后，jar 不再需要外部 Tomcat。"
               "打包结果 target/task-springboot.jar 约 32.6 MB，内含 Tomcat、Jackson、Thymeleaf、MyBatis-Plus 等依赖，"
               "目标机器只需要 JDK 17 和 MySQL 客户端/服务，不再需要 Maven 或 Tomcat。")
    cur = lead(cur, "⑤ 登录表沿用既有 t_user 结构。",
               "实际 MySQL 库中的 t_user 列是 id/username/password，而不是 login_name/login_pwd。"
               "为了避免改线上表结构，User 实体用 @TableField(\"username\")、@TableField(\"password\") 做映射，"
               "Java 侧仍叫 loginName/loginPwd；H2 测试库与 MySQL 初始化脚本也统一使用 username/password。")
    cur = lead(cur, "⑥ 测试环境使用 H2 内存库。",
               "自动化测试不应依赖物理 MySQL。test Profile 使用 jdbc:h2:mem:taskdb;MODE=MySQL，"
               "启动时执行 schema-h2.sql 和 data-h2.sql，既能在没有 MySQL 的机器上跑完 113 个用例，"
               "又能验证 MyBatis-Plus 的 COUNT + LIMIT 分页在 MySQL 兼容模式下的行为。")


# ---------------------------------------------------------------------------
# 4 详细设计
# ---------------------------------------------------------------------------
def section4():
    cur = find_heading("详细设计")
    cur = para(cur, "改造后的工程按“启动类 + 配置类 + 业务接口/实现 + 控制层 + 持久层 + 模板 + 测试”组织，"
                    "目录结构如下（省略 target 与 IDE 文件）。")
    cur = code_block(cur, r"""
task-springboot
├── pom.xml                         Spring Boot 3.2.12 / jar / Thymeleaf / MP / Validation
├── README.md                       运行、部署、三次演进复盘与仪表盘
└── src
    ├── main/java/cn/edu/mju/band
    │   ├── TaskApplication.java     唯一启动类（@SpringBootApplication）
    │   ├── buss/                    ITaskBuss、IUserBuss
    │   │   └── impl/                TaskBuss、UserBuss
    │   ├── config/                  MybatisPlusConfig、TaskPageProperties、WebMvcConfig
    │   ├── controller/              TaskController、LoginController、HomeController
    │   │   ├── form/                LoginForm
    │   │   └── GlobalExceptionHandler / GlobalModelAttributes
    │   ├── entity/                  Task、User（MP 注解 + Validation 注解）
    │   ├── exception/               ServiceException 等 3 个异常类
    │   ├── interceptor/             LoginInterceptor
    │   ├── mapper/                  TaskMapper、UserMapper（BaseMapper）
    │   └── web/                     SessionKeys
    └── main/resources
        ├── application.yml          公共配置 + 默认 dev
        ├── application-dev.yml      MySQL、DEBUG、自动建表
        ├── application-test.yml     H2、每页 3 条
        ├── application-prod.yml     环境变量、日志落盘、模板缓存
        ├── db/                      schema/data 的 H2 与 MySQL 脚本
        ├── static/css/app.css       页面样式
        └── templates/               task、add_update、login、error、fragments/layout
""")

    cur = sub_heading(cur, "4.1  分层结构与职责")
    cur = para(cur, "各层职责与依赖方向如表 2 所示。控制层只负责参数接收、校验结果和视图选择；业务层负责边界校验、"
                    "默认值和异常翻译；持久层只负责数据访问；模板只负责展示，不写 Java 逻辑。")
    cur = table(cur, "表 2  系统分层与职责", [
        ["层次", "主要类/文件", "职责", "依赖方向"],
        ["启动与配置", "TaskApplication、application-*.yml、MybatisPlusConfig",
         "自动配置、Profile 切换、Mapper 扫描、分页插件", "配置 → 容器"],
        ["表现层", "TaskController、LoginController、templates/*.html",
         "路由、参数绑定、@Valid 校验、模型数据、页面渲染", "Controller → Buss"],
        ["业务层", "TaskBuss、UserBuss",
         "参数边界校验、默认状态、分页参数、DataAccessException 翻译", "Buss → Mapper"],
        ["持久层", "TaskMapper、UserMapper、Task/User",
         "BaseMapper CRUD、条件构造器、分页查询、结果映射", "Mapper → 数据库"],
        ["横切", "LoginInterceptor、GlobalExceptionHandler、GlobalModelAttributes",
         "登录拦截、统一错误页、向所有页面注入 loginUser", "拦截器/Advice → MVC"],
        ["测试", "7 个测试类", "单元、切片、集成、拦截器测试", "测试 → 各层"],
    ], [2.2, 5.0, 4.6, 2.8])

    cur = sub_heading(cur, "4.2  一次请求的处理流程")
    cur = para(cur, "以带条件的分页查询为例，请求从浏览器到页面的路径如下：")
    cur = code_block(cur, r"""
GET /task?title=报告&status=1&pageNum=2&pageSize=3
  → LoginInterceptor.preHandle
      Session 中有 loginUser：放行
      没有 loginUser：GET 记录原始地址到 loginRedirect，302 /login
  → TaskController.list
      归一化空关键字；解析 status；取 Profile 默认 pageSize
  → TaskBuss.findPage
      校验 pageNum/status/pageSize；创建 Page(2,3)
  → TaskMapper.selectPage
      MP 生成 COUNT(*) 和 SELECT ... ORDER BY create_time DESC LIMIT ...
  → task.html
      th:each 渲染 records；分页链接携带 title/status；th:if 处理空列表
""")
    cur = para(cur, "登录请求的流程相反：POST /login → LoginForm 校验 → UserBuss.login → Session 写入 loginUser → "
                    "读取 loginRedirect → 302 回原地址；退出时 POST /logout → session.invalidate() → 302 /login?logout。")

    cur = sub_heading(cur, "4.3  数据库设计")
    cur = para(cur, "数据库共两张表：t_task 保存任务，t_user 保存登录账号。t_user 沿用 TaskMaster 既有结构，"
                    "避免为了实验去改线上表；t_task 与旧版字段保持一致，只额外用 MyBatis-Plus 注解声明主键策略。")
    cur = table(cur, "表 3  数据库表设计", [
        ["表名", "字段", "类型/约束", "说明"],
        ["t_task", "id", "INT，主键，AUTO_INCREMENT", "任务编号"],
        ["t_task", "title", "VARCHAR(100)，NOT NULL", "任务标题，业务层限长 100"],
        ["t_task", "content", "TEXT，可空", "任务内容"],
        ["t_task", "status", "TINYINT，默认 0", "0 待办 / 1 进行中 / 2 已完成"],
        ["t_task", "create_time", "TIMESTAMP，默认 CURRENT_TIMESTAMP", "创建时间，MP 插入时留空由数据库填充"],
        ["t_user", "id", "INT，主键，AUTO_INCREMENT", "用户编号"],
        ["t_user", "username", "VARCHAR(50)，NOT NULL，UNIQUE", "登录名，Java 侧映射为 loginName"],
        ["t_user", "password", "VARCHAR(50)，NOT NULL", "口令，教学示例为明文，生产应存 BCrypt"],
    ], [1.8, 2.6, 5.8, 4.4])
    cur = para(cur, "初始化数据由 db 目录下的脚本负责：H2 的 schema-h2.sql/data-h2.sql 提供 7 条任务和 admin 账号；"
                    "MySQL 的 schema-mysql.sql 使用 CREATE TABLE IF NOT EXISTS，data-mysql.sql 用幂等 INSERT 补 admin，"
                    "并且只在 t_task 为空时补 3 条演示任务。因此脚本可以重复执行，不会重复插入。")

    cur = sub_heading(cur, "4.4  分页与条件查询设计")
    cur = para(cur, "分页使用 MyBatis-Plus 的 Page<Task>，业务层不再手算偏移量，也不再单独写 count SQL。核心逻辑是：")
    cur = code_block(cur, r"""
Page<Task> page = new Page<>(pageNum, pageSize);

LambdaQueryWrapper<Task> wrapper = Wrappers.lambdaQuery(Task.class);
if (StringUtils.hasText(title)) {
    wrapper.like(Task::getTitle, title.trim());
}
if (status != null) {
    wrapper.eq(Task::getStatus, status);
}
wrapper.orderByDesc(Task::getCreateTime);

return taskMapper.selectPage(page, wrapper);
""")
    cur = para(cur, "selectPage 会先执行 COUNT 查询，再执行带 LIMIT 的当前页查询；分页插件自动识别 MySQL/H2 方言，"
                    "所以 dev 的 MySQL 与 test 的 H2 可以共用同一份代码。PaginationInnerInterceptor 设置 maxLimit=100、"
                    "overflow=false：前者与 TaskBuss.MAX_PAGE_SIZE 对齐，后者让页码超过末页时返回空页而不是偷偷回到第一页。"
                    "控制层另外计算最多 5 个页码的窗口 pageNumbers，避免总页数很大时生成成百上千个分页链接；"
                    "分页链接统一携带 title/status，翻页不会丢失筛选条件。")

    cur = sub_heading(cur, "4.5  表单校验与错误回显设计")
    cur = para(cur, "校验分为两层：第一层是 HTML 的 required/maxlength，只用于改善输入体验；第二层是服务端的 Jakarta Validation，"
                    "由 @Valid 触发，无法被浏览器或 curl 绕过。Task 字段规则如下：")
    cur = table(cur, "表 4  Task 字段校验规则", [
        ["字段", "注解", "规则", "错误提示/回显位置"],
        ["title", "@NotBlank", "不能为 null、空串或纯空白", "“任务标题不能为空”，显示在标题输入框下"],
        ["title", "@Size(max = 100)", "长度不超过 100", "“任务标题不能超过 100 个字符”"],
        ["status", "@NotNull", "必须选择状态", "“请选择任务状态”"],
        ["status", "@Min(0) / @Max(2)", "只能是 0/1/2", "“任务状态只能是 0/1/2”"],
    ], [2.2, 3.4, 4.8, 4.2])
    cur = para(cur, "控制层的写法是 @Valid @ModelAttribute(\"task\") Task task, BindingResult bindingResult；"
                    "如果 bindingResult.hasErrors() 为真，直接把请求转发回 add_update 模板，不调用业务层。"
                    "模板用 th:object=\"${task}\" 绑定对象，用 th:field 生成 name/value/id，用 th:errors=\"*{title}\" 显示字段错误，"
                    "用 #fields.hasGlobalErrors() 显示“任务编号不能为空”这类全局错误。登录表单 LoginForm 同样使用 @NotBlank，"
                    "空用户名/空密码会分别在登录页对应输入框下提示。")

    cur = sub_heading(cur, "4.6  登录、Session 与拦截器设计")
    cur = para(cur, "登录功能由四部分组成：t_user 表、UserBuss 登录校验、LoginController 会话写入、LoginInterceptor 统一拦截。"
                    "UserBuss 按 username 查一条记录，账号不存在、密码错误、数据库中口令为空都返回 null；"
                    "控制层统一提示“用户名或密码错误”，不暴露账号是否存在。口令比较使用 MessageDigest.isEqual，"
                    "避免按字符短路比较带来的时序差异（生产环境应改为 BCrypt 校验）。")
    cur = para(cur, "登录成功后把 User 放入 Session 的 loginUser 属性，并在放入前清空 loginPwd；同时调用 request.changeSessionId() "
                    "更换 Session ID，防御会话固定攻击。LoginInterceptor 注册在 /** 上，放行登录/退出、静态资源、错误页和首页；"
                    "未登录 GET 会把 requestURI + queryString 保存到 loginRedirect，登录成功后只允许回跳以“/”开头且不以“//”开头的站内地址，"
                    "防止 open redirect；未登录 POST 不保存回跳地址，避免把表单内容拼进 URL。退出时 session.invalidate()，"
                    "再回到 /login?logout 显示“已安全退出登录”。")

    cur = sub_heading(cur, "4.7  多环境配置与部署设计")
    cur = para(cur, "主配置 application.yml 只保留与环境无关的公共项：应用名、默认 Profile、Thymeleaf 编码、MyBatis-Plus 驼峰映射、"
                    "端口、Session Cookie 和日志格式。三套 Profile 只覆盖差异项，具体如表 5。")
    cur = table(cur, "表 5  三套环境的配置差异", [
        ["配置项", "dev", "test", "prod"],
        ["数据源", "MySQL localhost:3306/taskmaster", "H2 内存库 taskdb（MODE=MySQL）", "MySQL，URL/账号/密码取环境变量"],
        ["初始化", "启动执行 schema-mysql.sql + data-mysql.sql", "启动执行 schema-h2.sql + data-h2.sql", "spring.sql.init.mode=never，由 DBA 执行脚本"],
        ["每页条数", "5", "3", "10"],
        ["模板缓存", "false（改模板立即生效）", "false", "true（生产性能）"],
        ["日志", "DEBUG，打印 SQL", "root=WARN，业务层 INFO", "root=WARN，写入 logs/task-springboot.log"],
    ], [3.0, 4.4, 4.2, 3.0])
    cur = para(cur, "部署时只需要把 target/task-springboot.jar 和 db/schema-mysql.sql（可选 data-mysql.sql）拷到目标机器，"
                    "安装 JDK 17 与 MySQL 8 后执行建表脚本，再通过 DB_URL/DB_USERNAME/DB_PASSWORD 注入生产库连接，"
                    "执行 java -jar task-springboot.jar --spring.profiles.active=prod 即可启动。容器化、Nginx、HTTPS 属于后续运维增强，"
                    "不在本次实验的必做范围内。")


# ---------------------------------------------------------------------------
# 5 实现
# ---------------------------------------------------------------------------
def section5():
    cur = find_heading("实现")
    cur = para(cur, "实现环境为 Windows + JDK 17.0.1 + Maven 3.9.16 + Spring Boot 3.2.12 + MyBatis-Plus 3.5.7 + "
                    "Thymeleaf 3.1.2 + H2 2.2.224 + MySQL 8.x。构建与启动命令如下：")
    cur = code_block(cur, r"""
mvn clean package                       # 编译 + 113 个测试 + 打可执行 JAR
java -jar target/task-springboot.jar --spring.profiles.active=test --server.port=18080
java -jar target/task-springboot.jar   # dev，默认连接本机 MySQL
""")

    cur = sub_heading(cur, "5.1  可执行 JAR 与依赖配置")
    cur = para(cur, "pom.xml 的打包方式从 war 改为 jar，父工程使用 spring-boot-starter-parent 统一版本；"
                    "新增 Thymeleaf、Validation、MyBatis-Plus 三个 Starter，移除 JSP/JSTL/tomcat-embed-jasper。"
                    "spring-boot-maven-plugin 在 package 阶段把依赖重新打进 BOOT-INF，生成可直接运行的 fat jar。")
    cur = code_block(cur, r"""
<packaging>jar</packaging>
<properties>
    <java.version>17</java.version>
    <mybatis-plus.version>3.5.7</mybatis-plus.version>
</properties>
<dependencies>
    <dependency><groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-thymeleaf</artifactId></dependency>
    <dependency><groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId></dependency>
    <dependency><groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
        <version>${mybatis-plus.version}</version></dependency>
</dependencies>
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
</plugin>
""")

    cur = sub_heading(cur, "5.2  实体与 Mapper：用注解替代 XML")
    cur = para(cur, "Task 用 @TableName 声明表名，@TableId(type = IdType.AUTO) 声明自增主键，@TableField(\"create_time\") "
                    "声明下划线列名；Validation 注解直接加在字段上，控制层 @Valid 时复用同一套规则。"
                    "User 的 username/password 通过 @TableField 映射为 loginName/loginPwd，从而兼容既有数据库。")
    cur = code_block(cur, r"""
@TableName("t_task")
public class Task {
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    @NotBlank(message = "任务标题不能为空")
    @Size(max = 100, message = "任务标题不能超过 100 个字符")
    private String title;

    @NotNull(message = "请选择任务状态")
    @Min(value = 0, message = "任务状态只能是 0/1/2")
    @Max(value = 2, message = "任务状态只能是 0/1/2")
    private Byte status;

    @TableField("create_time")
    private Date createTime;
}

public interface TaskMapper extends BaseMapper<Task> { }
public interface UserMapper extends BaseMapper<User> { }
""")
    cur = para(cur, "MybatisPlusConfig 用 @MapperScan 扫描 mapper 包，并注册 MybatisPlusInterceptor；分页插件不写死 DbType，"
                    "由 MP 根据 JDBC URL 自动识别 MySQL 或 H2，因此 dev/test 可以共用配置。")
    cur = code_block(cur, r"""
@Configuration
@MapperScan("cn.edu.mju.band.mapper")
public class MybatisPlusConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        PaginationInnerInterceptor pagination = new PaginationInnerInterceptor();
        pagination.setMaxLimit(100L);
        pagination.setOverflow(false);
        interceptor.addInnerInterceptor(pagination);
        return interceptor;
    }
}
""")

    cur = sub_heading(cur, "5.3  业务层：分页、校验、异常翻译")
    cur = para(cur, "TaskBuss 保留原有接口和校验逻辑，只把持久层调用换成 BaseMapper；findPage 不再计算偏移量，"
                    "而是构造 Page 和 LambdaQueryWrapper 后交给 selectPage。所有 DataAccessException 仍被翻译成 "
                    "TaskServiceException，页面只看到“数据库暂时不可用，请稍后重试”。")
    cur = code_block(cur, r"""
@Override
public Page<Task> findPage(String title, Byte status, int pageNum, int pageSize) {
    checkPageArgs(pageNum, pageSize);
    checkStatus(status);

    Page<Task> page = new Page<>(pageNum, pageSize);

    LambdaQueryWrapper<Task> wrapper = Wrappers.lambdaQuery(Task.class);
    if (StringUtils.hasText(title)) {
        wrapper.like(Task::getTitle, title.trim());
    }
    if (status != null) {
        wrapper.eq(Task::getStatus, status);
    }
    wrapper.orderByDesc(Task::getCreateTime);

    try {
        return taskMapper.selectPage(page, wrapper);
    } catch (DataAccessException e) {
        throw wrap(e);
    }
}
""")

    cur = sub_heading(cur, "5.4  控制层：@Valid 校验与错误回显")
    cur = para(cur, "列表方法负责参数归一化和 pageNumbers 计算；新增/修改方法用 @Valid 触发校验，"
                    "BindingResult 紧跟其后。校验失败时不访问业务层，直接回到表单；成功时用 RedirectAttributes "
                    "写入 Flash 提示并重定向，避免刷新重复提交。删除只允许 POST，防止被浏览器预取或爬虫误删。")
    cur = code_block(cur, r"""
@GetMapping
public String list(@RequestParam(required = false) String title,
                   @RequestParam(required = false) String status,
                   @RequestParam(defaultValue = "1") Integer pageNum,
                   @RequestParam(required = false) Integer pageSize,
                   Model model) {
    if (pageSize == null) pageSize = pageProperties.getDefaultSize();
    if (title != null && title.trim().isEmpty()) title = null;
    Byte statusByte = parseStatus(status);
    Page<Task> page = buss.findPage(title, statusByte, pageNum, pageSize);
    model.addAttribute("page", page);
    model.addAttribute("searchTitle", title);
    model.addAttribute("searchStatus", statusByte);
    model.addAttribute("pageNumbers", pageNumbers(page));
    return "task";
}

@PostMapping(params = "opt=add")
public String add(@Valid @ModelAttribute("task") Task task,
                  BindingResult bindingResult, Model model,
                  RedirectAttributes ra) {
    if (bindingResult.hasErrors()) {
        model.addAttribute("opt", "add");
        return "add_update";
    }
    buss.add(task);
    ra.addFlashAttribute("message", "任务「" + task.getTitle() + "」已创建");
    return "redirect:/task";
}
""")

    cur = sub_heading(cur, "5.5  Thymeleaf 模板：静态可预览的页面")
    cur = para(cur, "公共页头/页脚抽到 fragments/layout.html，页面用 th:replace 引入；列表用 th:each 遍历 page.records，"
                    "状态用 th:if 控制样式，分页链接用 @{/task(...)} 自动处理 context-path。模板里没有 Java 代码，"
                    "把 task.html 直接拖进浏览器也能看到完整静态结构。")
    cur = code_block(cur, r"""
<header th:replace="~{fragments/layout :: header('list')}"></header>

<tr th:each="t : ${page.records}">
  <td th:text="${'#' + t.id}">#1</td>
  <td th:text="${t.title}">任务标题</td>
  <td>
    <span class="pill pill-todo" th:if="${t.status == 0}">待办</span>
    <span class="pill pill-doing" th:if="${t.status == 1}">进行中</span>
    <span class="pill pill-done" th:if="${t.status == 2}">已完成</span>
  </td>
</tr>

<a th:href="@{/task(pageNum=${page.current - 1},
                    title=${searchTitle}, status=${searchStatus})}">上一页</a>
""")
    cur = para(cur, "表单模板用 th:object 绑定 Task，用 th:field 生成输入框的 name/value/id，用 th:errors 回显字段错误。"
                    "注意 #fields 必须在 th:object 作用域内使用，所以全局错误提示被放在 form 内部，而不是 form 外部。")
    cur = code_block(cur, r"""
<form method="post" th:action="@{/task}" th:object="${task}">
  <div class="alert alert-danger" th:if="${#fields.hasGlobalErrors()}">
    <p th:each="err : ${#fields.globalErrors()}" th:text="${err}"></p>
  </div>
  <input type="hidden" name="opt" th:value="${opt}"/>
  <input type="hidden" th:field="*{id}"/>

  <input type="text" th:field="*{title}" maxlength="100"
         th:classappend="${#fields.hasErrors('title')} ? 'is-invalid'"/>
  <p class="field-error" th:if="${#fields.hasErrors('title')}"
     th:errors="*{title}">任务标题不能为空</p>

  <input type="radio" th:field="*{status}" value="0"><span>待办</span>
  <input type="radio" th:field="*{status}" value="1"><span>进行中</span>
  <input type="radio" th:field="*{status}" value="2"><span>已完成</span>
</form>
""")

    cur = sub_heading(cur, "5.6  登录与拦截器")
    cur = para(cur, "LoginController 负责登录页、登录提交和退出；登录成功后更换 Session ID、清空口令、写入 loginUser，"
                    "再根据 loginRedirect 回跳。LoginInterceptor 只做一件事：Session 中没有 loginUser 就重定向到 /login，"
                    "并记录原始 GET 地址。WebMvcConfig 负责把拦截器注册到 /**，并放行登录、静态资源、错误页和首页。")
    cur = code_block(cur, r"""
@PostMapping("/login")
public String login(@Valid @ModelAttribute("loginForm") LoginForm form,
                    BindingResult bindingResult, HttpServletRequest request) {
    if (bindingResult.hasErrors()) return "login";

    User user = userBuss.login(form.getLoginName(), form.getLoginPwd());
    if (user == null) {
        bindingResult.reject("login.failed", "用户名或密码错误");
        return "login";
    }

    HttpSession session = request.getSession(true);
    request.changeSessionId();
    String redirect = (String) session.getAttribute(SessionKeys.LOGIN_REDIRECT);
    session.removeAttribute(SessionKeys.LOGIN_REDIRECT);
    user.setLoginPwd(null);
    session.setAttribute(SessionKeys.LOGIN_USER, user);

    if (redirect != null && redirect.startsWith("/")
            && !redirect.startsWith("//") && !redirect.startsWith("/login")) {
        return "redirect:" + redirect;
    }
    return "redirect:/task";
}
""")
    cur = code_block(cur, r"""
public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                         Object handler) throws Exception {
    HttpSession session = request.getSession(true);
    if (session.getAttribute(SessionKeys.LOGIN_USER) != null) return true;

    if ("GET".equalsIgnoreCase(request.getMethod())) {
        String target = request.getRequestURI();
        if (request.getQueryString() != null) {
            target += "?" + request.getQueryString();
        }
        session.setAttribute(SessionKeys.LOGIN_REDIRECT, target);
    }
    response.sendRedirect(request.getContextPath() + "/login");
    return false;
}
""")

    cur = sub_heading(cur, "5.7  统一异常处理")
    cur = para(cur, "GlobalExceptionHandler 把三类异常映射到同一个 error.html：IllegalArgumentException 和 BindException 返回 400，"
                    "ServiceException 返回 500。这样参数错误能给出具体原因，数据库故障只给出统一文案，页面不会出现 Whitelabel 堆栈。")
    cur = code_block(cur, r"""
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public String handleIllegalArgument(IllegalArgumentException e, Model model) {
        model.addAttribute("error", e.getMessage());
        return "error";
    }

    @ExceptionHandler(BindException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public String handleBindException(BindException e, Model model) {
        String message = e.getBindingResult().getAllErrors().stream()
                .findFirst().map(DefaultMessageSourceResolvable::getDefaultMessage)
                .orElse("请求参数不合法");
        model.addAttribute("error", message);
        return "error";
    }

    @ExceptionHandler(ServiceException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public String handleServiceException(ServiceException e, Model model) {
        model.addAttribute("error", e.getMessage());
        return "error";
    }
}
""")

    cur = sub_heading(cur, "5.8  多环境配置与数据库初始化")
    cur = para(cur, "dev 使用本机 MySQL，并打开 spring.sql.init，首次启动自动建表、补 admin 账号；test 使用 H2 内存库，"
                    "每次启动执行 schema-h2.sql/data-h2.sql；prod 关闭自动初始化，由部署人员执行 schema-mysql.sql，"
                    "数据库连接全部来自环境变量。这样同一份代码在三套环境中的行为是可解释、可复现的。")
    cur = code_block(cur, r"""
# application-dev.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/taskmaster?createDatabaseIfNotExist=true...
    username: root
    password: "123456"
  sql:
    init:
      mode: always
      schema-locations: classpath:db/schema-mysql.sql
      data-locations: classpath:db/data-mysql.sql

# application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:taskdb;MODE=MySQL;DB_CLOSE_DELAY=-1
  sql:
    init:
      mode: always
      schema-locations: classpath:db/schema-h2.sql
      data-locations: classpath:db/data-h2.sql
""")

    cur = sub_heading(cur, "5.9  构建与运行结果")
    cur = para(cur, "执行 mvn clean package 后，编译、113 个测试、JAR 打包全部成功，关键输出如下：")
    cur = code_block(cur, r"""
[INFO] Tests run: 113, Failures: 0, Errors: 0, Skipped: 0
[INFO] Building jar: .../target/task-springboot.jar
[INFO] Replacing main artifact ... with repackaged archive
[INFO] BUILD SUCCESS
""")
    cur = para(cur, "以 test Profile 启动后，日志显示激活 test、端口 18080、启动耗时约 2.5 秒；浏览器访问 http://127.0.0.1:18080，"
                    "未登录访问 /task 会 302 到 /login，admin/123456 登录后能看到 7 条任务、每页 3 条、共 3 页。"
                    "以 dev Profile 启动时连接本机 MySQL，页面显示 10 条已有任务、每页 5 条，说明同一份代码可以通过 Profile 切换数据源。")


# ---------------------------------------------------------------------------
# 6 测试
# ---------------------------------------------------------------------------
def section6():
    cur = find_heading("测试")
    cur = para(cur, "测试按“纯单元 → 控制层切片 → 容器集成 → HTTP 验收”四层组织：越往下依赖越少、执行越快；"
                    "越往上越接近真实部署。全部用例使用 JUnit 5 + Mockito + AssertJ + Spring Test，当前共 113 个用例。")
    cur = table(cur, "表 6  测试用例分布与结果", [
        ["测试类", "用例数", "主要覆盖内容", "结果"],
        ["TaskBussTest", "61", "CRUD 正常流；null/空串/空白标题；标题 100/101 边界；状态 -1/0/1/2/3/127；"
                              "页码 0/-1；pageSize 0/-1/101/100；LambdaQueryWrapper 条件；数据库宕机异常翻译；校验先于 SQL", "通过"],
        ["UserBussTest", "15", "正确/错误密码；登录名 trim；账号不存在；数据库口令为 null；空参数不查库；用户表不可用", "通过"],
        ["TaskControllerTest", "15", "默认每页 5 条；筛选透传；空白归一化；非法状态 400；服务异常 500；"
                                     "新增/修改表单；空标题/非法状态回显；缺少编号；删除；未登录重定向", "通过"],
        ["LoginControllerTest", "10", "登录页；退出提示；已登录跳转；登录成功写 Session；回跳原地址；"
                                      "站外地址拦截；密码错误；空字段；用户服务异常；退出销毁 Session", "通过"],
        ["LoginInterceptorTest", "3", "已登录放行；未登录 GET 记录地址并重定向；未登录 POST 不记录表单", "通过"],
        ["HomeControllerTest", "1", "GET / 302 到 /task", "通过"],
        ["TaskApplicationTests", "8", "test Profile 生效；每页 3 条；H2 数据源；CRUD 全链路；"
                                      "MP 分页；状态/标题筛选；种子账号登录；空标题拦截", "通过"],
        ["合计", "113", "单元 + 切片 + 集成 + 拦截器", "全部通过"],
    ], [4.6, 1.8, 6.6, 1.6])

    cur = para(cur, "在 test Profile 下另外做了 26 项 HTTP 验收（使用脚本保存 Cookie，覆盖登录、分页、筛选、校验、增删改、退出、"
                    "错误页和静态资源），结果全部通过，摘要如表 7。")
    cur = table(cur, "表 7  运行时 HTTP 验收结果（摘要）", [
        ["场景", "请求/操作", "结果"],
        ["首页跳转", "GET /", "302 → /task"],
        ["未登录拦截", "GET /task", "302 → /login"],
        ["登录页", "GET /login", "200，包含登录表单"],
        ["错误密码", "POST /login（admin / bad）", "200，提示“用户名或密码错误”"],
        ["正确登录", "POST /login（admin / 123456）", "302 → /task，Session 写入 loginUser"],
        ["任务列表", "GET /task", "200，7 条任务、每页 3 条、3 页"],
        ["状态筛选", "GET /task?status=2", "200，只显示“已完成”"],
        ["标题筛选", "GET /task?title=JaCoCo", "200，命中 1 条"],
        ["空标题校验", "POST /task?opt=add（title=空格）", "200，表单回显“任务标题不能为空”"],
        ["非法状态校验", "POST /task?opt=add（status=9）", "200，表单回显“任务状态只能是 0/1/2”"],
        ["新增/修改/删除", "POST /task?opt=add/update/delete", "302 → /task，列表数据同步变化"],
        ["退出登录", "POST /logout", "302 → /login?logout；再次访问 /task 被拦截"],
        ["非法参数", "GET /task?status=abc", "400，错误页提示“任务状态参数非法：abc”"],
        ["静态资源", "GET /css/app.css", "200"],
    ], [3.0, 7.2, 4.4])

    cur = para(cur, "调试过程中遇到的问题按“现象—原因—解决”记录如表 8。这些问题基本覆盖了从依赖解析、旧构建残留、"
                    "测试环境限制到数据库结构兼容的主要风险。")
    cur = table(cur, "表 8  调试问题与解决办法", [
        ["问题", "现象", "原因", "解决办法"],
        ["Maven 依赖描述符读取失败", "IDE 报 Failed to read artifact descriptor for "
                                     "com.baomidou:mybatis-plus-spring-boot3-starter:3.5.7",
         "本地仓库只有 .lastUpdated 失败标记，没有真正的 POM/JAR；首次下载被中断",
         "删除 .lastUpdated，执行 mvn -U clean package 重新下载；IDE 执行 Maven: Reload All Maven Projects"],
        ["旧 target 残留 mapper XML", "应用启动报 Failed to parse mapping resource: target/classes/mapper/TaskMapper.xml",
         "mvn test 不会清理 target，旧构建的 XML 仍在 classpath；MP 自动扫描 mapper/*.xml",
         "执行 mvn clean package；迁移后确认 target/classes 下没有 mapper 目录"],
        ["Mockito 无法初始化", "测试启动报 Could not self-attach to current VM using external process",
         "受限终端禁止内联 MockMaker 的 JVM 自附加",
         "在 src/test/resources/mockito-extensions 放置 org.mockito.plugins.MockMaker，内容为 mock-maker-subclass"],
        ["t_user 列名不匹配", "dev 启动报 Unknown column 'login_name' in 'field list'",
         "既有库 t_user 实际是 id/username/password，不是 login_name/login_pwd",
         "User 用 @TableField(\"username\"/\"password\") 映射；H2 与 MySQL 脚本统一为 username/password"],
        ["Thymeleaf 全局错误不显示", "校验失败时页面没有错误提示，或模板解析报 #fields 不可用",
         "#fields 必须在 th:object 作用域内；全局错误提示最初放在 form 外",
         "把错误提示移入 form，使用 #fields.hasGlobalErrors()/th:errors"],
        ["JaCoCo 中文路径乱码", "测试启动时 JaCoCo agent 的 destfile 路径出现乱码，无法创建 jacoco.exec",
         "工作区目录名含中文，插件把绝对路径写入 argLine 时编码不一致",
         "报告 05 不要求覆盖率，移除 JaCoCo 插件；保留测试用例与测试报告"],
        ["分页方言差异", "担心 MySQL 的 LIMIT offset,size 在 H2 上不可用",
         "手写 SQL 时需要针对数据库改写法",
         "改用 MP 分页插件，自动识别 MySQL/H2；测试中确认 H2 生成 LIMIT ? OFFSET ?"],
    ], [2.8, 4.2, 4.0, 3.6], keep=False)

    cur = para(cur, "另外，控制层切片测试最初因为 LoginInterceptor 把 /task 拦到登录页而全部失败；在测试中为请求挂上已登录的 "
                    "MockHttpSession 后恢复正常，并补了未登录重定向用例。这也说明“登录功能一旦加入，所有原有页面测试都要考虑会话上下文”。")


# ---------------------------------------------------------------------------
# 7 结果分析
# ---------------------------------------------------------------------------
def section7():
    cur = find_heading("结果分析；")
    cur = para(cur, "（1）调整后的优势。")
    cur = lead(cur, "① 配置量明显下降。",
               "迁移前有 web.xml、springmvc.xml、applicationContext.xml、db.properties 和 TaskMapper.xml 五个配置源；"
               "迁移后没有任何 Spring XML，只剩 4 个 YAML 和 4 个 SQL 脚本，新增 Bean 只需加注解，新增页面只需加一个 HTML。")
    cur = lead(cur, "② 视图层真正可静态预览。",
               "Thymeleaf 模板是纯 HTML，task.html、add_update.html、login.html 可以直接在浏览器打开查看结构；"
               "同时不再依赖 JSP 容器，打包方式从 war 变成 jar，部署时不需要外部 Tomcat。")
    cur = lead(cur, "③ 持久层代码量减少。",
               "原 TaskMapper.xml 的 7 个 SQL（含 selectByPage、countByCondition）和 63 行 XML 被 BaseMapper 与 "
               "LambdaQueryWrapper 取代；分页偏移量、COUNT 语句、LIMIT 语法都由 MP 生成，Service 只描述“查什么”。")
    cur = lead(cur, "④ 校验和错误反馈更完整。",
               "标题为空、标题超长、状态越界、页码非法等错误都能在对应字段下回显；客户端 required 被绕过时，"
               "服务端 @Valid 仍然拦截；参数错误返回 400、数据库故障返回 500，页面不再出现 Whitelabel 堆栈。")
    cur = lead(cur, "⑤ 登录边界清晰。",
               "未登录访问 /task 会跳转登录页，登录后回到原地址；退出后 Session 销毁；登录成功更换 Session ID，"
               "回跳地址只允许站内路径，口令不进入 Session。")
    cur = lead(cur, "⑥ 部署和测试可复现。",
               "mvn clean package 生成 32.6 MB 的可执行 JAR，java -jar 约 2.5 秒启动；dev/test/prod 通过 Profile 切换，"
               "113 个测试和 26 项 HTTP 验收都可以重复执行，不再依赖“手工点页面”回归。")

    cur = para(cur, "（2）MyBatis-Plus 封装带来的代价。")
    cur = para(cur, "MyBatis-Plus 让 CRUD 和分页的代码量大幅下降，但封装不是免费的。表 9 从 SQL 可见性、N+1、复杂查询、"
                    "隐式行为和升级耦合五个角度说明代价及本工程的应对。")
    cur = table(cur, "表 9  MyBatis-Plus 封装代价与应对", [
        ["代价", "具体表现", "本工程的应对"],
        ["SQL 不可见", "条件构造器生成的 SQL 不在源码中，慢查询或结果异常时看不到最终语句",
         "dev 打开 cn.edu.mju.band.mapper=DEBUG，日志打印 Preparing/Parameters；复杂 SQL 仍保留 XML/注解作为补充"],
        ["N+1 风险", "selectList 后在循环里逐条查关联表，会产生 N+1 次查询",
         "当前任务表无关联；若增加“任务-标签”，改为批量 in 查询或自定义 join SQL"],
        ["复杂查询表达力弱", "多表 join、窗口函数、数据库特有语法用 Wrapper 写很别扭",
         "采用混合策略：简单 CRUD/条件查询用 BaseMapper，复杂报表 SQL 回到 XML 或 @Select"],
        ["隐式行为", "逻辑删除、字段自动填充、乐观锁等插件会改变 SQL 语义",
         "显式配置、写测试断言；不在业务层依赖隐式行为"],
        ["升级耦合", "MP 与 MyBatis、Spring Boot 存在版本兼容矩阵",
         "锁定 3.5.7，升级前跑完整测试；关注官方兼容说明"],
    ], [3.0, 6.2, 5.4])

    cur = para(cur, "（3）三次演进复盘与演进仪表盘。")
    cur = para(cur, "从 Servlet 到 SSM 再到 Spring Boot，三次演进解决的是不同层次的问题：第一次把 JDBC 和页面逻辑分离，"
                    "第二次用 Spring 管理对象和事务，第三次用 Starter、模板引擎、ORM 封装和可执行 JAR 把“能跑”推进到“易部署、可测试”。"
                    "复盘如表 10，仪表盘如表 11。")
    cur = table(cur, "表 10  三次演进复盘", [
        ["维度", "1.0 Servlet + JSP + JDBC", "2.0 SSM + MyBatis XML + JSP", "3.0 Spring Boot + Thymeleaf + MP + JAR"],
        ["启动", "外部 Tomcat + web.xml", "外部 Tomcat + web.xml + 两个 Spring XML", "SpringApplication.run() + 内嵌 Tomcat"],
        ["配置", "web.xml、JDBC 硬编码", "4 个 XML + db.properties", "4 个 YAML + Profiles，无 Spring XML"],
        ["视图", "JSP + JSTL", "JSP + JSTL", "Thymeleaf 纯 HTML，静态可预览"],
        ["持久层", "手写 JDBC/DAO", "MyBatis XML，手写分页 SQL", "BaseMapper + Wrapper + 分页插件"],
        ["校验", "无/手写 if", "业务层手写 if", "@Valid + BindingResult + 统一异常"],
        ["登录", "无", "无", "Session + LoginInterceptor"],
        ["部署", "war 丢进 Tomcat", "war 丢进 Tomcat", "java -jar 可执行 JAR，跨机部署"],
        ["测试", "无", "少量/无", "7 个测试类、113 个用例"],
    ], [2.2, 4.0, 4.2, 4.2])
    cur = table(cur, "表 11  演进仪表盘", [
        ["指标", "1.0", "2.0", "3.0", "变化"],
        ["配置源数量", "2", "5", "4 个 YAML", "配置集中、可读"],
        ["启动命令", "部署 war + 启 Tomcat", "部署 war + 启 Tomcat", "java -jar task-springboot.jar", "一条命令"],
        ["新增页面", "建 JSP + 改 XML", "建 JSP + 改 XML", "加一个 HTML", "零配置"],
        ["新增查询条件", "改 DAO + XML + Service", "改 Mapper XML + Service", "加一行 wrapper.eq(...)", "代码量下降"],
        ["分页 SQL", "手写 LIMIT + COUNT", "手写 LIMIT + COUNT", "插件生成", "少写两段 SQL"],
        ["表单校验", "无", "业务层 if", "注解 + BindingResult", "声明式、可回显"],
        ["未登录访问", "无登录", "无登录", "302 → /login → 回跳", "有会话边界"],
        ["部署依赖", "JDK + Tomcat + MySQL", "JDK + Tomcat + MySQL", "仅 JDK + MySQL", "少一个容器"],
        ["自动化测试", "0", "0/少量", "113 个用例", "可回归"],
    ], [2.6, 2.6, 3.6, 3.4, 2.4])

    cur = para(cur, "（4）经验和体会。")
    cur = lead(cur, "第一，迁移应先求等价、再求优化。",
               "本次没有一次性重写所有代码，而是按“视图 → 持久层 → 校验 → 登录 → 打包”逐层替换；每改一层就用测试或 HTTP 请求确认行为不变，"
               "出现问题时可以快速定位到最近一次改动。")
    cur = lead(cur, "第二，测试要覆盖边界和失败路径。",
               "标题 100/101、状态 -1/0/1/2/3/127、pageNum=0、pageSize=0/101、数据库宕机、用户表不可用等用例，"
               "比“只测正常流”更能暴露问题；113 个用例中相当一部分是异常流和边界值，这比单纯追求覆盖率更有价值。")
    cur = lead(cur, "第三，封装要有“安全带”。",
               "MyBatis-Plus 省掉了 SQL，但必须用 DEBUG 日志、测试断言和混合 SQL 策略补上可观测性；否则出现慢查询或 N+1 时很难排查。"
               "这也是报告要求讨论“封装代价”的原因。")
    cur = lead(cur, "第四，配置外置和依赖管理同样重要。",
               "多环境配置要明确优先级：命令行 > 环境变量 > application-{profile}.yml > application.yml；"
               "依赖下载失败时先看本地仓库是否有 .lastUpdated，再执行 mvn -U，而不是怀疑代码。")
    cur = lead(cur, "第五，遇到旧库结构要先核对再映射。",
               "本次实际库的 t_user 是 username/password，与实体命名的 loginName/loginPwd 不一致；通过 @TableField 做映射，"
               "既兼容旧库又保持 Java 语义清晰，比强行改表更安全。")


# ---------------------------------------------------------------------------
# 8 参考文献
# ---------------------------------------------------------------------------
def section8():
    cur = find_heading("参考文献")
    refs = [
        "[1] Spring Boot Reference Documentation 3.2.x：Auto-configuration、Profiles、Packaging、Testing[EB/OL]. "
        "https://docs.spring.io/spring-boot/docs/3.2.x/reference/html/",
        "[2] Spring Framework Reference Documentation 6.1：Web MVC、Validation、HandlerInterceptor[EB/OL]. "
        "https://docs.spring.io/spring-framework/reference/",
        "[3] Thymeleaf Documentation 3.1：Standard Expressions、Fragments、Spring Integration[EB/OL]. "
        "https://www.thymeleaf.org/documentation.html",
        "[4] MyBatis-Plus Documentation：BaseMapper、Wrapper、PaginationInnerInterceptor[EB/OL]. "
        "https://baomidou.com/",
        "[5] Jakarta Bean Validation 3.0 Specification / Hibernate Validator Reference[EB/OL]. "
        "https://jakarta.ee/specifications/bean-validation/3.0/",
        "[6] Jakarta Servlet 6.0 Specification：Session、Filter、changeSessionId[EB/OL]. "
        "https://jakarta.ee/specifications/servlet/6.0/",
        "[7] MySQL 8.0 Reference Manual：CREATE TABLE、LIMIT、utf8mb4[EB/OL]. "
        "https://dev.mysql.com/doc/refman/8.0/en/",
        "[8] Spring Boot Maven Plugin Reference：repackage、executable jar[EB/OL]. "
        "https://docs.spring.io/spring-boot/docs/3.2.x/maven-plugin/reference/html/",
        "[9] H2 Database Engine：Compatibility Modes（MODE=MySQL）[EB/OL]. "
        "https://www.h2database.com/html/features.html#compatibility",
    ]
    for item in refs:
        cur = new_para(cur, item, first_pt=0, size=9.5, after_sp=3, align=WD_ALIGN_PARAGRAPH.LEFT)


# ---------------------------------------------------------------------------
# 9 注意事项
# ---------------------------------------------------------------------------
def section9():
    cur = find_heading("注意事项")
    cur = para(cur, "（1）本报告中的 admin/123456 仅用于课堂演示，口令以明文保存在 t_user 中；生产环境必须改为 BCrypt/Argon2 "
                    "哈希存储，并修改默认密码。")
    cur = para(cur, "（2）当前登录只做了 Session 会话校验，没有引入 Spring Security，写操作没有 CSRF token；"
                    "正式上线应加 Spring Security 或至少校验 Origin/Referer。")
    cur = para(cur, "（3）prod 环境的数据库账号应遵循最小权限原则，只授予业务所需的 SELECT/INSERT/UPDATE/DELETE；"
                    "建表脚本由 DBA 执行，应用启动不自动改表。")
    cur = para(cur, "（4）生产部署建议在应用前加 Nginx 反向代理并启用 HTTPS，设置 server.servlet.session.cookie.secure=true；"
                    "日志写入 logs/task-springboot.log 后要配置轮转，避免磁盘被占满。")
    cur = para(cur, "（5）运行数据来自本机 2026 年 10 月 28 日的实际构建与启动；换 JDK、MySQL 或操作系统版本后，"
                    "启动耗时和页面细节可能略有差异，但构建、登录、分页、校验和部署步骤不变。")


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

# 去掉模板标题末尾多余的分号（如“分析问题和确定解决方案；”）
for par in doc.paragraphs:
    if par.style.name == "Heading 1" and par.text.rstrip().endswith("；"):
        for run in reversed(par.runs):
            if run.text.rstrip().endswith("；"):
                run.text = run.text.rstrip()[:-1]
                break

# 删除模板中的提示语，只保留正文
PROMPTS = {
    "说明对每个关键层进行调整的原因。",
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
