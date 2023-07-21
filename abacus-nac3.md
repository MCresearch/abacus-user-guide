# 数值原子轨道（三）：产生高精度数值原子轨道

<strong>作者：刘裕，邮箱：liuyu@stu.pku.edu.cn </strong>

<strong>审核：林霈泽，邮箱：linpeize@sslab.org.cn</strong>

<strong>最后更新时间：2023/06/20</strong>

# 一、PTG（PyTorch Gradient）方法

这篇文档是数值原子轨道系列的第三篇文档，除了第二篇文档提到的模拟退火算法之外，还可以使用 Pytorch 中的自动微分算法来最小化溢出函数。首先定义损失函数如下，并可以证明它与溢出函数是等价的：

$$
\Delta \mathrm{PSI} \stackrel{\text { def }}{=} \frac{1}{N_n} \sum_{n=1}^{N_m} \|\left|\Psi_n\right\rangle-\left|\tilde{\Psi}_n\right\rangle \|^2,
$$

其中

$$
\left|\tilde{\Psi}_n\right\rangle \stackrel{\text { def }}{=} \hat{P}\left|\Psi_n\right\rangle,
$$

且$$\hat{P}$$是由所有原子轨道张成的投影子，即$$\hat{P}=\sum_{\mu v}\left|\phi_\mu\right\rangle S_{\mu v}^{-1}\left\langle\phi_v\right| \text {}$$。由 $$\hat{P}^2=\hat{P}$$及 $$\left\langle\Psi_n|\Psi_n\right\rangle=\delta_{mn}$$可知，此处的损失函数$$\Delta \mathrm{PSI}$$与溢出函数是等价的。

# 二、PTG_dpsi（PyTorch Gradient with dpsi）方法

为了增加局域轨道做电子结构计算时的精度，损失函数的定义还可以被拓展，即在其中加入波函数的梯度，将总的损失函数定义为：

$$
\Delta \mathrm{PSI} \stackrel{\text { def }}{=} \frac{1}{N_n} \sum_{n=1}^{N_m} [\|\left|\Psi_n\right\rangle-\left|\tilde{\Psi}_n\right\rangle \|^2+\|\left|\nabla\Psi_n\right\rangle-\left|\nabla\tilde{\Psi}_n\right\rangle \|^2].
$$

由于投影波函数$$\left|\tilde{\Psi}_{n}\right\rangle$$是数值原子轨道的线性组合：

$$
\left|\tilde{\Psi}_{n}\right\rangle=\sum_{\mu} a_{\mu n}\left|\phi_{\mu}\right\rangle,
$$

其中系数的表达式为

$$
a_{\mu n}=\sum_{\nu} S_{\mu \nu}^{-1}\left\langle\phi_{\nu} \mid \Psi_{n}\right\rangle.
$$

那么投影波函数的梯度可以表示为数值原子轨道梯度的线性组合：

$$
\left|\nabla \tilde{\Psi}_{n}\right\rangle=\sum_{\mu} a_{\mu n}\left|\nabla \phi_{\mu}\right\rangle.
$$

因此，损失函数的梯度项可以转化为：

$$
\begin{array}{l} 
\|\left|\nabla \Psi_{n}\right\rangle-\left|\nabla \tilde{\Psi}_{n}\right\rangle \|^{2} \\
=\left\langle\nabla \Psi_{n} \mid \nabla \Psi_{n}\right\rangle-\sum_{\mu} a_{\mu n}\left\langle\nabla \Psi_{n} \mid \nabla \phi_{\mu}\right\rangle \\
-\sum_{\nu} a_{v n}^{*}\left\langle\nabla \phi_{v} \mid \nabla \Psi_{n}\right\rangle+\sum_{\mu \nu} a_{\mu n} a_{v n}^{*}\left\langle\nabla \phi_{v} \mid \nabla \phi_{\mu}\right\rangle.
\end{array}
$$

