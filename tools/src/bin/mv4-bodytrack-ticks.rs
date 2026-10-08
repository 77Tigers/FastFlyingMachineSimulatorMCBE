// Single-tick body-level timing summary for mv4. Usage: bodytrack FILE TICKS W0 PERIOD [LIMIT]
// Tracks block identities through successful moves (arms excluded). Blocks whose move-tick sets inside
// [W0, TICKS) are identical AND that are face-connected at tick 0 form a "body". Prints per body: size,
// materials, movement-start mask (one character per tick; 1 means launch) and initial box; then one period of events:
//   slot actor(carrier bodies | power-source bodies) push/pull load -> moved bodies
// "carrier" = bodies owning glue face-adjacent to the actor piston when it acts;
// "power" = bodies owning the source (redstone/rod/observer, or the hard-powered solid) powering it that tick.
use fastflyer::{debug::TickTrace,Block,Coord,Flyer,Kind};
use std::collections::{BTreeMap,BTreeSet};
fn dv(d:u8)->(i64,i64,i64){match d{0=>(1,0,0),1=>(-1,0,0),2=>(0,1,0),3=>(0,-1,0),4=>(0,0,1),_=>(0,0,-1)}}
fn add(c:Coord,d:u8)->Coord{let(x,y,z)=dv(d);Coord::new(c.x+x,c.y+y,c.z+z)}
struct Ev{t:usize,actor:usize,pull:bool,moved:Vec<usize>,fail:Option<String>,carriers:Vec<usize>,power:Vec<usize>}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<String>=std::env::args().collect();
 let mut f=Flyer::load(&a[1])?;
 let ticks:usize=a[2].parse()?;let w0:usize=a[3].parse()?;let period:usize=a[4].parse()?;
 if let Some(l)=a.get(5){f.push_limit=l.parse()?;}
 let mut ids:BTreeMap<Coord,usize>=BTreeMap::new();let mut kinds:Vec<Block>=vec![];let mut init:Vec<Coord>=vec![];
 for (p,b) in f.blocks(){if b.kind()!=Kind::PistonArm{ids.insert(p,kinds.len());kinds.push(b);init.push(p);}}
 let n=kinds.len();
 let glue=|k:Kind|k==Kind::Slime||k==Kind::Honey;
 let mut moves:Vec<BTreeSet<usize>>=vec![BTreeSet::new();n];
 let mut events:Vec<Ev>=vec![];
 let x0=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();
 for t in 0..ticks{
  let ids_start=ids.clone();
  let mut world:BTreeMap<Coord,Block>=f.blocks().into_iter().collect();
  let mut tr=TickTrace::new(&f);f.tick_traced(&mut tr,t)?;
  // power attribution at tick start: piston id -> source ids
  let mut pw:BTreeMap<usize,Vec<usize>>=BTreeMap::new();
  if let Some(step)=tr.steps.iter().find(|s|s.info.power.is_some()){
   let power=step.info.power.as_ref().unwrap();
   let mut hard_from:BTreeMap<Coord,Coord>=BTreeMap::new();
   for l in &power.links{if l.kind=="hard"{hard_from.insert(l.to,l.from);}}
   for l in &power.links{
    if l.kind=="soft"||l.kind=="hard→piston"{
     if let Some(&pid)=ids_start.get(&l.to){
      let mut srcs=vec![];
      if let Some(&sid)=ids_start.get(&l.from){srcs.push(sid);}
      if l.kind=="hard→piston"{if let Some(o)=hard_from.get(&l.from){if let Some(&oid)=ids_start.get(o){srcs.push(oid);}}}
      pw.entry(pid).or_default().extend(srcs);
     }
    }
   }
  }
  for step in tr.steps{
   if let Some(m)=&step.info.movement{
    let p=step.info.active_piston.unwrap();
    let pb=world.get(&p).copied().unwrap();
    let retract=step.info.title.contains("retract");
    let actor=*ids.get(&p).unwrap_or(&usize::MAX);
    let mut carriers=vec![];
    for d in 0..6u8{if d==pb.direction(){continue}let q=add(p,d);if let (Some(b),Some(&id))=(world.get(&q),ids.get(&q)){if glue(b.kind())&&!b.moving(){carriers.push(id);}}}
    let power=pw.get(&actor).cloned().unwrap_or_default();
    if let Some((c,w))=&m.failure{events.push(Ev{t,actor,pull:retract,moved:vec![],fail:Some(format!("FAIL {w}@({},{},{})",c.x,c.y,c.z)),carriers,power});}
    else if !m.sources.is_empty(){
     let (mut vx,mut vy,mut vz)=dv(pb.direction()); if retract{vx=-vx;vy=-vy;vz=-vz;}
     let mut moved=vec![];
     for s in &m.sources{if let Some(id)=ids.remove(s){moved.push((id,Coord::new(s.x+vx,s.y+vy,s.z+vz)));}}
     let mut mv=vec![];
     for (id,q) in moved{ids.insert(q,id);moves[id].insert(t);mv.push(id);}
     events.push(Ev{t,actor,pull:retract,moved:mv,fail:None,carriers,power});
    } else if !retract { events.push(Ev{t,actor,pull:false,moved:vec![],fail:None,carriers,power}); }
   }
   for ch in step.changes{if let Some(c)=ch.cell{world.insert(ch.pos,Block::from_cell(c)?);}else{world.remove(&ch.pos);}}
  }
 }
 let x1=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();
 let mut groups:BTreeMap<Vec<usize>,Vec<usize>>=BTreeMap::new();
 for id in 0..n{let key:Vec<usize>=moves[id].iter().filter(|&&t|t>=w0).cloned().collect();groups.entry(key).or_default().push(id);}
 let mut split:Vec<(Vec<usize>,Vec<usize>)>=vec![];
 for (k,members) in groups{
  let set:BTreeSet<Coord>=members.iter().map(|&i|init[i]).collect();
  let byc:BTreeMap<Coord,usize>=members.iter().map(|&i|(init[i],i)).collect();
  let mut seen:BTreeSet<Coord>=BTreeSet::new();
  for &i in &members{let c0=init[i];if seen.contains(&c0){continue}
   let mut comp=vec![];let mut st=vec![c0];seen.insert(c0);
   while let Some(c)=st.pop(){comp.push(byc[&c]);for d in 0..6u8{let q=add(c,d);if set.contains(&q)&&!seen.contains(&q){seen.insert(q);st.push(q);}}}
   split.push((k.clone(),comp));}
 }
 let pos:BTreeMap<usize,Coord>=ids.iter().map(|(c,i)|(*i,*c)).collect();
 split.sort_by_key(|(_,m)|{let s:i64=m.iter().map(|i|pos.get(i).map(|c|c.x).unwrap_or(0)).sum();(s*1000/(m.len() as i64), m.iter().map(|&i|init[i]).min())});
 let mut body=vec![0usize;n];
 println!("distance {} over {} ticks; bodies (rear->front by mean x):",x1-x0,ticks);
 let names=["air","sl","ho","st","gl","gz","RB","ob","rod","P","arm"];
 for (bi,(mt,members)) in split.iter().enumerate(){
  for &i in members{body[i]=bi;}
  let mut cnt=[0usize;11];let mut pst=(0,0);
  for &i in members{let b=kinds[i];cnt[b.kind() as usize]+=1;if b.kind()==Kind::Piston{if b.sticky(){pst.1+=1}else{pst.0+=1}}}
  let mats:Vec<String>=(1..9).filter(|&k|cnt[k]>0).map(|k|format!("{}{}",names[k],cnt[k])).collect();
  let mut word=vec!['0';period];for &t in mt{if t>=w0{word[t%period]='1';}}
  let xs:Vec<i64>=members.iter().map(|&i|init[i].x).collect();let ys:Vec<i64>=members.iter().map(|&i|init[i].y).collect();let zs:Vec<i64>=members.iter().map(|&i|init[i].z).collect();
  let at=if members.len()==1{format!("at({},{},{})",xs[0],ys[0],zs[0])}else{format!("box x{}-{} y{}-{} z{}-{}",xs.iter().min().unwrap(),xs.iter().max().unwrap(),ys.iter().min().unwrap(),ys.iter().max().unwrap(),zs.iter().min().unwrap(),zs.iter().max().unwrap())};
  let pk=if members.len()==1&&kinds[members[0]].kind()==Kind::Piston{if kinds[members[0]].sticky(){" [sticky piston]"}else{" [normal piston]"}}else{""};
  println!("  B{bi}: n={} {} P={} S={} start_mask={} {}{}",members.len(),mats.join(" "),pst.0,pst.1,word.iter().collect::<String>(),at,pk);
  if std::env::var("BT_CELLS").is_ok()&&members.len()>1{let mut v:Vec<String>=members.iter().map(|&i|{let b=kinds[i];let k=match b.kind(){Kind::Piston=>format!("{}{}",if b.sticky(){"S"}else{"P"},["+x","-x","+y","-y","+z","-z"][b.direction() as usize]),k=>names[k as usize].to_string()};format!("({},{},{}){}",init[i].x,init[i].y,init[i].z,k)}).collect();v.sort();println!("      cells: {}",v.join(" "));}
 }
 let bl=|v:&Vec<usize>|{let s:BTreeSet<usize>=v.iter().map(|&i|body[i]).collect();s.iter().map(|b|format!("B{b}")).collect::<Vec<_>>().join("/")};
 println!("events in one period from tick {} (tick actor(carriers|power) action load -> moved):",w0);
 for e in &events{
  if e.t<w0||e.t>=w0+period{continue}
  let ab=if e.actor==usize::MAX{"?".to_string()}else{format!("B{}",body[e.actor])};
  let mut per:BTreeMap<usize,usize>=BTreeMap::new();for i in &e.moved{*per.entry(body[*i]).or_default()+=1;}
  let s:Vec<String>=per.iter().map(|(b,c)|format!("B{b}x{c}")).collect();
  let act=if e.pull{"pull"}else if e.moved.is_empty()&&e.fail.is_none(){"ext0"}else{"push"};
  println!("  t{} {ab}({}|{}) {act} {:<3} -> {} {}",e.t%period,bl(&e.carriers),bl(&e.power),e.moved.len(),s.join(","),e.fail.clone().unwrap_or_default());
 }
 Ok(())
}
