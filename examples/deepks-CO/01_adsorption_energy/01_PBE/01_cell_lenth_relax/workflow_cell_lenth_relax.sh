abacus=$1
element="Rh"

cd 01_KPT
cp ../STRU_initial 00_template/STRU
bash run.sh $abacus #默认只跑16和32
bash read_energy_result.sh
energy_diff=$(tail -n 1 result_energy.log | awk '{print $NF}')
if [ $(echo "$energy_diff > 0.001" | bc) -eq 1 ]; then
    echo "energy difference is larger than 0.0001 eV, stop"
    exit 0
else
    echo "energy difference is less than 0.0001 eV, go on"
fi

cd ../02_cell_relax
cp ../STRU_initial STRU
#将收敛的KPT拷贝过来
bash run.sh 12 $abacus
cd ../
cp 02_cell_relax/OUT.ABACUS/STRU_ION_D ./STRU #完成cell relax之后的构型

