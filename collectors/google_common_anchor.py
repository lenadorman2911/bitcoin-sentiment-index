                                                                          

                                                                         
                                                                       
                                                                             
                                                                         
                                                                               
   
import argparse,time
from datetime import timedelta
import numpy as np
import pandas as pd
from common import PACKAGE,JsonCache,RequestBudget,date_range,new_run,save_json,sha,versions,key,utc_now

METHOD='google_common_anchor_daily_v2'
GREED=['buy bitcoin','bitcoin price prediction','bitcoin ath']
FEAR=['sell bitcoin','bitcoin crash','is bitcoin dead']

def windows(start,end,chunk_days=180,overlap_days=14):
    if not 1<=chunk_days<=240 or not 0<=overlap_days<chunk_days:raise ValueError('Invalid daily chunk/overlap size')
    current=pd.Timestamp(start);end=pd.Timestamp(end)
    while current<=end:
        stop=min(current+pd.Timedelta(days=chunk_days-1),end)
        yield current,stop
        if stop==end:break
        current=stop+pd.Timedelta(days=1-overlap_days)

def validate_frame(frame,queries,start,end):
    if frame.empty:raise ValueError('Google returned no observations')
    if not isinstance(frame.index,pd.DatetimeIndex):raise ValueError('Google index must contain dates')
    df=frame.copy();df.index=pd.to_datetime(df.index,utc=True).tz_convert(None).normalize()
    if df.index.duplicated().any():raise ValueError('Duplicate Google dates')
    df=df.sort_index()
    if len(df)>1 and df.index.to_series().diff().dropna().dt.days.min()>1:
        raise ValueError('Non-daily Google response; refusing weekly/monthly data as daily')
    if not set(queries).issubset(df.columns):raise ValueError('Missing individual query columns; group-mean caches cannot be used')
    df=df.loc[(df.index>=pd.Timestamp(start))&(df.index<=pd.Timestamp(end))]
    if df.empty:raise ValueError('Google dates fall outside requested window')
    for term in queries:
        df[term]=pd.to_numeric(df[term],errors='raise')
        if not np.isfinite(df[term]).all() or (df[term]<0).any() or (df[term]>100).any():raise ValueError('Invalid raw Google interest values')
    if 'isPartial' not in df:df['isPartial']=False
    def partial(v):
        if isinstance(v,(bool,np.bool_)):return bool(v)
        if str(v).lower() in ['true','false']:return str(v).lower()=='true'
        raise ValueError('Unrecognized isPartial value')
    df['isPartial']=df.isPartial.map(partial)
    return df[queries+['isPartial']]

def anchored_ratio(greed,fear,anchor):
    days=greed.index.union(fear.index).sort_values();g=greed.reindex(days);f=fear.reindex(days)
    ag=g[anchor];af=f[anchor]
    missing=g[GREED+[anchor]].isna().any(axis=1)|f[FEAR+[anchor]].isna().any(axis=1)
    partial=g.isPartial.fillna(True).astype(bool)|f.isPartial.fillna(True).astype(bool)
    valid=~missing&~partial&ag.gt(0)&af.gt(0)
    gv=g[GREED].mean(axis=1)/ag.where(valid);fv=f[FEAR].mean(axis=1)/af.where(valid)
    total=gv+fv;good=valid&total.gt(0)
    ratio=((gv-fv)/total).where(good)
    result=pd.DataFrame({'date':days,'google_trends_sentiment_ratio':ratio.to_numpy(),
      'greed_in_anchor_units':gv.to_numpy(),'fear_in_anchor_units':fv.to_numpy(),
      'anchor_greed_request':ag.to_numpy(),'anchor_fear_request':af.to_numpy(),
      'zero_query_values':g[GREED].eq(0).sum(axis=1).to_numpy()+f[FEAR].eq(0).sum(axis=1).to_numpy(),
      'low_anchor_rounding_warning':(ag.lt(5)|af.lt(5)).to_numpy(),
      'status':np.where(missing,'missing_response',np.where(partial,'partial_day',np.where(ag.le(0)|af.le(0),'zero_anchor',np.where(total.le(0),'zero_total','ok'))))})
    assert result.google_trends_sentiment_ratio.dropna().between(-1,1).all()
    return result

