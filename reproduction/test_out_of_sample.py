                                                                       
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def fit_weights(df,start,cutoff,families,window,ns):
    train=df[df.date.between(pd.Timestamp(start),cutoff)].reset_index(drop=True)
    if train.empty or train.date.max()>cutoff:
        raise RuntimeError('Invalid calibration cutoff')
    _,threshold,stress=ns['compute_stress'](train)
    future=train.log_return.abs().shift(-1)
    if future.iloc[-1]==future.iloc[-1] or stress.iloc[-1]:
        raise RuntimeError('Last training feature must not use a post-cutoff return')
    counts={component:int((stress&np.isfinite(train[f'{component}_rz_{window}'])&future.notna()).sum())
            for values in families.values() for component in values}
    short={component:n for component,n in counts.items() if n<ns['MIN_OBS']}
    if short:
        raise RuntimeError('Insufficient stress pairs; no silent fallback allowed: '+str(short))
    weights,correlations,raw=ns['compute_cw_weights'](train,families,window,stress)
    if sum(raw.values())<=0 or not np.isclose(sum(weights.values()),1):
        raise RuntimeError('Invalid calibration weights')
    metadata=dict(training_start=str(train.date.min().date()),training_end=str(train.date.max().date()),
                  last_predictor_date=str(train.date.iloc[-2].date()),
                  latest_available_return_date=str(train.date.iloc[-1].date()),
                  calibration_dates=len(train),observable_forward_returns=len(train)-1,
                  stress_days=int(stress.sum()),q90=float(threshold),minimum_component_stress_pairs=min(counts.values()))
    return weights,correlations,counts,metadata

def evaluate(group):
    cfgi=group[['ew','cw','cfgi']].dropna()
    if len(cfgi)!=len(group) or not np.isfinite(cfgi.to_numpy()).all():
        raise RuntimeError('EW/CW comparison must use complete common dates')
    ew=cfgi.ew.corr(cfgi.cfgi);cw=cfgi.cw.corr(cfgi.cfgi)
    result=dict(test_start=str(group.date.min().date()),test_end=str(group.date.max().date()),
                n_cfgi=len(cfgi),ew_pearson_cfgi=ew,cw_pearson_cfgi=cw,cw_minus_ew=cw-ew,
                ew_spearman_cfgi=cfgi.ew.corr(cfgi.cfgi,method='spearman'),
                cw_spearman_cfgi=cfgi.cw.corr(cfgi.cfgi,method='spearman'))
    for target in ['forward_log_return_30d','forward_absolute_log_return_1d']:
        pair=group[['ew','cw',target]].dropna()
        result['n_'+target]=len(pair)
        for method in ['ew','cw']:
            result[method+'_pearson_'+target]=pair[method].corr(pair[target])
            result[method+'_spearman_'+target]=pair[method].corr(pair[target],method='spearman')
    return result
