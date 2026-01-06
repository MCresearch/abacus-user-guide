dirs=(`ls -d 0*`)
for dir in ${dirs[@]}
do
    if [ $dir == "00_template" ];then
        continue
    fi
    result_dir=$dir
    # 使用 grep 查找字符串
    if ! grep -q "Relaxation is converged!" ${result_dir}/OUT.ABACUS/running_relax.log; then
        echo "Error: ${dir} relaxation not converged"
        continue
    fi
    if [ -f ${result_dir}/abacus.out ];then
        last_ge_line=$(grep -E "GE[0-9]+" ${result_dir}/abacus.out | tail -n 1)
        energy=$(echo "$last_ge_line" | awk '{print $2}')
        echo "$dir $energy"
    fi
done
