#!bin/sh
n_atom=3
sparse="    "
file="result_force.log"
:> result_force.log
#source ~/lustre2/2_liangxinyuan/01_lab/00_tools/conda_init.sh
for ((i=1;i<=13;i++))
do
    energy=$(echo "(100+10*($i-1))" | bc)
    energy_2=$(echo "(100+10*$i)" | bc )
    echo -n "$energy" >> $file
    echo  -n "$sparse" >> $file
    python cal_force.py $n_atom  ecutwfc_$energy ecutwfc_230 >> $file
    echo "" >> $file
    echo "$i done"
done
