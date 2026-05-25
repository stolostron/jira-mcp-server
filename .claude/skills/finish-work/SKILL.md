---
name: finish-work
description: Use when the user runs /finish-work or asks to wrap up, commit, push, open a PR, and update Jira for the current work session.
---

Update `plans/INDEX.md`, Jira, and the PR for the current work session. Safe to re-run — each step skips what is already done.

## Step 1 — Find the current session

Read `plans/INDEX.md`. Find the most recent `sessions` entry where `pr: ~` (no PR yet). If ambiguous, ask the user. Extract `jira` and `jira_url`; if missing, ask.

## Step 2 — Check if a PR exists

Look at the `pr` field of the session entry. If it is set, skip to **Phase 2**. Otherwise run **Phase 1**.

---

## Phase 1 — No PR yet

### Step 3 — Compose a commit message

Use conventional commits format: one subject line + short body. No quotes or special characters.

### Step 4 — Create the branch (if needed)

- If on `main` or `master`: `git checkout -b <JIRA-ID>` (e.g. `git checkout -b ACM-12345`).
- If already on a feature branch, use it.

### Step 5 — Stage, commit, and push

```
git add <modified files>
git commit -S -s -m "<subject line>"
git push -u origin <branch>
```

### Step 6 — Create a PR

Create a PR from the branch to `main`. Include the Jira link in the PR body. If a PR already exists for this branch, skip creation.

### Step 7 — Continue with Phase 2

Once the PR exists, continue immediately with Phase 2 below.

---

## Phase 2 — PR exists

### Step 3 — Write an implementation summary

Cover: what changed (files/functions), tests added, known gaps.

- If the PR description is empty or minimal, update it with the summary.
- Otherwise post the summary as a **comment on the PR**.

### Step 4 — Update Jira

Use the jira-mcp-server for all Jira operations:

- Set `git_commit` to the commit SHA (skip if already set).
- Set `git_pull_requests` to the PR URL (skip if already set).
- Post a short comment: commit message subject + body (skip if an identical comment already exists).
- Transition the Jira ticket to `Review` status (skip if already in `Review` or later).
- Ask if the user wants to log implementation time.

### Step 5 — Update `plans/INDEX.md`

Update the session entry:

- `pr`: full PR URL
- `summary`: one sentence describing what was actually accomplished

### Step 6 — Remind the user

Confirm tests exist and pass.
