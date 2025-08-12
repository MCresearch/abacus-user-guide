# ABACUS对比CP2K精度和效率测试 | Si的状态方程（EOS）

**作者：John Yan (AISI电子结构团队实习生)，邮箱：csuyanzhuang@gmail.com**

**最后更新时间：2024/07/12**

**注意！本文中文文档维护者从原始Notebook版本手动逐块转换校对得到，为了保证阅读体验，建议访问原始Notebook页面进行阅读。链接：https://www.bohrium.com/notebooks/77351186918**

# 零、写在前面

Kohn-Sham密度泛函理论计算的关键一步就是选择合适的基组对KS方程进行参数化，将其转换为本征值求解问题。不同的基组选择，将极大影响计算的精度和效率。最为常见的选择是平面波基组，优点是体系精度可以随着平面波数量系统性增加，但是巨大的基组数量也限制了可计算体系的尺寸大小，一般限制在1000个原子以内。选择局域基组可以显著的增加可计算体系的大小，在一定精度的保证下，大幅提升计算的效率。计算软件 **CP2K**支持局域的高斯基组GTOs来进行计算，广泛地应用于计算化学领域。而国产开源密度泛函理论计算软件ABACUS除了平面波基组之中，还良好支持数值原子轨道基组。这一系列的教程通过使用**ABACUS**的LCAO基组和**CP2K**的GTOs基组的结果进行系统的测试，我们相信这可以帮助熟悉**CP2K**的用户快速建立起对**ABACUS**计算结果的认知和信心。

# 一、对比工作流程介绍

对比的**精度指标**：以全电子计算的Si体系的EOS作为精度对标参考，将cp2k和abacus计算的eos与其进行比较，计算delta数值，数值越大表明精度越低。

对比的**效率指标**：完成计算的时间，cp2k用时读取自output.log中Timing-Total time，abacus用时读取自log中的TIME STATISTICS-TIME-total

* Step1:构建精度对标参考：使用ELK进行Si的EOS计算（包括k点收敛性测试）

* Step2:使用cp2k常用的赝势和基组进行Si的EOS计算（包括k点、cutoff、rel_cutoff收敛性测试）

* Step3:基于cp2k使用的赝势生成abacus可以读取的upf赝势、并基于此赝势生成轨道文件（包括ecutwfc收敛性测试）

* Step4:基于以上赝势和轨道文件分别进行ABACUS的Si的eos的pw和lcao计算（包括k点收敛性测试）

* Step5:总结精度和效率指标进行比较

# 二、准备文件介绍

为了确保ABACUS、CP2K和ELK计算的结果具有可比较性，需要对参数进行对齐，目前总结了以下关键参数需要对齐：

* 任务类型
    scf计算对应的参数

    elk：tasks 0

    cp2k：RUNTYPE ENERGY

    abacus：calculation scf

* 晶胞信息：
统一通过ATOMKIT工具由相应的cif文件生成

* 泛函类型：
pbe泛函对应的参数

    elk：xctype 20

    cp2k：XC_FUNCTIONAL PBE

    abacus：dft_functional PBE

* k点：
根据k点收敛性测试结果进行对齐

    elk：ngirdk  7, 7, 7

    cp2k：KPOINT  7, 7, 7

    abacus：kspacing 0.10 (对应的k点为7, 7, 7)

* 新旧电荷密度混合方法：
broydpm方法对应的参数

    elk：mixtype 3

    cp2k：&MIXING METHOD BROYDEN_MIXING

    abacus：mixing_type broyden


此外还有自旋极化、自旋轨道耦合等参数，可以参考官网的关键词手册，这里不进行详细介绍。

进入项目目录，使用tree命令查看文件结构，当前目录包括四个子目录，分别包含abacus部分的工作、cp2k部分的工作、elk部分的工作以及summary总结工作。其中需要准备的输入文件是elk的elk.in(类似INPUT文件)、Si.in(描述元素性质的文件)，cp2k的input.inp文件，abacus的INPUT文件、STRU文件。

```shell
# 进入工作目录，使用tree命令查看文件结构
!cd /root/abacus_benchmark_demo  && tree -L 2
```

