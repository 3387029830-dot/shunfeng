# Stage 0.5 工具链集成验证

2026-11-16，Asia/Shanghai。工作分支 `stage05/toolchain-integration` 从已审查提交 `dd6f2da5325294cf22507210d143fac7de1cc081` 派生。全部样本均为中性几何。请审核此次技术验证，Stage 1 需另行批准。

## 环境

| 项目 | 实测 |
|---|---|
| Mac | Apple Silicon arm64，macOS 26.6 (25G72) |
| Inkscape | 1.4.4 (dcaf3e7)，`/Applications/Inkscape.app`，CLI `Contents/MacOS/inkscape`。官方 ARM64 DMG SHA-256 核对通过，Gatekeeper 确认为公证 Developer ID |
| Affinity | 3.3.3，`/Applications/Affinity.app`，Bundle ID `com.canva.affinity`。官网下载的 DMG，Gatekeeper 确认为 Canva Pty Ltd 公证 Developer ID。用户完成 Canva 浏览器授权 |
| GitHub CLI | 2.104.0，官方 macOS ARM64 发布包校验通过。用户完成设备授权，凭证保存在 macOS 钥匙串 |

官方安装入口为 [Inkscape 1.4.4 ARM64](https://inkscape.org/release/inkscape-1.4.4/mac-os-x/dmg-arm64/dl/) 和 [Affinity 下载](https://www.affinity.studio/download)。GitHub 授权采用 [GitHub CLI 浏览器授权](https://docs.github.com/en/github-cli/github-cli/authenticating-with-github-cli)。

## 测试结果

| 环节 | 结果 | 证据 |
|---|---|---|
| Inkscape 打开、分组、活字、透明与裁剪 | 通过。保留原图层和嵌套组、文本节点、55% 不透明度、裁剪关系 | [输入 SVG](../../tests/stage05/inputs/neutral.svg)、[Inkscape 重存 SVG](../../tests/stage05/inkscape/neutral_inkscape.svg) |
| Inkscape 定向节点修改 | 通过。通过对象 ID 修改贝塞尔控制点，其他命名对象一致 | [修改 SVG](../../tests/stage05/inkscape/neutral_node_modified.svg)、[节点命令](logs/node_edit.json) |
| Inkscape 输出与稳定性 | 通过。三状态批量输出 PNG/PDF，重复 PNG 哈希相同，重复 PDF 页内容哈希相同。PDF 全文件哈希受元数据影响 | [CLI 结果](INKSCAPE_RESULTS.json) |
| Inkscape 矢量 PDF 与中文 | 有条件通过。活字 PDF 有路径和子集字体，无栅格图像。视觉核对通过。精确 Unicode 提取失败，`文` 提取为 `⽂`，NFKC 后匹配。转曲副本通过路径检查 | [活字 PDF](../../tests/stage05/inkscape/neutral_live.pdf)、[回渲](evidence/inkscape_pdf_render.png) |
| Affinity SVG 导入与编辑 | 通过。打开 Inkscape 重存 SVG，看到 3 个命名图层、形状组和嵌套组、裁剪与透明。节点工具拖动贝塞尔端点，文字工具将原文改为「中文复测：节点已移动」。原生保存并关闭重开 | [节点](evidence/affinity_node_edited.png)、[文字](evidence/affinity_text_edited.png)、[原生文件](../../tests/stage05/affinity/neutral-import.af) |
| Affinity 中文 PDF | 中文活字可在原生文件编辑，导入字体栏显示 `! Helvetica`，实际显示来自回退。当前 PDF 打印预设可见中文并保留矢量路径，文字提取为空。可搜索中文 PDF 的交付预设待测 | [PDF](../../tests/stage05/affinity/neutral-import.pdf)、[PNG](../../tests/stage05/affinity/neutral-import.png) |
| Affinity Place/Link | 通过。背景 SVG 链接到 3 个原生画板。状态 SVG 单独链接到画板 2。替换源内容后资源管理器标记「已修改」，点击「更新」后正常，关闭重开仍显示链接有效 | [更新前状态](evidence/affinity_link_modified.png)、[重开资源](evidence/affinity_resources_reopened.png) |
| Affinity 原生迭代与导出 | 通过。只更新状态 02，画板 1、3 回渲 RGB 逐像素一致。画板 2 差异框为 `[216, 123, 323, 279]`，位于旋转线段区域，原生测试矩形保留并可选。导出三页矢量 PDF 和 1998×480 PNG | [机器检查](AFFINITY_EXPORT_RESULTS.json)、[前 PDF](../../tests/stage05/affinity/three_boards_before.pdf)、[后 PDF](../../tests/stage05/affinity/three_boards_after.pdf)、[后 PNG](../../tests/stage05/affinity/three_boards_after.png) |
| Affinity JavaScript SDK | 最小探针通过。在脚本编辑器执行 `require('affinity:application')` 并打印模块导出。脚本开关仅在测试时启用，完成后恢复。文件系统、网络、Canva AI 权限保持关闭 | [脚本](../../scripts/stage05/affinity_sdk_probe.js)、[运行输出](evidence/affinity_sdk.png) |

## 复现端到端演示

1. 用现有 Python 运行 `python3 scripts/stage05/test_inkscape.py` 和 `python3 scripts/stage05/test_iteration.py`。前者需要 pypdf。二者要求 Inkscape CLI，可用 `SF_INKSCAPE` 指定路径。已提交源输入、结果及每次 CLI 调用的命令和退出状态。Inkscape PDF 元数据会随导出变化。
2. 拷贝 `tests/stage05/affinity/` 到独立验证目录。打开 `three_boards_after.af` 检查当前结果。若链接仍定位到原目录或显示缺失，在文档 → 资源管理器中按文件名将两个资源指向副本的 `links/`。验证了本机重开与同机副本打开，跨机器定位待测。
3. 复现前后过程时，先把 `iteration/state_02_before.svg` 拷贝到独立验证目录的 `links/state_02.svg`，打开 `three_boards_before.af` 副本并检查链接指向该目录。用资源管理器刷新确保是旧姿态。两个原生快照都使用同名状态槽，更新前 PDF 是固定快照。
4. 只把 `iteration/state_02_after.svg` 拷贝到该状态槽。资源管理器应只显示状态 02 修改。更新后保存为新 .af。检查背景分组显示 3 条画板链接，画板 2 的独立矩形在链接资源之上。链接 SVG 内部节点由源文件负责，Affinity 原生修形保存在独立层。直接重建或换掉容器可能影响原生层，更新应针对资源槽。
5. GUI 导出 PDF 采用「PDF（用于打印）」与「整个文档」，PNG 采用「整个文档」。截图记录图层嵌套、文字工具、资源管理器的状态和画板编号、重开的原生矩形。现有 PDF 可运行 `python3 scripts/stage05/verify_affinity_exports.py` 复核，需 Pillow、pypdf、pypdfium2。
6. 用户已授权 GitHub CLI 的 HTTPS 凭证配置。当前仓库以钥匙串支持的凭证助手读取远程，先 `git fetch --no-tags origin`，再核对 dev 与工作分支的头，普通非强制推送到派生分支。远端 SHA 与本地提交等值检查记录在交接。系统代理配置、GitHub 服务器保护和付费服务沿用用户现状。

## 待关闭的风险

测试画板通过 GUI 手工框选，PDF 页尺寸为 640×478、640×480、638×480 pt。进入正式稿后应以批准的精确画幅创建画板。可搜索中文 PDF 字体、PDF/X、ICC 与出血待真实印刷规格。跨机器链接相对定位、SDK 写入或无人值守尚未验证。Stage 1 开始前需确认画幅、允许字体和艺术审查人。

首选 A 路线的中性闭环已跑通。审查基线后先确认画幅与本阶段结论，再由用户和规划层明确批准 Stage 1 的二维结构试验。
