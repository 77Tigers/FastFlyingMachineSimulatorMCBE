// Side-contact tower placement on a routed six-body back ring.
#define main round2_main
#include "../round2/ring.cpp"
#undef main
#include <functional>
#include <random>

namespace tower {
constexpr int N = 18;
enum Part { Glue, Red, Hopper, Loop, Sticky };
struct Block {
  int id;
  Part part;
  int pos;
};
using Blocks = vector<Block>;
bool pull_towerless = false;
int column[N], level[N], rest[N], below[N], mate[N], loop_to[N], material[N],
    base[N];
int ids[4][6], axis, pl, loops;
int slot(int i, int s) { return (s - rest[i] + 6) % 6; }
bool moving(int i, int s) { return slot(i, s) >= 2; }
int displacement(int i, int s) {
  int x = 0;
  for (int k = 0; k < s; k++)
    x += moving(i, k);
  return x;
}
int hopper_count(int i) {
  return (level[i] == 0 ? pull_towerless || column[i] % 3 != 0 : level[i] == 1)
             ? 3
             : 4;
}
void topology() {
  int n = 0;
  for (int j = 0; j < 4; j++)
    for (int i = 0; i < 6; i++)
      if (!j || i % 3) {
        ids[j][i] = n;
        level[n] = j;
        column[n++] = i;
      }
  for (int i = 0; i < N; i++) {
    int c = column[i], l = level[i];
    rest[i] = (2 * (c - l + 6)) % 6;
    material[i] = (c + l) % 2;
    below[i] = l ? ids[l - 1][c] : (c + 1) % 6;
    mate[i] = ids[l][(c + 3) % 6];
    loop_to[i] = l && c % 3 == 1 ? ids[l][c + 1] : below[i];
  }
}
enum Mode { Solid, Ready, Spent, Extended, Arm, StickyArm };
struct Location {
  int dx, carrier;
  Mode mode;
};
vector<Location> states_at(int i, Part part, int s) {
  int m = slot(i, s), h = displacement(i, s);
  if (part == Sticky && m == 1)
    return {{h, i, Extended}, {h - 1, i, StickyArm}};
  if (part != Hopper && part != Loop)
    return {{h, i, Solid}};
  vector<Location> out;
  int last = hopper_count(i) + 1,
      carrier = part == Loop ? loop_to[i] : below[i];
  if (m >= 2 && m <= last)
    out.push_back({h, i, Ready});
  if ((m >= 3 && m <= last + 1) || (m == 0 && last == 5)) {
    out.push_back({h - 1, i, Extended});
    out.push_back({h, i, Arm});
  }
  if (m < 2 || m >= 4)
    out.push_back({h - (m == 1 ? 1 : 2), carrier, Spent});
  return out;
}
using Forbidden = array<uint8_t, 17 * 3 * 3>;
Forbidden bad[N][5][N][5];
int index(int dx, int dy, int dz) {
  return (dx + 8) * 9 + (dy + 1) * 3 + dz + 1;
}
void pair_tables() {
  for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++)
      for (Part a : {Glue, Red, Hopper, Loop, Sticky})
        for (Part b : {Glue, Red, Hopper, Loop, Sticky}) {
          auto &f = bad[i][a][j][b];
          for (int s = 0; s < 6; s++)
            for (auto u : states_at(i, a, s))
              for (auto v : states_at(j, b, s)) {
                auto ban = [&](int offset) {
                  int x = xc(offset) + u.dx - v.dx;
                  f[index(x, yc(offset), zc(offset))] = 1;
                };
                ban(0);
                for (int rev : {0, 1}) {
                  auto c = rev ? v : u, n = rev ? u : v;
                  Part p = rev ? b : a, q = rev ? a : b;
                  int host = rev ? j : i, other = rev ? i : j,
                      sign = rev ? -1 : 1;
                  bool passive = c.mode == Extended || c.mode == Arm ||
                                 c.mode == StickyArm;
                  bool neighbour_passive = n.mode == Extended ||
                                           n.mode == Arm || n.mode == StickyArm;
                  if (!passive && moving(c.carrier, s) &&
                      c.carrier != n.carrier) {
                    if (!(n.mode == StickyArm && below[other] == c.carrier))
                      ban(sign * X);
                    if (p == Glue && !neighbour_passive &&
                        (q != Glue || material[host] == material[other]))
                      for (int d : dirs)
                        ban(sign * d);
                  }
                  if (p == Sticky && c.mode == Solid && slot(host, s) == 0)
                    ban(-sign * X);
                  if (p != Red)
                    continue;
                  if ((q == Hopper || q == Loop) &&
                      (n.mode == Spent || (n.mode == Ready && host != other)))
                    for (int d : dirs)
                      if (d != -X)
                        ban(sign * d);
                  if (q == Sticky && n.mode != StickyArm && slot(other, s) != 0)
                    for (int d : dirs)
                      if (d != X)
                        ban(sign * d);
                }
              }
        }
}
bool conflict(Block a, Block b) {
  int d = b.pos - a.pos, x = xc(d), y = yc(d), z = zc(d);
  return abs(x) <= 8 && abs(y) <= 1 && abs(z) <= 1 &&
         bad[a.id][a.part][b.id][b.part][index(x, y, z)];
}
Block mirrored(Block b) { return {mate[b.id], b.part, turn(b.pos, 2) + axis}; }
struct Context {
  int body;
  const Blocks &world;
  map<pair<Part, int>, bool> memo;
  bool permits(Part part, int pos) {
    auto key = make_pair(part, pos);
    auto found = memo.find(key);
    if (found != memo.end())
      return found->second;
    Block b = {body, part, pos}, m = mirrored(b);
    bool ok = !conflict(b, m);
    for (auto c : world)
      if (ok && (conflict(b, c) || conflict(m, c)))
        ok = false;
    return memo[key] = ok;
  }
};
const int sides[] = {Y, -Y, 1, -1};
set<int> lanes(const Blocks &w, int body) {
  set<int> g;
  for (auto b : w)
    if (b.id == body && b.part == Glue && xc(b.pos) == base[body] + 1)
      g.insert(b.pos - (base[body] + 1) * X);
  return g;
}
int sticky_lane(const Blocks &w, int body) {
  for (auto b : w)
    if (b.id == body && b.part == Sticky)
      return b.pos - xc(b.pos) * X;
  return 999999;
}
bool adjacent(const set<int> &g, int lane) {
  for (int d : sides)
    if (g.count(lane + d))
      return true;
  return false;
}
vector<int> perimeter(const set<int> &g) {
  set<int> e;
  for (int p : g)
    for (int d : sides)
      if (!g.count(p + d))
        e.insert(p + d);
  return {e.begin(), e.end()};
}
void combinations(const vector<int> &a, int start, int count,
                  vector<int> &chosen, const function<void()> &fn) {
  if (!count) {
    fn();
    return;
  }
  for (int k = start; k + count <= (int)a.size(); k++) {
    chosen.push_back(a[k]);
    combinations(a, k + 1, count - 1, chosen, fn);
    chosen.pop_back();
  }
}
bool powered(int st, const set<int> &r) {
  return st != 999999 && adjacent(r, st);
}
int cell_budget(int i) {
  if (level[i] == 1)
    return pl - 1 - 4 - (column[i] % 3 == 2 ? loops : 0);
  if (level[i] == 2)
    return pl - 1 - 4;
  return pl - 3;
}
struct Option {
  Blocks cells;
  int score;
};
int node_limit = 90, choices = 40, layout_limit = 300;
array<long, 4> generated = {}, entered = {};
vector<Option> layouts(int i, const Blocks &w, mt19937 &rng) {
  Context ctx{i, w, {}};
  int j = level[i], bottom = below[i], x = base[i] * X;
  bool pull = j < 3;
  int lower_st = sticky_lane(w, bottom);
  auto floor = lanes(w, bottom);
  int send = (j == 1 && column[i] % 3 == 1) ? loops : 0;
  auto peer = send ? lanes(w, loop_to[i]) : set<int>{};
  int pickup_layer = send ? base[i] - 2 + displacement(i, rest[i]) -
                                displacement(loop_to[i], rest[i])
                          : 0;
  if (send && pickup_layer != base[loop_to[i]] + 1) {
    peer.clear();
    for (auto b : w)
      if (b.id == loop_to[i] && b.part == Glue && xc(b.pos) == pickup_layer)
        peer.insert(b.pos - pickup_layer * X);
  }
  auto eligible = [&](const set<int> &plane, Part k) {
    vector<int> list;
    for (int h : perimeter(plane))
      if (ctx.permits(k, x + h) && ctx.permits(Glue, x + X + h))
        list.push_back(h);
    return list;
  };
  auto m = eligible(floor, Hopper), l = eligible(peer, Loop);
  if ((int)m.size() < hopper_count(i) - send || (int)l.size() < send)
    return {};
  vector<int> stickies;
  if (!pull)
    stickies.push_back(999999);
  else
    for (int s : floor)
      if (ctx.permits(Sticky, x + X + s))
        stickies.push_back(s);
  if (stickies.empty())
    return {};
  shuffle(m.begin(), m.end(), rng);
  shuffle(l.begin(), l.end(), rng);
  vector<int> mh, lh;
  vector<Option> result;
  int budget = cell_budget(i);
  auto emit = [&]() {
    set<int> hs(mh.begin(), mh.end());
    hs.insert(lh.begin(), lh.end());
    if ((int)hs.size() != hopper_count(i))
      return;
    vector<int> rc;
    for (int v : perimeter(hs))
      if (ctx.permits(Red, x + v) && ctx.permits(Glue, x + X + v))
        rc.push_back(v);
    for (int nr = 1; nr <= 2; nr++) {
      vector<int> picked;
      bool minimal = false;
      combinations(rc, 0, nr, picked, [&]() {
        set<int> rs(picked.begin(), picked.end());
        for (int h : hs)
          if (!adjacent(rs, h))
            return;
        minimal = true;
        vector<int> power_positions;
        if (lower_st == 999999 || powered(lower_st, rs))
          power_positions = {999999};
        else {
          for (int d : sides)
            if (!hs.count(lower_st + d) && ctx.permits(Red, x + lower_st + d))
              power_positions.push_back(lower_st + d);
          if (ctx.permits(Red, x + X + lower_st))
            power_positions.push_back(X + lower_st);
        }
        for (int power : power_positions)
          for (int st : stickies) {
            set<int> g = hs;
            g.insert(rs.begin(), rs.end());
            if (st != 999999 && g.count(st))
              continue;
            int omit = st, extra = power != 999999;
            if (extra) {
              int lane = power - xc(power) * X;
              if (xc(power) == 0) {
                if (!ctx.permits(Glue, x + X + lane) || st == lane)
                  continue;
                g.insert(lane);
              } else {
                if (g.count(lane) || st == lane)
                  continue;
              }
            }
            if ((int)g.size() + nr + extra > budget)
              continue;
            // Grow a connected plate, with side contact to its sticky and any
            // plate-layer power block.
            auto legal_lane = [&](int p) {
              return p != omit && !(extra && power == p + X) &&
                     ctx.permits(Glue, x + X + p);
            };
            bool failed = false;
            for (int target :
                 {st, extra && xc(power) == 1 ? power - X : 999999}) {
              if (target == 999999 || adjacent(g, target))
                continue;
              int best = 999999, dist = 99;
              for (int d : sides)
                if (legal_lane(target + d))
                  for (int p : g)
                    if (norm(p - target - d) < dist) {
                      dist = norm(p - target - d);
                      best = target + d;
                    }
              if (best == 999999) {
                failed = true;
                break;
              }
              g.insert(best);
            }
            if (failed)
              continue;
            set<int> connected = {*g.begin()};
            while (connected.size() < g.size()) {
              vector<int> q(connected.begin(), connected.end());
              map<int, int> parent;
              for (int p : q)
                parent[p] = p;
              int hit = 999999;
              for (size_t n = 0; n < q.size() && hit == 999999; n++)
                for (int d : sides) {
                  int p = q[n] + d;
                  if (parent.count(p) || !legal_lane(p))
                    continue;
                  parent[p] = q[n];
                  if (g.count(p)) {
                    hit = p;
                    break;
                  }
                  if (norm(p - *g.begin()) <= 8)
                    q.push_back(p);
                }
              if (hit == 999999) {
                failed = true;
                break;
              }
              for (int p = hit; !connected.count(p); p = parent[p]) {
                g.insert(p);
                connected.insert(p);
              }
              if ((int)g.size() + nr + extra > budget) {
                failed = true;
                break;
              }
            }
            if (failed || (int)g.size() + nr + extra > budget)
              continue;
            Blocks cells;
            for (int h : mh)
              cells.push_back({i, Hopper, x + h});
            for (int h : lh)
              cells.push_back({i, Loop, x + h});
            for (int r : rs)
              cells.push_back({i, Red, x + r});
            if (extra)
              cells.push_back({i, Red, x + power});
            if (st != 999999)
              cells.push_back({i, Sticky, x + X + st});
            for (int v : g)
              cells.push_back({i, Glue, x + X + v});
            // Individual tests used the assembled world. Check within this
            // segment and against its mate.
            for (size_t a = 0; a < cells.size() && !failed; a++)
              for (size_t b = 0; b < cells.size(); b++) {
                if ((a < b && conflict(cells[a], cells[b])) ||
                    conflict(cells[a], mirrored(cells[b]))) {
                  failed = true;
                  break;
                }
              }
            if (!failed) {
              int score = 4 * ((int)g.size() + nr + extra) + (rng() % 24);
              result.push_back({cells, score});
            }
          }
      });
      if (minimal && nr == 1 && result.size() > 500)
        break;
    }
  };
  combinations(m, 0, hopper_count(i) - send, mh,
               [&]() { combinations(l, 0, send, lh, emit); });
  sort(result.begin(), result.end(),
       [](auto &a, auto &b) { return a.score < b.score; });
  generated[j] += result.size();
  if ((int)result.size() > layout_limit)
    result.resize(layout_limit);
  return result;
}
int order(int k) {
  // Placing the receiving tower first gives loop hoppers explicit glue to ride.
  return ids[1 + k / 2][(k % 2) ? 1 : 2];
}
bool build(int k, Blocks &w, mt19937 &rng, int &nodes) {
  if (k == 6)
    return true;
  if (nodes >= node_limit)
    return false;
  int i = order(k);
  entered[level[i]]++;
  nodes++;
  auto candidates = layouts(i, w, rng);
  int tried = 0;
  for (auto &l : candidates) {
    size_t old = w.size();
    for (auto b : l.cells) {
      w.push_back(b);
      w.push_back(mirrored(b));
    }
    if (build(k + 1, w, rng, nodes))
      return true;
    w.resize(old);
    if (++tried >= choices || nodes >= node_limit)
      break;
  }
  return false;
}
// Confirm all pairwise slot and sweep constraints on the complete ring,
// including mixed interfaces assembled by the two search stages.
bool checked(const Blocks &world) {
  for (size_t a = 0; a < world.size(); a++)
    for (size_t b = 0; b < a; b++)
      if (conflict(world[a], world[b]))
        return false;
  for (int s = 0; s < 6; s++) {
    set<int> red;
    for (auto b : world)
      if (b.part == Red)
        red.insert(b.pos + displacement(b.id, s) * X);
    for (auto b : world)
      if (b.part == Sticky) {
        int p = b.pos + displacement(b.id, s) * X;
        bool on = false;
        for (int d : dirs)
          if (d != -X && red.count(p + d))
            on = true;
        if (on != (slot(b.id, s) == 0))
          return false;
        if (slot(b.id, s) == 1) {
          bool pulls_glue = false;
          for (auto g : world)
            if (g.id == below[b.id] && g.part == Glue &&
                g.pos + displacement(g.id, s) * X == p - 2 * X)
              pulls_glue = true;
          if (!pulls_glue)
            return false;
        }
      }
  }
  return true;
}
struct Ring {
  Blocks cells;
  array<int, 6> origins;
};
vector<Ring> read_backs(const char *path) {
  ifstream in(path);
  if (!in)
    throw runtime_error("cannot read backs");
  vector<Ring> rows;
  string line;
  while (getline(in, line)) {
    istringstream s(line);
    string tag;
    s >> tag;
    if (tag == "ring") {
      rows.push_back({});
      continue;
    }
    int i = stoi(tag), x, y, z;
    string kind;
    s >> kind >> x >> y >> z;
    if (kind == "origin")
      rows.back().origins[i] = pt(x, y, z);
    else
      rows.back().cells.push_back({i,
                                   kind == "G"   ? Glue
                                   : kind == "R" ? Red
                                   : kind == "S" ? Sticky
                                                 : Hopper,
                                   pt(x, y, z)});
  }
  return rows;
}
} // namespace tower
int main(int argc, char **argv) {
  using namespace tower;
  if (argc != 8) {
    cerr << "towers backs PL loop-hoppers rng nodes options out\n";
    return 2;
  }
  pull_towerless = getenv("PULL_TOWERLESS") != nullptr;
  topology();
  pair_tables();
  auto rings = read_backs(argv[1]);
  pl = atoi(argv[2]);
  loops = atoi(argv[3]);
  mt19937 rng(atoi(argv[4]));
  node_limit = atoi(argv[5]);
  choices = atoi(argv[6]);
  int n = 0;
  shuffle(rings.begin(), rings.end(), rng);
  for (auto &r : rings) {
    n++;
    axis = r.origins[3];
    auto w = r.cells;
    for (int i = 0; i < N; i++) {
      int lo = below[i], s = rest[i];
      base[i] = level[i]
                    ? base[lo] + 3 + displacement(lo, s) - displacement(i, s)
                    : xc(r.origins[i]);
    }
    int nodes = 0;
    if (build(0, w, rng, nodes) && checked(w)) {
      ofstream out(argv[7]);
      out << N << " " << pl << "\n";
      for (int i = 0; i < N; i++)
        out << i << " body " << column[i] << " " << level[i] << " " << rest[i]
            << " " << material[i] << "\n";
      for (auto b : w)
        out << b.id << " " << "GRHLS"[b.part] << " " << xc(b.pos) << " "
            << yc(b.pos) << " " << zc(b.pos) << "\n";
      cout << "built ring " << n << " nodes " << nodes << "\n";
      return 0;
    }
  }
  cout << "searched " << n << " backs; tower calls/returned layouts by level";
  for (int j = 1; j < 4; j++)
    cout << " " << entered[j] << "/" << generated[j];
  cout << "\n";
  return 1;
}
