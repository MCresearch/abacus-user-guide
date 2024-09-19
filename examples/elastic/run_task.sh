#!/bin/bash
for i in task.*
do
cd ./$i
pwd
# 超算环境注意修改sub.sh中的内容
sbatch ../sub.sh
# 或者直接运行abacus
# mpirun -n 4 abacus
cd ../
done