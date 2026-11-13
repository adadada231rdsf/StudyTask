"""
T6–T9：编辑、删除确认、状态切换、逾期与即将到期提醒。
"""
from datetime import date, timedelta


def _valid(**over):
    data = {
        "name": "实验一报告",
        "course": "软件工程",
        "description": "",
        "due_date": "2026-12-01",
        "priority": "中",
        "status": "待完成",
    }
    data.update(over)
    return data


def _d(offset: int) -> str:
    return (date.today() + timedelta(days=offset)).strftime("%Y-%m-%d")


# ---------- T6：编辑 ----------
def test_t6_edit_updates_fields(client, helpers):
    tid = helpers.insert(name="旧名称", priority="低")
    resp = client.post(f"/tasks/{tid}/edit", data=_valid(name="新名称", priority="高",
                                                         description="改了描述"))
    assert resp.status_code == 302
    row = helpers.rows()[0]
    assert row["name"] == "新名称"
    assert row["priority"] == "高"
    assert row["description"] == "改了描述"


def test_t6_edit_form_prefilled(client, helpers):
    tid = helpers.insert(name="预填检查")
    body = client.get(f"/tasks/{tid}/edit").get_data(as_text=True)
    assert 'value="预填检查"' in body


def test_t6_edit_invalid_keeps_old_data(client, helpers):
    tid = helpers.insert(name="保持原样")
    resp = client.post(f"/tasks/{tid}/edit", data=_valid(name=""))
    assert resp.status_code == 400
    assert "任务名称不能为空" in resp.get_data(as_text=True)
    assert helpers.rows()[0]["name"] == "保持原样", "校验失败不应改动数据库"


def test_t6_edit_404(client):
    assert client.get("/tasks/9999/edit").status_code == 404


# ---------- T7：删除需要确认 ----------
def test_t7_delete_get_shows_confirm_without_deleting(client, helpers):
    tid = helpers.insert(name="待删除任务")
    resp = client.get(f"/tasks/{tid}/delete")
    assert resp.status_code == 200
    assert "确认删除" in resp.get_data(as_text=True)
    assert len(helpers.rows()) == 1, "GET 确认页不能删除数据"


def test_t7_delete_post_removes(client, helpers):
    tid = helpers.insert(name="待删除任务")
    resp = client.post(f"/tasks/{tid}/delete")
    assert resp.status_code == 302
    assert helpers.rows() == []
    assert client.get(f"/tasks/{tid}").status_code == 404


# ---------- T8：状态切换 ----------
def test_t8_status_cycle(client, helpers):
    tid = helpers.insert(status="待完成")
    for target in ["进行中", "已完成", "待完成"]:
        resp = client.post(f"/tasks/{tid}/status", data={"status": target},
                           follow_redirects=False)
        assert resp.status_code == 302
        assert helpers.rows()[0]["status"] == target


def test_t8_invalid_status_rejected(client, helpers):
    tid = helpers.insert(status="待完成")
    resp = client.post(f"/tasks/{tid}/status", data={"status": "已归档"},
                       follow_redirects=True)
    assert helpers.rows()[0]["status"] == "待完成", "非法状态不应写入"
    assert "非法的状态值" in resp.get_data(as_text=True)


def test_t8_status_404(client):
    assert client.post("/tasks/9999/status", data={"status": "已完成"}).status_code == 404


# ---------- T9：逾期 / 即将到期 ----------
def test_t9_overdue_badge(client, helpers):
    tid = helpers.insert(name="逾期任务", due_date=_d(-1), status="待完成")
    body = client.get("/").get_data(as_text=True)
    assert "已逾期" in body
    assert client.get(f"/tasks/{tid}").get_data(as_text=True).count("已逾期") >= 1


def test_t9_due_soon_badge_boundaries(client, helpers):
    """今天到期、+3 天到期 → 即将到期；+4 天 → 无提醒。"""
    helpers.insert(name="今天到期", due_date=_d(0))
    helpers.insert(name="三天后", due_date=_d(3))
    helpers.insert(name="四天后", due_date=_d(4))

    from project import repository as repo
    from project.validation import decorate

    with client.application.app_context():
        rows = {r["name"]: decorate(r) for r in repo.all_tasks()}

    assert rows["今天到期"]["due_state"] == "due_soon"
    assert rows["三天后"]["due_state"] == "due_soon"
    assert rows["四天后"]["due_state"] == ""


def test_t9_done_task_has_no_reminder(client, helpers):
    helpers.insert(name="已完成任务", due_date=_d(-5), status="已完成")
    from project import repository as repo
    from project.validation import decorate

    with client.application.app_context():
        row = [r for r in repo.all_tasks()][0]
        item = decorate(row)
    assert item["due_label"] == ""


def test_t9_doing_task_still_reminded(client, helpers):
    """“进行中”的任务未完成，仍应提醒。"""
    helpers.insert(name="进行中逾期", due_date=_d(-2), status="进行中")
    body = client.get("/").get_data(as_text=True)
    assert "已逾期" in body