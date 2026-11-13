"""
开发辅助脚本：生成一批演示数据，方便截图和演示。

用法：
    python seed_demo.py          # 追加 8 条示例任务
    python seed_demo.py --reset  # 先清空任务表再写入
"""
import argparse
from datetime import date, timedelta

from project import create_app
from project import db as database
from project import repository as repo


def _d(offset: int) -> str:
    return (date.today() + timedelta(days=offset)).strftime("%Y-%m-%d")


DEMO = [
    ("软件工程实验一报告", "软件工程", "完成 StudyTask 系统，写 4 页实验报告并准备演示", _d(4), "高", "进行中"),
    ("数据库第三章习题", "数据库", "1—8 题，注意范式分解", _d(-2), "中", "待完成"),
    ("Web 课程大作业", "Web应用程序开发", "前后端分离，完成后端接口联调", _d(12), "高", "进行中"),
    ("英语四级单词 100 个", "高级英语", "每天 30 分钟", _d(1), "低", "待完成"),
    ("大学物理实验报告", "大学物理", "单摆实验数据处理", _d(-6), "中", "已完成"),
    ("软工小组会议纪要", "软件工程", "整理 11 月 13 日会议结论", _d(-1), "低", "已完成"),
    ("数据结构课程设计选题", "数据结构", "确定选题并提交给助教", _d(3), "高", "待完成"),
    ("软件工程实验二预习", "软件工程", "阅读指导书实验二部分", _d(20), "低", "待完成"),
]


def main():
    parser = argparse.ArgumentParser(description="写入演示数据")
    parser.add_argument("--reset", action="store_true", help="先清空任务表")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.reset:
            database.get_db().execute("DELETE FROM task")
            database.get_db().commit()
            print("已清空任务表")
        for name, course, desc, due, pri, st in DEMO:
            tid = repo.create_task({
                "name": name, "course": course, "description": desc,
                "due_date": due, "priority": pri, "status": st,
            })
            print(f"  + #{tid} {name}")
        print(f"共写入 {len(DEMO)} 条演示任务")


if __name__ == "__main__":
    main()