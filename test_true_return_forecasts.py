                                                                               

                                                                             
   
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys
sys.dont_write_bytecode=True
import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from expanded_component_tests import defs, ROOT, SOURCE, CUT, END, DROPS

PREVIOUS=Path(__file__).resolve().parent/'results/expanded'
OUT=Path(__file__).resolve().parent/'results/returns'
HORIZONS=[1,7,30,60,90]
REFERENCE='https://users.ssc.wisc.edu/~kdwest/publications/2000/Approximately%20Normal%20Tests%20for%20Equal%20Predictive%20Accuracy%20in%20Nested%20Models.pdf'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def mean_test(values,lag,one_sided=False):
    x=np.asarray(values,dtype=float);n=len(x);centered=x-x.mean()
    longrun=float(centered@centered)
    for k in range(1,min(lag,n-1)+1):longrun+=2*(1-k/(lag+1))*float(centered[k:]@centered[:-k])
                                                                       
    se=np.sqrt(max(0,longrun)/(n*(n-1)))
    if se<=0:return dict(difference=float(x.mean()),se=float(se),z=float('nan'),p=float('nan'))
    stat=float(x.mean()/se)
    return dict(difference=float(x.mean()),se=float(se),z=stat,p=float(norm.sf(stat) if one_sided else 2*norm.sf(abs(stat))))

def evaluate(y,pred,mean,expanding,control):
    errors=y-pred;mse=float(np.mean(errors**2));den=float(np.mean((y-mean)**2))
    return dict(n=len(y),mse=mse,rmse=np.sqrt(mse),mae=float(np.mean(abs(errors))),
        r2_oos_fixed_mean=1-mse/den,r2_oos_expanding_mean=1-mse/np.mean((y-expanding)**2),
        r2_oos_control_only=1-mse/np.mean((y-control)**2),direction_accuracy=float(np.mean(np.sign(pred)==np.sign(y))),
        forecast_mean=float(pred.mean()),actual_mean=float(y.mean()),
        forecast_actual_correlation=float(np.corrcoef(pred,y)[0,1]) if np.std(pred)>1e-12 else float('nan'))

