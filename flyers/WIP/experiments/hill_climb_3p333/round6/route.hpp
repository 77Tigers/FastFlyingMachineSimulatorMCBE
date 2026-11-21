#pragma once
#include "motion.hpp"
namespace search {
using namespace tower;
using World = vector<Block>;
bool glue(Part k) { return k == Glue || k == Center; }
bool add(World &w, Block b) {
  for (auto c : w) {
    if (b.id == c.id && b.pos == c.pos &&
        (c.part == b.part || (b.part == Glue && glue(c.part))))
      return true;
    if (conflict(b, c))
      return false;
  }
  w.push_back(b);
  return true;
}
bool legal(const World &w, Block b) {
  for (auto c : w)
    if (conflict(b, c) &&
        !(b.id == c.id && b.pos == c.pos && b.part == Glue && glue(c.part)))
      return false;
  return true;
}
bool side_pick(const World &world, int carrier, int spent) {
  for (auto c : world)
    if (c.id == carrier) {
      if (glue(c.part) && norm(c.pos - spent) == 1)
        return true;
      if (c.part != Hopper && c.part != Loop && c.pos == spent - X)
        return true;
    }
  return false;
}
using Sites = vector<int>;
using Groups = vector<Sites>;
int distance(int a, int b) { return norm(a - b); }
Sites neighbors(int p) {
  Sites s;
  for (int d : dirs)
    s.push_back(p + d);
  return s;
}
// Connect fixed glue and one legal contact site per outstanding attachment.
Sites connect(const World &world, int id, int cap, Groups extra = {},
              int shuffle_seed = 0) {
  set<int> req;
  for (auto c : world)
    if (c.id == id) {
      if (glue(c.part))
        req.insert(c.pos);
      if (c.part == Red)
        --cap;
      if (c.part != Hopper && !glue(c.part))
        extra.push_back(neighbors(c.pos));
    }
  int left = cap - int(req.size());
  if (left < 0 || req.empty())
    return {};
  Groups groups;
  auto unseen = req;
  while (!unseen.empty()) {
    Sites g{*unseen.begin()};
    unseen.erase(g[0]);
    for (size_t k = 0; k < g.size(); ++k)
      for (int d : dirs)
        if (unseen.erase(g[k] + d))
          g.push_back(g[k] + d);
    groups.push_back(g);
  }
  for (auto &g : extra) {
    if (any_of(g.begin(), g.end(), [&](int p) { return req.count(p); }))
      continue;
    g.erase(remove_if(g.begin(), g.end(),
                      [&](int p) {
                        return !legal(world, {id, Glue, p});
                      }),
            g.end());
    if (g.empty() || !left)
      return {};
    sort(g.begin(), g.end());
    if (find(groups.begin(), groups.end(), g) == groups.end())
      groups.push_back(g);
  }
  if (groups.size() == 1)
    return {req.begin(), req.end()};
  if (groups.size() > 14)
    return {};
  // Every component needs at most 'left' new cells to reach fixed glue.
  for (auto &g : groups) {
    int nearest = 999;
    for (int a : g)
      for (int b : req)
        nearest = min(nearest, norm(a - b));
    if (nearest > left)
      return {};
  }
  int lo[3] = {99, 99, 99}, hi[3] = {-99, -99, -99};
  for (auto &g : groups)
    for (int p : g) {
      int a[] = {xc(p), yc(p), zc(p)};
      for (int k = 0; k < 3; k++) {
        lo[k] = min(lo[k], a[k]);
        hi[k] = max(hi[k], a[k]);
      }
    }
  // Enumerate two extra planes around the required sites for routes around
  // hardware.
  Sites points;
  for (int x = lo[0] - 2; x <= hi[0] + 2; x++)
    for (int y = lo[1] - 2; y <= hi[1] + 2; y++)
      for (int z = lo[2] - 2; z <= hi[2] + 2; z++) {
        int p = pt(x, y, z);
        if (none_of(req.begin(), req.end(),
                    [&](int q) { return norm(p - q) <= left; }))
          continue;
        if (legal(world, {id, Glue, p}))
          points.push_back(p);
      }
  if (shuffle_seed) {
    mt19937 rng(shuffle_seed);
    shuffle(points.begin(), points.end(), rng);
  }
  unordered_map<int, int> ids;
  vector<uint8_t> cost(points.size()), used(points.size());
  vector<int16_t> members(points.size()), edges;
  for (size_t k = 0; k < points.size(); ++k) {
    ids[points[k]] = k;
    cost[k] = !req.count(points[k]);
  }
  for (size_t i = 0; i < groups.size(); i++) {
    bool ok = false;
    for (int p : groups[i])
      if (ids.count(p)) {
        members[ids[p]] |= 1 << i;
        ok = true;
      }
    if (!ok)
      return {};
  }
  for (int p : points)
    for (int d : dirs) {
      auto it = ids.find(p + d);
      edges.push_back(it == ids.end() ? -1 : it->second);
    }
  if (route(points.size(), groups.size(), left, edges.data(), cost.data(),
            members.data(), used.data()) == 100)
    return {};
  Sites answer(req.begin(), req.end());
  for (size_t k = 0; k < points.size(); k++)
    if (used[k] && cost[k])
      answer.push_back(points[k]);
  return answer;
}
} // namespace search
