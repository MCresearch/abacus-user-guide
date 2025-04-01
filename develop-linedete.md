# ABACUS 全局数据结构和代码行数检测

**作者：韩昊知，邮箱：haozhi.han@stu.pku.edu.cn**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2025/04/01**

# 一、背景

我们将从 ABACUS 的两个主要方面来介绍目前重构还需要进行的工作：一是全局变量和全局类。二是文件的大小和长度。这个文档的主要目的也是要呼吁更多的开发者能够有意识的，主动的对代码目前的一些问题进行重构，这有利于提升代码整体的质量。我们也欢迎更多的开源社区伙伴能够加入进来，提升 ABACUS 代码的质量。

第二部分，我们提供了一个测试 ABACUS 代码关于全局数据结构和代码行数的脚本。

第三部分，我们针对 ABACUS 3.4.2 版本和 3.10.0 版本进行了检测，检测结果和检测时间已列在文档中，可以看到在 3.4.2 版本里 GlobalV 出现了 `7972` 次，GlobalC 出现了 `3504` 次。而在 3.10.0 版本里， GlobalV 出现了 `2673` 次，而 GlobalC 出现了 `556` 次，在过去几个大版本的持续迭代中，GlobalV 和 GlobalC 的出现频率已经大幅度降低。

希望这个数据能够帮助到想要对代码进行相关重构的同学。我们会隔一段时间后再对本文档进行更新。

## 全局变量和全局类

ABACUS 代码里长期存在一些全局变量（程序里以 GlobalV：：开头的变量，V 代表 variables）和全局类（程序里以 GlobalC：：开头的类，C 代表 classes）。这里全局的含义说明这些变量和类可以在程序的任何一个角落调用，不需要通过函数的接口传递。

在程序发展早期，使用全局变量和全局类可以加速程序新功能的开发，使得开发者可以快速的调用到想要的模块，例如 ucell 代表原胞信息的类，那么只要需要使用到诸如原子位置和种类等信息，都可以直接调用，就显得很方便。

然而，随着 ABACUS 代码数量的增加，对一些全局变量和全局类**不加控制的使用**导致了严重的问题，即当某一个全局变量或者全局类被修改之后，会影响大量的代码，从而可能引发不同功能的 bug，另外也会给对全局变量或者全局类修改的开发者带来很多额外的工作量。

大多数的开发者会延用 ABACUS 目前的全局类和全局变量的使用，但我们认为这可能会慢慢的导致 ABACUS 的代码结构越来越变得不可维护，因此有必要做出一些代码结构上的调整甚至重构。

目前 ABACUS 开发团队觉得需要做两件事情来提升代码质量，一方面需要对全局变量和全局类的使用加以控制，不在特殊情况下一般不建议使用。另外一方面，对一些可以不成为全局变量或者全局类的代码加以修改和重构，逐步减少全局变量和全局类的使用次数，通过一些更规范的函数参数传递来进行替代。但是，这项工作涉及到的工作量较大，因此需要逐步的推进完成，甚至依赖开源的力量来推动它完成，从而根本上提升 ABACUS 的代码质量。

## 代码长度

在 ABACUS 开发的过程中，有些开发者倾向于将同一类功能的代码都放入到同一个代码文件，但后期我们发现如果对这个过程不加以一定条件的约束，会使得代码质量下降。首先，随着程序的不断发展，一个长的代码里可能会有一些代码可以被别的地方重用，但是这部分代码不容易被抽出来。其次，当要对一个长代码里的一些函数进行局部修改时，也会容易使得开发者难以聚焦到一个特定功能代码上。反之，如果把代码尽可能按照“一定的规则”分散开来，例如每个代码文件长度不超过 500 行，那会使得维护和更新变得更容易，因此我们倡导开发者持续的针对代码长度进行重构，目前软件里有不少超过 >500 行的程序。

# 二、测试脚本

此脚本功能：

_# --------------1. 计算总代码行数--------------_

_# --------------2. 统计每个文件夹内 GlobalV 和 GlobalC 出现的次数--------------_

_# --------------3. 输出行数大于 500 行的文件路径及其行数--------------_

