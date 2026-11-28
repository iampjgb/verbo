import json,math
J={j['id']:j for j in json.load(open('/home/claude/verbo/bible/fact/journeys.json'))}
def d(a,b): return math.hypot((a[0]-b[0])*math.cos(math.radians(36)),a[1]-b[1])
def graph(segs):
    # nodes: snapped endpoints; edges: seg index with direction
    nodes=[];E={}
    def nid(p):
        for i,q in enumerate(nodes):
            if d(p,q)<0.05: return i
        nodes.append(p);return len(nodes)-1
    for k,s in enumerate(segs):
        a,b=nid(s[0]),nid(s[-1])
        E.setdefault(a,[]).append((b,k,False));E.setdefault(b,[]).append((a,k,True))
    return nodes,E
def route(jid,stops):
    j=J[jid];segs=j['segs'];nodes,E=graph(segs)
    near=lambda p:min(range(len(nodes)),key=lambda i:d(nodes[i],p))
    out=[]
    for x,y in zip(stops,stops[1:]):
        a,b=near(x),near(y)
        da,db=d(nodes[a],x),d(nodes[b],y)
        # BFS fewest segments
        from collections import deque
        prev={a:None};q=deque([a])
        while q:
            u=q.popleft()
            if u==b:break
            for v,k,rev in E.get(u,[]):
                if v not in prev: prev[v]=(u,k,rev);q.append(v)
        if b not in prev: out.append((None,da,db));continue
        path=[];u=b
        while prev[u]: pu,k,rev=prev[u];s=segs[k][::-1] if rev else segs[k];path=s[1:]+path if path else s[:] ;u=pu
        # rebuild properly
        chain=[];u=b;parts=[]
        while prev[u]: pu,k,rev=prev[u];parts.append(segs[k][::-1] if rev else segs[k]);u=pu
        parts.reverse();pts=[]
        for s in parts: pts+= s if not pts else s[1:]
        out.append((pts,round(da,3),round(db,3)))
    return out
if __name__=='__main__':
    import sys
    j=J['paul2'];print([ (s['n'],s['x'],s['y']) for s in j['stops']])
