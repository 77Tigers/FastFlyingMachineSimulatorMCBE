#define BACKUP_LIBRARY
#include "backup.cpp"
int main(int argc, char **argv) {
  if (argc != 8) {
    cerr << "three B1-x B2-extra B2-sticky B0-min-x B0-max-x max-rings file\n";
    return 2;
  }
  ordinary_back = 2;
  topology();
  pair_tables();
  RearSearch search(atoi(argv[4]), atoi(argv[5]), atoi(argv[6]), argv[7]);
  search.middle_x = atoi(argv[1]);
  World base{{2, Red, 0}, {2, Glue, X}};
  for (int h : {Y, 1, -1}) {
    add(base, {2, Hopper, h});
    add(base, {2, Glue, X + h});
  }
  // A two-cell side extension lets the gated middle hand back its two
  // hoppers one plane nearer the rear of the ordinary three-hopper body.
  Sites lanes{-Y, Y + 1, Y - 1, 2 * Y, 2, -2};
  int lane = lanes.at(atoi(argv[2]));
  if (!add(base, {2, Glue, X + lane}) || !add(base, {2, Glue, lane}))
    return 0;
  set<int> stickies;
  for (auto g : base)
    if (glue(g.part))
      for (int d : dirs)
        if (legal(base, {2, Sticky, g.pos + d}))
          stickies.insert(g.pos + d);
  int si = 0, stencils = 0;
  for (int p : stickies) {
    if (si++ != atoi(argv[3]) && atoi(argv[3]) >= 0)
      continue;
    auto w = base;
    if (!add(w, {2, Sticky, p}) || !add(w, {3, Glue, p - X}))
      continue;
    set<Sites> seen;
    for (int d : dirs)
      for (int e : dirs)
        for (int f : dirs) {
          auto q = w;
          bool ok = true;
          for (auto [h, off] : {pair{Y, d}, pair{1, e}, pair{-1, f}})
            if (!side_pick(q, 3, h) && !add(q, {3, Glue, h + off})) {
              ok = false;
              break;
            }
          if (!ok)
            continue;
          Sites covers;
          for (auto g : q)
            if (g.id == 3)
              covers.push_back(g.pos);
          sort(covers.begin(), covers.end());
          if (covers.size() > 3 || !seen.insert(covers).second ||
              connect(q, 3, 6).empty())
            continue;
          stencils++;
          for (int shard = 0; shard < 4; shard++) {
            search.seed(q, shard);
            if (search.count >= search.maxrings)
              goto done;
          }
        }
  }
done:
  cout << "stencils " << stencils << " seeds " << search.middles << " plates "
       << search.plates << " cores " << search.cores << " armed "
       << search.powered << " clear halves " << search.shells << " closed "
       << search.count << "\n";
}
