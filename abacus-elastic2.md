# 采用 ABACUS 计算弹性常数教程

**作者：兰书悦，邮箱：lanshuyue@stu.pku.edu.cn**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2026/02/01**

# 背景介绍


依据胡克定律，弹性常数定量描述了固体材料在弹性变形范围内应力与应变的线性关联。弹性常数作为刻画材料抵抗弹性变形 “刚度” 的核心物理参数，是材料力学性能表征、工程结构设计与新型功能材料研发的关键基础数据，其精准获取直接影响材料服役性能评估、器件可靠性预测及材料设计的科学性。目前，通过第一性原理计算方法例如密度泛函理论，可以预测材料的弹性常数。

ABACUS（原子算筹）作为一款国产密度泛函理论软件，可用于弹性常数、电子结构、力学性能等诸多物理化学性质的计算模拟。然而，进行弹性常数计算涉及多个环节操作：从**初始结构构建**、**晶格优化**，到**施加应变**、**计算应力张量**，再到**弹性常数拟合**，每个步骤均对参数选择、操作细节有要求。新手用户常因**参数脚本设置不当**、**应变施加不规范**或**结果分析逻辑缺失**，导致计算结果偏差较大甚至计算失败，而有一定经验的研究者也可能在复杂体系的弹性常数矩阵求解、异常结果排查等环节遭遇瓶颈。

为帮助不同基础学习者快速掌握采用ABACUS计算弹性常数的方法，本教程将从理论基础（胡克定律与弹性常数定义）出发，介绍采用ABACUS计算弹性常数的流程，详细说明关键参数的选择逻辑、操作步骤及注意事项。


# 弹性常数

胡克定律描述了固体材料在弹性变形范围内，应力 $\sigma$ 与应变 $\epsilon$ 之间的线性关系：

$$
\sigma = C \cdot \epsilon
$$

其中 $$C$$ 为**弹性常数**，是广义胡克定律的核心参数，其物理意义是表征材料抵抗弹性变形的**刚度**。当应力超出材料的弹性极限时，材料可能发生塑性变形或断裂，胡克定律不再适用。

## 弹性张量

在三维连续介质中，应力 $$\sigma$$ 与应变 $$\epsilon$$ 均为二阶对称张量，各包含 9 个分量（3×3 矩阵）。由于对称性（ $$\sigma_{ij} = \sigma_{ji}$$， $$\epsilon_{kl} = \epsilon_{lk}$$），二者各自仅有 **6 个独立分量**。

应变张量示例：

$$
\epsilon = \begin{bmatrix}
\epsilon_{11} & \epsilon_{12} & \epsilon_{13} \\
\epsilon_{21} & \epsilon_{22} & \epsilon_{23} \\
\epsilon_{31} & \epsilon_{32} & \epsilon_{33}
\end{bmatrix}
$$

弹性常数 $$C$$ 为四阶张量，共有 81 个分量（3×3×3×3）。基于应力与应变张量的对称性，以及弹性势能的存在，弹性张量 $$C_{ijkl}$$ 满足以下对称关系：

1. **应力张量对称性**： $$C_{ijkl} = C_{jikl}$$
2. **应变张量对称性**： $$C_{ijkl} = C_{ijlk}$$
3. **弹性势能对称性**（源于应变能密度函数 $$U$$）：$$C_{ijkl} = C_{klij}$$

其中，弹性势能表达式为：

$$
U = \frac{1}{2} C_{ijkl} \epsilon_{ij} \epsilon_{kl}, \quad \sigma_{ij} = \frac{\partial U}{\partial \epsilon_{ij}}
$$

上述对称性使得 81 个分量中仅有 **21 个独立分量**。

例如， $$C_{1122} = C_{2211}$$ 表示沿 $$y$$ 方向拉伸引起 $$x$$ 方向应力响应的刚度，与沿 $$x$$ 方向拉伸引起 $$y$$ 方向应力响应的刚度相同，体现了能量互易性。其中$$C_{1122}$$ 描述的是在 y 方向（方向 2）施加拉伸应变 $$\epsilon_{22}$$，导致在 x 方向（方向 1）产生拉伸应力 $$\sigma_{11}$$的系数。$$C_{2211}$$描述的是在 x 方向（方向 1）施加拉伸应变 $$\epsilon_{11}$$，导致在 y 方向（方向 2）产生拉伸应力 $$\sigma_{22}$$的系数。这两个弹性张量相等表示无论先拉伸 x 还是 y 方向，储存的弹性能都是一样的。

