from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import os

doc = Document()

# ── 全局样式 ──
style = doc.styles['Normal']
style.font.name = 'Microsoft YaHei'
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
style.paragraph_format.line_spacing = 1.5

for level in range(1, 4):
    hs = doc.styles[f'Heading {level}']
    hs.font.name = 'Microsoft YaHei'
    hs.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    hs.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

# ── 封面 ──
for _ in range(4):
    doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('城市充电桩信息查询系统')
run.font.size = Pt(28)
run.bold = True
run.font.color.rgb = RGBColor(0x10, 0xB9, 0x81)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('实验报告')
run.font.size = Pt(22)
run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

doc.add_paragraph()

info_items = [
    ('课  程', '数据库原理及应用'),
    ('技术栈', 'PostgreSQL + FastAPI + Vue 3 + TypeScript'),
    ('UI框架', 'Element Plus + ECharts'),
    ('日  期', '2026年5月'),
]
for label, value in info_items:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f'{label}：{value}')
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

doc.add_page_break()

# ── 目录 ──
doc.add_heading('目  录', level=1)
toc_items = [
    '一、实验目的',
    '二、系统架构',
    '三、项目目录结构',
    '四、数据库设计',
    '五、后端 API 设计',
    '六、前端 UI 设计',
    '七、页面展示',
    '八、系统运行说明',
    '九、总结与收获',
]
for item in toc_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(4)

doc.add_page_break()

# ── 一、实验目的 ──
doc.add_heading('一、实验目的', level=1)
purposes = [
    '掌握 PostgreSQL 数据库设计与数据导入流程',
    '掌握 FastAPI 后端框架的 RESTful API 开发',
    '掌握 Vue 3 + TypeScript 前端框架的组件化开发',
    '掌握 ECharts 数据可视化与 Element Plus UI 组件库的使用',
    '理解前后端分离架构与数据交互流程',
    '掌握前端项目目录结构的合理规划与组件拆分',
]
for p in purposes:
    doc.add_paragraph(p, style='List Number')

# ── 二、系统架构 ──
doc.add_heading('二、系统架构', level=1)

doc.add_heading('2.1 整体技术栈', level=2)
table = doc.add_table(rows=6, cols=2, style='Light Shading Accent 1')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
data = [
    ('层级', '技术选型'),
    ('前端框架', 'Vue 3 (Composition API)'),
    ('UI 组件库', 'Element Plus'),
    ('数据可视化', 'ECharts'),
    ('后端框架', 'FastAPI (Python)'),
    ('数据库', 'PostgreSQL (psycopg)'),
]
for i, (k, v) in enumerate(data):
    table.rows[i].cells[0].text = k
    table.rows[i].cells[1].text = v

doc.add_heading('2.2 数据流程', level=2)
flow_text = (
    'CSV 原始数据 (public/data/*.csv)\n'
    '    ↓ scripts/csv_to_json.py\n'
    'JSON 中间文件 (public/data_json/*.json)\n'
    '    ↓ scripts/import_json_to_db.py\n'
    'PostgreSQL 数据库 (car_charging_db.charging_system)\n'
    '    ↓ FastAPI 后端 (backend/main.py) — 11+ 个 RESTful API\n'
    '    ↓ Axios HTTP 请求层 (src/api/*.ts)\n'
    '    ↓ Vue 3 前端组件渲染'
)
p = doc.add_paragraph()
run = p.add_run(flow_text)
run.font.size = Pt(10)

# ── 三、项目目录结构 ──
doc.add_heading('三、项目目录结构', level=1)
dir_text = """vue-carcharging/
├── backend/
│   ├── main.py                    # FastAPI 后端（15个API端点）
│   └── database.py                # PostgreSQL 连接
├── public/data/                   # CSV原始数据
├── public/data_json/              # JSON转换文件
├── scripts/
│   ├── csv_to_json.py             # CSV→JSON
│   └── import_json_to_db.py       # JSON→PostgreSQL
├── src/                           # Vue 3 前端
│   ├── api/                       # 7个API请求模块
│   │   ├── http.ts                # Axios实例
│   │   ├── cities/operators/...   # 实体接口
│   │   └── charts.ts              # 8个图表接口
│   ├── assets/styles/variables.css# CSS变量设计系统
│   ├── components/
│   │   ├── layout/                # AppLayout + Sidebar
│   │   ├── dashboard/             # SummaryCards + ChartsPanel
│   │   ├── stations/              # 查询/结果/详情弹窗
│   │   └── records/               # 查询/结果/详情弹窗
│   ├── views/
│   │   ├── DashboardView.vue      # 仪表盘(/)
│   │   └── DataOverviewView.vue   # 数据总览(/overview)
│   ├── router/index.ts            # 双路由配置
│   ├── stores/app.ts              # Pinia状态管理
│   ├── App.vue                    # 轻量根组件(7行)
│   └── main.ts                    # 应用入口
├── index.html
├── vite.config.ts
└── package.json"""
p = doc.add_paragraph()
run = p.add_run(dir_text)
run.font.size = Pt(9)

