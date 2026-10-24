                                                                                  
from pathlib import Path
from datetime import datetime,timezone
import json,sys,hashlib,math
sys.dont_write_bytecode=True
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from statsmodels.stats.multitest import multipletests
from expanded_component_tests import defs,ROOT,SOURCE,CUT,END,DROPS
from test_true_return_forecasts import mean_test

PREVIOUS=Path(__file__).resolve().parent/'results/expanded'
OUT=Path(__file__).resolve().parent/'results/risk'
HORIZONS=[1,7,30];EPS=1e-12;REPS=99999
FOCUS={('sample_a_2021_plus','baseline_all_families',0,90),('sample_b_2023_plus','baseline_all_families',0,90),('sample_b_2023_plus','market_behavioral',15,30)}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def qlike(y,f):
                                                                               
    return y/f+np.log(f)
def auc(actual,score):
    n1=int(actual.sum());n0=len(actual)-n1
    return float((rankdata(score)[actual].sum()-n1*(n1+1)/2)/(n1*n0)) if n1 and n0 else float('nan')
def fit_positive(xtr,xte,y):
    logy=np.log(y+EPS);coef=np.linalg.lstsq(xtr,logy,rcond=None)[0]
    resid=logy-xtr@coef;smearing=float(np.exp(resid).mean())
    train=np.maximum(EPS,np.exp(xtr@coef)*smearing-EPS)
    forecast=np.maximum(EPS,np.exp(xte@coef)*smearing-EPS)
    assert np.isfinite(forecast).all() and np.isfinite(train).all() and (forecast>0).all()
    return forecast,train,coef,smearing
def evaluate(y,f,training_y,training_f,mean,naive,history):
    mse=float(np.mean((y-f)**2));ql=float(np.mean(qlike(y,f)))
    threshold=float(np.quantile(training_y,.9));alarm_threshold=float(np.quantile(training_f,.9))
    actual=y>=threshold;alarm=f>=alarm_threshold
    tp=int(np.sum(actual&alarm));fp=int(np.sum(~actual&alarm));positives=int(actual.sum());alarms=int(alarm.sum())
    return dict(n=len(y),mse=mse,mae=float(np.mean(abs(y-f))),qlike=ql,
        mse_reduction_vs_mean=1-mse/np.mean((y-mean)**2),mse_reduction_vs_naive30=1-mse/np.mean((y-naive)**2),mse_reduction_vs_history=1-mse/np.mean((y-history)**2),
        qlike_gain_vs_mean=float(np.mean(qlike(y,mean))-ql),qlike_gain_vs_naive30=float(np.mean(qlike(y,naive))-ql),qlike_gain_vs_history=float(np.mean(qlike(y,history))-ql),
        actual_mean=float(y.mean()),forecast_mean=float(f.mean()),auc=auc(actual,f),stress_threshold=threshold,alarm_threshold=alarm_threshold,
        stress_days=positives,alarms=alarms,true_alarms=tp,false_alarms=fp,recall=tp/positives if positives else float('nan'),precision=tp/alarms if alarms else float('nan'),false_positive_rate=fp/(len(y)-positives) if positives<len(y) else float('nan'))
def mbb_counts(rng,n,length,reps):
    starts=rng.integers(0,n-length+1,size=(reps,math.ceil(n/length)))
    ix=(starts[:,:,None]+np.arange(length)).reshape(reps,-1)[:,:n]
    return np.array([np.bincount(row,minlength=n) for row in ix],dtype=float)
def bootstrap_inference(observed,draw):
    lo,hi=np.quantile(draw,[.025,.975]);p=(1+np.sum(abs(draw-observed)>=abs(observed)))/(len(draw)+1)
    return dict(difference=float(observed),ci_low=float(lo),ci_high=float(hi),p=float(p))

