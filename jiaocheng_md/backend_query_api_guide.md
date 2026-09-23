# 后端表查询接口教程

本文档记录“城市充电桩信息查询系统”后端表查询接口的设计与实现。当前后端使用 FastAPI，数据库使用 PostgreSQL，主要完成两个业务模块的数据查询：

```text
1. 充电站查询模块
2. 充电记录查询模块
```

目前暂不包含图表统计接口，本文只讲表查询和详情查询。

## 1. 后端在系统中的作用

系统整体数据流是：

```text
Vue 前端
    ↓ Axios
FastAPI 后端
    ↓ psycopg
PostgreSQL 数据库
```

前端不直接访问数据库，而是请求 FastAPI 接口。FastAPI 接收到请求后查询 PostgreSQL，再把结果整理成 JSON 返回给前端。

例如：

```text
用户点击“充电站查询”
    ↓
前端请求 /api/stations
    ↓
FastAPI 查询 stations、cities、operators、charger_specs
    ↓
返回站点列表 JSON
```

## 2. 当前接口列表

当前 `backend/main.py` 中包含以下接口：

```text
GET /api/health
GET /api/cities
GET /api/operators
GET /api/charger-specs

GET /api/stations
GET /api/stations/{station_id}

GET /api/records
GET /api/records/{record_id}
```

接口分为三类：

```text
基础字典接口：cities、operators、charger-specs
列表查询接口：stations、records
详情查询接口：stations/{station_id}、records/{record_id}
```

## 3. FastAPI 路由基础

FastAPI 使用装饰器定义接口。

例如：

```python
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "城市充电桩系统后端运行正常",
    }
```

含义是：

```text
当浏览器或前端用 GET 方法访问 /api/health 时，
FastAPI 执行 health_check() 函数。
```

返回的 Python 字典会自动转换成 JSON。

## 4. 后端启动命令

推荐从项目根目录启动后端：

```powershell
python -m uvicorn backend.main:app --reload
```

含义：

```text
backend.main  表示 backend/main.py
app           表示 main.py 里的 FastAPI 应用对象
--reload      表示开发模式，代码修改后自动重启
```

启动后访问：

```text
http://127.0.0.1:8000/docs
```

可以看到 FastAPI 自动生成的接口文档。

## 5. 数据库连接

数据库连接统一放在：

```text
backend/database.py
```

示例结构：

```python
import psycopg


DB_CONFIG = {
    "dbname": "car_charging_db",
    "user": "postgres",
    "password": "你的数据库密码",
    "host": "localhost",
    "port": 5432,
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)
```

这样做的原因：

```text
1. 避免每个接口重复写数据库配置。
2. 后续修改数据库配置时，只需要改一个文件。
3. main.py 中只需要调用 get_connection()。
```

在接口中使用：

```python
with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT ...")
        rows = cur.fetchall()
```

## 6. 列表接口和详情接口

本项目查询流程分为两层：

```text
列表接口：返回多条简略信息
详情接口：根据 id 返回某一条完整信息
```

这正好对应作业要求：

```text
点击查询
    ↓
显示查询结果窗口
    ↓
点击某条结果
    ↓
显示详细内容窗口
```

以后前端流程是：

```text
点击“查询”
    ↓
GET /api/stations
    ↓
展示站点列表
    ↓
点击某个 station
    ↓
GET /api/stations/{station_id}
    ↓
展示站点详情
```

## 7. 基础字典接口

基础字典接口用于给前端查询窗口提供下拉选项。

例如城市下拉框需要：

```text
GET /api/cities
```

运营商下拉框需要：

```text
GET /api/operators
```

充电桩规格下拉框需要：

```text
GET /api/charger-specs
```

这些接口通常不需要复杂筛选，只需要按主键排序返回。

## 8. /api/cities 接口

接口作用：

```text
查询城市列表。
```

SQL：

```sql
SELECT
    city_id,
    city_name,
    longitude,
    latitude,
    area_code,
    population,
    gdp_billion
FROM charging_system.cities
ORDER BY city_id;
```

返回结构：

```json
{
  "data": [
    {
      "city_id": 1,
      "city_name": "定南县",
      "longitude": 114.96,
      "latitude": 24.68,
      "area_code": "0797-4291000",
      "population": 380000,
      "gdp_billion": 45.2
    }
  ]
}
```

## 9. 充电站列表接口 /api/stations

接口作用：

```text
查询充电站简略列表。
```

它返回的是列表展示需要的核心字段：

```text
station_id
station_name
city_name
operator_name
type_name
power_kw
```

不返回地址、电话、停车位等详细字段，因为这些字段属于详情接口。

## 10. 为什么 stations 要 JOIN 多张表

`stations` 表里保存的是编号：

```text
city_id
operator_id
spec_id
```

