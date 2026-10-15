//! Contract evaluator shared by contract-search and contract-solve (moved from bin/contract-search.rs).
//! Mirrors tools/extension_contract.py in prescribed mode. Research tool only.
#![allow(dead_code, clippy::all)]
// (origin) Local search that minimises load for an extension contract in prescribed mode.
// usage: contract-search CONTRACT.json SECONDS THREADS OUT_DIR
//          [--seed N] [--margin M] [--order before|after|both|interleaved] [--recurrence exact|bounded]
//          [--move-pistons] [--dump-fails] [--neighborhood] [--eval-only] [--samples] [--rng N --phase-x N --phase-z N]
//
// In-process evaluator that mirrors tools/extension_contract.py (prescribed mode): it drives a
// PrescribedSession with the contract's script, follows permanent identities through every
// successful move, checks port words, input load budgets and recurrence, and scores a candidate
// lexicographically by (max single-action load, #actions at that max, blocks, sum of loads).
// Research tool only: uses the public simulator API; does not change the simulator.
use fastflyer::{
    debug::TickTrace, Block, Coord, Flyer, Kind, PrescribedMove, PrescribedOrder,
    PrescribedOutcome, PrescribedSession,
};
use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};




// ---------------------------------------------------------------- minimal JSON
#[derive(Clone, Debug)]
pub enum J {
    Null,
    Bool(bool),
    Num(i64),
    Str(String),
    Arr(Vec<J>),
    Obj(Vec<(String, J)>),
}
impl J {
    pub fn get(&self, key: &str) -> Option<&J> {
        match self {
            J::Obj(v) => v.iter().find(|(k, _)| k == key).map(|(_, v)| v),
            _ => None,
        }
    }
    pub fn str(&self) -> Option<&str> {
        if let J::Str(s) = self { Some(s) } else { None }
    }
    pub fn int(&self) -> Option<i64> {
        if let J::Num(n) = self { Some(*n) } else { None }
    }
    pub fn arr(&self) -> Option<&Vec<J>> {
        if let J::Arr(a) = self { Some(a) } else { None }
    }
}
pub struct Parser<'a> {
    pub s: &'a [u8],
    pub i: usize,
}
impl<'a> Parser<'a> {
    fn ws(&mut self) {
        while self.i < self.s.len() && (self.s[self.i] as char).is_whitespace() {
            self.i += 1;
        }
    }
    fn expect(&mut self, c: u8) -> Result<(), String> {
        self.ws();
        if self.s.get(self.i) == Some(&c) {
            self.i += 1;
            Ok(())
        } else {
            Err(format!("json: expected '{}' at byte {}", c as char, self.i))
        }
    }
    fn value(&mut self) -> Result<J, String> {
        self.ws();
        match self.s.get(self.i).copied() {
            None => Err("json: unexpected end".into()),
            Some(b'{') => {
                self.i += 1;
                let mut out = vec![];
                self.ws();
                if self.s.get(self.i) == Some(&b'}') {
                    self.i += 1;
                    return Ok(J::Obj(out));
                }
                loop {
                    self.ws();
                    let k = match self.value()? {
                        J::Str(s) => s,
                        _ => return Err("json: object key must be string".into()),
                    };
                    self.expect(b':')?;
                    let v = self.value()?;
                    out.push((k, v));
                    self.ws();
                    match self.s.get(self.i) {
                        Some(b',') => self.i += 1,
                        Some(b'}') => {
                            self.i += 1;
                            return Ok(J::Obj(out));
                        }
                        _ => return Err(format!("json: bad object at byte {}", self.i)),
                    }
                }
            }
            Some(b'[') => {
                self.i += 1;
                let mut out = vec![];
                self.ws();
                if self.s.get(self.i) == Some(&b']') {
                    self.i += 1;
                    return Ok(J::Arr(out));
                }
                loop {
                    out.push(self.value()?);
                    self.ws();
                    match self.s.get(self.i) {
                        Some(b',') => self.i += 1,
                        Some(b']') => {
                            self.i += 1;
                            return Ok(J::Arr(out));
                        }
                        _ => return Err(format!("json: bad array at byte {}", self.i)),
                    }
                }
            }
            Some(b'"') => {
                self.i += 1;
                let mut out = String::new();
                loop {
                    let c = *self.s.get(self.i).ok_or("json: unterminated string")?;
                    self.i += 1;
                    match c {
                        b'"' => return Ok(J::Str(out)),
                        b'\\' => {
                            let e = *self.s.get(self.i).ok_or("json: bad escape")?;
                            self.i += 1;
                            match e {
                                b'n' => out.push('\n'),
                                b't' => out.push('\t'),
                                b'r' => out.push('\r'),
                                b'u' => {
                                    let h = std::str::from_utf8(&self.s[self.i..self.i + 4])
                                        .map_err(|e| e.to_string())?;
                                    let cp = u32::from_str_radix(h, 16).map_err(|e| e.to_string())?;
                                    out.push(char::from_u32(cp).unwrap_or('?'));
                                    self.i += 4;
                                }
                                other => out.push(other as char),
                            }
                        }
                        _ => {
                            // collect a full utf-8 sequence
                            let start = self.i - 1;
                            let mut end = self.i;
                            while end < self.s.len() && (self.s[end] & 0xC0) == 0x80 {
                                end += 1;
                            }
                            out.push_str(std::str::from_utf8(&self.s[start..end]).map_err(|e| e.to_string())?);
                            self.i = end;
                        }
                    }
                }
            }
            Some(b't') if self.s[self.i..].starts_with(b"true") => {
                self.i += 4;
                Ok(J::Bool(true))
            }
            Some(b'f') if self.s[self.i..].starts_with(b"false") => {
                self.i += 5;
                Ok(J::Bool(false))
            }
            Some(b'n') if self.s[self.i..].starts_with(b"null") => {
                self.i += 4;
                Ok(J::Null)
            }
            Some(c) if c == b'-' || c.is_ascii_digit() => {
                let st = self.i;
                self.i += 1;
                while self.i < self.s.len() && self.s[self.i].is_ascii_digit() {
                    self.i += 1;
                }
                let int_end = self.i;
                // Non-integers (e.g. index.json "bps") are accepted and truncated; contracts only use integers.
                while self.i < self.s.len() && matches!(self.s[self.i], b'.' | b'e' | b'E' | b'+' | b'-' | b'0'..=b'9') {
                    self.i += 1;
                }
                std::str::from_utf8(&self.s[st..int_end])
                    .unwrap()
                    .parse::<i64>()
                    .map(J::Num)
                    .map_err(|e| e.to_string())
            }
            Some(c) => Err(format!("json: unexpected '{}' at byte {}", c as char, self.i)),
        }
    }
}
pub fn parse_json(text: &str) -> Result<J, String> {
    let mut p = Parser { s: text.as_bytes(), i: 0 };
    let v = p.value()?;
    p.ws();
    if p.i != p.s.len() {
        return Err("json: trailing characters".into());
    }
    Ok(v)
}
pub fn jstr(s: &str) -> String {
    let mut o = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            c if (c as u32) < 0x20 => o.push_str(&format!("\\u{:04x}", c as u32)),
            c => o.push(c),
        }
    }
    o.push('"');
    o
}

// ---------------------------------------------------------------- RNG
pub struct Rng(pub u64);
impl Rng {
    pub fn next(&mut self) -> u64 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 7;
        self.0 ^= self.0 << 17;
        self.0
    }
    pub fn range(&mut self, n: usize) -> usize {
        (self.next() % n as u64) as usize
    }
    pub fn chance(&mut self, p: f64) -> bool {
        (self.next() >> 11) as f64 / (1u64 << 53) as f64 <= p
    }
}

// ---------------------------------------------------------------- contract
pub type Cells = BTreeMap<Coord, u16>;
pub const DIRS: [(i64, i64, i64); 6] = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)];
pub const ARM: u16 = 10;

