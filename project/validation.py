"""
校验与派生逻辑：把 SRS 里的约束集中在一处，便于测试和复用。

- validate_task(): 对应 FR-01（名称/课程/截止日期/优先级/状态校验）
- decorate():      对应 FR-07（逾期、即将到期标识）和展示用派生字段
"""
from datetime import date, datetime, timedelta

from . import db as database

# ---------- 字段长度约束（SRS A.2 数据项）----------
NAME_MAX = 100
COURSE_MAX = 60
DESC_MAX = 1000
DATE_FMT = "%Y-%m-%d"


def parse_date(value: str):
    """严格按 YYYY-MM-DD 解析；非法返回 None。"""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), DATE_FMT).date()
    except (ValueError, AttributeError):
        return None


def validate_task(form: dict) -> tuple:
    """
    校验任务表单。

    返回 (cleaned: dict | None, errors: dict[str, str])。
    cleaned 中已去掉首尾空白；errors 为“字段 -> 中文错误信息”，可直接回显。
    """
    errors = {}

    name = (form.get("name") or "").strip()
    course = (form.get("course") or "").strip()
    description = (form.get("description") or "").strip()
    due_raw = (form.get("due_date") or "").strip()
    priority = (form.get("priority") or "").strip() or database.PRIORITY_MID
    status = (form.get("status") or "").strip() or database.STATUS_TODO

    # 名称：必填，1—100 字
    if not name:
        errors["name"] = "任务名称不能为空"
    elif len(name) > NAME_MAX:
        errors["name"] = f"任务名称不能超过 {NAME_MAX} 个字"

    # 课程：必填，1—60 字
    if not course:
        errors["course"] = "所属课程不能为空"
    elif len(course) > COURSE_MAX:
        errors["course"] = f"所属课程不能超过 {COURSE_MAX} 个字"

    # 描述：可选，不超过 1000 字
    if len(description) > DESC_MAX:
        errors["description"] = f"任务描述不能超过 {DESC_MAX} 个字"

    # 截止日期：必填，格式 YYYY-MM-DD
    due = parse_date(due_raw)
    if not due_raw:
        errors["due_date"] = "截止日期不能为空"
    elif due is None:
        errors["due_date"] = "截止日期格式应为 YYYY-MM-DD，且必须是真实存在的日期"

    if priority not in database.PRIORITIES:
        errors["priority"] = "优先级只能是 高 / 中 / 低"

    if status not in database.STATUSES:
        errors["status"] = "状态只能是 待完成 / 进行中 / 已完成"

    if errors:
        return None, errors

    return {
        "name": name,
        "course": course,
        "description": description,
        "due_date": due.strftime(DATE_FMT),
        "priority": priority,
        "status": status,
    }, {}


def decorate(row, today: date = None) -> dict:
    """
    把数据库行转成可直接渲染的字典，附加展示字段。

    due_state: 'overdue'（逾期）/ 'due_soon'（即将到期）/ ''（正常）
    依据 FR-07：仅对未完成任务判断；已完成任务不显示任何提醒。
    """
    today = today or date.today()
    item = dict(row)
    due = parse_date(item["due_date"])
    item["due_state"] = ""
    item["due_label"] = ""

    if due is not None and item["status"] != database.STATUS_DONE:
        if due < today:
            item["due_state"] = "overdue"
            item["due_label"] = "已逾期"
        elif due <= today + timedelta(days=database.DUE_SOON_DAYS):
            item["due_state"] = "due_soon"
            item["due_label"] = "即将到期"

    item["days_left"] = (due - today).days if due else None
    return item


def summary(rows: list) -> dict:
    """
    对应 FR-08：任务总数、已完成数、完成率。
    总数为 0 时完成率显示 0%，避免除零。
    """
    total = len(rows)
    done = sum(1 for r in rows if r["status"] == database.STATUS_DONE)
    rate = 0 if total == 0 else round(done * 100 / total, 1)
    return {"total": total, "done": done, "rate": rate}