# 数据库导入流程教程

本文档说明“城市充电桩信息查询系统”的数据导入流程。当前项目的数据来源是 CSV 文件，老师要求先转换为 JSON 文件，所以本项目采用：

```text
CSV 原始数据 -> JSON 中间文件 -> PostgreSQL 数据库表
```

最终导入链路如下：

```text
public/data/*.csv
        ↓
scripts/csv_to_json.py
        ↓
public/data_json/*.json
        ↓
scripts/import_json_to_db.py
        ↓
PostgreSQL 数据库 car_charging_db
        ↓
charging_system schema 下的 6 张表
```

## 1. 相关目录

```text
vue-carcharging/
├─ public/
│  ├─ data/                  原始 CSV 文件
│  └─ data_json/             转换后的 JSON 文件
├─ scripts/
│  ├─ csv_to_json.py         CSV 转 JSON 脚本
│  └─ import_json_to_db.py   JSON 导入数据库脚本
├─ docs/
│  └─ database_import_guide.md
└─ .venv/                    Python 虚拟环境
```

## 2. 数据库信息

数据库名称：

```text
car_charging_db
```

Schema 名称：

```text
charging_system
```

本项目不设置默认 `search_path`，所以所有表都使用完整名称：

```text
charging_system.cities
charging_system.operators
charging_system.charger_specs
charging_system.stations
charging_system.users
charging_system.charging_records
```

这样做的好处是表归属清晰，不会和 PostgreSQL 默认的 `public` schema 混在一起。

## 3. 文件与表的对应关系

| 原始 CSV 文件 | JSON 文件 | 数据库表 |
|---|---|---|
| `expanded_cities.csv` | `expanded_cities.json` | `charging_system.cities` |
| `operators_info.csv` | `operators_info.json` | `charging_system.operators` |
| `charger_specifications.csv` | `charger_specifications.json` | `charging_system.charger_specs` |
| `expanded_stations.csv` | `expanded_stations.json` | `charging_system.stations` |
| `users.csv` | `users.json` | `charging_system.users` |
| `charging_records.csv` | `charging_records.json` | `charging_system.charging_records` |

## 4. CSV 转 JSON 脚本

脚本位置：

```text
scripts/csv_to_json.py
```

主要作用：

```text
1. 读取 public/data 下的所有 CSV 文件。
2. 使用 CSV 表头作为 JSON 的 key。
3. 每一行 CSV 转换成一个 JSON 对象。
4. 每个 CSV 文件生成一个同名 JSON 文件。
5. 跳过 CSV 中的空行。
```

核心代码：

```python
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "public" / "data"
JSON_DIR = BASE_DIR / "public" / "data_json"

csv_files = sorted(CSV_DIR.glob("*.csv"))

for csv_path in csv_files:
    with csv_path.open("r", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = [
            row
            for row in reader
            if any(value.strip() for value in row.values())
        ]

        json_path = JSON_DIR / (csv_path.stem + ".json")

        with json_path.open("w", encoding="utf-8") as json_file:
            json.dump(rows, json_file, ensure_ascii=False, indent=2)

        print(csv_path.name, len(rows))
```

### 4.1 路径代码解释

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

`__file__` 表示当前脚本文件，也就是：

```text
scripts/csv_to_json.py
```

`.parent` 是 `scripts` 文件夹，`.parent.parent` 就是项目根目录。

```python
CSV_DIR = BASE_DIR / "public" / "data"
```

表示原始 CSV 数据目录。

```python
JSON_DIR = BASE_DIR / "public" / "data_json"
```

表示 JSON 输出目录。

### 4.2 读取所有 CSV

```python
csv_files = sorted(CSV_DIR.glob("*.csv"))
```

`glob("*.csv")` 表示查找所有以 `.csv` 结尾的文件。

`sorted()` 用来排序，让文件处理顺序稳定。

### 4.3 DictReader 的作用

```python
reader = csv.DictReader(csv_file)
```

`DictReader` 会把 CSV 的第一行当作字段名。

