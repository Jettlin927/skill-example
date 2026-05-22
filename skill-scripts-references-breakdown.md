# Skill 中 scripts 和 references 的设计拆解

## 核心判断

一个好的 skill 不应该只是 `SKILL.md`。`SKILL.md` 负责告诉 Codex “什么时候触发、按什么流程做、去哪里找资源”；`references/` 负责保存不该反复塞进主说明里的领域知识；`scripts/` 负责把高频、脆弱、可验证的动作变成稳定工具。

可以用一句话判断：

> 让 AI 判断的留在 `SKILL.md`，让 AI 查阅的放进 `references/`，让机器执行的放进 `scripts/`。

## 三层职责

### 1. SKILL.md：路由和流程

`SKILL.md` 是 skill 的入口，不是知识库，也不是代码仓库。

它应该包含：

- 触发条件：用户说什么、出现什么文件、遇到什么场景时要用这个 skill。
- 总流程：先做什么，再做什么，遇到分支怎么判断。
- 资源导航：什么情况下读取哪个 reference，什么情况下运行哪个 script。
- 关键约束：必须遵守的顺序、禁止事项、验证要求。

它不适合包含：

- 大段 API 文档。
- 很长的字段说明、业务规则、示例全集。
- 每次都会重复写的 Python/JS/Bash 代码。
- 可以被脚本校验或生成的内容。

`SKILL.md` 的质量标准不是“信息最多”，而是“让另一个 Codex 能快速知道下一步该做什么”。

### 2. references/：按需加载的知识

`references/` 存的是 Codex 工作时需要理解、对照、检索的材料。它们不是自动执行的，而是在某个分支需要时才读。

适合放入 `references/` 的内容：

- API 文档、CLI 参数说明、SDK 用法。
- 数据库 schema、字段含义、业务口径。
- 公司政策、品牌规范、合同模板说明。
- 复杂流程的详细分支说明。
- 大量示例、边界案例、错误码解释。

什么时候应该拆到 `references/`：

- 内容超过 `SKILL.md` 的主流程需要。
- 只有部分任务会用到这段知识。
- 内容经常被查询，但不需要每次全部加载。
- 同一个 skill 支持多个领域、平台、文件格式或工作流。

推荐结构：

```text
my-skill/
├── SKILL.md
└── references/
    ├── api.md
    ├── schema.md
    ├── examples.md
    └── troubleshooting.md
```

`SKILL.md` 中要明确写出何时读取：

```markdown
When the user asks about invoice fields, read references/schema.md.
When an API call fails, read references/troubleshooting.md before retrying.
```

不要把 reference 做成一个“垃圾桶”。如果所有内容都塞进 `reference.md`，只是把单文件问题换了一个位置。

### 3. scripts/：稳定、可重复、可验证的动作

`scripts/` 存的是可执行工具。它的价值是把“AI 每次临时写代码”变成“机器每次稳定执行”。

适合放入 `scripts/` 的内容：

- 文件解析、格式转换、批量处理。
- schema 校验、字段检查、数据清洗。
- API 调用封装、分页拉取、重试逻辑。
- 报表生成、图片/PDF/表格渲染。
- 环境检查、权限检查、依赖诊断。
- 任何 AI 容易写错、但程序可以稳定完成的步骤。

什么时候必须考虑写 script：

- 同一段代码会被反复重写。
- 操作有明确输入输出。
- 失败模式可以被程序检测。
- 人工推理成本高，但程序执行成本低。
- 结果需要可复现。
- 任务涉及坐标、分页、编码、格式、校验、批量数据等脆弱细节。

推荐结构：

```text
my-skill/
├── SKILL.md
├── scripts/
│   ├── inspect_input.py
│   ├── transform.py
│   └── validate_output.py
└── references/
    └── workflow.md
```

脚本应该尽量满足：

- 命令行参数清晰。
- 输入输出文件明确。
- 错误信息可行动。
- 能独立运行。
- 不依赖 Codex 记住隐藏上下文。
- 有代表性样例或至少在开发时实际跑通过。

## 设计决策表

