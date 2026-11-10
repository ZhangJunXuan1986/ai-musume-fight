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
VERSION = "v3.2-4399-keys"

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
            ("P1 攻击", "J 普攻     K 跳跃     J+K 变身（满 3 格气）"),
            ("P1 技能", "U 技1     I 技2     O 技3     L 奥义"),
            ("P1 功能", "Q 闪避     E 净化     Z 秘卷"),
            ("", ""),
            ("P2 移动", "← / → 左右    ↑ 上挑修饰    ↓ 防御"),
            ("P2 攻击", "1 普攻     2 跳跃     1+2 变身"),
            ("P2 技能", "4 技1     5 技2     6 技3     3 奥义"),
            ("P2 功能", "7 闪避     8 净化     9 秘卷"),
        ]
        for i, (a, b) in enumerate(rows1):
            y = 192 + i * 44
            if a:
                draw_text(s, a, left.x + 20, y, 17, COL_GOLD, True)
                draw_text(s, b, left.x + 130, y, 16, COL_TEXT)
        draw_text(s, "旧「冲刺 / 远攻 / 必杀 / 援助」已删除，键位改挂新技能",
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
        draw_text(s, "点左上「返回主页面」或按 Esc 退出", SCREEN_W // 2, 664, 16,
                  COL_DIM, align="center")

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
        draw_text(s, "P2  1攻 2跳  4技1 5技2 6技3 3奥义  7闪 8净 9卷",
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
    "AAEAAAATAQAABAAwR0RFRhURFqoAA4J4AAAAQEdQT1MAGQAMAAOCuAAAABBHU1VCbIx0hQADgsgAAAAaT1MvMmYwBBgAAAG4AAAAYGNtYXAW+rM1AAAk9AAAHHRjdnQgRJ1NcgAASvAAAAIQZnBnbXPTI7AAAEFo",
    "AAAHBWdhc3AABAAHAAOCbAAAAAxnbHlm5szuVwAAcKAAAwwXaGVhZBagftkAAAE8AAAANmhoZWEPeQ6XAAABdAAAACRobXR4OaDi8wAAAhgAACLcbG9jYQs4yMsAAE0AAAAjoG1heHALkAKDAAABmAAAACBuYW1l",
    "lU2vyQADfLgAAAWUcG9zdP8DAGYAA4JMAAAAIHByZXBBvdqCAABIcAAAAn52aGVhEr4JcgADguQAAAAkdm10eP9h260AA4MIAAAR0AABAAAAADMzR0w3Dl8PPPUCPwgAAAAAAMY/xrAAAAAA5xg7RP/w/hQICAag",
    "AAAACAAAAAEAAAAAAAEAAAd+/h0AAAgA//D/8ggIAAEAAAAAAAAAAAAAAAAAAAiHAAEAAAjnAGYADQCIAA4AAgAQAC8AWgAAAh8BYwAEAAEAAwWTAZAABQAIBZoFMwAAAR4FmgUzAAAD0ABmAfIAAAILBgYDCAQC",
    "AgSAAAADCAHkYAAAABAAAAAAV1FZRgBAACD/XgYf/hQAhAd+AeMAEAAAAAAAAARKBbYAAAAgAAIIAAJYCAABUAQAAEgIAAFQBAAASAgAANgIAADYCAAA2AgAANgIAADYCAAA2AgAANgE0AC4BNABGATQALgE0ACA",
    "BNAAkATQALAIAACwCAAAsAgAAfAIAAAACAAAMAgAADAIAAQACAAA2AgABAAIAAHgCAAEAAgAAYAIAACoCAAAeAgAAKAIAACgCAAAkAgAAFgIAACgCAAAkAgAAHAIAAB4CAAAeAgAAFAIAABgCAAA4AgAALAIAACw",
    "CAAAeAgAAHgIAACICAAAoAgAAHAIAABYCAAAyAgAAGgIAAB4CAABAAgAAJAIAAB4CAAA2AgAAGgIAABoCAAAcAgAAIAIAABgCAAAgAgAAGgIAABgCAAAWAgAAHAIAABYCAAAUAgAAFAIAABQCAAAUAgAAFAIAABY",
    "CAAAWAgAAFAIAABQCAAASAgAAQgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAaAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABoCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABQCAAAUAgAAGgIAABQCAAAUAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABwCAAAYAgAAJAIAABoCAAAcAgAAIAIAABoCAAAWAgAAGgIAACI",
    "CAAAeAgAAGgIAABgCAAASAgAAGgIAADwCAAAcAgAAGAIAACICAAAaAgAAGgIAABoCAAAaAgAAGgIAAB4CAAAaAgAAHgIAABYCAAAaAgAANAIAADYCAAAgAgAAJgIAACwCAAAyAgAAHAIAABoCAAAgAgAAHgIAABg",
    "CAAASAgAAEgIAACACAAAkAgAAIgIAABgCAAAaAgAADgIAABgCAAASAgAAIgIAABYCAAAcAgAAHgIAABYCAAAgAgAAGgIAABoCAAASAgAAHAIAABoCAAAWAgAAIAIAABoCAAAUAgAANAIAAB4CAAAiAgAAIAIAAB4",
    "CAAAiAgAAGgIAAEwCAAAmAgAAMgIAADQCAAAWAgAAHgIAABQCAAAUAgAAFAIAABQCAAAaAgAAGAIAACICAAAaAgAAGgIAABoCAAAUAgAAGgIAACYCAAAoAgAAKAIAAFICAAAiAgAAHgIAADACAAAaAgAAGgIAACo",
    "CAAAWAgAAGgIAACgCAAAcAgAAFAIAADICAAAYAgAAFAIAADgCAAAYAgAAHAIAACgCAAAWAgAAKAIAACQCAAAgAgAAFgIAABgCAAASAgAALAIAACgCAAAoAgAAGgIAACgCAAAqAgAAKgIAACYCAAAqAgAAKgIAACg",
    "CAAAWAgAAHAIAAC4CAAAuAgAAOAIAAC4CAAAuAgAALgIAAC4CAAAuAgAAMAIAADACAAAcAgAAEAIAABYCAAAWAgAAHAIAABYCAAAWAgAAFAIAABYCAAAgAgAAGgIAABYCAAAUAgAAFgIAABYCAAAcAgAAHAIAACg",
    "CAAAeAgAAIAIAABgCAAAWAgAAFgIAABgCAAAaAgAAHAIAABQCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAFgIAABoCAAAaAgAAHgIAACICAAAWAgAAGgIAACYCAAAgAgAAHgIAACYCAAAcAgAAIgIAABo",
    "CAAAmAgAAGAIAABwCAAAkAgAAJAIAACACAAAaAgAAHAIAACACAAAaAgAAJgIAABICAAAgAgAAGgIAABoCAAAaAgAAKgIAABYCAAAYAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGgIAABYCAAAeAgAAGgIAAEo",
    "CAAAaAgAARAIAADACAAAWAgAAJAIAACICAAAmAgAAIgIAABgCAAAmAgAAIAIAABwCAAASAgAAFAIAABQCAAASAgAAFAIAABQCAAAUAgAAFAIAABgCAAAYAgAAHgIAAB4CAAAaAgAAJAIAADACAAAiAgAAIgIAACI",
    "CAAAiAgAANgIAAD4CAAAgAgAAFgIAABoCAAAUAgAAFAIAABgCAAAYAgAAFgIAABgCAAAWAgAAFAIAABYCAAAWAgAAHAIAABoCAAAaAgAAFAIAABICAAASAgAAEgIAABICAAAWAgAAFAIAABQCAAAWAgAAFAIAABQ",
    "CAAAWAgAAFAIAABgCAAAaAgAAFgIAABYCAAAaAgAAFAIAABoCAAAaAgAAHgIAACICAAAWAgAAGgIAABYCAAAaAgAAFgIAABoCAAAoAgAAFAIAABQCAAAUAgAAFgIAABYCAAAUAgAAFAIAABYCAAAUAgAAFgIAABY",
    "CAAAWAgAAGAIAABYCAAAWAgAAFAIAABgCAAAUAgAAFgIAABgCAAAUAgAAFAIAABQCAAAWAgAAFAIAABYCAAAYAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAHgIAABQCAAAYAgAAFAIAABACAAAYAgAAFAIAABg",
    "CAAAWAgAAFgIAABACAAAYAgAAGAIAABgCAAAQAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABYCAAAYAgAAFgIAABgCAAAYAgAAFgIAABYCAAAYAgAAGAIAABgCAAAWAgAAFgIAABYCAAAWAgAAIgIAADQ",
    "CAAAkAgAAGgIAABYCAAASAgAAGgIAABQCAAAaAgAAHgIAABoCAAAUAgAAFAIAADACAAAWAgAAHAIAACACAAAqAgAAFgIAACACAAAUAgAAHAIAACwCAABEAgAAHgIAACYCAAAuAgAAGAIAABoCAAAkAgAAFAIAABw",
    "CAAAaAgAAGgIAACQCAAAkAgAAIgIAABYCAAAaAgAAHgIAABoCAAAaAgAAHgIAABYCAAAaAgAAGgIAABYCAAAWAgAAFgIAACICAAAkAgAADAIAACQCAAAMAgAADAIAABICAAAWAgAAIAIAABQCAAASAgAAEgIAAAw",
    "CAAAaAgAAGAIAABgCAAAYAgAAHgIAABICAAASAgAAEgIAABICAAASAgAAFAIAABICAAAUAgAAGAIAABgCAAASAgAAFAIAABQCAAASAgAAEgIAAA4CAAAUAgAAFAIAABICAAAUAgAADgIAABoCAAAcAgAAGgIAABo",
    "CAAAWAgAAIAIAABICAAASAgAAHAIAACQCAAAaAgAAQgIAACICAAAeAgAAFgIAABwCAAAYAgAAFgIAABYCAAAaAgAAGgIAABoCAAAWAgAAGgIAABoCAAAWAgAAGAIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABY",
    "CAAAWAgAAFgIAABYCAAAYAgAAGAIAABgCAAAWAgAAFgIAABgCAAAWAgAAFgIAABYCAAAYAgAAGAIAABYCAAAWAgAAFgIAABYCAAAaAgAAGgIAABICAAAcAgAAFAIAABgCAAAaAgAAGgIAABYCAAAaAgAAGgIAABY",
    "CAAAaAgAAGgIAABoCAAASAgAAEgIAABQCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAcAgAAGgIAABoCAAAaAgAAGgIAABoCAAAYAgAAIAIAABYCAABAAgAARAIAADQCAAAeAgAAGAIAADoCAAAmAgAAEAIAABI",
    "CAAASAgAAEAIAABoCAABEAgAAKgIAABoCAAAaAgAAGgIAABoCAAAUAgAAGgIAABoCAABUAgAAJAIAAAwCAAAkAgAAGgIAABoCAAAUAgAAHgIAACgCAAAoAgAAGgIAACgCAAAiAgAAIgIAACICAAAYAgAAFgIAABY",
    "CAAAUAgAAFAIAABICAAAOAgAAFAIAABICAAAUAgAADgIAABACAAASAgAAGgIAABoCAAAaAgAAEgIAABYCAAAkAgAAEgIAAA4CAAAOAgAAFgIAAA4CAAAOAgAAFgIAABICAAASAgAAJgIAABgCAAAcAgAAGgIAACA",
    "CAAAaAgAAIAIAABoCAAAeAgAAGgIAABoCAAAUAgAAGAIAABoCAAAaAgAAGAIAABoCAAAaAgAAGgIAABwCAAAaAgAAGgIAABQCAAAcAgAAFAIAABYCAAAWAgAAGgIAABoCAAAcAgAAHAIAABYCAAAcAgAAGgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAWAgAAMgIAAB4CAAAeAgAAGgIAABY",
    "CAAAUAgAAGAIAABwCAAASAgAAGgIAABgCAAAUAgAAFAIAABQCAAAkAgAAFgIAABQCAAAiAgAAFAIAABoCAAAUAgAAEAIAABYCAABIAgAAJAIAABgCAAAgAgAAGgIAAB4CAAAeAgAAGgIAAB4CAAAgAgAAGgIAABo",
    "CAAAgAgAAHgIAAB4CAAAaAgAAGgIAACACAAAaAgAAGgIAAB4CAAAgAgAAIAIAABQCAAAWAgAAFAIAABgCAAAWAgAAEgIAABQCAAAYAgAAEgIAABICAAAaAgAAFAIAABACAAASAgAAEgIAABYCAAAaAgAAJgIAABo",
    "CAAAaAgAAEgIAACACAAAaAgAAEAIAABgCAAAYAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABo",
    "CAAAcAgAAHAIAACQCAAAaAgAAGAIAABwCAAAaAgAAHAIAABgCAAAgAgAAGAIAABgCAAAYAgAAEgIAABoCAAASAgAAEgIAABICAAAcAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABgCAAASAgAAEgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAHAIAABoCAAAaAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABg",
    "CAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGgIAAB4CAAAKAgAAGgIAABoCAAAQAgAAIgIAABwCAAAYAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABICAAAUAgAAFAIAABw",
    "CAAA0AgAANAIAADQCAAA0AgAANAIAADQCAAAqAgAAKgIAACgCAAAoAgAAKAIAACgCAAAqAgAAIgIAACgCAAAiAgAAKAIAACgCAAAYAgAAHgIAACICAAAYAgAAGAIAABoCAAAaAgAAGAIAABoCAAAaAgAAGgIAABo",
    "CAAAgAgAAGgIAABoCAAAWAgAAFAIAABgCAAAaAgAAHAIAABQCAAAUAgAAGAIAABYCAAAYAgAAFgIAACQCAAAaAgAAEgIAABICAAASAgAAFAIAABoCAAAaAgAANgIAACACAAAaAgAAIAIAACACAAAgAgAAHAIAABg",
    "CAAAUAgAAFgIAABgCAAAYAgAAOgIAABQCAAAYAgAA4AIAALoCAABoAgAAlAIAADwCAABuAgAA6AIAAMQCAACIAgAAdAIAAIwCAABUAgAASgIAAFgCAACEAgAAjAIAAKYCAACOAgAAjAIAAHgCAACSAgAAjAIAAIo",
    "CAACOAgAAjAIAAGoCAABiAgAAjAIAAIwCAACMAgAAjgIAAD4CAABaAgAAiAIAAHICAAB6AgAAjAIAAIwCAABoAgAAdAIAAIoCAACAAgAAiAIAAKACAABUAgAAaAIAAFgCAACSAgAAWAIAAIQCAACAAgAAZgIAAGw",
    "CAABaAgAAIgIAAGACAABkAgAAdgIAAM4CAACEAgAApAIAAIICAAAAAgAAxAIAAIoCAACMAgAAlAIAAHYCAACCAgAAhAIAAHYCAACGAgAAkgIAAIQCAACaAgAAlAIAAEQCAACGAgAAfgIAAIwCAAB2AgAApgIAAJo",
    "CAACMAgAAhgIAAHACAABGAgAAdAIAAHACAACUAgAAmgIAAO4CAACKAgAAjAIAAEICAAAaAgAAGAIAABgCAAAeAgAA+gIAAGoCAACkAgAAngIAAIoCAACgAgAAmAIAALQCAACSAgAAnAIAAJICAACaAgAAogIAAJ4",
    "CAACmAgAAlgIAAKQCAAC2AgAAnAIAACACAAD8AgAA9gIAAGwCAAAiAgABBAIAABoCAADqAgAAKAIAABoCAAAYAgAAhAIAABQCAABmAgAAGgIAAFICAAAiAgAAnAIAACwCAAAiAgAAygIAABoCAAAeAgAAGgIAAB4",
    "CAADAAgAAJAIAABQCAAAeAgAA7AIAABoCAAAaAgAAQAIAABoCAAAYAgAAFAIAAEACAABAAgAAPAIAABwCAAAsAgAAFAIAAEACAAAcAgAAGgIAACACAACSAgAAOgIAACgCAAAaAgAAGAIAAE4CAABKAgAAZAIAAF4",
    "CAADCAgAAKAIAAB4CAAAaAgAAHAIAAEQCAADSAgAAIAIAAB4CAAAeAgAAlgIAAKgCAABsAgAAGgIAACACAAAaAgAAFAIAAGYCAAAiAgAAiAIAAH4CAACwAgAAIgIAAE4CAADWAgAAXAIAAGICAACOAgAAfgIAAIA",
    "CAACEAgAAGAIAABYCAAAaAgAAdAIAAHgCAACEAgAAVgIAAHACAABMAgAAHAIAACACAAAkAgAAVAIAABoCAAAiAgAAYAIAABoCAAAiAgAASgIAACICAAAYAgAAJgIAAGACAABeAgAAkAIAAKICAABkAgAAbAIAAGY",
    "CAACCAgAAMgIAACICAABgAgAAIgIAAKoCAACOAgAAFgIAABwCAAC4AgAAIgIAAMACAADeAgAA3gIAAMQCAADQAgAA2gIAAUACAAAYAgAAvAIAAIYCAACsAgAADgIAAK4CAADSAgAAoAIAABoCAAAaAgAAtgIAABo",
    "CAAAYAgAAFgIAABgCAAAaAgAAHAIAAKgCAACqAgAAyAIAABQCAAAiAgAA1AIAABgCAACqAgAAfgIAAKoCAAC6AgAAqAIAAWACAAAWAgAAzAIAALACAAAoAgAAEAIAAMYCAAAiAgABEgIAAKoCAACWAgAAGgIAABY",
    "CAACyAgAAFgIAABYCAAAaAgAAmAIAAHYCAABYAgAAvAIAAKQCAAAeAgAAEgIAABICAABMAgAAhAIAACACAAAcAgAAIAIAABYCAACqAgAAkgIAANACAAC+AgAAmgIAALYCAAAqAgAAdgIAALoCAAAmAgAAGgIAARI",
    "CAACiAgAAIAIAAQoCAAAgAgAAcAIAAL4CAADAAgAArAIAALACAAC+AgAAGgIAABwCAABQAgAAVgIAABwCAAA0AgAAFgIAALYCAADoAgAAzgIAABYCAADIAgAA3AIAACACAAEeAgAA2AIAAJgCAACiAgAAkAIAAJY",
    "CAACuAgAAqgIAAP4CAAAoAgAAKAIAACgCAAAqAgAAsgIAACoCAAAoAgAAMAIAABoCAADSAgAAIAIAABoCAABCAgAAyAIAABICAADaAgAAFgIAABQCAACqAgAAvgIAANYCAAAYAgAAogIAAK4CAACEAgAAKgIAALw",
    "CAACUAgAAwAIAAIICAADWAgAAuAIAALoCAACyAgAArAIAANQCAADOAgAAugIAAL4CAAAaAgAA5AIAAKoCAACwAgAAwAIAAMICAACmAgAAvAIAALICAAEAAgAAqAIAACACAAAaAgAAJAIAAB4CAADoAgAAJAIAABI",
    "CAADCAgAAGAIAAIoCAACEAgAASgIAAOoCAACOAgAAkAIAAJgCAAC4AgAAGgIAAIICAAFaAgAACgIAAB4CAACoAgAAkgIAALQCAACEAgAAEgIAAKQCAACeAgAAsgIAAIACAAC8AgAAjAIAAOQCAAAuAgAA1gIAAKY",
    "CAACUAgAAqAIAAB4CAAAqAgAAqAIAAJQCAAC+AgAAxgIAAKQCAADAAgAAHAIAAK4CAADYAgAAbgIAAKoCAAEMAgAA0gIAALQCAAAYAgAAuAIAAJQCAAASAgAAqgIAAIICAAAaAgAAkgIAALYCAACMAgAA4gIAAMQ",
    "CAAC0AgAAjgIAAB4CAAAOAgAAGgIAABgCAAAoAgAAngIAANoCAADAAgAA6gIAAHICAACMAgAAngIAAJwCAAEEAgAAEgIAAJwCAAAeAgAArgIAALACAACsAgAAJAIAAHoCAACQAgAAtAIAAKICAAASAgAA5AIAACA",
    "CAAAmAgAA6gIAAKwCAAD8AgAA9AIAABoCAAEGAgAAIAIAACACAADkAgAA0AIAAJoCAACaAgAA4gIAALgCAAAuAgAAmgIAABoCAADcAgAAHAIAAL4CAAAQAgAAvgIAAM4CAADgAgAA7AIAAEICAAAsAgAAHAIAAI4",
    "CAAAcAgAANAIAANICAAC8AgAAGgIAAMgCAAASAgAA/gIAACQCAADIAgAAUAIAAHoCAACWAgAAJAIAACACAAE0AgAAFAIAALgCAAASAgAAGgIAAB4CAAAYAgAAxAIAAMACAADmAgAAFgIAALgCAADCAgABJgIAALQ",
    "CAAAYAgAAggIAABICAADkAgAAGAIAABgCAAAWAgAAKAIAALYCAADKAgAAqAIAAM4CAACEAgAAZAIAABoCAADWAgAAXAIAANICAAAYAgAAqAIAAMICAAAaAgAAEgIAABoCAAAeAgAAFgIAAL4CAACuAgAAsAIAANI",
    "CAAEwAgAAuAIAAEYCAAAUAgAAfgIAABoCAAAaAgAAzAIAABYCAAAWAgAA6gIAACgCAAAcAgAAugIAAKQCAADoAgAAhAIAAK4CAAAoAgAAHgIAABICAAAcAgAAVAIAAPgCAAAUAgAAHAIAAIoCAAAeAgABQgIAACA",
    "CAAAYAgAAtAIAARoCAACIAgAA2gIAAM4CAAC4AgAAhgIAANgCAACsAgAA7AIAAGACAAAUAgAAWgIAABYCAAB2AgAAGAIAAMACAAAoAgAAMAIAAMYCAAAaAgAA+gIAAO4CAAD0AgAAFgIAALgCAAAWAgAAKgIAABo",
    "CAAAcAgAAGAIAAPQCAAEIAgAAGgIAALYCAADcAgAAygIAAKICAADCAgAAxAIAABQCAAAUAgAA5AIAABICAADUAgAAEgIAAKwCAAA8AgAAnAIAAKoCAADEAgAAKgIAAMwCAACuAgAAJgIAACACAAAgAgAAugIAAJg",
    "CAAAaAgAAdAIAAHACAADGAgAAugIAAOwCAAAWAgAAuAIAABoCAAAgAgAAHAIAAFYCAAAqAgAA8AIAACACAAAgAgAAGgIAANoCAACoAgAA5AIAACYCAADEAgAAuAIAANoCAAEMAgAAIAIAABgCAAAYAgAAygIAAKI",
    "CAADCAgAAnAIAAHACAACOAgAAtgIAAPwCAADeAgAA4AIAAGoCAAAiAgAA6AIAABoCAAAeAgAAIAIAALgCAACUAgAAFgIAAOoCAAAgAgAAqAIAAOQCAAEAAgAAHAIAACICAAAcAgAAxgIAAKwCAAAWAgAAJgIAAFI",
    "CAAAaAgAAQAIAABwCAABkAgAAbAIAAHYCAAAUAgAAsAIAACICAAAaAgAAGgIAALoCAAAsAgAAygIAABoCAAA0AgAAqgIAACYCAAB6AgAAFgIAAMgCAADMAgAANgIAACwCAAAWAgABMgIAALQCAAASAgAAEgIAAJQ",
    "CAADGAgAAGgIAAKoCAACsAgABQAIAABYCAADYAgAAGgIAABICAACoAgAAegIAABoCAAAaAgAAtgIAALYCAAAaAgAAyAIAABgCAAAWAgAAHAIAAMwCAAAaAgAAFAIAAB4CAADiAgAAFAIAALQCAACYAgAAFAIAABY",
    "CAAAgAgAAmgIAABACAAAQAgAAFAIAABoCAABkAgABJAIAARoCAAAaAgAAHAIAAKoCAAB+AgAAigIAAJgCAAC8AgAAPAIAAJICAAEKAgAA7AIAAO4CAAAUAgAA3AIAADwCAAAUAgAAFAIAABQCAAAUAgAAFgIAABw",
    "CAADyAgAAGgIAABoCAAAaAgAAGgIAAG4CAABEAgAAkAIAABoCAADGAgAAqAIAAB4CAAAiAgAAVgIAALACAACQAgAAHAIAACoCAAAqAgAAwAIAANoCAADSAgAAFAIAAMACAADIAgAAHAIAAIYCAAASAgAAMAIAACI",
    "CAAEqAgAAIAIAABwCAACeAgAAEgIAALgCAAAUAgAAmAIAAK4CAAAaAgAAGgIAAPQCAAAkAgAAGAIAAKgCAAC2AgAAKgIAABICAAAUAgAAEgIAABICAAEOAgAAEgIAABYCAAAWAgAAGgIAABICAAAmAgAAFgIAABY",
    "CAAAUAgAA9gIAASgCAADyAgAA3AIAABQCAADOAgAArAIAAMQCAACqAgAAkAIAAMACAACgAgABiAIAACICAACaAgAAngIAABwCAACAAgAAzAIAAKICAADkAgABNgIAACYCAAAaAgAAJgIAAI4CAAAUAgAApAIAAJ4",
    "CAAAcAgAAHAIAABQCAADgAgAAFAIAABoCAADmAgAAFAIAAIwCAADqAgAAGgIAANoCAAEMAgABXAIAANYCAADMAgAAuAIAAOYCAACaAgAAogIAAQACAAAUAgAAFgIAAPgCAAEwAgAAFAIAARACAADIAgAAFgIAAMo",
    "CAAC6AgAAGgIAABoCAAAaAgAAGAIAABYCAACgAgAA0AIAASACAAEgAgAAPAIAACICAABkAgAAKgIAABwCAAAUAgAAGgIAAOwCAADAAgAAGAIAABwCAAAaAgAAFAIAABQCAACKAgAAwgIAALACAAC8AgAAFgIAABY",
    "CAACcAgAALgIAACACAACQAgAAFAIAALYCAAC4AgAAFAIAABoCAADmAgABVgIAABgCAAAqAgAAnAIAACYCAAAYAgAALgIAABoCAACiAgAAGgIAABgCAAAeAgAA8AIAABYCAACmAgAAtgIAAJoCAAAaAgAAGgIAACg",
    "CAADIAgAAzAIAAIICAACkAgAAGgIAACwCAAEGAgAAFgIAABwCAAAmAgAADgIAAHQCAAAUAgAAFAIAAMQCAAEeAgABQgIAAMICAAAUAgAAGgIAAOYCAAAaAgAAfAIAAI4CAAAWAgABAAIAABQCAADkAgAAwgIAABI",
    "CAAAaAgAAGgIAAFYCAAFiAgAArAIAAIACAAFaAgAAFAIAABYCAAASAgAAsgIAABgCAAESAgAAbAIAAIwCAAFsAgAAFgIAAEYCAAAYAgAAGgIAAB4CAAEAAgAAiAIAABACAADYAgAAEgIAAKACAAAMAgABOAIAABo",
    "CAAAUAgAAsgIAAB4CAAB0AgAAFgIAALoCAACqAgAAtgIAABICAADaAgAAGgIAACACAAAgAgAAGgIAARYCAAAgAgAAJgIAAMICAAAiAgAAJAIAAFYCAACYAgAAFAIAABYCAAAUAgAAGgIAANwCAAAaAgAA0gIAAUQ",
    "CAAAkAgAA2gIAAOwCAAAYAgAAFgIAABYCAAAeAgAAMAIAACICAAAaAgAAGgIAABoCAAAaAgAAFAIAABQCAAAUAgAAFAIAABoCAAAaAgAAIAIAACQCAAAoAgAAtgIAAMYCAACMAgAAGAIAAJYCAAAiAgAAIgIAALo",
    "CAACmAgAAEgIAAMQCAAAWAgAAjAIAAA4BM0AAAHnAR0ALQAAAScBKQCFAJgBuAEdAc8A0wCTAOEAngCDAD0ArACaAI8AnACaAecBmgCYAJgAmACoAB8AIQCHAIEAhwDZAPQAdQCHAOEAiQDTAOkAcQCHAFQAsABU",
    "ALoAjQBmAH0AIQACADUAIQBmAZwA0wEh//ABogCHAJ4ArACJAIUAnABmAKAAxQCHANcAvABcAKAAcwCeAIkBCADLAIsAoABS//wAYABSALYA4QIbAOMAmAFcAecAvv/6AE4ARgAAAAIAAAADAAAAFAADAAEAAAAU",
    "AAQcYAAABxQEAAAJAxQAIwAlAF0AfgCyALcA1yAUICYhkyIeJGYlsiW2JbwlwCXGJc8mBicTMAIwDTARTgBOB04LTg5OFE4iTiVOKk4tTjROO05FTklOS05OTllOXU5gTmZOcU6GTolOjE6OTpJOlE6bTqROp06u",
    "TrpOwE7GTs5O007WTuVO7E73TvtO/U8RTxhPGk8gTyRPOE88T0ZPT09TT1VPWU9cT2BPf0+LT5tPnU+nT79P3U/hT+5QDVASUBlQPFA+UEdQT1BaUFxQf1CoUKxQu1DPUPVRQVFDUUlRTVFcUWVRaFFtUXFRc1F4",
    "UXxRhVGNUZlRs1G1UbdRu1HAUcZRz1HRUeBR9lH7Uf1SAFIDUgdSElIXUhlSG1IdUiBSJFIrUjBSN1I7Uk1SVFJqUohSm1KhUqlSv1MFUxZTOlNBU0NTR1NKU1VTV1NhU3BTdFN3U4tTmlOfU7tTwlPIU8pTzVPR",
    "U9hT4FPkU+xT8FPzU/dUBFQIVA5UEVQmVCxUL1Q4VEhUWFRoVH1UjFTBVMhUzVTlVOpVJFUvVUZVilXcVjRWaFbKVttW3lbgVuJW9Fb6Vv5XBlcIVyNXKFcwVzpXQFdHV1BXV1eCV4tX31f6WINYnlkEWQdZDVkW",
    "WRpZHFknWSpZLlkxWTRZUVlXWWVZc1l2WX1Zy1nQWf9aGFrMW1BbWFtmW4NbiVuMW5hbmlueW6JbpFuqW7Nbtlu5W71b+Vv8XARcD1wRXBZcGFwdXDFcOlw+XEBcQlxFXE9cXl0pXUxd5l3oXe5d8l4DXideOF5F",
    "XlVec152Xo9elV6XXqZerV72XvpfAF8CXw9fFV8gXydfOl9TX1VfYl9xX3tfgF+FX4tfl1+hX6pfrl+9X8NfxV/XX+tgAWAOYBJgHWAnYDtgUmBiYG9gxWDvYPNhCGEPYR9hYmISYhZiGGIqYjRiQGJHYktiTWJT",
    "YlhiW2JjYmdiaWJrYnBigGKEYopik2KVYphiomKkYqxisWK1YsZiyWLNYtJi1mLbYt9i6WLxYv9jAmMHYwljEWMhYyRjKGMqY19jYmNuY3djiWOSY6VjqGO3Y9Bj0mP0ZBxkHmQtZEdkeGSeZKRkrWTFZM5lL2U2",
    "ZTllO2U+ZUhlTGVPZWNlcGV0ZYdli2WXZZxlp2WpZa1lsGW5Zctl4GXiZedl6WX2Zg5mE2YgZi9mPmZvZoJml2a0ZvRnAGcJZw1nHWcfZyxnL2c1ZzpnQGdDZ0ZnUGdfZ2FnZWd/Z4FnhGecZ7Zn0GfTZ+VoB2gP",
    "aCFoOWg8aEZoSGhMaGNoZWh2aK9owGktacxp/WohaipqWWsha2Vre2u1a81rz2vSa9RsFGw0bDhsQmxHbElsiWyhbL9syWzVbOJs6Gz8bTttPm1BbUttT21ubXdtiG2obeFt8W33bgVuEG4hbjJuOG6QbtFu3m7h",
    "bwJvD28Ub8Bwa3B1cK5wuXDfcO1xNnFncgZyKnIxckhyTHJZcmlyeXK2ctBy7HL4cxxzK3OHc6lzsHQDdAZ093UfdSh1MnU1dTt1THVZdWV1l3WrddV2e3Z9doR2xnbKds920nbWdth27nb0dvl2/ncBdwt3IHc8",
    "d0B3W3dhd6x3s3fld+l37XgBeBR4NHg4eEB4bHhueJd4sHi+eTp5PHk+eV55gXm7ecF5zXnSedh58Hn7egt6M3o/enp6f3qBepd6nXrLetZ62Xrgeu97G3smeyx7SXtUe1Z7fnuAe5d7oXute8d8B3xzfHt8knzK",
    "fPt9IH0ifSd9K30vfqJ+p36vfrl+v37Efsh+z37TftV+2X7dft9+537pfu1/AH8TfxZ/GH8pfzp/UX9pf25/jn/7gAOABYAMgBeAM4BMgFSAWoClgMyA3ID2gP2BEYEagXCBf4HCgeqB9IIMgnKCgoKxgs+C5YMD",
    "gzaDUIO3g9yEJYQ9hLiExITdhc+GWobLh4OH+YhAiEWITIhhiGWIaIhwiI2Iq4jCiMWI2Yj4iYGJhonCicSJxonJidKJ44nmigCLoYuki6mLrouwi7KLuIu/i8GLzYvRi9WL3Yvli+2L74v0i/uMAYwDjGGMao0f",
    "jSONJo0ojS+NNI05jUSNS41UjVaNcI13jYWNio2zjcON0Y3djd+N743zjimOq46yjrqPZo9oj2yPbo97j32PkY+Tj6iPuY/Fj8eP0Y/Uj9mP3I/fj/eP/ZACkAmQEJASkBqQIJA7kFOQbpB/kKOQ6JD9kU2RkpHK",
    "kc2Rz5HRlIiUn5SulMGU9pT6lQGVC5UZlS6VXJV/leiV6pXulfSWAZYyljWWRZZNllCWZJZplpCWlJbGlvaXAJcHlzKXOJdSl1mXXpdgl2KX85h2mHuYf5iEmJiYnZjOmNiY35ltmXCZiJmPmZaZmZpsmnGae5p/",
    "moyaqJrYnHycuJ4hntGe2J8gn1Cfmf9e//8AAAAgACUAKABfALIAtwDXIBQgJiGQIh4kYCWyJbYlvCXAJcYlzyYFJxMwADAKMBBOAE4HTglODU4TTiJOJE4qTi1ONE46TkVOSE5LTk5OWU5dTl9OZk5xToZOiU6L",
    "To5Okk6UTptOpE6nTq5Ouk6/TsVOzU7TTtZO407sTvZO+079TxFPGE8aTyBPJE84TzxPRk9NT1NPVU9ZT1xPYE9/T4tPm0+dT6dPv0/dT+FP7lANUBJQGVA8UD5QR1BPUFpQXFB/UKhQrFC7UM9Q9VFBUUNRSFFN",
    "UVxRZVFoUW1RcVFzUXZRfFGFUYxRmVGyUbVRt1G7UcBRxlHPUdFR4FH2UfpR/VIAUgNSBlISUhdSGVIbUh1SIFIkUitSMFI2UjpSTVJUUmlSiFKbUp5SqFK/UwVTFlM6U0FTQ1NHU0pTVVNXU2BTcFNzU3dTi1Oa",
    "U59Tu1PCU8hTylPMU9FT1lPgU+NT6lPvU/NT91QDVAhUDFQRVCZUK1QvVDhUSFRYVGhUfVSMVMFUyFTNVOVU6lUkVS9VRlWKVdxWNFZoVspW21beVuBW4lb0VvpW/lcGVwhXI1coVzBXOldAV0dXT1dXV4JXi1ff",
    "V/pYg1ieWQRZB1kNWRZZGlkcWSdZKlkuWTFZNFlRWVdZZVlzWXZZfVnLWdBZ/1oYWsxbUFtXW2Zbg1uJW4xbmFuaW55boFukW6pbs1u2W7lbvVv4W/xcBFwPXBFcFlwYXB1cMVw6XD5cQFxCXEVcT1xeXSldTF3l",
    "Xehd7l3xXgNeJl44XkVeVV5yXnZej16TXpdepl6tXvZe+l8AXwJfD18VXyBfJ185X1JfVV9iX3Ffe1+AX4Rfi1+XX6Ffql+uX71fw1/FX9df62ABYA5gEmAdYCdgO2BSYGJgb2DFYO9g82EIYQ9hH2FiYg9iFmIY",
    "YipiNGI/YkdiS2JNYlNiWGJbYmNiZ2JpYmticGJ+YoRiimKTYpVimGKiYqRirGKxYrVixWLJYs1i0mLWYtti32LpYvFi/WMBYwdjCWMRYyFjJGMoYypjX2NiY25jd2OJY5JjpWOnY7djz2PSY/RkHGQeZC1kRmR4",
    "ZJ5kpGStZMVkzWUvZTZlOWU7ZT5lSGVMZU9lY2VwZXRlh2WLZZdlnGWnZallrWWwZblly2XgZeJl52XpZfZmDmYTZh9mL2Y+Zm5mgmaWZrRm9Gb/ZwhnDWcdZx9nKmcvZzVnOmdAZ0NnRmdQZ19nYWdlZ39ngWeE",
    "Z5xntmfQZ9Nn5WgHaA9oIWg3aDxoRmhIaExoY2hlaHZor2jAaS1pzGn9aiFqKmpZayBrYmt7a7VrzWvPa9Jr1GwUbDRsOGxCbEdsSWyJbKFsv2zJbNVs4WzobPxtO20+bUFtS21PbW5td22Ibaht4W3xbfduBW4Q",
    "biFuMm44bpBu0W7ebuFvAm8PbxRvwHBrcHVwrnC5cN9w7XE2cWdyBnIqcjFyR3JMcllyaXJ5crZy0HLscvhzG3Mrc4dzqXOvdAN0BnT3dR91KHUxdTV1O3VMdVl1ZXWXdat11XZ7dn12hHbGdsp2z3bRdtZ22Hbu",
    "dvR2+Hb+dwF3C3cfdzx3QHdbd2F3rHezd+V36XfteAF4FHg0eDh4QHhseG54l3iweL55Onk8eT55XnmBebt5wXnNedJ52Hnweft6C3ozej96enp/eoF6l3qdest61nrZeuB673sbeyZ7LHtJe1R7Vnt+e4B7l3uh",
    "e617x3wHfHN8e3ySfMp8+30gfSJ9J30rfS9+on6mfq9+t36/fsN+yH7PftN+1X7Yft1+337nful+7X8AfxN/Fn8Yfyl/On9Rf2l/bn+Of/uAA4AFgAyAF4AzgEyAVIBagKWAzIDcgPaA/YERgRqBcIF/gcKB6oHz",
    "ggyCcoKCgrGCz4LlgwODNoNQg7eD3IQlhD2EuITEhN2Fz4ZahsuHg4f5iECIRYhMiGGIZYhoiHCIjYiriMGIxYjZiPiJgYmGicGJxInGiciJ0onjieaKAIuhi6SLqYuti7CLsou4i76LwYvNi9GL1Yvdi+WL7Yvv",
    "i/SL+4wBjAOMYYxqjR+NI40ljSiNL400jTmNRI1LjVSNVo1wjXeNhY2KjbONw43Rjd2N343vjfOOKY6rjrKOuo9mj2iPbI9uj3uPfY+Rj5OPqI+5j8WPx4/Qj9SP2I/bj96P94/9kACQCZAPkBKQGpAfkDuQU5Bu",
    "kH+Qo5DokP2RTZGSkcqRzJHPkdGUiJSflK6UwZT2lPqVAJULlRmVLpVclX+V6JXqle2V9JYBljKWNJZElk2WUJZklmmWj5aUlsaW9pcAlweXMpc4l1KXWZdel2CXYpfzmHWYeZh+mISYl5icmM6Y2JjemW2ZcJmI",
    "mY+ZlpmZmmyacZp7mn+ajJqomticfJy4niGe0Z7YnyCfUJ+Z/wH//whmCGUIYwhiCC8IKwgM6NDov95x5sjbpdpa2lfaUtpP2kraQtoN2QHQFdAO0AyyHrIYsheyFrISsgWyBLIAsf6x+LHzseqx6LHnseWx27HY",
    "sdex0rHIsbSxsrGxsbCxrbGssaaxnrGcsZaxi7GHsYOxfbF5sXexa7FlsVyxWbFYsUWxP7E+sTmxNrEjsSCxF7ERsQ6xDbEKsQixBbDnsNywzbDMsMOwrLCPsIywgLBisF6wWLA2sDWwLbAmsBywG6/5r9Gvzq/A",
    "r62viK89rzyvOK81ryevH68drxmvFq8VrxOvEK8IrwKu967frt6u3a7artau0a7Jrsiuuq6lrqKuoa6frp2um66Rro2ujK6LroquiK6Frn+ue652rnSuY65drkmuLK4arhiuEq39rbitqK2FrX+tfq17rXmtb61u",
    "rWatWK1WrVStQq00rTCtFa0PrQqtCa0IrQWtAaz6rPis86zxrO+s7KzhrN6s26zZrMWsway/rLesqKyZrIqsdqxorDSsLqwqrBOsD6vWq8yrtqtzqyKqy6qYqjeqKKomqiWqJKoTqg6qC6oEqgOp6anlqd6p1anQ",
    "qcqpw6m9qZOpi6k4qR6olqh8qBeoFagQqAioBagEp/qn+Kf1p/On8afVp9Cnw6e2p7Snrqdhp12nL6cXpmSl4aXbpc6lsqWtpauloKWfpZylm6WapZWljaWLpYmlhqVMpUqlQ6U5pTilNKUzpS+lHKUUpRGlEKUP",
    "pQ2lBKT2pCykCqNyo3GjbKNqo1qjOKMooxyjDaLxou+i2KLVotSixqLAonmidqJxonCiZKJfolWiT6I+oieiJqIaogyiA6H/ofyh96HsoeOh26HYocqhxaHEobOhoKGLoX+hfKFyoWmhVqFAoTGhJaDQoKegpKCQ",
    "oIqge6A5n42fip+Jn3ifb59ln1+fXJ9bn1afUp9Qn0mfRp9Fn0SfQJ8znzCfK58jnyKfIJ8XnxafD58Lnwie+Z73nvSe8J7tnume5p7dntaey57KnsaexZ6+nq+erZ6qnqmedZ5znmieYJ5PnkeeNZ40niaeD54O",
    "ne2dxp3Fnbedn51vnUqdRZ09nSadH5y/nLmct5y2nLScq5yonKack5yHnISccpxvnGScYJxWnFWcUpxQnEicN5wjnCKcHpwdnBGb+pv2m+ub3ZvPm6Cbjpt7m1+bIJsWmw+bDJr9mvya8prwmuua55rimuCa3prV",
    "mseaxprDmqqaqZqnmpCad5pemlyaS5oqmiOaEpn9mfuZ8pnxme6Z2JnXmceZj5l/mROYdZhFmCKYGpfslyaW5pbRlpiWgZaAln6WfZY+lh+WHJYTlg+WDpXPlbiVm5WSlYeVfJV3lWSVJpUklSKVGZUWlPiU8JTg",
    "lMGUiZR6lHWUaJRelE6UPpQ5k+KTopOWk5STdJNok2SSuZIPkgaRzpHEkZ+RkpFKkRqQfJBZkFOQPpA7kC+QIJARj9WPvI+hj5aPdI9mjwuO6o7ljpOOkY2hjXqNco1qjWiNY41TjUeNPI0MjPmM0IwrjCqMJIvj",
    "i+CL3Ivbi9iL14vCi72Luou2i7SLq4uYi32Leotgi1uLEYsLitqK14rUisGKr4qQio2KhopbilqKMooaig2JkomRiZCJcYlPiRaJEYkGiQKI/YjmiNyIzYimiJuIYYhdiFyIR4hCiBWIC4gJiAOH9YfKh8CHu4ef",
    "h5WHlIdth2yHVodNh0KHKYbqhn+GeIZihiuF+4XXhdaF0oXPhcyEWoRXhFCESYREhEGEPoQ4hDWENIQyhC+ELoQnhCaEI4QRg/+D/YP8g+yD3IPGg6+Dq4OMgyCDGYMYgxKDCILtgtWCzoLJgn+CWYJKgjGCK4IY",
    "ghCBu4GtgWuBRIE8gSWAwICxgIOAZoBRgDSAAn/pf4N/X38XfwB+hn57fmN9cnzofHh7wXtMewZ7Anr8euh65Xrjetx6wHqjeo56jHp5elt503nPeZV5lHmTeZJ5inl6eXh5X3e/d713uXe2d7V3tHevd6p3qXee",
    "d5t3mHeRd4p3g3eCd353eHdzd3J3FXcNdll2VnZVdlR2TnZKdkZ2PHY2di52LXYUdg52AXX9ddV1xnW5da51rXWedZt1ZnTldN902HQtdCx0KXQodBx0G3QIdAdz83Pkc9lz2HPQc85zy3PKc8lzsnOtc6tzpXOg",
    "c59zmHOUc3pzY3NJczlzFnLScr5yb3IrcfRx83HycfFvO28lbxdvBW7Rbs5uyW7AbrNun25yblBt6G3nbeVt4G3UbaRto22VbY5tjG15bXVtUG1NbRxs7WzkbN5stGyvbJZskGyMbItsimv6a3lrd2t1a3FrX2tc",
    "ayxrI2seapFqj2p4anJqbGpqaZhplGmLaYhpfGlhaTJnj2dUZexlPWU3ZPBkwWR5BRIAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
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
    "AAAeCAAAHiQAAB46AAAeUAAAHmwAAB6CAAAemAAAHrQAAB7KAAAe4AAAHvwAAB8SAAAfKAAAHz4AAB9UAAAf8gAAIGkAACEAAAAhkwAAIkoAACMtAAAjhwAAJAsAACRzAAAk+gAAJYIAACYcAAAmpwAAJ2kAAChO",
    "AAAoxAAAKX0AACoXAAAqLQAAKkMAACpZAAAqbwAAKoUAACqbAAAqsQAAKscAACrdAAAq8wAAK1EAACvJAAAsIwAALIQAACyaAAAs+wAALWwAAC37AAAuEQAALicAAC49AAAuUwAALmkAAC5/AAAulQAALqsAAC7B",
    "AAAu1wAALu0AAC8DAAAvGQAALy8AAC/sAAAwAgAAMBgAADAuAAAwRAAAMKYAADE+AAAxVAAAMWoAADGAAAAxlgAAMawAADHIAAAyXwAAMnUAADLhAAAzEQAAM1sAADPHAAA0OAAANNAAADV4AAA1wgAANhQAADYq",
    "AAA2QAAANlYAADZsAAA2mwAANrEAADbHAAA23QAAN1cAADg1AAA4pAAAOSwAADlCAAA52QAAOo8AADqlAAA7bAAAO4IAADuYAAA7ywAAPCAAADx+AAA8lAAAPQcAAD1oAAA93gAAPkkAAD6xAAA+xwAAPt0AAD9U",
    "AAA/uwAAQD0AAECqAABBFQAAQSsAAEFBAABBVwAAQW0AAEGDAABB5gAAQmkAAEL/AABDoAAAQ7YAAEQtAABEQwAARFkAAETpAABFBQAARRsAAEUxAABF9wAARg0AAEYjAABGOQAARygAAEdEAABHdwAAR40AAEfd",
    "AABH8wAASAkAAEgfAABINQAASEsAAEhhAABIdwAASI0AAEkUAABJKgAASUAAAElWAABJbAAASYIAAEoYAABKLgAASuAAAEr8AABLEgAAS9EAAEvnAABL/QAATKEAAEy3AABNcQAATYcAAE44AABOTgAATqEAAE8Q",
    "AABPlQAAUB0AAFCnAABQwwAAUNkAAFDvAABRdgAAUYwAAFGiAABRuAAAUc4AAFHkAABR+gAAUhAAAFJtAABSgwAAUyMAAFM5AABTTwAAU2UAAFP+AABUFAAAVKgAAFS+AABU1AAAVOoAAFUAAABVFgAAVSwAAFVC",
    "AABVWAAAVW4AAFWEAABV5gAAVfwAAFYSAABWKAAAVosAAFb0AABXCgAAVyAAAFfNAABX4wAAWEIAAFhYAABYbgAAWIQAAFiaAABYsAAAWMYAAFjcAABY+AAAWSgAAFmOAABZzwAAWnoAAFrdAABbQQAAW8cAAFx0",
    "AABcigAAXTgAAF1OAABdagAAXaYAAF4PAABelwAAXtoAAF7wAABfBgAAXxwAAF8yAABfSAAAX14AAF90AABf5AAAX/oAAGAQAABgfAAAYJIAAGEzAABhSQAAYV8AAGF1AABhiwAAYaEAAGG3AABiIwAAYjkAAGJP",
    "AABiZQAAYoEAAGKXAABirQAAYsMAAGLZAABi7wAAYwsAAGMhAABjPQAAY1kAAGPlAABkmwAAZLEAAGTHAABk3QAAZPMAAGUJAABlHwAAZTUAAGVLAABlYQAAZXcAAGWNAABlowAAZbkAAGXPAABl5QAAZfsAAGYR",
    "AABmJwAAZj0AAGcKAABn/gAAaBQAAGjbAABo8QAAaQcAAGkdAABpMwAAaUkAAGlfAABp2AAAajgAAGpOAABqZAAAanoAAGqQAABqpgAAarwAAGrSAABq6AAAav4AAGvUAABr6gAAbAAAAGwWAABsLAAAbEIAAGxY",
    "AABsbgAAbIQAAGyaAABssAAAbMYAAGzcAABs8gAAbQgAAG0eAABtNAAAbUoAAG1gAABtdgAAbYwAAG2iAABtuAAAbc4AAG3kAABt+gAAbhAAAG4mAABuPAAAblIAAG5oAABufgAAbpQAAG6wAABuxgAAbtwAAG7y",
    "AABvCAAAbx4AAG80AABvSgAAb2AAAG92AABvkgAAb6gAAG++AABv1AAAb+oAAHAAAABwFgAAcCwAAHBCAABwWAAAcG4AAHCEAABwoAAAcLYAAHDMAABw4gAAcPgAAHF/AABxlQAAcasAAHHBAABx1wAAce0AAHID",
    "AAByGQAAci8AAHJFAAByWwAAct0AAHLzAABzWAAAc24AAHOEAAB0RQAAdFsAAHRxAAB05AAAdPoAAHV2AAB1jAAAdaIAAHX4AAB2DgAAdiQAAHbHAAB3TQAAd2MAAHf0AAB4CgAAeMkAAHjfAAB49QAAeQsAAHkh",
    "AAB6LQAAetUAAHrrAAB7AQAAe3AAAHv+AAB8FAAAfCoAAHxAAAB8swAAfSQAAH2ZAAB+DQAAfp4AAH60AAB+ygAAfuAAAH72AAB/DAAAf5gAAH+uAACARwAAgF0AAIBzAACAiQAAgSMAAIE5AACBTwAAgWsAAIGB",
    "AACBlwAAga0AAIHDAACB2QAAge8AAIIFAACCGwAAgjEAAIJHAACCXQAAgnMAAIKJAACCnwAAgrUAAILLAACC5wAAgv0AAIMTAACDKQAAgz8AAINVAACD1AAAg+oAAIQlAACEawAAhPUAAIVyAACGGwAAhjEAAIbt",
    "AACHwAAAh9YAAIhSAACIuQAAiUQAAInmAACKnQAAirMAAIrJAACK3wAAivUAAIsLAACLxQAAi9sAAIvxAACMBwAAjB0AAIwzAACMSQAAjF8AAIx1AACMkQAAjK0AAIzDAACM2QAAjO8AAI0LAACNIQAAjTcAAI1N",
    "AACNYwAAjXkAAI2PAACNpQAAjccAAI3dAACN8wAAjgkAAI4fAACONQAAjksAAI5hAACOgwAAjwMAAI8ZAACPLwAAj0UAAI9bAACPdwAAj40AAI+pAACPvwAAkCQAAJEUAACRYwAAkXkAAJGPAACSBQAAkhsAAJIx",
    "AACSRwAAkl0AAJJzAACSiQAAkp8AAJK1AACSywAAkucAAJL9AACTEwAAkykAAJM/AACTVQAAk2sAAJPUAACUawAAlNgAAJVEAACV2wAAlmEAAJcGAACXHAAAlzIAAJeZAACXrwAAl8UAAJfbAACX8QAAmEUAAJhb",
    "AACYcQAAmIcAAJidAACYswAAmMkAAJjfAACY9QAAmUQAAJnAAACZ1gAAmewAAJqbAACbOAAAm+AAAJyLAACcoQAAnLcAAJ15AACdjwAAnaUAAJ27AACd0QAAnecAAJ39AACeEwAAnikAAJ4/AACeVQAAnmsAAJ6B",
    "AACelwAAnq0AAJ7DAACe2QAAnu8AAJ9sAACfggAAn5gAAJ+uAACfygAAoMEAAKDXAACg7QAAoQMAAKEZAAChLwAAoUUAAKFbAAChcQAAoYcAAKGdAAChswAAockAAKHfAACh9QAAol0AAKJzAACiiQAAoy4AAKNE",
    "AACjWgAAo3AAAKOGAACjnAAAo7IAAKPIAACj3gAAo/QAAKQKAACkIAAApDYAAKRMAACkYgAApOkAAKT/AAClFQAApTEAAKYRAACmJwAApj0AAKZZAACmbwAApoUAAKabAACmsQAApscAAKbdAACm8wAApwkAAKcf",
    "AACnNQAAp0sAAKdhAACndwAAp40AAKejAACnuQAAp88AAKflAACn+wAAqBEAAKgnAACoPQAAqFMAAKhpAACofwAAqJUAAKirAACowQAAqNcAAKmUAACpqgAAqcAAAKnWAACp7AAAqoUAAKsYAACrhgAAq5wAAKwT",
    "AACsKQAArD8AAKxVAACsawAArIEAAKyXAACsrQAArM8AAKzrAACtBwAArR0AAK05AACtTwAArbEAAK4wAACuRgAArrUAAK9UAACvagAAr4AAAK+WAACvrAAAr8gAALCdAACwswAAsM8AALDlAACw+wAAsRcAALEz",
    "AACxSQAAsWUAALF7AACxkQAAsacAALG9AACx0wAAsjkAALJPAACyZQAAsoEAALKXAACzPgAAs1QAALNqAACzgAAAs5YAALOyAACzyAAAs94AALP0AAC0CgAAtCAAALShAAC0twAAtM0AALTjAAC0/wAAtRUAALXX",
    "AAC17QAAtgMAALZuAAC2hAAAtpoAALawAAC2xgAAttwAALbyAAC3CAAAtx4AALc0AAC3SgAAt2AAALd2AAC3jAAAt6IAALe4AAC3zgAAt+QAALf6AAC4EAAAuCYAALg8AAC4UgAAuWIAALl4AAC6EQAAuicAALo9",
    "AAC6UwAAumkAALswAAC7RgAAvEkAALxfAAC8dQAAvIsAALyhAAC9JgAAvTwAAL1SAAC9aAAAveAAAL32AAC+DAAAviIAAL44AAC+TgAAvmQAAL56AAC/GQAAvy8AAL9FAAC/tgAAv8wAAL/iAAC/+AAAwA4AAMAk",
    "AADAOgAAwFAAAMBsAADAxwAAwN0AAMDzAADBCQAAwR8AAME1AADBSwAAwWEAAMF3AADBjQAAwaMAAMG5AADBzwAAweUAAMKKAADCoAAAwrYAAMLMAADC4gAAwvgAAMMOAADDJAAAwzoAAMNQAADDZgAAw3wAAMOS",
    "AADDqAAAw74AAMPUAADD6gAAxAAAAMQWAADELAAAxEIAAMS+AADFawAAxhwAAMa3AADGzQAAxuMAAMb5AADHDwAAxyUAAMc7AADHUQAAx2cAAMd9AADHkwAAx6kAAMe/AADIMAAAyIkAAMifAADItQAAyMsAAMjh",
    "AADI9wAAyQ0AAMkjAADJOQAAyVUAAMlrAADJgQAAyZcAAMmtAADJwwAAyd8AAMn1AADKCwAAyiEAAMo3AADKTQAAymMAAMp5AADKlQAAyyoAAMtAAADLqgAAy8AAAMxCAADM0gAAzU8AAM1lAADNewAAzZEAAM2n",
    "AADNvQAAzdMAAM3pAADN/wAAzhUAAM4rAADOQQAAztwAAM7yAADPUQAA0A8AANAlAADQOwAA0FEAANBnAADQ9wAA0ZQAANH3AADSDQAA0iMAANI5AADSTwAA0u0AANOAAADUFwAA1C0AANRDAADVIgAA1TgAANZF",
    "AADWWwAA1xAAANdLAADXdwAA1+4AANhqAADZCQAA2ZcAANm0AADZ7gAA2igAANpxAADaoQAA2sgAANrmAADbAwAA2yIAANt9AADbpgAA2/cAANxgAADcqAAA3QAAAN1vAADdlAAA3hQAAN6BAADergAA3uQAAN8O",
    "AADfNgAA32AAAN/OAADghgAA4MsAAOE3AADhigAA4dcAAOIHAADiMAAA4pMAAOLBAADi9AAA4ycAAONeAADjfAAA48cAAOQDAADkZwAA5LAAAOUhAADldQAA5eAAAOYDAADmRwAA5nkAAObaAADnFgAA50QAAOdx",
    "AADnmAAA57cAAOfdAADoCAAA6CMAAOhIAADoswAA6RUAAOliAADpwwAA6h8AAOpoAADrHAAA62AAAOuuAADsCAAA7EMAAOxxAADs0wAA7RMAAO1sAADtzwAA7jMAAO5rAADuzgAA7xcAAO9ZAADvjgAA7+kAAPAn",
    "AADweAAA8KUAAPEDAADxHQAA8XwAAPG0AADx6gAA8lAAAPM0AADzxAAA9EQAAPTLAAD1VQAA9Y4AAPW4AAD2fwAA9wUAAPdrAAD4FgAA+MEAAPl2AAD6JgAA+oQAAPrxAAD7aAAA+9kAAPwxAAD8lwAA/PgAAP1a",
    "AAD9yQAA/mgAAP7RAAD/TQABAC0AAQDAAAEBNQABAXcAAQHaAAECYQABAwsAAQPFAAEE7AABBUYAAQZLAAEGqwABB4YAAQgeAAEIhQABCTQAAQmgAAEKOgABCqQAAQsxAAELtgABDCIAAQyaAAENgwABDf4AAQ5S",
    "AAEPDwABD5QAARAVAAEQrwABETYAARG0AAESHQABEo0AARMWAAEThAABE+gAARRZAAEUvQABFXYAARXoAAEWUAABFt0AARdmAAEYKAABGO8AARlWAAEZlwABGccAARqtAAEa+QABG1cAARurAAEcZQABHPkAAR1S",
    "AAEdbAABHfsAAR5HAAEfHQABH/sAASCgAAEhRgABIfgAASJPAAEjAwABI8kAASRRAAEkpAABJRAAASXxAAEmXgABJpoAAScnAAEneQABJ8UAASh5AAEpDwABKVgAASm8AAEqKwABKqUAASsdAAErdwABLDIAASzv",
    "AAEtQgABLaYAAS36AAEugQABLtYAAS+AAAEwNwABMK8AATEQAAExuQABMkMAATKOAAEy6AABM0IAATPvAAE0ZAABNRYAATV3AAE2WwABNq0AATfbAAE4DgABOKAAATkiAAE5cwABOdUAATodAAE6fAABOw8AATtp",
    "AAE8GQABPKYAATzlAAE9cgABPewAAT5sAAE+/AABP1IAAT/GAAFAMQABQOEAAUFEAAFBggABQgwAAUKqAAFDXgABRA4AAURdAAFE3AABRS0AAUWhAAFGEQABRoIAAUcaAAFHigABR/cAAUhLAAFIpAABSR4AAUnd",
    "AAFKwwABS2gAAUv8AAFM5QABTUcAAU2nAAFOFwABTuIAAU+SAAFQTQABUPkAAVGrAAFR8wABUkMAAVK9AAFTOAABU5gAAVQdAAFUyQABVREAAVV8AAFWdQABVw8AAVeeAAFYAQABWHIAAVkuAAFZ7QABWpkAAVsM",
    "AAFbtgABXAwAAVy0AAFdUAABXdgAAV49AAFelgABXucAAV86AAFffQABYAAAAWBdAAFhRgABYdwAAWKVAAFiywABY1wAAWQgAAFk6AABZUsAAWYvAAFm9QABZ08AAWekAAFn0QABaD0AAWh4AAFozAABaQEAAWlR",
    "AAFp+gABamMAAWr0AAFrhAABbAkAAWwxAAFsvQABbPAAAW0jAAFtmAABbfoAAW5wAAFu7wABb30AAXAMAAFw0QABcWwAAXH3AAFybgABcqEAAXMhAAFzqQABdCAAAXSkAAF1UQABdeIAAXZHAAF2egABdqoAAXbX",
    "AAF3BwABdzcAAXfUAAF4BAABeDcAAXhqAAF4rgABeUgAAXm+AAF6IgABen0AAXsiAAF7gQABfCIAAXzhAAF9OwABfbgAAX5XAAF+vwABfzMAAX+sAAF/8gABgK8AAYE8AAGBigABghoAAYJbAAGDHgABg4QAAYP8",
    "AAGEkgABhT0AAYWsAAGGLQABhq8AAYdCAAGHwgABiHUAAYj5AAGJzAABipQAAYsqAAGL1AABjEcAAYz/AAGNvAABjhgAAY6pAAGPCgABj24AAY+4AAGQcAABkPsAAZF3AAGSBgABkrAAAZMUAAGTtAABlC8AAZSA",
    "AAGU2QABld0AAZaiAAGXpwABmEgAAZiMAAGZDQABmVwAAZnqAAGacQABmt0AAZtMAAGb2AABnDoAAZymAAGdOwABnboAAZ58AAGe2gABn5UAAZ/yAAGgRQABoIIAAaDtAAGhYwABoccAAaIvAAGioQABovIAAaN2",
    "AAGkIAABpIYAAaVbAAGmBQABppsAAadqAAGoLAABqO0AAamvAAGqfAABqu0AAauPAAGr2AABrKoAAa1LAAGt4wABrkMAAa8mAAGv0wABsIgAAbEHAAGxzwABslsAAbLgAAGzgAABtAYAAbSVAAG1KwABtakAAbY6",
    "AAG2xgABtxUAAbeTAAG4AwABuHkAAbjIAAG5mAABuj8AAbquAAG7NAABu6IAAbwiAAG8VwABvL8AAb0pAAG9kgABvioAAb7XAAG/lAABwF4AAcD2AAHBeAABwf4AAcKLAAHCugABwy4AAcPHAAHEjAABxTcAAcXD",
    "AAHGSgABxrEAAccqAAHHpQAByB4AAciPAAHJEAAByewAAcp8AAHLJwABy54AAcwwAAHMxgABzSoAAc2MAAHOTAABzt0AAc+uAAHQGgAB0LYAAdEMAAHRNAAB0XUAAdJAAAHSsQAB03wAAdO1AAHUHAAB1I0AAdTg",
    "AAHVggAB1dMAAdYlAAHWeQAB1toAAdcvAAHXxAAB2FIAAdjdAAHZXAAB2ZoAAdobAAHasgAB20UAAduCAAHcGQAB3K4AAd1FAAHd9AAB3mcAAd7SAAHfaQAB3+AAAeBTAAHgyAAB4VUAAeHcAAHiYgAB4uoAAeOD",
    "AAHkIAAB5JQAAeUBAAHlmAAB5gQAAeaKAAHnDgAB544AAehBAAHokwAB6QsAAelCAAHp1gAB6nIAAerTAAHrPwAB648AAewnAAHskAAB7PoAAe1nAAHuDQAB7rMAAe80AAHv+gAB8EcAAfDbAAHxRAAB8bgAAfJK",
    "AAHzNgAB85gAAfQNAAH0UQAB9MkAAfUyAAH1tgAB9hYAAfZIAAH2mgAB9zoAAfffAAH4fgAB+OsAAflaAAH50gAB+kIAAfqTAAH7BAAB+3EAAfvQAAH8MwAB/JgAAfzZAAH9NAAB/cUAAf4RAAH+mwAB/zkAAf+7",
    "AAIAPgACAMEAAgFjAAIB6wACApkAAgLiAAIDFQACA4kAAgP4AAIESAACBLAAAgViAAIFqgACBg4AAgbnAAIHcwACCAEAAghnAAII8QACCU4AAgnKAAIKSgACCtMAAgszAAILfwACC98AAgw/AAIMxgACDQ8AAg1K",
    "AAINvAACDiQAAg5RAAIPLQACD6sAAhAaAAIQcgACELUAAhEhAAIRiAACEeUAAhJEAAISoQACEucAAhNQAAITrAACFAUAAhRkAAIUlQACFNoAAhVCAAIV8QACFlgAAhbQAAIXWQACF5EAAhfvAAIYTgACGKgAAhkm",
    "AAIZcgACGcAAAhnwAAIabQACGuUAAhtcAAIbtwACHBMAAhx7AAIc5AACHU0AAh21AAIeGgACHrUAAh8gAAIfSgACH3AAAh/hAAIgRAACIJwAAiEIAAIhaAACIcgAAiJJAAIiywACI1IAAiOfAAIkEwACJFUAAiSn",
    "AAIk6QACJV4AAiW2AAImLgACJncAAicNAAInWAACJ+oAAih+AAIpAwACKYsAAiofAAIqogACKxkAAiulAAIr/QACLFQAAiyLAAItBwACLbAAAi5qAAIvCQACL6MAAi/kAAIwIwACMIkAAjErAAIxpQACMj0AAjKH",
    "AAIy+gACM4gAAjQBAAI0TQACNJoAAjTYAAI1agACNcsAAjZiAAI2pwACNtoAAjdZAAI3jwACN+cAAjhBAAI41QACOToAAjlzAAI5mwACOgEAAjowAAI6wwACOzQAAjuhAAI8JwACPKoAAj0oAAI9iwACPc4AAj5H",
    "AAI+zAACPyMAAj9gAAI/rwACP/gAAkA0AAJAqAACQOAAAkElAAJBogACQhYAAkKiAAJDVgACRAsAAkR/AAJE/AACRTcAAkWjAAJF4QACRkUAAkatAAJHJgACR88AAkg3AAJIkAACSN8AAklbAAJJrQACSg4AAkpj",
    "AAJKrQACSxcAAktwAAJLnQACTDkAAk0AAAJNmwACTjcAAk6oAAJPQgACT+MAAlASAAJQ8AACUWcAAlHUAAJSSwACUtgAAlNLAAJTegACU+cAAlRMAAJUuAACVPkAAlWHAAJWLQACVrcAAlcpAAJXbAACV68AAlgC",
    "AAJYVwACWJcAAljpAAJZYQACWe4AAlpGAAJahAACWvgAAls3AAJbogACXAYAAlx2AAJdHwACXYUAAl4YAAJeiAACXvEAAl9QAAJgGAACYMYAAmECAAJhfgACYd0AAmIQAAJiWAACYrMAAmLxAAJjYwACY8wAAmRT",
    "AAJk7wACZYIAAmYHAAJmzgACZ0YAAmenAAJoCAACaHwAAmleAAJpmAACagcAAmpUAAJq2wACazYAAmu8AAJsQAACbJUAAm0FAAJtdwACbegAAm5qAAJu0QACbykAAm+nAAJwJwACcFUAAnDhAAJxSQACcbIAAnIQ",
    "AAJyWwACctUAAnNiAAJzxAACdHUAAnUYAAJ1bgACdf0AAnYXAAJ2ZwACdwsAAndcAAJ3pAACeHAAAni6AAJ5EwACeU8AAnmJAAJ51AACeg8AAno1AAJ69AACeyUAAnvJAAJ8XwACfIsAAny3AAJ9DgACfaIAAn37",
    "AAJ+UwACfswAAn86AAJ/+wACgCwAAoChAAKBCgACgXAAAoGrAAKCEgACgosAAoM4AAKDvwAChHIAAoUIAAKFiwAChfEAAoZdAAKG1gACh0oAAogRAAKIaQACiQoAAolzAAKJwgACim8AAoq8AAKLBwACi1cAAou3",
    "AAKMGwACjSAAAo2GAAKN1AACjiIAAo54AAKOwgACjwcAAo94AAKQOgACkJ8AApEsAAKRegACkdIAApIiAAKStgACkwEAApNCAAKThgAClBUAApSfAAKU9wAClYkAApXMAAKWDQAClqgAApcUAAKXhgACl84AAphU",
    "AAKY+wACmb8AApoNAAKaZwACmsgAApsGAAKbegACm9wAApw3AAKcggACnNoAAp0lAAKdegACncAAAp4xAAKelAACnusAAp89AAKf9gACoGYAAqEGAAKhfgACohgAAqJ4AAKixQACozkAAqPGAAKkbAACpJ0AAqUp",
    "AAKllAACpfMAAqaXAAKnFQACp0sAAqegAAKoKQACqGoAAqirAAKpQAACqXsAAqm0AAKqSgACqqsAAqsfAAKrWwACq8oAAqwrAAKsvwACrQEAAq1aAAKtqQACrikAAq6FAAKu2AACr0kAAq/3AAKwLgACsGwAArDB",
    "AAKxNwACsXIAArG5AAKyAAACsm8AArL1AAKzSwACs78AArQlAAK0bQACtKsAArUKAAK1YgACtbgAArYuAAK2bAACtqEAArclAAK3igACt8wAArgcAAK4cQACuMUAArkDAAK5dgACuboAArpPAAK6rwACuzkAAru7",
    "AAK8JgACvIQAAr0EAAK9agACvaYAAr4GAAK+RAACvoIAAr8HAAK/QwACv8sAAsByAALBAwACwUQAAsF/AALBtgACwjEAAsJ1AALCuQACwyQAAsN/AALEFwACxHEAAsUpAALFmQACxdcAAsZNAALGwQACxyIAAseF",
    "AALHvgACx/gAAshIAALImAACyOQAAsk3AALJigACyd0AAsoPAALKPQACym8AAsqhAALLEAACy4EAAsv4AALMQAACzI8AAs2yAALOjAACzt0AAs8mAALPgwACz/wAAtB4AALQ6AAC0VAAAtG2AALSKQAC0nkAAtND",
    "AALTqwAC06sAAtQOAALUaAAC1ZIAAtbnAALXQAAC15kAAtgEAALYUwAC2LgAAtjyAALZMAAC2WsAAtn2AALaTwAC2vQAAtu9AALcXAAC3QEAAt28AALeKAAC3yMAAt/cAALgPgAC4LsAAuFGAALhrQAC4jYAAuLl",
    "AALkIwAC5RAAAuXKAALmTAAC5rsAAucrAALnqwAC6EQAAuixAALpJwAC6YMAAuqDAALqzgAC680AAux8AALs8QAC7WwAAu4iAALu4wAC730AAu/cAALwQAAC8Q0AAvLRAALzywAC9K4AAvUfAAL1eQAC9bQAAvYO",
    "AAL2OwAC9n8AAvcpAAL3wgAC+DgAAvjTAAL5cQAC+gAAAvsbAAL7lgAC/A4AAvyVAAL9TQAC/agAAv5zAAL+5QAC/1kAAv/4AAMAlgADAQIAAwGcAAMCOgADAqcAAwNQAAME2gADBcEAAwaDAAMG9gADB60AAwfc",
    "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",
    "SAeYBoASJghMAAAQBgaHAAD//wBQ/0AHsAZ4EiYGrAAAEAYGqgAA//8AWP9AB7gGgBImCDAAABAGB48AAP//AFj/SAewBoASJgeOAAAQBgacAAD//wBY/0gHmAaAEiYHjgAAEAYHMgAA//8AWP9IB5AGgBImB44A",
    "ABAGBgEAAP//AFj/SAeYBoASJgeOAAAQBgWXAAD//wBY/0gHkAaAEiYHjgAAEAYFGAAA//8AcP9IB5AGgBImB68AABAmBgkAABAGBLkAAP//AGj/SAewBhgSJgc7AAAQBgeBAAD//wBo/0gHmAYYEiYHzQAAEAYH",
    "mwAA//8AaP8wB6gGOBImBY0AABAGBzsAAP//AGj/UAeYBngSJgcDAAAQBgWYAAD//wBo/4gHmAYgEiYHAwAAEAYHMgAA//8AYP9AB6gGeBImBkoAABAGBQYAAAABAID/kAeYBngAHgAAARcGByERMxEhFSERIRUh",
    "ESEVITUhESE1IREhBgcnAAH4mDBIAcigArj9SAJo/ZgDGPj4A1D9mAJo/ehYcIABAAY4MKiYAbD+UJj+SJj+SJiYAbiYAbiwiGgBOAAFAFj/SAcYBhgAGAAcACAAJgAqAAABERQGIyInJxYzMjURIREjESECAyc2",
    "EhEREyERISERIREBIREhFRQlESERBxhgYGCQIJhYQP34oP3oKKCYeGCgAgD+AAKgAgj7UAII/gACoAIIBhj6IHBwEKAQcAFY/egCGP6w/thg8AGIARAC6P4gAUj+uAFI/NgBSKhQ+P64AUgABQEA/0AHAAZ4AAsA",
    "DwATABcAGwAAAREjNSEVIxEhETMRASERISERIREBIREhASERIQcAqPtQqAKosP1QAgD+AAKwAgD7UAIA/gACsAIA/gAFEPowoKAF0AFo/pj9sAG4/kgBuPwAAbj+SAG4AAUBEP84BuAGMAALAA8AEwAXABsAAAER",
    "IzUhESMRIRUjERMhESEhESERASERIQEhESEG4KD+CKD+CKCgAfj+CAKYAfj7cAH4/ggCmAH4/ggGMProgP2gAmCABRj+AAFo/pgBaPyYAWj+mAFoAAUA0P9oB6AGeAAdACEAJQApAC0AAAERIREUFjMyNzI2NxcG",
    "BwYhIyImNREhFSMRIREzEQERIREjESERFREhETMRIREGkP1oUOCIkHAwELAoWGj+cGjgiP4YoAKIoAH4/gig/hgB6KAB+AVw++j/ADAoCFCYSPggKFhgAThoBIABCP74/kABKP7YASj+2Jj+2AEo/tgBKAAHAHj/",
    "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",
    "d5WVd6ZsdKV2kpdxq7VSbUFQUENo5FZrQVBUQGcCbdWujYa129Wsj4O5AUK4a09RZbK5bU5PZwAAAAAPALoAAwABBAkAAAEWAAAAAwABBAkAAQAwARYAAwABBAkAAgAOAUYAAwABBAkAAwAqAVQAAwABBAkABAAw",
    "ARYAAwABBAkABQAkAX4AAwABBAkABgAqAaIAAwABBAkABwCcAcwAAwABBAkACAAoAmgAAwABBAkACgDgApAAAwABBAkACwA4A3AAAwABBAkADABcA6gAAwABBAkADQBcBAQAAwABBAkADgBUBGAAAwABBAkAEgAm",
    "BLQARABpAGcAaQB0AGkAegBlAGQAIABkAGEAdABhACAAYwBvAHAAeQByAGkAZwBoAHQAIACpACAAMgAwADAANwAsACAARwBvAG8AZwBsAGUAIABDAG8AcgBwAG8AcgBhAHQAaQBvAG4ALgAKAEMAbwBwAHkAcgBp",
    "AGcAaAB0ACAAqQAgADIAMAAwADgALQAyADAAMAA5ACAAVwBlAG4AUQB1AGEAbgBZAGkAIABCAG8AYQByAGQAIABvAGYAIABUAHIAdQBzAHQAZQBlAHMAIAAoAGgAdAB0AHAAOgAvAC8AdwBlAG4AcQAuAG8AcgBn",
    "AC8AKQAgAGEAbgBkACAAUQBpAGEAbgBxAGkAYQBuACAARgBhAG4AZwBXAGUAbgBRAHUAYQBuAFkAaQAgAE0AaQBjAHIAbwAgAEgAZQBpACAATQBvAG4AbwBSAGUAZwB1AGwAYQByAFcAZQBuAFEAdQBhAG4AWQBp",
    "ACAALQAgAE0AaQBjAHIAbwAgAEgAZQBpAFYAZQByAHMAaQBvAG4AIAAwAC4AMgAuADAALQBiAGUAdABhAFcAZQBuAFEAdQBhAG4AWQBpAE0AaQBjAHIAbwBIAGUAaQBNAG8AbgBvAEQAcgBvAGkAZAAgAGkAcwAg",
    "AGEAIAB0AHIAYQBkAGUAbQBhAHIAawAgAG8AZgAgAEcAbwBvAGcAbABlACAAYQBuAGQAIABtAGEAeQAgAGIAZQAgAHIAZQBnAGkAcwB0AGUAcgBlAGQAIABpAG4AIABjAGUAcgB0AGEAaQBuACAAagB1AHIAaQBz",
    "AGQAaQBjAHQAaQBvAG4AcwAuAEEAcwBjAGUAbgBkAGUAcgAgAEMAbwByAHAAbwByAGEAdABpAG8AbgBXAGUAbgBRAHUAYQBuAFkAaQAgAE0AaQBjAHIAbwAgAEgAZQBpACAAaQBzACAAYQAgAGgAdQBtAGEAbgBp",
    "AHMAdAAgAHMAYQBuAHMAIABzAGUAcgBpAGYAIAB0AHkAcABlAGYAYQBjAGUAIABkAGUAcwBpAGcAbgBlAGQAIABmAG8AcgAgAHUAcwBlAHIAIABpAG4AdABlAHIAZgBhAGMAZQBzACAAYQBuAGQAIABlAGwAZQBj",
    "AHQAcgBvAG4AaQBjACAAYwBvAG0AbQB1AG4AaQBjAGEAdABpAG8AbgAuAGgAdAB0AHAAOgAvAC8AdwB3AHcALgBhAHMAYwBlAG4AZABlAHIAYwBvAHIAcAAuAGMAbwBtAC8AaAB0AHQAcAA6AC8ALwB3AHcAdwAu",
    "AGEAcwBjAGUAbgBkAGUAcgBjAG8AcgBwAC4AYwBvAG0ALwB0AHkAcABlAGQAZQBzAGkAZwBuAGUAcgBzAC4AaAB0AG0AbABMAGkAYwBlAG4AcwBlAGQAIAB1AG4AZABlAHIAIAB0AGgAZQAgAEEAcABhAGMAaABl",
    "ACAATABpAGMAZQBuAHMAZQAsACAAVgBlAHIAcwBpAG8AbgAgADIALgAwAGgAdAB0AHAAOgAvAC8AdwB3AHcALgBhAHAAYQBjAGgAZQAuAG8AcgBnAC8AbABpAGMAZQBuAHMAZQBzAC8ATABJAEMARQBOAFMARQAt",
    "ADIALgAwAFcAZQBuAFEAdQBhAG4AWQBpACAATQBpAGMAcgBvACAASABlAGkAAwAAAAAAAP8AAGYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIABQAC//8AAwABAAAADAAAAAAAAAACAAgAAADLAAEAzQEBAAEBAwFl",
    "AAEBZwFtAAEBbwKhAAECowObAAEDnQRwAAEIhgjmAAEAAQAAAAoADAAOAAAAAAAAAAEAAAAKABYAGAABbGF0bgAIAAAAAAAAAAAAAAABEAAFWveJAAAIAP9I+egOGAAAAAEAAAAAAAAAAAAAAAAAAQgABbgDwAYY",
    "A8AGGAYIBggGCAYIBggGCAYIBOAEsARQBLAE2AS4BgAGAAZIAAABMAE4BmAGYAZgAuAGYAZgA4AGCAXgBlgGCAYYBngGeAYwBmAGGAY4BngGgAZ4BngGcAaIBmgGUAZ4BmAGEAZ4BngGAAZ4BngGEAaIBngFkAYA",
    "BggGCAZ4BoAGaAaABlAGeAZ4BngGgAZ4BoAGgAZ4BngGgAZ4BoAGeAZ4BngGeAZ4BngGiAaABngGeAZ4BngGgAZ4BngGeAZ4BoAGeAZ4BoAGeAZ4BngGeAZ4BngGeAaIBoAGeAaIBngGeAZ4BoAGeAaIBngGeAZ4",
    "BoAGgAZ4BngF+AZ4BngGgAZ4BngGiAZYBnAGgAZwBkAGiAaIBoAGYAYgBjAGeAZ4BkAGeAZ4BogGgAaABngGEAZABngGeAYoBhgGEAZwBngGcAZ4BngGgAZwBngGeAZwBngGeAZwBngGgAaQBnAGeAaABogGcAZ4",
    "BngGeAaIBngGeAZ4BogGeAY4BngGUAZ4BoAGiAZ4BngGeAaABgAGeAZ4BjgGOAY4BjgGeAaABhAGMAYQBngGcAY4BngGeAZgBeAGeAYIBngGGAYIBoAGeAYwBoAGiAaQBjgGeAZoBoAGOAaABmgGgAYwBkAGSAZA",
    "BpAGgAYoBogGkAZYBigGgAaABoAGgAZ4BngGQAaIBjgGOAYIBjgGOAY4BjgGOAY4BjgGIAaABngGWAZgBoAGWAaABngGYAZYBngGeAaIBogGgAaIBoAGeAaIBoAGcAaABngGeAZ4BngGgAaQBngGeAZ4BoAGeAZ4",
    "BoAGgAYwBogGgAaIBogGiAaQBogGiAaIBogGiAaIBogGiAaIBogGiAaIBngGeAY4BoAGeAZwBmgGaAZ4BngGGAZIBkgGSAZIBkgGSAZ4BngGCAZ4BjAGkAYgBggGiAaABngGeAZ4BngF8AYoBogGgAaABoAGgAaA",
    "BoAGgAaABhAGcAZ4BiAGQAZ4BngGaAZ4BnAGQAZ4BoAGSAZoBmgGgAZ4BngGgAaABngGeAZ4BngGgAZgBmAGeAZ4BngGeAaABiAGeAaABngGeAaQBngGeAZ4BoAGkAaIBngGeAZ4BoAGgAaABngGgAZ4BngGYAZ4",
    "BoAGeAZ4BngGeAZ4BngGgAZ4BngGeAY4BngGeAZ4BngGeAZ4BngGeAaABoAGeAZ4BngGgAaABngGgAZ4BngGeAZ4BoAGiAaIBoAGeAZ4BngGeAZ4BogGeAZ4BngGgAZ4BngGeAaABngGeAaABoAGeAZ4BngGeAZ4",
    "BoAGeAZ4BngGeAaABoAGeAaQBngGgAZ4BngGeAaABngGeAZ4BoAGeAZ4BoAGcAaABngGgAZ4BngGeAaIBoAGeAYYBiAGGAY4BngGSAZQBkgGeAZQBjAGeAZIBoAGYAaIBlAGOAZ4BkAGSAaABkgGeAZ4BngGeAaA",
    "BnAGQAZ4BogGeAZ4BngGeAaIBngGeAZ4BngGMAaABoAGgAaABngGeAZ4BngGgAZ4BoAGeAZ4BngGeAZ4BngGgAZ4BngGgAZ4BngGeAZ4BoAGiAZ4BhAGcAaABfAGeAYwBoAGeAZgBogGeAaIBogGaAZoBmgGcAZw",
    "BoAGeAaABngGeAZ4BngGaAaABngGgAaABoAGgAZoBngGaAZoBngGeAZ4BngGcAZYBmgGgAZ4BmgGWAZ4BngGeAZYBoAGeAZ4BoAGeAYwBngGeAaABmgGeAZ4BjAGeAaABngGgAaABoAGgAaABoAGgAYYBhgGOAZ4",
    "BiAGeAZ4BhgGeAYwBngGMAY4BngGgAaQBogGiAaQBngGgAZ4BngGkAaYBngGeAaABoAGIAZ4BngGeAZwBngGYAZ4BigGSAaIBngGeAZwBoAGeAZ4BngGMAYoBngGOAZ4BjAGeAZ4BngGQAYIBoAGgAaIBngGkAaA",
    "BoAGgAZ4BoAGgAZoBoAGgAaIBogGkAaIBogGgAZ4BngGgAZ4BogGiAaIBogGiAaIBogGiAaIBogGiAaIBogGeAaIBngGeAZoBngGgAZYBngGSAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGeAaIBoAGeAZ4",
    "BngGeAZ4BngGgAZ4BoAGgAYoBlAGUAaABnAGeAaABigGeAYwBjAGcAZIBkgGeAZ4BoAGgAaABngGSAZIBoAGgAYYBngGSAaABoAGeAZ4BoAGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BogGOAaIBoAGeAaABngGeAZ4",
    "BngGgAaABngGeAZ4BngGcAZwBkAGWAYgBjAGeAaIBogGiAagBoAGgAaABngGeAZ4BoAGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BoAGeAZ4BogGeAaABngGoAaABngGiAZ4BmgGaAZABngGeAZ4BoAGgAZ4BngGeAZ4",
    "BoAGMAZYBoAGMAZIBoAGYAZwBogGgAaABoAGeAaABngGeAZ4BngGgAaABkgGeAZIBnAGSAZoBngGSAaABnAGSAaABkgGeAaABkgGiAZgBngGYAZIBoAGSAaABngGSAZ4BoAGeAYYBoAGeAZABkgGcAY4BlgGUAaA",
    "BngGeAZ4BngGeAaQBoAGeAZ4BngGeAaIBnAGkAaQBpAGkAaQBpAGeAZIBngGgAYwBoAGSAaABngGcAZ4BjAGgAZgBlgGYAZwBnAGeAaIBngGgAYoBogGOAY4BjgGeAZIBjgGaAY4BlAGUAZ4BngGMAZIBfgGkAaA",
    "BogGgAaABoAGaAZIBjgGeAY4BmAGUAaIBpAGgAaIBkAGgAaABoAGeAW4BbgFuAYQBcgF0AW4BbgFuAYYBKABMAMoATAFuAXQBbgFyAXIBcAFuAXIBbgF0AXIBCAEIATgA+gE4AXIBbgFwAW4BcgFuAW4BbgFyAW4",
    "BbgFuAW4BbgFuAW4BdAFuAXQBbgFyAW4BbgFuAW4BbgFuAW4BbgFuAW4BcD/SAYgBGAGGARgBhgEYAYgBGAGGAYQBhAGGAYYBGAEYARgBGAEYARgBGAFcARIBEgESARIBEgESAW4BhgFuANYAngGgANoAygDYAZw",
    "BTAEaAQIBoAGSAZ4BkgGgAYwBmAGMAaABnAGgAYgBkAGcAY4A+AGgAYoBXAFGAYgA9AGiAZAA+AE4AZ4BoACKAUgBKgFYATYBMAE2ARIBQAE2ARABIgGeAZ4BkgE6AZIBLgEmARYBIAEeARABGAGeAQIA8AEyAZ4",
    "BngGmAaQBGAEwAZ4BZAGeAaABngGWAYoBngGaAaABngEiAKwBfgGIAOoBoAGcAZwBkADSAZIBEgGiAZ4BoAGeAZ4BnAGeANoBkAGcAT4BRAE8ARIBQgEsAUoBHgEMASABIgDkAOQBAgGOATYBJgFAAT4BQAE0ASQ",
    "A7gEcAaQBJgE4AYgBXgF6AZ4AkgFiAVQBQgCcAaABnAGKAUwBngGeAaABQAGeALwBjgGIAaABmgGkAZ4BngGIAZ4BoAGgAZ4BngGYAZ4BogGiAZ4BjgGMAaABjgGgAaABngGgAZ4BNAC+AY4BjAGeAZ4BkAGeAaA",
    "BggGWAZQBkgGiANABoAF8AZoBnAGIAZ4BngGeAaABogGeAYYBngDSAaABngEmAaABogGSAYoA0AGeAMYBoAGeAZ4BagGQAaIBngCkAZ4BogCeAIIBoAGQAZ4BhgGSAIIBnAGgAY4BjgGeAGoBngCoAIIBoAGAAZ4",
    "BoAGOAY4BnAGGAZQAtgF0AaABoAGeAZ4BoAGOAZ4BdgFyAXIBcAFwAaABcgFyAXIAhgGeANoBngC2AZgBoAGOAZIBkgGEAZ4BjgGeAY4BoAGeAZ4BngGOAYYBngGMAaABngGeAZ4BngGeAZ4BngGSAYoBngGgAZ4",
    "BkAGcAaIBngGGAZ4AlgF6AGABoAGeAZ4BoAGeAYQBngGeAYgBhAGgAZIBoAGMAZ4BigGGAZ4BoAGeAY4BoAGCAZ4BngGgAZ4BngGeAZ4BoAF4AZIBngGAAZwBhAGeAY4BngF6AZ4BngGgAZ4BkAGiAZ4BngGeAYw",
    "BngGgAZ4BjAGeAZ4BjgE6AZ4BngGUAY4BnAGcAaIBngGMAZ4BngGeAZ4BngGeAYYBoAGgAYoBoAEyAZ4BhAE6AZ4BoAGQAaABngGeAZwBigGgAaAAggE8AaABngGMAZ4A3gDWAZwBnAGMAZ4BngGYAZ4BoACaAaI",
    "BOgF6AFIBngGcAaABggGeAZ4BlgGgAQQBngDaAYIBjAGgAKoBjAF+AYoBngGQALYBmAGeATYBNgGeAMABmgGgAZoBogGgAaABoAGeAaABngGKAZABLgGIAYoBoAGeAZ4BngC4AZ4BogGeAaIBnAGcAZQBoAGeAZI",
    "BoAFGAZgBngE+AZoBlgGWAZ4BmAGYAZoBjgGGAZ4AyAGgAZ4BIgGWAZ4BngGeAZwBogBIAaABkAGiAaIBngGeAaIBngEiAaQBngGgAY4BhgGGAZYBjAE6AX4BmgGgAaABoAGgAZ4BkAGgAZ4AlAGgAOoBngGGAaA",
    "BiADAAZgBngGeAY4BmgGeAZ4BngGeALgBogGCAYIBoAGeAMwBngEoAaABlgGeAZ4AqAGcAZgBoAGeAZ4BngDuAZ4BiAGgAKoBggGgAaQBlgGiAYoBjAFyAUwBWgGMAaABngGeAZYArgGiAaIAnACqAYwBjgGOAZA",
    "BjAGeAZoBHgGOAZQBEgGMALQBgAGCAZwBnAGcAZoBoAGUAZwBjAGeAZ4BUgGeAZ4BDAGgAZgBngGeAZ4BngEgAZ4BjAGMAKQBkAGeAaABoAGOAXgAigGiAR4AXgFeAVYBWAGUAZABjAGEAaIBjgGCAZ4BngGeAY4",
    "BogEMAYQBogGeAZ4BlgGeAZ4BoAGcAZwBngGcAZ4BggGeAaABoAGGAXIBfgGeASYBngCGAQwBjgGeAZ4BngGeAYoBjgGIAZ4BoAGeAZIBiAGgAZ4BhAEgAY4BfgGSAX4BhAGcARQBnAGQAOYBoAGgAZ4BPAGeAZ4",
    "BngGOAZQBjgGUAY4BngGeAZ4BngGSAQ4BoAGSAZ4BngGeAJIBUgGUAZoBngGOAYgBngC8AKgBhAGEAaIBoAGgAaABogGkAaABnAGeAYYBogGgAY4BfAGeAZ4BogGgAIgBoAGeAZ4BngGgAZIBjgDgAZABlAGGAY4",
    "BoAGIAZ4BngGAAZwBngGeAZ4BogF4AaABoAGeAY4BlgGWAZ4BoAGSAZ4BigGeAZ4BhgGMAZ4BngGUAZoBmAGgAYIBhgGIAYAAdgGQAYwBkgGeAYgBngGgAaABhgGgAYYBhgGSAZwBoAGeAZ4BlgGgAYABnAGaAZ4",
    "BoAGUAaABkgGSAZIBngGcAaABmgGeAZoBjAGeAYQBngGcAaABngGQAYgArgGSAPQBoADkAaIAsAGeAYYBngGGAZoAygGeAaABoAGgAY4BngGeAZYBlgGkAMQBjgGIAHgBngGeAZ4BhAGEAZwA5AGiAaABoAC4AZo",
    "AyAGEAZ4BngGgAZYBogGeAZ4BnAEyADABjAGIAaABmgGeAaAArAGeAaABHgGiAX4BEgGSAZIBoAGeAZ4BngGeAZ4BiAGeAOgBmgGgAZ4BngGeAZ4BngDMAOABkAGeAYoBnAGAAZ4BngGcAZ4AngGeAMoBngGeAYo",
    "BogCQAaIBngGeAZoBngGMAZ4BhAGeAZ4BngGeAaABnAGMAGwBngGCAZ4BngGeADoBngGeAE4BgAGkAZ4BogF4AXgBjAGeAZ4BngGOAaABnAGaAZ4BoAGCAZ4BngGeAZ4BkAGQAYwBjACaAHIAiACQAZ4BngGeAZ4",
    "BogGiAZ4BfAF8AY4BmAGeAZ4BngGYAZYBogGeAZ4BkgGaAaABoAAAAW2BbYFtgXHBbYFtgYUBKIBBgJ5AS0FtgXNBbYFywXLBb4FtgXLBbYFzQXLBGYEZgTJA+kEyQXLBbYFvAW2BcsFtgW2BbYFywW2BbYFtgW2",
    "BbYFtgW2Bc0FtgXNBbYFywW2BbgFtgW2BbYFtgW2BbYFtgW2/0gGIQReBhQEXgYUBF4GHwReBhQGDgYOBhQGFAReBF4EXgReBF4EXgReBW8ESgRKBEoESgRKBEoFtgYUBbYDWgXFA14EewJ5APoEDg==",
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