根据经验，使用这个算法生成的双重-ζ + 极化(DZP)基组，精度与模拟退火法或 PTG 法生成的三重-ζ + 双极化(TZDP)甚至四倍-ζ + 三重极化(QZTP)基组相当。

在平面波计算中，除了[数值原子轨道（二）：生成给定模守恒赝势的数值原子轨道](abacus-nac2.md) 提到的 overlap 输出文件 `OUT.${suffix}/orb_matrix.0.dat` 之外，overlap 输出文件 `OUT.${suffix}/orb_matrix.1.dat` 同样会作为生成轨道的输入文件之一，该文件保存与波函数梯度相关的如下 overlap 项：

1）电子波函数梯度$$|\nabla \Psi_i\rangle$$和局域轨道梯度$$|\nabla \phi_\mu\rangle$$的 overlap，也就是电子波函数梯度$$|\nabla \Psi_i\rangle$$以及球贝塞尔函数梯度$$\nabla j_l(q r)$$之间的 overlap$$\langle \nabla \Psi_i|\nabla j_l(q r)\rangle$$；

2）球贝塞尔函数梯度$$\nabla j_l(q r)$$之间的 overlap$$\langle \nabla j_{l_2}(q_2 r)|\nabla j_{l_1}(q_1 r)\rangle$$；

3）电子波函数梯度$$|\nabla \Psi_i\rangle$$之间的 overlap$$\langle \nabla \Psi_i|\nabla \Psi_i\rangle$$。

# 三、安装 Pytorch

PTG 和 PTG_dpsi 方法采用 python 语言，无需编译，但是依赖 pytorch 包，下面介绍利用 conda 安装 pytorch 的方法：

```bash
# 确定conda版本
$ conda -V
conda 4.8.3

# 确定python3版本
$ python3 -V
Python 3.5.2

# 创建python环境
$ conda create -n pytorch python=3.5

# 激活环境（每次使用pytorch需要激活该环境）
$ source activate pytorch

# 安装pytorch
$ conda install pytorch torchvision torchaudio cpuonly -c pytorch

# 安装依赖库
$ pip3 install --user scipy numpy
$ pip3 install --user torch_optimizer

# 退出python环境（使用完毕后）
$ source deactivate
```

# 四、产生高精度数值原子轨道流程

首先下载 PTG_dpsi 仓库

```bash
# github仓库
git clone -b main https://github.com/abacusmodeling/ABACUS-orbitals
```

接着准备输入文件 `SIAB_INPUT`

```bash
#--------------------------------------------------------------------------------
#1. CMD & ENV
EXE_mpi    mpirun -np 4
EXE_pw     /home/liuyu/github/abacus-develop/build/abacus
EXE_opt    /home/liuyu/github/ABACUS-orbitals/SIAB/opt_orb_pytorch_dpsi/main.py
#-------------------------------------------------------------------------------- 
#2. Electronic calculatation
 element     Si          # Element Name
 Ecut        100         # in Ry
 Rcut        6 7         # in Bohr
 Pseudo_dir  /home/liuyu/github/abacus-develop/tests/PP_ORB
 Pseudo_name Si_ONCV_PBE-1.0.upf 
 sigma       0.01        # energy range for gauss smearing (in Ry) 

#--------------------------------------------------------------------------------
#3. Reference structure related parameters for PW calculation
#For the built-in structure types (including 'dimer', 'trimer' and 'tetramer'):
#STRU Name   #STRU Type  #nbands #MaxL   #nspin  #Bond Length list
 STRU1       dimer       8       2       1       1.8 2.0 2.3 2.8 3.8
 STRU2       trimer      10      2       1       1.9 2.1 2.6

#-------------------------------------------------------------------------------- 
#4. SIAB calculatation
 max_steps    200
# Orbital configure and reference target for each level
#LevelIndex   #Ref STRU Name    #Ref Bands   #InputOrb    #OrbitalConf
 Level1       STRU1             4            none         1s1p      
 Level2       STRU1             4            fix          2s2p1d    
 Level3       STRU2             6            fix          3s3p2d    

#--------------------------------------------------------------------------------
#5. Save Orbitals
#Index       #LevelNum    #OrbitalType
 Save1       Level1       SZ           
 Save2       Level2       DZP         
 Save3       Level3       TZDP
```

