//! Export one deterministic column proposal with its actual partial scaffold.
//! Diagnostic only; no search or design acceptance.
use fastflyer_tools::{columns, contract::*, solve::*};
use std::{fs, path::PathBuf};

fn main() -> Result<(), String> {
    let a: Vec<String> = std::env::args().skip(1).collect();
    if a.len() != 7 && !(a.len() == 9 && a[7] == "--target-port") { return Err("column-witness PROBLEM OUT START COUNT DUAL INDEX_OR_HARDWARE_JSON_OR_first-pass LIMIT [--target-port INDEX]".into()); }
    let problem = PathBuf::from(&a[0]); let out = PathBuf::from(&a[1]);
    let start: usize = a[2].parse().map_err(|_| "start")?;
    let count: usize = a[3].parse().map_err(|_| "count")?;
    let dual: bool = a[4].parse().map_err(|_| "dual")?;
    let limit: u64 = a[6].parse().map_err(|_| "limit")?;
    let mut ctx = load_ctx(&problem, None)?; ctx.push_limit = limit;
    let target_port: Option<usize> = a.get(8).map(|s| s.parse()).transpose().map_err(|_| "target port")?;
    let moves: Vec<Move> = internal_moves(&ctx).into_iter().filter(|m| target_port.map_or(true, |p| m.0 == p)).collect();
    if moves.len() != 3 || moves.iter().any(|m| m.0 != moves[0].0) {
        return Err("requires one three-move body extension".into());
    }
    let bodies = port_bodies(&ctx, &ctx.base_cells);
    let body = bodies.iter().find(|b| b.port == moves[0].0).ok_or("body")?;
    if !(2..=3).contains(&count) || start >= body.word.len() || !(0..count).all(|j| body.word[(start+j)%body.word.len()]) {
        return Err("invalid burst".into());
    }
    let proposals = columns::candidates(&ctx.base_cells, body, count, dual);
    let natural: Vec<bool> = moves.iter().map(|m| (0..count).any(|j| m.1 == (start+j)%body.word.len())).collect();
    let mut sc = scaffold_ctx(&ctx, &moves, &natural); sc.allow_ext_fail = false;
    let sample = Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz };
    let index: usize = if a[5] == "first-pass" {
        proposals.iter().position(|c| evaluate(&sc,c,sample,false).is_ok()).ok_or("no passing proposal")?
    } else if let Ok(i) = a[5].parse::<usize>() { i } else {
        let text = fs::read_to_string(&a[5]).map_err(|e| e.to_string())?;
        let parsed = parse_json(&text)?;
        let mut wanted = ctx.base_cells.clone();
        for row in parsed.arr().ok_or("hardware array")? {
            let r = row.arr().filter(|r| r.len() == 4).ok_or("hardware row")?;
            let p = fastflyer::Coord::new(r[0].int().ok_or("x")?,r[1].int().ok_or("y")?,r[2].int().ok_or("z")?);
            if wanted.contains_key(&p) { return Err("hardware overlaps base".into()); }
            wanted.insert(p, u16::try_from(r[3].int().ok_or("cell")?).map_err(|_| "cell range")?);
        }
        proposals.iter().position(|c| *c == wanted).ok_or("hardware not in generated column family")?
    };
    let cells = proposals.get(index).ok_or("proposal index out of range")?;
    let outcome = match evaluate(&sc, cells, sample, false) {
        Ok(ev) => format!("PASS diagnostic load {}", ev.max_load), Err(e) => e.msg,
    };
    fs::create_dir_all(&out).map_err(|e| e.to_string())?;
    let text = fs::read_to_string(&problem).map_err(|e| e.to_string())?;
    let mut parsed = parse_json(&text)?;
    let script = parsed.get("prescribed_script").and_then(J::str).ok_or("requires prescribed extension")?.to_owned();
    if let J::Obj(fields) = &mut parsed {
        fields.retain(|(key,_)| key != "cycles");
        fields.push(("cycles".into(), J::Num(sc.cycles as i64)));
        // A partially supplied body keeps its complete motion word. Mark it
        // as an input in the exported diagnostic so the supplied row is legal.
        if let Some((_,J::Arr(ports))) = fields.iter_mut().find(|(k,_)| k == "ports") {
            if let J::Obj(port) = &mut ports[moves[0].0] {
                port.retain(|(key,_)| key != "role");
                port.push(("role".into(),J::Str("input".into())));
            }
        }
    }
    let probe = out.join("probe.json");
    fs::write(&probe, ser(&parsed).replace(&jstr(&script), &jstr("probe_drive.txt"))).map_err(|e| e.to_string())?;
    let mut events: Vec<_> = sc.events.iter().filter(|(t,_,_)| t+1 < sc.cycles*sc.period).copied().collect();
    events.sort();
    let drive = events.iter().map(|(t,p,l)| format!("{t} {} {} {} {l}",p.x,p.y,p.z)).collect::<Vec<_>>().join("\n");
    fs::write(out.join("probe_drive.txt"), drive+"\n").map_err(|e| e.to_string())?;
    write_solution(&sc, &probe, &out, cells, limit)?;
    let hardware = cells.iter().filter(|(p,_)| !ctx.base_cells.contains_key(p)).map(|(p,c)| format!("[{},{},{},{}]",p.x,p.y,p.z,c)).collect::<Vec<_>>().join(",");
    fs::write(out.join("witness.json"),format!("{{\"diagnostic_only\":true,\"proposal\":{index},\"start\":{start},\"count\":{count},\"dual\":{dual},\"limit\":{limit},\"outcome\":{},\"hardware\":[{hardware}]}}\n",jstr(&outcome))).map_err(|e| e.to_string())?;
    println!("{outcome}");
    Ok(())
}
