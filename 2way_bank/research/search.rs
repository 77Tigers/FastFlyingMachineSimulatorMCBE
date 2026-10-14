use fastflyer::{Block, Coord, Flyer, Kind};
use fastflyer_tools::{kind_counts, min_x, Result};
use std::io::Write;
const DIRS: [(i64,i64,i64);6] = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)];
fn setup(base: &[(Coord,Block)], sticky: usize, state: usize, mirror: bool) -> Option<Flyer> {
    let mut f=Flyer::with_defaults(); f.push_limit=12; f.rng_state=42;
    let mut pi=0; let mut oi=0;
    let np=base.iter().filter(|(_,b)| b.kind()==Kind::Piston).count();
    for &(mut p,mut b) in base {
        if b.kind()==Kind::PistonArm {continue}
        if b.kind()==Kind::Piston {
            b=Block::piston(b.direction(), sticky>>pi&1!=0, b.angry(), if state>>pi&1!=0 {2} else {0},false).ok()?; pi+=1;
        } else if b.kind()==Kind::Observer {
            b=Block::observer(b.direction(), state>>(np+oi)&1!=0,false).ok()?; oi+=1;
        } else {b=b.with_moving(false)}
        if mirror {p.x=-p.x; if matches!(b.kind(),Kind::Piston|Kind::Observer|Kind::Rod) && b.direction()<2 { b=Block::from_cell(b.cell()^32).ok()?; }}
        f.set(p,b);
    }
    for (p,b) in f.blocks() {
        if b.kind()==Kind::Piston && b.state()==2 {
            let d=DIRS[b.direction() as usize]; let q=Coord::new(p.x+d.0,p.y+d.1,p.z+d.2);
            if f.get(q).is_some(){return None}
            f.set(q,Block::plain(Kind::PistonArm,false).ok()?);
        }
    }
    Some(f)
}
fn eval(mut f: Flyer, ticks:usize)->Option<i64>{
    let x=min_x(&f); let kc=kind_counts(&f);
    for t in 0..ticks {
        let r=f.tick().ok()?;
        if r.extension_failures>0 || kind_counts(&f)!=kc{return None}
        if t==39 && (min_x(&f)-x).abs()<3{return None}
    }
    Some(min_x(&f)-x)
}
fn main()->Result<()> {
    let a:Vec<String>=std::env::args().collect();
    if a.get(1).is_some_and(|s|s=="snapshot") {
        let mut f=Flyer::load(&a[2])?;
        for _ in 0..a[4].parse::<usize>()? {f.tick()?;}
        f.save(&a[3])?;return Ok(())
    }
    let dir=a.get(1).map(|s|s.as_str()).unwrap_or("2way_bank/seeds");
    let out=a.get(2).map(|s|s.as_str()).unwrap_or("2way_bank/candidates"); std::fs::create_dir_all(out)?;
    let mut log=std::fs::File::create(format!("{out}/search.csv"))?;
    writeln!(log,"seed,sticky_mask,best_positive,best_negative,positive_state,negative_state")?;
    for path in fastflyer_tools::flyers_in(dir)? {
        let f=Flyer::load(&path)?; let base=f.blocks();
        let np=base.iter().filter(|(_,b)|b.kind()==Kind::Piston).count();
        let no=base.iter().filter(|(_,b)|b.kind()==Kind::Observer).count();
        if np+no>13 || np>8 {continue}
        let stem=std::path::Path::new(&path).file_stem().unwrap().to_str().unwrap();
        let mut pairs=0; let mut moving=0;
        for sticky in 0..1usize<<np {
            let mut pos=(0,0); let mut neg=(0,0);
            for state in 0..1usize<<(np+no) {
                if let Some(f)=setup(&base,sticky,state,false) {
                    if let Some(dx)=eval(f,120) {
                        if dx>pos.0 {pos=(dx,state)}
                        if dx<neg.0 {neg=(dx,state)}
                    }
                }
            }
            if pos.0>0 || neg.0<0 { moving+=1; writeln!(log,"{stem},{sticky},{},{},{},{}",pos.0,neg.0,pos.1,neg.1)?;log.flush()?; }
            if pos.0>0 && neg.0<0 {
                pairs+=1;
                setup(&base,sticky,pos.1,false).unwrap().save(format!("{out}/{stem}_s{sticky}_A.flyer"))?;
                setup(&base,sticky,neg.1,true).unwrap().save(format!("{out}/{stem}_s{sticky}_B.flyer"))?;
                println!("PAIR {stem} sticky={sticky} dx120=({}, {}) states=({}, {})",pos.0,-neg.0,pos.1,neg.1);
            }
        }
        println!("DONE {stem} pistons={np} observers={no} moving_hardware={moving} pairs={pairs}");
    }
    Ok(())
}