def main():
    OUT.mkdir(exist_ok=False)
    paths=[SOURCE,PREVIOUS/'parameters.csv',PREVIOUS/'strategy_metadata.json',PREVIOUS/'paired_bootstrap_inputs.npz',ROOT/'scripts/build_cw_index_versions.py',ROOT/'reproduction/test_out_of_sample.py',Path(__file__)]
    protected={str(p):digest(p) for p in paths}
    plan=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),status='exploratory extension on previously inspected holdout, not an untouched confirmation',
        train_cutoff=str(CUT.date()),test_origin_start='2025-01-01',last_realized_return=str(END.date()),horizons=HORIZONS,primary_horizon=30,
        settings='All 512 sample/specification/ablation/window combinations, paired EW/CW; no forecast-result selection.',
        purging='Fit forecast coefficients only where origin >= sample_start+90 days and origin+horizon <= 2024-12-31. CW construction weights use returns known through 2024-12-31.',
        predictors=['raw EW or CW index at forecast origin','controlled sensitivity: previous-calendar-day VIX after past-only forward fill max7 days'],
        forecast_models=['constant + index','constant + lagged VIX + index'],fitting='Direct OLS per horizon and configuration, coefficients fixed throughout test; no sign reversal, no clipping, no test refit.',
        benchmarks=['fixed training mean of same forward-return target on matched training dates','expanding historical mean using only target outcomes completed by origin-1 day','zero return','VIX-only in controlled sensitivity','CFGI and momentum-volatility with identical fitting and dates'],
        primary_metric='OOS R2 = 1-MSPE(model)/MSPE(fixed training mean), not in-sample regression R2; paired EW/CW MSPE comparison.',
        tests='EW-vs-CW: two-sided Bartlett-HAC mean of squared-error EW minus CW, positive favors CW. Nested index-vs-mean/control: one-sided Clark-West adjusted loss; approximate conditional inference.',
        hac_lags='Primary max(30,horizon-1); sensitivity max(60,horizon-1),90. Overlap retained; auxiliary nonoverlapping phase0 every horizon days.',
        multiplicity='Holm across 512 EW/CW comparisons within each horizon/model/lag; nested tests across both EW and CW in each horizon/model/lag. Also Holm over all primary-lag horizons and model variants.',
        reference=REFERENCE,limits=['Holdout previously inspected, selected example already known; no independent fresh confirmation','Archived features and unverified release timestamps/data vintages','Fixed, not monthly re-estimated forecasts','HAC and Clark-West p-values approximate; generated CW predictor uncertainty not fully modeled','Forecast-error comparisons do not establish net trading value','Past-only lagged VIX differs from previous contemporaneous-VIX association regressions'])
    (OUT/'plan_before_evaluation.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
    bpath=ROOT/'scripts/build_cw_index_versions.py'
    builder=defs(bpath,{'rz_col','flatten_components','compute_stress','build_ew_index','compute_cw_weights','apply_cw_weights'},{'pd':pd,'np':np,'spearmanr':spearmanr})
    helper=defs(ROOT/'reproduction/test_out_of_sample.py',{'fit_weights'},{'pd':pd,'np':np})
    df=pd.read_csv(SOURCE,parse_dates=['date']).query('date<=@END').sort_values('date').reset_index(drop=True)
    assert df.date.diff().dropna().eq(pd.Timedelta(days=1)).all()
    assert np.allclose(df.log_return.dropna(),np.log1p(df['return'].dropna()),atol=1e-10)
    parameters=pd.read_csv(PREVIOUS/'parameters.csv');parameters=parameters[parameters.scope=='fixed_training_holdout']
    old=np.load(PREVIOUS/'paired_bootstrap_inputs.npz')
    vix=df.vix.ffill(limit=7).shift(1).to_numpy()
    targets={h:df.log_return.rolling(h).sum().shift(-h).to_numpy() for h in HORIZONS}
                                                                                         
    altered=df.log_return.copy();altered[df.date>CUT]=123+altered[df.date>CUT]*-777
    target_checks=[]
    for h in HORIZONS:
        y2=altered.rolling(h).sum().shift(-h).to_numpy();known=df.date+pd.Timedelta(days=h)<=CUT
        assert np.allclose(targets[h][known],y2[known],equal_nan=True,atol=1e-10)
        target_checks.append(dict(horizon=h,last_training_origin=str((CUT-pd.Timedelta(days=h)).date()),last_training_outcome=str(CUT.date()),future_return_perturbation_invariant=True))
    test_rng=np.random.default_rng(20261021)
    for lag in [0,30,60,90]:
        x=test_rng.normal(size=573);mine=mean_test(x,lag);ref=sm.OLS(x,np.ones((len(x),1))).fit(cov_type='HAC',cov_kwds={'maxlags':lag,'use_correction':True},use_t=False)
        assert np.isclose(mine['se'],ref.bse[0],atol=1e-12) and np.isclose(mine['p'],ref.pvalues[0],atol=1e-12)
    metrics=[];tests=[];training=[];coefficients=[];nonoverlap=[];checks=[];daily=[];prediction_arrays={};predict_metadata=[]
    highlighted={('sample_a_2021_plus','baseline_all_families',0,90),('sample_b_2023_plus','baseline_all_families',0,90),('sample_b_2023_plus','market_behavioral',0,30),('sample_b_2023_plus','market_behavioral',15,30)}
    groups=parameters.groupby(['sample','version','mask','window'],sort=False)
    for groupno,((sample,version,mask,w),par) in enumerate(groups,1):
        mask=int(mask);w=int(w);start=builder['SAMPLES'][sample];removed=[c for j,c in enumerate(DROPS) if mask&(1<<j)]
        families={f:{c:d for c,d in comps.items() if c not in removed} for f,comps in builder['VERSIONS'][version].items()}
        weights=dict(zip(par.component,par.cw_weight))
        ew=builder['build_ew_index'](df,families,w)[0].to_numpy();cw=builder['apply_cw_weights'](df,families,w,weights).to_numpy()
        eligible=df.date>=pd.Timestamp(start)+pd.Timedelta(days=90)
        assert np.isfinite(ew[eligible]).all() and np.isfinite(cw[eligible]).all()
        for method,x in [('ew',ew),('cw',cw)]:
            sid='|'.join([sample,version,str(mask),str(w),method])
            assert np.allclose(x[df.date>CUT],old['feature::'+sid],atol=1e-12)
        if mask==0 or (sample,version,mask,w) in highlighted:
            fitted=helper['fit_weights'](df,start,CUT,families,w,builder)[0]
            assert all(np.isclose(fitted[c],weights[c],atol=1e-14) for c in weights)
            changed=df.copy();future=changed.date>CUT
            for col in [f'{c}_rz_{w}' for c in weights]+['log_return']:changed.loc[future,col]=changed.loc[future,col]*-777+123
            fitted2=helper['fit_weights'](changed,start,CUT,families,w,builder)[0]
            assert fitted==fitted2
            checks.append(dict(sample=sample,version=version,mask=mask,window=w,cw_refit_matches_saved=True,cw_future_invariant=True))
        features={'ew':ew,'cw':cw,'cfgi':df.cfgi.to_numpy(),'momentum_volatility':.5*(df[f'momentum_7d_rz_{w}']-df[f'volatility_30d_rz_{w}']).to_numpy()}
        base=dict(sample=sample,version=version,mask=mask,removed=';'.join(removed),window=w)
        for h,y in targets.items():
            origin_end=df.date+pd.Timedelta(days=h)
            historical=pd.Series(y).where(eligible).shift(h+1).expanding().mean().to_numpy()
            known=(eligible&(origin_end<=CUT)).to_numpy()
            hold=((df.date>CUT)&(origin_end<=END)).to_numpy()
            for mode in ['index_only','with_lagged_vix']:
                complete=np.isfinite(y)&np.isfinite(ew)&np.isfinite(cw)&np.isfinite(features['cfgi'])&np.isfinite(features['momentum_volatility'])
                if mode=='with_lagged_vix':complete&=np.isfinite(vix)
                tr=known&complete;te=hold&complete;assert tr.sum()>=100 and te.sum()>h
                assert df.loc[tr,'date'].max()+pd.Timedelta(days=h)<=CUT
                assert df.loc[te,'date'].min()>CUT and origin_end[te].max()<=END
                yy=y[te];constant=float(y[tr].mean());mean=np.full(len(yy),constant)
                if mode=='with_lagged_vix':
                    dtr=np.column_stack([np.ones(tr.sum()),vix[tr]]);dte=np.column_stack([np.ones(te.sum()),vix[te]])
                else:dtr=np.ones((tr.sum(),1));dte=np.ones((te.sum(),1))
                control_beta=np.linalg.lstsq(dtr,y[tr],rcond=None)[0];control=dte@control_beta
                predictions={};state={}
                for method,x in features.items():
                    xtr=np.column_stack([dtr,x[tr]]);xte=np.column_stack([dte,x[te]])
                    beta=np.linalg.lstsq(xtr,y[tr],rcond=None)[0];pred=xte@beta
                    assert np.isfinite(pred).all()
                    predictions[method]=pred;state[method]=beta
                    metrics.append(dict(base,horizon=h,mode=mode,method=method,**evaluate(yy,pred,mean,historical[te],control)))
                    coefficients.append(dict(base,horizon=h,mode=mode,method=method,intercept=beta[0],beta_index=beta[-1],beta_vix=beta[1] if mode=='with_lagged_vix' else float('nan')))
                    if method in ['ew','cw']:
                        model_key=f'g{groupno:03d}_h{h}_{mode}_{method}'
                        prediction_arrays[model_key]=pred
                        predict_metadata.append(dict(base,horizon=h,mode=mode,method=method,key=model_key,first_origin=str(df.loc[te,'date'].min().date()),last_origin=str(df.loc[te,'date'].max().date()),n=int(te.sum())))
                for method,pred in [('fixed_mean',mean),('expanding_mean',historical[te]),('zero',np.zeros(len(yy))),('control_only',control)]:metrics.append(dict(base,horizon=h,mode=mode,method=method,**evaluate(yy,pred,mean,historical[te],control)))
                training.append(dict(base,horizon=h,mode=mode,n_train=int(tr.sum()),first_training_origin=str(df.loc[tr,'date'].min().date()),last_training_origin=str(df.loc[tr,'date'].max().date()),latest_training_target=str(origin_end[tr].max().date()),n_test=int(te.sum()),first_test_origin=str(df.loc[te,'date'].min().date()),last_test_origin=str(df.loc[te,'date'].max().date()),training_target_mean=constant))
                lags=sorted(set([max(30,h-1),max(60,h-1),90]))
                loss={k:(yy-v)**2 for k,v in predictions.items()}
                for lag in lags:
                    common=dict(base,horizon=h,mode=mode,hac_lag=lag,primary_lag=bool(lag==max(30,h-1)),n=len(yy))
                    tests.append(dict(common,test='ew_vs_cw',method='cw',**mean_test(loss['ew']-loss['cw'],lag)))
                    for method in ['ew','cw']:
                        pred=predictions[method]
                        for benchmark,pred0 in [('fixed_mean',mean),('control_only',control)]:
                            if benchmark=='control_only' and mode=='index_only':continue
                            adjusted=(yy-pred0)**2-loss[method]+(pred-pred0)**2
                            tests.append(dict(common,test='clark_west_vs_'+benchmark,method=method,**mean_test(adjusted,lag,one_sided=True)))
                for phase in [0]:
                    ix=np.arange(phase,len(yy),h)
                    for method in ['ew','cw']:
                        pred=predictions[method]
                        nonoverlap.append(dict(base,horizon=h,mode=mode,method=method,phase=phase,n=len(ix),r2_oos_fixed_mean=1-np.mean((yy[ix]-pred[ix])**2)/np.mean((yy[ix]-mean[ix])**2),mse=float(np.mean((yy[ix]-pred[ix])**2))))
                if (sample,version,mask,w) in highlighted:
                    for j,date in enumerate(df.loc[te,'date']):daily.append(dict(base,horizon=h,mode=mode,date=str(date.date()),actual=yy[j],ew=predictions['ew'][j],cw=predictions['cw'][j],cfgi=predictions['cfgi'][j],momentum_volatility=predictions['momentum_volatility'][j],fixed_mean=mean[j],expanding_mean=historical[te][j],control_only=control[j]))
                if groupno==1:
                                                                                                    
                    tr_copy=np.column_stack([dtr,features['cw'][tr]]).copy();y_copy=y[tr].copy()
                    evil=np.array(features['cw']);evil[~known]=evil[~known]*-777+123
                    y_evil=y.copy();y_evil[~known]=y_evil[~known]*-777+123
                    assert np.array_equal(tr_copy,np.column_stack([dtr,evil[tr]])) and np.array_equal(y_copy,y_evil[tr])
        if groupno%32==0:print('FORECAST_SETTINGS',groupno,'/512',flush=True)
    assert groupno==512
    results=pd.DataFrame(metrics);inference=pd.DataFrame(tests)
    for _,g in inference.groupby(['test','horizon','mode','hac_lag']):inference.loc[g.index,'p_holm_horizon_mode']=multipletests(g.p,method='holm')[1]
    for _,g in inference[inference.primary_lag].groupby('test'):inference.loc[g.index,'p_holm_all_primary_horizons_modes']=multipletests(g.p,method='holm')[1]
    for name,rows in [('forecast_metrics',results),('forecast_tests',inference),('training_audit',pd.DataFrame(training)),('forecast_coefficients',pd.DataFrame(coefficients)),('nonoverlapping_forecasts',pd.DataFrame(nonoverlap)),('highlighted_daily_forecasts',pd.DataFrame(daily)),('cw_no_future_checks',pd.DataFrame(checks)),('target_purging_checks',pd.DataFrame(target_checks)),('prediction_metadata',pd.DataFrame(predict_metadata))]:rows.to_csv(OUT/(name+'.csv'),index=False)
    np.savez_compressed(OUT/'all_ew_cw_predictions.npz',**prediction_arrays)
    primary=results[(results.horizon==30)&(results['mode']=='index_only')&results.method.isin(['ew','cw'])]
    pair=primary.pivot(index=['sample','version','mask','window'],columns='method',values='mse').reset_index()
    pair['winner']=np.where(pair.cw<pair.ew,'cw',np.where(pair.ew<pair.cw,'ew','tie'))
    pair['cw_mse_reduction_vs_ew_percent']=100*(1-pair.cw/pair.ew)
    pair.to_csv(OUT/'primary_EW_vs_CW.csv',index=False)
    assert all(digest(Path(p))==h for p,h in protected.items())
    manifest=dict(status='complete',source_files_unchanged=True,protected_hashes=protected,settings=512,forecast_models=len(predict_metadata),metric_rows=len(results),test_rows=len(inference),target_purging=True,weights_fixed_before_test=True,coefficients_fixed_before_test=True,hac_crosscheck=True,earlier_holdout_indices_exact=True,exploratory=True)
    (OUT/'verification.json').write_text(json.dumps(manifest,indent=2))
    print('FORECASTS_COMPLETE',json.dumps({k:v for k,v in manifest.items() if k!='protected_hashes'}),flush=True)
    print('PRIMARY_WINNERS',pair.winner.value_counts().to_dict(),flush=True)
    print('PRIMARY_POSITIVE_R2',primary.groupby('method').r2_oos_fixed_mean.apply(lambda z:int((z>0).sum())).to_dict(),flush=True)

if __name__=='__main__':main()
