# Substratum

A curated, schema-validated catalog of open tensions and anomalies in
contemporary physics, spanning particle physics, cosmology, gravitation,
and condensed matter.

The repository has two parallel layers:

- **`data/`** — a record of where the Standard Model and ΛCDM are currently
  under empirical stress. Each entry tracks the discrepancy's history,
  current significance, primary references, and status (open, contested,
  resolved, theoretical).
- **`benchmarks/`** — the **non-negotiable constraint set** that any
  candidate replacement framework must satisfy before it is worth taking
  seriously. Reductions to known theories, foundational-principle tests,
  forbidden phenomena, and a meta-entry pointing back into `data/` for
  the open tensions any new framework has to explain.

Together: tensions tell you where the current models break; benchmarks tell
you what the next model has to look like.

## Why

Tension trackers exist inside individual subfields (PDG for particle physics,
review articles for cosmology), but no single, structured, cross-domain
dataset does this in a way that survives time. Significances drift. The 2022
W-mass anomaly was 7σ at CDF and is now consistent with the SM after ATLAS
and CMS measurements. The muon g-2 tension was ~4σ in 2021 and has shrunk
substantially as lattice QCD evaluations of the hadronic vacuum polarization
have matured. A useful atlas tracks that motion, not a single snapshot.

## What this repo is *not*

- Not a unified theory.
- Not a "translation layer" that maps unrelated phenomena into shared
  jargon. Such mappings, without a derivation, are numerology.
- Not a claim that the Standard Model or General Relativity are wrong.
  They are extraordinarily well-tested effective theories. Tensions are
  where the next physics *might* live, or where systematics are still
  being understood.

## Scope of an entry

Each anomaly is a JSON file under `data/` validated against
`schema/anomaly.schema.json`. Required fields:

- **observable** — what is measured (e.g. `a_mu = (g-2)/2`)
- **characteristic_scale** — approximate length and energy scale
- **standard_prediction** — value, uncertainty, model, references
- **measurements** — array of independent experimental results
- **tension_history** — σ over time, so the record reflects how the
  picture has actually evolved
- **status** — `open`, `contested`, `resolved`, or `theoretical`
- **references** — primary literature, DOIs where available

Optional structured hooks (filled per domain when meaningful):

- **trend** — `growing` / `stable` / `shrinking` / `resolved` /
  `theoretical`. Orthogonal to status.
- **principles_stressed** — which foundational principles (unitarity,
  causality, Lorentz, CPT, equivalence, lepton-flavor universality, …)
  the anomaly would stress *if* it survives systematics. Most entries
  explicitly record `principle: none, status: none` — that the anomaly
  does *not* violate a foundational principle is itself information.
- **smeft_context** — for particle entries, the Warsaw-basis SMEFT
  operator(s) most directly probed plus references to standard global
  fits (Fitmaker, SMEFiT, HEPfit). No invented dictionaries; we use
  the BSM community's working framework.
- **cosmology_context** — for cosmology / astrophysics entries, the
  extension classes that move the needle (early dark energy,
  interacting dark sectors, modified recombination, …) and the *cost
  elsewhere* of each (which other tension or constraint they worsen).

See `schema/anomaly.schema.json` for the full schema and
`CONTRIBUTING.md` for how to add or update entries.

## Current entries

### `data/` — open tensions

| ID | Domain | Status | Trend | Latest σ |
|----|--------|--------|-------|----------|
| `muon_g_minus_2` | particle | contested | shrinking | ~1–4 (depends on SM input) |
| `hubble_tension` | cosmology | open | stable | ~5 |
| `w_boson_mass` | particle | contested | shrinking | CDF outlier; world avg consistent |
| `s8_tension` | cosmology | open | stable | ~2–3 |
| `cosmological_constant` | theoretical | theoretical | — | naturalness, not σ |

### `benchmarks/` — what any new framework must satisfy

Each entry includes a `procedural` block: the canonical parameterization
(PPN, SMEFT, SME, ΛCDM extensions, Yukawa…), the predicted observable,
the bound restated in those parameters, what a candidate framework must
expose to be evaluated, and an `evaluator_status` flag indicating how
hard the evaluation is (`trivial` / `tractable` / `requires_code` /
`requires_simulation` / `requires_lattice` / `research_problem`).

44 benchmark entries across 11 domains. Every entry is backed by
primary literature (arXiv / DOI). See `ROADMAP.md` for the full
populated list and remaining additions.

**Domain coverage:**

| Domain | Entries | Canonical parameterizations |
|--------|---------|------------------------------|
| Gravity (PPN, GW, EP) | 12 | PPN, PPK, TIGER, Yukawa, SME-grav |
| Particle precision (QED) | 4 | SMEFT (Warsaw), bound-state QED |
| Flavor and CP violation | 10 | WET, CKM, SMEFT CP-odd |
| Weak / EW precision | 3 | SMEFT, Peskin-Takeuchi S/T/U |
| Lorentz / CPT | 4 | SME (photon, meson, lepton sectors) |
| Cosmology | 7 | ΛCDM + extensions, Boltzmann codes |
| Dark matter | 5 | DM-EFT, SIDM, axion couplings |
| QCD | 3 | Lattice QCD, χPT |
| Astrophysics | 3 | TOV, helioseismic inversion |
| Constants / clocks | 1 | dilaton d_e, ULDM |
| Meta | 1 | links to `data/` |

The procedural block makes each constraint executable in principle.
For `trivial` and `tractable` cases (graviton speed, EP, m_W, S/T/U,
PPN parameters, axion-photon coupling), evaluation against a candidate
framework is a one-liner; for `requires_simulation` (CMB, BBN, LSS,
Lyman-α, helioseismology), the framework needs to be implemented as a
module in CLASS / CAMB / PArthENoPE / GARSTEC.

## Roadmap

1. **Data layer (this milestone).** Schema, ~5–10 high-quality seed
   entries, validation tooling.
2. **Coverage.** Extend to: KOTO/NA62 rare kaon decays, B-anomalies
   (R(K), R(D*)), atomic parity violation, neutron lifetime, ANITA
   anomalous events, lithium problem, CMB cold spot, axis of evil,
   superconductor tensions.
3. **Visualization.** Plot σ-vs-time per entry; cross-domain landscape
   on (length_scale, energy_scale).
4. **Optional, clearly speculative.** A separate, explicitly-flagged
   `notes/` area where reformulation ideas (geometric algebra, tensor
   networks, modified gravity) can be discussed *without* being mixed
   into the rigorous data layer.

## Validation

```bash
python scripts/validate.py
```

Validates every file in `data/` against the schema and reports problems.
