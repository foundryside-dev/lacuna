//! Mounted via `#[path = "shelf_layout.rs"] mod shelving;` in main.rs (rs-path-mount).

pub fn label() -> &'static str {
    "shelving: mounted via #[path]"
}
