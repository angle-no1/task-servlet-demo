# -*- coding: utf-8 -*-
"""按实验报告模板生成已填写的《Java高级编程实验报告》。"""
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

SRC = r"C:\Users\augenstern\Desktop\java2\04_完整学号_姓名_题目_设计报告(单元测试与 SpringBoot 快速迁移) (2).docx"
OUT_DIR = r"C:\Users\augenstern\Desktop\task-servlet-demo 5\task-servlet-demo\report"
OUT = os.path.join(OUT_DIR, "04_完整学号_姓名_题目_设计报告(单元测试与 SpringBoot 快速迁移)_已填写.docx")

doc = Document(SRC)

# ----------------------------------------------------------------------------- helpers
BODY_FONT = "Times New Roman"
EA_FONT = "宋体"
CODE_FONT = "Consolas"


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
    # 部分渲染器（LibreOffice）对中文取 szCs 字号，这里与 sz 保持一致
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
             shading=None, line=1.25, snap_off=False):
    par = doc.add_paragraph()
    par.style = doc.styles["Normal"]
    if text:
        run = par.add_run(text)
        set_run(run, size=size, bold=bold, ascii_font=ascii_font, east=east)
    pf = par.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after_sp)
    pf.line_spacing = line
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


def table(after, cap, rows, widths):
    cur = caption(after, cap)
    tbl = doc.add_table(rows=len(rows), cols=len(rows[0]))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    tbl_pr = tbl._tbl.tblPr

    # 固定表格总宽（1cm = 567 twips），配合 autofit=False 让列宽严格按设计值渲染
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
                tr_pr = tbl.rows[r_idx]._tr.get_or_add_trPr()
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


# ----------------------------------------------------------------------------- 封面日期
cover = doc.tables[0]
for row in cover.rows:
    if row.cells[0].text.strip() == "完成日期":
        cell = row.cells[1]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run("2026 年 10 月 27 日")
        set_run(run, size=10.5)

# ----------------------------------------------------------------------------- 3 分析问题和确定解决方案
cur = find_heading("分析问题和确定解决方案；")

cur = para(cur, "原项目 task-mybatis 采用 Servlet + Spring MVC + MyBatis 的传统装配方式，共有 4 个配置文件："
          "web.xml 负责 ContextLoaderListener、DispatcherServlet、CharacterEncodingFilter 和欢迎页；"
          "applicationContext.xml 负责数据源、SqlSessionFactory、MapperScannerConfigurer、事务管理器和 taskBuss 业务 Bean；"
          "springmvc.xml 负责控制器组件扫描与视图解析；db.properties 单独保存 4 项数据库连接参数。")
cur = para(cur, "对照实验要求逐项检查后，确认原项目存在 4 类需要解决的问题：")
cur = lead(cur, "（1）装配方式落后。",
           "容器、MVC、持久层、事务四套配置分散在 4 个文件、约 30 个 XML 标签中，"
           "新增一个 Bean 就要改 XML，配置写错只能在容器启动时才暴露，且无法脱离外部 Tomcat 运行。")
cur = lead(cur, "（2）环境无法切换。",
           "数据库地址、账号密码、日志级别全部硬编码，dev/test/prod 三种环境只能改源码再重新打包，"
           "迁移到 SpringBoot 后需要用 Profiles 一次性隔离。")
cur = lead(cur, "（3）业务层缺少防御性校验。",
           "原 TaskBuss 只判断了标题是否为 null/空串，超长标题（超过 varchar(100)）、非法状态、"
           "pageNum=0、pageSize 过大等参数会直接打到数据库；持久层异常原样抛给容器，页面出现 500 堆栈。")
cur = lead(cur, "（4）没有任何自动化测试。",
           "修改一处 SQL 只能手工点页面回归，既无法证明边界值被覆盖，也没有覆盖率可以度量。")

cur = para(cur, "因此确定“先去 XML、再分环境、后补测试”的路线：表现层用 Starter 自动配置替代 web.xml 与 springmvc.xml，"
                "持久层用 mybatis-spring-boot-starter 替代手写 SqlSessionFactory，业务层保留接口 + 实现的分层结构只把 XML 注入改为注解注入，"
                "配置层用 application.yml + Profiles 统一管理，最后用 JUnit 5 + Mockito 补齐单元测试，用 JaCoCo 反向驱动补测。"
                "各层的具体调整如下表所示。")
