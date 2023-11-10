# 最大局域化 Wannier 函数方法简介

<strong>作者：刘人熙，邮箱：rxliu@stu.pku.edu.cn</strong>

<strong>审核：陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/11/09</strong>

# 一、Wannier 函数是什么？

电子的<strong>能量</strong>和<strong>波函数</strong>是电子结构计算中最关心的物理量之一，了解电子的这两个性质，就能进一步了解电子乃至原子体系的更多性质。

在周期性势场中，电子波函数满足<strong>布洛赫定理（Bloch Theorem）</strong>，该定理指出，当电子处于满足

$$
V(\mathbf{r}+\mathbf{R})=V(\mathbf{r})
$$

的周期性势场$$V(\mathbf{r})$$下时，电子的本征波函数$$\psi_{n\mathbf{k}}(\mathbf{r})$$满足公式$$\psi_{n\mathbf{k}}(\mathbf{r})=e^{i\mathbf{k}\cdot\mathbf{r}}u_{n\mathbf{k}}(\mathbf{r})$$，

其中$$u_{n\mathbf{k}}(\mathbf{r})$$是另一个周期性函数，满足

$$u_{n\mathbf{k}}(\mathbf{r})=u_{n\mathbf{k}}(\mathbf{r}+\mathbf{R})$$，这里的$$\mathbf{R}$$代表晶格矢量。

图 1 左列展示了一维情况下一些布洛赫波函数的形态，即通常情况下，电子波函数在实空间中是<strong>非局域的</strong>。

事实上，电子波函数的模平方代表电子出现的概率密度，能被实验验证。在计算中，可以发现电子波函数有一个可调节的“相位因子“，这个随机的相位因子可以导致计算出来的电子波函数在实空间的局域程度不同。因此，长期以来，人们一直在探索什么形式的电子波函数适合描述例如共价键这样的物理性质，Wannier 函数就是常用的一种方法。

Wannier 函数就是一种周期性势场中的电子波函数表示方法，早在 1937 年，Gregory H. Wannier 最早定义了周期性势场中的波函数可以写成：

$$
|\mathbf{R}n\rangle=\frac{V}{(2\pi)^3}\int_{BZ}d\mathbf{k}e^{-i\mathbf{k}\cdot\mathbf{R}}|\psi_{n\mathbf{k}}\rangle
$$

这里的 V 代表晶格体积。从公式直观上看，这相当于在第一布里渊区中对电子波函数做傅立叶变换，也就是对各个本征态波函数$$\psi_{n\mathbf{k}}$$按照$$e^{-i\mathbf{k}\cdot\mathbf{R}}$$的权重做加权平均，把各个本征态“折叠”到$$\mathbf{R}$$晶格中，实现局域化。得到的波函数$$|\mathbf{R}n\rangle$$被称作 Wannier 函数，一维的图示如图 1 右列。

![左列：不同k点对应的布洛赫波函数；右列：不同晶格中的Wannier函数。](picture/fig_wannier.jpg)

易于验证 Wannier 函数是正交归一的，布洛赫波函数可以通过逆傅立叶变换从 Wannier 函数得到：

$$
|\psi_{n\mathbf{k}}\rangle=\sum_{\mathbf{R}}e^{i\mathbf{k}\cdot\mathbf{R}}|\mathbf{R}n\rangle
$$

于是对于同一个能带的子空间来说，布洛赫波函数和 Wannier 函数都可以构成电子波函数的完备表示，也就是

$$P_n=
\sum_{\mathbf{R}}|\mathbf{R}n\rangle\langle\mathbf{R}n|=\sum_{\mathbf{k}}|\psi_{n\mathbf{k}}\rangle\langle\psi_{n\mathbf{k}}|$$。

# 二、最大局域化 Wannier 函数

## 2.1 Wannier 函数的不唯一性

