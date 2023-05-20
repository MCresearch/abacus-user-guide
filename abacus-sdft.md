# ABACUS 随机波函数 DFT 方法使用教程

<strong>作者：陈涛，邮箱：chentao@stu.pku.edu.cn，最后更新时间：2023/04/29</strong>

# 1. 介绍

本教程旨在介绍 ABACUS 中随机波函数密度泛函理论（Stochastic Density Functional Theory，以下简称 SDFT）计算功能。目前 ABACUS 使用 SDFT 主要聚焦在高温高压物质的模拟，特别是温稠密物质（Warm Dense Matter，简称 WDM）。在进行温稠密物质计算时（温度高达数十到上千 eV， 1 eV=11604.5 K），传统的 Kohn-Sham 密度泛函理论（KSDFT）需要用到极大数量的占据态电子波函数导致计算困难，而 SDFT 使用随机波函数轨道，可以有效地避开对角化哈密顿矩阵这个问题，应用于高温计算。关于 ABACUS 中实现 SDFT 算法的细节可以参考 Qianrui Liu and Mohan Chen*, <em>"Plane-wave-based stochastic-deterministic density functional theory for extended systems,"</em>[ ](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.106.125132) Phys. Rev. B, <strong>106</strong>, 125132 (2022)。本教程中将会展示如何在 ABACUS 计算中使用 SDFT 功能，此外还会介绍混合随机波函数密度泛函理论方法使用（mixed stochastic-deterministic DFT，简称 MDFT），即在 SDFT 计算中，混入一部分的低能 Kohn-Sham 轨道，从而加速结果收敛。

# 2. 软件和算例准备

ABACUS 的软件包（3.2.0 版本）中提供了一个 SDFT 的算例，可以从 Gitee 上[下载](https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/stochastic)。可以在网页右侧点击克隆/下载-> 下载 ZIP 得到算例，或者在 linux 终端执行如下命令得到算例：

```bash
git clone https://gitee.com/mcresearch/abacus-user-guide.git
```

下载后解压，之后进入/abacus-user-guide/examples/stochastic 文件夹。算例中有三个文件夹，pw_Si2、pw_md_Al 和 186_PW_SDOS_10D10S

# 3. 采用 SDFT 进行电子自洽迭代计算

<strong>pw_Si2</strong><strong>文件夹</strong><strong>：</strong>这是一个电子温度为 0.6 Ry（约 8.16 eV）的 2 个原子的金刚石结构硅（Si）的电子自洽迭代（Self Consistent Field，简称 SCF）算例，包含布里渊区 k 点的 KPT 文件和包含原子位置的 STRU 文件与传统的 KSDFT 计算并无区别，主要的不同在于输入文件 INPUT，注意目前 SDFT 仅支持 smearing_method 为 fd。INPUT 文件如下：

```bash
INPUT_PARAMETERS
#Parameters     (General)
calculation     scf
esolver_type    sdft
pseudo_dir      ../../PP_ORB
nbands          4
nbands_sto      64
nche_sto        100
method_sto      1
#Parameters (Accuracy)
ecutwfc         50
scf_nmax        20
symmetry        1
#Parameters (Smearing)
smearing_method fd
smearing_sigma  0.6
```

