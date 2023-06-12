# ABACUS使用教程

## 一、介绍

ABACUS（中文名量子算筹）是国产开源密度泛函理论软件，相关新闻可在[ABACUS 新闻稿整理](abacus-news.md)查看。本教程系列旨在帮助新手用户入门了解ABACUS的使用。秉着开源软件的理念，本文档是由开源社区的老师同学们贡献所成。如果你也想贡献一份文档，我们十分欢迎，请参考[如何贡献ABACUS使用教程](contribute.md)

## 二、ABACUS基本操作教程

1. ABACUS的编译介绍
   1. [官方编译教程](https://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html)
   2. [知乎上用户提供的ABACUS 3.0安装教程](https://zhuanlan.zhihu.com/p/574031713)
   3. [<mark style="color:red;">编译无MPI的ABACUS</mark>](https://dptechnology.feishu.cn/wiki/wikcnuC1vwoPzEugtZNAyTd7ZWg)<mark style="color:red;"></mark>
   4. 曙光DCU平台编译教程：[ABACUS 在曙光 DCU 集群上的编译与使用](abacus-dcu.md)
2. ABACUS建模介绍
   1. 准备晶胞和原子位置等信息的文件STRU：[<mark style="color:red;">如何转换STRU的格式</mark>](https://dptechnology.feishu.cn/wiki/wikcn6fjwNR77kxbyKDdFZASkOg)<mark style="color:red;"></mark>
   2. 数值原子轨道基组生成教程：[<mark style="color:red;">如何产生ABACUS中的数值原子轨道文件</mark>](https://dptechnology.feishu.cn/wiki/wikcnbOETPFjYPqlb5SzWPGlcHh)<mark style="color:red;"></mark>
   3. 准备赝势（缺）
3. Kohn-Sham密度泛函理论
   1. 电子自洽迭代
      1. 平面波PW（缺）
      2. 数值原子轨道LCAO（缺）
   2. 带自旋的体系计算：[<mark style="color:red;">ABACUS磁性材料计算使用教程</mark>](https://xmywuqhxb0.feishu.cn/docx/E4ZvdMJzGonWJhxanBacS6dWnsP)<mark style="color:red;"></mark>
   3. \+U计算：[<mark style="color:red;">ABACUS DFT+U使用教程</mark>](https://dptechnology.feishu.cn/wiki/wikcnLTpXB1be9s1Q896GrA7PBf)<mark style="color:red;"></mark>
   4. 结构优化（缺）
   5. 分子动力学：[ABACUS 分子动力学使用教程](abacus-md.md)
4. DeePKS方法（缺）
5. 隐式溶剂计算等相关功能（缺，找许审镇老师）
6. 随机波函数密度泛函理论：[ABACUS 随机波函数DFT方法使用教程](abacus-sdft.md)
7. 分析结果
   1. 能带计算
      1. [<mark style="color:red;">如何正确画能带，NSCF读电荷密度</mark>](https://dptechnology.feishu.cn/wiki/wikcnUTWmTj8sQYeSdwcInFRLwg)<mark style="color:red;"></mark>
      2. [<mark style="color:red;">用ABACUS-ASE自动产生能带路径</mark>](https://dptechnology.feishu.cn/wiki/wikcnxzVKuGZ9lSAoKOM1lpD6Pf)<mark style="color:red;"></mark>
   2. PDOS计算
      1. [<mark style="color:red;">ABACUS里怎样做DOS和PDOS计算</mark>](https://dptechnology.feishu.cn/wiki/wikcnM7MsN60p43DsZ1uSjkIyxg)<mark style="color:red;"></mark>
8. 和其他软件对接
   1. ABACUS+Phonopy教程：[ABACUS+Phonopy 计算声子谱](abacus-phonopy.md)
   2. ABACUS+ShengBTE教程：[ABACUS+ShengBTE 计算晶格热导率](abacus-shengbte.md)
   3. ABACUS+DPGEN教程：[ABACUS+DPGEN 使用教程](abacus-dpgen.md)
   4. ABACUS+CINEB教程（缺，找许审镇老师）
      1. [<mark style="color:red;">ABACUS-ASE做NEB计算</mark>](https://dptechnology.feishu.cn/wiki/wikcnzar41sN8ZtGLtm3PLnarSc) <mark style="color:red;"></mark> （简单算例）

## 三、使用经验

1. 有VASP使用背景的用户上手ABACUS教程：[<mark style="color:red;">ABACUS新人使用的一些注意事项</mark>](https://dptechnology.feishu.cn/wiki/wikcnffgspo43uB4jPQZditWlXf)<mark style="color:red;"></mark>
2. ABACUS进行LCAO计算前轨道基组测试教程：[<mark style="color:red;">LCAO具体计算前的基本参数测试教程文档</mark>](https://dptechnology.feishu.cn/wiki/wikcneQF9WVQS4KAS6fyC6lGBEe?create\_from=copy\_within\_wiki\&from=create\_suite\_copy)<mark style="color:red;"></mark>
3. 对比测试ABACUS中解析计算的晶格应力与能量差分方法计算的晶格应力的教程：[<mark style="color:red;">差分测试规范</mark>](https://dptechnology.feishu.cn/wiki/wikcnFDqUKlmjjBlTHe9zhLNkce)<mark style="color:red;"></mark>