cur = table(cur, "表 1  迁移前后对照表", [
    ["层次", "迁移前（XML 装配）", "迁移后（SpringBoot）", "调整原因"],
    ["启动与容器", "web.xml：ContextLoaderListener、DispatcherServlet、CharacterEncodingFilter、welcome-file", "spring-boot-starter-web 自动配置；TaskApplication 单一启动类；server.servlet.encoding 统一 UTF-8", "去掉容器样板配置，内嵌 Tomcat，一条命令启动"],
    ["表现层", "springmvc.xml：component-scan、mvc:annotation-driven、InternalResourceViewResolver", "spring.mvc.view.prefix/suffix + @Controller 组件扫描", "视图参数降级为配置项，新增页面不用改 XML"],
    ["业务层", "applicationContext.xml 中 <bean id=\"taskBuss\">，setter 注入 TaskMapper", "@Service + @Autowired setter 注入", "组件扫描替代手工 Bean，仍保持接口解耦、便于 Mock"],
    ["持久层", "DriverManagerDataSource、SqlSessionFactoryBean、MapperScannerConfigurer、DataSourceTransactionManager", "mybatis-spring-boot-starter 自动装配；MyBatisConfig 上的 @MapperScan；mybatis.* 配置项", "Starter 统一版本与装配，去掉 4 个手工 Bean"],
    ["数据源", "db.properties 明文 4 项", "application-{dev,test,prod}.yml + HikariCP + ${DB_URL} 等环境变量占位符", "一份代码多环境，敏感信息不写死"],
    ["异常处理", "无，异常直接抛给容器变成 500 堆栈", "GlobalExceptionHandler（@ControllerAdvice）+ TaskServiceException", "统一错误页与状态码，隔离持久层细节"],
    ["测试", "无", "JUnit 5 + Mockito + Spring Boot Test + JaCoCo 门槛", "回归可重复、覆盖率可度量"],
], [2.9, 4.4, 4.2, 3.1])

cur = para(cur, "几个关键决策的说明：")
cur = lead(cur, "① 保留 JSP 而不是换模板引擎。",
           "本次实验的目标是“去 XML + 补测试”，视图层改动越少越能验证迁移前后的等价性，"
           "因此保留原 JSP 页面，用 war 打包 + tomcat-embed-jasper + JSTL 3.0 让内嵌 Tomcat 编译 JSP，"
           "页面路由与功能与原项目保持一致；随后又用一份统一的 app.css 重做了顶栏、卡片、表格与表单的视觉样式，"
           "并补充了响应式布局，保证手机宽度下也能正常操作。")
cur = lead(cur, "② 把 @MapperScan 放在独立的 MyBatisConfig 中。",
           "@WebMvcTest 只装配 MVC 层，如果 @MapperScan 写在启动类上，切片测试仍会去创建 Mapper 代理，"
           "而切片又没有 SqlSessionFactory，测试启动就会失败；独立配置类可被切片自动排除。")
cur = lead(cur, "③ test 环境使用 H2 内存库。",
           "单元测试和集成测试都不应该依赖物理 MySQL。H2 的 MODE=MySQL 兼容原 SQL 中的 LIMIT offset,count，"
           "因此可以在没有 MySQL 的机器上完整验证 MyBatis 映射、分页 SQL 与事务。")
cur = lead(cur, "④ 新增统一异常翻译。",
           "Mapper 抛出的 DataAccessException 属于持久层细节，不能直接展示给用户。"
           "TaskBuss 捕获后翻译为 TaskServiceException，再由 @ControllerAdvice 输出统一文案，并用 400/500 区分参数错误与服务故障。")
cur = lead(cur, "⑤ 把每页条数放进 yml。",
           "实验要求“业务参数也能随环境隔离”，所以新增 task.page.default-size，dev/test/prod 分别为 5/3/10，"
           "由 TaskPageProperties 绑定，用一条 --spring.profiles.active 参数即可同时切换数据源、日志和业务参数。")

# ----------------------------------------------------------------------------- 4 详细设计
cur = find_heading("详细设计")
cur = para(cur, "迁移后的工程按“启动类 + 配置类 + 业务接口/实现 + 控制层 + 持久层 + 测试”组织，目录结构如下（省略 entity 细节）：")
cur = code_block(cur, r"""
task-springboot
├── pom.xml                        Spring Boot 3.2.12 + web / mybatis / jacoco
├── src/main/java/cn/edu/mju/band
│   ├── TaskApplication.java       唯一启动类（@SpringBootApplication）
│   ├── buss/ITaskBuss.java        业务接口
│   ├── buss/impl/TaskBuss.java    @Service：参数校验 + 异常翻译 + 分页计算
│   ├── config/MyBatisConfig.java  @MapperScan，替代 MapperScannerConfigurer
│   ├── config/TaskPageProperties.java  task.page.* 业务参数绑定
│   ├── controller/HomeController.java / TaskController.java
│   ├── controller/GlobalExceptionHandler.java  @ControllerAdvice 统一错误页
│   ├── entity/{Task,Page,User}.java
│   ├── exception/TaskServiceException.java
│   └── mapper/TaskMapper.java     MyBatis 代理接口
├── src/main/resources
│   ├── application.yml            公共配置 + 默认激活 dev
│   ├── application-dev.yml        MySQL + DEBUG 日志 + 每页 5 条
│   ├── application-test.yml       H2 内存库 + 每页 3 条
│   ├── application-prod.yml       MySQL 环境变量 + 每页 10 条
│   ├── mapper/TaskMapper.xml      动态 SQL（保留）
│   ├── db/schema-h2.sql、data-h2.sql
│   └── static/css/app.css         统一页面样式（顶栏/卡片/表格/表单）
├── src/main/webapp/WEB-INF/template/{task,add_update,error}.jsp
└── src/test/java/cn/edu/mju/band   4 个测试类、78 个用例
    ├── buss/impl/TaskBussTest.java
    ├── controller/TaskControllerTest.java、HomeControllerTest.java
    └── TaskApplicationTests.java
""")

