# Roadmap

This file tracks the constraint inventory we have populated and what
remains. The goal is a procedural benchmark set comprehensive enough
that any candidate unified-physics framework can be evaluated against
it.

## Conventions

- A constraint is **populated** when it has a JSON entry in
  `benchmarks/` that validates against `schema/benchmark.schema.json`,
  cites primary literature with arXiv/DOI, and (where applicable)
  includes a `procedural` block with the canonical parameterization.
- Every entry must be backed by primary references. No textbook-only
  citations.

## Status

### Populated (44 benchmark entries, 5 data entries)

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

### Future high-priority additions

- `n_eff_combined_cmb_bbn` — combined N_eff bound from CMB damping tail
  + BBN; finer than per-experiment entries
- `lorentz_electron_sme` — full electron-sector SME coefficient table
- `cmb_isotropy_dipole_anomalies` — large-scale anomalies (low-l, axis
  of evil, hemispherical asymmetry)
- `katrin_neutrino_mass` — direct kinematic m(ν_e) bound
- `0nubb_neutrino_majorana` — neutrinoless double-beta-decay limits
- `proton_radius_muonic_hydrogen` — separate entry for the Pohl-et-al.
  measurement (currently mentioned in `lamb_shift_qed_precision`)
- `lithium_problem_bbn` — the ~3σ ⁷Li/H discrepancy (currently noted
  inside `bbn_light_element_abundances`)

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
