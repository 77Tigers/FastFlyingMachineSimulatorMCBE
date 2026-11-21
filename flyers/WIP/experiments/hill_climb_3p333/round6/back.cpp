#include "route.hpp"
using namespace search;

struct Search {
  int x0, x1, cap1, goal, count = 0;
  int front_cap = 10, yzr = 6;
  bool stagger = false, swap_push = false, joint = false;
  long cores = 0, stalks = 0, fronts = 0, pushes = 0, joins = 0, routes = 0;
  ofstream out;
  World plate;
  struct Ends {
    World hardware;
    int axis;
  };
  map<int, vector<Ends>> ends_by_axis;
  set<vector<tuple<int, int, int>>> saved;
  Search(int t0, int t1, int cap, int limit, const char *path)
      : x0(-t1 - t0), x1(-t1), cap1(cap), goal(limit), out(path) {}
  bool mirror_add(World &w, Block c, int a) {
    axis = a;
    return add(w, c) && add(w, mirrored(c));
  }
  void save(const World &w, int a) {
    vector<tuple<int, int, int>> key;
    for (auto c : w)
      key.emplace_back(c.id, c.part, c.pos);
    sort(key.begin(), key.end());
    if (!saved.insert(key).second)
      return;
    out << "ring " << ++count << "\n";
    array<int, 6> origins{x0 * X, x1 * X, 0, a + x0 * X, x1 * X + a, a};
    // The tower search uses the half-turn translation independently of the
    // B0 center. Encode B0's lane as zero for that origin convention.
    for (int i = 0; i < 6; i++)
      out << i << " origin " << xc(origins[i]) << " " << yc(origins[i]) << " "
          << zc(origins[i]) << "\n";
    for (auto [i, k, p] : key)
      out << i << " " << symbols[k] << " " << xc(p) << " " << yc(p) << " "
          << zc(p) << "\n";
    out.flush();
  }
  const vector<Ends> &ends(int a) {
    auto [it, fresh] = ends_by_axis.try_emplace(a);
    if (!fresh)
      return it->second;
    auto &result = it->second;
    World base;
    for (auto b : plate)
      if (!mirror_add(base, b, a))
        return result;
    set<int> ps, rs;
    for (auto b : plate)
      if (b.id == 2) {
        ps.insert(b.pos - X);
        if (glue(b.part))
          for (int d : dirs)
            rs.insert(b.pos + d);
      }
    for (int p : ps)
      for (int host : {3, 0}) {
        if (host == 0 && !swap_push)
          continue;
        auto w = base;
        if (!mirror_add(w, {host, Push, p}, a))
          continue;
        for (int r : rs) {
          int dp = r - p, dc = r - (a + turn(p, 2));
          auto powers = [](int diff) { return norm(diff) == 1 && diff != X; };
          if (!(powers(dp) || powers(dc)))
            continue;
          auto q = w;
          if (mirror_add(q, {2, Red, r}, a))
            result.push_back({q, a});
        }
      }
    return result;
  }
  void close(const World &front, int center, int pushsite) {
    for (int dy = -yzr; dy <= yzr; dy++)
      for (int dz = -yzr; dz <= yzr; dz++) {
        int a = pt(0, yc(center) + dy, zc(center) + dz);
        if (any_of(plate.begin(), plate.end(), [&](Block b) {
              return b.id == 3 && norm(center - a - turn(b.pos, 2)) > front_cap;
            }))
          continue;
        for (auto &end : ends(a)) {
          World w = end.hardware;
          bool ok = true;
          for (auto b : front)
            if (b.id < 2 && !mirror_add(w, b, a)) {
              ok = false;
              break;
            }
          if (!ok)
            continue;
          if (pushsite == 999999) {
            set<int> sites;
            for (auto g : w)
              if (g.id == 4 && glue(g.part))
                for (int d : dirs)
                  sites.insert(g.pos + d);
            for (int pos : sites) {
              int hit = pos + 3 * X;
              if (norm(hit - center) > 4)
                continue;
              auto candidate = w;
              if (!mirror_add(candidate, {4, Push, pos}, a))
                continue;
              if (none_of(candidate.begin(), candidate.end(),
                          [&](Block b) { return b.id == 0 && b.pos == hit; }) &&
                  !mirror_add(candidate, {0, Glue, hit}, a))
                continue;
              finish(candidate, pos, a);
              if (count >= goal)
                return;
            }
          } else
            finish(w, pushsite, a);
          if (count >= goal)
            return;
        }
      }
  }
  void finish(const World &w, int pushsite, int a) {
    joins++;
    for (int donor : {0, 3})
      for (int d : {-X, Y, -Y, 1, -1}) {
        auto v = w;
        if (!mirror_add(v, {donor, Red, pushsite + 2 * X + d}, a))
          continue;
        for (int variant = 0; variant < 4; variant++) {
          auto q = v;
          auto g = connect(q, 0, front_cap, {}, variant);
          if (g.empty())
            break;
          bool ok = true;
          for (int p : g)
            if (!mirror_add(q, {0, Glue, p}, a)) {
              ok = false;
              break;
            }
          if (ok) {
            routes++;
            save(q, a);
            break;
          }
        }
        if (count >= goal)
          return;
      }
  }
  void place_front(const World &w) {
    set<int> possible_h, ps;
    for (auto c : w)
      if (c.id == 1) {
        if (glue(c.part))
          for (int d : dirs) {
            int h = c.pos + 2 * X + d;
            if (xc(h) == x0 || (stagger && xc(h) == x0 + 1))
              possible_h.insert(h);
            ps.insert(c.pos + d);
          }
        int h = c.pos + 3 * X;
        if ((xc(h) == x0 || (stagger && xc(h) == x0 + 1)) && c.part != Hopper)
          possible_h.insert(h);
      }
    for (int h : possible_h)
      for (int du : {Y, -Y, 1, -1, -X}) {
        int center = h + du;
        if (xc(center) != x0)
          continue;
        for (int dv : {Y, -Y, 1, -1, X}) {
          int j = center + dv;
          if (h >= j || !possible_h.count(j))
            continue;
          auto core = w;
          if (!add(core, {0, Center, center}) || !add(core, {0, Hopper, h}) ||
              !add(core, {0, Hopper, j}) || !add(core, {0, Glue, h + X}) ||
              !add(core, {0, Glue, j + X}))
            continue;
          for (int od : {-X, Y, -Y, 1, -1}) {
            auto f = core;
            if (!add(f, {0, Observer, center + od}))
              continue;
            fronts++;
            if (swap_push)
              close(f, center, 999999);
            if (count >= goal)
              return;
            for (int p : ps) {
              int hit = p + 3 * X;
              if (norm(hit - center) > 4)
                continue;
              auto v = f;
              if (!add(v, {1, Push, p}))
                continue;
              bool existing = any_of(v.begin(), v.end(), [&](Block c) {
                return c.id == 0 && c.pos == hit;
              });
              if (!existing && !add(v, {0, Glue, hit}))
                continue;
              pushes++;
              close(v, center, p);
              if (count >= goal)
                return;
            }
          }
        }
      }
  }
  void grow(const World &base, const Sites &glues, int room) {
    set<Sites> checked;
    auto walk = [&](auto &&self, World &v, int p, Sites &extra,
                    int left) -> void {
      if (xc(p) <= x0 + int(stagger)) {
        Sites key = extra;
        sort(key.begin(), key.end());
        if (checked.insert(key).second) {
          stalks++;
          place_front(v);
        }
      }
      if (!left || xc(p) - left > x0 + int(stagger) || count >= goal)
        return;
      for (int d : {-X, Y, -Y, 1, -1, X}) {
        int next = p + d;
        if (xc(next) > x1 + 1 ||
            find(glues.begin(), glues.end(), next) != glues.end() ||
            find(extra.begin(), extra.end(), next) != extra.end())
          continue;
        size_t old = v.size();
        if (!add(v, {1, Glue, next}))
          continue;
        extra.push_back(next);
        self(self, v, next, extra, left - 1);
        extra.pop_back();
        v.resize(old);
        if (count >= goal)
          return;
      }
    };
    auto w = base;
    Sites extra;
    for (int p : glues) {
      walk(walk, w, p, extra, room);
      if (count >= goal)
        return;
    }
  }
  // Route the three middle faces, both spent front hoppers and the pusher
  // in one Steiner problem. This also admits nonminimal middle plates.
  void join_middle(const World &w, const Sites &hs) {
    set<int> centers;
    for (int h : hs)
      for (int dy = -3; dy <= 3; dy++)
        for (int dz = -3; dz <= 3; dz++)
          if (abs(dy) + abs(dz) <= 4)
            centers.insert(pt(x0, yc(h) + dy, zc(h) + dz));
    for (int c : centers)
      for (int u : {Y, -Y, 1, -1, X})
        for (int v : {Y, -Y, 1, -1, X}) {
          if (u >= v)
            continue;
          auto front = w;
          int h = c + u, j = c + v;
          if (!add(front, {0, Center, c}) || !add(front, {0, Hopper, h}) ||
              !add(front, {0, Hopper, j}) || !add(front, {0, Glue, h + X}) ||
              !add(front, {0, Glue, j + X}))
            continue;
          Groups pickups;
          for (int ready : {h, j})
            if (!side_pick(front, 1, ready - 2 * X))
              pickups.push_back(neighbors(ready - 2 * X));
          if (connect(front, 1, cap1, pickups).empty())
            continue;
          stalks++;
          for (int od : {-X, Y, -Y, 1, -1, X}) {
            auto f = front;
            if (!add(f, {0, Observer, c + od}))
              continue;
            fronts++;
            set<int> hits;
            for (auto b : f)
              if (b.id == 0) {
                hits.insert(b.pos);
                if (glue(b.part))
                  for (int d : dirs)
                    hits.insert(b.pos + d);
              }
            for (int hit : hits) {
              int p = hit - 3 * X;
              auto b = f;
              if (!add(b, {1, Push, p}))
                continue;
              if (none_of(b.begin(), b.end(),
                          [&](Block k) { return k.id == 0 && k.pos == hit; }) &&
                  !add(b, {0, Glue, hit}))
                continue;
              set<Sites> seen;
              for (int variant = 0; variant < 3; variant++) {
                auto g = connect(b, 1, cap1, pickups, variant);
                if (g.empty())
                  break;
                sort(g.begin(), g.end());
                if (!seen.insert(g).second)
                  continue;
                auto q = b;
                for (int pos : g)
                  add(q, {1, Glue, pos});
                pushes++;
                close(q, c, p);
                if (count >= goal)
                  return;
              }
            }
          }
        }
  }
  void run(int extra, int observer) {
    plate = {{2, Center, 0},         {2, Observer, observer},
             {2, Hopper, Y},         {2, Hopper, 1},
             {2, Glue, X},           {2, Glue, X + Y},
             {2, Glue, X + 1},       {2, Glue, extra},
             {2, Sticky, X + Y + 1}, {3, Glue, Y + 1}};
    run_plate();
  }
  void run_plate() {
    ends_by_axis.clear();
    World base;
    for (auto b : plate)
      if (!add(base, b))
        return;
    Sites hs;
    for (int hx = x1 - int(stagger); hx <= x1 + int(stagger); hx++)
      for (int y = -4; y <= 4; y++)
        for (int z = -4; z <= 4; z++) {
          int h = pt(hx, y, z);
          if (side_pick(plate, 2, h - 2 * X) && legal(plate, {1, Hopper, h}) &&
              legal(plate, {1, Glue, h + X}))
            hs.push_back(h);
        }
    for (size_t i = 0; i < hs.size(); i++)
      for (size_t j = 0; j < i; j++)
        for (size_t k = 0; k < j; k++) {
          Sites h{hs[i], hs[j], hs[k]};
          if (none_of(h.begin(), h.end(), [&](int p) { return xc(p) == x1; }))
            continue;
          auto hardware = plate;
          bool ok = true;
          set<int> power;
          for (int p : h) {
            ok &= add(hardware, {1, Hopper, p}) &&
                  add(hardware, {1, Glue, p + X});
            for (int d : {Y, -Y, 1, -1})
              power.insert(p + d);
          }
          if (!ok)
            continue;
          for (int p : power)
            for (int q : power) {
              if (q < p)
                continue;
              if (any_of(h.begin(), h.end(), [&](int f) {
                    return (norm(f - p) != 1 || p == f + X) &&
                           (norm(f - q) != 1 || q == f + X);
                  }))
                continue;
              auto v = hardware;
              if (!add(v, {1, Red, p}) || !add(v, {1, Red, q}))
                continue;
              if (joint) {
                if (!connect(v, 1, cap1).empty()) {
                  cores++;
                  join_middle(v, h);
                }
                if (count >= goal)
                  return;
                continue;
              }
              set<Sites> alternatives;
              for (int variant = 0; variant < 8; variant++) {
                auto g = connect(v, 1, cap1, {}, variant);
                if (g.empty())
                  break;
                sort(g.begin(), g.end());
                if (!alternatives.insert(g).second)
                  continue;
                auto w = v;
                for (int pos : g)
                  add(w, {1, Glue, pos});
                int room = cap1 - int(g.size()) - 1 - int(p != q);
                cores++;
                grow(w, g, room);
                if (count >= goal)
                  return;
              }
            }
        }
  }
};
#ifndef BACK_LIBRARY
int main(int argc, char **argv) {
  if (argc != 8) {
    cerr << "back t0 t1 extra-index observer-index B1-cap max-rings output\n";
    return 2;
  }
  topology();
  pair_tables();
  Search s(atoi(argv[1]), atoi(argv[2]), atoi(argv[5]), atoi(argv[6]), argv[7]);
  array<int, 6> extras{X + 2 * Y, X + 2, X + Y - 1, X + 1 - Y, -1, -Y};
  array<int, 3> obs{-Y, -X, -1};
  s.run(extras.at(atoi(argv[3])), obs.at(atoi(argv[4])));
  cout << "cores " << s.cores << " stalks " << s.stalks << " fronts "
       << s.fronts << " pushes " << s.pushes << " joins " << s.joins
       << " routed " << s.count << "\n";
}

#endif
