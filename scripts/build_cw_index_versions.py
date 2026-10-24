                                                                       
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


WINDOWS         = [7, 30, 60, 90]

WARMUP_DAYS     = 90

STRESS_QUANTILE = 0.90

MIN_OBS         = 30

SAMPLES = {
    "sample_a_2021_plus": "2021-11-01",
    "sample_b_2023_plus": "2023-07-10",
}

VERSIONS = {
    "baseline_all_families": {
        "market": {
            "momentum_7d":         +1,
            "volatility_30d":      -1,
            "btc_dominance_proxy": -1,
            "volume_usd_proxy":    +1,
            "usdt_dominance":      -1,
        },
        "derivatives": {
            "funding_zscore":    +1,
            "liquidation_proxy": -1,
            "dvol":              -1,
        },
        "behavioral": {
            "google_trends_sentiment_ratio": +1,
            "wikipedia_views_bitcoin":        +1,
            "reddit_sentiment_score":         +1,
            "github_commits":                 +1,
        },
    },

    "baseline_all_families_with_taker": {
        "market": {
            "momentum_7d":         +1,
            "volatility_30d":      -1,
            "btc_dominance_proxy": -1,
            "volume_usd_proxy":    +1,
            "usdt_dominance":      -1,
        },
        "derivatives": {
            "funding_zscore":         +1,
            "liquidation_proxy":      -1,
            "dvol":                   -1,
            "taker_buy_volume_ratio": +1,
        },
        "behavioral": {
            "google_trends_sentiment_ratio": +1,
            "wikipedia_views_bitcoin":        +1,
            "reddit_sentiment_score":         +1,
            "github_commits":                 +1,
        },
    },

    "market_behavioral": {
        "market": {
            "momentum_7d":         +1,
            "volatility_30d":      -1,
            "btc_dominance_proxy": -1,
            "volume_usd_proxy":    +1,
            "usdt_dominance":      -1,
        },
        "behavioral": {
            "google_trends_sentiment_ratio": +1,
            "wikipedia_views_bitcoin":        +1,
            "reddit_sentiment_score":         +1,
            "github_commits":                 +1,
        },
    },
}

def rz_col(name, window):
    return f"{name}_rz_{window}"

def to_score_0_100(series: pd.Series) -> pd.Series:
       
                                          

                                                 

                                            
                                  

                      
                       
       
    return series.expanding().rank(pct=True) * 100

def flatten_components(families):
    out = {}

    for family_name, comps in families.items():
        for comp, direction in comps.items():
            out[comp] = {
                "family": family_name,
                "direction": direction,
            }

    return out

def compute_stress(df):
       
                                                                            

                                                  

                                                     

                                                                       
                              
       

    fwd_abs = df["log_return"].abs().shift(-1)

    threshold = fwd_abs.dropna().quantile(STRESS_QUANTILE)

    flag = (fwd_abs >= threshold).astype(int)

                                      
    if len(flag) > 0:
        flag.iat[-1] = 0

    return flag, threshold, flag.astype(bool)

def build_ew_index(df, families, window):
       
                              
                                        
                                     

                                                                         
                                    
       

    family_df = pd.DataFrame(index=df.index)

    for family_name, comps in families.items():
        aligned = {}

        for comp, direction in comps.items():
            col = rz_col(comp, window)

            if col in df.columns:
                aligned[comp] = df[col] * direction

        if aligned:
            family_df[family_name] = (
                pd.DataFrame(aligned, index=df.index)
                .mean(axis=1, skipna=True)
            )

    if family_df.empty:
        return pd.Series(np.nan, index=df.index), family_df

    ew = family_df.mean(axis=1, skipna=True)

    return ew, family_df

def compute_cw_weights(df, families, window, stress_mask):
       
                                        

              
                                                    
                                            
                                              
                                                  

                   
                                                            
                                                                            
       

    components = flatten_components(families)

    fwd_abs_ret = df["log_return"].abs().shift(-1)

    raw_weights = {}
    corr_values = {}

    for comp, meta in components.items():
        col = rz_col(comp, window)

        if col not in df.columns:
            raw_weights[comp] = 0.0
            corr_values[comp] = np.nan
            continue

        raw = df[col]

        stress_df = pd.concat(
            [
                raw.rename("raw"),
                fwd_abs_ret.rename("fwd"),
                stress_mask.rename("stress"),
            ],
            axis=1,
        )

        stress_df = (
            stress_df[stress_df["stress"]]
            .dropna(subset=["raw", "fwd"])
        )

        if len(stress_df) < MIN_OBS:
            raw_weights[comp] = 0.0
            corr_values[comp] = np.nan
            continue

        corr, _ = spearmanr(
            stress_df["raw"],
            stress_df["fwd"],
        )

        corr = float(corr) if not np.isnan(corr) else 0.0

        corr_values[comp] = corr
        raw_weights[comp] = abs(corr)

    total = sum(raw_weights.values())

    if total == 0:
        print("  WARNING: all CW raw weights are zero — using uniform fallback")

        n = len(components)

        weights = {
            comp: 1.0 / n
            for comp in components
        }

        return weights, corr_values, raw_weights

    weights = {
        comp: raw_weight / total
        for comp, raw_weight in raw_weights.items()
    }

    return weights, corr_values, raw_weights

def apply_cw_weights(df, families, window, weights):
       
                                                                   

                      
                                                     
                                                                       
                                         

                                                                  
                                                                     
                                     
       

    components = flatten_components(families)

    cw = pd.Series(0.0, index=df.index, dtype=float)
    weight_used = pd.Series(0.0, index=df.index, dtype=float)

    for comp, meta in components.items():
        col = rz_col(comp, window)
        weight = weights.get(comp, 0.0)

        if weight == 0 or col not in df.columns:
            continue

        aligned = df[col] * meta["direction"]

        valid = aligned.notna()

        cw.loc[valid] += (
            weight * aligned.loc[valid]
        )

        weight_used.loc[valid] += weight

    cw = cw / weight_used.replace(0, np.nan)
    cw = cw.where(weight_used > 0, np.nan)

    return cw
