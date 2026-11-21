#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>
#include <unordered_set>
#include <unordered_map>
using namespace std;
extern "C" int route(int, int, int, const int16_t *, const uint8_t *, const int16_t *, uint8_t *);
extern "C" int profile(int, int, int, const int16_t *, const uint8_t *, const int16_t *, uint8_t *);
constexpr int X = 4096, Y = 64;
int pt(int x, int y, int z) { return x * X + y * Y + z; }
int xc(int p) { return (p + 32 * Y + 32 + 32 * X) / X - 32; }
int yc(int p) { return (p - xc(p) * X + 32 + 32 * Y) / Y - 32; }
int zc(int p) { return p - xc(p) * X - yc(p) * Y; }
const int dirs[] = {X, -X, Y, -Y, 1, -1};
int norm(int p) { return abs(xc(p)) + abs(yc(p)) + abs(zc(p)); }
int turn(int p, int s) {
  int y = yc(p), z = zc(p);
  if (s & 4)
    z = -z;
  for (int j = 0; j < (s & 3); j++) {
    int k = y;
    y = -z;
    z = k;
  }
  return pt(xc(p), y, z);
}
struct Grid {
  vector<int> points;
  map<int, int> index;
  vector<int16_t> links, members;
  vector<uint8_t> cost;
  int groups = 0;
};
int length=6;
int nextb(int i){return (i+1)%6;}
int contact_dx(int i){return i%3==2 ? 2 : 0;}
enum Kind {G,R,H,KLoop,KSticky,KPush,KCenter,KObserver};
struct Cell {int p,i; Kind k;};
#include <functional>
#include <random>

