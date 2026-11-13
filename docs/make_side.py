# -*- coding: utf-8 -*-
"""把三张界面截图拼成一张横排图，供报告排版用（节省纵向空间）。"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
GAP = 18
BG = (255, 255, 255)

names = ["screenshot_index.png", "screenshot_detail.png", "screenshot_validation.png"]
items = []
for n in names:
    im = Image.open(os.path.join(BASE, n)).convert("RGB")
    items.append(im)

W = sum(i.width for i in items) + GAP * (len(items) - 1)
H = max(i.height for i in items)
canvas = Image.new("RGB", (W, H), BG)
x = 0
for im in items:
    canvas.paste(im, (x, 0))
    x += im.width + GAP
canvas.save(os.path.join(BASE, "_side.png"), optimize=True)
print("side:", canvas.size)