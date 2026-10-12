# TorkReda Wall Brackets
#
# In Sweden, in many appartments there is a TorkReda drying rack in the
# bathroom. The wall brackets are plastic and might break from age.
#
# You could buy a spare part, but what is the fun about that ;)
#
# As I wanted to print it in PETG, there are some modifications to make
# the model stronger. The walls are just a tiny bit thicker and some
# large fillets were added to the inside where it doesn't change the
# functionality.
#
# The 3mf file places the model on the plate with the wall side
# down. The settings used are
#
#   Base setting  : 0.20mm Strength
#   Walls         : Wall loops 99
#   Sparse infill : 100 %
#   Support       : tree(auto)
#   Brim type     : Outer brim only
#
# Author  : Kent Boortz <kent.boortz@gmail.com>
# License : Public Domain

# pylint: disable=consider-using-f-string
# pylint: disable=consider-using-generator
# pylint: disable=global-statement
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-statements
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

wall_plate_height     = 110
wall_plate_bot_width  = 42
wall_plate_top_width  = 32

front_plate_height    = 57
front_plate_bot_width = 36
front_plate_top_width = 31
front_plate_depth     = 86
front_plate_angle     = 12

thickness             = 4       # Original is 3.9

split_height          = 70

rest_rad              = 14.5 / 2
rest_center           = 18 - rest_rad # Where to create the hole

tilt_rad              = 7 / 2
tilt_center           = 6.2 - tilt_rad

slot_start            = 13
slot_rad              = 6.4 / 2
slot_length           = 41
hole_rad              = 16 / 2

dot_start             = 90
dot_rad               = 5 / 2
dot_depth             = 2.5

fillet_gen            = 0.6     # Generic, small fillet

# ======================================================================
# Create the wall plate and front plate faces, tilt the front plate,
# and loft() between them. Use a plane and split() to divide into two
# shapes, that we work on separately until joining them at the end.
# ======================================================================

# We create the half and then mirror it
wall_pts = [
    (0, -wall_plate_top_width / 2),
    (0, wall_plate_top_width / 2),
    (wall_plate_height, wall_plate_bot_width / 2),
    (wall_plate_height, -wall_plate_bot_width / 2),
    (0, -wall_plate_top_width / 2),
]

front_pts = [
    (0, -front_plate_top_width / 2),
    (0, front_plate_top_width / 2),
    (front_plate_height, front_plate_bot_width / 2),
    (front_plate_height, -front_plate_bot_width / 2),
    (0, -front_plate_top_width / 2),
]

in_wall_pts = [
    (thickness, -wall_plate_top_width / 2 + thickness),
    (thickness, wall_plate_top_width / 2 - thickness),
    (wall_plate_height, wall_plate_bot_width / 2 - thickness),
    (wall_plate_height, -wall_plate_bot_width / 2 + thickness),
    (thickness, -wall_plate_top_width / 2 + thickness),
]
in_front_pts = [
    (thickness, -front_plate_top_width / 2 + thickness),
    (thickness, front_plate_top_width / 2 - thickness),
    (front_plate_height, front_plate_bot_width / 2 - thickness),
    (front_plate_height, -front_plate_bot_width / 2 + thickness),
    (thickness, -front_plate_top_width / 2 + thickness),
]

wall_polygon  = Polyline(wall_pts)
front_polygon = Polyline(front_pts)
wall_face     = make_face(wall_polygon)
front_face    = make_face(front_polygon)

in_wall_polygon  = Polyline(in_wall_pts)
in_front_polygon = Polyline(in_front_pts)
in_wall_face     = make_face(in_wall_polygon)
in_front_face    = make_face(in_front_polygon)

front_face       = Location((0, 0, front_plate_depth),
                         (0, -front_plate_angle, 0)) * front_face

in_front_face    = Location((0, 0, front_plate_depth),
                         (0, -front_plate_angle, 0)) * in_front_face

part             = loft([wall_face, front_face])
in_part          = loft([in_wall_face, in_front_face])

