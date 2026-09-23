from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (900, 720), '#f8fafc')
draw = ImageDraw.Draw(img)

gray = '#64748b'
light_gray = '#e2e8f0'
white = '#ffffff'

font_path = 'C:/Windows/Fonts/msyh.ttc'
font_mono_path = 'C:/Windows/Fonts/consola.ttf'
font_title = ImageFont.truetype(font_path, 20)
font_header = ImageFont.truetype(font_path, 15)
font_text = ImageFont.truetype(font_path, 12)
font_mono = ImageFont.truetype(font_mono_path, 12)
font_tag = ImageFont.truetype(font_path, 11)

draw.text((450, 15), '数据库 E-R 模型图', fill='#0f172a', font=font_title, anchor='mt')
draw.line([(200, 40), (700, 40)], fill=light_gray, width=1)

def draw_box(x, y, w, h, name, top_color, bottom_color, light, fields):
    for yi in range(y, y + 22):
        r = int(int(top_color[1:3],16)*(1-(yi-y)/22)+int(bottom_color[1:3],16)*((yi-y)/22))
        g = int(int(top_color[3:5],16)*(1-(yi-y)/22)+int(bottom_color[3:5],16)*((yi-y)/22))
        b = int(int(top_color[5:7],16)*(1-(yi-y)/22)+int(bottom_color[5:7],16)*((yi-y)/22))
        draw.line([(x, yi), (x+w, yi)], fill=(r, g, b))
    draw.rectangle([x, y+22, x+w, y+h], fill=light, outline=gray, width=1)
    draw.text((x+w//2, y+11), name, fill=white, font=font_header, anchor='mt')
    for i, f in enumerate(fields):
        draw.text((x+8, y+27+i*16), f, fill=gray, font=font_mono)

draw_box(320, 65, 240, 48, 'cities (城市)', '#10b981', '#059669', '#d1fae5', ['PK city_id, city_name, ...'])
draw_box(30, 270, 260, 48, 'operators (运营商)', '#8b5cf6', '#7c3aed', '#f3e8ff', ['PK operator_id, ...'])
draw_box(30, 470, 260, 48, 'charger_specs (规格)', '#f59e0b', '#d97706', '#fef3c7', ['PK spec_id, type_name, ...'])
draw_box(280, 270, 340, 60, 'stations (充电站)', '#3b82f6', '#2563eb', '#dbeafe', ['PK station_id, name, addr', 'FK city/operator/spec_id'])
draw_box(600, 470, 260, 48, 'users (用户)', '#ef4444', '#dc2626', '#fee2e2', ['PK user_id, username, ...'])
draw_box(530, 640, 320, 48, 'charging_records', '#ec4899', '#db2777', '#fce7f3', ['PK record_id, energy, cost'])
draw.text((690, 648), '(充电记录)', fill=gray, font=font_text)

import math
def arrow(x1, y1, x2, y2, c, l1='', l2='', mid='', mx=0, my=0):
    draw.line([(x1, y1), (x2, y2)], fill=c, width=2)
    a = math.atan2(y2-y1, x2-x1)
    draw.polygon([(x2,y2),(x2-8*math.cos(a-0.4),y2-8*math.sin(a-0.4)),(x2-8*math.cos(a+0.4),y2-8*math.sin(a+0.4))], fill=gray)
    if l1: draw.text((x1, y1-14), l1, fill=c, font=font_text, anchor='mb')
    if l2: draw.text((x2, y2+4), l2, fill=c, font=font_text, anchor='mt')
    if mid and mx and my: draw.text((mx, my), mid, fill='#475569', font=font_text)

arrow(440, 113, 440, 270, '#10b981', '1', 'N', 'city_id', 450, 200)
draw.line([(290, 294), (290, 330), (370, 330)], fill=gray, width=2)
arrow(370, 330, 395, 330, gray, '', '', 'operator_id', 310, 328)
draw.line([(290, 494), (290, 360), (370, 360)], fill=gray, width=2)
arrow(370, 360, 395, 360, gray, '', '', 'spec_id', 310, 358)
arrow(730, 518, 730, 640, '#ef4444', '1', 'N', 'user_id', 740, 580)
draw.line([(620, 330), (700, 640)], fill=gray, width=2)

draw.rectangle([60, 560, 74, 574], fill='#d1fae5', outline='#10b981')
draw.text((80, 566), 'PK = 主键', fill='#475569', font=font_tag)
draw.rectangle([200, 560, 214, 574], fill='#dbeafe', outline='#3b82f6')
draw.text((220, 566), 'FK = 外键', fill='#475569', font=font_tag)

op = 'd:\\城市充电桩信息查询系统\\vue-carcharging\\docs\\er_diagram.png'
img.save(op)
print('ER diagram saved:', op)
