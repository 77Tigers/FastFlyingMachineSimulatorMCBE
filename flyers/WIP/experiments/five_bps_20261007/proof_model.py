"""Finite tagged-piston geometry abstraction for the two rigid carriers.
Orders over-approximate actual chunk schedules; no simulator changes.
State: (tick parity, bank, x-relative-to-own-ready-position, own state, moving owner).
"""
from itertools import permutations
from collections import deque

def step(q,good=False,fire=True):
 parity,bank,d,s,m=q
 a,b=(0,0) if parity==0 else (1,0)
 shift=[a,b];start=parity;finish=1-start
 x=5+shift[bank]+d
 powered=(bank==start and s==0 and m==-1 and d==0)
 out=set()
 for order in permutations('FSU'):
  if good:
   if order.index('F')>order.index('S'):continue
   # Entire finishing Z bank runs before the starting Z bank.
   if bank==finish and order.index('U')>order.index('S'):continue
   if bank==start and order.index('U')<order.index('F'):continue
  for choose_fire in ([False,True] if fire and powered else [False]):
   xx,ss,mm=x,s,m
   for e in order:
    if e=='F':
     if mm==finish:mm=-1
     if s==1:ss=2
    elif e=='U':
     if s==2:ss=3
     if s==3:ss=0
    else:
     if choose_fire:ss=1
     elif ss==0 and mm==-1:
      if bank==0:
       contacts=({3+a,4+a,5+a} if start==0 else {4+b,5+b})
      else:
       contacts=({3+a,4+a} if start==0 else {3+b,4+b,5+b})
      if xx in contacts:xx+=1;mm=start
   post=shift[bank]+int(start==bank)
   out.add((1-parity,bank,xx-(5+post),ss,mm))
 return out

def reachable():
 initial={(0,0,0,0,-1),(0,1,0,3,-1)}
 seen=set(initial);todo=deque(initial)
 while todo:
  q=todo.popleft()
  for r in step(q):
   if r not in seen:
    assert -3<=r[2]<=0,(q,r)
    seen.add(r);todo.append(r)
 return seen
if __name__=='__main__':
 qs=reachable();print('reachable tagged states',len(qs));print(sorted(qs))
 # A reset block must recover every piston that is not chosen to fire in it.
 for length in range(1,11):
  bad=[]
  for q in qs:
   current={q}
   for _ in range(length):current={r for p in current for r in step(p,good=True,fire=False)}
   if any(r[2]!=0 or r[3]!=0 for r in current):bad.append((q,current))
  print('good ticks',length,'non-reset initial states',len(bad))
  if not bad:break