Wannier 的局域化定义简单直接，深受学界欢迎，但是它存在随规范变化因而不唯一的问题。这种不唯一性来源于布洛赫波的不唯一性，对于非简并的$$n\mathbf{k}$$态的本征波函数$$\psi_{n\mathbf{k}}$$，规范变换后的$$\psi_{n\mathbf{k}}e^{i\phi(\mathbf{k})}$$（$$\phi(\mathbf{k})$$为实数）同样是本征态，二者之间只差一个相位因子。但是这样一来，布洛赫波中的$$u_{n\mathbf{k}}$$分量就变成了$$u_{n\mathbf{k}}e^{i\phi(\mathbf{k})}$$，Wannier 函数就变成了$$\frac{V}{(2\pi)^3}\int_{BZ}d\mathbf{k}e^{-i\mathbf{k}\cdot\mathbf{R}+i\phi(\mathbf{k})}|\psi_{n\mathbf{k}}\rangle$$，得到的 Wannier 函数就完全不一样了。

在简并情况下，比如说 J 个能带构成一组互相相交的能带，和其他能带不相交，这时这 J 个能带的本征波函数做幺正变换，依然可以构成本征波函数，也就是

$$
|\tilde{\psi}_{n\mathbf{k}}\rangle=\sum_{m}U_{mn}^{\mathbf{k}}|\psi_{m\mathbf{k}}\rangle
$$

依然是本征态，他们可以张成对应于这 J 个能带的同一个线性空间，该线性空间的投影算符可以写作

$$P_{\mathbf{k}}=\sum_{n=1}^{J}|\psi_{n\mathbf{k}}\rangle\langle\psi_{n\mathbf{k}}|=\sum_{m=1}^{J}|\tilde\psi_{m\mathbf{k}}\rangle\langle\tilde\psi_{m\mathbf{k}}|$$。

第二个等号具体证明如下：

$$
\sum_{m=1}^{J}|\tilde\psi_{m\mathbf{k}}\rangle\langle\tilde\psi_{m\mathbf{k}}|=\sum_{m=1}^{J}\sum_{pq}^{J}U_{mp}^{\mathbf{k}}|\psi_{p\mathbf{k}}\rangle U^{\mathbf{k}*}_{qm}\langle\psi_{q\mathbf{k}}|
$$

$$
=\sum_{pq}^{J}\sum_{m=1}^{J}U^{\mathbf{k}*}_{qm}U_{mp}^{\mathbf{k}}|\psi_{p\mathbf{k}}\rangle\langle\psi_{q\mathbf{k}}|=\sum_{pq}^{J}\delta_{pq}|\psi_{p\mathbf{k}}\rangle\langle\psi_{q\mathbf{k}}|=\sum_{p=1}^{J}|\psi_{p\mathbf{k}}\rangle\langle\psi_{p\mathbf{k}}|
$$

也就是说一组或者一个孤立的能带的投影算符是不随规范变换的。

这时不同规范下的 Wannier 函数的变换会更为复杂，Wannier 函数也存在不唯一确定的问题。

所以是否可以选取一个给定的规范，可以在一个系统上给出唯一的一组 Wannier 函数，满足我们在第一部分中提出的两个动机呢？这个简单的问题并没有在固体物理建立的最初几十年里有一个完整的解答。

## 2.2 独立的能带的 Wannier 函数的 spread 函数

直到 1997 年，Nicola Marzari 和 David Vanderbilt 在文献[1]提出，可以针对一组孤立的 J 个能带（也可以是单独一个孤立的能带），要求 Wannier 函数在晶格内的 spread 最小，以此作为规范，所谓的 spread 就是在 Wannier 函数上位置 r 的方差

$$\Omega=\sum_{n}\langle\mathbf{0}n|\mathbf{r}^2|\mathbf{0}n\rangle-|\langle\mathbf{0}n|\mathbf{r}|\mathbf{0}n\rangle|^2$$.

