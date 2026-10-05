"""Negotiated six-body routing: rip up optional routes, retain mandatory ports.

This replaces the previous greedy 'freeze every connection' strategy.
Body geometry conflicts may be explored internally, but only conflict-free,
connected assemblies within the cell cap are returned to the real simulator.
"""
import heapq,collections,time
import six
D=six.D

def components(cells):
 left=set(cells);groups=[]
 while left:
  p=min(left);left.remove(p);part={p};todo=[p]
  while todo:
   for d in D:
    q=six.add(todo[-1],d)
    if q in left:left.remove(q);part.add(q);todo.append(q);break
   else:todo.pop()
  groups.append(part)
 return groups

def bridge(cells,blocked,weights,bounds,rng,deadline):
 groups=components(cells)
 if len(groups)==1:return set()
 heap=[];dist={};owner={};prev={}
 for j,part in enumerate(groups):
  for p in sorted(part):dist[p]=0;owner[p]=j;prev[p]=None;heapq.heappush(heap,(0,rng.random(),p))
 best=1e30;meeting=None;visits=0
 while heap:
  cost,_,p=heapq.heappop(heap)
  if cost!=dist[p]:continue
  if cost>best:break
  visits+=1
  if visits%512==0 and time.monotonic()>deadline:return None
  for d in D:
   q=six.add(p,d)
   if not all(bounds[2*k]<=q[k]<=bounds[2*k+1] for k in range(3)):continue
   if q not in cells and q in blocked:continue
   if q in owner and owner[q]!=owner[p]:
    total=cost+dist[q]
    if total<best:best=total;meeting=(p,q)
   else:
    nc=cost+(0 if q in cells else 1+weights.get(q,0))
    if nc<dist.get(q,1e30):dist[q]=nc;owner[q]=owner[p];prev[q]=p;heapq.heappush(heap,(nc,rng.random(),q))
 if meeting is None:return None
 path=set()
 for p in meeting:
  while p is not None:
   if p not in cells:path.add(p)
   p=prev[p]
 return path

SHIFTS={(i,j):{six.disp(t,j)-six.disp(t,i)+b-a for t in range(3)
 for a in ((0,1) if t%3==i%3 else (0,))
 for b in ((0,1) if t%3==j%3 else (0,))} for i in range(6) for j in range(6) if i!=j}

def obstacles(cells,j,i):
 result=set()
 for p in cells:
  for dx in SHIFTS[i,j]:
   q=six.shift(p,dx);result.add(q)
   if six.K[i]==six.K[j]:result.update(six.add(q,d) for d in D)
 return result

def route(mandatory,fixed,bounds,cap,rng,deadline,report):
 must=[set(s) for s in mandatory];blocked=[set(fixed[i]) for i in range(6)]
 for i in range(6):
  for j in range(6):
   if i!=j:blocked[i].update(obstacles(must[j],j,i))
 routes=[set(s) for s in must];history=[collections.Counter() for _ in range(6)]
 best=None
 for iteration in range(40):
  if time.monotonic()>deadline:break
  for i in rng.sample(range(6),6):
   weights=collections.Counter({p:v*.4 for p,v in history[i].items()})
   for j in range(6):
    if i!=j:
     for p in obstacles(routes[j]-must[j],j,i):weights[p]+=2+iteration*.5
   candidate=set(must[i])
   while len(components(candidate))>1:
    path=bridge(candidate,blocked[i],weights,bounds,rng,deadline)
    if path is None or len(candidate)+len(path)>cap:break
    candidate.update(path)
   if len(components(candidate))==1:routes[i]=candidate
  conflicts=[]
  for i in range(6):
   for j in range(i):
    hit=routes[i]&obstacles(routes[j],j,i)
    if hit:
     conflicts.append((i,j,len(hit)))
     history[i].update(hit)
     history[j].update(routes[j]&obstacles(routes[i],i,j))
  missing=sum(len(components(s))-1 for s in routes)
  score=(missing,sum(c for i,j,c in conflicts),max(map(len,routes)),sum(map(len,routes)))
  if best is None or score<best:best=score;report['best']=score;report['iteration']=iteration
  if not missing and not conflicts:
   report['counts']=list(map(len,routes));return routes
  # A stalled body gets a fresh chance after optional neighbouring routes are
  # removed; required timing/power ports are never removed.
  if iteration%8==7:
   j=rng.randrange(6);routes[j]=set(must[j])
 return None
