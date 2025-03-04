# Tensor 类文档 2：使用和拓展

作者：陈诺，邮箱：cn037@stu.pku.edu.cn

审核：陈默涵，邮箱：mohanchen@pku.edu.cn

最后更新时间：2025/03/02

# 一、概述

`Tensor` 是一种底层数据容器，提供了跨平台的数据管理和计算操作。

- 通过异构内存管理和算子构建，实现“一套代码跨平台运行”，能够在不同平台（如 CPU，GPU 和 DCU）上通过 Tensor 对象分配和管理内存，并使用不同平台上的库和代码展开异构计算。
- 在密度泛函理论（DFT）为代表的科学计算中，`Tensor` 可以作为单纯的统一底层多维数据结构，为跨平台的算法开发提供支持；同时，`Tensor` 的设计参考了当今最流行的深度学习框架如 PyTorch 和 TensorFlow 中的张量(Tensor)实现，保留了引入自动微分等现代深度学习框架其他功能的可能性。

## 1.1 代码结构

代码目录：

[abacus-develop/source/module_base/module_container at develop · deepmodeling/abacus-develop](https://github.com/deepmodeling/abacus-develop/tree/develop/source/module_base/module_container)

```bash
➜  module_base git:(develop) ✗ tree -d module_container 
module_container            #代码位置，位于module_base目录下
├── ATen                    #ATen/Array-Tensor 存储了Tensor容器的方法
│   ├── core                #存储了Tensor对象的核心方法，比如reshape，tensor_buffer以及Tensor对象的定义
│   ├── kernels             #定义了异构计算的函数，比如矩阵乘法gemm/gemv等等
│   │   ├── cuda            #提供了异构计算函数所需的CUDA实现
│   │   ├── rocm            #提供了异构计算函数所需的ROCM实现
│   │   └── test            #针对定义的异构计算函数的单元测试
│   └── ops                 #针对Tensor对象，定义了一系列算子
│       └── test            #算子的单元测试
├── base                    #Tensor无关的基础函数
│   ├── core                
│   ├── macros              #常用的宏函数声明
│   ├── third_party         #第三方软件，比如BLAS等的声明
│   │   └── backward-cpp    #提供backtrace的实现
│   └── utils           
└── test                    #base模块的单元测试
```

Tensor 代码目录中唯一的外部依赖为 `"module_base/module_device/types.h"`，用于和现有 HSolver 模块中使用的 Device 模板参数交互。

## 1.2 头文件

该类依赖以下头文件：

```cpp
#include <base/core/allocator.h>         // 存储管理模块
#include <ATen/core/tensor_types.h>      // 自定义类型
#include <ATen/core/tensor_shape.h>      // Tensor维度管理
#include <ATen/core/tensor_buffer.h>     // 管理Tensor对象的数据存储
#include <ATen/core/tensor_accessor.h>   // Tensor对象的访问函数
#include <ATen/kernels/memory.h>         // 内存操作函数
#include <base/macros/macros.h>          // 宏函数定义
```

# 二、Tensor 对象的构造和生命周期

Tensor 对象可以自行分配所需设备上的内存空间，也可以暂时管理一块内存（不负责分配、释放），相当于提供了一个“视图”。

## 2.1 DeviceType

Tensor 是一种异构容器，在构造对象时，需要指明所处的位置。

Tensor<u>不是模板类</u>。不同于基于模板的类，Tensor 对象接收一个 `ct::DeviceType` 类型的 `device_type` 参数，以参数形式决定数据存储位置。

- 可选择的设备类型有：
  （Tensor 内部的 device）

```cpp
// source/module_base/module_container/ATen/core/tensor_types.h
namespace container {
    enum class DeviceType {
        UnKnown = 0,  ///< Memory type is unknown.
        CpuDevice = 1,     ///< Memory type is CPU.
        GpuDevice = 2,     ///< Memory type is GPU(CUDA or ROCm).
    };
}
```

- 外部的设备类型标识符，如HSolver模块中使用的模板参数计算设备标识符base_device::AbacusDevice_t

```cpp
// ./ATen/core/tensor_types.h:#include "module_base/module_device/types.h"
namespace base_device
{
    enum AbacusDevice_t
    {
        UnKnown,
        CpuDevice,
        GpuDevice,
        DspDevice
    };
}
```

在使用Tensor时应转化为Tensor内部的container::DeviceType：

```cpp
// 在当前调用 Tensor 的 HSolver 模块中，如果接收到的 Device 为外部的base_device::AbacusDevice_t 类型，
// 需要转化为 Tensor 内部的设备类型。

using ct_Device = typename ct::PsiToContainer<Device>::type;
// 此处的 ct: namespace ct = container; tensor.h 中定义的别名

// source/module_base/module_container/ATen/core/tensor_types.h
template <>
struct PsiToContainer<base_device::DEVICE_CPU>
{
    using type = container::DEVICE_CPU; /**< The return type specialization for std::complex<float>. */
};

template <>
struct PsiToContainer<base_device::DEVICE_GPU>
{
    using type = container::DEVICE_GPU; /**< The return type specialization for std::complex<double>. */
};
```

此处的`PsiToContainer`即为针对HSolver中`base_device::AbacusDevice_t`的转化，由于设备类型命名和Tensor完全相同，需要特别注意。
其他基于模板参数指定设备类型的转化，可仿照该函数实现。

## 2.2 DataType

Tensor是一种多精度容器，支持不同类型不同精度的原始数据。

可选择的数据类型有：

```cpp
// source/module_base/module_container/ATen/core/tensor_types.h
enum class DataType {
    DT_INVALID = 0, ///< Invalid data type */
    DT_FLOAT = 1, ///< Single-precision floating point */
    DT_DOUBLE = 2, ///< Double-precision floating point */
    DT_INT = 3, ///< 32-bit integer */
    DT_INT64 = 4, ///< 64-bit integer */
    DT_COMPLEX = 5, ///< 32-bit complex */
    DT_COMPLEX_DOUBLE = 6, /**< 64-bit complex */
// ... other data types
};
```

构造方式

```cpp
container::Tensor t(container::DataType::DT_DOUBLE, container::DeviceType::GpuDevice,
                         container::TensorShape({3, 4}));
```

## 2.3 TensorShape

指定 Tensor 形状的类型。

在调用时，一般以 `std::initializer_list` 的形式构造和使用，见“构造”部分。

```cpp
TensorShape(std::initializer_list<int64_t> dims);
```

## 2.4 构造

`Tensor` 的构造函数定义在 `source/module_base/module_container/ATen/core/tensor.h` 中。

1. `Tensor()`

   1. 默认构造函数。创建一个 1 维，0 个元素的空的 float Tensor 对象。
2. `explicit Tensor(DataType data_type)`

   1. 构造一个给定 `data_type` 数据类型的 Tensor。
   2. 必须显式（explicit）调用，不会用于隐式的类型转换。
3. `Tensor(DataType data_type, const TensorShape& shape)`

   1. 构造一个给定数据类型 `data_type` 和形状 `shape` 的 Tensor。
   2. 在指定形状时，可以使用`TensorShape`的基于 [std::initializer_list](https://en.cppreference.com/w/cpp/utility/initializer_list) 的构造函数，传入一个由维度构成的列表：

    ```cpp
    Tensor(t_type, {dim1, dim2});
    ```

4. `Tensor(DataType data_type, DeviceType device, const TensorShape& shape)`

	1. 构造一个给定数据类型`data_type`和形状`shape`的Tensor。
	2. 数据存放在指定的device上。
5. `Tensor(const Tensor& other)`

	1. 复制构造函数，deep copy另一个Tensor的数据域。
6. `Tensor(Tensor&& other) noexcept`

	1. 移动构造函数。
	2. 用于临时对象，通过`std::move`避免不必要的资源复制，资源的所有权从一个对象转移到另一个对象。
	3. 也可作为从头开始构造一个Tensor的一种形式：
	4. 
    ```cpp
    work = std::move(ct::Tensor(t_type, device_type, {dim1, dim2}));
    ```

此外，还有其他的构造方式，如：

7. `bool AllocateFrom(const Tensor& other, const TensorShape& shape)`
   1. 从 other 复制数据，并根据传入的 shape 重新分配内存。原先拥有的内存块会被释放。
   2. 如果复制和分配成功则返回 true。

## 2.5 复制

对于 `Tensor` 对象，我们也希望重用其中的数据。有时希望在某些操作后保留原始数据而非就地修改，这时就需要以某种方式“复制”一个 Tensor 对象。

`Tensor` 类有“浅”和“深”两种数据共享方式。

实际上，我们使用的对象一般不直接存放原始数据，而是提供了一个针对大块内存的“引用”（reference）或指针（pointer）；实际传参时，引入的参数也是这样的引用而非大批量原始数据。当多个引用（如 A 和 B）指向同一块原始数据时，基于 A 对原始数据做出的改变，自然也会在通过 B 访问数据时看见这些改变，因为它们引用的实际上是同一块内存。

以下，从另一个 Tensor“复制数据”指的是：

1. data_type
2. device
3. shape


- “浅拷贝”(Shallow copy)
  - 创建一个新的对象，复制原始对象的各字段（field）和引用（数据域指针的值），但不复制引用指向的实际原始数据域。这将导致新旧两个对象共享相同的内存数据。
  - 快速和节省空间，提高性能，特别是在处理大对象时；必须时刻注意自己在操作的实际上是某个对象的“引用”。
  - 在 Tensor 中，`CopyFrom` 函数提供了这一功能。

```cpp
// ATen/core/tensor.h

// 以下所有方法 复制数据，但是共享原始内存。

class Tensor {
// 复制成功返回 true
bool CopyFrom(const Tensor& other);
// 复制的同时 reshape 到传入的TensorShape，如果复制和 reshape 都成功则返回 true。
bool CopyFrom(const Tensor& other, const TensorShape& shape);

}
```

- 此外，如果我们需要直接“接管”一个临时对象，Tensor的赋值运算符可以接受一个右值，并获得该Tensor对象的内容和所有权。这实质上是一个浅拷贝。参数`other`是源Tensor对象的右值引用，表示临时对象或将要被移动的对象。
	
```cpp
// ATen/core/tensor.h
Tensor& operator=(Tensor&& other) noexcept;

// 例如
// source/module_hsolver/diago_bpcg.cpp
this->eigen    = std::move(ct::Tensor(r_type, device_type, {this->n_band}));
```

- “深拷贝”(Deep copy)
  - 创建一个新的对象，递归复制原始对象的所有字段，会创建所有属性和嵌套对象的独立副本，获得一个和原始对象完全独立的全新对象。
  - 这意味着开辟一块和原对象相同大小的内存，逐个复制其中的全部元素。安全，但是慢且消耗内存。
  - 在 Tensor 中，这一操作由赋值运算符“=”实现。

```cpp
// ATen/core/tensor.h
// 这个赋值操作会进行内存分配和复制。
Tensor& operator=(const Tensor& other);
```

当赋值的右端是一个右值rvalue时，请参考“浅拷贝”中的重载。

- 此外，如果不创建新对象，想要复制数据域，可以使用`sync`：
  
```cpp
// 确保当前Tensor的数据和rhs同步。
void sync(const Tensor& rhs);
// module_hsolver/hsolver_pw.cpp
ct::TensorMap(psi.get_pointer(), psi_tensor, {psi.get_nbands(), psi.get_nbasis()}).sync(psi_tensor);
```

## 2.6 其他成员函数

`template <typename T> T* data() const` 直接数据域的接口。可以和其他的自定义算子等基于 `T *` 的接口交互。

例如：

```cpp
const Real eh = hsolver::dot_real_op<T, Device>()(ctx_, this->n_basis_, sphi.data<T>(), grad.data<T>());
```

不常用，见 [Tensor 类文档 1：构造和使用说明](https://mcresearch.github.io/abacus-user-guide/develop-tensor1.html)

部分使用方法可见单元测试

`abacus-develop/source/module_base/module_container/test/tensor_test.cpp`

# 三、TensorMap

`TensorMap` 类是一个特殊的 `Tensor` 类，它提供了一种方式来映射一个<u>已经存在的数据指针</u>到一个 `Tensor` 对象，而不是拥有和管理自己的内存。这种设计使得 `TensorMap` 可以引用和操作存储在其他地方的数据，而不需要复制数据。因此，`TensorMap` 对它托管对象的生命周期不负责任，也不应该析构外部传入的数据域。

在我们把波函数初猜等来自外界的非空数据纳入 Tensor 框架时，可能需要使用这种方式。需要注意的是，必须获取可靠的外部维度信息，并在使用 Tensor 时保持维度的一致性。

## 3.1 构造

1. `TensorMap(void *data, DataType data_type,DeviceType device, const TensorShape &shape)`

   1. 把一块数据域 `data` 映射到一个 `Tensor` 对象
2. `TensorMap(void *data, const Tensor& other, const TensorShape& shape)`

   1. 创建一个 `TensorMap` 对象，它引用由 `data` 指针指向的数据，并将其与给定 `Tensor` 对象 other 和 shape 关联。允许以指定的形状访问数据，而不拥有数据。
3. `TensorMap(void *data, const Tensor& other)`

   1. 数据的形状由 other 的形状决定。

## 3.2 使用

TensorMap 可以在和外界交互时，将返回的结果写入外部内存。

```cpp
// source/module_hsolver/hsolver_pw.cpp
ct::TensorMap(psi.get_pointer(), psi_tensor, {psi.get_nbands(), psi.get_nbasis()}).sync(psi_tensor);
```

这段代码将一个外部的指针包装成 TensorMap，并使用 Tensor 的 sync 复制了数据块。

# 四、算子

利用异构的 Tensor 对象，进行相应的异构计算操作。

为了实现“一套代码，八方通行”，针对一个统一的接口，在底层需要进行不同设备、不同精度的重载。

```bash
(base) ➜  module_container git:(develop) ✗ tree -L 2
.
├── ATen
│   ├── core
│   ├── kernels
│   ├── ops
│   └── tensor.h
├── base
│   ├── core
│   ├── macros
│   ├── third_party
│   └── utils
├── CMakeLists.txt
└── test
    ├── ...
    └── tensor_utils_test.cpp
```

例如，对于常用的底层计算（kernels），定义在 `ATen/kernels` 中 `blas.*`：

```bash
# ATen/kernels
kernels
├── blas.cpp
├── blas.h
├── CMakeLists.txt
├── cuda
│   ├── blas.cu
│   ├── lapack.cu
│   ├── linalg.cu
│   └── memory.cu
├── lapack.cpp
├── lapack.h
├── linalg.cpp
├── linalg.h
├── memory.h
├── memory_impl.cpp
├── rocm
│   ├── blas.hip.cu
│   ├── lapack.hip.cu
│   ├── linalg.hip.cu
│   └── memory.hip.cu
└── test
    ├── blas_test.cpp
    ├── CMakeLists.txt
    ├── lapack_test.cpp
    ├── linalg_test.cpp
    └── memory_test.cpp
```

在 `.h` 文件中声明后，需要实现对应的异构支持：

- `.h` 声明
  - 面向算法实现者的统一接口

```cpp
template <typename T, typename Device>
struct blas_gemv {
void operator()(
const char& trans,
const int& m,
const int& n,
const T* alpha,
const T* A,
const int& lda,
const T* x,
const int& incx,
const T* beta,
T* y,
const int& incy);
};
```

- `.cpp` CPU实现，位于对应的cpp中
	- 调用CPU Blas LAPACK库等
	- 此处在`.cpp`中实现了针对DEVICE_CPU 的重载
	- 通过下一层函数重载支持不同数据类型（BlasConnector`::`gemv）

```cpp
template <typename T>
struct blas_gemv<T, DEVICE_CPU> {
    void operator()(
        const char& trans,
        const int& m,
        const int& n,
        const T* alpha,
        const T* A,
        const int& lda,
        const T* x,
        const int& incx,
        const T* beta,
        T* y,
        const int& incy)
    {
        BlasConnector::gemv(trans, m, n, *alpha, A, lda, x, incx, *beta, y, incy);
    }
};
```

- `cuda/.cu` GPU 实现
  - 调用 CuBLAS 库等，包括对于 handle 等平台代码的处理和包装

 ```cpp
template <typename T>
struct blas_gemv<T, DEVICE_GPU> {
    void operator()(
        const char& trans,
        const int& m,
        const int& n,
        const T* alpha,
        const T* A,
        const int& lda,
        const T* x,
        const int& incx,
        const T* beta,
        T* y,
        const int& incy)
    {
        cuBlasConnector::gemv(cublas_handle, trans, m, n, *alpha, A, lda, x, incx, *beta, y, incy);
    }
};
```

- `rocm/.hip.cu` DCU实现
	- 类似GPU的CUDA实现
	- 随着DCU平台增加对CUDA的支持，不用再手动维护DCU专用版本代码

算子在底层用多套代码实现了异构，开发算法时，可以对不同的计算设备和精度，用统一的接口调用。

更高层的线性代数操作，可以在简单kernels的基础上进行。

例如，Tensor中有对于`einsum`的实现，位于`ATen/ops`中：

```cpp
// Make the conj params only works for the matmul equations.
inline static Tensor einsum(const std::string& equation, const Tensor& A) {
    const EinsumOption& option = {};
    return std::move(op::einsum_impl(equation, option, A));
}

inline static Tensor einsum(const std::string& equation, const Tensor& A, const Tensor& B, const EinsumOption& option = {}) {
    return std::move(op::einsum_impl(equation, option, A, B));
}
```

该算子基于多个中间层操作最终调用 Tensor 定义的 gemm 接口。

```cpp
kernels::blas_gemm<T, Device>()
```
