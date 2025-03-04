# 如何在 ABACUS 中进行异构计算

<strong>作者：张笑扬，邮箱：2100011024@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2025/03/02</strong>

## 一、前言

异构编程（Heterogeneous Programming）是一种利用不同类型计算单元协同工作来完成计算任务的编程模式。传统的同构系统中，所有计算任务都由单一类型的处理器（如 CPU）完成。但随着计算需求的不断增长，单一类型处理器在处理某些特定任务时效率有限。例如，CPU 虽然具有强大的通用性和控制能力，但在处理大规模并行计算任务时，性能表现不如专门的计算单元。因此，异构系统应运而生，它结合了不同类型的计算单元，如 CPU、GPU（图形处理器）、FPGA（现场可编程门阵列）、ASIC（专用集成电路）等，以充分发挥各计算单元的优势，提高计算效率，这里我们主要讨论 CPU 结合 GPU（或者类似 GPU）的异构编程。

在国产密度泛函理论软件 ABACUS（原子算筹）里，异构的主要对象之一是数学库。近期我们对数学库 blas 的调用进行了封装，相关文件我们称为 blas_connector。blas_connector 得到重构之后（在这个 PR 得到接收之后 [https://github.com/deepmodeling/abacus-develop/pull/5799](https://github.com/deepmodeling/abacus-develop/pull/5799)），可以通过直接调用 blas_connector.h 里面提供的算子，配合 device 和 memory 等基础模块即可直接编写异构代码。这套方案比起现在使用的方案来说，希望解决不同模块各自封装的问题，且对于新开发者来说可以避免使用模板和各自封装导致的理解困难。之后会逐渐使用这套方案替换原有的实现，从而实现整体异构方案的统一化与重构。用这种方法去除模板之后，能实现更灵活的计算，后续会用这个方式完成混合精度计算功能的实现。

下文将会介绍如何使用 ABACUS 现有的工具简单的进行异构计算的实现。

## 二、管理设备类型

ABACUS 目前使用这几种方式进行计算设备的标识。主要记录在 `source/module_base/module_device/types.h` 文件中。包括 `struct` 和 `enum` 两种方式

```cpp
// !source/module_base/module_device/types.h
#ifndef MODULE_TYPES_H_
#define MODULE_TYPES_H_

namespace base_device
{

struct DEVICE_CPU;
struct DEVICE_GPU;
struct DEVICE_DSP;

enum AbacusDevice_t
{
    UnKnown,
    CpuDevice,
    GpuDevice,
    DspDevice
};

} // namespace base_device

#endif // MODULE_TYPES_H_
```

其中，`DEVICE_XXX` 是定义为结构体的标识符。这些结构体被作为模板参数使用，在之前是作为 ctx 这种标识符使用，使用方式有些反直觉。

另一个 `AbacusDevice_t` 就是一个枚举类型变量。是一个很早就出现在 ABACUS 的代码中但是几乎一直没有被使用的数据结构。在重构 blas_connector 之后会逐渐启用，用于提供一个更加简单清晰的设备标识。

除此之外，在 ABACUS 里的有些其他模块会存在自己的设计。如 `source/module_basis/module_pw/module_fft/fft_base.h` 的 fft 模块中，使用一个字符串来标记设备类型

```cpp
std::string device = "cpu"; //或者是gpu
```

这个类简单的使用一个字符串来标记 device 类型。本质上和使用 `AbacusDevice_t` 没有区别。这里建议新开发者如果希望加入新的异构功能，尽量都是用 `AbacusDevice_t` 来标记。

## 三、数据内存管理（旧）

由于这些 Operator 的实现存在一些冗余的参数，因此会在近期的 Pull Request 中迎来对应的重构工作。因此暂时不建议使用这里的 Operator 进行内存管理，但是其仍然具有一定参考价值。

### 3.1 给指针分配内存

注：如果你需要进行大量数据的计算和转移（如需要储存一个矩阵），这里建议使用 ABACUS 提供的 `Tensor` 数据结构进行计算，见 Tensor 文档。你也可以用这种方式进行异构计算，它会更加灵活，但是你需要自己进行内存管理，防止内存溢出等问题。

现在可用的异构内存工具位于 `source/module_base/module_device/memory_op.h` 文件中。只需要包含这个头文件即可使用。目前这些算子的使用方式还是以模板为主。我们主要会使用以下 Operator。

```cpp
template <typename FPTYPE, typename Device>
struct resize_memory_op
{
    /// @brief Allocate memory for a given pointer. Note this op will free the pointer first.
    ///
    /// Input Parameters
    /// \param size : array size
    /// \param record_string : label for memory record
    ///
    /// Output Parameters
    /// \param arr : allocated array
    void operator()(const Device* dev, FPTYPE*& arr, const size_t size, const char* record_in = nullptr);
};
```

这个算子的主要作用是给一个指定指针分配内存。你也可以使用这个算子给以及包含了一段数据的指针分配内存，这样的话原来的内存区域会被释放，然后重新分配一段内存。你可以这样使用这个算子

```cpp
double* ptr = nullptr;
base_device::memory::resize_memory_op<double, base_device::DEVICE_CPU>()(ptr, sizeof(double));
```

可以注意到，首先我们有两个模板参数叫 base_device::DEVICE_GPU 和 base_device::DEVICE_CPU，用于决定这个 Operator 会执行在哪个设备上。。

之后我们只要调用这个 Operator 来实现在不同设备分配内存。上文展示了在 CPU 的一个 double 指针上分配一定内存的方法。这个 Operator 的用法是这样的

```cpp
base_device::memory::resize_memory_op<TYPE, DEVICE>()(pointer, size);
```

在尖括号模板参数中，TYPE 是需要分配的数据类型，如 `float`，`double`，`std::complex<double>` 等。DEVICE 决定空间会被分配到哪个计算设备上，可以选填 `base_device::DEVICE_CPU` 或 `base_device::DEVICE_GPU`。在后面的参数中，pointer 是需要被分配内存的指针，size 是希望分配的空间大小，一般可以用 `sizeof(TYPE) * count` 的方式指定分配多少个数据。

### 3.2 初始化一片内存的值

`memory_op.h` 提供了以下算子来初始化一片内存区域的值

```cpp
template <typename FPTYPE, typename Device>
struct set_memory_op
{
    /// @brief memset for multi-device
    ///
    /// Input Parameters
    /// \param var : the specified constant value
    /// \param size : array size
    ///
    /// Output Parameters
    /// \param arr : output array initialized by the input value
    void operator()(FPTYPE* arr, const int var, const size_t size);
};
```

同样的，可以这样使用这个 Operator

```cpp
base_device::memory::set_memory_op<TYPE, DEVICE>()(pointer, var, size)
```

`TYPE`：被操作指针的数据类型

`DEVICE`：计算设备类型，可选 `base_device::DEVICE_CPU` 或 `base_device::DEVICE_GPU`

`pointer`：被操作的指针

`var`：设置内存区域的值，<strong>只能为 0 或者-1</strong>

`size`：设置内存区域的大小

注意！由于底层实现的原因，这个算子只能用来将一片内存区域<strong>全部设置为 0 或者全部设置为-1</strong>，不能用于给这篇内存填充别的特定数值。一般情况下我们也不会需要使用这个来填充别的数值的使用场景。

### 3.3 在不同设备间转移数据

`memory_op.h` 提供了以下算子来在不同设备间转移数据

```cpp
template <typename FPTYPE, typename Device_out, typename Device_in>
struct synchronize_memory_op
{
    /// @brief memcpy for multi-device
    ///
    /// Input Parameters
    /// \param arr_in : input array
    /// \param size : array size
    ///
    /// Output Parameters
    /// \param arr_out : output array initialized by the input array
    void operator()(FPTYPE* arr_out,
                    const FPTYPE* arr_in,
                    const size_t size);
};

template <typename FPTYPE_out, typename FPTYPE_in, typename Device_out, typename Device_in>
struct cast_memory_op
{
    /// @brief memcpy for multi-device
    ///
    /// Input Parameters
    /// \param arr_in : input array
    /// \param size : array size
    ///
    /// Output Parameters
    /// \param arr_out : output array initialized by the input array
    void operator()(FPTYPE_out* arr_out,
                    const FPTYPE_in* arr_in,
                    const size_t size);
};
```

这个算子的作用是在不同计算设备间转移数据。其中 `synchronize_memory_op` 会转移同种数据类型的数据，`cast_memory_op` 可以在设备间转移不同类型的数据，但是效率可能稍低。这个算子可以这么使用

```cpp
base_device::memory::synchronize_memory_op<TYPE, DEVICE_OUT, DEVICE_IN>(pointer_out, pointer_in, size);
```

这个函数会将 `pointer_in` 长度为 `size` 的内容拷贝到 `pointer_out`。要求这两个指针的数据类型 `TYPE` 要相同。如果选在相同的 `DEVICE_OUT` 和 `DEVICE_IN`，会在同一个计算设备上的两个指针之间移动数据，也就是起到一个拷贝的作用。

`TYPE`：被操作指针的数据类型

`DEVICE_OUT`：拷贝的目标计算设备类型，可选 `base_device::DEVICE_CPU` 或 `base_device::DEVICE_GPU`

`DEVICE_IN`：被拷贝的计算设备类型，可选 `base_device::DEVICE_CPU` 或 `base_device::DEVICE_GPU`

`pointer_in`：被拷贝的指针

`pointer_out`：拷贝的目标指针

`size`：拷贝内存区域的大小

另一个算子使用方法类似，但是会提供一个类型转换

```cpp
base_device::memory::cast_memory_op<TYPE_OUT, TYPE_IN, DEVICE_OUT, DEVICE_IN>(pointer_out, pointer_in, size);
```

`TYPE`：被操作指针的数据类型

`DEVICE_OUT`：拷贝的目标计算设备类型，可选 `base_device::DEVICE_CPU` 或 `base_device::DEVICE_GPU`

`DEVICE_IN`：被拷贝的计算设备类型，可选 `base_device::DEVICE_CPU` 或 `base_device::DEVICE_GPU`

`pointer_in`：被拷贝的指针

`pointer_out`：拷贝的目标指针

`size`：拷贝内存区域的大小

使用这两个算子可以将 CPU 上的数据拷贝到 GPU 上，或者将 GPU 数据转移到 CPU 上。也可以在同一设备上使用实现内存区域的拷贝。

### 3.4 删除内存区域

为了防止内存溢出，一定要记得在开辟内存区域最后删除。在 `memory_op.h` 提供了以下算子来释放内存空间

```cpp
template <typename FPTYPE, typename Device>
struct delete_memory_op
{
    /// @brief free memory for multi-device
    ///
    /// Input Parameters
    /// \param arr : the input array
    void operator()(const Device* dev, FPTYPE* arr);
};
```

这个使用方式非常简单，只需要

```cpp
base_device::memory::delete_memory_op<TYPE, DEVICE>()(pointer);
```

`TYPE`：被操作指针的数据类型

`DEVICE`：计算设备类型，可选 `base_device::DEVICE_CPU` 或 `base_device::DEVICE_GPU`

`pointer`：需要删除内存区域的指针

### 3.5 使用别名

在一般使用的时候，为了避免算子名称过长导致的代码可读性下降，我们一般使用关键字 using 来缩短对应模板函数的名称，如

```cpp
using resmem_sh_op = base_device::memory::resize_memory_op<float, base_device::DEVICE_CPU>;

// Then you can directly using resmem_sh_op to resize memory
```

在 `memory_op.h` 中，已经做好了大量这种定义

```cpp
using resmem_sh_op = base_device::memory::resize_memory_op<float, base_device::DEVICE_CPU>;
using resmem_dh_op = base_device::memory::resize_memory_op<double, base_device::DEVICE_CPU>;
using resmem_ch_op = base_device::memory::resize_memory_op<std::complex<float>, base_device::DEVICE_CPU>;
using resmem_zh_op = base_device::memory::resize_memory_op<std::complex<double>, base_device::DEVICE_CPU>;

using resmem_sd_op = base_device::memory::resize_memory_op<float, base_device::DEVICE_GPU>;
using resmem_dd_op = base_device::memory::resize_memory_op<double, base_device::DEVICE_GPU>;
using resmem_cd_op = base_device::memory::resize_memory_op<std::complex<float>, base_device::DEVICE_GPU>;
using resmem_zd_op = base_device::memory::resize_memory_op<std::complex<double>, base_device::DEVICE_GPU>;

using setmem_sh_op = base_device::memory::set_memory_op<float, base_device::DEVICE_CPU>;
using setmem_dh_op = base_device::memory::set_memory_op<double, base_device::DEVICE_CPU>;
using setmem_ch_op = base_device::memory::set_memory_op<std::complex<float>, base_device::DEVICE_CPU>;
using setmem_zh_op = base_device::memory::set_memory_op<std::complex<double>, base_device::DEVICE_CPU>;

using setmem_sd_op = base_device::memory::set_memory_op<float, base_device::DEVICE_GPU>;
using setmem_dd_op = base_device::memory::set_memory_op<double, base_device::DEVICE_GPU>;
using setmem_cd_op = base_device::memory::set_memory_op<std::complex<float>, base_device::DEVICE_GPU>;
using setmem_zd_op = base_device::memory::set_memory_op<std::complex<double>, base_device::DEVICE_GPU>;

using delmem_sh_op = base_device::memory::delete_memory_op<float, base_device::DEVICE_CPU>;
using delmem_dh_op = base_device::memory::delete_memory_op<double, base_device::DEVICE_CPU>;
using delmem_ch_op = base_device::memory::delete_memory_op<std::complex<float>, base_device::DEVICE_CPU>;
using delmem_zh_op = base_device::memory::delete_memory_op<std::complex<double>, base_device::DEVICE_CPU>;

using delmem_sd_op = base_device::memory::delete_memory_op<float, base_device::DEVICE_GPU>;
using delmem_dd_op = base_device::memory::delete_memory_op<double, base_device::DEVICE_GPU>;
using delmem_cd_op = base_device::memory::delete_memory_op<std::complex<float>, base_device::DEVICE_GPU>;
using delmem_zd_op = base_device::memory::delete_memory_op<std::complex<double>, base_device::DEVICE_GPU>;

using syncmem_s2s_h2h_op
    = base_device::memory::synchronize_memory_op<float, base_device::DEVICE_CPU, base_device::DEVICE_CPU>;
using syncmem_s2s_h2d_op
    = base_device::memory::synchronize_memory_op<float, base_device::DEVICE_GPU, base_device::DEVICE_CPU>;
using syncmem_s2s_d2h_op
    = base_device::memory::synchronize_memory_op<float, base_device::DEVICE_CPU, base_device::DEVICE_GPU>;
using syncmem_d2d_h2h_op
    = base_device::memory::synchronize_memory_op<double, base_device::DEVICE_CPU, base_device::DEVICE_CPU>;
using syncmem_d2d_h2d_op
    = base_device::memory::synchronize_memory_op<double, base_device::DEVICE_GPU, base_device::DEVICE_CPU>;
using syncmem_d2d_d2h_op
    = base_device::memory::synchronize_memory_op<double, base_device::DEVICE_CPU, base_device::DEVICE_GPU>;

using syncmem_c2c_h2h_op
    = base_device::memory::synchronize_memory_op<std::complex<float>, base_device::DEVICE_CPU, base_device::DEVICE_CPU>;
using syncmem_c2c_h2d_op
    = base_device::memory::synchronize_memory_op<std::complex<float>, base_device::DEVICE_GPU, base_device::DEVICE_CPU>;
using syncmem_c2c_d2h_op
    = base_device::memory::synchronize_memory_op<std::complex<float>, base_device::DEVICE_CPU, base_device::DEVICE_GPU>;
using syncmem_z2z_h2h_op
    = base_device::memory::synchronize_memory_op<std::complex<double>, base_device::DEVICE_CPU, base_device::DEVICE_CPU>;
using syncmem_z2z_h2d_op
    = base_device::memory::synchronize_memory_op<std::complex<double>, base_device::DEVICE_GPU, base_device::DEVICE_CPU>;
using syncmem_z2z_d2h_op
    = base_device::memory::synchronize_memory_op<std::complex<double>, base_device::DEVICE_CPU, base_device::DEVICE_GPU>;

using castmem_s2d_h2h_op
    = base_device::memory::cast_memory_op<double, float, base_device::DEVICE_CPU, base_device::DEVICE_CPU>;
using castmem_s2d_h2d_op
    = base_device::memory::cast_memory_op<double, float, base_device::DEVICE_GPU, base_device::DEVICE_CPU>;
using castmem_s2d_d2h_op
    = base_device::memory::cast_memory_op<double, float, base_device::DEVICE_CPU, base_device::DEVICE_GPU>;
using castmem_d2s_h2h_op
    = base_device::memory::cast_memory_op<float, double, base_device::DEVICE_CPU, base_device::DEVICE_CPU>;
using castmem_d2s_h2d_op
    = base_device::memory::cast_memory_op<float, double, base_device::DEVICE_GPU, base_device::DEVICE_CPU>;
using castmem_d2s_d2h_op
    = base_device::memory::cast_memory_op<float, double, base_device::DEVICE_CPU, base_device::DEVICE_GPU>;

using castmem_c2z_h2h_op = base_device::memory::
    cast_memory_op<std::complex<double>, std::complex<float>, base_device::DEVICE_CPU, base_device::DEVICE_CPU>;
using castmem_c2z_h2d_op = base_device::memory::
    cast_memory_op<std::complex<double>, std::complex<float>, base_device::DEVICE_GPU, base_device::DEVICE_CPU>;
using castmem_c2z_d2h_op = base_device::memory::
    cast_memory_op<std::complex<double>, std::complex<float>, base_device::DEVICE_CPU, base_device::DEVICE_GPU>;
using castmem_z2c_h2h_op = base_device::memory::
    cast_memory_op<std::complex<float>, std::complex<double>, base_device::DEVICE_CPU, base_device::DEVICE_CPU>;
using castmem_z2c_h2d_op = base_device::memory::
    cast_memory_op<std::complex<float>, std::complex<double>, base_device::DEVICE_GPU, base_device::DEVICE_CPU>;
using castmem_z2c_d2h_op = base_device::memory::
    cast_memory_op<std::complex<float>, std::complex<double>, base_device::DEVICE_CPU, base_device::DEVICE_GPU>;
```

在这个命名中，`s,d,c,z` 分别代表 `float,double,std::complex<float>,std::complex<double>` 这四种数据类型。而 `h` 代表 host，一般都指的是 CPU，`d` 代表 device，一般都指 GPU。

所以一个名为 `syncmem_s2s_h2d_op` 的别名指的是一个将 float 转换为 float（s2s），将数据从 CPU 拷贝到 GPU（h2d）的 `synchronize_memory_op`。

## 四、数据内存管理（新）

在 Pull Request [https://github.com/deepmodeling/abacus-develop/pull/5861](https://github.com/deepmodeling/abacus-develop/pull/5861) 合并之后，添加了直接进行内存管理的函数。这些函数本质上是对上述算子的封装，但是使用它可以使代码更加清晰，且避免了增加重构工作的工作量。因此建议使用这些函数进行内存管理。

### 4.1 给指针分配内存

```cpp
template <typename FPTYPE>
void resize_memory(FPTYPE* arr, const size_t size, base_device::AbacusDevice_t device_type = base_device::AbacusDevice_t::CpuDevice);
```

直接调用这个函数即可给指针 `arr` 分配内存。`FPTYPE` 可为包括 float, double, std::complex<float>和 std::complex<double>的任意数据类型。`device_type` 可选 `base_device::AbacusDevice_t::CpuDevice` 或者 `base_device::AbacusDevice_t::GpuDevice`。

### 4.2 初始化一片内存的值

```cpp
template <typename FPTYPE>
void set_memory(FPTYPE* arr, const int var, const size_t size, base_device::AbacusDevice_t device_type = base_device::AbacusDevice_t::CpuDevice);
```

直接调用这个函数即可给指针 `arr` 管理的一片内存区域初始化值。

其中，`var` 是需要赋的数值，<strong>只能为 0 或者-1</strong>！`size` 是这片内存区域的长度。`device_type` 可选 `base_device::AbacusDevice_t::CpuDevice` 或者 `base_device::AbacusDevice_t::GpuDevice`。

注意！由于底层实现的原因，这个算子只能用来将一片内存区域<strong>全部设置为 0 或者全部设置为-1</strong>，不能用于给这篇内存填充别的特定数值。一般情况下我们也不会需要使用这个来填充别的数值的使用场景。

### 4.3 在不同设备间转移数据

有如下两个函数可以用于在不同设备间转移数据。

```cpp
template <typename FPTYPE>
void synchronize_memory(FPTYPE* arr_out, const FPTYPE* arr_in, const size_t size, base_device::AbacusDevice_t device_type_out, base_device::AbacusDevice_t device_type_in);

template <typename FPTYPE_out, typename FPTYPE_in>
void cast_memory(FPTYPE_out* arr_out, const FPTYPE_in* arr_in, const size_t size, base_device::AbacusDevice_t device_type_out, base_device::AbacusDevice_t device_type_in);
```

其中，`synchronize_memory` 负责转移同类型数据，`cast_memory` 可以转移不同类型的数据。

`arr_out` 是转移数据的目标指针，`arr_in` 是转移数据的原始指针。`size` 是转移数据的长度。

`device_type_out` 是目标设备类型，可选 `base_device::AbacusDevice_t::CpuDevice` 或者 `base_device::AbacusDevice_t::GpuDevice`。

`device_type_in` 是数据原本储存区域的设备类型，可选 `base_device::AbacusDevice_t::CpuDevice` 或者 `base_device::AbacusDevice_t::GpuDevice`。

如果 `device_type_out` 和 `device_type_in` 相同的话，则是进行一次简单的数据拷贝工作。

### 4.4 删除内存区域

为了防止内存溢出，一定要记得在开辟内存区域最后删除。只需要简单的执行这个函数即可

```cpp
emplate <typename FPTYPE>
void delete_memory(FPTYPE* arr, base_device::AbacusDevice_t device_type = base_device::AbacusDevice_t::CpuDevice);
```

这个函数会删除指定设备上的 `arr` 指针的内存区域。

## 五、执行数学计算

现在可以直接调用 Blas_connector 进行异构计算。只需要包含 `source/module_base/blas_connector.h` 这个头文件即可。

在 `blas_connector.h` 中，链接了 blas 的诸多函数（不建议直接使用），且都实现了对应的异构算子，只需要调整一个参数即可选择对应的异构设备进行计算。

要使用实现好的算子，只需要调用 `BlasConnector` 命名空间下的算子即可。具体有哪些算子直接查看 `source/module_base/blas_connector.h`。以最常用的 gemm 为例，这些算子一般是这么构成的

```cpp
static
void gemm(const char transa, const char transb, const int m, const int n, const int k,
    const float alpha, const float *a, const int lda, const float *b, const int ldb,
    const float beta, float *c, const int ldc, base_device::AbacusDevice_t device_type = base_device::AbacusDevice_t::CpuDevice);

static
void gemm_cm(const char transa, const char transb, const int m, const int n, const int k,
    const float alpha, const float *a, const int lda, const float *b, const int ldb,
    const float beta, float *c, const int ldc, base_device::AbacusDevice_t device_type = base_device::AbacusDevice_t::CpuDevice);
```

这个算子前面的所有参数都和标准 blas 算子的参数排列方式相同，只要以相同的方式传入参数即可。注意到最后一个参数是 `base_device::AbacusDevice_t` 类型的参数，这是一个来自上文所说的 `source/module_base/module_device/types.h` 的枚举类型，代表使用的计算设备。如果我们需要在 GPU 上调用对应的算子进行计算的话，就这么使用

```cpp
BlasConnector::gemm(...parameters..., base_device::AbacusDevice_t::GpuDevice);
```

如果需要在 CPU 上进行计算，只需要把这个参数改成 `base_device::AbacusDevice_t::GpuDevice` 或者直接空着不写（不建议），因为默认值就是 CPU 参数。

可以注意到，对于相同的算子有时候会有两种类型的封装，其中一种有后缀 `_cm`，这代表这是一个<strong>列优先</strong> 的封装，如果没有后缀则为一个<strong>行优先</strong> 的封装。由于 blas 本身都是基于列优先实现的，所以部分算子可能没有<strong>行优先</strong> 的封装。

这样你就可以使用上文所述的内存管理工具和 Blas 计算库，在完全不使用专用的异构 API，如 CUDA，来进行异构代码的编写，实现功能在不同的设备上都能够运行。
