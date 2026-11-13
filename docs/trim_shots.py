# -*- coding: utf-8 -*-
"""把截图下方的大片空白裁掉，只留内容 + 少量留白，避免报告里图片占掉整页。"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
PAD = 14

for name in ("screenshot_index.png", "screenshot_detail.png", "screenshot_validation.png"):
    path = os.path.join(BASE, name)
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()

    def dark(x, y):
        return sum(px[x, y]) / 3 < 235

    rows = [y for y in range(h) if any(dark(x, y) for x in range(0, w, 3))]
    cols = [x for x in range(w) if any(dark(x, y) for y in range(0, h, 3))]
    if not rows or not cols:
        print("skip", name)
        continue
    box = (
        max(0, cols[0] - PAD),
        max(0, rows[0] - PAD),
        min(w, cols[-1] + PAD + 1),
        min(h, rows[-1] + PAD + 1),
    )
    out = im.crop(box)
    out.save(path, optimize=True)
    print(name, (w, h), "->", out.size)