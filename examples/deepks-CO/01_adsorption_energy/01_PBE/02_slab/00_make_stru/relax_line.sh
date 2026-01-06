name=$1
file=${name}_slab_relax.STRU
cp ${name}_slab.STRU $file
#先让所有原子都不动
sed -i  '20,59s/1 1 1/ 0 0 0/' $file
for i in {0..7}; do
    #允许最表层原子移动
    sed -i "$((24 + 5 * i)),$((24 + 5 * i))s/0 0 0/1 1 1/g" $file
    #允许次表层原子移动
    sed -i "$((23 + 5 * i)),$((23 + 5 * i))s/0 0 0/1 1 1/g" $file
done