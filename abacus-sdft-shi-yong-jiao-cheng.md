---
description: 作者：陈涛，邮箱：chentao@stu.pku.edu.cn
---

# ABACUS SDFT使用教程

## 1. 介绍

本教程旨在介绍ABACUS中SDFT功能。在进行高温的温稠密物质计算时（数十到上千eV），传统的KSDFT需要使用很多占据态电子波函数导致计算困难，而SDFT使用随机波函数轨道，可以有效地避开这个问题，应用于高温计算。关于SDFT有很多参考材料，其中ABACUS中SDFT算法细节和简单应用见：[Plane-wave-based stochastic-deterministic density functional theory for extended systems](https://doi.org/10.1103/PhysRevB.106.125132)本教程中将会展示如何在ABACUS计算中使用SDFT功能。

## 2.准备

ABACUS的软件包中提供了一个SDFT的算例，可以从Gitee上[下载](https://gitee.com/deepmodeling/abacus-develop/tree/develop/examples/stochastic)。算例中有二个文件夹，pw\_Si2和pw\_md\_Alpw\_Si2：这是一个电子温度为0.6 Ry（约8.16 eV） 2原子金刚石结构Si的SCF算例，KPT文件和STRU文件与平常的KSDFT计算并无区别，主要的不同在于INPUT，目前SDFT仅支持smearing\_method为fd。

```bash
INPUT_PARAMETERS
#Parameters     (General)
calculation     scf
esolver_type    sdft
pseudo_dir      ../../../tests/PP_ORB
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

这些参数在ABACUS的[线上文档](https://abacus.deepmodeling.com/en/latest/advanced/input\_files/input-main.html#electronic-structure-sdft)中均有说明，在这里再进行简单概述：

* esolver\_type是总控制，默认为ksdft，设置为sdft，才会使用SDFT计算
* nbands是使用KS轨道数目，如果设置为0，且nbands\_sto不为0，则会进行SDFT计算；如果不为0，且nbands\_sto不为0，则会进行混合KS和随机轨道的SDFT计算，也称之为MDFT。一般nbands设置为能量低于费米能级对应的能带数，可以取得效率与精度的平衡
* nbands\_sto是使用随机波函数轨道数目，越大则随机误差越小，但效率也会降低。一般采用10个左右不同的随机种子生成的相同数目的随机波函数轨道进行SDFT计算，测试能量误差，调整随机波函数轨道数目控制能量误差小于万分之一即可。注意，此项设置为0会导致ABACUS使用完备基进行计算，效率极低！
* nche\_sto是切比雪夫展开阶数，越大则阶数越多，精度越高但效率会降低。大致关系为温度（反比关系）越大，阶数越小；ecut（正比关系）越大，阶数越大；推荐使running\_scf.log中的Chebyshev Precision小于1e-8
* method\_sto是进行SDFT计算使用的方法，1代表消耗内存较少但稍慢的方法，2代表更快但需要更大内存的方法，默认是2

pw\_md\_Al：这是一个电子温度为7.35 Ry（约100 eV）16原子Al的MD算例

```bash
INPUT_PARAMETERS
#Parameters     (General)
calculation     md
esolver_type    sdft
pseudo_dir      ../../../tests/PP_ORB
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

注意calculation需设置为md，esolver\_type需设置为sdft，才能进行基于SDFT的MD模拟。同时这里，nbands设置为0，nbands\_sto设置为64，意味着进行仅使用随机轨道的SDFT计算，而不是MDFT。此外还有如下参数可能会用到：

* seed\_sto：生成随机轨道的随机种子。默认是0，代表随时间随机生成；若要控制使用相同的随机种子，可以设置一个大于1的整数
* npart\_sto：当使用method\_sto＝2运行例如DOS的SDFT后处理时，将控制使用内存大小为正常的1/npart\_sto，防止爆内存导致无法计算，默认为1
* bndpar：将所有核分成bndpar组，计算所用随机轨道将平均分布在每个组中，可以提高并行效率，默认为1。值得注意的是，这个参数并不是越大越好，并且不如K点并行（kpar）有效，实际计算中应该优先使用K点并行，然后测试不同大小的bndpar，确定最佳的bndpar

ecut的测试：对于温稠密物质，一般使用Gamma点或2\*2\*2的K点即可，但是ecut的收敛性测试是必不可少的，由于随机误差的出现，SDFT的ecut的测试与传统的KSDFT稍有区别，但是原理是类似的在确定好nbands\_sto后，就可以测试ecut了。与测试nbands\_sto类似，在不同的ecut，需要采用10个左右不同的随机种子生成的相同数目的随机波函数轨道进行SDFT计算，然后取平均能量。由于温稠密物质能量一般都比较高，因此只要控制相邻二个ecut（相差为10 Ry）对应的平均能量差小于万分之一即可

## 3. 流程

与KSDFT并无区别，直接运行ABACUS程序即可

## 4. 结尾

在高温计算中，使用SDFT可以大大提高计算速度，使很多昂贵的计算变为可能。
