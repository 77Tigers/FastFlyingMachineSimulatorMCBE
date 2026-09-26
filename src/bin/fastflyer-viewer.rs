//! Local, read-only-in-browser viewer for simulated flyer ticks.

use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

use fastflyer::debug::TickTrace;
use fastflyer::{Block, Coord, Flyer, Kind};

const HTML: &str = include_str!("../../viewer/index.html");
const CSS: &str = include_str!("../../viewer/style.css");
const V2_CSS: &str = include_str!("../../viewer/v2.css");
const JS: &str = include_str!("../../viewer/app.js");
const THREE: &str = include_str!("../../viewer/node_modules/three/build/three.module.js");
const THREE_CORE: &str = include_str!("../../viewer/node_modules/three/build/three.core.js");
const ORBIT: &str =
    include_str!("../../viewer/node_modules/three/examples/jsm/controls/OrbitControls.js");

fn demo() -> Flyer {
    let mut flyer = Flyer::new(0, 0, 2, 12).unwrap();
    flyer.set(
        Coord::new(0, 0, 0),
        Block::piston(0, false, false, 0, false).unwrap(),
    );
    flyer.set(
        Coord::new(1, 0, 1),
        Block::piston(1, true, false, 0, false).unwrap(),
    );
    flyer.set(
        Coord::new(0, 0, 1),
        Block::plain(Kind::Slime, false).unwrap(),
    );
    flyer.set(
        Coord::new(1, 0, 0),
        Block::plain(Kind::Slime, false).unwrap(),
    );
    flyer.set(
        Coord::new(0, 1, 1),
        Block::observer(3, true, false).unwrap(),
    );
    flyer.set(
        Coord::new(1, 1, 0),
        Block::observer(3, false, false).unwrap(),
    );
    flyer
}

fn trace(mut flyer: Flyer, ticks: usize) -> Result<String, fastflyer::Error> {
    let mut trace = TickTrace::new(&flyer);
    for tick in 1..=ticks {
        flyer.tick_traced(&mut trace, tick)?;
    }
    Ok(trace.to_json())
}

fn respond(
    stream: &mut TcpStream,
    status: &str,
    content_type: &str,
    body: &[u8],
) -> std::io::Result<()> {
    let header = format!("HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {}\r\nAccess-Control-Allow-Origin: http://127.0.0.1\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n", body.len());
    stream.write_all(header.as_bytes())?;
    stream.write_all(body)
}

