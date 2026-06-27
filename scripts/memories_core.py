from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

DEFAULT_MEMORIES_ROOT = Path(r"E:\_memories")


@dataclass(frozen=True)
class Memory:
    path: Path
    filename: str
    type: str | None
    agent: str | None
    summary: str | None
    created: str | None
    project: str | None
    entities: list[str]
    body: str


def ensure_memories_dir(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)


def next_filename(root: Path, now: datetime | None = None) -> str:
    ensure_memories_dir(root)
    current = now or datetime.now().astimezone()
    today = current.strftime("%Y-%m-%d")
    max_number = 0
    for path in root.glob(f"{today}-*.md"):
        suffix = path.stem.removeprefix(f"{today}-")
        if suffix.isdigit():
            max_number = max(max_number, int(suffix))
    return f"{today}-{max_number + 1:03d}.md"


def write_memory(
    *,
    root: Path,
    memory_type: str,
    agent: str,
    entities: Iterable[str],
    summary: str,
    body: str,
    project: str | None = None,
) -> Path:
    ensure_memories_dir(root)
    path = root / next_filename(root)
    created = datetime.now().astimezone().isoformat()
    entity_lines = "\n".join(f"  - {entity}" for entity in entities if entity)
    project_line = f"project: {project}\n" if project else ""
    content = (
        "---\n"
        f"type: {memory_type}\n"
        f"agent: {agent}\n"
        f"summary: {summary}\n"
        f"created: {created}\n"
        f"{project_line}"
        "entities:\n"
        f"{entity_lines}\n"
        "---\n"
        f"{body.strip()}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def parse_memory(path: Path) -> Memory | None:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except OSError:
        return None

    if not content.startswith("---"):
        return None

    end_frontmatter = content.find("---", 3)
    if end_frontmatter < 0:
        return None

    frontmatter = content[3:end_frontmatter].strip()
    body = content[end_frontmatter + 3 :].strip()
    fields: dict[str, str] = {}
    entities: list[str] = []
    current_key: str | None = None

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-") and current_key == "entities":
            entities.append(stripped[1:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            fields[current_key] = value.strip()

    return Memory(
        path=path,
        filename=path.name,
        type=fields.get("type"),
        agent=fields.get("agent"),
        summary=fields.get("summary"),
        created=fields.get("created"),
        project=fields.get("project"),
        entities=entities,
        body=body,
    )


def parse_created(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def project_matches(memory: Memory, project: str | None) -> bool:
    if not project:
        return True
    return (memory.project or "").casefold() == project.casefold()


def all_memories(root: Path, project: str | None = None) -> list[Memory]:
    ensure_memories_dir(root)
    memories = [memory for path in root.glob("*.md") if (memory := parse_memory(path))]
    scoped = [memory for memory in memories if project_matches(memory, project)]
    return sorted(scoped, key=lambda memory: memory.created or "", reverse=True)


def recent_memories(root: Path, days: int, project: str | None = None) -> list[Memory]:
    cutoff = datetime.now().astimezone() - timedelta(days=days)
    recent: list[Memory] = []
    for memory in all_memories(root, project=project):
        created = parse_created(memory.created)
        if created and created >= cutoff:
            recent.append(memory)
    return recent


def recall_memories(
    root: Path,
    query: str | None = None,
    entity: str | None = None,
    limit: int = 20,
    project: str | None = None,
) -> list[Memory]:
    query_normalized = query.casefold() if query else None
    entity_normalized = entity.casefold() if entity else None
    results: list[Memory] = []

    for memory in all_memories(root, project=project):
        if query_normalized:
            searchable = f"{memory.summary or ''} {memory.body}".casefold()
            if query_normalized not in searchable:
                continue
        if entity_normalized:
            if not any(item.casefold() == entity_normalized for item in memory.entities):
                continue
        results.append(memory)

    if limit > 0:
        return results[:limit]
    return results


def body_preview(body: str, length: int = 200) -> str:
    return body[:length] + "..." if len(body) > length else body