```python
import os

def count_lines_of_code(file_path):
    """
    计算文件的代码行数

    :param file_path: 文件路径
    :return: 代码行数
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        lines = file.readlines()
    return len(lines)

def count_lines_in_folder(folder_path):
    """
    计算文件夹中所有文件的代码行数

    :param folder_path: 文件夹路径
    :return: 总代码行数
    """
    total_lines = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 构建文件的完整路径
            file_path = os.path.join(root, file)

            # 跳过非文本文件
            if not file_path.endswith((".cpp", ".c", ".h")):
                continue

            # 计算文件的代码行数并累加到总行数中
            lines = count_lines_of_code(file_path)
            total_lines += lines

    return total_lines

# ----------------------------------------------
def count_globals_in_file(file_path):
    """
    统计一个文件中出现了多少次 GlobalV 和 GlobalC
    
    :param file_path: 文件路径
    :return: {'globalv_count': GlobalV 出现的次数, 'globalc_count': GlobalC 出现的次数}
    """
    globalv_count = 0
    globalc_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            globalv_count = content.count('GlobalV')
            globalc_count = content.count('GlobalC')
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return {'globalv_count': globalv_count, 'globalc_count': globalc_count}

def count_globals_in_folder(folder_path):
    """
    统计一个文件夹中出现了多少次 GlobalV 和 GlobalC
    
    :param folder_path: 文件夹路径
    :return: {'globalv_count': GlobalV 出现的总次数, 'globalc_count': GlobalC 出现的总次数}
    """
    globalv_count = 0
    globalc_count = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 构建文件的完整路径
            file_path = os.path.join(root, file)

            # 跳过非文本文件
            if not file_path.endswith(('.cpp', '.c', '.h')):
                continue

            # 调用 count_globals_in_file 函数，统计文件中 GlobalV 和 GlobalC 的出现次数
            file_counts = count_globals_in_file(file_path)
            globalv_count += file_counts['globalv_count']
            globalc_count += file_counts['globalc_count']
    
    return {'globalv_count': globalv_count, 'globalc_count': globalc_count}

def count_globals_in_subfolders(main_folder_path):
    """
    统计一个文件夹内所有子文件夹的 GlobalV 和 GlobalC 出现次数
    
    :param main_folder_path: 主文件夹路径
    :return: 字典，包含每个子文件夹的 GlobalV 和 GlobalC 出现次数
    """
    subfolder_counts = {}

    for root, dirs, files in os.walk(main_folder_path):
        for folder in dirs:
            folder_path = os.path.join(root, folder)

            # 调用 count_globals_in_folder 函数，统计子文件夹中 GlobalV 和 GlobalC 的出现次数
            folder_counts = count_globals_in_folder(folder_path)
            subfolder_counts[folder] = folder_counts
    
    return subfolder_counts

def print_folder_tree_with_counts(folder_path, indent=""):
    """
    输出文件夹树结构，同时统计每个文件夹内出现了多少次 GlobalV 和 GlobalC
    
    :param folder_path: 文件夹路径
    :param indent: 缩进字符串，用于表示层级关系
    """
    folder_info = count_globals_in_folder(folder_path)
    
    # 输出当前文件夹的名称
    print(indent + "|-- " + os.path.basename(folder_path))

    # 输出当前文件夹内的 GlobalV 和 GlobalC 出现次数
    print(indent + f"    GlobalV 出现了 {folder_info['globalv_count']} 次")
    print(indent + f"    GlobalC 出现了 {folder_info['globalc_count']} 次")
    
    # 获取文件夹中的所有项目（文件和子文件夹）
    items = os.listdir(folder_path)
    
    for item in items:
        # 构建项目的完整路径
        item_path = os.path.join(folder_path, item)
        
        # 检查项目是否是文件夹
        if os.path.isdir(item_path):
            # 递归调用，打印子文件夹的树结构
            print_folder_tree_with_counts(item_path, indent + "    ")

# 指定文件夹路径
folder_path = "./abacus-develop/source"

# --------------1. 计算代码行数--------------
# 调用函数，获取文件夹中所有文件的代码行数
total_lines = count_lines_in_folder(folder_path)
print(f"整个文件夹中所有文件总共有 {total_lines} 行代码。")

# --------------2. 统计 GlobalV 和 GlobalC 出现的次数--------------
# 调用函数，输出文件夹树和统计 GlobalV 和 GlobalC 的出现次数
print_folder_tree_with_counts(folder_path)

# --------------3. 出文件夹内行数大于 500 行的文件及其行数--------------
def count_lines(file_path):
    """
    统计一个文件的行数
    
    :param file_path: 文件路径
    :return: 文件的行数
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            return len(lines)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

def count_lines_in_folder(folder_path):
    """
    统计一个文件夹内行数大于 500 行的文件
    
    :param folder_path: 文件夹路径
    :return: 文件路径及其行数的字典
    """
    files_over_500_lines = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 构建文件的完整路径
            file_path = os.path.join(root, file)

            # 跳过非文本文件
            if not file_path.endswith(('.txt', '.py', '.java', '.cpp', '.c', '.html', '.css', '.js')):
                continue

            # 调用 count_lines 函数，统计文件的行数
            lines_count = count_lines(file_path)

            # 检查行数是否大于 500
            if lines_count > 500:
                files_over_500_lines[file_path] = lines_count
    
    return files_over_500_lines

# 输入文件夹路径
folder_path = "./abacus-develop/source"

# 调用函数，获取文件夹内行数大于 500 行的文件
files_over_500_lines = count_lines_in_folder(folder_path)

# 出文件夹内行数大于 500 行的文件及其行数
if files_over_500_lines:
    print("行数大于 500 行的文件:")
    for file_path, lines_count in files_over_500_lines.items():
        print(f"{file_path}: {lines_count} 行")
else:
    print("文件夹内没有行数大于 500 行的文件。")

import subprocess

def get_git_info(folder_path):
    try:
        # 获取最新提交的版本号
        commit_version = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=folder_path, text=True).strip()

        # 获取最新提交的时间
        commit_time = subprocess.check_output(['git', 'show', '-s', '--format=%ci', 'HEAD'], cwd=folder_path, text=True).strip()

        # 获取最近一次标签的名称
        latest_tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], cwd=folder_path, text=True).strip()

        return commit_version, commit_time, latest_tag
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None, None, None

from datetime import datetime
import pytz

# 设置时区为东八区（北京时间）
beijing_timezone = pytz.timezone('Asia/Shanghai')

# 获取当前时间，并设置时区为北京时间
current_datetime_utc = datetime.utcnow()
current_datetime_beijing = current_datetime_utc.replace(tzinfo=pytz.utc).astimezone(beijing_timezone)

# 格式化输出
formatted_datetime_beijing = current_datetime_beijing.strftime("%Y-%m-%d %H:%M:%S")

print("东八区时间（北京时间）:", formatted_datetime_beijing)

# 指定要检查的文件夹路径
folder_path = './abacus-develop'

# 获取Git信息
commit_version, commit_time, latest_tag = get_git_info(folder_path)

if commit_version:
    print(f"The latest commit version in the repository is: {commit_version}")
    print(f"The commit time is: {commit_time}")
    print(f"The latest tag is: {latest_tag}")
else:
    print("Failed to retrieve Git information.")
```

# 三、检测结果

## v3.4.2 检测结果