如果只查询 `stations`，前端只能看到：

```text
city_id = 1
operator_id = 2
spec_id = 5
```

这对用户不友好。

所以需要 JOIN：

```sql
JOIN charging_system.cities AS c
    ON s.city_id = c.city_id
JOIN charging_system.operators AS o
    ON s.operator_id = o.operator_id
JOIN charging_system.charger_specs AS cs
    ON s.spec_id = cs.spec_id
```

这样可以把编号转换成可读信息：

```text
city_id      -> city_name
operator_id  -> operator_name
spec_id      -> type_name、power_kw
```

## 11. stations 列表 SQL

```sql
SELECT
    s.station_id,
    s.station_name,
    c.city_name,
    o.operator_name,
    cs.type_name,
    cs.power_kw
FROM charging_system.stations AS s
JOIN charging_system.cities AS c
    ON s.city_id = c.city_id
JOIN charging_system.operators AS o
    ON s.operator_id = o.operator_id
JOIN charging_system.charger_specs AS cs
    ON s.spec_id = cs.spec_id
ORDER BY s.station_id
LIMIT 50;
```

别名说明：

```text
s   stations
c   cities
o   operators
cs  charger_specs
```

使用别名可以让 SQL 更短、更清晰。

## 12. stations 查询参数

`/api/stations` 支持可选参数：

```text
city_id
operator_id
keyword
```

示例：

```text
/api/stations
/api/stations?city_id=1
/api/stations?operator_id=2
/api/stations?keyword=服务区
/api/stations?city_id=1&operator_id=2&keyword=服务区
```

FastAPI 函数写法：

```python
def get_stations(
    city_id: int | None = None,
    operator_id: int | None = None,
    keyword: str | None = None,
):
```

含义：

```text
city_id 可以传，也可以不传。
operator_id 可以传，也可以不传。
keyword 可以传，也可以不传。
```

如果不传，对应值就是 `None`。

## 13. 动态 WHERE 条件

为了让查询条件可选，代码使用：

```python
conditions = []
params = []
```

`conditions` 用来保存 SQL 条件。

`params` 用来保存条件对应的参数值。

例如：

```python
if city_id is not None:
    conditions.append("s.city_id = %s")
    params.append(city_id)
```

如果用户访问：

```text
/api/stations?city_id=1
```

那么：

```python
conditions = ["s.city_id = %s"]
params = [1]
```

如果用户还传了 `operator_id=2`：

```python
conditions = ["s.city_id = %s", "s.operator_id = %s"]
params = [1, 2]
```

## 14. build_where 函数

代码中封装了：

```python
def build_where(conditions: list[str]) -> str:
    if not conditions:
        return ""
    return "WHERE " + " AND ".join(conditions)
```

作用：

```text
根据 conditions 列表生成 SQL 的 WHERE 部分。
```

如果：

```python
conditions = []
```

返回：

```text
""
```

也就是不加 WHERE。

如果：

```python
conditions = ["s.city_id = %s", "s.operator_id = %s"]
```

返回：

```sql
WHERE s.city_id = %s AND s.operator_id = %s
```

其中：

```python
" AND ".join(conditions)
```

表示把多个条件用 `AND` 连接起来。

## 15. %s 参数占位符

在 SQL 中：

```sql
WHERE s.station_id = %s
```

`%s` 是 psycopg 的参数占位符，不是 Python 变量。

真正的值通过 `execute()` 的第二个参数传入：

```python
cur.execute(
    """
    SELECT ...
    WHERE s.station_id = %s;
    """,
    (station_id,),
)
```

对应关系是：

```text
第 1 个 %s  ->  station_id
```

如果：

```python
station_id = 1
```

效果相当于：

```sql
WHERE s.station_id = 1
```

但这是参数化查询，更安全。

## 16. 为什么单个参数要写逗号

```python
(station_id,)
```

这是一个只有一个元素的元组。

在 Python 中：

```python
(station_id)
```

不是元组，只是普通括号。

只有：

```python
(station_id,)
```

才表示单元素元组。

因为 `execute()` 的第二个参数需要一个参数序列，所以单个参数也要写成元组。

## 17. 充电站详情接口 /api/stations/{station_id}

接口作用：

```text
根据 station_id 查询某一个充电站的完整信息。
```

路径参数：

```python
@app.get("/api/stations/{station_id}")
def get_station_detail(station_id: int):
```

如果访问：

```text
/api/stations/1
```

FastAPI 会自动把 `1` 传给：

```python
station_id = 1
```

详情接口会返回：

```text
地址
电话
经纬度
城市名
运营商名
充电桩规格
开放时间
是否有卫生间
停车位数量
```

如果没有查到数据：

```python
raise HTTPException(status_code=404, detail="充电站不存在")
```

