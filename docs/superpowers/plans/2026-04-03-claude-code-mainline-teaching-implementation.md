# Claude Code Mainline Teaching Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reframe the repository so readers learn Claude Code source through one dominant request-lifecycle mainline, with source navigation and architecture understanding as supporting rails.

**Architecture:** Keep all existing source facts and most existing content, but rewrite the repository’s entrypoints and teaching scaffolding around a single “one request lifecycle” spine. Land the change in four phases: homepage/index framing, source navigation framing, staged path rewrites, then layer/example normalization plus a verification sweep.

**Tech Stack:** Markdown documentation, Python example docstrings, git, Python 3 for verification utilities

---

## File Structure / Responsibility Map

- `README.MD` — Chinese homepage; must become the canonical statement of the mainline and the shortest learning route.
- `README_EN.MD` — English homepage; must mirror the same information architecture as the Chinese README.
- `docs/paths/README.md` / `docs/paths/README.en.md` — course index; should explain how the mainline is split into stages.
- `docs/source-map.md` / `docs/source-map.en.md` — source tracing guide; should become a per-step map from lifecycle stages to files/symbols.
- `docs/example-source-bridge.md` / `docs/example-source-bridge.en.md` — bridge from runnable examples back to lifecycle steps and real source files.
- `docs/paths/p1-first-hour*.md` — stage 1; should cover entrypoint/setup/first glimpse of the loop and stop aggressively.
- `docs/paths/p2-core-loop*.md` — stage 2; should cover the single-turn core request loop.
- `docs/paths/p3-source-reading*.md` — stage 3; should cover direct reading of the mainline files.
- `docs/paths/p4-advanced-architecture*.md` — stage 4; should cover branch topics only after the mainline is stable.
- `docs/layers/*.md` / `docs/layers/*.en.md` — deep dives; must explain how each layer supports the mainline.
- `examples/*.py` — runnable teaching slices; top docstrings must explicitly say where the example sits on the mainline.

---

### Task 1: Reframe the homepages and course indexes around the mainline

**Files:**
- Modify: `README.MD`
- Modify: `README_EN.MD`
- Modify: `docs/paths/README.md`
- Modify: `docs/paths/README.en.md`
- Test: `README.MD`
- Test: `README_EN.MD`

- [ ] **Step 1: Snapshot the current openings so the rewrite keeps existing facts**

Run:

```bash
sed -n '1,220p' README.MD
sed -n '1,220p' README_EN.MD
sed -n '1,220p' docs/paths/README.md
sed -n '1,220p' docs/paths/README.en.md
```

Expected: You can see the current introductions, route descriptions, and existing link structure before editing.

- [ ] **Step 2: Rewrite `README.MD` so the first screen states the one request lifecycle mainline**

Replace the top framing with a structure equivalent to:

```md
## 你现在要抓的唯一主线

这个仓库的第一目标，不是记住所有层，而是抓住 Claude Code 中“一次请求如何流动”：

**用户输入
→ 启动 / 模式分流
→ 进入 `query` / `queryLoop`
→ 模型产出
→ 工具调用
→ 工具执行
→ 工具结果回流
→ 状态 / UI 更新
→ 下一轮或退出**

## 9 个 examples 在主线中的位置

| Example | 主线位置 | 读者要抓住什么 |
|---|---|---|
| `l1_startup.py` | 输入 → 启动 / 分流 | CLI 如何进入正确运行模式 |
| `l2_agent_loop.py` | 进入 `queryLoop` → 单轮 loop | 一轮请求怎样驱动模型与工具 |
| `l3_tool_system.py` | 模型产出 → 工具调用 | 工具如何被注册、选择、执行 |
| `l4_ui_ink.py` | 状态 / UI 更新 | 终端 UI 如何反映主线状态 |
| `l5_state_commands.py` | 状态组织 / 命令入口 | 状态如何支撑多轮对话 |
| `l6_advanced.py` | 主线外的扩展边界 | skills / coordinator / cost 是怎样挂接的 |
| `l7_permissions.py` | 工具执行前的关口 | 权限系统怎样介入主线 |
| `l8_streaming.py` | 主线贯穿方式 | 为什么主抽象是 async generator |
| `l9_context_mgmt.py` | 多轮持续运行 | context 管理如何保护主线继续前进 |
```

Constraint: Keep existing factual claims about repo contents; change framing, not source facts.

- [ ] **Step 3: Mirror the same information architecture in `README_EN.MD`**

Add an English equivalent of the same sections:

