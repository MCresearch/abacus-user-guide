# ABACUS+DeePMD-kit 做机器学习分子动力学

<strong>作者：刘裕，邮箱：liuyu@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2024/10/15</strong>

# 一、介绍

本教程旨在介绍结合 ABACUS（中文名原子算筹，这里基于 ABACUS 3.8.0 版本）和 DeePMD-kit 软件进行基于机器学习原子间势函数的分子动力学模拟。

DeePMD-kit 是一款基于神经网络拟合第一性原理数据得到势能模型，用于分子动力学模拟的软件。无需人工干预，其可以端对端地将用户提供的数据在数个小时内转化为深度势能模型，可以保持量子力学精度准确性的基础上，将分子动力学的计算速度提升数个量级。

如果不熟悉 DeePMD-kit 的读者，这里可以推荐大家先阅读 DeePMD-kit 的相关原理文档和说明，熟悉这部分的读者可以跳过：

- [https://docs.deepmodeling.com/projects/deepmd/en/r2/](https://docs.deepmodeling.com/projects/deepmd/en/r2/)
- [https://bohrium-doc.dp.tech/docs/software/DeePMD-kit](https://bohrium-doc.dp.tech/docs/software/DeePMD-kit)
- [https://mp.weixin.qq.com/s/hLULtXgwKbhuT2Zvy6XZLA](https://mp.weixin.qq.com/s/hLULtXgwKbhuT2Zvy6XZLA)
- [https://bohrium.dp.tech/notebooks/2649266844](https://bohrium.dp.tech/notebooks/2649266844)

# 二、准备

### 2.1 案例下载地址

ABACUS 的 MD 算例下载地址为（国内 gitee）：

[https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/md](https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/md)

可以采用的下载命令是：

`git clone https://gitee.com/mcresearch/abacus-user-guide.git`

之后进入 `/abacus-user-guide/examples/md/3_DPMD` 目录

或者采用 Github 仓库地址：

[https://github.com/MCresearch/abacus-user-guide/tree/master/examples/md](https://github.com/MCresearch/abacus-user-guide/tree/master/examples/md)

### 2.2 安装相关软件

#### 2.2.1 ABACUS

这里默认读者已经准备好 ABACUS 的安装环境和依赖软件，如还没有可以参考相关教程。

#### 2.2.2 DeePMD-kit

DeePMD-kit 安装教程请参考 DeePMD-kit 的线上文档：[https://docs.deepmodeling.com/projects/deepmd/en/r2/](https://docs.deepmodeling.com/projects/deepmd/en/r2/)

新手用户建议采用 [offline package](https://github.com/deepmodeling/deepmd-kit/releases) 方式安装 DeePMD-kit：[https://docs.deepmodeling.com/projects/deepmd/en/r2/getting-started/install.html#install-off-line-packages](https://docs.deepmodeling.com/projects/deepmd/en/r2/getting-started/install.html#install-off-line-packages)

如果用户希望直接使用 DPA2 做基于 ABACUS 软件的分子动力学模拟，需要满足以下条件：

1. 安装 DeePMD-kit v3 版本
2. DeePMD-kit v3 版本应该与采用的 DPA2 训练使用的 DeePMD-kit 版本一致
3. DeePMD-kit v3 支持 PyTorch backend

#### 2.2.3 ABACUS + DeePMD-kit

1\. cmake 安装方式：

在普通 abacus 构建项目命令的基础上，指定 DeePMD-kit 的地址即可编译支持 DP 势场的 ABACUS：

```bash
$ cmake -B build -DDeePMD_DIR=/dir_to_deepmd-kit ...
$ cmake --build build -j4
$ cmake --install build
```

如果采取的不是 offline packages 安装方式，则 TensorFlow 和 PyTorch 的地址可能与 DeePMD-kit 不同，则需要额外指定他们的地址：

```bash
$ cmake -B build -DDeePMD_DIR=/dir_to_deepmd-kit -DTensorFlow_DIR=/dir_to_tensorflow -DTorch_DIR=/dir_to_pytorch ...
$ cmake --build build -j4
$ cmake --install build
```

TensorFlow 和 PyTorch 后端可能只有一个，也可能都有，用户应该根据自己的需求安装支持对应后端的 DeePMD-kit。如果只有 TensorFlow 后端，则只需要提供 TensorFlow_DIR 即可，PyTorch 后端同理

2\. make 安装方式

修改 Makefile.vars 文件，指定 DeePMD_DIR，LIBTORCH_DIR（可选）和 TensorFlow_DIR（可选）：

```bash
DeePMD_DIR      = /dir_to_deepmd-kit
LIBTORCH_DIR    = /dir_to_pytorch
TensorFlow_DIR  = /dir_to_tensorflow
```

或者执行 make 命令时，指定 DeePMD_DIR，LIBTORCH_DIR（可选）和 TensorFlow_DIR（可选）：

```bash
$ make DeePMD_DIR=/dir_to_deepmd-kit  LIBTORCH_DIR=/dir_to_pytorch  TensorFlow_DIR=/dir_to_tensorflow
```

3\. 编译可能出现的问题

- 采用 offilne 方式安装 DeePMD-kit，并使用 intel 编译器编译 ABACUS 时，可能会出现 mkl 库冲突，如

```bash
lib/libmkl_sequential.so.2: 对'mkl_lapack_sgesvda_batch_kernel'未定义的引用
```

为避免影响原有的 DeePMD-kit，可以新建目录/another_dir_to_deepmd，将原地址下的 lib 和 include 文件夹复制至该目录下，然后删除 lib 中所有带 mkl 字符的库文件

```bash
$ cd /another_dir_to_deepmd/lib
$ rm *mkl*
```

# 三、机器学习分子动力学模拟

### 3.1 INPUT 文件设置

```bash
INPUT_PARAMETERS
#Parameters        (General)
suffix              autotest
calculation         md

esolver_type        dp
pot_file            ../../PP_ORB/Al-SCAN.pb

cal_force           1
cal_stress          1

md_nstep            3
md_type             msst
md_dt               1
md_tfirst           200
md_dumpfreq         1
md_restartfreq      1

msst_qmass          200
msst_vel            0.028
msst_vis            0.3

init_vel            1
```

这些参数在 [ABACUS 线上文档](http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#molecular-dynamics)中均有说明，在这里再进行简单概述：

- `calculation`：设置 ABACUS 计算类型，做分子动力学模拟请设置为 md
- `esolver_type`：给定原子位置后的能量求解方式，默认 Kohn-Sham 密度泛函理论（ksdft），还可以设置 LJ 势（lj）或者深度势能（dp），这里设置为 dp
- `md_type`：MD 算法种类，例如选择不同的系综 nve、nvt、npt 等
- `md_nstep`：MD 模拟的总步数
- `md_dt`：MD 计算每一步的时间步长（单位是 fs），与 md_nstep 共同决定 MD 总时长
- `md_tfirst`：MD 系统的初始温度（单位是 K）
- `pot_file`：DP 模型文件路径
- `md_dumpfreq`：MD 输出文件 MD_dump 中原子以及晶胞信息的输出频率
- `md_restartfreq`：结构文件 STRU_MD_$step 的输出频率，MD 续算文件 Restart_md.dat 的更新频率
- `init_vel`：从 STRU 文件中读取原子速度

### 3.2 STRU 文件

```bash
ATOMIC_SPECIES
Al 26.9815

LATTICE_CONSTANT
36.9005650344

LATTICE_VECTORS
1 0 0 #latvec1
0 1 0 #latvec2
0 0 1 #latvec3

ATOMIC_POSITIONS
Cartesian

Al #label
0 #magnetism
864 #number of atoms
0  0  0  m  1  1  1  v  0.000116448153697  -3.54062829069e-05  6.37221822545e-05
0.0833333333321  0.0833333333321  0  m  1  1  1  v  6.31461715716e-05  -7.68881397243e-05  0.000126053061667
0.0833333333321  0  0.0833333333321  m  1  1  1  v  -0.000203773691434  5.08681990052e-05  -5.02990480666e-05
0  0.0833333333321  0.0833333333321  m  1  1  1  v  0.00024862569861  -0.000253289379344  2.04134042994e-05
0  0  0.166666666668  m  1  1  1  v  8.86312919936e-05  0.000160542135344  -0.000121839904824
0.0833333333321  0.0833333333321  0.166666666668  m  1  1  1  v  2.55030351768e-05  -3.68630188311e-05  2.89192521276e-05
0.0833333333321  0  0.25  m  1  1  1  v  -0.000135330676077  -3.26957881398e-05  3.15103467938e-07
0  0.0833333333321  0.25  m  1  1  1  v  0.000131365976691  9.92067819339e-05  -0.00017808361164
...
...
...
```

DPMD 除了不需要提供 KPT，赝势和轨道文件之外，其他设置与正常计算一致。
