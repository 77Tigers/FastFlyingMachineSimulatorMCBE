// Check the stated PL14 interfaces in slot-zero world coordinates.
#define STAGGER_SCREEN
#include "back.cpp"

#include "fixed.inc"
int main() {
  topology();pair_tables();
  auto known=links(0,O,oriented(T,2),2,12,0,2);
  assert(any_of(known.begin(),known.end(),[](const Handoff &h){return h.delta==pt(2,3,1);}));
  cout<<"Recovered the Round 4 O3 to T3 handoff at (2,3,1).\n";
  for (auto [name,core] : {pair{"O3",O},pair{"T3",T}}) {
    int placements=0,legal_count=0,min_conflicts=99;
    auto prev=hardware(1,core,0,0);
    for(int rot=0;rot<8;rot++)for(int dy=-5;dy<=5;dy++)for(int dz=-5;dz<=5;dz++){
      auto gate=fixed_gate(pt(-3,dy,dz),rot);
      bool covers=true;
      for(int q:core.covers){
        covers &= any_of(gate.begin(),gate.end(),[&](Cell c){return c.i==2&&c.k==G&&c.p==q-2*X;});
      }
      if(!covers)continue;
      placements++;
      int collisions=0;
      for(auto a:prev)for(auto b:gate) {
        if(a.i==b.i&&a.k==G&&b.k==G&&a.p==b.p)continue;
        if(incompatible(a,b))collisions++;
      }
      if(!collisions)legal_count++;
      min_conflicts=min(min_conflicts,collisions);
    }
    cout<<name<<" at t1=-3: "<<placements<<" co-located plate covers, "<<legal_count
        <<" legal";
    if(placements)cout<<", minimum conflicting pairs "<<min_conflicts;
    cout<<"\n";
  }
  auto gate=fixed_gate(-3*X,0);
  auto middle=middle_cores(gate,-3,11);
  int smallest=99;Core best;vector<int> best_glue;
  for(auto c:middle){
    auto w=gate,added=hardware(1,c,0,0);
    w.insert(w.end(),added.begin(),added.end());
    if(!legal(w))continue;
    bool glued=true;
    for(int h:c.hoppers){
      glued &= any_of(gate.begin(),gate.end(),[&](Cell g){return g.i==2 && (g.k==G || g.k==KCenter) && norm(h-2*X-g.p)==1;});
    }
    if(!glued)continue;
    auto route=glue_route(1,99,w,11);
    int size=route.size()+c.red.size();
    if(!route.empty() && size<smallest){smallest=size;best=c;best_glue=route;}
  }
  if(smallest<99){
    cout<<"Alternate middle with three side pickups on the fixed gate; glue+red "<<smallest<<"\n";
    for(auto [label,points]:{pair{"H",best.hoppers},pair{"R",best.red},pair{"G",best_glue}})
      for(int p:points)cout<<label<<" "<<xc(p)<<" "<<yc(p)<<" "<<zc(p)<<"\n";
  }
  for(auto [name,middle,t]:{tuple{"O3",O,0},tuple{"T3",T,1}}){
    for(int capacity=11;capacity<=17;capacity++){
      int count=0;
      for(int rot=0;rot<8;rot++)count+=links(0,T,oriented(middle,rot),t,capacity,0,rot).size();
      cout<<"T3 to "<<name<<" t0="<<t<<" glue+red cap "<<capacity<<" placements "<<count<<"\n";
      if(count)break;
    }
  }
}
