# ABACUS 如何处理内存 bug？

<strong>作者：刘千锐，邮箱：terry_liu@pku.edu.cn</strong>

<strong>最后更新时间：2024.12.25</strong>

# 一、<strong>前言</strong>

在 ABACUS 的开发和重构过程中，段错误、内存泄漏等内存问题不可避免。这些问题通常由<strong>变量的未初始化</strong>、<strong>地址的无效读写</strong>、<strong>内存分配未释放、内存双重释放</strong>等原因引起。为了在出现这些问题后能够快速定位并解决，可以借助 AddressSanitizer、Valgrind、Compute Sanitizer 等工具进行问题排查。

# 二、AddressSanitizer 的使用

相比 Valgrind，AddressSanitizer 的运行速度更快。它能够有效地检测指针越界、内存未释放等明显的内存问题，但无法发现由未初始化变量引起的错误。因此，AddressSanitizer 适用于第一步的快速检测。

AddressSanitizer 仅支持 GNU 编译器。使用时，只需在编译时通过 `gcc`、`g++`、`gfortran` 等命令添加 `-fsanitize=address ` 等选项即可。在 ABACUS 中，只需将 CMake 中的 `ENABLE_ASAN` 变量设置为 `ON`，即可启用该功能。可以通过执行 `cmake -DENABLE_ASAN=ON` 或直接修改主目录下的 `CMakeLists.txt` 文件（不推荐这种方式）来实现。编译完成后，直接运行 ABACUS 或单元测试的可执行文件，即可开始检测内存问题。

这里倡议每位开发者新加的单元测试，或者集成测试都应该至少要通过 AddressSanitizer 的检测~

以下为一些检测示例：

## 1. 内存泄漏：

```cpp
<strong>==3802922==ERROR: LeakSanitizer: detected memory leaks</strong>

<strong>Direct leak of 40 byte(s) in 1 object(s) allocated from:</strong>
    #0 0x7f938ed35787 in operator new[](unsigned long) ../../../../src/libsanitizer/asan/asan_new_delete.cc:107
<strong>    #1 0x556d75ea6897 in UnitCell::read_atom_species(std::basic_ifstream<char, std::char_traits<char> >&, std::basic_ofstream<char, std::char_traits<char> >&) /home/qianrui/github/reconstruction/hotfix/source/module_cell/read_atoms.cpp:25</strong>
    #2 0x556d75e898b2 in UnitCell::setup_cell(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::basic_ofstream<char, std::char_traits<char> >&) /home/qianrui/github/reconstruction/hotfix/source/module_cell/unitcell.cpp:521
    #3 0x556d765e788a in Driver::driver_run() /home/qianrui/github/reconstruction/hotfix/source/driver_run.cpp:49
    #4 0x556d765e0e76 in Driver::atomic_world() /home/qianrui/github/reconstruction/hotfix/source/driver.cpp:180
    #5 0x556d765e6667 in Driver::init() /home/qianrui/github/reconstruction/hotfix/source/driver.cpp:37
    #6 0x556d75c8006f in main /home/qianrui/github/reconstruction/hotfix/source/main.cpp:43
```

以上输出说明了<strong>read_atoms.cpp:25</strong>处分配的内存未释放：

```cpp
this->atom_label = new std::string[ntype]; //atom labels
```

需要在析构函数中加入该内存的释放。

## 2. 双重释放/释放后使用：

