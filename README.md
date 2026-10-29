# harness-builder

[English](README.en.md)

为其他项目**创建、改进、重构 agent harness** 的 Agent Plugins v1.0.0 插件。
它把《软件工程 Agent Harness 通用构建规范》落成一组可装进 Claude Code、
Codex、Antigravity 的技能：两个手动唤起的入口（创建 / 改进）、一本方法论手册、
六个按 harness 层划分的构建技能、平台生命周期技能，以及规范驱动开发（SDD）的
方法论与三种载体（OpenSpec、Spec-Kit、轻量 SPEC.md）。另有一个只读的验证
子代理，在干净上下文中回读刚构建的 harness（仅 Claude Code）。

每一处决策都向用户确认：插件给出推荐项和理由，不替用户选择。

## 安装

- **Claude Code**：`/plugin marketplace add hoshiori-dev/harness-builder`，再安装
  `harness-builder`；本地开发用 `claude --plugin-dir .`。
- **Codex**：`codex plugin marketplace add hoshiori-dev/harness-builder`，再
  `codex plugin add harness-builder@harness-builder`。
- **Antigravity**：`agy plugin install https://github.com/hoshiori-dev/harness-builder`。

技能内附带的脚本与模板资产使用 Python（PEP 723，优先标准库），有 uv 时用
`uv run`，没有时用系统 `python3` 也能运行；目标项目无需安装 Deno。

## 技能

| 技能 | 调用 | 说明 |
|---|---|---|

## 文档

方法论文档与各技能的使用说明发布在 <https://hoshiori-dev.github.io/harness-builder/>（中文）。

## 开发

打开 dev container，`just check` 跑全部检查。流程、规范与权限约定见
[AGENTS.md](AGENTS.md)（agent 入口）与 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可

Apache-2.0，见 [LICENSE](LICENSE)。
