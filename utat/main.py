import numpy as np
from pyPanair.preprocess import wgs_creator
wgs = wgs_creator.LaWGS("main")

# Nose cone data
L = 19.05
R = 3.81

# Control Panel... get it?
wing_panels = 40
wing_tip_panels = 5
tip_nose_cone_panels = 20 # only relevant if
nose_cone_panels = 40
body_panels = 30
aft_body_panels = 15
base_panels = 9

'''
AIRFOIL
'''
# Creates the base of the airfoil
root_airfoil = wgs_creator.read_airfoil("real_base_airfoil_detailed.csv", y_coordinate=R, expansion_ratio=1)
root_airfoil = root_airfoil.shift((86.84, 0., 0.))

# Creates the tip of the airfoil
tip_airfoil = wgs_creator.read_airfoil("real_tip_airfoil_detailed.csv", y_coordinate=R, expansion_ratio=1)
tip_airfoil = tip_airfoil.shift((89.38, 11.43, 0.))

# Connect the base and the tip to create two wings, then rotate them clockwise / counterclockwise
wing1 = root_airfoil.linspace(tip_airfoil, num=wing_panels)

wing1 = wing1.rotx((0,0,0), angle=45)

wing2 = root_airfoil.linspace(tip_airfoil, num=wing_panels)
wing2 = wing2.rotx((0,0,0), angle=-45)

# Add wings to WGS
wgs.append_network("wing1", wing1, 1)
wgs.append_network("wing2", wing2, 1)

'''
FILL IN WING TOP
'''
wingtip_upper, wingtip_lower = tip_airfoil.rotx((0,0,0), angle=45).split_half()
wingtip_lower = wingtip_lower.flip()
wingtip = wingtip_upper.linspace(wingtip_lower, num = wing_tip_panels)
wgs.append_network("wingbase1", wingtip, 1)

wingtip_upper, wingtip_lower = tip_airfoil.rotx((0,0,0), angle=-45).split_half()
wingtip_lower = wingtip_lower.flip()
wingtip = wingtip_upper.linspace(wingtip_lower, num = wing_tip_panels)
wgs.append_network("wingbase2", wingtip, 1)
'''
NOSE CONE
'''
# Function for the nose cone:
def g(x):
    rho = (R**2+L**2)/(2*R)

    return np.sqrt(rho**2-(L-x)**2)+R-rho

def get_xa():
    rho = (R**2+L**2)/(2*R)
    x_0 = L - np.sqrt((rho-r_n)**2-(rho-R)**2)
    y_t = r_n*(rho-R)/(rho-r_n)
    x_t = x_0 - np.sqrt(r_n**2 - y_t**2)
    x_a = x_0 - r_n
    return x_a, x_t

def blunted_tip(x):
    rho = (R**2+L**2)/(2*R)
    x_0 = L - np.sqrt((rho-r_n)**2-(rho-R)**2)
    y_t = r_n*(rho-R)/(rho-r_n)
    x_t = x_0 - np.sqrt(r_n**2 - y_t**2)
    return np.sqrt(r_n**2-(x_0-x)**2)

def blunted_cone(x):
    global x_a

    r_n = 1
    rho = (R**2+L**2)/(2*R)
    x_0 = L - np.sqrt((rho-r_n)**2-(rho-R)**2)
    y_t = r_n*(rho-R)/(rho-r_n)
    x_t = x_0 - np.sqrt(r_n**2 - y_t**2)
    x_a = x_0 - r_n


    return np.sqrt(rho**2-(L-x)**2)+R-rho
'''
# FOLLOWING LINES ARE FOR NORMAL TIP
'''
x_nose = np.linspace(0., L, num=nose_cone_panels)  # x-coordinates of the line
y_nose = g(x_nose)  # y-coordinates of the line
nose_line = wgs_creator.Line(np.zeros((nose_cone_panels, 3)))  # create an array of zeros
nose_line[:,0] = x_nose
nose_line[:,1] = y_nose

fbody_p1 = wgs_creator.Point(nose_line[-1])  # point at the end of the nose_line
fbody_p2 = fbody_p1.replace(x=86.84)
fbody_line = fbody_p1.linspace(fbody_p2, num=body_panels)  # interpolate fbody_p1 and fbody_p2

nose_fbody_line = nose_line.concat(fbody_line)  # concatenate nose_line & fbody_line
'''
# FOLLOWING LINES ARE FOR BLUNTED TIP

r_n = 0.2
x_a, x_t = get_xa()

x_tip = np.linspace(x_a, x_t, num=tip_nose_cone_panels)
y_tip = np.array([blunted_tip(x) for x in x_tip])
tip_line = wgs_creator.Line(np.zeros((tip_nose_cone_panels, 3)))  # create an array of zeros
tip_line[:,0] = x_tip
tip_line[:,1] = y_tip

x_nose = np.linspace(x_t, L, num=nose_cone_panels)  # x-coordinates of the line
y_nose = blunted_cone(x_nose)  # y-coordinates of the line

nose_line = wgs_creator.Line(np.zeros((nose_cone_panels, 3)))  # create an array of zeros
nose_line[:,0] = x_nose
nose_line[:,1] = y_nose

fbody_p1 = wgs_creator.Point(nose_line[-1])  # point at the end of the nose_line
fbody_p2 = fbody_p1.replace(x=86.84)
fbody_line = fbody_p1.linspace(fbody_p2, num=body_panels)  # interpolate fbody_p1 and fbody_p2

tip_nose_line = tip_line.concat(nose_line)  # concatenate nose_line & fbody_line
nose_fbody_line = tip_nose_line.concat(fbody_line)  # concatenate nose_line & fbody_line
'''

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
# PART WHERE WINGS ARE ATTACHED TO
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
aft_body_line = aft_body_p1.linspace(aft_body_p2, num=aft_body_panels)

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
body_base = body_base_line.linspace(body_base_line2, num=base_panels)
wgs.append_network("bodybase", body_base, boun_type=5)

'''
DEFINE WAKES
'''
wake_length = 100 + 11.43 * 50

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
wgs.create_wgs(roll=0)

# CREATE AUX FILE
wgs.create_aux(alpha=2.47, mach=1.60, cbar=9.9, span=30.48, sref=48.315, xref=63.60, zref=0.)

print("done")