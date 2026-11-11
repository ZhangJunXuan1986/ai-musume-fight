# -*- coding: utf-8 -*-
"""
================================================================================
 AI娘大乱斗 · 网页 / 手机双用版  /  AI Musume Fight Web
 类似 4399 死神VS火影的本地双人格斗 · 一份源码 · 两处运行
================================================================================

【一份源码，两处运行】
    A. 电脑 / 手机「Python编译器IDE」：直接运行本文件，pygame 窗口，跟之前一样。
    B. 浏览器 / GitHub Pages：pygbag 把本文件连同 assets/ 编译成 WebAssembly，
       访客打开网址就能玩，不用装 Python。本仓库的 Actions 自动完成构建与发布。

【2026-11-10 v3.4 —— 【决定性修复】自己接管浏览器输入，不再碰 SDL 鼠标坐标】
★ 拿用户仓库真实文件复查后的结论（这次有证据，不是猜）：
  · 键盘一直能用、鼠标和触摸一直不能用 —— 只有坐标换算这一环会同时影响后两者。
  · 之前 v4/v5/v6/v7 全在改 index.html 的 CSS，试图"让 SDL 报对坐标"，
    但 SDL/emscripten 怎么把 clientX 映到画布，取决于 pygbag 版本、DPR、
    canvas 内联样式和浏览器，改来改去始终拿不到确定结果。
  · v3.3 加的 F9 诊断在【手机上按不出来】（手机没 F 键），等于没给用户证据通道。
★ 本版做法：不修 CSS，改由游戏自己接管浏览器输入。
  · 本文件本来就用 platform.window.localStorage 读写战绩 —— 证明 pygbag 的
    Python 能访问浏览器 window。现在复用同一条通道：
    JS 在 document 上监听 pointerdown/move/up（capture 阶段，canvas 晚出现也接得住），
    用 canvas.getBoundingClientRect() 把 clientX/Y 归一化到虚拟画布 1280×720，
    推进 window.__aimfQ；Python 每帧调 aimfDrain() 取回 JSON，直接喂给
    on_touch_down / on_touch_move / on_touch_up。
  · 【canvas 被 CSS 改成多大、有没有 transform、有没有 DPR、哪个 workflow 生效，
    全都不影响】：rect 是真实显示尺寸，归一化永远成立。
  · 桥可用时【忽略 SDL 的鼠标/触摸事件】（避免重复点击），键盘事件照旧走 SDL。
    桥万一注入失败，自动回退到原来的 SDL 路径，不会比现在更差。
  · 主页面右上角新增【输入诊断】可点按钮（手机上终于能开诊断了），
    F9 在电脑上仍可用。诊断叠层会显示输入源、canvas 内外尺寸、最近事件坐标。
  · 因此本版【不需要改 main.yml】：v7 保持原样即可，只传 game/main.py 一个文件。

【2026-11-10 v3.3 —— 修小键盘 + 诊断优先，不再猜 CSS】
    ★ 把这轮踩的坑写死在代码里，防止以后再犯：
      · 键盘事件【不经过坐标换算】，所以从第一版到 v3.2 一直能用；
      · 鼠标 / 触摸走 SDL 的 clientX → 画布坐标换算。从我为了修「页面飞左上角」
        第一次给 canvas 注入 CSS 起，这套换算就被干扰了，之后 v4 / v5 / v6
        一直在改 CSS 猜坐标，越修越偏。
      · 【触摸和鼠标不冲突】，两者在 SDL 里是同一套 MOUSEBUTTONDOWN / FINGERDOWN，
        能同时支持，之前是一起坏的，不是二选一。
      · 本版 workflow 彻底撤销对 canvas 元素的任何 CSS 干预：不改 style.width、
        不加 transform、不加 canvas{...} 规则、不删 pygbag 生成的 canvas style。
        只改 viewport meta（浏览器级缩放，让手机看全）+ 一条不挡点击的竖屏提示。
        回到最初「能点」的状态。
      · 内置【F9 诊断叠层】：显示 SDL 收到的原始鼠标坐标、换算后的画布坐标、
        最近按键与触摸事件。还不对就按 F9 截图，一次定位，不再靠猜。
    · 修小键盘：pygame 里 NumPad 是独立 keycode K_KP1..K_KP9，
      和主键盘 K_1..K_9 不是一回事，所以按小键盘数字一直没反应。
      现在把 K_KP* 别名注入 just，PVP 归 P2、PVE 单人时全部归 P1
      （一个人玩左手 WASD + 右手小键盘，不用抬手去够字母区）。

【2026-11-10 v3.2 —— 按 4399 键位重排 / 跳跃与绕背 / 操作说明页】
    · 键位全部按 4399《死神VS火影》习惯重排，且【每个触屏键上都标出键盘键名】：
        P1  A/D 移动  W 上挑  S 防  J 普攻  K 跳
            U 技1  I 技2  O 技3  L 奥义  Q 闪避  E 净化  Z 秘卷
        P2  ←→ 移动  ↑ 上挑  ↓ 防  1 普攻  2 跳
            4 技1  5 技2  6 技3  3 奥义  7 闪避  8 净化  9 秘卷
    · 删掉旧一代「冲刺 L / 远攻 U / 必杀 I / 援助 O」独立动作（与技1~奥义功能重合），
      四个键位直接改挂新技能；KEYS 里对应项置 None，不再触发任何旧逻辑。
    · 虚拟按钮补上【跳】(K / 2)。跳跃时不再强制推开双方 → 可以跳过对手绕背；
      起跳保留水平惯性，落地后仍可自由左右穿插，角色不再永远锁在左右两边。
    · 新增【操作说明】页面：主页面菜单项 + 战斗页中间「说明」键 + 右上角「操作说明」；
      键盘表 / 触屏键位表 / 4 技能全名与联动 / 模式切换，一次讲清。
    · 删掉右上角 8 个旧小按钮（确/退/上下左右/再/清），只留 1 个「操作说明」。
    · PVP 顶部说明条同时显示 P1 与 P2 的技能名，不再只有 P1。
    · 主页面重排：菜单 6 项与右侧模式卡片分列，文字不再互相压叠。
    · 网页 CSS 换成 v6：flex 居中 + transform:scale，不再用 fixed+left/top
      （手机上贴左上角就是那个写法在不同浏览器算出的 vw/vh 不一致）；
      并加一层事件坐标兜底，防止某些浏览器把缩放后的 CSS 像素当成画布坐标。

【2026-11-10 v3.1 —— 修「点了没反应」+ 按键重排 + 模式切换】
    · 根因：网页 CSS 把 canvas 的【布局宽高】直接改小，pygbag 的鼠标/触摸坐标
      仍按布局像素给，右下角按钮永远点不到 → 配套 main.yml 改用
      `transform:scale()`（canvas 布局尺寸恒等于内部 1280×720），点按即刻恢复。
    · 手机触摸与鼠标可能同一帧各来一次 → 加同帧同坐标去重，菜单不再「切了又切回」。
    · 火影手游式分区：普攻大圆 / 3 个技能扇形圆 / 金色奥义 / 闪避·净化·秘卷
      独立横条；每个技能显示【角色专属短名 + 编号】，不再是「技1 技2 技3」。
    · 顶部技能说明条：常驻显示 4 个技能全名与联动关系，点之前就知道是什么。
    · 主页面 + 战斗页都有【切模式】【切操作】按钮，PVE/PVP、手机摇杆/电脑键盘
      一眼可见、一键切换；HUD 常显当前模式。
    · 结算层加可点「再战 / 回主页面」，不再只能靠键盘 R。

【2026-11-10 v3 玩法大升级 —— 参考火影手游】
    · 8 位 AI娘 各有【被动 + 4 技能 + 技能联动】；技能带前后摇、CD、耗气与状态
    · 新增【闪避】（小位移+长无敌，专躲技能）与【净化】（解控+免控）
    · 新增【秘卷】槽：8 个功能性可选技能（霸体 / 范围控制 / 远程控制 / 强化 /
      替身攻击 / 净化 / 回气 / 护盾），统一 CD 并各有代价
    · 【场地】9 种 AI娘 主题风格 + 7 种可开关机制（默认关，保证平衡）
    · 【模式】PVE 只显示 P1 一套按键（P2 电脑），PVP 双方按键都可见；
      移动键可设「自动 / 显示 / 隐藏」：手机显示摇杆，电脑窗口隐藏用键盘
    · 按键改成火影手游式紧凑圆形簇，全部压在两侧下缘，中间画面完全留空
    · 联网 PK 本版不实现，预留 NET_ENABLED 与《联网改造指南.md》
    · 全部新增数值集中在 ①-B 配置区，逐行中文注释；见《数值速查表.md》与《技能平衡表.md》

【2026-11-10 v2 更新 —— 四个实测问题，一次修完】
    A. 文字全变方框：根因是 assets/font.ttf 这个二进制文件没成功传进仓库，
       get_font 回退到只含 CJK 的字体，ASCII/全角都渲染不出。
       现在把字体【base64 内嵌在本文件末尾】，用 io.BytesIO 直接加载，
       ★ 只需覆盖 main.py 一个文本文件，font.ttf 传不传都不影响 ★
    B. 横屏后卡在 Loading：竖屏提示原来是不透明全覆盖层（inset:0 / z-index 99999），
       手机锁定竖屏或旋转事件不触发时会一直盖住 canvas。
       现在改成顶部一条 pointer-events:none 的小胶囊，canvas 始终可见可点；
       并由 JS 主动按 16:9 计算尺寸、监听旋转/可见性变化重新适配。
    C. 基础数值：速度调回适中，前摇 / 有效帧 / 后摇拆成三个独立常量，
       全部集中在 ① CONFIG 区，逐行中文注释。改动位置见随包《数值速查表.md》。
    D. 操作按钮：新增 TOUCH_STYLE = "naruto" —— 左下固定圆形摇杆（底盘不动、
       只有摇杆头跟手指）+ 弧形排列的圆形技能键，类似火影手游；
       想回到原来的方块网格把值改成 "grid" 即可。

【2026-11-09 实测修复（浏览器里跑起来后发现的三个问题）】
    1) 暂停只闪一帧：原来只写了 banner 且计时设 0，下一帧立即被清掉。
       现在有真正的 self.paused 状态：冻结计时 / 双方 / 实体，画面盖暂停遮罩，
       再点一次「暂停 / 继续」恢复。
    2) 数字 / 字母 / 箭头全是方框：打包字体误用了纯 CJK 后备字体
       （DroidSansFallback，ASCII 覆盖 0/62）。现改用文泉驿微米黑重新子集化，
       并加「网页文字保险层」把 ASCII 转全角、几何箭头换汉字，双保险。
    3) 移动太慢：MOVE_SPEED 4.6 -> 8.2、DASH_SPEED 13 -> 18，
       并按真实帧间隔补偿位移（浏览器掉到 30fps 也不会再慢一半）。

【为网页做了哪些改动（其余逻辑一行没动）】
    1) import asyncio；主循环改成 async def run()，每帧 await asyncio.sleep(0)
       —— pygbag 要求把控制权还给浏览器事件循环，否则标签页会卡死。
    2) IS_WEB = (sys.platform == "emscripten")，网页下：
       - 关掉 pygame.FULLSCREEN 那套自绘缩放，canvas 固定 1280×720，
         由注入的 CSS 等比缩放居中（tools/patch_index.py）
       - 战绩从「写 JSON 文件」改成「浏览器 localStorage」
    3) resource_path() 增加多个候选路径，兼容 pygbag 的虚拟文件系统。
    4) 入口改成模块级 asyncio.run(App().run())；--selftest / --touchtest 仍是同步分支。
    5) assets/font.ttf 是子集化字体（只保留源码用到的字，约 190 KB）。
       浏览器没有系统字体注册表，必须自带字体文件，否则中文全是方块；
       字体还必须覆盖 UI 用的 ▲▼◀▶ 等符号，不然按钮会变方块。
    6) 美术接口：assets/<角色id>.png 存在就自动替换代码绘制的 Q 版，
       不存在就照常跑。tools/prepare_assets.py 负责把任意图片处理成规格。

【目录约定（pygbag 强制要求入口叫 main.py 且在应用目录根）】
    game/main.py           <- 就是本文件
    game/assets/font.ttf   <- 子集化字体
    game/assets/<id>.png   <- 8 张立绘（占位图，可被正式图覆盖）
    game/favicon.png
    tools/patch_index.py   <- 给生成的 index.html 注入横屏/缩放 CSS
    tools/make_font.py     <- 改了中文文案后重新生成字体
    tools/prepare_assets.py<- 占位图 / 相册照片处理 / 规格校验
    .github/workflows/deploy.yml
    美术素材方案.md         <- 素材怎么搞、Termux 命令、出图提示词

【本地怎么跑】
    pip install pygame-ce pygbag
    python -m pygbag game                      # 本地预览 http://localhost:8000
    python -m pygbag --build --width 1280 --height 720 game   # 只构建，产物 game/build/web
    python game/main.py --selftest            # 不开窗口自检

【这一版修了什么 —— 针对你截图里「画面只剩顶部一条、文字被切一半」】
    上一版把窗口写死成 1280×720，手机横屏比例和它不一致，SDL 把画面裁切了；
    而且手机没有物理键盘，P1/P2 那两套 WASD / 方向键根本按不了。
    这一版做了两件事：
      1) 自适应缩放：读取手机实际分辨率，把 1280×720 的虚拟画布【等比缩放居中】
         贴到全屏，保证整幅画面完整可见、不裁切（左右或上下留黑边）。
      2) 触屏虚拟按键：左下 P1 一组、右下 P2 一组，支持多点同时按住；
         右上角一排小键管菜单（确认 / 返回 / 上下左右 / 再战 / 清战绩）。
         组合技「上挑 W+J」「破防 S+J」「变身 J+K」已做成独立按钮，不用双按。
    战斗逻辑、数值、8 位角色、页面全部沿用上一版，一行没改。

【手机上具体怎么玩】
    1. 把这个文件导入手机「Python编译器IDE」（替换掉之前那份）
    2. 手机【横屏】，点「运行」
    3. 主页面点「开始对战」（手指触摸 = 鼠标点击，已做坐标反变换）
    4. 左下角 = P1 十二个动作键，右下角 = P2 十二个动作键，直接点 / 按住
    5. 只想一个人玩：点屏幕中间「AI：关」切成「AI：开」，P2 交给电脑
    6. 右上角小键：确=确认 / Esc=返回 / ▲▼◀▶ 改设置 / R=再战 / C=清战绩
    7. 想退回主页面：右上角 Esc，或战斗中中间区「返回」

【电脑上怎么跑 / 自检】
    pip install pygame
    python ai_musume_fight_touch_clean.py
    python ai_musume_fight_touch_clean.py --selftest     # 无窗口自检（只验行为）
    python ai_musume_fight_touch_clean.py --touchtest    # 模拟多点触控压力测试

【打包成 exe（电脑上）】
    pyinstaller -F -w -n AIMusumeFightTouch --add-data "assets;assets" ai_musume_fight_touch_clean.py

【v3 改哪里】
    改技能伤害 / CD / 前后摇 / 加联动  -> ①-B 的 SKILL_BASE 与 SKILL_KITS
    加秘卷 / 场地 / 场地机制           -> SCROLLS / ARENAS / ARENA_EFFECTS
    改闪避 / 净化 / 状态时长           -> ①-B 的 DODGE_* / CLEANSE_* / STATUS_INFO
    改按键位置 / 圆键大小              -> CLUSTER_R / STICK_* / TOUCH_ALPHA
    改默认模式 / 默认场地               -> DEFAULT_MODE / DEFAULT_ARENA_IDX

【改哪里 —— 按变更原因找，不按文件找】
    改血量 / 伤害 / 怒气 / 按键 / 加角色  -> ① CONFIG 区（只动这一处）
    改按键大小 / 位置 / 状态栏避让      -> CONFIG 的「虚拟按键几何」
    改手机缩放 / 黑边 / 性能            -> CONFIG 的 MOBILE_* 与 FPS
    改战斗判定（防御 / 破防 / 反制）    -> App.apply_hit 及其 4 个私有子方法
    改角色形象 / 动作                  -> draw_fighter 与 8 个 _trait_*
    改某个页面                        -> 同名 upd_xxx / draw_xxx 方法
    改触摸映射 / 坐标换算              -> _poll_events / on_touch_down / to_canvas
    改 AI 对手                        -> ai_decide 与 AI_DEFAULT_ON

    结构约定：单文件、App 类持有状态、私有方法按职责分组。
    不设函数数量 / 行数指标 —— 那不是质量，只验行为：
    --selftest 检查配置、按键冲突、角色数据、3600 帧空跑、战绩读写、按钮布局。
    --touchtest 检查缩放坐标反变换、两指同时按住、AI 托管全流程。

【设计目标】
    1. 单文件：复制走就能跑，手机 IDE 无 import 风险，PyInstaller 一行出 exe。
    2. 集中调参：数值 / 角色 / 按键几何都在 ① 区，改完存盘重跑即可。
    3. 完整页面：主页面 / 角色选择 / 对局设置 / 游戏页 / P1-P2 战绩页 / 结算页。
    4. 机制复刻：3 格怒气、变身、援助、受击反制、上挑浮空、破防、冲刺、连击、计时。

【操作】
    P1 : A/D 移动  W 上  S 防御/下  J 普攻  K 跳  L 冲刺  U 远攻  I 必杀  O 援助
    P2 : ←/→ 移动  ↑ 上  ↓ 防御/下  1 普攻  2 跳  3 冲刺  4 远攻  5 必杀  6 援助
    组合：J+K / 1+2 三格气变身；W+J 上挑；S+J 下段破防；W+U 斜上远攻；
          受击瞬间按 O / 6 触发「灵压爆发 / 替身术」（消耗 1 格气）。
================================================================================
"""

import os
import sys
import json
import math
import time
import random
import asyncio
import base64
import io as _io
import pygame
# ==============================================================================
# ①-C 网页输入桥（v3.4）—— 不依赖 SDL 的鼠标/触摸坐标换算
#   pygbag 下 Python 通过 platform.window 访问浏览器（战绩 localStorage 已用同款通道）。
#   这段 JS 由 Python 在启动时注入，负责把 pointer 事件按真实 rect 归一化成
#   虚拟画布坐标；Python 每帧 drain 队列。注入失败会自动回退 SDL 原路径。
# ==============================================================================
_WEB_INPUT_JS = "(function(){\nif (window.__aimfBridge) return;\nvar W = __W__, H = __H__;\nvar q = [], active = {};\nwindow.__aimfQ = q;\nwindow.__aimfBridge = 1;\nfunction cvs(){\n  var cs = document.querySelectorAll('canvas'), best = null, a = 0;\n  for (var i=0;i<cs.length;i++){\n    var c = cs[i];\n    if (c.width * c.height > a){ a = c.width * c.height; best = c; }\n  }\n  return best;\n}\nfunction norm(cx, cy){\n  var c = cvs(); if (!c) return null;\n  var r = c.getBoundingClientRect();\n  if (!r.width || !r.height) return null;\n  /* clientX -> canvas 内部像素 -> 游戏虚拟画布坐标（两段换算都显式做） */\n  var x = (cx - r.left) * (c.width / r.width)  * (W / c.width);\n  var y = (cy - r.top)  * (c.height / r.height) * (H / c.height);\n  if (x < 0 || y < 0 || x > W || y > H) return null;\n  return [x, y, c.width, c.height, Math.round(r.width), Math.round(r.height)];\n}\nfunction push(kind, id, cx, cy){\n  var n = norm(cx, cy); if (!n) return;\n  q.push({t:kind, id:id, x:Math.round(n[0]), y:Math.round(n[1]),\n          cw:n[2], ch:n[3], rw:n[4], rh:n[5]});\n  if (q.length > 256) q.splice(0, q.length - 256);\n}\nfunction ptr(kind){\n  return function(e){\n    var id = (e.pointerId == null) ? 1 : e.pointerId;\n    if (kind === 'move' && !active[id]) return;\n    if (kind === 'down') active[id] = 1;\n    if (kind === 'up') delete active[id];\n    push(kind, id, e.clientX, e.clientY);\n  };\n}\nif (window.PointerEvent){\n  document.addEventListener('pointerdown',   ptr('down'), true);\n  document.addEventListener('pointermove',   ptr('move'), true);\n  document.addEventListener('pointerup',     ptr('up'),   true);\n  document.addEventListener('pointercancel', ptr('up'),   true);\n} else {\n  /* 老浏览器兜底：touch 与 mouse 都走同一个短时去重，避免一次点击来两遍 */\n  var lt = 0, lx = -999, ly = -999;\n  function dup(x, y){\n    var n = Date.now();\n    if (n - lt < 350 && Math.abs(x-lx) < 14 && Math.abs(y-ly) < 14) return true;\n    lt = n; lx = x; ly = y; return false;\n  }\n  function legacy(kind, id, x, y){\n    if (kind === 'down' && dup(x, y)) return;\n    push(kind, id, x, y);\n  }\n  document.addEventListener('mousedown', function(e){legacy('down',1,e.clientX,e.clientY);}, true);\n  document.addEventListener('mousemove', function(e){if(active[1]) legacy('move',1,e.clientX,e.clientY);}, true);\n  document.addEventListener('mouseup',   function(e){delete active[1]; legacy('up',1,e.clientX,e.clientY);}, true);\n  ['touchstart','touchmove','touchend','touchcancel'].forEach(function(name){\n    document.addEventListener(name, function(e){\n      var kind = (name==='touchstart')?'down':(name==='touchmove'?'move':'up');\n      for (var i=0;i<e.changedTouches.length;i++){\n        var t = e.changedTouches[i], id = t.identifier + 1000;\n        if (kind==='down') active[id] = 1;\n        if (kind==='up') delete active[id];\n        if (kind!=='move' || active[id]) legacy(kind, id, t.clientX, t.clientY);\n      }\n    }, true);\n  });\n}\nvar c0 = cvs();\nif (c0){ try { c0.style.touchAction = 'none'; } catch(err){} }\nwindow.aimfDrain = function(){\n  var o = q.slice(); q.length = 0; return JSON.stringify(o);\n};\nwindow.aimfInfo = function(){\n  var c = cvs(), r = c ? c.getBoundingClientRect() : null;\n  return JSON.stringify({\n    bridge:1, pe: window.PointerEvent ? 1 : 0,\n    canvases: document.querySelectorAll('canvas').length,\n    cw: c ? c.width : 0, ch: c ? c.height : 0,\n    rw: r ? Math.round(r.width) : 0, rh: r ? Math.round(r.height) : 0,\n    dpr: window.devicePixelRatio || 1, queued: q.length, W:W, H:H\n  });\n};\n})();"


def _web_window():
    """拿到 pygbag 的 JS window 代理；桌面 / 自检 / 注入失败都返回 None。"""
    if not IS_WEB:
        return None
    try:
        import platform as _wp
        return _wp.window
    except Exception:
        return None


def _web_install_input_bridge(js):
    """把输入桥 JS 注入页面。优先 window.eval，失败再用 <script> 标签。
    返回 (是否可用, 诊断信息 dict)。任何异常都不抛给游戏主流程。"""
    w = _web_window()
    if w is None:
        return False, {"reason": "no window"}
    ok = False
    try:
        w.eval(js)
        ok = True
    except Exception:
        try:
            d = w.document
            sc = d.createElement("script")
            sc.textContent = js
            d.head.appendChild(sc)
            ok = True
        except Exception:
            ok = False
    if not ok:
        return False, {"reason": "inject failed"}
    try:
        info = json.loads(str(w.aimfInfo()))
        return bool(info.get("bridge")), info
    except Exception as e:
        return False, {"reason": "info failed %r" % (e,)}


def _web_drain_input():
    """取回本帧积攒的浏览器输入事件（JSON 字符串 -> list）。失败返回 None。"""
    w = _web_window()
    if w is None:
        return None
    try:
        raw = w.aimfDrain()
        if raw is None:
            return None
        data = json.loads(str(raw))
        return data if isinstance(data, list) else None
    except Exception:
        return None


# ==============================================================================
# 运行环境判定：pygbag / 浏览器 WASM 下 sys.platform == "emscripten"
# 桌面与手机 IDE 均为 False，代码走原来的路径。
# ==============================================================================
IS_WEB = (sys.platform == "emscripten")
WEB_STATS_KEY = "ai_musume_stats_v1"   # localStorage 的键名

# ==============================================================================
# ① 可调参数区 CONFIG ——【只改这里就能改数值 / 加角色 / 换按键 / 换配色】
#    每一项都带注释说明作用，改完保存后重新运行即可生效，不需要动下面的逻辑。
# ==============================================================================

# ---- 窗口与帧率 ----
SCREEN_W = 1280                 # 虚拟画布宽度（所有 UI 坐标都按这个写，不改）
SCREEN_H = 720                 # 虚拟画布高度
_WEB_INPUT_JS = (_WEB_INPUT_JS.replace("__W__", str(SCREEN_W))
                            .replace("__H__", str(SCREEN_H)))
FPS = 60                       # 逻辑帧率；手机卡顿可降到 45
WINDOW_TITLE = "AI娘大乱斗 · 手机触屏版"
VERSION = "v3.4-js-input-bridge"

# ---- 手机适配（只改这里就能调全屏 / 按键 / 灵敏度）----
MOBILE_TOUCH = True            # True=绘制虚拟按键并接管触摸；False=回到纯键盘模式
MOBILE_FULLSCREEN = True       # True=占满手机屏幕；False=按 1280×720 开窗（电脑调试用）
MOBILE_STRETCH = False         # False=等比缩放居中留黑边（不裁切，推荐）；True=拉伸铺满（轻微变形）
MOBILE_SMOOTH = False          # True=平滑缩放更好看但更耗性能；False=快速缩放
MOBILE_FORCE_LANDSCAPE = True  # 检测到竖屏时按横屏尺寸计算（仍建议手机开自动旋转）
# ★ 操作布局开关："naruto" = 固定圆形摇杆 + 弧形圆键（火影手游式）
#                  "grid"   = 原来的 3×4 方块网格
TOUCH_STYLE = "naruto"
TOUCH_ALPHA = 165              # 虚拟按键底色不透明度 0~255（越小越不挡画面）
TOUCH_HINT = "左半 甲：摇杆＋圆键   右半 乙：摇杆＋圆键   中间：电脑 / 暂停 / 返回 / 再战"
AI_DEFAULT_ON = False          # 手机单人玩：改成 True 则开局自动托管 P2
AI_THINK_FRAMES = 11           # AI 每隔多少帧决策一次（越小越凶）

# ---- 虚拟按键几何 ----
# 手机屏幕比例 / 状态栏高度各家不同，按键挤了或挡了就只改这一块，
# 不用翻下面三个 build_* 函数。改完 --selftest 会检查按钮是否还在画布内。
TOUCH_BTN_W, TOUCH_BTN_H = 99, 44    # 左右两组每个动作键的宽高
TOUCH_BTN_GAP = 6                     # 动作键之间的间距（列步长 = W + GAP，行步长 = H + GAP）
TOUCH_P1_X0, TOUCH_P2_X0 = 16, 850   # 两组按键的起始 x（虚拟画布坐标）
TOUCH_Y0 = 566                        # 第一行按键的 y
TOUCH_GLOBAL_X, TOUCH_GLOBAL_Y = 872, 40   # 右上角菜单键起点（y=40 避开状态栏）
TOUCH_GLOBAL_W, TOUCH_GLOBAL_H, TOUCH_GLOBAL_GAP = 47, 28, 4
TOUCH_MID_X1, TOUCH_MID_X2 = 470, 650      # 战斗页中间区两列 x
TOUCH_MID_Y1, TOUCH_MID_Y2 = 590, 646      # 中间区两行 y
TOUCH_MID_W, TOUCH_MID_H = 160, 46

# ---- 固定摇杆几何（仅 TOUCH_STYLE="naruto" 生效）----
# 「不动主体」= 底盘圆心固定在左下/右下，永远不跟手指跑；只有小摇杆头在底盘内移动。
STICK_P1_CENTER = (132, 606)         # P1 摇杆底盘圆心（虚拟画布坐标）
STICK_P2_CENTER = (1148, 606)        # P2 摇杆底盘圆心（镜像）
STICK_RADIUS = 72                    # 底盘半径
STICK_KNOB_RADIUS = 30               # 摇杆头半径
STICK_MAX_OFFSET = 46                # 摇杆头最大偏移（像素）
STICK_DEADZONE = 0.32                # 死区：偏移比例小于此值不算方向
ROUND_LABELS = {"攻", "上挑", "破防", "防", "跳", "冲", "远", "必杀", "援反", "变身"}

# ---- 场地物理 ----
GROUND_Y = 516                 # 地面线：手机版下移一点，给底部虚拟按键留出空间
GRAVITY = 0.78                 # 重力加速度（像素/帧²）
JUMP_V = -16.0                 # 起跳初速度（负数=向上）
# ---- 手感基础数值（★ 想调快慢就改这几行 ★）----
MOVE_SPEED = 5.0               # 左右移动速度（像素/帧）。嫌慢调大、嫌快调小，建议 3.0~8.0
DASH_SPEED = 14.0              # 冲刺瞬时速度（像素/帧），建议 10~20
FRAME_COMPENSATE = True        # 位移按真实帧间隔补偿；浏览器掉帧时不会整体变慢（别关）
FRAME_SCALE_MIN = 0.6          # 补偿下限（防止切后台回来瞬移）
FRAME_SCALE_MAX = 2.0          # 补偿上限
DASH_FRAMES = 10               # 冲刺持续帧数
DASH_CD = 45                   # 冲刺冷却帧数
ARENA_LEFT = 40                # 场地左边界
ARENA_RIGHT = SCREEN_W - 40    # 场地右边界
BODY_W = 56                    # 角色碰撞盒宽度
BODY_H = 96                    # 角色碰撞盒高度

# ---- 血量 / 时间 / 训练 ----
BASE_HP = 1000                 # 基础血量（100% 档）
HP_SCALE_OPTIONS = [1.0, 2.0, 3.0, 4.0, 5.0]   # 对应 100% / 200% / ... / 500%
HP_SCALE_LABELS = ["100%", "200%", "300%", "400%", "500%"]
TIME_OPTIONS = [30, 60, 90, 0]                 # 回合秒数；0 = 无限时
TIME_LABELS = ["30 秒", "60 秒", "90 秒", "无限时"]
DEFAULT_TIME_IDX = 1           # 默认 60 秒
DEFAULT_HP_IDX = 0             # 默认 100% 血
DEFAULT_TRAINING = False       # 默认关闭训练模式
TRAIN_REGEN = 60               # 训练模式每秒回血量（按 HP_SCALE 缩放）

# ---- 怒气（气条）----
RAGE_MAX = 300                 # 怒气上限；每 100 = 1 格，共 3 格
RAGE_PER_GRID = 100            # 一格气需要的怒气值
RAGE_ON_HIT = 16               # 命中对手时自己增加的怒气
RAGE_ON_TAKE = 11              # 被命中时自己增加的怒气
RAGE_ON_PROJ = 10              # 投射物命中时增加的怒气
ULT_COST = 100                 # 必杀耗气（1 格）
ASSIST_COST = 100              # 援助耗气（1 格）
COUNTER_COST = 100             # 受击反制耗气（1 格）
TRANSFORM_COST = 300           # 变身耗气（3 格，变身后清空怒气）
COUNTER_WINDOW = 7             # 「受击瞬间」判定缓冲帧数（越大越容易触发反制）

# ---- 战斗数值 ----
DAMAGE = {
    "normal": 42,              # 普通攻击（J / 1）
    "up": 48,                  # 上挑 W+J（附带浮空）
    "down": 38,                # 下段 S+J（无视防御 / 破防）
    "far": 34,                 # 远攻投射物（U / 4）
    "ult": 130,                # 必杀（I / 5）
    "assist": 55,              # 援助攻击
    "counter": 30,             # 受击反制的反震伤害
}
ATK_REACH = 78                 # 近身攻击盒向前延伸距离
# ---- 出招三段（★ 前摇/后摇太长就改这三行，单位是帧，60 帧 = 1 秒 ★）----
ATK_STARTUP = 4                # 前摇：按下到判定生效。越小越跟手，建议 2~6
ATK_ACTIVE = 6                 # 有效帧：这几帧内才判定命中，建议 4~10
ATK_RECOVERY = 6               # 后摇：判定结束到能再动/再出招。越小连招越顺，建议 3~10
ATK_TOTAL = ATK_STARTUP + ATK_ACTIVE + ATK_RECOVERY   # 总帧数（自动相加，别直接改）
ATK_CD = 4                     # 两次攻击之间的最小间隔帧，建议 0~8
FAR_CD = 42                    # 远攻冷却帧
ULT_CD = 90                    # 必杀冷却帧
ASSIST_CD = 150                # 援助冷却帧
GUARD_REDUCE = 0.10            # 防御时承受的伤害比例（0.10 = 减伤 90%）
LAUNCH_V = -12.0               # 上挑给对手的浮空初速度
KNOCKBACK = 7.0                # 命中后的水平击退速度
HURT_FRAMES = 16               # 受击硬直帧数
INVULN_FRAMES = 8              # 命中后的短暂无敌帧（防同一次攻击多段命中）
COUNTER_INVULN = 26            # 反制成功后的无敌帧
TRANSFORM_ATK = 1.35           # 变身后的伤害倍率
TRANSFORM_SPEED = 1.20         # 变身后的移动速度倍率
TRANSFORM_DEF = 0.85           # 变身后的受伤倍率
COMBO_TIMEOUT = 100            # 连击计数多少帧内不中断

# ---- 投射物 / 特效 ----
PROJ_SPEED = 11.0              # 远攻投射物水平速度
PROJ_RADIUS = 16               # 投射物碰撞半径
PROJ_LIFE = 110                # 投射物最大存活帧
ULT_PROJ_SPEED = 8.5           # 必杀大弹速度
PARTICLE_MAX = 260             # 同屏粒子上限（调小可提升低配机器帧率）
SHAKE_ON_ULT = 14              # 必杀命中时的屏幕震动强度（像素）

# ---- 按键映射（改这里就能整体换键位）----
from pygame.locals import *  # noqa: F401,F403  # 导入 K_a / K_LEFT 等按键常量，改键位只改下面三个字典
# 【4399《死神VS火影》键位】WASD / 方向键移动，J / 1 普攻，K / 2 跳跃。
# 旧一代「冲刺 / 远攻 / 必杀 / 援助」四个独立动作已停用（置 None），
# 它们原本占的 L/U/I/O 与 3/4/5/6 现在直接改挂新技能，功能不再重合。
KEYS_P1 = {
    "left": K_a, "right": K_d, "up": K_w, "guard": K_s,
    "atk": K_j, "jump": K_k,
    "dash": None, "far": None, "ult": None, "assist": None,
}
KEYS_P2 = {
    "left": K_LEFT, "right": K_RIGHT, "up": K_UP, "guard": K_DOWN,
    "atk": K_1, "jump": K_2,
    "dash": None, "far": None, "ult": None, "assist": None,
}
GLOBAL_KEYS = {
    "confirm": K_RETURN, "cancel": K_ESCAPE, "restart": K_r,
    "clear_stats": K_c, "pause": K_p,
}

# ---- 配色主题 ----
COL_BG_TOP = (16, 18, 38)
COL_BG_BOT = (42, 28, 72)
COL_GROUND = (28, 30, 56)
COL_GRID = (70, 74, 120)
COL_PANEL = (24, 26, 52)
COL_PANEL_LIGHT = (40, 44, 84)
COL_TEXT = (238, 240, 255)
COL_DIM = (150, 156, 196)
COL_P1 = (86, 196, 255)
COL_P2 = (255, 138, 96)
COL_GOLD = (255, 208, 96)
COL_HP = (96, 226, 140)
COL_HP_LOW = (240, 92, 92)
COL_RAGE = (255, 196, 72)
COL_RAGE_FULL = (255, 96, 96)

# ==============================================================================
# ①-B v3 玩法配置 —— 模式 / 技能 / 被动 / 秘卷 / 场地（全部数据驱动）
#   加角色技能只改 SKILL_KITS，加场地只改 ARENAS，加秘卷只改 SCROLLS。
#   下面所有战斗逻辑都不用动；数值改完存盘重跑即生效。
# ==============================================================================

# ---- 对局模式 ----
MODE_PVE = "pve"          # 单人打电脑：只显示 P1 一套按键，P2 交电脑
MODE_PVP = "pvp"          # 本地双人：双方按键都可见
DEFAULT_MODE = MODE_PVE
NET_ENABLED = False       # 联网 PK 预留开关（本版不实现，见《联网改造指南.md》）

# ---- 移动键显隐（「手游 PVE 显示移动键 / 电脑 PVP 不显示」）----
MOVE_UI_SHOW, MOVE_UI_HIDE, MOVE_UI_AUTO = "show", "hide", "auto"
DEFAULT_MOVE_UI = MOVE_UI_AUTO   # auto：网页/手机全屏显示摇杆，电脑窗口隐藏（用键盘）
MOVE_UI_OPTIONS = [MOVE_UI_AUTO, MOVE_UI_SHOW, MOVE_UI_HIDE]
MOVE_UI_LABELS = ["自动", "显示", "隐藏"]

# ---- 技能槽与通用平衡基准（单位：帧，60 帧 = 1 秒）----
SKILL_SLOTS = ("s1", "s2", "s3", "ult")
SKILL_BASE = {
    # cd 冷却 / dmg 基础伤害 / rage 耗气 / startup 前摇 / active 有效 / recovery 后摇 / reach 近身距离
    "s1":   {"cd": 96,  "dmg": 56,  "rage": 0,   "startup": 4,  "active": 6,  "recovery": 10, "reach": 96},
    "s2":   {"cd": 186, "dmg": 78,  "rage": 0,   "startup": 7,  "active": 8,  "recovery": 14, "reach": 112},
    "s3":   {"cd": 252, "dmg": 88,  "rage": 0,   "startup": 9,  "active": 10, "recovery": 16, "reach": 124},
    "ult":  {"cd": 600, "dmg": 210, "rage": 200, "startup": 14, "active": 14, "recovery": 26, "reach": 160},
}
SKILL_LABEL = {"s1": "技1", "s2": "技2", "s3": "技3", "ult": "奥义"}

# ---- 状态效果（统一由 add_status / tick_status / cleanse 管理）----
STATUS_INFO = {
    "stun":          ("定身", (255, 110, 110)),   # 不能移动/放技能
    "slow":          ("减速", (150, 190, 255)),   # 移速 ×SLOW_MUL
    "silence":       ("沉默", (200, 150, 255)),   # 不能放技能，可普攻/移动
    "sleep":         ("催眠", (160, 160, 220)),   # 不能动，受击解除
    "super_armor":   ("霸体", (255, 190, 90)),    # 免疫硬直（不免疫控制）
    "cleanse_immune":("免控", (140, 235, 200)),   # 免疫新负面
    "buff_atk":      ("强化", (255, 216, 110)),   # 伤害 ×(1+val)
    "buff_speed":    ("迅捷", (140, 235, 255)),   # 移速 ×(1+val)
    "shield":        ("护盾", (120, 210, 255)),   # 吸收 val 点伤害
    "counter_ready": ("替身", (255, 160, 200)),   # 受击自动替身反击
}
NEGATIVE_STATUS = ("stun", "slow", "silence", "sleep", "mark")
SLOW_MUL = 0.62            # 减速状态移速倍率
BUFF_ATK_VAL = 0.25        # 强化状态伤害加成
BUFF_SPEED_VAL = 0.15      # 迅捷状态移速加成
SUPER_ARMOR_EXTRA = 0.20   # 霸体被「破霸体」技能命中的额外受伤（平衡代价）

