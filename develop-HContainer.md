# HContainer 模块介绍

**作者 1：郑大也，单位：北京科学智能研究院**

**作者 2：吴尔杰，单位：北京大学**

**最后更新时间：2025-03-13**

## 概述

HContainer 是 ABACUS 软件中的一个重要组件，用于存储和操作描述电子体系的哈密顿量矩阵的数据结构，适用于处理基于原子轨道基组建立的具有稀疏性的哈密顿量。由于该数据结构的存储逻辑为对所有可能的原子对（原子 i，原子 j 及二者位置对应的布拉维格矢 R）存储相应的矩阵，因此也适用于存储其它需要按原子对索引的矩阵信息。

代码地址：/source/module_hamilt_lcao/module_hcontainer/

包含的文件：atom_pair.h, atom_pair.cpp, base_matrix.h, base_matrix.cpp, transfer.h,  transfer.cpp,  hcontainer_funcs.h, func_transfer.cpp, func_folding.cpp, output_hcontainer.h, output_hcontainer.cpp, hcontainer.h, hcontainer.cpp

### 特点

- **模板化**：`HContainer` 目前支持 `double` 和 `std::complex<double>` 两种数据类型。
- **结构化**：HContainer 采用三层结构实现，最外层为 HContainer 类，中间层为 AtomPair 类，内存为 BaseMatrix 类，数据可通过该三层结构灵活管理
- **稀疏性处理**：针对数值原子轨道基组下哈密顿量矩阵的稀疏特性，HContainer 提供了专门的存储和访问机制。
- **并行支持**：HContainer 支持 MPI 并行，可以高效地在多处理器上进行数据分配和收集。
- **灵活的内存管理**：HContainer 允许用户自定义内存分配策略，支持内存池的使用，以提高内存使用效率。

### 使用场景

- 需要按原子对（AtomPair 数据结构）存储的矩阵信息，例如**实空间**数值原子轨道基组（**LCAO**）**哈密顿量**、**交叠矩阵**等。
- 需要按块稀疏矩阵形式存储的对象，比如 LCAO 基组密度矩阵等。

## 主要组件

### HContainer 类

HContainer 类是本模块的核心，提供以下关键功能：

- **初始化**：支持多种初始化方式，包含

  - 通过 `Parallel_Orbitals` 类的实例对象初始化原子对，适用于轨道并行
  - 从旧的 Hcontainer 对象复制（仅 AtomPair 等结构信息，不包含数据）或移动
  - 利用总原子数创建，不包含任何 AtomPair 信息
  - 从 `unitcell` 创建，包含所有可能的 AtomPair 信息，可包含 `Parallel_Orbitals` 信息
- **内存分配**：

  1. **存储结构**：`HContainer` 类内部使用 `std::vector<AtomPair<T>>` 对象 `atom_pairs` 来存储原子对的信息（`AtomPair`），这些原子对按照原子序号的矩阵 `(i, j)` 排序。
  2. **稀疏表**：`HContainer` 包含两个成员变量 `sparse_ap` 和 `sparse_ap_index`，这两个 `std::vector<std::vector<int>>` 用作稀疏表，以快速定位原子对。
  3. **内存池**：提供 `allocate` 方法，允许用户指定内存池或由 HContainer 自行分配内存，通过 `allocate()` 函数第一个传入参数指定（传入指针指定或传入 nullptr 自动分配），第二个 bool 型参数用于指定是否初始化底层 BaseMatrix 矩阵元为 0。可利用 `get_memory_size` 方法获取总内存占用信息。
