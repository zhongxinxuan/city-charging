# 图表统计接口教程

本文档说明"城市充电桩信息查询系统"图表统计接口的设计与实现。图表数据全部来自后端的 SQL 聚合查询，前端使用 ECharts 渲染展示。

## 1. 图表统计在系统中的作用

系统目前共 **7 个图表统计接口**，为仪表盘和数据总览页面提供数据支持：

```text
仪表盘（3个图表）：
  1. 各区县站点数量      柱状图（含占比标签）
  2. 运营商市场占比       环形饼图（含百分比）
  3. 充电桩类型分布       横向柱状图

数据总览（6个图表）：
  1. 各区县站点数量      柱状图
  2. 运营商站点占比       环形饼图
  3. 支付方式分布         饼图
  4. 充电记录-按区县分布   柱状图
  5. 平均充电费用-按区县   柱状图
  6. 平均充电电量-按区县   柱状图
```

仪表盘和数据总览的图表**侧重点不同**：
- 仪表盘图表更**详细**（含占比数值标签、百分比标签）
- 数据总览图表更**整体**（简洁风格，覆盖更多维度）

## 2. 接口列表

所有图表接口都在 `backend/main.py` 中，统一前缀为 `/api/charts/`：

| 端点 | 说明 | 页面 |
|---|---|---|
| `GET /api/charts/stations-by-city` | 各区县站点数量 | 仪表盘 + 数据总览 |
| `GET /api/charts/operator-share` | 运营商站点占比 | 仪表盘 + 数据总览 |
| `GET /api/charts/station-type-distribution` | 充电桩类型分布 | 仪表盘 |
| `GET /api/charts/payment-method-distribution` | 支付方式分布 | 数据总览 |
| `GET /api/charts/records-by-city` | 充电记录-按区县 | 数据总览 |
| `GET /api/charts/avg-cost-by-city` | 平均充电费用-按区县 | 数据总览 |
| `GET /api/charts/avg-energy-by-city` | 平均充电电量-按区县 | 数据总览 |

## 3. 统一返回结构

所有图表接口返回相同的数据结构：

```json
{
  "data": [
    { "name": "章贡区", "value": 120 },
    { "name": "定南县", "value": 85 }
  ]
}
```

```text
name  类别名称（字符串）
value 数值（整数或浮点数）
```

前端用 `ChartPoint` 类型接收：

```typescript
export interface ChartPoint {
  name: string
  value: number
}
```

## 4. 各区县站点数量（stations-by-city）

接口作用：

```text
统计每个城市/区县有多少个充电站，按站点数降序排列。
```

SQL：

```sql
SELECT
    c.city_name,
    COUNT(s.station_id) AS station_count
FROM charging_system.cities AS c
LEFT JOIN charging_system.stations AS s
    ON c.city_id = s.city_id
GROUP BY c.city_id, c.city_name
ORDER BY station_count DESC, c.city_id;
```

SQL 解释：

```text
LEFT JOIN 确保没有站点的城市也会显示（count=0）
GROUP BY 按城市分组统计
ORDER BY station_count DESC 站点数多的排前面
```

返回示例：

```json
{
  "data": [
    { "name": "章贡区", "value": 120 },
    { "name": "宁都县", "value": 95 },
    { "name": "定南县", "value": 85 }
  ]
}
```

## 5. 运营商站点占比（operator-share）

接口作用：

```text
统计每个运营商拥有多少充电站，用于饼图展示市场占比。
```

SQL：

```sql
SELECT
    o.operator_name,
    COUNT(s.station_id) AS station_count
FROM charging_system.operators AS o
LEFT JOIN charging_system.stations AS s
    ON o.operator_id = s.operator_id
GROUP BY o.operator_id, o.operator_name
ORDER BY station_count DESC, o.operator_id;
```

和城市统计的区别：

```text
stations-by-city 按 city_id 分组
operator-share   按 operator_id 分组
```

返回示例：

```json
{
  "data": [
    { "name": "国家电网", "value": 480 },
    { "name": "特来电", "value": 360 },
    { "name": "星星充电", "value": 280 }
  ]
}
```

## 6. 充电桩类型分布（station-type-distribution）

接口作用：

```text
统计每种充电桩规格覆盖了多少个充电站，用于仪表盘横向柱状图。
```

SQL：

```sql
SELECT
    cs.type_name,
    COUNT(s.station_id) AS station_count
FROM charging_system.charger_specs AS cs
LEFT JOIN charging_system.stations AS s
    ON cs.spec_id = s.spec_id
GROUP BY cs.type_name              ← 按类型名称分组，不按 spec_id
ORDER BY station_count DESC, cs.type_name;
```

