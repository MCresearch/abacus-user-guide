# ABACUS 随机密度泛函理论典型算例

**作者：陈诺，邮箱：chennuo@stu.pku.edu.cn；**

**作者：李雨桥，邮箱：yuqiaoli25@stu.pku.edu.cn**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2026/03/17**

# 一、介绍

ABACUS 作为一款高效开源的第一性原理计算软件，不仅支持传统的 Kohn-Sham 密度泛函理论（Kohn-Sham Density Functional Theory, KSDFT），还集成了随机波函数密度泛函理论（Stochastic Density Functional Theory, SDFT）[1]。SDFT 方法主要旨在解决传统 KSDFT 在模拟高温高压物质，特别是温稠密物质（Warm Dense Matter, WDM）时面临的计算瓶颈。在电子温度高达数十至上千 eV 的极端条件下，传统方法需要处理极大数量的占据态电子波函数并进行昂贵的哈密顿矩阵对角化，导致计算难以进行。SDFT 通过引入随机波函数轨道，利用 c 切比雪夫多项式展开等技术，有效避开了显式的矩阵对角化步骤，从而显著降低了计算复杂度，使其成为高温体系模拟的理想选择。此外，ABACUS 还支持混合随机-确定性 DFT 方法（Mixed stochastic-deterministic DFT, MDFT），即在计算中混入部分低能 Kohn-Sham 轨道，以进一步加速结果收敛。SDFT 和 MDFT 方法的优势使其能在极端高温条件下有效模拟物质性质，如预测极端高温环境下多种材料的状态方程 [2]，并用于为机器学习势函数方法提供训练数据 [3]，探索温稠密物质的性质。相关内容可参考新闻稿：[ABACUS 还能干这个？预测极端高温环境下多种材料的状态方程](https://mp.weixin.qq.com/s/dOSDZRKrK_PrfULoQqDR9w)以及 [ABACUS 还能干这个？为数百万度高温物质的 DP 势提供训练数据](https://mp.weixin.qq.com/s/8M8RyKGuMkRIeCMnjwup3A)。

# 二、算例概况

本算例集提供了一系列随机密度泛函理论和混合随机-确定性密度泛函理论的测试案例及参考结果，为跨平台计算结果的一致性提供参考依据。

> 在温稠密物质模拟中，温度常用电子伏特 (eV) 表示，1 eV = 11604.5 K。

1. 算例 1：密度为 12.307 g/cc，700 eV 高温的温稠密碳，随机密度泛函理论算例；目录名为 C-sdft-8atom-700eV-3.5η，峰值内存约 0.3GB
2. 算例 2：密度 14.416 g/cc，172.34 eV 高温的温稠密碳，混合随机-确定性密度泛函理论算例；目录名为 C-mdft-8atom-172.34eV-4.1η，峰值内存约 0.3GB
3. 算例 3：密度 9.84 g/cc，350 eV 的温稠密硼，随机密度泛函理论算例；目录名为 B-sdft-32atom-350eV-4.0η，峰值内存约 2.1GB

以上算例可在 `gitee` 或者 `GitHub` 上免费下载。具体方式是：在网页右侧点击 `克隆/下载-> 下载 ZIP` 得到算例压缩包并解压，或在命令行通过如下命令下载算例：

## `gitee` 网站

```
git clone https://gitee.com/mcresearch/abacus-user-guide.git
```

## `GitHub` 网站

```
git clone https://github.com/MCresearch/abacus-user-guide.git
```

进入目录 `abacus-user-guide/examples/sdft_bench` 文件夹可查看算例，算例包含了相应的赝势文件，无需额外下载。

# 三、输入

以下为三组算例的主要输入参数。输入参数详细说明可参考 ABACUS 文档（[https://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#electronic-structure-sdft](https://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#electronic-structure-sdft)），这里简单说明算例 INPUT 文件的一些重要参数：

- **calculation **设置为 `scf`，代表进行电子自洽迭代计算（Self-Consistent Field）。
- **esolver_type **设置系统总能量求解方法，默认为 `ksdft`（Kohn-Sham Density Functional Theory），这里需要设置为 `sdft` 才会使用 SDFT 或者 MDFT 进行计算。
- **nbands 和 nbands_sto **分别代表使用的 Kohn-Sham 轨道（determinstic orbitals）的数目和随机波函数轨道（stochastic orbitals）数目。如果 `nbands` 设置为 0，且 `nbands_sto` 不为 0，则进行 SDFT 计算；如果 `nbands` 与 `nbands_sto` 都不为 0，则会进行混合 KS 电子轨道和随机轨道的 MDFT 计算。

  - `nbands_sto` 设置为 `all` 时，使用完备的基组，避免引入随机误差。
- **nche_sto **是电子体系哈密顿量的切比雪夫展开阶数，切比雪夫展开阶数越多计算精度也会越高，但效率越低。
- **ecutwfc **是平面波截断能，只有动能低于该阈值的平面波才会被包含在基组中。`ecutwfc` 越大，包含的平面波越多，基组越完备，计算结果（如总能量、力、应力）越精确，同时计算成本（时间、内存需求）越高。

在本算例集中，选取了较小的平面波截断能（ecutwfc）和切比雪夫展开阶数（nche_sto）以控制峰值内存和计算时间，便于在广泛的硬件平台上测试 SDFT/MDFT 功能。实际计算时需要对随机轨道数目 `nbands_sto`、切比雪夫展开阶数 `nche_sto`、平面波截断能 `ecutwfc` 等参数进行收敛性测试，详见 [ABACUS 随机波函数 DFT 方法使用教程 · GitBook](https://mcresearch.github.io/abacus-user-guide/abacus-sdft.html)。以下为算例的详细输入参数，包括 INPUT/STRU/KPT 文件。

## 算例 1：C-sdft-8atom-700eV-3.5η

此算例为 8 原子碳，温度 700 eV，纯随机轨道 SDFT， nbands 设置为 0。

### INPUT

```bash
INPUT_PARAMETERS
#Parameters     (General)
calculation     scf

esolver_type    sdft
pseudo_dir      .
orbital_dir     .
nbands          0
nbands_sto      all
nche_sto        10
seed_sto        20000
kpar 4

symmetry        0
cal_force       1
cal_stress      1

min_dist_coef   0
#Parameters (Accuracy)
ecutwfc         30
scf_thr         1e-8
scf_nmax        50

#Parameters (3.Basis)
basis_type      pw
gamma_only      0

#Parameters (4.Smearing)
smearing_method fd
smearing_sigma  51.44908446

#Parameters (5.Mixing)
mixing_type     broyden
mixing_beta     0.7
```

### STRU

```bash
ATOMIC_SPECIES
C 12.0107 C-0.6.UPF upf201

LATTICE_CONSTANT
2.34921622

LATTICE_VECTORS
1.8897261246257702 0.0000 0.0000
0.0000 1.8897261246257702 0.0000
0.0000 0.0000 1.8897261246257702

ATOMIC_POSITIONS
Direct

C #label
0 #magnetism
8 #number of atoms
...
```

### KPT

```bash
K_POINTS
0
Gamma
2 2 2 0.5 0.5 0.5
```

## 算例 2：C-mdft-8atom-172.34eV-4.1η

此算例为 8 原子碳，温度 172.34 eV，混合随机-确定性轨道 MDFT。

### INPUT

```bash
INPUT_PARAMETERS
#Parameters     (General)
calculation     scf

esolver_type    sdft 
pseudo_dir      . 
orbital_dir     .
nbands          80
nbands_sto      all
nche_sto        10
seed_sto        20000

symmetry        0 
cal_force       1 
cal_stress      1 
kpar            4

min_dist_coef   0
#Parameters (Accuracy)
ecutwfc         20
scf_thr         1e-8 
scf_nmax        50  

#Parameters (3.Basis)
basis_type      pw
gamma_only      0

#Parameters (4.Smearing)
smearing_method fd
smearing_sigma  12.66676459

#Parameters (5.Mixing)
mixing_type     broyden
mixing_beta     0.7
```

### STRU

```bash
ATOMIC_SPECIES
C 12.0107 C-0.6.UPF upf201

LATTICE_CONSTANT
2.22852608

LATTICE_VECTORS
1.8897261246257702 0.0000 0.0000
0.0000 1.8897261246257702 0.0000
0.0000 0.0000 1.8897261246257702

ATOMIC_POSITIONS
Direct

C #label
0 #magnetism
8 #number of atoms
...
```

### KPT

```bash
K_POINTS
0
Gamma
2 2 2 0.5 0.5 0.5
```

## 算例 3：B-sdft-32atom-350eV-4.0η

此算例为 32 原子硼，温度 350 eV，纯随机 SDFT。

### INPUT

```bash
INPUT_PARAMETERS
#Parameters (1.General)
calculation     scf
esolver_type    sdft
nbands          0
nbands_sto      all
nche_sto        2
seed_sto        20000
symmetry        1
kpar            4
pseudo_dir      .
cal_stress      1
cal_force       1

ks_solver       cg

min_dist_coef   0
#Parameters (2.Iteration)
ecutwfc         10
scf_thr         1e-8
scf_nmax        50

#Parameters (3.Basis)
basis_type      pw
gamma_only      0

#Parameters (4.Smearing)
smearing_method fd
smearing_sigma  25.72454223

#Parameters (5.Mixing)
mixing_type     broyden
mixing_beta     0.7
```

### STRU

```bash
ATOMIC_SPECIES
B 10.81 B-0.7.upf

LATTICE_CONSTANT
3.87877229

LATTICE_VECTORS
1.88972612463 0 0 #latvec1
0 1.88972612463 0 #latvec2
0 0 1.88972612463 #latvec3

ATOMIC_POSITIONS
Cartesian

B #label
0 #magnetism
32 #number of atoms
...
```

### KPT

```bash
K_POINTS
0
Gamma
4 4 4 0.5 0.5 0.5
```

# 四、参考结果

对于每个算例，基于 ABACUS v3.9.0.25 版本 [Release v3.9.0.25 · deepmodeling/abacus-develop](https://github.com/deepmodeling/abacus-develop/releases/tag/v3.9.0.25) 进行测试给出一组参考结果；测试使用的 CPU 硬件为 `Intel® Xeon® Gold 6132`，并使用 28 进程并行。

```
OMP_NUM_THREADS=1 mpirun -np 28 abacus
```

## **算例 1：C-sdft-8atom-700eV-3.5η**

- 关键参数

```bash
FFT格子15*15*15；symmetry 0；非自旋极化（nspin=1）；k点数 4；
```

- 迭代能量和收敛数据：

| ITER | ETOT/eV | EDIFF/eV | DRHO | TIME/s |
|:------|---------|----------|------|--------|
| CG1 | -1.03510842e+05 | 0.00000000e+00 | 6.8322e+01 | 0.12 |
| CG2 | -1.03477074e+05 | 3.37677021e+01 | 6.4904e+00 | 0.12 |
| CG3 | -1.03477944e+05 | -8.70302376e-01 | 2.2376e-04 | 0.12 |
| CG4 | -1.03477944e+05 | -7.82068782e-06 | 1.6715e-06 | 0.12 |
| CG5 | -1.03477944e+05 | -1.20840460e-05 | 8.6856e-10 | 0.12 |

- 总耗时（秒）：1
- 应力：

| Stress_x | Stress_y | Stress_z |
|----------|----------|----------|
| 653060.0345820124 | -0.0000000011 | -0.0000000012 |
| -0.0000000011 | 653060.0345820172 | -0.0000000001 |
| -0.0000000012 | -0.0000000001 | 653060.0345820081 |

- 总压强：653060.034582 kbar
- 总能量：-103477.94442751311 eV

| Energy | Rydberg | eV |
|:---|:---|:---|
| E_KohnSham | -7605.485909470700 | -103477.944427513095 |
| E_KS(sigma->0) | -3620.826491988900 | -49263.871760400398 |
| E_Harris | -7605.485919174800 | -103477.944559544601 |
| E_band | 693.370953180800 | 9433.795790949900 |
| E_one_elec | 777.554483510000 | 10579.171481182701 |
| E_Hartree | 0.213231073900 | 2.901157596100 |
| E_xc | -64.471687434500 | -877.182308784800 |
| E_Ewald | -349.463101656500 | -4754.689423281700 |
| E_entropy(-TS) | -7969.318834963500 | -108428.145334225395 |
| E_descf | 0.000000000000 | 0.000000000000 |
| E_localpp | -8.279816805300 | -112.652686948400 |
| E_exx | 0.000000000000 | 0.000000000000 |
| E_Fermi | -97.258660495300 | -1323.271962583300 |
| E_gap(k) | 0.000000000000 | 0.000000000000 |

## **算例 2：C-mdft-8atom-172.34eV-4.1η**

- 关键参数

```bash
FFT格子12*12*12；symmetry 0；非自旋极化（nspin=1）；k点数 4；
```

- 迭代能量和收敛数据：

| ITER | ETOT/eV | EDIFF/eV | DRHO | TIME/s |
|:------|---------|----------|------|--------|
| CG1 | -1.93218981e+04 | 0.00000000e+00 | 5.2431e+01 | 0.09 |
| CG2 | -1.93136274e+04 | 8.27074737e+00 | 4.4473e+00 | 0.07 |
| CG3 | -1.93152166e+04 | -1.58918086e+00 | 2.1547e-03 | 0.07 |
| CG4 | -1.93152190e+04 | -2.45295655e-03 | 2.1207e-05 | 0.07 |
| CG5 | -1.93152190e+04 | -1.41285976e-05 | 9.9416e-09 | 0.07 |

- 总耗时（秒）：1
- 应力：

| Stress_x | Stress_y | Stress_z |
|----------|----------|----------|
| 317971.7182958177 | -0.0055815013 | -0.0022782560 |
| -0.0055815013 | 317971.7205291149 | -0.0104593909 |
| -0.0022782560 | -0.0104593909 | 317971.7193757975 |

- 总压强：317971.719400 kbar
- 总能量：-19315.21903970846 eV

| Energy | Rydberg | eV |
|:---|:---|:---|
| E_KohnSham | -1419.641905891800 | -19315.219039708500 |
| E_KS(sigma->0) | -713.745750248700 | -9711.009126667401 |
| E_Harris | -1419.642046724300 | -19315.220955832301 |
| E_band | 341.406351218100 | 4645.071709955700 |
| E_one_elec | 426.592246459400 | 5804.085274468000 |
| E_Hartree | 2.229839496100 | 30.338522772800 |
| E_xc | -68.282731083300 | -929.034217734100 |
| E_Ewald | -368.388949477900 | -5012.188793133100 |
| E_entropy(-TS) | -1411.792311286200 | -19208.419826082099 |
| E_descf | 0.000000000000 | 0.000000000000 |
| E_localpp | -44.230202623600 | -601.782779375000 |
| E_exx | 0.000000000000 | 0.000000000000 |
| E_Fermi | -7.548030710200 | -102.696226338000 |
| E_gap(k) | 0.083805560900 | 1.140233152400 |

## **算例 3：B-sdft-32atom-350eV-4.0η**

- 关键参数

```bash
FFT格子15*15*15；symmetry 1；非自旋极化（nspin=1）；k点数 32；
```

- 迭代能量和收敛数据：

| ITER | ETOT/eV | EDIFF/eV | DRHO | TIME/s |
|:------|---------|----------|------|--------|
| CG1 | -1.00188957e+05 | 0.00000000e+00 | 1.8451e+02 | 0.30 |
| CG2 | -1.00209871e+05 | -2.09142483e+01 | 1.8587e+01 | 0.28 |
| CG3 | -1.00275565e+05 | -6.56942117e+01 | 7.7940e-03 | 0.28 |
| CG4 | -1.00277612e+05 | -2.04693781e+00 | 6.4808e-06 | 0.28 |
| CG5 | -1.00277606e+05 | 6.37347121e-03 | 3.9209e-07 | 0.29 |
| CG6 | -1.00277613e+05 | -7.26670022e-03 | 3.7190e-10 | 0.28 |

- 总耗时（秒）：2
- 应力：

| Stress_x | Stress_y | Stress_z |
|----------|----------|----------|
| 89752.2769606179 | -3327.5008047372 | -1942.9469782955 |
| -3327.5008047372 | 86096.4625893440 | 46.1222896893 |
| -1942.9469782955 | 46.1222896893 | 83568.9780406885 |

- 总压强：86472.572530 kbar
- 总能量：-100277.61291647585 eV

| Energy | Rydberg | eV |
|:---|:---|:---|
| E_KohnSham | -7370.265966250000 | -100277.612916475802 |
| E_KS(sigma->0) | -3803.406020729500 | -51747.993689427101 |
| E_Harris | -7370.265977531100 | -100277.613069963307 |
| E_band | 626.136633785300 | 8519.025946019199 |
| E_one_elec | 879.496037809300 | 11966.157482629900 |
| E_Hartree | 1.597054817900 | 21.729045541400 |
| E_xc | -195.632279310600 | -2661.713711352300 |
| E_Ewald | -922.006888525500 | -12544.547279197401 |
| E_entropy(-TS) | -7133.719891041100 | -97059.238454097504 |
| E_descf | 0.000000000000 | 0.000000000000 |
| E_localpp | -17.482495033500 | -237.861547712500 |
| E_exx | 0.000000000000 | 0.000000000000 |
| E_Fermi | -8.153564900200 | -110.934941655000 |
| E_gap(k) | 0.000000000000 | 0.000000000000 |

# 五、参考文献

[1] Liu, Q., & Chen, M. (2022). Plane-wave-based stochastic-deterministic density functional theory for extended systems. _Physical Review B_.

[2] Chen, T., Liu, Q., Gao, C., & Chen, M. (2025). First-principles prediction of shock Hugoniot curves of boron, aluminum, and silicon from stochastic density functional theory. _Matter and Radiation at Extremes_.

[3] Chen, T., Liu, Q., Liu, Y., Sun, L., & Chen, M. (2023). Combining stochastic density functional theory with deep potential molecular dynamics to study warm dense matter. _Matter and Radiation at Extremes_.