```text
.
├── abacus
│   ├── abacus_eos
│   ├── abacus_kconv
│   ├── abacus_orb_gen
│   ├── abacus_pw_ecutconv
│   ├── abacus_pw_eos
│   └── abacus_upf_gen
├── cp2k
│   ├── cp2k_cutoffconv
│   ├── cp2k_eos
│   ├── cp2k_kconv
│   └── cp2k_relcutoffconv
├── elk
│   ├── elk_eos
│   ├── elk_kconv
│   └── elk_rgkmax_conv
└── summary
    ├── summary.csv
    ├── summary.py
    ├── summary_eos.png
    └── summary_table.png

17 directories, 4 files
```
# 三、使用ELK进行Si的EOS的全电子计算

我们需要确定精度的标定标准。对于使用赝势的DFT软件，最好的选择是使用全电子计算软件的计算结果作为参考。这里我们使用ELK进行Si的EOS计算（另外的例子也可见ABINIT：https://docs.abinit.org/tutorial/paw3/ ），首先对ELK进行k点收敛性测试。

## ELK的K点收敛性测试

进入工作目录，查看文件

```shell
!cd /root/abacus_benchmark_demo/elk/elk_kconv && ls
```

```text
Si.in	       elk_kconv.png  elk_si_k10  elk_si_k4  elk_si_k7
elk.in	       elk_kconv.py   elk_si_k2   elk_si_k5  elk_si_k8
elk_kconv.csv  elk_si_k1      elk_si_k3   elk_si_k6  elk_si_k9
```

查看输入文件Si.in模版，以下任务需要修改其中的ngridk字段

```shell
!cat /root/abacus_benchmark_demo/elk/elk_kconv/elk.in
```

```text
tasks
0

xctype
20

sppath
  './'

avec
    1.8897260000    0.0000000000    0.0000000000
    0.0000000000    1.8897260000    0.0000000000
    0.0000000000    0.0000000000    1.8897260000

scale
5.43070000

atoms
    1                : nspecies
  'Si.in'            : spfname
    8
     0.0000000000    0.0000000000    0.0000000000    0.000    0.000    0.000
     0.0000000000    0.5000000000    0.5000000000    0.000    0.000    0.000
     0.5000000000    0.0000000000    0.5000000000    0.000    0.000    0.000
     0.5000000000    0.5000000000    0.0000000000    0.000    0.000    0.000
...
tempk
300

ngridk
  1  1  1
```

查看自动修改k点创建子目录、运行elk计算、回收elk结果并可视化的python脚本

```shell
!cat /root/abacus_benchmark_demo/elk/elk_kconv/elk_kconv.py
```

```python
import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt

# 获取当前目录
current_dir = os.getcwd()

# 要复制的文件列表
files_to_copy = ['elk.in', 'Si.in']

# 初始化列表来存储数据
data = []

# 创建子目录并复制文件，修改elk.in文件中的ngridk值
for i in range(10):
    kpoints_value = 1 + i  # 步长调整为1
    sub_dir_name = f'elk_si_k{kpoints_value}'
    sub_dir_path = os.path.join(current_dir, sub_dir_name)

    # 创建子目录
    os.makedirs(sub_dir_path, exist_ok=True)

    # 复制文件到子目录
    for file_name in files_to_copy:
...
plt.savefig('elk_kconv.png')  # 保存图形
plt.show()  # 显示图形

print("所有子目录创建、文件修改、计算任务和数据处理完成。")
```

运行这行代码会自动进行具有不同k点的计算

```shell
!cd /root/abacus_benchmark_demo/elk/elk_kconv && python /root/abacus_benchmark_demo/elk/elk_kconv/elk_kconv.py
```

根据收敛曲线以及下文中abacus和cp2k的k点收敛结果，选定k点为（7，7，7）

## ELK的rgkmax收敛性测试

rgkmax是elk所采用的FP-LAPW方法中muffin-tin potential实空间的半径（记作rmt）与平面波G+k（记作gk）的乘积。因此测试rgkmax的收敛等同于测试平面波基组的数量。进入工作目录，查看文件

