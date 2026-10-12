# IKEA HEMNES Bedside Table Power Strip Holder
#
# This is not very useful to anyone as it is specific for IKEA HEMNES
# bedside table together with a Lidl SilverCrest 4-way power strip that
# has one USB-A and one USB-C port. The power strip dimensions are
# 270 x 49.5 x 41.5 mm. Screw into the table leg using 4x20 mm screws.
#
# As I'm a beginner trying to use Python and the "build123d" module
# to create this print, it is not even a good example of "build123d"
# usage, but maybe it demonstrates what can be done with such a
# package.
#
# This is one of my first uses of "build123d", i.e. nothing fancy :)
#
# I created the 3mf file on macOS
#
#  % open -a BambuStudio *plain_side.stl
#  % open -a BambuStudio *cord_side.stl
#
# Moved them apart in BambuStudio, and hit the Auto Orient button
# for each so that no support is needed.
#
# This Python script can't be embedded into the 3mf file using Bambu
# Studio. During the upload to https://makerworld.com I could add
# this file to "Raw Model Files".
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
# native language. This is also reflected in how I hame the variables.
#
#                     BRACKET
# +--------------+      /            ||               ||               ||
# | \  \  \  \   |\    /             ||               ||               ||
# |  \  \  \  \  | \  /              ||               ||               ||
# |  TABLE LEG \ |  \/            +--++--+         +--++--+         +--++--+
# | \  \  \  \   |  /\    LIP     |      |         |      |         |      |
# |  \  \  \  \  |    \   /       |      |         |      |         |      |
# |   \  \  \  \ |     \ /      +-+------+-+     +-+------+-+     +-+------+-+
# +----------+---+---+--+       |          |     |          |     |          |
#             \      |   \------+----------+---+----------+---+----------+-----|
#              \     |    \                                                     |
#               \/   |     \                                                   |
#               /\   |      \              N-WAY SOCKET                       |
#              /  \  |       \                                                 |
#           HEEL   \ | HOLDER \                                               |
#                   \|         \-------------------------------------------- |
#                    +----------+

import sys
import os.path
from time import sleep
from pathlib import Path

from build123d import *
from ocp_vscode import *

socket_length   = 270           # Lidl 4x socket with one USB-A and one USB-C
socket_width    = 49.5
socket_height   = 41.5          # 40.5, but 41.5 if counting where stands up a bit
lip_overlap     = 13            # How much to go into front of the socket
leg_opening     = 300           # Opening between the table legs
leg_width       = 35            # Thickness where meets side of socket
cord_radius     = 5.5           # Opening on one side, really the strain relief radius
cord_entry_radius = 7.5         # Extra sink space where cord goes into socket
sink_radius     = 4.5           # 9 mm head of the screw/washer
screw_radius    = 2.2           # Screws 4 x 20 or 4 x 25 mm
screw_plate     = 4             # Thickness of the screw hole
heel_overlap    = 10            # How much to lean on the leg

vent_offset_x   = 7             # This socket has ventilation holes in a row
vent_offset_y   = 4
vent_width      = 25
vent_height     = 6

# Thickness of various parts of the model
# FIXME changing to 2.5 causes renumbering of the faces...
wall_thickness  = 3             # General thickness of model
#holder_back_extra_heel = 2.5    # Extra room on the back, not to cover vents and hole

# ----------------------------------------------------------------------
# Calculated measurements
# ----------------------------------------------------------------------

part_depth    = socket_width + wall_thickness * 2

# We need to calculate the bracket first, as we want the same angle
bracket_width   = leg_width     # Part where we screw into the leg
bracket_height  = (leg_opening - socket_length) / 2 - wall_thickness + lip_overlap

holder_width    = socket_height + wall_thickness * 2 # Part where we stick in the socket
holder_offset   = (leg_opening - socket_length) / 2 - wall_thickness
holder_top_lip  = lip_overlap
holder_bot_lip  = holder_top_lip + (bracket_height / bracket_width) * holder_width
holder_hole1    = (part_depth - cord_radius) / 4
holder_hole2    = part_depth - holder_hole1

