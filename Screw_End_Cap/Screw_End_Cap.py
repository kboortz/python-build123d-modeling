# Screw End Cap
#
# You have a screw that extend from the wall, but for some reason you
# don't want/can cut it? You can at least protect humans from getting
# bad scratches or bad injury with this protective screw end cap.
#
# Use TPU, and to make the model soft use:
#
#   Wall loops            : 1
#   Top shell layers      : 2
#   Bottom shell layers   : 2
#   Sparce infill density : 10%
#   Sparce infill pattern : Gyroid
#
#   Variable layer height
#     Adaptive : 0.23
#     Smooth   : 10
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
from shutil import copy

from build123d import *
from ocp_vscode import *

# ======================================================================
# Data
# ======================================================================

# How much the screw extends from the wall
screw_heights   = [15, 20, 25, 30, 35, 40, 45, 50]
screw_diameters = [6, 8, 10]

screw_widening  = 1.3           # Make the hole a bit bigger
screw_grabber   = 1             # Star shaped friktion part

bottom_radius   = 20
top_radius      = 10

blade_count     = 6
blade_thickness = 0.5           # The nozzle size
blade_width     = top_radius

# ======================================================================
# Create paths and directories
# ======================================================================

script_dir = os.path.dirname(os.path.realpath(__file__))
basename   = Path(__file__).stem

dir_step = os.path.join(script_dir, "step")
dir_3mf  = os.path.join(script_dir, "3mf")
template = os.path.join(script_dir, "Templates", "Template.3mf")
    
os.makedirs(dir_step, exist_ok=True)
##os.makedirs(dir_3mf, exist_ok=True)

# ======================================================================
# Create the model
# ======================================================================

for screw_height in screw_heights:
    for screw_diameter in screw_diameters:

        screw_opening = screw_diameter / 2 * screw_widening
        top_extra = screw_opening + 1

        cap    = Cone(bottom_radius=bottom_radius,
                     top_radius=top_radius,
                     height=screw_height + top_extra,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

        e      = cap.edges().sort_by(Axis.Z).filter_by(GeomType.CIRCLE)[1]

        cap    = fillet(e, radius=top_radius)

        hole   = Circle(screw_opening)
        cap   -= extrude(hole, amount=screw_height)

        blades = Sketch() + \
                 PolarLocations(radius=0, count=blade_count) * \
                 Rectangle(blade_width, blade_thickness,
                           align=(Align.MIN, Align.CENTER, Align.MIN))

        # We stop the blades before the top, else will be hard to put
        # the cap on to the screw
        cap   += extrude(blades, amount=screw_height - screw_diameter)

        hole   = Circle(screw_diameter / 2 / screw_widening)
        cap   -= extrude(hole, amount=screw_height)

        # To make it easier for the printer, make the hole inside round
        # at the top, i.e. no need for support for overhang
        cap   -= Pos(0, 0, screw_height) * Sphere(screw_opening)

        show(cap)

        # ----------------------------------------------------------------------
        # Create the STEP file
        # ----------------------------------------------------------------------

        file_name = "%s_d%s_h%s.step" % (
            basename,
            screw_diameter,
            screw_height,
        )

        export_step(cap, os.path.join(dir_step, file_name))
        print("%s for M%s screw with %s mm height" % \
              (basename.replace("_", " "), screw_diameter, screw_height))

##        # NOTE: we don't overwrite... might have manually spent time
##        #       on the 3mf files
##        file_name = "%s_h%s_d%s.3mf" % (
##            basename,
##            screw_height,
##            screw_diameter,
##        )
##        file_3mf = os.path.join(dir_3mf, file_name)
##
##        if not os.path.isfile(file_3mf):
##            copy(template, file_3mf)
