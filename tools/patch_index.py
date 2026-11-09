# -*- coding: utf-8 -*-
"""给 pygbag 生成的 index.html 注入移动端适配（v3）。

v3 针对实测的「竖屏能看到 Loading，横屏后就不动了」：
  * 竖屏提示改成顶部一条 pointer-events:none 的小胶囊，不再用不透明 inset:0 全覆盖
    —— 以前若手机锁竖屏 / 旋转事件没触发，遮罩会一直盖住 canvas，看起来像下载卡住。
  * canvas 尺寸由 JS 按 16:9 主动计算，监听 resize / orientationchange /
    visualViewport / visibilitychange 重新适配；加载中 canvas 晚出现也有定时兜底。
  * 保留 touch-action:none 防止双击缩放抢走触摸。
只做字符串插入，幂等，不碰 pygbag 模板变量。
"""
import io
import os
import sys
import re

MARK = "AIMF_WEB_PATCH_V3"

CSS = """<style id="AIMF_WEB_PATCH_V3">
html,body{margin:0;padding:0;background:#000;overflow:hidden;overscroll-behavior:none}
canvas{display:block;touch-action:none!important;outline:none}
/* 只是一条小提示：不遮画布、不拦点击、不设不透明全屏背景 */
#aimf-rotate{
  display:none;position:fixed;left:50%;top:calc(8px + env(safe-area-inset-top,0px));
  transform:translateX(-50%);z-index:9999;pointer-events:none;
  background:rgba(11,13,28,.86);color:#ffd060;
  border:1px solid rgba(255,208,96,.45);border-radius:22px;
  padding:8px 18px;max-width:92vw;white-space:nowrap;text-align:center;
  font:600 14px/1.5 system-ui,-apple-system,sans-serif;
}
@media (orientation:portrait){#aimf-rotate{display:block}}
</style>
"""

BODY = """<div id="aimf-rotate">请把手机横过来玩（竖屏也能继续加载）</div>
<script>
(function(){
  var lastW=0,lastH=0,tries=0;
  function fit(){
    var c=document.querySelector('canvas');
    if(!c) return;
    var vw=window.innerWidth||document.documentElement.clientWidth;
    var vh=(window.visualViewport&&window.visualViewport.height)||window.innerHeight;
    if(!vw||!vh) return;
    var w=Math.min(vw,vh*16/9),h=w*9/16;
    if(Math.abs(w-lastW)<1&&Math.abs(h-lastH)<1) return;
    lastW=w;lastH=h;
    c.style.setProperty('width',Math.round(w)+'px','important');
    c.style.setProperty('height',Math.round(h)+'px','important');
    c.style.setProperty('position','fixed','important');
    c.style.setProperty('left','50%','important');
    c.style.setProperty('top','50%','important');
    c.style.setProperty('transform','translate(-50%,-50%)','important');
    c.style.setProperty('touch-action','none','important');
    c.setAttribute('tabindex','0');
  }
  fit();
  ['resize','orientationchange','pageshow','focus'].forEach(function(e){
    window.addEventListener(e,fit);
  });
  if(window.visualViewport) window.visualViewport.addEventListener('resize',fit);
  document.addEventListener('visibilitychange',function(){
    if(!document.hidden){fit();try{document.querySelector('canvas').focus();}catch(e){}}
  });
  /* pygbag 的 canvas 可能比本脚本晚出现：前 15 秒持续兜底探测 */
  var timer=setInterval(function(){
    fit();
    var c=document.querySelector('canvas');
    if(c&&c.width>0&&++tries>60) clearInterval(timer);
  },250);
  document.addEventListener('dblclick',function(e){e.preventDefault();},{passive:false});
  document.addEventListener('gesturestart',function(e){e.preventDefault();});
  document.addEventListener('pointerdown',function(){
    try{document.querySelector('canvas').focus();}catch(e){}
  },{passive:true});
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
    # 清掉旧版补丁，避免叠两层互相打架
    src = re.sub(r"<style id=\"AIMF_WEB_PATCH_V[12]\">.*?</style>\s*", "", src, flags=re.S)
    src = re.sub(r"<div id=\"aimf-rotate\">.*?</div>\s*", "", src, flags=re.S)
    src = re.sub(r"<script>\s*\(function\(\)\{\s*var c = document\.querySelector.*?</script>\s*",
                 "", src, flags=re.S)
    if "</head>" in src:
        src = src.replace("</head>", CSS + "</head>", 1)
    else:
        src = CSS + src
    if "</body>" in src:
        src = src.replace("</body>", BODY + "</body>", 1)
    else:
        src = src + BODY
    io.open(path, "w", encoding="utf-8").write(src)
    print("[patch_index] v3 已注入：不遮挡提示 + canvas 自适应")
    return 0


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "game/build/web/index.html"
    sys.exit(patch(p))