heel_width      = socket_height + wall_thickness * 2
heel_height     = holder_offset + heel_overlap

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
# Construct the parts
# ----------------------------------------------------------------------

pts_bracket = [
    (0, 0),
    (bracket_width, 0),
    (bracket_width, bracket_height),
    (0, 0),
]

# FIXME move plane?
pts_holder = [
    (0, 0),
    (holder_width, 0),
    (holder_width, holder_bot_lip),
    (0, holder_top_lip),
    (0, 0),
]

# FIXME move plane?
pts_heel = [
    (0, 0),
    (0, -heel_height),
    (heel_width, 0),
    (0, 0),
]

bracket_profile  = Polyline(pts_bracket)
holder_profile   = Polyline(pts_holder)
heel_profile     = Polyline(pts_heel)

bracket_face     = make_face(Plane.YZ * bracket_profile)
holder_face      = make_face(Plane.YZ * Pos(X=bracket_width, Y=holder_offset) * holder_profile)
heel_face        = make_face(Plane.YZ * Pos(X=bracket_width, Y=holder_offset) * heel_profile)

bracket_part     = extrude(bracket_face, amount=part_depth)
holder_part      = extrude(holder_face, amount=part_depth)
heel_part        = extrude(heel_face, amount=part_depth)

# Cut out where to insert the socket
holder_part      = offset(holder_part, amount=-wall_thickness,
                          openings=holder_part.faces().sort_by().last)

# Cut out the heel to save filament
heel_part        = offset(heel_part, amount=-wall_thickness,
                          openings=heel_part.faces().sort_by()[1])

# Make holes for screws
bracket_part -= Pos(holder_hole1, bracket_width / 2, 0) * \
    Cylinder(screw_radius, height=bracket_height)

bracket_part -= Pos(holder_hole1, bracket_width / 2, screw_plate) * \
    Cylinder(sink_radius, height=bracket_height,
             align=(Align.CENTER, Align.CENTER, Align.MIN))

# FIXME use mirror() somehow?
bracket_part -= Pos(holder_hole2, bracket_width / 2, 0) * \
    Cylinder(screw_radius, height=bracket_height)

bracket_part -= Pos(holder_hole2, bracket_width / 2, screw_plate) * \
    Cylinder(sink_radius, height=bracket_height,
             align=(Align.CENTER, Align.CENTER, Align.MIN))

# ----------------------------------------------------------------------
# Cut out slots for the ventilation holes on the socket
# ----------------------------------------------------------------------

holder_back_plane = Plane(holder_part.faces().sort_by()[8])

# FIXME this is all stupid, but currently I know too little about
# build123d to fix it :(

vent1 = holder_back_plane * Pos(8, 18, 0) * \
    SlotOverall(vent_width, vent_height)
holder_part -= extrude(vent1, -wall_thickness*10)

vent2 = holder_back_plane * Pos(8, -18, 0) * \
    SlotOverall(vent_width, vent_height)
holder_part -= extrude(vent2, -wall_thickness*10)

# ----------------------------------------------------------------------
# Combine them to one side of our 3D print
# ----------------------------------------------------------------------

plain_side = bracket_part + heel_part + holder_part

# ----------------------------------------------------------------------
# Create the other side with a slot for the cord
# ----------------------------------------------------------------------

cord_side = plain_side

cord_side -= Pos(part_depth / 2, 0, 0) * \
    Box(cord_radius * 2, bracket_width + holder_width / 2, 200,
        align=(Align.CENTER, Align.MIN, Align.CENTER))

holder_side_plane = Plane(holder_part.faces().sort_by()[1])
cord_side -= holder_side_plane * \
    CounterSinkHole(radius=cord_radius, counter_sink_radius=cord_entry_radius, depth=10)

# ----------------------------------------------------------------------
# Output the STL and view the model
# ----------------------------------------------------------------------

# FIXME better name
script_path = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem
basepath = os.path.join(script_path, basename)
export_stl(plain_side, os.path.join(script_path, basepath + "_plain_side.stl"))
export_stl(cord_side,  os.path.join(script_path, basepath + "_cord_side.stl"))

show(plain_side)
sleep(4)
show(cord_side)
