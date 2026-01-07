np=$1
abacus=$2
mpirun -n $np $abacus | tee -a abacus.out


