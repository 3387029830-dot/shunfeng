# TEST REPORT

日期：2026-11-14，Asia/Shanghai。输入、输出均位于本项目；正式人物、客厅、品牌画面数量为零。

## 实测与阻断总表

| ID | 输入 / 操作 | 实际结果 / 结果文件 | 判定 |
|---|---|---|---|
| E01 | uname、sw_vers、Python、Git、过滤后的 system_profiler | reports/environment.json | 通过；内存 16GB 是已装总量 |
| E02 | sysctl -n hw.memsize | Operation not permitted；system_profiler 替代取得内存 | 首命令失败，信息需求已解决 |
| S01 | `python3 scripts/geometry.py` | tests/svg/neutral.svg、state_01/02/03.svg | 通过，标准库生成 |
| S02 | `python3 scripts/test_structure.py` | reports/structure_results.json；logs/structure.log | 所列断言通过；不是艺术验收 |
| S03 | xmllint --noout 每个 SVG | 6 个 XML 良构性检查通过 | 通过；非完整 SVG schema / 规范认证 |
| S04 | neutral 源与 patched 比较 | 只变 Bezier d；neutral_patched.svg | 通过，稳定对象 ID 可定向编辑 |
| S05 | 复制配置，仅 state_02 +7° | state_02_plus7.svg；其他两组内容不变 | 通过，配置本体未改 |
| S06 | 三状态 background 子树字节比较、center 属性比较 | 背景哈希相同，中心全为(320,280) | 通过，共同坐标系 |
| S07 | 重建 / `--state state_02` | 字节不变；未改内容不重写 mtime | 通过，确定性与独立导出 |
| R01 | Chrome 无头读取 neutral.svg、640×480 截图 | 进程 exit 134；logs/chrome_png.log 为空，未获诊断详情 | 失败；原因未确定，不冒称权限已定位 |
| R02 | qlmanage -t -s 640 -o previews neutral.svg | exit 255；logs/quicklook.log 显示 sandbox initialization failed | 失败，图形代理限制 |
| R03 | `node scripts/render_png.cjs`，捆绑 sharp | 6 张 853×640 PNG；reports/render_results.json 与 logs/render_png.log | 通过（替代渲染器，不是 Inkscape） |
| R04 | 中文、形状、裁剪、透明度目视 / 像素抽样 | previews/neutral.png；reports/pixel_results.json | 本渲染器通过；字形可读，字体是否替代未取证 |
| R05 | patched PNG 与原 PNG 像素差 | 差异框 (76,423)-(469,486)，仅曲线区域 | 通过；其他区域未变化 |
| P01 | ReportLab 将 neutral.png 嵌入诊断 PDF，pypdf 读回 | tests/svg/raster_diagnostic.pdf；reports/pdf_results.json；1 页、640×520pt、1 张图像 | 通过（仅光栅传递） |
| P02 | Poppler 回渲该 PDF | previews/pdf_check.png；初次退出0但大量 fontconfig 警告 | 带警告通过 |
| P03 | 工作区局部 FONTCONFIG_FILE 重跑 Poppler | logs/pdf_render_fixed.log，回渲 PNG 已目视：标题与图形完整 | 通过，不改全局设置 |
| I01 | Inkscape PNG / 矢量 PDF / 图层界面 | 未找到目标应用 | 阻断，未执行 |
| A01 | Affinity Open/Place/更新/保存/导出/SDK | 未找到目标应用，未打开 GUI | 阻断，待人工验证 |
| B01 | Blender 创建对象/角度/固定相机/批量/保存 .blend | 未找到 Blender；遵照任务书仅已安装时执行 | 跳过，未执行 |

## 输入设计与范围

neutral.svg 含 circle、rect、三次 Bezier、三层嵌套 g、三层 Inkscape 图层标记、一段中文、opacity=0.55 与 clipPath。只有裁剪，未使用 mask；不能声称遮罩兼容性通过。源节点和文本均保留为 XML 图形元素，但 GUI 内能否继续编辑仍须目标软件核查。

中性参数 config/geometry_test.json 定义 640×480 viewBox、中心(320,280)、长度170/125、固定方向25°、三组可变角-165/-125/-85°。所有这些仅是软件测试值，不是未来人体、画布或海报姿态的批准值。PNG 输出 853×640 是 sharp 在显式 density=96 下的当前结果；不将其物理尺寸 / DPI 当作印刷规格。

结构测试断言数以 structure_results.json 为准，所有记录 PASS；XML 良构性、固定背景、定向变化与确定性都是不同断言。几何三状态目视见 previews/geometry_contact.png，无人体意义。透明矩形样本RGB(227,185,161)，裁剪外部与背景同为(244,241,234)；只是点检，不是全画面色彩管理验收。

## 执行命令与重现

标准库步骤见 README；脚本会写 tests/svg 和 reports。Chrome 的实际可执行为 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`，参数 `--headless --disable-gpu --no-first-run --no-default-browser-check --disable-background-networking --user-data-dir=<工作区>/work/chrome-stage0 --screenshot=<项目>/previews/neutral.png --window-size=640,480 file://<项目>/tests/svg/neutral.svg`。退出134，未继续尝试系统权限或禁用沙箱。Quick Look 参数见 R02，日志保留错误原文。

PDF 操作：使用 Codex 捆绑 Python 运行 scripts/pdf_diagnostic.py，再执行捆绑 `pdftoppm -png -scale-to 900 -singlefile tests/svg/raster_diagnostic.pdf previews/pdf_check`。首次日志重复警告已去重保存，原字节数和SHA256见日志。重跑前设置工作区字体目录和缓存；完整重跑脚本 scripts/render_pdf_check.sh 与 config/diagnostic_fonts.conf 可复用。

## 目标软件补测（未执行命令模板）

```sh
/Applications/Inkscape.app/Contents/MacOS/inkscape --version
/Applications/Inkscape.app/Contents/MacOS/inkscape tests/svg/neutral.svg --export-area-page --export-filename=tests/svg/inkscape-neutral.png
/Applications/Inkscape.app/Contents/MacOS/inkscape tests/svg/neutral.svg --export-area-page --export-filename=tests/svg/inkscape-neutral.pdf
```

以上路径是安装后候选，必须先确认实际 App Bundle。然后逐 SVG 批量导出，读回 PDF、检查页面尺寸、中文是否活字/嵌字、路径是否向量，并回渲比较。按 tests/affinity/MANUAL_CHECK.md 完成人工验证；未运行的脚本和说明不计为通过。

## 本轮不支持的结论

尚不能宣称：Inkscape 渲染成功、跨软件分组保留、Affinity 原生保存成功、外部 SVG 可更新、SDK 无人值守、SVG→矢量PDF可靠、PDF/X/CMYK/ICC合格、Blender有效提升人体时钟、姿态自然或创意能被识别。Stage 0 形成可审查基础设施，仍有生产阻断项。
