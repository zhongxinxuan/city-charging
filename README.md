# 城市充电桩信息查询系统

> "Agent 创意初体验"参赛作品 · 用智能体辅助完成的城市充电数据可视化与查询平台

## 作品简介

日常生活中找充电桩经常要绕路、不知道哪个站点有空位、不知道哪家运营商更划算。本作品把散乱的城市充电数据做成一个一目了然的网页：首页总览仪表盘展示站点数、记录数、运营商分布和多维度统计图表；支持按城市、运营商筛选充电站并查看详情；支持按支付方式等条件检索充电记录。前端使用 Vue 3 + Element Plus + ECharts，后端使用 FastAPI + SQLite，前后端代码均由智能体辅助生成。

## 功能模块

- **总览仪表盘**：汇总卡片 + 站点分布柱状图、运营商占比环形图等多组图表
- **数据总览**：站点数量分布、平均充电费用、平均电量等多维度统计
- **充电站查询**：按城市 / 运营商 / 关键字筛选，支持查看站点详情（地址、充电枪规格、营业时间、停车位等）
- **充电记录查询**：按城市 / 支付方式 / 关键字筛选，支持查看记录详情（用户、车辆、SOC、费用等）

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Element Plus + ECharts + Pinia + Vue Router |
| 后端 | Python FastAPI + Uvicorn |
| 数据库 | SQLite（由 `public/data_json/*.json` 自动导入） |

## 本地运行

### 1. 安装依赖

```powershell
# 前端依赖
npm install

# 后端依赖（建议先建虚拟环境）
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 初始化数据库

```powershell
python -m backend.init_db
```

会在 `backend/charging.db` 生成 SQLite 数据库。

### 3. 启动后端（端口 8000）

```powershell
uvicorn backend.main:app --reload --port 8000
```

### 4. 启动前端（端口 5173，已配置 proxy 转发 /api）

```powershell
npm run dev
```

浏览器打开 <http://localhost:5173>。

## 线上部署（Render 免费层）

本项目已配置 `render.yaml`，可一键部署：

1. 把代码推到 GitHub 仓库（`dist/` 已构建好并提交，无需在服务器装 Node）。
2. 登录 <https://render.com>，选 **New + → Blueprint**，选中该仓库。
3. Render 会自动读取 `render.yaml`，点 **Apply**。
4. 等待 3–5 分钟，拿到 `https://<你的服务名>.onrender.com` 链接。

> 免费层注意：15 分钟无访问会休眠，首次打开需等待 30–50 秒，请在邮件里注明。

### 手动部署其他平台

只要满足：
- 环境有 Python 3.11+；
- 先执行 `pip install -r requirements.txt && python -m backend.init_db`；
- 再执行 `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`；
- `dist/` 目录与 `backend/` 同级（FastAPI 会自动托管它）。

## 目录结构

```
├── backend/
│   ├── main.py          # FastAPI 接口 + 静态文件托管
│   ├── database.py      # SQLite 连接
│   ├── init_db.py       # 从 JSON 建库导数据
│   └── charging.db      # 运行后生成，不进 git
├── public/data_json/    # 原始数据（6 个 JSON）
├── src/                 # Vue 前端源码
├── dist/                # 前端构建产物（提交到 git，供线上托管）
├── requirements.txt
└── render.yaml
```
