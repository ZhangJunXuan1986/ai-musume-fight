# -*- coding: utf-8 -*-
"""给 pygbag 生成的 index.html 强制注入「canvas 16:9 居中铺满」。

v4 修复实测的「页面飞左上角」：
  旧版用 `if MARK in src: 跳过`，只要模板里残留旧标记就什么 CSS 都不注入，
  canvas 会保持 pygbag 默认样式贴在左上角，右边一大片浏览器底色。
本版改为【每次都先删干净旧注入块，再重写最新版】，幂等且不赌文件是否上传过。

用法：python patch_index.py <index.html>
"""
import io, os, re, sys

CSS_ID = "aimf-fit-css-v4"
JS_ID  = "aimf-fit-js-v4"
TIP_ID = "aimf-rotate-v4"

CSS = """<style id="%(css)s">
html,body{margin:0!important;padding:0!important;width:100%%!important;height:100%%!important;
  overflow:hidden!important;overscroll-behavior:none!important;
  background:#0b0d1a!important;zoom:1!important;transform:none!important;}
canvas{display:block!important;outline:none!important;
  position:fixed!important;margin:0!important;transform:none!important;zoom:1!important;
  max-width:none!important;max-height:none!important;object-fit:fill!important;
  touch-action:none!important;}
#%(tip)s{display:none;position:fixed;left:50%%;top:calc(8px + env(safe-area-inset-top,0px));
  transform:translateX(-50%%);z-index:9999;pointer-events:none;
  background:rgba(11,13,28,.86);color:#ffd060;border:1px solid rgba(255,208,96,.45);
  border-radius:22px;padding:8px 18px;max-width:92vw;white-space:nowrap;text-align:center;
  font:600 14px/1.5 system-ui,-apple-system,sans-serif;}
@media (orientation:portrait){#%(tip)s{display:block}}
</style>
""" % {"css": CSS_ID, "tip": TIP_ID}

BODY = """<div id="%(tip)s">请把手机横过来玩（竖屏也能继续加载）</div>
<script id="%(js)s">
(function(){
  var tries=0;
  function fit(){
    var cs=document.querySelectorAll('canvas');
    if(!cs.length) return;
    var vw=window.innerWidth||document.documentElement.clientWidth;
    var vh=(window.visualViewport&&window.visualViewport.height)||window.innerHeight;
    if(!vw||!vh) return;
    for(var i=0;i<cs.length;i++){
      var c=cs[i];
      if(c.style.display==='none') continue;
      var bw=c.width||1280, bh=c.height||720;
      if(bw<2||bh<2) continue;
      var s=Math.min(vw/bw,vh/bh);
      var w=Math.round(bw*s), h=Math.round(bh*s);
      var L=Math.round((vw-w)/2), T=Math.round((vh-h)/2);
      /* 用像素 left/top 定位，彻底不用 transform，避免任何残留 scale 叠加 */
      c.style.setProperty('position','fixed','important');
      c.style.setProperty('left',L+'px','important');
      c.style.setProperty('top',T+'px','important');
      c.style.setProperty('margin','0','important');
      c.style.setProperty('width',w+'px','important');
      c.style.setProperty('height',h+'px','important');
      c.style.setProperty('max-width','none','important');
      c.style.setProperty('max-height','none','important');
      c.style.setProperty('transform','none','important');
      c.style.setProperty('zoom','1','important');
      c.style.setProperty('object-fit','fill','important');
      c.style.setProperty('touch-action','none','important');
      c.setAttribute('tabindex','0');
    }
    if(window.__aimfLast!==vw+'x'+vh){
      window.__aimfLast=vw+'x'+vh;
      console.log('[aimusume-fit] injected: canvas '+cs[0].width+'x'+cs[0].height+' -> '+w+'x'+h+' @ '+L+','+T);
    }
  }
  fit();
  ['resize','orientationchange','pageshow','focus','load'].forEach(function(e){
    window.addEventListener(e,fit);
  });
  if(window.visualViewport) window.visualViewport.addEventListener('resize',fit);
  document.addEventListener('visibilitychange',function(){
    if(!document.hidden){fit();try{document.querySelector('canvas').focus();}catch(e){}}
  });
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
""" % {"tip": TIP_ID, "js": JS_ID}


def strip_old(src):
    """删掉自己历次注入过的所有块，保证每次构建都是全新的最新版。"""
    src = re.sub(r'<style id="AIMF_WEB_PATCH_V[0-9]+">.*?</style>\s*', '', src, flags=re.S)
    src = re.sub(r'<style id="%s">.*?</style>\s*' % CSS_ID, '', src, flags=re.S)
    src = re.sub(r'<div id="aimf-rotate[^"]*">.*?</div>\s*', '', src, flags=re.S)
    src = re.sub(r'<div id="%s">.*?</div>\s*' % TIP_ID, '', src, flags=re.S)
    src = re.sub(r'<script id="%s">.*?</script>\s*' % JS_ID, '', src, flags=re.S)
    # 旧版无 id 的 fit 脚本（按特征精确删，不误伤 pygbag 自带 script）
    src = re.sub(r'<script>\s*\(function\(\)\{\s*var lastW=0,lastH=0,tries=0;.*?</script>\s*',
                 '', src, flags=re.S)
    src = re.sub(r'<script>\s*\(function\(\)\{\s*var tries=0;.*?</script>\s*',
                 '', src, flags=re.S)
    return src


def patch(path):
    if not os.path.exists(path):
        print("[patch_index] skip: %s 不存在" % path)
        return 1
    src = io.open(path, "r", encoding="utf-8", errors="replace").read()
    src = strip_old(src)
    if "</head>" in src:
        src = src.replace("</head>", CSS + "</head>", 1)
    else:
        src = CSS + src
    if "</body>" in src:
        src = src.replace("</body>", BODY + "</body>", 1)
    else:
        src = src + BODY
    io.open(path, "w", encoding="utf-8").write(src)
    print("[aimusume-fit] injected (v4 force-rewrite)")
    return 0


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "game/build/web/index.html"
    sys.exit(patch(p))
