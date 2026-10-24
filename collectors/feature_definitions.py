                                                                            
import numpy as np
import pandas as pd

def add_features(df):
    print("\nCreating derived features...")

    df = df.sort_values("date").reset_index(drop=True)

    if "price" in df.columns:
        df["return"] = df["price"].pct_change()
        df["log_return"] = np.log(df["price"] / df["price"].shift(1))
        df["momentum_7d"] = df["price"] / df["price"].shift(7) - 1

    if "return" in df.columns:
        df["volatility_30d"] = df["return"].rolling(30).std()
        df["volatility_7d"] = df["return"].rolling(7).std()

    if "volume_btc" in df.columns:
        df["volume_ma_30"] = df["volume_btc"].rolling(30).mean()
        df["volume_volatility_30d"] = df["volume_btc"].rolling(30).std()
        df["volume_spike"] = df["volume_btc"] / df["volume_ma_30"]

    if "volume_btc" in df.columns and "price" in df.columns:
        df["volume_usd_proxy"] = df["volume_btc"] * df["price"]

    if "funding_rate" in df.columns:
        df["funding_volatility"] = df["funding_rate"].rolling(30).std()

        funding_mean = df["funding_rate"].rolling(30).mean()
        funding_std = df["funding_rate"].rolling(30).std()

        df["funding_zscore"] = (df["funding_rate"] - funding_mean) / funding_std

    if "return" in df.columns and "volume_btc" in df.columns:
        df["liquidation_proxy"] = df["return"].abs() * df["volume_btc"]

                            
    if "btc_dominance" in df.columns and "btc_dominance_proxy" not in df.columns:
        df = df.rename(columns={"btc_dominance": "btc_dominance_proxy"})

    return df
