# Issue #7｜Skill 安装验证与 Gate 0 审核

2026-11-17（北京时间）。按 [Issue #7 的执行补充](https://github.com/3387029830-dot/shunfeng/issues/7#issuecomment-6943096408) 使用本报告路径和已有的 [Draft PR #8](https://github.com/3387029830-dot/shunfeng/pull/8)，以 `dev` 为基分支。

## 同步与环境

| 项目 | 实测记录 |
|---|---|
| 仓库与工作目录 | `3387029830-dot/shunfeng`。仓库位于当前聊天工作目录下的 `outputs/SF-City-Advertising-GitHub`，操作在仓库根目录执行。 |
| 同步前 | `git status --short --branch` 仅输出 `## tooling/illustration-skills...origin/tooling/illustration-skills`。本地 HEAD 为 `23e87fddc37a2f41c432eb7cdd9306591527f0c8`，远程名为 `origin`。 |
| 审计起点 | 获取远端并建立本地跟踪分支 `design/single-poster-reset`。本地和远端 HEAD 同为 `597c832c453eebb74d157de61b28ed669db711a1`，基于旧技术基线 `dd6f2da5325294cf22507210d143fac7de1cc081`。本报告的交付 SHA 记在 PR 和交接消息中。 |
| 切换后 | 原有 `tests/stage05/affinity/three_boards_after.af~lock~` 因目标分支的忽略规则显示为未跟踪。`git status --short --untracked-files=all` 已定位，未读取内容，也未暂存或改动。 |
| 本机 | `codex-cli 0.156.1`；macOS 26.6，构建号 `25G72`；`arm64`。 |
| 旧任务状态 | [Issue #6](https://github.com/3387029830-dot/shunfeng/issues/6) 已关闭，GitHub 状态原因为 `not_planned`，Issue 正文明确由 #7 取代。 |

## 安装、原生发现和本轮实际使用

五套 Skill 随目标分支同步到 `.agents/skills/`，由 Codex 原生机制验证。用 `codex app-server --listen stdio://` 建立 JSON-RPC 会话，完成 `initialize` 和 `initialized`，发送 `skills/list` 请求（`forceReload: true`）。分别传入仓库根目录、仓库内 `docs/design` 和原聊天工作目录，按返回路径筛选本仓库 Skill。

- **项目级安装成功。** 仓库根目录与 `docs/design` 各返回五套，名称和路径匹配，均为 `scope: "repo"`、`enabled: true`，五套均无加载错误。每个入口包含 `name` 与非空 `description`，名称与目录一致，Codex 实际解析并注册。
- **原聊天工作目录未识别。** 目录在仓库之外，此处返回本仓库 Skill 数量为 0。当前回合的应用方式是手动显式读取下表五份 `SKILL.md` 并遵循其适用步骤。故桌面原会话的原生 `$` 选择器触发没有实测成功。后续需要原生触发时，从实际仓库根目录打开 Codex 项目或新会话，再检查五个名称。
- **失败与受阻。** 仓库范围内未出现 Skill 加载失败。上游专有工具、生成链和在线示例停用，具体范围见下节。Gate 0 准入决定待用户确认。

| 实际调用顺序 | 入口 | 在本会话执行的检查与结果 |
|---|---|---|
| 1 | [`sf-single-poster-art-direction`](../../.agents/skills/sf-single-poster-art-direction/SKILL.md) | 用阶段停点和历史隔离原则检查项目入口。明确一张印刷海报为当前交付，修正入口和路线里旧三联的执行状态及 Gate 顺序。 |
| 2 | [`design-principles`](../../.agents/skills/design-principles/SKILL.md) | 按消息与受众的检验方法检查简报。当前只确定主题范围，具体配送事件、广告受众和优先传播目标都未批准。将它们留在简报审核，作品的层级和区分度留待有实际作品时检查。 |
| 3 | [`creative-direction`](../../.agents/skills/creative-direction/SKILL.md) | 按项目变更深度核对重启范围。已撤销整套旧视觉策略，可继承经过验证的制作工具。创意输入只认用户确认项。语气目标可沿用，隐喻、构图、颜色和字体由后续阶段探索。 |
| 4 | [`art-direction`](../../.agents/skills/art-direction/SKILL.md) | 按参考可见性、来源和使用权限核对仓库记录。用户图目前只依据重启简报登记，第 3/7 项为重复或近似记录。品牌资产目录只有说明和台账，未发现可投放的官方 Logo、图像或字体文件。 |
| 5 | [`collateral-design`](../../.agents/skills/collateral-design/SKILL.md) | 按成品尺寸原则及印刷参考清单核对媒介。实体印刷已确定。尺寸、方向、观看距离和印厂规格仍空缺。保留真实尺寸校样、出血/安全边距、色彩转换、字体许可与 PDF 预检为印前检查项目。 |

## 完整性、许可和静态审查

从 [固定上游提交](https://github.com/zstvns/design-skills/tree/6a8ea60e3fe70884138554a235ab77b6cb2106d5) 浅获取 Git 对象，核对 `FETCH_HEAD`、文件清单和文件字节。四套上游文件与固定提交逐字节一致。各外部目录的随附许可证也与该提交的根 MIT 许可证逐字节一致，保留 `Copyright (c) 2026 Zach Stevens`。项目专用 Skill 未标为上游代码。

| Skill | 文件数 | 本地引用命中次数 | 附件 |
|---|---:|---:|---|
| `sf-single-poster-art-direction` | 1 | 8 | 项目文档、资产台账及四个协同入口由文本链接引用。 |
| `design-principles` | 5 | 3 | 2 个引用文件、MIT、1 个 eval JSON（4 条）。 |
| `creative-direction` | 9 | 14 | 5 个引用文件、1 个 HTML 示例、MIT、1 个 eval JSON（5 条）。 |
| `art-direction` | 7 | 5 | 4 个引用文件、MIT、1 个 eval JSON（6 条）。 |
| `collateral-design` | 11 | 27 | 8 个引用文件、MIT、1 个 eval JSON（6 条）。 |

以各引用文件的所在目录解析 Markdown 本地链接与 `references/`、`examples/` 文本路径，包括跨 Skill 链接。57 次路径引用均可解析，无缺失。四个 eval JSON 均可解析，Skill 名称相符，21 条用例的 ID 在各自文件内唯一。上游的 `examples/magister` 外链目标目录存在于固定上游树。本轮未请求外链，未运行上游评测或渲染。

- **HTML。** `creative-direction/examples/magister-stylescapes.html` 有 1 段内联脚本，处理标签切换、图示、配色、交互和动画。静态阅读未发现该内联段显式请求凭证、持久存储或调用外部接口。页面另加载未锁版本的 `unpkg.com` Lucide 脚本，连接 Google Fonts 两个域名并引用 Wikimedia Commons 图像。远程代码内容、运行效果、图像和字体素材使用权均未验证。项目仅保留上游静态样例，不打开或执行。
- **代码示例。** 五套目录内没有独立的 JS、Python 或 Shell 脚本。静态阅读 Markdown 中的 JS/HTML 片段、ImageMagick 命令、Wikimedia API 与 Python 占位管道，以及无头浏览器示例。viewer 片段包含动态脚本注入，工具示例会发起网络请求或写入输出，均不进入项目运行路径。
- **工作流依赖。** 上游品牌/营销文档、Logo 与影像库、`brand-strategy`、`logo-design` 等同伴 Skill，以及 Claude Design、Figma、Adobe MCP、生成器和浏览器 viewer 不属于本项目安装范围。[项目 Skill 的协同规则](../../.agents/skills/sf-single-poster-art-direction/SKILL.md#协同-skill-的项目边界)已指向真实简报、规范和授权台账，停用上游产品与代码路径。后续按阶段使用 SVG、Inkscape 和 Affinity。没有创建品牌占位文档、假 Logo 或生成式资产。

## Gate 0 审核

核对了[当前简报](TASK_BRIEF_GATE0.md)、[项目重启规范](SINGLE_POSTER_RESET.md)、[原课程任务](../USER_TASK_V1.md)、[品牌目录说明](../../assets/brand/README.md)和[授权台账](../../assets/licenses.md)。

| 状态 | 审核项 |
|---|---|
| 已确认 | 顺丰同城；最终一张独立实体印刷海报；文案可自主创作；画幅待定。旧人体模拟时钟、三联、旧女性角色、沙发客厅、三姿态与固定腰胯规则退出当前创意。 |
| 已有背景 | 原任务记录大学平面广告结课作业。现有记录未给出新单张海报的课程必需文字、署名、展示和尺寸要求。简报暂列教师和同学为课程观看者，广告受众待确认。 |
| 工作假设 | 可探索即时取送体验和抵达感，假设传播重点为建立品牌或服务认知。城市消费者、本地商户和企业客户都可能随所选场景改变，目前没有目标受众结论。 |
| 未知｜创意输入 | 优先配送情境、具体广告受众和传播目的。课程要求和必要版面信息待核实。 |
| 未知｜品牌与版权 | 官方可用 Logo/VI、颜色和字体规范、字体与图像许可、必用文字和允许发布的业务主张无可核验证据。未填写时效、价格、覆盖范围、承诺或官方 slogan。七张用户图只供后续研究，未在本轮打开、搜集或使用作成品素材。 |
| 未知｜生产参数 | 成品宽高和方向、观看距离、纸材/工艺、出血和安全边距、色彩配置和 PDF 要求。确认实际印厂和课程要求后于 Gate 5 前锁定，未把通用尺寸或数值写成规定。 |

**结论。** Gate 0 审核完成，简报和进入 Gate 1 的许可仍待确认。历史文件与原预览保留，本轮无新增视觉预览、SVG 或原生稿。

**唯一待确认问题。** 这张海报优先表现哪一种顺丰同城配送情境？

## 执行记录

| 实际执行 | 结果 |
|---|---|
| `git status --short --branch`、`git remote`、`git fetch --no-tags origin`、`git switch --track origin/design/single-poster-reset`、`git rev-parse HEAD` | 同步成功，确认审计输入为 `597c832c453eebb74d157de61b28ed669db711a1`。 |
| `codex --version`、`sw_vers`、`uname -m`、`python3 work/single-poster-skill-audit/discover.py` | 通过。用本地临时脚本发送上述 App Server 请求，编辑项目 Skill 前后均重复得到仓库根目录 5、`docs/design` 5、外层聊天目录 0，目标 Skill 加载错误 0。 |
| 上游 `git fetch --depth=1`、`git ls-tree -rz`、`git show`，`python3 work/single-poster-skill-audit/check_vendor.py` | 通过。核对 pin、文件字节、许可、引用、评测 JSON 和示例脚本标签。两个辅助脚本均为本地审计脚本，存于 Git 忽略的 `work/`，没有提交。 |
| `git diff --check`、`git diff --cached --check`、`python3 scripts/check_repository.py` | 通过。提交前检查补丁、暂存目录和仓库既有敏感路径、凭证格式及大小规则。 |
| GUI 菜单验证、评测运行、上游示例渲染、视觉生产测试 | 未执行。以实际 App Server 发现和当前回合的显式正文应用为证据。其余都超出本轮审计，未将它们记为通过。 |
