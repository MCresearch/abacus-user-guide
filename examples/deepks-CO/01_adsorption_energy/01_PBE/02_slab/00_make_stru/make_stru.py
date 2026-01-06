from ase.build import bulk, surface
from ase.io import write
from ase.visualize import view
import sys
import dpdata

def create_fcc_111_surface(element, fcc_lattice_constant, n_layer, vacuum, repetitions, output_file):
    # 创建具有特定晶胞边长的 FCC 结构
    # 注意！给的a应该是conventioanl cell的a，而不是primitive cell的a！！！
    fcc_structure = bulk(element, 'fcc', a=fcc_lattice_constant)
    print(fcc_structure)

    # 切取 (111) 表面，层数为n_layer
    fcc_111_surface = surface(fcc_structure, (1, 1, 1), layers=n_layer)
    print(fcc_111_surface)

    # 添加真空层
    fcc_111_surface.center(vacuum=vacuum/2, axis=2)

    # 将所有原子向下移动，使得真空层只在一边
    positions = fcc_111_surface.get_positions()
    positions[:, 2] -= vacuum / 2
    fcc_111_surface.set_positions(positions)   

    # 重复晶胞结构
    fcc_111_surface = fcc_111_surface.repeat(repetitions)

    # 打印结构信息
    print(fcc_111_surface)

    # 保存结构到文件
    write(output_file, fcc_111_surface, format='vasp')

    #view(fcc_111_surface)

#适用于仅有一个元素
def get_stru_info(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    mass = None
    pseudopotential = None
    orbital_file = None

    for line in lines:
        if line.startswith('ATOMIC_SPECIES'):
            element_line = lines[lines.index(line) + 1].split()
            mass = float(element_line[1])
            pseudopotential = element_line[2]
        elif line.startswith('NUMERICAL_ORBITAL'):
            orbital_file = lines[lines.index(line) + 1].strip()

    return mass, pseudopotential, orbital_file

# 示例用法
element = sys.argv[1]  # 元素符号，例如铑 (Rh)

system=dpdata.System(f"../../00_cell_lenth_relax/STRU", fmt="abacus/stru")
lattice_constant = system.data["cells"][0][0][0] # 原胞晶胞边长（单位：Å）

fcc_lattice_constant=lattice_constant*2

n_layer = 5  # 表面层数
vacuum = 15  # 真空层厚度（单位：Å）
repetitions = (2,4,1)  # 重复晶胞结构，例如 "2,2,1"
output_file = f"{element}_slab.vasp"  # 输出文件名

create_fcc_111_surface(element, fcc_lattice_constant, n_layer, vacuum, repetitions, output_file)

#读取一些信息
mass, pseudopotential, orbital_file = get_stru_info("../../00_cell_lenth_relax/STRU")

#调用dpdata将vasp文件转为abacus格式
system=dpdata.System(output_file, fmt="vasp/poscar")
system.to("abacus/stru", output_file.replace(".vasp",".STRU"),mass=[mass],pp_file=[pseudopotential],numerical_orbital=[orbital_file])

