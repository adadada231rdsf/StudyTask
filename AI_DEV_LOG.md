# AI 开发日志（AI_DEV_LOG.md）

> 记录方式说明：本项目在 AI 辅助下完成。每一条记录包含 **任务描述 → AI 输出 → 学生判断 → 结果**。
> 「学生判断」字段由本人在核对后填写：采纳、修改后采纳，或拒绝并说明理由。

---

## 一、任务拆分

| 编号 | 任务 | 对应需求 | 完成方 |
| --- | --- | --- | --- |
| A1 | 读实验指导书，梳理 FR-01~FR-10 与数据约束 | — | AI + 学生确认 |
| A2 | 设计分层结构（views / repository / validation / db） | FR-01~FR-10 | AI |
| A3 | 建表 SQL 与数据访问层 | FR-01, FR-06, FR-09 | AI |
| A4 | 校验层：长度、必填、日期格式、枚举 | FR-10 | AI |
| A5 | 派生逻辑：逾期、即将到期、统计 | FR-07, FR-08 | AI |
| A6 | 路由与模板页面 | FR-01~FR-05 | AI |
| A7 | 手写样式，适配本地使用 | — | AI |
| A8 | 编写 pytest 用例覆盖 T1~T10 | 测试与质量 | AI |
| A9 | 运行测试、修 bug | — | AI + 学生验证 |
| A10 | 起草 README、验收表、本日志 | 文档 | AI |
| A11 | Git 提交与仓库管理 | — | 学生 |
| A12 | 演示 PPT、答辩、实验报告的最终润色 | 演示与答辩 | 学生 |

---

## 二、问题记录

### 问题 1：详情页「状态下拉框」渲染为空

**现象**
详情页截图显示，状态切换的下拉框里一片空白，没有任何选项。

**定位过程**
1. 一开始怀疑是 CSS 把 `select` 压扁了（`.inline` 用了 `flex`，`select` 会被压缩）。
2. 于是加了 `flex: 0 0 auto; min-width: 92px`，重新截图 —— **框变宽了，里面依然是空的**，说明不是样式问题。
3. 用 `document.querySelector('select')` 读到 `options.length === 0`，确认是 **选项根本没渲染出来**。
4. 回到模板：`templates/detail.html` 的循环写的是 `{% for s in statuses %}`，但在 `project/views.py` 的 `detail()` 里调用 `render_template("detail.html", task=...)` 时 **没有传 `statuses`**。其他页面（index/create/edit）都显式传了，只有详情页漏了。
5. 为什么没报错：Jinja2 对未定义的变量默认渲染为空值，`for` 循环直接不执行，所以既不报错也不显示 —— 属于「静默失败」。

**修复**
```python
# project/views.py
return render_template("detail.html", task=decorate(row),
                       statuses=database.STATUSES)
```

**补充**
在 `tests/test_create_validation.py` 里补了一条回归用例 `test_t5_detail_status_options_rendered`，断言详情页 HTML 里三种状态都存在、且当前状态被选中。这样以后谁再漏传变量，测试会直接失败。

**学生判断**
（填写：是否认可该修复、有没有更好的做法，例如把 `statuses` 放进 `context_processor` 全局注入，避免每个页面都手动传。）

---

### 问题 2：列表页新增任务后，统计数字不变

**现象**
（模拟场景）先打开首页，再另开标签页新建一条任务，回到首页时“任务总数”还是旧数字。

**分析**
统计 `stats` 在 `index()` 里由 `repo.all_tasks()` 现算，本身没问题；问题出在浏览器用了局部缓存/后退页面，没有重新请求服务端。
本项目没有做前后端分离，也没有 AJAX 局部刷新，因此**页面上的数字永远是“这次请求时刻”的快照**。

**修复思路**
不引入前端框架的前提下，采用「提交后重定向」（POST-Redirect-GET）保证每次回到首页都是一次新的 GET：

- 新建 → 302 到详情页
- 删除 → 302 回首页
- 改状态 → 302 回来源页

已全部实现，验证方式：`pytest` 中 `follow_redirects=False` 断言状态码为 302。

**学生判断**
（填写：是否接受“不做前端自动刷新”这一取舍；如果不接受，说明你打算怎么加。）

---

### 问题 3：测试运行时出现 `PytestCacheWarning: could not create cache path`

**现象**
第一次跑 `python -m pytest` 最后多出一段警告：
```
PytestCacheWarning: could not create cache path ...\.pytest_cache\v\cache\nodeids: [WinError 5] 拒绝访问
```

**分析**
pytest 想把缓存写到 `.pytest_cache`，但当前目录落在桌面上（受系统/安全软件保护），创建子目录被拒绝。**不影响测试结果**，39 条全部通过，只是多了噪音。

**修复**
在 `pyproject.toml` 里关掉缓存插件：
```toml
[tool.pytest.ini_options]
addopts = "-v --tb=short -p no:cacheprovider"
```
重新运行，警告消失。

**学生判断**
（填写：是否同意关闭缓存；关闭后 pytest 不会再记录“上次失败用例”信息，你能否接受。）

---

### 问题 4：日期 `2026-02-30` 这类“格式对但日期不存在”的输入

**现象**
只做正则 `^\d{4}-\d{2}-\d{2}$` 校验时，`2026-02-30` 会被放行，存进数据库后排序、逾期判断都会出错。

**分析**
格式合法 ≠ 日期真实存在。

**修复**
用 `datetime.strptime(value, "%Y-%m-%d")` 解析，解析失败一律视为非法，报错文案统一为“截止日期格式应为 YYYY-MM-DD，且必须是真实存在的日期”。用例 `test_t4_invalid_date_format` 覆盖 `2026-13-01`、`2026-02-30`、`abc`、`20261201` 等输入。

**学生判断**
（填写：是否认可“一律要求 YYYY-MM-DD”这一强制格式；是否考虑过放宽成 `2026/12/1`。）

---

## 三、AI 使用情况小结（供实验报告引用）

- AI 承担：需求梳理、分层设计、代码编写、测试编写、文档起草。
- 学生承担：环境搭建与运行验证、Git 提交、验收表逐条核对、演示 PPT、答辩讲解，以及本日志「学生判断」列。
- AI 输出并非全部照单全收：问题 1 的定位过程里我一度把原因归到 CSS，是截图复现 + 读 `options.length` 才纠正到模板变量上，这类「先错后对」的过程保留在上面的记录里。