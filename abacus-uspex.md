# ABACUS+USPEX 接口教程

<strong>作者：柳向阳，邮箱：xiangyangliu@mail.ustc.edu.cn；郭晓庆，邮箱：xiaoqing.guo@mail.nwpu.edu.cn</strong>

<strong>审核：牛海洋，邮箱：haiyang.niu@nwpu.edu.cn；陈默涵，邮箱：mohanchen@pku.edu.cn</strong>

<strong>最后更新时间：2023/09/14</strong>

# 一、背景介绍

近年来，随着高性能计算机的快速发展，晶体结构预测算法已然成为计算材料学的核心研究手段之一，极大地促进了新材料设计与研发的进程。Artem R.Oganov 教授课题组开发的进化类晶体结构预测算法 USPEX 是当前主流的全局搜索类算法之一。软件自 2004 年发布以来，该算法已被广泛应用于科研人员的研究工作中。晶体结构预测算法的主要作用是生成结构以及控制结构的演进，结构预测的效率及可靠性除却算法本身的影响外还对结构弛豫软件有极强的依赖性。ABACUS（原子算筹）作为一款国产开源密度泛函理论软件，同时兼具高精度和高效率，可适用于从小体系到上千原子体系的电子结构优化、原子结构弛豫、分子动力学等计算。因此实现晶体结构预测算法 USPEX（[https://uspex-team.org/en](https://uspex-team.org/en)）和第一性原理软件 ABACUS 的结合会给广大研究人员在结构预测研究中带来便利。

本教程旨在为大家提供一个 USPEX-ABACUS 接口的实现教程，方便大家程序配置。本教程以单质硅（Si）的结构预测为例, 介绍了该接口使用所需的输入文件和参数设置。

如需了解更多关于 USPEX 的使用信息，请参考 USPEX 官方文档：[USPEX Documentation ‒ USPEX](https://uspex-team.org/en/uspex/documentation)

# 二、接口介绍

- 当前发行的 USPEX 提供了分别以 matlab 和 python 为核心编程语言的两个版本，前者的版本编号为 USPEX-vXX（如 USPEX_v10.5），后者的版本编号为 USPEX-YEAR-XX（如 USPEX 2023.0.2），需要注意的是当前只有 python 版本可以自定义外部接口。该教程中的接口是在 USPEX 2023.0.2 和 ABACUS 3.3.0 版本进行编写测试的，如发生版本变更引起的异常，根据报错再行修改。
- 首先通过 USPEX 官网（[USPEX 下载 ‒ USPEX](https://uspex-team.org/zh/uspex/downloads)）下载 USPEX 2023.0.2 软件（注册后即可免费下载），解压后根据所使用的 python 版本，选择软件压缩包进行安装，例如 `pip install uspex-2023.0.2-cp310-cp310-linux_x86_64.whl`。

  注：若系统提示需要安装虚拟环境，可以在 USPEX 2023.0.2 目录下激活虚拟环境后重新进行安装。

```bash
python -m venv tutorial-env
source tutorial-env/bin/activate
```

- 该接口共包含三个文件

  (1) USPEX/components.py（对接口进行注册）

  (2) USPEX/Stages/Interfaces/ASEInterfacesAdapter.py（完成 ASE 接口中的读 read 和写 write 功能）

  (3) USPEX/Stages/Interfaces/ABACUS_Interface.py（接口实体，主要功能是准备 Abacus 的输入文件和读取    Abacus 的计算结果）

  注：以上路径中 USPEX 为主目录。

  上述文件可在 Github 仓库下载：[https://github.com/gxq1219/Interface_USPEX-ABACUS/tree/master](https://github.com/gxq1219/Interface_USPEX-ABACUS/tree/master)
- 安装完成后将以上文件复制到对应的路径下，并且需要手动添加环境变量，例如:`export PATH=python3.10/site-packages/USPEX:$PATH`，然后将 USPEX 2023.0.2 目录下的 `random_cell` 复制到设置的环境变量路径下。
- 该接口需要安装 ase-abacus 版本的 ase 库，测试版本为 ase-3.23.0b1

  安装 ase-abacus 接口

```bash
git clone https://gitlab.com/1041176461/ase-abacus.git
cd ase-abacus
python3 setup.py install
```

- 此次测试是在 QSUB 任务管理系统下进行测试，如果更换任务管理系统，应修改 USPEX 输入文件 `input.uspex` 中的 `taskManager` 和 `TM`，此外需修改 `USPEX/Stages/TaskManager` 中所选任务管理方式中对任务队列状态识别的方式，如在 `QSUB.py` 文件中应根据所使用平台修改 `def _parseJobID` 中的内容识别出提交任务的 ID，以及下文的 `def isReady` 和 `def isExist` 等函数。

`QSUB.py` 示例（第 56 行的函数，根据自己超算平台修改，功能是执行 qsub sub.sh 后从屏幕输出的文本中提取出 jobID）：

```python
"""
USPEX.Stages.TaskManagers.QSUB
==============================
"""
import logging
from os.path import join as pj
logger = logging.getLogger(__name__)
class QSUB:
    shortname = 'QSUB'
    _RUNSCRIPT = 'jobscript'
    def __init__(self, header : str, connector):
        """
        :param header: description of params of TaskManager
        :param connector: for remote submission
        """
        self.connector = connector
        self.header = header
    def _prepareSubmission(self, COMMAND_EXEC : str, JOB_NAME : str,
                                 inputFile : str, outputFile : str, errorFile : str) -> str:
        """
        Preparing jobscript for submission
        :param commandExec:
        :param jobName:
        :return: jobscript as string
        """
        content = ''
        for line in self.header.split('\n'):
            if ' -N ' in line:
                logger.info('Job name found in HEADER will be overwritten')
            elif ' -o ' in line:
                logger.info('Output file name found in HEADER will be overwritten')
            elif ' -e ' in line:
                logger.info('Error file name found in HEADER will be overwritten')
            else:
                content += line + '\n' 
        content += f'#PBS -N  {JOB_NAME}\n'
        content += f'#PBS -o  {outputFile}\n'
        content += f'#PBS -e  {errorFile}\n'
        content += f'cd $PBS_O_WORKDIR\n'
        content += f'\n{COMMAND_EXEC}\n'
        return ''.join(content)
    async def submit(self, command: str, jobname: str, input: str, output: str, error: str, calcFolder : str) -> int:
        content = self._prepareSubmission(command, jobname, input, output, error)
        with open(pj(calcFolder, self._RUNSCRIPT), 'wt') as f:
            f.write(content)
        await self.connector.sync_l2r(pj(calcFolder, self._RUNSCRIPT))
        returncode, out, err = await self.connector.execute(f'qsub {self._RUNSCRIPT}', cwd=calcFolder)
        logger.debug(f'process returned code {returncode}')
        if returncode != 0:
            logger.error(err)
            logger.error(out)
        jobID = self._parseJobID(out, err)
        logger.info(f"Job ID is {jobID}")
        return jobID

    def _parseJobID(self, output : str, error : str) -> int:
        """
        :param output:
        :param error:
        :return: jobID
        """
        if '.mgmt' in output:
            tmp = output.index('.mgmt')
            return int(output[:tmp])
        elif 'job' in output:
            tmp = output.index('job') + 4
            return int(output[tmp:])
        elif 'comput100' in output:
            tmp = output.index('comput100')-1
            return int(output[:tmp]) 
        else:
            return int(output)
    async def isReady(self, jobID):
        returncode, out, err = await self.connector.execute(f'qstat {jobID}')
        return not (' R ' in out or ' Q ' in out)
    async def isExist(self, jobID):
        returncode, out, err = await self.connector.execute(f'qstat {jobID}')
        return len(out) > 0
    async def kill(self, jobID):
        returncode, out, err = await self.connector.execute(f'qdel {jobID}')
        #logger.info(f'Process with jobID={jobID}  killed.')
```

# 三、流程（以 Si 为例）

## 1. 准备 USPEX 的输入文件 input.uspex

```json
{
    optimizer: {
        type: GlobalOptimizer
        target: {
            type: Atomistic
            conditions: {externalPressure: 0.00001}
            compositionSpace: {symbols: [Si]
                               blocks: [[4]]}
        }
        optType: enthalpy
        selection: {
            type: USPEXClassic
            popSize: 4
            initialPopSize: 4
            bestFrac: 0.6
            optType: (aging enthalpy)
            fractions: {
                heredity: (0.4 0.7 0.5)
                softmodemutation: (0.2 0.5 0.3)
                randSym: (0.05 0.5 0.1)
                randTop: (0.05 0.5 0.1)
            }
        }
    }
    stages: [abacus1 abacus2 abacus3 abacus4 abacus5]
    numParallelCalcs: 4 
    numGenerations: 25
    stopCrit: 10
}

#define abacus1
{type : abacus, commandExecutable : 'OMP_NUM_THREADS=1 mpirun -machinefile $PBS_NODEFILE -env I_MPI_HYDRA_DEBUG 3 -genv I_MPI_FABRICS shm:ofi abacus', kresol: 0.20, taskManager: TM}

#define abacus2
{type : abacus, commandExecutable : 'OMP_NUM_THREADS=1 mpirun -machinefile $PBS_NODEFILE -env I_MPI_HYDRA_DEBUG 3 -genv I_MPI_FABRICS shm:ofi abacus', kresol: 0.16, taskManager: TM}

#define abacus3
{type : abacus, commandExecutable : 'OMP_NUM_THREADS=1 mpirun -machinefile $PBS_NODEFILE -env I_MPI_HYDRA_DEBUG 3 -genv I_MPI_FABRICS shm:ofi abacus', kresol: 0.12, taskManager: TM}

#define abacus4
{type : abacus, commandExecutable : 'OMP_NUM_THREADS=1 mpirun -machinefile $PBS_NODEFILE -env I_MPI_HYDRA_DEBUG 3 -genv I_MPI_FABRICS shm:ofi abacus', kresol: 0.08, taskManager: TM}

#define abacus5
{type : abacus, commandExecutable : 'OMP_NUM_THREADS=1 mpirun -machinefile $PBS_NODEFILE -env I_MPI_HYDRA_DEBUG 3 -genv I_MPI_FABRICS shm:ofi abacus', kresol: 0.05, taskManager: TM}

#define TM
{
type : QSUB,
header:"#PBS -S /bin/bash
#PBS -N single
#PBS -l nodes=1:ppn=16
#PBS -j oe
#PBS -V"
} 
```

 注意：ABACUS在任务提交时，应注意指定OMP_NUM_THREADS，防止内存不足引起计算错误


## 2. 准备 Specific 文件夹

 所需文件：`INPUT_X`（使用ABACUS弛豫）、`ATOMIC_SPECIES`、`NUMERICAL_ORBITAL`以及轨道和赝势文件。

- `INPUT` 文件内容和个数由用户自行设置（需要与 input.uspex 中 stages 对应），具体可参考 uspex 官方文档。

  需要注意的是：`INPUT` 的 suffix 需指定为 USPEX；
- 需给出 `ATOMIC_SPECIES` 和 `NUMERICAL_ORBITAL` 两个文件指定所使用的 upf 文件和 orb 文件。

  ATOMIC_SPECIES 内容：元素符号 质量 赝势文件名

  NUMERICAL_ORBITAL 内容：元素符号 轨道文件名

## 3. 根据计算实际需求添加 Seeds 结构（可选，非必须）

## 4. 提交运算

```bash
nohup ./uspex-sub.sh >> log &

### content of uspex-sub.sh

#!/bin/sh
while true;do
    data >> log
    uspex -r >> log
    sleep 300   ### Users can adjust this value to manipulate the frequency of the call to uspex.
done
```

## 5. 计算结果

 如果程序可以正常提交任务，log文件中会打印如下内容：

```bash
2023-08-09 16:52:47,115 - USPEX.Optimizers.Target - INFO - Following utilities was not initialized: ['PowderSpectrumAnalyzer', 'SingleCrystalSpectrumAnalyzer'].
2023-08-09 16:52:47,115 - USPEX.Optimizers.Target - INFO - Permutation does not work when number of symbols in calculation is 1.
2023-08-09 16:52:47,123 - USPEX.Stages.GenerationController - INFO - Calculation initialized from input parameters.
2023-08-09 16:52:47,441 - USPEX.Selection.USPEXClassic - INFO - System 0 successfully created by RandSym operator.
2023-08-09 16:52:47,866 - USPEX.Selection.USPEXClassic - INFO - System 1 successfully created by RandSym operator.
2023-08-09 16:52:48,638 - USPEX.Selection.USPEXClassic - INFO - System 2 successfully created by RandSym operator.
2023-08-09 16:52:48,767 - USPEX.Selection.USPEXClassic - INFO - System 3 successfully created by RandSym operator.
2023-08-09 16:52:48,788 - USPEX.Stages.Executor - INFO - System 0 with tag 1 will be submitted now.
2023-08-09 16:52:48,788 - USPEX.Stages.TaskManagers.QSUB - INFO - Job name found in HEADER will be overwritten
2023-08-09 16:52:48,792 - USPEX.Stages.Executor - INFO - System 1 with tag 1 will be submitted now.
2023-08-09 16:52:48,792 - USPEX.Stages.TaskManagers.QSUB - INFO - Job name found in HEADER will be overwritten
2023-08-09 16:52:48,796 - USPEX.Stages.Executor - INFO - System 2 with tag 1 will be submitted now.
2023-08-09 16:52:48,797 - USPEX.Stages.TaskManagers.QSUB - INFO - Job name found in HEADER will be overwritten
2023-08-09 16:52:48,801 - USPEX.Stages.Executor - INFO - System 3 with tag 1 will be submitted now.
2023-08-09 16:52:48,801 - USPEX.Stages.TaskManagers.QSUB - INFO - Job name found in HEADER will be overwritten
2023-08-09 16:52:48,812 - USPEX.Stages.TaskManagers.QSUB - INFO - Job ID is 37768
2023-08-09 16:52:48,818 - USPEX.Stages.TaskManagers.QSUB - INFO - Job ID is 37769
2023-08-09 16:52:48,822 - USPEX.Stages.TaskManagers.QSUB - INFO - Job ID is 37770
2023-08-09 16:52:48,825 - USPEX.Stages.TaskManagers.QSUB - INFO - Job ID is 37771
```

如果程序可以正常输出结果，在 results1/Individuals 中会打印相关的信息，示例如下：

```bash
+----+------------------+-------------+---------------+--------------+---------------+-----------------+---------------+--------------+
| ID |      Origin      | Composition | Enthalpy (eV) | Volume (A^3) |  SYMMETRY (N) | Structure order | Average order | Quasientropy |
+----+------------------+-------------+---------------+--------------+---------------+-----------------+---------------+--------------+
| 0  |     RandSym      |    Si: 4    |    -425.452   |    59.320    | P6/mmm  (191) |       0.334     |      0.334    |    -0.000    |
| 2  |     RandSym      |    Si: 4    |    -418.078   |    59.320    | I4/mmm  (139) |       0.287     |      0.287    |    -0.000    |
| 3  |     RandSym      |    Si: 4    |    -425.038   |    59.320    | P4_332  (212) |       0.392     |      0.392    |    -0.000    |
| 4  | Softmodemutation |    Si: 4    |    -428.592   |    59.320    | I4/mmm  (139) |       0.325     |      0.325    |     0.000    |
| 5  | Softmodemutation |    Si: 4    |    -428.592   |    59.320    | I4/mmm  (139) |       0.325     |      0.325    |     0.000    |
| 6  |     Heredity     |    Si: 4    |    -427.892   |    59.320    |  P2_1/m  (11) |       0.202     |      0.215    |     0.077    |
| 8  | Softmodemutation |    Si: 4    |    -427.882   |    59.320    |  P2_1/m  (11) |       0.201     |      0.215    |     0.076    |
| 9  | Softmodemutation |    Si: 4    |    -427.887   |    59.320    |  P2_1/m  (11) |       0.202     |      0.215    |     0.075    |
| 10 |     Heredity     |    Si: 4    |    -428.645   |    59.320    |  Cmce    (64) |       0.261     |      0.261    |     0.000    |
| 11 | Softmodemutation |    Si: 4    |    -428.644   |    59.320    |  Cmce    (64) |       0.261     |      0.261    |     0.000    |
| 12 | Softmodemutation |    Si: 4    |    -428.645   |    59.320    |  Cmce    (64) |       0.261     |      0.261    |     0.001    |
| 14 |     Heredity     |    Si: 4    |    -428.628   |    59.320    |  Cmce    (64) |       0.263     |      0.263    |     0.000    |
| 15 |     Heredity     |    Si: 4    |    -428.928   |    59.320    |  Cmcm    (63) |       0.291     |      0.291    |     0.000    |
| 16 |     Heredity     |    Si: 4    |    -428.949   |    59.320    |  P2_1/m  (11) |       0.283     |      0.284    |     0.006    |
| 17 |     RandSym      |    Si: 4    |    -422.987   |    59.320    |  C2/m    (12) |       0.250     |      0.250    |     0.000    |
| 19 | Softmodemutation |    Si: 4    |    -428.927   |    59.320    |  Cmcm    (63) |       0.291     |      0.291    |     0.000    |
| 20 | Softmodemutation |    Si: 4    |    -428.928   |    59.320    |  Cmcm    (63) |       0.290     |      0.290    |     0.000    |
| 21 |     Heredity     |    Si: 4    |    -428.926   |    59.320    |  Cmcm    (63) |       0.290     |      0.290    |     0.000    |
```

# 四、结语

建议大家在使用前，首先选择小体系进行测试；此外大家也可根据自己的实际需要对接口文件进行修改扩充，有相关问题可通过邮件方式沟通。
