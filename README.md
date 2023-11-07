# ABACUS使用教程

# 一、介绍

ABACUS（Atomic-orbtial Based Ab-initio Computation at UStc，中文名原子算筹）是国产开源密度泛函理论软件，相关介绍 ABACUS 的新闻可在[ABACUS 新闻稿整理](abacus-news.md)查看，以下是一些常用地址：

ABACUS 在 DeepModeling 社区中的 GitHub 仓库地址为：

[https://github.com/deepmodeling/abacus-develop](https://github.com/deepmodeling/abacus-develop)

ABACUS 的 Gitee 镜像仓库地址为：

[https://gitee.com/deepmodeling/abacus-develop](https://gitee.com/deepmodeling/abacus-develop)

ABACUS 网站访问：

[http://abacus.ustc.edu.cn/](http://abacus.ustc.edu.cn/)

文档（包括安装方法、输入输出参数介绍、功能介绍、算例介绍、开发者须知等）：

[https://abacus.deepmodeling.com/en/latest/](https://abacus.deepmodeling.com/en/latest/)

本教程系列旨在帮助新手用户入门了解 ABACUS 的使用。秉着开源软件的理念，本文档是由开源社区的老师同学们贡献所成。如果你也想贡献一份文档，我们十分欢迎，请参考[如何贡献ABACUS使用教程](contribute.md)。

本教程中标有<a href="" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a> Logo的部分可以直接在[Bohrium Notebook](https://nb.bohrium.dp.tech)上打开。

在Bohrium Notebook上快速学习，见[快速开始 ABACUS｜自洽 能带 态密度 结构优化](https://nb.bohrium.dp.tech/detail/4641406377)；在Bohrium平台上运行大任务，见[教程](https://bohrium-doc.dp.tech/docs/software/ABACUS/)。

# 二、ABACUS基本操作教程

1. ABACUS的编译介绍
   1. [官方编译教程](https://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html)
   2. [GCC 编译 ABACUS 教程](abacus-gcc.md)
   3. [Intel oneAPI 编译 ABACUS 教程](abacus-intel.md)
   4. [在超算环境编译 ABACUS 的建议](abacus-hpc.md)
   5. [ABACUS 在曙光 DCU 集群上的编译与使用](abacus-dcu.md)
   6. [ABACUS toolchain 脚本集](https://github.com/deepmodeling/abacus-develop/tree/develop/toolchain) (md文档待整理)
2. ABACUS建模介绍
   1. 准备晶胞和原子位置等信息的文件STRU：[如何转换STRU的格式](https://nb.bohrium.dp.tech/detail/9814968648)
   <mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/9814968648" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   2. 准备赝势：
   [模守恒赝势生成方法简介](abacus-upf.md)
   3. 数值原子轨道基组生成教程：
      1. [数值原子轨道（一）：ABACUS 中的数值原子轨道命名和使用方法](abacus-nac1.md)
      2. [数值原子轨道（二）：生成给定模守恒赝势的数值原子轨道](abacus-nac2.md)<a href="https://nb.bohrium.dp.tech/detail/5215642163" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
      3. [数值原子轨道（三）：产生高精度数值原子轨道](abacus-nac3.md)<a href="https://nb.bohrium.dp.tech/detail/8841868194" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
3. Kohn-Sham密度泛函理论
   1. [电子自洽迭代](https://nb.bohrium.dp.tech/detail/7417640496)<a href="https://nb.bohrium.dp.tech/detail/7417640496" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   2. 带自旋的体系计算：[ABACUS磁性材料计算使用教程](https://nb.bohrium.dp.tech/detail/7141761751)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/7141761751" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   3. \+U计算：[ABACUS DFT+U使用教程](https://nb.bohrium.dp.tech/detail/2112617648)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/2112617648" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   4. 结构优化：[ABACUS 使用教程｜结构优化](https://nb.bohrium.dp.tech/detail/9119461238)<a href="https://nb.bohrium.dp.tech/detail/9119461238" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   5. 分子动力学：[ABACUS 分子动力学使用教程](abacus-md.md)<a href="https://nb.bohrium.dp.tech/detail/2241262724" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
4. DeePKS方法（缺）
5. [ABACUS 隐式溶剂模型使用教程](abacus-sol.md)
6. 随机波函数密度泛函理论：[ABACUS 随机波函数DFT方法使用教程](abacus-sdft.md)<a href="https://nb.bohrium.dp.tech/detail/5915692245" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
7. 无轨道密度泛函理论：[ABACUS 无轨道密度泛函理论方法使用教程](abacus-ofdft.md)<a href="https://nb.bohrium.dp.tech/detail/6416644691" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
8. 采用ABACUS进行表面计算
   1. [静电势和功函数](abacus-surface1.md)
   2. [偶极修正](abacus-surface2.md)
   3. [表面能计算](abacus-surface3.md)
   4. [表面缺陷能和吸附能计算](abacus-surface4.md)
   5. [外加电场](abacus-surface5.md)
   6. [补偿电荷](abacus-surface6.md)
9.  分析结果
   1. 能带计算
      1. [<mark style="color:red;">如何正确画能带，NSCF读电荷密度</mark>](https://xmywuqhxb0.feishu.cn/docx/K8GRdTst4oXQNoxnQVbcFZTmntb)<mark style="color:red;"></mark>
      2. [用ABACUS-ASE自动产生能带路径](https://nb.bohrium.dp.tech/detail/1211642609)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/1211642609" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   2. PDOS计算
      1. [<mark style="color:red;">ABACUS里怎样做DOS和PDOS计算</mark>](https://xmywuqhxb0.feishu.cn/docx/ONSldj82VoNGKSxaoDQcoKBtnGh)<mark style="color:red;"></mark>
10. 和其他软件对接
    1. [ABACUS+Phonopy 计算声子谱](abacus-phonopy.md)<a href="https://nb.bohrium.dp.tech/detail/8741867512" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    2. [ABACUS+ShengBTE 计算晶格热导率](abacus-shengbte.md)<a href="https://nb.bohrium.dp.tech/detail/2712467526" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    3. [ABACUS+Phono3py 计算晶格热导率](https://nb.bohrium.dp.tech/detail/6116471155)<a href="https://nb.bohrium.dp.tech/detail/6116471155" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    4. [ABACUS+DPGEN 使用教程](abacus-dpgen.md)<a href="https://nb.bohrium.dp.tech/detail/6116401077" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    5. [ABACUS+LibRI 做杂化泛函计算教程](abacus-libri.md)<a href="https://nb.bohrium.dp.tech/detail/8041860882" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    6. [ABACUS+Candela 使用教程](abacus-candela.md)<a href="https://nb.bohrium.dp.tech/detail/2912697542" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    7. [ABACUS+USPEX 接口教程](abacus-uspex.md)
    8. [ABACUS+Hefei NAMD 使用教程](abacus-namd.md)
    9. [ABACUS+pyatb 能带反折叠计算](https://nb.bohrium.dp.tech/detail/2012704420)<a href="https://nb.bohrium.dp.tech/detail/2012704420" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    10. [ABACUS+DeepH 建立碳材料的哈密顿量模型](https://nb.bohrium.dp.tech/detail/6242632169)<a href="https://nb.bohrium.dp.tech/detail/6242632169" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    11. [从 DFT 先去 DeePKS 再到 DeePMD | DeePKS案例篇 + 增强采样](https://nb.bohrium.dp.tech/detail/7144731675)<a href="https://nb.bohrium.dp.tech/detail/7144731675" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    12. [ABACUS+ASE接口使用技巧](https://bbs.abacus-dft.com/forum.php?mod=viewthread&tid=4&extra=page%3D1)
    13. ABACUS+CINEB教程（缺）
        1. [ASE-NEB-ABACUS工作流与算例](https://github.com/QuantumMisaka/ase-neb-abacus) （v1.0.1 支持对NEB的各个image进行并行计算，大大提升NEB计算效率）
        2. [<mark style="color:red;">ABACUS-ASE做NEB计算</mark>](https://dptechnology.feishu.cn/wiki/wikcnzar41sN8ZtGLtm3PLnarSc) <mark style="color:red;"></mark> （简单算例）

# 三、使用经验

1. 有VASP使用背景的用户上手ABACUS教程：[<mark style="color:red;">ABACUS新人使用的一些注意事项</mark>](https://xmywuqhxb0.feishu.cn/docx/KN3KdqbX6o9S6xxtbtCcD5YPnue)<mark style="color:red;"></mark>

# 四、开发者文档

1. [ABACUS 开源项目 C++ 代码规范](develop-C++.md)
2. [ABACUS 中使用格式化工具 clang-format](develop-format.md)
3. [ABACUS 注释规范：Doxygen 入门 (c++)](develop-dox.md)
4. [ABACUS 的 Github 仓库 Issues 处理流程](develop-issue.md)
5. [ABACUS 线上文档输入参数撰写规范](develop-input.md)
6. [Introduction to ABACUS: Path to PW calculation - Part 1](develop-path1.md)
7. [Introduction to ABACUS: Path to PW calculation - Part 2](develop-path2.md)
8. [Introduction to ABACUS: Path to PW calculation - Part 3](develop-path3.md)
9. [Introduction to ABACUS: Path to PW calculation - Part 4](develop-path4.md)
10. [Introduction to ABACUS: Path to PW calculation - Part 5](develop-path5.md)
11. [Introduction to ABACUS: Path to PW calculation - Summary 1](develop-sm1.md)
12. [Introduction to ABACUS: Path to PW calculation - Part 6](develop-path6.md)
13. [Introduction to ABACUS: Path to PW calculation - Part 7](develop-path7.md)
14. [Introduction to ABACUS: Path to PW calculation - Part 8](develop-path8.md)
15. [Introduction to ABACUS: Path to PW calculation - Part 9](develop-path9.md)
16. [Introduction to ABACUS: Path to PW calculation - Part 10](develop-path10.md)
17. [Introduction to ABACUS: Path to PW calculation - Part 11](develop-path11.md)
18. [Introduction to ABACUS: Path to PW calculation - Summary Final](develop-sm2.md)

