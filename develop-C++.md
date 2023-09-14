# ABACUS 开源项目 C++ 代码规范

<strong>作者：韩昊知，邮箱：haozhi.han@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/09/04</strong>

ABACUS（Atomic-orbtial Based Ab-initio Computation at UStc，中文名原子算筹）是国产开源密度泛函理论软件，相关介绍 ABACUS 的新闻可在 [ABACUS 新闻稿整理](abacus-news.md)查看。此文档用于给 ABACUS 开发者提供代码编程规范方面的建议。

# 前言

> <strong>让任何开发者都可以快速读懂别人的代码，这点对于 ABACUS 项目很重要。此外，使代码易于管理的方法之一是加强代码一致性，这需要从代码规范开始着手。</strong>

# 一、命名约定

## 1. 普通变量的命名统一是小写，并使用下划线命名法

以下是四种命名方法：下划线命名法、匈牙利命名法、驼峰式命名法、帕斯卡命名法

```cpp
<strong>string table_name; </strong>// 下划线命名法（推荐） - 用下划线区分单词（推荐使用）
string sTableName; // 匈牙利命名法 - 前缀字母用变量类型缩写，单词首字母大写
string tableName;  // 驼峰命名法 - 混合大小写（不推荐使用）
string TableName; // 帕斯卡命名法 - 每个单词首字母大写（不推荐使用)
```

<strong>下划线命名法：</strong>推荐使用

<strong>匈牙利命名法：</strong>目前 ABACUS 中有些变量（例如指针），首字母为数据类型（指针为 p），可以考虑用这种方式命名，但不推荐用大写字母

<strong>驼峰命名法/帕斯卡命名法：</strong>目前 ABACUS 大部分的代码不是用这种命名方式的，为了代码风格统一，所以不推荐使用

## 2. 函数命名

建议使用下划线命名法且所有字母全部小写，建议小于 18 个字符

```cpp
void calculate_area() {
  // function body
}
```

## 3. `private` 的类数据成员在最后以下划线结尾

`private` 的类数据成员和普通变量的命名方式一样，但要在最后以下划线结尾，以区分自己是 `private` 的类数据成员。

```cpp
class TableInfo 
{
...
private:
    string table_name_;  // 好 - 后加下划线
    string tablename_;   // 好
    static Pool<TableInfo>* pool_;  // 好
};
```

## 4. 只有全局变量用全大写命名

在 ABACUS 中，例如 NBANDS（能带数），NLOCAL（局域轨道数目）这种全大写的变量名是全局变量，其它的不建议用大写字母给变量命名。另外，ABACUS 将通过重构或者删除的方式逐步淘汰全局变量，因此不建议增加新的全局变量。

# 二、关于头文件

## 1. 只有在真正需要使用某个库/头文件时才 `#include` 它们

不需要的 `#include` 删除。

## 2. <strong>#include</strong>避免使用快捷目录 `.` (当前目录) 或 `..` (上级目录)

项目内头文件应按照项目源代码目录的树结构排列，避免使用 UNIX 特殊的快捷目录 `.` (当前目录) 或 `..` (上级目录)。例如

`source/module_hsolver/diago_cg.h` 文件是这样引用 `module_base` 的头文件：

```cpp
#include "diagh.h"
#include "module_base/complexmatrix.h"
```

## 3. <strong>#include 顺序（clang-format 可以自动）</strong>

使用标准的头文件包含顺序，这样可以可增强可读性，避免隐藏依赖。

> `foo.cpp` 中包含头文件的次序如下：
>
> 1. 与源文件对应的头文件：`dir2/foo2.h`（这种优先的顺序排序保证当 `dir2/foo2.h` 遗漏某些必要的库时， `dir/foo.cpp` 的构建会立刻中止）
> 2. C 系统文件
> 3. C++ 系统文件
> 4. 其他库的 `.h` 文件
> 5. 本项目内 `.h` 文件

## 4. 头文件需要 <strong>#define 保护</strong>

```cpp
#ifndef FOO_BAR_BAZ_H_
#define FOO_BAR_BAZ_H_
...
#endif // FOO_BAR_BAZ_H_
```

## 5. 避免使用前置声明

使用 `#include` 包含需要的头文件，尽量避免使用前置声明（见以下例子解释什么是前置声明）。

```cpp
// 什么是前置声明？
// MyClassB.h

// Bad: Overuse of forward declarations
class MyClassB;

class MyClassA {
public:
    void DoSomething(MyClassB* obj_b);
};

void MyClassA::DoSomething(MyClassB* obj_b) {
    // ...
}
```

