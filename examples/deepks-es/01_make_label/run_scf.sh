abacus="abacus"
for (( i=0;i<2;i++))
do
    group=group.0$i
    cd $group
    cd ABACUS
    for (( j=0;j<2;j++))
    do
        sub_group=$j
        cd $sub_group
        OMP_NUM_THREADS=8 mpirun -n 3 $abacus > log.txt &
        cd ../
    done
    cd ../../
    wait
done