```md
## The one mainline you should hold onto

The first goal of this repo is not to memorize every layer. It is to understand how one Claude Code request moves through the system:

**user input
→ startup / mode routing
→ enter `query` / `queryLoop`
→ model output
→ tool call
→ tool execution
→ tool result flows back
→ state / UI update
→ next turn or exit**
```

Expected: The Chinese and English READMEs have matching section order and matching teaching intent.

- [ ] **Step 4: Turn `docs/paths/README*` into lifecycle stage indexes instead of generic course lists**

Insert a section with this shape into both language versions:

```md
## 这四个阶段如何对应主线

| 阶段 | 主线位置 | 本阶段只搞懂什么 |
|---|---|---|
| P1 | 输入 → 启动 / 分流 | 请求是如何真正进入系统的 |
| P2 | `queryLoop` 单轮主线 | 模型、工具、回流如何串起来 |
| P3 | 主线源码直读 | 直接读关键文件与关键 symbol |
| P4 | 主线之外的边界 | permissions / memory / runtime modes 如何围绕主线展开 |
```

Also add a “这一阶段先不要看什么 / What to ignore for now” explanation near the top.

- [ ] **Step 5: Verify link integrity for the edited index files**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
import re
targets = [
    Path('README.MD'),
    Path('README_EN.MD'),
    Path('docs/paths/README.md'),
    Path('docs/paths/README.en.md'),
]
pat = re.compile(r'\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)')
for md in targets:
    text = md.read_text(encoding='utf-8')
    for target in pat.findall(text):
        if target.startswith(('http://', 'https://', 'mailto:')):
            continue
        resolved = (md.parent / target).resolve()
        assert resolved.exists(), f'{md}: missing {target}'
print('OK')
PY
```

Expected: `OK`

- [ ] **Step 6: Commit the homepage/index rewrite**

Run:

```bash
cat > /tmp/mainline-readme-commit.txt <<'EOF'
Make the learning entrypoints teach one request mainline first

The homepages and path indexes now orient readers around a single
request lifecycle before they branch into layers or deep dives.

Constraint: Keep existing repo facts and links intact while changing the teaching frame
Rejected: Add more introductory prose without changing structure | would not solve the missing spine
Confidence: high
Scope-risk: moderate
Reversibility: clean
Directive: Future top-level docs should always answer “where am I on the request lifecycle?” near the top
Tested: Targeted markdown link check for README and path index files
Not-tested: Full repo markdown audit after later tasks
EOF
git add README.MD README_EN.MD docs/paths/README.md docs/paths/README.en.md
git commit -F /tmp/mainline-readme-commit.txt
```

Expected: One commit recording the entrypoint reframing.

---

### Task 2: Rebuild source navigation docs around lifecycle steps

**Files:**
- Modify: `docs/source-map.md`
- Modify: `docs/source-map.en.md`
- Modify: `docs/example-source-bridge.md`
- Modify: `docs/example-source-bridge.en.md`
- Test: `docs/source-map.md`
- Test: `docs/example-source-bridge.md`

- [ ] **Step 1: Capture the current source-map and bridge structure**

Run:

```bash
sed -n '1,260p' docs/source-map.md
sed -n '1,260p' docs/source-map.en.md
sed -n '1,260p' docs/example-source-bridge.md
sed -n '1,260p' docs/example-source-bridge.en.md
```

Expected: You can identify where the current docs are descriptive but not explicitly step-based.

- [ ] **Step 2: Rewrite `docs/source-map.md` as a lifecycle tracing document**

Organize the file into repeating sections like:

```md
## Step 1 — 启动 / 模式分流

**主线位置：** 用户输入 → 启动 / 分流
**输入：** CLI 参数、工作目录、模式选择
**输出：** 进入某个 entrypoint 或进入交互式会话
**先看文件：**
- `src/main.tsx`
- `src/setup.ts`

**建议先搜的 symbol：**
- `main`
- `setup`
- `runHeadless`

