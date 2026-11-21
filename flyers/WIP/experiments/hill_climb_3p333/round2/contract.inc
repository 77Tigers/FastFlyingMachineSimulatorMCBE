void dump_contract(const char *path) {
  ifstream in(path);
  int ignored, li;
  in >> li >> ignored;
  string row;
  getline(in, row);
  vector<Cell> fixed;
  vector<set<int>> needed(li);
  vector<int> sticky(li);
  while (getline(in, row)) {
    istringstream line(row);
    int i, x, y, z;
    char kind;
    line >> i >> kind >> x >> y >> z;
    int p = pt(x, y, z);
    if (kind != 'G') {
      Kind k = kind == 'H' ? H : kind == 'S' ? S : R;
      fixed.push_back({p, i, k});
      if (k == H)
        needed[i].insert(p + X);
      if (k == S)
        sticky[i] = p;
    }
  }
  for (int i = 0; i < li; i++)
    needed[nextb(i)].insert(sticky[i] + (contact_dx(i) - 3) * X);
  for (int i = 0; i < li; i++)
    for (int p : needed[i])
      fixed.push_back({p, i, G});
  for (int i = 0; i < li; i++) {
    set<int> domain;
    // At the sticky pull, all three predecessor hoppers ride with this body.
    // A connected set of at most PL cells spans at most PL-1 axis steps in total.
    set<int> mandatory = needed[i];
    int prev = (i + li - 1) % li;
    for (auto c : fixed) {
      if (c.i == i && (c.k == R || c.k == S))
        mandatory.insert(c.p);
      if (c.i == prev && c.k == H)
        mandatory.insert(c.p + (contact_dx(prev) - 2) * X);
    }
    int lo[3] = {99, 99, 99}, hi[3] = {-99, -99, -99};
    for (int p : mandatory) {
      int a[] = {xc(p), yc(p), zc(p)};
      for (int d = 0; d < 3; d++) {
        lo[d] = min(lo[d], a[d]);
        hi[d] = max(hi[d], a[d]);
      }
    }
    int room = limit - 1 - (hi[0] - lo[0] + hi[1] - lo[1] + hi[2] - lo[2]);
    for (int x = lo[0] - room; x <= hi[0] + room; x++)
      for (int y = lo[1] - room; y <= hi[1] + room; y++)
        for (int z = lo[2] - room; z <= hi[2] + room; z++) {
          int extra = max({0, lo[0] - x, x - hi[0]}) + max({0, lo[1] - y, y - hi[1]}) +
                      max({0, lo[2] - z, z - hi[2]});
          if (extra <= room)
            domain.insert(pt(x, y, z));
        }
    for (int p : domain) {
      bool ok = true;
      for (auto c : fixed) {
        if (c.k == G && c.i == i && c.p == p)
          continue;
        if (forbidden(i, G, c.i, c.k, c.p - p)) {
          ok = false;
          break;
        }
      }
      if (ok)
        cout << i << ' ' << xc(p) << ' ' << yc(p) << ' ' << zc(p) << ' ' << needed[i].count(p)
             << '\n';
    }
  }
}
