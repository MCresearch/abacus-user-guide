# 电荷密度混合算法介绍

<strong>作者：孙亮，邮箱：l.sun@pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/11/09</strong>

# 一、背景

做基于 Kohn-Sham Density Functional Theory（KSDFT）的第一性原理计算的过程就是求解 Kohn-Sham (KS)方程 $$ [-\frac{1}{2}\nabla^2+V_{\rm{eff}}(r)]\psi_i^\sigma(r)=\varepsilon_i^\sigma\psi_i^\sigma(r),V_{\rm{eff}}(r)=V_{\rm ext}(r)+V_{\rm{H}}(r)+V_{\rm{xc}}(r) $$

的过程。由于其中

$$
V_{\rm{H}}(r)=\int{\frac{\rho(r')}{|r-r'|}dr'},V_{\rm{xc}}(r) = \frac{\delta E_{\rm{xc}}[\rho]}{\delta\rho(r)}
$$

均依赖于电荷密度$$\rho(r)$$，KS 方程无法直接求解，只能采取迭代的方法，也就是自洽场迭代法（scf, self-consistent field）。其流程可以概括为

$$
\cdots \rightarrow \rho^{i-1} \rightarrow V_{\rm{eff}}^{i-1} \rightarrow \rho^{i} \rightarrow V_{\rm{eff}}^{i} \rightarrow \rho^{i+1} \rightarrow \cdots
$$

上述过程也可以看作一个不动点问题：$$\rho = f(\rho)$$，$$f$$代表从$$\rho^{i-1}$$到$$\rho^i$$的映射。

我们常常采用<strong>电荷密度混合（charge mixing）</strong>方法来提升 scf 迭代过程的稳定性和收敛效率，引入 charge mixing 方法后，scf 流程可概括为

$$
\cdots \rightarrow \rho_{\rm{in}}^{i-1} \rightarrow V_{\rm{eff}}^{i-1} \rightarrow \rho_{\rm{out}}^{i-1}  \stackrel{CM}{\longrightarrow} \rho_{\rm{in}}^{i} \rightarrow V_{\rm{eff}}^{i} \rightarrow \rho_{\rm{out}}^{i} \stackrel{CM}{\longrightarrow} \rho_{\rm{in}}^{i+1} \rightarrow \cdots
$$

其中$$CM$$表示 charge mixing 方法，它将前几步的电荷密度以一定的比例混合，得到下一步输入$$f$$映射的电荷密度$$\rho_{\rm{in}}$$。

下面我们将介绍几种常用的 charge mixing 方法：<strong>plain mixing</strong>, <strong>Pulay mixing</strong>, 以及<strong>Broyden mixing</strong>方法。这三种算法均已实现在 ABACUS 中。

为了方便，下文中我们统一采用狄拉克符号，比如电荷密度记为$$|\rho\rangle$$。

# 二、算法介绍

我们一般定义$$|F^{i}\rangle = |\rho^{i}_ {\rm{out}}\rangle - |\rho^{i}_{\rm{in}}\rangle$$为<strong>残差</strong>，当它的模$$\langle F^{i}|F^{i}\rangle = 0$$时，迭代达到收敛。实际计算中，无法真正做到模为零，一般设置一个阈值$$\Delta$$来判断是否收敛。

值得一提的是，下面的推导中，我们都以电荷密度作为变量，但这些算法都适用于 charge mixing 过程中其它量的混合，比如动能密度等。它们也不仅适用于电荷密度混合，也可用于其它的优化问题。

## 1. Plain mixing

Plain mixing，也称 simple mixing，其思路是将$$|\rho^{i}_ {\rm{in}}\rangle$$和$$|\rho^{i}_ {\rm{out}}\rangle$$做线性组合，得到下一步的$$|\rho^{i+1}_{\rm{in}}\rangle$$，为了保证混合前后电子数不变，混合的公式为

$$
|\rho^{i+1}_{\rm{in}}\rangle = (1-\beta)|\rho^{i}_{\rm{in}}\rangle + \beta|\rho^{i}_{\rm{out}}\rangle = |\rho^{i}_{\rm{in}}\rangle + \beta(|\rho^{i}_{\rm{out}}\rangle - |\rho^{i}_{\rm{in}}\rangle) = |\rho^{i}_{\rm{in}}\rangle + \beta|F^{i}\rangle,
$$

<strong>其中</strong>$$\beta$$<strong>为 mixing 的步长，可以取 0 到 1 间的实数，</strong>$$\beta$$<strong>越小，则迭代越稳定，但收敛所需的步数可能越多。（见第三部分，介绍 ABACUS 里面的相关参数）</strong>

一般而言，plain mixing 收敛较慢，不在实际计算中采用。

## 2. Pulay mixing

Pulay mixing[1]也叫 direct inversion of the iterative sub-space (DIIS) method，其思路是用前$$n$$步的电荷密度$$\{|\rho^{i-n+1}_ {\rm{in}}\rangle, \cdots, |\rho^{i-1}_ {\rm{in}}\rangle, |\rho^{i}_ {\rm{in}}\rangle\}$$做线性组合，在此线性空间中找到一个“最佳”的电荷密度$$|\rho^i_{\rm{opt}}\rangle$$，使得$$\langle F^{i}_ {\rm{opt}}|F^{i}_ {\rm{opt}}\rangle$$取极小值，再由$$|\rho^i_{\rm{opt}}\rangle$$和$$|F^i_{\rm{opt}}\rangle$$线性组合得到下一步的$$|\rho^{i+1}_{\rm{in}}\rangle$$。

下面我们首先给出算法流程，然后进行相应的推导。

### 2.1 算法流程

需要存储前$$n$$步迭代的$$\{|\rho^{i-n+1}_ {\rm{in}}\rangle, \cdots, |\rho^{i-1}_ {\rm{in}}\rangle, |\rho^{i}_{\rm{in}}\rangle\}$$和$$\{|F^{i-n+1}\rangle, \cdots, |F^{i-1}\rangle, |F^{i}\rangle\}$$，

- 计算大小为$$n \times n$$的矩阵$$A,A_{jk} = \langle F^{i-n+j}|F^{i-n+k}\rangle$$；
- 计算逆矩阵$$A^{-1}$$；
- 计算混合系数$$\alpha_j = \frac{\sum_k^n{A^{-1}_ {jk}}}{\sum_{l}^{n}{\sum_k^n{A^{-1}_{lk}}}}$$；
- 更新密度$$|\rho^{i+1}_ {\rm{in}}\rangle = \sum_{j=1}^{n}{\alpha_j \left(|\rho^{i-n+j}_{\rm{in}}\rangle + \beta |F^{i-n+j}\rangle \right)}$$，$$\beta$$为 mixing 的步长。

### 2.2 算法推导

为了记号方便，我们将参与线性组合的前$$n$$步电荷密度$$\{|\rho^{i-n+1}_ {\rm{in}}\rangle, \cdots, |\rho^{i-1}_ {\rm{in}}\rangle, |\rho^{i}_ {\rm{in}}\rangle\}$$重新标记为$$\{|\rho^{1}_ {\rm{in}}\rangle, \cdots, |\rho^{n-1}_ {\rm{in}}\rangle, |\rho^{n}_{\rm{in}}\rangle\}$$。

首先我们定义$$|\rho^i_{\rm{opt}}\rangle = \sum_{j=1}^{n}{\alpha_j |\rho^j_{\rm{in}}\rangle}$$，为了保证电子数守恒，要求$$\sum_{j=1}^{n}{\alpha_j} = 1$$。

为了找到最佳的$$\{\alpha_j\}$$组合，使得$$\langle F^{i}_ {\rm{opt}}|F^{i}_ {\rm{opt}}\rangle$$取极小值，同时满足$$\sum_{j=1}^{n}{\alpha_j} = 1$$的条件，我们采用拉格朗日乘子法，定义

$$
L=\langle F^{i}_{\rm{opt}}|F^{i}_{\rm{opt}}\rangle - \lambda \left( \sum_{j=1}^{n}{\alpha_j} - 1 \right).
$$

进一步假设$$F_{\rm{opt}}^i[\rho^{i}_ {\rm{opt}}] = F_{\rm{opt}}^i[\sum_{j=1}^{n}{\alpha_j \rho^{i}_ {\rm{in}}}] = \sum_{j=1}^{n}{\alpha_j F^{j}[\rho^{j}_ {\rm{in}}]}$$，即$$|F_{\rm{opt}}^i\rangle = \sum_{j=1}^{n}{\alpha_j |F^{j}\rangle}$$，上式变为

$$
\begin{aligned}
L
&= \sum_{j=1}^{n}{\sum_{k=1}^{n}{\alpha_j \langle F^j|F^k\rangle\alpha_k}} - \lambda \left( \sum_{j=1}^{n}{\alpha_j} - 1 \right)\\
&
= \sum_{j=1}^{n}{\sum_{k=1}^{n}{\alpha_j A_{jk}\alpha_k}} - \lambda \left( \sum_{j=1}^{n}{\alpha_j} - 1 \right).
\end{aligned}
$$

上面我们定义了$$A_{jk} = \langle F^j|F^k\rangle$$，它满足$$A_{jk} = A_{kj}$$。

于是有

$$
\frac{\partial L}{\partial\alpha_j} = 2\sum_{k=1}^n{A_{jk}\alpha_k} - \lambda = 0 \longrightarrow 2\sum_{k=1}^n{A_{jk}\alpha_k} = \lambda,
$$

两边同乘$$A^{-1}_{lj}$$并对$$j$$求和，有

$$
2\sum_{j=1}^n\sum_{k=1}^n{A^{-1}_{lj}A_{jk}\alpha_k} = \lambda \sum_{j=1}^n{A^{-1}_{lj}} \longrightarrow 2\sum_{k=1}^n{\delta_{lk}\alpha_k} = 2\alpha_l = \lambda \sum_{j=1}^n{A^{-1}_{lj}}.
$$

由$$\sum_{l=1}^{n}{\alpha_l} = 1$$，有$$\frac{1}{2}\lambda\sum_{l=1}^{n}{\sum_{j=1}^n{A^{-1}_ {lj}}} = 1$$，因此$$\lambda = \frac{2}{\sum_{l}^{n}{\sum_{j}^n{A^{-1}_{lj}}}}.$$

代回上式，我们得到最佳混合比例

$$
\alpha_l = \frac{\sum_j^n{A^{-1}_{lj}}}{\sum_{k}^{n}{\sum_j^n{A^{-1}_{kj}}}}.
$$

最终，我们得到由前$$n$$步电荷密度线性组合可以得到的“最佳”电荷密度$$|\rho^i_{\rm{opt}}\rangle = \sum_{j=1}^{n}{\alpha_j |\rho^j_{\rm{in}}\rangle}$$，相应的残差$$|F_{\rm{opt}}^i\rangle = \sum_{j=1}^{n}{\alpha_j |F^{j}\rangle}$$，其中的系数$$\alpha_j = \frac{\sum_k^n{A^{-1}_ {jk}}}{\sum_{l}^{n}{\sum_k^n{A^{-1}_{lk}}}}.$$

因此下一次迭代的初始电荷密度

$$
\begin{aligned}
|\rho^{i+1}_{\rm{in}}\rangle 
&
= |\rho^{i}_{\rm{opt}}\rangle + \beta|F^{i}_{\rm{opt}}\rangle\\
&
= \sum_{j=1}^{n}{\alpha_j |\rho^j_{\rm{in}}\rangle} + \beta \sum_{j=1}^{n}{\alpha_j |F^{j}\rangle}\\
&
= \sum_{j=1}^{n}{\alpha_j \left(|\rho^j_{\rm{in}}\rangle + \beta |F^{j}\rangle \right)}.
\end{aligned}
$$

## 3. Broyden mixing

Broyden mixing 是拟牛顿法的一种，它的思路是对$$|F\rangle$$的雅可比矩阵的逆进行近似，从而采用牛顿法进行迭代。

在其发展过程中，曾出现过不同的形式，这里我们介绍的是 1988 年 Johnson 提出的 Simplified modified Broyden method[2]，它兼具收敛速度快与内存消耗少的优势，也是 ABACUS 默认采用的 mixing 方法。

我们先给出算法流程，再进行推导，以下推导参考了文献[3]。

### 3.1 算法流程

首先我们定义$$|\Delta\rho^{i}_ {\rm{in}}\rangle = |\rho^{i}_ {\rm{in}}\rangle - |\rho^{i-1}_{\rm{in}}\rangle$$，$$|\Delta F^{i}\rangle = |F^{i}\rangle - |F^{i-1}\rangle$$。

需要存储前$$n$$步迭代的$$\{|\Delta\rho^{i-n+1}_ {\rm{in}}\rangle, |\Delta\rho^{i-n+2}_ {\rm{in}}\rangle, \cdots, |\Delta\rho^{i}_{\rm{in}}\rangle\}$$和$$\{|\Delta F^{i-n+1}\rangle, |\Delta F^{i-n+2}\rangle, \cdots, |\Delta F^{i}\rangle\}$$，

- 计算大小为$$n \times n$$的矩阵$$B,B_{jk}=\langle\Delta F^{i-n+j}|\Delta F^{i-n+k}\rangle$$；
- 计算逆矩阵$$B^{-1}$$；
- 计算混合系数$$\alpha_j=-\sum_{k=1}^{n}{B^{-1}_{jk}\langle\Delta F^{i-n+k}|F^{i}\rangle}$$；
- 更新密度$$|\rho^{i+1}_ {\rm{in}}\rangle = |\rho^{i}_ {\rm{in}}\rangle + \beta|F^{i}\rangle + \sum_{j=1}^{n}\alpha_{j}\left(|\Delta\rho^{i-n+j}_{\rm{in}}\rangle + \beta|\Delta F^{i-n+j}\rangle\right)$$，$$\beta$$为 mixing 的步长。

### 3.2 算法推导

#### 3.2.1 牛顿法

我们首先介绍牛顿法，对于 charge mixing 中的不动点问题$$\rho = f(\rho)$$，可以改写为

$$|F\rangle = |\rho_{\rm{out}}\rangle - |\rho_{\rm{in}}\rangle = 0$$，这里$$|\rho_{\rm{out}}\rangle = f(|\rho_{\rm{in}}\rangle)$$。

假设$$|F'\rangle=F[\rho']=0$$，且$$|F\rangle$$在$$|\rho'\rangle$$附近足够光滑，选$$|\rho'\rangle$$附近的$$|\rho_0\rangle$$作为出发点，做泰勒展开，有

$$
|F'\rangle=|F_0\rangle+J_0(|\rho'\rangle-|\rho_0\rangle)+\cdots=0,
$$

