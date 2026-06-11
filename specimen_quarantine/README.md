# specimen_quarantine — deliberately broken inputs

Committed fixtures for the FAIL-CLOSED tour legs. Excluded from the main
wardline scan root (weft.toml), pytest (testpaths), and the package build.
The tour scans/feeds these expecting the gate to TRIP — a quarantine gate
that passes is a verify failure.
