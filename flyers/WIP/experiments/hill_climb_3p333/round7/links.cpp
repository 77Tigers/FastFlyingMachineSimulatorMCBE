// A local handoff table for independent six-body stencils and split pickups.
#define STAGGER_SCREEN
#include "../round4/back.cpp"

Core stencil(int kind) {
    if (kind==0) return O;
    if (kind==1) return T;
    return A3c;
}
vector<Cell> parts(int i, const Core &c, int origin, int mask) {
    vector<Cell> cells;
    for (int h : c.hoppers) {
        cells.push_back({origin+h,i,H});
        cells.push_back({origin+h+X,i,G});
    }
    for (int r : c.red) cells.push_back({origin+r,i,R});
    for (int n=0;n<(int)c.covers.size();n++)
        if (mask & (1<<n)) cells.push_back({origin+c.covers[n]+(contact_dx(i)-2)*X,nextb(i),G});
    return cells;
}
struct Example {
    int sym, y, z;
    vector<int> glue;
};
int main(int argc, char **argv) {
    if (argc==7 && string(argv[1])=="poses") {
        int from=atoi(argv[2]),to=atoi(argv[3]),cap=atoi(argv[4]),mask=atoi(argv[5]),t=atoi(argv[6]);
        length=6; back_tables();
        auto left=parts(0,stencil(from),0,mask);
        for (int sym=0;sym<8;sym++) for (int y=-15;y<=15;y++) for (int z=-15;z<=15;z++) {
            int delta=pt(t,y,z);
            auto cells=left;
            auto right=parts(1,oriented(stencil(to),sym),delta,0);
            cells.insert(cells.end(),right.begin(),right.end());
            if (!legal(cells)) continue;
            if (!glue_route(1,99,cells,cap).empty()) printf("%d %d %d\n",sym,y,z);
        }
        return 0;
    }
    if (argc!=4 && argc!=5) return 2;
    int from=atoi(argv[1]), to=atoi(argv[2]), cap=atoi(argv[3]);
    bool open=argc==5;
    length=6;
    back_tables();
    auto a=stencil(from), b=stencil(to);
    set<tuple<vector<int>,vector<int>,vector<int>>> seen;
    vector<Core> orientations;
    for (int sym=0;sym<8;sym++) {
        auto v=oriented(b,sym);
        // Record the original placement so offsets can be replayed.
        auto key=make_tuple(v.hoppers,v.red,v.covers);
        sort(get<0>(key).begin(),get<0>(key).end());
        sort(get<1>(key).begin(),get<1>(key).end());
        sort(get<2>(key).begin(),get<2>(key).end());
        if (!seen.insert(key).second) continue;
        orientations.push_back(v);
    }
    int full=(1<<a.covers.size())-1;
    for (int mask=1;mask<=full;mask++) {
        auto left=parts(0,a,0,mask);
        // These are finite stencil bounds. Every reported maximum is the
        // first feasible offset, in descending order including both ends.
        long n=0, conflict=0, over=0, ok=0;
        for (int t=5;t>=-15;t--) {
            map<tuple<int,int,int>,Example> examples;
            for (int o=0;o<(int)orientations.size();o++)
                for (int y=-15;y<=15;y++) for (int z=-15;z<=15;z++) {
                    int d=pt(t,y,z);
                    auto cells=left;
                    auto right=parts(1,orientations[o],d,open ? 0 : (1<<orientations[o].covers.size())-1);
                    cells.insert(cells.end(),right.begin(),right.end());
                    n++;
                    if (!legal(cells)) {conflict++; continue;}
                    auto g=glue_route(1,99,cells,cap);
                    if (g.empty()) {over++; continue;}
                    ok++;
                    examples[{o,y,z}]={o,y,z,g};
                }
            if (!examples.empty()) {
                auto ex=examples.begin()->second;
                printf("%d %d %d %d %d %ld %ld %ld %ld %d %d %d",from,to,cap,mask,t,n,conflict,over,ok,ex.sym,ex.y,ex.z);
                for (int p:ex.glue) printf(" %d,%d,%d",xc(p),yc(p),zc(p));
                puts("");
                break;
            }
            if (t==-15) printf("%d %d %d %d -99 %ld %ld %ld %ld\n",from,to,cap,mask,n,conflict,over,ok);
        }
    }
}
