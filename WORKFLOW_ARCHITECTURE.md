# WORKFLOW ARCHITECTURE

## 生产流程与事实源

Brief/审批 → 中心和比例参数 → 三姿态结构参照 → 人工轮廓设计 → 同源场景组合 → 风格色样审批 → 品牌资源验证 → 原生排版主稿 → PNG 校样 / 印刷 PDF → 审稿。Stage 0 只实现中性结构链，后续节点均须逐阶段批准。

| 数据 | 事实源 | 谁可写 / 如何更新 |
|---|---|---|
| 固定坐标、比例、姿态参数 | config/*.json | Codex 按批准任务改；schema_version 与变更说明一起更新 |
| 程序生成参照 | tests 或未来 source/generated | 可重建；只覆盖工具自己生成的文件 |
| 角色、家具正式矢量 | source/common/*.svg 与 source/各海报的姿态精修副本（未来创建） | 设计者精修；Codex 仅按指定对象 ID 改，不全量覆盖 |
| 原生版式、印刷色彩、字体 | 安装版本的 Affinity 原生主稿（未来创建） | 人工精修区；受控资源刷新后保存新版本 |
| PNG、PDF | previews / future deliverables | 派生结果，不能反向成为唯一源 |

## 坐标与布局契约

正式纸张尺寸、出血、分辨率、ICC、主体比例尚未确认，config/poster_layout.json 保持 null。中性测试使用 viewBox 0 0 640 480、固定中心(320,280)，**不能继承为海报构图**。统一采用 x 向右、y 向下，角度从 +x 顺时针；若引入 Blender，必须显式记录二维到世界坐标的变换、正交相机尺度和投影矩阵。

同一份 LivingRoom 背景源复用到三个画板；锁定 sofa、table、floor、background、decorations、shadow 的变换。角色 pelvis 世界坐标固定；沙发坐垫的接触线和遮挡层单独定义，禁止为适应姿态无记录地移动沙发。头、手、道具不能越过已批准的主体安全区域。

## 人物结构方案（尚未绘制）

Character/Pelvis 是根，Torso→Neck→Head；LeftArm/RightArm 含 shoulder/elbow/wrist；LeftLeg/RightLeg 含 hip/knee/ankle。所有关节使用局部坐标并共享固定段长、头身比例、服装轮廓基准。头部朝向、手臂和道具可独立控制。角度约束在角色设计阶段按具体造型校准；当前值保持 null，不能把通用生理范围当作本项目已批准动作。

骨架只定义方向与长度。正式轮廓采取“锚点驱动的分段 Bezier + 逐姿态修形”：将肩、腰、髋、膝锚点变换到世界坐标，随段旋转宽度截面，先得到体块；检查关节连续性，再人工调整切线、负形、衣褶和重心。肘膝不以圆片机械拼接，腰侧可按姿态保留独立修形曲线。每个姿态保存 correction paths；绑定变动后标记旧修形过期，不能自动宣称其仍合理。

用共同服装色、描边规范和段长校验保持同一角色；三姿态分别精修并排审核。手机手势需贴合躯干主方向；蛋糕盘与餐具要让开腰胯中心和主要轮廓。任何“自动变形”都必须经艺术指导确认，不把线段测试当作人体识别通过。

## 时钟、场景与品牌

ClockSystem 保留 Center/TickMarks/PartialArc/RedProgressArc/TorsoDirection/LegDirection。参考方向可以在审查层显示；最终隐藏骨架。少量刻度和局部圆弧退居辅助层，运动轨迹颜色留待品牌核验，不使用具体时间标签。若去掉弧线便完全失去人体时钟识别，应退回 Stage 1 重新设计姿态，不能靠加重边框掩盖问题。

场景不随姿态重生成。共同背景改动必须同时影响三张；单张道具和包装放到对应姿态资源中，不混入背景。三张外部公共资源更新后比对哈希及像素差异，并由艺术指导并排审查接触、遮挡、视角和主体占比。

assets/brand 建来源台账：文件名、获取 URL/提供者、日期、授权范围、校验值、官方/参考/本次原创分类。Logo 与品牌色须后续用户提供或合法渠道获取，本轮未下载。手机界面和包装若原创必须标“课程广告示意”，不能冒充品牌现有产品。配色测试值不是顺丰官方色。

## 定向更新与防覆盖

当前实测：修改 config/geometry_test.json 某 state 后运行 `python3 scripts/geometry.py --state state_02`，只处理对应 SVG；内容相同不重写。test_structure.py 在内存中额外加 7 度，证明仅第二组内容变化；实际 config 未因此改动。neutral_patched.svg 仅修改 id=bezier 的 d。

未来采用依赖清单：pose_02.json → pose_02 guide → pose_02 editable revision → layout asset slot 02 → preview 02；palette 或 common background 改动使三张失效。生成程序只写 generated，人工文件只读；发布资源由批准后的精修源复制到固定路径（同目录临时文件完成后原子替换），然后人工在资源管理器 Update/Replace。不能依赖跨工具内部对象 ID 始终相同；需维护 asset_slot→源文件映射。

每次更新前保存原生副本和资源哈希，生成后列出变更文件、未触及文件、过期修形和校样。若链接 SVG 在实际版本不支持，回退为逐画板替换受控 PDF/SVG 资源，位置尺寸固定；如果导致路径不可编辑，则保留 SVG 分层源并将原生主稿只作排版。不能往返全稿覆盖手工修形。

## 导出与版本

SVG 保留可编辑中文；字体记录 PostScript 名称、版本、授权和测试字符串。交付另出转曲副本，不能覆盖活字源。按印厂规格设置毫米尺寸、出血和 PDF/X、ICC；RGB 校样与印刷转换分开审查，未经规格确认不把测试 PDF 视为印刷件。

建议版本：stageNN_asset_v001 + change log + SHA256；共同资源升级必须关联三个主稿。Git 只在本独立项目经确认采用，不改现有上级仓库；小型文本适合 Git，二进制原生文件按阶段归档。LFS 仅在确定远程与体量后另评，不自动配置。本轮用 MANIFEST + decision log 保存审计状态。
