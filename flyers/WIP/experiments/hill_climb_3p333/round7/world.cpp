// All six motor/plate snapshots, with each individual pickup on its assigned
// carrier. A shared required glue voxel may serve the same owner twice.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <map>
#include <vector>
using namespace std;
using Move=array<int,3>; // orientation, y, z
using Key=array<int,5>;
using Placement=array<int,42>;
using Moves=array<vector<Move>,8>;
const int Y=32;
int turn(int p,int s) {
    int y=(p+16*Y+16)/Y-16,z=p-y*Y;
    if(s&4)z=-z;
    for(int k=0;k<(s&3);k++){int t=y;y=-z;z=t;}
    return Y*y+z;
}
int comp[8][8];
map<Key,array<Moves,2>> atlas;
const array<vector<int>,3> hops{{{-Y,-1,1},{1,Y,Y+2},{0,Y+1,Y+2}}};
const array<vector<int>,3> reds{{{-Y-1,-Y+1},{Y+1},{Y,2*Y+2}}};
const array<vector<int>,3> covers{{{0},{0,2},{1,2}}};
int shift(int i,int s) {
    int n=0;
    for(int k=0;k<s;k++)n+=(k+6-2*(i%3))%6>=2;
    return n;
}
struct Unit {int x,yz,owner;bool glue;};
using Frames=array<vector<Unit>,6>;
using Spec=array<int,5>; // body, kind, orientation, first mask, second mask
map<Spec,Frames> units;
const Frames &unit(Spec spec) {
    if(auto it=units.find(spec);it!=units.end())return it->second;
    auto [i,k,rot,m0,m1]=spec;
    Frames frames;
    for(int s=0;s<6;s++) {
        int m=(s+6-2*(i%3))%6,h=shift(i,s);
        auto put=[&](int x,int yz,int owner,bool glue){frames[s].push_back({x,turn(yz,rot),owner,glue});};
        for(int p:hops[k]) {
            put(h+1,p,i,true);
            if(m>=2 && m<=4)put(h,p,i,false);
            if(m>=3 && m<=5){put(h-1,p,i,false);put(h,p,i,false);}
            if(m<2 || m>=4)put(h-(m==1?1:2),p,i,false);
        }
        for(int p:reds[k])put(h,p,i,false);
        for(int side=0;side<2;side++) {
            int j=(i+1)%3+side*3,mask=side?m1:m0;
            for(int a=0;a<(int)covers[k].size();a++)
                if(mask>>a&1)put(2*(i%3==2)-2+shift(j,s),covers[k][a],j,true);
        }
    }
    return units.emplace(spec,frames).first->second;
}
using Ban=array<uint32_t,21>;
map<array<int,11>,Ban> bans;
bool clear(Spec a,Spec b,int dx,int y,int z) {
    if(abs(y)>10 || abs(z)>10)return true;
    array<int,11> key;
    copy(a.begin(),a.end(),key.begin());copy(b.begin(),b.end(),key.begin()+5);key[10]=dx;
    auto [it,fresh]=bans.try_emplace(key);
    if(fresh) {
        auto &af=unit(a),&bf=unit(b);
        for(int s=0;s<6;s++)for(auto u:af[s])for(auto v:bf[s]) {
            if(u.x!=v.x+dx || (u.glue && v.glue && u.owner==v.owner))continue;
            int p=u.yz-v.yz,dy=(p+16*Y+16)/Y-16,dz=p-dy*Y;
            if(abs(dy)<=10 && abs(dz)<=10)it->second[dy+10]|=1u<<(dz+10);
        }
    }
    return !(it->second[y+10] & (1u<<(z+10)));
}
struct Edge {int other;const Moves *moves;};
struct Join {
    Placement row;
    array<vector<Edge>,6> adj;
    array<Move,6> poses{};
    array<bool,6> placed{};
    long nodes=0;
    Spec spec(int i,int s)const{return {i,row[i],s,row[18+2*i],row[19+2*i]};}
    bool init(){
        for(int i=0;i<6;i++)for(int side=0;side<2;side++){
            int mask=row[18+2*i+side];if(!mask)continue;
            int j=(i+1)%3+3*side,t=row[6+j]-row[6+i]-2*(i%3==2);
            auto &edge=atlas.at({row[i],row[j],row[12+j],mask,t});
            if(edge[0][0].empty())return false;
            adj[j].push_back({i,&edge[0]});adj[i].push_back({j,&edge[1]});
        }
        placed[0]=true;return true;
    }
    bool visit(int n) {
        nodes++;if(n==6)return true;
        int best=-1;
        vector<Move> best_choices;
        for(int i=0;i<6;i++)if(!placed[i]) {
            bool linked=false;
            vector<Move> choices;
            for(auto e:adj[i])if(placed[e.other]) {
                auto [s,y,z]=poses[e.other];vector<Move> cur;
                for(auto [k,dy,dz]:(*e.moves)[s])cur.push_back({k,y+dy,z+dz});
                if(!linked){choices=std::move(cur);linked=true;}
                else {
                    vector<Move> joint;
                    set_intersection(choices.begin(),choices.end(),cur.begin(),cur.end(),back_inserter(joint));
                    choices=std::move(joint);
                }
                if(choices.empty())return false;
            }
            if(!linked)continue;
            choices.erase(remove_if(choices.begin(),choices.end(),[&](Move v){
                for(int j=0;j<6;j++)if(placed[j] &&
                    !clear(spec(j,poses[j][0]),spec(i,v[0]),row[6+i]-row[6+j],
                           v[1]-poses[j][1],v[2]-poses[j][2])) return true;
                return false;
            }),choices.end());
            if(choices.empty())return false;
            if(best<0 || choices.size()<best_choices.size()){best=i;best_choices=std::move(choices);}
        }
        for(auto v:best_choices) {
            placed[best]=true;poses[best]=v;
            if(visit(n+1))return true;
            placed[best]=false;
        }
        return false;
    }
};
int main(int argc,char**argv){
    if(argc!=3)return 2;
    for(int a=0;a<8;a++)for(int b=0;b<8;b++)for(int c=0;c<8;c++)
        if(turn(turn(Y,b),a)==turn(Y,c)&&turn(turn(1,b),a)==turn(1,c))comp[a][b]=c;
    ifstream geometry(argv[1]),rows(argv[2]);if(!geometry || !rows)return 2;
    Key key;int n;
    while(geometry>>key[0]>>key[1]>>key[2]>>key[3]>>key[4]>>n){
        auto &rel=atlas[key];
        for(int v=0;v<n;v++){
            int k,y,z;geometry>>k>>y>>z;
            for(int s=0;s<8;s++){
                int p=turn(y*Y+z,s),dy=(p+16*Y+16)/Y-16,dz=p-dy*Y,rot=comp[s][k];
                rel[0][s].push_back({rot,dy,dz});rel[1][rot].push_back({s,-dy,-dz});
            }
        }
        for(auto &direction:rel)for(auto &m:direction){
            sort(m.begin(),m.end());m.erase(unique(m.begin(),m.end()),m.end());
        }
    }
    long local=0,joint=0,retained=0,nodes=0;
    while(true){
        Join j{};for(auto &v:j.row)if(!(rows>>v))goto done;
        if(!j.init()){local++;continue;}
        if(j.visit(1)){
            retained++;for(int v:j.row)cout<<v<<' ';
            for(auto p:j.poses)for(int v:p)cout<<v<<' ';
            cout<<'\n';
        }else joint++;
        nodes+=j.nodes;
    }
done:
    cerr<<"local "<<local<<" joint "<<joint<<" retained "<<retained<<" nodes "<<nodes<<"\n";
}
