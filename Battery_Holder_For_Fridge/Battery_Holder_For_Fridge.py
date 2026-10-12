# This is battery holders for storing batteries in the fridge
#
# Yes, I know, it is mostly a myth that batteries should be store
# in the fridge. I will do that anyway just because I always do ;)
#
# This code is actually a mess. I tried use some Python module or
# separate script to take a 3MF template with the settings I want,
# and add a STL. I could not find any module or tool that did this,
# and running "BambuStudio" form command line on macOS just crashed.
# So I went into the trouble to edit the 3MF XML from this script!
#
# In retrospect, a few minutes using the GUI would have easily
# solved this without this messy coding. But anyway, I don't have
# the energy to redo this, so here it is.
#
# As I'm a beginner when it comes to using the Python "build123d"
# module to create this print, this is not even a good example of
# "build123d" usage, but maybe it demonstrates what can be done with
# such a package.
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

import re
import os.path
import tempfile
import shutil
import zipfile
from time import sleep
from pathlib import Path

from build123d import *
from ocp_vscode import *

# ======================================================================
# Data
# ======================================================================

wall       = 1

battery = [
    {
        "type"     : "AAA",
        "height"   : 20,
        "maxdepth" : 119.5,     # 120, but leave some space
        "columns"  : 5,         # "rows" is calculated from "maxdepth"
        "diameter" : 11,        # 10.5 + some space
    },
    {
        "type"     : "AA" ,
        "height"   : 25,
        "maxdepth" : 119.5,     # 120, but leave some space
        "columns"  : 4,         # "rows" is calculated from "maxdepth"
        "diameter" : 15,        # 14.5 + some space
    },
    {
        "type"     : "AAA",
        "height"   : 20,
        "maxdepth" : 109.5,     # 110, but leave some space
        "columns"  : 6,         # "rows" is calculated from "maxdepth"
        "diameter" : 11,        # 10.5 + some space
    },
    {
        "type"     : "AA" ,
        "height"   : 25,
        "maxdepth" : 109.5,     # 110, but leave some space
        "columns"  : 5,         # "rows" is calculated from "maxdepth"
        "diameter" : 15,        # 14.5 + some space
    },
    {
        "type"     : "AAA",
        "height"   : 20,
        "maxdepth" : 99.5,      # 100, but leave some space
        "columns"  : 6,         # "rows" is calculated from "maxdepth"
        "diameter" : 11,        # 10.5 + some space
    },
    {
        "type"     : "AA" ,
        "height"   : 25,
        "maxdepth" : 99.5,      # 100, but leave some space
        "columns"  : 5,         # "rows" is calculated from "maxdepth"
        "diameter" : 15,        # 14.5 + some space
    },
    {
        "type"     : "AAA",
        "height"   : 20,
        "maxdepth" : 89.5,      # 90, but leave some space
        "columns"  : 8,         # "rows" is calculated from "maxdepth"
        "diameter" : 11,        # 10.5 + some space
    },
    {
        "type"     : "AA" ,
        "height"   : 25,
        "maxdepth" : 89.5,      # 90, but leave some space
        "columns"  : 6,         # "rows" is calculated from "maxdepth"
        "diameter" : 15,        # 14.5 + some space
    },
    {
        "type"     : "AAA",
        "height"   : 20,
        "maxdepth" : 79.5,      # 90, but leave some space
        "columns"  : 10,        # "rows" is calculated from "maxdepth"
        "diameter" : 11,        # 10.5 + some space
    },
    {
        "type"     : "AA" ,
        "height"   : 25,
        "maxdepth" : 79.5,      # 90, but leave some space
        "columns"  : 8,         # "rows" is calculated from "maxdepth"
        "diameter" : 15,        # 14.5 + some space
    },
]

align_to_origin    = (Align.MIN, Align.MIN, Align.MIN)

# ======================================================================
# Calculated data
# ======================================================================

for battery_info in battery:
    battery_info["rows"] = \
        int(battery_info["maxdepth"] // \
            battery_info["diameter"])

# ======================================================================
# Function to create an 3mf file from a 3mf template and a shape
# ======================================================================

