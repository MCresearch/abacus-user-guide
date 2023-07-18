# 数值原子轨道（一）：ABACUS 中的数值原子轨道命名和使用方法

<strong>作者：梁馨元，邮箱：2201111875@stu.pku.edu.cn </strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/07/18</strong>

# 1. 数值原子轨道的背景知识

## 1.1 数值原子轨道

对电子结构的求解可以在不同的表象下进行，电子的波函数以及势函数也可以在不同基矢量下表示，常用的有平面波和局域轨道等。LCAO（Linear Combination of Atomic Orbitals）方法就是通过局域的原子轨道来求解量子力学问题。其中局域轨道的选取方式有多种，例如高斯轨道（Gaussian type Orbitals，GTOs 或 Gaussians）、数值原子轨道（Numerical Atomic Orbitals）、万尼尔函数（Wannier Functions）等。

## 1.2 数值原子轨道作为基矢量的优点

数值原子轨道作为基矢量有几个优点：第一，基矢量个数相比于一些常用的基矢量（例如平面波和实空间网格）大幅度降低；第二，数值原子轨道是局域的，空间上可以严格截断，采用数值原子轨道来构建体系的哈密顿量的效率可以达到线性标度的时间复杂度。

## 1.3 构造数值原子轨道基组的几种方案

构造精度高、可系统提升数量、可移植性好的原子轨道基组颇有挑战，因此也有多种方案被提出。例如，Junquera 等人提出在一维薛定谔方程中加入不同形式的约束势场，从而求解出具有严格截断的数值原子轨道[1]。Ozaki 在 OpenMX 软件中采用变分的方法来优化局域轨道的形状，从而得出一组最优的数值原子轨道[2]。Volker 等人提出在一个大的局域轨道基组中挑选最合适的局域轨道组成不同等级的基组轨道，该方案用于全电子密度泛函理论软件 FHI-aims 中[3]。Chen 等人提出利用前人提出的溢出函数（Spillage function）[4-5]来构造可系统提高数量的数值原子轨道，其中每个轨道都由一组球贝塞尔函数作为基矢量展开，该轨道被用在 ABACUS（原子算筹）软件中[6]。

# 2. 数值原子轨道的命名方法

## 2.1 数值原子轨道的组成

数值原子轨道（Numerical Atomic Orbitals，简称 NAO）是目前在 ABACUS 程序中支持的一种基矢量。从数学形式上来看，数值原子轨道可以分解为径向函数 flζ 和球谐函数 Ylm 的乘积。

$$
\phi_{l m \zeta}(\mathbf{r})=f_{l \zeta}(r) Y_{l m}(\hat{r}),
$$

其中 `l` 是角量子数，`m` 是磁量子数，`ζ` 代表了每个角量子数上对应的多个径向轨道，实际计算中通常采用多于 1 个轨道来增加基矢量的完备性。

## 2.2 数值原子轨道的命名方法

数值原子轨道有一套常用的命名方案用来表示选取的基组大小，早期该命名方案在 SIESTA 软件中被采用[7][8][9][10]，后来在 OpenMX、FHI-aims 和 ABACUS 中也采取这套命名方案。具体来说是，对于每个被电子占据的角量子数 `l`，若采用 1 条径向轨道，则称该基组为 `Single-ζ` 轨道，简称 `SZ` 轨道基组。若采用 2 条径向轨道，则称该基组为 `Double-ζ` 轨道，简称 `DZ` 轨道基组。

目前，在许多赝势结合数值原子轨道的程序里，通常会在 `DZ` 轨道的基础上引入 1 条极化（polar）的径向轨道，即角量子数更高的轨道，来组成 `DZP（Double-ζ valence orbitals plus SZ polarization）` 轨道基组。此外，还有基组数量更大的 `TZDP（Triple-ζ valence orbitals plus DZ polarization）` 轨道等。

## 2.3 数值原子轨道基组的个数

数值原子轨道基组的具体个数除了取决于轨道类别（比如 SZ、DZP、TZDP）外，也取决于元素种类、所选取的赝势。