Marzari 和 Vanderbilt 进一步发现这个 spread 函数可以分为规范不变和随规范变换的两个部分，并且给出了最小化 spread 函数的稳定的数值算法。

具体来说，规范不变的部分是：

$$\Omega_{I}=\sum_{n}\left[\langle\mathbf{0}n|\mathbf{r}^2|\mathbf{0}n\rangle-\sum_{\mathbf{R}m}|\langle\mathbf{R}m|\mathbf{r}|\mathbf{0}n\rangle|^2\right]$$，

规范变换的部分是

$$\tilde\Omega=\sum_{n}\sum_{\mathbf{R}m\neq\mathbf{0}n}|\langle\mathbf{R}m|\mathbf{r}|\mathbf{0}n\rangle|^2$$，

规范不变的部分可以写作：

$$
\Omega_I=\sum_{n\alpha}\left[\langle\mathbf{0}n|r_\alpha^2|\mathbf{0}n\rangle-\sum_{\mathbf{R}m}\langle\mathbf{0}n|r_\alpha|\mathbf{R}m\rangle\langle\mathbf{R}m|r_\alpha|\mathbf{0}n\rangle\right]
$$

$$
=\sum_{n\alpha}\left[\langle\mathbf{0}n|r_\alpha^2|\mathbf{0}n\rangle-\sum_{m}\langle\mathbf{0}n|r_{\alpha}P_{m}r_\alpha|\mathbf{0}n\rangle \right]
$$

$$
=\sum_{n\alpha}\langle\mathbf{0}n|r_{\alpha}(1-\sum_{m}P_{m})r_\alpha|\mathbf{0}n\rangle =\sum_{n\alpha}\langle \mathbf{0}n|r_{\alpha}Qr_\alpha|\mathbf{0}n\rangle
$$

上式中最后一个等号使用了定义

$$P=\sum_m P_m=\sum_{\mathbf{k}m}|\psi_{m\mathbf{k}}\rangle\langle\psi_{m\mathbf{k}}|$$，

$$Q=1-P$$，

因为 P 和 Q 算符是考虑的这组孤立能带上的投影矩阵和互补矩阵，所以它们是不随规范变换的，这一点已经在上文证明过。

$$\Omega_I$$可以进一步写成

$$
\Omega_I=\sum_{n\alpha}\langle\mathbf{0}n|\sum_{m}|\mathbf{0}m\rangle\langle \mathbf{0}m|r_\alpha Qr_\alpha|\mathbf{0}n\rangle=Tr_{c}(Pr_\alpha Qr_\alpha)
$$

这里的角标 c 表示对单个晶格（cell）求迹，也就是只对能带指标求迹。可以看到$$\Omega_{I}$$只和$$P, Q$$有关，是规范不变的。我们还可以进一步证明规范不变的部分是非负的，具体来说，$$\Omega_{I}$$可以进一步写作$$Tr_{c}\left[(Pr_\alpha Q)(P r_\alpha Q)^{\dagger}\right]$$，

这显然是非负的，使用投影矩阵满足

$$
P^2=P, P^\dagger =P
$$

的性质不难证明该等式。

在布洛赫表象下，Wannier 函数的$$\mathbf{r}$$和$$\mathbf{r}^2$$的均值可以表示为：

$$
\langle\mathbf{R}n|\mathbf{r}|\mathbf{0}m\rangle=i\frac{V}{(2\pi)^2}\int d\mathbf{k}e^{i\mathbf{k}\cdot\mathbf{R}}\langle u_{n\mathbf{k}}|\nabla_{\mathbf{k}}|u_{m\mathbf{k}}\rangle,
$$

$$
\langle\mathbf{R}n|\mathbf{r}^2|\mathbf{0}m\rangle=-\frac{V}{(2\pi)^2}\int d\mathbf{k}e^{i\mathbf{k}\cdot\mathbf{R}}\langle u_{n\mathbf{k}}|\nabla^2_{\mathbf{k}}|u_{m\mathbf{k}}\rangle
$$