def create_3mf_from_template(shape, template, outfile):

    def normalize_xml(xml_text):
        return re.sub(r'(<(metadata|resources|build)[^>]*?)\s*/>',
                      r'\1></\2>', xml_text, flags=re.DOTALL)

    def replace_xml_sections(tags, xml_src, xml_dst):
        for tag in tags:
            re_section = fr'<{tag}\s*[^>]*?>.*?</{tag}>'
            re_src_obj = re.search(re_section, xml_src, flags=re.DOTALL)
            if re_src_obj:
                xml_dst = re.sub(re_section, re_src_obj.group(), xml_dst,
                                 flags=re.DOTALL)
        return xml_dst
    
    # ----------------------------------------------------------------------
    # Create a Mesher and add the shape and meta data to it
    # ----------------------------------------------------------------------

    exporter = Mesher()
    exporter.add_shape(shape)       # Add our model
    exporter.add_code_to_metadata() # Add this source code

    # ----------------------------------------------------------------------
    # Add other data to the "3D/3dmodel.model" file
    # ----------------------------------------------------------------------

    #<metadata name="Designer" preserve="1"></metadata>
    #<metadata name="Copyright" preserve="1"></metadata>
    #<metadata name="Description" preserve="1"></metadata>
    #<metadata name="Designer" preserve="1"></metadata>
    #<metadata name="Title" preserve="1"></metadata>

    # ----------------------------------------------------------------------
    # Write the created mesher 3mf file to a temporary file
    # ----------------------------------------------------------------------

    tempfile_obj = tempfile.NamedTemporaryFile(suffix=".3mf")
    exporter.write(tempfile_obj.name)

    # ----------------------------------------------------------------------
    # Copy the template 3mf and merge in content from mesher 3mf. I
    # did lots of trail and errors using the 'xml.etree.ElementTree'
    # module, but I had so many issues. One being "ns0", "ns1"
    # prefixes being added, another being that unused 'xmlns' being
    # removed, like the "BambuStudio" one confusing Bambu Studio. I'm
    # sure there is some working solution somewhere, maybe one of
    # https://stackoverflow.com/questions/13412496/python-elementtree-module-how-to-ignore-the-namespace-of-xml-files-to-locate-ma
    # But let's use regular expressions and be done with it :(
    # ----------------------------------------------------------------------

    with zipfile.ZipFile(tempfile_obj.name, 'r') as fh_mesher:
        path = zipfile.Path(fh_mesher, at="3D/3dmodel.model")
        xml_mesher_text = normalize_xml(path.read_text(encoding='UTF-8'))

    with zipfile.ZipFile(template, 'r') as fh_template:
        path = zipfile.Path(fh_template, at="3D/3dmodel.model")
        xml_template_text = normalize_xml(path.read_text(encoding='UTF-8'))

    # ----------------------------------------------------------------------
    # Parse the XML files, and merge them. We want to use the template
    # created in Bambu Studio as the template, and replace the 'resources'
    # and 'build' elements with the ones from our mesher 3mf.
    # ----------------------------------------------------------------------

    xml_template_text = replace_xml_sections(['resources', 'build'],
                                             xml_mesher_text,
                                             xml_template_text)

    # ----------------------------------------------------------------------
    # Create the modified 3mf from the template and our changes
    # Code to avoid duplicate memebers with the same name from answer at
    # https://stackoverflow.com/questions/25738523/how-to-update-one-file-inside-zip-file
    # ----------------------------------------------------------------------

    with zipfile.ZipFile(template, 'r') as fh_template:
        with zipfile.ZipFile(outfile, 'w') as fh_outfile:
            fh_outfile.comment = fh_template.comment # Preserve the comment
            for item in fh_template.infolist():
                if item.filename != "3D/3dmodel.model":
                    fh_outfile.writestr(item, fh_template.read(item.filename))
            fh_outfile.writestr("3D/3dmodel.model", xml_template_text)

# ======================================================================
# Construct the part
# ======================================================================

for battery_info in battery:

    # We create a box that is fully inside of the cyliners that we
    # create later to fill the holes for the supporting part
    model = Pos(battery_info["diameter"] / 2 + wall,
                battery_info["diameter"] / 2 + wall,
                0) * \
                Box((battery_info["columns"] - 1) * battery_info["diameter"],
                    (battery_info["rows"] -1) * battery_info["diameter"],
                    battery_info["height"], align=align_to_origin)


    # Got help from Javi Ballister at the build123d discord to make
    # separate loops to one, more compact yet controlled and clear
    outter_locs = []
    inner_locs = []
    for col in range(battery_info["columns"]):
        for row in range(battery_info["rows"]):
            xoff = col * battery_info["diameter"]
            yoff = row * battery_info["diameter"]
            outter_locs.append(Location((xoff, yoff, 0)))
            inner_locs.append(Location((xoff + wall, yoff + wall, wall)))

    model += outter_locs * Cylinder(
        battery_info["diameter"] / 2 + wall,
        battery_info["height"],
        align=align_to_origin,
    )

    size = model.bounding_box().size

    model -= inner_locs * Cylinder(
        battery_info["diameter"] / 2,
        battery_info["height"],
        align=align_to_origin,
    )

    # We want to cut out a bit more, so that rows of batteries
    # still in plastic packaging, can be inserted
    xlen = (battery_info["columns"] - 1) * battery_info["diameter"]
    ylen = (battery_info["rows"] - 1) * battery_info["diameter"]
    beam_width = battery_info["diameter"] / 2 - wall * 2

    for col in range(battery_info["columns"]):
        xoff = col * battery_info["diameter"] + battery_info["diameter"] / 2 + wall
        model -= Pos(xoff - beam_width / 2, battery_info["diameter"] / 2, wall) * \
            Box(beam_width, ylen, battery_info["height"],
                align=align_to_origin)
        for row in range(battery_info["rows"]):
            yoff = row * battery_info["diameter"] + battery_info["diameter"] / 2 + wall
            model -= Pos(battery_info["diameter"] / 2, yoff - beam_width / 2, wall) * \
                Box(xlen, beam_width, battery_info["height"],
                    align=align_to_origin)

    # Output STL
    script_dir  = os.path.dirname(os.path.realpath(__file__))
    basename = "%s_%s_%sx%smm" % (
        Path(__file__).stem,
        battery_info["type"],
        int(size.X),
        int(size.Y))
    basepath = os.path.join(script_dir, basename)
    path_template = os.path.join(script_dir, "Templates",
                                 Path(__file__).stem + "_TEMPLATE.3mf")
    path_3mf      = os.path.join(script_dir, basepath + ".3mf")
    create_3mf_from_template(model,
                             path_template,
                             path_3mf)
    show(model)
    sleep(2)
