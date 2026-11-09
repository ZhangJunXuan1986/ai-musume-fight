# -*- coding: utf-8 -*-
"""美术素材准备工具（一个脚本干完，不改 main.py）。

游戏里已经留好接口：把图片命名成 assets/<角色id>.png 就会自动替换代码绘制的 Q 版。
本脚本负责把「任何来源的图片」变成符合这个接口的规格。

依赖：pip install pillow（Termux / 电脑都行）

用法：
    # 1) 先生成 8 张占位立绘，立刻能看到「放图就变」的效果
    python tools/prepare_assets.py --placeholder

    # 2) 把相册 / AI 出图的一张图，处理成某个角色的立绘
    python tools/prepare_assets.py --from ~/storage/dcim/photo.jpg deepseek

    # 3) 批量：目录里图片文件名含角色 id 就自动匹配（如 my_deepseek.png）
    python tools/prepare_assets.py --from-dir ~/storage/pictures

    # 4) 上线前检查 8 张图是否齐全、体积是否超标
    python tools/prepare_assets.py --check

    # 5) AI 出图常带白底，加 --remove-bg 把接近纯白的像素变透明
    python tools/prepare_assets.py --from pic.png qwen --remove-bg

规格（对应 main.py 的 _try_portrait）：
    透明 PNG / 360×420 以内 / 脚底贴着图片底边 / 默认面朝右（代码会自动水平翻转）
    运行时被等比缩放到高 116px，所以 300~420 高就够，再大只是浪费首屏流量。
"""
import os
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "game", "assets")

# 与 main.py 的 CHARACTERS 一一对应；改角色名单时这里也要同步
CHARS = [
    ("deepseek", "DeepSeek 鲸鱼娘", (86, 164, 255),  (120, 220, 255)),
    ("chatgpt",  "ChatGPT 白龙娘",  (232, 236, 248), (150, 200, 255)),
    ("claude",   "Claude 小 C",     (238, 148, 66),  (255, 205, 130)),
    ("gemini",   "Gemini 猫娘",     (150, 130, 245), (110, 220, 230)),
    ("qwen",     "通义千问大小姐",   (86, 158, 226),  (245, 240, 225)),
    ("kimi",     "Kimi 月相少女",   (206, 214, 236), (120, 130, 200)),
    ("glm",      "GLM 狐狸娘",      (72, 142, 196),  (240, 226, 120)),
    ("grok",     "Grok Ani",        (240, 206, 96),  (176, 44, 62)),
]
IDS = [c[0] for c in CHARS]

MAX_W, MAX_H = 360, 420          # 立绘最大尺寸（会被缩到高 116 显示）
MAX_KB = 400                     # 单张建议上限，超过会警告
TOTAL_KB = 2400                  # 8 张总量建议上限（首屏流量）


def need_pil():
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        return Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        print("缺少 Pillow，请先执行：pip install pillow")
        sys.exit(1)


