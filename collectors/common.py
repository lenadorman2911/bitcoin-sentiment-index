                                                                       
from pathlib import Path
from datetime import datetime,date,timedelta,timezone
import hashlib,json,importlib.metadata,time

PACKAGE=Path(__file__).resolve().parent
PROTECTED=[PACKAGE.parent/x for x in ['reference','scripts','reproduction']]

def utc_now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def key(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def versions():
    result={}
    for name in ['pandas','numpy','requests','pytrends','vaderSentiment']:
        try:result[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:result[name]=None
    return result
def safe_path(path):
    p=Path(path).resolve()
    if any(p==x.resolve() or x.resolve() in p.parents for x in PROTECTED):
        raise ValueError('Refusing to write inside an original project: '+str(p))
    return p
def new_run(label,out=None):
    p=safe_path(out or PACKAGE/'runs'/(label+'_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')))
    p.mkdir(parents=True,exist_ok=False)
    return p
def save_json(path,value):
    p=safe_path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False))
def date_range(start,end):
    a=date.fromisoformat(str(start));b=date.fromisoformat(str(end))
    if b<a:raise ValueError('end is before start')
    if b>=datetime.now(timezone.utc).date():raise ValueError('Only completed UTC days are accepted')
    return a,b
class RequestBudget:
    def __init__(self,maximum):
        if maximum<1:raise ValueError('max requests must be positive')
        self.maximum=maximum;self.used=0
    def take(self):
        if self.used>=self.maximum:raise RuntimeError('Request budget reached; rerun to resume from versioned cache')
        self.used+=1
class JsonCache:
    def __init__(self,path):self.path=safe_path(path);self.path.mkdir(parents=True,exist_ok=True)
    def get(self,spec):
        path=self.path/(key(spec)+'.json')
        if not path.exists():return None
        value=json.loads(path.read_text())
        if value.get('spec')!=spec or value.get('payload_hash')!=key(value.get('payload')):
            raise ValueError('Cache metadata/hash mismatch; do not reuse legacy caches')
        return value
    def put(self,spec,payload):
        value=dict(spec=spec,payload=payload,payload_hash=key(payload),retrieved_at_utc=utc_now())
        path=self.path/(key(spec)+'.json')
        if path.exists():raise FileExistsError('Immutable cache entry already exists')
        save_json(path,value);return value
