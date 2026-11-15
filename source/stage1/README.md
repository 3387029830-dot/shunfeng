# Stage 1 可编辑源

- [shared/sofa.svg](shared/sofa.svg) 是共享承托原稿。生成脚本把相同的沙发组嵌入三份独立画布，以便单文件在 Inkscape 打开。
- [refined/contours.json](refined/contours.json) 是人工书写的贝塞尔轮廓输入，与 [构图参数](../../config/stage1/geometry.v1.json) 分开。改变单姿态只重建该姿态的生成文件。
- `generated/` 存输出，包含 `P1.svg`、`P2.svg`、`P3.svg`，每张的 `_body.svg`、`_rig.svg`、`_B.svg`、`_C.svg`，以及审查板。三张均有独立的 `setting`、`figure` 和 `clock` 图层与可编辑的路径、组和变换。
- 在 Inkscape 里用图层面板隐藏沙发或时钟辅助，用节点工具选中 `torso`、`head-profile` 或四肢路径进行检查。如果需要保留手修，请另存到 `refined/` 下的新 SVG，生成器不会读取或覆盖这些手修稿。将修订同步进参数化版本时，先更新对应输入，再重建预览。

从仓库根目录用 Python 3.9+ 和 Inkscape 1.4.4 重建。

```sh
python3 scripts/stage1/build.py
python3 scripts/stage1/verify.py
```

默认机器为 macOS，可用 `SF_INKSCAPE` 指向已安装的 Inkscape 可执行文件。第一条命令只写 `source/stage1/generated/`。第二条导出到 `previews/stage1/`，校验结果写入 `reports/stage1/VALIDATION.json`。预览及审查板由 Inkscape 原生 SVG 渲染。

修改 `config/stage1/geometry.v1.json` 后可运行 `python3 scripts/stage1/build.py --pose P2` 只刷新 P2。此时审查板仍对应先前的合集版本。确认局部修改后执行完整重建，同步复合板和坐标表。为并行实验，可用 `--config` 与 `--out` 指向实验配置和工作目录。
