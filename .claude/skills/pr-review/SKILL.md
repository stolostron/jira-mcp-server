---
name: pr-review
description: Review GitHub pull requests
---

# PR Review Skill

This skill helps you conduct comprehensive reviews of GitHub pull requests.

**Supporting files**:
- `scripts/summarize-pr.py` - Comprehensive PR summary script (uses GraphQL)
- `scripts/prepare-worktree.py` - Create git worktree for PR review

**Important**: All scripts use `uv` for automatic dependency management. Run them directly (e.g., `scripts/summarize-pr.py`). If `uv` is not available, fall back to `python scripts/summarize-pr.py` but you'll need to install dependencies manually.

## When to Use This Skill

Use this skill when the user asks you to review a GitHub pull request. The user will typically provide a PR URL or PR number.

## How to Review a PR

### Step 1: Generate PR Summary

Start by generating a comprehensive summary of the PR. This gives you the complete picture before diving deep:

```bash
scripts/summarize-pr.py <OWNER> <REPO> <PR_NUMBER>
```

**This script provides:**
- PR metadata (title, author, status, branch, stats)
- Description
- Files changed with additions/deletions
- **Discussion & Reviews** - Chronological timeline of all comments and reviews
- **Unresolved Review Comments** - Code review threads that need addressing (with diff context)

**Read and analyze this output carefully:**
- What problem is being solved?
- What's the current discussion context?
- What unresolved issues already exist?
- Who has reviewed and what are their concerns?

**IMPORTANT**: The unresolved comments are **known blockers**. Don't duplicate these in your review - focus on finding NEW issues.

### Step 2: Prepare Git Worktree and Review Notes

Create a clean worktree for reviewing the PR and initialize review tracking:

```bash
WORKTREE_PATH=$(scripts/prepare-worktree.py <repository_directory> <PR_NUMBER>)
cd "$WORKTREE_PATH"
```

**What this does:**
- Creates a new worktree in `<repository>/git-worktrees/<branch-name>`
- Creates a review notes directory in `<repository>/review-notes/<branch-name>`
- Generates a `README.md` template in the review notes directory for tracking progress
- Fetches and checks out the PR branch in the worktree
- If the worktree already exists, checks for uncommitted changes before recreating
- Returns the path to the worktree directory

**Benefits:**
- Main repository stays on its current branch
- Can review multiple PRs simultaneously in different worktrees
- Clean separation between review work and regular development
- Review notes are organized per-PR with a structured template
- Progress tracking with checkboxes for each review step

**Use the review notes file:**
- Open `<repository>/review-notes/<branch-name>/README.md`
- Fill in notes as you progress through each step
- Check off tasks as you complete them
- Document unresolved comments and new issues found
- Write your final recommendation

### Step 3: Gather Context

This is the critical step that goes beyond mechanical checking. Based on the PR type and files changed, use the **Task tool with subagent_type=Explore** to gather additional context:

**For code PRs:**
- **Related files**: Files that import/use the changed code (to understand integration)
- **Test files**: Are there tests? Do they cover the changes?
- **Documentation**: README, API docs, comments - are they updated?
- **Configuration**: Are there deployment/config implications?
- **Recent related PRs**: Is this part of a larger effort?

**For design/documentation PRs (SDPs, RFCs, etc.):**
- **Related design docs**: Other SDPs or architectural decisions
- **Architecture principles**: Does this align with standards?
- **Existing implementations**: What code might be affected?
- **Previous discussions**: GitHub issues, meeting notes, etc.

**How to gather context:**
- Use `gh pr view` to see linked issues
- **Use Task tool with subagent_type=Explore** to search for:
  - Related files (imports, callers, tests)
  - Architectural standards or guidelines
  - Existing similar implementations
  - Documentation that needs updating
- Read the files you discover to understand integration points

**Example context gathering:**
```bash
# Use the Task tool with subagent_type=Explore to find:
# - "Find all files that import X module"
# - "Find test files related to Y feature"
# - "Find architecture docs about Z pattern"
```

### Step 4: Analyze the PR

Now review the PR comprehensively:

1. **Does it solve the stated problem?**
   - Compare the changes to the PR description
   - Check if the solution is complete

