# ABACUS 代码存放规范

<strong>作者：路登辉，邮箱：denghuilu@pku.edu.cn；赵天琦，邮箱：zhaotq13@tsinghua.org.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/11/09</strong>

# 一、背景

截止到 `ABACUS 3.4` 版本，ABACUS 的 Github 仓库（[https://github.com/deepmodeling/abacus-develop](https://github.com/deepmodeling/abacus-develop)）代码已超过 `30万` 行，涉及上千个源代码文件，有时一周内在 Github 仓库上就会 Merge 近 20 个 PR，涉及数千乃至上万行代码的修改。随着社区规模不断壮大，为了更好的在各个开发者之间协同合作，在过去已有的一些代码管理的共识的基础上，我们提出这个代码存放规范文档。

# 二、代码目录

进入主仓库之后，ABACUS 的源代码目录位于 `source` 文件夹下：

```bash
$ tree source -d -L 1
source
├── module_base            #基础模块
├── module_basis           #LCAO和PW基组模块
├── module_cell            #晶胞模块
├── module_elecstate       #电子波函数相关性质模块
├── module_esolver         #能量求解器模块
├── module_hamilt_general  #对于PW和LCAO基组共享的哈密顿量模块
├── module_hamilt_lcao     #LCAO基组下哈密顿量的相关模块
├── module_hamilt_pw       #PW基组下哈密顿量求解的相关模块
├── module_hsolver         #对角化求解矩阵特征值/特征向量等哈密顿求解器模块
├── module_io              #输入输出模块
├── module_md              #分子动力学模块
├── module_psi             #波函数模块
├── module_relax           #结构优化模块
├── module_ri              #Resolution of identity相关的Beyond DFT的模块
```

其中，<strong>14 个主模块</strong>的核心功能如上面注释所言，代码存放建议按照模块化管理，相关功能的代码存放到对应的模块当中。如果需要涉及到新建模块以及更新模块位置等需求，应该按照 [ABACUS 的 Github 仓库 Issues 处理流程 · GitBook](https://mcresearch.github.io/abacus-user-guide/develop-issue.html) 中相关规范要求去 Github 仓库提交 ISSUE 并邀请开发者讨论来进行。

## 2.1 模块内部代码存放规范

以 `module_base` 目录为例，该目录下包含了 ABACUS 中内存管理，错误处理，基础通讯以及基础算法等等功能的代码实现，是 ABACUS 中最底层的代码，其他模块大多依赖于 `module_base`。该模块中的代码分布如下，相应文件夹功能如注释所言：

```bash
$ tree source/module_base -d -L 1
source/module_base
CMakeLists.txt
├── abfs-vector3_order.cpp      #基础代码
├── abfs-vector3_order.h        #基础代码
├── ... 
├── CMakeLists.txt              #负责module_base中cmake编译的CMakeLists.txt
├── kernels                     #module_base中的异构计算代码
├── libm                        #libm模块，包含一些优化过后的数学库运算
├── module_container            #ABACUS中底层容器Tensor的实现
├── module_mixing               #charge-mixing实现
├── test                        #module_base中的单元测试
├── test_parallel               #module_base中并行相关的单元测试
├── ...
├── ylm.cpp                     #基础代码
└── ylm.h                       #基础代码
```

<strong>我们提出如下的模块代码存放规范：</strong>

1. <strong>基础代码存放规范：</strong>模块中的基础代码（除去部分特殊代码外的大部分代码）应直接存放到当前模块目录下，头文件以 `.h` 命名；源文件以 `.cpp` 命名；代码规范应该遵循 [ABACUS 开源项目 C++ 代码规范 · GitBook](https://mcresearch.github.io/abacus-user-guide/develop-C++.html) 中的要求。
2. <strong>异构计算代码存放规范：</strong>模块中涉及到<strong>异构计算（CPU 结合GPU计算）部分的代码</strong>应直接存放于当前模块的 `kernels` 目录下；这部分代码的结构将会在稍后详细介绍。
3. <strong>子模块代码存放规范：</strong>

   1. 在主模块下同样可能存在一些子模块，它们通常是具有特定功能的代码的集合：以 `module_base` 举例，`libm`，`module_container` 以及 `module_mixing` 分别表示了 `libm` 模块（后续建议改成 `module_libm` 模块），ABACUS 中底层 Tensor 容器模块（用来方便在不同硬件上存放数据）以及 charge-mixing 相关的功能模块，它们为 `module_base` 模块下的子模块，子模块中同样也可能有类似于主模块的文件代码排布。
   2. 如果要在当前模块中新建或者调整子模块应当去 Github 仓库提交相关的 ISSUE 讨论。
4. <strong>单元测试代码存放规范：</strong>

   1. 模块中代码的单元测试应当存放到当前模块的 `test` 目录下，特殊情况可以存放到以 `test` 开头的目录下面。例如，`test_parallel` 存放了一些并行计算的单元测试，因为 `test` 目录下面的 CMakeList 文件有时候会把 MPI 宏定义去除，再比如 `test_mpi` 里面只测试了 mpi 代码，没有打开 OPENMP。`module_base` 下面还有一个针对数值精度的测试，命名成了 `test_precision`。
   2. 当前模块的子模块的单元测试应当存放到相应子模块的 `test` 目录下；
5. <strong>CMakeLists.txt 存放规范：</strong>各个模块以及子模块通过各自目录中的 `CMakeLists.txt` 管理 CMake 编译结构，添加或修改代码要注意维护 CMake 编译的完备性，此外还应该维护 Makefile 编译的实现，确保代码可以通过 Github 的 CI 测试。

## 2.2 异构计算代码存放规范

当前 ABACUS 中 PW 部分代码已经实现了初步的 GPU 化，`Source` 目录中包含 GPU 的 module 如下，相应文件夹功能如注释所言：

```bash
├── module_base           #基础模块
│   ├── kernels           #module_base模块下的异构计算代码
│   │   ├── cuda          #module_base/kernels中函数的CUDA实现
│   │   ├── rocm          #module_base/kernels中函数的ROCm/DCU实现
│   │   └── test          #module_base/kernels中函数的单元测试
│   ├── libm              #子模块libm
│   │   └── test          #libm的单元测试
│   ├── module_container  #子模块，负责实现ABACUS中的底层Tensor容器
│   │   ├── ATen          #定义了Tensor容器的基本实现
│   │   ├── base          #定义了一些Tensor对象无关的基础函数
│   │   └── test          #module_container的单元测试
│   ├── test              #module_base的单元测试
│   │   └── data          #module_base的但愿测试依赖的数据        
│   └── test_parallel     #module_base的并行测试
├── <strong>...</strong>
├── module_elecstate      #电子波函数相关性质模块
│   ├── kernels           #module_elecstate中相关的异构计算代码
│   │   ├── cuda
│   │   ├── rocm
│   │   └── test
│   ├── module_charge     #charge子模块
│   ├── module_dm         #dm子模块
│   │   └── test          #module_dm的单元测试
│   ├── potentials        #potentials子模块
│   ├── test              #module_elecstate中的单元测试
│   │   └── support       #放置单元测试需要的输入文件
│   └── test_mpi          #只测试mpi并行代码的单元测试
├── <strong>...</strong>
├── module_hamilt_pw      #PW基组下哈密顿量求解的相关模块
│   ├── hamilt_ofdft      #OFDFT子模块
│   ├── hamilt_pwdft      #PWDFT子模块
│   │   ├── kernels
│   │   ├── operator_pw
│   │   └── test
│   └── hamilt_stodft       
├── module_hsolver        #对角化求解矩阵特征值/特征向量的模块
│   ├── genelpa
│   ├── kernels
│   │   ├── cuda
│   │   ├── rocm
│   │   └── test
│   └── test
├── <strong>...</strong>
├── module_psi            #波函数存储模块
│   ├── kernels
│   │   ├── cuda
│   │   ├── rocm
│   │   └── test
│   └── test
│       └── support
└── <strong>...</strong>
```

为了更进一步的规范异构计算代码在 ABACUS 中的维护和管理，以 `module_base/kernels` 举例，针对异构计算代码的位置和目录结构做出如下规范：

```bash
module_base/kernels/
├── cuda                     #存放算子的CUDA实现
│   └── math_op.cu           #算子的CUDA实现存放于cuda目录下
├── math_op.cpp              #算子的CPU实现
├── math_op.h                #算子的声明
├── rocm                     #存放算子的ROCM实现
│   └── math_op.hip.cu       #算子的ROCM实现存放于rocm目录下
└── test                     #提供了算子的单元测试
    ├── CMakeLists.txt       
    └── math_op_test.cpp
```

1. <strong>异构计算代码存放规范：</strong>在每个 module 下，异构计算相关的代码都应该存放在 kernels 目录下。<strong>异构计算</strong>代码都是以算子（OP）的形式存在的，一个算子包含了：CPU，CUDA 以及 ROCM 的实现，使得该算子可以作为统一的计算接口供 ABACUS 调用。
2. <strong>算子的声明和 CPU 实现存放规范：</strong>以 `module_base` 目录举例：`module_base/kernels` 目录应该直接存放当前 module 中涉及到的异构计算算子的声明 `.h` 文件和其 CPU 实现 `.cpp` 文件；
3. <strong>算子的CUDA实现存放规范：</strong>`kernels` 目录下的 `cuda` 子目录中相应的 `.cu` 文件存放算子的 CUDA 实现；
4. <strong>算子的 ROCM 实现存放规范：</strong>`kernels` 目录下的 `rocm` 子目录存放算子的 ROCM 实现；
5. <strong>算子的单元测试存放规范：</strong>`kernels` 子目录下的 test 目录存放当前 `kernels` 中涉及到的全部算子的单元测试。

# 三、总结

我们提倡在 ABACUS 中将各个模块的代码按照上述规范建议进行存放，目录结构可以延续上述风格以便代码识别；涉及到代码目录的问题欢迎到 Github 仓库进行讨论交流。