- **数据访问和操作**：支持多种数据访问和操作方式，其中加粗字体为主要使用方式。

  - 数据访问：
    - **通过data方法获取特定原子对（i,j,R）的哈密顿量矩阵数据指针**
    - 通过 `find_matrix` 方法获取特定原子对（i,j,R）的哈密顿量矩阵（BaseMatrix）指针
    - 通过 `find_matrix_offset` 方法获取特定原子对（i,j,R）的数据在内存池中的相对位置
    - 通过 `find_pair` 方法获取特定原子对（i,j）的 AtomPair 类型指针
    - 通过 `get_ijr_info` 方法将 HContainer 内所有 AtomPair 的 ijr 信息输出到 `std::vector<int>` 对象
  - 数据操作：
    - **通过insert_pair方法将特定 AtomPair 加入 HContainer 中**
    - 通过 `insert_ijrs` 方法利用 `ijr_info` 信息将一系列 AtomPair 批量加入 HContainer 中
    - 通过 `add` 方法将另外的 HContainer 数据加到当前 HContainer
    - 通过 `set_zero` 方法将所有矩阵元设置为 0
- **原子对操作**：提供 `insert_pair`、`find_pair`、`get_atom_pair`、`find_matrix` 和 `size_atom_pairs` 等方法，方便用户操作原子对。

  1. **insert_pair方法**：
     - 将 AtomPair 对象添加到 HContainer 中，存储于 `atom_pairs` 成员变量
     - 能够根据原子对是否已经存在自动处理，保证 `atom_pairs` 中信息严格有序
     - 能够对 `fix_gamma` 模式自动执行 merge 操作
  2. **find_pair 方法**：
     - 根据原子索引 `atom_i` 和 `atom_j`，`find_pair` 方法可以快速定位并返回一个指向 `AtomPair` 的指针。
     - 由于 `atom_pairs` 容器中的原子对是排序的，`find_pair` 可能使用二分查找算法来实现快速搜索。
  3. **get_atom_pair 方法**：
     - 这个方法返回一个对 `AtomPair` 的引用，基于原子序号 `atom_i` 和 `atom_j`。
     - 与 `find_pair` 类似，这个方法也依赖于原子对的排序来快速定位。
  4. **find_matrix 方法**：
     - 这个方法可以根据原子索引和 R 指标来查找 `BaseMatrix`。
     - 它首先使用 `find_pair` 找到相应的 `AtomPair`，然后在 `AtomPair` 中搜索具有匹配 R 指标的 `BaseMatrix`。
  5. **size_atom_pairs方法**：
     - 这个方法用于确定当前 HContainer 对象内包含的 `AtomPair` 总数，在 `fix_R` 模式下为当前布拉维格矢对应的 `AtomPair` 总数。
- **针对布拉维格矢R 指数的操作**：

  1. **固定布拉维格矢**：通过 `fix_R` 和 `unfix_R` 方法，用户可以固定或解除对特定布拉维格矢 R 的哈密顿量矩阵的操作。在 HContainer 内部，`fix_R` 方法通过将特定布拉维格矢 R（存储于 current_R，可利用 `get_current_R` 获取）下的原子对信息暂存于 `std::vector<const AtomPair<T>*>` 对象 `tmp_atom_pairs`，此时可通过 `get_atom_pair` 方法针对该临时变量进行操作。
  2. **布拉维格矢索引循环**：在某些情况下，用户可能会需要针对布拉维格矢进行循环操作（例如稀疏矩阵输出）。用户可通过调用 `size_R_loop` 方法初始化 `tmp_R_index` 对象并存储 HContainer 内所有 AtomPair 可能的取值，通过返回值获得其大小（注意存储顺序并未按照 R 的取值排序）。用户可通过 `find_R` 方法获得指定布拉维格矢在 `tmp_R_index` 对象中的 index，或通过 `loop_R` 方法从 index 获取特定的布拉维格矢信息。
- **Gamma 模式**：`fix_gamma` 方法允许 HContainer 进入 Gamma 模式，该模式下只处理 `R=(0,0,0)` 的哈密顿量矩阵。外部可通过 `is_gamma_only` 方法获取当前 HContainer 对象是否启用了该模式。

### AtomPair 类

