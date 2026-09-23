import os
from docx import Document
from docx.shared import Inches
from io import BytesIO
import xml.etree.ElementTree as ET

# ── 生成 E-R 图 SVG ──
svg_code = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 720" width="900" height="720">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/>
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%">
      <feDropShadow dx="1" dy="2" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
    <linearGradient id="g1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#10b981"/>
      <stop offset="100%" style="stop-color:#059669"/>
    </linearGradient>
    <linearGradient id="g2" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6"/>
      <stop offset="100%" style="stop-color:#2563eb"/>
    </linearGradient>
    <linearGradient id="g3" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#8b5cf6"/>
      <stop offset="100%" style="stop-color:#7c3aed"/>
    </linearGradient>
    <linearGradient id="g4" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#f59e0b"/>
      <stop offset="100%" style="stop-color:#d97706"/>
    </linearGradient>
    <linearGradient id="g5" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ef4444"/>
      <stop offset="100%" style="stop-color:#dc2626"/>
    </linearGradient>
    <linearGradient id="g6" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ec4899"/>
      <stop offset="100%" style="stop-color:#db2777"/>
    </linearGradient>
  </defs>

  <!-- 背景 -->
  <rect width="900" height="720" fill="#f8fafc" rx="8"/>

  <!-- 标题 -->
  <text x="450" y="38" text-anchor="middle" font-family="Microsoft YaHei" font-size="20" font-weight="bold" fill="#0f172a">数据库 E-R 模型图</text>
  <line x1="200" y1="50" x2="700" y2="50" stroke="#e2e8f0" stroke-width="1"/>

  <!-- ====== 实体1：cities ====== -->
  <g filter="url(#shadow)">
    <rect x="320" y="72" width="240" height="38" rx="6" fill="url(#g1)"/>
    <text x="440" y="97" text-anchor="middle" font-family="Microsoft YaHei" font-size="15" font-weight="bold" fill="#fff">cities (城市)</text>
    <rect x="320" y="110" width="240" height="22" rx="0" fill="#d1fae5"/>
    <text x="334" y="126" font-family="monospace" font-size="11" fill="#059669">PK city_id, city_name, population</text>
  </g>

  <!-- ====== 实体2：operators ====== -->
  <g filter="url(#shadow)">
    <rect x="32" y="280" width="250" height="38" rx="6" fill="url(#g3)"/>
    <text x="157" y="305" text-anchor="middle" font-family="Microsoft YaHei" font-size="15" font-weight="bold" fill="#fff">operators (运营商)</text>
    <rect x="32" y="318" width="250" height="22" rx="0" fill="#f3e8ff"/>
    <text x="46" y="334" font-family="monospace" font-size="11" fill="#7c3aed">PK operator_id, operator_name</text>
  </g>

  <!-- ====== 实体3：charger_specs ====== -->
  <g filter="url(#shadow)">
    <rect x="32" y="480" width="250" height="38" rx="6" fill="url(#g4)"/>
    <text x="157" y="505" text-anchor="middle" font-family="Microsoft YaHei" font-size="15" font-weight="bold" fill="#fff">charger_specs (规格)</text>
    <rect x="32" y="518" width="250" height="22" rx="0" fill="#fef3c7"/>
    <text x="46" y="534" font-family="monospace" font-size="11" fill="#d97706">PK spec_id, type_name, power_kw</text>
  </g>

  <!-- ====== 实体4：stations ====== -->
  <g filter="url(#shadow)">
    <rect x="280" y="280" width="320" height="38" rx="6" fill="url(#g2)"/>
    <text x="440" y="305" text-anchor="middle" font-family="Microsoft YaHei" font-size="15" font-weight="bold" fill="#fff">stations (充电站)</text>
    <rect x="280" y="318" width="320" height="38" rx="0" fill="#dbeafe"/>
    <text x="294" y="334" font-family="monospace" font-size="11" fill="#2563eb">PK station_id, station_name, address, phone</text>
    <text x="294" y="348" font-family="monospace" font-size="11" fill="#2563eb">FK city_id, FK operator_id, FK spec_id</text>
  </g>

  <!-- ====== 实体5：users ====== -->
  <g filter="url(#shadow)">
    <rect x="600" y="480" width="250" height="38" rx="6" fill="url(#g5)"/>
    <text x="725" y="505" text-anchor="middle" font-family="Microsoft YaHei" font-size="15" font-weight="bold" fill="#fff">users (用户)</text>
    <rect x="600" y="518" width="250" height="22" rx="0" fill="#fee2e2"/>
    <text x="614" y="534" font-family="monospace" font-size="11" fill="#dc2626">PK user_id, username, phone</text>
  </g>

  <!-- ====== 实体6：charging_records ====== -->
  <g filter="url(#shadow)">
    <rect x="530" y="648" width="300" height="38" rx="6" fill="url(#g6)"/>
    <text x="680" y="673" text-anchor="middle" font-family="Microsoft YaHei" font-size="15" font-weight="bold" fill="#fff">charging_records (充电记录)</text>
    <rect x="530" y="686" width="300" height="22" rx="0" fill="#fce7f3"/>
    <text x="544" y="702" font-family="monospace" font-size="11" fill="#db2777">PK record_id, energy_kwh, cost_yuan</text>
  </g>

  <!-- ====== 连线：cities → stations ====== -->
  <line x1="440" y1="148" x2="440" y2="280" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="430" y="165" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#10b981">1</text>
  <text x="430" y="270" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#3b82f6">N</text>
  <text x="450" y="220" font-family="Microsoft YaHei" font-size="12" fill="#64748b">city_id</text>

  <!-- ====== 连线：operators → stations ====== -->
  <line x1="282" y1="310" x2="282" y2="340" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="282" y1="340" x2="395" y2="340" stroke="#64748b" stroke-width="2"/>
  <polygon points="395,334 405,340 395,346" fill="#64748b"/>
  <text x="282" y="300" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#8b5cf6">1</text>
  <text x="395" y="350" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#3b82f6">N</text>
  <text x="310" y="338" font-family="Microsoft YaHei" font-size="12" fill="#64748b">operator_id</text>

  <!-- ====== 连线：charger_specs → stations ====== -->
  <line x1="282" y1="510" x2="282" y2="356" stroke="#64748b" stroke-width="2"/>
  <line x1="282" y1="356" x2="395" y2="356" stroke="#64748b" stroke-width="2"/>
  <polygon points="395,350 405,356 395,362" fill="#64748b"/>
  <text x="256" y="440" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#f59e0b">1</text>
  <text x="395" y="366" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#3b82f6">N</text>
  <text x="310" y="354" font-family="Microsoft YaHei" font-size="12" fill="#64748b">spec_id</text>

  <!-- ====== 连线：users → charging_records ====== -->
  <line x1="725" y1="520" x2="725" y2="648" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="715" y="540" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#ef4444">1</text>
  <text x="715" y="640" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#ec4899">N</text>
  <text x="735" y="590" font-family="Microsoft YaHei" font-size="12" fill="#64748b">user_id</text>

  <!-- ====== 连线：stations → charging_records ====== -->
  <line x1="600" y1="356" x2="710" y2="648" stroke="#64748b" stroke-width="2"/>
  <polygon points="712,638 718,648 706,648" fill="#64748b"/>
  <text x="590" y="440" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#3b82f6">1</text>
  <text x="720" y="640" font-family="Microsoft YaHei" font-size="12" font-weight="bold" fill="#ec4899">N</text>
  <text x="632" y="510" font-family="Microsoft YaHei" font-size="12" fill="#64748b">station_id</text>

  <!-- 图例 -->
  <rect x="70" y="585" width="14" height="14" rx="3" fill="#d1fae5" stroke="#10b981"/>
  <text x="90" y="597" font-family="Microsoft YaHei" font-size="11" fill="#475569">PK = 主键</text>
  <rect x="170" y="585" width="14" height="14" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
  <text x="190" y="597" font-family="Microsoft YaHei" font-size="11" fill="#475569">FK = 外键</text>
</svg>'''

svg_path = 'd:\\城市充电桩信息查询系统\\vue-carcharging\\docs\\er_diagram.svg'
with open(svg_path, 'w', encoding='utf-8') as f:
    f.write(svg_code)

# ── 插入到 DOCX ──
docx_path = 'd:\\城市充电桩信息查询系统\\vue-carcharging\\docs\\实验报告.docx'
doc = Document(docx_path)

# 找到 "4.2 表关系" 所在的段落索引，替换其后的文本内容
target_heading = None
for p in doc.paragraphs:
    if '4.2 表关系' in p.text:
        target_heading = p
        break

if target_heading:
    # 找到 heading 之后的所有文本段落，清空它们
    in_section = False
    paragraphs_to_remove = []
    for p in doc.paragraphs:
        if p.text.startswith('4.2 表关系'):
            in_section = True
            continue
        if in_section:
            if p.style.name.startswith('Heading'):
                break
            # 清空这些段落
            p.text = ''

# 在文档末尾添加图片
p = doc.add_paragraph()
p.alignment = 1  # center
run = p.add_run()
run.add_picture(svg_path, width=Inches(5.5))

doc.save(docx_path)
print(f'已插入 E-R 图到 {docx_path}')
