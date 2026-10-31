import sys,re,os,glob
sys.path.insert(0,sys.argv[1])
from tr import T
from bs4 import BeautifulSoup, Comment
os.chdir('/home/claude/site')
pages=['index.html','que-es-esto.html','bitacora.html','imaginario.html','kit.html']+sorted(f for f in glob.glob('escritos/*.html') if not f.endswith('index.html'))
def url(p):
    if p=='index.html': return '/'
    return '/'+p[:-5]
SW='display: inline-flex; align-items: center; min-height: 32px; padding: 0 10px; border: 1px solid rgba(252,251,248,0.35); border-radius: 999px; font-size: 12px; letter-spacing: 0.16em'
def add_switch(html,target,label,lang):
    a=f'<a href="{target}" hreflang="{lang}" lang="{lang}" style="{SW}">{label}</a>\n'
    i=html.find('</nav>\n</header>')
    if i<0: i=html.find('</nav>')
    return html[:i]+a+html[i:]
for p in pages:
    src=open(p).read()
    # strip old switch if re-run
    src=re.sub(r'<a href="[^"]*" hreflang="en" lang="en"[^>]*>EN</a>\n','',src)
    u=url(p); en_u='/en/' if u=='/' else '/en'+u
    es=add_switch(src,en_u,'EN','en')
    es=es.replace('<link rel="icon"',f'<link rel="alternate" hreflang="en" href="{en_u}">\n<link rel="icon"',1) if 'hreflang="en" href=' not in es else es
    open(p,'w').write(es)
    soup=BeautifulSoup(src,'html.parser')
    for el in soup.find_all(string=True):
        if isinstance(el,Comment) or el.parent.name in ('script','style'): continue
        s=str(el); k=s.strip()
        if k in T and T[k]!=k:
            el.replace_with(s.replace(k,T[k]))
    for tag in soup.find_all(True):
        for at in ('alt','placeholder','aria-label','title'):
            v=tag.get(at)
            if v and v.strip() in T: tag[at]=T[v.strip()]
        if tag.name=='meta' and tag.get('name')=='description' and tag.get('content') in T: tag['content']=T[tag['content']]
        if tag.name=='html': tag['lang']='en'
        if tag.name=='a' and tag.get('href','').startswith('/') and not tag['href'].startswith('//'):
            h=tag['href']
            if not re.search(r'\.(css|png|jpg|webp|js)$',h) and not h.startswith('/en'):
                tag['href']='/en/' if h=='/' else ('/en'+h)
    out=str(soup)
    out=re.sub(r'"a": "([^"]+)"',lambda m:'"a": "'+T.get(m.group(1),m.group(1)).replace('"','\\"')+'"',out)
    out=out.replace('src="images/','src="/images/').replace("'images/","'/images/").replace('"images/','"/images/')
    out=out.replace("location.href='/kit'","location.href='/en/kit'")
    out=out.replace('¡<em','<em')
    out=add_switch(out,u,'ES','es')
    out=out.replace('<link rel="icon"',f'<link rel="alternate" hreflang="es" href="{u}">\n<link rel="icon"',1)
    dest='en/index.html' if p=='index.html' else 'en/'+p
    os.makedirs(os.path.dirname(dest),exist_ok=True)
    open(dest,'w').write(out)
    print('ok',dest)