**下一步流向：**
进入 `query` / `queryLoop`，开始单轮请求处理
```

Repeat this pattern for:
- startup / routing
- entering `query` / `queryLoop`
- model output and tool selection
- tool execution
- tool result re-entry
- state / UI update
- next turn / exit conditions

- [ ] **Step 3: Mirror the same step pattern in `docs/source-map.en.md`**

The English version should use the same step count and same file/symbol mapping, not an independently structured summary.

- [ ] **Step 4: Rewrite both bridge docs so each example maps to a lifecycle step**

Use a table with this shape:

```md
| Example | Mainline step | What this example simplifies | Next source files to open |
|---|---|---|---|
| `l2_agent_loop.py` | enter `queryLoop` → single-turn loop | simplifies model/provider complexity | `src/query.ts`, `src/QueryEngine.ts` |
| `l7_permissions.py` | before tool execution | simplifies real checker breadth | `src/tools/BashTool/bashPermissions.ts`, `bashSecurity.ts` |
```

Also add a short rule above the table:

```md
先问：这个 example 在主线哪一步？
再问：真实源码在这一步多了哪些复杂度？
```

- [ ] **Step 5: Verify all source navigation docs still point to existing repo files**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
import re
targets = [
    Path('docs/source-map.md'),
    Path('docs/source-map.en.md'),
    Path('docs/example-source-bridge.md'),
    Path('docs/example-source-bridge.en.md'),
]
pat = re.compile(r'\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)')
for md in targets:
    text = md.read_text(encoding='utf-8')
    for target in pat.findall(text):
        if target.startswith(('http://', 'https://', 'mailto:')):
            continue
        resolved = (md.parent / target).resolve()
        assert resolved.exists(), f'{md}: missing {target}'
print('OK')
PY
```

Expected: `OK`

- [ ] **Step 6: Commit the source navigation rewrite**

Run:

```bash
cat > /tmp/mainline-sourcemap-commit.txt <<'EOF'
Make source navigation follow the request lifecycle

The source map and example bridge now guide readers step-by-step
through the request path, with explicit file, symbol, input, output,
and next-hop framing.

Constraint: Preserve accurate file and symbol references while changing doc structure
Rejected: Keep the old topical layout and add a summary at the top | too weak to guide real source tracing
Confidence: high
Scope-risk: moderate
Reversibility: clean
Directive: Any new source navigation page should be navigable as a call-chain trace, not only as a topic index
Tested: Targeted markdown link check for source-map and bridge docs
Not-tested: Reader usability against the full learning path
EOF
git add docs/source-map.md docs/source-map.en.md docs/example-source-bridge.md docs/example-source-bridge.en.md
git commit -F /tmp/mainline-sourcemap-commit.txt
```

---

### Task 3: Rewrite the staged path pages to advance one slice of the lifecycle at a time

**Files:**
- Modify: `docs/paths/p1-first-hour.md`
- Modify: `docs/paths/p1-first-hour.en.md`
- Modify: `docs/paths/p2-core-loop.md`
- Modify: `docs/paths/p2-core-loop.en.md`
- Modify: `docs/paths/p3-source-reading.md`
- Modify: `docs/paths/p3-source-reading.en.md`
- Modify: `docs/paths/p4-advanced-architecture.md`
- Modify: `docs/paths/p4-advanced-architecture.en.md`
- Test: `docs/paths/p1-first-hour.md`
- Test: `docs/paths/p4-advanced-architecture.en.md`

- [ ] **Step 1: Add a shared section skeleton to all path pages**

At the top of each page, add or normalize sections in this order:

```md
## 本阶段只搞懂什么
## 你在主线中的位置
## 先跑哪个 example
## 再读哪篇 layer
## 再开哪些源码文件
## 这一阶段先不要看什么
```

Expected: All four stages in both languages use the same orientation pattern.

- [ ] **Step 2: Reframe P1 around “how a request actually enters the system”**

Ensure the Chinese and English P1 pages emphasize:

```md
- 主线位置：用户输入 → 启动 / 模式分流
- 本阶段只搞懂：
  1. Claude Code 如何决定当前运行模式
  2. setup 在真正进入 loop 之前做了什么
  3. 为什么这一步还不该陷入 tools / streaming / memory
```

Primary files for this page should include `main.tsx` and `setup.ts`.

- [ ] **Step 3: Reframe P2 around the single-turn core loop**

Ensure P2 centers:

```md
- 主线位置：进入 `query` / `queryLoop` → 模型产出 → 工具回流
- 本阶段只搞懂：
  1. 一轮请求如何形成 while-loop
  2. 工具结果如何重新进入历史
  3. permissions / streaming 为什么在这里变重要
```

Primary files should include `query.ts`, `QueryEngine.ts`, and the tool system boundary.

- [ ] **Step 4: Reframe P3 and P4 so they branch only after the mainline is stable**

Use wording equivalent to:

```md
P3:
- 现在你不再是“了解概念”，而是沿主线直接阅读关键文件

P4:
- 只有在主线稳定后，才展开 permissions / memory / runtime modes / coordinator 等边界专题
```

Also add explicit “don’t open these yet” guidance in each page where appropriate.

