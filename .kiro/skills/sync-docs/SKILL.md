# Sync Docs Skill

Synchronize project documentation with current code state.

## Actions

### 1. Quality Assessment
Score each documentation file (0-100) across:
- Commands/workflows (20 pts)
- Architecture clarity (20 pts)
- Non-obvious patterns (15 pts)
- Conciseness (15 pts)
- Currency (15 pts)
- Actionability (15 pts)

Output quality report with grades (A-F) before making changes.

### 2. Steering & AGENT.md Sync
- Update AGENT.md and `.kiro/steering/steering.md` to reflect current state
- Verify commands are copy-paste ready against actual scripts

### 3. Architecture Doc Sync
- Update `docs/architecture.md` to reflect current system structure
- Add new components, update data flows, reflect infrastructure changes

### 4. Module Documentation Audit
- Scan all directories under `examples/`
- Create documentation for modules missing one
- Update existing module docs if out of date

### 5. Blog-Code Sync
- Compare `README.md` code snippets against actual `examples/` code
- Flag any mismatches

### 6. ADR Audit
- Check recent commits (`git log --oneline -20`)
- Suggest new ADRs for undocumented architectural decisions

### 7. Report
Output before/after quality scores and list of all changes.
