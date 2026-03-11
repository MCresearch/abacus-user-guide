# ABACUS 的多 GPU 矩阵求解器功能编译与使用

**作者：周徐源，邮箱：xy_z@pku.edu.cn**

**作者：邓子超，邮箱：dengzichao@pku.edu.cn**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2026/03/05**

# 背景介绍

ABACUS 的多 GPU 矩阵求解器功能基于 [NVHPC-SDK](https://developer.nvidia.com/hpc-sdk) 中的 [cuSOLVERMp](https://docs.nvidia.com/cuda/cusolvermp/) 模块实现，可高效支撑大规模密度泛函理论计算中的分布式稠密线性代数与本征值求解。

NVHPC‑SDK（NVIDIA HPC SDK），是 NVIDIA（英伟达公司）面向高性能计算推出的完整工具链，包含编译器、数学库、通信库与调试工具，是 GPU 加速 HPC 应用的标准开发平台。其前身可追溯到 **2013 年 7 月**：**NVIDIA 收购 PGI**，将其编译器技术纳入 GPU 计算生态，为后续 HPC SDK 奠定核心基础。**2013–2020 年**：PGI 编译器（`pgcc`/`pgc++`/`pgfortran`）成为 NVIDIA GPU 加速 HPC 的主力编译工具，深度支持 **CUDA Fortran** 与 **OpenACC**，广泛用于各类科学计算软件。**2020 年 5 月 14 日（GTC Digital）**：NVIDIA 正式**宣布推出 NVIDIA HPC SDK**，定位为 “面向 CPU+GPU 异构系统的全栈 HPC 开发平台”。**2020 年 8 月 5 日**：**v20.7 版本正式开源免费发布**，原 PGI 编译器统一更名为 `nvc`/`nvc++`/`nvfortran`，完成品牌整合。NVHPC‑SDK 首次将**编译器（nvc/nvc++/nvfortran）、数学库（cuBLAS/cuSOLVER/cuSOLVERMp）、通信库（NVSHMEM/NCCL）、调试工具（Nsight）**打包为单一 SDK，解决 HPC 开发者 “多工具链、多版本、难部署” 的痛点。

**2020–2022 年：**全面支持** CUDA 11.x–12.x**，强化多 GPU / 多节点通信（**NVSHMEM**）与分布式线性代数（**cuSOLVERMp**）能力。编译器支持 **C++17 并行算法自动 GPU 加速**、Fortran intrinsics GPU 化，降低传统 HPC 代码迁移门槛。

**2023 年**：加入对 **NVIDIA Grace CPU** 与 **Grace‑Hopper 超级芯片**的深度优化，支持统一内存编程。版本迭代至 **v23.x**，全面兼容 x86_64、Arm64、POWER 等架构。

**2024–2025 年：支持 Blackwell GPU（cc100/cc120）、CUDA 12.8–13.0**，持续提升 AI+HPC 融合场景性能 NVIDIA。优化 Arm 平台内存分配、标准并行（stdpar）编程模型，适配新一代超算架构。

**2026 年：**最新版本为** v25.11**，捆绑 CUDA 13.0。

cuSOLVERMp 则是 NVIDIA 提供的**分布式多节点 / 多 GPU 稠密线性代数库**，对标 ScaLAPACK 接口，支持 LU/Cholesky 等分解与线性系统求解，专为大规模矩阵并行计算优化。

# 编译安装

编译带 cusolvermp 支持的 ABACUS，需要在一般的 ABACUS 编译流程之前，先安装并加载 NVIDIA HPC SDK 环境。总体编译安装流程如下：

1. 安装 NVIDIA HPC SDK。 注意需要安装 >=23.5 版本的 HPC SDK，过早版本的 NVIDIA HPC SDK 可能出现兼容问题。
2. 加载 NVIDIA HPC SDK 环境。这里直接使用 NVIDIA 提供的 modulefile 即可。

a. 当 **NVIDIA HPC SDK 版本 <25.9** 时，`cusolvermp` 的通信功能依赖 **HPC-X** 组件，因此需要加载特定的 modulefile（`nvhpc-hpcx-cudaxx/xx.x`）。
      以 **HPC SDK 25.3** 为例，可按如下方式加载：

```bash
module use /opt/nvidia/hpc_sdk/modulefiles
module load nvhpc-hpcx-cuda12/25.3
```

b. 当 **NVIDIA HPC SDK 版本 ≥ 25.9** 时，`cusolvermp` 的通信功能改为使用 **NCCL**，不再依赖 **HPC-X** 组件，因此只需加载基础的 modulefile(`nvhpc/xx.x`) 即可。

以 **HPC SDK 26.1** 为例，可按如下方式加载：

```bash
module use /opt/nvidia/hpc_sdk/modulefiles
module load nvhpc/26.1
```

3. 编译 ABACUS。在编译 ABACUS 时候需设置 `"-DENABLE_CUSOLVERMP=ON"`

# 功能使用

在 `INPUT` 中设置 ks_solver：

```
# INPUT
ks_solver cusolvermp
```

注意：需要设置 MPI 进程数与 GPU 数一致。

祝大家使用愉快！
