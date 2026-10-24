                                                                       
from pathlib import Path
import numpy as np
import pandas as pd
import json
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"data/private/analysis_input.csv"
OUTPUT=ROOT/"results"
def save_json(path,value):
    path.write_text(json.dumps(value,indent=2))


def input_diagnostics():
    from expanded_component_tests import defs,ROOT
    b=defs(ROOT/'scripts/build_cw_index_versions.py',set(),{'pd':pd,'np':np})
    raw=pd.read_csv(SOURCE,parse_dates=['date'])
    components=list(dict.fromkeys(c for families in b['VERSIONS'].values() for comps in families.values() for c in comps))
    out=OUTPUT/'input_diagnostics';out.mkdir(exist_ok=False);coverage=[]
    for sample,start in b['SAMPLES'].items():
      ix=raw.date.between(pd.Timestamp(start)+pd.Timedelta(days=90),pd.Timestamp('2026-08-26'))
      for w in b['WINDOWS']:
        columns=[f'{c}_rz_{w}' for c in components]
        part=raw.loc[ix,columns].replace([np.inf,-np.inf],np.nan)
        for c,column in zip(components,columns):coverage.append(dict(sample=sample,window=w,component=c,n_dates=int(ix.sum()),n_valid=int(part[column].notna().sum()),missing_percent=float(100*part[column].isna().mean())))
        for method in ['pearson','spearman']:part.rename(columns=dict(zip(columns,components))).corr(method=method).to_csv(out/f'{sample}_W{w}_{method}.csv')
    pd.DataFrame(coverage).to_csv(out/'component_missingness.csv',index=False)

def baseline_daily_indices():
    from expanded_component_tests import defs,ROOT
    from scipy.stats import spearmanr
    raw=pd.read_csv(SOURCE,parse_dates=['date']);params=pd.read_csv(OUTPUT/'expanded/parameters.csv')
    b=defs(ROOT/'scripts/build_cw_index_versions.py',{'rz_col','flatten_components','build_ew_index','apply_cw_weights'},{'pd':pd,'np':np,'spearmanr':spearmanr})
    pca=defs(ROOT/'reproduction/test_pca_momentum_baselines.py',{'apply_pca'},{'pd':pd,'np':np})
    series=[]
    for (sample,version,w,scope),g in params[params['mask'].eq(0)].groupby(['sample','version','window','scope']):
        families=b['VERSIONS'][version];weights=dict(zip(g.component,g.cw_weight))
        state=dict(columns=[f'{c}_rz_{w}' for c in g.component],directions=g.direction.to_numpy(),mean=g.pca_mean.to_numpy(),sd=g.pca_sd.to_numpy(),loading=g.pca_loading.to_numpy())
        complete=np.isfinite(raw[state['columns']]).all(axis=1);pc=pd.Series(np.nan,index=raw.index)
        pc[complete]=pca['apply_pca'](raw[complete],state)
        values={'ew':b['build_ew_index'](raw,families,int(w))[0],'cw':b['apply_cw_weights'](raw,families,int(w),weights),'pca':pc}
        formal=raw.date>=pd.Timestamp(b['SAMPLES'][sample])+pd.Timedelta(days=90)
        for method,vals in values.items():
                                                                           
                                                                         
            data=pd.DataFrame({'date':raw.date,'raw_index':vals,'rank_full_available_history':vals.expanding().rank(pct=True)*100,'rank_from_formal_sample_start':vals.where(formal).expanding().rank(pct=True)*100})
            series.append(data.assign(sample=sample,version=version,window=w,scope=scope,method=method))
    pd.concat(series,ignore_index=True).to_csv(OUTPUT/'expanded/baseline_daily_indices.csv',index=False)

