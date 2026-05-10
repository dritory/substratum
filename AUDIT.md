# Audit protocol

The catalog is large enough that no single human keeps every claim in
their head. The growth rate also makes it easy to introduce small faults
faster than they get caught. This file documents the feedback loop that
prevents that and the queue of items still needing manual physicist
review.

## What runs automatically

Three layers run on every push and pull request via
`.github/workflows/ci.yml`:

1. **`scripts/validate.py`** — schema validation + cross-reference
   resolution. Catches: unknown puzzle/mechanism/benchmark ids, schema
   violations, filename-id mismatches.
2. **`scripts/check_citations.py`** — for every arXiv ID found anywhere
   in `data/`, `benchmarks/`, `puzzles/`, `mechanisms/`, `frameworks/`,
   resolves it against the arXiv API and verifies the first-author
   surname appears in the citation text. Catches: typoed IDs,
   copy-paste mismatches, withdrawn papers.
3. **`scripts/audit.py`** — consistency auditor. Catches:
   - `status_coherence` — mechanisms labelled `disfavored`/`historical`
     without a declared benchmark violation or empirical-pressure
     language in their history note.
   - `mainstream_must_close` — mechanisms marked `mainstream` that
     don't close any puzzle with role `solves` / `explains_pattern`.
   - `provenance_*` — references that lack both an `arxiv` ID and a
     `doi` (or a `url` for pre-electronic literature).
   - `compose_excludes_consistency` — internal contradictions between
     `composes_with` and `excludes` lists, including across entries.
   - `bound_consistency` — numerical bounds quoted in mechanism notes
     that disagree with the source benchmark's `current_bound` by more
     than a factor of two.
   - `orphan_benchmarks` (informational) — benchmarks not touched by
     any mechanism.

Any blocking issue fails CI and blocks merge.

## What needs human review

The automation catches structural and citational faults but cannot
evaluate physics correctness. The following classes of claim are
inherently judgment-laden and should be spot-checked by a physicist
reading each entry:

### High-priority manual checks

For every `mechanisms/<id>.json` entry, a reviewer should verify:

1. **Role assignments.** Each `addresses_puzzles[].role` is one of
   `solves` / `ameliorates` / `explains_pattern` / `requires`. The
   distinction between `solves` and `ameliorates` is the most
   subjective edge in the graph. Convention: a mechanism `solves` a
   puzzle if, given the mechanism, the puzzle's characteristic_numbers
   become natural without additional fine-tuning. It `ameliorates` if
   it softens the puzzle but leaves residual tuning.
2. **Confidence labels.** `established` / `proposed` / `contested` /
   `disfavored`. These should reflect the current literature
   consensus, not the mechanism's intrinsic appeal.
3. **`new_parameters_count`.** Used as the denominator of the
   compression score. Should count independent free parameters
   introduced beyond the baseline framework. Conventions vary; current
   choices are documented in each entry's `introduces.note`.
4. **`status` labels.** `mainstream` / `niche` / `historical` /
   `disfavored`. `mainstream` should be reserved for proposals that
   genuinely close at least one puzzle and remain actively cited;
   foundational scaffolding (e.g., `wess_zumino_supersymmetry`,
   `dynamical_susy_breaking`, `polchinski_d_branes`) is intentionally
   labelled `niche` because in our graph it does not independently
   close a specific puzzle.
5. **`touches_benchmarks[].effect`.** `respects` /
   `near_bound` / `violates` / `predicts_signal`. The most useful
   judgment call; should reflect the mechanism's prediction in its
   natural parameter space, not in a fine-tuned corner.

### Known-uncertain claims

These specific encodings are flagged for physicist review:

