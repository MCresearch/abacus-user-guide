# ABACUS FFT 模块介绍

**作者：张笑扬，邮箱：zxypku21@stu.pku.edu.cn**

**作者：刘涛，邮箱：liiutao@pku.edu.cn**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2025/11/20**

# 一、FFT 模块介绍

## 背景介绍

作为国产第一性原理电子结构软件 ABACUS 的核心数学库组件，三维快速傅里叶变换（Fast Fourier Transform, FFT）是决定软件计算性能的关键热点模块。FFT 作为高效求解离散傅里叶变换的经典算法，在 ABACUS 中承担着函数空间转换的核心功能，其广泛应用于波函数、电子密度、势函数等关键物理量在实空间（r 空间）与倒易空间（k 空间）的相互转换。通过实现两类空间的快速迭代转化，FFT 为软件高效开展电子结构精确计算提供了底层算法支撑，是保障大规模材料模拟效率的核心技术之一。

首先我们简述一下三维 FFT 的公式，通常我们定义一个正变换（FFT）和一个逆变换（IFFT），公式分别为

$$
g(k_x,k_y,k_z)=FFT[f(x,y,z)]
$$

和

$$
f(x,y,z) = IFFT^{}[g(k_x,k_y,k_z)]
$$。

## 物理模型

基于密度泛函理论（DFT）的算法特性，ABACUS 软件中需针对 FFT 变换的应用场景进行多维度针对性设计，核心要点如下：

- **物理模型角度**：FFT 需适配不同物理对象的计算需求。例如电子波函数对应的三维 FFT 网格尺寸为 nx×ny×nz（正整数，且为 2、3、5、7 的乘积形式），而电荷密度与势函数的 FFT 网格尺寸需达到 2nx×2ny×2nz—— 这是因为电荷密度是电子波函数的模平方，若要以同等精度描述电荷密度分布，需将网格密度提升一倍，对应动能截断值需提高 4 倍；对于超软赝势体系，FFT 网格还需进行额外的适配调整。此外，ABACUS 的 LCAO（线性缀加平面波）算法中，局域赝势、电子密度梯度求解、电子密度混合、Hartree 势计算等物理量的实现，也依赖平面波基组与 FFT 的协同工作来计算相应的物理量。
- **高性能计算角度**：CPU 平台的 FFT 并行计算需通过 all-to-all 的 MPI 通信实现，这在数千核以上的大规模并行场景中面临显著挑战。因此，多数 DFT 软件并未直接调用三维 FFT 函数，而是采用“一维 FFT 程序手写实现 + 二维 FFT 组合” 的方式替代直接三维 FFT 调用；而在 GPU 平台中，直接调用三维 FFT 已被证实可获得优异的计算效率，无需额外拆分优化。
- **平面波基组的角度**：基于平面波基组求解 Kohn-Sham 方程时，FFT 网格需完成物理量的空间变换，且倒空间中的有效计算区域并非与实空间对应的三维长方体网格，而是由动能截断值决定的球形区域（球内包含计算所需的全部平面波）。例如波函数 FFT 的球半径由 ecutwfc（波函数动能截断值）定义，电荷密度 FFT 的球半径由 ecutrho（电荷密度动能截断值）定义。由于球形区域体积小于长方体网格，在执行一维 FFT 时，不仅便于 MPI 进程的任务分配，还能通过裁剪无效网格区域减少计算量，提升整体效率。
- **软件框架角度**：基于上述 FFT 的多场景适配需求，ABACUS 需构建一款兼具灵活性与兼容性的精巧 FFT 模块：一方面需支持不同物理模型、不同算法（如平面波、LCAO）场景下的灵活调用，另一方面需实现跨超算平台的硬件适配能力，确保程序在不同计算硬件（CPU/GPU）上可自动匹配最优的 FFT 实现方案。这一设计目标是 ABACUS 软件 FFT 模块开发的核心诉求，也是保障软件在大规模材料模拟中兼顾精度与效率的关键支撑。其设计理念大致如下：

FFT 模块通过智能指针方式管理不同的设备，在算法层面支持 FFT_3D 计算和 many_FFT 计算。在对外的接口层提供 FFT 资源分配释放，FFT_backward 和 FFT_forward 和获得数据操作。

# 二、代码介绍

## 总体介绍

目前 ABACUS 已支持在 CPU、GPU、DCU、DSP 等硬件设备上运行 float（单精度）和 double（双精度）类型的三维 FFT 变换，为满足 FFT 操作对不同设备、精度及计算方式的适配需求，我们采用 C++ 的多态设计实现计算逻辑，其 FFT 模块代码放置于 `source/module_base/module_fft/`，现介绍主要文件如下：

