use fastflyer::Flyer;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = std::env::args().skip(1);
    let input = args.next().ok_or("expected input path")?;
    let output = args.next().ok_or("expected output path")?;
    if args.next().is_some() {
        return Err("too many arguments".into());
    }
    Flyer::load(input)?.save(output)?;
    Ok(())
}
