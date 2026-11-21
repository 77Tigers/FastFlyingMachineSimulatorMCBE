// Enumerate placements in the YZ plane. Each check covers six slot starts and every
// possible order of the three interchangeable hopping pistons.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>
#include <unordered_set>
#include <unordered_map>
using namespace std;
extern "C" int route(int, int, int, const int16_t *, const uint8_t *, const int16_t *, uint8_t *);
extern "C" int profile(int, int, int, const int16_t *, const uint8_t *, const int16_t *, uint8_t *);
constexpr int X = 4096, Y = 64;
int pt(int x, int y, int z) { return x * X + y * Y + z; }
int xc(int p) { return (p + 32 * Y + 32 + 32 * X) / X - 32; }
int yc(int p) { return (p - xc(p) * X + 32 + 32 * Y) / Y - 32; }
int zc(int p) { return p - xc(p) * X - yc(p) * Y; }
const int dirs[] = {X, -X, Y, -Y, 1, -1};
int norm(int p) { return abs(xc(p)) + abs(yc(p)) + abs(zc(p)); }
int turn(int p, int s) {
  int y = yc(p), z = zc(p);
  if (s & 4)
    z = -z;
  for (int j = 0; j < (s & 3); j++) {
    int k = y;
    y = -z;
    z = k;
  }
  return pt(xc(p), y, z);
}
int length = 3, limit = 17, pair_mask = 0;
bool unfixed_pickups = false, shared_leaves = false, conductor_mode = false, fixedrod = false,
     dark = false, bridge = false, dynamic_bridge = false, global_power = false,
     free_sticky = false, extra_power = false, rods = false;
