# A股每日复盘 Dashboard

一个面向个人交易者的本地可运行复盘面板。后端 FastAPI + SQLite 缓存，前端纯 HTML/JS（轻量图表）。默认使用无需 token 的数据源，离线时会回退示例数据保证可用。

## 目录结构
- backend/: FastAPI 服务、数据提供与缓存
- frontend/: 静态前端（无需构建，FastAPI 直接托管）
- requirements.txt: 后端依赖
- setup.bat / refresh.bat / start_api.bat / open_frontend.bat: Windows 一键脚本

## 1-2-3 跑通（Windows 10/11）
> 前置：已安装 **Python 3.9+**，系统可直接运行 `python`。无需安装 Node / 前端构建工具。

1. **安装依赖与初始化数据库**（仅首次）
   双击或在命令行运行（脚本已自动停留显示错误，防止闪退）：
   ```bat
   setup.bat
   ```
   这一步会创建 `.venv` 虚拟环境、安装依赖并通过 `backend/init_db.py` 初始化 `backend/app/data/cache.db`（避免不同编码下的命令行解析问题）。

2. **刷新数据**（可随时重复）
   ```bat
   refresh.bat auto
   ```
   - 默认 `auto`：自动选择最近交易日（工作日缺省用回退逻辑）。
   - 指定日期：`refresh.bat 20251230`

3. **启动后端 + 打开前端**
   ```bat
   start_api.bat
   open_frontend.bat
   ```
   - 打开浏览器访问 http://127.0.0.1:8000
   - 健康检查：`http://127.0.0.1:8000/api/health` 返回 `{ "status": "ok" }` 即正常

> 若命令提示 `python` 未找到，可在“应用和功能”中安装 Python，或使用 `py -3` 并修改脚本中的 `python` 为 `py -3`。

> 如果双击脚本后瞬间关闭：请在资源管理器地址栏输入 `cmd` 打开命令行，再执行 `setup.bat` / `refresh.bat auto` / `start_api.bat`，窗口会停留并显示具体错误。

## 功能概览
- 涨停全览：表格支持搜索、连板/龙虎榜/游资筛选与排序。
- KPI：涨停/连板数量、最高板、炸板率、晋级/断板率。
- 主线题材：按涨停数+连板+封单/成交加权排行 TOP10。
- 单股详情：封板信息、龙虎榜买卖金额、K 线（lightweight-charts），资金量柱状。
- 热键：点击表格行自动加载右侧详情。

## 数据与兼容性
- 默认数据源：东方财富涨停池/龙虎榜（附网络重试）。若网络不可用自动回退示例数据，保证页面可用。
- 支持切换/扩展：`backend/app/providers` 下可新增 Provider 并在 `refresh_service.py` 中替换。
- SQLite 缓存：`backend/app/data/cache.db` 自动创建，表结构见 `backend/app/services/cache.py`。
- 游资识别：`backend/app/hot_money_keywords.json` 可自定义关键词。

## 手动调用 API
- `GET /api/health`
- `GET /api/limitups?date=YYYYMMDD|auto`
- `GET /api/stock/{ts_code}?date=YYYYMMDD|auto`
- `GET /api/kline/{ts_code}?start=auto|YYYYMMDD&end=auto|YYYYMMDD`
- `GET /api/lhb?date=YYYYMMDD|auto`

## 自测
- `setup.bat`：完成 venv 和依赖安装
- `refresh.bat auto`：成功写入缓存并输出刷新完成日志
- `start_api.bat` 后访问 `http://127.0.0.1:8000/api/health` 返回 ok
- 前端首页显示示例涨停列表，点击行可加载 K 线

## 说明
- 所有网络请求带超时与重试，失败自动降级为本地示例数据，避免崩溃。
- K 线若数据源不可用将使用模拟数据填充，界面依旧可交互。
- Windows 路径/编码均为 UTF-8，脚本使用相对路径方便放置任意文件夹。