该输入文件同样包含 5 个部分：

## 1. CMD & ENV

- EXE_mpi：MPI 并行计算命令，这里我们采用的是 4 核 MPI 并行进行 dimer（或者 trimer）的平面波计算。
- EXE_pw：ABACUS 可执行程序的绝对路径。
- EXE_opt：数值原子轨道生成程序 PTG_dpsi 的绝对路径。

## 2. Electronic calculatation

- element：元素名。
- Ecut：平面波截断能，单位为 Ry。
- Rcut：数值原子轨道的截断半径，单位为 Bohr。这里的多个取值表明，采用相同的一套参数，生成多个不同截断半径的数值原子轨道文件，根据第一部分的基础知识，截断半径会极大地影响数值原子轨道的质量，因此该参数可以帮助我们一次性生成多个不同截断半径的数值原子轨道文件。
- Pseudo_dir：平面波计算采用的赝势文件所在文件夹的绝对路径。
- Pseudo：平面波计算采用的赝势文件名。
- sigma：平面波计算采用 Gaussian smearing 的展宽，单位为 Ry，一般取 0.01 即可。

## 3. Reference structure related parameters for PW calculation

- STRU Name：参考构型组别 STRU1、STRU2、STRU3......
- STRU Type：参考体系构型，一般可取 dimer，trimer，tetramer。
- nbands：平面波计算中的实际能带数，必须保证包含非占据态。
- MaxL：最大角动量。
- nspin：自旋量子数。
- Bond Length list：键长取值列表，单位为埃。以 STRU1 为例，这一组共有 5 个不同键长的 dimer 作为生成轨道的参考构型。

## 4. SIAB calculatation

- max_steps：优化步数
- LevelIndex：轨道分层的 index，取 Level1、Level2、Level3......
- Ref STRU Name：该层级的轨道采用哪一组参考构型生成。以上面的输入参数为例，Level1 和 Level2 的轨道采用 STRU1 组别的 dimer 参考构型生成，Level3 的轨道采用 STRU2 组别的 trimerr 参考构型生成。
- Ref Bands：拟合参考体系的能带数，若输入“auto”则自动拟合所有基态。
- InputOrb：是否在已有的轨道基础上生成新轨道，一般 Level1 设为 none，即没有旧轨道；Level2 一般以 Level1 生成的轨道为基础继续生成轨道，Level3 往后同理。
- OrbitalConf：轨道的具体配置，这里 Level1 是 SZ 层级，Level2 是 DZP 层级，Level3 是 TZDP 层级，实际上还可以继续设置更高层级的轨道。

## 5. Save Orbitals

- Index：取值 Save1、Save2、Save3......
- LevelNum：将特定 Level 的轨道保存到一个轨道文件中。以上面的输入参数为例，分别将 Level1、Level2、Level3 对应的轨道保存到单独的轨道文件中。
- OrbitalType：即保存的轨道文件中，该轨道基组所属的层级。以上面的输入参数为例，分别为 SZ、DZP、TDZP。

准备好输入参数文件 `SIAB_INPUT` 后，运行如下命令即可开始生成轨道：

```bash
$ python3 ~/github/ABACUS-orbitals/SIAB/SIAB.py SIAB_INPUT
```

程序正常结束后，轨道会分别保存在 `Orbital_Si_SZ`、`Orbital_Si_DZP`、`Orbital_Si_TZDP` 中，并自动命名成标准格式（如 Si_gga_6au_100Ry_2s2p1d.orb）。

# 五、参考文献

[1]   Peize Lin, Xinguo Ren and Lixin He, <em>Strategy for constructing compact numerical atomic orbital basis sets by incorporating the gradients of reference wavefunctions, </em>Phys. Rev. B <strong>103, </strong>235131 (2021).
