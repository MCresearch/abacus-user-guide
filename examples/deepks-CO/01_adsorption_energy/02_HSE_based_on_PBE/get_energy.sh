dirs=(`ls -d 0*`) 

function check_converge()
{
    # 定义文件路径和要查找的字符串
    file_path=abacus.out
    search_string="Updating EXX and rerun SCF"
    last_occurrence_string="Atomic-orbital Based Ab-initio Computation at UStc"

    # 查找最后一个特定字符串的行号
    last_occurrence_line=$(grep -n "$last_occurrence_string" "$file_path" | tail -n 1 | cut -d: -f1)

    # 如果没有找到最后一个特定字符串，则报错并退出
    if [ -z "$last_occurrence_line" ]; then
        echo "Error: '$last_occurrence_string' not found in $file_path"
        exit 1
    fi

    # 查找最后一个特定字符串之后出现的目标字符串的次数
    occurrences=$(tail -n +$((last_occurrence_line + 1)) "$file_path" | grep -c "$search_string")

    return $occurrences

}

for dir in ${dirs[@]}
do
    if [ $dir == "00_template" ];then
        continue
    fi
    cd ${dir}
    check_converge
    # 如果出现次数达到或超过 100 次，则没有收敛
    if [ "$?" -ge 100 ]; then
        echo "Error: dir not converge!"
        continue
    fi
    if [ -f abacus.out ];then
        last_ge_line=$(grep -E "GE[0-9]+" abacus.out | tail -n 1)
        energy=$(echo "$last_ge_line" | awk '{print $2}')
        echo "$dir $energy"
    fi
    cd ../
done