#[derive(Clone)]
pub struct Port {
    pub name: String,
    pub input: bool,
    pub at: Coord,
    pub word: Vec<bool>,
    pub provenance: Option<Vec<Option<Provenance>>>,
    pub baseline: Option<Vec<Option<u64>>>,
    pub spare: Option<Vec<Option<u64>>>,
    pub prefix: Vec<usize>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Provenance { Internal, Supplied }

#[derive(Clone, Debug)]
pub struct Contact {
    pub name: String,
    pub a: usize,
    pub b: usize,
    pub relation: ContactRelation,
    pub offset: Option<Coord>,
    pub slots: BTreeSet<usize>,
    pub required: bool,
}

#[derive(Clone, Copy, Debug)]
pub enum ContactRelation { Same, Adjacent, Offset }

#[derive(Clone)]
pub struct Ctx {
    pub name: String,
    pub period: usize,
    pub advance: i64,
    pub cycles: usize,
    pub ports: Vec<Port>,
    pub contacts: Vec<Contact>,
    pub required_cells: Vec<(Coord, u16)>,
    pub bounded: bool,
    pub advance_mode: bool,
    pub target: u64,
    pub rank_end: bool,
    pub file_limit: u64,
    pub envelope: Option<(Coord, Coord)>,
    pub schedule: BTreeMap<usize, Vec<PrescribedMove>>,
    pub events: Vec<(usize, Coord, u64)>,
    pub orders: Vec<PrescribedOrder>,
    pub px: u8,
    pub pz: u8,
    pub rng: u64,
    pub push_limit: u64,
    pub owners: BTreeMap<Coord, Vec<Coord>>,
    pub base_cells: Cells,
    /// Soft scoring (search only): keep simulating past port-word and recurrence errors; Progress.checks_ok
    /// then counts per-(port,tick) move/wait correctness and Progress.soft_penalty counts recurrence misses.
    pub soft: bool,
    /// Scaffold contexts only: a powered piston that cannot extend is not a failure (supplied strokes may
    /// already have moved its target). The final natural check never sets this.
    pub allow_ext_fail: bool,
}

pub fn order_name(o: PrescribedOrder) -> &'static str {
    match o {
        PrescribedOrder::BeforeNatural => "before_natural",
        PrescribedOrder::AfterNatural => "after_natural",
        PrescribedOrder::Interleaved => "interleaved",
    }
}
pub fn coord_arr(j: &J, what: &str) -> Result<Coord, String> {
    let a = j.arr().ok_or(format!("{what}: expected [x,y,z]"))?;
    if a.len() != 3 {
        return Err(format!("{what}: expected [x,y,z]"));
    }
    let g = |i: usize| a[i].int().ok_or(format!("{what}: expected integers"));
    Ok(Coord::new(g(0)?, g(1)?, g(2)?))
}
pub fn provenance(j: Option<&J>, slots: usize, word: &[bool], what: &str) -> Result<Option<Vec<Option<Provenance>>>, String> {
    let Some(j) = j else { return Ok(None) };
    let a = j.arr().filter(|a| a.len() == slots).ok_or(format!("{what}: expected {slots} entries"))?;
    let mut out = Vec::with_capacity(slots);
    for (i, item) in a.iter().enumerate() {
        let value = match item {
            J::Null if !word[i] => None,
            J::Str(s) if word[i] && s == "internal" => Some(Provenance::Internal),
            J::Str(s) if word[i] && s == "supplied" => Some(Provenance::Supplied),
            J::Null => return Err(format!("{what}[{i}]: moving slots need internal or supplied provenance")),
            _ if !word[i] => return Err(format!("{what}[{i}]: waits must be null")),
            _ => return Err(format!("{what}[{i}]: expected internal, supplied or null")),
        };
        out.push(value);
    }
    Ok(Some(out))
}

pub fn parse_contacts(j: Option<&J>, ports: &[Port], slots: usize) -> Result<Vec<Contact>, String> {
    let Some(j) = j else { return Ok(vec![]) };
    let a = j.arr().ok_or("contacts: expected array")?;
    let mut by_name = HashMap::new();
    for (i, p) in ports.iter().enumerate() {
        if p.name == "?" || by_name.insert(p.name.as_str(), i).is_some() {
            return Err("contacts require unique, named ports".into());
        }
    }
    let mut names = HashSet::new();
    let mut out = vec![];
    for (i, c) in a.iter().enumerate() {
        let where_ = format!("contacts[{i}]");
        let obj = match c { J::Obj(v) => v, _ => return Err(format!("{where_}: expected object")) };
        for (key, _) in obj {
            if !["name", "a", "b", "relation", "offset", "slots", "required"].contains(&key.as_str()) {
                return Err(format!("{where_}: unknown field {key}"));
            }
        }
        let get_str = |key: &str| c.get(key).and_then(J::str).ok_or(format!("{where_}.{key}: expected string"));
        let name = get_str("name")?.to_string();
        if name.is_empty() || !names.insert(name.clone()) { return Err(format!("{where_}.name must be unique and nonempty")); }
        let port_index = |key: &str| -> Result<usize, String> {
            let n = get_str(key)?;
            by_name.get(n).copied().ok_or(format!("{where_}.{key}: unknown port {n}"))
        };
        let (a, b) = (port_index("a")?, port_index("b")?);
        let relation = match get_str("relation")? {
            "same" => ContactRelation::Same,
            "adjacent" => ContactRelation::Adjacent,
            "offset" => ContactRelation::Offset,
            _ => return Err(format!("{where_}.relation unsupported")),
        };
        let offset = match (relation, c.get("offset")) {
            (ContactRelation::Offset, Some(v)) => Some(coord_arr(v, &format!("{where_}.offset"))?),
            (ContactRelation::Offset, None) => return Err(format!("{where_}.offset required for offset relation")),
            (_, Some(_)) => return Err(format!("{where_}.offset only valid for offset relation")),
            (_, None) => None,
        };
        let slot_values = c.get("slots").and_then(J::arr).filter(|v| !v.is_empty()).ok_or(format!("{where_}.slots: expected nonempty array"))?;
        let mut contact_slots = BTreeSet::new();
        for value in slot_values {
            let slot = value.int().filter(|n| *n >= 0 && (*n as usize) < slots).ok_or(format!("{where_}.slots: slot out of range"))? as usize;
            if !contact_slots.insert(slot) { return Err(format!("{where_}.slots: duplicate slot {slot}")); }
        }
        let required = match c.get("required") {
            None => true,
            Some(J::Bool(v)) => *v,
            _ => return Err(format!("{where_}.required: expected boolean")),
        };
        out.push(Contact { name, a, b, relation, offset, slots: contact_slots, required });
    }
    Ok(out)
}

pub fn parse_required_cells(j: Option<&J>) -> Result<Vec<(Coord, u16)>, String> {
    let Some(j) = j else { return Ok(vec![]) };
    let a = j.arr().ok_or("required_cells: expected array")?;
    let mut seen = BTreeSet::new();
    let mut out = vec![];
    for (i, item) in a.iter().enumerate() {
        let where_ = format!("required_cells[{i}]");
        let obj = match item { J::Obj(v) => v, _ => return Err(format!("{where_}: expected object")) };
        if obj.iter().any(|(k, _)| k != "at" && k != "cell") || item.get("at").is_none() || item.get("cell").is_none() {
            return Err(format!("{where_}: expected only at and cell"));
        }
        let at = coord_arr(item.get("at").unwrap(), &format!("{where_}.at"))?;
        let cell = item.get("cell").and_then(J::int).filter(|n| *n > 0 && *n <= u16::MAX as i64).ok_or(format!("{where_}.cell: expected positive encoded integer"))? as u16;
        if !seen.insert(at) { return Err(format!("{where_}: duplicate coordinate")); }
        out.push((at, cell));
    }
    Ok(out)
}
pub fn loads(j: Option<&J>, slots: usize, what: &str) -> Result<Option<Vec<Option<u64>>>, String> {
    let Some(j) = j else { return Ok(None) };
    let a = j.arr().filter(|a| a.len() == slots).ok_or(format!("{what}: expected {slots} entries"))?;
    a.iter()
        .map(|x| match x {
            J::Null => Ok(None),
            J::Num(n) if *n >= 0 => Ok(Some(*n as u64)),
            _ => Err(format!("{what}: expected nonnegative integer or null")),
        })
        .collect::<Result<Vec<_>, _>>()
        .map(Some)
}

