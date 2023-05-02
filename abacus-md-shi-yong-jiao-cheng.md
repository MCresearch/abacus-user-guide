# ABACUS MD使用教程
**作者：刘裕**

## 1. 介绍

本教程旨在介绍ABACUS中的分子动力学（MD）功能。MD是一种模拟分子和原子运动的方法，它基于牛顿力学的原理，可以计算分子体系的热力学和宏观性质，通过求解大量的运动方程，并从不同状态的分子构型中抽取样本，用来研究与原子运动路径相关的一些基本过程，如相变、扩散、化学反应等。

从头算分子动力学（AIMD）指的是MD模拟中的力场或势能函数的梯度由第一性原理计算软件计算得到，而不依赖经验参数。其中根据力场进行MD模拟的算法和经典MD方法没有区别。

在原子算筹的MD模块中，提供了基本的Velocity Verlet算法演化方法，和多种系综模拟方法；力场由ESolver模块提供，其既支持第一性原理计算力场，也支持LJ对势或[DeePMD-kit](https://github.com/deepmodeling/deepmd-kit)机器学习势函数。

## 2. INPUT参数

这里给出ABACUS MD计算的典型INPUT参数

```bash
INPUT_PARAMETERS
#Parameters (1.General)
suffix                  Sn_nve
esolver_type            ksdft
calculation             md
ntype                   1
nbands                  160

#Parameters (2.Iteration)
ecutwfc                 30
scf_thr                 1e-5
scf_nmax                100

#Parameters (3.Basis)
basis_type             lcao
ks_solver              genelpa
gamma_only             1

#Parameters (4.Smearing)
smearing_method        gaussian
smearing_sigma         0.01

#Parameters (5.Mixing)
mixing_type            pulay
mixing_beta            0.3
chg_extrap             second-order

#Parameters (6.MD)
md_type                0
md_nstep               10
md_dt                  1
md_tfirst              300
```

* **calculation**：ABACUS计算类型，请设置为md
* **esolver\_type**：能量求解器类型，默认采用ksdft，也可以使用sdft，lj和dp等其他类型
* **chg\_extrap**：电荷外插法，在MD计算中通常使用second-order
* **md\_type**：MD算法类型，这里采用的是NVE系综
* **md\_nstep**：MD运行步数
* **md\_dt**：MD的运动步长，单位为fs，原子越重则**md\_dt**越大
* **md\_tfirst**：控制MD的初始温度
* **init\_vel**：是否读取STRU中的原子速度，若为1则读取，否则根据**md\_tfirst**来随机初始原子速度
* **md\_restart**：控制MD续算的开关，若为1，且将最后输出的OUT.\*/STRU/STRU\_MD\_$num复制到工作目录，覆盖STRU，则可以进行MD续算

更多MD参数的详细用法请参考[ABACUS线上文档](https://abacus.deepmodeling.com/en/latest/advanced/input\_files/input-main.html#molecular-dynamics)

### ABACUS + DeePMD-kit

ABACUS MD目前支持DeePMD-kit生成的机器学习势函数，ABACUS联合DeePMD-kit的编译方法详见[ABACUS线上文档](https://abacus.deepmodeling.com/en/latest/advanced/install.html#build-with-deepmd-kit)

* esolver\_type：设置为dp
* pot\_file：指定DP势函数文件所在路径，默认为graph.pb

## 3. 算例

在[github](https://github.com/deepmodeling/abacus-develop/tree/develop/examples/md/lcao\_gammaonly\_Sn64)以及[gitee](https://gitee.com/deepmodeling/abacus-develop/tree/develop/examples/md/lcao\_gammaonly\_Sn64)的仓库中，我们提供了MD的计算算例

## 4. 总结

欢迎大家使用ABACUS的MD功能，我们会根据大家的反馈不断改进ABACUS MD的使用体验
