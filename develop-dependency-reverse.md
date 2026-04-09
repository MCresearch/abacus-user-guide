# 依赖反转原则入门介绍

**作者：陈默涵，邮箱：mohanchen@pku.edu.cn**

**辅助：Seed V2.0 Flash**

**最后更新时间：2026/04/09**

## 一、什么是依赖反转？

### 生活中的例子

想象一下，你去餐厅吃饭：

- **传统方式**：你直接跑到厨房，找到厨师说："我要一份宫保鸡丁！"
- **依赖反转方式**：你坐在桌子上，告诉服务员："我要一份宫保鸡丁！"，然后服务员去厨房告诉厨师。

在传统方式中，你（顾客）直接依赖于厨师（具体实现）。如果厨师不在，你就吃不到饭了。

在依赖反转方式中，你（顾客）依赖于服务员（抽象接口），而不是直接依赖于厨师（具体实现）。这样，不管谁在厨房做饭，甚至服务员可以去点外卖，你都能吃到想要的菜。

### 技术定义

依赖反转原则（Dependency Inversion Principle，DIP）有两个核心思想：

1. **高层模块不应该依赖低层模块，两者都应该依赖于抽象**
2. **抽象不应该依赖于细节，细节应该依赖于抽象**

简单来说，就是让代码之间的依赖关系从"具体实现 → 具体实现"转向"抽象 ← 具体实现"。

## 二、为什么需要依赖反转？

### 传统方式的问题

假设你是一个程序员，需要写一个程序来处理数据。传统的做法可能是这样的：

- 你写一个 `DataProcessor` 类来处理数据
- 这个类直接使用 `FileReader` 类来读取文件
- 如果以后需要从数据库读取数据，你就需要修改 `DataProcessor` 类

这样的代码有以下问题：

- **紧耦合**：`DataProcessor` 和 `FileReader` 紧密绑定在一起
- **难扩展**：添加新的数据源需要修改现有代码
- **难测试**：测试时必须使用真实的文件
- **难维护**：代码结构复杂，难以理解

### 依赖反转的好处

使用依赖反转后，代码会变成这样：

1. 你定义一个 `DataReader` （基类）接口，规定了读取数据的方法（但不实现，只是虚的，抽象的）
2. 通过继承 `DataReader` 的办法，实现 `FileReader` 和 `DatabaseReader` 等具体类
3. `DataProcessor` 类只依赖于基类 `DataReader` 接口，不关心具体是从哪里读取数据，不依赖于继承的实现

这样的代码有以下好处：

- **松耦合**：`DataProcessor`（需要依赖反转的代码） 和具体的数据源（用继承虚函数的方式写）解耦
- **易扩展**：添加新的数据源只需要实现 `DataReader` 接口（只需要实现继承的子类）
- **易测试**：测试时可以使用模拟的 `DataReader` 实现（实现个假的继承）
- **易维护**：代码结构清晰，职责明确

## 三、更多生活例子

### 例子 1：电视遥控器

- **传统方式**：每个电视品牌都有自己的遥控器，只能控制自己品牌的电视
- **依赖反转方式**：所有电视都遵循同一个接口标准，一个遥控器可以控制任何品牌的电视

### 例子 2：电源插座

- **传统方式**：每个电器都有自己独特的插头，需要专门的插座
- **依赖反转方式**：所有电器都使用标准插头，任何插座都可以使用

### 例子 3：USB 接口

- **传统方式**：每个设备都有自己的接口，需要专门的数据线
- **依赖反转方式**：所有设备都使用 USB 接口，一根数据线可以连接多种设备

## 四、以 DSP 代码为例

### 问题背景

在 ABACUS 项目中，`module_device` 模块中的 DSP 相关代码直接依赖于 `source_io` 模块中的 `PARAM` 全局变量：

```cpp
// 原始代码
arr = (FPTYPE*)mtfunc::malloc_ht(sizeof(FPTYPE) * size, GlobalV::MY_RANK % PARAM.inp.dsp_count);
```

这里的问题是：

- `memory_op_dsp.cpp` 文件直接依赖于 `parameter.h` 中的 `PARAM` 变量
- 如果 `PARAM` 的结构发生变化，这段代码就可能出错
- 测试时很难模拟不同的 `dsp_count` 值
- `module_device` 模块无法独立于 `source_io` 模块编译和测试

### 实现依赖反转

