// Search the six back bodies in their slot-zero world coordinates.
#define main round2_main
#include "../round2/ring.cpp"
#undef main
#include <numeric>
#include <random>


struct Core {
  vector<int> hoppers, red, covers;
};
Core A3c = {{0, Y + 1, Y + 2}, {Y, 2 * Y + 2}, {1, 2}};
Core T = {{1, Y, Y + 2}, {Y + 1}, {0, 2}};
Core O = {{-Y, -1, 1}, {-Y - 1, -Y + 1}, {0}};
Core oriented(Core c, int sym) {
  for (auto list : {&c.hoppers, &c.red, &c.covers})
    for (auto &p : *list)
      p = turn(p, sym);
  return c;
}
vector<Cell> hardware(int i, const Core &c, int origin) {
  vector<Cell> cells;
  for (int h : c.hoppers) {
    cells.push_back({origin + h, i, H});
    cells.push_back({origin + h + X, i, G});
  }
  for (int r : c.red)
    cells.push_back({origin + r, i, R});
  if (i % 3 == 2)
    cells.push_back({origin + X + c.covers.front(), i, S});
  for (int q : c.covers)
    cells.push_back({origin + q + (contact_dx(i) - 2) * X, nextb(i), G});
  return cells;
}
// Enforce power isolation between ready hoppers and foreign redstone blocks.
void back_tables() {
  tables();
  for (int i = 0; i < 6; i++)
    for (int j = 0; j < 6; j++)
      for (Kind a : {G, R, H})
        for (Kind b : {G, R, H})
          for (int s = 0; s < 6; s++) {
            for (auto u : states(a, i, s))
              for (auto v : states(b, j, s)) {
                auto ban = [&](int d) {
                  int dx = xc(d) + u.dx - v.dx;
                  bans[i][a][j][b][bi(dx, yc(d), zc(d))] = 1;
                };
                ban(0);
                for (int reverse : {0, 1}) {
                  auto c = reverse ? v : u, n = reverse ? u : v;
                  int sign = reverse ? -1 : 1;
                  bool same = c.owner == n.owner;
                  if (c.k != ARM && c.k != BUSY && moves(c.owner, s) && !same) {
                    ban(sign * X);
                    if (c.k == G && n.k != ARM && n.k != BUSY &&
                        (n.k != G || (n.owner % 2) == (c.owner % 2)))
                      for (int d : dirs)
                        ban(sign * d);
                  }
                  if (c.k == R && n.k == H && (!n.ready || i != j))
                    for (int d : dirs)
                      if (d != -X)
                        ban(sign * d);
                }
              }
          }
}
bool allowed(Cell u, const vector<Cell> &v) {
  for (auto c : v) {
    if (c.k == G && u.k == G && c.i == u.i && c.p == u.p)
      continue;
    if (forbidden(u.i, u.k, c.i, c.k, c.p - u.p))
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
      if (forbidden(a.i, a.k, b.i, b.k, b.p - a.p))
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
      if (c.k == G)
        req.insert(c.p);
      if (c.k == R)
        reds.push_back(c.p);
      if (c.k == S)
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
  if (body % 3)
    high[0] = min(high[0], xbase);
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
vector<Handoff> links(int i, const Core &a, const Core &b, int t, int cap) {
  vector<Handoff> out;
  auto h = hardware(i, a, 0);
  int j = nextb(i);
  for (int y = -10; y <= 10; y++)
    for (int z = -10; z <= 10; z++) {
      int delta = pt(t + contact_dx(i), y, z);
      auto n = hardware(j, b, delta), cells = h;
      cells.insert(cells.end(), n.begin(), n.end());
      if (!legal(cells))
        continue;
      auto g = glue_route(j, xc(delta), cells, cap);
      if (!g.empty())
        out.push_back({delta, g});
    }
  return out;
}
#ifndef STAGGER_SCREEN
int main(int argc, char **argv) {
  if (argc != 10 || (string(argv[1]) != "0" && string(argv[1]) != "1")) {
    cerr << "back sticky-index t0 t1 t2 cap0 cap1 cap2 output max-witnesses\n";
    return 2;
  }
  if (string(argv[1]) == "1")
    swap(A3c.covers[0], A3c.covers[1]);
  length = 6;
  back_tables();
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
  map<tuple<int, int, int>, vector<Handoff>> cache;
  auto edge = [&](int i, Core a, int sa, Core b,
                  int sb) -> const vector<Handoff> & {
    auto key = make_tuple(i, sa, sb);
    if (!cache.count(key))
      cache[key] = links(i, oriented(a, sa), oriented(b, sb), offsets[i],
                         caps[nextb(i) % 3]);
    return cache[key];
  };
  // Translate-equivalent orientations have the same available links.
  auto orientations = [](const Core &core) {
    set<array<vector<int>, 3>> seen;
    vector<int> result;
    for (int s = 0; s < 8; s++) {
      Core c = oriented(core, s);
      int my = 99, mz = 99;
      for (int p : c.hoppers) {
        my = min(my, yc(p));
        mz = min(mz, zc(p));
      }
      array<vector<int>, 3> sig = {c.hoppers, c.red, c.covers};
      for (auto &v : sig) {
        for (int &p : v)
          p -= pt(0, my, mz);
        sort(v.begin(), v.end());
      }
      if (seen.insert(sig).second)
        result.push_back(s);
    }
    return result;
  };
  auto s1s = orientations(T), s2s = orientations(A3c);
  for (int s1 : s1s)
    for (int s2 : s2s) {
      auto &e0 = edge(0, O, 0, T, s1);
      if (e0.empty())
        continue;
      auto &e2 = edge(2, A3c, s2, O, 2);
      if (e2.empty())
        continue;
      auto &e1 = edge(1, T, s1, A3c, s2);
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
            array<Core, 6> cores = {O,
                                    oriented(T, s1),
                                    oriented(A3c, s2),
                                    oriented(O, 2),
                                    oriented(T, (s1 & 4) | ((s1 + 2) % 4)),
                                    oriented(A3c, (s2 & 4) | ((s2 + 2) % 4))};
            vector<Cell> cells;
            for (int i = 0; i < 6; i++) {
              auto h = hardware(i, cores[i], at[i]);
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
                world.push_back(h);
                world.push_back(mate);
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
                out << i << " " << ("GRHS"[k]) << " " << xc(p) << " " << yc(p)
                    << " " << zc(p) << "\n";
              out.flush();
            }
            if (save > 0 && routed == save)
              goto done;
          }
    }
done:
  array<long, 3> singles = {};
  for (auto &[k, ls] : cache)
    singles[get<0>(k)] += ls.size();
  cout << "links " << singles[0] << " " << singles[1] << " " << singles[2]
       << " combinations " << tested << " clear " << clear << " routed "
       << routed << " saved " << min<long long>(routed, save) << "\n";
}
#endif
