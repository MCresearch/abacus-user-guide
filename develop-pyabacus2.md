# Pyabacus 文档二：HSolver 模块

<strong>作者：白晨旭</strong>

<strong>审核：陈默涵</strong>

<strong>单位：北京大学</strong>

<strong>最后更新时间：2024-11-15</strong>

# 一、简介

目前，`pyabacus.hsolver` 内实现了三种对角化算法的 `python` 化，分别是 `hsolver.dav_subspace`、`hsolver.davidson` 与 `hsolver.cg`，其签名分别如下：

```python
def dav_subspace(
    # 矩阵-向量组乘法函数，接收一个numpy数组，返回一个numpy数组
    mvv_op: Callable[[NDArray[np.complex128]], NDArray[np.complex128]],
    # 对角化过程中的特征向量组初猜
    init_v: NDArray[np.complex128],
    # 矩阵维度
    dim: int,
    # 要求的特征值个数，从最小的特征值开始，算法会求解num_eigs个特征值
    num_eigs: int,
    # 预处理向量
    precondition: NDArray[np.float64],
    # 基组允许容纳的向量个数(dav_ndim * nband个)
    dav_ndim: int = 2,
    # 迭代误差
    tol: float = 1e-2,
    # 最大迭代次数
    max_iter: int = 1000,
    # 是否使用子空间函数
    need_subspace: bool = False
) -> Tuple[NDArray[np.float64], NDArray[np.complex128]]:

# dav_subspace会返回一个元组，分别为特征值数组与其对应的特征向量集合

def dav_subspace(
    # 矩阵-向量组乘法函数，接收一个numpy数组，返回一个numpy数组
    mvv_op: Callable[[NDArray[np.complex128]], NDArray[np.complex128]],
    # 对角化过程中的特征向量组初猜
    init_v: NDArray[np.complex128],
    # 矩阵维度
    dim: int,
    # 要求的特征值个数，从最小的特征值开始，算法会求解num_eigs个特征值
    num_eigs: int,
    # 预处理向量
    precondition: NDArray[np.float64],
    # 基组允许容纳的向量个数(dav_ndim * nband个)
    dav_ndim: int = 2,
    # 迭代误差
    tol: float = 1e-2,
    # 最大迭代次数
    max_iter: int = 1000,
    # 是否使用PAW方法
    use_paw: bool = False
) -> Tuple[NDArray[np.float64], NDArray[np.complex128]]:

# davidson会返回一个元组，分别为特征值数组与其对应的特征向量集合

def cg(
    # 矩阵-向量组乘法函数，接收一个numpy数组，返回一个numpy数组
    mvv_op: Callable[[NDArray[np.complex128]], NDArray[np.complex128]],
    # 对角化过程中的特征向量组初猜
    init_v: NDArray[np.complex128],
    # 矩阵维度
    dim: int,
    # 要求的特征值个数，从最小的特征值开始，算法会求解num_eigs个特征值
    num_eigs: int,
    # 预处理向量
    precondition: NDArray[np.float64],
    # 迭代误差
    tol: float = 1e-2,
    # 最大迭代次数
    max_iter: int = 1000,
    # 是否使用子空间函数
    need_subspace: bool = False,
    # 计算模式：自洽场/非自洽场
    scf_type: bool = False,
    # 进程数
    nproc_in_pool: int = 1
) -> Tuple[NDArray[np.float64], NDArray[np.complex128]]:
    
# cg会返回一个元组，分别为特征值数组与其对应的特征向量集合
```

# 二、安装 `pyabacus`

我们建议用户使用 `conda` 进行安装，`conda` 是一个开源的软件包管理系统和环境管理系统，可以方便的管理不同版本的 `Python` 和软件包。用户可以按照以下步骤安装 `pyabacus`：

- 创建一个虚拟环境，并且激活虚拟环境 `conda create -n pyabacus python=3.8 & conda activate pyabacus`
- 下载 `ABACUS`

```bash
cd {your_working_directory}
git clone https://github.com/abacusmodeling/abacus-develop.git
cd abacus-develop/python/pyabacus
```

- 安装 `ABACUS` 所需的[依赖库](https://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html#prerequisites)
- 使用 `pip install -v .` 安装 `pyabacus`，或者使用 `pip install .[test]` 安装 Pyabacus 及其测试环境的依赖库(使用 `pip install -v .[test] -i https://pypi.tuna.tsinghua.edu.cn/simple` 加速安装过程)。

# 三、调用对角化算法

三种对角化方法签名几乎一致，只有微小的差别，调用方法也相同，下面统一用 `diago` 指代。

在调用这两个函数前，首先我们需要读取一个矩阵，我们可以从 [https://sparse.tamu.edu/PARSEC](https://sparse.tamu.edu/PARSEC) 上下载，之后使用 `scipy` 读取，并且确定要求的特征值个数（示例中为 8 个）：

```python
h_mat = scipy.io.loadmat(mat_file)['Problem']['A'][0, 0]
dim = h_mat.shape[0]
num_eigs = 8
```

我们也可以用 `numpy` 生成一个对角占优的 Hermitian 矩阵：

```python
n = 500
h_mat = np.random.rand(n,n)
h_mat =  h_mat +  h_mat.conj().T + np.diag(np.random.random(n))*10
```

之后，我们可以定义 `mvv_op` 算子：

```python
def mvv_op(x):
    return h_mat.dot(x)
# 如果你愿意的话，也可以定义为一个lambda函数
# mvv_op = lambda x: h_mat.dot(x)
```

选取初猜 `v0`：

```python
v0 = np.random.rand(nbasis, nband)
```

计算预处理子 `precond`，由于这里我们读取的矩阵为对角占优的稀疏矩阵，所以我们可以取出矩阵的对角元组成新的矩阵 `D`，并且计算 `D` 的逆作为矩阵的近似逆。

```python
diag_elem = h_mat.diagonal()
# 为了数值稳定，防止部分对角元过小（接近0）导致
# 其倒数为无穷大，我们将小于1e-8的点设置为1e-8
diag_elem = np.where(np.abs(diag_elem) < 1e-8, 1e-8, diag_elem)
precond = 1.0 / np.abs(diag_elem)
```

做完上述一系列准备工作后，我们即可调用 `pyabacus` 的算法来计算特征值问题了！

```python
# 下面的diago可按需替换为dav_subspace或davidson
e, v = diago(
    mm_op,
    v0,
    nbasis,
    nband,
    precond,
    dav_ndim=8, # cg法无该参数
    tol=1e-8,
    max_iter=1000
)

print(f'eigenvalues calculated by pyabacus is: \n', e)
```

# 四、结语

以上就是 Pyabacus 的一些基本安装和使用方法，如果读者对进一步交流感兴趣，欢迎登录 ABACUS 的 github 网站进行进一步的交流。
