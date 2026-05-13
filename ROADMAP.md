# Roadmap

This file tracks the constraint inventory we have populated and what
remains. The goal is a procedural benchmark set comprehensive enough
that any candidate unified-physics framework can be evaluated against
it, plus a layered representation of naturalness puzzles and proposed
mechanisms that surfaces dot-alignment across the open structural
problems.

## Conventions

- A constraint is **populated** when it has a JSON entry in
  `benchmarks/` that validates against `schema/benchmark.schema.json`,
  cites primary literature with arXiv/DOI, and (where applicable)
  includes a `procedural` block with the canonical parameterization.
- A puzzle is populated when it validates against
  `schema/puzzle.schema.json` and includes characteristic numbers and
  primary references.
- A mechanism is populated when it validates against
  `schema/mechanism.schema.json`, declares at least one
  `addresses_puzzles` edge with a confidence label, and includes
  primary references.
- Every entry must be backed by primary references. No textbook-only
  citations.

## Status

### Populated (75 benchmark entries, 5 data entries, 43 puzzles, 153 mechanisms)

**Gravity (10):**
- `recover_general_relativity` (PPN, PPK, GW waveform)
- `graviton_speed_gw170817` (kills most scalar/vector-tensor DE)
- `equivalence_principle_microscope` (η < 1.5×10⁻¹⁵)
- `inverse_square_law_short_distance` (Eöt-Wash 52 μm)
- `antihydrogen_gravity_alpha_g` (ALPHA-g 2023)
- `bullet_cluster_lensing_offset` (kills MOND-only DM)
- `nordtvedt_parameter_strong_ep` (LLR + PSR J0337+1715)
- `frame_dragging_gravity_probe_b` (geodetic + LT precession)
- `binary_pulsar_psr_b1913_16` (Hulse-Taylor quadrupole formula)
- `binary_pulsar_psr_j0737_3039` (double pulsar PPK)
- `graviton_mass_gw_dispersion` (m_g < 1.27×10⁻²³ eV)
- `gw_polarization_modes` (pure-tensor preferred at GW170814)

**Particle physics — precision (4):**
- `recover_standard_model_precision` (SMEFT)
- `electron_g_minus_2_precision` (cleanest QED test)
- `hydrogen_1s_2s_transition` (4×10⁻¹⁵ precision)
- `lamb_shift_qed_precision` (bound-state QED, proton radius)

**Particle physics — flavor and CP (10):**
- `muon_to_electron_gamma_meg` (Br < 4.2×10⁻¹³)
- `mu_e_conversion_sindrum` (R < 7×10⁻¹³)
- `r_k_lepton_universality` (LHCb 2022, now SM-consistent)
- `r_d_star_charged_current` (HFLAV, ~3.3σ above SM)
- `b_s_mixing_phase` (φ_s consistent with SM)
- `epsilon_prime_over_epsilon_kaon` (direct CPV in K → ππ)
- `kaon_rare_decays_kpi_nu_nu` (NA62 + KOTO)
- `cabibbo_angle_anomaly` (first-row CKM unitarity ~3σ)
- `neutron_electric_dipole_moment` (PSI 2020)
- `electron_edm_jila` (JILA 2023)

**Particle physics — weak / EW precision (3):**
- `neutron_lifetime_beam_vs_bottle` (~4σ tension)
- `atomic_parity_violation_cesium` (Q_W(Cs))
- `electroweak_oblique_s_t_u` (post-2024 EW fit)

**Forbidden phenomena (3):**
- `proton_decay_lifetime` (Super-K)
- `cabibbo_angle_anomaly` (also a tension/anomaly entry)
- `neutron_electric_dipole_moment` (also above)

**Lorentz / CPT (4):**
- `lorentz_invariance_photon` (SME, GRB dispersion)
- `vacuum_birefringence_polarization` (SME polarization)
- `cpt_kaon_mass_difference` (10⁻¹⁹ level)
- `cpt_antihydrogen_1s_2s` (ALPHA matching to H)

**Cosmology (7):**
- `bbn_light_element_abundances`
- `cmb_acoustic_peak_structure`
- `cmb_blackbody_firas` (μ, y distortions)
- `sum_neutrino_masses_cosmology` (Σm_ν < 0.072 eV)
- `primordial_gw_tensor_to_scalar_ratio` (r < 0.036)
- `large_scale_structure_galaxy_power_spectrum` (DESI, BOSS)
- `lyman_alpha_forest_small_scale_power` (WDM > 5.3 keV)