其中$$J_0=\frac{\partial F}{\partial\rho}|_{\rho=\rho_0}$$为雅可比矩阵，做线性近似后，有

$$
|\rho'\rangle=|\rho_0\rangle - J_0^{-1}|F_0\rangle,
$$

由此得到牛顿法的迭代公式

$$
|\rho^{i+1}_{\rm{in}}\rangle=|\rho^{i}_{\rm{in}}\rangle - J_i^{-1}|F^{i}\rangle,
$$

此公式中出现了雅可比矩阵的逆，精确求解将极为耗时，因此一般通过求解线性方程组来得到它：

记$$C_i=J^{-1}_i$$，由$$|F^{i-1}\rangle=|F^{i}\rangle+J_i(|\rho^{i-1}_ {\rm{in}}\rangle-|\rho^{i}_{\rm{in}}\rangle)$$，有$$C_i|\Delta F^{i}\rangle=|\Delta\rho^{i}_{\rm{in}}\rangle$$。

综上，牛顿法的完整迭代公式为

$$
|\rho^{i+1}_{\rm{in}}\rangle=|\rho^{i}_{\rm{in}}\rangle - C_i|F^{i}\rangle,C_i|\Delta F^{i}\rangle=|\Delta\rho^{i}_{\rm{in}}\rangle.
$$

