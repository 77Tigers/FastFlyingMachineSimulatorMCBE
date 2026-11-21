using TapKey = tuple<int, int, int, int>;
struct Tap {
  int red, beam, hard;
};
map<TapKey, vector<Tap>> tap_cache;
const vector<Tap> &fixed_taps(int i, int j, const vector<Pose> &ps,
                              const unordered_set<int> &profile, int edge_id) {
  auto p = ps[j];
  int rest = 2 * (j % 3),
      relative = p.p + X + shapes[p.shape].pickup + (shift(j, rest) - shift(i, rest)) * X - ps[i].p;
  TapKey key = {edge_id, p.shape, relative, 0};
  auto it = tap_cache.find(key);
  if (it != tap_cache.end())
    return it->second;
  vector<Tap> taps;
  for (int face : {X, Y, -Y, 1, -1}) {
    int receiver = X + shapes[p.shape].pickup + face;
    bool plate = false;
    for (int h : shapes[p.shape].p)
      plate |= h + X == receiver;
    for (int beam : {0, X, -X, Y, -Y, 1, -1}) {
      if (beam && !plate)
        continue;
      int red = relative + face - beam;
      if (profile.count(red))
        taps.push_back({red, beam, receiver});
    }
  }
  return tap_cache.emplace(key, move(taps)).first->second;
}
void fixed_rods(const vector<Pose> &ps, const vector<const unordered_set<int> *> &costs,
                const vector<int> &ids) {
  vector<vector<Socket>> opts(length);
  for (int j = 0; j < length; j++) {
    int before = (j + length - 1) % length;
    for (int k = 0; k < length; k += 3) {
      int i = (before + k) % length;
      auto &taps = fixed_taps(i, j, ps, *costs[i], ids[i]);
      for (auto t : taps) {
        int s = ps[j].p + X + shapes[ps[j].shape].pickup;
        opts[j].push_back({{s, j, S},
                           {s + (contact_dx(j) - 3) * X, nextb(j), G},
                           {ps[i].p + t.red, i, R, t.beam},
                           ps[j].p + t.hard});
      }
      if (length == 3)
        break;
    }
    if (opts[j].empty())
      return;
  }
  screened++;
  vector<Cell> cells;
  for (int i = 0; i < length; i++) {
    auto u = unit(i, ps[i]);
    if (conflict(cells, u))
      return;
    cells.insert(cells.end(), u.begin(), u.end());
  }
  rings++;
  map<pair<int, int>, bool> feasible;
  for (auto &options : opts) {
    vector<Socket> safe;
    for (auto o : options) {
      bool ok = true;
      auto r = o.power;
      for (auto c : cells) {
        if (c.i == r.i && c.p == r.p && c.k == R)
          continue;
        if (forbidden(c.i, c.k, r.i, R, r.p - c.p)) {
          ok = false;
          break;
        }
      }
      if (ok) {
        auto key = make_pair(r.i, r.p);
        if (!feasible.count(key)) {
          auto w = cells;
          bool exists = false;
          int red = 0;
          for (auto c : w)
            if (c.i == r.i && c.k == R) {
              red++;
              exists |= c.p == r.p;
            }
          if (!exists) {
            w.push_back(r);
            red++;
          }
          feasible[key] = !solve(r.i, ps, w, limit - 4 - red).empty();
        }
        if (feasible[key])
          safe.push_back(o);
      }
    }
    if (safe.empty())
      return;
    options.swap(safe);
  }
  try_sockets(ps, cells, opts, 0);
}
