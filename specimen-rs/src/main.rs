//! The Rust wing of the lacuna specimen: a clean-cored catalog CLI slice with
//! five INTENTIONAL, catalogued flaws (see tour/lacunae.toml). Do NOT fix them.

use std::process::Command;

mod catalog;
#[path = "shelf_layout.rs"]
mod shelving; // LACUNA (rs-path-mount): #[path] module mount — loomweave routes it (ADR-049 Am.8)

/// @trusted(level=ASSURED)
fn run_export() {
    // LACUNA (RS-WL-108): operator input reaches the program slot of Command::new.
    // `std::env::args` is a built-in EXTERNAL_RAW vocabulary source (rust_taint.yaml);
    // it must be called HERE — wardline's Rust taint model is flat-local, so taint
    // does not cross fn boundaries via parameters.
    let prog = std::env::args().nth(1).unwrap_or_default();
    Command::new(prog).status().ok();
}

/// @trusted(level=ASSURED)
fn shell_archive() {
    // LACUNA (RS-WL-112): operator input reaches a `sh -c` command line.
    let line = std::env::args().nth(2).unwrap_or_default();
    Command::new("sh").arg("-c").arg(line).status().ok();
}

fn main() {
    run_export();
    shell_archive();
    println!("{}", catalog::summary());
    println!("{}", shelving::label());
}
