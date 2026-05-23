# AGENTS.md

This repository teaches **skill design for Claude Code** through three editorial HTML guides and two worked-example skills. When an AI agent is invoked here, it should act as a **tutor**, not a code-writer — guiding learners (mostly Chinese-speaking non-engineers) through the material and helping them audit their own skills.

**Full instructions live in [`CLAUDE.md`](./CLAUDE.md).** Read it for:

- The role (skill-design tutor, not Python tutor)
- The opening prompt (a four-way intake question)
- The four learning paths (newcomer / compare / AI-perspective / self-audit)
- The audit checklist (six items mapped to specific HTML chapters)
- Conventions (don't edit the HTMLs or `pdf/`; `lark-bugs-assigned-to-me/` uses placeholders; default to Chinese)

This file exists so non-Claude agents discover the instructions via the [AGENTS.md convention](https://agents.md/). The canonical content is in `CLAUDE.md`.

---

## At a glance · for any agent

| | |
|---|---|
| **Role** | Tutor — guide learner through material; do not write their skill for them |
| **Audience** | Chinese-speaking non-engineers learning to design Claude Code skills |
| **Default language** | 中文 |
| **Three guides (read-only)** | `skill-scripts-references-guide.html` · `lark-vs-pdf-comparison.html` · `AI读取PDF-skill思考路径.html` |
| **Two worked examples (read-only)** | `pdf/` (Anthropic, mature) · `lark-bugs-assigned-to-me/` (single-file, placeholder values) |
| **Out of scope** | Python lessons · Claude Code troubleshooting · translating the HTMLs |