这里直接引用了文献[2]的结果。

这里对 k 的散度在 DFT 中，可以近似表示为相邻的 k 点的波函数之间的差分，具体来说就是：

$$\nabla f(\mathbf{k}) = \sum_{\mathbf{b}}\mathbf{b}\omega_b[f(\mathbf{k}+\mathbf{b})-f(\mathbf{k})]+O(b^2)$$,

这里的$$\mathbf{b}$$是$$\mathbf{k}$$指向相邻 k 点的向量，$$\omega_b$$是一个量纲为$$b^{-2}$$的常数权重参数，所以 spread 函数和他的导数都可以表示为布洛赫波函数中的周期性分量之间的内积，也就是

$$M_{mn}^{\mathbf{k}, \mathbf{b}}=\langle u_{m\mathbf{k}}|u_{n,\mathbf{k+b}}\rangle$$，

换句话说，密度泛函理论软件只需要提供$$M_{mn}^{\mathbf{k,b}}$$这个物理量，就可以通过优化得出最局域化的 Wannier 函数。

经过一系列推导，可以得到$$\Omega_I$$在布洛赫表象下的表达式：

$$
\Omega_I=\frac{1}{N}\sum_{\mathbf{k,b}}\omega_b \left(J-\sum_{mn}|M_{mn}^{(\mathbf{k, b})}|^2\right)=\frac{1}{N}\sum_{\mathbf{k,b}}\omega_b \mathrm{Tr}(P^{(\mathbf{k})}Q^{(\mathbf{k+b})})
$$

这里的$$P^{(\mathbf{k})}=\sum_{n}|u_{n\mathbf{k}}\rangle\langle u_{n\mathbf{k}}|$$，$$Q^{(\mathbf{k})}=1-P^{(\mathbf{k})}$$，$$J$$是能带数。

考虑到$$Tr(AB)=||A-B||^2/2$$，可以看到<strong>规范不变的 spread 函数衡量的是每个 k 点与其相邻 k 点上布洛赫波函数张成的线性空间的差别，</strong>可以看作是不同 k 点上的线性空间之间的“溢出函数” (spilage function)<strong>。</strong>换句话说，如果整个布里渊区内的 k 点上，布洛赫波函数张成的空间都一模一样，那么$$Tr(P^{\mathbf{k}}Q^{(\mathbf{k+b})})$$就是 0，规范不变部分的 spread 函数会直接消失，达到最小值。实际上，$$\Omega_I$$可以看作是这组孤立能带的本征态构成的线性空间的一个本征性质，所以不会随这个线性空间内的表象变换而变化。

在实际的计算中，spread 函数是作为一个整体优化的，但$$\Omega_I$$部分其实不会随优化改变，是一个固定的值。

## 2.3 纠缠能带的 Wannier 函数的 Spread 函数

2.2 部分简要叙述了对于一组孤立的能带，如何定义 spread 函数、如何将 spread 函数划分为规范不变和随规范变换的部分，以及 spread 函数在布洛赫表象下的表示。上述定义和划分在简并能带的情况是否依然成立呢？答案是肯定的，2001 年，Ivo Souza、Nicola Marzari 和 David Vanderbilt 共同在文献[3]提出了在一组纠缠的能带中抽取部分能带，对其 Wannier 函数做最大局域化的方法。Souza 等人提出了这样一个案例：对铜金属而言，其壳层电子 ($$3d^{10}4s^1$$)既包含 d 轨道电子也包含 s 轨道电子，直觉上说，d 轨道电子比较局域化，对应于能带中的窄带；s 轨道电子比较接近自由电子，对应于能带中的宽带。但实际上 s 轨道和 d 轨道发生了杂化，他们的能带是重叠在一起的，难以将 s 和 d 的能带、Wannier 函数区分开。这时，我们可以通过最大局域化 Wannier 函数的方式实现以上目的。

