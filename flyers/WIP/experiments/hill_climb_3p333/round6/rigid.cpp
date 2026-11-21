#include "route.hpp"
using namespace search;

int split_top = 0, split_bottom = 0;
struct Shape {
  World w;
  Sites glue, h;
};
bool united(const Sites &g) {
  set<int> pending(g.begin() + 1, g.end());
  Sites q{g[0]};
  for (size_t k = 0; k < q.size(); k++)
    for (int d : dirs)
      if (pending.erase(q[k] + d))
        q.push_back(q[k] + d);
  return pending.empty();
}
bool append(World &w, const World &other, int shift = 0) {
  for (auto b : other) {
    b.pos += shift;
    if (!add(w, b))
      return false;
  }
  return true;
}
vector<Shape> shapes(int id, Sites h, int cap) {
  vector<Shape> result;
  World w{{id, Center, 0}};
  Sites gs{0};
  int index = 0;
  for (int p : h) {
    Part kind =
        ((id == 1 ? split_top : split_bottom) >> index++) & 1 ? Loop : Hopper;
    if (!add(w, {id, kind, p}) || !add(w, {id, Glue, p + X}))
      return {};
    gs.push_back(p + X);
  }
  set<Sites> seen;
  auto grow = [&](auto &&self, World &b, Sites &g) -> void {
    Sites key = g;
    sort(key.begin(), key.end());
    if (!seen.insert(key).second)
      return;
    if (united(g))
      result.push_back({b, g, h});
    if (int(g.size()) == cap)
      return;
    set<int> extra;
    for (int p : g)
      for (int d : dirs)
        extra.insert(p + d);
    for (int p : extra) {
      if (find(g.begin(), g.end(), p) != g.end() || !add(b, {id, Glue, p}))
        continue;
      g.push_back(p);
      self(self, b, g);
      g.pop_back();
      b.pop_back();
    }
  };
  grow(grow, w, gs);
  return result;
}
Sites perimeter(const Shape &s, Part kind) {
  set<int> sites;
  for (int p : s.glue)
    for (int d : dirs)
      if (legal(s.w, {s.w[0].id, kind, p + d}))
        sites.insert(p + d);
  return {sites.begin(), sites.end()};
}
struct Cluster {
  int center, push, second, sticky;
};
vector<Cluster> clusters(const Shape &s, int id) {
  auto edge = perimeter(s, Push);
  set<int> powers;
  for (int p : edge)
    for (int d : dirs)
      if (d != X)
        powers.insert(p + d);
  vector<Cluster> result;
  for (int c : powers) {
    Sites ps, ss;
    for (int d : dirs)
      if (binary_search(edge.begin(), edge.end(), c + d)) {
        if (d != -X)
          ps.push_back(c + d);
        if (d != X && legal(s.w, {id, Sticky, c + d}))
          ss.push_back(c + d);
      }
    // Sticky and push can have different material clearance at the edge.
    for (int d : dirs)
      if (d != X && find(ss.begin(), ss.end(), c + d) == ss.end() &&
          legal(s.w, {id, Sticky, c + d}) &&
          any_of(s.glue.begin(), s.glue.end(),
                 [&](int g) { return norm(g - c - d) == 1; }))
        ss.push_back(c + d);
    for (int p : ps)
      for (int m : (id == 1 ? ss : ps))
        for (int z : ss) {
          if (p == m || m == z || p == z)
            continue;
          auto w = s.w;
          if (!add(w, {id, Push, p}) ||
              !add(w, {id, id == 1 ? Sticky : Push, m}) ||
              !add(w, {id, Sticky, z}))
            continue;
          result.push_back({c, p, m, z});
        }
  }
  return result;
}
struct Top {
  World w;
  Sites h;
  int red_rod, p_rod, s1_rod, s_bottom;
};
using HKey = array<int, 3>;
map<HKey, vector<Top>> tops;
bool opposite = false;
long topcount = 0, bottomcount = 0, catches = 0, meetings = 0, elbows = 0,
     rods = 0;
