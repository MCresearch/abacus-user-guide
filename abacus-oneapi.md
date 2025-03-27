# Intel oneAPI 2024/2025 编译 ABACUS 教程

**作者：陈诺，邮箱：cn037@stu.pku.edu.cn**

**最后更新时间：2025/03/22**

# Intel OneAPI 工具链

> 🎂
> **本教程适用于 2024.0 及更新版本的 oneAPI。**

## 简介

本教程介绍如何使用 Intel oneAPI 2024/2025 工具链编译 ABACUS。

和之前的版本相比，新的 oneAPI 工具链在编译器等方面有较大变化。

oneAPI 2024 中，Intel® C++ Compiler Classic (icc) 停止使用，并使用了新的目录布局。

oneAPI 2025 中，Intel® Fortran Compiler Classic (ifort) 停止使用。

### OneAPI Base Toolkit

OneAPI Base Toolkit 提供了一系列基础工具和库，包括 `BLAS`, `LAPACK`, `ScaLAPACK` and `FFTW3` 等关键组件：

- **Intel® oneAPI DPC++/C++ Compiler**：面向 CPU、GPU、FPGA 的 C++ 编译器。
- **Intel® oneAPI DPC++ Library**：提供并行算法的库。
- **Intel® oneAPI Math Kernel Library**：即 MKL，提供高度优化的数学函数库，包括线性代数、FFT 等。
- **Intel® VTune™ Profiler**：性能分析优化工具。

### OneAPI HPC Toolkit

OneAPI HPC Toolkit 是为高性能计算（HPC）特别优化的工具集，它在 OneAPI Base Toolkit 的基础上增加了更多针对 HPC 应用的特性和工具，包括：

- **Intel® oneAPI DPC++/C++ Compiler**：含有 C++ MPI 编译器。
- **Intel® Fortran Compiler & Intel® Fortran Compiler Classic**：Fortran 编译器。
- **Intel® MPI Library**：MPI 库。

## 安装

可以从官网上获得最新的安装包。安装需要管理员权限。

[Download the Intel® oneAPI Base Toolkit](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html?operatingsystem=linux&linux-install-type=offline)

