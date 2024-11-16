# HContainer 模块介绍

<strong>作者：郑大也</strong>

<strong>单位：北京科学智能研究院</strong>

<strong>最后更新时间：2024/07/14</strong>

## 一、概述

HContainer 是 ABACUS 软件中的一个组件，用于存储和操作描述电子体系的哈密顿量矩阵的数据结构，适用于处理具有稀疏性的哈密顿量。

代码地址：`/source/module_hamilt_lcao/module_hcontainer/`

包含的文件：atom_pair.h, atom_pair.cpp, base_matrix.h, base_matrix.cpp, transfer.h,  transfer.cpp,  hcontainer_funcs.h, func_transfer.cpp, func_folding.cpp, output_hcontainer.h, output_hcontainer.cpp, hcontainer.h, hcontainer.cpp

### 1. 特点

- <strong>模板化</strong>：`HContainer` 目前支持 `double` 和 `std::complex<double>` 两种数据类型，也可以根据需求提供更多的数值类型支持。
- <strong>稀疏性处理</strong>：针对哈密顿量矩阵的稀疏特性，HContainer 提供了专门的存储和访问机制。
- <strong>并行支持</strong>：HContainer 支持 MPI 并行，可以高效地在多处理器上进行数据分配和收集。
- <strong>灵活的内存管理</strong>：HContainer 允许用户自定义内存分配策略，支持内存池的使用，以提高内存使用效率。

### 2. 使用场景

- 需要按原子对存储<strong>实空间</strong>数值原子轨道基组（<strong>LCAO</strong>）<strong>哈密顿量</strong>时。
- 需要按块稀疏矩阵形式存储的对象，比如 LCAO 基组密度矩阵等。

## 二、主要组件

### 1. HContainer 类

HContainer 类是本模块的核心，提供以下关键功能：

- <strong>初始化</strong>：支持通过 `Parallel_Orbitals` 类的实例对象初始化原子对。
- <strong>内存分配</strong>：

  1. <strong>存储结构</strong>：`HContainer` 类内部使用 `std::vector<AtomPair<T>>` 来存储原子对的信息（`AtomPair`），这些原子对按照原子序号的矩阵 `(i, j)` 排序。
  2. <strong>稀疏表</strong>：`HContainer` 包含两个成员变量 `sparse_ap` 和 `sparse_ap_index`，这两个 `std::vector<std::vector<int>>` 用作稀疏表，以快速定位原子对。
  3. <strong>内存池</strong>：提供 `allocate` 方法，允许用户指定内存池或由 HContainer 自行分配内存。
- <strong>数据访问</strong>：通过 `data` 方法获取特定原子对的哈密顿量矩阵数据指针。
- <strong>原子对操作</strong>：提供 `insert_pair`、`find_pair` 和 `get_atom_pair` 等方法，方便用户操作原子对。

  1. <strong>find_pair</strong><strong> 方法</strong>：
     - 根据原子索引 `atom_i` 和 `atom_j`，`find_pair` 方法可以快速定位并返回一个指向 `AtomPair` 的指针。
     - 由于 `atom_pairs` 容器中的原子对是排序的，`find_pair` 可能使用二分查找算法来实现快速搜索。
  2. <strong>get_atom_pair</strong><strong> 方法</strong>：
     - 这个方法返回一个对 `AtomPair` 的引用，基于原子序号 `atom_i` 和 `atom_j`。
     - 与 `find_pair` 类似，这个方法也依赖于原子对的排序来快速定位。
  3. <strong>find_matrix</strong><strong> 方法</strong>：
     - 这个方法可以根据原子索引和 R 指标来查找 `BaseMatrix`。
     - 它首先使用 `find_pair` 找到相应的 `AtomPair`，然后在 `AtomPair` 中搜索具有匹配 R 指标的 `BaseMatrix`。
- <strong>R 指数循环</strong>：通过 `fix_R` 和 `unfix_R` 方法，用户可以固定或解除对特定布拉维格矢 R 的哈密顿量矩阵的操作。
- <strong>Gamma 模式</strong>：`fix_gamma` 方法允许 HContainer 进入 Gamma 模式，该模式下只处理 `R=(0,0,0)` 的哈密顿量矩阵。

## 三、使用示例

### 1. 初始化 HContainer

HContainer 作为一个类，可以用于实例化存储局域原子轨道基组下的哈密顿量矩阵、重叠矩阵等矩阵。

```cpp
<em>// 假设ucell是已经初始化的UnitCell对象</em>
HContainer<double> HR(ucell);
<em>// 或者使用Parallel_Orbitals对象paraV来对HContainer初始化</em>
HContainer<double> HR(paraV);
// 使用确定的<IJR>原子对数组初始化
HContainer<double> HR(paraV, data_pointer, ijr_info)；
```