**Dark matter (5):**
- `dm_direct_detection_lz` (LZ + XENONnT)
- `dm_indirect_fermi_lat_dwarfs` (annihilation bounds)
- `axion_haloscope_admx` (QCD axion + ALP photon coupling)
- `sidm_self_interaction_clusters` (σ/m < 0.47 cm²/g)
- `primordial_black_holes_microlensing` (PBH abundance)

**Strong interactions / QCD (3):**
- `strong_cp_theta_qcd` (θ_QCD < 10⁻¹⁰)
- `lattice_qcd_hadron_spectrum` (BMW)
- `nucleon_axial_charge_g_a` (CalLat lattice + PERKEO III)

**Astrophysics (3):**
- `helioseismology_solar_interior` (sound-speed profile)
- `neutron_star_mass_radius` (NICER + GW170817)
- `pulsar_timing_array_gw_background` (NANOGrav 15 yr)

**Precision constants (1):**
- `alpha_variation_atomic_clocks` (α̇/α < 2×10⁻¹⁸/yr)

**Meta (1):**
- `address_open_tensions` (links into `data/`)

**Pattern compression (3, new):**
- `quark_mass_fn_compression` (Froggatt-Nielsen ε^q ansatz vs PDG quark masses)
- `ckm_wolfenstein_lambda_hierarchy` (CKM organised in powers of λ ≈ 0.225)
- `neutrino_mass_scale_seesaw` (m_ν ~ y_ν² v² / M_R compression)

**Puzzles (9, new layer):**
- `cosmological_constant_smallness`, `gauge_hierarchy_problem`,
  `strong_cp_problem`, `flavor_mass_hierarchy`, `ckm_mixing_pattern`,
  `neutrino_mass_smallness`, `baryon_asymmetry`, `dark_matter_identity`,
  `gauge_coupling_unification`

**Puzzles (10, new layer):**
- `cosmological_constant_smallness`, `gauge_hierarchy_problem`,
  `strong_cp_problem`, `flavor_mass_hierarchy`, `ckm_mixing_pattern`,
  `neutrino_mass_smallness`, `baryon_asymmetry`, `dark_matter_identity`,
  `gauge_coupling_unification`, `inflation_initial_conditions`

**Mechanisms (53, new layer):**
- Strong-CP: `peccei_quinn_axion`, `nelson_barr`,
  `babu_mohapatra_parity`
- Flavor: `froggatt_nielsen`, `modular_flavor_symmetry`,
  `a4_family_symmetry`, `partial_compositeness`,
  `minimal_flavor_violation`
- Neutrino mass: `seesaw_type_i`, `seesaw_type_ii`, `seesaw_type_iii`,
  `inverse_seesaw`, `zee_radiative_neutrino_mass`,
  `scotogenic_neutrino_dm`
- Baryogenesis: `leptogenesis`, `electroweak_baryogenesis`,
  `affleck_dine_baryogenesis`, `gut_baryogenesis`
- Hierarchy: `mssm`, `twin_higgs`, `relaxion`, `composite_higgs`,
  `large_extra_dimensions_add`, `warped_extra_dimensions_rs`,
  `nnaturalness`, `coleman_weinberg_radiative`, `little_higgs`,
  `technicolor`
- SUSY mediation: `anomaly_mediated_susy_breaking`,
  `gauge_mediated_susy_breaking`
- Dark matter: `wimp_thermal_freezeout`, `asymmetric_dark_matter`,
  `ultralight_scalar_dm`, `sterile_neutrino_dm`,
  `higgs_portal_scalar_dm`, `mirror_dark_matter`,
  `wimpless_dark_matter`, `kaluza_klein_dark_matter`,
  `dark_photon_portal`, `super_wimp_gravitino`
- Inflation: `starobinsky_inflation`, `higgs_inflation`
- Unification / UV completion: `su5_minimal_gut`, `so10_gut`,
  `pati_salam`, `heterotic_string_compactification`
- Cosmological constant / modified gravity: `anthropic_landscape`,
  `sequestering`, `unimodular_gravity`, `quintessence`,
  `dgp_braneworld`, `asymptotic_safety_gravity`,
  `holographic_dark_energy`

All citations verified against primary literature via direct
WebSearch lookup against arXiv / journal abstracts.

### Recently populated

