# Thick liquid Container Scrapers
#
# These are scrapers to reduce waste go get the last out of bottles
# and Tetra Pak style containers that contains Yoghurt, sauces or
# other viscous/thick liquids.
#
# One of the most common brands in Sweden, Arla, uses Tetra Pak "Tetra
# Top 1000 Base CB" for their Yogurt. It has some variation of the
# Effie's C38 Pro cap with a 30 mm opening. According to a blog by
# Louise Ungerth, when trying to get the last out of these, 6.4 to 9 %
# of the Yogurt is left depending on how hard you try to get the last
# of it out. You are supposed to take apart the container but it is
# hard. With this scraper you can get more out without doing that
# (link to Swedish page)
#
#  https://louiseungerth.se/2019/03/12/ar-arlas-nya-forpackning-helkass/
#
# This model has a length of 280 mm and split into two parts and two
# plates, to fit the plate size of a A1 mini. This has the side effect
# that you can use different colors and materials for the shank and
# the handle without an AMS. You are supposed to glue together the two
# parts, but if you reduce the size of the handle 1-2 % you might get
# a snug fit and no need to glue. I printed the shank using PETG and
# the handle in PLA. The shank was printed with four wall loops and
# gyroid infill, and "0.16 mm High Quality".
#
# To make the scrape as big as possible, we first define a circle that
# is just enough to go into the opening of the container. Then we move
# it up or down and cut the sides to get the shape we want within that
# limitation.
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
from time import sleep

from build123d import *
from ocp_vscode import *

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------

infos = [
    {
        # This is the "Tetra Top 1000 Base CB" with 30 mm opening
        "name_extension"      : "_30mm",
        "scrape_radius"       : 14.5,  # 30 / 2 and a bit less
        "scrape_base_offset"  : 7,
        "bounding_box_height" : 17.4, # Originally scrape_radius * 1.2
        "bounding_box_width"  : 30,   # Originally scrape_radius * 2
        "shank_radius"        : 8,
    },
    {
        # More traditional Tetra Pak with 20 mm opening
        "name_extension"      : "_20mm",
        "scrape_radius"       : 9.5,  # 20 / 2 and a bit less
        # We want a different shape really, but got back to those
        #   ValueError: Failed creating a fillet with radius of 0.5, try
        #   a smaller value or use max_fillet() to find the largest
        #   valid fillet radius
        #"bounding_box_height" : 15,
        #"bounding_box_width"  : 15,
        "scrape_base_offset"  : 8.95,
        "bounding_box_height" : 11.5,
        "bounding_box_width"  : 30,
        "shank_radius"        : 1,
    },
    {
        # For sauce bottles, a bit rounded inside
        "name_extension"      : "_sauce",
        "scrape_radius"       : 11,  # 23 / 2 and a bit less
        "scrape_base_offset"  : 8.95,
        "bounding_box_height" : 22, # Need to be >= scrape_radius
        "bounding_box_width"  : 30,
        "shank_radius"        : None,
    },
]

total_length        = 280
scrape_length       = 230   # Max diagonally on Bambu Lab A1 mini plate
stem_radius         = 4
stem_base_offset    = 2.5
handle_depth        = 30    # How deep the stem goes into the handle
handle_length       = total_length - scrape_length + handle_depth
handle_radius       = 6
handle_base_offset  = 4.5
handle_insert_scale = 1.03  # How much bigger hole for gluing

script_path         = os.path.dirname(os.path.realpath(__file__))
basename            = Path(__file__).stem
basepath            = os.path.join(script_path, basename)

first  = True
handle = None               # Make "global" so can use show() for both


for info in infos:

    # ----------------------------------------------------------------------
    # To form the head we first create a cylinder that fits into the
    # opening of the container. Then we move this cylinder up or down,
    # and cut if off, to get the shape of it we want.  We use a
    # bounding box to cut off the head where we want, and to cut off
    # the bottom of the hole tool to make it lay down nicely on the
    # print bed.
    # ----------------------------------------------------------------------

    bounding_box = Rectangle(info["bounding_box_width"],
                             info["bounding_box_height"],
                             align=(Align.CENTER, Align.MIN, Align.MIN))

    # ----------------------------------------------------------------------
    # Create the scrape part of the model
    # ----------------------------------------------------------------------

    # Was all cylinder parts but I failed all tries to print this using
    # support on my A1 mini, so redesigned to lay down with no support.
    # General advice is to do 2D before 3D, so we form the different
    # 2D shapes before calling loft().

    c0 = (Pos(0, stem_base_offset, 0)           * Circle(stem_radius)) & bounding_box
    c1 = (Pos(0, stem_base_offset, 0)           * Circle(stem_radius)) & bounding_box
    c2 = (Pos(0, info["scrape_base_offset"], 0) * Circle(info["scrape_radius"])) & bounding_box
    c3 = (Pos(0, info["scrape_base_offset"], 0) * Circle(info["scrape_radius"])) & bounding_box

    if info["shank_radius"]:
        e = c2.vertices().group_by(Axis.Y)[-1]
        c2 = fillet(e, radius=info["shank_radius"])
        e = c3.vertices().group_by(Axis.Y)[-1]
        c3 = fillet(e, radius=info["shank_radius"])
    
    sections = [
        Pos(0, 0, 0)                 * c0,
        Pos(0, 0, scrape_length - 3) * c1,
        Pos(0, 0, scrape_length - 1) * c2,
        Pos(0, 0, scrape_length)     * c3,
    ]

    shank  = loft(sections, ruled=True)

    # Do some genera fillet
    shank = fillet(shank.edges().sort_by(Axis.Z), radius=0.5)

    export_step(shank, os.path.join(script_path,
                                    basepath + info["name_extension"] + "_shank.step"))

    # ----------------------------------------------------------------------
    # Create the handle part of the model once, as is the same
    # ----------------------------------------------------------------------

    if first:

        first = False

        # Could just use a circle and extrude() (or cylinder), but
        # lets use loft() if we want to change the shape in the future

        c0 = (Pos(0, handle_base_offset, 0) * Circle(handle_radius)) & bounding_box
        c1 = (Pos(0, handle_base_offset, 0) * Circle(handle_radius)) & bounding_box

        sections = [
            Pos(0, 0, 0)             * c0,
            Pos(0, 0, handle_length) * c1,
        ]

        handle  = loft(sections, ruled=True)

        # Do some genera fillet
        handle = fillet(handle.edges().sort_by(Axis.Z), radius=2)

        # Cut out a hole for the shank using the shank, but a tiny bit bigger
        # to make room for glue and make sure it can be inserted
        handle -= Pos(0, 2, handle_length - handle_depth) * \
            scale(shank, handle_insert_scale)

        # Punch a hole into the handle to hang it up, and do some
        # genera fillet to get the hole smoother
        hole = Plane.XZ * Pos(0, 18, 0) * Rot(0, 0, 90) * SlotOverall(20, 6)
        hole    = extrude(hole, amount=-handle_radius * 2)
        handle -= hole
        handle  = fillet(handle.edges().sort_by(Axis.Z), radius=0.5)

        export_step(handle, os.path.join(script_path, basepath + "_handle.step"))

    show(shank + Pos(25, 0, 0) * handle, position=[77.0, 82.0, 40.0])
    sleep(3)
    save_screenshot(os.path.join(script_path, basepath + info["name_extension"] + ".png"))
