//! Tiny, dependency-free browser ABI. Output buffers remain valid until the next call.

use std::cell::RefCell;

use crate::debug::TickTrace;
use crate::Flyer;

#[derive(Default)]
struct Output {
    flyer: Vec<u8>,
    trace: Vec<u8>,
    error: Vec<u8>,
    shift: [i64; 3],
}

thread_local! { static OUTPUT: RefCell<Output> = RefCell::new(Output::default()); }

#[no_mangle]
pub extern "C" fn ff_alloc(length: usize) -> *mut u8 {
    let mut bytes = vec![0u8; length].into_boxed_slice();
    let pointer = bytes.as_mut_ptr();
    std::mem::forget(bytes);
    pointer
}

#[no_mangle]
pub unsafe extern "C" fn ff_free(pointer: *mut u8, length: usize) {
    if !pointer.is_null() && length > 0 {
        drop(Box::from_raw(std::ptr::slice_from_raw_parts_mut(
            pointer, length,
        )));
    }
}

fn run(
    input: &[u8],
    tick: usize,
    simulate: bool,
    detailed: bool,
) -> Result<(Vec<u8>, Vec<u8>, [i64; 3]), String> {
    let mut flyer = Flyer::from_bytes(input).map_err(|error| error.to_string())?;
    let mut trace = (!simulate || detailed).then(|| TickTrace::new(&flyer));
    if simulate {
        if detailed {
            flyer
                .tick_traced(trace.as_mut().expect("detailed trace exists"), tick)
                .map_err(|error| error.to_string())?;
        } else {
            flyer.tick().map_err(|error| error.to_string())?;
        }
    }
    let (x, y, z) = flyer.normalization_shift();
    let convert =
        |value| i64::try_from(value).map_err(|_| "coordinate shift exceeds i64".to_string());
    let shift = [convert(x)?, convert(y)?, convert(z)?];
    let bytes = flyer.to_bytes().map_err(|error| error.to_string())?;
    Ok((
        bytes,
        trace
            .map(|value| value.to_json().into_bytes())
            .unwrap_or_default(),
        shift,
    ))
}

/// `simulate=0` inspects a saved flyer. `simulate=1` advances one tick.
/// Detailed traces contain only this one tick and are never retained by Rust.
#[no_mangle]
pub unsafe extern "C" fn ff_run(
    pointer: *const u8,
    length: usize,
    tick: usize,
    simulate: u32,
    detailed: u32,
) -> u32 {
    if pointer.is_null() || length == 0 {
        return 0;
    }
    let input = std::slice::from_raw_parts(pointer, length);
    let result = run(input, tick, simulate != 0, detailed != 0);
    OUTPUT.with(|slot| {
        let mut output = slot.borrow_mut();
        match result {
            Ok((flyer, trace, shift)) => {
                output.flyer = flyer;
                output.trace = trace;
                output.error.clear();
                output.shift = shift;
                1
            }
            Err(error) => {
                output.flyer.clear();
                output.trace.clear();
                output.error = error.into_bytes();
                0
            }
        }
    })
}

#[no_mangle]
pub extern "C" fn ff_flyer_ptr() -> *const u8 {
    OUTPUT.with(|slot| slot.borrow().flyer.as_ptr())
}
#[no_mangle]
pub extern "C" fn ff_flyer_len() -> usize {
    OUTPUT.with(|slot| slot.borrow().flyer.len())
}
#[no_mangle]
pub extern "C" fn ff_trace_ptr() -> *const u8 {
    OUTPUT.with(|slot| slot.borrow().trace.as_ptr())
}
#[no_mangle]
pub extern "C" fn ff_trace_len() -> usize {
    OUTPUT.with(|slot| slot.borrow().trace.len())
}
#[no_mangle]
pub extern "C" fn ff_error_ptr() -> *const u8 {
    OUTPUT.with(|slot| slot.borrow().error.as_ptr())
}
#[no_mangle]
pub extern "C" fn ff_error_len() -> usize {
    OUTPUT.with(|slot| slot.borrow().error.len())
}
#[no_mangle]
pub extern "C" fn ff_shift_x() -> i64 {
    OUTPUT.with(|slot| slot.borrow().shift[0])
}
#[no_mangle]
pub extern "C" fn ff_shift_y() -> i64 {
    OUTPUT.with(|slot| slot.borrow().shift[1])
}
#[no_mangle]
pub extern "C" fn ff_shift_z() -> i64 {
    OUTPUT.with(|slot| slot.borrow().shift[2])
}
