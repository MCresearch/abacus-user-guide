# MD examples of the ABACUS program.

By setting `calculation` to be `md`, ABACUS currently provides several different MD evolution methods, which is specified by keyword `md_type` in the `INPUT` file:

  - fire: a MD-based relaxation algorithm
  - nve: NVE ensemble with velocity Verlet algorithm
  - nvt: NVT ensemble
  - npt: Nose-Hoover style NPT ensemble
  - langevin: NVT ensemble with Langevin thermostat
  - msst: MSST method

When `md_type` is set to nvt, `md_thermostat` is used to specify the temperature control method used in NVT ensemble.

  - nhc: Nose-Hoover chain
  - anderson: Anderson thermostat
  - berendsen: Berendsen thermostat
  - rescaling: velocity Rescaling method 1
  - rescale_v: velocity Rescaling method 2

When `md_type` is set to npt, `md_pmode` is used to specify the cell fluctuation mode in NPT ensemble based on the Nose-Hoover style non-Hamiltonian equations of motion.

  - iso: isotropic cell fluctuations
  - aniso: anisotropic cell fluctuations
  - tri: non-orthogonal (triclinic) simulation box

Furthermore, ABACUS also provides a [list of keywords](http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#molecular-dynamics) to control relevant parmeters used in MD simulations.

To employ CMD calculations, `esolver_type` should be set to be `lj` or `dp`.
If DP model is selected, the filename of DP model is specified by keyword `pot_file`.

The MD output information will be written into the file `MD_dump`， in which the atomic forces, atomic velocities, and lattice virial are controlled by keyword `dump_force`, `dump_vel`, and `dump_virial`, respectively.

Note:
  - When doing md calculations, turn off `symmetry`.
  - If the output file is too large, the `out_level` option is suggested to be `m`.
  - Different INPUT files correspond to different MD types.


