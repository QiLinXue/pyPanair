import numpy as np
from pyPanair.preprocess import wgs_creator
wgs = wgs_creator.LaWGS("main")

# Nose cone data
L = 19.05
R = 3.81

'''
AIRFOIL
'''
# Creates the base of the airfoil
root_airfoil = wgs_creator.read_airfoil("base_airfoil.csv", y_coordinate=R, expansion_ratio=1)
root_airfoil = root_airfoil.shift((86.84, 0., 0.))

# Creates the tip of the airfoil
tip_airfoil = wgs_creator.read_airfoil("base_airfoil.csv", y_coordinate=R, expansion_ratio=0.5555)
tip_airfoil = tip_airfoil.shift((89.38, 11.43, 0.))

# Connect the base and the tip to create two wings, then rotate them clockwise / counterclockwise
wing1 = root_airfoil.linspace(tip_airfoil, num=40)
wing1 = wing1.rotx((0,0,0), angle=45)

wing2 = root_airfoil.linspace(tip_airfoil, num=40)
wing2 = wing2.rotx((0,0,0), angle=-45)

# Add wings to WGS
wgs.append_network("wing1", wing1, 1)
wgs.append_network("wing2", wing2, 1)

'''
FILL IN WING TOP
'''
# Creates a copy of the tips of the airfoil
wing_base_line = tip_airfoil.copy()  
wing_base_line = wing_base_line.flip()

# create a `Line` with 7 identical points (the center of the fin tip)
wing_base_line = wing_base_line.replace(x=92.6, y=15.24, z=0.)  # create a `Line` with 13 identical points (the center of the circle)
wing_base_line = wing_base_line.rotx((0,0,0), angle=45)

# Merge the two lines together to form a solid surface, and attach it to WGS
wing_base = wing_base_line.linspace(tip_airfoil.rotx((0,0,0), angle=45), num=2)
wgs.append_network("wingbase1", wing_base, boun_type=5)

# The same thing is repeated, but for the other wing
wing_base_line = tip_airfoil.copy()
wing_base_line = wing_base_line.replace(x=92.6, y=15.24, z=0.)
wing_base_line = wing_base_line.rotx((0,0,0), angle=-45)
wing_base = wing_base_line.linspace(tip_airfoil.rotx((0,0,0), angle=-45), num=2)
wgs.append_network("wingbase2", wing_base, boun_type=5)

'''
NOSE CONE
'''
# Function for the nose cone:
def g(x):
    rho = (R**2+L**2)/(2*R)

    return np.sqrt(rho**2-(L-x)**2)+R-rho

n_nose = 20  # number of points in the line
x_nose = np.linspace(0., L, num=n_nose)  # x-coordinates of the line
y_nose = g(x_nose)  # y-coordinates of the line
nose_line = wgs_creator.Line(np.zeros((n_nose, 3)))  # create an array of zeros
nose_line[:,0] = x_nose
nose_line[:,1] = y_nose

fbody_p1 = wgs_creator.Point(nose_line[-1])  # point at the end of the nose_line
fbody_p2 = fbody_p1.replace(x=86.84)
fbody_line = fbody_p1.linspace(fbody_p2, num=30)  # interpolate fbody_p1 and fbody_p2

nose_fbody_line = nose_line.concat(fbody_line)  # concatenate nose_line & fbody_line

nose_fbody_up = list()
for i in np.linspace(0, 90, 11):
    line = nose_fbody_line.rotx(rotcenter=nose_fbody_line[0], angle=i)
    nose_fbody_up.append(line)
nose_fbody_up = wgs_creator.Network(nose_fbody_up)

nose_fbody_low = list()
for i in np.linspace(-90, 0, 11):
    line = nose_fbody_line.rotx(rotcenter=nose_fbody_line[0], angle=i)
    nose_fbody_low.append(line)
nose_fbody_low = wgs_creator.Network(nose_fbody_low)

wgs.append_network("n_fb_up", nose_fbody_up, 1)
wgs.append_network("n_fb_low", nose_fbody_low, 1)

'''
PART WHERE WINGS ARE ATTACHED TO
'''

# AROUND WING 1

wingroot_up, wingroot_low = root_airfoil.split_half()
mbody_line = wingroot_up.replace(z=0.)

