# StudyTask 个人学习任务管理系统

软件工程实验一交付物。一个单用户、本地运行的 Web 系统，用于记录个人学习任务、跟踪状态与截止日期。

- 技术栈：Python 3.9+ / Flask 2.3 / SQLite（标准库 `sqlite3`）/ 原生 HTML + CSS
- 覆盖需求：SRS 附录 A 的 FR-01 ~ FR-10、验收用例 T1 ~ T10
- 测试：39 条 pytest 用例，全部通过

---

## 1. 从零开始运行

> 下面的命令在 Windows PowerShell 下验证通过。命令里出现的路径换成你自己的仓库路径即可。

### 第一步：进入项目目录

```powershell
cd C:\Users\你的用户名\Desktop\StudyTask
```

### 第二步：创建并激活虚拟环境（推荐，可跳过）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果提示“无法加载文件……因为在此系统上禁止运行脚本”，先在**当前窗口**执行一次：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后在同样的窗口里重新执行激活命令。

### 第三步：安装依赖

```powershell
pip install -r requirements.txt
```

国内网络慢可以加镜像：

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第四步：启动

```powershell
python run.py
```

看到下面的输出说明成功：

```
 * Running on http://127.0.0.1:5000
```

浏览器打开 <http://127.0.0.1:5000> 即可使用。

- 首次启动会自动在 `instance/studytask.sqlite` 建库建表，**不需要**手动执行 SQL。
- 端口被占用时：`python run.py --port 5001`
- 需要热重载（改代码自动重启）：`python run.py --debug`

### 第五步（可选）：写入演示数据

```powershell
python seed_demo.py --reset
```

会清空任务表并写入 8 条覆盖“逾期 / 即将到期 / 进行中 / 已完成”等各种状态的示例任务，方便演示和截图。

### 第六步：运行测试

```powershell
python -m pytest
```

预期输出结尾为 `39 passed`。测试使用临时数据库，**不会**动到你的真实数据。

---

## 2. 功能清单与需求对照

| 需求 | 说明 | 实现位置 |
| --- | --- | --- |
| FR-01 新建任务 | 表单录入，服务端校验后入库 | `project/views.py: create()`、`project/validation.py: validate_task()` |
| FR-02 任务列表与详情 | 列表页展示主要字段，详情页展示全部字段 | `templates/index.html`、`templates/detail.html` |
| FR-03 编辑任务 | 复用表单，校验失败保留用户输入 | `project/views.py: edit()` |
| FR-04 删除任务 | GET 只展示确认页，POST 才真正删除 | `project/views.py: delete()`、`templates/confirm_delete.html` |
| FR-05 状态流转 | 待完成 / 进行中 / 已完成，列表页可直接切换 | `project/repository.py: set_status()` |
| FR-06 组合筛选 | 课程 + 状态 + 优先级 + 关键字，可任意组合 | `project/repository.py: list_tasks()` |
| FR-07 到期提醒 | 逾期（红）/ 即将到期（橙，3 天内）/ 已完成不提醒 | `project/validation.py: decorate()` |
| FR-08 统计信息 | 任务总数、已完成数、完成率（总数 0 时为 0%） | `project/validation.py: summary()` |
| FR-09 排序 | 已完成沉底 → 截止日期升序 → 优先级高在前 | `project/repository.py: list_tasks()` 的 ORDER BY |
| FR-10 数据校验 | 长度、必填、日期格式、枚举值全部服务端校验 | `project/validation.py`；数据库层还有 CHECK 约束兜底 |

数据约束（SRS 附录 A.2）：

| 字段 | 约束 |
| --- | --- |
| 任务名称 | 必填，1—100 字 |
| 所属课程 | 必填，1—60 字 |
| 任务描述 | 可空，≤ 1000 字 |
| 截止日期 | 必填，`YYYY-MM-DD`，必须是真实存在的日期 |
| 优先级 | 高 / 中 / 低，默认 中 |
| 状态 | 待完成 / 进行中 / 已完成，默认 待完成 |

---

## 3. 验收用例结果

| 用例 | 内容 | 结果 |
| --- | --- | --- |
| T1 | 填写完整合法信息新建任务，成功并跳转详情 | 通过 |
| T2 | 名称/课程/截止日期留空提交，提示错误且不写库 | 通过 |
| T3 | 名称 100 / 101 字、课程 60 / 61 字、描述 1000 / 1001 字边界 | 通过 |
| T4 | 日期 `2026/12/01`、`2026-13-01`、`2026-02-30` 等非法格式被拒 | 通过 |
| T5 | 详情页完整展示全部字段，不存在的 ID 返回 404 | 通过 |
| T6 | 编辑任务字段并保存，列表与详情同步更新 | 通过 |
| T7 | 删除前出现确认页；确认后记录消失 | 通过 |
| T8 | 状态可循环切换为三种值，非法状态被拒绝 | 通过 |
| T9 | 逾期任务显示“已逾期”；今天至 +3 天显示“即将到期”；已完成不提醒 | 通过 |
| T10 | 课程 / 状态 / 优先级 / 关键字单独与组合筛选结果正确 | 通过 |

测试文件：

- `tests/test_create_validation.py` —— T1 ~ T5、默认值、XSS 转义
- `tests/test_edit_delete_status.py` —— T6 ~ T9
- `tests/test_filter_stats.py` —— T10、FR-08 统计、排序、错误页

---

## 4. 目录结构

```
StudyTask/
├── run.py                 # 启动入口
├── seed_demo.py           # 演示数据脚本
├── requirements.txt
├── pyproject.toml         # pytest 配置
├── .gitignore
├── project/               # 应用代码
│   ├── __init__.py        # 应用工厂、错误页、模板全局变量
│   ├── db.py              # 连接管理、建表 SQL、业务常量
│   ├── validation.py      # 校验与派生字段（逾期/统计）
│   ├── repository.py      # 全部 SQL
│   └── views.py           # 路由
├── templates/             # Jinja2 模板
├── static/style.css       # 手写样式
├── tests/                 # pytest 用例
├── docs/                  # 界面截图、验收记录
└── instance/              # 运行时自动生成，已被 .gitignore 忽略
```

---

## 5. 已知限制

- 单用户系统，没有登录与权限，不要部署到公网。
- 开发服务器（`python run.py`）只适合本地演示；按实验指导书 A.5，本实验不实现云部署。
- 数据库为单个 SQLite 文件，备份即复制 `instance/studytask.sqlite`。