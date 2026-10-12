# Splash Protected Manual Toothbrush Wall Mount
#
# If wall mounting the toothbrush close to the bathroom sink, there is
# a risk of water and soap splashing on the toothbrush!
#
# There are other models that handle this, but I found them too
# complicated or not that hygienic as the toothbrush bristles touches
# the holder when taking out the toothbrush.
#
# So I made a simpler model where you put the toothbrush in from the
# side, with a roof over the actual holder. There are two plates, one
# for a print with right handed access and one for left handed access.
#
# The holder is to be mounted on the wall using a double sided
# adhesive pad. The actual holder is detachable for easy cleaning.
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

import sys
import os.path
from pathlib import Path
from io import StringIO

from build123d import *
from ocp_vscode import *

# ======================================================================
# Data
# ======================================================================

model_depth            = 25     # From wall to outer part
model_height           = 40     # From opening to roof
model_width            = 30     # Plate against the wall tile,
                                # where to use double sided tape
wall                   = 1.2

opening_width          = 6      # Where you insert the toothbrush
opening_depth          = model_width - 3 # If too close, fillets will fail

corner_fillet          = 4
roof_fillet            = 10
cutout_fillet          = 2
smooth_fillet          = 0.5

bplate_height          = model_height - corner_fillet * 2
bplate_width           = model_width
bplate_thickness       = 2.5    # We cut 1.5 into the wall plate
dovetail_thickness     = 1.7    # Fastened on the part
# We simulate groove angle by specifying top and bottom width
dovetail_top           = 14
dovetail_bot           = 8
dovetail_top_offset    = 13
dovetail_bot_offset    = 5
dovetail_stop          = 4         # Edge to where dovetail ends
dovetail_scale         = 1.05      # Slichtly larger slot

arrow_icon_height      = 12
toothbrush_icon_height = 20

# position=(model_depth, vertical, horizontal)
arrow_location         = Location(position=(model_depth, 12, 20),
                                  orientation=(0, 90, 0))
toothbrush_location    = Location(position=(model_depth, 6.5, 8),
                                  orientation=(0, 90, 0))

# ======================================================================
# Create the model
# ======================================================================

face   = Rectangle(model_depth, model_height,
                   align=(Align.MIN, Align.MIN))
face   = fillet(face.vertices().sort_by(Axis.X)[0:3],
                radius=corner_fillet)
face   = fillet(face.vertices().sort_by(Axis.X).sort_by(Axis.Y)[-1],
                radius=roof_fillet)

model  = extrude(face, amount=model_width)

model  = offset(model, amount=-wall, openings=face)

# ----------------------------------------------------------------------
# Cut out the opening for sliding in the toothbrush
# ----------------------------------------------------------------------

face   = Plane.XZ * \
         Pos(model_depth / 2) * \
         Rectangle(opening_width, opening_depth,
                   align=(Align.CENTER, Align.MIN))
cutout = extrude(face, amount=-wall)

model -= cutout

# ----------------------------------------------------------------------
# Fillet the cutout corners
# ----------------------------------------------------------------------

e = (
    model.edges()
    .filter_by(Axis.Y)
    .group_by(Axis.Y)[0]
    .group_by(Axis.Z)[0:2]
)
model = fillet(e, radius=cutout_fillet)

# ----------------------------------------------------------------------
# Fillet all a little bit
# ----------------------------------------------------------------------

model  = fillet(model.edges(), radius=smooth_fillet)

# ----------------------------------------------------------------------
# Create a dovetail on the back of the part, by specifying the up and
# down faces and offset() in between
# ----------------------------------------------------------------------

# We are to tilt the bottom face 45 degrees, to make it easier for the
# 3D printer. When that face is tilted, we need to increase the height
# a bit

dovetail_bot_thickness = 2 ** 0.5 * dovetail_thickness

pts_top = [
    (dovetail_thickness, 0),
    (dovetail_top - dovetail_thickness, 0),
    (dovetail_top, dovetail_thickness),
    (0, dovetail_thickness),
]
pts_bot = [
    (dovetail_bot_thickness, 0),
    (dovetail_bot - dovetail_bot_thickness, 0),
    (dovetail_bot, dovetail_bot_thickness),
    (0, dovetail_bot_thickness),
]
top_face = make_face(Polyline(pts_top, close=True))
bot_face = make_face(Polyline(pts_bot, close=True))

top_face = Location((0, dovetail_top_offset, 0),
                     (0, 0, 90)) * top_face

bot_face = Location((0, dovetail_bot_offset,  bplate_width - dovetail_stop),
                     (0, -45, 90)) * bot_face

