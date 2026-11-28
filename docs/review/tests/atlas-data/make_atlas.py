import json
m=json.load(open('matched.json'))
PER=[("archaic","Archaic"),("classical","Classical"),("hellenistic-republican","Hellenistic"),("roman","Roman"),("late-antique","Late Antique")]
places={}
for k,v in m.items():
    pl=v.get('pl') or {}
    ids=sorted(v['ob']['ids'],key=lambda x:-x['score'])
    tot=sum(max(i['score'],0) for i in ids) or 1
    sites=[{"n":i['name'],"s":i['score'],"ll":i['lonlat']} for i in ids]
    known=len(ids)==1 and ids[0]['score']>=1000
    places[k]={
      "ob":{"id":v['ob']['id'],"slug":v['ob']['slug']},
      "sites":sites,
      "cert":"known" if known else "approx",
      "pl":{"id":pl.get('id'),"title":pl.get('title'),"names":pl.get('names',[])[:3],"acc":pl.get('acc'),
            "periods":[lab for key,lab in PER if key in pl.get('periods',[])],"ll":[round(x,4) for x in pl['repr']] if pl.get('repr') else None} if pl else None,
      "wd":v['wd']}
J={"paul1":{"title":"Paul's first journey","refs":"Acts 13–14","when":"about AD 46–48",
 "stops":[
 {"p":"antS","ref":"Acts 13:1-3","note":"The church set apart Barnabas and Saul for the work. Believers were first called Christians here (Acts 11:26)."},
 {"p":"sel","ref":"Acts 13:4","seg":13,"note":"Antioch's harbour on the coast. From here they sailed for Cyprus."},
 {"p":"sal","ref":"Acts 13:5","seg":5,"sea":1,"note":"The main city on the east coast of Cyprus, Barnabas's home island (Acts 4:36). They preached in the synagogues. John Mark helped them."},
 {"p":"pap","ref":"Acts 13:6-12","seg":7,"note":"Seat of the Roman governor, Sergius Paulus, who believed. From here on, Luke calls Saul by the name Paul."},
 {"p":"per","ref":"Acts 13:13","seg":4,"sea":1,"note":"John Mark left them here and went back to Jerusalem."},
 {"p":"antP","ref":"Acts 13:14-52","seg":9,"note":"Paul's first recorded sermon. Many Gentiles believed. Opposition drove them out of the region."},
 {"p":"ico","ref":"Acts 14:1-6","seg":6,"note":"A great number of Jews and Greeks believed. When a plot to stone them formed, they fled."},
 {"p":"lys","ref":"Acts 14:8-20","seg":11,"note":"Paul healed a man lame from birth. The crowd called them gods. Later Paul was stoned and left for dead."},
 {"p":"der","ref":"Acts 14:20-21","seg":2,"note":"They made many disciples. Then they turned back the way they came."},
 {"p":"lys","ref":"Acts 14:21-22","seg":3,"ret":1,"note":"They strengthened the disciples and urged them to remain true to the faith."},
 {"p":"ico","ref":"Acts 14:21-22","seg":0,"ret":1,"note":"They encouraged the believers to keep the faith through hardship."},
 {"p":"antP","ref":"Acts 14:21-23","seg":1,"ret":1,"note":"They appointed elders in each church, with prayer and fasting."},
 {"p":"per","ref":"Acts 14:24-25","seg":10,"ret":1,"note":"This time they preached the word in Perga."},
 {"p":"att","ref":"Acts 14:25-26","seg":8,"ret":1,"note":"The port where they boarded a ship for Syria."},
 {"p":"antS","ref":"Acts 14:26-28","seg":12,"sea":1,"ret":1,"trim":1,"note":"They gathered the church and reported how God had opened a door of faith to the Gentiles."}],
 "labels":{"antS":["Antioch","in Syria","above"],"sel":["Seleucia","","endb"],"sal":["Salamis","","start"],"pap":["Paphos","","below"],"per":["Perga","","above"],"att":["Attalia","","endb"],"antP":["Antioch","in Pisidia","above"],"ico":["Iconium","","start"],"lys":["Lystra","","end"],"der":["Derbe","","start"]},
 "regions":[[33.15,35.1,"CYPRUS"],[31.75,37.02,"PAMPHYLIA"],[32.3,38.85,"GALATIA"],[33.05,38.2,"LYCAONIA"],[35.75,37.35,"CILICIA"],[36.75,35.55,"SYRIA"]],
 "seas":[[30.9,35.45,"THE GREAT SEA"]],
 "relief":{"src":"bible/fact/relief_paul1.jpg","box":[22,29,44,43]}}}
SRC=[
 {"n":"OpenBible.info Bible Geocoding","u":"https://www.openbible.info/geo/","lic":"CC BY 4.0","use":"Which modern site matches each place, and how confident scholars are"},
 {"n":"Pleiades gazetteer of ancient places","u":"https://pleiades.stoa.org/","lic":"CC BY 3.0","use":"Ancient names, periods and location accuracy"},
 {"n":"Theographic Bible Metadata","u":"https://github.com/robertrouse/theographic-bible-metadata","lic":"CC BY-SA 4.0","use":"Journey routes and Bible place data"},
 {"n":"Natural Earth","u":"https://www.naturalearthdata.com/","lic":"Public domain","use":"Coastlines and rivers"},
 {"n":"Shaded relief by Tom Patterson, shadedrelief.com","u":"https://www.shadedrelief.com/","lic":"Public domain","use":"Terrain shading"}]
json.dump({"v":1,"places":places,"journeys":J,"sources":SRC},open('/home/claude/verbo/bible/fact/atlas.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(open('/home/claude/verbo/bible/fact/atlas.json').read()))
print(json.dumps(places['der'],ensure_ascii=False))
