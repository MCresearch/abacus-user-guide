# GCC 编译 ABACUS 教程

<strong>作者：韩昊知，邮箱：haozhi.han@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/09/19</strong>

# 一、介绍：关于 ABACUS

ABACUS（原子算筹）软件同时支持两种基矢量，一种是平面波（Plane wave，PW） 基组，一种是 LCAO (Linear combination of atomic orbitals)或者称 NAO(Numerical atomic orbitals)基组。因为两种基组运行依赖的软件库不完全相同，所以我们分开介绍。

实际上，LCAO 基组依赖的软件库比 PW 基组更多，因此如果用户只使用 PW 基组，并不需要将所有依赖的数学库全都下载安装好。

下面介绍，两种基组分别都依赖那些数学库：

- <strong>PW 基组依赖以下 3 个 数学库：</strong>

  - <strong>BLAS</strong>：BLAS（Basic Linear Algebra Subprograms）是一组基本的线性代数库，用于高效执行常见的基础线性代数运算，如矩阵乘法和向量操作。
  - <strong>LAPACK</strong>：LAPACK（Linear Algebra Package）是一个开源的数值线性代数库，用于解决线性代数问题，包括矩阵分解、方程组求解和特征值计算等。
  - <strong>FFTW3</strong>：FFTW3（Fastest Fourier Transform in the West 3）是一个高性能、开源的快速傅里叶变换（FFT）库，用于高效计算各种傅里叶变换和逆变换。
- <strong>LCAO 基组依赖以下 6 个 软件库：</strong>

  - BLAS
  - LAPACK
  - FFTW3
  - <strong>ScaLAPACK</strong>：ScaLAPACK（Scalable LAPACK）是一种并行计算库，构建在 LAPACK 之上，用于解决大规模线性代数问题，特别适用于分布式和并行计算环境。
  - <strong>CEREAL</strong>：CEREAL 是一个 C++ 序列化库，用于将 C++ 对象转换为可存储或传输的数据格式，以及将其反序列化回对象。
  - <strong>ELPA</strong>：ELPA（Eigenvalue SoLvers for Petaflop-Applications）是一个用于高性能计算的开源库，旨在解决大规模高性能计算中的特征值问题，特别是密集矩阵的特征值问题。（用户编译安装 abacus 的时候大多在这里出现问题）

> ELPA仅用于 LCAO基组求解特征值与特征矩阵的过程，如果由于机器等原因导致 ELPA 难以安装，可以暂不安装ELPA，在编译 abacus 的时候添加-DUSE_ELPA=0即可绕过ELPA安装困难的问题。
> 
> 在ABACUS中，LCAO基组求解特征值与特征矩阵提供了两种方法，一种是调用ELPA进行求解（默认选项），一种是调用ScaLAPACK进行求解。
> 
> 如果使用-DUSE_ELPA=0编译选项，请参考使用文档配置ks_solver为scalapack_gvx，调用ScaLAPACK进行求解。（http://abacus.deepmodeling.com/en/stable/advanced/input_files/input-main.html#ks-solver）

# 二、检查当前服务器基础环境：

## 1. 查看当前系统版本：

```bash
root@bohrium-11852-1041346:~# lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 20.04.5 LTS
Release:        20.04
Codename:       focal
```

## 2. 检查当前 GCC 编译器版本：

```bash
root@bohrium-11852-1041346:~# g++ --version
g++ (Ubuntu 9.4.0-1ubuntu1~20.04.1) 9.4.0
Copyright (C) 2019 Free Software Foundation, Inc.
```

## 3. 检查当前环境是否有 git

```bash
root@bohrium-11852-1041346:~# git --version
git version 2.25.1
```

# 三、安装 仅支持 PW 基组的 ABACUS

对于仅支持 PW 基组的 ABACUS，我们同时支持两种版本的编译：串行版本和并行版本。

编译这两个版本的主要区别在于是否需要安装 MPI library。

## 1. 编译串行版本

### 1.1 安装依赖库。

```bash
sudo apt update 
sudo apt install -y libopenblas-openmp-dev
sudo apt install -y liblapack-dev 
sudo apt install -y libfftw3-dev
```

