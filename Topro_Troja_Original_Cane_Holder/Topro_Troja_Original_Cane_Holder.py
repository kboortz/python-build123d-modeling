# Topro Troja Rolling Walker 19 mm Cane Holder
#
# This is a holder for a cane with 19 mm diameter to be attached to
# a "Troja Original" rolling walker. It is a snap-in tight fit so I
# don't think this model works for other cane diameters. I did notice
# that one telescopic cane that was maybe 21 mm worked as the part a
# bit down that attached to the holder was still 19 mm.
#
# There is a right hand and a left hand version on different plates.
#
# Topro rolling walkers have different connectors to mount canes.
# Even two walkers named the same might have different connecors,
# because the manufacturer has modified the model without changing
# the model name. This cane holder is for "Troja Original" where
# the same kind of connector is used on the upper and lower slide.
#
# This is snap-on, no screws required. Preferably printed in PETG
# or other filament that can be used outdoors.
#
# I used the auto setting for tree support. When placing the model
# STEP # files on  the plate, I had to use the “Lay on Face” feature
# to force the cup's bottom to lay down onto the plate.
#
# I used the 0.20mm Strength setting and Gyroid infill, but I
# really think the default setting would have work equally well.
#
# This module was created using Python and the "build123d" module.

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

import os
from os.path import join
from pathlib import Path

from build123d import *
from ocp_vscode import *


# ======================================================================
# Data
# ======================================================================

# The dimensions for the slot on the part we are to mount.
insert_outer_width  = 10.5      # Really 9.9
insert_inner_width  = 5         # Really 3.8
#insert_full_length  = 62        # Not used

insert_length       = 59        # Active slot length
insert_curve_rad    = 10
lower_insert_length = insert_length - 2 # No idea why

insert_inner_height = 4.5       # The narrow part (becomes smaller, need larger?)
insert_hat_height   = 7.0       # + "hat" without curve
insert_curve_height = 8.5       # + "hat" with curve

# The side of the mount piece is formed arount the plastic around the
# aluminum profile. We create the profiles to use it to cut out what
# we need removed. Might not be a true oval.

frame_rad_x       = 53 / 2
frame_rad_y       = 31 / 2

hook_radius       = 18 / 2      # For inner diameter 19
hook_lip_radius   = 23
#hook_opening     = 15          # For 19 to 21 mm canes
hook_height       = 30
hook_flat_length  = 35
hook_thickness    = 2.8         # 2 was too flexible in PETG
hook_tilt         = 13          # Degrees

cup_rad           = 35 / 2      # 30 - 35 mm
cup_expand        = 1.5         # Upper part is bigger
cup_height        = 35
cup_wall          = 3
cup_tilt          = 14          # Degrees
cup_fillet        = cup_wall / 2

# The actual main part

height            = insert_length
depth             = 18
width             = frame_rad_y * 2
fillet_rad        = 2.8

script_dir = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem


######################################################################
# Create the two ecliptic parts to use for cutouts later
######################################################################

frame_obj = EllipticalCenterArc(
    center=(-frame_rad_x, 0),
    x_radius=frame_rad_x,
    y_radius=frame_rad_y,
    arc_size=360,
)

frame_face = make_face(frame_obj)


######################################################################
# Create the profile to cut out the slot
######################################################################

slot_lines = Curve() + [
    Line((0, 0), (insert_curve_height, 0)),
    RadiusArc((insert_curve_height, 0),
              (insert_hat_height, insert_outer_width / 2),
              -insert_curve_rad),
    Line((insert_hat_height, insert_outer_width / 2),
         (insert_inner_height, insert_outer_width / 2)),
    Line((insert_inner_height, insert_outer_width / 2),
         (insert_inner_height, insert_inner_width / 2)),
    Line((insert_inner_height, insert_inner_width / 2),
         (0, insert_inner_width / 2)),
    Line((0, insert_inner_width / 2),
         (0, 0)),
]

slot_face = make_face(slot_lines)
slot_face = slot_face + mirror(slot_face, about=Plane.XZ)


######################################################################
# Create the hook
######################################################################

p1 = CenterArc((hook_flat_length, -hook_radius),
               hook_radius,
               90,
               -195)
p2 = TangentArc([p1@1, (0, -hook_lip_radius)], tangent=p1%1)

hook_inner_wire = Curve() + [
    Line((0, 0), (hook_flat_length, 0)),
    p1,
    p2,
]

# We create an outer wire and connect the inner and outer

hook_outer_wire = hook_inner_wire.offset_2d(hook_thickness,
                                            side=Side.LEFT,
                                            closed=False)

hook_outline = [
    hook_outer_wire,
    hook_inner_wire,
    Line(hook_outer_wire@1, hook_inner_wire@0),
    Line(hook_outer_wire@0, hook_inner_wire@1),
]

hook_face = make_face(hook_outline)
hook      = extrude(hook_face, amount=hook_height)