例如 CSV：

```csv
city_id,city_name,longitude
1,定南县,114.96
```

会被读取成：

```python
{
    "city_id": "1",
    "city_name": "定南县",
    "longitude": "114.96"
}
```

### 4.4 为什么使用 utf-8-sig

```python
encoding="utf-8-sig"
```

有些 CSV 文件开头会有 BOM 隐藏字符。如果直接用 `utf-8`，第一列字段名可能变成：

```text
\ufeffcity_id
```

或者在某些显示环境中变成乱码。

使用 `utf-8-sig` 可以自动处理这个隐藏字符，避免后续读取 JSON 时出现：

```text
KeyError: 'city_id'
```

### 4.5 跳过空行

```python
rows = [
    row
    for row in reader
    if any(value.strip() for value in row.values())
]
```

这段代码用于过滤空行。

如果 CSV 最后有：

```csv
,,,,,,
```

`DictReader` 会读出：

```python
{
    "city_id": "",
    "city_name": "",
    "longitude": "",
    ...
}
```

这些空行不应该导入数据库，所以用：

```python
any(value.strip() for value in row.values())
```

判断这一行是否至少有一个字段不为空。整行都为空时就跳过。

### 4.6 写出 JSON

```python
json.dump(rows, json_file, ensure_ascii=False, indent=2)
```

参数说明：

```text
rows                要写入的 Python 列表
json_file           打开的 JSON 文件对象
ensure_ascii=False  保留中文，不把中文转成 Unicode 编码
indent=2            使用 2 个空格缩进，方便阅读
```

运行命令：

```powershell
python scripts\csv_to_json.py
```

如果没有激活虚拟环境，也可以运行：

```powershell
.\.venv\Scripts\python.exe scripts\csv_to_json.py
```

## 5. JSON 导入 PostgreSQL 脚本

脚本位置：

```text
scripts/import_json_to_db.py
```

这个脚本负责把 `public/data_json` 中的 JSON 文件导入 PostgreSQL。

它使用的是“配置式导入”。

简单说：

```text
IMPORT_TASKS 负责描述每张表怎么导入。
通用函数负责按照配置执行导入。
```

## 6. 脚本整体结构

`import_json_to_db.py` 的结构大致是：

```python
import json
from pathlib import Path

import psycopg

BASE_DIR = ...
JSON_DIR = ...
DB_CONFIG = ...
IMPORT_TASKS = [...]

def normalize_value(value):
    ...

def load_json(filename):
    ...

def build_insert_sql(table, fields, conflict):
    ...

def test_connection():
    ...

def import_table(task):
    ...

def import_all():
    ...

if __name__ == "__main__":
    test_connection()
    import_all()
```

## 7. 数据库连接配置

```python
DB_CONFIG = {
    "dbname": "car_charging_db",
    "user": "postgres",
    "password": "你的数据库密码",
    "host": "localhost",
    "port": 5432,
}
```

含义：

```text
dbname    数据库名称
user      PostgreSQL 用户名
password  PostgreSQL 密码
host      数据库地址，本机使用 localhost
port      PostgreSQL 默认端口，一般是 5432
```

注意：文档中不要写真实密码，真实密码只保存在本地脚本中。

## 8. 配置式导入 IMPORT_TASKS

`IMPORT_TASKS` 是导入脚本的核心。

它是一个列表，列表中的每个字典表示一张表的导入任务。

例如城市表：

```python
{
    "filename": "expanded_cities.json",
    "table": "charging_system.cities",
    "fields": [
        "city_id",
        "city_name",
        "longitude",
        "latitude",
        "area_code",
        "population",
        "gdp_billion",
    ],
    "conflict": "city_id",
}
```

### 8.1 filename

```python
"filename": "expanded_cities.json"
```

表示要读取的 JSON 文件名。

脚本会用：

```python
json_path = JSON_DIR / filename
```

拼出完整路径：

```text
public/data_json/expanded_cities.json
```

### 8.2 table