bool present(const World &w, int id, int p, bool hopper = true) {
  return any_of(w.begin(), w.end(), [&](Block b) {
    return b.id == id && b.pos == p &&
           (hopper || (b.part != Hopper && b.part != Loop));
  });
}
void make_tops(Sites h, int gcap) {
  for (auto &s : shapes(1, h, gcap)) {
    auto tri = clusters(s, 1);
    for (int red : perimeter(s, Red)) {
      World base = s.w;
      if (!add(base, {1, Red, red}))
        continue;
      for (int o : dirs) {
        auto core = base;
        if (!add(core, {1, Observer, o}))
          continue;
        for (auto t : tri) {
          auto w = core;
          if (!add(w, {1, Push, t.push}) || !add(w, {1, Sticky, t.second}) ||
              !add(w, {1, Sticky, t.sticky}) ||
              !add(w, {0, Red, t.center + 2 * X}))
            continue;
          bool target = false;
          for (int d : dirs)
            if (d != -X && present(w, 1, red + d + X))
              target = true;
          if (!target && !opposite)
            continue;
          for (auto &b : w)
            b.pos -= red;
          HKey key{h[0] - red, h[1] - red, h[2] - red};
          sort(key.begin(), key.end());
          tops[key].push_back({w,
                               {key.begin(), key.end()},
                               t.center + 2 * X - red,
                               t.push - red,
                               t.second - red,
                               t.sticky - red});
          topcount++;
        }
      }
    }
  }
}
bool relay(const World &made, int red, const Top &t, Cluster B, Sites h,
           int rcap, const char *path) {
  for (int d : dirs)
    if (d != -X) {
      int p = red + d;
      if (!present(made, 2, p + X))
        continue;
      World w = made;
      if (!add(w, {0, Push, p}))
        continue;
      bool valid = true;
      for (int target :
           {t.p_rod + 3 * X, t.s1_rod - X, B.second + 3 * X, B.sticky - X}) {
        if (!present(w, 0, target))
          valid &= add(w, {0, Glue, target});
      }
      if (!valid)
        continue;
      Groups pickups;
      for (int bp : h)
        if (!side_pick(w, 0, bp))
          pickups.push_back(neighbors(bp));
      rods++;
      auto g = connect(w, 0, rcap, pickups);
      if (g.empty())
        continue;
      for (int q : g)
        if (!add(w, {0, Glue, q}))
          return false;
      ofstream out(path);
      out << "3 " << rcap + 3 << "\n";
      for (int i = 0; i < 3; i++)
        out << i << " body " << i << " 0 " << rest[i] << " " << material[i]
            << "\n";
      for (auto b : w)
        out << b.id << " " << symbols[b.part] << " " << xc(b.pos) << " "
            << yc(b.pos) << " " << zc(b.pos) << "\n";
      return true;
    }
  return false;
}
bool join(const Shape &s, Cluster b, int pl, const char *path) {
  int shift = -2 * X - b.center;
  World base;
  if (!append(base, s.w, shift))
    return false;
  Cluster B{b.center + shift, b.push + shift, b.second + shift,
            b.sticky + shift};
  if (!add(base, {2, Push, B.push}) || !add(base, {2, Push, B.second}) ||
      !add(base, {2, Sticky, B.sticky}) || !add(base, {1, Red, 0}))
    return false;
  bottomcount++;
  Sites bh = s.h;
  for (int &p : bh)
    p += shift;
  for (auto &[key, options] : tops) {
    Sites missing;
    for (int h : key)
      if (!side_pick(base, 2, h - 2 * X))
        missing.push_back(h - 3 * X);
    // Any remaining spent hopper must be pushed forward by the one B red
    // block or the observer on B.
    if (missing.size() > 2)
      continue;
    for (int o : dirs) {
      auto co = base;
      int ob = o + shift;
      if (!add(co, {2, Observer, ob}))
        continue;
      Sites reds = perimeter(s, Red);
      for (int local : reds) {
        int r = local + shift;
        if (any_of(missing.begin(), missing.end(),
                   [&](int m) { return m != r && m != ob; }))
          continue;
        auto bw = co;
        if (!add(bw, {2, Red, r}))
          continue;
        catches++;
        for (auto &t : options) {
          if (!present(t.w, 1, B.push + 3 * X) ||
              !present(bw, 2, t.s_bottom - 3 * X, false))
            continue;
          meetings++;
          auto w = bw;
          if (!append(w, t.w))
            continue;
          elbows++;
          if (relay(w, r, t, B, bh, pl - 3, path))
            return true;
        }
      }
    }
  }
  return false;
}
#ifndef RIGID_LIBRARY
int main(int argc, char **argv) {
  if (argc != 6) {
    cerr << "rigid PL same-material-pair top-shape bottom-pair-index output\n";
    return 2;
  }
  int pl = atoi(argv[1]), same = atoi(argv[2]), top = atoi(argv[3]),
      bi = atoi(argv[4]);
  rigid_ring = true;
  topology();
  below[0] = 1;
  below[1] = 2;
  below[2] = 0;
  for (int id = 0; id < 3; id++)
    material[id] = (id == same);
  pair_tables();
  array<Sites, 3> th{{{Y, -Y, 1}, {Y, 1, X}, {Y, -Y, X}}};
  make_tops(th.at(top), pl - 8);
  cerr << "top layouts " << topcount << " in " << tops.size()
       << " hopper triples\n";
  Sites ds{Y, -Y, 1, -1, X};
  int k = 0;
  for (int i = 0; i < 5; i++)
    for (int j = 0; j < i; j++) {
      if (k++ != bi && bi >= 0)
        continue;
      for (auto &s : shapes(2, {ds[i], ds[j]}, pl - 8))
        for (auto b : clusters(s, 2)) {
          if (join(s, b, pl, argv[5]))
            goto done;
        }
    }
done:
  cout << "bottom clusters " << bottomcount << " pickups " << catches
       << " opposed actuator hits " << meetings << " compatible " << elbows
       << " rod routing calls " << rods << "\n";
}

#endif