def fit_canvas(im, remove_bg=False):
    """把任意图片处理成规格：透明底 / 裁掉空边 / 等比缩放 / 脚底贴底边。"""
    Image, ImageDraw, _, ImageFilter = need_pil()
    im = im.convert("RGBA")

    if remove_bg:
        # 简单白底抠图：接近纯白且低饱和的像素 -> 全透明。
        # 只适合干净白底的 AI 出图；复杂背景请用专门的抠图工具。
        px = im.load()
        w, h = im.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a and min(r, g, b) >= 238 and (max(r, g, b) - min(r, g, b)) <= 14:
                    px[x, y] = (r, g, b, 0)

    # 裁掉四周全透明边：让角色贴着画布，脚底才会落在图片底边
    alpha = im.getchannel("A")
    bbox = alpha.getbbox()
    if bbox:
        im = im.crop(bbox)

    # 等比缩放到不超过 MAX_W × MAX_H
    w, h = im.size
    scale = min(MAX_W / float(w), MAX_H / float(h), 1.0)
    if scale < 1.0:
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))),
                       Image.LANCZOS)

    # 放到固定画布底部居中：底边 = 脚底，符合 blit(img, (cx-w/2, f.y-h))
    w, h = im.size
    canvas = Image.new("RGBA", (MAX_W, MAX_H), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((MAX_W - w) // 2, MAX_H - h))
    return canvas


def save_png(im, char_id):
    os.makedirs(ASSETS, exist_ok=True)
    out = os.path.join(ASSETS, char_id + ".png")
    im.save(out, "PNG", optimize=True)
    return out, os.path.getsize(out)


def make_placeholder():
    """生成 8 张几何占位立绘。
    用途不是当最终美术，而是让你先跑通「图片 -> assets -> 网页里生效」这条链路，
    确认流程没问题后再换成 AI 出图或手绘图。"""
    Image, ImageDraw, ImageFont, _ = need_pil()
    print("生成 8 张占位立绘 …")
    total = 0
    for idx, (cid, name, color, accent) in enumerate(CHARS):
        im = Image.new("RGBA", (MAX_W, MAX_H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx, foot = MAX_W // 2, MAX_H - 12

        # 影子
        d.ellipse((cx - 78, foot - 14, cx + 78, foot + 8), fill=(0, 0, 0, 70))
        # 裙 / 身体
        d.polygon([(cx - 52, foot - 12), (cx + 52, foot - 12),
                   (cx + 34, foot - 150), (cx - 34, foot - 150)], fill=color + (255,))
        d.rounded_rectangle((cx - 34, foot - 210, cx + 34, foot - 130),
                            radius=18, fill=accent + (255,))
        # 腿
        d.rounded_rectangle((cx - 26, foot - 40, cx - 8, foot), radius=7, fill=(245, 228, 214, 255))
        d.rounded_rectangle((cx + 8, foot - 40, cx + 26, foot), radius=7, fill=(245, 228, 214, 255))
        # 手臂
        d.rounded_rectangle((cx - 62, foot - 200, cx - 40, foot - 130), radius=10, fill=accent + (255,))
        d.rounded_rectangle((cx + 40, foot - 200, cx + 62, foot - 130), radius=10, fill=accent + (255,))
        # 头 + 眼
        hy = foot - 268
        d.ellipse((cx - 52, hy - 52, cx + 52, hy + 52), fill=(250, 232, 220, 255))
        d.ellipse((cx - 56, hy - 68, cx + 56, hy + 8), fill=color + (255,))
        d.ellipse((cx - 22, hy + 2, cx - 8, hy + 16), fill=(40, 40, 60, 255))
        d.ellipse((cx + 8, hy + 2, cx + 22, hy + 16), fill=(40, 40, 60, 255))
        d.arc((cx - 14, hy + 18, cx + 14, hy + 34), 0, 180, fill=(190, 90, 90, 255), width=3)

        # 每位角色一个几何标志物，方便一眼分辨
        if cid == "deepseek":    # 鲸尾
            d.polygon([(cx - 78, hy - 40), (cx - 106, hy - 66),
                       (cx - 96, hy - 20), (cx - 76, hy - 30)], fill=accent + (255,))
        elif cid == "chatgpt":   # 龙角
            d.polygon([(cx - 30, hy - 52), (cx - 42, hy - 96), (cx - 12, hy - 58)], fill=accent + (255,))
            d.polygon([(cx + 30, hy - 52), (cx + 42, hy - 96), (cx + 12, hy - 58)], fill=accent + (255,))
        elif cid == "claude":    # 书本
            d.rounded_rectangle((cx + 30, foot - 176, cx + 84, foot - 126),
                                radius=4, fill=(80, 60, 50, 255))
        elif cid == "gemini":    # 猫耳
            d.polygon([(cx - 48, hy - 42), (cx - 44, hy - 92), (cx - 10, hy - 56)], fill=accent + (255,))
            d.polygon([(cx + 48, hy - 42), (cx + 44, hy - 92), (cx + 10, hy - 56)], fill=accent + (255,))
        elif cid == "qwen":      # 折扇
            d.pieslice((cx - 100, foot - 240, cx - 20, foot - 160), 200, 340, fill=accent + (255,))
        elif cid == "kimi":      # 月相
            d.ellipse((cx + 46, hy - 90, cx + 100, hy - 36), fill=accent + (255,))
            d.ellipse((cx + 60, hy - 96, cx + 114, hy - 42), fill=(12, 14, 36, 255))
        elif cid == "glm":       # Z 字
            d.line((cx + 54, hy - 96, cx + 92, hy - 96), fill=accent + (255,), width=7)
            d.line((cx + 92, hy - 96, cx + 54, hy - 56), fill=accent + (255,), width=7)
            d.line((cx + 54, hy - 56, cx + 92, hy - 56), fill=accent + (255,), width=7)
        elif cid == "grok":      # 斧头
            d.line((cx + 56, foot - 230, cx + 76, foot - 96), fill=(120, 90, 70, 255), width=8)
            d.polygon([(cx + 44, foot - 238), (cx + 92, foot - 252),
                       (cx + 92, foot - 214), (cx + 44, foot - 218)], fill=accent + (255,))

        # 底部写角色 id，占位图一眼能认出对应谁
        try:
            font = ImageFont.truetype(os.path.join(ASSETS, "font.ttf"), 22)
        except Exception:
            font = ImageFont.load_default()
        d.text((cx, MAX_H - 34), cid, font=font, fill=(255, 255, 255, 220), anchor="mm")

        out, size = save_png(im, cid)
        total += size
        print("  %-10s %-18s %6.1f KB  %s" % (cid, name, size / 1024, out))
    print("占位图合计 %.1f KB" % (total / 1024))


def from_file(path, char_id, remove_bg):
    Image, _, _, _ = need_pil()
    if char_id not in IDS:
        print("未知角色 id: %s\n可用：%s" % (char_id, ", ".join(IDS)))
        return 1
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        print("找不到文件：%s" % path)
        return 1
    im = Image.open(path)
    out, size = save_png(fit_canvas(im, remove_bg), char_id)
    print("已生成 %s（%.1f KB）← %s" % (out, size / 1024, path))
    if size > MAX_KB * 1024:
        print("  警告：单张超过 %d KB，建议用更小的源图或再压一次" % MAX_KB)
    return 0


def from_dir(folder, remove_bg):
    folder = os.path.expanduser(folder)
    if not os.path.isdir(folder):
        print("找不到目录：%s" % folder)
        return 1
    hit = 0
    for fn in sorted(os.listdir(folder)):
        low = fn.lower()
        if not low.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
            continue
        matched = [cid for cid in IDS if cid in low]
        if len(matched) != 1:
            continue
        rc = from_file(os.path.join(folder, fn), matched[0], remove_bg)
        hit += (rc == 0)
    print("批量处理完成，匹配 %d 张" % hit)
    if hit == 0:
        print("提示：文件名里要含角色 id，例如 deepseek.png / my_gemini.jpg")
    return 0


def check():
    Image, _, _, _ = need_pil()
    print("检查 assets/ 立绘规格（目标 ≤%d×%d，透明 PNG，脚底贴底边）" % (MAX_W, MAX_H))
    total, missing = 0, []
    for cid, name, _, _ in CHARS:
        p = os.path.join(ASSETS, cid + ".png")
        if not os.path.exists(p):
            print("  缺失  %-10s %s" % (cid, name))
            missing.append(cid)
            continue
        im = Image.open(p)
        kb = os.path.getsize(p) / 1024
        total += kb
        alpha = im.convert("RGBA").getchannel("A")
        bbox = alpha.getbbox()
        foot_ok = bbox and bbox[3] >= im.height - 6
        flag = "OK" if (im.mode == "RGBA" and im.width <= MAX_W
                       and im.height <= MAX_H and kb <= MAX_KB and foot_ok) else "需检查"
        print("  %-6s %-10s %-18s %4d×%-4d %7.1f KB" %
              (flag, cid, name, im.width, im.height, kb))
    print("合计 %.1f KB / 建议上限 %d KB" % (total, TOTAL_KB))
    if missing:
        print("缺 %d 张；不想画图就先跑 --placeholder，游戏会照常用 Q 版" % len(missing))
    if total > TOTAL_KB:
        print("警告：总量偏大，网页首屏会变慢，建议压缩或减小尺寸")
    return 0


def main():
    ap = argparse.ArgumentParser(description="AI娘大乱斗 · 美术素材准备工具")
    ap.add_argument("--placeholder", action="store_true", help="生成 8 张几何占位立绘")
    ap.add_argument("--from", dest="src", help="单张源图路径")
    ap.add_argument("char_id", nargs="?", help="角色 id，配合 --from 使用")
    ap.add_argument("--from-dir", dest="folder", help="批量导入目录（按文件名含角色 id 匹配）")
    ap.add_argument("--remove-bg", action="store_true", help="把接近纯白的背景变透明")
    ap.add_argument("--check", action="store_true", help="检查 8 张立绘规格")
    a = ap.parse_args()

    if a.placeholder:
        make_placeholder()
    elif a.src:
        if not a.char_id:
            print("用 --from 时请带上角色 id，例如：--from pic.png deepseek")
            return 1
        return from_file(a.src, a.char_id, a.remove_bg)
    elif a.folder:
        return from_dir(a.folder, a.remove_bg)
    elif a.check:
        return check()
    else:
        ap.print_help()
        print("\n角色 id：" + ", ".join(IDS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
