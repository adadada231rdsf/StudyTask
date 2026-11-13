# -*- coding: utf-8 -*-
"""生成《实验一 演示 PPT》。运行：python docs/build_pptx.py"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "实验一_演示_宋逸轩.pptx")

# ---------- 配色 ----------
INK = RGBColor(0x1F, 0x23, 0x28)
MUTED = RGBColor(0x6B, 0x72, 0x80)
ACCENT = RGBColor(0x1A, 0x5C, 0x8A)
ACCENT2 = RGBColor(0xC8, 0x4B, 0x31)
BG = RGBColor(0xF7, 0xF8, 0xFA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xDD, 0xE2, 0xE8)

FONT = "微软雅黑"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
W = prs.slide_width
H = prs.slide_height
BLANK = prs.slide_layouts[6]


def set_font(run, size, bold=False, color=INK, font=FONT):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font._rPr.get_or_change_to_latin() if False else None
    from pptx.oxml.ns import qn
    rPr = run.font._rPr
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", font)


def textbox(slide, x, y, w, h, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    tf.paragraphs[0].alignment = align
    return tf


def para(tf, text, size=18, bold=False, color=INK, space_before=0, space_after=6,
         align=PP_ALIGN.LEFT, first=False, line=1.25):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    p.line_spacing = line
    r = p.add_run()
    r.text = text
    set_font(r, size, bold, color)
    return p


def rect(slide, x, y, w, h, fill=None, line_col=None, line_w=1.0, shape=MSO_SHAPE.RECTANGLE, adj=None):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line_col is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line_col
        s.line.width = Pt(line_w)
    s.shadow.inherit = False
    if adj is not None:
        try:
            s.adjustments[0] = adj
        except Exception:
            pass
    s.text_frame.text = ""
    return s


def new_slide(bg=WHITE):
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, W, H, fill=bg)
    return s


def header(slide, kicker, title_text, idx=None):
    rect(slide, Inches(0.75), Inches(0.62), Inches(0.09), Inches(0.5), fill=ACCENT)
    tf = textbox(slide, Inches(1.0), Inches(0.6), Inches(10.5), Inches(0.4))
    para(tf, kicker, 12, True, ACCENT, first=True, space_after=0)
    tf2 = textbox(slide, Inches(1.0), Inches(0.92), Inches(11.0), Inches(0.6))
    para(tf2, title_text, 28, True, INK, first=True, space_after=0)
    if idx is not None:
        tf3 = textbox(slide, W - Inches(1.2), Inches(0.7), Inches(0.6), Inches(0.4),
                      align=PP_ALIGN.RIGHT)
        para(tf3, f"{idx:02d}", 13, True, LINE, first=True)
    rect(slide, Inches(0.75), Inches(1.62), W - Inches(1.5), Emu(9525), fill=LINE)


def bullet(tf, text, size=17, color=INK, bold=False, space_after=10, mark="—", mark_color=None):
    p = tf.add_paragraph()
    p.space_after = Pt(space_after)
    p.line_spacing = 1.3
    r0 = p.add_run()
    r0.text = mark + "  "
    set_font(r0, size, True, mark_color or ACCENT)
    r = p.add_run()
    r.text = text
    set_font(r, size, bold, color)
    return p


def slide_table(slide, data, x, y, col_w, row_h=0.42, header_h=0.45,
                font=13, head_font=13):
    rows, cols = len(data), len(data[0])
    total_w = sum(col_w)
    gt = slide.shapes.add_table(rows, cols, x, y, Inches(total_w),
                                Inches(header_h + row_h * (rows - 1)))
    tbl = gt.table
    tbl.first_row = True
    for i, wd in enumerate(col_w):
        tbl.columns[i].width = Inches(wd)
    tbl.rows[0].height = Inches(header_h)
    for r in range(1, rows):
        tbl.rows[r].height = Inches(row_h)
    for r in range(rows):
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.margin_left = Inches(0.1)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = ACCENT if r == 0 else (WHITE if r % 2 else BG)
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = str(data[r][c])
            set_font(run, head_font if r == 0 else font, r == 0,
                     WHITE if r == 0 else INK)
    return gt


def bullet_lit(tf, head, rest, size=12.5, space_after=9, bold_color=None):
    """加粗前缀 + 普通正文，避免手动换行。"""
    p = tf.add_paragraph()
    p.space_after = Pt(space_after)
    p.line_spacing = 1.3
    r0 = p.add_run()
    r0.text = "·  "
    set_font(r0, size, True, ACCENT)
    r1 = p.add_run()
    r1.text = head
    set_font(r1, size, True, bold_color or INK)
    if rest:
        r2 = p.add_run()
        r2.text = rest
        set_font(r2, size, False, INK)
    return p


# ==================== 1. 封面 ====================
s = new_slide(BG)
rect(s, 0, 0, Inches(0.28), H, fill=ACCENT)
tf = textbox(s, Inches(1.5), Inches(1.9), Inches(10), Inches(0.5))
para(tf, "软件工程实验一", 18, True, ACCENT, first=True, space_after=0)

tf = textbox(s, Inches(1.5), Inches(2.45), Inches(10.5), Inches(1.5))
para(tf, "个人学习任务管理系统", 46, True, INK, first=True, space_after=4, line=1.1)
para(tf, "StudyTask", 32, True, ACCENT, space_after=0, line=1.1)

rect(s, Inches(1.5), Inches(4.35), Inches(1.6), Emu(28575), fill=ACCENT2)

tf = textbox(s, Inches(1.5), Inches(4.75), Inches(10), Inches(1.2))
para(tf, "Python · Flask · SQLite   ｜   FR-01 ~ FR-10   ｜   39 条测试全通过",
     17, False, MUTED, first=True, space_after=10)
para(tf, "242806010116   宋逸轩   24 级计科", 17, True, INK, space_after=0)

# ==================== 2. 项目概览 ====================
s = new_slide()
header(s, "OVERVIEW", "项目概览", 2)

cards = [
    ("7", "张页面", "列表 / 新建 / 详情 / 编辑 / 删除确认 / 错误页"),
    ("10", "项功能需求", "FR-01 ~ FR-10 全部实现并通过验收"),
    ("39", "条自动化测试", "pytest · 39 passed in 1.30s"),
    ("920", "行代码", "5 个 Python 模块 + 6 个模板 + 手写 CSS"),
]
cw = Inches(2.85)
gap = Inches(0.28)
x0 = Inches(0.75)
for i, (num, label, sub) in enumerate(cards):
    x = x0 + i * (cw + gap)
    rect(s, x, Inches(2.0), cw, Inches(2.05), fill=BG)
    rect(s, x, Inches(2.0), cw, Inches(0.06), fill=ACCENT2 if i == 2 else ACCENT)
    tf = textbox(s, x + Inches(0.25), Inches(2.25), cw - Inches(0.5), Inches(0.7))
    para(tf, num, 40, True, ACCENT, first=True, space_after=0, line=1.0)
    tf = textbox(s, x + Inches(0.25), Inches(2.95), cw - Inches(0.5), Inches(0.35))
    para(tf, label, 16, True, INK, first=True, space_after=0)
    tf = textbox(s, x + Inches(0.25), Inches(3.35), cw - Inches(0.5), Inches(0.6))
    para(tf, sub, 11.5, False, MUTED, first=True, space_after=0, line=1.2)

tf = textbox(s, Inches(0.75), Inches(4.5), W - Inches(1.5), Inches(2.2))
para(tf, "它解决什么问题", 17, True, INK, first=True, space_after=10)
bullet(tf, "学生要同时跟多门课的任务，截止日期散落在各处，哪个快到期、哪个已经逾期，没有统一入口")
bullet_lit(tf, "目标：", "一个本地运行的单用户工具，录入 → 筛选 → 状态流转 → 到期提醒，全流程闭环",
           space_after=10)
bullet(tf, "范围：不做登录与多用户，不做云部署（按指导书 A.5），数据存本地 SQLite 文件")

# ==================== 3. 功能清单 ====================
s = new_slide()
header(s, "FEATURES", "功能需求与实现位置", 3)
data = [
    ["需求", "功能", "实现要点", "位置"],
    ["FR-01", "新建任务", "服务端校验后入库，成功跳转详情", "views.py / validation.py"],
    ["FR-02", "列表与详情", "列表主字段，详情全字段；不存在 404", "index.html / detail.html"],
    ["FR-03", "编辑任务", "复用表单，失败保留用户输入", "views.py: edit()"],
    ["FR-04", "删除任务", "GET 只确认，POST 才真删", "views.py: delete()"],
    ["FR-05", "状态流转", "三状态，列表页直接切换", "repository.set_status()"],
    ["FR-06", "组合筛选", "课程+状态+优先级+关键字", "repository.list_tasks()"],
    ["FR-07", "到期提醒", "逾期红 / 3 天内橙 / 已完成不提醒", "validation.decorate()"],
    ["FR-08", "统计信息", "总数、已完成数、完成率", "validation.summary()"],
    ["FR-09", "排序", "已完成沉底→日期升序→优先级", "ORDER BY 子句"],
    ["FR-10", "数据校验", "长度/必填/日期真实性/枚举", "validation.py + CHECK"],
]
slide_table(s, data, Inches(0.75), Inches(1.95), [1.1, 2.1, 5.2, 3.4],
            row_h=0.42, font=12.5, head_font=12.5)

# ==================== 4. 架构 ====================
s = new_slide()
header(s, "ARCHITECTURE", "分层架构", 4)

layers = [
    ("路由层  views.py", "接收请求 · 调用校验 · 渲染模板 · 重定向", ACCENT),
    ("校验层  validation.py", "字段校验 · 日期解析 · 逾期与统计派生", ACCENT),
    ("数据访问层  repository.py", "集中全部 SQL · 组合筛选 · 排序", ACCENT),
    ("数据库层  db.py", "连接管理 · 建表 SQL · 业务常量", ACCENT),
]
y = Inches(2.0)
bw = Inches(7.4)
for i, (name, desc, color) in enumerate(layers):
    yy = y + i * Inches(1.02)
    rect(s, Inches(0.85), yy, bw, Inches(0.82), fill=BG, line_col=LINE)
    rect(s, Inches(0.85), yy, Inches(0.08), Inches(0.82), fill=color)
    tf = textbox(s, Inches(1.12), yy + Inches(0.11), bw - Inches(0.4), Inches(0.3))
    para(tf, name, 16, True, INK, first=True, space_after=0)
    tf = textbox(s, Inches(1.12), yy + Inches(0.45), bw - Inches(0.4), Inches(0.3))
    para(tf, desc, 11.5, False, MUTED, first=True, space_after=0)
    if i < 3:
        ar = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(4.35), yy + Inches(0.84),
                                Inches(0.3), Inches(0.16))
        ar.fill.solid()
        ar.fill.fore_color.rgb = LINE
        ar.line.fill.background()
        ar.shadow.inherit = False

# 右侧说明
rect(s, Inches(8.7), Inches(2.0), Inches(3.9), Inches(4.15), fill=BG)
tf = textbox(s, Inches(9.0), Inches(2.25), Inches(3.3), Inches(3.7))
para(tf, "设计取舍", 16, True, ACCENT2, first=True, space_after=12)
bullet(tf, "路由层不写 SQL、不写校验规则，改需求只动一处", 12.5, space_after=9, mark="·")
bullet(tf, "不用 ORM：只有一张表，手写 SQL 更好审查", 12.5, space_after=9, mark="·")
bullet(tf, "应用工厂 create_app()，测试可注入临时数据库", 12.5, space_after=9, mark="·")
bullet(tf, "全部 SQL 参数化占位符，防注入", 12.5, space_after=9, mark="·")

# ==================== 5. 数据库 ====================
s = new_slide()
header(s, "DATA MODEL", "数据库设计：单表 + 双重约束", 5)

code_lines = [
    "CREATE TABLE task (",
    "  id          INTEGER PRIMARY KEY AUTOINCREMENT,",
    "  name        TEXT NOT NULL,",
    "  course      TEXT NOT NULL,",
    "  description TEXT NOT NULL DEFAULT '',",
    "  due_date    TEXT NOT NULL,   -- YYYY-MM-DD",
    "  priority    TEXT NOT NULL DEFAULT '中',",
    "  status      TEXT NOT NULL DEFAULT '待完成',",
    "  created_at  TEXT NOT NULL,",
    "  updated_at  TEXT NOT NULL,",
    "  CHECK (priority IN ('高','中','低')),",
    "  CHECK (status IN ('待完成','进行中','已完成'))",
    ");",
]
rect(s, Inches(0.75), Inches(2.0), Inches(6.55), Inches(4.3), fill=RGBColor(0x1E, 0x24, 0x2B))
tf = textbox(s, Inches(1.0), Inches(2.2), Inches(6.1), Inches(4.0))
for i, ln in enumerate(code_lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(2)
    p.line_spacing = 1.05
    r = p.add_run()
    r.text = ln
    col = RGBColor(0x8F, 0xC8, 0xE8) if ln.strip().startswith("--") else RGBColor(0xE4, 0xE8, 0xEC)
    set_font(r, 11, False, col, "Consolas")

tf = textbox(s, Inches(7.75), Inches(2.0), Inches(4.9), Inches(4.3))
para(tf, "三个设计要点", 17, True, INK, first=True, space_after=12)
bullet_lit(tf, "日期存 TEXT 固定 YYYY-MM-DD", "，字典序 = 日期序，排序比较直接交给 SQL",
           size=13.5, space_after=14)
bullet_lit(tf, "CHECK 约束兜底", "，即使代码漏校验，非法状态也写不进库",
           size=13.5, space_after=14)
bullet_lit(tf, "四列建索引", " course / status / priority / due_date，组合筛选不全表扫描",
           size=13.5, space_after=18)
bullet(tf, "名称课程长度上限由应用层校验（SQLite 无 VARCHAR 长度约束）",
       12, color=MUTED, space_after=0)

# ==================== 6. 关键逻辑 ====================
s = new_slide()
header(s, "LOGIC", "三处关键逻辑", 6)

blocks = [
    ("FR-07  到期提醒",
     "只在未完成任务上判断：\n\n"
     "due_date < 今天        → 已逾期（红）\n"
     "今天 ≤ due_date ≤ +3天 → 即将到期（橙）\n"
     "状态 = 已完成          → 一律不提醒",
     ACCENT2),
    ("FR-09  排序规则",
     "CASE WHEN status='已完成' THEN 1 ELSE 0 END,\n"
     "due_date ASC,\n"
     "CASE priority WHEN '高' THEN 0 WHEN '中' THEN 1 ELSE 2 END,\n"
     "id DESC\n\n"
     "→ 未完成在前，最紧急的排最上面",
     ACCENT),
    ("FR-08  统计口径",
     "统计基于全量任务（all_tasks()），\n"
     "不是筛选后的结果。\n\n"
     "理由：一筛选百分比就变，\n"
     "用户会误以为数据出错。\n\n"
     "总数 0 时直接返回 0%，不做除法",
     ACCENT),
]
bw = Inches(3.85)
for i, (title, content, color) in enumerate(blocks):
    x = Inches(0.75) + i * (bw + Inches(0.3))
    rect(s, x, Inches(2.0), bw, Inches(4.35), fill=BG)
    rect(s, x, Inches(2.0), bw, Inches(0.07), fill=color)
    tf = textbox(s, x + Inches(0.28), Inches(2.3), bw - Inches(0.56), Inches(0.4))
    para(tf, title, 15.5, True, color, first=True, space_after=0)
    tf = textbox(s, x + Inches(0.28), Inches(2.85), bw - Inches(0.56), Inches(3.3))
    lines = content.split("\n")
    for j, ln in enumerate(lines):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.space_after = Pt(0)
        p.line_spacing = 1.25
        r = p.add_run()
        r.text = ln if ln else " "
        mono = ("due_date" in ln or "CASE" in ln or "today" in ln)
        set_font(r, 10.5 if mono else 12.5, False,
                 RGBColor(0x2D, 0x5A, 0x7A) if mono else INK,
                 "Consolas" if mono else FONT)

# ==================== 7. 界面① ====================
s = new_slide()
header(s, "SCREENSHOT 1", "任务列表页：统计 · 筛选 · 到期徽章", 7)
img = os.path.join(BASE, "screenshot_index.png")
rect(s, Inches(0.75), Inches(1.95), Inches(9.3), Inches(4.85), fill=BG)
pic = s.shapes.add_picture(img, Inches(0.9), Inches(2.05), height=Inches(4.6))
pic.left = int((Inches(0.75) + Inches(9.3) - pic.width) / 2)

tf = textbox(s, Inches(10.35), Inches(2.0), Inches(2.4), Inches(4.6))
para(tf, "看点", 15, True, ACCENT2, first=True, space_after=10)
for t in ["顶部三张统计卡：总数 / 已完成 / 完成率",
          "筛选区四项可任意组合，刷新后条件保留",
          "逾期任务：红色「已逾期」徽章",
          "3 天内到期：橙色「即将到期」徽章",
          "已完成任务自动沉到列表底部且不提醒",
          "每行可直接下拉改状态，无需进详情"]:
    bullet(tf, t, 11, space_after=10, mark="·")

# ==================== 8. 界面② ====================
s = new_slide()
header(s, "SCREENSHOT 2", "校验与详情：错误提示与字段完整性", 8)
img1 = os.path.join(BASE, "screenshot_validation.png")
img2 = os.path.join(BASE, "screenshot_detail.png")
rect(s, Inches(0.75), Inches(1.95), Inches(5.85), Inches(4.75), fill=BG)
p1 = s.shapes.add_picture(img1, Inches(0.9), Inches(2.05), height=Inches(3.15))
p1.left = int(Inches(0.75) + (Inches(5.85) - p1.width) / 2)
rect(s, Inches(6.9), Inches(1.95), Inches(5.85), Inches(4.75), fill=BG)
p2 = s.shapes.add_picture(img2, Inches(7.05), Inches(2.05), height=Inches(3.15))
p2.left = int(Inches(6.9) + (Inches(5.85) - p2.width) / 2)

tf = textbox(s, Inches(0.9), Inches(5.4), Inches(5.55), Inches(1.15))
para(tf, "校验失败：逐字段中文提示，已填内容全部保留", 12, True, ACCENT2,
     first=True, space_after=4)
para(tf, "名称 / 课程 / 截止日期的错误分别标在对应字段下方，返回 HTTP 400", 10.5, False, MUTED,
     space_after=0, line=1.2)

tf = textbox(s, Inches(7.05), Inches(5.45), Inches(5.55), Inches(1.1))
para(tf, "详情页：六个字段 + 创建/更新时间完整展示", 12, True, ACCENT,
     first=True, space_after=4)
para(tf, "状态下拉框三选项，切换后 302 回本页并刷新徽章", 10.5, False, MUTED,
     space_after=0, line=1.2)

# ==================== 9. 问题 1 ====================
s = new_slide()
header(s, "ISSUE 1 / 4", "详情页下拉框一片空白", 9)

steps = [
    ("现象", "详情页状态下拉框没有任何选项，页面也不报错", MUTED),
    ("假设 ① ✗", "怀疑 CSS：.inline 用了 flex，select 被压缩", ACCENT2),
    ("验证 ①", "加 flex: 0 0 auto; min-width: 92px，重截图\n框宽了，里面依然空 → 不是样式问题", ACCENT),
    ("假设 ② ✓", "读 options.length === 0 → 选项根本没渲染", ACCENT),
    ("根因", "detail() 调 render_template 时漏传 statuses\nJinja 对未定义变量静默渲染为空", ACCENT2),
]
y = Inches(1.95)
for i, (tag, txt, col) in enumerate(steps):
    yy = y + i * Inches(0.8)
    rect(s, Inches(0.8), yy, Inches(1.75), Inches(0.62), fill=BG, line_col=LINE)
    tf = textbox(s, Inches(0.8), yy, Inches(1.75), Inches(0.62),
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    para(tf, tag, 12, True, col, first=True, space_after=0, line=1.1)
    tf = textbox(s, Inches(2.75), yy, Inches(6.3), Inches(0.62), anchor=MSO_ANCHOR.MIDDLE)
    for j, ln in enumerate(txt.split("\n")):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.space_after = Pt(0)
        p.line_spacing = 1.15
        r = p.add_run()
        r.text = ln
        set_font(r, 12.5, False, INK)

rect(s, Inches(9.3), Inches(1.95), Inches(3.25), Inches(3.9), fill=RGBColor(0x1E, 0x24, 0x2B))
tf = textbox(s, Inches(9.5), Inches(2.12), Inches(2.9), Inches(1.7))
para(tf, "# 修复", 11, False, RGBColor(0x8F, 0xC8, 0xE8), first=True, space_after=6)
for ln in ['render_template(',
           '  "detail.html",',
           '  task=decorate(row),',
           '  statuses=database',
           '            .STATUSES)']:
    p = tf.add_paragraph()
    p.space_after = Pt(1)
    r = p.add_run()
    r.text = ln
    set_font(r, 10, False, RGBColor(0xE4, 0xE8, 0xEC), "Consolas")

rect(s, Inches(9.55), Inches(3.72), Inches(2.75), Emu(9525), fill=RGBColor(0x3A, 0x44, 0x50))
tf = textbox(s, Inches(9.5), Inches(3.9), Inches(2.9), Inches(1.8))
para(tf, "补回归测试", 11, True, RGBColor(0xE8, 0x8A, 0x76), first=True, space_after=5)
for ln in ['test_t5_detail_status_',
           'options_rendered']:
    p = tf.add_paragraph()
    p.space_after = Pt(1)
    r = p.add_run()
    r.text = ln
    set_font(r, 9.5, False, RGBColor(0xE4, 0xE8, 0xEC), "Consolas")
para(tf, "断言三种状态都在，且当前项 selected", 9.5, False,
     RGBColor(0x9F, 0xAD, 0xBB), space_after=0, line=1.25)

tf = textbox(s, Inches(0.8), Inches(5.95), Inches(8.2), Inches(0.9))
para(tf, "教训：修完样式框变宽了，「看起来在变好」很容易让人停手。"
         "必须拿可观察的证据（options.length）证伪，才能跳出错误方向。",
     12.5, True, ACCENT2, first=True, space_after=0, line=1.35)

# ==================== 10. 问题 2-4 ====================
s = new_slide()
header(s, "ISSUE 2 · 3 · 4", "另外三个真实问题", 10)

items = [
    ("问题 2　统计数字不刷新",
     "另一标签页新建任务后回首页，总数还是旧的。\n"
     "统计在服务端现算，问题是浏览器用了缓存页没有重新请求。",
     "POST-Redirect-GET：新建 302→详情，删除 302→首页，改状态 302→来源页。\n"
     "测试用 follow_redirects=False 断言 302。",
     ACCENT),
    ("问题 3　pytest 报 WinError 5",
     "PytestCacheWarning：无法创建 .pytest_cache 缓存目录，桌面受安全软件保护。\n"
     "不影响结果，39 条依然全过，只是输出噪音。",
     "pyproject.toml 加 -p no:cacheprovider 关闭缓存插件。\n"
     "代价：--lf 失效，对当前项目规模可接受。",
     ACCENT),
    ("问题 4　2026-02-30 被放行",
     "正则 ^\\d{4}-\\d{2}-\\d{2}$ 只管格式，2026-02-30 能通过，\n"
     "存进去后排序与逾期判断都会错。格式合法 ≠ 日期存在。",
     "改用 datetime.strptime(v, \"%Y-%m-%d\") 解析，失败即非法。\n"
     "用例覆盖 2026-13-01 / 2026-02-30 / abc / 20261201。",
     ACCENT2),
]
bw = Inches(3.85)
for i, (title, prob, fix, color) in enumerate(items):
    x = Inches(0.75) + i * (bw + Inches(0.3))
    rect(s, x, Inches(1.95), bw, Inches(4.6), fill=BG)
    rect(s, x, Inches(1.95), bw, Inches(0.07), fill=color)
    tf = textbox(s, x + Inches(0.26), Inches(2.18), bw - Inches(0.52), Inches(0.4))
    para(tf, title, 14, True, INK, first=True, space_after=0)
    tf = textbox(s, x + Inches(0.26), Inches(2.68), bw - Inches(0.52), Inches(1.9))
    para(tf, prob, 10.5, False, MUTED, first=True, space_after=0, line=1.3)
    rect(s, x + Inches(0.26), Inches(4.35), bw - Inches(0.52), Emu(9525), fill=LINE)
    tf = textbox(s, x + Inches(0.26), Inches(4.5), bw - Inches(0.52), Inches(1.8))
    para(tf, "修复", 11, True, color, first=True, space_after=4)
    para(tf, fix, 10.5, False, INK, space_after=0, line=1.3)

# ==================== 11. 测试 ====================
s = new_slide()
header(s, "TESTING", "39 条自动化测试，覆盖 T1 ~ T10", 11)

rect(s, Inches(0.75), Inches(1.95), Inches(6.0), Inches(1.55), fill=RGBColor(0x1E, 0x24, 0x2B))
tf = textbox(s, Inches(1.0), Inches(2.15), Inches(5.6), Inches(1.2))
for i, ln in enumerate(["> python -m pytest",
                        "============================= 39 passed in 1.30s ===================="]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(6)
    r = p.add_run()
    r.text = ln
    set_font(r, 13 if i == 0 else 11.5, False,
             RGBColor(0xE4, 0xE8, 0xEC) if i == 0 else RGBColor(0x6F, 0xD1, 0x8A),
             "Consolas")

data = [
    ["测试文件", "覆盖", "数量"],
    ["test_create_validation.py", "T1~T5 · 默认值 · XSS · 回归", "13"],
    ["test_edit_delete_status.py", "T6~T9 · 编辑 · 删除 · 状态 · 提醒", "13"],
    ["test_filter_stats.py", "T10 · 统计 · 排序 · 错误页", "13"],
]
slide_table(s, data, Inches(0.75), Inches(4.6), [3.5, 3.8, 0.85], row_h=0.42, font=11,
            header_h=0.42)

tf = textbox(s, Inches(7.35), Inches(1.95), Inches(4.9), Inches(4.8))
para(tf, "测试策略", 16, True, INK, first=True, space_after=10)
bullet(tf, "应用工厂注入临时数据库，互不污染", 11.5, space_after=9)
bullet(tf, "边界值：100/101 字、今天 / +3 / +4 天", 11.5, space_after=9)
bullet(tf, "安全：<script> 转义、' OR 1=1;-- 不出全量", 11, space_after=9)
bullet(tf, "为已修缺陷补回归用例，防止改回去", 11.5, space_after=9)
bullet(tf, "手工验收 T1~T10 逐条走查", 11.5, space_after=9)

# ==================== 12. AI 协作 ====================
s = new_slide()
header(s, "AI COLLABORATION", "AI 做了什么，人做了什么", 12)

rect(s, Inches(0.75), Inches(1.95), Inches(5.75), Inches(3.5), fill=BG)
rect(s, Inches(0.75), Inches(1.95), Inches(5.75), Inches(0.07), fill=ACCENT)
tf = textbox(s, Inches(1.0), Inches(2.2), Inches(5.3), Inches(3.1))
para(tf, "AI 承担  ·  A2 ~ A10", 15, True, ACCENT, first=True, space_after=12)
for t in ["分层结构与表结构设计",
          "校验规则、逾期与统计逻辑",
          "路由、模板与手写样式",
          "39 条 pytest 用例",
          "README / 验收表 / 开发日志框架"]:
    bullet(tf, t, 13, space_after=8, mark="·")

rect(s, Inches(6.85), Inches(1.95), Inches(5.75), Inches(3.5), fill=BG)
rect(s, Inches(6.85), Inches(1.95), Inches(5.75), Inches(0.07), fill=ACCENT2)
tf = textbox(s, Inches(7.1), Inches(2.2), Inches(5.3), Inches(3.1))
para(tf, "人承担  ·  A1 / A11 / A12", 15, True, ACCENT2, first=True, space_after=12)
for t in ["确认需求理解是否正确",
          "真实环境运行与验证（Python 3.13 + Flask 2.3.3）",
          "T1~T10 逐条手工验收",
          "Git 提交与仓库管理",
          "对每处 AI 输出作出采纳 / 修改 / 拒绝的判断"]:
    bullet(tf, t, 13, space_after=8, mark="·")

rect(s, Inches(0.75), Inches(5.75), Inches(11.85), Inches(1.1), fill=RGBColor(0xFD, 0xF3, 0xEF))
tf = textbox(s, Inches(1.0), Inches(5.95), Inches(11.35), Inches(0.8))
para(tf, "最典型的一次判断：AI 把「下拉框空白」判成 CSS 问题，人的追问把它逼回了模板变量。"
         "AI 产出快，但它的第一判断经常是错的 —— 验证这一步不能外包。",
     13, True, RGBColor(0x8A, 0x33, 0x22), first=True, space_after=0, line=1.35)

# ==================== 13. 总结 ====================
s = new_slide()
header(s, "TAKEAWAYS", "总结与后续", 13)

cols = [
    ("证据优于直觉", "框变宽了看起来在变好，但 options.length 才是判据。没有可观察证据的「修好了」都不可信。"),
    ("校验做两层", "应用层给中文逐字段提示，数据库 CHECK 兜底。只有一层时，换个入口就漏。"),
    ("测试是保险", "为已修缺陷补回归用例 —— 缺陷修完不等于不会再犯，只有断言能锁住。"),
]
bw = Inches(3.85)
for i, (title, desc) in enumerate(cols):
    x = Inches(0.75) + i * (bw + Inches(0.3))
    rect(s, x, Inches(1.95), bw, Inches(2.1), fill=BG)
    tf = textbox(s, x + Inches(0.28), Inches(2.15), bw - Inches(0.56), Inches(0.4))
    para(tf, title, 15, True, ACCENT, first=True, space_after=0)
    tf = textbox(s, x + Inches(0.28), Inches(2.62), bw - Inches(0.56), Inches(1.35))
    para(tf, desc, 11.5, False, INK, first=True, space_after=0, line=1.35)

tf = textbox(s, Inches(0.75), Inches(4.35), Inches(5.7), Inches(2.4))
para(tf, "目前的不足", 15, True, ACCENT2, first=True, space_after=10)
for t in ["没有登录与多用户，只能单机使用",
          "原生 CSS 无响应式，移动端体验一般",
          "提醒窗口固定 3 天，不可配置"]:
    bullet(tf, t, 12.5, space_after=8, mark="·")

tf = textbox(s, Inches(6.85), Inches(4.35), Inches(5.7), Inches(2.4))
para(tf, "后续可以做的", 15, True, ACCENT, first=True, space_after=10)
for t in ["按课程分组的时间线视图",
          "提醒阈值做成配置项",
          "导出 Markdown / ICS 日历"]:
    bullet(tf, t, 12.5, space_after=8, mark="·")

# ==================== 14. 结束 ====================
s = new_slide(BG)
rect(s, 0, 0, Inches(0.28), H, fill=ACCENT)
tf = textbox(s, Inches(1.5), Inches(2.6), Inches(10.5), Inches(1.2))
para(tf, "谢谢", 54, True, INK, first=True, space_after=8, line=1.1)
tf = textbox(s, Inches(1.5), Inches(3.75), Inches(10.5), Inches(0.9))
para(tf, "演示完毕，请提问", 22, False, MUTED, first=True, space_after=0)
rect(s, Inches(1.5), Inches(4.55), Inches(1.6), Emu(28575), fill=ACCENT2)
tf = textbox(s, Inches(1.5), Inches(4.85), Inches(10.5), Inches(0.8))
para(tf, "github.com/adadada231rdsf/StudyTask", 15, True, ACCENT, first=True, space_after=4)
para(tf, "242806010116   宋逸轩", 13, False, MUTED, space_after=0)

prs.save(OUT)
print("saved:", OUT, "slides:", len(prs.slides.__iter__.__self__._sldIdLst))