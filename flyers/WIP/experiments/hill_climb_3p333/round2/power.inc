// All power blocks are chosen after placing the three hopping pistons and the sticky.
// A requirement is a piston and slot. On a failed firing order we branch on every
// source that could make one of the remaining hoppers fire in that slot.
using Mask = uint64_t;
using Orders = array<unsigned char, 6>;
struct Source {
  Cell cell;
  Mask bits;
  Orders bad;
  Cell hard;
};
const int permutations[][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
long long adequate = 0, leaves = 0;

struct PowerSearch {
  const vector<Pose> &poses;
  vector<Cell> cells;
  vector<Source> sources;
  vector<int> space;
  vector<int> selected;
  vector<Cell> structural;
  map<pair<int, vector<int>>, bool> fits_cache;
  bool fits(Cell candidate) {
    int i = candidate.i;
    vector<int> keys = {candidate.p};
    for (int u : selected)
      if (sources[u].cell.i == i)
        keys.push_back(sources[u].cell.p);
    sort(keys.begin(), keys.end());
    auto key = make_pair(i, keys);
    auto it = fits_cache.find(key);
    if (it != fits_cache.end())
      return it->second;
    auto world = structural;
    for (int p : keys)
      world.push_back({p, i, R});
    auto g = solve(i, poses, world, limit - 4 - keys.size());
    return fits_cache[key] = !g.empty();
  }
  long long attempts = 0;
  Mask sticky_bits = 0;
  vector<vector<int>> serving;
  int bit(int i, int slot, int h) { return 10 * i + slot * 3 + h; }
  Mask missing(int i, int slot, int spent, Mask have) {
    if (slot == 3)
      return 0;
    Mask options = 0, candidates = 0;
    for (int h = 0; h < 3; h++)
      if (!(spent & (1 << h))) {
        Mask m = Mask(1) << bit(i, slot, h);
        candidates |= m;
        if (have & m)
          options |= m;
      }
    if (!options)
      return candidates;
    for (int h = 0; h < 3; h++)
      if (options & (Mask(1) << bit(i, slot, h))) {
        Mask fail = missing(i, slot + 1, spent | (1 << h), have);
        if (fail)
          return fail;
      }
    return 0;
  }
  void visit(Mask have, vector<bool> &excluded) {
    if (++attempts > 20000)
      return;
    Orders bad{};
    for (int u : selected)
      for (int i = 0; i < length; i++)
        bad[i] |= sources[u].bad[i];
    for (int i = 0; i < length; i++) {
      if (bad[i] == 63)
        return;
      for (int k = 0; k < 6; k++)
        if (bad[i] & (1 << k)) {
          Mask path = 0;
          for (int slot = 0; slot < 3; slot++)
            path |= Mask(1) << bit(i, slot, permutations[k][slot]);
          if ((have & path) == path)
            return;
        }
    }

    vector<int> opts;
    bool found = false;
    auto consider = [&](Mask bits) {
      if (!bits)
        return true;
      vector<int> cand;
      while (bits) {
        int b = __builtin_ctzll(bits);
        bits &= bits - 1;
        for (int u : serving[b])
          if (!excluded[u] && space[sources[u].cell.i] > 0)
            cand.push_back(u);
      }
      if (cand.empty())
        return false;
      sort(cand.begin(), cand.end());
      cand.erase(unique(cand.begin(), cand.end()), cand.end());
      if (!found || cand.size() < opts.size()) {
        opts = move(cand);
        found = true;
      }
      return true;
    };
    for (int i = 0; i < length; i++) {
      Mask m = Mask(1) << (10 * i + 9);
      if (!(have & m) && !consider(m))
        return;
      if (!consider(missing(i, 0, 0, have)))
        return;
      // Each individual hopper must eventually fire. This also sees an unreachable late piston
      // early.
      for (int h = 0; h < 3; h++) {
        Mask a = 0;
        for (int slot = 0; slot < 3; slot++)
          a |= Mask(1) << bit(i, slot, h);
        if (!(have & a) && !consider(a))
          return;
      }
    }
    if (!found) {
      leaves++;
      vector<vector<int>> gl(length);
      auto n = cells.size();
      for (int i = 0; i < length; i++) {
        int count = 0;
        for (auto c : cells)
          count += c.i == i && c.k == R;
        gl[i] = solve(i, poses, cells, limit - 4 - count);
        if (gl[i].empty() || (bridge && !reaches(i, poses, cells, gl[i]))) {
          cells.resize(n);
          return;
        }
        for (int p : gl[i])
          cells.push_back({p, i, G});
      }
      cells.resize(n);
      powered++;
      routed++;
      output(poses, cells, gl);
      if ((max_output > 0 && routed >= max_output) || (max_output < 0 && routed >= -max_output))
        exit(0);
      return;
    }
    sort(opts.begin(), opts.end(), [&](int a, int b) {
      return __builtin_popcountll(sources[a].bits & ~have) >
             __builtin_popcountll(sources[b].bits & ~have);
    });
    for (int u : opts) {
      auto src = sources[u];
      bool ok = true, add_hard = src.hard.i >= 0;
      for (auto c : cells) {
        if (forbidden(c.i, c.k, src.cell.i, R, src.cell.p - c.p)) {
          ok = false;
          break;
        }
        if (add_hard) {
          if (c.i == src.hard.i && c.p == src.hard.p && c.k == G) {
            add_hard = false;
            continue;
          }
          if (forbidden(c.i, c.k, src.hard.i, G, src.hard.p - c.p)) {
            ok = false;
            break;
          }
        }
      }
      excluded[u] = true;
      if (ok && fits(src.cell)) {
        space[src.cell.i]--;
        size_t size = cells.size();
        cells.push_back(src.cell);
        if (add_hard)
          cells.push_back(src.hard);
        selected.push_back(u);
        visit(have | src.bits, excluded);
        selected.pop_back();
        cells.resize(size);
        space[src.cell.i]++;
      }
      if (attempts > 20000)
        break;
    }
    for (int u : opts)
      excluded[u] = false;
  }
  void run(const vector<const unordered_set<int> *> &taps, const vector<int> &slack,
           const vector<const unordered_set<int> *> &goals) {
    space = slack;
    serving.resize(10 * length);
    map<tuple<int, int, int, int, int>, Mask> hits;
    array<unordered_set<int>, 6> glue;
    for (int s = 0; s < 6; s++)
      for (auto c : cells)
        if (c.k == G)
          glue[s].insert(c.p + shift(c.i, s) * X);
    for (int j = 0; j < length; j++) {
      int r = 2 * (j % 3);
      for (int slot = 0; slot < 4; slot++)
        for (int h = 0; h < (slot == 3 ? 1 : 3); h++) {
          int s = (r + (slot == 3 ? 0 : slot + 2)) % 6,
              piston = poses[j].p + (slot == 3 ? X + shapes[poses[j].shape].pickup
                                               : shapes[poses[j].shape].p[h]);
          Mask bitmask = Mask(1) << (slot == 3 ? 10 * j + 9 : bit(j, slot, h));
          for (int face : dirs) {
            if (face == (slot == 3 ? -X : X))
              continue;
            int target = piston + face + shift(j, s) * X;
            for (int beam : {0, X, -X, Y, -Y, 1, -1}) {
              if (beam && !rods)
                continue;
              for (int i = 0; i < length; i++)
                if (space[i]) {
                  int red = target - beam - shift(i, s) * X;
                  if (!taps[i]->count(red - poses[i].p))
                    continue;
                  if (!beam || glue[s].count(target))
                    hits[{i, red, beam, -1, 0}] |= bitmask;
                  else if (conductor_mode) {
                    for (int owner : {i, j}) {
                      int q = target - shift(owner, s) * X;
                      if (goals[owner]->count(q - poses[owner].p))
                        hits[{i, red, beam, owner, q}] |= bitmask;
                    }
                  }
                }
            }
          }
        }
    }
    Mask all = 0;
    for (auto [key, mask] : hits) {
      auto [i, p, beam, owner, conductor] = key;
      bool ok = true;
      for (auto c : cells)
        if (forbidden(i, R, c.i, c.k, c.p - p)) {
          ok = false;
          break;
        }
      if (!ok)
        continue;
      if (owner >= 0) {
        if (forbidden(i, R, owner, G, conductor - p))
          continue;
        for (auto c : cells)
          if (forbidden(owner, G, c.i, c.k, c.p - conductor)) {
            ok = false;
            break;
          }
        if (!ok)
          continue;
        auto plain = hits.find({i, p, beam, -1, 0});
        if (plain != hits.end())
          mask |= plain->second;
      }
      if (beam) {
        auto q = hits.find({i, p, 0, -1, 0});
        if (q != hits.end())
          mask |= q->second;
      }
      Orders bad{};
      for (int s = 0; s < 6 && ok; s++) {
        int red = p + shift(i, s) * X, hard = red + beam;
        bool hot = beam &&
                   (glue[s].count(hard) || (owner >= 0 && hard == conductor + shift(owner, s) * X));
        auto on = [&](int target, int front) {
          return (norm(red - target) == 1 && red != target + front) ||
                 (hot && norm(hard - target) == 1 && hard != target + front);
        };
        for (int j = 0; j < length && ok; j++) {
          int m = local(j, s), base = poses[j].p + shift(j, s) * X;
          if (m != 0 && on(base + X + shapes[poses[j].shape].pickup, -X)) {
            ok = false;
            break;
          }
          for (int h = 0; h < 3; h++)
            for (int f = 2; f <= 4; f++) {
              if (m >= 2 && m <= f)
                continue;
              int delta = m == 1 || m == f + 1 ? -1 : -2;
              if (on(base + shapes[poses[j].shape].p[h] + delta * X, X))
                for (int k = 0; k < 6; k++)
                  if (permutations[k][f - 2] == h)
                    bad[j] |= 1 << k;
            }
          if (bad[j] == 63)
            ok = false;
        }
      }
      if (!ok)
        continue;
      int u = sources.size();
      sources.push_back({{p, i, R, beam}, mask, bad, {conductor, owner, G}});
      all |= mask;
      while (mask) {
        int b = __builtin_ctzll(mask);
        mask &= mask - 1;
        serving[b].push_back(u);
      }
    }
    for (int i = 0; i < length; i++) {
      bool matched = false;
      for (auto &perm : permutations) {
        Mask path = 0;
        for (int slot = 0; slot < 3; slot++)
          path |= Mask(1) << bit(i, slot, perm[slot]);
        matched |= (all & path) == path;
      }
      if (!(all & (Mask(1) << (10 * i + 9))) || !matched)
        return;
    }
    adequate++;
    structural = cells;
    vector<bool> excluded(sources.size());
    visit(0, excluded);
  }
};
