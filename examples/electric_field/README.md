# Examples for Electric Field

## Descriptions

- Folders `1_unspin_scf` and `2_unspin_band` correspond to the SCF and band structure calculations for the spin-unpolarized case with no external electric field.
- Folders `3_spin_scf` and `4_spin_band` correspond to the SCF and band structure calculations for the spin-polarized case with no external electric field.
- Folders `5_spin_elec_scf` and `6_spin_elec_band` correspond to the SCF and band structure calculations for the spin-polarized case with 0.1 V/$\mathrm{\AA}$ external electric field.

## Notes

The `SPIN1_CHG.cube` and `SPIN2_CHG.cube` (if exists) obtained from SCF calculations should be copyed into the work directory of the band structure calculation to restart NSCF calculations.