# Issue #11｜Skill 调用凭证与应用矩阵

依据 [Issue #11 补充指令](https://github.com/3387029830-dot/shunfeng/issues/11#issuecomment-6946602540)。最初读取 Issue 时尚无该评论，进入预演前已从仓库根目录验证发现并原生调用五套 Skill。初稿完成后的首次推送遇到远端更新。获取远端提交 `86e6c4449548054493476e166ea2e23547751bf9` 并读取补充指令后，暂停发布，补交以下逐项凭证，再做最终修订和复核。 [Issue #11 调用凭证](https://github.com/3387029830-dot/shunfeng/issues/11#issuecomment-6946724876)

## 发现、显式调用与完整读取

Codex CLI 0.156.1 的 App Server 在实际仓库根目录将以下五份返回为 `scope: repo`、`enabled: true`，目标加载错误为零。本轮按下列顺序在任务文字中显式使用 `$skill-name`，向 `turn/start` 同时提供类型为 `skill` 的五条原生输入，将每份完整 UTF-8 正文放进该次任务上下文。执行状态为 `completed`。当前执行也逐份阅读并使用其完整正文。

| 调用顺序 | 仓库内实际入口 | 全文行数 | 本轮适用规则与落实 |
|---|---|---:|---|
| 1 `$sf-single-poster-art-direction` | [项目总控](../../.agents/skills/sf-single-poster-art-direction/SKILL.md) | 108 | ① 以一个主视觉事件统领内街和交付。② 只做 A/B 两套同创意试验，C 冻结。③ 只用普通品牌字占位，按 Gate 4.6 交审停下。应用于 A/B 骨架、排版和停止条件。 |
| 2 `$design-principles` | [设计原则](../../.agents/skills/design-principles/SKILL.md) | 172 | ① 清楚排序主体、交付点和文案。② 节制辅助元素与色彩。③ 检验实际画面，移除品牌后仍应读到主体关系。应用于 128 × 160、去品牌、轮廓和灰阶。 |
| 3 `$creative-direction` | [创意方向](../../.agents/skills/creative-direction/SKILL.md) | 123 | ① 从已批准创意与气质提炼一般原则。② 固定纸箱与送达关系，分别发展材料语言。③ 比较真实渲染证据与难点，留待用户选择。应用于两板和比较矩阵。 |
| 4 `$art-direction` | [艺术指导](../../.agents/skills/art-direction/SKILL.md) | 139 | ① 实看作品并标明用途、来源和近似边界。② 写清材质、视角、光源及承托。③ 用局部与离散尺寸审查实际图像。应用于独立研究报告、三维材质帧和局部。 |
| 5 `$collateral-design` | [平面媒介](../../.agents/skills/collateral-design/SKILL.md) | 247 | ① 同一固定试验画幅、标题层级和留白，核对缩小可读性。② 核对四边与像素尺寸。③ 把出血、纸张、ICC、色彩与软件重开列作印前待验证。应用于并排板与印刷风险比较。 |

五份 Skill 的 SHA-256，按上表顺序：

```text
4f8d8be0454151729c6f59de82c9ef5eaa36fc6522608569a67828ad9a14246c
85fde3778ff1d496f03ee4460e7443e19b13512e7fd0e339044566c95ec290bd
0e244512d5021bd9b428814e6e598a2f063f3db2302c9432e6f0cf325b019b1b
37c3dc50ffd1e9e8a35cb9010892b12f3106ee8a5301baa63a779e9103eecf22
878d28f085e7369c767ebe5583a487406e13d736b9295aa6295b1a38fc0d4cf1
```

本仓库未发现上游 `brand-strategy`、`brand`、`logo-design`、`web-design` 或 `copywriting` 的项目安装，也没有 `.agents/brand.md`、`.agents/design.md`、`.agents/product-marketing.md`、已授权图像库和官方标识。品牌方向从用户已批的 Gate 0 和 Gate 4.6 获取，仅将当前四个通用 Skill 的适用部分用于本阶段。项目总控、AGENTS.md、任务书及用户决定优先，停用上游生成器、外部设计画布、HTML 查看器与全量品牌系统流程。未安装或伪造缺失依赖。

## 完工应用矩阵

| Skill | 本轮具体应用 | 文件或证据 | 完整度 |
|---|---|---|---|
| 项目总控 | 保留打开的箱体、连续街面和落地封箱件，共用一个故事；品牌为普通字，艺术交审停在 Gate 4.6。 | [A/B 主图对照](../../previews/stage4_6/comparison.png) · [比较与停点](COMPARISON.md) | 项目在 Gate 4.6 的批准范围完整执行。 |
| design-principles | 同层级比较，首眼看箱中城市、再看落点。检查缩略、无品牌与黑轮廓。查出 A 塔楼重复窗有地产感、B 纸层缩小时合并，以及两案黑轮廓丢失包裹区分。 | [A 缩略](../../previews/stage4_6/style-a-thumbnail.png) · [B 缩略](../../previews/stage4_6/style-b-thumbnail.png) · [只隐藏品牌实例](../../previews/stage4_6/no-brand-comparison.png) · [看图记录](COMPARISON.md) | 本阶段层级、克制和自审完整应用。 |
| creative-direction | 比较 G3-B 的同一骨架，分别建立矿物模型/箱材与纸层/开槽的视觉差异。按实图记录可读性、偏好与执行成本。 | [A 风格板](../../previews/stage4_6/style-a-board.png) · [B 风格板](../../previews/stage4_6/style-b-board.png) · [比较矩阵](COMPARISON.md) | 本阶段风格探索完整应用。品牌系统、正式字体与选型暂不定。 |
| art-direction | 实看八个独立案例并标注商业/品牌分类、迁移、近似及许可；以原创几何和面光测试接触影、纸厚和折面。实际查看细节与去品牌结果。 | [A 参考](STYLE_A_SURREAL_STILL_LIFE.md) · [B 参考](STYLE_B_PAPER_SCULPTURE.md) · [A 局部](../../previews/stage4_6/style-a-detail.png) · [B 局部](../../previews/stage4_6/style-b-detail.png) | 适用的研究与艺术指导板阶段完整应用。系统级摄影图库和生成器越出本轮范围。 |
| collateral-design | 720 × 900 固定 4:5，两板共享标题位置和同尺度。检验四边、原尺寸与 128px 诊断；归档分辨率、纸色并阶、低照度印刷等待验项。 | [输出尺寸与哈希](RENDER_RESULTS.json) · [印刷风险](COMPARISON.md) | 适用的预演和媒介检查完整应用。印厂规格与正式印前交付尚未批准。 |
