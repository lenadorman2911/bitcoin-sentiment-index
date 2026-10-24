import unittest,sys,json,tempfile
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import scripts.build_cw_index_versions as b
from reproduction.test_out_of_sample import fit_weights
from reproduction.test_investment_value import self_tests
from compare_public_indices import compare

class CoreTests(unittest.TestCase):
    def test_simulation(self):self.assertTrue(all(self_tests().values()))
    def test_ew_missing_components(self):
        d=pd.DataFrame({'a_rz_7':[1.,np.nan],'z_rz_7':[3.,5.],'c_rz_7':[9.,9.]})
        result=b.build_ew_index(d,{'one':{'a':1,'z':1},'two':{'c':-1}},7)[0]
        np.testing.assert_allclose(result,[-3.5,-2.])
    def test_cw_available_weight_renormalization(self):
        d=pd.DataFrame({'a_rz_7':[1.,np.nan],'z_rz_7':[3.,5.]})
        x=b.apply_cw_weights(d,{'one':{'a':1,'z':-1}},7,{'a':.25,'z':.75})
        np.testing.assert_allclose(x,[-2.,-5.])
    def test_no_post_cutoff_returns(self):
        rng=np.random.default_rng(9);d=pd.DataFrame({'date':pd.date_range('2020-01-01',periods=800),'log_return':rng.normal(0,.02,800),'a_rz_7':rng.normal(size=800)})
        cutoff=d.date.iloc[599];families={'market':{'a':1}}
        w,_,_,m=fit_weights(d,'2020-01-01',cutoff,families,7,vars(b))
        d.loc[d.date>cutoff,['log_return','a_rz_7']]=999
        w2,_,_,m2=fit_weights(d,'2020-01-01',cutoff,families,7,vars(b))
        self.assertEqual(w,w2);self.assertEqual(m,m2)
    def test_provider_files_remain_independent(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);dates=pd.date_range('2020-01-01',periods=12)
            for name,v in [('first',np.arange(12)),('second',[4,8,3,2,6,1,9,5,11,7,10,0])]:
                pd.DataFrame({'date':dates,'value':v}).to_csv(p/(name+'.csv'),index=False)
            config=[dict(name=n,file=n+'.csv',source_url='https://example.org/'+n,collection_method='synthetic test') for n in ['first','second']]
            (p/'providers.json').write_text(json.dumps(config))
            result=compare(p,p/'result','2026-08-26');self.assertEqual(result.iloc[0]['n'],12)
            self.assertLess(abs(result.iloc[0].pearson),.99)
            config[1]['file']='first.csv';(p/'providers.json').write_text(json.dumps(config))
            with self.assertRaises(ValueError):compare(p,p/'other-result','2026-08-26')

if __name__=='__main__':unittest.main()