pub fn port_position_at(p: &Port, tick: usize, period: usize) -> Coord {
    let prefix = p.word[..(tick % period) / 2].iter().filter(|&&m| m).count() as i64;
    let total = p.word.iter().filter(|&&m| m).count() as i64;
    Coord::new(p.at.x + (tick / period) as i64 * total + prefix, p.at.y, p.at.z)
}

pub fn load_ctx(path: &Path, recurrence_override: Option<&str>) -> Result<Ctx, String> {
    let text = fs::read_to_string(path).map_err(|e| format!("cannot read contract {}: {e}", path.display()))?;
    let raw = parse_json(&text)?;
    if raw.get("version").and_then(J::int) != Some(1) {
        return Err("contract.version: expected 1".into());
    }
    let name = raw.get("name").and_then(J::str).unwrap_or("contract").to_string();
    let dir = path.parent().unwrap_or(Path::new("."));
    let flyer_path = dir.join(raw.get("flyer").and_then(J::str).ok_or("contract.flyer missing")?);
    let period = raw.get("period_ticks").and_then(J::int).ok_or("period_ticks missing")? as usize;
    if period < 2 || period % 2 != 0 {
        return Err("period_ticks must be even".into());
    }
    let advance = raw.get("advance").and_then(J::int).ok_or("advance missing")?;
    let cycles = raw.get("cycles").and_then(J::int).unwrap_or(3) as usize;
    // A contract without prescribed_script is a plain natural contract (no supplied strokes).
    let script_path = raw.get("prescribed_script").and_then(J::str).map(|s| dir.join(s));
    let mut recurrence = raw.get("recurrence").and_then(J::str).unwrap_or("exact").to_string();
    if let Some(r) = recurrence_override {
        recurrence = r.to_string();
    }
    if recurrence != "exact" && recurrence != "bounded" && recurrence != "advance" {
        return Err("recurrence must be exact, bounded or advance".into());
    }
    let envelope = match raw.get("boundary_envelope") {
        Some(e) => Some((
            coord_arr(e.get("min").ok_or("envelope.min")?, "boundary_envelope.min")?,
            coord_arr(e.get("max").ok_or("envelope.max")?, "boundary_envelope.max")?,
        )),
        None => None,
    };
    let slots = period / 2;
    let mut ports = vec![];
    for (i, p) in raw.get("ports").and_then(J::arr).ok_or("ports missing")?.iter().enumerate() {
        let where_ = format!("ports[{i}]");
        let word_s = p.get("word").and_then(J::str).ok_or(format!("{where_}.word"))?;
        if word_s.len() != slots || word_s.chars().any(|c| c != 'm' && c != 'w') {
            return Err(format!("{where_}.word: expected {slots} characters from m/w"));
        }
        let word: Vec<bool> = word_s.chars().map(|c| c == 'm').collect();
        if word.iter().filter(|&&m| m).count() as i64 != advance {
            return Err(format!("{where_}: word move count != advance"));
        }
        let mut prefix = vec![0usize];
        for &m in &word {
            prefix.push(prefix.last().unwrap() + m as usize);
        }
        let input = match p.get("role").and_then(J::str) {
            Some("input") => true,
            Some("output") => false,
            _ => return Err(format!("{where_}.role: expected input/output")),
        };
        let baseline = loads(p.get("baseline_load"), slots, &format!("{where_}.baseline_load"))?;
        let spare = loads(p.get("spare_load"), slots, &format!("{where_}.spare_load"))?;
        let provenance = provenance(p.get("provenance"), slots, &word, &format!("{where_}.provenance"))?;
        if baseline.is_some() || spare.is_some() {
            for s in 0..slots {
                if word[s] && baseline.as_ref().map_or(true, |b| b[s].is_none()) {
                    return Err(format!("{where_}: baseline_load must be nonnull for moving slot {s}"));
                }
                if word[s] && spare.as_ref().map_or(false, |b| b[s].is_none()) {
                    return Err(format!("{where_}: spare_load must be nonnull for moving slot {s}"));
                }
            }
        }
        ports.push(Port {
            name: p.get("name").and_then(J::str).unwrap_or("?").to_string(),
            input,
            at: coord_arr(p.get("at").ok_or(format!("{where_}.at"))?, &format!("{where_}.at"))?,
            word,
            provenance,
            baseline,
            spare,
            prefix,
        });
    }
    let contacts = parse_contacts(raw.get("contacts"), &ports, slots)?;
    let required_cells = parse_required_cells(raw.get("required_cells"))?;
    // script
    let script = match &script_path {
        Some(sp) => fs::read_to_string(sp).map_err(|e| format!("cannot read script {}: {e}", sp.display()))?,
        None => String::new(),
    };
    let mut schedule: BTreeMap<usize, Vec<PrescribedMove>> = BTreeMap::new();
    let mut events = vec![];
    let mut event_keys = BTreeSet::new();
    for (ln, line) in script.lines().enumerate() {
        let line = line.split('#').next().unwrap_or("").trim();
        if line.is_empty() {
            continue;
        }
        let f: Vec<&str> = line.split_whitespace().collect();
        if f.len() != 5 {
            return Err(format!("script line {}: expected tick x y z limit", ln + 1));
        }
        let n = |i: usize| f[i].parse::<i64>().map_err(|_| format!("script line {}: bad integer", ln + 1));
        let tick = n(0)? as usize;
        let c = Coord::new(n(1)?, n(2)?, n(3)?);
        let limit = n(4)? as u64;
        if tick % 2 != 0 || tick + 1 >= period * cycles || tick % period + 2 > period {
            return Err(format!("script line {}: bad tick {tick}", ln + 1));
        }
        if !event_keys.insert((tick, c.x, c.y, c.z)) {
            return Err(format!("script line {}: duplicate prescribed input {:?} at tick {tick}", ln + 1, c));
        }
        schedule.entry(tick).or_default().push(PrescribedMove { input: c, max_load: limit });
        events.push((tick, c, limit));
    }
    if events.is_empty() && script_path.is_some() {
        return Err("empty prescribed script".into());
    }
    for &(tick, c, _) in &events {
        let slot = (tick % period) / 2;
        let m = ports.iter().filter(|p| p.input && p.word[slot] && port_position_at(p, tick, period) == c).count();
        if m != 1 {
            return Err(format!("script tick {tick}: target {:?} does not identify exactly one declared moving input", c));
        }
    }
    let flyer = Flyer::load(&flyer_path).map_err(|e| format!("failed to load {}: {e}", flyer_path.display()))?;
    let base_cells: Cells = flyer.blocks().into_iter().map(|(p, b)| (p, b.cell())).collect();
    let mut owners = BTreeMap::new();
    for (&p, &c) in &base_cells {
        if c & 15 == Kind::Piston as u16 {
            let m = flyer.piston_blocks(p);
            if !m.is_empty() {
                owners.insert(p, m.to_vec());
            }
        }
    }
    Ok(Ctx {
        name,
        period,
        advance,
        cycles,
        ports,
        contacts,
        required_cells,
        bounded: recurrence == "bounded",
        advance_mode: recurrence == "advance",
        target: u64::MAX,
        rank_end: true,
        file_limit: flyer.push_limit,
        envelope,
        schedule,
        events,
        orders: vec![],
        px: flyer.phase_x,
        pz: flyer.phase_z,
        rng: flyer.rng_state,
        push_limit: flyer.push_limit,
        owners,
        base_cells,
        soft: false,
        allow_ext_fail: false,
    })
}