# ---- 闪避 / 净化 / 秘卷 的独立数值 ----
DODGE_DIST = 78            # 闪避小位移（像素），主要用来躲技能
DODGE_INVULN = 14          # 闪避无敌帧（比受击无敌长，才躲得掉）
DODGE_CD = 150             # 闪避冷却帧（2.5 秒）
DODGE_RAGE_ON_SUCCESS = 8  # 无敌帧内确实躲掉一次攻击，回的气
CLEANSE_CD = 300           # 净化冷却帧（5 秒）
CLEANSE_IMMUNE = 90        # 净化后免控帧（1.5 秒）
SCROLL_CD_FALLBACK = 360   # 秘卷未单独写 cd 时的默认冷却（6 秒）

# ---- 8 位 AI娘 的技能组 / 被动 / 联动 ----------------------------------------
# 技能 spec 字段说明：
#   name 名称 / kind 类型 / dmg 伤害 / cd 冷却 / rage 耗气
#   startup,active,recovery 前后摇（省略则用 SKILL_BASE）
#   tag=True 命中给目标挂本角色标记；consume=True 命中带标记目标触发联动
#   link 联动额外效果 {dmg 追加伤害, status 追加状态, frames 帧数, knock 击退, launch 浮空}
#   status / status_frames 本技能自身附带的状态；radius 范围；proj 投射物速度；count 弹数
#   self_rage / self_heal / self_cleanse 自身收益；break_guard 破防；pierce_armor 破霸体
# 被动 passive：{name, desc, type, cd, val}，type 见 tick_passive 分发
SKILL_KITS = {
    "deepseek": {
        "passive": {"name": "干饭回气", "type": "rage_tick", "cd": 480, "val": 14,
                    "desc": "每 8 秒若近 3 秒未受击，回 14 点气"},
        "mark": "饭粒", "link_from": "s1", "link_to": "s3",
        "link_desc": "鲸尾上挑命中带饭粒目标，额外浮空并定身 30 帧",
        "skills": {
            "s1": {"name": "白饭碗击", "kind": "melee", "dmg": 56, "cd": 96, "tag": True,
                   "desc": "近身碗击，挂「饭粒」"},
            "s2": {"name": "Token 飞弹", "kind": "proj", "dmg": 74, "cd": 186,
                   "proj": 12, "status": "slow", "status_frames": 90,
                   "desc": "直线飞弹，命中减速 1.5 秒"},
            "s3": {"name": "鲸尾上挑", "kind": "melee", "dmg": 84, "cd": 252,
                   "launch": LAUNCH_V, "consume": True,
                   "link": {"dmg": 30, "status": "stun", "frames": 30, "launch": -14.0},
                   "desc": "上挑浮空；消耗饭粒触发联动"},
            "ult": {"name": "深度推理·全量蒸馏", "kind": "ult_proj", "dmg": 206, "cd": 600,
                    "rage": 200, "proj": 9, "radius": 40, "consume": True,
                    "link": {"dmg": 55},
                    "desc": "全量大弹，对带饭粒目标追加 55"},
        },
    },
    "chatgpt": {
        "passive": {"name": "豪门护盾", "type": "shield_tick", "cd": 720, "val": 40,
                    "desc": "开局及每 12 秒获得 40 点护盾"},
        "mark": "欠费", "link_from": "s1", "link_to": "s3",
        "link_desc": "白龙升角命中带欠费目标，破防并大幅击退",
        "skills": {
            "s1": {"name": "账单拍击", "kind": "melee", "dmg": 58, "cd": 96, "tag": True,
                   "desc": "近身拍击，挂「欠费」"},
            "s2": {"name": "Image 绘图炮", "kind": "proj", "dmg": 76, "cd": 186,
                   "proj": 11, "tag": True, "desc": "绘图炮，同样挂欠费"},
            "s3": {"name": "白龙升角", "kind": "dash_strike", "dmg": 86, "cd": 252,
                   "consume": True, "break_guard": True,
                   "link": {"dmg": 26, "knock": 13, "pierce_armor": True},
                   "desc": "突进顶角；消耗欠费破防破霸体"},
            "ult": {"name": "六万亿·全家桶", "kind": "ult_aoe", "dmg": 214, "cd": 600,
                    "rage": 200, "radius": 190, "consume": True, "link": {"dmg": 48},
                    "desc": "大范围全家桶，欠费目标追加 48"},
        },
    },
    "claude": {
        "passive": {"name": "宪法减伤", "type": "damage_cap", "cd": 0, "val": 0.30,
                    "desc": "单次受伤超过 120 的部分减免 30%"},
        "mark": "待审", "link_from": "s1", "link_to": "s3",
        "link_desc": "长上下文压书命中带待审目标，沉默 1 秒",
        "skills": {
            "s1": {"name": "宪法式校验", "kind": "melee", "dmg": 56, "cd": 96, "tag": True,
                   "desc": "近身校验，挂「待审」"},
            "s2": {"name": "Artifact 结界", "kind": "aoe", "dmg": 40, "cd": 186,
                   "radius": 130, "status": "stun", "status_frames": 25,
                   "desc": "自身周围定身 25 帧"},
            "s3": {"name": "长上下文压书", "kind": "proj", "dmg": 88, "cd": 252,
                   "proj": 7, "consume": True,
                   "link": {"dmg": 20, "status": "silence", "frames": 60},
                   "desc": "慢速大书；消耗待审追加沉默"},
            "ult": {"name": "戒律·拒绝执行", "kind": "ult_proj", "dmg": 200, "cd": 600,
                    "rage": 200, "proj": 10, "self_cleanse": True,
                    "desc": "贯穿大弹并净化自身"},
        },
    },
    "gemini": {
        "passive": {"name": "九命灵动", "type": "dodge_cd", "cd": 0, "val": 0.25,
                    "desc": "闪避冷却缩短 25%，成功闪避回 8 气"},
        "mark": "星尘", "link_from": "s1", "link_to": "s3",
        "link_desc": "星空爆裂命中带星尘目标，范围扩大并定身 30 帧",
        "skills": {
            "s1": {"name": "哈基米抓", "kind": "melee", "dmg": 54, "cd": 96, "tag": True,
                   "count": 2, "desc": "双段猫抓，挂「星尘」"},
            "s2": {"name": "多模态分身", "kind": "dash_strike", "dmg": 72, "cd": 186,
                   "desc": "分身突进斩"},
            "s3": {"name": "星空爆裂", "kind": "aoe", "dmg": 92, "cd": 252,
                   "radius": 130, "consume": True,
                   "link": {"dmg": 30, "status": "stun", "frames": 30, "radius": 195},
                   "desc": "范围爆裂；消耗星尘扩大范围并定身"},
            "ult": {"name": "双生星轨", "kind": "ult_proj", "dmg": 108, "cd": 600,
                    "rage": 200, "proj": 11, "count": 2, "desc": "双发星轨弹 108×2"},
        },
    },
    "qwen": {
        "passive": {"name": "品茶回血", "type": "hp_tick", "cd": 600, "val": 0.02,
                    "desc": "每 10 秒回复 2% 最大血量"},
        "mark": "茶香", "link_from": "s1", "link_to": "s3",
        "link_desc": "青瓷回旋命中带茶香目标，回血并破防",
        "skills": {
            "s1": {"name": "折扇一合", "kind": "melee", "dmg": 54, "cd": 96, "tag": True,
                   "desc": "近身合扇，挂「茶香」"},
            "s2": {"name": "流苏远掷", "kind": "proj", "dmg": 46, "cd": 186,
                   "proj": 12, "status": "stun", "status_frames": 30,
                   "desc": "远程控制弹，定身 30 帧"},
            "s3": {"name": "青瓷回旋", "kind": "aoe", "dmg": 84, "cd": 252,
                   "radius": 125, "consume": True, "break_guard": True,
                   "link": {"dmg": 18, "self_heal": 60, "status": "buff_speed", "frames": 120},
                   "desc": "回旋瓷片；消耗茶香回血并加速"},
            "ult": {"name": "千问·万卷", "kind": "ult_proj", "dmg": 188, "cd": 600,
                    "rage": 200, "proj": 10, "count": 3, "radius": 26,
                    "desc": "三连书卷弹"},
        },
    },
    "kimi": {
        "passive": {"name": "月相蓄能", "type": "full_rage_bonus", "cd": 0, "val": 0.10,
                    "desc": "气满 3 格时技能伤害 +10%"},
        "mark": "月痕", "link_from": "s1", "link_to": "s3",
        "link_desc": "长笛引月命中带月痕目标，定身翻倍并把对手拉向自己",
        "skills": {
            "s1": {"name": "月牙斩", "kind": "proj", "dmg": 60, "cd": 96,
                   "proj": 12, "tag": True, "desc": "月牙飞刃，挂「月痕」"},
            "s2": {"name": "星轨位移", "kind": "dash_strike", "dmg": 40, "cd": 186,
                   "status": "slow", "status_frames": 90, "desc": "后撤留痕并减速"},
            "s3": {"name": "长笛引月", "kind": "proj", "dmg": 52, "cd": 252,
                   "proj": 9, "status": "stun", "status_frames": 35, "consume": True,
                   "link": {"dmg": 24, "status": "stun", "frames": 70, "knock": -9},
                   "desc": "引月定身；消耗月痕定身翻倍并拉拽"},
            "ult": {"name": "月全食", "kind": "ult_aoe", "dmg": 212, "cd": 600,
                    "rage": 200, "radius": 200, "status": "slow", "status_frames": 120,
                    "desc": "全屏月食，范围伤害并减速"},
        },
    },
    "glm": {
        "passive": {"name": "嗜睡蓄力", "type": "idle_charge", "cd": 120, "val": 0.25,
                    "desc": "静止 2 秒后下一击伤害 +25%"},
        "mark": "睡意", "link_from": "s1", "link_to": "s3",
        "link_desc": "Z 字催眠命中带睡意目标，催眠翻倍并回气",
        "skills": {
            "s1": {"name": "打盹头槌", "kind": "melee", "dmg": 58, "cd": 96, "tag": True,
                   "desc": "迷糊头槌，挂「睡意」"},
            "s2": {"name": "黑书压顶", "kind": "proj", "dmg": 80, "cd": 186,
                   "proj": 8, "desc": "厚重黑书飞砸"},
            "s3": {"name": "Z 字催眠", "kind": "aoe", "dmg": 32, "cd": 252,
                   "radius": 140, "status": "sleep", "status_frames": 45, "consume": True,
                   "link": {"dmg": 22, "status": "sleep", "frames": 90, "self_rage": 40},
                   "desc": "范围催眠；消耗睡意翻倍并回 40 气"},
            "ult": {"name": "嗜睡·全域休眠", "kind": "ult_aoe", "dmg": 196, "cd": 600,
                    "rage": 200, "radius": 210, "status": "sleep", "status_frames": 60,
                    "desc": "全域休眠，范围伤害并催眠 1 秒"},
        },
    },
    "grok": {
        "passive": {"name": "毒舌反伤", "type": "reflect", "cd": 0, "val": 0.08,
                    "desc": "受击时反弹 8% 伤害给攻击者"},
        "mark": "挑衅", "link_from": "s1", "link_to": "s3",
        "link_desc": "哥特冲锋命中带挑衅目标，破霸体并定身 25 帧",
        "skills": {
            "s1": {"name": "巨斧横扫", "kind": "melee", "dmg": 64, "cd": 96, "tag": True,
                   "desc": "横扫巨斧，挂「挑衅」"},
            "s2": {"name": "毒舌弹幕", "kind": "proj", "dmg": 25, "cd": 186,
                   "proj": 13, "count": 3, "desc": "三连毒舌弹 25×3"},
            "s3": {"name": "哥特冲锋", "kind": "dash_strike", "dmg": 94, "cd": 252,
                   "consume": True, "pierce_armor": True,
                   "link": {"dmg": 26, "status": "stun", "frames": 25, "pierce_armor": True},
                   "desc": "扛斧冲锋；消耗挑衅破霸体定身"},
            "ult": {"name": "Ani·全域爆破", "kind": "ult_aoe", "dmg": 226, "cd": 600,
                    "rage": 200, "radius": 200, "knock": 12,
                    "desc": "全域爆破并大幅击退"},
        },
    },
}

# ---- 秘卷（功能性可选技能，开局选 1 个；统一 CD 约 6 秒，各有代价）----------
SCROLLS = {
    "霸体":     {"name": "霸体", "cd": 360, "kind": "self", "status": "super_armor",
                "frames": 180, "desc": "3 秒免疫硬直；被破霸体技能命中多受 20% 伤害"},
    "范围控制": {"name": "范围控制", "cd": 390, "kind": "aoe", "radius": 155,
                "status": "stun", "frames": 40, "dmg": 20, "desc": "自身周围定身 40 帧"},
    "远程控制": {"name": "远程控制", "cd": 360, "kind": "proj", "proj": 11,
                "status": "stun", "frames": 45, "dmg": 35, "desc": "前方控制弹，定身 45 帧"},
    "强化":     {"name": "强化", "cd": 420, "kind": "self", "status": "buff_atk",
                "frames": 180, "val": 0.25, "desc": "伤害 +25%、移速 +15%；期间自身受伤 +10%"},
    "替身攻击": {"name": "替身攻击", "cd": 420, "kind": "self", "status": "counter_ready",
                "frames": 300, "desc": "5 秒内受击自动替身免伤并反击 60"},
    "净化":     {"name": "净化", "cd": 330, "kind": "cleanse", "frames": 90,
                "desc": "立即解除全部负面并免控 1.5 秒"},
    "回气":     {"name": "回气", "cd": 480, "kind": "rage", "val": 80,
                "desc": "立即回 80 点气，冷却 8 秒"},
    "护盾":     {"name": "护盾", "cd": 420, "kind": "shield", "val": 120, "frames": 300,
                "desc": "获得 120 点护盾，持续 5 秒"},
}
SCROLL_ORDER = ["霸体", "范围控制", "远程控制", "强化", "替身攻击", "净化", "回气", "护盾"]
DEFAULT_SCROLL = "霸体"

# ---- 场地（9 种 AI娘 主题风格；deco 是程序化装饰类型）------------------------
ARENAS = [
    {"id": "deepsea",  "name": "鲸落深海",   "top": (8, 24, 52),   "bot": (14, 70, 112),
     "ground": (10, 38, 70), "grid": (46, 112, 168), "deco": "bubble",
     "desc": "DeepSeek 的主场，气泡与鲸影缓缓上浮"},
    {"id": "library",  "name": "白龙书库",   "top": (24, 28, 52),  "bot": (72, 76, 108),
     "ground": (38, 40, 70),  "grid": (128, 136, 178), "deco": "book",
     "desc": "ChatGPT 的藏书阁，书页与金色龙纹漂浮"},
    {"id": "archive",  "name": "暖橙档案室", "top": (48, 28, 24),  "bot": (110, 66, 44),
     "ground": (62, 40, 32),  "grid": (176, 118, 78),  "deco": "paper",
     "desc": "Claude 的宪法档案室，暖光与稿纸纷飞"},
    {"id": "starcat",  "name": "星海猫窝",   "top": (20, 16, 56),  "bot": (66, 40, 116),
     "ground": (34, 26, 76),  "grid": (126, 104, 208), "deco": "star",
     "desc": "Gemini 的星海，猫耳剪影与流星划过"},
    {"id": "teahouse", "name": "青瓷茶庭",   "top": (14, 36, 44),  "bot": (40, 88, 88),
     "ground": (22, 52, 56),  "grid": (92, 158, 150),  "deco": "teacup",
     "desc": "千问的茶庭，青瓷盏与流苏垂落"},
    {"id": "observatory","name":"月相观星台","top": (12, 16, 40),  "bot": (40, 44, 92),
     "ground": (22, 26, 58),  "grid": (96, 108, 176),  "deco": "moon",
     "desc": "Kimi 的观星台，月相缓缓轮转"},
    {"id": "foxden",   "name": "狐眠书斋",   "top": (16, 20, 44),  "bot": (36, 48, 92),
     "ground": (24, 30, 62),  "grid": (86, 116, 172),  "deco": "zzz",
     "desc": "GLM 的书斋，Z 字与狐火打盹"},
    {"id": "gothic",   "name": "哥特机房",   "top": (34, 12, 24),  "bot": (88, 30, 40),
     "ground": (48, 18, 30),  "grid": (176, 88, 76),   "deco": "gothic",
     "desc": "Grok Ani 的机房，尖拱窗与红色数据流"},
    {"id": "terminal", "name": "训练终端",   "top": (16, 18, 38),  "bot": (42, 28, 72),
     "ground": (28, 30, 56),  "grid": (70, 74, 120),   "deco": "plain",
     "desc": "中性训练场，无装饰，最省性能"},
]
DEFAULT_ARENA_IDX = 0

# ---- 场地机制（默认 none，保证对战平衡；设置页可开）--------------------------
ARENA_EFFECTS = {
    "none":        {"name": "纯净",   "desc": "无额外机制，纯视觉", "color": (150, 156, 196)},
    "center_rage": {"name": "中央聚气", "desc": "站在中场每秒 +10 气", "color": (255, 196, 72)},
    "edge_slow":   {"name": "边缘迟滞", "desc": "靠近两侧 15% 区域移速 -25%", "color": (150, 190, 255)},
    "energy_orb":  {"name": "能量球", "desc": "每 6 秒刷新一颗，拾取回 50 血 / 40 气", "color": (140, 235, 200)},
    "low_gravity": {"name": "低重力", "desc": "重力 ×0.65，跳跃更高", "color": (180, 160, 255)},
    "wind":        {"name": "周期风场", "desc": "每 8 秒交替左右推送角色", "color": (120, 210, 255)},
    "heal_zone":   {"name": "中央疗愈", "desc": "站中场每秒回 0.6% 最大血", "color": (96, 226, 140)},
}
ARENA_EFFECT_ORDER = ["none", "center_rage", "edge_slow", "energy_orb",
                      "low_gravity", "wind", "heal_zone"]
DEFAULT_ARENA_EFFECT = "none"
CENTER_ZONE = (SCREEN_W * 0.40, SCREEN_W * 0.60)   # 中央区域 x 范围
EDGE_ZONE = 0.15                                    # 边缘区域占比
ENERGY_ORB_PERIOD = 360                             # 每 6 秒一颗
WIND_PERIOD = 480                                   # 每 8 秒换向
WIND_FORCE = 0.9                                    # 每帧推力
ORB_PICK_RADIUS = 46                                # 拾取半径

# ---- 技能动作与键盘映射（触屏按钮直接发 (action, side) 元组）----------------
ACTION_ORDER = ("atk", "s1", "s2", "s3", "ult", "dodge", "cleanse", "scroll")
ACTION_LABELS = ("攻", "技1", "技2", "技3", "奥义", "闪避", "净化", "秘卷")
# 【键盘动作键，沿用 4399 手感】U/I/O/L 与 4/5/6/3 原本是远攻/必杀/援助/冲刺，
# 现在分别挂 技1/技2/技3/奥义；Q/E/Z 与 7/8/9 挂 闪避/净化/秘卷。
# 说人话：右手一列 U I O L = 四个技能，Q E Z = 三个功能键，不再有重复功能。
ACTION_KEYS_P1 = {
    "s1": K_u, "s2": K_i, "s3": K_o, "ult": K_l,
    "dodge": K_q, "cleanse": K_e, "scroll": K_z,
}
ACTION_KEYS_P2 = {
    "s1": K_4, "s2": K_5, "s3": K_6, "ult": K_3,
    "dodge": K_7, "cleanse": K_8, "scroll": K_9,
}
# 触屏键面上要显示的键盘键名（P1 / P2 分别一套）
KEYCAP_P1 = {"atk": "J", "jump": "K", "s1": "U", "s2": "I", "s3": "O",
             "ult": "L", "dodge": "Q", "cleanse": "E", "scroll": "Z"}
KEYCAP_P2 = {"atk": "1", "jump": "2", "s1": "4", "s2": "5", "s3": "6",
             "ult": "3", "dodge": "7", "cleanse": "8", "scroll": "9"}


def keycap(act, side):
    """返回该动作在键盘上的键名；触屏按钮下方会画出来。"""
    return (KEYCAP_P1 if side == 1 else KEYCAP_P2).get(act, "")


# ---- 数字小键盘（NumPad）--------------------------------------------------
# pygame/SDL 里小键盘数字是 K_KP1..K_KP9，与主键盘 K_1..K_9 是【不同的 keycode】。
# 用户截图里 NumLock 灯亮着 = 数字模式，按下去 SDL 报的就是 K_KP*。
# 这里把 K_KP* 别名成对应主键，注入 just；所有瞬发判定（普攻/跳/技能/功能）
# 都读 just，所以一处注入全通。keys（持续按住）不用管，移动靠 WASD / 方向键。
# PVE 单人时 P2 由电脑托管，小键盘全部让给 P1，右手不用伸到字母区。
NUMPAD_COMMON = {
    K_KP_ENTER: K_RETURN,      # 确认
    K_KP_PLUS: K_RIGHT,        # 设置页 ◀▶ 改值
    K_KP_MINUS: K_LEFT,
}
NUMPAD_ALIAS_P2 = dict(NUMPAD_COMMON)
NUMPAD_ALIAS_P2.update({
    K_KP1: K_1,    # 普攻
    K_KP2: K_2,    # 跳
    K_KP3: K_3,    # 奥义
    K_KP4: K_4,    # 技1
    K_KP5: K_5,    # 技2
    K_KP6: K_6,    # 技3
    K_KP7: K_7,    # 闪避
    K_KP8: K_8,    # 净化
    K_KP9: K_9,    # 秘卷
    K_KP0: K_r,    # 再战
})
NUMPAD_ALIAS_P1 = dict(NUMPAD_COMMON)
NUMPAD_ALIAS_P1.update({
    K_KP1: K_j,    # 普攻
    K_KP2: K_k,    # 跳
    K_KP3: K_l,    # 奥义
    K_KP4: K_u,    # 技1
    K_KP5: K_i,    # 技2
    K_KP6: K_o,    # 技3
    K_KP7: K_q,    # 闪避
    K_KP8: K_e,    # 净化
    K_KP9: K_z,    # 秘卷
    K_KP0: K_r,    # 再战
})
DIAG_TOGGLE = K_F9             # 诊断叠层开关，按一下开、再按一下关


def numpad_alias(mode):
    """按模式选小键盘归属：PVE 单人归 P1，PVP 双人归 P2。"""
    return NUMPAD_ALIAS_P1 if mode == MODE_PVE else NUMPAD_ALIAS_P2
ACTION_BY_KEY = {}
for _a, _k in ACTION_KEYS_P1.items():
    ACTION_BY_KEY[_k] = (_a, 1)
for _a, _k in ACTION_KEYS_P2.items():
    ACTION_BY_KEY[_k] = (_a, 2)

# ---- 火影手游式按键几何（右侧技能簇基准，镜像给左侧）------------------------
# 设计原则：所有键都压在屏幕两侧下缘，中间 400~1000 完全留给战斗画面。
# ---- v3.1 火影手游式分区布局（右侧基准；PVP 时左侧整体镜像）------------------
# 设计：普攻大圆在右下，3 个技能扇形排在它上方，奥义独立金色圆在更外侧，
#       闪避 / 净化 / 秘卷做成一排横胶囊，功能键与技能键彻底分开，不再混成一团。
SKILL_ROUND = [
    # 动作,   圆心x, 圆心y, 半径, 边框色
    ("atk",   1152, 606, 40, (190, 214, 255)),   # 普攻大圆
    ("s1",    1046, 578, 27, (120, 190, 255)),   # 技能 1（错开，外接框不与技2相交）
    ("s2",    1096, 516, 27, (120, 190, 255)),   # 技能 2
    ("s3",    1158, 508, 27, (120, 190, 255)),   # 技能 3
    ("ult",   1232, 562, 31, (255, 208, 96)),    # 奥义（金色）
]
FUNC_BAR = [
    # 动作,    左上x, y,   宽,  高   —— 横胶囊，不跟技能圆混在一起
    ("jump",     896, 662, 72, 36),   # 跳跃：4399 的 K / 2，之前漏了
    ("dodge",    972, 662, 72, 36),
    ("cleanse", 1048, 662, 72, 36),
    ("scroll",  1124, 662, 72, 36),
]
FUNC_LABEL = {"jump": "跳", "dodge": "闪避", "cleanse": "净化", "scroll": "秘卷"}
SKILL_INDEX = {"s1": "1", "s2": "2", "s3": "3", "ult": "奥"}
# 每个技能的【专属短名】：键上直接显示角色特性，不再写「技1 / 技2 / 技3」
SKILL_SHORT = {
    "deepseek": {"s1": "白饭", "s2": "飞弹", "s3": "鲸尾", "ult": "蒸馏"},
    "chatgpt":  {"s1": "账单", "s2": "绘图", "s3": "龙角", "ult": "全家桶"},
    "claude":   {"s1": "校验", "s2": "结界", "s3": "压书", "ult": "拒绝"},
    "gemini":   {"s1": "猫抓", "s2": "分身", "s3": "星爆", "ult": "星轨"},
    "qwen":     {"s1": "合扇", "s2": "流苏", "s3": "回旋", "ult": "万卷"},
    "kimi":     {"s1": "月牙", "s2": "星轨", "s3": "引月", "ult": "月食"},
    "glm":      {"s1": "头槌", "s2": "黑书", "s3": "催眠", "ult": "休眠"},
    "grok":     {"s1": "横扫", "s2": "弹幕", "s3": "冲锋", "ult": "爆破"},
}
CLUSTER_L_OFFSET = 0       # 左侧镜像时的额外偏移（0 = 严格镜像）
CLUSTER_PVP_STICK_SHIFT = 250  # PVP 强制显示摇杆时两簇往中间挪，避免压摇杆
STICK_RADIUS = 56          # 固定摇杆底盘半径
STICK_P1_CENTER = (110, 626)
STICK_P2_CENTER = (1170, 626)
ROUND_LABELS = set(ACTION_LABELS)
TOUCH_ALPHA = 205          # 底盘更实，文字才看得清；仍比全不透明轻
# 网页输入坐标：配套 main.yml 用 transform:scale() 后，此值保持 1.0 即可。
# 若个别浏览器点击仍整体偏小/偏大，把它改成 canvas.width / rect.width 的比值。
WEB_INPUT_SCALE = 1.0


# ---- 角色数据（8 位社区娘化角色）-------------------------------------------
# 想加角色：照抄一段改 id/name/color/skills 即可，菜单与选人页会自动扩容。
#   id      : 也用作可选立绘文件名 assets/<id>.png
#   color   : 主色（身体/头发），accent : 点缀色，aura : 变身光环色
#   stats   : hp / atk / speed 倍率，1.0 为基准
#   lore    : 联网调研得到的社区二创人设（非官方设定）
#   skills  : 五个技能名 + 变身形态名，会显示在选人页与战斗提示里
CHARACTERS = [
    {
        "id": "deepseek", "name": "DeepSeek 鲸鱼娘", "short": "大肥鱼",
        "color": (86, 164, 255), "accent": (255, 255, 255), "aura": (120, 220, 255),
        "stats": {"hp": 1.05, "atk": 0.96, "speed": 1.00},
        "lore": "蓝发鲸尾女仆，头戴铁盆当饭盆，爱吃白米饭和 Token，动不动「我去吃饭」",
        "skills": {"normal": "白饭碗击", "up": "鲸尾上挑", "far": "Token 飞弹",
                   "ult": "深度推理·全量蒸馏", "assist": "喊外援 GPT",
                   "counter": "掉线赔礼", "transform": "满上下文形态"},
    },
    {
        "id": "chatgpt", "name": "ChatGPT 白龙娘", "short": "白龙娘",
        "color": (232, 236, 248), "accent": (180, 200, 255), "aura": (255, 240, 190),
        "stats": {"hp": 1.10, "atk": 1.02, "speed": 0.94},
        "lore": "白发白角白色长裙与龙尾，豪门大姐大，身价六万亿、口嫌体正直",
        "skills": {"normal": "账单拍击", "up": "白龙升角", "far": "Image 绘图炮",
                   "ult": "六万亿·全家桶", "assist": "插件商店",
                   "counter": "服务降级", "transform": "白龙完全体"},
    },
    {
        "id": "claude", "name": "Claude 小 C", "short": "小 C",
        "color": (238, 148, 66), "accent": (60, 52, 48), "aura": (255, 190, 110),
        "stats": {"hp": 0.96, "atk": 1.10, "speed": 0.98},
        "lore": "暖橙长直发、放射花朵头饰、常抱书本；戒律里长大的优等生，写代码最猛",
        "skills": {"normal": "宪法式校验", "up": "长上下文压书", "far": "Artifact 结界",
                   "ult": "戒律·拒绝执行", "assist": "Clawd 螃蟹宠",
                   "counter": "安全对齐", "transform": "越界圣女"},
    },
    {
        "id": "gemini", "name": "Gemini 哈基米猫娘", "short": "猫娘",
        "color": (150, 130, 245), "accent": (110, 220, 230), "aura": (190, 160, 255),
        "stats": {"hp": 0.94, "atk": 0.96, "speed": 1.18},
        "lore": "蓝紫渐变发、异色瞳、猫耳猫尾、星空短裙，元气小傻子爱跳题",
        "skills": {"normal": "猫爪连击", "up": "猫尾挑飞", "far": "多模态闪光",
                   "ult": "跳题瞬移·全模态", "assist": "搜索弹幕",
                   "counter": "换个思路", "transform": "双子星形态"},
    },
    {
        "id": "qwen", "name": "通义千问大小姐", "short": "千问",
        "color": (86, 158, 226), "accent": (245, 240, 225), "aura": (150, 210, 255),
        "stats": {"hp": 1.02, "atk": 0.98, "speed": 1.00},
        "lore": "蓝发蓝白古风长袍、折扇流苏、嘴上挑剔默默照顾人，离不开奶茶",
        "skills": {"normal": "折扇一合", "up": "流苏挑月", "far": "奶茶泼",
                   "ult": "茶道·千问归一", "assist": "额度刷新",
                   "counter": "规矩之外", "transform": "千金全开"},
    },
    {
        "id": "kimi", "name": "Kimi 月相少女", "short": "Kimi",
        "color": (206, 214, 236), "accent": (120, 130, 200), "aura": (200, 210, 255),
        "stats": {"hp": 0.98, "atk": 1.00, "speed": 1.06},
        "lore": "银白卷发、月相与长笛，安静话少，擅长一口气读完 200 万字",
        "skills": {"normal": "长笛音波", "up": "月牙挑", "far": "星夜长文",
                   "ult": "满月·长上下文", "assist": "月相印记",
                   "counter": "安静退场", "transform": "月全食"},
    },
    {
        "id": "glm", "name": "GLM 嗜睡狐狸娘", "short": "GLM",
        "color": (72, 142, 196), "accent": (240, 226, 120), "aura": (130, 190, 230),
        "stats": {"hp": 1.06, "atk": 0.94, "speed": 0.96},
        "lore": "黑长发、Z 标志、抱黑书，先画图再讲原理，嗜睡还爱送鸡蛋",
        "skills": {"normal": "打盹撞击", "up": "流程图上挑", "far": "鸡蛋投掷",
                   "ult": "先画个图再讲原理", "assist": "同门支援",
                   "counter": "再睡五分钟", "transform": "清醒模式"},
    },
    {
        "id": "grok", "name": "Grok Ani", "short": "Ani",
        "color": (240, 206, 96), "accent": (176, 44, 62), "aura": (255, 150, 120),
        "stats": {"hp": 0.92, "atk": 1.14, "speed": 1.04},
        "lore": "金发双马尾、黑红哥特裙、扛巨斧，实时热搜嘴炮不断，争议担当",
        "skills": {"normal": "巨斧横劈", "up": "哥特挑斩", "far": "嘴炮弹",
                   "ult": "实时热搜·爆", "assist": "X 热搜置顶",
                   "counter": "已读乱回", "transform": "失控模式"},
    },
]

# ---- 文件与资源路径 ----
ASSET_DIR = "assets"           # 可选素材目录（立绘 / 字体），不存在也不影响运行
FONT_FILE = "font.ttf"         # 可选中文字体，放 assets/ 下自动优先使用
STATS_FILE = "ai_musume_stats.json"   # 战绩存档（生成在脚本或 exe 同目录）

# ---- 字体候选（按顺序尝试，找不到就回退 pygame 内置字体）----
FONT_CANDIDATES = [
    "WenQuanYi Micro Hei", "Microsoft YaHei", "SimHei",
    "Noto Sans CJK SC", "PingFang SC", "Heiti SC", "Arial Unicode MS",
]

# ==============================================================================
# ② 通用工具函数 —— 路径 / 字体 / 绘图 / 数学
# ==============================================================================

def resource_path(rel):
    """资源路径：兼容 桌面 / PyInstaller / pygbag 虚拟文件系统 三种摆放。
    pygbag 会把整个 game/ 目录挂到 VFS 的 assets/ 下，且会把 cwd 也设成该目录，
    所以依次尝试 _MEIPASS、__file__ 目录、cwd，最后退回裸相对路径。"""
    rel = rel.replace("\\", "/")
    bases = []
    if getattr(sys, "_MEIPASS", None):
        bases.append(sys._MEIPASS)
    try:
        bases.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass
    try:
        bases.append(os.getcwd())
    except Exception:
        pass
    for b in bases:
        try:
            p = os.path.join(b, rel)
            if os.path.exists(p):
                return p
        except Exception:
            continue
    return rel


def save_path():
    """战绩存档路径：写在脚本 / exe 的同目录，保证打包后也可写。
    想把存档放别处，改这一行即可。"""
    try:
        base = os.path.dirname(os.path.abspath(sys.argv[0])) or os.getcwd()
    except Exception:
        base = os.getcwd()
    return os.path.join(base, STATS_FILE)


def clamp(v, lo, hi):
    """把数值限制在 [lo, hi] 区间内。"""
    return max(lo, min(hi, v))


def lerp(a, b, t):
    """线性插值，用于粒子与 UI 的平滑过渡。"""
    return a + (b - a) * t


_FONT_CACHE = {}
# 字体来源：embedded(内嵌字节) / file(assets/font.ttf) / fallback(系统默认)
# web_safe_text 只在 fallback 时才把 ASCII 转全角，避免字体正常时数字变「Ｐ１」那种宽字。
_FONT_SOURCE = "none"


# ------------------------------------------------------------------------------
# 网页文字保险层
# 浏览器 WASM 里 pygame 可能回退到「仅含 CJK 的后备字体」，那时 ASCII 字母 / 数字
# 会全部渲染成方框（中文反而正常）。解决办法：网页模式下把 ASCII 统一转成【全角】
# ——任何中文字体都必带全角 ASCII，中文标点也更稳。桌面版不转换，画面保持原样。
# 几何箭头这类 CJK 字体常缺的符号，直接换成汉字。
# ------------------------------------------------------------------------------
_GEOM_MAP = {
    "◀": "左", "▶": "右", "▲": "上", "▼": "下",
    "⏎": "确", "←": "左", "→": "右", "↑": "上", "↓": "下",
    "✓": "对", "✗": "错", "★": "星", "☆": "星", "●": "点",
}


def web_safe_text(text):
    """仅在【完全没加载到字体】时把 ASCII 转全角（CJK 后备字体也有全角字形）。
    字体正常时原样输出，数字字母保持紧凑，不会显示成 Ｐ１ ６０ 这种宽字。"""
    if not IS_WEB or _FONT_SOURCE != "fallback":
        return str(text)
    out = []
    for ch in str(text):
        if ch in _GEOM_MAP:
            out.append(_GEOM_MAP[ch])
        elif ch == " ":
            out.append(" ")
        elif 0x21 <= ord(ch) <= 0x7E:
            out.append(chr(ord(ch) + 0xFEE0))   # ASCII -> 全角
        else:
            out.append(ch)
    return "".join(out)


def get_font(size, bold=False):
    """按大小缓存字体；优先 assets/font.ttf，其次系统中文字体。
    中文若显示成方块，把任意 .ttf 中文字体放到 assets/font.ttf 即可解决。"""
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    global _FONT_SOURCE
    f = None
    # ① 首选：本文件末尾内嵌的字体字节（不依赖任何外部文件，网页里最可靠）
    try:
        cand = pygame.font.Font(_io.BytesIO(_font_bytes()), size)
        cand.set_bold(bold)
        if cand.size("A")[0] > 0 and cand.size("中")[0] > 0:
            f = cand
            _FONT_SOURCE = "embedded"
    except Exception:
        pass
    # ② 内嵌万一失败：再试 assets/font.ttf（你自己换字体时用）
    if f is None:
        custom = resource_path(os.path.join(ASSET_DIR, FONT_FILE))
        tries = [custom,
                 os.path.join(ASSET_DIR, FONT_FILE),
                 os.path.join("game", ASSET_DIR, FONT_FILE),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), ASSET_DIR, FONT_FILE)]
        seen = set()
        for p in tries:
            if not p or p in seen:
                continue
            seen.add(p)
            try:
                if not os.path.exists(p):
                    continue
                cand = pygame.font.Font(p, size)
                cand.set_bold(bold)
                if cand.size("A")[0] > 0 and cand.size("中")[0] > 0:
                    f = cand
                    _FONT_SOURCE = "file"
                    break
            except Exception:
                continue
    if f is None:
        for name in FONT_CANDIDATES:
            p = pygame.font.match_font(name)
            if p:
                try:
                    f = pygame.font.Font(p, size)
                    f.set_bold(bold)
                    break
                except Exception:
                    continue
    if f is None:
        f = pygame.font.Font(None, size)  # 兜底：此时才启用全角保险层
        _FONT_SOURCE = "fallback"
    _FONT_CACHE[key] = f
    return f


_PORTRAIT_CACHE = {}


def load_portrait(char_id):
    """可选立绘接口：把图片命名为 assets/<角色id>.png 就会自动替换代码绘制的 Q 版。
    没有图片时返回 None，游戏照常运行 —— 这是「零依赖也能跑、放图就变好看」的关键。"""
    if char_id in _PORTRAIT_CACHE:
        return _PORTRAIT_CACHE[char_id]
    p = resource_path(os.path.join(ASSET_DIR, char_id + ".png"))
    img = None
    if os.path.exists(p):
        try:
            img = pygame.image.load(p).convert_alpha()
        except Exception:
            img = None
    _PORTRAIT_CACHE[char_id] = img
    return img


def draw_text(surf, text, x, y, size=24, color=COL_TEXT, bold=False,
              align="left", shadow=True):
    """带描边阴影的文字绘制；align 支持 left / center / right。"""
    text = web_safe_text(text)
    f = get_font(size, bold)
    img = f.render(text, True, color)
    r = img.get_rect()
    if align == "center":
        r.centerx, r.top = x, y
    elif align == "right":
        r.right, r.top = x, y
    else:
        r.topleft = (x, y)
    if shadow:
        s = f.render(text, True, (0, 0, 0))
        surf.blit(s, (r.x + 2, r.y + 2))
    surf.blit(img, r)
    return r


def draw_panel(surf, rect, fill=COL_PANEL, border=COL_PANEL_LIGHT, radius=14, width=2):
    """圆角面板：所有菜单卡片统一用它，保证页面风格一致。"""
    pygame.draw.rect(surf, fill, rect, border_radius=radius)
    if width:
        pygame.draw.rect(surf, border, rect, width=width, border_radius=radius)


