// Join two three-link paths by their displacement and end module. The second
// half has its own orientations, offsets and transverse coordinates.
string pattern;
bool pattern_ok(int i, int shape) { return pattern.empty() || shapes[shape].name[0] == pattern[i]; }
void general(const vector<int> &ts) {
  using Half = array<Edge, 3>;
  using Key = pair<int, int>;
  long long joined = 0;
  for (int start = 0; start < (int)shapes.size(); start++) {
    if (shapes[start].sym || !pattern_ok(0, start))
      continue;
    map<Key, vector<Half>> first;
    for (auto a : edges[{start, ts[0]}])
      for (auto b : edges[{a.b, ts[1]}])
        for (auto c : edges[{b.b, ts[2]}])
          if (pattern_ok(1, a.b) && pattern_ok(2, b.b) && pattern_ok(3, c.b))
            first[{c.b, a.d + b.d + c.d + 2 * X}].push_back({a, b, c});
    for (int m = 0; m < (int)shapes.size(); m++)
      for (auto d : edges[{m, ts[3]}])
        for (auto e : edges[{d.b, ts[4]}])
          for (auto f : edges[{e.b, ts[5]}]) {
            if (f.b != start || !pattern_ok(3, m) || !pattern_ok(4, d.b) || !pattern_ok(5, e.b))
              continue;
            int mid = -d.d - e.d - f.d - 2 * X;
            auto it = first.find({m, mid});
            if (it == first.end())
              continue;
            for (auto &abc : it->second) {
              auto a = abc[0], b = abc[1];
              vector<Pose> poses = {{start, 0}, {a.b, a.d},       {b.b, a.d + b.d},
                                    {m, mid},   {d.b, mid + d.d}, {e.b, mid + d.d + e.d}};
              joined++;
              test(poses);
            }
          }
  }
  cerr << "general closures=" << joined << " profiled=" << screened << " rings=" << rings
       << " complete wirings=" << leaves << " routed=" << routed << '\n';
}