## `fft_bundle.h` 介绍

定义 FFT_Bundle 类。ABACUS 提供给开发者使用的 FFT 接口是 `FFT_Bundle` 类。首先是 `FFT_Bundle` 这个类的构造与析构函数。开发者可以直接创建一个 `FFT_Bundle` 对象，也可以传入两个参数构造 `FFT_Bundle` 对象。第一个参数 device_in：支持 cpu, gpu 和 dsp，由于曙光 DCU 上较为完备的适配，DCU 和 GPU 是一样的。第二个参数 precision_in：支持 float, double, mixing。类里还有个 setfft 函数也可以用来设置这两个参数，这两种初始化方式是一样的。

在设置好计算设备和精度之后，使用 `initfft` 这个函数来进行初始化。

FFT_Bundle 类有 private 的成员变量为指向 FFT_BASE 对象的**智能指针(C++ 特性)，这样就定义了 FFT_base 基类并由各设备的具体实现类继承其计算接口**。

初始化 FFT_Bundle 可以用如下的方式，参考这部分代码 `source/module_basis/module_pw/pw_basis_k.cpp`：

```
this->fft_bundle.clear();
    if (this->xprime)
    {
        this->fft_bundle.initfft(this->nx,
                          this->ny,
                          this->nz,
                          this->lix,
                          this->rix,
                          this->nst,
                          this->nplane,
                          this->poolnproc,
                          this->gamma_only,
                          this->xprime);
    }
    else
    {
        this->fft_bundle.initfft(this->nx,
                          this->ny,
                          this->nz,
                          this->liy,
                          this->riy,
                          this->nst,
                          this->nplane,
                          this->poolnproc,
                          this->gamma_only,
                          this->xprime);
    }
    this->fft_bundle.setupFFT();
```

因此，ABACUS 可以通过 FFT_Bundle 类统一管理各类 FFT plan（每个 FFT 调用都需要先调用一个 FFT 的 plan 函数设定 FFT 的各种参数）。为提升代码可读性，最外层函数设计为直接通过 <T, Device> 模板方式调用。

## `fft_base.h` 介绍

这是一个纯虚基类，作为不同设备的基类，可以设置 `FFT plan`,删除 `FFT plan`,销毁分配内存空间。

接下来，集成 FFT_base 的类关系图如下：

FFT_Base 是 FFT_Bundle 中的成员，FFT_CPU 等不同设备继承自 FFT_base，其实现过程就是继承 FFT_Base 类，然后重载对应的函数，在函数内部实现各自的功能即可，在运行时通过多态判断设备。

而对应的 FFT_Budlde 对象可以保存在不同的物理模型对象里，例如 PW_Basis 类和 PW_basisi_k 类中。

## 平面波的类

举一个最典型的例子来说明 ABACUS 软件如何调用 FFT。模块 `source/source_basis/module_pw` 里定义了平面波的类。例如，在 `pw_basis.h` 文件里定义了 `PW_Basis` 类，`FFT_Bundle` 是这个类的一个成员变量。

在平面波的类里，提供了一系列名字为 `real2recip`、`recip2real`、`real_to_recip` 和 `recip_to_real` 的函数，用于对波函数或者电荷密度进行 FFT 操作。调用这些实际屏蔽了所有对 FFT 接口本身的交互。**这里实际上是结合了上述所讲的平面波球的特性，调用了 FFT_Bundle 类的 1 维 FFT 和 2 维 FFT，组装了一个供 DFT 使用的定制化 3 维 FFT。**

在程序中可直接通过 `PW_Basis_K` 类（继承了 `PW_Basis` 类，带上了布里渊区 k 点的信息，类声明在 `pw_basis_k.h` 文件里）对应对象来进行调用 FFT 的操作，<T,Device> 分别指代计算精度和设备。

具体细节如下：

第一、初始化 PW_BASIS 类

