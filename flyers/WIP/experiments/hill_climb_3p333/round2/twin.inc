// Two stickies resting in the same slot can take the same pulse. Place their
// modules close enough to share a donor and join three pairs into a six-link ring.
struct PairPose {
  int a, b, delta;
};
struct PairEdge {
  int to, d;
};
void twins(const vector<int> &ts, int reach) {
  vector<PairPose> pairs;
  map<tuple<int, int, int>, int> index;
  int ns = shapes.size();
  for (int a = 0; a < ns; a++)
    for (int b = 0; b < ns; b++)
      for (int y = -reach; y <= reach; y++)
        for (int z = -reach; z <= reach; z++) {
          int d = pt(0, y, z);
          if (norm(d) > reach || !d)
            continue;
          auto u = unit(0, {a, 0}), v = unit(3, {b, d});
          if (conflict(u, v))
            continue;
          index[{a, b, d}] = pairs.size();
          pairs.push_back({a, b, d});
        }
  vector<map<pair<int, int>, vector<PairEdge>>> graph(3);
  long long links = 0;
  for (int k = 0; k < 3; k++)
    for (int i = 0; i < (int)pairs.size(); i++) {
      auto a = pairs[i];
      for (auto e : edges[{a.a, ts[k]}])
        for (int j = 0; j < (int)pairs.size(); j++) {
          auto b = pairs[j];
          if (b.a != e.b || !profiles.count({a.b, b.b, e.d + b.delta - a.delta}))
            continue;
          auto p = unit(0, {a.a, 0}), q = unit(3, {a.b, a.delta}), r = unit(1, {b.a, e.d}),
               s = unit(4, {b.b, e.d + b.delta});
          if (conflict(p, s) || conflict(q, r))
            continue;
          graph[k][{i, j}].push_back({j, e.d});
          links++;
        }
    }
  cerr << "paired clusters " << pairs.size() << " paired links " << links << '\n';
  long long closed = 0;
  for (int i = 0; i < (int)pairs.size(); i++) {
    auto a = pairs[i];
    if (shapes[a.a].sym)
      continue;
    auto it = index.find({a.b, a.a, -a.delta});
    if (it == index.end())
      continue;
    int end = it->second;
    for (int j = 0; j < (int)pairs.size(); j++)
      for (auto e : graph[0][{i, j}]) {
        auto b = pairs[j];
        for (int k = 0; k < (int)pairs.size(); k++) {
          auto c = pairs[k];
          if (graph[2][{k, end}].empty())
            continue;
          for (auto f : graph[1][{j, k}]) {
            int g = a.delta - e.d - f.d - 2 * X;
            for (auto h : graph[2][{k, end}])
              if (h.d == g) {
                closed++;
                test({{a.a, 0},
                      {b.a, e.d},
                      {c.a, e.d + f.d},
                      {a.b, a.delta},
                      {b.b, e.d + b.delta},
                      {c.b, e.d + f.d + c.delta}});
                break;
              }
          }
        }
      }
  }
  cerr << "paired closures=" << closed << " rings=" << rings << " coverable=" << adequate
       << " wirings=" << leaves << " routed=" << routed << '\n';
}