cur = sub_heading(cur, "4.1  启动流程与自动配置")
cur = para(cur, "启动类只做三件事：标注 @SpringBootApplication 开启自动配置与组件扫描；"
                "用 @ConfigurationPropertiesScan 注册业务参数类；在 main 方法中调用 SpringApplication.run()。"
                "原来 web.xml 中的 DispatcherServlet、编码过滤器、欢迎页由 WebMvcAutoConfiguration 提供；"
                "applicationContext.xml 中的数据源、SqlSessionFactory、事务管理器由 DataSourceAutoConfiguration、"
                "MybatisAutoConfiguration、TransactionAutoConfiguration 按 classpath 条件自动装配，Mapper 代理由 MyBatisConfig 上的 @MapperScan 扫描。"
                "整个项目不再需要任何 XML 装配文件。")

cur = sub_heading(cur, "4.2  多环境配置设计")
cur = para(cur, "主配置 application.yml 只保留与环境无关的公共项（应用名、视图前缀后缀、MyBatis 映射、端口与编码、日志格式），"
                "并通过 spring.profiles.active: dev 指定默认环境；三套子配置只覆盖差异项，差异如下表。")
cur = table(cur, "表 2  三套环境的配置差异", [
    ["配置项", "dev", "test", "prod"],
    ["数据源", "MySQL localhost:3306/taskmaster", "H2 内存库 taskdb（MODE=MySQL）", "MySQL，URL/账号/密码取 ${DB_URL} 等环境变量"],
    ["连接池", "HikariCP，最大 10、最小空闲 2", "H2 内嵌连接", "HikariCP，最大 30、最小空闲 10"],
    ["日志级别", "cn.edu.mju.band=DEBUG（打印 SQL 参数）", "root=WARN，业务层 INFO", "root=WARN，并输出到 logs/task-springboot.log"],
    ["task.page 默认每页条数", "5", "3", "10"],
    ["数据初始化", "沿用现有 t_task 表", "启动时执行 schema-h2.sql + data-h2.sql", "不初始化，由 DBA 管理"],
], [3.8, 3.4, 3.8, 3.5])
cur = para(cur, "切换环境只需一条命令行参数，例如 java -jar target/task-springboot.war --spring.profiles.active=test，"
                "启动日志会打印 “The following 1 profile is active: \"test\"”，随后数据源、日志级别和每页条数同时生效。"
                "配置优先级从高到低为：命令行参数 > 环境变量 > application-{profile}.yml > application.yml。")

cur = sub_heading(cur, "4.3  业务层的校验与异常设计")
cur = para(cur, "校验集中在 TaskBuss 内部，按“先校验、后访问数据库”的顺序执行，具体规则如下：")
cur = lead(cur, "① 任务对象：", "null 直接拒绝，避免后续空指针。")
cur = lead(cur, "② 标题：", "null、空串、纯空白（空格、制表符、换行）都视为空标题；按 t_task.title 的 varchar(100) 限制，"
                        "长度上限 100，trim 后超过 100 则拒绝，刚好 100 允许。")
cur = lead(cur, "③ 状态：", "只允许 0 待办、1 进行中、2 已完成；新增时未指定状态则按业务默认值 0 落库，更新时状态为 null 则拒绝，避免把状态刷成 NULL。")
cur = lead(cur, "④ 编号：", "findById、delete、update 的编号为 null 时拒绝。")
cur = lead(cur, "⑤ 分页：", "pageNum 必须 ≥ 1，pageSize 必须在 1～100 之间，防止 (pageNum-1)*pageSize 溢出或超大 LIMIT 拖垮数据库。")
cur = lead(cur, "⑥ 持久层异常：", "捕获 DataAccessException，翻译成 TaskServiceException（提示“数据库暂时不可用，请稍后重试”）并保留 cause。"
                              "由于校验在访问 SQL 之前，即使数据库宕机，非法参数仍能得到明确的参数错误提示，而不是连接异常。")

cur = sub_heading(cur, "4.4  测试分层设计")
cur = para(cur, "测试按“纯单元 → 控制层切片 → 容器集成”三层组织，越往下依赖越少、执行越快：")
cur = lead(cur, "第一层（TaskBussTest）：", "纯 Mockito 单元测试，用 @Mock 打桩 TaskMapper、@InjectMocks 注入被测对象，"
                                      "不启动 Spring 容器、不连数据库，覆盖正常流、异常流、边界值和数据库宕机五类场景。")