AtomPair 类是 HContainer 内主要存储的对象，用于按原子对整理矩阵信息，提供以下功能：

- **初始化**：支持多种初始化方式，包含

  - 通过 `Parallel_Orbitals` 类的实例对象初始化原子对（i,j，可选择包含 R），适用于轨道并行
  - 利用原子对的轨道矩阵序数初始化原子对（i,j，可选择包含 R）
  - 仅使用原子对序（i,j）初始化
  - 从旧的 AtomPair 对象复制或移动
- **内存分配**：

  1. **存储结构**：`AtomPair` 类内部使用 `std::vector<BaseMatrix<T>>` 对象 `values` 来存储矩阵信息，这些矩阵没有严格排序，vector 中每一个值对应某个布拉维格矢 R 下的 BaseMatrix，布拉维格矢 R 信息则对应存储于 `std::vector<ModuleBase::Vector3<int>>` 对象 R_index。
  2. **内存池**：提供 `allocate` 方法，允许用户指定内存池或由 AtomPair 自行分配内存，通过 `allocate()` 函数第一个传入参数指定（传入指针指定或传入 nullptr 自动分配），第二个 bool 型参数用于指定是否初始化底层 BaseMatrix 矩阵元为 0。可利用 `get_memory_size` 方法获取该 AtomPair 内存占用信息。
- **数据访问和操作**：支持多种数据访问和操作方式。

  - 数据访问：
    - 通过 `get_row_size`、`get_col_size` 或 `get_size` 获取底层矩阵的维度信息
    - 通过 `get_atom_i` 和 `get_atom_j` 获取当前原子对序数信息
    - 通过 `identify` 方法判断其它原子对或 AtomPair 对象与当前对象是否属于相同原子对
    - 通过 `get_HR_values` 获取给定布拉维格矢 R 的底层矩阵 BaseMatrix
    - 通过 `find_matrix` 获取给定布拉维格矢 R 的底层矩阵 BaseMatrix 对象指针
    - 通过 `get_matrix_values` 获取布拉维格矢序和底层矩阵数据指针的元组
    - 通过 `get_value` 获取当前固定布拉维格矢 R 模式下特定矩阵元的数据
    - 通过 `get_pointer` 获取指定卜拉维格式下底层矩阵的数据指针
  - 数据操作：
    - 通过 `set_zero` 方法将所有矩阵元设置为 0
    - 通过 `set_size` 方法设置底层矩阵的维度（默认情况下为两个原子的基组长度），需要在 `allocate` 方法调用前执行以保证内存正确分配
    - 通过 `convert_add` 将其它 BaseMatrix 值加入指定布拉维格矢 R 对应的底层 BaseMatrix 中
    - 通过 `merge` 方法将其它 AtomPair 信息加入到当前 AtomPair 中
    - 通过 `metge_to_gamma` 将所有信息添加到 R=(0,0,0)的 BaseMatrix 中，对应于 HContainer 的 Gamma 模式
    - 通过 `add_to_matrix`、`add_from_matrix` 和 `add_to_array` 将带特定相位的信息存入或读出
- **针对布拉维格矢 R 指数的操作**：

  1. **固定布拉维格矢**：通过 `find_R` 方法寻找并指定特定布拉维格矢 R 并存储于 current_R，之后针对特定矩阵的操作将针对在该布拉维格矢下的原子对矩阵进行操作。用户可通过 `get_R_size` 获取所有可能的 R 取值的大小。

### BaseMatrix 类

BaseMatrix 是底层的矩阵类，操作简单，包含：