### 1.2 从仓库克隆代码到本地，并进入目录。

```bash
git clone https://github.com/deepmodeling/abacus-develop.git
cd abacus-develop/
```

### 1.3 开始编译并安装 `abacus`。

```bash
cmake -B build -DENABLE_MPI=OFF
cd build && make -j`nproc`
```

可以看到在当前目录下，已经编译成功了 `abacus_pw_serial` 可执行文件。

`abacus_pw_serial` 就是串行版本的支持平面波基组的 ABACUS。

## 2. 编译并行版本

### 2.1 安装依赖库。（同串行，如果已经安装，则不用重复操作）

```bash
sudo apt update 
sudo apt install -y libopenblas-openmp-dev
sudo apt install -y liblapack-dev 
sudo apt install -y libfftw3-dev
```

### 2.2 安装 MPI library。这里选择更为常用的 <strong>open MPI</strong>。

```bash
sudo apt install -y libopenmpi-dev
```

### 2.3 从仓库克隆代码到本地，并进入目录。

```bash
git clone https://github.com/deepmodeling/abacus-develop.git
cd abacus-develop/
```

### 2.4 开始编译并安装 `abacus`。

```bash
cmake -B build -DENABLE_LCAO=OFF
cd build && make -j`nproc`
```

可以看到在当前目录下，已经编译成功了 `abacus_pw` 可执行文件。

`abacus_pw` 就是并行版本的支持平面波基组的 ABACUS。

# 四、安装 支持两种基组的 ABACUS

对于同时支持两种基组的 ABACUS，仅可以编译并行版本。<strong>并无串行版本。</strong>

在本文最初就提到支持 LCAO 基组的 ABACUS 所依赖软件库的更多。

## 1. 安装 PW 基组依赖的软件库。（同上，如果已经安装，则不用重复操作）

```bash
sudo apt update 
sudo apt install -y libopenblas-openmp-dev
sudo apt install -y liblapack-dev 
sudo apt install -y libfftw3-dev
```

## 2. 安装 MPI library。这里选择更为常用的 <strong>open MPI</strong>。（同上，如果已经安装，则不用重复操作）

```bash
sudo apt install -y libopenmpi-dev
```

## 3. 安装 LCAO 基组依赖的 ScaLAPACK 和 CEREAL 软件库。

```bash
sudo apt install -y libscalapack-mpi-dev
sudo apt install -y libcereal-dev
```

## 4. <strong>安装 ELPA 软件库</strong>。（一般这里容易出问题）

如果你的系统是 Ubuntu 22.04，那么你可以以很简单的方式成功安装 ELPA：

```bash
sudo apt install -y libelpa-dev
```

如果你的系统不是 Ubuntu 22.04，很可惜，你需要稍微辛苦一点来安装 ELPA。但别急，这也并不难！

手动编译安装 ELPA 可以分为以下几步：

- 下载并进入 ELPA 目录：

```bash
wget https://elpa.mpcdf.mpg.de/software/tarball-archive/Releases/2021.05.002/elpa-2021.05.002.tar.gz
tar xzf elpa-2021.05.002.tar.gz 
cd elpa-2021.05.002
mkdir build  && cd build
```

- `configure`

```bash
../configure --enable-openmp CFLAGS="-O3 -march=native -funsafe-loop-optimizations -funsafe-math-optimizations -ftree-vect-loop-version -ftree-vectorize" FCFLAGS="-O2 -mavx" --disable-avx512
```

- 编译安装

```bash
make -j`nproc`
make install
ln -s /usr/local/include/elpa_openmp-2021.05.002/elpa /usr/local/include/
```

> 注意：`ln -s /usr/local/include/elpa_openmp-2021.05.002/elpa /usr/local/include/ ` 是非常重要的！（很多用户是这里出的问题！）

## 5. 开始编译并安装 `abacus`。

```bash
cmake -B build
cd build && make -j`nproc`
```

可以看到在当前目录下，已经编译成功了 `abacus` 可执行文件。

`abacus` 就是完整版的 ABACUS，它同时支持两种基矢量，而且还是并行版本！
