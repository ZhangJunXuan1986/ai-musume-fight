# -*- coding: utf-8 -*-
"""给 pygbag 生成的 index.html 注入移动端适配。

只做字符串插入，不碰 pygbag 的模板变量；重复执行幂等；文件结构变了也不会让
构建失败。做三件事：
  1) canvas 等比缩放并居中（浏览器里不能再靠 pygame.FULLSCREEN）
  2) touch-action:none，避免手机上双击缩放 / 拖动页面抢走触摸
  3) 竖屏时盖一层「请横屏」提示
"""
import io
import os
import sys

MARK = "AIMF_WEB_PATCH_V2"

CSS = """<style id="AIMF_WEB_PATCH_V2">
/* 画布：保持 1280x720 内在比例，等比缩小到屏幕内，禁用浏览器手势 */
canvas{
  position:fixed !important; left:50% !important; top:50% !important;
  transform:translate(-50%,-50%) !important;
  max-width:100vw !important; max-height:100vh !important;
  max-height:100dvh !important;  /* 手机浏览器地址栏收起时用动态视口高度 */
  width:auto !important; height:auto !important;
  touch-action:none !important; outline:none;
}
html,body{margin:0;padding:0;background:#000;overflow:hidden;overscroll-behavior:none}
#aimf-rotate{
  display:none; position:fixed; inset:0; z-index:99999;
  background:#0b0d1c; color:#ffd060;
  align-items:center; justify-content:center; flex-direction:column;
  font:600 22px/1.8 system-ui,-apple-system,sans-serif; text-align:center;
}
@media (orientation:portrait){ #aimf-rotate{display:flex} }
</style>
"""

BODY = """<div id="aimf-rotate">
  <div style="font-size:48px">&#8635;</div>
  请把手机横过来玩
  <span style="font-size:14px;color:#8a92b8">AI娘大乱斗 · 横屏双人格斗</span>
</div>
<script>
(function(){
  var c = document.querySelector('canvas');
  if (c) {
    c.setAttribute('tabindex','0');
    c.addEventListener('pointerdown', function(){ try { c.focus(); } catch(e){} });
  }
  document.addEventListener('dblclick', function(e){ e.preventDefault(); }, {passive:false});
  document.addEventListener('gesturestart', function(e){ e.preventDefault(); });
})();
</script>
"""


def patch(path):
    if not os.path.exists(path):
        print("[patch_index] skip: %s 不存在（可能 pygbag 输出路径变了）" % path)
        return 1
    src = io.open(path, "r", encoding="utf-8", errors="replace").read()
    if MARK in src:
        print("[patch_index] 已打过补丁，跳过")
        return 0
    if "</head>" in src:
        src = src.replace("</head>", CSS + "</head>", 1)
    else:
        src = CSS + src
    if "</body>" in src:
        src = src.replace("</body>", BODY + "</body>", 1)
    else:
        src = src + BODY
    io.open(path, "w", encoding="utf-8").write(src)
    print("[patch_index] 已注入横屏提示与 canvas 缩放：%s" % path)
    return 0


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "game/build/web/index.html"
    sys.exit(patch(p))
