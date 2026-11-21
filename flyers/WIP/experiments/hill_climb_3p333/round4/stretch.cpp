// Test PL14 back-ring handoffs with one hopper on a different X plane.
#define STAGGER_SCREEN
#include "back.cpp"

struct CorePose {
  Core c;
  bool staggered;
};
using Signature = array<vector<int>, 4>;

// Translate in YZ. The first cover also locates B2's sticky.
Signature signature(const Core &c, bool sticky) {
  int y = yc(c.hoppers.front()), z = zc(c.hoppers.front());
  for (int h : c.hoppers) {
    y = min(y, yc(h));
    z = min(z, zc(h));
  }
  Signature key = {c.hoppers, c.red, c.covers, {}};
  if (sticky)
    key[3].push_back(c.covers.front());
  for (auto &group : key) {
    for (auto &p : group)
      p -= pt(0, y, z);
    sort(group.begin(), group.end());
  }
  return key;
}

// Each site must remain next to the hoppers on its plane. Retain each
// inclusion-minimal subset of the template's power or pickup sites.
vector<vector<int>> port_sites(const vector<int> &ports, const vector<int> &sites) {
  vector<vector<int>> covers;
  for (int mask = 1; mask < (1 << sites.size()); mask++) {
    vector<int> used(sites.size());
    bool covered = true;
    for (int p : ports) {
      int count = 0, which = 0;
      for (size_t i = 0; i < sites.size(); i++)
        if ((mask & (1 << i)) && norm(p - sites[i]) == 1) {
          count++;
          which = i;
        }
      if (!count)
        covered = false;
      if (count == 1)
        used[which] = 1;
    }
    vector<int> subset;
    for (size_t i = 0; i < sites.size(); i++)
      if (mask & (1 << i)) {
        covered &= used[i] > 0;
        subset.push_back(sites[i]);
      }
    if (covered)
      covers.push_back(subset);
  }
  return covers;
}
vector<int> neighbours(int port) {
  return {port - Y, port - 1, port + 1, port + Y};
}
vector<CorePose> variants(vector<Core> cores, int body, int cap) {
  bool rotate = body != 0, sticky = body == 2;
  set<Signature> seen;
  vector<CorePose> all;
  auto add = [&](Core c, bool staggered) {
    for (size_t i = 0; i < (sticky ? c.covers.size() : 1); i++) {
      Core active = c;
      swap(active.covers.front(), active.covers[i]);
      for (int s = 0; s < (rotate ? 8 : 1); s++) {
        Core pose = oriented(active, s);
        auto key = signature(pose, sticky);
        if (!rotate)
          for (int rot = 1; rot < 8; rot++)
            key = min(key, signature(oriented(pose, rot), sticky));
        if (!seen.insert(key).second)
          continue;
        auto cells = hardware(body, pose, 0);
        if (legal(cells) && !glue_route(body, 99, cells, cap).empty())
          all.push_back({pose, staggered});
      }
    }
  };
  for (auto c : cores) {
    add(c, false);
    for (int single = 0; single < 3; single++)
      for (int step : {-2, -1, 1, 2}) {
        auto hp = c.hoppers;
        int lone = hp[single];
        hp.erase(hp.begin() + single);
        auto red = port_sites(hp, c.red), covers = port_sites(hp, c.covers);
        for (int n : neighbours(hp[0]))
          if (norm(n - hp[1]) == 1) {
            red.push_back({n});
            covers.push_back({n});
          }
        for (auto &r : red)
          for (auto &q : covers)
            for (int lone_red : neighbours(lone))
              for (int lone_cover : neighbours(lone)) {
                Core split{hp, r, q};
                split.hoppers.push_back(lone + step * X);
                split.red.push_back(lone_red + step * X);
                split.covers.push_back(lone_cover + step * X);
                add(split, true);
              }
      }
  }
  return all;
}

