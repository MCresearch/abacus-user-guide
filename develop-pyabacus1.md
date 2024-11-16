# Pyabacus 文档一：用户手册

<strong>作者：白晨旭</strong>

<strong>审核：陈默涵</strong>

<strong>单位：北京大学</strong>

<strong>最后更新时间：2024-11-15</strong>

# 一、简介

`pyabacus` 是密度泛函理论软件 ABACUS（原子算筹）的 Python 接口，提供了与 ABACUS 软件交互的 Python API。

该项目基于 `pybind11` 和 `scikit-build-core` 构建。

# 二、模块

`pyabacus` 当前提供以下模块：

- <strong>io</strong>：`pyabacus` 中的输入/输出模块。
- <strong>Cell</strong>：用于单元结构的模块，将 Python 中的 `ModuleNAO` 与用户输入连接。
- <strong>ModuleBase</strong>：基本数学函数模块。
- <strong>ModuleNAO</strong>：数值原子轨道 (NAO) 模块。
- <strong>hsolver</strong>：用于求解哈密顿量的模块。

# 三、安装

我们建议用户使用 conda 进行安装，conda 是一个开源的软件包管理系统和环境管理系统，可以方便的管理不同版本的 Python 和软件包。用户可以按照以下步骤安装 Pyabacus：

- 创建一个虚拟环境，并且激活虚拟环境 `conda create -n pyabacus python=3.8 & conda activate pyabacus`
- 下载 ABACUS 软件

```bash
cd {your_working_directory}
git clone https://github.com/abacusmodeling/abacus-develop.git
cd abacus-develop/python/pyabacus
```

- 安装 ABACUS 所需的[依赖库](https://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html#prerequisites)
- 使用 `pip install -v .` 安装 Pyabacus，或者使用 `pip install .[test]` 安装 Pyabacus 及其测试环境的依赖库(使用 `pip install -v .[test] -i https://pypi.tuna.tsinghua.edu.cn/simple` 加速安装过程)。

# 四、调用

用户可以通过以下代码调用 Pyabacus 的接口：

```python
import pyabacus
s = pyabacus.ModuleBase.Sphbes()
s.sphbesj(1, 0.0)
0.0
```

上面的代码调用了 ABACUS 的 `ModuleBase::Sphbes` 模块。

目前，我们移植了下面几个模块：

- `ModuleBase::Sphbes`
- `ModuleBase::Integral`
- `RadialCollection`
- `TwoCenterIntegrator`
- `hsolver::dav_subspace` 在 Python 中调用这些模块的方法可见 `examples` 文件夹内示例。

# 五、示例

`examples` 文件夹中包含了一些 Pyabacus 的示例脚本，用户可以通过这些示例脚本了解 Pyabacus 的使用方法。

运行 `examples` 文件夹中的 `python vis_nao.py` 以可视化数值原子轨道。

```bash
$ cd examples/
$ python vis_nao.py
```

运行 `examples` 文件夹中的 `python ex_s_rotate.py` 来检查 S 矩阵。

```bash
$ cd examples/
$ python ex_s_rotate.py
norm(S_e3 - S_numer) =  3.341208104032616e-15
```

运行 `examples` 文件夹中的 `python diago_matrix.py` 来对角化一个矩阵

```bash
$ cd examples/
$ python diago_matrix.py
eigenvalues calculated by pyabacus: [-0.38440611 0.24221155 0.31593272 0.53144616 0.85155108 1.06950155 1.11142051 1.12462152]
eigenvalues calculated by scipy: [-0.38440611 0.24221155 0.31593272 0.53144616 0.85155108 1.06950154 1.11142051 1.12462151]
error: [9.26164700e-12 2.42959514e-10 2.96529468e-11 7.77933273e-12 7.53686002e-12 2.95628810e-09 1.04678111e-09 7.79106313e-09]
```

# 六、测试

Pyabacus 使用 `pytest` 进行单元测试，用户可以在 `abacus-develop/python/pyabacus/tests` 目录下使用 `pytest -v` 命令进行单元测试。

# 七、结语

以上就是 Pyabacus 的一些基本安装和使用方法，如果读者对进一步交流感兴趣，欢迎登录 ABACUS 的 github 网站进行进一步的交流。
