# Anti-Roll Ring For Round Appliances
#
# Are you scared that your favorite round trimmer, that is not
# manufactured any longer, will fall off the sink onto the floor and
# be shattered?
#
# I am. I have a nose trimmer Philips NT1150/10 that is a fantastic
# product! Close trim, still no risk to hurt myself.
#
# Unfortunately this product is not manufactured any longer and the
# replacement is a joke in comparison. And no other manufacturer has
# anything even close.
#
# After my previous one fell and shattered, I did manage to find one
# of the last ones sold. You press on this print and the trimmer
# making it triangular, i.e. will not that easily roll and fall down.
#
# To make this ring to be flexible, use TPU with 1 or 2 walls and
# 5-10% gyroid infill.
#
# As I'm a beginner trying to use Python and the "build123d" module
# to create this print, it is not even a good example of "build123d"
# usage, but maybe it demonstrates what can be done with such a
# package.
#
# This model is licensed under the MakerWorld Creative Commons
# Attribution-NonCommercial-Share-Alike
# https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Author: Kent Boortz <kent.boortz@gmail.com>

# pylint: disable=consider-using-f-string
# pylint: disable=consider-using-generator
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

# ======================================================================
# Imports
# ======================================================================

import os.path
from pathlib import Path

from build123d import *
from ocp_vscode import *

# ======================================================================
# Data
# ======================================================================

# https://www.reddit.com/r/mathematics/comments/18nwbrw/radius_of_a_circle_inscribed_in_a_triangle_my_own/

hole_diameter   = 26
side_length     = hole_diameter * 2.2
corner_rad      = side_length / 8
knurling_count  = 60
knurling_rad    = 0.9
knurling_depth  = 14

mask_side_len   = side_length + knurling_rad * 4
mask_chamfer    = 4
mask_corner_rad = corner_rad * 1.15

# ======================================================================
# Construct the part
# ======================================================================

# Could use rotation=degrees to get it more even distributed, but
# it should not be visible they are not.

# ----------------------------------------------------------------------
# Create the outer triangle
# ----------------------------------------------------------------------

face  = Triangle(a=side_length, b=side_length, c=side_length)
face  = fillet(face.vertices(), radius=corner_rad)
wire  = face.wire()

# ----------------------------------------------------------------------
# Create a mask from the outer triangle + a chamfer
# ----------------------------------------------------------------------

mask  = Triangle(a=mask_side_len, b=mask_side_len, c=mask_side_len)
mask  = fillet(mask.vertices(), radius=mask_corner_rad)
mask  = extrude(mask, amount=knurling_depth / 2, both=True)

e = [*mask.edges().group_by(Axis.Z)[0],
     *mask.edges().group_by(Axis.Z)[-1]]

mask  = chamfer(e, length=mask_chamfer)

# ----------------------------------------------------------------------
# Create the straight knurling
# ----------------------------------------------------------------------

for knurling_idx in range(0, knurling_count):
    face += Pos(wire@(knurling_idx / knurling_count)) * Circle(knurling_rad)

# As 3D printers are bad at printing in the air without support,
# we use a mask to get 45 degrees, something the printer can handle
# without support.
ring  = extrude(face, amount=knurling_depth / 2, both=True) & mask

# ----------------------------------------------------------------------
# Punch the hole
# ----------------------------------------------------------------------

face  = Circle(hole_diameter / 2)
ring -= extrude(face, amount=knurling_depth / 2, both=True)

# ----------------------------------------------------------------------
# Output the STEP and view the model
# ----------------------------------------------------------------------

script_path = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem
basepath = os.path.join(script_path, basename)
export_step(ring, os.path.join(script_path, basepath + ".step"))

show(ring)
