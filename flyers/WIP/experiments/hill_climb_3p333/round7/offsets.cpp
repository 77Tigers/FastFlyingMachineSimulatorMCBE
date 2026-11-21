// Enumerate the two carriers of each phase independently. Floyd-Warshall
// prunes incompatible difference constraints before listing integer X poses.
#include <algorithm>
#include <array>
#include <cstdio>
#include <vector>
using namespace std;
struct Template {int kind,mask[2],riders[2];};
int best[3][3][15][4];
vector<Template> options;
array<Template,6> assembly;
array<int,6> caps,x;
array<array<int,6>,6> dist;
long programs=0, feasible=0, poses=0, disconnected=0;
void positions(int i) {
    if(i<6) {
        int lo=-99, hi=99;
        for(int j=0;j<i;j++) {
            lo=max(lo,x[j]-dist[i][j]);
            hi=min(hi,x[j]+dist[j][i]);
        }
        if(i>=3 && assembly[i].kind==assembly[i-3].kind) lo=max(lo,x[i-3]);
        for(int v=lo;v<=hi;v++) {x[i]=v;positions(i+1);}
        return;
    }
    poses++;
    for(auto a:assembly) printf("%d ",a.kind);
    for(int v:x) printf("%d ",v);
    for(int v:caps) printf("%d ",v);
    for(auto a:assembly) printf("%d %d ",a.mask[0],a.mask[1]);
    for(auto a:assembly) printf("%d %d ",a.riders[0],a.riders[1]);
    puts("");
}
void check() {
    programs++;
    for(int j=0;j<6;j++) {
        int pre=(j+2)%3,side=j/3;
        caps[j]=14-3*(j%3==2)-assembly[pre].riders[side]-assembly[pre+3].riders[side];
    }
    for(int i=0;i<6;i++) {dist[i].fill(99);dist[i][i]=0;}
    for(int i=0;i<6;i++) for(int side=0;side<2;side++) {
        int mask=assembly[i].mask[side];
        if(!mask) continue;
        int j=(i+1)%3+side*3, wrap=2*(i%3==2);
        int top=best[assembly[i].kind][assembly[j].kind][caps[j]][mask];
        if(top < -15) return;
        dist[i][j]=min(dist[i][j],top+wrap);
        dist[j][i]=min(dist[j][i],15-wrap);
    }
    for(int k=0;k<6;k++) for(int i=0;i<6;i++) for(int j=0;j<6;j++)
        dist[i][j]=min(dist[i][j],dist[i][k]+dist[k][j]);
    for(int i=0;i<6;i++) if(dist[i][i]<0) return;
    // Two disconnected three-body cycles each need their own -2 closure.
    // Incoming/outgoing ownership never changes between those cycles.
    for(int j=1;j<6;j++) if(dist[0][j]>40) {disconnected++;return;}
    feasible++;
    positions(1);
}
void enumerate(int i) {
    if(i==6) {check();return;}
    for(auto a:options) {
        if(i>=3 && a.kind<assembly[i-3].kind) continue;
        assembly[i]=a;enumerate(i+1);
    }
}
int main() {
    int n,k[5];
    if(scanf("%d",&n)!=1) return 2;
    for(int i=0;i<n;i++) {
        if(scanf("%d%d%d%d%d",k,k+1,k+2,k+3,k+4)!=5)return 2;
        options.push_back({k[0],{k[1],k[2]},{k[3],k[4]}});
    }
    while(scanf("%d%d%d%d%d",k,k+1,k+2,k+3,k+4)==5)
        best[k[0]][k[1]][k[2]][k[3]]=k[4];
    enumerate(0);
    fprintf(stderr,"programs %ld feasible %ld poses %ld disconnected %ld\n",programs,feasible,poses,disconnected);
}
