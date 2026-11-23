"""Download a deliberately limited, non-address cohort from NYC Open Data."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, time
import requests
ROOT = Path(__file__).resolve().parents[1]
API = 'https://data.cityofnewyork.us/resource/erm2-nwe9.json'
WHERE = "created_date >= '2025-01-01T00:00:00' AND created_date < '2025-04-01T00:00:00' AND agency = 'DSNY'"
FIELDS = 'unique_key,created_date,closed_date,agency,complaint_type,descriptor,borough,status'
def get(params):
    for attempt in range(3):
        try:
            r = requests.get(API, params=params, timeout=90)
            r.raise_for_status()
            return r
        except requests.RequestException:
            if attempt == 2: raise
            time.sleep(2 ** attempt)
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    raw=ROOT/'data/raw/requests.json'; raw.parent.mkdir(parents=True,exist_ok=True)
    if args.refresh:
        import shutil
        shutil.rmtree(raw.parent/'pages',ignore_errors=True)
    if raw.exists() and not args.refresh:
        print('Using frozen snapshot. Pass --refresh explicitly to replace it.');return
    started=datetime.now(timezone.utc).isoformat(); rows=[];last='';urls=[]
    cache=raw.parent/'pages';cache.mkdir(exist_ok=True)
    for page in sorted(cache.glob('*.json')):
        saved=json.loads(page.read_text());rows.extend(saved['rows']);urls.append(saved['url'])
    if rows:last=rows[-1]['unique_key']
    # Keyset pagination avoids shifting offsets. The source is mutable, so a snapshot
    # is a bounded extraction, not an atomic database transaction.
    while True:
        condition=WHERE + (" AND unique_key > '"+last+"'" if last else '')
        r=get({'$select':FIELDS,'$where':condition,'$order':'unique_key ASC','$limit':10000})
        batch=r.json(); urls.append(r.url)
        if not batch:break
        (cache/f'{len(urls):03d}.json').write_text(json.dumps({'url':r.url,'rows':batch}))
        rows.extend(batch);last=batch[-1]['unique_key'];print('Downloaded',len(rows),flush=True)
        if len(batch)<10000:break
    body=json.dumps(rows,ensure_ascii=False,indent=2).encode();raw.write_bytes(body)
    meta={'source':API,'publisher':'NYC Open Data / NYC311','where':WHERE,'fields':FIELDS,
          'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),
          'rows':len(rows),'sha256':hashlib.sha256(body).hexdigest(),'page_urls':urls,
          'note':'Mutable source; extraction is not atomic. No addresses or free-text resolution messages collected.'}
    (raw.parent/'manifest.json').write_text(json.dumps(meta,indent=2))
    print('Snapshot saved',len(rows),'rows')
if __name__=='__main__':main()
