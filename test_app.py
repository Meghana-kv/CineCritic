import pytest
import app as a
@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(a,'DB',str(tmp_path/'test.db'));monkeypatch.setattr(a,'predict',lambda text:'dies' in text)
    monkeypatch.setattr(a,'catalog',lambda:[dict(id=1,title='Interstellar',year=2014,language='English',genre='Sci-fi',poster='test.jpg',description='Test',director='Test',cast='Test')]);return a.app.test_client()
def data(**kw):return dict(movie='Interstellar',name='Viewer',rating='5',body='Great movie')|kw
def test_home(client):assert client.get('/').status_code==200
def test_review(client):assert b'Great movie' in client.post('/review',data=data(),follow_redirects=True).data
def test_spoiler(client):assert b'<details class="warning">' in client.post('/review',data=data(body='Hero dies'),follow_redirects=True).data
def test_manual(client):assert b'<details class="warning">' in client.post('/review',data=data(manual='yes'),follow_redirects=True).data
@pytest.mark.parametrize('change',[{'rating':'0'},{'rating':'6'},{'rating':'abc'},{'movie':'bad'},{'body':''},{'name':''},{'body':'x'*2001}])
def test_invalid(client,change):assert client.post('/review',data=data(**change)).status_code==400
def test_health(client):assert client.get('/health').json['status']=='ok'
def test_metrics(client):assert 'average_ms' in client.get('/metrics').json
def test_rating(client):
    client.post('/review',data=data());client.post('/review',data=data(rating='3'));assert b'8.0/10' in client.get('/movie/1').data
def test_like(client):
    assert b'Liked' in client.post('/like/1',follow_redirects=True).data;assert b'Like movie' in client.post('/like/1',follow_redirects=True).data
def test_missing(client):assert client.get('/movie/999').status_code==404