牛顿法中，需要先求出矩阵$$C_i$$，在 charge mixing 的应用场景中，$$C_i$$的大小为$$N\times N$$，$$N$$为实空间格点数，因此$$C_i$$的求解和储存都很不方便。

#### 3.2.2 Broyden 算法

为了克服牛顿法的问题，人们提出了拟牛顿法（quasi-Newton），其基本思路是对$$C_i$$进行近似，而不是精确求解。拟牛顿法中，我们一般要求近似的$$C_i$$仍然满足$$C_i|\Delta F^{i}\rangle=|\Delta\rho^{i}_{\rm{in}}\rangle$$的条件，称为<strong>拟牛顿条件</strong>。

Simplified modified Broyden method 是拟牛顿法的一种，假设$$C_{i-1}$$已知，它通过求解以下优化问题得到$$C_i$$：

$$
\min_{C} \frac{1}{2}\|C-C_{i-1}\|^2_{F}, {\rm{s.t.}}\ S_{i}=CY_{i}.
$$

其中$$S_i=(|\Delta\rho^{i-n+1}_ {\rm{in}}\rangle, |\Delta\rho^{i-n+2}_ {\rm{in}}\rangle, \cdots, |\Delta\rho^{i}_{\rm{in}}\rangle)$$，$$Y_i=(|\Delta F^{i-n+1}\rangle, |\Delta F^{i-n+2}\rangle, \cdots, |\Delta F^{i}\rangle)$$，均为大小为$$N\times n$$的矩阵，$$S_{i}=CY_{i}$$要求$$C$$对于前$$n$$步的$$|\Delta\rho^{j}_{\rm{in}}\rangle$$和$$|\Delta F^{j}\rangle$$均满足拟牛顿条件，

