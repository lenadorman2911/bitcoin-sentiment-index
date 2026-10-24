                                                                                  
from pathlib import Path
import ast, hashlib, itertools, json, sys, warnings, os
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, ttest_ind, f as fdist
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.multitest import multipletests
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'data/private/analysis_input.csv'
OUT = ROOT / 'results/expanded'
END = pd.Timestamp('2026-08-26')
CUT = pd.Timestamp('2024-12-31')
DROPS = ['github_commits', 'volume_usd_proxy', 'wikipedia_views_bitcoin', 'usdt_dominance', 'liquidation_proxy']
HORIZONS = [1, 7, 30, 60, 90]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def defs(path, names, namespace):
    tree = ast.parse(path.read_text())
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
            try:
                namespace[n.targets[0].id] = ast.literal_eval(n.value)
            except (ValueError, TypeError):
                pass
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace

def binary_sim(target, btc, cost):
    before = np.r_[0, target[:-1]]
    fee = np.where(target > before, cost / (1 + cost), np.where(target < before, cost, 0.0))
    net = (1 - fee) * (1 + target * btc) - 1
    net[-1] = (1 + net[-1]) * (1 - cost * target[-1]) - 1
    turnover = np.where(target > before, 1 / (1 + cost), np.where(target < before, 1.0, 0.0))
    turnover[-1] += target[-1]
    trades = int(np.count_nonzero(np.diff(np.r_[0, target, 0])))
    return (net, float(turnover.sum()), trades)

def stat_job(task):
    sid, metadata, scope, dates, values, cfgi, vix, ret, targets = task
    warnings.simplefilter('ignore')
    base = dict(strategy_id=sid, scope=scope, **metadata)
    x = pd.Series(values, index=pd.DatetimeIndex(dates), name='index')
    rows = []

    def add(test, **r):
        rows.append(dict(base, test=test, **r))

    def correlation(y, label):
        pair = pd.concat([x, pd.Series(y, index=x.index, name='y')], axis=1).dropna()
        add('correlation', target=label, n=len(pair), pearson=pair['index'].corr(pair.y), spearman=pair['index'].corr(pair.y, method='spearman'))
    correlation(cfgi, 'cfgi')
    correlation(vix, 'vix')
    rolling = x.rolling(180).corr(pd.Series(cfgi, index=x.index))
    add('rolling_cfgi_180', n=int(rolling.notna().sum()), mean=rolling.mean(), median=rolling.median(), minimum=rolling.min(), maximum=rolling.max())
    good = np.isfinite(values) & np.isfinite(ret)
    runs = []
    a = None
    for j, ok in enumerate(np.r_[good, False]):
        if ok and a is None:
            a = j
        if not ok and a is not None:
            runs.append((a, j))
            a = None
    a, b = max(runs, key=lambda ab: ab[1] - ab[0])
    xx = np.asarray(values)[a:b]
    rr = np.asarray(ret)[a:b]
    if len(xx) >= 100:
        ad = adfuller(xx, autolag='AIC')
        add('adf', n=int(ad[3]), statistic=ad[0], p=ad[1], selected_lag=ad[2], contiguous_start=str(pd.Timestamp(dates[a]).date()), contiguous_end=str(pd.Timestamp(dates[b - 1]).date()), complete_run_length=b - a)
        for lag in range(1, 8):
            yy = rr[lag:]
            restricted = np.column_stack([np.ones(len(yy))] + [rr[lag - k:len(rr) - k] for k in range(1, lag + 1)])
            full = np.column_stack([restricted] + [xx[lag - k:len(xx) - k] for k in range(1, lag + 1)])
            sr = float(np.sum((yy - restricted @ np.linalg.lstsq(restricted, yy, rcond=None)[0]) ** 2))
            su = float(np.sum((yy - full @ np.linalg.lstsq(full, yy, rcond=None)[0]) ** 2))
            dfree = len(yy) - full.shape[1]
            stat = max(0.0, (sr - su) / lag / (su / dfree))
            add('granger', lag=lag, n=len(yy), statistic=stat, p=float(fdist.sf(stat, lag, dfree)), complete_run_length=b - a)
    for h, y in zip(HORIZONS, targets):
        correlation(y, 'forward_' + str(h))
        pair = pd.DataFrame({'index': values, 'target': y, 'vix': vix}, index=x.index)
        z = pair[['index', 'target']].dropna()
        q25, q75 = z['index'].quantile([0.25, 0.75])
        lo = z.loc[z['index'] <= q25, 'target']
        hi = z.loc[z['index'] >= q75, 'target']
        add('high_low', horizon=h, n=len(z), n_low=len(lo), n_high=len(hi), q25=q25, q75=q75, mean_low=lo.mean(), mean_high=hi.mean(), difference=hi.mean() - lo.mean(), p_welch_descriptive=ttest_ind(hi, lo, equal_var=False).pvalue)
        q = pair.dropna()
        design = sm.add_constant(q[['index', 'vix']])
        fit = sm.OLS(q.target, design).fit()
        for cov, lag in [('HC3', 0), ('HAC', 30), ('HAC', 60), ('HAC', 90)]:
            robust = fit.get_robustcov_results(cov_type=cov, **{'maxlags': lag, 'use_correction': True} if cov == 'HAC' else {}, use_t=False)
            ci = robust.conf_int()[1]
            add('ols', horizon=h, covariance=cov, lag=lag, n=len(q), beta=robust.params[1], se=robust.bse[1], p=robust.pvalues[1], ci_low=ci[0], ci_high=ci[1], r_squared=fit.rsquared, hac_observation_lags=True, overlap_lag_coverage=bool(cov == 'HAC' and lag >= h - 1))
        for quantile in [0.25, 0.5, 0.75]:
            mod = sm.QuantReg(z.target, sm.add_constant(z[['index']])).fit(q=quantile, max_iter=2000)
            add('quantile', horizon=h, quantile=quantile, n=len(z), beta=mod.params['index'], se_asymptotic=mod.bse['index'], p_asymptotic_descriptive=mod.pvalues['index'], iterations=mod.iterations, iteration_limit=bool(mod.iterations >= 2000))
    return rows

