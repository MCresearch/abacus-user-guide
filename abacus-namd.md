# ABACUS+Hefei NAMD 使用教程

<strong>作者：李源波，邮箱：liyuanbo9812@pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/10/01</strong>

# 一<strong>、介绍</strong>

激发态动力学一直是凝聚态物理中的重要问题，在激发状态下，凝聚态体系中的准粒子会发生复杂的相互作用，涉及到不同时间尺度的超快过程，因此，研究凝聚态体系的激发态动力学不仅需要从时间、空间、能量和动量等多个维度对其进行描述，还需要描述不同准粒子之间的动态耦合，而目前商用的第一性原理软件无法满足这样的需求。针对这一问题，中国科学技术大学赵瑾教授团队发展了自主可控的激发态动力学软件 Hefei-NAMD（[https://hefei-namd.org/code/](https://hefei-namd.org/code/)），基于面跳跃算法（Surface Hopping）与经典路径近似，初步实现激发态动力学在时间、空间、动量、能量、自旋等多个维度上的描述，并可以研究激发态电子、空穴、激子、声子、极化子等准粒子的动态相互作用。Hefei-NAMD 程序采用模块化架构，包含单粒子动力学、自旋动力学、动量空间动力学以及 GW+rtBSE 模块。目前程序使用周期性边界条件，可处理上百个原子，且与密度泛函软件 VASP、Quantum Espresso 等存在接口，Hefei-NAMD 和 ABACUS v3.2 建立的接口（主要针对局域轨道算法，涉及波函数与局域轨道下的交叠矩阵等信息，用来计算非绝热耦合项和电子跃迁概率）和提供的相关案例，可以进一步拓宽 Hefei-NAMD 的使用范围。

本教程旨在介绍采用 ABACUS（基于 ABACUS 3.2.0 版本）做分子动力学计算，将结果作为 Hefei NAMD 软件的输入文件进行后续非绝热分子动力学计算的流程。

这里推荐大家阅读 Hefei NAMD 软件的相关文档和说明：

[http://staff.ustc.edu.cn/~zqj/posts/Hefei-NAMD-Training/](http://staff.ustc.edu.cn/~zqj/posts/Hefei-NAMD-Training/)

[https://github.com/QijingZheng/Hefei-NAMD](https://github.com/QijingZheng/Hefei-NAMD)

[https://github.com/vtzf/abacus-namd](https://github.com/vtzf/abacus-namd)（这个是拥有与 ABACUS 接口的 Hefei NAMD 仓库，功能与上面的仓库是一样的），第一步请先下载这个链接上面的 python 代码。

# 二、计算<strong>流程</strong>

我们这里提供的测试案例是包含 2 个原子的金刚石结构 Si 结构，采用的模守恒赝势是 `Si_ONCV_PBE-1.0.upf`，以及原子轨道文件采用的是 `Si_gga_8au_60Ry_2s2p1d.orb`（GGA 泛函，8 au 截断半径，60 Ry 能量截断，以及包含 2s2p1d 的 DZP 轨道）。

## 1. 用 ABACUS 进行分子动力学(MD)计算

### 1.1 输入文件 INPUT

大部分参数为做分子动力学计算所需要参数，具体含义可以参考 [ABACUS 的分子动力学教程](https://mcresearch.gitee.io/abacus-user-guide/abacus-md.html)。为了后续用 Hefei NAMD 进行<strong>非绝热分子动力学</strong>计算，ABACUS 会输出每一步分子动力学模拟的哈密顿量矩阵 H、交叠矩阵 S、波函数文件。因此需将相关的 ABACUS 的 `INPUT` 文件中的输入参数 `out_wfc_lcao` 和 `out_mat_hs` 都设置为 1，表示输出这些物理量。计算完成后，在 `OUT.***` 文件夹中，每一个分子步都对应一个文件夹 `MD_n`，在每个文件夹中会有 `data-0-H`、`data-0-S`、`LOWF_GAMMA_S1.dat` 三个文件储存我们需要输出的物理量。

```bash
INPUT_PARAMETERS
 #Parameters     (General)
 suffix          autotest
 pseudo_dir      ../../tests/PP_ORB
 orbital_dir     ../../tests/PP_ORB
 nbands          8
 calculation     md

 #Parameters (Accuracy)
 ecutwfc         50
 scf_nmax        20

 basis_type      lcao
 md_nstep        10

 cal_stress      1
 stress_thr      1e-6
 cal_force       1
 force_thr_ev    1.0e-3

 ks_solver       genelpa
 mixing_type     pulay
 mixing_beta     0.7

 md_type         nve
 md_restart      0
 md_tfirst       10
 init_vel        1

 read_file_dir   ./

 gamma_only      1

 out_wfc_lcao    1
 out_mat_hs      1
```

### 1.2 结构文件 STRU

```bash
ATOMIC_SPECIES
 Si 1 Si_ONCV_PBE-1.0.upf

 NUMERICAL_ORBITAL
 Si_gga_8au_60Ry_2s2p1d.orb

 LATTICE_CONSTANT
 10.2

 LATTICE_VECTORS
 0.5 0.5 0 #latvec1
 0.5 0 0.5 #latvec2
 0 0.5 0.5 #latvec3

 ATOMIC_POSITIONS
 Cartesian

 Si #label
 0 #magnetism
 2 #number of atoms
 0  0  0  m  1  1  1  v  1.75205850628e-05  0.000155425594558  -3.99334763874e-05
 0.241  0.255  0.250999999999  m  1  1  1  v  -1.75205850628e-05  -0.000155425594558  3.99334763874e-05
```

## 2. 用 Hefei NAMD 进行非绝热分子动力学（NAMD）计算

Hefei NAMD 代码为 python 代码，在 `src` 目录下，建议使用 python 3.9。需要的 python 库有 Numpy，Scipy，Numba，MPI4py（>= 3.1.3）。

### 2.1 设置 NAMD 计算参数

在 Args.py 中设置 NAMD 的各种参数，在 Args.py 的注释中有关于各种参数具体含义的详细介绍。

```python
# NAMD parameter
# manual input start
dftdir   = '/public/share/zhaojin/tuyy/abacus/sh/OUT.autotest1/'
namddir  = '../namd_test/' # output NAMD output file in namddir
dt       = 1      # MD time step (fs)
start_t  = 1      # start MD step
end_t    = 2000   # end MD step
istart_t = 901    # isample start MD step
iend_t   = 1000   # isample end MD step

LCHARGE  = True   # output atom projected charge density
atom     = [13,26]# atom number of all species (only needed in atomic basis)
orbital  = [27,13]# atomic orbital basis number (only needed in atomic basis)
whichA   = [0,13,14,15] # atom index for projected charge density (starts from 0)

LRANGE   = True   # select range of band, change iband
                  # if not given, LRECOMB specifies energy range
                  # if LRECOMB not given, energy range: [0,nbands]
LHOLE    = True   # Hole/electron transfer
dE       = 2.0    # initial energy from VBM/CBM (eV)

LPHASE   = True   # phase correction

TEMP     = 300    # temperature in Kelvin
NACTIME  = 1000   # time for used NAC (i_end_t-state_t+NACTIME<nstep)
NAMDTIME = 1000   # time for NAMD run
NELM     = 1000   # electron time step (per fs)
NTRAJ    = 5000   # SH trajectories number

LINTERP  = 2      # hamiltonian interpolation algorithm 1,2,3
LTA      = False  # Liouville-Trotter algorithm for small NELM
LSH      = 'FSSH' # run DISH, FSSH or DCSH

LRECOMB  = False  # consider electron-hole recombination

OutMode  = 'text' # output file format 'numpy(.npy)' or 'text'
# manual input end
```

### 2.2 读取 ABACUS 的输出文件

运行 NAC.py 即可将 ABACUS 的输出文件转成 Hefei NAMD 需要的 NATXT 和 EIGTXT 文件。

在超算上计算的话，可以直接使用用 sub_scripts 目录下的 sub_nac 脚本提交任务，用户可在 sub_nac 中自行修改节点数等信息。

```bash
sbatch sub_nac
```

### 2.3 进行非绝热分子动力学计算

运行 SurfHop.py 即可进行 NAMD 的计算。

在超算上计算的话，可以直接使用用 `sub_scripts` 目录下的 `sub_sh` 脚本提交任务，用户可在 `sub_sh` 中自行修改节点数等信息。

```bash
sbatch sub_sh
```

输出文件中，`SUPROP` 文件中包含了电子驰豫能量和电子占据数随时间的演化，`PSICT` 文件则包含波函数系数随时间的演化。可用 [https://github.com/QijingZheng/Hefei-NAMD/tree/master/scripts](https://github.com/QijingZheng/Hefei-NAMD/tree/master/scripts) 中的脚本进行画图。

# 三<strong>、结语</strong>

本篇主要介绍了如何利用 ABACUS 和 Hefei NAMD 进行非绝热分子动力学的计算，简单来说就是通过 ABACUS 跑分子动力学得到每一步的波函数和哈密顿量等信息，Hefei NAMD 再读入这些信息进行非绝热分子动力学的计算。关于非绝热分子动力学的详细介绍则可以查看 Hefei NAMD 的相关网站（见最上面的网站），如有问题欢迎联系。

# 四、参考文献

Zheng, Q.; Chu, W.; Zhao, C.; Zhang, L.; Guo, H.; Wang, Y.; Jiang, X.; Zhao, J. Ab initio nonadiabatic molecular dynamics investigations on the excited carriers in condensed matter systems. <em>Wiley Interdiscip. Rev. Comput. Mol. Sci.</em> <strong>2019</strong>, <em>9</em>, e1411.
