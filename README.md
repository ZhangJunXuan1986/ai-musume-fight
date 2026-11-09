# AI娘大乱斗 · 网页版（GitHub Pages）

一份 Python 源码，两个地方能跑：手机「Python编译器IDE」直接运行，或用
**pygbag** 编译成 WebAssembly 静态站，推到 GitHub Pages 后任何人打开网址就能玩。

> 先说清楚：**浏览器不会执行 .py 文件**。所以不是把源码丢进仓库就行，
> 必须由 GitHub Actions 把 `game/main.py` 打包成 HTML/JS/WASM 再发布。

## 目录

```
.github/workflows/deploy.yml   # 自动构建 + 发布到 Pages
game/
  main.py                     # 游戏本体（也是你之前那份收敛版，加了网页适配）
  assets/font.ttf             # 子集化中文字体（约百 KB）
  favicon.png
tools/
  patch_index.py              # 给生成的 index.html 注入横屏/缩放 CSS
  make_font.py                # 改了中文文案后重新生成字体
requirements.txt             # 本地开发依赖
```

## 五步上线

1. 在 GitHub 新建仓库（比如 `ai-musume-fight`），把**本目录所有文件**推到 `main` 分支。
   `.github/` 目录别漏。
2. 仓库 **Settings → Pages → Build and deployment → Source** 选 **GitHub Actions**。
3. 去 **Actions** 标签，等 `Deploy to GitHub Pages (pygbag)` 跑完（首次约 2–5 分钟，
   要从 CDN 拉 Python WASM 运行时）。也可以点 `Run workflow` 手动触发。
4. 打开 `https://<你的用户名>.github.io/<仓库名>/`
5. 手机**横屏**打开，点「开始对战」→ 左下 P1 / 右下 P2 → 中间「AI：关」可切单人。

> 如果 Actions 报权限错：Settings → Actions → General → Workflow permissions
> 选 **Read and write permissions**。不过本 workflow 用的是官方 Pages 部署接口，
> 只要第 2 步选了 GitHub Actions 通常就够了。

## 本地预览 / 构建

```bash
pip install -r requirements.txt

# 本地起服务（会打开 http://localhost:8000）
python -m pygbag game

# 只构建不启服务器，产物在 game/build/web/
python -m pygbag --build --width 1280 --height 720 game
python tools/patch_index.py game/build/web/index.html

# 桌面直接跑（不打包）
python game/main.py

# 不开窗口的自检
python game/main.py --selftest
python game/main.py --touchtest
```

`game/build/web/` 是纯静态文件（index.html + favicon.png + *.apk），
也可以直接拖到 Netlify / Cloudflare Pages / itch.io。

## 为网页改了什么（其余逻辑一行没动）

| 改动 | 原因 |
|---|---|
| `import asyncio`；`App.run` 改 `async def`，每帧 `await asyncio.sleep(0)` | pygbag 硬性要求，不让出事件循环浏览器标签会卡死 |
| 入口改成模块级 `asyncio.run(App().run())` | pygbag 用 runpy 以 `__main__` 执行 `main.py` |
| `IS_WEB = sys.platform == "emscripten"` | 区分网页与桌面 |
| 网页下关掉 `pygame.FULLSCREEN` 自绘缩放 | 浏览器里没有系统窗口，canvas 固定 1280×720，缩放交给 CSS |
| 战绩从 JSON 文件改成 `localStorage` | 浏览器 VFS 不适合持久化；桌面/IDE 仍写 JSON |
| `resource_path()` 多候选路径 | 兼容 pygbag 虚拟文件系统的挂载位置 |
| `assets/font.ttf` 子集化中文字体 | 浏览器没有系统字体注册表，不带字体中文全是方块 |
| `tools/patch_index.py` | 竖屏提示、canvas 等比居中、`touch-action:none` 防误触缩放 |

## 改了中文文案怎么办

浏览器打包的字体只包含当前源码里出现过的字。新增角色名/技能名后：

```bash
python tools/make_font.py                    # 自动找系统里的中文字体
python tools/make_font.py /path/to/Font.ttf  # 或手动指定
```

然后重新 push，Actions 会重新构建。

## 已知代价（程序员视角，别踩坑）

- **首屏 15–20 MB**：Python WASM 运行时 + pygame 运行时，冷启动 5–15 秒，
  之后浏览器有缓存会快很多。这是 pygbag 路线的固有成本。
- **手机浏览器帧率**可能低于桌面；配置页把 `FPS` 改成 45、`PARTICLE_MAX` 调小可缓解。
- **iOS Safari 需要较新版本**（WASM 支持）；Chrome / Edge 系最稳。
- **音频**：本作没有音效，反而避开了「必须用户先点击才能播音频」的坑。
- **战绩存在访客自己的浏览器 localStorage**，换设备/清缓存会丢；桌面 IDE 版仍写 JSON。
- 菜单里的「退出游戏」在网页里只是停止循环，页面不会关，刷新即可重来。
- **字体授权**：`assets/font.ttf` 是从系统字体子集化而来，仅作演示。
  若仓库公开或商用，建议换成有明确授权的字体（如 SIL OFL 的 Noto Sans SC），
  并在仓库里保留对应许可文件。

## 为什么不用纯 JS 重写

还有一个选项是彻底移植成单文件 HTML + Canvas/JS：秒开、无 WASM、手机浏览器最省资源。
但那等于把 2000 多行游戏逻辑重写一遍，是另一个项目，不是「把现有代码放上网页」。
**保留你迭代到现在这份 Python 资产、改动最小**，所以选了 pygbag。
如果以后确定只要网页端、愿意放弃桌面/IDE 版，再转 JS 也不迟。

## 技术依据

- pygbag 官方：`main.py` 命名、`async def` 主循环、`await asyncio.sleep(0)`、
  `asyncio.run()` 模块级调用、`--build` 只构建不启服务器、产物在 `build/web/`
- GitHub Pages 官方 Actions：`configure-pages` / `upload-pages-artifact` / `deploy-pages`
- pygbag 默认 canvas 尺寸参数 `--width / --height`，这里显式指定 1280×720 与游戏一致
