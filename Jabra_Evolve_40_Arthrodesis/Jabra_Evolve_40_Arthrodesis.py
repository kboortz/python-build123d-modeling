# Jabra Evolve 40 UC Stereo Headset Arthrodesis
#
# Frequently my Jabra Evolve 40 breaks just where the ear cup connects
# to the slider. The spot where it breaks is very hard to repar or
# glue, so as a last resort I have created a 3D-model to fixate the
# ear cup to the glider. An unfortunate side effect is that the ear
# cup can't be rotated, but that is not a big loss.
#
# As I'm a beginner trying to use Python and the "build123d" module
# to create this print, it is not even a good example of "build123d"
# usage, but maybe it demonstrates what can be done with such a
# package.
#
# This is one of my first uses of "build123d", i.e. nothing fancy :)
#
# This model is licensed under the MakerWorld Creative Commons
# Attribution-NonCommercial-Share-Alike
# https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Author: Kent Boortz <kent.boortz@gmail.com>

# pylint: disable=consider-using-f-string
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

# ======================================================================
# Illustrative ascii drawing
# ======================================================================
#
# Note that how I name things might be incorrect, English is not my
# native language. This is also reflected in how I name the variables.
#
#                   58.5 mm             8.6 mm
#      +------------------------------+ /
#      |                              |--+
# 9 mm |                              |  | 8.6 mm (width 17.6)
#      |                              |--+
#       \                            /
#   9 mm \                          /
#         +------------------------+
#                   46 mm

import sys
import os.path
from time import sleep
from pathlib import Path

from build123d import *
from ocp_vscode import *

# ----------------------------------------------------------------------
# Measurements
# ----------------------------------------------------------------------

cup_outer_diameter    = 47      # 46, but we need some space
cup_inner_diameter    = 59.5    # 58.5, but we need some space
cup_outer_height      = 9
cup_inner_height      = 10
cup_inner_lip         = 1.5     # Small grab around cup
cup_thickness         = 0.5

slider_hold_height    = 8.8
slider_hold_depth     = 8.8
slider_hold_width     = 17.7
slider_hold_offset    = 0
slider_hold_thickness = 1
slider_hold_insert    = 5       # Temporary push into cup
slider_hold_adjust    = 2.5     # FIXME should not be needed...

slider_beam_width     = 8.5
slider_beam_thickness = 3

# ----------------------------------------------------------------------
# Calculated measurements
# ----------------------------------------------------------------------

cup_outer_radius   = cup_outer_diameter / 2
cup_inner_radius   = cup_inner_diameter / 2

cup_height         = cup_outer_height + cup_inner_height

slider_beam_height = \
    (slider_hold_height + slider_beam_thickness) / 2 \
    + slider_beam_thickness
slider_beam_length = cup_inner_diameter + slider_hold_depth + 20

# ----------------------------------------------------------------------
# Debug function
# ----------------------------------------------------------------------

# Debug function, to view the face index numbers in preview. Note that
# this function adding text will cause the faces to be renumbered, so
# we show and exit to view what the real face numbers will be.
def engrave_face_numbers(part_arg, axis=Axis.Z):
    fontsz, fontht = 15.0, 1.0
    for idx, one_face in enumerate(part_arg.faces().sort_by(axis)):
        try:
            # Might be circular face, can't create plane
            sk = Plane(one_face) * Text(str(idx), font_size=fontsz)
            part_arg += extrude(sk, amount=fontht)
        # pylint: disable-next=broad-exception-caught
        except Exception as e:
            print("WARNING: could not engrave face %d (%s)" % (idx, e))

    show(part_arg)
    sys.exit(0)

# ----------------------------------------------------------------------
# Construct ear cup holder part
# ----------------------------------------------------------------------

pts_cup = [
    (0, 0),
    (cup_outer_radius + cup_thickness, 0),
    (cup_inner_radius + cup_thickness, cup_outer_height),
    (cup_inner_radius + cup_thickness, cup_height + cup_thickness + cup_inner_lip),
    (cup_inner_radius - cup_inner_lip, cup_height + cup_thickness + cup_inner_lip),
    (cup_inner_radius, cup_height),
    (cup_inner_radius, cup_inner_height),
    (cup_outer_radius, cup_thickness),
    (0, cup_thickness),
]

cup_profile   = Polyline(pts_cup)
cross_section = make_face(Plane.YZ * cup_profile)

cup_hold = revolve(cross_section, axis=Axis.Z)

# ----------------------------------------------------------------------
# Construct slider hold part
# ----------------------------------------------------------------------

slider_hold = Box(slider_hold_depth + slider_hold_insert,
                  slider_hold_width, slider_hold_height)

slider_hold = Pos(cup_inner_radius \
                  + slider_hold_depth / 2 \
                  - slider_hold_insert \
                  + slider_hold_adjust,
                  0,
                  cup_height - slider_hold_offset - slider_hold_height / 2) * \
                  slider_hold

cup_hold    -= slider_hold
slider_hold -= Cylinder(cup_inner_radius, cup_height,
                        align=(Align.CENTER, Align.CENTER, Align.MIN))

# Cut out where to insert the slider hold
slider_hold = offset(slider_hold, amount=slider_hold_thickness,
                     openings=slider_hold.faces()[4])

model = cup_hold + slider_hold

# ----------------------------------------------------------------------
# Cut out so can mount it
# ----------------------------------------------------------------------

cutout = Box(slider_beam_length, slider_beam_width, slider_beam_height)
cutout = Pos(slider_beam_length / 2,
             0,
             cup_height \
             + slider_beam_height / 2 \
             - slider_hold_offset \
             - slider_hold_height / 2 \
             - slider_beam_thickness / 2) * \
             cutout

model -= cutout

# ----------------------------------------------------------------------
# Output the STL and view the model
# ----------------------------------------------------------------------

script_path = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem
basepath = os.path.join(script_path, basename)
export_stl(model, os.path.join(script_path, basepath + ".stl"))

show(model)