对于各向同性材料，弹性张量可采用 **Voigt 标记法** 表示为 6×6 对称矩阵：

$$
\begin{bmatrix} \sigma_1 \\ \sigma_2 \\ \sigma_3 \\ \sigma_4 \\ \sigma_5 \\ \sigma_6 \end{bmatrix} = 
\begin{bmatrix} 
C_{11} & C_{12} & C_{13} & C_{14} & C_{15} & C_{16} \\ 
C_{12} & C_{22} & C_{23} & C_{24} & C_{25} & C_{26} \\ 
C_{13} & C_{23} & C_{33} & C_{34} & C_{35} & C_{36} \\ 
C_{14} & C_{24} & C_{34} & C_{44} & C_{45} & C_{46} \\ 
C_{15} & C_{25} & C_{35} & C_{45} & C_{55} & C_{56} \\ 
C_{16} & C_{26} & C_{36} & C_{46} & C_{56} & C_{66} 
\end{bmatrix}
\begin{bmatrix} \epsilon_1 \\ \epsilon_2 \\ \epsilon_3 \\ 2\epsilon_4 \\ 2\epsilon_5 \\ 2\epsilon_6 \end{bmatrix}
$$

该矩阵含 **21 个独立弹性常数**。

## 弹性模量

晶胞对应力的弹性形变响应由**弹性张量矩阵**表示。而在宏观上测量材料的弹性性质时，无数个微小晶粒随机取向组成一块多晶材料时，宏观上它通常表现为各向同性，由弹性模量表示，可以由弹性张量计算得到其近似值。

描述材料宏观弹性行为的常用模量：

- **杨氏模量 ** $$E$$：表征材料在单向拉伸或压缩时的刚度。
- **体积模量 ** $$K$$：表征材料在均匀静水压作用下的体积变形阻力。
- **剪切模量 ** $$G$$：表征材料在剪切应力作用下形状改变的阻力。
- **泊松比 ** $$\nu$$：无量纲参数，反映材料在单向拉伸时横向收缩与纵向伸长之比，通常在 0–0.5 之间。

这些参数之间存在严格的数学关联，共同构成材料弹性性能的核心表征体系。

对于多晶材料，宏观弹性模量可通过单晶弹性常数 $$C_{ij}$$ 近似预测，常用方法包括：

- **Voigt 近似**：假设各晶粒应变均匀，给出模量**上界**。
- **Reuss 近似**：假设各晶粒应力均匀，给出模量**下界**。
- **Hill 近似**：取 Voigt 与 Reuss 结果的平均值。

若采用 **Voigt 近似**，各模量计算公式如下：

$$
9K = (C_{11} + C_{22} + C_{33}) + 2(C_{12} + C_{23} + C_{31})
$$

$$
15G = (C_{11} + C_{22} + C_{33}) - (C_{12} + C_{23} + C_{31}) + 3(C_{44} + C_{55} + C_{66})
$$

$$
E = \frac{9KG}{3K + G}
$$

# 弹性张量的计算方法

核心流程是：对原始晶体施加一组已知的微小应变，经 DFT 计算获得相应的应力响应，最后通过线性拟合确定应力-应变关系中的弹性常数。

## 应变的表示

在连续介质力学中，晶体的均匀应变可由一个二阶对称张量描述：

$$
\varepsilon = \begin{bmatrix}
\varepsilon_{11} & \varepsilon_{12} & \varepsilon_{13} \\
\varepsilon_{21} & \varepsilon_{22} & \varepsilon_{23} \\
\varepsilon_{31} & \varepsilon_{32} & \varepsilon_{33}
\end{bmatrix}
$$

由于对称性 ( $$\varepsilon_{ij} = \varepsilon_{ji}$$)，独立的应变分量仅有 6 个。因此，常采用 **Voigt 记号** 将其表示为一个六维数组：

$$
\begin{bmatrix}
\epsilon_{1} \\ \epsilon_{2} \\ \epsilon_{3} \\ \epsilon_{4} \\ \epsilon_{5} \\ \epsilon_{6}
\end{bmatrix}
\equiv
\begin{bmatrix}
\varepsilon_{11} \\ \varepsilon_{22} \\ \varepsilon_{33} \\ 2\varepsilon_{23} \\ 2\varepsilon_{13} \\ 2\varepsilon_{12}
\end{bmatrix}
$$

