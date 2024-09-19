# 以格点积分程序为例：一些代码开发习惯小贴士

<strong>作者：张昊翀，邮箱：zhc@iai.ustc.edu.cn</strong>

<strong>单位：合肥综合性国家科学中心人工智能研究院</strong>

<strong>日期：2024 年 7 月 14 日</strong>

# 前言

在 ABACUS 的代码开发的实际过程中，会遇到很多技术和非技术的问题。这里我们结合数值原子轨道的格点积分功能 GPU 化的代码开发经历，介绍相关的编程、开发、调试经验，希望对初入 ABACUS 的开发者有所启发和帮助。

# 一、格点积分的调试技巧

## 先易后难的调试过程

1. bx,by,bz 先都设成 1，1 能跑通再设成 2 等等
2. 同步算法和异步算法优先调通同步的。异步算法不要一次性的全异步化，事先根据代码结构，分块异步化。
3. 多 stream 并行先从 stream 数=1 开发调试。
4. 针对格点积分的问题特点构造例子，我调试的顺序

   1. 一个很大的（大于截断半径）晶胞中心一个铜原子，不考虑周期性边界条件
   2. 把原子放到晶胞的一个面上，只考虑一个面的周期性边界条件
   3. 缩小晶胞，考虑多个面的周期性边界条件
   4. 一个很大的（大于截断半径）晶胞中心两个铜原子，不考虑周期性边界条件
   5. 缩小晶胞
   6. 一个很大的（大于截断半径）晶胞中心一个铜原子和一个氧原子，不考虑周期性边界条件，考虑多种类型的原子
   7. 以上都调通基本上也没发现 bug 了

## 尽量构建更小规模的单元测试

1. 对格点积分 GPU 开发来说，我构建了批量矩阵乘的单元测试。测试方法主要是和 CPU 矩阵乘比较计算结果。
2. 对 GPU 开发来说，构建单元测试的一个有效方法是开发完 cuda 之后再写一份 CPU 的代码，然后比较计算结果。

   1. 对于 abacus 来说，和 GPU 输出相同算法相同的 CPU 代码往往可以利用现有的 CPU 代码重构得到。

# 二、开发节奏

小步快跑，快速积累和迭代。

## 多提交

1. 每次完成一个小的原子改动就应该 commit 一下。
2. 每次 commit 应该只包含一个功能点相关的改动。
3. 每次 commit 的代码改动量最好不要超过 150 行。
4. 每次 pr 可能是过去几个月 commit 的积累。

## 多测试

1. 每次 commit 前先用两到三个有代表性的小例子做个快速的测试，尽量保证自己 commit 的代码都是能跑对的，如果 commit 会临时造成计算结果错误那么要在 message 里注明。
2. 每天晚上可以对当日积累的提交做个比较全面的全量测试。如果有例子测试不过可以单独挑出来回退版本看是哪个 commit 引起的。

## 多交流

1. 要充分利用他人的碎片时间来对自己的代码进行 Code review。每次 commit 的代码尽量让别人在 10 分钟的时间内完成 code review。
2. 好好写 message，写给别人看，也写给自己看。一般人三天以后是看不懂自己写了啥的。

# 三、内存错误怎么调试

## 先启用调试信息和编译 debug 版本

```bash
cmake -B build -DUSE_CUDA=ON -DCMAKE_BUILD_TYPE=Debug -DDEBUG_INFO=ON
cmake --build build -j`nproc`
```

如果 debug 版本能跑对，但是 release 版本跑不对……那事情就大条了。这种情况有一些是多线程或者代码异步执行导致的。

## core dump

请参考以下的教程：

[https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/developer_guide/debugging-crashed-application](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/developer_guide/debugging-crashed-application)

[https://developer.toradex.com/software/linux-resources/linux-features/enable-and-analyse-core-dumps-in-linux/](https://developer.toradex.com/software/linux-resources/linux-features/enable-and-analyse-core-dumps-in-linux/)

## gdb 或 cuda-gdb

gdb 执行程序调试，直接 run，正常情况下出现内存错误的时候就会停住。然后使用 bt 命令可以查看调用栈，可以定位代码。

## Valgrind

内存泄露等错误的利器

[https://valgrind.org/docs/manual/quick-start.html](https://valgrind.org/docs/manual/quick-start.html)

## 善用 assert 断言

有效帮助我们规范内存使用逻辑

例如：

```cpp
hamilt::AtomPair<double>* tmp_ap = hR->find_pair(iat1, iat2);
#ifdef __DEBUG
    assert(tmp_ap!=nullptr);
#endif
```

最好和__DEBUG 选项配合使用。
