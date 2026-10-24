                                                                       
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from scipy.stats import norm


def contrast(beta,covector,cov):
    value=float(covector@beta)
    se=float(np.sqrt(covector@cov@covector))
    return dict(beta=value,se=se,p=float(2*norm.sf(abs(value/se))),
        ci_low=float(value-1.959963984540054*se),ci_high=float(value+1.959963984540054*se))
