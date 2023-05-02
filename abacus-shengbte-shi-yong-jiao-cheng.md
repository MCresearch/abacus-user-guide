# ABACUS+ShengBTE 计算晶格热导率

<strong>作者：陈涛，邮箱：</strong><strong>chentao@stu.pku.edu.cn</strong><strong>，</strong><strong>最后更新</strong><strong>时间：2023/04/</strong><strong>29</strong>

# <strong>1. 介绍</strong>

本教程旨在介绍采用 ABACUS（基于 ABACUS 3.2.0 版本）做密度泛函理论计算，并且结合 ShengBTE 软件计算晶格的热导率的流程。其中，整个计算过程中还用到了：1）采用 Phonopy 程序来计算二阶力常数，2）采用 ASE 程序进行原子结构的转换，3）采用 ShengBTE 的 thirdorder 程序计算三阶力常数，4）最后使用 ShengBTE 来计算材料的晶格热导率。

上述提到了一些需要结合的外部软件，这里推荐大家阅读这些软件的相关文档和说明：

ShengBTE：[https://bitbucket.org/sousaw/shengbte/src/master/](https://bitbucket.org/sousaw/shengbte/src/master/)

phonopy：[http://abacus.deepmodeling.com/en/latest/advanced/interface/phonopy.html](http://abacus.deepmodeling.com/en/latest/advanced/interface/phonopy.html)

ASE：[http://abacus.deepmodeling.com/en/latest/advanced/interface/ase.html](http://abacus.deepmodeling.com/en/latest/advanced/interface/ase.html)

thirdorder: [https://bitbucket.org/sousaw/thirdorder/src/master/](https://bitbucket.org/sousaw/thirdorder/src/master/)

# <strong>2. 准备</strong>

ABACUS 的软件包中提供了一个 ABACUS+ShengBTE 计算晶格热导率的算例，可以从 Gitee 上[下载](https://gitee.com/mcresearch/abacus-user-guide/tree/master/examples/interface_ShengBTE)。算例中包含采用数值原子轨道的 LCAO（Linear Combination of Atomic Orbitals）和采用平面波基矢量的 PW（Plane wave，平面波）两个文件夹。每个文件夹下分别又包含了 2nd、3rd 和 shengbte 这三个文件夹，分别保存了使用 phonopy 计算二阶力常数（2nd）、thirdorder 计算三阶力常数（3rd）和 ShengBTE 计算晶格热导率（shengbte）的相关文件。

# <strong>3. 流程</strong>

以 LCAO 文件夹为例，我们这里提供的测试案例是包含 2 个原子的金刚石结构 Si 结构，采用的模守恒赝势是 Si_ONCV_PBE-1.0.upf，以及原子轨道文件采用的是 Si_gga_7au_100Ry_2s2p1d.orb（GGA 泛函，7 au 截断半径，100 Ry 能量截断，以及包含 2s2p1d 的 DZP 轨道）。

## 3.1 计算二阶力常数

要计算二阶力常数，除了 ABACUS 之外，还需要结合 Phonopy 和 ASE。首先，进入 2nd 文件夹。

### 3.1.1 结构优化

做晶格热导率计算之前要先对模拟的材料体系的进行原子构型的优化。下面是采用 ABACUS 做结构优化（relax）后得到的原子构型文件 STRU。在这个例子里，为了简单起见，结构优化过程采用的是 2\*2\*2 的布里渊区 k 点采样，平面波的能量截断值 ecut（LCAO 里面也用到了平面波基矢量）为 100 Ry，注意实际计算中应该要采用更收敛的 k 点采样。

```bash
ATOMIC_SPECIES
Si 28.0855 Si_ONCV_PBE-1.0.upf

NUMERICAL_ORBITAL
Si_gga_7au_100Ry_2s2p1d.orb

LATTICE_CONSTANT
1.88972612546

LATTICE_VECTORS
0 2.81594778072 2.81594778072 #latvec1
2.81594778072 0 2.81594778072 #latvec2
2.81594778072 2.81594778072 0 #latvec3

ATOMIC_POSITIONS
Direct # direct coordinate

Si #label
0 #magnetism
2 #number of atoms
0.875  0.875  0.875  m  0  0  0
0.125  0.125  0.125  m  0  0  0
```

注意：第一行 Si 的质量 28.0855 在计算中不起作用。

### 3.1.2 计算二阶力常数

调用 Phonopy 软件产生需要计算的超胞及相应微扰的多个原子构型，命令如下：

```bash
phonopy setting.conf --abacus -d
```

其中 setting.conf 文件的内容为：

```bash
DIM = 2 2 2
ATOM_NAME = Si
```

这里我们采用的 Si 的例子只需要产生 1 个微扰构型 STRU-001 即可，对所有微扰构型（这里 Si 的例子只有 1 个）进行 SCF 计算（SCF 代表 Self-consistent field，这里代表进行密度泛函理论的电子迭代自洽计算）获得原子受力，算完之后用以下命令产生 FORCE_SET 文件：

```bash
phonopy -f OUT.DIA-50/running_scf.log
```

小技巧：在 ABACUS 的输入文件 INPUT 中可以设置变量 stru_file，该变量对应的原子构型文件为 STRU-001 则 ABACUS 可以直接读取该结构文件。

下一步，设置 band.conf 文件计算得到声子谱以及二阶力常数：

```bash
phonopy -p band.conf --abacus
```

这里出现的 band.conf 文件，其内容如下（具体参数含义可以查看 Phonopy 说明文档）：

```bash
ATOM_NAME = Si
DIM = 2 2 2
MESH = 8 8 8
PRIMITIVE_AXES = 1 0 0 0 1 0 0 0 1
BAND = 0.0 0.0 0.0  0.5 0.0 0.5  0.625  0.25  0.625, 0.375 0.375 0.75  00 0.0 0.0  0.5 0.5 0.5
BAND_POINTS = 101
BAND_CONNECTION = .TRUE.
FORCE_CONSTANTS = WRITE
FULL_FORCE_CONSTANTS = .TRUE.
```

这一步结束之后，Phonopy 软件会产生 band.yaml（用于绘制声子谱）和 FORCE_CONSTANTS 文件。其中，FORCE_CONSTANTS 文件包含的数据即为二阶力常数，注意这里务必设置 FULL_FORCE_CONSTANTS = .TRUE.，输出全部的二阶力常数，否则 ShengBTE 读取数据会报错。

此外，可以使用如下命令输出 gnuplot 格式的声子谱，用于绘制声子谱：

```bash
phonopy-bandplot --gnuplot > pho.dat
```

### 3.1.3 后处理

注意 ShengBTE 软件要求 FORCE_CONSTANTS_2ND 文件里数据的单位为 eV/Å^2，但是 ABACUS 结合 phonopy 计算的 FORCE_CONSTANTS 单位为 eV/(Å\*au)，其中 au 是原子单位制，1 au=0.52918 Å。可以使用 2nd 目录下提供的 au2si.py 脚本进行单位转换，生成 FORCE_CONSTANTS_2ND 文件，命令如下：

```python
python au2si.py
```

在 shengbte 文件夹中提供了 FORCE_CONSTANTS_2ND 文件供参考计算结果。

## 3.2 计算三阶力常数

要计算三阶力常数，需要结合 thirdorder 程序，计算后输出三阶力常数文件 FORCE_CONSTANTS_3RD。但是，thirdorder 目前只支持读取 VASP 和 QE 的输入输出文件。因此，这里我们是通过将 ABACUS 的结构文件和输出受力分别转换为 POSCAR 和 vasprun.xml 来使用 thirdorder，请先进入 3rd 文件夹，具体步骤将在以下叙述。

### 3.2.1 获得微扰构型

首先将 ABACUS 软件进行结构优化（relax）后的 STRU 文件转化为 POSCAR（目录下已给出转化过的 POSCAR，或者需要自己动手进行这个转换）。

之后，运行 thirdorder_vasp 程序，产生微扰过后的一系列原子构型文件 3RD.POSCAR.\*，例如这个例子一共产生了 40 个构型：

```bash
thirdorder_vasp.py sow 2 2 2 -2
```

执行 pos2stru.py 命令，将上述 POSCAR 转化为 STRU 文件，注意该脚本里调用了 ASE 软件包的函数（需提前安装好 ASE）：

```python
python pos2stru.py
```

注意：这里不能调用 dpdata 软件进行转化。因为 dpdata 会强制将晶格改为下三角矩阵，相当于旋转了晶格，会导致原子间受力方向也相应旋转，从而发生错误。

### 3.2.2 计算微扰构型的原子受力

可以参考目录下 run_stru.sh 使用脚本批量产生 SCF-\* 文件夹并提交计算，这里需要采用 ABACUS 对 40 个原子构型分别进行 SCF 计算，会有些耗时。建议每个 SCF 单独在 SCF-\* 文件夹内运行，这里的 INPUT 中的<strong>scf_thr 需要至少</strong><strong>小到</strong><strong>1e-8</strong>才能得到收敛的结果。

计算完成后，运行 aba2vasp.py，将 ABACUS 计算的原子受力包装成 vasprun.xml 格式，放置在每个 SCF-\* 文件夹中，命令如下：

```python
python aba2vasp.py
```

vasprun.xml 格式示意：

```xml
<modeling>
    <calculation>
        <varray name="forces">
            <v>1.865e-05 -0.04644196 -0.00153852</v>
            <v>-1.77e-05 -0.00037715 -0.00149635</v>
            <v>1.973e-05 0.002213 -0.00149461</v>
            <v>-1.976e-05 0.00065303 -0.0014804</v>
            <v>8.31e-06 -0.0003306 -0.00024288</v>
            <v>-8.25e-06 -0.00038306 -0.00025385</v>
            <v>1.071e-05 0.00060621 -0.00025797</v>
            <v>-1.05e-05 -0.00014553 -0.00027532</v>
            <v>0.00668053 0.00645634 -0.04642593</v>
            <v>-0.00668085 0.00645595 -0.00040122</v>
            <v>-0.00650454 0.00628877 -0.00025123</v>
            <v>0.00650504 0.00628892 -0.00028948</v>
            <v>-0.00039591 2.479e-05 0.00223371</v>
            <v>0.00039608 2.426e-05 0.0006732</v>
            <v>0.0003264 3.122e-05 0.00052874</v>
            <v>-0.00032589 3.415e-05 -0.00023577</v>
            <v>-2.908e-05 -0.00832477 0.00635709</v>
            <v>3.737e-05 -0.00125057 -7.444e-05</v>
            <v>-2.582e-05 0.00656076 0.00636285</v>
            <v>2.566e-05 -0.00049974 -6.661e-05</v>
            <v>-5.431e-05 0.00502637 0.00639077</v>
            <v>4.553e-05 -0.00180978 0.0001325</v>
            <v>-3.609e-05 -0.00676473 0.00638092</v>
            <v>3.806e-05 5.503e-05 0.00012759</v>
            <v>-0.00670704 0.00646596 0.01310437</v>
            <v>0.00670119 3.673e-05 0.00602948</v>
            <v>0.00036366 0.00627899 -0.00657272</v>
            <v>-0.00036508 2.288e-05 0.00026009</v>
            <v>0.00648649 0.0064463 -0.00036521</v>
            <v>-0.00648098 1.594e-05 0.00671469</v>
            <v>-0.00034493 0.00630074 0.00662932</v>
            <v>0.00034331 4.157e-05 -0.0002028</v>
        </varray>
    </calculation>
</modeling>
```

最后执行如下命令：

```bash
find SCF-* -name vasprun.xml|sort -n|thirdorder_vasp.py reap 2 2 2 -2
```

即可得到三阶力常数文件 FORCE_CONSTANTS_3RD。在 shengbte 文件夹中提供了 FORCE_CONSTANTS_3rd 文件供参考计算结果。

## 3.3 运行 ShengBTE 得到晶格热导率

进入 shengbte 文件夹，里面已经准备好 CONTROL（ShengBTE 的参数文件）、FORCE_CONSTANTS_2ND（二阶力常数文件）、FORCE_CONSTANTS_3RD（三阶力常数文件）这三个文件，使用如下命令运行 ShengBTE 即可得到晶格热导率，其中 Ref 文件夹中给出了计算结果供参考：

```bash
mpirun -n 10 ShengBTE
```

# <strong>4. 结尾</strong>

对于 ABACUS 中使用平面波（PW）来做 ShengBTE 的计算也是采用以上类似的流程，但要注意使用平面波时，计算三阶力常数的 INPUT 中<strong>scf_thr 需要至少</strong><strong>小到</strong><strong>1e-12</strong>。通过计算结果可以发现，PW 和 LCAO 基组计算出的 Si 的晶格热导率是接近的，300 K 下均在 100 W/(m K) 左右，而实验中 Si 在 300 K 的热导率在 150 W/(m K) 附近。这是因为作为教学例子，这里使用的是 2\*2\*2 的扩胞以及 2\*2\*2 的 K 点，导致计算结果偏小，实际科研中需要测试扩胞的大小以及 K 点的采样方案来达到收敛的结果。以上就是 ABACUS(3.2.0)+ShengBTE 计算晶格热导率的全部流程，如果有什么问题，欢迎通过邮件联系（<strong>chentao@stu.pku.edu.cn</strong><strong> 或 </strong><strong>mohanchen@pku.edu.cn</strong>）。
