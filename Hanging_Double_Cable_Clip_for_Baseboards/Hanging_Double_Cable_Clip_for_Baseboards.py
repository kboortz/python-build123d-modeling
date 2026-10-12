# Hanging Double Cable Clip for Baseboards
#
# Special cable clip for a typical extension cord and network cable.
# The cable diameters are to be 8.0 and 6.0 mm. You hang the clip on
# the baseboard. The actual cable clip will be on the front of the
# upper part of the baseboard.
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

cable_clip_width       = 10
cable_clip_thickness   = 1.5

# Cable clips, first highest up
cable_clip1_dia        = 6.0
cable_clip2_dia        = 8.0
cable_max_dia          = max(cable_clip1_dia, cable_clip2_dia)
cable_clip1_rad        = cable_clip1_dia / 2
cable_clip2_rad        = cable_clip2_dia / 2
cable_max_rad          = cable_max_dia / 2

cable_clip1_opening    = cable_clip1_dia * 0.85
cable_clip2_opening    = cable_clip2_dia * 0.85

baseboard_thicknesses  = [
     9.5 + 0.5,
    12.0 + 0.5,                 # Add 0.5 mm for paint etc
    15.0 + 0.5,
    14.3 + 0.5,                 # 9/16"
    15.9 + 0.5,                 # 5/8"
]
baseboard_outer_fillet = 1.5
baseboard_inner_fillet = 0.6

base_clip_height       = 30
base_clip_thickness    = 0.8    # Most are around 0.5
base_clip_shar_length  = 4
base_clip_shar_angle   = 4

common_fillet          = 0.6

clip_align             = (Align.MIN, Align.MIN, Align.CENTER)

script_dir             = os.path.dirname(os.path.realpath(__file__))


######################################################################
# Create the clip
######################################################################

# We first create like a box where we cut out the clip for the cable
# and the clip for the baseboard

for baseboard_thickness in baseboard_thicknesses:

    box_height = cable_clip1_dia + cable_clip2_dia + cable_clip_thickness * 3
    box_depth  = cable_max_dia + cable_clip_thickness + \
                 baseboard_thickness + base_clip_thickness

    face       = Rectangle(box_depth, box_height, align=clip_align)

    clip1_y    = cable_clip_thickness + cable_clip1_rad
    clip2_y    = cable_clip_thickness * 2 + cable_clip1_dia + cable_clip2_rad
    clip1_x    = cable_max_dia + cable_clip_thickness - cable_clip1_rad
    clip2_x    = cable_max_dia + cable_clip_thickness - cable_clip2_rad
    face      -= Pos(clip1_x, clip1_y) * Circle(cable_clip1_rad)
    face      -= Pos(clip2_x, clip2_y) * Circle(cable_clip2_rad)
    face       = fillet(face.vertices().sort_by(Axis.X)[0:2],
                        radius=cable_clip1_rad)

    # Cut out the baseboard

    face        -= Pos(cable_max_dia + cable_clip_thickness, cable_clip_thickness) * \
                   Rectangle(baseboard_thickness, box_height, align=clip_align)
    face         = fillet(face.vertices().sort_by(Axis.Y)[2], radius=baseboard_outer_fillet)
    face         = fillet(face.vertices().sort_by(Axis.Y)[2], radius=baseboard_inner_fillet)
    face         = fillet(face.vertices().sort_by(Axis.Y)[-2], radius=baseboard_inner_fillet)

    # Cut from the back to the holes, to create hooks

    face        -= Pos(cable_max_dia + cable_clip_thickness,
                       cable_clip_thickness + cable_clip1_rad) * \
                   Rectangle(cable_clip1_dia, cable_clip1_opening)
    face        -= Pos(cable_max_dia + cable_clip_thickness,
                       cable_clip_thickness * 2 + cable_clip1_dia + cable_clip2_rad) * \
                   Rectangle(cable_clip2_dia, cable_clip2_opening)

    # Make the baseboard clip a little bit sharp at the edge
    face        -= Pos(box_depth, box_height - base_clip_shar_length) * \
                   Rot(Z=7) * \
                   Rectangle(10, 10, align=clip_align)

    clip         = extrude(face, amount=cable_clip_width)

    e = clip.edges().filter_by(Axis.Z).group_by(Axis.X)[2:7]
    clip         = fillet(e, radius=common_fillet)

    e = clip.edges().filter_by(Axis.Z).group_by(Axis.X)[-1][0]
    clip         = fillet(e, radius=common_fillet)


    ######################################################################
    # View and save as a STEP file
    ######################################################################

    show(clip)

    sleep(3)

    basepath = os.path.join(script_dir, "%s_%.1fmm" % (
        Path(__file__).stem,
        baseboard_thickness,
    ))

    export_step(clip, basepath + ".step")
    export_stl(clip, basepath + ".stl")
