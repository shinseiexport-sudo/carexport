#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""img/ の元画像から、サイト表示用にリサイズした画像を web/ へ書き出します。

使い方:
    python3 make_images.py

必要環境: Python 3 / Pillow (pip install pillow)
アスペクト比は保ったまま、はみ出した分を中央で切り落として（cover方式）歪みを出しません。
"""

import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "img")
DST = os.path.join(HERE, "web")

# (元ファイル, 出力ファイル, 幅, 高さ)
JOBS = [
    ("hero-factory.jpg", "hero-factory-1440.jpg", 1440, 810),  # トップ：ヘッダー直下の横長 16:9
    ("port.jpg",         "port-1440.jpg",         1440, 810),  # 輸出先：ページ見出し直下の横長 16:9
    ("engine.jpg",       "engine-900.jpg",         900, 675),  # トップ：エンジン 4:3
    ("container.jpg",    "container-900.jpg",      900, 675),  # トップ：コンテナ 4:3
    ("loading.jpg",      "loading-900.jpg",        900, 675),  # トップ：積み込み 4:3
]


def cover(im, w, h):
    """比率を保って拡大縮小し、余った部分を中央基準で切り落として w x h に揃える。"""
    sw, sh = im.size
    s = max(w / sw, h / sh)
    nw, nh = round(sw * s), round(sh * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def main():
    if not os.path.isdir(SRC):
        raise SystemExit("img/ が見つかりません: %s" % SRC)
    os.makedirs(DST, exist_ok=True)
    for name, out, w, h in JOBS:
        path = os.path.join(SRC, name)
        if not os.path.exists(path):
            print("skip (not found): %s" % name)
            continue
        im = Image.open(path).convert("RGB")
        bw, bh = im.size
        im2 = cover(im, w, h)
        im2.save(os.path.join(DST, out), "JPEG", quality=82, optimize=True, progressive=True)
        print("%s %dx%d -> %s %dx%d" % (name, bw, bh, out, w, h))
    print("done: %s" % DST)


if __name__ == "__main__":
    main()