fn handle(mut stream: TcpStream) -> std::io::Result<()> {
    stream.set_read_timeout(Some(std::time::Duration::from_secs(10)))?;
    let mut request = Vec::new();
    let mut buffer = [0u8; 8192];
    let header_end = loop {
        if request.len() > 64 * 1024 {
            return respond(
                &mut stream,
                "413 Payload Too Large",
                "text/plain",
                b"headers too large",
            );
        }
        let size = stream.read(&mut buffer)?;
        if size == 0 {
            return Ok(());
        }
        request.extend_from_slice(&buffer[..size]);
        if let Some(end) = request.windows(4).position(|slice| slice == b"\r\n\r\n") {
            break end + 4;
        }
    };
    let headers = match std::str::from_utf8(&request[..header_end]) {
        Ok(value) => value.to_owned(),
        Err(_) => {
            return respond(
                &mut stream,
                "400 Bad Request",
                "text/plain",
                b"invalid headers",
            )
        }
    };
    let mut lines = headers.lines();
    let first = lines.next().unwrap_or("");
    let mut parts = first.split_whitespace();
    let method = parts.next().unwrap_or("");
    let path = parts.next().unwrap_or("");
    let content_length = lines
        .filter_map(|line| line.split_once(':'))
        .find(|(key, _)| key.eq_ignore_ascii_case("content-length"))
        .and_then(|(_, value)| value.trim().parse::<usize>().ok())
        .unwrap_or(0);
    if content_length > 10_000_000 {
        return respond(
            &mut stream,
            "413 Payload Too Large",
            "text/plain",
            b"flyer file too large",
        );
    }
    while request.len() - header_end < content_length {
        let size = stream.read(&mut buffer)?;
        if size == 0 {
            break;
        }
        request.extend_from_slice(&buffer[..size]);
    }
    if request.len() - header_end < content_length {
        return respond(
            &mut stream,
            "400 Bad Request",
            "text/plain",
            b"incomplete body",
        );
    }
    let route = path.split('?').next().unwrap_or(path);
    let ticks = path
        .split("ticks=")
        .nth(1)
        .and_then(|s| s.split('&').next())
        .and_then(|s| s.parse::<usize>().ok())
        .unwrap_or(200)
        .min(1_000_000);
    match (method, route) {
        ("GET", "/") => respond(
            &mut stream,
            "200 OK",
            "text/html; charset=utf-8",
            HTML.as_bytes(),
        ),
        ("GET", "/style.css") => respond(
            &mut stream,
            "200 OK",
            "text/css; charset=utf-8",
            CSS.as_bytes(),
        ),
        ("GET", "/v2.css") => respond(
            &mut stream,
            "200 OK",
            "text/css; charset=utf-8",
            V2_CSS.as_bytes(),
        ),
        ("GET", "/app.js") => respond(
            &mut stream,
            "200 OK",
            "text/javascript; charset=utf-8",
            JS.as_bytes(),
        ),
        ("GET", "/vendor/three.module.js") => respond(
            &mut stream,
            "200 OK",
            "text/javascript; charset=utf-8",
            THREE.as_bytes(),
        ),
        ("GET", "/vendor/three.core.js") => respond(
            &mut stream,
            "200 OK",
            "text/javascript; charset=utf-8",
            THREE_CORE.as_bytes(),
        ),
        ("GET", "/vendor/OrbitControls.js") => respond(
            &mut stream,
            "200 OK",
            "text/javascript; charset=utf-8",
            ORBIT.as_bytes(),
        ),
        ("GET", "/api/demo.flyer") => {
            let bytes = demo().to_bytes().unwrap();
            respond(&mut stream, "200 OK", "application/octet-stream", &bytes)
        }
        ("GET", "/api/demo") => {
            let json = trace(demo(), ticks).unwrap();
            respond(
                &mut stream,
                "200 OK",
                "application/json; charset=utf-8",
                json.as_bytes(),
            )
        }
        ("POST", "/api/trace") => {
            match Flyer::from_bytes(&request[header_end..header_end + content_length]) {
                Ok(flyer) => match trace(flyer, ticks) {
                    Ok(json) => respond(
                        &mut stream,
                        "200 OK",
                        "application/json; charset=utf-8",
                        json.as_bytes(),
                    ),
                    Err(error) => respond(
                        &mut stream,
                        "422 Unprocessable Content",
                        "text/plain; charset=utf-8",
                        error.to_string().as_bytes(),
                    ),
                },
                Err(error) => respond(
                    &mut stream,
                    "400 Bad Request",
                    "text/plain; charset=utf-8",
                    error.to_string().as_bytes(),
                ),
            }
        }
        _ => respond(&mut stream, "404 Not Found", "text/plain", b"not found"),
    }
}

fn main() -> std::io::Result<()> {
    let port = std::env::args()
        .nth(1)
        .and_then(|s| s.parse::<u16>().ok())
        .unwrap_or(8765);
    let listener = TcpListener::bind(("127.0.0.1", port))?;
    println!("FastFlyer viewer: http://127.0.0.1:{port}/");
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                if let Err(error) = handle(stream) {
                    eprintln!("request error: {error}");
                }
            }
            Err(error) => eprintln!("connection error: {error}"),
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn six_block_demo_flies_forward() {
        let mut flyer = demo();
        for _ in 0..12 {
            flyer.tick().unwrap();
            for (pos, block) in flyer.blocks() {
                if !block.moving() {
                    continue;
                }
                let owners = flyer
                    .blocks()
                    .into_iter()
                    .filter(|(owner, candidate)| {
                        candidate.kind() == Kind::Piston
                            && flyer.piston_blocks(*owner).contains(&pos)
                    })
                    .count();
                assert_eq!(owners, 1, "moving block at {pos:?} must have one owner");
            }
        }
        let blocks = flyer.blocks();
        assert_eq!(blocks.len(), 6);
        assert_eq!(
            blocks
                .iter()
                .filter(|(_, block)| block.kind() == Kind::Piston)
                .count(),
            2
        );
        assert_eq!(
            blocks
                .iter()
                .filter(|(_, block)| block.kind() == Kind::Slime)
                .count(),
            2
        );
        assert_eq!(
            blocks
                .iter()
                .filter(|(_, block)| block.kind() == Kind::Observer)
                .count(),
            2
        );
        assert!(blocks.iter().all(|(pos, _)| pos.x >= 2));
    }
}
