// hoptrace FILE TICKS W0 PERIOD [LIMIT]
// Glue bodies = same-material face-connected glue components at tick 0 (labelled A,B,C,... by mean x).
// Prints, for every non-glue block, one cell per slot from W0: Fx = fired (extend) pushing body x,
// R = retract action (Rx = sticky pull of body x), rx = moved together with body x, .. = still. Pistons get a second line with
// power at the slot's even tick (P) / odd tick (p) / both (B).
// HOP_REL=X additionally prints positions (dx to body X reference block : y : z) at each slot start.
use fastflyer::{debug::TickTrace,Block,Coord,Flyer,Kind};
use std::collections::{BTreeMap,BTreeSet};
fn dv(d:u8)->(i64,i64,i64){match d{0=>(1,0,0),1=>(-1,0,0),2=>(0,1,0),3=>(0,-1,0),4=>(0,0,1),_=>(0,0,-1)}}
fn add(c:Coord,d:u8)->Coord{let(x,y,z)=dv(d);Coord::new(c.x+x,c.y+y,c.z+z)}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<String>=std::env::args().collect();
 let mut f=Flyer::load(&a[1])?;
 let ticks:usize=a[2].parse()?;let w0:usize=a[3].parse()?;let period:usize=a[4].parse()?;
 if let Some(l)=a.get(5){f.push_limit=l.parse()?;}
 let mut ids:BTreeMap<Coord,usize>=BTreeMap::new();let mut kinds:Vec<Block>=vec![];let mut init:Vec<Coord>=vec![];
 for (p,b) in f.blocks(){if b.kind()!=Kind::PistonArm{ids.insert(p,kinds.len());kinds.push(b);init.push(p);}}
 let n=kinds.len();
 let glue=|k:Kind|k==Kind::Slime||k==Kind::Honey;
 let mut body=vec![usize::MAX;n];let mut nb=0;
 let at:BTreeMap<Coord,usize>=init.iter().enumerate().map(|(i,c)|(*c,i)).collect();
 for i in 0..n{ if !glue(kinds[i].kind())||body[i]!=usize::MAX{continue}
  let mut st=vec![i];body[i]=nb;
  while let Some(j)=st.pop(){for d in 0..6u8{if let Some(&q)=at.get(&add(init[j],d)){if body[q]==usize::MAX&&kinds[q].kind()==kinds[i].kind(){body[q]=nb;st.push(q);}}}}
  nb+=1;}
 let mut mx:Vec<(f64,usize)>=(0..nb).map(|b|{let v:Vec<i64>=(0..n).filter(|&i|body[i]==b).map(|i|init[i].x).collect();(v.iter().sum::<i64>() as f64/v.len() as f64,b)}).collect();
 mx.sort_by(|x,y|x.partial_cmp(y).unwrap());
 let mut lab=vec![' ';nb];for (r,(_,b)) in mx.iter().enumerate(){lab[*b]=(b'A'+r as u8) as char;}
 for (_,b) in &mx{let c=(0..n).filter(|&i|body[i]==*b).count();println!("body {} = {} {} cells",lab[*b],c,if kinds[(0..n).find(|&i|body[i]==*b).unwrap()].kind()==Kind::Slime{"slime"}else{"honey"});}
 let slots=(ticks-w0)/2;
 let mut row:Vec<Vec<String>>=vec![vec!["..".to_string();slots];n];
 let mut gw:Vec<Vec<char>>=vec![vec!['w';slots];nb];
 let mut pwr:Vec<Vec<char>>=vec![vec!['.';slots+1];n];
 let mut posh:Vec<BTreeMap<usize,Coord>>=vec![];
 let x0=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();
 let mut fails=0;
 for t in 0..ticks{
  if t>=w0&&(t-w0)%2==0{posh.push(ids.iter().map(|(c,i)|(*i,*c)).collect());}
  let mut world:BTreeMap<Coord,Block>=f.blocks().into_iter().collect();
  if t>=w0{ let s=(t-w0)/2;
   let solid=|k:Kind|matches!(k,Kind::Slime|Kind::Honey|Kind::SmoothStone|Kind::GlazedTerracotta);
   let mut hard:BTreeSet<Coord>=BTreeSet::new();
   for (c,bk) in &world{ if bk.moving(){continue}
     if bk.kind()==Kind::Rod||(bk.kind()==Kind::Observer&&bk.powered()){let q=add(*c,bk.direction());if let Some(o)=world.get(&q){if solid(o.kind()){hard.insert(q);}}}}
   for (c,bk) in &world{ if bk.kind()!=Kind::Piston||bk.moving(){continue}
     let front=add(*c,bk.direction()); let mut on=false;
     for d in 0..6u8{let q=add(*c,d); if q==front{continue} if let Some(o)=world.get(&q){ if o.moving(){continue}
       if o.kind()==Kind::RedstoneBlock||o.kind()==Kind::Rod{on=true}
       if o.kind()==Kind::Observer&&o.powered()&&add(q,o.direction())==*c{on=true}
       if hard.contains(&q){on=true} }}
     if on{ if let Some(&pid)=ids.get(c){ let cc=&mut pwr[pid][s]; *cc=if (t-w0)%2==0{'P'}else if *cc=='P'{'B'}else{'p'}; } } } }
  let mut tr=TickTrace::new(&f);f.tick_traced(&mut tr,t)?;
  for step in tr.steps{
   if let Some(m)=&step.info.movement{
    let p=step.info.active_piston.unwrap();
    let pb=world.get(&p).copied().unwrap();
    let retract=step.info.title.contains("retract");
    let actor=*ids.get(&p).unwrap_or(&usize::MAX);
    if m.failure.is_some(){fails+=1;}
    let (mut vx,mut vy,mut vz)=dv(pb.direction()); if retract{vx=-vx;vy=-vy;vz=-vz;}
    let mut moved=vec![];
    for s in &m.sources{if let Some(id)=ids.remove(s){moved.push((id,Coord::new(s.x+vx,s.y+vy,s.z+vz)));}}
    let bs:BTreeSet<usize>=moved.iter().filter(|(i,_)|body[*i]!=usize::MAX).map(|(i,_)|body[*i]).collect();
    let bl:String=bs.iter().map(|b|lab[*b]).collect();
    if t>=w0{let s=(t-w0)/2;
     if actor!=usize::MAX{row[actor][s]=if retract{if bl.is_empty(){"R ".to_string()}else{format!("R{}",bl)}}else{format!("F{}",if bl.is_empty(){"-".to_string()}else{bl.clone()})};}
     for (id,_) in &moved{if body[*id]==usize::MAX{row[*id][s]=format!("r{}",if bl.is_empty(){"?".to_string()}else{bl.clone()});}else{gw[body[*id]][s]='m';}}}
    for (id,q) in moved{ids.insert(q,id);}
   }
   for ch in step.changes{if let Some(c)=ch.cell{world.insert(ch.pos,Block::from_cell(c)?);}else{world.remove(&ch.pos);}}
  }
 }
 let x1=f.blocks().iter().map(|(p,_)|p.x).min().unwrap();
 println!("distance {} ticks {} failures {}",x1-x0,ticks,fails);
 for (_,b) in &mx{println!("word {} {}",lab[*b],gw[*b].chunks(period/2).map(|c|c.iter().collect::<String>()).collect::<Vec<_>>().join(" "));}
 let names=["air","sl","ho","st","gl","gz","RB","ob","rod","P","arm"];
 for i in 0..n{ if body[i]!=usize::MAX{continue}
  let b=kinds[i];let k=if b.kind()==Kind::Piston{format!("{}{}",if b.sticky(){"S"}else{"P"},["+x","-x","+y","-y","+z","-z"][b.direction() as usize])}else{names[b.kind() as usize].to_string()};
  println!("{:>3} {:<4} {}",i,k,row[i].chunks(period/2).map(|c|c.join(" ")).collect::<Vec<_>>().join(" | "));
  if b.kind()==Kind::Piston{println!("    pow  {}",pwr[i][..slots].chunks(period/2).map(|c|c.iter().map(|x|format!("{} ",x)).collect::<Vec<_>>().join(" ")).collect::<Vec<_>>().join(" | "));}}
 if let Ok(rl)=std::env::var("HOP_REL"){ let rb=lab.iter().position(|&c|c.to_string()==rl).unwrap();
  let refid=(0..n).filter(|&i|body[i]==rb).min_by_key(|&i|(init[i].x,init[i].y,init[i].z)).unwrap();
  println!("positions relative to body {} reference block (start of each slot), dx:y:z",rl);
  for i in 0..n{ if body[i]==rb{continue} if body[i]!=usize::MAX && std::env::var("HOP_BODIES").is_err(){continue}
   let v:Vec<String>=posh.iter().map(|m|{let c=m[&i];let r=m[&refid];format!("{}:{}:{}",c.x-r.x,c.y,c.z)}).collect();
   println!("{:>3} {}",i,v.chunks(period/2).map(|c|c.join(" ")).collect::<Vec<_>>().join(" | "));}}
 Ok(())
}