// ---------------------------------------------------------------- evaluation
#[derive(Clone, Copy)]
pub struct Sample {
    pub rng: u64,
    pub px: u8,
    pub pz: u8,
}

pub fn build(ctx: &Ctx, cells: &Cells, s: Sample) -> Option<Flyer> {
    build_with(ctx, cells, s, ctx.push_limit)
}
pub fn build_with(ctx: &Ctx, cells: &Cells, s: Sample, limit: u64) -> Option<Flyer> {
    let mut f = Flyer::new(s.px, s.pz, s.rng, limit).ok()?;
    for (&p, &c) in cells {
        f.set(p, Block::from_cell(c).ok()?);
    }
    for (o, m) in &ctx.owners {
        if cells.contains_key(o) {
            f.set_piston_blocks(*o, m.clone()).ok()?;
        }
    }
    Some(f)
}

#[derive(Clone, Default)]
pub struct RunStats {
    pub max_load: u64,
    pub count_max: u64,
    pub presc_max: u64,
    pub sum: u64,
    pub excess: u64,
    pub input_loads: Vec<Vec<Option<u64>>>, // per port index (empty for outputs)
    pub hot: Vec<Coord>,                    // initial positions of identities in max-load actions
    // endogenous = natural piston actions only (not prescribed injections)
    pub end_max: u64,
    pub end_count: u64,
    pub end_sum: u64,
    pub end_excess: u64,
    pub end_hot: Vec<Coord>,
}

#[derive(Default, Clone)]
pub struct Progress {
    pub ticks_ok: usize,
    pub checks_ok: usize,
    pub soft_penalty: usize,
    pub soft_first: Option<String>,
    pub last_replay: Option<String>,
}

pub fn shift(c: Coord, dx: i64) -> Coord {
    Coord::new(c.x + dx, c.y, c.z)
}