注意：

```text
GROUP BY cs.type_name 按类型名称分组
而不是 GROUP BY cs.spec_id, cs.type_name
后者会导致同名类型重复出现（因为多个 spec_id 可能对应同一个 type_name）
```

返回示例：

```json
{
  "data": [
    { "name": "直流快充桩", "value": 800 },
    { "name": "交流慢充桩", "value": 720 },
    { "name": "超级快充桩", "value": 450 }
  ]
}
```

## 7. 支付方式分布（payment-method-distribution）

接口作用：

```text
统计每种支付方式使用了多少次，用于数据总览饼图。
```

SQL：

```sql
SELECT
    r.payment_method,
    COUNT(r.record_id) AS record_count
FROM charging_system.charging_records AS r
GROUP BY r.payment_method
ORDER BY record_count DESC;
```

```text
直接查 charging_records 表
不需要 JOIN 其他表，因为 payment_method 就在记录表中
```

返回示例：

```json
{
  "data": [
    { "name": "微信支付", "value": 380 },
    { "name": "支付宝", "value": 320 },
    { "name": "信用卡", "value": 180 }
  ]
}
```

## 8. 充电记录-按区县分布（records-by-city）

接口作用：

```text
统计每个城市产生了多少条充电记录。
```

SQL：

```sql
SELECT
    c.city_name,
    COUNT(r.record_id) AS record_count
FROM charging_system.cities AS c
LEFT JOIN charging_system.stations AS s
    ON c.city_id = s.city_id
LEFT JOIN charging_system.charging_records AS r
    ON s.station_id = r.station_id
GROUP BY c.city_id, c.city_name
ORDER BY record_count DESC, c.city_id;
```

联表路径：

```text
cities → stations → charging_records
city_id → station_id → record_id
```

两张 LEFT JOIN 确保没有记录的城市也会显示。

## 9. 平均充电费用-按区县（avg-cost-by-city）

接口作用：

```text
统计每个城市充电记录的平均费用。
```

SQL：

```sql
SELECT
    c.city_name,
    ROUND(AVG(r.cost_yuan)::numeric, 2) AS avg_cost
FROM charging_system.cities AS c
JOIN charging_system.stations AS s
    ON c.city_id = s.city_id
JOIN charging_system.charging_records AS r
    ON s.station_id = r.station_id
GROUP BY c.city_id, c.city_name
ORDER BY avg_cost DESC;
```

SQL 关键点：

```text
AVG(r.cost_yuan)         计算平均费用
::numeric                 转为 numeric 类型
ROUND(..., 2)             保留 2 位小数
JOIN（不是 LEFT JOIN）    只统计有记录的城市
ORDER BY avg_cost DESC    平均费用高的排前面
```

## 10. 平均充电电量-按区县（avg-energy-by-city）

接口作用：

```text
统计每个城市充电记录的平均充电量（kWh）。
```

SQL：

```sql
SELECT
    c.city_name,
    ROUND(AVG(r.energy_kwh)::numeric, 2) AS avg_energy
FROM charging_system.cities AS c
JOIN charging_system.stations AS s
    ON c.city_id = s.city_id
JOIN charging_system.charging_records AS r
    ON s.station_id = r.station_id
GROUP BY c.city_id, c.city_name
ORDER BY avg_energy DESC;
```

与 avg-cost-by-city 的区别：

```text
avg-cost-by-city    AVG(cost_yuan)    平均费用（元）
avg-energy-by-city  AVG(energy_kwh)   平均电量（kWh）
```

## 11. 前端 API 层（charts.ts）

前端调用接口的统一写法：

```typescript
import { http } from './http'

export interface ChartPoint {
  name: string
  value: number
}

// 所有图表接口都返回 ChartPoint[]
export async function getStationsByCityChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/stations-by-city')
  return response.data.data
}

export async function getOperatorShareChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/operator-share')
  return response.data.data
}

export async function getStationTypeDistributionChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/station-type-distribution')
  return response.data.data
}
// ... 其他接口类似
```

```text
所有图表接口的返回值结构相同
前端用统一的 ChartPoint 类型接收
扩展新的图表接口时只需在 charts.ts 中添加函数
```

## 12. 仪表盘图表渲染（ChartsPanel.vue）

仪表盘有 3 个图表，在 `ChartsPanel.vue` 中渲染：

```text
┌──────────┐  ┌──────────┐  ┌──────────┐
│ 各区县    │  │ 运营商    │  │ 充电桩    │
│ 站点数量  │  │ 市场占比  │  │ 类型分布  │
│ (柱状图)  │  │ (环形饼图) │  │ (横向柱状)│
└──────────┘  └──────────┘  └──────────┘
```

