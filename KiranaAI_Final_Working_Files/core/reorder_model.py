"""One-week-ahead reorder forecast on original synthetic, chronological store-SKU panel."""
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix,roc_auc_score
import streamlit as st

class ReorderPredictor:
    FEATURE_COLS=['units_ordered_this_week','units_ordered_previous_week',
                  'units_ordered_last_4_weeks','orders_in_last_4_weeks',
                  'weeks_since_last_purchase','average_units_per_order','historical_reorder_interval_weeks']
    TARGET_COL='reorder_due_next_week'

    def __init__(self,reorder_df,catalog_df):
        self.raw_df=reorder_df.copy()
        self.catalog_df=catalog_df.copy()
        self.model=None
        self.metrics={}
        self.baseline_metrics={}
        self.feature_importance=[]
        self._train_and_evaluate()

    @staticmethod
    def _make_model():
        return Pipeline([('imputer',SimpleImputer(strategy='constant',fill_value=-1)),
                         ('scaler',StandardScaler()),
                         ('classifier',LogisticRegression(max_iter=500,class_weight='balanced',random_state=42))])

    @staticmethod
    def _measure(ytrue,pred,prob=None):
        m=dict(accuracy=float(accuracy_score(ytrue,pred)),
               precision=float(precision_score(ytrue,pred,zero_division=0)),
               recall=float(recall_score(ytrue,pred,zero_division=0)),
               f1=float(f1_score(ytrue,pred,zero_division=0)),
               confusion_matrix=confusion_matrix(ytrue,pred,labels=[0,1]).tolist())
        m['roc_auc']=float(roc_auc_score(ytrue,prob)) if prob is not None and len(np.unique(ytrue))==2 else None
        return m

    def _train_and_evaluate(self):
        df=self.raw_df
        tr=df[df.week_number.between(1,9)].dropna(subset=[self.TARGET_COL])
        va=df[df.week_number.between(10,12)].dropna(subset=[self.TARGET_COL])
        te=df[df.week_number.between(13,15)].dropna(subset=[self.TARGET_COL])
        future=df[df.week_number==16]
        if len(tr)!=10800 or len(va)!=3600 or len(te)!=3600 or len(future)!=1200:
            raise ValueError('Expected original 30×40×16 weekly panel and chronological split')
        self.validation_model=self._make_model()
        self.validation_model.fit(tr[self.FEATURE_COLS],tr[self.TARGET_COL].astype(int))
        vprobs=self.validation_model.predict_proba(va[self.FEATURE_COLS])[:,1]
        self.validation_metrics=self._measure(va[self.TARGET_COL].astype(int),(vprobs>=0.5).astype(int),vprobs)
        # Refit on train+validation ONLY; held-out test remains unseen.
        self.test_model=self._make_model()
        tv=pd.concat([tr,va])
        self.test_model.fit(tv[self.FEATURE_COLS],tv[self.TARGET_COL].astype(int))
        probs=self.test_model.predict_proba(te[self.FEATURE_COLS])[:,1]
        y=te[self.TARGET_COL].astype(int)
        self.metrics=self._measure(y,(probs>=0.5).astype(int),probs)
        self.metrics.update(model_name='Logistic Regression (balanced)',train_observations=len(tv),
               test_observations=len(te),train_period='Weeks 1–12 (train 1–9, validation 10–12)',
               test_period='Weeks 13–15',test_positive_rate=float(y.mean()))
        # Simple prior-week baseline on identical held-out target records.
        baseline=(te['units_ordered_this_week']>0).astype(int)
        self.baseline_metrics=self._measure(y,baseline)
        self.baseline_metrics.update(model_name='Repeat this week',test_observations=len(te))
        self.feature_importance=sorted([
          dict(feature=name,coefficient=float(weight),abs_impact=abs(float(weight)))
          for name,weight in zip(self.FEATURE_COLS,self.test_model.named_steps['classifier'].coef_[0])],
          key=lambda x:-x['abs_impact'])
        # Refit on ALL known labels in weeks 1–15 for the genuinely future 17th week prediction.
        history=df[df.week_number.between(1,15)].dropna(subset=[self.TARGET_COL])
        self.model=self._make_model()
        self.model.fit(history[self.FEATURE_COLS],history[self.TARGET_COL].astype(int))

    def get_evaluation_metrics(self):
        return dict(logistic_regression=self.metrics,baseline=self.baseline_metrics,
                    validation=self.validation_metrics,feature_importance=self.feature_importance)

    def predict_reorder_opportunities(self,store_id,current_order_skus=None,top_k=3):
        current_order_skus=set(current_order_skus or [])
        snapshot=self.raw_df[(self.raw_df.store_id==store_id)&(self.raw_df.week_number==16)].copy()
        if snapshot.empty:return []
        snapshot['reorder_probability']=self.model.predict_proba(snapshot[self.FEATURE_COLS])[:,1]
        catalog=self.catalog_df[['sku_id','brand','product_name','pack_size','category','availability','unit_price_inr']]
        merged=snapshot.merge(catalog,on='sku_id',how='inner')
        merged=merged[(merged.availability=='available')&(~merged.sku_id.isin(current_order_skus))]
        # Do not nudge never-ordered items from cold history on a fabricated model probability alone.
        merged=merged[merged['orders_in_last_4_weeks']>=1]
        merged=merged.sort_values('reorder_probability',ascending=False)
        ans=[]
        for _,row in merged.head(top_k).iterrows():
            # Conservative suggestion of individual packs, not inferred cartons.
            qty=max(1,round(float(row['average_units_per_order']))) if pd.notna(row['average_units_per_order']) else 1
            ans.append(dict(sku=row.sku_id,product_name=f'{row.brand} {row.product_name} {row.pack_size}',
                category=row.category,probability=float(row.reorder_probability),
                ordered_last_4w=int(row.orders_in_last_4_weeks),
                avg_qty_last_4w=float(row.units_ordered_last_4_weeks),
                suggested_quantity=min(qty,500),suggested_unit='pack',unit_price_inr=float(row.unit_price_inr)))
        return ans

@st.cache_resource
def get_reorder_predictor(reorder_df,catalog_df):
    return ReorderPredictor(reorder_df,catalog_df)