pub fn run_order(ctx: &Ctx, cells: &Cells, order: PrescribedOrder, sample: Sample, want_hot: bool, prog: &mut Progress) -> Result<RunStats, String> {
    for (at, encoded) in &ctx.required_cells {
        if cells.get(at) != Some(encoded) {
            return Err(format!("required cell at ({},{},{}) expected encoded {}, actual {:?}", at.x, at.y, at.z, encoded, cells.get(at)));
        }
    }
    let flyer = build(ctx, cells, sample).ok_or("cannot build flyer")?;
    let origins: Vec<Coord> = cells.iter().filter(|(_, &c)| c & 15 != ARM).map(|(&p, _)| p).collect();
    let kinds: Vec<u16> = origins.iter().map(|p| cells[p] & 15).collect();
    let mut id_pos = origins.clone();
    let mut at: HashMap<Coord, usize> = origins.iter().enumerate().map(|(i, &p)| (p, i)).collect();
    let mut port_ids = vec![];
    for p in &ctx.ports {
        port_ids.push(*at.get(&p.at).ok_or(format!("port {}: no permanent block at {:?}", p.name, p.at))?);
    }
    // several ports may name the same permanent identity (e.g. a target that is both output and input)
    let mut port_of_id: HashMap<usize, Vec<usize>> = HashMap::new();
    for (pi, &id) in port_ids.iter().enumerate() {
        port_of_id.entry(id).or_default().push(pi);
    }
    if ctx.bounded {
        if let Some((lo, hi)) = ctx.envelope {
            if origins.iter().any(|p| p.x < lo.x || p.y < lo.y || p.z < lo.z || p.x > hi.x || p.y > hi.y || p.z > hi.z) {
                return Err("initial permanent identity outside boundary_envelope".into());
            }
        }
    }
    let mut init_owners: Vec<(Coord, Coord)> = vec![];
    for (o, ms) in &ctx.owners {
        if cells.contains_key(o) {
            for &m in ms {
                init_owners.push((*o, m));
            }
        }
    }
    init_owners.sort();
    let mut cur: HashMap<Coord, u16> = cells.iter().map(|(&p, &c)| (p, c)).collect();
    let mut owners_now = init_owners.clone();
    let mut session = PrescribedSession::new(flyer);
    let slots = ctx.period / 2;
    let mut st = RunStats::default();
    st.input_loads = ctx.ports.iter().map(|p| if p.input { vec![None; slots] } else { vec![] }).collect();
    let total = ctx.period * ctx.cycles;
    for tick in 0..total {
        let slot = (tick % ctx.period) / 2;
        if tick % 2 == 0 {
            for contact in &ctx.contacts {
                if !contact.slots.contains(&slot) { continue; }
                let a = id_pos[port_ids[contact.a]];
                let b = id_pos[port_ids[contact.b]];
                let d = Coord::new(b.x - a.x, b.y - a.y, b.z - a.z);
                let holds = match contact.relation {
                    ContactRelation::Same => d == Coord::new(0, 0, 0),
                    ContactRelation::Adjacent => d.x.abs() + d.y.abs() + d.z.abs() == 1,
                    ContactRelation::Offset => d == contact.offset.unwrap(),
                };
                if holds != contact.required {
                    return Err(format!("tick {tick}: contact {} expected {}, actual offset ({},{},{})", contact.name,
                        if contact.required { "required relation" } else { "forbidden relation" }, d.x, d.y, d.z));
                }
            }
        }
        let moves: &[PrescribedMove] = ctx.schedule.get(&tick).map(|v| v.as_slice()).unwrap_or(&[]);
        let mut trace: TickTrace = session.new_trace();
        let report = session.tick_traced(moves, order, &mut trace, tick).map_err(|e| format!("tick {tick}: simulation error: {e}"))?;
        if order == PrescribedOrder::Interleaved {
            let realized_order = trace.steps.iter().map(|step| {
                format!("{}:{}:chunk={:?}:piston={:?}:input={:?}", step.info.stage,
                    step.info.action.unwrap_or(""), step.info.active_chunk,
                    step.info.active_piston, step.info.active_input)
            }).collect::<Vec<_>>().join(",");
            prog.last_replay = Some(format!("tick={tick}, schedule_seed={:?}, action_order=[{}]",
                report.schedule_seed, realized_order));
        }
        for a in &report.actions {
            if let PrescribedOutcome::Failed(r) = &a.outcome {
                return Err(format!("tick {tick}: prescribed move at ({},{},{}) failed: {:?}", a.input.x, a.input.y, a.input.z, r));
            }
        }
        if report.natural.extension_failures > 0 && !ctx.allow_ext_fail {
            return Err(format!("tick {tick}: extension failure"));
        }
        if trace.steps.is_empty() {
            return Err(format!("tick {tick}: no steps"));
        }
        let mut moved = vec![false; ctx.ports.len()];
        let mut observed_provenance: Vec<Option<Provenance>> = vec![None; ctx.ports.len()];
        let mut moving_dest: HashSet<Coord> = HashSet::new();
        for step in &trace.steps {
            let action = step.info.action;
            if let Some(mv) = &step.info.movement {
                if action != Some("settle prescribed move") {
                    if let Some((pos, reason)) = mv.failure {
                        return Err(format!("tick {tick}: movement failed ({}) at ({},{},{}) action {:?}", reason, pos.x, pos.y, pos.z, action));
                    }
                    if mv.sources.len() != mv.destinations.len() {
                        return Err(format!("tick {tick}: unequal source/destination counts"));
                    }
                    let mapping: HashMap<Coord, Coord> = mv.sources.iter().copied().zip(mv.destinations.iter().copied()).collect();
                    if mapping.len() != mv.sources.len() {
                        return Err(format!("tick {tick}: repeated movement source"));
                    }
                    if matches!(action, Some("extend") | Some("retract") | Some("prescribed move")) {
                        let load = mv.sources.len() as u64;
                        if load > st.max_load {
                            st.max_load = load;
                            st.count_max = 0;
                            st.hot.clear();
                        }
                        if load == st.max_load {
                            st.count_max += 1;
                            if want_hot {
                                for s in &mv.sources {
                                    if let Some(&id) = at.get(s) {
                                        st.hot.push(origins[id]);
                                    }
                                }
                            }
                        }
                        st.sum += load;
                        st.excess += load.saturating_sub(ctx.target);
                        if action != Some("prescribed move") {
                            if load > st.end_max {
                                st.end_max = load;
                                st.end_count = 0;
                                st.end_hot.clear();
                            }
                            if load == st.end_max {
                                st.end_count += 1;
                                if want_hot {
                                    for s in &mv.sources {
                                        if let Some(&id) = at.get(s) {
                                            st.end_hot.push(origins[id]);
                                        }
                                    }
                                }
                            }
                            st.end_sum += load;
                            st.end_excess += load.saturating_sub(ctx.target);
                        }
                        let mut this: Vec<(usize, Coord, Coord)> = vec![];
                        for s in &mv.sources {
                            if let Some(&id) = at.get(s) {
                                this.push((id, *s, mapping[s]));
                            }
                        }
                        for &(id, _, _) in &this {
                            if let Some(pis) = port_of_id.get(&id) {
                                if moved[pis[0]] {
                                    return Err(format!("tick {tick}: tagged identity of port {} moved more than once", ctx.ports[pis[0]].name));
                                }
                            }
                        }
                        for &(_, old, _) in &this {
                            at.remove(&old);
                        }
                        for &(id, _, new) in &this {
                            if at.insert(new, id).is_some() {
                                return Err(format!("tick {tick}: two permanent identities occupy ({},{},{})", new.x, new.y, new.z));
                            }
                            id_pos[id] = new;
                        }
                        for &(id, _, _) in &this {
                            let Some(pis) = port_of_id.get(&id) else { continue };
                            for &pi in pis {
                            moved[pi] = true;
                            observed_provenance[pi] = Some(if action == Some("prescribed move") { Provenance::Supplied } else { Provenance::Internal });
                            let port = &ctx.ports[pi];
                            if port.input {
                                let o = &mut st.input_loads[pi][slot];
                                *o = Some(o.map_or(load, |x| x.max(load)));
                                if let Some(b) = port.baseline.as_ref().and_then(|b| b[slot]) {
                                    let allowed = b + port.spare.as_ref().and_then(|s| s[slot]).unwrap_or(0);
                                    if load > allowed {
                                        return Err(format!("tick {tick}: input {} load budget exceeded; moved {load}, baseline {b} + spare {} = {allowed}", port.name, allowed - b));
                                    }
                                }
                            }
                            }
                        }
                        if action == Some("prescribed move") {
                            let inp = step.info.active_input;
                            let Some(&(_, _, limit)) = ctx.events.iter().find(|e| e.0 == tick && Some(e.1) == inp) else {
                                return Err(format!("tick {tick}: undeclared prescribed move"));
                            };
                            let inp = inp.unwrap();
                            if !mapping.contains_key(&inp) || load > limit {
                                return Err(format!("tick {tick}: prescribed movement omitted input or exceeded max_load {limit}"));
                            }
                            if mapping.iter().any(|(s, d)| *d != shift(*s, 1)) {
                                return Err(format!("tick {tick}: prescribed movement is not a +X translation"));
                            }
                            let closure: Vec<Coord> = mv.sources.iter().chain(mv.destinations.iter()).copied().collect();
                            if closure.iter().any(|c| moving_dest.contains(c)) {
                                return Err(format!("tick {tick}: prescribed closures overlap prior moving destinations"));
                            }
                            moving_dest.extend(mv.destinations.iter().copied());
                            st.presc_max = st.presc_max.max(load);
                        }
                    }
                }
            }
            for ch in &step.changes {
                match ch.cell {
                    Some(c) => {
                        cur.insert(ch.pos, c);
                    }
                    None => {
                        cur.remove(&ch.pos);
                    }
                }
            }
            owners_now.clear();
            owners_now.extend(step.owners.iter().copied());
            for (id, pos) in id_pos.iter().enumerate() {
                match cur.get(pos) {
                    None => return Err(format!("tick {tick}: permanent identity {id} deleted at ({},{},{})", pos.x, pos.y, pos.z)),
                    Some(c) if c & 15 != kinds[id] => return Err(format!("tick {tick}: permanent identity {id} replaced at ({},{},{})", pos.x, pos.y, pos.z)),
                    _ => {}
                }
            }
            for ch in &step.changes {
                if let Some(c) = ch.cell {
                    if c & 15 != ARM && !at.contains_key(&ch.pos) {
                        return Err(format!("tick {tick}: new or replacement permanent block at ({},{},{})", ch.pos.x, ch.pos.y, ch.pos.z));
                    }
                }
            }
        }
        // port words (graded: count satisfied ports before reporting the first mismatch)
        let mut port_err: Option<String> = None;
        for (pi, port) in ctx.ports.iter().enumerate() {
            let should = tick % 2 == 0 && port.word[slot];
            let mut ok = true;
            if moved[pi] != should {
                ok = false;
                port_err.get_or_insert_with(|| format!("tick {tick}: port {} expected {}, actual {}", port.name, if should { "move +X" } else { "wait" }, if moved[pi] { "moved" } else { "did not move" }));
            }
            if tick % 2 == 0 {
                if let Some(expected) = port.provenance.as_ref().and_then(|p| p[slot]) {
                    if observed_provenance[pi] != Some(expected) {
                        ok = false;
                        let label = |v| match v { Provenance::Internal => "internal", Provenance::Supplied => "supplied" };
                        port_err.get_or_insert_with(|| format!("tick {tick}: port {} expected provenance {}, observed {}", port.name, label(expected), observed_provenance[pi].map(label).unwrap_or("none")));
                    }
                }
            }
            let id = port_ids[pi];
            let o = origins[id];
            let (cyc, rem) = (tick / ctx.period, tick % ctx.period);
            let n = cyc * port.prefix[slots] + port.prefix[rem / 2 + 1];
            let expect = Coord::new(o.x + n as i64, o.y, o.z);
            if id_pos[id] != expect {
                ok = false;
                port_err.get_or_insert_with(|| format!("tick {tick}: port {} expected position ({},{},{}), actual ({},{},{})", port.name, expect.x, expect.y, expect.z, id_pos[id].x, id_pos[id].y, id_pos[id].z));
            }
            let moving = cur.get(&id_pos[id]).map_or(false, |c| c & 16 != 0);
            if moving != should {
                ok = false;
                port_err.get_or_insert_with(|| format!("tick {tick}: port {} expected moving={should}, actual moving={moving}", port.name));
            }
            if ctx.soft {
                let word_ok = moved[pi] == should;
                prog.checks_ok += word_ok as usize;
            } else {
                prog.checks_ok += ok as usize;
            }
        }
        if let Some(e) = port_err {
            if !ctx.soft {
                return Err(e);
            }
            prog.soft_first.get_or_insert(e);
        }
        // boundary
        if (tick + 1) % ctx.period == 0 {
            if session.has_pending_moves() {
                return Err(format!("tick {tick}: prescribed move remains pending at period boundary"));
            }
            let k = ((tick + 1) / ctx.period) as i64;
            let dx = ctx.advance * k;
            if ctx.advance_mode {
                for (id, p) in id_pos.iter().enumerate() {
                    if *p != shift(origins[id], dx) {
                        let e = format!("tick {tick}: permanent identity {id} at ({},{},{}) is not its origin advanced by {dx} at cycle {k} boundary", p.x, p.y, p.z);
                        if !ctx.soft {
                            return Err(e);
                        }
                        prog.soft_penalty += 1;
                        prog.soft_first.get_or_insert(e);
                    }
                }
            } else if !ctx.bounded {
                let miss = if cur.len() != cells.len() { cells.len().max(1) } else { cells.iter().filter(|(p, c)| cur.get(&shift(**p, dx)) != Some(c)).count() };
                if miss > 0 {
                    let e = format!("tick {tick}: recurrence mismatch at cycle {k} boundary");
                    if !ctx.soft {
                        return Err(e);
                    }
                    prog.soft_penalty += miss;
                    prog.soft_first.get_or_insert(e);
                }
                let exp: Vec<(Coord, Coord)> = init_owners.iter().map(|&(o, m)| (shift(o, dx), shift(m, dx))).collect();
                if owners_now != exp {
                    let e = format!("tick {tick}: piston owner recurrence mismatch at cycle {k} boundary");
                    if !ctx.soft {
                        return Err(e);
                    }
                    prog.soft_penalty += 1;
                    prog.soft_first.get_or_insert(e);
                }
            } else if let Some((lo, hi)) = ctx.envelope {
                let (lo, hi) = (shift(lo, dx), shift(hi, dx));
                for (id, p) in id_pos.iter().enumerate() {
                    if p.x < lo.x || p.y < lo.y || p.z < lo.z || p.x > hi.x || p.y > hi.y || p.z > hi.z {
                        let e = format!("tick {tick}: permanent identity {id} at ({},{},{}) outside translated envelope", p.x, p.y, p.z);
                        if !ctx.soft {
                            return Err(e);
                        }
                        prog.soft_penalty += 1;
                        prog.soft_first.get_or_insert(e);
                    }
                }
            }
        }
        prog.ticks_ok = tick + 1;
    }
    if let Some(e) = prog.soft_first.clone() {
        return Err(e);
    }
    Ok(st)
}