```shell
!cd /root/abacus_benchmark_demo/elk/elk_rgkmax_conv  && ls
```

```text
Si.in		     elk_rgkmax_conv.png  elk_si_rgk3  elk_si_rgk6  elk_si_rgk9
elk.in		     elk_rgkmax_conv.py   elk_si_rgk4  elk_si_rgk7
elk_rgkmax_conv.csv  elk_si_rgk10	  elk_si_rgk5  elk_si_rgk8
```

自动化EOS计算脚本如下

```python
import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import re
import csv

# 定义提取总时间的函数
def extract_total_time(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # 定义正则表达式来匹配 Timings (CPU seconds) 部分的 total 值
    match = re.search(r'total\s*:\s*([\d\.]+)', content)
    if match:
        return float(match.group(1))  # 返回 total 对应的数值
    else:
        return None

# 保存INFO.OUT提取的数据到CSV文件
def save_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Directory', 'Total Time (CPU seconds)'])
        writer.writerows(data)
...
save_to_csv(timing_data, 'elk_time.csv')

print("所有子目录创建、文件修改、计算任务和数据处理完成。")
print(f'计算时间数据已保存到 elk_time.csv')
```

运行计算与数据回收脚本

```shell
!cd /root/abacus_benchmark_demo/elk/elk_rgkmax_conv  && python /root/abacus_benchmark_demo/elk/elk_rgkmax_conv/elk_rgkmax_conv.py
```

## ELK的Si的EOS计算

进入工作目录，查看文件

```shell
!cd /root/abacus_benchmark_demo/elk/elk_eos && ls
```

```text
Si.in	     Si_eos_5.40  Si_eos_5.70  elk.in	    elk_eos.py
Si_eos_5.20  Si_eos_5.50  Si_eos_5.80  elk_eos.csv  elk_time.csv
Si_eos_5.30  Si_eos_5.60  Si_eos_5.90  elk_eos.png
```

运行自动化eos计算脚本，进行eos计算和结果回收（需要十分钟左右）

```shell
!cd /root/abacus_benchmark_demo/elk/elk_eos && python /root/abacus_benchmark_demo/elk/elk_eos/elk_eos.py
```

# 四、使用CP2K基于GTH-PBE赝势和DZVP-GTH-q4基组进行Si的EOS计算

选定cp2k常用的GTH-PBE赝势和DZVP-GTH-q4基组进行Si的EOS计算，在EOS计算前需要进行k点、CUTOFF、REL_CUTOFF收敛性测试。

## CP2K的K点收敛性测试

进入工作目录，查看文件

```shell
! cd /root/abacus_benchmark_demo/cp2k/cp2k_kconv && ls
```

```text
cp2k_Si_kpoints_1   cp2k_Si_kpoints_4  cp2k_Si_kpoints_8  cp2k_kconv.py
cp2k_Si_kpoints_10  cp2k_Si_kpoints_5  cp2k_Si_kpoints_9  input.inp
cp2k_Si_kpoints_2   cp2k_Si_kpoints_6  cp2k_kconv.csv
cp2k_Si_kpoints_3   cp2k_Si_kpoints_7  cp2k_kconv.png
```

查看输入文件模版input.inp

```text
&GLOBAL
  PROJECT Si
  PRINT_LEVEL MEDIUM
  RUN_TYPE ENERGY
&END GLOBAL

&FORCE_EVAL
  METHOD Quickstep
         &SUBSYS
      &CELL
            A [angstrom]   5.43070000   0.00000000   0.00000000
            B [angstrom]   0.00000000   5.43070000   0.00000000
            C [angstrom]   0.00000000   0.00000000   5.43070000
         PERIODIC XYZ
      &END CELL
      &COORD
         SCALED
            Si   0.00000000   0.00000000   0.00000000
            Si   0.00000000   0.50000000   0.50000000
            Si   0.50000000   0.00000000   0.50000000
            Si   0.50000000   0.50000000   0.00000000
            Si   0.75000000   0.75000000   0.25000000
            Si   0.75000000   0.25000000   0.75000000
            Si   0.25000000   0.75000000   0.75000000
            Si   0.25000000   0.25000000   0.25000000
...
      &END PRINT
    &END SCF
  &END DFT
&END FORCE_EVAL
```