cur = lead(cur, "第二层（TaskControllerTest、HomeControllerTest）：", "@WebMvcTest 只装配 MVC 层，"
                                                                   "用 @MockBean 替换 ITaskBuss，验证参数绑定、默认值、视图名、重定向和异常状态码，不渲染 JSP。")
cur = lead(cur, "第三层（TaskApplicationTests）：", "@SpringBootTest + @ActiveProfiles(\"test\") 启动完整容器，"
                                                "连接 H2 内存库，验证 Profile 是否生效、MyBatis 动态 SQL、事务和分页的端到端行为，并用 @Transactional 自动回滚测试数据。")
cur = para(cur, "用例设计主要使用等价类划分、边界值分析和错误推测：标题取 null、空串、空白、100 字符、101 字符；"
                "状态取 -1、0、1、2、3、127；分页偏移取 1/2/3 页，总条数取 0、1、5、6、20、21 条，"
                "同时用 @ParameterizedTest + @CsvSource 把边界组合写成数据表，保证每个分支都有独立、可重复的断言。")

cur = sub_heading(cur, "4.5  覆盖率门槛设计")
cur = para(cur, "JaCoCo 在 prepare-agent 阶段挂载探针，test 阶段生成报告，verify 阶段执行门禁检查：核心类 TaskBuss 要求行覆盖率 ≥ 90%、分支覆盖率 ≥ 85%，"
                "整个工程（排除 entity 与启动类）要求行覆盖率 ≥ 80%。门禁不通过时 mvn verify 直接失败，避免“测试写了但没覆盖到”的情况。")

# ----------------------------------------------------------------------------- 5 实现
cur = find_heading("实现")
cur = para(cur, "实现环境：JDK 17.0.1、Maven 3.9.16、Spring Boot 3.2.12、MyBatis-Spring-Boot 3.0.3、"
           "MySQL 8.0.46（库 taskmaster，表 t_task）、H2 2.2.224、JaCoCo 0.8.11。"
           "构建与验证命令如下：")
cur = code_block(cur, r"""
mvn -B clean verify                     # 编译 + 测试 + 覆盖率门禁 + 打 war
java -jar target/task-springboot.war    # 默认 dev 环境（MySQL）
java -jar target/task-springboot.war --spring.profiles.active=test   # test（H2）
""")

cur = sub_heading(cur, "5.1  统一启动类")
cur = para(cur, "启动类是迁移的入口：@SpringBootApplication 负责自动配置和组件扫描，@ConfigurationPropertiesScan 注册业务参数，"
                "main 方法把控制权交给 SpringApplication。原来 web.xml 与两个 XML 容器文件全部删除。")
cur = code_block(cur, r"""
@SpringBootApplication
@ConfigurationPropertiesScan("cn.edu.mju.band.config")
public class TaskApplication {
    public static void main(String[] args) {
        SpringApplication.run(TaskApplication.class, args);
    }
}

@Configuration
@MapperScan("cn.edu.mju.band.mapper")   // 替代 MapperScannerConfigurer
public class MyBatisConfig {
}
""")

cur = sub_heading(cur, "5.2  多环境配置")
cur = para(cur, "application.yml 只写公共项，并用 spring.profiles.active 指定默认环境；test 子配置把数据源换成 H2，"
                "并声明建表与初始化脚本，使集成测试完全不依赖 MySQL。")
cur = code_block(cur, r"""
# application.yml
spring:
  profiles:
    active: dev                 # 命令行 --spring.profiles.active=test 可覆盖
  mvc:
    view: { prefix: /WEB-INF/template/, suffix: .jsp }
mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: cn.edu.mju.band.entity
  configuration:
    map-underscore-to-camel-case: true

# application-test.yml
spring:
  datasource:
    driver-class-name: org.h2.Driver
    url: jdbc:h2:mem:taskdb;MODE=MySQL;DB_CLOSE_DELAY=-1
    username: sa
  sql:
    init:
      mode: always
      schema-locations: classpath:db/schema-h2.sql
      data-locations: classpath:db/data-h2.sql
task:
  page: { default-size: 3 }
""")

cur = sub_heading(cur, "5.3  业务层关键实现")
cur = para(cur, "业务层在保留原 CRUD 语义的前提下补了三件事：参数边界校验、状态默认值处理、持久层异常翻译。"
                "下面是新增与分页两个核心方法（省略部分注释）：")