#[derive(Clone)]
pub struct Eval {
    pub excess: u64,
    pub max_load: u64,
    pub all_max: u64,
    pub count_max: u64,
    pub presc_max: u64,
    pub sum: u64,
    pub blocks: usize,
    pub input_loads: Vec<Vec<Option<u64>>>,
    pub hot: Vec<Coord>,
}
impl Eval {
    pub fn score(&self) -> (u64, u64, u64, usize, u64) {
        (self.excess, self.max_load, self.count_max, self.blocks, self.sum)
    }
}

pub fn permanent_blocks(cells: &Cells) -> usize {
    cells.values().filter(|&&c| c & 15 != ARM).count()
}

pub struct EvalFail {
    pub msg: String,
    pub ticks: usize,
    pub checks: usize,
    pub penalty: usize,
}
impl std::fmt::Display for EvalFail {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.msg)
    }
}
pub fn totals(ctx: &Ctx) -> (usize, usize) {
    let t = ctx.orders.len() * ctx.period * ctx.cycles;
    (t, t * ctx.ports.len())
}

pub fn evaluate(ctx: &Ctx, cells: &Cells, sample: Sample, want_hot: bool) -> Result<Eval, EvalFail> {
    let mut runs = vec![];
    let (mut ticks, mut checks) = (0usize, 0usize);
    for &o in &ctx.orders {
        let mut prog = Progress::default();
        match run_order(ctx, cells, o, sample, want_hot, &mut prog) {
            Ok(r) => {
                ticks += prog.ticks_ok;
                checks += prog.checks_ok;
                runs.push(r);
            }
            Err(e) => {
                let replay = if o == PrescribedOrder::Interleaved {
                    prog.last_replay.as_ref().map(|value| format!(" replay({value})")).unwrap_or_default()
                } else { String::new() };
                return Err(EvalFail { msg: format!("sample(rng={}, phase_x={}, phase_z={}) [{}] {e}{replay}",
                    sample.rng, sample.px, sample.pz, order_name(o)),
                    ticks: ticks + prog.ticks_ok, checks: checks + prog.checks_ok, penalty: prog.soft_penalty });
            }
        }
    }
    let all_max = runs.iter().map(|r| r.max_load).max().unwrap_or(0);
    if ctx.rank_end {
        for r in runs.iter_mut() {
            r.max_load = r.end_max;
            r.count_max = r.end_count;
            r.sum = r.end_sum;
            r.excess = r.end_excess;
            r.hot = std::mem::take(&mut r.end_hot);
        }
    }
    let max_load = runs.iter().map(|r| r.max_load).max().unwrap_or(0);
    let mut ev = Eval {
        all_max,
        excess: runs.iter().map(|r| r.excess).sum(),
        max_load,
        count_max: 0,
        presc_max: 0,
        sum: 0,
        blocks: permanent_blocks(cells),
        input_loads: ctx.ports.iter().map(|p| if p.input { vec![None; ctx.period / 2] } else { vec![] }).collect(),
        hot: vec![],
    };
    for r in &runs {
        if r.max_load == max_load {
            ev.count_max += r.count_max;
            ev.hot.extend(r.hot.iter().copied());
        }
        ev.presc_max = ev.presc_max.max(r.presc_max);
        ev.sum += r.sum;
        for (pi, v) in r.input_loads.iter().enumerate() {
            for (s, x) in v.iter().enumerate() {
                if let Some(x) = x {
                    let o = &mut ev.input_loads[pi][s];
                    *o = Some(o.map_or(*x, |y| y.max(*x)));
                }
            }
        }
    }
    ev.hot.sort();
    ev.hot.dedup();
    Ok(ev)
}