- [ ] **Step 5: Run a focused path-page consistency check**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
files = sorted(Path('docs/paths').glob('p*.md')) + sorted(Path('docs/paths').glob('p*.en.md'))
required = [
    '本阶段只搞懂什么',
    '你在主线中的位置',
    '先跑哪个 example',
]
for p in files:
    text = p.read_text(encoding='utf-8')
    if p.name.endswith('.en.md'):
        continue
    for marker in required:
        assert marker in text, f'{p}: missing {marker}'
print('OK')
PY
```

Expected: `OK`

- [ ] **Step 6: Commit the staged path rewrite**

Run:

```bash
cat > /tmp/mainline-paths-commit.txt <<'EOF'
Teach the lifecycle in staged path-sized slices

Each path page now states its exact position on the request mainline,
the narrow questions readers should answer there, and the source files
they should open next.

Constraint: Keep the four-stage structure while making each stage lifecycle-specific
Rejected: Collapse the paths into one long article | removes pacing and makes scope creep harder to control
Confidence: high
Scope-risk: moderate
Reversibility: clean
Directive: Path pages should reduce cognitive load by saying what to ignore, not only what to read
Tested: Focused consistency check for required Chinese path sections
Not-tested: Parallel section-presence check for English pages
EOF
git add docs/paths/p1-first-hour.md docs/paths/p1-first-hour.en.md docs/paths/p2-core-loop.md docs/paths/p2-core-loop.en.md docs/paths/p3-source-reading.md docs/paths/p3-source-reading.en.md docs/paths/p4-advanced-architecture.md docs/paths/p4-advanced-architecture.en.md
git commit -F /tmp/mainline-paths-commit.txt
```

---

### Task 4: Normalize layer docs and example docstrings to the same mainline language

**Files:**
- Modify: `docs/layers/*.md`
- Modify: `docs/layers/*.en.md`
- Modify: `examples/l1_startup.py`
- Modify: `examples/l2_agent_loop.py`
- Modify: `examples/l3_tool_system.py`
- Modify: `examples/l4_ui_ink.py`
- Modify: `examples/l5_state_commands.py`
- Modify: `examples/l6_advanced.py`
- Modify: `examples/l7_permissions.py`
- Modify: `examples/l8_streaming.py`
- Modify: `examples/l9_context_mgmt.py`
- Test: `examples/l1_startup.py`
- Test: `examples/l9_context_mgmt.py`

- [ ] **Step 1: Add lifecycle-role headers to every layer doc**

At the top of each Chinese layer document, add a compact block like:

```md
## 这一层在主线里的职责
## 如果没有这一层，主线会断在哪
## 读源码时只需要先盯哪些 symbol
## 这一层最容易误解什么
## 读完后你应该能回答什么问题
```

Mirror the equivalent English sections in each `.en.md` file.

- [ ] **Step 2: Normalize each example docstring to explicitly state mainline position**

Update each example’s top docstring so it includes lines equivalent to:

```py
这个 example 在主线中的位置：
  用户输入 → 启动 / 分流

它模拟了哪一步：
  展示请求如何真正进入 Claude Code，而不是直接进入 Agent Loop。

此时先不用管什么：
  先不要展开 tools、streaming、memory 的细节。
```

Use the right lifecycle stage for each file, not the same text everywhere.

- [ ] **Step 3: Align supporting example text with the current 9-example repo state**

Before moving on, verify that no example still claims:

```text
6 个学习层级
l1~l6 共 6 个示例文件
```

Run:

```bash
rg -n "6 个学习层级|l1~l6|6 layers|6-layer" examples docs README.MD README_EN.MD
```

Expected: No stale instructional claims remain except where they are intentionally historical.

- [ ] **Step 4: Run Python syntax verification after docstring edits**

Run:

```bash
python3 -m compileall examples
```

Expected: Every file in `examples/` compiles successfully.

- [ ] **Step 5: Smoke-run the examples after docstring normalization**

Run:

```bash
python3 - <<'PY'
import subprocess
commands = {
    'l1': "printf '/exit\\n' | python3 examples/l1_startup.py",
    'l2': "printf 'exit\\n' | python3 examples/l2_agent_loop.py",
    'l3': "printf 'n\\n' | python3 examples/l3_tool_system.py",
    'l4': "python3 examples/l4_ui_ink.py",
    'l5': "printf 'exit\\n' | python3 examples/l5_state_commands.py",
    'l6': "python3 examples/l6_advanced.py",
    'l7': "printf 'n\\n' | python3 examples/l7_permissions.py",
    'l8': "printf 'exit\\n' | python3 examples/l8_streaming.py",
    'l9': "python3 examples/l9_context_mgmt.py",
}
for name, cmd in commands.items():
    proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=20)
    assert proc.returncode == 0, f"{name} failed"
print("OK")
PY
```

Expected: `OK`

- [ ] **Step 6: Commit the layer/example normalization**

Run:

```bash
cat > /tmp/mainline-layers-examples-commit.txt <<'EOF'
Make deep dives and examples speak the same lifecycle language

The layer docs and Python examples now state their role on the request
mainline explicitly, so readers can move between runnable slices and
real source without losing their position.

Constraint: Preserve example behavior while changing only teaching framing and top-level guidance
Rejected: Leave examples as isolated “layer demos” | keeps the repo easy to browse but hard to mentally connect
Confidence: high
Scope-risk: moderate
Reversibility: clean
Directive: New examples and deep dives should declare their lifecycle position before any detailed explanation
Tested: `python3 -m compileall examples`; full nine-example smoke run
Not-tested: Human pass over every bilingual deep-dive page for tone symmetry
EOF
git add docs/layers README.MD README_EN.MD examples
git commit -F /tmp/mainline-layers-examples-commit.txt
```

Note: Before running the `git add` above, verify you are only staging intended files, since this repository may already contain unrelated local edits.

---

### Task 5: Run a final repository-wide teaching QA pass

**Files:**
- Modify: `README.MD` (if needed)
- Modify: `README_EN.MD` (if needed)
- Modify: `docs/source-map.md` (if needed)
- Modify: `docs/paths/*.md` (if needed)
- Test: entire repository teaching surface

- [ ] **Step 1: Run a repository-wide markdown link audit**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
import re
pat = re.compile(r'\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)')
for md in Path('.').rglob('*.md'):
    if '.git' in md.parts or 'claudecode_src' in md.parts:
        continue
    text = md.read_text(encoding='utf-8')
    for target in pat.findall(text):
        if target.startswith(('http://', 'https://', 'mailto:')):
            continue
        resolved = (md.parent / target).resolve()
        assert resolved.exists(), f'{md}: missing {target}'
print('OK')
PY
```

Expected: `OK`

- [ ] **Step 2: Run a lifecycle-language spot audit on the main teaching surface**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
checks = {
    Path('README.MD'): ['唯一主线', 'examples 在主线中的位置'],
    Path('docs/paths/README.md'): ['主线', 'example'],
    Path('docs/source-map.md'): ['主线步骤', '下一步流向'],
}
for path, markers in checks.items():
    text = path.read_text(encoding='utf-8')
    for marker in markers:
        assert marker in text, f'{path}: missing {marker}'
print('OK')
PY
```

Expected: `OK`

- [ ] **Step 3: Manually read the first 120 lines of the main entry docs**

Run:

```bash
sed -n '1,120p' README.MD
sed -n '1,120p' README_EN.MD
sed -n '1,120p' docs/paths/README.md
sed -n '1,120p' docs/source-map.md
```

Manual check criteria:
- The first screen states the mainline before listing resources.
- A reader can answer “where am I in the lifecycle?” without scrolling deep.
- The docs tell the reader what to do next, not only what exists.

- [ ] **Step 4: Apply any small fixes found in the QA pass**

If you find missing markers, broken wording symmetry, or bad links, fix those exact files immediately instead of deferring.

- [ ] **Step 5: Commit the final QA polish**

Run:

```bash
cat > /tmp/mainline-qa-commit.txt <<'EOF'
Tighten the lifecycle teaching surface after the main rewrite

This pass verifies that the repo’s primary learning surfaces now state
the request lifecycle clearly, preserve working links, and guide readers
forward without forcing them to assemble the spine themselves.

Constraint: Keep the QA pass narrow and evidence-driven
Rejected: Skip final teaching QA because the docs already compile logically | risks leaving the new structure inconsistent at entrypoints
Confidence: medium
Scope-risk: narrow
Reversibility: clean
Directive: Treat teaching clarity regressions like real regressions; verify the repo’s entry docs after structural rewrites
Tested: Repo-wide markdown link audit; lifecycle-language spot audit; manual first-screen read
Not-tested: External reader study
EOF
git add README.MD README_EN.MD docs/paths docs/source-map.md docs/source-map.en.md docs/example-source-bridge.md docs/example-source-bridge.en.md docs/layers examples
git commit -F /tmp/mainline-qa-commit.txt
```

---

## Spec Coverage Check

- **Single dominant lifecycle mainline** — covered by Tasks 1–4.
- **Source navigation as auxiliary rail** — covered by Task 2.
- **Architecture understanding as auxiliary rail** — covered by Tasks 3–4.
- **README / paths / source-map / examples all aligned** — covered across Tasks 1–4.
- **Success criteria validated** — covered by Task 5.

No spec requirement is intentionally deferred.
