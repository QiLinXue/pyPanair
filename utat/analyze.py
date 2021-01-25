from pyPanair.postprocess import read_ffmf
from pyPanair.postprocess import write_vtk
from prettytable import PrettyTable

ffmf = read_ffmf()
data = PrettyTable()
print("\n\n\n\n Analyzing...")

data.field_names = ["Property", "Value"]
data.add_row(["Angle of Attack", read_ffmf().alpha[0]])
data.add_row(["Coefficient of Lift", read_ffmf().cl[0]])
data.add_row(["Coefficient of Drag", read_ffmf().cdi[0]])
print(data)

write_vtk(n_wake=4)
print("VTK Generation Complete!")


# import pandas as pd
# from pyPanair.postprocess import calc_section_force
# calc_section_force(aoa=2.47, mac=9.9, rot_center=(63.6,0,0), casenum=1, networknum=1)

# section_force = pd.read_csv("section_force.csv")
# print(section_force)