```cpp
<strong>==3805185==ERROR: AddressSanitizer: heap-use-after-free on address 0x604000012510 at pc 0x5580e4711320 bp 0x7fff1f0e03b0 sp 0x7fff1f0e03a0</strong>
<strong>READ of size 8 at 0x604000012510 thread T0</strong>
    <strong>#0 0x5580e471131f in UnitCell::~UnitCell() /home/qianrui/github/reconstruction/hotfix/source/module_cell/unitcell.cpp:46</strong>
    #1 0x5580e4e7e11e in Driver::driver_run() /home/qianrui/github/reconstruction/hotfix/source/driver_run.cpp:42
    #2 0x5580e4e76ff6 in Driver::atomic_world() /home/qianrui/github/reconstruction/hotfix/source/driver.cpp:180
    #3 0x5580e4e7c7e7 in Driver::init() /home/qianrui/github/reconstruction/hotfix/source/driver.cpp:37
    #4 0x5580e451606f in main /home/qianrui/github/reconstruction/hotfix/source/main.cpp:43
    #5 0x7f4f44dde082 in __libc_start_main ../csu/libc-start.c:308
    #6 0x5580e457b54d in _start (/home/qianrui/github/reconstruction/hotfix/build2/abacus+0x31c54d)

<strong>0x604000012510 is located 0 bytes inside of 40-byte region [0x604000012510,0x604000012538)</strong>
<strong>freed by thread T0 here:</strong>
    #0 0x7f4f4e8556ef in operator delete[](void*) ../../../../src/libsanitizer/asan/asan_new_delete.cc:168
    <strong>#1 0x5580e4710ae9 in UnitCell::~UnitCell() /home/qianrui/github/reconstruction/hotfix/source/module_cell/unitcell.cpp:38</strong>
    #2 0x5580e4e7e11e in Driver::driver_run() /home/qianrui/github/reconstruction/hotfix/source/driver_run.cpp:42
    #3 0x5580e4e76ff6 in Driver::atomic_world() /home/qianrui/github/reconstruction/hotfix/source/driver.cpp:180
    #4 0x5580e4e7c7e7 in Driver::init() /home/qianrui/github/reconstruction/hotfix/source/driver.cpp:37
    #5 0x5580e451606f in main /home/qianrui/github/reconstruction/hotfix/source/main.cpp:43

<strong>previously allocated by thread T0 here:</strong>
    #0 0x7f4f4e854787 in operator new[](unsigned long) ../../../../src/libsanitizer/asan/asan_new_delete.cc:107
    <strong>#1 0x5580e473ca17 in UnitCell::read_atom_species(std::basic_ifstream<char, std::char_traits<char> >&, std::basic_ofstream<char, std::char_traits<char> >&) /home/qianrui/github/reconstruction/hotfix/source/module_cell/read_atoms.cpp:25</strong>
    #2 0x5580e471fa32 in UnitCell::setup_cell(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, std::basic_ofstream<char, std::char_traits<char> >&) /home/qianrui/github/reconstruction/hotfix/source/module_cell/unitcell.cpp:522
    #3 0x5580e4e7da0a in Driver::driver_run() /home/qianrui/github/reconstruction/hotfix/source/driver_run.cpp:49
    #4 0x5580e4e76ff6 in Driver::atomic_world() /home/qianrui/github/reconstruction/hotfix/source/driver.cpp:180
    #5 0x5580e4e7c7e7 in Driver::init() /home/qianrui/github/reconstruction/hotfix/source/driver.cpp:37
    #6 0x5580e451606f in main /home/qianrui/github/reconstruction/hotfix/source/main.cpp:43
```

以上输出表明，在<strong>read_atoms.cpp:25</strong>分配的内存，在<strong>unitcell.cpp:38</strong>释放后，又在<strong>unitcell.cpp:46</strong>处二次使用造成内存错误。

## 3. 读写越界

```cpp
<strong>==3810456==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x603000000d18 at pc 0x5589923553a9 bp 0x7ffd0a71e2c0 sp 0x7ffd0a71e2b0</strong>
<strong>WRITE of size 8 at 0x603000000d18 thread T0</strong>
    <strong>#0 0x5589923553a8 in void Mixing_Test::solve_linear_eq<double>(double*, double*, bool) /home/qianrui/github/reconstruction/hotfix/source/module_base/module_mixing/test/mixing_test.cpp:90</strong>
    #1 0x55899233583c in Mixing_Test_BroydenSolveLinearEq_Test::TestBody() /home/qianrui/github/reconstruction/hotfix/source/module_base/module_mixing/test/mixing_test.cpp:162
    #2 0x5589925e2c47 in void testing::internal::HandleSehExceptionsInMethodIfSupported<testing::Test, void>(testing::Test*, void (testing::Test::*)(), char const*) (/home/qianrui/github/reconstruction/hotfix/build2/source/module_base/module_mixing/test/test_mixing+0x2e4c47)

<strong>0x603000000d18 is located 0 bytes to the right of 24-byte region [0x603000000d00,0x603000000d18)</strong>
<strong>allocated by thread T0 here:</strong>
    #0 0x7f8c23365587 in operator new(unsigned long) ../../../../src/libsanitizer/asan/asan_new_delete.cc:104
    #1 0x558992335737 in __gnu_cxx::new_allocator<double>::allocate(unsigned long, void const*) /usr/include/c++/9/ext/new_allocator.h:114
    #2 0x558992335737 in std::allocator_traits<std::allocator<double> >::allocate(std::allocator<double>&, unsigned long) /usr/include/c++/9/bits/alloc_traits.h:443
    #3 0x558992335737 in std::_Vector_base<double, std::allocator<double> >::_M_allocate(unsigned long) /usr/include/c++/9/bits/stl_vector.h:343
    #4 0x558992335737 in std::_Vector_base<double, std::allocator<double> >::_M_create_storage(unsigned long) /usr/include/c++/9/bits/stl_vector.h:358
    #5 0x558992335737 in std::_Vector_base<double, std::allocator<double> >::_Vector_base(unsigned long, std::allocator<double> const&) /usr/include/c++/9/bits/stl_vector.h:302
    #6 0x558992335737 in std::vector<double, std::allocator<double> >::vector(unsigned long, std::allocator<double> const&) /usr/include/c++/9/bits/stl_vector.h:508
    <strong>#7 0x558992335737 in Mixing_Test_BroydenSolveLinearEq_Test::TestBody() /home/qianrui/github/reconstruction/hotfix/source/module_base/module_mixing/test/mixing_test.cpp:161</strong>
```

以上输出表明该单元测试在<strong>mixing_test.cpp:161</strong>分配的内存，在代码<strong>mixing_test.cpp:90</strong>处调用的对其进行了越界的赋值。

# 三、Valgrind 的使用

