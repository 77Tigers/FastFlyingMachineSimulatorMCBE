// Enumerate a necessary two-plane motor module before choosing the last pull
// or the victim's own hopper. Each extra cell costs one of twelve rigid cells.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <set>
#include <string>
#include <vector>
using namespace std;

constexpr int X = 1024, Y = 32;
const array<int, 4> sides{Y, -Y, 1, -1};
const array<int, 6> faces{X, -X, Y, -Y, 1, -1};
int xc(int p) { return (p + 16 * X + 16 * Y + 16) / X - 16; }
int yc(int p) { return (p - X * xc(p) + 16 * Y + 16) / Y - 16; }
int zc(int p) { return p - X * xc(p) - Y * yc(p); }
int norm(int p) { return abs(xc(p)) + abs(yc(p)) + abs(zc(p)); }
using Cluster = array<int,4>;
using Cells = set<int>;

struct Pose {
    Cells fixed, empty, passive;
    int first, caught, spent, own_h, early, late, rod;
    bool shared;

    Pose(Cluster a, Cluster b, int r, bool own_direct, bool return_direct, bool shared_gate) : shared(shared_gate) {
        rod = r;
        first = r + b[0];
        caught = r - 3*X + b[1];
        spent = r - (return_direct ? 2 : 3)*X + b[3];
        own_h = a[3] + X*own_direct;
        early = X + a[1];
        late = X + a[2];
        fixed = {0, a[0], early, late, r, first, caught};
        passive = {a[0], early, late, r};
        empty = {a[1], a[2], X+a[0], caught+X};
        if (shared) {
            empty.insert(own_h); empty.insert(own_h-X);
            for (int d : faces) passive.insert(own_h+d);
        }
        const array<int,6> db{0,-1,-2,-2,-2,-1}, dc{3,3,3,2,1,2};
        for (int s=0; s<6; ++s) {
            int donor=dc[s]*X, hub=r+(db[s]-1)*X;
            empty.insert(donor);
            if (s==2 || s==3) {
                for (int d : faces) passive.insert(donor+d);
                empty.insert(donor-X);
            }
            for (int p : {hub, hub+b[0], hub+X+b[1], hub+X+b[2]}) empty.insert(p);
            if (s<=1) {
                empty.insert(hub+b[1]);
                empty.insert(hub+b[2]);
            }
            if (s==1) empty.insert(hub+X+b[0]);
            if (!shared) continue;
            int h=spent+(2+db[s])*X;
            empty.insert(h);
            if (s==1) empty.insert(h+X);
            if (s==0) for (int d : faces) passive.insert(h+d);
            if (s<2) empty.insert(h-X);
        }
    }
    bool fits() const {
        for (int p : fixed) if (empty.count(p)) return false;
        return !passive.count(caught) && first!=rod;
    }
};

// From a fixed root, every connected completion must select a first new cell
// on the boundary of its reached set. Branch on that cut; forbid earlier
// siblings to enumerate a body once. The reverse search permits precisely
// the same directed edges as the forward search.
struct CutSearch {
    const Pose &pose;
    Cells used, excluded;
    int cap;
    vector<int> goals;
    CutSearch(const Pose &p, int n) : pose(p), used(p.fixed), excluded(p.empty), cap(n) {
        goals.assign(used.begin(),used.end());
    }

