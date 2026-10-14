#!/usr/bin/env bash
# サイトを再生成します: img/ (元画像) -> web/ (表示用画像) -> site/ (HTML一式)
#
# 使い方:
#   bash build.sh
#
# 出力: site/  index.html, about.html, ..., ja/ (日本語), img/ (表示用画像),
#             robots.txt, sitemap.xml
set -e
cd "$(dirname "$0")"

echo "[1/2] 表示用の画像を書き出します (img/ -> web/)"
python3 make_images.py

echo "[2/2] HTMLを生成します (build/ -> site/)"
python3 build/site.py

echo "完了: site/ に出力しました"
