from pathlib import Path
import hashlib,json
import duckdb
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def db():return duckdb.connect(str(ROOT/'data/processed/serviceops.duckdb'),read_only=True)
def test_snapshot_checksum():
 m=json.loads((ROOT/'data/raw/manifest.json').read_text())
 assert hashlib.sha256((ROOT/'data/raw/requests.json').read_bytes()).hexdigest()==m['sha256']
def test_unique_grain_and_manifest_count():
 with db() as c:
  n,unique=c.execute('select count(*),count(distinct request_id) from requests').fetchone()
 assert n==unique==json.loads((ROOT/'data/raw/manifest.json').read_text())['rows']
def test_cohort():
 with db() as c:
  assert c.execute("select count(*) from requests where agency!='DSNY' or created_at<'2025-01-01' or created_at>='2025-04-01'").fetchone()[0]==0
def test_reconciliation():
 with db() as c:
  n,closed,nonclosed=c.execute('select count(*),count(*) filter(where is_closed_status),count(*) filter(where not is_closed_status) from requests').fetchone()
  assert n==closed+nonclosed
  assert c.execute('select sum(requests) from segment_summary').fetchone()[0]==n
def test_duration_rules():
 with db() as c:
  assert c.execute('select count(*) from requests where closure_hours<0 or open_age_hours<0').fetchone()[0]==0
  assert c.execute('select count(*) from requests where closure_hours is not null and (not is_closed_status or invalid_created or invalid_closed)').fetchone()[0]==0
  assert c.execute('select count(*) from requests where is_closed_status and open_age_hours is not null').fetchone()[0]==0
def test_exports_reconcile():
 d=pd.read_csv(ROOT/'data/processed/requests.csv')
 assert len(d)==json.loads((ROOT/'reports/audit.json').read_text())['raw_rows']
def test_hand_calculated_fixture(tmp_path):
 # Execute the actual production SQL against a tiny deliberately dirty dataset.
 from datetime import datetime
 folder=tmp_path/'data/raw';folder.mkdir(parents=True)
 rows=[]
 for i,(status,start,end) in enumerate([
 ('Closed','2025-01-01','2025-01-02'),('Closed','2025-01-01','2025-01-04'),
 ('Closed','2025-01-01',None),('Open','2025-01-01',None),
 ('Closed','2025-01-02','2025-01-01')]):
  rows.append(dict(unique_key=str(i),created_date=start,closed_date=end,agency='DSNY',complaint_type='Example',borough='BRONX',status=status))
 source=folder/'requests.json';source.write_text(json.dumps(rows))
 sql=(ROOT/'sql/model.sql').read_text().replace('data/raw/requests.json',str(source))
 c=duckdb.connect()
 for statement in sql.split(';'):
  if statement.strip():
   c.execute(statement,{'snapshot':datetime(2025,2,1)} if '$snapshot' in statement else None)
 result=c.execute('select count(*),sum(is_closed_status::int),median(closure_hours),sum(invalid_closed::int) from requests').fetchone()
 assert result==(5,4,48.0,1)
 assert c.execute('select count(closure_hours) from requests').fetchone()[0]==2
def test_dashboard_and_filter():
 from streamlit.testing.v1 import AppTest
 at=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
 assert not at.exception
 assert at.metric[0].value=='73,362'
 at.multiselect[0].set_value(['Snow or Ice']).run(timeout=30)
 assert not at.exception
 assert at.metric[0].value=='7,990'
 at.multiselect[1].set_value(['BROOKLYN']).run(timeout=30)
 assert at.metric[0].value=='3,335'
 assert at.metric[2].value=='4.36 days'
