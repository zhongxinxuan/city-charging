# 项目运行与构建教程

本文档说明"城市充电桩信息查询系统"的本地运行、构建部署和环境配置流程。

## 1. 系统运行流程

完整运行链路：

```text
1. 启动 PostgreSQL 数据库服务
2. 创建数据库并导入数据
3. 启动 FastAPI 后端服务
4. 启动 Vue 3 前端开发服务器
5. 浏览器访问前端页面
```

## 2. 环境要求

| 工具 | 最低版本 | 本项目测试版本 |
|---|---|---|
| Node.js | >= 20.19.0 | v24.14.0 |
| npm | >= 10 | 11.9.0 |
| Python | >= 3.10 | 3.14.3 |
| PostgreSQL | >= 14 | 18.3 |

## 3. 项目目录结构

```text
vue-carcharging/
├── backend/                 FastAPI 后端代码
│   ├── main.py              路由和接口
│   └── database.py          数据库连接配置
├── public/
│   ├── data/                CSV 原始数据（6个文件）
│   └── data_json/           JSON 转换后的数据
├── scripts/
│   ├── csv_to_json.py       CSV → JSON 转换脚本
│   └── import_json_to_db.py JSON → PostgreSQL 导入脚本
├── src/                     Vue 3 前端代码
├── docs/                    教程文档
├── .venv/                   Python 虚拟环境
├── package.json             前端依赖配置
├── vite.config.ts           Vite 构建配置
└── tsconfig.json            TypeScript 配置
```

## 4. Python 虚拟环境

项目使用 Python 虚拟环境隔离后端依赖。

### 4.1 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

激活后终端前面会出现 `(.venv)` 标识：

```text
(.venv) PS D:\城市充电桩信息查询系统\vue-carcharging>
```

### 4.2 创建虚拟环境

如果 `.venv` 目录不存在，可以创建：

```powershell
python -m venv .venv
```

### 4.3 安装依赖

```powershell
pip install fastapi uvicorn psycopg psycopg-binary
```

或从 requirements 文件安装。

## 5. 数据库配置

### 5.1 修改数据库密码

在 `backend/database.py` 中：

```python
DB_CONFIG = {
    "dbname": "car_charging_db",
    "user": "postgres",
    "password": "你的数据库密码",    ← 改成自己的密码
    "host": "localhost",
    "port": 5432,
}
```

### 5.2 创建数据库

启动 PostgreSQL 服务后：

```powershell
psql -U postgres
```

```sql
CREATE DATABASE car_charging_db;
\c car_charging_db;
CREATE SCHEMA charging_system;
```

### 5.3 创建表结构

数据库建表语句需要在 PostgreSQL 中执行。创建以下 6 张表：

```sql
-- 城市表
CREATE TABLE charging_system.cities (
    city_id INTEGER PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    longitude DECIMAL(10,6),
    latitude DECIMAL(10,6),
    area_code VARCHAR(20),
    population INTEGER,
    gdp_billion DECIMAL(10,2)
);

-- 运营商表
CREATE TABLE charging_system.operators (
    operator_id INTEGER PRIMARY KEY,
    operator_name VARCHAR(200) NOT NULL,
    company_type VARCHAR(100),
    founded_year INTEGER,
    headquarters VARCHAR(200)
);

-- 充电桩规格表
CREATE TABLE charging_system.charger_specs (
    spec_id INTEGER PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL,
    power_kw DECIMAL(8,2),
    voltage_v DECIMAL(8,2),
    current_a DECIMAL(8,2),
    connector_type VARCHAR(100),
    charge_time_min INTEGER,
    cost_per_kwh DECIMAL(6,2)
);

-- 充电站表
CREATE TABLE charging_system.stations (
    station_id INTEGER PRIMARY KEY,
    station_name VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    phone VARCHAR(50),
    longitude DECIMAL(10,6),
    latitude DECIMAL(10,6),
    city_id INTEGER REFERENCES charging_system.cities(city_id),
    operator_id INTEGER REFERENCES charging_system.operators(operator_id),
    spec_id INTEGER REFERENCES charging_system.charger_specs(spec_id),
    opening_hours VARCHAR(200),
    has_restroom BOOLEAN,
    parking_spots INTEGER
);

-- 用户表
CREATE TABLE charging_system.users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    user_type VARCHAR(50),
    vehicle_type VARCHAR(100),
    vehicle_model VARCHAR(200)
);

-- 充电记录表
CREATE TABLE charging_system.charging_records (
    record_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES charging_system.users(user_id),
    station_id INTEGER REFERENCES charging_system.stations(station_id),
    charge_start_time TIMESTAMP,
    charge_end_time TIMESTAMP,
    duration_minutes INTEGER,
    energy_kwh DECIMAL(10,2),
    cost_yuan DECIMAL(10,2),
    payment_method VARCHAR(50),
    start_soc INTEGER,
    end_soc INTEGER
);
```

