#!/usr/bin/env python3
import re
from pathlib import Path

CONFLICT = re.compile(r"<<<<<<< .*?\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n", re.S)


def _dedupe(seq):
    seen = set()
    out = []
    for s in seq:
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out


def merge_block(a: str, b: str) -> str | None:
    """Try to safely merge a & b; return merged or None if unsafe."""
    a_lines = [l.rstrip() for l in a.strip("\n").splitlines()]
    b_lines = [l.rstrip() for l in b.strip("\n").splitlines()]

    # 1) Identical ignoring whitespace
    if "".join(a_lines) == "".join(b_lines):
        return "\n".join(a_lines) + "\n"

    # 2) Pure import sections → union + sort + stable grouping
    if all(l.startswith(("import ", "from ")) or l == "" for l in a_lines + b_lines):
        imports = _dedupe(a_lines + b_lines)
        imports = [l for l in imports if l]  # drop empties
        imports.sort()
        return "\n".join(imports) + "\n"

    # 3) Duplicate FastAPI router include → keep one
    both = "\n".join(a_lines + [""] + b_lines)
    if "app.include_router" in both:
        # Keep exactly one include_router block per distinct router line
        def blocks(lines):
            buf, blocks = [], []
            for l in lines + [""]:
                buf.append(l)
                if l.strip().startswith(")") or l.strip() == "":
                    if "app.include_router" in "\n".join(buf):
                        blocks.append("\n".join(buf).strip("\n"))
                    buf = []
            return blocks

        ablocks = blocks(a_lines)
        bblocks = blocks(b_lines)
        merged = _dedupe(ablocks + bblocks)
        # If nothing recognized, bail
        if merged:
            return "\n\n".join(merged) + "\n"

    # 4) For small additive lists/dicts: keep both unique lines
    if len(a_lines) <= 10 and len(b_lines) <= 10:
        union = _dedupe(a_lines + b_lines)
        return "\n".join(union) + "\n"

    return None  # unsafe


def resolve_file(path: Path) -> bool:
    text = path.read_text()
    changed = False

    def repl(m):
        nonlocal changed
        merged = merge_block(m.group(1), m.group(2))
        if merged is None:  # leave unresolved
            return m.group(0)
        changed = True
        return merged

    new = CONFLICT.sub(repl, text)
    if changed:
        path.write_text(new)
    return changed


def main():
    root = Path(".")
    changed_any = False
    for p in root.rglob("*.py"):
        txt = p.read_text(errors="ignore")
        if "<<<<<<<" in txt and ">>>>>>>" in txt:
            if resolve_file(p):
                print(f"resolved {p}")
                changed_any = True
    if not changed_any:
        print("no python conflicts resolved")


if __name__ == "__main__":
    main()
