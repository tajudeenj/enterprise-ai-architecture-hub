# EA Intelligence Hub — Phase 2 POC

A runnable Enterprise AI Architecture portfolio and governance prototype using **Streamlit + SQLite** and **synthetic banking data**.

## Windows 11 / Python 3.13

```powershell
git clone https://github.com/tajudeenj/enterprise-ai-architecture-hub.git
cd enterprise-ai-architecture-hub
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If you previously cloned, run `git pull` inside the project folder before starting.

## Phase 2 features

- Persistent SQLite repository (`ea_hub.sqlite3`, created on first run)
- Synthetic business capability, application and reusable asset catalogue
- AI initiative registration with capability/application references
- Explicit application-to-asset dependency relationships and impact view
- Review tracking across EA, GISD, GSD, Infrastructure, Data Governance and Investment
- 2027–2028 initiative roadmap
- Downloadable **conceptual Mermaid HLD** from recorded relationships
- Synthetic sample portfolio preloaded once, when the database is initialized

## Scope and limitations

**Demonstration only; not production ready.** Review statuses are not authenticated approvals. Architecture relationships are manually captured, not automatically discovered. HLD is a conceptual graph and must be validated by architecture/security teams before use. There is no RBAC, approval evidence immutability, model integration, automated network discovery, or cost estimation engine. Do not enter bank production data or confidential information.

## Next milestones

1. Authentication, RBAC, audit trail, review ownership and lifecycle
2. Import from CMDB/API inventory and graph impact analysis
3. Multi-option feasibility/TCO and architecture decision records
4. Validated diagram generation from approved infrastructure metadata
5. Portfolio roadmap with dependencies, baselines and delivery progress
