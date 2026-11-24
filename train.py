import argparse, pandas as pd, joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('dataset',nargs='?',default='starter.csv'); p.add_argument('--text',default='text'); p.add_argument('--label',default='spoiler'); a=p.parse_args()
d=pd.read_csv(a.dataset)[[a.text,a.label]].dropna(); d.columns=['text','label']; d=d.drop_duplicates('text'); d.label=d.label.astype(str).str.lower().map({'true':1,'false':0,'1':1,'0':0}); d=d.dropna(); x,y=d.text,d.label.astype(int)
x1,x2,y1,y2=train_test_split(x,y,test_size=.25,random_state=42,stratify=y)
m=make_pipeline(TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,max_features=50000),LogisticRegression(class_weight='balanced',max_iter=1000)); m.fit(x1,y1); pred=m.predict(x2); print('Dataset:',a.dataset,'Train:',len(x1),'Test:',len(x2)); print(classification_report(y2,pred,zero_division=0)); print('Spoiler F1:',f1_score(y2,pred)); joblib.dump(m,Path(__file__).with_name('model.joblib'))
