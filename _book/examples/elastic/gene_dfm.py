from pymatgen.core.structure import Structure
from pymatgen.analysis.elasticity.elastic import Strain
from pymatgen.analysis.elasticity.strain import DeformedStructureSet
import os, sys, dpdata, glob
from monty.serialization import dumpfn

try:
    run_type = sys.argv[1]
except:
    print("Usage: python gene_dfm.py [abacus|vasp]")
    sys.exit(1)

cwd = os.getcwd()
path_to_equi = os.path.join(cwd, 'relax')

if  run_type == "abacus":
    CONTCAR = os.path.join('OUT.*', 'STRU_ION_D')
    POSCAR = "STRU"
    INCAR = "INPUT"
    KPOINTS = "KPT"
elif run_type == "vasp":
    CONTCAR = "CONTCAR"
    POSCAR = "POSCAR"
    INCAR = "INCAR"
    KPOINTS = "KPOINTS"

# print(CONTCAR)
equi_contcar = glob.glob(os.path.join(path_to_equi, CONTCAR))[0]
# print(equi_contcar)
if not os.path.exists(equi_contcar):
    raise RuntimeError("Please do relaxation first!")

if run_type == "abacus":
    stru = dpdata.System(equi_contcar, fmt = "stru")
    stru.to("poscar", "POSCAR.tmp")
    ss = Structure.from_file("POSCAR.tmp")
    os.remove("POSCAR.tmp")
elif run_type == "vasp":
    ss = Structure.from_file(equi_contcar)

norm_strains = [-0.010, -0.005, 0.005, 0.010]
shear_strains = [-0.010, -0.005, 0.005, 0.010]

dfm_ss = DeformedStructureSet(ss, symmetry=False, norm_strains=norm_strains, shear_strains=shear_strains)
# print(dfm_ss)
n_dfm = len(dfm_ss)

print("gen with norm " + str(norm_strains))
print("gen with shear " + str(shear_strains))
for ii in range(n_dfm):
    output_task = os.path.join('./', "task.%03d" % ii)
    os.makedirs(output_task, exist_ok=True)
    os.chdir(output_task)
    dfm_ss.deformed_structures[ii].to("POSCAR", fmt = "POSCAR")
    if run_type == "abacus":
        stru = dpdata.System("POSCAR", fmt="vasp/poscar")
        n_atoms = len(stru["atom_names"])
        atom_mass = []
        pseudo = []
        orb = []
        with open(equi_contcar, "r") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            if "ATOMIC_SPECIES" in line:
                for i in range(n_atoms):
                    atom_mass.append(float(lines[idx+i+1].split()[1]))
                    pseudo.append(lines[idx+i+1].split()[2])
            if "NUMERICAL_ORBITAL" in line:
                for i in range(n_atoms):
                    orb.append(lines[idx+i+1])
        if orb == []:
            stru.to("stru", "STRU", mass=atom_mass, pp_file=pseudo)
        else:
            stru.to("stru", "STRU", mass=atom_mass, pp_file=pseudo, numerical_orbital=orb)
        os.remove("POSCAR")
    os.system("cp ../{} .".format(INCAR))
    if run_type == "abacus":
        with open(INCAR, "r") as f:
            lines = f.readlines()
        pseudo_dir = "../"
        orb_dir = "../"
        for line in lines:
            if 'pseudo_dir' in line:
                if pseudo_dir != line.split()[1].strip():
                    line = line.replace(line, 'pseudo_dir ' + pseudo_dir)
            if 'orb_dir' in line:
                if orb_dir != line.split()[1].strip():
                    line = line.replace(line, 'orb_dir ' + orb_dir)
        with open(INCAR, "w") as f:
            f.writelines(lines)
    os.system("cp ../{} .".format(KPOINTS))
    if run_type == "vasp":
        os.system("cp ../POTCAR .")
    df = Strain.from_deformation(dfm_ss.deformations[ii])
    dumpfn(df.as_dict(), "strain.json", indent=4)
    os.chdir(cwd)