def period_stability():
    import statsmodels.api as sm
    from statsmodels.stats.multitest import multipletests
    from scipy.stats import norm,chi2
    from expanded_component_tests import defs,ROOT
    raw=pd.read_csv(SOURCE,parse_dates=['date'])
    raw['target']=raw.log_return.rolling(30).sum().shift(-30);raw['target_end']=raw.date+pd.Timedelta(days=30)
    baseline=pd.read_csv(OUTPUT/'expanded/baseline_daily_indices.csv',parse_dates=['date'])
    b=defs(ROOT/'scripts/build_cw_index_versions.py',{'rz_col','build_ew_index'},{'pd':pd,'np':np})
    ch=defs(ROOT/'reproduction/test_newey_west.py',{'calendar_hac'},{'pd':pd,'np':np})['calendar_hac']
    contrast=defs(ROOT/'reproduction/test_period_stability.py',{'contrast'},{'np':np,'norm':norm})['contrast']
    out=OUTPUT/'period_stability';out.mkdir(exist_ok=False);series=[];rows=[];checks=[]
    for version in ['baseline_all_families','market_behavioral']:
      families=b['VERSIONS'][version]
      for w in b['WINDOWS']:
        ew=b['build_ew_index'](raw,families,w)[0]
        series.append((dict(version=version,window=w,method='EW',family='ew_original',weights='none'),ew))
        no={f:{c:d for c,d in v.items() if c!='github_commits'} for f,v in families.items()}
        series.append((dict(version=version,window=w,method='EW_no_GitHub',family='ew_no_github',weights='none'),b['build_ew_index'](raw,no,w)[0]))
        for sample in b['SAMPLES']:
            values=baseline[(baseline['sample']==sample)&baseline.version.eq(version)&baseline.window.eq(w)&baseline.scope.eq('retrospective_full_sample')&baseline.method.eq('cw')].set_index('date').raw_index.reindex(raw.date).to_numpy()
            series.append((dict(version=version,window=w,method='CW',family='cw_fixed_definition',weights=sample),values))
    for meta,index in series:
      data=raw[['date','target','target_end','vix']].copy();data['index']=np.asarray(index)
      boundary=pd.Timestamp('2023-07-10')
      for poststart in [boundary,boundary+pd.Timedelta(days=90)]:
        pre=data.date.ge('2022-01-30')&data.date.lt(boundary)&data.target_end.lt(boundary)
        post=data.date.ge(poststart)&data.target.notna()
        for control in ['vix','none']:
            q=data[pre|post].dropna(subset=['target','index']+(['vix'] if control=='vix' else [])).copy()
            q['post']=q.date.ge(poststart).astype(float)
            a=q[q.post.eq(0)];z=q[q.post.eq(1)];assert a.target_end.max()<z.date.min()
            x=pd.DataFrame({'const':1.,'index':q['index'],'post':q.post,'index_post':q['index']*q.post},index=q.index)
            if control=='vix':x['vix']=q.vix;x['vix_post']=q.vix*q.post
            fit=sm.OLS(q.target,x).fit();cols=x.columns.tolist();k=len(cols);beta=np.asarray(fit.params)
            vp=np.eye(k)[cols.index('index')];vd=np.eye(k)[cols.index('index_post')]
            separate=['index']+(['vix'] if control=='vix' else [])
            ba=sm.OLS(a.target,sm.add_constant(a[separate])).fit().params['index'];bz=sm.OLS(z.target,sm.add_constant(z[separate])).fit().params['index']
            assert np.isclose(beta@vp,ba,atol=1e-10) and np.isclose(beta@(vp+vd),bz,atol=1e-10)
            checks.append(dict(meta,control=control,post_start=str(poststart.date()),pooled_matches_separate=True,n_pre=len(a),n_post=len(z)))
            restriction=np.eye(k)[[cols.index(c) for c in ['post','index_post']+(['vix_post'] if control=='vix' else [])]]
            for lag in [30,60,90]:
              obs=fit.get_robustcov_results(cov_type='HAC',maxlags=lag,use_correction=True,use_t=False).cov_params()
              for units,cov in [('observations',obs),('calendar_days',ch(fit,q.date,lag))]:
                cov=np.asarray(cov);assert np.linalg.eigvalsh(cov).min()>-1e-10
                row=dict(meta,control=control,post_start=str(poststart.date()),lags=lag,lag_units=units,n_pre=len(a),n_post=len(z))
                for label,vector in [('pre',vp),('post',vp+vd),('delta',vd)]:row.update({label+'_'+c:v for c,v in contrast(beta,vector,cov).items()})
                rb=restriction@beta;wald=float(rb@np.linalg.solve(restriction@cov@restriction.T,rb))
                row.update(joint_shift_wald=wald,joint_shift_p=float(chi2.sf(wald,len(restriction))));rows.append(row)
    result=pd.DataFrame(rows)
    for _,ix in result.groupby(['family','control','post_start','lags','lag_units']).groups.items():result.loc[ix,'delta_p_holm_family']=multipletests(result.loc[ix,'delta_p'],method='holm')[1]
    result.to_csv(out/'slope_change_results.csv',index=False);pd.DataFrame(checks).to_csv(out/'pooled_separate_checks.csv',index=False)
    save_json(out/'verification.json',dict(status='complete',models=len(checks),covariance_results=len(result),pre_post_outcomes_nonoverlapping=True,pooled_matches_separate=True,scope='Retrospective sensitivity at fixed July 2023 boundary; CW uses one fixed full-sample definition on both sides; not causal/OOS break evidence. Not automatically restored to article or slides.'))

