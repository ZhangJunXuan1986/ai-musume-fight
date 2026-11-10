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
VERSION = "v3.1-naruto-ui"

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
    ("dodge",    968, 662, 76, 36),
    ("cleanse", 1048, 662, 76, 36),
    ("scroll",  1128, 662, 76, 36),
]
FUNC_LABEL = {"dodge": "闪避", "cleanse": "净化", "scroll": "秘卷"}
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
    """战斗页中间区：切模式 / 切操作 / 暂停 / 返回。
    这两个切换键就是「手游端游怎么切」的答案，战斗中一点即生效并重开一局。"""
    w, h = 104, 34
    x0, y0 = 512, 548     # 放在地面线上方一点，避开底部 y=662 的功能条
    return [
        _btn(x0,       y0,      w, h, "切模式", (), ()),
        _btn(x0 + 110, y0,      w, h, "切操作", (), ()),
        _btn(x0,       y0 + 40, w, h, "暂停",   (), (GLOBAL_KEYS["pause"],)),
        _btn(x0 + 110, y0 + 40, w, h, "返回",   (), (GLOBAL_KEYS["cancel"],)),
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
        # 主页面「模式 / 操作」切换键 + 结算层两个可点键
        self._refresh_mode_btns()
        self.result_btns = [
            _btn(SCREEN_W // 2 - 220, 500, 200, 52, "再战", (), ()),
            _btn(SCREEN_W // 2 + 20, 500, 200, 52, "回主页面", (), ()),
        ]
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
        """当前页面可点的按钮列表。战斗页左右簇 + 中间；结算层换成两个大按钮。"""
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
                if act == "atk":
                    draw_text(layer, "普攻", rect.centerx, rect.centery - 11,
                              20, COL_TEXT, True, "center", shadow=False)
                    draw_text(layer, "连击", rect.centerx, rect.centery + 12,
                              12, COL_DIM, False, "center", shadow=False)
                else:
                    nm = skill_short_name(f.char["id"], act) if f else act
                    sz = 17 if len(nm) <= 2 else 14
                    draw_text(layer, nm, rect.centerx, rect.centery - 12,
                              sz, col, True, "center", shadow=False)
                    # 编号与 CD 秒数 / 气不足 共用同一行，冷却时让位避免糊成一团
                    if cd == 0 and cost_ok:
                        draw_text(layer, SKILL_INDEX.get(act, ""), rect.centerx,
                                  rect.centery + 10, 13, COL_DIM, False, "center", shadow=False)
            else:
                txt = FUNC_LABEL.get(label, label)
                draw_text(layer, txt, rect.centerx, rect.centery - 9,
                          16, COL_TEXT, True, "center", shadow=False)

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

        # 战斗页底部提示：当前模式 / 操作方案，常驻可见
        if naruto and not self.over:
            tip = "%s  ·  %s  ·  摇杆移动 / 上挑 / 下防  ·  中间可切模式" % (
                self.mode_label(), self.input_label())
            draw_text(layer, tip, SCREEN_W // 2, SCREEN_H - 26, 14,
                      COL_GOLD, align="center", shadow=False)
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
        # v3.1：右侧两块「模式 / 操作」卡片，点一下就切，不用翻设置页
        draw_text(s, "开局前先选", 995, 268, 20, COL_GOLD, True, "center")
        draw_text(s, "PVE = 只你一套键 / PVP = 两人各一套", 995, 496, 14,
                  COL_DIM, align="center")
        draw_text(s, "手机摇杆 / 电脑键盘 / 滑动手势", 995, 518, 14,
                  COL_DIM, align="center")
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
        arena = ARENAS[self.arena_idx % len(ARENAS)]
        eff = ARENA_EFFECTS[self.arena_effect]
        # ---- v3.1 顶部技能说明条：每个键是什么、怎么联动，点之前就看得见 ----
        bar = pygame.Rect(316, 96, 648, 52)
        draw_panel(s, bar, (12, 16, 38), COL_PANEL_LIGHT, 10, 1)
        l1, l2 = skill_help_lines(self.p1.char["id"])
        draw_text(s, l1, bar.centerx, 102, 15, COL_TEXT, True, "center")
        draw_text(s, l2, bar.centerx, 124, 13, COL_GOLD, False, "center")
        line = "%s  ·  %s  ·  %s  ·  秘卷 %s" % (
            self.mode_label(), self.input_label(), arena["name"], self.scroll_id)
        draw_text(s, line, SCREEN_W // 2, 156, 15, eff["color"], align="center")
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
    assert len(SKILL_ROUND) + len(FUNC_BAR) == expect_side
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
    assert gb[0][0].x == TOUCH_GLOBAL_X and gb[0][0].y == TOUCH_GLOBAL_Y
    # v3.1 中间区改成 2×2 四个切换键（切模式 / 切操作 / 暂停 / 返回）
    assert len(mb) == 4 and all(b[0].right <= SCREEN_W and b[0].bottom <= SCREEN_H for b in mb)
    assert {b[1] for b in mb} == {"切模式", "切操作", "暂停", "返回"}
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
    "AAEAAAATAQAABAAwR0RFRhTgFnQAA3zIAAAAQEdQT1MAGQAMAAN9CAAAABBHU1VCbIx0hQADfRgAAAAaT1MvMmYwBBgAAAG4AAAAYGNtYXB56BN3AAAkuAAAHDRjdnQgRJ1NcgAASnQAAAIQZnBnbXPTI7AAAEDs",
    "AAAHBWdhc3AABAAHAAN8vAAAAAxnbHlml5ZrlQAAb+gAAwceaGVhZBagYuoAAAE8AAAANmhoZWEPeQ6IAAABdAAAACRobXR4waDUMwAAAhgAACKgbG9jYQsUU2AAAEyEAAAjZG1heHALgQKDAAABmAAAACBuYW1l",
    "lU2vyQADdwgAAAWUcG9zdP8DAGYAA3ycAAAAIHByZXBBvdqCAABH9AAAAn52aGVhEr4JcgADfTQAAAAkdm10eNXBpN8AA31YAAARsgABAAAAADMzY+hgm18PPPUCPwgAAAAAAMY/xrAAAAAA5xgfVf/w/hQICAag",
    "AAAACAAAAAEAAAAAAAEAAAd+/h0AAAgA//D/8ggIAAEAAAAAAAAAAAAAAAAAAAh4AAEAAAjYAGYADQCIAA4AAgAQAC8AWgAAAh8BYwAEAAEAAwWTAZAABQAIBZoFMwAAAR4FmgUzAAAD0ABmAfIAAAILBgYDCAQC",
    "AgSAAAADCAHkYAAAABAAAAAAV1FZRgBAACD/XgYf/hQAhAd+AeMAEAAAAAAAAARKBbYAAAAgAAIIAAJYCAABUAQAAEgIAAFQBAAASAgAANgIAADYCAAA2AgAANgIAADYCAAA2AgAANgE0AC4BNABGATQALgE0ACA",
    "BNAAkATQALAIAACwCAAAsAgAAfAIAAAACAAAMAgAADAIAAQACAAA2AgABAAIAAHgCAAEAAgAAYAIAACoCAAAeAgAAKAIAACgCAAAkAgAAFgIAACgCAAAkAgAAHAIAAB4CAAAeAgAAFAIAABgCAAA4AgAALAIAACw",
    "CAAAeAgAAHgIAACICAAAoAgAAHAIAABYCAAAyAgAAGgIAAB4CAABAAgAAJAIAAB4CAAA2AgAAGgIAABoCAAAcAgAAIAIAABgCAAAgAgAAGgIAABgCAAAWAgAAHAIAABYCAAAUAgAAFAIAABQCAAAUAgAAFAIAABY",
    "CAAAWAgAAFAIAABQCAAASAgAAQgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABoCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQ",
    "CAAAUAgAAFAIAABoCAAAUAgAAFAIAABoCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAYAgAAJAIAABoCAAAcAgAAIAIAABoCAAAWAgAAGgIAACICAAAeAgAAGgIAABg",
    "CAAASAgAAGgIAADwCAAAcAgAAGAIAACICAAAaAgAAGgIAABoCAAAaAgAAGgIAAB4CAAAaAgAAHgIAABYCAAAaAgAANAIAADYCAAAgAgAAJgIAACwCAAAyAgAAHAIAABoCAAAgAgAAHgIAABgCAAASAgAAEgIAACQ",
    "CAAAiAgAAGAIAABoCAAAOAgAAGAIAABICAAAiAgAAFgIAABwCAAAeAgAAFgIAACACAAAaAgAAGgIAABICAAAcAgAAGgIAABYCAAAgAgAAGgIAABQCAAA0AgAAHgIAACICAAAgAgAAHgIAACICAAAaAgAATAIAACY",
    "CAAAyAgAANAIAABYCAAAeAgAAFAIAABQCAAAUAgAAFAIAABoCAAAYAgAAIgIAABoCAAAaAgAAGgIAABQCAAAaAgAAJgIAACgCAAAoAgAAUgIAACICAAAeAgAAMAIAABoCAAAaAgAAKgIAABYCAAAaAgAAKAIAABw",
    "CAAAUAgAAMgIAABgCAAAUAgAAOAIAABgCAAAcAgAAKAIAABYCAAAoAgAAJAIAACACAAAWAgAAGAIAABICAAAsAgAAKAIAACgCAAAaAgAAKAIAACoCAAAqAgAAJgIAACoCAAAqAgAAKAIAABYCAAAcAgAALgIAAC4",
    "CAAA4AgAALgIAAC4CAAAuAgAALgIAAC4CAAAwAgAAMAIAABwCAAAQAgAAFgIAABYCAAAcAgAAFgIAABYCAAAUAgAAFgIAACACAAAaAgAAFgIAABQCAAAWAgAAFgIAABwCAAAcAgAAKAIAAB4CAAAgAgAAGAIAABY",
    "CAAAWAgAAGAIAABoCAAAcAgAAFAIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAWAgAAGgIAABoCAAAeAgAAIgIAABYCAAAaAgAAJgIAACACAAAeAgAAJgIAABwCAAAiAgAAGgIAACYCAAAYAgAAHAIAACQ",
    "CAAAkAgAAIAIAABoCAAAcAgAAIAIAABoCAAAmAgAAEgIAACACAAAaAgAAGgIAABoCAAAqAgAAFgIAABgCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAaAgAAFgIAAB4CAAAaAgAASgIAABoCAABEAgAAMAIAABY",
    "CAAAkAgAAIgIAACYCAAAiAgAAGAIAACYCAAAgAgAAHAIAABICAAAUAgAAFAIAABICAAAUAgAAFAIAABQCAAAUAgAAGAIAABgCAAAeAgAAHgIAABoCAAAkAgAAMAIAACICAAAiAgAAIgIAACICAAA2AgAAPgIAACA",
    "CAAAWAgAAGgIAABQCAAAUAgAAGAIAABgCAAAWAgAAGAIAABYCAAAUAgAAFgIAABYCAAAcAgAAGgIAABoCAAAUAgAAEgIAABICAAASAgAAEgIAABYCAAAUAgAAFAIAABYCAAAUAgAAFAIAABgCAAAaAgAAFgIAABY",
    "CAAAaAgAAFAIAABoCAAAaAgAAHgIAACICAAAWAgAAGgIAABYCAAAaAgAAFgIAABoCAAAoAgAAFAIAABQCAAAUAgAAFgIAABYCAAAUAgAAFAIAABYCAAAUAgAAFgIAABYCAAAWAgAAGAIAABYCAAAWAgAAFAIAABg",
    "CAAAUAgAAFgIAABgCAAAUAgAAFAIAABQCAAAWAgAAFAIAABYCAAAYAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAHgIAABQCAAAYAgAAFAIAABACAAAYAgAAFAIAABgCAAAWAgAAFgIAABACAAAYAgAAGAIAABg",
    "CAAAQAgAAFgIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABYCAAAYAgAAFgIAABgCAAAYAgAAFgIAABYCAAAYAgAAGAIAABgCAAAYAgAAFgIAABYCAAAWAgAAFgIAACICAAA0AgAAJAIAABoCAAAWAgAAEgIAABo",
    "CAAAUAgAAGgIAAB4CAAAaAgAAFAIAABQCAAAwAgAAFgIAABwCAAAgAgAAKgIAABYCAAAgAgAAFAIAABwCAAAsAgAARAIAAB4CAAAmAgAALgIAABgCAAAaAgAAJAIAABQCAAAcAgAAGgIAABoCAAAkAgAAJAIAACI",
    "CAAAWAgAAGgIAAB4CAAAaAgAAGgIAAB4CAAAWAgAAGgIAABoCAAAWAgAAFgIAABYCAAAiAgAAJAIAAAwCAAAkAgAADAIAAAwCAAASAgAAFgIAACACAAAUAgAAEgIAABICAAAMAgAAGgIAABgCAAAYAgAAGAIAAB4",
    "CAAASAgAAEgIAABICAAASAgAAEgIAABQCAAASAgAAFAIAABgCAAAYAgAAEgIAABQCAAAUAgAAEgIAABICAAAOAgAAFAIAABQCAAASAgAAFAIAAA4CAAAaAgAAHAIAABoCAAAaAgAAFgIAACACAAASAgAAEgIAABw",
    "CAAAkAgAAGgIAAEICAAAiAgAAHgIAABYCAAAcAgAAGAIAABYCAAAWAgAAGgIAABoCAAAaAgAAFgIAABoCAAAaAgAAFgIAABgCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAFgIAABYCAAAWAgAAGAIAABg",
    "CAAAYAgAAFgIAABYCAAAYAgAAFgIAABYCAAAWAgAAGAIAABgCAAAWAgAAFgIAABYCAAAaAgAAGgIAABICAAAcAgAAFAIAABgCAAAaAgAAGgIAABYCAAAaAgAAGgIAABYCAAAaAgAAGgIAABoCAAASAgAAEgIAABQ",
    "CAAAWAgAAFgIAABYCAAAWAgAAFgIAABwCAAAaAgAAGgIAABoCAAAaAgAAGgIAABgCAAAgAgAAFgIAAEACAABEAgAANAIAAB4CAAAYAgAAOgIAACYCAAAQAgAAEgIAABICAAAQAgAAGgIAAEQCAAAqAgAAGgIAABo",
    "CAAAaAgAAGgIAABQCAAAaAgAAGgIAAFQCAAAkAgAADAIAACQCAAAaAgAAGgIAABQCAAAeAgAAKAIAACgCAAAaAgAAKAIAACICAAAiAgAAIgIAABgCAAAWAgAAFgIAABQCAAAUAgAAEgIAAA4CAAAUAgAAEgIAABQ",
    "CAAAOAgAAEAIAABICAAAaAgAAGgIAABoCAAASAgAAFgIAACQCAAASAgAADgIAAA4CAAAWAgAADgIAAA4CAAAWAgAAEgIAABICAAAmAgAAGAIAABwCAAAaAgAAIAIAABoCAAAgAgAAGgIAAB4CAAAaAgAAGgIAABQ",
    "CAAAYAgAAGgIAABoCAAAYAgAAGgIAABoCAAAaAgAAHAIAABoCAAAaAgAAFAIAABwCAAAUAgAAFgIAABYCAAAaAgAAGgIAABwCAAAcAgAAFgIAABwCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAFgIAADICAAAeAgAAHgIAABoCAAAWAgAAFAIAABgCAAAcAgAAEgIAABoCAAAYAgAAFAIAABQ",
    "CAAAUAgAAJAIAABYCAAAUAgAAIgIAABQCAAAaAgAAFAIAABACAAAWAgAASAIAACQCAAAYAgAAIAIAABoCAAAeAgAAHgIAABoCAAAeAgAAIAIAABoCAAAaAgAAIAIAAB4CAAAeAgAAGgIAABoCAAAgAgAAGgIAABo",
    "CAAAeAgAAIAIAACACAAAUAgAAFgIAABQCAAAYAgAAFgIAABICAAAUAgAAGAIAABICAAASAgAAGgIAABQCAAAQAgAAEgIAABICAAAWAgAAGgIAACYCAAAaAgAAGgIAABICAAAgAgAAGgIAABACAAAYAgAAGAIAABo",
    "CAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAGgIAABoCAAAaAgAAHAIAABwCAAAkAgAAGgIAABgCAAAcAgAAGgIAABw",
    "CAAAYAgAAIAIAABgCAAAYAgAAGAIAABICAAAaAgAAEgIAABICAAASAgAAHAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAYAgAAEgIAABICAAAaAgAAGgIAABoCAAAaAgAAHAIAABoCAAAaAgAAFgIAABg",
    "CAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGAIAABgCAAAYAgAAGgIAAB4",
    "CAAAKAgAAGgIAABoCAAAQAgAAIgIAABwCAAAYAgAAGgIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABQCAAAUAgAAFAIAABICAAAUAgAAFAIAABwCAAA0AgAANAIAADQCAAA0AgAANAIAADQCAAAqAgAAKgIAACg",
    "CAAAoAgAAKAIAACgCAAAqAgAAIgIAACgCAAAiAgAAKAIAACgCAAAYAgAAHgIAACICAAAYAgAAGAIAABoCAAAaAgAAGAIAABoCAAAaAgAAGgIAABoCAAAgAgAAGgIAABoCAAAWAgAAFAIAABgCAAAaAgAAHAIAABQ",
    "CAAAUAgAAGAIAABYCAAAYAgAAFgIAACQCAAAaAgAAEgIAABICAAASAgAAFAIAABoCAAAaAgAANgIAACACAAAaAgAAIAIAACACAAAgAgAAHAIAABgCAAAUAgAAFgIAABgCAAAYAgAAOgIAABQCAAAYAgAA4AIAALo",
    "CAABoAgAAlAIAADwCAABuAgAA6AIAAMQCAACIAgAAdAIAAIwCAABUAgAASgIAAFgCAACEAgAAjAIAAKYCAACOAgAAjAIAAHgCAACSAgAAjAIAAIoCAACOAgAAjAIAAGoCAABiAgAAjAIAAIwCAACMAgAAjgIAAD4",
    "CAABaAgAAiAIAAHICAAB6AgAAjAIAAIwCAABoAgAAdAIAAIoCAACAAgAAiAIAAKACAABUAgAAaAIAAFgCAACSAgAAWAIAAIQCAACAAgAAZgIAAGwCAABaAgAAIgIAAGACAABkAgAAdgIAAM4CAACEAgAApAIAAII",
    "CAAAAAgAAxAIAAIoCAACMAgAAlAIAAHYCAACCAgAAhAIAAHYCAACGAgAAkgIAAIQCAACaAgAAlAIAAEQCAACGAgAAfgIAAIwCAAB2AgAApgIAAJoCAACMAgAAhgIAAHACAABGAgAAdAIAAHACAACUAgAAmgIAAO4",
    "CAACKAgAAjAIAAEICAAAaAgAAGAIAABgCAAAeAgAA+gIAAGoCAACkAgAAngIAAIoCAACgAgAAmAIAALQCAACSAgAAnAIAAJICAACaAgAAogIAAJ4CAACmAgAAlgIAAKQCAAC2AgAAnAIAACACAAD8AgAA9gIAAGw",
    "CAAAiAgABBAIAABoCAADqAgAAKAIAABoCAAAYAgAAhAIAABQCAABmAgAAGgIAAFICAAAiAgAAnAIAACwCAAAiAgAAygIAABoCAAAeAgAAGgIAAB4CAADAAgAAJAIAABQCAAAeAgAA7AIAABoCAAAaAgAAQAIAABo",
    "CAAAYAgAAFAIAAEACAABAAgAAPAIAABwCAAAsAgAAFAIAAEACAAAcAgAAGgIAACACAACSAgAAOgIAACgCAAAaAgAAGAIAAE4CAABKAgAAXgIAAMICAAAoAgAAHgIAABoCAAAcAgAARAIAANICAAAgAgAAHgIAAB4",
    "CAACWAgAAqAIAAGwCAAAaAgAAIAIAABoCAAAUAgAAZgIAACICAACIAgAAfgIAALACAAAiAgAATgIAANYCAABcAgAAYgIAAI4CAAB+AgAAgAIAAIQCAAAYAgAAFgIAABoCAAB0AgAAeAIAAIQCAABWAgAAcAIAAEw",
    "CAAAcAgAAIAIAACQCAABUAgAAGgIAACICAABgAgAAGgIAACICAABKAgAAIgIAABgCAAAmAgAAYAIAAF4CAACQAgAAogIAAGQCAABsAgAAZgIAAIICAAAyAgAAIgIAAGACAAAiAgAAqgIAAI4CAAAWAgAAHAIAALg",
    "CAAAiAgAAwAIAAN4CAADeAgAAxAIAANACAADaAgABQAIAABgCAAC8AgAAhgIAAKwCAAAOAgAArgIAANICAACgAgAAGgIAABoCAAC2AgAAGgIAABgCAAAWAgAAGAIAABoCAAAcAgAAqAIAAKoCAADIAgAAFAIAACI",
    "CAADUAgAAGAIAAKoCAAB+AgAAugIAAKgCAAFgAgAAFgIAAMwCAACwAgAAKAIAABACAADGAgAAIgIAARICAACqAgAAlgIAABoCAAAWAgAAsgIAABYCAAAWAgAAGgIAAJgCAAB2AgAAWAIAALwCAACkAgAAHgIAABI",
    "CAAASAgAATAIAAIQCAAAgAgAAHAIAACACAAAWAgAAqgIAAJICAADQAgAAvgIAAJoCAAC2AgAAKgIAAHYCAAC6AgAAJgIAABoCAAESAgAAogIAACACAAEKAgAAIAIAAHACAAC+AgAAwAIAAKwCAACwAgAAvgIAABo",
    "CAAAcAgAAUAIAAFYCAAAcAgAANAIAABYCAAC2AgAA6AIAAM4CAAAWAgAAyAIAANwCAAAgAgABHgIAANgCAACYAgAAogIAAJACAACWAgAArgIAAKoCAAD+AgAAKAIAACgCAAAoAgAAKgIAALICAAAqAgAAKAIAADA",
    "CAAAaAgAA0gIAACACAAAaAgAAQgIAAMgCAAASAgAA2gIAABYCAAAUAgAAqgIAAL4CAADWAgAAGAIAAKICAACuAgAAhAIAACoCAAC8AgAAlAIAAMACAACCAgAA1gIAALgCAACyAgAArAIAANQCAADOAgAAugIAAL4",
    "CAAAaAgAA5AIAAKoCAACwAgAAwAIAAMICAACmAgAAvAIAALICAAEAAgAAqAIAACACAAAaAgAAJAIAAB4CAADoAgAAJAIAABICAADCAgAAGAIAAIoCAACEAgAASgIAAOoCAACOAgAAkAIAAJgCAAC4AgAAGgIAAII",
    "CAAFaAgAACgIAAB4CAACSAgAAtAIAAIQCAAASAgAApAIAAJ4CAACyAgAAgAIAALwCAACMAgAA5AIAAC4CAADWAgAApgIAAJQCAACoAgAAHgIAACoCAACoAgAAlAIAAL4CAADGAgAApAIAAMACAAAcAgAArgIAANg",
    "CAABuAgAAqgIAAQwCAADSAgAAtAIAABgCAAC4AgAAlAIAABICAACqAgAAggIAABoCAACSAgAAtgIAAIwCAADiAgAAxAIAALQCAACOAgAAHgIAAA4CAAAaAgAAGAIAACgCAACeAgAA2gIAAMACAADqAgAAcgIAAIw",
    "CAACeAgAAnAIAAQQCAAASAgAAnAIAAB4CAACuAgAAsAIAAKwCAAAkAgAAegIAAJACAAC0AgAAogIAABICAADkAgAAIAIAACYCAADqAgAArAIAAPwCAAD0AgAAGgIAAQYCAAAgAgAAIAIAAOQCAADQAgAAmgIAAJo",
    "CAADiAgAAuAIAAC4CAACaAgAAGgIAANwCAAAcAgAAvgIAABACAAC+AgAAzgIAAOACAADsAgAAQgIAACwCAAAcAgAAjgIAABwCAAA0AgAA0gIAALwCAAAaAgAAyAIAABICAAD+AgAAJAIAAMgCAABQAgAAegIAAJY",
    "CAAAkAgAAIAIAATQCAAAUAgAAuAIAABICAAAaAgAAHgIAABgCAADEAgAAwAIAAOYCAAAWAgAAuAIAAMICAAEmAgAAtAIAABgCAACCAgAAEgIAAOQCAAAYAgAAGAIAABYCAAAoAgAAtgIAAMoCAACoAgAAzgIAAIQ",
    "CAABkAgAAGgIAANYCAABcAgAA0gIAABgCAACoAgAAwgIAABoCAAASAgAAGgIAAB4CAAAWAgAAvgIAAK4CAACwAgAA0gIAATACAAC4AgAARgIAABQCAAB+AgAAGgIAABoCAADMAgAAFgIAABYCAADqAgAAKAIAABw",
    "CAAC6AgAApAIAAOgCAACEAgAArgIAACgCAAAeAgAAEgIAABwCAAD4AgAAFAIAABwCAACKAgAAHgIAAUICAAAgAgAAGAIAALQCAAEaAgAAiAIAANoCAADOAgAAuAIAAIYCAADYAgAArAIAAOwCAABgAgAAFAIAAFo",
    "CAAAWAgAAdgIAABgCAADAAgAAKAIAADACAADGAgAAGgIAAPoCAADuAgAA9AIAABYCAAC4AgAAFgIAACoCAAAaAgAAHAIAABgCAAD0AgABCAIAABoCAAC2AgAA3AIAAMoCAACiAgAAwgIAAMQCAAAUAgAAFAIAAOQ",
    "CAAASAgAA1AIAABICAACsAgAAPAIAAJwCAACqAgAAKgIAAMwCAACuAgAAJgIAACACAAC6AgAAmAIAABoCAAB0AgAAcAIAAMYCAAC6AgAA7AIAABYCAAC4AgAAGgIAACACAAAcAgAAVgIAACoCAADwAgAAIAIAACA",
    "CAAAaAgAA2gIAAKgCAADkAgAAJgIAAMQCAAC4AgAA2gIAAQwCAAAgAgAAGAIAABgCAADKAgAAogIAAMICAACcAgAAcAIAAI4CAAC2AgAA/AIAAN4CAADgAgAAagIAACICAADoAgAAGgIAAB4CAAAgAgAAuAIAAJQ",
    "CAAAWAgAA6gIAACACAACoAgAA5AIAAQACAAAcAgAAIgIAABwCAADGAgAArAIAABYCAAAmAgAAUgIAABoCAABAAgAAHAIAAGQCAABsAgAAdgIAABQCAACwAgAAIgIAABoCAAAaAgAAugIAACwCAADKAgAAGgIAADQ",
    "CAACqAgAAJgIAAHoCAAAWAgAAyAIAAMwCAAA2AgAALAIAABYCAAEyAgAAtAIAABICAAASAgAAlAIAAMYCAAAaAgAAqgIAAKwCAAFAAgAAFgIAANgCAAAaAgAAEgIAAKgCAAB6AgAAGgIAABoCAAC2AgAAtgIAABo",
    "CAADIAgAAGAIAABYCAAAcAgAAzAIAABoCAAAUAgAAHgIAAOICAAAUAgAAtAIAAJgCAAAUAgAAFgIAACACAACaAgAAEAIAABACAAAUAgAAGgIAAGQCAAEkAgABGgIAABoCAAAcAgAAqgIAAH4CAACKAgAAmAIAALw",
    "CAAA8AgAAkgIAAQoCAADsAgAA7gIAABQCAADcAgAAPAIAABQCAAAUAgAAFAIAABQCAAAWAgAAHAIAAPICAAAaAgAAGgIAABoCAAAaAgAAbgIAAEQCAACQAgAAGgIAAMYCAACoAgAAHgIAACICAABWAgAAsAIAAJA",
    "CAAAcAgAAKgIAACoCAADAAgAA2gIAANICAAAUAgAAwAIAAMgCAAAcAgAAhgIAABICAAAwAgAAIgIAASoCAAAgAgAAHAIAAJ4CAAASAgAAuAIAABQCAACYAgAArgIAABoCAAAaAgAA9AIAACQCAAAYAgAAqAIAALY",
    "CAAAqAgAAEgIAABQCAAASAgAAEgIAAQ4CAAASAgAAFgIAABYCAAAaAgAAEgIAACYCAAAWAgAAFgIAABQCAAD2AgABKAIAAPICAADcAgAAFAIAAM4CAACsAgAAxAIAAKoCAACQAgAAwAIAAKACAAGIAgAAIgIAAJo",
    "CAACeAgAAHAIAAIACAADMAgAAogIAAOQCAAE2AgAAJgIAABoCAAAmAgAAjgIAABQCAACkAgAAngIAABwCAAAcAgAAFAIAAOACAAAUAgAAGgIAAOYCAAAUAgAAjAIAAOoCAAAaAgAA2gIAAQwCAAFcAgAA1gIAAMw",
    "CAAC4AgAA5gIAAJoCAACiAgABAAIAABQCAAAWAgAA+AIAATACAAAUAgABEAIAAMgCAAAWAgAAygIAALoCAAAaAgAAGgIAABoCAAAYAgAAFgIAAKACAADQAgABIAIAASACAAA8AgAAIgIAAGQCAAAqAgAAHAIAABQ",
    "CAAAaAgAA7AIAAMACAAAYAgAAHAIAABoCAAAUAgAAFAIAAIoCAADCAgAAsAIAAM4CAAC8AgAAFgIAABYCAACcAgAALgIAACACAACQAgAAFAIAALYCAAC4AgAAFAIAABoCAADmAgABVgIAABgCAAAqAgAAnAIAACY",
    "CAAAYAgAALgIAABoCAACiAgAAGgIAABgCAAAeAgAA8AIAABYCAACmAgAAtgIAAJoCAAAaAgAAGgIAACgCAADIAgAAzAIAAIICAACkAgAAGgIAACwCAAEGAgAAFgIAABwCAAAmAgAADgIAAHQCAAAUAgAAFAIAAMQ",
    "CAAEeAgABQgIAAMICAAAUAgAAGgIAAOYCAAAaAgAAfAIAAI4CAAAWAgABAAIAABQCAADkAgAAwgIAABICAAAaAgAAGgIAAFYCAAFiAgAArAIAAIACAAFaAgAAFAIAABYCAAASAgAAsgIAABgCAAESAgAAbAIAAIw",
    "CAAFsAgAAFgIAAEYCAAAYAgAAGgIAAB4CAAEAAgAAiAIAABACAADYAgAAEgIAAKACAAAMAgABOAIAABoCAAAUAgAAsgIAAB4CAAB0AgAAFgIAALoCAACqAgAAtgIAABICAADaAgAAGgIAACACAAAgAgAAGgIAARY",
    "CAAAgAgAAJgIAAMICAAAiAgAAJAIAAFYCAACYAgAAFAIAABYCAAAUAgAAGgIAANwCAAAaAgAA0gIAAUQCAAAkAgAA2gIAAOwCAAAYAgAAFgIAABYCAAAeAgAAMAIAACICAAAaAgAAGgIAABoCAAAaAgAAFAIAABQ",
    "CAAAUAgAAFAIAABoCAAAaAgAAIAIAACQCAAAoAgAAtgIAAMYCAACMAgAAGAIAAJYCAAAiAgAAIgIAALoCAACmAgAAEgIAAMQCAAAWAgAAjAIAAA4BM0AAAHnAR0ALQAAAScBKQCFAJgBuAEdAc8A0wCTAOEAngCD",
    "AD0ArACaAI8AnACaAecBmgCYAJgAmACoAB8AIQCHAIEAhwDZAPQAdQCHAOEAiQDTAOkAcQCHAFQAsABUALoAjQBmAH0AIQACADUAIQBmAZwA0wEh//ABogCHAJ4ArACJAIUAnABmAKAAxQCHANcAvABcAKAAcwCe",
    "AIkBCADLAIsAoABS//wAYABSALYA4QIbAOMAmAFcAecAvv/6AE4ARgAAAAIAAAADAAAAFAADAAEAAAAUAAQcIAAABwQEAAAJAwQAIwAlAF0AfgCyALcA1yAUICYhkyIeJGYlsiW2JbwlwCXGJc8mBicTMAIwDTAR",
    "TgBOB04LTg5OFE4iTiVOKk4tTjROO05FTklOS05OTllOXU5gTmZOcU6GTolOjE6OTpJOlE6bTqROp06uTrpOwE7GTs5O007WTuVO9077Tv1PEU8YTxpPIE8kTzhPPE9GT09PU09VT1lPXE9gT39Pi0+bT51Pp0+/",
    "T91P7lANUBJQGVA8UD5QR1BPUFpQXFB/UKhQrFC7UM9Q9VFDUUlRTVFcUWVRaFFtUXFRc1F4UXxRhVGNUZlRs1G1UbdRu1HAUcZRz1HRUeBR9lH7Uf1SAFIDUgdSElIXUhlSG1IdUiRSK1IwUjdSO1JNUlRSalKI",
    "UptSoVKpUr9TBVMWUzpTQVNDU0dTSlNVU1dTYVNwU3RTd1OLU5pTn1O7U8JTyFPKU81T0VPYU+BT5FPsU/BT81P3VARUCFQOVBFUJlQsVC9UOFRIVFhUaFR9VIxUwVTIVM1U5VTqVSRVL1VGVYpV3FY0VmhWylbb",
    "Vt5W4FbiVvRW+lb+VwZXCFcjVyhXMFc6V0BXR1dQV1dXgleLV99X+liDWJ5ZBFkHWQ1ZFlkaWRxZJ1kqWS5ZMVk0WVFZV1llWXNZdll9WctZ0Fn/WhhazFtQW1hbZluDW4lbjFuYW5pbnluiW6RbqluzW7ZbuVu9",
    "W/lb/FwEXA9cEVwWXBhcHVwxXDpcPlxAXEJcRVxPXF5dKV1MXeZd6F3uXfJeA14nXjheRV5VXnNedl6PXpVel16mXq1e9l76XwBfAl8PXxVfIF8nXzpfU19VX2JfcV97X4BfhV+LX5dfoV+qX65fvV/DX8Vf11/r",
    "YAFgDmASYB1gJ2A7YFJgYmDFYPNhCGEPYR9hYmISYhZiGGIqYjRiQGJHYktiTWJTYlhiW2JjYmdiaWJrYnBigGKEYopik2KVYphiomKkYqxisWK1YsZiyWLNYtJi1mLbYt9i6WLxYv9jAmMHYwljEWMhYyRjKGMq",
    "Y19jYmNuY3djiWOSY6VjqGO3Y9Bj0mP0ZBxkHmQtZEdkWGR4ZJ5kpGStZMVkzmUvZTZlOWU7ZT5lSGVMZU9lY2VwZXRlh2WLZZdlnGWnZallrWWwZblly2XgZeJl52XpZfZmDmYTZiBmL2Y+Zm9mgmaXZrRm9GcA",
    "ZwlnDWcdZx9nLGcvZzVnOmdAZ0NnRmdQZ19nYWdlZ39ngWeEZ5xntmfQZ9Nn5WgHaA9oIWg5aDxoRmhIaExoY2hlaHZor2jAaS1pzGn9aiFqKmpZayFrZWt7a7VrzWvPa9Jr1GwUbDRsOGxCbEdsSWyJbKFsv2zJ",
    "bNVs4mzobPxtO20+bUFtS21PbW5td22Ibaht4W3xbfduBW4QbiFuMm44bpBu0W7ebuFvAm8Ub8Bwa3B1cK5wuXDfcO1xNnFncgZyKnIxckhyTHJZcmlyeXK2ctBy7HL4cxtzK3OHc6lzsHQDdAZ093UfdSh1MnU1",
    "dTt1THVZdWV1l3WrddV2e3Z9doR2xnbKds920nbWdth27nb0dvl2/ncBdwt3IHc8d0B3W3dhd6x3s3fld+l37XgBeBR4NHg4eEB4bHhueJd4sHi+eTp5PHk+eV55gXm7ecF5zXnSedh58Hn7egt6M3o/enp6f3qB",
    "epd6nXrLetZ62Xrgeu97G3smeyx7SXtUe1Z7fnuAe5d7oXute8d8B3xzfHt8knzKfPt9IH0ifSd9K30vfqJ+p36vfrl+v37Efsh+037Vftl+3X7ffud+6X7tfwB/E38Wfxh/KX86f1F/aX9uf45/+4ADgAWADIAX",
    "gDOATIBUgFqApYDMgNyA9oD9gRGBGoFwgX+BwoHqgfSCDIJygoKCsYLPguWDA4M2g1CDt4PchCWEPYS4hMSE3YXPhlqGy4eDh/mIQIhFiEyIYYhliGiIcIiNiKuIwojFiNmI+ImBiYaJwonEicaJyYnSieOJ5ooA",
    "i6GLpIupi66LsIuyi7iLv4vBi82L0YvVi92L5Yvti++L9Iv7jAGMA4xhjGqNH40jjSaNKI0vjTSNOY1EjUuNVI1WjXCNd42FjYqNs43DjdGN3Y3fje+N844pjquOso66j2iPbI9uj3uPfY+Rj5OPqI+5j8WPx4/R",
    "j9SP2Y/cj9+P94/9kAKQCZAQkBKQGpAgkDuQU5BukH+Qo5DokP2RTZGSkcqRzZHPkdGUiJSflK6UwZT2lPqVAZULlRmVLpVclX+V6JXqle6V9JYBljKWNZZFlk2WUJZklmmWkJaUlsaW9pcAlweXMpc4l1KXWZde",
    "l2CXYpfzmHaYe5h/mISYmJidmM6Y2JjfmW2ZcJmImY+ZlpmZmmyacZp7mn+ajJqomticfJy4niGe0Z7YnyCfUJ+Z/17//wAAACAAJQAoAF8AsgC3ANcgFCAmIZAiHiRgJbIltiW8JcAlxiXPJgUnEzAAMAowEE4A",
    "TgdOCU4NThNOIk4kTipOLU40TjpORU5ITktOTk5ZTl1OX05mTnFOhk6JTotOjk6STpROm06kTqdOrk66Tr9OxU7NTtNO1k7jTvZO+079TxFPGE8aTyBPJE84TzxPRk9NT1NPVU9ZT1xPYE9/T4tPm0+dT6dPv0/d",
    "T+5QDVASUBlQPFA+UEdQT1BaUFxQf1CoUKxQu1DPUPVRQ1FIUU1RXFFlUWhRbVFxUXNRdlF8UYVRjFGZUbJRtVG3UbtRwFHGUc9R0VHgUfZR+lH9UgBSA1IGUhJSF1IZUhtSHVIkUitSMFI2UjpSTVJUUmlSiFKb",
    "Up5SqFK/UwVTFlM6U0FTQ1NHU0pTVVNXU2BTcFNzU3dTi1OaU59Tu1PCU8hTylPMU9FT1lPgU+NT6lPvU/NT91QDVAhUDFQRVCZUK1QvVDhUSFRYVGhUfVSMVMFUyFTNVOVU6lUkVS9VRlWKVdxWNFZoVspW21be",
    "VuBW4lb0VvpW/lcGVwhXI1coVzBXOldAV0dXT1dXV4JXi1ffV/pYg1ieWQRZB1kNWRZZGlkcWSdZKlkuWTFZNFlRWVdZZVlzWXZZfVnLWdBZ/1oYWsxbUFtXW2Zbg1uJW4xbmFuaW55boFukW6pbs1u2W7lbvVv4",
    "W/xcBFwPXBFcFlwYXB1cMVw6XD5cQFxCXEVcT1xeXSldTF3lXehd7l3xXgNeJl44XkVeVV5yXnZej16TXpdepl6tXvZe+l8AXwJfD18VXyBfJ185X1JfVV9iX3Ffe1+AX4Rfi1+XX6Ffql+uX71fw1/FX9df62AB",
    "YA5gEmAdYCdgO2BSYGJgxWDzYQhhD2EfYWJiD2IWYhhiKmI0Yj9iR2JLYk1iU2JYYltiY2JnYmlia2JwYn5ihGKKYpNilWKYYqJipGKsYrFitWLFYslizWLSYtZi22LfYuli8WL9YwFjB2MJYxFjIWMkYyhjKmNf",
    "Y2JjbmN3Y4ljkmOlY6djt2PPY9Jj9GQcZB5kLWRGZFhkeGSeZKRkrWTFZM1lL2U2ZTllO2U+ZUhlTGVPZWNlcGV0ZYdli2WXZZxlp2WpZa1lsGW5Zctl4GXiZedl6WX2Zg5mE2YfZi9mPmZuZoJmlma0ZvRm/2cI",
    "Zw1nHWcfZypnL2c1ZzpnQGdDZ0ZnUGdfZ2FnZWd/Z4FnhGecZ7Zn0GfTZ+VoB2gPaCFoN2g8aEZoSGhMaGNoZWh2aK9owGktacxp/WohaipqWWsga2Jre2u1a81rz2vSa9RsFGw0bDhsQmxHbElsiWyhbL9syWzV",
    "bOFs6Gz8bTttPm1BbUttT21ubXdtiG2obeFt8W33bgVuEG4hbjJuOG6QbtFu3m7hbwJvFG/AcGtwdXCucLlw33DtcTZxZ3IGcipyMXJHckxyWXJpcnlytnLQcuxy+HMbcytzh3Opc690A3QGdPd1H3UodTF1NXU7",
    "dUx1WXVldZd1q3XVdnt2fXaEdsZ2ynbPdtF21nbYdu529Hb4dv53AXcLdx93PHdAd1t3YXesd7N35Xfpd+14AXgUeDR4OHhAeGx4bniXeLB4vnk6eTx5PnleeYF5u3nBec150nnYefB5+3oLejN6P3p6en96gXqX",
    "ep16y3rWetl64Hrvext7Jnsse0l7VHtWe357gHuXe6F7rXvHfAd8c3x7fJJ8ynz7fSB9In0nfSt9L36ifqZ+r363fr9+w37IftN+1X7Yft1+337nful+7X8AfxN/Fn8Yfyl/On9Rf2l/bn+Of/uAA4AFgAyAF4Az",
    "gEyAVIBagKWAzIDcgPaA/YERgRqBcIF/gcKB6oHzggyCcoKCgrGCz4LlgwODNoNQg7eD3IQlhD2EuITEhN2Fz4ZahsuHg4f5iECIRYhMiGGIZYhoiHCIjYiriMGIxYjZiPiJgYmGicGJxInGiciJ0onjieaKAIuh",
    "i6SLqYuti7CLsou4i76LwYvNi9GL1Yvdi+WL7Yvvi/SL+4wBjAOMYYxqjR+NI40ljSiNL400jTmNRI1LjVSNVo1wjXeNhY2KjbONw43Rjd2N343vjfOOKY6rjrKOuo9oj2yPbo97j32PkY+Tj6iPuY/Fj8eP0I/U",
    "j9iP24/ej/eP/ZAAkAmQD5ASkBqQH5A7kFOQbpB/kKOQ6JD9kU2RkpHKkcyRz5HRlIiUn5SulMGU9pT6lQCVC5UZlS6VXJV/leiV6pXtlfSWAZYyljSWRJZNllCWZJZplo+WlJbGlvaXAJcHlzKXOJdSl1mXXpdg",
    "l2KX85h1mHmYfpiEmJeYnJjOmNiY3pltmXCZiJmPmZaZmZpsmnGae5p/moyaqJrYnHycuJ4hntGe2J8gn1Cfmf8B//8IVwhWCFQIUwggCBwH/ejB6LDecea526XaWtpX2lLaT9pK2kLaDdkB0BXQDtAMsh6yGLIX",
    "shayErIFsgSyALH+sfix87Hqseix57Hlsdux2LHXsdKxyLG0sbKxsbGwsa2xrLGmsZ6xnLGWsYuxh7GDsX2xebF3sWuxW7FYsVexRLE+sT2xOLE1sSKxH7EWsRCxDbEMsQmxB7EEsOaw27DMsMuwwrCrsI6wfrBg",
    "sFywVrA0sDOwK7AksBqwGa/3r8+vzK++r6uvhq85rzWvMq8krxyvGq8WrxOvEq8Qrw2vBa7/rvSu3K7brtqu167Trs6uxq7Frreuoq6frp6unK6arpiujq6KromuiK6HroGue653rnKucK5frlmuRa4orhauFK4O",
    "rfmttK2krYGte616rXetda1rrWqtYq1UrVKtUK0+rTCtLK0RrQutBq0FrQStAaz9rPas9KzvrO2s66zorN2s2qzXrNWsway9rLuss6ykrJWshqxyrGSsMKwqrCasD6wLq9KryKuyq2+rHqrHqpSqM6okqiKqIaog",
    "qg+qCqoHqgCp/6nlqeGp2qnRqcypxqm/qbmpj6mHqTSpGqiSqHioE6gRqAyoBKgBqACn9qf0p/Gn76ftp9GnzKe/p7KnsKeqp12nWacrpxOmYKXdpdelyqWupamlp6WcpZulmKWXpZalkaWJpYelhaWCpUilRqU/",
    "pTWlNKUwpS+lK6UYpRClDaUMpQulCaUApPKkKKQGo26jbaNoo2ajVqM0oySjGKMJou2i66LUotGi0KLCoryidaJyom2ibKJgoluiUaJLojqiI6IiohaiCKH/ofuh+KHzoeih36HXodShxqHBocChr6GcoYehe6F4",
    "oW6hZaFSoTyhLaDLoJ6giqCEoHWgM5+Hn4Sfg59yn2mfX59Zn1afVZ9Qn0yfSp9Dn0CfP58+nzqfLZ8qnyWfHZ8cnxqfEZ8QnwmfBZ8CnvOe8Z7unuqe557jnuCe157QnsWexJ7Anr+euJ6pnqeepJ6jnm+ebZ5i",
    "nlqeSZ5Bni+eLp4gngmeCJ3nncCdv52xnZmdiZ1qnUWdQJ04nSGdGpy6nLScspyxnK+cppyjnKGcjpyCnH+cbZxqnF+cW5xRnFCcTZxLnEOcMpwenB2cGZwYnAyb9Zvxm+ab2JvKm5ubiZt2m1qbG5sRmwqbB5r4",
    "mvea7Zrrmuaa4prdmtua2ZrQmsKawZq+mqWapJqimouacppZmleaRpolmh6aDZn4mfaZ7ZnsmemZ05nSmcKZipl6mQ6YcJhAmB2YFZfnlyGW4ZbMlpOWfJZ7lnmWeJY5lhqWF5YOlgqWCZXKlbOVlpWNlYKVd5Vy",
    "lV+VIZUflR2VFJURlPOU65TblLyUhJR1lHCUY5RZlEmUOZQ0k92TnZORk4+Tb5NekrOSCZIAkciRvpGZkYyRRJEUkHaQU5BNkDiQNZApkBqQC4/Pj7aPm4+Qj26PX48EjuOO3o6MjoqNmo1zjWuNY41hjVyNTI1A",
    "jTWNBYzyjMmMJIwjjB2L3IvZi9WL1IvRi9CLu4u2i7OLr4uti6SLkYt2i3OLWYtUiwqLBIrTitCKzYq6iqiKiYqGin+KVIpTiiuKE4oGiYuJiomJiWqJSIkPiQqI/4j7iPaI34jViMaIn4iUiFqIVohViECIO4gO",
    "iASIAof8h+6Hw4e5h7SHmIeOh42HZodlh0+HRoc7hyKG44Z4hnGGW4YkhfSF0IXPhcuFyIXFhFOEUIRJhEKEPYQ6hDeELYQshCqEJ4QmhB+EHoQbhAmD94P1g/SD5IPUg76Dp4Ojg4SDGIMRgxCDCoMAguWCzYLG",
    "gsGCd4JRgkKCKYIjghCCCIGzgaWBY4E8gTSBHYC4gKmAe4BegEmALH/6f+F/e39Xfw9++H5+fnN+W31qfOB8cHu5e0R6/nr6evR64Hrdett61Hq4ept6hnqEenF6U3nLecd5jXmMeYt5inmCeXJ5cHlXd7d3tXex",
    "d653rXesd6d3onehd5Z3k3eQd4l3gnd7d3p3dndwd2t3ancNdwV2UXZOdk12THZGdkJ2PnY0di52JnYldgx2BnX5dfV1zXW+dbF1pnWldZZ1k3VedN1013TQdCN0IHQfdBN0EnP/c/5z6nPbc9Bzz3PHc8VzwnPB",
    "c8BzqXOkc6JznHOXc5Zzj3OLc3FzWnNAczBzDXLJcrVyZnIicetx6nHpcehvMm8cbw5u/G7IbsVuwG63bqpulm5pbkdt323ebdxt123LbZttmm2MbYVtg21wbWxtR21EbRNs5GzbbNVsq2ymbI1sh2yDbIJsgWvx",
    "a3Brbmtsa2hrVmtTayNrGmsVaohqhmpvamlqY2phaY9pi2mCaX9pc2lYaSlnhmdLZeNlNGUuZOdkuGRwBQkAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
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
    "AAApeQAAKY8AACmlAAApuwAAKdEAACnnAAAp/QAAKhMAACopAAAqhwAAKv8AACtZAAArugAAK9AAACwxAAAsogAALTEAAC1HAAAtXQAALXMAAC2JAAAtnwAALbUAAC3LAAAt4QAALfcAAC4NAAAuIwAALjkAAC5P",
    "AAAvDAAALyIAAC84AAAvTgAAL2QAAC/GAAAwXgAAMHQAADCKAAAwoAAAMLYAADDMAAAw6AAAMX8AADGVAAAyAQAAMjEAADJ7AAAy5wAAM1gAADPwAAA0mAAANOIAADU0AAA1SgAANWAAADV2AAA1jAAANbsAADXR",
    "AAA15wAANf0AADZ3AAA3VQAAN8QAADhMAAA4YgAAOPkAADmvAAA5xQAAOowAADqiAAA6uAAAOusAADtAAAA7ngAAO7QAADwnAAA8iAAAPP4AAD1pAAA90QAAPecAAD39AAA+dAAAPtsAAD9dAAA/ygAAQDUAAEBL",
    "AABAYQAAQHcAAECNAABAowAAQQYAAEGJAABCHwAAQsAAAELWAABDTQAAQ2MAAEN5AABECQAARCUAAEQ7AABEUQAARRcAAEUtAABFQwAARVkAAEZIAABGZAAARpcAAEatAABG/QAARxMAAEcpAABHPwAAR1UAAEdr",
    "AABHgQAAR5cAAEetAABINAAASEoAAEhgAABIdgAASIwAAEiiAABJOAAASU4AAEoAAABKHAAASjIAAErxAABLBwAASx0AAEvBAABL1wAATJEAAEynAABNWAAATW4AAE3BAABOMAAATrUAAE89AABPxwAAT+MAAE/5",
    "AABQDwAAUJYAAFCsAABQwgAAUNgAAFDuAABRBAAAURoAAFEwAABRjQAAUaMAAFJDAABSWQAAUm8AAFKFAABTHgAAUzQAAFPIAABT3gAAU/QAAFQKAABUIAAAVDYAAFRMAABUYgAAVHgAAFSOAABUpAAAVQYAAFUc",
    "AABVMgAAVUgAAFWrAABWFAAAVioAAFZAAABW7QAAVwMAAFdiAABXeAAAV44AAFekAABXugAAV9AAAFfmAABX/AAAWBgAAFhIAABYrgAAWO8AAFmaAABZ/QAAWmEAAFrnAABblAAAW6oAAFxYAABcbgAAXIoAAFzG",
    "AABdLwAAXbcAAF36AABeEAAAXiYAAF48AABeUgAAXmgAAF5+AABelAAAXwQAAF8aAABfMAAAX5wAAF+yAABgUwAAYGkAAGB/AABglQAAYKsAAGDBAABg1wAAYUMAAGFZAABhbwAAYYUAAGGhAABhtwAAYc0AAGHj",
    "AABh+QAAYg8AAGIrAABiQQAAYl0AAGJ5AABjBQAAY7sAAGPRAABj5wAAY/0AAGQTAABkKQAAZD8AAGRVAABkawAAZIEAAGSXAABkrQAAZMMAAGTZAABk7wAAZQUAAGUbAABlMQAAZf4AAGbyAABnCAAAZ88AAGfl",
    "AABn+wAAaBEAAGgnAABoPQAAaFMAAGjMAABpLAAAaUIAAGlYAABpbgAAaYQAAGmaAABpsAAAacYAAGncAABp8gAAasgAAGreAABq9AAAawoAAGsgAABrNgAAa0wAAGtiAABreAAAa44AAGukAABrugAAa9AAAGvm",
    "AABr/AAAbBIAAGwoAABsPgAAbFQAAGxqAABsgAAAbJYAAGysAABswgAAbNgAAGzuAABtBAAAbRoAAG0wAABtRgAAbVwAAG1yAABtiAAAbaQAAG26AABt0AAAbeYAAG38AABuEgAAbigAAG4+AABuVAAAbmoAAG6G",
    "AABunAAAbrIAAG7IAABu3gAAbvQAAG8KAABvIAAAbzYAAG9MAABvYgAAb3gAAG+OAABvqgAAb8AAAG/WAABv7AAAcAIAAHCJAABwnwAAcLUAAHDLAABw4QAAcPcAAHENAABxIwAAcTkAAHFPAABxZQAAcecAAHH9",
    "AAByYgAAcngAAHKOAABzTwAAc2UAAHN7AABz7gAAdAQAAHSAAAB0lgAAdKwAAHUCAAB1GAAAdS4AAHXRAAB2VwAAdm0AAHb+AAB3FAAAd9MAAHfpAAB3/wAAeBUAAHgrAAB5NwAAed8AAHn1AAB6CwAAenoAAHsI",
    "AAB7HgAAezQAAHtKAAB7vQAAfC4AAHyjAAB9FwAAfagAAH2+AAB91AAAfeoAAH4AAAB+FgAAfqIAAH64AAB/UQAAf2cAAH99AAB/kwAAgC0AAIBDAACAWQAAgHUAAICLAACAoQAAgLcAAIDNAACA4wAAgPkAAIEP",
    "AACBJQAAgTsAAIFRAACBZwAAgX0AAIGTAACBqQAAgb8AAIHVAACB8QAAggcAAIIdAACCMwAAgkkAAIJfAACC3gAAgvQAAIMvAACDdQAAg/8AAIR8AACFJQAAhTsAAIX3AACGygAAhuAAAIdcAACHwwAAiE4AAIjw",
    "AACJpwAAib0AAInTAACJ6QAAif8AAIoVAACKzwAAiuUAAIr7AACLEQAAiycAAIs9AACLUwAAi2kAAIt/AACLmwAAi7cAAIvNAACL4wAAi/kAAIwVAACMKwAAjEEAAIxXAACMbQAAjIMAAIyZAACMrwAAjNEAAIzn",
    "AACM/QAAjRMAAI0pAACNPwAAjVUAAI13AACN9wAAjg0AAI4jAACOOQAAjk8AAI5rAACOgQAAjp0AAI6zAACPGAAAkAgAAJBXAACQbQAAkIMAAJD5AACRDwAAkSUAAJE7AACRUQAAkWcAAJF9AACRkwAAkakAAJHF",
    "AACR2wAAkfEAAJIHAACSHQAAkjMAAJJJAACSsgAAk0kAAJO2AACUIgAAlLkAAJU/AACV5AAAlfoAAJYQAACWdwAAlo0AAJajAACWuQAAls8AAJcjAACXOQAAl08AAJdlAACXewAAl5EAAJenAACXvQAAl9MAAJgi",
    "AACYngAAmLQAAJjKAACZeQAAmhYAAJq+AACbaQAAm38AAJuVAACcVwAAnG0AAJyDAACcmQAAnK8AAJzFAACc2wAAnPEAAJ0HAACdHQAAnTMAAJ1JAACdXwAAnXUAAJ2LAACdoQAAnbcAAJ3NAACeSgAAnmAAAJ52",
    "AACejAAAnqgAAJ+fAACftQAAn8sAAJ/hAACf9wAAoA0AAKAjAACgOQAAoE8AAKBlAACgewAAoJEAAKCnAACgvQAAoNMAAKE7AAChUQAAoWcAAKIMAACiIgAAojgAAKJOAACiZAAAonoAAKKQAACipgAAorwAAKLS",
    "AACi6AAAov4AAKMUAACjKgAAo0AAAKPHAACj3QAAo/MAAKQPAACk7wAApQUAAKUbAAClNwAApU0AAKVjAACleQAApY8AAKWlAACluwAApdEAAKXnAACl/QAAphMAAKYpAACmPwAAplUAAKZrAACmgQAAppcAAKat",
    "AACmwwAAptkAAKbvAACnBQAApxsAAKcxAACnRwAAp10AAKdzAACniQAAp58AAKhcAACocgAAqIgAAKieAACotAAAqU0AAKngAACqTgAAqmQAAKrbAACq8QAAqwcAAKsdAACrMwAAq0kAAKtfAACrdQAAq5cAAKuz",
    "AACrzwAAq+UAAKwBAACsFwAArHkAAKz4AACtDgAArX0AAK4cAACuMgAArkgAAK5eAACudAAArpAAAK9lAACvewAAr5cAAK+tAACvwwAAr98AAK/7AACwEQAAsC0AALBDAACwWQAAsG8AALCFAACwmwAAsQEAALEX",
    "AACxLQAAsUkAALFfAACyBgAAshwAALIyAACySAAAsl4AALJ6AACykAAAsqYAALK8AACy0gAAsugAALNpAACzfwAAs5UAALOrAACzxwAAs90AALSfAAC0tQAAtMsAALU2AAC1TAAAtWIAALV4AAC1jgAAtaQAALW6",
    "AAC10AAAteYAALX8AAC2EgAAtigAALY+AAC2VAAAtmoAALaAAAC2lgAAtqwAALbCAAC22AAAtu4AALcEAAC3GgAAuCoAALhAAAC42QAAuO8AALkFAAC5GwAAuTEAALn4AAC6DgAAuxEAALsnAAC7PQAAu1MAALtp",
    "AAC77gAAvAQAALwaAAC8MAAAvKgAALy+AAC81AAAvOoAAL0AAAC9FgAAvSwAAL1CAAC94QAAvfcAAL4NAAC+IwAAvjkAAL5PAAC+ZQAAvnsAAL6RAAC+pwAAvsMAAL8eAAC/NAAAv0oAAL9gAAC/dgAAv4wAAL+i",
    "AAC/uAAAv84AAL/kAAC/+gAAwBAAAMAmAADAPAAAwOEAAMD3AADBDQAAwSMAAME5AADBTwAAwWUAAMF7AADBkQAAwacAAMG9AADB0wAAwekAAMH/AADCFQAAwisAAMJBAADCVwAAwm0AAMKDAADCmQAAwxUAAMPC",
    "AADEcwAAxQ4AAMUkAADFOgAAxVAAAMVmAADFfAAAxZIAAMWoAADFvgAAxdQAAMXqAADGAAAAxhYAAMaHAADG4AAAxvYAAMcMAADHIgAAxzgAAMdOAADHZAAAx3oAAMeQAADHrAAAx8IAAMfYAADH7gAAyAQAAMga",
    "AADINgAAyEwAAMhiAADIeAAAyI4AAMikAADIugAAyNAAAMjsAADJgQAAyZcAAMoBAADKFwAAypkAAMspAADLpgAAy7wAAMvSAADL6AAAy/4AAMwUAADMKgAAzEAAAMxWAADMbAAAzIIAAMyYAADNMwAAzUkAAM2o",
    "AADOZgAAznwAAM6SAADOqAAAzr4AAM9OAADP6wAA0E4AANBkAADQegAA0JAAANCmAADRRAAA0dcAANJuAADShAAA0poAANN5AADTjwAA1JwAANSyAADVZwAA1aIAANXOAADWRQAA1sEAANdgAADX7gAA2AsAANhF",
    "AADYfwAA2MgAANj4AADZHwAA2T0AANlaAADZeQAA2dQAANn9AADaTgAA2rcAANr/AADbVwAA28YAANvrAADcawAA3NgAAN0FAADdOwAA3WUAAN2NAADdtwAA3iUAAN7dAADfIgAA344AAN/hAADgLgAA4F4AAOCH",
    "AADg6gAA4RgAAOFLAADhfgAA4bUAAOHTAADiHgAA4loAAOK+AADjBwAA43gAAOPMAADkNwAA5FoAAOSeAADk0AAA5TEAAOVtAADlmwAA5cgAAOXvAADmDgAA5jQAAOZfAADmegAA5p8AAOcKAADnbAAA57kAAOga",
    "AADodgAA6L8AAOlzAADptwAA6gUAAOpfAADqmgAA6sgAAOsqAADragAA68MAAOwmAADsigAA7MIAAO0lAADtbgAA7bAAAO3lAADuQAAA7n4AAO7PAADu/AAA71oAAO90AADv0wAA8AsAAPBBAADwpwAA8YsAAPIb",
    "AADymwAA8yIAAPOsAADz5QAA9A8AAPTWAAD1XAAA9cIAAPZtAAD3GAAA980AAPh9AAD42wAA+UgAAPm/AAD6MAAA+ogAAPruAAD7TwAA+7EAAPwgAAD8vwAA/SgAAP2kAAD+hAAA/xcAAP+MAAD/zgABADEAAQC4",
    "AAEBYgABAhwAAQNDAAEDnQABBKIAAQUCAAEF3QABBnUAAQbcAAEHiwABB/cAAQiRAAEI+wABCYgAAQoNAAEKeQABCvEAAQvaAAEMVQABDKkAAQ1mAAEN6wABDmwAAQ8GAAEPjQABEAsAARB0AAEQ5AABEW0AARHb",
    "AAESPwABErAAARMUAAETzQABFD8AARSnAAEVNAABFb0AARZ/AAEXRgABF60AARfuAAEYHgABGGoAARjIAAEZHAABGdYAARpqAAEawwABGt0AARtsAAEbuAABHI4AAR1sAAEeEQABHrcAAR9pAAEfwAABIHQAASE6",
    "AAEhwgABIhUAASKBAAEjYgABI88AASQLAAEkmAABJOoAASU2AAEl6gABJoAAASbJAAEnLQABJ5wAASgWAAEojgABKOgAASmjAAEqYAABKrMAASsXAAErawABK/IAASxHAAEs8QABLagAAS4gAAEugQABLyoAAS+0",
    "AAEv/wABMFkAATCzAAExYAABMdUAATKHAAEy6AABM8wAATQeAAE1TAABNX8AATYRAAE2kwABNuQAATdGAAE3jgABN+0AATiAAAE42gABOYoAAToXAAE6VgABOuMAATtdAAE73QABPG0AATzDAAE9NwABPaIAAT5S",
    "AAE+tQABPvMAAT99AAFAGwABQM8AAUF/AAFBzgABQk0AAUKeAAFDEgABQ4IAAUPzAAFEiwABRPsAAUVoAAFFvAABRhUAAUaPAAFHTgABSDQAAUjZAAFJbQABSlYAAUq4AAFLGAABS4gAAUxTAAFNAwABTa8AAU5h",
    "AAFOqQABTvkAAU9zAAFP7gABUE4AAVDTAAFRfwABUccAAVIyAAFTKwABU8UAAVRUAAFUtwABVSgAAVXkAAFWowABV08AAVfCAAFYbAABWMIAAVlqAAFaBgABWo4AAVrzAAFbTAABW50AAVvwAAFcMwABXLYAAV0T",
    "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",
    "AAI//gACQDwAAkCgAAJBCAACQYEAAkIqAAJCkgACQusAAkM6AAJDtgACRAgAAkRpAAJEvgACRQgAAkVyAAJFywACRfgAAkaUAAJHWwACR/YAAkiSAAJJAwACSZ0AAko+AAJKbQACS0sAAkvCAAJMLwACTKYAAk0z",
    "AAJNpgACTdUAAk5CAAJOpwACTxMAAk9UAAJP4gACUIgAAlESAAJRhAACUccAAlIKAAJSXQACUrIAAlLyAAJTRAACU7wAAlRJAAJUoQACVN8AAlVTAAJVkgACVf0AAlZhAAJW0QACV3oAAlfgAAJYcwACWOMAAllM",
    "AAJZqwACWnMAAlshAAJbXQACW9kAAlw4AAJcawACXLMAAl0OAAJdTAACXb4AAl4nAAJergACX0oAAl/dAAJgYgACYSkAAmGhAAJiAgACYmMAAmLXAAJjuQACY/MAAmRiAAJkrwACZTYAAmWRAAJmFwACZpsAAmbw",
    "AAJnYAACZ9IAAmhDAAJoxQACaSwAAmmEAAJqAgACaoIAAmqwAAJrPAACa6QAAmwNAAJsawACbLYAAm0wAAJtvQACbh8AAm7QAAJvcwACb8kAAnBYAAJwcgACcMIAAnFmAAJxtwACcf8AAnLLAAJzFQACc24AAnOq",
    "AAJz5AACdC8AAnRqAAJ0kAACdU8AAnWAAAJ2JAACdroAAnbmAAJ3EgACd2kAAnf9AAJ4VgACeK4AAnknAAJ5lQACelYAAnqHAAJ6/AACe2UAAnvLAAJ8BgACfG0AAnzmAAJ9kwACfhoAAn7NAAJ/YwACf+YAAoBM",
    "AAKAuAACgTEAAoGlAAKCbAACgsQAAoNlAAKDzgAChB0AAoTKAAKFFwAChWIAAoWyAAKGEgAChnYAAod7AAKH4QACiC8AAoh9AAKI0wACiR0AAoliAAKJ0wACipUAAor6AAKLhwACi9UAAowtAAKMfQACjREAAo1c",
    "AAKNnQACjeEAAo5wAAKO+gACj1IAAo/+AAKQkAACkNMAApEUAAKRrwACkhsAApKNAAKS1QACk1sAApQCAAKUxgAClRQAApVuAAKVzwAClg0AApaBAAKW4wAClz4AApeJAAKX4QACmCwAApiBAAKYxwACmTgAApmb",
    "AAKZ8gACmkQAApr9AAKbbQACnA0AApyFAAKdHwACnX8AAp3MAAKeQAACns0AAp9zAAKfpAACoDAAAqCbAAKg+gACoZ4AAqIcAAKiUgACoqcAAqMwAAKjcQACo7IAAqRHAAKkggACpLsAAqVRAAKlsgACpiYAAqZi",
    "AAKm0QACpzIAAqfGAAKoCAACqGEAAqiwAAKpMAACqYwAAqnfAAKqUAACqv4AAqs1AAKrcwACq8gAAqw+AAKseQACrMAAAq0HAAKtdgACrfwAAq5SAAKuxgACrywAAq90AAKvsgACsBEAArBpAAKwvwACsTUAArFz",
    "AAKxqAACsiwAArKRAAKy0wACsyMAArN4AAKzzAACtAoAArR9AAK0wQACtVYAArW2AAK2QAACtsIAArctAAK3iwACuAsAArhxAAK4rQACuQ0AArlLAAK5iQACug4AArpKAAK60gACu3kAArwKAAK8SwACvIYAAry9",
    "AAK9OAACvXwAAr3AAAK+KwACvoYAAr8eAAK/eAACwDAAAsCgAALA3gACwVQAAsHIAALCKQACwowAAsLFAALC/wACw08AAsOfAALD6wACxD4AAsSRAALE5AACxRYAAsVEAALFdgACxagAAsYXAALGiAACxv8AAsdH",
    "AALHlgACyLkAAsmTAALJ5AACyi0AAsqKAALLAwACy38AAsvvAALMVwACzL0AAs0wAALNgAACzkoAAs6yAALOsgACzxUAAs9vAALQmQAC0e4AAtJHAALSoAAC0wsAAtNaAALTvwAC0/kAAtQ3AALUcgAC1P0AAtVW",
    "AALV+wAC1sQAAtdjAALYCAAC2MMAAtkvAALaKgAC2uMAAttFAALbwgAC3E0AAty0AALdPQAC3ewAAt8qAALgFwAC4NEAAuFTAALhwgAC4jIAAuKyAALjSwAC47gAAuQuAALkigAC5YoAAuXVAALm1AAC54MAAuf4",
    "AALocwAC6SkAAunqAALqhAAC6uMAAutHAALsFAAC7dgAAu7SAALvtQAC8CYAAvCAAALwuwAC8RUAAvFCAALxhgAC8jAAAvLJAALzPwAC89oAAvR4AAL1BwAC9iIAAvadAAL3FQAC95wAAvhUAAL4rwAC+XoAAvns",
    "AAL6YAAC+v8AAvudAAL8CQAC/KMAAv1BAAL9rgAC/lcAAv/hAAMAyAADAYoAAwH9AAMCtAADAuMAAwOZAAMEAwADBJkAAwTcAAMFegADBaYAAwZKAAMHHgACAlgAAAWoBbgAAwAHAAABIREhNyERIQJYA1D8sGgC",
    "eP2IBbj6SGgE6AABAVAAWAawA8AAFgAAASEVIRMWFRQjIicBJjU0NwE2MzIVFAcCkAQg++CIICAYKP6oMDABWCgYICACQGj+8DgYICABODAwKDABOCAgGDgAAQBI/hgDuAYYABYAAAERIxEFBiMiNTQ3ATYzMhcB",
    "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",
    "EQYHJwAB4KBIYKBIUFABEAZ4MODY+rgEGHBgoAGQAAEAUP9IAtgGeAAKAAABFwYHESMRBgcnAAI4oFh4oGBoUAFYBngw6OD6yAQ4gHCgAZAAAgBoBJgHkAaIAA8AHwAAARcHIRUhFhcHJicjBgcnNiUXBgchFSEX",
    "ByYnIwYHJzYBuKAwAdD/AEA4kEBYgGCAgPADoJgQGAIo/sBIkDBAiFBoiMgGiDBYiEBAUGhogGBguNgwKDCIWFBQWHBYYKgAAgBoBJgHkAaIAA8AIAAAARcHIRUhFhcHJicjBgcnNiUXBgchFSEXByYnIxUGByc2",
    "AbigMAHQ/wBAOJBAWIBggIDwA6CYEBgCKP7AcIhIWJBYcIDYBogwWIhAQFBoaIBgYLjYMCgwiIBQaGgIgFBgsAADAID/mANYBngAGQAdACEAAAEWFwc0JwYFJzY3ESERIREzESERIRE2NyYnExEjESMRIxEC8Egg",
    "mAj4/tgYkHj/AAEAmAEI/vhAOBAgKHCYaAF4wNAoMDBQOJgYIAGoAwABaP6Y/QD+eBAYWFABSAHg/iAB4P4gAAQAkP+YArgF8AAHAAsADwATAAABESM1IxUjERMzESMRMxEjETMRIwK4mPiYmPj4+Pj4+AXw+gBI",
    "oAZY/kgBKP0gASj9IAEoAAQAoP+YAtAF8AAHAAsADwATAAABESM1IRUjERMhESERIREhESERIQLQmP74kJABCP74AQj++AEI/vgF8PnYcKAGWP5IASj9IAEo/SABKAAEAtj/SAewBjgAFAArAEAAVgAAASECBxYX",
    "BycGByc2NyYnNxYXNjchJSECBxYXByYnBwYGByc2Nyc3Fhc2NyEBIQIHFhcHJicGByc2NyYnNxc2NyElIQIHFhcHJicGByc2NyYnNxYXNjchA0ACCBhoSEBgeHiYSKBIaGhgYGAoIP6gAkAB6BhoYFBoUFBYGGBA",
    "SIhgyGBgYDAY/sD96AHAGFBYSFhISJDAUMhoWFhgkCAQ/vAB+AIQGKBYoGiIaFh4UHBYeCCQGEhQGP6gBjj+8LA4OHhwmFCAUGhQQGg4QFCIkP7gsEhYeFBIYCA4IIBIcJBoOEhgiP1A/vC4UFh4WEDgaIhoyFBA",
    "aHBgaJD+gPBwUHBAcGhIiEBouMAokIiYwAAEAxj/QAeoBmAABQA1ADoAQAAAARcEBScgBRYXITY3FwYHMxUhByEVIQYHIRUGBxYXByYnBgcnNjcmJwYHJxITIzUhNyE1MyYnARYXNjcBFhcHJicHKFD+cP24MAHg",
    "/uhgOAFIaDCoOGCo/dAYAnj9aBAYAkBIgJDIUOCowPhI4JhwUGCQgPBY+AEYEP8AoDBAAThQgHBA/vhIMHgoSAZgiFAYkLhwgKCoMJCIiJiQUECIyHhIMJhAcHg4mChYaIDIqGABKAFQkJiIWEj8mIhgWJAD0FBY",
    "SFhQAAECMP9IB5gGeAAWAAABFwYHIRUhESEVIREhFSERIxEjBgcnEgOgqCAwA6D9QAJA/cACWP2ooIBosHDwBngogHCY/siQ/siY/hgFgPjIgAEwAAIAYP9AAtgGeAAFABAAAAEXAgUnJBcXBgcRIxEGBycAAgiI",
    "mP7YYAEYyIhQiJhgSGABQAZ4SP7Y2IDY2EigqPwgA0BgOIABAAACAlj/mAeYBngABQAZAAABFhcHJicBIRUhESEVIREhFSE1IREhNSERIQS4eEiISHj+YATo/dgB4P4gAkj6wAJY/iAB4P3gBnhwiFCAcP7YmP4w",
    "kP4wmJgB0JAB0AAFAIgDWAd4BmAAEwAXABsAHwAjAAATIRUhFSERIzUhESMRIRUjESE1IRMhFSElIRUhFSEVISUhFSHgBkD9MAMooP14oP14oAMo/TCYAej+GAMgAfj+CAHw/hD82AHo/hgGYIhg/pDo/ogBeOAB",
    "aGD+yHh4eFCAeHgABQCIAwgHeAZYABMAFwAbAB8AIwAAEyEVIRUhESMRIREjESEVIxEhNSETIRUhJSEVIQUhFSElIRUh4AZA/TADKKD9eKD9eKADKP0wmAHo/hgDKAHo/hj80AHo/hgDKAHo/hgGWIh4/ngBAP44",
    "Acj4AYB4/qCAgIBgeHh4AAQC6P9IB6AGiAALAA8AFwAbAAABFwcSBQckAwIFJwADIRUhBREjNSEVIxETIREhBQigKPABMGj+4PDQ/uBQAXhgAnD9kAMIoP2woKACUP2wBogwUP7I2JjgATj+sNiYAUD+oJjY/PCI",
    "iAMQ/hABYAACApj/SAeoBngAGAAcAAABFwURIRUhESERIzUhFSMRIREhNSERBSckASERIQboSP5AAjj9yAHAoP0goAHA/cgCOP54QAIY/pAC4P0gBniIcP6wmP7Q/OBwcAMgATCYATBAoED6UAGIAAIASP9QA2gG",
    "eAAUABoAAAEzETY3FwYHFRQHFhcHJicCBycAEQMXAgMnNgGgkHhIeHjAEKiAaHB4YMCIAVDomBhgkFgGeP5ocHhguJDokJDYyJjYsP640GgBcAIQAdgg/qD++Fj4AAMDEP9IB1gGSAAHAAsAHgAAAREjNSEVIxET",
    "IREhEyERMxEhFSEUBwEHAwIHJwATIQdYmPzomJgDGPzoOAEAmAEQ/vAIATBw6GCocAEICP8ABkj5AHh4BwD6EAVY/rABEP7wmEhI/jCIAZD+6KBwAQgBmAADAFj/SAJgBmgABQALABEAAAEWFwcmJxMWFwcmJwEX",
    "AgMnEgEgsJBooKggoIhwiKABKIhguKDABmhgiIiYaP6AWHCIiFj+eGD+iP6gcAFQAAYCMP9IB6gGgAAKACUAKwAxADYAPAAAARcGByEVIQYHJzYXIQMzFSMGBzMVIwIjIicnFjMyNyE2NyM1MzYXITY1IQYlFhcH",
    "JicBEyEGBwEWFwcmJwNwqBggA3D8QGCQcNhIA8AQqLAIGLjAIOBQiBiYWEgQ/JgwILDIGIgCmAj9eAgBCGBQaFBgAcAg/WAYIAFIaFhgYGAGgChISJCogHjIwP4wkKigiP7oEIgQkNj4kODgqKCwiDhQeGBA/WgB",
    "SLCYAShAUHhgQAABADj/SANYBoAAHAAAEyERBgcnJCUXBREhFSEVFhcHJicRIxEGBycSEyFoATh4gDgBaAEoSP7wASD+4KB4aFhYmGCYcOBw/uAEYAEIIBiQQICIYP7IkCioqJCYePxwAyDwyIgBIAF4AAIB5//j",
    "AuUFtgADAAsANEAcAQADBpYCCgoMDS8AAQAAAhUEAQYEAQSbCKgCAwA/P+FdXRE5L10REgE5LzPhMjk5MTABIwMzAzIVFCMiNTQCpHkz33F/f38BngQY+0SLjIyLAAIBHQOmA7AFtgADAAcALkAcBM8HAaAHAU8H",
    "AQcAIAMwA5ADoAMEAwYBngcAAwA/Mu0yAS9dwS9dXV3BMTABAyMDIQMjAwIKKZspApMpmykFtv3wAhD98AIQAAIALQAABKAFtgAbAB8AuEBzHAgUCasKEg8OCwQKE6oUBAEAGQQYBaoGFh4dBwQGF6sYHxUKFEAC",
    "UAICEAoUBhgCAhgGFAoQBtAa8BoCfxqfGgIa4AzwDAIMCAQMrg0cAQ0fABCuERkVET8RTxF/EY8RnxEFPw1PDQINEQ0RBRcTAwoFEgA/Mz8zEjk5Ly9dXREzMxDhMjIRMzMQ4TIyAS9dL11dFzkvLy8vLy9dERI5",
    "ORDhERc5EOERFzkQ4REXORDhETk5MTABAzMVIQMjEyEDIxMjNTMTIzUhEzMDIRMzAzMVASETIQOoQPD+9lKUVP7eUpBO2fRB6QECUpNSASVUkFTd/RQBI0D+3QN9/riJ/lQBrP5UAayJAUiJAbD+UAGw/lCJ/rgB",
    "SAAFAAD/7gTNBccACwATABcAIwArAM+5ACL/4LMJDUgguP/gQA4JDUgcIAkNSBogCQ1ICrj/4LMJDUgIuP/gQCEJDUgEIAkNSAIgCQ1IZyqXKqcqAyq0G7UhFRYXFAAWARa4/8BAGhUYSA8UARRAFRhIFhQWFANo",
    "JpgmqCYDJrQhuP/AQC4VGEghLWgOmA6oDgMOtAm1ZxKXEqcSAxK0Ayi2HrckthgZFwYVGAy2ALcQtgYHAD/h9OE/Pz/h9OEBL+Fd9OFdENQr4V0SOTkvLytdK10RMxEzEPThXTEwKysrKysrKysBIiY1NDYzMhYV",
    "FAYnMjU0IyIVFAEBIwETIiY1NDYzMhYVFAYnMjU0IyIVFAEjg6CeiYGinYiLi40Dif0nngLZI4KhnomBop2Ii4uNAxC9oKS2uqCiu3fm4eHmAi/6SgW2+ji9n6S2uqChu3bm4eHmAAEBJ/68A6QFtgAJACdAFQYF",
    "BQABAQsD8B8IfwiPCAMIBvkA+AA/PwEvXeERMy8zMxEzMTABMwAREAEjABEQAuPB/j8Bv7/+RAW2/oj9+/33/owBYQIaAhQAAQEp/rwDpgW2AAkAJ0AVA/AQCHAIgAgDCAgLAAEBBgUG+AD5AD8/AS8zMxEzETMv",
    "XeExMAEjABEQATMAERAB6b4Bvv5AwAG9/rwBcwIKAgYBd/6X/er95AABAIUCdwRIBhQADgAkQBX0BwEHBQkHBAoDCwENAgwLCAYGAAAAPzIvMxc5ARkvXTEwAQMlFwUTBwMDJxMlNwUDAssrAY0b/oX2s7CdufL+",
    "iR0BhysGFP53b8Ec/rpgAWb+mmABRhzBbwGJAAEAmAEGBDMEogALAB9AEAkGqgDAA9ADAgMJAK0GA7MAPzPhMgEvXTPhMjEwASE1IREzESEVIREjAhv+fQGDlQGD/n2VAoeWAYX+e5b+fwABAbj+3wMSAQYABgA/",
    "QBkZBikG6Qb5BgQGmAGZcASABNAE4ATwBAUEuP/AQA8JDEgEBAcIA54fBi8GAgYAL13tERIBOS8rXf3hXTEwARcGAyMSNwMCEDmJmEwjAQYY4P7RAUPkAAEBHQHRA7ACeQADACBAEoACkAICAgIFIAAwAAIAALkB",
    "vQA/4QEvXREzL10xMAE1IRUBHQKTAdGoqAABAc//4QL+AS0ABwAdQA8ClzAGsAYCBgYICQCcBKgAP+0REgE5L13tMTABMhUUIyI1NAJmmJiXAS2mpqamAAEA0wAAA/gFtgADABxADAMAAAUBAgIEAwMBEgA/PxEB",
    "My8zETMvMjEwAQEjAQP4/Y2yAnMFtvpKBbYAAgCT/+wEOQXNAAkAFQA2QBINb9AIAQgXE28AAxADIAMDBwO4/8BADBUYSAMQcwUHCnMAGQA/4T/hAS8rXl3hEN5d4TEwBSICERAhMhIRECUyEhEQAiMiAhEQEgJk",
    "5ewB0ejt/iuTioqTkYeHFAGDAW4C8P59/pP9D5sBGQE9ATsBGf7p/sP+wv7oAAEA4QAAAvYFtgAKACtAFgkBCAgAbgABEAECBgEBDAsEBwkGABgAPz/NORESATkvXl3hMy8RMzEwISMRNDcGBwcnATMC9rAIJ1KT",
    "YQF/lgOReu8rRnl7ASsAAQCeAAAELQXLABcAVUAdkBegF7AXAxcXBm//EQERQA8TSBEZ1RblFvUWAxa4/+hAFwkMSBYMAAGwAQIBBgELCXMOBwIWdAEYAD/hMj/hMxI5AS9dMjIrXRDeK13hMy9dMTAhITUBNjY1",
    "NCYjIgcnNjMyFhUUBgcBFSEELfxxAV7DfH9soJ5mwObC4Hbo/ucCsJwBfdXRfnGDiXes1LN3+vr+1QgAAQCD/+wEHwXLACIAX0A6CxMbEwIAEBVvICADXxABEBAIDW+fA68DAgMkG88I3wjvCAMACAEIABBzaBEB",
    "ERELGhhzHQcLcwkGGQA/M+E/4TMSOS9d4TkBL11dMxDeXeEROS9dETMv4RI5MTBdARUEERQEISInNRYzIBEQISM1MzI2NTQmIyIHJzYzMhYVFAYCtgFp/uz++/KRuMcBYv6DhYWgsIhysqZcu/nO56QDAgYv/tPL",
    "6U+qYAEhAQKXmH1md3l9lsaliroAAgA9AAAEZgW+AAoAEgBWQBgHEAkPSAsHA24JAAJAEBNIAAIBAgITFBK4//BAGAsPSBIFQAoQSAUBBHQJBg4HCwsCBwYCGAA/PxI5LxI5MzPhMgEvKzMrERI5L10rMzPhMjIx",
    "MCsBIxEjESE1ATMRMyERNBMjBgcBBGbVsP1cApi81f57DQkkNv5lAUj+uAFInwPX/DABZLABAGZO/aAAAQCs/+wEHwW2ABgAUkAxDUALD0gNDQAFb58UrxQCFBoODw8LCQoKAACQAKAAsAAEAAkHcxERCwNzARcZ",
    "DnQLBgA/4T8z4RE5L+EzAS9dMy8zMzMRMxDeXeESOS8rMTA3NRYzIBEQISIHJxMhFSEDNjMyBBUUBCMirJDYAVD+qFmOWjcCsv3sJ2tm0gED/uz74DusYAE6ASYaOQKwpv5dFOXH6v8AAgCa/+wEMwXLABUAIQBP",
    "QBYBQAsPSAEBEhZuvwwBDCMGHG8AEgESuP/AQBYUGEgSBhl1fwkBCQkfA3MBFAcfcw8ZAD/hPzPhEjkvXeEyAS8rXeEyEN5d4RI5LysxMAEVJiMiAgMzNjMyFhUUAiMiABEQITITNCYjIgYVFBYzMjYDxUdf4OEK",
    "DF/Uw93xy9r+/QJ/aAKJf3+sooN/jwW4mxj+5v7Oqu7O5P75AVEBNANa/AyRnKJomN2wAAEAjwAABDsFtgAGAEdAMHkGiQYCRwZXBgIHBhcGJwYDBgAAAggBGAEoAQMBBQgAAtAC4ALwAgQCBQJ0AwYAGAA/P+Ey",
    "AS9dEM4yXRE5LzNdMTBdXSEBITUhFQEBTgIz/Q4DrP3VBRCmkfrbAAMAnP/sBDEFzQATAB4AKQB8QB8KHwwmbgIUAAIcbgwWbhIMEgwSCL8CAQIrIW4ACAEIuP/AtxQYSAjXFAEUuP/wQCIMD0gHFBcUAjkfWR9p",
    "H3kfBCofAR8KABQEIxlzDwcjcwUZAD/hP+ESFzldXV0rXQEvK13hEM5dETk5Ly8Q4RDhETk5EOEROTkxMAEEFRQGIyImNRAlJjU0NjMyFhUUBTY1NCYjIgYVFBYXBhUUITI2NTQmJwL8ATX8z9jyARrr6bK45P5m",
    "6H5uan1jbP4BFIiVfpcDBqDptdzPugEBiJLfob2+ouY3Z69lamplWn3Xeczwg3Vai0oAAgCa/+wEMwXLABUAIQBOuQAB/8BAFAsPSAEBDAYcb78SARIjFm4ADAEMuP/AQBMUGEgMBhl1CQkPA3UBFBkfcw8HAD/h",
    "PzPhETkv4TIBLytd4RDeXeEyEjkvKzEwBTUWMzISEyMGIyImNTQSMzIAERAhIgMUFjMyNjU0JiMiBgEIQ2Pg4QoMYNTC3fHL3AEB/YFpAYl/f6yghYCOApwZARoBMqrs0OQBCP6q/tH8pgPzkZyjZ5fergACAef/",
    "4wLlBGYABwAPAC1AGwoClg4wBmAGsAbgBvAGBQYGEBEImwyoBJsAEAA/7T/tERIBOS9dM+0yMTABMhUUIyI1NBMyFRQjIjU0AmZ/f39/f39/BGaLi4uL/JSLjIyLAAIBmv74AuwEZgAHAA4AREAuGQ4pDukO+Q4E",
    "DpgMmQkJApYwBmAGsAbgBvAGBQYGDxALnR8OLw4/DgMOBJsAEAA/7S9d7RESATkvXe0yL+3hXTEwATIVFCMiNTQTFwYDIzY3Am1/f3/XDjN9iT4mBGaLi4uL/IgXxf7m//cAAQCYAN0EMwTJAAYAYUA9ZwZ3BocG",
    "A2gEeASIBAN2BYYFAgUEAQQACAEBBwIBBQUDBuAAAd8AAUAAAT8AAQAAAQAABCADwAMCDwMBAwAvXV0zMy9dXV1dXTISOREzMxEBMy8QzjIREjldMTAAXV0lATUBFQEBBDP8ZQOb/TUCy90Bw2YBw6D+qv6qAAIA",
    "mAG6BDMD6QADAAcAQEAnBwIJBAABAQEBCAWtcAQBTwRfBG8EAwAEAQQEAK2PAQFQAQEPAQEBAC9dXV3hMy9dXV3hEQEzL10zEM4yMTATNSEVATUhFZgDm/xlA5sDVJWV/maWlgABAJgA3QQzBMkABgBfQDxoAngC",
    "iAIDZwB3AIcAA3kBiQECAQYECAIGBgcFBAEBAwDgBgHfBgFABgE/BgEABgEGBgIgA8ADAg8DAQMAL11dMzMvXV1dXV0zEjkRMzMRATMvMxDOETldMTAAXV0TAQE1ARUBmALK/TYDm/xlAX0BVgFWoP49Zv49AAIA",
    "qP/jBCMFywAZACEASkAqGQAAHJYgIA0HRxIjICMBAA0BDQcPLwABAAAPFRoBBhoBGpseqAwKUQ8EAD/hMz/hXV0ROS9dEjkBL11dEN7hETkv5TMRMzEwATU0Njc2NjU0JiMiByc2MzIWFRQGBwYGFRUHMhUUIyI1",
    "NAHRXHOCU5WErsVB0dnW+2uPdkJIf39/AZ4leJZSYXRkXHNamWHDpIWmbFdsWhKki4yMiwACAB//SgSuBbYALgA4AI9AWhY0ATTTBgAvGDgBONMOCx4OHAYB1A4BYA4BGQ4BBA4BBg4GDiQJEwET0io6BhkBGdIk",
    "ETbVAy0DMdUJPwNPA48DzwPfAwUwCUAJ0AkDAwkDCRwW1icDHNYeIQAvM+E/4RI5OS8vXV0Q4REzEOEyAS/hXRDW4V0ROTkvL11dXV1dETkzEOFdMjkQ4V0xMAEjBiMiJjU0NjMyFwMGFRUUMzIREAIjIgIREAAz",
    "MjcVBiMgABEQACEyABEUAiMiAyYjIgYVFDMyEwMfBEqceIzCnol3FgJIZN684v0BA++1pZ7C/tb+sQFOASD4ASmAcoBMNjFZX3+DDgGRtNGwzv0v/mAmHwewAX8BFgE8/oD+sf7I/qtOhVIBngFyAY0Bz/54/q3n",
    "/ukCthW7k/wBOAACACEAAASsBbwABwAOAKhACgIOAwgBALcGAQa4//hAYg4RSEcGASYGARcGAQYGAQa4BQEFCA4RSEgFASkFARgFAQkFAQULCwRYAAFIAAEqAAEJABkAAgAHBxBXAwFHAwElAwEGAxYDAgMEAl8L",
    "EBEUSAsQCw5IHQsBCwUODgUDBAASAD8yPzkvEjldKyvhAS8zXV1dXREzLzNdXV1dEjk9LzNdXV1dK10zXV1dXStdEjk5Ejk5MTAhAyEDIwEzAQEDJicGBwMD7JD+FZK+AePDAeX+e4UnFxQakAHF/jsFvPpEAmoB",
    "qHxmY1T+LQADAIcAAARxBbYADgAXAB4AUkAyE1sUByQHAgcEBA4cWwogDxlaAA4BAA4QDvAOAwgOBxhgnw8BaA8BDw8AGWAOEhdgAAMAP+E/4RE5L11d4TkBL15dceEyEN7hEjkvOV3hMTATISAWFRQGBxUEERQG",
    "IyETITI2NTQmIyERESEgETQhhwG4ARL3nYYBTP/c/fG7ARycj5mm/vgBMwE3/rwFtq/DgKoSCjb+4MbiA0puf3ho/Zf98AES/gABAIH/7AScBcsAFQAxQBwBQBQYSAEBBgsXEVsABvAGAgYMDl8JBAAUXwMTAD/h",
    "Mj/hMgEvXeEQzhE5LysxMCUVBiMgABEQACEyFwcmIyIAERASMzIEZJLU/sv+uAFmATbco06al9f/APDngsmiOwGIAWkBWgGUVpxO/sP+8f7h/tMAAgCHAAAEewW2AAgADwAsQBoNWwURCloAAAEAABAA8AADCAAJ",
    "YAEDCmAAEgA/4T/hAS9eXXHhEN7hMTAzESEgABEQACEDETMgERAhhwFWAT0BYf6S/qdyYAIU/hMFtv6G/q3+l/6ABRf7iQJDAjQAAQDZAAAEIwW2AAsAQEAlCAgBBABAEhZIAA0GClrwAQEAAQEBCV9oBgEGBgoF",
    "XwIDCl8BEgA/4T/hEjkvXeEBL11d4TIQzisyETkvMTAhIREhFSERIRUhESEEI/y2A0r9cAJp/ZcCkAW2pP48ov34AAEA9AAABD0FtgAJAFdAFggIAd8DAcADAQMLBgBaAAFAAVABAwG4/8BAIBUYSAEJX2gGAS8G",
    "XwbvBv8GBAZAEBVIBgYABV8CAwASAD8/4RI5LytdXeEBLytd4TIQzl1dETkvMDEhIxEhFSERIRUhAa66A0n9cQJp/ZcFtqT9/KQAAQB1/+wERgXLABgAP0AlAAcWWgwCGhJbAAcBBxhfLwBfAAIAQBAYSAAAFA9f",
    "DQoEFF8EEwA/4T8z4RI5Lytd4QEvXeEQ3jLhEjkxMAEhEQYjIAAREAAhMhcHJiMiAhEQITI3ESMCoAGmw+H++v7ZAUQBHMCaSJKGwNYBimFp7QME/TNLAY8BYgFfAY9WolT+yf7r/bQdAbQAAQCHAAAERgW2AAsA",
    "P0AmCQFaAA0IBFoQBSAFAiAFMAUCBQNfmAgBDwgvCAIGCAgKBgMFABIAPzI/MzkvXl1d4QEvXXHhMhDe4TIxMCEjESERIxEzESERMwRGu/23u7sCSbsCqv1WBbb9mAJoAAEA4QAAA+kFtgALAENAKAsICloFAtAD",
    "AaIDAZMDAQOOAwEEYwMBBRADUAMCAwkEYQYDAwphABIAP+EyP+EyAS9dX11fXV9dXV0zM+EyMjEwISE1JRElNSEVBREFA+n8+AEn/tkDCP7aASZ7FASYFHt7FPtoFAABAIn/7APTBbYADQArsgZaCbj/wEAUCQxI",
    "CQ8AAOAA8AADAANfAQwTBwMAPz8z4QEvXRDeK+ExMDc1FjMyNjURMxEUBCMiiaKTobq6/uft2SemPp+TA/X8Ddj/AAEA0wAABK4FtgAMAMm3Jgw2DEYMAwy4//BAiRAYSPgKAdkK6QoCyAoBuQoBqAoBiQoBCggM",
    "EEh5CQFYCQEZCQEKCQGIAQEBCBQYSAEIDA9I6AIBAhALFkhHAgECDAAIBFoABWAFcAWABQQFCxALC9AA8AACfwABAAAQAEAAYAAEABAApgi2CMYIA3cIhwgCJgg2CFYIZggEAwIIDAQFCgYDBQASAD8yPzMSFzld",
    "XV0BLzhdXV0zLzgvXeEyETk5XTEwACtdASsrXV1dXV0rXV1dXV1dK10hIwEHESMRMxE3ATMBBK7T/j6Murp5AcXR/fcCunL9uAW2/SWoAjP9gwABAOkAAAQfBbYABQAuQB8FQBIWSAUHA1oAAFAAYABwANAA4ADw",
    "AAcAAQMDXwASAD/hPwEvXeEQzisxMDMRMxEhFem7AnsFtvrwpgABAHEAAARcBbYAEwC2QAz3EwG2EwGXE6cTAhO4//BAJQ0RSCcTAQYTFhMC6Qv5CwILIA0WSDoLAQkLGQspCwPmCPYIAgi4/+BATQ0WSDUIAQYI",
    "FggmCAP4AAG5AAGYAKgAAgAQDRFIKAABCQAZAAIRDvrgDfANAg8NAQ0VAgX6AAYQBkAGUAYEBgsBBwMSAg5ZCQEJBgASAD8yMl0yLjM/MzMBL13hMhDeXV3hMjEwXV0rXV1dXV0rXV1dK11dXStdXV0hASMSFREj",
    "ETMTMxMzESMRNBMjAQIU/uoIEpf3+Ab6/JkOCP7lBQD+9oz8lgW2+1gEqPpKA3dmASH7AgABAIcAAAREBbYADwBzuQAJ//BAThAYSEUJVQllCQM0CQEVCSUJAgYJAQEQEBhISgFaAWoBAzsBARoBKgECCQEBAQ77",
    "DxEJBvsAB+AH8AcDBw5JAlkCAgIIA0YKVgoCCgcAEgA/MjJdPzNdMwEvXeEyEN7hMjEwXV1dXStdXV1dKyEjASMSFREjETMBMwI1ETMERNf9vAgSrNUCQgYOrgS6/uuM/OcFtvtMAS9lAyAAAgBU/+wEewXNAAkA",
    "EwAkQBQNWwcVElsfAi8CAgIQXwQECl8AEwA/4T/hAS9d4RDe4TEwBSARECEgABEQACcyEhEQAiMgERACaP3sAhYBAAER/uz/raGjqf6vFALzAu7+ef6X/pf+eKMBIgEsAS8BHf20/bIAAgCwAAAERgW2AAkAEQA4",
    "QCIOW+8G/wYCBhMKAVoAApACoAIDAgBgnwoBCgoBEWADAwESAD8/4RI5L13hAS9d4TIQ3l3hMTABESMRISARFAQhJzMyNjUQISMBaroBlAIC/uv++L+qxqv+rskCOf3HBbb+VNv2npCZARcAAgBU/mIEewXNAA8A",
    "GQBVuQAA//BAMA0RSAUACRNbDmwDfAOMAwMDGAsOSAMCAg4bGFsfCS8JAgkWXwsEEF8HBQcDAwAHEwA/MzMvETMQ4T/hAS9d4RDOMi8zK10Q4RI5OTEwKyUWFwcmJwYjIBEQISAAERAFMhIREAIjIBEQA15Vwnns",
    "XCQo/ewCFgEAARH97a2ho6n+rye0g46r5QYC8wLu/nn+l/3yQAEiASwBLwEd/bT9sgACALoAAASTBbYACwAUAHNASysOARoOAQsIEBhIKQsBGAsBCggSGEgpCgEICgEKCRAJCUYIAQsIARBbBkATFkgGFgwBWgAC",
    "gAKQAqACBAIIAwBgDAwBFGADAwoBEgA/Mz/hEjkv4RE5AS9d4TIQ3ivhEjk5XTMvODMxMF1dK11dK11dAREjESEgERAFASMBJzMyNjU0JiMjAXW7AWUCCP7fAY3b/qLlpKuioLKfAlz9pAW2/mH+4Wn9cQJcnoSQ",
    "jXwAAQCN/+wEPwXLAB8AOEAfEBAFWrAbwBsCGyEVWgsAAAALAQsVBQ4DYB4TE18OBAA/4T/hEjk5AS9dMy8Q4RDeXeEzLzEwNzUWMyA1NCYnJiY1NCQzMhcHJiMgFRQWFxYWFRQEIyCN08sBXo3X0LUBAeDlu0DB",
    "p/7bg832pf7r//73MbJW8GhwTUnLoq7FTqRO0WZ8R1i7k8DbAAEAZgAABGQFtgAHADxAJAYGAFoD0AEBogEBkwEBA44BAQRjAQEFEAFQAQIBBwNfBAMAEgA/P+EyAS9dX11fXV9dXV3G8cIvMTAhIxEhNSEVIQLD",
    "u/5eA/7+XwUSpKQAAQB9/+wEUAW4AA4AJ0AWDVrgAfABAgEQCVoABgEGC18EEwcAAwA/Mj/hAS9d4RDeXeExMAEREAIjIBERMxEQISATEQRQ/PT+HboBMwEnBQW4/Ez+/P7sAhwDrvxc/n0BhQOkAAEAIQAABKwF",
    "tgAKAJlAGGcFAbgDAQMIDRFIKQMBGAMBCQMBtwIBArj/+EA7DRFIJgIBFwIBBgIBaAAB6AMBA+cCAQIICARIAFgAAioAAQkAGQACAAEBDEcFVwUCJQUBBgUWBQIFBAi4//BADgsYSBIIAQgDAQQDAgMSAD8zPzMS",
    "OV0rAS8zXV1dETMvM11dXRI5PS8zXTNdMTBdXV1dK11dXV0rXV0BMwEjATMBFhc2NwPlx/4Xu/4ZxAEnKS8fPgW2+koFtvxhf8+RwwABAAIAAATLBbYAGQFjQFQpGTkZAggZGBkCJxUBFRUBBhUBBxQXFCcUAyYQ",
    "NhACKQo5CgIoBgEZBgEIBgEmAjYCAgcCFwICSBFoEagRuBEEKRE5EQIR5xD3EALGENYQArQQARC4//BAIQ8TSFQQAUUQARAX5gEBxwHXAQKlAbUBApYBAXcBhwECAbj/8ECMCQ9IAekAAcgA2AACqgC6AAKZAAF4",
    "AIgAAgAQCQ9IAA3oCvgKAskK2QoCuwoBiAqoCgJpCnkKAlsKAUoKAQpnCacJtwkDJgk2CUYJAwkEJBc0F5QXpBcEBAQUBGQExATUBAUXDQQEDRcDEigHAQcQCAEICBsnEwETEgQXSw1bDQINFxEAAAcKERISBwMA",
    "PzM/MxI5LxI5OV0RMwEvM10RMy9dM10SFzk9Ly8vXV0RM11dM11dXV1dXV0RMytdXV1dXTMrXV1dXV0RM11dK11dXTNdXTEwXV1dXV1dXV1dXV1dXQEzExYXNhMTMwMjAyYnBgcDIwMzExYSFTY3AhCxkT0LAj9G",
    "qru+qCgaICGcvsuqWBciGC4D8P3321g1AjYCl/pKAkSKkK1v/b4Ftv1psP5sJ5ehAAEANQAABJYFtgALAL5AJAgICQsLCgAHAAUFBAICAwEGAQgIBwUFBgQJBAsLAAICAQMKB7j/+EAXDA9IBgcWByYHAwkIDA9I",
    "CQkZCSkJAwO4//hAPAwPSAYDFgMmAwMBCAwPSAkBGQEpAQMLCAIFBAQJCgEKrwABAAANBwYDBgQCBQsIBAcJCgMGAwEDBAMAEgA/FzI/FzMXOQEvMzMvMxEzL10yMi8zERc5XStdK10rXSsxMIcIwAjAEIcIwAjA",
    "EIcIwAjAEIcIwAjAISMBASMBATMBATMBBJbT/p3+kr0Bxf5axwFLAU6//loCe/2FAvwCuv3RAi/9TAABACEAAASqBbYACAC1uQAI//hAJA0QSCYINggCFwgBaAF4AQJaAQFIAQEpATkBAhgBAScAtwACALj/+LMN",
    "EUgIuP/4QEoUGEgIrwf/BwJZBwEHBQEIFBhIAeAC8AICewIBUAIBAgIABFrQBQGiBQGTBQEDjgUBBGMFAQUQBVAFAgUGBjQAAQADAwEEEgcBAwA/Mz8SOS8zXTMvAS9dX11fXV9dXV3xOcIvXV1dMisQxl1dMisx",
    "MAArXQFdXV1dXV1dKwEBMwERIxEBMwJkAX3J/hm7/hnLAtMC4/yD/ccCLwOHAAEAZgAABGQFtgAJAERAKCYIAQcIFwgCKQMBCAMYAwIDBwcAAAEAAAsIAgQEAgcEXwUDAghfARIAP+EyP+EyAS8zLxEzETMvXTMv",
    "MzEwXV1dXSEhNQEhNSEVASEEZPwCAxn8/APV/OcDLZEEf6aR+4EAAQGc/rwDrAW2AAcAM0AgBAAAAQAACQbxfwGPAb8BzwHfAQUAAQEBBfUC+Ab1AfkAP+E/4QEvXV3hETMvXTMxMAEhESEVIREhA6z98AIQ/qYB",
    "Wv68BvqV+jEAAQDTAAAD+AW2AAMAHEAMAgEBBQADAwQCEgADAD8/EQEzLzMRMy8zMTABASMBAYUCc7L9jQW2+koFtgABASH+vAMxBbYABwA0twHxcAaABgIGuP/AQBUUGEgGBgkD4ADwAAIAAfUG+QL1BfgAP+E/",
    "4QEvXTMRMy8rXeExMAUhESE1IREhASEBWv6mAhD98K4Fz5X5BgAB//D+vATb/0gAAwAStgAABQEBugIAL+EBLxEzLzEwASE1IQTb+xUE6/68jAABAaIE2QMrBiEABwAfQBAFhwSGAQAACQWSDwFfAQIBAC9d7REB",
    "My8z/eExMAEjJic1MxYXAyt5pmrbVlgE2Y6lFbJ7AAIAh//sBAIEXgAXACEAQkAmCwEhR48XnxcCFyMcSBEACBAIAggIGFILCx4QDlATEAEeTgUWABUAPz/hMj/hMxI5L+EBL15dM+EQ3l3hMjIxMCEnIwYGIyIm",
    "NRAlNzU0IyIHJzYzMhYVEQMHBgYVFDMyNjUDfyUITaKAo7kB/sv0k7U/xLvjy7SixKTIk6+YYUusmwFMEAdF7FKJYK7A/RACGQcIa26yo5QAAgCe/+wERAYUABIAHAA6QCIYSO8O/w4CDh4BCAYTRwADsAMCAwEW",
    "UBEWCBpQCxAEAAMVAD8/P+EyP+EyAS9d4TIyORDeXeExMCUjByMRMxEUBzM2MzISERACIyIDFBYzIBEQISIGAVQMJYW2CAhr18nl5sjPc4uYARD+7puGi4sGFP6IUZGk/tX+9P7y/tMCO+PBAaYBnrwAAQCs/+wE",
    "JQReABMAK0AXAACPCQEJFQVIAA8BDwNRARIQCQdRDBYAP+EzPzPhAS9d4RDOXTIvMTABByYjIBEQITI3FQYjIAAREAAhMgQlPpZ2/o0BaZ2khsP+//7kASIBB7IEI545/mP+aj6gPQEjARABGQEmAAIAif/sBC8G",
    "FAASAB0AOkAjFAAOR5ARoBECER8ZSAAG4AbwBgMGDwALF1AJEAEbUAMWEhUAPz/hMj/hMj8BL13hEN5d4TIyMTAlIwYjIgIREBIzMhczJjURMxEjAzU0JiMgERAhMjYDgQhx0cnl5sjOdAwMtpMji5j+8AESmIWT",
    "pwErAQwBDgEtoIEhAbT57AH6KePB/lr+YrEAAgCF/+wESAReABEAFgBHQCwTSAUPAB8AAgAYEgFIAAsQCwIQCyALAgsBUA8SHxICBxISAxVQDhADUQUIFgA/M+E/4RI5L15d4QEvXXHhMhDecTLhMTABIRIhMjcV",
    "BiMiABEQADMyEhUlIRAhIARI/PoIAVDDr6bG9f7aAQ/j1P38/gI9/vD+7QIC/olMoEsBKwEGAQoBN/703yMBMQABAJwAAARaBh8AFQBGQCgAAA0NFxQCRwMHA48F7wUCBQUAA7AD8AMDAwQBTgcGFA8QUA4LAQIV",
    "AD8/M+E/MzPhMgEvXTMvXREzEOEyETMvOS8xMAEhESMRITUlNTQ2MzIXByYjIgYVFSEEFP57tv7DAT200YF7KWhne1gBhQPB/D8DwW4hYMGuI48cZHNoAAMAZv4UBGYEXgAkACwANgCAQC80ERECJAkcBB8nRgFf",
    "BN8E7wT/BAQEOAsaGh8wPxZPFl8WAxYWK0aAH5AfoB8DH7j/wEAdBglIHxwEIiVSBwcuKU8iGC5RDQ0iEDJOExsCAA8APzI/4T85L+EyEOEROS/hEjk5AS8rXeEzL13BETMvwRDeXTLhEhc5My/BMTABFQcWFRQG",
    "IyInBhUUMzMyFhUQISImNTQ3JjU0NyYmNTQ2MzIXAzI1NCMiFRQBIyIVFCEgNTQmBGbEQdW+Nx9kobuuuP3L2uPwYIVZZtXFVkCa3+HhAUW85gEPAYtkBEpxG1WAob8GOE1Umo/+h6GR1Dova3BQJatltsUU/bzm",
    "7/Lj/gzGrt9YPQABAKAAAAQtBhQAEQA8QCYkDzQPAgBHsBHAEQIREwoGRwAHEAcgB9AHBAcHBANQDhAIAAcAFQA/Mj8/4TIBL15d4TIQ3l3hMTBdIREQIyARESMRMxEHMzYzIBERA3fu/s22tggKZ+kBhQLDAQT+",
    "cv3HBhT+MpCo/m/9MwACAMUAAAQzBg4ACAASADNAHA4CDUcHChEDVhIBEhIUEw0SThAVCU4LDwVTAAAAP+0/4T/hMhESATkvXRcz4TIyMTABMhUUBiMiNTQTJTUhEQUVITUlAnlqPytrD/7zAcMBYPySAVgGDnI6",
    "OXNy/awVe/xFFHt7FAACAIf+FANWBg4ABwAXADlAIBAIBg5HApAToBMCExMZGAAIAQgLUAkWGw9OEg8EUwAAAD/lP+E/M+EBL10REjkvXTPhMhE5MTABMhUUIyI1NAE1FjMyNjURJTUhERQGIyIC52trav4Khpt1",
    "g/5cAlrizqQGDnJzc3L4KZoncmUEORV7+0G0wwABANcAAASLBhQADgB2QAsZBikGOQYDCAYBBLj/4EA+EBRIRgRWBAIJAgEJAQEbBysHOwcDBAcCAwMGBSAQE0gABWAFAgUFEAwACUcACmAKAgoLAAQHAAcCCgUV",
    "Ag8APz8zEjk5ETM/AS9d4TIyETMvXSszMy8zOTkxMABdAV1dXStdXQE3ATMBASMBBxEjETMRAwF/hwGL3v4SAgrV/laBtLQQAimYAYn+Jf2RAfhS/loGFP02/t8AAQC8AAAEKwYUAAkALUAYBQRHCAFdCQFPCQEJ",
    "CQsKCQROBhUATgIAAD/hP+EyERIBOS9dXTMz4TIxMAElNSERBRUhNSUCFP70AcMBYPyRAVgFhRV6+nsUe3sUAAEAXAAABHMEXgAgAGtARRmFCAF2CAFlCAFWCAE3CEcIAghHiwkBegkBCQkRAEeQIKAgwCDQIAQP",
    "IAEgIhQQR0ARUBECERoUEQQMUBwXEBIPEQkAFQA/MjI/PzPhMhI5OQEvXeEyEN5dXeEROS9dXeFdXV1dXTIxMCERNCYjIgYVESMRECMiBhURIxEzFzM2MzIXMzYzMhYVEQPRNT5XT6F9VEiifxsKQ4ajMgZMj4B0",
    "AsOScqbD/aICwwEEn+/9xwRKlKi2trnY/TMAAQCgAAAELQReABAANkAhAEewEMAQAhASCgZHAAcQByAH0AcEBwcLA1ANEAgPBwAVAD8yPz/hMgEvXl3hMhDeXeExMCERECMgEREjETMXMzYzIBERA3fu/s22kxsK",
    "Z+kBhQLDAQT+cv3HBEqUqP5v/TMAAgBz/+wEWAReAAsAEwAiQBIOSAkVEkgAAwEDEFAGEAxQABYAP+E/4QEvXeEQ3uExMAUiABEQADMyABEQACcgERAhIBEQAmLY/ukBD+baARb+7uABNv7I/ssUATcBBAEHATD+",
    "yv7//vf+zpcBpAGg/mD+XAACAJ7+FAREBF4AEgAdAD5AJhlIDw4fDgIOHxQBBEcABRAFIAXQBQQHBQAXUBEWCBtQCxAGDwQbAD8/P+EyP+EyAS9eXeEyMhDeceExMCUjFhURIxEzFzM2MzISERACIyIDFRQWMyAR",
    "ECEiBgFUDAy2kxsIbtTJ5ebIz3OLmAEQ/u6YhYuBIf4rBjaUqP7V/vT+8v7TAmQp48EBpgGesAACAIn+FAQvBF4AEgAdADxAJQEIEwMFR5AEoAQCBB8ZSAAO4A7wDgMOCBtQCxYEGwEXUBEQAg8APz/hMj8/4TIB",
    "L13hEN5d4RcyMTABMzczESMRNDcjBiMiAhEQEjMyEzU0JiMgERAhMjYDeQgbk7YMDHHRyeXmyM9zi5j+8AESmIUDtpT5ygHVKYGnASsBDAEOAS39nCnjwf5a/mKxAAEBCAAABCMEXgAQADFAG5AAAQAAEgsHRy8I",
    "AQAIAQgLBwNRAQ8QCQ8HFQA/Pz8z4RI5AS9dXeEyETMvXTEwAQcmIyIGFREjETMXMzY2MzIEIzF7ZaOxtpQWCEyuf3YEMaYtua/9sARKyXdmAAEAy//sBAIEXgAfADxAIhAQBUYbIRVGCwAAAAtQC2AL8AsECxUF",
    "DgNQAR4WE1ARDhAAPzPhPzPhEjk5AS9dMy8Q4RDe4TMvMTA3NRYzIDU0JicmJjU0NjMyFwcmIyIVFBYXFhYVFAYjIsvBsQETYrHped/Fxqs8tonsZbbTi+rW+DGmVqI5VEBXkWOIm0qVSIU9SUFNlWyWqwABAIv/",
    "7AQCBW8AEwBZQDcMEEcFCQUgBwEHBy8FPwV/BY8FzwXfBQYABQEFBRQVDg5/AY8BrwEDARUGD04LCQgMDxJQAAMWAD8z4T8zMzPhMgEQzl0yLxESOS9dXTMvXREzEOEyMTAlFQYjIBERITUlEzMRIRUhERQzMgP8",
    "gnr+lv71AQtNaQG2/krAXZaKIAFYAn1eMQEf/tuJ/YPDAAEAoP/sBC0ESgARADBAHAEOR5ARoBECERMJRwAGsAYCBg8HDwELUAQWABUAPz/hMj8zAS9d4RDeXeEyMTAhJyMGIyARETMREDMyNjURMxEDmhsKaeX+",
    "ebbsoZS2k6cBkQLN/T3+/LnUAjr7tgABAFIAAAR5BEoACwBzQDgmCwEpAAE3C2cL5wv3CwQGCxYLAgs4AGgA6AD4AAQJABkAAgAFBQEJCAkMSAkQCiAKMAoDCgoNArj/+EAVCQxIAi8BPwECAUYFVgUCBQkBDwAV",
    "AD8/MzldAS9dMysRMy9dMysSOT0vM11dM11dMTBdXSEBMxMWFzM2ExMzAQHy/mC88FUPBgde773+YARK/XTnXiwBGQKM+7YAAf/8AAAE0QRKABkBK7kAGf/wthQYSKcZARm4//BAGA0SSAkWGRYpFgMpFQEnEVcR",
    "AgYRFhECELj/8EBCDRhIJxA3EAIPEA0YSCgPOA8CKA5YDgIJDhkOAigNASYKAQYJFgkmCQMGEBQYSKgGAXkGiQaZBgMoBkgGWAZoBgQFuP/wQAoUGEinBQEmBQEFuP/wQCoNEkgHBQEAEBQYSKgAASkAAQAQDRJI",
    "CAABBgULEA8CGQAUlAukC7QLAwu4/+BAMAsOSJsUqxS7FAMUIAsOSAsCFBQCCwMHFxAYARgIBxQLWwIBVAsBAgsGFw8HDwAGFQA/Mz8zMxI5OV1dETMBLzMvXTMSFzk9Ly8vK10rXREzMxEzMxEzMzEwXStdXStd",
    "K11dK11dXStdXV1dXV0rXStdXV1dK10rIQMDIwMDIwMzExYXMzY3EzMTFhczNjcTMwMDLYNEBkGHvd+iYiIXBh8lhcF/KxgGHx1mnuECVAFK/rL9sARK/eG6z7mtAkL9vsOj8pcCH/u2AAEAYAAABGoESgALAKm3",
    "xArUCuQKAwq4//BAJAsOSMsI2wjrCAMIEAsOSMsE2wTrBAMEEAsOSMQC1ALkAgMGArj/8EAUCw5ISQkBCRASF0gKCRoJAkYDAQO4//BALRIXSAUDFQMCBAUFBgMJAAQLCAAHEAcCBwcNAgEKHwsBCwkGAAMEAQsH",
    "FQQBDwA/Mz8zEhc5AS9dMzMyETMvXTMSFzkzETMxMABdK11dK10BK19dK10rXStdAQEzAQEzAQEjAQEjAf7+d88BIgEjz/51AZ3O/sr+yc8CMwIX/mYBmv3p/c0BtP5MAAEAUv4UBHkESgAWAHFAHjgIAQkIGQgp",
    "CAM3AQEGARYBJgEDFhAJDEgWBAQICbj/wEASCQxICQkYDw8BHwAvAD8AAwAEuP/wQBQLDkgEBBQEAgQAFhYSUBANGwgADwA/Mj8z4T8SOV0rAS9dMjIvETMvKzM5PS8zKzEwXV1dXRMzARYXMzY3EzMBBgYjIic1",
    "FjMyNjc3UrwBBlIHBhdD773+JUOynVZSPkpgayo6BEr9cs1VcLQCjPsnrq8RkQxSZJYAAQC2AAAEFARKAAkARkAOAwgJDEgDBwdwAAEACwi4//hAGAkMSAgCBAR/AgEAAgECBwROBQ8CCE4BFQA/4TI/4TIBL11d",
    "My8RMysQzl0yLzMrMTAhITUBITUhFQEhBBT8ogKU/Y0DK/15Apl9A0SJkvzRAAEA4f68A+kFtgAZAGJAPxQA8QwWCXAGgAYCBgYJEF8DAUADAQMb4AnwCQIfCQEJFgn17wr/CgLZCgEPCi8Krwq/CgQKCgMQ9Q/4",
    "A/UE+QA/4T/hEjkvXV1d4TkBL11dEM5dXTIROS9dEjkz4TIxMAUUFhcVJBERNCE1IDURECUVBgYVERQHFRYVAulwkP5K/q4BUgG2kHDp6RBRSwKWBgEfAU69m70BTQEfBpUCS1H+tM8pDCnPAAECG/4UArAGFAAD",
    "ABVACgKqTwMBAwIbAAAAPz8BL13hMTABMxEjAhuVlQYU+AAAAQDj/rwD7AW2ABkAYEA+BRnxDQN/E48TAhMTCe8P/w8CEA8BDxsVUAkBTwkBCQMQ9e8P/w8C2Q8BDw8vD68Pvw8EDw8KFvUV+Qn1CvgAP+E/4RE5",
    "L11dXeE5AS9dXTMQzl1dETkvXTkz4TIxMAE0NzUmNRE0Jic1BBERFCEVIBUREAU1NjY1AePq6nGPAbcBUv6u/kmPcQE7zykMKc8BTFFMAZUG/uH+s72bvf6y/uEGlgFMUQABAJgCSgQzA1oAEQAvQBoJEwAAAQAA",
    "EhCtCQOyB60A3wwBcAwBPwwBDAAvXV1dM+H9MuERATMvXRDOMTATNTYzMhcWMzI3FQYjIicmIyKYY5RklIJHbHdjlWSTg0ZsAkqibD84eaJsPzgAAQFcAqADbwXFABUATUAzFRUG4A8QHxBPEF8QfxCPEJ8QBxAQ",
    "FAsLAAFgAXABgAEEAQYBChARGEgKCOQN3gIU5AHdAD/hMj/hMysSOQEvXTIvMjIvXeEzLzEwASE1NzY2NTQjIgcnNjMyFhUUBgcHIQNv/e27bz1vUVNOdYN2gkaBhwFrAqBmx3ZlOXNMVmd4aEKIgYgAAQHnAkgC",
    "5QNeAAcAIkAUApYwBmAGsAbgBvAGBQYGCAkAmwQAL+0REgE5L13tMTABMhUUIyI1NAJmf39/A16Li4uLAAEAvgEtBA4EewALAFy5AAb/8LMPFkgGuP/4QBgKDkgAEA8WSAAICg5ICRAPFkgJCAoOSAO4//CzDxZI",
    "A7j/+EAUCg5IgAPAA9AD8AMEHwMBA98AAQAAGS9dAS9dXTEwACsrKysBKysrKwEBNwEBFwEBBwEBJwH8/sJpAT0BQmj+vwE/Zv6+/sNmAtMBP2n+wgE+Z/6//sBmAT3+xWcAAf/6AdEE0wJ5AAMAE7cCAgUAALkB",
    "vQA/4QEvETMvMTADNSEVBgTZAdGoqAADAE7/4wR/APoABwAPABcAX0A9NBIBJRIBBhIWEgISlhYWDjQCASUCAQYCFgICApYGBjQKASUKAQYKFgoCCpbgDvAOAg4OGBkQAAibFAQMqAA/MzPhMjIREgE5L13hXV1d",
    "My/hXV1dETMv4V1dXTEwNzIVFCMiNTQhMhUUIyI1NCEyFRQjIjU0zX9/fwIYf39/Ahl/f3/6i4yMi4uMjIuLjIyLAAMARgGRBIUEDgATAB0AJwBfuQAQ/+CzCQxIDrj/4EAyCQxIBiAJDEgEIAkMSB4KABQEBSOr",
    "Dw8BDykZqwUmFq4KAAIMCAggHK4SPwKPAt8CAwIAL10z4TIzLzMSOTnhMgEv4RDeXeERFzkxMCsrKysBBiMiJjU0NjMyFzYzMhYVFAYjIgMmIyIGFRQWMzI3FjMyNjU0JiMiAmJ2mneVlXembHSldpKXcau1Um1B",
    "UFBDaORWa0FQVEBnAm3Vro2GtdvVrI+DuQFCuGtPUWWyuW1OT2cAAAAAAA8AugADAAEECQAAARYAAAADAAEECQABADABFgADAAEECQACAA4BRgADAAEECQADACoBVAADAAEECQAEADABFgADAAEECQAFACQBfgAD",
    "AAEECQAGACoBogADAAEECQAHAJwBzAADAAEECQAIACgCaAADAAEECQAKAOACkAADAAEECQALADgDcAADAAEECQAMAFwDqAADAAEECQANAFwEBAADAAEECQAOAFQEYAADAAEECQASACYEtABEAGkAZwBpAHQAaQB6",
    "AGUAZAAgAGQAYQB0AGEAIABjAG8AcAB5AHIAaQBnAGgAdAAgAKkAIAAyADAAMAA3ACwAIABHAG8AbwBnAGwAZQAgAEMAbwByAHAAbwByAGEAdABpAG8AbgAuAAoAQwBvAHAAeQByAGkAZwBoAHQAIACpACAAMgAw",
    "ADAAOAAtADIAMAAwADkAIABXAGUAbgBRAHUAYQBuAFkAaQAgAEIAbwBhAHIAZAAgAG8AZgAgAFQAcgB1AHMAdABlAGUAcwAgACgAaAB0AHQAcAA6AC8ALwB3AGUAbgBxAC4AbwByAGcALwApACAAYQBuAGQAIABR",
    "AGkAYQBuAHEAaQBhAG4AIABGAGEAbgBnAFcAZQBuAFEAdQBhAG4AWQBpACAATQBpAGMAcgBvACAASABlAGkAIABNAG8AbgBvAFIAZQBnAHUAbABhAHIAVwBlAG4AUQB1AGEAbgBZAGkAIAAtACAATQBpAGMAcgBv",
    "ACAASABlAGkAVgBlAHIAcwBpAG8AbgAgADAALgAyAC4AMAAtAGIAZQB0AGEAVwBlAG4AUQB1AGEAbgBZAGkATQBpAGMAcgBvAEgAZQBpAE0AbwBuAG8ARAByAG8AaQBkACAAaQBzACAAYQAgAHQAcgBhAGQAZQBt",
    "AGEAcgBrACAAbwBmACAARwBvAG8AZwBsAGUAIABhAG4AZAAgAG0AYQB5ACAAYgBlACAAcgBlAGcAaQBzAHQAZQByAGUAZAAgAGkAbgAgAGMAZQByAHQAYQBpAG4AIABqAHUAcgBpAHMAZABpAGMAdABpAG8AbgBz",
    "AC4AQQBzAGMAZQBuAGQAZQByACAAQwBvAHIAcABvAHIAYQB0AGkAbwBuAFcAZQBuAFEAdQBhAG4AWQBpACAATQBpAGMAcgBvACAASABlAGkAIABpAHMAIABhACAAaAB1AG0AYQBuAGkAcwB0ACAAcwBhAG4AcwAg",
    "AHMAZQByAGkAZgAgAHQAeQBwAGUAZgBhAGMAZQAgAGQAZQBzAGkAZwBuAGUAZAAgAGYAbwByACAAdQBzAGUAcgAgAGkAbgB0AGUAcgBmAGEAYwBlAHMAIABhAG4AZAAgAGUAbABlAGMAdAByAG8AbgBpAGMAIABj",
    "AG8AbQBtAHUAbgBpAGMAYQB0AGkAbwBuAC4AaAB0AHQAcAA6AC8ALwB3AHcAdwAuAGEAcwBjAGUAbgBkAGUAcgBjAG8AcgBwAC4AYwBvAG0ALwBoAHQAdABwADoALwAvAHcAdwB3AC4AYQBzAGMAZQBuAGQAZQBy",
    "AGMAbwByAHAALgBjAG8AbQAvAHQAeQBwAGUAZABlAHMAaQBnAG4AZQByAHMALgBoAHQAbQBsAEwAaQBjAGUAbgBzAGUAZAAgAHUAbgBkAGUAcgAgAHQAaABlACAAQQBwAGEAYwBoAGUAIABMAGkAYwBlAG4AcwBl",
    "ACwAIABWAGUAcgBzAGkAbwBuACAAMgAuADAAaAB0AHQAcAA6AC8ALwB3AHcAdwAuAGEAcABhAGMAaABlAC4AbwByAGcALwBsAGkAYwBlAG4AcwBlAHMALwBMAEkAQwBFAE4AUwBFAC0AMgAuADAAVwBlAG4AUQB1",
    "AGEAbgBZAGkAIABNAGkAYwByAG8AIABIAGUAaQADAAAAAAAA/wAAZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAFAAL//wADAAEAAAAMAAAAAAAAAAIACAAAAMcAAQDJAP0AAQD/AWEAAQFjAWkAAQFrApoAAQKc",
    "A5IAAQOUBGcAAQh3CNcAAQABAAAACgAMAA4AAAAAAAAAAQAAAAoAFgAYAAFsYXRuAAgAAAAAAAAAAAAAAAEQAAVa94kAAAgA/0j56A4YAAAAAQAAAAAAAAAAAAAAAAABCAAFuAPABhgDwAYYBggGCAYIBggGCAYI",
    "BggE4ASwBFAEsATYBLgGAAYABkgAAAEwATgGYAZgBmAC4AZgBmADgAYIBeAGWAYIBhgGeAZ4BjAGYAYYBjgGeAaABngGeAZwBogGaAZQBngGYAYQBngGeAYABngGeAYQBogGeAWQBgAGCAYIBngGgAZoBoAGUAZ4",
    "BngGeAaABngGgAaABngGeAaABngGeAZ4BngGeAZ4BngGiAaABngGeAZ4BngGgAZ4BngGeAZ4BoAGeAZ4BoAGeAZ4BngGeAZ4BngGiAaABngGiAZ4BngGeAaABngGiAZ4BngGeAaABoAGeAX4BngGeAaABngGeAaI",
    "BlgGcAaABnAGQAaIBogGgAZgBiAGMAZ4BngGQAZ4BngGiAaABoAGeAYQBkAGeAZ4BigGGAYQBnAGeAZwBngGeAaABnAGeAZwBngGeAZwBngGgAaQBnAGeAaABogGcAZ4BngGeAaIBngGeAZ4BogGeAY4BngGUAZ4",
    "BoAGiAZ4BngGeAaABgAGeAZ4BjgGOAY4BjgGeAaABhAGMAYQBngGcAY4BngGeAZgBeAGeAYIBngGGAYIBoAGeAYwBoAGiAaQBjgGeAZoBoAGOAaABmgGgAYwBkAGSAZABpAGgAYoBogGkAZYBigGgAaABoAGgAZ4",
    "BngGQAaIBjgGOAYIBjgGOAY4BjgGOAY4BjgGIAaABngGWAZgBoAGWAaABngGYAZYBngGeAaIBogGgAaIBoAGeAaIBoAGcAaABngGeAZ4BngGgAaQBngGeAZ4BoAGeAZ4BoAGgAYwBogGgAaIBogGiAaQBogGiAaI",
    "BogGiAaIBogGiAaIBogGiAaIBngGeAY4BoAGeAZwBmgGaAZ4BngGGAZIBkgGSAZIBkgGSAZ4BngGCAZ4BjAGkAYgBggGiAaABngGeAZ4BngF8AYoBogGgAaABoAGgAaABoAGgAaABhAGcAZ4BiAGQAZ4BngGaAZ4",
    "BnAGQAZ4BoAGSAZoBmgGgAZ4BngGgAaABngGeAZ4BngGgAZgBmAGeAZ4BngGeAaABiAGeAaABngGeAZ4BngGgAaQBogGeAZ4BngGgAaABoAGeAaABngGeAZgBngGgAZ4BngGeAZ4BngGeAaABngGeAZ4BjgGeAZ4",
    "BngGeAZ4BngGeAZ4BoAGgAZ4BngGeAaABoAGeAaABngGeAZ4BngGgAaIBogGgAZ4BngGeAZ4BngGiAZ4BngGeAaABngGeAZ4BoAGeAZ4BoAGgAZ4BngGeAZ4BngGgAZ4BngGeAaIBngGgAaABngGkAZ4BoAGeAZ4",
    "BngGgAZ4BngGeAaABngGeAaABnAGgAZ4BoAGeAZ4BngGiAaABngGGAYgBhgGOAZ4BkgGUAZIBngGUAYwBngGSAaABmAGiAZQBjgGeAZABkgGgAZIBngGeAZ4BngGgAZwBkAGeAaIBngGeAZ4BngGiAZ4BngGeAZ4",
    "BjAGgAaABoAGgAZ4BngGeAZ4BoAGeAaABngGeAZ4BngGeAZ4BoAGeAZ4BoAGeAZ4BngGeAaABogGeAYQBnAGgAXwBngGMAaABngGYAaIBngGiAaIBmgGaAZoBnAGcAaABngGgAZ4BngGeAZ4BmgGgAZ4BoAGgAaA",
    "BoAGaAZ4BmgGaAZ4BngGeAZ4BnAGWAZoBoAGeAZoBngGeAZ4BlgGgAZ4BngGgAZ4BjAGeAZ4BoAGaAZ4BngGMAZ4BoAGeAaABoAGgAaABoAGgAYYBhgGOAZ4BiAGeAZ4BhgGeAYwBngGMAY4BngGgAaQBogGiAaQ",
    "BngGgAZ4BngGkAaYBngGeAaABoAGIAZ4BngGeAZwBngGYAZ4BigGSAaIBngGeAZwBoAGeAZ4BngGMAYoBngGOAZ4BjAGeAZ4BngGQAYIBoAGgAaIBngGkAaABoAGgAZ4BoAGgAZoBoAGgAaIBogGkAaIBogGgAZ4",
    "BngGgAZ4BogGiAaIBogGiAaIBogGiAaIBogGiAaIBogGeAaIBngGeAZoBngGgAZYBngGSAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGeAZ4BngGiAaABngGeAZ4BngGeAZ4BoAGeAaABoAGKAZQBlAGgAZwBngGgAYo",
    "BngGMAYwBnAGSAZIBngGeAaABoAGgAZ4BkgGSAaABoAGGAZ4BkgGgAaABngGeAaABngGeAZ4BngGeAZ4BngGeAZ4BngGeAaIBjgGiAaABngGgAZ4BngGeAZ4BoAGgAZ4BngGeAZ4BnAGcAZABlgGIAYwBngGiAaI",
    "BogGoAaABoAGgAZ4BngGeAaABngGeAZ4BngGeAZ4BngGeAZ4BngGeAaABngGeAaIBngGgAZ4BqAGgAZ4BogGeAZoBmgGQAZ4BngGeAaABoAGeAZ4BngGeAaABjAGWAaABjAGSAaABmAGcAaIBoAGgAZ4BoAGeAZ4",
    "BngGeAaABoAGSAZ4BkgGcAZIBmgGeAZIBoAGcAZIBoAGSAZ4BoAGSAaIBmAGeAZgBkgGgAZIBoAGeAZIBngGgAZ4BhgGgAZ4BkAGSAZwBjgGWAZQBoAGeAZ4BngGeAZ4BpAGgAZ4BngGeAZ4BogGcAaQBpAGkAaQ",
    "BpAGkAZ4BkgGeAaABjAGgAZIBoAGeAZwBngGMAaABmAGWAZgBnAGcAZ4BogGeAaABigGiAY4BjgGOAZ4BkgGOAZoBjgGUAZQBngGeAYwBkgF+AaQBoAGiAaABoAGgAZoBkgGOAZ4BjgGYAZQBogGkAaABogGQAaA",
    "BoAGgAZ4BbgFuAW4BhAFyAXQBbgFuAW4BhgEoAEwAygBMAW4BdAFuAXIBcgFwAW4BcgFuAXQBcgEIAQgBOAD6ATgBcgFuAXABbgFyAW4BbgFuAXIBbgFuAW4BbgFuAW4BbgF0AW4BdAFuAXIBbgFuAW4BbgFuAW4",
    "BbgFuAW4BbgFwP9IBiAEYAYYBGAGGARgBiAEYAYYBhAGEAYYBhgEYARgBGAEYARgBGAEYAVwBEgESARIBEgESARIBbgGGAW4A1gCeAaAA2gDKANgBnAFMARoBAgGgAZIBngGSAaABjAGYAYwBoAGcAaABiAGQAZw",
    "BjgD4AaABigFcAUYBiAD0AaIBkAD4ATgBngGgAIoBSAEqAVgBNgEwATYBEgFAATYBEAEiAZ4BngGSAToBkgEuASYBFgEgAR4BEAEYAZ4BAgDwATIBngGeAaYBpAEYATABngFkAZ4BoAGeAZYBngGaAaABngEiAKw",
    "BfgGIAOoBoAGcAZwBkADSAZIBEgGiAZ4BoAGeAZ4BnAGeANoBkAGcAT4BRAE8ARIBQgEsAUoBHgEMASABIgDkAOQBAgGOATYBJgFAAT4BQAE0ASQA7gEcAaQBJgE4AYgBXgF6AZ4AkgFiAVQBQgCcAaABnAGKAUw",
    "BngGeAaABQAGeALwBjgGIAaABmgGkAZ4BngGIAZ4BoAGgAZ4BngGYAZ4BogGiAZ4BjgGMAaABjgGgAaABngGgAZ4BNAC+AY4BjAGeAZ4BngGgAYIBlgGUAZIBogDQAaABfAGaAZwBiAGeAZ4BngGgAaIBngGGAZ4",
    "A0gGgAZ4BJgGgAaIBkgGKANABngDGAaABngGeAWoBkAGiAZ4ApAGeAaIAngCCAaABkAGeAYYBkgCCAZwBoAGOAY4BngBqAZ4AqACCAaABgAGeAaABjgGOAZwBhgGUALYBdAGgAaABngGeAaABjgGeAXYBcgFyAXA",
    "BcAGgAXIBcgFyAIYBngDaAZ4AtgGYAaABjgGSAZIBhAGeAY4BngGOAaABngGeAZ4BjgGGAZ4BjAGgAZ4BngGeAZ4BngGeAZIBigGeAaABngGQAZwBogGeAYYBngCWAXoAYAGgAZ4BngGgAZ4BhAGeAZ4BiAGEAaA",
    "BkgGgAYwBngGKAYYBngGgAY4BoAGCAZ4BngGgAZ4BngGeAZ4BoAF4AZIBngGAAZwBhAGeAY4BngF6AZ4BngGgAZ4BkAGiAZ4BngGeAYwBngGgAZ4BjAGeAZ4BjgE6AZ4BngGUAY4BnAGcAaIBngGMAZ4BngGeAZ4",
    "BngGeAYYBoAGgAYoBoAEyAZ4BhAE6AZ4BoAGQAaABngGeAZwBigGgAaAAggE8AaABngGMAZ4A3gDWAZwBnAGMAZ4BngGYAZ4BoACaAaIBOgF6AFIBngGcAaABggGeAZ4BlgGgAQQBngDaAYIBjAGgAKoBjAF+AYo",
    "BngGQALYBmAGeATYBNgGeAMABmgGgAZoBogGgAaABoAGeAaABngGKAZABLgGIAYoBoAGeAZ4BngC4AZ4BogGeAaIBnAGcAZQBoAGeAZIBoAFGAZgBngE+AZoBlgGWAZ4BmAGYAZoBjgGGAZ4AyAGgAZ4BIgGWAZ4",
    "BngGeAZwBogBIAaABkAGiAaIBngGeAaIBngEiAZ4BoAGOAYYBhgGWAYwBOgF+AZoBoAGgAaABoAGeAZABoAGeAJQBoADqAZ4BhgGgAYgAwAGYAZ4BngGOAZoBngGeAZ4BngC4AaIBggGCAaABngDMAZ4BKAGgAZY",
    "BngGeAKgBnAGYAaABngGeAZ4A7gGeAYgAqgGCAaABpAGiAYoBjAFyAUwBWgGMAaABngGeAZYArgGiAaIAnACqAYwBjgGOAZABjAGeAZoBHgGOAZQBEgGMALQBgAGCAZwBnAGcAZoBoAGUAZwBjAGeAZ4BUgGeAZ4",
    "BDAGgAZgBngGeAZ4BngEgAZ4BjAGMAKQBkAGeAaABoAGOAXgAigGiAR4AXgFeAVYBWAGUAZABjAGEAaIBjgGCAZ4BngGeAY4BogEMAYQBogGeAZ4BlgGeAZ4BoAGcAZwBngGcAZ4BggGeAaABoAGGAXIBfgGeASY",
    "BngCGAQwBjgGeAZ4BngGeAYoBjgGIAZ4BoAGeAZIBiAGgAZ4BhAEgAY4BfgGSAX4BhAGcARQBnAGQAOYBoAGgAZ4BPAGeAZ4BngGOAZQBjgGUAY4BngGeAZ4BngGSAQ4BoAGSAZ4BngGeAJIBUgGUAZoBngGOAYg",
    "BngC8AKgBhAGEAaIBoAGgAaABogGkAaABnAGeAYYBogGgAY4BfAGeAZ4BogGgAIgBoAGeAZ4BngGgAZIBjgDgAZABlAGGAY4BoAGIAZ4BngGAAZwBngGeAZ4BogF4AaABoAGeAY4BlgGWAZ4BoAGSAZ4BigGeAZ4",
    "BhgGMAZ4BngGUAZoBmAGgAYIBhgGIAYAAdgGQAYwBkgGeAYgBngGgAaABhgGgAYYBhgGSAZwBoAGeAZ4BlgGgAYABnAGaAZ4BoAGUAaABkgGSAZIBngGcAaABmgGeAZoBjAGeAYQBngGcAaABngGQAYgArgGSAPQ",
    "BoADkAaIAsAGeAYYBngGGAZoAygGeAaABoAGgAY4BngGiAZ4BlgGWAaQAxAGOAYgAeAGeAZ4BngGEAYQBnADkAaIBoAGgALgBmgDIAYQBngGeAaABlgGiAZ4BngGcATIAMAGMAYgBoAGaAZ4BoACsAZ4BoAEeAaI",
    "BfgESAZIBkgGgAZ4BngGeAZ4BngGIAZ4A6AGaAaABngGeAZ4BngGeAMwA4AGQAZ4BigGcAYABngGeAZwBngCeAZ4AygGeAZ4BigGiAJABogGeAZ4BmgGeAYwBngGEAZ4BngGeAZ4BoAGcAYwAbAGeAYIBngGeAZ4",
    "AOgGeAZ4ATgGAAaQBngGiAXgBeAGMAZ4BngGeAY4BoAGcAZoBngGgAYIBngGeAZ4BngGQAZABjAGMAJoAcgCIAJABngGeAZ4BngGiAaIBngF8AXwBjgGYAZ4BngGeAZgBlgGiAZ4BngGSAZoBoAGgAAABbYFtgW2",
    "BccFtgW2BhQEogEGAnkBLQW2Bc0FtgXLBcsFvgW2BcsFtgXNBcsEZgRmBMkD6QTJBcsFtgW8BbYFywW2BbYFtgXLBbYFtgW2BbYFtgW2BbYFzQW2Bc0FtgXLBbYFuAW2BbYFtgW2BbYFtgW2Bbb/SAYhBF4GFARe",
    "BhQEXgYfBF4GFAYOBg4GFAYUBF4EXgReBF4EXgReBF4FbwRKBEoESgRKBEoESgW2BhQFtgNaBcUDXgR7AnkA+gQOAAA=",
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
