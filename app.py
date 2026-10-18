import sqlite3
import streamlit as st
import pandas as pd
import ea_repository as er

st.set_page_config(page_title="EA Intelligence Hub",layout="wide")
er.init()
st.title("EA Intelligence Hub")
st.caption("Phase 2 • Persistent architecture repository • Synthetic demonstration data • No production bank information")

def dataframe(sql,params=()):
    return pd.DataFrame(er.rows(sql,params))
def options(table):
    return er.rows("SELECT id,name FROM "+table+" ORDER BY name")
def label(items,i):
    return next(x["name"] for x in items if x["id"]==i)

tabs=st.tabs(["Executive Dashboard","Initiative Intake","Application Landscape","Capabilities & Reuse","Impact Analysis","Governance","Roadmap & HLD"])
with tabs[0]:
    portfolio=dataframe("""SELECT i.id,i.name,i.business,c.name capability,a.name application,
      i.change_type,i.target_quarter,i.status,i.benefit_aed
      FROM initiatives i JOIN capabilities c ON c.id=i.capability_id
      JOIN applications a ON a.id=i.application_id ORDER BY i.id""")
    a,b,c,d=st.columns(4)
    a.metric("Initiatives",len(portfolio))
    b.metric("Applications",len(er.rows("SELECT id FROM applications")))
    c.metric("Reusable assets",len(er.rows("SELECT id FROM assets")))
    d.metric("Estimated benefit (AED)",f'{portfolio["benefit_aed"].sum():,.0f}' if not portfolio.empty else "0")
    st.dataframe(portfolio,use_container_width=True,hide_index=True)
    st.warning("Benefits are synthetic estimates, not validated savings. Governance reviews are demonstration records, not official bank approvals.")
with tabs[1]:
    caps=options("capabilities");apps=options("applications")
    with st.form("intake",clear_on_submit=True):
        name=st.text_input("Initiative name")
        business=st.text_input("Business division")
        cap=st.selectbox("Business capability",[x["id"] for x in caps],format_func=lambda i:label(caps,i))
        app=st.selectbox("Affected application",[x["id"] for x in apps],format_func=lambda i:label(apps,i))
        change=st.selectbox("Initiative type",["New project","New product","Enhancement","AI enablement","Replacement"])
        desc=st.text_area("Business objective and proposed AI functionality")
        target=st.selectbox("Target quarter",[f"{y}-Q{q}" for y in [2027,2028] for q in range(1,5)])
        benefit=st.number_input("Estimated annual benefit AED",min_value=0,step=10000)
        if st.form_submit_button("Register and create review gates"):
            if not name.strip() or not business.strip():
                st.error("Initiative name and business division are required")
            else:
                try:
                    er.register(name.strip(),business.strip(),cap,app,change,desc,target,benefit)
                    st.success("Saved to SQLite and review gates initialized")
                except sqlite3.IntegrityError:
                    st.error("An initiative with that name already exists")
with tabs[2]:
    st.subheader("Application portfolio")
    st.dataframe(dataframe("SELECT * FROM applications ORDER BY name"),use_container_width=True,hide_index=True)
    with st.form("add_app"):
        name=st.text_input("Application name");owner=st.text_input("Application owner")
        lifecycle=st.selectbox("Lifecycle",["Active","Planned","Retiring","Retired"])
        readiness=st.selectbox("AI readiness",["Unknown","Assessment required","Feasible","Not feasible"])
        hosting=st.text_input("Hosting / infrastructure")
        if st.form_submit_button("Add application"):
            if name and owner and hosting:
                try:
                    er.execute("INSERT INTO applications(name,owner,lifecycle,ai_readiness,hosting) VALUES(?,?,?,?,?)",(name,owner,lifecycle,readiness,hosting))
                    st.success("Application added; refresh to select it elsewhere")
                except sqlite3.IntegrityError: st.error("Application already exists")
            else:st.error("Name, owner and hosting are required")