# ── 四、数据库设计 ──
doc.add_heading('四、数据库设计', level=1)

doc.add_heading('4.1 数据表', level=2)
table = doc.add_table(rows=7, cols=3, style='Light Shading Accent 1')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
db_data = [
    ('表名', '说明', '记录数'),
    ('cities', '赣州市各区县', '8行'),
    ('operators', '充电运营商', '5行'),
    ('charger_specs', '充电桩规格', '5行'),
    ('stations', '充电站', '2,402行'),
    ('users', '用户信息', '500行'),
    ('charging_records', '充电记录', '1,000行'),
]
for i, row_data in enumerate(db_data):
    for j, val in enumerate(row_data):
        table.rows[i].cells[j].text = val

doc.add_heading('4.2 表关系', level=2)
p = doc.add_paragraph('cities ──┐')
p = doc.add_paragraph('         │ 1:N')
p = doc.add_paragraph('stations ┼── city_id')
p = doc.add_paragraph('         ├── operator_id ──── operators')
p = doc.add_paragraph('         └── spec_id ──────── charger_specs')
doc.add_paragraph('charging_records ── user_id ──── users')
doc.add_paragraph('                 ── station_id ── stations')

# ── 五、后端 API ──
doc.add_heading('五、后端 API 设计', level=1)
table = doc.add_table(rows=16, cols=3, style='Light Shading Accent 1')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
api_data = [
    ('方法', '端点', '说明'),
    ('GET', '/api/health', '健康检查'),
    ('GET', '/api/cities', '城市列表'),
    ('GET', '/api/operators', '运营商列表'),
    ('GET', '/api/charger-specs', '充电桩规格'),
    ('GET', '/api/stations', '充电站列表(筛选)'),
    ('GET', '/api/stations/{id}', '充电站详情'),
    ('GET', '/api/records', '充电记录列表(筛选)'),
    ('GET', '/api/records/{id}', '充电记录详情'),
    ('GET', '/api/charts/stations-by-city', '各区县站点数'),
    ('GET', '/api/charts/operator-share', '运营商占比'),
    ('GET', '/api/charts/station-type-distribution', '充电桩类型分布'),
    ('GET', '/api/charts/payment-method-distribution', '支付方式分布'),
    ('GET', '/api/charts/records-by-city', '充电记录-按区县'),
    ('GET', '/api/charts/avg-cost-by-city', '平均充电费用'),
    ('GET', '/api/charts/avg-energy-by-city', '平均充电电量'),
]
for i, row_data in enumerate(api_data):
    for j, val in enumerate(row_data):
        table.rows[i].cells[j].text = val

# ── 六、前端 UI 设计 ──
doc.add_heading('六、前端 UI 设计', level=1)

doc.add_heading('6.1 配色方案', level=2)
table = doc.add_table(rows=7, cols=3, style='Light Shading Accent 1')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
color_data = [
    ('用途', '色值', '说明'),
    ('主色 (Primary)', '#10b981', '翠绿，代表新能源'),
    ('侧边栏背景', '#0f172a', '深蓝，沉稳科技感'),
    ('辅色 (Secondary)', '#3b82f6', '蓝色，用于折线图'),
    ('强调色 (Accent)', '#f59e0b', '橙色，用于标签'),
    ('页面背景', '#f1f5f9', '浅灰，干净清爽'),
    ('卡片背景', '#ffffff', '纯白，内容突出'),
]
for i, row_data in enumerate(color_data):
    for j, val in enumerate(row_data):
        table.rows[i].cells[j].text = val

doc.add_heading('6.2 页面结构', level=2)

