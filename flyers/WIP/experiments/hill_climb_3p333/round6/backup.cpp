#include "route.hpp"
using namespace search;

struct RearSearch {
  World b2;
  int maxrings, count = 0, minx, maxx, middle_x = 3;
  long middles = 0, plates = 0, cores = 0, powered = 0, shells = 0,
       feasible = 0;
  ofstream out;
  map<tuple<int, int, int, int>, Sites> rear;
  set<vector<tuple<int, int, int>>> saved;
  RearSearch(int lo, int hi, int m, const char *path)
      : maxrings(m), minx(lo), maxx(hi), out(path) {}
  World gate(int i, int c, int u, int v, int o) {
    World w;
    for (auto [k, p] :
         {pair{Center, c}, pair{Hopper, c + u}, pair{Hopper, c + v},
          pair{Glue, c + u + X}, pair{Glue, c + v + X}, pair{Observer, c + o}})
      w.push_back({i, k, p});
    return w;
  }
  bool extend(World &w, const World &additions) {
    for (auto c : additions)
      if (!add(w, c))
        return false;
    return true;
  }
  // The mate's center must be reachable from B2's rear pickup.
  const Sites &rear_centers(int x, int u, int v, int o) {
    auto [it, fresh] = rear.try_emplace({x, u, v, o});
    if (fresh)
      for (int y = -5; y <= 5; y++)
        for (int z = -5; z <= 5; z++) {
          int c = pt(x, y, z);
          auto w = b2;
          if (extend(w, gate(3, c, turn(u, 2), turn(v, 2), turn(o, 2))) &&
              !connect(w, 3, 9).empty())
            it->second.push_back(c);
        }
    return it->second;
  }
  void close(const World &w, int c, int u, int v, int o, int p) {
    for (int center3 : rear_centers(xc(c), u, v, o)) {
      axis = c - turn(center3, 2);
      auto full = w;
      bool ok = true;
      for (auto b : w)
        if (!add(full, mirrored(b))) {
          ok = false;
          break;
        }
      if (!ok)
        continue;
      shells++;
      for (int donor : {0, 3})
        for (int d : {-X, Y, -Y, 1, -1}) {
          auto q = full;
          Block r{donor, Red, p + 2 * X + d};
          if (!add(q, r) || !add(q, mirrored(r)))
            continue;
          for (int variant = 0; variant < 4; variant++) {
            auto g = connect(q, 0, 10, {}, variant);
            if (g.empty())
              break;
            auto f = q;
            ok = true;
            for (int gp : g) {
              Block b{0, Glue, gp};
              if (!add(f, b) || !add(f, mirrored(b))) {
                ok = false;
                break;
              }
            }
            if (!ok)
              continue;
            vector<tuple<int, int, int>> result;
            for (auto b : f)
              result.emplace_back(b.id, b.part, b.pos);
            sort(result.begin(), result.end());
            if (!saved.insert(result).second)
              break;
            feasible++;
            out << "ring " << ++count << "\n";
            for (int i = 0; i < 6; i++) {
              int at = (i % 3 == 2   ? 0
                        : i % 3 == 1 ? middle_x
                                     : xc(c)) *
                           X +
                       (i >= 3 ? axis : 0);
              out << i << " origin " << xc(at) << " " << yc(at) << " " << zc(at)
                  << "\n";
            }
            for (auto [i, k, pos] : result)
              out << i << " " << symbols[k] << " " << xc(pos) << " " << yc(pos)
                  << " " << zc(pos) << "\n";
            out.flush();
            break;
          }
          if (count >= maxrings)
            return;
        }
    }
  }
  void front(const World &w) {
    set<int> hs, ps;
    for (auto b : w)
      if (b.id == 1) {
        if (glue(b.part))
          for (int d : dirs) {
            hs.insert(b.pos + 2 * X + d);
            ps.insert(b.pos + d);
          }
        if (b.part != Hopper)
          hs.insert(b.pos + 3 * X);
      }
    for (int h : hs)
      for (int u : {Y, -Y, 1, -1, X}) {
        int c = h - u;
        if (xc(c) < minx || xc(c) > maxx)
          continue;
        for (int v : {Y, -Y, 1, -1, X}) {
          if (u >= v || !hs.count(c + v))
            continue;
          for (int o : {Y, -Y, 1, -1, -X, X}) {
            auto f = w;
            if (!extend(f, gate(0, c, u, v, o)))
              continue;
            cores++;
            for (int p : ps) {
              int hit = p + 3 * X;
              if (norm(hit - c) > 3)
                continue;
              auto b = f;
              if (!add(b, {1, Push, p}))
                continue;
              if (none_of(b.begin(), b.end(),
                          [&](Block e) { return e.id == 0 && e.pos == hit; }) &&
                  !add(b, {0, Glue, hit}))
                continue;
              powered++;
              close(b, c, u, v, o, p);
              if (count >= maxrings)
                return;
            }
          }
        }
      }
  }
  void stalks(const World &w, int id, int cap) {
    set<Sites> base_routes;
    for (int var = 0; var < 3; var++) {
      auto gs = connect(w, id, cap, {}, var);
      if (gs.empty())
        return;
      sort(gs.begin(), gs.end());
      if (!base_routes.insert(gs).second)
        continue;
      World f = w;
      for (int p : gs)
        add(f, {id, Glue, p});
      int left = cap - int(gs.size()) -
                 count_if(w.begin(), w.end(),
                          [&](Block b) { return b.id == id && b.part == Red; });
      set<Sites> seen;
      auto grow = [&](auto &&self, World &q, int at, Sites &ext,
                      int n) -> void {
        Sites key = ext;
        sort(key.begin(), key.end());
        if (seen.insert(key).second) {
          plates++;
          front(q);
        }
        if (n <= 0 || count >= maxrings)
          return;
        for (int d : {-X, Y, -Y, 1, -1, X}) {
          int next = at + d;
          if (find(gs.begin(), gs.end(), next) != gs.end() ||
              find(ext.begin(), ext.end(), next) != ext.end())
            continue;
          size_t old = q.size();
          if (!add(q, {1, Glue, next}))
            continue;
          ext.push_back(next);
          self(self, q, next, ext, n - 1);
          ext.pop_back();
          q.resize(old);
          if (count >= maxrings)
            return;
        }
      };
      Sites ext;
      for (int p : gs) {
        grow(grow, f, p, ext, left);
        if (count >= maxrings)
          return;
      }
    }
  }
  void run(int sticky, int variant) {
    // Three hoppers on B2 share the glue opposite the center of the U.
    World w;
    for (int h : {-Y, -1, 1}) {
      add(w, {2, Hopper, h});
      add(w, {2, Glue, h + X});
    }
    for (int r : {-Y - 1, 1 - Y}) {
      add(w, {2, Red, r});
      add(w, {2, Glue, r + X});
    }
    if (!add(w, {2, Sticky, X + sticky}) || !add(w, {3, Glue, 0}) ||
        !add(w, {3, Glue, sticky}))
      return;
    seed(w, variant);
  }
  void seed(const World &w, int variant) {
    b2 = w;
    rear.clear();
    set<int> ps;
    for (auto b : w)
      if (b.id == 2 && glue(b.part))
        for (int d : dirs)
          ps.insert(b.pos + d);
    for (int y = -4; y <= 4; y++)
      for (int z = -4; z <= 4; z++)
        for (int u : {Y, -Y, 1, -1, X})
          for (int v : {Y, -Y, 1, -1, X}) {
            if (u >= v)
              continue;
            int c = pt(middle_x, y, z);
            if (!side_pick(w, 2, c + u - 2 * X) ||
                !side_pick(w, 2, c + v - 2 * X))
              continue;
            for (int o : {-Y, Y, -1, 1, -X, X}) {
              auto f = w;
              if (!extend(f, gate(1, c, u, v, o)))
                continue;
              for (int p : ps) {
                auto n = f;
                if (!add(n, {2, Push, p}))
                  continue;
                int hit = p + 3 * X;
                if (none_of(
                        n.begin(), n.end(),
                        [&](Block b) { return b.id == 1 && b.pos == hit; }) &&
                    !add(n, {1, Glue, hit}))
                  continue;
                for (int d : {-X, Y, -Y, 1, -1}) {
                  auto b = n;
                  if (!add(b, {1, Red, p + 2 * X + d}))
                    continue;
                  if (middles++ % 4 != variant)
                    continue;
                  stalks(b, 1, 10);
                  if (count >= maxrings)
                    return;
                }
              }
            }
          }
  }
};
#ifndef BACKUP_LIBRARY
int main(int argc, char **argv) {
  if (argc != 7) {
    cerr << "backup min-x max-x sticky-index shard max-rings output\n";
    return 2;
  }
  ordinary_back = 2;
  topology();
  pair_tables();
  array<int, 6> sticks{0, Y + 1, Y - 1, -2 * Y, 2, -2};
  RearSearch search(atoi(argv[1]), atoi(argv[2]), atoi(argv[5]), argv[6]);
  search.run(sticks.at(atoi(argv[3])), atoi(argv[4]));
  cout << "middle seeds " << search.middles << " plates " << search.plates
       << " cores " << search.cores << " armed " << search.powered
       << " clear halves " << search.shells << " closed " << search.count
       << "\n";
}

#endif
