# Pyabacus 文档三：开发者指南

<strong>作者：白晨旭</strong>

<strong>审核：陈默涵</strong>

<strong>单位：北京大学</strong>

<strong>最后更新时间：2024-11-15</strong>

# 一、简介

欢迎来到 pyabacus 项目！pyabacus 是国产第一性原理软件 ABACUS（中文名原子算筹）的 Python 接口，它旨在为用户提供了便捷的 Python API，使用户能够利用 Python 语言更灵活地实现电子结构计算并分析结果。本文档主要针对开发者撰写，以下是本文档的目录

- 项目结构

  - 根目录 CMake 配置
  - 模块 CMake 配置
- Python 化上手指南

  - Python 化指南
  - 如何编写单元测试
  - 如何参与开源贡献
- 资料汇总

读者可以参考该系列文档的前两个文档来熟悉 pyabacus。如果读者希望做出贡献，本指南将帮助您了解项目结构、开发流程和代码贡献方式。

# 二、结构

## 2.1 目录结构

pyabacus 项目的目录结构如下所示：

```python
pyabacus/
├── CMakeLists.txt
└── src
    ├── pyabacus
    │   └── {your_module}
    │       ├── {interface}.py
    │       └── __init__.py
    └── {your_module}
        ├── {your_code}.cpp
        └── CMakeLists.txt
```

项目采用 `pybind11` 和 `scikit-build-core` 构建，借助 CMake 构建工具链。因此，CMakeLists.txt 的配置是深入理解项目结构的关键。

## 2.2 根目录 CMake 配置

根目录下的 `CMakeLists.txt` 是 `pyabacus` 项目的主要配置文件。它设置了项目、查找必要的依赖项、配置构建选项，并为不同模块包含子目录。以下是文件中每部分的详细说明：

```python
cmake_minimum_required(VERSION 3.15...3.26)

# 项目设置
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES CXX)
```

- 此部分设置项目名称、版本和使用的编程语言（本项目中为 C++）。项目名称和版本分别从 `SKBUILD_PROJECT_NAME` 和 `SKBUILD_PROJECT_VERSION` 变量中获取。

```python
# 查找 Python 和 pybind11
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
```

- 该部分查找所需的 Python 和 pybind11 包。

```python
# 设置源路径
set(ABACUS_SOURCE_DIR "${PROJECT_SOURCE_DIR}/../../source")
set(BASE_PATH "${ABACUS_SOURCE_DIR}/module_base")
set(NAO_PATH "${ABACUS_SOURCE_DIR}/module_basis/module_nao")
set(HSOLVER_PATH "${ABACUS_SOURCE_DIR}/module_hsolver")
set(PSI_PATH "${ABACUS_SOURCE_DIR}/module_psi")
set(ENABLE_LCAO ON)
list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/../../cmake")
```

- 此部分设置了各种源路径和配置选项，定义了不同模块的路径并附加了自定义的 CMake 模块路径。

```python
# 添加数学库
if(DEFINED ENV{MKLROOT} AND NOT DEFINED MKLROOT)
    set(MKLROOT "$ENV{MKLROOT}")
endif()
if(MKLROOT)
  set(MKL_INTERFACE lp64)
  set(ENABLE_MPI ON)
  if (ENABLE_MPI)
    find_package(MPI REQUIRED)
    include_directories(${MPI_CXX_INCLUDE_PATH})
  endif()

  set(USE_OPENMP ON)
  if(USE_OPENMP)
    find_package(OpenMP REQUIRED)
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    add_link_options(${OpenMP_CXX_LIBRARIES})
  endif()
  find_package(MKL REQUIRED)
  add_definitions(-D__MKL)
  include_directories(${MKL_INCLUDE} ${MKL_INCLUDE}/fftw)

  if(NOT ENABLE_DEEPKS)
    list(APPEND math_libs IntelMKL::MKL)
  endif()

  if(CMAKE_CXX_COMPILER_ID MATCHES Intel)
    list(APPEND math_libs -lifcore)
  endif()
else()
    find_package(FFTW3 REQUIRED)
    add_compile_definitions(__FFTW3)
    find_package(LAPACK REQUIRED)
    include_directories(${FFTW3_INCLUDE_DIRS})
    list(APPEND math_libs FFTW3::FFTW3 LAPACK::LAPACK)

  if(ENABLE_LCAO)
    find_package(ScaLAPACK REQUIRED)
    list(APPEND math_libs ScaLAPACK::ScaLAPACK)
  endif()
endif()
```

