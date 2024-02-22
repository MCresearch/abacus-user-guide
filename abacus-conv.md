# ABACUS 收敛性问题解决手册

<strong>作者：周巍青，邮箱：zhouwq@aisi.ac.cn</strong>

<strong>单位：北京科学智能研究院（AISI）</strong>

<strong>最后更新日期：2024/2/22</strong>

<strong>如果遇到手册中无法解决的收敛性问题，欢迎给 ABACUS 提出 Issues，我们将持续更新这个文档</strong>

---

# 可选参数

## mixing_type

描述：混合电荷密度所使用的方法

可选：broyden，pulay，plain

<strong>默认值：broyden</strong>

说明：没有特殊理由，不建议更改这个参数

## mixing_ndim

描述：DIIS 混合计算混合系数时会保存的历史电荷密度数目

可选：int

<strong>默认值：8</strong>

说明：一般而言，这个值越大，收敛性越好，但是代价是内存消耗线性增加，8 一般是够用的。

## mixing_beta

描述：电荷密度的混合系数，1.0 时表示全部用输出电荷，0.0 时表示全部用输入电荷

可选：double

<strong>默认值：0.8（nspin=1）；0.4（nspin=2|4）</strong>

说明：一般而言，这个值越大，收敛越快，但是 SCF 跑飞不收敛的风险也越大；这个值越小，收敛越慢，但是收敛会更稳定，不收敛的情况会减少。

## mixing_gg0

描述：电荷密度混合时所做的 kerker 预处理的强度。Kerker 预处理会显著降低一些低频长程的电荷波动，对于金属性体系的收敛帮助极大。

可选：double

<strong>默认值：1.0</strong>

说明：默认 1.0 代表 ABACUS 默认打开 kerker 预处理，你可以手动设置成 0.0 将其关闭。一般而言，绝缘体/分子/原子体系中 kerker 预处理的效果不明显，甚至有负优化，可以关闭。

## mixing_gg0_min

描述：电荷密度的混合系数，所做的 kerker 预处理中，小于这一$|q|$的电荷分量不再进一步衰减

可选：double

<strong>默认值：0.1</strong>

说明：没有特殊理由，不建议更改这个参数

## mixing_beta_mag

描述：磁密度的混合系数，只在 nspin=2|4 时才会启用

可选：double

<strong>默认值：4*mixing_beta，但是最大不超过 1.6</strong>

说明：与电荷密度的混合类似，这个值越大，收敛越快，但是 SCF 跑飞不收敛的风险也越大；这个值越小，收敛越慢，但是收敛会更稳定，不收敛的情况会减少

## mixing_gg0_mag

描述：磁密度的混合时所做的 kerker 预处理的强度

可选：double

<strong>默认值：0.0</strong>

说明：默认 0.0 代表 ABACUS 默认关闭对磁密度的 kerker 预处理，你可以手动设置成非零将其打开。一般而言，对于磁密度的 Kerker 预处理物理意义并不明确，不建议打开。

## mixing_angle

描述：使用<strong>J. Phys. Soc. Jpn. 82 (2013) 114706</strong>中所描述的角度混合来更新电荷密度，只在非共线计算，即 nspin=4 时才可以启用

可选：double

<strong>默认值：0.0</strong>

说明：默认 0.0 代表 ABACUS 默认不使用这个方法，还是默认优先使用传统的 DIIS 混合。你可以手动设置成非零将其打开。这一方法可以解决非共线计算中磁矩收敛困难、收敛到错误磁态的问题。

## mixing_tau

描述：是否混合动能密度，只在 metaGGA 计算中才能使用

可选：bool

<strong>默认值：false</strong>

说明：ABACUS 默认不混合动能密度。但是打开一般会提升收敛性。

## mixing_dmr

描述：使用混合电荷密度的系数，同样混合密度矩阵。打开这一参数的前提必须同时设置 `mixing_restart`

可选：bool

<strong>默认值：false</strong>

说明：ABACUS 默认不混合密度矩阵。如果你在进行需要密度矩阵构建算符的计算，例如 DFT+U/EXX/DeePKS，你可以试图打开 `mixing_dmr`。经过我们大量的 DFT+U 算例测试，`mixing_dmr` 配合一个合适的 `mixing_restart` 会显著地提升 ABACUS 计算的收敛性。

## mixing_restart

描述：在第 `mixing_restart` 步 SCF 清空 mixing 的历史，直接使用上一步的输出作为这一步的输入，一般与 `mixing_dmr` 配合使用

可选：int

<strong>默认值：0</strong>

说明：ABACUS 默认不进行 restart，一个不适合的 `mixing_restart` 设置可能导致计算收敛不了。

# 如果收敛困难怎么办

## 非磁计算（nspin=1）

非磁实际上可调的自由度不多，<strong>所有体系</strong>都可以遵循的原则如下：