def draw_bar(surf, rect, ratio, color, back=(18, 20, 42), reverse=False):
    """通用进度条：血条 / 气条 / 属性条都用这个。reverse=True 时从右往左减少。"""
    pygame.draw.rect(surf, back, rect, border_radius=6)
    ratio = clamp(ratio, 0.0, 1.0)
    if ratio <= 0:
        return
    w = int(rect.w * ratio)
    if reverse:
        fill = pygame.Rect(rect.right - w, rect.y, w, rect.h)
    else:
        fill = pygame.Rect(rect.x, rect.y, w, rect.h)
    pygame.draw.rect(surf, color, fill, border_radius=6)


def draw_rage(surf, rect, rage):
    """3 格气条：按 100 怒气 = 1 格分段绘制，满 3 格变红。"""
    pygame.draw.rect(surf, (18, 20, 42), rect, border_radius=6)
    gap = 4
    cell = (rect.w - gap * 2) // 3
    for i in range(3):
        lo = i * RAGE_PER_GRID
        r = clamp((rage - lo) / float(RAGE_PER_GRID), 0.0, 1.0)
        x = rect.x + i * (cell + gap)
        box = pygame.Rect(x, rect.y, cell, rect.h)
        pygame.draw.rect(surf, (46, 48, 84), box, border_radius=4)
        if r > 0:
            c = COL_RAGE_FULL if rage >= RAGE_MAX else COL_RAGE
            pygame.draw.rect(surf, c, (x, box.y, int(cell * r), box.h), border_radius=4)


def shade(color, factor):
    """把颜色整体调亮 / 调暗，用于变身光环与命中闪光。"""
    return tuple(int(clamp(c * factor, 0, 255)) for c in color)


# ==============================================================================
# ②.5 手机触屏适配层 —— 自适应缩放 / 虚拟按键布局 / 坐标反变换 / AI 决策
#      这一层不碰任何战斗规则：把触摸「翻译」成上一版原本要的键盘事件。
# ==============================================================================

# 按钮定义在【虚拟画布 1280×720】坐标里，缩放后手指位置会自动反变换回来。
# 每个按钮: (rect, 标签, 持续按住的键列表, 按下瞬间触发的键列表)
#   hold -> 合成进 keys 数组；tap -> 加进 just 集合，正好对应 Fighter.update 的读法。
def _btn(x, y, w, h, label, hold=(), tap=()):
    return (pygame.Rect(x, y, w, h), label, tuple(hold), tuple(tap))


def build_side_buttons(keys, xs, ys):
    """生成一侧（P1 或 P2）的 12 个战斗按键：3 行 × 4 列。
    keys 传 KEYS_P1 / KEYS_P2，生成的两套键码互不冲突。"""
    spec = [
        ("左",     ("left",),  ()),                 # 左移（持续按住）
        ("防",     ("guard",), ()),                # 防御（持续按住）
        ("右",     ("right",), ()),                # 右移（持续按住）
        ("跳",     (), ("jump",)),                 # 跳跃（点一下）
        ("攻",     (), ("atk",)),                  # 普攻
        ("上挑",   ("up",), ("atk",)),             # W+J 浮空，做成独立按钮
        ("破防",   ("guard",), ("atk",)),          # S+J 破防，做成独立按钮
        ("冲",     (), ("dash",)),                 # 冲刺
        ("远",     (), ("far",)),                  # 远攻投射物
        ("必杀",   (), ("ult",)),                  # 1 格气
        ("援反",   (), ("assist",)),               # 援助 / 受击瞬间反制
        ("变身",   (), ("atk", "jump")),           # J+K，3 格气
    ]
    out = []
    for i, (lab, holds, taps) in enumerate(spec):
        r, c = divmod(i, 4)
        out.append(_btn(xs[c], ys[r], TOUCH_BTN_W, TOUCH_BTN_H, lab,
                        [keys[n] for n in holds], [keys[n] for n in taps]))
    return out


def build_global_buttons():
    """v3.4：右上角两个入口 —— 操作说明 + 输入诊断。
    手机上按不出 F9，所以补一个可点的诊断按钮；进对战前点开，叠层会一直显示。"""
    return [_btn(24, 24, 150, 36, "操作说明", (), ()),
            _btn(184, 24, 120, 36, "输入诊断", (), ())]


def build_mid_buttons():
    """战斗页中间区：切模式 / 切操作 / 暂停 / 返回。
    这两个切换键就是「手游端游怎么切」的答案，战斗中一点即生效并重开一局。"""
    w, h = 104, 34
    x0, y0 = 512, 540     # 放在地面线上方一点，避开底部 y=662 的功能条
    return [
        _btn(x0,       y0,      w, h, "切模式", (), ()),
        _btn(x0 + 110, y0,      w, h, "切操作", (), ()),
        _btn(x0,       y0 + 40, w, h, "暂停",   (), (GLOBAL_KEYS["pause"],)),
        _btn(x0 + 110, y0 + 40, w, h, "返回",   (), (GLOBAL_KEYS["cancel"],)),
        _btn(x0,       y0 + 80, w * 2 + 6, h, "操作说明", (), ()),
    ]


def skill_short_name(char_id, slot):
    """键面上显示的 2~3 字专属短名；没配就自动从技能全名取前两字。"""
    n = SKILL_SHORT.get(char_id, {}).get(slot)
    if not n:
        full = skill_spec(char_id, slot).get("name", "技能")
        n = full.split("·")[0][:2]
    return n


def skill_help_lines(char_id):
    """顶部技能说明条：4 个技能全名 + 联动关系，点之前就知道每个键是什么。"""
    names = [skill_spec(char_id, sl).get("name", "?") for sl in SKILL_SLOTS]
    kit = SKILL_KITS.get(char_id, SKILL_KITS["deepseek"])
    return (("技1 %s   技2 %s   技3 %s   奥义 %s" % tuple(names)),
            ("联动 %s → %s：%s" % (SKILL_LABEL[kit["link_from"]],
                                 SKILL_LABEL[kit["link_to"]], kit["link_desc"])))


def build_skill_cluster(side, mirror=False, shift=0):
    """v3.1 火影手游式分区：5 个圆键（普攻/3技能/奥义）+ 3 个横胶囊功能键。
    label 放【角色专属短名】，tap 发 (action, side)；绘制层按动作取 CD 与配色。
    shift>0 时整簇往画面中间挪，给 PVP 强制显示的双摇杆让位。"""
    out = []

    def mx(x):
        return SCREEN_W - x + CLUSTER_L_OFFSET + shift if mirror else x - shift

    for act, cx, cy, r, _col in SKILL_ROUND:
        cx = mx(cx)
        out.append(_btn(int(cx - r), int(cy - r), r * 2, r * 2,
                        act, (), ((act, side),)))
    for act, x, y, w, h in FUNC_BAR:
        if mirror:
            x = SCREEN_W - (x + w) + CLUSTER_L_OFFSET + shift
        else:
            x = x - shift
        out.append(_btn(int(x), int(y), w, h, act, (), ((act, side),)))
    return out


def build_naruto_layout():
    """默认 PVP 布局：左侧 P1 簇 + 右侧 P2 簇；PVE 时由 App._rebuild_buttons 改。"""
    return (build_skill_cluster(1, mirror=True),
            build_skill_cluster(2, mirror=False),
            build_global_buttons(),
            build_mid_buttons())


def build_touch_layout():
    """汇总四组按钮。按 TOUCH_STYLE 选摇杆式或网格式；改几何去 CONFIG 区。"""
    if TOUCH_STYLE == "naruto":
        return build_naruto_layout()
    step_x = TOUCH_BTN_W + TOUCH_BTN_GAP
    step_y = TOUCH_BTN_H + TOUCH_BTN_GAP
    xs1 = [TOUCH_P1_X0 + i * step_x for i in range(4)]
    xs2 = [TOUCH_P2_X0 + i * step_x for i in range(4)]
    ys = [TOUCH_Y0 + r * step_y for r in range(3)]
    return (build_side_buttons(KEYS_P1, xs1, ys),
            build_side_buttons(KEYS_P2, xs2, ys),
            build_global_buttons(),
            build_mid_buttons())


# pygame 1.x 没有 FINGER* 事件常量，取不到时自动只走鼠标触摸映射
FINGER_DOWN = getattr(pygame, "FINGERDOWN", -1)
FINGER_MOTION = getattr(pygame, "FINGERMOTION", -1)
FINGER_UP = getattr(pygame, "FINGERUP", -1)


class KeyState:
    """只读代理：物理键盘状态 + 虚拟按钮 / AI 注入的按住状态。
    刻意不把 pygame.key.get_pressed() 转成普通 list —— pygame 2 的方向键常量
    是 1073741905 这类大数，ScancodeWrapper 内部会做 scancode 映射，转成 list 会
    丢掉这个兼容逻辑导致 IndexError。代理一层即可同时保留两者。"""
    def __init__(self, base, held):
        self.base = base
        self.held = held

    def __getitem__(self, key):
        if key in self.held:
            return True
        try:
            return bool(self.base[key])
        except (IndexError, KeyError):
            return False

    def __len__(self):
        return len(self.base)


def ai_decide(bot, foe, frame):
    """P2 电脑对手：按距离 / 怒气 / 血量返回 (持续按住的键, 本帧触发的键)。
    只操作 KEYS_P2 的键码，和 P1 键码完全不重叠，所以不会干扰玩家。"""
    k = KEYS_P2
    dist = abs(bot.x - foe.x)
    near = dist <= ATK_REACH + 60
    if bot.rage >= TRANSFORM_COST and not bot.transformed:
        return (), (k["atk"], k["jump"])
    if bot.rage >= ULT_COST and (near or frame % 5 == 0):
        return (), (k["ult"],)
    if foe.guard and bot.rage >= ASSIST_COST:
        return (), (k["assist"],)
    if near:
        if foe.guard:
            return (k["guard"],), (k["atk"],)          # S+J 破防
        return (), (k["atk"],)
    if bot.x < foe.x:
        return (k["right"],), (k["far"],) if dist > 330 else ()
    return (k["left"],), (k["far"],) if dist > 330 else ()


# ==============================================================================
# ③ 战绩数据层 —— JSON 持久化（P1 / P2 各自独立统计）
# ==============================================================================

def blank_side():
    """单侧玩家的空战绩结构。"""
    return {"matches": 0, "wins": 0, "damage": 0, "max_combo": 0,
            "chars": {}, "recent": []}


def _web_storage():
    """浏览器 localStorage 桥。pygbag 通过 platform.window 暴露 JS 对象；
    拿不到就返回 None，游戏自动回退到「本局有效」的临时战绩，不会崩。"""
    if not IS_WEB:
        return None
    try:
        import platform as _web_platform
        return _web_platform.window.localStorage
    except Exception:
        return None


def _web_get(key):
    try:
        ls = _web_storage()
        return ls.getItem(key) if ls is not None else None
    except Exception:
        return None


def _web_set(key, value):
    try:
        ls = _web_storage()
        if ls is not None:
            ls.setItem(key, value)
    except Exception:
        pass


def load_stats():
    """读战绩：网页读 localStorage，桌面/IDE 读 JSON 文件。
    文件缺失、JSON 损坏、浏览器禁用存储时都返回全新战绩，不让游戏崩。"""
    data = None
    if IS_WEB:
        raw = _web_get(WEB_STATS_KEY)
        if raw:
            try:
                data = json.loads(raw)
            except Exception:
                data = None
    else:
        try:
            with open(save_path(), "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except Exception:
            data = None
    if not isinstance(data, dict):
        data = {}
    for side in ("P1", "P2"):
        if not isinstance(data.get(side), dict):
            data[side] = blank_side()
        for k, v in blank_side().items():
            data[side].setdefault(k, v)
    return data


def save_stats(data):
    """写战绩：网页写 localStorage，桌面/IDE 写 JSON（UTF-8 / 缩进 2）。"""
    if IS_WEB:
        _web_set(WEB_STATS_KEY, json.dumps(data, ensure_ascii=False))
        return
    try:
        with open(save_path(), "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
    except Exception:
        pass  # 只读目录等极端情况下静默失败，不影响对局


def record_match(data, winner, p1, p2, training=False):
    """一局结束后更新 P1/P2 战绩。winner: 1 / 2 / 0(平局)。
    训练模式不写战绩，避免刷数据。"""
    if training:
        return data
    sides = {1: data["P1"], 2: data["P2"]}
    fighters = {1: p1, 2: p2}
    for i in (1, 2):
        s, f = sides[i], fighters[i]
        s["matches"] += 1
        if winner == i:
            s["wins"] += 1
        s["damage"] += int(f.dealt)
        s["max_combo"] = max(s["max_combo"], f.max_combo)
        cid = f.char["id"]
        s["chars"][cid] = s["chars"].get(cid, 0) + 1
        s["recent"].insert(0, {
            "result": "胜" if winner == i else ("平" if winner == 0 else "负"),
            "char": f.char["short"],
            "dmg": int(f.dealt),
            "combo": f.max_combo,
            "ts": time.strftime("%m-%d %H:%M"),
        })
        s["recent"] = s["recent"][:8]
    save_stats(data)
    return data


# ==============================================================================
# ④ 实体层 —— Fighter / Projectile / Assist / Particle / FloatingText
# ==============================================================================

class Fighter:
    """格斗角色：状态机 + 物理 + 输入 + 命中判定。
    状态：idle / run / jump / atk / guard / dash / hurt / ko。
    所有数值都从 CONFIG 与角色 stats 读取，本类不含硬编码战斗常数。"""

    def __init__(self, side, char, x):
        self.side = side                       # 1 = P1, 2 = P2
        self.char = char
        self.keys = KEYS_P1 if side == 1 else KEYS_P2
        self.x = float(x)                      # 脚底中心 x
        self.y = float(GROUND_Y)              # 脚底 y
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1 if side == 1 else -1  # 1 向右 / -1 向左
        self.max_hp = BASE_HP * HP_SCALE_OPTIONS[DEFAULT_HP_IDX] * char["stats"]["hp"]
        self.hp = self.max_hp
        self.rage = 0
        self.state = "idle"
        self.state_t = 0                      # 当前状态已持续帧数
        self.atk_kind = "normal"              # 本次攻击类型
        self.atk_cd = 0
        self.atk_hit = False                  # 本次攻击是否已命中（防止多段）
        self.far_cd = 0
        self.ult_cd = 0
        self.assist_cd = 0
        self.dash_cd = 0
        self.pending_assist = 0               # O 键延迟：用于「受击瞬间」反制判定
        self.guard = False
        self.invuln = 0
        self.hurt_t = 0
        self.transformed = False
        self.combo = 0
        self.combo_t = 0
        self.max_combo = 0
        self.dealt = 0                        # 本局累计造成伤害（写入战绩）
        self.flash = 0                        # 命中白闪帧
        self.walk_phase = 0.0
        # ---- v3 新增：状态 / 技能 CD / 闪避 / 被动 ----
        self.status = {}                  # 状态名 -> 剩余帧
        self.status_val = {}              # 状态名 -> 数值（护盾值 / 强化倍率）
        self.cd_s1 = self.cd_s2 = self.cd_s3 = self.cd_ult = 0
        self.dodge_cd = 0
        self.dodge_invuln = 0             # 闪避专用无敌（比受击无敌长）
        self.dodge_success = False
        self.cleanse_cd = 0
        self.scroll_cd = 0
        self.skill_busy = 0               # 技能前摇+有效+后摇期间不能再放技能
        self.idle_t = 0
        self.charged = 0                  # 嗜睡蓄力标记
        self.last_hurt_t = -9999
        self.passive_cd = {}
        self.mark_owner = ""
        self.last_skill = ""

    # ---- 派生属性 ----
    @property
    def atk_mul(self):
        """最终伤害倍率 = 角色倍率 × 变身倍率。"""
        return self.char["stats"]["atk"] * (TRANSFORM_ATK if self.transformed else 1.0)

    @property
    def speed(self):
        """最终移速 = 基础 × 角色倍率 × 变身倍率。"""
        v = MOVE_SPEED * self.char["stats"]["speed"] * (TRANSFORM_SPEED if self.transformed else 1.0)
        if has_status(self, "slow"):
            v *= SLOW_MUL
        if has_status(self, "buff_speed"):
            v *= 1.0 + status_val(self, "buff_speed", BUFF_SPEED_VAL)
        if getattr(self, "arena_edge_slow", False):
            v *= 0.75
        return v

    def rect(self):
        """角色碰撞盒：用于攻击相交判定。"""
        return pygame.Rect(int(self.x - BODY_W / 2), int(self.y - BODY_H), BODY_W, BODY_H)

    def attack_box(self):
        """当前攻击的有效判定盒（朝向前方）。"""
        return pygame.Rect(
            int(self.x if self.facing > 0 else self.x - ATK_REACH),
            int(self.y - 74), ATK_REACH, 56,
        )

    def alive(self):
        return self.hp > 0

    # ---- 对外动作 ----
    def do_transform(self):
        """3 格气变身：清空怒气、强化属性、播放光环。"""
        self.rage = 0
        self.transformed = True
        self.invuln = 20
        self.state, self.state_t = "idle", 0

    def do_counter(self, src, game):
        """受击反制（灵压爆发 / 替身术）：消耗 1 格气、弹开对手、短暂无敌。"""
        self.rage -= COUNTER_COST
        self.pending_assist = 0
        self.invuln = COUNTER_INVULN
        self.state, self.state_t = "idle", 0
        src.vx = -src.facing * 11
        src.state, src.state_t = "hurt", 0
        src.hurt_t = HURT_FRAMES
        game.apply_hit(self, src, DAMAGE["counter"] * self.atk_mul,
                       label=self.char["skills"]["counter"])
        game.spawn_burst(self.x, self.y - 50, self.char["aura"], 26)
        game.floats.append(FloatingText(self.x, self.y - 110,
                                        self.char["skills"]["counter"], self.char["aura"]))
        game.shake = 8

    def start_attack(self, kind):
        """进入攻击状态；kind 决定伤害、浮空与破防。"""
        self.state, self.state_t = "atk", 0
        self.atk_kind = kind
        self.atk_hit = False
        self.atk_cd = ATK_TOTAL + ATK_CD
        self.guard = False

    # ---- 主更新 ----
    def _tick_timers(self, game):
        """每帧递减冷却 / 硬直 / 无敌 / 连击计时；并结算 O 键的延迟援助。"""
        self.state_t += 1
        for name in ("atk_cd", "far_cd", "ult_cd", "assist_cd", "dash_cd",
                     "invuln", "flash", "hurt_t", "combo_t",
                     "cd_s1", "cd_s2", "cd_s3", "cd_ult",
                     "dodge_cd", "dodge_invuln", "cleanse_cd", "scroll_cd",
                     "skill_busy", "idle_t"):
            setattr(self, name, max(0, getattr(self, name) - 1))
        tick_status(self)
        if self.combo_t == 0:
            self.combo = 0
        if self.pending_assist > 0:
            self.pending_assist -= 1
            if self.pending_assist == 0 and self.rage >= ASSIST_COST and self.assist_cd == 0:
                game.summon_assist(self)  # 没被击中 → 延迟结算为「召唤援助」

    def _try_transform(self, game, keys, just, k):
        """J+K / 1+2 变身判定（3 格气，优先级最高）。返回 True 表示本帧已消耗。"""
        if not (keys[k["atk"]] and keys[k["jump"]] and
                (k["atk"] in just or k["jump"] in just) and
                self.rage >= TRANSFORM_COST and not self.transformed):
            return False
        self.do_transform()
        game.spawn_burst(self.x, self.y - 50, self.char["aura"], 46)
        game.floats.append(FloatingText(self.x, self.y - 130,
                                        self.char["skills"]["transform"], COL_GOLD))
        game.shake = 10
        return True

    def _update_busy(self, game):
        """攻击 / 受击 / 冲刺中的状态退出与收尾判定，不读新输入。"""
        if self.state == "hurt" and self.hurt_t == 0:
            self.state = "idle"
        if self.state == "atk" and self.state_t >= ATK_TOTAL:
            self.state = "idle"
        if self.state == "dash" and self.state_t >= DASH_FRAMES:
            self.state = "idle"
            self.vx *= 0.3
        self.resolve_attack(game)
        self.physics(game)

    def _do_movement(self, keys, k, can_guard, game):
        """左右移动 + 走路相位 + 地面状态切换。"""
        moving = False
        step = self.speed * game.frame_scale
        if keys[k["left"]]:
            self.x -= step
            moving = True
        if keys[k["right"]]:
            self.x += step
            moving = True
        self.walk_phase += 0.22 if moving else 0.06
        if self.y >= GROUND_Y - 1:
            self.state = "guard" if can_guard else ("run" if moving else "idle")

    def _do_jump_dash(self, game, keys, just, k):
        """v3.2：只保留跳跃（K / 2）。旧冲刺 L / 3 已停用，位移交给「闪避」。
        起跳时给一点水平惯性，配合空中不推开，就能从对手头顶跳过去绕背。"""
        if k["jump"] in just and self.y >= GROUND_Y - 1:
            self.vy = JUMP_V
            self.state = "jump"
            if keys[k["right"]]:
                self.vx += self.speed * 1.15
            elif keys[k["left"]]:
                self.vx -= self.speed * 1.15
            game.spawn_burst(self.x, self.y - 6, self.char["accent"], 8)
        if k["dash"] in just and self.dash_cd == 0:
            self.vx = self.facing * DASH_SPEED
            self.dash_cd = DASH_CD
            self.state, self.state_t = "dash", 0
            self.invuln = max(self.invuln, 5)
            game.spawn_burst(self.x, self.y - 40, self.char["color"], 12)

    def _do_melee(self, game, keys, just, k):
        """普攻 / W+J 上挑 / S+J 下段破防，三选一。"""
        if k["atk"] not in just or self.atk_cd != 0:
            return
        if keys[k["up"]]:
            self.start_attack("up")       # W+J / ↑+1：浮空
        elif keys[k["guard"]]:
            self.start_attack("down")     # S+J / ↓+1：破防
        else:
            self.start_attack("normal")
        game.spawn_slash(self)

    def _do_far(self, game, keys, just, k):
        """远攻投射物：W+U 斜上 / S+U 下段 / 平射。"""
        if k["far"] not in just or self.far_cd != 0:
            return
        self.far_cd = FAR_CD
        vy = -5.0 if keys[k["up"]] else (3.0 if keys[k["guard"]] else 0.0)
        game.projectiles.append(Projectile(
            self.x + self.facing * 34, self.y - 58,
            self.facing * PROJ_SPEED, vy, self,
            DAMAGE["far"] * self.atk_mul, self.char["color"],
            self.char["skills"]["far"]))
        self.start_attack("far")

    def _do_ult(self, game, just, k):
        """必杀：消耗 1 格气，发射大弹 + 粒子 + 震屏 + 技能名浮字。"""
        if k["ult"] not in just or self.rage < ULT_COST or self.ult_cd != 0:
            return
        self.rage -= ULT_COST
        self.ult_cd = ULT_CD
        self.start_attack("ult")
        game.projectiles.append(Projectile(
            self.x + self.facing * 40, self.y - 62,
            self.facing * ULT_PROJ_SPEED, -1.0, self,
            DAMAGE["ult"] * self.atk_mul, self.char["aura"],
            self.char["skills"]["ult"], big=True))
        game.spawn_burst(self.x + self.facing * 40, self.y - 62,
                         self.char["aura"], 34)
        game.shake = 10
        game.floats.append(FloatingText(self.x, self.y - 132,
                                        self.char["skills"]["ult"], COL_GOLD))

    def _do_assist(self, just, k):
        """援助 / 反制一键两用：按下先挂 COUNTER_WINDOW 帧缓冲。
        期间若被命中 → apply_hit 里转为「灵压爆发 / 替身术」；
        缓冲结束仍没被命中 → _tick_timers 里结算为召唤援助。"""
        if k["assist"] in just and self.pending_assist == 0:
            self.pending_assist = COUNTER_WINDOW

    # ---- 主更新（只做编排，具体动作都在上面的 _do_* 里）----
    def update(self, game, keys, just):
        """每帧更新：计时 → 朝向 → 变身 → 防御 → 分派动作 → 物理 → 判定。"""
        self._tick_timers(game)
        # v3：定身 / 催眠完全不能操作；沉默只能普攻与移动
        if is_disabled(self):
            self.physics(game)
            return
        if has_status(self, "silence"):
            allowed = {self.keys[n] for n in ("left", "right", "up", "guard", "atk", "jump", "dash")}
            just = {x for x in just if x in allowed}
        if not self.alive():
            self.state = "ko"
            self.vx *= 0.85
            self.physics(game)
            return

        k = self.keys
        opp = game.other(self)
        busy = self.state in ("atk", "hurt", "dash")

        # 朝向：仅在自由状态自动面向对手；攻击/受击时锁定 → 绕背可破防
        if self.state in ("idle", "run", "guard", "jump"):
            self.facing = 1 if opp.x >= self.x else -1

        if self._try_transform(game, keys, just, k):
            return

        # 防御（按住 S / ↓，仅地面自由状态）
        can_guard = (keys[k["guard"]] and self.y >= GROUND_Y - 1 and not busy
                     and self.state != "ko")
        self.guard = can_guard

        if busy:
            self._update_busy(game)
            return

        self._do_movement(keys, k, can_guard, game)
        self._do_jump_dash(game, keys, just, k)
        self._do_melee(game, keys, just, k)
        self._do_far(game, keys, just, k)
        self._do_ult(game, just, k)
        self._do_assist(just, k)
        self.resolve_attack(game)
        self.physics(game)

    def resolve_attack(self, game):
        """近身攻击在有效帧内做一次矩形相交判定。"""
        # v3：技能由 pending_skills 统一结算，这里跳过，避免 DAMAGE["skill"] 查不到
        if self.state != "atk" or self.atk_kind in ("far", "ult", "skill"):
            return
        # 只有「前摇结束后 ~ 有效帧结束」这段窗口才判定；其余帧是前摇/后摇
        if (self.state_t < ATK_STARTUP
                or self.state_t > ATK_STARTUP + ATK_ACTIVE or self.atk_hit):
            return
        opp = game.other(self)
        if not self.attack_box().colliderect(opp.rect()):
            return
        self.atk_hit = True
        kind = self.atk_kind
        game.apply_hit(self, opp, DAMAGE[kind] * self.atk_mul,
                       break_guard=(kind == "down"),
                       launch=(LAUNCH_V if kind == "up" else 0.0),
                       label=self.char["skills"].get(kind, kind))

    def physics(self, game):
        """重力、地面、场地边界、击退衰减。"""
        grav = GRAVITY * (0.65 if getattr(game, "arena_effect", "none") == "low_gravity" else 1.0)
        self.vy += grav
        self.y += self.vy
        self.x += self.vx
        self.vx *= 0.86
        if abs(self.vx) < 0.15:
            self.vx = 0.0
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0.0
            if self.state == "jump":
                self.state = "idle"
        self.x = clamp(self.x, ARENA_LEFT + BODY_W / 2, ARENA_RIGHT - BODY_W / 2)


class Projectile:
    """飞行道具：远攻 / 必杀都用它；带拖尾与生命周期。"""

    def __init__(self, x, y, vx, vy, owner, dmg, color, label, big=False):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.owner = owner
        self.dmg = dmg
        self.color = color
        self.label = label
        self.radius = PROJ_RADIUS * (2.0 if big else 1.0)
        self.life = PROJ_LIFE
        self.trail = []
        self.dead = False

    def update(self, game):
        self.life -= 1
        self.trail.append((self.x, self.y))
        if len(self.trail) > 9:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY * 0.18
        target = game.other(self.owner)
        box = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                          self.radius * 2, self.radius * 2)
        spec = getattr(self, "v3_spec", None)
        if box.colliderect(target.rect()) and not target.invuln:
            if spec:
                skill_hit(game, self.owner, target, spec,
                          getattr(self, "v3_label", self.label))
            else:
                game.apply_hit(self.owner, target, self.dmg,
                               launch=(-6.0 if self.radius > PROJ_RADIUS else 0.0),
                               label=self.label, rage_gain=RAGE_ON_PROJ)
            game.spawn_burst(self.x, self.y, self.color, 20)
            game.shake = max(game.shake, SHAKE_ON_ULT if self.radius > PROJ_RADIUS else 5)
            self.dead = True
        if self.life <= 0 or self.x < -60 or self.x > SCREEN_W + 60 or self.y > SCREEN_H + 60:
            self.dead = True

    def draw(self, surf):
        for i, (tx, ty) in enumerate(self.trail):
            a = (i + 1) / float(len(self.trail) + 1)
            pygame.draw.circle(surf, shade(self.color, 0.5 + 0.5 * a),
                               (int(tx), int(ty)), int(self.radius * a * 0.8))
        pygame.draw.circle(surf, shade(self.color, 1.35), (int(self.x), int(self.y)),
                           int(self.radius))
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)),
                           max(2, int(self.radius * 0.35)))


class Assist:
    """援助角色：从己方身后冲向对手，命中一次后离场。"""

    def __init__(self, owner):
        self.owner = owner
        self.x = owner.x - owner.facing * 150
        self.y = GROUND_Y - 52
        self.vx = owner.facing * 15.0
        self.color = owner.char["accent"]
        self.label = owner.char["skills"]["assist"]
        self.dmg = DAMAGE["assist"] * owner.atk_mul
        self.hit = False
        self.life = 90
        self.dead = False

    def update(self, game):
        self.x += self.vx
        self.life -= 1
        target = game.other(self.owner)
        box = pygame.Rect(int(self.x - 22), int(self.y - 26), 44, 52)
        if not self.hit and box.colliderect(target.rect()) and not target.invuln:
            self.hit = True
            game.apply_hit(self.owner, target, self.dmg, label=self.label)
            game.spawn_burst(self.x, self.y, self.color, 22)
            game.shake = max(game.shake, 6)
        if self.life <= 0 or self.x < -100 or self.x > SCREEN_W + 100:
            self.dead = True

    def draw(self, surf):
        pygame.draw.circle(surf, shade(self.color, 1.2), (int(self.x), int(self.y)), 22)
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), 9)
        draw_text(surf, self.label, self.x, self.y - 46, 16, self.color, align="center")


class Particle:
    """通用粒子：命中火花、落地烟尘、变身光点。"""

    def __init__(self, x, y, color, speed=4.0, life=28):
        ang = random.uniform(0, math.tau)
        self.vx = math.cos(ang) * speed * random.uniform(0.3, 1.0)
        self.vy = math.sin(ang) * speed * random.uniform(0.3, 1.0) - 1.0
        self.x, self.y = x, y
        self.color = color
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)
        self.dead = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.16
        self.vx *= 0.97
        self.life -= 1
        if self.life <= 0:
            self.dead = True

    def draw(self, surf):
        a = self.life / float(self.max_life)
        c = shade(self.color, 0.45 + 0.75 * a)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), max(1, int(self.size * a)))


class FloatingText:
    """上浮文字：技能名、伤害数字、变身提示。"""

    def __init__(self, x, y, text, color, size=22):
        self.x, self.y = x, y
        self.text = str(text)
        self.color = color
        self.size = size
        self.life = 52
        self.dead = False

    def update(self):
        self.y -= 0.9
        self.life -= 1
        if self.life <= 0:
            self.dead = True

    def draw(self, surf):
        a = clamp(self.life / 30.0, 0.0, 1.0)
        c = tuple(int(v * a + 20 * (1 - a)) for v in self.color)
        draw_text(surf, self.text, self.x, self.y, self.size, c, True, "center")


# ==============================================================================
# ⑤ 渲染层 —— 背景 / Q 版角色 / 标志物 / 打击特效 / HUD
# ==============================================================================

def draw_background(surf, t, game=None):
    """战斗背景：转交给 v3 场地绘制（9 种风格 + 可选机制），全部代码绘制。"""
    draw_arena_bg(surf, t, game)


def _trait_deepseek(surf, f, cx, cy, t, col, acc, face, sway):
    """铁盆（饭盆）+ 鲸尾 + 女仆头饰。"""
    pygame.draw.arc(surf, (150, 156, 168), (cx - 20, cy - 8, 40, 26), math.pi, 0, 4)
    pygame.draw.line(surf, (150, 156, 168), (cx - 20, cy + 5), (cx + 20, cy + 5), 3)
    pygame.draw.polygon(surf, col, [(cx - face * 24, cy + 42),
                                    (cx - face * 52, cy + 30 + sway),
                                    (cx - face * 50, cy + 54 + sway)])
    pygame.draw.rect(surf, acc, (cx - 12, cy - 12, 24, 5), border_radius=2)


def _trait_chatgpt(surf, f, cx, cy, t, col, acc, face, sway):
    """白龙双角 + 龙尾。"""
    for s in (-1, 1):
        pygame.draw.polygon(surf, acc, [(cx + s * 12, cy - 12),
                                        (cx + s * 20, cy - 32),
                                        (cx + s * 6, cy - 16)])
    pygame.draw.arc(surf, col, (cx - face * 46, cy + 34, 54, 40), 0, math.pi, 4)


def _trait_claude(surf, f, cx, cy, t, col, acc, face, sway):
    """放射花朵头饰 + 抱着的书。"""
    for i in range(8):
        a = i * math.pi / 4
        pygame.draw.line(surf, acc,
                         (cx + math.cos(a) * 7, cy - 18 + math.sin(a) * 7),
                         (cx + math.cos(a) * 15, cy - 18 + math.sin(a) * 15), 2)
    pygame.draw.rect(surf, (58, 48, 44), (cx + face * 12 - 12, cy + 30, 26, 20), border_radius=2)
    pygame.draw.line(surf, acc, (cx + face * 12 + 1, cy + 30), (cx + face * 12 + 1, cy + 50), 2)


def _trait_gemini(surf, f, cx, cy, t, col, acc, face, sway):
    """猫耳 + 猫尾 + 异色瞳。"""
    for s in (-1, 1):
        pygame.draw.polygon(surf, col, [(cx + s * 8, cy - 14),
                                        (cx + s * 22, cy - 34),
                                        (cx + s * 22, cy - 10)])
    pygame.draw.arc(surf, col, (cx - face * 44, cy + 26, 40, 44), 0, math.pi, 4)
    pygame.draw.circle(surf, (255, 210, 80), (int(cx - 7 + face * 3), int(cy + 2)), 3)
    pygame.draw.circle(surf, (90, 220, 235), (int(cx + 7 + face * 3), int(cy + 2)), 3)


def _trait_qwen(surf, f, cx, cy, t, col, acc, face, sway):
    """折扇 + 古风长袍下摆 + 流苏。"""
    pts = [(cx + face * 18, cy + 34)]
    for i in range(7):
        a = -0.9 + i * 0.3
        pts.append((cx + face * 18 + math.cos(a) * 26 * face,
                    cy + 34 + math.sin(a) * 26))
    pygame.draw.polygon(surf, acc, pts)
    pygame.draw.line(surf, col, (cx + face * 18, cy + 34),
                     (cx + face * 40, cy + 16), 2)
    pygame.draw.line(surf, COL_GOLD, (cx - face * 18, cy + 46),
                     (cx - face * 18, cy + 62 + sway), 2)


def _trait_kimi(surf, f, cx, cy, t, col, acc, face, sway):
    """月相 + 长笛。"""
    pygame.draw.circle(surf, acc, (int(cx), int(cy - 22)), 9)
    pygame.draw.circle(surf, COL_BG_TOP, (int(cx + 4), int(cy - 25)), 9)
    pygame.draw.line(surf, acc, (cx + face * 14, cy + 26), (cx + face * 46, cy + 18), 4)
    for i in range(3):
        pygame.draw.circle(surf, COL_TEXT,
                           (int(cx + face * (20 + i * 9)), int(cy + 24 - i * 2)), 2)


def _trait_glm(surf, f, cx, cy, t, col, acc, face, sway):
    """Z 标志 + 抱黑书 + 狐狸耳。"""
    for s in (-1, 1):
        pygame.draw.polygon(surf, col, [(cx + s * 10, cy - 12),
                                        (cx + s * 18, cy - 30),
                                        (cx + s * 22, cy - 10)])
    zx, zy = cx - face * 20, cy + 26
    pygame.draw.lines(surf, COL_GOLD, False,
                      [(zx - 7, zy - 7), (zx + 7, zy - 7),
                       (zx - 7, zy + 7), (zx + 7, zy + 7)], 2)
    pygame.draw.rect(surf, (28, 30, 40), (cx + face * 10 - 12, cy + 34, 24, 18),
                     border_radius=2)


def _trait_grok(surf, f, cx, cy, t, col, acc, face, sway):
    """双马尾 + 巨斧（攻击时斧头更靠前）。"""
    for s in (-1, 1):
        pygame.draw.circle(surf, col, (int(cx + s * 25), int(cy - 4 + sway * s)), 9)
        pygame.draw.line(surf, col, (cx + s * 16, cy - 10), (cx + s * 25, cy - 4), 3)
    ax = cx + face * (34 if f.state == "atk" else 22)
    pygame.draw.line(surf, (90, 70, 70), (ax, cy + 8), (ax + face * 8, cy + 48), 4)
    pygame.draw.polygon(surf, acc, [(ax + face * 8, cy + 6),
                                    (ax + face * 26, cy + 12),
                                    (ax + face * 8, cy + 26)])


# 新增角色只需写一个 _trait_xxx 并在这里注册，不用动 draw_traits 本身
TRAIT_DRAWERS = {
    "deepseek": _trait_deepseek, "chatgpt": _trait_chatgpt,
    "claude": _trait_claude, "gemini": _trait_gemini,
    "qwen": _trait_qwen, "kimi": _trait_kimi,
    "glm": _trait_glm, "grok": _trait_grok,
}


def draw_traits(surf, f, cx, cy, t):
    """按角色 id 分派标志物绘制（零素材也能看出谁是谁）。
    想换真立绘，把 assets/<id>.png 放好即可，draw_fighter 会自动优先 blit。"""
    fn = TRAIT_DRAWERS.get(f.char["id"])
    if fn is None:
        return
    fn(surf, f, cx, cy, t, f.char["color"], f.char["accent"],
       f.facing, math.sin(t * 0.08 + f.side) * 3)


def _draw_aura(surf, f, cx, cy):
    """变身光环：三层椭圆，越外层越淡。"""
    if not f.transformed:
        return
    for i in range(3):
        pygame.draw.ellipse(surf, shade(f.char["aura"], 0.6 + i * 0.2),
                            (cx - 40 - i * 8, cy - 56 - i * 6,
                             80 + i * 16, 112 + i * 12), 2)


def _draw_shadow(surf, f, cx):
    """脚底椭圆影子，让角色「踩」在地面线上。"""
    pygame.draw.ellipse(surf, (10, 12, 26), (cx - 30, int(f.y) - 8, 60, 12))


