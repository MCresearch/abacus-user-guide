from ase.build import bulk, surface, fcc111, add_adsorbate, molecule
from ase.io import read, write
from ase.visualize import view
from ase import Atoms
import sys
import dpdata
import math
import numpy as np
import copy

# 获取表面原子的 Z 范围
def get_surface_atom_pos(atoms, z_range):
    positions = atoms.get_positions()
    return [pos for pos in positions if z_range[0] < pos[2] < z_range[1]]

def find_nearest_pos(positions, target_position, cell_lengths):
    """
    查找在一系列原子中，x 和 y 坐标最接近某一个坐标的原子。

    参数:
    positions : 一系列位置
    target_position (list or tuple): 目标坐标，格式为 [x, y]。
    cell_lengths (list or tuple): 晶胞的长度，格式为 [a, b]。

    返回:
    最接近的原子的位置。
    """
    positions = np.array(positions)  # 将列表转换为 NumPy 数组
    xy_positions = positions[:, :2]  # 只取 x 和 y 坐标
    target_xy = np.array(target_position)

    # 计算每个原子与目标坐标的最小距离，考虑周期性边界条件
    min_distances = np.full(len(xy_positions), np.inf)
    for i, pos in enumerate(xy_positions):
        for dx in [-cell_lengths[0], 0, cell_lengths[0]]:
            for dy in [-cell_lengths[1], 0, cell_lengths[1]]:
                dist = np.linalg.norm(pos + np.array([dx, dy]) - target_xy)
                if dist < min_distances[i]:
                    min_distances[i] = dist

    # 找到最小距离的原子索引
    nearest_atom_index = np.argmin(min_distances)

    return positions[nearest_atom_index]

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


element = sys.argv[1]  # 元素符号，例如铑 (Rh)

system = dpdata.System(f"../01_relax/OUT.ABACUS/STRU_ION_D", fmt="abacus/stru")
# 调用dpdata将vasp文件转为abacus格式
output_file = f"{element}_slab_after_relax.vasp"
system.to("vasp/poscar", output_file)

#读取一些信息
mass, pseudopotential, orbital_file = get_stru_info("../01_relax/OUT.ABACUS/STRU_ION_D")

# 读取生成的表面结构
surface_structure = read(output_file)


# 根据晶胞边长估计一层原子的高度
height = surface_structure.cell[0, 0] / 2 * (3**0.5) / 2
print("height:", height)

# 获取晶胞参数
cell = surface_structure.get_cell()
cell_lengths = cell.lengths()[:2]  # 只取 x 和 y 方向的晶胞长度

co_lenth = 1.138  # CO 键长
co_molecule = Atoms('CO', positions=[(0., 0., 0.), (0., 0., co_lenth)])

metal_r=surface_structure.cell[0, 0] / 4 # 估计金属原子半径，略小于实际金属原子半径


adsorbs=[("top",4, 0.1),("hcp",3, 0.4),("fcc",2,0.4),("bridge",4, 0.3)]

for (name,n_layer,dist_offset) in adsorbs:

    print(f"-----Adsorbate: {name}-----")

    # 获取表面原子的坐标
    surface_atom_pos = get_surface_atom_pos(surface_structure, z_range=(math.floor(height * (n_layer-0.5)), math.ceil(height * (n_layer))))

    # 打印表面原子的坐标
    print("Surface atoms positions:", surface_atom_pos)

    # 目标坐标
    target_position = [0,0] #尽量找位于边界上的原子

    print("Target positions:", target_position)

    nearest_atom_position = find_nearest_pos(surface_atom_pos, target_position, cell_lengths)

    print(f"Nearest atom position: {nearest_atom_position}")

    dist=metal_r+0.70-dist_offset # metal_r+c_r-dist_offset,在hollow位置尽量往下一些
    print("CO and metal dist:", dist)

    # 创建 surface_structure 的副本
    surface_structure_copy = copy.deepcopy(surface_structure)

    co_position=nearest_atom_position[:2]
    if name == "bridge":
        co_position=co_position+cell[0][:2]/4
        #print(co_position)

    # 添加 CO 分子到最接近目标位置的原子上方
    add_adsorbate(surface_structure_copy, co_molecule, height=dist, position=co_position)
    # offset 用的是分数坐标，这样加 CO 更自然
    add_adsorbate(surface_structure_copy, co_molecule, height=dist, position=co_position, offset=[0.5, 0.5])

    # 保存吸附结构到文件
    output_file_with_co = f"{element}_slab_CO_{name}.vasp"
    write(output_file_with_co, surface_structure_copy)

    #调用dpdata将vasp文件转为abacus格式
    system=dpdata.System(output_file_with_co, fmt="vasp/poscar")
    system.to("abacus/stru", output_file_with_co.replace(".vasp",".STRU"),mass=[mass,12,16],\
              pp_file=[pseudopotential,"C_ONCV_PBE-1.0.upf","O_ONCV_PBE-1.0.upf"],\
                numerical_orbital=[orbital_file,"C_gga_7au_100Ry_2s2p1d.orb","O_gga_7au_100Ry_2s2p1d.orb"])
