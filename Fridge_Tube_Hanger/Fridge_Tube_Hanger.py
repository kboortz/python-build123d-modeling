# Fridge Tube Hanger (using IKEA ALFTA double-sided tape refill)
#
# There are excellent models out there already. The ones I used falls
# down now and then, seems that the 24x24 mm self-adhesive pads I use
# can't hold it up. So I'm designing my own hangers that are to use
# IKEA ALFTA double-sided tape refill, in hope that this will work
# better. These tapes are made to be easy to remove.
#
# For ALFTA the back plate should be 24x70 mm, but extending it to
# 25x72 to be able to use two or three Biltema 86-2055 fastening pads.
#
# You can see how to use the ALFTA pads in the assembly instructions
#
#   https://www.ikea.com/se/en/assembly_instructions/alfta-adhesive-hook-for-frame-white__AA-2204434-2-2.pdf
#
# Likely best printed with the wall side against a textured PEI plate,
# to get better grip. Alternatively fuzzy skin can be used on the wall
# side.
#
# While not a remix, I have taken inspiration and some measurements
# from this nice print
#
#   https://makerworld.com/en/models/1213086-tubehanger-refrigerator
#
# I output a STEP file instead of STL. The STEP file preserves the
# geometric data, while using STL means the build123d package has to
# use the geometric data to create a mesh model. Using STEP means we
# let the slicer deal with whatever conversion is needed and this
# "might" produce better prints.
#
# I'm using the Python module "build123d" to create this model. I'm a
# beginner trying to use this module and this means this code is not a
# good example of "build123d" usage. But maybe it demonstrates what
# can be done with such a package.
#
# While all bad coding is mine, I did get this working from help by
# members in the build123d channel on the Discord CadQuery server.
#
# Author  : Kent Boortz
# License : Public Domain
#
# pylint: disable=consider-using-f-string
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
# Measurements
# ----------------------------------------------------------------------

opening_diameter  = 17.3
opening_offset    = 30
rest_diameter     = 24
opening_thickness = 2.6
opening_margin    = 4           # Space to width
outer_diameter    = rest_diameter + opening_margin * 2

back_width        = 25          # 24 is enough for ALFTA
back_height       = 72          # 70 is enough for ALFTA
back_thickness    = 3
back_offset       = 15

holder_base_width = back_width  # Where meeting the back
holder_depth      = 45
holder_thickness  = 7

smooth_rad        = 1
back_corner_rad   = 2
connection_rad    = 6

# ----------------------------------------------------------------------
# We will create three parts, as we have problems with fillet()
# failing when a bit more complicated. So we create the parts one by
# one, including smoothing using fillet with small radius. Then we
# put them together.
#
# First create the back part
# ----------------------------------------------------------------------

back = Plane.YZ * \
       Pos(0, -back_offset, 0) * \
       RectangleRounded(back_width, back_height, radius=back_corner_rad)

# Round the backplate four corners a bit
back = extrude(back, amount=-back_thickness)

# Smooth the side opposite the wall
back = fillet(back.edges().group_by(Axis.X)[-1], radius=smooth_rad)

# ----------------------------------------------------------------------
# Create the base holder part
# ----------------------------------------------------------------------

l1     = CenterArc((opening_offset, 0), outer_diameter / 2, 0, 100)
l2     = Polyline(l1 @ 1, (0, holder_base_width / 2), (0, 0))
w1     = l1 + l2
w2     = mirror(w1, Plane.XZ)
face   = make_face(w1 + w2)
holder = extrude(face, amount=holder_thickness)

# ----------------------------------------------------------------------
# Cut out into the holder part
# ----------------------------------------------------------------------

opening = Pos(opening_offset, 0, 0) * Circle(opening_diameter / 2)
opening = extrude(opening, amount=holder_thickness)
rest    = Pos(opening_offset, 0, opening_thickness) * Circle(rest_diameter / 2)
rest    = extrude(rest, amount=holder_thickness - opening_thickness)

slot    = Pos(opening_offset + opening_diameter / 2, 0, 0) * \
          Rectangle(opening_diameter, opening_diameter)
slot    = extrude(slot, amount=holder_thickness)

holder -= rest + opening + slot

# Smooth the holder
holder = fillet(holder.edges().group_by(Axis.X)[1:], radius=smooth_rad)

# ----------------------------------------------------------------------
# Create a connecting part. If fillet() was not so sensitive and complex,
# a simple fillet with radius=6 would have been the best solution. But
# now we fake this fillet connection as a separate part.
# ----------------------------------------------------------------------

fu = CenterArc((connection_rad, connection_rad + holder_thickness),
               connection_rad, 180, 90)
fd = CenterArc((connection_rad, -connection_rad),
               connection_rad, 90, 90)
c1 = Polyline(fu @ 0, fd @ 1)
c2 = Polyline(fu @ 1, fd @ 0)
face = make_face(fu + fd + c1 + c2)
conn = Plane.XZ * extrude(face, amount=holder_base_width / 2, both=True)
conn = fillet(conn.edges().group_by(Axis.X)[1:], radius=smooth_rad)

# ----------------------------------------------------------------------
# Put it together
# ----------------------------------------------------------------------

model = back + holder + conn

# ----------------------------------------------------------------------
# Output the STEP and view the model
# ----------------------------------------------------------------------

script_path = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem
basepath = os.path.join(script_path, basename)
export_step(model, os.path.join(script_path, basepath + ".step"))

show(model)
