// One-interface mwmw diagnostic. A scripted temporary piston drives B through
// real Rust movement in each B slot; installing/removing it is a fixture action.
use fastflyer::{debug::TickTrace, Block, Coord, Flyer, Kind};

fn c(x:i64,y:i64,z:i64)->Coord { Coord::new(x,y,z) }
fn b(f:&Flyer,p:Coord)->Block { f.get(p).unwrap_or_else(|| panic!("missing {p:?}")) }

fn install_b_driver(f:&mut Flyer, bx:i64, pickup:Coord) {
    let h=c(bx,0,0); let o=c(bx,-1,0);
    assert_eq!(b(f,h).kind(),Kind::Honey);
    assert_eq!(b(f,o).kind(),Kind::Observer);
    let p=b(f,pickup);
    assert_eq!(p.kind(),Kind::Piston);
    assert_eq!(p.state(),0,"external B should pick only retracted piston");
    assert!(!p.moving());
    assert_eq!((pickup.x-bx).abs()+(pickup.y-h.y).abs()+(pickup.z-h.z).abs(),1);
    let other=if pickup.y==1 { c(bx,0,1) } else { c(bx,1,0) };
    let retractor=b(f,other);
    assert_eq!(retractor.kind(),Kind::Piston);
    assert_eq!(retractor.state(),2,"the other honey neighbour must be immovable during B pickup");
    for d in [c(-1,0,0),c(1,0,0),c(0,-1,0),c(0,1,0),c(0,0,-1),c(0,0,1)] {
        let n=c(bx+d.x,d.y,d.z);
        if n!=o && n!=pickup && n!=other { assert!(f.get(n).is_none(),"unexpected H neighbour {n:?}"); }
    }
    let base=c(bx-1,0,0); let power=c(bx-2,0,0);
    assert!(f.get(base).is_none()); assert!(f.get(power).is_none());
    for pos in [h,o,pickup] { assert!(f.get(c(pos.x+1,pos.y,pos.z)).is_none(),"driver destination blocked at {pos:?}"); }
    f.set(base,Block::piston(0,false,false,0,false).unwrap());
    f.set(power,Block::plain(Kind::RedstoneBlock,false).unwrap());
    println!("  SCRIPT installed temporary B driver {:?} + power {:?}; expected pickup {:?}",base,power,pickup);
}

fn remove_b_driver(f:&mut Flyer,bx:i64) {
    let base=c(bx-1,0,0); let power=c(bx-2,0,0); let arm=c(bx,0,0);
    assert_eq!(b(f,base).state(),2);
    assert_eq!(b(f,arm).kind(),Kind::PistonArm);
    assert_eq!(b(f,power).kind(),Kind::RedstoneBlock);
    assert!(b(f,c(bx+1,-1,0)).powered(),"moved O must pulse naturally when B finishes");
    for pos in [base,arm,power] { f.remove(pos).unwrap(); }
    println!("  SCRIPT removed temporary B driver after real 2-tick move; O powered=true");
}

fn main()->Result<(),Box<dyn std::error::Error>> {
    let mut f=Flyer::new(8,8,5,12)?;
    f.set(c(0,0,0),Block::plain(Kind::Honey,false)?);
    f.set(c(0,-1,0),Block::observer(2,true,false)?);
    f.set(c(0,0,1),Block::piston(0,false,false,0,false)?);
    f.set(c(-1,1,0),Block::piston(0,false,false,0,false)?);
    for p in [c(-1,1,1),c(0,1,1),c(1,1,1),c(1,0,1),c(1,1,0)] {
        f.set(p,Block::plain(Kind::Slime,false)?);
    }
    let initial=f.occupied_count();
    let mut initial_shape:Vec<_>=f.blocks().into_iter().map(|(p,v)|(p,v.cell())).collect();
    initial_shape.sort();
    let mut bx=0;
    for t in 0..16 {
        if t==8 {
            let mut shape:Vec<_>=f.blocks().into_iter().map(|(p,v)|(c(p.x-2,p.y,p.z),v.cell())).collect();
            shape.sort();
            assert_eq!(shape,initial_shape,"8-tick shape must repeat translated +2 X");
            println!("T8 SHAPE matches initial state translated +2 X");
        }
        if t%4==2 {
            // Slot 1 picks P1 after A's P0 push; slot 3 picks P0 after P1's push.
            let pickup=if t%8==2 { c(bx,1,0) } else { c(bx,0,1) };
            install_b_driver(&mut f,bx,pickup);
        }
        let mut tr=TickTrace::new(&f);
        let report=f.tick_traced(&mut tr,t)?;
        println!("T{t} ext={} fail={} ret={} Bx={bx}",report.extensions_started,report.extension_failures,report.retractions_started);
        for step in &tr.steps {
            if let Some(m)=&step.info.movement {
                if !m.sources.is_empty()||m.failure.is_some() {
                    println!("  {} piston={:?} n={} sources={:?} failure={:?}",step.info.title,step.info.active_piston,m.sources.len(),m.sources,m.failure);
                }
            }
        }
        for (p,v) in f.blocks() {
            if v.kind()==Kind::Piston { println!("  piston {:?} state={} moving={} angry={}",p,v.state(),v.moving(),v.angry()); }
        }
        if t%4==3 { remove_b_driver(&mut f,bx); bx+=1; }
        assert_eq!(f.occupied_count(),initial+(if t%4==0||t%4==1 {1} else if t%4==2 {3} else {0}),"block count incl arm and temporary driver");
    }
    Ok(())
}
