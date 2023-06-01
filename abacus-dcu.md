# ABACUS 在曙光 DCU 集群上的编译与使用

<strong>作者：贾志炜，邮箱：</strong><strong>jiazhiwei@stu.pku.edu.cn</strong><strong>，审阅：韩昊知，最后更新时间：2023/06/01</strong>

# 1. 介绍

本教程旨在介绍 ABACUS 在 [曙光 DCU 计算平台](https://ac.sugon.com/) 上的编译与使用。

## DCU

- DCU (Deep Computing Unit) 是一款面向人工智能、科学计算的高性能全功能 GPGPU (General-Purpose computing on Graphics Processing Units) 加速卡。
- 中科海光基于 DCU 硬件提供完整的软件工具链，以 DTK(DCU toolkit)为基础软件层为开发者提供运行、编译、调试和性能分析等功能，并提供多种深度优化的计算加速库。DCU 加速卡支持 ROCm/Hip 并行架构。
- 曙光计算集群采用 CPU 和 DCU 加速卡（Deep Computing Unit）相结合的异构融合计算体系结构。

## ABACUS 的异构并行计算

INPUT 文件中 device 参数需设置为 `gpu`。

目前 GPU/DCU 版本的 ABACUS 仅支持 PW 基组的计算，因此 INPUT 文件中 `basis_type` 参数仅能设置为 `pw`。

# 2. 准备

## 曙光计算平台

用户需要在平台上申请异构计算资源：

[https://ac.sugon.com/doc/1.0.6/30000/general-handbook/platform/source.html](https://ac.sugon.com/doc/1.0.6/30000/general-handbook/platform/source.html)

## E-shell

曙光计算平台采用 E-shell 来对管理节点进行操作。

- 可使用网页版或 [E-Shell Client](https://ac.sugon.com/doc/1.0.6/30000/general-handbook/User-Guide/E-Shell-Client.html)。
- 不可直接运行任务，而是使用 Slurm 调度系统。
- 采用 [modules 工具](https://modules.readthedocs.io/en/latest/index.html) 来管理环境变量与系统依赖项。许多依赖如编译器版本等可以通过 modules 来处理。

## slurm

Slurm 工作调度工具是面向 Linux 和 Unix 及类似内核的免费和开源工作调度程序，可以方便用户进行作业的提交、管理、监测。

- `sinfo`: 查看系统资源。
- `squeue`: 查看当前作业状态。
- <strong>s</strong><strong>alloc</strong>: 分配节点的作业提交，用 salloc 申请的节点会在当前终端退出时释放掉。用于程序测试以及中小型任务的提交。
- <strong>s</strong><strong>batch</strong>: 批处理模式的作业提交，需要编写 slurm 作业提交脚本。在 E-shell 的默认目录存有 slurm 脚本模板。在下面的流程中也会介绍提交 ABACUS 任务的脚本案例。
- `srun`: 交互式提交作业命令，有屏幕输出，但容易受网络波动影响，断网或关闭窗口会导致作业中断。

# 3. 流程

## 配置超算环境

```bash
module avail    # 列出已有环境
module list <strong>    </strong><strong>#</strong> 查看当前已加载环境
module load     # 加载环境
module unload   # 卸载环境
```

- 昆山节点

```bash
module purge
1) compiler/devtoolset/7.3.1
2) compiler/rocm/dtk-22.10 
3) compiler/cmake/3.17.2 
4) mpi/hpcx/2.6.0/gcc-7.3.1
```

- 乌镇节点

```bash
1) compiler/devtoolset/7.3.1
2) compiler/dtk/21.10          
3) compiler/cmake/3.23.1
4) mpi/hpcx/gcc-7.3.1
```

对于使用其他 DCU 节点（合肥、哈尔滨、西安）的用户，如果 module 中没有找到类似的环境，欢迎在 [ABACUS 仓库](https://github.com/deepmodeling/abacus-develop) 提出 issue，我们将尽力协助解决。

## 编译 ABACUS 依赖软件包

目前按照 DCU 版本已验证的编译方法，有三个数学库需要自行编译。

若曙光平台网络连接不畅，请在软件官网选择合适的软件包，再用曙光平台的 E-File 传送至节点。

- FFTW: [https://fftw.org/pub/fftw/fftw-3.3.10.tar.gz](https://fftw.org/pub/fftw/fftw-3.3.10.tar.gz)
- OpenBLAS: [https://github.com/xianyi/OpenBLAS/releases/download/v0.3.21/OpenBLAS-0.3.21.tar.gz](https://github.com/xianyi/OpenBLAS/releases/download/v0.3.21/OpenBLAS-0.3.21.tar.gz)
- ScaLAPACK: [https://github.com/Reference-ScaLAPACK/scalapack/archive/refs/tags/v2.2.0.tar.gz](https://github.com/Reference-ScaLAPACK/scalapack/archive/refs/tags/v2.2.0.tar.gz)

### 3.1 编译 FFTW

```bash
tar -zxvf fftw-3.3.10.tar.gz

mkdir build
./configure --prefix=/work/home/your_username/fftw-3.3.10/build
cd ~/fftw-3.3.10/build
make 
make install
```

FFTW 需要编译单精度版本和双精度版本：

```bash
cd ~/fftw-3.3.10/build
./configure --prefix=/work/home/your_username/fftw-3.3.10/build <strong>--enable-float</strong>
make 
make install
```

### 3.2 编译 OpenBLAS

```bash
tar -zxvf OpenBLAS-0.3.23.tar.gz
cd OpenBLAS-0.3.23

make USE_OPENMP=1 NO_AVX512=1 FC="gfortran -fPIC" CC="gcc -fPIC" -j8
mkdir build 
make PREFIX=/work/home/your_username/OpenBLAS-0.3.21/build install
```

### 3.3 编译 ScaLAPACK

```bash
cp SLmake.inc.example SLmake.inc
```

复制包中提供的 SLmake.inc.example 作为基准，并对 SLmake.inc 的内容作出一部分修改:

```bash
FC            = mpif90 -fPIC
CC            = mpicc -fPIC
BLASLIB       =
LAPACKLIB     = -L/work/home/your_username/OpenBLAS-0.3.21/build/lib -lopenblas
```

```bash
make
```

## 编译 DCU 版本的 ABACUS

```bash
git clone https://gitee.com/deepmodeling/abacus-develop  # main分支
cd abacus-develop
mkdir build
cd build
```

- CMake 配置：

指定编译器为 clang，关闭 OpenMP、LCAO 计算模块，设定三个数学库的位置，设定 USE_ROCM=ON。

```bash
CC=clang CXX=clang++ cmake -B build -DUSE_OPENMP=OFF -DENABLE_LCAO=OFF \
-DFFTW3_DIR=/work/home/your_username/fftw-3.3.10/build/ \
-DLAPACK_DIR=/work/home/your_username/OpenBLAS-0.3.21/build/lib \
-DSCALAPACK_DIR=/work/home/your_username/scalapack-2.2.0/ \
-DUSE_ROCM=ON
```

- Make 编译：make 部分建议不要并行编译。

```bash
make
```

## 提交任务

- salloc（中小型任务与交互性程序测试）

```bash
salloc -p [队列名] -N 1 -n 32 --gres=dcu:4

... load text ...

salloc: Waiting for resource configuration
salloc: Nodes node_num are ready for job  # 分配计算节点，可用ssh直接连接

ssh node_num

...交互式进行计算任务
```

- sbatch（大型任务与批量提交）

  - 写一个作业提交脚本，可以参考以下结构：

```bash
#!/bin/bash
#SBATCH --job-name=ABACUS_GPU 
#SBATCH --partition=kshdnormal
#SBATCH --nodes=1 
#SBATCH --output=output.log    
#SBATCH --ntasks-per-node=32  
#SBATCH --mail-user=username@email  
<strong>#SBATCH --gres=dcu:4  #dcu个数</strong>
#SBATCH --time=01:00:00  
#SBATCH --error=error.log   

#以上的SBATCH信息会由slurm识别
abacus=/work/home/your_username/abacus-develop/build/abacus_pw
#设置环境
module purge
module load compiler/devtoolset/7.3.1
module load compiler/rocm/dtk-22.10 
module load compiler/cmake/3.17.2 
module load mpi/hpcx/2.11.0/gcc-7.3.1
#运行脚本
cd your_task_path 
mpirun -np 4 $abacus
```

```bash
sbatch abacus_dcu.slurm
```

作业已提交，可在“作业管理”中查看。

# 4. 结语

DCU 可以提高 ABACUS 计算性能，也充分利用了 ROCm 并行框架，使得 ABACUS 异构计算能应用在更多的平台上。
