# 调研来源与适用范围

检索日期：2026-11-14。仅采用官方开发者文档、软件方教学与艺术家本人流程。下表明确正文阅读、搜索索引和版本边界；没有把营销主张变成本机测试结论。部分网页直开时返回空壳，搜索索引摘录仍可查，但证据强度较弱。

| 来源 | 读取情况 | 适用结论 | 局限 |
|---|---|---|---|
| [Inkscape CLI](https://wiki.inkscape.org/wiki/Using_the_Command_Line) | 官方wiki搜索正文摘录 | PNG/PDF、export-id、actions、stdin和多输入适合批量导出 | 命令因版本而异；未安装实测 |
| [Inkscape 1.4.4发布公告](https://lists.inkscape.org/hyperkitty/list/inkscape-announce%40lists.inkscape.org/message/OCEYDBJCKK2ZF65O3FNKZOSTL7JBTZND/) | 官方公告索引，2026-05-06 | 1.4.4已发布三平台，可作为候选基线 | 安装包页403；安装当天再核验 |
| [1.4.4发行说明](https://wiki.inkscape.org/wiki/Release_notes/1.4.4) | 官方wiki索引正文 | 警示Mac CLI扩展限制，防止假定所有Python扩展均能跑 | 页面仍带draft/未发布字样，与发布公告矛盾；不据此认定版本未发布，按公告为准 |
| [Inkscape基础教程](https://inkscape.org/doc/tutorials/basic/tutorial-basic.html) | 搜索返回官方教程镜像inkscaper.net正文摘录，原域未独立读完 | SVG/XML可编辑，g组和图层适合作为资源结构 | 镜像来源级别低于官方原站；本轮不依赖其做关键兼容承诺 |
| [Affinity SDK 3.3.1](https://sdk.affinity.studio/33001/) | 直接读正文 | JavaScript bindings与beta状态可确认 | 文档自述可能有遗漏和错误；不是本机安装版本 |
| [SDK API列表](https://sdk.affinity.studio/33001/js/apis.html) | 直接读正文 | 可见CurveBuilder、CubicBezier、GroupNode、Document、ExportConfig等接口 | 只查到类型存在，未调用，不能推断所有命令闭环 |
| [Affinity内置脚本](https://www.affinity.studio/features/scripting) | 官方搜索正文 | 内置Script Editor执行，Scripts Panel复用脚本 | 宣传页面不保证无人值守或特定SVG刷新API |
| [官方裁切标脚本教程](https://www.affinity.studio/help/scripting-tutorial-crop-marks/) | 索引有代码和beta声明，直开仅导航空壳 | 说明创建对象/填描/对话框的官方示例，且部分功能未可脚本化 | 未阅读完整教程正文，未执行示例 |
| [Affinity导出设置](https://www.affinity.studio/help/sharing-export-settings/) | 官方索引正文 | PDF可选嵌入字体或文字转曲，复杂特性可能栅格化 | 未测中文嵌字或PDF标准输出 |
| [Affinity Preflight](https://www.affinity.studio/help/sharing-preflight/) | 官方索引正文 | 置入文件字体等问题可能需回原始源修复 | 本机无软件；不能用预检替代目视 |
| [Publisher Resource Manager](https://affinity.help/publisher/en-US.lproj/pages/Advanced/resourceManager.html) | 官方帮助索引正文 | linked/embedded、Update/Replace/Collect机制 | 旧版Publisher文档，不能证明新版SVG支持；字体不随Collect收集 |
| [Affinity格式页](https://www.affinity.studio/help/appendix-fileformat/) | 直开仅导航空壳，未取得格式表 | 不据此给出完整导入格式矩阵 | 新版原生扩展、SVG链接适用性留待本机查证 |
| [Affinity矢量软件](https://www.affinity.studio/graphic-design-software) | 官方索引摘录 | 官方说明可编辑矢量设计及PDF/SVG/PNG等导出 | 不保证第三方SVG全部节点/效果保留 |
| [Affinity下载](https://www.affinity.studio/download) | 官方索引摘录 | 官方安装渠道 | 具体macOS最低版本和下载应用版本未核实 |
| [Blender GP SVG](https://docs.blender.org/manual/en/5.0/files/import_export/grease_pencil_svg.html) | 官方5.0索引正文；直开工具402 | Object Mode导出、采样、宽度、裁切与最大3D视口投影限制 | 5.0说明不能无条件套到5.2，必须锁版本复测；402为读取工具错误，不代表官方软件收费 |
| [Blender GP Armature](https://docs.blender.org/manual/id/5.2/grease_pencil/modifiers/deform/armature.html) | 官方5.2印尼语页索引 | GP有独立Armature修改器，适合姿态变形的候选技术 | 本轮未读全约束细节或实测权重质量 |
| [Blender Python保存](https://docs.blender.org/api/current/bpy.ops.wm.html?highlight=append) | 官方API索引正文 | save_as_mainfile可指定保存路径 | 不能证明本机能保存或渲染 |
| [透明渲染设置](https://docs.blender.org/api/5.4/bpy.types.RenderSettings.html) | 官方API索引含film_transparent | 有透明背景参数 | 索引为5.4文档，不代表建议安装5.4；5.2兼容需实测 |
| [Blender命令行渲染](https://docs.blender.org/manual/en/2.80/advanced/command_line/render.html?highlight=background+render) | 官方旧版正文索引；latest读取失败 | 支持背景渲染这一通用工作方式 | 仅作概念依据；现代引擎参数必须按安装版本查证 |
| [Blender系统要求](https://www.blender.org/download/requirements/) | 官方索引正文 | 当前Mac最低Apple Silicon/macOS13/8GB，建议32GB | 未跑本机benchmark；不能保证具体GP场景性能 |
| [Blender发布](https://www.blender.org/releases/) | 官方索引显示5.2.4 LTS/2026-11-10；直开403 | 候选当前LTS | 发行/补丁号安装时核对 |
| [Adobe：Tyler Pate矢量插画工作坊](https://www.youtube.com/watch?v=Tx2rZ7pR8Ck) | 软件方官方频道视频说明索引 | 手绘概念草图转矢量的可复现示范；说明列出Sketching Process | 本轮未观看全片，不声称分析过全部技法 |
| [Tyler Pate本人流程说明](https://www.linkedin.com/posts/tyler-pate_illustration-adobelive-adobeillustrator-activity-7440747738180521984-bnqu) | 艺术家本人发布的索引摘录 | 灵感→概念草图→Illustrator矢量；支持先审草图再精修 | 是本人概述，不提供参数化绑定系统，不能当作本项目完整广告案例 |

## 调研后的工程判断

专业插画的可取路径是先解决概念和轮廓，再做节点精修与色彩，最终进入版式与输出，而不是先渲染成品再追认创意。上面案例只支持“草图→矢量”的分阶段方法；没有证据证明任意角色可通过骨架自动达到商业质量。本项目的角色修形、共享资产和审批策略是针对需求提出的工程架构，仍须阶段性验证。

同一空间和多姿态的一致性优先用同源资源、锁定坐标、固定比例与审查叠图解决。GP骨骼能提供控制，但手臂、衣服、腰胯接触与指针识别仍需艺术指导。Python标准库适合生成参照和修改XML，JavaScript SDK只在软件内逐个验证功能后接入。暂未找到并完整核验与“人体时钟三联静态广告”完全相同的专业案例，不虚构先例。