[Download the Intel® HPC Toolkit](https://www.intel.com/content/www/us/en/developer/tools/oneapi/hpc-toolkit-download.html?operatingsystem=linux&linux-install-type=offline)

以 **2024.2 版本**为例，展示配置环境和安装 ABACUS 的流程。

### Offline installer
#### Base Toolkit
- 下载

```bash
wget https://registrationcenter-download.intel.com/akdlm/IRC_NAS/9a98af19-1c68-46ce-9fdd-e249240c7c42/l_BaseKit_p_2024.2.0.634_offline.sh
```
- 安装，可选图形化界面安装
```bash
sudo sh ./l_BaseKit_p_2024.2.0.634_offline.sh
```
- 或直接在shell中静默安装
```bash
sudo sh ./l_BaseKit_p_2024.2.0.634_offline.sh -a --silent --cli --eula accept
```
#### HPC Toolkit
- 下载
```bash
wget https://registrationcenter-download.intel.com/akdlm/IRC_NAS/d4e49548-1492-45c9-b678-8268cb0f1b05/l_HPCKit_p_2024.2.0.635_offline.sh
```
- 安装，类似
```bash
sudo sh ./l_HPCKit_p_2024.2.0.635_offline.sh -a --silent --cli --eula accept
```
- 按照默认配置，全局安装目录位于`/opt/intel/oneapi`。以2024.2版本为例，该目录如下：
```bash
➜  oneapi ls
2024.2   basekit  common    dal       dev-utilities  dnnl      dpl     installer  ippcp      logs  modulefiles-setup.sh  setvars.sh   tbb  vtune
advisor  ccl      compiler  debugger  diagnostics    dpcpp-ct  hpckit  ipp        licensing  mkl   mpi                   support.txt  tcm
```
- 其中有一些重要的目录和工具，如 `2024.2/` 和 `installer/`

## 环境变量设置

要使用 oneAPI 提供的编译器和库，需要正确设置环境。

- 2024.0 及之后的版本，使用了新的目录布局。这导致了和老版本不同的环境配置方式。

> 参见 [Use the setvars and oneapi-vars Scripts with Linux*](https://www.intel.com/content/www/us/en/docs/oneapi/programming-guide/2024-2/use-the-setvars-and-oneapi-vars-scripts-with-linux.html)

- 和之前的版本相比，由组件目录布局（Component Directory Layout）改为统一目录布局（Unified Directory Layout），新版本的所有组件（bin, lib, include, share）等统一放在以工具包版本号命名的顶级目录中。
- 在原先的 Component Directory Layout 中，不同的组件有各自的环境变量设置脚本，由一个位于 oneAPI 安装目录的脚本 `/opt/intel/oneapi/setvars.sh` 统一管理。新版的 Unified Directory Layout 中，每个组件被集中到组件共用的共享文件夹中，即每个组件将其头文件提供给一个公共的 include 文件夹，将其库文件提供给一个公共的 lib 文件夹，以此类推。这样，不同版本工具包之间的切换更容易，无需维护通用的 `setvars.sh`，而是通过工具包版本号命名的目录提供的脚本 `/opt/intel/oneapi/<toolkit-version>/oneapi-vars.sh` 设置。
- 以 2024.2 为例，每次使用 icpx 等编译器之前，需要在 shell 环境中 source 一次脚本：

```bash
. /opt/intel/oneapi/2024.2/oneapi-vars.sh
# configure, build, ...
```

此时，编译器应该被添加到环境中，可以运行命令检查是否正确配置：

```bash
# source前
➜  oneapi mpiicpx -v
zsh: command not found: mpiicpx
# source后
➜  oneapi mpiicpx -v
mpiicpx for the Intel(R) MPI Library @IMPI_OFFICIALVERSION@ for Linux*
Copyright Intel Corporation.
Intel(R) oneAPI DPC++/C++ Compiler 2024.2.0 (2024.2.0.20240602)
Target: x86_64-unknown-linux-gnu
Thread model: posix
InstalledDir: /opt/intel/oneapi/compiler/2024.2/bin/compiler
Configuration file: /opt/intel/oneapi/compiler/2024.2/bin/compiler/../icpx.cfg
Found candidate GCC installation: /usr/lib/gcc/x86_64-linux-gnu/11
Selected GCC installation: /usr/lib/gcc/x86_64-linux-gnu/11
Candidate multilib: .;@m64
Selected multilib: .;@m64
icpx: warning: argument unused during compilation: '-I /opt/intel/oneapi/2024.2/include' [-Wunused-command-line-argument]
```

> 🎂
> source 和.命令

- `.` 命令在 POSIX 标准中定义，因此它在所有 POSIX 兼容的 shell 中都应该可用。
- `source` 命令一般情况下是 `.` 的别名，但在某些环境中不可用。如果脚本不能使用 source，请换成通用的 `.`.

这一步会配置环境变量，但是并不会设定默认的 C++ 编译器。因此，设置了 oneAPI 编译器的环境变量之后，还需要在配置（configure）时指定构建（build）采用的编译器，如 `CXX=icpx`。

- **2024.0** 开始，原先的 classical 编译器停止使用。

> [Intel® C++ Compiler Classic Release Notes](https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-c-compiler-release-notes.html)

请使用新的 `icpx/mpiicpx` 取代原来的 `icpc/mpiicpc`。

# abacus 安装

## 依赖库

### 安装 cereal

```bash
sudo apt install libcereal-dev
```

### 安装 elpa

在 Ubuntu22.04 等发行版中，可以通过 apt 获取预构建的 elpa 包（pre-build packages）。不幸的是，使用不同的 MPI 库构建 elpa 可能会导致冲突，apt 获取的 elpa 包和 oneAPI 2024.2 构建的 abacus 在运行时可能出现问题。

```bash
/usr/bin/ld: warning: libmpi.so.40, needed by /usr/lib/x86_64-linux-gnu/libelpa.so, may conflict with libmpi.so.12
```

运行算例时报错：

```bash
* * * * * *
 << Start SCF iteration.
Abort(403251971) on node 0 (rank 0 in comm 0): Fatal error in internal_Bcast: Unknown error class, error stack:
internal_Bcast(4152): MPI_Bcast(buffer=0x2c0e960, count=1, INVALID DATATYPE, 1, comm=0xc400001b) failed
internal_Bcast(4112): Invalid datatype
Abort(67707651) on node 1 (rank 1 in comm 0): Fatal error in internal_Bcast: Unknown error class, error stack:
internal_Bcast(4152): MPI_Bcast(buffer=0x2fcdac0, count=1, INVALID DATATYPE, 1, comm=0xc4000013) failed
internal_Bcast(4112): Invalid datatype
```

因此，我们需要手动利用 oneAPI 工具链构建 elpa。

#### 使用 toolchain

由于 elpa 的编译较复杂，我们可以通过 abacus toolchain 脚本自动构建和安装 elpa。该脚本用 icpx 和 mpiicpc 编译 elpa，同时会默认安装 cereal 和 libxc。

[一键配置编译 ABACUS | toolchain 脚本的使用](https://bohrium.dp.tech/notebooks/5215742477)

```bash
. /opt/intel/oneapi/2024.2/oneapi-vars.sh
cd abacus-develop/toolchain
./toolchain_intel.sh # 脚本将会用intel工具链安装依赖。
```

安装完成的库目录为 `abacus-develop/toolchain/install`.

```bash
# 安装完成的库目录为abacus-develop/toolchain/install
 ➜  toolchain git:(develop) ✗ ls install
cereal-1.3.2  cmake-3.28.1  elpa-2023.05.001  libxc-6.2.2  lsan.supp  setup  toolchain.conf  toolchain.env  tsan.supp  valgrind.supp
```

- 使用 toolchain 构建的 elpa，在构建 abacus 时有警告如下，暂未发现影响使用。该问题由 scalapack 库未指定 mkl 版本导致，“自行编译安装”方式（见下）无此问题。

> 参见 [2.4 Non standard paths or non standard libraries](https://gitlab.mpcdf.mpg.de/elpa/elpa/-/blob/master/documentation/INSTALL.md#24-non-standard-paths-or-non-standard-libraries)

```bash
/usr/bin/ld: warning: libmpi.so.40, needed by /lib/x86_64-linux-gnu/libscalapack-openmpi.so.2.1, may conflict with libmpi.so.12
```

除了使用 toolchain，也可以根据 [documentation/INSTALL.md · master · elpa / elpa · GitLab](https://gitlab.mpcdf.mpg.de/elpa/elpa/-/blob/master/documentation/INSTALL.md)，自行编译安装 elpa。

#### 自行编译安装

自行下载和安装 elpa 到环境中。以 oneAPI 2024.2 和 elpa-2024.05.001 为例。

- 在官网下载 elpa 包。

```bash
wget https://elpa.mpcdf.mpg.de/software/tarball-archive/Releases/2024.05.001/elpa-2024.05.001.tar.gz

tar xvf elpa-2024.05.001.tar.gz
```

- 以 oneAPI 2024.2 为例提供一个安装脚本，仅供参考。这一步可能需要几分钟。如果运行脚本时显示 oneAPI warnings 提示已经设置过环境变量并退出，请打开一个新的 shell 环境，执行安装脚本。最后的 `make install和ln` 需要 sudo 权限，如果无法提供，请手动完成这两步。
- oneAPI **2025.0 开始**，Intel® Fortran Compiler Classic (ifort) 停止使用。

> [Intel® HPC Toolkit Release Notes](https://www.intel.cn/content/www/cn/zh/developer/articles/release-notes/oneapi-hpc-toolkit/2025.html)

请使用新的 `ifx/mpiifx` 取代原来的 `ifort/mpiifort`。

请根据实际情况，指定安装脚本中的 oneAPI 工具链版本。如果使用 oneAPI 2025.0 之后的版本，请把 21 行 `FC=mpiifort` 替换为 `FC=mpiifx`。

```bash
cd elpa-2024.05.001
```

```bash
#!/bin/bash -e

# buildelpa.sh
# run in elpa main dir

# source oneAPI environments
echo "using oneAPI 2024.2"
. /opt/intel/oneapi/2024.2/oneapi-vars.sh \
|| { echo "Failed to load oneAPI environment. Please restart in a new shell without oneAPI vars set."; false; }

# in elpa main dir
# check whether there is a 'build' directory
if [ -d "build" ]; then
    echo "rm -rf build"
    rm -rf build
fi
mkdir build && cd build

MKL_HOME=/opt/intel/oneapi/2024.2

__CC=mpiicx CXX=mpiicpx FC=mpiifort ../configure \
--disable-avx --disable-avx2 --disable-avx512 --disable-sse --disable-sse-assembly \
SCALAPACK_LDFLAGS="-L$MKL_HOME/lib/ -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_sequential \
                             -lmkl_core -lmkl_blacs_intelmpi_lp64 -lpthread -lm -Wl,-rpath,$MKL_HOME/lib/" \
SCALAPACK_FCFLAGS="-L$MKL_HOME/lib/ -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_sequential \
                    -lmkl_core -lmkl_blacs_intelmpi_lp64 -lpthread -lm -I$MKL_HOME/include/mkl/intel64/lp64"

make -j$(nproc) > make.log 2>&1 
echo "installation process may require administrative privileges."
read -p "Would you like to continue with 'sudo make install'? (y/n): " -n 1 -r
echo    # (Optional) Move to a new line

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Proceeding with installation using administrative privileges..."
    sudo make install > install.log 2>&1 
else
    echo "Installation has been canceled."
    echo "Please manually execute 'make install' and link elpa to default path."
fi

# link elpa to /usr/local/include

# The target path for the symbolic link
LINK_PATH="/usr/local/include/elpa"
# The source path for the original link (replace with the actual source path)
SOURCE_PATH="/usr/local/include/elpa-2024.05.001/elpa"

# Check if the link exists
if [ -L "$LINK_PATH" ]; then
    # If the link exists, delete it
    echo "The link already exists, deleting the old link..."
    sudo rm "$LINK_PATH"
else
    # If the link does not exist, check for the presence of a file or directory
    if [ -e "$LINK_PATH" ]; then
        echo "A file or directory exists at the path, unable to create the link. Please delete or rename the file/directory first."
        exit 1
    fi
fi

# Create a new symbolic link
sudo ln -s "$SOURCE_PATH" "$LINK_PATH"

# Check if the link was created successfully
if [ -L "$LINK_PATH" ]; then
    echo "The new symbolic link has been created successfully."
else
    echo "Failed to create the symbolic link."
    exit 1
fi

echo "elpa install over."
```

## 安装 ABACUS

配置好依赖后，我们可以开始安装 ABACUS。

如果你使用 toolchain 配置环境，那么 toolchain 提供了一系列环境变量和构建工具。构建时，请利用 `abacus-develop/toolchain/build_abacus_intel.sh` 脚本直接构建 ABACUS（在其中修改配置选项），也可以手动构建。（不推荐）

如果需要手动安装 ABACUS 并使用 toolchain 的 ELPA：需要记住此前 toolchain 安装 elpa 的目录。

如果之前选择手动安装 ELPA，可以用默认方式自行用 cmake 构建。

```bash
# 设置环境
. /opt/intel/oneapi/2024.2/oneapi-vars.sh
# configure
# 在此选择oneAPI的编译器，添加编译选项，指定此前的安装路径，如
CXX=mpiicpx cmake -B build \
-DELPA_DIR=~/abacus-develop/toolchain/install/elpa-2023.05.001/cpu/
# 根据需要添加其他cmake选项

# build
cmake --build build -j`nproc` 
# install
cmake --install build
```

# 常见问题和解决方法

- 在开始构建之前，请清除原有的 build 目录。

```bash
rm -rf build
```

- 找不到编译器，记得运行 vars 脚本设置 oneAPI 环境变量。

```bash
CMake Error at /usr/share/cmake-3.22/Modules/CMakeDetermineCXXCompiler.cmake:48 (message):
  Could not find compiler set in environment variable CXX:

  mpiicpx.

Call Stack (most recent call first):
  CMakeLists.txt:7 (project)


CMake Error: CMAKE_CXX_COMPILER not set, after EnableLanguage
-- Configuring incomplete, errors occurred!

# 请设置环境
. /opt/intel/oneapi/2024.2/oneapi-vars.sh
```

- 找不到 elpa，请在配置时指定安装路径。

```bash
CMake Error in CMakeLists.txt:
  Imported target "ELPA::ELPA" includes non-existent path

    "/usr/include/elpa"

  in its INTERFACE_INCLUDE_DIRECTORIES.  Possible reasons include:

  * The path was deleted, renamed, or moved to another location.

  * An install or uninstall procedure did not complete successfully.

  * The installation package was faulty and references files it does not
  provide.


# 请指定ELPA_DIR（及其他自己手动构建的库）
CXX=mpiicpx cmake -B build \
-DELPA_DIR=~/abacus-develop/toolchain/install/elpa-2023.05.001/cpu/
```

- 期望使用 intel 工具链编译，但 cmake 显示使用 GNU 工具链。请使用 CXX=mpiicpx 指定编译器。

```bash
cmake -B build -DELPA_DIR=~/abacus-develop/toolchain/install/elpa-2023.05.001/cpu/
-- The CXX compiler identification is GNU 11.4.0

# CXX=mpiicpx cmake ...
# -- The CXX compiler identification is IntelLLVM 2024.2.0
```

- cmake 提示编译器错误，请使用新版的 icpx/mpiicpx，而不是 icpc/mpiicpc

```bash
CMake Error at /usr/share/cmake-3.22/Modules/CMakeTestCXXCompiler.cmake:62 (message):
  The C++ compiler

    "/opt/intel/oneapi/2024.2/bin/mpiicpc"

  is not able to compile a simple test program.
  
# use CXX=mpiicpx instead of CXX=mpiicpc
```

- 运行了 oneAPI 配置环境变量脚本，但是链接错误

  - 请检查 oneAPI HPC kits 的安装；可进入 installer 查看当前安装的所有 Toolkits 和对应版本，见下条。
  - 使用 `/opt/intel/oneapi/2024.2/oneapi-vars.sh`，而不是 `/opt/intel/oneapi/setvars.sh`
- 如果安装了多版本的 oneAPI 工具链，怀疑环境遭到破坏，可以使用 `/opt/intel/oneapi/installer` 中的 `installer` 工具修复和移除不需要版本以及更新。

```bash
cd /opt/intel/oneapi/installer
sudo ./installer

# 可以用Repair尝试修复环境
# 使用Remove移除不需要的组件
# 使用Update获得新版本
```

- 如果遇到 `libmpi.so` 相关报错，可以用 `locate` 查看所有相关库。

```bash
locate libmpi.so
```

- 运行算例或测试失败，请确保最新构建后运行了 install 命令，且没有因为权限不足安装失败。

# 参考

Abacus 文档

[Easy Installation](https://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html)

[一键配置编译 ABACUS | toolchain 脚本的使用](https://bohrium.dp.tech/notebooks/5215742477)

[Intel oneAPI 编译 ABACUS 教程 · GitBook](https://mcresearch.github.io/abacus-user-guide/abacus-intel.html)

elpa

[documentation/INSTALL.md · master · elpa / elpa · GitLab](https://gitlab.mpcdf.mpg.de/elpa/elpa/-/blob/master/documentation/INSTALL.md)

Intel 文档

[Use the setvars and oneapi-vars Scripts with Linux*](https://www.intel.com/content/www/us/en/docs/oneapi/programming-guide/2024-2/use-the-setvars-and-oneapi-vars-scripts-with-linux.html)

[Intel® C++ Compiler Classic Release Notes](https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-c-compiler-release-notes.html)

[Porting Guide for DPCPP or ICX](https://www.intel.com/content/www/us/en/developer/articles/guide/porting-guide-for-icc-users-to-dpcpp-or-icx.html)

[Porting Guide for ifort Users to ifx](https://www.intel.com/content/www/us/en/developer/articles/guide/porting-guide-for-ifort-to-ifx.html)

[Intel® oneAPI Base Toolkit Release Notes](https://www.intel.com/content/www/us/en/developer/articles/release-notes/intel-oneapi-toolkit-release-notes.html)