#### 步骤 1：创建抽象接口

就像创建一个服务员的角色，定义好服务的方法：

```cpp
// dsp_selector.h
class DspSelector {
public:
    virtual ~DspSelector() = default;
    // 获取DSP rank的方法
    virtual int get_rank() const = 0;
    // 设置DSP rank的方法
    virtual void set_rank(const int rank) = 0;
};
```

这个接口就像服务员的工作手册，规定了服务员必须提供哪些服务。

#### 步骤 2：实现具体类

就像雇佣具体的服务员，按照工作手册提供服务：

```cpp
// dsp_selector.cpp
class DefaultDspSelector : public DspSelector {
private:
    int rank_ = 0; // 存储DSP rank

public:
    // 获取rank
    int get_rank() const override {
        return rank_;
    }

    // 设置rank，并检查是否合法
    void set_rank(const int rank) override {
        if (rank < 0) {
            throw std::runtime_error("DSP rank必须是非负的");
        }
        rank_ = rank;
    }
};
```

这个具体类就像一个实际的服务员，按照工作手册的要求提供服务。

#### 步骤 3：创建工厂函数

就像创建一个服务员派遣中心，负责管理服务员：

```cpp
// dsp_selector.cpp
void create_default_selector(const int rank) {
    // 创建一个新的服务员
    dsp_selector = std::unique_ptr<DefaultDspSelector>(new DefaultDspSelector());
    // 告诉服务员要做什么
    dsp_selector->set_rank(rank);
}
```

这个工厂函数就像服务员派遣中心，负责创建和管理服务员。

#### 步骤 4：初始化选择器

就像顾客告诉服务员要点什么菜：

```cpp
// dsp_config.cpp
void init_dsp_selector(const int my_rank, const int dsp_count) {
    // 验证参数
    if (my_rank < 0) {
        throw std::runtime_error("my_rank必须是非负的");
    }
    if (dsp_count <= 0) {
        throw std::runtime_error("dsp_count必须是正数");
    }
    
    // 计算应该使用哪个DSP
    const int rank = my_rank % dsp_count;
    // 告诉派遣中心派一个服务员来处理
    base_device::memory::create_default_selector(rank);
}
```

这个函数就像顾客点单，告诉服务员派遣中心需要什么样的服务。

#### 步骤 5：修改使用代码

就像顾客通过服务员点菜，而不是直接找厨师：

```cpp
// memory_op_dsp.cpp
void operator()(FPTYPE*& arr, const size_t size, const char* record_in) {
    if (arr != nullptr) {
        mtfunc::free_ht(arr);
    }
    // 通过服务员获取DSP rank
    int rank = get_dsp_selector()->get_rank();
    arr = (FPTYPE*)mtfunc::malloc_ht(sizeof(FPTYPE) * size, rank);
    // 其余代码不变
    ...
}
```

现在，`memory_op_dsp.cpp` 不再直接依赖于 `parameter.h`，而是通过 `DspSelector` 接口获取 DSP rank。

## 五、依赖反转的好处

### 1. 灵活性

如果以后需要改变 DSP rank 的计算方式，只需要修改 `DefaultDspSelector` 类，不需要修改使用它的代码。

例如，如果我们想根据不同的策略选择 DSP，只需要创建一个新的 `DspSelector` 实现：

```cpp
class RoundRobinDspSelector : public DspSelector {
private:
    int current_rank_ = 0;
    int max_rank_ = 0;

public:
    RoundRobinDspSelector(int max_rank) : max_rank_(max_rank) {}

    int get_rank() const override {
        return current_rank_;
    }

    void set_rank(const int rank) override {
        current_rank_ = rank % max_rank_;
    }
};
```

### 2. 可测试性

测试时可以创建一个特殊的 `DspSelector` 实现，返回固定的 rank 值，方便测试：

```cpp
class TestDspSelector : public DspSelector {
private:
    int test_rank_ = 0;

public:
    TestDspSelector(int rank) : test_rank_(rank) {}

    int get_rank() const override {
        return test_rank_;
    }

    void set_rank(const int rank) override {
        test_rank_ = rank;
    }
};
```

### 3. 解耦

`memory_op_dsp.cpp` 不再直接依赖于 `parameter.h`，它们通过 `DspSelector` 接口间接联系。这样，`module_device` 模块可以独立于 `source_io` 模块编译和测试。

### 4. 可维护性

