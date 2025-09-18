import subprocess, pathlib, re, sys, textwrap

def sh(cmd):
    return subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)

# Collect conflicted files (index stage 1/2/3 present)
files = sh("git ls-files -u | cut -f2 | sort -u").stdout.strip().splitlines()
files = [f for f in files if f]

if not files:
    print("::set-output name=body::No conflicts found.")
    sys.exit(0)

def extract_conflicts(path):
    p = pathlib.Path(path)
    try:
        t = p.read_text(errors="ignore")
    except Exception:
        return []
    blocks = []
    # Grab <<<<<<< … ======= … >>>>>>> blocks with a bit of context around
    pattern = re.compile(r"<<<<<<<[^\n]*\n(.*?)\n=======[^\n]*\n(.*?)\n>>>>>>>[^\n]*\n", re.S)
    for m in pattern.finditer(t):
        ours, theirs = m.group(1).rstrip(), m.group(2).rstrip()
        blocks.append((ours, theires := theirs))
    return blocks

comment = []
comment.append("### ⚠️ Merge conflicts detected\n")
comment.append("The following files have conflicts. Each block shows `OURS` vs `THEIRS`.\n")
comment.append("Reply with **Suggested changes** for the merged result under each block.\n")

for f in files:
    comment.append(f"\n#### `{f}`\n")
    blocks = extract_conflicts(f)
    if not blocks:
        comment.append("> (Conflict markers exist but couldn’t parse reliably.)\n")
        continue
    for i, (ours, theirs) in enumerate(blocks, 1):
        comment.append(f"<details><summary>Conflict {i}</summary>\n\n")
        comment.append("**OURS**:\n")
        comment.append("```diff\n" + ours + "\n```\n")
        comment.append("**THEIRS**:\n")
        comment.append("```diff\n" + theirs + "\n```\n")
        # Empty suggestion block the agent can fill in
        merged_hint = textwrap.dedent("""\
        <!-- Replace the code block below with a GitHub Suggested Change
        that represents the correct merged content for this conflict. -->
        """)
        comment.append(merged_hint)
        comment.append("</details>\n")

body = "\n".join(comment)
# GitHub Actions multiline output
print(body)
with open(os.environ.get("GITHUB_OUTPUT","/tmp/out"), "a") as f:
    f.write(f"body<<EOF\n{body}\nEOF\n")
