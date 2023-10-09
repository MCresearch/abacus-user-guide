# 在超算环境编译 ABACUS 的建议

<strong>作者：韩昊知，邮箱：haozhi.han@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/09/26</strong>

由于不同超算环境提供的软件包版本各不相同，因此我们没办法提供给您确切的安装方法。

但是，我们将在本篇文档中介绍一些在超算环境中编译安装 ABACUS 的注意事项和相关知识。

如果在具体编译操作过程中遇到了任何问题，请随时联系我们。

# 一、关于 ABACUS

首先，再次简单介绍一下 ABACUS。ABACUS（原子算筹）软件同时支持两种基矢量，一种是<strong>平面波（Plane wave，PW） </strong>基组，一种是 <strong>LCAO (Linear combination of atomic orbitals) </strong>或者称 NAO (Numerical atomic orbitals) 基组。

用户可以编译 <strong>仅支持 PW 基组的 ABACUS</strong> 或者 <strong>同时支持两种基组的 ABACUS</strong>。同时，针对 PW 基组的 ABACUS，用户还可以选择编译串行版本或并行版本。但因为这个文档的主题是如何在超算环境中编译 ABACUS（应该没有人在超算上跑串行的 ABACUS 吧），我们接下来只会介绍并行版本的编译方法。如果想要在普通的服务器上安装串行版本的 PW 基组的 ABACUS<strong>，</strong>可以参考 [GCC 编译 ABACUS 教程 · GitBook](https://mcresearch.gitee.io/abacus-user-guide/abacus-gcc.html) 和 [Intel oneAPI 编译 ABACUS 教程 · GitBook](https://mcresearch.gitee.io/abacus-user-guide/abacus-intel.html)。

# 二、超算平台的简单介绍：

## 1. 关于 Modules

一般情况下，大多数超算平台是通过 [Environment Modules](https://modules.sourceforge.net/) 来管理基础软件库的。

如何使用 Modules？这里提供一些参考的教程：[软件模块使用方法 - 上海交大超算平台用户手册 Documentation](https://docs.hpc.sjtu.edu.cn/app/module.html)

## 2. 超算上编译 ABACUS 的基本路线

在超算平台上编译 ABACUS，同样也有两种选择：

- 一种是 基于 [GCC（the GNU Compiler Collection）](https://gcc.gnu.org/)编译
- 一种是 基于 [Intel oneAPI](https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#gs.5x6evn) 或者 [Intel Parallel Studio](https://www.intel.cn/content/www/cn/zh/developer/articles/release-notes/intel-parallel-studio-xe-release-notes-and-new-features.html) 编译

> 不得不说，使用 Intel oneAPI 将会简单很多！因此，如果你所使用的超算平台正好有 Intel oneAPI ，那么请毫不犹豫的使用它！

### 2.1 ABACUS 依赖的软件库

- <strong>C/C++ 编译器</strong>：由于 ABACUS 是由 C++ 语言编写的软件，所以一定需要 C++ 编译器。
- <strong>Fortran 编译器</strong>：Fortran 编译器并不直接用于编译 ABACUS 软件，而是需要用其编译 ABACUS 所依赖的数学库：`BLAS`、`LAPACK`、`ScaLAPACK` 和 `ELPA`。（这四个软件都是使用 Fortran 语言写的，因此需要依赖 Fortran 编译器）
- <strong>MPI 库</strong>：如果要编译并行版本的 ABACUS，那么 MPI Library 是必须的。同时也需要注意，如果你选择自己编译 `ScaLAPACK` 和 `ELPA`，那么 MPI Library 也是必须的。
- <strong>数学库</strong>：

  - <strong>BLAS</strong>：BLAS（Basic Linear Algebra Subprograms）是一组基本的线性代数库，用于高效执行常见的基础线性代数运算，如矩阵乘法和向量操作。
  - <strong>LAPACK</strong>：LAPACK（Linear Algebra Package）是一个开源的数值线性代数库，用于解决线性代数问题，包括矩阵分解、方程组求解和特征值计算等。
  - <strong>FFTW3</strong>：FFTW3（Fastest Fourier Transform in the West 3）是一个高性能、开源的快速傅里叶变换（FFT）库，用于高效计算各种傅里叶变换和逆变换。
  - <strong>ScaLAPACK</strong>：ScaLAPACK（Scalable LAPACK）是一种并行计算库，构建在 LAPACK 之上，用于解决大规模线性代数问题，特别适用于分布式和并行计算环境。
  - <strong>ELPA</strong>：ELPA（Eigenvalue SoLvers for Petaflop-Applications）是一个用于高性能计算的开源库，旨在解决大规模高性能计算中的特征值问题，特别是密集矩阵的特征值问题。（用户编译安装 abacus 的时候大多在这里出现问题）
- <strong>CEREAL</strong>：CEREAL 是一个 C++ 序列化库，用于将 C++ 对象转换为可存储或传输的数据格式，以及将其反序列化回对象。

> 如果你只编译 <strong>仅支持 PW 基组的 ABACUS</strong>，那么你不需要安装 `ScaLAPACK`<strong>、</strong>`ELPA`<strong> 和 </strong>`CEREAL`。他们是 LCAO 基组才依赖的软件库。

### 2.2 基于 Intel oneAPI  编译 ABACUS

首先在此介绍一下 Intel oneAPI 和 Intel Parallel Studio 的区别。用户可能在超算平台上同时看到 Intel oneAPI 和 Intel Parallel Studio。这是因为 Intel Parallel Studio 是 oneAPI 的前身，或者说 Intel Parallel Studio 是 oneAPI 的子集。Intel Parallel Studio 在 2020 年已经停止维护，而 Intel oneAPI 却是在 2019 年 11 月正式提出。因此我们可以将 Intel oneAPI 看作是 新版的 Parallel Studio 或加强版。

Intel oneAPI（Intel® oneAPI Toolkits）同时包含 C/C++ 编译器、 Fortran 编译器 和 Intel MPI Library。因此如果加载了 Intel oneAPI 环境，也就不用再次加载其他的 MPI Library。除此之外，Intel oneAPI 还包含了 Intel® oneAPI Math Kernel Library（简称为 MKL），这个软件库里面包含了大量常用的数学库，包括 ABACUS 依赖的 `BLAS`、`LAPACK`、`FFTW3` 和 `ScaLAPACK` 4 个软件库。

因此，如果你只编译 <strong>支持 PW 基组的 ABACUS</strong>，那么 Intel oneAPI 就已经可以解决所有的依赖问题。

如果你要编译 <strong>同时支持两种基组的 ABACUS</strong>，那么还需要手动编译安装 `ELPA` 和 `CEREAL`，安装完成后，可以参考官方文档中的 [ABACUS-Installation-Options](https://abacus.deepmodeling.com/en/latest/advanced/install.html) 编译 ABACUS。

> 注意：
> 在使用 Intel oneAPI 编译 ABACUS 的时候，并不意味着软件环境中不需要 GCC。
> refer：[How the Compiler Uses GCC](https://www.intel.com/content/www/us/en/docs/cpp-compiler/developer-guide-reference/2021-8/gcc-compatibility-and-interoperability.html#gcc-compatibility-and-interoperability_GUID-52CB6FE0-83DA-4028-9EF4-0DFAF1652736)
> Intel compilers 需要使用 GCC 中的头文件和库。因此同时也需要加载 GCC。

### 2.3 基于 GCC 编译 ABACUS

GCC（the GNU Compiler Collection）它同时包含 C/C++ 编译器和 Fortran 编译器，但其不包含 MPI Library。因此我们还需要额外的 MPI 库（[Open MPI](https://www.open-mpi.org/) 或者 [MPICH](https://www.mpich.org/)）。

由于这是基于 GCC 编译 ABACUS，如果用户所使用的超算环境中没有提供 `BLAS`、`LAPACK`、`FFTW3`、`ScaLAPACK`、`ELPA` 和 `CEREAL` 的 modules，那么这些数学库都需要用户一个个手动编译安装。

在安装完成后，可以参考官方文档中的 [ABACUS-Installation-Options](https://abacus.deepmodeling.com/en/latest/advanced/install.html) 编译 ABACUS。

# 三、拓展教程

## 1. ABACUS 高级编译选择：

[Easy Installation ‒ ABACUS documentation](http://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html#easy-installation)

[Advanced Installation Options ‒ ABACUS documentation](https://abacus.deepmodeling.com/en/latest/advanced/install.html)

## 2. 超算平台使用教程推荐：

1. [上海交大超算平台用户手册](https://docs.hpc.sjtu.edu.cn/)
2. [中国科大超算中心用户使用手册](https://scc.ustc.edu.cn/zlsc/user_doc/html/index.html)
3. [北大超算手册](https://hpc.pku.edu.cn/_book/)
4. [超算小站](https://nscc.mrzhenggang.com/)