```shell
整个文件夹中所有文件总共有 324219 行代码。
|-- source
    GlobalV 出现了 7972 次
    GlobalC 出现了 3504 次
    |-- module_relax
        GlobalV 出现了 289 次
        GlobalC 出现了 207 次
        |-- relax_old
            GlobalV 出现了 244 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 130 次
                GlobalC 出现了 0 次
        |-- relax_new
            GlobalV 出现了 19 次
            GlobalC 出现了 200 次
            |-- test
                GlobalV 出现了 3 次
                GlobalC 出现了 117 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
    |-- module_io
        GlobalV 出现了 2022 次
        GlobalC 出现了 501 次
        |-- test
            GlobalV 出现了 262 次
            GlobalC 出现了 28 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test_serial
            GlobalV 出现了 20 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_basis
        GlobalV 出现了 101 次
        GlobalC 出现了 7 次
        |-- module_pw
            GlobalV 出现了 3 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 3 次
                GlobalC 出现了 0 次
            |-- test_serial
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- kernels
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- test
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- rocm
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- cuda
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- module_ao
            GlobalV 出现了 72 次
            GlobalC 出现了 7 次
            |-- test
                GlobalV 出现了 23 次
                GlobalC 出现了 0 次
                |-- GaAs
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- orb_obj
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- lcao_H2O
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- 1_Documents
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- doxygen
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- sphinx
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                    |-- source
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
        |-- module_nao
            GlobalV 出现了 26 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 17 次
                GlobalC 出现了 0 次
    |-- module_hamilt_pw
        GlobalV 出现了 704 次
        GlobalC 出现了 620 次
        |-- hamilt_pwdft
            GlobalV 出现了 492 次
            GlobalC 出现了 527 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- kernels
                GlobalV 出现了 6 次
                GlobalC 出现了 36 次
                |-- test
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- rocm
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- cuda
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- operator_pw
                GlobalV 出现了 1 次
                GlobalC 出现了 1 次
        |-- hamilt_stodft
            GlobalV 出现了 124 次
            GlobalC 出现了 93 次
        |-- hamilt_ofdft
            GlobalV 出现了 88 次
            GlobalC 出现了 0 次
    |-- module_md
        GlobalV 出现了 57 次
        GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 50 次
            GlobalC 出现了 0 次
    |-- module_psi
        GlobalV 出现了 150 次
        GlobalC 出现了 24 次
        |-- test
            GlobalV 出现了 48 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- kernels
            GlobalV 出现了 1 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- rocm
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- cuda
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_ri
        GlobalV 出现了 167 次
        GlobalC 出现了 121 次
        |-- test
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
        |-- test_code
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
    |-- module_elecstate
        GlobalV 出现了 896 次
        GlobalC 出现了 88 次
        |-- module_dm
            GlobalV 出现了 2 次
            GlobalC 出现了 1 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 1 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 337 次
            GlobalC 出现了 11 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test_mpi
            GlobalV 出现了 20 次
            GlobalC 出现了 0 次
        |-- kernels
            GlobalV 出现了 2 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- rocm
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- cuda
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- potentials
            GlobalV 出现了 73 次
            GlobalC 出现了 11 次
        |-- module_charge
            GlobalV 出现了 234 次
            GlobalC 出现了 32 次
    |-- module_cell
        GlobalV 出现了 885 次
        GlobalC 出现了 129 次
        |-- test
            GlobalV 出现了 290 次
            GlobalC 出现了 100 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test_pw
            GlobalV 出现了 8 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_neighbor
            GlobalV 出现了 75 次
            GlobalC 出现了 2 次
            |-- test
                GlobalV 出现了 26 次
                GlobalC 出现了 0 次
        |-- module_paw
            GlobalV 出现了 54 次
            GlobalC 出现了 2 次
            |-- test
                GlobalV 出现了 3 次
                GlobalC 出现了 0 次
        |-- module_symmetry
            GlobalV 出现了 100 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_base
        GlobalV 出现了 488 次
        GlobalC 出现了 1 次
        |-- test
            GlobalV 出现了 74 次
            GlobalC 出现了 0 次
            |-- data
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test_parallel
            GlobalV 出现了 153 次
            GlobalC 出现了 0 次
        |-- module_container
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- ATen
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- ops
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                    |-- test
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                |-- kernels
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                    |-- test
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                    |-- rocm
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                    |-- cuda
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                |-- core
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- base
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- third_party
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                    |-- backward-cpp
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                |-- macros
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- utils
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- core
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- libm
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- kernels
            GlobalV 出现了 0 次
            GlobalC 出现了 1 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- rocm
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- cuda
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_mixing
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_esolver
        GlobalV 出现了 775 次
        GlobalC 出现了 326 次
        |-- test
            GlobalV 出现了 4 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_hamilt_lcao
        GlobalV 出现了 1088 次
        GlobalC 出现了 1257 次
        |-- module_tddft
            GlobalV 出现了 92 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_deepks
            GlobalV 出现了 186 次
            GlobalC 出现了 2 次
            |-- test
                GlobalV 出现了 67 次
                GlobalC 出现了 0 次
            |-- doxygen
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- sphinx
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- source
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- hamilt_lcaodft
            GlobalV 出现了 478 次
            GlobalC 出现了 897 次
            |-- operator_lcao
                GlobalV 出现了 8 次
                GlobalC 出现了 48 次
                |-- test
                    GlobalV 出现了 1 次
                    GlobalC 出现了 0 次
        |-- module_gint
            GlobalV 出现了 178 次
            GlobalC 出现了 213 次
        |-- module_hcontainer
            GlobalV 出现了 6 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 6 次
                GlobalC 出现了 0 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- module_dftu
            GlobalV 出现了 142 次
            GlobalC 出现了 145 次
        |-- module_deltaspin
            GlobalV 出现了 6 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 4 次
                GlobalC 出现了 0 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
    |-- module_hsolver
        GlobalV 出现了 154 次
        GlobalC 出现了 23 次
        |-- test
            GlobalV 出现了 35 次
            GlobalC 出现了 0 次
        |-- kernels
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- rocm
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- cuda
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- genelpa
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
    |-- module_hamilt_general
        GlobalV 出现了 167 次
        GlobalC 出现了 196 次
        |-- test
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
        |-- module_ewald
            GlobalV 出现了 19 次
            GlobalC 出现了 6 次
        |-- module_vdw
            GlobalV 出现了 2 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 2 次
                GlobalC 出现了 0 次
        |-- module_xc
            GlobalV 出现了 80 次
            GlobalC 出现了 19 次
            |-- test
                GlobalV 出现了 20 次
                GlobalC 出现了 5 次
        |-- module_surchem
            GlobalV 出现了 66 次
            GlobalC 出现了 171 次
            |-- test
                GlobalV 出现了 53 次
                GlobalC 出现了 137 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
行数大于 500 行的文件:
./abacus-develop/source/module_relax/relax_old/ions_move_cg.cpp: 501 行
./abacus-develop/source/module_relax/relax_old/test/ions_move_cg_test.cpp: 556 行
./abacus-develop/source/module_relax/relax_old/test/lattice_change_basic_test.cpp: 526 行
./abacus-develop/source/module_relax/relax_old/test/lattice_change_cg_test.cpp: 534 行
./abacus-develop/source/module_relax/relax_new/relax.cpp: 616 行
./abacus-develop/source/module_io/to_wannier90.cpp: 2091 行
./abacus-develop/source/module_io/parameter_pool.cpp: 1633 行
./abacus-develop/source/module_io/write_HS_sparse.cpp: 961 行
./abacus-develop/source/module_io/numerical_basis.cpp: 792 行
./abacus-develop/source/module_io/unk_overlap_lcao.cpp: 853 行
./abacus-develop/source/module_io/cal_r_overlap_R.cpp: 645 行
./abacus-develop/source/module_io/input.cpp: 4041 行
./abacus-develop/source/module_io/berryphase.cpp: 717 行
./abacus-develop/source/module_io/write_dos_lcao.cpp: 669 行
./abacus-develop/source/module_io/input_conv.cpp: 748 行
./abacus-develop/source/module_io/winput.cpp: 721 行
./abacus-develop/source/module_io/write_HS.cpp: 1363 行
./abacus-develop/source/module_io/test/input_conv_test.cpp: 540 行
./abacus-develop/source/module_io/test/bessel_basis_test.cpp: 561 行
./abacus-develop/source/module_io/test/write_input_test.cpp: 916 行
./abacus-develop/source/module_io/test/input_test.cpp: 1691 行
./abacus-develop/source/module_basis/module_pw/fft.cpp: 789 行
./abacus-develop/source/module_basis/module_ao/ORB_atomic_lm.cpp: 772 行
./abacus-develop/source/module_basis/module_ao/ORB_table_alpha.cpp: 550 行
./abacus-develop/source/module_basis/module_ao/ORB_gen_tables.cpp: 1015 行
./abacus-develop/source/module_basis/module_ao/ORB_table_phi.cpp: 880 行
./abacus-develop/source/module_basis/module_ao/ORB_read.cpp: 589 行
./abacus-develop/source/module_basis/module_ao/test/ORB_nonlocal_lm_test.cpp: 755 行
./abacus-develop/source/module_basis/module_ao/test/ORB_atomic_lm_test.cpp: 886 行
./abacus-develop/source/module_basis/module_nao/beta_radials.cpp: 761 行
./abacus-develop/source/module_basis/module_nao/test/gaunt.txt: 7242 行
./abacus-develop/source/module_basis/module_nao/test/numerical_radial_test.cpp: 549 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/VNL_in_pw.cpp: 1841 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/stress_func_nl.cpp: 717 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/wf_atomic.cpp: 755 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/forces.cpp: 1100 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/wavefunc.cpp: 739 行
./abacus-develop/source/module_hamilt_pw/hamilt_stodft/sto_iter.cpp: 638 行
./abacus-develop/source/module_md/nhchain.cpp: 873 行
./abacus-develop/source/module_psi/psi_initializer_nao.cpp: 522 行
./abacus-develop/source/module_psi/test/psi_initializer_unit_test.cpp: 635 行
./abacus-develop/source/module_psi/kernels/device.cpp: 654 行
./abacus-develop/source/module_ri/exx_lip.cpp: 950 行
./abacus-develop/source/module_elecstate/elecstate_pw.cpp: 527 行
./abacus-develop/source/module_elecstate/occupy.cpp: 1007 行
./abacus-develop/source/module_elecstate/module_dm/density_matrix.cpp: 823 行
./abacus-develop/source/module_elecstate/test/potential_new_test.cpp: 646 行
./abacus-develop/source/module_elecstate/test/elecstate_base_test.cpp: 699 行
./abacus-develop/source/module_elecstate/test/support/WAVEFUNC1.txt: 4231 行
./abacus-develop/source/module_elecstate/module_charge/charge.cpp: 748 行
./abacus-develop/source/module_elecstate/module_charge/charge_mixing.cpp: 729 行
./abacus-develop/source/module_cell/read_pp_upf201.cpp: 908 行
./abacus-develop/source/module_cell/read_atoms.cpp: 1290 行
./abacus-develop/source/module_cell/unitcell.cpp: 1764 行
./abacus-develop/source/module_cell/klist.cpp: 1429 行
./abacus-develop/source/module_cell/test/unitcell_test.cpp: 1573 行
./abacus-develop/source/module_cell/test/klist_test.cpp: 778 行
./abacus-develop/source/module_cell/test/read_pp_test.cpp: 705 行
./abacus-develop/source/module_cell/module_neighbor/sltk_atom_input.cpp: 672 行
./abacus-develop/source/module_cell/module_neighbor/sltk_grid.cpp: 1109 行
./abacus-develop/source/module_cell/module_paw/paw_cell.cpp: 668 行
./abacus-develop/source/module_cell/module_paw/paw_cell_libpaw.cpp: 719 行
./abacus-develop/source/module_cell/module_symmetry/symmetry.cpp: 2118 行
./abacus-develop/source/module_cell/module_symmetry/symmetry_basic.cpp: 1166 行
./abacus-develop/source/module_base/math_sphbes.cpp: 810 行
./abacus-develop/source/module_base/spherical_bessel_transformer.cpp: 546 行
./abacus-develop/source/module_base/math_ylmreal.cpp: 706 行
./abacus-develop/source/module_base/mcd.c: 884 行
./abacus-develop/source/module_base/ylm.cpp: 1884 行
./abacus-develop/source/module_base/opt_DCsrch.cpp: 644 行
./abacus-develop/source/module_base/test/math_chebyshev_test.cpp: 536 行
./abacus-develop/source/module_base/test/complexmatrix_test.cpp: 588 行
./abacus-develop/source/module_base/test/global_function_test.cpp: 794 行
./abacus-develop/source/module_base/test/complexarray_test.cpp: 511 行
./abacus-develop/source/module_base/test/cubic_spline_test.cpp: 1468 行
./abacus-develop/source/module_base/test/vector3_test.cpp: 749 行
./abacus-develop/source/module_base/test/math_ylmreal_test.cpp: 513 行
./abacus-develop/source/module_base/test_parallel/parallel_reduce_test.cpp: 558 行
./abacus-develop/source/module_base/module_container/test/tensor_test.cpp: 536 行
./abacus-develop/source/module_base/module_container/ATen/ops/einsum_op.cpp: 1048 行
./abacus-develop/source/module_base/libm/sincos.cpp: 1262 行
./abacus-develop/source/module_esolver/esolver_ks.cpp: 576 行
./abacus-develop/source/module_esolver/esolver_ks_pw.cpp: 1129 行
./abacus-develop/source/module_esolver/esolver_ks_lcao_tddft.cpp: 621 行
./abacus-develop/source/module_esolver/esolver_ks_lcao_elec.cpp: 627 行
./abacus-develop/source/module_esolver/esolver_ks_lcao.cpp: 970 行
./abacus-develop/source/module_esolver/esolver_sdft_pw_tool.cpp: 1332 行
./abacus-develop/source/module_esolver/esolver_of.cpp: 1380 行
./abacus-develop/source/module_hamilt_lcao/module_tddft/propagator.cpp: 616 行
./abacus-develop/source/module_hamilt_lcao/module_deepks/LCAO_deepks_pdm.cpp: 824 行
./abacus-develop/source/module_hamilt_lcao/module_deepks/LCAO_deepks_torch.cpp: 769 行
./abacus-develop/source/module_hamilt_lcao/module_deepks/test/klist_1.cpp: 604 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/FORCE_k.cpp: 1248 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/wavefunc_in_pw.cpp: 695 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/LCAO_matrix.cpp: 1003 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/LCAO_gen_fixedH.cpp: 1096 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/LCAO_nnr.cpp: 539 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/FORCE_STRESS.cpp: 889 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/LCAO_hamilt.cpp: 930 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/operator_lcao/deepks_lcao.cpp: 507 行
./abacus-develop/source/module_hamilt_lcao/module_gint/gint.cpp: 585 行
./abacus-develop/source/module_hamilt_lcao/module_gint/gint_k_pvpr.cpp: 702 行
./abacus-develop/source/module_hamilt_lcao/module_gint/gint_k_sparse1.cpp: 529 行
./abacus-develop/source/module_hamilt_lcao/module_gint/gint_tools.cpp: 1376 行
./abacus-develop/source/module_hamilt_lcao/module_gint/grid_technique.cpp: 529 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/hcontainer.cpp: 728 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/transfer.cpp: 671 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/func_transfer.cpp: 663 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/atom_pair.cpp: 737 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/test/test_hcontainer_complex.cpp: 577 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/test/test_hcontainer.cpp: 674 行
./abacus-develop/source/module_hamilt_lcao/module_deltaspin/spin_constrain.cpp: 547 行
./abacus-develop/source/module_hsolver/diago_david.cpp: 1080 行
./abacus-develop/source/module_hsolver/diago_cg.cpp: 641 行
./abacus-develop/source/module_hsolver/kernels/test/math_kernel_test.cpp: 736 行
./abacus-develop/source/module_hamilt_general/module_vdw/vdwd3.cpp: 1435 行
./abacus-develop/source/module_hamilt_general/module_vdw/vdwd3_parameters_tab.cpp: 33131 行
./abacus-develop/source/module_hamilt_general/module_vdw/test/vdw_test.cpp: 610 行
./abacus-develop/source/module_hamilt_general/module_xc/xc_functional_gradcorr.cpp: 725 行
./abacus-develop/source/module_hamilt_general/module_xc/xc_functional_vxc.cpp: 776 行
./abacus-develop/source/module_hamilt_general/module_xc/test/test_xc2.cpp: 519 行
./abacus-develop/source/module_hamilt_general/module_xc/test/test_xc.cpp: 922 行
东八区时间（北京时间）: 2023-11-20 11:28:29
The latest commit version in the repository is: baccbe3356f81c9b349582e4b02fd723d77a50d9
The commit time is: 2023-11-17 22:22:05 +0800
The latest tag is: v3.4.2
```