def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT / 'construction_verification.json').exists(), 'Do not overwrite completed calculations'
    bpath = ROOT / 'scripts/build_cw_index_versions.py'
    hpath = ROOT / 'reproduction/test_out_of_sample.py'
    ppath = ROOT / 'reproduction/test_pca_momentum_baselines.py'
    ipath = ROOT / 'reproduction/test_investment_value.py'
    builder = defs(bpath, {'rz_col', 'flatten_components', 'compute_stress', 'build_ew_index', 'compute_cw_weights', 'apply_cw_weights'}, {'pd': pd, 'np': np, 'spearmanr': spearmanr})
    helper = defs(hpath, {'fit_weights'}, {'pd': pd, 'np': np})
    pca = defs(ppath, {'fit_pca', 'apply_pca'}, {'pd': pd, 'np': np})
    investment = defs(ipath, {'simulate', 'metrics', 'self_tests'}, {'pd': pd, 'np': np})
    protected = {str(p): digest(p) for p in [SOURCE, bpath, hpath, ppath, ipath, Path(__file__)]}
    plan = dict(recorded_utc=datetime.now(timezone.utc).isoformat(), status='exploratory; previously examined holdout, not fresh confirmatory data', drops=DROPS, all_subsets=32, deduplication='Absent components do not create duplicate configurations; retain mapping of all requested masks.', training_end=str(CUT.date()), end=str(END.date()), samples=builder['SAMPLES'], windows=builder['WINDOWS'], methods=['ew', 'cw', 'pca'], scopes=['retrospective_full_sample', 'fixed_training_holdout'], pca='Correlation-matrix PC1, complete training cases, train-only centering/scaling, sign by positive training EW correlation; never returns/CFGI.', missing='EW/CW retain original available-component rules. PCA complete cases. Main paired holdout comparisons use identical dates; full-sample available-case and common-method correlation results both reported. No gap-compression in time-series tests.', statistical_suite=['Pearson/Spearman CFGI, VIX, forward 1/7/30/60/90 log returns', '180-day rolling CFGI correlation', 'ADF AIC on longest complete contiguous run', 'Granger all lags 1..7 on same complete run', 'High-low quartile differences; Welch p descriptive only', 'OLS VIX-control HC3 and HAC 30/60/90 observation lags', 'Quantile regressions .25/.5/.75 asymptotic descriptive only', 'Cronbach alpha component sets, not index selection criterion', 'Retrospective LUNA/FTX and fixed-window event extrema', 'Train-only holdout investment tests, costs and lag sensitivity', 'Paired block-bootstrap CE and correlation differences, 4999 draws, blocks30/60/90, Holm families'], primary_horizon=30, primary_hac_lag=30, primary_window=90, primary_bootstrap_block=60, investment='Own training median after 90-day warmup, fixed. Below median100% BTC else cash; reverse rule descriptive. Lag2 primary/lag3 sensitivity; 0/5/10/25/50bps,10primary. Cash0; entry/exit costs; CEgamma3.', cfgi='Observed CFGI unchanged. Only trading threshold fitted separately on A/B training histories.', multiplicity='Holm separately by test/scope/target/horizon/covariance/lag/quantile where applicable across all configurations/methods; bootstrap per block and comparison family. No selection of best composition using these outcomes.', limitations=['Fixed-cutoff extension, not rerun of monthly expanding refits', 'Statistical regression tests in holdout fit association on holdout, not OOS return prediction', 'ADF/Granger complete-run restriction particularly reduces PCA Sample A', 'HAC lags count retained observations; VIX gaps are not imputed', 'HAC30/60 do not cover full overlap for90-day outcomes; HAC90 retained', 'Quantile and Welch asymptotic p-values are not time-dependence robust', 'Bootstrap conditions on estimated weights/thresholds; no nested fitting', 'The five-component exclusion list is not a claim that all retained component directions are proven', 'No taker backfill or volume replacement in historical A crises'])
    (OUT / 'analysis_plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    df = pd.read_csv(SOURCE, parse_dates=['date']).query('date<=@END').sort_values('date').reset_index(drop=True)
    assert df.date.diff().dropna().eq(pd.Timedelta(days=1)).all()
    assert np.allclose(df.log_return.dropna(), np.log1p(df['return'].dropna()), atol=1e-10)
    dates = pd.date_range('2025-01-04', END)
    btc = df.set_index('date').loc[dates, 'return'].to_numpy()
    assert len(dates) == 600
    checks = investment['self_tests']()
    rng = np.random.default_rng(20261021)
    for c in [0, 0.0005, 0.001, 0.0025, 0.005]:
        target = rng.integers(0, 2, 600).astype(float)
        old = investment['simulate'](target, btc, c)
        new = binary_sim(target, btc, c)
        assert np.allclose(old[0], new[0], atol=1e-15) and np.isclose(old[2].sum(), new[1]) and (old[3] == new[2])
    arrays = {}
    metadata = {}
    mappings = []
    params = []
    calibration = []
    thresholds = []
    metrics = []
    crises = []
    alpha = []
    tasks = []
    commoncorr = []
    events = []
    invariance = []
    registry_tree = ast.parse((ROOT / 'reproduction/audit_event_windows.py').read_text())
    registry_node = next((n for n in registry_tree.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and (n.targets[0].id == 'REGISTRY')))
    registry = eval(compile(ast.Expression(registry_node.value), 'event_registry', 'eval'), {'__builtins__': {}, 'dict': dict})
    pd.DataFrame(registry).to_csv(OUT / 'event_registry.csv', index=False)
    targets = {h: df.log_return.rolling(h).sum().shift(-h) for h in HORIZONS}
    nsettings = 0
    for sample, start in builder['SAMPLES'].items():
        for version, original in builder['VERSIONS'].items():
            if sample == 'sample_a_2021_plus' and version.endswith('with_taker'):
                continue
            present = {c for comps in original.values() for c in comps}
            unique = {}
            for mask in range(32):
                requested = [c for j, c in enumerate(DROPS) if mask & 1 << j]
                actual = tuple((c for c in requested if c in present))
                unique[actual] = sum((1 << DROPS.index(c) for c in actual))
                mappings.append(dict(sample=sample, version=version, requested_mask=mask, effective_mask=unique[actual], removed=';'.join(actual)))
            for dropped, mask in unique.items():
                families = {f: {c: d for c, d in comps.items() if c not in dropped} for f, comps in original.items()}
                components = [c for comps in families.values() for c in comps]
                directions = np.array([d for comps in families.values() for d in comps.values()])
                for w in builder['WINDOWS']:
                    nsettings += 1
                    ew = builder['build_ew_index'](df, families, w)[0]
                    base = dict(sample=sample, version=version, mask=mask, removed=';'.join(dropped), window=w, components=len(components))
                    trainmask = df.date.between(pd.Timestamp(start) + pd.Timedelta(days=90), CUT)
                    for scope, cutoff in [('retrospective_full_sample', END), ('fixed_training_holdout', CUT)]:
                        weights, corr, counts, cal = helper['fit_weights'](df, start, cutoff, families, w, builder)
                        state = pca['fit_pca'](df, start, cutoff, families, w, builder)
                        calibration.append(dict(base, scope=scope, **cal, **{'pca_' + k: v for k, v in state['metadata'].items()}))
                        for j, c in enumerate(state['components']):
                            params.append(dict(base, scope=scope, component=c, direction=state['directions'][j], cw_weight=weights[c], cw_stress_rho=corr[c], cw_n=counts[c], pca_mean=state['mean'][j], pca_sd=state['sd'][j], pca_loading=state['loading'][j]))
                        complete = np.isfinite(df[state['columns']]).all(axis=1)
                        pc = pd.Series(np.nan, index=df.index)
                        pc.loc[complete] = pca['apply_pca'](df.loc[complete], state)
                        values = {'ew': ew, 'cw': builder['apply_cw_weights'](df, families, w, weights), 'pca': pc}
                        eligible = df.date.between(pd.Timestamp(start) + pd.Timedelta(days=90) if scope == 'retrospective_full_sample' else pd.Timestamp('2025-01-01'), END)
                        indices = df.index[eligible]
                        comp = df.loc[eligible, [f'{c}_rz_{w}' for c in components]] * directions
                        comp = comp.dropna()
                        k = comp.shape[1]
                        if scope == 'retrospective_full_sample':
                            alpha.append(dict(base, n=len(comp), alpha=k / (k - 1) * (1 - comp.var(ddof=1).sum() / comp.sum(axis=1).var(ddof=1))))
                        shared = eligible & np.isfinite(pc) & np.isfinite(values['cw']) & np.isfinite(ew)
                        for method, vals in values.items():
                            sid = '|'.join([sample, version, str(mask), str(w), method])
                            meta = dict(base, method=method)
                            tasks.append((sid, meta, scope, df.loc[indices, 'date'].to_numpy(), vals.loc[indices].to_numpy(), df.loc[indices, 'cfgi'].to_numpy(), df.loc[indices, 'vix'].to_numpy(), df.loc[indices, 'log_return'].to_numpy(), [targets[h].loc[indices].to_numpy() for h in HORIZONS]))
                            for label, y in [('cfgi', df.cfgi), ('vix', df.vix), ('forward30', targets[30])]:
                                pair = pd.DataFrame({'x': vals[shared], 'y': y[shared]}).dropna()
                                commoncorr.append(dict(strategy_id=sid, **meta, scope=scope, target=label, n=len(pair), pearson=pair.x.corr(pair.y), spearman=pair.x.corr(pair.y, method='spearman')))
                            if scope == 'fixed_training_holdout':
                                metadata[sid] = meta
                                arrays['feature::' + sid] = vals.loc[df.date > CUT].to_numpy()
                                th = float(vals[trainmask].median())
                                thresholds.append(dict(strategy_id=sid, **meta, threshold=th, n_training=int(vals[trainmask].notna().sum())))
                                for lag in [2, 3]:
                                    signal = pd.Series(vals.to_numpy(), index=df.date).loc[dates - pd.Timedelta(days=lag)].to_numpy()
                                    assert np.isfinite(signal).all()
                                    for rule in ['contrarian', 'trend']:
                                        target = (signal < th).astype(float)
                                        if rule == 'trend':
                                            target = 1 - target
                                        for cost in [0, 5, 10, 25, 50]:
                                            net, turn, trades = binary_sim(target, btc, cost / 10000)
                                            metrics.append(dict(strategy_id=sid, **meta, rule=rule, return_lag=lag, cost_bps=cost, turnover=turn, trades=trades, average_btc_allocation=float(target.mean()), **investment['metrics'](net)))
                                            if lag == 2 and rule == 'contrarian' and (cost == 10):
                                                arrays['return::' + sid] = net
                            else:
                                score = vals.expanding().rank(pct=True) * 100
                                if sample == 'sample_a_2021_plus':
                                    for event, date in [('LUNA', '2022-05-11'), ('FTX', '2022-11-08')]:
                                        j = df.index[df.date.eq(date)][0]
                                        crises.append(dict(strategy_id=sid, **meta, event=event, date=date, raw=vals.iloc[j], score=score.iloc[j], cfgi=df.cfgi.iloc[j]))
                                for event in registry:
                                    center = pd.Timestamp(event['proposed'])
                                    if center < pd.Timestamp(start) + pd.Timedelta(days=90):
                                        continue
                                    for half in [10, 20, 35]:
                                        sub = score[df.date.between(center - pd.Timedelta(days=half), center + pd.Timedelta(days=half))]
                                        if sub.notna().sum() < 2 * half + 1:
                                            continue
                                        for kind in ['peak', 'trough']:
                                            j = sub.idxmax() if kind == 'peak' else sub.idxmin()
                                            date = df.date.iloc[j]
                                            events.append(dict(strategy_id=sid, **meta, event=event['key'], event_date=str(center.date()), halfwindow=half, kind=kind, extremum_date=str(date.date()), score=score.iloc[j], days_before=(center - date).days, boundary=bool(date in [center - pd.Timedelta(days=half), center + pd.Timedelta(days=half)])))
                        if scope == 'fixed_training_holdout' and mask == 0:
                            altered = df.copy()
                            future = altered.date > CUT
                            altered.loc[future, state['columns']] = altered.loc[future, state['columns']] * -777 + 123
                            altered['cfgi'] = altered.cfgi * -999 + 321
                            altered.loc[future, 'log_return'] = altered.loc[future, 'log_return'] * -777 + 123
                            other = pca['fit_pca'](altered, start, CUT, families, w, builder)
                            assert all((np.array_equal(state[k], other[k]) for k in ['mean', 'sd', 'loading']))
                            w2 = helper['fit_weights'](altered, start, CUT, families, w, builder)[0]
                            assert weights == w2
                            invariance.append(dict(base, pca_future_cfgi_invariant=True, cw_future_invariant=True))
            print('CONSTRUCTED', sample, version, 'settings', nsettings, flush=True)
    assert nsettings == 512 and len(metadata) == 1536 and (len(tasks) == 3072)
    for sample, start in builder['SAMPLES'].items():
        sid = 'CFGI|' + sample
        meta = dict(sample=sample, version='CFGI', mask=-1, removed='', window=0, components=1, method='cfgi')
        metadata[sid] = meta
        th = float(df.loc[df.date.between(pd.Timestamp(start) + pd.Timedelta(days=90), CUT), 'cfgi'].median())
        thresholds.append(dict(strategy_id=sid, **meta, threshold=th))
        for lag in [2, 3]:
            signals = df.set_index('date').loc[dates - pd.Timedelta(days=lag), 'cfgi'].to_numpy()
            for rule in ['contrarian', 'trend']:
                target = (signals < th).astype(float)
                if rule == 'trend':
                    target = 1 - target
                for cost in [0, 5, 10, 25, 50]:
                    net, turn, trades = binary_sim(target, btc, cost / 10000)
                    metrics.append(dict(strategy_id=sid, **meta, rule=rule, return_lag=lag, cost_bps=cost, turnover=turn, trades=trades, **investment['metrics'](net)))
                    if lag == 2 and rule == 'contrarian' and (cost == 10):
                        arrays['return::' + sid] = net
    for sid, target in [('buy_hold', np.ones(600)), ('constant_50', np.full(600, 0.5)), ('cash', np.zeros(600))]:
        for cost in [0, 5, 10, 25, 50]:
            net, _, turn, trades = investment['simulate'](target, btc, cost / 10000)
            metrics.append(dict(strategy_id=sid, sample='benchmark', version='benchmark', mask=-1, window=0, method=sid, rule='benchmark', return_lag=0, cost_bps=cost, turnover=float(turn.sum()), trades=trades, **investment['metrics'](net)))
            if cost == 10:
                arrays['return::' + sid] = net
    for sample, start in builder['SAMPLES'].items():
        for scope, begin in [('retrospective_full_sample', pd.Timestamp(start) + pd.Timedelta(days=90)), ('fixed_training_holdout', pd.Timestamp('2025-01-01'))]:
            ix = df.date.between(begin, END)
            tasks.append(('CFGI|' + sample, metadata['CFGI|' + sample], scope, df.loc[ix, 'date'].to_numpy(), df.loc[ix, 'cfgi'].to_numpy(), df.loc[ix, 'cfgi'].to_numpy(), df.loc[ix, 'vix'].to_numpy(), df.loc[ix, 'log_return'].to_numpy(), [targets[h].loc[ix].to_numpy() for h in HORIZONS]))
    arrays['cfgi_feature'] = df.loc[df.date > CUT, 'cfgi'].to_numpy()
    for name, rows in [('mask_mapping', mappings), ('parameters', params), ('calibration', calibration), ('training_thresholds', thresholds), ('strategy_metrics_all_sensitivities', metrics), ('crisis_diagnostics', crises), ('cronbach_alpha', alpha), ('common_method_correlations', commoncorr), ('fixed_window_events', events), ('no_future_checks', invariance)]:
        pd.DataFrame(rows).to_csv(OUT / (name + '.csv'), index=False)
    table = pd.DataFrame(metrics)
    primary = table[(table.cost_bps == 10) & (table.rule.eq('contrarian') & table.return_lag.eq(2) | table.rule.eq('benchmark'))]
    primary.to_csv(OUT / 'primary_metrics.csv', index=False)
    np.savez_compressed(OUT / 'paired_bootstrap_inputs.npz', **arrays)
    (OUT / 'strategy_metadata.json').write_text(json.dumps(metadata, indent=2))
    (OUT / 'construction_verification.json').write_text(json.dumps(dict(settings=1536, statistical_jobs=len(tasks), simulation_self_tests=checks, protected_hashes=protected), indent=2))
    print('CONSTRUCTION_SAVED; statistics jobs', len(tasks), flush=True)
    stats = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for j, result in enumerate(pool.map(stat_job, tasks, chunksize=4), 1):
            stats.extend(result)
            if j % 64 == 0:
                print('STATISTICS', j, '/', len(tasks), flush=True)
            if j % 256 == 0:
                pd.DataFrame(stats).to_csv(OUT / 'statistical_tests_checkpoint.csv', index=False)
    tests = pd.DataFrame(stats)
    for _, g in tests[tests.p.notna()].groupby(['test', 'scope', 'target', 'horizon', 'covariance', 'lag'], dropna=False):
        tests.loc[g.index, 'p_holm_family'] = multipletests(g.p, method='holm')[1]
    tests.to_csv(OUT / 'statistical_tests.csv', index=False)
    assert all((digest(Path(p)) == h for p, h in protected.items()))
    (OUT / 'statistical_verification.json').write_text(json.dumps(dict(status='complete', jobs=len(tasks), rows=len(tests), protected_sources_unchanged=True), indent=2))
    print('STATISTICS_COMPLETE', len(tests), flush=True)
if __name__ == '__main__':
    main()