> 在这段代码中，`MyClassB` 被声明为一个类，但没有给出其定义。这被称为前置声明（Forward Declaration），它告诉编译器 `MyClassB` 是一个存在的类，但不提供该类的详细信息。

## 6. <strong>当函数只有 10 行甚至更少时，才将其定义为内联函数</strong>

只有当函数只有 10 行甚至更少时才将其定义为内联函数（关键字 `inline`）。

# 三、关于类（Class）

## 1. 先声明类的成员变量，<strong>再声类的成员函数</strong>

## 2. <strong>将public 部分放在最前，之后是protected数据，最后是private</strong>

## 3. <strong>不使用运算符重载</strong>

若要使用，建议提交 issue 讨论

## 4. <strong>什么时候用 struct？</strong>

只有数据成员、没有成员函数时可以用 `struct`

## 5. 类型转换<strong>使用static_cast<>()</strong>

建议使用 C++ 的类型转换，如 `static_cast<>()`。

不要使用 `int y = (int)x` 或 `int y = int(x)` 等转换方式。

> - 用 `static_cast` 替代 C 风格的值转换, 或某个类指针需要明确的向上转换为父类指针时。
> - 用 `const_cast` 去掉 `const` 限定符。
> - 用 `reinterpret_cast` 指针类型和整型或其它指针之间进行不安全的相互转换。 仅在你对所做一切了然于心时使用。

## 6. 继承采用 `public` 继承

如果你想使用私有继承，你应该替换成把基类的实例作为成员对象的方式去定义类。

## 7. 不过度使用实现继承，可以考虑组合

例如，如下案例：

```cpp
class Engine {
public:
    void start() { /* 启动引擎 */ }
};

class Car {
public:
    Car(const std::string& n, Engine& e) : name_(n), engine_(e) {}
    void drive() { engine_.start(); std::cout << name_ << " is driving\n"; }

private:
    std::string name_;
    Engine& engine_;
};

int main() {
    Engine engine;
    Car car("mycar", engine);
    car.drive();
    return 0;
}
```

# 四、关于函数（Function）

## 1. 函数传参：不变参数用 const 和 &

函数的输入参数与输出参数:

在一个函数中，不变的量，我们可以看作是函数的输入参数；变化的量，我们可以看作是函数的输出参数。

在输入参数中可以选择 `const T*` （指向常量对象的指针，不能通过这个指针来修改其指向的对象的值。然而，你可以改变指针本身的值）。

也可以使用 `const T&` （不能通过这个引用来修改其引用的对象的值，在其生命周期内不能重新引用另一个对象）。

> 所以，建议使用 `const T&`，若要使用 `const T*`，则应给出相应的理由，否则会使读者感到迷惑。

```cpp
void Foo(const string &in, string *out);
// 输入参数：in （const + 引用&）
// 输出参数：out（指针变量）
```

## 2. 函数传参：会变的参数用指针

什么是引用参数:

- 在 C 中, 如果函数需要修改输入变量的值, 参数必须为指针, 如 `int foo(int *pval)`。
- 在 C++ 中, 函数还可以声明为引用参数: `int foo(int &val)`。

> 引用参数在语法上是值变量却拥有指针的语义（变量可以被改变！）。

## 3. <strong>每个函数不超过 50 行</strong>

建议编写简短，凝练的函数，有特殊情况的除外。

## 4. 函数返回值（`return` 的值）多使用<strong>值返回</strong>和<strong>引用返回</strong>，避免使用<strong>指针返回</strong>

# 五、关于作用域

## 1. 变量要初始化

无初始化的变量可能会引起结果不稳定（例如出现随机数），因此建议养成习惯，对所有变量的值要初始化，见下面的例子：

```cpp
int i;
i = f(); // 坏——初始化和声明分离

int j = f(); // 好——初始化时声明
```

```cpp
vector<int> v;  // 坏——初始化和声明分离
v.push_back(1);
v.push_back(2);

vector<int> v = {1, 2}; // 好——初始化时声明
```

## 2. 将局部变量置于最小作用域

> 在 `if`, `while` 和 `for` 语句中：
>
> - 变量不是对象，则变量应当在内部声明与初始化，这样子这些变量的作用域就被限制在这些语句中了，举例而言：
>
>   ```cpp
>   while (const char* p = strchr(str, '/'))
>   {
>   str = p + 1;
>   }
>
>   ```
>
> - 如果变量是一个对象, 每次进入作用域都要调用其构造函数, 每次退出作用域都要调用其析构函数。这会导致效率降低。建议将构造函数调用次数减少以提高程序效率。
>
>   ```cpp
>   Foo f;  // 构造函数和析构函数只调用 1 次
>   for (int i = 0; i < 1000000; ++i) 
>   {
>       f.DoSomething(i);
>   }
>
>   // 低效的实现
>   for (int i = 0; i < 1000000; ++i) 
>   {
>       Foo f;  // 构造函数和析构函数分别调用 1000000 次!
>       f.DoSomething(i);
>   }
>   ```