Previous batch (9 entries):
- `katrin_neutrino_mass` (m_ν_e < 0.45 eV)
- `neutrinoless_double_beta_decay` (KamLAND-Zen <m_ββ>)
- `lithium_problem_bbn` (~3σ ⁷Li/H discrepancy)
- `proton_radius_muonic_hydrogen` (Antognini 2013 + post-2017 e-H)
- `neutrino_oscillation_pmns` (NuFIT 5.2 mass splittings + angles)
- `cmb_large_scale_anomalies` (low-ℓ, axis of evil, hemispherical, Cold Spot)
- `higgs_couplings_lhc` (κ_W, κ_Z, κ_t, κ_b, κ_τ)
- `dark_photon_kinetic_mixing` (BaBar, NA64; ε vs m_A')
- `lorentz_electron_sme` (electron-sector SME bounds)

Latest batch (9 entries; previously listed as future high-priority):
- `muon_edm_bnl` (BNL E821 |d_μ| < 1.8×10⁻¹⁹ e cm; PSI muEDM target)
- `casimir_force_precision` (Yukawa bounds at sub-μm to 8 μm)
- `n_eff_combined_cmb_bbn` (CMB+BBN joint, |ΔN_eff| < 0.3)
- `tau_lepton_universality` (HFLAV g_τ/g_l ratios at 0.1% level)
- `b_to_s_gamma_inclusive` (NNLO SM vs world-avg, |ΔC_7| < 0.05)
- `meson_mixing_d_k` (Δm_K, ε_K, x_D, y_D — generic FCNC reach 10⁵ TeV)
- `muon_anomalous_magnetic_moment` (FNAL+BNL world avg vs WP2020 / lattice SM)
- `cosmic_ray_gzk_cutoff` (UHECR suppression; |δ_p − δ_π| < 6×10⁻²³)
- `solar_neutrino_msw` (Borexino + SNO MSW-LMA, P_ee(E))

### Future high-priority additions

The original high-priority list is now fully populated. Candidates for
the next batch (none yet written; pull requests welcome):

- `b_to_k_nu_nu_belle2` — Belle II 2.7σ excess in B⁺ → K⁺ νν̄
- `atmospheric_neutrino_oscillation_super_k` — independent measurement
  of θ₂₃, |Δm²₃₁| from atmospheric neutrinos
- `pion_beta_decay_vud` — V_ud from π⁺ → π⁰ e⁺ ν, complementary to
  superallowed nuclear β decay (cabibbo_angle_anomaly)
- `bbn_deuterium_precision` — D/H from Cooke et al. as a clean probe
  of Ω_b h² (currently folded into bbn_light_element_abundances)
- `direct_w_boson_mass_measurement` — separate from
  `electroweak_oblique_s_t_u`, focusing on the m_W observable itself
  and the CDF / ATLAS / CMS / LHCb tension landscape (currently in
  data/w_boson_mass.json)
- `inflationary_n_s_alpha_s` — scalar spectral index and running from
  Planck + ACT (currently in cmb_acoustic_peak_structure)
- `super_k_atmospheric_lorentz` — atmospheric-neutrino LIV bounds
  complementary to `lorentz_electron_sme`

## Future research questions

These are deferred research-grade investigations that the catalog enables
but does not itself perform. Listed for orientation, not as near-term
work items.

- **Graph mining for non-obvious alignments.** Once the mechanism
  catalog is sufficiently dense (~50+ entries across all puzzles),
  search for the smallest mechanism subset that closes the most
  puzzles, and identify recurring `structural_features` combinations
  among high-degree mechanisms. The goal is to surface latent
  unification clues that no single subfield would notice. Speculative;
  success would mean re-discovering known clusters (SUSY-GUT,
  axion+seesaw+leptogenesis) plus identifying at least one
  non-obvious composition.
- **Cross-mechanism conflict detection.** Beyond the explicit
  `excludes` field, detect implicit conflicts via shared field content,
  scale clashes, or contradictory predictions on the same benchmark.
- **Bayesian compression weighting.** Replace the simple
  puzzles_closed / parameters_introduced ratio with a posterior
  weighting that accounts for confidence labels and benchmark coverage.

## How to contribute

For each prospective entry:
1. Identify the primary literature (DOI / arXiv).
2. Choose the canonical parameterization for the procedural block.
3. Write the JSON entry following the existing format.
4. Run `python scripts/validate.py`.

Pull requests welcome; small entries are fine — better to land
something with one solid primary reference than to wait for a
comprehensive review.

## Source policy

Every entry in `data/` and `benchmarks/` must include at least one
primary-literature reference with either an arXiv ID or a DOI. We do
not cite review articles unless they originate or definitively settle
the result. If a number cannot be sourced to a published paper,
preprint, or experimental collaboration data release, it does not
belong in the catalog.
