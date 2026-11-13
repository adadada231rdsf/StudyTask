"""
T1–T5：新建任务、必填校验、长度与日期格式、详情展示。
对应 SRS 附录 A 的验收用例。
"""
from datetime import date, timedelta


def _valid(**over):
    data = {
        "name": "实验一报告",
        "course": "软件工程",
        "description": "完成 StudyTask 并写 4 页报告",
        "due_date": "2026-12-01",
        "priority": "高",
        "status": "待完成",
    }
    data.update(over)
    return data


# ---------- T1：正常新建 ----------
def test_t1_create_task_success(client, helpers):
    resp = client.post("/tasks/new", data=_valid(), follow_redirects=False)
    assert resp.status_code == 302, "创建成功后应重定向到详情页"
    assert "/tasks/" in resp.headers["Location"]

    rows = helpers.rows()
    assert len(rows) == 1
    assert rows[0]["name"] == "实验一报告"
    assert rows[0]["priority"] == "高"
    assert rows[0]["status"] == "待完成"
    assert rows[0]["created_at"] == rows[0]["updated_at"]


# ---------- T2：必填项为空 ----------
def test_t2_required_fields_empty(client, helpers):
    resp = client.post("/tasks/new", data=_valid(name="", course="", due_date=""))
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "任务名称不能为空" in body
    assert "所属课程不能为空" in body
    assert "截止日期不能为空" in body
    assert helpers.rows() == [], "校验失败不能写库"


def test_t2_blank_spaces_treated_as_empty(client):
    resp = client.post("/tasks/new", data=_valid(name="   "))
    assert resp.status_code == 400
    assert "任务名称不能为空" in resp.get_data(as_text=True)


# ---------- T3：长度边界 ----------
def test_t3_name_length_boundary(client, helpers):
    ok = client.post("/tasks/new", data=_valid(name="a" * 100))
    assert ok.status_code == 302

    bad = client.post("/tasks/new", data=_valid(name="a" * 101))
    assert bad.status_code == 400
    assert "任务名称不能超过 100 个字" in bad.get_data(as_text=True)
    assert len(helpers.rows()) == 1, "超长名称不应写入"


def test_t3_course_length_boundary(client):
    assert client.post("/tasks/new", data=_valid(course="c" * 60)).status_code == 302
    bad = client.post("/tasks/new", data=_valid(course="c" * 61))
    assert bad.status_code == 400
    assert "所属课程不能超过 60 个字" in bad.get_data(as_text=True)


def test_t3_description_length_boundary(client):
    assert client.post("/tasks/new", data=_valid(description="d" * 1000)).status_code == 302
    bad = client.post("/tasks/new", data=_valid(description="d" * 1001))
    assert bad.status_code == 400
    assert "任务描述不能超过 1000 个字" in bad.get_data(as_text=True)


# ---------- T4：日期格式 ----------
def test_t4_invalid_date_format(client):
    for value in ["2026/12/01", "2026-13-01", "2026-02-30", "abc", "20261201"]:
        resp = client.post("/tasks/new", data=_valid(due_date=value))
        assert resp.status_code == 400, f"{value} 应被判为非法"
        assert "截止日期格式应为 YYYY-MM-DD" in resp.get_data(as_text=True)


def test_t4_valid_date_accepted(client):
    resp = client.post("/tasks/new", data=_valid(due_date="2026-02-28"))
    assert resp.status_code == 302


# ---------- T5：详情页展示 ----------
def test_t5_detail_shows_all_fields(client, helpers):
    tid = helpers.insert(name="数据库作业", course="数据库",
                         description="做完第 3 章习题", due_date="2026-11-30", priority="中")
    resp = client.get(f"/tasks/{tid}")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    for text in ["数据库作业", "数据库", "做完第 3 章习题", "2026-11-30", "中"]:
        assert text in body


def test_t5_detail_404(client):
    resp = client.get("/tasks/9999")
    assert resp.status_code == 404
    assert "页面或任务不存在" in resp.get_data(as_text=True)


def test_t5_detail_status_options_rendered(client, helpers):
    """回归：详情页状态下拉曾因模板变量未注入而渲染为空。"""
    tid = helpers.insert(status="进行中")
    body = client.get(f"/tasks/{tid}").get_data(as_text=True)
    for s in ["待完成", "进行中", "已完成"]:
        assert f'value="{s}"' in body
    assert 'value="进行中" selected' in body


def test_t5_detail_escapes_html(client, helpers):
    tid = helpers.insert(name="<script>alert(1)</script>")
    body = client.get(f"/tasks/{tid}").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;" in body


# ---------- 默认值：优先级中、状态待完成 ----------
def test_defaults_when_fields_missing(client, helpers):
    data = _valid()
    data.pop("priority")
    data.pop("status")
    resp = client.post("/tasks/new", data=data)
    assert resp.status_code == 302
    row = helpers.rows()[0]
    assert row["priority"] == "中"
    assert row["status"] == "待完成"