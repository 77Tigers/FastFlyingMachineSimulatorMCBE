#define RIGID_LIBRARY
#include "rigid.cpp"

long pairs_seen = 0, axes_seen = 0, mirror_ok = 0, routes_seen = 0;
bool half_add(World &w, Block b) { return add(w, b) && add(w, mirrored(b)); }
bool in_body(const World &w, int i, int p, bool hopper = true) {
  return present(w, i, p, hopper) || present(w, mate[i], p, hopper);
}
bool finish(const World &w, const Top &t, const Cluster &B, int red,
            const Sites &bh, int pl, const char *path) {
  int contacts[] = {t.p_rod + 3 * X, t.s1_rod - X, B.second + 3 * X,
                    B.sticky - X};
  for (int push : neighbors(red)) {
    if (push - red == -X || !in_body(w, 2, push + X))
      continue;
    for (int owner : {0, 3}) {
      auto a = w;
      if (!half_add(a, {owner, Push, push}))
        continue;
      for (int mask = 0; mask < 16; mask++) {
        auto q = a;
        bool ok = true;
        for (int k = 0; k < 4; k++) {
          int i = mask >> k & 1 ? 3 : 0;
          if (!present(q, i, contacts[k]) &&
              !half_add(q, {i, Glue, contacts[k]})) {
            ok = false;
            break;
          }
        }
        if (!ok)
          continue;
        Groups pickups;
        for (size_t k = 0; k < bh.size(); k++) {
          int h = bh[k];
          if (((split_bottom >> k) & 1) != (below[2] == 3))
            h = axis + turn(h, symmetry);
          if (!side_pick(q, 0, h))
            pickups.push_back(neighbors(h));
        }
        routes_seen++;
        for (int var = 0; var < 3; var++) {
          auto gs = connect(q, 0, pl - 3, pickups, var);
          if (gs.empty())
            break;
          auto full = q;
          ok = true;
          for (int p : gs)
            if (!half_add(full, {0, Glue, p})) {
              ok = false;
              break;
            }
          if (!ok)
            continue;
          ofstream out(path);
          out << "6 " << pl << "\n";
          for (int i = 0; i < 6; i++)
            out << i << " body " << i << " 0 " << rest[i] << " " << material[i]
                << "\n";
          for (auto b : full)
            out << b.id << " " << symbols[b.part] << " " << xc(b.pos) << " "
                << yc(b.pos) << " " << zc(b.pos) << "\n";
          return true;
        }
      }
    }
  }
  return false;
}
void hit_axes(set<int> &axes, int target, const World &w, int id, bool hopper) {
  for (auto b : w)
    if (b.id == id && (hopper || b.part != Hopper) && xc(b.pos) == xc(target))
      axes.insert(target - turn(b.pos, symmetry));
}
bool testBT(const Shape &s, Cluster b, int pl, const char *path) {
  int shift = -2 * X - b.center;
  Cluster B{b.center + shift, b.push + shift, b.second + shift,
            b.sticky + shift};
  World base;
  if (!append(base, s.w, shift))
    return false;
  if (!add(base, {2, Push, B.push}) || !add(base, {2, Push, B.second}) ||
      !add(base, {2, Sticky, B.sticky}) || !add(base, {1, Red, 0}))
    return false;
  Sites bh = s.h;
  for (int &p : bh)
    p += shift;
  for (auto &[key, options] : tops) {
    for (auto &t : options) {
      auto seed = base;
      if (!append(seed, t.w))
        continue;
      // Put the largest material groups together before choosing the two
      // passive B attachments. All body coordinates refer to slot zero.
      bool tp = present(seed, 1, B.push + 3 * X);
      auto axes_base = set<int>{};
      if (!tp)
        hit_axes(axes_base, B.push + 3 * X, t.w, 1, true);
      if (!tp && axes_base.empty())
        continue;
      for (int o : dirs) {
        auto co = seed;
        if (!add(co, {2, Observer, o + shift}))
          continue;
        for (int rlocal : perimeter(s, Red)) {
          int r = rlocal + shift;
          auto bw = co;
          if (!add(bw, {2, Red, r}))
            continue;
          pairs_seen++;
          bool sb = present(bw, 2, t.s_bottom - 3 * X, false);
          set<int> axes = axes_base;
          if (tp && !sb)
            hit_axes(axes, t.s_bottom - 3 * X, bw, 2, false);
          if (tp && sb)
            for (int y = -7; y <= 7; y++)
              for (int z = -7; z <= 7; z++)
                axes.insert(pt(0, y, z));
          for (int ax : axes) {
            if (!involution(ax))
              continue;
            axis = ax;
            if (!sb &&
                !present(bw, 2, axis + turn(t.s_bottom - 3 * X, symmetry),
                         false))
              continue;
            bool caught = true;
            for (int h : key) {
              int pos = h - 2 * X;
              bool loop = any_of(t.w.begin(), t.w.end(), [&](Block b) {
                return b.id == 1 && b.pos == h && b.part == Loop;
              });
              if (loop != (below[1] == 5))
                pos = axis + turn(pos, symmetry);
              if (!side_pick(bw, 2, pos))
                caught = false;
            }
            if (!caught)
              continue;
            axes_seen++;
            auto full = bw;
            bool clear = true;
            for (auto block : bw)
              if (!add(full, mirrored(block))) {
                clear = false;
                break;
              }
            if (!clear)
              continue;
            mirror_ok++;
            if (finish(full, t, B, r, bh, pl, path))
              return true;
          }
        }
      }
    }
  }
  return false;
}
int main(int argc, char **argv) {
  if (argc != 6 && argc != 9) {
    cerr << "half PL material-bits pickup-bits top-shape output [top-split "
            "bottom-split symmetry]\n";
    return 2;
  }
  int pl = atoi(argv[1]), m = atoi(argv[2]), mask = atoi(argv[3]),
      top = atoi(argv[4]);
  if (argc == 9) {
    split_top = atoi(argv[6]);
    split_bottom = atoi(argv[7]);
    symmetry = atoi(argv[8]);
  }
  opposite = rigid_ring = true;
  topology();
  for (int i = 0; i < 3; i++) {
    material[i] = m >> i & 1;
    material[i + 3] = 1 - material[i];
    int receiver = (i + 1) % 3;
    if (i == 1 && (mask & 1) || i == 2 && (mask & 2))
      receiver += 3;
    below[i] = receiver;
    below[i + 3] = (receiver + 3) % 6;
    loop_to[i] = below[i + 3];
    loop_to[i + 3] = below[i];
  }
  pair_tables();
  array<Sites, 3> th{{{Y, -Y, 1}, {Y, 1, X}, {Y, -Y, X}}};
  make_tops(th.at(top), pl - 8);
  cerr << "top layouts " << topcount << " in " << tops.size()
       << " hopper triples\n";
  Sites ds{Y, -Y, 1, -1, X};
  for (int i = 0; i < 5; i++)
    for (int j = 0; j < i; j++)
      for (auto &s : shapes(2, {ds[i], ds[j]}, pl - 8))
        for (auto b : clusters(s, 2))
          if (testBT(s, b, pl, argv[5]))
            goto done;
done:
  cout << "T/B pairs " << pairs_seen
       << " half-turn axes with contacts and pickups " << axes_seen
       << " clear halves " << mirror_ok << " rod routing calls " << routes_seen
       << "\n";
}