查看收敛性测试脚本

```python
import os
import shutil
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt

# 获取当前目录
current_dir = os.getcwd()

# 要复制的文件列表
files_to_copy = ['input.inp']

# 初始化列表来存储数据
data = []

# 创建子目录并复制文件，修改input.inp文件中的KPOINTS字段的值
for i in range(10):
    kpoints_value = i + 1  # KPOINTS的递增值
    sub_dir_name = f'cp2k_Si_kpoints_{kpoints_value}'  # 根据kpoints_value命名子目录
    sub_dir_path = os.path.join(current_dir, sub_dir_name)
    # 创建子目录
    os.makedirs(sub_dir_path, exist_ok=True)

    # 复制文件到子目录
...
plt.savefig('cp2k_kconv.png')  # 保存图形
plt.show()  # 显示图形

print("所有子目录创建、文件修改、计算任务和数据处理完成。")
```

根据k点收敛曲线，选定k点为（7，7，7）

## CP2K的CUTOFF收敛性测试

进入工作目录，查看文件

```shell
! cd /root/abacus_benchmark_demo/cp2k/cp2k_cutoffconv && ls
```

```text
cp2k_cutoff_100  cp2k_cutoff_350  cp2k_cutoff_600      cp2k_cutoffconv.png
cp2k_cutoff_150  cp2k_cutoff_400  cp2k_cutoff_650      cp2k_cutoffconv.py
cp2k_cutoff_200  cp2k_cutoff_450  cp2k_cutoff_700      input.inp
cp2k_cutoff_250  cp2k_cutoff_500  cp2k_cutoff_750
cp2k_cutoff_300  cp2k_cutoff_550  cp2k_cutoffconv.csv
```

运行计算并回收结果

```shell
!cd /root/abacus_benchmark_demo/cp2k/cp2k_cutoffconv && python /root/abacus_benchmark_demo/cp2k/cp2k_cutoffconv/cp2k_cutoffconv.py
```

根据收敛性曲线，选定CUTOFF为300 Hartree。

## CP2K的REL_CUTOFF收敛性测试

进入工作目录，查看文件

```shell
! cd /root/abacus_benchmark_demo/cp2k/cp2k_relcutoffconv && ls
```

```text
cp2k_relcutconv.png  cp2k_relcutoff_40	cp2k_relcutoff_70	input.inp
cp2k_relcutoff_20    cp2k_relcutoff_50	cp2k_relcutoffconv.csv
cp2k_relcutoff_30    cp2k_relcutoff_60	cp2k_relcutoffconv.py
```

运行计算并回收结果

```shell
!cd /root/abacus_benchmark_demo/cp2k/cp2k_relcutoffconv && python /root/abacus_benchmark_demo/cp2k/cp2k_relcutoffconv/cp2k_relcutoffconv.py
```

根据收敛曲线，选定收敛REL_CUTOFF为50 Hartree。

## CP2K的Si的EOS计算

进入工作目录，查看文件

```shell
! cd /root/abacus_benchmark_demo/cp2k/cp2k_eos && ls
```

```text
Si_eos_5.20  Si_eos_5.50  Si_eos_5.80	cp2k_eos.png   input.inp
Si_eos_5.30  Si_eos_5.60  Si_eos_5.90	cp2k_eos.py
Si_eos_5.40  Si_eos_5.70  cp2k_eos.csv	cp2k_time.csv
```

运行计算并回收结果

```shell
!python /root/abacus_benchmark_demo/cp2k/cp2k_eos/cp2k_eos.py
```

# 五、使用ABACUS基于由CP2K的GTH-PBE赝势生成的赝势进行Si的EOS计算

为了对齐赝势，可以将cp2k使用的GTH-PBE赝势通过ATOM模块转换成abacus可读取的upf赝势文件进行直接比较，并且可以基于此生成的赝势进一步生成轨道文件，进行lcao计算。

