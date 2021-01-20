from pyPanair.postprocess import read_ffmf
read_ffmf()

from pyPanair.postprocess import write_vtk, write_tec
write_vtk(n_wake=4)
write_tec()

import pandas as pd
from pyPanair.postprocess import calc_section_force
calc_section_force(aoa=2.47, mac=9.9, rot_center=(63.6,0,0), casenum=1, networknum=1)

section_force = pd.read_csv("section_force.csv")
print(section_force)