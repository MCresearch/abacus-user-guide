#!/bin/bash
export OMP_NUM_THREADS=4
export ABACUS=abacus
export CANDELA=candela
cp INPUT_ABACUS INPUT
mpirun -n 4 $ABACUS
cp INPUT_CANDELA INPUT
mpirun -n 4 $CANDELA
rm INPUT
