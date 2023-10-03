# ABACUS 线上文档输入参数撰写规范

<strong>作者：刘建川，邮箱：liujianchuan2013@163.com</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn；韩昊知，邮箱：haozhi.han@stu.pku.edu.cn</strong>

<strong>最后更新时间：2023/10/03</strong>

# 一、背景

<strong>ABACUS 代码仓库地址：</strong>[https://github.com/deepmodeling/abacus-develop](https://github.com/deepmodeling/abacus-develop)

<strong>ABACUS 线上文档地址：</strong>[https://abacus.deepmodeling.com/en/latest/](https://abacus.deepmodeling.com/en/latest/)

（ ABACUS 线上文档是包括开发者在内的所有用户了解 ABACUS 软件使用方法的重要渠道。）

<strong>本文档关注：“关键字”部分的文档</strong>

- 对应的文档地址：[https://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html](https://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html)
- 对应的代码地址：[https://github.com/deepmodeling/abacus-develop/blob/develop/docs/advanced/input_files/input-main.md](https://github.com/deepmodeling/abacus-develop/blob/develop/docs/advanced/input_files/input-main.md)

<strong>更新方式：</strong>目前对该文档的更新同样是通过 PR 的方式提交到 ABACUS 的 Github 仓库上，因此<strong>任何人都可以通过提交 PR 的方式对文档做出修改，我们也鼓励用户如果发现问题后可以主动修复文档</strong>。

# 二、规范格式

每个输入参数都应遵循以下格式：

> <strong>Name of Parameter</strong>
> <strong>Type:</strong>
> <strong>Availability: (可选)</strong>
> <strong>Description:</strong>
> <strong>Default:</strong>
> <strong>Unit:  (可选)</strong>
> <strong>Example: (可选)</strong>

按照上述顺序排列，上述所有字段需加粗，后面使用英文冒号（不加粗），冒号后空一格开始写内容（不加粗）

- <strong>上述关键字用黑色实心圆，关键字后的介绍不用加粗</strong>

> 错误示范：<strong>Type:</strong>Integer
> 错误示范：<strong>Type: </strong>integer
> 错误示范：<strong>Type: integer</strong>
> 正确示范：<strong>Type</strong>:<strong> </strong>Integer
> 错误示范：Default: 0
> 错误示范: Default: false
> 正确示范：<strong>Default</strong>:<strong> </strong>False

## 1. Name of Parameter

这个参数代表了参数的名称，建议起参数名称的时候遵从以下规范（xxx 由设定参数名的开发者指定）：

- <strong>输出某物理量的参数：</strong>建议以 `out_xxx` 为参数名，其中 out 是 output 的缩写。可参考的变量名有 `out_chg`（输出电荷密度），`out_pot`（输出势函数），`out_dm`（输出密度矩阵 density matrix）
- <strong>收敛阈值相关参数：</strong>建议以 `xxx_thr` 为参数名，其中 `thr` 是 threshold 的缩写。可参考的变量名有 `scf_thr`（电子自洽迭代的收敛阈值），`force_thr`（结构弛豫时原子中的最大受力域值），和 `stress_thr`(晶格优化时的应力收敛阈值)
- <strong>计算某物理量的参数：</strong>建议以 `cal_xxx` 为参数名，其中 `cal` 是 calculate 的缩写
- <strong>初始化某物理量的参数：</strong>建议以 `init_xxx` 为参数名，其中 `init` 是 initialize 的缩写。可参考的变量名有 `init_wfc`（初始化波函数）, `init_chg`（初始化电荷密度）, `init_vel`（初始化原子速度）
- <strong>结构弛豫相关参数：</strong>建议以 `relax_xxx` 为参数名，其中 `relax` 代表（结构）弛豫
- <strong>并行策略相关参数：</strong>建议以 `xxxpar` 为参数名，其中 `par` 是代表 parallel，即并行。可参考的变量名有 `kpar`（k 点并行），`bndpar`（能带并行）
- <strong>其它参数：</strong>建议先寻找 ABACUS 目前支持的参数名来设计相关参数

## 2. Type

- Type：冒号之后首字母大写，输入参数的种类，有 Integer，Real 和 String 三种类型。对于 Boolean 类型，Default 字段后的内容统一写：True 或 False（首字母大写），且先写 True，再写 False
- 注意 Real 类型不要写成 double 或者 float 类型

## 3. Availability（Optional）

如果是完整的一句话就首字母大写，如果是单词或短语就小写

## 4. Description

- 冒号之后首字母大写
- 如果有 Note 的标注，可在 Description 字段下，单独写一个 Note，不用加粗。
- Description 字段里如果有涉及到 1 和 0 是表示 True 或 False，统一改成 True 或 False。
- 字段如果是完整句子，末尾要加英文句号："."，若是单词和短语则不加。其他字段均不加。
- String 类型的参数 直接列出所有选项
- 当一个参数有多种取值时，按照从小到大顺序描述不同的取值，例如 propagator 这个参数，就在 description 里面描述参数是 0，1，2 三种情况下的波函数演化方法。
- 不写“when set to”、“if set to”，直接写参数后，再写该参数的描述

## 5. Default

参数默认的数值，分成有单位的和没有单位的两种。如果是小数，建议采用科学计数法表示，“e”一律小写，如: 2e-6

## 6. Unit（Optional）

如有需要使用 Unit 来标定输入参数的单位，紧接在 Unit 后面描述单位，另外内容里如果涉及到写单位，需要用空格隔开，如：U (eV)

单位撰写需符合标准：

> 错误示范：KBar
> 错误示范：ev
> 正确示范：kbar
> 正确示范：eV

## 7. Example（Optional）

- 如有案例，可添加相关例子的链接和简单描述。如果需要，可以添加上述的 Example 字段描述案例。

# 三、其他问题

- 所有简写应该大写，以及后面用括号写出全称，每一个关键字的描述出现了简写均需要写全称，如:“soc”改成“SOC（spin-orbital-coupling）”。即使最常见的如 PW、MD 等也均写出全称
- 对参数的描述保持客观，如：不写“An important parameter”这种话
- 相关的参数建议放在文档上靠近的地方。举例：symmetry 参数是控制是否打开对称性操作的参数，而 symmetry_prec 是用来控制对称性操作的精度，这两个参数就可以放在一起先后介绍，并且在介绍的时候，可以提及相关的参数
- 一些太长的输出，单独开辟一个专区去介绍
- 如关键字告诉了用户输出了文件，建议告诉用户文件名称和文件保存的路径
- 注意语法问题
- 标点符号格式要一致
- 注意不要出现乱码

以上若有问题或者建议，欢迎写信给作者！虽然我们邮箱基本不会收到类似邮件，但开源精神的意义就在于提供了这种可能性，然后坚信更好的事情会到来。
