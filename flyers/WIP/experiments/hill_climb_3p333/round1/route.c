/* Minimum number of optional glue cells connecting required groups in a grid.
   Fixed face and pickup cells cost zero. An RB group contains its legal
   attachment neighbours, so the plate and connector can both pick up an RB. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static void recover(int n, int mask, int v, const int16_t *from, uint8_t *out) {
    out[v] = 1;
    int step = from[mask * n + v];
    if (step >= 0) {
        recover(n, mask, step, from, out);
    } else if (step < -1) {
        int part = -step - 1;
        recover(n, part, v, from, out);
        recover(n, mask ^ part, v, from, out);
    }
}

/* Every path from the root to this terminal group crosses the current
   boundary. Charging its unit cost once gives a lower bound even when the
   route branches, or several different pickups can serve one piston. */
static int cut_bound(int n, int groups, int cap, const int16_t *edges,
                     const uint8_t *cost, const int16_t *members, int reverse) {
    int root=0;
    while(!(members[root]&1) || cost[root]) ++root;
    uint8_t residual[2048], seen[2048];
    int queue[2048], boundary[2048], bound=0;
    memcpy(residual,cost,(size_t)n);
    for(int group=0;group<groups;++group) {
        int bit=1<<(reverse ? groups-1-group : group);
        for(;;) {
            int tail=0, nbound=0;
            memset(seen,0,n);
            for(int v=0;v<n;++v) if(members[v]&bit) {
                seen[v]=1;
                if(residual[v]) boundary[nbound++]=v;
                else queue[tail++]=v;
            }
            for(int i=0;i<tail && !seen[root];++i) for(int d=0;d<6;++d) {
                int w=edges[6*queue[i]+d];
                if(w<0 || seen[w]) continue;
                seen[w]=1;
                if(residual[w]) boundary[nbound++]=w;
                else queue[tail++]=w;
            }
            if(seen[root]) break;
            if(!nbound || ++bound>cap) return 0;
            for(int i=0;i<nbound;++i) residual[boundary[i]]=0;
        }
    }
    return 1;
}

int route(int n, int groups, int cap, const int16_t *edges, const uint8_t *cost,
          const int16_t *members, uint8_t *selected) {
    if(n<=0 || n>2048 || groups<=0 || groups>14 || cap<0) return 100;
    for (int reverse=0; reverse<2; ++reverse)
        if (!cut_bound(n,groups,cap,edges,cost,members,reverse)) return 100;
    int masks = 1 << groups;
    uint8_t *dist = malloc(n * masks);
    int16_t *from = malloc(n * masks * sizeof(int16_t));
    int *queue = malloc((n + 1) * sizeof(int));
    uint8_t *queued = calloc(n, 1);
    memset(dist, 100, n * masks);
    for (int mask = 1; mask < masks; ++mask) {
        uint8_t *row = dist + mask * n;
        int16_t *parent = from + mask * n;
        if (!(mask & (mask - 1))) {
            for (int v = 0; v < n; ++v) {
                if (members[v] & mask) {
                    row[v] = cost[v];
                    parent[v] = -1;
                }
            }
        }
        for (int part = (mask - 1) & mask; part; part = (part - 1) & mask) {
            int other = mask ^ part;
            if (other < part) continue;
            for (int v = 0; v < n; ++v) {
                int val = dist[part * n + v] + dist[other * n + v] - cost[v];
                if (val <= cap && val < row[v]) {
                    row[v] = val;
                    parent[v] = -part - 1;
                }
            }
        }
        int head = 0, tail = 0;
        for (int v = 0; v < n; ++v) {
            if (row[v] <= cap) {
                queue[tail++] = v;
                queued[v] = 1;
            }
        }
        while (head != tail) {
            int v = queue[head++];
            if (head == n + 1) head = 0;
            queued[v] = 0;
            for (int i = 0; i < 6; ++i) {
                int w = edges[6 * v + i];
                if (w < 0) continue;
                int val = row[v] + cost[w];
                if (val > cap || val >= row[w]) continue;
                row[w] = val;
                parent[w] = v;
                if (!queued[w]) {
                    queue[tail++] = w;
                    if (tail == n + 1) tail = 0;
                    queued[w] = 1;
                }
            }
        }
    }
    int full = masks - 1, best = -1;
    for (int v = 0; v < n; ++v) {
        if (dist[full * n + v] <= cap &&
            (best < 0 || dist[full * n + v] < dist[full * n + best])) best = v;
    }
#ifdef RED_BRIDGE
    best = -1;
    for(int v=0;v<n;++v) if((members[v]&1) && dist[full*n+v]<=cap &&
        (best<0 || dist[full*n+v]<dist[full*n+best])) best=v;
#endif
    int result = 100;
    if (best >= 0) {
        result = dist[full * n + best];
        recover(n, full, best, from, selected);
    }
    free(dist);
    free(from);
    free(queue);
    free(queued);
    return result;
}