2. **Are unresolved comments blocking?**
   - Review the unresolved threads from Step 1's summary
   - Determine severity and impact

3. **What NEW issues exist?**
   - Things not already flagged in unresolved threads (from Step 1)
   - Consider: correctness, design, testing, documentation, edge cases
   - **Record file:line for each issue** - You'll need these to submit inline comments

4. **Context and design concerns**
   - Does it fit the broader architecture?
   - Are there cross-cutting concerns (security, performance, etc.)?
   - Is the approach consistent with similar code?

**Review criteria by PR type:**

For **code PRs**:
- Correctness and logic
- Test coverage
- Error handling
- Performance implications
- Security concerns
- Documentation completeness
- Code style and conventions

For **design/documentation PRs**:
- Completeness of requirements
- Clarity of problem statement
- Well-defined use cases
- Consistency in terminology
- Alignment with architecture principles
- Missing sections or incomplete information
- Feasibility of implementation

### Step 5: Complete Review Notes and Provide Recommendation

As you work through the review, systematically fill in the review notes at `<repository>/review-notes/<branch-name>/README.md`:

1. **Step 1 - PR Summary Analysis**
   - Check off each task as you review the summary output
   - Document key observations in the Notes section
   - List unresolved comments under "Unresolved Comments (from PR)"

2. **Step 3 - Context Gathering**
   - Note what related files/tests/docs you examined
   - Document architectural concerns or patterns found
   - Check off tasks as you complete them

3. **Step 4 - Code Review**
   - Work through the changed files systematically
   - Check off review tasks as you complete them
   - Document new issues found under "New Issues Found" with `file:line` references

4. **Step 5 - Final Recommendation**
   - Select the appropriate status (Approve/Request Changes/Comment)
   - Write a clear summary of your findings
   - List specific, actionable items for the author
   - **Focus on NEW issues**, not duplicating unresolved comments

**Review notes structure:**
- **Unresolved Comments**: Issues already flagged in the PR discussion
- **New Issues Found**: Problems you discovered during review
- **Final Recommendation**: Your verdict and next steps
- Use `file:line` references for all code-specific feedback

### Tracking Line Numbers for GitHub Comments

**IMPORTANT**: As you review, track the exact line numbers where you want to leave inline comments. This information is required when submitting reviews to GitHub.

For each issue you find, record in your review notes:
- **File path**: Relative to repo root (e.g., `src/components/Button.tsx`)
- **Line number**: The line in the NEW file (right side of diff)
- **Comment text**: What feedback to leave
- **Suggestion** (optional): If proposing a fix, include the corrected line

**Example format in review notes:**

```markdown
### Inline Comments to Submit

| File | Line | Comment |
|------|------|---------|
| `src/api/client.ts` | 45 | Missing error handling for network failures |
| `src/api/client.ts` | 52 | Typo: "recieve" → "receive" |
| `docs/README.md` | 12 | This section contradicts the API docs |

### Suggestions (with replacement text)

1. `src/api/client.ts:52`
   ```suggestion
   const response = await this.receive(data);
   ```
```

**Finding line numbers:**
- **ALWAYS verify line numbers by reading the actual file** - Use the Read tool with the file from the worktree to confirm exact line numbers before submitting comments
- `gh pr diff` line numbers are for the diff output, NOT the file - don't use them directly
- Use `grep -n "pattern" <file>` or Read tool to get the true line number in the file
- The line number should be from the NEW version of the file (what the PR proposes), not the old version

**Common mistake to avoid:**
When you see content in a diff or remember a line number from earlier, ALWAYS re-verify by reading the file before submitting comments. Off-by-one errors are common and put comments in the wrong place.

```bash
# WRONG: Using grep on diff output
gh pr diff 1060 | grep -n "pattern"  # This gives diff line numbers, not file line numbers

# RIGHT: Read the actual file and verify
Read tool: /path/to/worktree/file.md (offset: 65, limit: 10)
# Or use grep on the actual file:
grep -n "pattern" /path/to/worktree/file.md
```

This tracking ensures you have all the information needed to submit inline comments via the GitHub API without re-reading files.

## Output Format

