#define BACK_LIBRARY
#include "back.cpp"

int main(int argc, char **argv) {
  if (argc != 11 && argc != 12) {
    cerr << "flex t0 t1 extra-index observer-index sticky-index pickup-mode "
            "front-cap middle-cap max-rings output [swap|joint]\n";
    return 2;
  }
  topology();
  pair_tables();
  Search s(atoi(argv[1]), atoi(argv[2]), atoi(argv[8]), atoi(argv[9]),
           argv[10]);
  s.swap_push = argc == 12 && string(argv[11]) == "swap";
  s.joint = argc == 12 && string(argv[11]) == "joint";
  s.stagger = true;
  s.front_cap = atoi(argv[7]);
  s.yzr = 7;
  Sites extras;
  for (int p : {0, X, X + Y, X + 1})
    for (int d : dirs) {
      int q = p + d;
      if (q != 0 && q != X && q != X + Y && q != X + 1 && q != Y && q != 1)
        extras.push_back(q);
    }
  sort(extras.begin(), extras.end());
  extras.erase(unique(extras.begin(), extras.end()), extras.end());
  auto extra = extras.at(atoi(argv[3]));
  int obs[] = {-Y, -X, -1};
  World core{{2, Center, 0},   {2, Observer, obs[atoi(argv[4])]},
             {2, Hopper, Y},   {2, Hopper, 1},
             {2, Glue, X},     {2, Glue, X + Y},
             {2, Glue, X + 1}, {2, Glue, extra}};
  World base;
  for (auto b : core)
    if (!add(base, b))
      return 0;
  set<int> st;
  for (auto b : base)
    if (glue(b.part))
      for (int d : dirs)
        if (legal(base, {2, Sticky, b.pos + d}))
          st.insert(b.pos + d);
  int n = 0, m = 0, mode = atoi(argv[6]);
  for (int p : st) {
    if (n++ != atoi(argv[5]) && atoi(argv[5]) >= 0)
      continue;
    auto w = base;
    if (!add(w, {2, Sticky, p}) || !add(w, {3, Glue, p - X}))
      continue;
    set<Sites> configurations;
    for (int d : dirs)
      for (int e : dirs) {
        auto q = w;
        if (!side_pick(q, 3, Y) && !add(q, {3, Glue, Y + d}))
          continue;
        if (!side_pick(q, 3, 1) && !add(q, {3, Glue, 1 + e}))
          continue;
        Sites covers;
        for (auto b : q)
          if (b.id == 3)
            covers.push_back(b.pos);
        sort(covers.begin(), covers.end());
        if ((mode == 0 && covers.size() > 1) ||
            (mode == 1 && covers.size() > 2) ||
            !configurations.insert(covers).second)
          continue;
        if (connect(q, 3, s.front_cap - 3).empty())
          continue;
        s.plate = q;
        m++;
        s.run_plate();
        if (s.count >= s.goal)
          goto done;
      }
  }
done:
  cout << "stencils " << m << " cores " << s.cores << " stalks " << s.stalks
       << " fronts " << s.fronts << " pushes " << s.pushes << " joins "
       << s.joins << " routed " << s.count << "\n";
}