```cpp
// 声明一个平面波基组对象，用于平面波计算
PW_BASIS pwtest;
// 初始化MPI并行环境，设置进程池中的进程数和当前进程的排名，以及通信域
// nproc_in_pool: 进程池中的总进程数
// rank_in_pool: 当前进程在池中的排名（从0开始）
// POOL_WORLD: MPI通信域，通常使用MPI_COMM_WORLD或类似的通信域
pwtest.initmpi(nproc_in_pool, rank_in_pool, POOL_WORLD);
// 初始化实空间和倒易空间网格
// lat0: 晶格常数（单位：Bohr）
// latvec: 晶格矢量矩阵（3x3矩阵）
// wfcecut: 波函数截断能（单位：Ry或Ha，取决于具体实现）
pwtest.initgrids(lat0, latvec, wfcecut);
// 设置计算参数
// gamma_only: 布尔值，指示是否只使用Gamma点（k=0）进行计算
// wfcecut: 波函数截断能
// distribution_type: 平面波分布类型
// xprime: 在进行CPU计算时xy方向是否使用x优先，对性能的影响
pwtest.initparameters(gamma_only, wfcecut, distribution_type, xprime);
// 设置傅里叶变换器，用于实空间和倒易空间之间的转换，包括FFT网格的初始化和规划
pwtest.setuptransform();
// 收集当前进程负责的局部平面波（G向量）信息
pwtest.collect_local_pw();
// 去除对称性相关的重复G向量，优化计算效率
pwtest.collect_uniqgg();
```

第二、初始化 FFT，程序中被包含在 setuptransform 中

```cpp
// 清理已有的FFT资源，释放内存和计划，防止重复初始化导致的内存泄漏
this->fft_bundle.clear();
// 配置FFT计算设备和数值精度
// device: 指定计算设备（如"cpu"，"gpu"，"dsp"）
// precision: 指定计算精度（如"single"单精度或"double"双精度,"mixing"混合精度）
this->fft_bundle.setfft(this->device, this->precision);
// 初始化FFT网格参数和并行配置
// nx, ny, nz: FFT全局网格尺寸（x/y/z方向的总格点数）
// lix, rix: 当前进程处理的实空间xy方向切片数据起始位置
// nst: 波函数分块的起始索引
// nplane: 平面波分片数量，改进程上Z方向数据
// poolnproc: 进程池中的总进程数
// gamma_only: 是否仅处理Gamma点
// xprime: 是否计算X优先方向
this->fft_bundle.initfft(
    this->nx, this->ny, this->nz,
    this->lix, this->rix,
    this->nst,
    this->nplane,
    this->poolnproc,
    this->gamma_only,
    this->xprime
);
// 生成FFT计算计划并分配内存，根据配置参数创建FFTW/cuFFT等库的执行计划
this->fft_bundle.setupFFT();
```

第三、可参考 `module_pw/test_gpu/pw_basis_C2C.cpp`，以下是对调用函数的解释，以 pw_basis 的 recip_to_real 的 CPU 调用方式为例，其它可依函数参数参考

```cpp
/​**​
 * @brief 将实空间数据变换到倒易空间（傅里叶域）
 * 
 * @tparam TR       实空间数据类型（必须为实数类型或与 TK 相同）
 * @tparam TK       倒易空间数据类型（必须为复数类型） 
 * @tparam Device   计算设备类型（此处限定为CPU）
 * 
 * @param[in] in    输入数据指针（实空间）
 * @param[out] out  输出数据指针（倒易空间）
 * @param add       叠加模式标志。为true时，结果叠加到现有out数据
 * @param factor    缩放因子。执行计算时对所有结果乘以此参数
 * 
 * ### 模板类型约束
 * 1. TK必须是复数类型：
 *    - TK 不能是其自身的实数部件类型（即排除 float -> float 的情况）
 *    - 例：允许 TK=std::complex<float>，禁止 TK=float
 * 
 * 2. TR与TK兼容：
 *    - TR必须是TK的实数部件类型（允许实数输入的R2C变换）
 *      或 TR==TK（允许复数输入的C2C变换）
 *    - 例1（合法）：TR=float, TK=std::complex<float>
 *    - 例2（合法）：TR=std::complex<double>, TK=std::complex<double>
 *    - 例3（非法）：TR=double, TK=std::complex<float>
 * 
 * 3. 设备限定：
 *    - 仅支持DEVICE_CPU设备计算（禁用GPU或其他加速设备）
 */
template <typename TR, typename TK, typename Device,
          typename std::enable_if<
            // 约束1：TK必须为复数类型（类型不等于其实数分量类型）
            !std::is_same<TK, typename GetTypeReal<TK>::type>::value 
            
            // 约束2：TR必须是TK转换后的实数类型或与TK相同
            && (std::is_same<TR, typename GetTypeReal<TK>::type>::value 
                || std::is_same<TR, TK>::value)
            
            // 约束3：限定为CPU计算设备
            && std::is_same<Device, base_device::DEVICE_CPU>::value, 
          int>::type = 0>
void real_to_recip(TR* in,
                   TK* out,
                   const bool add = false,
                   const typename GetTypeReal<TK>::type factor = 1.0);
```

