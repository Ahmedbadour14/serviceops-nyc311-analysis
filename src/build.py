"""Build audited local metrics and portable exports from the frozen snapshot."""
from pathlib import Path
import hashlib,json,os
from datetime import datetime
import duckdb
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
def build():
 os.chdir(ROOT)
 manifest=json.loads(Path('data/raw/manifest.json').read_text())
 raw=Path('data/raw/requests.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=manifest['sha256']:raise ValueError('Raw snapshot checksum mismatch')
 snapshot=datetime.fromisoformat(manifest['completed_utc']).astimezone(ZoneInfo('America/New_York')).replace(tzinfo=None)
 Path('data/processed').mkdir(parents=True,exist_ok=True);Path('reports').mkdir(exist_ok=True)
 con=duckdb.connect('data/processed/serviceops.duckdb')
 sql=Path('sql/model.sql').read_text()
 for statement in sql.split(';'):
  if statement.strip():
   if '$snapshot' in statement:con.execute(statement,{'snapshot':snapshot})
   else:con.execute(statement)
 for table in ['requests','segment_summary','weekly_volume']:
  con.execute(f"COPY {table} TO 'data/processed/{table}.csv' (HEADER, DELIMITER ',')")
 audit=con.execute('''SELECT count(*) AS raw_rows,count(distinct request_id) AS unique_ids,
 count(*) FILTER(WHERE invalid_created) AS invalid_created,
 count(*) FILTER(WHERE invalid_closed) AS invalid_closed,
 count(*) FILTER(WHERE is_closed_status AND closure_hours IS NULL) AS closed_without_valid_duration,
 count(*) FILTER(WHERE NOT is_closed_status AND closed_at IS NOT NULL) AS nonclosed_with_close_date,
 count(*) FILTER(WHERE closure_hours IS NOT NULL) AS valid_closed,
 count(*) FILTER(WHERE NOT is_closed_status) AS nonclosed_status,
 count(*) FILTER(WHERE status='Unknown') AS unknown_status,
 median(closure_hours) AS median_hours,quantile_cont(closure_hours,0.9) AS p90_hours
 FROM requests''').fetchdf().iloc[0].to_dict()
 audit={k:(float(v) if k.endswith('hours') else int(v)) for k,v in audit.items()}
 audit.update(snapshot_utc=manifest['completed_utc'],sha256=manifest['sha256'])
 Path('reports/audit.json').write_text(json.dumps(audit,indent=2))
 # Same-type comparisons: baseline is request-weighted raw duration within that type,
 # not an unweighted mean of borough medians. Candidate list is investigative, not causal.
 candidates=con.execute('''WITH baseline AS(SELECT problem,median(closure_hours) AS type_median FROM requests GROUP BY problem)
 SELECT s.*,b.type_median,median_hours-b.type_median AS median_gap_hours
 FROM segment_summary s JOIN baseline b USING(problem)
 WHERE valid_closure_count>=100 AND type_median>0 AND median_hours>=type_median*1.25 AND median_hours-type_median>=24
 AND borough NOT IN ('Unknown','Unspecified')
 ORDER BY requests DESC LIMIT 8''').fetchdf()
 candidates.to_csv('reports/investigation_candidates.csv',index=False)
 print(json.dumps(audit,indent=2));print(candidates[['problem','borough','requests','median_hours','type_median']].to_string(index=False))
 con.close()
if __name__=='__main__':build()