- **初始化**：指定矩阵行列大小和数据指针（可选）创建，支持使用其它 BaseMatrix 复制或移动创建
- **内存分配**：提供 `allocate` 方法，允许用户指定内存池或由 AtomPair 自行分配内存，通过 `allocate()` 函数第一个传入参数指定（传入指针指定或传入 nullptr 自动分配），第二个 bool 型参数用于指定是否初始化矩阵元为 0。可通过 `get_memory_size` 方法获取当前 BaseMatrix 的内存占用。
- **数据访问和操作**：支持多种数据访问和操作方式。

  - 数据访问：
    - 通过 `get_value` 方法获取矩阵特定位置的值
    - 通过 `get_col_size` 和 `get_row_size` 获取矩阵维度
  - 数据操作：
    - 通过 `set_size` 方法设置矩阵的列和行（注意顺序）大小，需要在分配内存前指定（在 HContainer 类内矩阵的大小会 AtomPair 自动设置成原子轨道数的大小，但用户可以通过该方法重新设置）
    - 通过 `set_zero` 方法将所有矩阵元设置为 0
    - 通过 `add_array` 方法将一个 array 对应的数据按序加到矩阵对应位置
    - 通过 `add_element` 方法为矩阵特定位置的元素加上某个值
    - 通过 `get_pointer` 方法获取整个 BaseMatrix 的数据指针头

### Output_HContainer 类

Output_HContainer 类独立于 HContainer 类存在，主要用于将信息以稀疏矩阵以 csr 格式输出。

- **初始化**：要求传入 HContainer 对象和输出流（std::ostream）对象，并设定稀疏阈值和输出精度
- **使用方式**：通过直接调用 `write` 方法按布拉维格矢 R 序（Rx，Ry，Rz 依次从小到大）输出，或使用 `write` 方法传入特定（Rx，Ry，Rz）输出指定布拉维格矢 R 下的稀疏矩阵信息。输出将直接利用传入的 std::ostream 对象实现

## 使用示例

Hcontainer 类的使用一般依次包含以下基本操作：

- 初始化 HContainer 对象（创建对象）
- 向 HContainer 内加入所有原子对信息（创建 AtomPair 对象并添加）并指定底层矩阵的维度大小（可选）
- 为 HContainer 分配内存空间并初始化数据
- 向 HContainer 内添加数据或其他操作

（如果使用了复制创建的方式，则相当于直接执行了前三步，可以直接进行数据操作）

### 初始化 HContainer

HContainer 作为一个类，可以用于实例化存储局域原子轨道基组下的哈密顿量矩阵、重叠矩阵等矩阵。

```cpp
_// 假设ucell是已经初始化的UnitCell对象，此时HContainer中将包含所有原子对，仅用于构建单元测试_
HContainer<double> HR(ucell);
_// 或者使用Parallel_Orbitals对象__paraV来对HContainer初始化__，此时HContianer中不包含任何原子对_
HContainer<double> HR(paraV);
// 使用确定的<IJR>原子对数组初始化
HContainer<double> HR(paraV, data_pointer, ijr_info)；
```

### 插入原子对

在初始化 HContainer 的对象时有一个重要步骤，即插入原子对信息。当收集完所有原子对信息之后，即可对 HContainer 的对象进行内存分配。

```cpp
// double是数据类型，这里0和1代表原子序号i和j（在所有原子中的序数）
AtomPair<double> atom_ij(0, 1, paraV); // 不包含R，用于Gamma-only
AtomPair<double> atom_ij(0, 1, dRx, dRy, dRz, paraV) // 包含R的信息，也可以用ModuleBase::Vector3<int>对象
// 设定底层矩阵的维度大小（可选，在不执行时默认创建大小为两原子在当前进程的轨道基数）
atom_ij.set_size(ncol, nrow);
// 在HContainer中插入原子对的信息
HR.insert_pair(atom_ij);
```

### 内存分配

在对 HContainer 分配内存时使用 `allocate()` 函数。此时可以让 HContainer 自身来管理内存空间，也可使用自定义的数组（如这里给出的例子）

```cpp
// 方法一：使用自定义内存空间并初始化为零
double* custom_memory = new double[custom_size];
HR.allocate(custom_memory, true);

// 方法二：自动分配内存并初始化为零
HR.allocate(nullptr, true);
```

