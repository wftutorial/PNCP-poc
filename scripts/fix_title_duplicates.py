"""Fix duplicate | SmartLic in Next.js page title metadata.

The root layout applies template `%s | SmartLic`, so pages that
already include `| SmartLic` in their title string get doubled:
  "Page | SmartLic | SmartLic"

This script removes ` | SmartLic` suffix from top-level title: lines,
leaving openGraph.title, twitter.title, and absolute titles untouched.
"""
import re
import os

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "app")

# Patterns that indicate we've entered a nested block where title: is NOT the main title
NESTED_BLOCK_PATTERN = re.compile(r"^\s+(openGraph|twitter|alternates)\s*:")

# Title line with | SmartLic suffix (template literal or plain string)
TITLE_WITH_BRAND = re.compile(r'(\s*\|\s*SmartLic)([`\'"])')

changes = []

for root, dirs, files in os.walk(FRONTEND_DIR):
    dirs[:] = [d for d in dirs if d not in ["node_modules", ".next", "__pycache__"]]
    for fname in files:
        if not fname.endswith((".tsx", ".ts")):
            continue

        path = os.path.join(root, fname)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                lines = fp.readlines()
        except Exception:
            continue

        new_lines = []
        in_nested = False
        nested_depth = None
        modified = False

        for i, line in enumerate(lines):
            # Detect entering openGraph/twitter/alternates block
            m = NESTED_BLOCK_PATTERN.match(line)
            if m:
                in_nested = True
                nested_depth = len(line) - len(line.lstrip())
            elif in_nested and line.strip():
                curr_indent = len(line) - len(line.lstrip())
                # Exit nested block: back to same/lower indentation AND a new property
                if (
                    curr_indent <= nested_depth
                    and not line.strip().startswith("}")
                    and re.match(r"^\s+\w", line)
                    and not NESTED_BLOCK_PATTERN.match(line)
                ):
                    in_nested = False
                    nested_depth = None

            # Only modify top-level title: lines
            is_title_line = bool(re.match(r"^\s{1,8}title\s*:", line))
            is_absolute = "absolute" in line

            if is_title_line and not in_nested and not is_absolute:
                new_line = TITLE_WITH_BRAND.sub(r"\2", line)
                if new_line != line:
                    rel = os.path.relpath(path, os.path.join(FRONTEND_DIR, ".."))
                    changes.append(
                        f"{rel}:{i+1}\n  BEFORE: {line.rstrip()}\n  AFTER:  {new_line.rstrip()}"
                    )
                    line = new_line
                    modified = True

            new_lines.append(line)

        if modified:
            with open(path, "w", encoding="utf-8") as fp:
                fp.writelines(new_lines)

print(f"Files modified: {len(set(c.split(':')[0] for c in changes))}")
print(f"Total changes:  {len(changes)}\n")
for c in changes:
    print(c)
    print()
