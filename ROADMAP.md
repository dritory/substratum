# Roadmap

This file tracks the constraint inventory we still need to populate. The
goal is a procedural benchmark set comprehensive enough that any
candidate unified framework can be evaluated against it.

## Conventions

- A constraint is **listed** here when we have identified the canonical
  parameterization and the primary literature.
- A constraint is **populated** when it has a JSON entry in `benchmarks/`
  that validates against `schema/benchmark.schema.json` and includes a
  `procedural` block.
- We populate from highest-impact downward — meaning constraints that
  kill the most candidate frameworks first.

## Status

### Populated (15 entries)

Gravity:
- `recover_general_relativity` (PPN, PPK, GW waveform)
- `graviton_speed_gw170817`
- `equivalence_principle_microscope`
- `inverse_square_law_short_distance`
- `antihydrogen_gravity_alpha_g`
- `bullet_cluster_lensing_offset`

Particle / EFT:
- `recover_standard_model_precision` (SMEFT)
- `lorentz_invariance_photon` (SME)
- `proton_decay_lifetime`
- `neutron_electric_dipole_moment`
- `electron_edm_jila`

Cosmology:
- `bbn_light_element_abundances`
- `cmb_acoustic_peak_structure`

Precision:
- `alpha_variation_atomic_clocks`

Meta:
- `address_open_tensions` (links into `data/`)

### Listed but not yet populated

#### Gravity (extending PPN coverage)
- `nordtvedt_parameter_strong_ep` — strong equivalence principle from
  lunar laser ranging (eta_N < 4.4 × 10⁻⁴) and binary pulsar PSR J0337+1715
- `frame_dragging_gravity_probe_b` — Lense-Thirring precession measurement
- `binary_pulsar_psr_b1913_16` — orbital decay matches GR quadrupole
  formula to ~0.1%
- `binary_pulsar_psr_j0737_3039` (double pulsar) — multi-PPK precision tests
- `graviton_mass_gw_dispersion` — m_g < 1.27 × 10⁻²³ eV/c² (LIGO/Virgo
  GWTC-3)
- `gw_polarization_modes` — only +,× modes detected; constrains scalar,
  vector, breathing modes from alternative theories of gravity

#### Particle physics (precision and forbidden)
- `electron_g_minus_2_precision` — a_e to 13 digits; cleanest QED test
- `hydrogen_1s_2s_transition` — most precisely measured atomic transition
- `lamb_shift_qed_precision` — direct test of QED radiative corrections
- `muon_to_electron_gamma_meg` — Br(μ → eγ) < 4.2 × 10⁻¹³
- `mu_e_conversion_mu2e` — upcoming μ → e conversion in nuclei
- `r_k_lepton_universality_b_to_sll` — R(K), R(K*) ratios
- `r_d_star_charged_current` — R(D), R(D*) ratios
- `b_s_mixing_phase` — phi_s consistent with SM
- `epsilon_prime_over_epsilon` — direct CP violation in K → ππ
- `kaon_rare_decays_kotos_na62` — K → π ν ν̄ branching ratios
- `cabibbo_angle_anomaly` — first-row CKM unitarity tension
- `neutron_lifetime_beam_vs_bottle` — ~4σ tension between methods
- `atomic_parity_violation_cesium` — weak charge of cesium
- `electroweak_oblique_s_t_u` — global EW fit beyond just m_W

#### Lorentz / CPT (extending the photon entry)
- `vacuum_birefringence_polarization` — astrophysical polarization
  bounds on (k_AF) coefficients
- `cpt_kaon_mass_difference` — |m_K0 − m_K̄0|/m_K0 < 10⁻¹⁸
- `cpt_antihydrogen_1s_2s` — antihydrogen vs hydrogen transition match
- `lorentz_electron_sme` — electron-sector SME bounds

#### Cosmology (extending CMB/BBN)
- `sum_neutrino_masses_cosmology` — Σm_ν < 0.12 eV (Planck+BAO)
- `n_eff_cmb_bbn` — joint CMB+BBN bound on relativistic species
- `primordial_gravitational_waves_r` — tensor-to-scalar ratio r < 0.036
  (BICEP/Keck 2021)
- `cmb_isotropy_isotropic_blackbody` — large-scale isotropy and
  blackbody spectrum (FIRAS)
- `large_scale_structure_galaxy_power_spectrum` — BOSS / DESI / Euclid
  full-shape constraints
- `lyman_alpha_forest_small_scale_power` — small-scale matter power
  cutoff; bounds warm/fuzzy DM

#### Dark matter / dark sector
- `dm_direct_detection_lz_xenonnt` — WIMP-nucleon cross section limits
- `dm_indirect_fermi_lat` — galactic-center gamma-ray bounds on DM
  annihilation
- `axion_haloscope_admx` — QCD axion couplings to photons
- `sidm_self_interaction_cluster_mergers` — σ/m < 1 cm²/g
- `primordial_black_holes_microlensing` — PBH dark-matter fraction
  from OGLE / HSC / Subaru

#### Strong interactions / QCD
- `strong_cp_theta_qcd` — θ_QCD < 10⁻¹⁰
- `lattice_qcd_hadron_spectrum` — meson and baryon masses from first
  principles
- `nucleon_axial_charge_g_a` — gA from lattice agrees with experiment

#### Astrophysics
- `helioseismology_solar_interior` — radial sound speed profile of the
  Sun, constrains modified gravity in dense plasma
- `neutron_star_mass_radius` — TOV-equation tests of strong-field
  gravity from NICER and GW170817
- `pulsar_timing_array_gw_background` — NANOGrav / EPTA / PPTA detection
  of nano-Hz gravitational-wave background

## How to contribute

For each listed-but-not-populated entry, the work is:

1. Identify the primary literature (DOI / arXiv).
2. Choose the canonical parameterization.
3. Write the JSON entry following the existing format.
4. Validate with `python scripts/validate.py`.

Pull requests welcome; small entries are fine — better to land
something than to wait for perfection.
