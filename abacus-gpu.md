# 编译 Nvidia GPU 版本的 ABACUS

<strong>作者：韩昊知，邮箱：haozhi.han@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2024/03/15</strong>

# 一、介绍

本教程旨在介绍 ABACUS 在支持 NVIDIA GPU 的服务器上的编译与使用。

## 当前 ABACUS 支持的 GPU 并行计算

- <strong>INPUT 文件中 device 参数需设置为 gpu。</strong>
- 目前 GPU 版本的 ABACUS 仅支持 PW 基组的计算，因此 INPUT 文件中 `basis_type` 参数仅能设置为 `pw`。

> 详细请看官方文档：[https://abacus.deepmodeling.com/en/latest/advanced/acceleration/cuda.html](https://abacus.deepmodeling.com/en/latest/advanced/acceleration/cuda.html)
> LCAO 基组的 GPU 计算版本近期会发布。

## NVIDIA GPU & CUDA

NVIDIA GPU (Graphics Processing Unit)  是由一种专门设计来处理图形和并行计算任务的电子芯片。自从 NVIDIA 推出其首款 GPU 以来，它们已经从仅仅处理视频游戏图形的设备发展成为能处理各种高性能计算和深度学习任务的强大工具。

CUDA（Compute Unified Device Architecture），是显卡厂商 NVIDIA 推出的运算平台。 CUDA 是一种由 NVIDIA 推出的通用并行计算架构，该架构使 NVIDAI GPU 能够解决复杂的计算问题。

为了使 ABACUS 的部分功能支持 NVIDIA GPU，ABACUS 开发团队针对 NVIDIA GPU 写了大量的 CUDA 代码，使其在 NVIDIA GPU 上有较高的运行效率。相比于 CPU 版本的计算任务，有极高的效率提升！

> 新闻稿：[https://mp.weixin.qq.com/s/D8gcQb0bikMdgizLsbvCfQ](https://mp.weixin.qq.com/s/D8gcQb0bikMdgizLsbvCfQ)

# 二、检查环境

检查当前环境是否有 NVIDIA GPU

- `nvidia-smi` 命令帮助检测你的服务器是否有 NVIDIA GPU 设备。
- `nvcc --version` 命令帮助你检测你的服务器软件环境中是否包含 cuda toolkit

> 更详细的内容查看：[https://abacus.deepmodeling.com/en/latest/advanced/acceleration/cuda.html#required-hardware-software](https://abacus.deepmodeling.com/en/latest/advanced/acceleration/cuda.html#required-hardware-software)

# 三、编译

如果您已经尝试过使用 <strong>GCC 编译 ABACUS 教程 </strong>或者<strong> Intel oneAPI 编译 ABACUS 教程</strong>，那么编译支持在 NVIDIA GPU 上运行的 ABACUS 十分简单。

在保证可以正常编译 CPU 版本的 ABACUS 的环境下，使用：

```bash
cmake -B build -DUSE_CUDA=1 # for GCC 
cd build && make -j`nproc`
# or
CXX=icpx cmake -B build -DUSE_CUDA=1 # for Intel oneAPI
cd build && make -j`nproc`
```

这样编译出来的 `abacus` 可执行文件就是支持 NVIDIA GPU 运行的 ABACUS。
