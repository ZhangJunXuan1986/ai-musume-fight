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

【2026-11-11 v3.5 —— 按实测截图修 9 个问题（输入桥保持不动）】
★ 本版【不改 main.yml、不改 tools】：v3.4 的 JS 输入桥已验证触摸/鼠标都能用，
   只传 game/main.py 一个文件即可。
A. 【开局 100% 复现的 bug】双方自动前冲 + 发飞弹 + 气够自动放大招：
   ai_decide 返回旧键码 (k["far"],)，但 v3.2 已把 KEYS_P2 的
   far/ult/assist/dash 置成 None；synth_keys 把 None 加进【全局】just，
   而 _do_far/_do_ult/_do_assist/_do_jump_dash 用 `k["far"] not in just` 判断，
   k["far"] is None → None in just 恒真 → 两边同时触发。实测一帧后
   p1.vx=12 / proj=3 / ult_cd=90 / 浮字「深度推理」。
   修法：AI 改返回 (action,side) 元组；synth_keys 过滤 None；四个旧 _do_* 加
   `if k[...] is None: return` 守卫；start_match 清空 just/touch_hits/ai_cache。
B. AI 太呆：旧 ai_decide 的键码根本进不了 dispatch_actions（只认元组），
   所以电脑永远不放 4 技能 / 闪避 / 净化 / 秘卷，只会平 A。
   重写为按距离分层的元组决策：远距离主动靠近 + s2 远程技，
   中距离 s1/s3 突进控场，近身连招 + 满气奥义（带节流，不一好就放），
   被控净化、对手出招贴脸闪避、偶尔开秘卷。难度常量集中在 ①-C。
C. 「大招一好就自己放」= A 的连带效果；修完 A 后玩家侧不再自动放，
   AI 侧奥义加了距离 + 节流条件，不再气一满就甩。
D. 闪避 CD 150 帧(2.5 秒) → 72 帧(1.2 秒)，常量在 ①-B，注释写明可调。
E. 双方高速对冲能直接穿过：_separate_fighters 原本只在 |d|<19px 时推开，
   一帧就跨过窗口。改为【扫掠检测】：记录上帧相对位置，落地且发生左右翻转时
   拉回最小间距；空中仍完全不推（保留 v3.2 的「跳过去绕背」）。
F. 手机按键太小：技能圆键半径 27~40 → 34~48，功能胶囊 72x36 → 84x48，
   中间按钮 104x34 → 128x46；全部重新排布，自检验证同簇圆键两两不相交、不越界。
G. 「中间的选项点不了」：hit_button 改为 mid_btns 优先（PVP 两簇内移时会抢命中）；
   战斗页 active_buttons 补上 global_btns → 右上角「输入诊断」随时可点。
H. 「诊断页退不出去」：点诊断框内【任意处】即可关闭；Esc / F9 / 右上角按钮
   三条路都能关；框内文字明确写出。手机上不再需要 F 键。
I. 操作说明页全面更新：新键位、PVE 电脑行为、诊断关闭、闪避 CD、
   地面不能穿人 / 空中可绕背、奥义耗气与 CD、中间按钮位置，全部写进页面。
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
VERSION = "v3.5-ai-fix"

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
DODGE_CD = 72              # 闪避冷却帧（60 帧=1 秒；72≈1.2 秒）。嫌长/嫌短改这一行
DODGE_RAGE_ON_SUCCESS = 8  # 无敌帧内确实躲掉一次攻击，回的气
CLEANSE_CD = 300           # 净化冷却帧（5 秒）
CLEANSE_IMMUNE = 90        # 净化后免控帧（1.5 秒）
SCROLL_CD_FALLBACK = 360   # 秘卷未单独写 cd 时的默认冷却（6 秒）

# ---- ①-C 电脑对手（PVE）行为参数：改这里就能调 AI 强度，不用动逻辑 ----
AI_ENGAGE = 132            # 贴身距离：小于它进入近身连招
AI_RETREAT = 54            # 过近时偶尔后撤拉开的距离
AI_FAR = 300               # 远距离阈值：大于它优先放远程技 s2 并主动靠近
AI_ULT_RAGE = 200          # AI 放奥义至少要 2 格气
AI_ULT_EVERY = 5           # 奥义节流：每 N 次【决策】才考虑一次，避免一好就放
AI_DODGE_EVERY = 3         # 对手贴脸出招时，每 N 次【决策】考虑一次闪避
AI_SCROLL_EVERY = 22       # 秘卷每 N 次【决策】开一次（≈4 秒）
AI_RETREAT_EVERY = 8       # 后撤节奏（每 N 次决策里前 2 次后撤）
# 注意：AI 只在 t % AI_THINK_FRAMES == 0 时决策，所以节流必须按【决策次数】
# 取模，不能用全局 frame —— 否则 N 不是 11 的倍数时永远命中不了（v3.5 实测踩过）。

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
DIAG_RECT = pygame.Rect(296, 176, 688, 326)   # 诊断框：点框内任意处也能关闭（手机无 F9）


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
    # v3.5：手机实测按键太小，半径整体放大约 25%，并重新排布保证两两不相交
    ("atk",   1150, 600, 48, (190, 214, 255)),   # 普攻大圆
    ("s1",    1030, 570, 34, (120, 190, 255)),   # 技能 1
    ("s2",    1078, 505, 34, (120, 190, 255)),   # 技能 2
    ("s3",    1155, 497, 34, (120, 190, 255)),   # 技能 3
    ("ult",   1235, 555, 38, (255, 208, 96)),    # 奥义（金色）
]
FUNC_BAR = [
    # 动作,    左上x, y,   宽,  高   —— 横胶囊，不跟技能圆混在一起
    # v3.5：72x36 → 84x48，触摸面积接近翻倍
    ("jump",     916, 658, 84, 48),   # 跳跃：4399 的 K / 2
    ("dodge",   1006, 658, 84, 48),
    ("cleanse", 1096, 658, 84, 48),
    ("scroll",  1186, 658, 84, 48),
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
    # v3.5：104x34 → 128x46，手机上一指点得中；行距同步加大
    w, h = 128, 46
    x0, y0 = 500, 526     # 仍在画面中央下缘，不压角色（角色在 y≈380~516）
    step_x, step_y = w + 12, h + 8
    return [
        _btn(x0,           y0,            w, h, "切模式", (), ()),
        _btn(x0 + step_x,  y0,            w, h, "切操作", (), ()),
        _btn(x0,           y0 + step_y,   w, h, "暂停",   (), (GLOBAL_KEYS["pause"],)),
        _btn(x0 + step_x,  y0 + step_y,   w, h, "返回",   (), (GLOBAL_KEYS["cancel"],)),
        _btn(x0,           y0 + step_y*2, w*2 + 12, h, "操作说明", (), ()),
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
    """v3.5：电脑直接返回 (action, side) 动作元组，走 dispatch_actions。

    旧版返回的是 KEYS_P2 键码，而 v3 的技能派发只认 (action,side) 元组，
    所以电脑从来放不出技能；更糟的是它返回的 (None,) 被塞进全局 just，
    让【玩家和电脑双方】每帧自动冲刺 / 发飞弹 / 放大招。这里彻底重写。

    返回 (持续按住的键码, 本帧动作元组)；移动仍用 P2 的方向键码，
    与 P1 键码完全不重叠，不会干扰玩家。
    """
    k = KEYS_P2
    dist = abs(bot.x - foe.x)
    held = []
    acts = []
    # 决策计数：AI 只在 t % AI_THINK_FRAMES == 0 时被调用，
    # 所有节流按这个计数取模，才不会和 11 帧周期错位。
    tick = getattr(bot, "ai_tick", 0) + 1
    bot.ai_tick = tick

    # 1) 走位：远了主动靠近，太近偶尔后撤，避免两个模型贴成一团
    if dist > AI_ENGAGE:
        held.append(k["right"] if bot.x < foe.x else k["left"])
    elif dist < AI_RETREAT and tick % AI_RETREAT_EVERY < 2:
        held.append(k["left"] if bot.x < foe.x else k["right"])

    # 2) 被控 → 优先净化（定身/催眠/沉默/减速/标记）
    if (is_disabled(bot) or any(has_status(bot, n) for n in NEGATIVE_STATUS)) \
            and bot.cleanse_cd == 0:
        acts.append(("cleanse", 2))

    # 3) 对手贴脸且在出招 → 用闪避躲（有内置 CD，不会连滚）
    if (dist < AI_ENGAGE + 40 and foe.state == "atk"
            and bot.dodge_cd == 0 and tick % AI_DODGE_EVERY == 0):
        acts.append(("dodge", 2))

    # 4) 按距离分层选技能；每个槽位都有 CD，cast_skill 会自己挡住没好的
    if dist > AI_FAR:                       # 远距离：远程技 + 追击
        if bot.cd_s2 == 0:
            acts.append(("s2", 2))
        elif bot.cd_s1 == 0:
            acts.append(("s1", 2))
        elif bot.cd_s3 == 0:
            acts.append(("s3", 2))
    elif dist > AI_ENGAGE:                  # 中距离：突进 / 控场
        if bot.cd_s1 == 0:
            acts.append(("s1", 2))
        elif bot.cd_s3 == 0:
            acts.append(("s3", 2))
        elif bot.cd_s2 == 0:
            acts.append(("s2", 2))
    else:                                   # 近身：连招 + 满气奥义（带节流）
        if (bot.rage >= AI_ULT_RAGE and bot.cd_ult == 0
                and tick % AI_ULT_EVERY == 0):
            acts.append(("ult", 2))
        if bot.cd_s3 == 0:
            acts.append(("s3", 2))
        elif bot.cd_s1 == 0:
            acts.append(("s1", 2))
        elif bot.cd_s2 == 0:
            acts.append(("s2", 2))
        elif bot.atk_cd == 0:
            acts.append(("atk", 2))

    # 5) 秘卷偶尔开（霸体 / 控制 / 强化 / 替身，设置页可换）
    if bot.scroll_cd == 0 and tick % AI_SCROLL_EVERY == 0:
        acts.append(("scroll", 2))

    return tuple(held), tuple(acts)


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
        # 旧冲刺已停用；必须显式挡 None，否则全局 just 里的 None 会让双方开局自动冲
        if k["dash"] is not None and k["dash"] in just and self.dash_cd == 0:
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
        """旧远攻（已停用）。守卫必须显式挡 None：None 曾混进全局 just，
        导致 k["far"] is None 时 `None in just` 恒真，双方每帧自动发飞弹。"""
        if k["far"] is None or k["far"] not in just or self.far_cd != 0:
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
        """旧必杀（已停用）。挡 None，否则气一满就自动甩大招。"""
        if k["ult"] is None or k["ult"] not in just or self.rage < ULT_COST \
                or self.ult_cd != 0:
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
        """旧援助 / 反制（已停用）。挡 None，避免每帧自动挂援助缓冲。"""
        if k["assist"] is None:
            return
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
            # v3.5：带上 global_btns，战斗页右上角「输入诊断」随时可点可关
            return self.left_btns + self.right_btns + self.mid_btns + self.global_btns
        out = list(self.global_btns)
        if self.scene == "menu":
            out += self.mode_btns
        if self.scene == "select":
            out.append(self.assign_btn)
        return out

    def hit_button(self, pos):
        """v3.5：中间按钮优先判定。PVP 两簇向内平移时会压到中间区域，
        旧版按 left+right+mid 顺序遍历，中间选项永远被技能圆抢走 → 点不到。"""
        if self.scene == "game" and not self.over:
            for b in self.mid_btns:
                if b[0].collidepoint(pos):
                    return b
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
        # v3.5：诊断叠层点框内任意处关闭（手机没有 F9，之前打开就退不出去）
        if self.diag and DIAG_RECT.collidepoint(pos):
            self.diag = False
            self._diag("诊断：点框内关闭")
            return
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
                    # v3.5：绝不让 None / 裸键码混进全局 just（会同时触发 P1 的旧动作）
                    if c is not None:
                        self.just.add(c)
            held.update(c for c in self.ai_cache[0] if c is not None)
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
        # v3.5：清掉上一局残留，避免旧按键 / 旧 AI 决策带进新一局开局
        self.just = set()
        self.clicks = []
        self.touch_hits = {}
        self.stick_hits = {}
        self.ai_cache = ((), ())
        self._prev_d = None
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
        r = DIAG_RECT
        ov = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        ov.fill((6, 9, 24, 232))
        s.blit(ov, r.topleft)
        pygame.draw.rect(s, (255, 208, 96), r, 2, border_radius=10)
        draw_text(s, "输入诊断 · 点本框任意处关闭 · 或按 Esc / F9",
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
            "点框内关闭；右下技能键坐标应接近 (1100,600)",
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
        """v3.5：地面不能互相穿过，空中仍可跳过去绕背。
        · 任一方在空中 → 完全不推（保留 v3.2 的跳跃绕背）；
        · 双方落地时做【扫掠检测】：若这一帧左右关系发生翻转（一帧跨过了对方），
          按翻转前的左右次序把两人拉回最小间距，高速对冲就不再穿模；
        · 没翻转但贴得太近时，按当前左右关系轻轻推开（d<0 也不强行翻回来）。
        """
        if self.p1.y < GROUND_Y - 2 or self.p2.y < GROUND_Y - 2:
            self._prev_d = self.p2.x - self.p1.x
            return
        d = self.p2.x - self.p1.x
        prev = getattr(self, "_prev_d", None)
        limit = BODY_W * 0.62          # 最小中心间距（比旧版 0.34 更稳）
        if prev is not None and prev * d < 0 and abs(d) < BODY_W * 3:
            # 发生了穿越：把两人放回「翻转前」的左右次序，各占 limit 的一半
            sign = 1 if prev > 0 else -1
            mid = (self.p1.x + self.p2.x) / 2.0
            self.p1.x = mid - sign * limit / 2.0
            self.p2.x = mid + sign * limit / 2.0
            self.p1.x = clamp(self.p1.x, ARENA_LEFT + BODY_W/2, ARENA_RIGHT - BODY_W/2)
            self.p2.x = clamp(self.p2.x, ARENA_LEFT + BODY_W/2, ARENA_RIGHT - BODY_W/2)
        elif abs(d) < limit:
            push = (limit - abs(d)) / 2.0 * (1 if d >= 0 else -1)
            self.p1.x -= push
            self.p2.x += push
            self.p1.x = clamp(self.p1.x, ARENA_LEFT + BODY_W/2, ARENA_RIGHT - BODY_W/2)
            self.p2.x = clamp(self.p2.x, ARENA_LEFT + BODY_W/2, ARENA_RIGHT - BODY_W/2)
        self._prev_d = self.p2.x - self.p1.x

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
        # v3.5：Esc 优先关诊断；否则战斗中直接回主页面（手机上「返回」也可点）
        if k["cancel"] in just:
            if self.diag:
                self.diag = False
            elif not self.over:
                self.scene = "menu"
                return

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
            ("P1 移动", "A / D 左右   W 上挑   S 防御"),
            ("P1 攻击", "J 普攻   K 跳跃   J+K 满 3 格气变身"),
            ("P1 技能", "U 技1   I 技2   O 技3   L 奥义"),
            ("P1 功能", "Q 闪避   E 净化   Z 秘卷"),
            ("P2 主键盘", "1攻 2跳  4/5/6技  3奥义  7/8/9功能"),
            ("P2 小键盘", "Num1攻 Num2跳 Num4/5/6技 Num3奥义"),
            ("单人 PVE", "小键盘归 P1；电脑会追击·放技能·闪避"),
            ("诊断页", "点右上角「输入诊断」开，点框内任意处关"),
            ("中间按钮", "切模式 / 切操作 / 暂停 / 返回 / 说明"),
        ]
        for i, (a, b) in enumerate(rows1):
            y = 192 + i * 44
            if a:
                draw_text(s, a, left.x + 20, y, 17, COL_GOLD, True)
                draw_text(s, b, left.x + 130, y, 16, COL_TEXT)
        draw_text(s, "NumLock 灯亮；旧冲刺/远攻/必杀/援助已删，键位改挂新技能",
                  left.x + 20, 596, 14, COL_DIM)

        # 右半：触屏键位 + 技能说明
        right = pygame.Rect(660, 140, 580, 500)
        draw_panel(s, right, COL_PANEL, COL_PANEL_LIGHT, 12, 1)
        draw_text(s, "触屏按键（左右各一套，位置对称）", right.x + 20, 154, 22, COL_P2, True)
        rows2 = [
            ("摇杆", "左右移动，上＝上挑，下＝防御；底盘不动"),
            ("普攻 大圆", "连击起手，键面标 J / 1；已放大"),
            ("3 个技能圆", "键面写专属短名 + 键盘键名，CD 变暗"),
            ("金色奥义圆", "耗 2 格气、CD 长，键面标 L / 3"),
            ("跳 横胶囊", "起跳可越过对手绕背，标 K / 2"),
            ("闪避", "小位移 + 短无敌，CD 约 1.2 秒（可改）"),
            ("净化", "解定身 / 催眠 / 沉默；秘卷设置页可换"),
            ("PVE 电脑", "远了放远程技并靠近，近身连招，被控净化"),
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
        draw_text(s, "v3.5：开局不再自动冲与发弹 · 奥义不再自动放 · 地面不能穿人，空中可跳过绕背",
                  SCREEN_W // 2, 640, 15, COL_GOLD, align="center")
        draw_text(s, "点左上「返回主页面」或按 Esc 退出  ·  诊断页点框内任意处关闭",
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
    # ---- v3.5：这轮修的 5 件事都进自检，防止回退 ----
    assert DODGE_CD <= 90, "闪避 CD 又被调回过长"
    # AI 必须返回元组动作，绝不能吐 None / 裸键码
    aa = App(selftest=True); aa.mode = MODE_PVE; aa.start_match()
    for _d in (560, 300, 120, 60):
        aa.p2.x = aa.p1.x + _d
        _held, _acts = ai_decide(aa.p2, aa.p1, 11)
        assert all(isinstance(x, tuple) and len(x) == 2
                   and x[0] in ACTION_ORDER and x[1] == 2 for x in _acts), _acts
        assert all(x is not None for x in _held), _held
    # None 混进 just 也不能再触发任何旧动作
    bb = App(selftest=True); bb.start_match(); bb.p1.rage = 300
    _before = (bb.p1.vx, len(bb.projectiles), bb.p1.ult_cd, bb.p1.pending_assist)
    bb.update(1.0/FPS, pygame.key.get_pressed(), {None})
    assert (bb.p1.vx, len(bb.projectiles), bb.p1.ult_cd, bb.p1.pending_assist) == _before
    # 战斗页能点到「输入诊断」（否则手机上诊断页退不出去）
    assert any(b[1] == "输入诊断" for b in aa.active_buttons()) or aa.scene != "game"
    cc = App(selftest=True); cc.mode = MODE_PVP; cc.start_match()
    assert any(b[1] == "输入诊断" for b in cc.active_buttons())
    # 中间按钮优先命中（PVP 两簇内移时也曾抢走点击）
    assert all(cc.hit_button(b[0].center) is b for b in cc.mid_btns)
    # 圆键放大后仍两两不相交、全部在画布内
    for _mirror in (False, True):
        _cl = build_skill_cluster(1, mirror=_mirror)
        _rounds = [b[0] for b in _cl if b[0].w == b[0].h]
        for i in range(len(_rounds)):
            assert 0 <= _rounds[i].left and _rounds[i].right <= SCREEN_W
            assert 0 <= _rounds[i].top and _rounds[i].bottom <= SCREEN_H
            for j in range(i+1, len(_rounds)):
                dx = _rounds[i].centerx - _rounds[j].centerx
                dy = _rounds[i].centery - _rounds[j].centery
                assert (dx*dx + dy*dy) ** 0.5 > (_rounds[i].w + _rounds[j].w) / 2.0 + 2
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
    "AAEAAAATAQAABAAwR0RFRhXoF5QAA6ZMAAAAQEdQT1MAGQAMAAOmjAAAABBHU1VCbIx0hQADppwAAAAaT1MvMnYwBBgAAAG4AAAAYGNtYXDF0KdtAAAmVAAAHZRjdnQgRJ1NcgAATXAAAAIQZnBnbXPTI7AAAEPo",
    "AAAHBWdhc3AABAAHAAOmQAAAAAxnbHlmhtSNYQAAdIQAAywIaGVhZBaZ+SMAAAE8AAAANmhoZWEPcQ7rAAABdAAAACRobXR450dQOwAAAhgAACQ6bG9jYQwaVfQAAE+AAAAlBG1heHAL6QKDAAABmAAAACBuYW1l",
    "lU2vyQADoIwAAAWUcG9zdP8DAGYAA6YgAAAAIHByZXBBvdqCAABK8AAAAn52aGVhFlYF2gADprgAAAAkdm10eAn89EMAA6bcAAASggABAAAAADMzDdaoM18PPPUCPwgAAAAAAMY/xrAAAAAA5xm0Nv/o/hQICAf4",
    "AAAACAAAAAEAAAAAAAEAAAd+/h0AAAgA/+j/8AgIAAEAAAAAAAAAAAAAAAAAAAjdAAEAAAlAAGYADQCIAA4AAgAQAC8AWgAAAh8BYwAEAAEAAwWTAZAABQAIBZoFMwAAAR4FmgUzAAAD0ABmAfIAAAILBgYDCAQC",
    "AgSAAAADCAH0YAAAABAAAAAAV1FZRgBAACD/XgYf/hQAhAd+AeMAEAAAAAAAAARKBbYAAAAgAAIIAAJYCAABUAQAAEgIAAFQBAAASAgAANgIAADYCAAA2AgAANgIAADYCAAA2AgAANgE0P/oBNAAuATQARgE0AC4",
    "BNAAgATQAJAE0ACwCAAAsAgAALAIAAHwCAAAAAgAADAIAAAwCAAEAAgAANgIAAQACAAB4AgABAAIAAGACAAAqAgAAHgIAACgCAAAoAgAAJAIAABYCAAAoAgAAJAIAABwCAAAiAgAAHgIAAB4CAAAUAgAAGAIAADg",
    "CAAA6AgAALAIAACwCAAAeAgAAHgIAACICAAAoAgAAHAIAABYCAAAyAgAAGgIAAB4CAABAAgAAJAIAAB4CAAA2AgAAGgIAABoCAAAcAgAAIAIAABgCAAAgAgAAGgIAABgCAAAWAgAAHAIAABYCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABYCAAAWAgAAFAIAABQCAAASAgAAQgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAaAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABoCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGgIAABQCAAAUAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAYAgAAJAIAABoCAAAcAgAAIAIAABo",
    "CAAAWAgAAGgIAACICAAAeAgAAGgIAABgCAAASAgAAGgIAADwCAAAcAgAAGAIAACICAAAaAgAAGgIAABoCAAAaAgAAGgIAAB4CAAAaAgAAHgIAABYCAAAaAgAAGAIAADQCAAA2AgAAIAIAACYCAAAsAgAAMgIAABw",
    "CAAAaAgAAIAIAAB4CAAAYAgAAEgIAABICAAAgAgAAJAIAACICAAAYAgAAGgIAAA4CAAAYAgAAEgIAACICAAAWAgAAHAIAAB4CAAAWAgAAIAIAABoCAAAaAgAAEgIAABwCAAAaAgAAFgIAACACAAAaAgAAFAIAADQ",
    "CAAAeAgAAIgIAACACAAAeAgAAIgIAABoCAABMAgAAJgIAAB4CAAAyAgAANAIAABYCAAAeAgAAFAIAABQCAAAUAgAAFAIAABQCAAAaAgAAGAIAACICAAAaAgAAGgIAABoCAAAUAgAAGgIAACYCAAAoAgAAKAIAAFI",
    "CAAAiAgAAHgIAADACAAAaAgAAGgIAACoCAAAWAgAAGgIAACgCAAAcAgAAFAIAADICAAAYAgAAFAIAACgCAAA4AgAAGAIAABwCAAAoAgAAFgIAACgCAAAaAgAAJAIAACACAAAWAgAAGAIAABICAAAsAgAAKAIAACg",
    "CAAAaAgAAKAIAACoCAAAqAgAAJgIAACoCAAAqAgAAKgIAACgCAAAWAgAAHAIAAC4CAAAuAgAAOAIAAC4CAAAuAgAALgIAAC4CAAAuAgAAMAIAADACAAAcAgAAEAIAABYCAAAWAgAAHAIAABYCAAAWAgAAFAIAABY",
    "CAAAWAgAAIAIAABoCAAAWAgAAFAIAACACAAAWAgAAFgIAABwCAAAcAgAAKAIAAB4CAAAgAgAAGAIAABICAAAWAgAAFgIAABgCAAAaAgAAHAIAABoCAAAUAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABY",
    "CAAAaAgAAGgIAAB4CAAAiAgAAFgIAABoCAAAmAgAAIAIAACACAAAeAgAAJgIAABwCAAAiAgAAGgIAACYCAAAYAgAAHAIAACQCAAAkAgAAIAIAABoCAAAcAgAAIAIAABoCAAAmAgAAEgIAACACAAAaAgAAGgIAABo",
    "CAAAaAgAAKgIAABYCAAAYAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGgIAABYCAAAeAgAAGgIAAEoCAAAaAgAARAIAADACAAAWAgAAJAIAACICAAAmAgAAIgIAABgCAAAmAgAAIAIAABwCAAASAgAAFAIAABQ",
    "CAAASAgAAFAIAABQCAAAUAgAAFAIAABgCAAAYAgAAHgIAAB4CAAAaAgAAJAIAADACAAAiAgAAIgIAACICAAAiAgAANgIAAD4CAAAgAgAAFgIAABoCAAAUAgAAFAIAABgCAAAYAgAAFgIAABgCAAAWAgAAFAIAABY",
    "CAAAWAgAAHAIAABoCAAAaAgAAFAIAABICAAASAgAAEgIAABICAAASAgAAFgIAABQCAAAUAgAAFgIAABQCAAAUAgAAFgIAABQCAAAYAgAAGgIAABYCAAAWAgAAGgIAABQCAAAaAgAAGgIAAB4CAAAiAgAAFgIAABo",
    "CAAAaAgAAFgIAABoCAAAWAgAAGgIAACgCAAAUAgAAFAIAABQCAAAWAgAAFgIAABQCAAAUAgAAFgIAABQCAAAWAgAAFgIAABYCAAAYAgAAFgIAABYCAAAUAgAAGAIAABgCAAAUAgAAFAIAABYCAAAYAgAAFAIAABQ",
    "CAAAUAgAAFgIAABQCAAAWAgAAGAIAABYCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAeAgAAFAIAABgCAAAUAgAAEAIAABgCAAAUAgAAGAIAABYCAAAWAgAAEAIAABgCAAAYAgAAGAIAABACAAAWAgAAEAIAABg",
    "CAAAYAgAAGAIAABgCAAAYAgAAGAIAABYCAAAYAgAAFgIAABgCAAAYAgAAFgIAABYCAAAWAgAAGAIAABgCAAAYAgAAFgIAABYCAAAWAgAAFgIAABgCAAAiAgAANAIAACQCAAAaAgAAFgIAABICAAAaAgAAFAIAABo",
    "CAAAeAgAAGgIAABQCAAAUAgAAMAIAABYCAAAcAgAAIAIAACoCAAAWAgAAIAIAABQCAAAcAgAALAIAAFgCAABEAgAAHgIAACYCAAAuAgAAGAIAABoCAAAkAgAAFAIAABwCAAAkAgAAGgIAABoCAAAkAgAAJAIAACI",
    "CAAAWAgAAGgIAAD4CAAAeAgAAGgIAABoCAAAeAgAAFgIAABoCAAAaAgAAFgIAABYCAAAWAgAAIgIAACQCAAAMAgAAJAIAAAwCAAAMAgAAEgIAABYCAAAgAgAAFAIAABICAAASAgAADAIAABoCAAAYAgAAGAIAABg",
    "CAAAeAgAAEgIAABICAAASAgAAEgIAABICAAAUAgAAEgIAABQCAAAYAgAAGAIAABICAAAUAgAAFAIAABICAAASAgAADgIAABQCAAAUAgAAEgIAABQCAAAOAgAAGgIAABwCAAAaAgAAGgIAABoCAAAWAgAAIAIAABI",
    "CAAAWAgAAEgIAABwCAAAkAgAAGgIAAEICAAAiAgAAHgIAABYCAAAcAgAAGAIAABYCAAAWAgAAGgIAABoCAAAaAgAAFgIAABoCAAAaAgAAFgIAABgCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABY",
    "CAAAWAgAAGAIAABgCAAAYAgAAFgIAABYCAAAYAgAAFgIAABYCAAAWAgAAFgIAABgCAAAYAgAAFgIAABYCAAAWAgAAFgIAABoCAAASAgAAGgIAABICAAAcAgAAFAIAABgCAAAaAgAAGgIAABYCAAAaAgAAGgIAABY",
    "CAAAaAgAAGgIAABoCAAASAgAAEgIAABYCAAAUAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAHAIAABoCAAAaAgAAGgIAABoCAAAaAgAAGAIAACACAAAWAgAAFgIAAEACAABEAgAANAIAAB4CAAAYAgAAOgIAACY",
    "CAAAQAgAAEgIAABICAAAQAgAAGgIAAEQCAAAqAgAAGgIAABoCAAAaAgAAGgIAABQCAAAaAgAAGgIAAFQCAAAkAgAADAIAACQCAAAaAgAAGgIAABQCAAAeAgAAKAIAACgCAAAaAgAAKAIAACICAAAiAgAAIgIAABg",
    "CAAAWAgAAFgIAABQCAAAUAgAAEgIAAA4CAAAUAgAAEgIAABQCAAAOAgAAEAIAABICAAAaAgAAGgIAABoCAAASAgAAFgIAACQCAAASAgAADgIAAA4CAAAWAgAAFgIAAA4CAAAOAgAAFgIAABICAAASAgAAJgIAABg",
    "CAAAcAgAAGgIAACACAAAaAgAAIAIAABoCAAAeAgAAGgIAABoCAAAUAgAAGAIAABoCAAAaAgAAGAIAABoCAAAaAgAAGgIAABwCAAAaAgAAGgIAABQCAAAcAgAAFAIAABYCAAAWAgAAFgIAABoCAAAaAgAAHAIAABw",
    "CAAAWAgAAHAIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAFgIAADI",
    "CAAAeAgAAHgIAABoCAAAWAgAAFAIAABQCAAAYAgAAHAIAABICAAAaAgAAGAIAABQCAAAUAgAAFAIAACQCAAAWAgAAFAIAACICAAAUAgAAGgIAABQCAAAUAgAAEAIAABYCAABIAgAAJAIAABgCAAAgAgAAGgIAAB4",
    "CAAAeAgAAGgIAAB4CAAAgAgAAGgIAABoCAAAgAgAAHgIAAB4CAAAaAgAAGgIAACACAAAaAgAAGgIAAB4CAAAeAgAAIAIAACACAAAUAgAAFgIAABQCAAAYAgAAFgIAABICAAAUAgAAGAIAABICAAASAgAAGgIAABQ",
    "CAAAQAgAAEgIAABICAAAeAgAAFgIAABoCAAAmAgAAGgIAABoCAAASAgAAIAIAABoCAAAQAgAAGAIAABgCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAcAgAAHAIAACQCAAAaAgAAGAIAABwCAAAaAgAAHAIAABgCAAAgAgAAGAIAABgCAAAYAgAAEgIAABoCAAASAgAAEgIAABICAAAcAgAAFAIAABQ",
    "CAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAYAgAAEgIAABICAAAaAgAAGgIAABoCAAAaAgAAHAIAABoCAAAaAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABg",
    "CAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABoCAAAeAgAACgIAABoCAAAaAgAAEAIAACICAAAcAgAAGAIAABoCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAASAgAAFAIAABQCAAAcAgAANAIAADQCAAA0AgAANAIAADQCAAA0AgAANAIAACoCAAAqAgAAKgIAACgCAAAqAgAAKAIAACgCAAAoAgAAKgIAACICAAAoAgAAIgIAACg",
    "CAAAoAgAAFgIAABgCAAAeAgAAIgIAABgCAAAYAgAAGgIAABoCAAAYAgAAGgIAABoCAAAaAgAAGgIAACACAAAaAgAAGgIAABYCAAAUAgAAGAIAABoCAAAcAgAAFAIAABQCAAAYAgAAFgIAABgCAAAWAgAAJAIAABo",
    "CAAASAgAAEgIAABICAAAUAgAAGgIAABoCAAA2AgAAIAIAABoCAAAgAgAAIAIAACACAAAcAgAAGAIAABQCAAAWAgAAGAIAABgCAAA6AgAAFAIAABgCAADgAgAAugIAAGgCAACUAgAAPAIAAG4CAADoAgAAxAIAAIg",
    "CAAB0AgAAjAIAAFQCAABKAgAAWAIAAIQCAACMAgAApgIAAI4CAACMAgAAeAIAAJICAACMAgAAigIAAI4CAACMAgAAagIAAGICAACMAgAAjAIAAIwCAACOAgAAPgIAAFoCAACIAgAAcgIAAHoCAACMAgAAjAIAAGg",
    "CAAB0AgAAigIAAIACAACIAgAAoAIAAFQCAABoAgAAWAIAAJICAABYAgAAhAIAAIACAABmAgAAbAIAAFoCAAAiAgAAYAIAAGQCAAB2AgAAzgIAAIQCAACkAgAAggIAAAACAADEAgAAigIAAIwCAACUAgAAdgIAAII",
    "CAACEAgAAdgIAAIYCAACSAgAAhAIAAJoCAACUAgAARAIAAIYCAAB+AgAAjAIAAHYCAACmAgAAmgIAAIwCAACGAgAAcAIAAEYCAAB0AgAAcAIAAJQCAACaAgAA7gIAAIoCAACMAgAAQgIAABoCAAAYAgAAGAIAAB4",
    "CAAD6AgAAagIAAKQCAACeAgAAigIAAKACAACYAgAAtAIAAJICAACcAgAAkgIAAJoCAACiAgAAngIAAKYCAACWAgAApAIAALYCAACcAgAAIAIAAPwCAAD2AgAAbAIAACICAAEEAgAAGgIAAOoCAAAoAgAAGgIAABg",
    "CAACEAgAAFAIAAGYCAAAaAgAAUgIAACICAACcAgAALAIAACICAADKAgAAGgIAAB4CAAAaAgAAHgIAAMACAAAkAgAAFAIAAB4CAADsAgAAGgIAABoCAABAAgAAGgIAABgCAAAUAgAAQAIAAEACAAA8AgAAHAIAACw",
    "CAAAUAgAAQAIAABwCAAAaAgAAIAIAAJICAAA6AgAAKAIAABoCAAAYAgAATgIAAEoCAABeAgAAwgIAACgCAAAeAgAAPgIAABoCAAAcAgAARAIAANICAAAgAgAAHgIAAB4CAACWAgAAqAIAANoCAABsAgAAGgIAACA",
    "CAAAaAgAAFAIAAGYCAAAiAgAANAIAAIgCAAB+AgAAsAIAACICAABOAgAA1gIAAFwCAABiAgAAjgIAAH4CAACAAgAAhAIAABgCAAAWAgAAGgIAAHQCAAB4AgAAhAIAAFYCAABwAgAATAIAABwCAAAgAgAAJAIAAFQ",
    "CAAAaAgAAIgIAAGACAAAgAgAAGgIAACICAABKAgAAIgIAABgCAAAgAgAAJgIAAGACAABeAgAAkAIAAKICAABkAgAAbAIAAGYCAAB6AgAAggIAADICAAAiAgAAYAIAAKgCAAAiAgAAqgIAAI4CAAAWAgAAHAIAALg",
    "CAAAiAgAAwAIAAN4CAADeAgAAxAIAANACAADaAgABQAIAABgCAAC8AgAAhgIAAKwCAAAOAgAArgIAANICAACgAgAAGgIAABoCAAC2AgAAGgIAABgCAAAWAgAAGAIAABoCAAAcAgAAqAIAAKoCAADIAgAAFAIAACI",
    "CAADUAgAAGAIAAKACAACqAgAAfgIAAH4CAACqAgAAugIAAKgCAAFgAgAAFgIAAMwCAACwAgAAKAIAABACAADGAgAAIgIAARICAACqAgAAlgIAABoCAAAWAgAAsgIAABYCAAAWAgAAGgIAAJgCAAB2AgAAWAIAALw",
    "CAACkAgAAHgIAABICAAASAgAATAIAAIQCAAAgAgAAHAIAACACAAAWAgAAqgIAAJICAADQAgAAvgIAAJoCAAC2AgAAKgIAAHYCAAC6AgAAJgIAABoCAAESAgAAogIAACACAAEKAgAAIAIAAHACAAC+AgAAwAIAAKw",
    "CAACwAgAAvgIAABoCAAAcAgAAUAIAAFYCAAAcAgAANAIAABYCAAC2AgAA6AIAAM4CAAAWAgAAyAIAANwCAAAgAgABHgIAANgCAACYAgAAogIAAJACAACWAgAArgIAAKoCAAD+AgAAKAIAACgCAAAoAgAAKgIAALI",
    "CAAAqAgAAKAIAADACAAAaAgAA0gIAACACAAAaAgAAQgIAAMgCAAASAgAA2gIAABYCAAAUAgABJgIAAJ4CAACqAgAAvgIAANYCAAAYAgAAogIAAK4CAACEAgAAKgIAALwCAACUAgAAwAIAAIICAADWAgAAuAIAALo",
    "CAACyAgAArAIAANQCAADOAgAAugIAAL4CAAAaAgAA5AIAAKoCAACwAgAAwAIAAMICAACmAgAAvAIAALICAAEAAgAAqAIAACACAAAaAgAAJAIAAB4CAADoAgAAJAIAABICAADCAgAAGAIAAIoCAACEAgAASgIAAOo",
    "CAACOAgAAkAIAAJgCAAC4AgAAGgIAAIICAAFaAgAACgIAAB4CAACoAgAAkgIAALQCAACEAgAAEgIAAKQCAACeAgAAsgIAAL4CAACAAgAAvAIAAIwCAADkAgAAVgIAAC4CAADWAgAApgIAAJQCAACoAgAAHgIAACo",
    "CAACoAgAAlAIAAL4CAADGAgAApAIAAMACAAAcAgAArgIAANgCAABuAgAAqgIAAQwCAADSAgAAtAIAABgCAAC4AgAAvAIAAJQCAAASAgAAqgIAAIICAACGAgAAGgIAAJICAAC2AgAAjAIAAOICAADEAgAAtAIAAI4",
    "CAAAeAgAADgIAABoCAAAYAgAAKAIAAJ4CAADaAgAAwAIAAOoCAAByAgAAjAIAAJ4CAACcAgABBAIAABICAACcAgAAmAIAAB4CAACuAgAAsAIAAKwCAAAkAgAAegIAAJACAAC0AgAAogIAABICAADkAgAAyAIAACA",
    "CAAAmAgAA6gIAAL4CAACsAgAA/AIAAPQCAAAaAgABBgIAACACAAAgAgAA5AIAANACAACaAgAAmgIAAOICAAC4AgAALgIAAJoCAAAaAgAA3AIAABwCAAC+AgAAEAIAAL4CAADOAgAA4AIAAOwCAABCAgAALAIAABw",
    "CAADAAgAAjgIAABwCAAA0AgAA0gIAALwCAAAaAgAAyAIAABICAAD+AgAAJAIAAMgCAABQAgAAegIAAJYCAAAkAgAAIAIAATQCAAAUAgAAuAIAABICAAAaAgAAagIAAB4CAAAeAgAAsAIAAGACAAAYAgAAxAIAAMA",
    "CAADmAgAAFgIAALgCAADCAgABJgIAALQCAAAYAgAAggIAABICAADkAgAAGAIAABgCAAAWAgAAKAIAALYCAADKAgAAqAIAAM4CAACEAgAAZAIAABoCAADWAgAAXAIAANICAAAYAgAAqAIAAMICAAAaAgAAEgIAABo",
    "CAAAeAgAAFgIAAL4CAACuAgAAsAIAANICAAEwAgAAuAIAAEYCAAAUAgAAfgIAABoCAAAaAgAAzAIAABYCAAAWAgAAzAIAAOoCAAAoAgAAHAIAALoCAAAYAgAAKgIAAKQCAADoAgAAhAIAAQACAACuAgAAKAIAAB4",
    "CAAASAgAAHAIAAFQCAAD4AgAAFAIAABwCAACKAgAAHgIAAUICAAAgAgAAGAIAALQCAAEaAgAAiAIAANoCAADOAgAAuAIAAIYCAADYAgAArAIAAOwCAABgAgAAFAIAAFoCAAAWAgAAdgIAABgCAADAAgAAKAIAADA",
    "CAADGAgAAGgIAAPoCAADuAgAA9AIAABYCAAC4AgAAFgIAACoCAAAaAgAAHAIAABgCAAD0AgABCAIAABoCAAC2AgAA3AIAAMoCAACiAgAAwgIAAMQCAAAUAgAAFAIAAOQCAAASAgAA1AIAABICAACsAgAAPAIAAJw",
    "CAACqAgAAxAIAACoCAADMAgAArgIAACYCAAAgAgAAIAIAALoCAACYAgAAGgIAAHQCAABwAgAAqgIAAMYCAAC6AgAA7AIAABYCAAC4AgAAGgIAACACAAAcAgAAVgIAACoCAADwAgAAIAIAACACAAAaAgAA2gIAAKg",
    "CAADkAgAAtgIAACYCAADEAgAAuAIAAOoCAADaAgABDAIAACACAAAYAgAAGAIAAMoCAACiAgAAwgIAAJwCAABwAgAAjgIAAPwCAADeAgAA4AIAABYCAABqAgAAIgIAAOgCAAAaAgAAHgIAACACAAC4AgAAkAIAAJQ",
    "CAAAWAgAA6gIAACACAACoAgAA5AIAAQACAAAcAgAAIgIAABwCAADGAgAArAIAABYCAAAmAgAAUgIAABoCAABAAgAAHAIAAGQCAABsAgAAdgIAABQCAACwAgAAIgIAABoCAAAaAgAAugIAACwCAADKAgAAGgIAADQ",
    "CAACqAgAAJgIAAHoCAAAWAgAAyAIAAMwCAAA2AgAALAIAABYCAAEyAgAAtAIAABICAAASAgAAlAIAAMYCAAAaAgAAqgIAAKwCAAFAAgAAFgIAANgCAAAaAgAAEgIAAKgCAAB6AgAAGgIAABoCAAC2AgAAtgIAABo",
    "CAADIAgAAGAIAABYCAAAcAgAAzAIAABoCAAAUAgAAHgIAABICAADiAgAAFAIAALQCAACYAgAAFAIAABYCAAAgAgAAmgIAABACAAAQAgAAFAIAABoCAAAWAgAAZAIAASQCAAEaAgAAGgIAABwCAACqAgAAfgIAAIo",
    "CAACYAgAAvAIAAHQCAAA8AgAAkgIAAQoCAADsAgAA7gIAABQCAADcAgAAPAIAABQCAAAUAgAAFAIAABQCAAAWAgAAHAIAAPICAAAaAgAAGgIAABoCAAAaAgAAbgIAAEQCAACQAgAAGgIAAMYCAACoAgAAHgIAACI",
    "CAABWAgABNAIAAIQCAACwAgAAkAIAABwCAAAqAgAAKgIAAMACAADaAgAA0gIAABQCAADAAgAAyAIAABoCAAASAgAAHAIAAIYCAAASAgAAMAIAACICAAEqAgAAIAIAABwCAACeAgAAogIAABICAAC4AgAAFAIAAJg",
    "CAACuAgAAGgIAABoCAAD0AgAAJAIAABgCAACoAgAAtgIAACoCAAASAgAAFAIAABICAAASAgABDgIAABICAAAWAgAAFgIAABoCAAASAgAAJgIAABYCAAAWAgAAFAIAAPYCAAEoAgAA8gIAANwCAAAUAgAAzgIAAKw",
    "CAADEAgAAqgIAAJACAADAAgAAoAIAAYgCAAAiAgAAmgIAAJ4CAAAcAgAAgAIAAMwCAACiAgAA5AIAATYCAAAmAgAAGgIAACYCAACOAgAAFAIAAKQCAACeAgAAHAIAABwCAAAUAgAA4AIAABQCAAAaAgAA5gIAABQ",
    "CAACMAgAA6gIAABoCAADaAgABDAIAAVwCAADWAgAAzAIAALgCAADmAgAAmgIAAKICAAEAAgAAFAIAABYCAAD4AgABMAIAABQCAAEQAgAAyAIAABYCAADKAgAAFgIAALoCAAAaAgAAGgIAABoCAAAYAgAAFgIAAKA",
    "CAADQAgABIAIAASACAAA8AgAAIgIAAGQCAAAqAgAAHAIAABQCAAAaAgABCgIAAOwCAADAAgAAGAIAABwCAAAaAgAAFAIAABQCAACKAgAArgIAAMICAACwAgAAvAIAABYCAAAWAgAAnAIAAC4CAAAgAgAAkAIAABQ",
    "CAAC2AgAAuAIAABQCAAAaAgAA5gIAAVYCAAAYAgAAKgIAAJwCAAAmAgAAGAIAAC4CAAAaAgAAogIAABoCAAAYAgAAHgIAAPACAAAWAgAApgIAALYCAACaAgAAGgIAABoCAAAoAgAAyAIAAMwCAACCAgAApAIAABo",
    "CAAAsAgABBgIAABYCAAAcAgAAJgIAAA4CAAB0AgAAFAIAABQCAADEAgABHgIAAUICAADCAgAAFAIAABoCAADmAgAAGgIAAHwCAACOAgAAFgIAAQACAAAUAgAA5AIAAMICAAASAgAAGgIAABoCAABWAgABYgIAAKw",
    "CAACAAgABWgIAABQCAAAWAgAAwAIAABICAACyAgAAGAIAARICAABsAgAAjAIAAWwCAAAWAgAARgIAABgCAAAaAgAAHgIAAQACAACIAgAAEAIAANgCAAASAgAAoAIAAAwCAAE4AgAAGgIAABQCAACyAgAAHgIAAHQ",
    "CAAAWAgAAugIAAKoCAAC2AgAAEgIAANoCAAAaAgAAIAIAACACAAAaAgABFgIAACACAAAmAgAAwgIAACICAAAkAgAAVgIAAJgCAAAUAgAAFgIAABQCAAAaAgAA3AIAABoCAADSAgABRAIAACQCAADaAgAA7AIAABg",
    "CAAAWAgAAFgIAAB4CAAAwAgAAIgIAABoCAAAaAgAAGgIAABoCAAAUAgAAFAIAABQCAAAUAgAAGgIAABoCAAAgAgAAJAIAACgCAAC2AgAAxgIAAIwCAAAYAgAAlgIAACICAAAiAgAAugIAAKYCAAASAgAAxAIAABY",
    "CAACMAgAADgEzQAAAecBHQAtAAAAPQHwAScBKQCFAJgBuAEdAc8A0wCTAOEAngCDAD0ArACaAI8AnACaAecBmgCYAJgAmACoAB8AIQCHAIEAhwDZAPQAdQCHAOEAiQDTAOkAcQCHAFQAsABUALoAjQBmAH0AIQAC",
    "ADUAIQBmAZwA0wEh//ABogCHAJ4ArACJAIUAnABmAKAAxQCHANcAvABcAKAAcwCeAIkBCADLAIsAoABS//wAYABSALYA4QIbAOMAmAFcAecAvv/6AE4ARgCYAAAAAAACAAAAAwAAABQAAwABAAAAFAAEHYAAAAdc",
    "BAAACQNcACMAXQB+ALIAtwDXIBQgJiGTIh4iSCRmJYglsiW2JbwlwCXGJc8mBicTMAIwDTARTgBOB04LTg5OFE4cTiJOJU4qTi1OMk40TjtORU5JTktOTk5ZTl1OYE5mTnFOhk6JToxOjk6STpROm06kTqdOrk66",
    "TsBOxk7OTtNO1k7lTuxO9077Tv1PEU8YTxpPIE8kTzhPPE9GT09PU09VT1lPXE9gT39Pi0+bT51Pp0+/T91P4U/uUA1QElAZUDxQPlBHUE9QWlBcUHZQf1CoUKxQu1DPUPVRQ1FJUU1RXFFlUWhRbVFxUXNReFF8",
    "UYVRjVGZUbNRtVG3UbtRwFHGUc9R0VHgUe1R9lH7Uf1SAFIDUgdSElIXUhlSG1IdUiBSJFIrUjBSN1I7Uk1SVFJqUohSm1KhUqlSv1MFUxZTOlNBU0NTR1NKU1VTV1NhU2tTcFN0U3dThlOLU5pTn1O7U8JTyFPK",
    "U81T0VPYU+BT5FPsU/BT81P3VARUCFQOVBFUJlQsVC9UOFRGVEhUWFRoVH1UjFTBVMhUzVTlVOpVJFUvVUZVglWKVdxWNFZoVspW21beVuBW4lb0VvpW/lcGVwhXI1coVzBXOldAV0dXUVdXV4JXi1ffV/pYXliD",
    "WJ5ZBFkHWQ1ZFlkaWRxZH1knWSpZLlkxWTRZT1lRWVdZZVlzWXZZfVnLWdBZ/1oYWsxbUFtYW2Zbg1uJW4xbmFuaW55bolukW6pbs1u2W7lbvVv5W/xcBFwPXBFcFFwWXBhcHVwxXDpcPlxAXEJcRVxPXF5dKV1M",
    "XeZd6F3uXfJeA14nXjheRV5VXnNedl6PXpVel16mXq1e9l76XwBfAl8PXxVfIF8nXzpfU19VX2JfcV97X4BfhV+LX5dfoV+qX65fvV/DX8Vf11/rX/1gAWAOYBJgHWAnYDtgUmBiYG9gxWDvYPNhCGEPYR9hYmIS",
    "YhZiGGIqYjRiN2JAYkdiS2JNYlNiWGJbYmNiZ2JpYmticGKAYoRiimKTYpVimGKbYqJipWKsYrFitWLGYslizWLSYtZi22LfYuli7GLxYv9jAmMHYwljEWMhYyRjKGMqY19jYmNuY3djiWOSY6BjpWOoY7dj0GPS",
    "Y/RkHGQeZC1kR2RKZHhknmSkZK1kxWTOZRJlL2U2ZTllO2U+ZUhlTGVPZWNlcGV0ZYdli2WXZZxlp2WpZa1lsGW5Zctl4GXiZeVl52XpZfZmDmYTZiBmL2Y+Zlpmb2aCZpdmtGb0ZwBnCWcNZx1nH2csZy9nNWc6",
    "Z0BnQ2dGZ1BnX2dhZ2Vnf2eBZ4RnnGe2Z9Bn02flaAdoD2ghaDloPGhGaEhoTGhjaGVodmivaMBpLWnMaf1qIWoqallrIWs+a2Vre2uLa7VrzWvPa9Jr1GwUbDRsOGxCbEdsSWyJbKFsv2zJbNVs4mzobPxtO20+",
    "bUFtS21PbW5td22Ibaht4W3xbfduBW4QbiFuMm44bpBu0W7abt5u4W7kbwJvFG/AcGtwb3B1cK5wuXDfcO1xNnFncgZyKnIxckhyTHJZcmlyeXKvcrZy0HLscvhzHHMrc4dzqXOwdAN0BnT3dR91KXUydTV1O3VM",
    "dVl1ZXWXdat11XZ7dn12hHbGdsp2z3bSdtZ22HbudvR2+Xb+dwF3C3cgdzx3QHdbd2F3rHezd+V36XfteAF4FHg0eDh4QHhseG54l3iweL55Onk8eT55XnmBebt5wXnNedJ52Hnweft6C3ozej96enp/eoF6l3qd",
    "est61nrZeuB673sbeyZ7LHtJe1R7Vnt+e4B7l3uhe617x3wHfHN8e3ySfMp833z7fSB9In0nfSt9L36ifqd+r365fr9+xH7Ifs9+037Vftl+3X7ffud+6X7tfwB/E38Wfxh/KX86f1F/aX9uf45/+4ABgAOABYAM",
    "gBeAM4BMgFSAWoClgMyA3ID2gP2BEYEagTiBcIF/gcKB6oH0ggyCcoKCgrGCz4LlgwODNoNQg7eD3IQlhD2EuITEhN2Fz4ZRhlqGy4eDh/mIQIhFiEyIYYhliGiIcIiNiKuIwojFiNmI+Il/iYGJhonCicSJxonJ",
    "idKJ44nmigCLoYuki6mLrouwi7KLuou/i8GLyovNi9GL1Yvdi+WL7Yvvi/SL+4wBjAOMYYxqjR+NI40mjSiNL400jTmNRI1LjVSNVo1wjXeNhY2KjbONw43Rjd2N343oje+N844pjquOso66j2iPbI9uj3uPfY+R",
    "j5OPqI+5j8WPx4/Rj9SP2Y/cj9+P94/9kAKQCZAQkBKQGpAgkDuQTZBTkG6Qf5CjkOiQ/ZFNkZKRypHNkc+R0ZSIlJ+UrpTBlPaU+pUBlQuVGZUulVyVf5XoleqV7pX0lgGWCJYfljKWNpZFlk2WUJZklmmWkJaU",
    "lr6Wxpb2lwCXB5cylziXUpdZl16XYJdil/OYdph7mH+YhJiYmJ2YzpjYmN+ZbZlwmYiZj5mWmZmabJpxmnuaf5qMmqia2Jx8nLieIZ7RntifIJ9Qn5n/Xv//AAAAIAAlAF8AsgC3ANcgFCAmIZAiHiJIJGAliCWy",
    "JbYlvCXAJcYlzyYFJxMwADAKMBBOAE4HTglODU4TThxOIk4kTipOLU4yTjROOk5FTkhOS05OTllOXU5fTmZOcU6GTolOi06OTpJOlE6bTqROp06uTrpOv07FTs1O007WTuNO7E72TvtO/U8RTxhPGk8gTyRPOE88",
    "T0ZPTU9TT1VPWU9cT2BPf0+LT5tPnU+nT79P3U/hT+5QDVASUBlQPFA+UEdQT1BaUFxQdlB/UKhQrFC7UM9Q9VFDUUhRTVFcUWVRaFFtUXFRc1F2UXxRhVGMUZlRslG1UbdRu1HAUcZRz1HRUeBR7VH2UfpR/VIA",
    "UgNSBlISUhdSGVIbUh1SIFIkUitSMFI2UjpSTVJUUmlSiFKbUp5SqFK/UwVTFlM6U0FTQ1NHU0pTVVNXU2BTa1NwU3NTd1OGU4tTmlOfU7tTwlPIU8pTzFPRU9ZT4FPjU+pT71PzU/dUA1QIVAxUEFQmVCtUL1Q4",
    "VEZUSFRYVGhUfVSMVMFUyFTNVOVU6lUkVS9VRlWCVYpV3FY0VmhWylbbVt5W4FbiVvRW+lb+VwZXCFcjVyhXMFc6V0BXR1dPV1dXgleLV99X+lheWINYnlkEWQdZDVkWWRpZHFkfWSdZKlkuWTFZNFlPWVFZV1ll",
    "WXNZdll9WctZ0Fn/WhhazFtQW1dbZluDW4hbjFuYW5pbnlugW6RbqluzW7ZbuVu9W/hb/FwEXA9cEVwUXBZcGFwdXDFcOlw+XEBcQlxFXE9cXl0pXUxd5V3oXe5d8V4DXiZeOF5FXlVecl52Xo9ek16XXqZerV72",
    "XvpfAF8CXw9fFV8gXydfOV9SX1VfYl9xX3tfgF+EX4tfl1+hX6pfrl+9X8NfxV/XX+tf/WABYA5gEmAdYCdgO2BSYGJgb2DFYO9g82EIYQ9hH2FiYg9iFmIYYipiNGI3Yj9iR2JLYk1iU2JYYltiY2JnYmlia2Jw",
    "Yn5ihGKKYpNilWKYYptiomKkYqxisWK1YsViyWLNYtJi1mLbYt9i6WLsYvFi/WMBYwdjCWMRYyFjJGMoYypjX2NiY25jd2OJY5JjoGOlY6djt2PPY9Jj9GQcZB5kLWRGZEpkeGSeZKRkrWTFZM1lEmUvZTZlOWU7",
    "ZT5lSGVMZU9lY2VwZXRlh2WLZZdlnGWnZallrWWwZblly2XgZeJl5WXnZell9mYOZhNmH2YvZj5mWmZuZoJmlma0ZvRm/mcIZw1nHWcfZypnL2c1ZzpnQGdDZ0ZnUGdfZ2FnZWd/Z4FnhGecZ7Zn0GfTZ+VoB2gP",
    "aCFoN2g8aEZoSGhMaGNoZWh2aK9owGktacxp/WohaipqWWsgaz5rYmt7a4trtWvNa89r0mvUbBRsNGw4bEJsR2xJbIlsoWy/bMls1WzhbOhs/G07bT5tQW1LbU9tbm13bYhtqG3hbfFt924FbhBuIW4ybjhukG7R",
    "btpu3m7hbuRvAm8Ub8Bwa3BvcHVwrnC5cN9w7XE2cWdyBnIqcjFyR3JMcllyaXJ5cq9ytnLQcuxy+HMbcytzh3Opc690A3QGdPd1H3UodTF1NXU7dUx1WXVldZd1q3XVdnt2fXaEdsZ2ynbPdtF21nbYdu529Hb4",
    "dv53AXcLdx93PHdAd1t3YXesd7N35Xfpd+14AXgUeDR4OHhAeGx4bniXeLB4vnk6eTx5PnleeYF5u3nBec150nnYee95+3oLejN6P3p6en96gXqXep16y3rWetl64Hrvext7Jnsse0l7VHtWe357gHuXe6F7rXvH",
    "fAd8c3x7fJJ8ynzffPt9IH0ifSd9K30vfqJ+pn6vfrd+v37Dfsh+z37TftV+2H7dft9+537pfu1/AH8TfxZ/GH8pfzp/UX9pf25/jn/7gAGAA4AFgAyAF4AzgEyAVIBagKWAzIDcgPaA/YERgRqBOIFwgX+BwoHq",
    "gfOCDIJygoKCsYLPguWDA4M2g1CDt4PchCWEPYS4hMSE3YXPhlGGWobLh4OH+YhAiEWITIhhiGWIaIhwiI2Iq4jBiMWI2Yj4iX+JgYmGicGJxInGiciJ0onjieaKAIuhi6SLqYuti7CLsou6i76LwYvKi82L0YvV",
    "i92L5Yvti++L9Iv7jAGMA4xhjGqNH40jjSWNKI0vjTSNOY1EjUuNVI1WjXCNd42FjYqNs43DjdGN3Y3fjeiN743zjimOq46yjrqPaI9sj26Pe499j5GPk4+oj7mPxY/Hj9CP1I/Yj9uP3o/3j/2QAJAJkA+QEpAa",
    "kB+QO5BNkFOQbpB/kKOQ6JD9kU2RkpHKkcyRz5HRlIiUn5SulMGU9pT6lQCVC5UZlS6VXJV/leiV6pXtlfSWAZYIlh+WMpY0lkSWTZZQlmSWaZaPlpSWvpbGlvaXAJcHlzKXOJdSl1mXXpdgl2KX85h1mHmYfpiE",
    "mJeYnJjOmNiY3pltmXCZiJmPmZaZmZpsmnGae5p/moyaqJrYnHycuJ4hntGe2J8gn1Cfmf8B//8IvAi7CLoIhwiDCGTpKOkX3nHnIOb326XahNpb2ljaU9pQ2kvaQ9oO2QLQFtAP0A2yH7IZshiyF7ITsgyyB7IG",
    "sgKyALH8sfux9rHtseux6rHosd6x27HasdWxy7G3sbWxtLGzsbCxr7GpsaGxn7GZsY6xirGGsYCxfLF6sW6xaLFfsVyxW7FIsUKxQbE8sTmxJrEjsRqxFLERsRCxDbELsQiw6rDfsNCwz7DGsK+wkrCPsIOwZbBh",
    "sFuwObA4sDCwKbAfsB6wBa/9r9Wv0q/Er7GvjK8/rzuvOK8qryKvIK8crxmvGK8WrxOvC68Frvqu4q7hruCu3a7ZrtSuzK7Lrr2usa6prqaupa6jrqGun66VrpGukK6Pro6ujK6JroOuf656rniuZ65hrk2uMK4e",
    "rhyuFq4BrbytrK2JrYOtgq1/rX2tc61yrWqtYa1drVutWa1MrUitOq02rRutFa0QrQ+tDq0LrQetAKz+rPms96z1rPKs56zkrOGs4KzMrMisxqy+rLGssKyhrJKsfqxwrDysNqwyrBusF6veq9SrvquDq3yrK6rU",
    "qqGqQKoxqi+qLqotqhyqF6oUqg2qDKnyqe6p56neqdmp06nMqcepnamVqUKpKKjFqKGoh6giqCCoG6gTqBCoD6gNqAaoBKgBp/+n/afjp+Kn3afQp8Onwae7p26naqc8pySmcaXupeil26W/pbuluaWupa2lqqWp",
    "pailo6WbpZmll6WUpVqlWKVRpUelRqVEpUOlQqU+pSulI6UgpR+lHqUcpROlBaQ7pBmjgaOAo3ujeaNpo0ejN6MroxyjAKL+ouei5KLjotWiz6KIooWigKJ/onOibqJkol6iTaI2ojWiKaIbohKiDqILogah+6Hy",
    "oeqh56HZodSh06HCoa+hnqGboY+hjKGCoXmhZqFQoUGhNaDgoLegtKCgoJqgi6BJn52fmp+Zn4iff599n3afcJ9tn2yfZ59jn2GfWp9Xn1afVZ9Rn0SfQZ88nzSfM58xny+fKZ8onyKfHp8bnwyfCp8HnwOfAJ78",
    "nvme8J7unuqe357entqe2Z7SnsOewZ6+nr2eiZ6HnnyedJ5jnlueTp5KnkmeO54kniOeAp3bndqdzJ20nbKdhZ1gnVudU508nTWc8pzWnNCczpzNnMucwpy/nL2cqpyenJuciZyGnHucd5xtnGycaZxnnF+cTpw6",
    "nDmcN5w2nDWcKZwSnA6cA5v1m+ebzJu5m6eblJt4mzmbMJspmyabF5sWmwybCpsFmwGa/Jr6mvia75rhmuCa3ZrEmsOawZqqmpGaeJp2mmWaRJo9miyaF5oVmgyaC5oImfKZ8ZnhmamZmZktmI+YX5g8mDSYBpdA",
    "lySXAZbslt2WtJadlpyWmpaZllqWO5Y4li+WK5YqleuV1JW3la6Vo5WYlZOVgJVClUCVPpU1lTKVFJUMlPyU3ZSllJaUkZSElHqUapRalFWT/pO+k7aTs5Oxk6+TkpOBktaSLJIpkiSR7JHikb2RsJFokTiQmpB3",
    "kHGQXJBZkE2QPpAvj/qP9I/bj8CPtY+Tj4WPKo8JjwSOso6wjcCNmY2RjYqNiI2DjXONZ41cjSyNGYzwjEuMSoxEjAOMAIv8i/uL+Iv3i+KL3Yvai9aL1IvLi7iLnYuai4CLe4sxiyuK+or3ivSK4YrPirCKrYqm",
    "inuKeopSijqKLYmyibGJsImRiW+JNokxiSaJIokdiQeI/YjuiMeIvIiCiH6IfYhoiGOINogsiCqIJIgWh+uH4Yfch8CHtoe1h46HjYd3h26HY4dKhwuGoIaZhoOGTIY4hh2F+YX4hfSF8YXuhHyEeYRyhGuEZoRj",
    "hGCEWoRXhFaEVIRRhFCESYRIhEWEM4QhhB+EHoQOg/6D6IPRg82DroNCgz2DPIM7gzWDK4MQgviC8YLsgqKCfIJtglSCToI7gjOCFoHfgdGBj4FogWCBSYDkgNWAp4CKgHWAWIAmgA1/p3+Dfzt/JH6qfp9+h32W",
    "fRV9DXyde+Z7cXsreyd7IXsNewp7CHsBeuV6yHqzerF6nnqAefp5+Xn1ebt5unm5ebh5sHmgeZ55hXfld+N333fcd9t32nfTd9B3z3fHd8V3wne/d7h3sXeqd6l3pXefd5p3mXc8dzR2gHZ9dnx2e3Z1dnF2bXZj",
    "dl12VXZUdjt2NXYodiR1/HXtdeB11XXUdcx1xnXDdY51DXUHdQB0U3RQdE90Q3RCdC90LnQadAt0AHP/c/dz9XPyc/Fz8HPZc9Rz0nPMc8dzxnO/c7tzoXOQc4tzcXNhcz5y+nLmcpdyU3IcchtyGnIZb2NvTW8/",
    "by1u+W72bvFu6G7bbsdumm54bhBuD24Nbght/G32beBtzm3NbcBtuW23baRtoG17bXhtT21IbRltEG0KbOBs22zCbLxsuGy3bLZsJmula6NroWuda4triGtYa09rSmq9artqpGqeaphqlmnEacBpt2m0aahpjWle",
    "Z7tngGYYZWllY2UcZO1kpQU+AAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
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
    "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",
    "/+IFtgCWAIwA5QCWAIkA+gAAARgBDAMdAJkCSgB4ArYAjQCoAIwAAAAAAnkA2QC0AAAAAAFaAG0AfwCgAAAAAABtAIgAAAAAAAAAAAAAAAAAAAAAAIwAoAAAAIIAiQAAAAAAAAAAAAAFtvzqABH/6wCWAAAAAAAA",
    "AHMAZQB4AAAAAAAAAAAAvAGqA1QBqgIdALwAtgAAAAAAAACWAAAAAAW2/rwAmACsATkB9QGDAx3/8wCDAHoAhgAAAAD+bwCJAAAAAAAAACoAAAB5AAAAyAAAARcAAAFlAAAB8QAAAp0AAANfAAAEAAAABLYAAAV9",
    "AAAGAgAABh0AAAY4AAAGUwAABm8AAAaLAAAGqwAABt8AAAcXAAAHfQAAB7gAAAe4AAAH3AAACCYAAAhoAAAIqwAACMwAAAjrAAAJGAAACUQAAAleAAAJvwAACfYAAAomAAAKYQAACsEAAAsdAAALlwAAC+gAAAyK",
    "AAANGgAADcsAAA5LAAAOnAAADvQAAA98AAAPkgAAECQAABB8AAAQ4wAAEVAAABHIAAASOgAAEsgAABMoAAATngAAFDIAABShAAAVLwAAFUUAABWNAAAWMgAAFvoAABcjAAAXeAAAF88AABgjAAAYOQAAGNoAABlP",
    "AAAZZQAAGakAABm/AAAZ1QAAGesAABoBAAAaFwAAGi0AABpDAAAaWQAAGm8AABr3AAAbewAAG5EAABunAAAbvQAAG9MAABvpAAAb/wAAHBUAAByuAAAcxAAAHNoAABzwAAAdBgAAHRwAAB0yAAAdSAAAHV4AAB10",
    "AAAdigAAHjkAAB5PAAAeZQAAHnsAAB6XAAAerQAAHsMAAB7fAAAe9QAAHwsAAB8hAAAfNwAAH00AAB9pAAAffwAAH5UAAB+xAAAfxwAAH90AAB/5AAAgDwAAICUAACA7AAAgVwAAIG0AACCDAAAgmQAAIK8AACEm",
    "AAAhvQAAIlAAACMHAAAj6gAAJEQAACTIAAAlMAAAJbcAACY/AAAm2QAAJ2QAACgmAAApCwAAKYEAACo6AAAq1AAAKuoAACsAAAArFgAAKywAACtCAAArWAAAK24AACuEAAArmgAAK7AAACwOAAAsKgAALKIAACz8",
    "AAAtXQAALXMAAC3UAAAuRQAALtQAAC7qAAAvAAAALxYAAC8sAAAvQgAAL1gAAC9uAAAvhAAAL5oAAC+wAAAvxgAAL9wAAC/yAAAwCAAAMMUAADDbAAAw8QAAMQcAADEdAAAxfwAAMhcAADItAAAyQwAAMlkAADJv",
    "AAAyhQAAMqEAADM4AAAzTgAAM7oAADPqAAA0NAAANKAAADURAAA1qQAANlEAADabAAA27QAANzwAADdSAAA3aAAAN34AADeUAAA3wwAAN9kAADfvAAA4BQAAOBsAADiVAAA5cwAAOeIAADpqAAA6gAAAOxcAADvN",
    "AAA74wAAPKoAADzAAAA81gAAPQkAAD1eAAA9vAAAPdIAAD5FAAA+pgAAPxwAAD+HAAA/7wAAQAUAAEAbAABAkgAAQPkAAEF7AABB6AAAQf4AAEJpAABCfwAAQpUAAEKrAABCwQAAQtcAAENKAABDrQAARDAAAETG",
    "AABFZwAARX0AAEX0AABGCgAARiAAAEawAABGzAAARuIAAEb4AABHvgAAR9QAAEfqAABIAAAASBYAAEkFAABJIQAASVQAAElqAABJugAASdAAAEnmAABJ/AAAShIAAEooAABKPgAASlQAAEpqAABK8QAASwcAAEsd",
    "AABLMwAAS0kAAEtfAABL9QAATAsAAEwhAABM0wAATO8AAE0FAABNxAAATdoAAE3wAABOBgAATqoAAE7AAABPegAAT5AAAFBBAABQVwAAUG0AAFDAAABRLwAAUbQAAFI8AABSxgAAU6AAAFO8AABT0gAAU+gAAFRv",
    "AABUhQAAVJsAAFSxAABUxwAAVN0AAFTzAABVCQAAVWYAAFV8AABWHAAAVjIAAFZIAABWXgAAVnQAAFcNAABXIwAAV7cAAFfNAABX4wAAV/kAAFgPAABYJQAAWDsAAFhRAABYZwAAWH0AAFiTAABY9QAAWQsAAFkh",
    "AABZNwAAWZoAAFoDAABaoAAAWrYAAFrMAABbeQAAW48AAFvuAABcBAAAXBoAAFwwAABcRgAAXFwAAFxyAABciAAAXKQAAFzUAABdOgAAXXsAAF4mAABeiQAAXu0AAF9zAABgIAAAYDYAAGDkAABg+gAAYRYAAGFS",
    "AABhuwAAYkMAAGKGAABinAAAYrIAAGLIAABi3gAAYvQAAGMKAABjIAAAY5AAAGOmAABjvAAAZCgAAGQ+AABk3wAAZPUAAGULAABlIQAAZTcAAGVNAABlYwAAZc8AAGXlAABl+wAAZhEAAGYtAABmQwAAZlkAAGZv",
    "AABmhQAAZpsAAGa3AABmzQAAZukAAGcFAABnkQAAaEcAAGhdAABocwAAaIkAAGifAABotQAAaMsAAGjhAABo9wAAaQ0AAGkjAABpOQAAaU8AAGllAABpewAAaZEAAGmnAABpvQAAadMAAGnpAABp/wAAaswAAGvA",
    "AABr1gAAbJ0AAGyzAABsyQAAbN8AAG04AABtTgAAbWQAAG16AABt8wAAblMAAG5pAABufwAAbpUAAG6rAABuwQAAbtcAAG7tAABvAwAAbxkAAG/vAABwBQAAcBsAAHAxAABwRwAAcF0AAHBzAABwjwAAcKUAAHC7",
    "AABw0QAAcOcAAHD9AABxEwAAcSkAAHE/AABxVQAAcWsAAHGBAABxlwAAca0AAHHDAABx2QAAce8AAHIFAAByGwAAcjEAAHJHAAByXQAAcnMAAHKJAABynwAAcrUAAHLLAABy4QAAcvcAAHMTAABzKQAAcz8AAHNV",
    "AABzawAAc4EAAHOXAABzrQAAc8MAAHPZAABz7wAAdAsAAHQhAAB0NwAAdE0AAHRjAAB0eQAAdI8AAHSlAAB0uwAAdNEAAHTtAAB1AwAAdRkAAHU1AAB1SwAAdWEAAHV3AAB1jQAAdaMAAHYqAAB2QAAAdlYAAHZs",
    "AAB2ggAAdpgAAHauAAB2xAAAdtoAAHbwAAB3BgAAd4gAAHeeAAB4AwAAeBkAAHgvAAB48AAAeQYAAHkcAAB5jwAAeaUAAHohAAB6NwAAengAAHqOAAB65AAAevoAAHsQAAB7swAAfDkAAHxPAAB84AAAfPYAAH0M",
    "AAB9ywAAfeEAAH33AAB+DQAAfiMAAH8vAAB/1wAAf+0AAIADAACAGQAAgIgAAIEWAACBLAAAgUIAAIFYAACBywAAgjwAAIKxAACDJQAAg7YAAIPMAACD4gAAg/gAAIQOAACEJAAAhLAAAITGAACFXwAAhXUAAIWL",
    "AACFoQAAhjsAAIZRAACGZwAAhoMAAIaZAACGrwAAhsUAAIbbAACG8QAAhwcAAIcdAACHMwAAh0kAAIdfAACHdQAAh4sAAIehAACHtwAAh80AAIfjAACH/wAAiBUAAIgrAACIQQAAiFcAAIhtAACI7AAAiQIAAIkY",
    "AACJUwAAiZkAAIojAACKoAAAi0kAAItfAACLdQAAjDEAAI0EAACNGgAAjZYAAI39AACOiAAAjyoAAI/hAACP9wAAkA0AAJAjAACQOQAAkE8AAJEJAACRHwAAkTUAAJFLAACRYQAAkXcAAJGNAACRowAAkbkAAJHV",
    "AACR8QAAkgcAAJIdAACSMwAAkk8AAJJlAACSewAAkpEAAJKnAACSvQAAktMAAJLpAACTCwAAkyEAAJM3AACTTQAAk2MAAJN5AACTlQAAk6sAAJPBAACT4wAAlGMAAJR5AACUjwAAlKUAAJS7AACU0QAAlO0AAJUD",
    "AACVHwAAlTUAAJWaAACWigAAltkAAJbvAACXBQAAl3sAAJeRAACXpwAAl70AAJfTAACX6QAAl/8AAJgVAACYKwAAmEEAAJhXAACYcwAAmIkAAJifAACYtQAAmMsAAJjhAACY9wAAmWAAAJn3AACasAAAmx0AAJuJ",
    "AACcIAAAnKYAAJ1LAACdYQAAnXcAAJ3eAACd9AAAngoAAJ4gAACeNgAAnooAAJ6gAACetgAAnswAAJ7iAACe+AAAnw4AAJ8kAACfOgAAn4kAAKAFAACgGwAAoDEAAKDgAAChfQAAoiUAAKLQAACi5gAAovwAAKO+",
    "AACj1AAAo+oAAKQAAACkFgAApCwAAKRCAACkWAAApG4AAKSEAACkmgAApLAAAKTGAACk3AAApPIAAKUIAAClHgAApTQAAKWxAAClxwAApd0AAKXzAACmDwAApwYAAKccAACnMgAAp0gAAKdeAACndAAAp4oAAKeg",
    "AACntgAAp8wAAKfiAACn+AAAqA4AAKgkAACoOgAAqFAAAKi4AACozgAAqOQAAKmJAACpnwAAqbUAAKnLAACp4QAAqfcAAKoNAACqIwAAqjkAAKpPAACqZQAAqnsAAKqRAACqpwAAqr0AAKtEAACrWgAAq3AAAKuM",
    "AACrogAArIIAAKyYAACsrgAArMoAAKzgAACs9gAArQwAAK0iAACtOAAArU4AAK1kAACtegAArZAAAK2mAACtvAAArdIAAK3oAACt/gAArhQAAK4qAACuQAAArlYAAK5sAACuggAArpgAAK6uAACuxAAArtoAAK7w",
    "AACvBgAArxwAAK8yAACvSAAAsAUAALAbAACwMQAAsEcAALBdAACxEQAAsaoAALI9AACyqwAAssEAALM4AACzTgAAs2QAALN6AACzkAAAs6YAALO8AACz0gAAs/QAALQQAAC0LAAAtEIAALRYAAC0dAAAtIoAALTs",
    "AAC1awAAtYEAALXwAAC2jwAAtqUAALa7AAC20QAAtucAALcDAAC32AAAt+4AALgKAAC4IAAAuDYAALhSAAC4bgAAuIQAALigAAC4tgAAuMwAALjiAAC4+AAAuQ4AALkkAAC5igAAuaAAALm2AAC50gAAuegAALqP",
    "AAC6pQAAursAALrRAAC65wAAuwMAALsZAAC7LwAAu0UAALveAAC79AAAvAoAALyLAAC8oQAAvLcAALzNAAC86QAAvP8AAL3BAAC91wAAve0AAL5YAAC+bgAAvoQAAL6aAAC+sAAAvsYAAL7cAAC+8gAAvwgAAL8e",
    "AAC/NAAAv0oAAL9gAAC/dgAAv4wAAL+iAAC/uAAAv84AAL/kAAC/+gAAwBAAAMAmAADAPAAAwFIAAMFiAADBeAAAwhEAAMInAADCPQAAwlMAAMJpAADDMAAAw0YAAMRJAADEXwAAxHUAAMSLAADEoQAAxSYAAMU8",
    "AADFUgAAxWgAAMXgAADF9gAAxgwAAMYiAADGOAAAxk4AAMZkAADGegAAxpAAAMcvAADHRQAAx1sAAMdxAADHhwAAx50AAMezAADHyQAAx98AAMf1AADIEQAAyGwAAMiCAADImAAAyK4AAMjEAADI2gAAyPAAAMkG",
    "AADJHAAAyTIAAMlIAADJXgAAyXQAAMmKAADKLwAAykUAAMpbAADKcQAAyocAAMqdAADKswAAyskAAMrfAADK9QAAywsAAMshAADLNwAAy00AAMtjAADLeQAAy48AAMulAADLuwAAy9EAAMvnAADL/QAAzHkAAM0m",
    "AADN1wAAznIAAM6IAADOngAAzrQAAM7KAADO4AAAzvYAAM8MAADPIgAAzzgAAM9OAADPZAAAz3oAAM/rAADQRAAA0FoAANBwAADQhgAA0JwAANCyAADQyAAA0N4AAND0AADRCgAA0SAAANE2AADRUgAA0WgAANF+",
    "AADRlAAA0aoAANHAAADR3AAA0fIAANIIAADSHgAA0jQAANJKAADSYAAA0nYAANKMAADSqAAA0z0AANNTAADTvQAA09MAANRVAADU5QAA1WIAANV4AADVjgAA1aQAANW6AADV0AAA1eYAANX8AADWEgAA1igAANY+",
    "AADWVAAA1u8AANcFAADXZAAA2CIAANg4AADYTgAA2GQAANh6AADZCgAA2acAANoKAADaIAAA2jYAANpMAADaYgAA2wAAANuTAADcKgAA3EAAANxWAADdNQAA3UsAAN5YAADebgAA3yMAAN9eAADfigAA4AEAAOB9",
    "AADhHAAA4aoAAOHHAADiAQAA4jsAAOKEAADitAAA4tsAAOL5AADjFgAA4zUAAOOQAADjuQAA5AoAAORzAADkuwAA5RMAAOWCAADlpwAA5icAAOaUAADmwQAA5vcAAOchAADnSQAA53MAAOfhAADomQAA6N4AAOlK",
    "AADpnQAA6eoAAOoaAADqQwAA6qYAAOrUAADrBwAA6zoAAOtxAADrjwAA69oAAOwWAADsegAA7MMAAO00AADtiAAA7fMAAO4WAADuWgAA7owAAO7tAADvKQAA71cAAO+EAADvqwAA78oAAO/wAADwGwAA8DYAAPBb",
    "AADwxgAA8SgAAPF1AADx1gAA8jIAAPJ7AADzLwAA83MAAPPBAAD0GwAA9FYAAPSEAAD05gAA9SYAAPV/AAD14gAA9kYAAPZ+AAD24QAA9yoAAPdsAAD3oQAA9/wAAPg6AAD4iwAA+LgAAPkWAAD5MAAA+Y8AAPnH",
    "AAD5/QAA+mMAAPtHAAD71wAA/FcAAPzeAAD9aAAA/aEAAP3LAAD+kgAA/xgAAP9+AAEAKQABANQAAQGJAAECOQABApcAAQMEAAEDewABA+wAAQREAAEEqgABBQsAAQVtAAEF3AABBnsAAQbkAAEHYAABCEAAAQjT",
    "AAEJSAABCYoAAQntAAEKdAABCx4AAQvYAAEM/wABDVkAAQ5eAAEOvgABD5kAARAxAAEQmAABEUcAARGzAAESTQABErcAARNEAAETyQABFDUAARStAAEVlgABFhEAARZlAAEXIgABF6cAARgoAAEYwgABGUkAARnH",
    "AAEaMAABGqAAARspAAEblwABG/sAARxsAAEc0AABHYkAAR37AAEeYwABHvAAAR95AAEgOwABIQIAASFpAAEhqgABIdoAASImAAEihAABItgAASOSAAEkGQABJK0AASUGAAElIAABJa8AASX7AAEm0QABJ68AAShU",
    "AAEo+gABKX4AASowAAEqhwABKzsAASwBAAEsiQABLNwAAS1IAAEtvwABLqAAAS8NAAEvSQABL9YAATAoAAEwdAABMSgAATG+AAEyBwABMmsAATLaAAEzVAABM8wAATQmAAE04QABNZ4AATXxAAE2VQABNqkAATcw",
    "AAE3hQABOC8AATjmAAE5XgABOb8AATpoAAE68gABOz0AATubAAE79QABPE8AATz8AAE9cQABPiMAAT7oAAE/SQABQC0AAUB/AAFBrQABQeAAAUJyAAFC9AABQ0UAAUOvAAFEEQABRFkAAUS4AAFFSwABRZgAAUXy",
    "AAFGogABRy8AAUduAAFH+wABSHUAAUj1AAFJhQABSdsAAUpPAAFKugABS2oAAUvNAAFMCwABTJUAAU0zAAFN5wABTpcAAU7mAAFPZQABT7YAAVAqAAFQmgABUQsAAVGjAAFSEwABUoAAAVLUAAFTLQABU6cAAVRm",
    "AAFVTAABVfEAAVaFAAFXbgABV9AAAVgwAAFYoAABWcAAAVqLAAFbeAABXCgAAVzjAAFdjwABXkEAAV6JAAFe2QABX1MAAV/OAAFgLgABYLMAAWFfAAFhpwABYhIAAWMLAAFjpQABZDQAAWSXAAFlCAABZcQAAWaD",
    "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",
    "AAJNEwACTXQAAk4LAAJOUAACToMAAk8CAAJPOAACT5AAAk/qAAJQfgACUOMAAlEcAAJRRAACUaoAAlHZAAJSbAACUt0AAlNKAAJT0AACVFMAAlTRAAJVNAACVXcAAlXwAAJWdQACVswAAlcJAAJXWAACV6EAAlfd",
    "AAJYUQACWIkAAljOAAJZSwACWb8AAlpLAAJa/wACW7QAAlwoAAJcpQACXOAAAl1MAAJdigACXfEAAl5VAAJevQACXzYAAl/fAAJgRwACYKAAAmDvAAJhawACYb0AAmIeAAJicwACYr0AAmM1AAJjnwACY/gAAmQl",
    "AAJkwQACZYgAAmYjAAJmvwACZzAAAmfKAAJoawACaSIAAmlRAAJqLwACaqYAAmsTAAJrigACbBcAAmyKAAJsuQACbSYAAm2LAAJt9wACbjgAAm7GAAJvbAACb/YAAnBoAAJwqwACcO4AAnFBAAJxlgACcdYAAnIo",
    "AAJyoAACcy0AAnOFAAJzwwACdDcAAnR2AAJ0zQACdTYAAnWhAAJ2BQACdnUAAnceAAJ3hAACeBcAAniHAAJ48AACeU8AAnoXAAJ6xQACe2IAAnvRAAJ8DQACfIkAAnzoAAJ9GwACfWMAAn2+AAJ9/AACfm4AAn7X",
    "AAJ/TAACf9MAAoBvAAKBAgACgYcAAoJOAAKCxgACgycAAoOIAAKD/AAChN4AAoUYAAKFhwAChdQAAoZbAAKGtgAChzwAAofAAAKIFQACiIUAAoj3AAKJaAACieoAAopRAAKKqQACiycAAounAAKL1QACjGEAAozJ",
    "AAKNMgACjZAAAo3bAAKOVQACjuIAAo9EAAKP9QACkJgAApDuAAKRfQACkZcAApHnAAKSiwACktwAApMkAAKT8AAClDoAApSTAAKUzwAClQkAApVUAAKVjwAClbUAApZ0AAKWpQACl0kAApffAAKYCwACmDcAApiO",
    "AAKZIgACmXsAApnTAAKaTAACmroAApt7AAKbrAACnCEAApyKAAKc8AACnSsAAp2SAAKeCwACnrgAAp8/AAKf8gACoIgAAqELAAKhcQACod0AAqJWAAKiygACo5EAAqPpAAKkigACpPMAAqVCAAKlrAACplkAAqam",
    "AAKm8QACp0EAAqehAAKoBQACqQoAAqlwAAKpvgACqgwAAqpiAAKqrAACqvEAAqtiAAKsJAACrIkAAq0WAAKtjQACrdsAAq4zAAKugwACrxcAAq9iAAKvowACr+cAArB2AAKxBwACsZEAArHpAAKyewACsr4AArL/",
    "AAKzmgACtAYAArR4AAK0wAACtUYAArXtAAK2sQACtv8AArdZAAK3ugACt/gAArhsAAK4zgACuSkAArl0AAK5zAACuhcAArpsAAK6sgACuyMAAruGAAK73QACvC8AArzoAAK9WAACvfgAAr5wAAK/CgACv2oAAr+3",
    "AALAKwACwLgAAsFeAALBjwACwhsAAsKGAALC5QACw4kAAsQHAALEPQACxJIAAsUbAALFXAACxZ0AAsYyAALGbQACxqYAAsc8AALHnQACyBEAAshNAALIvAACyR0AAsmxAALJ8wACykwAAsqbAALLGwACy3cAAsvK",
    "AALMOwACzOkAAs0gAALNXgACzbMAAs4pAALOZAACzqsAAs7yAALPlQAC0AQAAtCKAALQ4AAC0VQAAtG6AALSAgAC0kAAAtKfAALS9wAC000AAtPDAALUAQAC1DYAAtS6AALVHwAC1WEAAtWxAALWBgAC1loAAtaY",
    "AALXCwAC108AAtfkAALYRAAC2M4AAtlQAALZuwAC2hkAAtqZAALa/wAC2zsAAtubAALb2QAC3BcAAtycAALc2AAC3WAAAt4HAALemAAC3tkAAt8UAALfSwAC38YAAuAKAALgTgAC4LkAAuEUAALhrAAC4gYAAuK+",
    "AALjLgAC42wAAuPiAALkVgAC5LcAAuUaAALlUwAC5Y0AAuXdAALmLQAC5nkAAubMAALnHwAC53IAAuekAALn0gAC6AQAAug2AALopQAC6RYAAumNAALp1QAC6iQAAutHAALsIQAC7HIAAuy7AALtGAAC7ZEAAu4N",
    "AALufQAC7uUAAu9LAALvvgAC8A4AAvDYAALxQAAC8UAAAvGjAALx/QAC8ycAAvR8AAL18QAC9iYAAvZ/AAL22AAC90MAAveSAAL39wAC+DEAAvhvAAL4qgAC+TUAAvmOAAL6MwAC+vwAAvubAAL8QAAC/PsAAv1n",
    "AAL+YgAC/xsAAv99AAL/+gADAIUAAwDsAAMBdQADAiQAAwNiAAMETwADBQkAAwWLAAMF+gADBmoAAwbqAAMHgwADB/AAAwhmAAMIwgADCcIAAwoNAAMLDAADC7sAAwwwAAMMqwADDWEAAw4iAAMOvAADDxsAAw9/",
    "AAMQTAADEhAAAxMKAAMT7QADFF4AAxS4AAMU8wADFU0AAxV6AAMVvgADFmgAAxcBAAMXdwADGBIAAxiwAAMZPwADGloAAxrVAAMbTQADG9QAAxyMAAMc5wADHbIAAx4kAAMemAADHzcAAx/VAAMgQQADINsAAyF5",
    "AAMh5gADIo8AAyQZAAMlAAADJcIAAyY1AAMm7AADJxsAAyfRAAMoOwADKNEAAykUAAMpsgADKd4AAyqCAAMrVgADLAgAAgJYAAAFqAW4AAMABwAAASERITchESECWANQ/LBoAnj9iAW4+khoBOgAAQFQAFgGsAPA",
    "ABYAAAEhFSETFhUUIyInASY1NDcBNjMyFRQHApAEIPvgiCAgGCj+qDAwAVgoGCAgAkBo/vA4GCAgATgwMCgwATggIBg4AAEASP4YA7gGGAAWAAABESMRBQYjIjU0NwE2MzIXARYVFCMiJwIwYP7wQBggKAE4KDAw",
    "KAE4KCAYOATQ+UgGuIggICAgAVg4OP6oKBggIAABAVAAWAawA8AAFgAAASE1IQMmNTQzMhcBFhUUBwEGIyI1NDcFcPvgBCCIICAYKAFYMDD+qCgYICAB2GgBEDgYICD+yDAoMDD+yCAgGDgAAQBI/hgDuAYYABYA",
    "AAURMxElNjMyFRQHAQYjIicBJjU0MzIXAdBgARg4GCAo/sgoMDAo/sgoIBhAqAbA+UCIICAYKP6oMDABWCgYICAAAwDY/8AHKAYIAAsAFwAiAAABEAAhIAAREAAhIAADEAAhIAAREAAhIAAFIxE0NwYHByc3Mwco",
    "/iD+uP64/iAB2AFQAVAB2FD+UP7Y/tj+UAGwASgBKAGw/XBwCBgwWDjgYALg/rj+KAHYAUgBUAHY/ij+sAEoAbD+UP7Y/tj+WAGokAIgWIAYKEhIsAADANj/wAcoBggACwAXAC8AAAEQACEgABEQACEgAAMQACEg",
    "ABEQACEgAAUhNTc2NjU0JiMiByc2MzIWFRQGBwcVIQco/iD+uP64/iAB2AFQAVAB2FD+UP7Y/tj+UAGwASgBKAGw/jj94NCAQEhIWGg4cJBwiFCAqAGYAuD+uP4oAdgBSAFQAdj+KP6wASgBsP5Q/tj+2P5YAaiQ",
    "WOiIeEhISFBIaIBoUJiQsAgAAwDY/8AHKAYIAAsAFwA6AAABEAAhIAAREAAhIAADEAAhIAAREAAhIAABFhUUBiMiJzUWMzI2NTQmIyM1MzI2NTQmIyIHJzYzMhYVFAco/iD+uP64/iAB2AFQAVAB2FD+UP7Y/tj+",
    "UAGwASgBKAGw/WDgqKCQWHB4aHB4cFBQaGBISHBgOHCYeIgC4P64/igB2AFIAVAB2P4o/rABKAGw/lD+2P7Y/lgBqAE4ILCAiDBoOFBYUFBYUFhAQEhQWHhgsAAEANj/wAcoBggACwAXACIAKgAAARAAISAAERAA",
    "ISAAAxAAISAAERAAISAAJSMVIzUhNQEzETMjNTQ3IwYHAwco/iD+uP64/iAB2AFQAVAB2FD+UP7Y/tj+UAGwASgBKAGw/iiAaP5oAZBwgOgICAgo+ALg/rj+KAHYAUgBUAHY/ij+sAEoAbD+UP7Y/tj+WAGoMMDA",
    "YAJQ/bjQmHAwQP6YAAMA2P/ABygGCAALABcAMwAAARAAISAAERAAISAAAxAAISAAERAAISAABTUWMzI2NTQmIyIHBycTIRUhAzYzMhYVFAYjIgco/iD+uP64/iAB2AFQAVAB2FD+UP7Y/tj+UAGwASgBKAGw/CBY",
    "gGBoaGgwOCA4IAGg/sAYUDCAmKCYiALg/rj+KAHYAUgBUAHY/ij+sAEoAbD+UP7Y/tj+WAGocGg4WGBYWAgIKAGYYP8AEJBwmJAABADY/8AHKAYIAAsAFwAtADkAAAEQACEgABEQACEgAAMQACEgABEQACEgAAEV",
    "JiMgAzM2MzIWFRQGIyImNRASMzIDIgYVFBYzMjY1NCYHKP4g/rj+uP4gAdgBUAFQAdhQ/lD+2P7Y/lABsAEoASgBsP3gKED++AgIOIBwiJB4gKDAwDiYUGhoUFBQUALg/rj+KAHYAUgBUAHY/ij+sAEoAbD+UP7Y",
    "/tj+WAGoAthYEP6YaIiAiKDIwAEAAQD+WGg4aHhgaFhgAAMA2P/ABygGCAALABcAHgAAARAAISAAERAAISAAAxAAISAAERAAISAABQEhNSEVAQco/iD+uP64/iAB2AFQAVAB2FD+UP7Y/tj+UAGwASgBKAGw/IAB",
    "UP5AAjD+uALg/rj+KAHYAUgBUAHY/ij+sAEoAbD+UP7Y/tj+WAGokAMIYFj88AAB/+j+QATgB/gAAwAAAxEhERgE+P5ACbj2SAABALgBsAQYBOAAAgAAASEBBBj8oAGwAbADMAABARgBUARIBLAAAgAAAQERBEj8",
    "0AMA/lADYAABALgBIAQYBFAAAgAACQIEGP5Q/lAEUPzQAzAAAQCAAVADuASwAAIAAAkCA7j8yAM4AVABsAGwAAEAkAEoBEAE2AADAAAJAwRA/ij+KAHYAwD+KAHYAdgAAQCwAUgEIAS4AAsAABM0ADMyABUUACMi",
    "ALABALi4AQD/ALi4/wADALgBAP8AuLj/AAEAAAEAsP+4B1AGAAAJAAABARMBIRMTIQETBAD94ND+AAKA0NACgP4IyAEw/ogCcAF4AmD9oP6I/ZAAAgCw/7gHUAYAAAkAEwAAAQETASETEyEBEwEBAwEBAwEhAwME",
    "AP3g0P4AAoDQ0AKA/gjI+5gBYJgBgAGAmAFo/kiYmAEw/ogCcAF4AmD9oP6I/ZADmP74/kgBEP7wAbgBCAG4/kgAAQHw/3gGsAZIAAoAAAEAASMCAzcSExIBBrD+WP74cKj4qLhw4AFQBiD88PxoAbABkFj+qP7A",
    "A0ACkAABADD/EAJIATAABQAABQcCJTcEAkh4oP8AeAEgiGgBAMBg6AACADD/GAJYATgACwAXAAA3NDYzMhYVFAYjIiY3FBYzMjY1NCYjIgYwoHhwoKBweKCAWEA4WFg4QFgocKCgcHCgoHBAWFhAQFBQAAIEAP9o",
    "ByAGYAAFAAsAAAUHAQEXARMHAQEXAQcgcP5QAbBw/nCQeP5YAah4/nBYQAN4A4A4/Lj8yEADeAOAOPy4AAIA2P9oBAAGYAAFAAsAAAEBJwEBNxMBJwEBNwQA/lh4AZD+cHio/lB4AZj+aHgC4PyIQAM4A0g4/ID8",
    "iEADOANIOAABBAAC4AYgBmAABQAAASERIxEhBiD+mLgCIAXI/RgDgAABAeD/aAQAAuAABQAABSE1IREzBAD94AFouJiQAugAAQQA/2gGgAZgAAgAAAUhESEVABEQAQaA/YACgP5wAZCYBvhI/qj+IP4w/pgAAQGA",
    "/2gEAAZgAAgAAAUhNQAREAE1IQQA/YABkP5wAoCYQAFoAdAB4AFYSAABAKgC6AdQA4AAAwAAEyEVIagGqPlYA4CYAAEAeP9IB3gGCAAaAAABITUhFSEUByEQAiMiJycWMzI2EyECAgUnNgACiP34Bvj7sBADiHiw",
    "YJAYkGBISBD9ECD4/vBw4AEwBXCYmNio/Lj+wCCYIMACmP6Q/ijIgJACEAADAKD/2AdgBeAAAwAHAAsAAAEhFSETIRUhAyEVIQEABgD6AFgFUPqwuAbA+UAF4Jj96Jj92JgAAQCg/6AHcAZYAAsAAAEzESEVIREh",
    "FSE1IQNYqAMQ/PADcPkwArgGWP3QoPy4oKAAAQCQ/0gHeAYIAA0AAAEhNSEVIREEBQckJREjA3D9IAbo/JgBiAEQcP74/uCgBXCYmP5A6OCY8Lj8UAACAFj/SAeoBhgADgAUAAATIRUhBgcRIxEAAScAASEBAAEH",
    "AAGYBsj9WDhQsP7Q/oB4AhgBkPyYBIABUAFAgP7o/ogGGKBoePqwBGj+gP7weAFwAnD+qP7w/oiAAVgBWAACAKD/WAdQBngAFAAYAAABESECAiMiJycEMzI3NhMhETMRIRUBIRUhAkAEuBiQuHDwIAEIaGggKCD7",
    "SKAFEPlQBND7MAS4/oj9OP7gIJggWIgB2APQ/tiY/OiYAAEAkP9QB2AGeAAjAAATITchNSE3FwchFSEHIRUhByEVBgcWFwckJTcEFzY3ISc2NyGQAmA4/gACKCCwKALQ/RA4A8D8GEgDULDogHBo/pj9+EgBGOjA",
    "oP0AQDgo/cgEGOCY6BDYmOCY4KDoqEhIkOi4kFhoiMCYYIAABABw/4AHmAYwAAcACwAPABMAAAERIRUhNSEREyERIREhESERIREhBmABOPjYAUigA2j8mANo/JgDaPyYBjD56JiYBhj9+AFo/JABcPyIAXAAAwCI",
    "/1AHoAZ4ACIAKAAuAAABMxEhFSERFAYjIicnFjMyNREhJzYTITUhNjcXByEVIQIHIQEEEwcCJyUXAgUnJAP4oAKg/WBQcGhgIGhoOP04KNCY/igCKEAwqGAD6PvQkLgCEAHQAQDYcNj4/PiIoP6waAFABFj+kJj9",
    "0HhYEJgQWAIQmNABIJiAiCDomP7g0P8AwP74iAEY0GBQ/ujggNAAAQB4/0AHgAZgACcAAAEXBAURIRUhESEVIQIHJCUmJzcSEwcnBAUnJBMhNSERITUhEQQhJyAGsFD+yP6IAnj9iAMw/CC4uAHIAfBQaJjQkKhQ",
    "/bj9cDABALj9mAM4/ZgCaP7Q/rAwAtgGYJAoIP7wmP7omP6QmBBAkIBI/wD+wFCwUBiQuAFgmAEYmAEIGIgAAgB4/0AHiAYYADIANgAAAREUBiMiJycWMzI1ESEGBxYXByYnBgcnNhMhBgcWFwcmJwYHJzYTIREj",
    "ESERITUhFSERAyERIQcQcGhQaCiQSED+4BAgoHhoaGg4oHDYGP7QCBiIYGhQWEC4cPAg/sCgAej9mAcQ/cig/tABMARQ+7BgYAiYCFADkMCYeHiQiHDgoHDoAgiIcGBYkGhY8KBw2AHI+4gFEAEwmJj+0AEw/tAA",
    "BABQ/0gHaAY4ABEAFQAbACEAAAEhFSERIRUhFRABJxIRESERIQEhESEFFhcHJiclFwYHJzYBEAY4/hACEPp4/viI8AHY/fgCqAEA/wD+UGhAmDhoBOCYSFiYaAY4mP3YmMD+gP6oaAEYAVgBWAIo/dgCKGCAoFiY",
    "iEgwuHhQkAACAGD/SAewBngADAAQAAABFwcABQckAQABJyQAEzMRIwPwqCgBGAIoYP3o/tj+wP4AcAFoAYBooKAGeChI/hDAsOgB4P44/uCA2AGA/nD7eAADAOD/OAcoBoAADwATABcAAAERIzUhESMRIRUjESER",
    "MxEBIREhIREhEQcooP3AoP3YoALIoP04Aij92ALIAkAFSPwogP1IAriQA+gBOP7I/UACKP3YAigABQDo/0gHIAZ4ABcAGwAfACMAJwAAASE1MxUhESEVIREjNSERIxEhFSMRITUhNyERISERIREBIREhIREhEQE4",
    "AnioAnj9iALIoP3YqP3YoALI/YigAdj+KAKAAdj7WAIo/dgC0AIoBdCoqP3YsP1QeP6IAXiYAtCwkAEA/wABAPwgAQj++AEI//8AsP9AB3AGeBImB1sAABAGBTcAAAADALD/SAcgBngAGwAhACcAAAEhNhEzEAch",
    "EAIGIyInJxYzMjYSESECAScAEyETFhcHJicBFhcHJicBEAJAEKgIAyA4mLBoaCiAeGhQKP1wQP1YWAJQSP3I+IBQqEh4AyiAULBIcARY6AE4/sjo/Tj+WJAYoBhQAcgBsPzw/piYATACsAJwmLBAsJD9ALDIUNCo",
    "AAEAeP+QB4gGcAAZAAABFhchFSERIRUhESEVITUhESE1IREhNSEmJwPYUDAC+Pz4AqD9YANA+PADMP1oApj9CALwMEAGcJiwmP5QmP3gmJgCIJgBsJiQgAABAHj/QAeoBogAFwAAARcGByEVFAIHAAUHJAEABScA",
    "EyECBScAAwCgKEACmJhYASABqFj+SP7o/rD9kEgDwOj9wLj/AIABmAaIIJCIoBj+aJD+QMCw2AHI/ijIsAEQA7D+uNCAAWAAAgCI/1AHWAZoAAUAFwAAARcAAScAJRcAASQlJic3EhMHJicEBScAA2ig/uj+MJgB",
    "4AJwoP5Y/mABwAIYYHCQ8KCwKDD9mP2YSAJQBmg4/YD+QFgB2PBA/KD+wBB4uKBI/sD+gEhwaIAQmAHoAAIAoP9AB4AGUAAFABkAAAEWFwcCJwUSAQATFwIBBAUHJAEABSckJQADA/hoIKAoaP6waAHAAYBomGD+",
    "YAEgAbhY/kj+uP64/hBQAdgBMP5AiAZQ6PAwAQDgoP44/igBYAJwKP14/nDosKCoASD+8LiYuPABwAIgAAEAcP9AB6AGeAAeAAABFhchFQABFgQhIQcgJCQjIgYHJzY2MzMAASE1ISYnA7hoOAKo/hj9uIgBYAFw",
    "AXgw/dD9+P7oIBhIsIDQgDggAogBYPrgAsA4WAZ4sNCQ/fj+aFhQuFC4SOiA+GgByAFwoLiQAAMAWP9QB6gGYAAcACIAKAAAARcEBREhFSERFAYjIicnFjMyNjURITUhEQQFJyAFFwIHJzYlFhcHJicG4FD+uP5w",
    "A1D8sFh4mIggkJgoGPyoA1j+wP6YMAMAAkCoeJiQqPv4mHCgYJgGYJAwIP1ImP3wcGAYoCAgQAHomAKwGAiYuDj+2MhQ8MDI6FDo0AABAMj/kAeABhAAGQAAEyEVAAAVFBYhMyA2NxcCBiEjICQ1NDcAASHYBdD8",
    "YP6A2AHAcAGQmBC4KNj+cND9yP7giAEIAzD7UAYQiP0g/mhYSECA2ED++LCQmICYASACiAABAGj/SAeoBngAIgAAEyE2NTMUByERFBYzMjY3FwIHBiMiJjURIQIHAgUnJBM2EyHYAeAQoBACkChAaEAIqBBIQNCo",
    "UP4IKIig/sBYARiQgCD+KATouNjYuPt4MCBg8Dj+8FhQUHAEIP3w+P7Y2JC4ARjwAbgAAQB4/3AHkAZ4ACwAAAEzESURMxElEAYjIicnFjMyNzYRBREjEQURFBYhIDc2NxcCBiEgJyY1EQcnJQGIoAGgoAJ4cLhI",
    "WBhgWEgQIP44oP5gcAHAAdhoQCCYKMj9uP3gSGjQQAEQBbD+OHgCGP4QqP0g8AigGFCAAaCA/UACmHj9EDAQKBj4SP7oeCAgeALwOJhIAAMBAP9ABvAGAAAPABUAGwAAASEQAgYjIicnFjMyNzYRIQUEBQckJQEX",
    "BAUnJAEABfAwkHhweCiIiFgQKPq4AVABGAEQWP7o/ugDQCD+OP3IQAJQBgD8SP2YoBiwGID4BADAULCQuFj+iJD4uLCwAAMAkP9IB0AGeAAeACMAKQAAATMRIRUUAgchEAYjIicnFjMyNhMhESMRITUhESE1IQE2",
    "NyERARYXByYnAzCgAjA4IAGIeIB4iCCQgDAYGP1IoP1gAqD+EAHwAdA4KP5wAfDQsHCwyAZ4/piIEP7QcP3o+BigGFABiP0IAviYAaCY/cio+P5gA4h4oICweP//AHj/SAeYBngSJghtAAAQBgagAAAAAQDY/0AH",
    "GAYQABMAABMhFQQFERQGIyInJxYzMjURJCUh2AZA/tD+iHBokJAYeJhgAVgBCPqoBhCo+ND8QFBQIKAgIAPwyMAAAwBo/0gHqAaIAC0AMQA1AAABBgcnJBMXByEVBgchETMVIxEjNSERFAYjIicnFjMyNTUhNSE1",
    "ITUhNSE1ITY3AxUhNQEVITUCcLjwYAGAuIhAAuhISAGQ2Nig/hhYkHhoIICASP2QAnD8wANA/ggCyFgwuAHo/hgB6AVgyICA6AEIUFCAcFj+kJj+OFj+6HBYEKAYUPiY2JjYmGBg/qjY2P6Q2NgABQBo/0AHmAZ4",
    "ADMANwA7AD8AQwAAEyE1MxUhFSEVIREhFSERMxUjESM1IRUUBiMiJycWMzI2NTUhNSE1ITUhNSE1ITUhESE1IQEhNSEhFSE1ARUhNQEVITWAAxigAzD80AKQ/XACqLi4oP34YHigiCCYmDAg/SgC2PzQAzD9KALY",
    "/XgCiPzoATAB6P4YAogB8P4QAgj9+AIIBhhgYJhY/mhg/viY/rBAcHBgEJgQKDhImHiYcJhgAZhY/qhoaGj+CHBw/vh4eAACAHAAAAeIBZAAAwAHAAABIRUhAyEVIQEgBbj6SLAHGPjoBZCY+6CYAAEAgP9IB4AG",
    "AAAZAAABIRUhESEVIREUBiMiJycWMzI2NREhNSERIQEIBej9eAMY/OhYkIiAIIiIMDD8uANI/UAGAJj9+Jj9UHBgGJgYIEACiJgCCAACAGD/mAegBggAEQAVAAATIRUhAyEVAyEVITUhEyEnEyEBEyEDsAao+9BQ",
    "A9DwAej4wASoaPxgQPD+MAToePygcAYImP7omPxwmJgBaIADWPzAAZD+cAACAID/oAeABggAEQAVAAATIRUhAyERIRUhNSETITUhEyEBIREh0AZg/MBwAwABAPkAAaiY/lgByHD9gAH4Axj9gAYImP4g/KiYmALA",
    "mAHg+sgCwP//AGj/iAegBngSJgWVAAAQBgWUAAAABABg/zgHqAaAAAkADwAVACkAABMhJic3FhchFSEFFwIFJyQlBBcHJicTFwYHBAUHJCUEBSckJSYnNxYXNpADEChAqEgwAxD5KAH4gND+uGABGAPIAQjYeOD4",
    "WJiA0AF4AZBg/gD+0P6A/hhQAfABMOiwiKjwyAVweGA4gJCYOGj/AKCYgOCg0JDoqP7oQPi42FiomND4eKBo0LDYaOCoqAADAFj/OAdgBmgACQAZAB8AAAEWFyEVITUhJicBFwYHIRUhERAHJxIRESE2JRYXByYn",
    "BAg4GAL4+ZACwBgoAfC4OGgB+Pp46JjgA3hg/dBYKKAwUAZoaGiYmFhQ/pg4iJiY/oD+yPhYAQABMAHAkMBwkDiQeP//AHD/SAeQBoASJggAAAAQBgU2AAAAAQBY/0gHqAZQAA0AAAEzERQAAQcAAwIBJwARA6Co",
    "AXAB8Fj9mOC4/WBYA0gGUP5IyP0g/wCoAUACiP2w/oiYAfACyP//AFD/SAeYBngSJgjIAAAQBggyAAD//wBQ/zgHmAZ4EiYIYAAAEAYIyAAA//8AUP9IB5gGeBImBgYAABAGCMUAAP//AFD/SAcwBoASJgjIAAAQ",
    "BgWJAAD//wBQ/0gHiAZ4EiYIxQAAEAYHsgAA//8AWP84B6gGgBImB2sAABAGBTUAAP//AFj/YAeoBoASJghzAAAQBgh1AAD//wBQ/0gHkAZ4EiYIxwAAEAYIdAAA//8AUP9IB6AGeBImCMgAABAGBgUAAAADAEj/",
    "OAewBoAACwARACAAAAEABScAARcHAAUHJCUWFwcmJwEhFQAHFwckJTcWFzY3IQQA/pj+GGgCcAFAkCgBgAHQYP5Q/mBYKJgoUP3QBVj++ODQaP7I/ihQ8NDYwPuQBYD+kPCQAUABkFg4/qDIoMiggKA4qID+gJD+",
    "uLCImPi4kGBoqPAAAwEI/0gHmAZ4AA8AGAAeAAABMxACBxITBwInAgUnJAATATMRJDcXBAUnARITBwIDBaCgIDDwuIigyMD+SGgBcAEIYPtooAEI8Ej+6P6gaAHw0ICYeMgGeP2A/sCg/vD+2IgBIPj+mMCIoAGw",
    "AhgB8PsQeJiIsKhwBOD++P7gWAEgAQj//wBQ/0gHaAaAEiYG+wAAEAYIxQAA//8AUP9IB6AGeBImCMcAABAGBgAAAP//AFD/QAewBngSJgjIAAAQBgZlAAD//wBQ/0gHiAZ4EiYIxQAAEAYGtwAA//8AUP9IB6AG",
    "eBImCMUAABAGB2EAAP//AFD/SAe4BngSJgjHAAAQBgX+AAD//wBQ/0AHoAZ4EiYHNQAAEAYIyAAAAAMAaP9IB6AGiAAMABAAJgAAARcGBwAFByQBAAUnAAMhFSETITUhFSECByQlJic3FhMHJicEBSc2BACoICgB",
    "kAGwYP5g/mD+oP4YUAKAiANI/LiQ/cgGkPxwsLABkAGoWFiI4NiASFj92P2YMPgGiDgwKP6YwKDAAaD+kPCQAVD+6Jj+iJiY/siIGFBYYGDI/uiAaGBwIJCo//8AUP9IB5AGgBImCMgAABAGBfsAAP//AFD/QAeg",
    "BngSJgjFAAAQBgU0AAD//wBQ/0gHUAZ4EiYIxwAAEAYIVwAA//8AUP9IB5AGeBImCMcAABAGBWIAAP//AFD/SAe4BngSJgjHAAAQBghCAAD//wBQ/0gHmAaAEiYIyAAAEAYHxgAA//8AUP9AB6AGeBImCMUAABAG",
    "B5EAAP//AFD/SAeYBngSJgjSAAAQBgjFAAD//wBQ/0AHqAZ4EiYIxQAAEAYHjwAA//8AUP9IB5AGeBImCKAAABAGCMUAAAAEAGj/SAegBoAACwAkACoAMAAAARcHAAUHJAEABScAASE1ITUhFSEVIRUhERQGIyIn",
    "JxYzMjURIQUWFwcmJyUXAgUnNgPgoCgBgAHIYP5I/mj+oP4oUAJo/iAC0P6YA3D+mAK4/UhQiGBQIGhoOP0wBMjI0Iio6P0AeLj++GjwBoAwOP64uKDAAXD+iPCYAUj9iNiYmNiY/gBwWBCgGEgB6ICo2IDY0Fhg",
    "/wCokIj//wBQ/0gHmAZ4EiYIxQAAEAYI0AAA//8AUP9AB4AGeBImCMgAABAGBfoAAP//AFD/SAeYBoASJgjHAAAQBgbLAAD//wBQ/zgHYAZ4EiYH/QAAECYGxAAAEAYIfgAA//8AUP9AB3gGeBImCJIAABAGCMcA",
    "AP//AFD/SAegBngSJgaqAAAQBgjHAAD//wBQ/0gHWAZ4EiYIiwAAECYH4gAAEAYF+AAA//8AUP9AB7gGeBImB/0AABAGBh4AAP//AFD/SAewBngSJgjFAAAQBgX2AAD//wBQ/0gHmAZ4EiYIxQAAEAYF9QAA//8A",
    "aP9IB6AGiBImBz8AABAGB04AAP//AFD/SAeQBoASJgjHAAAQBgWkAAD//wBQ/0gHWAZ4EiYGiQAAECYH4gAAEAYIiwAA//8AaP9IB5gGiBImB04AABAGB08AAP//AFD/SAeQBngSJgjFAAAQBghZAAD//wBQ/0gH",
    "mAZ4EiYGNwAAECYHlwAAEAYH/QAA//8AUP9IB7AGeBImCMYAABAGB/4AAP//AFD/QAdwBoASJgjHAAAQBgVCAAD//wBQ/0gHoAZ4EiYIxwAAECYHqAAAEAYIGAAA//8AUP9IB3gGiBImCMYAABAGBicAAP//AFD/",
    "SAdoBngSJgjGAAAQBgY4AAD//wBQ/0gHaAZ4EiYIxQAAEAYFMwAA//8AUP9IB5gGeBImCMcAABAmBygAABAGBksAAP//AFD/SAeQBngSJgfiAAAQBgVxAAD//wBQ/zgHqAaAEiYIxQAAEAYF7gAA//8AUP9IB6AG",
    "gBImCMUAABAGBewAAP//AFD/SAeoBngSJgf8AAAQBgjHAAAAAgBg/0gHoAX4AAMAIgAAASEVIQMhFSERFBYzMjY2NxcOAiEiJjURIRAHBgUnJBIRIQEgBcD6QIAGwP3YIDDgWDAIqBBIoP7gkGD+oICY/phYAUD4",
    "/ggF+Jj+gJj8+CgYIGjQMPiYOEhgA0D+QNDoiJhwAXgBgAABAJD/UAeQBngALQAAARcGByERMxEhFSERIRUhERQWMzI2NjcXAgYhIiY1ESECBSckEyE1IREhBgcnEgIYoCg4AWigApD9cAMQ/bg4cKhIIAioEID+",
    "0MiI/sgg/dBoAego/fgDKP5QUGCQ6AZgMIiAAVD+sJj+qJj9qCAgIGjQMP7IkEBoApD9UKCYiAIwmAFYqHhwASgAAwBo/0gHiAZ4AB0AIwApAAABMxEhFSERFBYzMjY3FwYGIyAmNREhAgEnJBMhNSEBFwIHJzYl",
    "FhcHJicDqKgDCP24ULiIOAioEGj4/vCg/vhY/dBwAgBQ/fADAAKomJiocLD74JCQkICoBnj9GJj9QCAgOMA48GhIWAL4/Vj++IjoAkCYAlhY/wCYaLjAoOBwyMAAAwBw/0gHqAaAACsAMAA1AAABFwchFQYHIREh",
    "ERQWMzI2NxcCBwYhIiY1ESMGBwYFJyQTIREhNjchBgcnJBMhNjchASERIQYCkKhYAtBIUAHQ/gBIkOhQCKgQSEj+uOiQMEjguP7YaAHwwP4oAtBgQP1wyJiQAXBAAXgoEP5QAigCAP4oCAaAOHiIgGj9gP5QICBI",
    "yDD/AEA4SFgB6ODIqEiYgAGAAoBoeMBgaOD9EJDA/rABULgABwCA/0AHkAZ4AAoADgASAB8AJwAvAEAAAAEXBgcHIREhETM2AyE1IREhNSEBFwYHETY3FwYHJxE2JSERITUzESEBFwIABSckACUzERQWMzI2NxcG",
    "BwYhICY1A6CwEBgIASj9YMggUAFw/pABcP6Q/uhQiJBwgDCQ2FC4BAgBqP5w8P74/UigKP7Y/shoASgBCAHAoFCQsFAQkBBIMP7o/vh4BngoQDgQ/HgDiFD+MOj9qOgCmIhIIP0QKECIWEBYA8gYCPwQmALA/Igg",
    "/uD+0ECIOAEA8P5QICBIwDD4SDBIYAABAGj/SAewBngAEwAAASYnNxIAABcHJiYCJwMCAAUnJAADuFhomNgBKAFA4ICA2MBQqKj+aP7gWAEwAYAE4KiQYP7Y/Lj+SHiIQOABINABqP4o/eDIoOACMAACAFj/mAew",
    "BogAHgAjAAABFSERIRUhESEVITUhESE1IREhNQYHJwABFwcABQcmAQIFISQGaP3wAjj9yALY+ZgC6P3IAjj92Gh4UAJ4ARCoKAGQAcBgeP0o6P7gBBD+2AOYUP7AmP7AmJgBQJgBQEhAQKABWAGAMDj+cNioQAJY",
    "/wDI2AAEAGj/eAeQBlgABQAJAA8AFQAAARYXByYnASEVIQUXAAEnAAEAEwcCAQP4aECgOHD9QAbY+SgCOJD+yP7AgAGAA2ABWPCA+P6wBlig0DDQoP5AmLBQ/eD+yHABgAG4/oj+aIgBwAF4AAQAiP9IB3AGcAAT",
    "ABcAHQAjAAATIREzESERMxEhFSERIRUhNSERIQEhESEDFwAFJyQlBAUHJiXYAWigAjCgAXD+kAHA+RgBuP6YAggCMP3QMJj/AP7wkAFAA2gBCAEAoNj+4AT4AXj+iAF4/oiY/fiYmAII/fgCCP0YWP7QqIDI6Lj4",
    "gPDgAAIAeP9AB6AGgAAfACUAAAECBSckEyE1ITU2ESE1ITY3FwYHIRUhEAchFSESBQckARYXByYnBBB4/Vh4AqhY/UgC0Aj9iAOAgECwSHABoP1ACAMQ/UDQAlBo/dD9cHBAiEBoAeD+MNCYwAGwmDgQASiYyNBA",
    "uKCY/pgImP5QmMC4BniIkFCQiAAGAGj/QAeQBnAAEwAXABsAHwAlACsAABMhNTMVITUzFSEVIREhFSE1IREhBSE1IREhNSERITUhExcGBSckJQQFByQl4AEIoAMQoAEA/wABWPjYAYD++AGoAxD88AMQ/PADEPzw",
    "UHDY/mBIAWgDMAFQAQhw/uj+wAWQ4ODg4KD8qJCQA1jAwP3o0P3wuP6AeKB4oFCgcJiIqHAABwBg/zgHmAZAAAcACwAPABMAFwAdACMAAAERIRUhNSEREyE1IREhNSERITUhESE1IRMXBgUnJCUEBQckJQZwASj4",
    "yAEwoAOg/GADoPxgA6D8YAOg/GCwaND+YEgBYALoAUABQGD+wP64BkD7IJiYBOD+uLD+IKj+ILD+IKj+sHiYcJhQkEiIoKBQAAkASP9AB7AGiAAPABMAFwAbAB8AIwAnAC0AMwAAAREzFSE1MxEhNTMVITUzFQEh",
    "ESEhESERMxEhEQEhESEBIREhASERIQEXBgUnJCUEBQckJQboyPiYyAHAoAEYoPyIASD+4AHAARigASD7aAEg/uABwAEY/ugBuAEg/uD9uIDw/rB4ATgDEAE4ASBI/tD+0AWg+/iYmAQI6Ojo6P3wAXj+iAF4/ogB",
    "ePyQAXD+kAFw/pABcP3QYLh4oFiAWIComFgABgBo/0gHmAaIADQAOAA8AEAARABIAAABFhchNjcXBgchFSEVIREzFSMRIRIFByQDESMRIREjEQIFJyQTITUhNSE1ITUhNSE1ITUhJwE1IR0CITUzFSE1ARUhNTMV",
    "ITUCkGhoAThwQLA4aAIQ/aAB2Li4/oDoAVBQ/rDwmP7omMD+0GgBOND+iAHI/agCWP5IAbj90AIIgAJY/ugBGJgBSP0IARiYAUgGiGiIeHg4WGCIqP7YiP7Y/vh4oJgBIP4gAkj9uAHY/viokJABAIigiKCIqIig",
    "/jCoqIigoKCg/tigoKCgAAEA8P9IBxgGgAAhAAABMxEhERQGIyInJxYzMjURIQYHBBMHAicCBScAEyERIxEhA6igAtB4cHioKNhoUP3ICBgBKPhw4PiQ/rhQAbAo/eigArgGgP6Y+xhwaCCoIFgEKGhg8P7IiAE4",
    "4P6o8JgBQAHQ+sgF0AADAHD/QAeYBmAAMwA3ADsAAAERMxEhETMVIxEUBiMiJycWMzI1ESEVEAMnEhE1IxEUBgcHJzMyNREhFRADJxIRNSM1MxETIREhASERIQOgsAKIwMBgYEBgIGBIOP7AkKiQsEA4+CCwQP7Q",
    "sJiwyMiYATD+0AMoAUD+wAZg/QgC+P0ImP1YcHAIoAhwAniI/hj+4EABGAHwSP1oWHAQCKBwAmh4/hD+6EABEAHwQJgC+P0IAlj9qAJYAAUAYP9IB6AGIAAgACQAKAAsADAAABMhFSEVIREzFSMRFAYjIicnFjMy",
    "NREhESMRIzUzESE1IQEhNSEhFSE1ASE1IQUhNSGoBrD8+AKA0NCAeHCQKMBgYPuYoMjIAoD9AAEgAeD+IAKIAeD7mAHg/iACiAHg/iAGIJjI/RCY/tBgYCCYIFABCP4QAfCYAvDI/bjo6Oj9qODg4P//AIj/WAdo",
    "BjASJgf7AAAQBgUyAAD//wBo/0gHWAZ4EiYH+gAAEAYIOwAA//8AaP9IB7AGeBImB/oAABAGBekAAP//AGj/SAewBkASJgf6AAAQBgbXAAD//wBo/0AHqAZ4EiYH+gAAEAYFpgAA//8AaP9IB5gGeBImB/oAABAG",
    "BegAAP//AHj/SAeYBogSJgi+AAAQBga5AAD//wBo/0gHoAaAEiYH+gAAEAYHjgAA//8AeP9IB6gGgBImCL4AABAGBjEAAP//AFj/SAegBngSJgi9AAAQBgWFAAAAAQBo/1AHmAYQABoAAAERFBYzMjY3FwIHBiMi",
    "JjURIREQAgcnNhIREQWYMGB4SAioEEhA6MhY/ZjQ6HDAyAYQ+jgoIGj4MP7gYFBIeAVY/cD+oP4wuIiQAbgBaAKI//8AYP84B4AGgBImBrUAABAmBrYAABAGBTEAAAACAND/SAcoBkAAEwAdAAABABMSExcCAxYX",
    "ByYnAgUnJBMAAQUzESM1IREzESECQAEY+LB4oJDIyLCAoLjg/uB4AUDQ/vj+2ATAoKD6SKAFGAXw/vD+6AEQAWgg/lj+yPD4gPjo/sjIcPABIAFAARhI+gBQBbj64AABANj/SAcYBngAGwAAEzMRIREhETMRIREz",
    "ESERMxEjNSERIREzESM1IdigAjD9gKAB4KAB2KCg/igCMKCg+mACmP2gAxgCiP4QApD9cAHw/UA4/OgCYPywWAABAID/UAeABngAHQAAEyERITUhETMRIRUhESEVIREhETMRIzUhETMRIREhgAM4/XACkKACsP1Q",
    "Ayj82AHooKD7EKAByPzIA3gBQJgBKP7YmP7AmP14Afj9AHACkP4IAoj//wCY/1AHaAYoEiYHGgAAEAYFMAAAAAEAsP9IBygGGAAYAAABIRACBwYjIicnFjMyNzYRIQIAASckABMhATgF8DBIOGiIgCiYmEgQKP0A",
    "CP7Q/shwASgBABj+SAYY/ED9iFA4EJgYgPgEIP2I/UD/AHj4AmgCYAACAMj/OAcYBhAAFQAbAAABIRACIyInJxYzMhITIQIABSckABMhExcCAycSATgF4Ji4iMgYyIhoSBj98Aj+eP5gcAG4AUAI/XCwkCi4iKgG",
    "EPrw/mAgmCABIARg/Nj9wNiAyAJQAqj+yCD+mP7wUAEIAAMAcP9IB6AGcAAFAAsAIQAAAQAFBwABJRcAAScAAyEQAiMiJycWMzI2EyECAAUnJAATIQUoASgBUGj+sP7I/jB4/vj+kHABWBgEoHCwYIAgiGBAOBD+",
    "EBj+4P6ogAFAAQAo/qgGcP4w8LABAAHweGD+KP7AmAEI/tD9GP7gEKgQoAIo/rD+cKCIkAFQARj//wBo/zgHWAZ4EiYF8AAAEAYHaAAA//8AgP9IB1gGcBImBzIAABAGCEkAAP//AHj/SAcwBngSJgbFAAAQBgiY",
    "AAD//wBg/0AHMAZ4EiYImAAAEAYF5wAA//8ASP9IB1gGgBImBeUAABAGCEkAAP//AEj/QAdABnASJgdgAAAQBgf2AAD//wCA/0AHYAZ4EiYIfgAAEAYHAAAA//8AkP9AB1gGeBImBeQAABAGCEkAAP//AIj/QAdY",
    "BnASJgc9AAAQBghJAAD//wBg/0gHMAZ4EiYFQAAAEAYFPwAA//8AaP9IB1gGeBImBioAABAGCEkAAP//ADj/SAdYBnASJgYpAAAQBghJAAD//wBg/0gHWAZ4EiYGKwAAEAYISQAA//8ASP9IBzAGgBImCJgAABAG",
    "BngAAAAHAIj/SAeABpAABQAPABwALQAxADUAOQAAARYXByYnJRcGByEVITUhNgEzERQGIyInJxYzMjUBERQGIyInJxYzMjU1IREjERMhNSERITUhATMRIwKYWDiYOFADaLhYWAII+QgEMGgBWJhIcHhwIHh4OP1g",
    "YGhIWCB4QED+QJCQAcD+QAHA/kADWJiYBpBogEB4aDA4iGiQkJD+gPvIeFgYoCBgA9D7+GBgEJgQULj+UATY/rDA/fjAAbD8oP//AFj/SAdYBnASJghJAAAQBgdBAAD//wBw/0gHYAZ4EiYGEAAAEAYIfgAA//8A",
    "eP9IB4gGgBImBeIAABAGBeEAAP//AFj/SAeQBogSJgf5AAAQBgVuAAAAAQCA/0AHCAZwABsAABMhETMRIRACBiMiJycWMzI2EhEhFRABJwARNSHoAjCgA1A4iKiAgCiYkFBIKP1Y/SBYApj90AUQAWD+oPzo/hio",
    "EKAQWAIAAhgg/OD+CJAB0AK4IAADAGj/SAeYBngAGwAhACcAAAEzESEQAgYjIicnFjMyNhIRIRAABSckABEhNSEBEhMHAgMlFwIDJxIDCKACSEiYqICAKJiQYFAw/mD+uP6wcAFAASj92AIoA6CQYKBYiPtYmGCo",
    "mKAGeP6w/PD94JAYsBhQAggCIP3I/ZiokKACIAH4mP6w/uj+uEgBWAEIMDD+sP74UAEA//8AaP9IB2gGeBImBvcAABAGB2kAAP//AEj/MAdQBngSJgb2AAAQBgWiAAD//wBw/0AHeAaIEiYHDwAAEAYHEQAA//8A",
    "aP9IB2gGeBImBvUAABAGBeAAAP//AFj/SAdoBngSJgeAAAAQBgb1AAD//wCA/zgHqAZ4EiYF0wAAECYF3wAAEAYFLwAAAAMAaP9wB5gGiAAUACcAKwAAARcGByEQAiMiJycWMzI2ESEGBycAExEUFiEgNjcXBgcG",
    "ISAmNREhEQMhESECIJgYMARwcJggOChgIDAw++iQuHABKKhgAXgCSJAQoDBwWP1w/iCYA2ig/dgCKAaIIGhY/Kj+yAioCOACcPCgaAEQ/Mj+gCgQUKg44EgwQHAD8P2wAbj+4P//AFD/SAeYBngSJgjIAAAQBgcc",
    "AAAAAgDQ/5AHcAY4AAcAGwAAARUhESEVIREBFwYHFhcHJicGASc2ASYlNwQXNgcw+kAGAPlgBNiYmMDYwIC40KD+iGDwARDo/viAAQDYsAY4mPqImAao/vhQ+PDY6IDo2Mj+6JCgASjo2GDQ0NAAAQB4/0gHiAZ4",
    "AAsAABMhETMRIRUhESMRIXgDMKADQPzAoPzQBAgCcP2QmPvYBCgAAQCI/0AHgAZQABIAAAEXBgURIRUhESMRITUhEQQFJyQGeIi4/ggDMPzQoPzYAyj++P6gaAPABlCQMDj+EJj8cAOQmAHYGBigSAABAID/SAeA",
    "BngAHgAAARcGBxEhETMRIRUhESMRIRUQAScAETUhNSERBgcnJARASLjQAlCgAZD+cKD9sP4IaAG4/igB2LDAOAHwBliQQDD+IAMA/QCY/GgDmCj96P6wiAEwAbAomAG4KCCYSAADAHj/QAeIBoAAEwAZAB8AABMh",
    "ETMRIRUhESEVIREjESE1IREhARcGByc2JRYXByYn2ALYqALQ/TADMPzQqPzIAzj9KAVokICYeJj8AKBgmFiYBBACcP2QmP6wmP2wAlCYAVACsEj4iHCYuKDAWMCoAAYAiP84B3AGiAAFABsAHwAjACcAKwAAARYX",
    "ByYnJRcGByERIRUhFSERIxEhNSE1IREhNgEhNSEhFSE1ASE1ISEVITUCqFhAkDhYA0ioOFgBMP2gAyD84Kj84AMg/aADgGj8uAHA/kACaAHA+9gBwP5AAmgBwAaIWHBAcFhAKJB4/Ji4kP6QAXCQuANomP4A0NDQ",
    "/cjQ0NAAAgBo/0gHmAZ4ABwAOAAAEyE1MxUhFSEVIREUBiMiJycWMzI1ESERIxEhNSEBFhczNjcXBgczFSEVIRUhESMRITUhNSE1ISYnaANIoANI/LgC0HBwYIgosFhQ+uCYAuD8uAKYaEDAQDCgMDj4/kAB8P4Q",
    "mP4IAfj+QAEQOEgFuMDAmMD7uGBoEKAQUAOQ+3gFGMD+iHB4eHgocFiQsJD+sAFQkLCQUEgAAgEw/0gHKAZ4AA8AEwAAATMRIRUhESERIzUhFSMRIQEhESEDWKADMPzQAsig+7CgAij+eARQ+7AGeP6gmP6I/ECI",
    "iAPA/WACCAACAJj/SAd4BngACwAVAAABFSEVITUhETMRIRUBMxUEBQckJREjBCgDUPkgAvCgAnj86KABeAEQaP74/uigBND4oKACoP7wmP4Q0KiYmKiI/eAAAQB4/6gHcAYIABYAAAEhNSEQAiMiJycWMzI3NhEh",
    "ESEVITUhAyj96AXQcLCIgCiYmEgQIP2QA6j5CAKwBXCY/HD+2CCoIECQAqj60JiY//8AyP9IB1AGgBImCKgAABAGBS4AAP//AND/SAdQBgASJgWZAAAQBgioAAD//wBY/0gHWAZ4EiYFmgAAEAYH+AAA//8AeP9g",
    "B6gGeBImBigAABAGBS0AAAABAFD/QAdwBjgACQAAARUhERADJxIREQdw+hiokJgGOJj9aP3o/lBYAagB+AMA//8AUP9AB3AGOBImANEAABAGBSwAAP//AFD/QAdwBjgSJgDRAAAQBgUrAAD//wBQ/0AHoAY4EiYA",
    "0QAAEAYFKgAA//8AUP9AB4gGOBImANEAABAGBSkAAAABAGj/OAegBngAIQAAEyERMxEhFSERIRUhAgckJSYnNxITByYnBAUnJBMhNSERIegCwKACsP1QA1j8aPDoAZgB2FBoiPCoqDA4/bD9sEgBYNj9IANA/UAF",
    "YAEY/uiY/mig/mjIGHCQiED+2P6gUHhwkBCo+AFwoAGYAAUAYP9AB6gGgAARACYALAAyADgAAAEXBgckJSYnNxYXByYnBAUnJAEhNxcGByEVIQQFByQBIQIFJyQ3IQUXBAUnJAUXBAUnJCUXAAUnJANIkKCoAXAB",
    "iEhQgMjAeDhA/cj9iCgBOP4IApBQmBAYA9D9+AEQARBg/rj+uP6g4P4wSAFwqP34BEBo/sD+AFACEAHwaP5g/WhYAqgCcGD+EPxoWAPABoAo0HAQMEBAWJDAgEBASBiIgP6IeDggIJjAaKCYATD+8HiQWKBQeMho",
    "gHgwePiAiJAQcP6YaIiAAAIAiP9AB3gGEAAQABcAAAEjNSECAQQFByQBAAUnJAEAAQATIRITFgGQeAWIUP5YARABwGD+UP7A/rj+GHACGAEQ/lgCIAFYWPxgUKBABXiY/Wj+KPjAqLgBMP7QsJjAAQgB+P6AAXgB",
    "4P74/wBgAAEAaP9AB6AGMAAhAAATIRUDIQIBFgUHJCUEBSckNyYDNxIXNhMhJxMhAgEnABMh+ATAkAH4eP7I4AFQeP7I/wD++P5wWAGI6OiogKjo8GD+YCiQ/fhA/hBoAbg4/qAGMIj+cP4A/tiYgJiIwMCIiICo",
    "yAEQYP7ouPABOIgBkPtw/kCIAZAEOP//AGj/QAeoBhASJghHAAAQBghIAAAAAgBo/0gHeAZ4ACAAJQAAARcEBREhAgEXFgUHJicnBgcGByckNwADIxUQAScSEREkARIFABMGgGD94P0wBLg4/pAw4AFoUODY+LBA",
    "qMBYAUDo/riIMP7weOgDAP5wiAEoATA4BniQeBj+uP4w/qgYgHCYSGiIgCBQQJhgmAEAAZjA/iD+cHABcAGQAzAI/Yj+oNgBAAE4AAMAUP9IB2AGcAAkACkALwAAAQYHIRUCBxYFByQlBAUnJCUmJwIFJwATIScT",
    "FwMhNhMXBgchFQE2NyEWARYXByYnA4AoKAOQmODwAShI/rD+6P7Y/nhQAXABAMiQuP6wcAHwmP5AMKiYiAFoQDCYMDADeP2I0Hj9WJABsJCIcICoA/B4aHj+0LCAWJhgsLhYoEiIoOD+wPhwAZgB6IgBgCD+uNAB",
    "ECj4wKD9KJDQ0ASgcJhwkJD//wBo/0gHqAY4EiYFSwAAEAYF3QAAAAYAmP9IB3AGeAAFABMAGQAfADEANgAAARcEBScgBRcGByERIzUhFSMRITYlFhcHJiclFhcHJicTIRUGBwQFByQlBAUnJCUmJyMhFhc2NwbA",
    "UP2Q/HgwAugCaLhgeAFIoPqAoAS4kP4IYCigKFj+mGAooChYKASgkMgBEAGYWP5Q/sD+oP4wYAHIASDokIgBSIDYwHAGeJBQEJB4QLiQ/pDY2AFwyJBwkDiQeCBwiDiQcP2QkOiQeEioWKi4UJBQkJjYqHiAoP//",
    "AKD/QAeABngSJgWEAAAQBga8AAD//wCg/2gHYAZgEiYG2wAAEAYG2gAAAAIBSP9gBsAF4AAHAAsAAAERIzUhFSMREyERIQbAoPvAmJgEQPvABeD5gLCwBoD6yASgAAIAiP9IB3AGeAATABcAABMhETMRIRUhESER",
    "IzUhFSMRIREhASERIYgDIKgDIPzgAlCg/BCgAjj84AGIA/D8EAToAZD+cJD+cPyAiIgDgAGQ/BAByAAEAHj/SAd4BggAAwAHAA0AEwAAASERITchESEBBAEHAiUlFwAFJyQBcAUg+uCgA+D8IAMQAVgBAIj4/qj+",
    "KIj/AP6YcAGABgj8OJgCmPxY6P74iAEo8GBg/qjIgOj//wDA/0gG8AZ4EiYIkQAAEAYFsgAAAAMAaP9IBvgGGAATABsAHwAAEyEQBiMiJycWMzI2EyECBSckEyEBESM1IRUjERMhESHYBiB4uIjAIMiQUDgQ/WBY",
    "/WhYAkBo/cgF+KD72KCgBCj72AYY/cDgGJgYgAF4/aCQoHAB4P0I/LiAgANI/cgBoAADAGj/SAegBggAEQAXABsAABMhFSERFAYjIicnFjMyNjURIQERIRUjERMhESFoBzj+0HCoWEggWFBYOPqYA+D9oKCgAcD+",
    "QAYImPqocGAQmBAoOAUw/sj9QHADMP3YAZAAAwCo/0gHWAaAABAAGAAcAAABABMHJwQFJwATFwAHJCUmJwERIzUhFSMREyERIQWIASCwmGD9SP1ISAGg8KD+6PAB4AJIcIgBoKD74KCgBCD74AWY/wD+4FiYcBCY",
    "AQgBqED+QKgQWIh4/VD8uIiIA0j90AGgAAIAWP9YB3gGeAAZAB0AABMhNjcXBgchFSEGByERIzUhFSMRBgcnABMhASERIYgCeDggqBg4A8j8AGCgBGig/HCgmLhoAcig/cgCKAOQ/HAFKJi4GKCYmPC4/HCQkAMo",
    "kHiQASgBYPvwAdAAAwBo/0gHmAYwAAMABwAbAAABIREhNyE1IQEhFSEDIQIGIyInJwQzMjY3IRMhAVAFMPrQoAPw/BD+eAcw+vBABGgYgIjA6CABALg4OBD7cHD+iAYw/diY+P3gmP8A/kDYEKAQaPgBmP//AKD/",
    "cAeoBoASJgcJAAAQBgWxAAD//wBw/0gHeAaIEiYHDwAAEAYG0wAAAAQAUP9IB6gGkAAMABAAGAAcAAABFwYHAAUHJAEABScAASEVIQURIzUhFSMREyERIQPwqBggAZABuGD+WP5g/oj+IFgCiP7IBLj7SAUAoPvw",
    "oKAEEPvwBpAwICD+wLCguAFw/qDYkAEw/qCg2PzggIADIP34AXAABADI/zgHOAY4ABAAFAAYABwAAAERFAYjIicnFjMyNREhESMRASEVIRchESE3IREhBzhwcGCAIKhYQPrQoAEwBBj76GgDSPy4oAII/fgGOPnY",
    "YGgQoBBQBWj5mAcA/oiY4P2QmAFAAAIAYP9IBxgGeAAfACMAAAEXBgchFQAFIREjNSEVIxEGByckASEHFhcHJicGBycAEyERIQMoqCgwA5D+2P1YA+Cg/DigmKhwBEgBkPzAeIiAcICYYHCQAdBAA8j8OAZ4ODg4",
    "iP4w8PzAeHgC6CggsJgCCHBgcHiAYEhAcAEI+wgBmAADAFD/SAdoBmgAEAAYABwAAAEXBAUVIRUhEAIHJzYSEREkAREjNSEVIxETIREhBqhQ/dj9EAWI+nhwkJCAaANYAlCg/OCgoAMg/OAGaJBQKPiY/fD+QLB4",
    "kAGoAiAByDD8oPyYiJADcP24AbD//wCg/6AHsAZ4EiYHBwAAEAYFsQAAAAMA4P9IByAGgAAWABoAHgAAARcGByERFAYjIicnFjMyNREhESMRITYDIREhNyERIQMwwDBYA7hwaGiIILBYOPsQqAHIUIgDGPzomAHw",
    "/hAGgDhogPq4YGgYoBhQBIj6gAYYeP3o/VCQAZD//wBg/0gHmAY4EiYFTgAAEAYFlgAA//8AcP9IB7AGgBImBZgAABAGBZcAAP//AKD/SAeIBmgSJgfyAAAQBgWrAAD//wBY/0AHMAaAEiYFTQAAEAYFKAAA//8A",
    "oP9IB5gGMBImCJ0AABAGBawAAAACAGj/MAeQBjAAGQAdAAABIREhFSEVIQAFByQBESMRAAUnJAEhNSE1ITchESEBYAUw/cADQP1QARgBmGD+OP7ooP7w/jhwAagBCP1YA0D9sKAD8PwQBjD9cNiY/rCgsOABmP0o",
    "AtD+eOiQyAFImNiYAWAAAwCQ/4gHgAZAAAMABwAbAAABIREhNyERIQEhFSEVIRUhESEVITUhESE1ITUhAWAFOPrIoAP4/Aj+2AZQ/SACiP14Azj5EAMY/YACgP0wBkD9kJgBQP2AmNiY/wCYmAEAmNgABQCA/zAH",
    "aAZIAAMABwAPABoAIAAAASERITchNSEBESMRIREjEQUzERQABSckADU2BQQFByQlAZgEuPtIoAN4/IgEgKD7uKACYKD+kP4wcAHAAUgIAXABOAEwgP74/pgGSP4QmMD+IP0IAmD9mAMA+P7Q0P7AYJBYAQDACMCg",
    "2IDQyAAEAFj/SAcgBkAAFQAlACkALQAAAREUBiMiJycWMzI1ESEREAMnNhIREQEhNTMVIRUhFSEVITUhNSETIREhNyE1IQcgWGB4qCi4cDj7QNCYcFgBMAF4oAGA/oABuPwQAZj+iFADCPz4mAHY/igGQPnYYGgQ",
    "kBBoBWD9aP3g/lhg+AGIASAC+P6AmJiQsJCQsP5I/hiI2AAFAGD/QAeoBpAACwAPACAAKAAsAAABFwcABQckAQAFJwADIRUhBREUBiMiJycWMzI1ESERIxEBFSMRIREjNTURIRED+Kg4AZABsGD+UP5g/pD+KFAC",
    "gOgEEPvwBSBwcEBgKIBASP6AoP04kAJwmP64BpAwOP7gkKCoAUD+0MCQAQj+2JCw/fBoaAioCFgBSPzYA8D9SKADWPz4UJgBkP5w//8ASP9IB1AGgBImBvQAABAGBaIAAAAGALD/SAdIBigAAwAHAA8AEwAbAB8A",
    "AAEhESE3IREhAREjNSEVIxETIREhJREjNSEVIxETIREhAVgFUPqwoAQY++gBsJj+OJiYAcj+OAYAmP5AmJgBwP5ABij9SJgBiP1A/Hh4eAOI/YAB8JD8eHh4A4j9gAHw//8AoP9IB6AGiBImCNUAABAGBbEAAP//",
    "AKD/QAdoBpASJge4AAAQBgWxAAAABgBo/0gHmAZYAAcACwAPACAAJgAqAAATIRUjESMRIRchESE3ITUhASEVIREUBiMiJycWMzI1ESEFESEVIxETITUhuAaY2KD64KgDQPzAoAIA/gD+aAcw/uhQiFhQIGhgOPqI",
    "BFD9KJiYAkD9wAZYmP2AAoCI/liAqP5QmP2gcFgQoBhIAkh4/kh4AjD+0Kj//wCg/0AHiAYoEiYF8QAAECYF8gAAEAYFrQAA//8AqP9IB5gGgBImBbAAABAGBa8AAP//AKj/SAegBoASJgeNAAAQBgWuAAAABgCY",
    "/0gHWAaAACAAJgAsADIANgA6AAATISYnNxYXIRUhBgchERQGIyInJxYzMjURIREjESEmJyEBITY3IRYDFwYHJzYlFhcHJicFIREhNyE1IZgDACAoqDggAwj+kFBQAZhwcDhQIGg4SPtwoAGIQFD+kAKoAVBQQP2g",
    "SAh4gMBguAIwuJBgmLD+SAKg/WCYAXD+kAXQQDg4UGCYkHD70GBgEJgQUAN4+6AE8Ih4/wCAgHj+wFC4cHB4kGCIeJBo8P4IgPj//wCo/0AHmAYwEiYGGgAAEAYFsAAA//8AqP9IB7AGgBImB/QAABAGBa4AAP//",
    "AKj/SAeYBngSJgYUAAAQBgWwAAD//wCg/0gHsAZ4EiYFrQAAEAYFJwAAAAkAWP9IB5gGQAADAAcACwAPACwANAA4AEAARAAAASERITchNSElIREhNyE1IQMhNjcXFAchJic3FhchFSEWBQckAyMGBAUnJDchAREj",
    "NSEVIxETIREhJREjNSEVIxETIREhBGgCmP1omAFg/qD8AAKI/XiQAWj+mLgCmCAImBgBcBggeEhAAQj9oMAB4Dj9yOhoSP5w/sBoAdjI/eAC0KD+uJiYAUj+uAU4oP6goKABYP6gBkD+EJDQkP4QkND9+EhQEEhA",
    "IBhYQFCQoDCQOAEoaMgokDiQ/pj9mEhIAmj+cAEAkP2YSEgCaP5wAQD//wBw/zgHYAaIEiYIKwAAECYILAAAEAYILQAAAAIAuP9IB0gGOAAHAAsAAAERIzUhFSMREyERIQdIoPqwoKAFUPqwBjj5EHBwBvD6GAVQ",
    "//8AuP9IB0gGOBImAQsAABAGBSYAAAAEAOD/SAcoBggABwALAA8AEwAAAREjNSEVIxETIREhBSERITchESEHKKD6+KCgBQj6+AEIAvD9EKABsP5QBgj5QJCQBsD6aAUA+PzwmAHg//8AuP9IB0gGOBImAQsAABAG",
    "B6YAAP//ALj/SAdIBjgSJgcGAAAQBgELAAD//wC4/0gHSAY4EiYHSQAAEAYBCwAA//8AuP9IB0gGOBImAQsAABAGB0gAAP//ALj/SAdIBjgSJgdHAAAQBgELAAD//wDA/0gHQAY4EiYHLQAAEAYHwQAA//8AwP9I",
    "B0AGOBImB8EAABAGBSUAAP//AHD/iAeQBiASJgc8AAAQBgUkAAAAAgBA/1AHgAaAABgAKAAAEyE2NxcGByEVIQIHESMRBgcnNjc1MzY3IQEhETMRIRUhESEVITUhESGAAjg4MKAoKAQQ+6iQkKBYYHCgiGhIWP4Q",
    "AjgB4KAB8P4QAjj66AJA/iAFgICAIHhomP7QuPxQAuhgWICgqIhwqP4YAYj+eJj90JiYAjD//wBY/3AHoAZ4EiYIPgAAEAYIPAAA//8AWP9IB1gGWBImCD4AABAGBgoAAP//AHD/gAeYBmASJgfzAAAQBgfSAAD/",
    "/wBY/1AHYAaAEiYIPgAAEAYFmwAA//8AWP9IB5gGWBImCD4AABAGB+0AAAADAFD/kAeYBoAADwAcACkAABMhETMRIRUhESEVITUhESEBFwYHFhcHJicCBycAARcGBxYXByYnBgcnAPgCsKACwP1AA0j44AM4/VAE",
    "yKAQKLi4gICocKh4ATD8IKAQKLi4gICoaLB4ASgCGARo+5iY/qiYmAFYBIgoiIDI+IDQyP8AuHgBWAHAKIiAyPiA0MjwyHgBWP//AFj/SAeQBngSJgg9AAAQBgfHAAD//wBY/0gHsAZ4EiYIrwAAEAYIPgAAAAUA",
    "gP+QB4AGYAAlACkALQAxADUAAAEXBAUVIRUhESEVIREhFSEVIRUhNSE1ITUhESE1IREhNSE1BScgAREhESMRIRERIREhIREhEQawUP7I/oADEP7YAVD+sAEY/QAC8PmgAtD9GAEQ/rABUP7gAvj9iDAC2AHI/qig",
    "/sABQP7AAeABWAZgkBgYuJD+6Jj+4JDYkJDYkAEgmAEYkLAQkP0oARj+6AEY/uj+SAEg/uABIP//AGj/gAeQBlgSJgduAAAQJgbHAAAQBgbGAAD//wBY/0AHsAZ4EiYIPQAAEAYGSQAAAAUAUP+AB7AGeAAfACMA",
    "JwArADsAABMhNTMVITUzFSEVIREhFSEWBQckAyECBSckNyE1IREhBSE1IREhNSERITUhAyE1MxUhFSEVIRUhNSE1IagBSJAC+JgBUP6wAZj+KLgBKFj+kOD9+ND+eFgBWJD+MAGI/rgB2AL4/QgC+P0IAvj9CFgB",
    "gKABgP6AAsD6AAKg/oAF8IiIiIiQ/WCQqFiokAEY/wCoiJCQkAKgeHj+eIj+YJD9+LCwkKiQkKj//wCA/3gHiAaIEiYIZgAAEAYFIwAA//8AWP9AB7AGiBImCD0AABAGBYIAAP//AFj/UAdoBogSJgg9AAAQBgXb",
    "AAAAAwBw/1AHqAaAABoAIQArAAABFwYHIRUUAgcWBAUHJCQnAgUnJBMmAwYHJxI3Ehc2EyEGATMRBBcHJicRIwHwmCAwAeiYWKgB8AHYSP4o/hDA0P7gSAEguHBYWHBw8JhYgHg4/ogIAxCgASjQYLDooAaAMKCY",
    "oDj98KDIwAioCMjY/tiIoHgBELgBQLioeAGYMP6w4OgBcBACEP3AiMCQqID9IP//AHD/QAd4BogSJgcQAAAQBgcPAAAABACg/0AHWAaAACYAKgAuADMAAAEXByEVIQchESEGByEVBgcEBQckJQQFJyQlJicGByck",
    "NyERBgcnJBMhNSERITUhExYXNjcCMJgwBFj7YFgEcP0AKDgDUIjwAQABeED+MP7A/tD+UGgBeAEYkHCAiHgBQKj++EhYcAEQoAOA/IADgPyAmICo2IgGgCBwkID9oEBAkKhwSCioMJBwUJg4WGCIYEiQiMACCFhI",
    "eOj+qGj+uGD+AHhQUHj//wB4/1AHWAZ4EiYInAAAEAYHXQAAAAIAgP9ABvgGiAAZADAAAAEXBgchFQAFJyQBIQcWFwcmJwYHJyQ3NzM2ExcGByEVAAUnJAEhBgcWFwcmJwYHJyQECKBAUAKY/sj7oEAECAEY/Vhw",
    "WFhwYHhoaGgBcJgICIi4kDA4Amj+oPsoQASQATD9kIhQaGB4aIBwcGAB2AaIIFBAkP4YoKBoAYBAQEhwWFgwIHCAcAhY/TBIKCiQ/cC4oIgB0GAgSFB4YGA4KIig//8AYP9IB5AGgBImCAEAABAGBSIAAP//AEj/",
    "QAd4BngSJge9AAAQBga6AAAAAQBY/0gHsAZwABIAABMhETMRIRUhEgEHAAECAScAEyGwAuiwAxD9ENgCcFj9yP74sP1IWAMIMP0gBKAB0P4woP0I/vCwAQgCuP24/oiYAbgCaAACAFj/SAegBoAAFAAaAAATIREz",
    "ERQHIRUhAAEHAAECAScAEyEBFhcHJiegAxCoCAMI/PABYAH4WP4A/sDI/XBYAsh4/QgDIJiAcICYBNABsP7AODiY/Pj+yLABWAK4/Yj+aJAB0AKQ/OhggIiQaAADAGD/OAegBngAFwAdACMAAAERMxUhEgUHJAMG",
    "AAUnABMhNTMRIREzEQEhNjURISERFAchEQag+P0QyAIwWP2w8ED+QP6wWAJwmP0A6AJIoP24AaAI/lgCSAgB0AVA/ZCY/lCgsMACKMD+cIiIAQgBYJgCcAE4/sj9kCggAZD+cCAoAdgAAQBo/zgHsAZ4ACUAAAEX",
    "BgchETMRIRUhERQHIRUhEgUHAAMCAScAEyE1ITY1ESEGBycSAgCYICgBgKACgP2AEAMA/Rj4AkBo/ZDQ2P2QWAJosP1AAwAQ/jhggHjoBjggiHgBYP6gmP8AUFCY/li4oAEAAaj+WP7wmAEQAWiYUFABANiQcAEQ",
    "AAQAcP9IB4gGeAASABgAHgAjAAATITYSETMQBxQHIRUhAgUnJBMhARYXByYnBxYXByYnAQQXBwFwA7AwIKAIOAK4/RDY/VhYAmC4/JgB0OjAeLjYaOjAeLjYBEgBIOhw/gACmIABMAIw/cAQ4LCY/ijgkNgBUAQY",
    "gKiAuHjogKiIuHj9MNC4iAGQAAIAaP84B6gGeAAnAEEAABMhNjcXByEVIQchFSEGByEVIRYFByQDIQYFJzY3ITUhNjchNSE2NyEBIRUhByEVIQYHBAUHJCUGBSckNyE1ITY1IdgC2BAIkBAC0P0AMAL4/MAgKAQQ",
    "/niwARhQ/rDY/bDQ/rBY8LD+cAIgQCD+GAI4IBj9WAF4A2D+oBACsP0wEAgBoAEwcP64/pCw/ihIAgiQ/ZgCmBD+mAX4QEAQcJCAiEBAkLBgmIgBIPCwgIiYkEg4iEBA/TiIiJAgGHiYgLhosGiIaNCQQEj//wBQ",
    "/0gHmAZ4EiYGbgAAECYGbQAAEAYG8QAA//8AaP9AB6AGgBImBpYAABAGBSEAAP//AGj/OAegBpASJgWIAAAQBgUgAAAAAgBo/0AHmAZ4ABoAIQAAEyE2NxcGByEVIQIDBAUHJiUABSckJSQlEhMhIQIHFhcSE2gC",
    "YFBAqEBABBj+kGjgAUgBIHDo/nD+sP4YWAHgARD++P7IkHj94ALgcHj44PBQBPDIwBDQqJj98P74qLiguND+4GigaNCAkAEYARj+4MhocAEAAcD//wBo/0AHYAZ4EiYIcAAAEAYHsQAA//8AaP9AB6AGeBImCFIA",
    "ABAGBwgAAP//AGj/QAeQBoASJghyAAAQBgU7AAD//wBo/0AHqAZ4EiYIcAAAEAYIHQAA//8AWP9AB5AGeBImBo4AABAGBo0AAP//AGj/QAeoBoASJggRAAAQBghSAAD//wBo/0AHqAaAEiYGXQAAEAYIcAAAAAEA",
    "eP9IB4gGMAAbAAABIRUEBRUhFSERFAYjIicnFjMyNREhNSE1JCUhAUAFmP7g/qADMPzQcHCQiBhwmGD8yAM4AUgBCPtABjCw8NCImP1ASFAgmCAgAqCY2Mi4//8AiP9AB3gGiBImCGYAABAGBR8AAAACAFj/SAeY",
    "BoAAFwAzAAATITY3FwchFSECBxEjEQYHJzY3NTM2NyEFIRUGBxUhFSERFAYjIicnFjMyNREhNSE1NjchiAI4MCiYQAQI+7CIiKBYYGioeGBwKP4YAtADaIioAgj9+GhoSEgYOEho/agCWIh4/VgFsGhoMKCY/uiw",
    "+/gDSGBYaKiogLhQ0LCQiFiY/lBQSAiYCBgBmJiocHD//wBo/0gHmAaIEiYFYwAAEAYFHgAA//8AmP+IB2gGiBImB1UAABAGB1YAAP//AID/SAeIBogSJgdVAAAQBgUdAAD//wCA/0AHeAaIEiYIZgAAEAYGdAAA",
    "AAMAeP9IB6gGkAANABEALAAAAREjNSEVIxEhJic3FhcBIRUhByEVIREUFjMyNjcXAgYhIiY1ESECAAUnJBMhBzio+tioAvAYIKg4GP1IBIj7ePgGgP3wOHjQSAioEID+yNCI/tAw/sj+0EgB8ED+GAXI/pjIyAFo",
    "UEgwWHD+iJjYmP4AICBI0Dj/AIBIYAI4/rD+mEigeAHo//8AmP9IB2gGiBImCGYAABAGBRwAAAACAHD/UAegBogADQAqAAABESM1IRUjESEmJzcWFwEhFSERIRUhERYhIQchICQnBgcnABMXBgcSFxEhB1io+pig",
    "AxggKKBAIP0ABRD92AIg/eC4AQABiDj+sP3o/oiIYLh4AVA4oBhAoNj9wAXY/qDQyAFYSDgwUGD+aJD+mJD+gBComNDguHgBcAHYKLio/vgwA2D//wCI/0gHiAaIEiYIZgAAEAYFGwAA//8AaP9gB3gGiBImCGYA",
    "ABAGBRoAAP//AJj/UAdoBogSJghmAAAQBgUZAAD//wBg/0AHmAaIEiYIZgAAEAYGmgAA//8AcP94B5AGiBImCGYAABAGCGUAAP//AJD/UAdoBogSJghmAAAQBgZzAAD//wCQ/0gHeAaIEiYIZgAAEAYFGAAA//8A",
    "gP9AB4AGiBImCGYAABAGBRcAAP//AGj/SAeYBogSJghmAAAQBgZYAAD//wBw/0AHqAaIEiYIZgAAEAYFFgAAAAIAgP9IB3AGeAAVABsAABMhETMRIRUhERQGIyInJxYzMjY1ESEFEhMHAgOABJCgAcD+QFB4oJgg",
    "oKAgIPtwAbjYiJiA2AUQAWj+mJj7uIhgIKggKEAEIJj/AP7YWAEgAQj//wBo/1AHkAZ4EiYIBQAAEAYH5gAA//8AmP9IB3AGOBImBYcAABAGBRUAAP//AEj/SAeYBoASJgfVAAAQBgh2AAAAAwCA/0gHmAZ4AAwA",
    "EgAYAAABMxEUBiMiJycWMzI1ARcCAycSARITBwIDA8igUIiwmCC4sDj+MJiQ4KD4BJjooLCQ4AZ4+ZhwWCCgKEgEyDj9qP5YaAGwAiD+OP3oUAIwAcAABABo/0gHaAZwAAMACQAPABYAAAEzESMBFhMHAiclFwID",
    "JxIBFwAFJyQAA6CgoAJg2JCgiND8cKCI2JjgBNBw/fD8KFgCOAKYBnD7OAQA+P7YSAE48Dg4/jD+wGABSP8AgP2AuJiIAWgABABo/0AHmAaAAA8AHQAjACkAAAECBycAExcGByEVBgcnNjcFMxEUBiMiJycWMzI2",
    "NQESEwcCAyUXAgEnAAIooHCQATCIoDA4BMBomIBwSP14oHC4kHggiIhgQAIg8KComOj8uKjI/wCgASgEsP7ocHABUAGYMIiAkLCQWHBwkPvwcGAQmBAoOAL4/rj+gEgBkAE4QDj+WP7gWAFY//8AaP9IB5gGaBIm",
    "CE8AABAGCFAAAP//AGj/iAeQBmgSJgbqAAAQBghPAAAABACo/1AHWAZ4ABEAFwAbADAAAAEzETM2NxcGByERIxEhESMRIQEWFwcmJxMhFSEFIRUhAgckJSYnNxYXBycEBSc2EyEDsKDAgFiwYHABkKD6kKADCP6A",
    "cFCIUIBgBAj7+P7YBkj8gKigAZgBwFBggPCQmFD90P2AKPC4/fAGeP5oqMAwsIj+OAEw/sAB2AFgeJBIkID9mJi4mP7ggBA4YFhQ0OhYiFAYkJgBGP//AFj/SAeoBngSJgc3AAAQBgc2AAAAAgBg/0gHoAYYABIA",
    "FgAAARUQASc2EhERIREjNSESAQcAAwEhESECEP7omJh4BXig/lCQAnh4/XCgAlD7yAQ4A0hQ/ej+aGDwAYABGALo/MBw/eD+wJgBeAKAAjj+YP//AFD/QAeoBkgSJghpAAAQBgUUAAD//wBQ/0AHYAZIEiYIaQAA",
    "EAYFEwAA//8AUP8wB3gGSBImCGkAABAGBRIAAP//AFD/OAdwBkgSJghpAAAQBgURAAD//wBQ/0AHiAZIEiYIagAAEAYIaAAA//8AUP9AB1gGSBImB54AABAGBRAAAP//AGj/QAcoBngSJgeaAAAQBgUPAAD//wBY",
    "/0AHmAZ4EiYHkwAAECYGNQAAEAYFDgAAAAEAeP+IB4gGCAALAAATIRUhESEVITUhESHIBnD9EANA+PADMP0gBgiY+rCYmAVQAAEAaP+IB3gGeAAcAAATITY3FwYHIRUhAgchFSERIRUhNSERIQYHJwATIbAB+CgQ",
    "mBAYA/j74FBwBIj9sALY+YgDAP4YiLB4AYiQ/jAFUJCYIIiAmP74wJj9yJiYAjjguHgBqAHYAAIBKP+IB4gGMAALAA8AAAEVIREhESERIRUhERMhESEHYPpoBQD7AAXA+aCgBGD7oAYwmP6Y/WD+kJgGqPv4AXAA",
    "AQBo/4gHcAaQADUAAAEWFyE2NxcGByEVIQYHIRUhByEVIQYHIRUhESEVITUhESEGByckEyE1ITY3ITUhNjchNSEmJwKgWEABiFgwuDhIAbD9KBAYAsD9EEgDuPv4QEgEIP2gAsj50ALI/lDA0FgBUOj9+AJoKCj9",
    "sAKAGBD9KAGgMDgGkGh4eGg4YEiYWFiQsJhwWJj+8JiYARCoUJCIAUCYSGiQWFiYUEgAAQEQ/3AHgAYgABsAAAEhESM1IREUFiEgNyQ3NhMXAgcGISAmNREhESEBEAWIoPvQoAHoASgQAQAgIBigKFA4/YD9uOAE",
    "0PsYBiD8iHD9QDAgCBAYOAEIWP7QSDhIcAOIAdgAAQDA/4AHeAYIAB4AABMhESM1IREUFiEyNjUyNjY3FwIGISMgJjURMxEhESHABcCg++iYAZDg4KBQMAigOOD9kKD+mMCgBBj64AYI/HCA/Yg4KAgIOKiQQP6Y",
    "eFhoBFj++AHgAAEAWP9IB4AGiAApAAATITY3FwchFSEGByERMxEhERQGIyInJxYzMjURIREjESERIxEGBycAEyGIAkhIOKBgA/D7yFCAAaCgAkBwaFhwKJhQQP5goP5ooICgaAFA6P4IBXCIkDDomKDIATD+0P1w",
    "YGAYmBhQAdD8cAOQ/RgCuKCIaAFQAaAAAwCQ/zgHaAaAABsAIwA8AAABMxUhNTMVITUzFSEVIRUjNSEVIzUhFSM1ITUhAREjNSEVIxEBERQGIyInJxYzMjURIREjESERIxEhNTMVAdCgAUCgATigAUD+wKD+yKD+",
    "wKD+yAE4BZig+migBfBgaFh4KKBQQP5YoP5YoAJIoAZ4wMjIyMiY+Pjw8Pj4mP4w/pDg6AF4/nD+QGBgEJgQUAEI/XACkP4IAojAwP//AIj/KAeABngSJgfwAAAQBgatAAAAAwCY/0AHYAZ4ABcANAA4AAABMxEz",
    "NjcXBgchESM1IRUjESEmJzcWFzMBIREhFSERFAYjIicnFjMyNTUhESMRIREjESE1ITchNSEDoKD4UDioQEABeKD6eKABcDBAiGA46P44BED+OAKIcHBIaCCIQEj+GKD+GKACiP4omAMQ/PAGeP7geIAwcFj+sMjI",
    "AVBoYEB4kP7o/jiQ/ohYYBCQEEjQ/eACIP5YAjCQgMj//wCI/0gHcAZ4EiYH8AAAEAYGJAAA//8AYP9IB8AGeBImB8QAABAmBY4AABAGBQ0AAAABAJj/SAdoBfAADwAAASEVIREhFSERIxEhNSERIQEABgD9UAMY",
    "/Oig/OgDGP1QBfCY/eCY/KgDWJgCIAADAID/UAeABigADwAVABsAABMhFSERIRUhESMRITUhESEFFwIHJxIlFhMHAifgBjj9QAMo/Nig/MgDOP0oBTCoaIigmPwImGioYJAGKJj84Jj9eAKImAMgYDj+uOhYARDo",
    "6P7gSAEg6AADAHD/KAeYBogABQAhACUAAAEWFwcmJyUXBgchFSERIRUhESMRIQIBJyQTITUhESE1ITYDESERAlhwaIBggAOgsGBgAdj+eAHo/hig/fAY/ghYAbAY/hAB8P6IA8BwCP3wBohokGiAgFgwwIiY/jiY",
    "/TgCyP44/uCQ8AFomAHImLD88AHI/jgAAQBI/0AHaAaAABAAAAEVIREQAyc2EjURISYnNxYXB2j6UNiYcGAC+CA4oEggBZCY/bD+CP6QWOgBaPgCsGBYOHCA//8AUP9IB2gGgBImCDcAABAGBQwAAP//AFD/SAdw",
    "BoASJgg3AAAQBgULAAD//wBI/0AHmAaAEiYBdQAAEAYFCgAA//8AUP9IB4AGgBImCDcAABAGB5AAAP//AFD/OAdoBoASJgg3AAAQBgUJAAD//wBQ/0AHoAaAEiYINwAAEAYFCAAA//8AUP9AB6AGgBImCDYAABAG",
    "BQcAAAABAGD/QAegBhAAHgAAARYXNhMhJwEhNSEVBgchAgMWISEHISAnBgcnNjcmJwFYOEhoOP54EAFo/kgCeLCgAWgguJgCeAJIQP34/WjYgKhgoHhwOAJ4sHCoAUCQAaiYmOi4/jD+wKCwyJBwkGiImOj//wBg",
    "/0AHoAZwEiYBfQAAEAYFBgAA//8AeP9IB7AGeBImBggAABAGB+kAAAACAHj/OAeQBiAAFwAdAAABIRUhESEVIREjESECAScAEyE1ITY1ESEhERQHIREBGAYA/sgBsP5QoP3AUP5QeAGQSP4YAfgI/qACAAgCMAYg",
    "mP3QmPyIA3j9kP7oeAEAAhCYWGABeP54WFACMP//AGj/OAeYBkASJgZqAAAQBgUFAAAAAwCQ/0gHkAZ4ABgAHgAtAAATISY1MxQXIRUhEhMWMzITFwIGIyIDAgMhARYXByYnASEVIRE2NxcEBSc2NxEhkAPoELAI",
    "Alj9sCiYaEBIKJAoeGCIiMg4/BAFiIhoaHCA+yADUP6Y4LgY/lj98CDQuP64BSCosLigmP3w/oj4AXg4/sjIARgBqAKAAfBIaIB4UP0wmP4AICiYaECoGCACGP//AMD/SAbABngSJgfvAAAQBgi/AAD//wCI/0AH",
    "qAZoEiYIwAAAEAYFPAAA//8AiP9AB7gGeBImCIYAABAGCMAAAP//AIj/SAegBnASJgjAAAAQBgZAAAD//wCI/0AHmAZAEiYIwAAAEAYFgQAA//8A2P9IB1AGeBImB1oAABAGBYAAAAADAPj/SAb4BoAAEQAXAB0A",
    "AAEzESERIzUhNSERITUhESE1IQEWFwcmJyUXAgcnNgOwoAKQoPq4BUj6+AUI+sgCqP3goGiYYKAFUKhoiKCYBoD9cPtYcJgBOJgBOJgCQMDYWNjAUDj++LBY0P//AID/QAeYBkgSJgWNAAAQBgUEAAD//wBY/0gH",
    "qAZoEiYIjAAAEAYIGgAA//8AaP9IB6gGaBImCBoAABAGBdQAAP//AFD/SAdoBoASJgWMAAAQJgfnAAAQBgUDAAD//wBQ/0gHmAZ4EiYIggAAEAYI0gAA//8AYP9AB6gGeBImCNEAABAGBgwAAP//AGD/QAeYBoAS",
    "JgjRAAAQBgbOAAD//wBY/0gHsAaAEiYIgwAAEAYIOAAA//8AYP9AB5gGeBImCNEAABAGB+4AAP//AFj/QAeABngSJgiDAAAQJgiAAAAQBgiBAAD//wBQ/0AHmAZ4EiYIggAAEAYIXwAA//8AWP9IB6AGeBImCIMA",
    "ABAmCBgAABAGBQIAAP//AFj/QAeoBoASJgiDAAAQJgi3AAAQBgUBAAAABABw/4AHsAZgAAUAFwAdACMAAAEEFwcCJQMzERQWMzI2NjcXAgYGISAmNQESEwcCAyUXAgMnEgMwASDogPD++ECoULjgeDAIqBBQoP7I",
    "/vCgBCigaLBgmPswoFhwoIgGYKjwmAEIsP6o+9AgICh4+DD+6LBASGAEEP6Y/lBQAcABYCg4/ej+kFgBuAAEAGj/WAegBmAABQAjACkALwAAARYXByYnAzMRAAEXAAEVFBYzMjY2ExcCBgYhICY1NQYHJyQ3ARcC",
    "AycSARITBwIDA2jQgJh4yFCgAZgBQJj+gP4QUMDoaDAIqBBQoP7Q/vCgyOhIARjg/qCgKKCgoAWQmHCgaJgGYND4WPDY/qD9CAFgAvhI/Jj+eHgoIDB4ARA4/ti4SEhoQJBwiJiwA1Ao/jj+gFgBiAFY/qD+aEgB",
    "qAFQ//8AaP94B5AGeBImBYsAABAGBw0AAP//AFD/SAewBngSJgivAAAQBgiwAAD//wBI/3AHqAaYEiYHyAAAEAYFAAAA//8ASP9wB6gGeBImB8gAABAGBP8AAP//AEj/cAeoBngSJgYsAAAQBgfIAAD//wBI/3AH",
    "qAaAEiYFUAAAEAYHyAAA//8ASP9wB6gGIBImBeoAABAGB8gAAP//AFj/SAegBngSJgixAAAQBgYHAAD//wBQ/3AHqAaAEiYIQwAAEAYE/gAA//8AUP9IB6gGeBImCH8AABAGCLAAAP//AFj/QAewBngSJgixAAAQ",
    "BgbPAAD//wBQ/3AHqAaQEiYGwAAAEAYIQwAA//8AUP9IB5gGeBImCJoAABAGB/8AAP//AFj/OAeIBngSJgixAAAQBgVcAAD//wBQ/3AHqAZ4EiYIQwAAEAYE/QAA//8AYP9QB7AGgBImBhgAABAGB0YAAP//AGj/",
    "YAegBpASJgipAAAQBginAAD//wBY/1gHqAaIEiYIngAAEAYE/AAA//8AWP9IB5gGeBImCLEAABAGCBIAAP//AGj/SAegBngSJggFAAAQBghuAAAAAgBQ/0gHmAZ4AAUAPAAAARYXByYnBRUhEhM2ExcCAxIzMjY3",
    "FwIjIgMGByc2NwIDIREhAgIjIicnFjMyNhMhFRADJzYSNREhAzMUFwYQWECQOFgBqP3gGGhwUKBgsIBIGDgQkEiomKCYuFDAkJAg/TACIAhggFBgGGBYKBAY/ojAkGhQA2AQqAgGeFhwQGhg8JD+QP7Q6AFQQP5Y",
    "/uD++HhwQP6wASC4aKBwuAFwAjj+sP3I/tgQoBBYAeBQ/jj+mFjYAUjwAoABMKCQAAIAaP9IB6gGgABFAEsAAAEXBgcRISYRMxAXIRUhEhc2NxcCBxIzMjY3FwIjIgMGByckNwIDIRE2NxcGBxEUBiMiJycWMzI1",
    "EQYHJzY3ESE1IREFJyQlFhcHJicDsEiQqAH4GLAQAjj90CBAcGCYiKBwQBhAEIhIsJCQyPhQASCoYCD9+LCQIKi4UHiQgCiQkDjA0CDoyP5QAbD+2EABoAPooGCQWKgGSJAgIP7g+AEw/sjwoP8A8KDQUP7YwP74",
    "WFA4/uABOLB4kJCwARgBeP7AKDCgODD+aIhgILAoaAFIMCiwKCgBcKABCDCgKGCguFCwmP//AGj/SAewBoASJgcxAAAQBgcwAAAABQB4/0gH0AaAACIAKAAsADAANgAAEyERMxQXIRUhEhM2ExcCBxYWMzITFwIj",
    "IiYnBgcnJDcCAyEBFhcHJicBIREhNyERIQEXBAUnJHgEAKAIAmj9oCBYeGCQgJhAmDAwEJgosEDYWLjoUAEAoJAo+/gGAFhAoDBQ+xACsP1QoAFw/pACaBj+cP4YIAIYBVABMKCQmP5o/ujYARBI/ojwmLABMCj+",
    "SMCo2JCYqNgBcAHoAchgeEiAYP3I/aiYASj9uJiAUKhQ//8AiP9AB5gGeBImBy4AABAGBy8AAP//AFj/SAegBoASJgegAAAQBgefAAD//wBo/0AHsAZ4EiYFbwAAEAYE+wAAAAIAaP9IBxAGeAARABUAAAEhESEV",
    "IwICBycAExEhJic3FgEhESEEsAJg+wgICICYiAEAEAKIKECgUP2QBFj7qAU4/Vgg/uD+oKh4ARABsAK4kHg4mP1IAXj//wBY/0AHmAZ4EiYG1gAAEAYG1QAA//8AaP9IB5AGYBImBUYAABAGBPoAAP//AFj/QAdA",
    "BngSJgbWAAAQBgT5AAAAAQBo/1AHmAaAACQAAAEXBAURIRUhESEVIREUBiMiJycWMzI2NREhNSERITUhEQQFJyAGwFD+0P6IAqj9WAMw/NBYiIh4IICIMCj8oANg/SgC2P6w/oA4AwAGgJBIMP64oP7goP5YeGAY",
    "qCAoOAGAoAEgoAEwIBCoAAEAoP9IB2gGeAAaAAATIREzESEVIREUBiMiJycWMzI2NREAAScAASGgBJCgAZj+aGCImIggkJg4KP4w/choAnAB4PuQBRABaP6YmPugcGAQmBAoOANg/ej+2IABQAJY//8AUP9IB5gG",
    "eBImB/cAABAGCG8AAP//AFD/SAeYBngSJghvAAAQBgbzAAD//wBQ/0gHmAZ4EiYG/QAAEAYIbwAA//8AWP9IBzgGeBImB1wAABAGBaoAAP//AFj/SAeQBngSJgi8AAAQBgXSAAD//wBQ/0gHmAaAEiYG/gAAEAYI",
    "bwAA//8AUP9IB1AGeBImBYAAABAGCG8AAP//AFj/SAeYBngSJgc5AAAQBgi8AAD//wBQ/0gHoAZ4EiYIbgAAEAYIbwAAAAMAWP9QB7AGOAArADgAQwAAASEVBAUVMxUjFSEVIRUhFSERFAYjIicnFjMyNREhNSE1",
    "ITUhNSM1MzUkNyEBFwYHEhcHAAM3Fhc2JSECAgcnNjc2EyEBSAVw/uj+qNjYARD+8AFg/qBYUKCYGICoMP7IATj/AAEA2NgBKOj7kAXgcKi4iPB4/ohgmAgYmPnoAfgI4OhowFhwEP6oBjiYmIhQiLiIuIj+wFBI",
    "GJgYGAEoiLiIuIigcHD+8IC4cP4Q6IgBeANYKIiAcGj+EP3wuIiQwOABcP//AFj/QAeoBngSJgi8AAAQBgbvAAD//wBY/0AHoAZ4EiYIvAAAEAYFzwAA//8AYP9IB6gGeBImCFMAABAGCCYAAP//AFj/SAe4BngS",
    "Jgi8AAAQBgWpAAD//wBY/0AHmAZ4EiYIvAAAEAYFqAAA//8AUP9IB4gGeBImCG8AABAGB/IAAP//AGD/SAeoBoASJggjAAAQJgewAAAQBgevAAD//wBg/0gHmAZ4EiYIUwAAEAYF3gAA//8AUP9IB1gGeBImCG8A",
    "ABAGBccAAP//AFD/OAegBngSJghvAAAQBgT4AAD//wBY/0gHkAaAEiYIvAAAEAYGaQAA//8AYP9IB6AGgBImCBMAABAGCLsAAP//AFD/QAeYBngSJghvAAAQBgZfAAD//wBQ/0gHsAZ4EiYIbwAAEAYG2QAA//8A",
    "UP84B5gGeBImCG8AABAGBdoAAP//AFj/SAeYBoASJgi8AAAQBgWQAAD//wBQ/0gHQAaAEiYIbwAAEAYGAQAA//8AWP9IB5gGeBImCLwAABAGCJQAAP//AGD/SAeYBoASJgi7AAAQBgVeAAD//wBY/0gHUAZ4EiYI",
    "vAAAEAYIXQAA//8AYP9IB5AGeBImCLsAABAGBWEAAP//AGD/SAeABngSJghTAAAQBgWRAAD//wBg/0gHqAZ4EiYIUwAAEAYI1gAA//8AYP9AB3gGeBImCLsAABAGBqQAAP//AGD/OAegBoASJgi7AAAQBgbRAAD/",
    "/wBg/0gHoAaIEiYIuwAAEAYI1QAA//8AeP9IB6AGiBImBr0AABAGByAAAP//AFD/SAeYBoASJghvAAAQBgbMAAD//wBg/0gHmAZ4EiYIUwAAEAYInwAA//8AUP9IB4AGeBImCG8AABAGBosAAP//AED/QAeYBngS",
    "JgiTAAAQBgVBAAD//wBg/0gHuAZ4EiYIuwAAEAYGowAA//8AUP9IB2gGeBImCG8AABAGBpEAAP//AGD/QAeIBogSJghTAAAQBgaQAAD//wBY/0gHoAZ4EiYH6wAAEAYIvAAA//8AWP9AB4gGeBImBfEAABAmBfIA",
    "ABAGBWsAAP//AED/SAegBngSJgiTAAAQBgdLAAD//wBg/0gHqAaAEiYIuwAAEAYHQAAA//8AYP9IB4gGeBImCLsAABAGBkEAAP//AGD/QAeYBngSJghTAAAQBgV/AAD//wBA/0gHkAZ4EiYIkwAAEAYGOgAA//8A",
    "WP9IB5gGgBImBjsAABAGBWsAAP//AED/SAegBngSJgiTAAAQBgZIAAD//wBg/0gHkAZ4EiYIUwAAEAYFgwAA//8AYP9IB5AGeBImCLsAABAGBZMAAP//AGD/SAegBoASJgi7AAAQBgeNAAD//wBg/0AHiAaAEiYG",
    "lAAAECYIIwAAEAYF8gAA//8AYP9IB5AGeBImCLsAABAGBUoAAP//AGD/SAeIBngSJghTAAAQBgYjAAD//wBY/0AHmAZ4EiYGJgAAEAYFawAA//8AYP9AB5AGeBImCFMAABAGBlMAAP//AFj/QAewBngSJgYOAAAQ",
    "BgVrAAD//wBg/0gHkAaAEiYIUwAAEAYGDwAA//8AYP9IB6gGeBImCFMAABAGBhkAAP//AFj/MAd4BngSJgVrAAAQBgT3AAD//wBY/0gHkAZ4EiYF3AAAEAYFawAA//8AWP9IB5gGeBImBb4AABAmBb0AABAGBWsA",
    "AP//AGD/SAewBngSJgi7AAAQBgYLAAD//wBg/0gHmAaAEiYIuwAAEAYF1wAA//8AYP9AB6gGgBImCCMAABAmCLcAABAGBPYAAP//AFj/SAeoBngSJgXWAAAQBgVrAAD//wBY/0gHmAaQEiYIPwAAEAYFawAA//8A",
    "WP9IB7gGeBImB/EAABAGBWsAAP//AFj/SAegBoASJgcgAAAQBgV9AAD//wBg/zgHoAaAEiYIIwAAEAYFWAAAAAIAiP9AB4gGeAAdACIAABMhETMRIRUhESEVAgUEBQckJQQFJyQlJAMjNSERIQESBSQTkAMYoAMo",
    "/NgCcKD+uAEgAZhA/jD+qP6I/ggoAdgBMP7gwIACePzoAcjQAQgBOJgFcAEI/viY/siI/oDggEiwSMjIQJAwqNABiJgBOP4w/piYyAE4//8A0P9AB6gGeBImCLkAABAGB1MAAP//AJD/QAeoBngSJgi4AAAQBgi5",
    "AAD//wBo/0AHqAaAEiYHaQAAEAYFzAAA//8AWP9AB6gGeBImBqEAABAGCBcAAP//AEj/QAegBngSJgi6AAAQBgaeAAD//wBo/0AHoAZ4EiYGnwAAEAYIugAA//8AUP9AB6AGgBImCBkAABAGCIgAAP//AGj/QAeo",
    "BngSJgVqAAAQBggXAAD//wB4/0AHqAZ4EiYIFwAAEAYE9QAA//8AaP9oB5gGgBImBbMAABAGBPQAAAACAFD/OAeIBnAAGQAeAAATISYnNxYXIRUhAgAHBAUHJAEEBSckJQADISESAQATgAM4SFCIeFgDCP7IQP7o",
    "YAEgAdhg/kD+mP6w/hBwAeABSP64iP7YAdiIASgBKGgFKHhwYJC4mP7Q/kA42KiwmAEg+LiYqOgBQAHo/lD++AEAAbj//wBQ/0gHsAaAEiYGqAAAEAYGqQAAAAMAwP9IB3gGeAALABEAFwAAATMRJRcFESMRBScl",
    "AQQXByYlAwQXByYlBQCgAcgQ/iig+9gYBED9OAEQ0Gjo/wA4ASDwcPj+6AZ4+8g4mDj9oAJQeJh4A7h4qIiwgP6wiLCAwID//wBY/0gHwAaAEiYIZAAAEAYIYwAA//8AcP9IB6gGeBImBXsAABAGBPMAAAACAID/",
    "OAeYBngAJQA6AAATITY3FwYHIRUhBgczETMRIRUhFTY3FwYHESMRBSc2NxEhJzY3IwEXBAURIRUjESMRIQICByc2EhERJJABGCgwkCggAZD+OGBo4KABAP8AgGgYeIig/ngg6MD+gCCAYNgGaFD+8P6YAsjooP7A",
    "CGB4gGhgAbgFYIiQIIB4mPCwAQD/AJDwEBiQIBj+OAGgQLAYIAEQmLDoAbCIUDD+mJj72AQo/hD+YKhokAG4AjAB2DD//wCo/1AHmAZ4EiYFxgAAEAYIVQAA//8AWP9IB5gGiBImCFYAABAGCFUAAAABAID/SAd4",
    "BoAAIAAAARYXIRUhFAchEAIjIicnFjMyNhMhAgEnJBM2ESE1ISYnA9hoOAMA+7gIA4iAwGiYGJhoYEgQ/Qgo/gBYAQiAcP3wAzgwUAaAoLCYsJD9EP7gEKAQuAIg/Zj+8JCIARD4AjCYmID//wBQ/0AHsAZ4EiYI",
    "BwAAEAYFUwAAAAEAcP9AB5AGGAAkAAATIRUhBgchFSERFBYzIDc2NxcGBiEiJjURIwIBJwATITUhNjch8AYg/SAIIANo/WA4gAEAKDAIqBCQ/pjYgEiI/YBwAkiA/VgC0CAQ/WAGGJj4yJj9EBggICjAMPCASFgD",
    "IP2Y/oCAAWACCJjI+P//ALD/OAewBiASJgdQAAAQBgTyAAAAAwFg/0gGmAYgAAcACwAPAAABESM1IRUjERMhESERIREhBpig/AigoAP4/AgD+PwIBiD5KJiYBtj9OAIw+vACSP//ARD/SAdABhgSJgXJAAAQBgTx",
    "AAAAAwB4/0gHiAY4AA8AEwAXAAABIREhFSEVIREjESE1ITUhEyE1IREhNSEBQAV4/ZADQPzAoPzQAzD9mKAEOPvIBDj7yAY4/JDomP4AAgCY6AIA2P3A2P//AJj/UAeQBngSJgfmAAAQBgdCAAD//wC4/0gHWAZI",
    "EiYGAwAAEAYGBAAAAAMAYP8wB0gGUAAlACkALQAAASERIQYHIRAHBiMiJycWMzI2ESMCAScAEyEABSckEyEGByckNyMTITUhESE1IQFoBUj8YDhIBLg4MKBwoCjYYDAw+JD9iIACWIj++P74/ghoAbj4/rB4mIAB",
    "SLDwoAQI+/gECPv4BlD9GFBQ/aCggAioCKgBoP4g/tiIAQABgP6Y0IC4AQBgWICgyAG4oP44oAADAGj/eAdwBkgAIQAlACkAAAEhESEVIRUhFSEVIRUhFSE1ITUhNSE1IQYHJzY3FwchNSETITUhESE1IQFIBXj9",
    "qALA/UACgP2AAwj5IAMw/ZACcP3wUGiQ0GCYMAHA/YigBDj7yAQ4+8gGSP0gwJC4kMCYmMCQuIBgcMDwOHjAAbCg/kCg//8AkP9QB7AGeBImCK0AABAGBUUAAAAEAFD/SAegBlAAAwAHAAsAKAAAASERIRMhNSER",
    "ITUhASEVIRUhFSEVFiEhByMgJCcGBycAExcGBxYXESEBiATw+xCYA8D8QAPA/ED+aAbw/OACuP1I2AFgARA42P4Q/fiQgLiAAVhAoBAokNj80AZQ/SgBsJj+SKD+YJDQkPgooMCo4JiAARABcCBwaLhIAij//wBw",
    "/6gHkAYwEiYIrgAAEAYE8AAA//8AkP9QB8AGiBImBxkAABAGCK0AAAAHAGj/SAeQBngAFwAbACEAJwAvADMANwAAARYXITY3FwYHIRUhESEVITUhESE1ISYnATMRIwUXBgcnNiUWFwcmJwERIzUhFSMREyE1IREh",
    "NSECiGhAAWBAOKg4OAH4/cgCkPjYAoD94AGoOEABkNjYApCIWGBwYPwIWDiQOFAFKKD8MKCgA9D8MAPQ/DAGeHB4cHgwaFCI/miQkAGYiEhI/VABmChIqGBgcIB4iECQcP3I/OBYWAMg/tiY/lCY//8AaP9IB5gG",
    "SBImBpgAABAGBO8AAP//AJD/SAeIBoASJgY9AAAQBgdDAAD//wCQ/0AHkAZgEiYIrQAAEAYGUwAA//8AiP9IB5gGiBImCKwAABAGCKsAAAAGAFj/SAeYBlAAHwAjACcAKwAvAFQAAAEhESEVIRUhFSEVIRYFByQn",
    "IQYFJyQ3ITUhNSE1ITUhEyE1IREhNSEBNSEVFSE1IRMzFRc2NxcGBxYXByYlFRQGIyInJxYzMjU1BAUnNjcmJzcWFzcBUAVo/tABgP6AAeD+gKgBCFD+sND9kLD+uGgBCJj+oAHo/oABgP7QkARA+8AEQPvAAxD+",
    "KAHY/iigoFhIMIhAONCwYPj++FCAWFAgaGAw/wD+wEDQuDhQgFhAaAZQ/bhoiGiQkFCYgPjwkIBwkJBoiGgBYGD+yGD+sGho8Gj+2MggUFhQWEBYaHiYcJBwUBCYGEh4iHCQSEhQSFBQWDAABQBo/zgHiAY4AB8A",
    "IwAnACsALwAAEyEVIRUhESEGBwQFByQlBgUnJDcmJzcWFzY3IREhNSEBITUhIRUhNQEhNSEhFSE1qAaw/PACiP1wGFgBaAJQMP2Y/mjg/jBAAZjAoHCAeJBQGP2IAoD9AAEgAeD+IAKAAej7mAHg/iACgAHoBjiY",
    "qP0A0ICoGKgQ2LBAmDCAaIhQeFhooAMAqP4YsLCw/iCwsLD//wD4/0AHAAaQEiYGAgAAEAYE7gAA//8AeP9IB5gGeBImB64AABAGBO0AAP//AGj/SAeYBkASJgh9AAAQBgh8AAAAAwBo/0AGmAZIABQAGAAeAAAB",
    "ERQGIyInJxYzMjURIQIDJxISERETIREhAyERIRUUBphgYHi4KMB4QPwgSNCYqIigA8D8QAgDyPxABkj54HBwGKAYcAFo/qD+4FgBAAGgARADAP4IAWD8qAFgoGAAAwB4/0AHcAaAACIAJgAqAAATITY3FwYHIRUh",
    "BgchERQGIyInJxYzMjU1IREjEQYHJwATIQEhNSERITUhmAJgODCYICgDwPvwQFgECHBweKgo2GhI/ICgiJh4AWDQ/fACGAOA/IADgPyABaBwcCBgYJh4ePwAYGgQoBBQqP5YA+iQeHABIAFY/bjA/fi4//8AWP9I",
    "B6AGSBImCBYAABAGCBQAAP//AGj/QAdQBngSJgiZAAAQBgflAAD//wBo/0AHUAZ4EiYG3gAAEAYG3QAAAAEAWP9IB5gGeAAdAAABIREzESEVIREhFSEABQckAREjEQABJwABITUhESEBIAKIoAKY/WgC6P2AASgB",
    "wFj+KP7goP7g/jhoAeABAP2AAvD9eAVIATD+0Jj+2Jj+SMCw+AHI/MADQP5A/wCQAQABmJgBKAABAFj/SAeoBngAHQAAEyERMxEhFSERIRUhAAUHJAERIxEAASckASE1IREhiAMgoAMo/NgC2P2IASAB4Fj+KP7Q",
    "oP7o/jBoAdABEP2gAtD84AVAATj+yJD+0Jj+cMCw6AGw/MgDOP5Q/viQ+AGYmAEwAAEAWP9IB6AGgAAeAAATIREzESEVIQABBwABESEVIREjESE1IREAASc2ADchqAMAoAMA/XgBIAHAWP4o/tgByP44oP5AAcD+",
    "6P4waMABqHD9eAUYAWj+mJj9wP74qAE4Alj9SJj+eAGImAKo/dD+sJCAAfDwAAIAiP9AB2gGcAAVABsAABMhETMRIRUhAAEHAAERIxEAAScAASEBFhcHJieQAxigAyD9QAEYAahY/kj+8KD+8P5YaAHAAQD9SATI",
    "sJBwgKgEmAHY/iiY/cj/AKgBKAIw+8gEMP3w/tCIAUACCAJQYHh4iFgAAgCQ/0gHcAZAABMAKQAAASEGBgcnNjY1NSERFDMhFSEiJjUBITUzFSEVIQAFByQBESMRAAUnJBMhBPD+ABCY0HjIkAM4QAEw/qhgWPvY",
    "AvCgAvj9mAEIAYBQ/lj+4KD+8P5QaAGY8P2wBaj4+IBwcOCwmP5QYJBgWP5g6OiY/qigoMgBoP1YArj+aOCIyAFI//8AMP9IB6gGeBImCJcAABAGCJYAAP//AJD/UAdwBogSJgfQAAAQBgiNAAD//wAw/zgHqAZ4",
    "EiYIlwAAEAYHZAAA//8AMP9IB5gGeBImCJcAABAGCHEAAP//AEj/SAeQBngSJgh6AAAQBgh5AAAAAwBY/0AHqAZ4AB0AIQAlAAATITUzFSEVIRUhESEABQckAREjEQAFJyQBIREhNSEBIREhIREhEZADIKADIPzg",
    "Aoj94AEoAchY/ij+2KD+6P4wcAHQARD98AKI/OABOAHo/hgCiAHoBcC4uJDA/Zj+yJCwwAFo/YgCgP6g0JDAASgCaMD9cAE4/sgBOP//AID/UAeYBogSJgcOAAAQBgetAAAAAwBQ/0gHqAZ4AB0AIwApAAATITUz",
    "FSEVIREhFSEABQckAREjEQABJyQBITUhESEFFwYHJzYlFhcHJifIAuigAuj9GANI/UgBEAG4WP4o/tig/uj+KHAB0AEI/UADSP0YBViQiIiAoPwgiFiYUIgFuMDAmP4AmP6IsLDoAcj86AMI/lj/AJDoAWiYAgAw",
    "WNB4cIigoLBYsKD//wBI/0gHmAZ4EiYIlQAAEAYHJAAA//8ASP9IB5gGeBImCJUAABAGBwMAAP//ADD/SAdgBngSJgiXAAAQBgbcAAAABQBo/0AHkAYwABkAHQAhACUAKQAAASERIRUhFSEABQckAREjEQAFJyQB",
    "ITUhNSETITUhIRUhNQEhNSEhFSE1ATAFmP2AA0D9SAEQAbBg/jD+6KD+4P5QcAGgARj9WAMw/YigAdj+KAJ4AeD7qAHY/igCeAHgBjD8wJiY/vCIsLgBWP24AkD+sLiQqAEQmJgB4MjIyP3wwMDA//8AYP9AB6AG",
    "gBImCE4AABAGBU8AAP//AGD/QAeYBoASJgiHAAAQBgTsAAD//wBg/0AHoAaAEiYITQAAECYITAAAEAYITgAA//8AeP+IB4gGgBImBXoAABAGCFQAAP//AEj/QAegBngSJgiVAAAQBgW/AAD//wBI/0gHkAZ4EiYI",
    "lQAAEAYE6wAA//8ASP9AB6gGeBImCJUAABAGBncAAP//AEj/SAeYBngSJgiVAAAQBgaXAAD//wBI/0gHoAaAEiYIawAAEAYIlQAA//8AUP9IB7AGeBImCHcAABAGB+gAAP//AEj/SAeoBoASJgiVAAAQBgaZAAD/",
    "/wBQ/0gHmAZ4EiYIdwAAEAYGbwAA//8AYP9AB5gGeBImCKoAABAGCIcAAP//AGD/QAeYBngSJgiHAAAQBgTqAAD//wBI/0gHaAZ4EiYIlQAAEAYGkQAA//8AUP9AB7AGeBImCEYAABAGBqcAAP//AFD/QAdoBngS",
    "JghGAAAQBgXZAAD//wBI/0AHmAaAEiYIlQAAEAYGVQAA//8ASP9IB6gGeBImBcAAABAGCJUAAP//ADj/SAeQBngSJgbJAAAQJgbKAAAQBgVEAAD//wBQ/0gHoAaAEiYIRgAAEAYFUgAA//8AUP9IB5gGeBImCEUA",
    "ABAGCEYAAP//AEj/SAewBngSJggQAAAQBgiVAAD//wBQ/zgHkAZ4EiYIRgAAEAYF/AAA//8AOP9IB7AGeBImBu4AABAGBUQAAAACAGj/QAeYBoAAEAAfAAABAgcnABMXBgchFRQCByc2NwUzFAcSBQcAAwIFJyQA",
    "EgKgmLiIASiYmCAoBAiAUJB4MP14oBDwAnhw/cDYcP0gWAFQAXB4BLj+qLB4ASgCMCCQeJgY/pCgWNjwWLCQ/cDwqAEQAcD+EOigYAEoAVj//wBw/0gHqAaIEiYHvgAAEAYHvwAA//8AaP9IB6gGeBImCDAAABAG",
    "B7wAAAABAGj/mAeYBngADwAAATMRIRUhESEVITUhETMRIQQgoAKg/WAC2PjQATigAeAGeP24mPyYmJgE8PsQAAEAaP+IB5gGEAATAAATIRUhESEVIREhFSE1IREzESERIcgGkP0wApj9aAMQ+NABMKABsPzgBhCY",
    "/eiY/ViYmAQQ+/AFWAACAFj/cAeoBnAAEAAoAAABMxEhFSERJRcEBSc3ETMRNwEzESQ3FwQFERQWMzI2NjcXDgIjIiY1AoigASj+2AEgGP5A/dggoKDwAiigAQDYaP74/sg4aJhQIAioCECA8Mh4BnD92Jj9AFCY",
    "kGCoGAUI+xgwBej9oGiQkKBw/NgYICB44Dj4oEBIWAADAID/IAeABoAADwAbACEAAAEzFSEVIRUhFSE1IREzESERMxEkExcCAAUnJCUBFwIHJzYDsKACcP2QAzD5AAFIoAFIoAEowKDQ/Vj9qEgBuAE4/qiIqLiA",
    "0AaA+Jj4mJgB6P4Y/wD92LABAED+2P6AeJBQgAJIUP7YqHjIAAEASP9AB6gF8AAxAAATIRUhESQ3FwQFERQWMzI2NjcXDgIjIiY1ESEGByECAScAEyEGBxYXByYnBgcnABMheAcQ/aABIPBo/uD+qECIqEggCKAI",
    "QIjo6ID9+CAwAfBY/RhgAnh4/oAwOKBwYGiYOEB4ARiA/pgF8Jj90GiQkJhw/bgYICho4DD4oEBQUAVIkID8YP6YkAEIAth4aFBwkHBYYFh4AXgB2P//AFj/KAeoBngSJgcsAAAQBge7AAD//wBI/0AHqAZ4EiYG",
    "HAAAEAYH4wAAAAUAcP9QB5gGMAAbACEAJwAtADMAABMhEhMhAgMzFSMCBzMVIwIhIicnFjMyNyESEyMlEjchAgcBFhcHJicBEjchAgcBFhcHJidwAQAYEAVACBDY4BAgyOAw/uhYkCCwWHgg+0A4KPAFuBAI+/AI",
    "GAFY8Kh4sPAC+CAY+/AgIAGg6LB4sPADmAFAAVj+qP7AkP74+Jj+4BCQCIgBOAFgkAEI+P7w8AHIgJB4oID8EAEI+P7o6AHAgIiAoIgABgCQ/zgHmAaAAAoAJQAqADAANQA7AAABFwYHIRUhBgcnAAEhNjchAyEV",
    "IQMzFSMUBiMiJycWMzI3ITYTISU2NSEDARYXByYnARMhBgcBFhcHJicCQJggKASo+wB4qIgBMP7QAUAYEASQEAEg/tgg4PCIcEBwIIhIQBD70Dgg/tAFQBD8sBgBeJBgmFCYAlAY/KAYIAGokFiYUJAGgDBQUJDQ",
    "mGgBGP1w6Pj+IJD+uJhwkBCgEGDgAQCQqKD+uAEwWHBYaGD9UAFIsJgBMFhoWGBg//8AaP9IB5gGeBImCDUAABAGCDQAAAACAQj/SAeYBmAADAAiAAABMxEhFSERJDcXBAUnATMRJDcXBAURFBYzMjY3FwIGIyAm",
    "NQEIqAHw/hABCNAg/wD+sFADOKgBGPBo/uD+sFjweEgQmCCAyP64qAZg/cig/JBYaKh4cFAGyP2ocKCQsID88CAgYMBA/viAYGgAAwCI/0gHsAaIAAkADQAbAAABFwchFSEGBycSFyEVIQchEBIzMjcXAiMiAgMh",
    "AfCYMATw+tBwkJDomASA+4C4BQBASCggkDiggKAI+6AGiDhwmOiwWAEggJCg/jj+QOAw/qgBgAIYAAIAeP9IB6gGeAAaACQAAAEzERYXJBMXAgUSBQcAAREUBiMiJycWMzI2NQEhFRQAAScAEyEDuKBIWAEQyIjQ",
    "/sD4AWhg/jD+4FiIoIggmJgwKPzoAoD+2P7YWAGQgP4YBnj+uLCoqAEAaP7ouP5Q8LgBUAKY/EBwYCCgKCBABHCYQP1A/vCIAXACGAADAFj/SAeYBogABQAhACoAAAEEBQckJQchERYXJDcXAgUSBQcAAREUBiMi",
    "JycWMzI1ESEDIRUCAScAEyECOAHYAahI/kD+QJgDSCgwAQCwgMD+6PgBUGD+aP8AUFCA0CDoWDD9WMgCwMj+MGABsKD96AaIQFiocEDg/tBYWLDwaP7ouP54uLABCAH4/UhYWBiYGDAEaP8AmP4A/uCIARABiAAD",
    "AHD/QAeoBogABQAtADMAAAEWFwcmJwUhETMRIRUhEhc2NxcCBxIFBwADERQGIyInJxYzMjY1EQAFJyQBESEFFhcHJicFiKCIYIiY+4AC+KADEP0oSHiYcKCgsMABUFj98PhQcJiQIJiYIBj+qP5gQAHIAXD9CAEI",
    "iIiQcKAGiFBgcGhIyAEo/tiY/ujYuOBQ/tio/uCgsAEIApj8qHhgIKgoIEAB4P7o0LjYARAB4FCo6HDQ0P//AGD/UAdwBmgSJggzAAAQBgcbAAD//wBY/0gHmAZoEiYI2QAAEAYGBgAA//8AWP9IB4gGaBImCNkA",
    "ABAGBXAAAP//AGj/QAegBnASJggiAAAQBgXIAAD//wBo/0gHmAZwEiYIIgAAEAYFigAAAAQAaP9IB6gGgAAkACgALAA1AAABFwYHIREhFRYXNjcXBgcWBQckAREUBiMiJycWMzI2NREhESE2ASE1IREhNSEBIRUC",
    "BSckEyEDoKgYIAK4/YhggNCggJjg2AEoWP4g/uBQcJCIIJCQIBj9mAIgKP5YBED7wARA+8D+sAKwuP44YAGQmP4IBoAoQDD9ICiQeGiYaJhwwHCg0AGQ/iB4WBigICBAAsgC4Ej+iJj+UJD+QJD+iOCQuAEQ//8A",
    "WP9IB5AGeBImCNkAABAGBaUAAP//AGj/SAegBoASJggiAAAQBggTAAD//wBo/0AHoAZ4EiYIIgAAEAYH7AAA//8AWP9IB5gGeBImCNkAABAGCNIAAP//AGD/SAeYBngSJggzAAAQBgVbAAD//wBY/0gHqAZ4EiYI",
    "2QAAEAYI1gAA//8AWP9IB6gGaBImCNkAABAGBnEAAP//AFj/QAegBoASJgjZAAAQBggIAAD//wBY/0AHYAZ4EiYIfgAAECYF+AAAEAYFYAAA//8AWP9IB2AGgBImCH4AABAmCNkAABAGBycAAP//AFj/SAeQBoAS",
    "JgjZAAAQBgWnAAD//wBY/0gHqAaAEiYI2QAAEAYI2gAA//8AWP9IBzgGgBImCNkAABAGBfcAAP//AFj/QAewBmgSJgV5AAAQJgVnAAAQBgVgAAD//wBY/0AHmAZ4EiYI2QAAEAYGPwAA//8AYP9IB5AGaBImCDMA",
    "ABAGBWkAAP//AGD/UAeoBmgSJggzAAAQBgXvAAD//wBg/0gHmAZ4EiYIMwAAEAYH/wAA//8AWP9AB5AGeBImBj4AABAGBWAAAP//AFj/QAegBngSJgjZAAAQBgYTAAD//wBg/1AHkAZ4EiYIMwAAEAYGIQAA//8A",
    "WP9AB5AGcBImB4gAABAmB4oAABAmB4kAABAGBWAAAP//AFj/QAe4BlgSJgaVAAAQBgVgAAD//wBY/0gHYAZoEiYI2QAAEAYGGwAA//8AWP9AB7AGgBImBVoAABAGBWAAAP//AGD/SAeIBoASJggzAAAQBgYyAAD/",
    "/wBg/0gHmAZ4EiYIMwAAEAYHlAAA//8AWP9AB6AGiBImBn0AABAmBn4AABAGBWAAAP//AFj/SAeYBmgSJgjZAAAQBgXtAAD//wBY/0AHYAZ4EiYFxQAAEAYFYAAA//8AWP9AB6AGeBImCIoAABAmCIkAABAmCBgA",
    "ABAGBWAAAAADAGj/SAegBngAEAAWABwAAAEzEAcVEgEHAAMCASckABM2ARcCAycSARcCAycSA6igCOgCeGj9sNCY/UhgAYABaDgg/jigWJiYmATwoHjImMgGeP3AEEj9KP7goAFQAhD9qP74mJgBoAEIqAGQOP6I",
    "/vhgAQgBODj+iP7wYAEI//8ASP9QB5gGeBImB3oAABAGB/cAAP//AGj/QAeYBlgSJgh7AAAQBgTpAAD//wBI/1AHoAaAEiYI1wAAEAYHXgAA//8AcP9QB5AGeBImBloAABAGBOgAAP//AFD/SAdYBngSJgguAAAQ",
    "BgjYAAD//wBg/0AHqAaAEiYIpAAAECYF0QAAEAYE5wAA//8AaP9IB4gGeBImBrMAABAGBOYAAP//AGj/QAeoBjASJgZnAAAQJgZoAAAQBgikAAD//wBY/0gHuAZ4EiYIJAAAEAYIJQAAAAEAaP9QB5AGeAAYAAAB",
    "FwUSEhMHAgIDBgcRIxEGBxEQAScSEREkBqBg/vAgwMB4yNAokKCgwND+8IDwAwgGeJgw/dj9iP7gmAEgAqgCcBgQ+hAF4BAI/dj9+P5AcAGYAcACwBAABABo/0gHeAaAAAUAHQBAAEUAAAEXBAUnIAUWFzMnNxYX",
    "MzY3FwYHIREjNSEVIxEhJwMhNjcXBgchFSEHIRUGBwQFByQlBAUnJDcnJiYnBgcnJBMhARYXJDcGqFD9oPyIMALg/mhIQPhQiEhA8FgwoDA4AQCg+uCgATBI+AHAMCCoICgEKPuYSAP4kOABAAFQMP4w/sD+2P54",
    "SAE48JAoWDCQuHgBCLj+kAIgmNgBCIAGgJhYEJioYHiAYGCAkJA4gGj+wLC4AUh4/ehocChYWJCIgLhwSAigEIBgMKAgOFggUDi4gHC4ATj++IhYWIgAAQBY/0gHKAZoABQAAAEzESERMxEhFSERIREjESECAycA",
    "EQFwoAJQoAIo+ugD4KD8sDjwgAEYBmD+IAHo/hiY/sD8oALI/lD+6GgBUAHo//8AaP9IB5AGeBImCCEAABAGByMAAP//AGj/SAeYBngSJgghAAAQBgi0AAAAAQBo/0AHgAYwACIAAAEXBgchESE1IRUhESEVIREU",
    "BiMiJycWMzI1ESMAASckASEnAbioUFgDaPuwBpD+YAHA/kBYiKiQIKiwQCD+cP1gaAJoAWj86DAFMCC4uAH4mJj+CJj9CHBgIKgoUALY/hD+8Ij4AYCI//8ASP9IB4AGeBImCKEAABAGCKIAAP//AEj/SAeYBoAS",
    "JgiiAAAQBgbNAAD//wBY/0gHiAaAEiYH4QAAEAYHHQAA//8AUP9AB7AGeBImBvIAABAGBvAAAP//AFj/QAe4BoASJgiGAAAQBgfhAAD//wBY/0gHsAaAEiYH4AAAEAYG4gAA//8AWP9IB5gGgBImB+AAABAGB30A",
    "AP//AFj/SAeQBoASJgfgAAAQBgY8AAD//wBY/0gHmAaAEiYH4AAAEAYFzQAA//8AWP9IB5AGgBImB+AAABAGBUoAAP//AHD/SAeQBoASJggBAAAQJgZFAAAQBgTlAAD//wBo/0gHsAYYEiYHhgAAEAYH0wAA//8A",
    "aP9IB5gGGBImCCAAABAGB+0AAP//AGj/MAeoBjgSJgXDAAAQBgeGAAD//wBo/1AHmAZ4EiYHTQAAEAYFzgAA//8AaP+IB5gGIBImB00AABAGB30AAP//AGD/QAeoBngSJgaMAAAQBgU4AAAAAQCA/5AHmAZ4AB4A",
    "AAEXBgchETMRIRUhESEVIREhFSE1IREhNSERIQYHJwAB+JgwSAHIoAK4/UgCaP2YAxj4+ANQ/ZgCaP3oWHCAAQAGODComAGw/lCY/kiY/kiYmAG4mAG4sIhoATgABQBY/0gHGAYYABgAHAAgACYAKgAAAREUBiMi",
    "JycWMzI1ESERIxEhAgMnNhIRERMhESEhESERASERIRUUJREhEQcYYGBgkCCYWED9+KD96CigmHhgoAIA/gACoAII+1ACCP4AAqACCAYY+iBwcBCgEHABWP3oAhj+sP7YYPABiAEQAuj+IAFI/rgBSPzYAUioUPj+",
    "uAFIAAUAWP9QB5AGOAAnACsALwA0ADgAAAECAyc2EhERIREUBiMiJycWMzI1NSERFBYzMjcyNjcXBgYhIyImNRERIREhIREhEQUVFSERAREhEQHIMLCQgGAFqGBoUHAoeFBA/hhY6HBoUDgImCCQ/rBo6JD+IAHg",
    "Aoj+GP2AAeACiP4YAij+aP7AWPABkAEYAvj7aHBoEJgQcFj+MDAoCDBwQMg4WGACCAOA/tABMP7QkNBgATD+0AEw/tAABQEA/0AHAAZ4AAsADwATABcAGwAAAREjNSEVIxEhETMRASERISERIREBIREhASERIQcA",
    "qPtQqAKosP1QAgD+AAKwAgD7UAIA/gACsAIA/gAFEPowoKAF0AFo/pj9sAG4/kgBuPwAAbj+SAG4AAUBEP84BuAGMAALAA8AEwAXABsAAAERIzUhESMRIRUjERMhESEhESERASERIQEhESEG4KD+CKD+CKCgAfj+",
    "CAKYAfj7cAH4/ggCmAH4/ggGMProgP2gAmCABRj+AAFo/pgBaPyYAWj+mAFoAAUA0P9oB6AGeAAdACEAJQApAC0AAAERIREUFjMyNzI2NxcGBwYhIyImNREhFSMRIREzEQERIREjESERFREhETMRIREGkP1oUOCI",
    "kHAwELAoWGj+cGjgiP4YoAKIoAH4/gig/hgB6KAB+AVw++j/ADAoCFCYSPggKFhgAThoBIABCP74/kABKP7YASj+2Jj+2AEo/tgBKAAHAHj/SAeQBjAAAwAHAAsADwATABcAIwAAEyEVIQUhESETIREhIREhEQEh",
    "ESEhESERATMRIzUhFSMRMxEheAcY+OgBkAPg/CCYARD+8AGoAQj9UAEQ/vABqAEIATioqPrgqKgFIAYwmLD8IAI4ASD+4AEg/TABKP7YASgB2Pq4gIAFUPvIAAcAYP9IB5gGOAAPABMAFwAbAB8AJwArAAABIREh",
    "FgUHJAEhAgUnJDchEyE1ISEVITUBITUhIRUhNQEzEAIHJzY2JTMRIwE4BYj+4OgBEGD+wP7I/nDg/oh4ASDY/uCgAdD+MAJ4AdD7uAHQ/jACeAHQ/FiguOBw2JACiKCgBjj8qJhooJABEP74oJhgsAH4yMjI/djI",
    "yMj9wP7Q/tBYkFDg+P1Y//8A6P9IBygGeBImBbcAABAGBOQAAP//AJj/SAeoBoASJgffAAAQBgaZAAAAAgBA/0AHmAaQABQAGgAAARYXIRUhERADJxITBgcnNjcRISYnARYXByYnBJAwGALA+njokMgQcIBAsIgC",
    "wBgg/OhQIJAgUAaQUFiY/Yj9+P5wWAFwAThgULBYeALYQDD+0LC4KMio//8ASP9AB4AGiBImB94AABAGB28AAP//AEj/QAegBogSJgfeAAAQBgTjAAD//wBA/0AHoAaQEiYCwgAAEAYGhwAA//8AaP9wB7AGeBIm",
    "B90AABAGBOIAAAADARD/QAbwBoAADQARABUAAAEXBgchESM1IRUjESE2ASERIREhESEDaLgoOAMwoPtgoAH4SP5gBKD7YASg+2AGgCiAaPnQqKAGKID9GAHQ+6gB8P//AKj/SAdgBngSJggOAAAQBgYJAAD//wBo",
    "/3AHmAZ4EiYHYwAAEAYIwwAA//8AaP9wB5gGkBImCMQAABAGBOEAAP//AGj/cAeYBpgSJgjCAAAQBgTgAAD//wBo/3AHmAZ4EiYIwQAAEAYE3wAA//8AUP9wB6gGeBImCMIAABAGBN4AAP//AGj/cAeYBoASJge1",
    "AAAQBgjCAAD//wBo/3AHmAaAEiYHtAAAEAYIwgAAAAQBUP9IBpgGIAAHAAsADwATAAABESM1IRUjERMhESERIREhESERIQaYoPv4oKAECPv4BAj7+AQI+/gGIPkosLAG2P4gAUj84AFI/OABQAAFAJD/gAd4BngA",
    "EwAXABsAHwAjAAABMwchFSEHIREhFSE1IREhNyE1IQE1IRURITUhESE1IREhNSED0KgYAvD88CACMAEo+RgBGAHQIP0YAwgB+PyYA2j8mANo/JgDaPyYBniwmMD7qJiYBFjAmP2AkJD++Ij+aJD+WJj//wAw/0gH",
    "SAZ4EiYIlwAAEAYGMAAA//8AkP9gB6gGeBImCMwAABAGBi8AAAAFAGj/QAeIBnAAIAAmACoALgAyAAABFwQFFAchFSEGByERIzUhFSMRITY3IRUQAgcnNhIRESQDNjUEBRUBITUhESE1IREhNSEG+FD+6P64EAKw",
    "/UgIEAJIoPx4oAHYEAj9iFhoiFhQA6B4EP7I/qABKAOI/HgDiPx4A4j8eAZwkBgQUGiYcFD7oFBQBGBQcFD9sP4wuHCYAbgCOAHoGP7IWFgYCJD9gJD+SJD+SJAABwBo/0gHeAZ4AAMACQAPAB4AIgAmACoAAAEz",
    "ESMBFwIHJzYlFhcHJicXFwQFIREjNSEVIxEHJyQBITUhESE1IREhNSEDsKCg/miYwMiA4ASwwICgcMA4aP7g/oADKJj8CJjwUANY/oAD+PwIA/j8CAP4/AgGeP3wAdBY/vCgeLjQuOhI2MjQeLiI++hISAOAQKCw",
    "/nCI/miI/miAAAQAUP9IB3AGYAAlACkALQAxAAABFwQFByEVIQchFSEGByERIzUhFSMRBgcnJDchNSE3ITUhNwUnJAEhNSERITUhESE1IQbwQP6Q/lgwAwD8uDgECPuQKCgEQKD8YKCoyFABEMD+aAIYQP5oAegw",
    "/fA4AzD+aAOg/GADoPxgA6D8YAZggBgQeJhomEAo/AhAQANYmHCYoNiYaJhwGIgY+/h4/oB4/oB4AAcAeP84B4gGeAATABcAGwAfACMAKQAvAAABMwchFSEHIREhFSE1IREhNyE1IQE1IRUVITUhESE1IREhNSET",
    "FwYFJyQlBAUHJCUD2KAQAsD9KBACMAEY+PABMAH4EP0QAwgCEPxoA5j8aAOY/GgDmPxokIjw/rBgASgDCAEoAShY/tj+0AZ4kJB4/ECQkAPAeJD9+HBw8Hj+oHD+qHD+6HCAUIhAcDhomIA4//8AoP9IB5gGKBIm",
    "CM0AABAGBdUAAP//AKD/UAeoBkgSJgjNAAAQBggGAAAABABo/0gHcAaIADAANAA4ADwAAAEWFyE2NxcGByEVIQchFSEGByEVIQYHIREjNSEVIxEGByckNyE1ITchNSE3ITUhJicTITUhESE1IREhNSEC2Fg4AWBI",
    "KLAYUAHA/NAgAuD86BggA/D7wDAYA9CY/JiYkLhwAUi4/igCQED+GAIgKP1YAdgoOHgDaPyYA2j8mANo/JgGiGB4YHg4MHCQcIhAOJBAGPyAODgCwHBYcKjIkHiIcJBISPuQaP6waP64aP//AKD/SAeYBngSJgjN",
    "AAAQBgXYAAD//wCI/3gHkAZ4EiYHwgAAEAYIRAAA//8AiP9AB4AGcBImBWgAABAGBWYAAP//AIj/aAeYBoASJgfCAAAQBgXXAAD//wBg/1gHUAZ4EiYFwgAAEAYFogAA//8AWP9YB6AGeBImB9sAABAGBykAAP//",
    "AFj/WAegBngSJgfcAAAQBgZeAAD//wBQ/0AHeAYwEiYHhQAAEAYHFgAA//8AUP9IB6AGKBImB4UAABAGB+oAAP//AEj/QAeYBngSJgZsAAAQBgcXAAD//wA4/4gHkAY4EiYIZwAAEAYFwQAA//8AUP9IB1gGeBIm",
    "B4UAABAGBmAAAP//AEj/MAewBjASJgdqAAAQBgZrAAD//wBQ/0gHaAZ4EiYGWwAAEAYHhQAA//8AOP9IB7AGeBImCGcAABAGBiIAAP//AED/eAeIBngSJgeDAAAQBgV+AAD//wBI/0gHmAZAEiYGbAAAEAYGEQAA",
    "AAQAaP9IB5gGCAADABQAGgAgAAABIRUhAyEVIREUBiMiJycWMzI1ESEFABMHAgElFwIHJwABKAWw+lCQBtD88GCgaFggcHBg/OAFEAEg0IjQ/uj9CJDg8IgBGAYImP6YmPygcFgIoBBIA0jI/uD+wIABWAEgYFj+",
    "WPh4ASj//wBo/0gHkAaAEiYIbAAAEAYIswAA//8AaP9IB6gGgBImCLMAABAGCKMAAP//AEj/QAdgBogSJgYuAAAQBgV3AAD//wBY/1gHqAZ4EiYFoQAAECYHCwAAEAYHCgAAAAQAkP84B2gGkAAJABwAJABLAAAT",
    "ISYnNxYXIRUhBRcGBxYXByYnBAcnNjclNxYXNgUzESERMxEhBREUBiMiJycWMzI2NREhBgc2JSYnNxYXBycEBSc2NyERIxEhNxcHkAMQKECoWDADAPkoBLiAWIiQgGigsP7ouGCwuP7QWNDIqPxAmASQkPpIBiiQ",
    "iGCAKKhYQED9IGBg8AEAOECYqFiYMP6Q/mgwiHD+SKACqDCgGAXYSEAwWGCQGEhASDhAcFhAcDB4MEhgcEBISAj+eAGI/eiA/bBgYBCYECgoAZioYBAoSDgwmMAwYEgYiHCw/XgDGHAwQP//AEj/QAegBoASJggx",
    "AAAQBgb0AAD//wA4/0gHcAaAEiYI2wAAEAYHKwAA//8AOP9AB6AGgBImCNsAABAGBc8AAP//AFj/SAe4BngSJggcAAAQBggfAAD//wBY/zgHoAZoEiYIHgAAEAYF/QAA//8AOP9AB3AGgBImBbQAABAGCNsAAP//",
    "ADj/QAdoBoASJgjbAAAQBga7AAD//wBY/0gHkAZoEiYIHAAAEAYFVgAA//8ASP9IB8AGgBImBXYAABAGBVkAAP//AEj/SAeQBoASJgYPAAAQBgV2AAD//wCY/4gHeAaIEiYIZgAAEAYE3QAA//8AYP9IB1gGiBIm",
    "CEsAABAGCEoAAP//AHD/SAeoBpASJgb/AAAQBgTcAAD//wBo/0gHmAaIEiYHRAAAEAYHRQAA//8AgP9IB3AGiBImBwEAABAGBNsAAAADAGj/kAeYBoAACQATABkAABMhJic3FhchFSEFFwIDIRUhNSESARITBwID",
    "wAL4MECwSCgC4Pl4BQC4eMgCYPjQBBjY/ODAYLBguAUQqJA4qMiYOCj90P5AmJgCAAH4/nj+KEAB4AGI//8AgP+AB5AGeBImBXwAABAGBNoAAP//AGj/SAeYBngSJggKAAAQBgbSAAAABQB4/0gHiAaAABMAGQAp",
    "AC0AMQAAARYXIRUhBgchFSE1ISYnITUhJicDITY3IRYBIREhFSEVIRUjNSE1ITUhEyE1IREhNSEECDAgAsj+0DAwAej5EAHgMDj+4ALQICBgAcg4IP2IMP54BTD9wAM4/Mig/MgDOP2woAPw/BAD8PwQBoBIWIh4",
    "QJCQYFiIQDD+UGBYWP6g/YBwmNDQmHABeIj+gIj//wBo/0AHmAZ4EiYHcQAAEAYHcgAA//8AaP9IB5AGiBImBUgAABAGBNkAAP//AFD/SAeQBogSJgiPAAAQBgTYAAD//wBg/0gHkAaIEiYIygAAEAYE1wAA//8A",
    "aP9QB5AGiBImCMkAABAGBXUAAP//AGj/QAeoBogSJga/AAAQBgVIAAD//wBg/0gHmAaIEiYHswAAEAYGyAAA//8AaP+IB5gGiBImBUgAABAGBNYAAP//AGj/SAeQBogSJgVJAAAQBgTVAAD//wBo/0gHmAaIEiYI",
    "yQAAEAYE1AAA//8AcP9IB5AGiBImB8UAABAGBkYAAP//AGj/UAeYBogSJgjKAAAQBgTTAAD//wBo/0gHkAaIEiYHxQAAEAYGIAAA//8AUP84B5AGiBImCMkAABAGBVQAAAADAHD/SAd4BngAFQAbACEAABMhETMR",
    "IRUhAAUHAAERIxEAAScAEyEBFwYHJzYlFhcHJieIAyCgAzD9aAEAAZhg/kj+6KD++P5IeAGo6P2IBZiwiIComPvowHiYcMADwAK4/UiY/kjQuAEIAgD8WAOo/hD+4JgBEAGgAuhI+LBYyMDA2FjYwP//AFD/SAeY",
    "BogSJgbxAAAQBgayAAD//wBY/0AHmAZ4EiYG4QAAEAYGsQAA//8AWP9AB3AGeBImBq8AABAmB+QAABAGBhcAAP//AFj/QAeYBngSJgeHAAAQBgawAAAAAwBo/0gHSAZoADAANgA8AAABFwAFJCUmJzcWEwcmJwUR",
    "FAYjIicnFjMyNREEBSckJQYFJyQTBSckJRcEBQIHJDc2ARcGBSckARYXByYnBUiQ/kj+IAH4AZhQWJD4mJg4UP5AUHBwYCBocCj+0P64KAEoARD4/wAgARC4/jBYA/gBoHj+uP4wsPABGNCY/bBo8P7gUAEABDD4",
    "mJiQ+AU4OP5Q8Cg4WFhY6P7wWHBoQP4YgGAYoBhgAbggGICQwCgYkKgBABCQIDiIKCD/AKgYKHj86ID4mJh4AQDQ6Fjg0P//AGj/OAeYBngSJgg1AAAQBgZmAAD//wBw/zgHWAaAEiYGYgAAEAYGYwAA//8AcP84",
    "B4gGWBImBmEAABAmB4wAABAGBNIAAP//AFj/OAegBngSJgbjAAAQBgeMAAD//wBw/zgHWAZIEiYFeAAAEAYGZgAA//8AaP+IB5gGeBImB6IAABAGBv0AAP//AGj/SAdgBngSJgeiAAAQBggOAAD//wBo/0gHmAZ4",
    "EiYHbQAAEAYHAwAA//8AaP9gB6gGeBImByoAABAGB6IAAP//AGj/SAegBngSJgeiAAAQBgdiAAD//wBo/1AHoAZ4EiYHogAAEAYFoAAA//8AaP9IB6gGeBImB6IAABAGCA8AAP//AGj/QAeoBngSJgeiAAAQBge7",
    "AAD//wBo/1AHqAZ4EiYHbQAAEAYFXQAA//8AaP+QB6gGeBImB6IAABAGCB0AAP//AGj/SAeoBngSJgeiAAAQBggbAAD//wBo/3AHqAZ4EiYHogAAEAYGDAAA//8AaP9IB5gGeBImB6IAABAGBT4AAP//AGj/QAeo",
    "BngSJge6AAAQBgdtAAD//wBo/0AHmAZ4EiYHogAAEAYGhAAA//8AaP9IB6AGiBImCNUAABAGB6IAAP//AGj/aAewBoASJgeiAAAQBgaAAAD//wBo/0gHmAZ4EiYHogAAEAYF5gAA//8AaP+QB5gGeBImBlQAABAG",
    "B6IAAP//AGj/QAd4BngSJgdtAAAQBgV0AAD//wBo/0AHsAZ4EiYHbQAAEAYF/wAA//8AaP9IB7AGeBImB20AABAGCM4AAP//AGj/QAeoBngSJgeiAAAQBgjPAAD//wBo/0AHeAaAEiYHbQAAEAYFQwAA//8AaP9I",
    "B6gGeBImB20AABAGBh0AAP//AGj/SAd4BoASJgdtAAAQBgVzAAD//wBY/0gHoAaAEiYGggAAEAYGgwAAAAMAyP9IB0AGKAAQACMANwAAAREUBiMiJycWMzI1ESERIxEFFwIHFhcHJwIHJzYTJic3Fhc2JRcCAxYX",
    "ByYnBgcnNhMmJzcWFzYHQHhwUGgokEhQ+sigAligGEhoUJhgeMBg0GBwkIhgUCACeKAgaHBgeFBYgMhg0HiAmIBwaDgGKPnwYGgQoBBQBVD5uAbg+Bj+6PiouEjg/uDIgPgBKMioQHB4qMgY/sD+6MDQgLig+LCA",
    "2AEA2NBYoKDA//8AeP9IB4AGUBImB6cAABAGBjkAAP//AHj/eAeQBlASJgenAAAQBgTRAAD//wBo/0gHkAaAEiYHtQAAEAYHpQAA//8AWP9IB3gGcBImBkoAABAGBZ4AAAABAFD/YAeQBngAOAAAASE1MxUhFSEV",
    "MyQBFwYHIRUhBgUVJCUXBAUVFBYhIDY2NxcOAiEgJjURBgcnNjc1FzY3ITUhNSEBAAH4qAIA/gDwATgBAHDA2AHw/Ujo/rgB+AG4YP4g/dCIAWABIJhAGLAYYLj+cP44yLC4SODQaKiY/MgCiP4IBYD4+Jj44AEY",
    "eNiomKCouICoiLiAgCAgGGDAMOCYMFhQAbBYSJhYYFAYWGCY+AABAFD/UAeYBngAMAAAASMGByckJSE1ITUhNSE1MxUhFSEVMyQlFwYHIRUhBgUhFSEHIQIGIyInJxYzMjY3IQKgsLCwQAHYAYD8wAK4/fgCCKAC",
    "CP348AFAAQhowNgB0P1AgP74A9D8KDAD+Ci40KjIIOCocGgg+/gCYEhAiKDImMCYwMCYwMjwcLiQmFCAmLj+eNAwmDBoyAADAGD/QAeYBoAAJAAoACwAAAEhNTMVIRUhFTMkJRcGByEVIQUhESM1IRUjEQYHJyQl",
    "ITUhNSEBITUhESE1IQEYAjigAaD+YJgBUAEIaMDYAej9MP6AA2ig/HigoKBIAbgBaPzoAuj9yAFwA4j8eAOI/HgFqNjYkNjQ+Hi4mJDQ/GhgaAMIOECYkLiQ2PxwyP3oyAABAHD/SAeQBigAIgAAEyEVIQYHIREU",
    "BiMiJycWMzI1ESERIxEhESMRIREjESE2NyFwByD8sDA4A0BoaDhIIGgwOP7AmP7AoP7IoAI4QCj86AYomKCQ+7hgaBCYCFADiPvwBBD78AQQ+4AFGJCg//8ASP9AB6AGeBImBr4AABAGBt8AAAAEAGj/SAeYBjAA",
    "EQAVABkAHgAAEyEVIRElFwYHESMRBAUnJREhASERIREhESERJCU1IYgG6P7QAUAYqLCg/aD9SCABWP7IAdgDQPzAA0D8wAHIAXj8wAYwmPvgIJAYEP5oAYhAMKAYBID++AEI/VABEP0oICjo//8AYP9IB5AGMBIm",
    "BesAABAGBUwAAP//AFD/SAewBnASJgaTAAAQBgiyAAD//wBQ/zgHoAZIEiYHHwAAEAYE0AAA//8AUP9IB6gGSBImB3wAABAGB88AAP//AJD/SAd4BngSJgVyAAAQBgTPAAD//wBY/0gHmAZ4EiYIFgAAEAYHewAA",
    "//8AUP9AB6AGgBImB8kAABAGCBUAAP//AIj/SAeoBoASJggqAAAQJggpAAAQJggoAAAQBggnAAD//wBQ/0gHkAaAEiYIFQAAECYG7QAAEAYG7AAA//8AaP9AB3gGeBImB84AABAmCA0AABAGBM4AAP//AFD/SAeo",
    "BngSJggVAAAQBgXAAAD//wBQ/zgHkAZIEiYGpQAAEAYIFQAA//8AQP9AB7AGSBImB4QAABAmBoYAABAGBvoAAP//AFj/SAeQBoASJgZwAAAQBgVtAAAABAEg/0gG2AaAAA0AEQAVABkAAAEXBgchESM1IRUjESE2",
    "ASERIREhESERIREhA2C4GEADGKD7iKAB6ED+eAR4+4gEePuIBHj7iAaAKFhw+bigoAZIcP3gARj9OAEY/TgBGAABAJD/gAd4BhgAIwAAEyEVIQIHJCUnNxYTBycFESEVIREhFSE1IREhNSERBAUnJBMh0AZo/ICo",
    "wAGoAci4kNjYmID+IAKo/VgDKPkYAxj9WAKo/uD+yDABCMj94AYYmP7YmBAwyGDQ/uB4sDD+0Jj+oJiYAWCYASgYCJigATD//wBg/0AHqAZ4EiYIFwAAEAYGiAAAAAIAgP9IB4AGSAAaAB4AAAEXBAURIRUhESER",
    "IzUhFSMRIREhNSERBAUnIAEhESEGyFD+wP54AzD80AJ4oPvYoAJQ/NADMP7A/pgwAvj+MAQo+9gGSIg4GP7QmP7Q/NBoaAMwATCYASAYCJj6cAGYAAQAaP9wB5gGgAAeACQAKAAsAAABFwchFQYHIREhERQWISA3",
    "NjcXBgcGISAmNREGBycAByE2NyEGAyERIQEhESECoKBQAqhIUAHg+wiQAagCUFAgIJgoWED9SP3owEhIUAGQOAKIYDD9sHgoAeD+IAJ4Aej+GAaAMICAiGj9WP6gMCAoEOhY8EAwSHAD0DgwkAEg4HBwkP2YAYj+",
    "eAGI//8AeP9AB4gGgBImB3kAABAGBvgAAP//AHj/QAeYBngSJgilAAAQBgTNAAD//wBo/0gHoAZ4EiYHrAAAEAYEzAAA//8AeP9IB4gGgBImB3kAABAGBMsAAP//AID/UAeoBngSJgilAAAQJgeBAAAQBgceAAAA",
    "BQBo/0gHkAZ4ABMAHwA1ADsAQQAAEyE1MxUhNTMVIRUhFSM1IRUjNSEFFwcEBQckAQAFJyQBITUzFSEVIREUBiMiJycWMzI2NREhFxcCByckJRYXByYnkAGYqAJgqAGY/mio/aCo/mgDcKgwAYgBkGD+WP54/oD+",
    "QFgCgP5QAnioAnD9kFiAUFAgWFAoIP2I6JjI8IgBCAQ4yMiQqNgF2KCgoKCYuLjAwEg4MPB4oJABGP7omJDo/oDw8Jj+OHBgGJgYKDgBoEhQ/uiQcLDQqOB42ND//wBo/0gHkAZ4EiYIkAAAEAYEygAA//8AgP84",
    "B4gGeBImCKUAABAmBzgAABAGBMkAAP//AHj/QAeIBngSJgiQAAAQBgTIAAD//wB4/0AHiAZ4EiYIkAAAEAYExwAA//8AaP84B7AGeBImCJAAABAmBp0AABAGBMYAAP//AGj/QAeoBngSJgimAAAQJghaAAAQBghb",
    "AAD//wCA/0gHiAZ4EiYIpgAAEAYExQAA//8AaP9wB5gGeBImCKUAABAmCMIAABAGBMQAAP//AGj/OAegBngSJgimAAAQBgTDAAD//wB4/0AHkAaIEiYGegAAEAYGewAA//8AeP9AB4AGiBImBnwAABAGBMIAAP//",
    "AID/OAeYBjgSJghAAAAQBghBAAD//wCA/0gHiAaIEiYIywAAEAYGEgAA//8AUP8wB5AGgBImBlYAABAGBMEAAAAEAFj/sAeoBngADQARABUAGQAAARcGByERMxUhNTMRITYBIREhASERIQEhESEDgKA4QAM4yPiw",
    "wAHoUP5oASD+4AG4ARj+6AGwASD+4AZ4KKhg+wCYmAUAgPqABGj7mARo+5gEaP//AFD/QAeABoASJgbCAAAQBgbBAAD//wBg/0AHmAZ4EiYI0QAAEAYH9QAA//8AWP9IB5AGeBImCIMAABAmBV8AABAGBMAAAP//",
    "AEj/QAdYBngSJgdfAAAQBgddAAAAAQBQ/1gHuAZ4ADQAAAEGByckNyE1ITUhNSE1ITUhNTMVIRUhFSEVIRUhFSEWFzY3FwYHFgUHAAMjBgcRNjcXBgUnAijQoGgBoPD9kANA/VACsP0IAvigAvj9CAKw/VADQP0Y",
    "QFjguHDQ0LgBWFj9WKhoaHDwuCDo/shQAXCIQJCg8JiomKCYoKCYoJiomLBwWJiAkFi4gJgBCAJgeGD+IDhImFhIUP//AGD/WAe4BoASJggAAAAQBgS/AAD//wBI/0AHoAaAEiYIhQAAEAYHXgAA//8ASP9AB5gG",
    "eBImB9oAABAGBxcAAP//AGj/UAeoBngSJgc+AAAQBgS+AAD//wBQ/0gHkAZ4EiYGwwAAECYGdQAAEAYGdgAA//8AQP9AB6AGeBImBo8AABAGBWQAAP//AEj/QAeQBnASJgiFAAAQBgWfAAD//wBI/0AHuAZwEiYI",
    "hQAAEAYFOQAAAAQAeP9IB4gGOAAPABMAJgAuAAABESM1IRUjESERITUhFSERAyERIQEhEQYjIicmNREhFRAFJyQ1NSEhERQWMzI3EQcYoPsQoAHw/aAHEP2ooP7oARj8+ATwQEDwOED+6P6YYAEo/rADqECIQEAE",
    "UPr4mJgFCAFQmJj+sAFQ/rD8KAE4CCAwcAFQEP6o0Jig8BD+2DAYCAFo//8AWP9AB5AGQBImBo4AABAGBL0AAP//AGj/QAeoBlgSJgasAAAQBgarAAAAAwCY/0gHkAYgAAcAEgAjAAABESMRIREjEQEzEAcQAAUn",
    "JAASFzMRFBYzIDY3FwYHBiEiJjUGYKD8aKAB8KAI/oj+aGgBOAE4cLigSIABAFAQmCBQOP6w+HAGIPtABCj74AS4/vD+MBD+mP4QkIhoASABWDD9uCggUKAo6EAwSGD//wBo/0AHoAYwEiYIBQAAEAYGUAAA//8A",
    "aP9AB6AGeBImBlAAABAGBbYAAP//AEj/MAeoBogSJgXDAAAQBgV3AAD//wCA/0gHoAaIEiYFtQAAECYGYQAAEAYEvAAA//8AaP9IB5AGiBImBWMAABAGBLsAAAAGAED/QAcgBqAAIwApAC0AMQA3ADsAAAEXBgch",
    "FQYHIREUBiMiJycWMzI1NSERIxEhAgcnNhERBgcnJBUhNjchBgMhNSEhFSE1ASE1IRUUJRUhNQKgsCgwArhQWAIYUFB4yCjoWCj9+KD+CDDgcPhQWHABkAJYaDj9wEBIAdj+KAJ4Agj7eAHg/igCeAIIBqAoSECA",
    "aFD7aHBoGLgYOOj+MAHQ/vDQkOACCAGoODCA4KBYWFD+GPDw8P2Q8EhAiPDw//8AYP9AB5gGgBImBtgAABAGBLoAAP//AGD/OAeIBoASJgbYAAAQBgYVAAAABQBo/0gHoAaAAAkADQARABkAHQAAEyEmJzcWFyEV",
    "IRchFSEVIRUhBREjNSEVIxETIREhaANQGDCgOCADOPjIwAWw+lAFsPpQBZCg+7igoARI+7gFkGhYMGiIkKCYoJiY/VBoaAKw/lABGP//AGj/OAeYBngSJgejAAAQBghgAAD//wBo/zgHqAZ4EiYHowAAEAYHawAA",
    "//8AaP+oB5AGeBImB6MAABAGBwwAAP//AGj/QAdYBoASJgekAAAQBgXEAAD//wBo/0AHqAZ4EiYHowAAEAYFbAAA//8AaP9wB7gGeBImB6MAABAGBzoAAP//AGj/QAeYBngSJgbrAAAQBgejAAD//wBo/2AHqAZ4",
    "EiYHowAAEAYHNAAA//8AaP9IB4AGeBImB6MAABAGBZIAAP//AGj/QAeQBngSJgejAAAQBgVHAAD//wBo/5AHoAZ4EiYHUgAAEAYIUQAA//8AaP9AB7AGgBImB6MAABAGCDkAAP//AGj/SAdQBngSJgejAAAQBgXL",
    "AAD//wBo/0gHgAZ4EiYHowAAEAYFnQAA//8AaP9IB6gGeBImB6QAABAGCFgAAP//AGj/SAeYBngSJgejAAAQBgacAAD//wBo/0gHmAaAEiYHowAAEAYImwAA//8AaP9IB5gGeBImB6MAABAGBwIAAP//AGj/SAeY",
    "BngSJgekAAAQBgeCAAD//wBo/0AHqAaIEiYHowAAEAYGVwAA//8AaP9AB7AGeBImB1IAABAGBf8AAP//AGj/SAegBoASJgejAAAQBgeNAAD//wBo/0gHWAZ4EiYHowAAEAYIOgAAAAQAcP9IB6AGoABAAEYASwBQ",
    "AAABFwYHIRUGByERIRYXJDcXBgcSBQckAwYHFhUUBiMiJycWMzI2NTUEBSckJSYnBAUnJCUmJwYFJyQ3IREGByc2NgMhNjchBgMhNjchIQYHITUCeKAgKAKwQEgB+P0AkDABAMhwgIhYAWho/pBwSEgIgIhYkCiY",
    "eDAw/oj+EEgCGAGIEBj+uP4wSAHQAVAoMPj+eEgBUOj+aDAwYMjgSAJYUDj9uEBYAZg4OP34ArggOAIgBqAgQDh4WED+SIi4YJh4WED+yLCI0AFgIBhASNDQGKAgiIAg8HiIgPhIONhwiGDQMDCwSJAwiAFAIBhw",
    "eND++EBQSP6IMHhgSKj//wBw/0gHkAaAEiYIAAAAEAYEuQAAAAMAkP84B2AGeAAXACIAKAAAAREjESERIxEhNjchBgUnJBMXBgchFQYHATMQBxAFJyQANTYBBAUHJCUGqKD8OKACiGhI/eCw/vhwAYi4qCAwAnhY",
    "WP7IoAj8uGgBwAFQCAE4ATgBOID+8P6YBFD8cAL4/QgDkICIuIh4yAEgKDg4gKBw/uD+yBD+ELiAYAEg4Aj+sHigiKig//8AaP8wB5gGiBImBvwAABAGBuUAAP//AGD/QAeoBngSJggXAAAQBgchAAD//wBw/0AH",
    "qAZoEiYHGAAAEAYG5gAA//8AaP84B4gGaBImBnkAABAGBLgAAAAIAHD/OAeQBkAACwAPABMAFwAbACMAKwAxAAATIRMhAyEVIQMhEyElNyEHJQchNwE3IQchITchAREjESERIxEFFwIABSckAAUEBQckJXABQCgE",
    "yCgBGP7YIPsgMP7YBWgY/pAg/ggYAYAgAcAQ/ogY/fABgBj+gARQmPwYmAJQqDj+mP5oQAFwATgBQAEQATBQ/sD+4AUgASD+4JD+4AEgkJiYmJiY/kCYmJj+UP2wAcD+MAJg2Bj+4P64SKA4AQBQSLCYyFD//wBg",
    "/0gHmAZ4EiYG6QAAEAYHIQAAAAkAgP9IB3gGeAAiACYAKgAvADQAOQBCAEgATgAAEyE1MxUhNTMVIREhFSECBiMjESMRIREjEQYHJyQ3IRMhNSEhFSE1MxUhNQE1IRQHIzY1IQcTITUhBiUVIScWMzI2NwEzAgUn",
    "JCUEBQckJdgB8KABCKAByP44AmgQWFhIqPyYqGB4YAFAiP6oQAGY/hACkAEIoAEw/jD++BCwIP7oELACIP6gSAJIASAQSDgYGAj84KgQ/KhYAwgBAAFwAUBA/qD+qAXgmJiYmP5wgP74iP5YAXD+iAGYOCiIcIgB",
    "kICAgICA/niAQEBAQID+uMBgYMBQCCBY/nj9wDiQILBQeJiQSP//AGD/MAeQBngSJgaNAAAQBgbkAAD//wBg/0AHqAaAEiYHIgAAEAYFZQAA//8AYP9IB5AGgBImBugAABAGBucAAP//AEj/SAeQBngSJgY2AAAQ",
    "BgXjAAAAAQBo/0AHoAZ4ACgAAAEhNTMVIRUhFSEVIREhFSERFiEhByMgJCcGBycAExcGBxYXESE1ITUhARgCkKACoP1gAwj8+AKw/VDgAWABGDjg/gD98KBgmHgBKDigGDig8P0IAvj9cAWI8PCg8Jj+6Jj+iCio",
    "uKjYsHgBWAHYIMCouEgDAJjw//8ASP84B6AGeBImB9cAABAGB9kAAP//AEj/OAegBngSJgfYAAAQBgS3AAD//wBI/zgHqAaAEiYH2AAAEAYEtgAAAAIAcP9AB6AGMAAcACAAAAEhESERIRUhERYhIQcjICQnBgcn",
    "ABMXBgcWBREhNyERIQGABSD92AKo/VjYATgBGDjg/gj9+JhomIABQDCgGDigAQj9qKAD4PwgBjD9QP7YmP6AILDAsOCweAFwAdAgwKDQUAMYmAGQ//8AUP9IB6gGWBImCAsAABAGCAQAAP//AFD/aAegBoASJggC",
    "AAAQBge2AAD//wBQ/2gHoAYwEiYIBAAAEAYHKQAA//8AUP9QB6gGSBImB9YAABAGCAYAAP//AFD/SAeoBoASJggCAAAQBgiEAAD//wBQ/0gHqAaAEiYIBAAAEAYIAwAA//8AUP9IB7gGYBImCAIAABAGBqIAAP//",
    "AFD/SAeYBnASJggCAAAQBgWPAAAABABg/0gHoAaIACIAJgAqAC4AAAEXBgchETY3FwYHERQGIyInJxYzMjY1EQAFJyQBITUzESE2AyE1IREhNSERITUhAyCwKDAC+GhYcJCgkIiQyCj4gEBA/gj80EgCoAH4+6jA",
    "AWA4+APQ/DAD0PwwA9D8MAaIMEg4/MhISHh4aP4wYGAomCgoKAFI/tj4mMABCJADkFj+eKD+MKj+KKj//wBI/0gHqAaAEiYG0AAAEAYGigAA//8ASP9AB3AGgBImBkIAABAGBkMAAP//AGj/SAeoBngSJgepAAAQ",
    "BgdZAAD//wBo/0gHoAaAEiYHqQAAEAYFowAA//8AaP9IB6AGeBImB6kAABAGBzMAAP//AGj/SAeoBngSJgepAAAQBgZZAAD//wBw/zgHqAZ4EiYHPgAAEAYEtQAA//8AaP8gB7AGeBImB6oAABAGB6kAAP//AGj/",
    "SAewBoASJgfMAAAQBgfNAAD//wBY/0gHgAaAEiYHZwAAECYHZgAAEAYHZQAAAAIAYP9YB6AGSAAFABcAABMWFwcmJwMhERYEISEHISAkJwcnNjcRI/CggHCImBgBkGABKAHwAjBQ/YD+oP7AeOhwgHjwBkhokIig",
    "aP3g/QBIQLBgaOioSFACgP//AGD/WAegBngSJgb5AAAQBgPDAAD//wBg/1gHsAZIEiYDwwAAEAYEtAAA//8AYP9YB6AGcBImA8MAABAGBLMAAP//AGD/WAegBkgSJgPDAAAQBgSyAAD//wBg/1gHoAZoEiYHJgAA",
    "EAYDwwAA//8AYP9YB6AGeBImBlIAABAGA8MAAP//AGD/WAegBkgSJgPDAAAQBgSxAAD//wBg/1gHoAaAEiYDwwAAEAYEsAAA//8AYP9YB6AGcBImA8MAABAGBK8AAP//AGD/WAegBkgSJgYzAAAQBgPDAAD//wBg",
    "/1gHoAaAEiYDwwAAEAYErgAA//8AYP9YB6AGSBImA8MAABAGBK0AAP//AGD/WAegBngSJgfLAAAQBgPDAAAABQBg/1gHoAaAAA0AEQAVABsALQAAARcGByERIRUhESERITYDFSE1ASE1IQEWFwcmJwMhERYEISEH",
    "ISAkJwcnNjcRIwSAqBggAdD84ANI/BgBSCDIAoD9gAKw/VD9UKCAaJCYGAGQYAEoAfACMFD9gP6g/sB46HCAePAGgChoWP4AsP34BLh4/vjY2Pxw4APoaIiImHD94P0ASECoWGjoqEhQAoD//wBg/1gHoAZIEiYG",
    "hQAAEAYDwwAA//8AYP9YB6AGiBImA8MAABAGBpIAAP//AGD/WAegBmASJgabAAAQBgPDAAD//wBg/1gHoAZ4EiYGcgAAEAYDwwAA//8AYP9YB6AGYBImA8MAABAGBKwAAP//AGD/WAegBkgSJgPDAAAQBgSrAAD/",
    "/wBg/1gHoAaAEiYDwwAAEAYEqgAA//8AYP9YB6AGSBImA8MAABAGBKkAAP//AGD/WAegBoASJgY0AAAQBgPDAAD//wBg/1gHoAZ4EiYDwwAAEAYEqAAA//8AYP9YB6AGSBImA8MAABAGBKcAAP//AGD/WAegBoAS",
    "JgYfAAAQBgPDAAD//wBg/1gHoAZ4EiYDwwAAEAYGLQAA//8AYP9YB6AGgBImA8MAABAGBKYAAP//AGD/WAegBngSJgXKAAAQBgPDAAD//wBo/0gHiAYYEiYILwAAEAYGpgAA//8AeP9IB4gGgBImBqYAABAGBfQA",
    "AP//ACj/SAeIBngSJgamAAAQBgXzAAD//wBo/0gHuAZAEiYHiwAAEAYHOwAA//8AaP9IB5gGSBImB4sAABAGB6EAAP//AED/SAeQBnASJgZcAAAQBgWcAAAABQCI/5gHgAY4ABMAFwAbAB8AIwAAASERIRUhFSEV",
    "IRUhNSE1ITUhNSETIREhIREhEQEhNSEhFSE1ATAFsP14Aqj9WAMo+QgDMP1IArj9eKAB6P4YAogB6PuQAej+GAKIAegGOPxA0JjgmJjgmNACIAEI/vgBCP1w+Pj4AAUAcP+AB4gGWAAlACkALQAxADUAAAEXBAUV",
    "IRUhFSERIRUhFSEVIRUhNSE1ITUhNSERITUhNSE1BScgASE1ISEVITUBITUhIRUhNQa4UP7A/oADQPzAApD9cALw/RADOPjwAzj9GALo/WgCmPzYAyj9YDAC8P3gAgD+AAKgAgD7YAIA/gACoAIABliIGAiAkHD9",
    "WHCQcJiYcJBwAqhwkHgQkPz4gICA/niAgIAACQBg/3AHmAZQAAMABwALAA8AIwAnACsALwAzAAABIREhEyE1IREhNSEBIRUhFyERIRUhFSEVIRUhNSE1ITUhNSETITUhIRUhNQEhNSEhFSE1AVgFQPrAoAQA/AAE",
    "APwA/pAG6PkYyAVY/agCoP1gA0j4yANI/WgCmP2ooAG4/kgCYAG4++gBuP5IAmABuAZQ/egBSFj+4Fj+2HhQ/fBQeFCIiFB4UAE4WFhY/vBQUFAAAgBo/3gHoAaAAAsAKwAAARcHAAUHJAEABScAAyEVIREhFSER",
    "MzY3FwYHIRUhNSEmJzcWFzMRITUhESED+KAwAXgBwGD+YP5g/pj+IFACeKgDwP5gAqj9WKhwWKhgaAGw+VABoEhgmHBQuP1IArj+iAaAMDD+2JigoAFY/rDQmAEY/vCg/vCY/iCwyDDAiJiYoIBIqMAB4JgBEP//",
    "AFD/SAeYBngSJgd4AAAQBggJAAD//wBQ/0gHcAZ4EiYHmwAAEAYHKwAA//8AUP9wB5gGeBImB5sAABAGBToAAP//AFD/SAeQBngSJgebAAAQBgXQAAD//wBQ/1AHqAZ4EiYHmwAAEAYIBgAA//8AUP9QB5gGkBIm",
    "B5wAABAGBT0AAP//AFD/SAdQBoASJgheAAAQBgedAAD//wBQ/zgHoAZ4EiYHUQAAEAYHmwAA//8AUP9IB6AGeBImCLYAABAGB50AAP//AEj/SAeYBngSJgh4AAAQBgX5AAD//wBQ/0gHmAZ4EiYHfwAAEAYFUQAA",
    "//8AUP9AB7AGiBImB5wAABAGBYYAAAACAHD/UAdgBnAAFgAcAAATIREzESEVIRIFBwADIRE2NxcGBycRIQEXAAUnJHABoKAEsP0YyAIgYP2Y0P7osIAgsPhI/mAFeID+6P5oWAFoA5gC2P0omP4I0KgBAAJw/SBg",
    "aJiIeFADYANoaP6oyJCwAAMA0P9ABzAGkAAFABQAGAAAARYXByYnBSERFAYjIicnFjMyNREhBTMRIwIAcEiQQHAB4APYYFhAWChgQDj8yP14oKAGkICYWJiACPnwcHAIqBBwBVCQ+jj//wDQ/0AHMAaQEiYD+AAA",
    "EAYHbAAA//8A0P9ABzAGkBImBwUAABAGA/gAAP//AND/QAcwBpASJgP4AAAQBgSlAAD//wDQ/0AHMAaQEiYD+AAAEAYEpAAA//8A0P9ABzAGkBImA/gAABAGBKMAAP//AND/QAcwBpASJgeSAAAQBgP4AAD//wCo",
    "/zgHqAZ4EiYH1AAAEAYHawAA//8AqP9AB5AGeBImB9QAABAGBUcAAP//AKj/QAdYBkgSJgfUAAAQBgYEAAD//wCg/0AHgAZ4EiYGUQAAEAYIXAAA//8AqP9AB7AGeBImB9QAABAGBmQAAP//AKD/SAeYBoASJghc",
    "AAAQJga0AAAQBgfDAAD//wCg/0AHoAYwEiYIXAAAEAYFvwAA//8AoP9IB5gGgBImCFwAABAGBoEAAP//AKj/QAeoBkgSJggGAAAQBgfUAAD//wCI/0AHqAaAEiYHTAAAEAYHfgAA//8AoP9IB6gGeBImBcAAABAG",
    "CFwAAP//AIj/QAeQBnASJgdMAAAQJgerAAAQBgSiAAD//wCg/0gHwAZ4EiYFWQAAEAYIXAAA//8AoP9IB4AGMBImCFwAABAGBhYAAP//AFj/SAeoBoASJgZEAAAQBgdXAAD//wBg/0AHoAaAEiYIYQAAEAYIjgAA",
    "//8AeP8wB4gGYBImCNMAABAGBKEAAP//AIj/QAd4BlgSJgjUAAAQBghiAAD//wBg/0gHmAZgEiYI0wAAEAYEoAAA//8AYP9IB5AGcBImBk8AABAGBJ8AAP//AGj/SAeABnASJgZOAAAQJgZMAAAQBgZNAAAABABo",
    "/0AHmAZ4ABcAKAAsADAAABMhNTMVIRUhFSEVIRUhFSE1ITUhNSE1IQERFAYjIicnFjMyNTUhESMREyE1IREhNSHIAuCgAvD9EAKw/VADUPjQA0D9YAKg/SAGAIB4aIgouFhg+8igoAQ4+8gEOPvIBgB4eIiIgICQ",
    "kICAiP1w/RhgYBCYEFBI/tADqP8AeP6IiP//AGD/SAeYBogSJgZ/AAAQBga4AAAAAgBo/0gHkAZ4AA8AHwAAATMRIxEhNSERITUhESE1IQEzESEVIREhFSERIRUhESMC0KCg/ZgCaP34Agj9+AIIAaigAjj9yAHw",
    "/hACeP2IoAZ4+NgBgJgBWJgBUJgBOP7ImP6wmP6omP54//8AaP9IB5AGgBImBVUAABAGBJ4AAAAGAGj/UAeQBigADwATABcAGwAfACMAABMhFSEHIREjNSEVIxEhNyEBIREhASERIQUhNSERITUhESE1IWgHKPyI",
    "WANQoPsQoAJAWPzwARgBKP7YA8gBKP7Y/fgBcP6QAXD+kAFw/pAGKJjw+rBoaAVQ8Pq4A8D8QAPA2Nj9uNj9sOgABQBo/0gHmAaIAAkAGQAhACUAKQAAARYXIRUhNSEmJwMWFyE2NxcGByEVITUhJicBESM1IRUj",
    "ERMhNSERITUhBAA4IALQ+bACyCAowFgoAbhgKLgoYAIQ+NACADBABIig/CigoAPY/CgD2PwoBohIWJiYODj+2HiYqGg4WICYmHho/fj8UGBgA7D+oMj94MgAAwCA/0AHcAY4AA8AGgAgAAABITUhFSEHIREjESER",
    "IxEhEzMQBxAFJyQAETYBBAUHJCUDqP0YBoj9EEgCiKD8GKAB8EigEPywaAHAAWAIASgBcAEwaP7A/pgFoJiYyPwgA0D8wAPg/tD+oBD92NCAaAFIAQAI/piIwIjQkP//AGj/SAeYBjgSJgd3AAAQBgdwAAD//wBo",
    "/0gHmAY4EiYHVAAAEAYHBAAA//8AWP9IB5gGeBImB5cAABAGBq4AAP//AFD/QAeYBkgSJgdUAAAQBgW8AAD//wBg/0gHmAY4EiYHlwAAEAYFVwAA//8AaP9IB5gGaBImB5kAABAGCLUAAP//AHD/SAewBjgSJgd1",
    "AAAQBgd2AAD//wBQ/0gHmAZQEiYHlwAAEAYHmAAA//8AUP84B7AGUBImB0oAABAGB5YAAP//AGD/QAeYBngSJgdzAAAQBgeVAAD//wBY/0gHmAZ4EiYHdAAAEAYHlQAAAAIAYP9gB8gGMAAWACoAAAEQExIzMhMX",
    "AgYjIicCESEREAEnEhERARcCBxYTByYnBgcnNjcmJzcWFzYGaDgoODAIkBhgUJBAaPwg/wCI6AOIiGiQsJCgeIig0IjwqKjIkKiQiAYw/Ij+YP7wARgg/viYyAFoBAj9IP5A/mhoAVABoAN4/qBI/vjo6P74SODQ",
    "2LhY2PDgyECouND//wBY/zgHuAZIEiYFuwAAEAYFugAAAAEAkP9gB6gF+AAZAAATIRAXNjcXBgcWFwcmJxIzMhMXAiMiAwIDIZAE6AjAqHDQ6ODYgJCwQKBYQJhY2LhggBj7yAX4/wDYkMCYyJCQuIiQiP1IASAo",
    "/lgBCAFoA5AABQBo/zgHqAaQAAsAGwAfACMAMAAAARcHBAUHJAEABSckBREhESUXBAUnESEmJzcWFwUVITUBFSE1AQQFNjcXBgcWFwcAJQP4gCABiAHIWP5A/lj+oP4QMAIoA+j7uAGwMP7Y/vhQAkAoMJhIKP2w",
    "A6j8WAOo/agBCAEAoGCIaHiwqFj+AP3wBpBYIOh4mIgBEP7gmJiw+P0g/nBwkFA4YAS4UEAwWGiYkJD+4JCQ/rBAYGBwWGhQSFiQAQiI//8ASP9QB5AGgBImB8AAABAGByUAAP//AEj/QAdwBogSJge3AAAQBgW5",
    "AAD//wBI/zAHkAaAEiYGJQAAEAYFuQAA//8AUP9IB4gGgBImB7kAABAGBg0AAAAFAGj/SAeYBoAABQAdACEAJQApAAABFhcHJiclFwYHIRUhBgchESM1IRUjESE2NyE1ITYBITUhESE1IREhNSECwEggoChAAyi4",
    "QGACOPyQGCACsKD8CKAB2Bgg/PAEQGj8+AP4/AgD+PwIA/j8CAaAaIA4gHAwOJBomFhY+0BwcATAMICYkPzgsP4QuP4QsAADAGj/SAeYBmgAIwAnACsAAAEXBAUVIRUhBAUHJAERIREjNSEVIxEhEQAFJyQlITUh",
    "NQUnIAEhNSERITUhBoBQ/tj+mAMo/YgBGAGQYP5Q/rgCUKD8EKACQP7o/khoAagBEP1wAxD9wDACqP4oA/D8EAPw/BAGaIgoELCQwHiosAEo/kj8oGBgA2ABiP74mICA2JCgEJj7SLD+GLAAAgDY/1gHUAZIABUA",
    "GQAAASEDIQICIyInJxYzMjYTIRMXAyETIQMhFSEBWATwWAFgIJCwWIAgoFhISBD7aECoMAKgQPvIgATQ+zAGSPzA/Wj+6AioCMgBqALQEP3YAqj7uJj//wCA/1AHkAY4EiYHFAAAEAYHEgAA//8AaP9QB6AGeBIm",
    "BxUAABAGBuAAAP//AID/SAeQBjgSJgcUAAAQBgWcAAD//wCA/1AHkAZgEiYHEwAAEAYFuAAAAAYAgP9AB3gGUAALABEAFQAmACoALgAAAREhESM1IRUjESERASERIRUhASE1IQERFAYjIicnFjMyNTUhESMREyE1",
    "IREhNSEGeAEAoPpIoAEIAugBaPxQAkj9uAGw/lAESGhoaIggsFg4/GigoAOY/GgDmPxoBlD96P6g0NgBaAIY/egBiHD+6JD+aPzIYFgQkBBIgP6oA/D+8ID+gIAABgBw/0AHkAaIAAgADAAQACEAJQApAAABFhch",
    "FSE1IScBIREhNyE1IQERFAYjIicnFjMyNREhESMRASERITchNSEEEDggAyj44AM4QP4gBOD7IKADoPxgBSB4gFh4IJhQYPqooAGIA4D8gJgCUP2wBohIUIiIaP6Y/mCIkP54/RhgWBCQEEgCQPzoA6D/AP5QiKgA",
    "BwBg/4gHkAaQAA0AEwAXABsAHwAjACcAAAEHJwATFwYHIRUHIREhAQYHITY3ASE1ISEVITUBITUhIRUhNQEhFSEBSJhQAaC4oCgwArhwAXj6iAE4gEgCyFAw/OAB0P4wAnAB0PvAAdD+MAJwAdD6UAcg+OAEKGCQ",
    "ARABKDBIQIjI/GgEWIg4YGD9uPDw8P2Y8PDw/aiY//8AUP9IB5AGgBImB8oAABAGBkcAAP//AFj/QAdwBogSJgdXAAAQBgdYAAAACQBg/0AHkAZAABMAFwAdACEAJwAtADMAOQA/AAABIREhFSEVIRUhFSE1ITUh",
    "NSE1ITchESEFFhcHJiclESERBxcGByc2ARcGByc2JRYXByYnJRYXByYnJRYXByYnATAFmP2AApD9cAMo+SADIP1wApD9gKAB4P4gAQBIKJAoUAIQAeD4kEBQiFj8UJB4gIiYBah4eIBokP0AUDioMEgCcGBAoEBY",
    "BkD9KKCQqJCQqJCgiAHISHiQMJhweP44AchAOKBwSID78FjQgHiQoICgiKigUJCwSLiISJCoSLCI//8AYP9AB6AGgBImCAwAABAGB9EAAAAIAOj/UAe4BoAAFQAjACwANQA7AEEARwBNAAABFwQFFSEVIRUhNSE1",
    "ITUhNSERIREkATMSEjMyNjcXAiMiJyYBMxE2NxcGBScBMxE2NxcGBScBFhcHJiclFhcHJicFFhcHJiclFhcHJicDYHD++P7AAgD+AASY/hgB6P4AAqD6KAFwA4CgCGAgGBAIiBigaFBo+xigyKAYyP7wSAKAoMig",
    "GMj+8Ej+sJh4WIiYAuiYeFiIkP3YoIhgkJgC4KiAYIigBoB4QCCIiKioiJiI/SgCsCj84P44/rCAiCD+aLjwAhj86DhIkFhISAOA/Og4SJBYSEgDeEBYeGhAaEBYeGhA2EhgeHBIaEhgeHBI//8AUP9AB7AGgBIm",
    "BtQAABAGBJ0AAAADAGD/SAdwBngADwAVADMAABMhNjcXBgchFSECAScAEyEBFhcHJicBFwIFFRQWMzI3NjcXAgcGISAmNTUGByckNxEzETaIAoAgCKAQGAO4/DCQ/choAfiY/ZgE0JBYkFCQAVCgwP7QSKDAICgI",
    "qBBIQP7g/wCIwOhIASDQoLgE6LjYENCwmPzw/giQAbACyAIQeIBQgHD9iDD+iPC4GCAoMPAw/tBAQFBQeHhgiHiYAqD96KgAAgOA/+AEgAW4AAMADwAAASMDMxMUBiMiJjU0NjMyFgRAeDjgEEBAQEBAQEBAAaAE",
    "GPq4SEhISEhAQAACAugDqAUYBbgAAwAHAAABAyMDIQMjAwOwKHgoAjAoeCgFuP3wAhD98AIQAAIBoAAABmAFuAAbAB8AAAEDIRUhAyMTIQMjEyE1IRMhNSETMwMhEzMDIRUBIRMhBUBAARj+0FCYWP7YUJBQ/wAB",
    "GEj+6AEwUJBQAShQkFABAPzwASBA/uADgP64iP5QAbD+UAGwiAFIiAGw/lABsP5QiP64AUgAAwJQ/4gFsAYQABwAIQAmAAAlFSM1Iic1FjMRJiY1NDY3NTMVFhcHJicRFhYVEAERBhUUARE2NTQESIjoiMio0JCw",
    "sIi4mECQgNiQ/hCwATi4cOjgSKhYAbBAqICAsBiwsAhAmEAI/mBQoHj+6AKwAXAgkIj+6P6QGKCAAAUA8P/wBxAFyAALABcAGwAnADMAABM0NjMyFhUUBiMiJiU0JiMiBhUUFjMyNgEBIwEDNDYzMhYVFAYjIiYl",
    "NCYjIgYVFBYzMjbwmJCYmJiYkJgByFBQSFBQSFBQAzD80JgDKJCQmJiYmJiYkAHASFBQSEhQUEgEAOjg4Ojo4ODoqKCgqKCoqAJY+kgFuPwA6ODg6Ojg4OiooKCoqKCgAAMBuP/wBsgF0AAZACMAKwAAASY1NDYz",
    "MhYVFAUBNjczBgcBIycGIyImNRABNjU0JiMiBhUUAQEGFRQWMzIC4KjAuKi4/tABYGgouDigARjoqMj42OgBwOhoUGBYAeD+eNiQeMADKLiwkLCwkNCw/pBosPCg/tiwwNDAAQABAIiISGBYUIj9GAGYgLhwgAAB",
    "A6ADqARgBbgAAwAAAQMjAwRgKHAoBbj98AIQAAEDEP7ABeAFuAALAAABMwAREAEjJgAREAAFIMD98AIQwOj+2AEoBbj+wP24/cj+yGgB6AEgASgB6AABAiD+wATwBbgACwAAASMAERABMxYAERAAAuDAAhD98MDo",
    "ASj+2P7AATgCOAJIAUB4/hj+2P7g/hgAAQHQAlAGMAYYAA4AAAEDJRcFAQcDAycBJTcFAwRoMAHgGP44ATCw8Ni4ATD+OBgB2CgGGP5wcMAY/pBgAZD+cGABcBjAcAGQAAECMAEIBdAEoAALAAABITUhETMRIRUh",
    "ESMDuP54AYiQAYj+eJACiJgBgP6AmP6AAAEBUP8IApgBMAAGAAMAMDElAyMTIxEhApjQeIh4ATgo/uABIAEIAAEBKAKgBsADKAADAAMAMDEBIRUhASgFmPpoAyiIAAEBYAAAApgBMAADAAMAMDEhIREhApj+yAE4",
    "ATAAAQIQAAAF8AW4AAMAAAEBIwEF8PzoyAMYBbj6SAW4AAICMP/wBdAF0AALABcAAAEQEjMyEhEQAiMiAgEQAiMiBhEQEjMyEgIw6Ojo6Ojo6OgC6JiAiJCQiICYAuABeAF4/oj+iP6I/ogBeAF4AVABAPj+qP6o",
    "/wABAAABApgAAASwBbgACAAAISMRNDcFJwEzBLCwCP7wYAGAmAOQwKjoeAEwAAECOAAABcgFyAAXAAAhITUBNjY1NCYjIgcnNjMyFhUUAgcBFSEFyPxwAWDQcIBwoJhowOjA4IjY/ugCsKABeOjIeHCAiHio0LCA",
    "/wDw/tgIAAECMP/wBdAFyAAiAAABBBEUBCEiJzUWMzI2NTQmIyM1MzI2NTQmIyIHJzYhMhYVEARoAWj+8P74+JC4yLCwuMCIiKCwiHC4qFi4AQDQ4AMAMP7QyOhIsGCQkICAmJiAYHh4gJDIoP7gAAIB4AAABggF",
    "wAAKABIAAAEjESMRITUBMxEzIRE0NyMGBwEGCNCw/VgCmMDQ/oAICCA4/mABSP64AUigA9j8MAFg0OBoSP2gAAECSP/wBbgFuAAaAAAlNRYzMjY1NCYjIgcnEyEVIQM2MzIEFRQAISICSJDYqKiwqFiQWDgCsP3o",
    "KHBg2AEA/vD/AOA4sGCgmJiQGDgCsKj+YBDowOj/AAACAjD/8AXQBcgAFQAhAAABFSYjIAMzNjMyFhUUAiMiABEQACEyASIGFRQWMzI2NTQmBWBIYP5IEAhg2MDg+MjQ/vABQAFAaP8AgLCogIiIiAW4mBj9sKjo",
    "0Oj/AAFIATgBsAGo/UCoaKDQqKiYmAABAigAAAXYBbgABgAAIQEhNSEVAQLoAjD9EAOw/dAFEKiQ+tgAAwI4//AFyAXQABMAHQApAAABBBUUBiMiJjUQJSY1NDYzMhYVFAU2NTQmIyIGFRQTBBUUFjMyNjU0JicE",
    "mAEw+NDg6AEY6NjAwOD+YOh4cHhw0P8AiJCIkGioAwio4LDg0LgBAIiQ4JjIyJjoOGiwaGhoaLD/AHjQeHiIcFiIUAACAjD/8AXQBcgAFQAhAAAhNRYzIBMjBiMiJjU0EjMyABEQACEiATI2NTQmIyIGFRQWAqBI",
    "YAG4EAhg2MDg+MjQARD+wP7AaAEIeLCweIiIiJgYAlCw8NDoAQD+uP7I/lD+WALAoHCg0KiomJgAAgGoAAACyAQgAAMABwADADAxASERIREhESECyP7gASD+4AEgAtgBSPvgAUgAAgGI/vgCqAQgAAMACgADADAx",
    "ASERIREDIxMjESECqP7gASCAaFiQASAC2AFI++D++AEIAUgAAQIwALgF0ATgAAYAACUBNQEVAQEF0PxgA6D9IALguAHgaAHgoP6I/pAAAgIwAbgF0APoAAMABwAAATUhFQE1IRUCMAOg/GADoANYkJD+YJiYAAEC",
    "MAC4BdAE4AAGAAAJAjUBFQECMALg/SADoPxgAVgBcAF4oP4gaP4gAAICOP/gBbgFyAAXACMAAAE1NDYkNjU0JiMiByc2MzIWFRQGBAYVFRMUBiMiJjU0NjMyFgNwUAEASJCIsMBI4NDg8Fj+4EBAQEBAODhAQEAB",
    "oCB4iMB4YFh4WJBoyKhwoOBgWBD+0EhISEhIQEAAAgD4/0gHCAW4AC4AOQAAAQYjIiY1NDYzMhcDFRUUFjMyNjUQACEgABEQACEyNxUGIyAAERAAISAAERQCIyIDJiMiBhUUFjMyEwTgYMCQsOjAqJAYOEBIcP7I",
    "/wD+wP6IAUABINjgwPD+mP5wAdgBcAFAAYjIkKhIUEh4kGBYyBABkLDIuND4MP5gQAhYWMDAARABQP5w/qj+0P64WIhYAZABaAGIAfD+cP6w6P7wArAYsKB4gAE4AAIBaAAABpgFwAAHAA4AACEDIQMjATMBAQMm",
    "JwYHAwXQsP24qMgCQLACQP5QqDAQEDigAcj+OAXA+kACaAHIgGBAoP44AAMCIAAABiAFuAANABYAHwAAASEgFhUQBRUEERQEIyETITI2NTQmIyERESEyNjU0JiMCIAHQARjw/tgBUP8A4P3guAEwqIiQsP7gAUig",
    "mKCgBbi4uP7wMAg4/uDA6ANIeHhwcP2Y/fCIiICAAAEByP/wBjgFyAAVAAAlFQYjIAAREAAhMhcHJiMiABEQACEyBgCg6P64/pgBiAFI8LBQqKjo/uABAAEIkMigOAGAAXABWAGQUKBQ/sj+6P7g/tgAAgHoAAAG",
    "cAW4AAgAEQAAIREhIAAREAAhAREzIAAREAIjAegB6AE4AWj+iP6w/vjwARABCPj4Bbj+iP6o/pj+gAUY+4gBIAEgASABGAABAjAAAAXQBbgACwAAISERIRUhESEVIREhBdD8YAOg/SACuP1IAuAFuKj+QKD9+AAB",
    "AjAAAAXQBbgACQAAISMRIRUhESEVIQLwwAOg/SACuP1IBbio/gCoAAEBoP/wBmAFyAAZAAABIREGISAAERAAITIXByYjIAAREAAhMjcRIQRYAgjw/uj+uP6QAZABcOjISNCw/wD+2AEYARCImP6wAwj9MEgBiAFo",
    "AVgBkFCoWP7Q/uD+4P7YIAGwAAEB0AAABjAFuAALAAAhIxEhESMRMxEhETMGMLj9ELi4AvC4Aqj9WAW4/ZgCaAABAigAAAXYBbgACwAAISE1JRElNSEVBREFBdj8UAF4/ogDsP6IAXh4GASYEICAEPtoGAABAgD/",
    "8AVIBbgADQAAJTUWMzI2NREzERQAIyICAKCYqLC4/vDw4CioQKCQA/j8CND/AAABAiAAAAZ4BbgADAAAISMBBxEjETMRNwEzAQZ46P3YkLi4eAIw4P2QArBw/cAFuP0YmAJQ/WgAAQKAAAAF+AW4AAUAACERMxEh",
    "FQKAwAK4Bbj68KgAAQFQAAAGuAW4ABIAACEBIxIVESMRIQEBIREjETQTIwEDqP5ICBCoARABoAGgARjAEAj+QAUA/uiA/JgFuPtYBKj6SAN4iAEA+wAAAQGgAAAGYAW4AA8AACEjASMSFREjETMBMwI1ETMGYMD8",
    "oAgQqMADWAgQsAS4/uCA/OgFuPtIAQiQAyAAAgFg//AGoAXQAAsAFwAAARAAISAAERAAISAAARACIyICERASMzISAWABYAFAATgBaP6Y/sj+wP6gBIDw8PDw8PDw8ALgAXABgP54/pj+mP54AYABcAEgASj+2P7g",
    "/tj+2AEoAAICSAAABjAFuAAKABMAAAERIxEhIAQVFAQhJTMyNjU0JiMhAwjAAegBAAEA/vD++P7w+MioqKj+6AI4/cgFuNjY2PigkJiIkAACAWD+YAagBdAAEAAcAAAlFgUHJAMjIAAREAAhIAAREAMQAiMiAhEQ",
    "EjMyEgUASAEYeP7wiFD+wP6gAWABQAE4AWjA8PDw8PDw8PAYqHiYgAEQAYABcAFwAYD+eP6Y/dACMAEgASj+2P7g/tj+2AEoAAICEAAABmgFuAAMABUAAAERIxEhIAQVEAUBIwElITI2NTQmIyEC0MAB4AEIAQD+",
    "4AGQ4P6o/qABIKComLj+6AJg/aAFuNDQ/uBo/XACYJiQiIiAAAECAP/wBgAFyAAhAAAlNRYzMjY1NCcmJSYmNTQkITIXByYjIgYVFBYEFhUUBCEgAgDo4MDISDj+wNioAQgBAODwSNi4qKB4AiCg/vD+6P7AMLBQ",
    "cHhgODBwSNCQoNBYoFh4WHBgwLiI0MgAAQGYAAAGaAW4AAcAACEjESE1IRUhBGDA/fgE0P34BRCoqAABAbD/8AZQBbgAEQAAAREUACEgADURMxEUFjMyNjcRBlD+yP7g/uj+0LjQ0MDICAW4/FD4/uABIPgDsPxI",
    "uLi4uAO4AAEBaAAABpgFuAAJAAABMwEjATMBFhcTBdDI/cjA/cjIAXgwKFgFuPpIBbj8IJCQASAAAQCIAAAHeAW4ABgAAAEzExIXNjcTMwEjAyYnBgcDIwEzExYTNjcDoMjgSBgYKMjI/pDA+CgoKCDwuP54yOAY",
    "KCgoBbj8qP7wiNioA3D6SAOoiLDIcPxYBbj8iHD++PigAAEBgAAABnAFuAALAAAhIwEBIwEBMwEBMwEGcOD+aP5Y0AII/jDQAXgBcMj+OAKI/XgC+ALA/cACQP1YAAEBkAAABnAFuAAIAAABATMBESMRATMEAAGY",
    "2P3wwP3w2ALQAuj8gP3IAjADiAABAdgAAAYoBbgACQAAISE1ASE1IRUBIQYo+7ADWPzABCD8sANokASAqJD7gAABAzj+wAVwBbgABwAAASERIRUhESEFcP3IAjj+gAGA/sAG+Jj6MAABAhAAAAXwBbgAAwAAAQEj",
    "AQLYAxjI/OgFuPpIBbgAAQKQ/sAEyAW4AAcAAAUhESE1IREhApABiP54Ajj9yLAF0Jj5CAABAggCKAX4BcAABgAAAQEzASMBAQIIAahoAeCg/pD+wAIoA5j8aALg/SAAAQAA/sAICP9IAAMAAAEhNSEICPf4CAj+",
    "wIgAAQMQBNgEoAYgAAcAAAEjJic1MxYXBKCAmHjgUGAE2IiwELB4AAICKP/wBcgEYAAXACIAACEnIwYjIiY1ECU3NTQmIyIHJzYzMhYVEQMHBgYVFBYzMjY1BUgoCIj4sMACGNiAiKC4QMjg2NCwsOCocHCguJio",
    "qJgBUBAIQHh4UIhguLj9EAIYCAhwaFhYqJAAAgIw//AGKAYYABIAHgAAJSMHIxEzERQHMzYzMgAREAAjIjcyNjU0JiMiBhUUFgLoECCIuAgIcPDgAQD++NjgyKCYmKCwmKCIiAYY/ohYkKj+2P7w/uj+4JDY0NDQ",
    "uOjowAABAlD/8AXIBGAAFQAAAQcmIyIGFRQWMzI3FQYjIAAREAAhMgXIOJiAuLiwuLCQeND/AP7oASABELAEIJg40NDI0ECgOAEgARABGAEoAAIB2P/wBdAGGAARAB0AACUjBiMiABEQADMyFzMnETMRIwM1NCYj",
    "IgYVFBYzIAUoEHjo4P8AAQDY6HgQCLiIMKCwmKCgoAFIkKABIAEQARgBKKCgAbj56AH4KOjA0NjQ0AACAgj/8AX4BGAAEQAYAAABIRIhMjcVBiMgABEQADMyABUlITQmIyIGBfj80AgBYNC4qNj/AP7QASDo2AEQ",
    "/NACaKCIiKgCAP6IUKBIATABAAEIATj+8OAokKCgAAECEAAABdAGIAAVAAABIREjESE1JTU0NjMyFwcmIyIGFRUhBYj+gLj+wAFAuNCAeChoaHhYAYADwPxAA8BwIGDAsCCQGGB4aAADAdj+GAYoBGAAJgAyAD8A",
    "AAEVBxYVFAYjIicGFRQWMzMyFhUUBCEiJjU0JSY1NDcmJjU0NjMyFxM0JiMiBhUUFjMyNgMjIgYVFBYzMjY1NCYGKMBA6NA4KGBQWMi4wP7Q/tDw8AEYYIhweODYYEhoiIiAiIiIgIiY0IiImJjg4GgESHAYWICY",
    "yAg4UCgomJDAuJiY0EAocHBQILBgsNAY/qhweHh4cHBw/ZhgYFhYcHBQQAABAhgAAAXoBhgAFAAAATMRBzM2MzIWFREjETQmIyIGFREjAhi4CAh48OjIuHiIwKC4Bhj+MJCowND9MALAkHiw4P3IAAICSAAABbgG",
    "EAALABUAAAEUBiMiJjU0NjMyFgMlNSERBRUhNSUEaDgwODg4ODA4yP74AcABYPyQAVgFoEA4OEA4ODj94Bh4/EgYeHgYAAICEP4YBOAGEAALABsAAAEUBiMiJjU0NjMyFgE1FjMyNjURJTUhERQGIyIE4Dg4MDg4",
    "MDg4/TCImIB4/mACWNjYoAWgQDg4QDg4OPhgmChwaAQ4GHj7QLDAAAECaAAABiAGGAAMAAABATMBASMBBxEjETMRAxACGNj+GAII2P5YgLi4AigCIP4o/ZAB+FD+WAYY/TAAAQJQAAAFuAYYAAkAAAElNSERBRUh",
    "NSUDqP7wAcABYPyYAVgFiBCA+ngYeHgYAAEBEAAABvAEYAAhAAAhETQmIyIGFREjETQmIyIGFREjETMXMzYzMhczNjMyFhURBjhoaIiIsGhoiIi4mBgIYND4SAho4LC4AsCIgLiw/aACwIiAsOD9yARIkKi4uMjI",
    "/TAAAQIYAAAF6ARgABMAACERNCYjIgYVESMRMxczNjMyFhURBTB4iMCguJgYCHjw6MgCwJB4sOD9yARIkKjA0P0wAAIB+P/wBggEYAALABcAAAEQADMyABEQACMiAAE0JiMiBhUUFjMyNgH4ARjw6AEg/ujw6P7g",
    "A1CgqKigoKiooAIoARABKP7Q/vj+8P7YATABCNDQ0NDQ2NgAAgIw/hgGKARgABIAHgAAJSMWFREjETMXMzYzMgAREAAjIhMiBhUUFjMyNjU0JgLoCAi4iCAQgODYAQj/AODw2KigmLCgmJiQkFD+aAYwiKD+2P7o",
    "/vD+4APYwOjouNDQ2NAAAgHY/hgF0ARgABIAHgAAATM3MxEjETQ3IwYjIgAREAAzMhM1NCYjIgYVFBYzIAUYCBiYuBAQePDY/wABAODggKCwmKCgoAFIA7iQ+dAB0CiAoAEgARABGAEo/Zgo6MDQ2NDQAAECmAAA",
    "BbAEYAAPAAABByYjIgYVESMRMxczNjMyBbAweGioqLiQGAiI8HgEMKgwsLj9sARIyOAAAQJo//AFoARgACAAACU1FjMyNjU0JiQmNTQ2MzIXByYjIgYVFBYFFhYVFAYjIgJoyLCIiFD+UHjY0MioOLiIeHhIARCo",
    "eODg8DCoWFBQQECwiGCAqEiYSEBIODhwQJBgkLAAAQIw//AFqAVwABUAACUVBiMiJjURITUlEzMRIRUhERQWMzIFoIB4uLj++AEIUGgBuP5IYGBgmIggqLACeGAwASD+2Ij9iGhgAAECGP/wBegESAATAAABERQW",
    "MzI2NREzESMnIwYjIiY1EQLQeIjAoLiYGAh48OjIBEj9QJB4sOACOPu4kKC42ALIAAEBwAAABjgESAAKAAAhATMBFhc2NwEzAQOI/jjAARhYEAhgARi4/jgESP1Q2Ego+AKw+7gAAQEYAAAG6ARIABcAACEDIwYH",
    "AyMBMxMWFzY3EzMTFhc2NxMzAQT4+AgwGKjY/ujAgCggKCiwyKgwICAoiLj+4AOg8Ej9mARI/big0NCAAmj9mKioyKgCSPu4AAEB0AAABjAESAALAAABATMBATMBASMBASMDmP5Q0AFIAVDI/lAByND+oP6g0AIw",
    "Ahj+YAGg/ej90AHA/kAAAQHA/hgGEARIABYAAAEzARYXMzQ3EzMBBgYjIic1FjMyNjc3AcDAAShAIAhQ+Lj+MEjAoGhgSGhocDAwBEj9UKBoEPgCsPsgwJAQkBBYcIgAAQJQAAAFsARIAAkAACEhNQEhNSEVASEF",
    "sPygApD9kAMw/XgCmIADQIiQ/NAAAQJo/sAF2AW4AB0AACUUFjMVICQ1ETQmIzUyNjURNCQhFSIGFRUQBRUEEQSAsKj++P8AuLCwuAEAAQiosP7wARAYYGiQqKABKGBgmGBgASCoqJhgaPj/ACAQIP8AAAEDuP4Y",
    "BEgGGAADAAABMxEjA7iQkAYY+AAAAQIo/sAFmAW4AB0AAAEQJTUkETU0JiM1IAQVERQWMxUiBhURFAQhNTI2NQOAARD+8KiwAQgBALiwsLj/AP74sKgBEAEAIBAgAQD4aGCYqKj+4GBgmGBg/tigqJBoYAABAjAC",
    "SAXQA1gADwAAATU2MzIEMzI3FQYjIiQjIgIwaJBgASBAaIBokGj+6EBoAkioaHh4oGhwAAIBCP9ABfACeAADAAsAAAEzESMBMxUQBSckEQVQoKD84KD+yJABKAJ4/OADGND+iOhwyAEoAAMAaALQB5AGgAAVABkA",
    "HQAAARcHITUzFSEVIRUhFSE1ITUhBgcnNgMhESE3ITUhAeCIMAFwoALI/TgDSPjYA0D+EDBAcLhYBYj6eJgEWPuoBoAoUHh4iHiIiHgwIFhw/jj+oHhwAAYAYP9IB5ADaAAXAB4ANQA5AEEARQAAARcGByEVBgcW",
    "FwckJwYFJzY3JicGByc2FxYXMjY3ISUhESMVMxUjFTY3FwQFJzI3ETMRNxEhNyE1IQERIzUhFSMREyE1IQSQiAgQAghQkKjAOP742Mj++DDAmEg4KDBwsGhoeBCoOP5Q/BgCiOjg4JB4GP6Y/kgYQDCQiP7wkAFo",
    "/pgFeJD+UJCQAbD+UANoIBgYcIBQKCCAKFhIKIAQKCgwKCBgYCBIMFhAqP5oiHioEBh4SDCICAF4/pgQAcB4qP44/jhISAHI/viYAAMAYP9IB5gDKAAfACQAKAAAARUhESEVIxcGBxYFByQDIxE2NxcGBycRIwIH",
    "JzY2NREBNjchFgEhFSEHSPpQBbCoWGi4sAEQOP1w8NiomCDg0EjYEJiQYEgEMKiA/hhY/VgEiPt4Ayh4/uh4QFhIQCCISAGA/sAoMIBAMFABiP7wyFCQ0JgBmP1gQFhYAZhwAAMAeP8wB4gDYAALABEAIAAAARcH",
    "BAUHJCUEBSckBRYXByYnAxYXNjchNSEVBgcXByQlA+CgMAF4AcBY/lj+UP6w/kBQAmABMDggiCA4eICIkGD8yAQQeLDAeP74/pgDYDggwGiQcPDgkIjAEEBQMFhA/lgoOGBgkIiQgFCAmIgAAwPoAFgHcAZwACEA",
    "JQApAAABMzY3FwYHIRUhBgchERQGIyInJxYzMjU1IREjEQcnNjcjASE1IREhNSEEMPA4KJggKAGg/hhAMAJAYFg4UCBoODD+gJBoaIhgoAEYAYD+gAGA/oAFmHBoIGBYkHBA/LBYWBCIEEiA/rgDiGhwiJD+MJj+",
    "YIgABAGo//AGeAUwABYAHAAgACQAAAEXByEVBgcWBQckJQYFJyQ3JicGByckFxYXNjchAyERITchNSEDMJgoAfhosMgBMGD+4P742P7QQAEAuFhASEh4AQhQWHiQaP5g4AMw/NCQAhD98AUwMEiIuHhYQIhIgHBY",
    "kEBYSFhAOGC4QGhQSKD9qP4QiOgAAwKQALAFaARoAAMABwALAAABESERAREhERURIREFaP0oAkD+WAGoBGj8SAO4/nABAP8AmP74AQgAAgJ4ARAFaAQIAAMABwAAASERITchESECeALw/RCgAbD+UAQI/QiYAcgA",
    "BgIoAHgHgAaAAB8AIwApAC8ANQA7AAABFhchFSERMzUzFSE1MxUzFSMRIREjFRADJxIRESEmJwE1IRUFFhcHJiclFwYHJzYlFhcHJiclFhcHJicFQDAYAdj8AMiYATiQ4OD9oMiokKACGBggAVD+yAIIcEiASGD9",
    "cIhAWIhoAWgoEJAIIAGAMBiQECgGgEhgkP8AyMjIyIj+kAFwUP5w/tBYATgBcAIoQDj8iOjosKDIONCYKDDYmFCoiKCwKLigIJioKLCYAAQCgABQBzgGSAAZAB0AIQAlAAABESEGByEVAgUnJBMhBxYXByYnBgcn",
    "NjchEQUjETsCESMBMxEjBzj9mCgwAlDY/SBAApi4/fAYeGhwaHhAWHDwmP6gArDIyJDAwP1guLgGSP3ASEiI/gCgmHgBkCBYYIB4WEBAeLjwAkCQ/uABIP7gASAAAwJgANAHiAZ4ABUAGQAdAAABFwczNTMVIRUh",
    "FSEVITUhNSEGByc2AyERITchESEDoIhA2JgBwP5AAjD62AJg/uBIWHjAOAPw/BCYAsD9QAZgKJjY2JD4kJD4eFhY0P2I/eCQAQgABQLQAIgHSAZIACMAJwArAC8AMwAAASEVBgcXIREUBiMiJycWMzI1NSERIxEh",
    "ESMRISYnNxYXNjchEyE1IQUhNSEBITUhBSE1IQLQBGDI6CABqGhgUHAgkEgw/qig/riYAfhoiIBgUKB4/LCYAUj+uAHoAVj+qP4YAUj+uAHoAVj+qAZIcJhoIPx4UFgQiBBAoP7AAUD+qAQgSEBgODhAUP3YkJCQ",
    "/kioqKgAAwJIAFAHUAaAACoALgAyAAABFhczNjcXBgchESEVIQIHBgcGByczMjY3IREjEQYFJyQ3IRMhNSE1ISYnARUhNQE1IQcD0Fg4yEA4qDg4AQj+QAIwECAYOCDwGLggIAj+eJiw/thoATCg/ohAAaj+IAEI",
    "KDgB0AEw/jj+2BAGgHB4cHAwYFD+KMD+yIBgKBAIkGDg/dgB2PCYgJDIAdDIiFBI/uDIyP3wwMAAAQJwAJAHgAYwADcAAAEhFSEGBxYXFhc2NxcGBxYXByYnFhUUBiMiJycWMzI2NTUGBSckASYnNQYFJyQ3JicH",
    "BgcnJDchArgEgP44SEhoKBAQqHCIcLjAuHiowAiIiHCAIJCAODj4/shYAWABGAgQ2P7oYAEo8CAgqGCIaAFI8P4QBjCYSDiQoAgQiMBouIiw0HjQwFhw+LggqCBooEjYgJiIAQA4MBC4cJhwwCgwaDgwiGi4AAIC",
    "SABYB6AGYAAbADUAAAEXBgUVIRUhFgUHJCcRIzUGBSckNyE1ITUFJyADIzUhByECBiMiJycWMzI2NyE3IQYGByc2NgbAUNj/AAIo/lDYARhQ/sDYmMj+0GABIND+SAIg/lgwAgDo6ANwSAE4EFhwUHggkFggGAj+",
    "oFD+wBCw0GjAmAZgiBgIkIiQQJhwyP8A8LhwgFiQiIgQkPxwiNj+qKAQmCBAqNjQ+GBwWMAAAwJoAHgG+AYwAAsADwAVAAABESM1IQIDJzYSNRETIREhAQQTBwIBBuCg/YgIwJhwUKACeP2IATABCPiA4P7YBjD8",
    "wID+YP7AWNABOOACYP3YAZD9aNj+2IgBGAEYAAECiABQB0AGgAAhAAABFwYHIRUhBgchETMRIRUhFSEVIREjESE1ITUhJzY3ITUhBEiYGCACeP1QWHABIKABoP5gAdj+KKD9wAJA/jgogGD++AFIBoAgYFCY2KAB",
    "CP74mPCY/tABMJjwmKDYmAACAngAWAeABnAAHQAhAAABIREzESERMxEhFSERIRUhESMRIQIFJzYTITUhESEBIREhArABGKABIKABQP7AAVj+qKD+2Dj+8Ij4MP7AAVD+6AG4ASD+4AUoAUj+uAFI/riY/qiY/dgC",
    "KP6Y4GjIARiYAVj+qAFYAAICmACwB1AGgAAFAB0AAAEWFwcmJwEhFSECBxYXByYnBgUnJDcmJzcWFzYTIQTIaDCgOGD+iASg/wAYgLiggJio6P6YaAF4wNDweOjAaBj9AAaAcJA4kHj+4Jj+oMCgqICooPBQmFjA",
    "uKhYmKCIASgAAgJYAKAHgAYgAA8AFQAAASEVIQYHESMRBwYHJwABIQEWFwcmJwK4BKD+OCg4oLiAiHgBeAEQ/dgDUNigeKDgBiCYWGD70ANA2JBwgAEYAej+oMjYePDIAAICkACoB2gGQAADABkAAAEhFSEDIRUh",
    "AgckJSYnNxYTByYnBAUnNhMhAygDoPxgmATY/XCQiAEwAUBQaJDYiJggKP5o/jAwsID+cAZAmP6omP5wqBA4gHhY+P7gWEhIUBigyAGAAAIC2ABoB4AGcAAVABsAAAEzESEVIREUBiMiJycWMzI2NREhNSEBFhMH",
    "AicFeKABaP6YWJBwYCBocDgo/WACoP4ogECoQHgGcP7ImPyYcGAooDAoOANAmP7I2P74OAEQ2AABAnAAgAewBjgAGwAAASEREBIzMhMXAiMiAgMRIREhFSERIxEhNSERIQKgA+g4OBgQkBiggIgI/ngBWP6ooP6w",
    "AVD+4AY4/Xj+wP7AAVAg/iABMAIAAfD+KJj9WAKomAHYAAEAgP84BGgD4AAhAAABMxUhFSEVJRcGBxEjEQUnJTUhJzY3IzUhNxcHIRUhBgczAoCYASj+2AE4GKCwmP4gIAIA/nggaFDIARhAiDAB0P3oSFjwApCw",
    "gIgwgCAY/ugBAECQOKCAaHiImBiAiIBgAAID8ABoB6gGgAAoAC4AAAEVIRIXNjcXAgcWMzI2NxcGBiMiJwYHJzY3AgMjETY3FwYHJxEhAzMTExYXByYnB1D+qBAoUECQYIhIOBgYCIgQYFCIYHCgULhoSBjYODhA",
    "aIBgAWgIkBC4SCiAKEAFOJD+8NCo4DD+qNjocHAY2JD4iHB4iKgBGAGA/SBASHiIeGgD+AFI/rgBMGBwOHhYAAMD2ACoB0AGKAATABcAGwAAASEQBiMiJycWMzI2EyECBSckEyMTIREhNyERIQP4A0hYeFhwIIBY",
    "ICAI/tgQ/tBoAQAQ8CADCPz4mAHY/igGKP3wyBiYGGABWP4omIBwAYD9aP2gkAFAAAMBsP84B4gFcAAVABsAIQAAAREjESERIxEhNjchNSE3FwchFSEGBwMzAgUnJCUEFwcmJQbQoPz4oAGoIBj9SALYIJgYAmD9",
    "gBggcKAI/TBYAoABIAEA+Hjg/tgDgP1YAhD94AK4WGCYoCCAmGBY/uj9GEiYIPiIsHioqAAEAIj/SAeIBRgAAwAHAA8AQgAAASERITchNSEBESM1IRUjEQUhFSEHFhc2NxcGBxYFByQDBgcVFAYjIicnFjMyNjU1",
    "BAUnJCU0JwQFJyQlJwYFJyQ3IQGIBQD7AJgD2PwoBUiY+lCYAQgFEP1wEIg4+NBgeIBwAShw/tCIQEB4gDhoIGhYMDD+kP4IQAIoAWAY/rj+SEgBoAFQQOj+uGgBcOD+YAUY/sB4UP7w/viAiAEQ4HgQYIhQgGhI",
    "QNhgeHABCBgQYIiQCIgISEgw2HCAcOAQKKhwgFioMGhIgDhIAAIEEP9IB5gGIAATAC4AAAEhEAYjIicnFjMyNjchAgUnNhMjExcGBzM1MxUhFSEVIRUhESMRITUhNSMGByc2BDADQFiAUHgggFgoGAj+2DD/AGDQ",
    "MOiwgBggmJgBGP7oAUD+wJj+eAGI0DA4eJAGIP5QqBiQGFDw/piQgHABCP4QKFhY0NCQ4JD+eAGIkOBoSFjQAAMAaP9IB5AD0AAHAA8AHwAAAREjESERIxEBFwIABSckADMzERQWMyA2NxcGBiEiJjUGGJj86JgB",
    "4KA4/lD+SEgBqAF4oJhIeAEQWBiQGJD+mOhwA9D9MAJA/cgCyP74MP6Y/mhQmEgBWP7QIChIkCjYcEhoAAIDqAOAB2AGiAAJAA8AAAEXByEVIQYHJzYFFhcHJicEuJBIAmD9UEBQeLgBOKCIaIigBogwqJBoWFjY",
    "sGCAgJBgAAUAoAMQB2AGQAALAA8AEwAXABsAABMhFSEVIREhESE1IQU1IRUBITUhIRUhNTMVITWgBsD92AHI+gAB2P3IBAj+wP44ATj+yAHIAUCQASgGQJig/ggB+KCgoKD+kOjo6OjoAAIAaP+ABJgD4AAZACYA",
    "ABMhJic3FhchFSEGBxE2NxcGBycRBgcnJDchBRYXNjcXBgcWFwcmJ6ABwBggmDAgAYj+GEBgmIAo2LhQUGBYAQiI/qgCCGBQYECISGhYUGjQ8AM4QDgwSGCQcFj+SCgwiEgwWAGAQDiIkLCIODhYYEhoYEhQgOiY",
    "AAMAYP9YB7gE4AAoACwAMAAAASERIRUhESEWFxc2NxcGBxYFByQBBgcRMiUXBAUnEQYHJyQlIREhNSEzITUhESE1IQFwBQgBKP7Y/cA4OHDIkIhw6MgBUDD9gP6ogIgoAYAo/tj/AFCwiGgBmAEg/lj+8AEQmAPY",
    "/CgD2PwoBOD+6JD+6FhAcFiIaHBogBigGAJYaEj+yHiIYEBYAUBQKIhouAEYkIj+YIgABgIQ/1AFgAZ4ABIAFgAaAB4AIgA4AAABFwchFQYHMxEhESE2NyMGByc2EzM1IyEVMzUBMzUjIRUzNQEhNjUXByEVIQYH",
    "FhcHJicGByckNyEDOIgwAVAwMNj9EAFwOCj4OEh4qAiYmAEoqP4wmJgBKKj9cAFgCJgIAVD+oAgQuLBYqKhw2HABIED+yAZ4KGiAYFD9SAK4UFhYSGCg/diYmJj+WJiYmP5gMDAYSIggIEiIiJBQkGB4gLAACABQ",
    "AkgHkAaAACEAJwArAC8AMwA3AEsAZQAAARcGByEVBgczERQGIyMnMzI1NSMVIzUjBgcnNjURBgcnNhchNjchBgczNSMhFTM1ATM1IyEVMzUTIRAGIyInJxYzMjY3IQYHJzY3IxMXBzM1MxUhFSEVIRUhFSM1ITUh",
    "NSMGByc2AaiIEAgBSBgg2EhIcCBoKLiIuChggJA4OEDwGAEoIBj+6BgIsLABOLj+ELCwATi4yAMoUIBQcCCAWCggCP7AMPBYyCjYqIAggJABGP7oAUD+wJD+eAGI6CAoaIgGgCgQEHAoGP2AUFCIMEi4uKh4UMDg",
    "ARAgGHh4eBggGPhYWFj+2FhYWAIg/wBwEIAQKFDAUHA4aP74KEBgYIBYgNDQgFgoGFBoAAMBmP94B3gCKAALABEAFwAAATMRMxEzESEVITUhARcGByc2JRYXByYnA7CYuJgB4PogAhgDAJhoeJCQ/DB4WJBQgAIo",
    "/eACIP3gkJACADD4oFC4wLDQQMC4AAQAaP84B6AFIABKAE4AUgBWAAATMxEzESEnMxUzJic3FhczFSESFzYTFwIHFjMyNjcXBgYjIicGByc2NyERIRUjFTMRIxUzFTY3JgMhERADJxITIxAHJzYRIzUhNSElIxUz",
    "BxUhNQEVMzWoiKADmAiQeBggcEAoWP6YCDBIOIBIeEA4EBgIiBhYSHhgWIBwKBj9qAJwyMjI0GBISCD8+KCIiAh4eHBoWAFY/tgDIJCQkAFo/piQBGj+8AFAYGAgIEhASID+gPjAASgg/kDoyFhgILiA0IBweCAY",
    "A7h4qP6IoGBocPgCQP4I/lj+wFABKAEo/oiYaHABOIiASKhwmJj++KCgAAQBSAIIBzgEqAAKAA4AEgAYAAABFwchFSEHBgcnNiUzESMBMxEjJRYXByYnBNCQMAII/bhAKEiAwP4woKD+mJCQBFhgQIg4YASoKJCQ",
    "iEBYaODo/aACMP3w8FhwUGhgAAYAiP9IB4AFYAAnAC8AMwA3ADsAPwAAASQ3NjcXBAUkJSYnNxYXByYnBCEnJDcGByc2NyE1ISYnNxYXIRUhBgERIzUhFSMRFyE1ISEVITUBITUhBSE1IQKgAQCgUKiI/lD+SAKA",
    "AThASIDIgJAgKP1I/UgYAWDwyNAYwIj9sAMgEBigKCADGPwQcAOwmPuAmJgCAP4AApAB8PuAAgD+AAKQAfD+EAOwCCAQWGDgYBAgODhQkKBYMCgwiEhYGBBwUGiIKCgwOEiIaP4I/VBQUAKw+Hh4eP6YeHh4AAQC",
    "cP9IB7AE2AAWAB0AJQApAAABFwchFQYHFgUHJCUEBSckNyYnBgcnJBcWFzY3IQYBESM1IRUjERMhNSEEEJgwAmhwoNgBCFD+wP8A/wD+qFgBMMhoWFBYiAEgaHigoFj+CAgCwJj9oJCQAmD9oATYMFCAuHBQMKBA",
    "eIA4kDhQSFhIQGjIOHBQYHgQ/dj9sFhYAlD+kOgABQCw/0AHWATAAAcACwAPABcAGwAAAREjNSEVIxEBIREhNyE1IQERIzUhFSMREyE1IQdYoPqYoAEQBIj7eJgDWPyoBIiY+3iYmASI+3gEwP6g0NABYP7w/kCI",
    "sP5Q/choaAI4/rjAAAUAiP9AB4AE2AAFAAsAEQAXAC0AAAEXBAUnIAUXBgcnNiUWFwcmJyUWFwcmJwMhNTMVIRUhAAUHJAERIxEABSckASEGyFD9kPxwMALwAkCoaICIiP4YSDCYKFD+kFhAmDBY0AMgoAMg/UgB",
    "IAGoWP5I/uCg/vj+SGgBmAEI/WgE2JBQEJBoOOigSMCIYHBIcGAwiKBImJD+oIiIkP8AeKigATD+AAIY/tCwiJABAAACAyj/OAeIBEgAFAAaAAABITY1MxQHIRUhEgUHAAMCAScAEyEBFhcHJicDSAGICJgIAfj+",
    "SFgBiHD+sIBA/pBwAYAg/oADIFg4gDBYAxCQqKiQkP5I+JABAAGA/oD++HgBAAHQAchYYEhgUAACAGj/SAeQBQAAFAAwAAATITY3FwYHIRUhBgcRIxEGBycANyEFIRUGBxUhFSERFAYjIicnFjMyNREhNSE1Njch",
    "iAJIMCigGCAD4PvIcKiYUGBwAXCg/hAC2ANgiKgCAP4AYGBgWBhIYFD9uAJIgGj9gARgUFAoQDiQuLD84AKYSECAAQjwiJh4YDiQ/uBQSBCYEBgBCJCIUEgAAgB4/0gHeATYABkAHQAAEyE2NxcGByEVIQYHIREj",
    "NSEVIxEGByckEyEBIREhiAKYQECgMDgDoPwIaGgEKKD8WJiQoFABcND90AIIA6j8WAPQeJAweGCYqGD9GGhoAkBoUJC4ASD9EAFQAAMAaP9IB6AEQAAbACEAJwAAEyE2NzMGByEQAgYjIicnFjMyNzYRIQIFJyQT",
    "IQUWFwcmJyUXBgcnNvgCeBAIsAgQAigwgLh4eCCIiIAYOP5QkP1YYAJweP2oBfhoSKBAaPrwmFiImIgDcGBwcGD98P54eBiYIFiQAgj9MMigqAJQaMDgSPC4GDjQqEioAAIAeP9AB5gEiAAKACUAAAEXBgcRIxEG",
    "BycAATMRJDcXAAURFBYzIDY1FwYGISImNREHJzY3ApigWIiYcIBYAXgCKKgBQMCA/vj+iECAASBQqBCQ/ojgiLBYeJAEiDCwqPxAAxB4YJgBKAFA/jC4sGj++Lj+WCAYWJg44HBAYAGASJgoSAABAwD/sAVoBngA",
    "IQAAASM1MxEjNTMRMxEzFSMRMxUjAgc2NyYnNxITByYnBgcnNgPAwNi4uJC4uNDQYGh4iCgwgGBAkBAIwNAwcAKYkAGokAEY/uiQ/liQ/pCoEDCggDj/AP7YQEhAOBiIwAACAJADmAd4BngADQAjAAABMxEjNQYF",
    "JyQlNSE1ISUzFSQ3FwQFFRQWMzI2NxcGBiMgJjUC4KCg+P7YMAFAARD90AIwAXCgARDwWP7o/sBIwIhQEJggiNj++KAGeP04oGhQkFhggICQuEBQgGBAoCAYUKA42GhIYAAHAFD/OAegBkgAEQAVABkAHQA1ADsA",
    "QQAAEyEVIxE2MxcHFSM1BAUnNxEjBSE1IREhNSERJTUhBRcGBRUWFzY3FwYHFgUHJAERIxEEBSckBRcGBSckBRcEBSckmAOAYCggEFiY/uD+qBiAeAEQAXj+iAF4/ogBeP6IBEho8P7QcJCoeJCQoNgBEFD+GP7Q",
    "kP74/tBAAuj+CGjY/wBgAQgBeGD/AP6IWAGIBkiQ/fAIeAhwWDAgiBACWGho/qh4/pAoWMhwUDgIeGh4iFiYcIBIoKABQP3wAsAoKJBQ6HCIWGhoIHDogIiAAAUAeP94B5AE6AATABcAGwAfACMAAAEzByEVIQch",
    "ESEVITUhESE3ITUhATUhFRUhNSERITUhESE1IQOwoAgC8P0ACAJQARD46AEYAgAQ/RgC8AJI/DgDyPw4A8j8OAPI/DgE6KiIYPyoiIgDWGCI/jhYWNBY/thY/tBgAAIDsANQB4gGSAARABYAAAEhFQYHFhcHJicG",
    "Byc2NyYnIzMWFzY3A9ADQHCgqOBQ+Mio6Di4kJBAWPBIeIhQBkiQwIBQQJhIiGA4iChImKCIYGiAAAYAaP9QB5gEuAAPAB0ALgAyADYAOgAAARYXITY3FwYHIRUhNSEmJwEzERQGIyInJxYzMjY1AREUBiMiJycW",
    "MzI1NSERIxETITUhESE1IQEzESMCcFhAAchAKKAoOAIg+NAB6DA4BICgUHhoYBhgaCAg/WBoaEBQIHA4QP5AmJgBwP5AAcD+QANIoKAEuFBgUGA4QDiQkDgw/rj86HBQGJAYIDgC0Pz4WFgQiAhIWP7QA7j++Hj+",
    "kHABYP1wAAUAaP9IB5gEmAAVABkAHQAhACUAAAEhESEVIRUhESMRIQYFJyQ3ITUhNSETITUhESE1IREhNSEBNSEVAUgFgP7IAgj9+KD+IDD+gHABODj+CAIQ/tCYBFD7sARQ+7AEUPuwAxD+KASY/Ph4kP7IATjA",
    "gJhIYJB4AihY/thY/thY/qh4eAAGAQD/SAcoBFgABQAUABgAHAAgACQAAAEWFwcmJyUhERQGIyInJxYzMjURIQUzESMBESERATUhHQIhNQIQcEiYOHABmAQIYGBQcCiAUDj8mP3goKAEaP0gAkj+UAGwBFhoeFBw",
    "cAj8EGhwCJgIcAM4UPwQA5j9UAKw/vCIiICYmAAFAGj/iAeYBIAADAAQABoAIAAmAAABAAUnJAEXBgcEBQckJSEVIQEhNjcXBgchFSEBFhcHJicFFhcHJicD0P6w/khgAlABMIgQGAGAAdBg/kj82AMY/Oj+iAPQ",
    "qGCgaHgBsPm4AvBgIKAgWP7oYCCgIFgDsP8AmIDYARBIGBDoeKCIGJj+CPDoOPCwmAJgmKAoqJAImJAwoJAAAwBg/0gHQAR4AB4AIgAmAAABIREhFSECBiMiJycWMzI2NyERIxEABSckNyETITUhIRUhNQEhNSEB",
    "MAWw/YAC4BBgWIigILB4GBAI/dig/vj+AFgB+ND9wGACeP1wAzAB4PtoAhj+CAR4/kCw/oiwCJgIQMj9yAH4/tigkJDoAcCwsLD+GLAAAwBQ/0gHiARAAAoAHwAlAAABFwYHESMRBgcnJCUhNTMVIRUhERQGIyIn",
    "JxYzMjURIQUWFwcmJwIokEhYoGBoYAEIAYgC8KABGP7oWHiQgCCIkEj9EAEgkGCgUJgEQEiQkPxwArh4YJDoqMjImP1weFgYoCBgAmhIqMhgwLAABQEA/0gHAARgAAsADwATABcAGwAAAREjNSEVIxEhNTMVASER",
    "ISERIREBIREhIREhEQcAoPtAoAKooP1YAgj9+AKoAhj7QAII/fgCqAIYA4j7wHBwBEDY2P5gAQj++AEI/WABCP74AQgAAwEAAtAHYAZ4AAMAGgAeAAABMxEjARYXNjchNSEVAgcWFwcmJwYHJzY3JicBMxEjAmiY",
    "mAHQcJigUP1wA1BwqKDocOi4wOhQyJCIaP1AoKAGePxYApCAYHigmHD/AIhQOJBIYHg4mChQYIABGP0QAAIA8P9IBzAECAAlACkAAAEhESERIQchERQGIyInJxYzMjURIQYHFhcHJicGByc2NyERIxEhJSE1IQO4",
    "/hAEeP4YEALogIA4UChwOGj9kAgI4LhwsMBw8Ej4WP4YmAK4/sADOPzIAmABqP5YcP4YYGAYkBBIATgQGFh4iIBgqECQQLj96AKo+JgAAgBw/0gHqAPAABUAGwAAEyE2NxcUByEVIRIFByQDBgAFJyQTIQEWFwcm",
    "J5AC+CAIoCADQP0AyAJwWP2Y+FD+aP7QaAI4sP04BOhoSIBAcAKYgKgQmICY/niAsKAByND+sECYgAGYAbhYaFBoYAADALD/iAd4BMgABQALABcAAAEXAAUnJCUEBQckJQEhFSERIRUhNSERIQMYaP8A/ohYAZAC",
    "sAFQASCA/vD+uPygBdj9YAMY+UADCP1oBMh4/wCAiJjIoNiA4Jj+SKD+QJiYAcAABABQAlAHqAZ4AA4AFAAYABwAAAEXBwAFByQnFSE1BgcnJAchJicGBwEhESE3ITUhA+igKAGoAaBg/tCg/ODQ4FgCgAgCcLCY",
    "eJj+qATY+yiQA7j8SAZ4MCj++HigaGhoSHhYmPiAYHBgYP8A/lCIoAAEAQACqAdwBngACgAOABIAGAAAARcGByEVIQIHJxIBMxEjATMRIwEWFwcmJwTQoCgoAlD9eHBwgOD+GKCg/oCgoASwkIiAgKAGeDiIaJj+",
    "6KBoAWgBqPwwA4D86AEwcJiAmJAAAgBwAegHmAaYAAUANAAAARYXByYnARcFFhc2NxcGBxYWMzI3FwYGIyIkJwQFJyQ3JicFJyUmJwUnJSYnMxYXJRcFFhcE0EggkCBIAvgQ/OAwSOC4aLDIKNhAkAiYEJCQYP7Y",
    "cP4w/oBIAjDwWCj9EBgCwCAQ/fgYAfggCKAQGAMYEP0AECAGmEhYMGBI/oCYWEhASFhwWEgoWMAoqJCAYIhImGBQaEBQmEhASDCQMHB4eGhAkEBAOAAEAGgCaAeYBpAABQAPABUAGwAAARYXByYnJRcGByEVITUh",
    "NgEXBgUnJCUEBQckJQIomGCYWKAECLhgcAGw+agD8Hj9aHDA/mBQAVgDeAEwATBg/tD+0AaQgIhYiHhQOLiImJiw/niAuJCYaMhgwKDYaAAEAID/cAeABGAAAwAHAAsAGwAAASEVIQUhESE3ITUhExYXITY3FwYH",
    "IRUhNSEmJwK4ArD9UP7IBNj7KJgDqPxYaGBIAZhYMLAoWAII+QAB8DhIBGCQgP34kOj+YIiYgKA4aICQkHhoAAICSP9AB6AEwAASACgAAAERFDMzFSEiJjU1IQYGByc2NjUDIQIFFgUHJCUGBSckNyYnNxYXNjch",
    "BjhA4P74WFj+eBB4kGCIYIgD4CD+4OgBGFD+qP7o6P6gUAEoyJB4WJDg4Dj88ATA/thQiFBYwLioQHBAoOj9oP7Q0FAwoEB4cEigMEhYgHiYaHioAAIA6AMYBygGeAARACUAAAEXBgURJSc3FhcHJicGBycRJCEh",
    "AgIjIicnFjMyNhMhAgUnJBMjA0hw+P7AASBQgIBYkBgg4NBIAWABqAM4CICYKFAgYDBAOAj+6Aj+2HABAAjgBniAaDD+iHiISMDgQEhAcEhYAmA4/hj/ABCgEJgBIP544HjQASAABQCgAcgHYAWQAB0AIwApAC8A",
    "NQAAARcGBzI3NjcXAgU2NyYnNxYXByYnBAUnNjcGByc2JRYXByYnJRcGByc2ARcGByc2JRYXByYnA6iQeGBwiEhAkOj+4MioICiAiGCQICj+0P6gKMCwiJgYqP4YgFiQUIgF2IiIiHig+8B4kNh44ASoqJB4iKAF",
    "kCj4cBhQWDD+yNAgKDAwQKDIQFBISDCAeLAYEIjIQHCIUIBwWFCwaHB4/vBYsJh4mHhgiJCgaAADAGgBGAeIBngAGwAwADYAAAEXByECASckEyEGBxYXByYnBgcWFwcmJwYHJwAlITY1MxQHIRUhEgUHJAMCBSck",
    "EyEBFhcHJicB+JA4AahI/YhgAgho/tAQGIBoaGBoGCCAaGhoeBgoaAEAApgBKAiYCAGI/rBIAUho/vCAaP6ASAGIMP7oAohgWIBIYAZ4KJj8qP64kPACkCAgSGBwWEAwKGB4eIBYIChwARgIqOjgsJD+YPiI4AF4",
    "/njQgOABwAIQYIBgeHgAAQBgASgDMAaAACAAABMhETMRMxUjETcXBgcRFAYjIicnFjMyNjU1BgcnNjcRIYABKKjQ0MgYcHBgkDg4IDhAQCCAmDCwmP7YBTgBSP64kP74QIAwIP7weGAIoAgoOLgoIJAgMAEwAAIB",
    "OAGABzgGeAALAA8AAAEzFSEVIREhESERIQEhESEDiKADEPzwApj6eAJQ/lAESPu4BnjYmP74/YACgP4YAVAAAQEoA0AGyAZYAAsAAAEhNSE1IREhNSE1IQFoBLj7GAWQ+mAE+PtIBSCgmPzooKgAAwF4AlgHIAZ4",
    "AAsADwATAAABMxUhFSEVIREhESEBITUhESE1IQN4oAMI/PgCiPrYAgD+oAPo/BgD6PwYBnhokHj9UAKw/vB4/oCAAAQDCP/IB5AGaAAFAA8AEwAXAAABFhcHJiclFwYHIRUhNSE2ASEVIQMhFSEEWHBIkEBwAnCw",
    "WGgBOPwYAhBo/bgDaPyYqASI+3gGaJCgWKCYUDDYoJiYyP0gmP5QmAADAKACwAdgBoAADwATABcAABMhNTMVITUzFSEVIREhESEFITUhATUhFaABQKADEKABMP7Q+7D+wAHgAxD88AMQ/PAFyLi4uLiY/ZACcKio",
    "/iioqAACAHgCeAeYBngAHAA7AAATITUzFSEVIQchFSEHFhcHJicGByckNyE1ITY1ISUhNTMVIRUhFCMUByEVIRYFByQnBgUnNjchNSE2NyHIATiQASD+4AgBUP6YEMigYJigcPBYARBA/sABaBD+yAOAATiQASj+",
    "2AgIAXj+sGgBCFD+8Hhg/uhQ6FD+4AFYEAj+yAXgmJiImIgoWHB4cGDAaIh4wIhIUIiYmIgQSECIsFCQYPDAcIBgkIhIUAAFAPgC4AcABpAADwATABkAHQAjAAABFhchNjcXBgchESERISYnAyERIRcWFwcmJyUR",
    "IREFFwYHJzYCiHhQAVBoSKhQUAGo+fgBkEBYaAIo/dj4WECIOFgCUAIY/tCYSGCAYAaAcHh4gDBwWP1IArhYSP0wAahIaIBAiGiA/lgBqEgwqHBIgAAFAGj/SAeYBIgACQAaAB4AJAAqAAATISYnNxYXIRUhFyER",
    "IREUBiMiJycWMzI1ESE3ITUhExcGBSckJRYXByYnaANAICigMCADSPjQ6AVg/cBQgHhgIIB4MP2AkAQ4+8hoYMD+6FgBMAPw+LB4uPgDuFhAOGBwkFD+aP7QcFgYoCBIARiIiP7AcLhgiGiYgJCAqIgAAwBw/6gH",
    "kAKwAAsAEQAXAAA3IREzETMRMxEhFSEBFhcHJiclFwYHJzZwAoCg8KACcPjgASCQYJBYkAVgkHCoaJA4Anj9iAJ4/YiQAujI4FDYyEhQ0MBouAABARD/eAGwBfgAAwAAATMRIwEQoKAF+PmAAAIDSP84B7AGIAAZ",
    "ACkAAAEhFSECByEVIxUjAgEnABMhJxMXBgczNhMhATMRFDMyNjcXAgcGIyImNQPoA6D+uBAYAWj4kHj+QHgBaJj+uDCQmDhA8CAQ/kgCAKAoQCgIkBAoIKiIQAYgmP7Q0JgI/ej+aIgBWAHQkAGwIMDAyAE4/ND9",
    "6EhI+Cj+0Eg4SGgAAQCA/0gHWAOoABIAAAEXBAUVIRUhESMRIQIDJxIRESQFaFj+aP3oBUj+EKD9QCjoePACSAOoiGgQqJj94AIg/uj/AHABAAEgAVAIAAUAeAI4B5gGgAAXAB0AOwA/AEMAAAEXByEVIwIHFhcH",
    "JicGByc2NyYnBgcnNhcWFzY3ISUhNTMVIRUhFSERIRYXByYnFSMRBgcnNjcjESE1IRMzNSMhFTM1BRCQMAH4cDCAiMhguJiAyGDAgGhIKChgoFhYaGgo/tD7aAGYkAGQ/nABSP7wiHBYaHCQiOBYuKD4AWD+aMjQ",
    "0AFguAaAIKiI/uCIcFiAYIB4UIBAcGiAODBw2FiYeIjA2HBweHD+eFhocGhQ6AEoqGh4SIgBiHD+gJiYmAAGAHj/QARABnAAEAAWABwAIgA7AEEAABMhETMRIRUhESM1BgcnNjchExYXByYnJRcGByc2ERYXByYn",
    "ASE2NxcHIRUGBxYXByYnBgUnNjcmJzY3IyEGBxc2N5ABoJABgP6AkIi4aMiY/qjAQCiAKDgCyHhIUGhQWDh4MFj9kAE4IBiYMAFoYIiIcGBoqKj+6DDQmICYYEjoAZA4QMB4SAUgAVD+sIj+kPjAeIBoyAG4YHhA",
    "eGg4OIhIYEj+YGBoSHBg/nBAQBBwiNCQUEiQWGCQWIhAaEhIgHhoUGCAmAAEAlj/SAVQBnAAGQAqAC4AMgAAASEmJzcWFyEVIQYHNjcnNxYXBycGByc2NyMBERQGIyInJxYzMjU1IREjERchNSERITUhAlgBOBgo",
    "mDAYASD+eDhIeIhAcGA4gCDQ6ChYQNACqFhgOFAgaDgw/siQkAE4/sgBOP7IBbBQQDBYaIiYeAgoiDCoyDhoOBCIaMD9+PzwYGAYmBhQeP6YA9j4eP6IiAAEAqD/MAd4BkAAJAAoACwAMAAAASE1ITUhNSE1IREh",
    "ESEVIRUhFSEVIQIHJCUnNxYXByYnBAUnNgEzESMBMxEjATMRIwQI/pgCEP5oAZj+SAQY/kAByP44Aij9OHiIASgBSIiIyIigKDD+YP4oKLACUKCg/bCYmAEomJgBeJiQkLgCWP2ouJCQmP74gBhAqEDA8FBQSFAY",
    "gJAEAAFI/rgBSP64AUgAAgNo/zgHoAZQACAAJQAAASMRIxEhAgYjIicnFjMyNhMhESECAxYXByYnBgcnNjcmBTY3IRIEYFigA6gIaHhoeBh4eCgQGP2YA0go0IjAWMiYmNBo4Ii4ASCIKP5oUAMI/EgHAP5YyBiY",
    "GDABEP3g/lD+2IBQqGCYoGiQYJDQUNj4/vAABAGw/0AHQANIABQAKQAvADUAAAEhERQGIyInJxYzMjURBgcnJDcRISUhERQGIyInJxYzMjURBgUnJDcRIQUWFwcmJyUWFwcmJwIAAkhQSFiIIJg4MNDwQAEo2P5Q",
    "AqACoFBIWIggmDgw6P7wQAFI8P34/chwWGBYaAMQeGBgYHADSPygUFgQkBAwAQCYeIiImAEgkPygUFgYkBgwAQCQeIiAmAEgKFBocHBQaFhocHhQAAIAaP9IA/AGSAAPABQAAAEXBAUVIREhAgMnNhIRESQBIREh",
    "FAOgUP74/qgCGP3YCIiIQEgBqP7wAYD+iAZIiFAw4P2Q/mD++HCAAagCIAHAKPygAUCwAAkAgP9ABSgESAATABcAGwAfACMAJwArADEANwAAEyERIxUzFSMVIRUhNSE1IzUzNSMTITUhIRUhNQEhNSEhFSE1AzUh",
    "FRUhNSEHFwYHJzYlFhcHJifQA+jQ+PgBQPtYASDg4NCQASj+2AGwARj9OAEo/tgBsAEY0P7YASj+2ChwuMho6AIAoIhYkJgESP3oaIBQeHhQgGgBQGBgYP7YWFhY/shoaNBQ6ECQUGBYYEBYcGhIAAQAaAFwB5AG",
    "iAAwADQAOAA8AAABFSESFzY3FwIHFhYzMjY1FwYGIyInBgcnNjcmAyEREAcnNhERITQnMxYVMyYnNxYXASEVIRchESE3ITUhB2D9+ChIiEiIgJBYMCAgIJgIcGBomFBoiIhogDD82JiQkAOwCKAI+DBAaHBQ+tgC",
    "2P0oKAJ4/YiQAVj+qAXQkP7QsMi4KP7g0HAwkJAo8LDIcGhogID4AXD+iP7I8Fj4ASgBuFhQWFA4MFBYYP7wiHj+UIigAAUAUAIABxAGeAAWABoAHgAiACYAABMhNTMVIRUhFRYXByYnESMRBgcnJBMhASERIRMh",
    "NSERITUhESE1IYgBYJABOP7ImJB4UGCQeLhoAQiA/rADeAMQ/PCQAej+GAHo/hgB6P4YBZDo6JBImLh4iID+CAII2LCA4AEgASj78ALYqP4wqP44oAADAZgCQAZoBoAACQANABMAAAEXBgchESERITYBIREhExYX",
    "ByYnBSi4aHgBaPswArCA/WgDoPxgYHhQmEh4BoA4yJD9UAKwwP0gAZACGHiIWIB4AAIAiAI4B4AGeAAVABsAABMhNjcXFAchFSESBQckAyMCBSckEyEBFhcHJifwApAYCJgYAxD9sNgByED98PhAsP2gYAIYsP2g",
    "AsCokHCQoAVoeJgQiHiY/oB4oJgCAP34iJB4AYj+uFBgiHhYAAEA0AIwBxAGmAAfAAABFwchEAIjIicnFjMyNhMjAgEnABMjAgEnJBMjBgcnJAJgoEAEUHCoUHAgeFBQMBD4WP5wgAFgYOho/jCAAaBo4HiQgAEQ",
    "BpggmP1Q/wAYoBiQAej+SP6wgAEgAWj+cP7YgPgBQKBweMAABAIg/1gFeAZ4AAsAOwBBAEcAAAEzFTMRMxEzNTMRIQchFSEGBzI3NjcXBgc2NyYnNxYXByYnBgcRFAYjIicnFjMyNREGByc2NwYHJzY3IwEWFwcm",
    "JyUXBgcnNgJ4mHiQeJj9UAgCwP6wUHBwWDhAgMD4yJgQGHBgSIAQGFhYSHBAOBhISCiYqCigmGh4GIhY2AJYOChwKDj+UHhASHhYBhDwAVj+qPj+eHCIkFgQMEAwyIgYICAgMHiYODgwGAj+oFhIEIAQOAEwGBBw",
    "WHAQCHBgkP1oUGgwaFAoKKhwQIgAAwH4/2gFYAZwAAsADwAfAAABMxEzETMRMxEzESEHIRUhBRE3FwYHJxEjFRADJzYRNQJgkGigYJD9eCgCeP2IAkCAaGCocKDQgLAF6P6IAgD+AAF4/fhokHD+AIBgeHhoAdhA",
    "/tj+6GDQARDQAAECwABoBNAGeAAQAAABMxEzFSMRNjcXBgcnESM1MwNImPDwWFhAgKhgiIgGeP3QkP2QUGiIkIBoAuiQAAMAiP9AB5gDaAAaACAAJgAAATM3Ehc2NxcGBxYFBwADERQGIyInJxYzMjY1ARYXByYn",
    "BRcEBSckA6CQGHioqGCIeLCwARiA/iD4UHhoWCBoYCAg/jCAUJBIgAH4IP6Y/uBQAbgDWBD/ALB4gGiIcJiAoAEQAZj90HhYGJgYIEACiHCAWIB4uJjweKigAAIBOALQB1gGQAASABYAAAERIRUUFiEgNzY3FwYG",
    "ISAmNREXFSE1BpD7SJgBwAIgOCAYmCiA/YD92NCgBCAGQP34iCggGAiQWKhIUGACwJjQ0AABA1gA+AdoBnAAFAAAARcGBxEhFSERIRUhETMRMxEGByckBvBwsNABQP7AAYj8SKD4yOBIAkAGcIAwKP5omP4omAO4",
    "/OAD8CAYmDgAAgFw/0AHoAT4ABYANAAAARcGBxEhFSERIRUhNSERITUhEQYHJyQBFhc2NyEnASE1IRUBIQIHFgUhByEgJwYHJzY3JicGuHCAqAGA/oABUPzoATD+sAFQcIBAAXD8qDA4SCD+4BABGP7AAfj++AEQ",
    "GIiQAfAB+Dj+QP3owHCQYJBgYDAE+HgoIP7QiP7AiIgBQIgBGBgQkCD9cJhogNB4ATiQiP7A/pjggAiYqIBgiFhwiMgABAGI/0AHoAUQAA8AEwAlACoAAAEhNTMVITUzFSEVIREhESEFNSEVASEVBgUWBQckJQQF",
    "JyQ3JicjIRYXNjcB4AEwmAHomAEw/tD86P7QA7D+GP6IBKiI/wDYAXgw/jj+6P7Y/oBgAWj4uJhoATCYqNCABHiYmJiYiP7AAUC4uLj+8HjIkFgQoBCYeECQMFh40KhQaJAAAgI4/zgHaATwAA8AEwAAATMVIRUh",
    "ESERIzUhFSMRIQEhESEECKACwP1AAmig/GigAdD+0AOY/GgE8PiY/wD82HBwAyj94AGIAAMB+P+gB5gESAAFAA8AFQAAARITBwIDASESExcCAyEVIRMSEwcCAwSAkDCwKIj+GANAwIiogLgBqPpg8KBQoFCgBEj+",
    "uP64MAFoATD8GAHIAig4/fD+WJgEEP7Y/pA4AXABMAABAgD/SAdwBQgAIgAAASE2NxcGByEVIQYHITUzFSEVIRUhFSERIxEhNSE1ISc2NyECGAF4ODCYICgC8Py4cJABoJgB0P4wAkj9uJj9cAKQ/aAgoID+6ARI",
    "YGAgWEiQsIjo6JDomP7YASiY6JiAsAABAhD/SAdQBLAAJQAAASEVBgUWFyEVBgcnNjchERQGIyInJxYzMjURITUhJic3Fhc2NyECaARoyP8AGBACIEBYqFAw/lBYeHhoIHB4SP3QAlB4kHBYWLig/JgEsJCwgBAY",
    "iLCgMJCI/eh4YBioIGAB8JBYWFA4MFBoAAMAYABoB8AFKAAYABwAIAAAASERIQchFSEWBQckJyEGBSckNyE1ITY3IRMhNSERITUhAZAE4P0YQAQ4/liwATh4/pjQ/cDY/rhQAUhg/ngCEDAg/rCYA7D8UAOw/FAF",
    "KP24YIiAeJC40OCweLhgiDAwAWBg/shgAAMAWP94A/AEeAATABcAGwAAEzM1MxUhNTMVMxUjESM1IRUjESMBIREhESERIViYkAF4kGhokP6IkJgBKAF4/ogBeP6IA9CgoKiomPxAeHgDwP7wARD9UAEQAAYAaP9A",
    "BygEMAARABUAGgAuADIANwAAAREUBgcFJzc2NTUhAgcnEhEREyE1IREhNSEVAREUBiMiJycWMzI1NSECBycSERETITUhESE1IRUDmEA4/wAg4CD+gChoiJCQAXj+iAF4/ogFoFhYWHgogFg4/kAggIiokAGw/lAB",
    "sP5QBDD8CFhwEAigCBBYsP74yFABMAFYAhD+sLD+GKh4Alj8CHBwCKAIcLD++NBQATgBUAIY/rCw/hiogAADAdD/SAdQBIAAMgA2ADoAAAEXBAUVIREhFSERFAYjIicnFjMyNREhFTcnNxYXByYnBAUnJTUhESMR",
    "ITUhESE1BCEnIAEhNSEhFSE1BvhA/uj+qAIo/dgCiIB4UGggiEhg/hjYKGhgQHgQGP6Y/kgYAYj+OJgCYP3wAhD++P7YKAKQ/lABeP6IAhABkASAeBAIaP6IcP5QUFgIiAhIARCQGDAwYIA4KCAwIIgYmP4gAlhw",
    "AXhgCHj+MIiIiAACAeD/OAdwBIgAEwAXAAABIREzESEVIRUhESM1IRUjESE1IRMhESEB4AJQmAKo/VgCOJj8UJgCEP2w2AOw/FADSAFA/sCQ6P1oYGACmOj9cAEYAAICEP8wB3gDkAADABkAAAEhFSEBITUhFSEC",
    "ByQlJic3FhcHJicEBSc2ArAEGPvoARj+SAVo/RCYqAFgAXBYaIj4oJgoOP4I/dAw8AOQmP6YmJj+8IAQMGBgUND4WEhIUBiQmAADAVj/SAdgA5AADQARABUAAAEhEAIjIicnFjMyNhMhFyERITchESEBWAYIcKBw",
    "oCCoeEA4EPqQ4AN4/IiYAkj9uAOQ/OD+2BCYEKgCgJj94JABAAABAcD/aAeoBAgAJgAAARcEBRUlFwUVJRcFFRQWMyA2NxcGBwYhIiY1NQUnJTUFJyU1BSckBohI/uD+wAKAEP1wAugQ/QhQiAFQaBCYGFhQ/mD4",
    "eP4AGAIY/mAYAbj+cDgCeAQIgCggiECQQKBYkFjAICBQiCjASDhIYNBAkEigMJAwiCCIMAACATACqAdIBjgAEwAXAAABESEVFBYhIDc2NxcGBwYhICY1ERcVITUGgPtQmAHAAiAwIBiYIFg4/ZD90MigBBAGOP3w",
    "mDAgGBCQWKgwIFBoAtiY4OAABABw/0AHqATYABcAGwAjADQAAAEhNTMVITUzFSEVIRUhESMRIREjESE1IQUhNSETMxAABSckADczERQWMzI2NxcGBwYhIiY1AUABaKABcKABcP6QAQig/ICgAQj+mAIIAXD+kDig",
    "/oj+CEAB4AEw2JhgaPhQEJgYUED+uPhoBECYmJiYkKj9oAHQ/jACYKioqP54/pj+qCiYKAEIIP7gICBQmDDIQDBAUAABAID/QAeABJgAMwAAASEVIQcWFyQ3FwYHEgUHJAMHFhUUBiMiJycWMzI2NTUABSckASYn",
    "AAUnJCUmJwQFJyQlIQFwBSD9wGiYOAEAyHCIiIABIHD+2JB4IJCIaMAouJgwOP6I/fhQAjABgBAY/qD+UFAByAFIKDD+6P7waAFoASj+EASYkEiIqGiogGBI/qjAkOABgDBwiODoGLAgkJBY/uiYmJgBKFAw/vhw",
    "iIjoMDCYUJBQqAACAJD/SAd4BQAAIwAnAAABITUzFSEVIRUhFSEVIRUhFSERIzUhFSMRITUhNSE1ITUhNSETITUhAXgCOKACOP3IAmj9mAMo/NgCQJD7+KACWPzgAyD9oAJg/ciABAj7+ASYaGiIcIh4iHj9sFBY",
    "Alh4iHiIcPwg4AAFAVD/UAbIBPgACwAPABMAFwAbAAABITUzFSERIREjESETITUhIRUhNRE1IRUjNSEVAVACaKACcP2QoP2YkAHY/igCeAHY/iig/igEGODg/Lj+gAGAAfDAwMD96MjIyMgAAgBo/2AHeAUAAAUA",
    "MQAAARYXByYnBSE2NxcGByEVIRE2NxcCBRUUFjMyNzY3FwYGISImNQYHJzY3ESMCAScAEyEFMHBIiEBw/CgCCCAIqBAYA8D9WNCQoMD+wEiY+CgwCKAQkP6o+IiQsGD4qJiQ/fhoAciI/iAFAGhoUGho+JCgEJiI",
    "mP4QmPA4/rDQKBggICjAMPh4SFhIQJBYWAJg/bj+iIgBQAH4AAQAiP9IB4gE0AATABkAHwAkAAATITY1NhEzEAcUByEVIQIFJyQ3IQEWFwcmJwcWFwcmJwEEFwcBiAOQSAioCDACmP0Y2P2AWAH44PzYAcjgwHC4",
    "2GDguHC40ARAASjwaP3oAeCYwBABiP5IEKiAoP6wqJiA4ANIaIh4iGCQaIh4iGD+EKCQgAE4AAMBgP9IBrAEkAALAA8AEwAAAREhFSERIzUhFSMREyE1IREhESEGOPvgBJiY/ACYmAOQ/HAEAPwABJD+ALj9eGBo",
    "BUj+kOD8QAEIAAIAgP9IB4gEcAAVABsAABMhETMRIRUhERQGIyInJxYzMjY1ESEFFhcHJieABIigAeD+IFBwmIggkJggGPt4AdiIYKhQiANwAQD/AJj9SHhgGKggKDgCkHi44FDYyAABAGj/SAeYA7gAGwAAASEV",
    "BgUVIRUhERQGIyInJxYzMjURITUhNTY3IQG4BHjY/wADQPzAaGhwaBhYcGD8qANY0KD8iAO4oIB4OJj+kEhQGJgYIAFQmIhgWAABAIj/QAd4BHAAGwAAASEVBgUVIRUhERQGIyInJxYzMjURITUhNTY3IQGQBMjo",
    "/ugDIPzgcGiwqBiQuEj86AMY8MD8QARwqKiQSKD+MEhQIJggIAGwoKB4eAAFASgBsAb4BpAADQAeACQAKgAwAAABFwYHIREjESERIxEhNgEhETMRIRUhESMRBgcnNjchARcGByc2JRYXByYnARYXByYnA7iwGCAC",
    "yKD7cKACUDj+SAHAoAG4/kiggOBo4Gj+wANIeEhIaFD90EgwgChIArCIgHBwmAaQKDg4+7gDuPxIBEh4/agBIP7giP6gASi4gHCAgAGYSGhAWEhQUFhIUFD+mGCAcICAAAEAiP9AB4AEmAAiAAABFSEVIRUhFSEV",
    "IRUhFSEGByQlJic3FhcHJwQFJzY3ITUhEQaA/AADwPxAA8D8QAUA+4hwYAGoAcA4SIj4mJhw/bj9cCigeP5AAWgEmJB4gIiAeJCwUAgwMDBYoLhYgEgYiGiwkAMIAAQAYP9IB4gE4AAKACIAKQAvAAABFwYHESMR",
    "BgcnAAEXByEVFAIHBAUHJCcGBSc2NyYnBgcnAAE2EyEGBxYTFhcHJicCGJhIYKBYYFABMAJwoCgCkOCwAQgBCFj+0PjY/wBY+LCwiDg4aAEIAYDoeP3gQEiIaHBgYGhwBOAwyMD8KALAgGigAXgBoCh4cDD96LCo",
    "UJhwsMBgoFCYmLhIOHABKP4A+AGAmHDYAXhQaIB4WAAEAID/eAeIBRAAJwArAC8APwAAASE1MxUhNTMVIRUhFSEVIRUhFSEWBQckASEGBSckNyE1ITUhNSE1IQUhNSERITUhAyE1MxUhFSEVIRUhNSE1IQF4ASiQ",
    "AZCYASj+2AFA/sAB8P4Q8AFAWP5w/vD+uNj+aFgBWKj+OAHo/tgBKP7YAbgBkP5wAZD+cOgBYJABYP6gAuj52AKw/qAEqGhoaGiIeIh4kLhImIABGPigiICQkHiIeHh4/oh4/gigoIiYkJCYAAIAmAJIB4AGIAAR",
    "ABYAAAEhFQIFBAUHJCUEBSckJSYDIyEWFyQ3AVAFMLD+4AEgAbBA/iD+qP6w/khoAagBMNigqAFYmNABGJAGIJj+6LiASKhA0LBQkEiQsAEY6JCwyAADAYAAYAaIBXgAPQBCAEgAAAEXBgchFSEHIRUjFhcHJicU",
    "BiMiJycWMzI2NyERFBYzIDY3FwYGISAmNREGByc2NyE1ITchNSE2NxcGBzM2ASEnIQYDFhcHJicFCJgwSAEI/bgwArDgWKhweFhQaFBgGGBgIBAI/ngwwAEAOBCYIHD+sP7YWGBwWLh4/vABeDj+iAGoKBiQGCBo",
    "YP44AiBI/oAokDg4cDBABWAwaFiIYIhwYIBgcOBwGHgYKFD+6CAQMGg4kEg4WAEwWEiAeIiIYIh4kBiAcHD9uGg4ApA4UFhIQAACAXgBCAZABegABwAWAAABMxACByc2EgEVBiMiJyY1ETMRFBYzMgLAmLjYULCY",
    "A4BIUMgoQJgwaFAF6P2Y/hiQkIABqP5okBAgKGgDsPxwICAACAJA/0gHsAZ4ABIAKABKAFAAVABYAF4AYgAAATMRNxEzFTMVIxU2NxcEBSc2NwEzFTY3FwYHFRQWMzI2NxcGBiMiJjUFFwchFQYHIREUBiMiJycX",
    "MjU1IRUjNSEGByc2ETUGByckFyE2NyEGAyE1ISEVITUBITUhFRQlFSE1AtCIeIjQ0HBYEP7Y/pggMCACkJComFjA2CBYeDgQiCBgyKhg/rh4IAHwKCgBOFBIYJgg8Cj+sJj+wCC4cNg4MFgBKDgBqCgg/nA4OAEg",
    "/uABuAFQ/PABKP7gAbgBUAX4/nAgAfCwiJggIIBoQIAICAIo8EBYeGBIeCAQQHA4oGBIWGhIMGBIKP0oUFAQiAgoYPDwmIBwkAE4wDAYcMBoMDhI/uh4eHj+kIgoGECIiAACAoj/QAcwAkgABwALAAABESM1IRUj",
    "ERMhESEHMKD8mKCgA2j8mAJI/QCAiAMI/hgBWAAFAZD/SAeIBYgAFQAZAB0AIwApAAABITY3FwchESERFAYjIicnFjMyNREhEyE1IREhNSETFwIHJzYlFhcHJicCSAGIKBCYMAKA/hBQaIBwIHiAMP3okAOA/IAD",
    "gPyAMICo4HDwA6C4sJCYyATYWFgoiPz4/kh4WCCgKGABkAHQqP4YuP6AWP7YqHjIwJDQcMC4AAQBsP9IB6AFUAADAAcACwAnAAABIREhEyE1IREhNSEDIRUGBRUhFSEVFAYjIicnFjMyNTUhNSE1NjchAigE0Psw",
    "mAOY/GgDmPxomATY6P7gAqj9WHBweHAYYHhg/WACoLiY/IgFUP2IAYBo/qhw/qCgWEgwkKhASCiIKBiQkIAwMAACAZj/mAdYBQgADwAVAAABMxEhFSERIRUhNSERITUhARYXByYnBBigAhD98AKg+kACgP4QAfAB",
    "0KBgiGCYBQj+aJj9WJiYAqiY/vCgwFC4qAABAej/QAcIBTAAHQAAASE2NzMGByEQAgYjIicnFjMyNzYRIQICByc2EhMhAlgBgBAIoAgQApAweIBoYCh4eFAQIP4IKOjwgNjgKP6QA+iYsLCY/XD+aIAgoCBoqAJg",
    "/oD+OLBwkAGgAVgAAQII/2AHKAJwAB0AAAEhERQWISA2NxcGBwYhICY1ESERFAYjIicnFjMyNQU4/XBYAVgBuGgQoChYQP3w/jiIA9BgYFiIIJBYOAHY/mAoGFioOOhAOEhwAlj+0GhoGJgYaAABAMgAAAPgBoAA",
    "EAAAARcGBREhFSERJCUXBAUnESQDqDjw/ngCOP3IAQgBEDj+yP6QSAGIBoCYQED+MJj9uEBgiHBgUAWgMAABAIgCOANgBnAAHgAAEyE1MxUhFSEVNxcGBxUUBiMiJycWMzI1NQUnNjc1IZABKKABCP748BiAiFB4",
    "YFggYGBA/wAwoJD+2AWY2NiYwDiAKBi4cFgokChYcDCQGCDYAAIBgACIBoAGKAAlACsAAAEhFQYFFTY3FwYFFQQXByYnERQGIyInJxYzMjURBAcnJDcRNjchExYXByYnAZAE8PD+4OioYND+4AEw2GDQ2FhQYGAQ",
    "SGAw/uDgUAFw4Oi4/CB4wJhooLAGKKiYiNBQiICQcCCgmICgeP74SFAIoBAgATjYcKCosAGQcGj+6HiggLCAAAECoAKwB3AGUAAWAAABFwYHFSEVIRUhFSE1ITUhNSE1BgcnIAawUMjoAiD94AHw+8ABsP3wAhC4",
    "0DAB4AZQiCgY2JDgkJDgkNAQCJAAAgCI/1gG+AUwABMAFwAAAQchAgIjIicnFjMyNhMhExcHIRUBIRUhAnAgBKgooNCAwCDoeGhgEPtgaKggBAj5+AUg+uADyOj9iP7wIKAo0AGIAugQwJj90JgABQKo/0gHaAZ4",
    "ABEAFwAbAB8AMQAAATMRMzY3FwYHIREjESERIxEhARYXByYnEyEVIQchFSEFFwYHJCUmJzcWFwcmJwQFJzYEwJhQcEioQGgBCJj8aJACGP7QYECQOGCIAvD9EMgEiPt4AWCgYHgBCAEQOECIsHiYIDD+eP5IMMAG",
    "eP5okNA4qID+QAEw/sgByAFYeIhIiHj9oJDIkCAwwHgQOFhYUNjwWFBQUBiIgAACAjj/QAegBngACgAnAAABBgcnABMXBgchFQUzFAchAgcGIyInJxYzMjc2ESECAAUnJBMhNSE2A8hokHgBGHiYKEADiPy4oAgC",
    "aAhAQLhokBigaEgYOP5AIP7o/uBYAeAw/qABaAgE0LCIaAEgAVgweGiYeJiA/SCQeBiYIFC4Abj+sP5ogJDYAgCYeAABAFj/UAPABoAADgAAATMRFAcWFwcmJwIDJwARAfCgIMCQYHCgePiIAZgGgP4Y2MiQsJCY",
    "iP4o/uBwAfgC4AAEAHD/SAeQBQAAAwAHAA8AKQAAASERITchNSEBESM1IREjEQERFBYzMjY3FwYGISImNREhFRQGBSckNjU1AaAEyPs4kAOg/GAFAJD6yJgEqDBYoEgQmAiQ/wDAWP4w8P6wYAFIuAUA/oCIcP6g",
    "/oDw/wABkP7w/kgoIECIOLB4SHABUEDg2DiYMKCwqAAFAuD/QAdwBngACgAQABgAHAAgAAABFwYHIRUhBgcnAAUWFwcmJwMVIxEhESM1ASMRMyERIREEaKAgOALA/Ph4mHgBEAGIeEiYSHDYoAPQoP5g8PABoP8A",
    "BnggkICY6JhwATBgeIhYiHj76LADoPxQwAJY/kABwP5AAAIAiP9AB6gC8AAfACUAABMhFSEHIREUMzMyNzcXBgYHIyImNREhAzY3FwQHJxMhARYXByYniAbw+0AoA2BQOGggCKAQcIhgkGD9GGjQ0Bj+yPBAyP5w",
    "A1iQeGB4iALwiJD+cGCAcDDAgAhgiAEA/pgoQIhgIHACuP6wSGBwaEgABQMA/0gHuAY4ABkAHQAhACUAKQAAASERIRUhFSESBQckAxEjEQIFJyQTITUhNSETMzUjIRUzNQEzNSMhFTM1A5ADmP6AAdj+oJgBAFD+",
    "8LCQoP7oYAEIoP6IAej+eJjw8AGA6P2Y8PABgOgGOPzokJD+wKCYuAGA/YgCcP6g2IjAATiQkAHIyMjI/fjAwMAAAwN4/3AHmAYgAA0AEQAVAAABIQMzFSE1MxMjNTMTIwEhEyEDIRMhA9ADeFio++CwOMDQONgB",
    "QAFwKP6YeAGIKP6IBiD56JiYAqCYAkj9uAJI+oACoAADA3j/SAeQBoAAEQAZAB0AAAEXAgckJSYnNxITByYnBAUnNgERIzUhFSMREyERIQUAoLCoARABIEhQiLB4kCAo/pD+YDDoAsCY/eCYmAIg/eAGgDD+QKgQ",
    "OIh4QP8A/tBAWFhQGJDg/dD8wICAA0D90AGgAAIDEP9AB6gGaAAWABwAAAEzESEVIRIFBwADIxE2NxcGBycRIzUzARcCByc2A8igAwj+WIABYFD+YIjIgIBAqNBouLgCiIjIyHjoBmj9MJj9+NCYAQgCaP0AUFiA",
    "eHBoA1iYAqBQ/rDAaPAABgNA/1AHmAaQAAUAJgAqAC4AMgA2AAABFhcHJicFIREzESEVIRUhERQGIyInJxYzMjU1IREjESERIxEhNSETITUhIRUhNQEhNSEhFSE1BpBoQHhAYP0gAeCQAej+GAGwaHAwOCBYKEj+",
    "6JD+8JgBqP4g0AEQ/vABoAEY/UgBEP7wAaABGAaQWGBIYFDQAQj++JCY+8BYWAiQCEjI/lgBqP5YBPiY/gDY2Nj9yNjY2AADA2j/SAeYBngADwAXABsAAAEhETMRIRUhESEVITUhESEBESM1IRUjERMhESEDaAHA",
    "oAHQ/jABiPxgAXj+QAPQmP3YmJgCKP3YBXABCP74mP7omJgBGP2I/OiIiAMY/ggBYAACBQD/SAcwBngADAAQAAABMxEUBiMiJycWMzI1ATMRIwaQoGCQcFggcHhQ/nCgoAZ4+aB4WBigGEgFcPt4AAIAYP9wBIgG",
    "IAAVACYAABMhFSECBzY3Jic3FhMHJicEBSc2EyEBFwQFJyURITUhNTMVIRUhEYAD8P4giIDg8DhAkJhgoBgg/rD+iDC4iP6oA+gg/kD92EABuP6IAXigAYD+gAYgmP64kBg4eGhA8P7oSFBQUBiYqAFA+xiQWEio",
    "MAEYkPDwkP8AAAMC8P9AB5gGeAANACYALQAAARYXIREjNSEVIxEhJicTFwYHIRUjAgcWFwcmJwYFJyQ3JRMjNSE2EzYTIQYHFgVgOCABwJj8+JgB0BgwCKAwMAJ4wDiA0LhokPjo/nhIAVjI/pCI+AE4QOBwKP64",
    "MECYBnh4mP6wwMABUHho/lAQqIiQ/tC4gJCQiJjIWJhIoNABOJCo/TCYAQCQaFAABgIY/0AHcAaAAA8AEwAsADAANAA4AAABJic3FhchESEREAMnEhEREyE1IQERFAYjIicnFjMyNREjESMRIxEjESMRIxETMzUj",
    "IRUzNTMVMzUEuCg4oEAoAfj8ALiIoKADaPyYBBhgYDhAIGAwMIiAkICQkJCQkAEQkICIBahYUDBgeP4Q/uj+QP5oaAFIAagDCP6g0P4A/OBYWBCICEABCP7oARj+6AEY/iAD2P6Q4ODg4OAABgKw/0AHeAaAAA4A",
    "EgArAC8AMwA3AAABJzcWFyERIREQAycSERETITUhAREUBiMiJycWMzI1ESMRIxEjESMRIxEjERMzNSMzFTM1MxUzNQUAQJgwIAG4/ICwgJiYAuj9GAOYWFgwOCBYKChwgGiIaJCQaGjwaIBwBaioMGB4/hD+6P5I",
    "/mhgAUABsAMI/qDQ/gD82FBYEIgQSAEI/ugBGP7oARj+IAPY/pDg4ODg4AABADj/SAK4BngAFgAAEzMRMxEzFSMVFhcHJicRIxECBycSEyNw6IiwsIBYYDhAiEhgeLBAuAUAAXj+iJCImJiIeGj8OAPg/tioeAEo",
    "AXgAAwK4/1AHsAZ4ABYAHAAiAAABETMVIRIFByQDAgUnABMhNTMRIREzEQEzNjURIyERFAchEQcgeP4IyAFIWP7A2Jj+kIABmHD+KHgBkJj+cOgQ+AGQCAEIBTj9kJD+eMCg2AGY/oDwaAEQAXCQAnABQP7A/ZBI",
    "SAFQ/rBISAHgAAEDSP9IB5AGYAAUAAABFwQFESEVIREjESEVEAEnNhI1ESQHAGD+4P6AAtD++JD+yP74cIBgAagGYIhgEP6gkPvQBDCI/gj+WGjoAXDgAvgQAAECgP9AB5AGeAAhAAABFhchFSEUByECAiMiJycW",
    "MzI3NhEhAgIHJzYSEyM1ISYnBXBYKAGg/VAIAnAIgLhokBCYaEgYMP5AINjocMD4COgB8DBIBniYwJiQePzo/ugYqBho8AGg/qj+WLCIgAG4AoiYoIgAAgBoA/gHkAaIAA8AHwAAARcHIRUhFhcHJicjBgcnNgEX",
    "ByEVIRYXByYnIwYHJzYBwJhAAfD+4EhAoEBgYHBwiPADkJgwAkD+qEg4kEhYeDhQgKAGiDCYkGBwWJiQ0Gho+AEoMJCQYGBYkIh4YGDQAAIAaAQoB5AGiAAOAB8AAAEXByEVIRcHJicjAgcnNgEXBgchFSEWFwcm",
    "JyMGByc2AcCYQAHw/uiAoEBYaLgoiPADoJgYIAI4/rBAOJBAWIhIiIjoBogwgJiwWIiA/vAIaOABGDBAQJhQWFiIeJCAaOAABgLY/0gHkAZ4ABMAGwAfACMAJwArAAABIREzESERMxEhFSEVIzUhFSM1IQERIzUh",
    "FSMREyERISERIREBIREhASERIQLYAQiYAYCYAQD/AJj+gJj++ARomP0omJgBKP7YAbgBIP0oASj+2AG4ASD+4AV4AQD/AAEA/wCQ8PDw8P64+6hwcARY/lABIP7gASD9OAEg/uABIAAEAGj/SAQ4BjgAEQAVABkA",
    "HQAAEyEVIxE3FwYHESMRBAUnNxEjASERIREhESERJREhgAOIYHgYSEig/tD+sCCQeAEYAXD+kAFw/pABcP6QBjiY+9gQkBAI/mgBgDAooBAEgP8AAQD9cAEA/SAwASAABABg/0gD0AYwABAAFAAYABwAABMhFSMR",
    "NxcHESMRBAUnNxEjASERIREhESERJREhaANgmIgYoJD/AP7gIIB4ARABKP7YASj+2AEo/tgGMJD72BiQIP5oAXgwIKAQBID/AAEA/XABAP0gMAEgAAIAWP9ABwgGgAAQABQAAAEVEAIHJwARESEmJzcWFyERAyER",
    "IQIQoKhwARgCgBgomDAYAnig+6gEWAMwQP6o/lCoiAEIAmgCaGBIOGh4/ZAB2P7AAAIAYAJoB5gGOAAOABQAABMhFSEGBxEjEQAFJyQBIQUEBQckJbAGoP0YEBig/tj+WHACKAEg/QgEeAFoAQiA/vj+oAY4mCAY",
    "/QACUP7wsIjgAUB4yOCA+NAAAwBoAtAHMAaAABoAHgAiAAATITY1MxQHIRAGIyInJxYzMjYTIQYCByckEyElIREhNyERIaABGAiYCAGwcJhQcCB4UFAoEP7gEKi4cAEwGP7wA/gCmP1ooAFg/qAF4EhYWEj96Ngg",
    "kBiIATjo/uh4cLgBUJj9UJABiAADAHACOAeIBoAAGAAfADgAAAEXByEVFAIHFhcHJicGBSc2NyYnNjchNSETNjchBgcWARYXNjchNSEVFAIHBxYXByYnBgcnNjcmJwIAoEABkIhggHBgaKDI/tgo8JCIqGBI/wAB",
    "SMCIQP7YQEBwAshQmJBQ/aADCIBAUHjgSPCQkLBouICIaAaAEKiIIP7YaEhIkFhYoDCQIHBIUJiQmP4YkMCIYDgBUMC4qOiQeCD+4GhoaECgUICAQJg4aJDYAAQCoP9IB5gGeAAnACsALwBOAAABMzUzFSERMxUj",
    "ESEVIRUhFSEVIRUjNSE1ITUjNTM1IzUzNSE1ITUjIRUzNQMVMzUBFhc2EyMnEyM1IRUCBzMCAxYhIQchICcGByc2NyYDBLjIkAEgaGj+4AEw/tABYP6gkP7wARDg4MjI/uABIMgBWJiYmPywICAoGMgQ2NgBeHBo",
    "yBBoYAGwAZg4/qD+OJBQaFBwSFAoBeCYmP7wiP7wmICQgNDQgJCAmICQiJCQkP7okJD+mKiAqAEAeAHQgHj++Mj+KP7Y4JjgkHB4gKC4ARgABQKo/2AHoAaAAA0AEQAVABsALgAAARcGByERIRUhESERMzYFIRUh",
    "ASE1IQEWFwcmJxMhERYWISEHISImJwYHJic3ESMFkJgYIAEw/fACMP044CABEP6IAXj+iAGY/mj+GIBgYHB4GAEoSNABWAEwSP544OBIWGAwOMCQBoAoaFj+ALj+CASwcPjo/UjoA+hokHiYcP3Q/QhQQKhgcHhw",
    "WEiYAoAAAgMg/0AHsAZ4AAsALAAAARcGByEVISIGByc2EyEVBgcnNyMRIRUhERYzMwcjICQnBgcnNhMXBgcWFxEhBFCQGCAC6PzgCEhYeLAgA1A4SKBo6AF4/oiAsLA4eP7Y/shoQHBo0BiQECBQgP7oBngwWEiQ",
    "oHBg6P7giHh4MLj+qJD+YBigiJCwiIj4AggQ6LCISANQAAMAUP84B5AE0AAfACoASQAAARYXIRUhFAchEAYjIicnFjMyNzYRIwIDJxITIzUhJiclFwchFSEUBgcnNhcXBgchFSEVFSEVIRYFByQnBgUnJDchNSE1",
    "IwYHJzYCIDAYARD+UAgBgGigQEAoWFBIEBjwOKCQ2AiwAUAYIALokCACiP0oWEh4sIiIEBgCQP6IAaD+gFgBQHD+6IBw/tBYAShY/oABsIBAUGigBNBQaJBwaP2A2CCYIEhwAXj+OP8AYAFgAnCQSEAQKGCQCJBA",
    "YLB4KDAoiIgwkMiAiIjo2JiImLCQuFBAaIAAAgCI/0gHeAL4AA8AHwAAATMRIzUhNSE1ITUhNSE1ISUzFSEVIRUhFSEVIRUhFSMC8IiI/ZgCaP3wAhD9oAJgAYiYAlj9qAIA/gACaP2YmAL4/FCYiHiAgICYmIB4",
    "gICImAADA1D/iAeQBjgAAwAHABsAAAEhESE3IREhAyE1ITUhFSEVIRUhFSEVITUhNSEDuAN4/IiYAkj9uKABeP5gA+D+YAFo/pgByPvAAdj+iAY4/ZiQAUj7+PCQkPCQ+JCQ+AACAGD/SAPYBjAACQAeAAABFSER",
    "EAMnEhERAQIGIyInJxYzMjYTIxE2NxcGBScRA9D9sIiYkALYCGhQMDAYODgYEBDQwJgYuP8ASAYwkP1w/ej+UFgBsAHwAvD+yP2AqBCYEFABuPvYSFCQaFhQBRgABQKA/zgHoAZ4ACkATQBVAF0AYwAAAQcnNjcX",
    "BzM1MxUzFSMVMxUjFRQzMjY1FwYGIyImNTUjBgcnNjcjNTM1BSMGByc2NyM1MzUjByc2NxcHMzUzFTMVIxUzFSMVNjcXBgcnBREjESERIxEFFwIABSckEhcWFwcmJwWIIHhAKIAgUICgoNCAGCgYcAg4cFhASBig",
    "aIgIWOD96EAYsGiQGGDYgCCASCh4GFCAoKDIgDAoIGBYOALomP1ooAHIoCj+0P7gQAEI+NjY0Hi48AVYUCCgmCBooKCAcHCoOBhQIIA4OFDI0JBYgIhwcODIkFhomHBwUCCgmCBooKCAcHC4ICBoUCg4UP2QAej+",
    "EAJ4wBD+uP6YSJg4ASBggKhwoKAABQKo/2gHwAZ4ABsAIQAxADcAPQAAASE2NyEGByc2NxcGByEVBgchESE1ITUhNSE1IQEWFwcmJyczERQWMzI2NxcGBiMiJjUBFhcHJiclFwYHJzYDmAHISDD+cGCAaPB4kCAo",
    "AeA4OAEI/GADCP0YAuj9CAGYeGBgYHDYmECAkDgIkBBg8PBoAuiAWIhIgPygkBhQkFgEqFBgYFBomNAoQDh4aFD9KIiwgJj9cFBgeHhQQP7AKBgocDCgUEBYAWCYqFCooDAg4LhQsAAEAfj/WAewBoAACQAPABUA",
    "RQAAASEmJzcWFyEVIQUXBgcnNiUWFwcmJxUWFwcmJwcWFzY3FwYHFhcHJAMGIwYHETY3FwYHJxEGByckEwYHJzYTFwIHNjcmJwJ4AiAgMKg4KAIQ+xgBGICQ2HDQAyCgoHiQuLCocDAwsDBIiHB4kJCI4FD+OLAQ",
    "GFhYkIAo0LhQmIBgASjogIgo8KCgkJjo+EBIBcBQODhYaJAQSLCocJCgeKCAoKDAiMhwQDggqJBgaHCAWLgooHgCsAh4aP5gMDiAYDhQAXCAQICAASAQCICQASgw/wB4GChIQAADAfj/SAeYBngAJAApAC8AAAEH",
    "IRUCBxYXByYnBgUnJDcmJwIFJwATIScTFwYHITYTFwYHIRUBNjchFgEWFwcmJwTAQAKweKiw2Ej40ND+6FgBELiQcJj+8HABmIj+oDCgmEBIAQg4KJggMAKI/iCQWP4YaAEwgIB4cJAD8OB4/tCwgFCgWKCoUKBI",
    "gJDQ/tD4eAGQAgCQAYggsKjYARAo+Mig/TCQyMgEqHCYeJiYAAgCqP84B4gGQAALAA8AEwAXABsAIwArADEAAAEzEyEDMxUjAyETIyU3IwclBzM3ATcjByEzNyMBESMRIREjEQUXAgAFJyQABRYXByYnAtCYIAOY",
    "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",
    "ACAAVAByAHUAcwB0AGUAZQBzACAAKABoAHQAdABwADoALwAvAHcAZQBuAHEALgBvAHIAZwAvACkAIABhAG4AZAAgAFEAaQBhAG4AcQBpAGEAbgAgAEYAYQBuAGcAVwBlAG4AUQB1AGEAbgBZAGkAIABNAGkAYwBy",
    "AG8AIABIAGUAaQAgAE0AbwBuAG8AUgBlAGcAdQBsAGEAcgBXAGUAbgBRAHUAYQBuAFkAaQAgAC0AIABNAGkAYwByAG8AIABIAGUAaQBWAGUAcgBzAGkAbwBuACAAMAAuADIALgAwAC0AYgBlAHQAYQBXAGUAbgBR",
    "AHUAYQBuAFkAaQBNAGkAYwByAG8ASABlAGkATQBvAG4AbwBEAHIAbwBpAGQAIABpAHMAIABhACAAdAByAGEAZABlAG0AYQByAGsAIABvAGYAIABHAG8AbwBnAGwAZQAgAGEAbgBkACAAbQBhAHkAIABiAGUAIABy",
    "AGUAZwBpAHMAdABlAHIAZQBkACAAaQBuACAAYwBlAHIAdABhAGkAbgAgAGoAdQByAGkAcwBkAGkAYwB0AGkAbwBuAHMALgBBAHMAYwBlAG4AZABlAHIAIABDAG8AcgBwAG8AcgBhAHQAaQBvAG4AVwBlAG4AUQB1",
    "AGEAbgBZAGkAIABNAGkAYwByAG8AIABIAGUAaQAgAGkAcwAgAGEAIABoAHUAbQBhAG4AaQBzAHQAIABzAGEAbgBzACAAcwBlAHIAaQBmACAAdAB5AHAAZQBmAGEAYwBlACAAZABlAHMAaQBnAG4AZQBkACAAZgBv",
    "AHIAIAB1AHMAZQByACAAaQBuAHQAZQByAGYAYQBjAGUAcwAgAGEAbgBkACAAZQBsAGUAYwB0AHIAbwBuAGkAYwAgAGMAbwBtAG0AdQBuAGkAYwBhAHQAaQBvAG4ALgBoAHQAdABwADoALwAvAHcAdwB3AC4AYQBz",
    "AGMAZQBuAGQAZQByAGMAbwByAHAALgBjAG8AbQAvAGgAdAB0AHAAOgAvAC8AdwB3AHcALgBhAHMAYwBlAG4AZABlAHIAYwBvAHIAcAAuAGMAbwBtAC8AdAB5AHAAZQBkAGUAcwBpAGcAbgBlAHIAcwAuAGgAdABt",
    "AGwATABpAGMAZQBuAHMAZQBkACAAdQBuAGQAZQByACAAdABoAGUAIABBAHAAYQBjAGgAZQAgAEwAaQBjAGUAbgBzAGUALAAgAFYAZQByAHMAaQBvAG4AIAAyAC4AMABoAHQAdABwADoALwAvAHcAdwB3AC4AYQBw",
    "AGEAYwBoAGUALgBvAHIAZwAvAGwAaQBjAGUAbgBzAGUAcwAvAEwASQBDAEUATgBTAEUALQAyAC4AMABXAGUAbgBRAHUAYQBuAFkAaQAgAE0AaQBjAHIAbwAgAEgAZQBpAAMAAAAAAAD/AABmAAAAAAAAAAAAAAAA",
    "AAAAAAAAAAAAAAACAAUAAv//AAMAAQAAAAwAAAAAAAAAAgAIAAAA0AABANIBCgABAQwBdAABAXYBfAABAX4CwQABAsMDwgABA8QEnAABCNwJPwABAAEAAAAKAAwADgAAAAAAAAABAAAACgAWABgAAWxhdG4ACAAA",
    "AAAAAAAAAAAAARAABVr3iQAACAD/SPZQEbAAAAABAAAAAAAAAAAAAAAAAAEIAAW4A8AGGAPABhgGCAYIBggGCAYIBggGCAf4BOAEsARQBLAE2AS4BgAGAAZIAAABMAE4BmAGYAZgAuAGYAZgA4AGCAXgBlgGCAYY",
    "BngGeAYwBngGYAYYBjgGeAaABngGeAZ4BnAGiAZoBlAGeAZgBhAGeAZ4BgAGeAZ4BhAGiAZ4BZAGAAYIBggGeAaABmgGgAZQBngGeAZ4BoAGeAaABoAGeAZ4BoAGeAaABngGeAZ4BngGeAZ4BogGgAZ4BngGeAZ4",
    "BoAGeAZ4BngGeAaABngGeAaABngGeAZ4BngGeAZ4BngGiAaABngGiAZ4BngGeAaABngGiAZ4BngGeAZ4BoAGgAZ4BfgGeAZ4BoAGeAZ4BogGWAZwBoAGcAZABogGiAaABmAGIAYwBngGeAZABngGeAaIBoAGgAZ4",
    "BhAGgAZABngGeAYoBhgGEAZwBngGcAZ4BngGgAZwBngGeAZwBngGeAZwBngGgAaQBnAGeAaABogGcAZ4BngGeAaIBngGeAZ4BogGeAY4BngGUAZ4BoAGiAZ4BngGeAYIBoAGAAZ4BngGOAY4BjgGOAY4BngGgAYQ",
    "BjAGEAZ4BnAGOAZ4BngGYAXgBngGCAZ4BhgGCAaABngGMAaABogGkAY4BngGaAZ4BoAGOAaABmgGgAYwBjAGQAZIBkAGkAaABigGiAaQBlgGKAaABoAGgAYwBoAGeAZ4BkAGiAY4BjgGCAY4BjgGOAY4BjgGOAY4",
    "BiAGgAZ4BlgGYAaABlgGgAZ4BngGYAZYBngGeAaIBogGiAaABogGgAZ4BogGgAZ4BnAGgAZ4BngGeAZ4BngGgAaQBngGeAZ4BoAGeAZ4BoAGgAYwBogGgAaIBogGiAaIBpAGiAaIBogGiAaIBogGiAaIBogGiAaI",
    "BogGeAZ4BjgGgAZ4BnAGgAZoBmgGeAZ4BhgGSAZIBkgGSAZIBkgGeAZ4BggGeAYwBpAGIAYIBogGgAZ4BngGeAZ4BfAGKAaIBoAGgAaABoAGgAaABoAGgAYQBnAGeAYgBkAGeAZ4BmgGeAZwBkAGeAaABkgGaAZo",
    "BoAGeAZ4BoAGgAZ4BngGeAZ4BoAGYAZgBngGeAaYBngGeAaABiAGeAaABngGeAaQBngGeAZ4BoAGkAaIBngGeAZ4BoAGgAaABngGgAZ4BngGeAZgBngGgAZ4BngGeAZ4BngGeAaABngGeAZ4BjgGeAZ4BngGeAZ4",
    "BngGgAZ4BngGeAaABoAGeAZ4BngGgAaABngGgAZ4BngGeAZ4BngGgAaIBogGgAZ4BngGeAZ4BngGiAZ4BngGeAaABngGeAZ4BoAGeAZ4BngGgAaABngGeAZ4BngGeAaABngGeAZ4BngGeAaABoAGeAaQBngGgAaA",
    "BngGeAZ4BoAGeAZ4BngGgAZ4BngGgAZwBoAGeAaABngGeAZ4BogGgAZ4BhgGIAYgBhgGOAZ4BkgGUAZIBngGUAYwBogGeAZIBoAGYAaIBlAGOAaQBngGQAZIBoAGSAZ4BngGeAZ4BoAGcAZABngGiAZ4BngGeAZ4",
    "BogGeAZ4BngGeAYwBoAGgAaABoAGeAZ4BngGeAaABngGgAZ4BngGeAZ4BngGeAaABngGeAaABngGeAZ4BngGgAaIBngGeAYQBnAGgAXwBngGeAYwBoAGeAZgBogGeAaIBogGaAZoBmgGcAZwBoAGeAaABngGeAZ4",
    "BngGaAaABngGgAaABoAGgAZoBngGaAZoBngGeAZ4BngGcAZYBmgGgAaABngGiAZoBngGeAZ4BngGWAaABngGeAaABngGMAZ4BngGgAZoBngGeAYwBngGgAaABngGgAaABoAGgAaABoAGgAYYBhgGOAZ4BiAGeAZ4",
    "BhgGOAZ4BjAGeAYwBjgGeAaABpAGiAaIBpAGeAaABngGeAaQBpgGeAZ4BoAGgAYgBngGeAZ4BnAGeAZgBngGKAZIBogGeAZ4BnAGgAZ4BngGeAYwBigGeAY4BngGMAZ4BngGeAZABggGgAaABogGeAaQBoAGgAaA",
    "BngGaAaABoAGaAaABoAGiAaIBpAGiAaIBoAGeAZ4BoAGeAaIBogGiAaIBogGiAaIBogGiAaIBogGiAaIBngGiAZ4BngGeAZoBngGgAZYBngGSAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGeAaIBoAGeAZ4",
    "BngGeAZ4BngGgAZ4BoAGgAYoBlAGUAaABnAGeAZ4BoAGKAZ4BjAGMAZwBkgGSAZ4BngGgAaABoAGeAZ4BkgGSAaABoAGGAZ4BkgGgAaABngGeAaABngGeAZ4BngGeAZ4BngGeAZ4BngGeAaIBogGOAaIBoAGeAaA",
    "BngGeAZ4BngGgAaABngGeAZ4BngGcAZwBjgGQAZYBiAGMAZ4BogGiAaIBqAGgAaABoAGeAZ4BngGgAZ4BngGeAZ4BngGeAZ4BoAGeAZ4BngGeAaABngGeAaIBngGgAZ4BqAGgAZ4BogGeAZoBmgGQAZ4BngGeAaA",
    "BoAGeAZ4BngGeAaABjAGWAaABjAGSAaABoAGYAZwBogGgAaABngGgAZ4BngGeAZ4BoAGgAZIBngGSAZwBkgGaAZ4BkgGgAZwBkgGgAZIBngGgAZIBogGYAZ4BmAGSAaABkgGgAZ4BkgGgAZ4BoAGeAYYBoAGeAZA",
    "BkgGcAY4BlgGUAaABngGeAZ4BngGeAaQBoAGeAZ4BngGeAaIBnAGkAaQBpAGkAaQBpAGkAZ4BngGSAZ4BngGgAYwBoAGSAaABngGcAZ4BjAGgAaABmAGWAZgBnAGcAZ4BogGeAaABigGiAY4BjgGOAZ4BkgGOAZo",
    "BjgGUAZQBngGeAYwBkgF+AaQBoAGiAaABoAGgAZoBkgGOAZ4BjgGYAZQBogGkAaABogGQAaABoAGgAZ4BbgFuAW4BhAFyAXQBbgFuAW4BhgEoAEwAygBMAW4BdAFuAXIBcgFwAW4BcgFuAXQBcgEIAQgBOAD6ATg",
    "BcgFuAXABbgFyAW4BbgFuAXIBbgFuAW4BbgFuAW4BbgF0AW4BdAFuAXIBbgFuAW4BbgFuAW4BbgFuAW4BbgFwP9IBiAEYAYYBGAGGARgBiAEYAYYBhAGEAYYBhgEYARgBGAEYARgBGAEYAVwBEgESARIBEgESARI",
    "BbgGGAW4A1gCeAaAA2gDKANgBnAFMARoBAgGgAZIBngGSAaABjAGYAYwBoAGcAaABiAGQAZwBjgD4AaABigFcAUYBiAD0AaIBkAD4ATgBngGgAIoBSAEqAVgBNgEwATYBEgFAATYBEAEiAZ4BngGSAToBkgEuASY",
    "BFgEgAR4BEAEYAZ4BAgDwATIBngGeAaYBpAEYATABngFkAZ4BoAGeAZYBngGaAaABngGkASIArAF+AYgA6gGgAZwBnAGQAZQA0gGSARIBogGeAaABngGmAZ4BnAGeANoBkAGcAT4BRAE8ARIBQgEsAUoBHgEMASA",
    "BIgDkAOQBAgGOATYBJgFAAT4BQAE0ASQBHADuARwBpAEmATgBRAGIAV4BegGeAJIBYgFUAUIBTACcAaABnAGKAZQBTAGeAZ4BoAFAAZ4AvAGOAYgBoAGaAaQBngGeAYgBngGgAaABngGeAZgBngGiAaIBngGOAYw",
    "BoAGOAaABoAGeAaABngE0AL4BjgGMAZ4BngGgAZ4BkAGeAaABggGWAZQBkgGiANABoAF8AZoBnAGIAZ4BngGeAaABogGeAYYBngDSAaABngEmAaABogGSAYoA0AGeAMYBoAGeAZ4BagGQAaIBngCkAZ4BogCeAII",
    "BoAGQAZ4BhgGSAIIBnAGgAY4BjgGeAGoBngCoAIIBoAGAAZ4BoAGOAY4BnAGGAZQAtgF0AaABoAGeAZ4BoAGOAZ4BdgFyAXIBcAFwAaABcgFyAXIAhgGeANoBngC2AZgBoAGOAZIBkgGeAVwBhAGeAY4BngGOAaA",
    "BngGeAZ4BjgGGAZ4BjAGgAZ4BngGeAZ4BngGeAZ4BkgGKAZ4BoAGeAZABnAGiAZ4BhgGeAJYBegBgAaABngGeAaABngGEAZ4BngGIAYQBoAGSAaABjAGeAYoBhgGeAaABngGOAaABggGeAZ4BoAGeAYQBngGeAZ4",
    "BoACaAXgBkgGeAYABnAGEAZ4BjgGeAXoBngGeAaABngGQAaIBngGeAZ4BjAGeAaABngGMAYwBngGeAY4BoAE6AZ4BngGUAY4BnAGcAaIBngGMAZ4BngGeAZ4BngGeAYYBoAGgAYoBoAEyAZ4BhAGSAToBngGgAZA",
    "BoAGeAZ4BnAGKAaABoAGgAIIBPAGgAZ4BngGMAZ4A3gDWAZwBnAGMAZ4BngGYAZ4BoACaAaIBOgF6AFIBngGcAaABggGeAZ4BlgGgAQQBngGeANoBggGMAaAAqgGMAX4BigGeAZAAtgGYAZ4BNgE2AZ4AwAGaAaA",
    "BmgB2AaIBogCAAaIBoAGgAaABngGgAZ4BigGQAS4BiAGKAaABngGeAZ4AuAGeAaIBngGiAZwBnAGUAaABngGSAaABRgGYAZ4BPgGaAZYBlgGeAZgBmAGaAY4BhgGeAMgBoAGeASIBlgGeAZ4BngGeAZwBogBIAaA",
    "BoACOAZABogGiAZ4BngGeAaIBngEiAaQBngGgAY4BhgGGAZYBjAE6AX4BmgGgAaABoAGgAZ4BkAGgAZ4AlAGgAOoBngGGAaABiADAAZgBngGeAY4BmgGeAZ4BngGeALgBogGCAYIBoAGeAMwBngEoAaABlgGeAZ4",
    "AqAGcAZgBoAGeAZ4BngDuAZ4BiAGgAKoBggGgAaQBlgGiAYoBjAFyAUwBWgGeAYwBoAGeAZ4BlgCuAaIBogCcAKoBjAGOAY4BkAGMAZ4BmgGiAR4BjgGUAYYBEgGMALQBgAGCAZwBnAGcAZoBoAGUAYwBngGeAYY",
    "BUgGeAZ4BDAGgAZgBngGeAZ4BngGeASABngGMAYwApAGQAZ4BoAGgAY4BeACKAaIBHgBeAV4BVgFYAZQBkAGMAYQBogGOAYIBngGeAZ4BjgGiAQwBhAGiAZ4BngGWAZ4BngGgAZwBnAGeAZwBngGCAZ4BoAGgAYY",
    "BcgF+AZ4BJgGeAIYBDAGOAZ4BngGeAZ4BigGOAYgBngGgAZ4BngGSAYgBoAGeAYQBIAGOAX4BkgF+AYQBngGcARQBnAGQAOYBoAGgAZ4BPAGeAWABngGeAY4BlAGOAZQBjgGeAZ4BngGeAZIBDgGgAZIBngGeAZ4",
    "AkgFSAZQBmgGeAY4BiAGeALwAqAGgAaABhAGEAaIBoAGgAaABogGkAaABnAGeAZ4BnAGGAaIBoAGOAXwBngGeAaIBoAGeAIgBoAGeAZ4BngGgAZIBjgDgAZABlAGGAY4BoAGIAZ4BngGAAZwBngGeAZ4BogF4AaA",
    "BoAGeAY4BlgGWAZ4BoAGSAZ4BigGeAZ4BhgGMAZ4BngGUAZoBmAGgAYIBhgGIAYAAdgGQAYwBkgGeAYgBngGgAaABhgGgAYYBhgGSAZwBoAGeAZ4BlgGgAYABnAGaAZ4BoAGUAaABkgGSAZIBngGcAaABmgGeAZo",
    "BjAGaAZ4BhAGeAZwBoAGeAZABiACuAZIA9AGgAOQBogCwAZ4BhgGeAZ4BhgGaAMoBngGgAaABoAGgAY4BngGeAZYBlgGkAMQBjgGIAHgBngGeAZ4BhAGEAZwA5AGiAaABoAC4AZoAyAGEAZ4BngGgAZYBogGeAZ4",
    "BnAEyADABjAGIAaABmgGeAaAArAGeAaABHgGiAX4BEgGSAZIBoAGeAZ4BngGeAZ4BiAGeAOgBmgGgAZ4BngGeAZ4BngDMAOABkAGeAYoBnAGAAZ4BngGgAZwBngCeAZ4AygGeAZ4BigGiAJABogGeAZ4BmgGeAYw",
    "BngGEAZ4BngGeAZ4BoAGcAYwAbAGeAYIBngGeAZ4AOgGeAZ4ATgGAAaQBngGiAXgBeAGMAZ4BngGeAY4BoAGcAZoBngGgAYIBngGeAZ4BngGQAZABjAGMAJoAcgCIAJABngGeAZ4BngGiAaIBngF8AXwBjgGYAZ4",
    "BngGeAZgBlgGiAZ4BngGSAZoBoAGgAAABbYFtgW2BccFzQW2BbYFtgYUBKIBBgJ5AS0FtgXNBbYFywXLBb4FtgXLBbYFzQXLBGYEZgTJA+kEyQXLBbYFvAW2BcsFtgW2BbYFywW2BbYFtgW2BbYFtgW2Bc0FtgXN",
    "BbYFywW2BbgFtgW2BbYFtgW2BbYFtgW2/0gGIQReBhQEXgYUBF4GHwReBhQGDgYOBhQGFAReBF4EXgReBF4EXgReBW8ESgRKBEoESgRKBEoFtgYUBbYDWgXFA14EewJ5APoEDgQlAAA=",
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
