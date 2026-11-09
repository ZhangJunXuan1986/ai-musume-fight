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
VERSION = "v3-skills"

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
KEYS_P1 = {
    "left": K_a, "right": K_d, "up": K_w, "guard": K_s,
    "atk": K_j, "jump": K_k, "dash": K_l, "far": K_u,
    "ult": K_i, "assist": K_o,
}
KEYS_P2 = {
    "left": K_LEFT, "right": K_RIGHT, "up": K_UP, "guard": K_DOWN,
    "atk": K_1, "jump": K_2, "dash": K_3, "far": K_4,
    "ult": K_5, "assist": K_6,
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
# 键盘备用键（避开原有 WASD/JKL/UIO、方向键 1~6、GLOBAL 的 R/C/P）
ACTION_KEYS_P1 = {
    "s1": K_q, "s2": K_e, "s3": K_z, "ult": K_x,
    "dodge": K_v, "cleanse": K_b, "scroll": K_n,
}
ACTION_KEYS_P2 = {
    "s1": K_7, "s2": K_8, "s3": K_9, "ult": K_0,
    "dodge": K_MINUS, "cleanse": K_EQUALS, "scroll": K_LEFTBRACKET,
}
ACTION_BY_KEY = {}
for _a, _k in ACTION_KEYS_P1.items():
    ACTION_BY_KEY[_k] = (_a, 1)
for _a, _k in ACTION_KEYS_P2.items():
    ACTION_BY_KEY[_k] = (_a, 2)

# ---- 火影手游式按键几何（右侧技能簇基准，镜像给左侧）------------------------
# 设计原则：所有键都压在屏幕两侧下缘，中间 400~1000 完全留给战斗画面。
CLUSTER_R = [
    # 标签,    圆心x, 圆心y, 半径, 动作,      持续按住
    ("攻",     1130, 636, 34, "atk",     ()),
    ("技1",    1050, 598, 25, "s1",      ()),
    ("技2",    1092, 554, 25, "s2",      ()),
    ("技3",    1146, 550, 25, "s3",      ()),
    ("奥义",   1200, 592, 27, "ult",     ()),
    ("闪避",   1032, 660, 23, "dodge",   ()),
    ("净化",   1082, 668, 23, "cleanse", ()),
    ("秘卷",   1182, 664, 25, "scroll",  ()),
]
CLUSTER_L_OFFSET = 120     # 左侧簇整体右移，避开左下摇杆
CLUSTER_PVP_STICK_SHIFT = 130  # PVP 且强制显示摇杆时，两簇往中间挪，避免与摇杆重叠
STICK_RADIUS = 52          # 固定摇杆底盘半径（缩小，少挡画面）
STICK_P1_CENTER = (110, 630)
STICK_P2_CENTER = (1170, 630)
ROUND_LABELS = set(ACTION_LABELS)
TOUCH_ALPHA = 132          # 更透明，尽量不遮画面


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
    """右上角菜单键（主页面 / 选人 / 设置 / 战绩页可用）。
    y=40 是为了避开手机状态栏，避免像截图里那样把 HUD 挡住。"""
    gx, gy = TOUCH_GLOBAL_X, TOUCH_GLOBAL_Y
    gw, gh, gap = TOUCH_GLOBAL_W, TOUCH_GLOBAL_H, TOUCH_GLOBAL_GAP
    spec = [
        ("确",  (GLOBAL_KEYS["confirm"],)),
        ("退",  (GLOBAL_KEYS["cancel"],)),
        ("上",  (pygame.K_UP,)),
        ("下",  (pygame.K_DOWN,)),
        ("左",  (pygame.K_LEFT,)),
        ("右",  (pygame.K_RIGHT,)),
        ("再",  (GLOBAL_KEYS["restart"],)),
        ("清",  (GLOBAL_KEYS["clear_stats"],)),
    ]
    return [_btn(gx + i * (gw + gap), gy, gw, gh, lab, (), tap)
            for i, (lab, tap) in enumerate(spec)]


def build_mid_buttons():
    """战斗页中间区：AI 开关 / 暂停 / 返回 / 再战。
    不放在右上角，是因为那里要留给 P2 的血条和气条。"""
    w, h = TOUCH_MID_W, TOUCH_MID_H
    return [
        _btn(TOUCH_MID_X1, TOUCH_MID_Y1, w, h, "电脑：关", (), ()),
        _btn(TOUCH_MID_X2, TOUCH_MID_Y1, w, h, "暂停／继续", (), (GLOBAL_KEYS["pause"],)),
        _btn(TOUCH_MID_X1, TOUCH_MID_Y2, w, h, "返回",     (), (GLOBAL_KEYS["cancel"],)),
        _btn(TOUCH_MID_X2, TOUCH_MID_Y2, w, h, "再战",     (), (GLOBAL_KEYS["restart"],)),
    ]


def build_skill_cluster(side, mirror=False, shift=0):
    """v3 火影手游式技能簇：8 个圆键，全部压在屏幕一侧下缘。
    side 决定动作归属（PVE 时右侧簇也归 P1）；tap 直接发 (action, side) 元组，
    不占用 pygame 键码，键盘与触屏共用同一套 dispatch_actions。
    shift>0 时整簇往画面中间挪，给 PVP 强制显示的双摇杆让位。"""
    out = []
    for lab, cx, cy, r, act, holds in CLUSTER_R:
        if mirror:
            cx = SCREEN_W - cx + CLUSTER_L_OFFSET + shift
        else:
            cx = cx - shift
        out.append(_btn(int(cx - r), int(cy - r), r * 2, r * 2,
                        lab, (), ((act, side),)))
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

    def _do_jump_dash(self, game, just, k):
        """跳跃与冲刺：两个独立判定，顺序与原版一致。"""
        if k["jump"] in just and self.y >= GROUND_Y - 1:
            self.vy = JUMP_V
            self.state = "jump"
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
        self._do_jump_dash(game, just, k)
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
        self._rebuild_buttons()

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
        self.menu_items = ["开始对战", "角色选择", "对局设置", "P1 / P2 战绩", "退出游戏"]
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
        """当前页面可点的按钮列表（战斗页多加左右两组和中间区）。"""
        if self.scene == "game":
            # 战斗页右上角是 P2 血条/气条，不能盖；返回/再战/暂停都在中间区
            return self.left_btns + self.right_btns + self.mid_btns
        out = list(self.global_btns)
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
        pos = self.to_canvas(*phys)
        self.mouse = pos
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
        # 中间的「电脑：关/开」按钮单独处理，不映射成键盘
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
        """把虚拟按键画到虚拟画布最上层（缩放后一起贴到手机屏幕）。"""
        if self.selftest or not MOBILE_TOUCH:
            return
        btns = self.active_buttons()
        layer = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        naruto = (TOUCH_STYLE == "naruto" and self.scene == "game")
        # 先画两个「永远不动」的摇杆底盘（火影手游式）
        if naruto and self.move_ui_visible():
            for side in self.visible_sides():
                c = STICK_P1_CENTER if side == 1 else STICK_P2_CENTER
                pygame.draw.circle(layer, (18, 22, 52, TOUCH_ALPHA), c, STICK_RADIUS)
                pygame.draw.circle(layer, (140, 164, 235, 190), c, STICK_RADIUS, 3)
                pygame.draw.circle(layer, (70, 82, 140, 120), c, STICK_RADIUS - 14, 2)
                ox, oy = self._stick_offset(side)
                knob = (int(c[0] + ox), int(c[1] + oy))
                hot = any(sd == side for sd, _d, _e in self.stick_hits.values())
                kc = (110, 214, 255, 235) if hot else (86, 176, 235, 210)
                pygame.draw.circle(layer, kc, knob, STICK_KNOB_RADIUS)
                pygame.draw.circle(layer, (232, 246, 255, 240), knob, STICK_KNOB_RADIUS, 3)
        for rect, label, _h, _t in btns:
            hot = rect in [b[0] for b in self.touch_hits.values()]
            fill = (70, 90, 170, TOUCH_ALPHA + 40) if hot else (26, 30, 64, TOUCH_ALPHA)
            if naruto and label in ROUND_LABELS:
                c, r = rect.center, min(rect.w, rect.h) // 2
                pygame.draw.circle(layer, fill, c, r)
                pygame.draw.circle(layer, (150, 170, 240, 200), c, r, 2)
                size = 18 if r >= 26 else 15
            else:
                pygame.draw.rect(layer, fill, rect, border_radius=9)
                pygame.draw.rect(layer, (150, 170, 240, 200), rect, 2, border_radius=9)
                size = 19 if rect.w >= 90 else 15
            draw_text(layer, label, rect.centerx, rect.y + (rect.h - size) // 2 - 1,
                      size, COL_TEXT, True, "center", shadow=False)
            # v3：技能键上画一圈 CD 冷却弧；秘卷 / 闪避 / 净化同样显示
            if naruto and label in ROUND_LABELS:
                for _b in btns:
                    if _b[1] == label and _b[3]:
                        act = _b[3][0]
                        if isinstance(act, tuple):
                            a, side = act
                            f = self.p1 if side == 1 else self.p2
                            if f is None:
                                break
                            cd = {"s1": f.cd_s1, "s2": f.cd_s2, "s3": f.cd_s3,
                                  "ult": f.cd_ult, "dodge": f.dodge_cd,
                                  "cleanse": f.cleanse_cd, "scroll": f.scroll_cd}.get(a, 0)
                            full = {"s1": 96, "s2": 186, "s3": 252, "ult": 600,
                                    "dodge": DODGE_CD, "cleanse": CLEANSE_CD,
                                    "scroll": SCROLL_CD_FALLBACK}.get(a, 1)
                            if cd > 0:
                                rr = min(rect.w, rect.h) // 2 + 3
                                pygame.draw.arc(layer, (255, 120, 120, 230),
                                                (rect.centerx - rr, rect.centery - rr, rr * 2, rr * 2),
                                                math.pi / 2,
                                                math.pi / 2 + 2 * math.pi * (cd / float(full)), 3)
                        break
        if self.scene == "game":
            if naruto:
                hy = SCREEN_H - 26
                pygame.draw.rect(layer, (14, 16, 36, 175),
                                 (SCREEN_W // 2 - 280, hy - 4, 560, 24), border_radius=8)
                tip = ("PVE · 单人打电脑   左下摇杆 / 右下技能   中间：暂停 / 返回 / 再战"
                       if self.mode == MODE_PVE else
                       "PVP · 本地双人   左右各一套摇杆与技能   中间：暂停 / 返回 / 再战")
                draw_text(layer, tip, SCREEN_W // 2, hy, 14, COL_GOLD,
                          align="center", shadow=False)
            else:
                pygame.draw.rect(layer, (14, 16, 36, 175),
                                 (SCREEN_W // 2 - 240, 538, 480, 28), border_radius=8)
                draw_text(layer, TOUCH_HINT, SCREEN_W // 2, 543, 16, COL_GOLD,
                          align="center", shadow=False)
        s.blit(layer, (0, 0))

    # ---- 通用工具 ----
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
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                self.just.add(ev.key)
                act = ACTION_BY_KEY.get(ev.key)
                if act:
                    self.just.add(act)
            elif ev.type == pygame.MOUSEMOTION:
                self.mouse = self.to_canvas(*ev.pos)
                if -1 in self.stick_hits:
                    self._stick_update(-1, self.mouse)
                if -1 in self.swipe:
                    side, x0 = self.swipe[-1]
                    d = self.mouse[0] - x0
                    self.swipe_dir[side] = 1 if d > 18 else (-1 if d < -18 else 0)
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                self.on_touch_down(-1, ev.pos)
            elif ev.type == pygame.MOUSEBUTTONUP:
                self.on_touch_up(-1)
            elif ev.type == FINGER_DOWN:
                # ev.x / ev.y 是 0~1 归一化坐标
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
        return pygame.Rect(SCREEN_W // 2 - 190, 300 + i * 62, 380, 48)

    def _do_menu(self, i):
        if i == 0:
            self.start_match()
        elif i == 1:
            self.lock = {1: False, 2: False}
            self.scene = "select"
        elif i == 2:
            self.scene = "settings"
        elif i == 3:
            self.scene = "stats"
        elif i == 4:
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
        """双方不许穿模：重叠时朝两侧轻轻推开。"""
        d = self.p2.x - self.p1.x
        if abs(d) < BODY_W * 0.7:
            push = (BODY_W * 0.7 - abs(d)) / 2.0 * (1 if d >= 0 else -1)
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

        draw_text(s, "AI娘大乱斗", SCREEN_W // 2, 168, 76, COL_TEXT, True, "center")
        draw_text(s, "AI MUSUME FIGHT  ·  本地双人格斗  ·  3 格气 / 变身 / 援助",
                  SCREEN_W // 2, 248, 21, COL_GOLD, False, "center")

        for i, label in enumerate(self.menu_items):
            r = self._menu_rect(i)
            hot = (i == self.menu_idx)
            draw_panel(s, r, COL_PANEL_LIGHT if hot else COL_PANEL,
                       COL_GOLD if hot else COL_PANEL_LIGHT, 12, 2 if hot else 1)
            draw_text(s, ("▶  " if hot else "   ") + label,
                      r.x + 28, r.y + 10, 26, COL_GOLD if hot else COL_TEXT, hot)
        # 当前设置摘要
        info = "时间 %s   |   血量 %s   |   训练模式 %s   |   P1: %s   P2: %s" % (
            TIME_LABELS[self.time_idx], HP_SCALE_LABELS[self.hp_idx],
            "ON" if self.training else "OFF",
            CHARACTERS[self.sel[1]]["short"], CHARACTERS[self.sel[2]]["short"])
        draw_text(s, info, SCREEN_W // 2, SCREEN_H - 76, 18, COL_DIM, align="center")
        draw_text(s, "手指点按菜单 · 右上角「确」确认 /「Esc」返回", SCREEN_W // 2,
                  SCREEN_H - 50, 16, COL_DIM, align="center")

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
        draw_text(s, "右上角 ▲▼ 选行 · ◀▶ 改值 · 确 / Esc 返回",
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
        """键盘提示条：手机触屏版底部让给虚拟按键，仅在 MOBILE_TOUCH=False 时画。"""
        if MOBILE_TOUCH:
            return
        bar = pygame.Rect(0, SCREEN_H - 58, SCREEN_W, 58)
        pygame.draw.rect(s, (12, 14, 30), bar)
        draw_text(s, "P1  A/D 移动  S 防  J 攻  K 跳  L 冲  U 远  I 必杀  O 援助",
                  14, SCREEN_H - 54, 15, COL_P1)
        draw_text(s, "P2  ←→ 移动  ↓ 防  1 攻  2 跳  3 冲  4 远  5 必杀  6 援助",
                  SCREEN_W - 14, SCREEN_H - 28, 15, COL_P2, align="right")

    def draw_hud(self, s):
        """战斗 HUD v3：左右两侧 → 状态徽章 / 秘卷 / 场地名 → 中央计时 → 键盘提示。"""
        self._draw_side_hud(s, self.p1, False, COL_P1, 36)
        self._draw_side_hud(s, self.p2, True, COL_P2, SCREEN_W - 36 - 480)
        # 状态徽章放在两侧、第 108 行，与中央文字错开，不互相压字
        draw_status_badges(s, self.p1, 36, 108)
        draw_status_badges(s, self.p2, SCREEN_W - 36, 108, "right")
        # 场地 / 机制 / 秘卷 / 模式：中央一行小字，放在计时牌下方
        arena = ARENAS[self.arena_idx % len(ARENAS)]
        eff = ARENA_EFFECTS[self.arena_effect]
        line = "%s  ·  %s  ·  %s  ·  秘卷 %s" % (
            "PVE" if self.mode == MODE_PVE else "PVP",
            arena["name"], eff["name"], self.scroll_id)
        draw_text(s, line, SCREEN_W // 2, 88, 16, eff["color"], align="center")
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
        draw_text(s, "右上角 R 再战一局      Esc 返回主页面", SCREEN_W // 2, 470, 26,
                  COL_GOLD, True, "center")


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
    all_keys = list(KEYS_P1.values()) + list(KEYS_P2.values())
    assert len(all_keys) == len(set(all_keys)), "P1/P2 按键存在冲突"
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
    expect_side = 8 if TOUCH_STYLE == "naruto" else 12
    assert len(lb) == expect_side and len(rb) == expect_side and len(gb) == 8 and len(mb) == 4
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
        assert len(lb) == 8 and len(rb) == 8, "摇杆布局应有 8 个圆键/侧"
        assert all(b[3] and isinstance(b[3][0], tuple) for b in lb + rb), "技能键必须发动作元组"
        assert STICK_P1_CENTER[0] + STICK_RADIUS < lb[0][0].left, "摇杆底盘压到技能键"
        assert STICK_P2_CENTER[0] + STICK_RADIUS <= SCREEN_W, "P2 摇杆越界"
        assert STICK_P1_CENTER[0] - STICK_RADIUS >= 0, "P1 摇杆越界"
        assert all(b[0].w == b[0].h for b in lb + rb), "圆键外接框必须是正方形"
    else:
        assert lb[0][0].x == TOUCH_P1_X0 and lb[0][0].y == TOUCH_Y0
        assert rb[0][0].x == TOUCH_P2_X0
        assert lb[0][0].w == TOUCH_BTN_W and lb[0][0].h == TOUCH_BTN_H
        assert lb[1][0].x - lb[0][0].x == TOUCH_BTN_W + TOUCH_BTN_GAP
        assert lb[4][0].y - lb[0][0].y == TOUCH_BTN_H + TOUCH_BTN_GAP
    assert gb[0][0].x == TOUCH_GLOBAL_X and gb[0][0].y == TOUCH_GLOBAL_Y
    assert mb[0][0].x == TOUCH_MID_X1 and mb[0][0].y == TOUCH_MID_Y1
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
        assert STICK_P1_CENTER == (110, 630), "底盘圆心不该被手指改动"
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
    transform = _tt_phys(app, _tt_center(app.left_btns, "秘卷"))
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
    "AAEAAAATAQAABAAwR0RFRhS1FkoAA3ToAAAAQEdQT1MAGQAMAAN1KAAAABBHU1VCbIx0hQADdTgAAAAaT1MvMmYwBBgAAAG4AAAAYGNtYXDU94uDAAAkaAAAG/xjdnQgRJ1NcgAASewAAAIQZnBnbXPTI7AAAEBk",
    "AAAHBWdhc3AABAAHAAN03AAAAAxnbHlmt0e1AAAAbwwAAwAcaGVhZBaf9LMAAAE8AAAANmhoZWEPeQ51AAABdAAAACRobXR4Kli9QgAAAhgAACJQbG9jYQrgpPkAAEv8AAAjEG1heHALbAKDAAABmAAAACBuYW1l",
    "lU2vyQADbygAAAWUcG9zdP8DAGYAA3S8AAAAIHByZXBBvdqCAABHbAAAAn52aGVhEr4JcgADdVQAAAAkdm10eIEfeIwAA3V4AAARiAABAAAAADMzRyPoP18PPPUCPwgAAAAAAMY/xrAAAAAA5xexHv/w/hQICAag",
    "AAAACAAAAAEAAAAAAAEAAAd+/h0AAAgA//D/8ggIAAEAAAAAAAAAAAAAAAAAAAhlAAEAAAjDAGYADQCIAA4AAgAQAC8AWgAAAh8BYwAEAAEAAwWTAZAABQAIBZoFMwAAAR4FmgUzAAAD0ABmAfIAAAILBgYDCAQC",
    "AgSAAAADCAHkYAAAABAAAAAAV1FZRgBAACD/XgYf/hQAhAd+AeMAEAAAAAAAAARKBbYAAAAgAAIIAAJYCAABUAQAAEgIAAFQBAAASAgAANgIAADYCAAA2AgAANgIAADYCAAA2AgAANgE0AC4BNABGATQALgE0ACA",
    "BNAAkATQALAIAACwCAAAsAgAAfAIAAAACAAAMAgAADAIAAQACAAA2AgABAAIAAHgCAAEAAgAAYAIAACoCAAAeAgAAKAIAACgCAAAkAgAAFgIAACgCAAAkAgAAHAIAAB4CAAAeAgAAGAIAADgCAAAsAgAALAIAAB4",
    "CAAAeAgAAIgIAACgCAAAcAgAAFgIAADICAAAaAgAAHgIAAEACAAAkAgAAHgIAADYCAAAaAgAAGgIAABwCAAAgAgAAGAIAACACAAAaAgAAGAIAABYCAAAcAgAAFgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFgIAABY",
    "CAAAUAgAAFAIAABICAABCAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAaAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQ",
    "CAAAUAgAAGgIAABQCAAAUAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABgCAAAkAgAAGgIAABwCAAAgAgAAGgIAABYCAAAaAgAAIgIAAB4CAAAaAgAAGAIAABI",
    "CAAAaAgAAPAIAABwCAAAYAgAAIgIAABoCAAAaAgAAGgIAABoCAAAaAgAAHgIAABoCAAAeAgAAFgIAABoCAAA0AgAANgIAACACAAAmAgAALAIAADICAAAcAgAAGgIAACACAAAeAgAAGAIAABICAAASAgAAJAIAACI",
    "CAAAYAgAAGgIAAA4CAAAYAgAAEgIAACICAAAWAgAAHAIAAB4CAAAWAgAAIAIAABoCAAAaAgAAEgIAABwCAAAaAgAAFgIAACACAAAaAgAAFAIAADQCAAAeAgAAIgIAACACAAAeAgAAIgIAABoCAABMAgAAJgIAADI",
    "CAAA0AgAAFgIAAB4CAAAUAgAAFAIAABQCAAAUAgAAGgIAABgCAAAiAgAAGgIAABoCAAAaAgAAFAIAABoCAAAmAgAAKAIAACgCAABSAgAAIgIAAB4CAAAwAgAAGgIAABoCAAAqAgAAFgIAABoCAAAoAgAAHAIAABQ",
    "CAAAyAgAAGAIAABQCAAA4AgAAGAIAABwCAAAoAgAAFgIAACgCAAAkAgAAIAIAABYCAAAYAgAAEgIAACwCAAAoAgAAKAIAABoCAAAoAgAAKgIAACoCAAAmAgAAKgIAACoCAAAoAgAAFgIAABwCAAAuAgAALgIAADg",
    "CAAAuAgAALgIAAC4CAAAuAgAAMAIAADACAAAcAgAAEAIAABYCAAAWAgAAHAIAABYCAAAWAgAAFAIAABYCAAAgAgAAGgIAABYCAAAUAgAAFgIAABYCAAAcAgAAHAIAACgCAAAeAgAAIAIAABgCAAAWAgAAFgIAABg",
    "CAAAaAgAAHAIAABQCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAFgIAABoCAAAaAgAAHgIAACICAAAWAgAAGgIAACYCAAAgAgAAHgIAACYCAAAcAgAAIgIAABoCAAAmAgAAGAIAABwCAAAkAgAAJAIAACA",
    "CAAAaAgAAHAIAACACAAAaAgAAJgIAABICAAAgAgAAGgIAABoCAAAaAgAAKgIAABYCAAAYAgAAGAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABoCAAAWAgAAHgIAABoCAABKAgAARAIAADACAAAWAgAAJAIAACI",
    "CAAAmAgAAIgIAABgCAAAmAgAAIAIAABwCAAASAgAAFAIAABQCAAASAgAAFAIAABQCAAAUAgAAFAIAABgCAAAYAgAAHgIAAB4CAAAaAgAAJAIAADACAAAiAgAAIgIAACICAAAiAgAANgIAAD4CAAAgAgAAFgIAABo",
    "CAAAUAgAAFAIAABgCAAAYAgAAFgIAABgCAAAWAgAAFAIAABYCAAAWAgAAHAIAABoCAAAaAgAAFAIAABICAAASAgAAEgIAABICAAAWAgAAFAIAABYCAAAUAgAAFAIAABgCAAAaAgAAFgIAABYCAAAaAgAAFAIAABo",
    "CAAAaAgAAHgIAACICAAAWAgAAGgIAABYCAAAaAgAAFgIAABoCAAAoAgAAFAIAABQCAAAUAgAAFgIAABYCAAAUAgAAFAIAABYCAAAUAgAAFgIAABYCAAAWAgAAGAIAABYCAAAWAgAAFAIAABgCAAAUAgAAFgIAABg",
    "CAAAUAgAAFAIAABQCAAAWAgAAFAIAABYCAAAYAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAHgIAABQCAAAYAgAAFAIAABACAAAYAgAAFAIAABgCAAAWAgAAFgIAABACAAAYAgAAGAIAABgCAAAQAgAAFgIAABg",
    "CAAAYAgAAGAIAABgCAAAYAgAAGAIAABYCAAAYAgAAFgIAABgCAAAYAgAAFgIAABYCAAAYAgAAGAIAABgCAAAYAgAAFgIAABYCAAAWAgAAFgIAACICAAA0AgAAJAIAABoCAAAWAgAAEgIAABoCAAAUAgAAGgIAAB4",
    "CAAAaAgAAFAIAABQCAAAwAgAAFgIAABwCAAAgAgAAKgIAABYCAAAgAgAAFAIAABwCAAAsAgAARAIAAB4CAAAmAgAALgIAABgCAAAaAgAAJAIAABQCAAAcAgAAGgIAABoCAAAkAgAAJAIAACICAAAWAgAAGgIAAB4",
    "CAAAaAgAAGgIAAB4CAAAWAgAAGgIAABoCAAAWAgAAFgIAABYCAAAiAgAAJAIAAAwCAAAkAgAADAIAAAwCAAASAgAAFgIAACACAAAUAgAAEgIAABICAAAMAgAAGgIAABgCAAAYAgAAGAIAAB4CAAASAgAAEgIAABI",
    "CAAASAgAAEgIAABQCAAASAgAAFAIAABgCAAAYAgAAEgIAABQCAAAUAgAAEgIAABICAAAOAgAAFAIAABQCAAASAgAAFAIAAA4CAAAaAgAAHAIAABoCAAAaAgAAFgIAACACAAASAgAAEgIAABwCAAAkAgAAGgIAAEI",
    "CAAAiAgAAHgIAABYCAAAcAgAAGAIAABYCAAAWAgAAGgIAABoCAAAaAgAAFgIAABoCAAAaAgAAFgIAABgCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAGAIAABgCAAAWAgAAFgIAABg",
    "CAAAWAgAAFgIAABYCAAAYAgAAGAIAABYCAAAWAgAAFgIAABoCAAAaAgAAEgIAABwCAAAUAgAAGAIAABoCAAAaAgAAFgIAABoCAAAaAgAAFgIAABoCAAAaAgAAGgIAABICAAASAgAAFAIAABYCAAAWAgAAFgIAABY",
    "CAAAWAgAAHAIAABoCAAAaAgAAGgIAABoCAAAaAgAAGAIAACACAAAWAgAAQAIAAEQCAAA0AgAAHgIAABgCAAA6AgAAJgIAABACAAASAgAAEgIAABACAAAaAgAARAIAACoCAAAaAgAAGgIAABoCAAAaAgAAFAIAABo",
    "CAAAaAgAAVAIAACQCAAAMAgAAJAIAABoCAAAaAgAAFAIAAB4CAAAoAgAAKAIAABoCAAAoAgAAIgIAACICAAAiAgAAFgIAABYCAAAUAgAAFAIAABICAAAOAgAAFAIAABICAAAUAgAADgIAABACAAASAgAAGgIAABo",
    "CAAAaAgAAEgIAABYCAAAkAgAAEgIAAA4CAAAOAgAAFgIAAA4CAAAOAgAAFgIAABICAAASAgAAJgIAABgCAAAcAgAAGgIAACACAAAaAgAAIAIAABoCAAAeAgAAGgIAABoCAAAUAgAAGAIAABoCAAAYAgAAGgIAABo",
    "CAAAaAgAAHAIAABoCAAAUAgAAHAIAABQCAAAWAgAAFgIAABoCAAAaAgAAHAIAABwCAAAWAgAAHAIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAWAgAAMgIAAB4CAAAeAgAAGgIAABYCAAAUAgAAGAIAABwCAAASAgAAGgIAABgCAAAUAgAAFAIAABQCAAAkAgAAFgIAABQCAAAiAgAAFAIAABo",
    "CAAAUAgAAEAIAABYCAABIAgAAJAIAABgCAAAgAgAAGgIAAB4CAAAeAgAAGgIAAB4CAAAgAgAAGgIAABoCAAAgAgAAHgIAAB4CAAAaAgAAGgIAACACAAAaAgAAGgIAAB4CAAAgAgAAIAIAABQCAAAWAgAAFAIAABg",
    "CAAAWAgAAEgIAABQCAAAYAgAAEgIAABICAAAaAgAAFAIAABACAAASAgAAEgIAABYCAAAaAgAAJgIAABoCAAAaAgAAEgIAACACAAAaAgAAEAIAABgCAAAYAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAcAgAAHAIAACQCAAAaAgAAGAIAABwCAAAaAgAAHAIAABgCAAAgAgAAGAIAABgCAAASAgAAGgIAABI",
    "CAAASAgAAEgIAABwCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGAIAABICAAASAgAAGgIAABoCAAAaAgAAGgIAABwCAAAaAgAAGgIAABYCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABg",
    "CAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABoCAAAeAgAACgIAABoCAAAaAgAAEAIAACICAAAcAgAAGAIAABo",
    "CAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAASAgAAFAIAABQCAAAcAgAANAIAADQCAAA0AgAANAIAADQCAAA0AgAAKgIAACoCAAAoAgAAKAIAACgCAAAoAgAAKgIAACICAAAoAgAAIgIAACg",
    "CAAAoAgAAGAIAAB4CAAAiAgAAGAIAABgCAAAaAgAAGgIAABgCAAAaAgAAGgIAABoCAAAaAgAAIAIAABoCAAAaAgAAFgIAABQCAAAYAgAAGgIAABwCAAAUAgAAFAIAABgCAAAWAgAAGAIAABYCAAAkAgAAGgIAABI",
    "CAAASAgAAEgIAABQCAAAaAgAAGgIAADYCAAAgAgAAIAIAACACAAAgAgAAHAIAABgCAAAUAgAAFgIAABgCAAAYAgAAOgIAABQCAAAYAgAA4AIAALoCAABoAgAAlAIAADwCAABuAgAA6AIAAMQCAACIAgAAdAIAAIw",
    "CAABUAgAASgIAAFgCAACEAgAAjAIAAKYCAACOAgAAjAIAAHgCAACSAgAAjAIAAIoCAACOAgAAjAIAAGoCAABiAgAAjAIAAIwCAACMAgAAjgIAAD4CAABaAgAAiAIAAHICAAB6AgAAjAIAAIwCAABoAgAAdAIAAIo",
    "CAACAAgAAiAIAAKACAABUAgAAaAIAAFgCAACSAgAAWAIAAIQCAACAAgAAZgIAAGwCAABaAgAAIgIAAGACAABkAgAAdgIAAM4CAACEAgAApAIAAIICAAAAAgAAxAIAAIoCAACMAgAAlAIAAHYCAACCAgAAhAIAAHY",
    "CAACGAgAAkgIAAIQCAACaAgAAlAIAAEQCAACGAgAAfgIAAIwCAAB2AgAApgIAAJoCAACMAgAAhgIAAHACAABGAgAAdAIAAHACAACUAgAAmgIAAO4CAACKAgAAjAIAAEICAAAaAgAAGAIAABgCAAAeAgAA+gIAAGo",
    "CAACkAgAAngIAAIoCAACgAgAAmAIAALQCAACSAgAAnAIAAJICAACaAgAAogIAAJ4CAACmAgAAlgIAAKQCAAC2AgAAnAIAACACAAD8AgAA9gIAAGwCAAAiAgABBAIAABoCAADqAgAAKAIAABoCAAAYAgAAhAIAABQ",
    "CAABmAgAAGgIAAFICAAAiAgAAnAIAACwCAAAiAgAAygIAABoCAAAeAgAAGgIAAB4CAADAAgAAJAIAABQCAAAeAgAA7AIAABoCAAAaAgAAQAIAABoCAAAYAgAAFAIAAEACAABAAgAAPAIAABwCAAAsAgAAFAIAAEA",
    "CAAAcAgAAGgIAACACAACSAgAAOgIAACgCAAAaAgAAGAIAAE4CAABKAgAAXgIAAMICAAAoAgAAHgIAABoCAAAcAgAARAIAANICAAAgAgAAHgIAAB4CAACWAgAAqAIAAGwCAAAaAgAAIAIAABoCAAAUAgAAZgIAACI",
    "CAACIAgAAfgIAALACAAAiAgAATgIAANYCAABcAgAAYgIAAI4CAAB+AgAAgAIAAIQCAAAYAgAAFgIAABoCAAB0AgAAeAIAAIQCAABWAgAAcAIAAEwCAAAcAgAAIAIAACQCAABUAgAAGgIAACICAABgAgAAGgIAACI",
    "CAABKAgAAIgIAABgCAAAmAgAAYAIAAF4CAACQAgAAogIAAGQCAABsAgAAZgIAAIICAAAyAgAAIgIAAGACAAAiAgAAqgIAAI4CAAAWAgAAHAIAALgCAAAiAgAAwAIAAN4CAADeAgAAxAIAANACAADaAgABQAIAABg",
    "CAAC8AgAAhgIAAKwCAAAOAgAArgIAANICAACgAgAAGgIAABoCAAC2AgAAGgIAABgCAAAWAgAAGAIAABoCAAAcAgAAqAIAAKoCAADIAgAAFAIAACICAADUAgAAGAIAAKoCAAB+AgAAugIAAKgCAAFgAgAAFgIAAMw",
    "CAACwAgAAKAIAABACAAAiAgABEgIAAKoCAACWAgAAGgIAABYCAACyAgAAFgIAABYCAAAaAgAAmAIAAHYCAABYAgAAvAIAAKQCAAAeAgAAEgIAABICAABMAgAAhAIAACACAAAcAgAAIAIAABYCAACqAgAAkgIAANA",
    "CAAC+AgAAmgIAALYCAAAqAgAAdgIAALoCAAAmAgAAGgIAARICAACiAgAAIAIAAQoCAAAgAgAAcAIAAL4CAADAAgAArAIAALACAAC+AgAAGgIAABwCAABQAgAAVgIAABwCAAA0AgAAFgIAALYCAADoAgAAzgIAABY",
    "CAADIAgAA3AIAACACAAEeAgAA2AIAAJgCAACiAgAAkAIAAJYCAACuAgAAqgIAAP4CAAAoAgAAKAIAACgCAAAqAgAAsgIAACoCAAAoAgAAMAIAABoCAADSAgAAIAIAABoCAABCAgAAyAIAABICAADaAgAAFgIAABQ",
    "CAACqAgAAvgIAANYCAACiAgAArgIAAIQCAAAqAgAAvAIAAJQCAADAAgAAggIAANYCAAC4AgAAsgIAAKwCAADUAgAAzgIAALoCAAC+AgAAGgIAAOQCAACqAgAAsAIAAMACAADCAgAApgIAALwCAACyAgABAAIAAKg",
    "CAAAgAgAAGgIAACQCAAAeAgAA6AIAACQCAAASAgAAwgIAABgCAACKAgAAhAIAAEoCAADqAgAAjgIAAJACAACYAgAAGgIAAIICAAFaAgAACgIAAB4CAACSAgAAtAIAAIQCAAASAgAApAIAAJ4CAACyAgAAgAIAALw",
    "CAACMAgAA5AIAAC4CAADWAgAApgIAAJQCAACoAgAAHgIAACoCAACoAgAAlAIAAL4CAADGAgAApAIAAMACAAAcAgAArgIAANgCAABuAgAAqgIAAQwCAADSAgAAtAIAABgCAAC4AgAAlAIAABICAACqAgAAggIAAJI",
    "CAAC2AgAAjAIAAOICAADEAgAAtAIAAI4CAAAeAgAADgIAABoCAAAYAgAAKAIAAJ4CAADaAgAAwAIAAOoCAAByAgAAjAIAAJ4CAACcAgABBAIAABICAACcAgAAHgIAAK4CAACwAgAArAIAACQCAAB6AgAAkAIAALQ",
    "CAACiAgAAEgIAAOQCAAAgAgAAJgIAAOoCAACsAgAA/AIAAPQCAAAaAgABBgIAACACAAAgAgAA5AIAANACAACaAgAAmgIAAOICAAC4AgAALgIAAJoCAAAaAgAA3AIAABwCAAC+AgAAEAIAAL4CAADOAgAA4AIAAOw",
    "CAABCAgAALAIAABwCAACOAgAAHAIAADQCAADSAgAAvAIAABoCAADIAgAAEgIAAP4CAAAkAgAAyAIAAFACAAB6AgAAlgIAACQCAAAgAgABNAIAABQCAAC4AgAAEgIAABoCAAAeAgAAGAIAAMQCAADAAgAA5gIAABY",
    "CAAC4AgAAwgIAASYCAAC0AgAAGAIAAIICAAASAgAA5AIAABgCAAAYAgAAFgIAACgCAAC2AgAAygIAAKgCAADOAgAAhAIAAGQCAAAaAgAA1gIAAFwCAADSAgAAGAIAAKgCAADCAgAAGgIAABICAAAaAgAAHgIAABY",
    "CAAC+AgAArgIAALACAADSAgABMAIAALgCAABGAgAAFAIAAH4CAAAaAgAAGgIAAMwCAAAWAgAAFgIAAOoCAAAoAgAAHAIAALoCAACkAgAA6AIAAIQCAACuAgAAKAIAAB4CAAASAgAA+AIAABQCAAAcAgAAigIAAB4",
    "CAAFCAgAAIAIAABgCAAC0AgABGgIAAIgCAADaAgAAzgIAALgCAACGAgAA2AIAAKwCAADsAgAAYAIAABQCAABaAgAAFgIAAHYCAAAYAgAAwAIAACgCAAAwAgAAxgIAABoCAAD6AgAA7gIAABYCAAC4AgAAFgIAACo",
    "CAAAaAgAAHAIAABgCAAD0AgABCAIAABoCAAC2AgAA3AIAAMoCAACiAgAAwgIAAMQCAAAUAgAAFAIAAOQCAAASAgAA1AIAABICAACsAgAAPAIAAJwCAACqAgAAKgIAAMwCAACuAgAAJgIAACACAAC6AgAAmAIAABo",
    "CAAB0AgAAxgIAALoCAADsAgAAFgIAALgCAAAaAgAAIAIAABwCAABWAgAAKgIAAPACAAAgAgAAIAIAANoCAACoAgAA5AIAACYCAADEAgAAuAIAANoCAAEMAgAAIAIAABgCAADKAgAAogIAAMICAACcAgAAcAIAAI4",
    "CAAC2AgAA/AIAAN4CAADgAgAAagIAACICAADoAgAAGgIAAB4CAAAgAgAAuAIAAJQCAAAWAgAA6gIAACACAACoAgAA5AIAAQACAAAcAgAAIgIAABwCAADGAgAArAIAABYCAAAmAgAAUgIAABoCAABAAgAAHAIAAGQ",
    "CAABsAgAAdgIAABQCAACwAgAAIgIAABoCAAAaAgAAugIAACwCAADKAgAAGgIAADQCAACqAgAAJgIAAHoCAAAWAgAAyAIAAMwCAAA2AgAALAIAABYCAAEyAgAAtAIAABICAAASAgAAlAIAAMYCAAAaAgAAqgIAAKw",
    "CAAFAAgAAFgIAANgCAAAaAgAAEgIAAKgCAAB6AgAAGgIAABoCAAC2AgAAtgIAABoCAADIAgAAGAIAABYCAAAcAgAAzAIAABoCAAAUAgAAHgIAAOICAAAUAgAAtAIAAJgCAAAUAgAAFgIAACACAACaAgAAEAIAABA",
    "CAAAUAgAAGgIAAGQCAAEkAgABGgIAABoCAAAcAgAAqgIAAH4CAACKAgAAmAIAALwCAAA8AgAAkgIAAQoCAADsAgAA7gIAABQCAADcAgAAPAIAABQCAAAUAgAAFAIAABQCAAAWAgAAHAIAAPICAAAaAgAAGgIAABo",
    "CAAAaAgAAbgIAAEQCAACQAgAAGgIAAMYCAACoAgAAHgIAACICAABWAgAAsAIAAJACAAAcAgAAKgIAACoCAADAAgAA2gIAANICAAAUAgAAwAIAAMgCAAAcAgAAhgIAABICAAAwAgAAIgIAASoCAAAgAgAAHAIAAJ4",
    "CAAASAgAAuAIAABQCAACYAgAArgIAABoCAAAaAgAA9AIAACQCAAAYAgAAqAIAALYCAAAqAgAAEgIAABQCAAASAgAAEgIAAQ4CAAASAgAAFgIAABYCAAAaAgAAEgIAACYCAAAWAgAAFgIAABQCAAD2AgABKAIAAPI",
    "CAADcAgAAFAIAAM4CAACsAgAAxAIAAKoCAACQAgAAwAIAAKACAAGIAgAAIgIAAJoCAACeAgAAHAIAAIACAADMAgAAogIAAOQCAAE2AgAAJgIAABoCAAAmAgAAjgIAABQCAACkAgAAngIAABwCAAAcAgAAFAIAAOA",
    "CAAAUAgAAGgIAAOYCAAAUAgAAjAIAAOoCAAAaAgAA2gIAAQwCAAFcAgAA1gIAAMwCAAC4AgAA5gIAAJoCAACiAgABAAIAABQCAAAWAgAA+AIAATACAAAUAgABEAIAAMgCAAAWAgAAygIAALoCAAAaAgAAGgIAABo",
    "CAAAYAgAAFgIAAKACAADQAgABIAIAASACAAA8AgAAIgIAAGQCAAAqAgAAHAIAABQCAAAaAgAA7AIAAMACAAAYAgAAHAIAABoCAAAUAgAAFAIAAIoCAADCAgAAsAIAAM4CAAC8AgAAFgIAABYCAACcAgAALgIAACA",
    "CAACQAgAAFAIAALYCAAC4AgAAFAIAABoCAADmAgABVgIAABgCAAAqAgAAnAIAACYCAAAYAgAALgIAABoCAACiAgAAGgIAABgCAAAeAgAA8AIAABYCAACmAgAAtgIAAJoCAAAaAgAAGgIAACgCAADIAgAAzAIAAII",
    "CAACkAgAAGgIAACwCAAEGAgAAFgIAABwCAAAmAgAADgIAAHQCAAAUAgAAFAIAAMQCAAEeAgABQgIAAMICAAAUAgAAGgIAAOYCAAAaAgAAfAIAAI4CAAAWAgABAAIAABQCAADkAgAAwgIAABICAAAaAgAAGgIAAFY",
    "CAAFiAgAAgAIAAVoCAAAUAgAAFgIAABICAACyAgAAGAIAARICAABsAgAAjAIAAWwCAAAWAgAARgIAABgCAAAaAgAAHgIAAQACAACIAgAAEAIAANgCAAASAgAAoAIAAAwCAAE4AgAAGgIAABQCAACyAgAAHgIAAHQ",
    "CAAAWAgAAugIAAKoCAAC2AgAAEgIAANoCAAAaAgAAIAIAACACAAAaAgABFgIAACACAAAmAgAAwgIAACICAAAkAgAAVgIAAJgCAAAUAgAAFgIAABQCAAAaAgAA3AIAABoCAADSAgABRAIAACQCAADaAgAA7AIAABg",
    "CAAAWAgAAFgIAAB4CAAAwAgAAIgIAABoCAAAaAgAAGgIAABoCAAAUAgAAFAIAABQCAAAUAgAAGgIAABoCAAAgAgAAJAIAACgCAAC2AgAAxgIAAIwCAAAYAgAAlgIAACICAAAiAgAAugIAAKYCAAASAgAAxAIAABY",
    "CAACMAgAADgEzQAAAecBHQAtAAABJwEpAIUAmAG4AR0BzwDTAJMA4QCeAIMAPQCsAJoAjwCcAJoB5wGaAJgAmACYAB8AIQCHAIEAhwDZAPQAdQCHAOEAiQDTAOkAcQCHAFQAsABUALoAjQBmAH0AIQACADUAIQBm",
    "AZwA0wEh//AAhwCeAKwAiQCFAJwAZgCgAMUAhwDXALwAXACgAHMAngCJAQgAywCLAKAAUv/8AGAAUgC2AOECGwDjAJgBXAHnAL7/+gBOAEYAAAACAAAAAwAAABQAAwABAAAAFAAEG+gAAAb2BAAACQL2ACMAJQA+",
    "AF0AXwB+ALIAtwDXIBQgJiGTIh4kZiWyJbYlvCXAJcYlzyYGJxMwAjANMBFOAE4HTgtODk4UTiJOJE4qTi1ONE47TkVOSU5LTk5OWU5dTmBOZk5xToZOiU6MTo5Okk6UTptOpE6nTq5Ouk7ATsZOzk7TTtZO5U73",
    "TvtO/U8RTxhPGk8gTyRPOE88T0ZPT09TT1VPWU9cT2BPf0+LT5tPnU+nT79P3U/uUA1QElAZUDxQPlBHUE9QWlBcUH9QqFCsULtQz1D1UUNRSVFNUVxRZVFoUW1RcVFzUXhRfFGFUY1RmVGzUbVRt1G7UcBRxlHP",
    "UdFR4FH2UftR/VIAUgNSB1ISUhdSGVIbUh1SJFIrUjBSN1I7Uk1SVFJqUohSm1KhUqlSv1MFUxZTOlNBU0NTR1NKU1VTV1NhU3BTdFN3U4tTmlOfU7tTwlPIU8pTzVPRU9hT4FPkU+xT8FPzU/dUBFQIVA5UEVQm",
    "VCxUL1Q4VEhUWFRoVH1UjFTBVMhUzVTlVOpVJFUvVUZVilXcVjRWaFbKVttW3lbgVvRW+lb+VwZXCFcjVyhXMFc6V0BXR1dQV1dXgleLV99X+liDWJ5ZBFkHWQ1ZFlkaWRxZJ1kqWS5ZMVk0WVFZV1llWXNZdll9",
    "WctZ0Fn/WhhazFtQW1hbZluDW4lbjFuYW5pbnluiW6RbqluzW7ZbuVu9W/lb/FwEXA9cEVwWXBhcHVwxXDpcPlxAXEJcRVxPXF5dKV1MXeZd6F3yXgNeJ144XkVeVV5zXnZej16VXpdepl6tXvZe+l8AXwJfD18V",
    "XyBfJ186X1NfVV9iX3Ffe1+AX4Vfi1+XX6Ffql+uX71fw1/FX9df62ABYA5gEmAdYCdgO2BiYMVg82EIYQ9hH2FiYhJiFmIYYipiNGJAYkdiS2JNYlNiWGJbYmNiZ2JpYmticGKAYoRiimKTYpVimGKiYqRirGKx",
    "YrVixmLJYs1i0mLWYtti32LpYvFi/2MCYwdjCWMRYyFjJGMoYypjX2NiY25jd2OJY5JjpWOoY7dj0GPSY/RkHGQeZC1kR2RYZHhknmSkZK1kxWTOZS9lNmU5ZTtlPmVIZUxlT2VjZXBldGWHZYtll2WcZadlqWWt",
    "ZbBluWXLZeBl4mXnZell9mYOZhNmIGYvZj5mb2aCZpdmtGb0ZwBnCWcNZx1nH2csZy9nNWc6Z0BnQ2dGZ1BnX2dhZ2Vnf2eBZ4RnnGe2Z9Bn02flaAdoD2ghaDloPGhGaEhoTGhjaGVodmivaMBpLWnMaf1qIWoq",
    "allrIWtla3trtWvNa89r0mvUbBRsNGw4bEJsR2xJbIlsoWy/bMls1WzibOhs/G07bT5tQW1LbU9tbm13bYhtqG3hbfFuBW4QbiFuMm44bpBu0W7ebuFvAm8Ub8Bwa3B1cK5wuXDfcO1xNnFncgZyKnIxckhyTHJZ",
    "cmlyeXK2ctBy7HL4cxtzK3OHc6lzsHQDdAZ093UfdSh1MnU1dTt1THVZdWV1l3WrddV2e3Z9doR2xnbKds920nbWdth27nb0dvl2/ncBdwt3IHc8d0B3W3dhd6x3s3fpd+14AXgUeDR4OHhAeGx4bniXeLB4vnk6",
    "eTx5PnleeYF5u3nBec150nnYefB5+3oLejN6P3p6en96gXqXep16y3rWetl64Hrvext7Jnsse0l7Vnt+e4B7l3uhe618B3xzfHt8knzKfPt9IH0ifSd9K30vfqJ+p36vfrl+v37Efsh+037Vftl+3X7ffud+6X7t",
    "fwB/E38Wfxh/KX86f1F/aX9uf45/+4ADgAWADIAXgDOATIBUgFqApYDMgNyA9oD9gRGBGoFwgX+BwoHqgfSCDIJygoKCsYLPguWDA4M2g1CDt4PchCWEPYS4hMSE3YXPhlqGy4eDh/mIQIhFiEyIYYhliGiIcIiN",
    "iKuIwojFiNmI+ImBiYaJwonEicaJyYnSieOJ5ooAi6GLpIupi66LsIuyi7iLv4vBi82L0YvVi92L5Yvti++L9Iv7jAGMA4xhjGqNH40jjSaNKI0vjTSNOY1EjVSNVo1wjXeNhY2KjbONw43Rjd2N343vjfOOKY6r",
    "jrKOuo9oj2yPbo97j32PkY+Tj6iPuY/Fj8eP0Y/Uj9mP3I/fj/eP/ZACkAmQEJASkBqQIJA7kFOQbpB/kKOQ6JD9kU2RkpHKkc2Rz5HRlIiUn5SulMGU9pT6lQGVC5UZlS6VXJV/leiV6pXulfSWAZYyljWWRZZN",
    "llCWZJZplpCWlJbGlvaXAJcHlzKXOJdSl1mXXpdgl2KX85h2mHuYf5iEmJiYnZjOmNiY35ltmXCZiJmPmZaZmZpsmnGaf5qMmqia2Jx8nLieIZ7RntifIJ9Qn5n/Xv//AAAAIAAlACgAQABfAGEAsgC3ANcgFCAm",
    "IZAiHiRgJbIltiW8JcAlxiXPJgUnEzAAMAowEE4ATgdOCU4NThNOIk4kTipOLU40TjpORU5ITktOTk5ZTl1OX05mTnFOhk6JTotOjk6STpROm06kTqdOrk66Tr9OxU7NTtNO1k7jTvZO+079TxFPGE8aTyBPJE84",
    "TzxPRk9NT1NPVU9ZT1xPYE9/T4tPm0+dT6dPv0/dT+5QDVASUBlQPFA+UEdQT1BaUFxQf1CoUKxQu1DPUPVRQ1FIUU1RXFFlUWhRbVFxUXNRdlF8UYVRjFGZUbJRtVG3UbtRwFHGUc9R0VHgUfZR+lH9UgBSA1IG",
    "UhJSF1IZUhtSHVIkUitSMFI2UjpSTVJUUmlSiFKbUp5SqFK/UwVTFlM6U0FTQ1NHU0pTVVNXU2BTcFNzU3dTi1OaU59Tu1PCU8hTylPMU9FT1lPgU+NT6lPvU/NT91QDVAhUDFQRVCZUK1QvVDhUSFRYVGhUfVSM",
    "VMFUyFTNVOVU6lUkVS9VRlWKVdxWNFZoVspW21beVuBW9Fb6Vv5XBlcIVyNXKFcwVzpXQFdHV09XV1eCV4tX31f6WINYnlkEWQdZDVkWWRpZHFknWSpZLlkxWTRZUVlXWWVZc1l2WX1Zy1nQWf9aGFrMW1BbV1tm",
    "W4NbiVuMW5hbmlueW6BbpFuqW7Nbtlu5W71b+Fv8XARcD1wRXBZcGFwdXDFcOlw9XEBcQlxFXE9cXl0pXUxd5V3oXfFeA14mXjheRV5VXnJedl6PXpNel16mXq1e9l76XwBfAl8PXxVfIF8nXzlfUl9VX2JfcV97",
    "X4BfhF+LX5dfoV+qX65fvV/DX8Vf11/rYAFgDmASYB1gJ2A7YGJgxWDzYQhhD2EfYWJiD2IWYhhiKmI0Yj9iR2JLYk1iU2JYYltiY2JnYmlia2JwYn5ihGKKYpNilWKYYqJipGKsYrFitWLFYslizWLSYtZi22Lf",
    "Yuli8WL9YwFjB2MJYxFjIWMkYyhjKmNfY2JjbmN3Y4ljkmOlY6djt2PPY9Jj9GQcZB5kLWRGZFhkeGSeZKRkrWTFZM1lL2U2ZTllO2U+ZUhlTGVPZWNlcGV0ZYdli2WXZZxlp2WpZa1lsGW5Zctl4GXiZedl6WX2",
    "Zg5mE2YfZi9mPmZuZoJmlma0ZvRm/2cIZw1nHWcfZypnL2c1ZzpnQGdDZ0ZnUGdfZ2FnZWd/Z4FnhGecZ7Zn0GfTZ+VoB2gPaCFoN2g8aEZoSGhMaGNoZWh2aK9owGktacxp/WohaipqWWsga2Jre2u1a81rz2vS",
    "a9RsFGw0bDhsQmxHbElsiWyhbL9syWzVbOFs6Gz8bTttPm1BbUttT21ubXdtiG2obeFt8W4FbhBuIW4ybjhukG7Rbt5u4W8CbxRvwHBrcHVwrnC5cN9w7XE2cWdyBnIqcjFyR3JMcllyaXJ5crZy0HLscvhzG3Mr",
    "c4dzqXOvdAN0BnT3dR91KHUxdTV1O3VMdVl1ZXWXdat11XZ7dn12hHbGdsp2z3bRdtZ22HbudvR2+Hb+dwF3C3cfdzx3QHdbd2F3rHezd+l37XgBeBR4NHg4eEB4bHhueJd4sHi+eTp5PHk+eV55gXm7ecF5zXnS",
    "edh58Hn7egt6M3o/enp6f3qBepd6nXrLetZ62Xrgeu97G3smeyx7SXtWe357gHuXe6F7rXwHfHN8e3ySfMp8+30gfSJ9J30rfS9+on6mfq9+t36/fsN+yH7TftV+2H7dft9+537pfu1/AH8TfxZ/GH8pfzp/UX9p",
    "f25/jn/7gAOABYAMgBeAM4BMgFSAWoClgMyA3ID2gP2BEYEagXCBf4HCgeqB84IMgnKCgoKxgs+C5YMDgzaDUIO3g9yEJYQ9hLiExITdhc+GWobLh4OH+YhAiEWITIhhiGWIaIhwiI2Iq4jBiMWI2Yj4iYGJhonB",
    "icSJxonIidKJ44nmigCLoYuki6mLrYuwi7KLuIu+i8GLzYvRi9WL3Yvli+2L74v0i/uMAYwDjGGMao0fjSONJY0ojS+NNI05jUSNVI1WjXCNd42FjYqNs43DjdGN3Y3fje+N844pjquOso66j2iPbI9uj3uPfY+R",
    "j5OPqI+5j8WPx4/Qj9SP2I/bj96P94/9kACQCZAPkBKQGpAfkDuQU5BukH+Qo5DokP2RTZGSkcqRzJHPkdGUiJSflK6UwZT2lPqVAJULlRmVLpVclX+V6JXqle2V9JYBljKWNJZElk2WUJZklmmWj5aUlsaW9pcA",
    "lweXMpc4l1KXWZdel2CXYpfzmHWYeZh+mISYl5icmM6Y2JjemW2ZcJmImY+ZlpmZmmyacZp/moyaqJrYnHycuJ4hntGe2J8gn1Cfmf8B//8IRAhDCEEIQAg/CD4ICwgHB+jorOib3nHmpNul2lraV9pS2k/aStpC",
    "2g3ZAdAV0A7QDLIeshiyF7IWshKyBbIEsf+x/bH3sfKx6bHnseax5LHasdex1rHRscexs7GxsbCxr7GssauxpbGdsZuxlbGKsYaxgrF8sXixdrFqsVqxV7FWsUOxPbE8sTexNLEhsR6xFbEPsQyxC7EIsQaxA7Dl",
    "sNqwy7DKsMGwqrCNsH2wX7BbsFWwM7AysCqwI7AZsBiv9q/Or8uvva+qr4WvOK80rzGvI68brxmvFa8SrxGvD68MrwSu/q7zrtuu2q7Zrtau0q7NrsWuxK62rqGunq6drpuuma6Xro2uia6Iroeuhq6Arnqudq5x",
    "rm+uXq5YrkSuJ64VrhOuDa34rbOto62ArXqtea12rXStaq1prWGtU61RrU+tPa0vrSutEK0KrQWtBK0DrQCs/Kz1rPOs7qzsrOqs56zcrNms1qzUrMCsvKy6rLKso6yUrIWscaxjrC+sKawlrA6sCqvRq8ersatu",
    "qx2qxqqTqjKqI6ohqiCqDaoIqgWp/qn9qeOp36nYqc+pyqnEqb2pt6mNqYWpMqkYqJCodqgRqA+oCqgCp/+n/qf0p/Kn76ftp+unz6fKp72nsKeup6inW6dXpymnEaZepdul1aXIpaylp6WlpZqlmaWWpZWllKWP",
    "pYelhaWDpYClRqVEpT2lM6UypS6lLaUppRalDqUMpQulCqUIpP+k8aQnpAWjbaNso2SjVKMyoyKjFqMHouui6aLSos+izqLAorqic6JwomuiaqJeolmiT6JJojiiIaIgohSiBqH9ofmh9qHxoeah3aHVodKhxKG/",
    "ob6hraGaoYWheaF2oWyhY6FQoSqgyKCboIeggaByoDCfhJ+Bn4Cfb59mn1yfVp9Tn1KfTZ9Jn0efQJ89nzyfO583nyqfJ58inxqfGZ8Xnw6fDZ8GnwKe/57wnu6e657nnuSe4J7dntSezZ7CnsGevZ68nrWepp6k",
    "nqGeoJ5snmqeX55XnkaePp4sniueHZ4GngWd5J29nbydrp2WnYadZ51CnT2dNZ0enRect5yxnK+crpysnKOcoJyenIucf5x8nGqcZ5xcnFicTpxNnEqcSJxAnC+cG5wanBacFZwJm/Kb7pvjm9Wbx5uYm4abc5tX",
    "mxibDpsHmwSa9Zr0muqa6Jrjmt+a2prYmtaazZq/mr6au5qimqGan5qImm+aVppUmkOaIpobmgqZ9ZnzmeqZ6ZnmmdCZz5m/mYeZd5kLmG2YPZgamBKX5Jcelt6WyZaQlnmWeJZ2lnWWNpYXlhSWC5YHlgaVx5Ww",
    "lZOVipV/lXSVb5VclR6VHJUalRGVDpTwlOiU2JS5lIGUcpRflFWURZQ1lDCT2ZOZk42Ti5Nrk1qSr5IFkfyRxJG6kZWRiJFAkRCQcpBPkEmQNJAxkCWQFpAHj8uPso+Xj4yPao9bjwCO347ajoiOho2WjW+NZ41f",
    "jV2NWI1IjTyNMY0BjO6MxYwgjB+MGYvYi9WL0YvQi82LzIu3i7KLr4uri6mLoIuNi3KLb4tVi1CLBosAisuKyIq1iqOKhIqBinqKT4pOiiaKDooBiYaJhYmEiWWJQ4kKiQWI+oj2iPGI2ojQiMGImoiPiFWIUYhQ",
    "iDuINogJh/+H/Yf3h+mHvoe0h6+Hk4eHh2CHX4dJh0CHNYbchnGGaoZUhh2F7YXJhciFxIXBhb6ETIRJhEKEO4Q2hDOEMIQmhCWEI4QghB+EGIQXhBSEAoPwg+6D7YPdg82Dt4Ogg5yDfYMRgwqDCYMDgvmC3oLG",
    "gr+CuoJwgkqCO4IighyCCYIBgayBnoFcgTWBLYEWgLGAooB0gFeAQoAlf/N/2n90f1B/CH7xfnd+bH5UfWN82Xxpe7J7PXr3evN67XrZetZ61HrNerF6lHp/en16anpMecR5wHmGeYV5hHmDeXt5a3lpeVB3sHeu",
    "d6p3p3emd6V3oHebd5p3j3eMd4l3gnd7d3R3c3dvd2l3ZHdjdwZ2/nZKdkd2RnZFdj92O3Y3di12HnYddgR1/nXxde11xXW2dal1nnWddY51i3VWdNV0z3TIdBt0GHQXdAt0CnP3c/Zz4nPTc8hzx3O/c71zunO5",
    "c7hzoXOcc5pzlHOPc45zh3ODc2lzUnM4cyhzBXLBcq1yXnIaceNx4nHhceBvKm8UbwZu9G7Abr1uuG6vbqJujm5hbj9t123WbdRtz23DbZNtkm2EbX1te21obWRtP208bQts3GzTbM1so2yebIVsf2x7bHpseWvp",
    "a2hrZmtka2BrTmtLaxtrEmsNaoBqfmpnamFqW2pZaYdpg2l2aWppT2kgZ31nQmXaZStlJWTeZK9kZwUAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
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
    "AACS1AAAk0AAAJPXAACUXQAAlQIAAJUYAACVLgAAlZUAAJWrAACVwQAAldcAAJXtAACWQQAAllcAAJZtAACWgwAAlpkAAJavAACWxQAAltsAAJbxAACXQAAAl7wAAJfSAACX6AAAmJcAAJk0AACZ3AAAmocAAJqd",
    "AACaswAAm3UAAJuLAACboQAAm7cAAJvNAACb4wAAm/kAAJwPAACcJQAAnDsAAJxRAACcZwAAnH0AAJyTAACcqQAAnL8AAJzVAACdUgAAnWgAAJ1+AACdlAAAnbAAAJ6nAACevQAAntMAAJ7pAACe/wAAnxUAAJ8r",
    "AACfQQAAn1cAAJ9tAACfgwAAn5kAAJ+vAACfxQAAn9sAAKBDAACgWQAAoG8AAKEUAAChKgAAoUAAAKFWAAChbAAAoYIAAKGYAAChrgAAocQAAKHaAACh8AAAogYAAKIcAACiowAAorkAAKLPAACi6wAAo8sAAKPh",
    "AACj9wAApBMAAKQpAACkPwAApFUAAKRrAACkgQAApJcAAKStAACkwwAApNkAAKTvAAClBQAApRsAAKUxAAClRwAApV0AAKVzAACliQAApZ8AAKW1AAClywAApeEAAKX3AACmDQAApiMAAKY5AACmTwAApmUAAKZ7",
    "AACnOAAAp04AAKdkAACnegAAp5AAAKgpAACovAAAqSoAAKlAAACptwAAqc0AAKnjAACp+QAAqg8AAKolAACqOwAAqlEAAKpzAACqjwAAqqsAAKrBAACq3QAAqvMAAKtVAACr1AAAq+oAAKxZAACs+AAArQ4AAK0k",
    "AACtOgAArVAAAK1sAACuQQAArlcAAK5zAACuiQAArp8AAK67AACu1wAAru0AAK8JAACvHwAArzUAAK9LAACvYQAAr3cAAK/dAACv8wAAsAkAALAlAACwOwAAsOIAALD4AACxDgAAsSQAALE6AACxVgAAsWwAALGC",
    "AACxmAAAsa4AALHEAACyRQAAslsAALJxAACyhwAAsqMAALK5AACzewAAs5EAALOnAAC0EgAAtCgAALQ+AAC0VAAAtGoAALSAAAC0lgAAtKwAALTCAAC02AAAtO4AALUEAAC1GgAAtTAAALVGAAC1XAAAtXIAALWI",
    "AAC1ngAAtbQAALXKAAC14AAAtfYAALcGAAC3HAAAt7UAALfLAAC34QAAt/cAALgNAAC41AAAuOoAALntAAC6AwAAuhkAALovAAC6tAAAusoAALrgAAC69gAAu24AALuEAAC7mgAAu7AAALvGAAC73AAAu/IAALwI",
    "AAC8pwAAvL0AALzTAAC86QAAvP8AAL0VAAC9KwAAvUEAAL1XAAC9bQAAvYkAAL3kAAC9+gAAvhAAAL4mAAC+PAAAvlIAAL5oAAC+fgAAvpQAAL6qAAC+wAAAvtYAAL7sAAC/AgAAv6cAAL+9AAC/0wAAv+kAAL//",
    "AADAFQAAwCsAAMBBAADAVwAAwG0AAMCDAADAmQAAwK8AAMDFAADA2wAAwPEAAMEHAADBHQAAwTMAAMFJAADBXwAAwdsAAMKIAADDOQAAw9QAAMPqAADEAAAAxBYAAMQsAADEQgAAxFgAAMRuAADEhAAAxJoAAMSw",
    "AADExgAAxNwAAMVNAADFpgAAxbwAAMXSAADF6AAAxf4AAMYUAADGKgAAxkAAAMZWAADGcgAAxogAAMaeAADGtAAAxsoAAMbgAADG/AAAxxIAAMcoAADHPgAAx1QAAMdqAADHgAAAx5YAAMeyAADIRwAAyF0AAMjH",
    "AADI3QAAyV8AAMnvAADKbAAAyoIAAMqYAADKrgAAysQAAMraAADK8AAAywYAAMscAADLMgAAy0gAAMteAADL+QAAzA8AAMxuAADNLAAAzUIAAM1YAADNbgAAzYQAAM4UAADOsQAAzxQAAM8qAADPQAAAz1YAAM/0",
    "AADQhwAA0R4AANE0AADRSgAA0ikAANI/AADTTAAA02IAANQXAADUUgAA1H4AANT1AADVcQAA1hAAANaeAADWuwAA1vUAANcvAADXeAAA16gAANfPAADX7QAA2AoAANgpAADYhAAA2K0AANj+AADZZwAA2a8AANoH",
    "AADadgAA2psAANsbAADbiAAA27UAANvrAADcFQAA3D0AANxnAADc1QAA3Y0AAN3SAADePgAA3pEAAN7eAADfDgAA3zcAAN+aAADfyAAA3/sAAOAuAADgZQAA4IMAAODOAADhCgAA4W4AAOG3AADiKAAA4nwAAOLn",
    "AADjCgAA404AAOOAAADj4QAA5B0AAORLAADkeAAA5J8AAOS+AADk5AAA5Q8AAOUqAADlTwAA5boAAOYcAADmaQAA5soAAOcmAADnbwAA6CMAAOhnAADotQAA6Q8AAOlKAADpeAAA6doAAOoaAADqcwAA6tYAAOs6",
    "AADrcgAA69UAAOweAADsYAAA7JUAAOzwAADtLgAA7X8AAO2sAADuCgAA7iQAAO6DAADuuwAA7vEAAO9XAADwOwAA8MsAAPFLAADx0gAA8lwAAPKVAADyvwAA84YAAPQMAAD0cgAA9R0AAPXIAAD2fQAA9y0AAPeL",
    "AAD3+AAA+G8AAPjgAAD5OAAA+Z4AAPn/AAD6YQAA+tAAAPtvAAD72AAA/FQAAP00AAD9xwAA/jwAAP5+AAD+4QAA/2gAAQASAAEAzAABAfMAAQJNAAEDUgABA7IAAQSNAAEFJQABBYwAAQY7AAEGpwABB0EAAQer",
    "AAEIOAABCL0AAQkpAAEJoQABCooAAQsFAAELWQABDBYAAQybAAENHAABDbYAAQ49AAEOuwABDyQAAQ+UAAEQHQABEIsAARDvAAERYAABEcQAARJ9AAES7wABE1cAARPkAAEUbQABFS8AARX2AAEWXQABFp4AARbO",
    "AAEXGgABF3gAARfMAAEYhgABGRoAARlzAAEZjQABGhwAARpoAAEbPgABHBwAARzBAAEdZwABHhkAAR5wAAEfJAABH+oAASByAAEgxQABITEAASISAAEifwABIrsAASNIAAEjmgABI+YAASSaAAElMAABJXkAASXd",
    "AAEmTAABJsYAASc+AAEnmAABKFMAASkQAAEpYwABKccAASobAAEqogABKvcAASuhAAEsWAABLNAAAS0xAAEt2gABLmQAAS6vAAEvCQABL2MAATAQAAEwhQABMTcAATGYAAEyfAABMs4AATP8AAE0LwABNMEAATVD",
    "AAE1lAABNfYAATY+AAE2nQABNzAAATeKAAE4OgABOMcAATkGAAE5kwABOg0AATqNAAE7HQABO3MAATvnAAE8UgABPQIAAT1lAAE9owABPi0AAT7LAAE/fwABQC8AAUB+AAFA/QABQU4AAUHCAAFCMgABQqMAAUM7",
    "AAFDqwABRBgAAURsAAFExQABRT8AAUX+AAFG5AABR4kAAUgdAAFJBgABSWgAAUnIAAFKOAABSwMAAUuzAAFMXwABTREAAU1ZAAFNqQABTiMAAU6eAAFO/gABT4MAAU/LAAFQNgABUS8AAVHJAAFSWAABUrsAAVMs",
    "AAFT6AABVKcAAVVTAAFVxgABVnAAAVbGAAFXbgABWAoAAViSAAFY9wABWVAAAVmhAAFZ9AABWjcAAVq6AAFbFwABXAAAAVyWAAFdTwABXYUAAV4WAAFe2gABX6IAAWAFAAFg6QABYa8AAWIJAAFiXgABYosAAWL3",
    "AAFjMgABY4YAAWO7AAFkCwABZLQAAWUdAAFlrgABZj4AAWbDAAFm6wABZ3cAAWeqAAFn3QABaFIAAWi0AAFpKgABaakAAWo3AAFqxgABa4sAAWwmAAFssQABbSgAAW1bAAFt2wABbmMAAW7aAAFvXgABcAsAAXCc",
    "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",
    "AAJQQwACUKcAAlEXAAJRwAACUiYAAlK5AAJTKQACU5IAAlPxAAJUuQACVWcAAlWjAAJWHwACVn4AAlaxAAJW+QACV1QAAleSAAJYBAACWG0AAlj0AAJZkAACWiMAAlqoAAJbbwACW+cAAlxIAAJcqQACXR0AAl3/",
    "AAJeOQACXqgAAl71AAJffAACX9cAAmBdAAJg4QACYTYAAmGmAAJiGAACYokAAmMLAAJjcgACY8oAAmRIAAJkyAACZPYAAmWCAAJl6gACZlMAAmaxAAJm/AACZ3YAAmgDAAJoZQACaRYAAmm5AAJqDwACap4AAmq4",
    "AAJrCAACa6wAAmv9AAJsRQACbREAAm1bAAJttAACbfAAAm4qAAJudQACbrAAAm7WAAJvlQACb8YAAnBqAAJxAAACcSwAAnFYAAJxrwACckMAAnKcAAJy9AACc20AAnPbAAJ0nAACdM0AAnVCAAJ1qwACdhEAAnZM",
    "AAJ2swACdywAAnfZAAJ4YAACeRMAAnmpAAJ6LAACepIAAnr+AAJ7dwACe+sAAnyyAAJ9CgACfasAAn4UAAJ+YwACfxAAAn9dAAJ/qAACf/gAAoBYAAKAvAACgcEAAoInAAKCdQACgsMAAoMZAAKDYwACg6gAAoQZ",
    "AAKE2wAChUAAAoXNAAKGGwAChnMAAobDAAKHVwACh6IAAofjAAKIJwACiLYAAolAAAKJmAACikQAAorWAAKLGQACi1oAAov1AAKMYQACjNMAAo0bAAKNoQACjkgAAo8MAAKPWgACj7QAApAVAAKQUwACkMcAApEp",
    "AAKRhAACkc8AApInAAKScgACkscAApMNAAKTfgACk+EAApQ4AAKUigAClUMAApWzAAKWUwAClssAApdlAAKXxQACmBIAApiGAAKZEwACmbkAApnqAAKadgACmuEAAptAAAKb5AACnGIAApyYAAKc7QACnXYAAp23",
    "AAKd+AACno0AAp7IAAKfAQACn5cAAp/4AAKgbAACoKgAAqEXAAKheAACogwAAqJOAAKipwACovYAAqN2AAKj0gACpCUAAqSWAAKlRAACpXsAAqW5AAKmLwACpmoAAqaxAAKm+AACp2cAAqftAAKoQwACqLcAAqkd",
    "AAKpZQACqaMAAqoCAAKqWgACqrAAAqsmAAKrZAACq5kAAqwdAAKsggACrMQAAq0UAAKtaQACrb0AAq37AAKubgACrrIAAq9HAAKvpwACsDEAArCzAAKxHgACsXwAArH8AAKyYgACsp4AArL+AAKzPAACs3oAArP/",
    "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",
    "Pf7FZwAB//oB0QTTAnkAAwATtwICBQAAuQG9AD/hAS8RMy8xMAM1IRUGBNkB0aioAAMATv/jBH8A+gAHAA8AFwBfQD00EgElEgEGEhYSAhKWFhYONAIBJQIBBgIWAgIClgYGNAoBJQoBBgoWCgIKluAO8A4CDg4Y",
    "GRAACJsUBAyoAD8zM+EyMhESATkvXeFdXV0zL+FdXV0RMy/hXV1dMTA3MhUUIyI1NCEyFRQjIjU0ITIVFCMiNTTNf39/Ahh/f38CGX9/f/qLjIyLi4yMi4uMjIsAAwBGAZEEhQQOABMAHQAnAF+5ABD/4LMJDEgO",
    "uP/gQDIJDEgGIAkMSAQgCQxIHgoAFAQFI6sPDwEPKRmrBSYWrgoAAgwICCAcrhI/Ao8C3wIDAgAvXTPhMjMvMxI5OeEyAS/hEN5d4REXOTEwKysrKwEGIyImNTQ2MzIXNjMyFhUUBiMiAyYjIgYVFBYzMjcWMzI2",
    "NTQmIyICYnaad5WVd6ZsdKV2kpdxq7VSbUFQUENo5FZrQVBUQGcCbdWujYa129Wsj4O5AUK4a09RZbK5bU5PZwAAAA8AugADAAEECQAAARYAAAADAAEECQABADABFgADAAEECQACAA4BRgADAAEECQADACoBVAAD",
    "AAEECQAEADABFgADAAEECQAFACQBfgADAAEECQAGACoBogADAAEECQAHAJwBzAADAAEECQAIACgCaAADAAEECQAKAOACkAADAAEECQALADgDcAADAAEECQAMAFwDqAADAAEECQANAFwEBAADAAEECQAOAFQEYAAD",
    "AAEECQASACYEtABEAGkAZwBpAHQAaQB6AGUAZAAgAGQAYQB0AGEAIABjAG8AcAB5AHIAaQBnAGgAdAAgAKkAIAAyADAAMAA3ACwAIABHAG8AbwBnAGwAZQAgAEMAbwByAHAAbwByAGEAdABpAG8AbgAuAAoAQwBv",
    "AHAAeQByAGkAZwBoAHQAIACpACAAMgAwADAAOAAtADIAMAAwADkAIABXAGUAbgBRAHUAYQBuAFkAaQAgAEIAbwBhAHIAZAAgAG8AZgAgAFQAcgB1AHMAdABlAGUAcwAgACgAaAB0AHQAcAA6AC8ALwB3AGUAbgBx",
    "AC4AbwByAGcALwApACAAYQBuAGQAIABRAGkAYQBuAHEAaQBhAG4AIABGAGEAbgBnAFcAZQBuAFEAdQBhAG4AWQBpACAATQBpAGMAcgBvACAASABlAGkAIABNAG8AbgBvAFIAZQBnAHUAbABhAHIAVwBlAG4AUQB1",
    "AGEAbgBZAGkAIAAtACAATQBpAGMAcgBvACAASABlAGkAVgBlAHIAcwBpAG8AbgAgADAALgAyAC4AMAAtAGIAZQB0AGEAVwBlAG4AUQB1AGEAbgBZAGkATQBpAGMAcgBvAEgAZQBpAE0AbwBuAG8ARAByAG8AaQBk",
    "ACAAaQBzACAAYQAgAHQAcgBhAGQAZQBtAGEAcgBrACAAbwBmACAARwBvAG8AZwBsAGUAIABhAG4AZAAgAG0AYQB5ACAAYgBlACAAcgBlAGcAaQBzAHQAZQByAGUAZAAgAGkAbgAgAGMAZQByAHQAYQBpAG4AIABq",
    "AHUAcgBpAHMAZABpAGMAdABpAG8AbgBzAC4AQQBzAGMAZQBuAGQAZQByACAAQwBvAHIAcABvAHIAYQB0AGkAbwBuAFcAZQBuAFEAdQBhAG4AWQBpACAATQBpAGMAcgBvACAASABlAGkAIABpAHMAIABhACAAaAB1",
    "AG0AYQBuAGkAcwB0ACAAcwBhAG4AcwAgAHMAZQByAGkAZgAgAHQAeQBwAGUAZgBhAGMAZQAgAGQAZQBzAGkAZwBuAGUAZAAgAGYAbwByACAAdQBzAGUAcgAgAGkAbgB0AGUAcgBmAGEAYwBlAHMAIABhAG4AZAAg",
    "AGUAbABlAGMAdAByAG8AbgBpAGMAIABjAG8AbQBtAHUAbgBpAGMAYQB0AGkAbwBuAC4AaAB0AHQAcAA6AC8ALwB3AHcAdwAuAGEAcwBjAGUAbgBkAGUAcgBjAG8AcgBwAC4AYwBvAG0ALwBoAHQAdABwADoALwAv",
    "AHcAdwB3AC4AYQBzAGMAZQBuAGQAZQByAGMAbwByAHAALgBjAG8AbQAvAHQAeQBwAGUAZABlAHMAaQBnAG4AZQByAHMALgBoAHQAbQBsAEwAaQBjAGUAbgBzAGUAZAAgAHUAbgBkAGUAcgAgAHQAaABlACAAQQBw",
    "AGEAYwBoAGUAIABMAGkAYwBlAG4AcwBlACwAIABWAGUAcgBzAGkAbwBuACAAMgAuADAAaAB0AHQAcAA6AC8ALwB3AHcAdwAuAGEAcABhAGMAaABlAC4AbwByAGcALwBsAGkAYwBlAG4AcwBlAHMALwBMAEkAQwBF",
    "AE4AUwBFAC0AMgAuADAAVwBlAG4AUQB1AGEAbgBZAGkAIABNAGkAYwByAG8AIABIAGUAaQADAAAAAAAA/wAAZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAFAAL//wADAAEAAAAMAAAAAAAAAAIACAAAAMYAAQDI",
    "APwAAQD+AV8AAQFhAWcAAQFpApYAAQKYA4oAAQOMBF4AAQhkCMIAAQABAAAACgAMAA4AAAAAAAAAAQAAAAoAFgAYAAFsYXRuAAgAAAAAAAAAAAAAAAEQAAVa94kAAAgA/0j56A4YAAAAAQAAAAAAAAAAAAAAAAAB",
    "CAAFuAPABhgDwAYYBggGCAYIBggGCAYIBggE4ASwBFAEsATYBLgGAAYABkgAAAEwATgGYAZgBmAC4AZgBmADgAYIBeAGWAYIBhgGeAZ4BjAGYAYYBngGgAZ4BngGcAaIBmgGUAZ4BmAGEAZ4BngGAAZ4BngGEAaI",
    "BngFkAYABggGCAZ4BoAGaAaABlAGeAZ4BngGgAZ4BoAGgAZ4BngGgAZ4BngGeAZ4BngGeAZ4BogGgAZ4BngGeAZ4BoAGeAZ4BngGeAaABngGeAaABngGeAZ4BngGeAZ4BogGgAZ4BogGeAZ4BngGgAZ4BogGeAZ4",
    "BngGgAaABngF+AZ4BngGgAZ4BngGiAZYBnAGgAZwBkAGiAaIBoAGYAYgBjAGeAZ4BkAGeAZ4BogGgAaABngGEAZABngGeAYoBhgGEAZwBngGcAZ4BngGgAZwBngGcAZ4BngGcAZ4BoAGkAZwBngGgAaIBnAGeAZ4",
    "BngGiAZ4BngGeAaIBngGOAZ4BlAGeAaABogGeAZ4BngGgAYABngGeAY4BjgGOAY4BngGgAYQBjAGEAZ4BnAGOAZ4BngGYAXgBngGCAZ4BhgGCAaABngGMAaABogGkAY4BngGaAaABjgGgAZoBoAGMAZABkgGQAaQ",
    "BoAGKAaIBpAGWAYoBoAGgAaABoAGeAZ4BkAGiAY4BjgGCAY4BjgGOAY4BjgGOAYgBoAGeAZYBmAGgAZYBoAGeAZgBlgGeAZ4BogGiAaABogGgAZ4BogGgAZwBoAGeAZ4BngGeAaABpAGeAZ4BngGgAZ4BngGgAaA",
    "BjAGiAaABogGiAaIBpAGiAaIBogGiAaIBogGiAaIBogGiAaIBogGeAZ4BjgGgAZ4BnAGaAZoBngGeAYYBkAGSAZIBkgGSAZIBkgGeAZ4BggGeAYwBiAGCAaIBoAGeAZ4BngGeAXwBigGiAaABoAGgAaABoAGgAaA",
    "BoAGEAZwBngGIAZABngGeAZoBngGcAZABngGgAZIBmgGaAaABngGeAaABoAGeAZ4BngGeAaABmAGYAZ4BngGeAZ4BoAGIAZ4BoAGeAZ4BngGgAaQBogGeAZ4BngGgAaABoAGeAaABngGeAZgBngGgAZ4BngGeAZ4",
    "BngGeAaABngGeAZ4BjgGeAZ4BngGeAZ4BngGeAZ4BoAGgAZ4BngGeAaABoAGeAaABngGeAZ4BngGgAaIBogGgAZ4BngGeAZ4BngGiAZ4BngGeAaABngGeAZ4BoAGeAZ4BoAGgAZ4BngGeAZ4BngGgAZ4BngGeAaI",
    "BngGgAaABngGkAZ4BoAGeAZ4BngGgAZ4BngGeAaABngGeAaABnAGgAZ4BoAGeAZ4BngGiAaABngGGAYgBhgGOAZ4BkgGUAZIBngGUAYwBngGSAaABmAGiAZQBjgGeAZABkgGgAZIBngGeAZ4BngGgAZwBkAGeAaI",
    "BngGeAZ4BngGiAZ4BngGeAZ4BjAGgAaABoAGgAZ4BngGeAZ4BoAGeAaABngGeAZ4BngGeAZ4BoAGeAZ4BoAGeAZ4BngGeAaABogGeAYQBnAGgAXwBngGMAaABngGYAaIBngGiAaIBmgGaAZoBnAGcAaABngGgAZ4",
    "BngGeAZ4BmgGgAZ4BoAGgAaABoAGaAZ4BmgGeAZ4BngGeAZwBlgGaAaABngGaAZ4BngGeAZYBoAGeAZ4BoAGeAYwBngGeAaABmgGeAZ4BjAGeAaABngGgAaABoAGgAaABoAGGAYYBjgGeAYgBngGeAYYBngGMAZ4",
    "BjAGOAZ4BoAGkAaIBogGkAZ4BoAGeAZ4BpAGmAZ4BngGgAaABiAGeAZ4BngGcAZ4BmAGeAYoBkgGiAZ4BngGcAaABngGeAYwBigGeAY4BngGMAZ4BngGeAZABggGgAaABogGeAaQBoAGgAaABngGgAaABmgGgAaA",
    "BogGiAaQBogGiAaABngGeAaABngGiAaIBogGiAaIBogGiAaIBogGiAaIBngGiAZ4BngGaAZ4BoAGWAZ4BkgGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BogGgAZ4BngGeAZ4BngGeAaABngGgAaABigGUAZQ",
    "BoAGcAZ4BoAGKAZ4BjAGMAZwBkgGSAZ4BngGgAaABoAGeAZIBkgGgAaABhgGeAZIBoAGgAZ4BngGgAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGiAY4BogGgAZ4BoAGeAZ4BngGeAaABoAGeAZ4BngGeAZwBnAGQAZY",
    "BiAGMAZ4BogGiAaIBqAGgAaABoAGeAZ4BngGgAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGgAZ4BngGiAZ4BoAGeAagBoAGeAaIBngGaAZoBkAGeAZ4BngGgAZ4BngGeAZ4BoAGMAZYBoAGMAZIBoAGYAZwBogGgAaA",
    "BngGgAZ4BngGeAZ4BoAGgAZIBngGSAZwBkgGaAZ4BkgGgAZwBkgGgAZIBngGgAZIBogGYAZ4BmAGSAaABkgGgAZ4BkgGeAaABngGGAaABngGQAZIBnAGOAZYBlAGgAZ4BngGeAZ4BngGkAaABngGeAZ4BngGiAZw",
    "BpAGkAaQBpAGkAaQBngGSAZ4BoAGMAaABkgGgAZ4BnAGeAYwBoAGYAZYBmAGcAZwBngGiAZ4BoAGKAaIBjgGOAY4BngGSAY4BmgGOAZQBlAGeAZ4BjAGSAX4BpAGgAaIBoAGgAaABmgGSAY4BjgGYAZQBogGkAaA",
    "BogGQAaABoAGgAZ4BbgFuAW4BhAFyAXQBbgFuAW4BhgEoAEwAygBMAW4BdAFuAXIBcgFwAW4BcgFuAXQBcgEIAQgBOAD6ATgBcgFuAXABbgFyAW4BbgFuAXIBbgFuAW4BbgFuAW4BbgF0AW4BdAFuAXIBbgFuAW4",
    "BbgFuAW4BbgFuAW4BbgFwP9IBiAEYAYYBGAGGARgBiAEYAYYBhAGEAYYBhgEYARgBGAEYARgBGAEYAVwBEgESARIBEgESARIBbgGGAW4A1gCeAaAA2gDKANgBnAFMARoBAgGgAZIBngGSAaABjAGYAYwBoAGcAaA",
    "BiAGQAZwBjgD4AaABigFcAUYBiAD0AaIBkAD4ATgBngGgAIoBSAEqAVgBNgEwATYBEgFAATYBEAEiAZ4BngGSAToBkgEuASYBFgEgAR4BEAEYAZ4BAgDwATIBngGeAaYBpAEYATABngFkAZ4BoAGeAZYBngGaAaA",
    "BngEiAKwBfgGIAOoBoAGcAZwBkADSAZIBEgGiAZ4BoAGeAZ4BnAGeANoBkAGcAT4BRAE8ARIBQgEsAUoBHgEMASABIgDkAOQBAgGOATYBJgFAAT4BQAE0ASQA7gEcAaQBJgE4AYgBXgF6AZ4AkgFiAVQBQgCcAaA",
    "BnAGKAUwBngGeAaABQAGeALwBjgGIAaABmgGkAZ4BngGIAZ4BoAGgAZ4BngGYAZ4BogGiAZ4BjgGMAaABjgGgAaABngGgAZ4BNAC+AY4BjAGeAZ4BngGgAYIBlgGUAZIBogDQAXwBmgGcAYgBngGeAZ4BoAGiAZ4",
    "BhgGeANIBoAGeASYBoAGiAZIBigDQAZ4AxgGgAZ4BngFqAZABogGeAKQBngGiAJ4AggGgAZABngGGAZIAggGcAaABjgGOAZ4AagGeAKgAggGgAYABngGgAY4BjgGcAYYBlAC2AXQBoAGgAZ4BngGgAY4BngF2AXI",
    "BcgFwAXABoAFyAXIBcgCGAZ4A2gGeALYBmAGgAY4BkgGSAYQBngGOAY4BoAGeAZ4BngGOAYYBngGMAaABngGeAZ4BngGeAZ4BkgGKAZ4BoAGeAZABnAGiAZ4BhgGeAJYBegBgAaABngGeAaABngGEAZ4BngGIAYQ",
    "BoAGSAaABngGKAYYBngGgAY4BoAGCAZ4BngGgAZ4BngGeAZ4BoAF4AZIBngGAAZwBhAGeAY4BngF6AZ4BngGgAZ4BkAGiAZ4BngGeAYwBngGgAZ4BjAGeAZ4BjgGeAZ4BlAGOAZwBnAGiAZ4BjAGeAZ4BngGeAZ4",
    "BngGGAaABoAGKAaABMgGeAYQBOgGeAaABkAGgAZ4BngGcAYoBoAGgAIIBPAGgAZ4BjAGeAN4A1gGcAZwBjAGeAZ4BmAGeAaAAmgGiAToBegBSAZ4BnAGgAYIBngGeAZYBoAEEAZ4A2gGCAYwBoACqAYwBfgGKAZ4",
    "BkAC2AZgBngE2ATYBngDAAZoBoAGaAaIBoAGgAaABngGgAZ4BigGQAS4BiAGKAaABngGeAZ4AuAGeAaIBngGiAZwBnAGUAaABngGSAaABRgGYAZ4BPgGaAZYBlgGeAZgBmAGaAY4BhgGeAMgBoAGeASIBlgGeAZ4",
    "BngGcAaIASAGgAZABogGiAZ4BngGiAZ4BngGgAY4BhgGGAZYBjAE6AX4BmgGgAaABoAGgAZ4BkAGgAZ4AlAGgAOoBngGGAaABiADAAZgBngGeAY4BmgGeAZ4BngC4AaIBggGCAaABngDMAZ4BKAGgAZYBngGeAKg",
    "BnAGYAaABngGeAZ4A7gGeAYgAqgGCAaABpAGiAYoBjAFyAUwBjAGgAZ4BngGWAK4BogGiAJwAqgGMAY4BjgGMAZ4BmgEeAY4BlAESAYwAtAGAAZwBnAGcAZoBoAGUAZwBjAGeAZ4BUgGeAZ4BDAGgAZgBngGeAZ4",
    "BngEgAZ4BjAGMAKQBkAGeAaABoAGOAXgAigGiAR4AXgFeAVYBWAGUAZABjAGEAaIBjgGCAZ4BngGeAY4BogEMAYQBogGeAZ4BlgGeAZ4BoAGcAZwBngGcAZ4BggGeAaABoAGGAXIBfgGeASYBngCGAQwBjgGeAZ4",
    "BngGeAYoBjgGIAZ4BoAGeAZIBiAGgAZ4BhAEgAY4BfgGSAX4BhAGcARQBnAGQAOYBoAGgAZ4BPAGeAZ4BngGOAZQBjgGUAY4BngGeAZ4BngGSAQ4BoAGSAZ4BngGeAJIBUgGUAZoBngGOAYgBngC8AKgBhAGEAaI",
    "BoAGgAaABogGkAaABnAGeAYYBogGgAY4BfAGeAZ4BogGgAIgBoAGeAZ4BngGgAZIBjgDgAZABlAGGAY4BoAGIAZ4BngGAAZwBngGeAZ4BogF4AaABoAGeAY4BlgGWAZ4BoAGSAZ4BigGeAZ4BhgGMAZ4BngGUAZo",
    "BmAGgAYIBhgGIAYAAdgGQAYwBkgGeAYgBngGgAaABhgGgAYYBhgGSAZwBoAGeAZ4BlgGgAYABnAGaAZ4BoAGUAaABkgGSAZIBngGcAaABmgGeAZoBjAGeAYQBngGcAaABngGQAYgArgGSAPQBoADkAaIAsAGeAYY",
    "BngGGAZoAygGeAaABoAGgAY4BngGiAZ4BlgGWAaQAxAGOAYgAeAGeAZ4BngGEAYQBnADkAaIBoAGgALgBmgDIAYQBngGeAaABlgGiAZ4BngGcATIAMAGMAYgBoAGaAZ4BoACsAZ4BoAEeAaIBfgESAZIBkgGgAZ4",
    "BngGeAZ4BngGIAZ4A6AGaAaABngGeAZ4BngGeAMwA4AGQAZ4BnAGAAZ4BngGcAZ4AngGeAMoBngGeAYoBogCQAaIBngGeAZoBngGMAZ4BhAGeAZ4BngGeAaABnAGMAGwBngGCAZ4BngGeADoBngGeAE4BgAGkAZ4",
    "BogF4AXgBjAGeAZ4BngGOAaABnAGaAZ4BoAGCAZ4BngGeAZ4BkAGQAYwBjACaAHIAiACQAZ4BngGeAZ4BogGiAZ4BfAF8AY4BmAGeAZ4BngGYAZYBogGeAZ4BkgGaAaABoAAAAW2BbYFtgXHBbYFtgYUBKIBBgJ5",
    "AS0FtgXNBbYFywXLBb4FtgXLBbYFzQXLBGYEZgTJA+kEyQW2BbwFtgXLBbYFtgW2BcsFtgW2BbYFtgW2BbYFtgXNBbYFzQW2BcsFtgW4BbYFtgW2BbYFtgW2BbYFtv9IBF4GFAReBhQEXgYfBF4GFAYOBg4GFAYU",
    "BF4EXgReBF4EXgReBF4FbwRKBEoESgRKBEoESgW2BhQFtgNaBcUDXgR7AnkA+gQO",
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