## 基于CP2K的GTH-PBE赝势生成ABACUS可读取的upf赝势文件

进入工作目录，查看文件

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_upf_gen && ls
```

```text
PROJECT-Si.UPF-1.upf  Si.inp  Si.out
```

查看生成upf赝势任务的输入文件

```shell
!cat /root/abacus_benchmark_demo/abacus/abacus_upf_gen/Si.inp
```

```text
&GLOBAL
  PROGRAM_NAME ATOM
&END GLOBAL
&ATOM
  ELEMENT  Si
  ELECTRON_CONFIGURATION CORE 3s2 3p2
  CORE [Ne]
  &METHOD
     METHOD_TYPE  KOHN-SHAM
     &XC
       &XC_FUNCTIONAL PBE
       &END XC_FUNCTIONAL
     &END XC
  &END METHOD
  &PP_BASIS
    BASIS_TYPE GEOMETRICAL_GTO
  &END PP_BASIS
  &POTENTIAL
    PSEUDO_TYPE GTH
    &GTH_POTENTIAL
    2    2
     0.44000000    1    -6.26928833
    2
     0.43563383    2     8.95174150    -2.70627082
                                        3.49378060
...
    &UPF_FILE
      FILENAME Si.UPF
    &END
  &END
&END ATOM
```

运行代码并得到对应的赝势upf文件

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_upf_gen && mpirun -np 8 /root/cp2k/exe/local/cp2k.popt -i Si.inp -o Si.out
```

查看生成的赝势的前15行

```python
!head -15 /root/abacus_benchmark_demo/abacus/abacus_upf_gen/PROJECT-Si.UPF-1.upf
```

```text
<UPF version="2.0.1">
   <PP_INFO>
       Converted from CP2K GTH format
       <PP_INPUTFILE>
Si
    2    2    0    0
    0.44000000000000       1   -6.26928833000000
       2
    0.43563383000000       2    8.95174150000000   -2.70627082000000
                                                    3.49378060000000
    0.49794218000000       1    2.43127673000000
       </PP_INPUTFILE>
   </PP_INFO>
   <PP_HEADER
       generated="Generated in analytical, separable form"
```

## 基于生成的赝势文件进行平面波计算确定生成轨道的截断能

进入工作目录，查看文件

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_pw_ecutconv && ls
```

```text
INPUT			 abacus_si_ecutwfc130.00  abacus_si_ecutwfc210.00
PROJECT-Si.UPF-1.upf	 abacus_si_ecutwfc140.00  abacus_si_ecutwfc30.00
STRU			 abacus_si_ecutwfc150.00  abacus_si_ecutwfc40.00
abacus_pw_ecutconv.csv	 abacus_si_ecutwfc160.00  abacus_si_ecutwfc50.00
abacus_pw_ecutconv.png	 abacus_si_ecutwfc170.00  abacus_si_ecutwfc60.00
abacus_pw_ecutconv.py	 abacus_si_ecutwfc180.00  abacus_si_ecutwfc70.00
abacus_si_ecutwfc100.00  abacus_si_ecutwfc190.00  abacus_si_ecutwfc80.00
abacus_si_ecutwfc110.00  abacus_si_ecutwfc20.00   abacus_si_ecutwfc90.00
abacus_si_ecutwfc120.00  abacus_si_ecutwfc200.00  cp2k_gen_gth_pbe_si.upf
```

运行abacus的pw计算并回收计算结果

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_pw_ecutconv && python /root/abacus_benchmark_demo/abacus/abacus_pw_ecutconv/abacus_pw_ecutconv.py
```

根据能量收敛曲线选定Ecutwfc为100 Ry。

## 基于生成的upf赝势文件生成相应的orb轨道文件

