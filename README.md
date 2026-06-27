# MnemoWeave

Agent-agnostic persistent memory weave. Each memory is a standalone Markdown file with YAML frontmatter — no database, no dependencies.

```
python scripts/memory.py memorize --type observation --agent claude --entities Python API \
  --summary "Discovered pattern" --body "Details..."
python scripts/memory.py recall --query "pattern"
python scripts/memory.py preview
```

## Features

- **Zero deps** — Python standard library only
- **Plain files** — Memories are `.md` files, readable by anything
- **Agent-agnostic** — Works with any AI agent
- **Project scoping** — Isolate memories per project
- **Configurable root** — CLI flag, env var, or manifest file

## Quick Start

```bash
# Write a memory
python scripts/memory.py memorize --type task_complete --agent codex \
  --entities PyTorch CUDA \
  --summary "Completed LSTM experiment" \
  --body "Ran time series experiment using PyTorch with CUDA."

# Recall
python scripts/memory.py recall --query "LSTM"

# Preview recent (last 7 days)
python scripts/memory.py preview

# Preview with project scope and custom time window
python scripts/memory.py --project my-project preview --days 30
```

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `preview` | Show recent memories (default: last 7 days) |
| `recall` | Search memories by query text and/or entity |
| `memorize` | Write a new memory |

### Global Options

| Flag | Env Var | Description |
|------|---------|-------------|
| `--root` | `AGENT_MEMORY_ROOT` | Memory storage directory |
| `--project` | `AGENT_MEMORY_PROJECT` | Project scope filter |

### Storage Resolution

Memory root is resolved in this order:
1. `--root` CLI flag
2. `AGENT_MEMORY_ROOT` environment variable
3. `mnemoweave.json` → `memory_root` field
4. Default: `E:\_memories`

## Storage Format

```
E:\_memories\
├── 2026-06-27-001.md
├── 2026-06-27-002.md
└── ...
```

Each file:
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

## File Structure

```
mnemoweave/
├── README.md
├── SKILL.md
├── mnemoweave.json
├── scripts/
│   ├── memory.py          # CLI entrypoint
│   └── memories_core.py   # Core logic
└── .gitignore
```

## License

MIT
