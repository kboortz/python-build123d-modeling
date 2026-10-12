# Clothes Hanger Door Hook
#
# After washing I hang some clothes on clothes hangers to dry. As I
# lack space I often put the hook of the clothes hangers over wardrobe
# doors. With this print I can more easily do this and also hang more
# than one clothes hanger on a wardrobe door.
#
# This print is inspired by
#
#  https://makerworld.com/en/models/1573532-door-clothes-hook
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
# Author  : Kent Boortz
#
# pylint: disable=consider-using-f-string
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

import os.path
from pathlib import Path
from time import sleep

from build123d import *
from ocp_vscode import show

# ======================================================================
# Dimensions and measurements
# ======================================================================

# Generate one
door_widths = [
    16.22,
    21.27,
    40.00,
]

height          = 65
depth           = 140
width           = 25            # Width of it all
hook_radius     = 10            # The three hooks cut out
grab            = 30            # Inside depth on the back side
grab_thickness  = 4
door_distance   = 8             # Space between door and first cutout

cutout_count    = 4
cutout_offset_x = 18
cutout_offset_y = 3

fillet_back     = 2
fillet_nock     = 8
fillet_edge     = 8
fillet_bottom   = 4
fillet_circles  = 2
fillet_strange  = 1
fillet_small    = 1

# ======================================================================
# Function to create the part with a door width
# ======================================================================

def create_part(arg_door_width):

    # ----------------------------------------------------------------------
    # Create the hook over the door
    # ----------------------------------------------------------------------

    pts = [
        (0, height - grab - grab_thickness),
        (0, height),
        (grab_thickness + arg_door_width + grab_thickness, height),
        (grab_thickness + arg_door_width + grab_thickness + depth, 0),
        (grab_thickness + arg_door_width, 0),
        (grab_thickness + arg_door_width, height - grab_thickness),
        (grab_thickness, height - grab_thickness),
        (grab_thickness, height - grab - grab_thickness),
    ]

    part_line = Polyline(pts, close=True)
    part_face = make_face(Plane.XY * part_line)
    part = extrude(part_face, amount=width / 2, both=True)

    part = fillet(part.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2], radius=fillet_back)
    part = fillet(part.edges().filter_by(Axis.Z).sort_by(Axis.X)[8],  radius=fillet_nock)
    part = fillet(part.edges().filter_by(Axis.Z).sort_by(Axis.X)[10], radius=fillet_edge)

    # ----------------------------------------------------------------------
    # Create a cylinder where to cut out the hangers
    # ----------------------------------------------------------------------

    cutout_face = Circle(hook_radius)
    cutout_part = extrude(cutout_face, amount=width / 2, both=True)

    cutout_pos_x = grab_thickness + arg_door_width + hook_radius + door_distance
    cutout_pos_y = height - hook_radius

    for _i in range(cutout_count):
        part -= Pos(cutout_pos_x, cutout_pos_y, 0) * cutout_part
        cutout_pos_x += hook_radius + cutout_offset_x
        cutout_pos_y -= hook_radius + cutout_offset_y

    # ----------------------------------------------------------------------
    # Do some more fillets
    # ----------------------------------------------------------------------

    part = fillet(part.edges().filter_by(Axis.X).sort_by(Axis.Y)[0:2],
                  radius=fillet_bottom)

    circle_edges = part.edges().filter_by(Axis.Z).sort_by(Axis.X)[-9:-2]
    part = fillet(circle_edges, radius=fillet_circles)

    # Well... what happens is by accident, but looks good. I only indtended
    # to round the last edge of the last circle, and wanted radius=4. Got
    # errors, and when using radius=1 it smooths more
    circle_edges = part.edges().filter_by(Axis.Z).sort_by(Axis.X)[-1]
    part = fillet(circle_edges, radius=fillet_strange)

    # Smooth the edges of the hook, to make stronger and more polished looking
    part = fillet(part.edges().filter_by(Axis.Z).sort_by(Axis.X)[4:7],
                  radius=fillet_small)

    # ----------------------------------------------------------------------
    # Output the STL and view the model
    # ----------------------------------------------------------------------

    show(part)
    sleep(1)

    script_path = os.path.dirname(os.path.realpath(__file__))
    basename = Path(__file__).stem
    basepath = os.path.join(script_path, basename)
    export_stl(part, os.path.join(script_path,
                                  "%s_%smm.stl" % (
                                      basepath,
                                      arg_door_width)))

# ======================================================================
# Create all parts for all door widths
# ======================================================================

for door_width in door_widths:
    create_part(door_width)
