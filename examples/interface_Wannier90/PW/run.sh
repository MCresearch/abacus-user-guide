export W90=/home/saber/work/0_compilers/4_qe/wannier90/wannier90-3.1.0/wannier90.x
export ABACUS=/home/saber/work/4_abacus/abacus-up-to-date/abacus-develop/build/abacus
export NP=12

mpirun -np $NP $W90 -pp diamond.win 
cp INPUT-scf INPUT
cp KPT-scf KPT
mpirun -np $NP $ABACUS >> scf.out 
cp INPUT-nscf INPUT
cp KPT-nscf KPT
mpirun -np $NP $ABACUS >> nscf.out
cp OUT.ABACUS/diamond.amn OUT.ABACUS/diamond.mmn OUT.ABACUS/diamond.eig OUT.ABACUS/UNK* .
mpirun -np $NP $W90 diamond.win
