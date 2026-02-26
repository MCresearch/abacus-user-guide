# 如何在 ABACUS 中新增一个输入参数（v3.9.24 后）

**作者：朱博南，邮箱：bzhu@bit.edu.cn 单位：北京理工大学**

**审阅：陈默涵，邮箱：mohanchen@pku.eud.cn，单位：北京大学**

**最后更新日期：2026/02/24**

如果遇到本文档无法解决的问题，欢迎给 ABACUS 提出 Issues（[https://github.com/deepmodeling/abacus-develop/issues](https://github.com/deepmodeling/abacus-develop/issues)），我们将持续更新此文档

本文档是对原教程 (<u>[https://mcresearch.github.io/abacus-user-guide/develop-addinp2.html](https://mcresearch.github.io/abacus-user-guide/develop-addinp2.html)</u>)的补充，重点介绍 v3.9.24 之后的**新变更**：

1. 参数注册时需要在 `.cpp` 中填写文档元数据字段（`category`, `type`, `description` 等）
2. ABACUS 内置帮助功能：`abacus -h <参数名>` 查询参数说明，`abacus -s <关键词>` 搜索参数
3. 如何通过 `abacus --generate-parameters-yaml` 生成 `docs/parameters.yaml`
4. 如何通过 Python 脚本从 YAML 自动生成 `input-main.md` 文档

关于参数声明（`input_parameter.h`）、读入函数（`read_value`）、检验函数（`check_value`）、宏函数简化（`read_sync_*`）等基础知识，请参阅[原教程](https://mcresearch.github.io/abacus-user-guide/develop-addinp2.html)。

---

# 1. 新增的文档元数据字段

## 1.1 背景与动机

ABACUS 的 v3.9.23 之前，源程序里 `/source/source_io/module_parameter/input_item.h` 定义的 `Input_Item` 只有一个 `annotation` 字段用于简短注释。参数的详细文档需要开发者**手动**维护在 `docs/advanced/input_files/input-main.md` 中，导致代码和文档容易脱节。同时，用户想了解某个 INPUT 参数的含义时，只能去查阅在线文档，没有离线快速查询的手段。

v3.9.23 之后，`Input_Item` 新增了** 6 个文档字段**，使得每个参数的完整文档直接写在 C++ 源代码中。这一改动有两个核心目的：

**目的一：内置帮助功能**

用户无需查阅在线文档，直接通过命令行即可获取参数说明：

```bash
# 查看某个参数的详细帮助
abacus -h ecutwfc

# 按关键词搜索参数
abacus -s relax
```

示例输出（`abacus -h ecutwfc`）：

```
Parameter: ecutwfc
Type:      Real
Default:   50 for PW basis, 100 for LCAO basis
Category:  Plane wave related variables
Unit:      Ry

Description:
  Energy cutoff for plane wave functions. Note that even for localized
  orbitals basis, you still need to setup an energy cutoff for this
  system. Because our local pseudopotential parts and the related force
  are calculated from plane wave basis set.
  Note: ecutwfc and ecutrho can be set simultaneously. If only one
        parameter is set, abacus will automatically set another
        parameter based on the 4-time relationship.
```

示例输出（`abacus -s relax`）：

```
Found 8 parameter(s) matching 'relax':

  relax_method                   - The methods to do geometry optimization. The available...
  relax_nmax                     - The maximal number of ionic iteration steps. If set to...
  relax_cg_thr                   - When relax_method is set to cg_bfgs, a mixed algorithm...
  ...

Use 'abacus -h <parameter>' for detailed help.
```

当用户输入了不存在的参数名时，帮助系统还会自动进行模糊匹配并给出建议：

```bash
abacus -h ecutwfx
# Error: Unknown parameter 'ecutwfx'
#
# Did you mean one of these?
#   - ecutwfc
#
# Use 'abacus -s <keyword>' to search for parameters.
```

**目的二：文档自动化**

文档元数据同时用于自动生成结构化文档：

- **自动生成 YAML**：通过 `abacus --generate-parameters-yaml` 导出全部参数信息到 `docs/parameters.yaml`
- **自动生成 Markdown 文档**：通过 Python 脚本（以下会介绍）从 YAML 生成 `input-main.md`，供在线文档使用

这样做到了**一处编写，三处生效**（命令行帮助、YAML 数据、在线文档），从根本上避免了代码与文档脱节的问题。

## 1.2 Input_Item 的新字段

路径：<u>source/source_io/module_parameter/input_item.h</u>

```cpp
class Input_Item
{
  public:
    // 原有字段
    std::string label;                   ///< 参数名
    std::vector<std::string> str_values; ///< 从 INPUT 读入的原始字符串
    std::stringstream final_value;       ///< 最终值（用于输出 INPUT 文件）

    // v3.9.23 新增的文档字段
    std::string category;      ///< 参数分类（如 "System variables"）
    std::string type;          ///< 数据类型（"Integer", "Real", "String", "Boolean"）
    std::string description;   ///< 详细描述（支持多行、列表）
    std::string default_value; ///< 默认值的字符串表示
    std::string unit;          ///< 物理单位（无单位时留空）
    std::string availability;  ///< 生效条件（始终可用时留空）

    std::string annotation;    ///< 简短注释（打印到 OUT.* 的 INPUT 中）

    // 四个 std::function 成员（不变，见原教程）
    // ...
};
```

## 1.3 如何填写文档字段

下面以添加一个虚构的 `my_str_parameter`（string 类型，默认值 `"foo"`）为例，完整展示填写方式。

### 第一步：在input_parameter.h 中声明

路径：<u>source/source_io/module_parameter/input_parameter.h</u>

```cpp
std::string my_str_parameter = "foo"; ///< a demo string parameter
```

### 第二步：在read_input_item_*.cpp 中注册（含文档字段

路径：source/source_io/module_parameter/read_input_item_system.cpp（根据参数类别选择对应文件）

```cpp
{
    Input_Item item("my_str_parameter");
    item.annotation = "a demo string parameter";

    // ===== 新增的文档字段 =====
    item.category = "System variables";
    item.type = "String";
    item.description = R"(This parameter controls the behavior of some feature.

* foo: use the default mode
* bar: enable advanced mode
* baz: enable experimental mode

[NOTE] This parameter only takes effect when calculation is set to scf.)";
    item.default_value = "foo";
    item.unit = "";
    item.availability = "Only used when calculation is scf";
    // ===== 文档字段结束 =====

    read_sync_string(input.my_str_parameter);

    item.check_value = [](const Input_Item& item, const Parameter& para) {
        const std::vector<std::string> allowed = {"foo", "bar", "baz"};
        if (std::find(allowed.begin(), allowed.end(), para.input.my_str_parameter) == allowed.end())
        {
            ModuleBase::WARNING_QUIT("ReadInput", "my_str_parameter must be foo, bar, or baz");
        }
    };

    this->add_item(item);
}
```

### 各字段说明

**category**：参数所属分类，用于文档和帮助系统的分组。必须使用已有的分类名称，常用值包括：

| category 值 | 含义 |
|------|------|
| `"System variables"` | 系统参数 |
| `"Electronic structure"` | 电子结构 |
| `"Plane wave related variables"` | 平面波相关 |
| `"Numerical atomic orbitals related variables"` | 数值原子轨道相关 |
| `"Geometry relaxation"` | 结构弛豫 |
| `"Molecular dynamics"` | 分子动力学 |
| `"Output information"` | 输出控制 |
| `"Exact Exchange (Common)"` | 杂化泛函 |
| `"DFT+U correction"` | DFT+U |

完整列表见 <u>docs/generate_input_main.py</u> 中的 `CATEGORY_ORDER`。如需新增分类，请同步更新该列表。

**type**：数据类型。常用值为 "Integer", "Real", "String", "Boolean"。对于复合类型的参数，也可以使用描述性的类型名，如 "Vector of Real", "Vector of string", "Integer Integer", "Int*2" 等。

**description**：参数的详细描述。支持以下格式：

```cpp
// 单行描述
item.description = "Energy cutoff for wavefunctions in Rydberg.";

// 多行描述（使用 R"(...)" 原始字符串）
item.description = R"(Specify the type of calculation.

* scf: self-consistent calculation
* nscf: non-self-consistent calculation
* relax: structure relaxation)";

// 带注意事项的描述
item.description = R"(Some description here.

[NOTE] This feature is experimental.)";
```

description 中的格式在生成文档时会被自动转换：`*` 列表标记 → `-` 标记，`[NOTE]` → blockquote。

**default_value**：默认值的字符串表示。注意这里填的是字符串，无论实际类型是什么：

```cpp
item.default_value = "foo";   // string 参数
item.default_value = "0";     // int 参数
item.default_value = "50.0";  // double 参数
item.default_value = "false"; // bool 参数
```

**unit**：物理单位。无单位时留空字符串 `""`：

```cpp
item.unit = "Ry";   // 有单位
item.unit = "eV";
item.unit = "";     // 无单位
```

**availability**：参数的生效条件，为自由格式的文本描述。始终可用时留空字符串 ""：

```cpp
item.availability = "basis_type==lcao";                          // 仅在 LCAO 基组时生效
item.availability = "Only used in localized orbitals set";       // 自然语言描述
item.availability = "symmetry==1 and exx calculation";           // 组合条件
item.availability = "";                                          // 始终可用
```

---

# 2. 生成docs/parameters.yaml

## 2.1 原理

ABACUS 编译后的可执行文件内置了所有参数的元数据。通过 `--generate-parameters-yaml` 命令行参数，可以将全部参数信息导出为 YAML 格式。

这一功能由 `ParameterHelp::generate_yaml()` 实现（source/source_io/input_help.cpp），它遍历所有已注册的 `Input_Item`，将文档字段序列化为 YAML。

## 2.2 操作步骤

```bash
# 1. 编译 ABACUS（确保代码已包含你的新参数）
cd build
cmake --build . -j8

# 2. 生成 YAML
./abacus --generate-parameters-yaml > ../docs/parameters.yaml

# 3. 验证 YAML 有效性
python3 -c "import yaml; d=yaml.safe_load(open('../docs/parameters.yaml')); print(len(d['parameters']), 'parameters')"
```

## 2.3 生成的 YAML 格式

生成的 `docs/parameters.yaml` 格式如下：

```yaml
# Auto-generated by: abacus --generate-parameters-yaml
# Do not edit manually.
parameters:
  - name: suffix
    category: System variables
    type: String
    description: |
      In each run, ABACUS will generate a subdirectory in the working directory.
      This subdirectory contains all the information of the run.
    default_value: ABACUS
    unit: ""
    availability: ""

  - name: my_str_parameter
    category: System variables
    type: String
    description: |
      This parameter controls the behavior of some feature.

      * foo: use the default mode
      * bar: enable advanced mode
      * baz: enable experimental mode

      [NOTE] This parameter only takes effect when calculation is set to scf.
    default_value: foo
    unit: ""
    availability: Only used when calculation is scf
```

## 2.4 验证单个参数

可以通过内置帮助系统验证你的参数元数据是否正确：

```bash
# 查看特定参数的帮助
./build/abacus -h my_str_parameter

# 搜索参数
./build/abacus -s my_str
```

帮助系统和 YAML 生成使用同一个运行时注册表，所以如果帮助输出正确，YAML 也会正确。

## 2.5 注意事项

- YAML 中数值类型的默认值（如 `"0"`, `"1.5"`）会被自动加引号，防止 YAML 解析器将其转换为数值类型
- YAML 关键字（`true`, `false`, `yes`, `no` 等）也会被自动加引号
- description 使用 YAML block scalar（`|`）格式，可以保留多行文本

---

# 3. 生成 `input-main.md` 文档

## 3.1 原理

`docs/generate_input_main.py` 读取 `parameters.yaml`，将参数按 category 分组、排序，生成 Markdown 格式的参数文档。

这个脚本有两种运行方式：

- **手动运行**：直接用命令行调用
- **Sphinx 自动运行**：在 `docs/conf.py` 中注册了 `builder-inited` 钩子，构建文档时自动调用

## 3.2 手动生成

```bash
python3 docs/generate_input_main.py docs/parameters.yaml \
    --output docs/advanced/input_files/input-main.md
```

输出示例：

```
Total: 523 documented parameters
Generated docs/advanced/input_files/input-main.md
Categories: 28
```

## 3.3 生成的 Markdown 格式

对于 `my_str_parameter`，生成的 Markdown 如下：

```sql
**### my_str_parameter

- **Type**: String
****- **Availability**: *****Only used when calculation is scf*****
- **Description**: This parameter controls the behavior of some feature.
  - foo: use the default mode
  - bar: enable advanced mode
  - baz: enable experimental mode

  > Note: This parameter only takes effect when calculation is set to scf.
****- **Default**: foo**
```

注意自动转换：

- `*` 列表标记 → `- ` 标记
- `[NOTE]` → `> Note:`
- `[WARNING]` → `> Warning:`

## 3.4 新增 category 时

如果你的参数使用了一个新的 category，需要将其添加到 <u>docs/generate_input_main.py</u> 的 `CATEGORY_ORDER` 列表中，否则该分类会被排到文档末尾：

```python
CATEGORY_ORDER = [
    "System variables",
    "Input files",
    # ...
    "My New Category",  # 添加到合适的位置
]
```

---

# 4. 完整工作流

添加新参数 `my_str_parameter` 的完整步骤：

### 步骤 1：声明参数

在 <u>source/source_io/module_parameter/input_parameter.h</u> 中：

```cpp
std::string my_str_parameter = "foo"; ///< a demo string parameter
```

### 步骤 2：注册参数（含文档字段）

在对应的 <u>read_input_item_*.cpp</u> 中（参照第 1 节的完整示例）。

### 步骤 3：在代码中使用

```cpp
std::string val = PARAM.inp.my_str_parameter; // 只读访问
```

### 步骤 4：添加单元测试

在 <u>source/source_io/test/read_input_ptest.cpp</u> 中添加测试（见[原教程](https://mcresearch.github.io/abacus-user-guide/develop-addinp2.html)）。

### 步骤 5：编译并生成文档

```bash
# 编译
cd build && cmake --build . -j8

# 验证帮助系统
./abacus -h my_str_parameter

# 生成 YAML
./abacus --generate-parameters-yaml > ../docs/parameters.yaml

# 验证 YAML
python3 -c "import yaml; d=yaml.safe_load(open('../docs/parameters.yaml')); print(len(d['parameters']), 'parameters')"

# 生成 Markdown 文档
python3 ../docs/generate_input_main.py ../docs/parameters.yaml \
    --output ../docs/advanced/input_files/input-main.md
```

### 步骤 6：提交 PR

PR 中需要包含以下文件的改动：

- `source/source_io/module_parameter/input_parameter.h`（参数声明）
- `source/source_io/module_parameter/read_input_item_*.cpp`（参数注册 + 文档字段）
- `docs/parameters.yaml`（重新生成）
- 测试文件

`docs/advanced/input_files/input-main.md` 会在文档构建时由 Sphinx 自动生成，通常不需要手动提交。

---

# 5. 内置帮助系统命令参考

v3.9.23 新增了命令行帮助系统，开发者在调试参数文档时非常有用：

```bash
# 查看通用帮助
abacus -h
abacus --help

# 查看指定参数的详细说明
abacus -h ecutwfc
abacus -h my_str_parameter

# 搜索参数（子串匹配）
abacus -s ecut
abacus -s relax

# 拼写纠错（自动模糊匹配）
abacus -h ecutwfx
# 输出: Error: Unknown parameter 'ecutwfx'
#        Did you mean one of these?
#          - ecutwfc
#        Use 'abacus -s <keyword>' to search for parameters.

# 导出全部参数的 YAML
abacus --generate-parameters-yaml

# 检查 INPUT 文件语法
abacus --check-input

# 查看版本信息
abacus -v
abacus --version

# 查看编译信息
abacus -i
abacus --info
```
