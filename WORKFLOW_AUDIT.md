# WORKFLOW AUDIT

## 结论与证据等级

当前 shell 直接访问用户 Mac 的 `/Applications`、本项目目录及系统工具，结果是 macOS/arm64，而不是 Linux 远程沙箱的结果。执行仍受 workspace-write 沙箱约束；能读 App Bundle 不代表能自动操作 GUI。联网调研经 Web 工具完成，不代表 shell 有网络权限。

状态用语：**实测通过**=本机有输入、执行和结果；**官方支持**=文档或官方搜索索引证据；**待验证**=未执行；**阻断**=缺少先决条件；**失败**=实际执行返回错误。官方支持不能升级为本机成功。

## 本机快照

| 检查 | 实测结果 | 证据 / 限制 |
|---|---|---|
| 主机 | MacBook Air / Mac17,3，Apple M5，arm64 | system_profiler、uname |
| 系统 | macOS 26.6，build 25G72 | sw_vers |
| 内存 | 16 GB 已安装内存 | system_profiler；不是当前空闲内存 |
| sysctl 内存检查 | 失败，Operation not permitted | 已用 system_profiler 替代；仍有 hw.cpufamily 警告 |
| 系统 Python | 3.9.6 | 标准库生成及结构测试通过 |
| Git | 2.54.0 (Apple Git-157) | 未 init、commit、LFS、remote 或 push |
| Codex Python | 3.12.14 | 捆绑运行时，含 Pillow、ReportLab、pypdf、pypdfium2 |
| XML 检查 | /usr/bin/xmllint | 六个 SVG XML 良构性通过，不是全量 SVG schema 验证 |
| Chrome | 157.0.8103.79 | App Bundle 在 /Applications；无头截图进程退出 134，未产生有效输出 |
| Quick Look | /usr/bin/qlmanage | 退出 255，sandbox initialization failed |
| PNG 备用渲染 | sharp/libvips | 六个 SVG 成功，详细依赖版本在 reports/render_results.json |
| PDF 备用诊断 | ReportLab → pypdf → Poppler | 单页 / 一张嵌入图像；只验证光栅传递 |

系统 Python 未发现 Pillow/cairosvg/reportlab/pypdf/lxml。没有为其安装包。应用探测范围为 `/Applications`、`/System/Applications`、`${USER_HOME}/Applications`，最深四层，进入 .app 前检查名称，并检查 PATH。**范围内没有发现 Inkscape、Affinity、Blender；不能排除其他自定义位置或未挂载磁盘。**没有实际安装版本或可执行路径可报告。

## 目标软件与官方渠道

| 工具 | 建议版本 / 架构 | 状态与兼容依据 |
|---|---|---|
| Inkscape | 官方稳定 1.4.4，macOS arm64；安装时再核验发布页 | 需用户批准后自行安装；[官方发布公告](https://lists.inkscape.org/hyperkitty/list/inkscape-announce%40lists.inkscape.org/message/OCEYDBJCKK2ZF65O3FNKZOSTL7JBTZND/) 确认三平台发布。下载页 [Inkscape](https://inkscape.org/release/inkscape-1.4.4/) 本轮直开 403。硬件实际运行未测 |
| Affinity | 新版 3.3.x 候选；SDK 文档为 3.3.1，应用精确版本须另核验 | [官方下载](https://www.affinity.studio/download)；未安装，SDK 版本不能冒充安装版本。macOS 最低要求本轮未获得足够正文，装前核验 |
| Blender | 仅触发备选时考虑官方当前 LTS Apple Silicon 版 | [官方发布](https://www.blender.org/releases/)、[系统要求](https://www.blender.org/download/requirements/)；官方索引显示 5.2 LTS / 5.2.4。M5/26.6/16GB 满足网页列出的最低架构、OS、内存要求，但未实测性能，且低于推荐 32GB |

SDK 官方明确 beta。只能在匹配版本的 Affinity 内验证；本轮没有执行 SDK，也没有接入第三方 MCP 或付费 AI 服务。

## 权限、文件安全与输出

执行前 outputs 和 work 均为空；未发现适用的父级 AGENTS.md。本轮新建 `outputs/SF-City-Advertising` 和 work 下的辅助文件。用户原任务书仅复制到 docs/USER_TASK_V1.md，原件未改。未读取凭证，未改系统设置、全局 Python、Homebrew 或现有设计稿。

Poppler 首轮能输出 PNG 但 fontconfig 重复警告。通过工作区局部 fonts.conf 和工作区缓存重跑解决，无全局字体配置修改。原日志已压缩为去重样例、原长度及 SHA256，避免保存无意义的大日志。

机器证据见 reports/environment.json；测试、命令及所有限制见 TEST_REPORT.md。结论：**可建设参数化矢量源与预览系统；专业编辑软件的导入、原生保存和矢量印刷导出尚未建立本机证据。**
