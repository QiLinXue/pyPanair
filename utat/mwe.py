'''
for full documentation, see tutorial 3
'''

import numpy as np
from pyPanair.preprocess import wgs_creator

# Init
wgs = wgs_creator.LaWGS("agardb_mod")

# Airfoil
root_airfoil = wgs_creator.read_airfoil("mwe.csv", y_coordinate=0.5, expansion_ratio=2.598)
root_airfoil = root_airfoil.shift((4.5, 0., 0.))
tip_airfoil = root_airfoil.replace(x=7.098, y=2., z=0.)
wing = root_airfoil.linspace(tip_airfoil, num=30)
wgs.append_network("wing", wing, 1)

# Nose + Forebody
n_nose = 8  # number of points in the line
x_nose = np.linspace(0., 3., num=n_nose)  # x-coordinates of the line
y_nose = x_nose/3 * (1 - 1/9*(x_nose)**2 + 1/54*(x_nose)**3)  # y-coordinates of the line
nose_line = wgs_creator.Line(np.zeros((n_nose, 3)))  # create an array of zeros
nose_line[:,0] = x_nose
nose_line[:,1] = y_nose

fbody_p1 = wgs_creator.Point(nose_line[-1])  # point at the end of the nose_line
fbody_p2 = fbody_p1.replace(x=4.5)
fbody_line = fbody_p1.linspace(fbody_p2, num=4)  # interpolate fbody_p1 and fbody_p2

nose_fbody_line = nose_line.concat(fbody_line)  # concatenate nose_line & fbody_line

nose_fbody_up = list()
for i in np.linspace(0, 90, 7):
    line = nose_fbody_line.rotx(rotcenter=nose_fbody_line[0], angle=i)  # create a copy of nose_fbody_line and rotate it around the x-axis
    nose_fbody_up.append(line)
nose_fbody_up = wgs_creator.Network(nose_fbody_up)  # create a Network object from a list of Lines

nose_fbody_low = list()
for i in np.linspace(-90, 0, 7):
    line = nose_fbody_line.rotx(rotcenter=nose_fbody_line[0], angle=i)
    nose_fbody_low.append(line)
nose_fbody_low = wgs_creator.Network(nose_fbody_low)

wgs.append_network("n_fb_up", nose_fbody_up, 1)
wgs.append_network("n_fb_low", nose_fbody_low, 1)

# Midbody
wingroot_up, wingroot_low = root_airfoil.split_half()
mbody_line = wingroot_up.replace(z=0.)

mbody_up = list()
for i in np.linspace(90, 0, 7)[:-1]:
    line = mbody_line.rotx((0,0,0), angle=i)
    mbody_up.append(line)
mbody_up.append(wingroot_up)
mbody_up = wgs_creator.Network(mbody_up)
wgs.append_network("mbody_up", mbody_up, 1)

wingroot_low = wingroot_low.flip()
mbody_low = list()
mbody_low.append(wingroot_low)
for i in np.linspace(0, -90, 7)[1:]:
    line = mbody_line.rotx((0,0,0), angle=i)
    mbody_low.append(line)
mbody_low = wgs_creator.Network(mbody_low)
wgs.append_network("mbody_low", mbody_low, 1)

# Aft body
aft_body_p1 = wgs_creator.Point(root_airfoil[0])  # TE of the root airfoil
aft_body_p2 = aft_body_p1.shift((1.402, -0.05, 0.))
aft_body_line = aft_body_p1.linspace(aft_body_p2, num=6)

aft_body_up = list()
for i in np.linspace(0, 90, num=7):
    line = aft_body_line.rotx((0,0,0), angle=i)
    aft_body_up.append(line)
aft_body_up = wgs_creator.Network(aft_body_up)
wgs.append_network("abody_up", aft_body_up, 1)

aft_body_low = list()
for i in np.linspace(-90, 0, num=7):
    line = aft_body_line.rotx((0,0,0), angle=i)
    aft_body_low.append(line)
aft_body_low = wgs_creator.Network(aft_body_low)
wgs.append_network("abody_low", aft_body_low, 1)

# Base Body
body_base_line_up = aft_body_up.edge(3)  # create a `Line` that corresponds to edge3 of the `Network` `body_base_up`
body_base_line_up = body_base_line_up.flip()  # the order of points are reversed
body_base_line_low = aft_body_low.edge(3)
body_base_line_low = body_base_line_low.flip()
body_base_line = body_base_line_up.concat(body_base_line_low)
body_base_line2 = body_base_line.replace(x=8.5, y=0., z=0.)  # create a `Line` with 13 identical points (the center of the circle)
body_base = body_base_line.linspace(body_base_line2, num=3)
wgs.append_network("bodybase", body_base, boun_type=5)

# Wakes
wake_length = 2.3093 * 50
wing_wake = wing.make_wake(3, wake_length)
wgs.append_network("wingwake", wing_wake, 18)

body_base_wake_up = aft_body_up.make_wake(3, wake_length)
wgs.append_network("bbwake_up", body_base_wake_up, -18)
body_base_wake_low = aft_body_low.make_wake(3, wake_length)
wgs.append_network("bbwake_low", body_base_wake_low, -18)

body_wake = aft_body_up.make_bodywingwake(4, wake_length)
wgs.append_network("bodywake", body_wake, 20)

# Create
wgs.create_stl()
wgs.create_wgs()
wgs.create_aux(alpha=0, mach=3, cbar=2.3093, span=4., sref=6.928, xref=5.943, zref=0.)