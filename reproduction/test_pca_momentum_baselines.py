                                                                       
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def fit_pca(df,start,cutoff,families,window,builder):
    components=[c for values in families.values() for c in values]
    directions=np.array([sign for values in families.values() for sign in values.values()],dtype=float)
    cols=[f'{c}_rz_{window}' for c in components]
    train=df[df.date.between(pd.Timestamp(start)+pd.Timedelta(days=90),cutoff)].copy()
    complete=train[cols].notna().all(axis=1)&np.isfinite(train[cols]).all(axis=1)
    observed=train[complete]
    if len(observed)<max(100,len(cols)*5):raise RuntimeError('Too few complete PCA training rows')
    matrix=observed[cols].to_numpy()*directions
    mean=matrix.mean(axis=0);sd=matrix.std(axis=0,ddof=1)
    if (sd<=0).any():raise RuntimeError('Constant PCA training component')
    standardized=(matrix-mean)/sd
    _,singular,vt=np.linalg.svd(standardized,full_matrices=False)
    vector=vt[0].copy()
    score=standardized@vector
    ew,_=builder['build_ew_index'](observed,families,window)
    correlation=float(np.corrcoef(score,ew.to_numpy())[0,1])
    orientation=1 if correlation>=0 else -1
    if abs(correlation)<1e-12:
        orientation=1 if vector[np.argmax(abs(vector))]>=0 else -1
    vector*=orientation
    eigenvalues=singular**2/(len(observed)-1)
    covariance=standardized.T@standardized/(len(observed)-1)
    if not np.allclose(covariance@vector,eigenvalues[0]*vector,atol=1e-9,rtol=1e-9):
        raise RuntimeError('SVD factor fails eigenvector check')
    if not np.isclose(np.linalg.norm(vector),1):raise RuntimeError('Nonunit PCA direction')
    metadata=dict(eligible_rows=len(train),complete_rows=len(observed),excluded_rows=len(train)-len(observed),
                  first_training_date=str(observed.date.min().date()),last_training_date=str(observed.date.max().date()),
                  requested_cutoff=str(cutoff.date()),number_components=len(cols),
                  explained_variance_ratio=float(eigenvalues[0]/eigenvalues.sum()),
                  first_eigenvalue=float(eigenvalues[0]),second_eigenvalue=float(eigenvalues[1]),
                  orientation_correlation_ew=abs(correlation),original_sign_multiplier=orientation)
    return dict(columns=cols,components=components,directions=directions,mean=mean,sd=sd,loading=vector,metadata=metadata)

def apply_pca(df,state):
    values=df[state['columns']].to_numpy()*state['directions']
    if not np.isfinite(values).all():raise RuntimeError('Missing PCA test component')
    return ((values-state['mean'])/state['sd'])@state['loading']
