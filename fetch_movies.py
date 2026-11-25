import os,json,urllib.request,urllib.parse,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
KEY=os.environ.get('TMDB_API_KEY')
MOVIES=[('Interstellar',2014,'en'),('La La Land',2016,'en'),('Inception',2010,'en'),('Inside Out',2015,'en'),('The Grand Budapest Hotel',2014,'en'),('Arrival',2016,'en'),('They Call Him OG',2025,'te'),('Pushpa 2: The Rule',2024,'te'),('Kalki 2898 AD',2024,'te'),('Devara: Part 1',2024,'te'),('Thandel',2025,'te'),('Court: State vs. A Nobody',2025,'te'),('HIT: The Third Case',2025,'te'),('Kuberaa',2025,'te'),('Lucky Baskhar',2024,'te'),('Sankranthiki Vasthunam',2025,'te'),('Saiyaara',2025,'hi'),('Chhaava',2025,'hi'),('Stree 2',2024,'hi'),('Laapataa Ladies',2024,'hi'),('Sitaare Zameen Par',2025,'hi'),('Sky Force',2025,'hi'),('Kantara - A Legend: Chapter 1',2025,'kn'),('Bagheera',2024,'kn'),('UI',2024,'kn'),('Max',2024,'kn'),('Coolie',2025,'ta'),('Amaran',2024,'ta'),('Dragon',2025,'ta'),('Maharaja',2024,'ta'),('Good Bad Ugly',2025,'ta'),('Lokah Chapter 1: Chandra',2025,'ml'),('L2: Empuraan',2025,'ml'),('Manjummel Boys',2024,'ml'),('Premalu',2024,'ml'),('Aavesham',2024,'ml')]
LANG={'en':'English','te':'Telugu','hi':'Hindi','kn':'Kannada','ta':'Tamil','ml':'Malayalam'}
def download(url):
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"CineCritic/1.0"})
            with urllib.request.urlopen(req,timeout=45) as r: return r.read()
        except (OSError, TimeoutError) as e:
            if attempt==3: raise
            print("  Connection failed; retrying",attempt+1,"/ 3",flush=True)
            time.sleep(2**attempt)
def api(path,**params):
    params.update(api_key=KEY,language='en-US')
    return json.loads(download('https://api.themoviedb.org/3/'+path+'?'+urllib.parse.urlencode(params)))
def main():
    if not KEY: raise SystemExit('Set TMDB_API_KEY first.')
    dest=ROOT/'static'/'posters';dest.mkdir(parents=True,exist_ok=True)
    cache=ROOT/'movies.json'; old=json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else []; rows={m['title']:m for m in old}
    for title,year,lang in MOVIES:
        if title in rows and (ROOT/'static'/rows[title]['poster']).is_file(): continue
        try:
            results=api('search/movie',query=title,year=year)['results']; matches=[m for m in results if m.get('original_language')==lang and m.get('release_date','')[:4]==str(year)]
            if not matches: raise ValueError('No matching language/year')
            m=max(matches,key=lambda x:(x['title'].casefold()==title.casefold(),x.get('popularity',0))); d=api('movie/'+str(m['id']),append_to_response='credits'); path=d.get('poster_path'); poster='posters/'+str(m['id'])+'.jpg'
            if not path: raise ValueError('No poster')
            (ROOT/'static'/poster).write_bytes(download('https://image.tmdb.org/t/p/w500'+path))
            rows[title]=dict(title=title,id=m['id'],year=year,language=LANG[lang],genre=', '.join(x['name'] for x in d['genres']),description=d.get('overview') or 'Synopsis unavailable.',director=', '.join(x['name'] for x in d['credits']['crew'] if x['job']=='Director'),cast=', '.join(x['name'] for x in d['credits']['cast'][:4]),poster=poster)
            print('OK:',title,flush=True)
        except Exception as e: print('SKIPPED:',title,type(e).__name__,str(e).replace(KEY,'[REDACTED]'),flush=True)
        cache.write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2),encoding='utf-8');time.sleep(.15)
    print('Cached movies:',len(rows),'/',len(MOVIES))
if __name__=='__main__':main()
