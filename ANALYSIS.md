# What the catalog now shows

*Synthesis of the dot-alignment report against 43 puzzles × 153 mechanisms × 75 benchmarks. Generated for the seed-density milestone. The raw graph is in `dot_alignment.md`; this document picks out what's worth saying.*

## 1. The convergent-puzzle ranking

When many distinct mechanisms target one puzzle, the puzzle is the active battleground; when few do, the puzzle is either solved or untouchable. Sorted by attention:

| puzzle | mechanisms targeting it | reading |
|---|---|---|
| `dark_matter_identity` | 44 | overwhelmingly the most-targeted puzzle. The fact that no proposal in the field has even a 60% confidence label tells you that mass attention has *not* produced consensus. |
| `cosmological_constant_smallness` | 22 | second-most. Yet every mechanism here is `contested` or weaker — the highest-status entry (`anthropic_landscape`) is `contested/solves`. The CC is *attention-rich, resolution-poor*: lots of swings, nothing landing. |
| `baryon_asymmetry` | 21 | unusually high *solver* density (13 of 21 are `solves`). The puzzle is structurally easy to attack — Sakharov conditions are explicit — and many routes work in principle. The bottleneck is *experimental discrimination*, not theory. |
| `inflation_initial_conditions` | 20 | similar to baryogenesis: many `solves`, three `established`. The shape of the inflaton potential is *underdetermined* by current data; LiteBIRD / CMB-S4 will collapse the candidate count. |
| `gauge_hierarchy_problem` | 20 | every entry is `ameliorates`, none `solves`. The most-attacked puzzle with the worst solution density. Post-LHC the field has *no* mechanism it confidently calls a solution. |
| `neutrino_mass_smallness` | 19 | seesaw is the convergent answer: 5 of the 19 are seesaw variants or close cousins. `explains_pattern/established` for `seesaw_type_i` is the highest confidence on any neutrino-mechanism edge. |
| `flavor_mass_hierarchy` | 13 | dominated by `explains_pattern` edges (8 of 13). The puzzle is *pattern-shaped*, and the mechanisms know it — they compress structure, not just fit. |
| `black_hole_information` | 7 | rare puzzle with two `SOLVES/established` edges (`ads_cft_holography`, `island_formula_bh_information`). This is the **clearest theoretical victory in the catalog** — the puzzle is largely closed for asymptotically-AdS geometries. |

The pattern: **attention does not equal progress.** The hierarchy and CC problems each have ~20 mechanisms and zero established solves. Black-hole information has 7 and two established solves. The dot count isn't the score — *the role-label distribution* is.

## 2. The high-degree mechanisms

Mechanisms touching ≥3 puzzles (the "GIM/SUSY/inflation" signature):

| mechanism | degree | status | solves/explains | what it actually does |
|---|---|---|---|---|
| `mssm` | 4 | niche | 0 | All four edges are `ameliorates`. Touches everything, closes nothing. Post-LHC degradation visible directly in the role labels. |
| `so10_gut` | 4 | niche | 0 | Same pattern: broad reach, all ameliorates. Embeds seesaw and unification but doesn't predict any of the input numbers. |
| `split_susy` | 4 | niche | 2 SOLVES | Strongest BSM candidate by this metric: explicitly solves DM identity + gauge coupling unification, ameliorates hierarchy and vacuum metastability. Pays the price by being `niche` (anthropic Higgs mass). |
| `axion_cosmic_birefringence` | 3 | mainstream | 1 SOLVES | Targets a *specific anomaly*, plus DM and CC. Worth tracking: the only `mainstream` high-degree mechanism that actually solves a puzzle. |
| `f_theory_compactification` | 3 | mainstream | 2 explains_pattern | Most-compressive string mechanism by the bipartite metric: produces flavor, unification, *and* landscape predictivity from the same construction. |
| `large_volume_scenario_lvs` | 3 | mainstream | 1 explains_pattern | Sibling of F-theory. The two together cover everything string-theoretic the catalog asks about. |
| `modular_flavor_symmetry` | 3 | niche | 3 explains_pattern | Three explains_pattern edges with only 3 new parameters → **compression score 1.0**. The cleanest non-trivial entry in the table. |
| `sidm_yukawa_dark_force` | 3 | niche | 2 SOLVES | Tulin-Yu-Zurek mechanism solves halo diversity *and* small-scale-structure simultaneously. The clearest dot-alignment in the DM-phenomenology space. |
| `nmssm` | 3 | niche | 0 | Same problem as MSSM: touches Higgs mass + hierarchy + DM but ameliorates each. |
| `dark_dimension_swampland` | 3 | niche | 0 | Speculative — touches three biggest puzzles with one extra dimension, but everything is `ameliorates/proposed`. |

