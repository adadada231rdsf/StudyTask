"""
数据库层：连接管理、建表、行工厂与任务状态常量。

设计取舍：
- 直接使用标准库 sqlite3，不引入 ORM。本系统只有一张业务表，
  ORM 会带来不必要的依赖和隐式行为，SQL 反而更容易审查。
- 所有写操作使用参数化查询，避免 SQL 注入。
- 外键约束打开，保证数据一致性。
"""
import sqlite3
from pathlib import Path

from flask import current_app, g

# ---------- 业务常量 ----------
STATUS_TODO = "待完成"
STATUS_DOING = "进行中"
STATUS_DONE = "已完成"
STATUSES = (STATUS_TODO, STATUS_DOING, STATUS_DONE)

PRIORITY_HIGH = "高"
PRIORITY_MID = "中"
PRIORITY_LOW = "低"
PRIORITIES = (PRIORITY_HIGH, PRIORITY_MID, PRIORITY_LOW)

# 逾期提醒窗口（天）：未来 3 天内到期记为“即将到期”
DUE_SOON_DAYS = 3

SCHEMA = """
CREATE TABLE IF NOT EXISTS task (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    course      TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    due_date    TEXT    NOT NULL,           -- 存为 YYYY-MM-DD，字典序即日期序
    priority    TEXT    NOT NULL DEFAULT '中',
    status      TEXT    NOT NULL DEFAULT '待完成',
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL,
    CHECK (priority IN ('高', '中', '低')),
    CHECK (status   IN ('待完成', '进行中', '已完成'))
);

CREATE INDEX IF NOT EXISTS idx_task_due      ON task(due_date);
CREATE INDEX IF NOT EXISTS idx_task_course   ON task(course);
CREATE INDEX IF NOT EXISTS idx_task_status   ON task(status);
CREATE INDEX IF NOT EXISTS idx_task_priority ON task(priority);
"""


def get_db() -> sqlite3.Connection:
    """取得当前请求（或应用上下文）内的数据库连接。"""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """建表：幂等，可重复执行。"""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def init_app(app) -> None:
    """注册到 Flask 应用：请求结束自动关闭连接。"""
    app.teardown_appcontext(close_db)
    # 确保 SQLite 文件所在目录存在
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        init_db()