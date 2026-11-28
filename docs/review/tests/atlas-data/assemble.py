import json
B=json.load(open('journeys_built.json'));P=json.load(open('places_matched.json'))
P['moab']={'cert':'region','ob':P['moab'].get('ob')}
for k in ('mari','aleppo','pelusium'): P[k]={'cert':'approx','way':1}
REL={'aegean':(19,29,44,43),'italy':(10,29,38,43),'levant':(30,26,39,35),'mesop':(31,28,49,40)}
RJ={'paul1':'aegean','paul2':'aegean','paul3':'aegean','paul4':'italy','exodus':'levant','egypt':'levant','ruth':'levant','bethlehem':'levant','abram1':'mesop','abram2':'mesop','jacob':'mesop','exile':'mesop'}
J=B['journeys']
for jid,j in J.items():
    r=RJ[jid];j['relief']={'src':f'bible/fact/relief_{r}.jpg','box':list(REL[r])}
    b=j['bbox'];x0,y0,x1,y1=REL[r];assert x0<b[0] and b[2]<x1 and y0<b[1] and b[3]<y1,(jid,b)
order=['abram1','abram2','jacob','exodus','ruth','exile','bethlehem','egypt','paul1','paul2','paul3','paul4']
SRC=[
 {"n":"OpenBible.info Bible Geocoding","u":"https://www.openbible.info/geo/","lic":"CC BY 4.0","use":"Which modern site matches each place, and how confident scholars are"},
 {"n":"Pleiades gazetteer of ancient places","u":"https://pleiades.stoa.org/","lic":"CC BY 3.0","use":"Ancient names and periods"},
 {"n":"Theographic Bible Metadata","u":"https://github.com/robertrouse/theographic-bible-metadata","lic":"CC BY-SA 4.0","use":"Journey routes and Bible place data"},
 {"n":"Natural Earth","u":"https://www.naturalearthdata.com/","lic":"Public domain","use":"Coastlines and rivers"},
 {"n":"Shaded relief by Tom Patterson, shadedrelief.com","u":"https://www.shadedrelief.com/","lic":"Public domain","use":"Terrain shading"}]
json.dump({'v':2,'order':order,'places':P,'journeys':J,'sources':SRC},open('/home/claude/verbo/bible/fact/atlas.json','w'),ensure_ascii=False,separators=(',',':'))
import os;print(os.path.getsize('/home/claude/verbo/bible/fact/atlas.json')//1024,'KB')
