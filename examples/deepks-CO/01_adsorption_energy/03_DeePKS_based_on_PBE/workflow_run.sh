np=$1
abacus=$2

now_dir=(`pwd`)

cd ../01_PBE
ref_dir=(`pwd`)
dirs=(`ls -d 0*/`) 
cd $now_dir

for dir in ${dirs[@]}
do
    dir=${dir%/}  # 去掉目录名末尾的斜杠
    if [ $dir == "01_cell_lenth_relax" ];then
        continue
    fi
    if [ ! -d $dir ]; then
        mkdir $dir
    fi
    cp 00_template/* $dir
    cd $dir
    cp_path=${ref_dir}/${dir}
    if [ $dir == "02_slab" ];then
        cp_path=${ref_dir}/${dir}/01_relax
    fi
    cp ${cp_path}/OUT.ABACUS/STRU_ION_D ./STRU
    cp ${cp_path}/KPT ./
    #add jle.orb
    if ! grep -q "NUMERICAL_DESCRIPTOR" STRU; then
        echo -e "\nNUMERICAL_DESCRIPTOR\njle.orb\n" >> STRU
    fi
    bash run.sh $np $abacus
    cd ../
done

