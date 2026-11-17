# Illustration Skills｜项目本地安装与启用记录

日期：2026-11-17
安装分支：`tooling/illustration-skills`
基于项目提交：`3089139521b311ddf29e2de01ba6b9807f21758b`
安装范围：仅仓库内 `.agents/skills/`，不修改用户全局环境、不安装额外 npm 包。

## 为什么要装

最近多轮角色脸部方案都未通过艺术审查。问题不是 SVG 能否生成，而是缺少成熟的人物插画参考、角色设计检查方法、表情/视线/比例的审美门槛。因此引入专门的外部方法论和项目专用 art-direction skill。**Skill 是设计流程与约束，不是保证自动变好看的模型，也不是自动授权批量绘制。**

## 已纳入的 Skills

| 本地 Skill | 上游 | 固定上游 commit | 用途 | 使用边界 |
|---|---|---|---|---|
| `sf-illustration-art-direction` | 本项目原创 | 本分支内 | 本广告专用艺术指导、参考研究、人物审查门槛 | 优先级最高，项目偏好和用户批准流程不可被覆盖 |
| `illustration-flat` | [MengTo/Skills](https://github.com/MengTo/Skills) | `3cc93458c4949c39a04e938ea7892a1d6d3d40bf` | 研究无描边扁平矢量、人物姿态、手部结构和 SVG 构造 | 上游人物是细长 corporate/design worker，不可照搬比例、配色或造型 |
| `illustration-line-interior` | [MengTo/Skills](https://github.com/MengTo/Skills) | `3cc93458c4949c39a04e938ea7892a1d6d3d40bf` | 研究室内场景的空间组织、人物与家具关系、线面层级 | 上游为 indigo 线稿办公/设计室内，不可直接作为顺丰客厅画风 |
| `game-character-design` | [jeremylongworth-source/AgentSkills](https://github.com/jeremylongworth-source/AgentSkills) | `45f314d2a3d3201dd5a0304a3f5a3f23a905a2` | 角色剪影、可读性、身份一致、姿态与制作检查 | 原用途是游戏角色，不能照搬战斗角色/武器/服装检查项；仅借用轮廓、身份和可读性原则 |

上游两个仓库的 LICENSE 已随 vendored 文件保存在各自 Skill 目录中（MIT）。上游仓库地址、commit 固定，不追随浮动 main 更新。项目自有 skill 不依赖外部许可证。

## 文件内容

- `.agents/skills/sf-illustration-art-direction/SKILL.md`
- `.agents/skills/illustration-flat/SKILL.md`、`style.json`、`references/craft.md`、`scripts/*`
- `.agents/skills/illustration-line-interior/SKILL.md`、`style.json`、`references/craft.md`、`scripts/*`
- `.agents/skills/game-character-design/SKILL.md`、`references/character-readability-checklist.md`、`agents/openai.yaml`、`LICENSE`

## 安全审查 / 依赖说明

- 已抽查 MengTo 的 `flat-kit.mjs`、`interior.mjs`、`lint.mjs`、`render.mjs`；脚本包含本地 Node 文件读写和渲染逻辑。两个 render 脚本使用 Node `child_process.execSync('npm root -g')` 查找 Playwright，启动本机 Chromium；不应在没有确认依赖、沙箱和调用参数前运行。
- 没有运行任何上游脚本，没有 npm install，没有执行网络安装器，也没有安装全局软件。
- Codex 首次启用前必须检查所有 Skill 的完整内容和所有脚本，检查额外的子目录/遗漏文件、相对引用是否完整、是否含有外连/敏感数据读取/破坏性命令；发现风险先停并报告。
- 仅在明确需要时调用 render 脚本。项目已有 Inkscape 工作流优先；不能为满足 Skill 自带示例而新增 Playwright/Chromium。
- 上游 Skill 中的示例、配色、比例和组件库是教学范例，不是本项目设计目标。不可机械套用到广告角色。

## Codex 安装后验证任务

1. 确认当前分支是 `tooling/illustration-skills`，检查工作区状态，禁止改动 `main/dev` 和 PR #3 的 Stage 1.1 产物。
2. 读取本文件及每个 `SKILL.md`、其引用的所有文件。确认 Codex 能在本仓库上下文发现这四个 Skill；报告识别到的名称、触发条件和冲突优先级。
3. 对上游源文件与固定 commit 的文件进行内容/路径核验，检查目录引用完整性；补全遗漏的 license / referenced file（若有），不得自行升级版本。
4. 做静态安全检查；不执行第三方 JS、不装包、不运行渲染、不修改系统配置。
5. 输出 `reports/tooling/illustration-skills/INSTALL_AUDIT.md`，写明可发现性、静态检查结果、缺失项、潜在冲突和启用方式。
6. 提交并推送本分支；建立 Draft PR 或更新对应 Issue，**不要合并**。

## 安装之后的第一项视觉工作（本 Issue 不执行）

当用户另外批准后，才用项目专用 skill + 外部技能指导进行参考研究。首个设计交付应是独立的角色视觉方向板，而不是继续在 S2-v2 上打补丁：至少 3 个真正不同的原创风格方向，先列出并实际打开可见的商业插画参考（来源/作者/具体作品/可见图/可借鉴的一般原则/不可复制部分/许可说明），再交同尺寸脸部与全身小图。用户选择之前不做三联、不做 Stage 2。用户明确说“美萌”意味着甜美轻萌、自然、亲和、有生活感的成年女性，不是幼儿化大头娃娃。

## 不属于本次安装范围

- 不安装 Adobe/Affinity/Inkscape 插件、MCP、全局 npm/Python 包。
- 不自动生成角色、海报、品牌素材或调用图像生成。
- 不合并 PR #3，不批准 Stage 2，不改 main/dev。
