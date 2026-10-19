//! Strict standard-sample verification without hardware search or limit raising.
use fastflyer_tools::{contract::*, solve::{verify, ORDERS}};
use std::{fs, path::PathBuf, time::{Duration, Instant}};

fn main() -> Result<(), String> {
    let a: Vec<String> = std::env::args().skip(1).collect();
    if !(2..=4).contains(&a.len()) { return Err("contract-verify PROBLEM OUT_JSON [SECONDS] [THREADS]".into()); }
    let problem = PathBuf::from(&a[0]); let output = PathBuf::from(&a[1]);
    let seconds: f64 = a.get(2).map(|s| s.parse()).transpose().map_err(|_| "seconds")?.unwrap_or(600.0);
    let threads: usize = a.get(3).map(|s| s.parse()).transpose().map_err(|_| "threads")?.unwrap_or(4);
    if !seconds.is_finite() || seconds <= 0.0 || threads == 0 { return Err("positive budget and threads required".into()); }
    let mut ctx = load_ctx(&problem,None)?;
    ctx.soft = false; ctx.allow_ext_fail = false;
    ctx.orders = if ctx.events.is_empty() { vec![ORDERS[0]] } else { ORDERS.to_vec() };
    let start = Instant::now();
    let (pass,total,fail,all_max,endogenous_max) = verify(&ctx,&ctx.base_cells,threads,start+Duration::from_secs_f64(seconds));
    let verified = pass == total && fail.is_none() && all_max <= ctx.push_limit;
    let result = format!("{{\"verified\":{verified},\"passed\":{pass},\"total\":{total},\"orders_per_sample\":{},\"ticks_per_order\":{},\"encoded_limit\":{},\"max_action\":{all_max},\"max_endogenous_action\":{endogenous_max},\"elapsed_seconds\":{},\"failure\":{}}}\n",
        ctx.orders.len(),ctx.period*ctx.cycles,ctx.push_limit,start.elapsed().as_secs_f64(),fail.as_deref().map(jstr).unwrap_or("null".into()));
    if let Some(parent) = output.parent() { fs::create_dir_all(parent).map_err(|e| e.to_string())?; }
    fs::write(output,&result).map_err(|e| e.to_string())?;
    println!("{result}");
    if verified { Ok(()) } else { Err("verification failed or incomplete; inspect report".into()) }
}
