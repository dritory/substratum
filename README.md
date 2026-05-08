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

| ID | Kind | Parameterization | Excludes |
|----|------|------------------|----------|
| `recover_general_relativity` | reduction | PPN + PPK + TIGER | unscreened modified-gravity at solar-system scale |
| `recover_standard_model_precision` | reduction | SMEFT (Warsaw) | sub-TeV new physics above current precision |
| `graviton_speed_gw170817` | precision_test | direct (c_gw − c)/c | most scalar/vector-tensor dark-energy models |
| `equivalence_principle_microscope` | principle | Eötvös η + dilaton charge | composition-dependent fifth forces above η ~ 10⁻¹⁵ |
| `antihydrogen_gravity_alpha_g` | principle | a_g̅/g + grav. SME | antimatter antigravity |
| `lorentz_invariance_photon` | principle | SME photon sector | linear-in-E LIV near M_Planck |
| `inverse_square_law_short_distance` | precision_test | Yukawa (α, λ) | mm-scale large extra dimensions |
| `bullet_cluster_lensing_offset` | cosmological | lensing-vs-gas offset | pure modified-gravity-without-DM |
| `proton_decay_lifetime` | forbidden | M_GUT, BNV SMEFT | minimal SU(5), most minimal SO(10) GUTs |
| `neutron_electric_dipole_moment` | forbidden | θ_QCD + SMEFT CP | many TeV-SUSY phases; large strong-CP phase |
| `electron_edm_jila` | forbidden | SMEFT C_eγ + Barr-Zee | leptonic CP violation at TeV |
| `alpha_variation_atomic_clocks` | precision_test | α̇/α + dilaton d_e | rolling moduli, ULDM photon coupling |
| `bbn_light_element_abundances` | cosmological | η, N_eff + nuclear network | early-universe ΔN_eff > ~0.3 |
| `cmb_acoustic_peak_structure` | cosmological | ΛCDM + extensions | drastic recombination physics, large EDE |
| `address_open_tensions` | tension_to_address | links to `data/` | "fix one tension, ignore the others" |

See `ROADMAP.md` for the inventory of constraints we have identified
but not yet populated (~30 more, covering extended PPN, B-meson and
kaon flavor physics, Lorentz/CPT in matter sectors, primordial GW
ratio, dark-matter direct detection, pulsar timing arrays, and more).

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