## v3.10.0 检测结果

```
整个文件夹中所有文件总共有 389895 行代码。
|-- source
    GlobalV 出现了 2673 次
    GlobalC 出现了 556 次
    |-- module_md
        GlobalV 出现了 28 次
        GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 24 次
            GlobalC 出现了 0 次
    |-- module_parameter
        GlobalV 出现了 2 次
        GlobalC 出现了 0 次
    |-- module_esolver
        GlobalV 出现了 197 次
        GlobalC 出现了 83 次
        |-- test
            GlobalV 出现了 2 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_relax
        GlobalV 出现了 173 次
        GlobalC 出现了 1 次
        |-- relax_old
            GlobalV 出现了 157 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 80 次
                GlobalC 出现了 0 次
        |-- relax_new
            GlobalV 出现了 10 次
            GlobalC 出现了 1 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 1 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
    |-- module_ri
        GlobalV 出现了 8 次
        GlobalC 出现了 22 次
        |-- test_code
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_exx_symmetry
            GlobalV 出现了 6 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_hamilt_pw
        GlobalV 出现了 194 次
        GlobalC 出现了 35 次
        |-- hamilt_stodft
            GlobalV 出现了 47 次
            GlobalC 出现了 0 次
            |-- kernels
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- cuda
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- rocm
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- hamilt_pwdft
            GlobalV 出现了 142 次
            GlobalC 出现了 35 次
            |-- operator_pw
                GlobalV 出现了 0 次
                GlobalC 出现了 1 次
            |-- kernels
                GlobalV 出现了 0 次
                GlobalC 出现了 17 次
                |-- cuda
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- rocm
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- test
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- hamilt_ofdft
            GlobalV 出现了 5 次
            GlobalC 出现了 0 次
    |-- module_elecstate
        GlobalV 出现了 267 次
        GlobalC 出现了 28 次
        |-- module_dm
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- module_charge
            GlobalV 出现了 76 次
            GlobalC 出现了 7 次
        |-- kernels
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- cuda
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- rocm
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- potentials
            GlobalV 出现了 24 次
            GlobalC 出现了 7 次
        |-- test_mpi
            GlobalV 出现了 46 次
            GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 61 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_hamilt_lcao
        GlobalV 出现了 254 次
        GlobalC 出现了 97 次
        |-- hamilt_lcaodft
            GlobalV 出现了 67 次
            GlobalC 出现了 90 次
            |-- operator_lcao
                GlobalV 出现了 1 次
                GlobalC 出现了 29 次
                |-- test
                    GlobalV 出现了 0 次
                    GlobalC 出现了 14 次
        |-- module_dftu
            GlobalV 出现了 9 次
            GlobalC 出现了 5 次
        |-- module_tddft
            GlobalV 出现了 93 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_hcontainer
            GlobalV 出现了 6 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 6 次
                GlobalC 出现了 0 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- module_deepks
            GlobalV 出现了 40 次
            GlobalC 出现了 2 次
            |-- sphinx
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- source
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 23 次
                GlobalC 出现了 0 次
            |-- doxygen
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_deltaspin
            GlobalV 出现了 7 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_gint
            GlobalV 出现了 32 次
            GlobalC 出现了 0 次
            |-- kernels
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- cuda
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_hamilt_general
        GlobalV 出现了 44 次
        GlobalC 出现了 133 次
        |-- module_ewald
            GlobalV 出现了 7 次
            GlobalC 出现了 8 次
        |-- module_vdw
            GlobalV 出现了 2 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 2 次
                GlobalC 出现了 0 次
        |-- module_xc
            GlobalV 出现了 5 次
            GlobalC 出现了 21 次
            |-- kernels
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- cuda
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- rocm
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- test
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 5 次
                GlobalC 出现了 5 次
        |-- module_surchem
            GlobalV 出现了 30 次
            GlobalC 出现了 104 次
            |-- test
                GlobalV 出现了 30 次
                GlobalC 出现了 103 次
                |-- support
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
    |-- module_rdmft
        GlobalV 出现了 5 次
        GlobalC 出现了 15 次
    |-- module_io
        GlobalV 出现了 647 次
        GlobalC 出现了 77 次
        |-- json_output
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test_serial
            GlobalV 出现了 7 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 248 次
            GlobalC 出现了 7 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_basis
        GlobalV 出现了 51 次
        GlobalC 出现了 1 次
        |-- module_nao
            GlobalV 出现了 24 次
            GlobalC 出现了 1 次
            |-- test
                GlobalV 出现了 19 次
                GlobalC 出现了 0 次
        |-- module_ao
            GlobalV 出现了 24 次
            GlobalC 出现了 0 次
            |-- 1_Documents
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- sphinx
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                    |-- source
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                |-- doxygen
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 14 次
                GlobalC 出现了 0 次
                |-- orb_obj
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- GaAs
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- lcao_H2O
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
        |-- module_pw
            GlobalV 出现了 3 次
            GlobalC 出现了 0 次
            |-- test_serial
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- kernels
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- cuda
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- rocm
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- test
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 3 次
                GlobalC 出现了 0 次
            |-- module_fft
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_psi
        GlobalV 出现了 73 次
        GlobalC 出现了 8 次
        |-- test
            GlobalV 出现了 17 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_lr
        GlobalV 出现了 41 次
        GlobalC 出现了 2 次
        |-- ri_benchmark
            GlobalV 出现了 1 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- dm_trans
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- operator_casida
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
        |-- potentials
            GlobalV 出现了 6 次
            GlobalC 出现了 0 次
        |-- AX
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- utils
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_hsolver
        GlobalV 出现了 58 次
        GlobalC 出现了 34 次
        |-- module_pexsi
            GlobalV 出现了 3 次
            GlobalC 出现了 0 次
        |-- kernels
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- cuda
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- rocm
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- genelpa
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 24 次
            GlobalC 出现了 0 次
    |-- module_base
        GlobalV 出现了 167 次
        GlobalC 出现了 1 次
        |-- grid
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test_parallel
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
        |-- libm
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_mixing
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- kernels
            GlobalV 出现了 0 次
            GlobalC 出现了 1 次
            |-- cuda
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- rocm
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- dsp
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 52 次
            GlobalC 出现了 0 次
            |-- data
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_device
            GlobalV 出现了 2 次
            GlobalC 出现了 0 次
            |-- cuda
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- rocm
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- module_container
            GlobalV 出现了 0 次
            GlobalC 出现了 0 次
            |-- base
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- core
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- third_party
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- macros
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- utils
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
            |-- ATen
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
                |-- core
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                |-- ops
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                    |-- test
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                |-- kernels
                    GlobalV 出现了 0 次
                    GlobalC 出现了 0 次
                    |-- cuda
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                    |-- rocm
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
                    |-- test
                        GlobalV 出现了 0 次
                        GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
    |-- module_cell
        GlobalV 出现了 411 次
        GlobalC 出现了 18 次
        |-- module_paw
            GlobalV 出现了 58 次
            GlobalC 出现了 2 次
            |-- test
                GlobalV 出现了 2 次
                GlobalC 出现了 0 次
        |-- module_neighbor
            GlobalV 出现了 7 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 4 次
                GlobalC 出现了 0 次
        |-- module_symmetry
            GlobalV 出现了 82 次
            GlobalC 出现了 0 次
            |-- test
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test_pw
            GlobalV 出现了 4 次
            GlobalC 出现了 0 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
        |-- test
            GlobalV 出现了 112 次
            GlobalC 出现了 4 次
            |-- support
                GlobalV 出现了 0 次
                GlobalC 出现了 0 次
行数大于 500 行的文件:
./abacus-develop/source/module_md/md_func.cpp: 527 行
./abacus-develop/source/module_md/nhchain.cpp: 887 行
./abacus-develop/source/module_esolver/esolver_of.cpp: 561 行
./abacus-develop/source/module_esolver/esolver_ks_lcao.cpp: 1315 行
./abacus-develop/source/module_esolver/esolver_ks_pw.cpp: 967 行
./abacus-develop/source/module_esolver/esolver_of_tool.cpp: 521 行
./abacus-develop/source/module_esolver/esolver_ks.cpp: 730 行
./abacus-develop/source/module_relax/relax_old/bfgs.cpp: 543 行
./abacus-develop/source/module_relax/relax_old/ions_move_cg.cpp: 501 行
./abacus-develop/source/module_relax/relax_old/test/lattice_change_cg_test.cpp: 535 行
./abacus-develop/source/module_relax/relax_old/test/lattice_change_basic_test.cpp: 529 行
./abacus-develop/source/module_relax/relax_old/test/ions_move_cg_test.cpp: 593 行
./abacus-develop/source/module_relax/relax_new/relax.cpp: 701 行
./abacus-develop/source/module_ri/exx_abfs-construct_orbs.cpp: 503 行
./abacus-develop/source/module_hamilt_pw/hamilt_stodft/sto_iter.cpp: 762 行
./abacus-develop/source/module_hamilt_pw/hamilt_stodft/sto_elecond.cpp: 1016 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/onsite_proj_tools.cpp: 1023 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/onsite_projector.cpp: 643 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/forces.cpp: 845 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/fs_nonlocal_tools.cpp: 830 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/VNL_in_pw.cpp: 1887 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/kernels/stress_op.cpp: 765 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/kernels/test/force_op_test.cpp: 3020 行
./abacus-develop/source/module_hamilt_pw/hamilt_pwdft/kernels/test/vnl_op_test.cpp: 4126 行
./abacus-develop/source/module_hamilt_pw/hamilt_ofdft/kedf_wt.cpp: 583 行
./abacus-develop/source/module_elecstate/elecstate_pw.cpp: 569 行
./abacus-develop/source/module_elecstate/occupy.cpp: 611 行
./abacus-develop/source/module_elecstate/module_charge/charge.cpp: 811 行
./abacus-develop/source/module_elecstate/module_charge/charge_mixing_rho.cpp: 620 行
./abacus-develop/source/module_elecstate/test/potential_new_test.cpp: 673 行
./abacus-develop/source/module_elecstate/test/elecstate_base_test.cpp: 574 行
./abacus-develop/source/module_elecstate/test/charge_mixing_test.cpp: 1145 行
./abacus-develop/source/module_elecstate/test/support/WAVEFUNC1.txt: 4231 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/LCAO_nl_mu.cpp: 585 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/LCAO_set_st.cpp: 554 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/record_adj.cpp: 507 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/FORCE_STRESS.cpp: 1101 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/hamilt_lcao.cpp: 517 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/operator_lcao/dftu_lcao.cpp: 539 行
./abacus-develop/source/module_hamilt_lcao/hamilt_lcaodft/operator_lcao/dspin_lcao.cpp: 533 行
./abacus-develop/source/module_hamilt_lcao/module_dftu/dftu_occup.cpp: 527 行
./abacus-develop/source/module_hamilt_lcao/module_dftu/dftu_io.cpp: 519 行
./abacus-develop/source/module_hamilt_lcao/module_dftu/dftu_force.cpp: 665 行
./abacus-develop/source/module_hamilt_lcao/module_tddft/propagator.cpp: 615 行
./abacus-develop/source/module_hamilt_lcao/module_tddft/td_current.cpp: 516 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/func_transfer.cpp: 663 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/atom_pair.cpp: 873 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/transfer.cpp: 672 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/hcontainer.cpp: 838 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/test/test_hcontainer_complex.cpp: 576 行
./abacus-develop/source/module_hamilt_lcao/module_hcontainer/test/test_hcontainer.cpp: 673 行
./abacus-develop/source/module_hamilt_lcao/module_deepks/LCAO_deepks_io.cpp: 610 行
./abacus-develop/source/module_hamilt_lcao/module_deepks/test/klist_1.cpp: 605 行
./abacus-develop/source/module_hamilt_lcao/module_deltaspin/cal_mw_from_lambda.cpp: 527 行
./abacus-develop/source/module_hamilt_lcao/module_deltaspin/spin_constrain.cpp: 590 行
./abacus-develop/source/module_hamilt_lcao/module_gint/grid_technique.cpp: 771 行
./abacus-develop/source/module_hamilt_lcao/module_gint/gint_k_sparse1.cpp: 555 行
./abacus-develop/source/module_hamilt_lcao/module_gint/kernels/cuda/code_gen.cpp: 4426 行
./abacus-develop/source/module_hamilt_lcao/module_gint/test/test_sph.cpp: 597 行
./abacus-develop/source/module_hamilt_general/module_vdw/vdwd3_autoset_xcparam.cpp: 581 行
./abacus-develop/source/module_hamilt_general/module_vdw/vdwd3_parameters_tab.cpp: 33131 行
./abacus-develop/source/module_hamilt_general/module_vdw/vdwd3_autoset_xcname.cpp: 606 行
./abacus-develop/source/module_hamilt_general/module_vdw/vdwd3.cpp: 1538 行
./abacus-develop/source/module_hamilt_general/module_vdw/test/vdw_test.cpp: 603 行
./abacus-develop/source/module_hamilt_general/module_xc/xc_functional_gradcorr.cpp: 794 行
./abacus-develop/source/module_hamilt_general/module_xc/test/test_xc.cpp: 923 行
./abacus-develop/source/module_hamilt_general/module_xc/test/test_xc2.cpp: 519 行
./abacus-develop/source/module_io/get_pchg_lcao.cpp: 551 行
./abacus-develop/source/module_io/read_input_item_system.cpp: 794 行
./abacus-develop/source/module_io/to_wannier90_lcao.cpp: 1214 行
./abacus-develop/source/module_io/winput.cpp: 907 行
./abacus-develop/source/module_io/write_dos_lcao.cpp: 692 行
./abacus-develop/source/module_io/output_mulliken.cpp: 629 行
./abacus-develop/source/module_io/get_wf_lcao.cpp: 759 行
./abacus-develop/source/module_io/numerical_basis.cpp: 863 行
./abacus-develop/source/module_io/to_wannier90_pw.cpp: 1057 行
./abacus-develop/source/module_io/read_input_item_other.cpp: 530 行
./abacus-develop/source/module_io/cal_r_overlap_R.cpp: 722 行
./abacus-develop/source/module_io/read_input_item_elec_stru.cpp: 848 行
./abacus-develop/source/module_io/to_wannier90.cpp: 517 行
./abacus-develop/source/module_io/write_HS_sparse.cpp: 800 行
./abacus-develop/source/module_io/to_qo_kernel.cpp: 605 行
./abacus-develop/source/module_io/unk_overlap_lcao.cpp: 646 行
./abacus-develop/source/module_io/read_input_item_output.cpp: 551 行
./abacus-develop/source/module_io/berryphase.cpp: 756 行
./abacus-develop/source/module_io/read_input.cpp: 502 行
./abacus-develop/source/module_io/input_conv.cpp: 574 行
./abacus-develop/source/module_io/cif_io.cpp: 529 行
./abacus-develop/source/module_io/test_serial/read_input_item_test.cpp: 1768 行
./abacus-develop/source/module_io/test/to_qo_test.cpp: 1563 行
./abacus-develop/source/module_io/test/bessel_basis_test.cpp: 558 行
./abacus-develop/source/module_io/test/read_wfc_lcao_test.cpp: 772 行
./abacus-develop/source/module_basis/module_nao/numerical_radial.cpp: 518 行
./abacus-develop/source/module_basis/module_nao/beta_radials.cpp: 764 行
./abacus-develop/source/module_basis/module_nao/test/gaunt.txt: 7242 行
./abacus-develop/source/module_basis/module_nao/test/numerical_radial_test.cpp: 589 行
./abacus-develop/source/module_basis/module_ao/ORB_read.cpp: 613 行
./abacus-develop/source/module_basis/module_ao/ORB_atomic_lm.cpp: 773 行
./abacus-develop/source/module_basis/module_ao/test/ORB_nonlocal_lm_test.cpp: 758 行
./abacus-develop/source/module_basis/module_ao/test/ORB_atomic_lm_test.cpp: 889 行
./abacus-develop/source/module_basis/module_pw/pw_transform_k.cpp: 520 行
./abacus-develop/source/module_psi/wf_atomic.cpp: 839 行
./abacus-develop/source/module_psi/wavefunc.cpp: 513 行
./abacus-develop/source/module_psi/psi.cpp: 508 行
./abacus-develop/source/module_psi/test/psi_initializer_unit_test.cpp: 770 行
./abacus-develop/source/module_lr/esolver_lrtd_lcao.cpp: 726 行
./abacus-develop/source/module_hsolver/diago_iter_assist.cpp: 620 行
./abacus-develop/source/module_hsolver/diago_david.cpp: 1133 行
./abacus-develop/source/module_hsolver/hsolver_pw.cpp: 676 行
./abacus-develop/source/module_hsolver/diago_cg.cpp: 642 行
./abacus-develop/source/module_hsolver/diago_dav_subspace.cpp: 793 行
./abacus-develop/source/module_hsolver/module_pexsi/dist_matrix_transformer.cpp: 765 行
./abacus-develop/source/module_hsolver/kernels/test/math_kernel_test.cpp: 751 行
./abacus-develop/source/module_base/cubic_spline.cpp: 566 行
./abacus-develop/source/module_base/math_chebyshev.cpp: 772 行
./abacus-develop/source/module_base/opt_DCsrch.cpp: 732 行
./abacus-develop/source/module_base/memory.cpp: 501 行
./abacus-develop/source/module_base/math_ylmreal.cpp: 721 行
./abacus-develop/source/module_base/math_lebedev_laikov.cpp: 5401 行
./abacus-develop/source/module_base/math_sphbes.cpp: 930 行
./abacus-develop/source/module_base/ylm.cpp: 1878 行
./abacus-develop/source/module_base/mcd.c: 884 行
./abacus-develop/source/module_base/test_parallel/parallel_reduce_test.cpp: 611 行
./abacus-develop/source/module_base/libm/sincos.cpp: 1262 行
./abacus-develop/source/module_base/test/global_function_test.cpp: 768 行
./abacus-develop/source/module_base/test/math_ylmreal_test.cpp: 514 行
./abacus-develop/source/module_base/test/vector3_test.cpp: 749 行
./abacus-develop/source/module_base/test/complexmatrix_test.cpp: 588 行
./abacus-develop/source/module_base/test/complexarray_test.cpp: 511 行
./abacus-develop/source/module_base/test/math_chebyshev_test.cpp: 648 行
./abacus-develop/source/module_base/module_device/device.cpp: 714 行
./abacus-develop/source/module_base/module_container/ATen/ops/einsum_op.cpp: 1048 行
./abacus-develop/source/module_base/module_container/test/tensor_test.cpp: 536 行
./abacus-develop/source/module_cell/unitcell.cpp: 953 行
./abacus-develop/source/module_cell/read_pp_upf100.cpp: 529 行
./abacus-develop/source/module_cell/klist.cpp: 1442 行
./abacus-develop/source/module_cell/read_atoms.cpp: 1246 行
./abacus-develop/source/module_cell/read_pp_upf201.cpp: 896 行
./abacus-develop/source/module_cell/module_paw/paw_cell_libpaw.cpp: 951 行
./abacus-develop/source/module_cell/module_paw/paw_cell.cpp: 774 行
./abacus-develop/source/module_cell/module_symmetry/symmetry.cpp: 2326 行
./abacus-develop/source/module_cell/module_symmetry/symmetry_basic.cpp: 1156 行
./abacus-develop/source/module_cell/test/unitcell_test_readpp.cpp: 579 行
./abacus-develop/source/module_cell/test/read_pp_test.cpp: 812 行
./abacus-develop/source/module_cell/test/klist_test.cpp: 781 行
./abacus-develop/source/module_cell/test/unitcell_test.cpp: 1834 行
东八区时间（北京时间）: 2025-04-01 10:35:20
The latest commit version in the repository is: 8eed91df69ac7734b7439f6c94d8b92de833ab6e
The commit time is: 2025-03-28 23:14:54 +0800
The latest tag is: v3.10.0
```
