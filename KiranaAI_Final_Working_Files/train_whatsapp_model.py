"""Train a small, catalog-safe product-family classifier on synthetic WhatsApp variants.
Run: python train_whatsapp_model.py
"""
from pathlib import Path
import json, re
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from core.catalog_matcher import normalize
ROOT=Path(__file__).resolve().parent
SOURCE_MAP={'SKU001':'PAR','SKU002':'PAR','SKU003':'MAG','SKU004':'SUR','SKU006':'FOR','SKU007':'FOR','SKU008':'TSL','SKU009':'AAS','SKU014':'COL','SKU016':'BRI','SKU018':'LAY'}
# Exclude incompatible source products (e.g. milk, soap, cola) rather than relabel them.

def build_examples():
    catalog=pd.read_csv(ROOT/'data/product_catalog.csv').fillna('')
    allowed=set(catalog.product_family_id)
    examples=[]
    for _,r in catalog.iterrows():
        for alias in str(r.search_aliases).split('|')+str(r.family_aliases).split('|'):
            if len(normalize(alias))>=4: examples.append((normalize(alias),r.product_family_id,'catalog'))
    aliases=pd.read_csv(ROOT/'data/approved_hinglish_aliases.csv').fillna('')
    for _,r in aliases.iterrows():
        if r.product_family_id in allowed:examples.append((normalize(r.alias),r.product_family_id,'curated'))
    external=pd.read_csv(ROOT/'data/supplemental_whatsapp_orders_300.csv').fillna('')
    # Supervise only when the original source catalog identifies ONE compatible
    # product family and the message contains a recognizable, bounded alias.
    source_aliases={'SKU001':['parle g','parle-g','parleg'], 'SKU002':['hide seek','hide & seek'],
        'SKU003':['maggi','maggie','magi','megi'], 'SKU004':['surf excel','surf exel','surfexel','surf exl'],
        'SKU006':['fortune tel','fortune oil','fortun tel','fortune'],
        'SKU007':['fortune soy','fortune soya'], 'SKU008':['tata namak','tata namk','tata salt','tata solt'],
        'SKU009':['aashirvaad','ashirwad','aashirwad'], 'SKU014':['colgate paste','colgate'],
        'SKU016':['good day','goodday'], 'SKU018':['lays','lay s']}
    for _,r in external.iterrows():
        message=normalize(r.raw_message)
        try: skus={str(it.get('sku')) for it in json.loads(r.source_ground_truth_json)}
        except (ValueError,TypeError):continue
        for sku in skus:
            family=SOURCE_MAP.get(sku)
            if family not in allowed:continue
            for alias in source_aliases.get(sku,[]):
                a=normalize(alias)
                if re.search(r'(?<!\w)'+re.escape(a)+r'(?!\w)',message):
                    examples.append((a,family,'whatsapp'))
    unique={(a,f):src for a,f,src in examples if a}
    return [(a,f,s) for (a,f),s in unique.items()]

def train():
    examples=build_examples()
    X=[a for a,f,s in examples];y=[f for a,f,s in examples]
    model=make_pipeline(TfidfVectorizer(analyzer='char_wb',ngram_range=(2,5),lowercase=True),
                        LogisticRegression(max_iter=1500,class_weight='balanced'))
    model.fit(X,y)
    out=ROOT/'models'/'whatsapp_family_classifier.joblib';out.parent.mkdir(exist_ok=True)
    joblib.dump(model,out)
    counts=pd.Series([s for a,f,s in examples]).value_counts().to_dict()
    report={'unique_training_phrases':len(examples),'sources':counts,'classes':sorted(set(y)),
        'method':'Character n-gram TF-IDF + logistic regression, trained on catalog aliases and conservatively compatible WhatsApp variants',
        'limitations':'Synthetic data, incompatible labels excluded, no independent held-out accuracy claim. Predictions require high confidence and catalog verification.'}
    (ROOT/'models'/'whatsapp_training_report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':train()
