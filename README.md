# harness-builder

[English](README.en.md)

为其他项目**创建、改进、重构 agent harness** 的 Agent Plugins v1.0.0 插件。
它把《软件工程 Agent Harness 通用构建规范》落成一组可装进 Claude Code、
Codex、Antigravity 的技能：两个手动唤起的入口（创建 / 改进）、一本方法论手册、
六个按 harness 层划分的构建技能、平台生命周期技能、项目 skill 编写技能，以及规范驱动开发（SDD）的
方法论与三种载体（OpenSpec、Spec-Kit、轻量 SPEC.md）。另有一个只读的验证
子代理，在干净上下文中回读刚构建的 harness（仅 Claude Code）。

每一处决策都向用户确认：插件给出推荐项和理由，不替用户选择。

## 安装

- **Claude Code**：`/plugin install harness-builder --marketplace hoshiori-dev/harness-builder`
  （Claude Code 2.1.275 及以上一步完成；更早版本先 `/plugin marketplace add hoshiori-dev/harness-builder`
  再安装）；本地开发用 `claude --plugin-dir .`。
- **Codex**：`codex plugin marketplace add hoshiori-dev/harness-builder`，再
  `codex plugin add harness-builder@harness-builder`。
- **Antigravity**：`agy plugin install https://github.com/hoshiori-dev/harness-builder`。

技能内附带的脚本与模板资产使用 Python（PEP 723，优先标准库），有 uv 时用
`uv run`，没有时用系统 `python3` 也能运行；目标项目无需安装 Deno。

## 技能

| 技能 | 调用 | 说明 |
|---|---|---|
| [`harness-create`](skills/harness-create/SKILL.md) | 手动 | 为项目创建第一套 harness：调研仓库、区分绿地/棕地、问五个变量、六层逐层定档并确认、计划获批后按层构建，最后干净上下文回读与复审。 |
| [`harness-improve`](skills/harness-improve/SKILL.md) | 手动 | 审计、修补、减薄、硬化或迁移既有 harness：先审计出缺陷清单，由用户决定修补还是重建，再按层交给构建技能。 |
| [`harness-architecture`](skills/harness-architecture/SKILL.md) | 自动 | 方法论手册：五个变量、上下文经济学、五种加载方式、单一事实源、熵增定律；回答“这条规则该放哪”。 |
| [`environment-building`](skills/environment-building/SKILL.md) | 自动 | 环境与沙箱层：沿用已有隔离环境，否则列选项由用户选；致命三要素分级、五项沙箱审计、控制面只读光谱、非交互环境变量。 |
| [`knowledge-routing-building`](skills/knowledge-routing-building/SKILL.md) | 自动 | 知识库与路由层：AGENTS.md（始终适用块 + 路由表 + 校验表 + Keep In Sync）、知识文件拆分、脚本封装与降噪。 |
| [`project-skill-building`](skills/project-skill-building/SKILL.md) | 自动 | 为目标项目编写、改进、诊断项目 skill：先定测试、描述与正文层级、剪枝、附带 lint_skill.py、子代理行为测试。 |
| [`hard-boundary-building`](skills/hard-boundary-building/SKILL.md) | 自动 | 硬边界层：按档位配置格式化、机密扫描、lint、类型检查、测试与 CI 闸门；自定义检查报错即路由；管理脚本语言由用户确认。 |
| [`authority-building`](skills/authority-building/SKILL.md) | 自动 | 授权边界层：按可逆性分类动作、两端审批与待决列表、固定拒绝清单与用户确认的放行清单（无询问条目）、检查点提交规则。 |
| [`spec-completion-building`](skills/spec-completion-building/SKILL.md) | 自动 | 规范与完成标准层：定级别与载体、四个完成必答、审批闸门模式、交付规范合同并交给对应载体技能。 |
| [`entropy-building`](skills/entropy-building/SKILL.md) | 自动 | 熵管理层：纠错报告落地、Keep In Sync 表或同步 skill、交付 check_harness.py 自检进 CI、周期清理与减薄。 |
| [`platform-lifecycle-building`](skills/platform-lifecycle-building/SKILL.md) | 自动 | 平台生命周期层（GitHub / GitLab）：最小实体集与删除测试、分支模型与合并方式、表单模板标签、发布闸门、项目工作流 skill。 |
| [`spec-driven-development`](skills/spec-driven-development/SKILL.md) | 自动 | 规范驱动开发方法论：八步循环、规范质量规则、审批包、与 issue / PR 的分工、接手既有代码不回填规范。 |
| [`openspec-workflow`](skills/openspec-workflow/SKILL.md) | 自动 | OpenSpec 载体：审批包、请求内归档、awaiting-archive 闸门、状态标签，以及 GitHub / GitLab 自动化。 |
| [`spec-kit-workflow`](skills/spec-kit-workflow/SKILL.md) | 自动 | Spec-Kit 载体：spec + plan 审批包、全部任务勾选即完成、声明式锁定、状态标签与平台自动化。 |
| [`lightweight-spec-workflow`](skills/lightweight-spec-workflow/SKILL.md) | 自动 | 轻量载体：小改动用 Plan Mode，中等改动用 SPEC.md / PLAN.md，带完成必答、场景、非目标与预授权动作。 |

另有 Claude Code 子代理 [`harness-verifier`](com.anthropic.claude-code/agents/harness-verifier.md)：只读，在干净上下文中回读刚构建的 harness 并逐文件报告缺口。

## 文档

方法论文档与各技能的使用说明发布在 <https://hoshiori-dev.github.io/harness-builder/>（中文）。

## 开发

打开 dev container，`just check` 跑全部检查。流程、规范与权限约定见
[AGENTS.md](AGENTS.md)（agent 入口）与 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可

Apache-2.0，见 [LICENSE](LICENSE)。
