from pyPanair.postprocess import read_ffmf
read_ffmf()

from pyPanair.postprocess import write_vtk, write_tec
write_vtk(n_wake=4)
write_tec()

import pandas as pd
from pyPanair.postprocess import calc_section_force
calc_section_force(aoa=5., mac=2.3093, rot_center=(5.943,0,0), casenum=1, networknum=1)

section_force = pd.read_csv("section_force.csv")
print(section_force)