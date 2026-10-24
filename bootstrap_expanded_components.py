                                                                          
from pathlib import Path
import json, math
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

OUT=Path(__file__).resolve().parent/'results/expanded'
REPS=4999;SEED=20261021

def counts(rng,n,length,reps):
    starts=rng.integers(0,n-length+1,size=(reps,math.ceil(n/length)))
    ix=(starts[:,:,None]+np.arange(length)[None,None,:]).reshape(reps,-1)[:,:n]
    result=np.zeros((reps,n))
    for j in range(reps):result[j]=np.bincount(ix[j],minlength=n)
    assert np.all(result.sum(axis=1)==n)
    return result

def inference(observed,draws):
    lo,hi=np.quantile(draws,[.025,.975])
    p=(1+np.sum(np.abs(draws-observed)>=abs(observed)))/(len(draws)+1)
    return dict(difference=float(observed),ci_low=float(lo),ci_high=float(hi),p=float(p))

def adjust(table):
    for _,ix in table.groupby(['block_days','family']).groups.items():table.loc[ix,'p_holm_all']=multipletests(table.loc[ix,'p'],method='holm')[1]
    for _,ix in table[table.window==90].groupby(['block_days','family']).groups.items():table.loc[ix,'p_holm_w90']=multipletests(table.loc[ix,'p'],method='holm')[1]
    return table

def main():
    meta=json.loads((OUT/'strategy_metadata.json').read_text())
    saved=np.load(OUT/'paired_bootstrap_inputs.npz')
    keys=[k.removeprefix('return::') for k in saved.files if k.startswith('return::')]
    ids={k:j for j,k in enumerate(keys)};returns=np.column_stack([saved['return::'+k] for k in keys])
    fkeys=[k for k in keys if k in meta and meta[k]['method']!='cfgi']
    fids={k:j for j,k in enumerate(fkeys)};features=np.column_stack([saved['feature::'+k] for k in fkeys]);cfgi=saved['cfgi_feature']
    assert returns.shape==(600,1541) and features.shape==(603,1536)
    assert np.isfinite(returns).all() and np.isfinite(features).all()
    observed_ce=365*(returns.mean(axis=0)-1.5*returns.var(axis=0,ddof=1))
    observed_corr=np.array([np.corrcoef(features[:,j],cfgi)[0,1] for j in range(features.shape[1])])
    pairs=[]
    for sid in fkeys:
        m=meta[sid]
        for rival,family in [('CFGI|'+m['sample'],'vs_cfgi'),('buy_hold','vs_buy_hold'),('constant_50','vs_50_50')]:pairs.append((sid,rival,family))
        prefix=sid.rsplit('|',1)[0]
        if m['mask']!=0:pairs.append((sid,'|'.join([m['sample'],m['version'],'0',str(m['window']),m['method']]),'reduced_vs_baseline'))
        if m['method']=='cw':pairs.append((sid,prefix+'|ew','cw_vs_ew'))
        if m['method']=='pca':
            pairs.append((sid,prefix+'|ew','pca_vs_ew'));pairs.append((sid,prefix+'|cw','pca_vs_cw'))
    corrpairs=[p for p in pairs if p[2] in ['reduced_vs_baseline','cw_vs_ew','pca_vs_ew','pca_vs_cw']]
    ce_rows=[];corr_rows=[]
    for length in [30,60,90]:
        rng=np.random.default_rng(SEED+length)
        ct=counts(rng,600,length,REPS)
        mean=ct@returns/600
        variance=(ct@(returns**2)-600*mean**2)/599
        ce=365*(mean-1.5*variance)
        for sid,rival,family in pairs:ce_rows.append(dict(strategy_id=sid,comparison=rival,family=family,block_days=length,**meta[sid],**inference(observed_ce[ids[sid]]-observed_ce[ids[rival]],ce[:,ids[sid]]-ce[:,ids[rival]])))
        del ct,mean,variance,ce
        rng=np.random.default_rng(SEED+1000+length)
        ct=counts(rng,603,length,REPS)
        mx=ct@features/603;my=ct@cfgi/603
        vx=ct@(features**2)/603-mx**2
        vy=ct@(cfgi**2)/603-my**2
        cov=ct@(features*cfgi[:,None])/603-mx*my[:,None]
        corr=cov/np.sqrt(vx*vy[:,None])
        for sid,rival,family in corrpairs:corr_rows.append(dict(strategy_id=sid,comparison=rival,family=family,block_days=length,**meta[sid],**inference(observed_corr[fids[sid]]-observed_corr[fids[rival]],corr[:,fids[sid]]-corr[:,fids[rival]])))
        del ct,mx,my,vx,vy,cov,corr
        print('PAIRED_BOOTSTRAP',length,'complete',flush=True)
    ce=adjust(pd.DataFrame(ce_rows));corr=adjust(pd.DataFrame(corr_rows))
    ce.to_csv(OUT/'ce_comparisons_bootstrap.csv',index=False);corr.to_csv(OUT/'correlation_changes_bootstrap.csv',index=False)
                                                                       
    rng=np.random.default_rng(SEED);n=600;ix=rng.integers(n,size=(3,n));ct=np.array([np.bincount(row,minlength=n) for row in ix])
    literal=returns[ix,:5];mean=ct@returns[:,:5]/n
    weighted=365*(mean-1.5*(ct@(returns[:,:5]**2)-n*mean**2)/(n-1))
    assert np.allclose(weighted,365*(literal.mean(axis=1)-1.5*literal.var(axis=1,ddof=1)),atol=1e-12)
    (OUT/'bootstrap_verification.json').write_text(json.dumps(dict(status='complete',draws=REPS,blocks=[30,60,90],strategies=1536,ce_comparisons=len(ce),correlation_comparisons=len(corr),weighted_moment_check=True,scope='fixed training holdout; conditional on weights and trading thresholds',primary_block=60),indent=2))
    print('BOOTSTRAP_COMPLETE',len(ce),len(corr),flush=True)

if __name__=='__main__':main()
