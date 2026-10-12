# Oversized Double Cable Clip for Baseboards
#
# Special cable clip for a typical extension cord and network cable.
# The cable diameters are to be 8.0 and 6.0 mm. The part you stick in
# behind the baseboard is oversized. This is to be used when the gap
# between the wall and the baseboard is a bit larger than usual.
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
from time import sleep
from pathlib import Path

from build123d import *
from ocp_vscode import *


# ======================================================================
# Data
# ======================================================================

clip_width            = 10
clip_thickness        = 1.5

# Clips numbered from floor side and up
clip1_dia             = 8.0
clip2_dia             = 6.0
clip1_rad             = clip1_dia / 2
clip2_rad             = clip2_dia / 2
clip1_opening         = clip1_dia * 0.85
clip2_opening         = clip2_dia * 0.85

backplate_width       = 25
backplate_height      = 30

# Most other models use around 0.5 between board and wall
backplate_thicknesses = [
    (1.5, 2),
    (1.0, 1),
    (0.6, 1)
]
backplate_offset      = 3         # Between clip and backplate

backplate_fillet      = 1.5
common_fillet         = 0.5
connect_fillet        = 2

backplate_align       = (Align.CENTER, Align.MIN, Align.CENTER)
clip_align            = (Align.MIN, Align.MIN, Align.CENTER)

script_dir            = os.path.dirname(os.path.realpath(__file__))


######################################################################
# Create the holes for the hooks
######################################################################

# We create a box where we cut out the two slots for the cables
box_height   = clip1_dia + clip2_dia + clip_thickness * 3
box_depth    = clip1_dia + clip_thickness

clip_face    = Pos(backplate_height + backplate_offset) * \
               Plane.YZ * \
               Rectangle(box_height, box_depth, align=clip_align)

clip1_height = backplate_height + backplate_offset + clip_thickness
clip2_height = clip1_height + clip1_dia + clip_thickness

clip_face    = fillet(clip_face.vertices().sort_by(Axis.Z)[-2:], radius=clip1_rad)

clip1_face   = Pos(clip1_height) * Plane.YZ * \
               Circle(clip1_rad, align=clip_align)
clip2_face   = Pos(clip2_height) * Plane.YZ * \
               Circle(clip2_rad, align=clip_align)
clip_face   -= clip1_face
clip_face   -= clip2_face


######################################################################
# Cut from the back to the holes, to create hooks
######################################################################

cut1_face  = Pos(clip1_face.center().Y) * \
             Plane.YZ * \
             Rectangle(clip1_opening, clip1_dia)
cut2_face  = Pos(clip2_face.center().Y) * \
             Plane.YZ * \
             Rectangle(clip2_opening, clip1_dia)
clip_face -= cut1_face
clip_face -= cut2_face

clip_hook  = extrude(clip_face, amount=clip_width / 2, both=True)


######################################################################
# Create models with different backplate thickness
######################################################################

for backplate_thickness, fillet_idx in backplate_thicknesses:

    bp_face   = Rectangle(backplate_width, backplate_height,
                          align=backplate_align) + \
                Pos(0, backplate_height) * \
                Rectangle(clip_width, backplate_offset,
                          align=backplate_align)

    bp_face   = fillet(bp_face.vertices().sort_by(Axis.Y)[0:-2],
                       radius=backplate_fillet)
    backplate = extrude(bp_face, amount=backplate_thickness)

    # Put together and fillet

    clip      = clip_hook + backplate

    e = clip.edges().filter_by(Axis.X).group_by(Axis.Z)[fillet_idx].sort_by(Axis.Y)[3]
    clip       = fillet(e, radius=connect_fillet)
    clip       = fillet(clip.edges().group_by(Axis.Z)[1:], radius=common_fillet)
    #clip       = chamfer(clip.edges(), length=common_fillet)


    ######################################################################
    # View and save as a STEP and a STL file
    ######################################################################

    show(clip)
    sleep(3)

    basepath = os.path.join(script_dir, "%s_%.1fmm" % (
        Path(__file__).stem,
        backplate_thickness,
    ))

    export_step(clip, basepath + ".step")
    export_stl(clip, basepath + ".stl")
