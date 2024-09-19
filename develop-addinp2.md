# 如何在 ABACUS 中新增一个输入参数（v3.7.0 后）

<strong>作者：刘千锐，邮箱：terry_liu@pku.edu.cn</strong>

<strong>单位：北京大学</strong>

<strong>最后更新日期：2024/7/10</strong>

<strong>如果遇到本文档无法解决的问题，欢迎给 ABACUS 提出 Issues，我们将持续更新这个文档</strong>

# <strong>开发者须知</strong>

## 1.1 声明参数并给出初始值

路径 <u>module_parameter/input_parameter.h</u>

首先现在<u>input_parameter.h</u>中添加相关输入参数的定义，如 `nelec_delta`：

```cpp
bool init_vel = false;          ///< read velocity from STRU or not  liuyu 2021-07-14
double symmetry_prec = 1.0e-6;  ///< LiuXh add 2021-08-12, accuracy for symmetry
bool symmetry_autoclose = true; ///< whether to close symmetry automatically
                                ///< when error occurs in symmetry analysis
double nelec = 0.0;             ///< total number of electrons
double nelec_delta = 0.0;       ///< change in the number of total electrons
```

在声明的同时给出默认值，如 nelec 默认为 0.0。

<u>注：对于任何类成员变量的 double, int, bool 等一般类型变量，在定义时就建议给一个初始值。如果类成员没有初始值，很可能会有难以察觉的 bug</u>

<u>注：string类型变量的初始值不能为"", 如果想自动设置，可以设置初始值为"auto", "none"等。</u>

## 1.2 在参数列表中添加参数

路径 <u>module\_io/read\_input\_item\_\*.cpp </u>（不同的参数分好了类，其对应不同文件，需要加到属于的文件里面），如 nelec 就在<u>read_input_item_general.cpp</u>中

添加 nelec 参数的 item

```cpp
Input_Item item("nelec");
```

之后依次添加：<strong>（*为必填）</strong>

注释（<strong>annotation*</strong>）：该注释会被打印在 OUT.*文件夹的 INPUT 中

```cpp
item.annotation = "input number of electrons";
```

读入函数（<strong>read_value*</strong>）：如何通过读入的 vector<string> str_value 转化成想要的 parameter 参数，<u>该函数只有在 INPUT 有相应参数的名字时才会执行。</u>

```cpp
item.read_value = [](const Input_Item& item, Parameter& para) {
            para.input.nelec = std::stoi(item.str_values[0]); 
        };
```

重新赋值函数（<strong>reset_value</strong>）：如果其他某些参数满足特定条件是，需要对当前参数（nelec）进行修改的函数，该函数一定会执行。<u>书写规范要求：只把修改当前参数的函数部分定义在当前参数的 reset_value，如果要修改其他参数，请定义在其他参数的 reset_value 。</u>

```cpp
item.reset_value = [](const Input_Item& item, Parameter& para) {
            if(para.input.somecondition)
            {
                para.input.nelec = 0.0;
            }
        };
```

检验函数（<strong>check_value</strong>）：用于检查目前参数是否合适，如果不合适就报错退出（warning_quit），该函数一定会执行。

```cpp
item.check_value = [](const Input_Item& item, const Parameter& para) {
            if(para.input.nelec < 0)
            {
                ModuleBase::WARNING_QUIT("ReadInput", "nelec should be no less than 0.0");
            }
```

获取最终打印值函数（<strong>get_final_value*</strong>）：用于给 stringstream final_value 赋值，最终 final_value.str()会被打印在 OUT.*的 INPUT 文件中，该函数一定会执行。

```cpp
item.get_final_value = [](Input_Item& item, const Parameter& para) {
            item.final_value << para.input.nelec;
        };
```

以及如果是并行版，需要添加广播函数（<strong>bcastfuncs*</strong>）：如何调用 Parallel_Common 进行 bcast 的函数，该函数一定会执行。<u>该函数不一定只传输该参数，还可以传输其他引入的非 INPUT 参数</u>，例如 gamma_only_local 这个变量不是 INPUT 参数，但是其由 gamma_only 和 basis_type 共同决定取值，这种额外引入的参数也需要在 gamma_only 或 basis_type 处添加他的 bcast 函数。

