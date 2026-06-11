# wl-native-lib-load

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/preview_sinks.py` → `load_codec_library`
- **Category:** injection
- **Demonstrates:** `wardline`
- **Expected finding:** `wardline` / `PY-WL-124`

## Why it's here

Untrusted path reaches ctypes.CDLL — native-library load (preview).

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
