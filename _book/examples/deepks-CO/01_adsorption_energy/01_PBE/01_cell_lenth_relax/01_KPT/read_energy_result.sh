#!/bin/sh
sparse="    "
file="../result_energy.log"
:> result_energy.log
echo  "kpoints${sparse}energy${sparse}energy_difference" >> result_energy.log
ks=(1 2 4 8 12 16 24 32)
previous_energy=0
first_iteration=true

for k in ${ks[@]}
do
    if [ ! -d k_$k ]; then
        #echo "k_$k not exist"
        continue
    fi
    cd k_$k
    echo -n "$k" >> $file
    echo -n "$sparse" >> $file
    current_energy=$(grep ' !FINAL_ETOT_IS .* eV' OUT.ABACUS/running_scf.log | awk '{printf $2}')
    echo -n "$current_energy" >> $file

    if [ "$first_iteration" = true ]; then
        echo "" >> $file
        first_iteration=false
    else
        energy_diff=$(echo "$current_energy - $previous_energy" | bc)
        echo -n "$sparse" >> $file
        echo "$energy_diff" >> $file
    fi

    previous_energy=$current_energy
    cd ..
    echo "$k done"
done