def quantile_rechecks():
    import statsmodels.api as sm
    from expanded_component_tests import defs,ROOT,CUT,END,DROPS
    from scipy.stats import spearmanr
    out=OUTPUT/'expanded';table=pd.read_csv(out/'statistical_tests.csv')
    raw=pd.read_csv(SOURCE,parse_dates=['date'])
    b=defs(ROOT/'scripts/build_cw_index_versions.py',{'rz_col','flatten_components','compute_stress','build_ew_index','compute_cw_weights','apply_cw_weights'},{'pd':pd,'np':np,'spearmanr':spearmanr})
    helper=defs(ROOT/'reproduction/test_out_of_sample.py',{'fit_weights'},{'pd':pd,'np':np})
    pca=defs(ROOT/'reproduction/test_pca_momentum_baselines.py',{'fit_pca','apply_pca'},{'pd':pd,'np':np})
    stored=np.load(out/'paired_bootstrap_inputs.npz');log=[]
    for ix,r in table[(table.test=='quantile')&table.iteration_limit.eq(True)].iterrows():
        families={f:{c:d for c,d in comps.items() if c not in {c for j,c in enumerate(DROPS) if int(r['mask'])&(1<<j)}} for f,comps in b['VERSIONS'][r.version].items()}
        if r.scope=='fixed_training_holdout':
            eligible=raw.date>CUT;values=stored['feature::'+r.strategy_id]
        else:
            eligible=raw.date>=pd.Timestamp(b['SAMPLES'][r['sample']])+pd.Timedelta(days=90)
            if r.method=='ew':vals=b['build_ew_index'](raw,families,int(r.window))[0]
            elif r.method=='cw':
                weights=helper['fit_weights'](raw,b['SAMPLES'][r['sample']],END,families,int(r.window),b)[0]
                vals=b['apply_cw_weights'](raw,families,int(r.window),weights)
            else:
                state=pca['fit_pca'](raw,b['SAMPLES'][r['sample']],END,families,int(r.window),b)
                complete=np.isfinite(raw[state['columns']]).all(axis=1);vals=pd.Series(np.nan,index=raw.index);vals[complete]=pca['apply_pca'](raw[complete],state)
            values=vals[eligible].to_numpy()
        y=raw.log_return.rolling(int(r.horizon)).sum().shift(-int(r.horizon))[eligible].to_numpy()
        pair=pd.DataFrame({'index':values,'target':y}).dropna()
        fit=sm.QuantReg(pair.target,sm.add_constant(pair[['index']])).fit(q=r['quantile'],max_iter=20000)
        for c,v in [('beta',fit.params['index']),('se_asymptotic',fit.bse['index']),('p_asymptotic_descriptive',fit.pvalues['index']),('iterations',fit.iterations),('iteration_limit',fit.iterations>=20000)]:table.loc[ix,c]=v
        log.append(dict(strategy_id=r.strategy_id,scope=r.scope,horizon=r.horizon,quantile=r['quantile'],iterations=fit.iterations,converged=fit.iterations<20000))
    (out/'statistical_tests.csv').rename(out/'statistical_tests_before_quantile_recheck.csv')
    table.to_csv(out/'statistical_tests.csv',index=False);pd.DataFrame(log).to_csv(out/'quantile_convergence_rechecks.csv',index=False)
    save_json(out/'quantile_recheck_verification.json',dict(rechecked=len(log),remaining_iteration_limits=int(table.iteration_limit.eq(True).sum())))