def main():
    OUT.mkdir(exist_ok=False)
    paths=[SOURCE,PREVIOUS/'parameters.csv',PREVIOUS/'paired_bootstrap_inputs.npz',ROOT/'scripts/build_cw_index_versions.py',Path(__file__),Path(__file__).resolve().parent/'test_true_return_forecasts.py']
    hashes={str(p):digest(p) for p in paths}
    plan=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),status='exploratory new risk task on a previously examined holdout; no claim of independent confirmation',
        primary_target='Next-day absolute log return, |r[t+1]|; primary loss MSE; primary model adds standardized index and its square to a historical-risk model; primary configuration Sample A full W90.',
        secondary_targets='Mean future absolute log return and mean future squared log return, horizons1/7/30. Squared returns are a daily second-moment risk proxy, not high-frequency realized variance or centered conditional variance.',
        horizons=HORIZONS,train_cutoff=str(CUT.date()),test_start='2025-01-01',last_outcome=str(END.date()),
        target_purging='Admit training origin only when origin+horizon<=2024-12-31; original 90-calendar-day warmup.',
        forecast_link='log(target+1e-12) OLS, train-only residual smearing to forecast positive mean; floor1e-12, no upper clipping. Means/scales from training only.',
        modes=['index_only: constant + standardized index + square','history_plus_index: history model + standardized index + square'],
        history_model='Constant and log trailing mean risk over1/7/30 calendar days; same form for absolute and squared-return targets. HAR-inspired daily proxy benchmark, not original intraday HAR-RV.',
        benchmarks=['Fitted history model','Trailing30 mean of absolute/squared return, available at forecast origin','EWMA of absolute/squared returns, decay0.94','Fixed training target mean','CFGI forecast using identical mapping and information','Momentum-volatility forecast using identical mapping'],
        index_models='All512 sample/version/ablation/window settings, EW and fixed CW; all coefficients fixed before2025. No sign flips or post-result composition selection.',
        evaluation='MSE/MAE for magnitude; QLIKE y/f+log(f) for squared-return proxy (target-only constant omitted, lower better). Always compare EW/CW on identical dates.',
        alarm_diagnostics='Actual stress threshold Q90 of training target; forecast alarm threshold Q90 of each own fitted training forecast. AUC, precision, recall, false-positive rate descriptive, not optimized on holdout.',
        inference='Two-sided paired Bartlett-HAC loss-difference tests; positive difference EW loss minus CW loss favors CW. Main lag30, sensitivity60/90. Holm per target/horizon/mode/lag/comparison and global main-lag family. Conditional on trained models; no exact nested-model inference claimed.',
        focus_bootstrap=dict(settings=[list(x) for x in sorted(FOCUS)],comparisons=['EW vs history','CW vs history','EW vs CW'],score='MSE absolute target; QLIKE squared target',blocks=[30,60,90],primary_block=60,repetitions=REPS,seed=20261021,paired=True,models_refit=False,holm='All54 focus comparisons per block; separate prespecified primary A/full/W90/absolute/h1 subset3'),
        limitations=['Previously inspected holdout; no untouched confirmatory period','Archived feature release vintages unknown','No monthly re-estimation','Historical risk is built from daily closing returns, not intraday data','QLIKE proxy robustness needs assumptions; daily squared returns are noisy','Bootstrap conditions on trained parameters; no full-pipeline re-estimation','Grid exploration cannot justify choosing a new winner on these same data'],
        references=['https://public.econ.duke.edu/~ap172/Patton_vol_proxies_JoE_2011.pdf','https://people.unipi.it/fulvio_corsi/pubblicazioni/'])
    (OUT/'plan_before_evaluation.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
    builder=defs(ROOT/'scripts/build_cw_index_versions.py',{'rz_col','build_ew_index','flatten_components','apply_cw_weights'},{'np':np,'pd':pd})
    raw=pd.read_csv(SOURCE,parse_dates=['date']).query('date<=@END').sort_values('date').reset_index(drop=True)
    assert raw.date.diff().dropna().eq(pd.Timedelta(days=1)).all()
    par=pd.read_csv(PREVIOUS/'parameters.csv');par=par[par.scope=='fixed_training_holdout']
    prior=np.load(PREVIOUS/'paired_bootstrap_inputs.npz')
    risks={'absolute':raw.log_return.abs(),'squared':raw.log_return**2}
    targets={(kind,h):risk.rolling(h).mean().shift(-h).to_numpy() for kind,risk in risks.items() for h in HORIZONS}
    history={kind:np.column_stack([np.log(risk.rolling(w).mean()+EPS) for w in [1,7,30]]) for kind,risk in risks.items()}
    naive={kind:risk.rolling(30).mean().to_numpy() for kind,risk in risks.items()}
    ewma={kind:risk.ewm(alpha=.06,adjust=False).mean().to_numpy() for kind,risk in risks.items()}
    target_checks=[]
    altered=raw.log_return.copy();altered[raw.date>CUT]=123-777*altered[raw.date>CUT]
    for (kind,h),y in targets.items():
        other=(altered.abs() if kind=='absolute' else altered**2).rolling(h).mean().shift(-h).to_numpy()
        known=(raw.date+pd.Timedelta(days=h)<=CUT).to_numpy()
        assert np.allclose(y[known],other[known],atol=1e-9,equal_nan=True)
        target_checks.append(dict(kind=kind,horizon=h,future_perturbation_invariant=True,last_training_origin=str((CUT-pd.Timedelta(days=h)).date())))
    metrics=[];tests=[];training=[];coefficients=[];daily=[];nonoverlap=[];focused=[];focusdiff={};arrays={};arraymeta=[]
    for groupno,((sample,version,mask,w),params) in enumerate(par.groupby(['sample','version','mask','window'],sort=False),1):
        mask=int(mask);w=int(w);start=builder['SAMPLES'][sample];remove=[c for j,c in enumerate(DROPS) if mask&(1<<j)]
        families={f:{c:d for c,d in comps.items() if c not in remove} for f,comps in builder['VERSIONS'][version].items()}
        weights=dict(zip(params.component,params.cw_weight));ew=builder['build_ew_index'](raw,families,w)[0].to_numpy();cw=builder['apply_cw_weights'](raw,families,w,weights).to_numpy()
        for method,x in [('ew',ew),('cw',cw)]:
            sid='|'.join([sample,version,str(mask),str(w),method]);assert np.allclose(x[raw.date>CUT],prior['feature::'+sid],atol=1e-12)
        features={'ew':ew,'cw':cw,'cfgi':raw.cfgi.to_numpy(),'momentum_volatility':.5*(raw[f'momentum_7d_rz_{w}']-raw[f'volatility_30d_rz_{w}']).to_numpy()}
        base=dict(sample=sample,version=version,mask=mask,removed=';'.join(remove),window=w)
        for (kind,h),y in targets.items():
            end=raw.date+pd.Timedelta(days=h);eligible=(raw.date>=pd.Timestamp(start)+pd.Timedelta(days=90)).to_numpy()
            finite=np.isfinite(y)&np.isfinite(history[kind]).all(axis=1)&np.isfinite(ew)&np.isfinite(cw)&np.isfinite(features['cfgi'])&np.isfinite(features['momentum_volatility'])
            tr=eligible&(end<=CUT).to_numpy()&finite;te=(raw.date>CUT).to_numpy()&(end<=END).to_numpy()&finite
            assert tr.sum()>=100 and te.sum()==603-h
            yy=y[te];mean=np.full(len(yy),float(y[tr].mean()))
            histtr=np.column_stack([np.ones(tr.sum()),history[kind][tr]]);histte=np.column_stack([np.ones(te.sum()),history[kind][te]])
            hp,ht,hb,hs=fit_positive(histtr,histte,y[tr])
            for mode in ['index_only','history_plus_index']:
                dtr=histtr if mode=='history_plus_index' else np.ones((tr.sum(),1));dte=histte if mode=='history_plus_index' else np.ones((te.sum(),1))
                predictions={};fitted={}
                for method,x in features.items():
                    center=float(x[tr].mean());sd=float(x[tr].std(ddof=1));assert sd>0
                    ztr=(x[tr]-center)/sd;zte=(x[te]-center)/sd
                    xtr=np.column_stack([dtr,ztr,ztr**2]);xte=np.column_stack([dte,zte,zte**2])
                    p,pfit,beta,smear=fit_positive(xtr,xte,y[tr]);predictions[method]=p;fitted[method]=pfit
                    metrics.append(dict(base,kind=kind,horizon=h,mode=mode,method=method,**evaluate(yy,p,y[tr],pfit,mean,naive[kind][te],hp)))
                    coefficients.append(dict(base,kind=kind,horizon=h,mode=mode,method=method,index_mean=center,index_sd=sd,beta_linear=beta[-2],beta_square=beta[-1],intercept=beta[0],smearing=smear))
                    if method in ['ew','cw']:
                        key=f'g{groupno:03d}_{kind}_h{h}_{mode}_{method}';arrays[key]=p
                        arraymeta.append(dict(base,kind=kind,horizon=h,mode=mode,method=method,key=key,n=len(p)))
                for method,p,pfit in [('history',hp,ht),('naive30',np.maximum(EPS,naive[kind][te]),np.maximum(EPS,naive[kind][tr])),('ewma094',np.maximum(EPS,ewma[kind][te]),np.maximum(EPS,ewma[kind][tr])),('fixed_mean',mean,np.full(tr.sum(),mean[0]))]:
                    metrics.append(dict(base,kind=kind,horizon=h,mode=mode,method=method,**evaluate(yy,p,y[tr],pfit,mean,naive[kind][te],hp)))
                for score in ['mse','qlike']:
                    loss={k:(yy-v)**2 if score=='mse' else qlike(yy,v) for k,v in predictions.items()}
                    lh=(yy-hp)**2 if score=='mse' else qlike(yy,hp)
                    for lag in [30,60,90]:
                        common=dict(base,kind=kind,horizon=h,mode=mode,score=score,hac_lag=lag,primary_lag=bool(lag==30),primary_score=bool(score==('mse' if kind=='absolute' else 'qlike')),n=len(yy))
                        tests.append(dict(common,test='ew_vs_cw',method='cw',**mean_test(loss['ew']-loss['cw'],lag)))
                        for method in ['ew','cw']:tests.append(dict(common,test='index_vs_history',method=method,**mean_test(lh-loss[method],lag)))
                    if mode=='history_plus_index' and (sample,version,mask,w) in FOCUS and score==('mse' if kind=='absolute' else 'qlike'):
                        for comparison,diff in [('ew_vs_history',lh-loss['ew']),('cw_vs_history',lh-loss['cw']),('ew_vs_cw',loss['ew']-loss['cw'])]:
                            key='|'.join([sample,version,str(mask),str(w),kind,str(h),comparison]);focusdiff[key]=diff
                            focused.append(dict(key=key,**base,kind=kind,horizon=h,score=score,comparison=comparison,primary_configuration=bool(sample=='sample_a_2021_plus' and version=='baseline_all_families' and mask==0 and w==90 and kind=='absolute' and h==1)))
                for method in ['ew','cw']:
                    ix=np.arange(0,len(yy),h);p=predictions[method]
                    nonoverlap.append(dict(base,kind=kind,horizon=h,mode=mode,method=method,n=len(ix),mse_gain_vs_history=float(np.mean((yy[ix]-hp[ix])**2-(yy[ix]-p[ix])**2)),qlike_gain_vs_history=float(np.mean(qlike(yy[ix],hp[ix])-qlike(yy[ix],p[ix])))))
                if (sample,version,mask,w) in FOCUS:
                    for j,date in enumerate(raw.loc[te,'date']):daily.append(dict(base,kind=kind,horizon=h,mode=mode,date=str(date.date()),actual=yy[j],ew=predictions['ew'][j],cw=predictions['cw'][j],cfgi=predictions['cfgi'][j],history=hp[j],naive30=naive[kind][te][j],ewma094=ewma[kind][te][j]))
            training.append(dict(base,kind=kind,horizon=h,n_train=int(tr.sum()),n_test=int(te.sum()),last_training_origin=str(raw.loc[tr,'date'].max().date()),latest_training_target=str(end[tr].max().date()),first_test_origin=str(raw.loc[te,'date'].min().date()),last_test_origin=str(raw.loc[te,'date'].max().date()),history_smearing=hs))
        if groupno%32==0:print('RISK_SETTINGS',groupno,'/512',flush=True)
    assert groupno==512 and len(focused)==54
    metric=pd.DataFrame(metrics);inference=pd.DataFrame(tests)
    for _,g in inference.groupby(['test','kind','horizon','mode','score','hac_lag']):inference.loc[g.index,'p_holm_target_mode']=multipletests(g.p,method='holm')[1]
    for _,g in inference[inference.primary_lag&inference.primary_score].groupby('test'):inference.loc[g.index,'p_holm_all_primary_scores_targets_modes']=multipletests(g.p,method='holm')[1]
    for name,table in [('risk_metrics',metric),('risk_tests',inference),('training_audit',pd.DataFrame(training)),('coefficients',pd.DataFrame(coefficients)),('focused_daily_forecasts',pd.DataFrame(daily)),('nonoverlapping_metrics',pd.DataFrame(nonoverlap)),('target_purging_checks',pd.DataFrame(target_checks)),('prediction_metadata',pd.DataFrame(arraymeta))]:table.to_csv(OUT/(name+'.csv'),index=False)
    np.savez_compressed(OUT/'all_ew_cw_risk_forecasts.npz',**arrays)
    np.savez_compressed(OUT/'focus_loss_differences.npz',**focusdiff)
    fmeta=pd.DataFrame(focused);fmeta.to_csv(OUT/'focus_bootstrap_metadata.csv',index=False)
    print('RISK_METRICS_SAVED',len(metric),len(inference),flush=True)
    boot=[]
    for length in [30,60,90]:
        for h in HORIZONS:
            selected=fmeta[fmeta.horizon==h];keys=selected.key.tolist();data=np.column_stack([focusdiff[k] for k in keys]);n=len(data)
            rng=np.random.default_rng(np.random.SeedSequence([20261021,length,h]));draw=np.empty((REPS,len(keys)))
            for start in range(0,REPS,2048):
                count=min(2048,REPS-start);ct=mbb_counts(rng,n,length,count);draw[start:start+count]=ct@data/n
            for j,row in enumerate(selected.to_dict('records')):boot.append(dict(row,block_days=length,**bootstrap_inference(data[:,j].mean(),draw[:,j])))
        print('RISK_FOCUSED_BOOTSTRAP',length,'complete',flush=True)
    bootstrap=pd.DataFrame(boot)
    for _,g in bootstrap.groupby('block_days'):bootstrap.loc[g.index,'p_holm_all54']=multipletests(g.p,method='holm')[1]
    for _,g in bootstrap[bootstrap.primary_configuration].groupby('block_days'):bootstrap.loc[g.index,'p_holm_primary3']=multipletests(g.p,method='holm')[1]
    bootstrap.to_csv(OUT/'focused_block_bootstrap.csv',index=False)
    assert all(digest(Path(p))==v for p,v in hashes.items())
    (OUT/'verification.json').write_text(json.dumps(dict(status='complete',settings=512,metric_rows=len(metric),statistical_rows=len(inference),focused_bootstrap_rows=len(bootstrap),bootstrap_repetitions=REPS,original_files_unchanged=True,protected_hashes=hashes,training_target_purging=True,saved_indices_reproduced=True,exploratory=True),indent=2))
    print('RISK_COMPLETE',flush=True)

if __name__=='__main__':main()