doc.add_heading('仪表盘页面 (/)', level=3)
dash_items = [
    '顶部：标题 + 快捷查询按钮组（充电站/充电记录）',
    '概览统计卡片（4个）：充电站2,402 / 记录1,000 / 用户500 / 运营商5',
    '3个ECharts详细图表：各区县站点柱状图(含占比)、运营商环形饼图(含百分比)、充电桩类型横向柱状图',
]
for item in dash_items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('数据总览页面 (/overview)', level=3)
overview_items = [
    '顶部：全维度统计数值（充电站/记录/城市/运营商）',
    '6个ECharts整体图表：站点分布、运营商占比、支付方式分布、充电记录分布、平均费用、平均电量',
    '数据表格：运营商信息、充电桩规格、站点样本、记录样本',
]
for item in overview_items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('6.3 组件拆分', level=2)
p = doc.add_paragraph('原有 App.vue（574行单文件）重构为12个独立组件：')
comp_text = """1. AppLayout.vue — 全局布局框架
2. Sidebar.vue — 深色侧边导航栏
3. SummaryCards.vue — 概览统计卡片
4. ChartsPanel.vue — 仪表盘3图表
5. StationQueryDialog.vue — 充电站查询弹窗
6. StationResultsDialog.vue — 充电站结果表格
7. StationDetailDialog.vue — 充电站详情
8. RecordQueryDialog.vue — 充电记录查询弹窗
9. RecordResultsDialog.vue — 充电记录结果表格
10. RecordDetailDialog.vue — 充电记录详情
11. DashboardView.vue — 仪表盘视图
12. DataOverviewView.vue — 数据总览视图"""
p = doc.add_paragraph()
run = p.add_run(comp_text)
run.font.size = Pt(10)

# ── 七、页面展示 ──
doc.add_heading('七、页面展示', level=1)
doc.add_paragraph('以下为系统关键页面的截图展示，请在运行后截图并插入对应位置。')

pages = [
    ('7.1 仪表盘页面', 'screenshot-dashboard.png', '显示侧边栏、概览卡片、3个ECharts图表'),
    ('7.2 数据总览页面', 'screenshot-overview.png', '显示6个整体图表、数据表格'),
    ('7.3 充电站查询弹窗', 'screenshot-query.png', '城市/运营商/关键词筛选'),
    ('7.4 查询结果表格', 'screenshot-results.png', '站点名称/城市/运营商/类型/功率'),
    ('7.5 充电站详情弹窗', 'screenshot-detail.png', '16个字段详尽展示'),
]
for title, fname, desc in pages:
    doc.add_heading(title, level=2)
    doc.add_paragraph(f'文件：{fname}')
    doc.add_paragraph(f'说明：{desc}')
    p = doc.add_paragraph()
    run = p.add_run(f'[请在此处插入 {fname} 截图]')
    run.font.color.rgb = RGBColor(0xEF, 0x44, 0x44)
    run.italic = True

# ── 八、系统运行说明 ──
doc.add_heading('八、系统运行说明', level=1)

doc.add_heading('8.1 环境要求', level=2)
env_items = ['Node.js >= 18', 'Python >= 3.10', 'PostgreSQL >= 14']
for item in env_items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('8.2 启动步骤', level=2)
steps = [
    ('数据库初始化', 'CREATE DATABASE car_charging_db;\nCREATE SCHEMA charging_system;'),
    ('数据导入', 'python scripts/csv_to_json.py\npython scripts/import_json_to_db.py'),
    ('启动后端', '.venv\\Scripts\\activate\nuvicorn backend.main:app --reload'),
    ('启动前端', 'npm run dev'),
    ('生产构建', 'npm run build'),
]
for title, cmd in steps:
    p = doc.add_paragraph()
    r = p.add_run(f'{title}：')
    r.bold = True
    p2 = doc.add_paragraph()
    run = p2.add_run(cmd)
    run.font.size = Pt(10)

# ── 九、总结 ──
doc.add_heading('九、总结与收获', level=1)
summaries = [
    '前后端分离架构：理解 FastAPI + Vue 3 的完整数据交互流程，掌握 RESTful API 设计与调用',
    '组件化开发：将 574 行单文件拆分为 12 个独立组件，提升可维护性和可复用性',
    '数据可视化：使用 ECharts 实现柱状图、环形饼图、横向柱状图等多种图表类型，并自行编写后端聚合查询SQL',
    'UI 框架应用：熟练使用 Element Plus 的 Dialog、Table、Form、Descriptions、Menu 等组件',
    'CSS 设计系统：建立 CSS 变量体系实现统一配色，翠绿+深蓝配色方案体现新能源科技感',
    '数据库操作：掌握 PostgreSQL 建表、CSV 导入、JSON 转换、GROUP BY 聚合查询等全流程',
    '问题排查：修复了图标名称错误、模板 ref 绑定失效、Promise.all 异常处理、SQL 重复分组等多个实际开发问题',
]
for s in summaries:
    doc.add_paragraph(s, style='List Number')

# ── 保存 ──
output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', '实验报告.docx')
doc.save(output_path)
print(f'实验报告已生成: {output_path}')
