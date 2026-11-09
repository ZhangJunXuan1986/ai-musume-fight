# assets

- `font.ttf`：子集化中文字体，只保留 `game/main.py` 里出现过的字符（约 970 个），由 `tools/make_font.py` 生成。浏览器没有系统字体注册表，删掉它中文会变方块。
- 本包内字体的原始来源文件：`/usr/share/fonts/truetype/wqy/wqy-microhei.ttc`（文泉驿微米黑）。
  若仓库公开或商用，请自行核对原字体的再分发条款，或换成有明确授权的字体（如 SIL OFL 的 Noto Sans SC）并保留许可文件。
- 想换角色立绘：放 `assets/<角色id>.png`（如 `deepseek.png`），`load_portrait()` 会自动优先使用；不放就走代码绘制的 Q 版。
- 新增任何文件后都要重新 push，pygbag 才会把它打进 WASM 包。
