# CineCritic P61
Academic prototype using Flask, SQLite and TF-IDF logistic regression instead of the prescribed stack. Python 3.10+.

Install: `python -m pip install -r requirements.txt`

Train: `python train.py` (40 original synthetic examples, smoke test only; not a public dataset or valid benchmark).
For a public labelled CSV, use `python train.py dataset.csv --text review_text --label is_spoiler` (adjust columns; labels must be 0/1 or true/false). Evaluate on held-out data; do not claim target achievement from starter data.

Run: `python app.py` and visit http://127.0.0.1:5002.
Tests: `python -m pytest --cov=app --cov-report=term-missing` (classifier mocked in web tests).
Spoilers are collapsed in HTML until clicked; not a security boundary. No authentication or moderator workflow yet. Metrics are process-local. Public dataset training, browser tests, CI/CD, external quality tools and full assignment evidence remain outstanding.
