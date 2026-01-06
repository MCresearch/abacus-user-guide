name=$1
adsorbs=("top" "hollow" "hcp" "bridge")

for adsorb in ${adsorbs[@]}; do
    file_name=${name}_slab_CO_${adsorb}
    file=${file_name}_relax.STRU
    cp ${file_name}.STRU $file
    #先让所有原子都不动
    sed -i  '24,73s/1 1 1/ 0 0 0/' $file
    for i in {0..7}; do
        #允许最表层原子移动
        sed -i "$((28 + 5 * i)),$((28 + 5 * i))s/0 0 0$/1 1 1/g" $file
        #允许次表层原子移动
        sed -i "$((27 + 5 * i)),$((27 + 5 * i))s/0 0 0$/1 1 1/g" $file
    done
    for i in {0..1};do
        #允许CO原子移动
        sed -i "$((67 + i)),$((67 + i))s/0 0 0$/1 1 1/g" $file
        sed -i "$((72 + i)),$((72 + i))s/0 0 0$/1 1 1/g" $file
    done
done
