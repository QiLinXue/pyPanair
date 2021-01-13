from pyPanair.postprocess import read_ffmf
read_ffmf()

from pyPanair.postprocess import write_vtk, write_tec
write_vtk(n_wake=4)
write_tec()