## 创建一个 FFT 例子

```cpp
// 初始化方法一
FFT_Bundle new_fft_bundle1("gpu", "double");

// 初始化方法二
FFT_Bundle new_fft_bundle2();
new_fft_bundle2.setfft("gpu", "double");
```

在设置好计算设备和精度之后，使用这个函数来进行初始化

```java
void initfft(int nx_in,
                 int ny_in,
                 int nz_in,
                 int lixy_in,
                 int rixy_in,
                 int ns_in,
                 int nplane_in,
                 int nproc_in,
                 bool gamma_only_in,
                 bool xprime_in = true,
                 bool mpifft_in = false);
```

在这些参数中，包含了计算的基本参数和并行参数。

其中，nx, ny, nz 为 FFT 全局网格尺寸（x/y/z 方向的总格点数）

lix, rix 为当前进程处理的实空间 xy 方向切片数据起始位置。

nst 为波函数分块的起始索引。

nplane 为平面波分片数量，改进程上 Z 方向数据。

poolnproc 为进程池中的总进程数。

gamma_only 为是否仅处理 Gamma 点。

xprime 为是否计算 X 优先方向。

除此之外，还有一个设置 fft_mode 的函数。

```java
void initfftmode(int fft_mode_in)
    {
        this->fft_mode = fft_mode_in;
    }
```

最后，调用这个没注释的函数来初始化 FFT

```cpp
void setupFFT();
```

这个函数会分配内存，以及对 FFT 进行 plan。对于一般的 FFT 来说，需要一个 Plan 来进行 FFT 计算。Plan 只需要生成一次（如果格点大小参数等都不变的话），然后以后每次都使用这个 Plan 计算。反复生成 Plan 是一个耗时的工作。

这样这个 FFT 的初始化工作就做完了。接着就是调用这个进行计算。

```cpp
template <typename FPTYPE>
    void fftzfor(std::complex<FPTYPE>* in, std::complex<FPTYPE>* out) const;
 
    template <typename FPTYPE>
    void fftxyfor(std::complex<FPTYPE>* in, std::complex<FPTYPE>* out) const;
 
    template <typename FPTYPE>
    void fftzbac(std::complex<FPTYPE>* in, std::complex<FPTYPE>* out) const;

    template <typename FPTYPE>
    void fftxybac(std::complex<FPTYPE>* in, std::complex<FPTYPE>* out) const;

    template <typename FPTYPE>
    void fftxyr2c(FPTYPE* in, std::complex<FPTYPE>* out) const;

    template <typename FPTYPE>
    void fftxyc2r(std::complex<FPTYPE>* in, FPTYPE* out) const;

    template <typename FPTYPE>
    void fft3D_forward(std::complex<FPTYPE>* in, std::complex<FPTYPE>* out) const;
    
    template <typename FPTYPE>
    void fft3D_backward(std::complex<FPTYPE>* in, std::complex<FPTYPE>* out) const;
```

可以看到，计算有很多类型的函数。前面的这些大部分都是一脉相承自 FFTW 软件包的函数。实际上最常用的一般是最后两个 `fft3D_forward` 和 `fft3D_backward`。这两个也是支持异构计算的，实际使用的时候认准这个就行。至于如何使用只要输入 input 的数组指针和 output 的数组指针即可，非常简单。

最后，当你觉得差不多用完了的时候，调用这个

```cpp
void clearFFT();
```

清空一下内容防止内存泄漏。

在清理完之后，可以继续复用这个 FFT_Bundle，或者让它销毁。

# 四、ABACUS 中调用 FFT 的地方

注：以下记录不一定完整，大概参考了 3.9.0.10 或者更早的代码。

## 电子密度的 FFT 变换

