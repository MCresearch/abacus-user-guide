import numpy as np
import sys
import glob
import os

# 检查是否提供了命令行参数
if len(sys.argv) > 1:
    try:
        e_fermi = float(sys.argv[1])  # 将e_fermi转换为浮点数
    except ValueError:
        print("Usage: python plot_band.py e_fermi")
        e_fermi = 0.0  # 如果转换失败，将e_fermi设置为0.0
else:
    e_fermi = 0.0  # 如果没有提供命令行参数，将e_fermi设置为0.0

# 读取KPT文件
kpt_data = np.loadtxt('KPT', skiprows=3)  # 假设KPT文件的前3行是标题行，需要跳过
kpt_indice = np.delete(kpt_data[:, 3].astype(int), -1)
kpt_indice = np.insert(kpt_indice, 0, 1)  # 删除最后一个元素，并在第一个位置插入1
print(kpt_indice)
kpt_indices = np.cumsum(kpt_indice.astype(int))
print(kpt_indices)

# 获取所有BANDS_*.dat文件的路径
band_files = glob.glob('OUT.*/BANDS_*.dat')

for band_file in band_files:
    data = np.loadtxt(band_file)
    id = os.path.basename(band_file) # 获取文件名
    print('Processing ' + id + '...')

    for idx, ii in enumerate(kpt_indice):
        if ii == 1 and idx != 0:
            data[kpt_indices[idx]-1 : , 1] -=  data[kpt_indices[idx]-1, 1] - data[kpt_indices[idx]-2, 1]
            kpt_indices_modify = np.array([kpt_indices[i] for i in range(len(kpt_indices)) if i != idx])
            # kpt_indices_del = np.delete(kpt_indices, idx)
            print(kpt_indices_modify)
    # 使用KPT文件第四列的数据作为索引来查找data第二列对应行的数据
    selected_data = data[kpt_indices_modify-1, 1]
    # print(selected_data)

    # 在文件的开头添加新内容
    plot_file = 'plot_' + id
    with open(plot_file, 'w+') as f:
        f.write('# ' + ' '.join(map(str, selected_data)) + '\n')

    merged_data = []  # 创建一个空列表来保存所有合并后的数据

    # 循环读取第三列到最后一列，并将每一列与第二列合并
    for i in range(2, data.shape[1]):
        data[:, i] -= e_fermi
        merged = np.column_stack((data[:, 1], data[:, i]))
        with open(plot_file, 'a') as f:
            np.savetxt(f, merged, fmt='%.6f')
            f.write('\n')
