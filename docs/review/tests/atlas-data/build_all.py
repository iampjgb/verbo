import json,math,csv,re,urllib.request,sys,os
sys.path.insert(0,'/home/claude/atlasdata')
from itin import IT,WHEN,REFS
from legs import route,d
JS={j['id']:j for j in json.load(open('/home/claude/verbo/bible/fact/journeys.json'))}
MAP=json.load(open('/home/claude/verbo/bible/fact/map.json'))
def inpoly(p,poly):
    x,y=p;c=False;n=len(poly)
    for i in range(n):
        x1,y1=poly[i];x2,y2=poly[i-1]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
LAND=[(min(q[0] for q in pl),max(q[0] for q in pl),min(q[1] for q in pl),max(q[1] for q in pl),pl) for pl in MAP['land']]
def onland(p): return any(a<=p[0]<=b and c<=p[1]<=e and inpoly(p,pl) for a,b,c,e,pl in LAND)
def dense(pts,step=0.05):
    out=[]
    for a,b in zip(pts,pts[1:]):
        n=max(1,int(d(a,b)/step))
        out+= [[a[0]+(b[0]-a[0])*t/n,a[1]+(b[1]-a[1])*t/n] for t in range(n)]
    return out+[pts[-1]]
def is_sea(pts):
    q=dense(pts)[1:-1] or pts
    return sum(not onland(p) for p in q)/len(q)>0.6
def key(name): return re.sub(r'[^a-z]','',name.lower())[:10]
def coords(jid,name):
    j=JS[jid];c=[s for s in j['stops']+j.get('minor',[]) if s['n']==name.split(' ')[0] or s['n']==name]
    if name=='Antioch S': c=[s for s in j['stops'] if s['n']=='Antioch' and s['x']>34]
    if name=='Antioch P': c=[s for s in j['stops'] if s['n']=='Antioch' and s['x']<34]
    if not c:
        for jj in JS.values():
            c=[s for s in jj['stops']+jj.get('minor',[]) if s['n']==name.split(' ')[0]]
            if name=='Antioch P': c=[s for s in jj['stops'] if s['n']=='Antioch' and s['x']<34]
            if c: break
    return [c[0]['x'],c[0]['y']]
def mi(pts):
    t=0
    for (a,b),(c,e) in zip(pts,pts[1:]):
        r=math.pi/180;h=math.sin((e-b)*r/2)**2+math.cos(b*r)*math.cos(e*r)*math.sin((c-a)*r/2)**2;t+=7918*math.asin(math.sqrt(h))
    return t
journeys={};places_needed={}
for jid,stops in IT.items():
    j=JS[jid];pts=[coords(jid,s[0]) for s in stops]
    legs=[None]
    if 'segs' in j:
        for (p,da,db),i in zip(route(jid,pts),range(1,len(pts))):
            if p is None or len(p)<2 or da>0.15 or db>0.15: print('  straight',jid,stops[i-1][0],'->',stops[i][0],da,db); p=[pts[i-1],pts[i]]
            if mi(p)>max(60,3.2*mi([pts[i-1],pts[i]])): print('  detour',jid,stops[i-1][0],'->',stops[i][0],round(mi(p))); p=[pts[i-1],pts[i]]
            legs.append(p)
    else:
        path=j['path'];last=0
        for i in range(1,len(pts)):
            k=min(range(last,len(path)),key=lambda t:d(path[t],pts[i]))
            if d(path[k],pts[i])>0.25: print('  off path',jid,stops[i][0],round(d(path[k],pts[i]),2))
            seg=path[last:k+1] if k>last else [path[last]]
            seg=[pts[i-1]]+seg[1:-1]+[pts[i]] if len(seg)>1 else [pts[i-1],pts[i]]
            legs.append(seg);last=k
    st=[];pl={}
    for (nm,ref,note,fl),p,lg in zip(stops,pts,legs):
        k=key(nm);pl[k]=[re.sub(r' [SP]$','',nm),{'Antioch S':'in Syria','Antioch P':'in Pisidia'}.get(nm,''),round(p[0],3),round(p[1],3)]
        o={'p':k,'ref':ref,'note':note}
        if 'way' in fl:o['way']=1
        if 'ret' in fl:o['ret']=1
        if lg:
            o['path']=[[round(a,3),round(b,3)] for a,b in lg];o['mi']=round(mi(lg))
            if is_sea(lg):o['sea']=1
        st.append(o);places_needed[k]=(nm,p)
    allp=[q for s in st for q in s.get('path',[])]+pts
    journeys[jid]={'title':j['title'],'refs':REFS[jid],'when':WHEN[jid],'miles':j.get('miles'),'note':j.get('note'),'debated':j.get('debated',False),'places':pl,'stops':st,
       'bbox':[min(q[0] for q in allp),min(q[1] for q in allp),max(q[0] for q in allp),max(q[1] for q in allp)]}
    print(jid,len(st),'stops',sum(1 for s in st if s.get('sea')),'sea legs', [s['mi'] for s in st if 'mi' in s][:20])
json.dump({'journeys':journeys,'places':{k:[v[0],v[1]] for k,v in places_needed.items()}},open('/home/claude/atlasdata/journeys_built.json','w'),ensure_ascii=False)