with tabs[3]:
    st.subheader("Business capability catalogue")
    st.dataframe(dataframe("SELECT * FROM capabilities"),use_container_width=True,hide_index=True)
    with st.form("add_cap"):
        name=st.text_input("Capability name");domain=st.text_input("Business domain");owner=st.text_input("Capability owner")
        if st.form_submit_button("Add capability"):
            if name and domain and owner:
                try:
                    er.execute("INSERT INTO capabilities(name,domain,owner) VALUES(?,?,?)",(name,domain,owner))
                    st.success("Capability saved; refresh to select")
                except sqlite3.IntegrityError:st.error("Capability already exists")
            else:st.error("All fields required")
    st.subheader("Reusable technology and services")
    st.dataframe(dataframe("SELECT * FROM assets"),use_container_width=True,hide_index=True)
    with st.form("add_asset"):
        name=st.text_input("Asset / reusable service name");kind=st.text_input("Asset type")
        status=st.selectbox("Status",["Existing","Proposed","Retiring"])
        owner=st.text_input("Asset owner");notes=st.text_area("Purpose / constraints")
        if st.form_submit_button("Add asset"):
            if name and kind and owner:
                try:
                    er.execute("INSERT INTO assets(name,kind,status,owner,notes) VALUES(?,?,?,?,?)",(name,kind,status,owner,notes))
                    st.success("Asset saved; refresh to link it")
                except sqlite3.IntegrityError:st.error("Asset already exists")
            else:st.error("Name, type and owner required")
with tabs[4]:
    apps=options("applications");assets=options("assets")
    appid=st.selectbox("Application to assess",[x["id"] for x in apps],format_func=lambda i:label(apps,i),key="impactapp")
    st.write("Verified-in-repository relationships (synthetic seeds are not verified against live systems):")
    st.dataframe(pd.DataFrame(er.impact(appid)),use_container_width=True,hide_index=True)
    st.subheader("Register application-to-asset dependency")
    with st.form("link"):
        assetid=st.selectbox("Asset",[x["id"] for x in assets],format_func=lambda i:label(assets,i))
        relation=st.selectbox("Relationship",["integrates_via","authenticates_via","hosted_on","depends_on","observed_by"])
        if st.form_submit_button("Save dependency"):
            er.execute("""INSERT OR IGNORE INTO relations(source_type,source_id,target_type,target_id,relation)
              VALUES('application',?,'asset',?,?)""",(appid,assetid,relation))
            st.success("Dependency recorded; refresh to see changes")
    st.subheader("Preliminary reuse recommendation")
    st.info("Review existing API, identity and integration assets before procuring or building new ones. No automated feasibility approval is implied.")
with tabs[5]:
    its=er.rows("SELECT id,name FROM initiatives ORDER BY name")
    iid=st.selectbox("Initiative",[x["id"] for x in its],format_func=lambda i:label(its,i),key="reviews")
    reviews=er.rows("SELECT * FROM reviews WHERE initiative_id=? ORDER BY id",(iid,))
    st.dataframe(pd.DataFrame(reviews),use_container_width=True,hide_index=True)
    with st.form("review"):
        function=st.selectbox("Review function",[r["function"] for r in reviews])
        status=st.selectbox("Recorded review status",["Pending","In review","Approved","Rejected","Changes requested"])
        reviewer=st.text_input("Reviewer name (demo only)")
        evidence=st.text_area("Review reference / evidence (demo only)")
        if st.form_submit_button("Record review status"):
            if status in ["Approved","Rejected"] and (not reviewer.strip() or not evidence.strip()):
                st.error("Reviewer and evidence reference required for final review status")
            else:
                er.execute("""UPDATE reviews SET status=?,reviewer=?,evidence=?,updated_at=CURRENT_TIMESTAMP
                    WHERE initiative_id=? AND function=?""",(status,reviewer,evidence,iid,function))
                st.success("Review record updated (not an authenticated approval)")
with tabs[6]:
    st.subheader("2027–2028 roadmap")
    st.dataframe(dataframe("SELECT name,target_quarter,status FROM initiatives ORDER BY target_quarter"),use_container_width=True,hide_index=True)
    items=er.rows("""SELECT i.*,a.name application,c.name capability FROM initiatives i
        JOIN applications a ON a.id=i.application_id
        JOIN capabilities c ON c.id=i.capability_id ORDER BY i.name""")
    iid=st.selectbox("Generate conceptual HLD for",[x["id"] for x in items],format_func=lambda i:next(x["name"] for x in items if x["id"]==i))
    item=next(x for x in items if x["id"]==iid)
    diagram=er.hld(item)
    st.code(diagram,language="mermaid")
    st.download_button("Download Mermaid HLD diagram",diagram,file_name="concept_hld.mmd",mime="text/plain")
    st.caption("Draft relationship view only. Not an approved infrastructure/network HLD. No ports, zones, encryption, data classification or security signoff is inferred.")