```python
"table": "charging_system.cities"
```

表示数据要插入的数据库表。

因为本项目不设置默认 `search_path`，所以这里写完整表名：

```text
schema.table
```

### 8.3 fields

```python
"fields": [
    "city_id",
    "city_name",
    "longitude",
    "latitude",
    "area_code",
    "population",
    "gdp_billion",
]
```

`fields` 有两个作用。

第一个作用：生成 SQL 中的列名。

```sql
INSERT INTO charging_system.cities (
    city_id,
    city_name,
    longitude,
    latitude,
    area_code,
    population,
    gdp_billion
)
```

第二个作用：从 JSON 的每一行中按顺序取值。

例如 JSON 行：

```python
row = {
    "city_id": "1",
    "city_name": "定南县",
    "longitude": "114.96",
    "latitude": "24.68",
    "area_code": "0797-4291000",
    "population": "380000",
    "gdp_billion": "45.2",
}
```

程序会根据 `fields` 生成：

```python
(
    "1",
    "定南县",
    "114.96",
    "24.68",
    "0797-4291000",
    "380000",
    "45.2",
)
```

字段顺序必须和 SQL 中的占位符顺序一致。

### 8.4 conflict

```python
"conflict": "city_id"
```

表示主键冲突字段。

它会生成：

```sql
ON CONFLICT (city_id) DO NOTHING;
```

含义：

```text
如果 city_id 已经存在，就跳过这一行，不报错。
```

这样脚本可以重复运行，不会因为主键重复而失败。

## 9. 为什么使用配置式导入

如果不使用配置式导入，每张表都要单独写一套导入函数：

```text
import_cities()
import_operators()
import_charger_specs()
import_stations()
import_users()
import_charging_records()
```

每个函数里都会重复：

```text
1. 读取 JSON
2. 连接数据库
3. 创建 cursor
4. 遍历 rows
5. 执行 INSERT
6. commit
```

实际上每张表不同的只有：

```text
1. JSON 文件名
2. 表名
3. 字段列表
4. 主键字段
```

所以把这些变化项放进配置，代码更简洁、更容易维护。

这种设计可以概括为：

```text
配置描述“导入什么”
函数负责“怎么导入”
```

## 10. 自动生成 INSERT SQL

函数：

```python
def build_insert_sql(table: str, fields: list[str], conflict: str) -> str:
    columns = ", ".join(fields)
    placeholders = ", ".join(["%s"] * len(fields))

    return f"""
    INSERT INTO {table} ({columns})
    VALUES ({placeholders})
    ON CONFLICT ({conflict}) DO NOTHING;
    """
```

### 10.1 函数参数

```python
table: str
```

表名，例如：

```text
charging_system.cities
```

```python
fields: list[str]
```

字段列表，例如：

```python
["city_id", "city_name", "longitude"]
```

```python
conflict: str
```

主键字段，例如：

```text
city_id
```

### 10.2 生成字段字符串

```python
columns = ", ".join(fields)
```

如果：

```python
fields = ["city_id", "city_name", "longitude"]
```

那么：

```python
columns = "city_id, city_name, longitude"
```

### 10.3 生成占位符

```python
placeholders = ", ".join(["%s"] * len(fields))
```

如果字段有 3 个：

```python
["%s"] * 3
```

结果是：

```python
["%s", "%s", "%s"]
```

再通过 `join` 变成：

```text
%s, %s, %s
```

### 10.4 返回 SQL

最终会生成类似：

```sql
INSERT INTO charging_system.cities (
    city_id, city_name, longitude, latitude, area_code, population, gdp_billion
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (city_id) DO NOTHING;
```

## 11. 为什么用 %s 占位符

在 psycopg 中，`%s` 是 SQL 参数占位符。

正确写法：

```python
cur.execute(sql, values)
```

不要用字符串拼接：

```python
sql = f"INSERT INTO table VALUES ({row['city_id']})"
```

原因：

