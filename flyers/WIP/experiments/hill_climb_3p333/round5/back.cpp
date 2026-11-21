#include "motion.hpp"
#include <numeric>
using namespace tower;
struct Core {
  vector<int> hoppers, red, covers;
};
struct Gate { int observer, red, hit; vector<int> plate; };
Gate gate;
Core gated_core = {{Y, 1}, {}, {Y+1}};
Core T = {{1, Y, Y + 2}, {Y + 1}, {0, 2}};
Core O = {{-Y, -1, 1}, {-Y - 1, -Y + 1}, {0}};
Core oriented(Core c, int sym) {
  for (auto list : {&c.hoppers, &c.red, &c.covers})
    for (auto &p : *list)
      p = turn(p, sym);
  return c;
}
vector<Cell> hardware(int i, const Core &c, int origin, int sym) {
  vector<Cell> cells;
  for (int h : c.hoppers) {
    cells.push_back({origin + h, i, H});
    cells.push_back({origin + h + X, i, G});
  }
  for (int r : c.red)
    cells.push_back({origin + r, i, R});
  if (i % 3 == 2) {
    auto add = [&](int p, Part kind, int id) {
      cells.push_back({origin + turn(p, sym), id, static_cast<Kind>(kind)});
    };
    add(0, Center, i);
    add(gate.observer, Observer, i);
    add(gate.red, Red, i);
    for(int g:gate.plate) add(g, Glue, i);
    add(X + Y + 1, Sticky, i);
    add((contact_dx(i) - 3) * X + gate.hit, Push, nextb(i));
  }
  for (int q : c.covers)
    cells.push_back({origin + q + (contact_dx(i) - 2) * X, nextb(i), G});
  return cells;
}
bool incompatible(Cell a, Cell b) {
  return conflict({a.i, static_cast<Part>(a.k), a.p},
                  {b.i, static_cast<Part>(b.k), b.p});
}
bool allowed(Cell u, const vector<Cell> &v) {
  for (auto c : v) {
    if ((c.k == G || (int)c.k == Center) && u.k == G && c.i == u.i && c.p == u.p)
      continue;
    if (incompatible(u, c))
      return false;
  }
  return true;
}
bool legal(const vector<Cell> &cells) {
  for (size_t i = 0; i < cells.size(); i++)
    for (size_t j = 0; j < i; j++) {
      auto a = cells[i], b = cells[j];
      if (a.k == G && b.k == G && a.i == b.i && a.p == b.p)
        continue;
      if (incompatible(a, b))
        return false;
    }
  return true;
}
vector<int> glue_route(int body, int xbase, const vector<Cell> &cells,
                       int capacity, int variant = 0) {
  set<int> req;
  vector<vector<int>> groups;
  vector<int> reds, sticky;
  for (auto c : cells)
    if (c.i == body) {
      if (c.k == G || (int)c.k == Center)
        req.insert(c.p);
      if (c.k == R)
        reds.push_back(c.p);
      if ((int)c.k == Sticky || (int)c.k == Push || (int)c.k == Observer)
        sticky.push_back(c.p);
    }
  int budget = capacity - req.size() - reds.size();
  if (budget < 0 || req.empty())
    return {};
  set<int> unseen = req;
  while (!unseen.empty()) {
    vector<int> g = {*unseen.begin()};
    unseen.erase(g[0]);
    for (size_t n = 0; n < g.size(); n++)
      for (int d : dirs)
        if (unseen.erase(g[n] + d))
          g.push_back(g[n] + d);
    groups.push_back(g);
  }
  auto attachments = reds;
  attachments.insert(attachments.end(), sticky.begin(), sticky.end());
  for (int r : attachments) {
    vector<int> g;
    bool met = false;
    for (int d : dirs) {
      g.push_back(r + d);
      met |= req.count(r + d) > 0;
    }
    if (!met)
      groups.push_back(g);
  }
  int low[3] = {99, 99, 99}, high[3] = {-99, -99, -99};
  for (auto &g : groups)
    for (int p : g) {
      array<int, 3> q = {xc(p), yc(p), zc(p)};
      for (int k = 0; k < 3; k++) {
        low[k] = min(low[k], q[k]);
        high[k] = max(high[k], q[k]);
      }
    }
  // A connected collection must span the coordinate range of its required glue.
  int spread = 1;
  for (auto f : {xc, yc, zc}) {
    int a = 99, b = -99;
    for (int p : req) {
      a = min(a, f(p));
      b = max(b, f(p));
    }
    for (const auto &g : groups) {
      int g0 = 99, g1 = -99;
      for (int p : g) {
        g0 = min(g0, f(p));
        g1 = max(g1, f(p));
      }
      a = min(a, g1);
      b = max(b, g0);
    }
    spread += b - a;
  }
  if (spread > capacity - (int)reds.size())
    return {};
  
  Grid gr;
  for (int x = low[0] - 1; x <= high[0] + 1; x++)
    for (int y = low[1] - 1; y <= high[1] + 1; y++)
      for (int z = low[2] - 1; z <= high[2] + 1; z++) {
        int p = pt(x, y, z);
        if (allowed({p, body, G}, cells))
          gr.points.push_back(p);
      }
  if (variant) {
    mt19937 rng(variant);
    shuffle(gr.points.begin(), gr.points.end(), rng);
  }
  for (int p : gr.points) {
    auto id = gr.index.size();
    gr.index[p] = id;
    gr.cost.push_back(!req.count(p));
  }
  for (int p : req)
    if (!gr.index.count(p))
      return {};
  gr.members.resize(gr.points.size());
  for (auto &g : groups) {
    bool ok = false;
    for (int p : g)
      if (gr.index.count(p)) {
        ok = true;
        gr.members[gr.index[p]] |= 1 << gr.groups;
      }
    if (!ok)
      return {};
    gr.groups++;
  }
  for (int p : gr.points)
    for (int d : dirs) {
      auto it = gr.index.find(p + d);
      gr.links.push_back(it == gr.index.end() ? -1 : it->second);
    }
  vector<uint8_t> selected(gr.points.size());
  int extra = route(gr.points.size(), gr.groups, budget, gr.links.data(),
                    gr.cost.data(), gr.members.data(), selected.data());
  if (extra == 100)
    return {};
  vector<int> out(req.begin(), req.end());
  for (size_t k = 0; k < selected.size(); k++)
    if (selected[k] && gr.cost[k])
      out.push_back(gr.points[k]);
  return out;
}
struct Handoff {
  int delta;
  vector<int> g;
};
vector<Handoff> links(int i, const Core &a, const Core &b, int t, int cap, int sa, int sb) {
  vector<Handoff> out;
  auto h = hardware(i, a, 0, sa);
  int j = nextb(i);
  for (int y = -10; y <= 10; y++)
    for (int z = -10; z <= 10; z++) {
      int delta = pt(t + contact_dx(i), y, z);
      auto n = hardware(j, b, delta, sb), cells = h;
      cells.insert(cells.end(), n.begin(), n.end());
      if (!legal(cells))
        continue;
      auto g = glue_route(j, xc(delta), cells, cap);
      if (!g.empty())
        out.push_back({delta, g});
    }
  return out;
}
// Place the middle body's hoppers on pickup sites already present on its carrier.
vector<Core> middle_cores(const vector<Cell>& fixed, int offset, int cap, int body=1, int carrier=2, int min_x=-2, int max_x=2) {
  set<int> possible;
  for(auto c:fixed) if(c.i==carrier && c.k!=H)
    for(int d:dirs)
      if(c.k==G || (int)c.k==Center || d==X) possible.insert(c.p+2*X+d);
  vector<int> hs;
  for(int h:possible) {
    if(xc(h)<min_x || xc(h)>max_x)continue;
    if(allowed({h,body,H},fixed) && allowed({h+X,body,G},fixed)) hs.push_back(h);
  }
  vector<Core> out;
  for(int a=0;a<(int)hs.size();a++)for(int b=0;b<a;b++)for(int c=0;c<b;c++) {
    Core core{{hs[a],hs[b],hs[c]}, {}, {}};
    auto world=fixed;
    for(int h:core.hoppers) {world.push_back({h,body,H});world.push_back({h+X,body,G});}
    if(!legal(world))continue;
    set<int> sites;
    for(int h:core.hoppers)for(int d:{Y,-Y,1,-1})
      if(allowed({h+d,body,R},world))sites.insert(h+d);
    for(int p:sites)for(int q:sites){
      if(q<p)continue;
      int mask=0,mp=0,mq=0;
      for(int k=0;k<3;k++){
        if(norm(p-core.hoppers[k])==1 && xc(p)==xc(core.hoppers[k]))mp|=1<<k;
        if(norm(q-core.hoppers[k])==1 && xc(q)==xc(core.hoppers[k]))mq|=1<<k;
      }
      if((mp|mq)!=7 || (q!=p && (mp==7 || mq==7))) continue;
      core.red={p}; if(p!=q)core.red.push_back(q);
      auto copy=world;
      for(int r:core.red)copy.push_back({r,body,R});
      if(!glue_route(body,99,copy,cap).empty())out.push_back(core);
    }
  }
  return out;
}
#ifndef STAGGER_SCREEN
int main(int argc, char **argv) {
  if (argc != 10 || (string(argv[1]) != "0" && string(argv[1]) != "1")) {
    cerr << "back stagger-first t0 t1 t2 cap0 cap1 cap2 output max-witnesses\n";
    return 2;
  }
  Core first = T, middle = atoi(argv[1]) ? T : O;
  length = 6;
  topology();
  pair_tables();
  array<int, 3> offsets, caps;
  for (int j = 0; j < 3; j++) {
    offsets[j] = atoi(argv[j + 2]);
    caps[j] = atoi(argv[j + 5]);
  }
  if (accumulate(offsets.begin(), offsets.end(), 0) != -2)
    return 2;
  ofstream out(argv[8]);
  int save = atoi(argv[9]);
  long long tested = 0, clear = 0, routed = 0;
  auto choices_for = [&](Core core, bool rotate) {
    vector<Core> poses;
    set<array<vector<int>,3>> seen;
    auto sites = [&](const vector<int>& exclude) {
      set<int> all;
      for (int h : core.hoppers)
        for (int d : {Y,-Y,1,-1})
          if (find(exclude.begin(),exclude.end(),h+d)==exclude.end()) all.insert(h+d);
      return vector<int>(all.begin(),all.end());
    };
    auto covers = [&](const vector<int>& points, int maximum) {
      vector<vector<int>> results;
      for (unsigned m=1; m < (1u << points.size()); m++) {
        if (__builtin_popcount(m)>maximum) continue;
        vector<int> group;
        for (size_t i=0;i<points.size();i++) if(m&(1u<<i)) group.push_back(points[i]);
        set<int> useful;
        bool ok=true;
        for(int h: core.hoppers) {
          vector<int> ns;
          for(int p: group) if(norm(p-h)==1) ns.push_back(p);
          if(ns.empty()) ok=false;
          if(ns.size()==1) useful.insert(ns[0]);
        }
        if(ok && useful.size()==group.size()) results.push_back(group);
      }
      return results;
    };
    for(auto red: covers(sites({}),2))
      for(auto cv: covers(sites(red),2)) {
        Core variant{core.hoppers,red,cv};
        for(int sym=0;sym<(rotate?8:1);sym++) {
          Core c=oriented(variant,sym);
          int dy=99,dz=99;
          for(int h:c.hoppers){dy=min(dy,yc(h));dz=min(dz,zc(h));}
          for(auto list:{&c.hoppers,&c.red,&c.covers}) {
            for(int &p:*list) p-=pt(0,dy,dz);
            sort(list->begin(),list->end());
          }
          if(seen.insert({c.hoppers,c.red,c.covers}).second) poses.push_back(c);
        }
      }
    return poses;
  };
  auto firsts=choices_for(first,true), mids=choices_for(middle,true);
  if (atoi(argv[1])==1) {
    set<array<vector<int>,3>> seen;
    firsts.clear();
    for(int lone:{0,Y+1,-Y,2*Y,2, Y-1})for(int dx:{-2,-1,1,2}) {
      for(int r:{Y,-Y,1,-1})for(int q:{Y,-Y,1,-1,-X}) {
        if(q==r)continue;
        for(int sym=0;sym<8;sym++) {
          Core c{{Y,1,lone+dx*X},{0,lone+dx*X+r},{Y+1,lone+dx*X+q}};
          c=oriented(c,sym);
          for(auto group:{&c.hoppers,&c.red,&c.covers})sort(group->begin(),group->end());
          if(!seen.insert({c.hoppers,c.red,c.covers}).second)continue;
          auto h=hardware(0,c,0,0);
          if(legal(h)&&!glue_route(0,99,h,caps[0]).empty())firsts.push_back(c);
        }
      }
    }
    cout<<"staggered towerless back poses "<<firsts.size()<<endl;
  }
  map<pair<int,int>,vector<Handoff>> middle_edges;
  vector<Gate> gates;
  for (int obs : {-Y,-1,-X}) {
    // The front plate joins the two hopper faces through the center.
    for (int extra : {0, X-Y, X-1, X+2*Y, X+Y-1, X+2, X+1-Y, -Y,-1,-X}) {
      set<int> glue{0,X,X+Y,X+1};
      glue.insert(extra);
      set<int> solids=glue;
      solids.insert(obs); solids.insert(Y); solids.insert(1); solids.insert(X+Y+1);
      if (glue.count(obs)) continue;
      for (int hit : solids) {
        if (hit==X+Y+1 || solids.count(hit-X)) continue;
        for(int d:{Y,-Y,1,-1}) {
          int red=hit-X+d;
          if(solids.count(red)) continue;
          bool attached=false;
          for(int side:dirs) attached|=glue.count(red+side)!=0;
          if(!attached)continue;
          vector<int> plate{X};
          if(extra && extra!=X)plate.push_back(extra);
          gates.push_back({obs,red,hit,plate});
        }
      }
    }
  }
  int viable=0, local_ok=0, right_ok=0;
  for (auto design:gates) {
    gate=design;
    auto single=hardware(2,gated_core,0,0);
    if(!legal(single)) continue;
    local_ok++;
    vector<pair<int,vector<Handoff>>> rhs,lhs;
    auto gated_cells=hardware(2,gated_core,offsets[1]*X,0);
    mids=middle_cores(gated_cells,offsets[1],caps[1]);
    middle_edges.clear();
    for(int mi=0;mi<(int)mids.size();mi++) {
      auto cells=gated_cells, h=hardware(1,mids[mi],0,0);
      cells.insert(cells.end(),h.begin(),h.end());
      if(!legal(cells))continue;
      auto glue=glue_route(2,99,cells,caps[2]);
      if(!glue.empty())rhs.push_back({mi,{{offsets[1]*X,glue}}});
    }
    if(rhs.empty())continue;
    right_ok++;
    for(int ai=0;ai<(int)firsts.size();ai++) {
      auto list=links(2,gated_core,oriented(firsts[ai],2),offsets[2],caps[0],0,2);
      if(!list.empty())lhs.push_back({ai,move(list)});
    }
    if(lhs.empty())continue;
    viable++;
    for(auto &[ai,e2]:lhs)for(auto &[mi,e1]:rhs){
      first=firsts[ai]; middle=mids[mi];
      auto key=make_pair(ai,mi);
      if(!middle_edges.count(key))
        middle_edges[key]=links(0,first,middle,offsets[0],caps[1],0,0);
      const auto &e0=middle_edges[key];
      int s1=0,s2=0;
      for (auto &a : e0)
        for (auto &b : e1)
          for (auto &c : e2) {
            tested++;
            int axis = a.delta + b.delta + c.delta;
            array<int, 6> at = {0,
                                a.delta,
                                a.delta + b.delta,
                                axis,
                                axis + turn(a.delta, 2),
                                axis + turn(a.delta + b.delta, 2)};
            array<Core, 6> cores = {first,
                                    oriented(middle, s1),
                                    oriented(gated_core, s2),
                                    oriented(first, 2),
                                    oriented(middle, (s1 & 4) | ((s1 + 2) % 4)),
                                    oriented(gated_core, (s2 & 4) | ((s2 + 2) % 4))};
            vector<Cell> cells;
            for (int i = 0; i < 6; i++) {
              int sym = i % 3 == 2 ? ((s2 & 4) | ((s2 + (i / 3) * 2) % 4)) : 0;
              auto h = hardware(i, cores[i], at[i], sym);
              cells.insert(cells.end(), h.begin(), h.end());
            }
            if (!legal(cells))
              continue;
            clear++;
            // Use the local shortest routes first. If neighbours obstruct one,
            // reroute it in the complete ring.
            array<vector<int>, 3> gs = {c.g, a.g, b.g};
            for (int &p : gs[0])
              p = turn(p + a.delta + b.delta, 2) + axis;
            for (int &p : gs[2])
              p += a.delta;
            auto addroute = [&](int i, const vector<int> &g,
                                vector<Cell> &world) {
              for (int p : g) {
                Cell h = {p, i, G}, mate = {turn(p, 2) + axis, i + 3, G};
                if (!allowed(h, world) || !allowed(mate, world))
                  return false;
                bool center = any_of(world.begin(), world.end(), [&](Cell c) {
                  return c.i == i && c.p == p && (int)c.k == Center;
                });
                if (!center) { world.push_back(h); world.push_back(mate); }
              }
              return true;
            };
            vector<Cell> world = cells;
            bool ok = true;
            for (int i = 0; i < 3 && ok; i++)
              ok = addroute(i, gs[i], world);
            if (!ok) {
              for (int retry = 0; retry < 6 && !ok; retry++) {
                world = cells;
                ok = true;
                for (int n = 0; n < 3 && ok; n++) {
                  int i = (n + retry) % 3;
                  auto g = glue_route(i, xc(at[i]), world, caps[i], retry);
                  ok = !g.empty() && addroute(i, g, world);
                }
              }
            }
            if (!ok)
              continue;
            routed++;
            if (routed <= save) {
              set<tuple<int, int, int>> unique;
              for (auto h : world)
                unique.emplace(h.i, h.k, h.p);
              out << "ring " << routed << "\n";
              for (int i = 0; i < 6; i++)
                out << i << " origin " << xc(at[i]) << " " << yc(at[i]) << " "
                    << zc(at[i]) << "\n";
              for (auto [i, k, p] : unique)
                out << i << " " << symbols[k] << " " << xc(p) << " " << yc(p)
                    << " " << zc(p) << "\n";
              out.flush();
            }
            if (save > 0 && routed == save)
              goto done;
          }
    }
    }
done:
  cout << "gate designs " << gates.size() << " locally legal " << local_ok << " middle-gated " << right_ok << " with both links " << viable
       << " combinations " << tested << " clear " << clear << " routed "
       << routed << " saved " << min<long long>(routed, save) << "\n";
}
#endif
