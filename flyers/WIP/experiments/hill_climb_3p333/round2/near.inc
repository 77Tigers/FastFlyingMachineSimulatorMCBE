// Perturb the individual hoppers, pickup lane, and whole-body origin of
// the 55-block control. All three bodies may choose different perturbations.
void near_control(int radius) {
  shapes.clear();
  vector<vector<Pose>> sets(3);
  array<int, 3> centers = {0, pt(-1, 3, 1), pt(-2, 1, 3)};
  array<vector<int>, 3> ports = {vector<int>{-Y, -1, 1}, vector<int>{-Y, -1, Y},
                                 vector<int>{-Y, 1, Y}};
  if (length == 6) {
    centers[2] = pt(-2, 4, 4);
    ports[2] = {-Y, -1, Y};
  }
  for (int i = 0; i < 3; i++) {
    set<tuple<vector<int>, int, int>> seen;
    auto insert = [&](vector<int> h, int sticky, int delta) {
      sort(h.begin(), h.end());
      if (set<int>(h.begin(), h.end()).size() != 3 || !seen.insert({h, sticky, delta}).second)
        return;
      int shape = shapes.size();
      shapes.push_back({h, {}, sticky, "local"});
      Pose pose{shape, centers[i] + delta};
      auto cells = unit(i, pose);
      bool safe = true;
      for (size_t a = 0; a < cells.size(); a++)
        for (size_t b = a + 1; b < cells.size(); b++) {
          auto c = cells[a], v = cells[b];
          if (forbidden(c.i, c.k, v.i, v.k, v.p - c.p))
            safe = false;
        }
      if (safe)
        sets[i].push_back(pose);
    };
    insert(ports[i], 0, 0);
    for (int d : dirs) {
      insert(ports[i], d, 0);
      insert(ports[i], 0, d);
      for (int j = 0; j < 3; j++) {
        auto h = ports[i];
        h[j] += d;
        insert(h, 0, 0);
      }
    }
    if (radius >= 2) {
      for (int d : dirs)
        for (int e : dirs) {
          for (int j = 0; j < 3; j++) {
            auto h = ports[i];
            h[j] += d;
            insert(h, e, 0);
            insert(h, 0, e);
            if (d + e)
              h[j] += e;
            insert(h, 0, 0);
          }
        }
    }
  }
  vector<int> twins;
  int initial = shapes.size();
  for (int i = 0; i < initial; i++) {
    auto sh = shapes[i];
    for (auto &h : sh.p)
      h = turn(h, 2);
    sort(sh.p.begin(), sh.p.end());
    sh.pickup = turn(sh.pickup, 2);
    twins.push_back(shapes.size());
    shapes.push_back(sh);
  }
  auto twin = [&](Pose p) { return Pose{twins[p.shape], pt(0, 5, 7) + turn(p.p, 2)}; };
  map<EdgeKey, bool> valid;
  auto feasible = [&](int prev, Pose a, Pose b) {
    int i = nextb(prev);
    int d = b.p - a.p - contact_dx(prev) * X;
    EdgeKey key = {a.shape, b.shape, d};
    auto it = valid.find(key);
    if (it != valid.end())
      return it->second;
    auto c = unit(prev, a), n = unit(i, b);
    if (conflict(c, n))
      return valid[key] = false;
    c.insert(c.end(), n.begin(), n.end());
    vector<Pose> ps(length);
    ps[i] = b;
    ps[prev] = a;
    unordered_set<int> taps, goals, power;
    auto g = solve(i, ps, c, limit - 4, 0, &taps, &goals, &power);
    if (g.empty())
      return valid[key] = false;
    base_glue[key] = g[0];
    profiles[key] = move(taps);
    targets[key] = move(goals);
    extras[key] = move(power);
    return valid[key] = true;
  };
  cerr << "pose choices " << sets[0].size() << ' ' << sets[1].size() << ' ' << sets[2].size()
       << '\n';
  int slice = getenv("POSE_SLICE") ? atoi(getenv("POSE_SLICE")) : 0;
  int slices = getenv("POSE_SLICES") ? max(1, atoi(getenv("POSE_SLICES"))) : 1;
  for (size_t ai = slice; ai < sets[0].size(); ai += slices) {
    auto a = sets[0][ai];
    for (auto b : sets[1]) {
      if (!feasible(0, a, b))
        continue;
      for (auto c : sets[2]) {
        if (!feasible(1, b, c))
          continue;
        if (length == 3) {
          if (feasible(2, c, a))
            test({a, b, c});
        } else {
          auto d = twin(a), e = twin(b), f = twin(c);
          if (feasible(2, c, d) && feasible(3, d, e) && feasible(4, e, f) && feasible(5, f, a))
            test({a, b, c, d, e, f});
        }
      }
    }
  }
  cerr << "local rings=" << rings << " power-coverable=" << adequate
       << " complete wirings=" << leaves << " routed=" << routed << '\n';
}