1. 尝试调小 `mixing_beta`
2. 尝试调大 `mixing_ndim`

分情况，你可以进一步有如下特殊的操作：

### 原子分子体系

原子分子的电荷高度局域，Kerker 预处理一般都难以实际取得正优化，你可以选择<strong>关闭 Kerkerk 预处理，</strong><strong>mixing_gg0=0.0</strong><strong>。</strong>

### 半导体/绝缘体

虽然绝缘体部分电子态也很局域，但是 Kerker 预处理一般是安全的，即使负优化也不会很严重，但是你仍可以选择<strong>关闭 Kerkerk 预处理，</strong><strong>mixing_gg0=0.0</strong><strong>。</strong>

### 金属

调节不同的 `mixing_gg0`、`mixing_gg0_min`。

### metaGGA 计算

打开 `mixing_tau=true`。一般会解决 metaGGA 收敛困难，以及 `EDIFF` 慢于 `DRHO` 的问题。

### 检查初始构型

一般而言，你不会在非磁计算遇到收敛性问题。如果真的遇到了，有很大概率初始构型太差，你可以调整构型，或者用先用宽松的收敛判据做几步弛豫计算，让体系构型更合理之后再调小 `scf_thr`。

## 共线磁性计算（nspin=2）

磁性计算中<strong>所有体系</strong>都可以遵循的原则如下：

1. 尝试调小 `mixing_beta`，并等比例调小 `mixing_beta_mag`
2. 尝试调大 `mixing_ndim`

分情况，你可以进一步有如下特殊的操作：

### 原子分子体系

孤立体系的磁性计算如果出现无法收敛，那大概率是出现一种极端的情况，即某一自旋全部来自某一轨道，不会叠加态。这种情况一旦出现，默认参数无法收敛。这时，请保证电荷密度和磁密度的混合系数完全一致：

```
mixing_beta      0.4
mixing_beta_mag  0.4
mixing_gg0       0.0
mixing_gg0_mag   0.0
```

相信这个设置之后，问题就会解决。

### 半导体/绝缘体

与非磁建议一致。

### 金属

与非磁建议一致。

### metaGGA 计算

打开 `mixing_tau=true`。一般会解决 metaGGA 收敛困难，以及 `EDIFF` 慢于 `DRHO` 的问题。

### DFT+U 计算

如果你的 DFT+U 计算无法收敛，我们推荐你做如下设置：

```
mixing_restart   10
mixing_dmr       1
```

`mixing_restart`=10 代表 SCF 的计算会在第 10 步直接用第 9 步的输出电荷开启一个新的 SCF，在那之后 DFT+U 的计算同时也会混合密度矩阵。在大多数情况下，10 是一个安全有效的设置，但请务必记住 `mixing_restart` 的设置是危险的，设置之后，你可能会遇到：

1. 本来不设置这 2 个参数还可以收敛，只是收敛的不快，设置之后完全不能收敛了。

答：那是因为 `mixing_restart` 的位置选取不合适，在 `mixing_restart` 前一步的输出密度很差，用其做初始密度使得计算直接跑飞。这个时候，我们建议你观察不开 `mixing_restart` 时候，`drho` 的收敛曲线，找一个距离基态近一些的位置做 `mixing_restart`（例如 `drho<10^-3`）。

1. 本来不能收敛，设置这 2 个参数之后，仍然不能收敛

答：大概率是 `mixing_restart` 的晚了，此时 SCF 已经跑飞，结合 `drho` 的收敛曲线，适当提前 `mixing_restart` 的位置。

### 弛豫计算

在弛豫计算中可以分多步做 relax，会使用上一步的 SCF 的磁矩做下一步优化的初始磁矩。这样对于弛豫计算的收敛性帮助巨大。

## 非共线磁性计算（nspin=4）

在使用传统的 DIIS 计算时，即 `mixing_angle=0.0`，参数建议与共线磁性一致。但是如果尝试之后，仍难以收敛，或收敛到错误的磁态，那么我们建议你进行如下的设置：

```
mixing_angle    1.0
```

我们实现了<strong>J. Phys. Soc. Jpn. 82 (2013) 114706</strong>中的新方法，这个方法寻找非共线基态的能力大大强于传统的 DIIS 混合。相信会对你有帮助。

# 其他 FAQ

## 我可以在 STRU 中不设置初始磁矩，就设置成 0 吗？

答：可以。当 STRU 中所有元素的初始磁矩都是 0 的时候，我们会自动为体系中的所有原子都赋予大小为 1 a.u.的原子磁矩。但是我们仍建议你设置它，因为一个好的初始磁矩对于计算的收敛速度和正确性都有巨大的帮助。

## 我可以在计算中设置 NUPDOWN 来帮助收敛吗？

答：可以。一个合理的 NUPDOWN 设置一般会使得计算收敛地比较稳定。<strong>但是</strong>这么做的前提是，一定要对所做的体系很可靠的先验知识。
