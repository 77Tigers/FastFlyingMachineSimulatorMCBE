// Place a hopper next to the rod which times the next body's sticky. This
// substitutes one dual-purpose source for a separate high-level hopper RB.
void stagger() {
  shapes.clear();
  array<vector<Pose>, 3> opts;
  int s[3] = {X, pt(0, 3, 1), pt(-1, 1, 3)};
  int high[3] = {pt(2, 1, 1), pt(1, 2, 2), pt(1, 0, 2)}, beam[3] = {Y, 1, -1};
  vector<vector<int>> old = {{-Y, -1, 1},
                             {pt(-1, 2, 1), pt(-1, 3, 0), pt(-1, 4, 1)},
                             {pt(-2, 0, 3), pt(-2, 1, 4), pt(-2, 2, 3)}};
  vector<int> conductor(3);
  for (int i = 0; i < 3; i++) {
    int j = nextb(i), stage = j * 2;
    conductor[j] = high[i] + beam[i] + (shift(i, stage) - shift(j, stage)) * X;
  }
  auto module = [&](int i, Pose pose) {
    auto cells = unit(i, pose);
    bool present = false;
    for (auto &c : cells) {
      if (c.k == R && c.p == high[i])
        c.direction = beam[i];
      if (c.k == G && c.i == i && c.p == conductor[i])
        present = true;
    }
    if (!present)
      cells.push_back({conductor[i], i, G});
    return cells;
  };
  for (int i = 0; i < 3; i++) {
    set<int> lows;
    for (int h : old[i])
      for (int d : {Y, -Y, 1, -1})
        lows.insert(h + d);
    for (int low : lows) {
      if (low == high[i])
        continue;
      vector<int> ports;
      for (int r : {low, high[i]})
        for (int d : {Y, -Y, 1, -1})
          ports.push_back(r + d);
      sort(ports.begin(), ports.end());
      ports.erase(unique(ports.begin(), ports.end()), ports.end());
      for (int a = 0; a < (int)ports.size(); a++)
        for (int b = 0; b < a; b++)
          for (int c = 0; c < b; c++) {
            vector<int> h = {ports[c], ports[b], ports[a]};
            int upper = 0;
            for (int p : h)
              upper += xc(p) == xc(high[i]);
            if (upper == 3)
              continue;
            int shape = shapes.size();
            shapes.push_back({h, {low, high[i]}, s[i] - X, "stagger"});
            Pose pose{shape, 0};
            auto u = module(i, pose);
            bool legal = true;
            for (size_t k = 0; k < u.size(); k++)
              for (size_t l = 0; l < k; l++)
                if (forbidden(u[k].i, u[k].k, u[l].i, u[l].k, u[l].p - u[k].p))
                  legal = false;
            if (legal)
              opts[i].push_back(pose);
          }
    }
  }
  cerr << "stagger choices";
  for (auto &g : opts)
    cerr << ' ' << g.size();
  cerr << '\n';
  map<pair<int, int>, bool> memo;
  auto edge = [&](int i, Pose a, Pose b) {
    auto key = make_pair(a.shape, b.shape);
    if (memo.count(key))
      return memo[key];
    int j = nextb(i);
    auto aa = module(i, a), bb = module(j, b);
    if (conflict(aa, bb))
      return memo[key] = false;
    aa.insert(aa.end(), bb.begin(), bb.end());
    vector<Pose> ps(3);
    ps[i] = a;
    ps[j] = b;
    return memo[key] = !solve(j, ps, aa, limit - 6).empty();
  };
  for (auto a : opts[0])
    for (auto b : opts[1]) {
      if (!edge(0, a, b))
        continue;
      for (auto c : opts[2]) {
        if (!edge(1, b, c) || !edge(2, c, a))
          continue;
        vector<Pose> ps = {a, b, c};
        vector<Cell> cells;
        for (int i = 0; i < 3; i++) {
          auto u = module(i, ps[i]);
          cells.insert(cells.end(), u.begin(), u.end());
        }
        rings++;
        for (int v = 0; v < 3; v++)
          full_route(ps, cells, 3, v);
      }
    }
  cerr << "stagger rings=" << rings << " routed=" << routed << '\n';
}