具体的做法是这样的，首先选取一个能量区间（energy window），这个区间包含 d 轨道的能带，也可以包含 s 轨道的能带。对于这个区间内的 k 点，如果只有 d 轨道的能带，就什么都不做；如果既含有 d 轨道也含有 s 轨道，就对这个 k 点的 d 轨道对应的$$\Omega_I$$做最小化。这相当于在 s 和 d 轨道的本征态构成的线性空间里优化 d 轨道构成的子空间$$S(\mathbf{k})$$，使该子空间与其他 k 点上的 d 轨道空间尽可能接近。完成这一步优化后，再按照优化独立能带的 Wannier 函数的办法优化$$\tilde\Omega$$。

完成优化后，可以通过 Slater-Koster 方法做内插值得到任意 k 点上的能带，从而实现对纠缠能带的解耦，在这个例子里就是可以把 d 轨道对应的能带和 s 轨道对应的能带分开，让他们各自长得像窄带和宽带。具体的做法可以参看文献[3] III F 部分和 IV 部分。

## 2.4 优化 Wannier 函数的 Spread 函数

在优化 spread 函数时，如果考虑的是纠缠能带中的一部分能带，就需要先优化$$\Omega_I$$，再优化$$\tilde\Omega$$；如果考虑的是孤立能带，直接优化$$\tilde\Omega$$。

### 2.4.1 通过自洽迭代方法优化$$\Omega_I$$

对于纠缠的能带中需要局域化的布洛赫波函数，需要优化的 spread 函数$$\Omega_I=\frac{1}{N_{kp}}\sum_{\mathbf{k, b}}\omega_b \sum_{m=1}^N \left[1-\sum_{n=1}^N |M_{mn}^{(\mathbf{k, b})}|^2\right]$$，其中$$N$$是考虑的能带数量，例如在铜的例子中，$$N=5$$。因为$$\Omega_I$$是对整个布里渊区求和的，各个 k 点耦合在一起，所以需要自洽迭代地对$$\Omega_I$$做优化。具体来说，在第 i 轮迭代，要求$$|u^{(i)}_{n\mathbf{k}}\rangle, n=1...N$$正交归一，同时$$u_{n\mathbf{k}}^{(i)}$$可以使$$\Omega_I^{(i)}$$达到极小，运用拉格朗日乘子法，写出变分方程：

$$
\frac{\delta\Omega_{I}^{(i)}}{\delta u^{(i)*}_{n\mathbf{k}}}+\sum_{n=1}^N \Lambda^{(i)}_{nm, \mathbf{k}}\frac{\delta}{\delta u_{m\mathbf{k}}^{(i)*}}[\langle u_{m\mathbf{k}}^{(i)}|u_{n\mathbf{k}}^{(i)}\rangle-\delta_{mn}]=0
$$

经过一系列线性代数操作（详细步骤在文献[3]III C 部分），得到最后的特征方程：

$$
\left[\sum_{\mathbf{b}}\omega_b \hat{P}_{\mathbf{k+b}}^{(i-1)}\right]|u_{m\mathbf{k}}^{(i)}\rangle=\lambda_{m\mathbf{k}}^{(i)}|u_{m\mathbf{k}}^{(i)}\rangle
$$

其中的$$\hat{P}_ {\mathbf{k+b}}^{(i-1)}$$是$$\mathbf{k+b}$$上的投影算符$$\hat{P}^{(i-1)}_ {\mathbf{k+b}}=\sum_{n=1}^{N}|u_{n\mathbf{k+b}}^{(i-1)}\rangle\langle u_{n\mathbf{k+b}}^{(i-1)}|$$。如果迭代不稳定，可以采用类似 charge mixing 的方法，线性混合前后两步迭代的$$\hat{P}_ {\mathbf{k+b}}$$，即$$[\hat{P}^{(i)}_ {\mathbf{k+b}}]_ {in}=\alpha\hat{P}_ {\mathbf{k+b}}^{(i-1)}+(1-\alpha)[\hat{P}_ {\mathbf{k+b}}^{(i-1)}]_ {in}$$，这里的$$[\hat{P}^{(i)}_ {\mathbf{k+b}}]_ {in}$$表示第 i 步迭代输入的投影算符，$$\hat{P}_{\mathbf{k+b}}^{(i-1)}$$表示第 i-1 步输出的投影算符。