代码结构更清晰，每个部分的职责更明确：

- `DspSelector` 接口：定义了获取和设置 DSP rank 的方法
- `DefaultDspSelector` 类：实现了具体的 DSP 选择逻辑
- `create_default_selector` 函数：负责创建和初始化选择器
- `init_dsp_selector` 函数：负责计算和设置 DSP rank
- `memory_op_dsp.cpp`：使用选择器获取 DSP rank

### 5. 可扩展性

添加新的 DSP 选择策略变得更加容易，只需要实现 `DspSelector` 接口即可。

## 六、代码结构

修改后的代码结构就像一个餐厅的组织结构：

```
source/
├── source_base/
│   └── module_device/          # 厨房
│       ├── dsp_selector.h      # 服务员接口（工作手册）
│       ├── dsp_selector.cpp    # 具体的服务员和派遣中心
│       └── memory_op_dsp.cpp   # 顾客（使用服务的人）
└── source_io/
    └── module_parameter/        # 前台
        ├── dsp_config.cpp      # 服务员派遣中心的具体操作
        └── input_conv.cpp      # 顾客点单的地方
```

## 七、如何识别需要使用依赖反转的情况

当你发现以下情况时，可能需要使用依赖反转：

1. **紧耦合**：一个模块直接依赖于另一个模块的具体实现
2. **难测试**：测试时需要模拟多个依赖
3. **难扩展**：添加新功能需要修改多个模块
4. **难维护**：代码结构复杂，职责不明确
5. **重复代码**：多个模块中有相似的代码

## 八、依赖反转的常见实现方式

### 1. 接口继承

就像我们在 DSP 例子中使用的方式，定义一个抽象接口，然后实现具体类。

### 2. 依赖注入

通过构造函数或 setter 方法将依赖传递给对象：

```cpp
class DataProcessor {
private:
    DataReader* reader;

public:
    // 通过构造函数注入依赖
    DataProcessor(DataReader* r) : reader(r) {}

    void process() {
        // 使用 reader 读取数据
    }
};
```

### 3. 工厂模式

通过工厂函数创建对象，隐藏创建细节：

```cpp
class DataReaderFactory {
public:
    static DataReader* createReader(const std::string& type) {
        if (type == "file") {
            return new FileReader();
        } else if (type == "database") {
            return new DatabaseReader();
        }
        return nullptr;
    }
};
```

### 4. 服务定位器

通过一个中央注册表来获取依赖：

```cpp
class ServiceLocator {
private:
    static std::map<std::string, void*> services;

public:
    static void registerService(const std::string& name, void* service) {
        services[name] = service;
    }

    static void* getService(const std::string& name) {
        return services[name];
    }
};
```

## 九、实际项目中的应用

依赖反转在实际项目中有广泛的应用，例如：

### 1. 框架设计

许多流行的框架都使用依赖反转，例如：

- Spring 框架（Java）：使用依赖注入来管理对象
- Angular 框架（JavaScript）：使用依赖注入来管理服务
- PyTorch（Python）：使用抽象接口来支持不同的设备

### 2. 测试

在测试中，依赖反转可以帮助我们：

- 模拟外部依赖，如数据库、网络服务等
- 测试不同的场景和边界情况
- 提高测试的速度和可靠性

### 3. 插件系统

依赖反转可以用于创建插件系统

- 定义插件接口
- 插件实现接口
- 主程序通过接口使用插件

### 4. 微服务架构

在微服务架构中，依赖反转可以帮助

- 服务之间通过接口通信，而不是直接依赖
- 服务可以独立部署和升级
- 服务可以使用不同的技术栈

## 十、总结

依赖反转原则就像餐厅的服务流程：顾客通过服务员点菜，而不是直接找厨师。这样，不管厨房怎么变化，顾客都能享受到一致的服务。

在代码中，我们通过创建抽象接口，让高层模块（顾客）依赖于抽象（服务员），而不是具体实现（厨师）。这样可以使代码更加灵活、可测试和可维护。

依赖反转不是一种复杂的技术，而是一种思考方式。它帮助我们设计出更加模块化、更加灵活的代码，是每个程序员都应该掌握的重要原则。

通过学习和应用依赖反转，你可以：

- 写出更加健壮的代码
- 更容易地添加新功能
- 更有效地测试你的代码
- 与团队成员更好地协作
- 成为一名更优秀的软件工程师
