"""ServiceOps local dashboard. Run: python -m streamlit run app.py"""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='ServiceOps | NYC311',page_icon='◷',layout='wide')
st.markdown('''<style>
.block-container{padding:2.5rem 2rem 1rem;max-width:1500px}
h1{font-size:1.65rem!important;font-weight:600!important;letter-spacing:-.3px!important;padding-bottom:.2rem!important}
h2,h3{font-size:1rem!important;font-weight:600!important}
[data-testid="stMetric"]{padding:8px 0 12px;border-bottom:1px solid #d6d9dd}
[data-testid="stMetricValue"]{font-size:1.75rem!important;font-weight:500}
[data-testid="stMetricLabel"]{font-size:.85rem;color:#525b66}
[data-testid="stSidebar"]{background:#f6f7f8}
[data-testid="stSidebar"] .block-container{padding-top:2rem}
@media(max-width:600px){.block-container{padding:2.5rem 1rem 1rem}}
</style>''',unsafe_allow_html=True)
@st.cache_data
def load():
 return pd.read_csv(ROOT/'data/processed/requests.csv'),json.loads((ROOT/'reports/audit.json').read_text())
try:df,audit=load()
except FileNotFoundError:
 st.error('Build the data first: python src/build.py');st.stop()
st.title('Sanitation service requests')
st.caption('NYC311 / DSNY   ·   Created Jan–Mar 2025   ·   Snapshot 23 Nov 2026')
with st.sidebar:
 st.header('Filters')
 problems=st.multiselect('Request type',sorted(df.problem.unique()),placeholder='All request types')
 boroughs=st.multiselect('Borough',sorted(df.borough.unique()),placeholder='All boroughs')
 st.caption('An empty selection includes every value. Filters apply to every chart, metric and download below.')
 st.divider();st.markdown('**Snapshot**');st.write(audit['snapshot_utc'][:10]+' UTC')
 st.caption('Live source is mutable. This app uses the packaged frozen snapshot, never an automatic refresh.')
 st.markdown('[Source and definitions](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)')
f=df.copy()
if problems:f=f[f.problem.isin(problems)]
if boroughs:f=f[f.borough.isin(boroughs)]
if f.empty:st.warning('No requests match these filters.');st.stop()
valid=f.closure_hours.dropna();nonclosed=f[~f.is_closed_status]
a,b,c,d=st.columns(4)
a.metric('Requests',f'{len(f):,}')
b.metric('Closed status',f'{f.is_closed_status.mean():.1%}')
c.metric('Median closure',f'{valid.median()/24:.2f} days' if len(valid) else 'No valid cases')
d.metric('P90 closure',f'{valid.quantile(.9)/24:.2f} days' if len(valid) else 'No valid cases')
st.caption(f'Duration base: {len(valid):,} valid closed records / {len(f):,} selected requests. Closure is an administrative record status, not proof of resolution.')
tab1,tab2,tab3=st.tabs(['Demand & closure','Unresolved at extraction','Quality & data'])
with tab1:
 st.subheader('Request type × borough')
 st.caption('Compare boroughs within the same request type. Segments with fewer than 100 valid closures are flagged. Descriptive differences only.')
 seg=f.groupby(['problem','borough']).agg(Requests=('request_id','size'),Valid_closed=('closure_hours','count'),Median_hours=('closure_hours','median'),P90_hours=('closure_hours',lambda s:s.quantile(.9))).reset_index()
 seg['Sample warning']=seg.Valid_closed.map(lambda n:'Small: <100 closed cases' if n<100 else '')
 st.dataframe(seg.sort_values('Requests',ascending=False),hide_index=True,width='stretch',height=280,column_config={'problem':'Request type','borough':'Borough','Valid_closed':st.column_config.NumberColumn('Valid closed',format='%d'),'Median_hours':st.column_config.NumberColumn('Median (h)',format='%.1f'),'P90_hours':st.column_config.NumberColumn('P90 (h)',format='%.1f')})
 st.divider()
 left,right=st.columns([1,1])
 with left:
  st.subheader('Request volume by type')
  volume=f.groupby('problem').size().nlargest(10).sort_values().rename('Requests').reset_index()
  fig=px.bar(volume,x='Requests',y='problem',orientation='h',color_discrete_sequence=['#526d82'])
  fig.update_layout(yaxis_title=None,xaxis_title='Requests',height=340,margin=dict(l=0,r=12,t=10,b=0))
  st.plotly_chart(fig,width='stretch')
 with right:
  st.subheader('Median time to closure')
  st.caption('Top 10 request types by volume; valid closed cases only. Different request types are not equivalent work.')
  top=volume.problem.tolist()
  durations=f[f.problem.isin(top)].groupby('problem').closure_hours.agg(['median','count']).sort_values('median').reset_index()
  durations['Median days']=durations['median']/24
  fig=px.bar(durations,x='Median days',y='problem',orientation='h',color_discrete_sequence=['#768797'],hover_data=['count'])
  fig.update_layout(yaxis_title=None,height=306,margin=dict(l=0,r=12,t=10,b=0));st.plotly_chart(fig,width='stretch')
with tab2:
 st.subheader(f'{len(nonclosed):,} requests have non-closed status at extraction')
 st.warning('This is not the backlog as of March 2025. Status is the source state when extracted in November 2026. Missing closure can reflect unresolved work or stale administrative records.')
 if nonclosed.empty:st.info('No non-closed cases in the current selection.')
 else:
  ages=pd.cut(nonclosed.open_age_hours/24,bins=[-1,7,30,90,365,float('inf')],labels=['0–7 days','8–30 days','31–90 days','91–365 days','Over 365 days'])
  age=ages.value_counts(sort=False).rename_axis('Age').reset_index(name='Requests')
  st.plotly_chart(px.bar(age,x='Age',y='Requests',color_discrete_sequence=['#526d82']),width='stretch')
  st.dataframe(nonclosed[['request_id','problem','borough','status','open_age_hours']].sort_values('open_age_hours',ascending=False),hide_index=True,width='stretch')
with tab3:
 st.subheader('Data checks and metric definitions')
 st.write('No address or resolution free text is included. Unique request ID is the grain; rows are never multiplied by joins.')
 st.json(audit)
 st.markdown('**Definitions:** Closed share = Closed-status rows / all requests. Median/P90 = valid closed rows only. Open age = extraction timestamp minus created timestamp for non-closed rows. Invalid dates remain in audit but never enter duration metrics.')
 st.info('Due date is an expected agency update date, not a universal resolution deadline. No invented SLA-breach rate is reported. See docs/METRICS.md for censoring and timezone limits.')
 st.download_button('Download filtered request data',f.to_csv(index=False).encode(),'serviceops_filtered.csv','text/csv')
st.divider()
st.caption('Source: NYC Open Data / NYC311. Portfolio project, not an official agency assessment. Methods, limitations and authorship: README and docs/METRICS.md.')