其中：

- $$\epsilon_{1}, \epsilon_{2}, \epsilon_{3}$$ 对应沿 $x, y, z$ 方向的正应变。
- $$\epsilon_{4}, \epsilon_{5}, \epsilon_{6}$$ 对应剪切应变分量。**注意**：Voigt 记号中的剪切应变分量已包含系数 2，以确保应力-应变关系在矩阵形式下保持 $\boldsymbol{\sigma} = \mathbf{C} \boldsymbol{\epsilon}$ 的简洁形式（如 2.1 节所示）。

## 晶格应变施加方法

对初始晶格基矢 $$\{ \mathbf{a}_1, \mathbf{a}_2, \mathbf{a}_3 \}$$ 施加应变，即通过一个**变形梯度张量** $$\mathbf{F}$$ 对其进行线性变换：

$$
\mathbf{a}_i' = \mathbf{F} \cdot \mathbf{a}_i, \quad (i=1,2,3)
$$

变形梯度张量 $$\mathbf{F}$$ 与目标应变张量 $$\varepsilon$$ 通过**有限应变理论**相关联。在 Materials Project 的实践[3]及材料科学开源 python 库 `pymatgen` 的 `convert_strain_to_deformation` 函数中， $$\mathbf{F}$$ 通过求解以下**格林-拉格朗日应变**方程得到：

$$
\varepsilon = \frac{1}{2} (\mathbf{F}^T \mathbf{F} - \mathbf{I})
$$

式中 $$\mathbf{I}$$ 为单位矩阵。对于微小的弹性应变，此关系可简化为线性近似。

## 计算流程与线性拟合

为求解弹性张量 $$\mathbf{C}$$ 的 21 个独立分量，需构建足够数量的线性方程。标准步骤如下：

1. **设计应变组**：对 6 个独立的应变分量（ $$\epsilon_1$$至 $$\epsilon_6$$），分别施加一组不同大小、符号的微扰。通常为每个分量选取一组值，例如：$$\{-0.01, -0.005, +0.005, +0.01\}$$。可生成 $$4 \times 6 = 24$$ 个不同的应变状态。应变幅度需保持足够小（通常 <1%），以确保响应处于线性弹性范围内，同时又需足够大以克服 DFT 计算中的数值噪声。
2. **DFT 单点计算**：将上述每一个应变状态，通过 $$\mathbf{F}$$ 应用于初始晶格，构造出变形后的晶体结构。对每个结构进行 **DFT（或经典势函数）** relax 弛豫计算（通常仅弛豫原子位置，保持应变后的晶胞固定），并提取计算输出的**应力张量 **$$\sigma$$。
3. **构建方程组与拟合**：对于第 $$m$$ 个应变状态，广义胡克定律在 Voigt 记号下给出一个线性方程：

$$
\begin{bmatrix} \sigma_1 \\ \sigma_2 \\ \sigma_3 \\ \sigma_4 \\ \sigma_5 \\ \sigma_6
\end{bmatrix}_m = \begin{bmatrix}
C_{11} & C_{12} & \cdots & C_{16} \\
C_{12} & C_{22} & \cdots & C_{26} \\
\vdots & \vdots & \ddots & \vdots \\
C_{16} & C_{26} & \cdots & C_{66}
\end{bmatrix}
\begin{bmatrix} \epsilon_1 \\ \epsilon_2 \\ \epsilon_3 \\ \epsilon_4 \\ \epsilon_5 \\ \epsilon_6 \end{bmatrix}_m
$$
通过 24 个应变-应力数据对，我们可以构建一个超定的线性方程组。利用**最小二乘法**进行线性回归，即可最优地拟合出弹性常数矩阵 $$\mathbf{C}$$ 中的所有 21 个独立分量。

# 以计算 Mo 晶体弹性常量为例

