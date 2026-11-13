"""
T10 + FR-06/FR-08：组合筛选、统计信息、列表排序与空状态。
"""
from datetime import date, timedelta


def _d(offset: int) -> str:
    return (date.today() + timedelta(days=offset)).strftime("%Y-%m-%d")


def _seed(helpers):
    helpers.insert(name="软工报告", course="软件工程", priority="高", status="待完成",
                   due_date=_d(5))
    helpers.insert(name="软工演示", course="软件工程", priority="低", status="已完成",
                   due_date=_d(2))
    helpers.insert(name="数据库习题", course="数据库", priority="中", status="进行中",
                   due_date=_d(1))
    helpers.insert(name="Web 大作业", course="Web 开发", priority="高", status="待完成",
                   due_date=_d(9), description="含前后端与部署")


# ---------- T10：组合筛选 ----------
def test_t10_filter_by_course(client, helpers):
    _seed(helpers)
    body = client.get("/?course=软件工程").get_data(as_text=True)
    assert "软工报告" in body and "软工演示" in body
    assert "数据库习题" not in body
    assert "Web 大作业" not in body


def test_t10_filter_by_status(client, helpers):
    _seed(helpers)
    body = client.get("/?status=已完成").get_data(as_text=True)
    assert "软工演示" in body
    assert "软工报告" not in body


def test_t10_filter_by_priority(client, helpers):
    _seed(helpers)
    body = client.get("/?priority=高").get_data(as_text=True)
    assert "软工报告" in body and "Web 大作业" in body
    assert "数据库习题" not in body


def test_t10_combined_filters(client, helpers):
    _seed(helpers)
    body = client.get("/?course=软件工程&priority=高&status=待完成").get_data(as_text=True)
    assert "软工报告" in body
    assert "软工演示" not in body
    assert "数据库习题" not in body


def test_t10_keyword_matches_name_and_description(client, helpers):
    _seed(helpers)
    assert "软工报告" in client.get("/?keyword=软工").get_data(as_text=True)
    assert "Web 大作业" in client.get("/?keyword=部署").get_data(as_text=True)
    assert "数据库习题" not in client.get("/?keyword=部署").get_data(as_text=True)


def test_t10_empty_result_message(client, helpers):
    _seed(helpers)
    body = client.get("/?course=不存在的课").get_data(as_text=True)
    assert "当前筛选条件下没有任务" in body


def test_t10_no_tasks_at_all(client):
    body = client.get("/").get_data(as_text=True)
    assert "还没有任务" in body


def test_t10_sql_injection_is_harmless(client, helpers):
    _seed(helpers)
    resp = client.get("/?keyword=%27%20OR%201%3D1%3B--")
    assert resp.status_code == 200
    assert "当前筛选条件下没有任务" in resp.get_data(as_text=True)
    assert len(helpers.rows()) == 4, "注入尝试不应影响数据"


# ---------- FR-08：统计 ----------
def test_fr08_stats_counts_and_rate(client, helpers):
    _seed(helpers)
    body = client.get("/").get_data(as_text=True)
    # 4 条任务，1 条已完成 → 25.0%
    assert 'id="task-count"' in body
    assert "25.0%" in body


def test_fr08_stats_zero_when_empty(client):
    body = client.get("/").get_data(as_text=True)
    assert "0%" in body
    assert "0.0%" not in body


def test_fr08_stats_ignore_filters(client, helpers):
    """统计是全量口径，不随筛选变化。"""
    _seed(helpers)
    with_high = client.get("/?priority=高").get_data(as_text=True)
    assert "25.0%" in with_high


# ---------- 排序 ----------
def test_sorting_done_sinks_and_due_asc(client, helpers):
    helpers.insert(name="完成任务", due_date=_d(1), status="已完成")
    helpers.insert(name="未完成早", due_date=_d(2), status="待完成")
    helpers.insert(name="未完成晚", due_date=_d(8), status="待完成")

    from project import repository as repo
    with client.application.app_context():
        names = [r["name"] for r in repo.list_tasks()]
    assert names.index("完成任务") == 2
    assert names.index("未完成早") < names.index("未完成晚")


# ---------- 错误页 ----------
def test_unknown_route_404_page(client):
    resp = client.get("/no-such-page")
    assert resp.status_code == 404
    assert "返回任务列表" in resp.get_data(as_text=True)