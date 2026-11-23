"""Local-only dashboard server. No external hosting or accounts."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json,os
import duckdb
ROOT=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT/'web'),**kw)
 def do_GET(self):
  u=urlparse(self.path)
  if u.path!='/api':return super().do_GET()
  q=parse_qs(u.query);params=[];where='TRUE'
  for field in ['problem','borough']:
   if q.get(field,[''])[0]:where+=' AND '+field+'=?';params.append(q[field][0])
  c=duckdb.connect(str(ROOT/'data/processed/serviceops.duckdb'),read_only=True)
  def rows(sql,args=None):
   cur=c.execute(sql,params if args is None else args)
   return [dict(zip([x[0] for x in cur.description],r)) for r in cur.fetchall()]
  data={'options':{'problem':[x['problem'] for x in rows('select distinct problem from requests order by 1',[])],'borough':[x['borough'] for x in rows('select distinct borough from requests order by 1',[])]}}
  base=' FROM requests WHERE '+where
  data['metrics']=rows('SELECT count(*) n,sum(is_closed_status::int) closed,count(closure_hours) AS valid_count,median(closure_hours)/24 median,quantile_cont(closure_hours,0.9)/24 p90,sum((NOT is_closed_status)::int) unresolved'+base)[0]
  data['volume']=rows('SELECT problem,count(*) n,median(closure_hours)/24 median,count(closure_hours) AS valid_count'+base+' GROUP BY 1 ORDER BY n DESC LIMIT 8')
  data['segments']=rows('SELECT borough,count(*) n,median(closure_hours)/24 median,quantile_cont(closure_hours,0.9)/24 p90,count(closure_hours) AS valid_count'+base+' GROUP BY 1 ORDER BY n DESC')
  reference_where='problem=?' if q.get('problem',[''])[0] else 'TRUE'
  reference_args=[q['problem'][0]] if q.get('problem',[''])[0] else []
  data['comparison']=rows('SELECT borough,count(*) n,median(closure_hours)/24 median,quantile_cont(closure_hours,0.9)/24 p90,count(closure_hours) AS valid_count FROM requests WHERE '+reference_where+' GROUP BY 1 ORDER BY n DESC',reference_args)
  data['weekly']=rows("SELECT strftime(date_trunc('week',created_at),'%b %d') AS week_label,count(*) n"+base+' GROUP BY date_trunc(\'week\',created_at) ORDER BY date_trunc(\'week\',created_at)')
  data['records']=rows('SELECT request_id,problem,borough,status,round(closure_hours,1) AS duration_hours'+base+' ORDER BY created_at DESC LIMIT 100')
  data['snapshot']=json.loads((ROOT/'reports/audit.json').read_text())
  c.close();body=json.dumps(data).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
if __name__=='__main__':
 if not (ROOT/'data/processed/serviceops.duckdb').exists():
  from src.build import build
  build()
 print('Open http://localhost:8765 . Press Ctrl+C to stop.',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
