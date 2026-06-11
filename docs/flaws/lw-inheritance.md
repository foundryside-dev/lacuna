# lw-inheritance

_Generated from `tour/lacunae.toml`. Do not edit by hand._

- **Location:** `specimen/repository.py` → `InMemoryRepository`
- **Category:** navigation
- **Demonstrates:** `loomweave`
- **Expected finding:** `loomweave` / `inherits-from`

## Why it's here

specimen.repository.InMemoryRepository inherits from both Repository and TimestampMixin, and BookRepository/UserRepository inherit from it — the Python plugin's inherits_from relation edges (ontology 0.8.0, ADR-051) record the hierarchy, and Loomweave's entity_relation_list walks it both ways (direction=in answers "what subclasses X").

> This is an intentional, permanent demonstration fixture. Removing or "fixing" it fails `make verify`.
