# Stage 1.1 交付清单

PNG 为 Inkscape 实际渲染。SVG 保留可编辑路径、形态候选与画板的等尺度排布。

| 证据 | PNG | SVG |
|---|---|---|
| 三张独立试样，B 辅助 | [P1](../../previews/stage11/P1.png) · [P2](../../previews/stage11/P2.png) · [P3](../../previews/stage11/P3.png) | [P1](../../source/stage11/generated/P1.svg) · [P2](../../source/stage11/generated/P2.svg) · [P3](../../source/stage11/generated/P3.svg) |
| 完全无家具、刻度和面部细节的剪影 | [P1](../../previews/stage11/P1_silhouette.png) · [P2](../../previews/stage11/P2_silhouette.png) · [P3](../../previews/stage11/P3_silhouette.png) | [P1](../../source/stage11/generated/P1_silhouette.svg) · [P2](../../source/stage11/generated/P2_silhouette.svg) · [P3](../../source/stage11/generated/P3_silhouette.svg) |
| 骨架与承托 | [P1](../../previews/stage11/P1_rig.png) · [P2](../../previews/stage11/P2_rig.png) · [P3](../../previews/stage11/P3_rig.png) | [P1](../../source/stage11/generated/P1_rig.svg) · [P2](../../source/stage11/generated/P2_rig.svg) · [P3](../../source/stage11/generated/P3_rig.svg) |
| 三联同机位 | [预览](../../previews/stage11/triptych.png) | [画板](../../source/stage11/generated/triptych.svg) |
| 体块与无背景骨架 | [预览](../../previews/stage11/body_study.png) | [画板](../../source/stage11/generated/body_study.svg) |
| 旧腿与 L0/L1 | [预览](../../previews/stage11/leg_comparison.png) | [画板](../../source/stage11/generated/leg_comparison.svg) |
| 深袜与浅袜的视觉长度 | [预览](../../previews/stage11/reach_comparison.png) | [画板](../../source/stage11/generated/reach_comparison.svg) |
| 女性身份、H0/H1 对比 | [预览](../../previews/stage11/female_identity.png) | [画板](../../source/stage11/generated/female_identity.svg) |
| 三张神态、视线与手部动作 | [预览](../../previews/stage11/expression_study.png) | [画板](../../source/stage11/generated/expression_study.svg) |
| S0/S1 承托对照 | [预览](../../previews/stage11/sofa_scene_comparison.png) | [画板](../../source/stage11/generated/sofa_scene_comparison.svg) |
| 人物／沙发／轻场景 | [预览](../../previews/stage11/scene_layers.png) | [画板](../../source/stage11/generated/scene_layers.svg) |
| 三姿态 × A/B/C | [预览](../../previews/stage11/clock_comparison.png) | [画板](../../source/stage11/generated/clock_comparison.svg) |
| 弧/靠背、冠点对齐、脚侧刻度放大 | [预览](../../previews/stage11/clock_detail.png) | [画板](../../source/stage11/generated/clock_detail.svg) |
| 共用钟心、腿轴和背景叠加 | [预览](../../previews/stage11/pelvis_alignment.png) | [画板](../../source/stage11/generated/pelvis_alignment.svg) |

- **新增参数与输入** [geometry.v1.json](../../config/stage11/geometry.v1.json)、[手绘矢量曲线](../../source/stage11/refined/character.svg)、[共享场景](../../source/stage11/shared/room.svg)。
- **新增脚本** [构建](../../scripts/stage11/build.py)、[实机验证和导出](../../scripts/stage11/verify.py)。复用冻结 Stage 1 模块中的 XML、几何和对照板基础函数；旧脚本和源文件保留。
- **新增生成物** 上表 SVG、[C 单张 P1](../../source/stage11/generated/P1_C.svg)、[P2](../../source/stage11/generated/P2_C.svg)、[P3](../../source/stage11/generated/P3_C.svg) 与 [坐标](../../source/stage11/generated/pose_coordinates.json)。PNG 均在 `previews/stage11/`，按清单选入 Git。
- **记录** [艺术复审](REVIEW.md)、[实测与完整输出 SHA256](VALIDATION.json)。追加 [阶段记录](../../docs/DECISIONS.md) 与 [项目规范状态](../../AGENTS.md)。