以上参数在 ABACUS 的[线上文档](http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#electronic-structure-sdft)中均有详细说明，这里再进行简单概述：

- <strong>calculation</strong>设置为 scf，代表进行电子自洽迭代计算（self-consistent field）。
- <strong>esolver_type</strong>是选择系统总能量求解方法的，默认为 ksdft（Kohn-Sham density functiona theory），这里需要设置为 sdft 才会使用 SDFT 或者 MDFT 进行计算。
- <strong>nbands</strong>是使用的 Kohn-Sham 轨道的数目（也叫 determinstic orbitals，是通过严格对角化矩阵计算出来的）。如果 nbands 设置为 0，且 nbands_sto（随机轨道数目，这里设成 64）不为 0，则会进行 SDFT 计算；如果 nbands>0，且 nbands_sto>0，则会进行混合 KS 电子轨道和随机轨道（stochastic orbitals）的 MDFT 计算。注意：一般 nbands 设置为能量低于费米能级对应的能带数，计算效率会比较高。
- <strong>nbands_sto</strong>是使用随机波函数（stochastic orbitals）轨道数目，原则上取得越大则随机误差越小，但计算效率也会相应降低。

  - 注 1：如何判断随机波函数个数是否足够的一个经验法则是：测试能量误差，实际计算中，一般可以采用<strong>10 个左右</strong>不同的随机数种子（可以参考 seed_sto 参数设置随机数种子，下面有介绍）生成的相同数目的随机波函数轨道进行 SDFT 计算，增加随机波函数轨道数目直到控制能量误差小于万分之一即可。
  - 注 2：当 nbands_sto 设为 0 时， 程序会自动转成 KSDFT 进行计算（ABACUS 3.2.2 版本以后）。
- <strong>nche_sto</strong>是将电子体系的哈密顿量进行切比雪夫展开的阶数，这个数取得越大则用到的切比雪夫展开阶数越多，相应的计算精度也会越高但效率会降低。大致关系为与温度成反比，温度越高，阶数可以取得越小；ecut（正比关系）越大，阶数越大；推荐使用的 nche_sto 的大小是使得输出文件 running_scf.log 中的 Chebyshev Precision 小于 1e-8。
- <strong>method_sto</strong>是进行 SDFT 计算使用的方法：1 代表消耗内存较少但稍慢的方法，2 代表更快但需要更大内存的方法，默认是 2。

注 1：在这个例子里我们提供的赝势是 Si.pz-vbc.UPF 文件，这个文件包含 4 个硅的价电子。事实上，当温度特别高的时候，一般的赝势可能会面临可移植性差的问题，例如高温会使得内壳层电离。这个时候，要选择合理的赝势进行计算，甚至可能需要自己造一个新的赝势，目前 ABACUS 3.2.0 支持的是模守恒的赝势。

注 2：ABACUS 的 SDFT 和 MDFT 支持多个 k 点采样，因此可以在 KPT 文件里设置不同的 k 点个数，在某些性质的计算里，要注意计算性质随着 k 点的收敛。

# 4. 采用 SDFT 进行分子动力学模拟

<strong>pw_md_Al 文件夹：</strong>这是一个电子温度为 7.35 Ry（约 100 eV）、包含 16 个铝（Al）原子的结构，我们对其进行分子动力学（Molecular Dynamics，简称 MD）的模拟。INPUT 文件如下：

```bash
INPUT_PARAMETERS
#Parameters     (General)
calculation     md
esolver_type    sdft
pseudo_dir      ../../PP_ORB
nbands          0
nbands_sto      64
nche_sto        20
method_sto      2
#Parameters (Accuracy)
ecutwfc         50
scf_nmax        20
scf_thr         1e-6
symmetry        1
#Parameters (Smearing)
smearing_method fd
smearing_sigma  7.34986072
#Parameters (MD)
md_tfirst       1160400
md_dt           0.2
md_nstep        10
```

注意要进行分子动力学模拟，calculation 参数需设置为 md。esolver_type 需设置为 sdft，才能进行 SDFT 的计算。这里 nbands 设置为 0，nbands_sto 设置为 64，代表仅仅使用随机轨道而没有 KS 轨道的 SDFT 计算。此外还有如下参数可能会用到：

- <strong>seed_sto：</strong>生成随机轨道的随机种子。默认是 0，代表随时间随机生成；若要控制使用相同的随机种子，可以设置一个大于 1 的整数。
- <strong>bndpar：</strong>将所有并行的进程分成 bndpar 个组，计算所用随机轨道将平均分布在每个组中，可以提高并行效率，默认为 1。值得注意的是，这个参数并不是越大越好，并且不如 K 点并行（<strong>kpar</strong><strong>参数</strong>）有效，实际计算中应该优先使用 K 点并行，然后测试不同大小的 bndpar，确定最佳的 bndpar。

平面波能量截断值 ecut 的测试：对于温稠密物质，一般使用 Gamma 点或 2*2*2 的 K 点即可，但是 ecut 的收敛性测试是必不可少的，由于随机误差的出现，SDFT 的 ecut 的测试与传统的 KSDFT 稍有区别，但是原理是类似的。在确定好 nbands_sto 后，就可以测试 ecut 了。与测试 nbands_sto 类似，在不同的 ecut，需要采用 10 个左右不同的随机种子生成的相同数目的随机波函数轨道进行 SDFT 计算，然后取平均能量。由于温稠密物质能量一般都比较高，因此只要控制相邻二个 ecut（相差为 10 Ry）对应的平均能量差小于一定标准即可（例如万分之一）。

# 5. 采用 SDFT 计算态密度

<strong>186_PW_SDOS_10D10S 文件夹：</strong>采用 SDFT 还可以计算给定体系的态密度（Density of States，简称 DOS）。例如，186_PW_SDOS_10D10S 是一个 1 个 Si 原子的算例。其中，INPUT 文件中我们将电子温度（通过设定 smearing_sigma）设为 0.6 Ry（约 8.16 eV），如下所示：

```bash
INPUT_PARAMETERS
#Parameters (1.General)
suffix          autotest
calculation     scf
esolver_type    sdft
method_sto      2

nbands          10
nbands_sto      10
nche_sto        120
emax_sto        0
emin_sto        0
seed_sto        20000
pseudo_dir      ../../PP_ORB
symmetry        1
kpar            1
bndpar          2

#Parameters (2.Iteration)
ecutwfc         20
scf_thr         1e-6
scf_nmax        20

#Parameters (3.Basis)
basis_type      pw

#Parameters (4.Smearing)
smearing_method fd
smearing_sigma  0.6

#Parameters (5.Mixing)
mixing_type     broyden
mixing_beta     0.4

out_dos          1
dos_emin_ev      -20
dos_emax_ev      100
dos_edelta_ev    0.1
dos_sigma        4
dos_nche         240
npart_sto        2
```

以上参数在 ABACUS 的[线上文档](http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#density-of-states)中均有说明，这里再进行简单概述：

- <strong>out_dos：</strong>需要设置为 1，才能输出能态密度。
- <strong>dos_emin_ev：</strong>能态密度的能量最小范围，单位 eV。
- <strong>dos_emax_ev：</strong>能态密度的能量最大范围，单位 eV。
- <strong>dos_sigma：</strong>能态密度的高斯展宽的因子，单位 eV。
- <strong>dos_nche：</strong>计算能态密度时切比雪夫展开阶数，默认为 100。
- <strong>npart_sto：</strong>当使用 method_sto＝2 运行例如 DOS 的 SDFT 后处理时，将控制使用内存大小为正常的 1/npart_sto，防止内存不够导致无法计算，默认为 1。

注：态密度的输出文件是 OUT 文件夹下的 DOS1_smearing.dat。

# 6. 小结

总体来讲，随机波函数密度泛函理论方法（SDFT 或者 MDFT）的使用与 KSDFT 并无太大的区别，直接运行 ABACUS 程序即可，但是对一些关键参数的选取会影响精度和效率（例如 nbands, nbands_sto, nche_sto, method_sto, bnd_par）。对于极端高温计算（>10 eV），使用 SDFT 可以大大提高计算速度，是比普通的 KSDFT 更好的选择。如果大家使用有问题，欢迎写信联系（见上，或写信到 mohanchen@pku.edu.cn）。
