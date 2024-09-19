# ABACUS+pymatgen 计算弹性常数

<strong>作者：陈涛，邮箱：chentao@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2024/07/11</strong>

# 一、介绍

本教程旨在描述如何采用 ABACUS 来计算材料体系的弹性常数（elastic constants）。弹性常数是表征材料弹性的量，也是材料的重要力学性质，可以通过原子尺度模拟计算获得，例如通过密度泛函理论或者原子间的势函数方法。在晶体结构预测辅助的新材料计算设计中，弹性常数常用于检查结构的稳定性。

在晶体的线弹性范围内，应力$$\boldsymbol{\sigma}$$和相应应变$$\boldsymbol{\varepsilon}$$之间的关系符合胡克定律，$$\boldsymbol{\sigma=C\varepsilon},\sigma_{ij}=C_{ijkl}\varepsilon_{kl}$$，其中$$i,j,k,l$$是笛卡尔指标（$$x,y,z$$），$$C_{ijkl}$$即为弹性常数。

由于$$\boldsymbol{\sigma}$$和$$\boldsymbol{\varepsilon}$$均是对称张量，基于 [Voigt 表示法](https://en.wikipedia.org/wiki/Voigt_notation)：$$xx\mapsto1,yy\mapsto2,zz\mapsto3,yz\mapsto4,xz\mapsto5,xy\mapsto6$$，则：$$\sigma_1=\sigma_{xx},\sigma_2=\sigma_{yy},\sigma_3=\sigma_{zz},\sigma_4=\sigma_{yz},\sigma_5=\sigma_{xz},\sigma_6=\sigma_{xy}$$

$$
\epsilon_1=\epsilon_{xx},\epsilon_2=\epsilon_{yy},\epsilon_3=\epsilon_{zz},\epsilon_4=\epsilon_{yz},\epsilon_5=\epsilon_{xz},\epsilon_6=\epsilon_{xy}
$$

此时，$$C_{xxxx}\mapsto C_{11},C_{xxyy}\mapsto C_{12},.....$$

$$
\begin{bmatrix}\sigma_{1}\\\sigma_{2}\\\sigma_{3}\\\sigma_{4}\\\sigma_{5}\\\sigma_{6}\end{bmatrix}=\begin{bmatrix}C_{11}&C_{12}&C_{13}&C_{14}&C_{15}&C_{16}\\C_{12}&C_{22}&C_{23}&C_{24}&C_{25}&C_{26}\\C_{13}&C_{23}&C_{33}&C_{34}&C_{35}&C_{36}\\C_{14}&C_{24}&C_{34}&C_{44}&C_{45}&C_{46}\\C_{15}&C_{25}&C_{35}&C_{45}&C_{55}&C_{56}\\C_{16}&C_{26}&C_{36}&C_{46}&C_{56}&C_{66}\end{bmatrix}\begin{bmatrix}\epsilon_{1}\\\epsilon_{2}\\\epsilon_{3}\\2\epsilon_{4}\\2\epsilon_{5}\\2\epsilon_{6}\end{bmatrix}
$$

如果我们通过施加应变$$\varepsilon_i$$使晶体变形并计算相应的应力，则可以从方程中获得弹性常数。晶体晶胞上的变形矩阵为$$\boldsymbol{D=I+\varepsilon}$$，其中$$\boldsymbol{I}$$是 3*3 的单位矩阵，$$\boldsymbol{\varepsilon}$$是 Voigt 表示法中的应变矩阵。

在 3 维晶体中，应变矩阵为 $$\boldsymbol{\varepsilon}=\left[\begin{array}{lrr}
\varepsilon_{1} & \varepsilon_{6} & \varepsilon_{5} \\
\varepsilon_{6} & \varepsilon_{2} & \varepsilon_{4} \\
\varepsilon_{5} & \varepsilon_{4} & \varepsilon_{3}
\end{array}\right]$$，在2维平面晶体中，应变矩阵为$$\boldsymbol{\varepsilon}=\left[\begin{array}{lrr}
\varepsilon_{1} & \varepsilon_{6} & 0\\
\varepsilon_{6} & \varepsilon_{2} & 0 \\
0 & 0 & 0
\end{array}\right]$$。

变形后，晶格矢量为$$\boldsymbol{A'=A \cdot D}$$，其中$$\boldsymbol{A}$$是初始的晶格矢量。

在实际计算中，6 种应变状态将逐一应用于初始弛豫（relaxation）后的结构，因此每次只考虑一种独立变形。对于 6 种应变状态中的每一种，应用 4 种不同的默认应变大小：$$\varepsilon_i\in\{-0.01,-0.005,0.005,0.01\}$$，将产生 24 种构型。接着对这 24 种构型分别使用 DFT 计算（固定晶格矢量，但允许原子弛豫，即 `relax`），对所获得的每种应变状态的 4 个应力和应变的集合使用线性拟合来计算相应的弹性常数。

更多细节可以参考：[Elastic Constants | Materials Project Documentation](https://docs.materialsproject.org/methodology/materials-methodology/elasticity)

# 二、准备

## 1. 下载例子

首先可以下载一个 ABACUS 的计算实例，可以从 Gitee 上[下载](https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/elastic)。具体来说，可以通过在网页右侧点击克隆/下载-> 下载 ZIP 得到算例，或者在 linux 终端执行如下命令得到算例：

```bash
git clone https://gitee.com/mcresearch/abacus-user-guide.git
```

下载后解压，之后进入 `abacus-user-guide/examples/elastic` 文件夹

里面有 `relax` 文件夹，为 8 原子金刚石的算例，周期性边界条件。

此外，`gene_dfm.py` 和 `compute_dfm.py` 为计算弹性常数使用的 python 脚本。

`run_task.sh` 和 `sub.sh` 为批量运行 abacus 计算的 shell 脚本，`INPUT`、`KPT`、`C_ONCV_PBE-1.0.upf` 和 `C_gga_7au_100Ry_2s2p1d.orb` 为运行 abacus 计算所需的输入文件。

## 2. 下载并安装 pymatgen

Python Materials Genomics (pymatgen，[https://pymatgen.org/](https://pymatgen.org/))是一个 API 包，该软件可以与 materials project 结合进行高通量计算。该软件包是由加州大学圣地亚哥雅各布斯工程学院的纳米工程教授 Shyue Ping Ong 和他的材料虚拟实验室(Materials Virtual Lab)团队开发并维护的程序。

在本教程里会用到 pymatgen 来计算弹性常数，此外还会用到 [dpdata](https://github.com/deepmodeling/dpdata/)，monty，numpy 这三个库，可以使用如下命令安装：

```bash
pip install monty numpy dpdata pymatgen
```

弹性常数所用方法相关文档：[https://pymatgen.org/pymatgen.analysis.elasticity.html](https://pymatgen.org/pymatgen.analysis.elasticity.html)

# 三、金刚石的弹性常数计算

## 1. 结构弛豫

进入 `relax` 文件夹，运行 ABACUS 进行结构弛豫，完成后在 `OUT.C8` 文件夹下出现 `STRU_ION_D` 文件。之后的应变都将在这个构型文件基础上产生。此外，计算弹性常数所用的应力也会减去这个构型的应力，因此也需要 `running_relax.log` 输出应力

## 2. 产生应变构型

回到例子根目录，执行如下命令：

```bash
python gene_dfm.py abacus
```

默认应变的大小（代表晶格常数的倍数，例如 0.01，其形变量是 1%）如下，对应 `gene_dfm.py` 的 41-42 行：

```python
norm_strains = [-0.010, -0.005, 0.005, 0.010]
shear_strains = [-0.010, -0.005, 0.005, 0.010]
```

将会产生 `task.000` 到 `task.023` 共 24 个文件夹，分别对应第一节所说的 24 种构型。进入任意 task 文件夹，其中会有 `INPUT`、`KPT`、`STRU` 和 `strain.json` 四个文件。

其中 `INPUT` 和 `KPT` 拷贝自例子根目录下的 `INPUT` 和 `KPT`，由于使用的赝势和轨道文件放在例子根目录下，所以 `pseudo_dir` 和 `orbital_dir` 均设置为 `../`。此外需要进行固定晶格矢量，但允许原子弛豫来计算应力，因此 `calculation` 设置为 `relax`。`STRU` 和 `strain.json` 分别是生成的构型文件和相应的应变大小。

## 3. 计算应力

分别进入上述 task 文件夹，运行 abacus 计算相应构型的应力。也可以使用例子根目录下的 `run_task.sh` 脚本，但要注意根据实际修改其和 `sub.sh` 的内容。

## 4. 计算弹性常数

回到例子根目录，执行如下命令：

```bash
python compute_dfm.py abacus
```

屏幕输出如下：

```bash
# Elastic Constants in GPa
1043.31  107.39  107.39    0.00    0.00    0.00 
 107.39 1043.31  107.39    0.00    0.00    0.00 
 107.39  107.39 1043.31    0.00    0.00    0.00 
   0.00   -0.00   -0.00  557.05    0.00    0.00 
  -0.00   -0.00   -0.00    0.00  557.05    0.00 
   0.00    0.00    0.00    0.00    0.00  557.05 
# Bulk   Modulus BV = 419.37 GPa
# Shear  Modulus GV = 521.42 GPa
# Youngs Modulus EV = 1105.91 GPa
# Poission Ratio uV = 0.06
```

第 2 到 7 行即为计算的各种弹性常数（单位：GPa），分别是体弹性模量（Bulk Modulus）、剪切模量（Shear Modulus）、杨氏模量（Youngs Modulus）和泊松比（Poission Ratio）。精度更高的计算结果存储在 `elastic.json` 内。

以下是常用的几个弹性常数相关的名词解释：

<strong>弹性模量（Bulk Modulus）：</strong>指当有力施加于物体或物质时，其弹性变形（非永久变形）趋势的数学描述。物体的弹性模量定义为弹性变形区的应力-应变曲线的斜率。

<strong>杨氏模量（Young's Modulus）：</strong>是材料力学中的名词，一般将杨氏模量习惯称为弹性模量。弹性材料承受正向应力时会产生正向应变，在形变量没有超过对应材料的一定弹性限度时，定义正向应力与正向应变的比值为杨氏模量。杨氏模量的大小标志了材料的刚性，杨氏模量越大，越不容易发生形变。大部分金属在合金成分不同、热处理在加工过程中的应用，其杨氏模量值会有 5％或更大的波动。

<strong>剪切模量（Shear Modulus）：</strong>又称刚度模量，描述材料在剪切力作用下抵抗形变的能力，即物体形变的大小与作用的剪切应力之间的关系。

<strong>泊松比（Poisson's Ratio）：</strong>当材料在一个方向被压缩，它会在与该方向垂直的另外两个方向伸长，这就是泊松现象，泊松比是用来反映泊松现象的无量纲的物理量。泊松比一般是正值，表示在一方向拉伸后，在其他方向收缩。不过也存在泊松比为零（在一方向拉伸后，在其他方向的尺寸不变），其至为负的材料。
