# 审查交接协议

每次完成阶段工作，Codex 必须提供下列九项；不以本地绝对路径代替仓库路径，不使用浮动 dev 链接作为唯一版本依据。

1. GitHub仓库地址：https://github.com/3387029830-dot/shunfeng （私有）。
2. 工作分支：通常为 dev，或 dev 派生的 feature 分支。
3. 最新提交：完整40位SHA；使用 git rev-parse HEAD 并核对远程头。
4. 修改摘要：目标、变更文件、视觉/技术影响、与原计划的差异。
5. 预览路径：例如 previews/geometry_contact.png；声明其属于中性测试还是已批准美术阶段。
6. SVG及原生源路径：tests/svg/neutral.svg；原生文件不存在须明确，不虚构 .af/.blend。
7. 实际运行的测试：命令、依赖版本、输入与结果路径、PASS/FAIL/BLOCKED；官方支持不得写为实测。
8. 未解决问题：软件、素材、权限、兼容性、视觉风险及影响。
9. 是否请求进入下一阶段：明确是/否、阶段名、需要谁批准；没有明确批准不得开始。

## 固定版本审查

先取得本轮完整SHA，然后用 `https://github.com/3387029830-dot/shunfeng/tree/<SHA>` 浏览整棵树，或 `.../blob/<SHA>/README.md`、`.../blob/<SHA>/previews/geometry_contact.png` 查看文件。用有权限的GitHub连接器按仓库+路径+ref=SHA读取，验证返回对象与该版本一致。若连接器无访问权，先请求授权，不以公开仓库替代，不声称已看过图片。

本地可用 git show SHA:path、git ls-tree -r SHA 和 git diff <baseline>..<SHA> 复核；这些操作本地对象已齐备时不需联网。交接中的SHA不写入其自身同一次提交（会自引用）；应在该提交后的消息/交接附件或后续提交中记录。仓库中的报告以可追溯的基线/树哈希及 git rev-parse HEAD 为准。

## 审批与回退

Codex提出PR，ChatGPT负责创意与系列审查，用户负责最终决策。PR需记录本轮固定SHA、测试、预览、源文件、风险和阶段请求。明确批准后才合并；合并后记录merge SHA。拒绝则在dev修订，不覆盖既有人工精修。不执行force push。服务器是否有强制分支保护必须另行验证，不把文本规定当作已启用保护。

本次迁移交接：工作内容仅GitHub工程初始化；不请求进入Stage1。七份报告在根目录；全部源为中性几何测试；原生设计稿不存在。最新SHA和远程验证结果由最终迁移消息提供。