由于cp2k生成的赝势文件的<PP_INFO>部分目前无法正常读取，需要将其他赝势文件的<PP_INFO>复制过来，例如从Si_ONCV_PBE-1.0.upf文件中复制。
另外需要将生成赝势文件中的functional="DFT"修改为functional="PBE"

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_orb_gen && tree -L 1
```

```text
.
├── PROJECT-Si.UPF-1.upf
├── SIAB
├── SIAB_INPUT.json
├── Si-dimer-1.75
├── Si-dimer-2.00
├── Si-dimer-2.25
├── Si-dimer-2.75
├── Si-dimer-3.75
├── Si-monomer
├── Si-trimer-1.90
├── Si-trimer-2.10
├── Si-trimer-2.60
├── Si_1s1p
├── Si_2s2p1d
├── Si_3s3p2d
├── Si_ONCV_PBE-1.0.upf
├── cp2k_gen_gth_pbe_si.upf
└── pp_info_modify.py

13 directories, 5 files
```

```shell
!head -15 /root/abacus_benchmark_demo/abacus/abacus_orb_gen/PROJECT-Si.UPF-1.upf 
```

```text
<UPF version="2.0.1">
   <PP_INFO>
       Converted from CP2K GTH format
       <PP_INPUTFILE>
Si
    2    2    0    0
    0.44000000000000       1   -6.26928833000000
       2
    0.43563383000000       2    8.95174150000000   -2.70627082000000
                                                    3.49378060000000
    0.49794218000000       1    2.43127673000000
       </PP_INPUTFILE>
   </PP_INFO>
   <PP_HEADER
       generated="Generated in analytical, separable form"
```

运行以下脚本可以自动将原upf文件的</PP_INFO>更新，并保存为cp2k_gen_gth_pbe_si.upf

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_orb_gen && python /root/abacus_benchmark_demo/abacus/abacus_orb_gen/pp_info_modify.py
```

查看修改后的upf文件的前15行

```shell
!head -15 /root/abacus_benchmark_demo/abacus/abacus_orb_gen/cp2k_gen_gth_pbe_si.upf
```

```text
<UPF version="2.0.1">
   <PP_INFO>

 This pseudopotential file has been produced using the code
 ONCVPSP  (Optimized Norm-Conservinng Vanderbilt PSeudopotential)
 scalar-relativistic version 2.1.1, 03/26/2014 by D. R. Hamann
 The code is available through a link at URL www.mat-simresearch.com.
 Documentation with the package provides a full discription of the
 input data below.


 While it is not required under the terms of the GNU GPL, it is
 suggested that you cite D. R. Hamann, Phys. Rev. B 88, 085117 (2013)
 in any publication using these pseudopotentials.
```

查看使用upf文件生成lcao轨道文件的配置文件

```shell
!cat /root/abacus_benchmark_demo/abacus/abacus_orb_gen/SIAB_INPUT.json
```

```json
{
    "pseudo_dir": "./",
    "ecutwfc": 100.0,
    "pseudo_name": "cp2k_gen_gth_pbe_si.upf",
    "bessel_nao_rcut": [
        6,
        7,
        8,
        9,
        10
    ],
    "smearing_sigma": 0.01,
    "optimizer": "bfgs",
    "max_steps": 5000,
    "spill_coefs": [
        0.0,
        1.0
    ],
    "spill_guess": "atomic",
    "nthreads_rcut": 4,
    "jY_type": "reduced",
    "reference_systems": [
        {
            "shape": "dimer",
            "nbands": "auto",
...
    ],
    "environment": "",
    "mpi_command": "mpirun -np 16",
    "abacus_command": "abacus"
}
```

运行以下脚本可实现轨道的生成，c16m32 cpu节点运行大约需要1小时时间，不建议取消注释运行。
注：如遇到无法执行情况，可通过下方SSH连接方式直接运行轨道生成文件。

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_orb_gen && /root/miniconda3/envs/orbgen/bin/python  SIAB/SIAB_nouvelle.py -i SIAB_INPUT.json
```

```shell
!python /root/abacus_benchmark_demo/abacus/abacus_orb_gen/SIAB/SIAB_nouvelle.py -i /root/abacus_benchmark_demo/abacus/abacus_orb_gen/SIAB_INPUT.json
```

查看输出的轨道文件的前20行，以Si_gga_7au_100.0Ry_2s2p1d.orb为例

```shell
! head -20 /root/abacus_benchmark_demo/abacus/abacus_orb_gen/Si_2s2p1d/7au_100.0Ry/Si_gga_7au_100.0Ry_2s2p1d.orb
```

```text
---------------------------------------------------------------------------
Element                     Si
Energy Cutoff(Ry)           100.0
Radius Cutoff(a.u.)         7
Lmax                        2
Number of Sorbital-->       2
Number of Porbital-->       2
Number of Dorbital-->       1
---------------------------------------------------------------------------
SUMMARY  END

