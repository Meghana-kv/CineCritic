from pathlib import Path
from functools import lru_cache
import joblib
@lru_cache(maxsize=1)
def model(): return joblib.load(Path(__file__).with_name('model.joblib'))
def predict(text): return bool(model().predict([text])[0])
