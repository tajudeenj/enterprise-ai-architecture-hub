import streamlit as st
import pandas as pd
from datetime import date
st.set_page_config(page_title='EA Intelligence Hub',layout='wide')
st.title('EA Intelligence Hub | Enterprise AI Architecture')
st.caption('Synthetic demonstration • Architecture recommendations require human validation')
if 'initiatives' not in st.session_state:
 st.session_state.initiatives=[{'Name':'HR Policy Assistant','Type':'AI enablement','Business':'HR','Capability':'Knowledge Retrieval','Application':'Fusion HCM','Target':'2027-Q2','Status':'Proposed','Value':120000},{'Name':'CRM Incident Intelligence','Type':'Enhancement','Business':'Operations','Capability':'Incident Management','Application':'Dynamics CRM / Oracle MPM','Target':'2027-Q3','Status':'Assessment','Value':90000},{'Name':'Core Banking AI Readiness','Type':'New initiative','Business':'Core Banking','Capability':'Customer Servicing','Application':'Core Banking (planned)','Target':'2028-Q1','Status':'Proposed','Value':0}]
assets=pd.DataFrame([('Entra ID','Identity','Shared SSO and access policies'),('APIC','Integration','API governance and routing'),('ESB','Integration','Existing enterprise integration'),('Model Gateway','AI platform','Proposed shared model access'),('AI Audit Service','Governance','Proposed centralized AI activity audit'),('Enterprise Retrieval','AI platform','Proposed permission-aware knowledge retrieval')],columns=['Asset','Category','Reuse opportunity'])
tabs=st.tabs(['Executive Dashboard','Register Initiative','Capability & Asset Catalogue','Architecture Recommendation','Governance','Roadmap & HLD'])
with tabs[0]:
 df=pd.DataFrame(st.session_state.initiatives);a,b,c=st.columns(3);a.metric('Initiatives',len(df));b.metric('Business areas',df.Business.nunique());c.metric('Illustrative annual benefit (AED)',f'{df.Value.sum():,}');st.dataframe(df,use_container_width=True)
with tabs[1]:
 with st.form('register'):
  name=st.text_input('Initiative name');typ=st.selectbox('Change type',['New initiative','New product','Enhancement','AI enablement','Replacement']);business=st.text_input('Business unit');cap=st.text_input('Business capability');application=st.text_input('Affected application');target=st.selectbox('Target quarter',[f'{y}-Q{q}' for y in [2027,2028] for q in range(1,5)]);value=st.number_input('Expected annual benefit AED (estimate)',min_value=0,step=10000);submitted=st.form_submit_button('Register initiative')
  if submitted:
   if name and business and cap and application:
    st.session_state.initiatives.append(dict(Name=name,Type=typ,Business=business,Capability=cap,Application=application,Target=target,Status='Proposed',Value=value));st.success('Initiative registered in this session')
   else:st.error('Fill all required text fields')
with tabs[2]:
 st.subheader('Reusable enterprise assets');st.dataframe(assets,use_container_width=True);st.info('Catalogue is illustrative. Replace with verified application, API and infrastructure inventories.')
with tabs[3]:
 df=pd.DataFrame(st.session_state.initiatives);chosen=st.selectbox('Select initiative',df.Name,key='recommend');item=df[df.Name==chosen].iloc[0]
 st.subheader('Preliminary EA assessment')
 st.write('Business capability:',item.Capability,'| Affected application:',item.Application)
 st.write('Potential reusable assets: Entra ID, APIC, ESB. For AI solutions, assess shared model gateway and audit service.')
 st.warning('Rule-based suggestions only. Validate functional fit, information classification, hosting constraints, costs and ownership before an architecture decision.')
 st.write('Recommended sequence: 1. Capability overlap check → 2. Existing application AI feasibility → 3. Reuse assessment → 4. Options and TCO → 5. Control reviews → 6. EA recommendation → 7. Funding decision.')
with tabs[4]:
 st.subheader('Architecture review gates')
 for x in ['Business sponsorship','EA capability and duplication review','GISD security assessment','GSD data movement/control review','Infrastructure architecture review','Data governance / model risk (if applicable)','CIO / investment approval']:
  st.checkbox(x,key='gate_'+x)
 st.caption('Checkboxes demonstrate review tracking, not formal approvals. Production version requires named approvers, evidence, immutable audit and role-based permissions.')
with tabs[5]:
 df=pd.DataFrame(st.session_state.initiatives);st.subheader('Target roadmap');st.dataframe(df[['Name','Target','Status']],use_container_width=True)
 st.subheader('Generated conceptual HLD — selected initiative')
 chosen=st.selectbox('Initiative',df.Name,key='hld');item=df[df.Name==chosen].iloc[0]
 st.code(f'''BUSINESS: {item.Business}\nCAPABILITY: {item.Capability}\nAPPLICATION: {item.Application}\nTARGET: {item.Target}\n\nBusiness User -> Enterprise Identity (Entra ID)\n    -> Approved Application / API Layer (APIC)\n    -> AI Model Access (proposed, subject to approval)\n    -> Approved Data Sources (classification & access review required)\n    -> Audit / Monitoring (proposed)\n\nHLD STATUS: CONCEPT ONLY — network zones, ports, data flows,\ntrust boundaries and control signoffs are NOT YET VALIDATED.''')
 st.download_button('Download conceptual HLD text',data=f'EA Concept HLD\nInitiative: {chosen}\nApplication: {item.Application}\nTarget: {item.Target}\nStatus: Unvalidated concept\n',file_name='ea_concept_hld.txt')
