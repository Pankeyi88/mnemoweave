# MnemoWeave

Agent-agnostic persistent memory weave. Drop it into your AI agent's skill directory and give it durable memory — no databases, no dependencies, just Markdown files.

```
~/.agent/
└── skills/
    └── mnemoweave/    ← clone here
```

## Quick Start

```bash
# Install for your agent
git clone https://github.com/Pankeyi88/mnemoweave.git ~/.agent/skills/mnemoweave
```

That's it. Your agent will automatically pick up the `SKILL.md` and `mnemoweave.json` and start using `preview` / `recall` / `memorize` as needed.

## How It Works

| Command | What the agent does |
|---------|-------------------|
| `preview` | Check recent context at session start |
| `recall` | Search past memories before answering |
| `memorize` | Save important context after completing a task |

All memories live as plain `.md` files:

```
E:\_memories\
├── 2026-06-27-001.md
├── 2026-06-27-002.md
└── ...
```

Each file is a Markdown with YAML frontmatter — readable by any tool:

```markdown
---
type: observation
agent: claude
summary: Discovered useful pattern
created: 2026-06-27T12:00:00+08:00
project: my-project
entities:
  - Python
  - API
---
Detailed observations in markdown...
```

## Configuration

Configure memory root in order of priority:

1. `--root` or `AGENT_MEMORY_ROOT` env var
2. `mnemoweave.json` → `memory_root`
3. Default: `E:\_memories`

Scope memories to a project via `--project` or `AGENT_MEMORY_PROJECT`.

## Compatible Agents

Works with any AI agent that supports custom skills — opencode, Claude Code, Cline, Goose, and others.

## License

MIT
