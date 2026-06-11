//! Clean-core catalog module — plus the two archaeology lacunae.

/// In-project trait so the derives edge resolves in-project (resolved-or-dropped contract).
pub trait Catalogued {
    fn shelf(&self) -> &'static str;
}

// LACUNA (rs-cfg-twin): two mutually-exclusive #[cfg] impls of the same type
// split into @cfg(...) qualname twins in the loomweave index.
pub struct Shelf;

#[cfg(feature = "metric")]
impl Shelf {
    pub fn capacity(&self) -> u32 { 100 }
}

#[cfg(not(feature = "metric"))]
impl Shelf {
    pub fn capacity(&self) -> u32 { 80 }
}

// LACUNA (rs-derives): a derive invocation naming the in-project trait — the
// anchored `derives` edge. Lives under a disabled cfg so `cargo check` never
// name-resolves it (no proc-macro needed) while tree-sitter still extracts it.
// The derive path is crate-qualified because loomweave's resolver treats a
// BARE derive path as crate-root-relative (specimen_rs.Catalogued — a miss);
// `crate::catalog::Catalogued` resolves to the in-project trait.
#[cfg(feature = "archaeology_specimen")]
mod derive_demo {
    #[derive(crate::catalog::Catalogued)]
    pub struct Pamphlet;
}

pub fn summary() -> String {
    format!("shelf capacity: {}", Shelf.capacity())
}
