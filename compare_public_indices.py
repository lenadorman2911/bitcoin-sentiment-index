                                                                                      
import argparse,json
from pathlib import Path
from itertools import combinations
import pandas as pd

def load_provider(path,name,end):
    frame=pd.read_csv(path,usecols=['date','value'])
    frame['date']=pd.to_datetime(frame.date,format='%Y-%m-%d',errors='raise')
    frame['value']=pd.to_numeric(frame.value,errors='raise')
    if frame.date.duplicated().any():raise ValueError(f'Duplicate dates in {name}')
    if frame.value.isna().any():raise ValueError(f'Missing values in {name}; document exclusions before exporting')
    return frame.loc[frame.date<=end].set_index('date').value.rename(name)

def compare(inputs,out,end):
    config=json.loads((inputs/'providers.json').read_text())
    if not isinstance(config,list) or len(config)<2:raise ValueError('At least two provider records required')
    names=[x['name'] for x in config]
    if len(names)!=len(set(names)):raise ValueError('Provider names must be unique')
    frames={};resolved=set()
    for record in config:
        path=(inputs/record['file']).resolve()
        if inputs.resolve() not in path.parents:raise ValueError('Provider file must be inside the input directory')
        if path in resolved:raise ValueError('Each provider must have its own source file')
        if not record.get('source_url') or not record.get('collection_method'):raise ValueError('Source provenance required')
        resolved.add(path);frames[record['name']]=load_provider(path,record['name'],pd.Timestamp(end))
    out.mkdir(parents=True,exist_ok=False);rows=[]
    for a,b in combinations(names,2):
        pair=pd.concat([frames[a],frames[b]],axis=1).dropna();n=len(pair)
        rows.append(dict(index_a=a,index_b=b,n=n,pearson=pair.iloc[:,0].corr(pair.iloc[:,1]) if n>=10 else float('nan')))
    pd.DataFrame(rows).to_csv(out/'pairwise_correlations.csv',index=False)
    (out/'providers.json').write_text(json.dumps(config,indent=2))
    return pd.DataFrame(rows)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--end',default='2026-08-26');a=p.parse_args()
    compare(a.input_dir,a.output,a.end)
