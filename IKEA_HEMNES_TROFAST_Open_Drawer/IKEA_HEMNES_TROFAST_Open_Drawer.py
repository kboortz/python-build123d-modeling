# IKEA TROFAST as an extra drawer for the IKEA HEMNES Bedside Table
#
# This is drawer runners for mounting the smallest IKEA TROFAST
# Storage Box as an extra drawer under the IKEA HEMNES Bedside Table.
# You can mount it using the IKEA ALFTA double-sided tape refill,
# or use 4 x 20 screws.
#
# You could of course 3D print the drawer but as IKEA TROFAST
# is dirt cheap, I opted for only creating the drawer runners.
#
# I output a STEP file instead of STL. The STEP file preserves the
# geometric data, while using STL means the build123d package has to
# use the geometric data to create a mesh model. Using STEP means we
# let the slicer deal with whatever conversion is needed and this
# might produce better prints.
#
# I'm using the Python module "build123d" to create this model. I'm a
# beginner trying to use this module and this means this code is not a
# good example of "build123d" usage. But maybe it demonstrates what
# can be done with such a package.
#
# Author  : Kent Boortz
# License : Public Domain
#
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

import os.path
from pathlib import Path

from build123d import *
from ocp_vscode import *


# ======================================================================
# Data
# ======================================================================

# The opening right under the drawer is ~301 mm, so no extra space
# where you will insert IKEA TROFAST. The leg is 35 mm that high up.
# Under where the regular drawer is inserted, there is a plate where
# we will mount this new track for a second drawer, it ends 70 mm from
# the front of the leg.
#
# Note that the space is a bit extra restricted for me, as I have a
# power strip holder taking up space (my own 3D model).

track_length         = 209      # Close to IKEA TROFAST width
track_width          = 12
track_thickness      = 4
track_stop_thickness = 2

track_wall_height    = 12.5     # IKEA TROFAST edge height is 12 mm
track_wall_width     = 30
track_wall_thickness = 4
track_wall_offset    = 25       # A bit in on the 35 mm leg

chamfer_width        = 4.5

mount_width          = 20       # ALFTA is 20, can't use more
mount_length         = 75       # ALFTA is 68
mount_thickness      = 12
mount_offset         = 65
mount_overlap        = 2.5      # Need to overlap track_wall_height some
alfta_thickness      = 1

screw_radius         = 2.2      # For screws 4 x 20
screw_plate          = 4        # Thickness of the screw hole

align_to_origin    = (Align.MIN, Align.MIN, Align.MIN)

# Adjust track_wall_height so we can overlap with mount
track_wall_height += mount_overlap

# ======================================================================
# Create where the new drawer will slide
# ======================================================================

track_rect      = Rectangle(track_width, track_length,
                            align=align_to_origin)
track           = extrude(track_rect, amount=track_thickness)

track_stop_rect = Plane.XZ * \
                  Pos(0, 0, -track_length) * \
                  Rectangle(track_wall_width,
                            track_wall_height + track_thickness,
                            align=align_to_origin)
track_stop      = extrude(track_stop_rect, amount=track_stop_thickness)

e = track_stop.edges().group_by(Axis.Y)[1].sort_by(Axis.X)[2:4]
track_stop      = fillet(e, radius=4)

track_wall_rect = Plane.YZ * \
                  Pos(track_wall_offset, 0, -track_wall_thickness) * \
                  Rectangle(track_length - track_wall_offset,
                            track_wall_height + track_thickness,
                            align=align_to_origin)
track_wall      = extrude(track_wall_rect, amount=track_wall_thickness)

model = Solid() + [track, track_stop, track_wall]

e = model.edges().group_by(Axis.X)[0].sort_by(Axis.Z)[0]
model = chamfer(e, chamfer_width)

# Smooth it all a bit, except upper part
model = fillet(model.edges().group_by(Axis.Z)[:-1], radius=0.5)


# ======================================================================
# Create the mount part
# ======================================================================

# Were the mount meets the table, there is a 1 mm gap, exactly what we
# need to make space for the IKEA ALFTA double-sided tape We could
# stretch out the mount to the end of the track, but then we would not
# be able reach the release handle on the tape to dismount.

mount_rect      = Plane.YZ * \
                  Pos(mount_offset,
                      track_wall_height + track_thickness - mount_overlap, 0) * \
                  Rectangle(mount_length, mount_width + mount_overlap,
                            align=align_to_origin)
mount           = extrude(mount_rect,
                          amount=mount_thickness)

e = mount.edges().group_by(Axis.X)[1].sort_by(Axis.Z)[0]
mount = fillet(e, radius=4)
mount = fillet(mount.edges().group_by(Axis.X)[2], radius=0.5)

# Alternative mounting two holes for using screws
hole = Plane.YZ * \
       Pos(mount_offset + mount_length / 8,
           track_wall_height + track_thickness + mount_width / 2,
           mount_thickness) * \
       CounterSinkHole(radius=screw_radius, counter_sink_radius=screw_plate,
                       depth=mount_thickness)

mount -= hole
mount -= Pos(0, mount_length * 6 / 8) * hole

model += mount


# ======================================================================
# View the model and output the STEP files
# ======================================================================

show(model)

script_path = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem
basepath = os.path.join(script_path, basename)
export_step(model, os.path.join(script_path, basepath + "_left.step"))
model = mirror(model, Plane.YZ)
export_step(model, os.path.join(script_path, basepath + "_right.step"))
