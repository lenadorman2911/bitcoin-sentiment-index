                                                                       
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def calendar_hac(fit,dates,lags):
                                                                              

                                                                             
                                                                                
       
    dates=pd.DatetimeIndex(dates)
    if dates.has_duplicates or not dates.is_monotonic_increasing:
        raise RuntimeError('Invalid model calendar')
    calendar=pd.date_range(dates.min(),dates.max(),freq='D')
    observed=fit.model.exog*np.asarray(fit.resid)[:,None]
    scores=np.zeros((len(calendar),observed.shape[1]))
    scores[calendar.get_indexer(dates)]=observed
    middle=scores.T@scores
    for lag in range(1,lags+1):
        cross=scores[lag:].T@scores[:-lag]
        middle+=(1-lag/(lags+1))*(cross+cross.T)
    bread=np.asarray(fit.normalized_cov_params)
    n,k=fit.model.exog.shape
    return bread@middle@bread*(n/(n-k))