int nextb(int i) { return (i + 1) % length; }
int local(int i, int s) { return (s + 6 - 2 * (i % 3)) % 6; }
int pulled(int i) { return (nextb(i) + ((pair_mask >> (i % 3) & 1) ? 3 : 0)) % length; }
bool moves(int i, int s) { return local(i, s) >= 2; }
int shift(int i, int s) {
  int dx = 0;
  for (int j = 0; j < s; j++)
    dx += moves(i, j);
  return dx;
}
int contact_dx(int i) {
  int s = 2 * (i % 3);
  return shift(i, s) - shift(nextb(i), s);
}
enum Kind { G, R, H, S, ARM, BUSY };
struct Cell {
  int p, i;
  Kind k;
  int direction = 0;
};
struct State {
  int dx, owner;
  Kind k;
  bool ready = false, removable = false;
};
vector<State> states(Kind k, int i, int s) {
  int m = local(i, s), h = shift(i, s);
  vector<State> v;
  if (k == S && m == 1)
    return {{h, i, BUSY}, {h - 1, i, ARM, false, true}};
  if (k != H)
    return {{h, i, k}};
  if (m >= 2 && m <= 4)
    v.push_back({h, i, H, true});
  if (m >= 3 && m <= 5) {
    v.push_back({h - 1, i, BUSY});
    v.push_back({h, i, ARM});
  }
  if (m == 0 || m == 1 || m >= 4)
    v.push_back({h - (m == 1 ? 1 : 2), nextb(i), H});
  return v;
}
// Pair rules use world-at-zero coordinates and a precomputed small displacement table.
using Table = array<uint8_t, 19 * 5 * 5>;
Table bans[12][4][12][4];
int bi(int x, int y, int z) { return ((x + 9) * 5 + y + 2) * 5 + z + 2; }
bool forbidden(int i, Kind a, int j, Kind b, int d) {
  int x = xc(d), y = yc(d), z = zc(d);
  return abs(x) <= 9 && abs(y) <= 2 && abs(z) <= 2 && bans[i][a][j][b][bi(x, y, z)];
}
void tables() {
  for (int i = 0; i < length; i++)
    for (int j = 0; j < length; j++)
      for (Kind a : {G, R, H, S})
        for (Kind b : {G, R, H, S}) {
          Table &ban = bans[i][a][j][b];
          ban.fill(0);
          for (int s = 0; s < 6; s++)
            for (auto u : states(a, i, s))
              for (auto v : states(b, j, s)) {
                int dx = v.dx - u.dx;
                auto block = [&](int x, int y, int z) {
                  x -= dx;
                  if (abs(x) <= 9)
                    ban[bi(x, y, z)] = 1;
                };
                block(0, 0, 0);
                auto movable = [](State u) { return u.k != ARM && u.k != BUSY; };
                for (int reverse : {0, 1}) {
                  auto c = reverse ? v : u, n = reverse ? u : v;
                  int owner = reverse ? j : i, other = reverse ? i : j, sign = reverse ? -1 : 1;
                  auto exclude = [&](int d) { block(sign * xc(d), sign * yc(d), sign * zc(d)); };
                  bool same = c.owner == n.owner;
                  bool share = shared_leaves && moves(c.owner, s) && moves(n.owner, s) &&
                               (c.k == R || n.k == R);
                  if (movable(c) && moves(c.owner, s) && !same && !share &&
                      !(n.removable && c.owner == pulled(n.owner)))
                    exclude(X);
                  if (c.k == G && moves(c.owner, s) && movable(n) && !same && !share &&
                      (n.k != G || (n.owner % 2) == (c.owner % 2)))
                    for (int d : dirs)
                      exclude(d);
                  if (!global_power && c.k == R &&
                      ((n.k == H && !n.ready) || (n.k == BUSY && (reverse ? a : b) == H)))
                    for (int d : dirs)
                      if (d != -X)
                        exclude(d);
                  if (c.k == R && (reverse ? a : b) == S && n.k != ARM && local(other, s) != 0)
                    for (int d : dirs)
                      if (d != X)
                        exclude(d);
                  if (c.k == S && local(owner, s) == 0)
                    exclude(-X); // Empty extension.
                }
              }
        }
}
struct Shape {
  vector<int> p, r;
  int pickup;
  string name;
  int sym = 0;
};
vector<Shape> shapes;
void addshape(Shape a) {
  for (int s = 0; s < 8; s++) {
    Shape b = a;
    b.sym = s;
    for (int &p : b.p)
      p = turn(p, s);
    for (int &r : b.r)
      r = turn(r, s);
    b.pickup = turn(b.pickup, s);
    sort(b.p.begin(), b.p.end());
    sort(b.r.begin(), b.r.end());
    bool dup = false;
    for (auto &c : shapes)
      if (c.p == b.p && c.r == b.r && c.pickup == b.pickup)
        dup = true;
    if (!dup)
      shapes.push_back(b);
  }
}
struct Pose {
  int shape, p;
};
vector<Cell> unit(int i, Pose p) {
  vector<Cell> c;
  auto &sh = shapes[p.shape];
  for (int h : sh.p) {
    c.push_back({p.p + h, i, H});
    c.push_back({p.p + h + X, i, G});
  }
  for (int r : sh.r)
    c.push_back({p.p + r, i, R});
  if (!free_sticky)
    c.push_back({p.p + X + sh.pickup, i, S});
  if (!unfixed_pickups)
    c.push_back({p.p + sh.pickup - 2 * X + contact_dx(i) * X, nextb(i), G});
  return c;
}
bool conflict(const vector<Cell> &a, const vector<Cell> &b) {
  for (auto u : a)
    for (auto v : b)
      if (forbidden(u.i, u.k, v.i, v.k, v.p - u.p))
        return true;
  return false;
}
struct Edge {
  int a, b, d, t;
};
map<tuple<int, int>, vector<Edge>> edges;
int lower_bound_dist(Shape &a, Shape &b, int d) {
  int best = 99;
  for (int h : b.p)
    best = min(best, norm(d + h + X - (a.pickup - 2 * X)));
  return best;
}
vector<int> redsites(int i, int j, Pose host) { // Source carried by i, sticky attached to j.
  int s = 2 * (j % 3);
  int at = host.p + X + (shift(j, s) - shift(i, s)) * X;
  return {at + Y, at - Y, at + 1, at - 1, at + X};
}
vector<int> sources(int i, int j, Pose host, const vector<Cell> &cells) {
  vector<int> good;
  for (int p : redsites(i, j, host)) {
    bool existing = false, ok = true;
    for (auto c : cells) {
      if (c.k == R && c.i == i && p == c.p) {
        existing = true;
        continue;
      }
      if (forbidden(i, R, c.i, c.k, c.p - p)) {
        ok = false;
        break;
      }
    }
    if (ok) {
      good.push_back(p);
      if (existing)
        return {p};
    }
  }
  return good;
}
vector<int> offsets;
void build_edges(int reach) {
  for (int a = 0; a < (int)shapes.size(); a++)
    for (int b = 0; b < (int)shapes.size(); b++)
      for (int t : offsets)
        for (int y = -reach; y <= reach; y++)
          for (int z = -reach; z <= reach; z++) {
            int d = pt(t, y, z);
            if (lower_bound_dist(shapes[a], shapes[b], d) > limit - 6)
              continue;
            auto c = unit(0, {a, 0}), n = unit(1, {b, d});
            if (conflict(c, n))
              continue;
            edges[{a, t}].push_back({a, b, d, t});
          }
}
struct Sites {
  vector<int> required;
  vector<vector<int>> groups;
};
Sites terminals(int i, const vector<Pose> &poses, const vector<Cell> &cells) {
  Sites req;
  for (auto c : cells)
    if (c.i == i) {
      if (c.k == G)
        req.required.push_back(c.p);
      if (c.k == R || c.k == S) {
        vector<int> g;
        if (bridge)
          g.push_back(c.p);
        else
          for (int d : dirs)
            g.push_back(c.p + d);
        req.groups.push_back(g);
      }
    }
  int prev = (i + length - 1) % length;
  for (int h : shapes[poses[prev].shape].p) {
    int spent = poses[prev].p + h + (contact_dx(prev) - 2) * X;
    req.groups.push_back({spent - X, spent + Y, spent - Y, spent + 1, spent - 1});
  }
  return req;
}
struct Grid {
  vector<int> points;
  map<int, int> index;
  vector<int16_t> links, members;
  vector<uint8_t> cost;
  int groups = 0;
};
vector<int> solve(int i, const vector<Pose> &poses, const vector<Cell> &cells, int budget,
                  int variant = 0, unordered_set<int> *taps = nullptr,
                  unordered_set<int> *targets = nullptr, unordered_set<int> *extras = nullptr) {
  unordered_set<int> hardware;
  if (bridge) {
    for (auto c : cells)
      if (c.i == i && (c.k == S || c.k == R))
        hardware.insert(c.p);
    if (dynamic_bridge) {
      int prev = (i + length - 1) % length;
      for (int h : shapes[poses[prev].shape].p)
        hardware.insert(poses[prev].p + h + (contact_dx(prev) - 2) * X);
      for (int h : shapes[poses[i].shape].p)
        hardware.insert(poses[i].p + h);
    }
  }
  Sites terms = terminals(i, poses, cells);
  set<int> req(terms.required.begin(), terms.required.end());
  vector<vector<int>> groups;
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
  for (auto &g : terms.groups) {
    bool met = false;
    for (int p : g)
      met |= req.count(p) > 0;
    if (!met)
      groups.push_back(g);
  }
  if (int(req.size()) > budget)
    return {};
  int x0 = 99, y0 = 99, z0 = 99, x1 = -99, y1 = -99, z1 = -99;
  for (auto &g : groups)
    for (int p : g) {
      x0 = min(x0, xc(p));
      x1 = max(x1, xc(p));
      y0 = min(y0, yc(p));
      y1 = max(y1, yc(p));
      z0 = min(z0, zc(p));
      z1 = max(z1, zc(p));
    }
  Grid gr;
  for (int x = x0 - 1; x <= x1 + 1; x++)
    for (int y = y0 - 1; y <= y1 + 1; y++)
      for (int z = z0 - 1; z <= z1 + 1; z++) {
        int p = pt(x, y, z);
        bool ok = true;
        for (auto c : cells) {
          if (c.k == G && c.i == i && c.p == p)
            continue;
          if (forbidden(i, G, c.i, c.k, c.p - p)) {
            ok = false;
            break;
          }
        }
        if (ok || hardware.count(p))
          gr.points.push_back(p);
        else if (req.count(p))
          return {};
      }
  if (variant & 1)
    reverse(gr.points.begin(), gr.points.end());
  if (gr.points.empty() || gr.points.size() > 2048)
    return {};
  for (int p : gr.points) {
    int id = gr.index.size();
    gr.index[p] = id;
    gr.cost.push_back(!req.count(p) && !hardware.count(p));
  }
  gr.members.assign(gr.points.size(), 0);
  for (auto &g : groups) {
    bool legal = false;
    for (int p : g)
      if (gr.index.count(p)) {
        gr.members[gr.index[p]] |= 1 << gr.groups;
        legal = true;
      }
    if (!legal)
      return {};
    gr.groups++;
  }
  if (gr.groups > 14)
    return {};
  for (int p : gr.points)
    for (int d : dirs) {
      auto it = gr.index.find(p + d);
      gr.links.push_back(it == gr.index.end() || (d != -X && hardware.count(p + d)) ? -1
                                                                                    : it->second);
    }
  vector<uint8_t> selected(gr.points.size());
  int n =
      (taps ? profile : route)(gr.points.size(), gr.groups, budget - req.size(), gr.links.data(),
                               gr.cost.data(), gr.members.data(), selected.data());
  if (n == 100)
    return {};
  if (taps) {
    for (int k = 0; k < (int)gr.points.size(); k++)
      if (int(selected[k]) + int(req.size()) <= budget - (free_sticky ? 0 : 1)) {
        for (int d : dirs)
          taps->insert(gr.points[k] + d - poses[i].p);
        if (targets)
          targets->insert(gr.points[k] - poses[i].p);
        if (extras && int(selected[k]) + int(req.size()) < budget)
          for (int d : dirs)
            extras->insert(gr.points[k] + d - poses[i].p);
      }
    for (auto c : cells)
      if (c.k == R && c.i == i)
        taps->insert(c.p - poses[i].p);
    return {n + int(req.size())};
  }
  vector<int> out;
  for (int k = 0; k < (int)gr.points.size(); k++)
    if (!hardware.count(gr.points[k]) && (selected[k] || !gr.cost[k]))
      out.push_back(gr.points[k]);
  return out;
}
using EdgeKey = tuple<int, int, int>;
map<EdgeKey, unordered_set<int>> profiles, targets, extras;
map<EdgeKey, int> base_glue, edge_ids;
long long screened = 0;
long long rings = 0, powered = 0, routed = 0;
int max_output = 5;
bool cross = false;
string outbase;
pair<int, int> bestscore = {999, 999};
void output(const vector<Pose> &poses, const vector<Cell> &cells, const vector<vector<int>> &glue) {
  if (max_output < 0) {
    int hot = 0, sum = 0;
    for (int i = 0; i < length; i++) {
      int load = 4 + glue[i].size();
      for (auto c : cells)
        load += (c.i == i && c.k == R);
      sum += load;
      hot += max(0, load - 17);
    }
    pair<int, int> score = {hot, sum};
    if (score >= bestscore)
      return;
    bestscore = score;
  }
  string path = outbase + "_" + to_string(routed) + ".txt";
  ofstream out(path);
  out << length << ' ' << limit << '\n';
  for (int i = 0; i < length; i++) {
    int total = 4;
    for (auto c : cells)
      if (c.i == i && c.k != G) {
        out << i << ' ' << "GRHS"[c.k] << ' ' << xc(c.p) << ' ' << yc(c.p) << ' ' << zc(c.p);
        if (c.direction)
          out << ' ' << xc(c.direction) << ' ' << yc(c.direction) << ' ' << zc(c.direction);
        out << '\n';
        total += c.k == R;
      }
    for (int p : glue[i])
      out << i << " G " << xc(p) << ' ' << yc(p) << ' ' << zc(p) << '\n';
    cerr << ' ' << total + glue[i].size();
  }
  cerr << " -> " << path << '\n';
}
void full_route(const vector<Pose> &poses, vector<Cell> &cells, int source, int variant = 0) {
  if (source < length) {
    int j = nextb(source);
    vector<pair<int, int>> choices;
    for (int i : {source, (source + 3) % length}) {
      if (!choices.empty() && i == source)
        break;
      if (i != source && !cross)
        continue;
      for (int p : sources(i, j, poses[j], cells))
        choices.push_back({i, p});
      if (length == 3)
        break;
    }
    for (auto [i, p] : choices) {
      bool has = false;
      for (auto c : cells)
        if (c.i == i && c.k == R && c.p == p)
          has = true;
      if (!has)
        cells.push_back({p, i, R});
      full_route(poses, cells, source + 1, variant);
      if (!has)
        cells.pop_back();
    }
    return;
  }
  powered++;
  vector<vector<int>> gl(length);
  auto original = cells.size();
  for (int k = 0; k < length; k++) {
    int i = (k + variant) % length;
    int red = 0;
    for (auto c : cells)
      red += c.i == i && c.k == R;
    gl[i] = solve(i, poses, cells, limit - 4 - red, variant);
    if (gl[i].empty()) {
      cells.resize(original);
      return;
    }
    for (int p : gl[i])
      cells.push_back({p, i, G});
  }
  cells.resize(original);
  ++routed;
  output(poses, cells, gl);
  if ((max_output > 0 && routed >= max_output) || (max_output < 0 && routed >= -max_output))
    exit(0);
}
struct Socket {
  Cell sticky, pickup, power;
  int conductor = 0;
};
void try_sockets(const vector<Pose> &poses, vector<Cell> &cells,
                 const vector<vector<Socket>> &options, int i) {
  if (i == length) {
    full_route(poses, cells, length);
    return;
  }
  for (auto socket : options[i]) {
    size_t size = cells.size();
    bool blocked = false;
    vector<Cell> add = {socket.sticky, socket.pickup, socket.power};
    if (socket.power.direction)
      add.push_back({socket.conductor, socket.sticky.i, G});
    for (auto v : add) {
      bool duplicate = false;
      for (auto c : cells) {
        if (c.i == v.i && c.k == v.k && (v.k == G || v.k == R || v.k == S) && c.p == v.p) {
          if (c.direction && v.direction && c.direction != v.direction) {
            blocked = true;
            break;
          }
          duplicate = true;
          continue;
        }
        if (forbidden(c.i, c.k, v.i, v.k, v.p - c.p)) {
          blocked = true;
          break;
        }
      }
      if (blocked)
        break;
      if (!duplicate)
        cells.push_back(v);
    }
    if (!blocked) {
      int prev = 0;
      bool changed_direction = false;
      if (socket.power.direction)
        for (auto &c : cells)
          if (c.k == R && c.i == socket.power.i && c.p == socket.power.p) {
            changed_direction = true;
            prev = c.direction;
            c.direction = socket.power.direction;
            break;
          }
      try_sockets(poses, cells, options, i + 1);
      if (changed_direction)
        for (auto &c : cells)
          if (c.k == R && c.i == socket.power.i && c.p == socket.power.p)
            c.direction = prev;
    }
    cells.resize(size);
  }
}
#include "fixedrod.inc"
#include "motion.inc"
#include "power.inc"
void test(const vector<Pose> &poses) {
  vector<const unordered_set<int> *> costs, goals, powers;
  vector<int> slack, ids;
  for (int i = 0; i < length; i++) {
    int prev = (i + length - 1) % length;
    int d = poses[i].p - poses[prev].p - contact_dx(prev) * X;
    auto it = profiles.find({poses[prev].shape, poses[i].shape, d});
    if (it == profiles.end())
      return;
    costs.push_back(&it->second);
    if (fixedrod)
      ids.push_back(edge_ids.at(it->first));
    goals.push_back(&targets.at(it->first));
    powers.push_back(&extras.at(it->first));
    slack.push_back(limit - 4 - base_glue.at(it->first));
  }
  if (fixedrod) {
    fixed_rods(poses, costs, ids);
    return;
  }
  if (dark) {
    vector<Cell> cells;
    for (int i = 0; i < length; i++) {
      auto u = unit(i, poses[i]);
      if (conflict(cells, u))
        return;
      cells.insert(cells.end(), u.begin(), u.end());
    }
    rings++;
    full_route(poses, cells, length);
    return;
  }
  if (global_power) {
    vector<Cell> cells;
    for (int i = 0; i < length; i++) {
      auto u = unit(i, poses[i]);
      if (conflict(cells, u))
        return;
      cells.insert(cells.end(), u.begin(), u.end());
    }
    rings++;
    PowerSearch ps{poses, cells};
    ps.run(costs, slack, goals);
    return;
  }
  if (free_sticky) {
    vector<vector<Socket>> options(length);
    for (int j = 0; j < length; j++) {
      int prev = (j + length - 1) % length;
      int victim = pulled(j);
      int s = 2 * (j % 3);
      for (int donor : {prev, (prev + 3) % length}) {
        for (int tg : *goals[victim]) {
          int pickup = tg + poses[victim].p, sticky = pickup - (contact_dx(j) - 3) * X;
          if (!costs[j]->count(sticky - poses[j].p))
            continue;
          for (int face : {X, Y, -Y, 1, -1}) {
            int conductor = sticky + face;
            for (int beam : {0, X, -X, Y, -Y, 1, -1}) {
              if (beam && (!rods || !goals[j]->count(conductor - poses[j].p)))
                continue;
              int power = conductor - beam + (shift(j, s) - shift(donor, s)) * X,
                  rel = power - poses[donor].p;
              auto &rs = shapes[poses[donor].shape].r;
              if (find(rs.begin(), rs.end(), rel) == rs.end() &&
                  !(extra_power && powers[donor]->count(rel)))
                continue;
              options[j].push_back(
                  {{sticky, j, S}, {pickup, victim, G}, {power, donor, R, beam}, conductor});
            }
          }
        }
        if (length == 3)
          break;
      }
      if (options[j].empty())
        return;
    }
    screened++;
    vector<Cell> cells;
    for (int i = 0; i < length; i++) {
      auto u = unit(i, poses[i]);
      if (conflict(cells, u))
        return;
      cells.insert(cells.end(), u.begin(), u.end());
    }
    rings++;
    try_sockets(poses, cells, options, 0);
    return;
  }
  for (int j = 0; j < length; j++) {
    int prev = (j + length - 1) % length;
    bool found = false;
    for (int i : {prev, (prev + 3) % length}) {
      for (int p : redsites(i, j, poses[j]))
        if (costs[i]->count(p - poses[i].p)) {
          found = true;
          break;
        }
      if (found || !cross)
        break;
    }
    if (!found)
      return;
  }
  screened++;
  vector<Cell> cells;
  for (int i = 0; i < length; i++) {
    auto u = unit(i, poses[i]);
    if (conflict(cells, u))
      return;
    cells.insert(cells.end(), u.begin(), u.end());
  }
  rings++;
  for (int j = 0; j < length; j++) {
    int i = (j + length - 1) % length;
    if (sources(i, j, poses[j], cells).empty() &&
        (!cross || sources((i + 3) % length, j, poses[j], cells).empty()))
      return;
  }
  full_route(poses, cells, 0);
}
int rotated_shape(int s, int q) {
  Shape &a = shapes[s];
  vector<int> p, r;
  for (int h : a.p)
    p.push_back(turn(h, q));
  for (int h : a.r)
    r.push_back(turn(h, q));
  sort(p.begin(), p.end());
  sort(r.begin(), r.end());
  for (int i = 0; i < (int)shapes.size(); i++)
    if (shapes[i].p == p && shapes[i].r == r)
      return i;
  abort();
}
#include "general.inc"
#include "twin.inc"
int twin_reach = 0;
void search(vector<int> ts, int fold) {
  vector<Pose> ap(length);
  for (auto &entry : edges) {
    vector<Edge> viable;
    for (auto e : entry.second) {
      auto c = unit(0, {e.a, 0}), b = unit(1, {e.b, e.d});
      c.insert(c.end(), b.begin(), b.end());
      ap[0] = {e.a, 0};
      ap[1] = {e.b, e.d};
      if (!global_power && !free_sticky && !cross && sources(0, 1, ap[1], c).empty())
        continue;
      unordered_set<int> taps, goals, power;
      auto g = solve(1, ap, c, limit - 4 - shapes[e.b].r.size(), 0, &taps, &goals, &power);
      if (g.empty())
        continue;
      edge_ids[{e.a, e.b, e.d}] = edge_ids.size();
      base_glue[{e.a, e.b, e.d}] = g[0];
      profiles[{e.a, e.b, e.d}] = move(taps);
      targets[{e.a, e.b, e.d}] = move(goals);
      extras[{e.a, e.b, e.d}] = move(power);
      viable.push_back(e);
    }
    entry.second.swap(viable);
  }
  int total = 0;
  map<int, int> by_t;
  for (auto &e : edges) {
    total += e.second.size();
    by_t[get<1>(e.first)] += e.second.size();
  }
  cerr << "links " << total;
  for (auto [t, n] : by_t)
    cerr << " t=" << t << ":" << n;
  cerr << '\n';
  if (twin_reach) {
    twins(ts, twin_reach);
    return;
  }
  if (ts.size() == 6) {
    general(ts);
    return;
  }
  for (int a = 0; a < (int)shapes.size(); a++) {
    if (shapes[a].sym)
      continue;
    int mate = rotated_shape(a, fold);
    for (auto e : edges[{a, ts[0]}])
      for (auto f : edges[{e.b, ts[1]}]) {
        if (length == 3) {
          if (profiles.count({f.b, a, -2 * X - e.d - f.d}))
            test({{a, 0}, {e.b, e.d}, {f.b, e.d + f.d}});
          continue;
        }
        for (auto g : edges[{f.b, ts[2]}]) {
          if (g.b != mate)
            continue;
          int mid = e.d + f.d + g.d + 2 * X;
          if (length == 3 && mid != 0)
            continue;
          vector<Pose> p = {{a, 0}, {e.b, e.d}, {f.b, e.d + f.d}};
          if (length > 3) {
            int sum = 0;
            for (int j = 0; j < length / 3; j++)
              sum = mid + turn(sum, fold);
            if (sum)
              continue;
            for (int i = 0; i < length - 3; i++)
              p.push_back({rotated_shape(p[i].shape, fold), mid + turn(p[i].p, fold)});
          }
          test(p);
        }
      }
  }
  cerr << "complete screened=" << screened << " rings=" << rings << " power assignments=" << powered
       << " power-coverable=" << adequate << " complete-wirings=" << leaves << " routed=" << routed
       << '\n';
}
#include "stagger.inc"
#include "near.inc"
#include "contract.inc"
int main(int argc, char **argv) {
  if (argc < 9) {
    cerr << "ring L PL t0 t1 family reach outstem count [power-mode [topology ...]]\n";
    return 1;
  }
  length = atoi(argv[1]);
  limit = atoi(argv[2]);
  int t0 = atoi(argv[3]), t1 = atoi(argv[4]);
  string fam = argv[5];
  int reach = atoi(argv[6]);
  outbase = argv[7];
  max_output = atoi(argv[8]);
  const string mode = argc > 9 ? argv[9] : "direct";
  const string topology = argc > 10 ? argv[10] : "";
  const set<string> modes = {"direct", "cross",  "fixedrod", "dark",      "free",   "extra",
                             "rod",    "global", "beam",     "conductor", "bridge", "dynamic"};
  if (!modes.count(mode) || (length != 3 && length != 6 && length != 12) || fam.empty()) {
    cerr << "Expected a supported power mode, a core family, and 3, 6 or 12 bodies.\n";
    return 2;
  }
  cross = mode != "direct";
  fixedrod = mode == "fixedrod";
  dark = mode == "dark";
  free_sticky = mode == "free" || mode == "extra" || mode == "rod";
  extra_power = mode == "extra" || mode == "rod";
  unfixed_pickups = free_sticky && getenv("FREE_PICKUPS") != nullptr;
  bridge = mode == "bridge" || mode == "dynamic";
  dynamic_bridge = mode == "dynamic";
  conductor_mode = mode == "conductor";
  global_power = bridge || conductor_mode || mode == "global" || mode == "beam";
  rods = mode == "rod" || (global_power && mode != "global");
  if ((global_power && length > 6) || (topology == "general" && (length != 6 || argc < 17)) ||
      ((topology == "swap" || topology == "twins") && (length != 6 || argc < 12)) ||
      (topology == "dump" && argc < 12) || (topology == "near" && !global_power) ||
      (topology == "stagger" && length != 3)) {
    cerr << "This mode and topology require different arguments or body count.\n";
    return 2;
  }
  if (fam == "M" || fam == "T")
    addshape({{1, Y, Y + 2}, {Y + 1}, 0, "T"});
  if (fam == "M" || fam == "O")
    addshape({{-Y, -1, 1}, {-Y - 1, -Y + 1}, 0, "O"});
  if (fam == "A")
    addshape({{-Y, -1, 1}, {-Y - 1, Y + 1}, 0, "A"});
  if (fam == "B")
    addshape({{-Y, -1, 1}, {-Y - 1, 2}, 0, "B"});
  if (fam == "F")
    addshape({{-Y, -1, 1 + X}, {-Y - 1, X + 2}, 0, "F"});
  if (fam == "L")
    addshape({{Y, 1, Y + 1}, {0, 2 * Y + 1}, Y + 2, "L"});
  if (global_power) {
    shapes.clear();
    if (fam == "O" || fam == "M")
      addshape({{-Y, -1, 1}, {}, 0, "O"});
    if (fam == "T" || fam == "M")
      addshape({{1, Y, Y + 2}, {}, 0, "T"});
    if (fam == "L")
      addshape({{Y, 1, Y + 1}, {}, 0, "L"});
    if (fam == "F")
      addshape({{-Y, -1, 1 + X}, {}, 0, "F"});
    if (fam == "N")
      addshape({{-Y, -1, 1}, {}, -X, "N"});
    if (fam == "D")
      addshape({{-Y, -1, 1}, {}, -2 * X, "D"});
    if (fam == "J")
      addshape({{-Y, -1, 1}, {}, X, "J"});
    if (fam == "C")
      addshape({{Y, 1, Y + 1}, {}, -X, "C"});
    if (fam == "P")
      addshape({{Y, 1, X}, {}, Y + 1, "P"});
    if (fam == "Q")
      addshape({{Y, 1, X}, {}, -X - Y, "Q"});
    if (fam == "I")
      addshape({{Y, Y + 1, Y + 2}, {}, 1, "I"});
    if (fam[0] == 'v') {
      int edge, x, y, z;
      if (sscanf(fam.c_str(), "v%d_%d_%d_%d", &edge, &x, &y, &z) != 4)
        return 2;
      addshape({{Y, edge ? 1 : -Y, pt(x, y, z)}, {}, 0, "user"});
    }
    if (fam == "Z")
      addshape({{-Y, -1, 1 - X}, {}, 0, "Z"});
  }
  shared_leaves = getenv("ALLOW_SHARED_RED") != nullptr;
  if (shapes.empty()) {
    cerr << "Unknown core family for this mode.\n";
    return 2;
  }
  if (topology == "twins")
    twin_reach = atoi(argv[11]);
  if (topology == "swap")
    pair_mask = atoi(argv[11]);
  tables();
  if (topology == "stagger") {
    stagger();
    return 0;
  }
  if (topology == "dump") {
    dump_contract(argv[11]);
    return 0;
  }
  if (topology == "near") {
    near_control(argc > 11 ? atoi(argv[11]) : 1);
    return 0;
  }
  vector<int> ts = {t0, t1, -2 - t0 - t1};
  if (topology == "general") {
    if (argc > 17)
      pattern = argv[17];
    if (!pattern.empty() && pattern.size() != 6) {
      cerr << "Expected six core names.\n";
      return 2;
    }
    for (int k = 0; k < 6; k++)
      if (k < 3)
        ts[k] = atoi(argv[11 + k]);
      else
        ts.push_back(atoi(argv[11 + k]));
  }
  offsets = ts;
  sort(offsets.begin(), offsets.end());
  offsets.erase(unique(offsets.begin(), offsets.end()), offsets.end());
  build_edges(reach);
  search(ts, length > 3
                 ? (argc > 10 && isdigit(argv[10][0]) ? atoi(argv[10]) : (length == 12 ? 1 : 2))
                 : 0);
}
