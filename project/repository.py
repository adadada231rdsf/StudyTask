"""
数据访问层：任务表的全部 SQL 都集中在这里，路由只调用函数。

这样做的理由：SQL 一旦散落在路由里，筛选条件（FR-06 组合条件）
很容易写漏。集中后可以给查询单独写测试。
"""
from datetime import datetime

from . import db as database


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def list_tasks(course: str = "", status: str = "", priority: str = "",
               keyword: str = "") -> list:
    """
    按条件筛选任务（FR-06：支持课程 + 状态 + 优先级组合）。

    动态拼接 WHERE 子句，参数一律走占位符。排序规则：
    已完成沉底 -> 截止日期升序 -> 优先级高在前。
    """
    sql = "SELECT * FROM task WHERE 1=1"
    args = []

    if course:
        sql += " AND course = ?"
        args.append(course)
    if status:
        sql += " AND status = ?"
        args.append(status)
    if priority:
        sql += " AND priority = ?"
        args.append(priority)
    if keyword:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        like = f"%{keyword}%"
        args.extend([like, like])

    sql += """
        ORDER BY CASE WHEN status = '已完成' THEN 1 ELSE 0 END,
                 due_date ASC,
                 CASE priority WHEN '高' THEN 0 WHEN '中' THEN 1 ELSE 2 END,
                 id DESC
    """
    return database.get_db().execute(sql, args).fetchall()


def get_task(task_id: int):
    return database.get_db().execute(
        "SELECT * FROM task WHERE id = ?", (task_id,)
    ).fetchone()


def create_task(data: dict) -> int:
    db = database.get_db()
    now = _now()
    cur = db.execute(
        """INSERT INTO task (name, course, description, due_date, priority,
                             status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (data["name"], data["course"], data["description"], data["due_date"],
         data["priority"], data["status"], now, now),
    )
    db.commit()
    return cur.lastrowid


def update_task(task_id: int, data: dict) -> None:
    db = database.get_db()
    db.execute(
        """UPDATE task
              SET name = ?, course = ?, description = ?, due_date = ?,
                  priority = ?, status = ?, updated_at = ?
            WHERE id = ?""",
        (data["name"], data["course"], data["description"], data["due_date"],
         data["priority"], data["status"], _now(), task_id),
    )
    db.commit()


def set_status(task_id: int, status: str) -> None:
    """只改状态（FR-05），避免整行覆盖造成并发写入丢失。"""
    db = database.get_db()
    db.execute(
        "UPDATE task SET status = ?, updated_at = ? WHERE id = ?",
        (status, _now(), task_id),
    )
    db.commit()


def delete_task(task_id: int) -> None:
    db = database.get_db()
    db.execute("DELETE FROM task WHERE id = ?", (task_id,))
    db.commit()


def distinct_courses() -> list:
    """供筛选项下拉使用。"""
    rows = database.get_db().execute(
        "SELECT DISTINCT course FROM task ORDER BY course"
    ).fetchall()
    return [r["course"] for r in rows]


def all_tasks() -> list:
    """统计用：不受筛选影响的全量任务（FR-08）。"""
    return database.get_db().execute("SELECT * FROM task").fetchall()