// Relative X is fixed. Compute the illegal YZ translations before routing.
vector<int> handoffs(int i, const Core &a, const Core &b, int t, int cap) {
  int j = nextb(i), x = t + contact_dx(i);
  auto prev = hardware(i, a, 0), next = hardware(j, b, x * X);
  constexpr int radius = 10, width = 2 * radius + 1;
  array<bool, width * width> banned{};
  for (auto u : prev)
    for (auto v : next) {
      int d = v.p - u.p;
      for (int dy = -1; dy <= 1; dy++)
        for (int dz = -1; dz <= 1; dz++) {
          int y = dy - yc(d), z = dz - zc(d);
          if (abs(y) > radius || abs(z) > radius)
            continue;
          if (u.k == G && v.k == G && u.i == v.i && d + pt(0, y, z) == 0)
            continue;
          if (forbidden(u.i, u.k, v.i, v.k, pt(xc(d), dy, dz)))
            banned[(y + radius) * width + z + radius] = true;
        }
    }
  auto bounds = [j](const vector<Cell> &cells, int (*axis)(int)) {
    pair<int, int> range{99, -99};
    for (auto v : cells)
      if (v.i == j && v.k == G) {
        range.first = min(range.first, axis(v.p));
        range.second = max(range.second, axis(v.p));
      }
    return range;
  };
  auto span = [](pair<int, int> a, pair<int, int> b, int shift) {
    return max(a.second, b.second + shift) - min(a.first, b.first + shift);
  };
  int room = cap - static_cast<int>(b.red.size()) - 1 - span(bounds(prev, xc), bounds(next, xc), 0);
  auto py = bounds(prev, yc), pz = bounds(prev, zc);
  auto ny = bounds(next, yc), nz = bounds(next, zc);
  vector<int> result;
  for (int y = -radius; y <= radius; y++)
    for (int z = -radius; z <= radius; z++) {
      if (span(py, ny, y) + span(pz, nz, z) > room ||
          banned[(y + radius) * width + z + radius])
        continue;
      vector<Cell> world = prev;
      for (auto v : next) {
        v.p += pt(0, y, z);
        world.push_back(v);
      }
      // Front plate depth varies with the split hopper's X.
      if (!glue_route(j, 99, world, cap).empty())
        result.push_back(pt(x, y, z));
    }
  return result;
}
int main() {
  length = 6;
  back_tables();
  // The independent handoff screen must recover the first saved PL15 ring.
  auto contains = [](const vector<int> &points, int target) {
    return find(points.begin(), points.end(), target) != points.end();
  };
  auto t = oriented(T, 2), a3c = oriented(A3c, 2);
  assert(contains(handoffs(0, O, t, 2, 12), pt(2, 3, 1)));
  assert(contains(handoffs(1, t, a3c, -3, 8), pt(-3, 2, 0)));
  assert(contains(handoffs(2, a3c, oriented(O, 2), -1, 12), pt(1, -1, -5)));

  vector<Core> templates{O, T, A3c};
  auto first = variants(templates, 0, 11);
  auto mid = variants(templates, 1, 11);
  auto last = variants(templates, 2, 7);
  cout << "poses " << first.size() << " " << mid.size() << " " << last.size() << endl;
  long pairs = 0, placements = 0, triangles = 0, clear = 0;
  map<tuple<int, int, int>, vector<int>> first_edges, last_edges;
  for (size_t b = 0; b < mid.size(); b++)
    for (size_t c = 0; c < last.size(); c++) {
      auto e1 = handoffs(1, mid[b].c, last[c].c, -3, 7);
      if (e1.empty())
        continue;
      pairs++;
      placements += e1.size();
      for (size_t a = 0; a < first.size(); a++) {
        if (!first[a].staggered && !mid[b].staggered && !last[c].staggered)
          continue;
        auto twin = oriented(first[a].c, 2);
        for (int t0 = -3; t0 <= 4; t0++) {
          auto key0 = make_tuple(a, b, t0), key2 = make_tuple(c, a, 1 - t0);
          if (!first_edges.count(key0))
            first_edges[key0] = handoffs(0, first[a].c, mid[b].c, t0, 11);
          auto &e0 = first_edges[key0];
          if (e0.empty())
            continue;
          if (!last_edges.count(key2))
            last_edges[key2] = handoffs(2, last[c].c, twin, 1 - t0, 11);
          for (int p : e0)
            for (int q : e1)
              for (int r : last_edges[key2]) {
                triangles++;
                int axis = p + q + r;
                vector<Cell> all;
                for (auto [i, core, at] : {tuple{0, first[a].c, 0}, tuple{1, mid[b].c, p},
                                          tuple{2, last[c].c, p + q}})
                  for (auto k : hardware(i, core, at)) {
                    all.push_back(k);
                    all.push_back({turn(k.p, 2) + axis, (k.i + 3) % 6, k.k});
                  }
                if (legal(all)) {
                  clear++;
                  if (clear < 5)
                    cout << "clear poses " << a << " " << b << " " << c << " t0 " << t0 << endl;
                }
              }
        }
      }
    }
  cout << "middle-to-last pairs " << pairs << " placements " << placements
       << " half-ring triples " << triangles << " collision-free rings " << clear << endl;
}
