# Issue #4 · 项目本地插画 Skills 安装审计

2026-11-17。审计分支 `tooling/illustration-skills`，审计前分支头 `73b7f2e107b86e933747767a9513f3b20f0b8e4b`。艺术基线 `3089139521b311ddf29e2de01ba6b9807f21758b`，对应 Draft PR #3。

**结论：四套 Skill 已在仓库内可发现并启用，核心引用和 MIT 许可完整。四套均可作为文字方法参考。第三方 JS 未运行，运行兼容性未验证。其中的浏览器渲染器不能作为 SVG 安全边界。** [Issue #4](https://github.com/3387029830-dot/shunfeng/issues/4)

## 可发现性与启用

实测本机 `codex-cli 0.156.1`。执行 `codex app-server generate-json-schema --out <scratch>/schema` 核对请求契约。随后通过 `codex app-server --listen stdio://` 初始化本地服务器，调用 `skills/list`，设置 `forceReload: true`，只读取目标四个条目的名称、相对路径和状态。请求未启动模型回合。

| 扫描位置 | 四个项目 Skill | 结果 |
|---|---|---|
| 仓库根目录 | 四个均为 `scope: repo`、`enabled: true` | 通过，无该目录加载错误 |
| `docs/tooling/` | 同样四个，路径仍是仓库内 `.agents/skills/` | 通过 |
| 仓库的上一级目录 | 四个目标仓库路径均未列出 | 与仓库作用域一致 |

以上是本机 Codex App Server 的发现验证。桌面现有会话的技能菜单刷新未单独验收。新任务从已检出该分支的仓库打开，按下表显式使用 `$skill-name`，或在授权范围内由描述匹配。仓库外打开的会话不会自动从这个子仓库发现这批 Skill。安装已限于仓库内，用户全局配置无需调整。

| Skill | 任务对应的使用方式 |
|---|---|
| `$sf-illustration-art-direction` | 项目中涉及女性角色、脸型、成人体态、情绪、人体时钟、客厅及艺术复审时优先使用。先实看参考和固定提交的预览，再做原创小量试样与人工选型。 |
| `$illustration-flat` | 扁平矢量人物、活动姿势或手与道具的关系。只参考肢体叠放、握持、剪影与可编辑 SVG 结构。 |
| `$illustration-line-interior` | 室内、人物与家具、空间层次。参考人物接触、背景与前景分层以及明度组织。 |
| `$game-character-design` | 上游触发针对游戏角色。广告任务可显式引用其剪影、识别距离和角色身份一致性清单。 |

优先级依次为用户本轮授权、仓库及阶段约束、项目美术 Skill、外部参考 Skill。项目灰阶、固定腰胯与 S0 居家构图优先于上游 480×360 工作卡的色板、场景、比例及示例。游戏角色的战斗、武器、阵营、游戏玩法和 3D 生产条目超出本项目使用范围。外部样例的评分规则不能取代用户与 ChatGPT 的艺术门槛。下一轮若获用户批准，按任务书交至少三个真正不同的原创视觉方向，保持同尺寸脸部与全身小图；项目 Skill 中的两版通用示例为最低工作模板，服从本次三方向要求。

## 固定来源与完整性

| 仓库本地 Skill | 固定上游与路径 | 核验结果 |
|---|---|---|
| `illustration-flat` | `agent-skills/illustration/illustration-flat`，`3cc93458c4949c39a04e938ea7892a1d6d3d40bf` | 11 个文件与上游逐字节一致，包含 MIT LICENSE、3 个示例和界面元数据。 [固定树](https://github.com/MengTo/Skills/tree/3cc93458c4949c39a04e938ea7892a1d6d3d40bf/agent-skills/illustration/illustration-flat) |
| `illustration-line-interior` | `agent-skills/illustration/illustration-line-interior`，同一固定提交 | 11 个文件与上游逐字节一致，包含 MIT LICENSE、3 个示例和界面元数据。 [固定树](https://github.com/MengTo/Skills/tree/3cc93458c4949c39a04e938ea7892a1d6d3d40bf/agent-skills/illustration/illustration-line-interior) |
| `game-character-design` | `skills/game-character-design`，`45f314d2a3d3201dd5a0304a3a4f3a5f23a905a2` | 4 个文件与上游逐字节一致。修正旧清单中无法 fetch 的 SHA。 [固定树](https://github.com/jeremylongworth-source/AgentSkills/tree/45f314d2a3d3201dd5a0304a3a4f3a5f23a905a2/skills/game-character-design) |
| `sf-illustration-art-direction` | 项目原创 `.agents/skills/sf-illustration-art-direction/SKILL.md` | 无代码依赖。引用其他三个本地 Skill 的名称均能解析。 |

以两个上游固定 SHA 拉取对象到忽略的 `work/`。用 `git ls-tree -r` 检查树和 `git show <SHA>:<path>` 逐文件比较；许可证分别与上游仓库根 `LICENSE` 比对。角色 Skill 的旧 SHA `45f314d2a3d3201dd5a0304a3f5a3f23a905a2` 实测 fetch 失败。以远程公布的完整对象号再次固定抓取，与本地原有 Skill、角色清单、界面元数据、许可证四个既有文件逐字节匹配，因此只改记录。没有随上游分支升级任何旧文件。

两套 MengTo 各补齐 3 份被 `SKILL.md`、`references/craft.md` 或 `style.json` 引用的示例，以及对应的 `agents/openai.yaml`。示例通过 XML 解析，统一为 480×360，图形和剪裁引用均在文件内；静态检查未发现脚本节点、事件属性、DTD 或外部资源引用。两个 `demo/` 的网页、说明和预览属于上游可选体验，这些文件未被本地 Skill 的必读路径引用。旁支风格 Skill 的名称是上游选型建议，当前授权范围为这四套，没有这些旁支。三个上游 MIT 许可文件完整保留，示例作为工作法参考。`books.svg` 和 `whiteboard.svg` 含上游行尾空白，以保留逐字节一致；其余变更通过 `git diff --cached --check`。

## 静态安全审查

| JS 文件 | 实际代码行为与边界 |
|---|---|
| `illustration-flat/scripts/flat-kit.mjs` | Node 内置 `fs`，几何、手部、头部与 SVG 文本辅助函数。显式 `--demo` 路径使用 `writeFileSync`，按调用参数写 SVG，路径处理没有建目录边界或防覆盖。 |
| `illustration-line-interior/scripts/interior.mjs` | 构造空间、肢体、姿势与 SVG 文本。仅 demo 分支导入 Node 的 `fs`，可按参数写文件；复用 SVG 文本输入时需由调用方保证来源和合法性。 |
| 两个 `scripts/lint.mjs` | 字节一致。读取指定 SVG，另可读取可选的色板 JSON。只检查示例风格的属性、ID 和 480×360 格式。正则扫描有语法覆盖边界，不能承担恶意 SVG 清洗，也不适合直接作为项目画幅验收。 |
| 两个 `scripts/render.mjs` | 字节一致。动态解析 `playwright` 或 `playwright-core`，可从当前目录和全局 npm 根加载。调用固定命令 `npm root -g`，从 `CHROME_PATH`、Playwright 缓存及系统路径查找 Chromium。读取指定文件，将 SVG 和部分标签文本交给 `page.setContent`，随后写 PNG。未限制外部请求，也没有在渲染前独立清洗输入；读取与输出路径由调用参数指定。项目批准的渲染链仍为 Inkscape。 |

六份脚本内未发现主动读取认证令牌、硬编码上传地址或删除文件的逻辑。渲染器有模块装载、浏览器环境和 HTML 输入的风险，按库来源与输入信任边界审查，未执行。六份 JS、Markdown 中的 demo/安装命令和浏览器渲染均未运行，npm/Python 包、Playwright/Chromium 和系统环境未变更。已核读四份 Skill 及所有本地引用、元数据、色板和许可证。仓库内容检查通过。

## 交审停止点

Issue #4 的仓库本地审计完成。下一轮的角色视觉研究等待用户另行批准，届时使用固定版本查看真实商业插画参考，记录来源、观察与可转译原则，再比较三种实质不同的原创成年女性方向。S2-v3 和三联制作均未启动。PR #3、`main`、`dev` 保持原版本。