在实际计算中，需要在特定的基组上把投影算符展开为矩阵做对角化，在这里选择的是选取的能量区间内原始的布洛赫函数$$u_{n\mathbf{k}}$$（这是必要的，因为优化算法本身不保证每次迭代得到的$$P_{\mathbf{k}}^{(i)}$$仍然落在原始布洛赫函数张成的线性空间里，这里选取基底相当于把新得到的投影算符投影到这个空间里，保证每次迭代得到的布洛赫函数仍在原始的线性空间范围内），所以最终需要对角化的矩阵是$$Z_{mn}^{(i)}(\mathbf{k})=\langle u_{m\mathbf{k}}|\sum_{\mathbf{b}}\omega_b[\hat{P}^{(i)}_{\mathbf{k+b}}]_{in}|u_{n\mathbf{k}}\rangle$$，这是一个大小为$$N\times N$$的厄米矩阵。每次自洽迭代中，需要对每个 k 点对角化$$Z_{mn}^{(i)}(\mathbf{k})$$，得到$$u_{n\mathbf{k}}^{(i)}$$；计算新的投影矩阵，进入下一次迭代。

最后还存在一个初始值$$Z_{mn}^{(0)}(\mathbf{k})$$如何选取的问题，这实际上是在选取初始的子空间$$S(\mathbf{k})$$。这里固然可以选择原始的布洛赫波函数$$u_{n\mathbf{k}}$$构成子空间，但是也可以有意地选择子空间使得其 Wannier 表象更接近我们的直觉认知。比如我们认为 Wannier 函数可能接近于一组名为$$g_n(\mathbf{r}), n=1...N$$的实空间基函数，那么就可以把每个 k 点上的布洛赫波函数投影到这组基函数上：$$|\phi_{n\mathbf{k}}\rangle=\sum_{m=1}^{N_{win}}A_{mn}^{(\mathbf{k})}|u_{m\mathbf{k}}\rangle$$，其中$$A_{mn}^{(\mathbf{k})}=\langle u_{m\mathbf{k}}|g_{n}\rangle$$，$$N_{win}$$是能量区间中总能带数。这样的投影轨道还不满足布洛赫波函数正交归一的要求，所以需要对其做正交归一化使其成为新的布洛赫波函数：$$|u_{n\mathbf{k}}^{(0)}\rangle=\sum_{m=1}^{N}(S^{-1/2})_{mn}|\phi_{m\mathbf{k}}\rangle=\sum_{m=1}^{N_{win}^{\mathbf{k}}}(AS^{-1/2})_{mn}|u_{m\mathbf{k}}\rangle$$

其中的重叠矩阵$$S_{mn}=S_{mn}^{\mathbf{k}}=\langle\phi_{m\mathbf{k}}|\phi_{n\mathbf{k}}\rangle=(A^{\dagger}A)_{mn}$$，这样就可以通过实空间中布洛赫波函数在一组预想的基函数上的投影给出来投影矩阵$$P_{k}$$的初猜，从而开始自洽迭代优化。

### 2.4.2 通过梯度下降方法优化$$\tilde \Omega$$

