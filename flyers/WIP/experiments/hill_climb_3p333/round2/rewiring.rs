//! Screen a one-cell reduction plus one local support or power edit on seed zero.
use fastflyer::{Block, Coord, Flyer, Kind};
use std::collections::{BTreeMap, BTreeSet};
use std::{env, fs};
const DIR: [(i64, i64, i64); 7] = [
    (1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
    (0, 0, 0),
];
fn at(p: Coord, d: (i64, i64, i64)) -> Coord {
    Coord::new(p.x + d.0, p.y + d.1, p.z + d.2)
}
fn members(f: &Flyer) -> BTreeMap<Coord, u16> {
    f.blocks()
        .into_iter()
        .filter(|(_, b)| !matches!(b.kind(), Kind::Piston | Kind::PistonArm))
        .map(|(p, b)| (p, b.cell() & !0x110))
        .collect()
}
fn copy(f: &Flyer) -> Flyer {
    let mut g = Flyer::new(f.phase_x, f.phase_z, f.rng_state, f.push_limit).unwrap();
    for (p, b) in f.blocks() {
        g.set(p, b);
    }
    g
}
fn clean(f: &Flyer, ticks: usize, phase: u8) -> bool {
    let mut w = copy(f);
    w.phase_x = phase;
    w.phase_z = phase;
    w.rng_state = 0;
    let initial = members(&w);
    for tick in 1..=ticks {
        let report = w.tick().unwrap();
        if report.extension_failures > 0 {
            return false;
        }
        if tick % 12 == 0 {
            let dx = (tick / 3) as i64;
            for (p, cell) in &initial {
                if w.get(at(*p, (dx, 0, 0))).map_or(0, |b| b.cell()) & !0x110 != *cell {
                    return false;
                }
            }
        }
    }
    true
}
#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
struct Change {
    cut: Coord,
    from: Coord,
    to: Coord,
    block: u16,
    face: Option<(Coord, Coord)>,
}
fn apply(f: &mut Flyer, c: Change) {
    f.remove(c.cut);
    let follow = c.face.map(|(old, new)| (f.remove(old).unwrap(), new));
    if c.block != 0 {
        let old = f.remove(c.from);
        if let Some(piston) = old.filter(|b| b.kind() == Kind::Piston && b.state() == 2) {
            let dir = DIR[piston.direction() as usize];
            if let Some(arm) = f.remove(at(c.from, dir)) {
                f.set(at(c.to, dir), arm);
            }
        }
        f.set(c.to, Block::from_cell(c.block).unwrap());
    }
    if let Some((b, new)) = follow {
        f.set(new, b);
    }
}
fn main() {
    let args: Vec<_> = env::args().collect();
    if args[1] == "--track" {
        let base = Flyer::load(&args[2]).unwrap();
        for phase in [0, 7] {
            assert!(clean(&base, 10000, phase));
            println!(
                "phase ({phase},{phase}) verified {} non-piston blocks at 833 period boundaries",
                members(&base).len()
            );
        }
        return;
    }
    let base = Flyer::load(&args[1]).unwrap();
    let text = fs::read_to_string(&args[2]).unwrap();
    let lines: Vec<_> = text
        .lines()
        .skip(1)
        .map(|l| l.split_whitespace().collect::<Vec<_>>())
        .collect();
    let mut raw = Coord::new(999, 999, 999);
    let mut saved = raw;
    for r in &lines {
        if r[1] == "G" {
            raw.x = raw.x.min(r[2].parse().unwrap());
            raw.y = raw.y.min(r[3].parse().unwrap());
            raw.z = raw.z.min(r[4].parse().unwrap());
        }
    }
    for (p, b) in base.blocks() {
        if matches!(b.kind(), Kind::Slime | Kind::Honey) {
            saved.x = saved.x.min(p.x);
            saved.y = saved.y.min(p.y);
            saved.z = saved.z.min(p.z);
        }
    }
    let mut owner = BTreeMap::new();
    for r in &lines {
        if r[1] == "G" || r[1] == "R" {
            let p = at(
                Coord::new(
                    r[2].parse().unwrap(),
                    r[3].parse().unwrap(),
                    r[4].parse().unwrap(),
                ),
                (saved.x - raw.x, saved.y - raw.y, saved.z - raw.z),
            );
            assert!(base.get(p).is_some());
            owner.insert(p, r[0].parse::<usize>().unwrap());
        }
    }
    let n = 1 + owner.values().max().unwrap();
    let mut groups = vec![vec![]; n];
    for (&p, &i) in &owner {
        groups[i].push(p);
    }
    let hot: Vec<_> = (0..n).filter(|&i| groups[i].len() + 4 > 17).collect();
    println!(
        "hot {:?} offset {:?}",
        hot,
        (saved.x - raw.x, saved.y - raw.y, saved.z - raw.z)
    );
    let mut pairs = Vec::new();
    for i in 0..n {
        let mut ports: Vec<_> = lines
            .iter()
            .filter(|r| r[1] == "H" && r[0].parse::<usize>().unwrap() == i)
            .map(|r| {
                Coord::new(
                    r[2].parse().unwrap(),
                    r[3].parse().unwrap(),
                    r[4].parse().unwrap(),
                )
            })
            .collect();
        ports.sort();
        let slot = (6 - 2 * (i % 3)) % 6;
        for (k, p) in ports.iter().enumerate() {
            let f = k + 2;
            let dx = if slot == f + 1 || slot == 1 {
                -1
            } else if slot == 0 || slot > f {
                -2
            } else {
                0
            };
            let anchor = at(*p, (saved.x - raw.x, saved.y - raw.y, saved.z - raw.z));
            pairs.push((at(anchor, (dx, 0, 0)), at(anchor, (1, 0, 0))));
        }
    }
    let mut wins = BTreeMap::<usize, Vec<Change>>::new();
    for &i in &hot {
        let mut choices = BTreeSet::new();
        for &cut in &groups[i] {
            choices.insert(Change {
                cut,
                from: cut,
                to: cut,
                block: 0,
                face: None,
            });
            if args.get(4).is_some_and(|s| s == "faces") {
                for &(from, face) in &pairs {
                    if face == cut {
                        continue;
                    }
                    let block = base.get(from).unwrap();
                    if block.kind() != Kind::Piston {
                        continue;
                    }
                    for x in -4i64..=4 {
                        for y in -4i64..=4 {
                            for z in -4i64..=4 {
                                if x.abs() + y.abs() + z.abs() > 5 {
                                    continue;
                                }
                                let d = (x, y, z);
                                let to = at(from, d);
                                let toface = at(face, d);
                                if to == from
                                    || to == face
                                    || toface == from
                                    || toface == face
                                    || to == toface
                                {
                                    continue;
                                }
                                if [to, toface]
                                    .iter()
                                    .any(|&p| p != cut && base.get(p).is_some())
                                {
                                    continue;
                                }
                                if block.state() == 2 {
                                    let arm = at(to, (1, 0, 0));
                                    if arm == toface || (arm != cut && base.get(arm).is_some()) {
                                        continue;
                                    }
                                }
                                choices.insert(Change {
                                    cut,
                                    from,
                                    to,
                                    block: block.cell(),
                                    face: Some((face, toface)),
                                });
                            }
                        }
                    }
                }
                continue;
            }
            if args.get(4).is_some_and(|s| s == "pistons") {
                for (from, block) in base
                    .blocks()
                    .into_iter()
                    .filter(|(_, b)| b.kind() == Kind::Piston)
                {
                    let arm = DIR[block.direction() as usize];
                    for x in -3i64..=3 {
                        for y in -4i64..=4 {
                            for z in -4i64..=4 {
                                if x.abs() + y.abs() + z.abs() > 4 {
                                    continue;
                                }
                                let to = at(from, (x, y, z));
                                if to == from || (to != cut && base.get(to).is_some()) {
                                    continue;
                                }
                                if block.state() == 2 {
                                    let end = at(to, arm);
                                    if end != from && end != cut && base.get(end).is_some() {
                                        continue;
                                    }
                                }
                                choices.insert(Change {
                                    cut,
                                    from,
                                    to,
                                    block: block.cell(),
                                    face: None,
                                });
                            }
                        }
                    }
                }
                continue;
            }
            for (&from, &j) in &owner {
                if from == cut {
                    continue;
                }
                let old = base.get(from).unwrap();
                let power = matches!(old.kind(), Kind::Rod | Kind::RedstoneBlock | Kind::Observer);
                if !power && i != j {
                    continue;
                }
                for &d in &DIR {
                    let to = at(from, d);
                    if to != from && to != cut && base.get(to).is_some() {
                        continue;
                    }
                    let mut bs = vec![old];
                    if power {
                        bs.push(Block::plain(Kind::RedstoneBlock, false).unwrap());
                        for facing in 0..6 {
                            bs.push(Block::rod(facing, false).unwrap());
                            bs.push(Block::observer(facing, false, false).unwrap());
                        }
                    }
                    for b in bs {
                        if to != from || b != old {
                            choices.insert(Change {
                                cut,
                                from,
                                to,
                                block: b.cell(),
                                face: None,
                            });
                        }
                    }
                }
            }
        }
        let tested = choices.len();
        for c in choices {
            let mut w = copy(&base);
            apply(&mut w, c);
            if clean(&w, 24, 0) && clean(&w, 120, 0) && clean(&w, 120, 7) {
                let nw = wins.entry(i).or_default();
                if nw.len() < 3 {
                    println!("body {i} edit {c:?}");
                }
                nw.push(c);
            }
        }
        println!(
            "body {} tests {} accepted {}",
            i,
            tested,
            wins.get(&i).map_or(0, Vec::len)
        );
    }
    fn combine(
        k: usize,
        hot: &[usize],
        wins: &BTreeMap<usize, Vec<Change>>,
        f: &Flyer,
        out: &str,
        edits: &mut Vec<Change>,
    ) -> bool {
        if k == hot.len() {
            let mut g = copy(f);
            g.push_limit = 17;
            if clean(&g, 240, 0) && clean(&g, 240, 7) {
                g.save(out).unwrap();
                println!("PL17 edits {:?}", edits);
                return true;
            }
            return false;
        }
        if let Some(cs) = wins.get(&hot[k]) {
            for &c in cs {
                if f.get(c.cut).is_none() || c.face.is_some_and(|(old, _)| f.get(old).is_none()) {
                    continue;
                }
                let mut g = copy(f);
                apply(&mut g, c);
                edits.push(c);
                if combine(k + 1, hot, wins, &g, out, edits) {
                    return true;
                }
                edits.pop();
            }
        }
        false
    }
    combine(0, &hot, &wins, &base, &args[3], &mut vec![]);
}
