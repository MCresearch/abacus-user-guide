# PW examples of the ABACUS program

This is a modified version of ABACUS PW examples(pw/).

Main Differences from the first test set (pw/):

1. **FFT grids** are manually set to powers of 2 (≥ the auto‑generated sizes) in all cases.
2. **`010_216Si`** uses a reduced number of bands (`nbands`) and a lower energy cutoff (`ecutwfc`).
3. **Kohn‑Sham solvers**(`ks_solver`) are tested separately: this set provides two parallel directories,
   `pw2/cg` (using `cg`) and `pw2/ds` (using `dav_subspace`), whereas the first set only
   used `cg`.
4. **Pseudopotentials** are switched to the `pseudo-dojo v0.5` standard (NC SR ONCVPSP v0.5,
   PBE, standard accuracy, `.upf`).

By setting `basis_type` to `pw`, ABACUS performs calculations using the plane-wave basis set. The core of these calculations is the Self-Consistent Field (SCF) iteration, which is controlled by several key parameters in the `INPUT` file.

The following keywords are essential for governing the convergence and performance of the SCF process:

- **scf_nmax**: The maximum number of SCF iterations.
- **scf_thr**: The convergence threshold for the total energy or density (in Rydberg).
- **ks_solver**: Specifies the algorithm used to solve the Kohn-Sham equations. The following options are available for the `pw` basis set:
  - `cg`: Conjugate Gradient method.
  - `dav_subspace`: Davidson subspace method without explicit orthogonalization; this method is recommended for high efficiency. For this method, `pw_diag_ndim` can be set to 2.
  - `dav`: The Davidson algorithm.
  - `bpcg`: The BPCG method (block-parallel Conjugate Gradient), which typically exhibits higher acceleration in a GPU environment.
- **mixing_type**: Defines the charge density mixing method to accelerate convergence.

For PW calculations, the precision is largely determined by the plane-wave expansion, which is controlled by:

- **ecutwfc**: The energy cutoff for the wavefunctions (in Rydberg).
- **pseudo_dir**: The directory where pseudopotential files (usually in `.upf` format) are stored.

For metallic systems, `smearing_method` and `smearing_sigma` are used to handle the Fermi surface:

- **smearing_method**: Options include `gauss` (Gaussian), `mp` (Methfessel-Paxton), `fixed` (for insulators), etc.
- **smearing_sigma**: The broadening width (in Rydberg).

For a detailed description of INPUT parameters, consult the [Full List of INPUT Keywords](https://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html).

### Notes

- **Symmetry**: For PW calculations, setting `symmetry` to `1` can significantly reduce the number of k-points and accelerate the calculation.
- **K-points**: Ensure the `KPT` file is appropriately configured for the Brillouin zone sampling.
- **Output**: The results of the SCF convergence and final energies are primarily written to the `running_scf.log` file in the `OUT.${suffix}` directory.