返回 404，表示资源不存在。

## 18. 充电记录列表接口 /api/records

接口作用：

```text
查询充电记录简略列表。
```

返回字段：

```text
record_id
username
station_name
city_name
charge_start_time
duration_minutes
energy_kwh
cost_yuan
payment_method
```

联表关系：

```sql
charging_records AS r
JOIN users AS u
JOIN stations AS s
JOIN cities AS c
```

原因：

```text
charging_records 中只有 user_id 和 station_id。
需要 JOIN users 获取 username。
需要 JOIN stations 获取 station_name。
需要 JOIN cities 获取 city_name。
```

## 19. records 查询参数

`/api/records` 支持：

```text
city_id
payment_method
keyword
```

示例：

```text
/api/records
/api/records?city_id=1
/api/records?payment_method=微信支付
/api/records?keyword=REC000001
```

其中 `keyword` 会搜索：

```text
record_id
username
station_name
```

## 20. 时间字段处理

PostgreSQL 的 `TIMESTAMP` 类型在 Python 中会变成 `datetime` 对象。

JSON 不能直接稳定显示 `datetime`，所以代码中使用：

```python
row[4].isoformat() if row[4] is not None else None
```

转换成字符串：

```text
2024-01-10T12:23:00
```

## 21. 数值字段处理

PostgreSQL 的 `NUMERIC` 类型在 Python 中通常是 `Decimal`。

为了方便返回 JSON，代码中使用：

```python
def to_float(value):
    return float(value) if value is not None else None
```

然后：

```python
"power_kw": to_float(row[5])
```

这样前端拿到的是普通数字。

## 22. 充电记录详情接口 /api/records/{record_id}

接口作用：

```text
根据 record_id 查询某一条充电记录的详细信息。
```

路径参数：

```python
@app.get("/api/records/{record_id}")
def get_record_detail(record_id: str):
```

因为 `record_id` 是：

```text
REC000001
```

不是纯数字，所以类型用 `str`。

详情接口返回：

```text
记录编号
用户编号
用户名
手机号
用户类型
车辆类型
车辆型号
站点编号
站点名称
城市名
开始时间
结束时间
充电时长
充电电量
费用
支付方式
开始 SOC
结束 SOC
```

如果查不到：

```python
raise HTTPException(status_code=404, detail="充电记录不存在")
```

## 23. 前端对应关系

充电站模块：

```text
点击查询
    ↓
GET /api/stations
    ↓
显示站点结果列表
    ↓
点击某个站点
    ↓
GET /api/stations/{station_id}
    ↓
显示站点详情窗口
```

充电记录模块：

```text
点击查询
    ↓
GET /api/records
    ↓
显示充电记录列表
    ↓
点击某条记录
    ↓
GET /api/records/{record_id}
    ↓
显示记录详情窗口
```

这正好对应作业要求：

```text
1 点击模块菜单
2 弹出查询窗口
3 点击查询，弹出查询结果窗口
4 再点击结果窗口，弹出更详细内容窗口
```

## 24. 测试地址

后端启动：

```powershell
python -m uvicorn backend.main:app --reload
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

常用测试地址：

```text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/api/cities
http://127.0.0.1:8000/api/operators
http://127.0.0.1:8000/api/charger-specs
http://127.0.0.1:8000/api/stations
http://127.0.0.1:8000/api/stations/1
http://127.0.0.1:8000/api/records
http://127.0.0.1:8000/api/records/REC000001
```

带查询参数：

```text
http://127.0.0.1:8000/api/stations?city_id=1
http://127.0.0.1:8000/api/stations?operator_id=2
http://127.0.0.1:8000/api/stations?keyword=服务区
http://127.0.0.1:8000/api/records?city_id=1
http://127.0.0.1:8000/api/records?payment_method=微信支付
http://127.0.0.1:8000/api/records?keyword=REC000001
```

## 25. 实验报告可用描述

可以在实验报告中写：

```text
后端采用 FastAPI 框架实现 RESTful 查询接口。系统通过 psycopg 连接 PostgreSQL 数据库，并将数据库查询结果转换为 JSON 返回给前端。充电站查询模块提供站点列表接口和站点详情接口，列表接口返回站点名称、城市、运营商和充电桩规格等简要信息，详情接口根据 station_id 返回地址、电话、经纬度、开放时间、停车位等完整信息。

充电记录模块同样采用列表接口和详情接口的设计方式。列表接口返回记录编号、用户、站点、城市、充电时间、电量和费用等信息，详情接口根据 record_id 返回用户车辆信息、充电起止时间、SOC 变化和支付方式等详细内容。查询接口支持可选参数筛选，通过动态拼接 WHERE 条件和参数化查询实现安全的条件查询。
```
