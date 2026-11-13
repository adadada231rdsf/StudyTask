"""
pytest 公共 fixture。

每个测试用独立的临时 SQLite 文件，互不干扰，也不会碰到开发用的真实数据。
"""
import os
import sys
import tempfile

import pytest

# 让 tests/ 目录下的用例可以直接 import project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app  # noqa: E402


@pytest.fixture()
def app():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)

    app = create_app({
        "TESTING": True,
        "DATABASE": path,
        "SECRET_KEY": "test-key",
        "WTF_CSRF_ENABLED": False,
    })
    app.config["TEST_DB_PATH"] = path

    yield app

    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def helpers(app):
    """一组直接操作数据库的便捷函数，用于准备前置数据和核对结果。"""
    from project import db as database

    def _conn():
        return database.get_db()

    class H:
        @staticmethod
        def insert(name="任务", course="软件工程", description="", due_date="2026-12-01",
                   priority="中", status="待完成"):
            from project import repository as repo
            with app.app_context():
                return repo.create_task({
                    "name": name, "course": course, "description": description,
                    "due_date": due_date, "priority": priority, "status": status,
                })

        @staticmethod
        def rows():
            from project import repository as repo
            with app.app_context():
                return [dict(r) for r in repo.all_tasks()]

    return H