cur = code_block(cur, r"""
@Service
public class TaskBuss implements ITaskBuss {
    public static final int TITLE_MAX_LENGTH = 100;
    public static final int MAX_PAGE_SIZE = 100;

    @Autowired
    public void setTaskMapper(TaskMapper taskMapper) { this.taskMapper = taskMapper; }

    @Override
    @Transactional
    public boolean add(Task task) {
        checkTask(task);                              // 先校验，避免非法数据触达 SQL
        if (task.getStatus() == null) {
            task.setStatus(Task.STATUS_TODO);         // 业务默认值：待办
        }
        try {
            return taskMapper.insert(task) > 0;
        } catch (DataAccessException e) {
            throw wrap(e);                            // 翻译成 TaskServiceException
        }
    }

    @Override
    public Page<Task> findPage(String title, Byte status, int pageNum, int pageSize) {
        checkPageArgs(pageNum, pageSize);
        checkStatus(status);
        Page<Task> page = new Page<>();
        int start = (pageNum - 1) * pageSize;         // 偏移量公式
        List<Task> list = taskMapper.selectByPage(title, status, start, pageSize);
        long total = taskMapper.countByCondition(title, status);
        page.setData(list);
        page.setPageNum(pageNum);
        page.setPageSize(pageSize);
        page.setTotal(total);
        page.setPages((int) Math.ceil((double) total / pageSize));
        return page;
    }

    private void checkTask(Task task) {
        if (task == null) throw new IllegalArgumentException("任务对象不能为空");
        if (task.getTitle() == null || task.getTitle().trim().isEmpty())
            throw new IllegalArgumentException("任务名称不能为空");
        if (task.getTitle().trim().length() > TITLE_MAX_LENGTH)
            throw new IllegalArgumentException("任务名称长度不能超过 "
                    + TITLE_MAX_LENGTH + " 个字符");
        checkStatus(task.getStatus());
    }

    private void checkStatus(Byte status) {
        if (status != null && (status < Task.STATUS_TODO || status > Task.STATUS_DONE))
            throw new IllegalArgumentException("任务状态非法，只能是 0/1/2");
    }
}
""")

cur = sub_heading(cur, "5.4  全局异常处理")
cur = para(cur, "@ControllerAdvice 把两类异常映射到同一个错误页，但区分 HTTP 状态码：参数错误返回 400，持久层故障返回 500。"
                "这样前端既能拿到可读提示，也不会把 500 堆栈暴露给用户。")
cur = code_block(cur, r"""
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public String handleIllegalArgument(IllegalArgumentException e, Model model) {
        log.warn("请求参数不合法：{}", e.getMessage());
        model.addAttribute("error", e.getMessage());
        return "error";
    }

    @ExceptionHandler(TaskServiceException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public String handleServiceException(TaskServiceException e, Model model) {
        log.error("业务处理失败：{}", e.getMessage(), e);
        model.addAttribute("error", e.getMessage());
        return "error";
    }
}
""")

cur = sub_heading(cur, "5.5  单元测试的关键写法")
cur = para(cur, "Mockito 扩展负责创建和注入 Mock；when().thenReturn() 打桩正常返回，thenThrow() 模拟数据库宕机，"
                "verify()/verifyNoInteractions() 验证调用次数，ArgumentCaptor 捕获实际入参，"
                "参数化测试把边界值写成表格，一行数据就是一个独立用例。")
cur = code_block(cur, r"""
@ExtendWith(MockitoExtension.class)
class TaskBussTest {
    @Mock  private TaskMapper taskMapper;
    @InjectMocks private TaskBuss taskBuss;

    @Test
    @DisplayName("add：插入 0 行返回 false")
    void add_shouldReturnFalseWhenInsertAffectsZeroRows() {
        when(taskMapper.insert(any(Task.class))).thenReturn(0);
        assertThat(taskBuss.add(validTask())).isFalse();
    }

    @ParameterizedTest
    @CsvSource({"1, 5, 0", "2, 5, 5", "3, 5, 10", "4, 20, 60"})
    void findPage_shouldComputeOffset(int pageNum, int pageSize, int expectedStart) {
        when(taskMapper.selectByPage(null, null, expectedStart, pageSize))
                .thenReturn(List.of());
        when(taskMapper.countByCondition(null, null)).thenReturn(0L);
        taskBuss.findPage(null, null, pageNum, pageSize);
        verify(taskMapper).selectByPage(null, null, expectedStart, pageSize);
    }

    @Test
    @DisplayName("数据库宕机：add 抛出统一业务异常并保留原因")
    void add_shouldWrapDataAccessException() {
        when(taskMapper.insert(validTask()))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));
        assertThatThrownBy(() -> taskBuss.add(validTask()))
                .isInstanceOf(TaskServiceException.class)
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }
}
""")

cur = sub_heading(cur, "5.6  JaCoCo 插件与门禁")
cur = para(cur, "在 pom.xml 中绑定 prepare-agent、report、check 三个执行点，excludes 排除 entity 与启动类，"
                "规则对 TaskBuss 和整个工程分别设置下限。")
