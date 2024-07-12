# ABACUS formatter-2.0 版本使用说明书

<strong>作者：黄一珂，邮箱：huangyk@aisi.ac.cn</strong>

<strong>最后更新时间：2024 年 7 月 12 日</strong>

# 前言

为系统解决 ABACUS 对输出可读内容到屏幕和文件中的需求，2023 第三季度 ABACUS 开发团队进行了 ABACUS formatter library 1.0 版本的开发。随着后期 ABACUS 各功能的输出需求对 formatter library 的功能要求越来越多样化，我们对 formatter library 代码进行了全面重构，推出了 formatter-2.0 版本。相较于 1.0 版本（[ABACUS formatter 库使用说明书](https://ucoyxk075n.feishu.cn/docx/Yym9dnm3aoTMfHxin8rcX9Rvnmb)），重构进行了大量冗余代码删减，如今已经轻量化成为只具有头文件、有明显“即插即用”性质的工具库。该工具库功能包括简单的字符串格式化、制表和部分 Python 字符串处理函数实现三部分。

# 字符串格式化

相较于 1.0 版本中只能对字符串加以 1)宽度、2)小数保留位数、3)正负号、4)左右对齐和 5)科学计数法的设定，2.0 版本基于 `std::snprintf` 函数（见 cppreference：[https://en.cppreference.com/w/cpp/io/c/fprintf](https://en.cppreference.com/w/cpp/io/c/fprintf)）实现了对 format string（例如 C++20 支持的 format library：[https://en.cppreference.com/w/cpp/utility/format/format](https://en.cppreference.com/w/cpp/utility/format/format)）的全面支持（如 %d, %o, %x, %u, %hd, %ld, %lu, %c, %s, %f, %e 等），弃置了基于 stream（iostream, ）的技术路线（见 [https://stackoverflow.com/questions/15106102/how-to-use-c-stdostream-with-printf-like-formatting](https://stackoverflow.com/questions/15106102/how-to-use-c-stdostream-with-printf-like-formatting)）。

另一方面，`std::cout` 是在 ABACUS 中最普遍出现，且经常被修改的全局变量。任何不刻意设置便输出的内容都将受到“上一次”对 `std::cout` 的 `IOManipulator` 的影响。

然而，使用新版的 formatter 需要注意数据类型，若数据类型出现不匹配，则很可能出现 undefined behavior（例如 issue [#4540](https://github.com/deepmodeling/abacus-develop/issues/4540) 中所报道），这一类型要求和 Python 自 3.12 版本开始功能健全且大范围流行和提倡的 f-string 一致。

## static format 函数的使用

实际上，由于 formatter library 的轻量化重构，从单元测试中就足以可以明白 formatter library 这一基础函数的使用方法。又因为该函数是类中 static 函数，因此可以随时避免创建类对象而直接使用该函数。基本的使用方法展示在下面：

```cpp
TEST(FormatterTest, FmtCoreStaticFormat) {
    // const char*
    std::string result = FmtCore::format("Hello, %s!", "world");
    // remove the last '\0' character
    EXPECT_EQ(result, "Hello, world!");
    // std::string
    result = FmtCore::format("Hello, %s!", std::string("world"));
    EXPECT_EQ(result, "Hello, world!");
    // int
    result = FmtCore::format("Hello, %d!", 123);
    EXPECT_EQ(result, "Hello, 123!");
    // float
    result = FmtCore::format("Hello, %f!", 123.456);
    EXPECT_EQ(result, "Hello, 123.456000!");
    // char
    result = FmtCore::format("Hello, %c!", 'a');
    EXPECT_EQ(result, "Hello, a!");
    // invalid format
    result = FmtCore::format("Hello, %z!", "world");
    EXPECT_EQ(result, "Hello, %!");
    // varadic template case
    result = FmtCore::format("Hello, %s, %d, %f, %c!", "world", 123, 123.456, 'a');
    EXPECT_EQ(result, "Hello, world, 123, 123.456000, a!");
}
```

下面我们对 ABACUS 中常用于输出的数据类型进行详细举例。

### int 类型输出：%d

```cpp
#include "module_base/formatter.h"
#include <iostream>

std::cout << FmtCore::format("%d", 1);

//output: "1"
```

如果想要修改其宽度，则需要在 `d` 之前设定数字，如设置宽度为 4：

```cpp
std::cout << FmtCore::format("%4d", 1);
//output: "   1"
```

如果需要输出左对齐而非右对齐的字符串，则在百分号 `%` 之后添加负号：

```cpp
std::cout << FmtCore::format("%-5d", 10);
// output: "10   "
```

### float/double 类型输出：%f 和 %e

对于浮点型数据，最重要的是其是否使用科学计数法、保留位数和宽度各如何。请认真观察如下示例：

```cpp
const double rough_pi = 3.1415926535897932384;
std::cout << FmtCore::format("%8f", rough_pi);
// output: "3.141592"
std::cout << FmtCore::format("%8.4f", rough_pi);
// output: "  3.1415"
std::cout << FmtCore::format("%.4f", rough_pi);
// output: "3.1415"
std::cout << FmtCore::format("%.0f", rough_pi);
// output: "3"
```

不难发现如果 f（或者 e）前面只有一个数字，该数字默认为最小宽度。如果在数字前有小数点，则该数字意为保留小数位数，因此 `%.0f` 将直接对数字取整。

对于需要使用科学计数法的场景，只需要将 `f` 替换成 `e` 即可。需要注意的是科学计数法中诸如 `e+00` 也需要占位 4 个长度，需要在规定字符串输出长度时加以考虑。

### std::string 类型输出：%s

对于字符串的输出最简单，另外一个具有相似功能的占位符为 %c，意为为 char 类型在格式化字符串（format string）中占位。

```cpp
std::cout << FmtCore::format("Hello, %s!\n", "world");
// output: "Hello, world!"
```

## dynamic format 函数的使用

为应对大批量、重复使用同一 format string 的需求，可以首先建立一个 FmtCore 对象，之后调用对象中的成员函数 `format` 时，就不需要再每次输入 format string：

```cpp
FmtCore fmt("Hello, %s!\n");
std::cout << fmt.format("world") << std::flush;
std::cout << fmt.format("again") << std::flush;
// output:
// "Hello, world!
//  Hello, again!"
```

因此在功能角度和 static 函数中的 format 基本无异。单元测试可以辅助理解：

```cpp
TEST(FormatterTest, FmtCoreDynamic)
{
    FmtCore fmt("Hello, %s!");
    EXPECT_EQ(fmt.fmt(), "Hello, %s!");
    std::string result = fmt.format(std::string("world"));
    EXPECT_EQ(result, "Hello, world!");

    fmt.reset("Hello, %d!");
    EXPECT_EQ(fmt.fmt(), "Hello, %d!");
    result = fmt.format(123);
    EXPECT_EQ(result, "Hello, 123!");

    fmt.reset("Hello, %f!");
    EXPECT_EQ(fmt.fmt(), "Hello, %f!");
    result = fmt.format(123.456);
    EXPECT_EQ(result, "Hello, 123.456000!");

    fmt.reset("Hello, %c!");
    EXPECT_EQ(fmt.fmt(), "Hello, %c!");
    result = fmt.format('a');
    EXPECT_EQ(result, "Hello, a!");

    // varadic template case
    fmt.reset("Hello, %s, %d, %f, %c!");
    EXPECT_EQ(fmt.fmt(), "Hello, %s, %d, %f, %c!");
    result = fmt.format(std::string("world"), 123, 123.456, 'a');
    EXPECT_EQ(result, "Hello, world, 123, 123.456000, a!");
}
```

# 制表功能

formatter-1.0 的另一项亮眼功能为自动制表，在 formatter-2.0 版本中这一 feature 得以保留，并由 1.0 版本的 Table 类重构成为更加轻量级的 FmtTable 类，用于提供想要制作排列整齐的数据表，又不太清楚表格的列宽的场景。

由于 FmtTable 类的设计初衷为”每一个 FmtTable instance“代表了一个 Table，因此在 Table 中设计需要用户提供如下信息：

- 每列标题，组织成 std::vector[std::string](std::string)
- 每列 format string，组织成 std::vector[std::string](std::string)
- 每列数据
- （可选）表中数据与表标题的左右对称
- （可选）表格的各个边框
- （可选）表格中每列的分隔符

## 形参表一览

```cpp
/**
     * @brief Construct a new Fmt Table object
     * 
     * @param titles titles, its size should be the same as the number of columns
     * @param nrows number of rows
     * @param aligns Alignments instance, can be constructed with initializer_list<char> like {'r', 'c'}, for right and center alignment for values and titles
     * @param frames Frames instance, can be constructed with initializer_list<char> like {'-', '-', '-', ' ', ' '}, for up, middle, down, left and right frames
     * @param delimiters Delimiters instance, can be constructed with initializer_list<char> like {'-', ' '}, for horizontal and vertical delimiters
     */
    FmtTable(const std::vector<std::string>& titles, 
             const size_t& nrows, 
             const std::vector<std::string>& fmts,
             const Alignments& aligns = {},
             const Frames& frames = {},
             const Delimiters& delimiters = {}): titles_(titles), fmts_(fmts), data_(nrows, titles.size()), aligns_(aligns), frames_(frames), delimiters_(delimiters)
    { assert(titles.size() == fmts.size()); };
```

基于 RAII 原则，我们假设需要制表并进行输出的数据经常是已经全部准备好的状态，而非如同 SCF 的迭代信息一样，需要特别估算每列的大致宽度信息。

因此在 FmtTable 构造函数中，我们一定需要 titles, n_rows, fmts，并对 align 和 Delimiter 参数设置了默认值因此并非总是需要。如果想要特殊配置，则可以选择单元测试中例子 [https://github.com/deepmodeling/abacus-develop/blob/develop/source/module_base/test/formatter_test.cpp#L323](https://github.com/deepmodeling/abacus-develop/blob/develop/source/module_base/test/formatter_test.cpp#L323)，仿照其进行制表调整。

## 使用代码示例

除了单元测试（[https://github.com/deepmodeling/abacus-develop/blob/develop/source/module_base/test/formatter_test.cpp](https://github.com/deepmodeling/abacus-develop/blob/develop/source/module_base/test/formatter_test.cpp)）外，目前 FmtTable 也已经用于 ABACUS 运行时间统计的输出（[https://github.com/deepmodeling/abacus-develop/blob/develop/source/module_base/timer.cpp#L280](https://github.com/deepmodeling/abacus-develop/blob/develop/source/module_base/timer.cpp#L280)），但可进一步实现对表中数据区域的每列左右对齐控制。

# static Python-style 字符串函数

## 函数功能简介

C/C++ 的文件读入功能也较为繁琐，尤其涉及需要进行字符串操作时，Python 中 str 的函数则更胜一筹。为了避免每次手动 parse 字符串，又注意到 std::string 同样是 STL 的标准容器，因此对标准容器支持的算法，也都能支持 std::string。目前出于个人使用习惯，实现了下列 Python-style static 函数：

- split：用于以固定分隔符切割字符串，返回 std::vector[std::string](std::string)，但也是因为该返回类型，注定 split 函数不会收录在 STL 中
- startswith/endswith：返回 boolean，用于判断字符串是否以给定字符串开始，或者以给定字符串结束。
- strip：用于消除出现在字符串行头行尾的空格、回车和\0 等字符，返回 std::string。
- center：为了支持下一步的 ABACUS 输出重构，首先实现 center 函数用于将字符串以某一个宽度居中，两段则填充以 center 函数第一个参数，使得 ABACUS 中所有内容都可以具有给定宽度的输出（即两端对齐）
- replace：用于消除字符串中存在的所有某个字符
- join：split 的反函数

## 代码示例

以上函数的例子可见单元测试：[https://github.com/deepmodeling/abacus-develop/blob/develop/source/module_base/test/formatter_test.cpp](https://github.com/deepmodeling/abacus-develop/blob/develop/source/module_base/test/formatter_test.cpp)

# Find a bug? Submit issue!

如果在使用 formatter 过程中发现了 bug 或者运行结果不达预期，可以在 deepmodeling/abacus-develop 仓库下提交 issue。
