"""Read-only API integration tests, using an ephemeral loopback port."""
import importlib.util,json,threading
from urllib.request import urlopen
from urllib.parse import urlencode
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(scope='module')
def api():
 spec=importlib.util.spec_from_file_location('dashboard',ROOT/'dashboard.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 server=module.ThreadingHTTPServer(('127.0.0.1',0),module.Handler)
 thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 def get(**kw):
  with urlopen('http://127.0.0.1:'+str(server.server_port)+'/api?'+urlencode(kw)) as r:return json.load(r)
 yield get
 server.shutdown();server.server_close();thread.join()
def test_api_all(api):
 d=api();assert d['metrics']['n']==73362;assert d['metrics']['valid_count']==72991
 assert len(d['records'])==100;assert len(d['weekly'])==14
 assert sum(x['n'] for x in d['segments'])==73362
def test_api_filter(api):
 d=api(problem='Snow or Ice',borough='BROOKLYN')
 assert len(d['comparison'])>1;assert sum(x['n'] for x in d['comparison'])==7990
 assert d['metrics']['n']==3335;assert round(d['metrics']['median'],2)==4.36
 assert all(x['borough']=='BROOKLYN' and x['problem']=='Snow or Ice' for x in d['records'])
def test_api_empty_and_parameter_safety(api):
 d=api(problem="unmatched' OR TRUE --")
 assert d['metrics']['n']==0;assert d['records']==[];assert d['metrics']['median'] is None
