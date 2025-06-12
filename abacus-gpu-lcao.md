# ABACUS LCAO 基组 GPU 版本使用说明

**作者：邓子超，邮箱：zcdeng@pku.edu.cnmailto:zcdeng@pku.edu.cn**

**审核：陈默涵，邮箱：mohanchen@pku.edu.cn**

**最后更新时间：2025/06/05**

**文档对应 notebook：[ABACUS LCAO 基组 GPU 版本使用介绍 | Bohrium](https://bohrium.dp.tech/notebooks/29414947682)**

# 一、简介

为了提升 ABACUS 的运行效率，2024 年 10 月发布的 ABACUS 3.8 版本支持 GPU 环境下采用 LCAO（Linear Combination of Atomic Orbitals）基组（即数值原子轨道基组）对 Kohn-Sham 方程进行求解。目前该版本提供 GPU 支持的模块有广义本征值求解器以及实空间生成哈密顿量的格点积分，这两部分也是 LCAO 基组求解 Kohn-Sham 方程的热点。在广义本征值求解器方面，目前 3.8 版本集成了 cuSolver，cuSolverMP，ELPA 软件，从而可以支持单卡和多卡的 GPU 加速。在格点积分模块里我们自研了 GPU 积分加速算法。开发团队未来还会针对 LCAO 算的更多模块提供 GPU 硬件以及其它国产硬件的支持。

# 二、安装

要使用 GPU 版的 ABACUS，使用 CMAKE 编译 ABACUS 的时候（ABACUS 编译方法详见 [https://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html](https://abacus.deepmodeling.com/en/latest/quick_start/easy_install.html)），需要进行如下设置。

- 格点积分 GPU 版支持，以及 cusolver 求解器支持：需要安装 cuda-toolkit，并在编译 ABACUS 时设置 `-DUSE_CUDA=ON`。
- (可选项)cusolvermp 求解器支持：编译 ABACUS 之前，需要确保系统上安装了 cusolvermp 相关库，具体安装方法见 [https://docs.nvidia.com/cuda/cusolvermp/](https://docs.nvidia.com/cuda/cusolvermp/)**。**除了设置 `-DUSE_CUDA=ON` 之外，还需要设置 `-DENABLE_CUSOLVERMP=ON`。
- (可选项)GPU 版 ELPA 求解器支持：编译 ABACUS 之前，需要确保系统上安装了支持 GPU 版本的 ELPA，安装方法详见 [https://github.com/marekandreas/elpa/blob/master/documentation/INSTALL.md](https://github.com/marekandreas/elpa/blob/master/documentation/INSTALL.md)，安装过程可以参考 [https://github.com/deepmodeling/abacus-develop/pull/4969](https://github.com/deepmodeling/abacus-develop/pull/4969)。安装好 ELPA 之后，在编译 ABACUS 时，需要设置 `-DUSE_CUDA=ON`, `-DUSE_ELPA=ON`。

# 三、使用

## 1. INPUT 参数设置

目前 ABACUS 的 LCAO 基组已经 GPU 化的模块包括**格点积分模块**和**广义特征值求解**模块。这两个模块是否使用 GPU 加速可以分开设置。与格点积分和广义特征值求解相关的输入参数包括 `device` 以及 `ks_solver`。下面详细介绍一下这两个参数的设置，注意以下介绍基于 ABACUS 的 LCAO 基组（INPUT 文件中的 `basis_type` 需要设置为 `lcao`）。

- device:`device` 用于指定 ABACUS 是否使用 GPU 来加速运算，可以设置为 `cpu` 或者 `gpu`。如果编译的是 GPU 版的 ABACUS（编译时设置了 `-DUSE_CUDA=ON`），同时机器中至少有一张 GPU 卡，那么 `device` 的默认值为 `gpu`,否则为 `cpu`。

  - 如果 `device` 设置为 `gpu`, 那么 ABACUS 将使用 GPU 来加速计算，对应的，格点积分将使用 GPU 加速计算，广义特征值求解器 `ks_solver` 也将默认设置为 `cusolver`, 如果您的机器包含多张 GPU，也可以将 `ks_solver` 设置为 `cusolvermp` 或者 `elpa` 来调用多卡求解特征值；
  - 如果 `device` 设置为 `cpu`，ABACUS 将使用 CPU 进行计算，格点积分部分也会使用 CPU 计算，广义特征值求解器 `ks_solver` 默认设置为 `scalapack_gvx`,`genelpa`,或者 `lapack`(默认值详见 [https://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#ks-solver](https://abacus.deepmodeling.com/en/latest/advanced/input_files/input-main.html#ks-solver))
- ks_solver:`ks_solver` 用于设置广义特征值求解器，目前 LCAO 基组支持的广义特征值求解器有 `lapack`,`scalapack_gvx`,`genelpa`,`cusolver`,`cusolvermp`,`elpa`。其中 `cusolver`,`cusolvermp` 与 `elpa` 可以调用 GPU 进行广义特征值求解,`cusolver` 只支持单 GPU 卡求解，`cusolvermp` 与 `elpa` 支持多 GPU 卡求解。

在 INPUT 文件中设置好 `device` 和 `ks_solver` 参数后，运行 ABACUS，即可调用 GPU 进行运算。

## 2. 多卡计算

ABACUS 的格点积分模块以及广义特征值求解模块均支持多块 GPU 卡加速，ABACUS 调用的 GPU 数量通过 MPI 进程数来设置。如果设置 n 个进程，ABACUS 将会自动调用 n 张 GPU 卡来进行计算，若机器中的 GPU 卡数小于 n，ABACUS 则会调用机器中所有 GPU 卡来进行运算，不推荐进程数设置成大于 GPU 卡数。需要注意的是，ABACUS 的广义特征值求解部分只有 `cusolvermp` 和 `elpa` 支持多卡加速，如果 `ks_solver` 设置成 `cusolver`，无论设置多少个进程，ABACUS 都只会调用一张 GPU 卡来进行广义特征值求解。

# 四、示例

下面以 `tests/performance/P102_si64_lcao` 的 64 个金刚石结构的硅原子体系为例，展示如何使用 GPU 版 ABACUS 进行 LCAO 基组下的计算。

环境：GPU/双 3090, CPU / Intel(R) Xeon(R) Gold 6132 CPU @ 2.60GHz

ABACUS 版本号：3.8.0, commit:72b1d7ce9

## 1. **GPU 算例和结果**

我们首先调用双 GPU 卡进行格点积分运算，同时使用 cusolver 进行广义特征值求解：修改 `INPUT` 文件，添加一行 `“device gpu”`, 同时将 `ks_solver` 设置为 `cusolver`，运行命令 `“OMP_NUM_THREADS=12 mpirun -n 2 abacus"`, 输出为：

```sql
Info: Local MPI proc number: 2,OpenMP thread number: 12,Total thread number: 24,Local thread limit: 56
                                                                                     
                              ABACUS v3.8.0

               Atomic-orbital Based Ab-initio Computation at UStc                    

                     Website: http://abacus.ustc.edu.cn/                             
               Documentation: https://abacus.deepmodeling.com/                       
                  Repository: https://github.com/abacusmodeling/abacus-develop       
                              https://github.com/deepmodeling/abacus-develop         
                      Commit: 72b1d7ce9 (Sat Oct 5 16:46:53 2024 +0800)

 Sat Oct  5 19:04:21 2024
 MAKE THE DIR         : OUT.autotest/
 RUNNING WITH DEVICE  : GPU / NVIDIA GeForce RTX 3090
 UNIFORM GRID DIM        : 192 * 192 * 96
 UNIFORM GRID DIM(BIG)   : 48 * 48 * 24
 DONE(0.652318   SEC) : SETUP UNITCELL
 DONE(0.70875    SEC) : SYMMETRY
 DONE(0.789308   SEC) : INIT K-POINTS
 ---------------------------------------------------------
 Self-consistent calculations for electrons
 ---------------------------------------------------------
 SPIN    KPOINTS         PROCESSORS  NBASE       
 1       1               2           832         
 ---------------------------------------------------------
 Use Systematically Improvable Atomic bases
 ---------------------------------------------------------
 ELEMENT ORBITALS        NBASE       NATOM       XC          
 Si      2s2p1d-8au      13          64          
 ---------------------------------------------------------
 Initial plane wave basis and FFT box
 ---------------------------------------------------------
 DONE(0.818906   SEC) : INIT PLANEWAVE
 -------------------------------------------
 SELF-CONSISTENT : 
 -------------------------------------------
 gemm_algo_selector::Fastest time: 0.03072 ms
 START CHARGE      : atomic
 DONE(8.17035    SEC) : INIT SCF
 * * * * * *
 << Start SCF iteration.
 ITER       ETOT/eV          EDIFF/eV         DRHO     TIME/s
 CU1     -6.83607351e+03   0.00000000e+00   1.7682e-01  13.42
 CU2     -6.83164916e+03   4.42435700e+00   1.2487e-01   7.31
 CU3     -6.83237991e+03  -7.30748856e-01   7.9826e-03   7.29
 CU4     -6.83238388e+03  -3.97353454e-03   1.2270e-03   7.22
 CU5     -6.83238393e+03  -5.42990673e-05   4.6013e-04   7.26
 CU6     -6.83238395e+03  -1.43977923e-05   3.8918e-05   7.30
 CU7     -6.83238395e+03  -3.55773794e-07   1.1467e-05   7.24
 CU8     -6.83238395e+03   3.54214631e-09   3.8113e-06   7.23
 CU9     -6.83238395e+03  -2.56457580e-09   6.6704e-08   6.62
 >> Leave SCF iteration.
 * * * * * *
----------------------------------------------------------------
 TOTAL-STRESS (KBAR)                                            
----------------------------------------------------------------
        30.8367522660        -0.0000000000         0.0000000000 
         0.0000000000        75.4069126649        36.2463263984 
         0.0000000000        36.2463263984        75.4069126649 
----------------------------------------------------------------
 TOTAL-PRESSURE: 60.550193 KBAR

TIME STATISTICS
----------------------------------------------------------------------------
    CLASS_NAME                NAME            TIME/s  CALLS   AVG/s  PER/%  
----------------------------------------------------------------------------
                   total                      95.57  11       8.69   100.00 
 Driver            reading                    0.13   1        0.13   0.14   
 Input_Conv        Convert                    0.12   1        0.12   0.12   
 Driver            driver_line                95.43  1        95.43  99.86  
 UnitCell          check_tau                  0.00   1        0.00   0.00   
 ESolver_KS_LCAO   before_all_runners         2.02   1        2.02   2.11   
 PW_Basis_Sup      setuptransform             0.29   1        0.29   0.30   
 PW_Basis_Sup      distributeg                0.27   1        0.27   0.28   
 mymath            heapsort                   0.09   1097     0.00   0.09   
 Symmetry          analy_sys                  0.06   1        0.06   0.06   
 PW_Basis_K        setuptransform             0.02   1        0.02   0.02   
 PW_Basis_K        distributeg                0.01   1        0.01   0.01   
 PW_Basis          setup_struc_factor         1.01   1        1.01   1.06   
 NOrbital_Lm       extra_uniform              0.04   5        0.01   0.04   
 Mathzone_Add1     SplineD2                   0.00   5        0.00   0.00   
 Mathzone_Add1     Cubic_Spline_Interpolation 0.00   5        0.00   0.00   
 Mathzone_Add1     Uni_Deriv_Phi              0.04   5        0.01   0.04   
 ppcell_vl         init_vloc                  0.04   1        0.04   0.04   
 Ions              opt_ions                   93.36  1        93.36  97.69  
 ESolver_KS_LCAO   runner                     77.64  1        77.64  81.24  
 ESolver_KS_LCAO   before_scf                 6.01   1        6.01   6.29   
 ESolver_KS_LCAO   beforesolver               0.27   1        0.27   0.28   
 ESolver_KS_LCAO   set_matrix_grid            0.19   1        0.19   0.20   
 atom_arrange      search                     0.00   1        0.00   0.00   
 Grid_Technique    init                       0.13   1        0.13   0.14   
 Grid_BigCell      grid_expansion_index       0.01   2        0.01   0.01   
 Record_adj        for_2d                     0.05   1        0.05   0.05   
 Grid_Driver       Find_atom                  0.01   1152     0.00   0.01   
 LCAO_domain       grid_prepare               0.00   1        0.00   0.00   
 Veff              initialize_HR              0.01   1        0.01   0.01   
 OverlapNew        initialize_SR              0.01   1        0.01   0.01   
 EkineticNew       initialize_HR              0.00   1        0.00   0.00   
 NonlocalNew       initialize_HR              0.03   1        0.03   0.03   
 Charge            set_rho_core               0.00   1        0.00   0.00   
 Charge            atomic_rho                 0.98   2        0.49   1.02   
 PW_Basis_Sup      recip2real                 30.81  74       0.42   32.24  
 PW_Basis_Sup      gathers_scatterp           1.36   74       0.02   1.42   
 Potential         init_pot                   3.73   1        3.73   3.90   
 Potential         update_from_charge         33.03  10       3.30   34.56  
 Potential         cal_fixed_v                0.42   1        0.42   0.44   
 PotLocal          cal_fixed_v                0.41   1        0.41   0.43   
 Potential         cal_v_eff                  32.52  10       3.25   34.03  
 H_Hartree_pw      v_hartree                  5.66   10       0.57   5.92   
 PW_Basis_Sup      real2recip                 8.21   85       0.10   8.59   
 PW_Basis_Sup      gatherp_scatters           2.45   85       0.03   2.56   
 PotXC             cal_v_eff                  26.76  10       2.68   28.00  
 XC_Functional     v_xc                       26.71  10       2.67   27.95  
 Potential         interpolate_vrs            0.05   10       0.00   0.05   
 Symmetry          rhog_symmetry              8.67   10       0.87   9.07   
 Symmetry          group fft grids            0.70   10       0.07   0.73   
 H_Ewald_pw        compute_ewald              0.02   1        0.02   0.03   
 Charge_Mixing     init_mixing                0.00   1        0.00   0.00   
 HSolverLCAO       solve                      23.39  9        2.60   24.47  
 HamiltLCAO        updateHk                   17.12  9        1.90   17.91  
 OperatorLCAO      init                       15.90  27       0.59   16.63  
 Veff              contributeHR               11.04  9        1.23   11.55  
 Gint_interface    cal_gint                   16.54  19       0.87   17.30  
 Gint_interface    cal_gint_vlocal            10.79  9        1.20   11.29  
 Gint_k            transfer_pvpR              0.25   9        0.03   0.26   
 OverlapNew        calculate_SR               1.18   1        1.18   1.23   
 OverlapNew        contributeHk               0.05   9        0.01   0.05   
 EkineticNew       contributeHR               1.18   9        0.13   1.23   
 EkineticNew       calculate_HR               1.17   1        1.17   1.23   
 NonlocalNew       contributeHR               3.59   9        0.40   3.76   
 NonlocalNew       calculate_HR               3.54   1        3.54   3.71   
 OperatorLCAO      contributeHk               0.05   9        0.01   0.05   
 HSolverLCAO       hamiltSolvePsiK            1.27   9        0.14   1.33   
 DiagoCusolver     cusolver                   1.22   9        0.14   1.28   
 ElecStateLCAO     psiToRho                   4.99   9        0.55   5.22   
 elecstate         cal_dm                     0.26   10       0.03   0.27   
 psiMulPsiMpi      pdgemm                     0.25   10       0.03   0.26   
 DensityMatrix     cal_DMR                    0.10   10       0.01   0.10   
 Gint              transfer_DMR               0.18   9        0.02   0.19   
 Gint_interface    cal_gint_rho               4.39   9        0.49   4.60   
 Charge_Mixing     get_drho                   0.04   9        0.00   0.04   
 Charge            mix_rho                    4.85   8        0.61   5.07   
 Charge            Broyden_mixing             0.27   8        0.03   0.29   
 ESolver_KS_LCAO   after_scf                  0.75   1        0.75   0.78   
 ModuleIO          write_rhog                 0.16   1        0.16   0.17   
 ESolver_KS_LCAO   cal_force                  15.72  1        15.72  16.45  
 Force_Stress_LCAO getForceStress             15.72  1        15.72  16.45  
 Forces            cal_force_loc              0.94   1        0.94   0.99   
 Forces            cal_force_ew               0.77   1        0.77   0.81   
 Forces            cal_force_cc               0.00   1        0.00   0.00   
 Forces            cal_force_scc              1.02   1        1.02   1.06   
 Stress_Func       stress_loc                 0.22   1        0.22   0.23   
 Stress_Func       stress_har                 0.13   1        0.13   0.14   
 Stress_Func       stress_ewa                 0.76   1        0.76   0.79   
 Stress_Func       stress_cc                  0.00   1        0.00   0.00   
 Stress_Func       stress_gga                 1.74   1        1.74   1.82   
 Force_LCAO        ftable                     10.13  1        10.13  10.60  
 Force_LCAO        allocate                   5.32   1        5.32   5.56   
 LCAO_domain       build_ST_new               2.55   2        1.28   2.67   
 LCAO_domain       vnl_mu_new                 2.67   1        2.67   2.79   
 Force_LCAO        cal_fedm                   0.06   1        0.06   0.06   
 Force_LCAO        cal_ftvnl_dphi             0.02   1        0.02   0.03   
 Force_LCAO        cal_fvl_dphi               1.36   1        1.36   1.42   
 Gint_interface    cal_gint_force             1.36   1        1.36   1.42   
 Force_LCAO        cal_fvnl_dbeta             3.37   1        3.37   3.52   
 ESolver_KS_LCAO   cal_stress                 0.00   1        0.00   0.00   
 ESolver_KS_LCAO   after_all_runners          0.00   1        0.00   0.00   
 ModuleIO          write_istate_info          0.00   1        0.00   0.00   
----------------------------------------------------------------------------


 START  Time  : Sat Oct  5 19:04:21 2024
 FINISH Time  : Sat Oct  5 19:05:56 2024
 TOTAL  Time  : 95
 SEE INFORMATION IN : OUT.autotest/
```

## 2. CPU 算例和结果

可以看到 GPU 运行用了 95 秒，接下来我们调用 CPU 进行计算，在 `INPUT` 文件中设置 `device` 为 `cpu`，同时设置 `ks_solver` 为 `scalapack_gvx`，运行命令 `“OMP_NUM_THREADS=12 mpirun -n 2 abacus"`, 输出：

```sql
Info: Local MPI proc number: 2,OpenMP thread number: 12,Total thread number: 24,Local thread limit: 56
                                                                                     
                              ABACUS v3.8.0

               Atomic-orbital Based Ab-initio Computation at UStc                    

                     Website: http://abacus.ustc.edu.cn/                             
               Documentation: https://abacus.deepmodeling.com/                       
                  Repository: https://github.com/abacusmodeling/abacus-develop       
                              https://github.com/deepmodeling/abacus-develop         
                      Commit: 72b1d7ce9 (Sat Oct 5 16:46:53 2024 +0800)

 Sat Oct  5 19:06:27 2024
 MAKE THE DIR         : OUT.autotest/
 RUNNING WITH DEVICE  : CPU / Intel(R) Xeon(R) Gold 6132 CPU @ 2.60GHz
 UNIFORM GRID DIM        : 192 * 192 * 96
 UNIFORM GRID DIM(BIG)   : 48 * 48 * 24
 DONE(0.274561   SEC) : SETUP UNITCELL
 DONE(0.330937   SEC) : SYMMETRY
 DONE(0.411047   SEC) : INIT K-POINTS
 ---------------------------------------------------------
 Self-consistent calculations for electrons
 ---------------------------------------------------------
 SPIN    KPOINTS         PROCESSORS  NBASE       
 1       1               2           832         
 ---------------------------------------------------------
 Use Systematically Improvable Atomic bases
 ---------------------------------------------------------
 ELEMENT ORBITALS        NBASE       NATOM       XC          
 Si      2s2p1d-8au      13          64          
 ---------------------------------------------------------
 Initial plane wave basis and FFT box
 ---------------------------------------------------------
 DONE(0.438332   SEC) : INIT PLANEWAVE
 -------------------------------------------
 SELF-CONSISTENT : 
 -------------------------------------------
 START CHARGE      : atomic
 DONE(7.72282    SEC) : INIT SCF
 * * * * * *
 << Start SCF iteration.
 ITER       ETOT/eV          EDIFF/eV         DRHO     TIME/s
 GE1     -6.83607351e+03   0.00000000e+00   1.7682e-01  25.64
 GE2     -6.83164916e+03   4.42435700e+00   1.2487e-01  19.58
 GE3     -6.83237991e+03  -7.30748856e-01   7.9826e-03  19.48
 GE4     -6.83238388e+03  -3.97353455e-03   1.2270e-03  19.56
 GE5     -6.83238393e+03  -5.42990735e-05   4.6013e-04  19.54
 GE6     -6.83238395e+03  -1.43977575e-05   3.8918e-05  19.67
 GE7     -6.83238395e+03  -3.55816331e-07   1.1467e-05  19.68
 GE8     -6.83238395e+03   3.53518576e-09   3.8113e-06  19.74
 GE9     -6.83238395e+03  -2.51817213e-09   6.6704e-08  19.04
 >> Leave SCF iteration.
 * * * * * *
----------------------------------------------------------------
 TOTAL-STRESS (KBAR)                                            
----------------------------------------------------------------
        30.8367522660        -0.0000000000         0.0000000000 
        -0.0000000000        75.4069126649        36.2463263984 
         0.0000000000        36.2463263984        75.4069126649 
----------------------------------------------------------------
 TOTAL-PRESSURE: 60.550193 KBAR

TIME STATISTICS
----------------------------------------------------------------------------
    CLASS_NAME                NAME            TIME/s  CALLS   AVG/s  PER/%  
----------------------------------------------------------------------------
                   total                      224.00 11       20.36  100.00 
 Driver            reading                    0.01   1        0.01   0.01   
 Input_Conv        Convert                    0.00   1        0.00   0.00   
 Driver            driver_line                223.99 1        223.99 99.99  
 UnitCell          check_tau                  0.00   1        0.00   0.00   
 ESolver_KS_LCAO   before_all_runners         1.75   1        1.75   0.78   
 PW_Basis_Sup      setuptransform             0.03   1        0.03   0.01   
 PW_Basis_Sup      distributeg                0.02   1        0.02   0.01   
 mymath            heapsort                   0.09   1097     0.00   0.04   
 Symmetry          analy_sys                  0.06   1        0.06   0.03   
 PW_Basis_K        setuptransform             0.02   1        0.02   0.01   
 PW_Basis_K        distributeg                0.01   1        0.01   0.00   
 PW_Basis          setup_struc_factor         1.00   1        1.00   0.45   
 NOrbital_Lm       extra_uniform              0.04   5        0.01   0.02   
 Mathzone_Add1     SplineD2                   0.00   5        0.00   0.00   
 Mathzone_Add1     Cubic_Spline_Interpolation 0.00   5        0.00   0.00   
 Mathzone_Add1     Uni_Deriv_Phi              0.04   5        0.01   0.02   
 ppcell_vl         init_vloc                  0.04   1        0.04   0.02   
 Ions              opt_ions                   222.19 1        222.19 99.19  
 ESolver_KS_LCAO   runner                     188.63 1        188.63 84.21  
 ESolver_KS_LCAO   before_scf                 5.96   1        5.96   2.66   
 ESolver_KS_LCAO   beforesolver               0.20   1        0.20   0.09   
 ESolver_KS_LCAO   set_matrix_grid            0.13   1        0.13   0.06   
 atom_arrange      search                     0.00   1        0.00   0.00   
 Grid_Technique    init                       0.07   1        0.07   0.03   
 Grid_BigCell      grid_expansion_index       0.01   2        0.01   0.01   
 Record_adj        for_2d                     0.05   1        0.05   0.02   
 Grid_Driver       Find_atom                  0.01   1152     0.00   0.00   
 LCAO_domain       grid_prepare               0.00   1        0.00   0.00   
 Veff              initialize_HR              0.01   1        0.01   0.00   
 OverlapNew        initialize_SR              0.01   1        0.01   0.00   
 EkineticNew       initialize_HR              0.00   1        0.00   0.00   
 NonlocalNew       initialize_HR              0.02   1        0.02   0.01   
 Charge            set_rho_core               0.01   1        0.01   0.00   
 Charge            atomic_rho                 0.98   2        0.49   0.44   
 PW_Basis_Sup      recip2real                 30.88  74       0.42   13.78  
 PW_Basis_Sup      gathers_scatterp           1.37   74       0.02   0.61   
 Potential         init_pot                   3.74   1        3.74   1.67   
 Potential         update_from_charge         33.04  10       3.30   14.75  
 Potential         cal_fixed_v                0.41   1        0.41   0.19   
 PotLocal          cal_fixed_v                0.41   1        0.41   0.18   
 Potential         cal_v_eff                  32.59  10       3.26   14.55  
 H_Hartree_pw      v_hartree                  5.67   10       0.57   2.53   
 PW_Basis_Sup      real2recip                 8.18   85       0.10   3.65   
 PW_Basis_Sup      gatherp_scatters           2.45   85       0.03   1.09   
 PotXC             cal_v_eff                  26.82  10       2.68   11.97  
 XC_Functional     v_xc                       26.78  10       2.68   11.95  
 Potential         interpolate_vrs            0.04   10       0.00   0.02   
 Symmetry          rhog_symmetry              8.58   10       0.86   3.83   
 Symmetry          group fft grids            0.69   10       0.07   0.31   
 H_Ewald_pw        compute_ewald              0.03   1        0.03   0.01   
 Charge_Mixing     init_mixing                0.00   1        0.00   0.00   
 HSolverLCAO       solve                      134.43 9        14.94  60.01  
 HamiltLCAO        updateHk                   71.31  9        7.92   31.83  
 OperatorLCAO      init                       70.08  27       2.60   31.29  
 Veff              contributeHR               65.22  9        7.25   29.12  
 Gint_interface    cal_gint                   135.97 19       7.16   60.70  
 Gint_interface    cal_gint_vlocal            64.86  9        7.21   28.95  
 Gint_Tools        cal_psir_ylm               22.23  41472    0.00   9.92   
 Gint_k            transfer_pvpR              0.25   9        0.03   0.11   
 OverlapNew        calculate_SR               1.19   1        1.19   0.53   
 OverlapNew        contributeHk               0.04   9        0.00   0.02   
 EkineticNew       contributeHR               1.19   9        0.13   0.53   
 EkineticNew       calculate_HR               1.18   1        1.18   0.53   
 NonlocalNew       contributeHR               3.59   9        0.40   1.60   
 NonlocalNew       calculate_HR               3.55   1        3.55   1.59   
 OperatorLCAO      contributeHk               0.05   9        0.01   0.02   
 HSolverLCAO       hamiltSolvePsiK            10.78  9        1.20   4.81   
 DiagoElpa         elpa_solve                 10.73  9        1.19   4.79   
 ElecStateLCAO     psiToRho                   52.34  9        5.82   23.37  
 elecstate         cal_dm                     0.16   10       0.02   0.07   
 psiMulPsiMpi      pdgemm                     0.16   10       0.02   0.07   
 DensityMatrix     cal_DMR                    0.09   10       0.01   0.04   
 Gint              transfer_DMR               0.18   9        0.02   0.08   
 Gint_interface    cal_gint_rho               51.86  9        5.76   23.15  
 Charge_Mixing     get_drho                   0.04   9        0.00   0.02   
 Charge            mix_rho                    4.86   8        0.61   2.17   
 Charge            Broyden_mixing             0.28   8        0.03   0.12   
 ESolver_KS_LCAO   after_scf                  0.74   1        0.74   0.33   
 ModuleIO          write_rhog                 0.16   1        0.16   0.07   
 ESolver_KS_LCAO   cal_force                  33.57  1        33.57  14.98  
 Force_Stress_LCAO getForceStress             33.56  1        33.56  14.98  
 Forces            cal_force_loc              0.97   1        0.97   0.44   
 Forces            cal_force_ew               0.77   1        0.77   0.34   
 Forces            cal_force_cc               0.00   1        0.00   0.00   
 Forces            cal_force_scc              1.05   1        1.05   0.47   
 Stress_Func       stress_loc                 0.23   1        0.23   0.10   
 Stress_Func       stress_har                 0.13   1        0.13   0.06   
 Stress_Func       stress_ewa                 0.75   1        0.75   0.34   
 Stress_Func       stress_cc                  0.00   1        0.00   0.00   
 Stress_Func       stress_gga                 1.76   1        1.76   0.79   
 Force_LCAO        ftable                     27.88  1        27.88  12.45  
 Force_LCAO        allocate                   5.29   1        5.29   2.36   
 LCAO_domain       build_ST_new               2.55   2        1.28   1.14   
 LCAO_domain       vnl_mu_new                 2.65   1        2.65   1.18   
 Force_LCAO        cal_fedm                   0.06   1        0.06   0.03   
 Force_LCAO        cal_ftvnl_dphi             0.02   1        0.02   0.01   
 Force_LCAO        cal_fvl_dphi               19.14  1        19.14  8.54   
 Gint_interface    cal_gint_force             19.14  1        19.14  8.54   
 Gint_Tools        cal_dpsir_ylm              6.23   2304     0.00   2.78   
 Gint_Tools        cal_dpsirr_ylm             1.84   2304     0.00   0.82   
 Force_LCAO        cal_fvnl_dbeta             3.36   1        3.36   1.50   
 ESolver_KS_LCAO   cal_stress                 0.00   1        0.00   0.00   
 ESolver_KS_LCAO   after_all_runners          0.00   1        0.00   0.00   
 ModuleIO          write_istate_info          0.00   1        0.00   0.00   
----------------------------------------------------------------------------


 START  Time  : Sat Oct  5 19:06:27 2024
 FINISH Time  : Sat Oct  5 19:10:11 2024
 TOTAL  Time  : 224
 SEE INFORMATION IN : OUT.autotest/
```

输出中的 `“RUNNING WITH DEVICE”` 一行标出了此次运算使用的设备，同时运行时间统计里可以看到格点积分以及广义特征值求解的具体耗时，通过这两项耗时可以对比 GPU 和 CPU 的计算效率。格点积分耗时对应 `cal_gint`, `cal_gint_vlocal`, `cal_gint_rho`,`cal_gint_force` 这几项，广义特征值求解对应 `hamiltSolvePsiK` 项（在上面输出中标黄项）。

可以看到 GPU 运行用了 95 秒，而同样体系用 CPU 运行用了 224 秒，GPU 对于该体系有一定的加速效果。

以上就是本教程的内容，希望对学习采用 ABACUS 结合 GPU 进行密度泛函理论计算的读者有所帮助，大家也可以在 bohrium 平台按照 [ABACUS LCAO 基组 GPU 版本使用介绍 | Bohrium](https://bohrium.dp.tech/notebooks/29414947682) 跑一遍实际安装使用流程，有问题可以发邮箱给作者（见开头）。