### 2. 插入原子对

在初始化 HContainer 的对象时有一个重要步骤，即插入原子对信息。当收集完所有原子对信息之后，即可对 HContainer 的对象进行内存分配。

```cpp
// double是数据类型，这里0和1代表原子序号i和j（在所有原子中的序数）
AtomPair<double> atom_ij(0, 1, paraV);
// 在HContainer中插入原子对的信息
HR.insert_pair(atom_ij);
```

### 3. 内存分配

在对 HContainer 分配内存时使用 `allocate()` 函数。此时可以让 HContainer 自身来管理内存空间，也可使用自定义的数组（如这里给出的例子）

```cpp
double* custom_memory = new double[custom_size];
HR.allocate(custom_memory, true); <em>// 使用自定义内存并初始化为零</em>
```

### 4. 数据访问

HContainer 的 `data()` 函数的参数为原子 `i` 和 `j` 的指标，以及布拉维格式 `R`，返回的是一个类型 `T`（doube 或者 complex<double>）的指针

```cpp
double* data_pointer = HR.data(0, 1, {0, 0, 0});
```

通过 <I,J,R> 原子对信息获取目标的小矩阵的接口为 data 函数，其参数为原子 I 和 J 的指标，以及布拉维格子 `R`，返回的是一个类型 `T`（doube 或者 complex<double>）的指针

```cpp
double* data_ijr_pointer = HR.data(i, j, r_index);
```

### 5. R 指数循环

固定布拉维格子 `R`，对原子对进行循环操作。

```cpp
HR.fix_R(0, 0, 0);
for (int i = 0; i < HR.size_atom_pairs(); i++) {
    double* data = HR.data(i);
    <em>// 操作data...</em>
}
HR.unfix_R();
```

### 6. 并行数据传输

#### 6.1 HTransPara 和 HTransSerial 类

这两个类用于处理 HContainer 在并行环境下的数据传输：

- <strong>HTransPara</strong>：负责并行处理器间的数据打包、发送和接收。
- <strong>HTransSerial</strong>：负责串行处理器与并行处理器间的数据传输。
- 在 `func_transfer.cpp` 文件里定义了一系列用于并行数据同步的接口，目前支持 5 种传输功能：

  - <strong>transferSerial2Parallels </strong>单进程上完整 HContainer 对象往多进程上 2D 块并行存储 HContainer 对象数据传输；（典型应用场景：暂无）
  - <strong>transferParallels2Serial </strong>多进程上 2D 块并行存储 HContainer 对象往单进程上完整 HContainer 对象数据传输；（典型应用场景：gatherParallels）
  - <strong>transferSerials2Parallels </strong>多进程上每进程各一个未并行存储的 HContainer 对象往多进程上 2D 块并行存储的 HContainer 对象数据传输并求和（典型应用场景：格点积分 transfer_pvpR）；
  - <strong>transferParallels2Serials </strong>多进程上 2D 块并行存储 HContainer 对象往多进程上传输目标进程需要的稀疏特征的未进行并行存储的 HContainer 对象（典型应用场景：格点积分 transfer_DM2DtoGrid）。
  - <strong>gatherParallels </strong>多进程上 2D 块并行存储 HContainer 对象往单进程上未并行且为空的 HContainer 对象数据传输（典型应用场景：write_dmr）

#### 6.2 并行模式下的注意事项

- <strong>并行程序编写</strong>：HContainer 中内置了<strong>2D 块轨道并行方案</strong>，通过指针 <strong>const Parallel_Orbitals* paraV</strong> 控制具体的并行方案，每个原子对的稠密矩阵在任何核数并行下都依然是稠密矩阵，调用 HContainer 时不需要手动判断轨道的并行方式，可以结合<strong>Parallel_Orbitals</strong>类中提供的获取 local 轨道指标的功能函数辅助完成高效的并行程序编写。
- <strong>数据同步</strong>：由于 HContainer 中采用了 2D 块轨道并行方案，一个矩阵元数据只唯一存储在其中一个进程的 HContainer 对象上，不需要进行手动同步，数据格式转换或并行方案切换时，可以手动调用<strong>hcontainer_funcs.h</strong>中提供的功能函数。

<strong>注 1</strong>：目前已开发的基于 HContainer 的功能函数有限，有更多对 HContainer 的接口需求请提交 Issue。

<strong>注 2</strong>：更多详细 Demo 代码和设计思路详见飞书文档 [HContainer 类设计文档](https://dptechnology.feishu.cn/docx/IiQEdkycoo1j7gxdKJMcQeYxnDg?from=from_copylink)