Valgrind 的检测更为细致，虽然运行速度较慢，但能够捕捉到更多的错误。不过，有时它也可能会“误报”一些问题。通常情况下，Intel 编译器可能会报告更多错误，而切换到 GNU 编译器后，这些问题可能就不再出现。此类问题往往与字符串操作函数、MPI、OpenMP 等相关，可以适当忽略。

valgrind 支持多种编译器，只需正常编译代码，在运行时加上 `valgrind` 即可，例如：

`valgrind ./abacus`

`mpirun -np 4 valgrind ./abacus`

## 1.未初始化的变量

```cpp
==3806036== Conditional jump or move depends on uninitialised value(s)
==3806036==    at 0x4991432: std::ostreambuf_iterator<char, std::char_traits<char> > std::num_put<char, std::ostreambuf_iterator<char, std::char_traits<char> > >::_M_insert_int<long>(std::ostreambuf_iterator<char, std::char_traits<char> >, std::ios_base&, char, long) const (in /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.28)
==3806036==    by 0x499FD8E: std::ostream& std::ostream::_M_insert<long>(long) (in /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.28)
<strong>==3806036==    by 0x109287: main (test.cpp:34)</strong>
```

表明<strong>test.cpp:34</strong>使用了未初始化的变量。

<strong>注意: </strong>

在 ABACUS 中之前有许多类成员变量未初始化，造成使用了未初始化的变量，造成其他位置的段错误，如果只使用 AddressSanitizer 工具检测，就只能定位到段错误的位置，而不能找到造成段错误的原因是使用了未初始化的变量，因此在用 AddressSanitizer 工具检测后无法看出错误原因之后，一定要用 Valgrind 检测

## 2.其他问题

无效写入：`Invalid write of size 4`

无效读取：`Invalid read of size 4`

双重释放：`Invalid free() / delete / delete[] / realloc()`

# 四、Compute Sanitizer 的使用

Compute Sanitizer 仅用于检测 GPU 代码，当前两种方法检测不出来时使用。

使用方法于 Valgrind 类似，在命令前面加 `compute-sanitizer`

例如当将 CPU 分配的内存传入 GPU 函数时：

```cpp
T* sum = new T[PARAM.inp.nbands * nchipk];
hsolver::gemm_op<T, Device>()(ctx, transC,transN, PARAM.inp.nbands, nchipk,npw, &ModuleBase::ONE, &psi(ik, 0, 0), npwx, wfgout, npwx, &ModuleBase::ZERO, sum, PARAM.inp.nbands);
```

valgrind 可能无法报出准确出错的位置，而 compute-sanitizer 就可以：

```cpp
========= Program hit cudaErrorInvalidValue (error 1) due to "invalid argument" on CUDA API call to cudaFree.
=========     Saved host backtrace up to driver entry point at error
=========     Host Frame: [0x418db6]
=========                in /lib/x86_64-linux-gnu/libcuda.so.1
=========     Host Frame:cudaFree [0x4f21e]
=========                in /usr/local/cuda/lib64/libcudart.so.11.0
=========     Host Frame:/home/qianrui/github/reconstruction/hotfix/source/module_base/module_device/cuda/memory_op.cu:202:base_device::memory::delete_memory_op<std::complex<double>, base_device::DEVICE_GPU>::operator()(base_device::DEVICE_GPU const*, std::complex<double>*) [0x789200]
=========                in /home/qianrui/github/reconstruction/hotfix/tests/integrate/187_PW_SDFT_MALL_GPU/../../../build-cuda/abacus
=========     Host <strong>Frame:/home/qianrui/github/reconstruction/hotfix/source/module_hamilt_pw/hamilt_stodft/sto_iter.cpp:114:Stochastic_Iter<std::complex<double>, base_device::DEVICE_GPU>::orthog(int const&, psi::Psi<std::complex<double>, base_device::DEVICE_GPU>&, Stochastic_WF<std::complex<double>, base_device::DEVICE_GPU>&) [0x5ccf76]</strong>
=========                in /home/qianrui/github/reconstruction/hotfix/tests/integrate/187_PW_SDFT_MALL_GPU/../../../build-cuda/abacus
```

# 五、其他方法

如果上述三种方法都无法提供有效的报错位置信息，说明问题可能比较复杂。此时，通常需要将断点处的代码提取成简化版本。例如，可以先将出问题的函数（如 `func1`）单独提取出来，并以单元测试的形式进行验证，查看是否能重现相同的报错。

1. 如果没有报错，接下来需要扩大范围，将调用 `func1` 的函数（如 `func2`）也加入进来，逐步增加代码范围，直到报错复现，并分析是哪个部分的代码导致了内存问题。
2. 如果有报错发生，则可以逐步移除其他部分的代码，找到最小化的代码集，这样就能定位问题的根本原因。

这种类型的 bug 通常较为棘手，解决过程需要开发者保持耐心，并不断尝试和调整。

以下是 ABACUS 解决相关问题的实例，供参考：

[#2351](https://github.com/deepmodeling/abacus-develop/issues/2351)， [FFTWissue](https://github.com/FFTW/fftw3/issues/327)

[#5497 (comment)](https://github.com/deepmodeling/abacus-develop/issues/5497#issuecomment-2561588945)
