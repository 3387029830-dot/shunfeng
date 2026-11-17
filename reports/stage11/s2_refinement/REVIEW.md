# Stage 1.1｜S2-v2 侧脸精修

对应 [PR #3 艺术选型意见](https://github.com/3387029830-dot/shunfeng/pull/3#issuecomment-6941537000)。基线 `eb60964fae70d5649d5326875548203ddfa1178c`。本轮提交侧脸精修与 P1 局部试摆，艺术验收待审。

| 审查图 | PNG | 可编辑 SVG |
|---|---|---|
| S2-v2 单张大图 | [大图](../../../previews/stage11/s2_refinement/S2-v2.png) | [侧脸源](../../../source/stage11/s2_refinement/S2-v2.svg) |
| 原版／v2 同角度同倍率放大 | [近景对照](../../../previews/stage11/s2_refinement/S2-comparison.png) | [对照 SVG](../../../source/stage11/s2_refinement/S2-comparison.svg) |
| 原版／v2 约 39 px 头高 | [小图](../../../previews/stage11/s2_refinement/small-comparison.png) | [小图 SVG](../../../source/stage11/s2_refinement/small-comparison.svg) |
| P1 头颈肩在 S0 靠垫上的局部试摆 | [试摆](../../../previews/stage11/s2_refinement/P1-cushion-fit.png) | [试摆 SVG](../../../source/stage11/s2_refinement/P1-cushion-fit.svg) |

## 修改与观察

- **鼻唇颏。** 重画从鼻梁、鼻尖到人中和颏部的连续曲线。鼻尖投影回收，鼻翼用淡线交代。上唇、开口和下唇顺着同一侧面轮廓，嘴角略提。下颌仍有成年人的转折，颊部保留一点饱满。
- **眼神与脸颊。** 杏眼的上睑更细、眉色更浅，下睑去掉阴影带，虹膜收进睑形。移除面颊径向渐变和点纹，只保留轻的侧面灰阶及嘴角旁一小笔。约 39 px 对照中，眼神与低束发保持辨识，v2 的笑意比放大时更克制。
- **头发与颈线。** 降低发冠，按刘海的走向重新分束；去掉多条亮线并收短后束。单头像提升领口、缩短颈段，保留原图的成人面部尺度。两张近景共用 520×556 画幅，对照板使用相同裁切与倍率；小图共用 0.143×。
- **P1 承托试摆。** 保留原 S0 靠垫和肩袖路径。v2 头部按耳位放置，缩放 0.262×，随半躺回转 −7°，另画局部颈根接回原衣领。图中低束发叠在靠垫前，肩背延续到垫面斜坡，颈前保持一段连续曲线。试摆验证二维遮挡与连接，实际受力和全景头身读感仍待艺术复审。原 P1、钟心、腿轴及房间证据保留。

## Inkscape 验证

Inkscape 1.4.4 实际导出 4 张 PNG，同环境二次导出哈希一致。四份 SVG 均可编辑，ID 唯一，灰阶和渐变均在文件内。对照板的两个人头均直接取自对应源稿。试摆保留 S0、原躯干和袖体节点，脸部轮廓复用 v2。其他目录与基线无差异。 [命令、尺寸与 SHA256](VALIDATION.json)

本轮到 S2-v2 选型为止。三套表情和全身整合留待批准。PR 保留 Draft，Stage 2 暂未获准。