def obtain(client,queries,start,end,anchor,cache,budget,fetch,delay):
    spec=dict(method=METHOD,queries=queries,anchor=anchor,start=str(start.date()),end=str(end.date()),geo='',hl='en-US',tz=0,gprop='',category=0,pytrends_version=versions()['pytrends'])
    item=cache.get(spec)
    if item is None:
        if not fetch:raise RuntimeError('No v2 raw cache. Explicit --fetch required; legacy group means cannot repair this ratio.')
        budget.take()
        if not client:
            from pytrends.request import TrendReq
            client.append(TrendReq(hl='en-US',tz=0,timeout=(10,20)))
        client[0].build_payload(queries,cat=0,timeframe=spec['start']+' '+spec['end'],geo='',gprop='')
        frame=validate_frame(client[0].interest_over_time(),queries,start,end)
        payload=frame.reset_index(names='date');payload['date']=payload.date.dt.strftime('%Y-%m-%d')
        item=cache.put(spec,payload.to_dict('records'))
        if delay:time.sleep(min(delay,60))
    frame=pd.DataFrame(item['payload']).set_index('date');frame.index=pd.to_datetime(frame.index)
    return validate_frame(frame,queries,start,end),dict(spec=spec,payload_hash=item['payload_hash'],retrieved_at_utc=item['retrieved_at_utc'])

def collect(start,end,out=None,cache_dir=None,anchor='buy bitcoin',fetch=False,max_requests=4,pause=2,chunk_days=180):
    start,end=date_range(start,end)
    if anchor in FEAR:raise ValueError('Use a non-fear anchor; anchor choice must be fixed before outcomes')
    run=new_run('google_v2',out);spec=dict(method=METHOD,anchor=anchor,greed=GREED,fear=FEAR,start=str(start),end=str(end),versions=versions(),script_sha256=sha(__file__))
    save_json(run/'manifest.json',dict(status='running',**spec))
    cache=JsonCache(cache_dir or PACKAGE/'cache'/METHOD);budget=RequestBudget(max_requests);client=[]
    try:
        chunks=[];requests=[]
        for a,b in windows(start,end,chunk_days):
            gq=list(dict.fromkeys([anchor]+GREED));fq=list(dict.fromkeys([anchor]+FEAR))
            g,gm=obtain(client,gq,a,b,anchor,cache,budget,fetch,pause)
            f,fm=obtain(client,fq,a,b,anchor,cache,budget,fetch,pause)
            requests.extend([gm,fm]);chunks.append(anchored_ratio(g,f,anchor))
        result=pd.concat(chunks).drop_duplicates('date',keep='first').set_index('date').reindex(pd.date_range(start,end))
        result.index.name='date';result['status']=result.status.fillna('missing_response');result=result.reset_index()
        result.to_csv(run/'google_diagnostics_v2.csv',index=False)
        if not result.google_trends_sentiment_ratio.notna().any():
            raise ValueError('No usable common-anchor observations; diagnostics saved, no corrected feature published')
        result[['date','google_trends_sentiment_ratio']].to_csv(run/'google_trends_sentiment_v2.csv',index=False)
        save_json(run/'requests.json',requests)
        save_json(run/'manifest.json',dict(spec,status='complete',n_dates=len(result),n_valid=int(result.google_trends_sentiment_ratio.notna().sum()),statuses=result.status.value_counts().to_dict(),requests_made=budget.used,output_sha256=sha(run/'google_trends_sentiment_v2.csv'),retrieval_vintages_not_historical_release_vintages=True))
        return run
    except Exception as exc:
        save_json(run/'manifest.json',dict(spec,status='failed',error_type=type(exc).__name__,error=str(exc),requests_made=budget.used));raise

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--start',required=True);p.add_argument('--end',required=True);p.add_argument('--out');p.add_argument('--cache');p.add_argument('--anchor',default='buy bitcoin');p.add_argument('--fetch',action='store_true');p.add_argument('--max-requests',type=int,default=4);p.add_argument('--pause',type=float,default=2);p.add_argument('--chunk-days',type=int,default=180)
    a=p.parse_args();print(collect(a.start,a.end,a.out,a.cache,a.anchor,a.fetch,a.max_requests,a.pause,a.chunk_days))
