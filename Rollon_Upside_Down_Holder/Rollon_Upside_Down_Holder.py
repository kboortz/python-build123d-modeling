# This is a holder for Ldb roll-on deoderant/antiperspirant. When
# there is little left in the bottle, this holder is used to keep the
# roll-on upside-down to be able to use the last of it before throwing
# it away.
#
# By modifying 'cutout_diameter' and other variables below, this can
# be made to fit other brands as well.
#
# This is my first use of "build123d", it is nothing fancy :)
#
# Author: Kent Boortz <kent.boortz@gmail.com>

import os

from build123d import *
from ocp_vscode import *

cutout_diameter   = 47.5  # Cut out diameter to fit the rollon
cylinder_diameter = 55    # Base cylinder diameter
cylinder_height   = 45    # Base cylinder height
bottom_thickness  = 1.5   # Thinkness between cutout and bottom

cutout_radius     = cutout_diameter / 2
cylinder_radius   = cylinder_diameter / 2

base   = Cylinder(cylinder_radius, cylinder_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
pos    = Pos(0, 0, cutout_radius + bottom_thickness)
circle = pos * Sphere(cutout_radius)
tube   = pos * Cylinder(cutout_radius, cylinder_height, align=(Align.CENTER, Align.CENTER, Align.MIN))

holder = base - circle - tube

script_path = os.path.dirname(os.path.realpath(__file__))

export_stl(holder, os.path.join(script_path, "rollon_upside_down_holder.stl"))

show(holder)