## 3. <strong>仅在局部作用域使用</strong>`using namespace`

使用 `using namespace` 语句来引入命名空间中的所有名称可能会导致名称冲突。因此，建议在需要时使用它并<strong>仅在局部作用域内使用（例如只在调用的时候使用）</strong>。

```cpp
// 建议不在程序开头使用，而是在具体用到std库的函数内使用该语句
using namespace std;
```

## 4. 用全局函数要加命名空间

以下是两种建议的方式，或者用类，或者用 namespace

```cpp
// 类的静态成员函数
class MyMath {
public:
    static int add(int a, int b) {
        return a + b;
    }
    
    static int sub(int a, int b) {
        return a - b;
    }
};

// or
// 命名空间内的非成员函数
namespace my_math {
    int add(int a, int b) {
        return a + b;
    }
    
    int sub(int a, int b) {
        return a - b;
    }
}
```

## 5. 优先使用命名空间的非成员函数

能使用命名空间的非成员函数，就不用类的静态成员函数。

```cpp
// 使用命名空间内的非成员函数
namespace my_math {
    int add(int a, int b) {
        return a + b;
    }
    
    int sub(int a, int b) {
        return a - b;
    }
}

int main() {
    int x = 3, y = 5;
    int z = my_math::add(x, y); // 调用 my_math 命名空间中的函数
    return 0;
}
```

```cpp
// 不要使用类的静态成员函数模拟命名空间
class MyMath {
public:
    static int add(int a, int b) {
        return a + b;
    }
    
    static int sub(int a, int b) {
        return a - b;
    }
};

int main() {
    int x = 3, y = 5;
    int z = MyMath::add(x, y); // 调用 MyMath 静态方法
    return 0;
}
```

# 六、其他 C++ 特性

## 1. 每个<strong>代码文件不超过 500 行</strong>

太长的代码阅读理解和维护的成本都太高，因此不建议一个文件太长。如果有文件超过 500 行，建议重构，把对象进一步的划分。

## 2. 禁止<strong>用 C++11 之后版本的语法</strong>

目前的主要考虑是用新语法会使得编译器编译成功的概率降低，另外提高开发者的开发门槛。因此，我们规定不能使用 C++11 之后的语法。

## 3. 多用<strong>前置自增 (++i) </strong>

对于迭代器和其他模板对象使用前缀形式 (`++i`) 的自增，自减运算符。

不考虑返回值的话，前置自增 (`++i`) 通常要比后置自增 (`i++`) 效率更高。

## 4. <strong>尽可能用 sizeof(a) 代替 sizeof(int)</strong>

这里 `a` 是一个参数名

原因：当代码中变量类型改变时会自动更新。

## 5. 多使用<strong>列表初始化</strong>

C++11 中，该特性得到进一步的推广，任何对象类型都可以被列表初始化。示范如下：

```cpp
// Vector 接收了一个初始化列表。
// 不考虑细节上的微妙差别，大致上相同。
// 可以任选其一。
vector<string> v{"foo", "bar"};
vector<string> v = {"foo", "bar"};

// 可以配合 new 一起用。
auto p = new vector<string>{"foo", "bar"};

// map 接收了一些 pair, 列表初始化大显神威。
map<int, string> m = {{1, "one"}, {2, "2"}};

// 初始化列表也可以用在返回类型上的隐式转换。
vector<int> test_function() { return {1, 2, 3}; }

// 初始化列表可迭代。
for (int i : {-1, -2, -3}) {}

// 在函数调用里用列表初始化。
void TestFunction2(vector<int> v) {}
TestFunction2({1, 2, 3});
```

## 6. 初始化时：<strong>整数用0，实数用0.0，指针用nullptr，字符 (串) 用'\0'</strong>

C++11 引入了一个新的关键字 `nullptr`，用来表示空指针。相对于传统的 `NULL` 或 `0`，`nullptr` 更加明确、类型安全。使用 `nullptr` 可以避免一些潜在的编程错误，比如将整数值误传给函数，导致出现不可预期的行为。

因此，建议在 C++11 及以上的版本中使用 `nullptr` 来表示空指针。

## 7. 少用 `auto`，使用前需对 `auto` 有更全面的了解