### 数据访问

由于 HContainer 按照块稀疏矩阵格式存储数据，其中的所有数据连续存储在一个一维数组中，直接获取该完整数组的接口为 get_wrapper 函数：

```cpp
double* data_pointer = HR.get_wrapper();
```

通过 <I,J,R> 原子对信息获取目标的小矩阵的接口为 data 函数，其参数为原子 I 和 J 的指标，以及布拉维格子 `R`，返回的是一个类型 `T`（doube 或者 complex<double>）的指针

```cpp
double* data_ijr_pointer = HR.data(i, j, r_index);
```

其它方法可参考第二章相关部分对照代码使用。

### R 指数循环

固定布拉维格子 `R`，对原子对进行循环操作。

此时 HContainer 中会生成临时 AtomPair 指针数组，用于按顺序遍历包含该布拉维格子 R 的原子对，需要注意的是完成计算后需要手动调用 unfix_R 函数删除该临时指针数组。

```cpp
HR.fix_R(0, 0, 0);
for (int i = 0; i < HR.size_atom_pairs(); i++) {
    double* data = HR.data(i);
    _// 操作data..._
}
HR.unfix_R();
```

### 并行数据传输

#### HTransPara 和 HTransSerial 类

这两个类用于处理 HContainer 在并行环境下的数据传输：

- **HTransPara**：负责并行处理器间的数据打包、发送和接收。
- **HTransSerial**：负责串行处理器与并行处理器间的数据传输。
- 在 `func_transfer.cpp` 文件里定义了一系列用于并行数据同步的接口，目前支持 5 种传输功能：

  - **transferSerial2Parallels** 单进程上完整 HContainer 对象往多进程上 2D 块并行存储 HContainer 对象数据传输；（典型应用场景：暂无）
  - **transferParallels2Serial** 多进程上 2D 块并行存储 HContainer 对象往单进程上完整 HContainer 对象数据传输；（典型应用场景：gatherParallels）
  - **transferSerials2Parallels** 多进程上每进程各一个未并行存储的 HContainer 对象往多进程上 2D 块并行存储的 HContainer 对象数据传输并求和（典型应用场景：格点积分 transfer_pvpR）；
  - **transferParallels2Serials** 多进程上 2D 块并行存储 HContainer 对象往多进程上传输目标进程需要的稀疏特征的未进行并行存储的 HContainer 对象（典型应用场景：格点积分 transfer_DM2DtoGrid）。
  - **gatherParallels** 多进程上 2D 块并行存储 HContainer 对象往单进程上未并行且为空的 HContainer 对象数据传输（典型应用场景：write_dmr）

#### 并行模式下的注意事项

- **并行程序编写**：HContainer 中内置了 **2D 块轨道并行方案**，通过指针 **const Parallel_Orbitals\* paraV** 控制具体的并行方案，每个原子对的稠密矩阵在任何核数并行下都依然是稠密矩阵，调用 HContainer 时不需要手动判断轨道的并行方式，可以结合 **Parallel_Orbitals** 类中提供的获取 local 轨道指标的功能函数辅助完成高效的并行程序编写。
- **数据同步**：由于 HContainer 中采用了 2D 块轨道并行方案，一个矩阵元数据只唯一存储在其中一个进程的 HContainer 对象上，不需要进行手动同步，数据格式转换或并行方案切换时，可以手动调用 **hcontainer_funcs.h** 中提供的功能函数。

**注 1**：目前已开发的基于 HContainer 的功能函数有限，有更多对 HContainer 的接口需求请提交 Issue。

**注 2**：更多详细 Demo 代码和设计思路详见飞书文档 [HContainer 类设计文档](https://dptechnology.feishu.cn/docx/IiQEdkycoo1j7gxdKJMcQeYxnDg?from=from_copylink)