/* Positions are encoded in base 32, with x along flight. */
static const int step[] = {1024,-1024,32,-32,1,-1};

int pose_extra(const int *wp, const int *wr, const int *vp, const int *own_bad,
         const int *prev_bad, int t, int shift, int room, const int *box,
         int margin, int *out, const int *extra_glue) {
    int points[2048], count=0, groups=0;
    uint8_t flags[32768] = {0};
    int16_t index[32768];
    for (int i=0; own_bad[i]>=0; ++i) flags[own_bad[i]]=1;
    for (int i=0; prev_bad[i]>=0; ++i) flags[prev_bad[i]-shift]=1;
    for (int i=0; i<4; ++i) {
        if (flags[wp[i]+1024]) return 0;
        flags[wp[i]+1024]=2;
    }
    int needed[12], nrequired=4;
    for(int i=0;i<4;++i) needed[i]=wp[i]+1024;
    for (int i=0;extra_glue[i]>=0;++i) {
        int v=extra_glue[i];
        if(flags[v]==1) return 0;
        if(flags[v]!=2) needed[nrequired++]=v;
        flags[v]=2;
    }
#ifdef RED_BRIDGE
    for(int i=0;wr[i]>=0;++i) flags[wr[i]]=10;
#endif
    int16_t members[2048]={0}, edges[2048*6];
    uint8_t cost[2048],selected[2048]={0};
    int low=box[0]-1-margin, high=box[3]+margin;
    for(int x=low;x<=high;++x)
    for(int y=box[1]-1-margin;y<=box[4]+1+margin;++y)
    for(int z=box[2]-1-margin;z<=box[5]+1+margin;++z) {
        int v=(x+12)*1024+(y+15)*32+z+15;
        if(flags[v]==1) continue;
        if (count == 2048) return 0;
        index[v]=count;
        points[count]=v;
        cost[count]=!(flags[v]&2);
        flags[v]|=4;
        ++count;
    }
    for(int i=0;i<count;++i) {
        for (int j=0;j<6;++j) {
            int u=points[i]+step[j];
            edges[6*i+j]=(flags[u]&4) ? index[u] : -1;
#ifdef RED_BRIDGE
            /* A redstone block pushes its +X destination. DP propagates from
               a terminal backwards, so its parent may be an RB at -X. */
            if ((flags[u]&8) && j!=1) edges[6*i+j]=-1;
#endif
        }
    }
    for (int j=0;j<nrequired;++j) {
        int v=needed[j], k=index[v];
        if(members[k]) continue;
        int queue[12]={v}, end=1;
        int bit=1<<groups++;
        members[k]=bit;
        for(int h=0;h<end;++h) for(int d=0;d<6;++d) {
            int u=queue[h]+step[d];
            if(flags[u]==6 && !members[index[u]]) {
                members[index[u]]=bit;
                queue[end++]=u;
            }
        }
    }
    for (int i=0;wr[i]>=0;++i) {
#ifdef RED_BRIDGE
        members[index[wr[i]]]|=1<<groups++;
        continue;
#endif
        int bit=1<<groups++, found=0;
        for (int j=0;j<6;++j) {
            int u=wr[i]+step[j];
            if (flags[u]&4) {
                members[index[u]]|=bit;
                found=1;
            }
        }
        if(!found) return 0;
    }
    for (int i=0;i<4;++i) {
        int v=vp[i]-shift-(t+2)*1024;
        int choices[]={v-1024,v+32,v-32,v+1,v-1};
        int bit=1<<groups++,found=0;
        for (int j=0;j<5;++j) {
            int u=choices[j];
            if(flags[u]&4) {
                members[index[u]]|=bit;
                found=1;
            }
        }
        if(!found) return 0;
    }
    int extra=route(count,groups,room-nrequired,edges,cost,members,selected);
    if(extra>room-nrequired) return 0;
    int num=0;
    for(int i=0;i<count;++i) if((selected[i] || cost[i]==0) && !(flags[points[i]]&8)) out[num++]=points[i];
    return num;
}

int pose(const int *wp, const int *wr, const int *vp, const int *own_bad,
         const int *prev_bad, int t, int shift, int room, const int *box,
         int margin, int *out) {
    static const int empty[]={-1};
    return pose_extra(wp,wr,vp,own_bad,prev_bad,t,shift,room,box,margin,out,empty);
}