- `mssm.new_parameters_count: 105` — Haber 1997
  ([arXiv:hep-ph/9709450](https://arxiv.org/abs/hep-ph/9709450)) gives
  124 for the most-general MSSM; 105 is sometimes quoted for the
  hard-SUSY-breaking parameters beyond the SM. Both numbers appear in
  the literature; the count is interpretation-dependent.
- `r_parity_violation.new_parameters_count: 49` — counts only the new
  R-parity-violating couplings, not the underlying MSSM parameters.
  Compression score for RPV thus measures only its incremental cost
  over MSSM, not the total.
- `island_formula_bh_information.new_parameters_count: 0` — the
  mechanism uses no free parameters beyond the gravitational and
  matter content already in the theory; this gives an effectively
  infinite compression score, which is intended but should be read as
  "a derivation, not a postulate."
- `dark_dimension_swampland` `addresses_puzzles` lists three puzzles
  (cosmological constant, dark matter, neutrino mass smallness) with
  confidence `proposed`. The cross-puzzle leverage is real per
  Montero-Vafa-Valenzuela, but the role-`ameliorates` judgments are
  early; future swampland-conjecture refinements may change them.
- Several modified-gravity entries (`teves_relativistic_mond`,
  `mannheim_conformal_gravity`, `emergent_entropic_gravity`,
  `galileon_modified_gravity`) carry `violates` edges on the Bullet
  Cluster or CMB benchmarks plus status `disfavored`. The encoded
  violations reflect the post-2006 / post-2017 (GW170817) consensus;
  proponents contest specific encodings.

The list above is the queue for the first physicist-eye sweep. As
issues are resolved or new claims added, this section should be
updated.

## How to add a new entry

1. Find primary references; require at least one with arXiv or DOI.
2. Encode the entry against the relevant schema.
3. Run `python scripts/validate.py` and
   `python scripts/audit.py` locally. Fix any blocking issues.
4. Commit. CI re-runs both scripts plus
   `scripts/check_citations.py` against the arXiv API.
5. If the new entry uses the `mainstream` status, justify by
   ensuring at least one `solves` or `explains_pattern` edge exists.
   If it uses `disfavored` or `historical`, justify by either a
   `violates` edge or empirical-pressure language in the `history`
   field.

## History of caught errors

These were caught and fixed during the source-verification pass; they
illustrate the failure modes the automation targets.

| Date           | Entry                                | Error                                                                                                                                       | Fix |
|----------------|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|-----|
| Round 1 audit  | `twin_higgs.json` [arXiv:1410.6808]  | Author "Longhitano" should be "Longhi"; title was "A Cornucopia of Compelling Cosmological Compositeness" rather than the published title. | Citation corrected to Craig-Knapen-Longhi, "Neutral Naturalness from the Orbifold Higgs", JHEP 03, 097 (2015). |
| Round 1 audit  | `nnaturalness.json` [arXiv:1607.06821] | Title was the arXiv-abstract paraphrase rather than the published title "Nnaturalness".                                                  | Corrected to "Nnaturalness". |
| Round 1 audit  | `ultralight_scalar_dm.json` [astro-ph/0003365] | Title "Fuzzy cold dark matter" was a popular alias rather than the actual paper title "Cold and Fuzzy Dark Matter".                       | Corrected. |
| Round 1 audit  | `mssm.json` LZ note                  | Cited bound `< 2e-47 cm^2 at ~30 GeV` was the LZ 2022 result, not LZ 2024 (`< 9.2e-48 cm^2 at m_chi ~36 GeV`).                              | Updated to LZ 4.2-tonne-year result. |
| Round 1 audit  | `wimp_thermal_freezeout.json` LZ note | Same outdated LZ bound.                                                                                                                   | Updated. |
| Round 1 audit  | `neutrino_mass_scale_seesaw.json`    | NuFIT label was "5.3" but arXiv:2007.14792 is the NuFIT 5.0 paper; sum-m_nu bound was Planck 2018 (0.12 eV) rather than DESI Y1 (0.072 eV); m_beta bound was KATRIN 2022 (0.8 eV) rather than KATRIN 2024 (0.45 eV). | All corrected. |
| Round 2 audit  | `conformal_cyclic_cosmology.json`    | Status `disfavored` but no `violates` edge or empirical-pressure language to justify.                                                       | History field already used "contested" and "speculative"; audit keyword list expanded to recognise both. |
| Round 2 audit  | `gut_baryogenesis.json`              | Status `historical` but no justification keywords.                                                                                          | History uses "supplanted"; audit keyword list expanded. |
| Round 2 audit  | 15 mechanisms                        | Status `mainstream` but no puzzle closed with role `solves` or `explains_pattern`.                                                          | Downgraded 15 to status `niche` (foundational frameworks that don't independently close a puzzle in our graph). |
| Round 2 audit  | 22 references                        | Pre-electronic / book-chapter references missing `arxiv`, `doi`, and `url`.                                                                 | Added INSPIRE-HEP, NASA ADS, or DOI links where available. |
| Round 2 audit  | `ultralight_scalar_dm` Lyman-α note  | Compared ULDM mass bound to the WDM thermal-mass bound stored as the benchmark `current_bound` (two different particle classes).            | Clarified the note. |