cur = code_block(cur, r"""
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.11</version>
  <executions>
    <execution>
      <id>prepare-agent</id>
      <goals><goal>prepare-agent</goal></goals>
    </execution>
    <execution>
      <id>report</id><phase>test</phase>
      <goals><goal>report</goal></goals>
    </execution>
    <execution>
      <id>check</id><phase>verify</phase><goals><goal>check</goal></goals>
      <configuration><rules>
        <rule>
          <element>CLASS</element>
          <includes><include>cn.edu.mju.band.buss.impl.TaskBuss</include></includes>
          <limits>
            <limit>
              <counter>LINE</counter><value>COVEREDRATIO</value><minimum>0.90</minimum>
            </limit>
            <limit>
              <counter>BRANCH</counter><value>COVEREDRATIO</value><minimum>0.85</minimum>
            </limit>
          </limits>
        </rule>
        <rule>
          <element>BUNDLE</element>
          <limits>
            <limit>
              <counter>LINE</counter><value>COVEREDRATIO</value><minimum>0.80</minimum>
            </limit>
          </limits>
        </rule>
      </rules></configuration>
    </execution>
  </executions>
</plugin>
""")

cur = sub_heading(cur, "5.7  运行结果")
cur = para(cur, "执行 mvn -B clean verify，编译、78 个测试、覆盖率门禁、war 打包全部成功，关键输出如下："
           )
cur = code_block(cur, r"""
[INFO] Tests run: 60, Failures: 0, Errors: 0, Skipped: 0 -- in TaskBussTest
[INFO] Tests run: 11, Failures: 0, Errors: 0, Skipped: 0 -- in TaskControllerTest
[INFO] Tests run:  1, Failures: 0, Errors: 0, Skipped: 0 -- in HomeControllerTest
[INFO] Tests run:  6, Failures: 0, Errors: 0, Skipped: 0 -- in TaskApplicationTests
[INFO] Tests run: 78, Failures: 0, Errors: 0, Skipped: 0
[INFO] Building war: target/task-springboot.war
[INFO] All coverage checks have been met.
[INFO] BUILD SUCCESS
""")
cur = para(cur, "两个环境分别启动后，用浏览器/HTTP 请求逐项验证，结果如下表。dev 环境读取真实 MySQL，test 环境读取 H2，"
                "两次启动的日志分别显示激活了 dev 与 test，证明命令行参数切换生效。")
cur = table(cur, "表 3  运行时验证结果", [
    ["验证场景", "请求 / 操作", "结果"],
    ["默认 dev 启动", "java -jar target/task-springboot.war --server.port=18080", "日志：The following 1 profile is active: \"dev\"；Tomcat 启动耗时 3.28 s"],
    ["首页跳转", "GET /", "302，Location=/task"],
    ["dev 任务列表", "GET /task", "200，每页 5 条、共 8 条、2 页，读取 MySQL taskmaster"],
    ["dev 状态筛选", "GET /task?status=2", "200，仅显示“已完成”记录"],
    ["切到 test 环境", "java -jar ... --spring.profiles.active=test --server.port=18081", "日志：active: \"test\"；数据源为 H2，每页 3 条、共 7 条、3 页"],
    ["test 新增任务", "POST /task?opt=add（title=运行时验证任务）", "302 回列表，随后按标题查询命中 1 条"],
    ["非法状态参数", "GET /task?status=abc", "400，错误页提示“任务状态参数非法：abc”"],
    ["页码越界", "GET /task?pageNum=0", "400，错误页提示“页码必须大于等于 1”"],
    ["数据库不可用", "Mockito 模拟 DataAccessResourceFailureException", "抛出 TaskServiceException，页面提示稍后重试（单元测试覆盖）"],
], [3.2, 6.8, 4.6])

# ----------------------------------------------------------------------------- 6 测试
cur = find_heading("测试")
cur = para(cur, "（1）测试结果。全部 78 个用例一次通过，无失败、无跳过；四个测试类分别覆盖业务层、控制层、首页与容器集成，"
           "具体分布如下表。")
cur = table(cur, "表 4  测试用例分布与结果（括号内为用例数）", [
    ["测试类（用例数）", "主要覆盖内容", "结果"],
    ["TaskBussTest（60）", "CRUD 正常流；null/空串/空白标题；标题 100/101 边界；状态 -1/0/1/2/3/127；"
                          "null 编号；页码 0/-1/-100；每页 0/-1/100/101；偏移量与总页数（0/1/5/6/20/21 条）；"
                          "Mapper 抛 DataAccessException 时统一异常；校验先于 SQL", "通过"],
    ["TaskControllerTest（11）", "默认分页参数、查询条件透传与空白归一化、状态解析失败返回 400、"
                                "服务异常返回 500、新增/修改/删除表单与重定向、视图名与模型属性", "通过"],
    ["HomeControllerTest（1）", "GET / 302 重定向到 /task", "通过"],
    ["TaskApplicationTests（6）", "test Profile 激活、业务参数=3、数据源为 H2、CRUD 全链路、"
                                 "分页与筛选（7 条数据 3 条/页）、空标题在 SQL 之前被拦截", "通过"],
], [4.3, 8.1, 2.2])