Mesh                        701
dr                          0.01
                Type                   L                   N
                   0                   0                   0
  -9.94327772020867e-03  -9.85918654232421e-03  -9.60697963972621e-03  -9.18685682932890e-03
  -8.59915088530649e-03  -7.84432715863854e-03  -6.92298304561070e-03  -5.83584730639540e-03
  -4.58377923515861e-03  -3.16776768343987e-03  -1.58892993885413e-03   1.51489538554255e-04
   2.05212051968615e-03   4.11146854661615e-03   6.32791660654468e-03   8.69972693610516e-03
   1.12250429524361e-02   1.39018913072218e-02   1.67281840597182e-02   1.97017209646062e-02
```

## ABACUS的K点收敛性测试

进入工作目录，查看文件

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_kconv && ls
```

```text
INPUT			       abacus_si_kspacing0.02  abacus_si_kspacing0.14
STRU			       abacus_si_kspacing0.04  abacus_si_kspacing0.16
Si_gga_7au_100.0Ry_2s2p1d.orb  abacus_si_kspacing0.06  abacus_si_kspacing0.18
abacus_kconv.csv	       abacus_si_kspacing0.08  abacus_si_kspacing0.20
abacus_kconv.png	       abacus_si_kspacing0.10  abacus_si_kspacing0.22
abacus_kconv.py		       abacus_si_kspacing0.12  cp2k_gen_gth_pbe_si.upf
```

运行代码可进行abacus计算和结果回收

```shell
cd /root/abacus_benchmark_demo/abacus/abacus_kconv && python /root/abacus_benchmark_demo/abacus/abacus_kconv/abacus_kconv.py
```

根据收敛曲线，参考elk和cp2k的设置，以下计算中kspacing选取0.10，对应k点为（7，7，7）

## ABACUS的Si的EOS计算（lcao）

进入工作目录，查看文件

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_eos && ls
```

```text
INPUT			       abacus_Si_eos_5.50  abacus_eos.png
STRU			       abacus_Si_eos_5.60  abacus_eos.py
Si_gga_7au_100.0Ry_2s2p1d.orb  abacus_Si_eos_5.70  abacus_time.csv
abacus_Si_eos_5.20	       abacus_Si_eos_5.80  cp2k_gen_gth_pbe_si.upf
abacus_Si_eos_5.30	       abacus_Si_eos_5.90
abacus_Si_eos_5.40	       abacus_eos.csv
```

运行abacus的eos计算并回收结果

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_eos && python /root/abacus_benchmark_demo/abacus/abacus_eos/abacus_eos.py
```

## ABACUS的Si的EOS计算（pw）