def monthly_chronology():
    from expanded_component_tests import defs,ROOT,CUT,END
    from scipy.stats import spearmanr
    raw=pd.read_csv(SOURCE,parse_dates=['date'])
    b=defs(ROOT/'scripts/build_cw_index_versions.py',{'rz_col','flatten_components','compute_stress','build_ew_index','compute_cw_weights','apply_cw_weights'},{'pd':pd,'np':np,'spearmanr':spearmanr})
    helper=defs(ROOT/'reproduction/test_out_of_sample.py',{'fit_weights','evaluate'},{'pd':pd,'np':np})
    out=OUTPUT/'monthly';out.mkdir(exist_ok=False);metrics=[];weights_rows=[];series=[]
    raw['forward_log_return_30d']=raw.log_return.rolling(30).sum().shift(-30)
    raw['forward_absolute_log_return_1d']=raw.log_return.abs().shift(-1)
    for sample,start in b['SAMPLES'].items():
      for version,families in b['VERSIONS'].items():
        if sample=='sample_a_2021_plus' and version.endswith('with_taker'):continue
        for w in b['WINDOWS']:
          ew=b['build_ew_index'](raw,families,w)[0]
          cw=pd.Series(np.nan,index=raw.index)
          for month in pd.date_range('2025-01-01','2026-08-01',freq='MS'):
            cutoff=month-pd.Timedelta(days=1)
            weights,corr,counts,cal=helper['fit_weights'](raw,start,cutoff,families,w,b)
            ix=raw.date.between(month,min(month+pd.offsets.MonthEnd(0),END))
            cw[ix]=b['apply_cw_weights'](raw,families,w,weights)[ix]
            assert pd.Timestamp(cal['latest_available_return_date'])<month
            for c,weight in weights.items():weights_rows.append(dict(sample=sample,version=version,window=w,month=str(month.date()),component=c,weight=weight,**cal))
          ix=(raw.date>CUT)&(raw.date<=END)
          group=raw.loc[ix,['date','cfgi','forward_log_return_30d','forward_absolute_log_return_1d']].copy();group['ew']=ew[ix];group['cw']=cw[ix]
          result=helper['evaluate'](group)
          metrics.append(dict(sample=sample,version=version,window=w,scheme='monthly_expanding',**result))
          series.append(group.assign(sample=sample,version=version,window=w))
    pd.DataFrame(metrics).to_csv(out/'monthly_metrics.csv',index=False);pd.DataFrame(weights_rows).to_csv(out/'monthly_weights.csv',index=False);pd.concat(series).to_csv(out/'monthly_series.csv',index=False)
    save_json(out/'verification.json',dict(status='complete',settings=len(metrics),monthly_training_only=True,forecasts_not_refit=True,warning='Descriptive chronological index validation, not a new direct-return forecast or untouched external test'))