- 此部分配置数学库。它检查 Intel 数学核心库 (MKL) 的可用性并在可用时进行配置。如果 MKL 不可用，则改用 FFTW3 和 LAPACK。同时，若启用 MPI 和 OpenMP，也进行相应配置。

```python
# 添加包含目录
include_directories(
    ${BASE_PATH} 
    ${ABACUS_SOURCE_DIR}
    ${ABACUS_SOURCE_DIR}/module_base/module_container
    )
```

- 此部分添加了项目所需的包含目录。

```python
# 添加基本库
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
# 添加 base 模块
set(BASE_BINARY_DIR "${PROJECT_SOURCE_DIR}/build/base")
add_subdirectory(${ABACUS_SOURCE_DIR}/module_base ${BASE_BINARY_DIR})
# 添加 parameter 模块
set(PARAMETER_BINARY_DIR "${PROJECT_SOURCE_DIR}/build/parameter")
add_subdirectory(${ABACUS_SOURCE_DIR}/module_parameter ${PARAMETER_BINARY_DIR})
# 添加 orb 模块
set(ORB_BINARY_DIR "${PROJECT_SOURCE_DIR}/build/orb")
add_subdirectory(${ABACUS_SOURCE_DIR}/module_basis/module_ao ${ORB_BINARY_DIR})
```

- 此部分设置位置无关代码标志，并为 base、parameter、orb 模块添加子目录，指定这些模块的构建目录。

```python
# 设置 RPATH
execute_process(
  COMMAND "${PYTHON_EXECUTABLE}" -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"
  OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
```

- 此部分设置 Python 包目录的<strong>运行时搜索路径</strong> (RPATH)，使用 Python 命令获取 `site-packages` 路径并将其存储在 `PYTHON_SITE_PACKAGES` 变量中。

```python
# 将包名设置为 pyabacus
set(TARGET_PACK pyabacus)
set(CMAKE_INSTALL_RPATH "${PYTHON_SITE_PACKAGES}/${TARGET_PACK}")
```

- 此部分将包名设置为 `pyabacus`，并配置安装 `RPATH` 以包含 Python `site-packages` 目录。

```python
# 为子模块添加子目录
add_subdirectory(${PROJECT_SOURCE_DIR}/src/hsolver)
add_subdirectory(${PROJECT_SOURCE_DIR}/src/ModuleBase)
add_subdirectory(${PROJECT_SOURCE_DIR}/src/ModuleNAO)
```

- 此部分为模块添加子目录，每个子目录包含自己的 `CMakeLists.txt` 以进行进一步配置。

通过遵循此结构，`CMakeLists.txt` 文件确保了所有必要的依赖项被找到、配置并包含在构建过程中。它还设置了项目环境并包含不同组件的子模块。

## 2.3 模块 CMake 配置

以下示例为模块（如 `pyabacus.hsolver`）的 `CMakeLists.txt` 文件：

```python
# 添加 diago 动态链接库
list(APPEND _diago
    ${HSOLVER_PATH}/diago_dav_subspace.cpp
    ${HSOLVER_PATH}/diago_david.cpp
    ${HSOLVER_PATH}/diag_const_nums.cpp
    ${HSOLVER_PATH}/diago_iter_assist.cpp
    ${HSOLVER_PATH}/kernels/dngvd_op.cpp
    ${HSOLVER_PATH}/kernels/math_kernel_op.cpp
    ${BASE_PATH}/kernels/math_op.cpp
    ${BASE_PATH}/module_device/device.cpp
    ${BASE_PATH}/module_device/memory_op.cpp
    ${PSI_PATH}/psi.cpp
)
add_library(diagopack SHARED ${_diago})
target_link_libraries(diagopack
    base
    parameter
    container
    orb
    ${math_libs}
    ${OpenBLAS_LIBRARIES} 
    ${LAPACK_LIBRARIES}
)

list(APPEND pymodule_hsolver
    ${PROJECT_SOURCE_DIR}/src/hsolver/py_hsolver.cpp
)

# 使用 pybind11 添加 Python 模块
pybind11_add_module(_hsolver_pack MODULE ${pymodule_hsolver})
# 将依赖项和 pybind11 库链接到模块
target_link_libraries(_hsolver_pack PRIVATE pybind11::headers diagopack)
target_compile_definitions(_hsolver_pack PRIVATE VERSION_INFO=${PROJECT_VERSION})

set_target_properties(diagopack PROPERTIES INSTALL
```

## 2.4 Python 化上手指南

