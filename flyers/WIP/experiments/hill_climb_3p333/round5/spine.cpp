// Place B0's hoppers on the glue already budgeted for B1's pickup stalk.
#define STAGGER_SCREEN
#include "back.cpp"
#include "fixed.inc"

long middles=0,stalks=0,fronts=0,shells=0;
int saved=0, front_capacity=11;
bool add(vector<Cell>&w,Cell c) {
  if(!allowed(c,w))return false;
  if(!any_of(w.begin(),w.end(),[&](Cell a){return a.i==c.i && a.p==c.p;}))w.push_back(c);
  return true;
}
void close_with_mate(const vector<Cell>&base,const Core&front,ostream&out) {
 auto w=base, cells=hardware(0,front,0,0);
 w.insert(w.end(),cells.begin(),cells.end());
 int y0=yc(front.hoppers[0]),z0=zc(front.hoppers[0]);
 for(int dy=-5;dy<=5;dy++)for(int dz=-5;dz<=5;dz++){
   int ax=pt(0,y0+dy,z0+dz);
   auto v=w;bool ok=true;
   for(auto c:w)if(!add(v,{turn(c.p,2)+ax,(c.i+3)%6,c.k})){ok=false;break;}
   if(!ok)continue;
   shells++;
   for(int variant=0;variant<3;variant++){
     auto g=glue_route(0,99,v,front_capacity,variant);
     if(g.empty())break;
     auto full=v;ok=true;
     for(int p:g)if(!add(full,{p,0,G})||!add(full,{turn(p,2)+ax,3,G})){ok=false;break;}
     if(!ok)continue;
     out<<"ring "<<++saved<<"\n";
     for(int i=0;i<6;i++){
       int o=(i%3==2?-3*X:0)+(i>=3?ax:0);
       out<<i<<" origin "<<xc(o)<<" "<<yc(o)<<" "<<zc(o)<<"\n";
     }
     set<tuple<int,int,int>> seen;
     for(auto c:full)if(seen.emplace(c.i,c.k,c.p).second)out<<c.i<<" "<<symbols[c.k]<<" "<<xc(c.p)<<" "<<yc(c.p)<<" "<<zc(c.p)<<"\n";
     out.flush();break;
   }
   if(saved>=50)return;
 }
}
int main(int argc,char**argv){
 if(argc<2 || argc>4)return 2;
 if(argc>=3)front_capacity=atoi(argv[2]);
 topology();pair_tables();ofstream out(argv[1]);
 auto gate_cells=fixed_gate(-3*X,0);
 if(argc==4 && string(argv[3])=="rear"){
   gate={-Y,-X-1,0,{X,-1}};
   gate_cells=hardware(2,gated_core,-3*X,0);
 }
 auto &gate=gate_cells;
 for(auto mid:middle_cores(gate,-3,11)){
   auto base=gate, mh=hardware(1,mid,0,0);base.insert(base.end(),mh.begin(),mh.end());
   if(!legal(base))continue;
   auto g=glue_route(1,99,base,11);
   if(g.empty())continue;
   int room=11-g.size()-mid.red.size();
   if(room<1)continue;
   for(int p:g)add(base,{p,1,G});
   middles++;set<vector<int>> seen;
   for(int start:g)for(int sideways:{0,Y,-Y,1,-1})for(int bend=0;bend<=room;bend++){
     auto v=base;int p=start;vector<int> spine;
     for(int step=0;step<room;step++) {
       p+=(step==bend&&sideways!=0)?sideways:-X;
       if(!add(v,{p,1,G}))break;
       spine.push_back(p);
     }
     sort(spine.begin(),spine.end());
     if(!seen.insert(spine).second)continue;
     // A three-hopper group within two cells of the back ring can join the rear ports.
     stalks++;auto fs=middle_cores(v,0,11,0,1,-3,2);fronts+=fs.size();
     for(auto f:fs){close_with_mate(v,f,out);if(saved>=50)goto done;}
   }
 }
done:
 cout<<"middle placements "<<middles<<" pickup stalks "<<stalks<<" three-hopper fronts "<<fronts<<" clear shells "<<shells<<" routed "<<saved<<endl;
}
