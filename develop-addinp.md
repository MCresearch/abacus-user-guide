# 如何在 ABACUS 中新增一个输入参数（截至 v3.5.3）

<strong>作者：周巍青，邮箱：</strong><strong>zhouwq@aisi.ac.cn</strong>

<strong>单位：北京科学智能研究院（AISI）</strong>

<strong>最后更新日期：2024/2/29</strong>

<strong>如果遇到本文档无法解决的问题，欢迎给 ABACUS 提出 Issues，我们将持续更新这个文档</strong>

# 在 input 类中申明和定义

## 1.1 声明

路径：<u>source/module_io/input.h</u>

首先现在<u>input.h</u>中添加相关输入参数的定义，如 `nelec_delta`：

```cpp
    //==========================================================
    // electrons / spin
    //==========================================================
    std::string dft_functional; // input DFT functional.
    double xc_temperature; // only relevant if finite temperature functional is used
    int nspin; // LDA ; LSDA ; non-linear spin
    double nupdown = 0.0;
    double nelec; // total number of electrons
    double nelec_delta; // change in the total number of electrons
    int lmaxmax;
```

## 1.2 设置初始值

路径：<u>source/module_io/input.cpp</u>

接下来你需要在 `Input::Default(void)` 和 `Input::Default_2(void)` 函数里对参数进行初始化，其中：

`Input::Default(void)`——定义单个变量的初始值

`Input::Default_2(void)`——根据部分参数的值，对一些有关联的参数重新赋值，如 `nelec_delta`：

```cpp
    //----------------------------------------------------------
    // electrons / spin
    //----------------------------------------------------------
    dft_functional = "default";
    xc_temperature = 0.0;
    nspin = 1;
    nelec = 0.0;
    nelec_delta = 0.0;
    lmaxmax = 2;
```

## 1.3 读取

路径：<u>source/module_io/input.cpp</u>

在 `Input::Read()` 中定义从 INPUT 文件中读取相应的参数，例如：

```cpp
        else if (strcmp("nelec_delta", word) == 0)
        {
            read_value(ifs, nelec_delta);
        }
```

## 1.4 MPI 广播

路径：<u>source/module_io/input.cpp</u>

读取完之后，需要定义如何在 `Input::Bcast()` 将读取的参数广播到所有的节点，原因是 ABACUS 程序从一个进程读入参数，之后通过 MPI 的 Bcast 函数广播到其它的进程。例如：

```cpp
    Parallel_Common::bcast_double(nelec_delta);
```

注意这里你需要根据参数的类型，使用不同的语句：

```cpp
    Parallel_Common::bcast_bool(out_wannier_wvfn_formatted);
    Parallel_Common::bcast_string(dft_functional);
    Parallel_Common::bcast_double(xc_temperature);
    Parallel_Common::bcast_int(nspin);
```

## 1.5 输出

路径：<u>source/module_io/write_input.cpp</u>

ABACUS 会在 `Input::Print(const std::string &fn)` 中做参数的输出，你也需要在这个函数中进行添加：

```cpp
ModuleBase::GlobalFunc::OUTP(ofs, "nelec_delta", nelec_delta, "change in number of total electrons");
```

## 1.6 添加测试

路径：

<u>source/module_io/test/input_test_para.cpp</u>

<u>source/module_io/test/write_input_test.cpp</u>

### 1.6.1 参数默认值和 MPI 广播的测试

`TEST_F(InputParaTest, Bcast)` 既测试了初始值的设定，也同样测试了 Bcast 的有效性，你也要将新增参数加入：

```cpp
EXPECT_DOUBLE_EQ(INPUT.nelec_delta, 0.0);
```

这里同样需要考虑不同的数据类型：

```cpp
EXPECT_TRUE(INPUT.out_wannier_mmn);
EXPECT_FALSE(INPUT.out_wannier_unk);
EXPECT_DOUBLE_EQ(INPUT.nelec, 0.0);
EXPECT_EQ(INPUT.basis_type, "pw");
```

### 1.6.2 参数输出的测试

`TEST_F(write_input, General1)` 测试了 ABACUS 参数输出的正确性，例如：

```cpp
EXPECT_THAT(output, testing::HasSubstr("nelec                          0 #input number of electrons"));
```

这里一定要注意空格和对齐。

# 将 input 成员转换为全局变量

参数参与计算一般会先转换为全局变量 GlobalV，再通过传参赋值给负责计算的类（但是注意将来我们会逐步弃用 GlobalV，所以这部分将来可能会变化）。

## 2.1 声明

路径：<u>source/module_base/global_variable.h</u>

在 GlobalV 这个命名空间中申明新增的参数，例如：

```cpp
extern double nelec_delta;
```

## 2.2 设置初始值

路径：<u>source/module_base/global_variable.cpp</u>

为 GlobalV::var 设置初始值，例如：

```cpp
double nelec_delta = 0;
```

## 2.3 利用 Input 类的成员为 GlobalV 中成员赋值

路径：<u>source/module_io/input_conv.cpp</u>

在 `Input_Conv::Convert(void)` 中为 Global 的参数赋值，例如：

```cpp
GlobalV::nelec = INPUT.nelec;
```

- 注意：Input类一个全局类，只要调用了头文件即可使用。

## 2.4 添加测试

路径：<u>source/module_io/test/input_conv_test.cpp</u>

在 `TEST_F(InputConvTest, Conv)` 测试这一转换是否正确，例如：

```cpp
EXPECT_EQ(GlobalV::nelec_delta,0);
```

# 添加文档

路径：<u>docs/advanced/input_files/input-main.md</u>

每个新参数的 PR<strong>必须</strong>包含相应的文档，否则不会被接收。请在 `input-main.md` 中添加参数描述。