- [Pybind 简单教程](https://r0ya4x7gse4.feishu.cn/docx/NACldN9xEoOEeqx6QEKcNIRjn0c?from=from_copylink)（<em>外部链接，感觉写的比较简单，可以直接阅读官方文档</em>）里边有我入门 pybind11 时做的一些笔记，可以理解为[官方文档](https://pybind11.readthedocs.io)的部分摘抄和学习
- 阅读 [pybind11 with cmake](https://pybind11.readthedocs.io/en/stable/compiling.html#cmake)，了解如何搭配 cmake 使用 pybind11
- 我们的项目使用 pybind11+cmake+scikit-build-core 构建，所以可以下载 [scikit-build-core template](https://github.com/pybind/scikit_build_example) 仓库，搞懂里边的代码，尝试跑一个 demo 出来

  - 有任何与 scikit-build-core 相关的问题可以查阅 [scikit-build-core 文档](https://scikit-build-core.readthedocs.io/)
- 阅读 [pyabacus README](https://github.com/deepmodeling/abacus-develop/blob/develop/python/pyabacus/README.md)，简单了解 pyabacus 目前的模块结构，尝试按照 README 编译 pyabacus 并跑通（可以运行 `python/pyabacus/examples` 内的 python 脚本）
- 阅读 [pyabacus How to contribute](https://github.com/deepmodeling/abacus-develop/blob/develop/python/pyabacus/CONTRIBUTING.md)，同步阅读 `pyabacus` 下各文件夹内 CMakeLists，理解它们之间的关系。本文档中给出了该部分的中文翻译，可对照查看。
- 同步地，可以看一下 `src/hsolver` 内的代码，其结构如下

  - `{method}.hpp` 为对应算法的头文件，头文件中将 `hsolver` 内对应算法进行了一定的包装，加入了 pybind 的一些头文件以方便调用
  - `py_hsolver.cpp` 为 pybind11 绑定，将三个方法对应的类绑定到 python
  - `../pyabacus/hsolver` 内的两个 `py` 文件将类的细节隐藏，用函数在外层抽象，将三个算法以函数的形式暴露给 python

了解了上面几点，你大概就了解了如何 Python 化 ABACUS 的一个模块，剩下需要搞懂的是

- 你要 Python 化的模块，按照面向对象的思想，你可以只搞懂对应模块的头文件中暴露出来的 public 方法的接口

  - 但是，如果想要优化/防止 python 化过度影响效率，最好要搞懂其原理
  - 作为高性能计算软件，我们时常与裸指针/底层数据打交道，但是我们处理的数据通常是矩阵 or 张量，所以一定要从源码中弄清楚数据的存储方式：行优先/列优先
    - 不要想当然，作为有着”历史积累“的软件，不同模块可能使用不用方式存储
    - 例如：`davidson` 算法与 `dav_subspace` 中的裸指针采用列优先方式，与 fortran 一致，while CG 算法中的 tensor 的底层数据是行优先方式，与 C++ 习惯及 NumPy 中一致
- 如何编写单元测试

  - 可以阅读 `tests` 文件夹内的代码，同时查阅 [pytest 文档](https://pytest.readthedocs.io/)
  - 提交 PR 前一定要做好单元测试，确保功能没有问题！
  - 看到一片绿色写着 PASS 时候是很有成就感的~

对上面问题有了基本的了解以后，我们就可以进行开发了！祝你在开发的过程中好运~

# 三、资料汇总

- [Pybind 简单教程](https://r0ya4x7gse4.feishu.cn/docx/NACldN9xEoOEeqx6QEKcNIRjn0c?from=from_copylink)
- [pybind11 with cmake](https://pybind11.readthedocs.io/en/stable/compiling.html#cmake)
- [scikit-build-core template](https://github.com/pybind/scikit_build_example)
- [scikit-build-core 文档](https://scikit-build-core.readthedocs.io/)
- [pyabacus README](https://github.com/deepmodeling/abacus-develop/blob/develop/python/pyabacus/README.md)
- [pyabacus How to contribute](https://github.com/deepmodeling/abacus-develop/blob/develop/python/pyabacus/CONTRIBUTING.md)
- [pytest 文档](https://pytest.readthedocs.io/)
- [寻找在 GitHub 上参与开源项目的方法](https://docs.github.com/zh/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github)
- [GitHub Issues 快速入门](https://docs.github.com/zh/issues/tracking-your-work-with-issues/configuring-issues/quickstart)
- [https://zhuanlan.zhihu.com/p/697280920](https://zhuanlan.zhihu.com/p/697280920)

# 四、结语

以上就是 Pyabacus 的一些基本安装和使用方法，如果读者对进一步交流感兴趣，欢迎登录 ABACUS 的 github 网站进行进一步的交流。
