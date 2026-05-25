---
name: start-work
description: Use when the user runs /start-work or asks to create a Jira sub-task for the current work session and register it in plans/INDEX.md.
---

Create a Jira sub-task for the current work session and register it in `plans/INDEX.md`.

**Args:** parent ticket ID (required), issue type override (optional, default `Sub-task`). Valid types: `Bug`, `Task`, `Spike`, `Sub-task`.

---

## Step 1 — Parse args

Read the parent ticket ID from the user's command args. If none was provided, ask the user for one before continuing.

## Step 2 — Fetch parent ticket

Call `get_issue` on the parent ticket ID. Record its summary, components, target version, labels, and Activity Type (work_type).

## Step 3 — Gather work summary

Ask the user for a 1–2 sentence description of the work to be done. This becomes the sub-task title and the `summary` field in `plans/INDEX.md`. If no issue type was provided as an arg, ask for that too (default: `Sub-task`).

## Step 4 — Create the Jira sub-task

Call `create_issue` with:

- `project_key`: `ACM`
- `assignee`: `jpacker@redhat.com`
- `security_level`: `Red Hat Employee`
- `parent`: parent ticket ID
- Inherit `components`, `target_version`, `work_type`, and `labels` from the parent.

## Step 5 — Comment on the new sub-task

Post a comment with:
- Brief context (why this work is needed, drawn from the parent ticket)
- Intended approach (what will change, drawn from the user's summary)

## Step 6 — Confirm and offer time logging

Show the user the new ticket key and URL. Ask if they want to log planning time against the new ticket.

## Step 7 — Append to `plans/INDEX.md`

Add to the `sessions` list, preceded by a `---` divider:

```yaml
---
- date: "YYYY-MM-DD"
  title: "<sub-task title>"
  jira: "ACM-NNNNN"
  jira_url: "https://redhat.atlassian.net/browse/ACM-NNNNN"
  pr: ~
  summary: "One sentence describing what the work will accomplish"
```

## Step 8 — Format the Jira description

Use the appropriate specialist skill based on the issue type:

| Issue Type | Skill |
|---|---|
| Sub-task / Task | `task-specialist` → `@claude/skills/task-specialist/SKILL.md` |
| Bug | `bug-specialist` → `@claude/skills/bug-specialist/SKILL.md` |
| Spike | `spike-specialist` → `@claude/skills/spike-specialist/SKILL.md` |