进入工作目录，查看文件

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_pw_eos && ls
```

```text
INPUT		    abacus_Si_eos_5.60	abacus_pw_eos.png
STRU		    abacus_Si_eos_5.70	abacus_pw_eos.py
abacus_Si_eos_5.20  abacus_Si_eos_5.80	abacus_pw_time.csv
abacus_Si_eos_5.30  abacus_Si_eos_5.90	cp2k_gen_gth_pbe_si.upf
abacus_Si_eos_5.40  abacus_eos.csv
abacus_Si_eos_5.50  abacus_pw_eos.csv
```

运行abacus的pw的eos计算并回收结果

```shell
!cd /root/abacus_benchmark_demo/abacus/abacus_pw_eos && python /root/abacus_benchmark_demo/abacus/abacus_pw_eos/abacus_pw_eos.py
```

# 六、ABACUS和CP2K在Si体系EOS上的精度和效率对比总结

## EOS的Birch-Murnaghan方程拟合

很多实际的应用，如测定相变、膨胀系数、弹性、热电效应、组分变化、应力等，都要求精确地测定晶格常数。理论计算平衡晶格常数多采用固体的状态方程（equation of state, EOS），该方程表示晶体体系的总能量E随体系体积V的变化，即具有E(V)的形式。晶体的状态方程对于基础科学和应用科学具有重要的意义，比如平衡体积（V0）、体弹性模量（B<sub>0</sub>）以及它的一阶导数（B<sub>0</sub>'），这些可测的物理量与晶体的状态方程直接相关。在高压下状态方程可用好几种不同的函数形式来描述，比如Murnaghan方程、Birch-Murnaghan(BM)方程和普适方程等。<br>
**三阶Birch-Murnaghan方程如下：**


$${\displaystyle E(V)=E_{0}+{\frac {9V_{0}B_{0}}{16}}\left\{\left[\left({\frac {V_{0}}{V}}\right)^{2/3}-1\right]^{3}B_{0}^{\prime }+\left[\left({\frac {V_{0}}{V}}\right)^{2/3}-1\right]^{2}\left[6-4\left({\frac {V_{0}}{V}}\right)^{2/3}\right]\right\}}$$

由该方程可以看出，当V=V<sub>0</sub>时，E=E<sub>0</sub>，这就分别是平衡晶格常数及其对应的能量。在实际操作中，我们就可以在平衡晶格常数a<sub>0</sub>附近计算得到若干E-V数据点，经曲线拟合得到体系最低能量对应的晶格常数。采用最小二乘法拟合可以得到V<sub>0</sub>, E<sub>0</sub>, B<sub>0</sub>, B<sub>0</sub>'。

## EOS的比较指标

Delta指标用于比较通过两种不同的DFT计算方法\(a\)和\(b\)计算的EOS。这里，Delta = Delta(a, b)定义为：

$${\displaystyle \Delta(a, b) = \sqrt{\frac{1}{V_M - V_m} \int_{V_m}^{V_M} [E_a(V) - E_b(V)]^2 \, dV}}$$

其中，E<sub>a</sub>(V)和E<sub>b</sub>(V)\)分别是通过方法\(a\)和\(b\)得到的数据点的Birch-Murnaghan拟合，两条EOS曲线已经根据它们的最低能量进行了对齐，如前所述，积分范围覆盖了以中心体积V<sub>0</sub>为中心的6%的体积范围,使得最小体积为0.94 V<sub>0</sub>，最大体积为1.06 V<sub>0</sub>

## 精度和效率指标对比总结

进入工作目录,查看文件

```shell
!cd /root/abacus_benchmark_demo/summary && ls
```

```text
summary.csv  summary.py  summary_eos.png  summary_table.png
```

运行代码可实现此前计算EOS的拟合和对标elk的delta数值

```shell
!python /root/abacus_benchmark_demo/summary/summary.py
```

查看结果对比表格

| File Name        | Min Volume (Å³) | E0 (eV)      | Bulk Modulus (eV/Å³) | Bulk Deriv | Delta (vs ELK) | Average Time (s) |
|------------------|-----------------|--------------|----------------------|------------|----------------|------------------|
| elk_eos.csv      | 164.2483        | -63145.1661  | 0.5581               | 4.4889     |                | 24.0062          |
| cp2k_eos.csv     | 167.1733        | -855.9611    | 0.5210               | 4.3658     | 0.0078         | 19.6194          |
| abacus_eos.csv   | 163.3456        | -856.9076    | 0.5662               | 4.3237     | 0.0023         | 11.9913          |
| abacus_pw_eos.csv| 162.7852        | -857.4154    | 0.5484               | 4.3849     | 0.0039         | 35.7300          |


**总结**：在Si体系下，ABACUS通过使用和cp2k相同的赝势，以及由此赝势生成的轨道文件进行EOS计算。在其他参数尽可能对齐的情况下，ABACUS的平面波方法（pw）计算精度最高，但耗时最长；ABACUS的轨道方法（lcao）计算精度略低于平面波（pw）方法但优于CP2K，同时耗时约为cp2k的60%，在精度和效率上均优于cp2k。