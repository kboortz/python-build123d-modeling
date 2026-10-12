# Anti Sink Chair Feet
#
# This adds larger feet on garden chair legs, to avoid damaging the new,
# summer hot and soft asphalt. For strength solid TPU is used, i.e. 99
# wall loops.
#
# This is for legs that are 25 mm (actually more like 24.7 mm) with
# rounded pads and a 13 degree angle. It is a snug fit. Easiest to get
# them on is push them on a bit at the right angle, and then use your
# body weight to push the whole chair down.
#
# Fun fact, prolonged exposure to the sun, and then UV light, can cause
# TPU to degrade over time and become brittle, discolored and lose its
# physical properties. But using black TPU transforms most of the light
# to heat, including the UV light, making this less of a problem. Well,
# hopefully :)
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

angle       = 13

# The leg diameter is hard. I measured it to be exactly 24.7 mm and
# expected that if I use that, the feet would stay on. It did not.
# So trying slightly smaller now and hope it will work.
leg_rad       = 24.2 / 2
leg_height    = 500             # Mostly for debugging, could be anything

shaft_rad     = leg_rad + 3.5
shaft_height  = 45
pad_rad       = 60 / 2
pad_height    = 8               # A flat part under the shaft

fillet_conn   = 4               # Connection pad to shaft
fillet_top    = 1.4             # Outside at the top of shaft
fillet_gen    = 0.6             # Generic, small fillet

align_XY      = (Align.CENTER, Align.CENTER, Align.MIN)

script_dir    = os.path.dirname(os.path.realpath(__file__))
basename      = Path(__file__).stem

# ======================================================================
# Create a replica of the leg to punch into the feet. Note that the
# leg has a cap that is rounded, i.e.  a half circle. We could remove
# it from the chair leg, but let's keep it and make the hole in the
# feet be the same shape.
# ======================================================================

leg = Pos(Z=pad_height + leg_rad) * \
      Cylinder(radius=leg_rad,
               height=leg_height,
               align=align_XY)

tip = Pos(Z=pad_height + leg_rad) * \
      Sphere(radius=leg_rad)

# ======================================================================
# We create the shair leg to use to punch into the chair feet
# ======================================================================

pad   = Cylinder(radius=pad_rad,
                 height=pad_height,
                 align=align_XY)

shaft = Pos(Z=pad_height / 2) * \
        Cylinder(radius=shaft_rad,
                 height=shaft_height,
                 align=align_XY)

# ======================================================================
# Tilt the shaft and connect it to the pad
# ======================================================================

feet  = shaft - tip - leg
feet  = Rot(angle) * feet
feet += pad

# ======================================================================
# Soften the connection between shaft and pad
# ======================================================================

e     = feet.edges() \
        - feet.edges().filter_by(GeomType.CIRCLE) \
        - feet.edges().filter_by(Axis.Z)
feet  = fillet(e.sort_by(Axis.Z)[0], radius=fillet_conn)

e = feet.edges().sort_by(Axis.Z).filter_by(GeomType.CIRCLE)[-1]
feet  = fillet(e, radius=fillet_top)

e1 = feet.edges().sort_by(Axis.Z).filter_by(GeomType.CIRCLE)[0:2]
e2 = feet.edges().sort_by(Axis.Z).filter_by(GeomType.CIRCLE)[-2]
feet  = fillet([e1, e2], radius=fillet_gen)

# ======================================================================
# Create the STEP file
# ======================================================================

show(feet)

file_name = "%s_%s_deg.step" % (
    basename,
    angle,
)

export_step(feet, os.path.join(script_dir, file_name))
