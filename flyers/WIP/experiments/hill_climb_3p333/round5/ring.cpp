// Fit all six rigid pushes and pulls to a pair of half-turn-symmetric body triples.
#define STAGGER_SCREEN
#include "back.cpp"

int budget;
vector<Cell> mirrored_cells(vector<Cell> v,int ax) {
  for(auto &c:v){c.i=(c.i+3)%6;c.p=turn(c.p,2)+ax;}
  return v;
}
bool append(vector<Cell>&w,vector<Cell> v,int ax) {
  auto other=mirrored_cells(v,ax);v.insert(v.end(),other.begin(),other.end());
  for(auto c:v){if(!allowed(c,w))return false;w.push_back(c);}return true;
}
bool glue_all(vector<Cell> w,int ax, const char *out,int pl){
 for(int retry=0;retry<6;retry++){
  auto v=w;bool ok=true;
  for(int n=0;n<3&&ok;n++){
    int i=(n+retry)%3;
    auto gs=glue_route(i,99,v,budget,retry);
    if(gs.empty()){ok=false;break;}
    for(int p:gs)if(!any_of(v.begin(),v.end(),[&](Cell b){return b.i==i && b.p==p;}))
      if(!append(v,{{p,i,G}},ax)){ok=false;break;}
  }
  if(ok){
    ofstream file(out); file<<"6 "<<pl<<"\n";
    for(int i=0;i<6;i++)file<<i<<" body "<<i<<" 0 "<<rest[i]<<" "<<material[i]<<"\n";
    set<tuple<int,int,int>> seen;
    for(auto c:v)if(seen.emplace(c.i,c.k,c.p).second)file<<c.i<<" "<<symbols[c.k]<<" "<<xc(c.p)<<" "<<yc(c.p)<<" "<<zc(c.p)<<"\n";
    return true;
  }
 }
 return false;
}
long rings=0, routed=0, armed=0;
bool is_glue(Cell c){return c.k==G || c.k==KCenter;}
int near_glue(const vector<Cell>&w,int i,int p){
 int best=99;for(auto c:w)if(c.i==i && is_glue(c))best=min(best,norm(c.p-p));return best;
}
struct Mechanism{Cell piston; vector<Cell> cells; int score;};
array<long,7> count_depth{}, quality{};
array<long,6> working{}; int maxports=0;
bool fit_actuators(int used,const vector<Cell>&w,int ax,const char*out,int pl){
 count_depth[__builtin_popcount(used)]++;
 if(used==63){armed++;return glue_all(w,ax,out,pl);}
 vector<Mechanism> best;int select=-1, available=0;
 for(int k=0;k<6;k++)if(!(used & (1<<k))){
   int i=k/2,s=rest[i];bool push=k%2==0;
   int normal=push?(i+5)%6:nextb(i);
   vector<Mechanism> found;
   for(int target:{normal,(normal+3)%6}){
     int delta=displacement(i,s)-displacement(target,s)+(push?1:-3);
     set<int> sites;
     for(auto c:w){
       if(c.i==target && (c.k!=H||push)){
         sites.insert(c.p-delta*X);
         if(is_glue(c))for(int d:dirs)sites.insert(c.p+d-delta*X);
       }
       if(c.i==i && is_glue(c))for(int d:dirs) {
         sites.insert(c.p+d);
         for(int e:dirs)sites.insert(c.p+d+e);
       }
     }
     for(int pos:sites) {
       Cell actuator{pos,i,push?KPush:KSticky};
       if(!allowed(actuator,w))continue;
       int near=near_glue(w,i,pos);
       if(near>4)continue;
       int hit=pos+delta*X;
       bool existing=any_of(w.begin(),w.end(),[&](Cell c){return c.i==target&&c.p==hit&&(c.k!=H||push);});
       if(!existing && near_glue(w,target,hit)>4)continue;
       for(Kind kind:{G,R}){
         if(existing && kind==R)continue;
         vector<Cell> extra;
         if(!existing){
           Cell g{hit,target,kind};
           if(!allowed(g,w)||incompatible(g,actuator))continue;
           extra.push_back(g);
         }
         bool powered=false;
         for(auto c:w)if(c.k==R || c.k==KCenter){
           int m=slot(c.i,s);
           if(c.k==KCenter && m!=0 && m<3)continue;
           int diff=c.p-pos+(displacement(c.i,s)-displacement(i,s))*X;
           if(norm(diff)==1&&diff!=(push?X:-X))powered=true;
         }
         if(powered){found.push_back({actuator,extra,near+3*(int)extra.size()});continue;}
         for(int host=0;host<6;host++)if(rest[host]==(s+4)%6){
           int at=pos+(displacement(i,s)-displacement(host,s))*X;
           for(int side:dirs)if(side!=(push?X:-X)){
             Cell r{at+side,host,R};
             int dist=near_glue(w,host,r.p);
             if(dist>4 || !allowed(r,w)||incompatible(r,actuator))continue;
             if(!extra.empty() && incompatible(extra.front(),r))continue;
             auto e=extra;e.push_back(r);
             found.push_back({actuator,e,near+dist+3*(int)e.size()});
           }
         }
       }
     }
   }
   if(found.empty()){if(used)return false;continue;}
   available++;if(!used)working[k]++;
   if(select<0||found.size()<best.size()){select=k;best=move(found);}
 }
 if(!used){quality[available]++;if(available>maxports){maxports=available;cout<<"maximum single ports "<<available<<endl;}}
 if(available!=6-__builtin_popcount(used))return false;
 sort(best.begin(),best.end(),[](auto&a,auto&b){return a.score<b.score;});
 for(auto &m:best){
   auto v=w;auto e=m.cells;e.push_back(m.piston);
   if(!append(v,e,ax))continue;
   bool ok=true;
   for(int j=0;j<3;j++)if(glue_route(j,99,v,budget).empty()){ok=false;break;}
   if(ok&&fit_actuators(used|(1<<select),v,ax,out,pl))return true;
 }
 return false;
}
bool fit(const vector<Cell>&w,int ax,const char*out,int pl){
 for(int i=0;i<3;i++) if(glue_route(i,99,w,budget-1).empty())return false;
 routed++;
 return fit_actuators(0,w,ax,out,pl);
}

