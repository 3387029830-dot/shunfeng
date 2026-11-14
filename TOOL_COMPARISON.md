# TOOL COMPARISON

## 决策结论

条件推荐 **A：参数化 SVG + Inkscape + Affinity**。程序负责几何、稳定 ID、批量校验；设计软件负责自然轮廓、文字、色彩与排版。它最贴合三张静态插画和节点级局部修改。推荐不等于整条链已经跑通：两款软件均未找到，必须通过中性交换测试后才能确认为生产主线。

备选 **C：Blender 姿态辅助 + SVG 正式绘制 + Affinity**。只在二维几何无法低成本解决空间遮挡、坐骨接触或透视时启用；Blender 仅提供参照，不把渲染图当成最终人物资产。当前未见足够收益支持安装。

暂不推荐 **B：Grease Pencil + Affinity**。三张静态广告不足以抵消绑定、权重、描边投影、SVG 转换与修形成本。骨架复用能力强，但并不能自动产生自然轮廓。若未来扩展为动画，需重评。

## 评分法

1 最弱 / 成本最高，5 最强 / 成本最低。权重总和 100；加权总分=sum(权重×评分)/100。评分是面向本项目的工程判断，不是实测基准；A 的几何源仅部分实测，B/C 尚未运行，分数不表示渲染性能优劣。

| 维度 | 权重 | A | B | C | 依据及限制 |
|---|---:|---:|---:|---:|---|
| 图形可编辑性 | 15 | 5 | 3 | 5 | A/C 的正式路径保留 SVG；GP 导出不承诺原始层级回环 |
| 自动化 | 12 | 4 | 4 | 4 | CLI/Python 文档支持；Affinity 端尚未验证 |
| 姿态复用 | 12 | 3 | 5 | 5 | A 需锚点变换后手工修形；B/C 可借助骨骼 |
| 场景一致性 | 10 | 5 | 5 | 5 | 同源 SVG 或固定 Blender 场景 / 摄像机 |
| 美术自由度 | 12 | 5 | 4 | 5 | A/C 直接调 Bezier；GP 变形仍需修正 |
| 文件兼容性 | 10 | 4 | 2 | 3 | SVG 子集较透明；GP→SVG 是额外转换边界 |
| 学习成本低 | 8 | 4 | 2 | 2 | C 同时维护二维和三维 |
| 性能稳定性 | 6 | 4 | 3 | 3 | 按小型矢量工程估计，均无目标软件性能实测 |
| 三张静态适配 | 9 | 5 | 2 | 3 | A 工具链较短；B 的动画优势本轮用不上 |
| 局部修改成本低 | 6 | 5 | 3 | 3 | A 稳定 ID；C 修改可能需双源同步 |
| 加权总分 | 100 | 4.40 | 3.41 | 4.02 | 待真实艺术样张与交换结果修订 |

## 软件边界

**Inkscape**：官方 CLI 支持 PNG/PDF 导出和按对象导出；SVG 的 g、path、Bezier 适合标准库生成并人工精修。SVG 层通常是带 Inkscape 元数据的 g，别的软件保留 g 不等于保留“图层”语义。测试源含三层嵌套、独立文本层与 clipPath。中文依赖字体，不嵌入字体的 SVG 不能保证异机排版。PDF 应同时留 SVG；文字保留与转曲副本分开。macOS 1.4.4 文档的 CLI 扩展限制需复核，基础 PNG/PDF 导出不可由此直接判定失败。[CLI 文档](https://wiki.inkscape.org/wiki/Using_the_Command_Line)、[发行说明](https://wiki.inkscape.org/wiki/Release_notes/1.4.4)。

**Affinity**：官方支持矢量设计与 PDF/SVG 输出、文字处理；SDK 3.3.1 beta 有 CurveBuilder、GroupNode、Document、ExportConfig 等 API 名称。API 存在不等于已经有可用的无人值守打开、刷新、保存和导出闭环；不假设 Node 能直接 require affinity 模块。官方界面流程是内置 Script Editor 和 Scripts Panel。本轮以 GUI 人工执行为兜底。V2 与新版的脚本能力不得混用。[SDK](https://sdk.affinity.studio/33001/)、[内置脚本流程](https://www.affinity.studio/features/scripting)。

Open SVG 与 Place/Link SVG 是两条独立测试：前者考察节点编辑；后者考察外部资源刷新，不能同时承诺任意内部编辑和无损重新链接。原生格式按实际版本保存：新版候选 .af；若实际使用 Designer V2 则 .afdesign。格式和更新机制须在安装版本复测。V2 Publisher Resource Manager 文档只能提供机制参考，不能证明新版 SVG 链接支持。[资源管理参考](https://affinity.help/publisher/en-US.lproj/pages/Advanced/resourceManager.html)。

**Blender**：Python API 可控制对象、矩阵、摄像机和保存；GP 支持 Armature 变形，透明背景由 RenderSettings.film_transparent 控制。SVG 导出有 Object Mode 和视口投影限制，采样和描边宽度可改变轮廓，不能承诺 CSS、文本、遮罩、嵌套分组可无损回环。当前只需固定二维坐标，不需要三维渲染质感。[GP SVG 文档](https://docs.blender.org/manual/en/5.0/files/import_export/grease_pencil_svg.html)、[Python 保存 API](https://docs.blender.org/api/current/bpy.ops.wm.html?highlight=append)。本机未测试 GP、骨骼、透明渲染、批量状态或 .blend 保存。

**其他工具**：暂不引入 Krita、Figma、Canva、Penpot。本项目当前缺口是原生编辑/交换验证，不是在线协作、模板排版或位图绘画。sharp 仅为现有捆绑的诊断渲染器，无美术主稿角色，不新增创作软件。
