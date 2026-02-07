# ABACUS 平面波 KSDFT 电子电导热导计算教程

**作者：任泓旭，邮箱：rhx0820@stu.pku.edu.cn**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2026/02/07**

# 一、介绍

对于物质的电导率和热导率性质，一般可以分成电子和离子贡献，离子部分贡献目前已有较成熟的算法，特别是可以借助机器学习势函数加速计算。对于电子贡献的部分，则可以使用 [Kubo](https://journals.jps.jp/doi/10.1143/JPSJ.12.570)-[Greenwood](https://iopscience.iop.org/article/10.1088/0370-1328/71/4/306) 的公式进行计算[[Phys. Rev. B 83, 235120 (2011)](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.83.235120)]，该方法已被应用于液态金属、温稠密(Warm Dense matter, WDM)等物质的计算。Kubo-Greenwood 通过直接计算含频的昂萨格系数$$L_{mn}(\omega)$$，来计算电子的电导与热导：

$$
L_{mn}(\omega)=(-1)^{m+n}\frac{2\pi e^2}{3\omega\Omega}\\
\times\sum_{ij\alpha\mathbf{k}}W(\mathbf{k})\left(\frac{\epsilon_{i\mathbf{k}}+\epsilon_{j\mathbf{k}}}{2}-\mu\right)^{m+n-2} |\langle\Psi_{i\mathbf{k}}|\hat{v}_\alpha|\Psi_{j\mathbf{k}}\rangle|^2[f(\epsilon_{i\mathbf{k}})-f(\epsilon_{j\mathbf{k}})]\delta(\epsilon_{j\mathbf{k}}-\epsilon_{i\mathbf{k}}-\hbar\omega),
$$

这里的 n,m 指标取值范围为 1, 2， $$\Omega$$为体积，$$W(\mathbf{k})$$为 k 点的权重，$$\varepsilon_{i\mathbf{k}}$$为第 i 个波函数$$|{\Psi_{ik}}$$对应的本征能量， $$f(\varepsilon)=\frac{1}{1+\exp(\frac{\varepsilon-\mu}{kT})}$$为费米狄拉克分布，$$\mu$$为化学势，$$\delta(x)$$为 delta 函数，在实际计算中 delta 函数可以用高斯函数$$G(x)=\frac{1}{\sqrt{2\pi}s}\exp\left(-\frac{x^2}{2s^2}\right)$$或洛伦兹函数$$L(x)=\frac{1}{\pi}\frac{\gamma}{x^2+\gamma^2}$$代替，$$\hat{v}_{\alpha}$$为速度算符的第$$\alpha$$个分量$$(\alpha=x,y,z)$$对于速度算符，速度算符的定义为$$\hat{v}=\frac{i}{\hbar}[\hat{H},\hat{r}]$$。

含频电导$$\sigma(\omega)=L_{11}(\omega)$$，直流电导$$\sigma_0=\lim_{\omega\to0}\sigma(\omega)$$

含频热导$$\kappa(\omega)=\frac{1}{e^2T}\left(L_{22}-\frac{L^2_{12}}{L_{11}}\right)$$, 热导$$\kappa_0=\lim_{\omega\to0}(\omega)$$

通过 KSDFT 求解的波函数、本征能量，可以轻易的带入公式进行计算。

ABACUS 同时实现了基于 sDFT（Stochastic Density Functional Theory，随机波函数密度泛函理论）的 Kubo-Greenwood 方法，在温度高于 20 eV 的场景下效率更高。具体可参考 [ABACUS 随机波函数 DFT 计算电子电导热导教程 · GitBook](https://mcresearch.github.io/abacus-user-guide/abacus-sdft_cond.html)

# 二、采用 KSDFT 进行电子的电导热导计算

## 1. 输入文件

在电导热导计算中，包含布里渊区 K 点的 `KPT` 文件和包含原子位置的 `STRU` 文件与传统的 KSDFT 计算并无区别，主要的不同在于输入文件 `INPUT`。为了计算电导热导，我们只需要把 `cal_cond` 参数打开即可，INPUT 文件如下：

```bash
INPUT_PARAMETERS 
#Parameters     (General) 
calculation     scf 
pseudo_dir      . 
#Parameters     (Accuracy) 
ecutwfc         60    
scf_thr         1e-8 
symmetry        0 
#Parameters     (Smearing) 
smearing_method fd 
smearing_sigma  0.0304014440309863  # Rydberg 
#Parameters (MD) 
basis_type      pw  
nspin           1 

#Parameters (6.Conductivity) 
cal_cond         1 
cond_fwhm        0.05 
cond_wcut        10 
cond_dw          0.2 
cond_dt          0.1 
cond_nonlocal    true
```

以上参数在 ABACUS 的[线上文档](http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#electronic-structure-sdft)中均有详细说明，这里再进行简单概述：

- **cal_cond**: 控制是否计算电子贡献的电导热导
- **cond_smear**: 设置展宽类型，1：高斯展宽（默认），2：洛伦兹展宽
- **cond_fwhm**: 设置半高宽 FWHM，对于高斯展宽, $$\mathrm{FWHM}=2\sqrt{2\ln2}s$$; 对于洛伦兹展宽 $$\mathrm{FWHM}=2\gamma$$.
- **cond_wcut**: 计算频率的截断值，决定输出含频数据的频率范围, 单位: eV
- **cond_dw**: 频率的间隔，单位:eV
- **cond_dt**: 对响应函数积分时的积分间隔，原子单位 a.u.
- **cond_nonlocal**: 是否使用速度算符的非局域赝势修正，`true`：修正，`false`：不修正，默认为 `true`。更多信息可参考 [Phys. Rev. B 110, 014207](https://doi.org/10.1103/PhysRevB.110.014207)。

此外，将 **smearing_method** 设为 **fd** 和 **smearing_sigma** 设为温度（单位为 Rydberg）可以实现有限温度下的电子电导热导模拟。完整的算例可以在 [https://github.com/MCresearch/abacus-user-guide/tree/master/examples/ks_cond](https://github.com/MCresearch/abacus-user-guide/tree/master/examples/ks_cond) 中找到。

**计算时间的说明：**

- KSDFT 下 Kubo-Greenwood 方法计算电导热导的计算时间对 `cond_dt` 相对不敏感，建议取得尽可能小一些直至收敛。
- 相较于 sDFT，KSDFT 的 Kubo-Greenwood 方法不涉及切比雪夫展开和 `cond_dtbatch` 参数。

## 2. 输出

注：以下结果仅供参考，最终结果以最新版本计算输出为准。

- 对于 **LTS** 版本，响应函数和昂萨格系数输出至对应输入文件所在目录；
- 对于 **develop** 版本，响应函数和昂萨格系数统一输出至默认输出目录。（文档撰写时，最新的 **develop** 版本为 3.9.0.24。）
- 本文所列结果基于 **LTS v3.10.1** 版本运行得到。

### a. 屏幕输出

```bash
Calculating conductivity....
nw: 50 ; dw: 0.2 eV                              总频率数，频率间隔
nt: 43460 ; dt: 0.1 a.u.(ry^-1)                  总时间数，时间间隔
Recommended dt: 1.06327 a.u. 
DC electrical conductivity: -410750 Sm^-1        直流电导值（直接线性外推的简单估计值，实际需要根据含频电导拟合外推）
Thermal conductivity: 27.0337 W(mK)^-1           热导值
Lorenz number: -1.84646 k_B^2/e^2                洛伦兹常数
```

### b. je-je.txt

```bash
#t(a.u.)         c11(t)         c12(t)         c22(t)          decay 
       0             -0             -0             -0              1 
     0.1     -0.0294619     0.00509203    -0.00117584              1 
     0.2     -0.0588492      0.0101685    -0.00234789              1 
     0.3     -0.0880875       0.015214    -0.00351237              1 
     0.4      -0.117103       0.020213    -0.00466553              1 
     0.5      -0.145823      0.0251505    -0.00580368              1 
     0.6      -0.174174      0.0300114    -0.00692316              1 
     0.7      -0.202088       0.034781    -0.00802041       0.999999 
     0.8      -0.229493      0.0394451    -0.00909192       0.999999
```

储存响应函数的文件，各列分别为均为原子单位，时间 t, 响应函数$$C_{11}(t), C_{12}(t), C_{22}(t)$$, 窗函数

### c. Onsager.txt

```bash
## w(eV)         sigma(Sm^-1)     kappa(W(mK)^-1)        L12/e(Am^-1)      L22/e^2(Wm^-1) 
     0.1              424701             132.163             64877.9              644295 
     0.3              702565              47.104            -14780.7              226411 
     0.5         1.05583e+06             204.219              300223         1.06562e+06 
     0.7              715223             44.6657              169304              254472 
     0.9             41811.5             8.79352             20755.9             52512.6 
     1.1              466320             77.0295              140156              411867 
     1.3              538842             27.2582             -228481              227721 
     1.5              244561             23.5012              143053              196483 
     1.7             9128.47           0.0162282            -23180.6             58941.9
```

储存昂萨格系数的文件，各列分别为频率，电导，热导，$$L_{12}(\omega), L_{22}(\omega)$$

### d. vmatrix*.dat

二进制文件，输出至默认输出目录，用于存储速度矩阵$$\langle\Psi_{i\mathbf{k}}|\hat{v}_\alpha|\Psi_{j\mathbf{k}}\rangle$$，可作为中间变量快速计算电子电导热导，其具体使用方法将在下一节中介绍。

## 使用速度矩阵计算电子电导热导

前文已提到，为实现收敛往往需要调节 **cond_fwhm** 等参数，可能需要多次重新计算电导。若每次从头运行自洽迭代计算，将造成不必要的时间开销；若通过保存波函数来避免重复计算，则会带来较大的存储开销。

ABACUS 打开 **cal_cond** 开关时会生成 vmatrix*.dat，可用于外部软件 Candela 在不重新运行 SCF、也不保存波函数的情况下，仅通过调整运行参数重新计算电导。Candela 的安装请参考 [https://github.com/MCresearch/Candela](https://github.com/MCresearch/Candela) 和 [ABACUS+Candela 使用教程 · GitBook](https://mcresearch.github.io/abacus-user-guide/abacus-candela.html)。

可以在示例输入如下：

```bash
calculation ele_conductivity 
wf_in_type ABACUS 
wfdirectory OUT.ABACUS 

dw 0.1                        # 和ABACUS的cond_dw相同
wcut 10                       # 和ABACUS的cond_wcut相同
smear 1                       # 和ABACUS的cond_smear相同
fwhm 0.01                     # 和ABACUS的cond_fwhm相同 
cond_method 1
readvmatrix 1                 # 关键！
temperature 4800              # 单位为K
```

Candela 采用与 ABACUS 不同但数学上等价的方式计算电导，不需要设置 **cond_dt**。

> 经测试，ABACUS 最后兼容该功能的版本为 3.4.2，自 3.4.3 版本开始，输出文件的格式有大幅修改，目前所有 LTS 版本和最新的 develop 版本都暂不支持这一功能。
