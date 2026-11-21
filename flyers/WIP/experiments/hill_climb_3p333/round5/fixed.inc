vector<Cell> fixed_gate(int origin,int sym) {
  vector<Cell> v;
  for (auto [p,k] : {pair{0,H},pair{Y+1,H},pair{1,KCenter},pair{1-Y,KObserver},
                     pair{2,R},pair{X,G},pair{X+1,G},pair{X+Y+1,G},
                     pair{X+Y+2,G},pair{X+Y,KSticky}})
    v.push_back({origin+turn(p,sym),2,k});
  v.push_back({origin+turn(Y,sym),3,G});
  v.push_back({origin+turn(Y+2,sym),3,KPush});
  return v;
}
