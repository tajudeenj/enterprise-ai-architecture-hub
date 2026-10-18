"""SQLite-backed enterprise architecture repository. Synthetic seed data only."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB = Path(os.environ.get("EA_HUB_DB", "ea_hub.sqlite3"))

@contextmanager
def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS capabilities(
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, domain TEXT NOT NULL, owner TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS applications(
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, owner TEXT NOT NULL,
            lifecycle TEXT NOT NULL, ai_readiness TEXT NOT NULL, hosting TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS assets(
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, kind TEXT NOT NULL,
            status TEXT NOT NULL, owner TEXT NOT NULL, notes TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS relations(
            id INTEGER PRIMARY KEY, source_type TEXT NOT NULL, source_id INTEGER NOT NULL,
            target_type TEXT NOT NULL, target_id INTEGER NOT NULL, relation TEXT NOT NULL,
            UNIQUE(source_type,source_id,target_type,target_id,relation));
        CREATE TABLE IF NOT EXISTS initiatives(
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, business TEXT NOT NULL,
            capability_id INTEGER NOT NULL REFERENCES capabilities(id),
            application_id INTEGER NOT NULL REFERENCES applications(id),
            change_type TEXT NOT NULL, description TEXT NOT NULL, target_quarter TEXT NOT NULL,
            benefit_aed REAL NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'Proposed');
        CREATE TABLE IF NOT EXISTS reviews(
            id INTEGER PRIMARY KEY, initiative_id INTEGER NOT NULL REFERENCES initiatives(id),
            function TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending',
            reviewer TEXT NOT NULL DEFAULT '', evidence TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(initiative_id,function));
        CREATE TABLE IF NOT EXISTS milestones(
            id INTEGER PRIMARY KEY, initiative_id INTEGER NOT NULL REFERENCES initiatives(id),
            title TEXT NOT NULL, target_quarter TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Planned');
        CREATE TABLE IF NOT EXISTS decisions(
            id INTEGER PRIMARY KEY, initiative_id INTEGER NOT NULL REFERENCES initiatives(id),
            option_name TEXT NOT NULL, rationale TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'Draft',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        """)
        if db.execute("SELECT COUNT(*) FROM capabilities").fetchone()[0]:
            return
        db.executemany("INSERT INTO capabilities(name,domain,owner) VALUES(?,?,?)",[
            ("Knowledge Retrieval","Corporate Services","HR"),
            ("Integration Incident Management","Technology Operations","IT Operations"),
            ("Customer Servicing","Retail Banking","Core Banking")])
        db.executemany("INSERT INTO applications(name,owner,lifecycle,ai_readiness,hosting) VALUES(?,?,?,?,?)",[
            ("Fusion HCM","HR IT","Active","Assessment required","SaaS"),
            ("Dynamics CRM / Oracle MPM","Property Leasing IT","Active","Assessment required","Hybrid"),
            ("Core Banking (planned)","Core Banking IT","Planned","Unknown","TBD")])
        db.executemany("INSERT INTO assets(name,kind,status,owner,notes) VALUES(?,?,?,?,?)",[
            ("Entra ID","Identity","Existing","Identity Team","SSO; access review required"),
            ("APIC","API Gateway","Existing","Integration Team","Approved gateway pattern to be verified"),
            ("ESB","Integration","Existing","Integration Team","Existing middleware"),
            ("AI Model Gateway","AI Platform","Proposed","TBD","Not approved"),
            ("Enterprise AI Audit","Observability","Proposed","TBD","Not approved")])
        db.executemany("""INSERT INTO initiatives(name,business,capability_id,application_id,change_type,description,target_quarter,benefit_aed)
            VALUES(?, ?, (SELECT id FROM capabilities WHERE name=?), (SELECT id FROM applications WHERE name=?), ?, ?, ?, ?)""",[
            ("HR Policy Assistant","HR","Knowledge Retrieval","Fusion HCM","AI enablement","Permission-aware policy retrieval","2027-Q2",120000),
            ("CRM Incident Intelligence","Operations","Integration Incident Management","Dynamics CRM / Oracle MPM","Enhancement","Integration incident triage","2027-Q3",90000),
            ("Core Banking AI Readiness","Core Banking","Customer Servicing","Core Banking (planned)","New initiative","Evaluate AI enablement options","2028-Q1",0)])
        db.executemany("""INSERT INTO relations(source_type,source_id,target_type,target_id,relation)
            VALUES('application',(SELECT id FROM applications WHERE name=?),'asset',(SELECT id FROM assets WHERE name=?),?)""",[
            ("Fusion HCM","Entra ID","authenticates_via"),
            ("Dynamics CRM / Oracle MPM","APIC","integrates_via"),
            ("Dynamics CRM / Oracle MPM","ESB","integrates_via")])
        for row in db.execute("SELECT id FROM initiatives").fetchall():
            create_reviews(db,row["id"])

REVIEW_FUNCTIONS = [
    "EA Architecture","GISD Security","GSD Data Controls",
    "Infrastructure Architecture","Data Governance","Investment Approval"
]

def create_reviews(db, initiative_id):
    db.executemany("INSERT OR IGNORE INTO reviews(initiative_id,function) VALUES(?,?)",
                   [(initiative_id, f) for f in REVIEW_FUNCTIONS])

def rows(query, params=()):
    with connect() as db:
        return [dict(r) for r in db.execute(query,params).fetchall()]

def execute(query, params=()):
    with connect() as db:
        cursor=db.execute(query,params)
        return cursor.lastrowid

def register(name,business,capability_id,application_id,change_type,description,target_quarter,benefit):
    with connect() as db:
        cur=db.execute("""INSERT INTO initiatives
            (name,business,capability_id,application_id,change_type,description,target_quarter,benefit_aed)
            VALUES(?,?,?,?,?,?,?,?)""",
            (name,business,capability_id,application_id,change_type,description,target_quarter,benefit))
        create_reviews(db,cur.lastrowid)
        return cur.lastrowid

def impact(application_id):
    """Relationships are explicit, not inferred from undocumented infrastructure."""
    return rows("""SELECT a.name asset, a.kind, a.status, r.relation
        FROM relations r JOIN assets a ON a.id=r.target_id
        WHERE r.source_type='application' AND r.target_type='asset' AND r.source_id=?""",(application_id,))

def hld(initiative):
    related=impact(initiative["application_id"])
    lines=["flowchart TD", '    USER["Business user"]', '    APP["'+safe(initiative["application"])+'"]',
           '    USER --> APP']
    for n,r in enumerate(related):
        lines.append('    AS'+str(n)+'["'+safe(r["asset"])+' ('+safe(r["status"])+')"]')
        lines.append('    APP --> AS'+str(n))
    lines.append('    REVIEW["GISD / GSD / Infrastructure validation pending"]')
    lines.append('    APP -.-> REVIEW')
    return "\n".join(lines)

def safe(s):
    return str(s).replace('"',"'").replace("\n"," ")[:90]
