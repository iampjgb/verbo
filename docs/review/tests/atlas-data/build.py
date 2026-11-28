import json,csv,sys,urllib.request,os
OB='/tmp/obgeo/data/'
A={};[A.__setitem__(j['id'],j) for j in map(json.loads,open(OB+'ancient.jsonl'))]
M={};[M.__setitem__(j['id'],j) for j in map(json.loads,open(OB+'modern.jsonl'))]
wd={}
for r in csv.DictReader(open('/tmp/pwd/data/wd2pid.csv')):
    wd.setdefault(r['item'].rsplit('/',1)[-1],[]).append(r['itemPID'])
want={'antS':'ae41ab4','sel':'a6d306d','sal':'afa863b','pap':'a314765','per':'aff04b8','att':'ac744c1','antP':'a6c704a','ico':'ae425aa','lys':'af0719d','der':'aa401a9'}
out={}
def pfetch(pid):
    p='/'.join(pid[:4])
    u=f'https://raw.githubusercontent.com/isawnyu/pleiades.datasets/main/data/json/{p}/{pid}.json'
    try: return json.load(urllib.request.urlopen(u,timeout=30))
    except Exception as e: return None
for k,aid in want.items():
    a=A[aid];ex=json.loads(a['extra']);assoc=ex.get('associations',[])
    ids=[]
    for x in assoc:
        m=M.get(x['modern_id'],{});ll=m.get('lonlat','')
        q=(m.get('coordinates_source') or {}).get('id') if (m.get('coordinates_source') or {}).get('type')=='wikidata' else None
        ids.append({'name':x['name'],'score':x['score'],'lonlat':[float(v) for v in ll.split(',')] if ll else None,'wd':q})
    awd=(a['linked_data'].get('s7cc8b2') or {}).get('id')
    pids=[]
    for q in [awd]+[i['wd'] for i in ids]:
        if q and q in wd: pids+=wd[q]
    pids=list(dict.fromkeys({'sel':['658483'],'att':['638778'],'ico':['648647']}.get(k,[])+pids))
    pl=None
    for pid in pids:
        j=pfetch(pid)
        if j: pl=j;break
    rec={'ob':{'id':aid,'name':a['friendly_id'],'slug':a['url_slug'],'ids':ids},'wd':awd}
    if pl:
        names=[n.get('attested') or n.get('romanized') for n in pl.get('names',[])]
        locs=pl.get('locations',[])
        acc=[l.get('accuracy_value') for l in locs if l.get('accuracy_value')]
        tp=[]
        for l in locs+pl.get('names',[]):
            for t in l.get('attestations',[]): tp.append(t.get('timePeriod'))
        rec['pl']={'id':pl['id'],'title':pl['title'],'names':[n for n in names if n][:4],'repr':pl.get('reprPoint'),'acc':min(acc) if acc else None,'periods':sorted(set(x for x in tp if x)),'loc_precision':sorted(set(l.get('locationType',[''])[0] if isinstance(l.get('locationType'),list) and l.get('locationType') else str(l.get('precision','')) for l in locs))}
    out[k]=rec
    print(k,a['friendly_id'],awd,pids,(rec.get('pl')or{}).get('title'),[(i['name'],i['score']) for i in ids])
json.dump(out,open('/home/claude/atlasdata/matched.json','w'),ensure_ascii=False,indent=1)
