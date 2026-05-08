# Contributing

The repo has two layers, with two schemas:

- `data/` entries are validated against `schema/anomaly.schema.json`.
- `benchmarks/` entries are validated against `schema/benchmark.schema.json`.

`scripts/validate.py` runs both, plus a cross-reference check that every
`tension_links` id in `benchmarks/` resolves to an existing `data/` entry.

## Adding an anomaly

1. Pick a stable slug (e.g. `r_k_lepton_universality`) and create
   `data/<slug>.json`.
2. Populate every required field in `schema/anomaly.schema.json`.
3. Cite primary literature. Where possible, prefer the published-journal
   citation plus the arXiv ID. Avoid review-of-reviews chains.
4. Run `python scripts/validate.py`. Open a PR only if validation passes.

## Editing an existing entry

- **Update `tension_history` rather than overwriting it.** The whole point
  of this catalog is that significances drift. If a 4σ result becomes 2σ,
  that's a data point.
- Add the new measurement to `measurements` rather than replacing the
  old one. Old measurements have value as a record.
- If the status changes (`open` → `resolved`, `open` → `contested`),
  note when and why in the summary.

## Adding a benchmark

1. Pick a stable slug (e.g. `vacuum_birefringence_blazar`) and create
   `benchmarks/<slug>.json`.
2. Set `kind` to one of: `reduction`, `precision_test`,
   `principle_invariance`, `forbidden_phenomenon`, `cosmological_observable`,
   `tension_to_address`.
3. Fill in `requirement` as a precise, plain-English statement of what
   any candidate framework must do — phrased so it is testable, not
   aspirational.
4. Always populate `what_it_excludes` so it is clear what model classes
   actually die against this benchmark. A constraint that excludes
   nothing is not useful.
5. Cite primary literature for the bound. No textbook-only references.
6. Run `python scripts/validate.py`.

## What does *not* belong

- Speculation presented as fact. If you want to discuss a possible
  reformulation (modified gravity, GA, tensor-network mappings, etc.),
  put it in a separate `notes/` document and label it as speculative.
- Anomalies below ~2σ unless they have a strong theoretical motivation
  or are part of a coherent pattern with other entries.
- Numerology. The point of this catalog is to be a useful piece of
  evidence — not a search for shapes that are interesting only to us.

## Number hygiene

- Keep central values and uncertainties in the units the source paper
  used; specify units in every numeric field.
- For asymmetric errors use a string like `"+0.020/-0.014"`.
- σ values in `tension_history` are allowed to be strings when they
  depend on which baseline you use (e.g. `"~1 (lattice) / ~5 (data-driven)"`).
- Don't invent a σ. Cite the source's own claim, or compute it
  transparently and document the formula in the entry.

## Tests

```bash
pip install jsonschema
python scripts/validate.py
```

CI is not yet wired up; if you set it up, the green check is just
`python scripts/validate.py` against the whole `data/` directory.