// ---------------------------------------------------------------- mutation
pub struct MutCtx {
    pub immutable: BTreeSet<Coord>,
    pub lo: Coord,
    pub hi: Coord,
    pub pistons: bool,
    pub owner_members: BTreeSet<Coord>,
}
pub fn glue_kind(cell: u16) -> Option<Kind> {
    Block::from_cell(cell).ok().map(|b| b.kind()).filter(|k| matches!(k, Kind::Slime | Kind::Honey))
}
pub fn kind_of(cell: u16) -> Option<Kind> {
    Block::from_cell(cell).ok().map(|b| b.kind())
}
pub fn in_box(m: &MutCtx, q: Coord) -> bool {
    q.x >= m.lo.x && q.y >= m.lo.y && q.z >= m.lo.z && q.x <= m.hi.x && q.y <= m.hi.y && q.z <= m.hi.z
}
pub fn nbr(p: Coord, d: (i64, i64, i64)) -> Coord {
    Coord::new(p.x + d.0, p.y + d.1, p.z + d.2)
}
pub fn piston_dir(cell: u16) -> usize {
    ((cell >> 5) & 7) as usize
}
pub fn piston_state(cell: u16) -> u16 {
    (cell >> 10) & 3
}
// The arm cell of an extended piston (state 2), if consistent.
pub fn arm_of(c: &Cells, p: Coord, cell: u16) -> Option<Coord> {
    if piston_state(cell) != 2 || piston_dir(cell) > 5 {
        return None;
    }
    let a = nbr(p, DIRS[piston_dir(cell)]);
    c.get(&a).filter(|&&x| x & 15 == ARM).map(|_| a)
}
pub fn free(m: &MutCtx, c: &Cells, q: Coord) -> bool {
    !c.contains_key(&q) && in_box(m, q)
}
pub fn untouchable(m: &MutCtx, p: Coord) -> bool {
    m.immutable.contains(&p) || m.owner_members.contains(&p)
}
pub fn mutable(m: &MutCtx, c: &Cells, p: Coord, cell: u16) -> bool {
    if untouchable(m, p) {
        return false;
    }
    match kind_of(cell) {
        Some(Kind::Slime | Kind::Honey | Kind::RedstoneBlock | Kind::Rod | Kind::Observer) => true,
        Some(Kind::Piston) => {
            if !m.pistons || cell & 16 != 0 {
                return false;
            }
            match piston_state(cell) {
                0 => true,
                2 => arm_of(c, p, cell).map_or(false, |a| !untouchable(m, a)),
                _ => false,
            }
        }
        _ => false,
    }
}
// Flyer::save translates the machine so its minimum Y is 0 and its minimum X/Z chunk is 0, which would
// invalidate the absolute coordinates of the contract. Reject candidates whose canonical shift differs from the seed.
pub fn canon_key(c: &Cells) -> (i64, i64, i64) {
    let (mut x, mut y, mut z) = (i64::MAX, i64::MAX, i64::MAX);
    for k in c.keys() {
        x = x.min(k.x);
        y = y.min(k.y);
        z = z.min(k.z);
    }
    (x.div_euclid(16), y, z.div_euclid(16))
}
pub fn rand_in_box(m: &MutCtx, r: &mut Rng) -> Coord {
    Coord::new(
        m.lo.x + r.range((m.hi.x - m.lo.x + 1) as usize) as i64,
        m.lo.y + r.range((m.hi.y - m.lo.y + 1) as usize) as i64,
        m.lo.z + r.range((m.hi.z - m.lo.z + 1) as usize) as i64,
    )
}
// One structural edit. Piston edits keep the arm of an extended piston consistent; new pistons are retracted and unpowered.
pub fn mutate_once(c: &mut Cells, r: &mut Rng, hot: &[Coord], m: &MutCtx) {
    let keys: Vec<Coord> = c.keys().copied().collect();
    if keys.is_empty() {
        return;
    }
    let op = r.range(100);
    let p = if !hot.is_empty() && r.chance(0.7) { hot[r.range(hot.len())] } else { keys[r.range(keys.len())] };
    let Some(&cell) = c.get(&p) else { return };
    let d = DIRS[r.range(6)];
    let q = nbr(p, d);
    let free_q = free(m, c, q);
    let mut_p = mutable(m, c, p, cell);
    let kind = kind_of(cell);
    let is_glue = glue_kind(cell).is_some();
    let is_piston = kind == Some(Kind::Piston);
    match op {
        0..=13 => {
            if mut_p && is_glue {
                c.remove(&p);
            }
        }
        14..=29 => {
            if mut_p && is_glue && free_q {
                c.remove(&p);
                c.insert(q, cell);
            }
        }
        30..=41 => {
            if free_q {
                let k = glue_kind(cell).unwrap_or(if r.range(2) == 0 { Kind::Slime } else { Kind::Honey });
                c.insert(q, Block::plain(k, false).unwrap().cell());
            }
        }
        42..=47 => {
            if mut_p {
                if let Some(k) = glue_kind(cell) {
                    let nk = if k == Kind::Slime { Kind::Honey } else { Kind::Slime };
                    c.insert(p, Block::plain(nk, false).unwrap().cell());
                }
            }
        }
        48..=54 => {
            if mut_p && matches!(kind, Some(Kind::RedstoneBlock | Kind::Rod | Kind::Observer)) && free_q {
                c.remove(&p);
                c.insert(q, cell);
            }
        }
        55..=58 => {
            if mut_p {
                if let Ok(b) = Block::from_cell(cell) {
                    let nd = r.range(6) as u8;
                    let nb = match b.kind() {
                        Kind::Rod => Block::rod(nd, false).ok(),
                        Kind::Observer => Block::observer(nd, b.powered(), false).ok(),
                        _ => None,
                    };
                    if let Some(nb) = nb {
                        c.insert(p, nb.cell());
                    }
                }
            }
        }
        59..=65 => {
            if mut_p && is_glue {
                let q2 = nbr(q, DIRS[r.range(6)]);
                if free(m, c, q2) && q2 != p {
                    c.remove(&p);
                    c.insert(q2, cell);
                }
            }
        }
        66..=69 => {
            if mut_p && is_glue {
                let t = rand_in_box(m, r);
                if !c.contains_key(&t) {
                    c.remove(&p);
                    c.insert(t, cell);
                }
            }
        }
        70..=77 => {
            // move a piston (with its arm when extended)
            if mut_p && is_piston {
                let arm = arm_of(c, p, cell);
                c.remove(&p);
                if let Some(a) = arm {
                    c.remove(&a);
                }
                let qa = arm.map(|a| nbr(a, d));
                let ok = free(m, c, q) && qa.map_or(true, |qa| free(m, c, qa) && qa != q);
                if ok {
                    c.insert(q, cell);
                    if let Some(qa) = qa {
                        c.insert(qa, ARM);
                    }
                } else {
                    c.insert(p, cell);
                    if let Some(a) = arm {
                        c.insert(a, ARM);
                    }
                }
            }
        }
        78..=81 => {
            // change piston facing
            if mut_p && is_piston {
                let nd = r.range(6);
                if nd != piston_dir(cell) {
                    let new_cell = (cell & !(7 << 5)) | ((nd as u16) << 5);
                    match arm_of(c, p, cell) {
                        None if piston_state(cell) == 0 => {
                            c.insert(p, new_cell);
                        }
                        Some(a) => {
                            let na = nbr(p, DIRS[nd]);
                            c.remove(&a);
                            if free(m, c, na) {
                                c.insert(na, ARM);
                                c.insert(p, new_cell);
                            } else {
                                c.insert(a, ARM);
                            }
                        }
                        _ => {}
                    }
                }
            }
        }
        82..=85 => {
            if mut_p && is_piston {
                c.insert(p, cell ^ 0x100);
            }
        }
        86..=90 => {
            // add a retracted, unpowered piston next to p
            if m.pistons && free_q {
                let b = Block::piston(r.range(6) as u8, r.range(2) == 0, false, 0, false).unwrap();
                c.insert(q, b.cell());
            }
        }
        91..=94 => {
            if mut_p && is_piston {
                if let Some(a) = arm_of(c, p, cell) {
                    c.remove(&a);
                }
                c.remove(&p);
            }
        }
        95..=97 => {
            if free_q {
                c.insert(q, Block::plain(Kind::RedstoneBlock, false).unwrap().cell());
            }
        }
        _ => {
            if mut_p && matches!(kind, Some(Kind::RedstoneBlock | Kind::Rod | Kind::Observer)) {
                c.remove(&p);
            }
        }
    }
}
pub fn mutate(c: &mut Cells, r: &mut Rng, hot: &[Coord], m: &MutCtx) {
    let n = match r.range(10) {
        0..=3 => 1,
        4..=6 => 2,
        7..=8 => 3,
        _ => 4,
    };
    for _ in 0..n {
        mutate_once(c, r, hot, m);
    }
}

// ---------------------------------------------------------------- pareto
pub struct Member {
    pub key: (u64, u64, usize), // (max load, max prescribed-input load, blocks)
    pub cells: Cells,
    pub ev: Eval,
}
#[derive(Default)]
pub struct Pareto {
    pub members: Vec<Member>,
    pub best: Option<((u64, u64, u64, usize, u64), Cells, Eval)>,
}
impl Pareto {
    // returns true if inserted
    pub fn offer(&mut self, cells: &Cells, ev: &Eval) -> bool {
        if self.best.as_ref().map_or(true, |b| ev.score() < b.0) {
            self.best = Some((ev.score(), cells.clone(), ev.clone()));
        }
        let key = (ev.max_load, ev.presc_max, ev.blocks);
        let le = |a: &(u64, u64, usize), b: &(u64, u64, usize)| a.0 <= b.0 && a.1 <= b.1 && a.2 <= b.2;
        for m in &self.members {
            if le(&m.key, &key) {
                // existing dominates or equals; keep the one with better tie-break score
                if m.key == key && (ev.count_max, ev.sum) < (m.ev.count_max, m.ev.sum) {
                    break;
                }
                return false;
            }
        }
        self.members.retain(|m| !le(&key, &m.key));
        self.members.push(Member { key, cells: cells.clone(), ev: ev.clone() });
        self.members.sort_by_key(|m| m.key);
        true
    }
}