namespace tower {
constexpr char symbols[] = "GRHLSPCO";
constexpr int N = 24;
enum Part { Glue, Red, Hopper, Loop, Sticky, Push, Center, Observer };
struct Block {
  int id;
  Part part;
  int pos;
};
using Blocks = vector<Block>;
int column[N], level[N], rest[N], below[N], mate[N], loop_to[N], material[N],
    base[N];
int ids[6][6], axis, pl, loops;
bool bridge_hopper = false;
int slot(int i, int s) { return (s - rest[i] + 6) % 6; }
bool moving(int i, int s) { return slot(i, s) >= 2; }
int displacement(int i, int s) {
  int x = 0;
  for (int k = 0; k < s; k++)
    x += moving(i, k);
  return x;
}
int top_level(int c) {
  return c % 3 == 2 ? 5 : c % 3 == 1 ? 4 : 0;
}
bool all_gated = false;
bool gated(int i) { return level[i] == 0 && (all_gated || column[i] % 3 == 2); }
int hopper_count(int i) {
  if (gated(i)) return 2;
  // Each back receives a pull. On a tower, the top two bodies push four times.
  return level[i] == 0 || level[i] + 1 < top_level(column[i]) ? 3 : 4;
}
void topology() {
  int n = 0;
  for (int j = 0; j <= 5; j++)
    for (int i = 0; i < 6; i++)
      if (j <= top_level(i)) {
        ids[j][i] = n;
        level[n] = j;
        column[n++] = i;
      }
  for (int i = 0; i < N; i++) {
    int c = column[i], l = level[i];
    rest[i] = (2 * (c - l + 6)) % 6;
    material[i] = (c + l) % 2;
    below[i] = l ? ids[l - 1][c] : (c + 1) % 6;
    mate[i] = ids[l][(c + 3) % 6];
    loop_to[i] = l && c % 3 == 1 ? ids[l][c + 1] : below[i];
    if (bridge_hopper && l == 2 && c % 3 == 2)
      loop_to[i] = ids[0][c - 1];
  }
}
enum Mode { Solid, Ready, Spent, Extended, Arm, StickyArm };
struct Location {
  int dx, carrier;
  Mode mode;
};
vector<Location> states_at(int i, Part part, int s) {
  int m = slot(i, s), h = displacement(i, s);
  if (part == Push && m == 1)
    return {{h, i, Extended}, {h + 1, i, Arm}};
  if (part == Sticky && m == 1)
    return {{h, i, Extended}, {h - 1, i, StickyArm}};
  if (part != Hopper && part != Loop)
    return {{h, i, Solid}};
  vector<Location> out;
  int first = gated(i) ? 3 : 2, last = first + hopper_count(i) - 1,
      carrier = part == Loop ? loop_to[i] : below[i];
  if (m >= 2 && m <= last)
    out.push_back({h, i, Ready});
  if ((m >= first + 1 && m <= last + 1) || (m == 0 && last == 5)) {
    out.push_back({h - 1, i, Extended});
    out.push_back({h, i, Arm});
  }
  if (m < 2 || m >= first + 2)
    out.push_back({h - (m == 1 ? 1 : 2), carrier, Spent});
  return out;
}
using Forbidden = array<uint8_t, 17 * 3 * 3>;
Forbidden bad[N][8][N][8];
int index(int dx, int dy, int dz) {
  return (dx + 8) * 9 + (dy + 1) * 3 + dz + 1;
}
void pair_tables() {
  for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++)
      for (Part a : {Glue, Red, Hopper, Loop, Sticky, Push, Center, Observer})
        for (Part b : {Glue, Red, Hopper, Loop, Sticky, Push, Center, Observer}) {
          auto &f = bad[i][a][j][b];
          for (int s = 0; s < 6; s++)
            for (auto u : states_at(i, a, s))
              for (auto v : states_at(j, b, s)) {
                auto ban = [&](int offset) {
                  int x = xc(offset) + u.dx - v.dx;
                  f[index(x, yc(offset), zc(offset))] = 1;
                };
                ban(0);
                for (int rev : {0, 1}) {
                  auto c = rev ? v : u, n = rev ? u : v;
                  Part p = rev ? b : a, q = rev ? a : b;
                  int host = rev ? j : i, other = rev ? i : j,
                      sign = rev ? -1 : 1;
                  bool passive = c.mode == Extended || c.mode == Arm ||
                                 c.mode == StickyArm;
                  bool neighbour_passive = n.mode == Extended ||
                                           n.mode == Arm || n.mode == StickyArm;
                  if (!passive && moving(c.carrier, s) &&
                      c.carrier != n.carrier) {
                    if (!(n.mode == StickyArm && (below[other] == c.carrier || (all_gated && c.carrier < 6 && c.carrier % 3 == below[other] % 3))))
                      ban(sign * X);
                    bool own_actuator = q == Push && slot(other, s) == 0 &&
                        (c.carrier == (column[other] + 5) % 6 || (all_gated && c.carrier<6 && c.carrier%3==(column[other]+2)%3));
                    if ((p == Glue || p == Center) && !neighbour_passive && !own_actuator &&
                        ((q != Glue && q != Center) || material[host] == material[other]))
                      for (int d : dirs)
                        ban(sign * d);
                  }
                  if (p == Sticky && c.mode == Solid && slot(host, s) == 0)
                    ban(-sign * X);
                  bool pulse = p == Center && (slot(host, s) == 0 || slot(host, s) >= 3);
                  if (p != Red && !pulse)
                    continue;
                  if ((q == Hopper || q == Loop) &&
                      (n.mode == Spent || n.mode == Extended || (n.mode == Ready && gated(other) && slot(other,s)==2)))
                    for (int d : dirs)
                      if (d != -X)
                        ban(sign * d);
                  if (q == Push && n.mode != Arm && slot(other, s) != 0)
                    for (int d : dirs)
                      if (d != -X) ban(sign * d);
                  if (q == Sticky && n.mode != StickyArm && slot(other, s) != 0)
                    for (int d : dirs)
                      if (d != X)
                        ban(sign * d);
                }
              }
        }
}
bool conflict(Block a, Block b) {
  int d = b.pos - a.pos, x = xc(d), y = yc(d), z = zc(d);
  return abs(x) <= 8 && abs(y) <= 1 && abs(z) <= 1 &&
         bad[a.id][a.part][b.id][b.part][index(x, y, z)];
}
Block mirrored(Block b) { return {mate[b.id], b.part, turn(b.pos, 2) + axis}; }
} // namespace tower
