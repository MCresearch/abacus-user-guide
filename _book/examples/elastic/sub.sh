#!/bin/bash
#SBATCH -p master
#SBATCH -J lcao-elas
#SBATCH -n 6

intel
mpirun -n 6 abacus | tee abacus.out