    bool can_step(int a, int b, int leaf) const {
        return b-a==X || (a!=leaf && !pose.passive.count(a));
    }
    Cells reachable(int root, int leaf, bool reverse) const {
        Cells seen{root};
        vector<int> todo{root};
        for (size_t i=0;i<todo.size();++i) {
            int p=todo[i];
            for (int d : faces) {
                int q=p+d;
                if ((!used.count(q) && q!=leaf) || seen.count(q)) continue;
                if (reverse ? can_step(q,p,leaf) : can_step(p,q,leaf)) {
                    seen.insert(q); todo.push_back(q);
                }
            }
        }
        return seen;
    }
    void choose(Cells &best, bool &missing, Cells options) const {
        if (!missing || options.size()<best.size()) best=std::move(options);
        missing=true;
    }
    Cells boundary(const Cells &from, int leaf, bool reverse) const {
        Cells result;
        for (int p : from) for (int d : faces) {
            int q=p+d;
            if (used.count(q) || excluded.count(q)) continue;
            if (reverse ? can_step(q,p,leaf) : can_step(p,q,leaf)) result.insert(q);
        }
        return result;
    }
    bool complete() {
        bool missing=false;
        Cells best;
        // At slot 2 the two idle stickies must be carried. Their -X cells
        // are reserved for the arms and +X glue is inside the waiting rod's
        // six-neighbor sweep. A glue lateral to each sticky is necessary.
        for (int target : {pose.early,pose.late,pose.spent}) {
            if (!pose.shared && target==pose.spent && target!=pose.early && target!=pose.late) continue;
            Cells opts;
            for (int d : faces) {
                int p=target+d;
                if ((pose.passive.count(p) && d!=-X) || excluded.count(p)) continue;
                if (used.count(p)) { opts.clear(); opts.insert(target); break; }
                opts.insert(p);
            }
            if (!opts.count(target)) choose(best,missing,opts);
        }
        if (missing && (best.empty() || (int)used.size()==cap)) return false;
        // This donor moves with the victim on both early slots. It may be
        // dragged as a leaf and transmit an eastward obstruction for free.
        constexpr int leaf=3*X;
        for (int root : {pose.first,pose.caught}) {
            auto reached=reachable(root,leaf,false);
            bool cut=false;
            for (int goal : goals) if (!reached.count(goal)) {
                if ((int)used.size()==cap) return false;
                if (!cut) { choose(best,missing,boundary(reached,leaf,false)); cut=true; }
                auto incoming=reachable(goal,leaf,true);
                choose(best,missing,boundary(incoming,leaf,true));
                // Internal nodes of a shortest lattice walk have positive
                // cost except already selected cells. Do not charge them twice.
                if (best.empty()) return false;
            }
        }
        if (!missing) return true;
        vector<int> restore;
        for (int p : best) {
            used.insert(p);
            if (complete()) return true;
            used.erase(p);
            excluded.insert(p);
            restore.push_back(p);
        }
        for (int p : restore) excluded.erase(p);
        return false;
    }
};

int main(int argc, char **argv) {
    if (argc!=4) return 2;
    string mode=argv[3];
    bool shared=mode=="shared", borrowed=mode=="borrowed";
    if (!shared && !borrowed && mode!="free") return 2;
    int cap=atoi(argv[1]), r=atoi(argv[2]);
    vector<Cluster> cs;
    Cluster c=sides;
    sort(c.begin(),c.end());
    do { cs.push_back(c); } while (next_permutation(c.begin(),c.end()));
    long poses=0, blocked=0, bounds=0, survivors=0;
    for (auto a : cs) {
        if (a[0]!=Y || a[1]==-1 || (a[1]==-Y && a[2]==-1)) continue;
        for (auto b : cs) for (int y=-12;y<=12;y++) for (int z=-12;z<=12;z++) {
            // The two known rigid terminals must share a discovery with at
            // most fourteen sources. Two points can be at most 13 edges apart.
            if (r+abs(y)+abs(z)>(borrowed ? 14:13)) continue;
            int rod=r*X+y*Y+z;
            for (bool d : {false,true}) for (bool e : {false,true}) {
                if (!shared && (d || e)) continue;
                poses++;
                Pose p(a,b,rod,d,e,shared);
                if (borrowed) {
                    if (p.caught==0 || p.first==0) {blocked++; continue;}
                    p.fixed.erase(0);p.empty.insert(0);
                }
                if (!p.fits()) { blocked++; continue; }
                // A connected set spans at least the sum of its axis ranges.
                array<int,3> lo{0,0,0}, hi{0,0,0};
                for (int v : p.fixed) {
                    array<int,3> q{xc(v),yc(v),zc(v)};
                    for (int j=0;j<3;j++) { lo[j]=min(lo[j],q[j]); hi[j]=max(hi[j],q[j]); }
                }
                if (1+hi[0]-lo[0]+hi[1]-lo[1]+hi[2]-lo[2]>cap+1) { bounds++; continue; }
                CutSearch search(p,cap);
                if (!search.complete()) { bounds++; continue; }
                survivors++;
                printf("pose %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                    r,y,z,a[0],a[1],a[2],a[3],b[0],b[1],b[2],b[3],int(d),int(e));
            }
        }
    }
    fprintf(stderr,"%s r=%d poses=%ld blocked=%ld transport=%ld retained=%ld\n",argv[3],r,poses,blocked,bounds,survivors);
}
