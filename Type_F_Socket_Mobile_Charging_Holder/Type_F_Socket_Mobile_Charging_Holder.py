# Type F Socket Mobile Charging Holder
#
# I created this to solve a specific problem of charging mobiles where
# there is no natural place to put the phone. Instead of some wall
# mount requiring making holes in the wall, or similar, this holder is
# fixated by a type F adapter that I have in a type F socket.
#
# As I'm a beginner trying to use Python and the "build123d" module
# to create this print, it is not even a good example of "build123d"
# usage, but maybe it demonstrates what can be done with such a
# package.
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

import sys
import os.path
from time import sleep
from pathlib import Path

from build123d import *
from ocp_vscode import *

# ======================================================================
# Data
# ======================================================================

# Plate size is based on size of iPhone 17 Pro Max and
# Samsung Galaxy A16

plate_length      = 175
plate_width       = 90
plate_thickness   = 2
plate_corner_rad  = 4             # Round the corners
plate_fillet_rad  = 0.4

edge_width        = 2            # Small edge to protect
edge_thickness    = 2            # phones from falling off
edge_fillet_rad   = 1.6

base_width        = 130          # Enough to stand on adapter
base_depth        = 35           # Smaller vs typical adapter
base_height       = 10           # Space for larger charger
base_corner_rad   = 4
base_fillet_rad   = 1

# This is the free space for the socket
socket_space      = 37

# The back plate
bplate_width      = base_width - base_corner_rad * 2
bplate_height     = 40
bplate_thickness  = 1.2         # Should be thin
bplate_corner_rad = 10

beam_length       = 47
beam_with         = 4
beam_thickness    = 7
beam_fillet_rad   = 1.5

# FIXME this is a bit hard to explain. To get smother edge seen from
# where you put down the phone, we make the cutout bigger to get a
# larger fillet, but push it not fully down...
edge_up = 3

align_against_XZ = (Align.CENTER, Align.MIN, Align.CENTER)


# ======================================================================
# Create the plate for the phone to rest on
# ======================================================================

plate_rectangle  = RectangleRounded(plate_length,
                                    plate_width,
                                    radius=plate_corner_rad)
cutout_rectangle = RectangleRounded(plate_length - edge_width,
                                    plate_width - edge_width,
                                    radius=plate_corner_rad)

plate  = extrude(plate_rectangle,
                 amount=plate_thickness + edge_thickness)
cutout = extrude(cutout_rectangle,
                 amount=edge_thickness + edge_up)

# Round the plate a bit
plate  = fillet(plate.edges(), radius=plate_fillet_rad)

# Round the bottom of the cutout
e = cutout.edges().group_by(Axis.Z)[0]
cutout = fillet(e, radius=edge_fillet_rad + edge_up)

plate -= Plane.XY.offset(plate_thickness) * cutout

# ======================================================================
# Let the plate be on top of a riser from the adapter, to give some
# space for larger chargers
# ======================================================================

base_rectangle = RectangleRounded(base_width,
                                  base_depth,
                                  radius=base_corner_rad)

# We make it a tiny bit higher, to remove the fillet
# where the base and plate connect
base = extrude(base_rectangle, amount=base_height + plate_fillet_rad)

e = base.edges().group_by(Axis.Z)[0]
base = fillet(e, radius=base_fillet_rad)


# ======================================================================
# Back plate, stick down a thin plate on both sides of the connector
# at the back of the adapter, that go into the socket
# ======================================================================

bplate_rectangle = Rectangle(bplate_width, bplate_height + base_height)
bplate_rectangle -= Circle(socket_space / 2)
bplate_rectangle -= Pos(0, -socket_space / 2, 0) * \
                    Rectangle(socket_space, socket_space)
bplate_rectangle  = mirror(bplate_rectangle, about=Plane.XY)

e = bplate_rectangle.vertices().group_by(Axis.Y)[0]
bplate_rectangle  = fillet(e, radius=bplate_corner_rad)

bplate = extrude(bplate_rectangle, amount=bplate_thickness)

# As the back plate is thin, we add two stabilizers
beam_rectangle    = Rectangle(beam_with, beam_thickness)
beam_left         = Pos(bplate_width / 2 - beam_with / 2,
                        beam_thickness / 2, 0) * \
                    extrude(beam_rectangle, amount=-beam_length)
e = beam_left.edges().group_by(Axis.Y)[1:]
beam_left         = fillet(e, radius=beam_fillet_rad)
beams             = mirror(beam_left, about=Plane.YZ) + beam_left


# ======================================================================
# Put them together
# ======================================================================

model = Pos(0, plate_width / 2, 0) * plate + \
        Pos(0, base_depth / 2, plate_fillet_rad - base_height) * base + \
        Pos(0, 0, - bplate_height / 2 - base_height) * \
            bplate.rotate(Axis.X, 90) + \
        beams
    
# ======================================================================
# Output ...
# ======================================================================

# Hunting down strange flow changes, possibly causing a print to have
# a layer shift, I tried fix it by adding fillet between plate and base.
# Turns out, the likely cause was adaptive layer height. Turning it off,
# problem not visible in the slicing result speed view. But... maybe
# nice to have some fillet there, keeping it :) 
e = model.edges().group_by(Axis.Z)[20].sort_by(Axis.X)[4:12]
model = fillet(e, radius=4)
show(model)

script_path = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem
basepath = os.path.join(script_path, basename)
export_stl(model, os.path.join(script_path, basepath + ".stl"))
