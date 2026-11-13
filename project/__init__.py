"""
应用工厂。用工厂函数而不是全局 app，便于测试时注入临时数据库。
"""
import os

from flask import Flask

from . import db as database


def create_app(test_config: dict = None) -> Flask:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        instance_relative_config=False,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("STUDYTASK_SECRET", "study-task-dev-key"),
        DATABASE=os.path.join(base_dir, "instance", "studytask.sqlite"),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        JSON_AS_ASCII=False,
    )
    if test_config:
        app.config.update(test_config)

    database.init_app(app)

    from .views import bp as tasks_bp
    app.register_blueprint(tasks_bp)

    # ---------- 中文错误页：避免错误输入导致白屏 ----------
    @app.errorhandler(400)
    def bad_request(err):
        return render_template_error(app, 400, "请求参数有误，请检查后重试")

    @app.errorhandler(404)
    def not_found(err):
        return render_template_error(app, 404, "页面或任务不存在，可能已被删除")

    @app.errorhandler(413)
    def too_large(err):
        return render_template_error(app, 413, "提交的内容过大")

    @app.errorhandler(500)
    def server_error(err):
        return render_template_error(app, 500, "服务器内部错误，请重试")

    # ---------- 模板全局 ----------
    @app.context_processor
    def inject_globals():
        from . import db as d
        return {
            "STATUSES": d.STATUSES,
            "PRIORITIES": d.PRIORITIES,
            "APP_NAME": "StudyTask 学习任务管理",
        }

    return app


def render_template_error(app, code, message):
    from flask import render_template
    return render_template("error.html", code=code, message=message), code