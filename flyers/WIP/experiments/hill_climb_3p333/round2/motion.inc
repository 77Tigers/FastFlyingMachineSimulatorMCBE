// Check that every permitted actuator can discover the whole body by the
// simulator's two transport rules: six-face adhesion and forward obstruction.
bool reaches(int i, const vector<Pose> &poses, const vector<Cell> &cells, const vector<int> &gl) {
  auto &sh = shapes[poses[i].shape];
  int prev = (i + length - 1) % length;
  unordered_set<int> glue(gl.begin(), gl.end());
  vector<int> fixed;
  for (auto c : cells)
    if (c.i == i && (c.k == S || c.k == R))
      fixed.push_back(c.p);
  auto &ph = shapes[poses[prev].shape];
  int previous = poses[prev].p + (contact_dx(prev) - 2) * X;
  int target = poses[prev].p + ph.pickup + (contact_dx(prev) - 2) * X;
  for (int m = 2; m <= 5; m++)
    for (int k = 0; k < (m == 5 ? 1 : 3); k++)
      for (int own = 0; own < 8; own++) {
        if (__builtin_popcount((unsigned)own) != max(0, 4 - m) || (m < 5 && (own >> k & 1)))
          continue;
        for (int other = 0; other < 8; other++) {
          if (__builtin_popcount((unsigned)other) != min(3, m - 1))
            continue;
          unordered_set<int> blocks = glue;
          blocks.insert(fixed.begin(), fixed.end());
          for (int j = 0; j < 3; j++) {
            if (own >> j & 1)
              blocks.insert(poses[i].p + sh.p[j]);
            if (other >> j & 1)
              blocks.insert(previous + ph.p[j]);
          }
          int root = m == 5 ? target : poses[i].p + sh.p[k] + X;
          vector<int> q = {root};
          unordered_set<int> seen = {root};
          for (size_t h = 0; h < q.size(); h++) {
            int p = q[h];
            for (int d : dirs) {
              if (d != X && !glue.count(p))
                continue;
              int n = p + d;
              if (blocks.count(n) && seen.insert(n).second)
                q.push_back(n);
            }
          }
          if (seen.size() != blocks.size())
            return false;
        }
      }
  return true;
}