本算例可以从 GitHub 仓库下载：[https://github.com/MCresearch/TEAS/tree/main/2025-Mo-ElasticConstants](https://github.com/MCresearch/TEAS/tree/main/2025-Mo-ElasticConstants)。

要执行本弹性常数计算流程，需预先安装以下依赖库与软件：pymatgen 用于生成应变构型与处理晶体结构；ASE (Atomic Simulation Environment) 用于精确的文件格式转换。若计划采用深度学习势函数（如 DeePMD）进行计算，则需使用已编译 deepmd-kit 接口的 ABACUS 版本，以支持基于机器学习的势函数计算。

## 步骤一：cell-relax 计算 bcc Mo 的平衡晶格结构

现在我们以用 ABACUS 3.8.3 版本数值原子轨道基组计算 Mo 体心立方晶格(body-centered cubic,bcc 结构)的弹性常数为例。首先建立 `relax` 文件夹，设置 `INPUT`、`STRU`、`KPT` 等文件 。

`INPUT` 文件设置如下：

```
INPUT_PARAMETERS
#Parameters (1.General)
suffix                  cell-relax
calculation             cell-relax
symmetry                1
cal_force               1
cal_stress              1
pseudo_dir              ../
orbital_dir             ../

#Parameters (2.Iteration)
ecutwfc                 100
scf_nmax                100
force_thr_ev            0.01
stress_thr              0.1
relax_nmax              100

#Parameters (3.Basis)
basis_type              lcao

#Parameters (4.Smearing)
smearing_method         gauss
smearing_sigma          0.015

#Parameters (5.Mixing)
mixing_type             broyden
mixing_beta             0.8
```

`STRU` 文件设置如下：

```yaml
ATOMIC_SPECIES
Mo  95.9500 Mo_ONCV_PBE-1.0.upf auto

LATTICE_CONSTANT
1.8897259886

LATTICE_VECTORS
3.1556765866  -0.0000000000 -0.0000000000
-0.0000000000  3.1556765866 -0.0000000000
-0.0000000000 -0.0000000000  3.1556765866

ATOMIC_POSITIONS
Direct
Mo #label
0.0000   #magnetism
2 #number of atoms
1.0000000000 0.0000000000 0.0000000000 m 1 1 1
0.5000000000 0.5000000000 0.5000000000 m 1 1 1
```

在进行变胞弛豫（`cell-relax`）计算时，需注意以下关键设置以保证计算结果的有效性和准确性：

- **计算类型选择**：必须使用 `cell-relax`（而非仅原子弛豫的 `relax`），以同时优化晶格常数与原子位置，从而获得精确的平衡晶胞参数
- **应力计算开关**：在 `INPUT` 文件中必须设置 `cal_stress 1`，否则程序不会计算并输出应力矩阵。
- **收敛阈值设置**：建议将 `stress_thr` 设为更严格的值（例如 0.1 kbar，默认值为 0.5 kbar），以获得更精确的平衡晶格结构。
- **收敛性检查**：部分 ABACUS 版本中，若未设置 `relax_nmax`（最大离子弛豫步数），其默认值可能仅为 1 步。对于某些难以收敛的构型，必须确认结构优化已完全收敛。可通过检查输出文件中是否存在 `Relaxation is converged!` 关键字进行验证。

## 步骤二：生成 24 个应变结构

准备 `INPUT`、`KPT` 输入文件（注意事项见 4.3 节）后，在算例目录下，执行以下命令将自动完成应变构型的生成，并生成 `task.000`~`task.023` 共 24 个含有 `INPUT`、`STRU`、`KPT` 的执行文件夹：

```bash
python gene_dfm.py abacus
```

具体地，该脚本生成应变结构的细节如下

1. 读取初始结构：通过 `dpdata` 库自动读取 `./relax/OUT.*/STRU_ION_D` 目录下的 ABACUS 弛豫后结构。
2. 生成应变构型：调用 `pymatgen` 的 `DeformedStructureSet` 类，为独立的 6 个应变分量分别施加一组预设的应变值，共生成 24 个 变形后的晶体结构。这些结构以 `pymatgen` 的 `Structure` 对象格式暂存。在 `dfm_ss.deformed_structures` 列表中即储存了所有变形结构。
3. 写 `STRU` 结构文件：在 `dfm_ss` 中生成的变形结构以 `pymatgen` 的 `Structure` 对象格式储存，可直接通过 `pymatgen` 的内置方法便捷地输出为 VASP 格式的 `POSCAR` 文件。而为了适配 ABACUS 计算，需要将其进一步转换为 `STRU` 格式。虽然可利用 `dpdata` 等 Python 库实现格式转换，但需特别注意：**dpdata** 在读取 **POSCAR** 时会自动将晶格矢量转换为下三角矩阵，而读取 ABACUS **STRU** 时则保持原样**。这种标准化操作虽不改变结构本身，但会改变晶格基矢的 `x`、`y`、`z` 方向。由于弹性张量与应力-应变关系均基于特定坐标系定义，这种方向的改变将直接导致后续拟合得到的弹性常数矩阵出现错误。为此，本算例中的脚本用 `ase.io` 库进行文件读写，该库在格式转换过程中能保持晶格方向不变，从而确保了弹性张量计算的正确性。

## 步骤三：结构优化求应力

生成应变构型后，需对每个结构执行**固定晶胞的结构优化**，以计算其在当前应变状态下的平衡构型与对应的应力张量。

**具体操作流程如下：**

1. **准备输入文件**：在运行 `python gene_dfm.py abacus` 命令之前，需准备好 ABACUS 的 `INPUT` 输入文件。`gene_dfm.py` 脚本将自动将此 `INPUT` 文件复制到所有（24 个）应变构型的计算任务目录中。
2. **执行结构优化计算**：执行 `bash run_sub.sh` 脚本会为每个应变构型提交一个结构优化任务。此计算的目的是**在固定晶胞形状的前提下，弛豫原子位置至受力平衡**。

**关键注意事项：**

1. 务必执行 **relax**（原子位置弛豫），而非 `cell-relax`（晶胞弛豫）或 `scf`（单点自洽）计算。只有 `relax` 计算才能在固定应变下得到平衡的原子构象和对应的准确应力。
2. **收敛性检查**：不同版本的 ABACUS 中，`relax_nmax` 参数的默认值可能不同。必须严格检查每个任务的几何弛豫是否完全收敛，未收敛的应力数据将导致弹性常数拟合错误。**推荐的收敛检查方法：**在计算根目录下执行以下命令，检查输出中是否包含收敛关键字：

```bash
grep “Relaxation is converged!” */OUT.*/running_*
```

一个成功的检查结果应显示所有任务目录（`relax` 及 `task.000` 至 `task.023`）中均存在该收敛信息。若缺失，则表明对应任务未收敛，需要调整 `INPUT` 中的收敛阈值或增加最大迭代步数后重新计算。

## 步骤四：计算弹性张量

结构优化计算全部完成后，在算例目录下运行脚本进行弹性张量的计算 `python compute_dfm.py abacus`

计算完后屏幕将输出弹性张量 voight 形式矩阵、体积模量、剪切模量、杨氏模量、泊松比，并储存在 elastic.json 文件中。最终输出如下：

```
# Elastic Constants in GPa
 464.80  153.08  153.08    0.00    0.00    0.00
 153.08  464.80  153.08    0.00    0.00    0.00
 153.08  153.08  464.80    0.00    0.00    0.00
   0.00    0.00    0.00   98.77    0.00    0.00
  -0.00   -0.00   -0.00    0.00   98.77    0.00
  -0.00   -0.00   -0.00    0.00    0.00   98.77
# Bulk   Modulus BV = 256.99 GPa
# Shear  Modulus GV = 121.60 GPa
# Youngs Modulus EV = 315.11 GPa
# Poission Ratio uV = 0.30
```

Mo 晶体弹性常数计算结果对比：

| | BV | C11 | C12 | C44 |
|:---|:---|:---|:---|:---|
| Exp[2] | 264 | 466 | 163 | 110 |
| DFT | 257 | 465 | 153 | 99 |
| DPA-2势函数[1] | 259 | 479 | 149 | 83 |

# 参考资料

1. Zhang, D., Liu, X., Zhang, X. _et al._ DPA-2: a large atomic model as a multi-task learner. _npj Comput Mater_ 10, 293 (2024). [https://doi.org/10.1038/s41524-024-01493-2](https://doi.org/10.1038/s41524-024-01493-2)
2. D. L. Davidson and F. R. Brotzen, Journal of Applied Physics 39, 5768 (1968), ISSN 0021-8979
3. [Elastic Constants | Materials Project Documentation](https://docs.materialsproject.org/methodology/materials-methodology/elasticity)
4. 知乎的相关讨论：[https://zhuanlan.zhihu.com/p/1956305783714210045](https://zhuanlan.zhihu.com/p/1956305783714210045)
