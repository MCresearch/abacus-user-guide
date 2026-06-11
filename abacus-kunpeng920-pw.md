# 国产软硬件生态融合2：华为鲲鹏920处理器上ABACUS平面波基组的测试

**作者：张笑扬，邮箱：zxypku21@stu.pku.edu.cn**

**审核：周徐源，邮箱：xy_z@pku.edu.cn**

**审核：蒋巩明，邮箱：jianggongming@huawei.com**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2026/06/08**

本篇介绍ABACUS在华为鲲鹏920处理器上的平面波基组测试情况，关于ABACUS在华为鲲鹏920处理器上的编译请参见本系列前一篇[国产软硬件生态融合1：ABACUS基于华为鲲鹏920处理器的编译和使用指南](https://mp.weixin.qq.com/s/2qLbWy2XozE_IjijAd6S7w)

# 一、测试环境：

1. 使用abacus-develop的release页面的3.9.0.25，编译abacus_2p可执行文件

2. 对比环境：台式机工作站。（Intel Xeon Gold 6132，以下简称6132）

3. 920新型号比较：4进程4线程 / 8进程2线程（部分大算例4*4运行较缓慢）。6132和新型号运行方式示例：

```Bash
export OMP_NUM_THREADS=4
mpirun -np 4 abacus
```

4. 920专业版比较：针对其众核特性，使用单节点满载性能进行比较。

6132：28进程运行。920专业版：取运行速度最快的单节点进程数作为参考。专业版运行方式示例：

```Bash
export KML_FFT_THREAD_TYPE=OMP
export KML_BLAS_THREAD_TYPE=OMP
export OMP_NUM_THREADS=2
mpirun --map-by ppr:4:numa:pe=2 -np 8 abacus
```

# 二、总结表格

## 920新型号测试表格

920新型号和6132使用相同进程数+线程数进行效率测试。001和002算例为4*4，后面的算例均为8*2

|算例|001_4GaAS|002_C2H6O|003_4MoS2|004_12Pt111|005_3BaTiO3|006_16Na|007_27Fe|008_32H2O|009_Li27Ni9O5Mn9Co9|010_216Si|
|---|---|---|---|---|---|---|---|---|---|---|
|6132耗时/s|59|607|1041|917|8828|979|9955|4444|6761|2059|
|920新型号耗时/s|42|274|352|315|3217|772|3542|120|1982|520|
|加速比|1.4|2.2|3.0|2.9|2.7|1.3|2.8|3.7|3.4|3.9|

## 920专业版测试表格

920专业版由于其架构原因，不宜进行相同进程数与线程数的计算比较，这里比较单节点的性能峰值。

|算例|001_4GaAS|002_C2H6O|003_4MoS2|004_12Pt111|005_3BaTiO3|006_16Na|007_27Fe|008_32H2O|009_Li27Ni9O5Mn9Co9|010_216Si|
|---|---|---|---|---|---|---|---|---|---|---|
|6132耗时/s|31|496|833|656|7725|589|9772|447|6189|2103|
|920专业版耗时/s|54|84|231|178|1885|778|2056|54|579|236|
|加速比|0.57|5.9|3.6|3.7|4.1|0.76|4.7|8.8|10.7|8.9|

# 001_4GaAs（4*4）920新型号测试：加速1.4倍

## 920新型号结果：42 s

![](picture/fig-kunpeng920-pw-1.png)

## 对照组结果：59 s

![](picture/fig-kunpeng920-pw-2.png)

# 002_C2H6O（4*4）920新型号测试：加速2.2倍

## 920新型号结果：274 s

![](picture/fig-kunpeng920-pw-3.png)

![](picture/fig-kunpeng920-pw-4.png)

## 对照组结果：607 s

![](picture/fig-kunpeng920-pw-5.png)

![](picture/fig-kunpeng920-pw-6.png)

# 003_4MoS2（8*2）920新型号测试：加速3.0倍

## 920新型号结果：352 s

![](picture/fig-kunpeng920-pw-7.png)

![](picture/fig-kunpeng920-pw-8.png)

## 对照组结果：1041 s

![](picture/fig-kunpeng920-pw-9.png)

![](picture/fig-kunpeng920-pw-10.png)

# 004_12Pt111（8*2）920新型号测试：加速2.9倍

## 920新型号结果：315 s

![](picture/fig-kunpeng920-pw-11.png)

![](picture/fig-kunpeng920-pw-12.png)

## 对照组结果：917 s

![](picture/fig-kunpeng920-pw-13.png)

![](picture/fig-kunpeng920-pw-14.png)

# 005_3BaTiO3（8*2）920新型号测试：加速2.7倍

## 920新型号结果：3217 s

![](picture/fig-kunpeng920-pw-15.png)

![](picture/fig-kunpeng920-pw-16.png)

## 对照组结果：8828 s

![](picture/fig-kunpeng920-pw-17.png)

![](picture/fig-kunpeng920-pw-18.png)

# 006_16Na（8*2）920新型号测试：加速1.3倍

## 920新型号结果：772 s

![](picture/fig-kunpeng920-pw-19.png)

![](picture/fig-kunpeng920-pw-20.png)

## 对照组结果：979 s

![](picture/fig-kunpeng920-pw-21.png)

![](picture/fig-kunpeng920-pw-22.png)

# 007_27Fe（8*2）920新型号测试：加速2.8倍

## 920新型号结果：3542 s

![](picture/fig-kunpeng920-pw-23.png)

![](picture/fig-kunpeng920-pw-24.png)

## 对照组结果：9955 s

![](picture/fig-kunpeng920-pw-25.png)

![](picture/fig-kunpeng920-pw-26.png)

# 008_32H2O（8*2）920新型号测试：加速3.7倍

## 920新型号结果：120 s

![](picture/fig-kunpeng920-pw-27.png)

![](picture/fig-kunpeng920-pw-28.png)

## 对照组结果：444 s

![](picture/fig-kunpeng920-pw-29.png)

![](picture/fig-kunpeng920-pw-30.png)

# 009_Li27Ni9O54Mn9Co9（8*2）920新型号测试：加速3.4倍

## 920新型号结果：1982 s

![](picture/fig-kunpeng920-pw-31.png)

![](picture/fig-kunpeng920-pw-32.png)

## 对照组结果：6761 s

![](picture/fig-kunpeng920-pw-33.png)

![](picture/fig-kunpeng920-pw-34.png)

# 010_216Si（8*2）920新型号测试：加速3.9倍

## 920新型号结果：520 s

![](picture/fig-kunpeng920-pw-35.png)

![](picture/fig-kunpeng920-pw-36.png)

## 对照组结果：2059 s

![](picture/fig-kunpeng920-pw-37.png)

![](picture/fig-kunpeng920-pw-38.png)

# 920新型号测试总结

## 效率

在相同进程数和线程数的情况下，鲲鹏920型号比起6132工作站CPU有非常明显的优势。在所有的算例上都产生了明显的加速效果。面对较大的算例，普遍都能产生两倍以上的加速效果。并且这是开箱即用的结果，没有进行任何针对性优化，优化后效率预期会有进一步提升。

## 精度

能量误差在输出位数范围内基本可忽略。

总压力大约有0.001 kbar左右的误差。

# 001_4GaAs 920专业版测试：32进程2线程，加速0.57倍

## 920专业版结果：54 s

![](picture/fig-kunpeng920-pw-39.png)

## 对照组结果：31 s

![](picture/fig-kunpeng920-pw-40.png)

![](picture/fig-kunpeng920-pw-41.png)

# 002_C2H6O 920专业版测试：114进程，加速5.9倍

## 920专业版结果：84 s

![](picture/fig-kunpeng920-pw-42.png)

![](picture/fig-kunpeng920-pw-43.png)

## 对照组结果：496 s

![](picture/fig-kunpeng920-pw-44.png)

![](picture/fig-kunpeng920-pw-45.png)

# 003_4MoS2 920专业版测试：76进程 ，加速3.6倍

## 920专业版结果：231 s

![](picture/fig-kunpeng920-pw-46.png)

![](picture/fig-kunpeng920-pw-47.png)

## 对照组结果：833 s

![](picture/fig-kunpeng920-pw-48.png)

![](picture/fig-kunpeng920-pw-49.png)

# 004_12Pt111 920专业版测试：76进程，加速3.7倍

## 920专业版结果：178 s

![](picture/fig-kunpeng920-pw-50.png)

![](picture/fig-kunpeng920-pw-51.png)

## 对照组结果：656 s

![](picture/fig-kunpeng920-pw-52.png)

![](picture/fig-kunpeng920-pw-53.png)

# 005_3BaTiO3 920专业版测试：76进程 ，加速4.1倍

## 920专业版结果：1885 s

![](picture/fig-kunpeng920-pw-54.png)

![](picture/fig-kunpeng920-pw-55.png)

## 对照组结果：7725 s

![](picture/fig-kunpeng920-pw-56.png)

![](picture/fig-kunpeng920-pw-57.png)

# 006_16Na 920专业版测试：40进程 2线程 加速0.76倍

## 920专业版结果：778 s

![](picture/fig-kunpeng920-pw-58.png)

## 对照组结果：589 s

![](picture/fig-kunpeng920-pw-59.png)

![](picture/fig-kunpeng920-pw-60.png)

# 007_27Fe 920专业版测试：76进程 加速4.8倍

## 920专业版结果：2056 s

![](picture/fig-kunpeng920-pw-61.png)

![](picture/fig-kunpeng920-pw-62.png)

## 对照组结果：9772 s

![](picture/fig-kunpeng920-pw-63.png)

![](picture/fig-kunpeng920-pw-64.png)

# 008_32H2O 920专业版测试：76进程 加速8.8倍

## 920专业版结果：54 s

![](picture/fig-kunpeng920-pw-65.png)

![](picture/fig-kunpeng920-pw-66.png)

## 对照组结果：447 s

![](picture/fig-kunpeng920-pw-67.png)

![](picture/fig-kunpeng920-pw-68.png)

# 009_Li27Ni9O54Mn9Co9 920专业版测试：76进程 加速10.7倍

## 920专业版结果：579 s

![](picture/fig-kunpeng920-pw-69.png)

![](picture/fig-kunpeng920-pw-70.png)

## 对照组结果：6189 s

![](picture/fig-kunpeng920-pw-71.png)

![](picture/fig-kunpeng920-pw-72.png)

# 010_216Si 920专业版测试：114进程 加速8.9倍

## 920专业版结果：236 s

![](picture/fig-kunpeng920-pw-73.png)

## 对照组结果：2103 s

![](picture/fig-kunpeng920-pw-74.png)

![](picture/fig-kunpeng920-pw-75.png)

# 920专业版测试总结

## 效率

在相同进程数和线程数的情况下，鲲鹏920专业版比起6132工作站CPU有非常明显的优势。在绝大部分算例上都产生了明显的加速效果。对于几个尤其大的算例，能够产生接近十倍的加速比。并且这也是开箱即用的结果，没有进行任何针对性优化，优化后效率预期会非常优异。

## 精度

能量误差在输出位数范围内基本可忽略。

总压力大约有0.001 kbar左右的误差。

