# ABACUS 平面波基组下的杂化泛函

**作者：任泓旭，邮箱：rhx0820@stu.pku.edu.cn**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2025/09/21**

> 此文档基于 ABACUS 开发版 3.9.0.14 编写。注意，平面波杂化泛函是实验性功能，尚未经过系统性测试，我们目前不对此功能实现的正确性做出保证。

# 一、功能简介

密度泛函理论里的杂化泛函（Hybrid funcitonal）是在交换关联泛函中引入一部分 Fock 交换能成分（“精确交换能”，Exact Exchange，EXX），来改善对电子交换相互作用的描述，进而提高物性的计算精度。通常，杂化泛函在表面、带隙、吸附等方面可以得到优于 LDA、GGA 等普通密度泛函的结果。

相较于数值原子轨道基组下的杂化泛函，平面波基组下的杂化泛函效率较低。如果对效率要求较高，建议首先尝试数值原子轨道下的杂化泛函（[ABACUS+LibRI 做杂化泛函计算教程 · GitBook](https://mcresearch.github.io/abacus-user-guide/abacus-libri.html)）。

然而，由于平面波基组在数学上是相对完备的（而数值原子轨道不是），在部分对精度有较高需求的场景下，平面波基组下的杂化泛函仍然有用。此外，ABACUS 中的部分功能（如 Kubo-Greenwood 方法计算电导热导 [ABACUS 随机波函数 DFT 计算电子电导热导教程 · GitBook](https://mcresearch.github.io/abacus-user-guide/abacus-sdft_cond.html)）只支持平面波基组，在平面波基组下实现杂化泛函可以扩展这些功能的应用场景。

# 二、平面波基组下的杂化泛函算法

我们主要关注精确交换能和精确交换能算符求解的部分，以及自洽迭代（SCF）的部分（目前不支持非自洽计算 NSCF），其他部分和 LDA、GGA 等泛函是一致的。在这一节的所有公式中，斜体$$e$$为元电荷，正体$$\mathrm{e}$$是自然对数的底数。

## 精确交换能算符

考虑在 K 点$$\mathbf{k}$$上的轨道$$\varphi_\mathbf{k}(\mathbf{r})$$作用于精确交换能算符，定义周期性的布洛赫函数如下

$$
u_{n\mathbf{k}}(\mathbf{r})= \frac{1}{\sqrt\Omega} \sum_{\mathbf{G}} c(\mathbf{G})\mathrm{e} ^{i\mathbf{G}\cdot \mathbf{r}}  = \mathrm{e} ^{-i\mathbf{k}\cdot \mathbf{r}} \varphi_{\mathbf{k}}(\mathbf{r}),
$$

这里$$\Omega$$代表体积。引入交叠密度：

$$
n_{\mathbf{k}, m\mathbf{q}}(\mathbf{r}) = u_\mathbf{k}(\mathbf{r})u^*_{m\mathbf{q}}(\mathbf{r}),
$$

这里 m 遍历所有能带，$$\mathbf{q}$$遍历第一布里渊区所有的 K 点，对上式作傅里叶变换，得到关系：

$$
n(\mathbf{r}) = \sum_{\mathbf{G}} n(\mathbf{G}) \mathrm{e}^{i\mathbf{G} \cdot \mathbf{r}} \\
n(\mathbf{G}) = \frac{1}{\Omega} \int_\Omega n(\mathbf{r}) \mathrm{e}^{-i\mathbf{G} \cdot \mathbf{r}} d\mathbf{r}
$$

代入每个 k 点上，精确交换算符作用在波函数上的表达式，并替换密度与轨道：

$$
V_{\text{X, HF}} \varphi_\mathbf{k}(\mathbf{r}) = -e^2 \sum_{m\mathbf{q}}f_{m\mathbf{q}}u_{m\mathbf{q}}(\mathbf{r})\mathrm{e}^{i\mathbf{q}\cdot\mathbf{r}}
\int \frac{\sum_{\mathbf{G}} n_{\mathbf{k}, m\mathbf{q}}(\mathbf{G})\mathrm{e}^{i(\mathbf{k} - \mathbf{q} +\mathbf{G})\cdot\mathbf{r'}}}{|\mathbf{r} - \mathbf{r}'|} d\mathbf{r}',
$$

这里$$f_{m\mathbf{q}}$$是第 m 条能带在编号为 q 的 k 点处的占据数。

之后通过变量替换并交换积分与求和顺序：

$$
\begin{aligned}
V_{\text{X, HF}} \varphi_\mathbf{k}(\mathbf{r}) 
&= -e^2 \sum_{m\mathbf{q}}f_{m\mathbf{q}}u_{m\mathbf{q}}(\mathbf{r})\mathrm{e}^{i\mathbf{k}\cdot\mathbf{r}}
\sum_{\mathbf{G}} n_{\mathbf{k}, m\mathbf{q}}(\mathbf{G}) \mathrm{e}^{i\mathbf{G}\cdot\mathbf{r}}
\int \frac{\mathrm{e}^{i(\mathbf{k} - \mathbf{q} + \mathbf{G})\cdot\mathbf{r'}}}{|\mathbf{r}'|} d\mathbf{r}' \\
&= -e^2 \sum_{m\mathbf{q}}f_{m\mathbf{q}}u_{m\mathbf{q}}(\mathbf{r})\mathrm{e}^{i\mathbf{k}\cdot\mathbf{r}}
\sum_{\mathbf{G}} n_{\mathbf{k}, m\mathbf{q}}(\mathbf{G}) \mathrm{e}^{i\mathbf{G}\cdot\mathbf{r}}
\frac{4\pi}{|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2},
\end{aligned}
$$

即得精确交换能算符作用于轨道的表达式。

> 🔧 注：ABACUS 中 Kohn-Sham 轨道系数存储于倒空间，实际实现需多次进行正反 FFT。

## 精确交换能

类似地，定义交叠密度：

$$
n_{n\mathbf{k}, m\mathbf{q}}(\mathbf{r}) = u_{n\mathbf{k}}(\mathbf{r})u^*_{m\mathbf{q}}(\mathbf{r}),
$$

代入交换能表达式并利用相同技巧处理积分与求和顺序，得到交换能的计算公式为：

$$
E_{\text{X, HF}} = -\frac{e^2}{2} \cdot 4\pi\Omega \sum_{n\mathbf{k}, m\mathbf{q}} f_{n\mathbf{k}} f_{m\mathbf{q}}
\sum_{\mathbf{G}} \frac{n^*_{n\mathbf{k}, m\mathbf{q}}(\mathbf{G}) n_{n\mathbf{k}, m\mathbf{q}}(\mathbf{G})}{|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2},
$$

这里 m, n 遍历所有能带，$$\mathbf{k}, \mathbf{q}$$遍历第一布里渊区所有的 K 点。

## HSE 杂化泛函的特殊处理

HSE 泛函[1, 2]将长程库仑相互作用屏蔽：

$$
\frac{1}{|\mathbf{r} - \mathbf{r}'|} \to \frac{\mathrm{erfc}(\mu |\mathbf{r} - \mathbf{r}'|)}{|\mathbf{r} - \mathbf{r}'|},
$$

其傅里叶空间对应为：

$$
\int \frac{\mathrm{erfc}(\mu |\mathbf{r}'|)}{|\mathbf{r}'|} \mathrm{e}^{i(\mathbf{k}-\mathbf{q}+\mathbf{G})\cdot\mathbf{r}'} d\mathbf{r}'
= \frac{4\pi}{|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2} \left(1 - \mathrm{e}^{-|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2 / 4\mu^2}\right),
$$

因此可得修正后的算符与能量表达式：

$$
V_{\text{X, HSE}} \varphi_\mathbf{k}(\mathbf{r}) =
-e^2 \sum_{m\mathbf{q}} f_{m\mathbf{q}} u_{m\mathbf{q}}(\mathbf{r}) \mathrm{e}^{i\mathbf{k}\cdot\mathbf{r}}
\sum_{\mathbf{G}} n_{\mathbf{k}, m\mathbf{q}}(\mathbf{G}) \mathrm{e}^{i\mathbf{G}\cdot\mathbf{r}}
\frac{4\pi}{|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2} \left(1 - \mathrm{e}^{-|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2 / 4\mu^2}\right),
$$

$$
E_{\text{X, HSE}} = -\frac{e^2}{2} \cdot 4\pi\Omega \sum_{n\mathbf{k}, m\mathbf{q}} f_{n\mathbf{k}} f_{m\mathbf{q}}
\sum_{\mathbf{G}} \frac{n^*_{n\mathbf{k}, m\mathbf{q}}(\mathbf{G}) n_{n\mathbf{k}, m\mathbf{q}}(\mathbf{G})}{|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2}
\left(1 - \mathrm{e}^{-|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2 / 4\mu^2}\right).
$$

## 处理 |k - q + G| = 0 发散问题


当$$|\mathbf{k} - \mathbf{q} + \mathbf{G}| = 0$$时分母发散。若直接舍去该项会导致结果随 k 点增加收敛缓慢。采用 Sorouri 等人改进的方法[3] 解决此问题。

构造辅助函数：

$$
F(\mathbf{k}) = \sum_{\mathbf{G}} \frac{\mathrm{e}^{-\eta |\mathbf{k} + \mathbf{G}|^2}}{|\mathbf{k} + \mathbf{G}|^2},
$$

该函数具有与 $$1/|\mathbf{k}+\mathbf{G}|^2$$相同的发散行为，这里$$\eta$$ 为经验值。

定义剔除零项的求和$$\sum\ '$$和修正函数：

$$
F'(\mathbf{k}) = 
\begin{cases}
0, & \mathbf{k} = 0 \\
F(\mathbf{k}), & \mathbf{k} \neq 0
\end{cases}
$$

则精确交换能可重写为：

$$
\begin{aligned}
E_{\text{X, HF}} &= 
-\frac{e^2}{2} \cdot 4\pi\Omega \sum_{n\mathbf{k}, m\mathbf{q}} f_{n\mathbf{k}} f_{m\mathbf{q}}
\left(
\sum_{\mathbf{G}}\ ' \frac{|n_{n\mathbf{k}, m\mathbf{q}}(\mathbf{G})|^2}{|\mathbf{k} - \mathbf{q} + \mathbf{G}|^2}
- |n_{n\mathbf{k}, m\mathbf{k}}(0)|^2 F'(\mathbf{k} - \mathbf{q})
\right) \\
&\quad -\frac{e^2}{2} \cdot 4\pi\Omega \sum_{mn,\mathbf{k}} |n_{n\mathbf{k}, m\mathbf{k}}(0)|^2 \sum_{\mathbf{q}} F(\mathbf{k} - \mathbf{q}),
\end{aligned}
\tag{7}
$$

其中第一项消除了局部发散，第二项中$$\sum_{\mathbf{q}} F(\mathbf{k}-\mathbf{q})$$在密集 K 网格下近似为积分：

$$
\frac{1}{\text{nqs}} \sum_{\mathbf{q}} F(\mathbf{k} - \mathbf{q}) \approx \frac{\Omega}{(2\pi)^3} \int_{\text{BZ}} F(\mathbf{q}) d\mathbf{q},
$$

利用周期性及积分恒等式：

$$
\int_{\text{BZ}} F(\mathbf{k}) d\mathbf{k} = 2\pi \sqrt{\frac{\pi}{\eta}},
$$

最终将发散项转化为平滑积分，有效解决数值不稳定问题。

## 低秩分解方法（ACE 方法）

尽管精确交换算符可用前述方式计算，但其矩阵形式是满秩的，空间复杂度达 $$O(N_{\text{basis}}^2)$$，难以存储和操作。

Lin [4] 提出 Adaptively Compressed Exchange (ACE) 算符方法，通过低秩近似压缩算符维度，在保证精度前提下显著降低时空复杂度。

以下推导假设单 K 点情形，所有轨道为向量形式：

- $$\{\psi\}$$：用于构建算符的轨道；
- $$\{\varphi\}$$：内层迭代轨道；
- $$V$$：精确交换算符；
- $$V_{\text{ACE}}$$：其 ACE 近似；
- $$\Psi = [\psi_1, \psi_2, \dots, \psi_{N_b}]$$：轨道拼接成“矩阵”；
- $$\dagger$$：共轭转置。

**通过exxace参数可以调整是否使用 ACE 加速，默认启用。**

### ACE 基本假设

- 给定满秩算符 $$V[\{\psi\}]$$（高成本）；
- 寻找低秩近似 $$V_{\text{ACE}}[\{\psi\}]$$，使得 $$V_{\text{ACE}} \psi_i = V \psi_i$$ 对所有 $$\psi_i \in \{\psi\}$$ 严格成立；
- 若 $$\{\varphi\}$$ 在迭代中变化小，则 $$V_{\text{ACE}} \varphi_i \approx V \varphi_i$$。

### ACE 构建步骤

1. 计算响应：$$W = V \Psi$$
2. 构造重叠矩阵：$$M = \Psi^\dagger V \Psi$$
3. 因$M$是负半定 Hermite 矩阵，对$-M$进行 Cholesky 分解：$$M = -L L^\dagger$$
4. 求逆：$$L^{-1}$$
5. 计算中间量：$$\$Xi = L^{-1} W^\dagger$$
6. 得到近似算符：$$V_{\text{ACE}} = -\Xi^\dagger \Xi$$

> ✅ 优势：大幅减少内存占用与矩阵乘法开销，适用于大规模体系。

代码实现中，通过 ABACUS 提供的 `gemm_op`、`lapack_potrf` 等高级接口，实现了 ACE 加速在不同计算设备下的一致实现。

## 杂化泛函的 SCF 迭代

与普通交换关联泛函的 SCF 不同，杂化泛函的 SCF 涉及 Kohn-Sham 轨道的更新。通常采取两层循环，内层循环更新电子密度，外层循环更新参与构建精确交换能算符的轨道。

![](static/AzDYbMmiZok6s5xpLbQcKNdJndc.png)

可以分别通过 `scf_nmax` 和 `exx_hybrid_step` 来调整内/外层循环的最大次数。

# 三、使用方法

通常，只需指定 `dft_functional` 为对应的杂化泛函（如 PBE0、HSE06），其他参数以及 `KPT`、`STRU` 文件和普通泛函计算保持一致。注意，平面波杂化泛函目前不支持 K 点并行，需保持 `KPAR` 为 1。

```
INPUT_PARAMETERS
#Parameters  (General)
pseudo_dir      ../../../tests/PP_ORB        
symmetry        1        
#Parameters  (Accuracy)
basis_type      pw
ecutwfc         60  ###Energy cutoff
scf_nmax        100
device          cpu
ks_solver       cg
precision       double

dft_functional  hse
```

如需调整杂化泛函的参数，比如：ABACUS 中的 HSE 默认为 HSE06，如需使用 HSE03，则应设置

```
exx_erfc_alpha 0.25
exx_erfc_omega 0.15
```

（实际上还要在 libxc 的接口里面修改 PBE 交换部分的屏蔽参数，但 ABACUS 目前改不了）

## 主要参数列表

<table>
<tr>
<td>参数名<br/></td><td>类型<br/></td><td>说明<br/></td></tr>
<tr>
<td>exx_fock_alpha<br/></td><td>浮点数组<br/></td><td>Fock 交换项的混合数组<br/></td></tr>
<tr>
<td>exx_erfc_alpha<br/></td><td>浮点数组<br/></td><td>erfc屏蔽的Fock交换项的混合数组<br/></td></tr>
<tr>
<td>exx_erfc_omega<br/></td><td>浮点数组<br/></td><td>对应 exx_erfc_alpha 的 ω 参数数组，数组长度必须与 exx_erfc_alpha 相同<br/></td></tr>
<tr>
<td>exxace<br/></td><td>布尔值<br/></td><td>true开启，false关闭。默认为true。<br/></td></tr>
<tr>
<td>scf_nmax<br/></td><td>整数<br/></td><td>在普通泛函中是SCF的最大次数，在杂化泛函中是内层循环的最大次数。<br/></td></tr>
<tr>
<td>exx_hybrid_step<br/></td><td>整数<br/></td><td>杂化泛函中外层循环的最大次数<br/></td></tr>
</table>

# 四、参考文献

[1] J. Heyd, G. E. Scuseria, and M. Ernzerhof, J. Chem. Phys. **118**, 8207 (2003).

[2] J. Heyd, G. E. Scuseria, and M. Ernzerhof, J. Chem. Phys. **124**, 219906 (2006).

[3] A. Sorouri, W. M. C. Foulkes, and N. D. M. Hine, J. Chem. Phys. **124**, 064105 (2006).

[4] L. Lin, J. Chem. Theory Comput. **12**, 2242 (2016).