| 内容类型 | 放哪里 | 原因 |
| --- | --- | --- |
| 触发条件 | `SKILL.md` frontmatter description | Codex 只有先看到 description 才知道要不要加载 skill |
| 主流程 | `SKILL.md` | 每次触发都需要知道 |
| 分支导航 | `SKILL.md` | 决定后续读哪个文件或跑哪个脚本 |
| 详细 API 文档 | `references/` | 只有相关任务才需要 |
| 大量业务规则 | `references/` | 避免污染主上下文 |
| 重复代码片段 | `scripts/` | 不应该让 AI 每次重写 |
| 校验逻辑 | `scripts/` | 程序比自然语言稳定 |
| 模板文件 | `assets/` | 被复制或用于产出，不是给 Codex 阅读 |
| 调试手册 | `references/troubleshooting.md` | 出错时再加载 |

## 从用户任务反推资源

设计 skill 时，不要先写 `SKILL.md`。先列真实任务，再反推资源。

对每个任务问四个问题：

1. Codex 需要知道什么背景知识？
2. 哪些信息不是每次都需要？
3. 哪些步骤如果让 AI 临时写会不稳定？
4. 哪些结果可以用程序检查？

示例：

用户任务：填写 PDF 表单。

- 背景知识：PDF 表单可能是 fillable，也可能只是扫描图。
- 分支流程：先检查是否有可填字段，再决定用字段填充还是坐标标注。
- references：详细表单处理流程、坐标系统说明、异常情况。
- scripts：检查字段、提取字段、转换成图片、填充字段、生成验证图。

这类任务如果只有 `SKILL.md`，Codex 每次都要重新写 PDF 检查和坐标处理代码，效率低，也容易漂。

## 评审一个 skill 是否缺 scripts/references

可以用下面的问题快速评审：

- `SKILL.md` 是否超过很多屏，里面是否混入了大量资料？
- 是否出现“复制下面代码运行”但没有脚本文件？
- 是否有“根据情况判断很多字段/规则/API”但没有 reference？
- 是否每次调用都需要重新写解析、转换、校验代码？
- 是否有稳定输入输出，却仍然交给 AI 自由发挥？
- 是否缺少 inspect、transform、validate 三类脚本中的至少一类？
- 是否失败后只能让 AI 猜，而没有诊断脚本或 troubleshooting reference？

如果答案经常是“是”，这个 skill 大概率还停留在提示词阶段，没有完成工具化。

## 常见反模式

### 反模式 1：万能 SKILL.md

所有 API、示例、业务规则、代码都写进 `SKILL.md`。

问题：

- 上下文膨胀。
- Codex 每次都要读无关信息。
- 难以维护。
- 分支越多越不稳定。

改法：

- 主流程留在 `SKILL.md`。
- 详细文档拆到 `references/`。
- 重复执行逻辑拆到 `scripts/`。

### 反模式 2：把 script 当代码示例

`SKILL.md` 里写一大段代码，让 Codex 每次复制、改参数、运行。

问题：

- 每次复制都可能出错。
- 不同 Codex 会改出不同版本。
- 没有稳定命令接口。

改法：

- 放到 `scripts/xxx.py`。
- 在 `SKILL.md` 只保留命令：

```bash
python scripts/xxx.py <input> <output>
```

### 反模式 3：reference 没有导航

有 reference 文件，但 `SKILL.md` 没说什么时候读。

问题：

- Codex 不一定知道它存在。
- 可能读错文件，或者全部读一遍。

改法：

- 在主流程中写清楚条件：

```markdown
For OAuth errors, read references/auth.md.
For rate-limit errors, read references/rate-limits.md.
```

### 反模式 4：没有验证脚本

skill 只告诉 Codex “生成结果”，但没有办法检查结果是否正确。

问题：

- 成功与否靠模型自信。
- 错误会在用户那里才暴露。

改法：

- 加 `scripts/validate_output.py`。
- 把验证步骤写进 `SKILL.md` 的完成条件。

## 推荐的最小完整结构

对于一个真正有稳定产出的 skill，建议至少考虑：

```text
skill-name/
├── SKILL.md
├── references/
│   └── workflow.md
└── scripts/
    ├── inspect.py
    └── validate.py
```

不是每个 skill 都必须有 `scripts/` 和 `references/`，但如果一个 skill 面向的是重复性工作、文件处理、API 操作、业务规则或稳定交付，那么只写 `SKILL.md` 通常是不够的。

## 一套实用分工

可以把 skill 设计看成三个角色：

- `SKILL.md` 是项目经理：决定路线、顺序、分支和完成标准。
- `references/` 是资料库：保存需要查阅但不必每次加载的知识。
- `scripts/` 是生产线：把固定动作做快、做稳、做可验证。

同事写 skill 时，最重要的心智变化是：

> Skill 不是一份更长的提示词，而是一个可被 AI 调度的小型工具包。