数据加载：

```typescript
async function loadCharts() {
  const [cityData, operatorData, typeData] = await Promise.all([
    getStationsByCityChart(),
    getOperatorShareChart(),
    getStationTypeDistributionChart(),
  ])
  // 分别渲染三个图表
  renderCityChart(cityData)
  renderOperatorChart(operatorData)
  renderTypeChart(typeData)
}
```

柱状图配置要点：

```text
tooltip 显示站点数和占比百分比
label 在柱子上方显示具体数值
渐变色填充每个柱子（不同颜色）
```

环形饼图配置要点：

```text
radius: ['38%', '68%'] 产生环形效果
label 显示百分比数值
legend 在底部显示图例
```

横向柱状图配置要点：

```text
xAxis type: 'value'  水平方向是数值
yAxis type: 'category' 垂直方向是分类
label 显示在柱子右侧
```

## 13. 数据总览图表渲染（DataOverviewView.vue）

数据总览有 6 个图表，使用统一的 `buildOption` 函数生成配置：

```typescript
function buildOption(key: string, data: ChartPoint[], zoom: boolean) {
  const fs = zoom ? 13 : 11    // 放大时字体变大
  if (['c1', 'c4'].includes(key)) {
    return { /* 柱状图配置 */ }
  }
  if (key === 'c2') {
    return { /* 饼图配置 */ }
  }
  if (key === 'c3') {
    return { /* 支付方式饼图（品牌色）配置 */ }
  }
  // 带单位柱状图配置（c5=元，c6=kWh）
}
```

```text
6个图表共用一个 buildOption 函数
zoom=true 时适配大屏显示（字体和间距放大1.3倍）
每个图表通过 key 区分图表类型
```

## 14. 放大图表功能

每个图表卡片右上角都有一个放大按钮：

```text
点击按钮 → openZoom(key)
  ↓
el-dialog 打开 (width: 85%, top: 4vh)
  ↓
@opened 事件触发 → handleZoomOpened()
  ↓
setTimeout(200ms) 等待布局完成
  ↓
echarts.init(zoomChartRef) → setOption(zoom=true)
```

```text
放大后的图表字体从 11px → 13px
间距从 base → base * 1.3
饼图从隐藏标签 → 显示名称标签
```

## 15. 添加新的图表接口

在 `backend/main.py` 中添加后端接口：

```python
@app.get("/api/charts/your-chart-name")
def get_your_chart():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT some_name, COUNT(*) AS count
                FROM some_table
                GROUP BY some_name
                ORDER BY count DESC;
            """)
            rows = cur.fetchall()

    return {
        "data": [
            {"name": row[0], "value": row[1]}
            for row in rows
        ]
    }
```

在 `src/api/charts.ts` 中添加前端调用：

```typescript
export async function getYourChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/your-chart-name')
  return response.data.data
}
```

在 `DataOverviewView.vue` 中添加渲染：

```typescript
// 1. 在 loadAllData 中添加对应的 catch 调用
// 2. 在 renderAllCharts 中添加渲染函数调用
```

```text
后端：添加 SQL 查询 → 返回 { data: ChartPoint[] }
前端：添加 API 函数 → 调用并渲染
框架支持任意数量的图表接口
```

## 16. 常见问题

### 16.1 图表数据为空

```text
1. 检查后端是否启动
2. 在浏览器直接访问接口地址测试
3. 检查数据库是否有数据
```

### 16.2 SQL 报错

```text
1. 检查表名是否正确（charging_system.xxx）
2. 检查字段名是否存在
3. 检查 GROUP BY 字段是否完整
```

### 16.3 类型重复

```text
问题：GROUP BY cs.spec_id, cs.type_name
解决：改为 GROUP BY cs.type_name
原因：多个 spec_id 可能对应相同 type_name
```

## 17. 实验报告可用描述

可以在实验报告中写：

```text
图表统计模块采用后端 SQL 聚合查询的方式实现，所有图表数据来自 PostgreSQL 数据库的实时统计，而非前端样本数据。系统共提供 7 个图表统计接口，统一返回 name/value 格式的数据。

仪表盘使用 3 个图表展示详细统计，包括各区县站点数量柱状图（含占比百分比）、运营商市场占比环形饼图（含百分比标签）、充电桩类型分布横向柱状图。数据总览页面使用 6 个整体图表覆盖更多分析维度，新增了支付方式分布、平均充电费用和平均充电电量等分析维度。图表渲染使用 ECharts 库，通过线性渐变配色提升视觉效果，每个图表配有放大按钮可全屏查看。
```
