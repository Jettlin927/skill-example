---
name: distill-skill-design
description: Use this skill when the user wants a 省流版 / TL;DR of the skill-design philosophy from this repo, installed into their global AI agent config so future sessions inherit it. Triggers when the user says any of "省流版", "TL;DR", "总结 skill 设计原则", "把这套思路装到我的 AI", "把 skill 设计原则写到我的 claude.md / agents.md", "install skill design rules", "extract philosophy". Works cross-platform (macOS, Linux, Windows).
---

# Distill Skill Design

## 这个 skill 做什么

把本仓库三件 HTML 讲义里的 skill 设计原则**压成一份 TL;DR**，写入用户的**全局** AI agent 配置文件——这样他以后每次开 Claude Code 或 Codex，都会带着这套原则，不用每次重新解释。

TL;DR 内容存在 `references/skill-design-tldr.md`，这份 SKILL.md 只负责编排流程。

## 流程

### Step 1 · 检测候选文件

跑检测脚本，拿到候选文件的存在状态、大小、可写性：

```bash
python3 scripts/detect_target.py
```

> **Windows 用户**：如果 `python3` 不在 PATH，用 `python scripts/detect_target.py` 或 `py -3 scripts/detect_target.py`。脚本内部用 `pathlib.Path.home()` 解析路径，**不依赖** `~` 展开，所以两种系统行为一致。

候选文件：

| 候选 | macOS / Linux | Windows |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `%USERPROFILE%\.claude\CLAUDE.md` |
| Codex | `~/.codex/AGENTS.md` | `%USERPROFILE%\.codex\AGENTS.md` |

脚本输出 JSON，例如：

```json
{
  "platform": "darwin",
  "home": "/Users/jettlin",
  "candidates": [
    {"name": "claude", "path": "/Users/jettlin/.claude/CLAUDE.md", "exists": true,  "size_bytes": 1234, "writable": true},
    {"name": "codex",  "path": "/Users/jettlin/.codex/AGENTS.md",   "exists": false, "size_bytes": 0,    "writable": true}
  ]
}
```

### Step 2 · 问用户写到哪一个

把两个候选的**完整路径**和**当前状态**摆给用户看，让他选。

判断规则：
- 只有一个存在 → 默认选它，但仍然要确认一句"写到 X 可以吗？"。
- 两个都存在 → 让用户挑。
- 两个都不存在 → 让用户决定要不要新建（哪个）。
- 任一不可写（权限问题） → 不要硬上，告诉用户哪里出了问题。

### Step 3 · 安装

调安装脚本，把 `references/skill-design-tldr.md` 的内容用标记块写入目标：

```bash
python3 scripts/install_tldr.py <目标路径> references/skill-design-tldr.md
```

脚本行为：

| 目标文件状态 | 动作 |
|---|---|
| 不存在 | 创建（连同父目录），只放 TL;DR 块 |
| 存在但没有标记块 | 在末尾追加 TL;DR 块（前面留一个空行） |
| 已经有标记块 | 只替换标记之间的内容，块外的内容不动 |

标记块长这样（HTML 注释，markdown 里不可见，但能被脚本精准定位）：

```markdown
<!-- BEGIN skill-design-tldr · from github.com/Jettlin927/skill-example -->
... TL;DR 内容 ...
<!-- END skill-design-tldr -->
```

脚本输出 JSON 状态：

```json
{"ok": true, "action": "created" | "appended" | "replaced", "target": "...", "lines_in_block": 42}
```

### Step 4 · 确认

把脚本返回的关键信息复述给用户：
- 写到了哪个文件
- 是新建 / 追加 / 替换中的哪一种
- 一句话："以后这台机器上的 AI 都会看到这套原则。"

## 重要约定

- **只动用户的全局 agent 配置**（`~/.claude/CLAUDE.md` 或 `~/.codex/AGENTS.md`）。不要动当前项目里的 `CLAUDE.md` / `AGENTS.md`——那是项目级的，跟全局是两件事。
- **TL;DR 内容固定在 `references/skill-design-tldr.md`**。如果用户想改内容（增删条款），改的是这个文件，然后再跑一遍 skill；不要在脚本里硬编码内容。
- **不要走联网**。所有内容都是仓库自带的，离线可用。

## 不在范围内

- 同步用户已有的 CLAUDE.md / AGENTS.md 的其他内容（只管标记块之间）。
- 卸载 / 删除标记块（如果以后要做卸载，再加一个 `scripts/uninstall_tldr.py`）。
- 多机器同步（用户自己用 git / dotfiles 管理）。
