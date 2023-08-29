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

本教程系列旨在帮助新手用户入门了解 ABACUS 的使用。秉着开源软件的理念，本文档是由开源社区的老师同学们贡献所成。如果你也想贡献一份文档，我们十分欢迎，请参考[如何贡献ABACUS使用教程](abacus-contribute.md)。

本教程中标有<a href="" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a> Logo的部分可以直接在[Bohrium Notebook](https://nb.bohrium.dp.tech)上打开。

在Bohrium Notebook上快速学习，见[快速开始 ABACUS｜自洽 能带 态密度 结构优化](https://nb.bohrium.dp.tech/detail/4641406377)；在Bohrium平台上运行大任务，见[教程](https://bohrium-doc.dp.tech/docs/software/ABACUS/)。

# 二、ABACUS基本操作教程

1. ABACUS的编译介绍
   1. [官方编译教程](https://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html)
   2. [知乎上用户提供的ABACUS 3.0安装教程](https://zhuanlan.zhihu.com/p/574031713)
   3. [<mark style="color:red;">编译无MPI的ABACUS</mark>](https://xmywuqhxb0.feishu.cn/docx/JCv0dHPP6o69JdxtG33cIcTnnke)<mark style="color:red;"></mark>
   4. 曙光DCU平台编译教程：[ABACUS 在曙光 DCU 集群上的编译与使用](abacus-dcu.md)
2. ABACUS建模介绍
   1. 准备晶胞和原子位置等信息的文件STRU：[如何转换STRU的格式](https://nb.bohrium.dp.tech/detail/9814968648)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/9814968648" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
   2. 准备赝势：
   [模守恒赝势生成方法简介](abacus-upf.md)
   3. 数值原子轨道基组生成教程：
      1. [数值原子轨道（一）：ABACUS 中的数值原子轨道命名和使用方法](abacus-nac1.md)
      2. [数值原子轨道（二）：生成给定模守恒赝势的数值原子轨道](abacus-nac2.md)<a href="https://nb.bohrium.dp.tech/detail/5215642163" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
      3. [数值原子轨道（三）：产生高精度数值原子轨道](abacus-nac3.md)<a href="https://nb.bohrium.dp.tech/detail/8841868194" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
3. Kohn-Sham密度泛函理论
   1. [电子自洽迭代](https://nb.bohrium.dp.tech/detail/7417640496)<a href="https://nb.bohrium.dp.tech/detail/7417640496" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
   2. 带自旋的体系计算：[ABACUS磁性材料计算使用教程](https://nb.bohrium.dp.tech/detail/7141761751)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/7141761751" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
   3. \+U计算：[ABACUS DFT+U使用教程](https://nb.bohrium.dp.tech/detail/2112617648)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/2112617648" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
   4. 结构优化：[ABACUS 使用教程｜结构优化](https://nb.bohrium.dp.tech/detail/9119461238)<a href="https://nb.bohrium.dp.tech/detail/9119461238" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
   5. 分子动力学：[ABACUS 分子动力学使用教程](abacus-md.md)<a href="https://nb.bohrium.dp.tech/detail/2241262724" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
4. DeePKS方法（缺）
5. 隐式溶剂计算等相关功能（缺）
6. 随机波函数密度泛函理论：[ABACUS 随机波函数DFT方法使用教程](abacus-sdft.md)<a href="https://nb.bohrium.dp.tech/detail/5915692245" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
7. 无轨道密度泛函理论：[ABACUS 无轨道密度泛函理论方法使用教程](abacus-ofdft.md)<a href="https://nb.bohrium.dp.tech/detail/6416644691" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
8. 采用ABACUS进行表面计算
   1. [偶极修正](abacus-surface2.md)
9. 分析结果
   1. 能带计算
      1. [<mark style="color:red;">如何正确画能带，NSCF读电荷密度</mark>](https://xmywuqhxb0.feishu.cn/docx/K8GRdTst4oXQNoxnQVbcFZTmntb)<mark style="color:red;"></mark>
      2. [用ABACUS-ASE自动产生能带路径](https://nb.bohrium.dp.tech/detail/1211642609)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/1211642609" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
   2. PDOS计算
      1. [<mark style="color:red;">ABACUS里怎样做DOS和PDOS计算</mark>](https://xmywuqhxb0.feishu.cn/docx/ONSldj82VoNGKSxaoDQcoKBtnGh)<mark style="color:red;"></mark>
10. 和其他软件对接
    1. [ABACUS+Phonopy 计算声子谱](abacus-phonopy.md)<a href="https://nb.bohrium.dp.tech/detail/8741867512" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
    2. [ABACUS+ShengBTE 计算晶格热导率](abacus-shengbte.md)<a href="https://nb.bohrium.dp.tech/detail/2712467526" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
    3. [ABACUS+Phono3py 计算晶格热导率](https://nb.bohrium.dp.tech/detail/6116471155)<mark style="color:red;"></mark><a href="https://nb.bohrium.dp.tech/detail/6116471155" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
    4. [ABACUS+DPGEN 使用教程](abacus-dpgen.md)<a href="https://nb.bohrium.dp.tech/detail/6116401077" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
    5. [ABACUS+LibRI 做杂化泛函计算教程](abacus-libri.md)<a href="https://nb.bohrium.dp.tech/detail/8041860882" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
    6. [ABACUS+Candela 使用教程](abacus-candela.md)<a href="https://nb.bohrium.dp.tech/detail/2912697542" target="_blank"><img src="https://cdn.dp.tech/bohrium/web/static/images/open-in-bohrium.svg" alt="Open In Bohrium"/></a>
    7. ABACUS+CINEB教程（缺）
       1. [<mark style="color:red;">ABACUS-ASE做NEB计算</mark>](https://dptechnology.feishu.cn/wiki/wikcnzar41sN8ZtGLtm3PLnarSc) <mark style="color:red;"></mark> （简单算例）

# 三、使用经验

1. 有VASP使用背景的用户上手ABACUS教程：[<mark style="color:red;">ABACUS新人使用的一些注意事项</mark>](https://xmywuqhxb0.feishu.cn/docx/KN3KdqbX6o9S6xxtbtCcD5YPnue)<mark style="color:red;"></mark>
