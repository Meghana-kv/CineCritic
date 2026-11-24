import pytest
import app as a
@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(a,'DB',str(tmp_path/'test.db')); monkeypatch.setattr(a,'predict',lambda text:'dies' in text); return a.app.test_client()
def data(**kw): return dict(movie='Interstellar',name='Viewer',rating='5',body='Great movie',**{}) | kw
def test_home(client): assert client.get('/').status_code==200
def test_review(client):
    assert client.post('/review',data=data()).status_code==302
    assert b'Great movie' in client.get('/').data
def test_spoiler(client):
    client.post('/review',data=data(body='Hero dies')); assert b'<details class="warning">' in client.get('/').data
def test_manual(client):
    client.post('/review',data=data(manual='yes')); assert b'<details class="warning">' in client.get('/').data
@pytest.mark.parametrize('change',[{'rating':'0'},{'rating':'6'},{'rating':'abc'},{'movie':'bad'},{'body':''},{'name':''},{'body':'x'*2001}])
def test_invalid(client,change): assert client.post('/review',data=data(**change)).status_code==400
def test_health(client): assert client.get('/health').json['status']=='ok'
def test_metrics(client): assert 'average_ms' in client.get('/metrics').json