```text
1. 字符串拼接容易出错。
2. 中文、空值、引号等内容不好处理。
3. 存在 SQL 注入风险。
4. psycopg 不能自动帮你处理类型。
```

使用：

```python
cur.execute(sql, values)
```

psycopg 会自动处理：

```text
1. 字符串引号
2. None -> NULL
3. 数字、日期、布尔值等类型
```

## 12. 空值处理 normalize_value

函数：

```python
def normalize_value(value):
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    return value
```

逐行解释：

```python
if isinstance(value, str):
```

判断当前值是不是字符串。只有字符串才需要去空格。

```python
value = value.strip()
```

去掉字符串首尾空格。

```python
if value == "":
    return None
```

如果去空格后是空字符串，就返回 `None`。

Python 的 `None` 插入 PostgreSQL 时会变成：

```sql
NULL
```

这样可以避免错误：

```text
InvalidTextRepresentation: 无效的类型 integer 输入语法: ""
```

因为数据库的整数、小数、日期字段不能直接接收空字符串 `""`。

## 13. 读取 JSON load_json

函数：

```python
def load_json(filename: str) -> list[dict]:
    json_path = JSON_DIR / filename

    with json_path.open("r", encoding="utf-8") as json_file:
        return json.load(json_file)
```

作用：

```text
读取指定 JSON 文件，并返回 Python 列表。
```

例如：

```python
rows = load_json("expanded_cities.json")
```

返回：

```python
[
    {"city_id": "1", "city_name": "定南县", ...},
    {"city_id": "2", "city_name": "宁都县", ...},
]
```

## 14. 导入单张表 import_table

函数：

```python
def import_table(task: dict) -> None:
    rows = load_json(task["filename"])
    sql = build_insert_sql(task["table"], task["fields"], task["conflict"])

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            for row in rows:
                values = tuple(normalize_value(row[field]) for field in task["fields"])
                cur.execute(sql, values)

        conn.commit()

    print(f"Imported {task['table']}: {len(rows)} rows")
```

### 14.1 读取配置里的 JSON 文件

```python
rows = load_json(task["filename"])
```

如果当前任务是城市表，那么：

```python
task["filename"] = "expanded_cities.json"
```

就会读取城市 JSON。

### 14.2 生成 SQL

```python
sql = build_insert_sql(task["table"], task["fields"], task["conflict"])
```

根据当前任务的表名、字段列表和主键字段生成 SQL。

### 14.3 连接数据库

```python
with psycopg.connect(**DB_CONFIG) as conn:
```

`**DB_CONFIG` 表示把字典展开成参数。

例如：

```python
psycopg.connect(
    dbname="car_charging_db",
    user="postgres",
    password="...",
    host="localhost",
    port=5432,
)
```

### 14.4 创建游标

```python
with conn.cursor() as cur:
```

游标可以理解成“执行 SQL 的工具”。

### 14.5 遍历每一行数据

```python
for row in rows:
```

`rows` 是 JSON 文件读取出来的列表，每个 `row` 是一条数据。

### 14.6 生成 values

```python
values = tuple(normalize_value(row[field]) for field in task["fields"])
```

这句是配置式导入的关键。

它会按照 `fields` 字段列表，从 JSON 行中取值。

如果：

```python
task["fields"] = ["city_id", "city_name", "longitude"]
```

当前行：

```python
row = {
    "city_id": "1",
    "city_name": "定南县",
    "longitude": "114.96",
}
```

那么生成：

```python
values = ("1", "定南县", "114.96")
```

同时每个值都会经过：

```python
normalize_value(...)
```

用于处理空字符串。

### 14.7 执行插入

```python
cur.execute(sql, values)
```

把 SQL 和参数传给 PostgreSQL。

### 14.8 提交事务

```python
conn.commit()
```

提交事务，让插入结果真正保存到数据库。

## 15. 导入全部表 import_all

函数：

```python
def import_all() -> None:
    for task in IMPORT_TASKS:
        import_table(task)
```

含义：

```text
按照 IMPORT_TASKS 的顺序，一张表一张表导入。
```

