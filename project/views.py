"""
路由层：页面与表单处理。

约定：
- 所有表单提交都走 POST + 服务器端校验，前端 JS 只做体验增强，不承担校验责任。
- 删除使用 GET /tasks/<id>/delete 展示确认页，POST 才真正删除（FR-04）。
- 出错时保留用户已填写内容（回填 form），避免用户重填。
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from . import db as database
from . import repository as repo
from .validation import decorate, summary, validate_task

bp = Blueprint("tasks", __name__)


def _form_from_request() -> dict:
    """从表单或查询串取字段，统一成 dict。"""
    src = request.form if request.method == "POST" else request.args
    return {
        "name": src.get("name", ""),
        "course": src.get("course", ""),
        "description": src.get("description", ""),
        "due_date": src.get("due_date", ""),
        "priority": src.get("priority", database.PRIORITY_MID),
        "status": src.get("status", database.STATUS_TODO),
    }


@bp.route("/")
def index():
    """首页：列表 + 组合筛选 + 统计（FR-02 / FR-06 / FR-08）。"""
    filters = {
        "course": request.args.get("course", "").strip(),
        "status": request.args.get("status", "").strip(),
        "priority": request.args.get("priority", "").strip(),
        "keyword": request.args.get("keyword", "").strip(),
    }
    rows = repo.list_tasks(**filters)
    tasks = [decorate(r) for r in rows]

    return render_template(
        "index.html",
        tasks=tasks,
        filters=filters,
        stats=summary(repo.all_tasks()),
        courses=repo.distinct_courses(),
        statuses=database.STATUSES,
        priorities=database.PRIORITIES,
    )


@bp.route("/tasks/new", methods=["GET", "POST"])
def create():
    """新建任务（FR-01）。"""
    form = _form_from_request()
    errors = {}

    if request.method == "POST":
        cleaned, errors = validate_task(request.form)
        if cleaned:
            task_id = repo.create_task(cleaned)
            flash("任务已创建", "success")
            return redirect(url_for("tasks.detail", task_id=task_id))
    return render_template(
        "form.html",
        mode="create",
        form=form,
        errors=errors,
        statuses=database.STATUSES,
        priorities=database.PRIORITIES,
        max_name=100, max_course=60, max_desc=1000,
    ), (400 if errors else 200)


@bp.route("/tasks/<int:task_id>")
def detail(task_id: int):
    """任务详情（FR-02）。"""
    row = repo.get_task(task_id)
    if row is None:
        abort(404)
    return render_template("detail.html", task=decorate(row),
                           statuses=database.STATUSES)


@bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit(task_id: int):
    """编辑任务（FR-03）。"""
    row = repo.get_task(task_id)
    if row is None:
        abort(404)

    form = _form_from_request() if request.method == "POST" else dict(row)
    errors = {}

    if request.method == "POST":
        cleaned, errors = validate_task(request.form)
        if cleaned:
            repo.update_task(task_id, cleaned)
            flash("任务已更新", "success")
            return redirect(url_for("tasks.detail", task_id=task_id))
    return render_template(
        "form.html",
        mode="edit",
        task=row,
        form=form,
        errors=errors,
        statuses=database.STATUSES,
        priorities=database.PRIORITIES,
        max_name=100, max_course=60, max_desc=1000,
    ), (400 if errors else 200)


@bp.route("/tasks/<int:task_id>/status", methods=["POST"])
def change_status(task_id: int):
    """快速切换状态（FR-05）。"""
    if repo.get_task(task_id) is None:
        abort(404)
    status = request.form.get("status", "")
    if status not in database.STATUSES:
        flash("非法的状态值", "error")
        return redirect(url_for("tasks.detail", task_id=task_id))
    repo.set_status(task_id, status)
    flash(f"状态已更新为「{status}」", "success")
    return redirect(request.form.get("next") or url_for("tasks.detail", task_id=task_id))


@bp.route("/tasks/<int:task_id>/delete", methods=["GET", "POST"])
def delete(task_id: int):
    """删除任务：先确认再删除（FR-04）。"""
    row = repo.get_task(task_id)
    if row is None:
        abort(404)

    if request.method == "POST":
        repo.delete_task(task_id)
        flash("任务已删除", "success")
        return redirect(url_for("tasks.index"))

    # GET：展示确认页，不产生任何数据变更
    return render_template("confirm_delete.html", task=decorate(row))