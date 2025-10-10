# Jira Create Command

This command helps you create a new Jira issue by prompting for all necessary information and using the Jira MCP server.

## Usage

Type `/jira-create` or `/jira create` to start the interactive issue creation process.

## What this command does

### **Prompts for required information:**
- Issue summary/title
- Detailed description
- Project key (defaults to "ACM")
- Priority level (defaults to Normal)
- Security level (defaults to "Red Hat Employee")
- **Parent issue** (if creating sub-task)
- Due date (YYYY-MM-DD format)
- Components (with intelligent suggestions)
- Labels (including Train-* labels)
- Fix version/target release
- Assignee (suggests "assign to me")
- Work type
- Original time estimate
- Story points
- Target Start (defaults to today's date)
- Components

## Component Intelligence

The command automatically suggests appropriate components based on keywords:
- "virtualization", "vm", "kubevirt" → "Container Native Virtualization"
- "observability", "monitoring", "metrics" → "Observability"
- "multicluster", "cluster management" → "Multicluster"
- "policy", "governance" → "Governance"
- "applications", "app management" → "Application Management"
- "infrastructure", "bare metal" → "Infrastructure"
- "search", "console" → "Search"

**Sub-task Inheritance:**
- Sub-tasks automatically inherit the project from their parent
- Components, labels, and fix versions can be inherited or set independently
- The parent issue key is automatically set in the `parent` field

**Validation:**
- Ensures the parent issue exists before creating the sub-task
- Validates that the parent issue is not already a sub-task (sub-tasks can't have sub-tasks)

## Error Handling

The command validates:
- Date formats (YYYY-MM-DD)
- Time estimates (whole numbers only)
- Git commit SHAs (40 or 64 hex characters)
- Required field completion

If errors occur, helpful suggestions will be provided for correction.