导入顺序必须是：

```text
1. cities
2. operators
3. charger_specs
4. stations
5. users
6. charging_records
```

原因：

```text
stations 引用 cities、operators、charger_specs。
users 引用 cities。
charging_records 引用 users、stations。
```

基础表必须先导入，否则后面的外键会找不到对应数据。

## 16. 脚本入口

```python
if __name__ == "__main__":
    test_connection()
    import_all()
```

含义：

```text
当直接运行 import_json_to_db.py 时：
1. 先测试数据库连接。
2. 再导入所有表。
```

运行命令：

```powershell
python scripts\import_json_to_db.py
```

如果终端没有激活 `.venv`，可以运行：

```powershell
.\.venv\Scripts\python.exe scripts\import_json_to_db.py
```

成功输出示例：

```text
Database connection: car_charging_db
Imported charging_system.cities: 8 rows
Imported charging_system.operators: 5 rows
Imported charging_system.charger_specs: 5 rows
Imported charging_system.stations: 2402 rows
Imported charging_system.users: 500 rows
Imported charging_system.charging_records: 1000 rows
```

## 17. 数据库检查 SQL

检查每张表数量：

```sql
SELECT COUNT(*) FROM charging_system.cities;
SELECT COUNT(*) FROM charging_system.operators;
SELECT COUNT(*) FROM charging_system.charger_specs;
SELECT COUNT(*) FROM charging_system.stations;
SELECT COUNT(*) FROM charging_system.users;
SELECT COUNT(*) FROM charging_system.charging_records;
```

查看城市数据：

```sql
SELECT city_id, city_name
FROM charging_system.cities
ORDER BY city_id;
```

查看充电站和城市关联：

```sql
SELECT
    s.station_id,
    s.station_name,
    c.city_name
FROM charging_system.stations AS s
JOIN charging_system.cities AS c
    ON s.city_id = c.city_id
LIMIT 10;
```

查看充电记录和用户关联：

```sql
SELECT
    r.record_id,
    r.user_id,
    u.username,
    r.energy_kwh,
    r.cost_yuan
FROM charging_system.charging_records AS r
JOIN charging_system.users AS u
    ON r.user_id = u.user_id
LIMIT 10;
```

## 18. 常见错误

### 18.1 KeyError: 'city_id'

原因：

```text
CSV 第一列可能带 BOM 隐藏字符，导致字段名不是 city_id。
```

解决：

```python
encoding="utf-8-sig"
```

### 18.2 integer 输入语法无效

错误示例：

```text
InvalidTextRepresentation: 无效的类型 integer 输入语法: ""
```

原因：

```text
空字符串 "" 被插入到了 INTEGER、NUMERIC、DATE 等字段。
```

解决：

```text
1. CSV 转 JSON 时跳过空行。
2. 导入数据库时使用 normalize_value() 把 "" 转成 None。
```

### 18.3 ModuleNotFoundError: No module named 'psycopg'

原因：

```text
当前终端没有使用项目的 .venv 虚拟环境。
```

解决：

```powershell
.\.venv\Scripts\python.exe scripts\import_json_to_db.py
```

或者先激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 19. 实验报告可用描述

可以在实验报告中写：

```text
本系统的数据来源为 CSV 文件。为满足 JSON 数据处理要求，系统首先使用 Python 脚本读取 public/data 目录下的 CSV 文件，通过 csv.DictReader 将每一行数据转换为字典对象，再使用 json.dump 生成 JSON 文件并保存到 public/data_json 目录。

随后，系统使用 psycopg 连接 PostgreSQL 数据库，读取 JSON 文件并按照表之间的外键依赖顺序导入 charging_system schema 下的关系表。导入脚本采用配置式设计，通过 IMPORT_TASKS 描述 JSON 文件、数据库表、字段列表和主键冲突字段，再由通用函数自动生成 INSERT SQL 并执行导入。该方式减少了重复代码，也保证了数据导入过程清晰、可维护。
```