Your review output should be written in the review notes file at `<repository>/review-notes/<branch-name>/README.md`.

The template provides sections for:
- PR Summary Analysis with checkboxes
- Context Gathering notes
- Code Review progress tracking
- Unresolved Comments (from existing PR discussion)
- New Issues Found (your discoveries)
- Final Recommendation with status and action items

Use code references in the format `file_path:line_number` when pointing to specific locations.

## Important Notes

- **Always start with summarize-pr.py** - This gives you the complete PR context upfront
- **Always use prepare-worktree.py** - Never checkout PRs in the main repository
- **Always use the review notes file** - Document your progress systematically in `review-notes/<branch-name>/README.md`
- **Always use the `gh` CLI tool** via Bash, never try to construct GitHub URLs manually
- **Prefer running scripts with uv** - The scripts have uv-style dependency declarations and will auto-install dependencies. Fall back to `python` only if `uv` is unavailable.
- **Don't duplicate unresolved threads** - They're already documented, focus on NEW issues
- **Use Task tool with subagent_type=Explore** for context gathering - this is where you add value
- **Be thorough but constructive** - provide specific, actionable feedback
- **Prioritize findings** by severity and impact
- **Check off tasks** in the review notes as you complete each step
- **Track file:line numbers as you go** - Record exact locations for inline comments to avoid re-reading files later

## Example Workflow

```bash
# Step 1: Generate comprehensive PR summary
scripts/summarize-pr.py <OWNER> <REPO> <PR_NUMBER>

# Read and analyze the output:
# - What's the PR about?
# - What's the discussion history?
# - What unresolved issues exist?

# Step 2: Prepare git worktree
WORKTREE_PATH=$(scripts/prepare-worktree.py /path/to/repo <PR_NUMBER>)
cd "$WORKTREE_PATH"

# Step 3: Gather context using Task tool
# Use Task tool with subagent_type=Explore to find:
# - Related architecture docs
# - Similar implementations
# - Test coverage
# - Integration points

# Step 4: Analyze the PR
# - Read changed files
# - Check for issues not in unresolved threads
# - Verify alignment with context found

# Step 5: Provide structured review
# Follow the 5-section format above
```

## Leaving Review Comments on GitHub

When you need to leave comments on a PR (e.g., requesting changes), use GitHub's GraphQL API to create a pending review with iterative comments.

### Step 1: Get the PR Head Commit SHA

```bash
gh pr view <PR_NUMBER> --repo <OWNER>/<REPO> --json headRefOid --jq '.headRefOid'
```

### Step 2: Create an Empty Pending Review

```bash
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/reviews \
  --method POST \
  --input - <<'EOF'
{
  "commit_id": "<COMMIT_SHA>",
  "body": "",
  "comments": []
}
EOF
```

This returns a review ID (e.g., `3717123607`).

### Step 3: Get the Pending Review's GraphQL Node ID

```bash
gh api graphql -f query='
query {
  repository(owner: "<OWNER>", name: "<REPO>") {
    pullRequest(number: <PR_NUMBER>) {
      reviews(states: PENDING, first: 1) {
        nodes {
          id
          state
        }
      }
    }
  }
}'
```

This returns a node ID like `PRR_kwDOMIdo187djs4X`.

### Step 4: Add Comments Iteratively

Use the GraphQL `addPullRequestReviewThread` mutation to add comments one at a time:

```bash
gh api graphql -f query='
mutation {
  addPullRequestReviewThread(input: {
    pullRequestReviewId: "<REVIEW_NODE_ID>"
    path: "path/to/file.md"
    line: 25
    side: RIGHT
    body: "Your comment here.\n\n```suggestion\nSuggested replacement text\n```"
  }) {
    thread {
      id
    }
  }
}'
```