```cpp
#ifdef __MPI
        bcastfuncs.push_back([](Parameter& para) {
            Parallel_Common::bcast_bool(para.input.nelec); 
        });
#endif
```

最后将 item 添加到参数列表中：

```cpp
this->add_item(item);
```

### 总结：

```cpp
{
        Input_Item item("nelec");
        item.annotation = "input number of electrons";
        item.read_value = [](const Input_Item& item, Parameter& para) {
            para.input.nelec = std::stoi(item.str_values[0]); 
        };
        item.reset_value = [](const Input_Item& item, Parameter& para) {
            if(para.input.somecondition)
            {
                para.input.nelec = 0.0;
            }
        }; 
        item.check_value = [](const Input_Item& item, const Parameter& para) {
            if(para.input.nelec < 0)
            {
                ModuleBase::WARNING_QUIT("ReadInput", "nelec should be no less than 0.0");
            }
        };
        item.get_final_value = [](Input_Item& item, const Parameter& para) {
            item.final_value << para.input.nelec;
        };  
#ifdef __MPI
        bcastfuncs.push_back([](Parameter& para) {
            Parallel_Common::bcast_bool(para.input.nelec); 
        });
#endif
        this->add_item(item);
    }
```

以上是完整的参数添加实例，可以根据需要自己修改函数，然而实际上大部分参数的 bcastfuncs、get_final_value、read_value 函数填写是几乎一致的，他们有共同的形式，为了书写方便，可以利用 module_io/read_input_tool.h 定义的宏函数来进行书写的简化：

1\. 对于形如

```cpp
bcastfuncs.push_back([](Parameter& para) {
            Parallel_Common::bcast_bool(para.input.nelec); 
        });
```

的 bcastfuncs 函数书写可以分别使用 add_double_bcast, add_int_bcast, add_bool_bcast, add_string_bcast, add_doublevec_bcast, add_intvec_bcast, add_stringvec_bcast 函数进行代替

2\. 对于形如

```cpp
item.get_final_value = [](Input_Item& item, const Parameter& para) {
            item.final_value << para.input.nelec;
        };  
        bcastfuncs.push_back([](Parameter& para) {
            Parallel_Common::bcast_bool(para.input.PARAMETER); 
        });
```

的 get_final_value 与 bcastfuncs 函数的合并书写可以使用 sync_double, sync_int, sync_bool, sync_string, sync_doublevec, sync_intvec, sync_stringvec 函数进行代替

3\. 对于形如

```cpp
item.read_value = [](const Input_Item& item, Parameter& para) {
            para.input.nelec = std::stoi(item.str_values[0]); 
        };
        item.get_final_value = [](Input_Item& item, const Parameter& para) {
            item.final_value << para.input.nelec;
        };
        bcastfuncs.push_back([](Parameter& para) {
            Parallel_Common::bcast_bool(para.input.nelec); 
        });
```

的 read_value, get_final_value 与 bcastfuncs 函数的合并书写可以使用 read_sync_double, read_sync_string, read_sync_int, read_sync_bool 函数进行代替

因此添加 nelec 的代码可以简化成：

```cpp
{
        Input_Item item("nelec");
        item.annotation = "input number of electrons";
        read_sync_double(nelec);
        item.reset_value = [](const Input_Item& item, Parameter& para) {
            if(para.input.somecondition)
            {
                para.input.nelec = 0.0;
            }
        }; 
        item.check_value = [](const Input_Item& item, const Parameter& para) {
            if(para.input.nelec < 0)
            {
                ModuleBase::WARNING_QUIT("ReadInput", "nelec should be no less than 0.0");
            }
        };
        this->add_item(item);
```

## 1.2 参数的使用

<strong>目前已经舍弃使用 INPUT 与 GloablV::，请勿在里面添加新变量！</strong>

需要用到参数的地方，请以只读的方式使用

```cpp
int nbands = PARAM.inp.nbands; //只读的访问元素
```

而其不能作为修改的对象，这时编译不能通过：

```cpp
PARAM.inp.nbands = 0； //会报错
```

## 1.3 添加测试

### A. 读入测试

路径：<u>source/module_io/test/read_input_pteset.cpp</u>

```
       <u>source/module_io/test/support/INPUT</u>
```

在 INPUT 中添加这一参数：

```cpp
nelec                  10 #input number of electrons
```