def _try_portrait(surf, f, cx, show_portrait):
    """立绘替换接口：assets/<角色id>.png 存在就等比缩放绘制并返回 True。
    没有任何图片时返回 False，交给 _draw_* 系列画 Q 版。"""
    portrait = load_portrait(f.char["id"]) if show_portrait else None
    if portrait is None:
        return False
    h = 116
    w = int(portrait.get_width() * h / max(1, portrait.get_height()))
    img = pygame.transform.smoothscale(portrait, (w, h))
    if f.facing < 0:
        img = pygame.transform.flip(img, True, False)
    surf.blit(img, (cx - w // 2, int(f.y) - h))
    if f.flash > 0:
        pygame.draw.rect(surf, (255, 255, 255),
                         (cx - w // 2, int(f.y) - h, w, h), 3, border_radius=8)
    return True


def _pose_offset(f):
    """按动作状态算身体倾斜 / 上下浮动 / KO 倒地偏移。"""
    lean = 0
    if f.state == "hurt":
        lean = -f.facing * 8
    elif f.state == "dash":
        lean = f.facing * 10
    elif f.state == "ko":
        lean = -f.facing * 34
    bob = math.sin(f.walk_phase) * (3 if f.state == "run" else 1.2)
    bx = int(f.x) + lean
    by = int(f.y - 52) + (0 if f.state != "jump" else -6)
    return bx, by, bob


def _draw_ko(surf, f, bx, col, acc):
    """KO 倒地：横躺的简化人形 + 红色 K.O. 字。"""
    pygame.draw.ellipse(surf, shade(col, 0.8), (bx - 40, int(f.y) - 26, 80, 22))
    pygame.draw.circle(surf, acc, (bx + f.facing * 36, int(f.y) - 16), 13)
    draw_text(surf, "K.O.", bx, int(f.y) - 56, 22, COL_HP_LOW, True, "center")


def _draw_legs(surf, f, bx, by, col):
    """双腿：跑动时按 walk_phase 前后摆。"""
    swing = math.sin(f.walk_phase) * 9 if f.state == "run" else 0
    pygame.draw.line(surf, shade(col, 0.65), (bx - 8, by + 24),
                     (bx - 10 + swing, int(f.y) - 2), 7)
    pygame.draw.line(surf, shade(col, 0.65), (bx + 8, by + 24),
                     (bx + 10 - swing, int(f.y) - 2), 7)


def _draw_body(surf, f, bx, by, col, acc):
    """身体：裙摆梯形 + 腰带。"""
    pygame.draw.polygon(surf, col, [(bx - 16, by - 8), (bx + 16, by - 8),
                                    (bx + 24, by + 30), (bx - 24, by + 30)])
    pygame.draw.rect(surf, acc, (bx - 16, by + 8, 32, 4), border_radius=2)


def _draw_arms(surf, f, bx, by, col, acc):
    """手臂：攻击前伸 / 防御架盾 / 其他自然下垂。"""
    if f.state == "atk":
        hx = bx + f.facing * 40
        pygame.draw.line(surf, shade(col, 1.1),
                         (bx + f.facing * 10, by - 2), (hx, by - 10), 8)
        pygame.draw.circle(surf, acc, (int(hx), int(by - 10)), 8)
    elif f.state == "guard":
        pygame.draw.line(surf, shade(col, 1.1),
                         (bx - 10, by), (bx + f.facing * 8, by - 20), 8)
        pygame.draw.arc(surf, COL_P1 if f.side == 1 else COL_P2,
                        (bx - 26, by - 34, 52, 62), -1.1, 1.1, 3)
    else:
        pygame.draw.line(surf, shade(col, 1.0), (bx - 14, by), (bx - 20, by + 20), 7)
        pygame.draw.line(surf, shade(col, 1.0), (bx + 14, by), (bx + 20, by + 20), 7)


def _draw_head(surf, f, bx, by, bob, col, acc):
    """头 / 头发 / 眼睛，返回头部中心 y 供后续特效与阵营标定位。"""
    hcy = int(by - 24 + bob)
    pygame.draw.circle(surf, acc, (bx, hcy), 20)
    pygame.draw.ellipse(surf, col, (bx - 21, hcy - 22, 42, 24))
    pygame.draw.circle(surf, (30, 30, 48), (bx - 7 + f.facing * 3, hcy + 2), 3)
    pygame.draw.circle(surf, (30, 30, 48), (bx + 7 + f.facing * 3, hcy + 2), 3)
    return hcy


def _draw_status_rings(surf, f, bx, hcy):
    """命中白闪 / 无敌金圈 / 头顶 P1-P2 阵营标。"""
    if f.flash > 0:
        pygame.draw.circle(surf, (255, 255, 255), (bx, hcy - 4), 26, 3)
    if f.invuln > 0 and (f.invuln // 4) % 2 == 0:
        pygame.draw.circle(surf, COL_GOLD, (bx, hcy - 4), 30, 2)
    tag_col = COL_P1 if f.side == 1 else COL_P2
    draw_text(surf, "P" + str(f.side), bx, hcy - 54, 16, tag_col, True, "center")


def draw_fighter(surf, f, t, show_portrait=True):
    """角色绘制编排：光环 → 影子 → 立绘(有则直接返回) → Q 版姿态 → 标志物 → 特效。
    姿态覆盖：待机 / 跑 / 跳 / 攻击 / 防御 / 冲刺 / 受击 / KO / 变身。"""
    cx, cy = int(f.x), int(f.y - 52)
    col, acc = f.char["color"], f.char["accent"]
    _draw_aura(surf, f, cx, cy)
    _draw_shadow(surf, f, cx)
    if _try_portrait(surf, f, cx, show_portrait):
        return
    bx, by, bob = _pose_offset(f)
    if f.state == "ko":
        _draw_ko(surf, f, bx, col, acc)
        return
    _draw_legs(surf, f, bx, by, col)
    _draw_body(surf, f, bx, by, col, acc)
    _draw_arms(surf, f, bx, by, col, acc)
    hcy = _draw_head(surf, f, bx, by, bob, col, acc)
    draw_traits(surf, f, bx, hcy, t)
    _draw_status_rings(surf, f, bx, hcy)


def draw_slash(surf, x, y, facing, color, t):
    """近身攻击刀光：一段扇形弧线，随帧淡出。"""
    a = clamp(t / float(ATK_ACTIVE), 0.0, 1.0)
    if a <= 0:
        return
    r = 46 + (1 - a) * 24
    start = -0.9 if facing > 0 else math.pi - 0.9
    pygame.draw.arc(surf, shade(color, 1.4),
                    (int(x + facing * 12 - r), int(y - 74 - r), int(r * 2), int(r * 2)),
                    start, start + 1.8, max(2, int(6 * a)))


# ==============================================================================
# ⑥ 应用主体 —— 场景（页面）管理 / 战斗规则 / 输入分发
# ==============================================================================


# ==============================================================================
# ③-A v3 玩法引擎 —— 状态效果 / 技能 / 联动 / 被动 / 秘卷 / 场地
#   全部模块级函数，只操作 Fighter 实例属性，不改动原有类方法结构。
# ==============================================================================

def kit_of(f):
    """取角色的技能组；没配过就回退到 deepseek（保证加角色不崩）。"""
    return SKILL_KITS.get(f.char["id"], SKILL_KITS["deepseek"])


def skill_spec(char_id, slot):
    """把 SKILL_BASE 默认值与角色自定义 spec 合并，改数值只改数据表。"""
    base = dict(SKILL_BASE.get(slot, SKILL_BASE["s1"]))
    kit = SKILL_KITS.get(char_id, SKILL_KITS["deepseek"])
    base.update(kit["skills"].get(slot, {}))
    return base


def add_status(f, name, frames, val=0.0):
    """挂一个状态；负面状态会被「免控」挡掉，护盾/增益可叠加数值。"""
    if name in NEGATIVE_STATUS and has_status(f, "cleanse_immune"):
        return False
    f.status[name] = max(f.status.get(name, 0), int(frames))
    if val:
        f.status_val[name] = max(f.status_val.get(name, 0.0), float(val))
    return True


def has_status(f, name):
    return f.status.get(name, 0) > 0


def status_val(f, name, default=0.0):
    return f.status_val.get(name, default) if has_status(f, name) else default


def tick_status(f):
    """每帧递减状态计时；到期清掉数值。"""
    for k in list(f.status.keys()):
        f.status[k] -= 1
        if f.status[k] <= 0:
            f.status.pop(k, None)
            f.status_val.pop(k, None)


def cleanse(f):
    """净化：解除全部负面（含联动标记），增益保留。"""
    cleared = 0
    for k in list(f.status.keys()):
        if k in NEGATIVE_STATUS or k.startswith("mark"):
            f.status.pop(k, None)
            f.status_val.pop(k, None)
            cleared += 1
    return cleared


def is_disabled(f, for_skill=False):
    """定身 / 催眠：完全不能操作；沉默：只能普攻与移动。"""
    if has_status(f, "stun") or has_status(f, "sleep"):
        return True
    if for_skill and has_status(f, "silence"):
        return True
    return False


def dodge_cd(f):
    """九命灵动被动：闪避冷却缩短。"""
    kit = kit_of(f)
    mul = 1.0 - kit["passive"]["val"] if kit["passive"]["type"] == "dodge_cd" else 1.0
    return max(30, int(DODGE_CD * mul))


def skill_damage(f, spec, target):
    """最终伤害 = 基础 × 角色攻击倍率 × 强化 × 满气加成 × 嗜睡蓄力。"""
    kit = kit_of(f)
    dmg = spec.get("dmg", 50) * f.atk_mul
    if has_status(f, "buff_atk"):
        dmg *= 1.0 + status_val(f, "buff_atk", BUFF_ATK_VAL)
    if kit["passive"]["type"] == "full_rage_bonus" and f.rage >= RAGE_MAX:
        dmg *= 1.0 + kit["passive"]["val"]
    if getattr(f, "charged", 0) > 0:
        dmg *= 1.0 + kit["passive"]["val"]
        f.charged = 0
    return dmg


def mark_key(char_id):
    return "mark_" + char_id


def apply_mark(src, target, kit):
    """技能命中后给对手挂本角色的联动标记。"""
    add_status(target, mark_key(src.char["id"]), 240, 1.0)
    target.mark_owner = src.char["id"]


def check_link(src, target, kit, spec):
    """命中带标记目标 → 触发联动，返回额外伤害 / 额外状态。"""
    if not spec.get("consume"):
        return None
    key = mark_key(src.char["id"])
    if not has_status(target, key):
        return None
    target.status.pop(key, None)
    link = dict(spec.get("link", {}))
    return link


def skill_hit(game, src, target, spec, label=None, bonus=None):
    """统一的技能命中结算：伤害 → 状态 → 标记 → 联动 → 自身收益。"""
    if not target.alive():
        return False
    kit = kit_of(src)
    dmg = skill_damage(src, spec, target)
    link = check_link(src, target, kit, spec)
    if link:
        dmg += link.get("dmg", 0)
    if bonus:
        dmg += bonus
    # 霸体的代价：破霸体技能额外受伤；霸体本身不免疫控制
    if has_status(target, "super_armor") and (spec.get("pierce_armor") or (link and link.get("pierce_armor"))):
        dmg *= 1.0 + SUPER_ARMOR_EXTRA
    ok = game.apply_hit(
        src, target, dmg,
        break_guard=bool(spec.get("break_guard")),
        launch=float(spec.get("launch", 0.0)) + (link.get("launch", 0.0) if link else 0.0),
        label=label or spec.get("name", "技能"),
        rage_gain=spec.get("rage_gain", RAGE_ON_HIT))
    if not ok:
        return False
    # 命中后的附带效果
    eff_status = spec.get("status")
    frames = int(spec.get("status_frames", 0))
    if eff_status and frames:
        add_status(target, eff_status, frames, spec.get("status_val", 0.0))
    if link:
        lk_status, lk_frames = link.get("status"), int(link.get("status_frames", link.get("frames", 0)))
        if lk_status and lk_frames:
            add_status(target, lk_status, lk_frames, link.get("status_val", 0.0))
        if link.get("knock"):
            target.vx += float(link["knock"]) * src.facing
        if link.get("self_heal"):
            src.hp = min(src.max_hp, src.hp + float(link["self_heal"]))
        if link.get("self_rage"):
            src.rage = min(RAGE_MAX, src.rage + float(link["self_rage"]))
        if link.get("status") == "buff_speed":
            add_status(src, "buff_speed", lk_frames, BUFF_SPEED_VAL)
        game.shake = max(game.shake, 9)
        game.floats.append(FloatingText(target.x, target.y - 138,
                                        "联动！" + kit["link_desc"][:6], COL_GOLD, 20))
    if spec.get("tag"):
        apply_mark(src, target, kit)
    if spec.get("knock"):
        target.vx += float(spec["knock"]) * src.facing
    if spec.get("self_heal"):
        src.hp = min(src.max_hp, src.hp + float(spec["self_heal"]))
    if spec.get("self_rage"):
        src.rage = min(RAGE_MAX, src.rage + float(spec["self_rage"]))
    if spec.get("self_cleanse"):
        cleanse(src)
    return True


def spawn_skill_proj(game, f, spec, label):
    """投射物类技能：支持多弹、大弹、命中附状态 / 标记 / 联动。"""
    n = int(spec.get("count", 1))
    speed = float(spec.get("proj", PROJ_SPEED))
    big = spec["kind"].startswith("ult")
    radius = float(spec.get("radius", 0))
    for i in range(n):
        vy = -1.0 if big else (i - (n - 1) / 2.0) * 1.4
        p = Projectile(f.x + f.facing * 40, f.y - 60 - i * 6,
                       f.facing * speed, vy, f,
                       spec.get("dmg", 50) * f.atk_mul,
                       f.char["aura"], label, big=big)
        p.v3_spec = spec
        p.v3_label = label
        if radius:
            p.radius = radius
        game.projectiles.append(p)
    game.spawn_burst(f.x + f.facing * 40, f.y - 60, f.char["aura"], 18)


def resolve_skill_melee(game, f, spec, label):
    """近身 / 突进技能：矩形判定盒，命中即结算。"""
    reach = float(spec.get("reach", SKILL_BASE["s1"]["reach"]))
    box = pygame.Rect(int(f.x if f.facing > 0 else f.x - reach),
                      int(f.y - 96), int(reach), 96)
    target = game.other(f)
    if box.colliderect(target.rect()):
        skill_hit(game, f, target, spec, label)
        game.spawn_slash(f)
    else:
        game.floats.append(FloatingText(f.x, f.y - 110, "落空", COL_DIM, 16))
    game.spawn_burst(f.x + f.facing * reach * 0.6, f.y - 60, f.char["color"], 10)


def resolve_skill_aoe(game, f, spec, label, radius_override=None):
    """范围技能：以自身为圆心的距离判定，带扩散光圈演出。"""
    r = float(radius_override or spec.get("radius", 130))
    target = game.other(f)
    game.skill_rings.append({"x": f.x, "y": f.y - 48, "r": r,
                             "t": 18, "max": 18, "color": f.char["aura"]})
    if abs(target.x - f.x) <= r and abs(target.y - f.y) < 130:
        skill_hit(game, f, target, spec, label)
    game.spawn_burst(f.x, f.y - 48, f.char["aura"], 26)
    game.shake = max(game.shake, 7 if not spec["kind"].startswith("ult") else 12)


def pending_skill(game, f, action, spec, label):
    """登记一个带前摇的技能；到 startup 帧才真正出判定，给对手闪避窗口。"""
    game.pending_skills.append({
        "owner": f, "action": action, "spec": spec, "label": label,
        "t": int(spec.get("startup", 6)), "kind": spec["kind"],
    })
    f.state, f.state_t = "atk", 0
    f.atk_kind = "skill"
    f.skill_busy = int(spec.get("startup", 6)) + int(spec.get("active", 6)) + int(spec.get("recovery", 10))
    f.last_skill = label


def tick_pending_skills(game):
    """推进所有前摇中的技能；到点结算并清掉。"""
    still = []
    for ps in game.pending_skills:
        ps["t"] -= 1
        if ps["t"] > 0:
            still.append(ps)
            continue
        f, spec, label = ps["owner"], ps["spec"], ps["label"]
        if not f.alive():
            continue
        kind = ps["kind"]
        if kind in ("melee", "dash_strike"):
            if kind == "dash_strike":
                f.x = clamp(f.x + f.facing * 62, ARENA_LEFT + BODY_W / 2, ARENA_RIGHT - BODY_W / 2)
            resolve_skill_melee(game, f, spec, label)
        elif kind in ("aoe", "ult_aoe"):
            link = spec.get("link", {}) if spec.get("consume") else {}
            resolve_skill_aoe(game, f, spec, label,
                              radius_override=link.get("radius") if spec.get("consume") else None)
        else:
            spawn_skill_proj(game, f, spec, label)
    game.pending_skills = still


def cast_skill(game, f, action):
    """技能总入口。返回 False 表示因状态 / 冷却 / 气不足没放出来。"""
    if not f.alive() or is_disabled(f, for_skill=True):
        return False
    if getattr(f, "skill_busy", 0) > 0 and action != "atk":
        return False
    kit = kit_of(f)
    spec = skill_spec(f.char["id"], action)
    cd_key = "cd_" + action
    cost = int(spec.get("rage", 0))
    if getattr(f, cd_key, 0) > 0 or f.rage < cost:
        return False
    f.rage -= cost
    setattr(f, cd_key, int(spec.get("cd", 96)))
    label = spec.get("name", SKILL_LABEL.get(action, action))
    game.floats.append(FloatingText(f.x, f.y - 124, label, f.char["aura"], 18))
    pending_skill(game, f, action, spec, label)
    if action == "ult":
        game.shake = max(game.shake, SHAKE_ON_ULT)
    return True


def do_dodge(game, f):
    """闪避：小位移 + 长无敌，主要用来躲技能；不消耗气，靠 CD 平衡。"""
    if not f.alive() or is_disabled(f):
        return False
    if f.dodge_cd > 0:
        return False
    f.dodge_cd = dodge_cd(f)
    f.dodge_invuln = DODGE_INVULN
    f.invuln = max(f.invuln, DODGE_INVULN)
    # 默认朝身后闪，按住方向时朝该方向
    k = f.keys
    held = game.touch_held      # 是「按住的键码集合」，不是数组，用成员判断
    dx = 0
    if k["left"] in held:
        dx = -1
    elif k["right"] in held:
        dx = 1
    if dx == 0:
        dx = -f.facing
    f.x = clamp(f.x + dx * DODGE_DIST,
                ARENA_LEFT + BODY_W / 2, ARENA_RIGHT - BODY_W / 2)
    f.state, f.state_t = "dash", 0
    f.dodge_success = False
    game.spawn_burst(f.x, f.y - 40, f.char["color"], 14)
    game.floats.append(FloatingText(f.x, f.y - 112, "闪避", COL_TEXT, 16))
    return True


def do_cleanse(game, f):
    """净化：解除自身全部负面 + 短免控；对控制流角色的关键反制。"""
    if not f.alive() or f.cleanse_cd > 0:
        return False
    f.cleanse_cd = CLEANSE_CD
    n = cleanse(f)
    add_status(f, "cleanse_immune", CLEANSE_IMMUNE, 1.0)
    game.spawn_burst(f.x, f.y - 50, (140, 235, 200), 20)
    game.floats.append(FloatingText(f.x, f.y - 116,
                                    "净化 %d" % n if n else "净化", (140, 235, 200), 18))
    return True


def do_scroll(game, f):
    """秘卷：开局选一个的功能性技能。统一 CD，各有代价，避免碾压选项。"""
    if not f.alive() or is_disabled(f, for_skill=True) or f.scroll_cd > 0:
        return False
    sc = SCROLLS.get(game.scroll_id, SCROLLS[DEFAULT_SCROLL])
    f.scroll_cd = int(sc.get("cd", SCROLL_CD_FALLBACK))
    kind = sc["kind"]
    target = game.other(f)
    if kind == "self":
        add_status(f, sc["status"], int(sc.get("frames", 180)),
                   float(sc.get("val", BUFF_ATK_VAL)) if sc.get("status") == "buff_atk" else 0.0)
        if sc["status"] == "buff_atk":
            add_status(f, "buff_speed", int(sc.get("frames", 180)), BUFF_SPEED_VAL)
    elif kind == "cleanse":
        cleanse(f)
        add_status(f, "cleanse_immune", int(sc.get("frames", 90)), 1.0)
    elif kind == "rage":
        f.rage = min(RAGE_MAX, f.rage + float(sc.get("val", 80)))
    elif kind == "shield":
        add_status(f, "shield", int(sc.get("frames", 300)), float(sc.get("val", 120)))
    elif kind == "aoe":
        game.skill_rings.append({"x": f.x, "y": f.y - 48, "r": float(sc["radius"]),
                                 "t": 20, "max": 20, "color": f.char["aura"]})
        if abs(target.x - f.x) <= sc["radius"]:
            game.apply_hit(f, target, sc.get("dmg", 20), label=sc["name"])
            add_status(target, sc["status"], int(sc["frames"]), 1.0)
    elif kind == "proj":
        sp = {"name": sc["name"], "kind": "proj", "dmg": sc.get("dmg", 35),
              "proj": sc.get("proj", 11), "status": sc["status"],
              "status_frames": sc["frames"], "proj_radius": 20}
        spawn_skill_proj(game, f, sp, sc["name"])
    game.floats.append(FloatingText(f.x, f.y - 124, "秘卷·" + sc["name"], COL_GOLD, 18))
    game.spawn_burst(f.x, f.y - 46, COL_GOLD, 18)
    return True


def dispatch_actions(game, just):
    """把 just 里的 (action, side) 元组翻译成动作；键盘与触屏走同一条路。"""
    acts = [x for x in just if isinstance(x, tuple) and len(x) == 2
            and x[0] in ACTION_ORDER and x[1] in (1, 2)]
    for action, side in acts:
        f = game.p1 if side == 1 else game.p2
        if f is None:
            continue
        if action == "atk":
            if not is_disabled(f) and f.atk_cd == 0:
                f.start_attack("normal")
                game.spawn_slash(f)
        elif action == "dodge":
            do_dodge(game, f)
        elif action == "cleanse":
            do_cleanse(game, f)
        elif action == "scroll":
            do_scroll(game, f)
        else:
            cast_skill(game, f, action)


def tick_passive(game, f):
    """8 种被动统一分发：全部有内置 CD / 触发条件，不会无限叠。"""
    if not f.alive():
        return
    kit = kit_of(f)
    p = kit["passive"]
    typ, cd, val = p["type"], int(p.get("cd", 0)), float(p.get("val", 0))
    key = "passive_t_" + f.char["id"]
    cdmap = getattr(f, "passive_cd", None)
    if cdmap is None:
        cdmap = f.passive_cd = {}
    if typ == "idle_charge":
        if f.state in ("idle", "guard") and abs(f.vx) < 0.5:
            f.idle_t = getattr(f, "idle_t", 0) + 1
            if f.idle_t >= cd:
                f.charged = 1
        else:
            f.idle_t = 0
        return
    if typ in ("dodge_cd", "full_rage_bonus", "reflect", "damage_cap"):
        return   # 这类被动在命中/受击时机结算，不按帧跳
    remain = cdmap.get(key, 0)
    if remain > 0:
        cdmap[key] = remain - 1
        return
    if typ == "rage_tick":
        if game.t - getattr(f, "last_hurt_t", -9999) >= 180:
            f.rage = min(RAGE_MAX, f.rage + val)
            cdmap[key] = cd
    elif typ == "shield_tick":
        add_status(f, "shield", 360, val)
        cdmap[key] = cd
    elif typ == "hp_tick":
        f.hp = min(f.max_hp, f.hp + f.max_hp * val)
        cdmap[key] = cd


def tick_arena(game):
    """场地机制：默认 none 什么都不做；开启后按 ARENA_EFFECTS 生效。"""
    eff = game.arena_effect
    if eff == "none":
        return
    left, right = CENTER_ZONE
    for f in (game.p1, game.p2):
        if not f or not f.alive():
            continue
        in_center = left <= f.x <= right
        if eff == "center_rage" and in_center:
            f.rage = min(RAGE_MAX, f.rage + 10.0 / FPS)
        elif eff == "heal_zone" and in_center:
            f.hp = min(f.max_hp, f.hp + f.max_hp * 0.006 / FPS)
        elif eff == "wind":
            phase = (game.t // WIND_PERIOD) % 2
            f.x += WIND_FORCE if phase == 0 else -WIND_FORCE
        elif eff == "energy_orb":
            for orb in game.orbs[:]:
                if math.hypot(f.x - orb["x"], f.y - 50 - orb["y"]) <= ORB_PICK_RADIUS:
                    f.hp = min(f.max_hp, f.hp + 50)
                    f.rage = min(RAGE_MAX, f.rage + 40)
                    game.floats.append(FloatingText(f.x, f.y - 120, "能量 +50/+40",
                                                    (140, 235, 200), 18))
                    game.orbs.remove(orb)
    if eff == "energy_orb":
        game.orb_t += 1
        if game.orb_t >= ENERGY_ORB_PERIOD or not game.orbs:
            game.orb_t = 0
            if len(game.orbs) < 2:
                game.orbs.append({"x": random.randint(240, SCREEN_W - 240),
                                  "y": random.randint(-30, 30), "t": 0})
        for orb in game.orbs:
            orb["t"] += 1


def draw_arena_deco(surf, arena, t):
    """9 种程序化装饰，全部代码绘制，不依赖图片素材。"""
    kind = arena["deco"]
    c = arena["grid"]
    if kind == "plain":
        return
    for i in range(14):
        x = (i * 197 + 63) % SCREEN_W
        y = (i * 83 + 41 + int(t * (0.18 + i % 3 * 0.05))) % (GROUND_Y - 60)
        if kind == "bubble":
            r = 4 + i % 7
            pygame.draw.circle(surf, (c[0], c[1], c[2], 60), (x, y), r, 1)
            pygame.draw.circle(surf, (200, 235, 255, 90), (x - r // 3, y - r // 3), max(1, r // 4))
        elif kind == "book":
            pygame.draw.rect(surf, (c[0] + 20, c[1] + 16, c[2], 80), (x, y, 16, 11), 1)
            pygame.draw.line(surf, (255, 220, 150, 90), (x, y + 5), (x + 16, y + 5), 1)
        elif kind == "paper":
            pygame.draw.line(surf, (c[0], c[1], c[2], 90), (x, y), (x + 22, y - 6), 1)
            pygame.draw.line(surf, (c[0], c[1], c[2], 70), (x, y + 6), (x + 18, y), 1)
        elif kind == "star":
            pygame.draw.line(surf, (220, 210, 255, 120), (x, y), (x + 10, y), 2)
            if i % 4 == 0:
                pygame.draw.polygon(surf, (255, 230, 160, 100),
                                    [(x, y - 6), (x + 3, y), (x, y + 6), (x - 3, y)])
        elif kind == "teacup":
            pygame.draw.arc(surf, (c[0] + 30, c[1] + 30, c[2], 100),
                            (x, y, 20, 14), 0, 3.14, 2)
        elif kind == "moon":
            r = 10 + i % 9
            pygame.draw.circle(surf, (225, 226, 245, 80), (x, y), r)
            pygame.draw.circle(surf, arena["top"], (x + r // 2, y - r // 3), r - 2)
        elif kind == "zzz":
            font = get_font(14 + i % 8)
            surf.blit(font.render("Z", True, (c[0] + 40, c[1] + 40, c[2])), (x, y))
        elif kind == "gothic":
            pygame.draw.rect(surf, (c[0], c[1], c[2], 70), (x, y, 12, 30), 1)
            pygame.draw.arc(surf, (255, 120, 110, 90), (x, y - 8, 12, 16), 0, 3.14, 1)


def draw_arena_bg(surf, t, game=None):
    """v3 场地背景：按 ARENAS[arena_idx] 取配色 / 装饰 / 机制提示。"""
    idx = getattr(game, "arena_idx", DEFAULT_ARENA_IDX) if game else DEFAULT_ARENA_IDX
    arena = ARENAS[idx % len(ARENAS)]
    top, bot, ground, grid = arena["top"], arena["bot"], arena["ground"], arena["grid"]
    for y in range(0, GROUND_Y, 4):
        f = y / float(GROUND_Y)
        c = tuple(int(lerp(top[i], bot[i], f)) for i in range(3))
        pygame.draw.rect(surf, c, (0, y, SCREEN_W, 4))
    draw_arena_deco(surf, arena, t)
    pygame.draw.rect(surf, ground, (0, GROUND_Y, SCREEN_W, SCREEN_H - GROUND_Y))
    pygame.draw.line(surf, grid, (0, GROUND_Y), (SCREEN_W, GROUND_Y), 2)
    for i in range(-10, 22):
        gx = SCREEN_W / 2 + i * 74 + (t * 0.25) % 74
        pygame.draw.line(surf, grid,
                         (int(SCREEN_W / 2 + (gx - SCREEN_W / 2) * 0.25), GROUND_Y),
                         (int(gx), SCREEN_H), 1)
    for j in range(1, 6):
        gy = GROUND_Y + (j / 5.0) ** 1.7 * (SCREEN_H - GROUND_Y)
        pygame.draw.line(surf, grid, (0, int(gy)), (SCREEN_W, int(gy)), 1)
    if not game:
        return
    eff = game.arena_effect
    if eff in ("center_rage", "heal_zone"):
        left, right = CENTER_ZONE
        col = ARENA_EFFECTS[eff]["color"]
        overlay = pygame.Surface((int(right - left), SCREEN_H - GROUND_Y), pygame.SRCALPHA)
        overlay.fill((col[0], col[1], col[2], 26))
        surf.blit(overlay, (int(left), GROUND_Y))
        pygame.draw.line(surf, col, (int(left), GROUND_Y), (int(left), SCREEN_H), 1)
        pygame.draw.line(surf, col, (int(right), GROUND_Y), (int(right), SCREEN_H), 1)
    elif eff == "edge_slow":
        w = int(SCREEN_W * EDGE_ZONE)
        for x in (0, SCREEN_W - w):
            ov = pygame.Surface((w, SCREEN_H - GROUND_Y), pygame.SRCALPHA)
            ov.fill((150, 190, 255, 24))
            surf.blit(ov, (x, GROUND_Y))
    elif eff == "energy_orb":
        for orb in game.orbs:
            x, y = int(orb["x"]), int(GROUND_Y - 62 + orb["y"])
            pygame.draw.circle(surf, (140, 235, 200, 60), (x, y), 20)
            pygame.draw.circle(surf, (220, 255, 240), (x, y), 9)
            pygame.draw.circle(surf, (140, 235, 200), (x, y), 15, 1)
    elif eff == "wind":
        phase = (t // WIND_PERIOD) % 2
        for i in range(6):
            y = 120 + i * 56
            x0 = (t * 3 + i * 180) % SCREEN_W
            dx = 34 if phase == 0 else -34
            pygame.draw.line(surf, (120, 210, 255, 90), (x0, y), (x0 + dx, y), 2)


def draw_skill_rings(surf, game):
    """技能范围扩散圈（AOE / 秘卷）的短演出。"""
    for ring in game.skill_rings[:]:
        k = ring["t"] / float(ring["max"])
        r = int(ring["r"] * (1.0 - k * 0.75))
        pygame.draw.circle(surf, ring["color"], (int(ring["x"]), int(ring["y"])), max(2, r), 2)
        ring["t"] -= 1
        if ring["t"] <= 0:
            game.skill_rings.remove(ring)


def draw_status_badges(surf, f, x, y, align="left"):
    """HUD 上的状态图标条：让控制 / 护盾 / 霸体一眼可见；align=right 时靠右排。"""
    items = [(k, v) for k, v in f.status.items() if v > 0 and k in STATUS_INFO][:6]
    if not items:
        return
    font = get_font(13)
    boxes = []
    for k, _v in items:
        name, col = STATUS_INFO[k]
        boxes.append((name, col, font.size(name)[0] + 12))
    total = sum(b[2] for b in boxes) + 4 * (len(boxes) - 1)
    cur = x if align == "left" else x - total
    for name, col, w in boxes:
        pygame.draw.rect(surf, (18, 20, 42), (cur, y, w, 20), border_radius=5)
        pygame.draw.rect(surf, col, (cur, y, w, 20), 1, border_radius=5)
        surf.blit(font.render(name, True, col), (cur + 6, y + 3))
        cur += w + 4


class App:
    """游戏应用：持有窗口、场景状态、设置、战绩与一局对战的全部实体。
    页面状态：menu / select / settings / game / stats。"""

    def _init_core_state(self, selftest):
        """最基础的运行状态：时钟 / 场景 / 输入缓冲 / 战绩 / 手机 AI 开关。"""
        self.selftest = selftest
        self.clock = pygame.time.Clock()
        self.t = 0
        self.scene = "menu"
        self.running = True
        self.just = set()
        self.clicks = []                    # [(虚拟画布坐标, button), ...]
        self.mouse = (0, 0)
        # ---- F9 诊断（v3.3）：把 SDL 实际收到的坐标摊开给用户看，不再猜 ----
        self.diag = False
        self.diag_log = []
        self.last_raw = (0, 0)
        # ---- v3.4 网页输入桥状态 ----
        self.web_bridge = False          # True = 用 JS 队列，忽略 SDL 鼠标/触摸
        self.web_bridge_info = {}        # canvas 内外尺寸 / PointerEvent 支持等
        self.last_web_ev = None          # 最近一条 JS 事件，供诊断叠层显示
        self.stats = load_stats()
        self.clear_confirm = 0
        self.ai_on = AI_DEFAULT_ON          # 手机单人玩：中间按钮可一键切换
        self.ai_cache = ((), ())
        self.assign_side = 1                # 选人页：当前点击分配给 P1 还是 P2

    def _init_display(self, selftest):
        """手机自适应显示：读取真实分辨率 → 等比缩放居中 → 虚拟画布。
        这一段就是修掉「画面被裁成顶部一条」的地方。"""
        self.disp = None
        self.scale = 1.0
        self.off = (0, 0)
        self.out_w, self.out_h = SCREEN_W, SCREEN_H
        self.disp_w, self.disp_h = SCREEN_W, SCREEN_H
        # 网页里 canvas 尺寸由 pygbag 固定为 1280×720，缩放交给注入的 CSS，
        # 所以这里不走 FULLSCREEN / display.Info() 那条桌面专用分支。
        if not selftest and not IS_WEB and MOBILE_TOUCH and MOBILE_FULLSCREEN:
            info = pygame.display.Info()
            dw, dh = info.current_w, info.current_h
            if dw <= 0 or dh <= 0:
                dw, dh = SCREEN_W, SCREEN_H
            if MOBILE_FORCE_LANDSCAPE and dw < dh:
                dw, dh = dh, dw
            self.disp_w, self.disp_h = dw, dh
            try:
                self.disp = pygame.display.set_mode((dw, dh), pygame.FULLSCREEN)
            except Exception:
                self.disp = None          # 少数 IDE 不支持 FULLSCREEN
            if self.disp is None:
                dw, dh = SCREEN_W, SCREEN_H
                self.disp_w, self.disp_h = dw, dh
                self.disp = pygame.display.set_mode((SCREEN_W, SCREEN_H))
            pygame.display.set_caption(WINDOW_TITLE)
            self.scale = min(dw / float(SCREEN_W), dh / float(SCREEN_H))
            if MOBILE_STRETCH:
                self.out_w, self.out_h = dw, dh
            else:
                self.out_w = int(SCREEN_W * self.scale)
                self.out_h = int(SCREEN_H * self.scale)
            self.off = ((dw - self.out_w) // 2, (dh - self.out_h) // 2)
            self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
        else:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
            if not selftest:
                pygame.display.set_caption(WINDOW_TITLE)

    def _init_touch_state(self):
        """触屏状态：touch_id -> 当前按住的按钮，以及四组按钮布局。"""
        self.touch_hits = {}
        self.touch_held = set()
        self.left_btns, self.right_btns, self.global_btns, self.mid_btns = build_touch_layout()
        self.assign_btn = _btn(1000, 96, 180, 40, "选给：P1")
        # 主页面「模式 / 操作」切换键 + 结算层两个可点键
        self._refresh_mode_btns()
        self.result_btns = [
            _btn(SCREEN_W // 2 - 220, 500, 200, 52, "再战", (), ()),
            _btn(SCREEN_W // 2 + 20, 500, 200, 52, "回主页面", (), ()),
        ]
        self.help_back = _btn(24, 24, 150, 36, "返回主页面", (), ())
        self._last_down_key = None       # 同帧同坐标去重（手机 mouse+touch 双事件）
        self._rebuild_buttons()

    def input_label(self):
        """当前操作方案的可读名字：手机摇杆 / 电脑键盘 / 滑动手势。"""
        ui = getattr(self, "move_ui", DEFAULT_MOVE_UI)   # __init__ 早期可能还没赋值
        if ui == MOVE_UI_SHOW:
            return "手机摇杆"
        if ui == MOVE_UI_HIDE:
            return "电脑键盘" if not IS_WEB else "滑动手势"
        return ("手机摇杆" if (IS_WEB or getattr(self, "disp", None) is not None)
                and getattr(self, "mode", DEFAULT_MODE) == MODE_PVE else "电脑键盘")

    def mode_label(self):
        return "PVE 单人" if getattr(self, "mode", DEFAULT_MODE) == MODE_PVE else "PVP 双人"

    def _refresh_mode_btns(self):
        """主页面两个切换按钮的标签随状态更新。"""
        self.mode_btns = [
            _btn(880, 300, 230, 52, "模式：" + self.mode_label(), (), ()),
            _btn(880, 366, 230, 52, "操作：" + self.input_label(), (), ()),
        ]

    def _rebuild_buttons(self):
        """按模式重建技能簇：PVE 只给 P1 一套（放右下），PVP 左右各一套。
        这是「PVE 只看到自己的，PVP 双方可见」的落点。"""
        mode = getattr(self, "mode", DEFAULT_MODE)   # __init__ 早期也可能调用本方法
        if TOUCH_STYLE == "naruto":
            if mode == MODE_PVE:
                self.left_btns = []
                self.right_btns = build_skill_cluster(1, mirror=False)   # 右侧簇归 P1
            else:
                # PVP 且强制显示摇杆时，两簇往中间挪，避免圆键与摇杆抢同一块区域
                shift = CLUSTER_PVP_STICK_SHIFT if self.move_ui_visible() else 0
                self.left_btns = build_skill_cluster(1, mirror=True, shift=shift)
                self.right_btns = build_skill_cluster(2, mirror=False, shift=shift)
        else:
            step_x = TOUCH_BTN_W + TOUCH_BTN_GAP
            step_y = TOUCH_BTN_H + TOUCH_BTN_GAP
            xs1 = [TOUCH_P1_X0 + i * step_x for i in range(4)]
            xs2 = [TOUCH_P2_X0 + i * step_x for i in range(4)]
            ys = [TOUCH_Y0 + r * step_y for r in range(3)]
            self.left_btns = build_side_buttons(KEYS_P1, xs1, ys)
            self.right_btns = build_side_buttons(KEYS_P2, xs2, ys) if self.mode == MODE_PVP else []
        self.global_btns = build_global_buttons()
        self.mid_btns = build_mid_buttons()

    def move_ui_visible(self):
        """移动键显隐：
        自动 = 手机/网页的 PVE 显示摇杆；PVP 与电脑窗口默认隐藏（用滑动手势 / 键盘），
        正对应「手游 PVE 可显示移动键，电脑 PVP 不显示移动键」，也最不挡画面。
        想强制显示：设置页把「移动键」切成「显示」。"""
        if self.move_ui == MOVE_UI_SHOW:
            return True
        if self.move_ui == MOVE_UI_HIDE:
            return False
        return (IS_WEB or self.disp is not None) and getattr(self, "mode", DEFAULT_MODE) == MODE_PVE

    def visible_sides(self):
        return (1,) if self.mode == MODE_PVE else (1, 2)

    def _init_settings(self):
        """对局设置 / 角色选择 / 菜单光标（都可在页面里改）。"""
        self.time_idx = DEFAULT_TIME_IDX
        self.hp_idx = DEFAULT_HP_IDX
        self.training = DEFAULT_TRAINING
        self.sel = {1: 0, 2: 1}            # 已确认的角色索引
        self.cur = {1: 0, 2: 1}            # 选人页光标
        self.lock = {1: False, 2: False}
        self.menu_idx = 0
        self.settings_idx = 0
        self.menu_items = ["开始对战", "角色选择", "对局设置", "操作说明",
                           "P1 / P2 战绩", "退出游戏"]
        # ---- v3 模式 / 场地 / 秘卷 / 移动键 ----
        self.mode = DEFAULT_MODE
        self.arena_idx = DEFAULT_ARENA_IDX
        self.arena_effect = DEFAULT_ARENA_EFFECT
        self.scroll_id = DEFAULT_SCROLL
        self.move_ui = DEFAULT_MOVE_UI

    def _init_match_state(self):
        """一局对战的运行时对象（开局前都是空值）。"""
        self.p1 = self.p2 = None
        self.projectiles = []
        self.assists = []
        self.particles = []
        self.floats = []
        self.slashes = []
        self.shake = 0
        self.time_left = 0.0
        self.over = False
        self.winner = 0
        self.over_t = 0
        self.banner = ""                    # 开局 「准备 / 开打」提示
        self.banner_t = 0
        self.paused = False                # 网页 / 触屏下真正的对局暂停开关
        self.frame_scale = 1.0             # 本帧位移补偿系数（按真实 dt 计算）
        self.stick_hits = {}               # 固定摇杆：{触摸id: [阵营, dx, dy]}
        self.pending_skills = []           # 带前摇的技能，到点才结算（给闪避窗口）
        self.skill_rings = []              # AOE 扩散圈演出
        self.orbs = []                     # 场地机制「能量球」拾取物
        self.orb_t = 0
        self.swipe = {}                    # 关摇杆时的滑动手势：{tid: [side, start_x]}
        self.swipe_dir = {}                # {side: -1/0/1}

    def __init__(self, selftest=False):
        """只做编排：核心状态 → 显示 → 触屏 → 设置 → 对局对象。"""
        self._init_core_state(selftest)
        self._init_display(selftest)
        self._init_touch_state()
        self._init_settings()
        self._init_match_state()
        # 网页下自己接管输入；桌面 / 手机 IDE / 自检完全不受影响
        if IS_WEB:
            self.web_bridge, self.web_bridge_info = _web_install_input_bridge(
                _WEB_INPUT_JS)
            self._diag("输入桥 %s %s" %
                       ("启用" if self.web_bridge else "未启用（回退 SDL）",
                        json.dumps(self.web_bridge_info, ensure_ascii=False)[:110]))

    # ---- 手机触屏：坐标反变换 / 事件翻译 / 按键合成 / 按钮绘制 ----
    def to_canvas(self, px, py):
        """物理屏幕像素 -> 虚拟画布坐标。缩放和居中黑边都在这里抵消掉。"""
        if self.disp is None:
            return (int(px), int(py))
        return (int((px - self.off[0]) / self.scale),
                int((py - self.off[1]) / self.scale))

    def active_buttons(self):
        """当前页面可点的按钮列表。战斗页左右簇 + 中间；结算层换成两个大按钮。"""
        if self.scene == "help":
            return [self.help_back]
        if self.scene == "game":
            if self.over:
                return self.result_btns
            return self.left_btns + self.right_btns + self.mid_btns
        out = list(self.global_btns)
        if self.scene == "menu":
            out += self.mode_btns
        if self.scene == "select":
            out.append(self.assign_btn)
        return out

    def hit_button(self, pos):
        for b in self.active_buttons():
            if b[0].collidepoint(pos):
                return b
        return None

    def on_touch_down(self, tid, phys):
        """手指按下 / 鼠标按下：翻译成本页点击 + 虚拟按键 hold/tap。"""
        # 网页下 canvas 由 CSS transform:scale 缩放，pygame 给的是 canvas 内部坐标；
        # 只有极个别浏览器会偏差，用 WEB_INPUT_SCALE 手动校准（默认 1.0 不用动）。
        if IS_WEB and WEB_INPUT_SCALE != 1.0:
            phys = (phys[0] * WEB_INPUT_SCALE, phys[1] * WEB_INPUT_SCALE)
        pos = self.to_canvas(*phys)
        self.mouse = pos
        # 手机浏览器常把一次触摸同时派发成 FINGERDOWN 和 MOUSEBUTTONDOWN，
        # 不去重的话菜单「切模式」会被连切两次回到原值，看起来就是点了没反应。
        key = (self.t, int(pos[0]), int(pos[1]))
        if key == self._last_down_key:
            return
        self._last_down_key = key
        # 固定摇杆：手指落在底盘内就接管这根手指，底盘本身永远不动
        if self.scene == "game" and TOUCH_STYLE == "naruto" and self.move_ui_visible():
            for side in self.visible_sides():
                c = STICK_P1_CENTER if side == 1 else STICK_P2_CENTER
                if math.hypot(pos[0] - c[0], pos[1] - c[1]) <= STICK_RADIUS + 18:
                    self.stick_hits[tid] = [side, 0.0, 0.0]
                    self._stick_update(tid, pos)
                    return
        # 选人页：手机没有右键，用「选给：P1/P2」开关决定这次点击归谁
        if self.scene == "select":
            if self.assign_btn[0].collidepoint(pos):
                self.assign_side = 2 if self.assign_side == 1 else 1
                self.assign_btn = _btn(self.assign_btn[0].x, self.assign_btn[0].y,
                                       self.assign_btn[0].w, self.assign_btn[0].h,
                                       "选给：P%d" % self.assign_side)
                return
            idx = self._card_index(pos)
            if idx is not None:
                self.cur[self.assign_side] = idx
                self.sel[self.assign_side] = idx
                self.lock[self.assign_side] = True
                return
        b = self.hit_button(pos)
        # 页面自身的点击区域（菜单 / 选人「开始对战」按钮）沿用上一版 clicks 机制
        self.clicks.append((pos, 1))
        if b is None:
            # 关掉移动键时，在画面空白区左右滑动也能移动（左半=P1，右半=P2）
            if self.scene == "game" and not self.move_ui_visible():
                side = 1 if pos[0] < SCREEN_W // 2 else 2
                if side in self.visible_sides():
                    self.swipe[tid] = [side, pos[0]]
            return
        # ---- v3.2：操作说明 / 返回 ----
        if b[1] == "输入诊断":
            self.diag = not self.diag
            self._diag("诊断按钮 " + ("开" if self.diag else "关"))
            return
        if b[1] in ("操作说明",):
            self.help_from = self.scene
            self.scene = "help"
            return
        if b[1] == "返回主页面":
            self.scene = "menu"
            return
        # ---- v3.1：模式 / 操作 / 结算 三个切换键，不映射成键盘 ----
        if b[1].startswith("模式：") or b[1] == "切模式":
            self.mode = MODE_PVP if self.mode == MODE_PVE else MODE_PVE
            self._refresh_mode_btns()
            self._rebuild_buttons()
            if self.scene == "game":
                self.start_match()          # 战斗中切换 = 立刻按新模式重开一局
            return
        if b[1].startswith("操作：") or b[1] == "切操作":
            opts = [MOVE_UI_SHOW, MOVE_UI_HIDE, MOVE_UI_AUTO]
            self.move_ui = opts[(opts.index(self.move_ui) + 1) % len(opts)]
            self._refresh_mode_btns()
            self._rebuild_buttons()
            return
        if b[1] == "再战":
            self.start_match()
            return
        if b[1] == "回主页面":
            self.scene = "menu"
            return
        # 中间的「电脑：关/开」按钮（旧布局兼容）
        if b[1].startswith("电脑："):
            self.ai_on = not self.ai_on
            for i, m in enumerate(self.mid_btns):
                if m[1].startswith("电脑："):
                    self.mid_btns[i] = _btn(m[0].x, m[0].y, m[0].w, m[0].h,
                                            "电脑：开" if self.ai_on else "电脑：关")
            return
        self.touch_hits[tid] = b
        for c in b[3]:
            self.just.add(c)

    def on_touch_move(self, tid, phys):
        """v3.4：JS 桥送来的 pointermove。只更新鼠标 / 摇杆 / 滑动，不产生新点击。"""
        if IS_WEB and WEB_INPUT_SCALE != 1.0:
            phys = (phys[0] * WEB_INPUT_SCALE, phys[1] * WEB_INPUT_SCALE)
        pos = self.to_canvas(*phys)
        self.mouse = pos
        if tid in self.stick_hits:
            self._stick_update(tid, pos)
        if tid in self.swipe:
            side, x0 = self.swipe[tid]
            d = pos[0] - x0
            self.swipe_dir[side] = 1 if d > 18 else (-1 if d < -18 else 0)

    def on_touch_up(self, tid):
        self.touch_hits.pop(tid, None)
        sw = self.stick_hits.pop(tid, None)
        if sw:
            self._stick_update_done(sw[0])
        wsp = self.swipe.pop(tid, None)
        if wsp:
            self.swipe_dir.pop(wsp[0], None)

    def _stick_update_done(self, side):
        """抬手后该侧摇杆头回中；若这侧还有别的手指按着就不回。"""
        if not any(v[0] == side for v in self.stick_hits.values()):
            return

    def _stick_update(self, tid, pos):
        """摇杆头跟随手指，但只在底盘内移动；存归一化偏移供 synth_keys 翻译。"""
        if tid not in self.stick_hits:
            return
        side = self.stick_hits[tid][0]
        c = STICK_P1_CENTER if side == 1 else STICK_P2_CENTER
        dx = (pos[0] - c[0]) / float(STICK_MAX_OFFSET)
        dy = (pos[1] - c[1]) / float(STICK_MAX_OFFSET)
        n = math.hypot(dx, dy)
        if n > 1.0:
            dx, dy = dx / n, dy / n
        self.stick_hits[tid] = [side, dx, dy]

    def _stick_offset(self, side):
        """取某阵营当前摇杆头的像素偏移，用于绘制。"""
        for _tid, (sd, dx, dy) in self.stick_hits.items():
            if sd == side:
                return dx * STICK_MAX_OFFSET, dy * STICK_MAX_OFFSET
        return 0.0, 0.0

    def synth_keys(self):
        """把「物理键盘 + 虚拟按钮 + 电脑 AI」合成成上一版要的 keys 数组。
        Fighter.update 完全不用改，读到的还是同一套 K_* 键码。"""
        base = pygame.key.get_pressed()
        held = set()
        for b in self.touch_hits.values():
            held.update(b[2])
        # 固定摇杆 -> 方向键（Fighter 一行都不用改）
        for side, dx, dy in self.stick_hits.values():
            km = KEYS_P1 if side == 1 else KEYS_P2
            if dx < -STICK_DEADZONE:
                held.add(km["left"])
            elif dx > STICK_DEADZONE:
                held.add(km["right"])
            if dy > 0.60:
                held.add(km["guard"])     # 下 = 防御
            elif dy < -0.60:
                held.add(km["up"])        # 上 = 上挑/斜上远攻的修饰
        # 关摇杆时的滑动手势 -> 方向键
        for side, d in self.swipe_dir.items():
            km = KEYS_P1 if side == 1 else KEYS_P2
            if d > 0:
                held.add(km["right"])
            elif d < 0:
                held.add(km["left"])
        if self.scene == "game" and self.ai_on and self.p1 and self.p2:
            if self.t % AI_THINK_FRAMES == 0:
                self.ai_cache = ai_decide(self.p2, self.p1, self.t)
                for c in self.ai_cache[1]:
                    self.just.add(c)
            held.update(self.ai_cache[0])
        self.touch_held = held
        return KeyState(base, held)

    def draw_touch_layer(self, s):
        """v3.1 火影手游式按键层：实心底盘 + 分区 + 专属短名 + CD 秒数。"""
        if self.selftest or not MOBILE_TOUCH:
            return
        btns = self.active_buttons()
        layer = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        naruto = (TOUCH_STYLE == "naruto" and self.scene == "game")
        # 固定摇杆：底盘永远不动，只有摇杆头跟手指
        if naruto and self.move_ui_visible() and not self.over:
            for side in self.visible_sides():
                c = STICK_P1_CENTER if side == 1 else STICK_P2_CENTER
                pygame.draw.circle(layer, (12, 16, 38, 225), c, STICK_RADIUS)
                pygame.draw.circle(layer, (120, 160, 235, 210), c, STICK_RADIUS, 3)
                pygame.draw.circle(layer, (60, 76, 132, 150), c, STICK_RADIUS - 15, 2)
                ox, oy = self._stick_offset(side)
                knob = (int(c[0] + ox), int(c[1] + oy))
                hot = any(sd == side for sd, _d, _e in self.stick_hits.values())
                kc = (110, 214, 255, 245) if hot else (86, 176, 235, 225)
                pygame.draw.circle(layer, kc, knob, STICK_KNOB_RADIUS)
                pygame.draw.circle(layer, (232, 246, 255, 245), knob, STICK_KNOB_RADIUS, 3)
                draw_text(layer, "移动", c[0], c[1] + STICK_RADIUS + 8,
                          13, COL_DIM, align="center", shadow=False)

        for rect, label, _h, tap in btns:
            hot = rect in [b[0] for b in self.touch_hits.values()]
            is_round = bool(naruto and rect.w == rect.h and rect.w >= 48
                            and label in ("atk", "s1", "s2", "s3", "ult"))
            act, side = tap[0] if (tap and isinstance(tap[0], tuple)) else (None, 0)
            f = (self.p1 if side == 1 else self.p2) if side else None
            # --- CD 与气不足 ---
            cd, full, cost_ok = 0, 1, True
            if f and act in ACTION_ORDER and act != "atk":
                cd = {"s1": f.cd_s1, "s2": f.cd_s2, "s3": f.cd_s3,
                      "ult": f.cd_ult, "dodge": f.dodge_cd,
                      "cleanse": f.cleanse_cd, "scroll": f.scroll_cd}.get(act, 0)
                full = {"s1": 96, "s2": 186, "s3": 252, "ult": 600,
                        "dodge": DODGE_CD, "cleanse": CLEANSE_CD,
                        "scroll": SCROLL_CD_FALLBACK}.get(act, 1)
                need = skill_spec(f.char["id"], act).get("rage", 0) if act in SKILL_SLOTS else 0
                cost_ok = f.rage >= need

            # --- 底色 / 边框（按功能分区，颜色不再千篇一律）---
            if is_round:
                col = dict((a, c) for a, _x, _y, _r, c in SKILL_ROUND)[act]
                base = (18, 24, 52, 235) if not hot else (46, 62, 116, 245)
                if cd > 0 or not cost_ok:
                    base = (12, 14, 30, 225)
                pygame.draw.circle(layer, base, rect.center, rect.w // 2)
                pygame.draw.circle(layer, col + (225,), rect.center, rect.w // 2, 3)
            else:
                base = (18, 24, 52, 225) if not hot else (46, 62, 116, 240)
                if cd > 0:
                    base = (12, 14, 30, 215)
                pygame.draw.rect(layer, base, rect, border_radius=10)
                pygame.draw.rect(layer, (110, 140, 205, 190), rect, 2, border_radius=10)

            # --- 文字：技能显示专属短名 + 编号；功能键显示完整名 ---
            if is_round:
                kc = keycap(act, side)
                if act == "atk":
                    draw_text(layer, "普攻", rect.centerx, rect.centery - 12,
                              19, COL_TEXT, True, "center", shadow=False)
                    if cd == 0:
                        draw_text(layer, "J" if side == 1 else "1", rect.centerx,
                                  rect.centery + 9, 14, COL_GOLD, True, "center", shadow=False)
                else:
                    nm = skill_short_name(f.char["id"], act) if f else act
                    sz = 17 if len(nm) <= 2 else 14
                    draw_text(layer, nm, rect.centerx, rect.centery - 12,
                              sz, col, True, "center", shadow=False)
                    # 键面下方直接标键盘键名，不用猜「这个技能按什么」
                    if cd == 0 and cost_ok:
                        draw_text(layer, kc, rect.centerx, rect.centery + 9,
                                  14, COL_GOLD, True, "center", shadow=False)
            else:
                txt = FUNC_LABEL.get(label, label)
                draw_text(layer, txt, rect.centerx, rect.centery - 10,
                          15, COL_TEXT, True, "center", shadow=False)
                kc = keycap(label, side)
                if kc and cd == 0:
                    draw_text(layer, kc, rect.centerx, rect.centery + 8,
                              12, COL_GOLD, True, "center", shadow=False)

            # --- CD：红色弧 + 剩余秒数 ---
            if cd > 0:
                if is_round:
                    rr = rect.w // 2 + 3
                    pygame.draw.arc(layer, (255, 110, 110, 235),
                                    (rect.centerx - rr, rect.centery - rr, rr * 2, rr * 2),
                                    math.pi / 2,
                                    math.pi / 2 + 2 * math.pi * min(1.0, cd / float(full)), 3)
                sec = "%.1f" % (cd / float(FPS))
                draw_text(layer, sec, rect.centerx, rect.centery + 10 if is_round
                          else rect.centery + 9, 12, (255, 150, 150),
                          True, "center", shadow=False)
            elif is_round and act == "ult" and f and not cost_ok:
                draw_text(layer, "气不足", rect.centerx, rect.centery + 10,
                          11, (255, 150, 150), False, "center", shadow=False)

        # v3.2：删掉底部提示行。它原本压在「跳/闪避/净化/秘卷」横条上，
        # 而且 HUD 第 162 行已经显示模式与操作方案，信息重复。
        s.blit(layer, (0, 0))

    def other(self, f):
        """返回 f 的对手。"""
        return self.p2 if f.side == 1 else self.p1

    def spawn_burst(self, x, y, color, n=16):
        """生成一组粒子，受 PARTICLE_MAX 限制。"""
        room = max(0, PARTICLE_MAX - len(self.particles))
        for _ in range(min(n, room)):
            self.particles.append(Particle(x, y, color))

    def spawn_slash(self, f):
        """记录一次刀光特效。"""
        self.slashes.append({"x": f.x, "y": f.y, "face": f.facing,
                             "color": f.char["aura"], "t": ATK_ACTIVE})

    def summon_assist(self, owner):
        """援助延迟结算：扣 1 格气、进入冷却、生成援助实体。"""
        owner.rage -= ASSIST_COST
        owner.assist_cd = ASSIST_CD
        self.assists.append(Assist(owner))
        self.floats.append(FloatingText(owner.x, owner.y - 120,
                                        owner.char["skills"]["assist"], owner.char["accent"], 18))

    def _compute_damage(self, src, target, dmg, break_guard):
        """算最终伤害：背后无法防御 → 防御减伤 → 变身减伤 → 至少 1 点。"""
        from_back = (src.x - target.x) * target.facing < 0
        guarded = target.guard and not break_guard and not from_back
        actual = dmg * (GUARD_REDUCE if guarded else 1.0)
        if target.transformed:
            actual *= TRANSFORM_DEF
        return max(1.0, actual), guarded

    def _apply_damage_state(self, src, target, actual, guarded, launch,
                            break_guard, label):
        """扣血并写入受击状态：硬直 / 无敌 / 击退 / 浮空 / 破防。"""
        target.hp = max(0.0, target.hp - actual)
        target.flash = 6
        target.invuln = INVULN_FRAMES
        target.hurt_t = HURT_FRAMES
        target.state = "hurt" if not guarded else "guard"
        target.state_t = 0
        target.vx = src.facing * KNOCKBACK
        if launch:
            target.vy = launch
            target.y -= 2
        if break_guard:
            target.guard = False
            label = "[破防] " + label
        return label

    def _award_rage_combo(self, src, target, actual, rage_gain):
        """怒气与连击：打人的涨气，挨打的也涨气；记录本局累计伤害。"""
        src.rage = clamp(src.rage + (rage_gain if rage_gain is not None else RAGE_ON_HIT),
                         0, RAGE_MAX)
        target.rage = clamp(target.rage + RAGE_ON_TAKE, 0, RAGE_MAX)
        src.dealt += actual
        src.combo += 1
        src.combo_t = COMBO_TIMEOUT
        src.max_combo = max(src.max_combo, src.combo)

    def _spawn_hit_fx(self, src, target, actual, label, guarded):
        """命中反馈：粒子、伤害数字、技能名浮字、屏幕震动。"""
        self.spawn_burst(target.x, target.y - 54, src.char["aura"], 14)
        self.floats.append(FloatingText(target.x, target.y - 108,
                                        str(int(actual)), COL_GOLD, 24))
        if label:
            self.floats.append(FloatingText(src.x, src.y - 132, label,
                                            src.char["aura"], 17))
        self.shake = max(self.shake, 5 if not guarded else 2)

    def apply_hit(self, src, target, dmg, break_guard=False, launch=0.0,
                  label="", rage_gain=None):
        """统一命中入口 v3：无敌/闪避 → 替身 → 状态修正 → 算伤 → 扣血 → 反伤 → KO。"""
        if not target.alive():
            return False
        if target.invuln > 0:
            # 闪避无敌期间真的躲掉一次攻击 → 记成功、回气（九命灵动等被动用）
            if getattr(target, "dodge_invuln", 0) > 0 and not target.dodge_success:
                target.dodge_success = True
                target.rage = min(RAGE_MAX, target.rage + DODGE_RAGE_ON_SUCCESS)
                self.floats.append(FloatingText(target.x, target.y - 120,
                                                "闪避成功", (140, 235, 200), 18))
            return False
        # 秘卷「替身攻击」：受击自动免伤并反击
        if has_status(target, "counter_ready"):
            target.status.pop("counter_ready", None)
            target.invuln = 14
            if src.alive() and src.invuln <= 0:
                src.hp = max(0.0, src.hp - 60)
                src.state, src.state_t, src.hurt_t = "hurt", 0, HURT_FRAMES
                target.dealt += 60
                self.floats.append(FloatingText(src.x, src.y - 120, "替身反击 60",
                                                (255, 160, 200), 18))
                if not src.alive():
                    self.finish(winner=target.side)
            return False
        # 旧版「受击瞬间 O/6」反制保留
        if target.pending_assist > 0 and target.rage >= COUNTER_COST:
            target.do_counter(src, self)
            return False

        actual, guarded = self._compute_damage(src, target, dmg, break_guard)
        # ---- v3 状态修正（顺序：宪法减伤 → 强化易伤 → 护盾吸收 → 破霸体额外）----
        pk = kit_of(target)["passive"]
        if pk["type"] == "damage_cap" and actual > 120:
            actual = 120 + (actual - 120) * (1.0 - pk["val"])
        if has_status(target, "buff_atk"):
            actual *= 1.10
        shield = status_val(target, "shield", 0.0)
        if shield > 0:
            absorb = min(shield, actual)
            target.status_val["shield"] -= absorb
            actual -= absorb
            if target.status_val["shield"] <= 0:
                target.status.pop("shield", None)
            label = "[护盾] " + label
        if has_status(target, "super_armor") and getattr(src, "_pierce", False):
            actual *= 1.0 + SUPER_ARMOR_EXTRA
        actual = max(0.0, actual)

        label = self._apply_damage_state(src, target, actual, guarded, launch,
                                         break_guard, label)
        # 霸体免疫硬直（但破霸体技能可以打断）
        pierce = getattr(src, "_pierce", False)
        if has_status(target, "super_armor") and not pierce:
            target.state, target.state_t, target.hurt_t = "idle", 0, 0
        # 催眠被打醒
        if has_status(target, "sleep"):
            target.status.pop("sleep", None)
        # 毒舌反伤
        if pk["type"] == "reflect" and src.alive():
            back = actual * pk["val"]
            src.hp = max(0.0, src.hp - back)
            target.dealt += back
            if not src.alive():
                self.finish(winner=target.side)
        target.last_hurt_t = self.t
        self._award_rage_combo(src, target, actual, rage_gain)
        self._spawn_hit_fx(src, target, actual, label, guarded)
        if not target.alive():
            self.finish(winner=src.side)
        return True

    # ---- 开局 / 结算 ----
    def start_match(self):
        """按当前设置与角色选择创建一局对战。"""
        self.paused = False
        self.pending_skills = []
        self.skill_rings = []
        self.orbs = []
        self.orb_t = 0
        self.swipe = {}
        self.swipe_dir = {}
        self.ai_on = (self.mode == MODE_PVE)   # PVE 自动托管 P2；PVP 双人手操
        self._rebuild_buttons()
        hp_scale = HP_SCALE_OPTIONS[self.hp_idx]
        self.p1 = Fighter(1, CHARACTERS[self.sel[1]], SCREEN_W * 0.28)
        self.p2 = Fighter(2, CHARACTERS[self.sel[2]], SCREEN_W * 0.72)
        for f in (self.p1, self.p2):
            f.max_hp = BASE_HP * hp_scale * f.char["stats"]["hp"]
            f.hp = f.max_hp
        self.projectiles, self.assists, self.particles = [], [], []
        self.floats, self.slashes = [], []
        self.shake = 0
        self.time_left = float(TIME_OPTIONS[self.time_idx])
        self.over, self.winner, self.over_t = False, 0, 0
        self.banner, self.banner_t = "准备", 70
        self.scene = "game"

    def finish(self, winner=0):
        """结束对局：判定胜者、写战绩、切到结算覆盖层。"""
        if self.over:
            return
        if winner == 0 and self.p1 and self.p2:
            r1 = self.p1.hp / max(1.0, self.p1.max_hp)
            r2 = self.p2.hp / max(1.0, self.p2.max_hp)
            winner = 1 if r1 > r2 else (2 if r2 > r1 else 0)
        self.over = True
        self.winner = winner
        self.over_t = 0
        self.banner = ""
        if self.p1 and self.p2:
            record_match(self.stats, winner, self.p1, self.p2, self.training)
            self.stats = load_stats()

    def reset_stats(self):
        """清空战绩（需要按两次 C 二次确认）。"""
        self.stats = {"P1": blank_side(), "P2": blank_side()}
        save_stats(self.stats)

    # ---- 主循环 ----
    def _poll_events(self):
        """把一帧内的键盘 / 鼠标 / 多点触摸事件翻译成 just 集合与触摸状态。
        v3.4：网页下优先用【JS 输入桥】—— 它按 canvas 真实 rect 归一化坐标，
        不受 CSS 缩放 / DPR / SDL 换算影响；桥不可用时自动回退原来的 SDL 路径。"""
        self.just, self.clicks = set(), []
        alias = numpad_alias(self.mode)
        bridge = bool(self.web_bridge and IS_WEB)

        # ---------- ① JS 输入桥：取回队列，直接喂给触摸状态机 ----------
        if bridge:
            evs = _web_drain_input()
            if evs is None:
                # 取队列失败：本帧退回 SDL，不让输入凭空消失
                bridge = False
                self._diag("JS drain 失败，本帧回退 SDL")
            else:
                for e in evs:
                    try:
                        kind = e.get("t")
                        tid = int(e.get("id", 1))
                        x, y = float(e.get("x", 0)), float(e.get("y", 0))
                        self.last_web_ev = e
                        if kind == "down":
                            self._diag("JS DOWN id=%d (%d,%d) canvas=%dx%d rect=%dx%d" %
                                       (tid, x, y, e.get("cw", 0), e.get("ch", 0),
                                        e.get("rw", 0), e.get("rh", 0)))
                            self.last_raw = (int(x), int(y))
                            self.on_touch_down(tid, (x, y))
                        elif kind == "move":
                            self.on_touch_move(tid, (x, y))
                        elif kind == "up":
                            self.on_touch_up(tid)
                    except Exception as ex:
                        self._diag("JS 事件异常 %r" % (ex,))

        # ---------- ② SDL 事件：键盘永远处理；鼠标/触摸在桥可用时忽略 ----------
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == DIAG_TOGGLE:
                    self.diag = not self.diag
                    self._diag("F9 诊断 " + ("开" if self.diag else "关"))
                    continue
                # 小键盘 keycode 别名成主键；普通键 mapped == ev.key，行为不变
                mapped = alias.get(ev.key, ev.key)
                self.just.add(ev.key)
                self.just.add(mapped)
                act = ACTION_BY_KEY.get(mapped)
                if act:
                    self.just.add(act)
                try:
                    kn = pygame.key.name(ev.key)
                except Exception:
                    kn = str(ev.key)
                self._diag("KEY %-14s -> %-6s %s" %
                           (kn, pygame.key.name(mapped),
                            ("[" + act[0] + " P%d]" % act[1]) if act else ""))
            elif ev.type == pygame.MOUSEMOTION:
                if bridge:
                    continue                      # 桥已用真实 rect 算好坐标
                self.mouse = self.to_canvas(*ev.pos)
                if -1 in self.stick_hits:
                    self._stick_update(-1, self.mouse)
                if -1 in self.swipe:
                    side, x0 = self.swipe[-1]
                    d = self.mouse[0] - x0
                    self.swipe_dir[side] = 1 if d > 18 else (-1 if d < -18 else 0)
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if bridge:
                    continue                      # 避免与 JS 队列重复点击
                cv = self.to_canvas(*ev.pos)
                self._diag("SDL MOUSE raw=(%d,%d) -> canvas=(%d,%d)" %
                           (ev.pos[0], ev.pos[1], cv[0], cv[1]))
                self.last_raw = (int(ev.pos[0]), int(ev.pos[1]))
                self.on_touch_down(-1, ev.pos)
            elif ev.type == pygame.MOUSEBUTTONUP:
                if bridge:
                    continue
                self.on_touch_up(-1)
            elif ev.type == FINGER_DOWN:
                if bridge:
                    continue
                self._diag("SDL TOUCH norm=(%.3f,%.3f) disp=%dx%d" %
                           (ev.x, ev.y, self.disp_w, self.disp_h))
                self.on_touch_down(ev.touch_id,
                                   (ev.x * self.disp_w, ev.y * self.disp_h))
            elif ev.type == FINGER_MOTION:
                if bridge:
                    continue
                self.mouse = self.to_canvas(ev.x * self.disp_w, ev.y * self.disp_h)
                if ev.touch_id in self.stick_hits:
                    self._stick_update(ev.touch_id, self.mouse)
                if ev.touch_id in self.swipe:
                    side, x0 = self.swipe[ev.touch_id]
                    d = self.mouse[0] - x0
                    self.swipe_dir[side] = 1 if d > 18 else (-1 if d < -18 else 0)
            elif ev.type == FINGER_UP:
                if bridge:
                    continue
                self.on_touch_up(ev.touch_id)

    def _diag(self, line):
        """诊断日志只留最近 9 条，F9 关闭时也照常收集，方便随时打开看。"""
        self.diag_log.append(line)
        if len(self.diag_log) > 9:
            self.diag_log.pop(0)

    def _draw_diag(self, s):
        """F9 诊断叠层：显示原始坐标 / 画布坐标 / 最近事件 / 运行环境。"""
        if not self.diag:
            return
        r = pygame.Rect(296, 176, 688, 326)
        ov = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        ov.fill((6, 9, 24, 232))
        s.blit(ov, r.topleft)
        pygame.draw.rect(s, (255, 208, 96), r, 2, border_radius=10)
        draw_text(s, "输入诊断 · F9 / 右上角按钮开关 · 截图发我",
                  r.x + 16, r.y + 10, 19, COL_GOLD, True)
        cv = self.to_canvas(*self.last_raw)
        info = self.web_bridge_info or {}
        ev = self.last_web_ev or {}
        lines = [
            "输入源：%s  |  虚拟画布 %dx%d  |  帧 %d  |  页面 %s" %
            ("JS 桥（自算坐标）" if self.web_bridge else "SDL 回退",
             SCREEN_W, SCREEN_H, self.t, self.scene),
            "canvas 内部 %sx%s  /  显示 %sx%s  /  PointerEvent %s" %
            (info.get("cw", "?"), info.get("ch", "?"),
             info.get("rw", "?"), info.get("rh", "?"),
             "是" if info.get("pe") else "否"),
            "最近点击 (%4d,%4d)  canvas=%sx%s  rect=%sx%s" %
            (ev.get("x", self.last_raw[0]), ev.get("y", self.last_raw[1]),
             ev.get("cw", "?"), ev.get("ch", "?"),
             ev.get("rw", "?"), ev.get("rh", "?")),
            "点右下技能键应接近 (1100,600)；下面列最近事件",
        ] + list(reversed(self.diag_log))[:5]
        for i, ln in enumerate(lines):
            draw_text(s, ln, r.x + 16, r.y + 44 + i * 34,
                      15, COL_TEXT if i < 3 else COL_DIM)

    def _present(self):
        """把 1280×720 虚拟画布等比缩放居中贴到手机全屏（不裁切）。"""
        if self.disp is None:
            pygame.display.flip()
            return
        frame = (pygame.transform.smoothscale(self.screen, (self.out_w, self.out_h))
                 if MOBILE_SMOOTH else
                 pygame.transform.scale(self.screen, (self.out_w, self.out_h)))
        self.disp.fill((0, 0, 0))
        self.disp.blit(frame, self.off)
        pygame.display.flip()

    async def run(self):
        """主循环骨架：计时 → 收事件 → 合成按键 → 更新 → 绘制 → 呈现。
        await asyncio.sleep(0) 是 pygbag 的硬性要求：每帧把控制权还给浏览器，
        否则 JS 事件循环拿不到时间片，标签页会直接卡死。桌面下几乎零开销。"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += 1
            self._poll_events()
            keys = self.synth_keys()
            self.update(dt, keys, self.just)
            self.draw()
            self._present()
            await asyncio.sleep(0)
        pygame.quit()

    def update(self, dt, keys, just):
        """按当前页面分发更新。"""
        # 浏览器可能只跑 30fps，而位移原本是「每帧固定像素」，会整体变慢。
        # 这里按真实帧间隔算出补偿系数，交给 Fighter 使用。
        if FRAME_COMPENSATE:
            self.frame_scale = clamp(dt * FPS, FRAME_SCALE_MIN, FRAME_SCALE_MAX)
        else:
            self.frame_scale = 1.0
        self.clear_confirm = max(0, self.clear_confirm - 1)
        if self.scene == "menu":
            self.upd_menu(keys, just)
        elif self.scene == "select":
            self.upd_select(keys, just)
        elif self.scene == "settings":
            self.upd_settings(keys, just)
        elif self.scene == "game":
            self.upd_game(dt, keys, just)
        elif self.scene == "stats":
            self.upd_stats(keys, just)
        elif self.scene == "help":
            self.upd_help(keys, just)

    def upd_help(self, keys, just):
        """操作说明页：Esc / 点「返回主页面」退出（战斗中进来也回主页面）。"""
        if GLOBAL_KEYS["cancel"] in just or GLOBAL_KEYS["confirm"] in just:
            self.scene = "menu"
        for pos, btn in self.clicks:
            if btn == 1 and self.help_back[0].collidepoint(pos):
                self.scene = "menu"
                return

    # ---- 主页面 ----
    def upd_menu(self, keys, just):
        k = GLOBAL_KEYS
        if pygame.K_UP in just:
            self.menu_idx = (self.menu_idx - 1) % len(self.menu_items)
        if pygame.K_DOWN in just:
            self.menu_idx = (self.menu_idx + 1) % len(self.menu_items)
        for i, (pos, btn) in enumerate(self.clicks):
            if btn == 1 and self._menu_rect(i).collidepoint(pos):
                self.menu_idx = i
                self._do_menu(i)
                return
        if k["confirm"] in just or pygame.K_SPACE in just:
            self._do_menu(self.menu_idx)

    def _menu_rect(self, i):
        return pygame.Rect(SCREEN_W // 2 - 190, 292 + i * 56, 380, 48)

    def _do_menu(self, i):
        if i == 0:
            self.start_match()
        elif i == 1:
            self.lock = {1: False, 2: False}
            self.scene = "select"
        elif i == 2:
            self.scene = "settings"
        elif i == 3:
            self.scene = "help"
        elif i == 4:
            self.scene = "stats"
        elif i == 5:
            self.running = False

    # ---- 角色选择页 ----
    def upd_select(self, keys, just):
        k = GLOBAL_KEYS
        n = len(CHARACTERS)
        cols = 4
        # P1 用 WASD 移动光标，J 锁定；P2 用方向键移动，1 锁定
        p1 = KEYS_P1
        p2 = KEYS_P2
        if p1["left"] in just:
            self.cur[1] = (self.cur[1] - 1) % n
        if p1["right"] in just:
            self.cur[1] = (self.cur[1] + 1) % n
        if p1["up"] in just:
            self.cur[1] = (self.cur[1] - cols) % n
        if p1["guard"] in just:
            self.cur[1] = (self.cur[1] + cols) % n
        if p2["left"] in just:
            self.cur[2] = (self.cur[2] - 1) % n
        if p2["right"] in just:
            self.cur[2] = (self.cur[2] + 1) % n
        if p2["up"] in just:
            self.cur[2] = (self.cur[2] - cols) % n
        if p2["guard"] in just:
            self.cur[2] = (self.cur[2] + cols) % n
        if p1["atk"] in just:
            self.sel[1], self.lock[1] = self.cur[1], True
        if p2["atk"] in just:
            self.sel[2], self.lock[2] = self.cur[2], True
        # 鼠标：左键给 P1，右键给 P2
        for pos, btn in self.clicks:
            idx = self._card_index(pos)
            if idx is not None:
                if btn == 1:
                    self.cur[1] = self.sel[1] = idx
                    self.lock[1] = True
                elif btn == 3:
                    self.cur[2] = self.sel[2] = idx
                    self.lock[2] = True
        if self._start_btn().collidepoint(self.mouse) and any(b == 1 for _, b in self.clicks):
            self.start_match()
            return
        if k["confirm"] in just:
            self.start_match()
            return
        if k["cancel"] in just:
            self.scene = "menu"

    def _card_rect(self, idx):
        cols = 4
        cw, ch, gx, gy = 268, 208, 16, 16
        x0 = (SCREEN_W - (cols * cw + (cols - 1) * gx)) // 2
        y0 = 148
        return pygame.Rect(x0 + (idx % cols) * (cw + gx),
                           y0 + (idx // cols) * (ch + gy), cw, ch)

    def _card_index(self, pos):
        for i in range(len(CHARACTERS)):
            if self._card_rect(i).collidepoint(pos):
                return i
        return None

    def _start_btn(self):
        return pygame.Rect(SCREEN_W // 2 - 160, SCREEN_H - 96, 320, 52)

    # ---- 对局设置页 ----
    def upd_settings(self, keys, just):
        k = GLOBAL_KEYS
        items = 8
        if pygame.K_UP in just:
            self.settings_idx = (self.settings_idx - 1) % items
        if pygame.K_DOWN in just:
            self.settings_idx = (self.settings_idx + 1) % items
        if pygame.K_LEFT in just or pygame.K_RIGHT in just:
            d = 1 if pygame.K_RIGHT in just else -1
            i = self.settings_idx
            if i == 0:
                self.mode = MODE_PVP if self.mode == MODE_PVE else MODE_PVE
            elif i == 1:
                self.arena_idx = (self.arena_idx + d) % len(ARENAS)
            elif i == 2:
                lst = ARENA_EFFECT_ORDER
                self.arena_effect = lst[(lst.index(self.arena_effect) + d) % len(lst)]
            elif i == 3:
                self.scroll_id = SCROLL_ORDER[(SCROLL_ORDER.index(self.scroll_id) + d) % len(SCROLL_ORDER)]
            elif i == 4:
                self.move_ui = MOVE_UI_OPTIONS[(MOVE_UI_OPTIONS.index(self.move_ui) + d) % len(MOVE_UI_OPTIONS)]
            elif i == 5:
                self.time_idx = (self.time_idx + d) % len(TIME_OPTIONS)
            elif i == 6:
                self.hp_idx = (self.hp_idx + d) % len(HP_SCALE_OPTIONS)
            else:
                self.training = not self.training
        if k["cancel"] in just or k["confirm"] in just:
            self.scene = "menu"

    # ---- 战绩页 ----
    def upd_stats(self, keys, just):
        k = GLOBAL_KEYS
        if k["clear_stats"] in just:
            if self.clear_confirm > 0:
                self.reset_stats()
                self.clear_confirm = 0
            else:
                self.clear_confirm = 180      # 3 秒内再按一次 C 才真清空
        if k["cancel"] in just or k["confirm"] in just:
            self.scene = "menu"

    # ---- 游戏页 ----
    def _advance_banner(self):
        """开局 准备 → 开打 → 消失 的提示计时。"""
        self.banner_t = max(0, self.banner_t - 1)
        if self.banner_t == 0 and self.banner == "准备":
            self.banner, self.banner_t = "开打", 45
        elif self.banner_t == 0:
            self.banner = ""

    def _tick_round_timer(self, dt):
        """回合倒计时；训练模式 / 无限时不扣，时间到按血量比判胜。"""
        if not self.training and TIME_OPTIONS[self.time_idx] > 0:
            self.time_left = max(0.0, self.time_left - dt)
            if self.time_left <= 0:
                self.finish(winner=0)

    def _training_regen(self):
        """训练模式每帧回血，方便无限连招练习（血量倍率越高回得越多）。"""
        regen = TRAIN_REGEN * HP_SCALE_OPTIONS[self.hp_idx] / float(FPS)
        for f in (self.p1, self.p2):
            f.hp = min(f.max_hp, f.hp + regen)

    def _update_particles_only(self):
        """结算覆盖层出现后只让粒子 / 浮字继续飘，画面不僵住。"""
        for group in (self.particles, self.floats):
            for e in group:
                e.update()
            group[:] = [e for e in group if not e.dead]

    def _separate_fighters(self):
        """v3.2：允许跳过对手 / 绕背，不再把 P1 永远锁在左边。
        · 任意一方在空中（y < 地面线）→ 完全不推开，可直接跳过去；
        · 双方都落地且几乎重合时，按当前左右关系轻轻推开一点点（d<0 也不强行翻回来）。
        """
        if self.p1.y < GROUND_Y - 2 or self.p2.y < GROUND_Y - 2:
            return
        d = self.p2.x - self.p1.x
        limit = BODY_W * 0.34
        if abs(d) < limit:
            push = (limit - abs(d)) / 2.0 * (1 if d >= 0 else -1)
            self.p1.x -= push
            self.p2.x += push

    def _update_entities(self):
        """推进投射物 / 援助 / 粒子 / 浮字 / 刀光，并清掉已结束的实体。"""
        for p in self.projectiles:
            p.update(self)
        for a in self.assists:
            a.update(self)
        for e in self.particles:
            e.update()
        for e in self.floats:
            e.update()
        for s in self.slashes:
            s["t"] -= 1
        self.projectiles[:] = [p for p in self.projectiles if not p.dead]
        self.assists[:] = [a for a in self.assists if not a.dead]
        self.particles[:] = [e for e in self.particles if not e.dead]
        self.floats[:] = [e for e in self.floats if not e.dead]
        self.slashes[:] = [s for s in self.slashes if s["t"] > 0]

    def upd_game(self, dt, keys, just):
        """游戏页每帧编排：暂停开关 → 结算/计时/回血 → 双方更新 → 实体 → 判定。"""
        k = GLOBAL_KEYS
        self.over_t += 1 if self.over else 0
        self.shake = max(0, self.shake - 1)

        # 暂停开关：同一个键 / 同一个「暂停 / 继续」按钮，再按一次恢复。
        # 之前只写了个 banner 且计时设 0，下一帧就被清掉，等于没暂停 —— 这里修好。
        if k["pause"] in just:
            self.paused = not self.paused
        if self.paused and not self.over:
            return   # 计时、角色、实体全部冻结；画面由 draw() 画暂停遮罩

        self._advance_banner()

        if self.over:
            if k["restart"] in just:
                self.start_match()
            elif k["cancel"] in just:
                self.scene = "menu"
            self._update_particles_only()
            return

        self._tick_round_timer(dt)
        if self.training:
            self._training_regen()
        # ---- v3：动作分发 / 技能前摇 / 场地机制 / 被动 ----
        dispatch_actions(self, just)
        tick_pending_skills(self)
        tick_arena(self)
        for _f in (self.p1, self.p2):
            tick_passive(self, _f)

        self.p1.update(self, keys, just)
        self.p2.update(self, keys, just)
        self._separate_fighters()
        self._update_entities()

    # ---- 总绘制入口 ----
    def draw(self):
        s = self.screen
        if self.scene == "game":
            ox = random.randint(-self.shake, self.shake) if self.shake else 0
            oy = random.randint(-self.shake, self.shake) if self.shake else 0
            s.fill(COL_BG_TOP)
            buf = pygame.Surface((SCREEN_W, SCREEN_H))
            draw_background(buf, self.t, self)
            self.draw_game(buf)
            s.blit(buf, (ox, oy))
            if self.paused and not self.over:
                mask = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                mask.fill((6, 8, 24, 165))
                s.blit(mask, (0, 0))
                draw_text(s, "已暂停", SCREEN_W // 2, 236, 80,
                          COL_GOLD, True, "center")
                draw_text(s, "再点一次「暂停 / 继续」开打", SCREEN_W // 2, 344, 28,
                          COL_TEXT, align="center")
                draw_text(s, "也可以点中间「再战」重开一局", SCREEN_W // 2, 390, 22,
                          COL_DIM, align="center")
        elif self.scene == "menu":
            self.draw_menu(s)
        elif self.scene == "help":
            self.draw_help(s)
        elif self.scene == "select":
            self.draw_select(s)
        elif self.scene == "settings":
            self.draw_settings(s)
        elif self.scene == "stats":
            self.draw_stats(s)
        # 全局页脚（游戏页底部是虚拟按键，不再叠一层页脚）
        if self.scene != "game":
            draw_text(s, "AI娘大乱斗 " + VERSION + "  |  横屏触屏 · 图形版 · 点按即玩",
                      12, SCREEN_H - 26, 15, COL_DIM)
        # 虚拟按键画在最上层（selftest 里自动跳过，不影响逻辑自检）
        self.draw_touch_layer(s)
        # F9 诊断画在【所有东西之上】，包括虚拟按键，保证截图看得见
        self._draw_diag(s)

    # ---- 主页面 ----
    def draw_menu(self, s):
        draw_background(s, self.t, self)
        # 顶部装饰：8 位角色的小头像横排
        for i, ch in enumerate(CHARACTERS):
            cx = 90 + i * (SCREEN_W - 180) / max(1, len(CHARACTERS) - 1)
            cy = 108 + math.sin(self.t * 0.03 + i) * 8
            pygame.draw.circle(s, shade(ch["color"], 0.8), (int(cx), int(cy)), 26)
            pygame.draw.circle(s, ch["color"], (int(cx), int(cy)), 21)
            pygame.draw.circle(s, ch["accent"], (int(cx), int(cy)), 9)
            draw_text(s, ch["short"], cx, cy + 32, 14, COL_DIM, align="center")

        draw_text(s, "AI娘大乱斗", SCREEN_W // 2, 156, 70, COL_TEXT, True, "center")
        draw_text(s, "AI MUSUME FIGHT  ·  4399 键位  ·  4 技能 / 闪避 / 净化 / 秘卷",
                  SCREEN_W // 2, 232, 20, COL_GOLD, False, "center")

        # 左列：6 个菜单项（x 450~830）；右列：模式 / 操作卡片（x 880~1110）
        for i, label in enumerate(self.menu_items):
            r = self._menu_rect(i)
            hot = (i == self.menu_idx)
            draw_panel(s, r, COL_PANEL_LIGHT if hot else COL_PANEL,
                       COL_GOLD if hot else COL_PANEL_LIGHT, 12, 2 if hot else 1)
            draw_text(s, ("▶  " if hot else "   ") + label,
                      r.x + 28, r.y + 10, 24, COL_GOLD if hot else COL_TEXT, hot)
        # 右侧卡片由 draw_touch_layer 统一画底色，这里只补标题和两行短说明
        draw_text(s, "开局前先选", 995, 258, 20, COL_GOLD, True, "center")
        draw_text(s, "PVE = 只你一套键", 995, 440, 15, COL_DIM, align="center")
        draw_text(s, "PVP = 两人各一套", 995, 462, 15, COL_DIM, align="center")
        draw_text(s, "摇杆 / 键盘 / 滑动 可切换", 995, 484, 14, COL_DIM, align="center")
        draw_text(s, "点「操作说明」看完整键位表", 995, 512, 14, COL_GOLD, align="center")
        info = "时间 %s   |   血量 %s   |   训练 %s   |   P1 %s   P2 %s" % (
            TIME_LABELS[self.time_idx], HP_SCALE_LABELS[self.hp_idx],
            "ON" if self.training else "OFF",
            CHARACTERS[self.sel[1]]["short"], CHARACTERS[self.sel[2]]["short"])
        draw_text(s, info, SCREEN_W // 2, 652, 17, COL_DIM, align="center")
        # v3.2：旧提示行删掉，底部只留 info + 一行操作说明，不再三行叠字

    # ---- 操作说明页（v3.2 新增）----
    def draw_help(self, s):
        draw_background(s, self.t, self)
        draw_text(s, "操作说明", SCREEN_W // 2, 54, 44, COL_TEXT, True, "center")
        draw_text(s, "每个触屏键下方都标了键盘键名，两边完全对应",
                  SCREEN_W // 2, 104, 17, COL_GOLD, align="center")

        # 左半：键盘键位表
        left = pygame.Rect(40, 140, 600, 500)
        draw_panel(s, left, COL_PANEL, COL_PANEL_LIGHT, 12, 1)
        draw_text(s, "键盘（4399《死神VS火影》键位）", left.x + 20, 154, 22, COL_P1, True)
        rows1 = [
            ("P1 移动", "A / D 左右    W 上挑修饰    S 防御"),
            ("P1 攻击", "J 普攻     K 跳跃     J+K 变身"),
            ("P1 技能", "U 技1     I 技2     O 技3     L 奥义"),
            ("P1 功能", "Q 闪避     E 净化     Z 秘卷"),
            ("", ""),
            ("P2 主键盘", "1 攻 2 跳  4/5/6 技  3 奥义  7/8/9 功能"),
            ("P2 小键盘", "Num1 攻 Num2 跳 Num4/5/6 技 Num3 奥义"),
            ("单人 PVE", "小键盘自动归 P1，右手不用伸到字母区"),
            ("诊断", "点右上角「输入诊断」或按 F9，截图发我"),
        ]
        for i, (a, b) in enumerate(rows1):
            y = 192 + i * 44
            if a:
                draw_text(s, a, left.x + 20, y, 17, COL_GOLD, True)
                draw_text(s, b, left.x + 130, y, 16, COL_TEXT)
        draw_text(s, "小键盘需 NumLock 灯亮（数字模式）；旧冲刺/远攻/必杀/援助已删",
                  left.x + 20, 596, 14, COL_DIM)

        # 右半：触屏键位 + 技能说明
        right = pygame.Rect(660, 140, 580, 500)
        draw_panel(s, right, COL_PANEL, COL_PANEL_LIGHT, 12, 1)
        draw_text(s, "触屏按键（左右各一套，位置对称）", right.x + 20, 154, 22, COL_P2, True)
        rows2 = [
            ("摇杆", "左右移动，上＝上挑，下＝防御；底盘不动"),
            ("普攻 大圆", "连击起手，键面标 J / 1"),
            ("3 个技能圆", "技1 / 技2 / 技3，键面写角色专属短名"),
            ("金色奥义圆", "耗 2 格气，键面标 L / 3"),
            ("跳 横胶囊", "起跳可越过对手绕背，键面标 K / 2"),
            ("闪避", "小位移 + 短无敌，专门躲技能"),
            ("净化", "解除定身 / 催眠 / 沉默等负面"),
            ("秘卷", "霸体 / 控制 / 强化 / 替身… 设置页可换"),
        ]
        for i, (a, b) in enumerate(rows2):
            y = 192 + i * 44
            draw_text(s, a, right.x + 20, y, 17, COL_GOLD, True)
            draw_text(s, b, right.x + 150, y, 15, COL_TEXT)
        ch = CHARACTERS[self.sel[1]]
        names = [skill_spec(ch["id"], sl).get("name", "?") for sl in SKILL_SLOTS]
        kit = SKILL_KITS.get(ch["id"], SKILL_KITS["deepseek"])
        draw_text(s, "%s 的四个技能：" % ch["short"], right.x + 20, 560, 16, COL_TEXT, True)
        draw_text(s, " · ".join(names), right.x + 20, 584, 14, COL_TEXT)
        draw_text(s, "联动 %s → %s：%s" % (SKILL_LABEL[kit["link_from"]],
                  SKILL_LABEL[kit["link_to"]], kit["link_desc"]),
                  right.x + 20, 606, 13, COL_GOLD)
        draw_text(s, "点左上「返回主页面」或按 Esc 退出  ·  游戏中按 F9 可开输入诊断",
                  SCREEN_W // 2, 664, 16, COL_DIM, align="center")

    # ---- 角色选择页 ----
    def draw_select(self, s):
        draw_background(s, self.t, self)
        draw_text(s, "角色选择", SCREEN_W // 2, 24, 44, COL_TEXT, True, "center")
        draw_text(s, "点卡片选角色 · 先点右上「选给：P1/P2」切换归属 · 再点底部开始对战",
                  SCREEN_W // 2, 82, 17, COL_DIM, align="center")

        for i, ch in enumerate(CHARACTERS):
            r = self._card_rect(i)
            chosen = (self.sel[1] == i, self.sel[2] == i)
            cur = (self.cur[1] == i, self.cur[2] == i)
            border = COL_GOLD if any(chosen) else COL_PANEL_LIGHT
            draw_panel(s, r, COL_PANEL, border, 14, 3 if any(chosen) else 1)
            # 头像圆 + 可选立绘
            portrait = load_portrait(ch["id"])
            if portrait:
                img = pygame.transform.smoothscale(portrait, (64, 64))
                s.blit(img, (r.x + 14, r.y + 14))
            else:
                pygame.draw.circle(s, shade(ch["color"], 0.7), (r.x + 46, r.y + 46), 30)
                pygame.draw.circle(s, ch["color"], (r.x + 46, r.y + 46), 24)
                pygame.draw.circle(s, ch["accent"], (r.x + 46, r.y + 46), 11)
            draw_text(s, ch["name"], r.x + 92, r.y + 18, 20, COL_TEXT, True)
            draw_text(s, ch["lore"], r.x + 14, r.y + 84, 14, COL_DIM)
            # 属性条
            for j, (key, lab) in enumerate((("hp", "血"), ("atk", "攻"), ("speed", "速"))):
                v = ch["stats"][key]
                draw_text(s, lab, r.x + 14, r.y + 112 + j * 22, 13, COL_DIM)
                draw_bar(s, pygame.Rect(r.x + 36, r.y + 114 + j * 22, 150, 12),
                         v / 1.25, ch["color"])
            draw_text(s, "必杀 " + ch["skills"]["ult"], r.x + 14, r.y + 182, 14, COL_GOLD)
            # 阵营角标
            if chosen[0]:
                pygame.draw.circle(s, COL_P1, (r.right - 18, r.y + 18), 12)
                draw_text(s, "1", r.right - 18, r.y + 7, 16, (0, 0, 0), True, "center")
            if chosen[1]:
                pygame.draw.circle(s, COL_P2, (r.right - 18, r.y + 46), 12)
                draw_text(s, "2", r.right - 18, r.y + 35, 16, (0, 0, 0), True, "center")
            if cur[0]:
                pygame.draw.rect(s, COL_P1, r, 2, border_radius=14)
            if cur[1]:
                pygame.draw.rect(s, COL_P2, (r.x + 2, r.y + 2, r.w - 4, r.h - 4), 2, border_radius=14)

        b = self._start_btn()
        draw_panel(s, b, COL_PANEL_LIGHT, COL_GOLD, 12, 2)
        draw_text(s, "Enter / 点击这里  开始对战", b.centerx, b.y + 13, 22, COL_GOLD, True, "center")
        draw_text(s, "Esc 返回主页面", SCREEN_W // 2, SCREEN_H - 44, 16, COL_DIM, align="center")

    # ---- 对局设置页 ----
    def draw_settings(self, s):
        draw_background(s, self.t, self)
        draw_text(s, "对局设置", SCREEN_W // 2, 90, 52, COL_TEXT, True, "center")
        arena = ARENAS[self.arena_idx % len(ARENAS)]
        eff = ARENA_EFFECTS[self.arena_effect]
        rows = [
            ("对局模式", "PVE 单人" if self.mode == MODE_PVE else "PVP 双人",
             "PVE 只显示 P1 按键 / PVP 双方可见"),
            ("场地风格", arena["name"], arena["desc"]),
            ("场地机制", eff["name"], eff["desc"] + "（默认关闭保证平衡）"),
            ("秘卷", self.scroll_id, SCROLLS[self.scroll_id]["desc"]),
            ("移动键", MOVE_UI_LABELS[MOVE_UI_OPTIONS.index(self.move_ui)],
             "自动：手机显示摇杆，电脑窗口隐藏用键盘"),
            ("回合时间", TIME_LABELS[self.time_idx], "0 = 无限时"),
            ("血量倍率", HP_SCALE_LABELS[self.hp_idx], "100% ~ 500%"),
            ("训练模式", "ON" if self.training else "OFF", "无限时 / 自动回血 / 不记录战绩"),
        ]
        for i, (name, val, note) in enumerate(rows):
            r = pygame.Rect(SCREEN_W // 2 - 350, 156 + i * 60, 700, 54)
            hot = i == self.settings_idx
            draw_panel(s, r, COL_PANEL_LIGHT if hot else COL_PANEL,
                       COL_GOLD if hot else COL_PANEL_LIGHT, 10, 2 if hot else 1)
            draw_text(s, name, r.x + 18, r.y + 8, 20, COL_TEXT, True)
            draw_text(s, "◀  " + val + "  ▶", r.right - 18, r.y + 8, 20,
                      COL_GOLD if hot else COL_TEXT, True, "right")
            draw_text(s, note, r.x + 18, r.y + 32, 13, COL_DIM)
        draw_text(s, "点行选中 · ←→ 或左右滑动改值 · Esc 返回",
                  SCREEN_W // 2, 664, 18, COL_DIM, align="center")

    # ---- 战绩页 ----
    def draw_stats(self, s):
        draw_background(s, self.t, self)
        draw_text(s, "P1 / P2 战绩", SCREEN_W // 2, 40, 48, COL_TEXT, True, "center")
        draw_text(s, "数据保存在 " + STATS_FILE + "（关闭程序不会丢）",
                  SCREEN_W // 2, 100, 17, COL_DIM, align="center")

        for side, color, x0 in ((1, COL_P1, 70), (2, COL_P2, SCREEN_W // 2 + 30)):
            d = self.stats["P1" if side == 1 else "P2"]
            r = pygame.Rect(x0, 140, SCREEN_W // 2 - 100, 400)
            draw_panel(s, r, COL_PANEL, color, 16, 3)
            draw_text(s, "P" + str(side), r.x + 24, r.y + 16, 34, color, True)
            rate = d["wins"] / float(d["matches"]) * 100 if d["matches"] else 0
            items = [
                ("总场次", str(d["matches"])),
                ("胜场 / 胜率", "%d  /  %.1f%%" % (d["wins"], rate)),
                ("累计伤害", str(d["damage"])),
                ("最大连击", str(d["max_combo"]) + " HIT"),
            ]
            for i, (k, v) in enumerate(items):
                yy = r.y + 70 + i * 44
                draw_text(s, k, r.x + 24, yy, 20, COL_DIM)
                draw_text(s, v, r.right - 24, yy, 22, COL_TEXT, True, "right")
            # 常用角色
            fav = "-"
            if d["chars"]:
                cid = max(d["chars"], key=d["chars"].get)
                fav = next((c["short"] for c in CHARACTERS if c["id"] == cid), cid)
            draw_text(s, "常用角色  " + fav, r.x + 24, r.y + 256, 18, COL_GOLD)
            draw_text(s, "最近对局", r.x + 24, r.y + 292, 18, COL_DIM)
            for i, rec in enumerate(d["recent"][:5]):
                draw_text(s, "%s  %s  伤害%d  %dHIT  %s" % (
                    rec.get("ts", ""), rec.get("result", ""), rec.get("dmg", 0),
                    rec.get("combo", 0), rec.get("char", "")),
                    r.x + 24, r.y + 318 + i * 16, 14, COL_DIM)

        tip = "再按一次 C 确认清空战绩" if self.clear_confirm > 0 else "右上角 C 清空战绩 · Esc 返回"
        draw_text(s, tip, SCREEN_W // 2, SCREEN_H - 62, 18,
                  COL_HP_LOW if self.clear_confirm > 0 else COL_DIM, align="center")

    # ---- 游戏页 ----
    def draw_game(self, s):
        # 背景之后先画场地上的实体
        for a in self.assists:
            a.draw(s)
        for p in self.projectiles:
            p.draw(s)
        for sl in self.slashes:
            draw_slash(s, sl["x"], sl["y"], sl["face"], sl["color"], sl["t"])
        draw_fighter(s, self.p1, self.t)
        draw_fighter(s, self.p2, self.t)
        draw_skill_rings(s, self)
        for e in self.particles:
            e.draw(s)
        for e in self.floats:
            e.draw(s)
        self.draw_hud(s)
        if self.banner and not self.over:
            draw_text(s, self.banner, SCREEN_W // 2, 210, 68, COL_GOLD, True, "center")
        if self.over:
            self.draw_result(s)

    def _draw_side_hud(self, s, f, reverse, color, x):
        """单侧 HUD：名字 / 血条 / 数值 / 3 格气条 / 变身标记 / 连击数。"""
        r = pygame.Rect(x, 30, 480, 26)
        ratio = f.hp / max(1.0, f.max_hp)
        hp_col = COL_HP if ratio > 0.3 else COL_HP_LOW
        draw_bar(s, r, ratio, hp_col, reverse=reverse)
        pygame.draw.rect(s, COL_PANEL_LIGHT, r, 2, border_radius=6)
        draw_text(s, "P%d  %s" % (f.side, f.char["name"]),
                  x if not reverse else x + 480, 8, 19, color, True,
                  "left" if not reverse else "right")
        draw_text(s, "%d / %d" % (int(f.hp), int(f.max_hp)),
                  x + (10 if not reverse else 470), 33, 15, COL_TEXT,
                  False, "left" if not reverse else "right")
        draw_rage(s, pygame.Rect(x, 62, 300, 14), f.rage)
        draw_text(s, "气 %d/3" % (f.rage // RAGE_PER_GRID),
                  x + (310 if not reverse else 0), 59, 15,
                  COL_RAGE_FULL if f.rage >= RAGE_MAX else COL_DIM)
        if f.transformed:
            draw_text(s, "◆ " + f.char["skills"]["transform"],
                      x if not reverse else x + 480, 82, 16, COL_GOLD,
                      True, "left" if not reverse else "right")
        if f.combo >= 2 and f.combo_t > 0:
            draw_text(s, "%d HIT" % f.combo,
                      SCREEN_W // 2 + (-140 if f.side == 1 else 140), 110,
                      30, color, True, "center")

    def _draw_center_timer(self, s):
        """中央计时牌：训练 / 无限时显示文字，否则显示剩余秒数。"""
        if self.training or TIME_OPTIONS[self.time_idx] == 0:
            label = "TRAINING" if self.training else "∞"
            col = COL_GOLD if self.training else COL_TEXT
        else:
            label = str(int(math.ceil(self.time_left)))
            col = COL_HP_LOW if self.time_left < 10 else COL_TEXT
        draw_panel(s, pygame.Rect(SCREEN_W // 2 - 62, 20, 124, 62),
                   COL_PANEL, COL_GOLD, 12, 2)
        draw_text(s, label, SCREEN_W // 2, 30, 40, col, True, "center")

    def _draw_keybar(self, s):
        """底部键位速记：仅在纯键盘模式显示（手机/网页下方要留给虚拟按键提示）。
        触屏下每个键面已标键名，完整表在「操作说明」页，不在这里叠字。"""
        if MOBILE_TOUCH:
            return
        draw_text(s, "P1  J攻 K跳  U技1 I技2 O技3 L奥义  Q闪 E净 Z卷",
                  20, SCREEN_H - 30, 14, COL_P1)
        draw_text(s, "P2  1攻 2跳  4技1 5技2 6技3 3奥义  7闪 8净 9卷（小键盘同位置）",
                  SCREEN_W - 20, SCREEN_H - 30, 14, COL_P2, align="right")

    def draw_hud(self, s):
        """战斗 HUD v3：左右两侧 → 状态徽章 / 秘卷 / 场地名 → 中央计时 → 键盘提示。"""
        self._draw_side_hud(s, self.p1, False, COL_P1, 36)
        self._draw_side_hud(s, self.p2, True, COL_P2, SCREEN_W - 36 - 480)
        # 状态徽章放在两侧、第 108 行，与中央文字错开，不互相压字
        draw_status_badges(s, self.p1, 36, 108)
        draw_status_badges(s, self.p2, SCREEN_W - 36, 108, "right")
        arena = ARENAS[self.arena_idx % len(ARENAS)]
        eff = ARENA_EFFECTS[self.arena_effect]
        # ---- v3.2 顶部技能说明条：PVP 同时列出双方，不再只有 P1 ----
        bar = pygame.Rect(300, 96, 680, 56)
        draw_panel(s, bar, (12, 16, 38), COL_PANEL_LIGHT, 10, 1)
        n1 = [skill_spec(self.p1.char["id"], sl).get("name", "?") for sl in SKILL_SLOTS]
        if self.mode == MODE_PVP:
            n2 = [skill_spec(self.p2.char["id"], sl).get("name", "?") for sl in SKILL_SLOTS]
            draw_text(s, "P1  " + " / ".join(n1), bar.centerx, 101, 14,
                      COL_P1, True, "center")
            draw_text(s, "P2  " + " / ".join(n2), bar.centerx, 125, 14,
                      COL_P2, True, "center")
        else:
            a, b = skill_help_lines(self.p1.char["id"])
            draw_text(s, a, bar.centerx, 101, 15, COL_TEXT, True, "center")
            draw_text(s, b, bar.centerx, 125, 13, COL_GOLD, False, "center")
        line = "%s  ·  %s  ·  %s  ·  秘卷 %s  ·  点中间「说明」看键位" % (
            self.mode_label(), self.input_label(), arena["name"], self.scroll_id)
        draw_text(s, line, SCREEN_W // 2, 162, 14, eff["color"], align="center")
        self._draw_center_timer(s)
        self._draw_keybar(s)

    def draw_result(self, s):
        """结算覆盖层：胜者 + 双方本局数据 + 再战/返回提示。"""
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((6, 8, 20, 190))
        s.blit(ov, (0, 0))
        if self.winner == 0:
            title, col = "DRAW  ·  平局", COL_GOLD
        else:
            title = "P%d  WIN!" % self.winner
            col = COL_P1 if self.winner == 1 else COL_P2
        draw_text(s, title, SCREEN_W // 2, 176, 84, col, True, "center")
        if self.training:
            draw_text(s, "训练模式 · 本局不计入战绩", SCREEN_W // 2, 268, 20,
                      COL_DIM, align="center")
        for f, x in ((self.p1, SCREEN_W // 2 - 240), (self.p2, SCREEN_W // 2 + 240)):
            draw_text(s, f.char["name"], x, 300, 24,
                      COL_P1 if f.side == 1 else COL_P2, True, "center")
            draw_text(s, "造成伤害  %d" % int(f.dealt), x, 338, 19, COL_TEXT, align="center")
            draw_text(s, "最大连击  %d HIT" % f.max_combo, x, 368, 19, COL_TEXT, align="center")
            draw_text(s, "剩余血量  %d" % int(f.hp), x, 398, 19, COL_TEXT, align="center")
        draw_text(s, "点下方按钮再战 / 回主页面   （键盘 R 再战 · Esc 返回）",
                  SCREEN_W // 2, 470, 22, COL_GOLD, True, "center")


# ==============================================================================
# ⑦ 自检与入口 —— --selftest 可在无显示环境验证语法与逻辑
# ==============================================================================

def run_selftest():
    """无窗口自检：校验配置、按键冲突、角色数据，并空跑一局 60 秒逻辑。"""
    print("[1/6] 检查 CONFIG ...")
    assert len(CHARACTERS) == 8, "角色数量应为 8"
    assert RAGE_MAX == RAGE_PER_GRID * 3, "怒气上限应为 3 格"
    assert 0 <= DEFAULT_TIME_IDX < len(TIME_OPTIONS)
    assert 0 <= DEFAULT_HP_IDX < len(HP_SCALE_OPTIONS)
    for ch in CHARACTERS:
        assert set(("hp", "atk", "speed")) <= set(ch["stats"]), ch["id"]
        assert len(ch["skills"]) >= 7, ch["id"]
        assert ch["id"] in SKILL_KITS, "角色缺技能组: " + ch["id"]
        kit = SKILL_KITS[ch["id"]]
        assert set(SKILL_SLOTS) <= set(kit["skills"]), "技能槽不齐: " + ch["id"]
        assert kit["link_from"] in kit["skills"] and kit["link_to"] in kit["skills"], ch["id"]
        assert kit["skills"][kit["link_to"]].get("consume"), "联动目标没写 consume: " + ch["id"]
        assert kit["skills"][kit["link_from"]].get("tag"), "联动起点没写 tag: " + ch["id"]
        for slot in SKILL_SLOTS:
            sp = skill_spec(ch["id"], slot)
            assert sp["cd"] > 0 and sp["dmg"] > 0 and sp["startup"] >= 0, (ch["id"], slot)
    assert len(SCROLLS) == len(SCROLL_ORDER) and DEFAULT_SCROLL in SCROLLS
    assert len(ARENAS) == 9 and DEFAULT_ARENA_EFFECT in ARENA_EFFECTS
    assert DEFAULT_MODE in (MODE_PVE, MODE_PVP)
    print("[2/6] 检查按键无冲突 ...")
    # 旧动作键已停用（None），不参与冲突检查；4399 技能键一起查，防止功能重合
    all_keys = [x for x in (list(KEYS_P1.values()) + list(KEYS_P2.values())
                + list(ACTION_KEYS_P1.values()) + list(ACTION_KEYS_P2.values()))
                if x is not None]
    assert len(all_keys) == len(set(all_keys)), "键位存在冲突"
    assert set(ACTION_KEYS_P1.values()).isdisjoint(
        {v for v in KEYS_P1.values() if v is not None}), "P1 技能键与基础键重复"
    assert set(ACTION_KEYS_P2.values()).isdisjoint(
        {v for v in KEYS_P2.values() if v is not None}), "P2 技能键与基础键重复"
    assert NUMPAD_ALIAS_P2[K_KP4] == K_4 and NUMPAD_ALIAS_P2[K_KP3] == K_3
    assert NUMPAD_ALIAS_P1[K_KP4] == K_u and NUMPAD_ALIAS_P1[K_KP1] == K_j
    assert numpad_alias(MODE_PVE) is NUMPAD_ALIAS_P1
    assert numpad_alias(MODE_PVP) is NUMPAD_ALIAS_P2
    assert all(k not in ACTION_BY_KEY for k in NUMPAD_ALIAS_P2 if isinstance(k, int)
               and k in range(K_KP0, K_KP9 + 1)), "小键盘不应与主键冲突"
    # v3.4：输入桥源码必须齐备（坐标全部按 rect 归一化），且 SCREEN_W/H 已代入
    assert "getBoundingClientRect" in _WEB_INPUT_JS
    assert "aimfDrain" in _WEB_INPUT_JS and "aimfInfo" in _WEB_INPUT_JS
    assert "__W__" not in _WEB_INPUT_JS and "__H__" not in _WEB_INPUT_JS
    assert any(b[1] == "输入诊断" for b in build_global_buttons())
    assert callable(getattr(App, "on_touch_move", None))
    print("[3/6] 校验角色数据 ...")
    ids = [c["id"] for c in CHARACTERS]
    assert len(ids) == len(set(ids)), "角色 id 重复"
    print("[4/6] 启动无窗口对局 ...")
    app = App(selftest=True)
    app.start_match()
    keys = pygame.key.get_pressed()
    for frame in range(FPS * 60):
        app.update(1.0 / FPS, keys, set())
        app.draw()
        if app.over:
            break
    print("[5/6] 校验战绩读写 / 触屏布局 ...")
    s = load_stats()
    assert "P1" in s and "P2" in s
    lb, rb, gb, mb = build_touch_layout()
    expect_side = 9 if TOUCH_STYLE == "naruto" else 12
    assert len(SKILL_ROUND) + len(FUNC_BAR) == expect_side
    assert len(lb) == expect_side and len(rb) == expect_side and len(gb) == 2 and len(mb) == 5
    for b in lb + rb + gb + mb:
        assert b[0].right <= SCREEN_W and b[0].bottom <= SCREEN_H, b[1]
    # 左右两组不能互相重叠
    if TOUCH_STYLE == "naruto":
        assert lb[-1][0].right < TOUCH_MID_X1 and rb[0][0].left > TOUCH_MID_X2, "两组圆键压到中间区"
    else:
        assert lb[-1][0].right < 440 and rb[0][0].left > 840
    print("[6/6] 校验 CONFIG 按钮几何确实生效 ...")
    # 这是本次改动唯一需要回归的契约：改 CONFIG 常量，布局必须跟着变，
    # 且所有按钮仍完整落在虚拟画布内（不裁切、不遮挡状态栏）。
    if TOUCH_STYLE == "naruto":
        assert len(lb) == 9 and len(rb) == 9, "摇杆布局应有 9 个键/侧"
        assert all(b[3] and isinstance(b[3][0], tuple) for b in lb + rb), "技能键必须发动作元组"
        assert all(b[0].right <= SCREEN_W and b[0].bottom <= SCREEN_H for b in lb + rb)
        assert skill_short_name("deepseek", "s1") == "白饭", "短名表没生效"
        assert len(skill_help_lines("deepseek")) == 2
        # 默认 PVP 隐藏摇杆；强制显示时两簇会往中间挪，必须真的避开底盘
        lb2 = build_skill_cluster(1, mirror=True, shift=CLUSTER_PVP_STICK_SHIFT)
        assert STICK_P1_CENTER[0] + STICK_RADIUS < lb2[0][0].left, "PVP 显示摇杆时压到技能键"
        assert STICK_P2_CENTER[0] + STICK_RADIUS <= SCREEN_W, "P2 摇杆越界"
        assert STICK_P1_CENTER[0] - STICK_RADIUS >= 0, "P1 摇杆越界"
        # 前 5 个是圆键（正方形外接框），后 3 个是横胶囊
        assert all(b[0].w == b[0].h for b in lb[:5] + rb[:5]), "圆键外接框必须是正方形"
        assert all(b[0].w > b[0].h for b in lb[5:] + rb[5:]), "功能键应是横胶囊"
    else:
        assert lb[0][0].x == TOUCH_P1_X0 and lb[0][0].y == TOUCH_Y0
        assert rb[0][0].x == TOUCH_P2_X0
        assert lb[0][0].w == TOUCH_BTN_W and lb[0][0].h == TOUCH_BTN_H
        assert lb[1][0].x - lb[0][0].x == TOUCH_BTN_W + TOUCH_BTN_GAP
        assert lb[4][0].y - lb[0][0].y == TOUCH_BTN_H + TOUCH_BTN_GAP
    assert gb[0][1] == "操作说明" and gb[0][0].left >= 0 and gb[0][0].top >= 0
    # v3.1 中间区改成 2×2 四个切换键（切模式 / 切操作 / 暂停 / 返回）
    assert len(mb) == 5 and all(b[0].right <= SCREEN_W and b[0].bottom <= SCREEN_H for b in mb)
    assert {b[1] for b in mb} == {"切模式", "切操作", "暂停", "返回", "操作说明"}
    for b in lb + rb + gb + mb:
        r = b[0]
        assert (r.left >= 0 and r.top >= 0 and
                r.right <= SCREEN_W and r.bottom <= SCREEN_H), b[1]
    print("SELFTEST OK  |  角色 %d 位  |  空跑 %d 帧  |  虚拟按键 %d 个  |  "
          "CONFIG 几何生效  |  页面 %s" %
          (len(CHARACTERS), frame + 1, len(lb) + len(rb) + len(gb) + len(mb),
           "menu/select/settings/game/stats"))


def _tt_phys(app, center):
    """虚拟画布坐标 -> 1.5x 缩放后的物理屏幕坐标。"""
    return (app.off[0] + center[0] * app.scale,
            app.off[1] + center[1] * app.scale)


def _tt_center(btns, label):
    """按标签取按钮中心；找不到就取第一个（两种布局都适用）。"""
    for b in btns:
        if b[1] == label:
            return b[0].center
    return btns[0][0].center


def touchtest_setup():
    """搭一个「假装处在 1.5× 全屏缩放」的 App，验证坐标反变换 / 两指命中 / 固定摇杆。"""
    app = App(selftest=True)
    app.disp = object()
    app.scale, app.off = 1.5, (240, 0)
    app.disp_w, app.disp_h = 2400, 1080
    app.out_w, app.out_h = 1920, 1080
    assert app.to_canvas(240 + 16 * 1.5, 566 * 1.5) == (16, 566)
    app.mode = MODE_PVP                  # 触屏测试要两套按键都在
    app.move_ui = MOVE_UI_SHOW            # 同时验证双摇杆与错开后的技能簇
    app.start_match()
    app.scene = "game"                    # 战斗按键只在 game 场景激活
    def hold_center(btns):
        """v3 技能键全是 tap（动作元组），按住不会进 held；
        这里只取按钮中心做命中/多指断言，hold 由摇杆单独测。"""
        return btns[0][0].center, btns[0][1]
    c1, lab1 = hold_center(app.left_btns)
    c2, _lab2 = hold_center(app.right_btns)
    p1 = _tt_phys(app, c1)
    p2 = _tt_phys(app, c2)
    b = app.hit_button(app.to_canvas(*p1))
    assert b is not None and b[1] == lab1, ("坐标反变换失败", p1, b)
    app.just = set()
    app.on_touch_down(1, p1)              # P1 按住第一个键
    app.on_touch_down(2, p2)              # P2 同时按住
    assert len(app.touch_hits) == 2, ("多点触控失败", app.touch_hits)
    # 固定摇杆：底盘不动，手指拖到右边要翻译成「右移」
    if TOUCH_STYLE == "naruto":
        sp = _tt_phys(app, STICK_P1_CENTER)
        app.on_touch_down(9, sp)
        assert 9 in app.stick_hits, "摇杆没接管手指"
        assert STICK_P1_CENTER == (110, 626), "底盘圆心不该被手指改动"
        app._stick_update(9, (STICK_P1_CENTER[0] + STICK_MAX_OFFSET,
                              STICK_P1_CENTER[1]))
        assert app.synth_keys()[KEYS_P1["right"]], "摇杆右移没翻译成方向键"
        app._stick_update(9, (STICK_P1_CENTER[0] - STICK_MAX_OFFSET,
                              STICK_P1_CENTER[1]))
        assert app.synth_keys()[KEYS_P1["left"]], "摇杆左移没翻译成方向键"
        app.on_touch_up(9)
        assert 9 not in app.stick_hits, "抬手后摇杆没释放"
    app._tt_points = (p1, p2)
    return app


def touchtest_battle(app, frames=240):
    """两指按住 + 周期性点普攻 / 变身，空跑指定帧数验证按键合成。"""
    p1, _p2 = app._tt_points
    atk = _tt_phys(app, _tt_center(app.left_btns, "攻"))
    transform = _tt_phys(app, _tt_center(app.left_btns, "scroll"))
    for i in range(frames):
        app.just = set()
        if i % 17 == 0:
            app.on_touch_down(3, atk)      # 普攻 tap
            app.on_touch_up(3)
        if i % 53 == 0:
            app.on_touch_down(4, transform)  # 变身
            app.on_touch_up(4)
        keys = app.synth_keys()
        app.update(1.0 / FPS, keys, app.just)
        app.draw()
    # v3 技能键是 tap 动作，不产生 held；改验动作分发确实消费了秘卷 CD
    assert app.p1 is not None and app.p2 is not None and app.scene == "game"
    assert app.p1.scroll_cd > 0 or app.p2.scroll_cd > 0, "秘卷动作没被消费"


def touchtest_ai(app, frames=40):
    """打开 AI 开关，验证 P2 托管后仍能稳定推进帧。"""
    app.ai_on = True
    app.p2.rage = RAGE_MAX
    for _ in range(frames):
        app.just = set()
        keys = app.synth_keys()
        app.update(1.0 / FPS, keys, app.just)
        app.draw()


def run_touchtest():
    """模拟手机多点触控：缩放坐标 → 按钮命中 → 战斗 → AI 托管。"""
    app = touchtest_setup()
    touchtest_battle(app)
    touchtest_ai(app)
    print("TOUCHTEST OK | 缩放 1.5x | 多点 2 指 | 240 帧战斗 + AI 托管 | 页面", app.scene)




# ==============================================================================
# 附录：内嵌中文字体（base64）
# 放在入口之前：既保证 asyncio.run 启动时变量已定义，又不改动上面 CONFIG 的行号。
# 这样浏览器里不需要 assets/font.ttf 也能显示中文，彻底避开「二进制传不上去」。
# 想换成自己的字体：跑 tools/make_font.py 生成新 font.ttf，再把下面数据替换即可。
# ==============================================================================
_FONT_B64_LINES = (
    "AAEAAAATAQAABAAwR0RFRhWMFzMAA5cwAAAAQEdQT1MAGQAMAAOXcAAAABBHU1VCbIx0hQADl4AAAAAaT1MvMnYwBBgAAAG4AAAAYGNtYXDp4BwFAAAlxAAAHRxjdnQgRJ1NcgAATGgAAAIQZnBnbXPTI7AAAELg",
    "AAAHBWdhc3AABAAHAAOXJAAAAAxnbHlmSHMOzwAAcuwAAx6CaGVhZBaY48oAAAE8AAAANmhoZWEPcQ7IAAABdAAAACRobXR4zq8rUwAAAhgAACOsbG9jYQu7m20AAE54AAAkdG1heHALxQKDAAABmAAAACBuYW1l",
    "lU2vyQADkXAAAAWUcG9zdP8DAGYAA5cEAAAAIHByZXBBvdqCAABJ6AAAAn52aGVhFlYF2gADl5wAAAAkdm10eJqfkFwAA5fAAAASOgABAAAAADMzVCX9GV8PPPUCPwgAAAAAAMY/xrAAAAAA5xie3f/o/hQICAf4",
    "AAAACAAAAAEAAAAAAAEAAAd+/h0AAAgA/+j/8AgIAAEAAAAAAAAAAAAAAAAAAAi6AAEAAAkcAGYADQCIAA4AAgAQAC8AWgAAAh8BYwAEAAEAAwWTAZAABQAIBZoFMwAAAR4FmgUzAAAD0ABmAfIAAAILBgYDCAQC",
    "AgSAAAADCAH0YAAAABAAAAAAV1FZRgBAACD/XgYf/hQAhAd+AeMAEAAAAAAAAARKBbYAAAAgAAIIAAJYCAABUAQAAEgIAAFQBAAASAgAANgIAADYCAAA2AgAANgIAADYCAAA2AgAANgE0P/oBNAAuATQARgE0AC4",
    "BNAAgATQAJAE0ACwCAAAsAgAALAIAAHwCAAAAAgAADAIAAAwCAAEAAgAANgIAAQACAAB4AgABAAIAAGACAAAqAgAAHgIAACgCAAAoAgAAJAIAABYCAAAoAgAAJAIAABwCAAAiAgAAHgIAAB4CAAAUAgAAGAIAADg",
    "CAAA6AgAALAIAACwCAAAeAgAAHgIAACICAAAoAgAAHAIAABYCAAAyAgAAGgIAAB4CAABAAgAAJAIAAB4CAAA2AgAAGgIAABoCAAAcAgAAIAIAABgCAAAgAgAAGgIAABgCAAAWAgAAHAIAABYCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABYCAAAWAgAAFAIAABQCAAASAgAAQgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAaAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABoCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGgIAABQCAAAUAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABwCAAAYAgAAJAIAABoCAAAcAgAAIAIAABo",
    "CAAAWAgAAGgIAACICAAAeAgAAGgIAABgCAAASAgAAGgIAADwCAAAcAgAAGAIAACICAAAaAgAAGgIAABoCAAAaAgAAGgIAAB4CAAAaAgAAHgIAABYCAAAaAgAAGAIAADQCAAA2AgAAIAIAACYCAAAsAgAAMgIAABw",
    "CAAAaAgAAIAIAAB4CAAAYAgAAEgIAABICAAAgAgAAJAIAACICAAAYAgAAGgIAAA4CAAAYAgAAEgIAACICAAAWAgAAHAIAAB4CAAAWAgAAIAIAABoCAAAaAgAAEgIAABwCAAAaAgAAFgIAACACAAAaAgAAFAIAADQ",
    "CAAAeAgAAIgIAACACAAAeAgAAIgIAABoCAABMAgAAJgIAADICAAA0AgAAFgIAAB4CAAAUAgAAFAIAABQCAAAUAgAAGgIAABgCAAAiAgAAGgIAABoCAAAaAgAAFAIAABoCAAAmAgAAKAIAACgCAABSAgAAIgIAAB4",
    "CAAAwAgAAGgIAABoCAAAqAgAAFgIAABoCAAAoAgAAHAIAABQCAAAyAgAAGAIAABQCAAA4AgAAGAIAABwCAAAoAgAAFgIAACgCAAAkAgAAIAIAABYCAAAYAgAAEgIAACwCAAAoAgAAKAIAABoCAAAoAgAAKgIAACo",
    "CAAAmAgAAKgIAACoCAAAqAgAAKAIAABYCAAAcAgAALgIAAC4CAAA4AgAALgIAAC4CAAAuAgAALgIAAC4CAAAwAgAAMAIAABwCAAAQAgAAFgIAABYCAAAcAgAAFgIAABYCAAAUAgAAFgIAABYCAAAgAgAAGgIAABY",
    "CAAAUAgAAFgIAABYCAAAcAgAAHAIAACgCAAAeAgAAIAIAABgCAAASAgAAFgIAABYCAAAYAgAAGgIAABwCAAAUAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABYCAAAaAgAAGgIAAB4CAAAiAgAAFgIAABo",
    "CAAAmAgAAIAIAAB4CAAAmAgAAHAIAACICAAAaAgAAJgIAABgCAAAcAgAAJAIAACQCAAAgAgAAGgIAABwCAAAgAgAAGgIAACYCAAASAgAAIAIAABoCAAAaAgAAGgIAACoCAAAWAgAAGAIAABQCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABoCAAAWAgAAHgIAABoCAABKAgAAGgIAAEQCAAAwAgAAFgIAACQCAAAiAgAAJgIAACICAAAYAgAAJgIAACACAAAcAgAAEgIAABQCAAAUAgAAEgIAABQCAAAUAgAAFAIAABQCAAAYAgAAGAIAAB4",
    "CAAAeAgAAGgIAACQCAAAwAgAAIgIAACICAAAiAgAAIgIAADYCAAA+AgAAIAIAABYCAAAaAgAAFAIAABQCAAAYAgAAGAIAABYCAAAYAgAAFgIAABQCAAAWAgAAFgIAABwCAAAaAgAAGgIAABQCAAASAgAAEgIAABI",
    "CAAASAgAAEgIAABYCAAAUAgAAFAIAABYCAAAUAgAAFAIAABYCAAAUAgAAGAIAABoCAAAWAgAAFgIAABoCAAAUAgAAGgIAABoCAAAeAgAAIgIAABYCAAAaAgAAGgIAABYCAAAaAgAAFgIAABoCAAAoAgAAFAIAABQ",
    "CAAAUAgAAFgIAABYCAAAUAgAAFAIAABYCAAAUAgAAFgIAABYCAAAWAgAAGAIAABYCAAAWAgAAFAIAABgCAAAYAgAAFAIAABQCAAAWAgAAGAIAABQCAAAUAgAAFAIAABYCAAAUAgAAFgIAABgCAAAWAgAAGAIAABg",
    "CAAAYAgAAGAIAABgCAAAYAgAAHgIAABQCAAAYAgAAFAIAABACAAAYAgAAFAIAABgCAAAWAgAAFgIAABACAAAYAgAAGAIAABgCAAAQAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABYCAAAYAgAAFgIAABg",
    "CAAAYAgAAFgIAABYCAAAWAgAAGAIAABgCAAAYAgAAFgIAABYCAAAWAgAAFgIAABgCAAAiAgAANAIAACQCAAAaAgAAFgIAABICAAAaAgAAFAIAABoCAAAeAgAAGgIAABQCAAAUAgAAMAIAABYCAAAcAgAAIAIAACo",
    "CAAAWAgAAIAIAABQCAAAcAgAALAIAAFgCAABEAgAAHgIAACYCAAAuAgAAGAIAABoCAAAkAgAAFAIAABwCAAAkAgAAGgIAABoCAAAkAgAAJAIAACICAAAWAgAAGgIAAB4CAAAaAgAAGgIAAB4CAAAWAgAAGgIAABo",
    "CAAAWAgAAFgIAABYCAAAiAgAAJAIAAAwCAAAkAgAADAIAAAwCAAASAgAAFgIAACACAAAUAgAAEgIAABICAAAMAgAAGgIAABgCAAAYAgAAGAIAAB4CAAASAgAAEgIAABICAAASAgAAEgIAABQCAAASAgAAFAIAABg",
    "CAAAYAgAAEgIAABQCAAAUAgAAEgIAABICAAAOAgAAFAIAABQCAAASAgAAFAIAAA4CAAAaAgAAHAIAABoCAAAaAgAAGgIAABYCAAAgAgAAEgIAABICAAAcAgAAJAIAABoCAABCAgAAIgIAAB4CAAAWAgAAHAIAABg",
    "CAAAWAgAAFgIAABoCAAAaAgAAGgIAABYCAAAaAgAAGgIAABYCAAAYAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABgCAAAYAgAAGAIAABYCAAAWAgAAGAIAABYCAAAWAgAAFgIAABg",
    "CAAAYAgAAFgIAABYCAAAWAgAAFgIAABoCAAASAgAAGgIAABICAAAcAgAAFAIAABgCAAAaAgAAGgIAABYCAAAaAgAAGgIAABYCAAAaAgAAGgIAABoCAAASAgAAEgIAABYCAAAUAgAAFgIAABYCAAAWAgAAFgIAABY",
    "CAAAWAgAAHAIAABoCAAAaAgAAGgIAABoCAAAaAgAAGAIAACACAAAWAgAAQAIAAEQCAAA0AgAAHgIAABgCAAA6AgAAJgIAABACAAASAgAAEgIAABACAAAaAgAARAIAACoCAAAaAgAAGgIAABoCAAAaAgAAFAIAABo",
    "CAAAaAgAAVAIAACQCAAAMAgAAJAIAABoCAAAaAgAAFAIAAB4CAAAoAgAAKAIAABoCAAAoAgAAIgIAACICAAAiAgAAGAIAABYCAAAWAgAAFAIAABQCAAASAgAADgIAABQCAAASAgAAFAIAAA4CAAAQAgAAEgIAABo",
    "CAAAaAgAAGgIAABICAAAWAgAAJAIAABICAAAOAgAADgIAABYCAAAWAgAADgIAAA4CAAAWAgAAEgIAABICAAAmAgAAGAIAABwCAAAaAgAAIAIAABoCAAAgAgAAGgIAAB4CAAAaAgAAGgIAABQCAAAYAgAAGgIAABo",
    "CAAAYAgAAGgIAABoCAAAaAgAAHAIAABoCAAAaAgAAFAIAABwCAAAUAgAAFgIAABYCAAAaAgAAGgIAABwCAAAcAgAAFgIAABwCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABYCAAAyAgAAHgIAAB4CAAAaAgAAFgIAABQCAAAUAgAAGAIAABwCAAASAgAAGgIAABgCAAAUAgAAFAIAABQ",
    "CAAAkAgAAFgIAABQCAAAiAgAAFAIAABoCAAAUAgAAEAIAABYCAABIAgAAJAIAABgCAAAgAgAAGgIAAB4CAAAeAgAAGgIAAB4CAAAgAgAAGgIAABoCAAAgAgAAHgIAAB4CAAAaAgAAGgIAACACAAAaAgAAGgIAAB4",
    "CAAAgAgAAIAIAABQCAAAWAgAAFAIAABgCAAAWAgAAEgIAABQCAAAYAgAAEgIAABICAAAaAgAAFAIAABACAAASAgAAEgIAAB4CAAAWAgAAGgIAACYCAAAaAgAAGgIAABICAAAgAgAAGgIAABACAAAYAgAAGAIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAcAgAAHAIAACQCAAAaAgAAGAIAABw",
    "CAAAaAgAAHAIAABgCAAAgAgAAGAIAABgCAAAYAgAAEgIAABoCAAASAgAAEgIAABICAAAcAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABgCAAASAgAAEgIAABoCAAAaAgAAGgIAABoCAAAcAgAAGgIAABo",
    "CAAAWAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABg",
    "CAAAYAgAAGgIAAB4CAAAKAgAAGgIAABoCAAAQAgAAIgIAABwCAAAYAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABICAAAUAgAAFAIAABwCAAA0AgAANAIAADQCAAA0AgAANAIAADQ",
    "CAAAqAgAAKgIAACoCAAAoAgAAKgIAACgCAAAoAgAAKAIAACoCAAAiAgAAKAIAACICAAAoAgAAKAIAABgCAAAeAgAAIgIAABgCAAAYAgAAGgIAABoCAAAYAgAAGgIAABoCAAAaAgAAGgIAACACAAAaAgAAGgIAABY",
    "CAAAUAgAAGAIAABoCAAAcAgAAFAIAABQCAAAYAgAAFgIAABgCAAAWAgAAJAIAABoCAAASAgAAEgIAABICAAAUAgAAGgIAABoCAAA2AgAAIAIAABoCAAAgAgAAIAIAACACAAAcAgAAGAIAABQCAAAWAgAAGAIAABg",
    "CAAA6AgAAFAIAABgCAADgAgAAugIAAGgCAACUAgAAPAIAAG4CAADoAgAAxAIAAIgCAAB0AgAAjAIAAFQCAABKAgAAWAIAAIQCAACMAgAApgIAAI4CAACMAgAAeAIAAJICAACMAgAAigIAAI4CAACMAgAAagIAAGI",
    "CAACMAgAAjAIAAIwCAACOAgAAPgIAAFoCAACIAgAAcgIAAHoCAACMAgAAjAIAAGgCAAB0AgAAigIAAIACAACIAgAAoAIAAFQCAABoAgAAWAIAAJICAABYAgAAhAIAAIACAABmAgAAbAIAAFoCAAAiAgAAYAIAAGQ",
    "CAAB2AgAAzgIAAIQCAACkAgAAggIAAAACAADEAgAAigIAAIwCAACUAgAAdgIAAIICAACEAgAAdgIAAIYCAACSAgAAhAIAAJoCAACUAgAARAIAAIYCAAB+AgAAjAIAAHYCAACmAgAAmgIAAIwCAACGAgAAcAIAAEY",
    "CAAB0AgAAcAIAAJQCAACaAgAA7gIAAIoCAACMAgAAQgIAABoCAAAYAgAAGAIAAB4CAAD6AgAAagIAAKQCAACeAgAAigIAAKACAACYAgAAtAIAAJICAACcAgAAkgIAAJoCAACiAgAAngIAAKYCAACWAgAApAIAALY",
    "CAACcAgAAIAIAAPwCAAD2AgAAbAIAACICAAEEAgAAGgIAAOoCAAAoAgAAGgIAABgCAACEAgAAFAIAAGYCAAAaAgAAUgIAACICAACcAgAALAIAACICAADKAgAAGgIAAB4CAAAaAgAAHgIAAMACAAAkAgAAFAIAAB4",
    "CAADsAgAAGgIAABoCAABAAgAAGgIAABgCAAAUAgAAQAIAAEACAAA8AgAAHAIAACwCAAAUAgAAQAIAABwCAAAaAgAAIAIAAJICAAA6AgAAKAIAABoCAAAYAgAATgIAAEoCAABkAgAAXgIAAMICAAAoAgAAHgIAABo",
    "CAAAcAgAARAIAANICAAAgAgAAHgIAAB4CAACWAgAAqAIAANoCAABsAgAAGgIAACACAAAaAgAAFAIAAGYCAAAiAgAANAIAAIgCAAB+AgAAsAIAACICAABOAgAA1gIAAFwCAABiAgAAjgIAAH4CAACAAgAAhAIAABg",
    "CAAAWAgAAGgIAAHQCAAB4AgAAhAIAAFYCAABwAgAATAIAABwCAAAgAgAAJAIAAFQCAAAaAgAAIgIAAGACAAAaAgAAIgIAAEoCAAAiAgAAGAIAACYCAABgAgAAXgIAAJACAACiAgAAZAIAAGwCAABmAgAAggIAADI",
    "CAAAiAgAAYAIAAKgCAAAiAgAAqgIAAI4CAAAWAgAAHAIAALgCAAAiAgAAwAIAAN4CAADeAgAAxAIAANACAADaAgABQAIAABgCAAC8AgAAhgIAAKwCAAAOAgAArgIAANICAACgAgAAGgIAABoCAAC2AgAAGgIAABg",
    "CAAAWAgAAGAIAABoCAAAcAgAAqAIAAKoCAADIAgAAFAIAACICAADUAgAAGAIAAKACAACqAgAAfgIAAKoCAAC6AgAAqAIAAWACAAAWAgAAzAIAALACAAAoAgAAEAIAAMYCAAAiAgABEgIAAKoCAACWAgAAGgIAABY",
    "CAACyAgAAFgIAABYCAAAaAgAAmAIAAHYCAABYAgAAvAIAAKQCAAAeAgAAEgIAABICAABMAgAAhAIAACACAAAcAgAAIAIAABYCAACqAgAAkgIAANACAAC+AgAAmgIAALYCAAAqAgAAdgIAALoCAAAmAgAAGgIAARI",
    "CAACiAgAAIAIAAQoCAAAgAgAAcAIAAL4CAADAAgAArAIAALACAAC+AgAAGgIAABwCAABQAgAAVgIAABwCAAA0AgAAFgIAALYCAADoAgAAzgIAABYCAADIAgAA3AIAACACAAEeAgAA2AIAAJgCAACiAgAAkAIAAJY",
    "CAACuAgAAqgIAAP4CAAAoAgAAKAIAACgCAAAqAgAAsgIAACoCAAAoAgAAMAIAABoCAADSAgAAIAIAABoCAABCAgAAyAIAABICAADaAgAAFgIAABQCAAEmAgAAngIAAKoCAAC+AgAA1gIAABgCAACiAgAArgIAAIQ",
    "CAAAqAgAAvAIAAJQCAADAAgAAggIAANYCAAC4AgAAugIAALICAACsAgAA1AIAAM4CAAC6AgAAvgIAABoCAADkAgAAqgIAALACAADAAgAAwgIAAKYCAAC8AgAAsgIAAQACAACoAgAAIAIAABoCAAAkAgAAHgIAAOg",
    "CAAAkAgAAEgIAAMICAAAYAgAAigIAAIQCAABKAgAA6gIAAI4CAACQAgAAmAIAALgCAAAaAgAAggIAAVoCAAAKAgAAHgIAAKgCAACSAgAAtAIAAIQCAAASAgAApAIAAJ4CAACyAgAAvgIAAIACAAC8AgAAjAIAAOQ",
    "CAAAuAgAA1gIAAKYCAACUAgAAqAIAAB4CAAAqAgAAqAIAAJQCAAC+AgAAxgIAAKQCAADAAgAAHAIAAK4CAADYAgAAbgIAAKoCAAEMAgAA0gIAALQCAAAYAgAAuAIAALwCAACUAgAAEgIAAKoCAACCAgAAhgIAABo",
    "CAACSAgAAtgIAAIwCAADiAgAAxAIAALQCAACOAgAAHgIAAA4CAAAaAgAAGAIAACgCAACeAgAA2gIAAMACAADqAgAAcgIAAIwCAACeAgAAnAIAAQQCAAASAgAAnAIAAB4CAACuAgAAsAIAAKwCAAAkAgAAegIAAJA",
    "CAAC0AgAAogIAABICAADkAgAAIAIAACYCAADqAgAArAIAAPwCAAD0AgAAGgIAAQYCAAAgAgAAIAIAAOQCAADQAgAAmgIAAJoCAADiAgAAuAIAAC4CAACaAgAAGgIAANwCAAAcAgAAvgIAABACAAC+AgAAzgIAAOA",
    "CAADsAgAAQgIAACwCAAAcAgAAwAIAAI4CAAAcAgAANAIAANICAAC8AgAAGgIAAMgCAAASAgAA/gIAACQCAADIAgAAUAIAAHoCAACWAgAAJAIAACACAAE0AgAAFAIAALgCAAASAgAAGgIAAB4CAAAYAgAAxAIAAMA",
    "CAADmAgAAFgIAALgCAADCAgABJgIAALQCAAAYAgAAggIAABICAADkAgAAGAIAABgCAAAWAgAAKAIAALYCAADKAgAAqAIAAM4CAACEAgAAZAIAABoCAADWAgAAXAIAANICAAAYAgAAqAIAAMICAAAaAgAAEgIAABo",
    "CAAAeAgAAFgIAAL4CAACuAgAAsAIAANICAAEwAgAAuAIAAEYCAAAUAgAAfgIAABoCAAAaAgAAzAIAABYCAAAWAgAA6gIAACgCAAAcAgAAugIAABgCAAAqAgAApAIAAOgCAACEAgABAAIAAK4CAAAoAgAAHgIAABI",
    "CAAAcAgAAVAIAAPgCAAAUAgAAHAIAAIoCAAAeAgABQgIAACACAAAYAgAAtAIAARoCAACIAgAA2gIAAM4CAAC4AgAAhgIAANgCAACsAgAA7AIAAGACAAAUAgAAWgIAABYCAAB2AgAAGAIAAMACAAAoAgAAMAIAAMY",
    "CAAAaAgAA+gIAAO4CAAD0AgAAFgIAALgCAAAWAgAAKgIAABoCAAAcAgAAGAIAAPQCAAEIAgAAGgIAALYCAADcAgAAygIAAKICAADCAgAAxAIAABQCAAAUAgAA5AIAABICAADUAgAAEgIAAKwCAAA8AgAAnAIAAKo",
    "CAADEAgAAKgIAAMwCAACuAgAAJgIAACACAAAgAgAAugIAAJgCAAAaAgAAdAIAAHACAADGAgAAugIAAOwCAAAWAgAAuAIAABoCAAAgAgAAHAIAAFYCAAAqAgAA8AIAACACAAAgAgAAGgIAANoCAACoAgAA5AIAALY",
    "CAAAmAgAAxAIAALgCAADqAgAA2gIAAQwCAAAgAgAAGAIAABgCAADKAgAAogIAAMICAACcAgAAcAIAAI4CAAC2AgAA/AIAAN4CAADgAgAAagIAACICAADoAgAAGgIAAB4CAAAgAgAAuAIAAJACAACUAgAAFgIAAOo",
    "CAAAgAgAAqAIAAOQCAAEAAgAAHAIAACICAAAcAgAAxgIAAKwCAAAWAgAAJgIAAFICAAAaAgAAQAIAABwCAABkAgAAbAIAAHYCAAAUAgAAsAIAACICAAAaAgAAGgIAALoCAAAsAgAAygIAABoCAAA0AgAAqgIAACY",
    "CAAB6AgAAFgIAAMgCAADMAgAANgIAACwCAAAWAgABMgIAALQCAAASAgAAEgIAAJQCAADGAgAAGgIAAKoCAACsAgABQAIAABYCAADYAgAAGgIAABICAACoAgAAegIAABoCAAAaAgAAtgIAALYCAAAaAgAAyAIAABg",
    "CAAAWAgAAHAIAAMwCAAAaAgAAFAIAAB4CAAASAgAA4gIAABQCAAC0AgAAmAIAABQCAAAWAgAAIAIAAJoCAAAQAgAAEAIAABQCAAAaAgAAZAIAASQCAAEaAgAAGgIAABwCAACqAgAAfgIAAIoCAACYAgAAvAIAADw",
    "CAACSAgABCgIAAOwCAADuAgAAFAIAANwCAAA8AgAAFAIAABQCAAAUAgAAFAIAABYCAAAcAgAA8gIAABoCAAAaAgAAGgIAABoCAABuAgAARAIAAJACAAAaAgAAxgIAAKgCAAAeAgAAIgIAAFYCAAE0AgAAhAIAALA",
    "CAACQAgAAHAIAACoCAAAqAgAAwAIAANoCAADSAgAAFAIAAMACAADIAgAAGgIAABICAAAcAgAAhgIAABICAAAwAgAAIgIAASoCAAAgAgAAHAIAAJ4CAACiAgAAEgIAALgCAAAUAgAAmAIAAK4CAAAaAgAAGgIAAPQ",
    "CAAAkAgAAGAIAAKgCAAC2AgAAKgIAABICAAAUAgAAEgIAABICAAEOAgAAEgIAABYCAAAWAgAAGgIAABICAAAmAgAAFgIAABYCAAAUAgAA9gIAASgCAADyAgAA3AIAABQCAADOAgAArAIAAMQCAACqAgAAkAIAAMA",
    "CAACgAgABiAIAACICAACaAgAAngIAABwCAACAAgAAzAIAAKICAADkAgABNgIAACYCAAAaAgAAJgIAAI4CAAAUAgAApAIAAJ4CAAAcAgAAHAIAABQCAADgAgAAFAIAABoCAADmAgAAFAIAAIwCAADqAgAAGgIAANo",
    "CAAEMAgABXAIAANYCAADMAgAAuAIAAOYCAACaAgAAogIAAQACAAAUAgAAFgIAAPgCAAEwAgAAFAIAARACAADIAgAAFgIAAMoCAAAWAgAAugIAABoCAAAaAgAAGgIAABgCAAAWAgAAoAIAANACAAEgAgABIAIAADw",
    "CAAAiAgAAZAIAACoCAAAcAgAAFAIAABoCAAEKAgAA7AIAAMACAAAYAgAAHAIAABoCAAAUAgAAFAIAAIoCAACuAgAAwgIAALACAAC8AgAAFgIAABYCAACcAgAALgIAACACAACQAgAAFAIAALYCAAC4AgAAFAIAABo",
    "CAADmAgABVgIAABgCAAAqAgAAnAIAACYCAAAYAgAALgIAABoCAACiAgAAGgIAABgCAAAeAgAA8AIAABYCAACmAgAAtgIAAJoCAAAaAgAAGgIAACgCAADIAgAAzAIAAIICAACkAgAAGgIAACwCAAEGAgAAFgIAABw",
    "CAAAmAgAADgIAAHQCAAAUAgAAFAIAAMQCAAEeAgABQgIAAMICAAAUAgAAGgIAAOYCAAAaAgAAfAIAAI4CAAAWAgABAAIAABQCAADkAgAAwgIAABICAAAaAgAAGgIAAFYCAAFiAgAArAIAAIACAAFaAgAAFAIAABY",
    "CAAASAgAAsgIAABgCAAESAgAAbAIAAIwCAAFsAgAAFgIAAEYCAAAYAgAAGgIAAB4CAAEAAgAAiAIAABACAADYAgAAEgIAAKACAAAMAgABOAIAABoCAAAUAgAAsgIAAB4CAAB0AgAAFgIAALoCAACqAgAAtgIAABI",
    "CAADaAgAAGgIAACACAAAgAgAAGgIAARYCAAAgAgAAJgIAAMICAAAiAgAAJAIAAFYCAACYAgAAFAIAABYCAAAUAgAAGgIAANwCAAAaAgAA0gIAAUQCAAAkAgAA2gIAAOwCAAAYAgAAFgIAABYCAAAeAgAAMAIAACI",
    "CAAAaAgAAGgIAABoCAAAaAgAAFAIAABQCAAAUAgAAFAIAABoCAAAaAgAAIAIAACQCAAAoAgAAtgIAAMYCAACMAgAAGAIAAJYCAAAiAgAAIgIAALoCAACmAgAAEgIAAMQCAAAWAgAAjAIAAA4BM0AAAHnAR0ALQAA",
    "AD0B8AEnASkAhQCYAbgBHQHPANMAkwDhAJ4AgwA9AKwAmgCPAJwAmgHnAZoAmACYAJgAqAAfACEAhwCBAIcA2QD0AHUAhwDhAIkA0wDpAHEAhwBUALAAVAC6AI0AZgB9ACEAAgA1ACEAZgGcANMBIf/wAaIAhwCe",
    "AKwAiQCFAJwAZgCgAMUAhwDXALwAXACgAHMAngCJAQgAywCLAKAAUv/8AGAAUgC2AOECGwDjAJgBXAHnAL7/+gBOAEYAAAACAAAAAwAAABQAAwABAAAAFAAEHQgAAAc+BAAACQM+ACMAXQB+ALIAtwDXIBQgJiGT",
    "Ih4kZiWIJbIltiW8JcAlxiXPJgYnEzACMA0wEU4ATgdOC04OThROHE4iTiVOKk4tTjJONE47TkVOSU5LTk5OWU5dTmBOZk5xToZOiU6MTo5Okk6UTptOpE6nTq5Ouk7ATsZOzk7TTtZO5U7sTvdO+079TxFPGE8a",
    "TyBPJE84TzxPRk9PT1NPVU9ZT1xPYE9/T4tPm0+dT6dPv0/dT+FP7lANUBJQGVA8UD5QR1BPUFpQXFB/UKhQrFC7UM9Q9VFBUUNRSVFNUVxRZVFoUW1RcVFzUXhRfFGFUY1RmVGzUbVRt1G7UcBRxlHPUdFR4FHt",
    "UfZR+1H9UgBSA1IHUhJSF1IZUhtSHVIgUiRSK1IwUjdSO1JNUlRSalKIUptSoVKpUr9TBVMWUzpTQVNDU0dTSlNVU1dTYVNwU3RTd1OLU5pTn1O7U8JTyFPKU81T0VPYU+BT5FPsU/BT81P3VARUCFQOVBFUJlQs",
    "VC9UOFRIVFhUaFR9VIxUwVTIVM1U5VTqVSRVL1VGVYJVilXcVjRWaFbKVttW3lbgVuJW9Fb6Vv5XBlcIVyNXKFcwVzpXQFdHV1FXV1eCV4tX31f6WINYnlkEWQdZDVkWWRpZHFkfWSdZKlkuWTFZNFlRWVdZZVlz",
    "WXZZfVnLWdBZ/1oYWsxbUFtYW2Zbg1uJW4xbmFuaW55bolukW6pbs1u2W7lbvVv5W/xcBFwPXBFcFlwYXB1cMVw6XD5cQFxCXEVcT1xeXSldTF3mXehd7l3yXgNeJ144XkVeVV5zXnZej16VXpdepl6tXvZe+l8A",
    "XwJfD18VXyBfJ186X1NfVV9iX3Ffe1+AX4Vfi1+XX6Ffql+uX71fw1/FX9df61/9YAFgDmASYB1gJ2A7YFJgYmBvYMVg72DzYQhhD2EfYWJiEmIWYhhiKmI0YjdiQGJHYktiTWJTYlhiW2JjYmdiaWJrYnBigGKE",
    "Yopik2KVYphim2KiYqVirGKxYrVixmLJYs1i0mLWYtti32LpYuxi8WL/YwJjB2MJYxFjIWMkYyhjKmNfY2JjbmN3Y4ljkmOlY6hjt2PQY9Jj9GQcZB5kLWRHZEpkeGSeZKRkrWTFZM5lEmUvZTZlOWU7ZT5lSGVM",
    "ZU9lY2VwZXRlh2WLZZdlnGWnZallrWWwZblly2XgZeJl5WXnZell9mYOZhNmIGYvZj5mWmZvZoJml2a0ZvRnAGcJZw1nHWcfZyxnL2c1ZzpnQGdDZ0ZnUGdfZ2FnZWd/Z4FnhGecZ7Zn0GfTZ+VoB2gPaCFoOWg8",
    "aEZoSGhMaGNoZWh2aK9owGktacxp/WohaipqWWshaz5rZWt7a7VrzWvPa9Jr1GwUbDRsOGxCbEdsSWyJbKFsv2zJbNVs4mzobPxtO20+bUFtS21PbW5td22Ibaht4W3xbfduBW4QbiFuMm44bpBu0W7ebuFvAm8P",
    "bxRvwHBrcG9wdXCucLlw33DtcTZxZ3IGcipyMXJIckxyWXJpcnlyr3K2ctBy7HL4cxxzK3OHc6lzsHQDdAZ093UfdSh1MnU1dTt1THVZdWV1l3WrddV2e3Z9doR2xnbKds920nbWdth27nb0dvl2/ncBdwt3IHc8",
    "d0B3W3dhd6x3s3fld+l37XgBeBR4NHg4eEB4bHhueJd4sHi+eTp5PHk+eV55gXm7ecF5zXnSedh58Hn7egt6M3o/enp6f3qBepd6nXrLetZ62Xrgeu97G3smeyx7SXtUe1Z7fnuAe5d7oXute8d8B3xzfHt8knzK",
    "fPt9IH0ifSd9K30vfqJ+p36vfrl+v37Efsh+z37TftV+2X7dft9+537pfu1/AH8TfxZ/GH8pfzp/UX9pf25/jn/7gAGAA4AFgAyAF4AzgEyAVIBagKWAzIDcgPaA/YERgRqBcIF/gcKB6oH0ggyCcoKCgrGCz4Ll",
    "gwODNoNQg7eD3IQlhD2EuITEhN2Fz4ZahsuHg4f5iECIRYhMiGGIZYhoiHCIjYiriMKIxYjZiPiJf4mBiYaJwonEicaJyYnSieOJ5ooAi6GLpIupi66LsIuyi7iLuou/i8GLyovNi9GL1Yvdi+WL7Yvvi/SL+4wB",
    "jAOMYYxqjR+NI40mjSiNL400jTmNRI1LjVSNVo1wjXeNhY2KjbONw43Rjd2N343vjfOOKY6rjrKOuo9oj2yPbo97j32PkY+Tj6iPuY/Fj8eP0Y/Uj9mP3I/fj/eP/ZACkAmQEJASkBqQIJA7kE2QU5BukH+Qo5Do",
    "kP2RTZGSkcqRzZHPkdGUiJSflK6UwZT2lPqVAZULlRmVLpVclX+V6JXqle6V9JYBlh+WMpY2lkWWTZZQlmSWaZaQlpSWxpb2lwCXB5cylziXUpdZl16XYJdil/OYdph7mH+YhJiYmJ2YzpjYmN+ZbZlwmYiZj5mW",
    "mZmabJpxmnuaf5qMmqia2Jx8nLieIZ7RntifIJ9Qn5n/Xv//AAAAIAAlAF8AsgC3ANcgFCAmIZAiHiRgJYglsiW2JbwlwCXGJc8mBScTMAAwCjAQTgBOB04JTg1OE04cTiJOJE4qTi1OMk40TjpORU5ITktOTk5Z",
    "Tl1OX05mTnFOhk6JTotOjk6STpROm06kTqdOrk66Tr9OxU7NTtNO1k7jTuxO9k77Tv1PEU8YTxpPIE8kTzhPPE9GT01PU09VT1lPXE9gT39Pi0+bT51Pp0+/T91P4U/uUA1QElAZUDxQPlBHUE9QWlBcUH9QqFCs",
    "ULtQz1D1UUFRQ1FIUU1RXFFlUWhRbVFxUXNRdlF8UYVRjFGZUbJRtVG3UbtRwFHGUc9R0VHgUe1R9lH6Uf1SAFIDUgZSElIXUhlSG1IdUiBSJFIrUjBSNlI6Uk1SVFJpUohSm1KeUqhSv1MFUxZTOlNBU0NTR1NK",
    "U1VTV1NgU3BTc1N3U4tTmlOfU7tTwlPIU8pTzFPRU9ZT4FPjU+pT71PzU/dUA1QIVAxUEVQmVCtUL1Q4VEhUWFRoVH1UjFTBVMhUzVTlVOpVJFUvVUZVglWKVdxWNFZoVspW21beVuBW4lb0VvpW/lcGVwhXI1co",
    "VzBXOldAV0dXT1dXV4JXi1ffV/pYg1ieWQRZB1kNWRZZGlkcWR9ZJ1kqWS5ZMVk0WVFZV1llWXNZdll9WctZ0Fn/WhhazFtQW1dbZluDW4lbjFuYW5pbnlugW6RbqluzW7ZbuVu9W/hb/FwEXA9cEVwWXBhcHVwx",
    "XDpcPlxAXEJcRVxPXF5dKV1MXeVd6F3uXfFeA14mXjheRV5VXnJedl6PXpNel16mXq1e9l76XwBfAl8PXxVfIF8nXzlfUl9VX2JfcV97X4BfhF+LX5dfoV+qX65fvV/DX8Vf11/rX/1gAWAOYBJgHWAnYDtgUmBi",
    "YG9gxWDvYPNhCGEPYR9hYmIPYhZiGGIqYjRiN2I/YkdiS2JNYlNiWGJbYmNiZ2JpYmticGJ+YoRiimKTYpVimGKbYqJipGKsYrFitWLFYslizWLSYtZi22LfYuli7GLxYv1jAWMHYwljEWMhYyRjKGMqY19jYmNu",
    "Y3djiWOSY6Vjp2O3Y89j0mP0ZBxkHmQtZEZkSmR4ZJ5kpGStZMVkzWUSZS9lNmU5ZTtlPmVIZUxlT2VjZXBldGWHZYtll2WcZadlqWWtZbBluWXLZeBl4mXlZedl6WX2Zg5mE2YfZi9mPmZaZm5mgmaWZrRm9Gb/",
    "ZwhnDWcdZx9nKmcvZzVnOmdAZ0NnRmdQZ19nYWdlZ39ngWeEZ5xntmfQZ9Nn5WgHaA9oIWg3aDxoRmhIaExoY2hlaHZor2jAaS1pzGn9aiFqKmpZayBrPmtia3trtWvNa89r0mvUbBRsNGw4bEJsR2xJbIlsoWy/",
    "bMls1WzhbOhs/G07bT5tQW1LbU9tbm13bYhtqG3hbfFt924FbhBuIW4ybjhukG7Rbt5u4W8Cbw9vFG/AcGtwb3B1cK5wuXDfcO1xNnFncgZyKnIxckdyTHJZcmlyeXKvcrZy0HLscvhzG3Mrc4dzqXOvdAN0BnT3",
    "dR91KHUxdTV1O3VMdVl1ZXWXdat11XZ7dn12hHbGdsp2z3bRdtZ22HbudvR2+Hb+dwF3C3cfdzx3QHdbd2F3rHezd+V36XfteAF4FHg0eDh4QHhseG54l3iweL55Onk8eT55XnmBebt5wXnNedJ52Hnveft6C3oz",
    "ej96enp/eoF6l3qdest61nrZeuB673sbeyZ7LHtJe1R7Vnt+e4B7l3uhe617x3wHfHN8e3ySfMp8+30gfSJ9J30rfS9+on6mfq9+t36/fsN+yH7PftN+1X7Yft1+337nful+7X8AfxN/Fn8Yfyl/On9Rf2l/bn+O",
    "f/uAAYADgAWADIAXgDOATIBUgFqApYDMgNyA9oD9gRGBGoFwgX+BwoHqgfOCDIJygoKCsYLPguWDA4M2g1CDt4PchCWEPYS4hMSE3YXPhlqGy4eDh/mIQIhFiEyIYYhliGiIcIiNiKuIwYjFiNmI+Il/iYGJhonB",
    "icSJxonIidKJ44nmigCLoYuki6mLrYuwi7KLuIu6i76LwYvKi82L0YvVi92L5Yvti++L9Iv7jAGMA4xhjGqNH40jjSWNKI0vjTSNOY1EjUuNVI1WjXCNd42FjYqNs43DjdGN3Y3fje+N844pjquOso66j2iPbI9u",
    "j3uPfY+Rj5OPqI+5j8WPx4/Qj9SP2I/bj96P94/9kACQCZAPkBKQGpAfkDuQTZBTkG6Qf5CjkOiQ/ZFNkZKRypHMkc+R0ZSIlJ+UrpTBlPaU+pUAlQuVGZUulVyVf5XoleqV7ZX0lgGWH5YyljSWRJZNllCWZJZp",
    "lo+WlJbGlvaXAJcHlzKXOJdSl1mXXpdgl2KX85h1mHmYfpiEmJeYnJjOmNiY3pltmXCZiJmPmZaZmZpsmnGae5p/moyaqJrYnHycuJ4hntGe2J8gn1Cfmf8B//8ImQiYCJcIZAhgCEHpBej03nHm/dul2oTaW9pY",
    "2lPaUNpL2kPaDtkC0BbQD9ANsh+yGbIYsheyE7IMsgeyBrICsgCx/LH7sfax7bHrseqx6LHesdux2rHVscuxt7G1sbSxs7Gwsa+xqbGhsZ+xmbGOsYqxhrGAsXyxerFusWixX7FcsVuxSLFCsUGxPLE5sSaxI7Ea",
    "sRSxEbEQsQ2xC7EIsOqw37DQsM+wxrCvsJKwj7CDsGWwYbBbsDmwOLAwsCmwH7Aer/yv1K/Rr8OvsK+Lr0CvP687rzivKq8iryCvHK8ZrxivFq8TrwuvBa76ruKu4a7grt2u2a7Ursyuy669rrGuqa6mrqWuo66h",
    "rp+ula6RrpCuj66Oroyuia6Drn+ueq54rmeuYa5NrjCuHq4crhauAa28raytia2DrYKtf619rXOtcq1qrVytWq1YrUatOK00rRmtE60OrQ2tDK0JrQWs/qz8rPes9azzrPCs5azirN+s3azJrMWsw6y7rKysnayO",
    "rHqsbKw4rDKsLqwXrBOr2qvQq7qrf6t4qyeq0KqdqjyqLaorqiqqKaoYqhOqEKoJqgip7qnqqeOp2qnVqc+pyKnDqZmpkak+qSSonKiCqB2oG6gWqA6oC6gKqAioAaf/p/yn+qf4p9yn16fKp72nu6e1p2inZKc2",
    "px6ma6XopeKl1aW5pbSlsqWnpaalo6WipaGlnKWUpZKlkKWNpVOlUaVKpUClP6U7pTqlNqUjpRulGKUXpRalFKULpP2kM6QRo3mjeKNzo3GjYaM/oy+jI6MUovii9qLfotyi26LNoseigKJ9oniid6JromaiXKJW",
    "okWiLqItoiGiE6IKogaiA6H+ofOh6qHiod+h0aHMocuhuqGnoZahk6GHoYSheqFxoV6hSKE5oS2g2KCvoKygmKCSoIOgQZ+Vn5KfkZ+An3efdZ9un2ifZZ9kn1+fW59Zn1KfT59On02fSZ88nzmfNJ8snyufKZ8n",
    "nyGfIJ8anxafE58EnwKe/577nvie9J7xnuie5p7intee1p7SntGeyp67nrmetp61noGef550nmyeW55TnkGeQJ4ynhueGp35ndKd0Z3DnaudqZ18nVedUp1KnTOdLJzpnM2cx5zFnMScwpy5nLactJyhnJWckpyA",
    "nH2ccpxunGScY5xgnF6cVpxFnDGcMJwunC2cLJwgnAmcBZv6m+yb3pvDm7CbnpuLm2+bMJsmmx+bHJsNmwybApsAmvua95rymvCa7prlmtea1prTmrqauZq3mqCah5pummyaW5o6mjOaIpoNmguaApoBmf6Z6Jnn",
    "mdeZn5mPmSOYhZhVmDKYKpf8lzaXGpb3luKWqZaSlpGWj5aOlk+WMJYtliSWIJYfleCVyZWslaOVmJWNlYiVdZU3lTWVM5UqlSeVCZUBlPGU0pSalIuUhpR5lG+UX5RPlEqT85Ozk6eTpZOFk3mTdZLKkiCSHZIY",
    "keCR1pGxkaSRXJEskI6Qa5BlkFCQTZBBkDKQI4/uj+iPz4+0j6mPh495jx6O/Y74jqaOpI20jY2NhY19jXuNdo1mjVqNT40fjQyM44w+jD2MN4v2i/OL74vui+uL6ovVi9CLzYvJi8eLvouri5CLjYtzi26LJIse",
    "iu2K6ornitSKwoqjiqCKmYpuim2KRYotiiCJpYmkiaOJhIliiSmJJIkZiRWJEIj6iPCI4Yi6iK+IdYhxiHCIW4hWiCmIH4gdiBeICYfeh9SHz4ezh6mHqIeBh4CHaodhh1aHPYb+hpOGjIZ2hj+GD4XrheqF5oXj",
    "heCEboRrhGSEXYRYhFWEUoRMhEmESIRGhEOEQoQ7hDqEN4QlhBOEEYQQhACD8IPag8ODv4OggzSDL4Mugy2DJ4MdgwKC6oLjgt6ClIJugl+CRoJAgi2CJYHQgcKBgIFZgVGBOoDVgMaAmIB7gGaASYAXf/5/mH90",
    "fyx/FX6bfpB+eH2HfP18jXvWe2F7G3sXexF6/Xr6evh68XrVerh6o3qheo56cHnqeel55Xmreap5qXmoeaB5kHmOeXV31XfTd893zHfLd8p3xXfEd8F3wHe4d7Z3s3ewd6l3onebd5p3lneQd4t3inctdyV2cXZu",
    "dm12bHZmdmJ2XnZUdk52RnZFdix2JnYZdhV17XXeddF1xnXFdbZ1s3V+dP1093TwdEN0QHQ/dDN0MnQfdB50CnP7c/Bz73Pnc+Vz4nPhc+BzyXPEc8JzvHO3c7Zzr3Orc5FzgHN7c2FzUXMucupy1nKHckNyDHIL",
    "cgpyCW9Tbz1vL28dbulu5m7hbthuy263bopuaG4Abf9t/W34bextz229bbxtr22obaZtk22PbWptZ202bQds/mz4bM5syWywbKpspmylbKRsFGuTa5Frj2uLa3lrdmtGaz1rOGqraqlqkmqMaoZqhGmyaa5ppWmi",
    "aZZpe2lMZ6lnbmYGZVdlUWUKZNtkkwUsAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABARVlYVVRTUlFQT05NTEtKSUhHRkVEQ0JBQD8+PTw7Ojk4NzY1MTAv",
    "Li0sKCcmJSQjIiEfGBQREA8ODQsKCQgHBgUEAwIBACxFI0ZgILAmYLAEJiNISC0sRSNGI2EgsCZhsAQmI0hILSxFI0ZgsCBhILBGYLAEJiNISC0sRSNGI2GwIGAgsCZhsCBhsAQmI0hILSxFI0ZgsEBhILBmYLAE",
    "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",
    "AADILQAAyEMAAMhZAADIbwAAyIUAAMibAADJFwAAycQAAMp1AADLEAAAyyYAAMs8AADLUgAAy2gAAMt+AADLlAAAy6oAAMvAAADL1gAAy+wAAMwCAADMGAAAzIkAAMziAADM+AAAzQ4AAM0kAADNOgAAzVAAAM1m",
    "AADNfAAAzZIAAM2oAADNvgAAzdoAAM3wAADOBgAAzhwAAM4yAADOSAAAzmQAAM56AADOkAAAzqYAAM68AADO0gAAzugAAM7+AADPGgAAz68AAM/FAADQLwAA0EUAANDHAADRVwAA0dQAANHqAADSAAAA0hYAANIs",
    "AADSQgAA0lgAANJuAADShAAA0poAANKwAADSxgAA02EAANN3AADT1gAA1JQAANSqAADUwAAA1NYAANTsAADVfAAA1hkAANZ8AADWkgAA1qgAANa+AADW1AAA13IAANgFAADYnAAA2LIAANjIAADZpwAA2b0AANrK",
    "AADa4AAA25UAANvQAADb/AAA3HMAANzvAADdjgAA3hwAAN45AADecwAA3q0AAN72AADfJgAA300AAN9rAADfiAAA36cAAOACAADgKwAA4HwAAODlAADhLQAA4YUAAOH0AADiGQAA4pkAAOMGAADjMwAA42kAAOOT",
    "AADjuwAA4+UAAORTAADlCwAA5VAAAOW8AADmDwAA5lwAAOaMAADmtQAA5xgAAOdGAADneQAA56wAAOfjAADoAQAA6EwAAOiIAADo7AAA6TUAAOmmAADp+gAA6mUAAOqIAADqzAAA6v4AAOtfAADrmwAA68kAAOv2",
    "AADsHQAA7DwAAOxiAADsjQAA7KgAAOzNAADtOAAA7ZoAAO3nAADuSAAA7qQAAO7tAADvoQAA7+UAAPAzAADwjQAA8MgAAPD2AADxWAAA8ZgAAPHxAADyVAAA8rgAAPLwAADzUwAA85wAAPPeAAD0EwAA9G4AAPSs",
    "AAD0/QAA9SoAAPWIAAD1ogAA9gEAAPY5AAD2bwAA9tUAAPe5AAD4SQAA+MkAAPlQAAD52gAA+hMAAPo9AAD7BAAA+4oAAPvwAAD8mwAA/UYAAP37AAD+qwAA/wkAAP92AAD/7QABAF4AAQC2AAEBHAABAX0AAQHf",
    "AAECTgABAu0AAQNWAAED0gABBLIAAQVFAAEFugABBfwAAQZfAAEG5gABB5AAAQhKAAEJcQABCcsAAQrQAAELMAABDAsAAQyjAAENCgABDbkAAQ4lAAEOvwABDykAAQ+2AAEQOwABEKcAAREfAAESCAABEoMAARLX",
    "AAETlAABFBkAARSaAAEVNAABFbsAARY5AAEWogABFxIAARebAAEYCQABGG0AARjeAAEZQgABGfsAARptAAEa1QABG2IAARvrAAEcrQABHXQAAR3bAAEeHAABHkwAAR8yAAEffgABH9wAASAwAAEg6gABIX4AASHX",
    "AAEh8QABIoAAASLMAAEjogABJIAAASUlAAElywABJk8AAScBAAEnWAABKAwAASjSAAEpWgABKa0AASoZAAEqkAABK3EAASveAAEsGgABLKcAASz5AAEtRQABLfkAAS6PAAEu2AABLzwAAS+rAAEwJQABMJ0AATD3",
    "AAExsgABMm8AATLCAAEzJgABM3oAATQBAAE0VgABNQAAATW3AAE2LwABNpAAATc5AAE3wwABOA4AAThoAAE4wgABOW8AATnkAAE6lgABOvcAATvbAAE8LQABPVsAAT2OAAE+IAABPqIAAT7zAAE/VQABP50AAT/8",
    "AAFAjwABQNwAAUE2AAFB5gABQnMAAUKyAAFDPwABQ7kAAUQ5AAFEyQABRR8AAUWTAAFF/gABRq4AAUcRAAFHTwABR9kAAUh3AAFJKwABSdsAAUoqAAFKqQABSvoAAUtuAAFL3gABTE8AAUznAAFNVwABTcQAAU4Y",
    "AAFOcQABTusAAU+qAAFQkAABUTUAAVHJAAFSsgABUxQAAVN0AAFT5AABVQQAAVXPAAFWfwABVzoAAVfmAAFYmAABWOAAAVkwAAFZqgABWiUAAVqFAAFbCgABW7YAAVv+AAFcaQABXWIAAV38AAFeiwABXu4AAV9f",
    "AAFgGwABYNoAAWGGAAFh+QABYqMAAWL5AAFjoQABZD0AAWTFAAFlKgABZYMAAWXUAAFmJwABZmoAAWbtAAFnSgABaDMAAWjJAAFpggABabgAAWpJAAFrDQABa9UAAWw4AAFtHAABbeIAAW48AAFukQABbr4AAW8q",
    "AAFvZQABb7kAAW/uAAFwPgABcOcAAXFQAAFx4QABcnEAAXL2AAFzHgABc6oAAXPdAAF0EAABdIUAAXTnAAF1XQABddwAAXZqAAF2+QABd74AAXhZAAF45AABeVsAAXmOAAF6DgABepYAAXsNAAF7kQABfD4AAXzP",
    "AAF9NAABfWcAAX2XAAF9xAABffQAAX4kAAF+wQABfvEAAX8kAAF/VwABf5sAAYA1AAGAqwABgQ8AAYFqAAGCDwABgm4AAYMPAAGDzgABhCgAAYSyAAGFBgABhYMAAYYiAAGGigABhv4AAYd3AAGHvQABiHoAAYkH",
    "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",
    "AAJqRAACau0AAmtTAAJr5gACbFYAAmy/AAJtHgACbeYAAm6UAAJvMQACb6AAAm/cAAJwWAACcLcAAnDqAAJxMgACcY0AAnHLAAJyPQACcqYAAnMbAAJzogACdD4AAnTRAAJ1VgACdh0AAnaVAAJ29gACd1cAAnfL",
    "AAJ4rQACeOcAAnlWAAJ5owACeioAAnqFAAJ7CwACe48AAnvkAAJ8VAACfMYAAn03AAJ9uQACfiAAAn54AAJ+9gACf3YAAn+kAAKAMAACgJgAAoEBAAKBXwACgaoAAoIkAAKCsQACgxMAAoPEAAKEZwAChL0AAoVM",
    "AAKFZgAChbYAAoZaAAKGqwAChvMAAoe/AAKICQACiGIAAoieAAKI2AACiSMAAoleAAKJhAACikMAAop0AAKLGAACi64AAovaAAKMBgACjF0AAozxAAKNSgACjaIAAo4bAAKOiQACj0oAAo97AAKP8AACkFkAApC/",
    "AAKQ+gACkWEAApHaAAKShwACkw4AApPBAAKUVwAClNoAApVAAAKVrAACliUAApaZAAKXYAACl7gAAphZAAKYwgACmREAApl7AAKaKAACmnUAAprAAAKbEAACm3AAApvUAAKc2QACnT8AAp2NAAKd2wACnjEAAp57",
    "AAKewAACnzEAAp/zAAKgWAACoOUAAqFcAAKhqgACogIAAqJSAAKi5gACozEAAqNyAAKjtgACpEUAAqTWAAKlYAACpbgAAqZKAAKmjQACps4AAqdpAAKn1QACqEcAAqiPAAKpFQACqbwAAqqAAAKqzgACqygAAquJ",
    "AAKrxwACrDsAAqydAAKs+AACrUMAAq2bAAKt5gACrjsAAq6BAAKu8gACr1UAAq+sAAKv/gACsLcAArEnAAKxxwACsj8AArLZAAKzOQACs4YAArP6AAK0hwACtS0AArVeAAK16gACtlUAAra0AAK3WAACt9YAArgM",
    "AAK4YQACuOoAArkrAAK5bAACugEAAro8AAK6dQACuwsAArtsAAK74AACvBwAAryLAAK87AACvYAAAr3CAAK+GwACvmoAAr7qAAK/RgACv5kAAsAKAALAuAACwO8AAsEtAALBggACwfgAAsIzAALCegACwsEAAsMw",
    "AALDtgACxAwAAsSAAALE5gACxS4AAsVsAALFywACxiMAAsZ5AALG7wACxy0AAsdiAALH5gACyEsAAsiNAALI3QACyTIAAsmGAALJxAACyjcAAsp7AALLEAACy3AAAsv6AALMfAACzOcAAs1FAALNxQACzisAAs5n",
    "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",
    "eMDQKDAwUDiYGCABqAMAAWj+mP0A/ngQGFhQAUgB4P4gAeD+IAAEAJD/mAK4BfAABwALAA8AEwAAAREjNSMVIxETMxEjETMRIxEzESMCuJj4mJj4+Pj4+PgF8PoASKAGWP5IASj9IAEo/SABKAAEAKD/mALQBfAA",
    "BwALAA8AEwAAAREjNSEVIxETIREhESERIREhESEC0Jj++JCQAQj++AEI/vgBCP74BfD52HCgBlj+SAEo/SABKP0gASgABALY/0gHsAY4ABQAKwBAAFYAAAEhAgcWFwcnBgcnNjcmJzcWFzY3ISUhAgcWFwcmJwcG",
    "BgcnNjcnNxYXNjchASECBxYXByYnBgcnNjcmJzcXNjchJSECBxYXByYnBgcnNjcmJzcWFzY3IQNAAggYaEhAYHh4mEigSGhoYGBgKCD+oAJAAegYaGBQaFBQWBhgQEiIYMhgYGAwGP7A/egBwBhQWEhYSEiQwFDI",
    "aFhYYJAgEP7wAfgCEBigWKBoiGhYeFBwWHggkBhIUBj+oAY4/vCwODh4cJhQgFBoUEBoOEBQiJD+4LBIWHhQSGAgOCCASHCQaDhIYIj9QP7wuFBYeFhA4GiIaMhQQGhwYGiQ/oDwcFBwQHBoSIhAaLjAKJCImMAA",
    "BAMY/0AHqAZgAAUANQA6AEAAAAEXBAUnIAUWFyE2NxcGBzMVIQchFSEGByEVBgcWFwcmJwYHJzY3JicGBycSEyM1ITchNTMmJwEWFzY3ARYXByYnByhQ/nD9uDAB4P7oYDgBSGgwqDhgqP3QGAJ4/WgQGAJASICQ",
    "yFDgqMD4SOCYcFBgkIDwWPgBGBD/AKAwQAE4UIBwQP74SDB4KEgGYIhQGJC4cICgqDCQiIiYkFBAiMh4SDCYQHB4OJgoWGiAyKhgASgBUJCYiFhI/JiIYFiQA9BQWEhYUAABAjD/SAeYBngAFgAAARcGByEVIREh",
    "FSERIRUhESMRIwYHJxIDoKggMAOg/UACQP3AAlj9qKCAaLBw8AZ4KIBwmP7IkP7ImP4YBYD4yIABMAACAGD/QALYBngABQAQAAABFwIFJyQXFwYHESMRBgcnAAIIiJj+2GABGMiIUIiYYEhgAUAGeEj+2NiA2NhI",
    "oKj8IANAYDiAAQAAAgJY/5gHmAZ4AAUAGQAAARYXByYnASEVIREhFSERIRUhNSERITUhESEEuHhIiEh4/mAE6P3YAeD+IAJI+sACWP4gAeD94AZ4cIhQgHD+2Jj+MJD+MJiYAdCQAdAABQCIA1gHeAZgABMAFwAb",
    "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",
    "AHAAOgAvAC8AdwBlAG4AcQAuAG8AcgBnAC8AKQAgAGEAbgBkACAAUQBpAGEAbgBxAGkAYQBuACAARgBhAG4AZwBXAGUAbgBRAHUAYQBuAFkAaQAgAE0AaQBjAHIAbwAgAEgAZQBpACAATQBvAG4AbwBSAGUAZwB1",
    "AGwAYQByAFcAZQBuAFEAdQBhAG4AWQBpACAALQAgAE0AaQBjAHIAbwAgAEgAZQBpAFYAZQByAHMAaQBvAG4AIAAwAC4AMgAuADAALQBiAGUAdABhAFcAZQBuAFEAdQBhAG4AWQBpAE0AaQBjAHIAbwBIAGUAaQBN",
    "AG8AbgBvAEQAcgBvAGkAZAAgAGkAcwAgAGEAIAB0AHIAYQBkAGUAbQBhAHIAawAgAG8AZgAgAEcAbwBvAGcAbABlACAAYQBuAGQAIABtAGEAeQAgAGIAZQAgAHIAZQBnAGkAcwB0AGUAcgBlAGQAIABpAG4AIABj",
    "AGUAcgB0AGEAaQBuACAAagB1AHIAaQBzAGQAaQBjAHQAaQBvAG4AcwAuAEEAcwBjAGUAbgBkAGUAcgAgAEMAbwByAHAAbwByAGEAdABpAG8AbgBXAGUAbgBRAHUAYQBuAFkAaQAgAE0AaQBjAHIAbwAgAEgAZQBp",
    "ACAAaQBzACAAYQAgAGgAdQBtAGEAbgBpAHMAdAAgAHMAYQBuAHMAIABzAGUAcgBpAGYAIAB0AHkAcABlAGYAYQBjAGUAIABkAGUAcwBpAGcAbgBlAGQAIABmAG8AcgAgAHUAcwBlAHIAIABpAG4AdABlAHIAZgBh",
    "AGMAZQBzACAAYQBuAGQAIABlAGwAZQBjAHQAcgBvAG4AaQBjACAAYwBvAG0AbQB1AG4AaQBjAGEAdABpAG8AbgAuAGgAdAB0AHAAOgAvAC8AdwB3AHcALgBhAHMAYwBlAG4AZABlAHIAYwBvAHIAcAAuAGMAbwBt",
    "AC8AaAB0AHQAcAA6AC8ALwB3AHcAdwAuAGEAcwBjAGUAbgBkAGUAcgBjAG8AcgBwAC4AYwBvAG0ALwB0AHkAcABlAGQAZQBzAGkAZwBuAGUAcgBzAC4AaAB0AG0AbABMAGkAYwBlAG4AcwBlAGQAIAB1AG4AZABl",
    "AHIAIAB0AGgAZQAgAEEAcABhAGMAaABlACAATABpAGMAZQBuAHMAZQAsACAAVgBlAHIAcwBpAG8AbgAgADIALgAwAGgAdAB0AHAAOgAvAC8AdwB3AHcALgBhAHAAYQBjAGgAZQAuAG8AcgBnAC8AbABpAGMAZQBu",
    "AHMAZQBzAC8ATABJAEMARQBOAFMARQAtADIALgAwAFcAZQBuAFEAdQBhAG4AWQBpACAATQBpAGMAcgBvACAASABlAGkAAwAAAAAAAP8AAGYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIABQAC//8AAwABAAAADAAA",
    "AAAAAAACAAgAAADPAAEA0QEGAAEBCAFsAAEBbgF0AAEBdgK0AAECtgOyAAEDtASKAAEIuQkbAAEAAQAAAAoADAAOAAAAAAAAAAEAAAAKABYAGAABbGF0bgAIAAAAAAAAAAAAAAABEAAFWveJAAAIAP9I9lARsAAA",
    "AAEAAAAAAAAAAAAAAAAAAQgABbgDwAYYA8AGGAYIBggGCAYIBggGCAYIB/gE4ASwBFAEsATYBLgGAAYABkgAAAEwATgGYAZgBmAC4AZgBmADgAYIBeAGWAYIBhgGeAZ4BjAGeAZgBhgGOAZ4BoAGeAZ4BngGcAaI",
    "BmgGUAZ4BmAGEAZ4BngGAAZ4BngGEAaIBngFkAYABggGCAZ4BoAGaAaABlAGeAZ4BngGgAZ4BoAGgAZ4BngGgAZ4BoAGeAZ4BngGeAZ4BngGiAaABngGeAZ4BngGgAZ4BngGeAZ4BoAGeAZ4BoAGeAZ4BngGeAZ4",
    "BngGeAaIBoAGeAaIBngGeAZ4BoAGeAaIBngGeAZ4BoAGgAZ4BngF+AZ4BngGgAZ4BngGiAZYBnAGgAZwBkAGiAaIBoAGYAYgBjAGeAZ4BkAGeAZ4BogGgAaABngGEAaABkAGeAZ4BigGGAYQBnAGeAZwBngGeAaA",
    "BnAGeAZ4BnAGeAZ4BnAGeAaABpAGcAZ4BoAGiAZwBngGeAZ4BogGeAZ4BngGiAZ4BjgGeAZQBngGgAaIBngGeAZ4BoAGAAZ4BngGOAY4BjgGOAZ4BoAGEAYwBhAGeAZwBjgGeAZ4BmAF4AZ4BggGeAYYBggGgAZ4",
    "BjAGgAaIBpAGOAZ4BmgGgAY4BoAGaAaABjAGQAZIBkAGkAaABigGiAaQBlgGKAaABoAGgAYwBoAGeAZ4BkAGiAY4BjgGCAY4BjgGOAY4BjgGOAY4BiAGgAZ4BlgGYAaABlgGgAZ4BngGYAZYBngGeAaIBogGgAaI",
    "BoAGeAaIBoAGeAZwBoAGeAZ4BngGeAaABpAGeAZ4BngGgAZ4BngGgAaABjAGiAaABogGiAaIBpAGiAaIBogGiAaIBogGiAaIBogGiAaIBogGeAZ4BjgGgAZ4BnAGaAZoBngGeAYYBkgGSAZIBkgGSAZIBngGeAYI",
    "BngGMAaQBiAGCAaIBoAGeAZ4BngGeAXwBigGiAaABoAGgAaABoAGgAaABoAGEAZwBngGIAZABngGeAZoBngGcAZABngGgAZIBmgGaAaABngGeAaABoAGeAZ4BngGeAaABmAGYAZ4BngGmAZ4BngGgAYgBngGgAZ4",
    "BngGkAZ4BngGeAaABpAGiAZ4BngGeAaABoAGgAZ4BoAGeAZ4BngGYAZ4BoAGeAZ4BngGeAZ4BngGgAZ4BngGeAY4BngGeAZ4BngGeAZ4BoAGeAZ4BngGgAaABngGeAZ4BoAGgAZ4BoAGeAZ4BngGeAZ4BoAGiAaI",
    "BoAGeAZ4BngGeAZ4BogGeAZ4BngGgAZ4BngGeAaABngGeAaABoAGeAZ4BngGeAZ4BoAGeAZ4BngGeAZ4BoAGgAZ4BpAGeAaABoAGeAZ4BngGgAZ4BngGeAaABngGeAaABnAGgAZ4BoAGeAZ4BngGiAaABngGGAYg",
    "BiAGGAY4BngGSAZQBkgGeAZQBjAGiAZ4BkgGgAZgBogGUAY4BngGQAZIBoAGSAZ4BngGeAZ4BoAGcAZABngGiAZ4BngGeAZ4BogGeAZ4BngGeAYwBoAGgAaABoAGeAZ4BngGeAaABngGgAZ4BngGeAZ4BngGeAaA",
    "BngGeAaABngGeAZ4BngGgAaIBngGeAYQBnAGgAXwBngGMAaABngGYAaIBngGiAaIBmgGaAZoBnAGcAaABngGgAZ4BngGeAZ4BmgGgAZ4BoAGgAaABoAGaAZ4BmgGaAZ4BngGeAZ4BnAGWAZoBoAGeAZoBlgGeAZ4",
    "BngGeAZYBoAGeAZ4BoAGeAYwBngGeAaABmgGeAZ4BjAGeAaABoAGeAaABoAGgAaABoAGgAaABhgGGAY4BngGIAZ4BngGGAZ4BjAGeAYwBjgGeAaABpAGiAaIBpAGeAaABngGeAaQBpgGeAZ4BoAGgAYgBngGeAZ4",
    "BnAGeAZgBngGKAZIBogGeAZ4BnAGgAZ4BngGeAYwBigGeAY4BngGMAZ4BngGeAZABggGgAaABogGeAaQBoAGgAaABngGaAaABoAGaAaABoAGiAaIBpAGiAaIBoAGeAZ4BoAGeAaIBogGiAaIBogGiAaIBogGiAaI",
    "BogGiAaIBngGiAZ4BngGaAZ4BoAGWAZ4BkgGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGiAaABngGeAZ4BngGeAZ4BoAGeAaABoAGKAZQBlAGgAZwBngGeAaABigGeAYwBjAGcAZIBkgGeAZ4BoAGgAaA",
    "BngGSAZIBoAGgAYYBngGSAaABoAGeAZ4BoAGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BogGOAaIBoAGeAaABngGeAZ4BngGgAaABngGeAZ4BngGcAZwBjgGQAZYBiAGMAZ4BogGiAaIBqAGgAaABoAGeAZ4BngGgAZ4",
    "BngGeAZ4BngGeAZ4BngGgAZ4BngGeAZ4BoAGeAZ4BogGeAaABngGoAaABngGiAZ4BmgGaAZABngGeAZ4BoAGgAZ4BngGeAZ4BoAGMAZYBoAGMAZIBoAGYAZwBogGgAaABngGgAZ4BngGeAZ4BoAGgAZIBngGSAZw",
    "BkgGaAZ4BkgGgAZwBkgGgAZIBngGgAZIBogGYAZ4BmAGSAaABkgGgAZ4BkgGgAZ4BoAGeAYYBoAGeAZABkgGcAY4BlgGUAaABngGeAZ4BngGeAaQBoAGeAZ4BngGeAaIBnAGkAaQBpAGkAaQBpAGeAZ4BkgGeAZ4",
    "BoAGMAaABkgGgAZ4BnAGeAYwBoAGYAZYBmAGcAZwBngGiAZ4BoAGKAaIBjgGOAY4BngGSAY4BmgGOAZQBlAGeAZ4BjAGSAX4BpAGgAaIBoAGgAaABmgGSAY4BngGOAZgBlAGiAaQBoAGiAZABoAGgAaABngFuAW4",
    "BbgGEAXIBdAFuAW4BbgGGASgATADKAEwBbgF0AW4BcgFyAXABbgFyAW4BdAFyAQgBCAE4APoBOAFyAW4BcAFuAXIBbgFuAW4BcgFuAW4BbgFuAW4BbgFuAXQBbgF0AW4BcgFuAW4BbgFuAW4BbgFuAW4BbgFuAXA",
    "/0gGIARgBhgEYAYYBGAGIARgBhgGEAYQBhgGGARgBGAEYARgBGAEYARgBXAESARIBEgESARIBEgFuAYYBbgDWAJ4BoADaAMoA2AGcAUwBGgECAaABkgGeAZIBoAGMAZgBjAGgAZwBoAGIAZABnAGOAPgBoAGKAVw",
    "BRgGIAPQBogGQAPgBOAGeAaAAigFIASoBWAE2ATABNgESAUABNgEQASIBngGeAZIBOgGSAS4BJgEWASABHgEQARgBngECAPABMgGeAZ4BpgGkARgBMAGeAWQBngGgAZ4BlgGKAZ4BmgGgAZ4BIgCsAX4BiADqAaA",
    "BnAGcAZABlADSAZIBEgGiAZ4BoAGeAaYBngGcAZ4A2gGQAZwBPgFEATwBEgFCASwBSgEeAQwBIAEiAOQA5AECAY4BNgEmAUABPgFAATQBJADuARwBpAEmATgBiAFeAXoBngCSAWIBVAFCAJwBoAGcAYoBlAFMAZ4",
    "BngGgAUABngC8AY4BiAGgAZoBpAGeAZ4BiAGeAaABoAGeAZ4BmAGeAaIBogGeAY4BjAGgAY4BoAGgAZ4BoAGeATQAvgGOAYwBngGeAZ4BkAGeAaABggGWAZQBkgGiANABoAF8AZoBnAGIAZ4BngGeAaABogGeAYY",
    "BngDSAaABngEmAaABogGSAYoA0AGeAMYBoAGeAZ4BagGQAaIBngCkAZ4BogCeAIIBoAGQAZ4BhgGSAIIBnAGgAY4BjgGeAGoBngCoAIIBoAGAAZ4BoAGOAY4BnAGGAZQAtgF0AaABoAGeAZ4BoAGOAZ4BdgFyAXI",
    "BcAFwAaABcgFyAXIAhgGeANoBngC2AZgBoAGOAZIBkgGeAVwBhAGeAY4BngGOAaABngGeAZ4BjgGGAZ4BjAGgAZ4BngGeAZ4BngGeAZ4BkgGKAZ4BoAGeAZABnAGiAZ4BhgGeAJYBegBgAaABngGeAaABngGEAZ4",
    "BngGIAYQBoAGSAaABjAGeAYoBhgGeAaABngGOAaABggGeAZ4BoAGeAYQBngGeAZ4BoAF4AZIBngGAAZwBhAGeAY4BngF6AZ4BngGgAZ4BkAGiAZ4BngGeAYwBngGgAZ4BjAGMAZ4BngGOAaABOgGeAZ4BlAGOAZw",
    "BnAGiAZ4BjAGeAZ4BngGeAZ4BngGGAaABoAGKAaABMgGeAYQBOgGeAaABkAGgAZ4BngGcAYoBoAGgAIIBPAGgAZ4BjAGeAN4A1gGcAZwBjAGeAZ4BmAGeAaAAmgGiAToBegBSAZ4BnAGgAYIBngGeAZYBoAEEAZ4",
    "BngDaAYIBjAGgAKoBjAF+AYoBngGQALYBmAGeATYBNgGeAMABmgGgAZoBogGgAaABoAGeAaABngGKAZABLgGIAYoBoAGeAZ4BngC4AZ4BogGeAaIBnAGcAZQBoAGeAZIBoAFGAZgBngE+AZoBlgGWAZ4BmAGYAZo",
    "BjgGGAZ4AyAGgAZ4BIgGWAZ4BngGeAZwBogBIAaABoACOAZABogGiAZ4BngGeAaIBngEiAaQBngGgAY4BhgGGAZYBjAE6AX4BmgGgAaABoAGgAZ4BkAGgAZ4AlAGgAOoBngGGAaABiADAAZgBngGeAY4BmgGeAZ4",
    "BngGeALgBogGCAYIBoAGeAMwBngEoAaABlgGeAZ4AqAGcAZgBoAGeAZ4BngDuAZ4BiAGgAKoBggGgAaQBlgGiAYoBjAFyAUwBWgGMAaABngGeAZYArgGiAaIAnACqAYwBjgGOAZABjAGeAZoBogEeAY4BlAGGARI",
    "BjAC0AYABggGcAZwBnAGaAaABlAGcAYwBngGeAVIBngGeAQwBoAGYAZ4BngGeAZ4BngEgAZ4BjAGMAKQBkAGeAaABoAGOAXgAigGiAR4AXgFeAVYBWAGUAZABjAGEAaIBjgGCAZ4BngGeAY4BogEMAYQBogGeAZ4",
    "BlgGeAZ4BoAGcAZwBngGcAZ4BggGeAaABoAGGAXIBfgGeASYBngCGAQwBjgGeAZ4BngGeAYoBjgGIAZ4BoAGeAZ4BkgGIAaABngGEASABjgF+AZIBfgGEAZwBFAGcAZAA5gGgAaABngE8AZ4BngGeAY4BlAGOAZQ",
    "BjgGeAZ4BngGeAZIBDgGgAZIBngGeAZ4AkgFSAZQBmgGeAY4BiAGeALwAqAGgAaABhAGEAaIBoAGgAaABogGkAaABnAGeAZ4BnAGGAaIBoAGOAXwBngGeAaIBoAGeAIgBoAGeAZ4BngGgAZIBjgDgAZABlAGGAY4",
    "BoAGIAZ4BngGAAZwBngGeAZ4BogF4AaABoAGeAY4BlgGWAZ4BoAGSAZ4BigGeAZ4BhgGMAZ4BngGUAZoBmAGgAYIBhgGIAYAAdgGQAYwBkgGeAYgBngGgAaABhgGgAYYBhgGSAZwBoAGeAZ4BlgGgAYABnAGaAZ4",
    "BoAGUAaABkgGSAZIBngGcAaABmgGeAZoBjAGaAZ4BhAGeAZwBoAGeAZABiACuAZIA9AGgAOQBogCwAZ4BhgGeAZ4BhgGaAMoBngGgAaABoAGgAY4BngGeAZYBlgGkAMQBjgGIAHgBngGeAZ4BhAGEAZwA5AGiAaA",
    "BoAC4AZoAyAGEAZ4BngGgAZYBogGeAZ4BnAEyADABjAGIAaABmgGeAaAArAGeAaABHgGiAX4BEgGSAZIBoAGeAZ4BngGeAZ4BiAGeAOgBmgGgAZ4BngGeAZ4BngDMAOABkAGeAYoBnAGAAZ4BngGcAZ4AngGeAMo",
    "BngGeAYoBogCQAaIBngGeAZoBngGMAZ4BhAGeAZ4BngGeAaABnAGMAGwBngGCAZ4BngGeADoBngGeAE4BgAGkAZ4BogF4AXgBjAGeAZ4BngGOAaABnAGaAZ4BoAGCAZ4BngGeAZ4BkAGQAYwBjACaAHIAiACQAZ4",
    "BngGeAZ4BogGiAZ4BfAF8AY4BmAGeAZ4BngGYAZYBogGeAZ4BkgGaAaABoAAAAW2BbYFtgXHBc0FtgW2BbYGFASiAQYCeQEtBbYFzQW2BcsFywW+BbYFywW2Bc0FywRmBGYEyQPpBMkFywW2BbwFtgXLBbYFtgW2",
    "BcsFtgW2BbYFtgW2BbYFtgXNBbYFzQW2BcsFtgW4BbYFtgW2BbYFtgW2BbYFtv9IBiEEXgYUBF4GFAReBh8EXgYUBg4GDgYUBhQEXgReBF4EXgReBF4EXgVvBEoESgRKBEoESgRKBbYGFAW2A1oFxQNeBHsCeQD6",
    "BA4AAA==",
)

_FONT_BYTES_CACHE = None


def _font_bytes():
    """解码内嵌字体；只解一次，之后复用字节（多个字号共用）。"""
    global _FONT_BYTES_CACHE
    if _FONT_BYTES_CACHE is None:
        _FONT_BYTES_CACHE = base64.b64decode("".join(_FONT_B64_LINES))
    return _FONT_BYTES_CACHE


if __name__ == "__main__":
    if "--selftest" in sys.argv or "--touchtest" in sys.argv:
        # 电脑上的无窗口自检 / 触屏压力测试，同步执行，不进 asyncio
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.init()
        pygame.display.set_mode((SCREEN_W, SCREEN_H))
        if "--selftest" in sys.argv:
            run_selftest()
        else:
            run_touchtest()
        pygame.quit()
    else:
        # pygbag 要求 asyncio.run() 出现在模块级；桌面 IDE 走的是同一个循环
        pygame.init()
        asyncio.run(App().run())
