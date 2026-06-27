from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from memories_core import DEFAULT_MEMORIES_ROOT, body_preview, recent_memories, recall_memories, write_memory

SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_ROOT / "mnemoweave.json"
MEMORY_ROOT_ENV = "AGENT_MEMORY_ROOT"
MEMORY_PROJECT_ENV = "AGENT_MEMORY_PROJECT"


def load_manifest() -> dict[str, Any]:
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def resolve_root(args: argparse.Namespace) -> Path:
    if args.root:
        return Path(args.root).expanduser()
    env_root = os.environ.get(MEMORY_ROOT_ENV)
    if env_root:
        return Path(env_root).expanduser()
    manifest_root = load_manifest().get("memory_root")
    if manifest_root:
        return Path(manifest_root).expanduser()
    return DEFAULT_MEMORIES_ROOT


def resolve_project(args: argparse.Namespace) -> str | None:
    if args.project:
        return args.project
    return os.environ.get(MEMORY_PROJECT_ENV) or None


def preview_command(args: argparse.Namespace) -> int:
    root = resolve_root(args)
    project = resolve_project(args)
    memories = recent_memories(root, args.days, project=project)
    if not memories:
        project_suffix = f" for project {project}" if project else ""
        print(f"No memories in last {args.days} days{project_suffix}.")
        return 0

    heading = f"--- Recent Memories (last {args.days} days"
    heading += f", project: {project}" if project else ""
    heading += ") ---"
    print(heading)
    for memory in memories:
        project_label = f" | project: {memory.project}" if memory.project else ""
        print(f"[{memory.created}] {memory.agent} | {memory.type}{project_label}")
        print(f"  summary: {memory.summary}")
        print(f"  entities: {', '.join(memory.entities)}")
        print()

    entity_count = Counter(entity for memory in memories for entity in memory.entities)
    if entity_count:
        print("--- Frequent Entities ---")
        for entity, count in entity_count.most_common():
            print(f" {entity} ({count} times)")
    return 0


def recall_command(args: argparse.Namespace) -> int:
    root = resolve_root(args)
    project = resolve_project(args)
    memories = recall_memories(root, query=args.query, entity=args.entity, limit=args.limit, project=project)
    payload: list[dict[str, Any]] = [
        {
            "file": str(memory.path),
            "filename": memory.filename,
            "type": memory.type,
            "agent": memory.agent,
            "summary": memory.summary,
            "created": memory.created,
            "project": memory.project,
            "entities": ", ".join(memory.entities),
            "body_preview": body_preview(memory.body),
        }
        for memory in memories
    ]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def memorize_command(args: argparse.Namespace) -> int:
    root = resolve_root(args)
    project = resolve_project(args)
    path = write_memory(
        root=root,
        memory_type=args.type,
        agent=args.agent,
        entities=args.entities or [],
        summary=args.summary,
        body=args.body,
        project=project,
    )
    print(f"memorized: {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MnemoWeave memory CLI")
    parser.add_argument("--root", help=f"Memory root directory. Overrides {MEMORY_ROOT_ENV} and manifest memory_root.")
    parser.add_argument("--project", help=f"Project scope. Overrides {MEMORY_PROJECT_ENV}.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview = subparsers.add_parser("preview", help="Preview recent memories")
    preview.add_argument("--days", type=int, default=7)
    preview.set_defaults(func=preview_command)

    recall = subparsers.add_parser("recall", help="Search memories")
    recall.add_argument("--query")
    recall.add_argument("--entity")
    recall.add_argument("--limit", type=int, default=20)
    recall.set_defaults(func=recall_command)

    memorize = subparsers.add_parser("memorize", help="Write a new memory")
    memorize.add_argument("--type", required=True, choices=["observation", "task_complete"])
    memorize.add_argument("--agent", required=True)
    memorize.add_argument("--entities", nargs="*", default=[])
    memorize.add_argument("--summary", required=True)
    memorize.add_argument("--body", required=True)
    memorize.set_defaults(func=memorize_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