cur = para(cur, "JaCoCo 生成的 target/site/jacoco/index.html 与 jacoco.csv 显示，被统计的 7 个类行覆盖率、分支覆盖率均为 100%，"
                "指令覆盖 479/479、方法覆盖 32/32：")
cur = table(cur, "表 5  JaCoCo 覆盖率统计（排除 entity 与启动类）", [
    ["被测类", "行覆盖", "分支覆盖", "说明"],
    ["TaskBuss", "66/66（100%）", "36/36（100%）", "核心业务类，门槛 90%/85%"],
    ["TaskController", "41/41（100%）", "10/10（100%）", "列表、增删改、参数解析"],
    ["GlobalExceptionHandler", "8/8（100%）", "—", "400/500 两条异常分支"],
    ["HomeController", "2/2（100%）", "—", "首页重定向（补测前漏覆盖）"],
    ["TaskPageProperties", "5/5（100%）", "—", "业务参数绑定"],
    ["MyBatisConfig / TaskServiceException", "1/1、4/4（100%）", "—", "配置类与异常类"],
    ["合计", "127/127（100%）", "46/46（100%）", "指令 479/479，方法 32/32"],
], [5.2, 2.9, 2.8, 3.5])
cur = para(cur, "（2）调试过程中遇到的问题及解决办法。下表按“现象—原因—解决”记录本次迁移中实际遇到的 6 个问题。")
cur = table(cur, "表 6  调试问题与解决", [
    ["问题", "现象", "原因", "解决办法"],
    ["MyBatis 映射文件解析失败", "启动报 SAXParseException：lineNumber 63，元素类型为 mapper 的内容必须匹配 "
                                  "(cache-ref|cache|resultMap*|...)", "TaskMapper.xml 中残留一行 //- 开头的说明文字，"
                                                                        "不是合法的 XML 子元素", "改为 <!-- --> 注释后启动正常"],
    ["控制层切片测试无法启动", "@WebMvcTest 报 Property 'sqlSessionFactory' or 'sqlSessionTemplate' are required；"
                                "另报 No qualifying bean TaskPageProperties", "@MapperScan 写在启动类上，切片仍会创建 Mapper；"
                                                                              "切片不装配 MyBatis 自动配置；@ConfigurationPropertiesScan 在切片中不生效",
     "@MapperScan 移到独立 MyBatisConfig（切片不加载）；测试类 @Import(TaskPageProperties.class)"],
    ["参数错误返回 500", "/task?status=abc 返回 500，虽然是自定义错误页", "error.jsp 声明了 isErrorPage=\"true\"，"
                                                                          "异常处理器也未声明状态码，容器按错误页处理",
     "移除 isErrorPage；在 @ExceptionHandler 上加 @ResponseStatus(400/500)；测试断言改为 isBadRequest/is5xxServerError"],
    ["JSP 页面 404", "打成 jar 后访问 /task 返回 404", "可执行 jar 不支持 JSP 编译", "改为 war 打包，"
                                                                                   "引入 provided 的 starter-tomcat 与 tomcat-embed-jasper，"
                                                                                   "JSP 保留在原位置，java -jar war 正常运行"],
    ["H2 分页语法兼容性", "担心 MySQL 的 LIMIT ?,? 在 H2 上不可用", "原 SQL 使用 LIMIT offset,count 写法", "选用 H2 的 MODE=MySQL，"
                                                                                                        "先用最小程序验证 LIMIT ?,? 可用，保留原 SQL 不变"],
    ["Mockito 无法初始化", "受限终端下报 Could not self-attach to current VM using external process", "Mockito 内联 MockMaker "
                                                                                                   "启动时需要临时 JVM 自附加 agent，受限环境禁止子进程/命名管道",
     "在允许进程附加的正常终端执行 mvn verify（已通过）；若仍受限，可配置 mock-maker-subclass"],
], [2.9, 4.2, 4.2, 3.3])
cur = para(cur, "另外一个“问题”是 JaCoCo 报告直接暴露的：首次生成报告时 HomeController 的分支覆盖为 0/1、行覆盖 1/2，"
                "原因是控制层切片只测了 TaskController。补写 HomeControllerTest 断言 302 重定向后，覆盖率补齐到 100%。"
                "这也说明覆盖率报告的价值：它把“没想到要测的代码”直接摆在了报告里。")

# ----------------------------------------------------------------------------- 7 结果分析
cur = find_heading("结果分析；")
cur = para(cur, "（1）调整后的优势。")
cur = lead(cur, "① 配置量大幅下降。", "迁移前有 web.xml、applicationContext.xml、springmvc.xml、db.properties 四个配置源和约 30 个 XML 标签；"
                                  "迁移后没有任何 XML 装配文件，只剩 4 个 yml 声明式配置，新增 Bean 只需加注解。")
