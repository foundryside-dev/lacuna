# specimen-rs

<!-- rust-disk-hygiene -->
## Disk hygiene — build artifacts

At the **start of a session**, check the size of the regenerable build dirs:

```
du -sh target .worktrees 2>/dev/null
```

`target/` (Rust build output) and `.worktrees/` are 100% regenerable — nothing in them is
source. They can silently grow to hundreds of GB. If `target/` is **larger than ~10 GB**,
tell me its size and offer to reclaim it with `cargo clean` (the only cost is a slower next
build). Never delete without confirming first.
