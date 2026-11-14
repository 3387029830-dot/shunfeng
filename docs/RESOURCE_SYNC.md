# 资源同步与分支规范

仓库是经过脱敏的协作事实源；本地设计软件只编辑检出的工程副本。开始前核对分支和工作树，结束后保存原生文件、更新预览、测试、提交，再按固定SHA交接。不要从下载PNG回推唯一设计源。

## 分支

- main：稳定审查基线；本次初始化允许直接建立。今后正式设计改动必须经PR与用户/规划层明确批准。
- dev：Codex日常工作分支；阶段任务可从dev派生分支。未经授权不向main直接提交/推送、不开自动合并、不强推。
- PR审批不等于下一阶段批准；是否进入Stage1必须单独明确。

本仓库有本地pre-push防误推hook，运行 `git config --local core.hooksPath .githooks` 后拦截main的普通git push。连接器API不会运行本地hook；服务器保护未启用时，必须依靠AGENTS/审查流程，不声称技术强制。克隆不会自动安装hook，需要每个工作副本明确启用。

## 文件规则

| 类型 | 同步规则 |
|---|---|
| SVG/JSON/Markdown/脚本 | 默认同步，可编辑源为优先；不提交含私人路径的运行配置 |
| PNG | .gitignore只允许本轮选定8张诊断图；新增预览先审查、调整白名单 |
| PDF | 仅有价值且经过检查的诊断/交付文件；本轮PDF仅光栅诊断 |
| 日志/测试证据 | 保留命令、exit、错误类别和结果；私人路径用${USER_HOME}/${BUILD_HOME}替代；历史证据放reports/stage0 |
| 缓存/临时/认证 | 不提交__pycache__、fontcache、node_modules、.venv、.env、密钥、备份和压缩包 |
| Affinity/Blender原生文件 | 当前无此类文件，默认忽略，先评估大小/变化频率/LFS配额再有意识纳入 |

## LFS与配额

系统PATH中git lfs不可用；Codex捆绑git-lfs 3.7.1可直接运行。本轮不安装、不运行git lfs install、不启用过滤器，也不添加大型原生资产。基线仅约0.4MB，最大文件约46KB，普通Git即可；以reports/MIGRATION_CHECKS.json实际统计为准。

未来加入二进制前，记录文件大小/预计版本增长、GitHub账号当时的LFS额度与计费规则、审查方能否拉取。配额本轮未查询，不能承诺免费额度。经用户批准后再 `git lfs track` 指定扩展或文件并提交.gitattributes；使用现有捆绑LFS时需确保每个协作者的git能找到该可执行文件，不更改全局配置。缺LFS或额度不明时不强制add绕过忽略规则。

## 双向同步边界

普通git命令需要本机GitHub认证；本轮GitHub连接器认证与Keychain凭证不同。连接器上传时逐文件校验blob SHA，tree与commit必须同本地对象一致；ref更新前读取当前头，使用expected_sha防止覆盖别人提交。发现远程已变更则停止、取回差异、正常合并，不强推。

私人凭证只通过用户配置的认证渠道，不能贴到聊天/README/remote URL。私有仓库只对已授权账户可读，需确认ChatGPT审查连接器的仓库权限。原始未脱敏日志继续留本机，不上传到issues或外部附件。
