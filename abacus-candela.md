# ABACUS+Candela 使用教程

<strong>作者：陈涛，邮箱：chentao@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/08/23</strong>

# 一、介绍

本教程旨在介绍采用 Candela 分析 ABACUS（基于 3.2.4 版本）分子动力学轨迹，计算径向分布函数（Radial Distribution Function，简称 RDF），静态结构因子（Static Structure Factor，简称 SSF），离子-离子动态结构因子（Ion-ion Dynamic Structure Factor，简称 DSF）以及均方差位移（Mean Square Displacement，简称 MSD）流程。

上述性质的具体描述可以参考：[Qianrui Liu <em>et al</em> 2020 <em>J. Phys.: Condens. Matter</em> <strong>32</strong> 144002](https://iopscience.iop.org/article/10.1088/1361-648X/ab5890)，径向分布函数（RDF）见文中公式（12），静态结构因子（SSF）见公式（13），离子-离子动态结构因子（DSF）见公式（15，16，17）以及均方差位移（MSD）见公式（18）。

Candela 全称 Collection of ANalysis DEsigned for Large-scale Atomic simulations，目前支持分析 QE、ABACUS、LAMMPS 和 VASP 的分子动力学轨迹，Github 主页：[https://github.com/MCresearch/Candela](https://github.com/MCresearch/Candela)

# 二、准备

## 1. 下载并安装 Candela

```bash
git clone https://github.com/MCresearch/Candela.git
cd Candela
make -j4 #使用intel oneapi编译器
```

若使用 Intel Oneapi 编译器，按照上述流程操作，在编译完成后即可在 `bin` 目录下看到 `candela` 可执行文件

若使用其他编译器，需要按照 `Candela` 目录下 `Makefile.vars` 修改相应的 CXX

## 2 下载例子

可以从 Gitee 上[下载](https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/candela)。在网页右侧点击克隆/下载-> 下载 ZIP 得到算例，或者在 linux 终端执行如下命令得到算例：

```
git clone https://gitee.com/mcresearch/abacus-user-guide.git
```

下载完成后解压，之后进入 `abacus-user-guide/examples/candela` 文件夹

算例中包含 `RDF`、`SSF`、`DSF`、`MSD` 四个文件夹和 `MD_dump` 文件。其中 `MD_dump` 是 32 原子的铝的 MD 轨迹

# 三、流程

## 1 计算径向分布函数

进入 `RDF` 文件夹，`INPUT` 文件即为 Candela 的输入文件，具体如下：

```bash
calculation  pdf
geo_in_type  ABACUS
geo_directory  ../MD_dump
geo_1        0
geo_2        100
geo_interval 2
geo_ignore   50
geo_out      Al_rdf.txt

ntype        1
natom        32
rcut         2.3
dr           0.01
```

以上参数在 Candela 的[线上文档](https://candela-docs.readthedocs.io/en/latest/)中均有详细说明，这里再进行简单概述：

- calculation：设置为 pdf（Pair Distribution Function）即计算径向分布函数
- geo_in_type：读取的 MD 轨迹的格式，目前支持分析 pw.x（QE2），cp.x（QE），ABACUS（ABACUS）、LAMMPS（LAMMPS）和 VASP（VASP）
- geo_directory：MD 轨迹的位置
- geo_1：MD 轨迹起始的索引
- geo_2：MD 轨迹结束的索引
- geo_interval：Candela 读取 MD 轨迹的间隔
- geo_ignore：需要跳过的 MD 轨迹帧数
- geo_out：输出的文件名，默认为 result.dat
- ntype：原子种类
- natom：原子数
- rcut：计算 RDF 的截断半径，一般取晶格的一半，单位为 Angstrom
- dr：计算 RDF 的 r 的间隔，单位为 Angstrom

执行如下命令：

```bash
mpirun -n 2 candela
```

即可得到 RDF，输出到 `Al_rdf.txt`，其中第一列为 r，单位为 Angstrom，第二列即为对应的 RDF，第三列为对第二列积分的结果。

## 2 静态结构因子

进入 `SSF` 文件夹，`INPUT` 文件具体如下：

```bash
calculation   ssf           
geo_in_type   ABACUS
geo_directory ../MD_dump
geo_1         0
geo_2         100
geo_interval  2
geo_ignore    50

ssf_out       Al_ssf.txt
ntype         1
natom         32
struf_dgx     1.32656
struf_dgy     1.32656
struf_dgz     1.32656
struf_ng      6
```

以上参数在 Candela 的[线上文档](https://candela-docs.readthedocs.io/en/latest/)中均有详细说明，这里再进行简单概述：

- calculation：设置为 ssf，即计算静态结构因子
- ssf_out：输出的文件名
- struf_dgx：倒空间中的间隔，一般取 $$2\pi/a$$，其中a为x方向的晶格长度，单位为$$\mathrm{Angstrom^{-1}}$$
- struf_dgy：一般取 $$2\pi/b$$，其中b为y方向的晶格长度，单位为$$\mathrm{Angstrom^{-1}}$$
- struf_dgz：一般取 $$2\pi/c$$，其中c为z方向的晶格长度，单位为$$\mathrm{Angstrom^{-1}}$$
- struf_ng：上述倒空间中的间隔的数量

执行如下命令：

```bash
mpirun -n 2 candela
```

即可得到 SSF，输出到 `Al_ssf.txt`（原始的计算结果）以及 `sm-Al_ssf.txt`（平滑的计算结果），其中第一列为 q，单位为$$\mathrm{Angstrom^{-1}}$$，第二列即为对应的 SSF。

## 3 离子-离子动态结构因子

进入 `DSF` 文件夹，离子-离子动态结构因子需要对中间散射函数（Intermediate Scattering Function）进行傅里叶变换得到，因此需要先计算中间散射函数，`INPUT` 文件具体如下：

```bash
calculation     isf2
geo_in_type     ABACUS
geo_directory   ../MD_dump
geo_1           50
geo_2           100
geo_interval    1

isf_outfile     isf.txt
ntype           1
natom           32
isf_nt1         11
isf_nt2         40
dt_snapshots    0.00006

isf_target_q    2.65
isf_dgx         1.32656
isf_dgy         1.32656
isf_dgz         1.32656
isf_ngx         6
isf_ngy         6
isf_ngz         6
```

以上参数在 Candela 的[线上文档](https://candela-docs.readthedocs.io/en/latest/)中均有详细说明，这里再进行简单概述：

- calculation：设置为 isf2，即计算中间散射函数
- isf_outfile：输出的文件名
- isf_nt1：中间散射函数的时间长度
- isf_nt2：用于平均中间散射函数的时间长度，注意需要控制 interval*(nt1+nt2)<=geo_2-geo_1+1
- dt_snapshots：MD 轨迹每一帧之间的时间步长，单位为 ps
- isf_target_q：中间散射函数计算的目标 q，单位为$$\mathrm{Angstrom^{-1}}$$
- isf_dgx：倒空间中的间隔，一般取 $$2\pi/a$$，其中a为x方向的晶格长度，单位为$$\mathrm{Angstrom^{-1}}$$
- isf_dgy：一般取 $$2\pi/b$$，其中b为y方向的晶格长度，单位为$$\mathrm{Angstrom^{-1}}$$
- isf_dgz：一般取 $$2\pi/c$$，其中c为z方向的晶格长度，单位为$$\mathrm{Angstrom^{-1}}$$
- isf_ngx：上述倒空间中 x 方向的间隔的数量
- isf_ngy：上述倒空间中 y 方向的间隔的数量
- isf_ngz：上述倒空间中 z 方向的间隔的数量

执行如下命令：

```bash
mpirun -n 2 candela
```

即可得到 ISF，输出到 `isf.txt`，其中第一列为时间，单位为 ps，第二列即为对应的 ISF。

接着执行如下命令得到离子-离子动态结构因子，其中`PathtoCandela`指的是Candela的下载目录：

```bash
python PathtoCandela/examples/e3_dsf/onedsf.py 0.00006 0.0006
```

其中第一个参数 0.00006 = dt_snapshots * geo_interval，为 ISF 的时间步长，单位为 ps；第二个参数 0.0006，为对 ISF 做傅里叶变换的总时长，单位为 ps。这里 `onedsf.py` 默认读取 `isf.txt`，并输出到 `dsf.txt`，其中第一列为$$\hbar \omega$$，单位为 meV，第二列即为对应的 DSF。

## 4 均方差位移

进入 `MSD` 文件夹，`INPUT` 文件具体如下：

```bash
calculation   msd_multiple
geo_in_type   ABACUS
geo_directory ../MD_dump
geo_1         0
geo_2         100
geo_interval  1
geo_ignore    50

ntype         1
natom         32
msd_n         2
msd_t0        0.003
msd_t         0.0015
msd_dt0       0.0015
msd_dt        0.00006
msd_natom     32
```

以上参数在 Candela 的[线上文档](https://candela-docs.readthedocs.io/en/latest/)中均有详细说明，这里再进行简单概述：

- calculation：设置为 msd_multiple，即计算均方差位移
- msd_n：计算均方差位移的段数，目的是将 MD 轨迹分成若干段，分别计算均方差位移
- msd_t0：计算均方差位移的起始时间，单位为 ps
- msd_t：每段均方差位移的时长，单位为 ps
- msd_dt0：两段均方差位移起始位置的间隔，单位为 ps。若设置等于 msd_t，则每段均方差位移之间的时间距离为 0
- msd_dt：获取的 MD 轨迹每一帧之间的时间步长（等于geo_interval * dt，其中 dt 为 MD 轨迹每一帧之间的时间步长），单位为 ps
- msd_natom：需要设置为计算的原子数

执行如下命令：

```bash
mpirun -n 2 candela
```

即可得到 MSD，输出到 `MSD_each.txt` 和 `MSD_total.txt`。其中 `MSD_each.txt` 第一列为时间，单位为 ps，第二列到最后一列即为对应的每段的 MSD，单位为$$\mathrm{Angstrom^{2}}$$；`MSD_total.txt` 第一列为时间，单位为 ps，第二列为平均的每段的 MSD，单位为$$\mathrm{Angstrom^{2}}$$。