**Parameters:**
- `pullRequestReviewId`: The GraphQL node ID from Step 3 (e.g., `PRR_kwDOMIdo187djs4X`)
- `path`: File path relative to repo root
- `line`: Line number in the diff (the new file's line number)
- `side`: `RIGHT` for additions, `LEFT` for deletions
- `body`: Comment text (supports markdown and `suggestion` code blocks)

**Line number tips:**
- Use the line number from the new file, not the diff position
- If you have review notes with specific line numbers, trust those rather than recalculating from partial diffs
- When in doubt, use `gh pr diff <PR> | grep -n "pattern"` to find the exact line

**Using suggestion blocks:**
GitHub suggestions work on single lines. The suggestion replaces the entire line:

```markdown
\`\`\`suggestion
CORRECTED_LINE_CONTENT_HERE
\`\`\`
```

Note: Suggestions work on the raw file content. For lines inside markdown code blocks, the suggestion will replace the markdown source line (including the leading spaces/formatting), not the rendered content.

Repeat this step for each comment you want to add.

#### File-Level Comments

For comments about the file itself (e.g., "this file should be in a different directory"), use `subjectType: FILE` and omit the `line` parameter:

```bash
gh api graphql -f query='
mutation {
  addPullRequestReviewThread(input: {
    pullRequestReviewId: "<REVIEW_NODE_ID>"
    path: "path/to/file.md"
    subjectType: FILE
    body: "This file should be in a different directory."
  }) {
    thread {
      id
    }
  }
}'
```

**When to use file-level comments:**
- File is in the wrong directory
- File naming doesn't follow conventions
- File should be deleted or renamed
- General feedback about the file that isn't tied to a specific line

### Step 5: Submit the Review

When all comments are added, submit the review:

```bash
gh api graphql -f query='
mutation {
  submitPullRequestReview(input: {
    pullRequestReviewId: "<REVIEW_NODE_ID>"
    event: REQUEST_CHANGES
    body: "Brief summary here - see inline comments for details."
  }) {
    pullRequestReview {
      state
    }
  }
}'
```

**Event options:**
- `APPROVE` - Approve the PR
- `REQUEST_CHANGES` - Request changes
- `COMMENT` - General comment without approval/rejection

**Writing the review body:**
- **Don't repeat inline comments** - The details are already there; just point people to them
- **Keep it brief and human** - A sentence or two is fine. You're a helpful colleague, not a judge
- **Focus on the overall picture** - What's the main thing blocking approval, or why you're approving
- **Sound like a person** - "A few things to address before this is ready" beats "The following issues require resolution"

**Good examples:**
- "Looks good overall - just a couple small things to clean up. See inline comments."
- "Nice work! Left a few suggestions but nothing blocking."
- "A few things need addressing before we can merge - see comments."

**Avoid:**
- Bullet-pointed lists that duplicate your inline comments
- Formal summaries with "Required Changes" and "Suggestions" headers
- Repeating line numbers or file paths already in your comments

### Example: Complete Workflow

```bash
# 1. Get commit SHA
COMMIT_SHA=$(gh pr view 1021 --repo ansible/handbook --json headRefOid --jq '.headRefOid')

# 2. Create pending review
gh api repos/ansible/handbook/pulls/1021/reviews \
  --method POST \
  --input - <<EOF
{"commit_id": "$COMMIT_SHA", "body": "", "comments": []}
EOF

# 3. Get GraphQL review ID
REVIEW_ID=$(gh api graphql -f query='
query {
  repository(owner: "ansible", name: "handbook") {
    pullRequest(number: 1021) {
      reviews(states: PENDING, first: 1) {
        nodes { id }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviews.nodes[0].id')

# 4. Add comments (repeat as needed)
gh api graphql -f query="
mutation {
  addPullRequestReviewThread(input: {
    pullRequestReviewId: \"$REVIEW_ID\"
    path: \"path/to/file.md\"
    line: 25
    side: RIGHT
    body: \"Your comment here.\"
  }) {
    thread { id }
  }
}"

# 5. Submit review
gh api graphql -f query="
mutation {
  submitPullRequestReview(input: {
    pullRequestReviewId: \"$REVIEW_ID\"
    event: REQUEST_CHANGES
    body: \"A few things to address - see inline comments.\"
  }) {
    pullRequestReview { state }
  }
}"
```

### Why GraphQL?

The REST API for PR review comments is limited:
- Cannot easily add comments to an existing pending review
- The `/pulls/{pr}/comments` endpoint creates standalone comments, not pending review comments
- GraphQL's `addPullRequestReviewThread` mutation properly associates comments with a pending review