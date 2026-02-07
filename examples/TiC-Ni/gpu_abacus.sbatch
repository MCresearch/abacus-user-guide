#!/bin/bash
#SBATCH --job-name=ABACUS
#SBATCH --partition=4V100PX
#SBATCH --nodes=1
#SBATCH --ntasks=1          # Nodes * GPUs-per-node * Ranks-per-GPU
#SBATCH --gpus-per-node=1   # Specify the GPUs-per-node
#SBATCH --qos=improper-gpu     # Depending on your needs [Priority: rush-4gpu = rush-8gpu > improper-gpu > huge-gpu]

# ⚠ DO NOT modify [CUDA-MPS] and [Rank-Map] settings unless you know what you are doing.
source /opt/sai_config/mps_mapping.d/${SLURM_JOB_PARTITION}.bash

# Below are executing commands
nvidia-smi dmon -s pucvmte -o T > nvdmon_job-$SLURM_JOB_ID.log &
module load abacus/LTSv3.10.1-sm70-auto
#mpirun -np $SLURM_NTASKS -map-by $MAP_OPT -mca coll_hcoll_enable 0 abacus
abacus

# Must explicitly exit
exit