我们仍然采用拉格朗日乘子法，定义

$$
L = \frac{1}{2}\|C-C'\|^2_{F} + \frac{1}{2}u^T\left(S-CY\right)^T\left(S-CY\right)u,
$$

为了方便，这里我们省去了$$S_i,Y_i$$的下标$$i$$，并且记$$C'=C_{i-1}$$，其中$$u=(u_1, u_2, \cdots, u_n)^T$$为拉格朗日乘子组成的大小为$$n\times 1$$的向量。

将上式展开，有

$$
\begin{aligned}
L =& \frac{1}{2}\sum_{j=1}^n\sum_{k=1}^n\left(C_{jk}-C'_{jk}\right)^2\\
&+
\frac{1}{2}\sum_{j=1}^n\sum_{k=1}^n{u_j\left[
\left(S^TS\right)_{jk}
- 2\sum_{p=1}^N\sum_{q=1}^N{S_{pj}C_{pq}Y_{qk}}
+
\sum_{p=1}^N\sum_{q=1}^N\sum_{l=1}^N{Y_{pj}C_{qp}C_{ql}Y_{lk}}
\right]u_k},
\end{aligned}
$$

令$$\partial L/\partial{C_{\mu\nu}}=0$$，由上式有

$$
\frac{\partial L}{\partial{C}_{\mu\nu}}=C_{\mu\nu} - C'_{\mu\nu} - \sum_{j=1}^n\sum_{k=1}^n{\left(S_{\mu j} - \sum_{l=1}^N{C_{\mu l}Y_{lj}}\right)u_ju_kY_{\nu k}} = 0,
$$

因此

$$
C_{\mu\nu} \approx C'_{\mu\nu} + \sum_{j=1}^n\sum_{k=1}^n{\left(S_{\mu j} - \sum_{l=1}^N{C'_{\mu l}Y_{lj}}\right)u_ju_kY_{\nu k}},
$$

