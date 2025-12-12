#!/bin/bash

TOTAL_TASKS=4
TASKS_PER_BATCH=4
TOTAL_BATCHES=$((TOTAL_TASKS / TASKS_PER_BATCH))
WAIT_TIME=600  # s


files=($(ls | grep STRU-))


echo "generate KPT"
cat > KPT << EOF
K_POINTS
0
Gamma
1 1 1 0 0 0
EOF

echo "generate cal.sh"
cat > cal.sh << EOF
#!/bin/bash
#SBATCH -J ABACUS
#SBATCH -p cn-large
#SBATCH -N 1
#SBATCH --no-requeue
#SBATCH -A mhchen_cg2
#SBATCH --qos=mhchenq
#SBATCH -c 4

source /lustre3/mhchen_pkuhpc/mhchen_cls/ly/liuyu_source.sh
export OMP_NUM_THREADS=4
mpirun -np 1 abacus
EOF


for ((batch=1; batch<=TOTAL_BATCHES; batch++)); do
    echo "---------------------------"
    echo "Current batch: $batch"
    echo "---------------------------"
    
    for ((task=1; task<=TASKS_PER_BATCH; task++)); do
        index=$((task -1 + (batch-1)*TASKS_PER_BATCH))
        stru_file="${files[index]}"

        mkdir job_$index
        cd job_$index

        echo "generate INPUT"
        cat > INPUT << EOF
INPUT_PARAMETERS
#Parameters (1.General)
suffix                 phonon
calculation            scf
symmetry               1
nspin                  1
dft_functional         pbe
stru_file              ../$stru_file
kpoint_file            ../KPT

#Parameters (2.Iteration)
ecutwfc                100
scf_thr                1e-9
scf_nmax               100

#Parameters (3.Basis)
basis_type             lcao
ks_solver              genelpa
gamma_only             1

#Parameters (4.Smearing)
smearing_method        gaussian
smearing_sigma         0.001

#Parameters (5.Mixing)
mixing_type            broyden
mixing_beta            0.4

cal_force              1
cal_stress             1
EOF
        echo "submit job: $index"
        sbatch ../cal.sh
        cd ..
    done
    
    # wait WAIT_TIME if not the last batch
    if [ $batch -lt $TOTAL_BATCHES ]; then
        echo "wait ${WAIT_TIME} s..."
        sleep $WAIT_TIME
    fi
    echo "---------------------------"
done

echo "All jobs submitted!"
echo "---------------------------"
