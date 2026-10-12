# Airthings View Plus Stand
#
# This is a supporting stand trying to solve the problem that View
# Plus frequently falls over from light touch. This is problemantic if
# you have it on the bedside table and reach for anything on it during
# the night.
#
# This model is open in the bottom enabling the device to stand on the
# rubber feet as intended, yet have some extra support on the sides.
#
# As I'm a beginner trying to use Python and the "build123d" module
# to create this print, it is not even a good example of "build123d"
# usage. But maybe it demonstrates what can be done with such a
# package.
#
# This model is licensed under the MakerWorld Creative Commons
# Attribution-NonCommercial-Share-Alike
# https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Author: Kent Boortz <kent.boortz@gmail.com>

# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

import os.path
from pathlib import Path

from build123d import *
from ocp_vscode import *

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------

# Size of the device, approximate, as it is rounded in all dimensions,
# the numbers used are from trail and error
viewplus_depth  = 32.5
viewplus_height = 91
viewplus_width  = 167
viewplus_slope  = 5                   # According to iPhone Measure tool
viewplus_radius = viewplus_height / 2 # Radius of the side half circles

# Size of the plate
plate_width     = 130
plate_depth     = 70
plate_height    = 3             # Bottom plate

support_width   = 110
support_degrees = 55            # How high up we go
support_walls   = 1.4

# ----------------------------------------------------------------------
# Cut off all that is below the plate to make bottom open
# ----------------------------------------------------------------------

cutoff = Box(plate_width, plate_depth, 20, rotation=(180, 0, 0),
             align=(Align.CENTER, Align.CENTER, Align.MIN))

# ----------------------------------------------------------------------
# Construct the plate part
# ----------------------------------------------------------------------

plate = Box(plate_width, plate_depth, plate_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
plate = fillet(plate.edges().filter_by(Axis.Z), radius=10)
plate = fillet(plate.edges().group_by(Axis.Z)[-1], radius=2)

# ----------------------------------------------------------------------
# Construct the support part
# ----------------------------------------------------------------------

center_offset = viewplus_width / 2 - viewplus_radius

l1 = CenterArc((-center_offset, viewplus_radius),
               viewplus_radius, -90, -support_degrees)
l2 = CenterArc((center_offset,  viewplus_radius),
               viewplus_radius, -90, +support_degrees)
l3 = Line(l1 @ 0, l2 @ 0)
l4 = Line(l1 @ 1, l2 @ 1)

support       = Plane.XZ * make_face([l1, l2, l3, l4])
support       = extrude(support, amount=viewplus_depth / 2, both=True)

# We want to rotate from the side of the support, so we create
# a new axis on that side and rotate using the method rotate().
axis          = Axis((0, viewplus_depth, 0), (1,0,0))
support       = support.rotate(axis, 5)

support_solid = support         # Save for later before making hollow
support       = offset(support, amount=support_walls,
                       openings=support.faces().sort_by().last)

# ----------------------------------------------------------------------
# Finish up by cutting out the support part in the plate, to make
# a hole in the plate so the device stands on itself. And add it
# back to form the part holding the device. And finally, cut off
# parts that sticks out under the plate.
# ----------------------------------------------------------------------

model = plate - support_solid + support - cutoff

# ----------------------------------------------------------------------
# Output the STL and view the model
# ----------------------------------------------------------------------

script_path = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem
basepath = os.path.join(script_path, basename)
export_stl(model, os.path.join(script_path, basepath + ".stl"))

show(model)
