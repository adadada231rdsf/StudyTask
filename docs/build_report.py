# -*- coding: utf-8 -*-
"""生成《实验一 实验报告》docx。运行：python docs/build_report.py"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "实验一_实验报告_宋逸轩.docx")

doc = Document()

# ---------- 页面与默认字体 ----------
from docx.enum.section import WD_SECTION
sec = doc.sections[0]
sec.page_width = Cm(21)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(1.6)
sec.bottom_margin = Cm(1.6)
sec.left_margin = Cm(2.3)
sec.right_margin = Cm(2.3)

style = doc.styles["Normal"]
style.font.name = "宋体"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
style.paragraph_format.line_spacing = 1.18
style.paragraph_format.space_after = Pt(3)


def set_cn(run, font="宋体", size=10.5, bold=False, color=None):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    if color:
        run.font.color.rgb = color


def title(text, size=18):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    set_cn(p.add_run(text), "黑体", size, True)


def h1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    set_cn(p.add_run(text), "黑体", 13, True)


def h2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    set_cn(p.add_run(text), "黑体", 11, True)


def body(text, indent=True, size=10.5):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    set_cn(p.add_run(text), "宋体", size)
    return p


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.left_indent = Cm(0.9)
    set_cn(p.add_run(text), "宋体", 10.5)
    return p


def code(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    set_cn(p.add_run(text), "Consolas", 9)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F2F2F2")
    p._p.get_or_add_pPr().append(shd)
    return p


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def table(headers, rows, widths=None, size=9):
    """widths 为各列相对比例；按版心宽度归一化后写死 tblGrid（python-docx 的
    cell.width 不会写 tblGrid，LibreOffice/Word 会按内容重新分配列宽）。"""
    if widths:
        total = sum(widths)
        widths = [w * 16.0 / total for w in widths]
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cn(p.add_run(h), "黑体", size, True)
        shade(hdr[i], "DDE6F0")
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(0)
            set_cn(p.add_run(str(v)), "宋体", size)
    if widths:
        # tblGrid 决定实际列宽，必须显式写死
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    tl = OxmlElement("w:tblLayout")
    tl.set(qn("w:type"), "fixed")
    t._tbl.tblPr.append(tl)
    tw = t._tbl.tblPr.find(qn("w:tblW"))
    if tw is None:
        tw = OxmlElement("w:tblW")
        t._tbl.tblPr.append(tw)
    tw.set(qn("w:type"), "dxa")
    tw.set(qn("w:w"), str(int(sum(widths or [16.0]) * 567)))
    trPr = t.rows[0]._tr.get_or_add_trPr()
    hdr_el = OxmlElement("w:tblHeader")
    trPr.append(hdr_el)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    set_cn(p.add_run(text), "宋体", 9)


def picture(name, width=12.4):
    path = os.path.join(BASE, name)
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Cm(width))


# ==================== 封面信息 ====================
title("软件工程实验一 实验报告", 20)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_cn(p.add_run("个人学习任务管理系统 StudyTask"), "黑体", 14, True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(10)
set_cn(p.add_run("学号 242806010116    姓名 宋逸轩    班级 24 级计科"), "宋体", 11)

table(
    ["项目", "内容"],
    [
        ["实验名称", "实验一：个人学习任务管理系统"],
        ["技术栈", "Python 3.13 / Flask 2.3.3 / SQLite(sqlite3) / Jinja2 / 原生 HTML+CSS"],
        ["覆盖需求", "SRS 附录 A 的 FR-01～FR-10、验收用例 T1～T10"],
        ["测试结果", "pytest 39 条用例全部通过（39 passed in 1.30s）"],
        ["代码仓库", "https://github.com/adadada231rdsf/StudyTask"],
        ["开发方式", "AI 辅助开发（详见第三章）"],
    ],
    widths=[3.0, 13.2],
    size=10,
)

# ==================== 一、需求理解 ====================
h1("一、需求理解")
body(
    "本实验要求实现一个单用户、本地运行的 Web 应用，用于管理个人的学习任务。"
    "系统不需要登录与权限，不需要云部署，数据保存在本地 SQLite 文件中。"
    "用户可以在浏览器中录入学习任务，按课程、状态、优先级筛选查看，"
    "并根据截止日期获得逾期与即将到期的提醒。"
)
body("按 SRS 附录 A 整理出十项功能需求，实现情况如下：")
table(
    ["需求编号", "需求名称", "关键约束 / 实现要点"],
    [
        ["FR-01", "新建任务", "表单录入，服务端校验通过后入库，成功跳转详情页"],
        ["FR-02", "任务列表与详情", "列表展示主要字段；详情展示全部字段，不存在返回 404"],
        ["FR-03", "编辑任务", "复用同一表单，校验失败保留用户已填内容"],
        ["FR-04", "删除任务", "GET 只展示确认页不删数据，POST 才真正删除"],
        ["FR-05", "状态流转", "待完成 / 进行中 / 已完成，列表页可直接切换"],
        ["FR-06", "组合筛选", "课程 + 状态 + 优先级 + 关键字，可任意组合"],
        ["FR-07", "到期提醒", "逾期红标、3 天内即将到期橙标、已完成不提醒"],
        ["FR-08", "统计信息", "任务总数、已完成数、完成率；总数为 0 时显示 0%"],
        ["FR-09", "排序规则", "已完成沉底 → 截止日期升序 → 优先级高在前"],
        ["FR-10", "数据校验", "长度、必填、日期真实性、枚举值，服务端校验 + 数据库 CHECK 兜底"],
    ],
    widths=[1.8, 3.0, 10.4],
)
h2("数据项约束（SRS 附录 A.2）")
table(
    ["字段", "类型", "约束"],
    [
        ["任务名称 name", "文本", "必填，1—100 字"],
        ["所属课程 course", "文本", "必填，1—60 字"],
        ["任务描述 description", "文本", "可空，≤ 1000 字"],
        ["截止日期 due_date", "日期", "必填，格式 YYYY-MM-DD，且必须是真实存在的日期"],
        ["优先级 priority", "枚举", "高 / 中 / 低，默认「中」"],
        ["状态 status", "枚举", "待完成 / 进行中 / 已完成，默认「待完成」"],
    ],
    widths=[3.6, 1.8, 9.8],
)

# ==================== 二、设计 ====================
h1("二、系统设计")
h2("2.1 总体结构")
body(
    "系统采用经典的三层结构，按职责把代码拆成四个模块，路由层不写 SQL、不写校验规则："
)
table(
    ["层次", "模块文件", "职责"],
    [
        ["路由层", "project/views.py", "接收请求、调用校验与数据访问、渲染模板、重定向"],
        ["校验层", "project/validation.py", "字段校验、日期解析、逾期与统计等派生逻辑"],
        ["数据访问层", "project/repository.py", "集中全部 SQL，支持组合筛选与排序"],
        ["数据库层", "project/db.py", "连接管理、建表 SQL、业务常量（状态 / 优先级）"],
    ],
    widths=[2.6, 4.4, 8.2],
)
body(
    "另用 project/__init__.py 中的 create_app() 应用工厂组装应用。"
    "采用工厂模式而不是全局 app 对象，是为了让测试可以注入临时数据库配置，"
    "每条测试都在独立的临时文件上运行，互不干扰。"
)
h2("2.2 数据库设计")
body("系统只有一张业务表 task，字段与 SRS 数据项一一对应：")
code(
    "CREATE TABLE task (\n"
    "    id          INTEGER PRIMARY KEY AUTOINCREMENT,\n"
    "    name        TEXT NOT NULL,\n"
    "    course      TEXT NOT NULL,\n"
    "    description TEXT NOT NULL DEFAULT '',\n"
    "    due_date    TEXT NOT NULL,        -- YYYY-MM-DD，字典序即日期序\n"
    "    priority    TEXT NOT NULL DEFAULT '中',\n"
    "    status      TEXT NOT NULL DEFAULT '待完成',\n"
    "    created_at  TEXT NOT NULL,\n"
    "    updated_at  TEXT NOT NULL,\n"
    "    CHECK (priority IN ('高','中','低')),\n"
    "    CHECK (status   IN ('待完成','进行中','已完成'))\n"
    ");"
)
body(
    "设计上有三点考虑：一是截止日期存为 TEXT 且固定 YYYY-MM-DD 格式，"
    "这样字符串的字典序与日期先后顺序一致，排序和区间比较可以直接用 SQL 完成，无需额外函数；"
    "二是对优先级和状态加了 CHECK 约束，即使上层代码有疏漏，非法数据也写不进库，"
    "这是「校验层 + 数据库层」双重保护的第二道防线；"
    "三是为 course、status、priority、due_date 建了索引，组合筛选时不至于全表扫描。"
)
h2("2.3 关键实现思路")
bullet("逾期判断（FR-07）：只对未完成任务计算。due_date < 今天 → 逾期；今天 ≤ due_date ≤ 今天+3 天 → 即将到期；已完成任务一律不显示提醒。")
bullet("完成率（FR-08）：总是基于全量任务计算（all_tasks()），而不是基于筛选后的结果，避免用户一筛选就看到百分比变化。总数 0 时直接返回 0%，不做除零。")
bullet("排序（FR-09）：在 SQL 的 ORDER BY 中用 CASE WHEN 把已完成状态排到最后，再按截止日期升序、优先级 CASE 映射后升序。")
bullet("安全：所有 SQL 使用参数化占位符；模板使用 Jinja2 默认的自动转义。测试中专门验证了 <script>alert(1)</script> 被转义、以及 ' OR 1=1;-- 不会返回全部数据。")
bullet("表单失败回填：校验失败时返回 400 状态码并把 form 内容回传给模板，用户不必重填。")

# ==================== 三、AI 使用情况 ====================
h1("三、AI 使用情况")
body(
    "本实验全程使用 AI 编程助手辅助开发。为了便于追溯，把工作拆成 12 项任务分别记录各自由谁完成，"
    "完整记录见仓库中的 AI_DEV_LOG.md。"
)
table(
    ["编号", "任务", "完成方"],
    [
        ["A1", "读指导书，梳理 FR-01~FR-10 与数据约束", "AI + 学生确认"],
        ["A2", "设计分层结构（views / repository / validation / db）", "AI"],
        ["A3", "建表 SQL 与数据访问层", "AI"],
        ["A4", "校验层：长度、必填、日期格式、枚举", "AI"],
        ["A5", "派生逻辑：逾期、即将到期、统计", "AI"],
        ["A6", "路由与页面模板", "AI"],
        ["A7", "手写样式，适配本地使用", "AI"],
        ["A8", "编写 pytest 用例覆盖 T1~T10", "AI"],
        ["A9", "运行测试、修复缺陷", "AI + 学生验证"],
        ["A10", "起草 README、验收表、开发日志", "AI"],
        ["A11", "Git 提交与仓库管理", "学生"],
        ["A12", "验收逐条核对、报告与演示材料", "学生"],
    ],
    widths=[1.4, 10.0, 3.8],
)
h2("3.1 AI 承担的部分")
body(
    "AI 主要承担了需求条目到代码的落地工作：分层结构设计、建表语句、校验规则、"
    "逾期与统计的派生逻辑、路由与模板、以及 39 条 pytest 用例的编写。"
    "在文档方面起草了 README、验收记录表和开发日志的框架。"
)
h2("3.2 学生承担的部分")
body(
    "学生负责需要判断和需要本机环境的部分：确认需求理解的正确性、"
    "在真实环境（Python 3.13 + Flask 2.3.3）中运行与验证、"
    "按 T1~T10 逐条手工验收、执行 Git 提交与仓库管理，"
    "以及对 AI 每一处输出作出采纳 / 修改 / 拒绝的判断。"
)
h2("3.3 对 AI 输出的判断")
body(
    "AI 的输出并非全部照单全收，其中最典型的一次判断发生在问题 1 中："
    "AI 最初把「下拉框空白」归因为 CSS 被 flex 布局压扁，"
    "改为加宽样式后框确实变宽了、但选项依然为空，这才反证出是模板变量没有传值。"
    "如果不看实际渲染结果、只听 AI 的第一判断，就会把样式改得越来越复杂，而真正的缺陷仍然存在。"
    "这个「先错后对」的过程完整保留在 AI_DEV_LOG.md 的问题 1 记录里。"
)

# ==================== 四、问题与修复 ====================
h1("四、开发中遇到的问题及修复过程")
body(
    "以下四个问题均在开发过程中真实出现，修复过程与判断依据记录在 AI_DEV_LOG.md。"
)

h2("问题 1：详情页状态下拉框渲染为空")
body(
    "现象：详情页的下拉框里没有任何选项，页面也不报错。"
    "排查过程：先怀疑 CSS——.inline 使用了 flex 布局，select 会被压缩，"
    "于是加了 flex: 0 0 auto; min-width: 92px，重新截图发现框变宽了但里面依然空白，排除样式问题。"
    "接着在浏览器控制台读取 document.querySelector('select').options.length，结果为 0，"
    "确认选项根本没有被渲染出来。回到模板，templates/detail.html 写的是 {% for s in statuses %}，"
    "而 views.py 的 detail() 在 render_template 时没有传入 statuses。"
    "其他页面都显式传了，只有详情页漏了。之所以没报错，是因为 Jinja2 对未定义变量默认渲染为空，"
    "for 循环直接跳过，属于典型的静默失败。"
)
code(
    "# 修复前\n"
    "return render_template(\"detail.html\", task=decorate(row))\n"
    "# 修复后\n"
    "return render_template(\"detail.html\", task=decorate(row),\n"
    "                       statuses=database.STATUSES)"
)
body(
    "为防止复发，补了一条回归用例 test_t5_detail_status_options_rendered，"
    "断言详情页三个状态都存在且当前状态被选中。以后谁再漏传变量，测试会立即失败而不是悄悄放行。"
)

h2("问题 2：列表页新增任务后统计数字不刷新")
body(
    "现象：在另一个标签页新建任务后回到首页，任务总数还是旧数字。"
    "分析：统计值是在服务端每次请求时现算的，本身没有缓存；问题在于浏览器对后退 / 缓存页面没有重新请求服务端。"
    "本项目没有做前后端分离，也没有 AJAX 局部刷新，页面上的数字只能是「本次请求时刻」的快照。"
)
body(
    "修复：在不引入前端框架的前提下采用 POST-Redirect-GET，保证每次回到首页都是一次新的 GET 请求——"
    "新建后 302 到详情页，删除后 302 回首页，改状态后 302 回来源页。"
    "测试中用 follow_redirects=False 断言状态码为 302 来固定这一行为。"
)

h2("问题 3：测试运行时出现 PytestCacheWarning（WinError 5 拒绝访问）")
body(
    "现象：执行 python -m pytest 时最后总会多出一段警告，提示无法创建 .pytest_cache\\v\\cache\\nodeids，"
    "错误为 [WinError 5] 拒绝访问。分析：项目位于桌面目录，受系统或安全软件保护，"
    "pytest 尝试写入缓存子目录时被拒绝。该问题不影响测试结果，39 条用例全部通过，只是产生噪音。"
)
code(
    "[tool.pytest.ini_options]\n"
    "addopts = \"-v --tb=short -p no:cacheprovider\""
)
body(
    "修复：在 pyproject.toml 中关闭缓存插件，警告消失。代价是 pytest 不再记录上次失败用例信息（--lf），"
    "对本项目规模而言可以接受。"
)

h2("问题 4：2026-02-30 这类「格式对但日期不存在」的输入")
body(
    "现象：若只用正则 ^\\d{4}-\\d{2}-\\d{2}$ 校验，2026-02-30 会被放行，"
    "存进数据库后会和 3 月的任务混在一起排序，逾期判断也随之出错。"
    "根本原因是「格式合法」与「日期真实存在」是两回事。"
)
body(
    "修复：改用 datetime.strptime(value, \"%Y-%m-%d\") 解析，解析失败一律视为非法，"
    "错误文案统一为「截止日期格式应为 YYYY-MM-DD，且必须是真实存在的日期」。"
    "用例 test_t4_invalid_date_format 覆盖了 2026-13-01、2026-02-30、abc、20261201 等输入。"
)

# ==================== 五、测试与验收 ====================
h1("五、测试与验收")
h2("5.1 自动化测试")
body(
    "使用 pytest 编写了 39 条用例，覆盖 T1~T10 的全部验收点，另含默认值、XSS 转义、SQL 注入尝试、"
    "错误页等补充检查。测试通过应用工厂注入临时数据库，不会影响真实数据。"
)
table(
    ["测试文件", "覆盖内容", "用例数"],
    [
        ["tests/test_create_validation.py", "T1~T5、默认值、XSS 转义、详情页状态选项回归", "13"],
        ["tests/test_edit_delete_status.py", "T6~T9：编辑、删除确认、状态流转、到期提醒", "13"],
        ["tests/test_filter_stats.py", "T10：组合筛选、FR-08 统计、FR-09 排序、错误页", "13"],
    ],
    widths=[5.4, 8.2, 1.6],
)
body("执行命令与结果：", indent=False)
code("> python -m pytest\n============================= 39 passed in 1.30s =============================")

h2("5.2 手工验收")
table(
    ["用例", "操作", "预期结果", "结论"],
    [
        ["T1", "填写完整合法信息后创建", "跳转详情页，字段一致", "通过"],
        ["T2", "名称 / 课程 / 截止日期留空提交", "三条中文错误提示，不写库", "通过"],
        ["T3", "名称 100 字 / 101 字", "100 字成功，101 字被拒", "通过"],
        ["T4", "截止日期填 2026/12/01", "提示格式应为 YYYY-MM-DD", "通过"],
        ["T5", "打开任务详情页", "六个字段与时间全部展示", "通过"],
        ["T6", "编辑优先级 低 → 高", "详情页与列表同步更新", "通过"],
        ["T7", "删除 → 确认页 → 确认删除", "确认前不删，确认后消失", "通过"],
        ["T8", "状态依次切为 进行中→已完成→待完成", "每次成功，徽章随之变化", "通过"],
        ["T9", "查看昨天 / 今天 / +3 天 / +4 天到期任务", "逾期、即将到期、无提醒分别正确", "通过"],
        ["T10", "课程 / 状态 / 优先级 / 关键字的单独与组合筛选", "结果正确，无结果时有提示", "通过"],
    ],
    widths=[1.0, 5.4, 6.6, 1.6],
)
body("界面截图：", indent=False)
side = os.path.join(BASE, "_side.png")
if os.path.exists(side):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(side, width=Cm(12.0))
    caption("图 1  左：任务列表页（统计卡、组合筛选、逾期红标 / 即将到期橙标）；"
            "中：任务详情页完整字段；右：新建页校验失败的中文提示")
else:
    picture("screenshot_index.png", 12.4)
    caption("图 1  任务列表页：统计卡、组合筛选区、逾期（红）/ 即将到期（橙）徽章")
    picture("screenshot_detail.png", 11.2)
    caption("图 2  任务详情页：完整字段展示与状态切换下拉框")
    picture("screenshot_validation.png", 8.0)
    caption("图 3  新建页校验失败：中文错误提示且保留已填内容")

# ==================== 六、总结 ====================
h1("六、总结与体会")
body(
    "本次实验完整走了一遍「读懂需求 → 设计结构 → 编码 → 测试 → 验收」的过程。"
    "最大的体会是：AI 能大幅加快代码产出，但它给出的判断未必正确，必须用可观察的证据去验证。"
    "问题 1 中把「下拉框空白」误判为 CSS 问题就是例子——"
    "如果只改样式不去读 options.length，缺陷会被样式改动掩盖，排查方向越走越偏。"
)
body(
    "第二点体会是校验要做两层。只在应用层校验，一旦有新入口就容易漏；"
    "只在数据库层校验，用户看到的又只是「操作失败」这类笼统提示。"
    "本项目在 validation.py 给出中文的逐字段提示，同时在建表时用 CHECK 约束兜底，两者互补。"
)
body(
    "第三点是测试的价值。39 条用例中有几条是专门为已经修过的缺陷补的回归用例，"
    "例如详情页状态下拉框那条。缺陷修完不等于不会再犯，只有把它固化成断言，"
    "后续修改才不会悄悄把它改回去。"
)
body(
    "不足之处：系统目前没有登录与多用户支持，也不支持云部署，仅在本地单机使用；"
    "界面为原生 HTML + CSS，没有响应式适配，移动端体验一般。"
    "如果继续完善，计划加上按课程分组视图、简单的时间线统计，以及把提醒窗口天数做成可配置项。"
)

doc.save(OUT)
print("saved:", OUT)