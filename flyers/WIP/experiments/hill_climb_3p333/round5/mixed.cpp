#define STAGGER_SCREEN
#include "back.cpp"
array<int,3> cap{11,11,6};
int budget_for(int i){return cap[i%3];}
vector<Cell> mixed_core(int shape,int id,int origin,int sym){
 Core c;
 if(id%3!=2){
  // Face, side pickup and redstone positions in the hopper plane.
  if(shape==0)c=O;
  else if(shape==1)c=T;
  else c={{0,Y+1,Y+2},{Y,2*Y+2},{1,2}};
 }else c={{Y,1},{},{Y+1}};
 vector<Cell> v;
 auto add=[&](int p,Kind k,int body){v.push_back({origin+turn(p,sym),body,k});};
 for(int p:c.hoppers){add(p,H,id);add(p+X,G,id);}
 for(int p:c.red)add(p,R,id);
 if(id%3==2){add(0,KCenter,id);add(shape==0?-Y:shape==1?-X:X,KObserver,id);}
 for(int p:c.covers)add(p+(contact_dx(id)-2)*X,G,nextb(id));
 return v;
}
bool append_pair(vector<Cell>&world,Cell cell,int axis){
 for(auto b:{cell,Cell{turn(cell.p,2)+axis,(cell.i+3)%6,cell.k}}){
   if(!allowed(b,world))return false;
   if(!any_of(world.begin(),world.end(),[&](Cell c){return c.i==b.i && c.p==b.p;}))world.push_back(b);
 }
 return true;
}
bool local_routes(const vector<Cell>&world){
 for(int i=0;i<3;i++)if(glue_route(i,99,world,budget_for(i)).empty())return false;
 return true;
}
int saved=0;long rings=0,compatible=0,pushes=0;
void install(int stage,const vector<Cell>&world,int axis,const array<int,6>&orig,ostream&out){
 if(saved>=100)return;
 if(stage==2){
   for(int variant=0;variant<6;variant++){
     auto v=world;bool ok=true;
     for(int n=0;n<3&&ok;n++){
       int i=(n+variant)%3;auto g=glue_route(i,99,v,budget_for(i),variant);
       ok=!g.empty();
       for(int p:g)if(ok)ok=append_pair(v,{p,i,G},axis);
     }
     if(!ok)continue;
     out<<"ring "<<++saved<<"\n";
     for(int i=0;i<6;i++)out<<i<<" origin "<<xc(orig[i])<<" "<<yc(orig[i])<<" "<<zc(orig[i])<<"\n";
     set<tuple<int,int,int>> seen;
     for(auto c:v)if(seen.emplace(c.i,c.k,c.p).second)out<<c.i<<" "<<symbols[c.k]<<" "<<xc(c.p)<<" "<<yc(c.p)<<" "<<zc(c.p)<<"\n";
     out.flush();return;
   }
   return;
 }
 bool push=stage==0;
 int i=push?3:2,target=push?2:3, s=rest[i];
 int delta=displacement(i,s)-displacement(target,s)+(push?1:-3);
 set<int> sites;
 for(auto c:world){
   if(c.i==target && (push||c.k!=H)) {
     sites.insert(c.p-delta*X);
     if(c.k==G||c.k==KCenter)for(int d:dirs)sites.insert(c.p+d-delta*X);
   }
   if(c.i==i && (c.k==G||c.k==KCenter))for(int d:dirs)sites.insert(c.p+d);
 }
 for(int st:sites){
   auto w=world;Cell act{st,i,push?KPush:KSticky};
   if(!append_pair(w,act,axis))continue;
   int hit=st+delta*X;
   if(!any_of(w.begin(),w.end(),[&](Cell c){return c.i==target&&c.p==hit&&(push||c.k!=H);})){
      if(!append_pair(w,{hit,target,G},axis))continue;
   }
   if(!push){
     // Its first tower level will power the sticky.
     if(local_routes(w))install(2,w,axis,orig,out);
     continue;
   }
   for(int donor:{2,5}){
    int at=st+(displacement(i,s)-displacement(donor,s))*X;
    for(int d:{-X,Y,-Y,1,-1}){
      auto v=w;
      if(!append_pair(v,{at+d,donor,R},axis) || !local_routes(v))continue;
      pushes++;install(1,v,axis,orig,out);
    }
   }
 }
}
int main(int argc,char**argv){
 if(argc!=7){cerr<<"mixed first middle observer t0 t1 output\n";return 2;}
 topology();pair_tables();int sh[3]={atoi(argv[1]),atoi(argv[2]),atoi(argv[3])};
 int off[3]={atoi(argv[4]),atoi(argv[5]),-2-atoi(argv[4])-atoi(argv[5])};
 ofstream out(argv[6]);
 map<tuple<int,int,int>,vector<int>> cache;
 auto edge=[&](int i,int a,int b)->const vector<int>&{
   auto k=make_tuple(i,a,b);
   if(!cache.count(k)){
    auto &ls=cache[k];
    for(int y=-7;y<=7;y++)for(int z=-7;z<=7;z++){
      int d=pt(off[i]+contact_dx(i),y,z);auto w=mixed_core(sh[i],i,0,a),v=mixed_core(sh[(i+1)%3],i+1,d,b);
      w.insert(w.end(),v.begin(),v.end());
      if(legal(w)&&!glue_route(i+1,99,w,budget_for(i+1)).empty())ls.push_back(d);
    }
   }
   return cache[k];
 };
 for(int s1=0;s1<8;s1++)for(int s2=0;s2<8;s2++){
   auto &e0=edge(0,0,s1);if(e0.empty())continue;
   auto &e1=edge(1,s1,s2);if(e1.empty())continue;
   auto &e2=edge(2,s2,2);
   for(int a:e0)for(int b:e1)for(int c:e2){
     rings++;
     int ax=a+b+c;array<int,6>orig{0,a,a+b,ax,ax+turn(a,2),ax+turn(a+b,2)};
     vector<Cell>w;bool ok=true;
     for(auto [i,sym]:{pair{0,0},pair{1,s1},pair{2,s2}})
       for(auto p:mixed_core(sh[i],i,orig[i],sym))if(ok)ok=append_pair(w,p,ax);
     if(!ok||!local_routes(w))continue;
     compatible++;install(0,w,ax,orig,out);
     if(saved>=100)goto done;
   }
 }
done:
 cout<<"triples "<<rings<<" compatible "<<compatible<<" pushes "<<pushes<<" mixed rings "<<saved<<endl;
}