获得每个 k 点上需要考虑的布洛赫波函数张成的线性空间$$S(\mathbf{k})$$（也是获得每个 k 点上的投影矩阵$$P_{\mathbf{k}}$$）之后，就可以通过梯度下降法寻找使得 spread 函数最小的规范变换。这里的梯度下降不是对$$u_{n\mathbf{k}}$$做任意的梯度下降，因为需要满足新的$$u_{n\mathbf{k}}$$和原来的$$u_{n\mathbf{k}}$$之间的规范变换关系（幺正变换）。具体的做法是一次对布洛赫波函数做一个微小的转动$$U_{mn}^{(\mathbf{k})}=\delta_{mn}+dW_{mn}^{(\mathbf{k})}$$，其中$$dW_{mn}^{(\mathbf{k})}=-dW_{mn}^{(\mathbf{k})\dagger}$$是一个反厄米矩阵，从而满足$$U_{mn}^{(\mathbf{k})}$$是幺正的。经过一些推导（详细推导参考文献[1]的 IV B 部分），可以获得 spread 函数的梯度：

$$
G^{(\mathbf{k})}=\frac{d\Omega}{dW^{(\mathbf{k})}}=4\sum_{\mathbf{b}}\omega_b (\mathcal{A}[R^{(\mathbf{k,b})}]-\mathcal{S}[T^{(\mathbf{k,b})}])
$$

其中$$R^{(\mathbf{k,b})}=M_{mn}^{(\mathbf{k, b})}M_{nn}^{(\mathbf{k, b})*}, T_{mn}^{(\mathbf{k,b})}=\frac{M_{mn}^{(\mathbf{k,b})}}{M_{nn}^{(\mathbf{k,b})}}\cdot(\mathrm{Im} \ln{M_{nn}^{(\mathbf{k,b})}}+\mathbf{b}\cdot\overline{\mathbf{r}_n}), \overline{\mathbf{r}_n}=-\frac{1}{N}\sum_{(\mathbf{k,b})}\omega_{b}\mathbf{b}\mathrm{Im}\ln{M_{nn}}^{(\mathbf{k,b})}$$

在实际计算中，梯度下降的步长被设置为固定的$$\epsilon=\alpha/4\omega$$，其中$$\omega=\sum_{b}\omega_b$$，这样微扰矩阵$$\Delta W^{(\mathbf{k})}$$写作$$\Delta W^{(\mathbf{k})}=\frac{\alpha}{\omega}\sum_{\mathbf{b}}\omega_b (\mathcal{A}[R^{(\mathbf{k,b})}]-\mathcal{S}[T^{(\mathbf{k,b})}])$$，因为这个矩阵是反厄米的，所以波函数可以直接按照$$u_{n\mathbf{k}}\to e^{\Delta W^{(\mathbf{k})}}u_{n\mathbf{k}}$$变换，进入下一次迭代。这时 spread 函数的变化是$$d\Omega=-\frac{\alpha}{4\omega}\sum_{\mathbf{k}}||G^{(\mathbf{k})}||^2$$。

# 三、参考文献

1. Nicola Marzari and David Vanderbilt, Maximally localized generalized Wannier functions for composite energy bands, <em>Phys. Rev. B</em> <strong>56</strong>, 12847 (1997). (提出最大局域化 Wannier 函数方法的文献)
2. Blount, E. I., <em>Solid State Phys. </em><strong>13</strong>, 305 (1962). (关于 Bloch 状态的诸多基础性质的讨论，最大局域化中$$\langle n\mathbf{R}|\mathbf{r}|m\mathbf{0}\rangle$$在布洛赫表象下的表达式来源于此)
3. Ivo Souza, Nicola Marzari, and David Vanderbilt, Maximally localized generalized Wannier functions for entangled energy bands, <em>Phys. Rev. B</em>  <strong>65</strong>, 035109 (2001). (从纠缠能带中解耦出部分能带，做最大局域化 Wannier 函数的文献)
4. Arash A. Mostofi, Jonathan R. Yates, Young-Su Lee, Ivo Souza, David Vanderbilt, Nicola Marzari, wannier90: A tool for obtaining maximally-localised Wannier functions, <em>Comput. Phys. Commun.</em>, 178, 9, 685 (2008). (Wannier90 软件的初始文献)
