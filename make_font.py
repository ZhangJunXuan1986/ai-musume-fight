# -*- coding: utf-8 -*-
"""改了游戏里的中文文案后，重新生成 assets/font.ttf。

浏览器不认识操作系统字体，所有中文必须来自打包进来的字体文件。
为了不让首屏下载十几 MB，这里只保留源码里实际出现过的字符（子集化）。

用法：
    python tools/make_font.py                       # 自动在常见路径找字体
    python tools/make_font.py /path/to/your.ttf    # 指定任意含中文的 TTF/TTC

需要：pip install fonttools pygame
"""
import io
import os
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "game", "main.py")
OUT = os.path.join(ROOT, "game", "assets", "font.ttf")

SEARCH = [
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/**/*CJK*",
    "/usr/share/fonts/**/*Hei*.tt[fc]",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]


def find_font():
    if len(sys.argv) > 1:
        return sys.argv[1]
    for pat in SEARCH:
        for p in glob.glob(pat, recursive=True):
            if os.path.isfile(p):
                return p
    return None


def main():
    src_font = find_font()
    if not src_font or not os.path.exists(src_font):
        print("找不到中文字体，请显式指定：python tools/make_font.py <字体文件>")
        return 1
    text = set(io.open(SRC, "r", encoding="utf-8").read())
    text.update("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    text.update(" .:/-_()[]{}%#*+=<>|!?,;:'\"@&~^$\\`")
    text = "".join(sorted(c for c in text if ord(c) >= 32))

    from fontTools.ttLib import TTFont
    from fontTools import subset
    f = TTFont(src_font, fontNumber=0)
    opt = subset.Options()
    opt.name_IDs = ["*"]
    opt.notdef_outline = True
    sub = subset.Subsetter(options=opt)
    sub.populate(text=text)
    sub.subset(f)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    f.save(OUT)
    print("已生成 %s（%.1f KB，%d 个字符），来源 %s" %
          (OUT, os.path.getsize(OUT) / 1024, len(text), src_font))
    return 0


if __name__ == "__main__":
    sys.exit(main())
