# Psi 模块介绍

**作者：韩昊知，单位：北京大学**

**最后更新时间：2025-03-13**

# 一、基本简介

`Psi` 类是 ABACUS 软件里存储电子波函数的模块，实际上存储的是电子波函数在某个特定基组下的系数，是电子结构软件中最基本、最常用、但也耗内存最大的一种数据结构。

另外，`Psi` 类是一个模板类，用于支持不同设备、不同精度的 `Psi` 类的构造。

代码地址：`/source/module_psi/`

# 二、Psi Class 支持的基本功能与特点

1. 支持异构存储 Psi 的三维数据：

   1. 多设备支持：`Psi` 类通过模板参数 `typename Device` 控制 `Psi` 类在不同底层计算设备上的对象管理和操作。当前支持的异构设备分别是：`base_device::DEVICE_CPU`、`base_device::DEVICE_GPU`。
   2. 多精度支持：`Psi` 类通过模板参数 `typename T` 控制 `Psi` 类中核心数据的数据类型。当前支持的数据类型包括：`double`、`float`、`complex<double>`、`complex<float>`。
2. 快速、方便的定位到 Psi 内部的数据：

   1. 通过 `fix_k` 函数固定 `k` 维度，使后续访问波函数数据更加便捷和高效。
   2. 使用运算符函数 `(ikb1, ikb2, ibasis)` 直接访问目标元素。

# 三、成员变量

**全局信息:**

1. `T* psi = nullptr`: psi 数据的初始位置的指针
2. `Device* ctx = {}`: 用于获取设备变量的上下文标识符
3. `bool k_first = true`: 表示当前 psi 的存储方式是否是 k 点优先
4. `bool allocate_inside = true`: 表示当前 psi 的内存空间是否在当前 psi 对象内部被分配
5. `int npol = 1`: 表示当前 nspin 是否等于 4

   1. 如果 npol 为 1, nspin 不等于 4
   2. 如果 npol 为 2, nspin 等于 4

**维度信息:**

1. `const int* ngk = nullptr`: 使用数组表示不同 k 点的对应的 basis 的数量。
2. `nk`：psi 第一个维度的长度
3. `nbands`：psi 第二个维度的长度
4. `nbasis`：psi 第三个维度的长度

**可变信息:**

1. `mutable int current_k = 0`: 表示当前 k 点维度索引
2. `mutable int current_b = 0`: 表示当前 band 维度的索引
3. `mutable int current_nbasis = 1`: 表示当前 basis 维度的索引
4. `mutable T* psi_current = nullptr`: 表示 当前 psi 数据的指针
5. `mutable int psi_bias = 0`: 表示 当前 psi 数据 与 psi 初始位置 的偏移量

> `mutable` 相关变量的数值会根据 fix 相关函数而改变

# 四、成员函数

## 4.1 构造函数

### 第一类构造函数 (最常用的构造函数)

```cpp
// Constructor 1-1:
Psi(const int nk_in, 
    const int nbd_in, 
    const int nbs_in, 
    const int* ngk_in, 
    const bool k_first_in);
    
// Constructor 1-2:
Psi(const int nk_in, 
    const int nbd_in, 
    const int nbs_in, 
    const std::vector<int>& ngk_in, 
    const bool k_first_in);
```

- 最常用的构造方式
- 通过 nk_in，nbd_in，nbs_in，ngk_in 构造 psi

  - ngk_in 对应的数组大小应该与 nk_in 相同
- 分配内存空间
- 设置 psi 的初始值都为 0

> _NOTE: Constructor 1-1 在后续的重构中都会被替换为 Constructor 1-2._
> _请开发者都使用 Constructor 1-2_
> _NOTE: 非必要不构造 k_first_in==false 的 Psi 对象_

### 第二类构造函数 (构造 nk==1 的 Psi 类)

```cpp
// Constructor 2-1:
Psi(const int nk_in, // nk-in == 1
    const int nbd_in, 
    const int nbs_in, 
    const int current_nbasis_in, 
    const bool k_first_in);
```

- 对于这个构造函数 nk-in 永远等于  1
- 分配内存空间
- 初始化 psi 的数据为 0

```cpp
// Constructor 2-2:
Psi(T* psi_pointer,
    const int nk_in,
    const int nbd_in,
    const int nbs_in,
    const int current_nbasis_in,
    const bool k_first_in);
```

- 对于这个构造函数 nk-in 永远等于  1
- 不需要分配空间
- 不需要初始化 psi

**多用于以零成本的方式将 Tensor / 裸指针 的数据转化为 Psi 类。**

### 第三类构造函数 (拷贝构造函数)

```cpp
// Constructor 3-1:
Psi(const Psi& psi_in);

// Constructor 3-2:
template <typename T_in, typename Device_in = Device>
Psi(const Psi<T_in, Device_in>& psi_in);
```

> _NOTE: Constructor 3-1 在后续的重构中都会被替换为 Constructor 3-2._

## 4.2 赋值函数

```cpp
void set_all_psi(const T* another_pointer, const std::size_t size_in);
```

- 根据输入指针的数据, 初始化当前 psi 的数据.

```cpp
void zero_out();
```

