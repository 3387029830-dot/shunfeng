# SF-City-Advertising

顺丰同城三联广告的专业设计工程。**Stage 0 已批准。Stage 0.5 已验证中性工具链，尚未批准 Stage 1。**

[Stage 0.5 验收报告](reports/stage05/REVIEW.md)

远程仓库：[3387029830-dot/shunfeng](https://github.com/3387029830-dot/shunfeng)（私有）。用户提供的仓库名为 shunfeng；本项目名称仍为 SF-City-Advertising。

## 审查入口

[迁移报告](MIGRATION_REPORT.md) · [版本交接](docs/REVIEW_HANDOFF.md) · [资源同步规范](docs/RESOURCE_SYNC.md)

Stage 0 七份必需文档：[环境审计](WORKFLOW_AUDIT.md)、[工具比较](TOOL_COMPARISON.md)、[工作流架构](WORKFLOW_ARCHITECTURE.md)、[测试报告](TEST_REPORT.md)、[执行规范](AGENTS.md)、[路线](ROADMAP.md)、[阻断项](BLOCKERS.md)。另见[研究来源](docs/RESEARCH.md)、[风险登记](docs/RISKS.md)、[原任务书](docs/USER_TASK_V1.md)。

原 Stage 0 报告保留历史结论，其中“未初始化 Git / 未推送”等表述描述迁移前状态。当前 Git 协作规范以本 README、MIGRATION_REPORT、RESOURCE_SYNC 为准。脱敏历史证据冻结于 reports/stage0；原始未脱敏工程仍在用户本机原目录，本仓库只含迁移副本。

## 源与预览

- 配置：config/*.json；生成器：scripts/geometry.py。
- 中性 SVG：tests/svg/*.svg；[三状态预览](previews/geometry_contact.png)。
- Stage 0.5 原生 Affinity 测试文件和链接源位于 `tests/stage05/affinity/`，包含中性编辑与三画板迭代样本。
- [光栅 PDF 诊断回渲](previews/pdf_check.png)仅验证图像传递，不证明矢量/印刷导出。

## 重建（从仓库根目录执行）

最小结构重建只需要 Python 3.9+、xmllint（macOS系统已提供）：

```sh
python3 scripts/rebuild.py
```

执行生成与16项结构断言，不联网、不安装依赖。完整诊断使用已存在的 Node.js、sharp 0.35.5、Python 的 Pillow 13.0.0 / reportlab 4.4.9 / pypdf 6.21.4，以及 pdftoppm：

```sh
python3 scripts/rebuild.py --full
```

用对应 Python 可执行替换 python3；Node 通过 SF_NODE 指定，pdftoppm 通过 SF_PDFTOPPM 指定；若 sharp 不在当前 Node 模块搜索路径，用 SF_SHARP_MODULE 指向已安装的 sharp 模块。所有变量由本机环境提供，禁止提交私人绝对路径或认证信息。不自动安装任何依赖。缺少依赖应记录阻断，不能记通过。

完整重建写入6张PNG、光栅PDF、PDF回渲与几何对照图；像素可能随字体/渲染库版本改变。中文本机字体请求为Heiti SC，字体文件不在仓库中。已运行版本见 reports/render_results.json，历史结果见 reports/stage0。PDF元数据应避免私人作者、路径和文件附件。

## 分支与同步

main 是稳定审批分支，初始基线例外由本次迁移授权；后续 Codex 工作在 dev 或 dev 派生分支，完成后提交 PR 审查，未经明确批准不合入 main，不强推，不自动合并。提交固定SHA再交接，不能只链接浮动分支。

迁移基线通过 GitHub 连接器传输。Stage 0.5 已由用户授权 GitHub CLI HTTPS 登录，凭证保存在 macOS 钥匙串，仓库本地配置凭证助手。远程测试走派生分支。

[REVIEW_HANDOFF](docs/REVIEW_HANDOFF.md)定义所有阶段交接字段；私有仓库要求审查方账号/连接器被授权。版本可定位不等于任意ChatGPT会话自动拥有私有仓库访问权。