mbody_up = list()
for i in np.linspace(90, 45, 6)[:-1]:
    line = mbody_line.rotx((0,0,0), angle=i)
    mbody_up.append(line)
mbody_up.append(wingroot_up.rotx((0,0,0), angle=45))
mbody_up = wgs_creator.Network(mbody_up)
wgs.append_network("mbody_up", mbody_up, 1)

wingroot_low = wingroot_low.flip()
mbody_low = list()
mbody_low.append(wingroot_low.rotx((0,0,0), angle=45))
for i in np.linspace(45, 0, 6)[1:]:
    line = mbody_line.rotx((0,0,0), angle=i)
    mbody_low.append(line)
mbody_low = wgs_creator.Network(mbody_low)
wgs.append_network("mbody_low", mbody_low, 1)

#########################

# AROUND WING 2

wingroot_up, wingroot_low = root_airfoil.split_half()
mbody_line = wingroot_up.replace(z=0.)

mbody_up = list()
for i in np.linspace(0, -45, 6)[:-1]:
    line = mbody_line.rotx((0,0,0), angle=i)
    mbody_up.append(line)
mbody_up.append(wingroot_up.rotx((0,0,0), angle=-45))
mbody_up = wgs_creator.Network(mbody_up)
wgs.append_network("mbody_up2", mbody_up, 1)

wingroot_low = wingroot_low.flip()
mbody_low = list()
mbody_low.append(wingroot_low.rotx((0,0,0), angle=-45))
for i in np.linspace(-45, -90, 6)[1:]:
    line = mbody_line.rotx((0,0,0), angle=i)
    mbody_low.append(line)
mbody_low = wgs_creator.Network(mbody_low)
wgs.append_network("mbody_low2", mbody_low, 1)

##############################



'''
AFT BODY
'''
aft_body_p1 = wgs_creator.Point(root_airfoil[0])  # TE of the root airfoil
aft_body_p2 = aft_body_p1.shift((4.06, -0.01*R, 0.))
aft_body_line = aft_body_p1.linspace(aft_body_p2, num=5)

aft_body_up = list()
for i in np.linspace(0, 90, num=11):
    line = aft_body_line.rotx((0,0,0), angle=i)
    aft_body_up.append(line)
aft_body_up = wgs_creator.Network(aft_body_up)
wgs.append_network("abody_up", aft_body_up, 1)

aft_body_low = list()
for i in np.linspace(-90, 0, num=11):
    line = aft_body_line.rotx((0,0,0), angle=i)
    aft_body_low.append(line)
aft_body_low = wgs_creator.Network(aft_body_low)
wgs.append_network("abody_low", aft_body_low, 1)

'''
BODY BASE
'''
body_base_line_up = aft_body_up.edge(3)  # create a `Line` that corresponds to edge3 of the `Network` `body_base_up`
body_base_line_up = body_base_line_up.flip()  # the order of points are reversed
body_base_line_low = aft_body_low.edge(3)
body_base_line_low = body_base_line_low.flip()  
body_base_line = body_base_line_up.concat(body_base_line_low)
body_base_line2 = body_base_line.replace(102.33, y=0., z=0.)  # create a `Line` with 13 identical points (the center of the circle)
body_base = body_base_line.linspace(body_base_line2, num=3)
wgs.append_network("bodybase", body_base, boun_type=5)

'''
DEFINE WAKES
'''
wake_length = 11.43 * 50

wing_wake1 = wing1.make_wake(3, wake_length)
wgs.append_network("wingwake1", wing_wake1, 18)

wing_wake2 = wing2.make_wake(3, wake_length)
wgs.append_network("wingwake2", wing_wake2, 18)

body_base_wake_up = aft_body_up.make_wake(3, wake_length)
wgs.append_network("bbwake_up", body_base_wake_up, -18)

body_base_wake_low = aft_body_low.make_wake(3, wake_length)
wgs.append_network("bbwake_low", body_base_wake_low, -18)

# CREATE STL FILE
wgs.create_stl(include_wake=False) # to see the wakes, set this to True

# CREATE WGS FILE
wgs.create_wgs()

# CREATE AUX FILE
wgs.create_aux(alpha=3, mach=0.70, cbar=11.43, span=11.43, sref=8*101.613, xref=63.60, zref=0.)

print("done")