在 `TEST_F(InputParaTest, ParaRead)` 测试这一读入是否正确，例如：

```
EXPECT_EQ(PARAM.inp.nelec, 10);
```

### B. 特殊场景的 reset_value 和 check_value 测试

路径：<u>source/module_io/test/read_input_item_test.cpp</u>

在 `TEST_F(InputTest, Item_test)` 添加特定参数的 reset_value 函数和 check_value 的覆盖性测试。

## 1.4 添加文档

路径：<u>docs/advanced/input_files/input-main.md</u>

每个新参数的 PR<strong>必须</strong>包含相应的文档，否则不会被接收。请在 `input-main.md` 中添加参数描述。

# 设计文档参考

参考：林霈泽博士提的方案 [github.com](https://github.com/PeizeLin/abacus-develop/tree/3dc78534f7fedd89d00bd4fedbf3836d7fa54ce6)

## 2.1 背景

v3.7.0 之前添加参考[如何在 ABACUS 中新增一个输入参数（截至 v3.5.3）](https://mcresearch.github.io/abacus-user-guide/develop-addinp.html)

### 2.1.1 原 input.cpp

当添加一个新的 INPUT 参数，我们需在 input 类里做以下事情：

A. 首先在 Default 函数中给初始值；

B. 再在 read 函数中的 if 中加一个判断分支：

```cpp
if (strcmp("suffix", word) == 0) // out dir
{
     read_value(ifs, suffix);
}
```

C. 再在 Bcast 函数中添加 bcast

D. （大部分）在 GlobalV 定义一个相同功能的变量，并给个初始值（实际上这个初始值没有任何用，还容易让人误解到底这个和 input.cpp 哪个是初始值）

E. 再在 input_conv.cpp 中转化成 GlobalV 的变量

F. 再在 write_input.cpp 添加一行代码使其可以输出到 OUT.ABACUS 文件夹中 INPUT

> 痛点：
>
> 1. 每加一个参数，对于 ABACUS 主代码需“翻山越岭”地添加代码，不易管理
> 2. input.cpp 的变量和 GlobalV 的变量大部分重复，没有必要，且容易误解
> 3. 大量的 if 分支
>    改进思路：
> 4. 将相同的参数代码集中起来
> 5. input 类只实现读的功能，不存储参数，参数由另一个类存储

### 2.1.2 GlobalV

其实代码有全局变量不可怕，可怕的是全局变量会在运行中改变，而部分 GlobalV 就是这样，因此需要限制他人在初始化参数之后改变的行为。

<em>目前很多也使用了 public 的类静态成员变量，这其实和全局变量是一样的。</em>

## 2.2 重构设计

### 2.2.1 Parameter 类

该类只存储 ABACUS 运行的参数，将代替 GlobalV 的功能，该类将成员设成私有变量，只给 ReadInput 类修改的权限，其他类只有访值权限，没有修改权限：

```cpp
class Parameter
{
  public:
    Parameter(){};
    ~Parameter(){};
  public:
    // We can only read the value of input, but cannot modify it.
    const Input_para& inp = input;
    // We can only read the value of mdp, but cannot modify it.
    const MD_para& mdp = input.mdp;
    // We can only read the value of other parameters, but cannot modify it.
    const System_para& globalv = system;

    // Set the rank & nproc
    void set_rank_nproc(const int& myrank, const int& nproc);
    // Set the start time
    void set_start_time(const std::time_t& start_time);

  private:
    // Only ReadInput can modify the value of Parameter.
    friend class ModuleIO::ReadInput;
    // INPUT parameters
    Input_para input;
    // System parameters
    System_para system;
};
```

## 2.2 Input_Item 类

用于存储 input 参数的信息，每一个参数用 input_item 的一个对象存储，不同 input_item 用 vector 打包。

```cpp
class Input_Item
{
  public:
    Input_Item(const std::string& label_in)
    {
        label = label_in;
    }

    std::string label;                   ///< label of the input item
    std::vector<std::string> str_values; ///< string values of the input item
    std::stringstream final_value;       ///< final value for writing to output INPUT file
    std::string annotation; ///< annotation of the input item

    // ====== !!! These functions are complete.        ======
    // ====== !!! Do not add any more functions here.  ======
    /// read value if INPUT file has this item
    std::function<void(const Input_Item&, Parameter&)> read_value = [](const Input_Item& item, Parameter& param) {};
    /// check value 
    std::function<void(const Input_Item&, const Parameter&)> check_value = nullptr;
    /// reset some values
    std::function<void(const Input_Item&, Parameter&)> reset_value = nullptr;
    /// get final_value function for output INPUT file
    std::function<void(Input_Item&, const Parameter&)> get_final_value = nullptr;
    // ====== !!! Do not add any more functions here.  ======
};
```

四个存储的变量：

<strong>label</strong>: 参数的名字

<strong>annotation</strong>: 参数的注释，用于生成 INPUT 的注释

<strong>str_values</strong>: 读入的 raw 数据，一个参数可以有多个数据，因此用 vector 存储，例如：kspacing 3 3 3

<strong>final_value</strong>: 最终的取值，用于生成 INPUT

四个 std::function 成员：

<strong>read_value</strong>（必填）: 当从 INPUT 读入参数后，需要进行的赋值操作

<strong>reset_value</strong>（选填）: 根据其读入的值，可能会修改其他参数的值时填入，例如 calculation 默认是 scf，当你读入 calculation 是 nscf 后，则需要将 init_chg 改成 file

<strong>check_value</strong>（选填）：根据其读入的值进行判断参数是否合适，例如：读入 ecut 为-100，则需要 warning_quit()

<strong>get_final_value</strong>（大部分必填）：此函数一定会执行（无论是否从 INPUT 读入这个参数），需要在此函数中给出 final_value 的赋值函数，这样用于打印 INPUT 文件

## 2.2 ReadInput 类

此类只负责读入 INPUT 文件，并赋值给 Parameter 类的对象，此类不负责存储参数

```cpp
class ReadInput
{
 public:
     /**
     * @brief read in parameters from input file
     *
     * @param param parameters of ABACUS
     * @param filename_in read INPUT file name
     */
    void read_parameters(Parameter& param, const std::string& filename_in);
    
    /**
     * @brief write out parameters to output file
     *
     * @param param parameters of ABACUS
     * @param filename_out write output file name
     */
    void write_parameters(const Parameter& param, const std::string& filename_out);
  private:
    std::vector<std::pair<std::string, Input_Item>> input_lists;
    //----These functions are done only when INPUT file has them.------
    // read value if INPUT file has this item
    std::vector<Input_Item*> readvalue_items;

    /// bcast all values function
    /// if no MPI, this function will resize the vector
    std::vector<std::function<void(Parameter&)>> bcastfuncs;
```

主要两个 public 函数：

<strong>read_parameters</strong>： 读入 INPUT 文件，赋值给 param

<strong>write_parameters</strong>： 打印 INPUT 文件

3 个 vector:

<strong>input_lists</strong>: 用于存储所有的 Input_Item，用于遍历调用<strong> resetvalue, getfinalvalue</strong>

<strong>readvalue_items</strong>: 用于存储读入 INPUT 中相应 Input_Item 指针，并进行读入赋值操作

<strong>bcastfuncs</strong>: 用于所有参数的 bcast

原则上<strong>bcastfuncs</strong>也可以用 vector<Input_Item*> 存储，一方面由于其不依赖 Input_Item，并且可能会 bcast 非 input 列表参数，另一方面但为了访存效率，用 vector<functional>存储更好

### 2.2.1 read_parameters 函数

对于 ReadInput 的 read_parameter，其执行的顺序是:

先确定 INPUT 对应哪些 Input_Item，然后将 INPUT 中读入的信息存入 item 的 str_values 中，之后依次执行

1. <strong>readvalue_items</strong>
2. <strong>inputlist->resetvalue</strong>
3. i<strong>nputlist->checkvalue</strong>
4. <strong>bcastfuncs</strong>

### 2.2.2 write_parameters 函数

如果要打印 INPUT，顺序执行 input_lists 的<strong>getfinalvalue</strong>

然后

```cpp
for (auto& item: this->input_lists)
{
   Input_Item* p_item = &(item.second);
   if (p_item->getfinalvalue == nullptr)
            continue;
   p_item->getfinalvalue(*p_item, param);
   ModuleBase::GlobalFunc::OUTP(ofs, p_item->label, p_item->final_value.str(), p_item->annotation);
}
```