<strong>轨道类别：</strong>比如对于 O 元素的赝势而言，一般将两个 1s 电子作为核内电子，在构造赝势的时候只考虑它的外层 6 个价电子部分 2s、2p 轨道，则该 O 赝势下的电子的极化轨道为 d 轨道。故它的 SZ（Single-ζ）轨道包含 1 组 s 轨道、1 组 p 轨道，共 1\*1+1\*3=4 个轨道；DZP 轨道包含 2 组 s 轨道、2 组 p 轨道、1 组 d 轨道，共包含 2\*1+2\*3+1\*5=13 个轨道；TZDP 轨道包含 3 组 s 轨道、3 组 p 轨道、2 组 d 轨道，共包含 3\*1+3\*3+2\*5=22 个轨道。

<strong>元素种类：</strong>比如同为 DZP 轨道，对于 H 元素（1 个价电子）即为 2 组 s 轨道、1 组 p 轨道（p 轨道也是 H 的极化轨道），共包含 2\*1+1\*3=5 个轨道。对于 O 元素即为 2 组 s 轨道、2 组 p 轨道、1 组 d 轨道，共包含 2\*1+2\*3+1\*5=13 个轨道。

<strong>赝势：</strong>比如对于 Fe 元素而言，同为 DZP 轨道。若选取的赝势为，$$[Ne]3s^23p^64s^23d^6$$，即$$[Ne]=1s^22s^22p^6$$部分为芯电子，$$3s^23p^64s^23d^6$$部分为 16 个价电子，则 DZP 轨道包含 2\*2 套 s 轨道（3s 和 4s）、2 套 p 轨道（3p）、2 套 d 轨道（3d）、1 套 f 轨道（极化轨道），即每个原子的 DZP 数值原子轨道个数为 2\*2\*1+2\*3+2\*5+1\*7=27 个轨道。若选取的赝势为$$[Ar]4s^23d^6$$，则 DZP 轨道包含 2 套 s 轨道、2 套 d 轨道、1 套 p 轨道，共 2\*1+2\*5+1\*3=15 个轨道。

# 3. ABACUS 中数值原子轨道的使用方法

## 3.1 ABACUS 中的数值原子轨道文件

