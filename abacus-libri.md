# ABACUS+LibRI 做杂化泛函计算教程

<strong>作者：梁馨元，邮箱：2201111875@stu.pku.edu.cn</strong>

<strong>审核：林霈泽，邮箱：linpeize@sslab.org.cn</strong>

<strong>最后更新时间：2023/07/21</strong>

# 一、介绍

杂化泛函（Hybrid Functional）是指在密度泛函理论框架中的交换关联项里面加入一部分的 Hartree Fock (简称 HF)的精确交换能。开源密度泛函理论软件 ABACUS 可以结合另一款国产开源软件 [LibRI 软件](https://github.com/deepmodeling/LibRI)进行杂化密度泛函计算，目前仅支持在数值原子轨道基组下使用该功能。可以通过 `dft_functional` 参数指定所使用的杂化泛函类型，如可以选择 `hf` (Hartree-Fock), `pbe0`(PBE0), `hse`(HSE06)以及 `scan0` 杂化泛函。本教程以 HSE 杂化泛函为例，介绍如何<strong>在 ABACUS 里调用 LibRI 做杂化泛函自洽迭代、求力和应力以及结构优化。</strong>

注 1：使用 ABACUS+LibRI 做杂化泛函计算时，最大并行核数是$$N_a^4N_K^3$$，其中$$N_a$$是原子个数，$$N_k$$是 k 点个数。计算资源超出时可以运行，但会造成浪费。

注 2：使用 ABACUS+LibRI 做杂化泛函计算时，因为内存消耗比较大，推荐给定计算资源的前提下，先尽量使用 OpenMP 多线程并行，再考虑使用 MPI 多进程并行。

# 二、杂化泛函的使用

## 1. ABACUS 编译准备

如果要在 ABACUS 中使用杂化泛函进行计算，需要在编译 ABACUS 的时候也编译 `Libxc`、`LibRI` 和 `LibComm` 三个软件包，具体请见线上文档 [Advanced Installation Options ‒ ABACUS documentation](https://abacus.deepmodeling.com/en/latest/advanced/install.html)。

注意在链接 `LibRI`、`LibComm` 时如果报错未定义的引用等，可以先注意检查 ABACUS 源代码下 `deps` 文件夹下是否包含 `LibRI`、`LibComm` 两个文件夹。如果未包含这两个文件夹，或文件夹中无内容，在本地Github仓库中可以尝试如下两条语句，以获取这两个子仓库内容：
```bash
git submodule init
git submodule update --remote --recursive
```

## 2. 采用杂化泛函进行电子自洽迭代计算

本教程在 Gitee 上准备了一个硅晶体使用杂化泛函做自洽计算（SCF）的例子（[Gitee 的下载链接](https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/hybrid_functional/1_scf_Si)），以下是 `INPUT` 文件及相关的参数。由 `dft_functional` 设置为 hse 可知，该例子使用的杂化泛函为 HSE 泛函。`KPT` 文件取的是 4*4*4 的布里渊区 k 点。

```bash
INPUT_PARAMETERS
calculation scf
basis_type lcao
ntype 1
nbands 8
ecutwfc 60.0
scf_nmax 100

dft_functional hse
scf_thr 1e-7
```

杂化泛函相关的完整参数列表及解释见 [Full List of INPUT Keywords / exact-exchange ‒ ABACUS documentation](https://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#exact-exchange)。这里再进行简单概述：

- 泛函相关参数：
  - <strong>exx_hybrid_alpha</strong>：杂化泛函中加入的 HF 精确交换能（Fock 交换能）的比例$$α$$，即有$$E_x=αE_{x}^{HF}+(1-α)E_{x}^{LDA/GGA}$$。如果 dft_functional 设置为 hf，则默认值为<strong>1</strong>。目前其他杂化泛函的默认值是<strong>0.25</strong>。但是，如果是 SCAN0 泛函，有的文献取的是 0.1，所以需要根据你想取的值进行设定[1]。
  - <strong>exx_hse_omega</strong>：为 HSE 泛函中的区间分割参数（range-separation parameter）$$\omega$$，即有$$\frac{1}{r}=\frac{erfc({\omega}r)}{r}+\frac{erf({\omega}r)}{r}$$。默认值为<strong>0.11</strong>（$$bohr^{-1}$$），此时为 HSE06 泛函[2]。
  - <strong>exx_lambda</strong>：在 basis_type 设置为 lcao_in_pw 的情况下，用于补偿使用 lcao_in_pw 方法评估精确交换能时 G=0 处的发散点。默认值为<strong>0.3</strong>。
- <strong>exx_real_number</strong>：该参数设定为 True 时，强制 LibRI 使用 double 数据类型，当设定为 False 时，强制 LibRI 使用 complex 数据类型。当<strong>gamma_only</strong>=1 时，默认为 True，<strong>gamma_only</strong>=0 时默认为 False。
- 循环相关参数：
  - <strong>exx_separate_loop</strong>：ABACUS 提供了两种迭代方法来评估精确交换能$$E_{exx}$$。当 exx_separate_loop 设置为<strong>False</strong>时：采用单层循环，即先进行 GGA 循环，然后进行 Hybrid 循环，在该过程中，使用电子迭代来更新$$E_{exx}$$对应的哈密顿量$$H_{exx}$$。当 exx_separate_loop 设置为<strong>True</strong>时：采用双层循环，在内层循环中，进行自洽迭代并更新密度矩阵，在外层循环中，根据在内层循环中收敛的密度矩阵来计算$$H_{exx}$$。默认值为 True，即采用双层循环计算。单层循环有利于难以自洽收敛的体系达到收敛，但会显著增加内存消耗。
  - <strong>exx_hybrid_step</strong>：在 exx_separate_loop 设置为 True 的情况下，外层循环的最大迭代步数。默认值为<strong>100</strong>。
  - <strong>exx_mixing_beta</strong>：在 exx_separate_loop 设置为 True 的情况下，内层循环每次迭代时，密度矩阵混合的 mixing_beta 取值，默认为<strong>1.0</strong>。
- <strong>exx_pca_threshold</strong>：为了加速四中心积分$$\langle ik\vert\ jl\rangle$$的计算，ABACUS 采用 LRI 方法，将原子轨道的乘积在辅助基函数(ABF)的基础上展开，即$$\Phi_i\Phi_j \approx \sum_aC_{ij}^aP_a$$，并利用 PCA 减小辅助基函数(ABF)的大小(即$$P_a$$个数)。阈值越大，ABF 的数目越少，计算速度越快，计算精度越低。一个相对安全的值是<strong>1e-4</strong>，也是默认值。
- <strong>exx_ccp_rmesh_times</strong>：此参数决定计算 Columb 势所需的截断半径比原子轨道的截断半径大多少倍。对于 HSE 泛函，设置为 1 就足够了。但是对于 PBE0，必须使用一个大得多的数字。当使用 HSE 泛函时，默认值为<strong>1.5</strong>，其他情况下默认值为<strong>5</strong>。
- 张量筛选相关参数：
针对杂化泛函计算过程中的物理量进行筛选可以加速计算。具体来说，exx_c_threshold、exx_v_threshold、exx_dm_threshold、exx_c_grad_threshold、exx_v_grad_threshold 分别是针对$$C_{ij}^a$$、$$V_{ab}=\langle P_a\vert\ P_b\rangle$$、密度矩阵、$$\nabla C_{ij}^a$$、$$\nabla V_{ab}$$。阈值越大，筛掉的张量越多，计算速度越快，计算精度越低。具体请查看完整 INPUT 参数文档。
- Cauchy-Schwartz 不等式相关参数：
  - <strong>exx_cauchy_threshold</strong>：在实际中，Fock 交换矩阵是稀疏的，利用 Cauchy-Schwartz 不等式，我们可以在进行显式求值之前找到每个矩阵元素的上界。小于 exx_cauchy_threshold 的值将被截断。阈值越大，筛掉的张量越多，计算速度越快，精度越低。一个相对安全的值是<strong>1e-7</strong>，也是默认值。不等式算法参见参考文献[3]。
  - <strong>exx_cauchy_force_threshold、exx_cauchy_stress_threshold</strong>与<strong>exx_cauchy_threshold</strong>类似，区别在于它们分别针对的是求力、应力计算中的 Fock 交换矩阵元。
- opt_orb 相关参数：当<strong>dft_functional</strong>设置为 opt_orb 时使用，opt_orb 参考文献[4]。本功能仅用于生成 opt 辅助基组，不进行杂化泛函计算。
  - <strong>exx_opt_orb_lmax</strong>：球贝塞尔函数的最大角动量 L 值，opt-ABF 的径向部分用球贝塞尔函数的线性组合生成。
  - <strong>exx_opt_orb_ecut</strong>：球贝塞尔函数展开的截断，在优化 opt-ABF 的时候采用的是球贝塞尔函数基组。
  - <strong>exx_opt_orb_tolerence</strong>：解球贝塞尔函数零点时的阈值。

## 3. 杂化泛函计算代价

杂化泛函的计算精度高，与此同时它的计算代价也比较高。在 ABACUS 的输入参数文件 `INPUT` 中，若 `exx_separate_loop` 参数设为 True（默认），仅在 SCF 步骤中就涉及两层循环。每次内层循环完成，外层循环往前推进一步时，屏幕输出 `Updating EXX and rerun SCF`。

一次 SCF 需要的时间至少是以上两个循环涉及的单次电子迭代时间之和。对于单次电子迭代所需时间，在此提出一些已有的经验。<strong>以一步电子迭代的时间为衡量尺标</strong>，使用 DZP 基组，CPU 型号为 Intel(R) Xeon(R) Gold 6132 CPU @ 2.60GHz，使用 4 核计算一个水分子为 0.6s 左右，使用 14 个核计算 32 个水分子为 0.8s 左右，使用 14 个核计算 64 个水需要 1.9s 左右。

若将 `exx_separate_loop` 参数设为 False，即使用单层循环时，首先会进行 GGA 迭代直到自洽收敛，然后屏幕输出 `Entering 2nd SCF, where EXX is updated`，进行 Hybrid 迭代，此时每进行一次电子步得到新的密度后，都会更新一次精确交换能。以<strong>一步电子迭代 + 更新精确交换能的时间为衡量尺标</strong>，使用 DZP 基组，CPU 型号为 Intel(R) Xeon(R) Gold 6132 CPU @ 2.60GHz，使用 4 核计算一个水分子为 0.7s 左右，使用 14 个核计算 32 个水分子为 115s 左右，使用 14 个核计算 64 个水需要 330s 左右。对于更大的体系，如 2048 个 Si 原子的晶体，使用 DZP 基组，CPU 型号为 Intel(R) Xeon(R) Silver 4310 CPU @ 2.10GHz，用一个节点（56 核）算时，PBE 下一步电子迭代大概需要 380s，而 HSE 一步电子迭代 + 更新精确交换能大概需要 1680s。

在进行杂化泛函计算时推荐尽量使用多线程计算（OpenMP），此时内存开销相对较小，计算速度相对较快。

# 三、使用杂化泛函做结构优化

## 1. 数据准备

在 Gitee 上我们准备了一个简单的使用杂化泛函做结构优化的[例子](https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/hybrid_functional/2_relax_water)。该例子是在 LCAO 基组下，使用 HSE 泛函，优化单个水分子的结构。文件夹中 `log.ref` 是使用 3.2.1 版本的 ABACUS 软件包，v0.1.0 版本的 `LibRI` 和 `LibComm` 计算所得的屏幕输出。

## 2. 输入文件

准备计算所需的 `INPUT` 文件、`STRU` 文件、`KPT` 文件，以及 H、O 原子对应的数值原子轨道文件。其中 `INPUT` 文件如下。注意该文件中指明了计算类型为 relax，即不对晶胞做优化（cell relax），只对原子位置做优化（relax）。更多结构优化类型请看文档 [Geometry Optimization ‒ ABACUS documentation](https://abacus.deepmodeling.com/en/latest/advanced/opt.html)。

```bash
INPUT_PARAMETERS
calculation relax
basis_type lcao
ntype 2
ecutwfc 60.000000
scf_nmax 100
gamma_only 1

dft_functional hse
relax_nmax 100
scf_thr 1e-6
force_thr_ev 1e-2
```

在该例子中，结构优化包括多个离子步，每个离子步中都要做一次 SCF。由 `INPUT` 文件可知，SCF 收敛的标准由 `scf_thr=1e-6` 指定，或达到 SCF 的最大步数 `scf_nmax=100`，并计算受力。根据上一个离子步计算得到的受力，计算下一个离子步的原子位置，计算收敛的标准此时为 `force_thr_ev=1e-2`，或达到离子步的最大步数 `relax_nmax=100`。`STRU` 文件如下，可见在结构弛豫步骤中，三个原子都可以移动。

```bash
ATOMIC_SPECIES
O 16.00 O_ONCV_PBE-1.0.upf
H 1.00 H_ONCV_PBE-1.0.upf

LATTICE_CONSTANT
1

LATTICE_VECTORS
28 0 0 
0 28 0 
0 0 28 

ATOMIC_POSITIONS
Direct

O #label
0 #magnetism
1 #number of atoms
0.677639488918  0.5227809096584  0.232500040128  m  1  1  1

H #label
0 #magnetism
2 #number of atoms
0.641808457616  0.5785821615863  0.228644198512  m  1  1  1
0.708889637644  0.5204300746076  0.175087721492  m  1  1  1

NUMERICAL_ORBITAL
O_gga_6au_60Ry_2s2p1d.orb
H_gga_6au_60Ry_2s1p.orb
```

## 3. 结果

结构弛豫（relax）后的原子结构可见 `OUT.ABACUS/STRU_ION_D`。由输出文件可知，即使该例子中采用了相对稳定的构型，且 `scf_thr` 仅设为 1e-6，使用 HSE 做结构弛豫的计算代价仍然很高，使用 6 个核（Intel(R) Xeon(R) Gold 6132 CPU @ 2.60GHz）计算需要 5 分钟左右。

# 四、参考文献

[1] Staroverov V N, Scuseria G E, Tao J, et al. Comparative assessment of a new nonempirical density functional: Molecules and hydrogen-bonded complexes[J]. The Journal of chemical physics, 2003, <strong>119</strong>(23): 12129-12137.

[2] Aliaksandr V. Krukau, Oleg A. Vydrov, Artur F. Izmaylov, Gustavo E. Scuseria; Influence of the exchange screening parameter on the performance of screened hybrid functionals. <em>J. Chem. Phys.</em> 14 December 2006; <strong>125</strong> (22): 224106.

[3] Lin P, Ren X, He L. Efficient hybrid density functional calculations for large periodic systems using numerical atomic orbitals. Journal of Chemical Theory and Computation, 2021, <strong>17</strong>(1): 222–239.

[4] Lin P, Ren X, He L. Accuracy of localized resolution of the identity in periodic hybrid functional calculations with numerical atomic orbitals[J]. The Journal of Physical Chemistry Letters, 2020, <strong>11</strong>(8): 3082-3088.