注意我们将括号中的$$C_{\mu l}$$近似成了$$C'_{\mu l}$$，上式写成矩阵形式为

$$
C  =  C'+\left(S-C' Y\right)uu^T Y^T,
$$

代入拟牛顿条件$$S=CY$$中，要求$$uu^T = \left(Y^T Y\right)^{-1}$$，因此上述优化问题给出

$$
C_{i}  =  C_{i-1}+\left(S_i-C_{i-1} Y_i\right) \left(Y_i^T Y_i\right)^{-1} Y_i^T,
$$

假设$$C_{i-1}=C_0=-\beta I$$，上式变为

$$
C_{i}  = -\beta I + \left(S_i+\beta Y_i\right) \left(Y_i^T Y_i\right)^{-1} Y_i^T,
$$

于是迭代公式为

$$
\begin{aligned}
|\rho^{i+1}_{\rm{in}}\rangle &=|\rho^{i}_{\rm{in}}\rangle - C_i|F^{i}\rangle\\
&
= |\rho^{i}_{\rm{in}}\rangle - \left(-\beta I + \left(S_i+\beta Y_i\right) \left(Y_i^T Y_i\right)^{-1} Y_i^T\right) |F^{i}\rangle\\
&
= |\rho^{i}_{\rm{in}}\rangle + \beta|F^{i}\rangle - \left(S_i+\beta Y_i\right) \left(Y_i^T Y_i\right)^{-1} Y_i^T |F^{i}\rangle.
\end{aligned}
$$

下面我们将此公式改写成更加清楚的形式，首先令$$B=Y_i^T Y_i$$，则$$B_{jk}=\langle\Delta F^{i-n+j}|\Delta F^{i-n+k}\rangle$$，因此

$$
\begin{aligned}
-\left(Y_i^T Y_i\right)^{-1} Y_i^T |F^{i}\rangle &= -B^{-1}\left(\langle\Delta F^{i-n+1}|F^{i}\rangle, \langle\Delta F^{i-n+2}|F^{i}\rangle, \cdots, \langle\Delta F^{i}|F^{i}\rangle \right)^T\\
&
=\left(\alpha_1, \alpha_2, \cdots, \alpha_n \right)^T,
\end{aligned}
$$