ABACUS 提供了已经生成好的数值原子轨道库打包文件供下载（[官网下载链接](http://abacus.ustc.edu.cn/pseudo/list.htm)），对于绝大多数计算任务，这些数值原子轨道是经过精度和可靠性验证，可以直接使用的。这些轨道文件的开头提供了关于该轨道的重要信息。以 `O_gga_7au_100Ry_2s2p1d.orb` 轨道文件为例，首先文件名包含的信息有：氧元素（o），GGA 泛函（gga），数值原子轨道截断半径（7au，即 7 Bohr），推荐能量截断值（100 Ry），数值原子轨道个数（2s2p1d，2 个 s 的径向轨道，2 个 p 的径向轨道，1 个 d 的径向轨道）。值得注意的三个点是：

- <strong>ABACUS 里用到的模守恒赝势和轨道是需要匹配的</strong>。因为不同的赝势可能有不同的价电子，而数值原子轨道是用来描述这些价电子的，如果赝势的价电子多，则相应的默认数值原子轨道基组数量也会增多。
- <strong>推荐用户直接使用轨道文件包含的能量截断值做计算</strong>。ABACUS 里的数值原子轨道在生成时，是尽量的去匹配平面波输出的波函数，从而优化得到的。而平面波计算是有一个能量截断值的，因此为了尽可能的保证 LCAO 的精度，我们建议直接使用推荐的能量截断值，而不需要真正做计算的时候做体系能量随着能量截断值变化的收敛性测试。当你在 LCAO 计算时改变能量截断值时候，其实只是改变了平面波的个数，这些平面波是用来做一些数值计算的，本质上并没有改变基矢量的个数，而基矢量的个数增加是靠改变基组大小，例如 DZP 到 TZDP 来实现的。
- <strong>特殊情况可以自己生成数值原子轨道。</strong>如果用户有自己特殊的赝势，或者对目前提供的原子轨道的参数或者个数感觉不满意，例如对于导带的描述能力较差，也可以自己生成数值原子轨道，具体生成的方法可以参考这个系列文档的第二和第三篇。

打开以上提到的氧的数值原子轨道文件，文件的开头如下：

```bash
---------------------------------------------------------------------------
Element                     O
Energy Cutoff(Ry)           100
Radius Cutoff(a.u.)         7
Lmax                        2
Number of Sorbital-->       2
Number of Porbital-->       2
Number of Dorbital-->       1
---------------------------------------------------------------------------
SUMMARY  END
```

这里包括元素种类（`Element`），生成轨道时指定的截断能量值（`Energy Cutoff`）、截断半径（`Radius Cutoff`），最大角量子数（`L``max`）及各角量子数轨道的个数（`Number of *`` ``orbital`，*为 S、P、D 等轨道角动量）。根据这些信息可以知道该轨道的类别，比如该举例文件即包含 O 的 DZP 轨道。

上述 ABACUS 提供的数值原子轨道文件中，在取名中即包含文件开头的重要信息，包括各角量子数的轨道个数。由这些轨道的文件名即可判断轨道类型。

轨道文件中包含的后续内容为不同类型、不同角量子数（L）的多个径向数值原子轨道（即不同 N）的具体数据，目前轨道是存在均匀格点上的，之后有可能也会支持非均匀格点。

## 3.2 如何选择数值原子轨道文件

用户需要根据精度要求，选择数值原子轨道合适的截断能量值、截断半径及轨道类型。截断能量值、截断半径越大，轨道类型提升（SZ、DZP、TZDP），精度越高，结果更接近平面波。注意对于不同元素，要达到同样的精度，以上数值设置并不一定相同。

## 3.3 如何修改数值原子轨道文件的设置，获得低精度轨道类型文件

在 ABACUS 中生成数值原子轨道文件时，可以设置同时生成多种精度的轨道文件，即设置 `SIAB_INPUT` 文件中的参数 Save Orbitals，详见篇目（三）。

如果已有一份数值原子轨道文件，但希望直接用此文件进行低精度计算，比如希望使用 DZP 轨道文件进行 SZ 计算。可以修改文件开头的信息实现，具体是 `Lmax` 及各角量子数轨道个数，将这些参数调整到低精度计算对应的数值。文件的后续内容不需要做更改。

比如对于 O 元素而言，DZP 轨道文件参数如 3.1 所示，若要进行 `SZ` 基矢量的计算，则将 `L``max` 设置为 1，`Number of Sorbital/Porbital/Dorbital=1/1/0` 即可。

# 4. 参考文献

[1] J. Junquera, Ó. Paz, D. Sánchez-Portal, and E. Artacho, <em>Numerical Atomic Orbitals for Linear-Scaling Calculations</em>, Phys. Rev. B, <strong>64</strong>, 235111 (2001).

[2] T. Ozaki, <em>Variationally Optimized Atomic Orbitals for Large-Scale Electronic Structures</em>, Phys. Rev. B, <strong>67</strong>, 155108 (2003).

[3] V. Blum, R. Gehrke, F. Hanke, P. Havu, V. Havu, X. Ren, K. Reuter, and M. Scheffler, <em>Ab Initio Molecular Simulations with Numeric Atom-Centered Orbitals</em>, Comput. Phys. Commun., <strong>180</strong>, 2175 (2009).

[4] M. Chen, G.-C. Guo, and L. He, <em>Systematically Improvable Optimized Atomic Basis Sets for Ab Initio Calculations</em>, J. Phys.: Condens. Matter, <strong>22</strong>, 445501 (2010).

[5] M. Chen, G.-C. Guo, and L. He, <em>Electronic Structure Interpolation via Atomic Orbitals</em>, J. Phys.: Condens. Matter, <strong>23</strong>, 325501 (2011).

[6] Liu Xiao-Hui et al., <em>Introduction to first-principles simulation package ABACUS based on systematically improvable atomic orbitals</em>, Acta Phys. Sin., <strong>64</strong>, 187104 (2015).

[7] Sánchez‐Portal D, Ordejon P, Artacho E, et al. <em>Density‐functional method for very large systems with LCAO basis sets</em>, J. International Journal of Quantum Chemistry, <strong>65</strong>, 453-461 (1997).

[8] Artacho E, Sánchez‐Portal D, Ordejón P, et al. <em>Linear‐scaling ab‐initio calculations for large and complex systems</em>, J. Physica Status Solidi (b), <strong>215</strong>, 809-817 (1999).

[9] Junquera J, Paz Ó, Sánchez-Portal D, et al. Numerical atomic orbitals for linear-scaling calculations, J. Physical Review B, <strong>64</strong>, 235111 (2001).

[10] Soler J M, Artacho E, Gale J D, et al. The SIESTA method for ab initio order-N materials simulation, J. Phys.: Condens. Matter, <strong>14</strong>, 2475 (2002).
