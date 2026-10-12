# Torx Cap
#
# I have used torx screws to put up white corners on a cabin. I refuse
# to paint over the screws to make them invisible, as I in the future
# want to be able to take them down and repaint without the struggle
# to get the screws out. So I created torx caps to make the screws
# invisible from a distance.
#
# The page below defines the inner circle and the two circles for the
# shape as functions of the outer diameter
#
#   https://www.engineersedge.com/hardware/torx_head_fastener_basic_dimensions_15261.htm
#
# The page below has a table with the actual values for T20 and others
#
#   https://www.youfutools.com/Tool-knowledge/168.html

# ======================================================================
# Imports
# ======================================================================

import sys
import os.path
from time import sleep
from pathlib import Path

from build123d import *
from ocp_vscode import *

# ======================================================================
# Data
# ======================================================================

T20_A   = 3.94
T20_B   = 2.83
T20_R1  = 0.83
T20_R2  = 0.33
T20_C   = 1.4
cap_dia = 10
cap_dep = 1.5
cap_fil = 1.2

extra_deps = ["0.0", "0.5", "1.0", "1.5", "2.0", "2.5", "3.0"]

script_dir      = os.path.dirname(os.path.realpath(__file__))
basename        = Path(__file__).stem

# ======================================================================
# Create the cap head
# ======================================================================

head = Circle(cap_dia / 2)
head = extrude(head, amount=cap_dep)

e     = head.faces().sort_by(Axis.Z).last.edges()
#head  = fillet(e, radius=cap_fil)
head  = chamfer(e, length=cap_fil)

# ======================================================================
# Create the torx part, slightly "too large" to secure it in the screw
# Also create deeper variants in case screw head it deep down
# ======================================================================

caps = []

for extra_dep_str in extra_deps:

    extra_dep = float(extra_dep_str)

    insert = Circle(T20_A / 2)

    insert -= PolarLocations(radius=T20_B / 2 + T20_R1,
                             count=6,
                             start_angle=30) * Circle(T20_R1)

    insert  = fillet(insert.vertices(), radius=T20_R2)

    insert  = extrude(insert, amount=-(T20_C + extra_dep))

    e       = insert.faces().last.edges().sort_by(Axis.Z)
    insert  = fillet(e, radius=0.2)

    caps.append((extra_dep_str, insert + head))

# ======================================================================
# Create the STEP file
# ======================================================================

for extra_dep_str, cap in caps:

    show(cap)
    sleep(1)

    filename = basename
    if extra_dep_str != "0.0":
        filename += "_extra_" + extra_dep_str + "mm"
    step_filename  = filename + ".step"
    image_filename = filename + ".png"
    export_step(cap, os.path.join(script_dir, step_filename))
    save_screenshot(os.path.join(script_dir, image_filename))
