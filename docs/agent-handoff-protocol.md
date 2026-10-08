# Agent Handoff Protocol

Every implementation task leaves persistent context for the next task.

## Required report fields
1. What was implemented
2. What was learned
3. Decisions and rationale
4. Interfaces for downstream tasks
5. Tests and verification
6. Known limitations or concerns
7. Next-agent instructions

Detailed reports live under `.superpowers/sdd/<plan-workspace>/` during execution. The progress ledger records task completion, review findings and rulings. Agents must read their task brief first and then only the handoff reports explicitly referenced for their interfaces.

Do not paste the entire project history into a subagent prompt. Persistent files are the source of cross-task context.
