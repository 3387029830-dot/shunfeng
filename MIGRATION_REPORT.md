# GitHub迁移报告

本轮仅迁移Stage0及建立协作制度，Stage1未批准、未启动。

- 仓库： https://github.com/3387029830-dot/shunfeng 。用户提供此地址，已由连接器确认private及admin/push/pull权限；未重复建仓、未改为公开。
- 仓库已存在一条Initial commit，README仅为“# shunfeng”；保留该历史，本轮完整README替换占位文本。首次create_file因已存在README返回422，未产生修改；随后读取确认后改用Git Data更新。
- 原始Stage0工程保持不变，原清单58个文件的SHA256全部核对通过。迁移副本包含七份报告、配置、脚本、SVG、8张选定PNG和光栅诊断PDF。
- 私人home路径用${USER_HOME}/${BUILD_HOME}替代；历史日志的错误类别、退出状态、输入输出关系保留。reports/REDACTION_MAP.json记录原始及脱敏哈希，reports/STAGE0_ORIGINAL_MANIFEST.json是原工程历史清单，不是当前文件哈希。
- 渲染脚本不再硬编码本机依赖路径，改用SF_NODE/SF_SHARP_MODULE/SF_PDFTOPPM；默认从本机已有环境发现依赖。没有安装任何工具或包。
- 已实际运行README最小结构重建和完整诊断：16项结构断言通过、6张SVG转PNG、光栅PDF读回与Poppler回渲、像素检查和几何对照图生成完成。原目标软件兼容性阻断保持不变。
- 当前文件远小于大型资产规模，未启用LFS过滤器或付费服务。系统PATH缺git-lfs，Codex捆绑版本3.7.1可运行；无.af/.blend原生设计文件，未来需检查配额后再采用LFS。
- main为稳定基线，dev为工作分支；后续正式设计变更需PR审查批准。本地pre-push hook用于防误推main；服务器分支保护经分支元数据确认未启用，不声称已技术强制。
- 本机Git凭证助手无GitHub认证；连接器认证可用。同步采用GitHub Git Data API，非本机git push命令；普通CLI的远程认证仍由用户后续配置。未导出、复制或提交令牌。

远程写入之后的SHA、分支和固定版本文件读取验证将记录在reports/REMOTE_VERIFICATION.json（若当前提交尚无该文件，使用完成后的交接消息/外部完成报告，不把计划当成已执行）。文件内记录某次已验证提交，最终交接SHA可能是包含该验证记录的后续提交，以最终消息为准。

## 下一步

ChatGPT/用户按固定SHA审查Stage0与迁移制度；如需强制服务器保护，须确认GitHub账户方案与权限后另行启用，不自动付费。不请求进入Stage1。


## 已完成远程验证及重建修复

首个完整基线提交为 `82ca75637b4446ed02b3a5930048adbc3445fc05`，其树 `db93cb4f47d7ab5730189b3ca6e8d1fd1f6d666c` 与本地一致：91条文件路径、模式和blob SHA逐项相等。main/dev已写入该基线。七份报告、README、交接协议、SVG及一张PNG均从远程按固定SHA实际读取成功。分支API确认protected=false。

本地对象通过git fsck；远程初始签名提交及API提交已精确导入本地，SHA匹配，初始化历史保留。当前工作分支dev，origin/dev跟踪已设置，main误推hook已实测拦截。认证仍是连接器传输，不是本机git push/pull认证。

隔离克隆完整重建发现：所有图形测试通过，但旧PDF脚本把绝对图片路径参与内部对象命名，跨目录PDF字节不一致。迁移收尾改用ReportLab ImageReader按图片内容命名；在两个不同目录重建后，PDF和回渲PNG均字节一致。原Stage0证据未改。此修复只涉及中性诊断导出，不涉及广告创意或美术制作。

详细结果见reports/REMOTE_VERIFICATION.json；该文件记录已验证基线和修复证据，最终收尾提交SHA在交接消息提供，避免自引用。Stage1仍未批准，不请求进入。