e = hook.edges().sort_by(Axis.X)[5:7]
hook = fillet(e, radius=6)

hook = fillet(hook.edges(), radius=0.6)


######################################################################
# Create the cup
######################################################################

# We work with outer diameters
cup_outer_rad    = cup_rad + cup_wall
cup_outer_height = cup_height + cup_wall

# Start: Code from Roger Maitland (minimal modifications)
cup_outside   = Polyline((0, 0),
                         (cup_outer_rad, 0),
                         (cup_outer_rad * cup_expand, cup_outer_height))
cup_perimeter = offset(cup_outside, cup_wall,
                       side=Side.LEFT, kind=Kind.INTERSECTION)
cup_perimeter = fillet(cup_perimeter.vertices().sort_by(Axis.Y)[-2:],
                       cup_fillet)
cup_perimeter = fillet(cup_perimeter.vertices().sort_by(Axis.X)[2],
                       cup_fillet)
cup_profile   = Plane.XZ * make_face(cup_perimeter)
cup           = revolve(cup_profile, Axis.Z)
# End: Code from Roger Maitland
cup           = Location((10, 50, -20), (0, -cup_tilt, 0)) * cup

# We create a solid version with extended cylinder at top, to cut out
# defects later
cup_inside    = Polyline((0, cup_wall),
                         (cup_rad, cup_wall),
                         (cup_rad * cup_expand, cup_height),
                         (cup_rad * cup_expand, cup_height * 4),
                         (0, cup_height * 4),
                         (0, cup_wall))
cup_profile   = Plane.XZ * make_face(cup_inside)
cup_solid     = revolve(cup_profile, Axis.Z)
cup_solid     = Location((10, 50, -20), (0, -cup_tilt, 0)) * cup_solid


######################################################################
# Cut out and add hook to the upper part
######################################################################

main_face = Rectangle(depth, width,
                      align=(Align.MIN, Align.CENTER))

face = main_face - \
       Pos(8) * frame_face - \
       Pos(5) * slot_face

part_upper  = extrude(face, amount=insert_length)
part_upper += Location((0, -(width / 2), 29),
                       (0, hook_tilt, 0)) * hook

# Cut out a coner of the hook
part_upper -= Pos(-depth) * \
              extrude(main_face, amount=insert_length)


######################################################################
# Cut out and add a cup to the lower part
######################################################################

width_lower = width - 2

main_face = Pos(Y=-2) * Rectangle(depth, width_lower,
                               align=(Align.MIN, Align.CENTER))

face       = main_face - \
             Pos(7) * frame_face - \
             Pos(5) * slot_face

part_lower = extrude(face, amount=lower_insert_length)

# Connect to the cup

face_part  = part_lower.faces().sort_by(Axis.Y).last

# FIXME this is a work-around. If removing the Pos(Z=0.001), then
# the cup just disappears. The commented out line will not show
# the cup itself, with Pos(Z=0.001) it will ;)
#face_cup   = Pos(Z=0) * cup.faces().sort_by(Axis.Z)[1]
face_cup   = Pos(Z=0.001) * cup.faces().sort_by(Axis.Z)[1]

part_lower += loft([face_part, face_cup])
part_lower += cup
part_lower -= cup_solid

# Punch some holes to let water out
plane       = Plane(part_lower.faces().sort_by()[0])
part_lower -= plane * \
              PolarLocations(radius=cup_rad - 3, count=10) * \
              Cylinder(3, 10)


######################################################################
# Smooth some edges
######################################################################

r = ShapeList([
    part_upper.edges().sort_by(Axis.Y).filter_by(Axis.Z)[-1],
    part_upper.edges().sort_by(Axis.Y).filter_by(Axis.Z)[-2],
    part_upper.edges().sort_by(Axis.Y).filter_by(Axis.Z)[-14],
    part_upper.edges().sort_by(Axis.Y).filter_by(Axis.Z)[-17],
])
part_upper = fillet(r, radius=fillet_rad)

r = ShapeList([
    part_lower.edges().sort_by(Axis.Y).filter_by(Axis.Z)[0],
    part_lower.edges().sort_by(Axis.Y).filter_by(Axis.Z)[1],
])
part_lower = fillet(r, radius=fillet_rad)

r = part_upper.faces().filter_by(Axis.Z).edges()
part_upper = fillet(r, radius=0.6)

r = part_lower.faces().filter_by(Axis.Z).edges()
part_lower = fillet(r, radius=0.6)


######################################################################
# View and save as a STEP file
######################################################################

show(part_upper + Pos(75) * part_lower)

#export_step(part_upper, join(script_dir, basename + "_Hook.step"))
#export_step(part_lower, join(script_dir, basename + "_Cup.step"))
export_stl(part_upper, join(script_dir, basename + "_Hook.stl"))
export_stl(part_lower, join(script_dir, basename + "_Cup.stl"))
