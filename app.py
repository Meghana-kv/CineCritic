from flask import Flask, render_template, request, redirect, jsonify, g, abort, session, url_for
import sqlite3,time,os,json,secrets
from pathlib import Path
from classifier import predict
app=Flask(__name__)
ROOT=Path(__file__).resolve().parent
secret_file=ROOT/'.cine_secret'
if not secret_file.exists():secret_file.write_text(secrets.token_hex(32),encoding='utf-8')
app.secret_key=os.environ.get('CINE_SECRET') or secret_file.read_text(encoding='utf-8')
DB=os.environ.get('CINE_DB',str(ROOT/'cinecritic.db'))
metrics={'requests':0,'errors':0,'total_ms':0}
def catalog():
    p=ROOT/'movies.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else []
def db():
    c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,movie TEXT,name TEXT,rating INTEGER,body TEXT,spoiler INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS likes(movie TEXT,viewer TEXT,PRIMARY KEY(movie,viewer))');return c
@app.before_request
def start():
    g.start=time.perf_counter()
    if 'viewer' not in session:session['viewer']=secrets.token_hex(16)
@app.after_request
def finish(response):
    metrics['requests']+=1;metrics['errors']+=int(response.status_code>=500);metrics['total_ms']+=(time.perf_counter()-g.start)*1000;return response
def enrich(m,c):
    r=c.execute('SELECT AVG(rating)*2 AS score,COUNT(*) AS votes FROM reviews WHERE movie=?',(m['title'],)).fetchone()
    likes=c.execute('SELECT COUNT(*) FROM likes WHERE movie=?',(m['title'],)).fetchone()[0]
    liked=c.execute('SELECT 1 FROM likes WHERE movie=? AND viewer=?',(m['title'],session['viewer'])).fetchone() is not None
    return dict(m,score=r['score'],votes=r['votes'],likes=likes,liked=liked)
def find(mid):
    return next((m for m in catalog() if m['id']==mid),None) or abort(404)
@app.get('/')
def home():
    with db() as c:
        movies=[enrich(m,c) for m in catalog()];reviews=c.execute('SELECT * FROM reviews ORDER BY id DESC').fetchall()
    return render_template('index.html',movies=movies,reviews=reviews,metrics=metrics)
@app.get('/movie/<int:mid>')
def movie(mid):
    with db() as c:
        m=enrich(find(mid),c);reviews=c.execute('SELECT * FROM reviews WHERE movie=? ORDER BY id DESC',(m['title'],)).fetchall()
    return render_template('movie.html',m=m,reviews=reviews)
@app.post('/review')
def review():
    title=request.form.get('movie');name=request.form.get('name','').strip();body=request.form.get('body','').strip()
    try:rating=int(request.form.get('rating',''))
    except ValueError:return 'Invalid rating',400
    m=next((m for m in catalog() if m['title']==title),None)
    if not m or not 1<=rating<=5 or not 1<=len(name)<=60 or not 1<=len(body)<=2000:return 'Invalid review',400
    with db() as c:c.execute('INSERT INTO reviews(movie,name,rating,body,spoiler) VALUES(?,?,?,?,?)',(title,name,rating,body,int(predict(body) or request.form.get('manual')=='yes')))
    return redirect(url_for('movie',mid=m['id']))
@app.post('/like/<int:mid>')
def like(mid):
    m=find(mid)
    with db() as c:
        if c.execute('SELECT 1 FROM likes WHERE movie=? AND viewer=?',(m['title'],session['viewer'])).fetchone():c.execute('DELETE FROM likes WHERE movie=? AND viewer=?',(m['title'],session['viewer']))
        else:c.execute('INSERT INTO likes VALUES(?,?)',(m['title'],session['viewer']))
    return redirect(url_for('movie',mid=mid))
@app.get('/health')
def health():return jsonify(status='ok')
@app.get('/metrics')
def monitor():return jsonify(**metrics,average_ms=metrics['total_ms']/max(1,metrics['requests']))
if __name__=='__main__':app.run(port=5002)
