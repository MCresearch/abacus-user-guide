# Intel oneAPI 编译 ABACUS 教程

<strong>作者：韩昊知，邮箱：haozhi.han@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/09/21</strong>

# 一、前言

非特殊情况，linux 系统会默认安装 [GCC](https://gcc.gnu.org/)（GNU Compiler Collection）编译器套件。因此如果你的机器默认没有 [Intel® oneAPI Toolkits](https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#gs.5x6evn)，那么建议，你可以直接看上一篇文章：[GCC 编译 ABACUS 教程](abacus-intel.md) 。

如果您的机器恰好有 Intel® oneAPI Toolkits，那么您也可以使用它来编译 ABACUS。

# 二、关于 Intel® oneAPI Toolkits

Intel® oneAPI Toolkits 分为很多个版本的 Toolkit，这里解释下 Intel® oneAPI Base Toolkit 和 Intel® oneAPI HPC Toolkit 的区别。

简单来说：Intel® oneAPI HPC Toolkit 包含 Intel® oneAPI Base Toolkit。

Intel® oneAPI Base Toolkit 中包含：Intel® oneAPI Math Kernel Library（简称为 MKL），这个软件库里面包含了大量常用的数学库，包括 ABACUS 依赖的 `BLAS`、`LAPACK`、`FFTW3` 和 `ScaLAPACK` 4 个软件库。

因此使用 Intel oneAPI 来编译 ABACUS，可以省去逐个去安装数学库的过程！

Intel® oneAPI HPC Toolkit 相比于 Intel® oneAPI Base Toolkit 多了一些必要的 Intel 的编译器以及 <strong>Intel® MPI Library</strong>（ABACUS 想要编译并行版本必须的关键库）。

总结一下，使用 Intel oneAPI 编译 ABACUS，必须确保你的机器中包含<strong> Intel® oneAPI HPC Toolkit</strong>。

> 关于 Intel® oneAPI Toolkits 更详细的信息：[https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#hpc-kit](https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#hpc-kit)

# 三、编译 安装

开启 Intel® oneAPI Toolkits：

```powershell
source /opt/intel/oneapi/setvars.sh
```

## 1. 安装 仅支持 PW 基组的 ABACUS

对于仅支持 PW 基组的 ABACUS，我们同时支持两种版本的编译：串行版本和并行版本。

ABACUS 的 PW 基组只依赖：`BLAS`、`LAPACK`、`FFTW3` 三个数学库，而这三个数学库都已经被 Intel® oneAPI Base Toolkit 中包含：Intel® oneAPI Math Kernel Library（简称为 MKL）所包含，因此我们不需要再安装其他的软件库！

### 1.1 编译串行版本

```powershell
CXX=icpx cmake -B build -DENABLE_MPI=OFF
cd build && make -j`nproc`
```

> 注意，这里必须指定<strong>CXX=icpx</strong>，不然系统会使用默认的 `CXX` 编译器。同时这里的 `CXX` 也不要指定 `icpc`，icpc 是 Intel® C++ Compiler Classic，会带来一些报错。

可以看到在当前目录下，已经编译成功了 `abacus_pw_serial` 可执行文件。

`abacus_pw_serial` 就是串行版本的支持平面波基组的 ABACUS。

### 1.2 编译并行版本

```powershell
CXX=icpx cmake -B build -DENABLE_LCAO=OFF
cd build && make -j`nproc`
```

可以看到在当前目录下，已经编译成功了 `abacus_pw` 可执行文件。

`abacus_pw` 就是并行版本的支持平面波基组的 ABACUS。

## 2. 安装 支持两种基组的 ABACUS

对于同时支持两种基组的 ABACUS，仅可以编译并行版本。<strong>并无串行版本。</strong>

完整版的 ABACUS 需要依赖更多的软件库：`BLAS`、`LAPACK`、`FFTW3`、<strong>ScaLAPACK</strong>、<strong>CEREAL</strong>、<strong>ELPA</strong>共 6 个。

而前四个数学库（`BLAS`、`LAPACK`、`FFTW3`、`ScaLAPACK`）都已经被 Intel MKL 所包含，因此我们只需再额外安装<strong>CEREAL</strong>、<strong>ELPA</strong>即可。

### 2.1 安装 CEREAL

```powershell
sudo apt install -y libcereal-dev
```

### 2.2 安装 ELPA

<strong>如果你的系统是 Ubuntu 22.04</strong>，那么你可以以很简单的方式成功安装 ELPA。

```powershell
sudo apt install -y libelpa-dev
```

<strong>如果你的系统不是 Ubuntu 22.04</strong>，很可惜，你需要稍微辛苦一点来安装 ELPA。但别急，这也并不难！

> 注意；这里手动编译安装 ELPA 的方法与在 GCC 下编译不太一样，因为要保证 ELPA 和 ABACUS 都是基于 Intel oneAPI 来编译的！

手动编译安装 ELPA 可以分为以下几步：

- 下载并进入 ELPA 目录：

```powershell
wget https://elpa.mpcdf.mpg.de/software/tarball-archive/Releases/2021.05.002/elpa-2021.05.002.tar.gz
tar xzf elpa-2021.05.002.tar.gz 
cd elpa-2021.05.002
mkdir build  && cd build
```

- `configure`

```powershell
CC=mpiicc CXX=mpiicpc FC=mpiifort ../configure --enable-openmp FCFLAGS="-qmkl=cluster"
```

- 编译安装

```powershell
make -j`nproc`
make install
ln -s /usr/local/include/elpa_openmp-2021.05.002/elpa /usr/local/include/
```

> 注意：`ln -s /usr/local/include/elpa_openmp-2021.05.002/elpa /usr/local/include/ ` 是非常重要的！（很多用户是这里出的问题！）

### 2.3 编译安装 ABACUS

```powershell
CXX=icpx cmake -B build
cd build && make -j`nproc`
```

可以看到在当前目录下，已经编译成功了 `abacus` 可执行文件。

`abacus` 就是完整版的 ABACUS，它同时支持两种基矢量，而且还是并行版本！