建表顺序：

```text
1. cities         无外键依赖
2. operators      无外键依赖
3. charger_specs  无外键依赖
4. stations       依赖 cities、operators、charger_specs
5. users          无外键依赖
6. charging_records 依赖 users、stations
```

有外键的表必须在依赖的表创建之后创建。

## 6. 数据导入

### 6.1 第一步：CSV 转 JSON

```powershell
python scripts/csv_to_json.py
```

或者使用虚拟环境的 Python：

```powershell
.\.venv\Scripts\python.exe scripts/csv_to_json.py
```

执行过程：

```text
读取 public/data/ 下的 6 个 CSV 文件
↓
csv.DictReader 解析，CSV 表头作为 JSON 的 key
↓
跳过空行
↓
输出到 public/data_json/ 同名 JSON 文件
```

输出示例：

```text
expanded_cities.csv 8
operators_info.csv 5
charger_specifications.csv 5
expanded_stations.csv 2402
users.csv 500
charging_records.csv 1000
```

### 6.2 第二步：JSON 导入 PostgreSQL

```powershell
.\.venv\Scripts\python.exe scripts/import_json_to_db.py
```

成功输出：

```text
Database connection: car_charging_db
Imported charging_system.cities: 8 rows
Imported charging_system.operators: 5 rows
Imported charging_system.charger_specs: 5 rows
Imported charging_system.stations: 2402 rows
Imported charging_system.users: 500 rows
Imported charging_system.charging_records: 1000 rows
```

导入顺序：

```text
1. cities          基础数据
2. operators       基础数据
3. charger_specs   基础数据
4. stations        依赖前3张表
5. users           独立
6. charging_records 依赖 users 和 stations
```

外键依赖决定了导入顺序不能乱。

### 6.3 验证数据

在 psql 终端中执行：

```sql
SELECT COUNT(*) FROM charging_system.cities;              -- 8
SELECT COUNT(*) FROM charging_system.operators;           -- 5
SELECT COUNT(*) FROM charging_system.charger_specs;       -- 5
SELECT COUNT(*) FROM charging_system.stations;            -- 2402
SELECT COUNT(*) FROM charging_system.users;               -- 500
SELECT COUNT(*) FROM charging_system.charging_records;    -- 1000
```

也可以在浏览器测试后端接口：

```text
http://127.0.0.1:8000/api/cities
```

## 7. 启动后端

### 7.1 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

### 7.2 启动 FastAPI

```powershell
uvicorn backend.main:app --reload
```

```text
backend.main   backend/main.py 文件
app            main.py 里的 FastAPI 应用对象
--reload       开发模式，修改代码自动重启
```

启动成功后：

```text
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 7.3 验证后端

访问以下地址测试：

```text
http://127.0.0.1:8000/api/health
```

返回：

```json
{"status": "ok", "message": "城市充电桩系统后端运行正常"}
```

### 7.4 查看接口文档

FastAPI 自动生成 Swagger 文档：

```text
http://127.0.0.1:8000/docs
```

页面展示所有可用的接口、参数和返回格式，可以直接在页面点击"Try it out"测试接口。

## 8. 启动前端

### 8.1 安装依赖

首次运行前，需要安装 npm 依赖：

```powershell
npm install
```

如果已经安装过可以跳过此步骤。

### 8.2 开发模式启动

```powershell
npm run dev
```

启动成功后：

```text
VITE v8.0.8  ready in 300 ms
  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