// Encoded limit of saved flyers: the file's original limit, raised only if the measured max load needs it.
pub fn save_limit(ctx: &Ctx, max_load: u64) -> u64 {
    ctx.file_limit.max(max_load)
}
pub fn save_flyer(ctx: &Ctx, cells: &Cells, path: &Path, limit: u64) -> Result<(), String> {
    let f = build_with(ctx, cells, Sample { rng: ctx.rng, px: ctx.px, pz: ctx.pz }, limit).ok_or("cannot build flyer for save")?;
    f.save(path).map_err(|e| format!("save {}: {e}", path.display()))
}

pub fn input_loads_json(ctx: &Ctx, il: &[Vec<Option<u64>>]) -> String {
    let parts: Vec<String> = ctx
        .ports
        .iter()
        .enumerate()
        .filter(|(_, p)| p.input)
        .map(|(i, p)| {
            let v: Vec<String> = il[i].iter().map(|x| x.map_or("null".to_string(), |x| x.to_string())).collect();
            format!("{}:[{}]", jstr(&p.name), v.join(","))
        })
        .collect();
    format!("{{{}}}", parts.join(","))
}

pub fn samples_list() -> Vec<Sample> {
    let mut v = vec![];
    for rng in [0u64, 1, 2, 5, 42] {
        for px in [0u8, 7, 8, 15] {
            for pz in [0u8, 7, 8, 15] {
                v.push(Sample { rng, px, pz });
            }
        }
    }
    v
}

pub fn cell_desc(c: u16) -> String {
    match Block::from_cell(c) {
        Ok(b) => match b.kind() {
            Kind::Piston => format!("Piston(dir{}{} state{})", b.direction(), if b.sticky() { " sticky" } else { "" }, b.state()),
            Kind::Rod | Kind::Observer => format!("{:?}(dir{})", b.kind(), b.direction()),
            k => format!("{k:?}"),
        },
        Err(_) => format!("cell{c}"),
    }
}
pub fn diff_cells(seed: &Cells, cand: &Cells) -> Vec<String> {
    let mut keys: BTreeSet<Coord> = seed.keys().copied().collect();
    keys.extend(cand.keys().copied());
    let mut out = vec![];
    for k in keys {
        match (seed.get(&k), cand.get(&k)) {
            (Some(a), Some(b)) if a == b => {}
            (Some(a), Some(b)) => out.push(format!("~ ({},{},{}) {} -> {}", k.x, k.y, k.z, cell_desc(*a), cell_desc(*b))),
            (Some(a), None) => out.push(format!("- ({},{},{}) {}", k.x, k.y, k.z, cell_desc(*a))),
            (None, Some(b)) => out.push(format!("+ ({},{},{}) {}", k.x, k.y, k.z, cell_desc(*b))),
            _ => {}
        }
    }
    out
}

pub fn write_outputs(ctx: &Ctx, out_dir: &Path, par: &Pareto, extra: &str) -> Result<(), String> {
    if let Ok(rd) = fs::read_dir(out_dir) {
        for e in rd.flatten() {
            let n = e.file_name().to_string_lossy().to_string();
            if n.starts_with("pareto_") && n.ends_with(".flyer") {
                let _ = fs::remove_file(e.path());
            }
        }
    }
    let mut entries = vec![];
    for m in &par.members {
        let name = format!("pareto_{}_{}_{}.flyer", m.key.0, m.key.1, m.key.2);
        save_flyer(ctx, &m.cells, &out_dir.join(&name), save_limit(ctx, m.ev.all_max))?;
        entries.push(format!(
            "{{\"file\":{},\"max_load\":{},\"all_max_load\":{},\"count_at_max\":{},\"max_prescribed_input_load\":{},\"blocks\":{},\"sum_load\":{},\"input_loads\":{}}}",
            jstr(&name), m.ev.max_load, m.ev.all_max, m.ev.count_max, m.ev.presc_max, m.ev.blocks, m.ev.sum, input_loads_json(ctx, &m.ev.input_loads)
        ));
    }
    let mut best_json = String::from("null");
    if let Some((sc, cells, ev)) = &par.best {
        save_flyer(ctx, cells, &out_dir.join("best.flyer"), save_limit(ctx, ev.all_max))?;
        best_json = format!(
            "{{\"file\":\"best.flyer\",\"score\":[{},{},{},{},{}],\"excess\":{},\"max_load\":{},\"all_max_load\":{},\"count_at_max\":{},\"max_prescribed_input_load\":{},\"blocks\":{},\"input_loads\":{},\"diff_vs_seed\":[{}]}}",
            sc.0, sc.1, sc.2, sc.3, sc.4, ev.excess, ev.max_load, ev.all_max, ev.count_max, ev.presc_max, ev.blocks, input_loads_json(ctx, &ev.input_loads),
            diff_cells(&ctx.base_cells, cells).iter().map(|d| jstr(d)).collect::<Vec<_>>().join(",")
        );
    }
    let text = format!("{{{},\"best\":{},\"pareto\":[{}]}}\n", extra, best_json, entries.join(",\n"));
    fs::write(out_dir.join("summary.json"), text).map_err(|e| e.to_string())
}

// ---------------------------------------------------------------- main
pub fn rec_name(ctx: &Ctx) -> &'static str {
    if ctx.advance_mode {
        "advance"
    } else if ctx.bounded {
        "bounded"
    } else {
        "exact"
    }
}

/// The same contract with an n-fold period (words repeated, advance x n). Hopping hardware that alternates
/// between two pistons per glue period recurs only every 2 periods; in the doubled contract each move instance
/// has one actor again. Supplied strokes are re-derived for the new cycle count.
pub fn multiplied(ctx: &Ctx, n: usize) -> Result<Ctx, String> {
    let mut c = ctx.clone();
    let slots = ctx.period / 2;
    let rep = |v: &Vec<Option<u64>>| -> Vec<Option<u64>> { (0..n).flat_map(|_| v.iter().copied()).collect() };
    for p in c.ports.iter_mut() {
        p.word = (0..n).flat_map(|_| p.word.iter().copied()).collect();
        p.prefix = vec![0];
        for &m in &p.word {
            p.prefix.push(p.prefix.last().unwrap() + m as usize);
        }
        p.baseline = p.baseline.as_ref().map(rep);
        p.spare = p.spare.as_ref().map(rep);
        p.provenance = p.provenance.as_ref().map(|v| (0..n).flat_map(|_| v.iter().copied()).collect());
    }
    for k in c.contacts.iter_mut() {
        k.slots = (0..n).flat_map(|j| k.slots.iter().map(move |s| s + j * slots)).collect();
    }
    c.period = ctx.period * n;
    c.advance = ctx.advance * n as i64;
    let cyc = ((ctx.cycles + n - 1) / n).max(2);
    if c.events.is_empty() {
        c.cycles = cyc;
    } else {
        set_cycles(&mut c, cyc)?;
    }
    Ok(c)
}

// Re-derive the prescribed schedule for N periods by replicating the first period, shifted by the advance per cycle.
pub fn set_cycles(ctx: &mut Ctx, n: usize) -> Result<(), String> {
    let first: Vec<(usize, Coord, u64)> = ctx.events.iter().copied().filter(|e| e.0 < ctx.period).collect();
    if first.is_empty() {
        return Err("no prescribed events in the first period".into());
    }
    ctx.cycles = n;
    ctx.events.clear();
    ctx.schedule.clear();
    for j in 0..n {
        for &(t, c, l) in &first {
            let tick = t + j * ctx.period;
            let c = shift(c, ctx.advance * j as i64);
            if tick + 1 >= ctx.period * n {
                return Err("prescribed event cannot settle within the cycles".into());
            }
            ctx.events.push((tick, c, l));
            ctx.schedule.entry(tick).or_default().push(PrescribedMove { input: c, max_load: l });
        }
    }
    Ok(())
}