dovetail = loft([bot_face, top_face])

model   += dovetail

# ----------------------------------------------------------------------
# Create the slot for the dovetail by cutting out the model on the
# backplate
# ----------------------------------------------------------------------

face     = Location((corner_fillet, 0, 0), (0, 0, 0)) * \
           Rectangle(bplate_height, bplate_width,
                     align=(Align.MIN, Align.MIN))
bplate   = Plane.YZ * \
           extrude(face, amount=-bplate_thickness)
bplate  -= scale(model, by=dovetail_scale)

# ======================================================================
# Function that reads a SVG file, place it so bottom left is at
# origin, and return the face, with and height. If one of 'width' or
# 'height' optional argument is given, the face will be scaled to the
# size in the given dimension.
# ======================================================================

def svg_to_face(svg_data, width=None, height=None):

    if width and height:
        print("ERROR[svg_to_face()]: can't give both 'width' and 'height'")
        sys.exit(1)

    # Import the SVG that we really don't know the size or location of

    svg_fh         = StringIO(svg_data)
    svg_shape_list = import_svg(svg_fh)
    print("svg_shape_list=", svg_shape_list)  # Debug, might fail silently

    svg_face = make_face(svg_shape_list)

    # Rescale to the correct size from what we know it should be, and
    # the bounding box of what we got.

    if width:
        svg_scale = width / svg_face.bounding_box().size.X
        svg_face  = scale(svg_face, by=svg_scale)
    if height:
        svg_scale = height / svg_face.bounding_box().size.Y
        svg_face  = scale(svg_face, by=svg_scale)

    # Place it in the X Y plane with left bottom of the bounding box
    # at origin where the X and Y axes meet
    svg_face.position = (
        -svg_face.bounding_box().min.X,
        -svg_face.bounding_box().min.Y,
        0,
    )

    return svg_face, \
           svg_face.bounding_box().size.X, \
           svg_face.bounding_box().size.Y

# ======================================================================
# Add a sumbol to show how to instert the toothbrush
# ======================================================================

svg_arrow = '''\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" viewBox="0 0 568 671" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:1.5;">
    <g transform="matrix(1,0,0,1,-655.050303,-807.5)">
        <g transform="matrix(1,0,0,1,0,-79)">
            <path d="M1222,1090L1002.696,1090L1002.696,887L655.55,1228.45L1002.696,1556.292L1002.696,1363L1222,1363L1222,1090Z" style="stroke:black;stroke-width:1px;"/>
        </g>
    </g>
</svg>
'''

svg_toothbrush = '''\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" viewBox="0 0 599 2101" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:1.5;">
    <g transform="matrix(1,0,0,1,-1446.613542,-361.383437)">
        <g transform="matrix(1.586147,0,0,1.586147,616.98512,-162.881541)">
            <path d="M611.674,1654.249C558.308,1654.249 527.261,1569.61 523.723,1467.321C520.103,1362.641 544.697,1239.477 550.823,1169.624C571.421,934.729 575.429,544.288 575.586,404.462C575.648,349.189 587.643,330.523 615.134,330.847C637.319,331.108 654.746,338.791 655.71,364.486C972.872,305.82 940.839,468.256 775.621,466.52C940.012,481.494 934.932,573.743 784.462,578.379C936.512,582.834 942.366,695.703 781.183,696.624C938.031,703.075 950.538,855.716 659,789C713.323,1062.587 722.368,1281.268 728.767,1469.447C732.303,1573.424 703.443,1654.249 611.674,1654.249Z" style="stroke:black;stroke-width:0.63px;"/>
        </g>
    </g>
</svg>
'''

face_arrow, _, _      = svg_to_face(svg_arrow,
                                    height=arrow_icon_height)
face_toothbrush, _, _ = svg_to_face(svg_toothbrush,
                                    height=toothbrush_icon_height)

arrow                 = extrude(face_arrow, amount=-0.5)
toothbrush            = extrude(face_toothbrush, amount=-0.5)

model                -= arrow_location * arrow
model                -= toothbrush_location * toothbrush

# ======================================================================
# Create the STEP files
# ======================================================================

show([model, Pos(0, 0, -50) * bplate])

script_dir = os.path.dirname(os.path.realpath(__file__))
basename   = Path(__file__).stem

file_name = "%s.step" % (
    basename,
)

export_step(model, os.path.join(script_dir, file_name))

file_name = "%s_back_plate.step" % (
    basename,
)

export_step(bplate, os.path.join(script_dir, file_name))
