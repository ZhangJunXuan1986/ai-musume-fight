# -*- coding: utf-8 -*-
"""改了游戏里的中文文案后，重新生成 assets/font.ttf。

浏览器不认识操作系统字体，所有文字必须来自打包进来的字体文件。
为了不让首屏下载十几 MB，这里只保留源码里实际出现过的字符（子集化）。

重要：字体必须同时覆盖中文和 UI 用的箭头/圆点符号（▲▼◀▶ █ · …）。
像 DroidSansFallback 这类「中文够用但符号缺一堆」的字体，会让按钮显示成方块，
所以本脚本会逐个尝试候选字体并校验覆盖率，选不到合适的就明确报错。

用法：
    python tools/make_font.py                       # 自动在常见路径找字体
    python tools/make_font.py /path/to/your.ttf    # 指定任意含中文的 TTF/TTC

需要：pip install fonttools
"""
import io
import os
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "game", "main.py")
OUT = os.path.join(ROOT, "game", "assets", "font.ttf")

# 顺序有讲究：CJK 字体通常也带几何符号，纯 fallback 字体往往不带。
SEARCH = [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/**/*CJK*",
    "/usr/share/fonts/**/*Hei*.tt[fc]",
    "/usr/share/fonts/truetype/misans/MiSans-Normal.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # 兜底，符号可能缺
]

# 运行时必须能显示的最小符号集（主要来自虚拟按键标签与 HUD）
MUST_HAVE = "▲▼◀▶█·：「」（）【】、。！？—…／｜×°"


def candidates():
    if len(sys.argv) > 1:
        return [sys.argv[1]]
    out = []
    for pat in SEARCH:
        for p in glob.glob(pat, recursive=True):
            if os.path.isfile(p) and p not in out:
                out.append(p)
    return out


def build(src_font, text):
    from fontTools.ttLib import TTFont
    from fontTools import subset
    f = TTFont(src_font, fontNumber=1 if src_font.endswith(".ttc") else 0)
    opt = subset.Options()
    opt.name_IDs = ["*"]
    opt.notdef_outline = True
    opt.recalc_bounds = True
    sub = subset.Subsetter(options=opt)
    sub.populate(text=text)
    sub.subset(f)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    f.save(OUT)
    # 校验：生成后的 cmap 必须包含所有必要符号和足够多的汉字
    chk = TTFont(OUT, lazy=True)
    cmap = chk.getBestCmap() or {}
    missing = [c for c in MUST_HAVE if ord(c) not in cmap]
    han = [c for c in cmap if 0x4E00 <= c <= 0x9FFF]
    chk.close()
    return missing, len(han)


def main():
    text = set(io.open(SRC, "r", encoding="utf-8").read())
    text.update("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    text.update(" .:/-_()[]{}%#*+=<>|!?,;:'\"@&~^$\\`")
    text.update(MUST_HAVE)
    text = "".join(sorted(c for c in text if ord(c) >= 32))

    tried = []
    for src_font in candidates():
        try:
            missing, han = build(src_font, text)
        except Exception as e:
            tried.append("  %s -> 构建失败 %s" % (src_font, type(e).__name__))
            continue
        if not missing and han >= 200:
            print("已生成 %s（%.1f KB，%d 个字符，%d 个汉字）" %
                  (OUT, os.path.getsize(OUT) / 1024, len(text), han))
            print("来源字体：%s" % src_font)
            print("必要符号：全部覆盖")
            return 0
        tried.append("  %s -> 缺符号 %s / 汉字 %d" %
                     (src_font, "".join(missing) or "无", han))

    print("没有找到覆盖全部必要符号的字体。已尝试：")
    for t in tried:
        print(t)
    print("\n请显式指定一个带中文和几何符号的字体：")
    print("  python tools/make_font.py /path/to/NotoSansCJK-Regular.ttc")
    return 1


if __name__ == "__main__":
    sys.exit(main())
