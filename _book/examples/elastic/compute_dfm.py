from monty.serialization import loadfn, dumpfn
from pymatgen.analysis.elasticity.elastic import ElasticTensor
from pymatgen.analysis.elasticity.stress import Stress
import glob, os, sys
import numpy as np

def get_stress_vasp(lines: str) -> np.ndarray[3, 3]:
    stress = np.zeros([3,3])
    for line in lines:
        if "in kB" in line:
            stress_xx = float(line.split()[2])
            stress_yy = float(line.split()[3])
            stress_zz = float(line.split()[4])
            stress_xy = float(line.split()[5])
            stress_yz = float(line.split()[6])
            stress_zx = float(line.split()[7])
            stress[0] = [stress_xx, stress_xy, stress_zx]
            stress[1] = [stress_xy, stress_yy, stress_yz]
            stress[2] = [stress_zx, stress_yz, stress_zz]
    return stress

def get_stress_abacus(lines: str) -> np.ndarray[3, 3]:
    stress = np.zeros([3,3])
    for idx, line in enumerate(lines):
        if "TOTAL-STRESS (KBAR)" in line:
            stress_xx = float(lines[idx+2].split()[0])
            stress_yy = float(lines[idx+3].split()[1])
            stress_zz = float(lines[idx+4].split()[2])
            stress_xy = float(lines[idx+2].split()[1])
            stress_yz = float(lines[idx+3].split()[2])
            stress_zx = float(lines[idx+2].split()[2])
            stress[0] = [stress_xx, stress_xy, stress_zx]
            stress[1] = [stress_xy, stress_yy, stress_yz]
            stress[2] = [stress_zx, stress_yz, stress_zz]
    return stress

try:
    run_type = sys.argv[1]
except:
    print("Usage: python compute_dfm.py [abacus|vasp]")
    sys.exit(1)

if  run_type == "abacus":
    OUTCAR = "OUT.*/running_*.log"
elif run_type == "vasp":
    OUTCAR = "OUTCAR"

cwd = os.getcwd()
# print(cwd)

# equi_stress
equi = glob.glob(os.path.join(cwd, "relax/", OUTCAR))[0]
# print(equi)
with open(equi, "r") as fin:
    lines = fin.read().split("\n")
if run_type == "abacus":
    equi_stress = Stress(get_stress_abacus(lines) * (-1000))
elif run_type == "vasp":
    equi_stress = Stress(get_stress_vasp(lines) * (-1000))
    # print(equi_stress)


# read all the task dir
task_dirs = glob.glob("task.*")
lst_strain = []
lst_stress = []
for ii in task_dirs:
    os.chdir(os.path.join('./', ii))

    strain = loadfn("strain.json")
    # print(strain, strain.shape)

    stress = np.zeros([3,3])
    OUTCAR = glob.glob(OUTCAR)[0]
    with open(OUTCAR, "r") as fin:
        lines = fin.read().split("\n")
    if run_type == "abacus":
        stress = get_stress_abacus(lines)
    elif run_type == "vasp":
        stress = get_stress_vasp(lines)
    # print(stress, stress.shape)
    os.chdir(cwd)
    lst_strain.append(strain)
    lst_stress.append(Stress(stress * (-1000)))

# print(lst_strain)
et = ElasticTensor.from_independent_strains(lst_strain, lst_stress, eq_stress=equi_stress, vasp=False)

res_data = {}
ptr_data = '# Elastic Constants in GPa\n'
res_data["elastic_tensor"] = []
for ii in range(6):
    for jj in range(6):
        res_data["elastic_tensor"].append(et.voigt[ii][jj] / 1e4)
        ptr_data += "%7.2f " % (et.voigt[ii][jj] / 1e4)
    ptr_data += "\n"
BV = et.k_voigt / 1e4
GV = et.g_voigt / 1e4
EV = 9 * BV * GV / (3 * BV + GV)
uV = 0.5 * (3 * BV - 2 * GV) / (3 * BV + GV)
res_data["BV"] = BV
res_data["GV"] = GV
res_data["EV"] = EV
res_data["uV"] = uV
ptr_data += "# Bulk   Modulus BV = %.2f GPa\n" % BV
ptr_data += "# Shear  Modulus GV = %.2f GPa\n" % GV
ptr_data += "# Youngs Modulus EV = %.2f GPa\n" % EV
ptr_data += "# Poission Ratio uV = %.2f " % uV
print(ptr_data)
dumpfn(res_data, "elastic.json", indent=4)
