# IKEA STRANDMON Wing chair furniture leg raisers
#
# Using TPU to get both strength and smooth connection to the floor.
# In my case PrintOnion TPU Classic, where changed some defaults
# (advanced mode):
#
#   Strength -> Wall loops -> 10
#   Strength -> Sparce infill pattern -> Rectliniar
#   Strength -> Sparce infill dencity -> 100%
#   Speed -> Outer wall -> 100 mm/s
#
# This model is licensed under the MakerWorld Creative Commons
# Attribution-NonCommercial-Share-Alike
# https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Author: Kent Boortz <kent.boortz@gmail.com>

# pylint: disable=consider-using-f-string
# pylint: disable=consider-using-generator
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import

# ======================================================================
# Imports
# ======================================================================

import os.path
from time import sleep
from pathlib import Path

from build123d import *
from ocp_vscode import *

# ======================================================================
# Data
# ======================================================================

upper_thickness = 2      # Thickness where raiser ends

positions = ["front", "back"]

leg_info = {
    "front" : {
        "top_diameter" : 50,
        "bot_diameter" : 25,
        "height"       : 137,
        "raise"        : 60,
        "overlap"      : 50,
    },
    "back" : {
        "top_diameter" : 45,
        "bot_diameter" : 24,
        "height"       : 122,
        "raise"        : 70,    # A little higher in the back
        "overlap"      : 70,    # Move overlap in the back
    },
}

# ======================================================================
# Construct the legs to cut out later, one front and one back
# ======================================================================

align = (Align.CENTER, Align.CENTER, Align.MIN)

for position in positions:
    leg_info[position]["leg"] = \
        Cone(leg_info[position]["bot_diameter"] / 2,
             leg_info[position]["top_diameter"] / 2,
             leg_info[position]["height"],
             align=align)

# ======================================================================
# Construct the parts, one front and one back
# ======================================================================

for position in positions:
    # Calculate the top diameter of the raiser from the diameter at that
    # spot on the leg, and add some extra to create the hole to insert
    # the legs into
    top_diameter = leg_info[position]["bot_diameter"] + \
        leg_info[position]["overlap"] / leg_info[position]["height"] * \
        (leg_info[position]["top_diameter"] - leg_info[position]["bot_diameter"]) + \
        upper_thickness * 2
    leg_info[position]["raiser"] = \
        Cone(leg_info[position]["bot_diameter"] / 2,
             top_diameter / 2,
             leg_info[position]["raise"] + leg_info[position]["overlap"],
             align=align)
    leg_info[position]["raiser"] -= \
        Pos(0, 0, leg_info[position]["raise"]) * leg_info[position]["leg"]

# ======================================================================
# Output STL
# ======================================================================

script_path = os.path.dirname(os.path.realpath(__file__))
basename = Path(__file__).stem
basepath = os.path.join(script_path, basename)

for position in positions:
    filename = f"{basepath}_{position}.stl"
    export_stl(leg_info[position]["raiser"],
               os.path.join(script_path, filename))
    show(leg_info[position]["raiser"])
    sleep(4)
