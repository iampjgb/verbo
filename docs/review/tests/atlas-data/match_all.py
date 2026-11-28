import json,csv,math,urllib.request,re
B=json.load(open('journeys_built.json'))
OB='/tmp/obgeo/data/'
A=[json.loads(l) for l in open(OB+'ancient.jsonl')]
M={};[M.__setitem__(j['id'],j) for j in map(json.loads,open(OB+'modern.jsonl'))]
wd={}
for r in csv.DictReader(open('/tmp/pwd/data/wd2pid.csv')): wd.setdefault(r['item'].rsplit('/',1)[-1],[]).append(r['itemPID'])
ALIAS={'Ur of the Chaldees':'Ur','Red Sea crossing':'Red Sea','Kadesh-barnea':'Kadesh-barnea','Appii forum':'Forum of Appius','On':'Heliopolis','Malta':'Malta','Mount Sinai':'Mount Sinai','Moab':'Moab','Fair Havens':'Fair Havens','Three Taverns':'Three Taverns','Rameses':'Rameses','Seleucia':'Seleucia'}
NOOB={'Aleppo','Mari','Pelusium'}  # not places named in the Bible
PL_OVR={'seleucia':'658483','attalia':'638778','iconium':'648647','antiochs':'658381','antiochp':'609307'}
def dd(a,b): return math.hypot((a[0]-b[0])*math.cos(math.radians(35)),a[1]-b[1])
def pfetch(pid):
    u=f'https://raw.githubusercontent.com/isawnyu/pleiades.datasets/main/data/json/{"/".join(pid[:4])}/{pid}.json'
    try: return json.load(urllib.request.urlopen(u,timeout=30))
    except Exception: return None
PER=[("archaic","Archaic"),("classical","Classical"),("hellenistic-republican","Hellenistic"),("roman","Roman"),("late-antique","Late Antique")]
out={}
for k,(nm,ll) in B['places'].items():
    base=nm.split(' ')[0] if nm.startswith('Antioch') else nm
    q=ALIAS.get(base,base);rec={}
    if base not in NOOB:
        cands=[a for a in A if re.sub(r' \d+$','',a['friendly_id'])==q]
        best=None
        for a in cands:
            ex=json.loads(a['extra']);ids=sorted(ex.get('associations',[]),key=lambda x:-x['score'])
            if not ids: continue
            m=M.get(ids[0]['modern_id'],{});l=m.get('lonlat')
            dist=dd([float(v) for v in l.split(',')],ll) if l else 9
            if any(a['id']==x for x in []):pass
            if best is None or dist<best[0]: best=(dist,a,ids)
        if best and best[0]<1.5:
            a,ids=best[1],best[2]
            sites=[]
            for x in ids[:4]:
                m=M.get(x['modern_id'],{});l=m.get('lonlat')
                sites.append({'n':x['name'],'s':x['score'],'ll':[round(float(v),4) for v in l.split(',')] if l else None})
            rec['ob']={'id':a['id'],'slug':a['url_slug']};rec['sites']=sites
            top=sites[0]['s'] if sites else 0
            rec['cert']='known' if top>=900 and (len(sites)==1 or sites[1]['s']<100) else 'approx'
            rec['wd']=(a['linked_data'].get('s7cc8b2') or {}).get('id')
            rec['_wds']=[ (M.get(x['modern_id'],{}).get('coordinates_source') or {}).get('id') for x in ids[:1]]
        else: print('NO OB',k,nm,best and round(best[0],2))
    pids=[PL_OVR[k]] if k in PL_OVR else []
    for qid in [rec.get('wd')]+rec.pop('_wds',[]):
        if qid and qid in wd: pids+=wd[qid]
    pl=None
    for pid in dict.fromkeys(pids):
        pl=pfetch(pid)
        if pl and pl.get('reprPoint') and dd(pl['reprPoint'],ll)<1.5: break
        pl=None
    if pl:
        tp=set()
        for l in pl.get('locations',[])+pl.get('names',[]):
            for t in l.get('attestations',[]): tp.add(t.get('timePeriod'))
        names=[n.get('attested') or n.get('romanized') for n in pl.get('names',[])]
        rec['pl']={'id':pl['id'],'title':pl['title'],'names':[n for n in names if n][:3],'periods':[lab for key,lab in PER if key in tp]}
    if 'cert' not in rec: rec['cert']='approx' if base in NOOB or 'ob' not in rec else rec.get('cert')
    out[k]=rec
    print(f"{k:12} {nm:20} OB:{rec.get('ob',{}).get('slug','-'):18} {rec['cert']:7} PL:{(rec.get('pl') or {}).get('title','-')}  sites:{[(s['n'],s['s']) for s in rec.get('sites',[])][:3]}")
json.dump(out,open('places_matched.json','w'),ensure_ascii=False)
