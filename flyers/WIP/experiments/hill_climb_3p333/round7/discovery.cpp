// Budgeted directed discovery. Each violated reachability cut requires at
// least one newly placed cell. Recurse on disjoint choices for that cell.
#include <algorithm>
#include <cstdint>
#include <vector>
using namespace std;

struct Body {
    int n, cap;
    const int *adj, *flags, *roots, *leaves, *requirements;
    int actions, ngroups;
    vector<char> selected, unavailable;
    vector<int> chosen;
    int limit_at_nodes;
    int nodes=0;
    bool overflow=false;
    int maxresults=1, found=0;
    int *output=nullptr;

    bool step(int p,int q,int dir,int leaf) const {
        return dir==0 || (p!=leaf && (flags[p]&2) && !(flags[q]&4));
    }
    vector<char> reached(int root,int leaf,bool reverse) const {
        vector<char> seen(n);
        vector<int> queue{root};
        seen[root]=1;
        for (size_t i=0;i<queue.size();i++) {
            int p=queue[i];
            for(int d=0;d<6;d++) {
                int q=adj[6*p+d];
                if(q<0 || seen[q] || (!selected[q] && q!=leaf)) continue;
                if(reverse ? step(q,p,d^1,leaf):step(p,q,d,leaf)) {
                    queue.push_back(q); seen[q]=1;
                }
            }
        }
        return seen;
    }
    vector<int> cut(const vector<char> &seen,int leaf,bool reverse) const {
        vector<int> options;
        for(int p=0;p<n;p++) if(seen[p]) for(int d=0;d<6;d++) {
            int q=adj[6*p+d];
            if(q<0 || selected[q] || unavailable[q]) continue;
            if(reverse ? step(q,p,d^1,leaf) : step(p,q,d,leaf)) options.push_back(q);
        }
        sort(options.begin(),options.end());
        options.erase(unique(options.begin(),options.end()),options.end());
        return options;
    }
    bool search() {
        if(++nodes>limit_at_nodes) {overflow=true; return false;}
        bool missing=false;
        vector<int> best;
        auto consider=[&](vector<int> v) {
            if(!missing || v.size()<best.size()) best=std::move(v);
            missing=true;
        };
        for(int g=0;g<ngroups;g++) {
            vector<int> options;
            bool met=false;
            for(int p=0;p<n;p++) if(requirements[p] & (1<<g)) {
                if(selected[p]) { met=true; break; }
                if(!unavailable[p]) options.push_back(p);
            }
            if(!met) consider(options);
        }
        if(missing && (best.empty() || (int)chosen.size()==cap)) return false;
        for(int a=0;a<actions;a++) {
            int leaf=leaves[a];
            auto seen=reached(roots[a],leaf,false);
            bool cut_root=false;
            for(int target:chosen) if(!seen[target]) {
                if((int)chosen.size()==cap) return false;
                if(!cut_root) {consider(cut(seen,leaf,false)); cut_root=true;}
                consider(cut(reached(target,leaf,true),leaf,true));
                if(best.empty()) return false;
            }
        }
        if(!missing) {
            auto sorted=chosen;
            sort(sorted.begin(),sorted.end());
            int *dest=output+found*(cap+1);
            dest[0]=sorted.size();
            copy(sorted.begin(),sorted.end(),dest+1);
            if(++found==maxresults) return true;
            if((int)chosen.size()==cap) return false;
            // Every larger solution reaches its first extra voxel by a
            // face from the current body or a permitted moving leaf.
            for(int p=0;p<n;p++) if(selected[p] || (flags[p]&8))
                for(int d=0;d<6;d++) {
                    int q=adj[6*p+d];
                    if(q>=0 && !selected[q] && !unavailable[q]) best.push_back(q);
                }
            sort(best.begin(),best.end());
            best.erase(unique(best.begin(),best.end()),best.end());
        }
        for(int p:best) {
            selected[p]=1; chosen.push_back(p);
            if(search()) return true;
            selected[p]=0; chosen.pop_back(); unavailable[p]=1;
            if(overflow) break;
        }
        for(int p:best) unavailable[p]=0;
        return false;
    }
};

extern "C" int complete_body(int n,int cap,const int *adj,const int *flags,
    int nroots,const int *roots,const int *leaves,int groups,const int *req,
    int maxnodes,int maxresults,int *out) {
    Body b{n,cap,adj,flags,roots,leaves,req,nroots,groups,
            vector<char>(n),vector<char>(n),{},maxnodes};
    for(int p=0;p<n;p++) {
        if(flags[p]&1) {b.selected[p]=1; b.chosen.push_back(p);}
        b.unavailable[p]=bool(flags[p]&8);
    }
    if((int)b.chosen.size()>cap) return 0;
    b.output=out; b.maxresults=maxresults;
    b.search();
    return b.overflow?-1:b.found;
}
