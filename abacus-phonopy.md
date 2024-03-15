# ABACUS+Phonopy 计算声子谱

<strong>作者：赵天琦，邮箱：zhaotq13@tsinghua.org.cn；陈涛，邮箱：chentao@stu.pku.edu.cn</strong>

<strong>审核：刘建川，邮箱：liujianchuan2013@163.com</strong>

<strong>最后更新时间：2023/08/14</strong>

<strong>在Bohrium Notebook上快速学习：</strong><a href="https://nb.bohrium.dp.tech/detail/8741867512" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>

# 一、介绍

本教程旨在介绍采用 ABACUS（基于 ABACUS 3.2.2 版本）做密度泛函理论计算，并且结合 Phonopy 软件计算声子谱的流程。此外，本教程还用到 gnuplot 来绘图。

首先推荐大家阅读以下文档中的详细说明：

ABACUS 官方文档：[Phonopy - ABACUS documentation](https://link.zhihu.com/?target=http%3A//abacus.deepmodeling.com/en/latest/advanced/interface/phonopy.html)

Phonopy 相关文档：[ABACUS & phonopy calculation — Phonopy v.2.19.1](http://phonopy.github.io/phonopy/abacus.html)

Gnuplot 主页：[gnuplot homepage](http://www.gnuplot.info/)

# 二、准备

我们以 FCC Al 这个简单例子来演示使用 <strong>有限位移方法 </strong>来结合 ABACUS 和 Phonopy 计算声子谱。

## 1. 下载并安装 Phonopy

```bash
git clone https://github.com/phonopy/phonopy.git
cd phonopy
python3 setup.py install
```

## 2. 下载 FCC Al 例子

可以从 Gitee 上[下载](https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/interface_Phonopy)。可以在网页右侧点击克隆/下载-> 下载 ZIP 得到算例，或者在 linux 终端执行如下命令得到算例：

```
git clone https://gitee.com/mcresearch/abacus-user-guide.git
```

下载后解压，之后进入 `abacus-user-guide/examples/interface_Phonopy` 文件夹

# 三、流程

## 1. 使用 ABACUS 优化结构

这里我们已经给出一个已经优化好的 FCC Al 结构

ABACUS 中的结构文件名为 `STRU`<em>：</em>

```bash
ATOMIC_SPECIES
Al 26.982 Al_ONCV_PBE-1.0.upf upf201

NUMERICAL_ORBITAL
Al_gga_7au_100Ry_4s4p1d.orb

LATTICE_CONSTANT
1.88972612546

LATTICE_VECTORS
4.03459549706 0 0 #latvec1
0 4.03459549706 0 #latvec2
0 0 4.03459549706 #latvec3

ATOMIC_POSITIONS
Direct

Al #label
0 #magnetism
4 #number of atoms
0  0  0  m  0  0  0
0.5  0.5  0  m  0  0  0
0.5  0  0.5  m  0  0  0
0  0.5  0.5  m  0  0  0
```

## 2. 用 Phonopy 产生需要计算的超胞及相应微扰构型

这里我们使用 <strong>有限位移方法</strong><strong> </strong>计算声子谱，因此需要对晶格进行扩胞并对原子位置进行微扰。执行如下命令即可生成 2*2*2 的扩胞并产生微扰结构：

```bash
phonopy -d --dim="2 2 2" --abacus
```

这一步 phonopy 会根据晶格对称性自动产生相应个数的微扰结构。由于 FCC 的晶格对称性较强，因此这个例子只产生一个微扰结构：`STRU-001`。这里类似 K 点的对称性分析，晶体结构对称性越强，所需的微扰结构就越少，对称性稍差的体系一般会产生多个微扰结构。

经验性设置：1）扩胞越大，计算结果越精确，但是计算量也会上升，一般来说扩胞三个方向的 cell 长度均在 10-20 Å 是比较合适的；2）对于优化后的晶胞（复杂体系），原子位置可能不处于高对称点上，phonopy 可能计算存在一定的误差，可以使用 Matertial Studio 等软件把对称性加回去之后，再做上述步骤，这样能够得到准确的声子谱数据（保证计算出来的声子谱满足体系的对称性特征）。

## 3. 产生 FORCE_SET 文件

接着用 ABACUS 计算原子受力，其中需要注意的是 `calculation` 需要设置为 `scf`，并且设置 `cal_force` 为 1，因为这一步目的是输出原子受力。

小技巧：即为了计算不同的微扰结构的受力，可以在 `INPUT` 里添加关键字 `stru_file` 来指定 `STRU` 文件的路径和文件名：`stru_file ./STRU-001`

INPUT 内容如下：

```bash
INPUT_PARAMETERS
#Parameters (1.General)
suffix          Al-fcc
calculation     scf
esolver_type    ksdft
symmetry        1
pseudo_dir      ./psp
orbital_dir     ./psp
cal_stress      1
cal_force       1
stru_file       STRU-001

#Parameters (2.Iteration)
ecutwfc         100
scf_thr         1e-7
scf_nmax        50

#Parameters (3.Basis)
basis_type      lcao
gamma_only      0

#Parameters (4.Smearing)
smearing_method mp
smearing_sigma  0.015

#Parameters (5.Mixing)
mixing_type     pulay
mixing_beta     0.7
mixing_gg0      1.5
```

算完之后用以下命令产生 `FORCE_SET` 文件：

```bash
phonopy -f ./disp-001/OUT*/running_scf.log ./disp-002/OUT*/running_scf.log ...
```

即要指定所有微扰构型算完之后的 `running_scf.log` 文件位置。如果运行有错，需要首先检查是否所有构型都已正常结束，且其中有力输出（可以找“FORCE”来确认）。

## 4. 设置 band.conf 文件计算得到声子谱

执行如下命令：

```bash
phonopy -p band.conf --abacus
```

band.conf 内容如下：

```bash
ATOM_NAME = Al
DIM = 2 2 2
MESH = 8 8 8
PRIMITIVE_AXES = 0 1/2 1/2  1/2 0 1/2  1/2 1/2 0
BAND = 1 1 1  1/2 1/2 1  3/8 3/8 3/4  0 0 0   1/2 1/2 1/2
BAND_POINTS = 101
BAND_CONNECTION = .TRUE.
```

这一步结束之后会有 `band.yaml` 文件输出

以上参数在 Phonopy 的[线上文档](http://phonopy.github.io/phonopy/setting-tags.html)中均有详细说明，这里再进行简单概述：

- ATOM_NAME：指定结构文件中的元素种类。
- DIM：扩胞的大小，需要跟 `3.2 用Phonopy产生需要计算的超胞及相应微扰构型` 中的“dim”一致。
- MESH：q 点的采样网格。‘8 8 8’意味着采用 8*8*8 的 q 点网格，默认以（0，0，0）为中心。
- PRIMITIVE_AXES：输入晶胞到目标原胞的转换矩阵，并将根据原胞基矢量作为声子计算的坐标系。这里是 FCC 的原胞转换矩阵。
- BAND：采样能带的 q 点路径。不同晶格的高对称点不同，具体可以使用 [SeeK-path](https://www.materialscloud.org/work/tools/seekpath)，自动生成 q 点路径。
- BAND_POINTS：给出了包括能带路径末端的采样点的数量。
- BAND_CONNECTION：在能带交叉处辅助连接能带。

## 5. 绘制声子谱

本教程使用 gnuplot 绘制声子谱，在 Ubuntu 上 gnuplot 的安装如下：

```bash
sudo apt-get install gnuplot
```

用如下命令输出 gnuplot 格式的声子谱，并使用 gnuplot 绘制声子谱并存为 `Al-FCC_plot.png`：

```bash
phonopy-bandplot --gnuplot > pho.dat
gnuplot plot_pho.gp
```

plot_pho.gp 内容如下：

```bash
set terminal pngcairo size 1920, 1080 font 'Arial, 36'   ## 格式，大小和字体
set output "Al-FCC_plot.png"  ###输出的文件名

set ylabel 'Frequency (THz)'

set ytics 2
unset key

x1 = 0.13115990
x2 = 0.17753200
x3 = 0.31664810
xmax = 0.43023590
ymin = 0
ymax = 12

set xrange [0:xmax]
set yrange [ymin:ymax]
set xtics ("{/Symbol G}" 0, "X" x1, "K" x2, "{/Symbol G}" x3, "L" xmax)
set arrow 1 nohead from x1,ymin to x1,ymax lt 2
set arrow 2 nohead from x2,ymin to x2,ymax lt 2
set arrow 3 nohead from x3,ymin to x3,ymax lt 2

plot 'pho.dat' using 1:($2) w l lw 3
```

FCC Al 的声子谱：

![](picture/fig_phonopy.png)

也可使用 Origin 绘图，`pho.dat` 的第一列就是上图的横轴（K 点路径），其中高对称 K 点位置见 `pho.dat` 的第二行，第二列就是上图的纵轴（声子频率，单位 THz）。
