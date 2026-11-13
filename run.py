"""
StudyTask 启动入口。

用法：
    python run.py            # 开发模式，访问 http://127.0.0.1:5000
    python run.py --port 8000
"""
import argparse

from project import create_app

app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StudyTask 个人学习任务管理系统")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true", help="开启调试与热重载")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)