cur = lead(cur, "② 启动与部署更简单。", "不再需要外部 Tomcat 和手工打 war 部署，mvn clean verify 生成可执行 war，"
                                    "java -jar 一条命令启动，内嵌 Tomcat 启动耗时约 3.3 秒。")
cur = lead(cur, "③ 环境真正隔离。", "同一份代码通过 --spring.profiles.active 即可在 dev（MySQL/DEBUG/每页 5 条）、"
                                "test（H2/每页 3 条）、prod（环境变量/日志落盘/每页 10 条）之间切换，敏感配置不再出现在源码里。")
cur = lead(cur, "④ 业务逻辑可回归。", "迁移前 0 个自动化用例，迁移后 78 个，mvn verify 一次约 20 秒完成编译、测试和覆盖率门禁，"
                                "修改校验规则或分页公式时会立刻发现回归。")
cur = lead(cur, "⑤ 健壮性提升。", "非法参数返回 400 并给出具体原因，数据库故障返回 500 统一文案，持久层异常不再泄漏到页面；"
                             "数据库宕机时参数校验仍优先执行，错误提示不会被连接异常掩盖。")
cur = lead(cur, "⑥ 覆盖率可度量。", "核心业务类行覆盖 66/66、分支覆盖 36/36，工程整体行覆盖 127/127（100%），"
                              "命中 JaCoCo 设置的 90%/85% 与 80% 门槛。")
cur = para(cur, "（2）经验和体会。")
cur = lead(cur, "第一，迁移应先求等价、再求优化。", "本次保留了 JSP 和原有 SQL 写法，只把装配方式换成自动配置，"
                                     "每改一层就用页面或测试确认行为未变，避免了“大爆炸式重写”带来的定位困难。")
cur = lead(cur, "第二，单元测试要靠边界驱动。", "先列出参数的所有合法/非法区间（null、空串、空白、100/101、0/1/2、"
                                  "页码 0/1/2、总条数 5/6/20/21），再用参数化测试逐个落成数据行，"
                                  "写完以后分支覆盖率自然接近 100%，而不是先写完代码再“凑”覆盖率。")
cur = lead(cur, "第三，Mockito 的边界要选对。", "Mapper 是接口，天然适合 mock；Service 是被测对象，不能 mock。"
                                 "借助 verifyNoInteractions 可以断言“校验失败时根本没有访问数据库”，"
                                 "这正是数据库宕机场景下最想证明的行为。")
cur = lead(cur, "第四，覆盖率不是目的，而是发现盲区的工具。", "报告里唯一未覆盖的分支是首页重定向，"
                                          "补一个断言就能补齐；如果只盯着百分比刷数字，反而会写出大量没有断言的无效用例。")
cur = lead(cur, "第五，配置外置要重视优先级与安全。", "命令行 > 环境变量 > profile 配置 > 主配置的顺序要心里有数；"
                                    "生产环境用 ${DB_URL} 这类占位符，既方便运维注入，也避免密码进入代码仓库。")

# ----------------------------------------------------------------------------- 8 参考文献
cur = find_heading("参考文献")
refs = [
    "[1] Spring Boot Reference Documentation 3.2.x（Profiles、Auto-configuration、Testing）[EB/OL]. "
    "https://docs.spring.io/spring-boot/docs/3.2.x/reference/html/",
    "[2] Spring Framework Reference Documentation: Testing（MockMvc、@WebMvcTest、@SpringBootTest）[EB/OL]. "
    "https://docs.spring.io/spring-framework/reference/testing.html",
    "[3] JUnit 5 User Guide（@ParameterizedTest、@CsvSource、@BeforeEach）[EB/OL]. "
    "https://junit.org/junit5/docs/current/user-guide/",
    "[4] Mockito Framework Documentation（@Mock、@InjectMocks、verify、ArgumentCaptor）[EB/OL]. "
    "https://site.mockito.org/",
    "[5] JaCoCo Documentation（prepare-agent、report、check 与覆盖率规则）[EB/OL]. "
    "https://www.jacoco.org/jacoco/trunk/doc/",
    "[6] MyBatis-Spring-Boot-Starter Reference（自动配置、@MapperScan、mapper-locations）[EB/OL]. "
    "https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/",
    "[7] H2 Database Engine: Compatibility Modes（MODE=MySQL）[EB/OL]. "
    "https://www.h2database.com/html/features.html#compatibility",
]
for item in refs:
    cur = new_para(cur, item, first_pt=0, size=9.5, after_sp=3, align=WD_ALIGN_PARAGRAPH.LEFT)

# 去掉模板标题末尾多余的分号（如“分析问题和确定解决方案；”）
for par in doc.paragraphs:
    if par.style.name == "Heading 1" and par.text.rstrip().endswith("；"):
        for run in reversed(par.runs):
            if run.text.rstrip().endswith("；"):
                run.text = run.text.rstrip()[:-1]
                break

# 删除模板中“请在此处填写……”性质的提示语，只保留正文
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
