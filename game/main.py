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
FPS = 60                       # 逻辑帧率；手机卡顿可降到 45
WINDOW_TITLE = "AI娘大乱斗 · 手机触屏版"
VERSION = "v3.3-numpad-diag"

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
    """v3.2：删掉原来 8 个占位置的旧小按钮（确/退/上下左右/再/清）。
    菜单项本来就能点，方向键在手机上也用不上，只保留一个「操作说明」入口。"""
    return [_btn(24, 24, 150, 36, "操作说明", (), ())]


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
        手机 IDE 多数把触摸映射成鼠标；支持真多点时走 FINGER_* 分支。"""
        self.just, self.clicks = set(), []
        alias = numpad_alias(self.mode)
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
                self.mouse = self.to_canvas(*ev.pos)
                if -1 in self.stick_hits:
                    self._stick_update(-1, self.mouse)
                if -1 in self.swipe:
                    side, x0 = self.swipe[-1]
                    d = self.mouse[0] - x0
                    self.swipe_dir[side] = 1 if d > 18 else (-1 if d < -18 else 0)
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                # 诊断关键：记录 SDL 给的【原始坐标】，以及换算后的画布坐标。
                # 若原始坐标最大只有几百（而不是 1280），就是页面 CSS 缩放污染了换算。
                cv = self.to_canvas(*ev.pos)
                self._diag("MOUSE raw=(%d,%d) -> canvas=(%d,%d)" %
                           (ev.pos[0], ev.pos[1], cv[0], cv[1]))
                self.last_raw = (int(ev.pos[0]), int(ev.pos[1]))
                self.on_touch_down(-1, ev.pos)
            elif ev.type == pygame.MOUSEBUTTONUP:
                self.on_touch_up(-1)
            elif ev.type == FINGER_DOWN:
                # ev.x / ev.y 是 0~1 归一化坐标
                self._diag("TOUCH norm=(%.3f,%.3f) disp=%dx%d" %
                           (ev.x, ev.y, self.disp_w, self.disp_h))
                self.on_touch_down(ev.touch_id,
                                   (ev.x * self.disp_w, ev.y * self.disp_h))
            elif ev.type == FINGER_MOTION:
                self.mouse = self.to_canvas(ev.x * self.disp_w, ev.y * self.disp_h)
                if ev.touch_id in self.stick_hits:
                    self._stick_update(ev.touch_id, self.mouse)
                if ev.touch_id in self.swipe:
                    side, x0 = self.swipe[ev.touch_id]
                    d = self.mouse[0] - x0
                    self.swipe_dir[side] = 1 if d > 18 else (-1 if d < -18 else 0)
            elif ev.type == FINGER_UP:
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
        draw_text(s, "输入诊断 · 再按 F9 关闭 · 把这一屏截图发我",
                  r.x + 16, r.y + 10, 19, COL_GOLD, True)
        cv = self.to_canvas(*self.last_raw)
        lines = [
            "画布 %dx%d  |  网页 %s  |  缩放 %.3f  |  显示 %dx%d" %
            (SCREEN_W, SCREEN_H, "是" if IS_WEB else "否", self.scale,
             self.disp_w, self.disp_h),
            "鼠标原始 (%4d,%4d)  ->  画布 (%4d,%4d)   ← 关键：原始应能到 1280/720" %
            (self.last_raw[0], self.last_raw[1], cv[0], cv[1]),
            "输入校准 WEB_INPUT_SCALE = %.2f  |  帧 %d  |  页面 %s" %
            (WEB_INPUT_SCALE, self.t, self.scene),
            "最近事件（新→旧）：",
        ] + list(reversed(self.diag_log))[:6]
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
            ("诊断", "按 F9 看鼠标/触摸原始坐标，截图发我"),
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
    assert len(lb) == expect_side and len(rb) == expect_side and len(gb) == 1 and len(mb) == 5
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
    "AAEAAAATAQAABAAwR0RFRhVNFu4AA4ssAAAAQEdQT1MAGQAMAAOLbAAAABBHU1VCbIx0hQADi3wAAAAaT1MvMmYwBBgAAAG4AAAAYGNtYXD4bJ9RAAAlVAAAHMxjdnQgRJ1NcgAAS6gAAAIQZnBnbXPTI7AAAEIg",
    "AAAHBWdhc3AABAAHAAOLIAAAAAxnbHlmT+0pQgAAcbgAAxOyaGVhZBag2GYAAAE8AAAANmhoZWEPeQ6vAAABdAAAACRobXR4+aED4wAAAhgAACM8bG9jYQty5LgAAE24AAAkAG1heHALqAKDAAABmAAAACBuYW1l",
    "lU2vyQADhWwAAAWUcG9zdP8DAGYAA4sAAAAAIHByZXBBvdqCAABJKAAAAn52aGVhEr4JcgADi5gAAAAkdm10eAOib9UAA4u8AAASAAABAAAAADMzKIlASV8PPPUCPwgAAAAAAMY/xrAAAAAA5xiU0f/w/hQICAag",
    "AAAACAAAAAEAAAAAAAEAAAd+/h0AAAgA//D/8ggIAAEAAAAAAAAAAAAAAAAAAAifAAEAAAj/AGYADQCIAA4AAgAQAC8AWgAAAh8BYwAEAAEAAwWTAZAABQAIBZoFMwAAAR4FmgUzAAAD0ABmAfIAAAILBgYDCAQC",
    "AgSAAAADCAHkYAAAABAAAAAAV1FZRgBAACD/XgYf/hQAhAd+AeMAEAAAAAAAAARKBbYAAAAgAAIIAAJYCAABUAQAAEgIAAFQBAAASAgAANgIAADYCAAA2AgAANgIAADYCAAA2AgAANgE0AC4BNABGATQALgE0ACA",
    "BNAAkATQALAIAACwCAAAsAgAAfAIAAAACAAAMAgAADAIAAQACAAA2AgABAAIAAHgCAAEAAgAAYAIAACoCAAAeAgAAKAIAACgCAAAkAgAAFgIAACgCAAAkAgAAHAIAACICAAAeAgAAHgIAABQCAAAYAgAAOAIAACw",
    "CAAAsAgAAHgIAAB4CAAAiAgAAKAIAABwCAAAWAgAAMgIAABoCAAAeAgAAQAIAACQCAAAeAgAANgIAABoCAAAaAgAAHAIAACACAAAYAgAAIAIAABoCAAAYAgAAFgIAABwCAAAWAgAAFAIAABQCAAAUAgAAFAIAABQ",
    "CAAAWAgAAFgIAABQCAAAUAgAAEgIAAEICAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAaAgAAFAIAABQCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABQCAAAUAgAAFAIAABoCAAAUAgAAFAIAABoCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAcAgAAGAIAACQCAAAaAgAAHAIAACACAAAaAgAAFgIAABo",
    "CAAAiAgAAHgIAABoCAAAYAgAAEgIAABoCAAA8AgAAHAIAABgCAAAiAgAAGgIAABoCAAAaAgAAGgIAABoCAAAeAgAAGgIAAB4CAAAWAgAAGgIAADQCAAA2AgAAIAIAACYCAAAsAgAAMgIAABwCAAAaAgAAIAIAAB4",
    "CAAAYAgAAEgIAABICAAAgAgAAJAIAACICAAAYAgAAGgIAAA4CAAAYAgAAEgIAACICAAAWAgAAHAIAAB4CAAAWAgAAIAIAABoCAAAaAgAAEgIAABwCAAAaAgAAFgIAACACAAAaAgAAFAIAADQCAAAeAgAAIgIAACA",
    "CAAAeAgAAIgIAABoCAABMAgAAJgIAADICAAA0AgAAFgIAAB4CAAAUAgAAFAIAABQCAAAUAgAAGgIAABgCAAAiAgAAGgIAABoCAAAaAgAAFAIAABoCAAAmAgAAKAIAACgCAABSAgAAIgIAAB4CAAAwAgAAGgIAABo",
    "CAAAqAgAAFgIAABoCAAAoAgAAHAIAABQCAAAyAgAAGAIAABQCAAA4AgAAGAIAABwCAAAoAgAAFgIAACgCAAAkAgAAIAIAABYCAAAYAgAAEgIAACwCAAAoAgAAKAIAABoCAAAoAgAAKgIAACoCAAAmAgAAKgIAACo",
    "CAAAoAgAAFgIAABwCAAAuAgAALgIAADgCAAAuAgAALgIAAC4CAAAuAgAALgIAADACAAAwAgAAHAIAABACAAAWAgAAFgIAABwCAAAWAgAAFgIAABQCAAAWAgAAFgIAACACAAAaAgAAFgIAABQCAAAWAgAAFgIAABw",
    "CAAAcAgAAKAIAAB4CAAAgAgAAGAIAABICAAAWAgAAFgIAABgCAAAaAgAAHAIAABQCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAFgIAABoCAAAaAgAAHgIAACICAAAWAgAAGgIAACYCAAAgAgAAHgIAACY",
    "CAAAcAgAAIgIAABoCAAAmAgAAGAIAABwCAAAkAgAAJAIAACACAAAaAgAAHAIAACACAAAaAgAAJgIAABICAAAgAgAAGgIAABoCAAAaAgAAKgIAABYCAAAYAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGgIAABY",
    "CAAAeAgAAGgIAAEoCAAAaAgAARAIAADACAAAWAgAAJAIAACICAAAmAgAAIgIAABgCAAAmAgAAIAIAABwCAAASAgAAFAIAABQCAAASAgAAFAIAABQCAAAUAgAAFAIAABgCAAAYAgAAHgIAAB4CAAAaAgAAJAIAADA",
    "CAAAiAgAAIgIAACICAAAiAgAANgIAAD4CAAAgAgAAFgIAABoCAAAUAgAAFAIAABgCAAAYAgAAFgIAABgCAAAWAgAAFAIAABYCAAAWAgAAHAIAABoCAAAaAgAAFAIAABICAAASAgAAEgIAABICAAAWAgAAFAIAABQ",
    "CAAAWAgAAFAIAABQCAAAWAgAAFAIAABgCAAAaAgAAFgIAABYCAAAaAgAAFAIAABoCAAAaAgAAHgIAACICAAAWAgAAGgIAABoCAAAWAgAAGgIAABYCAAAaAgAAKAIAABQCAAAUAgAAFAIAABYCAAAWAgAAFAIAABQ",
    "CAAAWAgAAFAIAABYCAAAWAgAAFgIAABgCAAAWAgAAFgIAABQCAAAYAgAAFAIAABQCAAAWAgAAGAIAABQCAAAUAgAAFAIAABYCAAAUAgAAFgIAABgCAAAWAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAHgIAABQ",
    "CAAAYAgAAFAIAABACAAAYAgAAFAIAABgCAAAWAgAAFgIAABACAAAYAgAAGAIAABgCAAAQAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABYCAAAYAgAAFgIAABgCAAAYAgAAFgIAABYCAAAWAgAAGAIAABg",
    "CAAAYAgAAFgIAABYCAAAWAgAAFgIAACICAAA0AgAAJAIAABoCAAAWAgAAEgIAABoCAAAUAgAAGgIAAB4CAAAaAgAAFAIAABQCAAAwAgAAFgIAABwCAAAgAgAAKgIAABYCAAAgAgAAFAIAABwCAAAsAgAAWAIAAEQ",
    "CAAAeAgAAJgIAAC4CAAAYAgAAGgIAACQCAAAUAgAAHAIAABoCAAAaAgAAJAIAACQCAAAiAgAAFgIAABoCAAAeAgAAGgIAABoCAAAeAgAAFgIAABoCAAAaAgAAFgIAABYCAAAWAgAAIgIAACQCAAAMAgAAJAIAAAw",
    "CAAAMAgAAEgIAABYCAAAgAgAAFAIAABICAAASAgAADAIAABoCAAAYAgAAGAIAABgCAAAeAgAAEgIAABICAAASAgAAEgIAABICAAAUAgAAEgIAABQCAAAYAgAAGAIAABICAAAUAgAAFAIAABICAAASAgAADgIAABQ",
    "CAAAUAgAAEgIAABQCAAAOAgAAGgIAABwCAAAaAgAAGgIAABYCAAAgAgAAEgIAABICAAAcAgAAJAIAABoCAABCAgAAIgIAAB4CAAAWAgAAHAIAABgCAAAWAgAAFgIAABYCAAAaAgAAGgIAABoCAAAWAgAAGgIAABo",
    "CAAAWAgAAGAIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAYAgAAGAIAABgCAAAWAgAAFgIAABgCAAAWAgAAFgIAABYCAAAYAgAAGAIAABYCAAAWAgAAFgIAABYCAAAaAgAAEgIAABo",
    "CAAASAgAAHAIAABQCAAAYAgAAGgIAABoCAAAWAgAAGgIAABoCAAAWAgAAGgIAABoCAAAaAgAAEgIAABICAAAWAgAAFAIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABwCAAAaAgAAGgIAABoCAAAaAgAAGgIAABg",
    "CAAAgAgAAFgIAAEACAABEAgAANAIAAB4CAAAYAgAAOgIAACYCAAAQAgAAEgIAABICAAAQAgAAGgIAAEQCAAAqAgAAKgIAABoCAAAaAgAAGgIAABoCAAAUAgAAGgIAABoCAABUAgAAJAIAAAwCAAAkAgAAGgIAABo",
    "CAAAUAgAAHgIAACgCAAAoAgAAGgIAACgCAAAiAgAAIgIAACICAAAYAgAAFgIAABYCAAAUAgAAFAIAABICAAAOAgAAFAIAABICAAAUAgAADgIAABACAAASAgAAGgIAABoCAAAaAgAAEgIAABYCAAAkAgAAEgIAAA4",
    "CAAAOAgAAFgIAAA4CAAAOAgAAFgIAABICAAASAgAAJgIAABgCAAAcAgAAGgIAACACAAAaAgAAIAIAABoCAAAeAgAAGgIAABoCAAAUAgAAGAIAABoCAAAaAgAAGAIAABoCAAAaAgAAGgIAABwCAAAaAgAAGgIAABQ",
    "CAAAcAgAAFAIAABYCAAAWAgAAGgIAABoCAAAcAgAAHAIAABYCAAAcAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAWAgAAMgIAAB4CAAAeAgAAGgIAABYCAAAUAgAAGAIAABwCAAASAgAAGgIAABgCAAAUAgAAFAIAABQCAAAkAgAAFgIAABQCAAAiAgAAFAIAABoCAAAUAgAAEAIAABY",
    "CAABIAgAAJAIAABgCAAAgAgAAGgIAAB4CAAAeAgAAGgIAAB4CAAAgAgAAGgIAABoCAAAgAgAAHgIAAB4CAAAaAgAAGgIAACACAAAaAgAAGgIAAB4CAAAgAgAAIAIAABQCAAAWAgAAFAIAABgCAAAWAgAAEgIAABQ",
    "CAAAYAgAAEgIAABICAAAaAgAAFAIAABACAAASAgAAEgIAAB4CAAAWAgAAGgIAACYCAAAaAgAAGgIAABICAAAgAgAAGgIAABACAAAYAgAAGAIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABwCAAAcAgAAJAIAABoCAAAYAgAAHAIAABoCAAAcAgAAGAIAACACAAAYAgAAGAIAABgCAAASAgAAGgIAABI",
    "CAAASAgAAEgIAABwCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGAIAABICAAASAgAAGgIAABoCAAAaAgAAGgIAABoCAAAcAgAAGgIAABoCAAAWAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABg",
    "CAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAaAgAAHgIAAAoCAAAaAgAAGgIAABACAAAiAgAAHAIAABg",
    "CAAAaAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAEgIAABQCAAAUAgAAHAIAADQCAAA0AgAANAIAADQCAAA0AgAANAIAACoCAAAqAgAAKAIAACgCAAAoAgAAKAIAACoCAAAiAgAAKAIAACI",
    "CAAAoAgAAKAIAABgCAAAeAgAAIgIAABgCAAAYAgAAGgIAABoCAAAYAgAAGgIAABoCAAAaAgAAGgIAACACAAAaAgAAGgIAABYCAAAUAgAAGAIAABoCAAAcAgAAFAIAABQCAAAYAgAAFgIAABgCAAAWAgAAJAIAABo",
    "CAAASAgAAEgIAABICAAAUAgAAGgIAABoCAAA2AgAAIAIAABoCAAAgAgAAIAIAACACAAAcAgAAGAIAABQCAAAWAgAAGAIAABgCAAA6AgAAFAIAABgCAADgAgAAugIAAGgCAACUAgAAPAIAAG4CAADoAgAAxAIAAIg",
    "CAAB0AgAAjAIAAFQCAABKAgAAWAIAAIQCAACMAgAApgIAAI4CAACMAgAAeAIAAJICAACMAgAAigIAAI4CAACMAgAAagIAAGICAACMAgAAjAIAAIwCAACOAgAAPgIAAFoCAACIAgAAcgIAAHoCAACMAgAAjAIAAGg",
    "CAAB0AgAAigIAAIACAACIAgAAoAIAAFQCAABoAgAAWAIAAJICAABYAgAAhAIAAIACAABmAgAAbAIAAFoCAAAiAgAAYAIAAGQCAAB2AgAAzgIAAIQCAACkAgAAggIAAAACAADEAgAAigIAAIwCAACUAgAAdgIAAII",
    "CAACEAgAAdgIAAIYCAACSAgAAhAIAAJoCAACUAgAARAIAAIYCAAB+AgAAjAIAAHYCAACmAgAAmgIAAIwCAACGAgAAcAIAAEYCAAB0AgAAcAIAAJQCAACaAgAA7gIAAIoCAACMAgAAQgIAABoCAAAYAgAAGAIAAB4",
    "CAAD6AgAAagIAAKQCAACeAgAAigIAAKACAACYAgAAtAIAAJICAACcAgAAkgIAAJoCAACiAgAAngIAAKYCAACWAgAApAIAALYCAACcAgAAIAIAAPwCAAD2AgAAbAIAACICAAEEAgAAGgIAAOoCAAAoAgAAGgIAABg",
    "CAACEAgAAFAIAAGYCAAAaAgAAUgIAACICAACcAgAALAIAACICAADKAgAAGgIAAB4CAAAaAgAAHgIAAMACAAAkAgAAFAIAAB4CAADsAgAAGgIAABoCAABAAgAAGgIAABgCAAAUAgAAQAIAAEACAAA8AgAAHAIAACw",
    "CAAAUAgAAQAIAABwCAAAaAgAAIAIAAJICAAA6AgAAKAIAABoCAAAYAgAATgIAAEoCAABkAgAAXgIAAMICAAAoAgAAHgIAABoCAAAcAgAARAIAANICAAAgAgAAHgIAAB4CAACWAgAAqAIAANoCAABsAgAAGgIAACA",
    "CAAAaAgAAFAIAAGYCAAAiAgAAiAIAAH4CAACwAgAAIgIAAE4CAADWAgAAXAIAAGICAACOAgAAfgIAAIACAACEAgAAGAIAABYCAAAaAgAAdAIAAHgCAACEAgAAVgIAAHACAABMAgAAHAIAACACAAAkAgAAVAIAABo",
    "CAAAiAgAAYAIAABoCAAAiAgAASgIAACICAAAYAgAAJgIAAGACAABeAgAAkAIAAKICAABkAgAAbAIAAGYCAACCAgAAMgIAACICAABgAgAAIgIAAKoCAACOAgAAFgIAABwCAAC4AgAAIgIAAMACAADeAgAA3gIAAMQ",
    "CAADQAgAA2gIAAUACAAAYAgAAvAIAAIYCAACsAgAADgIAAK4CAADSAgAAoAIAABoCAAAaAgAAtgIAABoCAAAYAgAAFgIAABgCAAAaAgAAHAIAAKgCAACqAgAAyAIAABQCAAAiAgAA1AIAABgCAACqAgAAfgIAAKo",
    "CAAC6AgAAqAIAAWACAAAWAgAAzAIAALACAAAoAgAAEAIAAMYCAAAiAgABEgIAAKoCAACWAgAAGgIAABYCAACyAgAAFgIAABYCAAAaAgAAmAIAAHYCAABYAgAAvAIAAKQCAAAeAgAAEgIAABICAABMAgAAhAIAACA",
    "CAAAcAgAAIAIAABYCAACqAgAAkgIAANACAAC+AgAAmgIAALYCAAAqAgAAdgIAALoCAAAmAgAAGgIAARICAACiAgAAIAIAAQoCAAAgAgAAcAIAAL4CAADAAgAArAIAALACAAC+AgAAGgIAABwCAABQAgAAVgIAABw",
    "CAAA0AgAAFgIAALYCAADoAgAAzgIAABYCAADIAgAA3AIAACACAAEeAgAA2AIAAJgCAACiAgAAkAIAAJYCAACuAgAAqgIAAP4CAAAoAgAAKAIAACgCAAAqAgAAsgIAACoCAAAoAgAAMAIAABoCAADSAgAAIAIAABo",
    "CAABCAgAAyAIAABICAADaAgAAFgIAABQCAAEmAgAAngIAAKoCAAC+AgAA1gIAABgCAACiAgAArgIAAIQCAAAqAgAAvAIAAJQCAADAAgAAogIAAIICAADWAgAAuAIAALoCAACyAgAArAIAANQCAADOAgAAugIAAL4",
    "CAAAaAgAA5AIAAKoCAACwAgAAwAIAAMICAACmAgAAvAIAALICAAEAAgAAqAIAACACAAAaAgAAJAIAAB4CAADoAgAAJAIAABICAADCAgAAGAIAAIoCAACEAgAASgIAAOoCAACOAgAAkAIAAJgCAAC4AgAAGgIAAII",
    "CAAFaAgAACgIAAB4CAACoAgAAkgIAALQCAACEAgAAEgIAAKQCAACeAgAAsgIAAIACAAC8AgAAjAIAAOQCAAAuAgAA1gIAAKYCAACUAgAAqAIAAB4CAAAqAgAAqAIAAJQCAAC+AgAAxgIAAKQCAADAAgAAHAIAAK4",
    "CAADYAgAAbgIAAKoCAAEMAgAA0gIAALQCAAAYAgAAuAIAAJQCAAASAgAAqgIAAIICAAAaAgAAkgIAALYCAACMAgAA4gIAAMQCAAC0AgAAjgIAAB4CAAAOAgAAGgIAABgCAAAoAgAAngIAANoCAADAAgAA6gIAAHI",
    "CAACMAgAAngIAAJwCAAEEAgAAEgIAAJwCAAAeAgAArgIAALACAACsAgAAJAIAAHoCAACQAgAAtAIAAKICAAASAgAA5AIAACACAAAmAgAA6gIAAKwCAAD8AgAA9AIAABoCAAEGAgAAIAIAACACAADkAgAA0AIAAJo",
    "CAACaAgAA4gIAALgCAAAuAgAAmgIAABoCAADcAgAAHAIAAL4CAAAQAgAAvgIAAM4CAADgAgAA7AIAAEICAAAsAgAAHAIAAI4CAAAcAgAANAIAANICAAC8AgAAGgIAAMgCAAASAgAA/gIAACQCAADIAgAAUAIAAHo",
    "CAACWAgAAJAIAACACAAE0AgAAFAIAALgCAAASAgAAGgIAAB4CAAAYAgAAxAIAAMACAADmAgAAFgIAALgCAADCAgABJgIAALQCAAAYAgAAggIAABICAADkAgAAGAIAABgCAAAWAgAAKAIAALYCAADKAgAAqAIAAM4",
    "CAACEAgAAZAIAABoCAADWAgAAXAIAANICAAAYAgAAqAIAAMICAAAaAgAAEgIAABoCAAAeAgAAFgIAAL4CAACuAgAAsAIAANICAAEwAgAAuAIAAEYCAAAUAgAAfgIAABoCAAAaAgAAzAIAABYCAAAWAgAA6gIAACg",
    "CAAAcAgAAugIAAKQCAADoAgAAhAIAAQACAACuAgAAKAIAAB4CAAASAgAAHAIAAFQCAAD4AgAAFAIAABwCAACKAgAAHgIAAUICAAAgAgAAGAIAALQCAAEaAgAAiAIAANoCAADOAgAAuAIAAIYCAADYAgAArAIAAOw",
    "CAABgAgAAFAIAAFoCAAAWAgAAdgIAABgCAADAAgAAKAIAADACAADGAgAAGgIAAPoCAADuAgAA9AIAABYCAAC4AgAAFgIAACoCAAAaAgAAHAIAABgCAAD0AgABCAIAABoCAAC2AgAA3AIAAMoCAACiAgAAwgIAAMQ",
    "CAAAUAgAAFAIAAOQCAAASAgAA1AIAABICAACsAgAAPAIAAJwCAACqAgAAxAIAACoCAADMAgAArgIAACYCAAAgAgAAIAIAALoCAACYAgAAGgIAAHQCAABwAgAAxgIAALoCAADsAgAAFgIAALgCAAAaAgAAIAIAABw",
    "CAABWAgAAKgIAAPACAAAgAgAAIAIAABoCAADaAgAAqAIAAOQCAAAmAgAAxAIAALgCAADqAgAA2gIAAQwCAAAgAgAAGAIAABgCAADKAgAAogIAAMICAACcAgAAcAIAAI4CAAC2AgAA/AIAAN4CAADgAgAAagIAACI",
    "CAADoAgAAGgIAAB4CAAAgAgAAuAIAAJQCAAAWAgAA6gIAACACAACoAgAA5AIAAQACAAAcAgAAIgIAABwCAADGAgAArAIAABYCAAAmAgAAUgIAABoCAABAAgAAHAIAAGQCAABsAgAAdgIAABQCAACwAgAAIgIAABo",
    "CAAAaAgAAugIAACwCAADKAgAAGgIAADQCAACqAgAAJgIAAHoCAAAWAgAAyAIAAMwCAAA2AgAALAIAABYCAAEyAgAAtAIAABICAAASAgAAlAIAAMYCAAAaAgAAqgIAAKwCAAFAAgAAFgIAANgCAAAaAgAAEgIAAKg",
    "CAAB6AgAAGgIAABoCAAC2AgAAtgIAABoCAADIAgAAGAIAABYCAAAcAgAAzAIAABoCAAAUAgAAHgIAABICAADiAgAAFAIAALQCAACYAgAAFAIAABYCAAAgAgAAmgIAABACAAAQAgAAFAIAABoCAABkAgABJAIAARo",
    "CAAAaAgAAHAIAAKoCAAB+AgAAigIAAJgCAAC8AgAAPAIAAJICAAEKAgAA7AIAAO4CAAAUAgAA3AIAADwCAAAUAgAAFAIAABQCAAAUAgAAFgIAABwCAADyAgAAGgIAABoCAAAaAgAAGgIAAG4CAABEAgAAkAIAABo",
    "CAADGAgAAqAIAAB4CAAAiAgAAVgIAALACAACQAgAAHAIAACoCAAAqAgAAwAIAANoCAADSAgAAFAIAAMACAADIAgAAEgIAABwCAACGAgAAEgIAADACAAAiAgABKgIAACACAAAcAgAAngIAAKICAAASAgAAuAIAABQ",
    "CAACYAgAArgIAABoCAAAaAgAA9AIAACQCAAAYAgAAqAIAALYCAAAqAgAAEgIAABQCAAASAgAAEgIAAQ4CAAASAgAAFgIAABYCAAAaAgAAEgIAACYCAAAWAgAAFgIAABQCAAD2AgABKAIAAPICAADcAgAAFAIAAM4",
    "CAACsAgAAxAIAAKoCAACQAgAAwAIAAKACAAGIAgAAIgIAAJoCAACeAgAAHAIAAIACAADMAgAAogIAAOQCAAE2AgAAJgIAABoCAAAmAgAAjgIAABQCAACkAgAAngIAABwCAAAcAgAAFAIAAOACAAAUAgAAGgIAAOY",
    "CAAAUAgAAjAIAAOoCAAAaAgAA2gIAAQwCAAFcAgAA1gIAAMwCAAC4AgAA5gIAAJoCAACiAgABAAIAABQCAAAWAgAA+AIAATACAAAUAgABEAIAAMgCAAAWAgAAygIAALoCAAAaAgAAGgIAABoCAAAYAgAAFgIAAKA",
    "CAADQAgABIAIAASACAAA8AgAAIgIAAGQCAAAqAgAAHAIAABQCAAAaAgAA7AIAAMACAAAYAgAAHAIAABoCAAAUAgAAFAIAAIoCAACuAgAAwgIAALACAAC8AgAAFgIAABYCAACcAgAALgIAACACAACQAgAAFAIAALY",
    "CAAC4AgAAFAIAABoCAADmAgABVgIAABgCAAAqAgAAnAIAACYCAAAYAgAALgIAABoCAACiAgAAGgIAABgCAAAeAgAA8AIAABYCAACmAgAAtgIAAJoCAAAaAgAAGgIAACgCAADIAgAAzAIAAIICAACkAgAAGgIAACw",
    "CAAEGAgAAFgIAABwCAAAmAgAADgIAAHQCAAAUAgAAFAIAAMQCAAEeAgABQgIAAMICAAAUAgAAGgIAAOYCAAAaAgAAfAIAAI4CAAAWAgABAAIAABQCAADkAgAAwgIAABICAAAaAgAAGgIAAFYCAAFiAgAArAIAAIA",
    "CAAFaAgAAFAIAABYCAAASAgAAsgIAABgCAAESAgAAbAIAAIwCAAFsAgAAFgIAAEYCAAAYAgAAGgIAAB4CAAEAAgAAiAIAABACAADYAgAAEgIAAKACAAAMAgABOAIAABoCAAAUAgAAsgIAAB4CAAB0AgAAFgIAALo",
    "CAACqAgAAtgIAABICAADaAgAAGgIAACACAAAgAgAAGgIAARYCAAAgAgAAJgIAAMICAAAiAgAAJAIAAFYCAACYAgAAFAIAABYCAAAUAgAAGgIAANwCAAAaAgAA0gIAAUQCAAAkAgAA2gIAAOwCAAAYAgAAFgIAABY",
    "CAAAeAgAAMAIAACICAAAaAgAAGgIAABoCAAAaAgAAFAIAABQCAAAUAgAAFAIAABoCAAAaAgAAIAIAACQCAAAoAgAAtgIAAMYCAACMAgAAGAIAAJYCAAAiAgAAIgIAALoCAACmAgAAEgIAAMQCAAAWAgAAjAIAAA4",
    "BM0AAAHnAR0ALQAAAScBKQCFAJgBuAEdAc8A0wCTAOEAngCDAD0ArACaAI8AnACaAecBmgCYAJgAmACoAB8AIQCHAIEAhwDZAPQAdQCHAOEAiQDTAOkAcQCHAFQAsABUALoAjQBmAH0AIQACADUAIQBmAZwA0wEh",
    "//ABogCHAJ4ArACJAIUAnABmAKAAxQCHANcAvABcAKAAcwCeAIkBCADLAIsAoABS//wAYABSALYA4QIbAOMAmAFcAecAvv/6AE4ARgAAAAIAAAADAAAAFAADAAEAAAAUAAQcuAAAByoEAAAJAyoAIwAlAF0AfgCy",
    "ALcA1yAUICYhkyIeJGYlsiW2JbwlwCXGJc8mBicTMAIwDTARTgBOB04LTg5OFE4cTiJOJU4qTi1ONE47TkVOSU5LTk5OWU5dTmBOZk5xToZOiU6MTo5Okk6UTptOpE6nTq5Ouk7ATsZOzk7TTtZO5U7sTvdO+079",
    "TxFPGE8aTyBPJE84TzxPRk9PT1NPVU9ZT1xPYE9/T4tPm0+dT6dPv0/dT+FP7lANUBJQGVA8UD5QR1BPUFpQXFB/UKhQrFC7UM9Q9VFBUUNRSVFNUVxRZVFoUW1RcVFzUXhRfFGFUY1RmVGzUbVRt1G7UcBRxlHP",
    "UdFR4FH2UftR/VIAUgNSB1ISUhdSGVIbUh1SIFIkUitSMFI3UjtSTVJUUmpSiFKbUqFSqVK/UwVTFlM6U0FTQ1NHU0pTVVNXU2FTcFN0U3dTi1OaU59Tu1PCU8hTylPNU9FT2FPgU+RT7FPwU/NT91QEVAhUDlQR",
    "VCZULFQvVDhUSFRYVGhUfVSMVMFUyFTNVOVU6lUkVS9VRlWKVdxWNFZoVspW21beVuBW4lb0VvpW/lcGVwhXI1coVzBXOldAV0dXUVdXV4JXi1ffV/pYg1ieWQRZB1kNWRZZGlkcWR9ZJ1kqWS5ZMVk0WVFZV1ll",
    "WXNZdll9WctZ0Fn/WhhazFtQW1hbZluDW4lbjFuYW5pbnluiW6RbqluzW7ZbuVu9W/lb/FwEXA9cEVwWXBhcHVwxXDpcPlxAXEJcRVxPXF5dKV1MXeZd6F3uXfJeA14nXjheRV5VXnNedl6PXpVel16mXq1e9l76",
    "XwBfAl8PXxVfIF8nXzpfU19VX2JfcV97X4BfhV+LX5dfoV+qX65fvV/DX8Vf11/rYAFgDmASYB1gJ2A7YFJgYmBvYMVg72DzYQhhD2EfYWJiEmIWYhhiKmI0YjdiQGJHYktiTWJTYlhiW2JjYmdiaWJrYnBigGKE",
    "Yopik2KVYphiomKlYqxisWK1YsZiyWLNYtJi1mLbYt9i6WLsYvFi/2MCYwdjCWMRYyFjJGMoYypjX2NiY25jd2OJY5JjpWOoY7dj0GPSY/RkHGQeZC1kR2RKZHhknmSkZK1kxWTOZS9lNmU5ZTtlPmVIZUxlT2Vj",
    "ZXBldGWHZYtll2WcZadlqWWtZbBluWXLZeBl4mXlZedl6WX2Zg5mE2YgZi9mPmZvZoJml2a0ZvRnAGcJZw1nHWcfZyxnL2c1ZzpnQGdDZ0ZnUGdfZ2FnZWd/Z4FnhGecZ7Zn0GfTZ+VoB2gPaCFoOWg8aEZoSGhM",
    "aGNoZWh2aK9owGktacxp/WohaipqWWsha2Vre2u1a81rz2vSa9RsFGw0bDhsQmxHbElsYWyJbKFsv2zJbNVs4mzobPxtO20+bUFtS21PbW5td22Ibaht4W3xbfduBW4QbiFuMm44bpBu0W7ebuFvAm8PbxRvwHBr",
    "cG9wdXCucLlw33DtcTZxZ3IGcipyMXJIckxyWXJpcnlyr3K2ctBy7HL4cxxzK3OHc6lzsHQDdAZ093UfdSh1MnU1dTt1THVZdWV1l3WrddV2e3Z+doR2xnbKds920nbWdth27nb0dvl2/ncBdwt3IHc8d0B3W3dh",
    "d6x3s3fld+l37XgBeBR4NHg4eEB4bHhueJd4sHi+eTp5PHk+eV55gXm7ecF5zXnSedh58Hn7egt6M3o/enp6f3qBepd6nXrLetZ62Xrgeu97G3smeyx7SXtUe1Z7fnuAe5d7oXute8d8B3xzfHt8knzKfPt9IH0i",
    "fSd9K30vfqJ+p36vfrl+v37Efsh+z37TftV+2X7dft9+537pfu1/AH8TfxZ/GH8pfzp/UX9pf25/jn/7gAOABYAMgBeAM4BMgFSAWoClgMyA3ID2gP2BEYEagXCBf4HCgeqB9IIMgnKCgoKxgs+C5YMDgzaDUIO3",
    "g9yEJYQ9hLiExITdhc+GWobLh4OH+YhAiEWITIhhiGWIaIhwiI2Iq4jCiMWI2Yj4iX+JgYmGicKJxInGicmJ0onjieaKAIuhi6SLqYuui7CLsou4i7+LwYvKi82L0YvVi92L5Yvti++L9Iv7jAGMA4xhjGqNH40j",
    "jSaNKI0vjTSNOY1EjUuNVI1WjXCNd42FjYqNs43DjdGN3Y3fje+N844pjquOso66j2aPaI9sj26Pe499j5GPk4+oj7mPxY/Hj9GP1I/Zj9yP34/3j/2QApAJkBCQEpAakCCQO5BTkG6Qf5CjkOiQ/ZFNkZKRypHN",
    "kc+R0ZSIlJ+UrpTBlPaU+pUBlQuVGZUulVyVf5XoleqV7pX0lgGWMpY1lkWWTZZQlmSWaZaQlpSWxpb2lwCXB5cylziXUpdZl16XYJdil/OYdph7mH+YhJiYmJ2YzpjYmN+ZbZlwmYiZj5mWmZmabJpxmnuaf5qM",
    "mqia2Jx8nLieIZ7RntifIJ9Qn5n/Xv//AAAAIAAlACgAXwCyALcA1yAUICYhkCIeJGAlsiW2JbwlwCXGJc8mBScTMAAwCjAQTgBOB04JTg1OE04cTiJOJE4qTi1ONE46TkVOSE5LTk5OWU5dTl9OZk5xToZOiU6L",
    "To5Okk6UTptOpE6nTq5Ouk6/TsVOzU7TTtZO407sTvZO+079TxFPGE8aTyBPJE84TzxPRk9NT1NPVU9ZT1xPYE9/T4tPm0+dT6dPv0/dT+FP7lANUBJQGVA8UD5QR1BPUFpQXFB/UKhQrFC7UM9Q9VFBUUNRSFFN",
    "UVxRZVFoUW1RcVFzUXZRfFGFUYxRmVGyUbVRt1G7UcBRxlHPUdFR4FH2UfpR/VIAUgNSBlISUhdSGVIbUh1SIFIkUitSMFI2UjpSTVJUUmlSiFKbUp5SqFK/UwVTFlM6U0FTQ1NHU0pTVVNXU2BTcFNzU3dTi1Oa",
    "U59Tu1PCU8hTylPMU9FT1lPgU+NT6lPvU/NT91QDVAhUDFQRVCZUK1QvVDhUSFRYVGhUfVSMVMFUyFTNVOVU6lUkVS9VRlWKVdxWNFZoVspW21beVuBW4lb0VvpW/lcGVwhXI1coVzBXOldAV0dXT1dXV4JXi1ff",
    "V/pYg1ieWQRZB1kNWRZZGlkcWR9ZJ1kqWS5ZMVk0WVFZV1llWXNZdll9WctZ0Fn/WhhazFtQW1dbZluDW4lbjFuYW5pbnlugW6RbqluzW7ZbuVu9W/hb/FwEXA9cEVwWXBhcHVwxXDpcPlxAXEJcRVxPXF5dKV1M",
    "XeVd6F3uXfFeA14mXjheRV5VXnJedl6PXpNel16mXq1e9l76XwBfAl8PXxVfIF8nXzlfUl9VX2JfcV97X4BfhF+LX5dfoV+qX65fvV/DX8Vf11/rYAFgDmASYB1gJ2A7YFJgYmBvYMVg72DzYQhhD2EfYWJiD2IW",
    "YhhiKmI0YjdiP2JHYktiTWJTYlhiW2JjYmdiaWJrYnBifmKEYopik2KVYphiomKkYqxisWK1YsViyWLNYtJi1mLbYt9i6WLsYvFi/WMBYwdjCWMRYyFjJGMoYypjX2NiY25jd2OJY5JjpWOnY7djz2PSY/RkHGQe",
    "ZC1kRmRKZHhknmSkZK1kxWTNZS9lNmU5ZTtlPmVIZUxlT2VjZXBldGWHZYtll2WcZadlqWWtZbBluWXLZeBl4mXlZedl6WX2Zg5mE2YfZi9mPmZuZoJmlma0ZvRm/2cIZw1nHWcfZypnL2c1ZzpnQGdDZ0ZnUGdf",
    "Z2FnZWd/Z4FnhGecZ7Zn0GfTZ+VoB2gPaCFoN2g8aEZoSGhMaGNoZWh2aK9owGktacxp/WohaipqWWsga2Jre2u1a81rz2vSa9RsFGw0bDhsQmxHbElsYWyJbKFsv2zJbNVs4WzobPxtO20+bUFtS21PbW5td22I",
    "baht4W3xbfduBW4QbiFuMm44bpBu0W7ebuFvAm8PbxRvwHBrcG9wdXCucLlw33DtcTZxZ3IGcipyMXJHckxyWXJpcnlyr3K2ctBy7HL4cxtzK3OHc6lzr3QDdAZ093UfdSh1MXU1dTt1THVZdWV1l3WrddV2e3Z9",
    "doR2xnbKds920XbWdth27nb0dvh2/ncBdwt3H3c8d0B3W3dhd6x3s3fld+l37XgBeBR4NHg4eEB4bHhueJd4sHi+eTp5PHk+eV55gXm7ecF5zXnSedh58Hn7egt6M3o/enp6f3qBepd6nXrLetZ62Xrgeu97G3sm",
    "eyx7SXtUe1Z7fnuAe5d7oXute8d8B3xzfHt8knzKfPt9IH0ifSd9K30vfqJ+pn6vfrd+v37Dfsh+z37TftV+2H7dft9+537pfu1/AH8TfxZ/GH8pfzp/UX9pf25/jn/7gAOABYAMgBeAM4BMgFSAWoClgMyA3ID2",
    "gP2BEYEagXCBf4HCgeqB84IMgnKCgoKxgs+C5YMDgzaDUIO3g9yEJYQ9hLiExITdhc+GWobLh4OH+YhAiEWITIhhiGWIaIhwiI2Iq4jBiMWI2Yj4iX+JgYmGicGJxInGiciJ0onjieaKAIuhi6SLqYuti7CLsou4",
    "i76LwYvKi82L0YvVi92L5Yvti++L9Iv7jAGMA4xhjGqNH40jjSWNKI0vjTSNOY1EjUuNVI1WjXCNd42FjYqNs43DjdGN3Y3fje+N844pjquOso66j2aPaI9sj26Pe499j5GPk4+oj7mPxY/Hj9CP1I/Yj9uP3o/3",
    "j/2QAJAJkA+QEpAakB+QO5BTkG6Qf5CjkOiQ/ZFNkZKRypHMkc+R0ZSIlJ+UrpTBlPaU+pUAlQuVGZUulVyVf5XoleqV7ZX0lgGWMpY0lkSWTZZQlmSWaZaPlpSWxpb2lwCXB5cylziXUpdZl16XYJdil/OYdZh5",
    "mH6YhJiXmJyYzpjYmN6ZbZlwmYiZj5mWmZmabJpxmnuaf5qMmqia2Jx8nLieIZ7RntifIJ9Qn5n/Af//CH4IfQh7CHoIRwhDCCTo6OjX3nHm4Nul2lraV9pS2k/aStpC2g3ZAdAV0A7QDLIeshiyF7IWshKyC7IG",
    "sgWyAbH/sfmx9LHrsemx6LHmsdyx2bHYsdOxybG1sbOxsrGxsa6xrbGnsZ+xnbGXsYyxiLGEsX6xerF4sWyxZrFdsVqxWbFGsUCxP7E6sTexJLEhsRixErEPsQ6xC7EJsQaw6LDdsM6wzbDEsK2wkLCNsIGwY7Bf",
    "sFmwN7A2sC6wJ7AdsByv+q/Sr8+vwa+ur4mvPq89rzmvNq8oryCvHq8arxevFq8UrxGvCa8Drviu4K7frt6u267XrtKuyq7Jrruupq6jrqKuoK6erpyukq6Oro2ujK6Lromuhq6Arnyud651rmSuXq5Kri2uG64Z",
    "rhOt/q25ramthq2ArX+tfK16rXCtb61nrVmtV61VrUOtNa0xrRatEK0LrQqtCa0GrQKs+6z5rPSs8qzwrO2s4qzfrNys2qzGrMKswKy4rKmsmqyLrHesaaw1rC+sK6wUrBCr16vNq7erdKsjqsyqmao4qimqJ6om",
    "qiWqFKoPqgyqBaoEqeqp5qnfqdap0anLqcSpv6mVqY2pOqkgqJiofqgZqBeoEqgKqAeoBqgEp/2n+6f4p/an9KfYp9Onxqe5p7ensadkp2CnMqcapmel5KXepdGltaWwpa6lo6WipZ+lnqWdpZilkKWOpYyliaVP",
    "pU2lRqU8pTulN6U2pTKlH6UXpRSlE6USpRClB6T5pC+kDaN1o3Sjb6Nto12jO6Mrox+jEKL0ovKi26LYoteiyaLDonyieaJ0onOiZ6JioliiUqJBoiqiKaIdog+iBqICof+h+qHvoeah3qHboc2hyKHHobaho6GO",
    "oYKhf6F1oWyhWaFDoTShKKDToKqgp6CToI2gfqA8n5CfjZ+Mn3ufcp9wn2mfY59gn1+fWp9Wn1SfTZ9Kn0mfSJ9EnzefNJ8vnyefJp8knxufGp8UnxCfDZ7+nvye+Z71nvKe7p7rnuKe4J7cntGe0J7MnsuexJ61",
    "nrOesJ6vnnueeZ5unmaeVZ5NnjueOp4snhWeFJ3zncydy529naWdo512nVGdTJ1EnS2dJpzGnMCcvpy9nLucspyvnK2cmpyOnIuceZx2nGucZ5xdnFycWZxXnE+cPpwqnCmcJ5wmnCWcGZwCm/6b85vlm9ebqJuW",
    "m4ObZ5somx6bF5sUmwWbBJr6mvia85rvmuqa6Jrmmt2az5rOmsuaspqxmq+amJp/mmaaZJpTmjKaK5oamgWaA5n6mfmZ9pngmd+Zz5mXmYeZG5h9mE2YKpgil/SXLpbultmWoJaJloiWhpaFlkaWJ5YklhuWF5YW",
    "lf+V2JXBlaSVm5WQlYWVgJVtlS+VLZUrlSKVH5UBlPmU6ZTKlJKUg5R+lHGUZ5RXlEeUQpPrk6uTn5Odk32TcZNtksKSGJIVkhCR2JHOkamRnJFUkSSQhpBjkF2QSJBFkDmQKpAbj+aP4I/Hj6yPoY9/j3GPFo71",
    "jvCOno6cjayNhY19jXWNc41ujV6NUo1HjReNBIzbjDaMNYwwi++L7Ivoi+eL5Ivji86LyYvGi8KLwIu3i6SLiYuGi2yLZ4sdixeK5orjiuCKzYq7ipyKmYqSimeKZoo+iiaKGYmeiZ2JnIl9iVuJIokdiRKJDokJ",
    "iPKI6IjZiLKIp4htiGmIaIhTiE6IIYgXiBWID4gBh9aHzIfHh6uHoYegh3mHeIdih1mHToc1hvaGi4aEhm6GN4YHheOF4oXehduF2IRmhGOEXIRVhFCETYRKhESEQYRAhD6EO4Q6hDOEMoQvhB2EC4QJhAiD+IPo",
    "g9KDu4O3g5iDLIMlgySDHoMUgvmC4YLagtWCi4JlglaCPYI3giSCHIHHgbmBd4FQgUiBMYDMgL2Aj4BygF2AQIAOf/V/j39rfyN/DH6Sfod+b31+fPR8hHvNe1h7EnsOewh69Hrxeu966HrMeq96mnqYeoV6Z3nh",
    "eeB53HmieaF5oHmfeZd5h3mFeWx3zHfKd8Z3w3fCd8F3vHe3d7Z3rnesd6l3pnefd5h3kXeQd4x3hneBd4B3I3cbdmd2ZHZjdmJ2XHZYdlR2SnZEdjx2O3Yidhx2D3YLdeN11HXHdbx1u3Wsdal1dHTzdO105nQ7",
    "dDp0N3Q2dCp0KXQWdBV0AXPyc+dz5nPec9xz2XPYc9dzwHO7c7lzs3Ouc61zpnOic4hzcXNXc0dzJHLgcsxyfXI5cgJyAXIAcf9vSW8zbyVvE27fbtxu127ObsFurW6Abl5t9m31bfNt7m3ibbJtsW2jbZxtmm2H",
    "bYNtXm1bbSps+2zybOxswmy9bKRsnmyabJlsmGwIa4drhWuDa39rbWtqazprMWssap9qnWqGaoBqemp4aaZpommZaZZpimlvaUBnnWdiZfplS2VFZP5kz2SHBSAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
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
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "AAAAAAAAAABARVlYVVRTUlFQT05NTEtKSUhHRkVEQ0JBQD8+PTw7Ojk4NzY1MTAvLi0sKCcmJSQjIiEfGBQREA8ODQsKCQgHBgUEAwIBACxFI0ZgILAmYLAEJiNISC0sRSNGI2EgsCZhsAQmI0hILSxFI0ZgsCBh",
    "ILBGYLAEJiNISC0sRSNGI2GwIGAgsCZhsCBhsAQmI0hILSxFI0ZgsEBhILBmYLAEJiNISC0sRSNGI2GwQGAgsCZhsEBhsAQmI0hILSwBECA8ADwtLCBFIyCwzUQjILgBWlFYIyCwjUQjWSCw7VFYIyCwTUQjWSCw",
    "BCZRWCMgsA1EI1khIS0sICBFGGhEILABYCBFsEZ2aIpFYEQtLAGxCwpDI0NlCi0sALEKC0MjQwstLACwKCNwsQEoPgGwKCNwsQIoRTqxAgAIDS0sIEWwAyVFYWSwUFFYRUQbISFZLSxJsA4jRC0sIEWwAENgRC0s",
    "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",
    "AAAXgAAAF5YAABg3AAAYrAAAGMIAABkGAAAZHAAAGTIAABlIAAAZXgAAGXQAABmKAAAZoAAAGbYAABnMAAAaVAAAGtgAABruAAAbBAAAGxoAABswAAAbRgAAG1wAABtyAAAcCwAAHCEAABw3AAAcTQAAHGMAABx5",
    "AAAcjwAAHKUAABy7AAAc0QAAHOcAAB2WAAAdrAAAHcIAAB3YAAAd9AAAHgoAAB4gAAAePAAAHlIAAB5oAAAefgAAHpQAAB6qAAAexgAAHtwAAB7yAAAfDgAAHyQAAB86AAAfVgAAH2wAAB+CAAAfngAAH7QAAB/K",
    "AAAf4AAAH/YAACCUAAAhCwAAIaIAACI1AAAi7AAAI88AACQpAAAkrQAAJRUAACWcAAAmJAAAJr4AACdJAAAoCwAAKPAAAClmAAAqHwAAKrkAACrPAAAq5QAAKvsAACsRAAArJwAAKz0AACtTAAAraQAAK38AACuV",
    "AAAr8wAALGsAACzFAAAtJgAALTwAAC2dAAAuDgAALp0AAC6zAAAuyQAALt8AAC71AAAvCwAALyEAAC83AAAvTQAAL2MAAC95AAAvjwAAL6UAAC+7AAAv0QAAMI4AADCkAAAwugAAMNAAADDmAAAxSAAAMeAAADH2",
    "AAAyDAAAMiIAADI4AAAyTgAAMmoAADMBAAAzFwAAM4MAADOzAAAz/QAANGkAADTaAAA1cgAANhoAADZkAAA2tgAANswAADbiAAA2+AAANw4AADc9AAA3UwAAN2kAADd/AAA3+QAAONcAADlGAAA5zgAAOeQAADp7",
    "AAA7MQAAO0cAADwOAAA8JAAAPDoAADxtAAA8wgAAPSAAAD02AAA9qQAAPgoAAD6AAAA+6wAAP1MAAD9pAAA/fwAAP/YAAEBdAABA3wAAQUwAAEG3AABBzQAAQeMAAEH5AABCDwAAQiUAAEKIAABDCwAAQ6EAAERC",
    "AABEWAAARM8AAETlAABE+wAARYsAAEWnAABFvQAARdMAAEaZAABGrwAARsUAAEbbAABHygAAR+YAAEgZAABILwAASH8AAEiVAABIqwAASMEAAEjXAABI7QAASQMAAEkZAABJLwAASbYAAEnMAABJ4gAASfgAAEoO",
    "AABKJAAASroAAErQAABK5gAAS5gAAEu0AABLygAATIkAAEyfAABMtQAATVkAAE1vAABOKQAATj8AAE7wAABPBgAATxwAAE9vAABP3gAAUGMAAFDrAABRdQAAUZEAAFGnAABRvQAAUkQAAFJaAABScAAAUoYAAFKc",
    "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",
    "AACpsQAAqccAAKndAACp8wAAqgkAAKofAACqNQAAqksAAKphAACqdwAAqo0AAKqjAACquQAAqs8AAKrlAACq+wAAqxEAAKsnAACr5AAAq/oAAKwQAACsJgAArDwAAKzVAACtaAAArdYAAK3sAACuYwAArnkAAK6P",
    "AACupQAArrsAAK7RAACu5wAArv0AAK8fAACvOwAAr1cAAK9tAACviQAAr58AALABAACwgAAAsJYAALEFAACxpAAAsboAALHQAACx5gAAsfwAALIYAACy7QAAswMAALMfAACzNQAAs0sAALNnAACzgwAAs5kAALO1",
    "AACzywAAs+EAALP3AAC0DQAAtCMAALSJAAC0nwAAtLUAALTRAAC05wAAtY4AALWkAAC1ugAAtdAAALXmAAC2AgAAthgAALYuAAC2RAAAtt0AALbzAAC3CQAAt4oAALegAAC3tgAAt8wAALfoAAC3/gAAuMAAALjW",
    "AAC47AAAuVcAALltAAC5gwAAuZkAALmvAAC5xQAAudsAALnxAAC6BwAAuh0AALozAAC6SQAAul8AALp1AAC6iwAAuqEAALq3AAC6zQAAuuMAALr5AAC7DwAAuyUAALs7AAC7UQAAvGEAALx3AAC9EAAAvSYAAL08",
    "AAC9UgAAvWgAAL4vAAC+RQAAv0gAAL9eAAC/dAAAv4oAAL+gAADAJQAAwDsAAMBRAADAZwAAwN8AAMD1AADBCwAAwSEAAME3AADBTQAAwWMAAMF5AADCGAAAwi4AAMJEAADCtQAAwssAAMLhAADC9wAAww0AAMMj",
    "AADDOQAAw08AAMNrAADDxgAAw9wAAMPyAADECAAAxB4AAMQ0AADESgAAxGAAAMR2AADEjAAAxKIAAMS4AADEzgAAxOQAAMWJAADFnwAAxbUAAMXLAADF4QAAxfcAAMYNAADGIwAAxjkAAMZPAADGZQAAxnsAAMaR",
    "AADGpwAAxr0AAMbTAADG6QAAxv8AAMcVAADHKwAAx0EAAMe9AADIagAAyRsAAMm2AADJzAAAyeIAAMn4AADKDgAAyiQAAMo6AADKUAAAymYAAMp8AADKkgAAyqgAAMq+AADLLwAAy4gAAMueAADLtAAAy8oAAMvg",
    "AADL9gAAzAwAAMwiAADMOAAAzFQAAMxqAADMgAAAzJYAAMysAADMwgAAzN4AAMz0AADNCgAAzSAAAM02AADNTAAAzWIAAM14AADNlAAAzikAAM4/AADOqQAAzr8AAM9BAADP0QAA0E4AANBkAADQegAA0JAAANCm",
    "AADQvAAA0NIAANDoAADQ/gAA0RQAANEqAADRQAAA0dsAANHxAADSUAAA0w4AANMkAADTOgAA01AAANNmAADT9gAA1JMAANT2AADVDAAA1SIAANU4AADVTgAA1ewAANZ/AADXFgAA1ywAANdCAADYIQAA2DcAANlE",
    "AADZWgAA2g8AANpKAADadgAA2u0AANtpAADcCAAA3JYAANyzAADc7QAA3ScAAN1wAADdoAAA3ccAAN3lAADeAgAA3iEAAN58AADepQAA3vYAAN9fAADfpwAA3/8AAOBuAADgkwAA4RMAAOGAAADhrQAA4eMAAOIN",
    "AADiNQAA4l8AAOLNAADjhQAA48oAAOQ2AADkiQAA5NYAAOUGAADlLwAA5ZIAAOXAAADl8wAA5iYAAOZdAADmewAA5sYAAOcCAADnZgAA568AAOggAADodAAA6N8AAOkCAADpRgAA6XgAAOnZAADqFQAA6kMAAOpw",
    "AADqlwAA6rYAAOrcAADrBwAA6yIAAOtHAADrsgAA7BQAAOxhAADswgAA7R4AAO1nAADuGwAA7l8AAO6tAADvBwAA70IAAO9wAADv0gAA8BIAAPBrAADwzgAA8TIAAPFqAADxzQAA8hYAAPJYAADyjQAA8ugAAPMm",
    "AADzdwAA86QAAPQCAAD0HAAA9HsAAPSzAAD06QAA9U8AAPYzAAD2wwAA90MAAPfKAAD4VAAA+I0AAPi3AAD5fgAA+gQAAPpqAAD7FQAA+8AAAPx1AAD9JQAA/YMAAP3wAAD+ZwAA/tgAAP8wAAD/lgAA//cAAQBZ",
    "AAEAyAABAWcAAQHQAAECTAABAywAAQO/AAEENAABBHYAAQTZAAEFYAABBgoAAQbEAAEH6wABCEUAAQlKAAEJqgABCoUAAQsdAAELhAABDDMAAQyfAAENOQABDaMAAQ4wAAEOtQABDyEAAQ+ZAAEQggABEP0AARFR",
    "AAESDgABEpMAARMUAAETrgABFDUAARSzAAEVHAABFYwAARYVAAEWgwABFucAARdYAAEXvAABGHUAARjnAAEZTwABGdwAARplAAEbJwABG+4AARxVAAEclgABHMYAAR2sAAEd+AABHlYAAR6qAAEfZAABH/gAASBR",
    "AAEgawABIPoAASFGAAEiHAABIvoAASOfAAEkRQABJMkAASV7AAEl0gABJoYAASdMAAEn1AABKCcAASiTAAEpdAABKeEAASodAAEqqgABKvwAAStIAAEr/AABLJIAASzbAAEtPwABLa4AAS4oAAEuoAABLvoAAS+1",
    "AAEwcgABMMUAATEpAAExfQABMgQAATJZAAEzAwABM7oAATQyAAE0kwABNTwAATXGAAE2EQABNmsAATbFAAE3cgABN+cAATiZAAE4+gABOd4AATowAAE7XgABO5EAATwjAAE8pQABPPYAAT1YAAE9oAABPf8AAT6S",
    "AAE+7AABP5wAAUApAAFAaAABQPUAAUFvAAFB7wABQn8AAULVAAFDSQABQ7QAAURkAAFExwABRQUAAUWPAAFGLQABRuEAAUeRAAFH4AABSF8AAUiwAAFJJAABSZQAAUoFAAFKnQABSw0AAUt6AAFLzgABTCcAAUyh",
    "AAFNYAABTkYAAU7rAAFPfwABUGgAAVDKAAFRKgABUZoAAVJlAAFTFQABU9AAAVR8AAFVLgABVXYAAVXGAAFWQAABVrsAAVcbAAFXoAABWEwAAViUAAFY/wABWfgAAVqSAAFbIQABW4QAAVv1AAFcsQABXXAAAV4c",
    "AAFejwABXzkAAV+PAAFgNwABYNMAAWFbAAFhwAABYhkAAWJqAAFivQABYwAAAWODAAFj4AABZMkAAWVfAAFmGAABZk4AAWbfAAFnowABaGsAAWjOAAFpsgABangAAWrSAAFrJwABa1QAAWvAAAFr+wABbE8AAWyE",
    "AAFs1AABbX0AAW3mAAFudwABbwcAAW+MAAFvtAABcEAAAXBzAAFwpgABcRsAAXF9AAFx8wABcnIAAXMAAAFzjwABdFQAAXTvAAF1egABdfEAAXYkAAF2pAABdywAAXejAAF4JwABeNQAAXllAAF5ygABef0AAXot",
    "AAF6WgABeooAAXq6AAF7VwABe4cAAXu6AAF77QABfDEAAXzLAAF9QQABfaUAAX4AAAF+pQABfwQAAX+lAAGAZAABgL4AAYFIAAGBnAABghkAAYK4AAGDIAABg5QAAYQNAAGEUwABhRAAAYWdAAGF6wABhnsAAYa8",
    "AAGHEQABh9QAAYg6AAGIsgABiUgAAYnzAAGKYgABiuMAAYtlAAGL+AABjHgAAY0rAAGNrwABjoIAAY9KAAGP4AABkIoAAZD9AAGRtQABknIAAZLOAAGTXwABk8AAAZQkAAGUbgABlSYAAZWxAAGWLQABlrwAAZdm",
    "AAGXygABmGoAAZjlAAGZNgABmY8AAZqTAAGbWAABnF0AAZz+AAGdQgABncMAAZ4SAAGeoAABnycAAZ+TAAGgAgABoI4AAaDwAAGhXAABofEAAaJwAAGjMgABo5AAAaRLAAGkqAABpPsAAaU4AAGlowABphkAAaZ9",
    "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",
    "AAKB/gACgi8AAoLTAAKDaQACg5UAAoPBAAKEGAAChKwAAoUFAAKFXQAChdYAAoZEAAKHBQAChzYAAoerAAKIFAACiHoAAoi1AAKJHAACiZUAAopCAAKKyQACi3wAAowSAAKMlQACjPsAAo1nAAKN4AACjlQAAo8b",
    "AAKPcwACkBQAApB9AAKQzAACkXkAApHGAAKSEQACkmEAApLBAAKTJQAClCoAApSQAAKU3gAClSwAApWCAAKVzAAClhEAApaCAAKXRAACl6kAApg2AAKYhAACmNwAApksAAKZwAACmgsAAppMAAKakAACmx8AApuw",
    "AAKcOgACnJIAAp0kAAKdZwACnagAAp5DAAKerwACnyEAAp9pAAKf7wACoJYAAqFaAAKhqAACogIAAqJjAAKioQACoxUAAqN3AAKj0gACpB0AAqR1AAKkwAACpRUAAqVbAAKlzAACpi8AAqaGAAKm2AACp5EAAqgB",
    "AAKooQACqRkAAqmzAAKqEwACqmAAAqrUAAKrYQACrAcAAqw4AAKsxAACrS8AAq2OAAKuMgACrrAAAq7mAAKvOwACr8QAArAFAAKwRgACsNsAArEWAAKxTwACseUAArJGAAKyugACsvYAArNlAAKzxgACtFoAArSc",
    "AAK09QACtUQAArXEAAK2IAACtnMAArbkAAK3kgACt8kAArgHAAK4XAACuNIAArkNAAK5VAACuZsAAroKAAK6kAACuuYAArtaAAK7wAACvAgAArxGAAK8pQACvP0AAr1TAAK9yQACvgcAAr48AAK+wAACvyUAAr9n",
    "AAK/twACwAwAAsBgAALAngACwREAAsFVAALB6gACwkoAAsLUAALDVgACw8EAAsQfAALEnwACxQUAAsVBAALFoQACxd8AAsYdAALGogACxt4AAsdmAALIDQACyJ4AAsjfAALJGgACyVEAAsnMAALKEAACylQAAsq/",
    "AALLGgACy7IAAswMAALMxAACzTQAAs1yAALN6AACzlwAAs69AALPIAACz1kAAs+TAALP4wAC0DMAAtB/AALQ0gAC0SUAAtF4AALRqgAC0dgAAtIKAALSPAAC0qsAAtMcAALTkwAC09sAAtQqAALVTQAC1icAAtZ4",
    "AALWwQAC1x4AAteXAALYEwAC2IMAAtjrAALZUQAC2cQAAtoUAALa3gAC20YAAttGAALbqQAC3AMAAt0tAALeggAC3tsAAt80AALfnwAC3+4AAuBTAALgjQAC4MsAAuEGAALhkQAC4eoAAuKPAALjWAAC4/cAAuSc",
    "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",
    "JgfGAAAQJgYbAAAQBgTHAAD//wBo/0gHsAYYEiYHUAAAEAYHmAAA//8AaP9IB5gGGBImB+QAABAGB7IAAP//AGj/MAeoBjgSJgWeAAAQBgdQAAD//wBo/1AHmAZ4EiYHFwAAEAYFqgAA//8AaP+IB5gGIBImBxcA",
    "ABAGB0cAAP//AGD/QAeoBngSJgZcAAAQBgUVAAAAAQCA/5AHmAZ4AB4AAAEXBgchETMRIRUhESEVIREhFSE1IREhNSERIQYHJwAB+JgwSAHIoAK4/UgCaP2YAxj4+ANQ/ZgCaP3oWHCAAQAGODComAGw/lCY/kiY",
    "/kiYmAG4mAG4sIhoATgABQBY/0gHGAYYABgAHAAgACYAKgAAAREUBiMiJycWMzI1ESERIxEhAgMnNhIRERMhESEhESERASERIRUUJREhEQcYYGBgkCCYWED9+KD96CigmHhgoAIA/gACoAII+1ACCP4AAqACCAYY",
    "+iBwcBCgEHABWP3oAhj+sP7YYPABiAEQAuj+IAFI/rgBSPzYAUioUPj+uAFIAAUBAP9ABwAGeAALAA8AEwAXABsAAAERIzUhFSMRIREzEQEhESEhESERASERIQEhESEHAKj7UKgCqLD9UAIA/gACsAIA+1ACAP4A",
    "ArACAP4ABRD6MKCgBdABaP6Y/bABuP5IAbj8AAG4/kgBuAAFARD/OAbgBjAACwAPABMAFwAbAAABESM1IREjESEVIxETIREhIREhEQEhESEBIREhBuCg/gig/gigoAH4/ggCmAH4+3AB+P4IApgB+P4IBjD66ID9",
    "oAJggAUY/gABaP6YAWj8mAFo/pgBaAAFAND/aAegBngAHQAhACUAKQAtAAABESERFBYzMjcyNjcXBgcGISMiJjURIRUjESERMxEBESERIxEhERURIREzESERBpD9aFDgiJBwMBCwKFho/nBo4Ij+GKACiKAB+P4I",
    "oP4YAeigAfgFcPvo/wAwKAhQmEj4IChYYAE4aASAAQj++P5AASj+2AEo/tiY/tgBKP7YASgABwB4/0gHkAYwAAMABwALAA8AEwAXACMAABMhFSEFIREhEyERISERIREBIREhIREhEQEzESM1IRUjETMRIXgHGPjo",
    "AZAD4PwgmAEQ/vABqAEI/VABEP7wAagBCAE4qKj64KioBSAGMJiw/CACOAEg/uABIP0wASj+2AEoAdj6uICABVD7yAAHAGD/SAeYBjgADwATABcAGwAfACcAKwAAASERIRYFByQBIQIFJyQ3IRMhNSEhFSE1ASE1",
    "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",
    "AvgQ/OAwSOC4aLDIKNhAkAiYEJCQYP7YcP4w/oBIAjDwWCj9EBgCwCAQ/fgYAfggCKAQGAMYEP0AECAGmEhYMGBI/oCYWEhASFhwWEgoWMAoqJCAYIhImGBQaEBQmEhASDCQMHB4eGhAkEBAOAAEAGgCaAeYBpAA",
    "BQAPABUAGwAAARYXByYnJRcGByEVITUhNgEXBgUnJCUEBQckJQIomGCYWKAECLhgcAGw+agD8Hj9aHDA/mBQAVgDeAEwATBg/tD+0AaQgIhYiHhQOLiImJiw/niAuJCYaMhgwKDYaAAEAID/cAeABGAAAwAHAAsA",
    "GwAAASEVIQUhESE3ITUhExYXITY3FwYHIRUhNSEmJwK4ArD9UP7IBNj7KJgDqPxYaGBIAZhYMLAoWAII+QAB8DhIBGCQgP34kOj+YIiYgKA4aICQkHhoAAICSP9AB6AEwAASACgAAAERFDMzFSEiJjU1IQYGByc2",
    "NjUDIQIFFgUHJCUGBSckNyYnNxYXNjchBjhA4P74WFj+eBB4kGCIYIgD4CD+4OgBGFD+qP7o6P6gUAEoyJB4WJDg4Dj88ATA/thQiFBYwLioQHBAoOj9oP7Q0FAwoEB4cEigMEhYgHiYaHioAAIA6AMYBygGeAAR",
    "ACUAAAEXBgURJSc3FhcHJicGBycRJCEhAgIjIicnFjMyNhMhAgUnJBMjA0hw+P7AASBQgIBYkBgg4NBIAWABqAM4CICYKFAgYDBAOAj+6Aj+2HABAAjgBniAaDD+iHiISMDgQEhAcEhYAmA4/hj/ABCgEJgBIP54",
    "4HjQASAABQCgAcgHYAWQAB0AIwApAC8ANQAAARcGBzI3NjcXAgU2NyYnNxYXByYnBAUnNjcGByc2JRYXByYnJRcGByc2ARcGByc2JRYXByYnA6iQeGBwiEhAkOj+4MioICiAiGCQICj+0P6gKMCwiJgYqP4YgFiQ",
    "UIgF2IiIiHig+8B4kNh44ASoqJB4iKAFkCj4cBhQWDD+yNAgKDAwQKDIQFBISDCAeLAYEIjIQHCIUIBwWFCwaHB4/vBYsJh4mHhgiJCgaAADAGgBGAeIBngAGwAwADYAAAEXByECASckEyEGBxYXByYnBgcWFwcm",
    "JwYHJwAlITY1MxQHIRUhEgUHJAMCBSckEyEBFhcHJicB+JA4AahI/YhgAgho/tAQGIBoaGBoGCCAaGhoeBgoaAEAApgBKAiYCAGI/rBIAUho/vCAaP6ASAGIMP7oAohgWIBIYAZ4KJj8qP64kPACkCAgSGBwWEAw",
    "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",
    "kDBAiFBoiMgGiDBYiEBAUGhogGBguNgwKDCIWFBQWHBYYKgAAgBoBJgHkAaIAA8AIAAAARcHIRUhFhcHJicjBgcnNiUXBgchFSEXByYnIxUGByc2AbigMAHQ/wBAOJBAWIBggIDwA6CYEBgCKP7AcIhIWJBYcIDY",
    "BogwWIhAQFBoaIBgYLjYMCgwiIBQaGgIgFBgsAADAID/mANYBngAGQAdACEAAAEWFwc0JwYFJzY3ESERIREzESERIRE2NyYnExEjESMRIxEC8EggmAj4/tgYkHj/AAEAmAEI/vhAOBAgKHCYaAF4wNAoMDBQOJgY",
    "IAGoAwABaP6Y/QD+eBAYWFABSAHg/iAB4P4gAAQAkP+YArgF8AAHAAsADwATAAABESM1IxUjERMzESMRMxEjETMRIwK4mPiYmPj4+Pj4+AXw+gBIoAZY/kgBKP0gASj9IAEoAAQAoP+YAtAF8AAHAAsADwATAAAB",
    "ESM1IRUjERMhESERIREhESERIQLQmP74kJABCP74AQj++AEI/vgF8PnYcKAGWP5IASj9IAEo/SABKAAEAtj/SAewBjgAFAArAEAAVgAAASECBxYXBycGByc2NyYnNxYXNjchJSECBxYXByYnBwYGByc2Nyc3Fhc2",
    "NyEBIQIHFhcHJicGByc2NyYnNxc2NyElIQIHFhcHJicGByc2NyYnNxYXNjchA0ACCBhoSEBgeHiYSKBIaGhgYGAoIP6gAkAB6BhoYFBoUFBYGGBASIhgyGBgYDAY/sD96AHAGFBYSFhISJDAUMhoWFhgkCAQ/vAB",
    "+AIQGKBYoGiIaFh4UHBYeCCQGEhQGP6gBjj+8LA4OHhwmFCAUGhQQGg4QFCIkP7gsEhYeFBIYCA4IIBIcJBoOEhgiP1A/vC4UFh4WEDgaIhoyFBAaHBgaJD+gPBwUHBAcGhIiEBouMAokIiYwAAEAxj/QAeoBmAA",
    "BQA1ADoAQAAAARcEBScgBRYXITY3FwYHMxUhByEVIQYHIRUGBxYXByYnBgcnNjcmJwYHJxITIzUhNyE1MyYnARYXNjcBFhcHJicHKFD+cP24MAHg/uhgOAFIaDCoOGCo/dAYAnj9aBAYAkBIgJDIUOCowPhI4Jhw",
    "UGCQgPBY+AEYEP8AoDBAAThQgHBA/vhIMHgoSAZgiFAYkLhwgKCoMJCIiJiQUECIyHhIMJhAcHg4mChYaIDIqGABKAFQkJiIWEj8mIhgWJAD0FBYSFhQAAECMP9IB5gGeAAWAAABFwYHIRUhESEVIREhFSERIxEj",
    "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",
    "ABcAX0A9NBIBJRIBBhIWEgISlhYWDjQCASUCAQYCFgICApYGBjQKASUKAQYKFgoCCpbgDvAOAg4OGBkQAAibFAQMqAA/MzPhMjIREgE5L13hXV1dMy/hXV1dETMv4V1dXTEwNzIVFCMiNTQhMhUUIyI1NCEyFRQj",
    "IjU0zX9/fwIYf39/Ahl/f3/6i4yMi4uMjIuLjIyLAAMARgGRBIUEDgATAB0AJwBfuQAQ/+CzCQxIDrj/4EAyCQxIBiAJDEgEIAkMSB4KABQEBSOrDw8BDykZqwUmFq4KAAIMCAggHK4SPwKPAt8CAwIAL10z4TIz",
    "LzMSOTnhMgEv4RDeXeERFzkxMCsrKysBBiMiJjU0NjMyFzYzMhYVFAYjIgMmIyIGFRQWMzI3FjMyNjU0JiMiAmJ2mneVlXembHSldpKXcau1Um1BUFBDaORWa0FQVEBnAm3Vro2GtdvVrI+DuQFCuGtPUWWyuW1O",
    "T2cAAAAAAA8AugADAAEECQAAARYAAAADAAEECQABADABFgADAAEECQACAA4BRgADAAEECQADACoBVAADAAEECQAEADABFgADAAEECQAFACQBfgADAAEECQAGACoBogADAAEECQAHAJwBzAADAAEECQAIACgCaAAD",
    "AAEECQAKAOACkAADAAEECQALADgDcAADAAEECQAMAFwDqAADAAEECQANAFwEBAADAAEECQAOAFQEYAADAAEECQASACYEtABEAGkAZwBpAHQAaQB6AGUAZAAgAGQAYQB0AGEAIABjAG8AcAB5AHIAaQBnAGgAdAAg",
    "AKkAIAAyADAAMAA3ACwAIABHAG8AbwBnAGwAZQAgAEMAbwByAHAAbwByAGEAdABpAG8AbgAuAAoAQwBvAHAAeQByAGkAZwBoAHQAIACpACAAMgAwADAAOAAtADIAMAAwADkAIABXAGUAbgBRAHUAYQBuAFkAaQAg",
    "AEIAbwBhAHIAZAAgAG8AZgAgAFQAcgB1AHMAdABlAGUAcwAgACgAaAB0AHQAcAA6AC8ALwB3AGUAbgBxAC4AbwByAGcALwApACAAYQBuAGQAIABRAGkAYQBuAHEAaQBhAG4AIABGAGEAbgBnAFcAZQBuAFEAdQBh",
    "AG4AWQBpACAATQBpAGMAcgBvACAASABlAGkAIABNAG8AbgBvAFIAZQBnAHUAbABhAHIAVwBlAG4AUQB1AGEAbgBZAGkAIAAtACAATQBpAGMAcgBvACAASABlAGkAVgBlAHIAcwBpAG8AbgAgADAALgAyAC4AMAAt",
    "AGIAZQB0AGEAVwBlAG4AUQB1AGEAbgBZAGkATQBpAGMAcgBvAEgAZQBpAE0AbwBuAG8ARAByAG8AaQBkACAAaQBzACAAYQAgAHQAcgBhAGQAZQBtAGEAcgBrACAAbwBmACAARwBvAG8AZwBsAGUAIABhAG4AZAAg",
    "AG0AYQB5ACAAYgBlACAAcgBlAGcAaQBzAHQAZQByAGUAZAAgAGkAbgAgAGMAZQByAHQAYQBpAG4AIABqAHUAcgBpAHMAZABpAGMAdABpAG8AbgBzAC4AQQBzAGMAZQBuAGQAZQByACAAQwBvAHIAcABvAHIAYQB0",
    "AGkAbwBuAFcAZQBuAFEAdQBhAG4AWQBpACAATQBpAGMAcgBvACAASABlAGkAIABpAHMAIABhACAAaAB1AG0AYQBuAGkAcwB0ACAAcwBhAG4AcwAgAHMAZQByAGkAZgAgAHQAeQBwAGUAZgBhAGMAZQAgAGQAZQBz",
    "AGkAZwBuAGUAZAAgAGYAbwByACAAdQBzAGUAcgAgAGkAbgB0AGUAcgBmAGEAYwBlAHMAIABhAG4AZAAgAGUAbABlAGMAdAByAG8AbgBpAGMAIABjAG8AbQBtAHUAbgBpAGMAYQB0AGkAbwBuAC4AaAB0AHQAcAA6",
    "AC8ALwB3AHcAdwAuAGEAcwBjAGUAbgBkAGUAcgBjAG8AcgBwAC4AYwBvAG0ALwBoAHQAdABwADoALwAvAHcAdwB3AC4AYQBzAGMAZQBuAGQAZQByAGMAbwByAHAALgBjAG8AbQAvAHQAeQBwAGUAZABlAHMAaQBn",
    "AG4AZQByAHMALgBoAHQAbQBsAEwAaQBjAGUAbgBzAGUAZAAgAHUAbgBkAGUAcgAgAHQAaABlACAAQQBwAGEAYwBoAGUAIABMAGkAYwBlAG4AcwBlACwAIABWAGUAcgBzAGkAbwBuACAAMgAuADAAaAB0AHQAcAA6",
    "AC8ALwB3AHcAdwAuAGEAcABhAGMAaABlAC4AbwByAGcALwBsAGkAYwBlAG4AcwBlAHMALwBMAEkAQwBFAE4AUwBFAC0AMgAuADAAVwBlAG4AUQB1AGEAbgBZAGkAIABNAGkAYwByAG8AIABIAGUAaQADAAAAAAAA",
    "/wAAZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAFAAL//wADAAEAAAAMAAAAAAAAAAIACAAAAMwAAQDOAQIAAQEEAWgAAQFqAXAAAQFyAqwAAQKuA6kAAQOrBH4AAQieCP4AAQABAAAACgAMAA4AAAAAAAAAAQAA",
    "AAoAFgAYAAFsYXRuAAgAAAAAAAAAAAAAAAEQAAVa94kAAAgA/0j56A4YAAAAAQAAAAAAAAAAAAAAAAABCAAFuAPABhgDwAYYBggGCAYIBggGCAYIBggE4ASwBFAEsATYBLgGAAYABkgAAAEwATgGYAZgBmAC4AZg",
    "BmADgAYIBeAGWAYIBhgGeAZ4BjAGeAZgBhgGOAZ4BoAGeAZ4BnAGiAZoBlAGeAZgBhAGeAZ4BgAGeAZ4BhAGiAZ4BZAGAAYIBggGeAaABmgGgAZQBngGeAZ4BoAGeAaABoAGeAZ4BoAGeAaABngGeAZ4BngGeAZ4",
    "BogGgAZ4BngGeAZ4BoAGeAZ4BngGeAaABngGeAaABngGeAZ4BngGeAZ4BngGiAaABngGiAZ4BngGeAaABngGiAZ4BngGeAaABoAGeAZ4BfgGeAZ4BoAGeAZ4BogGWAZwBoAGcAZABogGiAaABmAGIAYwBngGeAZA",
    "BngGeAaIBoAGgAZ4BhAGQAZ4BngGKAYYBhAGcAZ4BnAGeAZ4BoAGcAZ4BngGcAZ4BngGcAZ4BoAGkAZwBngGgAaIBnAGeAZ4BngGiAZ4BngGeAaIBngGOAZ4BlAGeAaABogGeAZ4BngGgAYABngGeAY4BjgGOAY4",
    "BngGgAYQBjAGEAZ4BnAGOAZ4BngGYAXgBngGCAZ4BhgGCAaABngGMAaABogGkAY4BngGaAaABjgGgAZoBoAGMAZABkgGQAaQBoAGKAaIBpAGWAYoBoAGgAaABoAGeAZ4BkAGiAY4BjgGCAY4BjgGOAY4BjgGOAY4",
    "BiAGgAZ4BlgGYAaABlgGgAZ4BngGYAZYBngGeAaIBogGgAaIBoAGeAaIBoAGeAZwBoAGeAZ4BngGeAaABpAGeAZ4BngGgAZ4BngGgAaABjAGiAaABogGiAaIBpAGiAaIBogGiAaIBogGiAaIBogGiAaIBogGeAZ4",
    "BjgGgAZ4BnAGaAZoBngGeAYYBkgGSAZIBkgGSAZIBngGeAYIBngGMAaQBiAGCAaIBoAGeAZ4BngGeAXwBigGiAaABoAGgAaABoAGgAaABoAGEAZwBngGIAZABngGeAZoBngGcAZABngGgAZIBmgGaAaABngGeAaA",
    "BoAGeAZ4BngGeAaABmAGYAZ4BngGeAZ4BoAGIAZ4BoAGeAZ4BpAGeAZ4BngGgAaQBogGeAZ4BngGgAaABoAGeAaABngGeAZ4BmAGeAaABngGeAZ4BngGeAZ4BoAGeAZ4BngGOAZ4BngGeAZ4BngGeAZ4BngGeAaA",
    "BoAGeAZ4BngGgAaABngGgAZ4BngGeAZ4BngGgAaIBogGgAZ4BngGeAZ4BngGiAZ4BngGeAaABngGeAZ4BoAGeAZ4BoAGgAZ4BngGeAZ4BngGgAZ4BngGeAZ4BngGgAaABngGkAZ4BoAGeAZ4BngGgAZ4BngGeAaA",
    "BngGeAaABnAGgAZ4BoAGeAZ4BngGiAaABngGGAYgBiAGGAY4BngGSAZQBkgGeAZQBjAGeAZIBoAGYAaIBlAGOAZ4BkAGSAaABkgGeAZ4BngGeAaABnAGQAZ4BogGeAZ4BngGeAaIBngGeAZ4BngGMAaABoAGgAaA",
    "BngGeAZ4BngGgAZ4BoAGeAZ4BngGeAZ4BngGgAZ4BngGgAZ4BngGeAZ4BoAGiAZ4BhAGcAaABfAGeAYwBoAGeAZgBogGeAaIBogGaAZoBmgGaAZwBnAGgAZ4BoAGeAZ4BngGeAZoBoAGeAaABoAGgAaABmgGeAZo",
    "BmgGeAZ4BngGeAZwBlgGaAaABngGaAZYBngGeAZ4BngGWAaABngGeAaABngGMAZ4BngGgAZoBngGeAYwBngGgAaABngGgAaABoAGgAaABoAGgAYYBhgGOAZ4BiAGeAZ4BhgGeAYwBngGMAY4BngGgAaQBogGiAaQ",
    "BngGgAYQBngGeAaQBpgGeAZ4BoAGgAYgBngGeAZ4BnAGeAZgBngGKAZIBogGeAZ4BnAGgAZ4BngGeAYwBigGeAY4BngGMAZ4BngGeAZABggGgAaABogGeAaQBoAGgAaABngGgAaABmgGgAaABogGiAaQBogGiAaA",
    "BngGeAaABngGiAaIBogGiAaIBogGiAaIBogGiAaIBogGiAZ4BogGeAZ4BmgGeAaABlgGeAZIBngGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BogGgAZ4BngGeAZ4BngGeAaABngGgAaABigGUAZQBoAGcAZ4",
    "BoAGKAZ4BjAGMAZwBkgGSAZ4BngGgAaABoAGeAZIBkgGgAaABhgGeAZIBoAGgAZ4BngGgAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGiAY4BogGgAZ4BoAGeAZ4BngGeAaABoAGeAZ4BngGeAZwBnAGOAZABlgGIAYw",
    "BngGiAaIBogGoAaABoAGgAZ4BngGeAaABngGeAZ4BngGeAZ4BngGgAZ4BngGeAZ4BoAGeAZ4BogGeAaABngGoAaABngGiAZ4BmgGaAZABngGeAZ4BoAGgAZ4BngGeAZ4BoAGMAZYBoAGMAZIBoAGYAZwBogGgAaA",
    "BoAGeAaABngGeAZ4BngGgAaABkgGeAZIBnAGSAZoBngGSAaABnAGSAaABkgGeAaABkgGiAZgBngGYAZIBoAGSAaABngGSAZ4BoAGeAYYBoAGeAZABkgGcAY4BlgGUAaABngGeAZ4BngGeAaQBoAGeAZ4BngGeAaI",
    "BnAGkAaQBpAGkAaQBpAGeAZIBngGgAYwBoAGSAaABngGcAZ4BjAGgAZgBlgGYAZwBnAGeAaIBngGgAYoBogGOAY4BjgGeAZIBjgGaAY4BlAGUAZ4BngGMAZIBfgGkAaABogGgAaABoAGaAZIBjgGeAY4BmAGUAaI",
    "BpAGgAaIBkAGgAaABoAGeAW4BbgFuAYQBcgF0AW4BbgFuAYYBKABMAMoATAFuAXQBbgFyAXIBcAFuAXIBbgF0AXIBCAEIATgA+gE4AXIBbgFwAW4BcgFuAW4BbgFyAW4BbgFuAW4BbgFuAW4BdAFuAXQBbgFyAW4",
    "BbgFuAW4BbgFuAW4BbgFuAW4BcD/SAYgBGAGGARgBhgEYAYgBGAGGAYQBhAGGAYYBGAEYARgBGAEYARgBGAFcARIBEgESARIBEgESAW4BhgFuANYAngGgANoAygDYAZwBTAEaAQIBoAGSAZ4BkgGgAYwBmAGMAaA",
    "BnAGgAYgBkAGcAY4A+AGgAYoBXAFGAYgA9AGiAZAA+AE4AZ4BoACKAUgBKgFYATYBMAE2ARIBQAE2ARABIgGeAZ4BkgE6AZIBLgEmARYBIAEeARABGAGeAQIA8AEyAZ4BngGmAaQBGAEwAZ4BZAGeAaABngGWAYo",
    "BngGaAaABngEiAKwBfgGIAOoBoAGcAZwBkAGUANIBkgESAaIBngGgAZ4BngGcAZ4A2gGQAZwBPgFEATwBEgFCASwBSgEeAQwBIAEiAOQA5AECAY4BNgEmAUABPgFAATQBJADuARwBpAEmATgBiAFeAXoBngCSAWI",
    "BVAFCAJwBoAGcAYoBTAGeAZ4BoAFAAZ4AvAGOAYgBoAGaAaQBngGeAYgBngGgAaABngGeAZgBngGiAaIBngGOAYwBoAGOAaABoAGeAaABngE0AL4BjgGMAZ4BngGQAZ4BoAGCAZYBlAGSAaIA0AGgAXwBmgGcAYg",
    "BngGeAZ4BoAGiAZ4BhgGeANIBoAGeASYBoAGiAZIBigDQAZ4AxgGgAZ4BngFqAZABogGeAKQBngGiAJ4AggGgAZABngGGAZIAggGcAaABjgGOAZ4AagGeAKgAggGgAYABngGgAY4BjgGcAYYBlAC2AXQBoAGgAZ4",
    "BngGgAY4BngF2AXIBcgFwAXABoAFyAXIBcgCGAZ4A2gGeALYBmAGgAY4BkgGSAZ4BXAGEAZ4BjgGeAY4BoAGeAZ4BngGOAYYBjAGeAYwBoAGeAZ4BngGeAZ4BngGeAZIBigGeAaABngGQAZwBogGeAYYBngCWAXo",
    "AYAGgAZ4BngGgAZ4BhAGeAZ4BiAGEAaABkgGgAYwBngGKAYYBngGgAZ4BjgGgAYIBngGeAaABngGeAZ4BngGgAXgBkgGeAYABnAGEAZ4BjgGeAXoBngGeAaABngGQAaIBngGeAZ4BjAGeAaABngGMAZ4BngGOATo",
    "BngGeAZQBjgGcAZwBogGeAYwBngGeAZ4BngGeAZ4BhgGgAaABigGgATIBngGEAToBngGgAZABoAGeAZ4BnAGKAaABoACCATwBoAGeAYwBngDeANYBnAGcAYwBngGeAZgBngGgAJoBogE6AXoAUgGeAZwBoAGCAZ4",
    "BngGWAaABBAGeANoBggGMAaAAqgGMAX4BigGeAZAAtgGYAZ4BNgE2AZ4AwAGaAaABmgGiAaABoAGgAZ4BoAGeAYoBkAEuAYgBigGgAZ4BngGeALgBngGiAZ4BogGcAZwBlAGgAZ4BkgGgAUYBmAGeAT4BmgGWAZY",
    "BngGYAZgBmgGOAYYBngDIAaABngEiAZYBngGeAZ4BnAGiAEgBoAGQAaIBogGeAZ4BngGiAZ4BIgGkAZ4BoAGOAYYBhgGWAYwBOgF+AZoBoAGgAaABoAGeAZABoAGeAJQBoADqAZ4BhgGgAYgAwAGYAZ4BngGOAZo",
    "BngGeAZ4BngC4AaIBggGCAaABngDMAZ4BKAGgAZYBngGeAKgBnAGYAaABngGeAZ4A7gGeAYgBoACqAYIBoAGkAZYBogGKAYwBcgFMAVoBjAGgAZ4BngGWAK4BogGiAJwAqgGMAY4BjgGQAYwBngGaAR4BjgGUAYY",
    "BEgGMALQBgAGCAZwBnAGcAZoBoAGUAZwBjAGeAZ4BUgGeAZ4BDAGgAZgBngGeAZ4BngEgAZ4BjAGMAKQBkAGeAaABoAGOAXgAigGiAR4AXgFeAVYBWAGUAZABjAGEAaIBjgGCAZ4BngGeAY4BogEMAYQBogGeAZ4",
    "BlgGeAZ4BoAGcAZwBngGcAZ4BggGeAaABoAGGAXIBfgGeASYBngCGAQwBjgGeAZ4BngGeAYoBjgGIAZ4BoAGeAZ4BkgGIAaABngGEASABjgF+AZIBfgGEAZwBFAGcAZAA5gGgAaABngE8AZ4BngGeAY4BlAGOAZQ",
    "BjgGeAZ4BngGeAZIBDgGgAZIBngGeAZ4AkgFSAZQBmgGeAY4BiAGeALwAqAGEAYQBogGgAaABoAGiAaQBoAGcAZ4BnAGGAaIBoAGOAXwBngGeAaIBoAGeAIgBoAGeAZ4BngGgAZIBjgDgAZABlAGGAY4BoAGIAZ4",
    "BngGAAZwBngGeAZ4BogF4AaABoAGeAY4BlgGWAZ4BoAGSAZ4BigGeAZ4BhgGMAZ4BngGUAZoBmAGgAYIBhgGIAYAAdgGQAYwBkgGeAYgBngGgAaABhgGgAYYBhgGSAZwBoAGeAZ4BlgGgAYABnAGaAZ4BoAGUAaA",
    "BkgGSAZIBngGcAaABmgGeAZoBjAGeAYQBngGcAaABngGQAYgArgGSAPQBoADkAaIAsAGeAYYBngGGAZoAygGeAaABoAGgAaABjgGeAZ4BlgGWAaQAxAGOAYgAeAGeAZ4BngGEAYQBnADkAaIBoAGgALgBmgDIAYQ",
    "BngGeAaABlgGiAZ4BngGcATIAMAGMAYgBoAGaAZ4BoACsAZ4BoAEeAaIBfgESAZIBkgGgAZ4BngGeAZ4BngGIAZ4A6AGaAaABngGeAZ4BngGeAMwA4AGQAZ4BigGcAYABngGeAZwBngCeAZ4AygGeAZ4BigGiAJA",
    "BogGeAZ4BmgGeAYwBngGEAZ4BngGeAZ4BoAGcAYwAbAGeAYIBngGeAZ4AOgGeAZ4ATgGAAaQBngGiAXgBeAGMAZ4BngGeAY4BoAGcAZoBngGgAYIBngGeAZ4BngGQAZABjAGMAJoAcgCIAJABngGeAZ4BngGiAaI",
    "BngF8AXwBjgGYAZ4BngGeAZgBlgGiAZ4BngGSAZoBoAGgAAABbYFtgW2BccFtgW2BhQEogEGAnkBLQW2Bc0FtgXLBcsFvgW2BcsFtgXNBcsEZgRmBMkD6QTJBcsFtgW8BbYFywW2BbYFtgXLBbYFtgW2BbYFtgW2",
    "BbYFzQW2Bc0FtgXLBbYFuAW2BbYFtgW2BbYFtgW2Bbb/SAYhBF4GFAReBhQEXgYfBF4GFAYOBg4GFAYUBF4EXgReBF4EXgReBF4FbwRKBEoESgRKBEoESgW2BhQFtgNaBcUDXgR7AnkA+gQO",
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