其中$$\alpha_j=-\sum_{k=1}^{n}{B^{-1}_{jk}\langle\Delta F^{i-n+j}|F^{i}\rangle}$$。

最终

$$
\begin{aligned}
|\rho^{i+1}_{\rm{in}}\rangle 
&
=  |\rho^{i}_{\rm{in}}\rangle + \beta|F^{i}\rangle - \left(S_i+\beta Y_i\right) \left(Y_i^T Y_i\right)^{-1} Y_i^T |F^{i}\rangle\\
&
= |\rho^{i}_{\rm{in}}\rangle + \beta|F^{i}\rangle + \left(S_i+\beta Y_i\right) \left(\alpha_1, \alpha_2, \cdots, \alpha_n \right)^T\\
&
= |\rho^{i}_{\rm{in}}\rangle + \beta|F^{i}\rangle + \sum_{j=1}^{n}\alpha_{j}\left(|\Delta\rho^{i-n+j}_{\rm{in}}\rangle + \beta|\Delta F^{i-n+j}\rangle\right).
\end{aligned}
$$

# 三、ABACUS 相关参数介绍

上述三种算法均已在 ABACUS 中实现，下面我们简要介绍 ABACUS 中 charge mixing 的相关参数，并将它们与上面的公式对应起来，详细文档见[链接](https://abacus.deepmodeling.com/en/stable/advanced/input_files/input-main.html)。

- `mixing_type`：选择 mixing 算法，可选项为 `plain`, `pulay`, `broyden`，分别对应上述三种算法，一般而言，Broyden 算法收敛最快，Pulay 略慢，plain 最慢。默认选项为 `broyden`。
- `mixing_beta`：对应上述公式中的参数$$\beta$$，$$\beta$$绝对值越小，则收敛过程越稳定，但达到收敛所需的步数可能增多。对于难以收敛的体系，特别是收敛过程中能量出现上下波动的例子，可以尝试减小 `mixing_beta`。
- `mixing_ndim`：对应上述公式中的参数$$n$$，Pulay 和 Broyden 算法会借助过去$$n$$步的信息构建下一次迭代的电荷密度，默认值为 8。对于难以收敛的体系，略增大 `mixing_ndim` 可以增强收敛过程的稳定性。
- `mixing_gg0`：是否采用 Kerker scaling 方法，此方法会抑制混合过程中的高频项。特别是对于难以收敛的金属体系，打开 Kerker 方法可以帮助计算达到收敛。
- `mixing_tau`：是否对动能密度进行混合，适用于使用 meta-GGA 交换关联泛函的场景。
- `mixing_dftu`：是否对密度矩阵进行混合，适用于使用 DFT+U 的场景。
- `scf_thr`：对应于 charge mixing 的收敛判据$$\Delta$$，对于原子轨道基组(LCAO)，默认值为 1e-7，对于平面波基组(PW)，默认值为 1e-9。
- `scf_thr_type`：选择上述公式中内积$$\langle f|f\rangle$$的定义，以及相应收敛判据的计算方式。

  - 1：$$\langle f|f\rangle = \frac{1}{2}\iint{\frac{f(r)f(r')}{|r-r'|}drdr'}$$，收敛判据为$$\langle\Delta\rho|\Delta\rho\rangle < \Delta$$，默认用于 PW 基组；
  - 2：$$\langle f|f\rangle = \int{f^2(r)dr}$$，收敛判据为$$\int{|\Delta\rho|dr} < \Delta$$，默认用于 LCAO 基组。

# 四、参考文献

[1] [Pulay P. Convergence acceleration of iterative sequences. The case of SCF iteration[J]. Chemical Physics Letters, 1980, 73(2): 393-398.](https://www.sciencedirect.com/science/article/abs/pii/0009261480803964)

[2] [Johnson D D. Modified Broyden’s method for accelerating convergence in self-consistent calculations[J]. Physical Review B, 1988, 38(18): 12807.](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.38.12807)

[3] [Lin L, Yang C. Elliptic preconditioner for accelerating the self-consistent field iteration in Kohn--Sham density functional theory[J]. SIAM Journal on Scientific Computing, 2013, 35(5): S277-S298.](https://epubs.siam.org/doi/abs/10.1137/120880604)