The **honest top-three by compression-plus-coverage**: `modular_flavor_symmetry`, `f_theory_compactification`, `sidm_yukawa_dark_force`. None is mainstream-established; all are *worth comprehensive cross-domain accountability*.

## 3. Structural-feature clusters

Latent mechanism families surface from shared `structural_features` tags:

- **Pseudo-Goldstone family**: `composite_higgs`, `little_higgs`, `natural_inflation`, `peccei_quinn_axion`, `relaxion`, `twin_higgs`. One structural idea (a light boson protected by approximate shift symmetry) recurring across hierarchy, strong CP, DM, and inflation. This is the catalog's clearest hidden cross-puzzle dot.
- **Ultralight scalar family**: `early_dark_energy`, `k_essence_dark_energy`, `quintessence`, `ultralight_scalar_dm`. Same kind of field (m ≲ 10⁻²⁷ eV) repurposed for DM, DE, and the H₀ tension. Suggests these are aspects of *one* underlying field, not four.
- **Out-of-equilibrium + sphaleron-conversion**: 6 of the 12 baryogenesis mechanisms share both tags. The Sakharov conditions impose strong structural similarity.
- **Higgs-portal family**: scalar DM, vector DM, vacuum stabilizer, EWPT singlet — same operator |H|² O for different phenomenology. A natural unified portal sector probably underlies all four.

Structural-feature co-occurrence is doing its intended job: surfacing connections invisible at the level of individual mechanism names.

## 4. Dependency chains (`requires`)

A few mechanisms can't stand alone:
- All leptogenesis variants `require` `neutrino_mass_smallness` to be addressed elsewhere (the right-handed neutrinos do double duty).
- All SUSY-breaking mechanisms `require` `gauge_hierarchy_problem` (they're solutions to *how* SUSY breaks, given that it does).
- `axiogenesis` and `kinetic_misalignment_axion` `require` `strong_cp_problem` to already be solved by the axion.

The dependency graph means the catalog tracks not just which mechanisms address which puzzles, but **which mechanism families are mutually constitutive**. A complete framework needs to pick a consistent set across the dependency edges.

## 5. What the catalog has actually proven

- **`black_hole_information` is the only puzzle in the catalog with two established/solves edges.** That's a real theoretical result, not a model proposal.
- **The hierarchy problem has none.** Twenty mechanisms target it; none of them, by their own status labels, claims to solve it. This is the honest current state of naturalness.
- **Dark matter is over-served by mechanisms and under-served by data.** 44 distinct ideas, no consensus.
- **Flavor structure is converging.** Modular and froggatt-nielsen style mechanisms dominate, with `explains_pattern` edges at proposed-confidence; future precision flavor data will discriminate.
- **String theory's claim to compress observed structure is concrete.** F-theory + LVS together touch landscape, flavor, unification, hierarchy, and CC with finite parameter counts. They earn their `mainstream` status by the bipartite metric, even though every individual edge is `proposed`.

## 6. What's still missing from the bipartite picture

- Compression score is *parameter-naive*: 3 new parameters can mean very different things in different theories. A weighted version (counting tunings, dimensionalities, hidden complexity) is the natural next step.
- The graph treats `composes_with` as undirected; really some compositions are tight (seesaw needed by leptogenesis) and others loose (SUSY composes with anything). Edge weights would help.
- 24 benchmarks are still orphan (no mechanism touches them). These are mostly CPT and gravity-tests that no proposed mechanism even tries to predict — the most-honest signal of *what mechanism space is missing*.

## 7. Operational summary

If a candidate framework comes through next and addresses (a) DM identity *and* (b) hierarchy *and* (c) flavor pattern using fewer than ~5 new parameters, the catalog will register it as the highest-compression entry above. That's the bar.

The catalog won't tell you which mechanism is correct. It will tell you which one closes the most dots with the least conjecture — and the dot-counting machinery is now dense enough that the answer is non-trivial.