# Split into two parts
plane            = Pos(Z=split_height) * Plane.XY
body_part        = split(part, plane, keep=Keep.BOTTOM)
hook_part        = split(part, plane)

in_body_part     = split(in_part, plane, keep=Keep.BOTTOM)
in_hook_part     = split(in_part, plane)

# Cut off the bottom and top of the cutout, as it thickness
plane            = Pos(Z=thickness) * Plane.XY
in_body_part     = split(in_body_part, plane)
plane            = Location((0, 0, front_plate_depth - thickness),
                         (0, -front_plate_angle, 0)) * Plane.XY
in_hook_part     = split(in_hook_part, plane, keep=Keep.BOTTOM)

# ======================================================================
# We fillet the body part, to get the rounded upper side, and cut out
# the inside
# ======================================================================

e1 = body_part.edges().group_by(Axis.X)[0][0]
e2 = body_part.edges().group_by(Axis.X)[0][2]
body_part  = fillet([e1, e2], radius=wall_plate_top_width / 2)

e  = in_body_part.edges().sort_by(Axis.X).group_by(Axis.X)[1:2]
in_body_part  = fillet(e, radius=wall_plate_top_width / 2 - thickness)

body_part -= in_body_part
hook_part -= in_hook_part

# ======================================================================
# Combine them
# ======================================================================

bracket = hook_part + body_part

# ======================================================================
# Work on the hook part
# ======================================================================

circle     = Location((rest_center, 0, split_height), (0, 0, 0)) * \
             Circle(rest_rad)
rect       = Location((0, 0, split_height - tilt_rad), (0, 0, 0)) * \
             Rectangle(rest_center, rest_rad * 2, align=(Align.MIN, Align.CENTER))
bracket   -= extrude(circle + rect, amount=50)

# ======================================================================
# Work on the hook part
# ======================================================================

circle     = Location((tilt_center, 0, split_height - tilt_rad), (0, 0, 0)) * \
             Rot(X=90) * Circle(tilt_rad)

rect       = Location((0, 0, split_height - tilt_rad), (0, 0, 0)) * \
             Rot(X=90) * \
             Rectangle(tilt_center, tilt_rad * 2,
                       align=(Align.MIN, Align.CENTER, Align.MIN))

bracket -= extrude(circle, amount=50, both=True) + \
           extrude(rect, amount=50, both=True)

# ======================================================================
# Create the slot for the screw
# ======================================================================

circle_top = Circle(slot_rad)
circle_bot = Circle(hole_rad)
rect       = Rectangle(slot_length - slot_rad - hole_rad, slot_rad * 2,
                       align=(Align.MIN, Align.CENTER))

slot       = Pos(X=slot_start + slot_rad) * circle_top + \
             Pos(X=slot_start + slot_length - hole_rad) * circle_bot + \
             Pos(X=slot_start + slot_rad) * rect

bracket   -= extrude(slot, amount=thickness)

# ======================================================================
# Fillet some on the inside for strength
# ======================================================================

bracket = fillet(bracket.edges().group_by(Axis.Z)[-5], radius=10)

e1 = bracket.edges().group_by(Axis.Z)[2].group_by(Axis.Y)[0]
e2 = bracket.edges().group_by(Axis.Z)[2].group_by(Axis.Y)[-1]

bracket = fillet([e1, e2], radius=5.5)

# Could not figure out how to do this...
#bracket    = fillet(bracket.edges(), radius=fillet_gen)

# ======================================================================
# Create the small hole that I assume is for preventing the holder
# from rotating in some rare setups where there is something on the
# wall that will go into it
# ======================================================================

dot        = Pos(X=dot_start + dot_rad) * Circle(dot_rad)
bracket   -= extrude(dot, amount=dot_depth)

# ======================================================================
# Create the STEP file
# ======================================================================

show(bracket)

script_dir    = os.path.dirname(os.path.realpath(__file__))
basename      = Path(__file__).stem
export_step(bracket, os.path.join(script_dir, f"{basename}.step"))