vector<Cell> light(int sh,int id,int at,int sym){
 int obs=sh%3==0?-Y:sh%3==1?-X:-1;
 vector<Cell> v;
 const int shape=sh/3;
 int h0=Y,h1=shape>=5?-Y:1;
 if(shape>=5 && obs==-Y)obs=-1;
 for(auto [p,k]:{pair{0,KCenter},pair{obs,KObserver},pair{h0,H},pair{h1,H},pair{X+h0,G},pair{X+h1,G}})
   v.push_back({at+turn(p,sym),id,k});
 vector<int> covers;
 switch(shape){
 case 0:covers={Y+1};break;
 case 1:covers={2*Y,2};break;
 case 2:covers={Y-1,1-Y};break;
 case 3:covers={Y-X,1-Y};break;
 case 4:covers={Y-X,1-X};break;
 case 5:covers={Y+1,-Y+1};break;
 case 6:covers={Y-X,-Y+1};break;
 }
 for(int p:covers)v.push_back({at+turn(p,sym)+(contact_dx(id)-2)*X,nextb(id),G});
 return v;
}
int main(int argc,char**argv){
 if(argc!=6){cerr<<"ring PL shape0 shape1 shape2 output\n";return 2;}
 length=6;all_gated=true;topology();pair_tables();int pl=atoi(argv[1]);budget=pl-5;
 int sh[3];for(int i=0;i<3;i++){sh[i]=atoi(argv[i+2]);if(sh[i]<0||sh[i]>20)return 2;}
 map<tuple<int,int,int,int>,vector<int>> cache;
 auto edge=[&](int i,int sa,int sb,int t)->const vector<int>&{
   auto k=make_tuple(i,sa,sb,t);
   if(!cache.count(k)){
     auto &values=cache[k];
     for(int y=-6;y<=6;y++)for(int z=-6;z<=6;z++){
       int d=pt(t+contact_dx(i),y,z);
       auto w=light(sh[i],i,0,sa),v=light(sh[(i+1)%3],i+1,d,sb);
       w.insert(w.end(),v.begin(),v.end());
       if(legal(w)&&!glue_route(i+1,99,w,pl-6).empty()) values.push_back(d);
     }
   }
   return cache[k];
 };
 for(int t0:{-1,0,-2,1,-3,2})for(int s1=0;s1<8;s1++){
  auto &e0=edge(0,0,s1,t0);if(e0.empty())continue;
  for(int t1:{-1,0,-2,1,-3,2})for(int s2=0;s2<8;s2++){
   int t2=-2-t0-t1;if(t2< -3 || t2>2)continue;
   auto &e1=edge(1,s1,s2,t1);if(e1.empty())continue;
   auto &e2=edge(2,s2,2,t2);
   for(int a:e0)for(int b:e1)for(int c:e2){
     rings++;
     int ax=a+b+c;
     vector<Cell>w;
     bool ok=true;
     for(auto [i,at,sym]:{tuple{0,0,0},tuple{1,a,s1},tuple{2,a+b,s2}}){
       auto parts=light(sh[i],i,at,sym);
       if(!append(w,parts,ax)){ok=false;break;}
     }
     if(!ok)continue;
     if(fit(w,ax,argv[5],pl)){cout<<"closed "<<t0<<" "<<t1<<" "<<t2<<" rings "<<rings<<endl;return 0;}
   }
  }
 }
 cout<<"triples="<<rings<<" routed_cores="<<routed<<" actuator_configurations="<<armed
     <<" maximum_independent_sites="<<maxports<<"\n";
 cout<<"nodes_by_actuator_count";
 for(auto count:count_depth)cout<<" "<<count;
 cout<<"\n";
 return 0;
}
