"""Exact optimistic node-count Steiner minimum for a small set of contact groups."""
import heapq

def connected_glue_minimum(cells,groups):
 cells=sorted(cells);index={p:i for i,p in enumerate(cells)};n=len(cells);groups=[set(g)&index.keys() for g in groups]
 if not groups:return 0
 if not n or any(not g for g in groups):return None
 neighbors=[]
 for p in cells:
  ns=[]
  for axis in range(3):
   for sign in [-1,1]:
    q=list(p);q[axis]+=sign;j=index.get(tuple(q))
    if j is not None:ns.append(j)
  neighbors.append(ns)
 inf=10**7;dp=[[inf]*n for _ in range(1<<len(groups))]
 for k,g in enumerate(groups):
  for p in g:dp[1<<k][index[p]]=1
 for mask in range(1,len(dp)):
  row=dp[mask];sub=(mask-1)&mask
  while sub:
   other=mask^sub
   if sub<other:
    left,right=dp[sub],dp[other]
    for v in range(n):row[v]=min(row[v],left[v]+right[v]-1)
   sub=(sub-1)&mask
  heap=[(cost,v) for v,cost in enumerate(row) if cost<inf];heapq.heapify(heap)
  while heap:
   cost,v=heapq.heappop(heap)
   if cost!=row[v]:continue
   for w in neighbors[v]:
    if cost+1<row[w]:row[w]=cost+1;heapq.heappush(heap,(cost+1,w))
 result=min(dp[-1]);return result if result<inf else None
