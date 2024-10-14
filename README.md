# ABACUS使用教程

# 一、介绍

ABACUS（Atomic-orbtial Based Ab-initio Computation at UStc，中文名原子算筹）是国产开源密度泛函理论软件，相关介绍 ABACUS 的新闻可在[ABACUS 新闻稿整理](news.md)查看，以下是一些常用地址：

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
   3. [Intel oneAPI 2024.x 编译 ABACUS 教程](abacus-oneapi.md)
   4. [Intel oneAPI 编译 ABACUS 教程](abacus-intel.md)
   5. [编译 Nvidia GPU 版本的 ABACUS](abacus-gpu.md)
   6. [ABACUS LCAO 基组 GPU 版本使用说明](abacus-gpu-lcao.md)
   7. [在超算环境编译 ABACUS 的建议](abacus-hpc.md)
   8. [ABACUS 在曙光 DCU 集群上的编译与使用](abacus-dcu.md)
   9. [ABACUS toolchain 脚本集](https://github.com/deepmodeling/abacus-develop/tree/develop/toolchain) (md文档待整理)
   10. [ABACUS 编译教程系列之一：基于Intel编译器](https://www.bilibili.com/video/BV1ZN411L75Z/)（B站视频）
   11. [ABACUS 编译教程系列之二：基于CUDA](https://www.bilibili.com/video/BV1Jb4y1L7KB/)（B站视频）
   12. [ABACUS 编译教程系列之三：docker的使用](https://www.bilibili.com/video/BV13C4y1R7DL/)（B站视频）
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
   3. \+U计算：[ABACUS使用DFT+U计算教程 |基础版
](https://nb.bohrium.dp.tech/detail/52882361357)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/52882361357" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   4. 结构优化：[ABACUS 使用教程｜结构优化](https://nb.bohrium.dp.tech/detail/9119461238)<a href="https://nb.bohrium.dp.tech/detail/9119461238" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   5. [ABACUS 的平面波计算与收敛性测试](abacus-pw.md)
   6. 分子动力学：[ABACUS 分子动力学使用教程](abacus-md.md)<a href="https://nb.bohrium.dp.tech/detail/2241262724" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
4. DeePKS方法
   1. [DeePKS基础篇](https://nb.bohrium.dp.tech/detail/8742877753)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/8742877753" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
   2. [DeePKS案例篇 + 增强采样](https://nb.bohrium.dp.tech/detail/7144731675)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/7144731675" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
5. [ABACUS 隐式溶剂模型使用教程](abacus-sol.md)
6. 随机波函数密度泛函理论：[ABACUS 随机波函数DFT方法使用教程](abacus-sdft.md)<a href="https://nb.bohrium.dp.tech/detail/5915692245" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
7. 无轨道密度泛函理论：[ABACUS 无轨道密度泛函理论方法使用教程](abacus-ofdft.md)<a href="https://nb.bohrium.dp.tech/detail/6416644691" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
8. [ABACUS 实时演化含时密度泛函理论使用教程](abacus-tddft.md)
9. 采用ABACUS进行表面计算
   1. [静电势和功函数](abacus-surface1.md)
   2. [偶极修正](abacus-surface2.md)
   3. [表面能计算](abacus-surface3.md)
   4. [表面缺陷能和吸附能计算](abacus-surface4.md)
   5. [外加电场](abacus-surface5.md)
   6. [补偿电荷](abacus-surface6.md)
10. 分析结果
   1. 能带计算：[ABACUS+Atomkit 计算态密度和能带](abacus-dos.md)
   2. PDOS计算：[ABACUS 计算 PDOS](abacus-pdos.md)
   3. [ABACUS 输出部分的电荷密度和波函数及可视化教程](abacus-chg.md)
   4. [ABACUS 计算电子局域函数 ELF 使用教程](abacus-elf.md)
11. 和其他软件对接
    1. [ABACUS+Phonopy 计算声子谱](abacus-phonopy.md)<a href="https://nb.bohrium.dp.tech/detail/8741867512" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    2. [ABACUS+ShengBTE 计算晶格热导率](abacus-shengbte.md)<a href="https://nb.bohrium.dp.tech/detail/2712467526" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    3. [ABACUS+Phono3py 计算晶格热导率](https://nb.bohrium.dp.tech/detail/6116471155)<a href="https://nb.bohrium.dp.tech/detail/6116471155" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    4. [ABACUS+DPGEN 使用教程](abacus-dpgen.md)<a href="https://nb.bohrium.dp.tech/detail/6116401077" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    5. [ABACUS+LibRI 做杂化泛函计算教程](abacus-libri.md)<a href="https://nb.bohrium.dp.tech/detail/8041860882" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    6. [ABACUS+Candela 使用教程](abacus-candela.md)<a href="https://nb.bohrium.dp.tech/detail/2912697542" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    7. [ABACUS+USPEX 接口教程](abacus-uspex.md)
    8. [ABACUS+Hefei NAMD 使用教程](abacus-namd.md)
    9. [ABACUS+Wannier90 使用教程](abacus-wannier.md)
    10. [ABACUS+pymatgen 计算弹性常数](abacus-elastic.md)
    11. [ABACUS+Bader charge 分析教程](abacus-bader.md)
    12. [ABACUS+pyatb 能带反折叠计算](https://nb.bohrium.dp.tech/detail/2012704420)<a href="https://nb.bohrium.dp.tech/detail/2012704420" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    13. [ABACUS+DeepH 建立碳材料的哈密顿量模型](https://nb.bohrium.dp.tech/detail/6242632169)<a href="https://nb.bohrium.dp.tech/detail/6242632169" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
    14. [ABACUS+ASE接口使用技巧](https://bbs.abacus-dft.com/forum.php?mod=viewthread&tid=4&extra=page%3D1)
    15. ABACUS+ASE 做过渡态计算
        1. [ATST-Tools: ASE-ABACUS过渡态计算工作流套件与算例](https://github.com/QuantumMisaka/ATST-Tools)<a href="https://nb.bohrium.dp.tech/detail/39369325971" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a> 支持NEB，Dimer，AutoNEB等过渡态方法。
        2. [<mark style="color:red;">ABACUS-ASE做NEB计算</mark>](https://dptechnology.feishu.cn/wiki/wikcnzar41sN8ZtGLtm3PLnarSc) <mark style="color:red;"></mark> （简单算例）
    16. ABACUS+ASE 遗传算法 （暂缺，待更新）

# 三、使用经验

1. [ABACUS 答疑手册](abacus-question.md)
2. [ABACUS 收敛性问题解决手册](abacus-conv.md)
3. [ABACUS计算模拟实例 | 概述](https://bohrium.dp.tech/notebooks/93842852314)<a href="https://bohrium.dp.tech/notebooks/93842852314" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
4. [ABACUS计算模拟实例 | I. 原子及小分子气体能量计算](https://bohrium.dp.tech/notebooks/81868491785)<a href="https://bohrium.dp.tech/notebooks/81868491785" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
5. [ABACUS计算模拟实例 | II. C2H5OH的振动模式与频率计算](https://bohrium.dp.tech/notebooks/52515261357)<a href="https://bohrium.dp.tech/notebooks/52515261357" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
6. [ABACUS计算模拟实例 | III. 材料平衡晶格常数计算](https://bohrium.dp.tech/notebooks/24564476824)<a href="https://bohrium.dp.tech/notebooks/24564476824" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
7. [ABACUS计算模拟实例 | IV. 堆垛层错能的计算](https://bohrium.dp.tech/notebooks/57232361357)<a href="https://bohrium.dp.tech/notebooks/57232361357" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
8. [ABACUS计算模拟实例 | V. Al的弹性性能指标计算](https://bohrium.dp.tech/notebooks/73791986918)<a href="https://bohrium.dp.tech/notebooks/73791986918" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
9. [ABACUS计算模拟实例 | VI. 空位形成能与间隙能计算](https://bohrium.dp.tech/notebooks/97738352314)<a href="https://bohrium.dp.tech/notebooks/97738352314" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
10. [2024秋计算材料学-上机练习：ABACUS能带和态密度计算](https://bohrium.dp.tech/notebooks/21913576824)<a href="https://bohrium.dp.tech/notebooks/21913576824" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
11. [ABACUS计算模拟实例 | VIII. 基于HSE06的态密度与能带计算](https://bohrium.dp.tech/notebooks/58898161357)<a href="https://bohrium.dp.tech/notebooks/58898161357" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
12. [ABACUS计算模拟实例 | IX. 表面能的计算](https://bohrium.dp.tech/notebooks/45588412168)<a href="https://bohrium.dp.tech/notebooks/45588412168" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
13. [ABACUS计算模拟实例 | XI. Pt表面简单物种的吸附能计算](https://bohrium.dp.tech/notebooks/15517833825)<a href="https://bohrium.dp.tech/notebooks/15517833825" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
14. [ABACUS计算模拟实例 | XII. Pt(111)表面羟基解离的过渡态搜索](https://bohrium.dp.tech/notebooks/36595625971)<a href="https://bohrium.dp.tech/notebooks/36595625971" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
15. [ABACUS计算模拟实例 | XIII. Pt表面的ORR催化路径](https://bohrium.dp.tech/notebooks/49942212168)<a href="https://bohrium.dp.tech/notebooks/49942212168" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
16. [ABACUS对比CP2K精度和效率测试 | Si的状态方程（EOS）](https://bohrium.dp.tech/notebooks/77351186918)<a href="https://bohrium.dp.tech/notebooks/77351186918" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" /></a>
17. 有VASP使用背景的用户上手ABACUS教程：[<mark style="color:red;">ABACUS新人使用的一些注意事项</mark>](https://xmywuqhxb0.feishu.cn/docx/KN3KdqbX6o9S6xxtbtCcD5YPnue)<mark style="color:red;"></mark>

# 四、开发者文档

1. [ABACUS 开源项目 C++ 代码规范](develop-C++.md)
2. [ABACUS 中使用格式化工具 clang-format](develop-format.md)
3. [ABACUS 注释规范：Doxygen 入门 (c++)](develop-dox.md)
4. [ABACUS 的 Github 仓库 Issues 处理流程](develop-issue.md)
5. [ABACUS 线上文档输入参数撰写规范](develop-input.md)
6. [ABACUS 代码存放规范](develop-rule.md)
7. [ABACUS formatter-2.0 版本使用说明书](develop-formatter2.md)
8. [ABACUS 全局数据结构和代码行数检测](develop-linedete.md)
9. [性能分析工具：vtune 快速上手教程](develop-vtune.md)
10. [以格点积分程序为例：一些代码开发习惯小贴士](develop-grid.md)
11. [ABACUS 中的测试（一）：测试的重要性](develop-test1.md)
12. [ABACUS 中的测试（二）：测试工具 gtest](develop-test2.md)
13. [Introduction to ABACUS: Path to PW calculation - Part 1](develop-path1.md)
14. [Introduction to ABACUS: Path to PW calculation - Part 2](develop-path2.md)
15. [Introduction to ABACUS: Path to PW calculation - Part 3](develop-path3.md)
16. [Introduction to ABACUS: Path to PW calculation - Part 4](develop-path4.md)
17. [Introduction to ABACUS: Path to PW calculation - Part 5](develop-path5.md)
18. [Introduction to ABACUS: Path to PW calculation - Summary 1](develop-sm1.md)
19. [Introduction to ABACUS: Path to PW calculation - Part 6](develop-path6.md)
20. [Introduction to ABACUS: Path to PW calculation - Part 7](develop-path7.md)
21. [Introduction to ABACUS: Path to PW calculation - Part 8](develop-path8.md)
22. [Introduction to ABACUS: Path to PW calculation - Part 9](develop-path9.md)
23. [Introduction to ABACUS: Path to PW calculation - Part 10](develop-path10.md)
24. [Introduction to ABACUS: Path to PW calculation - Part 11](develop-path11.md)
25. [Introduction to ABACUS: Path to PW calculation - Summary Final](develop-sm2.md)
26. [如何在 ABACUS 中新增一个输入参数（v3.7.0 后）](develop-addinp2.md)
27. [如何在 ABACUS 中新增一个输入参数（截至 v3.5.3）](develop-addinp.md)
28. [C++ 程序设计的一些想法](develop-design.md)
29. [文件输出功能的实现代码结构设计建议：以 ABCUS CifParser 为例](develop-cifparser.md)

# 五、算法文档

1. [最大局域化 Wannier 函数方法简介](algorithm-wannier.md)
2. [电荷密度混合算法介绍](algorithm-mix.md)
3. [在 ABACUS 中进行差分测试](algorithm-delta.md)
