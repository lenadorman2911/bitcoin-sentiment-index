                                                                       
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def simulate(target,btc,cost):
                                                                                  
    n=len(btc);net=np.empty(n);fees=np.empty(n);turnover=np.empty(n)
    before=0.;trades=0
    for i,(w,r) in enumerate(zip(target,btc)):
        delta=w-before
        q=cost*delta/(1+cost*w) if delta>=0 else cost*(-delta)/(1-cost*w)
        traded=abs(w*(1-q)-before)
        assert np.isclose(q,cost*traded,atol=1e-12)
        assert 0<=q<1 and 0<=w<=1
        g=1+w*r
        net[i]=(1-q)*g-1
        fees[i]=q;turnover[i]=traded
        trades+=int(traded>1e-12)
        before=w*(1+r)/g
    terminal=cost*before
    net[-1]=(1+net[-1])*(1-terminal)-1
    fees[-1]+=terminal;turnover[-1]+=before
    trades+=int(before>1e-12)
    return net,fees,turnover,trades

def metrics(r):
    growth=np.cumprod(1+r)
    running=np.maximum.accumulate(np.r_[1.,growth])[1:]
    sd=np.std(r,ddof=1)
    return dict(total_return=float(growth[-1]-1),cagr=float(growth[-1]**(365/len(r))-1),
        annual_volatility=float(sd*np.sqrt(365)),sharpe_zero_rf=float(np.mean(r)/sd*np.sqrt(365)) if sd>0 else None,
        maximum_drawdown=float(np.min(growth/running-1)),
        ce_gamma3_annual=float(365*(np.mean(r)-1.5*np.var(r,ddof=1))))

def self_tests():
    r=np.array([.1,-.05,.02,.01])
    bh,_,_,_=simulate(np.ones(4),r,.001)
    assert np.isclose(np.prod(1+bh),np.prod(1+r)*(1-.001)/(1+.001))
    zero,_,_,_=simulate(np.zeros(4),r,.001)
    assert np.array_equal(zero,np.zeros(4))
    free,_,_,_=simulate(np.array([1,0,1,0]),r,0)
    assert np.allclose(free,np.array([.1,0,.02,0]))
    flat=np.zeros(4)
    paid,_,_,_=simulate(np.array([1,0,1,0]),flat,.001)
    assert np.isclose(np.prod(1+paid),((1-.001)/(1+.001))**2)
    return dict(buy_hold_entry_exit_exact=True,cash_zero=True,zero_cost_position_returns=True,round_trip_fees_exact=True)
