##!bin/sh
abacus=$1
ks=(1 2 4 8 12 16 24)
for ((i=5;i<${#ks[@]};i++))
do
    k=${ks[$i]}
    if [ ! -d k_$k ];then
        mkdir k_$k
    fi
    cd k_$k
    pwd
    cp ../00_template/* .
    sed -i "s/1 1 1/$k $k $k/g" KPT
    mpirun -n 8 $abacus >> abacus.out
    cd ..
    echo "k_$k done"
done
wait
echo "all work done"