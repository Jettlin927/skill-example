# Skill 拆解 · Skill Design by Example

> 把单文件 SKILL.md 拆成 `SKILL.md` + `references/` + `scripts/`——三件中文 HTML 讲义 + 两个对照样本，给非程序员同事讲明白 skill 怎么设计才能让 AI 用得顺。

## 谁会用得上

- 写过或想写 [Claude Code](https://claude.com/claude-code) skill 但不会写代码的同事（PM / 运营 / 内容 / 设计 / QA）
- 想把自己的"长 SKILL.md"拆得更结构化的工程师
- 给团队做 skill 设计培训的人——三件 HTML 是 1–2 小时的现成讲义

## 两种用法

### 路径 A · 直接读（不需要 AI）

在浏览器里依次打开：

1. **`skill-scripts-references-guide.html`** — 主指南（10 章）。从"为什么要分层"讲到"脚本到底要负责什么"。
2. **`lark-vs-pdf-comparison.html`** — 对照册（6 章 + 2 个动手练习）。把单文件 skill 和分层 skill 并排过一遍。
3. **`AI读取PDF-skill思考路径.html`** — AI 视角（5 章）。从"AI 怎么读 skill"反推"我应该怎么写"。

### 路径 B · 让 Claude Code 当导师

```bash
git clone https://github.com/Jettlin927/skill-example.git
cd skill-example
claude
```

然后说一句"我想学 skill 设计"。Claude 会读 [`CLAUDE.md`](./CLAUDE.md)、问你的起点，然后按四条路径之一牵着你过——读 HTML、做练习、最后审计你自己的 skill。

## 仓库结构

| 路径 | 是什么 |
|---|---|
| `skill-scripts-references-guide.html` | 主指南 · 10 章 |
| `lark-vs-pdf-comparison.html` | 对照册 + 2 个动手练习 |
| `AI读取PDF-skill思考路径.html` | AI 视角的四层思考路径 |
| `pdf/` | Anthropic 官方 PDF skill（成熟样板） |
| `lark-bugs-assigned-to-me/` | 单文件 skill（重构前样板，值已脱敏） |
| `skill-scripts-references-breakdown.md` | 主指南的原始拆解笔记 |
| `pdf-skill-script-breakdown.md` | PDF skill 脚本职责拆解笔记 |
| [`CLAUDE.md`](./CLAUDE.md) · [`AGENTS.md`](./AGENTS.md) | 给 AI 导师用的指令 |

## 脱敏说明

`lark-bugs-assigned-to-me/` 是真实在用的飞书 bug 查询 skill。这个仓库里的 SKILL.md 把内部 token、wiki URL 全部替换成了 `<YOUR_FEISHU_APP_ID>` 这类占位符——拿来读结构可以，要真用得自己替换。

## 许可

- 三件 HTML、拆解笔记、`CLAUDE.md` / `AGENTS.md`：版权归 Jettlin 所有，允许内部学习与转发，商用请联系。
- `pdf/` 来自 Anthropic，遵循其 [`LICENSE.txt`](./pdf/LICENSE.txt)。