| 功能描述                     | 文件名                             |
|------------------------------|------------------------------------|
| 超软磨势的缓加电荷密度       | electate_pw.cpp                    |
| 混合电荷密度                 | charge_mixing_preconditioner.cpp   |
| 混合电荷密度                 | charge_mixing_residual.cpp         |
| 混合电荷密度                 | charge_mixing_rho.cpp              |
| 电荷密度的对称性分析         | symmetry_rho.cpp                   |
| 将电荷密度转换为Hartree势    | H_Hartree_pw.cpp                   |
| 双格子技术时侯势能插值       | potential_new.cpp                  |
| 自动存储空间的电荷密度和tau  | esolver_fp.cpp                     |
| Orbital-Free求解器           | esolver_of_tool.cpp                |
| 溶剂模型                     | cal_totn.cpp                       |
| 溶剂模型                     | cal_vcav.cpp                       |
| 溶剂模型                     | minimize_cg.cpp                    |
| 溶剂模型                     | sol_force.cpp                      |
| 交换关联泛函                 | xc_functional_gradcorr.cpp         |
| 交换关联泛函                 | xc_functional_libxc_tools.cpp      |
| 动能泛函                     | kedf_lkt.cpp                       |
| 动能泛函                     | kedf_vw.cpp                        |
| 动能泛函                     | kedf_wt.cpp                        |
| 机器学习数据                 | ml_data_descriptor.cpp             |
| 机器学习数据                 | ml_data.cpp                        |
| 求力                         | forces_cc.cpp                      |
| 求力                         | forces_scc.cpp                     |
| 求力                         | forces_us.cpp                      |
| 求力                         | forces.cpp                         |
| 求应力                       | stress_func_cc.cpp                 |
| 求应力                       | stress_func_exx.cpp                |
| 求应力                       | stress_func_har.cpp                |
| 求应力                       | stress_func_loc.cpp                |
| 求应力                       | stress_func_us.cpp                 |
| 使用R样条插值计算结构因子    | structure_factor.cpp               |
| 计算有效势与Q函数的积分      | VNL_in_pw.cpp                      |
| 杂化泛函                     | op_exx_pw.cpp                      |
| 后处理                       | get_wf_icao.cpp                    |
| 后处理                       | to_wannier90_pw.cpp                |
| 后处理                       | unk_overlap_pw.cpp                 |
| 后处理                       | write_elf.cpp                      |
| recip2real                   |                                    |
| 处理电子态                   | electate_pw.cpp                    |
| 初始化电荷密度               | charge_init.cpp                    |
| 混合电荷                     | charge_mixing_preconditioner.cpp   |
| 混合电荷                     | charge_mixing_rho.cpp              |
| 电荷密度                     | charge.cpp                         |
| 对称性                       | source/module_electate/module_cf   |
| 将电荷密度转换为Hartree势    | source/module_electate/potentials/ |
| 实空间计算局域势             | pot_local.cpp                      |
| 势能插值                     | potential_new.cpp                  |
| Orbital-Free求解器           | esolver_of_tool.cpp                |
| 溶剂模型                     | cal_totn.cpp                       |
| 平面波基组的Hartree势计算    | cal_vcav.cpp                       |
| 溶剂模型                     | cal_vel.cpp                        |
| 交换关联泛函                 | xc_functional_gradcorr.cpp         |
| 动能泛函                     | kedf_lkt.cpp                       |
| 动能泛函                     | kedf_vw.cpp                        |
| 动能泛函                     | kedf_wt.cpp                        |
| 机器学习数据                 | ml_data_descriptor.cpp             |
| 机器学习数据                 | ml_data.cpp                        |
| 求解应力                     | stress_func_exx.cpp                |
| EXX算子                      | op_exx_pw.cpp                      |
| 后处理                       | get_wf_icao.cpp                    |
| 预处理                      | read_wfc_to_rho.cpp                |
| 后处理                       | to_wannier90_pw.cpp                |
| 后处理                       | unk_overlap_pw.cpp                 |
| 后处理                       | write_elf.cpp                      |
| 后处理                       | write_wfc_r.cpp                    |

## 波函数的 FFT 变换

| 功能描述           | 文件名                     |
|--------------------|----------------------------|
| recip_to_real      |                            |
| 动能密度           | electate_pw_cal_tau.cpp    |
| 电子结构           | electate_pw.cpp            |
| 交换关联泛函       | xc_functional_gradcorr.cpp |
| 描述子             | ml_data_descriptor.cpp     |
| metaGGA            | meta_pw.cpp                |
| 杂化泛函           | op_exx_pw.cpp              |
| 有效势             | veff_pw.cpp                |
| 随机波函数         | sto_iter.cpp               |
| partial charge计算 | get_pchg_pw.h              |
| real_to_recip      |                            |
| metaGGA            | meta_pw.cpp                |
| 杂化泛函           | op_exx_pw.cpp              |
| 有效势             | veff_pw.cpp                |

现在 VeffPW 算子支持 recip_to_real<T,Device> 的方式调用 FFT 变换，后续会添加更多的支持精度和参数方式选择的的 FFT 变换函数。
