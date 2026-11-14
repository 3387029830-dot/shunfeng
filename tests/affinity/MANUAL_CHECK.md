# Affinity 文件交换人工补测单

状态：**全部待执行**。没有安装软件、原生文件或GUI截图。本表是操作方案，不是成功记录。请使用原始neutral.svg副本，测试产生文件留在本目录，不动原输入。

1. 记录 App名称、版本、macOS、实际安装路径；在 About 截图，明确新版与V2。记录实际原生扩展名，不凭SDK版本推断。
2. File > Open neutral.svg。截图画面及Layers面板。核对circle、rectangle、bezier、clipped、chinese；展开三层g。记录层名称/顺序/分组是否保留；g保留与图层语义保留分开判断。
3. 用Node Tool拖动bezier单个节点，确认节点可编辑；矩形改色。Undo后再核对整体，不能将整图作为单张位图通过此项。
4. 用Text Tool将“中文测试”改成“中文复测”。检查文本仍为活字、字距、标点、字号与字形；记录字体名称/版本及缺字或替换提示。
5. 检查55%透明矩形和圆形裁剪，展开裁剪关系；临时关闭clip确认确为裁剪，不是预栅格图。与previews/neutral.png并排目视，记录可见差异。mask未在输入中出现，不应勾选mask通过。
6. Save As保存原生exchange_test（按实际扩展）；关闭再打开，重新测试节点和文本可编辑。记录文件路径、大小、截图和应用版本。
7. **另建文档**，用Place导入neutral_link_test.svg副本，尝试选择Linked。记录资源管理器实际状态；若SVG不允许链接，记失败/不支持，不改用PNG来冒充通过。
8. 将链接测试副本中bezier的d替换为neutral_patched.svg中的值（仅副本），在Resource Manager确认Modified/Update；更新后曲线变化且位置/尺寸/其他组不变。保存并关闭重开，测试链接仍可解析。移动测试文件夹后验证Relink/Collect，记录字体需单独处理。
9. 导出PDF（按应用可用预设，记录所有选项），单独测试文字嵌入与转曲副本。用PDF读取器/Poppler重开并回渲，检查中文、曲线、透明度、裁剪、尺寸。检查路径是否向量、页面是否整图栅格化；无需为了此项输出印刷承诺。
10. 若版本有Scripting Studio/Script Editor，先用官方文档的最小无外部依赖示例在空测试文档中创建单一路径；保存/撤销/异常分别验证，记录实际API和日志。逐项另测open/import/update/save/export，任一缺口均保留人工步骤。不接未知MCP。

每项记录：测试者、日期、软件版本、输入SHA256、实际动作、预期/实际、截图、输出SHA256、PASS/FAIL/BLOCKED。未经执行不得填写PASS。