- 将当前 psi 对象的数据都赋值为 0

## 4.3 Fix 函数

```cpp
void fix_k(const int ik) const;
```

- 根据 ik 修改 Psi 对象中 5 个 `mutable`(可变变量)的值

## 4.4 运算符函数 `(ikb1, ikb2, ibasis)`

```cpp
T& operator()(const int ikb1, const int ikb2, const int ibasis) const;
```

该运算符 `operator()(ikb1, ikb2, ibasis)` 用于访问 Psi 波函数的特定元素，索引方式取决于 `k_first` 标志的设定：

若 `k_first = true`，数据按照 k 维度优先存储，`ikb1` 表示 k 点索引，`ikb2` 表示能带索引。

若 `k_first = false`，数据按照能带维度优先存储，`ikb1` 表示能带索引，`ikb2` 表示 k 点索引。 该运算符提供了一种灵活的方式，以适应不同存储布局下的高效数据访问。

## 4.5 其他成员函数

1. 获取指针变量 psi_current：

```cpp
T* get_pointer() const;
```

1. 获取维度信息 nk

```cpp
const int& get_nk() const;
```

1. 获取维度信息 nbands

```cpp
const int& get_nbands() const;
```

1. 获取维度信息 nbasis

```cpp
const int& get_nbasis() const;
```

1. 获取当前 k 索引 current_k

```cpp
int get_current_k() const;
```

1. 获取当前 band 索引 current_b

```cpp
int get_current_b() const;
```

1. 获取当前 k 点的 basis 维度 current_nbasis

```cpp
int get_current_nbas() const;
```

1. 获取当前是否是 k 维度优先

```cpp
const bool& get_k_first() const;
```

# 五、易混淆概念辨析

## 5.1 nbasis vs current_nbasis vs ngk

- Nbasis 表示 Psi 对象 实际内存空间中第三个维度的大小.

  - 当 nspin != 4 的时候, nbasis = ngk 数组中的最大值
  - 当 nspin == 4 的时候, nbasis = (ngk 数组中的最大值 的 2 倍)
- current_nbasis 表示 当前 k 点的 ngk 变量

  - 无论 nspin 为多少,  current_nbasis 总 = ngk[current_k]
- Ngk 表示 存储 不同 k 点的 basis 变量 的数组指针

## 5.2 k_first 概念解释

强烈建议开发者在非必要的时候不要使用 `k_first = false` 的 `Psi` 设置。目前在 ABACUS 相关代码中，仅在 `module_lr` 内存在 `k_first = false` 的 `Psi` 用法。因此，对于绝大多数的 `Psi` 使用场景，默认的 `k_first = true` 即可应对。

在 `Psi` 类中，`k_first` 变量决定了数据的存储顺序，影响索引计算和访问方式。当 `k_first = true` 时，波函数数据按照 **k 维度优先** 进行存储。在这种情况下，相同 `k` 点的数据是连续存储的，适用于基于 k 点的计算。

相反，当 `k_first = false` 时，数据按照 **band 维度优先** 进行存储，即先存储所有 `band` 的数据，再存储不同的 `k` 点，最后是 `basis`。在这种情况下，相同 `band` 之间的数据是连续存储的，适用于逐个能带的计算。

# 六、使用场景

## 6.1 在指定硬件设备上构造特定精度的 Psi 的对象

在 GPU 上构造数据类型为 `std::complex<double>` 的 `Psi` 对象，其中 Psi 三个维度的值分别为 `nk = 16`, `nbands = 24`，`nbasis = 1024`。`ngk` 表示 16 个 k 点分别对应的有效 basis 的值。

```cpp
psi::Psi<std::complex<double>, base_device::DEVICE_GPU> psi = new psi::Psi<std::complex<double>, base_device::DEVICE_GPU>(16, 24, 1024, ngk, true);
```

## 6.2 输出 Psi 的所有值

```cpp
// 打印所有值
void print_all_values(const psi::Psi<double>& psi) const 
{   
    for (int ik = 0; ik < nk; ++ik) 
    {
        for (int iband = 0; iband < nbands; ++iband) 
        {
            for (int ibasis = 0; ibasis < nbasis; ++ibasis) 
            {
                if (psi.get_k_first()) 
                {
                    std::cout << "Psi(" << ik << ", " << iband << ", " << ibasis << ") = "
                              << psi(ik, iband, ibasis) << std::endl;
                } else 
                {
                    std::cout << "Psi(" << iband << ", " << ik << ", " << ibasis << ") = "
                              << psi(iband, ik, ibasis) << std::endl;
                }
            }
        }
    }
    
}
```

## 6.3 构造 nk==1 的 Psi 类

该需求经常用于构造一个临时的 Psi 对象，用于存储单个 k 点的 psi 数据，常用于 module_hsolver 内部。对于这种需求，我们推荐使用第二类构造函数。

```cpp
psi::Psi<std::complex<double>, base_device::DEVICE_GPU> psi = new psi::Psi<std::complex<double>, base_device::DEVICE_GPU>(1, 24, 1024, 1024, true);
```

第二类构造函数与第一类构造函数的主要区别在于原本传 ngk 的地方只需要传 `const int current_nbasis_in`。