在浏览器打开 `http://localhost:5173/`。

### 8.3 前后端联调

前端默认的后端地址配置在 `src/api/http.ts`：

```typescript
export const http = axios.create({
  baseURL: 'http://127.0.0.1:8000',   ← 指向后端
  timeout: 10000,
})
```

确保：

```text
1. 后端已启动（http://127.0.0.1:8000）
2. 前端已启动（http://localhost:5173）
3. 浏览器访问前端地址
4. 前端的 Axios 请求会自动转发到后端
```

如果后端改了端口，同步修改 `baseURL`。

## 9. 生产构建

### 9.1 构建

```powershell
npm run build
```

构建成功后会在项目根目录生成 `dist/` 文件夹。

```text
dist/
├── index.html
├── assets/
│   ├── index-xxx.js
│   ├── index-xxx.css
│   └── ...
```

### 9.2 类型检查

```powershell
npm run type-check
```

或单独运行：

```powershell
npx vue-tsc --noEmit
```

检查 TypeScript 类型错误，不输出文件。

## 10. 项目配置说明

### 10.1 Vite 配置（vite.config.ts）

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
```

```text
plugins     vue() 提供 Vue SFC 编译支持
resolve.alias @ 别名指向 src/ 目录
```

### 10.2 TypeScript 配置（tsconfig.app.json）

```json
{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "include": ["src/**/*", "src/**/*.vue"],
  "compilerOptions": {
    "noUncheckedIndexedAccess": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

```text
paths: @/* → ./src/*  配合 Vite 的别名
include: src/**/*.vue  包含所有 Vue 文件
```

### 10.3 前端依赖（package.json）

生产环境依赖：

| 包名 | 作用 |
|---|---|
| vue ^3.5.32 | 前端框架 |
| element-plus ^2.14.0 | UI 组件库 |
| @element-plus/icons-vue ^2.3.2 | 图标库 |
| echarts ^6.1.0 | 图表库 |
| axios ^1.16.1 | HTTP 请求 |
| pinia ^3.0.4 | 状态管理 |
| vue-router ^5.0.7 | 路由 |

## 11. 常见启动问题

### 11.1 端口被占用

后端端口被占用：

```text
Error: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)
```

解决：换端口启动：

```powershell
uvicorn backend.main:app --reload --port 8001
```

前端也要同步修改 `http.ts` 中的 `baseURL`。

### 11.2 数据库连接失败

```text
Connection refused: connect to 127.0.0.1:5432
```

解决：

```text
1. 确认 PostgreSQL 服务已启动
2. 检查 database.py 中的用户名和密码
3. 检查端口号是否正确（默认 5432）
```

### 11.3 ModuleNotFoundError

```text
ModuleNotFoundError: No module named 'fastapi'
```

解决：

```text
当前环境未安装对应包
激活虚拟环境后重新安装
使用 .venv\Scripts\python.exe 运行脚本
```

### 11.4 npm 命令找不到

```text
npm : The term 'npm' is not recognized as a cmdlet
```

解决：

```text
Node.js 未安装或未添加到 PATH
重新安装 Node.js
或使用完整路径运行
```

### 11.5 前端页面空白

可能原因：

```text
1. 后端未启动，API 请求全部失败
2. 跨域问题（CORS），前端无法调用后端
3. TypeScript 编译错误
```

## 12. 实验报告可用描述

可以在实验报告中写：

```text
系统运行需要 Node.js 24.14.0、Python 3.14.3 和 PostgreSQL 18.3 环境。数据库配置在 backend/database.py 中，包含数据库名称、用户名和密码等连接信息。数据导入分为两步：首先运行 csv_to_json.py 将 public/data 目录下的 6 个 CSV 文件转换为 JSON 格式，然后运行 import_json_to_db.py 按外键依赖顺序导入 PostgreSQL 数据库。后端使用 uvicorn 启动 FastAPI 服务，前端使用 Vite 启动开发服务器，前后端通过 Axios 在 localhost:5173 和 localhost:8000 之间通信。生产构建使用 npm run build 生成 dist 目录。
```
