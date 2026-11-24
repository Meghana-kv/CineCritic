from flask import Flask, render_template, request, redirect, jsonify, g
import sqlite3, time, os
from classifier import predict
app=Flask(__name__)
DB=os.environ.get('CINE_DB','cinecritic.db')
movies=[('Interstellar','Sci-fi','☾'),('La La Land','Romance','♫'),('Inception','Thriller','◇'),('Inside Out','Animation','♡'),('The Grand Budapest Hotel','Comedy','✿'),('Arrival','Sci-fi','✦')]
metrics={'requests':0,'errors':0,'total_ms':0}
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY, movie TEXT, name TEXT, rating INTEGER, body TEXT, spoiler INTEGER)'); return c
@app.before_request
def start(): g.start=time.perf_counter()
@app.after_request
def finish(response):
    metrics['requests']+=1; metrics['errors']+=int(response.status_code>=500); metrics['total_ms']+=(time.perf_counter()-g.start)*1000; return response
@app.get('/')
def home():
    with db() as c: reviews=c.execute('SELECT * FROM reviews ORDER BY id DESC').fetchall()
    return render_template('index.html',movies=movies,reviews=reviews,metrics=metrics)
@app.post('/review')
def review():
    movie=request.form.get('movie'); name=request.form.get('name','').strip(); body=request.form.get('body','').strip()
    try: rating=int(request.form.get('rating',''))
    except ValueError: return 'Invalid rating',400
    if movie not in [m[0] for m in movies] or not 1<=rating<=5 or not 1<=len(name)<=60 or not 1<=len(body)<=2000: return 'Invalid review',400
    with db() as c: c.execute('INSERT INTO reviews(movie,name,rating,body,spoiler) VALUES(?,?,?,?,?)',(movie,name,rating,body,int(predict(body) or request.form.get('manual')=='yes')))
    return redirect('/')
@app.get('/health')
def health(): return jsonify(status='ok')
@app.get('/metrics')
def monitor(): return jsonify(**metrics,average_ms=metrics['total_ms']/max(1,metrics['requests']))
if __name__=='__main__': app.run(port=5002)