`auto` 是 C++11 引入的关键字，它可以让编译器自动推导出变量的类型。之后，C++14 和 C++17 对 `auto` 的使用也有了一些扩展和改进。

- <strong>C++11</strong>：`auto` 只能用于定义<strong>局部变量</strong>，并且必须初始化。例如：

```cpp
auto i = 42; // 推导出 i 的类型为 int
auto f = 3.14f; // 推导出 f 的类型为 float
auto s = "hello"; // 推导出 s 的类型为 const char*
```

- <strong>C++14</strong>：`auto` 可以用于定义<strong>函数返回值类型</strong>，使得函数定义更加简洁。例如：

```cpp
auto add(int x, int y) { return x + y; } // 推导出返回类型为 int
auto divide(double x, double y) { return x / y; } // 推导出返回类型为 double
```

- <strong>C++17</strong>：`auto` 进一步扩展为 `auto` 和模板结合使用时，可以直接指定模板类型参数，从而实现更加灵活的类型推导。例如：

```cpp
std::vector<int> v{1, 2, 3};
auto it = v.begin(); // 推导出 it 的类型为 std::vector<int>::iterator
auto [first, second] = std::make_pair(1, 3.14); // 使用结构化绑定和 auto 推导出 first 和 second 的类型
```

> 但是大家注意，在 abacus 中，我们只支持 C++11 的标准，C++14/17 语法是不接受的。

## 8. <strong>auto 和 for 的混合使用时注意事项</strong>

在 C++11 中，`auto` 和 `for` 循环的结合使用已成为一种常见的编程范式，它可以让代码更加简洁、易读，并且减少了手动指定类型的错误。

```cpp
int arr[] = {1, 2, 3};

for (auto i : arr)  // 相当于复制
{
    std::cout << i << " "; 
}

for (const auto& i : arr) // 常量引用
{
    std::cout << i << " ";
}

for (auto& i : arr) // 能够实现对元素的直接修改。
{
    i *= 2;
}
```

## 9. <strong> constexpr 替代宏定义和 const 常量</strong>

在 C++11 里，用 constexpr 来定义真正的常量，或实现常量初始化。（真正的常量在编译时和运行时都不变）

```cpp
#define PI 3.14159 // PI 是一个宏定义常量，它不会进行类型检查，容易出错；
const double kE = 2.71828; // kE 是一个 const 常量，它不能用于编译期计算。

constexpr double kGravity = 9.8;
```

`constexpr` 可以替代宏定义和 `const` 常量的主要原因是：

- 类型安全：使用 `constexpr` 定义的常量会进行类型检查，避免了宏定义可能带来的类型错误，同时也比 `const` 常量更加严格。
- 编译时计算：`constexpr` 声明的变量或函数在编译时就可以被求值，而不需要在运行时计算。这比宏定义和 `const` 常量更高效，尤其是在需要多次使用同一个值的情况下。
- 更好的可读性和可维护性：使用 `constexpr` 可以使代码更加清晰易懂，减少了宏定义可能导致的代码混乱问题。同时，由于 `constexpr` 可以使用函数、类等 C++ 语言特性，因此更加灵活，对于复杂的计算也更容易维护和修改。

因此，在 C++11 及以上的版本中，建议使用 `constexpr` 来替代宏定义和 `const` 常量，以提高代码的可读性、可维护性和效率。

# 七、关于 ABACUS 中常用的关键词缩写

> 有些名字很长，我们希望尽量言简意赅的表达出一些关键词的意思。原则是一般 3-5 个字母的范围下尽量说清楚一个变量的含义。这些统一的命名会出现在函数名或者变量名里。

## 1. 两个字符

- `pw`：代表plane wave平面波
- `op`：代表具有multi-device和multi-precision支持的算子（operator），和Operator模块含义不同
  
## 2. 三个字符

- `fft`：快速傅里叶变换
- `kpt`：布里渊区kpoint的缩写
- `nao`：代表numerical atomic orbitals  （nao经常用来表示number of atomic orbitals，不知道会不会混）
- `orb`：orbital，轨道
- `hmt`：代表hamilt或者hamiltonian
- `pot`：代表potential
- `chg`：代表charge
- `den`：代表density（电荷密度尽量都用chg）
- `scf`：代表自洽迭代self consistent field
- `thr`：代表threshold
- `tab`：代表table
- `kin`：代表kinetic，动能的
- `cal`：代表calculate
- `opt`：代表optimize
- `gen`：代表generate

## 3. 四个字符

- `iter`：代表iteration
- `init`：代表初始化initializaiton
- `read`：读入
- `stru`：代表structure
- `veff`：代表有效势
- `vloc`：代表局域势

# Reference

[Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
