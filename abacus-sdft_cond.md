# ABACUS 随机波函数 DFT 计算电子电导热导教程

<strong>作者：刘千锐，邮箱：terry_liu@pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2024/10/15</strong>

# 一、介绍

对于物质的电导热导，一般可以分成电子和离子贡献，而对于电子贡献的部分可以使用 [Kubo](https://journals.jps.jp/doi/10.1143/JPSJ.12.570)-[Greenwood](https://iopscience.iop.org/article/10.1088/0370-1328/71/4/306) 的公式进行计算[[Phys. Rev. B 83, 235120 (2011)](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.83.235120)]，该方法已被广泛应用于液态金属、温稠密(Warm Dense matter, WDM)等物质的计算。Kubo-Greenwood 通过直接计算含频的昂萨格系数$$L_{mn}(\omega)$$，来计算电子的电导与热导：

$$
L_{mn}(\omega)=(-1)^{m+n}\frac{2\pi e^2}{3\omega\Omega}\\
\times\sum_{ij\alpha\mathbf{k}}W(\mathbf{k})\left(\frac{\epsilon_{i\mathbf{k}}+\epsilon_{j\mathbf{k}}}{2}-\mu\right)^{m+n-2} |\langle\Psi_{i\mathbf{k}}|\hat{v}_\alpha|\Psi_{j\mathbf{k}}\rangle|^2[f(\epsilon_{i\mathbf{k}})-f(\epsilon_{j\mathbf{k}})]\delta(\epsilon_{j\mathbf{k}}-\epsilon_{i\mathbf{k}}-\hbar\omega),
$$

这里的 n,m 指标取值范围为 1, 2， $$\Omega$$为体积，$$W(\mathbf{k})$$为 k 点的权重，$$\varepsilon_{i\mathbf{k}}$$为第 i 个波函数$$\left | \Psi_{ik}  \right \rangle$$对应的本征能量， $$f(\varepsilon)=\frac{1}{1+\exp(\frac{\varepsilon-\mu}{kT})}$$为费米狄拉克分布，$$\mu$$为化学势，$$\delta(x)$$为 delta 函数，在实际计算中 delta 函数可以用高斯函数$$G(x)=\frac{1}{\sqrt{2\pi}s}\exp\left(-\frac{x^2}{2s^2}\right)$$或洛伦兹函数$$L(x)=\frac{1}{\pi}\frac{\gamma}{x^2+\gamma^2}$$代替，$$\hat{v}_{\alpha}$$为速度算符的第$$\alpha$$个分量$$(\alpha=x,y,z)$$对于速度算符，速度算符的定义为$$\hat{v}=\frac{i}{\hbar}[\hat{H},\hat{r}]$$。

含频电导$$\sigma(\omega)=L_{11}(\omega)$$，直流电导$$\sigma_0=\lim_{\omega\to0}\sigma(\omega)$$

含频热导$$\kappa(\omega)=\frac{1}{e^2T}\left(L_{22}-\frac{L^2_{12}}{L_{11}}\right)$$, 热导$$\kappa_0=\lim_{\omega\to0}(\omega)$$

以上便是传统 KSDFT 计算的方法，通过 KSDFT 求解的波函数、本征能量，可以轻易的带入公式进行计算。

对于随机波函数密度泛函理论(sDFT)，其没有波函数、本征能量不能通过该方法进行计算。而应从原始的 [Kubo](https://journals.jps.jp/doi/10.1143/JPSJ.12.570) 公式中出发：

电流、热流响应函数：$$C_{mn}(t)=-2\theta(t)\Im\left\{Tr\left[\sqrt{\hat f}\hat{j}_m(1-\hat{f})e^{i\frac{\hat{H}}{\hbar}t}\hat{j}_ne^{-i\frac{\hat{H}}{\hbar}t}\sqrt{\hat f}\right]\right\}$$, 这里$$\theta(x)$$为阶跃函数，$$\Im$$为取虚部，$$\hat{f}=\frac{1}{1+\exp(\frac{\hat{H}-\mu}{kT})}$$为费米狄拉克算符，$$\hat{j}_1=e\hat{v}$$为电流算符，$$\hat{j}_2=(\hat{v}\hat{H}+\hat{H}\hat{v})/2-\mu\hat{v}$$为热流算符，$$e^{-i\hat{H}t/\hbar}$$为演化算符。这里求迹便可通过随机波函数进行计算。

而昂萨格系数就可通过响应函数的傅里叶变换进行计算：$$L_{mn}=\frac{2e^{m+n-2}}{3\Omega\hbar\omega}\Im[\tilde{C}_{mn}(\omega)]$$，这里计算$$\tilde{C}_{mn}(\omega)$$可以使用不同的窗函数：

高斯型：$$\tilde{C}_{mn}(\omega)=\int_0^\infty C_{mn}(t)e^{-i\omega t}e^{-\frac{1}{2}s^2t^2}dt$$

洛伦兹型：$$\tilde{C}_{mn}=\int_0^\infty C_{mn}(t)e^{-i\omega t}e^{-\gamma t}dt$$

其分别与前面提到的高斯函数$$G(x)$$和洛伦兹函数$$L(x)$$对应。

# 二、算例准备

下载链接：

[https://github.com/MCresearch/abacus-user-guide/tree/master/examples/stochastic/cond_Si](https://github.com/MCresearch/abacus-user-guide/tree/master/examples/stochastic/cond_Si)

# 三、采用 sDFT 进行电子的电导热导计算

## 1. 输入文件

`cond_Si` 文件夹：这是一个电子温度为 0.6 Ry（约 8.16 eV）的 单原子硅（Si）的电导热导计算算例，包含布里渊区 K 点的 KPT 文件和包含原子位置的 STRU 文件与传统的 KSDFT 计算并无区别，主要的不同在于输入文件 INPUT。为了计算电导热导，我们只需要把 `cal_cond` 参数打开即可，INPUT 文件如下：

```bash
INPUT_PARAMETERS
#Parameters (1.General)
suffix          Si
calculation     scf
esolver_type    sdft
nbands          10
nbands_sto      40
nche_sto        120
seed_sto        20000
symmetry        1
kpar            1
bndpar          2

#Parameters (2.Iteration)
ecutwfc         40
scf_thr         1e-6
scf_nmax        100

#Parameters (3.Basis)
basis_type      pw

#Parameters (4.Smearing)
smearing_method     fd
smearing_sigma      0.6

#Parameters (5.Mixing)
mixing_type     broyden
mixing_beta     0.4

#Parameters (6.Conductivity)
cal_cond         1
cond_smear       1
cond_fwhm        0.4
cond_wcut        20
cond_dw          0.02
cond_dt          0.1
```

以上参数在 ABACUS 的[线上文档](http://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#electronic-structure-sdft)中均有详细说明，这里再进行简单概述：

- <strong>cal_cond</strong>: 控制是否计算电子贡献的电导热导
- <strong>cond_smear</strong>: 设置展宽类型，1：高斯展宽（默认），2：洛伦兹展宽
- <strong>cond_fwhm</strong>: 设置半高宽 FWHM，对于高斯展宽, $$\mathrm{FWHM}=2\sqrt{2\ln2}s$$; 对于洛伦兹展宽 $$\mathrm{FWHM}=2\gamma$$.
- <strong>cond_wcut</strong>: 计算频率的截断值，决定输出含频数据的频率范围, 单位: eV
- <strong>cond_dw</strong>: 频率的间隔，单位:eV
- <strong>cond_dt</strong>: 对响应函数积分时的积分间隔，原子单位，响应函数振荡过快需要较小积分间隔，一般取值在 0.01-0.2 a.u.，在屏幕输出中有推荐的取值：Recommended dt: 1.553e-01 a.u.
- <strong>cond_dtbatch</strong>: 其与 cond_dt 共同决定演化算符$$\exp(i\hat{H}* \mathrm{cond\_dtbatch} * dt)$$的切比雪夫展开阶数，一般来说该值设的越大，内存消耗越多，但速度越快，当其达到一定值，速度就不会增加。当其设为 0 时，程序会自动决定 cond_dtbatch 以使切比雪夫展开阶数在 100 附近。

<strong>计算时间的说明：</strong>

- 使用 sDFT 计算电导热导还是比较慢的，计算时间正比于切比雪夫展开阶数和$$nt = t_{total}/(\mathrm{cond\_dtbatch} * dt)$$
- 切比雪夫阶数由平面波截断能决定，阶数约正比于截断能
- nt 由$$t_{total}$$决定，而$$t_{total}$$由 `cond_fwhm` 决定，其长度反比于 `cond_fwhm`，因此该方法不能使用任意小的展宽。
- 增加$$\mathrm{cond\_dtbatch} * dt$$会使切比雪夫展开阶数增加，会使 nt 减小，总体效应是其值越大，计算效率越高，但达到一定程度，效率就不再增高了。

## 2. 输出文件：

注：结果仅供参考，以最新版本算出的结果为准

### a. 屏幕输出：

```bash
set cond_dtbatch to 69                  自动设置cond_dtbatch参数
set N order of Chebyshev for KG as 113  演化算符的切比雪夫展开阶数
Calculating conductivity....
nw: 1000 ; dw: 2.000e-02 eV             总频率数，频率间隔
nt: 4862 ; dt: 1.000e-01 a.u.(ry^-1)    总时间数，时间间隔
Emin_KS(2): 1.373e+01 eV; Emax: 5.442e+02 eV; Recommended max dt: 1.553e-01 a.u. 推荐cond_dt
ik=0: (Time left 1.673e+02 s) 估计剩余计算时间
nt: 计算进度
69      138     207     276     345     414     483     552     621     690     
759     828     897     966     1035    1104    1173    1242    1311    1380    
1449    1518    1587    1656    1725    1794    1863    1932    2001    2070    
2139    2208    2277    2346    2415    2484    2553    2622    2691    2760    
2829    2898    2967    3036    3105    3174    3243    3312    3381    3450    
3519    3588    3657    3726    3795    3864    3933    4002    4071    4140    
4209    4278    4347    4416    4485    4554    4623    4692    4761    4830    

DC electrical conductivity: 2.454778e+05 Sm^-1   直流电导值（直接线性外推的简单估计值，实际需要根据含频电导拟合外推）
Thermal conductivity: 5.968738e+02 W(mK)^-1      热导值
Lorenz number: 3.456403e+00 k_B^2/e^2            洛伦兹常数
```

### b. je-je.txt:

```bash
#t(a.u.)         c11(t)         c12(t)         c22(t)          decay
       0             -0             -0             -0              1
     0.1       -1.39981        6.61846       -38.6529       0.999999
     0.2       -1.91869        6.94748       -25.4566       0.999997
     0.3       -1.87453        5.46871       -15.4962       0.999993
     0.4         -1.613        3.75367       -6.29163       0.999988
     0.5       -1.36998         3.0228       -6.02995       0.999981
     0.6        -1.1229        2.41076        -5.2121       0.999972
     0.7       -0.84644        1.75119       -5.82033       0.999962
     0.8      -0.529567       0.779473       -2.13103        0.99995
```

储存响应函数的文件，各列分别为均为原子单位，时间 t, 响应函数$$C_{11}(t), C_{12}(t), C_{22}(t)$$, 窗函数

### c. Onsager.txt:

```bash
## w(eV)         sigma(Sm^-1)     kappa(W(mK)^-1)        L12/e(Am^-1)      L22/e^2(Wm^-1)
    0.01              250820             604.318        -4.66249e+06          1.4392e+08
    0.03              261503             619.205        -4.83345e+06         1.47997e+08
    0.05              283291             649.006        -5.18082e+06         1.56228e+08
    0.07              317019              693.79        -5.71545e+06         1.68767e+08
    0.09              363915             753.684        -6.45332e+06         1.85835e+08
    0.11              425574              828.87        -7.41519e+06         2.07723e+08
    0.13              503909             919.555        -8.62601e+06         2.34774e+08
    0.15              601083             1025.94        -1.01141e+07         2.67375e+08
    0.17              719414             1148.17        -1.19101e+07         3.05944e+08
```

储存昂萨格系数的文件，各列分别为频率，电导，热导，$$L_{12}(\omega), L_{22}(\omega)$$
